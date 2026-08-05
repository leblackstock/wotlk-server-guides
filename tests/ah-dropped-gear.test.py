#!/usr/bin/env python3
"""Lock the audited scope and generated output for both dropped-gear guides."""

from __future__ import annotations

import html
import json
import re
import unicodedata
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CATALOG_PATH = ROOT / "data" / "ah-dropped-gear.json"
AUDIT_PATH = ROOT / "data" / "ah-dropped-gear-audit.json"
BASELINE_PATH = ROOT / "data" / "ah-price-baselines.json"
ELIGIBILITY_PATH = ROOT / "data" / "ah-auction-eligibility-audit.json"
CRAFTED_PATH = ROOT / "data" / "ah-crafted-sections.json"
VENDOR_PATH = ROOT / "data" / "ah-vendor-sections.json"
TOOLTIPS_PATH = ROOT / "assets" / "ah-item-ids.js"
SEARCH_PATH = ROOT / "assets" / "ah-search-index.js"

SOURCE_COMMIT = "e0fe11ba46b885a01e4a4038001e0055822cc7ba"
AUDIT_FINGERPRINT = "b5b3b34bd499e137308171d43d6eb22905cc5ce2dbbcf3bd61f26d9a1a3e503a"
EXPECTED_COUNTS = {
    "level-80-boe-epics": 85,
    "sought-after-world-drops": 262,
}
BRACKET_CAPS = {19, 29, 39, 49, 59, 69, 70}


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def load_js_object(path: Path, variable: str) -> dict:
    source = path.read_text(encoding="utf-8")
    match = re.search(rf"window\.{re.escape(variable)}=(.*?);(?:\n|$)", source)
    assert match, f"{path.name}: missing window.{variable}"
    return json.loads(match.group(1))


def normalize(value: str) -> str:
    value = unicodedata.normalize("NFKD", value)
    value = "".join(character for character in value if not unicodedata.combining(character))
    value = value.lower().replace("’", "").replace("'", "").replace("&", " and ")
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9]+", " ", value).strip())


def main() -> int:
    catalog = load(CATALOG_PATH)
    audit = load(AUDIT_PATH)
    baseline = load(BASELINE_PATH)
    eligibility = load(ELIGIBILITY_PATH)
    crafted = load(CRAFTED_PATH)
    vendor = load(VENDOR_PATH)
    tooltips = load_js_object(TOOLTIPS_PATH, "AH_ITEM_IDS")
    search = load_js_object(SEARCH_PATH, "AH_SEARCH_INDEX")

    assert catalog["audit_commit"] == SOURCE_COMMIT
    assert audit["source"]["commit"] == SOURCE_COMMIT
    assert audit["fingerprint"] == AUDIT_FINGERPRINT
    assert audit["rules"]["active_listings_used_for_prices"] is False
    assert audit["included_counts"] == EXPECTED_COUNTS

    entries = catalog["catalog"]
    assert len(entries) == sum(EXPECTED_COUNTS.values())
    ids = [int(item["item_id"]) for item in entries.values()]
    assert len(ids) == len(set(ids)), "Dropped-gear catalog contains duplicate item IDs"
    assert set(ids) == {int(item_id) for item_id in audit["items"]}

    counts = Counter(item["guide_id"] for item in entries.values())
    assert counts == Counter(EXPECTED_COUNTS)
    section_counts = Counter(item["section_id"] for item in entries.values())
    declared_sections = {
        section["id"]
        for guide in catalog["guides"].values()
        for section in guide["sections"]
    }
    assert set(section_counts) == declared_sections
    assert all(section_counts[section_id] > 0 for section_id in declared_sections)

    notes = [item["notes"] for item in entries.values()]
    assert len(set(notes)) >= 250, "Dropped-gear notes are not sufficiently item-specific"
    assert all(180 <= len(note) <= 340 for note in notes)
    assert all("supply" in note.casefold() for note in notes)
    assert all("Provisional fallback band. Post one at a time" not in note for note in notes)
    assert entries["shadowfang"]["notes"].startswith(
        "Fixed-stat level 19 one-handed weapon for bracket players"
    )
    assert "Shadowfang Keep trash farming" in entries["shadowfang"]["notes"]
    assert entries["wodins-lucky-necklace"]["notes"].startswith(
        "ICC-era iLvl 264 necklace for level-80 gearing"
    )
    assert "Sack of Frosty Treasures supply" in entries["wodins-lucky-necklace"]["notes"]

    for item_id, item in audit["items"].items():
        assert item["bonding"] == 2, f"{item_id}: not bind-on-equip"
        assert item["duration"] == 0, f"{item_id}: temporary item"
        assert item["item_class"] in {2, 4}, f"{item_id}: not equipment"
        assert item["source_types"], f"{item_id}: no audited loot source"
        if item["guide_id"] == "level-80-boe-epics":
            assert item["quality"] == 4 and item["required_level"] == 80
        else:
            assert item["required_level"] < 80
            assert item["random_property"] == 0 and item["random_suffix"] == 0
            if item["quality"] == 3:
                assert item["required_level"] in BRACKET_CAPS or 71 <= item["required_level"] <= 79
            else:
                assert item["quality"] == 4

    crafted_ids = {int(item["item_id"]) for item in crafted["catalog"].values()}
    vendor_ids = {int(item["item_id"]) for item in vendor["catalog"].values()}
    assert not set(ids) & crafted_ids, "Crafted output leaked into the dropped-gear catalog"
    assert not set(ids) & vendor_ids, "Vendor item leaked into the dropped-gear catalog"

    eligibility_items = eligibility["items"]
    for key, item in entries.items():
        item_id = str(item["item_id"])
        record = baseline["items"][item_id]
        assert record["source_type"] == "documented-fallback", key
        assert record["confidence"] == "fallback", key
        assert int(record["quick"]) <= int(record["target"]) <= int(record["high"]), key
        assert "No active listing was used" in record["reason"], key
        assert tooltips[normalize(item["name"])] == item["item_id"], key
        assert eligibility_items[item_id]["bonding"] == 2, key

    search_counts = Counter(item["guideId"] for item in search["items"])
    for guide_id, expected in EXPECTED_COUNTS.items():
        assert search_counts[guide_id] == expected
    for key, item in entries.items():
        matches = [
            row
            for row in search["items"]
            if row["guideId"] == item["guide_id"] and row["name"] == item["name"]
        ]
        assert len(matches) == 1, f"{key}: expected one guide-specific search entry"
        assert matches[0]["href"].endswith(f"#ah-item={key}"), key

    for guide_id, guide in catalog["guides"].items():
        source = (ROOT / "guides" / guide["file"]).read_text(encoding="utf-8")
        expected = EXPECTED_COUNTS[guide_id]
        assert source.count('data-market-source="dropped"') == expected
        assert source.count('data-dropped-gear-key="') == expected
        assert source.count("Provisional fallback") >= expected
        assert "Updated 2026-08-05" in source
        for key, item in entries.items():
            if item["guide_id"] != guide_id:
                continue
            assert f'data-dropped-gear-key="{key}"' in source
            assert f"Req {item['required_level']}" in source
            assert f"iLvl {item['item_level']}" in source
            assert html.escape(item["notes"]) in source

    print("Dropped-gear audit passed: 85 level-80 epic BoEs and 262 sought-after pre-80 drops are locked to canonical output.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
