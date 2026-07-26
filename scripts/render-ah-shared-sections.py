#!/usr/bin/env python3
"""Render canonical navigation, vendor, and crafted-market sections into AH guides."""

from __future__ import annotations

import argparse
import html
import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
GUIDES_DIR = ROOT / "guides"
VENDOR_DATA_PATH = ROOT / "data" / "ah-vendor-sections.json"
CRAFTED_DATA_PATH = ROOT / "data" / "ah-crafted-sections.json"
NAV_TEMPLATE_PATH = ROOT / "templates" / "ah-guide" / "navigation.html"
VENDOR_TEMPLATE_PATH = ROOT / "templates" / "ah-guide" / "vendor-convenience-section.html"
CRAFTED_TEMPLATE_PATH = ROOT / "templates" / "ah-guide" / "crafted-market-section.html"
AH_GUIDE_GLOB = "*ah-price-guide.html"

NAV_BLOCK = re.compile(
    r"(?:<!-- AH_SHARED_NAV_START -->\s*)?"
    r"<nav class=\"site-nav(?: ah-guide-nav)?\" aria-label=\"Guide navigation\">.*?</nav>"
    r"(?:\s*<!-- AH_SHARED_NAV_END -->)?",
    re.DOTALL,
)
VENDOR_BLOCK = re.compile(
    r"(?:<!-- AH_VENDOR_SECTION_START -->\s*)?"
    r"<section class=\"common vendor-compact\"(?: data-ah-template=\"[^\"]+\")?>.*?</section>"
    r"(?:\s*<!-- AH_VENDOR_SECTION_END -->)?",
    re.DOTALL,
)
CRAFTED_BLOCK = re.compile(
    r"<!-- AH_CRAFTED_SECTION_START -->\s*"
    r"<div class=\"ah-crafted-market\" data-ah-template=\"[^\"]+\">.*?</div>"
    r"\s*<!-- AH_CRAFTED_SECTION_END -->",
    re.DOTALL,
)
LEGACY_INSCRIPTION_CRAFTED_BLOCK = re.compile(
    r"<section class=\"common\"><h2>Darkmoon cards / decks</h2>.*?</section>\s*"
    r"<section class=\"common ref-compact\"><h2>Vellums</h2>.*?</section>",
    re.DOTALL,
)


def format_money(copper: int) -> str:
    if copper < 0:
        raise ValueError("Money cannot be negative")
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


def source_cost(item: dict) -> str:
    if item["source_type"] != "coin-vendor":
        return html.escape(item["source_cost_label"])

    cost = int(item["vendor_cost_copper"])
    count = int(item.get("vendor_buy_count", 1))
    if count <= 0 or cost % count:
        raise ValueError(f"Invalid vendor bundle for {item['name']}")
    if count == 1:
        return f"Vendor: {format_money(cost)} each"
    return (
        f"Vendor: {format_money(cost)} per {count} "
        f"({format_money(cost // count)} each)"
    )


def target_bid(target_copper: int) -> int:
    """Match the 85% target-bid convention used by the regular AH rows."""
    return max(1, round(target_copper * 0.85))


def render_vendor_row(key: str, item: dict) -> str:
    name = html.escape(item["name"])
    source_label = html.escape(item["source_label"])
    target_copper = int(item["target_copper"])
    bid = format_money(target_bid(target_copper))
    target = format_money(target_copper)
    stack = html.escape(item["stack"])
    notes = html.escape(item["notes"])
    cost = source_cost(item)
    return (
        f'        <tr data-vendor-key="{html.escape(key)}">\n'
        f'          <td data-column="item" data-label="Item">'
        f'<strong class="q-common">{name}</strong>'
        f'<div class="mini">{source_label}</div></td>\n'
        f'          <td data-column="target" data-label="Target Price">'
        f'<div class="pricepair target">\n'
        f'            <div><span class="label">Bid</span>'
        f'<span class="bid">{bid}</span></div>\n'
        f'            <div><span class="label">Buyout</span>'
        f'<span class="buyout">{target}</span></div>\n'
        f'          </div></td>\n'
        f'          <td data-column="stack" data-label="Stack Size">{stack}</td>\n'
        f'          <td data-column="demand" data-label="Demand">'
        f'<span class="demand low">Low</span></td>\n'
        f'          <td data-column="notes" data-label="Use / Selling Notes">'
        f'<strong>Source / cost:</strong> {cost}. {notes}</td>\n'
        f"        </tr>"
    )


