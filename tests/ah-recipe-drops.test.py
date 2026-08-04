#!/usr/bin/env python3
"""Lock the 90 recipe-drop rows to the audited tradeable 3.3.5 item set."""

from __future__ import annotations

import hashlib
import json
import re
import unicodedata
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
INDEX_PATH = ROOT / "assets" / "ah-search-index.js"
ITEM_IDS_PATH = ROOT / "assets" / "ah-item-ids.js"
EXPECTED_COUNTS = {
    "consumable-misc-recipe-drops-ah-price-guide.html": 15,
    "gear-pattern-drops-ah-price-guide.html": 37,
    "utility-recipe-drops-ah-price-guide.html": 38,
}
# Audited against AzerothCore's 3.3.5 item_template on 2026-08-04. Every
# fingerprinted record had item class 9 (Recipe) and bonding 0 (tradeable).
EXPECTED_AUDITED_FINGERPRINT = (
    "4bf4438cd4763db99666732922f83c7a9a832329c713d0c9f0a5d12541136cc5"
)


def fail(message: str) -> None:
    raise AssertionError(message)


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
    value = value.casefold().replace("'", "").replace(chr(0x2019), "")
    return " ".join(re.sub(r"[^a-z0-9]+", " ", value).split())


def main() -> int:
    index = generated_json(INDEX_PATH, "AH_SEARCH_INDEX")
    item_ids = generated_json(ITEM_IDS_PATH, "AH_ITEM_IDS")
    audited_rows: list[str] = []
    counts: Counter[str] = Counter()

    for entry in index["items"]:
        filename = entry["href"].split("/")[-1].split("#", 1)[0]
        if filename not in EXPECTED_COUNTS:
            continue
        item_id = item_ids.get(normalized_item_name(entry["name"]))
        if not item_id:
            fail(f'{filename}: recipe-drop tooltip is unresolved for {entry["name"]}')
        if not entry["name"].startswith(
            ("Formula:", "Recipe:", "Pattern:", "Plans:", "Schematic:", "Design:")
        ) and entry["name"] != "Book of Glyph Mastery":
            fail(f'{filename}: non-recipe item leaked into recipe-drop catalog: {entry["name"]}')
        counts[filename] += 1
        audited_rows.append(f'{filename}|{entry["name"]}|{item_id}')

    if dict(counts) != EXPECTED_COUNTS:
        fail(f"Recipe-drop guide counts changed: {dict(counts)}")
    if len(audited_rows) != 90:
        fail(f"Expected 90 recipe-drop rows, found {len(audited_rows)}")

    fingerprint = hashlib.sha256(
        "\n".join(sorted(audited_rows)).encode("utf-8")
    ).hexdigest()
    if fingerprint != EXPECTED_AUDITED_FINGERPRINT:
        fail(
            "Recipe-drop item set changed without a new class/binding audit: "
            f"{fingerprint}"
        )

    expected_corrections = {
        "Design: Etched Monarch Topaz": 41777,
        "Design: Shining Forest Emerald": 41782,
    }
    for name, item_id in expected_corrections.items():
        if item_ids.get(normalized_item_name(name)) != item_id:
            fail(f"{name}: expected audited 3.3.5 item ID {item_id}")

    print("All 90 recipe-drop rows match the audited tradeable 3.3.5 item set.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
