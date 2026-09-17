"""Merge only non-snapshot Forma v2 batches with exact-content deduplication."""

from __future__ import annotations

import hashlib
import json
from collections import Counter
from pathlib import Path

SOURCES = [
    Path("outputs/forma_single_300.jsonl"),
    Path("outputs/forma_v2_unique_200_batch2.jsonl"),
    Path("v2_generated_100_rendered.jsonl"),
    Path("v2_seed_dataset.jsonl"),
]


def fingerprint(row: dict) -> str:
    fields = {
        key: row.get(key)
        for key in (
            "task", "constraints", "research_evidence", "design_spec",
            "initial_code", "critic_feedback", "corrected_code",
        )
    }
    return hashlib.sha256(json.dumps(fields, sort_keys=True, ensure_ascii=False).encode()).hexdigest()


def main() -> None:
    output = Path("v2_merged_candidate.jsonl")
    manifest_path = Path("v2_merged_candidate.manifest.json")
    accepted = []
    seen_fingerprints: dict[str, str] = {}
    seen_ids: dict[str, str] = {}
    report = {"sources": {}, "duplicate_records_removed": [], "invalid_records_removed": []}

    for source in SOURCES:
        rows = 0
        accepted_from_source = 0
        for line_number, line in enumerate(source.read_text(encoding="utf-8").splitlines(), 1):
            if not line.strip():
                continue
            rows += 1
            try:
                row = json.loads(line)
            except json.JSONDecodeError as error:
                report["invalid_records_removed"].append({"source": str(source), "line": line_number, "reason": str(error)})
                continue
            example_id = row.get("example_id")
            fp = fingerprint(row)
            if not example_id or example_id in seen_ids:
                report["duplicate_records_removed"].append({"source": str(source), "line": line_number, "example_id": example_id, "reason": "duplicate example_id"})
                continue
            if fp in seen_fingerprints:
                report["duplicate_records_removed"].append({"source": str(source), "line": line_number, "example_id": example_id, "duplicate_of": seen_fingerprints[fp], "reason": "duplicate content fingerprint"})
                continue
            required = ("task", "design_spec", "initial_code", "corrected_code", "critic_feedback")
            if any(not row.get(field) for field in required):
                report["invalid_records_removed"].append({"source": str(source), "line": line_number, "example_id": example_id, "reason": "missing required value"})
                continue
            seen_ids[example_id] = str(source)
            seen_fingerprints[fp] = example_id
            accepted.append(row)
            accepted_from_source += 1
        report["sources"][str(source)] = {"input_rows": rows, "accepted_rows": accepted_from_source}

    with output.open("w", encoding="utf-8") as handle:
        for row in accepted:
            handle.write(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n")

    statuses = Counter(row.get("status") for row in accepted)
    report.update({
        "output": str(output),
        "input_rows": sum(item["input_rows"] for item in report["sources"].values()),
        "accepted_rows": len(accepted),
        "unique_example_ids": len(seen_ids),
        "duplicate_rows_removed": len(report["duplicate_records_removed"]),
        "invalid_rows_removed": len(report["invalid_records_removed"]),
        "statuses": dict(statuses),
        "requires_semantic_review": True,
        "note": "Exact duplicates are removed. A reviewer must still check semantic similarity before training.",
    })
    manifest_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
