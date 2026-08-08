#!/usr/bin/env python3
"""Render the audited Phase 3 Turn-in catalog and recipe audit notes."""

from __future__ import annotations

import argparse
import html
import importlib.util
import json
import re
import unicodedata
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
GUIDES_DIR = ROOT / "guides"
TURN_IN_GUIDE = GUIDES_DIR / "drop-turn-in-quest-page-items-ah-price-guide.html"
RECIPE_GUIDE = GUIDES_DIR / "gear-pattern-drops-ah-price-guide.html"
TURN_IN_CATALOG = ROOT / "data" / "ah-turn-in-catalog.json"
TURN_IN_EVIDENCE = ROOT / "data" / "ah-turn-in-price-evidence.json"
RECIPE_AUDIT = ROOT / "data" / "ah-recipe-drop-audit.json"
RECIPE_EVIDENCE = ROOT / "data" / "ah-recipe-drop-price-evidence.json"
SHARED_RENDERER = ROOT / "scripts" / "render-ah-shared-sections.py"
TODAY = "2026-08-08"
FIXED_TURN_IN_SECTION = "Darkmoon Faire drop turn-ins only"
DEMAND_CLASSES = {
    "Very High": "vh",
    "High": "hi",
    "Med-High": "hi",
    "Med": "med",
    "Medium": "med",
    "Low-Med": "low",
    "Low": "low",
}


def load_renderer():
    spec = importlib.util.spec_from_file_location("ah_phase3_renderer", SHARED_RENDERER)
    if spec is None or spec.loader is None:
        raise RuntimeError("Could not load shared AH renderer")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


RENDER = load_renderer()


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def normalize(value: str) -> str:
    value = "".join(
        char
        for char in unicodedata.normalize("NFKD", value)
        if not unicodedata.combining(char)
    )
    value = value.casefold().replace("’", "").replace("'", "").replace("&", " and ")
    return " ".join(re.sub(r"[^a-z0-9]+", " ", value).split())


def demand_class(value: str) -> str:
    return DEMAND_CLASSES.get(value, "med")


def render_turn_in_row(record: dict, evidence: dict) -> str:
    prices = evidence["proposal"]["proposed_band"]
    stack = html.escape(record["recommended_stack"]) if record["recommended_stack"] else "—"
    note = html.escape(record["restriction"], quote=False)
    return (
        '<tr><td data-column="item" data-label="Item">'
        f'<strong class="q-{record["quality"]}">{html.escape(record["name"])}</strong>'
        f'<div class="mini">{html.escape(record["detail"])}</div></td>'
        '<td data-column="target" data-label="Target Price">'
        f'{RENDER.render_price_pair("target", prices["target"])}</td>'
        '<td data-column="quick" data-label="Quick Price">'
        f'{RENDER.render_price_pair("quick", prices["quick"])}</td>'
        '<td data-column="high" data-label="High / Scarce">'
        f'{RENDER.render_price_pair("high", prices["high"])}</td>'
        f'<td data-column="stack" data-label="Stack Size">{stack}</td>'
        '<td data-column="demand" data-label="Demand">'
        f'<span class="demand {demand_class(record["demand"])}">{html.escape(record["demand"])}</span></td>'
        f'<td data-column="notes" data-label="Use / Selling Notes">{note}</td></tr>'
    )


def replace_turn_in_sections(source: str, catalog: dict, evidence: dict) -> str:
    section_pattern = re.compile(r'<section class="common">.*?</section>', re.DOTALL)
    heading_pattern = re.compile(r'<h2[^>]*>(.*?)</h2>', re.DOTALL)
    tbody_pattern = re.compile(r'(<tbody>).*?(</tbody>)', re.DOTALL)
    section_items = {
        section["title"]: [catalog["items"][str(item_id)] for item_id in section["items"]]
        for section in catalog["sections"]
    }

    def replace_section(match: re.Match[str]) -> str:
        block = match.group(0)
        heading = heading_pattern.search(block)
        if not heading:
            return block
        title = html.unescape(re.sub(r"<[^>]+>", "", heading.group(1))).replace("↑ Top", "").strip()
        items = section_items.get(title)
        if not items or not tbody_pattern.search(block):
            return block
        if title != FIXED_TURN_IN_SECTION:
            items = sorted(
                items,
                key=lambda record: (
                    -evidence["items"][str(record["item_id"])]["proposal"]["proposed_band"]["target"],
                    record["name"],
                ),
            )
        rows = "\n".join(
            render_turn_in_row(record, evidence["items"][str(record["item_id"])])
            for record in items
        )
        return tbody_pattern.sub(r"\1" + rows + r"\2", block, count=1)

    return section_pattern.sub(replace_section, source)


