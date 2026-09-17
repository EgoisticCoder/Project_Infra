"""
prepare_training_data.py — merges your own generated dataset with selected
external datasets into one training file for the LoRA fine-tune step.

RESEARCH NOTE (see chat for full writeup): of the datasets evaluated, only
WebSight is actually a fit for THIS model's task (text UI/UX advice + the
rate/improve/recreate screenshot bonus). The others are real, legitimate
datasets, but built for different tasks (screen captioning, GUI-agent action
prediction, object detection) — mixing them in as (prompt, output) pairs would
teach the model to imitate the wrong task, not add helpful variety.

IMPORTANT LIMITATION: FIELD_MAP below was verified against a real --inspect
run for websight/screen2words (see chat) — trust those two. If you add another
dataset later, run --inspect again before trusting its FIELD_MAP entry; column
names on dataset cards drift and are not guaranteed accurate without a live check.

This module is usable two ways:
  1. CLI:  python3 prepare_training_data.py --own-dataset dataset.jsonl --include-websight
  2. GUI:  app.py's "Merge datasets" screen imports run_merge() directly and
     drives it with checkboxes/inputs instead of CLI flags — same logic, same
     FIELD_MAP, so the two stay in sync by construction rather than by hand.
"""

import argparse
import json
import random
from pathlib import Path
from typing import Callable, Optional


# Column names VERIFIED against a real --inspect run (see chat) — no longer guesses.
FIELD_MAP = {
    "websight": {"code": "text", "idea": "llm_generated_idea", "image": "image"},
    "screen2words": {"captions": "captions", "image": "image"},
}

# What's actually recommended to turn on, and why — shown in both the CLI help
# and the GUI's merge screen labels.
RECOMMENDED_DEFAULTS = {
    "websight": True,        # real (code, screenshot) pairs — matches the implement/recreate stage
    "screen2words": False,   # screen->caption is the reverse task of what you need; off by default
}


def load_own_dataset(path: str, include_vision_examples: bool = True) -> list:
    """
    Load your dataset_gen JSONL output into chat-format training examples.

    Every "done" row contributes the core text example (app_type/seed_hint ->
    final design recommendations). If the row also has a rendered screenshot
    (screenshot_b64) from the optional pipeline stage, and include_vision_examples
    is True, it additionally contributes up to three multimodal examples — one
    per query type the deployed model needs to handle for an uploaded screenshot:
    rate it, improve it, recreate it — each only if that field is non-empty,
    so a partial/failed bonus stage doesn't emit an empty-answer example.
    """
    examples = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            row = json.loads(line)
            if row.get("status") != "done" or not row.get("final"):
                continue

            examples.append({
                "messages": [
                    {"role": "user", "content": (
                        f"Design a UI/UX concept for a {row['app_type']}. "
                        f"Context: {row['seed_hint']}."
                    )},
                    {"role": "assistant", "content": row["final"]},
                ],
                "source": "own_dataset",
            })

            screenshot_b64 = row.get("screenshot_b64")
            if include_vision_examples and screenshot_b64:
                image_url = {"url": f"data:image/png;base64,{screenshot_b64}"}

                if row.get("rating"):
                    examples.append({
                        "messages": [
                            {"role": "user", "content": [
                                {"type": "text", "text": "Rate this website's UI/UX."},
                                {"type": "image_url", "image_url": image_url},
                            ]},
                            {"role": "assistant", "content": row["rating"]},
                        ],
                        "source": "own_dataset_vision_rate",
                    })

                if row.get("vision_critique"):
                    examples.append({
                        "messages": [
                            {"role": "user", "content": [
                                {"type": "text", "text": "Here is my website's current UI. "
                                                          "What would you recommend to make it better?"},
                                {"type": "image_url", "image_url": image_url},
                            ]},
                            {"role": "assistant", "content": row["vision_critique"]},
                        ],
                        "source": "own_dataset_vision_improve",
                    })

                if row.get("improved_code"):
                    examples.append({
                        "messages": [
                            {"role": "user", "content": [
                                {"type": "text", "text": "Recreate this website with a better UI."},
                                {"type": "image_url", "image_url": image_url},
                            ]},
                            {"role": "assistant", "content": row["improved_code"]},
                        ],
                        "source": "own_dataset_vision_recreate",
                    })
    return examples


