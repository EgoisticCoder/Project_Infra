"""
prepare_training_data.py — merges your own generated dataset with selected
external datasets into one training file for the LoRA fine-tune step.

RESEARCH NOTE (see chat for full writeup): of the datasets you found, only
WebSight is actually a fit for THIS model's task (text UI/UX advice + a
bonus code/screenshot). The others are real, legitimate datasets, but built
for different tasks (screen captioning, GUI-agent action prediction, object
detection) — mixing them in as (prompt, output) pairs would teach the model
to imitate the wrong task, not add helpful variety. Details on --include
flags below.

IMPORTANT LIMITATION: this was written and syntax/logic-tested in an
environment with no network access to huggingface.co, so the exact column
names in FIELD_MAP below are my best reading of each dataset's public card,
NOT independently verified against a live download. Run:

    python3 prepare_training_data.py --inspect

first, on a machine that does have HF access, before trusting a real merge.
It prints each dataset's actual columns + a sample row so you can fix
FIELD_MAP if anything's off.
"""

import argparse
import json
import random
from pathlib import Path


# Column names VERIFIED against a real --inspect run (see chat) — no longer guesses.
FIELD_MAP = {
    "websight": {"code": "text", "idea": "llm_generated_idea", "image": "image"},
    "screen2words": {"captions": "captions", "image": "image"},
}

# What I'd actually turn on. See the chat writeup for the full reasoning per dataset.
RECOMMENDED_DEFAULTS = {
    "websight": True,        # real (code, screenshot) pairs — directly matches your bonus feature
    "screen2words": False,   # screen->caption is the reverse task of what you need; off by default
}


def load_own_dataset(path: str) -> list:
    """
    Load your dataset_gen JSONL output (app_type/seed_hint/final) into
    chat-format training examples for the primary text-advice task.
    Only rows with status == "done" are used.
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
    return examples


def _websight_row_to_examples(row: dict, field_map: dict) -> list:
    """
    Pure transform, kept separate from the network fetch so it's unit-testable.
    Returns 0-2 examples per row:
      - code example: idea text -> HTML/CSS (matches your bonus code+screenshot feature)
      - text example: a generic prompt -> the idea text itself, tagged separately so you
        can exclude it later if it turns out to dilute your own pipeline's more detailed
        style (WebSight's idea briefs are shorter/less structured than your generate->
        ground->critique->revise output).
    """
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


def _screen2words_row_to_example(row: dict, field_map: dict) -> dict | None:
    """Pure transform, kept separate from the network fetch so it's unit-testable.
    `captions` is a list in the real dataset (verified via --inspect) — several workers
    captioned the same screen; we use the first one rather than joining or averaging."""
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


def load_websight() -> list:
    """Streams the ENTIRE WebSight dataset (823k rows) — no cap, per your instruction.
    Reality check: this merges to ~98% WebSight / ~2% your own dataset by row count.
    That imbalance should be corrected via sampling weights in your actual fine-tune
    script (oversample own_dataset, downweight websight_*), not by capping here."""
    from datasets import load_dataset
    ds = load_dataset("HuggingFaceM4/WebSight", split="train", streaming=True)
    ds = ds.remove_columns(["image"])  # reduces memory/decode cost; likely NOT network bandwidth,
                                        # since streaming typically still fetches whole parquet shards
    examples = []
    for i, row in enumerate(ds, start=1):
        examples.extend(_websight_row_to_examples(row, FIELD_MAP["websight"]))
        if i % 10000 == 0:
            print(f"  ...WebSight: {i} rows processed, {len(examples)} examples so far")
    return examples


def load_screen2words() -> list:
    """Streams the ENTIRE Screen2Words dataset — no cap, per your instruction.
    Still not recommended (see chat) — this only runs if you pass --include-screen2words."""
    from datasets import load_dataset
    ds = load_dataset("rootsautomation/RICO-Screen2Words", split="train", streaming=True)
    drop_cols = [c for c in ["image", "image_icon", "image_semantic"] if c in ds.column_names]
    if drop_cols:
        ds = ds.remove_columns(drop_cols)
    examples = []
    for i, row in enumerate(ds, start=1):
        ex = _screen2words_row_to_example(row, FIELD_MAP["screen2words"])
        if ex:
            examples.append(ex)
        if i % 10000 == 0:
            print(f"  ...Screen2Words: {i} rows processed, {len(examples)} examples so far")
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


def main():
    parser = argparse.ArgumentParser(
        description="Merge your dataset_gen output with selected external datasets for fine-tuning."
    )
    parser.add_argument("--own-dataset", help="Path to your dataset_gen JSONL output.")
    parser.add_argument("--output", default="train_merged.jsonl", help="Merged output path.")
    parser.add_argument("--include-websight", action="store_true",
                         help="Include the FULL WebSight dataset (823k rows, no cap). Recommended.")
    parser.add_argument("--include-screen2words", action="store_true",
                         help="Include the FULL Screen2Words dataset (no cap). NOT recommended — "
                              "wrong task direction for this model (see README).")
    parser.add_argument("--merge-all", action="store_true",
                         help="Shortcut for --include-websight --include-screen2words together, "
                              "i.e. use every dataset this script knows about. Screen2Words still "
                              "prints its warning — this flag doesn't silence that.")
    parser.add_argument("--inspect", action="store_true",
                         help="Print real schema of external datasets and exit (no merge).")
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    if args.inspect:
        inspect_remote_datasets()
        return

    if not args.own_dataset:
        parser.error("--own-dataset is required unless using --inspect")

    use_websight = args.include_websight or args.merge_all
    use_screen2words = args.include_screen2words or args.merge_all

    all_examples = load_own_dataset(args.own_dataset)
    counts = {"own_dataset": len(all_examples)}
    print(f"Own dataset:    {counts['own_dataset']} examples")

    if use_websight:
        print("Streaming WebSight (823k rows — this takes a while)...")
        ws = load_websight()
        counts["websight_code"] = sum(1 for e in ws if e["source"] == "websight_code")
        counts["websight_idea_text"] = sum(1 for e in ws if e["source"] == "websight_idea_text")
        print(f"WebSight code:  {counts['websight_code']} examples")
        print(f"WebSight text:  {counts['websight_idea_text']} examples")
        all_examples.extend(ws)

    if use_screen2words:
        print("WARNING: Screen2Words is screen-captioning (image -> description), the reverse "
              "of your design-generation task. Including it can teach the model the wrong "
              "direction. Proceeding since you asked for all datasets.")
        print("Streaming Screen2Words...")
        s2w = load_screen2words()
        counts["screen2words"] = len(s2w)
        print(f"Screen2Words:   {counts['screen2words']} examples")
        all_examples.extend(s2w)

    rng = random.Random(args.seed)
    rng.shuffle(all_examples)

    with open(args.output, "w", encoding="utf-8") as f:
        for ex in all_examples:
            f.write(json.dumps(ex, ensure_ascii=False) + "\n")

    total = len(all_examples)
    print(f"\nWrote {total} total examples to {args.output}")
    print("Source breakdown:")
    for source, count in counts.items():
        pct = 100 * count / total if total else 0
        print(f"  {source:20s} {count:>8,} ({pct:5.1f}%)")
    if counts.get("websight_code", 0) + counts.get("websight_idea_text", 0) > counts["own_dataset"] * 5:
        print("\nNOTE: your own dataset is a small fraction of this file. Apply sampling weights "
              "in your fine-tune script (oversample own_dataset) rather than treating these raw "
              "counts as the training mixture — see the chat writeup.")


if __name__ == "__main__":
    main()
