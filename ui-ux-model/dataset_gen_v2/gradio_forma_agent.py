"""Forma V1/V2 test agent for Kaggle or a GPU machine.

Keys entered in the UI are held only in the current Python process and are not
written to disk. Use a private notebook/session when testing real credentials.
"""
from __future__ import annotations

import json
import os
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any

import gradio as gr
import requests
import torch
from bs4 import BeautifulSoup
from peft import PeftModel
from transformers import AutoProcessor, Qwen3VLForConditionalGeneration, TextIteratorStreamer

BASE_MODEL = os.getenv("FORMA_BASE_MODEL", "Qwen/Qwen3-VL-4B-Instruct")
ADAPTER = os.getenv("FORMA_ADAPTER", "EgoisticCoder/QiFu-v1")
HF_TOKEN = os.getenv("HF_TOKEN") or None
OPENROUTER_MODEL = "z-ai/glm-5.2:free"
GROQ_MODEL = "llama-3.3-70b-versatile"

print(f"Loading {BASE_MODEL} + {ADAPTER} …")
model = Qwen3VLForConditionalGeneration.from_pretrained(
    BASE_MODEL, device_map="auto", torch_dtype=torch.float16,
    low_cpu_mem_usage=True, token=HF_TOKEN, attn_implementation="sdpa",
)
model = PeftModel.from_pretrained(model, ADAPTER, token=HF_TOKEN, low_cpu_mem_usage=True)
model.eval()
processor = AutoProcessor.from_pretrained(BASE_MODEL, token=HF_TOKEN, use_fast=False)
DEVICE = next(model.parameters()).device
print("Forma model loaded.")


def flatten(value: Any) -> str:
    if isinstance(value, dict):
        return " ".join(f"{key}: {flatten(item)}" for key, item in value.items())
    if isinstance(value, list):
        return " ".join(flatten(item) for item in value)
    return "" if value is None else str(value)


def fetch_page(url: str) -> str:
    response = requests.get(url, timeout=20, headers={"User-Agent": "Forma/1.0"})
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")
    title = soup.title.get_text(" ", strip=True) if soup.title else ""
    for tag in soup(["script", "style", "noscript", "svg", "iframe"]):
        tag.decompose()
    text = " ".join(soup.get_text(" ", strip=True).split())
    return f"URL: {url}\nTitle: {title}\n{text[:10000]}"


def tavily_search(query: str, key: str) -> str:
    if not key.strip():
        return "Web search requested, but no Tavily key was supplied."
    response = requests.post(
        "https://api.tavily.com/search",
        json={"api_key": key.strip(), "query": query, "search_depth": "advanced", "max_results": 5, "include_answer": True},
        timeout=30,
    )
    response.raise_for_status()
    data = response.json()
    lines = [f"Tavily answer: {data.get('answer', '')}"]
    for item in data.get("results", []):
        lines.append(f"Source: {item.get('title', '')}\nURL: {item.get('url', '')}\n{item.get('content', '')[:2500]}")
    return "\n\n".join(lines)


def provider_code(prompt: str, openrouter_key: str, groq_key: str) -> tuple[str, str]:
    messages = [{"role": "system", "content": "You are a meticulous senior frontend engineer. Return production-quality accessible HTML/CSS/JS. Do not repeat code, do not use placeholders, and keep the response concise."}, {"role": "user", "content": prompt}]
    providers = []
    if openrouter_key.strip():
        providers.append(("OpenRouter", "https://openrouter.ai/api/v1", openrouter_key.strip(), OPENROUTER_MODEL))
    if groq_key.strip():
        providers.append(("Groq", "https://api.groq.com/openai/v1", groq_key.strip(), GROQ_MODEL))
    if not providers:
        return "No coding provider key supplied. Enable coding and enter an OpenRouter or Groq key.", "none"
    errors = []
    for name, base_url, key, model_name in providers:
        try:
            response = requests.post(
                f"{base_url}/chat/completions",
                headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
                json={"model": model_name, "messages": messages, "temperature": 0.2, "max_tokens": 12000},
                timeout=180,
            )
            response.raise_for_status()
            return response.json()["choices"][0]["message"]["content"], name
        except Exception as error:
            errors.append(f"{name}: {error}")
    return "Coding providers failed:\n" + "\n".join(errors), "failed"