def _websight_row_to_examples(row: dict, field_map: dict) -> list:
    """Pure transform, kept separate from the network fetch so it's unit-testable."""
    code = row.get(field_map["code"])
    idea = row.get(field_map["idea"])
    out = []
    if code:
        instruction = (f"Generate the HTML/CSS for this website design: {idea}"
                        if idea else "Generate the HTML/CSS for this website design.")
        out.append({
            "messages": [
                {"role": "user", "content": instruction},
                {"role": "assistant", "content": code},
            ],
            "source": "websight_code",
        })
    if idea:
        out.append({
            "messages": [
                {"role": "user", "content": "Describe a UI/UX concept for a website."},
                {"role": "assistant", "content": idea},
            ],
            "source": "websight_idea_text",
        })
    return out


def _screen2words_row_to_example(row: dict, field_map: dict) -> Optional[dict]:
    """Pure transform, kept separate from the network fetch so it's unit-testable.
    `captions` is a list in the real dataset (verified via --inspect) — several
    workers captioned the same screen; we use the first one rather than joining."""
    captions = row.get(field_map["captions"])
    if not captions:
        return None
    caption = captions[0] if isinstance(captions, list) else captions
    if not caption:
        return None
    return {
        "messages": [
            {"role": "user", "content": "Describe what this mobile screen shows."},
            {"role": "assistant", "content": caption},
        ],
        "source": "screen2words",
    }


def load_websight(limit: int = 0, progress_cb: Optional[Callable[[int], None]] = None) -> list:
    """limit <= 0 means "use all" (823k rows) — this is a deliberate choice you
    made explicitly (see chat), not a default; balance it at TRAIN time via
    sampling ratio, not by capping it here. progress_cb(count), if given, is
    called every 500 rows so a GUI can show live progress on a long pull."""
    from datasets import load_dataset
    ds = load_dataset("HuggingFaceM4/WebSight", split="train", streaming=True)
    examples = []
    for i, row in enumerate(ds):
        if limit > 0 and i >= limit:
            break
        examples.extend(_websight_row_to_examples(row, FIELD_MAP["websight"]))
        if progress_cb and i % 500 == 0:
            progress_cb(i)
    return examples


def load_screen2words(limit: int = 0, progress_cb: Optional[Callable[[int], None]] = None) -> list:
    """Same limit<=0 semantics as load_websight. Still not recommended (see
    RECOMMENDED_DEFAULTS) — this only runs if the caller explicitly opts in."""
    from datasets import load_dataset
    ds = load_dataset("rootsautomation/RICO-Screen2Words", split="train", streaming=True)
    examples = []
    for i, row in enumerate(ds):
        if limit > 0 and i >= limit:
            break
        ex = _screen2words_row_to_example(row, FIELD_MAP["screen2words"])
        if ex:
            examples.append(ex)
        if progress_cb and i % 500 == 0:
            progress_cb(i)
    return examples


def inspect_remote_datasets() -> None:
    """Prints real column names + a sample row for each external dataset. Run this
    FIRST, on a machine with HF access, before trusting FIELD_MAP above."""
    from datasets import load_dataset
    targets = [
        ("HuggingFaceM4/WebSight", None),
        ("rootsautomation/RICO-Screen2Words", None),
    ]
    for name, config in targets:
        print(f"\n=== {name} ===")
        try:
            ds = load_dataset(name, config, split="train", streaming=True)
            first = next(iter(ds))
            print("Columns:", list(first.keys()))
            for k, v in first.items():
                print(f"  {k}: {str(v)[:200]}")
        except Exception as e:
            print(f"Could not inspect: {e}")


