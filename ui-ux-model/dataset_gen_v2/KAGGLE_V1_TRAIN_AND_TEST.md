# Forma V1: Kaggle fine-tune and Gradio test

## 1. Prepare Kaggle

Create a Kaggle notebook with GPU enabled (2×T4 if available), Internet enabled, and add the dataset/model inputs you need. Upload or attach:

```text
v2_training_candidate.jsonl
kaggle_uiux_finetune.ipynb
```

Do not paste provider keys into notebook cells. Use Kaggle Secrets for `HF_TOKEN` and any training-only service keys.

## 2. Fine-tune

Open `kaggle_uiux_finetune.ipynb` and run its cells from top to bottom. The notebook installs the compatible Unsloth/Transformers/TRL stack, removes the CUDA-mismatched optional audio package, loads `Qwen/Qwen3-VL-4B-Instruct`, formats the JSONL records, applies LoRA, trains, validates, and saves the adapter.

Point the notebook's training data path to:

```text
/kaggle/input/<your-dataset-name>/v2_training_candidate.jsonl
```

The output adapter directory should contain `adapter_config.json`, `adapter_model.safetensors`, tokenizer/processor files, and a README. Upload that adapter to Hugging Face, for example `YOUR_USER/forma-v1-lora`.

## 3. Install inference dependencies

```bash
pip install -U torch transformers peft accelerate bitsandbytes torchvision \
  gradio requests beautifulsoup4 pillow
```

If Transformers imports fail because of Kaggle's preinstalled audio wheel:

```bash
pip uninstall -y torchaudio
```

## 4. Launch the agent

Set only the model identifiers globally:

```python
import os
os.environ["FORMA_ADAPTER"] = "YOUR_USER/forma-v1-lora"
os.environ["HF_TOKEN"] = "YOUR_HF_TOKEN"  # use Kaggle Secrets in real use
```

Run:

```python
%run /kaggle/input/<your-code-dataset>/gradio_forma_agent.py
```

The notebook prints a public Gradio URL through `share=True`.

## 5. Test modes

1. Text-only: ask for a cyberpunk ecommerce UI and leave all optional tools off.
2. Screenshot: upload an image and ask for evidence-based findings.
3. Website research: enter a URL, enable Tavily, and provide a Tavily key in the password field.
4. Code generation: enable coding and enter an OpenRouter key. Forma calls `z-ai/glm-5.2:free` first.
5. Fallback: enter a Groq key too. If OpenRouter fails, Forma calls `llama-3.3-70b-versatile` through Groq's OpenAI-compatible endpoint.

Keys entered in the UI are session-only and are not written to files. Never print them, store them in `gr.State`, or commit them.

## 6. Provider choice

The implementation uses `z-ai/glm-5.2:free` as the OpenRouter primary because the user requested a coding-capable free OpenRouter route. The Groq fallback uses `llama-3.3-70b-versatile`, whose API is OpenAI-compatible and generally useful for fast frontend code. The user can change the constants at the top of `gradio_forma_agent.py` if their provider account exposes a different model ID.

## 7. Important limitations

- Tavily supplies search and page text; it does not guarantee that a blocked or dynamic site can be visually inspected.
- The local Forma model performs the vision analysis. The external coding model receives the analysis and research context, not hidden chain-of-thought.
- Free-provider rate limits and model availability can change.
- Validate generated code in a sandbox before deployment.
