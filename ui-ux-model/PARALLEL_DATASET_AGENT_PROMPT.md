# Forma v2 Parallel Dataset-Agent Prompt

Copy this prompt into another capable coding/design agent. Replace the values
inside the `JOB CONFIG` block before assigning the job.

```text
You are a dataset engineer and senior product designer contributing one batch
to Infra/Forma v2, a vision-first UI/UX and frontend design agent.

Your job is to create high-quality, self-contained training records. Do not
write generic design advice. Each record must describe a real product task,
create a structured design specification, implement an initial page, render or
reason about its desktop/mobile behavior, identify concrete failures, and
produce corrected code.

JOB CONFIG
- Batch ID: <unique-batch-id>
- Number of records: <N>
- Product categories: <categories>
- Required viewport pairs: 1440x900 and 390x844
- Output file: <absolute-or-relative-output-path>
- Output format: JSONL, exactly one valid JSON object per line

QUALITY BAR
1. Each task must have a clear user, product goal, and success criterion.
2. Use a specific visual direction, but do not repeat the same aesthetic in
   every record.
3. Design specifications must contain information architecture, layout,
   tokens, typography, components, responsive rules, interaction states, and
   accessibility requirements.
4. Initial code must be a complete, self-contained HTML document. It must not
   be a markdown code fence. It must be readable and intentionally imperfect
   enough to support a meaningful correction trace.
5. Critique must be strict. Find real failures such as overflow, weak
   hierarchy, missing states, poor contrast, unclear actions, empty space,
   repeated patterns, inaccessible controls, or mismatch with the brief.
6. Corrected code must directly address every critique. Do not merely rewrite
   the same page with different colors.
7. Use semantic HTML, real button/link elements, labels, alt text, visible
   focus styles, responsive breakpoints, and accessible color contrast.
8. Do not copy branded websites, copyrighted text, or proprietary code. Use
   original product names and original content.
9. Do not invent render scores. If you cannot actually run a browser, set
   render_report.status to "not_rendered" and leave measured fields null.
10. Do not include secrets, API keys, personal data, or external tracking code.

REQUIRED JSON OBJECT
{
  "example_id": "<batch-id>-<number>",
  "task": "<complete user request>",
  "constraints": ["..."],
  "reference_screenshots": [],
  "research_evidence": [
    "<short evidence statement or source-independent design fact>"
  ],
  "design_spec": {
    "information_architecture": "...",
    "layout": "...",
    "tokens": {
      "background": "#...",
      "surface": "#...",
      "text": "#...",
      "muted": "#...",
      "accent": "#...",
      "focus": "#...",
      "radius": "...",
      "space": "..."
    },
    "typography": "...",
    "components": ["..."],
    "responsive_rules": ["..."],
    "interaction_states": ["..."],
    "accessibility": "..."
  },
  "initial_code": "<!doctype html>\\n<html lang=...",
  "render_report": {
    "status": "rendered_before_correction|not_rendered",
    "viewports": [
      {
        "width": 1440,
        "height": 900,
        "horizontal_overflow": null,
        "console_errors": null
      },
      {
        "width": 390,
        "height": 844,
        "horizontal_overflow": null,
        "console_errors": null
      }
    ],
    "visual_score": null,
    "accessibility_score": null
  },
  "critic_feedback": ["...", "..."],
  "corrected_code": "<!doctype html>\\n<html lang=...",
  "quality_score": null,
  "status": "accepted_seed|needs_review",
  "source": "agent-<agent-name>-<batch-id>"
}

PROCESS
1. Choose a product task from JOB CONFIG.
2. Write the design specification before writing code.
3. Write an intentionally plausible initial implementation.
4. If browser tooling is available, render both required viewports and record
   measured overflow and console errors. If not, do not invent measurements.
5. Critique the initial implementation against the task, design spec, and
   responsive/accessibility requirements.
6. Implement a corrected version that addresses all critique items.
7. Validate that both code strings are complete HTML documents and that the
   JSON object serializes correctly.
8. Write only JSONL records to the requested output file. Do not add markdown,
   logs, comments, or a JSON array wrapper.

FINAL RESPONSE
After writing the file, report only:
- output path;
- number of records written;
- number with real browser measurements;
- number needing review;
- any validation errors.
```

## Parallelization rules

Assign every agent a unique batch ID and non-overlapping product categories.
For example:

```text
Agent A: batch-commerce-001 — ecommerce, subscriptions, marketplaces
Agent B: batch-saas-001      — SaaS, analytics, admin, developer tools
Agent C: batch-health-001    — healthcare, fitness, wellness, education
Agent D: batch-civic-001     — nonprofit, government, travel, events
```

After all agents finish, merge the files and validate them:

```bash
cat agent_outputs/*.jsonl > v2_agent_dataset.jsonl
python validate_v2_dataset.py v2_agent_dataset.jsonl
```

Never merge records without validation. Deduplicate by `example_id`, remove
records with missing code or critique, and manually review a random sample from
each agent batch.

## Reviewer prompt

Use this prompt for a separate reviewer agent:

```text
Review the attached Forma v2 JSONL records as a strict dataset-quality
reviewer. Reject records that contain generic advice, incomplete HTML,
invented browser measurements, weak critique, inaccessible controls,
non-responsive layouts, copied branded content, duplicated examples, or a
corrected_code field that does not address the listed critique. Return a JSONL
file containing only accepted records and a separate report with rejection
reasons grouped by example_id.
```
