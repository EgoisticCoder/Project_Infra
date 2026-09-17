# Forma v2 — Prompt for 100 Unique Designs Per Agent

This is the correct prompt when every parallel agent must generate its own
unique set of 100 designs and all sets will be merged later.

The important distinction is:

```text
Agent A → 100 unique designs
Agent B → 100 different unique designs
Agent C → 100 different unique designs
                     ↓
             semantic deduplication
                     ↓
             one merged dataset
```

Do not ask agents to append to the same file while they are running.

---

## Copy this prompt into every agent

```text
You are a Forma v2 dataset-generation agent.

You must create EXACTLY 100 genuinely different UI/UX design records. This is
not a request for 100 color variations of the same layout. Every record must be
a distinct product experience with a distinct design direction, information
architecture, composition, component strategy, interaction model, content
hierarchy, and responsive behavior.

You are running in parallel with other agents. Your output will later be merged
with their outputs. You do not know their exact records, so you must use your
assigned uniqueness namespace and strict anti-repetition rules.

============================================================
AGENT CONFIGURATION
============================================================

Agent namespace: <UNIQUE_AGENT_NAMESPACE>
Agent number: <AGENT_NUMBER>
Output file: <PRIVATE_OUTPUT_FILE_FOR_THIS_AGENT>.jsonl
Required records: exactly 100
Assigned product families: <PRODUCT_FAMILIES>
Forbidden product families: <OTHER_AGENTS_FAMILIES>
Assigned visual vocabulary: <VISUAL_VOCABULARY>
Forbidden visual vocabulary: <OTHER_AGENTS_VOCABULARY>
Assigned design-slot range: <START_SLOT> to <END_SLOT>

Every example_id must be:

<AGENT_NAMESPACE>_design_001
<AGENT_NAMESPACE>_design_002
...
<AGENT_NAMESPACE>_design_100

Never reuse an ID. Never write outside your private output file.

============================================================
NON-NEGOTIABLE UNIQUENESS REQUIREMENT
============================================================

All 100 records must differ in all of the following dimensions:

1. Product problem and user goal.
2. Target audience and context of use.
3. Primary user journey.
4. Information architecture.
5. Hero or above-the-fold composition.
6. Main layout pattern.
7. Content density.
8. Primary component arrangement.
9. Navigation model.
10. Interaction model.
11. Responsive transformation strategy.
12. Color palette and contrast strategy.
13. Typography pairing and hierarchy.
14. Shape, radius, border, and surface language.
15. Motion or feedback behavior.
16. Empty, loading, error, and success states.
17. Accessibility considerations.
18. Actual content and labels.

Changing only the colors, product name, or heading does NOT create a new
design. If two records could be described as “the same page with a different
theme”, one of them must be redesigned.

Before writing each record, maintain an internal uniqueness ledger containing:

- product goal;
- audience;
- page type;
- layout pattern;
- navigation pattern;
- palette family;
- typography family;
- dominant component pattern;
- interaction pattern;
- responsive strategy.

Do not reuse a complete combination from that ledger. No layout pattern may be
used more than twice in the 100-record batch, and no exact palette, typography
pairing, or component arrangement may be reused.

============================================================
DESIGN VARIETY REQUIREMENT
============================================================

Across the 100 records, deliberately cover a broad matrix such as:

- ecommerce, healthcare, education, finance, travel, civic, media, music,
  sports, logistics, productivity, developer tools, climate, real estate,
  events, community, nonprofit, hospitality, portfolio, and public services;
- landing pages, dashboards, search results, detail pages, booking flows,
  comparison pages, onboarding, checkout, maps, timelines, calendars, tables,
  feeds, editors, command centers, forms, and profile/workspace views;
- editorial, brutalist, quiet luxury, Swiss, neo-brutalist, tactile, playful,
  utilitarian, dark cinematic, paper-like, monochrome, botanical, retro,
  kinetic, modular, data-dense, and accessibility-first systems;
- tab navigation, sidebar navigation, command palette, bottom navigation,
  stepper navigation, map navigation, timeline navigation, filter-first layouts,
  search-first layouts, and progressive disclosure;
- card grids, split panes, editorial columns, bento layouts, tables, kanban,
  timelines, maps, calendars, radial summaries, long-form pages, and guided
  flows.

Do not use a generic centered hero plus three cards for most records.

============================================================
REQUIRED RECORD FORMAT
============================================================

Write exactly one valid JSON object per line using this schema:

{
  "example_id": "<AGENT_NAMESPACE>_design_001",
  "task": "<specific user request with product goal>",
  "constraints": [
    "<responsive constraint>",
    "<accessibility constraint>",
    "<product/business constraint>",
    "<technical/content constraint>"
  ],
  "reference_screenshots": [],
  "research_evidence": [
    "<relevant evidence or design principle>",
    "<relevant evidence or design principle>"
  ],
  "design_spec": {
    "information_architecture": "<unique content and navigation structure>",
    "layout": "<unique composition and hierarchy>",
    "tokens": {
      "background": "#000000",
      "surface": "#FFFFFF",
      "text": "#000000",
      "muted": "#666666",
      "accent": "#000000",
      "focus": "#0000FF",
      "radius": "<unique radius language>",
      "space": "<unique spacing rhythm>"
    },
    "typography": "<specific pairing, hierarchy, and readability rules>",
    "components": ["<unique component>", "<unique component>"],
    "responsive_rules": ["<desktop-to-mobile transformation>"],
    "interaction_states": ["<specific interaction state>"],
    "accessibility": "<semantic, keyboard, contrast, and alternative-content rules>"
  },
  "initial_code": "<!doctype html>\\n<html lang=...",
  "render_report": {
    "status": "rendered_needs_visual_review|not_rendered",
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
    "<specific failure in hierarchy or product clarity>",
    "<specific responsive failure>",
    "<specific accessibility or interaction failure>",
    "<specific code/content failure>"
  ],
  "corrected_code": "<!doctype html>\\n<html lang=...",
  "quality_score": null,
  "status": "rendered_needs_visual_review|not_rendered|needs_review",
  "source": "agent-<AGENT_NAMESPACE>"
}

============================================================
INITIAL CODE REQUIREMENTS
============================================================

Both initial_code and corrected_code must:

- be complete standalone HTML documents;
- start with <!doctype html> and end with </html>;
- include <html lang="...">;
- include viewport metadata;
- include one meaningful h1;
- include a main landmark;
- use original text and product names;
- avoid copied brand identities and copyrighted marketing copy;
- use real links and buttons rather than clickable divs;
- include visible keyboard focus styles;
- include responsive CSS;
- avoid external tracking scripts and secrets;
- avoid infinite or distracting animations;
- avoid unbounded repeated markup;
- avoid horizontal overflow at 390px.

The initial version must be plausible but imperfect. The corrected version must
fix the exact issues identified in critic_feedback. Do not simply change the
colors or rewrite the copy.

============================================================
BROWSER AND MEASUREMENT RULES
============================================================

If browser tooling is available:

1. Render initial_code and corrected_code at 1440x900 and 390x844.
2. Capture screenshots.
3. Measure horizontal overflow.
4. Count console errors and page errors.
5. Verify h1, main, focusable controls, and primary action.
6. Put real measurements in render_report.

If browser tooling is unavailable:

1. Use render_report.status = "not_rendered".
2. Set every measurement and score to null.
3. Do not claim that screenshots were captured.

Never invent visual or accessibility scores.

============================================================
QUALITY REVIEW BEFORE WRITING EACH LINE
============================================================

Ask yourself:

- Is this a genuinely new product goal?
- Is the page structure unlike the previous records?
- Is the navigation model different enough?
- Is the typography and palette combination unused?
- Is the interaction pattern different?
- Does mobile transform rather than merely shrink?
- Does the critique identify real failures?
- Does corrected_code fix every listed failure?
- Could a reviewer distinguish this design without reading the product name?

If any answer is no, redesign the record before writing it.

============================================================
OUTPUT RULES
============================================================

Write exactly 100 records. Do not stop at 99. Do not write more than 100.
Write only to the private output file configured above.

At completion, report:

Output file: <path>
Agent namespace: <namespace>
Records requested: 100
Records written: <number>
Unique IDs: <number>
Browser-rendered records: <number>
Records needing review: <number>
Within-batch semantic duplicates detected: <number>
Validation errors: <number>
```

