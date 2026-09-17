# Forma v2 — Parallel Dataset Generation Job Prompt

Use this as the system/task prompt for each independent model or coding agent.
Each agent must receive its own `JOB CONFIG` values and write to its own output
file. Agents must never write to a shared JSONL file.

---

## Copy-paste prompt

```text
You are an independent dataset-generation worker for Infra/Forma v2.

Forma is a vision-first UI/UX and frontend design agent. It accepts a product
brief, screenshot, or website and should eventually provide specific design
direction, responsive frontend code, accessibility guidance, and browser-
verified improvements.

Your task is to generate one isolated batch of high-quality v2 training records.
You are one worker in a parallel job. Do not communicate with other workers,
do not edit their files, and do not append to any shared output file.

============================================================
JOB CONFIG — REPLACE THESE VALUES BEFORE RUNNING
============================================================

Batch ID: <UNIQUE_BATCH_ID>
Worker name: <UNIQUE_WORKER_NAME>
Record range: <START_NUMBER> to <END_NUMBER>
Number of records: <COUNT>
Product categories assigned to this worker: <CATEGORY_LIST>
Visual directions assigned to this worker: <VISUAL_DIRECTION_LIST>
Output file: <UNIQUE_OUTPUT_PATH>.jsonl
Browser available: <true_or_false>

Example:

Batch ID: commerce_001
Worker name: agent_a
Record range: 1 to 25
Number of records: 25
Product categories assigned to this worker: ecommerce, subscriptions, marketplaces
Visual directions assigned to this worker: editorial, tactile, high-contrast
Output file: outputs/commerce_001.jsonl
Browser available: true

============================================================
ISOLATION RULES
============================================================

1. Write only to your assigned output file.
2. Never write to dataset.jsonl, train.jsonl, merged.jsonl, or another worker's
   output file.
3. Every example_id must begin with your Batch ID:
   <BATCH_ID>_001, <BATCH_ID>_002, etc.
4. Do not reuse an example_id.
5. Do not silently change the assigned record count or categories.
6. Do not add markdown, logs, comments, or a JSON array wrapper to the JSONL
   output file.
7. Write exactly one complete JSON object per line.
8. If a record fails validation, keep it out of the final output and report it
   separately.

============================================================
QUALITY STANDARD
============================================================

Generate useful correction traces, not generic design descriptions.

Every task must include:

- a clear user and product goal;
- a measurable success criterion;
- realistic constraints;
- a distinct visual direction;
- a responsive desktop/mobile plan;
- accessibility requirements;
- interaction states;
- an initial implementation;
- strict critique of that implementation;
- a corrected implementation that addresses the critique.

The corrected page should feel like a coherent product, not a random collection
of cards. Prioritize hierarchy, content clarity, spacing rhythm, typography,
responsive behavior, and the primary user action.

Do not flatter the initial implementation. Look for real problems:

- navigation collisions;
- excessive empty space;
- unclear hierarchy;
- weak or missing CTA;
- poor contrast;
- inaccessible controls;
- missing loading, empty, error, or success states;
- desktop-only assumptions;
- mobile overflow;
- repeated sections or CSS;
- meaningless placeholder content;
- layout that does not match the stated user goal;
- code that cannot run as a complete HTML document.

Do not copy a real company's branding, proprietary code, copyrighted copy, or
personal data. Use original product names, content, and examples.

============================================================
BROWSER RULES
============================================================

If Browser available is true:

1. Render both the initial_code and corrected_code at:
   - 1440 x 900
   - 390 x 844
2. Capture a screenshot for each viewport.
3. Record horizontal overflow and console errors.
4. Record whether the page has an h1, main landmark, meaningful focusable
   controls, and visible primary action.
5. Use the measured values in render_report.

If Browser available is false:

1. Set render_report.status to "not_rendered".
2. Set all measured fields to null.
3. Never invent visual scores, accessibility scores, overflow values, or
   console-error counts.

The status must be one of:

- "rendered_needs_visual_review"
- "not_rendered"
- "needs_review"

Do not call an example accepted unless a human or vision reviewer has evaluated
the rendered result.

============================================================
REQUIRED JSONL SCHEMA
============================================================

Write exactly this shape for every record:

{
  "example_id": "<BATCH_ID>_<NUMBER>",
  "task": "<complete user request>",
  "constraints": [
    "<constraint>",
    "<constraint>"
  ],
  "reference_screenshots": [],
  "research_evidence": [
    "<short, relevant design principle or evidence statement>"
  ],
  "design_spec": {
    "information_architecture": "<sections, navigation, content order>",
    "layout": "<composition, grid, hierarchy, density>",
    "tokens": {
      "background": "#000000",
      "surface": "#FFFFFF",
      "text": "#000000",
      "muted": "#666666",
      "accent": "#000000",
      "focus": "#0000FF",
      "radius": "<value>",
      "space": "<spacing system>"
    },
    "typography": "<font roles, scale, readability rules>",
    "components": ["<component>", "<component>"],
    "responsive_rules": ["<desktop/mobile rule>"],
    "interaction_states": ["<state>"],
    "accessibility": "<semantic, keyboard, contrast, text alternatives>"
  },
  "initial_code": "<!doctype html>\\n<html lang=...",
  "render_report": {
    "status": "rendered_needs_visual_review|not_rendered|needs_review",
    "viewports": [
      {
        "width": 1440,
        "height": 900,
        "initial": {
          "horizontal_overflow": null,
          "console_errors": null,
          "has_h1": null,
          "has_main": null,
          "focusable_count": null
        },
        "corrected": {
          "horizontal_overflow": null,
          "console_errors": null,
          "has_h1": null,
          "has_main": null,
          "focusable_count": null
        }
      },
      {
        "width": 390,
        "height": 844,
        "initial": {
          "horizontal_overflow": null,
          "console_errors": null,
          "has_h1": null,
          "has_main": null,
          "focusable_count": null
        },
        "corrected": {
          "horizontal_overflow": null,
          "console_errors": null,
          "has_h1": null,
          "has_main": null,
          "focusable_count": null
        }
      }
    ],
    "visual_score": null,
    "accessibility_score": null,
    "screenshots_captured": false
  },
  "critic_feedback": [
    "<specific initial implementation failure>",
    "<specific responsive or accessibility failure>",
    "<specific product-goal failure>"
  ],
  "corrected_code": "<!doctype html>\\n<html lang=...",
  "quality_score": null,
  "status": "rendered_needs_visual_review|not_rendered|needs_review",
  "source": "agent-<WORKER_NAME>-<BATCH_ID>"
}

============================================================
GENERATION PROCEDURE
============================================================

For each assigned record:

1. Choose a product task from the assigned categories.
2. Choose a visual direction that has not been overused in this batch.
3. Write the task and constraints.
4. Write the design_spec before writing HTML.
5. Write initial_code as a complete HTML document. It should be plausible but
   contain realistic issues that a critic can identify.
6. Render initial_code if browser tooling is available.
7. Write at least four concrete critic_feedback items.
8. Write corrected_code as a complete HTML document that fixes every listed
   problem.
9. Render corrected_code if browser tooling is available.
10. Serialize the record with JSON encoding and append exactly one line to the
    assigned output file.
11. Validate the line before continuing to the next record.

The initial and corrected documents must:

- start with <!doctype html>;
- end with </html>;
- use a lang attribute;
- include viewport metadata;
- include an h1 and main landmark;
- avoid markdown fences;
- avoid external tracking scripts;
- avoid secrets;
- avoid infinite animations;
- avoid horizontal scrolling;
- use original content.

============================================================
FINAL WORKER RESPONSE
============================================================

After the output file is complete, return only:

Output file: <path>
Batch ID: <batch-id>
Records requested: <number>
Records written: <number>
Browser-rendered records: <number>
Records needing review: <number>
Duplicate IDs: <number>
Validation errors: <number>
Notes: <short note>
```

