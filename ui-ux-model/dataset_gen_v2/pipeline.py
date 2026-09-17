"""
pipeline.py — the actual generate -> ground -> critique -> revise (-> implement ->
render -> vision_critique) logic. No UI code here on purpose: this module is
provider-agnostic and testable on its own, independent of the terminal UI in app.py.

CHANGE LOG (this revision):
- Added implement_code / render_screenshot / vision_critique: an optional stage
  that turns a sample's final text recommendations into real HTML, renders it
  headless, and asks a vision model to critique the screenshot. This produces
  (screenshot, recommendations) training pairs that match the deployed model's
  actual real-world use case: "here's my current website — what would you
  improve?" See run_pipeline_for_sample(enable_screenshot=True).
- Added split_matrix() for dividing work across N providers running concurrently.
- Refactored _call_model into _call_chat (accepts a full `messages` list, so the
  same retry/backoff logic serves both plain-text and multimodal calls) with
  _call_model kept as a thin text-only wrapper so existing call sites don't change.

VERIFIED: render_screenshot() has been run against a real headless Chromium
in the environment these files were built in (Playwright + browser binaries
were present there) — see the test suite. Kaggle's default image is NOT
guaranteed to have Playwright's browser binaries pre-installed, though —
run `playwright install chromium` as a setup cell before a real run there,
and verify with --limit 1 first.
"""

import base64
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
    # Auth: use your Puter auth token (puter.com/dashboard -> Create token) as the
    # API key. Puter also proxies closed models (GPT/Claude/Gemini/Grok), but avoid
    # those for dataset generation — using their output to train a competing model
    # runs into those providers' usage policies. Stick to open-weight models here
    # (e.g. "deepseek/deepseek-v3.2", "mistralai/mistral-large-2512", "z-ai/glm-5.2").
    "puter": "https://api.puter.com/puterai/openai/v1/",
}

# Models used for the optional implement -> render -> vision_critique stage need
# to actually support vision input. These are NOT enforced in code (any model
# string is accepted — validation would require a live API call), just a
# starting point for the "Vision model" field in the setup screen.
SUGGESTED_VISION_MODELS = [
    "qwen/qwen3-vl-8b-instruct",       # OpenRouter — check current free-tier availability
    "qwen/qwen2.5-vl-32b-instruct",    # OpenRouter — check current free-tier availability
    "meta/llama-3.2-90b-vision-instruct",  # NVIDIA NIM
]

DEFAULT_APP_TYPES = [
    "ecommerce app", "SaaS dashboard", "fitness tracker", "food delivery app",
    "banking app", "social media app", "travel booking app",
    "productivity tool", "music streaming app", "real estate listing app",
    "healthcare/telemedicine app", "education/e-learning platform",
    "job board / recruiting platform", "event ticketing app", "recipe/cooking app",
    "personal finance/budgeting app", "meditation/wellness app", "pet care app",
    "dating app", "news/media app", "podcast app", "video streaming platform",
    "crypto/trading app", "logistics/delivery tracking app",
    "coworking/booking app", "nonprofit/donation platform",
    "subscription box service", "AR/VR shopping app", "smart home control app",
    "government/civic services portal",
]

# NOT a style directive — style is fully open, the model picks its own aesthetic
# direction every time. These are loose situational context to keep 15k+ samples
# from converging into near-duplicates of the same "design an X" prompt.
DEFAULT_SEED_HINTS = [
    "target audience: Gen Z", "target audience: busy professionals",
    "target audience: seniors/elderly users", "target audience: children/families",
    "primary goal: fast checkout/conversion", "primary goal: building trust and credibility",
    "primary goal: encouraging exploration/discovery", "primary goal: accessibility-first",
    "brand personality: bold and energetic", "brand personality: calm and minimal",
    "brand personality: quirky and playful", "brand personality: luxurious and exclusive",
    "constraint: must work great on small phone screens", "constraint: needs to support dark mode",
    "constraint: heavy on data/analytics display", "constraint: mostly visual/photo-driven content",
    "context: early-stage startup, limited budget", "context: established enterprise brand",
    "context: rebrand/redesign of an existing product", "context: brand new product launch",
]


class FatalProviderError(Exception):
    """Raised when a provider's whole run should stop (e.g. bad API key) instead of
    just skipping a sample. In the dual-provider setup, this stops only the worker
    that hit it — the other provider's worker keeps going."""


