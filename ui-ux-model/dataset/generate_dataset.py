"""
Bootstraps a large synthetic training set from dataset/seed_examples.jsonl.

Why this exists: there is no off-the-shelf "UI design idea in text" dataset.
The standard workaround (distillation) is to have a larger, capable LLM
generate many more examples in the same shape as your hand-written seed set,
validate them, and use *that* as the fine-tuning data for your small model.

Supports three providers:
  - openrouter (default) — nvidia/nemotron-3-ultra-550b-a55b:free, a strong
                 free frontier-reasoning MoE model. Best quality per example,
                 but capped at ~50 requests/day unfunded (1,000/day if the
                 account has ever added $10 of credit).
  - groq       — qwen/qwen3.6-27b, flagship-tier Qwen, free tier with a
                 generally more generous daily cap — use this for volume,
                 or as a fallback once OpenRouter's cap is hit for the day.
  - anthropic  — paid, kept as an option if you already have a key.

All three are called through the OpenAI-compatible chat completions shape
(Groq and OpenRouter both expose one at their own base_url); Anthropic uses
its native SDK since it predates that convention.

Usage:
    export OPENROUTER_API_KEY=sk-or-...
    python generate_dataset.py --limit 50                        # openrouter, default model, respects daily cap
    export GROQ_API_KEY=gsk_...
    python generate_dataset.py --limit 500 --provider groq        # higher volume
    python generate_dataset.py --limit 200 --provider anthropic --model claude-sonnet-5

Practical tip: run openrouter first for ~50 high-quality examples, then
switch to --provider groq for bulk volume, then concatenate both output
files — you get some of Nemotron's quality plus Qwen's throughput.
"""

import argparse
import json
import random
import re
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import config  # noqa: E402

REQUIRED_FIELDS = [
    "navbar",
    "color_palette",
    "typography",
    "buttons_and_transitions",
    "background_animation",
    "layout_notes",
]

# A pool of themes/site types to randomly combine so the model sees broad
# coverage instead of overfitting to only the seed combinations.
THEMES = [
    "Marvel-inspired superhero", "minimalist Scandinavian", "cyberpunk neon",
    "cozy artisan", "modern fintech", "luxury fashion", "playful kids education",
    "calm wellness", "streetwear sneaker culture", "botanical plant shop",
    "retro arcade", "art-deco", "brutalist", "pastel kawaii", "nautical coastal",
    "industrial loft", "vaporwave", "eco-sustainable", "space/sci-fi", "gothic dark academia",
]
SITE_TYPES = [
    "e-commerce store", "SaaS landing page", "portfolio site", "mobile banking app",
    "food delivery app", "travel booking site", "online course platform",
    "music streaming app", "real estate listing site", "fitness tracking app",
    "restaurant website", "nonprofit donation site", "event ticketing platform",
    "job board", "recipe sharing app",
]


