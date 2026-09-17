#!/usr/bin/env python3
"""Small dependency-free audit for merged Forma training records."""
from __future__ import annotations

import hashlib
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

INPUT = Path("v2_merged_candidate.jsonl")
OUTPUT = Path("v2_merged_candidate.audit.json")


def text(record: dict, *keys: str) -> str:
    parts = []
    for key in keys:
        value = record.get(key, "")
        if isinstance(value, (dict, list)):
            value = json.dumps(value, sort_keys=True)
        parts.append(str(value))
    return " ".join(parts)


def normalize(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", value.lower()).strip()


records = [json.loads(line) for line in INPUT.read_text(encoding="utf-8").splitlines() if line.strip()]
ids = [str(record.get("example_id", record.get("id", ""))) for record in records]
tasks = [normalize(text(record, "task")) for record in records]
task_counts = Counter(tasks)

# Compare compact task/spec summaries, not full HTML. This catches repeated design briefs
# while avoiding false positives caused by shared CSS boilerplate.
summaries = [set(normalize(text(record, "task", "design_spec", "constraints")).split()) for record in records]
near_pairs = []
for i in range(len(records)):
    for j in range(i + 1, len(records)):
        if not summaries[i] or not summaries[j]:
            continue
        union = summaries[i] | summaries[j]
        score = len(summaries[i] & summaries[j]) / len(union) if union else 0.0
        if score >= 0.92:
            near_pairs.append({"id_a": ids[i], "id_b": ids[j], "score": round(score, 4)})

report = {
    "input": str(INPUT),
    "rows": len(records),
    "unique_ids": len(set(ids)),
    "duplicate_ids": sorted([item for item, count in Counter(ids).items() if count > 1]),
    "duplicate_normalized_tasks": {task: count for task, count in task_counts.items() if count > 1},
    "status_counts": dict(Counter(str(record.get("status", "")) for record in records)),
    "near_duplicate_summary_pairs_at_0_92": near_pairs,
    "sha256": hashlib.sha256(INPUT.read_bytes()).hexdigest(),
}
OUTPUT.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
print(json.dumps({
    "rows": report["rows"],
    "unique_ids": report["unique_ids"],
    "duplicate_task_keys": len(report["duplicate_normalized_tasks"]),
    "near_duplicate_pairs": len(near_pairs),
    "output": str(OUTPUT),
}, indent=2))
