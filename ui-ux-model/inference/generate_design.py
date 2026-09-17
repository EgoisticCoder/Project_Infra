"""
End-to-end inference: retrieves relevant design principles (RAG) and feeds
them, alongside the fine-tuned model's own training, into a generation call.

Usage:
    python inference/generate_design.py "e-commerce store" "marvel-inspired superhero"
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import config  # noqa: E402
from rag.retrieve import retrieve  # noqa: E402
from train.finetune_lora import SYSTEM_PROMPT  # reuse the exact prompt used in training


def build_prompt(site_type: str, theme: str) -> tuple[str, list[str]]:
    user_query = f"Design a UI for a {site_type} in a {theme} theme."
    retrieved = retrieve(user_query)

    grounding = "\n".join(f"- {r}" for r in retrieved)
    augmented_user_message = (
        f"{user_query}\n\n"
        f"Relevant design principles to keep in mind:\n{grounding}"
    )
    return augmented_user_message, retrieved


def generate(site_type: str, theme: str) -> dict:
    from unsloth import FastLanguageModel

    model, tokenizer = FastLanguageModel.from_pretrained(
        model_name=str(config.ADAPTER_OUT_DIR),  # loads base model + saved LoRA adapter together
        max_seq_length=config.MAX_SEQ_LENGTH,
        load_in_4bit=True,
    )
    FastLanguageModel.for_inference(model)

    augmented_user_message, retrieved_snippets = build_prompt(site_type, theme)
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": augmented_user_message},
    ]
    inputs = tokenizer.apply_chat_template(
        messages, tokenize=True, add_generation_prompt=True, return_tensors="pt"
    ).to(model.device)

    output_ids = model.generate(inputs, max_new_tokens=400, temperature=0.7, do_sample=True)
    raw_text = tokenizer.decode(output_ids[0][inputs.shape[1]:], skip_special_tokens=True)

    try:
        parsed = json.loads(raw_text)
    except json.JSONDecodeError:
        parsed = {"_raw_output": raw_text, "_warning": "model output was not valid JSON"}

    return {"design": parsed, "grounded_on": retrieved_snippets}


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print('Usage: python generate_design.py "<site_type>" "<theme>"', file=sys.stderr)
        sys.exit(1)

    site_type, theme = sys.argv[1], sys.argv[2]
    result = generate(site_type, theme)
    print(json.dumps(result, indent=2, ensure_ascii=False))