def load_seed_examples() -> list[dict]:
    examples = []
    with open(config.SEED_FILE, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                examples.append(json.loads(line))
    return examples


def build_few_shot_prompt(seed_examples: list[dict], theme: str, site_type: str, n_shots: int = 3) -> str:
    """Constructs a few-shot prompt: show n_shots seed examples, then ask for a new one."""
    shots = random.sample(seed_examples, k=min(n_shots, len(seed_examples)))
    shot_text = "\n\n".join(
        f"Input: {s['prompt']}\nOutput: {json.dumps(s['response'])}" for s in shots
    )
    schema_hint = ", ".join(REQUIRED_FIELDS)
    return (
        "You generate structured UI/UX design guidance in a fixed JSON schema. "
        f"The JSON object must have exactly these keys: {schema_hint}. "
        "Each value is 1-3 sentences of concrete, actionable design guidance "
        "(specific colors with hex codes where relevant, specific animation timing, "
        "specific layout choices) — not generic advice.\n\n"
        f"Examples:\n\n{shot_text}\n\n"
        f"Now generate ONE new example for:\n"
        f"Input: Design a UI for a {site_type} in a {theme} theme.\n"
        "Output ONLY the JSON object, no other text."
    )


def call_llm(prompt: str, provider: str, model: str) -> str:
    """Dispatches to the right SDK/endpoint for the chosen provider."""
    if provider == "anthropic":
        import anthropic  # imported lazily so the script can be inspected without the package installed

        client = anthropic.Anthropic(api_key=config.PROVIDER_DEFAULTS["anthropic"]["api_key"])
        response = client.messages.create(
            model=model, max_tokens=500, messages=[{"role": "user", "content": prompt}]
        )
        return response.content[0].text

    elif provider in ("groq", "openrouter"):
        from openai import OpenAI  # both providers speak the OpenAI chat-completions shape

        cfg = config.PROVIDER_DEFAULTS[provider]
        client = OpenAI(api_key=cfg["api_key"], base_url=cfg["base_url"])

        # Both qwen3.6-27b (Groq) and Nemotron 3 Ultra (OpenRouter) are reasoning
        # models that default to thinking mode — and Groq specifically inlines
        # <think>...</think> directly into message.content by default, which
        # breaks JSON parsing outright. We don't need reasoning for a templated
        # structured-output task, so disable it via each provider's own param
        # (documented at console.groq.com/docs/reasoning and
        # openrouter.ai/docs/use-cases/reasoning-tokens). This also cuts token
        # usage and latency since no reasoning trace gets generated at all.
        extra_body = {}
        if provider == "groq":
            extra_body["reasoning_effort"] = "none"
        elif provider == "openrouter":
            extra_body["reasoning"] = {"effort": "none", "exclude": True}

        response = client.chat.completions.create(
            model=model, max_tokens=500, messages=[{"role": "user", "content": prompt}],
            extra_body=extra_body,
        )

        # OpenRouter's free tier is known to occasionally return a response
        # missing `choices` entirely (a documented compatibility quirk with
        # some upstream free-model routes) — the openai SDK then leaves
        # response.choices as None rather than raising, so indexing it blows
        # up with a cryptic "'NoneType' object is not subscriptable". Catch
        # it here and raise something the retry loop can actually explain.
        if not response.choices:
            raise RuntimeError(
                f"{provider} returned a response with no 'choices' (likely a free-tier "
                f"routing quirk, not your code) — retrying will usually work."
            )
        content = response.choices[0].message.content
        if not content:
            raise RuntimeError(
                f"{provider} returned an empty message content (finish_reason="
                f"{response.choices[0].finish_reason!r}) — retrying will usually work."
            )
        return content

    else:
        raise ValueError(f"Unknown provider: {provider}")


def parse_and_validate(raw_text: str) -> dict | None:
    """Extracts and validates the JSON object the model returned. Returns None if invalid."""
    raw_text = raw_text.strip()

    # Backstop in case reasoning wasn't fully suppressed (provider/model quirks,
    # future model swaps): strip a <think>...</think> block if present.
    raw_text = re.sub(r"<think>.*?</think>", "", raw_text, flags=re.DOTALL | re.IGNORECASE).strip()

    # Model sometimes wraps output in ```json fences despite instructions — strip defensively.
    if raw_text.startswith("```"):
        raw_text = raw_text.strip("`")
        raw_text = raw_text.split("\n", 1)[-1] if raw_text.lower().startswith("json") else raw_text
        raw_text = raw_text.strip()

    obj = _try_parse_json(raw_text)
    if obj is None:
        return None

    if not isinstance(obj, dict):
        return None
    if any(field not in obj or not isinstance(obj[field], str) or not obj[field].strip() for field in REQUIRED_FIELDS):
        return None
    return obj


def _try_parse_json(text: str) -> dict | None:
    """Tries a direct parse first; falls back to extracting the first {...} block
    from surrounding stray text (commentary the model added despite instructions)."""
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1 or end <= start:
        return None
    try:
        return json.loads(text[start:end + 1])
    except json.JSONDecodeError:
        return None


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--limit", type=int, default=None,
        help="how many new examples to generate (default: 50 for openrouter to respect its unfunded daily cap, 500 for groq/anthropic)",
    )
    parser.add_argument(
        "--provider", choices=["openrouter", "groq", "anthropic"], default="openrouter",
        help="which API to call (default: openrouter, Nemotron 3 Ultra free — best quality, ~50/day cap unfunded)",
    )
    parser.add_argument("--model", default=None, help="override the provider's default model")
    parser.add_argument(
        "--sleep", type=float, default=None,
        help="seconds between API calls; defaults to a safe value for the chosen provider's free-tier rate limit",
    )
    args = parser.parse_args()

    provider_cfg = config.PROVIDER_DEFAULTS[args.provider]
    model = args.model or provider_cfg["model"]
    sleep_seconds = args.sleep if args.sleep is not None else provider_cfg["min_seconds_between_calls"]
    limit = args.limit if args.limit is not None else (50 if args.provider == "openrouter" else 500)

    if not provider_cfg["api_key"]:
        env_var = {"groq": "GROQ_API_KEY", "openrouter": "OPENROUTER_API_KEY", "anthropic": "ANTHROPIC_API_KEY"}[args.provider]
        print(f"ERROR: set {env_var} (or pass --provider to use a different one).", file=sys.stderr)
        sys.exit(1)

    print(f"Provider: {args.provider} | Model: {model} | Limit: {limit} | Min delay between calls: {sleep_seconds}s")
    seed_examples = load_seed_examples()
    print(f"Loaded {len(seed_examples)} seed examples.")

    # Separate output file per provider — otherwise running openrouter then
    # groq (the recommended workflow) would silently overwrite the first
    # provider's output, since both used to share config.GENERATED_FILE.
    generated_file = config.DATASET_DIR / f"generated_examples_{args.provider}.jsonl"

    generated = []
    attempts = 0
    max_attempts = limit * 2  # allow some retries for invalid outputs
    consecutive_rate_limits = 0
    RATE_LIMIT_BREAKER = 3  # stop retrying after this many 429s in a row — the daily quota is exhausted, not a transient blip

    with open(generated_file, "w", encoding="utf-8") as out_f:
        while len(generated) < limit and attempts < max_attempts:
            attempts += 1
            theme = random.choice(THEMES)
            site_type = random.choice(SITE_TYPES)
            prompt_text = build_few_shot_prompt(seed_examples, theme, site_type)

            try:
                raw = call_llm(prompt_text, args.provider, model)
            except Exception as e:
                # Free-tier rate limits (HTTP 429) are expected, not exceptional —
                # back off and retry a few times. But if it keeps happening, that's
                # almost certainly the *daily* quota exhausted (esp. on OpenRouter's
                # 50/day unfunded cap), and no amount of waiting-and-retrying today
                # will fix that — so stop instead of looping for hours.
                if "429" in str(e) or "rate" in str(e).lower():
                    consecutive_rate_limits += 1
                    if consecutive_rate_limits >= RATE_LIMIT_BREAKER:
                        print(
                            f"  [stopped] {consecutive_rate_limits} rate limits in a row — "
                            f"this is very likely your daily quota, not a transient limit. "
                            f"Wrote {len(generated)}/{limit} before stopping. "
                            f"Try again tomorrow, fund the account, or rerun with --provider groq.",
                            file=sys.stderr,
                        )
                        break
                    print(f"  [rate limited] backing off 30s ({e})", file=sys.stderr)
                    time.sleep(30.0)
                else:
                    print(f"  [warn] API call failed: {e}", file=sys.stderr)
                    time.sleep(2.0)
                continue

            consecutive_rate_limits = 0  # reset on any successful call

            parsed = parse_and_validate(raw)
            if parsed is None:
                print(f"  [warn] discarded invalid output for '{theme}' / '{site_type}'", file=sys.stderr)
                time.sleep(sleep_seconds)  # a real call was made — still respect the rate limit
                continue

            record = {
                "prompt": f"Design a UI for a {site_type} in a {theme} theme.",
                "response": parsed,
            }
            out_f.write(json.dumps(record, ensure_ascii=False) + "\n")
            out_f.flush()
            generated.append(record)

            if len(generated) % 25 == 0:
                print(f"  generated {len(generated)}/{limit}")

            time.sleep(sleep_seconds)

    print(f"Done. Wrote {len(generated)} examples to {generated_file} "
          f"({attempts - len(generated)} discarded/failed attempts).")
    print("Next, once you've run all providers you want: "
          "cat seed_examples.jsonl generated_examples_*.jsonl > train.jsonl")


if __name__ == "__main__":
    main()
