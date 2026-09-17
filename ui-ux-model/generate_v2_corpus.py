"""Generate a balanced, reviewable Forma v2 seed corpus.

The records are deliberately marked needs_browser_review. They contain complete
initial/corrected HTML and critique traces, but this generator does not pretend
that browser measurements happened unless a separate Playwright validator runs.
"""

from __future__ import annotations

import argparse
import json
from html import escape
from pathlib import Path


PRODUCTS = [
    ("ecommerce", "Northline Goods", "help a shopper compare products and check out", "warm editorial", "#F4EFE7", "#241B17", "#C65D32", "serif headings with readable sans body"),
    ("saas dashboard", "TerraOps", "help an operations manager spot an anomaly and act", "quiet ecological", "#F5F7F6", "#17231F", "#247A5B", "calm geometric sans with tabular numbers"),
    ("science festival", "Open Field", "help a family find and reserve a suitable event", "bright civic", "#FFF9F0", "#13233A", "#F16B57", "friendly geometric sans with bold display headings"),
    ("telehealth portal", "Morrow Health", "help a patient book the right appointment confidently", "calm clinical", "#F4F8F7", "#173B42", "#287F78", "humanist sans with generous line-height"),
    ("personal finance app", "Lumen Ledger", "help a user understand spending and choose one next action", "trustworthy modern", "#F7F8FC", "#182238", "#5B62D6", "neutral sans with strong numeric hierarchy"),
    ("travel planning app", "Fieldnote", "help a traveler choose a stay and understand the itinerary", "sunlit atlas", "#FFF8ED", "#24344A", "#E4774E", "editorial serif accents with practical sans"),
    ("online course platform", "Common Thread", "help a learner resume a course and see progress", "warm academic", "#FAF7F1", "#282321", "#B45B35", "bookish serif display with accessible sans"),
    ("fitness tracker", "Arc Motion", "help a member choose a realistic workout for today", "energetic precise", "#F1F5F4", "#172526", "#E15B3D", "compact sans with bold metric numerals"),
    ("music discovery app", "Afterlight", "help a listener discover a playlist without decision fatigue", "late-night luminous", "#11131A", "#F5F3EF", "#B58CFF", "expressive display type with quiet UI labels"),
    ("nonprofit donation site", "Common Ground", "help a donor understand impact and complete a donation", "human and grounded", "#F7F3EC", "#20342D", "#D66C43", "friendly sans with restrained serif statement"),
    ("real-estate marketplace", "Hearthline", "help a renter compare homes and schedule a viewing", "quiet residential", "#F3F0EA", "#252A2B", "#647D68", "soft sans with strong address hierarchy"),
    ("developer documentation", "Signal Docs", "help a developer find an API example quickly", "technical editorial", "#F8FAFC", "#17202A", "#2563EB", "system sans with monospace code accents"),
    ("restaurant ordering app", "Saffron Table", "help a diner choose a meal and understand dietary options", "confident culinary", "#FFF7ED", "#321E19", "#D45A31", "high-contrast display serif and clear sans"),
    ("community forum", "Sidewalk", "help a new member find a relevant conversation and participate", "open neighborhood", "#F4F6F3", "#20302B", "#4F8F78", "approachable sans with clear metadata"),
    ("job marketplace", "Good Work", "help a candidate judge fit before applying", "direct optimistic", "#F6F8FB", "#1E293B", "#E07A3F", "neutral sans with concise labels"),
    ("event ticketing", "Night Index", "help a user find a live event and understand seating", "dark culture", "#111217", "#F4F1E9", "#FFB454", "editorial display with compact metadata"),
    ("logistics tracking", "Route 7", "help a customer understand delivery status and next steps", "clear utilitarian", "#F3F6F8", "#17212B", "#2775CA", "high-legibility sans with monospace IDs"),
    ("habit and wellbeing app", "Small Hours", "help a user complete one gentle daily ritual", "soft nocturnal", "#191A25", "#F3F0E8", "#D69A75", "soft serif headings with calm sans body"),
    ("public library site", "Civic Shelf", "help a visitor find a title and reserve it", "quiet public service", "#F7F8F5", "#1D302B", "#3B7A68", "readable sans with editorial title accents"),
    ("creative portfolio", "Mira Studio", "help a prospective client understand capability and start a conversation", "considered gallery", "#F2F0EC", "#171717", "#9A5A38", "large editorial type and restrained labels"),
]

