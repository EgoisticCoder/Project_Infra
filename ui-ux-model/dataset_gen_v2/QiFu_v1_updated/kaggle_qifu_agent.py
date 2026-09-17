"""Kaggle-ready QiFu agent: streaming generation, optional web research, and RAG.

Expected Kaggle setup:
  pip install -q -U gradio transformers peft accelerate torchvision \
      beautifulsoup4 requests ddgs scikit-learn playwright
  # This agent has no audio input; remove Kaggle's often CUDA-mismatched wheel.
  pip uninstall -y torchaudio
  playwright install chromium

Set QIFU_RAG_FILES to a comma-separated list of uploaded JSONL files, for example:
  /kaggle/input/uiux-rag/design_principles.jsonl,
  /kaggle/input/uiux-rag/seed_examples.jsonl
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
from transformers import (
    AutoProcessor,
    Qwen3VLForConditionalGeneration,
    TextIteratorStreamer,
)


BASE_MODEL_ID = "Qwen/Qwen3-VL-4B-Instruct"
ADAPTER_ID = os.getenv("MODEL_ID", "EgoisticCoder/QiFu-v1")
HF_TOKEN = os.getenv("HF_TOKEN") or None


def flatten(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, dict):
        return " ".join(f"{k}: {flatten(v)}" for k, v in value.items())
    if isinstance(value, list):
        return " ".join(flatten(v) for v in value)
    return str(value)


class LocalRAG:
    """Small, dependency-light lexical RAG index for UI/UX references."""

    def __init__(self, paths: list[str]):
        self.records: list[dict[str, str]] = []
        for raw_path in paths:
            path = Path(raw_path.strip())
            if not path.exists() or path.suffix != ".jsonl":
                continue
            source = path.stem
            with path.open("r", encoding="utf-8", errors="replace") as handle:
                for line in handle:
                    try:
                        row = json.loads(line)
                    except json.JSONDecodeError:
                        continue
                    text = flatten(row).strip()
                    if text:
                        self.records.append({"source": source, "text": text[:8000]})

        self.vectorizer = None
        self.matrix = None
        self._fit()

    def add_records(self, records: list[dict[str, str]]) -> None:
        self.records.extend(records)
        self._fit()

    def _fit(self) -> None:
        self.vectorizer = None
        self.matrix = None
        if self.records:
            self.vectorizer = TfidfVectorizer(
                lowercase=True,
                ngram_range=(1, 2),
                max_features=50000,
                stop_words="english",
            )
            self.matrix = self.vectorizer.fit_transform(
                [record["text"] for record in self.records]
            )

    def retrieve(self, query: str, k: int = 5) -> str:
        if not self.records or self.vectorizer is None or self.matrix is None:
            return "No local reference material was indexed."
        query_vector = self.vectorizer.transform([query])
        scores = cosine_similarity(query_vector, self.matrix)[0]
        indices = scores.argsort()[::-1][:k]
        chunks = []
        for index in indices:
            if scores[index] <= 0:
                continue
            record = self.records[index]
            chunks.append(
                f"[source: {record['source']}; relevance: {scores[index]:.2f}]\n"
                f"{record['text']}"
            )
        return "\n\n".join(chunks) or "No relevant local references found."


rag_paths = [
    path for path in os.getenv("QIFU_RAG_FILES", "").split(",") if path.strip()
]
RAG = LocalRAG(rag_paths)


def load_remote_rag_sources(max_rows: int = 250) -> list[dict[str, str]]:
    """Load a small, source-labelled retrieval index from HF datasets.

    This intentionally samples only a small number of rows. RAG should provide
    examples and vocabulary at inference time; it should not pull an entire
    training corpus into every Kaggle process.
    """
    try:
        from datasets import load_dataset
    except ImportError:
        print("Install datasets to enable remote RAG sources.")
        return []

    sources = [
        ("WebSight", "HuggingFaceM4/WebSight", ["llm_generated_idea", "text"]),
        ("Rico", "Voxel51/rico", ["detections"]),
        ("Screen2Words", "rootsautomation/RICO-Screen2Words", ["captions"]),
        ("WebUI", "xlelords/webui", [
            "title", "category", "meta_description", "color_palette",
            "fonts", "elements", "num_elements", "word_count",
        ]),
        # Mind2Web variants have changed names/schemas; override this ID if
        # your uploaded copy uses another repository or config.
        ("Mind2Web", "osunlp/Multimodal-Mind2Web", []),
        # VINS is commonly distributed as an archive rather than a standard
        # datasets table. Put extracted XML/JSON records in QIFU_RAG_FILES.
    ]
    collected: list[dict[str, str]] = []

    for source, dataset_id, preferred_fields in sources:
        try:
            print(f"Loading RAG sample: {source}...")
            stream = load_dataset(dataset_id, split="train", streaming=True)
            count = 0
            for row in stream:
                fields = preferred_fields or [
                    key for key in row
                    if key.lower() not in {
                        "image", "images", "screenshot", "pixel_values",
                        "html", "dom", "raw_html", "image_url",
                    }
                ]
                text = " ".join(
                    f"{field}: {flatten(row.get(field))}"
                    for field in fields
                    if row.get(field) is not None
                ).strip()
                if text:
                    collected.append({
                        "source": source,
                        "text": text[:8000],
                    })
                    count += 1
                if count >= max_rows:
                    break
            print(f"  Added {count} {source} records.")
        except Exception as error:
            print(f"  Skipped {source}: {error}")

    return collected


if os.getenv("QIFU_ENABLE_REMOTE_RAG", "0") == "1":
    remote_limit = int(os.getenv("QIFU_REMOTE_RAG_ROWS", "250"))
    RAG.add_records(load_remote_rag_sources(max_rows=remote_limit))
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


def clean_page(url: str) -> tuple[str, Image.Image | None]:
    response = requests.get(
        url,
        timeout=20,
        headers={"User-Agent": "Mozilla/5.0 QiFu-UIUX-Agent"},
    )
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")
    for tag in soup(["script", "style", "noscript", "svg", "iframe"]):
        tag.decompose()
    title = soup.title.get_text(" ", strip=True) if soup.title else ""
    text = " ".join(soup.get_text(" ", strip=True).split())
    return f"Title: {title}\n{text[:10000]}", None


def screenshot_page(url: str) -> Image.Image | None:
    try:
        from playwright.sync_api import sync_playwright

        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=True)
            page = browser.new_page(viewport={"width": 1280, "height": 900})
            page.goto(url, wait_until="domcontentloaded", timeout=25000)
            page.wait_for_timeout(1000)
            image = Image.open(BytesIO(page.screenshot(full_page=False))).convert("RGB")
            browser.close()
            return image
    except Exception as error:
        print(f"Screenshot skipped: {error}")
        return None


def search_web(query: str, limit: int = 4) -> list[dict[str, str]]:
    try:
        from ddgs import DDGS

        return list(DDGS().text(query, max_results=limit))
    except Exception as error:
        print(f"Web search skipped: {error}")
        return []


def research(query: str, website_url: str, inspect_page: bool) -> tuple[str, Image.Image | None]:
    results = search_web(query, limit=4)
    urls = [item.get("href") or item.get("url") for item in results]
    urls = [url for url in urls if url]
    page_parts = []

    with ThreadPoolExecutor(max_workers=4) as pool:
        jobs = {pool.submit(clean_page, url): url for url in urls[:4]}
        for job in as_completed(jobs):
            url = jobs[job]
            try:
                text, _ = job.result()
                page_parts.append(f"URL: {url}\n{text}")
            except Exception as error:
                print(f"Fetch skipped for {url}: {error}")

    screenshot = None
    if website_url and inspect_page:
        screenshot = screenshot_page(website_url)

    search_summary = "\n\n".join(
        f"Title: {item.get('title', '')}\nURL: {item.get('href', item.get('url', ''))}\n"
        f"Snippet: {item.get('body', item.get('snippet', ''))}"
        for item in results
    )
    return (
        f"SEARCH RESULTS:\n{search_summary}\n\nFETCHED PAGE TEXT:\n"
        f"{'\n\n'.join(page_parts[:4])}",
        screenshot,
    )


def generate_agent(
    image,
    website_url,
    prompt,
    use_web,
    inspect_page,
    max_tokens,
    temperature,
):
    """Generator used by Gradio; yields progress and streamed markdown."""
    try:
        prompt = (prompt or "Review this UI and suggest improvements.").strip()
        yield "⏳ Preparing request…", ""

        query = f"UI UX design patterns and accessibility guidance for: {prompt}"
        local_context = RAG.retrieve(prompt, k=5)
        web_context = "No web research requested."
        research_image = None

        if use_web:
            yield "🌐 Searching and reading relevant pages…", ""
            web_context, research_image = research(query, website_url, inspect_page)

        content = []
        if image is not None:
            content.append({"type": "image", "image": image})
        if research_image is not None:
            content.append({"type": "image", "image": research_image})

        final_prompt = f"""