@dataclass
class Sample:
    app_type: str
    seed_hint: str
    provider: str
    model: str
    draft: str = ""
    grounding: list = field(default_factory=list)
    critique: str = ""
    final: str = ""
    # Optional implement -> render -> {rate, improve, recreate} stage. Three
    # separate fields because the deployed model needs to handle all three
    # query types a user might ask about their uploaded screenshot — see
    # rate_screenshot / vision_critique / recreate_code below.
    code: str = ""
    screenshot_b64: str = ""
    rating: str = ""            # "rate my site" -> a scored, reasoned rating
    vision_critique: str = ""   # "how do I improve this" -> recommendations
    improved_code: str = ""     # "recreate this with a better UI" -> new HTML
    # pending -> drafting -> grounding -> critiquing -> revising ->
    #   [implementing -> rendering -> rating -> vision_critiquing -> recreating ->]
    #   done / failed
    status: str = "pending"
    error: Optional[str] = None
    timestamp: str = ""

    def to_json_dict(self) -> dict:
        return asdict(self)


def build_client(base_url: str, api_key: str) -> OpenAI:
    return OpenAI(base_url=base_url, api_key=api_key)


def _call_chat(client: OpenAI, model: str, messages: list, max_tokens: int = 600,
               retries: int = 3, temperature: float = 0.8) -> str:
    """
    Shared retry/backoff core for both plain-text and multimodal chat calls.
    Raises FatalProviderError on bad auth — retrying a rejected key just wastes
    time, so that one aborts the calling worker instead.
    """
    last_err: Optional[Exception] = None
    for attempt in range(1, retries + 1):
        try:
            resp = client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
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


def _call_model(client: OpenAI, model: str, prompt: str, max_tokens: int = 600, retries: int = 3) -> str:
    """Text-only convenience wrapper around _call_chat."""
    return _call_chat(client, model, [{"role": "user", "content": prompt}], max_tokens, retries)


def generate_draft(client: OpenAI, model: str, app_type: str, seed_hint: str) -> str:
    prompt = (
        f"You are a senior UI/UX designer known for creative, non-generic work. Design a "
        f"UI/UX concept for a {app_type}. Context: {seed_hint}. Choose whatever aesthetic "
        f"direction and style genuinely fits — conventional or unconventional, entirely your "
        f"call. Don't default to the safest, most predictable choice. Cover: color palette, "
        f"typography, layout/navigation, one key screen in detail, and micro-interactions "
        f"or animation. Be specific — no generic platitudes like 'make it user-friendly'."
    )
    return _call_model(client, model, prompt, max_tokens=700)


def ground_search(app_type: str, max_results: int = 3) -> list:
    """
    Pulls a handful of real-world reference snippets via DuckDuckGo.
    Returns [] on any failure — grounding improves quality but a search hiccup
    shouldn't kill the whole sample. No style term here since style is open —
    grounding is app-type-general, not style-specific, in this version.
    """
    if DDGS is None:
        return []
    query = f"{app_type} UI UX design inspiration examples"
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


def implement_code(client: OpenAI, model: str, final_text: str, app_type: str) -> str:
    """
    Turns the finished text recommendations into a real, renderable single-file
    HTML mockup. This is the bridge between "text design advice" (what the base
    pipeline produces) and "an image the vision model can critique" (what the
    deployed model needs to have seen during training, to handle a real uploaded
    screenshot well).
    """
    prompt = (
        "Turn the following UI/UX design recommendations into a single, self-contained "
        "HTML file implementing them as a static mockup of the one key screen described. "
        "Use the Tailwind CSS CDN script tag for styling (no build step, no external CSS "
        "files). Inline any needed JS in a <script> tag. Use realistic placeholder text and "
        "https://placehold.co for any images. Output ONLY the raw HTML, starting with "
        "<!DOCTYPE html> — no markdown code fences, no commentary before or after.\n\n"
        f"APP TYPE: {app_type}\n\nDESIGN RECOMMENDATIONS:\n{final_text}"
    )
    code = _call_model(client, model, prompt, max_tokens=2200)
    return _strip_markdown_fence(code)


