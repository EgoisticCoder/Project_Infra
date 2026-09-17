# Forma V2 dataset audit

## Decision

`v2_merged_candidate.jsonl` is the clean merge candidate. It is structurally valid and safe to use as the next review/training candidate. The original files under `outputs/` were not modified or deleted.

## Merge accounting

| Source | Input rows | Kept |
|---|---:|---:|
| `outputs/forma_single_300.jsonl` | 300 | 300 |
| `outputs/forma_v2_unique_200_batch2.jsonl` | 200 | 200 |
| `v2_generated_100_rendered.jsonl` | 100 | 20 |
| `v2_seed_dataset.jsonl` | 3 | 3 |
| **Total** | **603** | **523** |

The 80 excluded generated rows were exact content duplicates of other generated rows. They had different IDs, but the task/spec/code/fix content was identical. Keeping them would overweight repeated examples during fine-tuning.

The other output files were snapshots or supersets:

- `forma_single_100.jsonl` and `forma_single_101_300.jsonl` are subsets of `forma_single_300.jsonl`.
- `forma_v2_unique_100.jsonl` is effectively a subset of `forma_v2_unique_300.jsonl`.
- `forma_v2_unique_300.jsonl` contains the 100-record set plus the 200-record batch.

They are therefore intentionally not re-added to the merge.

## Validation results

- JSONL parsing: passed.
- Required schema validation: passed for all 523 merged records.
- Unique example IDs: 523/523.
- Duplicate normalized task keys: none.
- High-overlap task/spec summaries: none detected by the dependency-free audit.
- Statuses: 500 `needs_review`, 20 `rendered_needs_visual_review`, 3 `accepted_seed`.
- Browser-tested sample: 100/100 generated records rendered successfully; 0 initial mobile overflow, 0 corrected mobile overflow, and 0 initial/corrected console errors.

## Important limitation

The 500 records from the external output batches have not all received browser rendering or human visual review. Structural checks passing does not prove visual quality, accessibility, or design quality. Before final fine-tuning, render those records in chunks and assign visual/UX scores; exclude records with broken layouts, generic copy, repeated layouts, or weak corrections.

## Reproducibility

Run:

```bash
python merge_v2_outputs.py
python validate_v2_dataset.py v2_merged_candidate.jsonl
python audit_v2_candidate.py
```

The merge is deterministic and writes a manifest explaining every removed duplicate.

## Completed objective audit

`complete_v2_quality_pipeline.py` writes `v2_review_ready.jsonl` after testing every initial and corrected document at 1440x900 and 390x844. It also canonicalizes every `design_spec.tokens` object to the same eight keys and adds `audit_findings` and `recommendations` fields.

The pass found 1,072 responsive findings and 300 accessibility-structure findings in corrected documents. This output is a review queue, not an automatically accepted training set. Visual scores are deliberately still null and screenshots are not embedded; a reviewer must inspect the pages and accept/reject records before SFT.