VARIANTS = [
    ("mobile-first", "first-time users", "one primary action per section"),
    ("desktop-first", "returning users", "dense information without visual noise"),
    ("accessibility-first", "users with low vision", "meaning must never depend on color alone"),
    ("conversion-focused", "time-poor users", "make the next action obvious without pressure"),
    ("exploration-focused", "curious users", "support browsing while preserving a clear path"),
]


def initial_html(brand: str, product: str, accent: str, ink: str, background: str, goal: str) -> str:
    return f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{escape(brand)}</title><style>
body{{margin:0;font:16px Arial,sans-serif;background:{background};color:{ink}}}
header{{padding:24px 7%;background:{ink};color:white;display:flex;justify-content:space-between}}
nav{{display:flex;gap:24px}}.hero{{padding:90px 7%;display:grid;grid-template-columns:1fr 1fr;gap:48px}}
h1{{font:64px Georgia,serif;line-height:.95}}.cards{{display:grid;grid-template-columns:repeat(3,1fr);gap:16px;padding:30px 7%}}
.card{{background:white;padding:22px;border-radius:12px}}button{{background:{accent};color:white;border:0;padding:13px 18px;border-radius:7px}}
@media(max-width:700px){{nav{{display:none}}.hero{{grid-template-columns:1fr;padding:48px 6%}}.cards{{grid-template-columns:1fr;padding:20px 6%}}h1{{font-size:46px}}}}
</style></head><body><header><strong>{escape(brand)}</strong><nav><a href="#main">Overview</a><a href="#details">Details</a><a href="#help">Help</a></nav><button>Menu</button></header>
<main id="main"><section class="hero"><div><p>{escape(product.upper())}</p><h1>Make the next step easier.</h1><p>{escape(goal.capitalize())} with less searching and less friction.</p><button>Get started</button></div><div class="card"><h2>Today at a glance</h2><p>Important information appears here.</p></div></section><section id="details" class="cards"><article class="card"><h2>Key detail one</h2><p>Useful supporting information.</p></article><article class="card"><h2>Key detail two</h2><p>Useful supporting information.</p></article><article class="card"><h2>Key detail three</h2><p>Useful supporting information.</p></article></section></main></body></html>'''


def corrected_html(brand: str, product: str, accent: str, ink: str, background: str, goal: str, variant: str) -> str:
    return f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{escape(brand)} — {escape(product.title())}</title><style>
:root{{--bg:{background};--ink:{ink};--accent:{accent};--surface:#fff;--muted:#5e6a70;--focus:#174cff;--line:#d8dfdc}}
*{{box-sizing:border-box}}body{{margin:0;background:var(--bg);color:var(--ink);font:16px/1.55 Arial,sans-serif}}
a,button{{font:inherit}}a:focus-visible,button:focus-visible{{outline:3px solid var(--focus);outline-offset:3px}}
.shell{{width:min(1160px,88%);margin:auto}}header{{background:var(--ink);color:#fff}}
.bar{{min-height:70px;display:flex;align-items:center;gap:22px}}.brand{{font-weight:800;font-size:21px;margin-right:auto;color:#fff;text-decoration:none}}
.nav{{display:flex;gap:20px}}.nav a{{color:#fff;text-decoration:none}}.menu{{display:none;background:transparent;border:1px solid #fff;color:#fff;padding:8px;border-radius:8px}}
.hero{{padding:68px 0 52px;display:grid;grid-template-columns:minmax(0,1.2fr) minmax(280px,.8fr);gap:42px;align-items:center}}
.eyebrow{{color:var(--accent);font-size:12px;font-weight:800;letter-spacing:.12em}}h1{{font:clamp(3rem,7vw,6rem)/.93 Georgia,serif;letter-spacing:-.05em;margin:16px 0}}
.lede{{max-width:54ch;color:var(--muted)}}.actions{{display:flex;gap:10px;flex-wrap:wrap;margin-top:24px}}
.button{{display:inline-flex;align-items:center;padding:13px 18px;border-radius:8px;text-decoration:none;font-weight:700}}
.primary{{background:var(--accent);color:#fff}}.secondary{{border:1px solid var(--ink);color:var(--ink)}}
.hero-card,.card{{background:var(--surface);border:1px solid var(--line);border-radius:16px;padding:22px;box-shadow:0 8px 24px #14201812}}
.hero-card{{min-height:280px;display:flex;flex-direction:column;justify-content:end}}.hero-card strong{{font-size:28px}}
.section{{padding:26px 0 58px}}.section h2{{font:clamp(2rem,4vw,3.3rem)/1 Georgia,serif;margin:12px 0 22px}}
.grid{{display:grid;grid-template-columns:repeat(3,1fr);gap:16px}}.card h3{{margin:10px 0 6px}}.muted{{color:var(--muted)}}
.status{{display:inline-flex;padding:4px 9px;border-radius:99px;background:#e4f1eb;color:var(--ink);font-size:12px;font-weight:700}}
footer{{padding:28px 0 48px;border-top:1px solid var(--line);color:var(--muted)}}
@media(max-width:900px){{.grid{{grid-template-columns:repeat(2,1fr)}}}}
@media(max-width:700px){{.nav{{display:none}}.menu{{display:block}}.hero{{grid-template-columns:1fr;padding:46px 0 34px}}.hero-card{{min-height:220px;order:-1}}.grid{{grid-template-columns:1fr}}.bar{{min-height:64px}}}}
</style></head><body><header><div class="shell bar"><a class="brand" href="#top">{escape(brand)}</a><nav class="nav" aria-label="Primary navigation"><a href="#overview">Overview</a><a href="#details">Details</a><a href="#help">Help</a></nav><button class="menu" aria-label="Open navigation">Menu</button></div></header>
<main id="top"><section class="shell hero" id="overview"><div><div class="eyebrow">{escape(product.upper())} / {escape(variant.upper())}</div><h1>Make the next step easier.</h1><p class="lede">{escape(goal.capitalize())} with a clear path, useful context, and a calm interface that explains what matters now.</p><div class="actions"><a class="button primary" href="#details">Get started</a><a class="button secondary" href="#help">How it works</a></div></div><div class="hero-card"><span class="status">Ready to explore</span><h2>Today at a glance</h2><p class="muted">A focused summary keeps the most important decision visible without hiding the detail behind a maze of controls.</p></div></section><section class="shell section" id="details"><div class="eyebrow">DESIGNED FOR CLARITY</div><h2>Everything you need to move forward.</h2><div class="grid"><article class="card"><span class="status">01</span><h3>Clear starting point</h3><p class="muted">The primary action is visible and named for the result it produces.</p></article><article class="card"><span class="status">02</span><h3>Useful context</h3><p class="muted">Supporting details explain the decision without creating a wall of equal-weight content.</p></article><article class="card"><span class="status">03</span><h3>Confident next step</h3><p class="muted">Responsive states, labels, and feedback keep the experience understandable.</p></article></div></section></main><footer id="help"><div class="shell">{escape(brand)} — a focused experience for people who need to {escape(goal)}.</div></footer></body></html>'''


