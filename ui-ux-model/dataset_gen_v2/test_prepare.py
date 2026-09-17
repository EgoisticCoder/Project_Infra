import json, tempfile, os
import prepare_training_data as p

# --- Build a synthetic dataset_gen output: one fully-populated row, one
# text-only row (no screenshot stage), one "done" but missing improved_code.
rows = [
    {
        "app_type": "fitness tracker", "seed_hint": "target audience: Gen Z",
        "status": "done", "final": "Use a bold gradient palette...",
        "screenshot_b64": "ZmFrZWJhc2U2NA==",
        "rating": "7/10 — clean but generic spacing.",
        "vision_critique": "Increase contrast on the CTA button...",
        "improved_code": "<!DOCTYPE html><html>...improved...</html>",
    },
    {
        "app_type": "banking app", "seed_hint": "primary goal: building trust",
        "status": "done", "final": "Use a navy/white palette...",
        # no screenshot stage fields at all
    },
    {
        "app_type": "podcast app", "seed_hint": "brand personality: playful",
        "status": "done", "final": "Use warm colors...",
        "screenshot_b64": "ZmFrZWJhc2U2NA==",
        "rating": "6/10 — needs work.",
        "vision_critique": "",       # empty on purpose -> should NOT emit this example
        "improved_code": "<!DOCTYPE html>...</html>",
    },
    {
        "app_type": "skip me", "seed_hint": "n/a",
        "status": "failed", "final": "",   # should be skipped entirely
    },
]

with tempfile.TemporaryDirectory() as d:
    own_path = os.path.join(d, "dataset.jsonl")
    with open(own_path, "w") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")

    examples = p.load_own_dataset(own_path)
    by_source = {}
    for ex in examples:
        by_source.setdefault(ex["source"], 0)
        by_source[ex["source"]] += 1

    print("Counts by source:", by_source)
    assert by_source.get("own_dataset") == 3, "3 done rows with final text"
    assert by_source.get("own_dataset_vision_rate") == 2, "row1 + row3 have rating"
    assert by_source.get("own_dataset_vision_improve") == 1, "only row1 has non-empty critique"
    assert by_source.get("own_dataset_vision_recreate") == 2, "row1 + row3 have improved_code"
    assert "own_dataset_vision_rate" not in [] # sanity

    # Multimodal shape check on one example
    rate_ex = next(ex for ex in examples if ex["source"] == "own_dataset_vision_rate")
    content = rate_ex["messages"][0]["content"]
    assert isinstance(content, list) and content[1]["type"] == "image_url"
    assert content[1]["image_url"]["url"].startswith("data:image/png;base64,")
    print("Multimodal example shape OK:", content[0]["text"])

    # include_vision_examples=False should suppress all 3 vision sources
    examples_no_vision = p.load_own_dataset(own_path, include_vision_examples=False)
    sources_no_vision = {ex["source"] for ex in examples_no_vision}
    assert sources_no_vision == {"own_dataset"}
    print("include_vision_examples=False correctly suppresses vision examples")

    # run_merge with both external datasets disabled (no network needed)
    out_path = os.path.join(d, "train_merged.jsonl")
    counts = p.run_merge(own_path, out_path, include_websight=False, include_screen2words=False,
                          progress_cb=lambda m: None)
    assert counts["_total"] == 8  # 3 own_dataset + 2 rate + 1 improve + 2 recreate
    print("run_merge counts:", counts)
    with open(out_path) as f:
        lines = f.readlines()
    assert len(lines) == counts["_total"]
    print("run_merge wrote", len(lines), "lines matching counts total — OK")

print("\nALL TESTS PASSED")
