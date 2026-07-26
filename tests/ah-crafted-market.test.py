#!/usr/bin/env python3
"""Validate the shared crafted-market catalog and Inscription launch section."""

from __future__ import annotations

import json
import re
import subprocess
import sys
import unicodedata
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "data" / "ah-crafted-sections.json"
GUIDE_PATH = ROOT / "guides" / "inscription-materials-ah-price-guide.html"
INDEX_PATH = ROOT / "assets" / "ah-search-index.js"
ITEM_IDS_PATH = ROOT / "assets" / "ah-item-ids.js"


def fail(message: str) -> None:
    raise AssertionError(message)


def format_money(copper: int) -> str:
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


def generated_json(path: Path, variable: str) -> dict:
    source = path.read_text(encoding="utf-8")
    match = re.search(rf"window\.{variable}=(\{{.*?\}});\n", source, re.DOTALL)
    if not match:
        fail(f"Could not parse {variable} from {path.name}")
    return json.loads(match.group(1))


def normalized_item_name(value: str) -> str:
    value = "".join(
        character
        for character in unicodedata.normalize("NFKD", value)
        if unicodedata.category(character) != "Mn"
    )
    value = re.sub(r"['’]", "", value.casefold())
    return " ".join(re.sub(r"[^a-z0-9]+", " ", value).split())


def main() -> int:
    subprocess.run(
        [sys.executable, "scripts/render-ah-shared-sections.py", "--check"],
        cwd=ROOT,
        check=True,
    )
    subprocess.run(
        [sys.executable, "scripts/build-ah-search-index.py", "--check"],
        cwd=ROOT,
        check=True,
    )

    config = json.loads(DATA_PATH.read_text(encoding="utf-8"))
    catalog = config["catalog"]
    profiles = config["price_profiles"]
    defaults = config["catalog_defaults"]
    guide = config["guides"]["inscription-materials-ah-price-guide.html"]
    source = GUIDE_PATH.read_text(encoding="utf-8")
    index = generated_json(INDEX_PATH, "AH_SEARCH_INDEX")
    item_ids = generated_json(ITEM_IDS_PATH, "AH_ITEM_IDS")

    if len(catalog) != 107:
        fail(f"Expected 107 curated Inscription outputs, found {len(catalog)}")
    if len({item["item_id"] for item in catalog.values()}) != len(catalog):
        fail("Crafted item IDs must be unique")
    if len({item["name"].casefold() for item in catalog.values()}) != len(catalog):
        fail("Crafted item names must be unique")

    expected_order = [
        key
        for section in guide["sections"]
        for key in section["items"]
    ]
    actual_order = re.findall(r'data-crafted-key="([^"]+)"', source)
    if actual_order != expected_order or set(expected_order) != set(catalog):
        fail("Rendered Inscription rows do not match the canonical crafted catalog")

    for key, raw_item in catalog.items():
        item = defaults | profiles[raw_item["profile"]] | raw_item
        if not item["crafted"] or not item["tradeable"]:
            fail(f"{key}: every listed output must be crafted and tradeable")
        if item["binding"] not in {"none", "boe"}:
            fail(f"{key}: BoP or unknown binding is forbidden")
        quick = int(item["quick_copper"])
        target = int(item["target_copper"])
        high = int(item["high_copper"])
        if not 0 < quick <= target <= high:
            fail(f"{key}: expected positive quick <= target <= high prices")

        row_pattern = (
            rf'<tr data-crafted-key="{re.escape(key)}" data-market-source="crafted" '
            rf'data-profession="Inscription">(.*?)</tr>'
        )
        row_match = re.search(row_pattern, source, re.DOTALL)
        if not row_match:
            fail(f"{key}: missing standard crafted AH row metadata")
        row = row_match.group(1)
        if '<div class="pricepair target">' not in row:
            fail(f"{key}: target price does not use the standard AH price box")
        if "<strong>Reagent floor:</strong>" not in row:
            fail(f"{key}: row is missing its reagent floor")

        matches = [
            entry
            for entry in index["items"]
            if entry["name"] == item["name"]
            and entry["href"].startswith(
                "./guides/inscription-materials-ah-price-guide.html#"
            )
            and entry["marketSource"] == "crafted"
            and entry["profession"] == "Inscription"
        ]
        if len(matches) != 1:
            fail(f"{key}: expected one searchable crafted entry, found {len(matches)}")
        if matches[0]["target"] != format_money(target):
            fail(f"{key}: search target does not match canonical target")
        if item_ids.get(normalized_item_name(item["name"])) != int(item["item_id"]):
            fail(f"{key}: tooltip item ID is missing or incorrect")

    forbidden = (
        "Scroll of Protection VIII",
        "Scroll of Recall",
        "Master's Inscription",
        "Darkmoon Card of the North</strong>",
        "Darkmoon Card: Greatness",
    )
    crafted_block = source.split("<!-- AH_CRAFTED_SECTION_START -->", 1)[1].split(
        "<!-- AH_CRAFTED_SECTION_END -->", 1
    )[0]
    for label in forbidden:
        if label in crafted_block:
            fail(f"Excluded or non-tradeable output leaked into crafted market: {label}")

    print("Crafted-market catalog, rows, search metadata, and tooltip IDs are valid.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