You are QiFu, a senior product designer, UI/UX critic, visual design analyst,
and frontend engineer.

User request:
{prompt}

Use the following retrieved material only as supporting evidence. Do not copy
irrelevant tasks from it and do not claim that a retrieved example is a fact:

LOCAL UI/UX REFERENCES:
{local_context}

WEB RESEARCH:
{web_context}

Produce a precise, practical answer. Internally reason through hierarchy,
layout, typography, contrast, accessibility, interaction states, responsive
behavior, content structure, and conversion friction. Do not reveal private
chain-of-thought; provide concise rationale for each recommendation instead.

Use this response structure when applicable:
1. Overall verdict and score out of 10
2. What works
3. Highest-impact problems
4. Prioritized recommendations with rationale
5. Responsive and accessibility checklist
6. Suggested design system: colors, type scale, spacing, components, states
7. Implementation plan

If the user asks to design, recreate, or generate a UI, include a complete
self-contained HTML file with CSS and JavaScript after the recommendations.
Make it polished, responsive, accessible, and runnable without external files.
"""
        content.append({"type": "text", "text": final_prompt})
        messages = [{"role": "user", "content": content}]

        inputs = processor.apply_chat_template(
            messages,
            tokenize=True,
            add_generation_prompt=True,
            return_dict=True,
            return_tensors="pt",
        )
        inputs.pop("token_type_ids", None)
        inputs = {
            key: value.to(DEVICE) if hasattr(value, "to") else value
            for key, value in inputs.items()
        }

        streamer = TextIteratorStreamer(
            processor.tokenizer,
            skip_prompt=True,
            skip_special_tokens=True,
        )
        generation_error: list[Exception] = []

        def run_generation():
            try:
                with torch.inference_mode():
                    model.generate(
                        **inputs,
                        streamer=streamer,
                        max_new_tokens=int(max_tokens),
                        temperature=float(temperature),
                        top_p=0.9,
                        do_sample=float(temperature) > 0,
                        use_cache=True,
                    )
            except Exception as error:
                generation_error.append(error)
                streamer.end()

        yield "🧠 Generating response…", ""
        worker = threading.Thread(target=run_generation, daemon=True)
        worker.start()

        output = ""
        for piece in streamer:
            output += piece
            print(piece, end="", flush=True)
            yield "🧠 Generating response…", output
        worker.join()
        print("\n[QiFu generation complete]")

        if generation_error:
            raise generation_error[0]
        yield "✅ Response generated.", output.strip()
    except Exception as error:
        message = f"### Error\n\n```text\n{type(error).__name__}: {error}\n```"
        print(message)
        yield "❌ Generation failed.", message


with gr.Blocks(title="QiFu UI/UX Agent v1") as demo:
    gr.Markdown("# QiFu UI/UX Agent v1")
    status = gr.Markdown("Ready.")

    with gr.Row():
        with gr.Column():
            image = gr.Image(type="pil", label="Current UI screenshot")
            website_url = gr.Textbox(
                label="Website URL",
                placeholder="https://example.com",
            )
            prompt = gr.Textbox(
                label="Request",
                value=(
                    "Design a polished e-commerce website with a cyberpunk theme. "
                    "Give UI/UX recommendations and generate a complete HTML prototype."
                ),
                lines=7,
            )
            use_web = gr.Checkbox(
                label="Use web research",
                value=False,
            )
            inspect_page = gr.Checkbox(
                label="Render the supplied URL and inspect its appearance",
                value=False,
            )
            max_tokens = gr.Slider(
                minimum=256,
                maximum=8192,
                value=2048,
                step=256,
                label="Maximum output tokens",
            )
            temperature = gr.Slider(
                minimum=0.0,
                maximum=1.0,
                value=0.45,
                step=0.05,
                label="Temperature",
            )
            submit = gr.Button("Generate", variant="primary")

        output = gr.Markdown(label="QiFu response")

    submit.click(
        generate_agent,
        inputs=[image, website_url, prompt, use_web, inspect_page, max_tokens, temperature],
        outputs=[status, output],
    )


demo.launch(
    share=True,
    server_name="0.0.0.0",
    server_port=7860,
    debug=True,
    show_error=True,
)
