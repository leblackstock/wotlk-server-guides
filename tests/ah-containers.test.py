#!/usr/bin/env python3
"""Lock complete auctionable-container coverage and generated guide output."""

from __future__ import annotations

import json
import re
import subprocess
import sys
import unicodedata
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
AUDIT_PATH = ROOT / "data" / "ah-container-audit.json"
EVIDENCE_PATH = ROOT / "data" / "ah-container-price-evidence.json"
SECTIONS_PATH = ROOT / "data" / "ah-container-sections.json"
VENDOR_PATH = ROOT / "data" / "ah-vendor-sections.json"
CRAFTED_PATH = ROOT / "data" / "ah-crafted-sections.json"
SEARCH_PATH = ROOT / "assets" / "ah-search-index.js"
TOOLTIP_PATH = ROOT / "assets" / "ah-item-ids.js"


def generated(path: Path, variable: str) -> dict:
    source = path.read_text(encoding="utf-8")
    match = re.search(rf"window\.{variable}=(\{{.*?\}});\n", source, re.DOTALL)
    if not match:
        raise AssertionError(f"Could not parse {variable}")
    return json.loads(match.group(1))


def normalize(value: str) -> str:
    value = "".join(
        character
        for character in unicodedata.normalize("NFKD", value)
        if not unicodedata.combining(character)
    )
    value = value.casefold().replace("'", "").replace("&", " and ")
    return " ".join(re.sub(r"[^a-z0-9]+", " ", value).split())


def main() -> int:
    for command in (
        [sys.executable, "scripts/audit-ah-containers.py", "--check"],
        [sys.executable, "scripts/review-ah-container-prices.py", "--check"],
        [sys.executable, "scripts/render-ah-container-sections.py", "--check"],
    ):
        subprocess.run(command, cwd=ROOT, check=True)

    audit = json.loads(AUDIT_PATH.read_text(encoding="utf-8"))
    evidence = json.loads(EVIDENCE_PATH.read_text(encoding="utf-8"))
    sections = json.loads(SECTIONS_PATH.read_text(encoding="utf-8"))
    vendor = json.loads(VENDOR_PATH.read_text(encoding="utf-8"))
    crafted = json.loads(CRAFTED_PATH.read_text(encoding="utf-8"))
    search = generated(SEARCH_PATH, "AH_SEARCH_INDEX")
    tooltips = generated(TOOLTIP_PATH, "AH_ITEM_IDS")

    assert audit["summary"] == {
        "container_records": 175,
        "technically_auctionable_records": 115,
        "included_obtainable_auctionable_records": 93,
        "decisions": {
            "excluded-invalid-name": 12,
            "excluded-not-auctionable": 60,
            "excluded-unverified-acquisition": 10,
            "included-drop": 21,
            "included-existing-crafted": 52,
            "included-quest-reward": 1,
            "included-vendor": 19,
        },
        "primary_sources": {
            "crafted": 52,
            "drop": 21,
            "quest-reward": 1,
            "vendor": 19,
        },
    }
    included = {
        int(item_id): item
        for item_id, item in audit["items"].items()
        if item["decision"].startswith("included-")
    }
    assert len(included) == 93
    assert all(item["max_stack"] == 1 for item in included.values())
    assert all(item["technically_auctionable"] for item in included.values())

    crafted_ids = {
        int(item["item_id"])
        for item in crafted["catalog"].values()
        if int(item["item_id"]) in included
    }
    vendor_ids = {
        int(item["item_id"])
        for item in vendor["catalog"].values()
        if int(item["item_id"]) in included and not item.get("cost_only")
    }
    section_ids = {int(item["item_id"]) for item in sections["catalog"].values()}
    assert len(crafted_ids) == 52
    assert len(vendor_ids) == 19
    assert len(section_ids) == 22
    assert crafted_ids | vendor_ids | section_ids == set(included)
    assert not (crafted_ids & vendor_ids or crafted_ids & section_ids or vendor_ids & section_ids)

    assert audit["items"]["4496"]["primary_source"] == "vendor"
    assert set(audit["items"]["4496"]["acquisition_types"]) == {"vendor", "drop"}
    assert vendor["catalog"]["small-brown-pouch"]["target_copper"] == 1_000
    assert audit["items"]["19291"]["quest_reward_sources"][0]["quest_id"] == 7934
    assert sections["catalog"]["darkmoon-storage-box"]["target_copper"] == 35_000

    retry = evidence["source_snapshots"]["external_comparisons"]["retry_summary"]
    assert retry["initial_requests"] == 132
    assert retry["retry_delays_seconds"] == [2, 5, 10]
    assert retry["final_failed_requests"] == 0
    assert evidence["summary"]["items_with_completed_sales"] == 0
    assert evidence["summary"]["items_present_in_current_supply_snapshot"] == 3
    assert evidence["summary"]["items_seen_on_at_least_two_external_realms"] == 22
    assert evidence["rules"]["active_listings_used_to_set_prices"] is False
    assert evidence["rules"]["external_gold_values_copied"] is False

    world_source = (
        ROOT / "guides" / "sought-after-world-drops-ah-price-guide.html"
    ).read_text(encoding="utf-8")
    quest_source = (
        ROOT / "guides" / "drop-turn-in-quest-page-items-ah-price-guide.html"
    ).read_text(encoding="utf-8")
    assert world_source.count('data-container-key="') == 21
    assert quest_source.count('data-container-key="') == 1
    assert "<!-- AH_CONTAINER_DROPS_START -->" in world_source
    assert "<!-- AH_CONTAINER_QUEST_REWARDS_START -->" in quest_source
    assert "Updated 2026-08-08" in world_source
    assert "Updated 2026-08-08" in quest_source
    for source, marker in (
        (world_source, "AH_CONTAINER_DROPS"),
        (quest_source, "AH_CONTAINER_QUEST_REWARDS"),
    ):
        block = source.split(f"<!-- {marker}_START -->", 1)[1].split(
            f"<!-- {marker}_END -->", 1
        )[0]
        assert 'data-column="stack"' not in block
        assert "Stack Size" not in block

    search_counts = Counter(row["name"] for row in search["items"])
    for item_id, item in included.items():
        assert search_counts[item["name"]] == 1, item["name"]
        assert tooltips[normalize(item["name"])] == item_id, item["name"]
        matches = [row for row in search["items"] if row["name"] == item["name"]]
        assert matches[0]["stack"] == "1"

    print(
        "AH container validation passed: 93 obtainable auctionable containers "
        "are covered once across crafted, vendor, drop, and quest-reward routes."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
