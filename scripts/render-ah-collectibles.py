#!/usr/bin/env python3
"""Render the Companions, Mounts & Accessories AH guide."""

from __future__ import annotations

import argparse
import html
import importlib.util
import json
import re
import sys
import unicodedata
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "data" / "ah-collectible-sections.json"
AUDIT_PATH = ROOT / "data" / "ah-collectible-audit.json"
OUTPUT_PATH = ROOT / "guides" / "companions-mounts-accessories-ah-price-guide.html"
MANIFEST_PATH = ROOT / "data" / "ah-guides.json"
UX_RENDERER_PATH = ROOT / "scripts" / "render-ah-guide-ux.py"
SHARED_RENDERER_PATH = ROOT / "scripts" / "render-ah-shared-sections.py"
ASSET_VERSION = "20260810-ah-collectibles-v1"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def canonical_guide_ux(source: str) -> str:
    spec = importlib.util.spec_from_file_location("ah_collectible_ux_renderer", UX_RENDERER_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("Could not load the shared AH guide UX renderer")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    guide = next(item for item in load(MANIFEST_PATH)["guides"] if item["id"] == "collectibles")
    source = module.transform_page(source, guide)
    shared_spec = importlib.util.spec_from_file_location(
        "ah_collectible_shared_renderer", SHARED_RENDERER_PATH
    )
    if shared_spec is None or shared_spec.loader is None:
        raise RuntimeError("Could not load the shared AH section renderer")
    shared = importlib.util.module_from_spec(shared_spec)
    shared_spec.loader.exec_module(shared)
    return shared.transform_guide(
        source,
        guide["file"],
        guide,
        shared.NAV_TEMPLATE_PATH.read_text(encoding="utf-8").strip(),
        shared.BASELINE_NOTE_TEMPLATE_PATH.read_text(encoding="utf-8").strip(),
        shared.VENDOR_TEMPLATE_PATH.read_text(encoding="utf-8").strip(),
        shared.CRAFTED_TEMPLATE_PATH.read_text(encoding="utf-8").strip(),
        shared.DROPPED_SCROLL_TEMPLATE_PATH.read_text(encoding="utf-8").strip(),
        shared.load_vendor_config(),
        shared.load_crafted_config(),
        shared.load_dropped_scroll_config(),
    )


def slug(value: str) -> str:
    value = "".join(
        character for character in unicodedata.normalize("NFKD", value)
        if not unicodedata.combining(character)
    )
    return re.sub(r"[^a-z0-9]+", "-", value.casefold()).strip("-")


def format_money(copper: int) -> str:
    if copper >= 10_000:
        copper = ((copper + 50) // 100) * 100
    gold, remainder = divmod(copper, 10_000)
    silver, copper = divmod(remainder, 100)
    parts = []
    if gold:
        parts.append(f"{gold:,}g")
    if silver:
        parts.append(f"{silver}s")
    if copper or not parts:
        parts.append(f"{copper}c")
    return " ".join(parts)


def price_pair(kind: str, copper: int, *, label: str = "Buyout") -> str:
    bid = max(1, round(copper * 0.85))
    return (
        f'<div class="pricepair {kind}">'
        f'<div><span class="label">Bid</span><span class="bid">{format_money(bid)}</span></div>'
        f'<div><span class="label">{html.escape(label)}</span><span class="buyout">{format_money(copper)}</span></div>'
        '</div>'
    )


def exact_facts(item: dict) -> list[str]:
    facts = []
    if item["vendor_cost_copper"] is not None:
        facts.append(f'Exact vendor cost: {format_money(int(item["vendor_cost_copper"]))}.')
    if item["currency_cost"]:
        facts.append(f'Exact currency cost: {item["currency_cost"]}.')
    if item["recipe_floor_copper"]:
        floor = item["recipe_floor_copper"]
        facts.append(
            "Recipe floor: "
            f'{format_money(int(floor["quick"]))} / {format_money(int(floor["target"]))} / '
            f'{format_money(int(floor["high"]))}.'
        )
    if item["required_skill_id"]:
        skill = {197: "Tailoring", 202: "Engineering", 762: "Riding"}.get(item["required_skill_id"], "Profession")
        facts.append(f'{skill} {item["required_skill_rank"]} required to use.')
    if item.get("faction"):
        facts.append(f'{item["faction"]} recipe and buyer market.')
    return facts


def owner_note(item: dict) -> str:
    owner = item["canonical_owner"]
    if owner == "data/ah-crafted-sections.json":
        guide = "tailoring-cloth-ah-price-guide.html" if item["required_skill_id"] == 197 else "engineering-materials-ah-price-guide.html"
        label = "Tailoring" if item["required_skill_id"] == 197 else "Engineering"
        return f' <a href="./{guide}#ah-item={slug(item["name"])}">Canonical {label} row</a>.'
    if owner == "data/ah-vendor-sections.json":
        return ' <a href="./fishing-cooking-materials-ah-price-guide.html#ah-item=holiday-spices">Canonical Fishing &amp; Cooking row</a>.'
    return ""


def render_row(key: str, item: dict) -> str:
    facts = " ".join(exact_facts(item))
    confidence = "Exact acquisition floor" if item["vendor_cost_copper"] is not None else "Fallback market band"
    search_hint = " ".join(filter(None, [item["kind"], item["season"], item["source"]]))
    return (
        f'<tr data-collectible-key="{html.escape(key)}" data-market-source="{html.escape(item["group"])}" '
        f'data-search-hint="{html.escape(search_hint, quote=True)}">'
        '<td data-column="item" data-label="Item">'
        f'<strong class="q-{html.escape(item["quality"])}">{html.escape(item["name"])}</strong>'
        f'<div class="mini">{html.escape(item["kind"])} • Item {item["item_id"]}</div></td>'
        f'<td data-column="target" data-label="Target Price">{price_pair("target", int(item["target_copper"]))}</td>'
        f'<td data-column="quick" data-label="Quick Price">{price_pair("quick", int(item["quick_copper"]))}</td>'
        f'<td data-column="high" data-label="High / Scarce">{price_pair("high", int(item["high_copper"]))}</td>'
        f'<td data-column="stack" data-label="Stack Size">{html.escape(item["stack"])}</td>'
        f'<td data-column="demand" data-label="Demand"><span class="demand {html.escape(item["demand_class"])}">{html.escape(item["demand"])}</span></td>'
        '<td data-column="notes" data-label="Source / Selling Notes">'
        f'<strong>{html.escape(confidence)}.</strong> {html.escape(item["source"])}. '
        f'{html.escape(facts)} {html.escape(item["notes"])}{owner_note(item)}</td></tr>'
    )


def render_section(section: dict, catalog: dict) -> str:
    audience = section.get("audience")
    audience_attribute = (
        f' data-use-audience="{html.escape(audience)}"' if audience else ""
    )
    heading = (
        f'<h2 class="ah-category-heading">{html.escape(section["title"])}'
        '<a class="ah-back-to-top" href="#top" aria-label="Back to top">↑ Top</a></h2>'
    )
    intro = f'<p class="small">{html.escape(section["description"])}</p>'
    if not section["items"]:
        return (
            f'<section class="common collectible-market-section collectible-market-section--empty" '
            f'data-collectible-section="{html.escape(section["id"])}"{audience_attribute}>{heading}{intro}'
            f'<div class="note"><strong>No priced rows:</strong> {html.escape(section["empty_reason"])}</div></section>'
        )
    rows = "\n".join(render_row(key, catalog[key]) for key in section["items"])
    return (
        f'<section class="common collectible-market-section" '
        f'data-collectible-section="{html.escape(section["id"])}"{audience_attribute}>'
        f'{heading}{intro}<div class="table-wrap"><table class="ah-market-table ah-market-table--extended" '
        'data-table-family="market"><thead><tr><th data-column="item">Item</th>'
        '<th data-column="target">Target Price</th><th data-column="quick">Quick Price</th>'
        '<th data-column="high">High / Scarce</th><th data-column="stack">Stack Size</th>'
        '<th data-column="demand">Demand</th><th data-column="notes">Source / Selling Notes</th>'
        f'</tr></thead><tbody>{rows}</tbody></table></div></section>'
    )


def render_page(data: dict, audit: dict) -> str:
    catalog = data["catalog"]
    sections = "\n\n".join(render_section(section, catalog) for section in data["sections"])
    limited = sum(item["group"] == "vendor-limited" for item in catalog.values())
    unlimited = sum(item["group"] == "vendor-unlimited" for item in catalog.values())
    drops = sum(item["group"] == "companion-drops" for item in catalog.values())
    seasonal = sum(bool(item["season"]) for item in catalog.values())
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Companions, Mounts &amp; Accessories AH Price Guide — WotLK 3.3.5 Low Pop</title>
  <link rel="icon" href="../assets/brand/hellscream-server-logo.ico" sizes="any">
  <link rel="icon" type="image/png" href="../assets/brand/hellscream-server-logo-32.png" sizes="32x32">
  <link rel="apple-touch-icon" href="../assets/brand/hellscream-server-logo-180.png">
  <link rel="stylesheet" href="../assets/style.css?v={ASSET_VERSION}">
  <link rel="stylesheet" href="../assets/ah-guide-icons.css?v={ASSET_VERSION}">
  <script>const whTooltips={{colorLinks:false,iconizeLinks:false,renameLinks:false}};</script>
  <script src="https://wow.zamimg.com/js/tooltips.js" defer></script>
</head>
<body data-guide-section="auction-house" data-ah-guide="collectibles" data-ah-root="../">
<div class="wrap" id="top">
<!-- AH_SHARED_NAV_START -->
<nav class="site-nav ah-guide-nav" aria-label="Guide navigation">
  <a class="guide-hub-link" href="../index.html">Guide Hub</a>
  <a class="ah-hub-link" href="../auction-house.html">AH Hub</a>
</nav>
<!-- AH_SHARED_NAV_END -->
<!-- AH_GUIDE_UX_START -->
<header class="ah-guide-hero">
  <div class="ah-guide-heading">
    <img class="ah-guide-page-icon" src="../assets/ah-guide-icons/companions-mounts-accessories.svg" width="64" height="64" alt="">
    <div class="ah-guide-heading-copy">
      <span class="ah-guide-eyebrow">WotLK 3.3.5 · Auction House</span>
      <h1>Companions, Mounts &amp; Accessories</h1>
      <p class="sub">Verified tradeable pets, mounts, vanity accessories, vendor arbitrage, farmed drops, and separately organized seasonal markets.</p>
    </div>
  </div>
</header>

<section class="common ah-search-section ah-guide-search-section" aria-label="Auction House lookup">
  <div class="ah-search-heading"><span><span class="ah-search-eyebrow">Search every AH guide</span><span class="ah-search-count" id="ah-search-count"></span></span></div>
  <label class="visually-hidden" for="ah-search-input">Search by Auction House item name</label>
  <div class="ah-search-input-wrap"><input id="ah-search-input" class="ah-search-input" type="search" placeholder="Try Wood Frog Box, Spectral Tiger, or Snowman Kit…" autocomplete="off" autocapitalize="off" spellcheck="false" aria-describedby="ah-search-status" aria-controls="ah-search-results"></div>
  <nav class="ah-guide-major-nav" data-ah-major-nav aria-label="Jump to a major category"></nav>
  <p class="ah-search-status" id="ah-search-status" role="status" aria-live="polite" hidden></p>
  <ol class="ah-search-results" id="ah-search-results" hidden></ol>
</section>

<details class="common ah-guide-notes">
  <summary><span>Pricing notes &amp; legend</span><span class="ah-guide-notes-hint">Read before posting</span></summary>
  <div class="ah-guide-notes-content">
<!-- AH_GUIDE_NOTES_CONTENT_START -->
<div class="note"><strong>Vendor arbitrage:</strong> Buy from the named vendor and resell for convenience. Unlimited stock and true limited stock are separate because limited rows have verified stock caps and restock timers. Token and reputation vendors are separate again because their exact currency cost has no deterministic gold conversion.</div>
<div class="note"><strong>Collector markets:</strong> Most pets, mounts, and vanity rewards sell slowly. Post one at a time. An empty AH does not prove the High band, especially for promotional and Shadowmourne rewards.</div>
<div class="legend"><span class="pill p-quick">Quick</span><span class="pill p-bid">Target Bid</span><span class="pill p-target">Target Buyout</span><span class="pill p-watch">High / scarce</span></div>
<!-- AH_BASELINE_NOTE_START -->
<aside class="note ah-baseline-note"><strong>* Evidence Pricing:</strong> Exact vendor cost, stock, restock, token quantity, tradeability, loot route, and recipe floor are acquisition facts. Qualified completed sales take precedence; otherwise fixed Hellscream acquisition-cohort anchors and cross-server relative rank provide clearly labeled fallback bands. Active listings show competition only and never set or raise guide prices.</aside>
<!-- AH_BASELINE_NOTE_END -->
<!-- AH_GUIDE_NOTES_CONTENT_END -->
  </div>
</details>
<!-- AH_GUIDE_UX_END -->

<section class="common">
  <h2 class="ah-category-heading">What is covered<a class="ah-back-to-top" href="#top" aria-label="Back to top">↑ Top</a></h2>
  <div class="best-grid ah-summary-grid">
    <div class="best-card ah-summary-card"><h3>Vendor arbitrage</h3><p><strong>{unlimited}</strong> unlimited coin-vendor rows, <strong>{limited}</strong> true limited-stock rows, and a separate token/reputation section.</p></div>
    <div class="best-card ah-summary-card"><h3>Farmed &amp; crafted</h3><p><strong>{drops}</strong> pinned companion drops plus exact Engineering and Tailoring recipe floors.</p></div>
    <div class="best-card ah-summary-card"><h3>Rare rewards</h3><p>Verified quest companions, Landro's Gift Box mounts, and the tradeable Shadowmourne reward family.</p></div>
    <div class="best-card ah-summary-card"><h3>Season by season</h3><p><strong>{seasonal}</strong> event rows, with every holiday in its own section and explicit empty in-scope sections.</p></div>
  </div>
</section>

{sections}

<section class="common">
  <h2 class="ah-category-heading">Excluded and pending verification<a class="ah-back-to-top" href="#top" aria-label="Back to top">↑ Top</a></h2>
  <p class="small">The technically tradeable Magic Rooster Egg, Wooly White Rhino, and Blazing Hippogryph have no pinned acquisition route in the audited base data and remain unpriced until Hellscream availability is proven. BoP and temporary examples—including Fetch Ball, pet grooming items, temporary broom mounts, The Horseman's Reins, and Big Love Rocket—cannot be listed and stay out of the tables.</p>
</section>

<section class="common">
  <h2 class="ah-category-heading">Sources<a class="ah-back-to-top" href="#top" aria-label="Back to top">↑ Top</a></h2>
  <ul>
    <li><a href="https://github.com/azerothcore/azerothcore-wotlk/tree/e0fe11ba46b885a01e4a4038001e0055822cc7ba/data/sql/base/db_world">Pinned AzerothCore WotLK world data</a>: item templates, vendors, quests, creatures, game objects, and loot routes.</li>
    <li><a href="https://wotlkdb.com/">WotLKDB 3.3.5a</a>: exact Engineering and Tailoring spell reagents cross-checked on 2026-08-10.</li>
    <li><a href="../docs/ah-collectible-pricing-review.md">Saved Evidence Pricing review</a>: completed-sale coverage, fixed anchors, comparison coverage, and model limits.</li>
  </ul>
</section>

<section class="common"><h2 class="ah-category-heading">Disclaimer<a class="ah-back-to-top" href="#top" aria-label="Back to top">↑ Top</a></h2><p class="small">These are evidence-labeled starting bands for the Hellscream / Garrosh low-population economy, not live Auction House prices. Confirm the exact item and tradeable state before posting.</p></section>

<footer>WotLK 3.3.5 Companions, Mounts &amp; Accessories AH Guide • Hellscream / Garrosh • Created by Valdora • Updated {date.today().isoformat()}</footer>
</div>
<!-- AH_GUIDE_SCRIPTS_START -->
<script src="../assets/ah-search-index.js?v={ASSET_VERSION}" defer></script>
<script src="../assets/ah-guide-navigation-data.js?v={ASSET_VERSION}" defer></script>
<script src="../assets/ah-guide-navigation.js?v={ASSET_VERSION}" defer></script>
<script src="../assets/ah-search.js?v={ASSET_VERSION}" defer></script>
<!-- AH_GUIDE_SCRIPTS_END -->
</body>
</html>
'''


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    data = load(DATA_PATH)
    audit = load(AUDIT_PATH)
    expected = canonical_guide_ux(render_page(data, audit))
    if args.check:
        if not OUTPUT_PATH.is_file() or OUTPUT_PATH.read_text(encoding="utf-8") != expected:
            print(f"Stale collectible guide: {OUTPUT_PATH.relative_to(ROOT)}", file=sys.stderr)
            return 1
        print(f"Collectible guide is current: {len(data['catalog'])} priced rows.")
        return 0
    OUTPUT_PATH.write_text(expected, encoding="utf-8", newline="\n")
    print(f"Rendered collectible guide with {len(data['catalog'])} priced rows and {len(data['sections'])} market sections.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