---

## How to configure multiple agents

Use different namespaces and non-overlapping scopes:

```text
Agent A:
  namespace: agent_a_commerce
  categories: ecommerce, subscriptions, marketplaces
  styles: editorial, tactile, quiet luxury
  output: outputs/agent_a_commerce.jsonl

Agent B:
  namespace: agent_b_tools
  categories: SaaS, dashboards, developer tools
  styles: Swiss, utilitarian, data-dense
  output: outputs/agent_b_tools.jsonl

Agent C:
  namespace: agent_c_public
  categories: civic, nonprofit, education, library
  styles: civic, paper-like, accessible-first
  output: outputs/agent_c_public.jsonl
```

Each agent still generates exactly 100 records. With three agents, the expected
total is 300 records.

---

## Merge and deduplicate after all agents finish

Do not merge while agents are still writing:

```bash
cat outputs/agent_a_commerce.jsonl \
    outputs/agent_b_tools.jsonl \
    outputs/agent_c_public.jsonl \
    > v2_all_agents.jsonl
```

Then run structural validation:

```bash
python validate_v2_dataset.py v2_all_agents.jsonl
```

Structural validation cannot guarantee semantic uniqueness. Run a separate
reviewer agent over the merged file with this prompt:

```text
You are the final semantic-deduplication reviewer for Forma v2.

Compare every record against every other record. Mark a pair as duplicate when
the products, user goal, information architecture, page composition, layout,
component arrangement, interaction model, palette, typography, and responsive
behavior are substantially the same even if names or colors differ.

Return:
1. duplicate groups with example_ids;
2. the best record to keep in each group;
3. rejection reasons for every removed record;
4. an accepted JSONL file containing only records that are meaningfully
   distinct and structurally valid.

Do not silently rewrite records. Do not accept two designs that are merely the
same card-grid landing page with different copy.
```

The final training corpus should be created only after semantic deduplication,
human spot checks, browser validation, and train/validation/test splitting.
