"""
LoRA fine-tunes config.BASE_MODEL_ID on dataset/train.jsonl using Unsloth.

Run this on your RENTED GPU (RunPod / Vast.ai / Lambda), not on your laptop.
Fits comfortably in a single RTX 4090 (24GB) or A100 for a dataset in the
low thousands of examples — expect roughly 20-60 minutes depending on
dataset size and epochs, well within a <$50 single-session rental.

Before running:
    1. cd dataset && python generate_dataset.py --limit 500   (or however many)
    2. cat seed_examples.jsonl generated_examples.jsonl > train.jsonl
    3. Then, from the project root, on your GPU box:
       pip install -r requirements.txt
       python train/finetune_lora.py

Output: a LoRA adapter saved to train/lora_adapter/, loaded later by
inference/generate_design.py.
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import config  # noqa: E402

SYSTEM_PROMPT = (
    "You are a UI/UX design assistant. Given a short brief describing a "
    "website or app and a visual theme, respond with a single JSON object "
    "with exactly these keys: navbar, color_palette, typography, "
    "buttons_and_transitions, background_animation, layout_notes. "
    "Each value should be concrete and specific (hex colors, timing in ms, "
    "exact layout choices) rather than generic advice."
)


def load_training_examples() -> list[dict]:
    if not config.TRAIN_FILE.exists():
        print(
            f"ERROR: {config.TRAIN_FILE} not found. Build it first:\n"
            f"  cat dataset/seed_examples.jsonl dataset/generated_examples.jsonl "
            f"> dataset/train.jsonl",
            file=sys.stderr,
        )
        sys.exit(1)

    examples = []
    with open(config.TRAIN_FILE, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                examples.append(json.loads(line))
    return examples


def format_as_chat(example: dict) -> dict:
    """Formats one example into the chat-template shape Unsloth/TRL expect."""
    return {
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": example["prompt"]},
            {"role": "assistant", "content": json.dumps(example["response"], ensure_ascii=False)},
        ]
    }


def main():
    # Imported here (not at module top) so this file can be inspected/linted
    # on a machine without a GPU or these packages installed.
    from unsloth import FastLanguageModel
    from datasets import Dataset
    from trl import SFTTrainer, SFTConfig

    print(f"Loading base model: {config.BASE_MODEL_ID}")
    model, tokenizer = FastLanguageModel.from_pretrained(
        model_name=config.BASE_MODEL_ID,
        max_seq_length=config.MAX_SEQ_LENGTH,
        load_in_4bit=True,  # keeps VRAM usage low enough for a single consumer GPU
    )

    model = FastLanguageModel.get_peft_model(
        model,
        r=config.LORA_R,
        lora_alpha=config.LORA_ALPHA,
        lora_dropout=config.LORA_DROPOUT,
        target_modules=["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"],
        bias="none",
        use_gradient_checkpointing="unsloth",
    )

    raw_examples = load_training_examples()
    print(f"Loaded {len(raw_examples)} training examples.")
    if len(raw_examples) < 100:
        print(
            "WARNING: fewer than 100 examples. The model will likely just "
            "memorize/parrot these rather than generalize. Generate more "
            "synthetic examples first (see dataset/generate_dataset.py).",
            file=sys.stderr,
        )

    chat_examples = [format_as_chat(ex) for ex in raw_examples]

    def to_text(ex):
        return {"text": tokenizer.apply_chat_template(ex["messages"], tokenize=False)}

    dataset = Dataset.from_list(chat_examples).map(to_text)

    trainer = SFTTrainer(
        model=model,
        tokenizer=tokenizer,
        train_dataset=dataset,
        dataset_text_field="text",
        max_seq_length=config.MAX_SEQ_LENGTH,
        args=SFTConfig(
            per_device_train_batch_size=config.PER_DEVICE_BATCH_SIZE,
            gradient_accumulation_steps=config.GRAD_ACCUM_STEPS,
            num_train_epochs=config.NUM_TRAIN_EPOCHS,
            learning_rate=config.LEARNING_RATE,
            fp16=not FastLanguageModel.is_bfloat16_supported(),
            bf16=FastLanguageModel.is_bfloat16_supported(),
            logging_steps=10,
            output_dir=str(config.ROOT_DIR / "train" / "checkpoints"),
            save_strategy="epoch",
            report_to="none",
        ),
    )

    print("Starting training...")
    trainer.train()

    config.ADAPTER_OUT_DIR.mkdir(parents=True, exist_ok=True)
    model.save_pretrained(str(config.ADAPTER_OUT_DIR))
    tokenizer.save_pretrained(str(config.ADAPTER_OUT_DIR))
    print(f"Done. LoRA adapter saved to {config.ADAPTER_OUT_DIR}")


if __name__ == "__main__":
    main()
