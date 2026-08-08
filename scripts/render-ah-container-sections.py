#!/usr/bin/env python3
"""Render verified dropped and quest-reward container sections into AH guides."""

from __future__ import annotations

import argparse
import html
import json
import re
import sys
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
GUIDES_DIR = ROOT / "guides"
DATA_PATH = ROOT / "data" / "ah-container-sections.json"
FOOTER_DATE = re.compile(r"(Updated )\d{4}-\d{2}-\d{2}(</footer>)")


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def format_money(copper: int) -> str:
    if copper >= 10_000:
        copper = ((copper + 50) // 100) * 100
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


def target_bid(copper: int) -> int:
    return max(1, round(copper * 0.85))


def render_price_pair(kind: str, copper: int) -> str:
    return (
        f'<div class="pricepair {kind}">'
        f'<div><span class="label">Bid</span><span class="bid">'
        f'{format_money(target_bid(copper))}</span></div>'
        f'<div><span class="label">Buyout</span><span class="buyout">'
        f'{format_money(copper)}</span></div></div>'
    )


def render_row(key: str, item: dict) -> str:
    return (
        f'<tr data-container-key="{html.escape(key)}" '
        f'data-market-source="{html.escape(item["primary_source"])}">'
        '<td data-column="item" data-label="Item">'
        f'<strong class="q-{html.escape(item["quality"])}">'
        f'{html.escape(item["name"])}</strong>'
        f'<div class="mini">{html.escape(item["detail"])}</div></td>'
        '<td data-column="target" data-label="Target Price">'
        f'{render_price_pair("target", int(item["target_copper"]))}</td>'
        '<td data-column="quick" data-label="Quick Price">'
        f'{render_price_pair("quick", int(item["quick_copper"]))}</td>'
        '<td data-column="high" data-label="High / Scarce">'
        f'{render_price_pair("high", int(item["high_copper"]))}</td>'
        '<td data-column="notes" data-label="Use / Selling Notes">'
        f'{html.escape(item["notes"])}</td>'
        '<td data-column="demand" data-label="Demand">'
        f'<span class="demand {html.escape(item["demand_class"])}">'
        f'{html.escape(item["demand"])}</span></td>'
        f'<td data-column="market" data-label="Market">{html.escape(item["buyer"])}</td>'
        f'<td data-column="source" data-label="Source">{html.escape(item["source"])}</td>'
        "</tr>"
    )


def render_section(section: dict, catalog: dict) -> str:
    items = [(key, catalog[key]) for key in section["items"]]
    items.sort(
        key=lambda pair: (-int(pair[1]["target_copper"]), pair[1]["name"].casefold())
    )
    rows = "\n".join(render_row(key, item) for key, item in items)
    return (
        f'<section class="common container-market-section" '
        f'data-container-section="{html.escape(section["id"])}">'
        f'<h2 class="ah-category-heading">{html.escape(section["title"])}'
        '<a class="ah-back-to-top" href="#top" aria-label="Back to top">↑ Top</a></h2>'
        f'<p class="small"><strong>Prices are per container.</strong> '
        f'{html.escape(section["description"])}</p>'
        '<div class="table-wrap"><table class="ah-market-table '
        'ah-market-table--extended" data-table-family="market"><thead><tr>'
        '<th data-column="item">Item</th><th data-column="target">Target Price</th>'
        '<th data-column="quick">Quick Price</th><th data-column="high">High / Scarce</th>'
        '<th data-column="notes">Use / Selling Notes</th><th data-column="demand">Demand</th>'
        '<th data-column="market">Market</th><th data-column="source">Source</th>'
        f'</tr></thead><tbody>{rows}</tbody></table></div></section>'
    )


def render_block(guide: dict, catalog: dict) -> str:
    marker = guide["marker"]
    sections = "\n".join(
        render_section(section, catalog) for section in guide["sections"]
    )
    return f"<!-- {marker}_START -->\n{sections}\n<!-- {marker}_END -->"


def transform(source: str, filename: str, guide: dict, catalog: dict) -> str:
    marker = guide["marker"]
    block = render_block(guide, catalog)
    pattern = re.compile(
        rf"<!-- {re.escape(marker)}_START -->.*?<!-- {re.escape(marker)}_END -->",
        re.DOTALL,
    )
    if pattern.search(source):
        source = pattern.sub(block, source, count=1)
    elif filename == "sought-after-world-drops-ah-price-guide.html":
        insertion = "<!-- AH_DROPPED_GEAR_SECTIONS_END -->"
        if source.count(insertion) != 1:
            raise ValueError(f"{filename}: missing dropped-gear insertion marker")
        source = source.replace(insertion, insertion + "\n" + block, 1)
    elif filename == "drop-turn-in-quest-page-items-ah-price-guide.html":
        if source.count("<footer>") != 1:
            raise ValueError(f"{filename}: expected one container insertion point")
        source = source.replace("<footer>", block + "\n<footer>", 1)
    else:
        raise ValueError(f"{filename}: no container-section insertion rule")

    if filename == "sought-after-world-drops-ah-price-guide.html":
        source = source.replace(
            "Pre-level-80 epic BoEs, twink-bracket rares, and fixed-stat Northrend leveling drops with real buyer use.",
            "Pre-level-80 epic BoEs, twink-bracket rares, fixed-stat Northrend leveling drops, and verified Classic dropped bags.",
        )
        source = source.replace(
            "This is a curated pre-80 guide: epic BoE drops, fixed-stat rare gear at established twink caps, and fixed-stat Northrend 71–79 drops. Random-suffix greens are intentionally excluded.",
            "This is a curated pre-80 guide: epic BoE drops, fixed-stat rare gear at established twink caps, fixed-stat Northrend 71–79 drops, and verified auctionable Classic containers. Random-suffix greens are intentionally excluded.",
        )
        source = source.replace(
            "Guide focus:</strong> Dropped equipment only. Crafted gear, recipes, materials, turn-ins, vendor gear, and BoP items remain in their existing guides or outside AH coverage.",
            "Guide focus:</strong> Dropped equipment plus verified dropped bags and containers. Crafted items, recipes, materials, turn-ins, vendor gear, and BoP items remain in their existing guides or outside AH coverage.",
        )
    else:
        source = source.replace(
            "74 exact tradeable reputation, Darkmoon Faire, and quest-page items with audited turn-in quantities and stack limits.",
            "75 exact tradeable reputation, Darkmoon Faire, quest-page, and quest-reward items with audited use and acquisition facts.",
        )
    return source


def update_footer(source: str) -> str:
    updated, count = FOOTER_DATE.subn(
        rf"\g<1>{date.today().isoformat()}\g<2>", source, count=1
    )
    if count != 1:
        raise ValueError("Container guide is missing its Updated footer date")
    return updated


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    data = load(DATA_PATH)
    catalog = data["catalog"]
    stale: list[str] = []
    updates: list[tuple[Path, str]] = []
    for filename, guide in data["guides"].items():
        path = GUIDES_DIR / filename
        source = path.read_text(encoding="utf-8")
        expected = transform(source, filename, guide, catalog)
        if expected == source:
            continue
        stale.append(str(path.relative_to(ROOT)))
        updates.append((path, update_footer(expected)))
    if args.check:
        if stale:
            print("Container guide sections are stale: " + ", ".join(stale), file=sys.stderr)
            return 1
        print("Container guide sections are current.")
        return 0
    for path, expected in updates:
        path.write_text(expected, encoding="utf-8", newline="\n")
    print(
        "Rendered container additions: "
        f"{sum(item['primary_source'] == 'drop' for item in catalog.values())} drops and "
        f"{sum(item['primary_source'] == 'quest-reward' for item in catalog.values())} quest reward."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
