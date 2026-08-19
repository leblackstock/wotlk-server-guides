#!/usr/bin/env python3
"""Validate NPC SellPrice coverage and demand-aware AH liquidation recommendations."""

from __future__ import annotations

import json
import re
import subprocess
import sys
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
POLICY_PATH = ROOT / "data" / "ah-vendor-recommendations.json"
ELIGIBILITY_PATH = ROOT / "data" / "ah-auction-eligibility-audit.json"
INDEX_PATH = ROOT / "assets" / "ah-search-index.js"
MONEY_PART = re.compile(r"([0-9][0-9,]*)\s*([gsc])")


def money(value: str) -> int | None:
    if value == "—":
        return None
    matches = MONEY_PART.findall(value)
    assert matches and not MONEY_PART.sub("", value).strip(), value
    multipliers = {"g": 10_000, "s": 100, "c": 1}
    return sum(int(amount.replace(",", "")) * multipliers[unit] for amount, unit in matches)


subprocess.run(
    [sys.executable, "scripts/build-ah-search-index.py", "--check"],
    cwd=ROOT,
    check=True,
)
subprocess.run(
    [sys.executable, "scripts/audit-ah-auction-eligibility.py", "--check"],
    cwd=ROOT,
    check=True,
)

policy = json.loads(POLICY_PATH.read_text(encoding="utf-8"))
eligibility = json.loads(ELIGIBILITY_PATH.read_text(encoding="utf-8"))
index_source = INDEX_PATH.read_text(encoding="utf-8").splitlines()[1]
index = json.loads(index_source.removeprefix("window.AH_SEARCH_INDEX=").removesuffix(";"))

scope = policy["reviewed_scope"]
items = index["items"]
recommended = [item for item in items if item.get("vendorRecommended") is True]
automatic = [
    item
    for item in recommended
    if item["vendorRecommendationSource"] in {"margin", "manual-and-margin"}
]
manual = [
    item
    for item in recommended
    if item["vendorRecommendationSource"] in {"manual", "manual-and-margin"}
]

assert policy["version"] == 2
assert policy["margin_model"]["sell_price_source_commit"] == eligibility["item_template_source"]["commit"]
assert policy["margin_model"]["minimum_expected_profit_copper_per_listing"] == 2500
assert set(policy["margin_model"]["sale_probability_basis_points_by_demand"]) == {
    item["demand"] for item in items
}
assert len(items) == scope["search_entry_count"] == 4088
assert index["vendorRecommendationCount"] == len(recommended) == scope["vendor_recommendation_count"] == 486
assert len(automatic) == scope["automatic_margin_vendor_recommendation_count"] == 469
assert len(manual) == scope["manual_vendor_recommendation_count"] == 22
assert scope["below_vendor_after_cut_entry_count"] == 79
assert scope["close_margin_vendor_recommendation_count"] == 390
assert scope["above_margin_entry_count"] == 3111
assert 79 + 390 == len(automatic)
assert 469 + 3111 == scope["margin_evaluated_entry_count"]
assert sum(item["target"] == "—" for item in items) == scope["unpriced_reference_entry_count"] == 2
assert sum(item.get("_vendorReferencePromotion") is True for item in items) == 0
assert all(
    "sell_price_copper" in record and int(record["sell_price_copper"]) >= 0
    for record in eligibility["items"].values()
)
assert eligibility["source_counts"]["unique_audited_item_ids"] == len(eligibility["items"]) == 3920
assert eligibility["source_counts"]["collectible_item_ids"] == 127
assert all(
    isinstance(item.get("vendorRecommendationNote"), str)
    and 1 <= len(item["vendorRecommendationNote"]) <= 60
    for item in recommended
)
assert Counter(item["vendorRecommendationNote"] for item in recommended) == Counter(
    {
        "AH net is below NPC value.": 79,
        "Expected profit is too small.": 390,
        "Too niche to keep reposting.": 15,
        "No known use.": 1,
        "Novelty item with little demand.": 1,
    }
)

for item in automatic:
    target = money(item["target"])
    minimum = money(item["vendorMinimumTarget"])
    vendor_sell = money(item["vendorSell"])
    assert target is not None and minimum is not None and vendor_sell is not None
    assert vendor_sell > 0
    assert target < minimum, item["name"]

for item in items:
    if not item.get("vendorSell"):
        continue
    assert item.get("vendorRecommended") is True
    assert money(item["target"]) < money(item["vendorMinimumTarget"]), item["name"]

assert Counter(item["vendorRecommendationSource"] for item in recommended) == Counter(
    {"margin": 464, "manual": 17, "manual-and-margin": 5}
)
assert not any(
    item.get("vendorRecommended")
    for item in items
    if item["section"] == "Vendor & convenience items"
    or "coin vendor" in item.get("conversionHint", "").casefold()
)

required_manual = {
    "Raw Spinefin Halibut",
    "15 Pound Mud Snapper / 29 Pound Salmon / 32 Pound Catfish / 52 Pound Redgill / 68 Pound Grouper / 22 Pound Lobster / 92–103 Pound Mightfish",
    "Plated Armorfish",
    "Darkshore Grouper",
    "Crag Boar Rib",
}
assert required_manual <= {item["name"] for item in manual}

required_margin = {
    "Adamantite Maul",
    "Azure Moonstone Ring",
    "Blood Garnet",
    "Bottomless Bag",
    "Core Felcloth Bag",
}
assert required_margin <= {item["name"] for item in automatic}

for keep_item in (
    "Annihilator",
    "Anti-Venom",
    "Blue Ribboned Wrapping Paper",
    "Crafted Light Shot",
    "Elementium Ore",
    "Holiday Spices",
    "Portable Hole",
):
    matches = [item for item in items if item["name"] == keep_item]
    assert matches, keep_item
    assert not any(item.get("vendorRecommended") for item in matches), keep_item

print(
    f"Validated saved NPC SellPrice values for {len(eligibility['items']):,} item IDs and "
    f"{len(recommended):,} Vendor-chip entries across all {index['guideCount']} AH guides."
)