def turn_in_copy(source: str) -> str:
    source = re.sub(
        r'<section class="common"><h2 class="ah-category-heading">Timbermaw Hold drops.*?</section>\s*',
        "",
        source,
        count=1,
        flags=re.DOTALL,
    )
    source = source.replace(
        "Reputation turn-ins, Darkmoon Faire drops, quest pages, and other farmable quest-completion items.",
        "74 exact tradeable reputation, Darkmoon Faire, and quest-page items with audited turn-in quantities and stack limits.",
    )
    source = source.replace(
        '<div class="note" style="border-left-color:var(--purple);background:rgba(202,167,255,.08);color:#eadcff;"><strong>Grouping rule:</strong> Similar drops are lumped together when they behave like the same market. Split them only when one item or page is clearly scarce.</div>',
        '<div class="note" style="border-left-color:var(--purple);background:rgba(202,167,255,.08);color:#eadcff;"><strong>Exact-item rule:</strong> Every priced row is one real auctionable item. Uncatalogued Species, Deadwood Headdress Feather, and Winterfall Spirit Beads were removed because the pinned 3.3.5 records bind them on pickup.</div>',
    )
    source = source.replace(
        '<aside class="note ah-baseline-note"><strong>* Pricing baseline:</strong> These bands are frozen reference values, not live-AH medians. Active listings show competition only and never set or raise guide prices. Use listings to choose timing and stack size; change the baseline only from qualified completed sales, exact vendor costs, deterministic conversions, or measured acquisition evidence.</aside>',
        '<aside class="note ah-baseline-note"><strong>* Evidence Pricing:</strong> Exact quest quantities, stack limits, event or standing restrictions, and pinned tradeability are use facts—not automatic sale values. Qualified completed sales take precedence; otherwise fixed Hellscream cohort anchors and gold-normalized cross-server relative rank provide fallback bands. Active listings show competition only and never set or raise guide prices.</aside>',
    )
    source = source.replace(
        '<li><strong class="q-common">Timbermaw beads / feathers</strong><div class="mini">Repeatable Timbermaw rep drops.</div></li>',
        '<li><strong class="q-common">Argent Dawn parts</strong><div class="mini">Exact 30-item Light\'s Hope turn-ins.</div></li>',
    )
    source = source.replace(
        '<li><a href="https://www.wowhead.com/classic/guide/timbermaw-hold-reputation-wow-classic">Wowhead: Timbermaw Hold reputation guide</a></li>\n',
        "",
    )
    source = source.replace(
        "<strong>Check tradeability first.</strong> Some old turn-in items require a quest state, reputation range, active event, commission/trinket, or specific server behavior. Soulbound, quest-only, non-tradeable, and maker-only items should not be treated as AH goods.",
        "<strong>Check the buyer's unlock first.</strong> The rows are tradeable, but many are useful only during an active event, within a reputation range, after a quest unlock, or as one missing page. The Stack Size column follows the true maximum and likely turn-in purchase quantity; non-stackable Shredder pages show no stack recommendation.",
    )
    return source


def recipe_note(record: dict) -> tuple[str, str]:
    skill = f'{record["profession"]} {record["required_skill_rank"]}'
    market = record["market"].rstrip(".")
    if record["item_id"] == 45912:
        return (
            record["guide_source"],
            "Requires Inscription 425. Consumes the book to learn one eligible Northrend glyph recipe; the 25g Target preserves the user-reported average-sale estimate recorded 2026-08-03.",
        )
    if record["vendor_sources"]:
        vendor_parts = []
        for vendor in record["vendor_sources"]:
            minutes = vendor["restock_seconds"] // 60
            hours, minutes = divmod(minutes, 60)
            restock = f"{hours}h {minutes}m" if minutes else f"{hours}h"
            vendor_parts.append(
                f'{vendor["name"]} (stock {vendor["max_count"]}; {restock} restock)'
            )
        vendors = "; ".join(vendor_parts)
        return (
            f"Limited vendor: {vendors}",
            f"Requires {skill}; unlocks {market}. Exact vendor cost anchors the band, so AH value is a convenience/restock premium—not drop scarcity.",
        )
    source_rows = len(record["loot_sources"])
    return (
        f'{record["guide_source"]} • {source_rows} pinned loot path{"s" if source_rows != 1 else ""}',
        f"Requires {skill}; unlocks {market}. Buyer pool is limited to that profession and recipe need.",
    )