def _strip_markdown_fence(text: str) -> str:
    """Some models add ```html ... ``` fences despite instructions not to. Strip them
    if present; leave the text alone otherwise. Pure function, unit-testable."""
    t = text.strip()
    if t.startswith("```"):
        parts = t.split("```")
        if len(parts) >= 2:
            inner = parts[1]
            if inner.startswith("html"):
                inner = inner[4:]
            return inner.strip()
    return t


def render_screenshot(html: str, viewport_width: int = 1280, viewport_height: int = 900,
                       timeout_ms: int = 15000) -> Optional[bytes]:
    """
    Renders `html` in headless Chromium and returns PNG bytes, or None on any
    failure (Playwright not installed, browser binaries missing, broken markup,
    timeout, etc.) — a rendering problem skips just this sample's screenshot
    stage instead of failing the whole sample.

    Verified against a real render in this project's dev environment (see
    test_pipeline_e2e.py). Kaggle's image may not have the browser binaries
    pre-installed — run `playwright install chromium` there first.
    """
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        return None
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch()
            try:
                page = browser.new_page(viewport={"width": viewport_width, "height": viewport_height})
                page.set_content(html, timeout=timeout_ms, wait_until="networkidle")
                return page.screenshot(type="png")
            finally:
                browser.close()
    except Exception:
        return None


