"""
pipeline.py — the actual generate -> ground -> critique -> revise logic.
No UI code here on purpose: this module is provider-agnostic and testable
on its own, independent of the terminal UI in app.py.
"""

import random
import time
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from typing import Optional

from openai import OpenAI, APIError, APIConnectionError, RateLimitError, AuthenticationError

try:
    from ddgs import DDGS
except ImportError:
    DDGS = None  # grounding step degrades gracefully to "no references" if this isn't installed


# base_url presets — pick one in the setup screen, or type a custom URL
PROVIDER_PRESETS = {
    "groq": "https://api.groq.com/openai/v1",
    "openrouter": "https://openrouter.ai/api/v1",
    "nvidia_nim": "https://integrate.api.nvidia.com/v1",
    "gemini": "https://generativelanguage.googleapis.com/v1beta/openai/",
    "mistral": "https://api.mistral.ai/v1",
    "cerebras": "https://api.cerebras.ai/v1",
    "huggingface": "https://router.huggingface.co/v1",
}

DEFAULT_APP_TYPES = [
    "ecommerce app", "SaaS dashboard", "fitness tracker", "food delivery app",
    "banking app", "social media app", "travel booking app",
    "productivity tool", "music streaming app", "real estate listing app",
]

DEFAULT_STYLES = [
    "premium/luxury", "minimalist", "playful and vibrant",
    "dark mode futuristic", "neumorphic", "glassmorphic",
    "brutalist", "corporate/professional",
]


class FatalProviderError(Exception):
    """Raised when the whole run should stop (e.g. bad API key) instead of just skipping a sample."""


@dataclass
class Sample:
    app_type: str
    style: str
    provider: str
    model: str
    draft: str = ""
    grounding: list = field(default_factory=list)
    critique: str = ""
    final: str = ""
    status: str = "pending"  # pending -> drafting -> grounding -> critiquing -> revising -> done / failed
    error: Optional[str] = None
    timestamp: str = ""

    def to_json_dict(self) -> dict:
        return asdict(self)


def build_client(base_url: str, api_key: str) -> OpenAI:
    return OpenAI(base_url=base_url, api_key=api_key)


def _call_model(client: OpenAI, model: str, prompt: str, max_tokens: int = 600, retries: int = 3) -> str:
    """
    One chat-completion call with retry/backoff on rate limits and transient
    connection issues. Raises FatalProviderError on bad auth — retrying a
    rejected key just wastes time, so that one aborts the whole run instead.
    """
    last_err: Optional[Exception] = None
    for attempt in range(1, retries + 1):
        try:
            resp = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.8,
                max_tokens=max_tokens,
            )
            content = resp.choices[0].message.content
            return content.strip() if content else ""
        except AuthenticationError as e:
            raise FatalProviderError(f"API key rejected: {e}") from e
        except RateLimitError as e:
            last_err = e
            time.sleep(min(2 ** attempt, 30))  # exponential backoff, capped at 30s
        except (APIConnectionError, APIError) as e:
            last_err = e
            time.sleep(min(2 ** attempt, 15))
    raise RuntimeError(f"Failed after {retries} attempts: {last_err}")


def generate_draft(client: OpenAI, model: str, app_type: str, style: str) -> str:
    prompt = (
        f"You are a senior UI/UX designer. Give detailed, concrete UI/UX design "
        f"recommendations for a {style}-styled {app_type}. Cover: color palette, "
        f"typography, layout/navigation, one key screen in detail, and micro-interactions "
        f"or animation. Be specific — no generic platitudes like 'make it user-friendly'."
    )
    return _call_model(client, model, prompt, max_tokens=700)


def ground_search(app_type: str, style: str, max_results: int = 3) -> list:
    """
    Pulls a handful of real-world reference snippets via DuckDuckGo.
    Returns [] on any failure — grounding improves quality but a search hiccup
    shouldn't kill the whole sample.
    """
    if DDGS is None:
        return []
    query = f"{style} {app_type} UI UX design best practices examples"
    try:
        with DDGS() as ddgs:
            results = ddgs.text(query, max_results=max_results)
        return [f"{r.get('title', '')}: {r.get('body', '')}" for r in results]
    except Exception:
        return []


def critique_draft(client: OpenAI, model: str, draft: str, grounding: list) -> str:
    refs = "\n".join(f"- {g}" for g in grounding) if grounding else "(no external references found)"
    prompt = (
        "You are a strict design reviewer. Compare the DRAFT below against the REFERENCE "
        "notes gathered from real design sources. List at least 2 concrete, specific problems "
        "with the draft — vague statements, missing details, or things that contradict the "
        "references. Do not praise it; find genuine issues.\n\n"
        f"DRAFT:\n{draft}\n\nREFERENCES:\n{refs}"
    )
    return _call_model(client, model, prompt, max_tokens=400)


def revise_draft(client: OpenAI, model: str, draft: str, critique: str) -> str:
    prompt = (
        "Revise the DRAFT below to fix every issue raised in the CRITIQUE. Keep the same "
        "shape (color palette, typography, layout, key screen, micro-interactions) but make "
        "it more specific and concrete. Output ONLY the revised recommendations, no meta-commentary.\n\n"
        f"DRAFT:\n{draft}\n\nCRITIQUE:\n{critique}"
    )
    return _call_model(client, model, prompt, max_tokens=700)


def run_pipeline_for_sample(client: OpenAI, model: str, app_type: str, style: str,
                             provider_name: str, status_cb=None) -> Sample:
    """
    Runs the full generate -> ground -> critique -> revise chain for one sample.
    status_cb(sample), if given, is called after every stage transition — used by
    the UI to show live progress. Raises FatalProviderError if auth fails (caller
    should stop the whole run, not just this sample).
    """
    sample = Sample(app_type=app_type, style=style, provider=provider_name, model=model,
                     timestamp=datetime.now(timezone.utc).isoformat())

    def emit(status: str):
        sample.status = status
        if status_cb:
            status_cb(sample)

    try:
        emit("drafting")
        sample.draft = generate_draft(client, model, app_type, style)

        emit("grounding")
        sample.grounding = ground_search(app_type, style)

        emit("critiquing")
        sample.critique = critique_draft(client, model, sample.draft, sample.grounding)

        emit("revising")
        sample.final = revise_draft(client, model, sample.draft, sample.critique)

        emit("done")
    except FatalProviderError:
        raise  # bubble up — the whole run stops, not just this sample
    except Exception as e:
        sample.error = str(e)
        emit("failed")
    return sample


def build_sample_matrix(limit: int, app_types=None, styles=None, seed: int = 42) -> list:
    """
    Returns `limit` (app_type, style) pairs, shuffled for variety, cycling back
    to the start if `limit` exceeds the number of unique combinations.
    """
    app_types = app_types or DEFAULT_APP_TYPES
    styles = styles or DEFAULT_STYLES
    combos = [(a, s) for a in app_types for s in styles]
    rng = random.Random(seed)
    rng.shuffle(combos)
    return [combos[i % len(combos)] for i in range(limit)]