def update_recipe_rows(source: str, audit: dict) -> str:
    by_name = {normalize(record["name"]): record for record in audit["items"].values()}
    row_pattern = re.compile(r"<tr>.*?</tr>", re.DOTALL)
    name_pattern = re.compile(
        r'(<td[^>]*data-column="item"[^>]*>.*?<strong[^>]*>)(.*?)(</strong>)',
        re.DOTALL,
    )
    source_cell = re.compile(
        r'(<td[^>]*data-column="source"[^>]*>).*?(</td>)', re.DOTALL
    )
    note_cell = re.compile(
        r'(<td[^>]*data-column="notes"[^>]*>).*?(</td>)', re.DOTALL
    )

    def replace_row(match: re.Match[str]) -> str:
        row = match.group(0)
        name_match = name_pattern.search(row)
        if not name_match:
            return row
        name = html.unescape(re.sub(r"<[^>]+>", "", name_match.group(2))).strip()
        record = by_name.get(normalize(name))
        if not record:
            return row
        source_text, note_text = recipe_note(record)
        row = source_cell.sub(
            lambda cell: cell.group(1) + html.escape(source_text, quote=False) + cell.group(2),
            row,
            count=1,
        )
        row = note_cell.sub(
            lambda cell: cell.group(1) + html.escape(note_text, quote=False) + cell.group(2),
            row,
            count=1,
        )
        return row

    return row_pattern.sub(replace_row, source)


def recipe_copy(source: str) -> str:
    source = source.replace(
        '<div class="prof-note ah-info-panel ah-info-panel--accent"><strong>Guide focus:</strong> AH-priceable recipe and pattern drops across gear, utility, consumable, and miscellaneous unlock markets. Trainer, ordinary vendor, reputation, BoP, and research-only recipes remain outside this guide.</div>',
        '<div class="prof-note ah-info-panel ah-info-panel--accent"><strong>Guide focus:</strong> 90 tradeable profession recipe items. Eighty-five have pinned loot paths; five limited-vendor recipes are retained and explicitly labeled because their AH value is convenience and restock access, not drop scarcity. Trainer, unlimited ordinary-vendor, reputation, BoP, and research-only recipes remain outside this guide.</div>',
    )
    source = source.replace(
        '<aside class="note ah-baseline-note"><strong>* Pricing baseline:</strong> These bands are frozen reference values, not live-AH medians. Active listings show competition only and never set or raise guide prices. Use listings to choose timing and stack size; change the baseline only from qualified completed sales, exact vendor costs, deterministic conversions, or measured acquisition evidence.</aside>',
        '<aside class="note ah-baseline-note"><strong>* Evidence Pricing:</strong> Profession skill, learned-output value, pinned loot paths, recipe rarity, and exact limited-vendor cost are reviewed separately from sale evidence. Qualified completed sales take precedence; fixed Hellscream cohort anchors and gold-normalized cross-server relative rank provide fallback bands. Active listings show competition only and never set or raise guide prices.</aside>',
    )
    source = source.replace(
        '<div class="pattern-card ah-summary-card"><h3>Blacksmithing</h3><div class="big">15</div>',
        '<div class="pattern-card ah-summary-card"><h3>Blacksmithing</h3><div class="big">11</div>',
    )
    return source


def footer(source: str) -> str:
    return re.sub(r"Updated \d{4}-\d{2}-\d{2}</footer>", f"Updated {TODAY}</footer>", source, count=1)


def expected_outputs() -> dict[Path, str]:
    turn_catalog = load(TURN_IN_CATALOG)
    turn_evidence = load(TURN_IN_EVIDENCE)
    recipe_audit = load(RECIPE_AUDIT)
    recipe_evidence = load(RECIPE_EVIDENCE)
    if len(turn_catalog["items"]) != 74 or len(turn_evidence["items"]) != 74:
        raise ValueError("Turn-in render inputs do not cover 74 items")
    if len(recipe_audit["items"]) != 90 or len(recipe_evidence["items"]) != 90:
        raise ValueError("Recipe render inputs do not cover 90 items")
    turn_source = TURN_IN_GUIDE.read_text(encoding="utf-8")
    recipe_source = RECIPE_GUIDE.read_text(encoding="utf-8")
    turn_source = footer(replace_turn_in_sections(turn_in_copy(turn_source), turn_catalog, turn_evidence))
    recipe_source = footer(update_recipe_rows(recipe_copy(recipe_source), recipe_audit))
    return {TURN_IN_GUIDE: turn_source, RECIPE_GUIDE: recipe_source}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    stale = []
    for path, expected in expected_outputs().items():
        current = path.read_text(encoding="utf-8")
        if current == expected:
            continue
        if args.check:
            stale.append(path.name)
        else:
            path.write_text(expected, encoding="utf-8", newline="\n")
            print(f"Updated {path.name}")
    if stale:
        raise ValueError("Phase 3 static guide render is stale: " + ", ".join(stale))
    if not stale:
        print("Phase 3 Turn-in rows and recipe notes are current.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
