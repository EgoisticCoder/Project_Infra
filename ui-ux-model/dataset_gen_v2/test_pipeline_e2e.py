import pipeline as pl

class FakeMessage:
    def __init__(self, content): self.content = content
class FakeChoice:
    def __init__(self, content): self.message = FakeMessage(content)
class FakeResponse:
    def __init__(self, content): self.choices = [FakeChoice(content)]

class FakeCompletions:
    def __init__(self, outer): self.outer = outer
    def create(self, model, messages, temperature, max_tokens):
        self.outer.calls.append(model)
        # Return something different depending on which stage this is,
        # so we can sanity check the right content flows to the right field.
        last_user_content = messages[-1]["content"]
        if isinstance(last_user_content, list):  # multimodal (vision) call
            text_part = next(p["text"] for p in last_user_content if p["type"] == "text")
            return FakeResponse(f"[vision reply to: {text_part[:20]}...]")
        if "Turn the following" in last_user_content:
            return FakeResponse("<!DOCTYPE html><html><body>mock site</body></html>")
        if "Rewrite the HTML" in last_user_content:
            return FakeResponse("<!DOCTYPE html><html><body>mock improved site</body></html>")
        return FakeResponse(f"[text reply #{len(self.outer.calls)}]")

class FakeChat:
    def __init__(self, outer): self.completions = FakeCompletions(outer)

class FakeClient:
    def __init__(self):
        self.calls = []
        self.chat = FakeChat(self)

# --- Test 1: core pipeline only (no screenshot stage) ---
client = FakeClient()
statuses = []
sample = pl.run_pipeline_for_sample(
    client, "fake-model", "banking app", "target audience: Gen Z", "fake-provider",
    status_cb=lambda s: statuses.append(s.status),
)
assert sample.status == "done", sample.status
assert sample.draft and sample.critique and sample.final
assert statuses == ["drafting", "grounding", "critiquing", "revising", "done"]
print("Core pipeline (no screenshot) OK — statuses:", statuses)

# --- Test 2: screenshot stage enabled — Playwright IS available here, so this
# verifies the full implement -> render -> rate/improve/recreate chain for real,
# not just its failure path.
client2 = FakeClient()
statuses2 = []
sample2 = pl.run_pipeline_for_sample(
    client2, "fake-model", "fitness tracker", "brand personality: bold", "fake-provider",
    status_cb=lambda s: statuses2.append(s.status),
    enable_screenshot=True, code_model="fake-code-model", vision_model="fake-vision-model",
)
assert sample2.status == "done", sample2.status
assert sample2.code.startswith("<!DOCTYPE html>"), "implement_code should have run"
assert sample2.screenshot_b64, "Playwright is installed here — render should have succeeded"
assert len(sample2.screenshot_b64) > 100, "screenshot_b64 should be a real (non-trivial) PNG"
assert sample2.rating.startswith("[vision reply"), "rate_screenshot should have run"
assert sample2.vision_critique.startswith("[vision reply"), "vision_critique should have run"
assert sample2.improved_code.startswith("<!DOCTYPE html>"), "recreate_code should have run"
expected_stages = ["drafting", "grounding", "critiquing", "revising",
                   "implementing", "rendering", "rating", "vision_critiquing", "recreating", "done"]
assert statuses2 == expected_stages, statuses2
print("Full screenshot stage (real Playwright render + fake models) OK — statuses:", statuses2)
print(f"  screenshot_b64 length: {len(sample2.screenshot_b64)} chars")
print(f"  rating: {sample2.rating!r}")
print(f"  vision_critique: {sample2.vision_critique!r}")

# --- Test 2b: force a render failure (monkeypatch) and confirm graceful
# degradation — downstream stages skipped, sample still "done", core text kept.
_real_render = pl.render_screenshot
pl.render_screenshot = lambda *a, **kw: None
try:
    client2b = FakeClient()
    statuses2b = []
    sample2b = pl.run_pipeline_for_sample(
        client2b, "fake-model", "podcast app", "context: brand new product launch", "fake-provider",
        status_cb=lambda s: statuses2b.append(s.status),
        enable_screenshot=True, code_model="fake-code-model", vision_model="fake-vision-model",
    )
finally:
    pl.render_screenshot = _real_render

assert sample2b.status == "done", sample2b.status
assert sample2b.final, "core draft/critique/revise text must survive a render failure"
assert sample2b.code.startswith("<!DOCTYPE html>"), "implement_code still ran before the render"
assert sample2b.screenshot_b64 == "" and sample2b.rating == "" and sample2b.vision_critique == "" \
    and sample2b.improved_code == "", "everything past a failed render should stay empty"
assert "rating" not in statuses2b, "should never reach rating if render_screenshot returned None"
print("Forced render failure degrades gracefully OK — statuses:", statuses2b)

# --- Test 3: split_matrix + dual "provider" simulation at the pipeline level ---
matrix = pl.build_sample_matrix(6)
chunks = pl.split_matrix(matrix, 2)
assert len(chunks[0]) + len(chunks[1]) == 6
assert chunks[0] != chunks[1]
clientA, clientB = FakeClient(), FakeClient()
resultsA = [pl.run_pipeline_for_sample(clientA, "m", a, s, "A") for a, s in chunks[0]]
resultsB = [pl.run_pipeline_for_sample(clientB, "m", a, s, "B") for a, s in chunks[1]]
assert all(r.status == "done" for r in resultsA + resultsB)
assert len(clientA.calls) == len(chunks[0]) * 3  # draft, critique, revise per sample
assert len(clientB.calls) == len(chunks[1]) * 3
print(f"Dual-provider split OK — A handled {len(chunks[0])} samples, B handled {len(chunks[1])}")

print("\nALL PIPELINE E2E TESTS PASSED")