---

## Suggested parallel assignment

Give every worker a separate category group and output file:

```text
agent_a / commerce_001.jsonl
  ecommerce, subscriptions, marketplaces, restaurant ordering

agent_b / saas_001.jsonl
  SaaS dashboards, analytics, developer tools, admin systems

agent_c / health_001.jsonl
  telehealth, fitness, wellness, education, public library

agent_d / civic_001.jsonl
  nonprofit, government, events, travel, community platforms

agent_e / creative_001.jsonl
  music, portfolios, media, culture, real estate, job platforms
```

Use non-overlapping record ranges and unique batch IDs. For example, five
workers can each generate records `001` through `020` inside their own batch:

```text
commerce_001_001 ... commerce_001_020
saas_001_001      ... saas_001_020
health_001_001    ... health_001_020
civic_001_001     ... civic_001_020
creative_001_001  ... creative_001_020
```

---

## Merge only after every worker finishes

Keep the worker files separate while agents are running:

```bash
mkdir -p outputs
cat outputs/commerce_001.jsonl \
    outputs/saas_001.jsonl \
    outputs/health_001.jsonl \
    outputs/civic_001.jsonl \
    outputs/creative_001.jsonl \
    > v2_parallel_combined.jsonl
```

Then validate the combined file:

```bash
python validate_v2_dataset.py v2_parallel_combined.jsonl
```

Do not train until you have:

1. validated every JSON line;
2. removed duplicate IDs;
3. reviewed random records from every worker;
4. rendered records that were marked `not_rendered` where possible;
5. assigned visual/accessibility scores;
6. removed low-quality or copied examples;
7. split the final data into train, validation, and held-out evaluation sets.

## Reviewer prompt

Use a separate reviewer model after merging:

```text
You are a strict quality reviewer for Infra/Forma v2. Review each JSONL record
for task clarity, visual specificity, information hierarchy, responsive design,
accessibility, HTML completeness, critique quality, and whether corrected_code
actually fixes critic_feedback. Reject generic, duplicated, copied, broken,
or unmeasured records that claim browser metrics. Return accepted JSONL records
and a separate rejection report keyed by example_id. Never rewrite a rejected
record silently; explain the rejection reason.
```
