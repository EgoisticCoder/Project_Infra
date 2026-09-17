"""Render generated v2 HTML at desktop/mobile widths and update reports."""

import argparse
import json
from pathlib import Path

from playwright.sync_api import sync_playwright


VIEWPORTS = [(1440, 900), (390, 844)]


def inspect_page(browser, html: str, width: int, height: int) -> dict:
    page = browser.new_page(viewport={"width": width, "height": height})
    console_errors = []
    page.on("console", lambda message: console_errors.append(message.text) if message.type == "error" else None)
    page_errors = []
    page.on("pageerror", lambda error: page_errors.append(str(error)))
    try:
        page.set_content(html, wait_until="load")
        page.wait_for_timeout(50)
        metrics = page.evaluate("""() => ({
            scrollWidth: document.documentElement.scrollWidth,
            clientWidth: document.documentElement.clientWidth,
            hasH1: Boolean(document.querySelector('h1')),
            hasMain: Boolean(document.querySelector('main')),
            focusableCount: document.querySelectorAll('a,button,input,select,textarea').length
        })""")
        page.screenshot(type="png", full_page=False)
        return {
            "width": width,
            "height": height,
            "horizontal_overflow": metrics["scrollWidth"] > metrics["clientWidth"] + 1,
            "console_errors": len(console_errors) + len(page_errors),
            "has_h1": metrics["hasH1"],
            "has_main": metrics["hasMain"],
            "focusable_count": metrics["focusableCount"],
        }
    finally:
        page.close()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("input")
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    rows = []
    rendered = 0
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        try:
            for line_number, line in enumerate(Path(args.input).read_text(encoding="utf-8").splitlines(), 1):
                if not line.strip():
                    continue
                row = json.loads(line)
                initial = [inspect_page(browser, row["initial_code"], *viewport) for viewport in VIEWPORTS]
                corrected = [inspect_page(browser, row["corrected_code"], *viewport) for viewport in VIEWPORTS]
                row["render_report"] = {
                    "status": "rendered_needs_visual_review",
                    "viewports": [
                        {
                            "width": viewport["width"],
                            "height": viewport["height"],
                            "initial": initial[index],
                            "corrected": corrected[index],
                        }
                        for index, viewport in enumerate(initial)
                    ],
                    "visual_score": None,
                    "accessibility_score": None,
                    "screenshots_captured": True,
                }
                row["status"] = "rendered_needs_visual_review"
                rows.append(row)
                rendered += 1
                if rendered % 20 == 0:
                    print(f"Rendered {rendered} records")
        finally:
            browser.close()
    with Path(args.output).open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n")
    print(f"Wrote {rendered} rendered records to {args.output}")


if __name__ == "__main__":
    main()
