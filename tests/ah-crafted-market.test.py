#!/usr/bin/env python3
"""Validate the shared Inscription, Engineering, and Alchemy crafted catalog."""

from __future__ import annotations

import html
import json
import re
import subprocess
import sys
import unicodedata
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "data" / "ah-crafted-sections.json"
INDEX_PATH = ROOT / "assets" / "ah-search-index.js"
ITEM_IDS_PATH = ROOT / "assets" / "ah-item-ids.js"
EXPECTED_GUIDE_COUNTS = {
    "inscription-materials-ah-price-guide.html": 107,
    "engineering-materials-ah-price-guide.html": 55,
    "alchemy-materials-ah-price-guide.html": 12,
}


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


def merged_item(config: dict, key: str) -> dict:
    raw_item = config["catalog"][key]
    return (
        config["catalog_defaults"]
        | config["price_profiles"][raw_item["profile"]]
        | raw_item
    )


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
    guides = config["guides"]
    index = generated_json(INDEX_PATH, "AH_SEARCH_INDEX")
    item_ids = generated_json(ITEM_IDS_PATH, "AH_ITEM_IDS")

    expected_total = sum(EXPECTED_GUIDE_COUNTS.values())
    if len(catalog) != expected_total:
        fail(f"Expected {expected_total} curated crafted outputs, found {len(catalog)}")
    if set(guides) != set(EXPECTED_GUIDE_COUNTS):
        fail("Crafted guide configuration does not match the validated guide set")
    if len({item["item_id"] for item in catalog.values()}) != len(catalog):
        fail("Crafted item IDs must be unique")
    if len({item["name"].casefold() for item in catalog.values()}) != len(catalog):
        fail("Crafted item names must be unique")

    used_keys: list[str] = []
    sources: dict[str, str] = {}
    for filename, guide in guides.items():
        source = (ROOT / "guides" / filename).read_text(encoding="utf-8")
        sources[filename] = source
        if source.count("<!-- AH_CRAFTED_SECTION_START -->") != 1:
            fail(f"{filename}: expected one generated crafted-market block")

        expected_order = [
            key
            for section in guide["sections"]
            for key in section["items"]
        ]
        if len(expected_order) != EXPECTED_GUIDE_COUNTS[filename]:
            fail(
                f"{filename}: expected {EXPECTED_GUIDE_COUNTS[filename]} configured "
                f"outputs, found {len(expected_order)}"
            )
        actual_order = re.findall(r'data-crafted-key="([^"]+)"', source)
        if actual_order != expected_order:
            fail(f"{filename}: rendered rows do not match canonical crafted order")
        used_keys.extend(expected_order)

        for key in expected_order:
            item = merged_item(config, key)
            if not item["crafted"] or not item["tradeable"]:
                fail(f"{key}: every listed output must be crafted and tradeable")
            if item["binding"] not in {"none", "boe"}:
                fail(f"{key}: BoP or unknown binding is forbidden")

            quick = int(item["quick_copper"])
            target = int(item["target_copper"])
            high = int(item["high_copper"])
            if not 0 < quick <= target <= high:
                fail(f"{key}: expected positive quick <= target <= high prices")

            profession = re.escape(item["profession"])
            row_pattern = (
                rf'<tr data-crafted-key="{re.escape(key)}" '
                rf'data-market-source="crafted" data-profession="{profession}">'
                rf"(.*?)</tr>"
            )
            row_match = re.search(row_pattern, source, re.DOTALL)
            if not row_match:
                fail(f"{key}: missing standard crafted AH row metadata")
            row = row_match.group(1)

            for kind, value in (
                ("target", target),
                ("quick", quick),
                ("high", high),
            ):
                bid_value = int(
                    item.get(
                        f"{kind}_bid_copper",
                        max(1, round(value * 0.85)),
                    )
                )
                if not 0 < bid_value <= value:
                    fail(f"{key}: expected positive {kind} bid <= buyout")
                price_pattern = (
                    rf'<div class="pricepair {kind}">.*?'
                    rf'<span class="bid">{re.escape(format_money(bid_value))}</span>.*?'
                    rf'<span class="buyout">{re.escape(format_money(value))}</span>'
                )
                if not re.search(price_pattern, row, re.DOTALL):
                    fail(f"{key}: {kind} price does not match canonical data")
            if "<strong>Reagent floor:</strong>" not in row:
                fail(f"{key}: row is missing its reagent floor")
            if html.escape(item["notes"]) not in row:
                fail(f"{key}: selling note does not match canonical data")

            matches = [
                entry
                for entry in index["items"]
                if entry["name"] == item["name"]
                and entry["href"].startswith(f"./guides/{filename}#")
                and entry["marketSource"] == "crafted"
                and entry["profession"] == item["profession"]
            ]
            if len(matches) != 1:
                fail(f"{key}: expected one searchable crafted entry, found {len(matches)}")
            if matches[0]["target"] != format_money(target):
                fail(f"{key}: search target does not match canonical target")
            if item_ids.get(normalized_item_name(item["name"])) != int(item["item_id"]):
                fail(f"{key}: tooltip item ID is missing or incorrect")

    if len(used_keys) != len(set(used_keys)) or set(used_keys) != set(catalog):
        fail("Crafted catalog usage is duplicated or incomplete")

    inscription_block = sources[
        "inscription-materials-ah-price-guide.html"
    ].split("<!-- AH_CRAFTED_SECTION_START -->", 1)[1].split(
        "<!-- AH_CRAFTED_SECTION_END -->", 1
    )[0]
    for label in (
        "Scroll of Protection VIII",
        "Scroll of Recall",
        "Master's Inscription",
        "Darkmoon Card of the North</strong>",
        "Darkmoon Card: Greatness",
    ):
        if label in inscription_block:
            fail(f"Excluded or non-tradeable Inscription output leaked in: {label}")

    engineering_names = {
        merged_item(config, key)["name"]
        for key in used_keys
        if key.startswith("eng-")
    }
    for label in (
        "Titansteel Bar",
        "Cobalt Bar",
        "Dense Stone",
        "Salvaged Iron Golem Parts",
    ):
        if label in engineering_names:
            fail(f"Engineering input or vendor component leaked into crafted outputs: {label}")

    alchemy_names = {
        merged_item(config, key)["name"]
        for key in used_keys
        if key.startswith("alch-")
    }
    for label in (
        "Frost Lotus",
        "Eternal Fire",
        "Scarlet Ruby",
        "Pygmy Suckerfish",
        "Crystal Vial",
        "Arcanite Bar",
    ):
        if label in alchemy_names:
            fail(f"Alchemy input, vendor item, or reference row leaked into crafted outputs: {label}")

    alchemy_source = sources["alchemy-materials-ah-price-guide.html"]
    alchemy_outside_block = (
        alchemy_source.split("<!-- AH_CRAFTED_SECTION_START -->", 1)[0]
        + alchemy_source.split("<!-- AH_CRAFTED_SECTION_END -->", 1)[1]
    )
    if re.search(
        r'<strong class="q-common">Pygmy Oil</strong>',
        alchemy_outside_block,
    ):
        fail("Pygmy Oil remains duplicated in the Alchemy input rows")
    if re.search(
        r'<strong class="q-uncommon">Primal Might</strong>',
        alchemy_outside_block,
    ):
        fail("Primal Might remains duplicated in the Alchemy input rows")
    if "Major finished flasks / potions" in alchemy_outside_block:
        fail("Legacy Alchemy finished-consumable section remains after migration")

    print(
        "Crafted-market catalog, rows, prices, search metadata, and tooltip IDs "
        "are valid for Inscription, Engineering, and Alchemy."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