def vision_critique(client: OpenAI, model: str, image_b64: str, app_type: str) -> str:
    """
    The exact inference-time task, reproduced for training: given a screenshot of
    a website's current UI, give specific, actionable improvement recommendations.
    Phrased close to how a real user would ask, so the training pair transfers.
    """
    prompt = (
        f"Here is a screenshot of a {app_type}'s current UI. Act as a senior UI/UX "
        "designer reviewing it for a client who asked how to make it better. Give "
        "specific, actionable recommendations — cover visual hierarchy, color/contrast, "
        "typography, spacing, and anything that looks generic or dated. Be direct about "
        "what's weak; do not just praise it."
    )
    messages = [{
        "role": "user",
        "content": [
            {"type": "text", "text": prompt},
            {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{image_b64}"}},
        ],
    }]
    return _call_chat(client, model, messages, max_tokens=600, temperature=0.7)


def rate_screenshot(client: OpenAI, model: str, image_b64: str, app_type: str) -> str:
    """
    Covers the "rate my site" query type — distinct from vision_critique's "how
    do I improve it": this one is scored and comparative rather than purely
    prescriptive, so the deployed model learns both response shapes.
    """
    prompt = (
        f"Here is a screenshot of a {app_type}'s current UI. Rate its UI/UX out of "
        "10 and justify the score: name the 2-3 strongest elements and the 2-3"
        "weakest, and say what separates it from a top-tier product in this "
        "category. Be honest — most real websites score in the 5-7 range, not 9+."
    )
    messages = [{
        "role": "user",
        "content": [
            {"type": "text", "text": prompt},
            {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{image_b64}"}},
        ],
    }]
    return _call_chat(client, model, messages, max_tokens=500, temperature=0.7)


def recreate_code(client: OpenAI, model: str, original_code: str, critique: str, app_type: str) -> str:
    """
    Covers the "recreate this with a better UI" query type. Generated from the
    already-known original code + critique (cheaper and more reliable than a
    second vision call re-deriving both from the image) — but the training pair
    this feeds (see prepare_training_data.py) still presents the ORIGINAL
    SCREENSHOT as the user turn, matching exactly what a real user will upload.
    Only the generation method is a shortcut; the supervision target is correct.
    """
    prompt = (
        "Rewrite the HTML mockup below into an improved version that fixes every "
        "issue raised in the CRITIQUE. Keep it a single self-contained HTML file "
        "using the Tailwind CSS CDN script tag, same constraints as before (inline "
        "JS only, https://placehold.co for images). Output ONLY the raw revised "
        "HTML, starting with <!DOCTYPE html> — no markdown fences, no commentary.\n\n"
        f"APP TYPE: {app_type}\n\nORIGINAL HTML:\n{original_code}\n\nCRITIQUE:\n{critique}"
    )
    code = _call_model(client, model, prompt, max_tokens=2200)
    return _strip_markdown_fence(code)


def run_pipeline_for_sample(client: OpenAI, model: str, app_type: str, seed_hint: str,
                             provider_name: str, status_cb=None,
                             enable_screenshot: bool = False,
                             code_client: Optional[OpenAI] = None, code_model: Optional[str] = None,
                             vision_client: Optional[OpenAI] = None, vision_model: Optional[str] = None
                             ) -> Sample:
    """
    Runs generate -> ground -> critique -> revise for one sample, then optionally
    implement -> render -> vision_critique if enable_screenshot is True.

    code_client/vision_client default to `client`/`model` if not given — but in
    practice (see app.py) they're always routed through Provider A's credentials
    regardless of which provider drafted the sample, since the vision/code model
    names are configured once, not per-provider. A rendering failure only drops
    the screenshot bonus fields for this sample; it does not fail the sample —
    the draft/critique/revise text is kept either way.

    status_cb(sample), if given, is called after every stage transition — used by
    the UI to show live progress. Raises FatalProviderError if the PRIMARY
    provider's auth fails (caller should stop that worker, not the whole run).
    A code/vision auth failure during the optional stage is caught and simply
    ends that stage for this sample, since it's a bonus feature, not the core task.
    """
    sample = Sample(app_type=app_type, seed_hint=seed_hint, provider=provider_name, model=model,
                     timestamp=datetime.now(timezone.utc).isoformat())

    def emit(status: str):
        sample.status = status
        if status_cb:
            status_cb(sample)

    try:
        emit("drafting")
        sample.draft = generate_draft(client, model, app_type, seed_hint)

        emit("grounding")
        sample.grounding = ground_search(app_type)

        emit("critiquing")
        sample.critique = critique_draft(client, model, sample.draft, sample.grounding)

        emit("revising")
        sample.final = revise_draft(client, model, sample.draft, sample.critique)

        if enable_screenshot:
            cc, cm = (code_client or client), (code_model or model)
            vc, vm = (vision_client or client), (vision_model or model)
            try:
                emit("implementing")
                sample.code = implement_code(cc, cm, sample.final, app_type)

                emit("rendering")
                png_bytes = render_screenshot(sample.code)
                if png_bytes:
                    sample.screenshot_b64 = base64.b64encode(png_bytes).decode("ascii")

                    # Three separate calls so the deployed model has seen all
                    # three query types a real user might send with their
                    # uploaded screenshot: rate it / improve it / recreate it.
                    emit("rating")
                    sample.rating = rate_screenshot(vc, vm, sample.screenshot_b64, app_type)

                    emit("vision_critiquing")
                    sample.vision_critique = vision_critique(vc, vm, sample.screenshot_b64, app_type)

                    emit("recreating")
                    sample.improved_code = recreate_code(cc, cm, sample.code, sample.vision_critique, app_type)
            except FatalProviderError:
                pass  # bonus stage's own key is bad — keep the core text sample, drop the bonus
            except Exception:
                pass  # any other bonus-stage hiccup — same policy

        emit("done")
    except FatalProviderError:
        raise  # core provider auth failure — bubble up, the calling worker stops
    except Exception as e:
        sample.error = str(e)
        emit("failed")
    return sample


def build_sample_matrix(limit: int, app_types=None, seed_hints=None, seed: int = 42) -> list:
    """
    Returns `limit` (app_type, seed_hint) pairs, shuffled for variety, cycling back
    to the start if `limit` exceeds the number of unique combinations. Deterministic
    (fixed default seed) so a resumed run reproduces the same sequence and can safely
    pick up from wherever an interrupted run left off.
    """
    app_types = app_types or DEFAULT_APP_TYPES
    seed_hints = seed_hints or DEFAULT_SEED_HINTS
    combos = [(a, s) for a in app_types for s in seed_hints]
    rng = random.Random(seed)
    rng.shuffle(combos)
    return [combos[i % len(combos)] for i in range(limit)]


def split_matrix(items: list, n: int) -> list:
    """
    Splits `items` into `n` round-robin chunks (item[0] -> chunk 0, item[1] ->
    chunk 1, item[2] -> chunk 0, ...) rather than contiguous halves, so that if a
    dual-provider run is interrupted partway, both providers have touched a
    representative spread of app_types/seed_hints rather than one provider only
    ever reaching the back half of the matrix. n <= 1 returns a single chunk.
    """
    if n <= 1:
        return [list(items)]
    chunks = [[] for _ in range(n)]
    for i, item in enumerate(items):
        chunks[i % n].append(item)
    return chunks
