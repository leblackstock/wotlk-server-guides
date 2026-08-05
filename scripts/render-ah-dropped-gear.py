#!/usr/bin/env python3
"""Render the audited BoE dropped-gear guide sections."""

from __future__ import annotations

import argparse
import html
import json
import re
import sys
from collections import Counter
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
GUIDES_DIR = ROOT / "guides"
DATA_PATH = ROOT / "data" / "ah-dropped-gear.json"
BASELINE_PATH = ROOT / "data" / "ah-price-baselines.json"
BLOCK = re.compile(
    r"<!-- AH_DROPPED_GEAR_SECTIONS_START -->.*?<!-- AH_DROPPED_GEAR_SECTIONS_END -->",
    re.DOTALL,
)
BASELINE_NOTE = re.compile(
    r"<!-- AH_BASELINE_NOTE_START -->.*?<!-- AH_BASELINE_NOTE_END -->",
    re.DOTALL,
)
PRICING_STATUS = re.compile(
    r'<div class="rarity-audit ah-info-panel ah-info-panel--rare"><strong>Pricing status:</strong>.*?</div>'
)
STARTER_BASELINE_NOTE = """<!-- AH_BASELINE_NOTE_START -->
<aside class="note ah-baseline-note"><strong>* BoE pricing note:</strong> Target is the recommended opening listing, Quick is for a faster sale, and High / Scarce is for patient one-at-a-time posting when supply is genuinely thin. These are reviewed starting values for Hellscream's low-pop market—not guaranteed sale prices. Most rows are modeled estimates; only a few have local completed-sale evidence. Active listings show competition only and never set or raise guide prices. Do not raise a price merely because the AH is empty or one competing auction is expensive. Record completed sales and revise from actual Hellscream results.</aside>
<!-- AH_BASELINE_NOTE_END -->"""
FOOTER_DATE = re.compile(r"(Updated )\d{4}-\d{2}-\d{2}(</footer>)")


