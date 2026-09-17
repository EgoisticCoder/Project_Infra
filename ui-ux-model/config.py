"""
Central configuration for the UI/UX design-idea pipeline.

Everything downstream (dataset generation, fine-tuning, RAG, inference)
reads from here so you only change settings in one place.
"""

import os
from pathlib import Path

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
ROOT_DIR = Path(__file__).resolve().parent
DATASET_DIR = ROOT_DIR / "dataset"
SEED_FILE = DATASET_DIR / "seed_examples.jsonl"
GENERATED_FILE = DATASET_DIR / "generated_examples.jsonl"
TRAIN_FILE = DATASET_DIR / "train.jsonl"          # final file used for fine-tuning

RAG_DIR = ROOT_DIR / "rag"
KNOWLEDGE_BASE_FILE = RAG_DIR / "knowledge_base" / "design_principles.jsonl"
CHROMA_PERSIST_DIR = RAG_DIR / "chroma_store"      # local vector DB, created on first build

ADAPTER_OUT_DIR = ROOT_DIR / "train" / "lora_adapter"

# ---------------------------------------------------------------------------
# Base model (Phase B: fine-tuning)
# ---------------------------------------------------------------------------
# Qwen3.5-0.8B: Apache-licensed, strong instruction-following at small scale,
# supported by Unsloth for fast/cheap LoRA fine-tuning on a single rented GPU.
# Swap this string if you'd rather use e.g. "google/gemma-3-1b-it".
BASE_MODEL_ID = "Qwen/Qwen3.5-0.8B-Instruct"

MAX_SEQ_LENGTH = 1024
LORA_R = 16
LORA_ALPHA = 32
LORA_DROPOUT = 0.05
LEARNING_RATE = 2e-4
NUM_TRAIN_EPOCHS = 3
PER_DEVICE_BATCH_SIZE = 4
GRAD_ACCUM_STEPS = 4

# ---------------------------------------------------------------------------
# RAG (Phase C: retrieval-augmented generation)
# ---------------------------------------------------------------------------
# CPU-friendly, ~80MB, good enough for short design-principle snippets.
EMBEDDING_MODEL_ID = "sentence-transformers/all-MiniLM-L6-v2"
RAG_TOP_K = 4  # how many knowledge-base chunks to retrieve per query

# ---------------------------------------------------------------------------
# Dataset generation (bring-your-own LLM key)
# ---------------------------------------------------------------------------
# Set the relevant env var before running dataset/generate_dataset.py.
#
# Primary: OpenRouter, nvidia/nemotron-3-ultra-550b-a55b:free — a genuinely
# strong open frontier-reasoning MoE (550B total / 55B active), free tier.
# Trade-off vs. Groq, worth knowing before you rely on it: OpenRouter's free
# daily cap is only ~50 requests/day unfunded (1,000/day if the account has
# ever added $10 of credit) — much lower ceiling than Groq. Higher quality
# per example, but slower to reach large example counts unless you fund it.
#
# Secondary: Groq, qwen/qwen3.6-27b — flagship-tier reasoning/coding Qwen
# model, fast, and Groq's free-tier daily cap is generally more generous.
# Good as a volume source or a fallback when OpenRouter's cap is hit.
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY", "")
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")

# Per-provider defaults: base_url (None for native SDK), default model, and
# a safe seconds-between-requests to stay under the free-tier rate limit.
# Model catalogs and free-tier limits change — verify at
# console.groq.com/docs/models (+ /docs/rate-limits) or
# openrouter.ai/models?max_price=0 if a default 404s or rate-limits harder
# than expected.
PROVIDER_DEFAULTS = {
    "openrouter": {
        "base_url": "https://openrouter.ai/api/v1",
        "api_key": OPENROUTER_API_KEY,
        "model": "nvidia/nemotron-3-ultra-550b-a55b:free",
        "min_seconds_between_calls": 3.1,   # free tier: 20 requests/minute
    },
    "groq": {
        "base_url": "https://api.groq.com/openai/v1",
        "api_key": GROQ_API_KEY,
        "model": "qwen/qwen3.6-27b",
        "min_seconds_between_calls": 2.5,   # conservative default — check console.groq.com/docs/rate-limits for this specific model
    },
    "anthropic": {
        "base_url": None,  # uses the native anthropic SDK, not OpenAI-compatible
        "api_key": ANTHROPIC_API_KEY,
        "model": "claude-sonnet-5",
        "min_seconds_between_calls": 0.3,
    },
}
TARGET_GENERATED_EXAMPLES = 3000  # aim for ~3k synthetic examples on top of the seed set