def forma_stream(image, prompt: str, history: list[dict], url: str, use_search: bool, tavily_key: str, use_coding: bool, openrouter_key: str, groq_key: str, max_tokens: int):
    prompt = (prompt or "Review this interface for hierarchy, accessibility, responsive behavior, and interaction quality.").strip()
    history = history or []
    yield "Preparing analysis…", history
    web_context = "No web research requested."
    if use_search:
        yield "Searching with Tavily and reading the supplied page…", history
        try:
            search = tavily_search(prompt + (f" {url}" if url else ""), tavily_key)
            page = fetch_page(url) if url else ""
            web_context = search + ("\n\nSUPPLIED PAGE:\n" + page if page else "")
        except Exception as error:
            web_context = f"Web research failed: {error}"

    system = """You are Forma, Infra's senior UI/UX auditor and frontend engineer.
Analyze only evidence present in the screenshot/page context. Give specific findings with category, severity, element/value, and concrete fix. Cover hierarchy, contrast, responsive behavior, interaction states, layout, accessibility structure, and content. Do not invent defects. If asked for code, produce one complete non-repeated HTML document. Keep reasoning brief and expose only a useful progress summary, not hidden chain-of-thought."""
    context = f"\nWEB CONTEXT:\n{web_context}\n" if web_context else ""
    user_text = f"{system}\n\nUSER REQUEST:\n{prompt}{context}\n\nConversation context:\n{json.dumps(history[-6:], ensure_ascii=False)}"
    content = []
    if image is not None:
        content.append({"type": "image", "image": image})
    content.append({"type": "text", "text": user_text})
    messages = [{"role": "user", "content": content}]
    inputs = processor.apply_chat_template(messages, add_generation_prompt=True, tokenize=True, return_tensors="pt", return_dict=True)
    inputs = {key: value.to(DEVICE) if hasattr(value, "to") else value for key, value in inputs.items()}
    streamer = TextIteratorStreamer(processor.tokenizer, skip_prompt=True, skip_special_tokens=True)
    generation = dict(**inputs, streamer=streamer, max_new_tokens=int(max_tokens), do_sample=True, temperature=0.35, top_p=0.9, repetition_penalty=1.08)
    thread = threading.Thread(target=model.generate, kwargs=generation)
    thread.start()
    output = ""
    for piece in streamer:
        output += piece
        yield output, history
    thread.join()
    if use_coding:
        yield output + "\n\n_Coding model is drafting the implementation…_", history
        code_prompt = f"User request: {prompt}\n\nForma visual analysis:\n{output}\n\nWeb evidence:\n{web_context}\n\nCreate or improve the complete frontend implementation. Return only the final code and a short implementation note."
        code, provider = provider_code(code_prompt, openrouter_key, groq_key)
        output += f"\n\n### Implementation ({provider})\n\n{code}"
    history = history + [{"role": "user", "content": prompt}, {"role": "assistant", "content": output}]
    yield output, history


with gr.Blocks(title="Forma — Infra") as demo:
    gr.Markdown("# Forma\n### See better. Design smarter.\nUpload a UI screenshot, describe a design, or provide a URL for grounded UI/UX analysis.")
    history = gr.State([])
    with gr.Row():
        with gr.Column(scale=1):
            image = gr.Image(type="pil", label="UI screenshot (optional)")
            url = gr.Textbox(label="Website URL (optional)", placeholder="https://example.com")
            prompt = gr.Textbox(label="Prompt", lines=5, value="Review this interface and give specific, actionable UX, accessibility, responsive, and frontend recommendations.")
            use_search = gr.Checkbox(label="Use Tavily web search", value=False)
            tavily_key = gr.Textbox(label="Tavily API key (session-only)", type="password")
            use_coding = gr.Checkbox(label="Generate/improve code with external coding model", value=False)
            openrouter_key = gr.Textbox(label="OpenRouter key (primary, session-only)", type="password")
            groq_key = gr.Textbox(label="Groq key (fallback, session-only)", type="password")
            max_tokens = gr.Slider(512, 12000, value=4096, step=256, label="Forma output tokens")
            submit = gr.Button("Analyze", variant="primary")
            clear = gr.Button("Clear history")
        with gr.Column(scale=2):
            status = gr.Markdown("Ready.")
            output = gr.Markdown()
    submit.click(forma_stream, [image, prompt, history, url, use_search, tavily_key, use_coding, openrouter_key, groq_key, max_tokens], [output, history]).then(lambda: "Completed.", None, status)
    clear.click(lambda: ([], "", "Ready."), None, [history, output, status])


if __name__ == "__main__":
    demo.queue(default_concurrency_limit=1).launch(server_name="0.0.0.0", server_port=int(os.getenv("PORT", "7860")), share=True, show_error=True)
