# Infra / Forma V1

Infra is building **Forma**, a vision-language UI/UX engineering assistant that reviews interfaces, explains concrete usability and accessibility problems, searches for supporting design patterns, and proposes improved HTML/CSS implementations.

This repository contains the V1 hackathon submission: the landing page, the model/data pipeline, RAG utilities, inference tools, training notebook, validation scripts, and the reviewed V2 dataset candidate.

## What exists today

### Forma V1 model

V1 is a Qwen3-VL-4B-Instruct base model with the QiFu LoRA adapter. It accepts a UI screenshot or text brief and returns UI/UX recommendations and implementation-oriented feedback. The adapter is hosted separately; do not commit model weights or tokens to this repository.

### Repository map

| Path | Purpose |
|---|---|
| `ui-ux-model/train/` | LoRA fine-tuning entry point |
| `ui-ux-model/inference/` | Model inference utilities |
| `ui-ux-model/rag/` | Knowledge-base construction and retrieval |
| `ui-ux-model/dataset/` | Seed and generated training data |
| `ui-ux-model/dataset_gen/` | Earlier dataset-generation pipeline |
| `ui-ux-model/dataset_gen_v2/` | V2 generation, rendering, validation, merging, and audit tools |
| `ui-ux-model/kaggle_uiux_finetune.ipynb` | Reproducible Kaggle training notebook |
| `Landing_Page/` | Next.js marketing site and waitlist application |

## End-to-end flow

```text
Brief / screenshot / URL
          |
          v
  optional web research + RAG retrieval
          |
          v
   Forma V1 vision-language model
          |
          v
 UX findings -> concrete recommendations -> optional HTML/CSS
          |
          v
 human review, feedback, evaluation, dataset improvement
```

## Quick start: model pipeline

```bash
cd ui-ux-model
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Set secrets through the environment or a local, untracked `.env` file:

```bash
export HF_TOKEN="your_huggingface_token"
```

Validate a dataset:

```bash
python validate_v2_dataset.py dataset_gen_v2/v2_training_candidate.jsonl
```

The main V2 automated training candidate is:

```text
ui-ux-model/dataset_gen_v2/v2_training_candidate.jsonl
```

It contains 348 records that passed automated structural, responsive, and runtime checks. It is a preliminary SFT candidate, not a claim of production-ready visual quality. The rejected records and audit manifests are retained beside it.

## Dataset workflow

1. Generate unique design briefs and paired initial/corrected HTML examples.
2. Merge only non-snapshot sources and remove exact content duplicates.
3. Normalize the design-token schema.
4. Render initial and corrected pages at 1440×900 and 390×844.
5. Run objective checks for overflow, browser errors, landmarks, labels, focus behavior, and target sizing.
6. Review screenshots with a human or vision auditor and assign visual/accessibility scores.
7. Keep a held-out evaluation split and train only accepted records.

The V2 scripts and reports are documented in `ui-ux-model/dataset_gen_v2/V2_DATASET_AUDIT.md`. The dataset-generation prompts are in `UNIQUE_100_PER_AGENT_PROMPT.md` and the parallel-agent prompt files.

## Landing page

```bash
cd Landing_Page
pnpm install
pnpm dev
```

Copy `.env.example` to `.env.local` and fill only the services you have configured. The site includes the Infra/ Forma positioning, waitlist flow, authentication/database integration, and contact configuration. Never commit `.env.local`, SMTP credentials, database URLs, API keys, or HF tokens.

For a deployment build:

```bash
pnpm build
pnpm start
```

## Hackathon submission scope

V1 demonstrates the complete product loop: a fine-tuned vision-language model, UI/UX-focused data generation, RAG foundations, browser-based checks, a Kaggle training path, and a product landing page. The next milestone is V2: more diverse and human-reviewed screenshot/code pairs, grounded structured critiques, stronger web research/tool use, feedback history, and reliable code generation.

## Responsible use and limitations

- Model output is advisory and must be reviewed by a designer or engineer.
- A rendered page passing automated checks is not proof of good visual hierarchy or usability.
- Web pages may block crawlers or change after retrieval; research results must be cited and checked.
- Do not upload private screenshots, credentials, personal data, or proprietary source code without authorization.
- Do not expose API keys in notebooks, frontend code, commits, logs, or model prompts.

## License

The project code is released under the repository license. Base-model and dataset licenses remain those of their respective upstream sources; review each upstream license before redistribution or commercial use.

## Team / organization

Infra — **See better. Design smarter.**
