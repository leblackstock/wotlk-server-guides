#!/usr/bin/env python3
"""Validate that AH guide styles remain shared and scoped."""

from __future__ import annotations

import html
import json
import re
import sys
import unicodedata
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
GUIDES_DIR = ROOT / "guides"
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from ah_guides import active_guide_paths  # noqa: E402

STYLES_PATH = ROOT / "assets" / "ah-price-guide.css"
ICON_STYLES_PATH = ROOT / "assets" / "ah-guide-icons.css"
SEARCH_STYLES_PATH = ROOT / "assets" / "style.css"
ITEM_IDS_PATH = ROOT / "assets" / "ah-item-ids.js"
STYLESHEET_VERSION = "20260810-ah-source-notes-v1"


def normalize_item_name(value: str) -> str:
    value = "".join(
        character
        for character in unicodedata.normalize("NFKD", value)
        if unicodedata.category(character) != "Mn"
    )
    value = value.casefold().replace("’", "").replace("'", "").replace("&", " and ")
    return " ".join(re.sub(r"[^a-z0-9]+", " ", value).split())


guide_paths = active_guide_paths(guides_dir=GUIDES_DIR)
assert len(guide_paths) == 19

inline_style_guides = [
    path.name
    for path in guide_paths
    if re.search(r"<style(?:\s|>)", path.read_text(encoding="utf-8"), re.IGNORECASE)
]
assert not inline_style_guides, (
    "AH guide styles must live in the shared stylesheet: "
    + ", ".join(inline_style_guides)
)

for path in guide_paths:
    source = path.read_text(encoding="utf-8")
    assert '../assets/style.css' in source, f"{path.name}: shared search styles are missing"
    expected_href = f"../assets/ah-guide-icons.css?v={STYLESHEET_VERSION}"
    assert expected_href in source, f"{path.name}: shared AH stylesheet cache marker is stale"
    assert source.count("<!-- AH_BASELINE_NOTE_START -->") == 1, (
        f"{path.name}: expected exactly one canonical pricing-baseline note"
    )
    assert source.count('class="note ah-baseline-note"') == 1, (
        f"{path.name}: expected exactly one visible pricing-baseline note"
    )
    assert "Active listings show competition only and never set or raise guide prices." in source, (
        f"{path.name}: pricing-baseline note does not preserve the non-circular guard"
    )

icon_styles = ICON_STYLES_PATH.read_text(encoding="utf-8")
assert f'./ah-price-guide.css?v={STYLESHEET_VERSION}' in icon_styles, (
    "AH icon stylesheet does not load the cache-busted rarity stylesheet"
)

styles = STYLES_PATH.read_text(encoding="utf-8")
required_selectors = (
    'body[data-guide-section="auction-house"] .ah-item-link',
    'body[data-guide-section="auction-house"] .ah-item-link:hover',
    'body[data-guide-section="auction-house"] .ah-item-link:focus-visible',
    'body[data-guide-section="auction-house"] .ah-item-icon',
    'body[data-guide-section="auction-house"] .q-common',
    'body[data-guide-section="auction-house"] .q-uncommon',
    'body[data-guide-section="auction-house"] .q-rare',
    'body[data-guide-section="auction-house"] .q-epic',
    'body[data-guide-section="auction-house"] .q-legendary',
)
for selector in required_selectors:
    assert selector in styles, f"Missing shared selector: {selector}"

search_styles = SEARCH_STYLES_PATH.read_text(encoding="utf-8")
for quality in ("uncommon", "rare", "epic", "legendary"):
    selector = f".ah-search-item-name.quality-{quality}"
    assert selector in search_styles, f"Missing search-result rarity selector: {selector}"

item_ids_source = ITEM_IDS_PATH.read_text(encoding="utf-8")
item_ids_match = re.search(r"window\.AH_ITEM_IDS=(\{.*?\});\n", item_ids_source, re.DOTALL)
assert item_ids_match, "Could not parse generated AH item IDs"
item_ids = json.loads(item_ids_match.group(1))

checked_item_names = 0
for path in guide_paths:
    source = path.read_text(encoding="utf-8")
    first_cells = re.findall(
        r'<td data-column="item"[^>]*>\s*<strong(?: class="([^"]*)")?>(.*?)</strong>',
        source,
        re.DOTALL,
    )
    for classes, raw_name in first_cells:
        name = html.unescape(re.sub(r"<[^>]+>", "", raw_name)).strip()
        if normalize_item_name(name) not in item_ids:
            continue
        checked_item_names += 1
        assert re.search(r"\bq-(?:poor|common|uncommon|rare|epic|legendary)\b", classes or ""), (
            f"{path.name}: item name lacks a rarity class: {name}"
        )

print(
    f"Validated shared, scoped styling and rarity colors for "
    f"{checked_item_names} item names across 18 AH guides."
)
