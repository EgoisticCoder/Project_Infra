"""Standalone Kaggle QiFu agent.

Remote RAG is restricted to WebSight, Screen2Words, and WebUI.
Rico, Mind2Web, and VINS are intentionally not loaded by this file.

Kaggle setup (before executing this file):
  pip install -q -U gradio transformers peft accelerate torchvision \
      beautifulsoup4 requests ddgs scikit-learn playwright
  # This agent has no audio input; remove Kaggle's often CUDA-mismatched wheel.
  pip uninstall -y torchaudio
  playwright install chromium
"""

import json
import os
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from io import BytesIO
from pathlib import Path
from typing import Any

import gradio as gr
import requests
import torch
from bs4 import BeautifulSoup
from PIL import Image
from peft import PeftModel
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from transformers import AutoProcessor, Qwen3VLForConditionalGeneration, TextIteratorStreamer


BASE_MODEL_ID = "Qwen/Qwen3-VL-4B-Instruct"
ADAPTER_ID = os.getenv("MODEL_ID", "EgoisticCoder/QiFu-v1")
HF_TOKEN = os.getenv("HF_TOKEN") or None


def flatten(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, dict):
        return " ".join(f"{k}: {flatten(v)}" for k, v in value.items())
    if isinstance(value, list):
        return " ".join(flatten(item) for item in value)
    return str(value)


class RagIndex:
    def __init__(self):
        self.records = []
        self.vectorizer = None
        self.matrix = None

    def add(self, source: str, text: str):
        text = text.strip()
        if text:
            self.records.append({"source": source, "text": text[:7000]})

    def fit(self):
        if not self.records:
            return
        self.vectorizer = TfidfVectorizer(
            lowercase=True,
            stop_words="english",
            ngram_range=(1, 2),
            max_features=40000,
        )
        self.matrix = self.vectorizer.fit_transform(
            [record["text"] for record in self.records]
        )

    def search(self, query: str, k: int = 5) -> str:
        if self.vectorizer is None or self.matrix is None:
            return "No local or remote RAG records were indexed."
        vector = self.vectorizer.transform([query])
        scores = cosine_similarity(vector, self.matrix)[0]
        chunks = []
        for index in scores.argsort()[::-1][:k]:
            if scores[index] <= 0:
                continue
            record = self.records[index]
            chunks.append(f"[source: {record['source']}]\n{record['text']}")
        return "\n\n".join(chunks) or "No relevant RAG records found."


RAG = RagIndex()


def load_local_rag():
    for raw_path in os.getenv("QIFU_RAG_FILES", "").split(","):
        path = Path(raw_path.strip())
        if not path.exists():
            continue
        with path.open("r", encoding="utf-8", errors="replace") as handle:
            for line in handle:
                try:
                    row = json.loads(line)
                    RAG.add(path.stem, flatten(row))
                except json.JSONDecodeError:
                    pass


def load_remote_rag():
    if os.getenv("QIFU_ENABLE_REMOTE_RAG", "1") != "1":
        return
    try:
        from datasets import load_dataset
    except ImportError:
        print("datasets is not installed; skipping remote RAG.")
        return

    limit = int(os.getenv("QIFU_REMOTE_RAG_ROWS", "50"))
    sources = [
        ("WebSight", "HuggingFaceM4/WebSight", ["llm_generated_idea", "text"]),
        ("Screen2Words", "rootsautomation/RICO-Screen2Words", ["captions"]),
        ("WebUI", "xlelords/webui", [
            "title", "category", "meta_description", "color_palette",
            "fonts", "elements", "num_elements", "word_count",
        ]),
    ]

    for source, dataset_id, fields in sources:
        print(f"Loading RAG sample: {source} ({limit} rows)...")
        try:
            stream = load_dataset(dataset_id, split="train", streaming=True)
            count = 0
            for row in stream:
                text = " ".join(
                    f"{field}: {flatten(row.get(field))}"
                    for field in fields
                    if row.get(field) is not None
                )
                RAG.add(source, text)
                count += 1
                if count >= limit:
                    break
            print(f"  Added {count} {source} records.")
        except Exception as error:
            print(f"  Skipped {source}: {error}")


load_local_rag()
load_remote_rag()
RAG.fit()
print(f"Indexed {len(RAG.records)} RAG records.")


print("Loading base model...")
base_model = Qwen3VLForConditionalGeneration.from_pretrained(
    BASE_MODEL_ID,
    torch_dtype=torch.float16,
    device_map="auto",
    low_cpu_mem_usage=True,
    attn_implementation="sdpa",
    token=HF_TOKEN,
)

print("Loading QiFu adapter...")
model = PeftModel.from_pretrained(
    base_model,
    ADAPTER_ID,
    token=HF_TOKEN,
    low_cpu_mem_usage=True,
)
model.eval()
processor = AutoProcessor.from_pretrained(BASE_MODEL_ID, token=HF_TOKEN)
DEVICE = next(model.parameters()).device
print("Model loaded successfully.")


def read_page(url: str):
    response = requests.get(
        url,
        timeout=20,
        headers={"User-Agent": "Mozilla/5.0 QiFu-Agent"},
    )
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")
    for tag in soup(["script", "style", "noscript", "svg", "iframe"]):
        tag.decompose()
    title = soup.title.get_text(" ", strip=True) if soup.title else ""
    text = " ".join(soup.get_text(" ", strip=True).split())
    return f"Title: {title}\n{text[:9000]}"