def run_merge(own_dataset_path: str, output_path: str,
              include_websight: bool = True, websight_limit: int = 0,
              include_screen2words: bool = False, screen2words_limit: int = 0,
              include_vision_examples: bool = True, seed: int = 42,
              progress_cb: Optional[Callable[[str], None]] = None) -> dict:
    """
    Single entry point used by BOTH the CLI (__main__ below) and the GUI's
    "Merge datasets" screen, so the two never drift apart. progress_cb(msg), if
    given, receives short human-readable status lines as the merge proceeds.

    Returns a dict of counts by source, e.g. {"own_dataset": 412,
    "own_dataset_vision_rate": 88, "websight_code": 3000, ...} plus "_total".
    """
    def log(msg: str):
        if progress_cb:
            progress_cb(msg)

    all_examples = load_own_dataset(own_dataset_path, include_vision_examples=include_vision_examples)
    log(f"Own dataset: {len(all_examples)} examples")

    if include_websight:
        ws = load_websight(websight_limit, progress_cb=(lambda i: log(f"WebSight: {i} rows so far...")))
        log(f"WebSight: {len(ws)} examples")
        all_examples.extend(ws)

    if include_screen2words:
        log("WARNING: Screen2Words is screen-captioning (image -> description), the reverse "
            "of your design-generation task. Including it can teach the model the wrong direction.")
        s2w = load_screen2words(screen2words_limit,
                                 progress_cb=(lambda i: log(f"Screen2Words: {i} rows so far...")))
        log(f"Screen2Words: {len(s2w)} examples")
        all_examples.extend(s2w)

    rng = random.Random(seed)
    rng.shuffle(all_examples)

    with open(output_path, "w", encoding="utf-8") as f:
        for ex in all_examples:
            f.write(json.dumps(ex, ensure_ascii=False) + "\n")

    counts: dict = {}
    for ex in all_examples:
        counts[ex["source"]] = counts.get(ex["source"], 0) + 1
    counts["_total"] = len(all_examples)
    log(f"Wrote {len(all_examples)} total examples to {output_path}")
    return counts


def main():
    parser = argparse.ArgumentParser(
        description="Merge your dataset_gen output with selected external datasets for fine-tuning."
    )
    parser.add_argument("--own-dataset", help="Path to your dataset_gen JSONL output.")
    parser.add_argument("--output", default="train_merged.jsonl", help="Merged output path.")
    parser.add_argument("--include-websight", action="store_true", default=True,
                         help="Include WebSight (recommended, on by default).")
    parser.add_argument("--no-websight", dest="include_websight", action="store_false",
                         help="Disable WebSight.")
    parser.add_argument("--websight-limit", type=int, default=0,
                         help="Cap WebSight rows. 0 = use all 823k (default — see chat for the "
                              "balance-at-train-time reasoning).")
    parser.add_argument("--include-screen2words", action="store_true", default=False,
                         help="Include Screen2Words. NOT recommended — wrong task direction.")
    parser.add_argument("--screen2words-limit", type=int, default=0,
                         help="Cap Screen2Words rows. 0 = use all.")
    parser.add_argument("--no-vision-examples", dest="include_vision_examples",
                         action="store_false", default=True,
                         help="Skip the rate/improve/recreate screenshot examples even if present.")
    parser.add_argument("--inspect", action="store_true",
                         help="Print real schema of external datasets and exit (no merge).")
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    if args.inspect:
        inspect_remote_datasets()
        return

    if not args.own_dataset:
        parser.error("--own-dataset is required unless using --inspect")

    counts = run_merge(
        own_dataset_path=args.own_dataset, output_path=args.output,
        include_websight=args.include_websight, websight_limit=args.websight_limit,
        include_screen2words=args.include_screen2words, screen2words_limit=args.screen2words_limit,
        include_vision_examples=args.include_vision_examples, seed=args.seed,
        progress_cb=print,
    )
    print("\nSource mix:")
    for source, count in sorted(counts.items()):
        if source != "_total":
            print(f"  {source}: {count}")
    print(f"  TOTAL: {counts['_total']}")


if __name__ == "__main__":
    main()
