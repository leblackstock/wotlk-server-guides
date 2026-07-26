#!/usr/bin/env python3
"""Render canonical navigation and vendor-pricing sections into every AH guide."""

from __future__ import annotations

import argparse
import html
import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
GUIDES_DIR = ROOT / "guides"
DATA_PATH = ROOT / "data" / "ah-vendor-sections.json"
NAV_TEMPLATE_PATH = ROOT / "templates" / "ah-guide" / "navigation.html"
VENDOR_TEMPLATE_PATH = ROOT / "templates" / "ah-guide" / "vendor-convenience-section.html"
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


def render_row(key: str, item: dict) -> str:
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


def load_config() -> dict:
    config = json.loads(DATA_PATH.read_text(encoding="utf-8"))
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
    rows = "\n".join(render_row(key, catalog[key]) for key in item_keys)
    return template.replace("{{ROWS}}", rows)


def transform_guide(
    source: str,
    filename: str,
    nav_template: str,
    vendor_template: str,
    config: dict,
) -> str:
    source, nav_count = NAV_BLOCK.subn(nav_template, source, count=1)
    if nav_count != 1:
        raise ValueError(f"{filename}: expected exactly one guide navigation block")

    guide_config = config["guides"].get(filename)
    vendor_matches = len(VENDOR_BLOCK.findall(source))
    if guide_config:
        if vendor_matches != 1:
            raise ValueError(f"{filename}: expected exactly one vendor section")
        expected = render_vendor_section(
            vendor_template,
            guide_config["items"],
            config["catalog"],
        )
        source = VENDOR_BLOCK.sub(expected, source, count=1)
    elif vendor_matches:
        raise ValueError(f"{filename}: vendor section exists but is absent from canonical data")
    return source


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Fail if generated guide blocks are stale")
    args = parser.parse_args()

    config = load_config()
    nav_template = NAV_TEMPLATE_PATH.read_text(encoding="utf-8").strip()
    vendor_template = VENDOR_TEMPLATE_PATH.read_text(encoding="utf-8").strip()
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
            config,
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