def make_record(index: int, product_row: tuple, variant_row: tuple) -> dict:
    product, brand, goal, direction, background, ink, accent, typography = product_row
    layout_mode, audience, constraint = variant_row
    example_id = f"forma_v2_generated_{index:03d}"
    task = f"Design a {layout_mode} {product} experience for {brand}. The primary goal is to {goal}."
    constraints = [layout_mode, audience, constraint, "must work at 390px and 1440px widths", "include visible keyboard focus states"]
    spec = {
        "information_architecture": f"Brand and primary navigation, focused hero/summary, decision-supporting details, one primary action, and a compact help/footer area for the {product} task.",
        "layout": f"Use a {direction} visual system on a {background} canvas with {ink} text and {accent} as a restrained action accent. Use a responsive two-column hero and a three-card desktop grid that collapses cleanly on mobile.",
        "tokens": {"background": background, "surface": "#FFFFFF", "text": ink, "muted": "#5E6A70", "accent": accent, "focus": "#174CFF", "radius": "16px", "space": "8px base scale"},
        "typography": f"Use {typography}. Body text stays at least 16px, headings use a clear scale, and metadata is visually secondary but readable.",
        "components": ["responsive header", "summary/hero card", "primary and secondary actions", "decision-supporting feature cards", "status badge", "help footer"],
        "responsive_rules": ["Collapse navigation to a labelled menu button below 700px.", "Stack hero content below 700px and keep the primary action visible before supporting detail.", "Collapse the feature grid from three columns to two and then one.", "Prevent horizontal overflow at 390px."],
        "interaction_states": ["keyboard focus ring", "button hover and active states", "menu open and closed states", "action loading and success states", "empty/error messaging where data is unavailable"],
        "accessibility": "Use semantic landmarks, one h1, descriptive link labels, real buttons, visible focus, meaningful status text, and no color-only meaning.",
    }
    initial = initial_html(brand, product, accent, ink, background, goal)
    corrected = corrected_html(brand, product, accent, ink, background, goal, layout_mode)
    return {
        "example_id": example_id,
        "task": task,
        "constraints": constraints,
        "reference_screenshots": [],
        "research_evidence": [
            "The primary action should be labelled by its outcome rather than a vague verb.",
            "Important context should sit close to the decision it explains.",
            "Responsive layouts must preserve hierarchy rather than simply shrink desktop content.",
        ],
        "design_spec": spec,
        "initial_code": initial,
        "render_report": {
            "status": "not_rendered",
            "viewports": [
                {"width": 1440, "height": 900, "horizontal_overflow": None, "console_errors": None},
                {"width": 390, "height": 844, "horizontal_overflow": None, "console_errors": None},
            ],
            "visual_score": None,
            "accessibility_score": None,
        },
        "critic_feedback": [
            "The initial implementation is too generic for the product task and does not expose enough decision-specific context.",
            "The mobile navigation disappears without a working menu state.",
            "The initial page lacks explicit focus styling and does not explain loading, empty, or error states.",
            "The first version uses equal-weight cards without a clear relationship to the user's primary goal.",
            "The corrected version must preserve the visual direction while improving hierarchy, semantics, and responsive behavior.",
        ],
        "corrected_code": corrected,
        "quality_score": None,
        "status": "needs_browser_review",
        "source": "programmatic-v2-corpus-generator",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default="v2_generated_100.jsonl")
    parser.add_argument("--count", type=int, default=100)
    args = parser.parse_args()
    rows = []
    for index in range(args.count):
        rows.append(make_record(index + 1, PRODUCTS[index % len(PRODUCTS)], VARIANTS[index % len(VARIANTS)]))
    with Path(args.output).open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n")
    manifest = {
        "output": args.output,
        "records": len(rows),
        "product_categories": len(PRODUCTS),
        "variants": len(VARIANTS),
        "render_status": "not_rendered",
        "next_step": "Run browser rendering and quality validation before training.",
    }
    Path(Path(args.output).with_suffix(".manifest.json")).write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
