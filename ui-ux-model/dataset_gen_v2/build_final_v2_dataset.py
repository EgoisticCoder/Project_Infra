#!/usr/bin/env python3
"""Build a conservative final candidate from the reviewed corpus.

Records with corrected-page runtime errors, horizontal overflow, unlabeled
controls, missing image alt text, missing focus treatment, or structural
landmark defects are rejected. Medium touch-target findings remain explicitly
recorded because the detector can flag ordinary text links; they still need
manual review before release.
"""
from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

INPUT = Path("v2_review_ready.jsonl")
OUTPUT = Path("v2_training_candidate.jsonl")
REJECTED = Path("v2_training_rejected.jsonl")
MANIFEST = Path("v2_training_candidate.manifest.json")


def reject_reason(findings: list[dict]) -> list[str]:
    reasons = []
    for finding in findings:
        text = finding["text"].lower()
        if finding.get("severity") == "high":
            reasons.append(finding["text"])
        elif any(term in text for term in ("overflows horizontally", "browser error", "unlabeled interactive", "missing an alt", "removes focus outlines", "no <main>", "no visible h1", "uses onclick")):
            reasons.append(finding["text"])
    return reasons


rows = [json.loads(line) for line in INPUT.read_text(encoding="utf-8").splitlines() if line.strip()]
accepted, rejected = [], []
for row in rows:
    reasons = reject_reason(row.get("audit_findings", []))
    if reasons:
        row["status"] = "rejected_objective_audit"
        row["rejection_reasons"] = reasons
        rejected.append(row)
    else:
        row["status"] = "accepted_objective_audit_needs_visual_review"
        accepted.append(row)

for path, data in ((OUTPUT, accepted), (REJECTED, rejected)):
    with path.open("w", encoding="utf-8") as handle:
        for row in data:
            handle.write(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n")

manifest = {
    "input": str(INPUT), "output": str(OUTPUT), "rejected_output": str(REJECTED),
    "input_records": len(rows), "accepted_records": len(accepted), "rejected_records": len(rejected),
    "rejection_reasons": dict(Counter(reason for row in rejected for reason in row["rejection_reasons"])),
    "visual_scores_assigned": False, "screenshots_embedded": False,
    "ready_for_public_release": False,
    "ready_for_preliminary_sft": True,
    "warning": "Accepted records passed objective checks but still require visual/human review before production training or release.",
}
MANIFEST.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
print(json.dumps(manifest, indent=2))
