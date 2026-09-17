#!/usr/bin/env python3
"""Normalize records and run fast browser/static quality checks.

This intentionally does not invent visual or accessibility scores. Those remain
null until a human/vision reviewer assigns them.
"""
from __future__ import annotations

import json
import re
from collections import Counter
from pathlib import Path

from playwright.sync_api import sync_playwright

INPUT = Path("v2_merged_candidate.jsonl")
OUTPUT = Path("v2_review_ready.jsonl")
MANIFEST = Path("v2_review_ready.manifest.json")
VIEWPORTS = [(1440, 900), (390, 844)]
TOKEN_ALIASES = {"dark": "text", "coral": "accent", "teal": "accent"}


def normalize_tokens(tokens: dict) -> dict:
    source = dict(tokens)
    for old, new in TOKEN_ALIASES.items():
        if new not in source and old in source:
            source[new] = source[old]
    # Keep one stable schema so downstream training/evaluation code can rely on
    # the same token names for every record.
    defaults = {
        "background": "#F7F8FA", "surface": "#FFFFFF", "text": "#17202A",
        "muted": "#5E6A70", "accent": "#2563EB", "focus": "#174CFF",
        "radius": "16px", "space": "8px base scale",
    }
    return {key: source.get(key, default) for key, default in defaults.items()}


def static_findings(html: str) -> list[dict]:
    findings = []
    lower = html.lower()
    if not re.search(r"<main(?:\s|>)", lower):
        findings.append({"category": "accessibility_structure", "severity": "medium", "text": "The document has no <main> landmark."})
    if not re.search(r"<h1(?:\s|>)", lower):
        findings.append({"category": "hierarchy", "severity": "medium", "text": "The document has no visible h1 heading."})
    for match in re.finditer(r"<img\b([^>]*)>", lower):
        if not re.search(r"\balt\s*=", match.group(1)):
            findings.append({"category": "accessibility_structure", "severity": "high", "text": "An image element is missing an alt attribute."})
            break
    if re.search(r"outline\s*:\s*none|outline\s*:\s*0", lower) and not re.search(r":focus[^{}]*\{[^}]*outline|:focus-visible[^{}]*\{[^}]*outline|box-shadow[^;]*focus", lower):
        findings.append({"category": "interaction_states", "severity": "high", "text": "The stylesheet removes focus outlines without a visible replacement."})
    if re.search(r"<div[^>]+onclick=|<span[^>]+onclick=", lower):
        findings.append({"category": "accessibility_structure", "severity": "high", "text": "A div or span uses onclick instead of a keyboard-accessible button or link."})
    return findings


def inspect(page, html: str, width: int, height: int) -> dict:
    errors = []
    page.on("console", lambda message: errors.append(message.text) if message.type == "error" else None)
    page_errors = []
    page.on("pageerror", lambda error: page_errors.append(str(error)))
    page.set_viewport_size({"width": width, "height": height})
    page.set_content(html, wait_until="load")
    page.wait_for_timeout(20)
    result = page.evaluate("""() => {
      const all = [...document.querySelectorAll('a,button,input,select,textarea,[role="button"]')];
      const unlabeled = all.filter(el => !el.getAttribute('aria-label') && !el.textContent.trim() && !el.getAttribute('title')).length;
      const small = all.filter(el => { const r=el.getBoundingClientRect(); return r.width < 44 || r.height < 44; }).length;
      return {
        scrollWidth: document.documentElement.scrollWidth,
        clientWidth: document.documentElement.clientWidth,
        has_h1: Boolean(document.querySelector('h1')),
        has_main: Boolean(document.querySelector('main')),
        focusable_count: all.length,
        unlabeled_interactive_count: unlabeled,
        small_target_count: small
      };
    }""")
    result.update({
        "width": width, "height": height,
        "horizontal_overflow": result["scrollWidth"] > result["clientWidth"] + 1,
        "console_errors": len(errors) + len(page_errors),
    })
    return result


def main() -> None:
    rows = []
    counts = Counter()
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True, args=["--no-sandbox", "--disable-setuid-sandbox"])
        page = browser.new_page()
        for line in INPUT.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            row = json.loads(line)
            row["design_spec"]["tokens"] = normalize_tokens(row["design_spec"].get("tokens", {}))
            initial_static = static_findings(row["initial_code"])
            corrected_static = static_findings(row["corrected_code"])
            viewports = []
            for width, height in VIEWPORTS:
                viewports.append({
                    "width": width, "height": height,
                    "initial": inspect(page, row["initial_code"], width, height),
                    "corrected": inspect(page, row["corrected_code"], width, height),
                })
            objective = []
            for viewport in viewports:
                corrected = viewport["corrected"]
                if corrected["horizontal_overflow"]:
                    objective.append({"category": "responsive", "severity": "high", "text": f"Corrected page overflows horizontally at {viewport['width']}px."})
                if corrected["console_errors"]:
                    objective.append({"category": "interaction_states", "severity": "high", "text": f"Corrected page emits {corrected['console_errors']} browser error(s) at {viewport['width']}px."})
                if corrected["unlabeled_interactive_count"]:
                    objective.append({"category": "accessibility_structure", "severity": "high", "text": f"Corrected page has {corrected['unlabeled_interactive_count']} unlabeled interactive control(s) at {viewport['width']}px."})
                if corrected["small_target_count"]:
                    objective.append({"category": "responsive", "severity": "medium", "text": f"Corrected page has {corrected['small_target_count']} interactive target(s) below 44px at {viewport['width']}px."})
            findings = corrected_static + objective
            row["render_report"] = {"status": "rendered_needs_visual_review", "viewports": viewports, "visual_score": None, "accessibility_score": None, "screenshots_captured": False}
            row["audit_findings"] = findings
            row["recommendations"] = [{"finding_ref": item["text"], "recommendation": "Fix the cited element before acceptance; preserve the stated design tokens and responsive constraints.", "css_or_html_change": "See finding-specific implementation in the review pass.", "expected_effect": "Removes the detected objective defect."} for item in findings]
            row["status"] = "needs_human_visual_review"
            rows.append(row)
            counts.update([item["category"] for item in findings])
        browser.close()
    with OUTPUT.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n")
    manifest = {"input": str(INPUT), "output": str(OUTPUT), "records": len(rows), "objective_finding_categories": dict(counts), "visual_scores_assigned": False, "screenshots_embedded": False, "ready_for_final_training": False, "reason": "Human or vision-model visual review is still required; this pass does not invent visual scores."}
    MANIFEST.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