def load_vendor_config() -> dict:
    config = json.loads(VENDOR_DATA_PATH.read_text(encoding="utf-8"))
    catalog = config.get("catalog", {})
    guides = config.get("guides", {})
    if not catalog or not guides:
        raise ValueError("Vendor data must define catalog and guides")

    used: set[str] = set()
    for filename, guide in guides.items():
        path = GUIDES_DIR / filename
        if not path.is_file():
            raise FileNotFoundError(f"Missing AH guide: {path.relative_to(ROOT)}")
        for key in guide.get("items", []):
            if key not in catalog:
                raise KeyError(f"{filename} references unknown vendor item: {key}")
            used.add(key)

    unused = sorted(set(catalog) - used)
    if unused:
        raise ValueError(f"Unused vendor catalog entries: {', '.join(unused)}")
    return config


def render_vendor_section(template: str, item_keys: list[str], catalog: dict) -> str:
    rows = "\n".join(render_vendor_row(key, catalog[key]) for key in item_keys)
    return template.replace("{{ROWS}}", rows)


def load_crafted_config() -> dict:
    config = json.loads(CRAFTED_DATA_PATH.read_text(encoding="utf-8"))
    catalog = config.get("catalog", {})
    profiles = config.get("price_profiles", {})
    guides = config.get("guides", {})
    defaults = config.get("catalog_defaults", {})
    if not catalog or not profiles or not guides:
        raise ValueError("Crafted data must define catalog, price_profiles, and guides")

    used: set[str] = set()
    item_ids: set[int] = set()
    for key, item in catalog.items():
        profile_key = item.get("profile")
        if profile_key not in profiles:
            raise KeyError(f"{key} references unknown crafted profile: {profile_key}")
        item_id = int(item["item_id"])
        if item_id <= 0 or item_id in item_ids:
            raise ValueError(f"{key}: invalid or duplicate crafted item ID {item_id}")
        item_ids.add(item_id)
        merged = defaults | profiles[profile_key] | item
        if not merged.get("crafted") or not merged.get("tradeable"):
            raise ValueError(f"{key}: crafted catalog items must be crafted and tradeable")
        if merged.get("binding") not in {"none", "boe"}:
            raise ValueError(f"{key}: BoP or unknown binding is not allowed")

    for filename, guide in guides.items():
        path = GUIDES_DIR / filename
        if not path.is_file():
            raise FileNotFoundError(f"Missing AH guide: {path.relative_to(ROOT)}")
        for section in guide.get("sections", []):
            for key in section.get("items", []):
                if key not in catalog:
                    raise KeyError(f"{filename} references unknown crafted item: {key}")
                if key in used:
                    raise ValueError(f"Crafted item is used more than once: {key}")
                used.add(key)

    unused = sorted(set(catalog) - used)
    if unused:
        raise ValueError(f"Unused crafted catalog entries: {', '.join(unused)}")
    return config


def render_price_pair(kind: str, buyout_copper: int) -> str:
    bid = format_money(target_bid(buyout_copper))
    buyout = format_money(buyout_copper)
    return (
        f'<div class="pricepair {kind}">\n'
        f'<div><span class="label">Bid</span><span class="bid">{bid}</span></div>\n'
        f'<div><span class="label">Buyout</span><span class="buyout">{buyout}</span></div>\n'
        f"</div>"
    )


def crafted_item(config: dict, key: str) -> dict:
    item = config["catalog"][key]
    return (
        config.get("catalog_defaults", {})
        | config["price_profiles"][item["profile"]]
        | item
    )


def render_crafted_row(config: dict, key: str) -> str:
    item = crafted_item(config, key)
    profession = html.escape(item["profession"])
    name = html.escape(item["name"])
    detail = html.escape(item["detail"])
    stack = html.escape(item["stack"])
    demand = html.escape(item["demand"])
    demand_class = html.escape(item["demand_class"])
    materials = html.escape(item["materials"])
    notes = html.escape(item["notes"])
    quality = html.escape(item["quality"])
    return (
        f'<tr data-crafted-key="{html.escape(key)}" data-market-source="crafted" '
        f'data-profession="{profession}">'
        f'<td data-column="item" data-label="Item"><strong class="q-{quality}">{name}</strong>'
        f'<div class="mini">{detail}</div></td>'
        f'<td data-column="target" data-label="Target Price">'
        f'{render_price_pair("target", int(item["target_copper"]))}</td>'
        f'<td data-column="quick" data-label="Quick Price">'
        f'{render_price_pair("quick", int(item["quick_copper"]))}</td>'
        f'<td data-column="high" data-label="High / Scarce">'
        f'{render_price_pair("high", int(item["high_copper"]))}</td>'
        f'<td data-column="stack" data-label="Stack Size">{stack}</td>'
        f'<td data-column="demand" data-label="Demand">'
        f'<span class="demand {demand_class}">{demand}</span></td>'
        f'<td data-column="notes" data-label="Use / Selling Notes">'
        f'<strong>Reagent floor:</strong> {materials}. {notes}</td></tr>'
    )


