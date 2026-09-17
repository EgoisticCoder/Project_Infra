"""Validate Forma v2 JSONL records without requiring model or browser packages."""

import json
import sys
from pathlib import Path

REQUIRED = {
    "example_id", "task", "constraints", "research_evidence", "design_spec",
    "initial_code", "render_report", "critic_feedback", "corrected_code",
    "quality_score", "status", "source",
}
SPEC_REQUIRED = {
    "information_architecture", "layout", "tokens", "typography", "components",
    "responsive_rules", "interaction_states", "accessibility",
}


def validate(path: str) -> int:
    errors = []
    ids = set()
    count = 0
    for line_number, line in enumerate(Path(path).read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        count += 1
        try:
            row = json.loads(line)
        except json.JSONDecodeError as error:
            errors.append(f"line {line_number}: invalid JSON: {error}")
            continue
        missing = REQUIRED - row.keys()
        if missing:
            errors.append(f"line {line_number}: missing fields: {sorted(missing)}")
        example_id = row.get("example_id")
        if example_id in ids:
            errors.append(f"line {line_number}: duplicate example_id: {example_id}")
        ids.add(example_id)
        spec = row.get("design_spec", {})
        if SPEC_REQUIRED - spec.keys():
            errors.append(f"line {line_number}: incomplete design_spec")
        for field in ("initial_code", "corrected_code"):
            code = row.get(field, "")
            if not isinstance(code, str) or "<!doctype html>" not in code.lower() or "</html>" not in code.lower():
                errors.append(f"line {line_number}: {field} is not a complete HTML document")
        if not isinstance(row.get("critic_feedback"), list) or not row.get("critic_feedback"):
            errors.append(f"line {line_number}: critic_feedback must be a non-empty list")

    print(f"Records checked: {count}")
    print(f"Unique IDs: {len(ids)}")
    if errors:
        print(f"Validation errors: {len(errors)}")
        print("\n".join(f"- {error}" for error in errors))
        return 1
    print("Validation passed.")
    return 0


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("Usage: python validate_v2_dataset.py <records.jsonl>")
    raise SystemExit(validate(sys.argv[1]))
