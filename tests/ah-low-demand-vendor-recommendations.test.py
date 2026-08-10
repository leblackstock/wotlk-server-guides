#!/usr/bin/env python3
"""Validate the reviewed Low-demand liquidation recommendations used by AH search."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
AUDIT_PATH = ROOT / "data" / "ah-low-demand-vendor-recommendations.json"
INDEX_PATH = ROOT / "assets" / "ah-search-index.js"


subprocess.run(
    [sys.executable, "scripts/build-ah-search-index.py", "--check"],
    cwd=ROOT,
    check=True,
)

audit = json.loads(AUDIT_PATH.read_text(encoding="utf-8"))
index_source = INDEX_PATH.read_text(encoding="utf-8").splitlines()[1]
index = json.loads(
    index_source.removeprefix("window.AH_SEARCH_INDEX=").removesuffix(";")
)

low_items = [item for item in index["items"] if item["demand"] == "Low"]
low_names = {item["name"].casefold() for item in low_items}
recommended = [item for item in index["items"] if item.get("vendorRecommended") is True]
recommended_keys = {(item["guideId"], item["name"]) for item in recommended}
audit_item_keys = {
    (entry["guide_id"], entry["name"])
    for entry in audit["item_recommendations"]
}
audit_section_keys = {
    (entry["guide_id"], entry["section"])
    for entry in audit["section_recommendations"]
}
expected_keys = {
    (item["guideId"], item["name"])
    for item in index["items"]
    if (item["guideId"], item["section"]) in audit_section_keys
    or (item["guideId"], item["name"]) in audit_item_keys
}

scope = audit["reviewed_scope"]
assert len(low_items) == scope["low_entry_count_after_promotions"] == 1083
assert len(low_names) == scope["low_unique_name_count_after_promotions"] == 1056
assert len(recommended) == scope["vendor_recommendation_count"] == 22
assert (
    sum(item["target"] == "—" for item in recommended)
    == scope["promoted_reference_entry_count"]
    == 2
)
assert index["vendorRecommendationCount"] == len(recommended)
assert recommended_keys == expected_keys
assert all(item["demand"] == "Low" for item in recommended)
assert all(item["section"] != "Vendor & convenience items" for item in recommended)
assert not any(
    item.get("vendorRecommended") is True
    for item in index["items"]
    if item["section"] == "Vendor & convenience items"
)
assert len(low_items) - len(recommended) == 1061

required_recommendations = {
    "Raw Spinefin Halibut",
    "15 Pound Mud Snapper / 29 Pound Salmon / 32 Pound Catfish / 52 Pound Redgill / 68 Pound Grouper / 22 Pound Lobster / 92–103 Pound Mightfish",
    "Plated Armorfish",
    "Darkshore Grouper",
    "Crag Boar Rib",
}
assert required_recommendations <= {item["name"] for item in recommended}

for keep_item in ("Annihilator", "Anti-Venom", "Elementium Ore", "Crafted Light Shot"):
    matches = [item for item in low_items if item["name"] == keep_item]
    assert matches, keep_item
    assert not any(item.get("vendorRecommended") for item in matches), keep_item

print(
    f"Validated {len(low_items)} reviewed Low-demand entries: "
    f"{len(recommended)} Vendor recommendations and "
    f"{len(low_items) - len(recommended)} retained AH opportunities."
)