def render_crafted_section(config: dict, section: dict) -> str:
    title = html.escape(section["title"])
    description = html.escape(section["description"])
    rows = "\n".join(render_crafted_row(config, key) for key in section["items"])
    return (
        f'<section class="common crafted-market-section">\n'
        f'<h2>{title}</h2>\n'
        f'<p class="small">{description}</p>\n'
        f'<div class="table-wrap"><table class="ah-market-table ah-market-table--standard" '
        f'data-table-family="market"><thead><tr>'
        f'<th data-column="item">Item</th><th data-column="target">Target Price</th>'
        f'<th data-column="quick">Quick Price</th><th data-column="high">High / Scarce</th>'
        f'<th data-column="stack">Stack Size</th><th data-column="demand">Demand</th>'
        f'<th data-column="notes">Use / Selling Notes</th></tr></thead>'
        f'<tbody>{rows}</tbody></table></div>\n'
        f"</section>"
    )


def render_crafted_market(template: str, guide: dict, config: dict) -> str:
    sections = "\n".join(
        render_crafted_section(config, section)
        for section in guide["sections"]
    )
    return template.replace("{{SECTIONS}}", sections)


def transform_guide(
    source: str,
    filename: str,
    nav_template: str,
    vendor_template: str,
    crafted_template: str,
    vendor_config: dict,
    crafted_config: dict,
) -> str:
    source, nav_count = NAV_BLOCK.subn(nav_template, source, count=1)
    if nav_count != 1:
        raise ValueError(f"{filename}: expected exactly one guide navigation block")

    guide_config = vendor_config["guides"].get(filename)
    vendor_matches = len(VENDOR_BLOCK.findall(source))
    if guide_config:
        if vendor_matches != 1:
            raise ValueError(f"{filename}: expected exactly one vendor section")
        expected = render_vendor_section(
            vendor_template,
            guide_config["items"],
            vendor_config["catalog"],
        )
        source = VENDOR_BLOCK.sub(expected, source, count=1)
    elif vendor_matches:
        raise ValueError(f"{filename}: vendor section exists but is absent from canonical data")

    crafted_guide = crafted_config["guides"].get(filename)
    crafted_matches = len(CRAFTED_BLOCK.findall(source))
    if crafted_guide:
        expected = render_crafted_market(crafted_template, crafted_guide, crafted_config)
        if crafted_matches == 1:
            source = CRAFTED_BLOCK.sub(expected, source, count=1)
        elif (
            filename == "inscription-materials-ah-price-guide.html"
            and crafted_matches == 0
            and len(LEGACY_INSCRIPTION_CRAFTED_BLOCK.findall(source)) == 1
        ):
            source = LEGACY_INSCRIPTION_CRAFTED_BLOCK.sub(expected, source, count=1)
        else:
            raise ValueError(f"{filename}: expected one crafted-market or legacy block")
    elif crafted_matches:
        raise ValueError(f"{filename}: crafted section exists but is absent from canonical data")
    return source


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Fail if generated guide blocks are stale")
    args = parser.parse_args()

    vendor_config = load_vendor_config()
    crafted_config = load_crafted_config()
    nav_template = NAV_TEMPLATE_PATH.read_text(encoding="utf-8").strip()
    vendor_template = VENDOR_TEMPLATE_PATH.read_text(encoding="utf-8").strip()
    crafted_template = CRAFTED_TEMPLATE_PATH.read_text(encoding="utf-8").strip()
    changed: list[str] = []

    guide_paths = sorted(GUIDES_DIR.glob(AH_GUIDE_GLOB))
    if len(guide_paths) != 16:
        raise ValueError(f"Expected 16 AH guides, found {len(guide_paths)}")

    for path in guide_paths:
        source = path.read_text(encoding="utf-8")
        expected = transform_guide(
            source,
            path.name,
            nav_template,
            vendor_template,
            crafted_template,
            vendor_config,
            crafted_config,
        )
        if expected == source:
            continue
        if args.check:
            print(f"Stale generated AH blocks: {path.relative_to(ROOT)}", file=sys.stderr)
            return 1
        path.write_text(expected, encoding="utf-8", newline="\n")
        changed.append(str(path.relative_to(ROOT)))

    if changed:
        print("Updated canonical AH blocks in:")
        for path in changed:
            print(f"- {path}")
    else:
        print("Canonical AH blocks are current.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