def web_search(query: str, limit: int = 4):
    try:
        from ddgs import DDGS
        return list(DDGS().text(query, max_results=limit))
    except Exception as error:
        print(f"Search skipped: {error}")
        return []


def page_screenshot(url: str):
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=True)
            page = browser.new_page(viewport={"width": 1280, "height": 900})
            page.goto(url, wait_until="domcontentloaded", timeout=25000)
            page.wait_for_timeout(800)
            image = Image.open(BytesIO(page.screenshot(full_page=False))).convert("RGB")
            browser.close()
            return image
    except Exception as error:
        print(f"Screenshot skipped: {error}")
        return None


def research(prompt: str, url: str, inspect: bool):
    results = web_search(prompt, limit=4)
    urls = [item.get("href") or item.get("url") for item in results]
    pages = []
    with ThreadPoolExecutor(max_workers=4) as pool:
        jobs = {pool.submit(read_page, item): item for item in urls if item}
        for job in as_completed(jobs):
            try:
                pages.append(f"URL: {jobs[job]}\n{job.result()}")
            except Exception as error:
                print(f"Page skipped: {error}")
    screenshot = page_screenshot(url) if url and inspect else None
    snippets = "\n\n".join(
        f"Title: {item.get('title', '')}\nURL: {item.get('href', item.get('url', ''))}\n"
        f"Snippet: {item.get('body', item.get('snippet', ''))}"
        for item in results
    )
    return f"SEARCH:\n{snippets}\n\nPAGES:\n{'\n\n'.join(pages)}", screenshot


def clean_output(text: str) -> str:
    """Remove accidental continuation after the first complete HTML document."""
    if "</html>" in text.lower():
        end = text.lower().find("</html>") + len("</html>")
        return text[:end].strip()
    return text.strip()


def generate(image, url, prompt, use_web, inspect, max_tokens, temperature):
    try:
        yield "Preparing…", ""
        prompt = (prompt or "Review this UI and recommend improvements.").strip()
        context = RAG.search(prompt)
        web_context = "Web research disabled."
        research_image = None
        if use_web:
            yield "Searching and reading pages…", ""
            web_context, research_image = research(prompt, url, inspect)

        content = []
        if image is not None:
            content.append({"type": "image", "image": image})
        if research_image is not None:
            content.append({"type": "image", "image": research_image})
        content.append({"type": "text", "text": f"""
You are QiFu, a senior UI/UX designer and frontend engineer.

User request:
{prompt}

Retrieved UI references:
{context}

Web research:
{web_context}

Give a precise answer with a score, strengths, highest-impact issues,
prioritized recommendations, accessibility/responsive guidance, design-system
suggestions, and an implementation plan. Do not reveal private chain-of-thought;
give concise rationale instead. If a design or prototype is requested, include
a complete self-contained HTML/CSS/JavaScript file. Generate only one HTML
document. Do not repeat CSS selectors, sections, or code blocks. Stop immediately
after the closing </html> tag.
"""})

        inputs = processor.apply_chat_template(
            [{"role": "user", "content": content}],
            tokenize=True,
            add_generation_prompt=True,
            return_dict=True,
            return_tensors="pt",
        )
        inputs.pop("token_type_ids", None)
        inputs = {key: value.to(DEVICE) if hasattr(value, "to") else value for key, value in inputs.items()}
        streamer = TextIteratorStreamer(processor.tokenizer, skip_prompt=True, skip_special_tokens=True)
        errors = []

        def run():
            try:
                with torch.inference_mode():
                    model.generate(
                        **inputs,
                        streamer=streamer,
                        max_new_tokens=int(max_tokens),
                        temperature=float(temperature),
                        top_p=0.9,
                        repetition_penalty=1.08,
                        no_repeat_ngram_size=6,
                        do_sample=float(temperature) > 0,
                        use_cache=True,
                    )
            except Exception as error:
                errors.append(error)
                streamer.end()

        yield "Generating…", ""
        thread = threading.Thread(target=run, daemon=True)
        thread.start()
        output = ""
        for piece in streamer:
            output += piece
            print(piece, end="", flush=True)
            yield "Generating…", output
        thread.join()
        if errors:
            raise errors[0]
        print("\n[response complete]")
        yield "Response generated.", clean_output(output)
    except Exception as error:
        message = f"### Error\n```text\n{type(error).__name__}: {error}\n```"
        print(message)
        yield "Generation failed.", message


with gr.Blocks(title="QiFu UI/UX Agent v1") as demo:
    gr.Markdown("# QiFu UI/UX Agent v1")
    status = gr.Markdown("Ready.")
    with gr.Row():
        with gr.Column():
            image = gr.Image(type="pil", label="UI screenshot")
            url = gr.Textbox(label="Website URL", placeholder="https://example.com")
            prompt = gr.Textbox(
                label="Prompt",
                value="Design a cyberpunk e-commerce website and generate a complete HTML prototype.",
                lines=6,
            )
            use_web = gr.Checkbox(label="Use web search", value=False)
            inspect = gr.Checkbox(label="Render supplied URL", value=False)
            max_tokens = gr.Slider(256, 8192, value=3072, step=256, label="Maximum output tokens")
            temperature = gr.Slider(0.0, 1.0, value=0.45, step=0.05, label="Temperature")
            button = gr.Button("Generate", variant="primary")
        output = gr.Markdown()
    button.click(
        generate,
        inputs=[image, url, prompt, use_web, inspect, max_tokens, temperature],
        outputs=[status, output],
    )

demo.launch(share=True, server_name="0.0.0.0", server_port=7860, debug=True, show_error=True)