def display_money_copper(copper: int) -> int:
    if copper < 0:
        raise ValueError("Money cannot be negative")
    if copper >= 10_000:
        return ((copper + 50) // 100) * 100
    return copper


def format_money(copper: int) -> str:
    copper = display_money_copper(copper)
    gold, remainder = divmod(copper, 10_000)
    silver, copper = divmod(remainder, 100)
    parts: list[str] = []
    if gold:
        parts.append(f"{gold:,}g")
    if silver:
        parts.append(f"{silver}s")
    if copper or not parts:
        parts.append(f"{copper}c")
    return " ".join(parts)


def target_bid(value: int) -> int:
    return max(1, round(value * 0.85))


def render_price_pair(kind: str, value: int) -> str:
    return (
        f'<div class="pricepair {kind}">\n'
        f'<div><span class="label">Bid</span><span class="bid">{format_money(target_bid(value))}</span></div>\n'
        f'<div><span class="label">Buyout</span><span class="buyout">{format_money(value)}</span></div>\n'
        "</div>"
    )


def demand_class(value: str) -> str:
    return {
        "Very High": "vh",
        "High": "hi",
        "Med-High": "hi",
        "Medium": "med",
        "Low-Med": "low",
    }.get(value, "low")


def category_heading(title: str) -> str:
    return (
        f'<h2 class="ah-category-heading">{html.escape(title)}'
        '<a class="ah-back-to-top" href="#top" aria-label="Back to top">↑ Top</a></h2>'
    )


def render_row(key: str, item: dict, baseline: dict) -> str:
    price = baseline[str(item["item_id"])]
    quality = html.escape(item["quality"])
    quality_label = "Epic" if item["quality"] == "epic" else "Rare"
    metadata = (
        f'{quality_label} · Req {item["required_level"]} · '
        f'iLvl {item["item_level"]} · {item["slot"]}'
    )
    return (
        f'<tr data-dropped-gear-key="{html.escape(key)}" data-market-source="dropped">'
        f'<td data-column="item" data-label="Item"><strong class="q-{quality}">{html.escape(item["name"])}</strong>'
        f'<div class="mini">{html.escape(metadata)}</div></td>'
        f'<td data-column="target" data-label="Target Price">{render_price_pair("target", int(price["target"]))}</td>'
        f'<td data-column="quick" data-label="Quick Price">{render_price_pair("quick", int(price["quick"]))}</td>'
        f'<td data-column="high" data-label="High / Scarce">{render_price_pair("high", int(price["high"]))}</td>'
        f'<td data-column="notes" data-label="Use / Selling Notes">{html.escape(item["notes"])}</td>'
        f'<td data-column="demand" data-label="Demand"><span class="demand {demand_class(item["demand"])}">{html.escape(item["demand"])}</span></td>'
        f'<td data-column="market" data-label="Market">{html.escape(item["buyer"])}</td>'
        f'<td data-column="source" data-label="Source">{html.escape(item["source"])}</td>'
        "</tr>"
    )


def render_sections(guide_id: str, guide: dict, catalog: dict, baseline: dict) -> str:
    guide_items = [item for item in catalog.values() if item["guide_id"] == guide_id]
    if not guide_items:
        raise ValueError(f"{guide_id}: dropped-gear catalog is empty")
    by_section: dict[str, list[tuple[str, dict]]] = {}
    for section in guide["sections"]:
        section_items = [
            (key, item)
            for key, item in catalog.items()
            if item["guide_id"] == guide_id and item["section_id"] == section["id"]
        ]
        if not section_items:
            raise ValueError(f"{guide_id}: empty dropped-gear section {section['id']}")
        section_items.sort(
            key=lambda pair: (
                -int(baseline[str(pair[1]["item_id"])]["target"]),
                pair[1]["name"].casefold(),
            )
        )
        by_section[section["id"]] = section_items

    sections = []
    for section in guide["sections"]:
        rows = "\n".join(
            render_row(key, item, baseline)
            for key, item in by_section[section["id"]]
        )
        sections.append(
            f'<section class="common dropped-gear-section" data-dropped-gear-section="{html.escape(section["id"])}">'
            f'{category_heading(section["title"])}'
            '<div class="table-wrap"><table class="ah-market-table ah-market-table--extended" data-table-family="market">'
            '<thead><tr><th data-column="item">Item</th><th data-column="target">Target Price</th>'
            '<th data-column="quick">Quick Price</th><th data-column="high">High / Scarce</th>'
            '<th data-column="notes">Use / Selling Notes</th><th data-column="demand">Demand</th>'
            '<th data-column="market">Market</th><th data-column="source">Source</th></tr></thead>'
            f'<tbody>{rows}</tbody></table></div></section>'
        )
    return (
        "<!-- AH_DROPPED_GEAR_SECTIONS_START -->\n"
        + "\n".join(sections)
        + "\n<!-- AH_DROPPED_GEAR_SECTIONS_END -->"
    )


def transform(source: str, guide_id: str, guide: dict, catalog: dict, baseline: dict) -> str:
    block = render_sections(guide_id, guide, catalog, baseline)
    if not BLOCK.search(source):
        raise ValueError(f"{guide['file']}: missing dropped-gear section markers")
    if not BASELINE_NOTE.search(source):
        raise ValueError(f"{guide['file']}: missing pricing-baseline note markers")
    if not PRICING_STATUS.search(source):
        raise ValueError(f"{guide['file']}: missing pricing-status panel")
    pricing_status = (
        '<div class="rarity-audit ah-info-panel ah-info-panel--rare">'
        '<strong>Pricing status:</strong> Use Target for the first listing, Quick when you want a '
        'faster sale, and High / Scarce only when the item is genuinely scarce and you are willing '
        'to wait. Post one copy at a time and record whether it sells.</div>'
    )
    source = PRICING_STATUS.sub(pricing_status, source, count=1)
    source = BASELINE_NOTE.sub(STARTER_BASELINE_NOTE, source, count=1)
    return BLOCK.sub(block, source, count=1)


def update_footer_date(source: str) -> str:
    updated, count = FOOTER_DATE.subn(
        rf"\g<1>{date.today().isoformat()}\g<2>",
        source,
        count=1,
    )
    if count != 1:
        raise ValueError("Dropped-gear guide is missing its Updated footer date")
    return updated


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Fail if rendered guide sections are stale")
    args = parser.parse_args()
    data = json.loads(DATA_PATH.read_text(encoding="utf-8"))
    baseline = json.loads(BASELINE_PATH.read_text(encoding="utf-8"))["items"]
    stale: list[str] = []
    updates: list[tuple[Path, str]] = []
    for guide_id, guide in data["guides"].items():
        path = GUIDES_DIR / guide["file"]
        if not path.is_file():
            raise FileNotFoundError(f"Missing dropped-gear guide: {path.relative_to(ROOT)}")
        source = path.read_text(encoding="utf-8")
        expected = transform(source, guide_id, guide, data["catalog"], baseline)
        if expected != source:
            if not args.check:
                expected = update_footer_date(expected)
            stale.append(str(path.relative_to(ROOT)))
            updates.append((path, expected))
    if args.check:
        if stale:
            print("Dropped-gear guides are stale: " + ", ".join(stale), file=sys.stderr)
            return 1
        print("Dropped-gear guide sections are current.")
        return 0
    for path, source in updates:
        path.write_text(source, encoding="utf-8", newline="\n")
    counts = Counter(item["guide_id"] for item in data["catalog"].values())
    print(
        "Rendered dropped-gear guides: "
        f"{counts['level-80-boe-epics']} level-80 rows and "
        f"{counts['sought-after-world-drops']} world-drop rows."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
