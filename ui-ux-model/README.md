# UI/UX Design-Idea Model (fine-tune + RAG)

Given a brief like *"e-commerce store, Marvel theme"*, this pipeline outputs
structured, concrete design guidance (navbar style, color palette, typography,
button/transition behavior, background animation, layout notes) as JSON —
which downstream you can feed to an image generator to get actual mockups
(that's a later phase, not covered here).

## Architecture

```
dataset/          Seed examples + synthetic dataset generation (bootstraps
                   a large training set from a small hand-written seed set,
                   since no ready-made "UI idea in text" dataset exists)
train/            LoRA fine-tuning of Qwen3.5-0.8B via Unsloth
rag/              Local vector store of design principles, retrieved at
                   inference time to ground the model's output
inference/        Combines RAG retrieval + the fine-tuned model
```

**Why fine-tune AND use RAG (not just one):** fine-tuning teaches the model
the *output format and domain vocabulary* (it learns to talk like a UI
designer, in the right JSON shape). RAG grounds each specific answer in
concrete, retrievable design principles at generation time, so it isn't
purely relying on what got baked into the weights — you can update/expand
the knowledge base later without retraining.

## Setup

```bash
pip install -r requirements.txt
```

Steps 1-2 (dataset gen) run anywhere. Step 3 (fine-tuning) needs a rented GPU.
Step 4 (RAG build) and step 5 (inference) can run on the same GPU box, or
locally once you have the trained adapter downloaded.

### 1. Expand the seed dataset (free)
Default provider is **Groq** — free, no credit card, and its free-tier daily
request cap is generous enough to actually generate a few hundred/thousand
examples in one sitting (unlike OpenRouter's unfunded 50/day cap).
```bash
export GROQ_API_KEY=gsk_...             # console.groq.com — no card required
cd dataset
python generate_dataset.py --limit 500   # start small (--limit 20) to sanity-check output first
cat seed_examples.jsonl generated_examples.jsonl > train.jsonl
cd ..
```
Other providers:
```bash
export OPENROUTER_API_KEY=sk-or-...
python generate_dataset.py --limit 200 --provider openrouter   # good for variety, low daily cap unfunded

export ANTHROPIC_API_KEY=sk-ant-...
python generate_dataset.py --limit 200 --provider anthropic --model claude-sonnet-5   # paid
```
Free-tier model IDs rotate — if a default 404s, check
`console.groq.com/docs/models` or `openrouter.ai/models?max_price=0` and
pass `--model <id>`.

### 2. Rent a GPU and fine-tune
Any single RTX 4090 / A100 on RunPod, Vast.ai, or Lambda works. A dataset of
a few hundred to a few thousand examples trains in well under an hour —
comfortably inside a $50 budget even with a couple of retries.
```bash
python train/finetune_lora.py
```

### 3. Build the RAG knowledge base (CPU-only, free)
```bash
python rag/build_knowledge_base.py
```

### 4. Generate a design
```bash
python inference/generate_design.py "e-commerce store" "marvel-inspired superhero"
```

## Honest limitations (read before you scale this up)

- **10 seed examples is a starting point, not a finished dataset.** The
  model will only be as good as what `generate_dataset.py` produces —
  inspect the generated examples before training, don't blindly trust them.
- **The RAG knowledge base here (18 entries) is a skeleton.** It's enough to
  prove the pipeline works end-to-end; a genuinely useful system needs this
  in the hundreds, built from real UX references (see below).
- **This sandbox couldn't install/run the ML libraries** (out of disk space
  in this environment) — dataset generation logic, JSONL structure, and
  script syntax are all verified, but the fine-tuning and full RAG
  embedding steps are untested end-to-end. Run them on your GPU box, watch
  the first training run's loss curve, and sanity-check a few generations
  before trusting the output.
- **On UI/UX inspiration-site "collaborations":** Dribbble/Behance/Mobbin-style
  partnerships are realistically enterprise-scale asks, and much of that
  content isn't the platform's own IP to license anyway. For a real next
  step, look at existing open academic datasets built for exactly this —
  **Rico** (mobile UI screenshots + view hierarchies) and **WebUI** (web UI +
  DOM data) — before spending time chasing partnerships.
- **The image-generation + verification phase needs a vision-capable model**,
  not this text model — a separate, later project.
