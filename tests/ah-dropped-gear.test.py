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
PRICE_EVIDENCE_PATH = ROOT / "data" / "ah-dropped-gear-price-evidence.json"
CROSS_SERVER_PATH = ROOT / "data" / "ah-dropped-gear-cross-server-diagnostics.json"
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
    price_evidence = load(PRICE_EVIDENCE_PATH)
    cross_server = load(CROSS_SERVER_PATH)
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
    assert price_evidence["review"]["reviewed_items"] == sum(EXPECTED_COUNTS.values())
    assert price_evidence["review"]["cohort_model_deployed"] is False
    assert price_evidence["review"]["starter_estimate_model_deployed"] is True
    assert price_evidence["review"]["starter_estimate_model_version"] == "hellscream-low-pop-relative-rank-v1"
    assert price_evidence["review"]["external_diagnostics"]["used_to_set_prices"] is False
    assert price_evidence["review"]["external_diagnostics"]["used_for_relative_rank"] is True
    assert cross_server["rules"]["external_asks_used_to_set_prices"] is False
    assert cross_server["summary"]["catalog_items"] == sum(EXPECTED_COUNTS.values())
    assert cross_server["summary"]["sources"] == 6
    assert cross_server["summary"]["realms"] == 3

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
        proposal = price_evidence["items"][item_id]["proposal"]
        assert record["source_type"] == proposal["source_type"], key
        assert record["confidence"] == proposal["confidence"], key
        assert {band: int(record[band]) for band in ("quick", "target", "high")} == proposal["proposed_band"], key
        assert record["reason"] == proposal["reason"], key
        assert int(record["quick"]) <= int(record["target"]) <= int(record["high"]), key
        assert "Active listing prices were not used" in record["reason"] or "External asks informed relative order only" in record["reason"], key
        assert tooltips[normalize(item["name"])] == item["item_id"], key
        assert eligibility_items[item_id]["bonding"] == 2, key
        assert cross_server["items"][item_id]["used_to_set_price"] is False, key

    assert price_evidence["items"]["37752"]["proposal"]["decision"] == "accept-sparse-direct-sale"
    assert price_evidence["items"]["44313"]["proposal"]["decision"] == "accept-sparse-direct-sale"
    assert sum(
        record["proposal"]["decision"] == "accept-reviewed-starter-estimate"
        for record in price_evidence["items"].values()
    ) == 345

    search_counts = Counter(item["guideId"] for item in search["items"])
    for guide_id, expected in EXPECTED_COUNTS.items():
        expected_search = expected + (21 if guide_id == "sought-after-world-drops" else 0)
        assert search_counts[guide_id] == expected_search
    assert [
        section["id"]
        for section in catalog["guides"]["sought-after-world-drops"]["sections"]
    ] == [
        "world-northrend-weapons",
        "world-northrend-armor",
        "world-northrend-accessories",
        "world-outland-weapons",
        "world-outland-armor",
        "world-outland-accessories",
        "world-classic-weapons",
        "world-classic-armor",
        "world-classic-accessories",
    ]
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
        expected_columns = (
            '<th data-column="item">Item</th><th data-column="target">Target Price</th>'
            '<th data-column="quick">Quick Price</th><th data-column="high">High / Scarce</th>'
            '<th data-column="notes">Use / Selling Notes</th><th data-column="demand">Demand</th>'
            '<th data-column="market">Market</th><th data-column="source">Source</th>'
        )
        expected_tables = len(guide["sections"]) + (
            1 if guide_id == "sought-after-world-drops" else 0
        )
        assert source.count(expected_columns) == expected_tables
        assert "Provisional fallback" not in source
        assert "Guide snapshot" not in source
        assert 'class="common ah-dropped-gear-summary"' not in source
        assert 'class="note ah-dropped-gear-fallback-note"' not in source
        assert source.count("<strong>* BoE pricing note:</strong>") == 1
        assert "Target is the recommended opening listing" in source
        assert "Most rows are modeled estimates" in source
        assert "Do not raise a price merely because the AH is empty" in source
        assert "Updated 2026-08-10" in source
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
