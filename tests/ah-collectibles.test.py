#!/usr/bin/env python3
"""Lock the verified collectibles catalog, evidence, ownership, and guide output."""

from __future__ import annotations

import json
import re
import subprocess
import sys
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
AUDIT_PATH = ROOT / "data" / "ah-collectible-audit.json"
EVIDENCE_PATH = ROOT / "data" / "ah-collectible-price-evidence.json"
SECTIONS_PATH = ROOT / "data" / "ah-collectible-sections.json"
CRAFTED_PATH = ROOT / "data" / "ah-crafted-sections.json"
VENDOR_PATH = ROOT / "data" / "ah-vendor-sections.json"
MANIFEST_PATH = ROOT / "data" / "ah-guides.json"
ELIGIBILITY_PATH = ROOT / "data" / "ah-auction-eligibility-audit.json"
GUIDE_PATH = ROOT / "guides" / "companions-mounts-accessories-ah-price-guide.html"
INDEX_PATH = ROOT / "assets" / "ah-search-index.js"


for command in (
    [sys.executable, "scripts/audit-ah-collectibles.py", "--check"],
    [sys.executable, "scripts/review-ah-collectible-prices.py", "--check"],
    [sys.executable, "scripts/render-ah-collectibles.py", "--check"],
    [sys.executable, "scripts/render-ah-shared-sections.py", "--check"],
    [sys.executable, "scripts/apply-ah-section-price-order.py", "--check"],
    [sys.executable, "scripts/build-ah-search-index.py", "--check"],
    [sys.executable, "scripts/apply-ah-item-tooltips.py", "--check"],
    [sys.executable, "scripts/audit-ah-auction-eligibility.py", "--check"],
):
    subprocess.run(command, cwd=ROOT, check=True)


audit = json.loads(AUDIT_PATH.read_text(encoding="utf-8"))
evidence = json.loads(EVIDENCE_PATH.read_text(encoding="utf-8"))
sections = json.loads(SECTIONS_PATH.read_text(encoding="utf-8"))
crafted = json.loads(CRAFTED_PATH.read_text(encoding="utf-8"))
vendor = json.loads(VENDOR_PATH.read_text(encoding="utf-8"))
manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
eligibility = json.loads(ELIGIBILITY_PATH.read_text(encoding="utf-8"))
guide = GUIDE_PATH.read_text(encoding="utf-8")
index = json.loads(
    INDEX_PATH.read_text(encoding="utf-8")
    .splitlines()[1]
    .removeprefix("window.AH_SEARCH_INDEX=")
    .removesuffix(";")
)


expected_groups = {
    "vendor-unlimited": 29,
    "vendor-limited": 2,
    "vendor-token": 12,
    "crafted-collectibles": 10,
    "companion-drops": 20,
    "companion-quest-rewards": 2,
    "promotional-mounts": 5,
    "quest-accessories": 5,
    "season-love-is-in-the-air": 17,
    "season-noblegarden": 3,
    "season-midsummer": 2,
    "season-winter-veil": 11,
    "season-lunar-festival": 15,
}
expected_seasons = [
    "Love is in the Air",
    "Noblegarden",
    "Children's Week",
    "Midsummer Fire Festival",
    "Brewfest",
    "Hallow's End",
    "Day of the Dead",
    "Pilgrim's Bounty",
    "Winter Veil",
    "Lunar Festival",
    "Pirates' Day",
]
expected_empty_seasons = {
    "Children's Week",
    "Brewfest",
    "Hallow's End",
    "Day of the Dead",
    "Pilgrim's Bounty",
    "Pirates' Day",
}

assert audit["source"]["commit"] == "e0fe11ba46b885a01e4a4038001e0055822cc7ba"
assert audit["rules"]["allowed_bonding"] == [0, 2, 3]
assert audit["rules"]["active_listings_set_prices"] is False
assert audit["summary"]["included_items"] == len(audit["items"]) == 133
assert audit["summary"]["groups"] == expected_groups
assert audit["summary"]["existing_exact_name_overlaps"] == 11
assert set(audit["empty_seasons"]) == expected_empty_seasons
assert len({item["item_id"] for item in audit["items"].values()}) == 133
assert all(item["auctionable"] for item in audit["items"].values())
assert all(item["duration"] == 0 for item in audit["items"].values())
assert all(item["buy_count"] >= 1 for item in audit["items"].values())
assert all(
    item["vendor_unit_cost_copper"]
    == (item["buy_price_copper"] + item["buy_count"] - 1) // item["buy_count"]
    for item in audit["items"].values()
)

white_kitten = audit["items"]["8489"]
wood_frog = audit["items"]["11027"]
assert white_kitten["vendor_sources"] == [{
    "entry": 8666,
    "name": "Lil Timmy",
    "max_count": 1,
    "restock_seconds": 3600,
    "extended_cost": 0,
}]
assert wood_frog["vendor_sources"] == [{
    "entry": 14860,
    "name": "Flik",
    "max_count": 1,
    "restock_seconds": 1800,
    "extended_cost": 0,
}]
assert audit["items"]["17194"]["buy_count"] == 5
assert audit["items"]["17194"]["vendor_unit_cost_copper"] == 2

assert evidence["summary"] == {
    "items_reviewed": 133,
    "decisions": {
        "exact-token-cost-plus-fallback-opportunity-anchor": 26,
        "exact-unlimited-vendor-arbitrage": 44,
        "fixed-acquisition-cohort-estimate": 62,
        "sparse-completed-sales-shrunk": 1,
    },
    "items_with_completed_sales": 1,
    "items_present_in_current_supply_snapshot": 2,
    "items_seen_on_at_least_two_external_realms": 56,
    "final_failed_comparison_requests": 0,
}
assert evidence["rules"]["active_hellscream_listing_prices_used"] is False
assert evidence["rules"]["external_gold_values_copied"] is False
assert evidence["rules"]["limited_and_unlimited_vendor_sections_separate"] is True
assert evidence["rules"]["seasons_rendered_separately"] is True
retry = evidence["source_snapshots"]["external_comparisons"]["retry_summary"]
assert retry["initial_requests"] == 366
assert retry["retry_delays_seconds"] == [2, 5, 10]
assert retry["final_failed_requests"] == 0
assert evidence["source_snapshots"]["auction_scan"]["listing_prices_saved"] is False
assert evidence["source_snapshots"]["auction_scan"]["listing_prices_used_to_set_baselines"] is False
assert all(
    record["external_relative_review"]["used_to_set_gold_value"] is False
    and record["external_relative_review"]["external_gold_value_copied"] is False
    for record in evidence["items"].values()
)
frog_evidence = evidence["items"]["11027"]
assert frog_evidence["local_completed_sales"]["completed_buyouts"] == 1
assert frog_evidence["local_completed_sales"]["distinct_buyers"] == 1
assert frog_evidence["local_completed_sales"]["distinct_days"] == 1
assert frog_evidence["proposal"]["sales_weight"] == 0.25
assert frog_evidence["proposal"]["confidence"] == "low"
assert evidence["items"]["17194"]["exact_vendor_cost_copper"] == 2

assert len(sections["catalog"]) == 133
assert len(sections["sections"]) == 21
season_sections = sections["sections"][10:]
assert [section["title"] for section in season_sections] == expected_seasons
assert {
    section["title"] for section in season_sections if not section["items"]
} == expected_empty_seasons
assert all(
    section.get("empty_reason")
    for section in season_sections
    if not section["items"]
)
for section in sections["sections"]:
    targets = [sections["catalog"][key]["target_copper"] for key in section["items"]]
    assert targets == sorted(targets, reverse=True), section["title"]

crafted_by_id = {int(item["item_id"]): item for item in crafted["catalog"].values()}
crafted_ids = {
    item["item_id"]
    for item in audit["items"].values()
    if item["group"] == "crafted-collectibles"
}
assert crafted_ids == set(crafted_by_id) & crafted_ids
for item_id in crafted_ids:
    canonical = crafted_by_id[item_id]
    proposal = evidence["items"][str(item_id)]["proposal"]["band"]
    assert {band: canonical[f"{band}_copper"] for band in ("quick", "target", "high")} == proposal
    assert canonical["pricing_floor_copper"] == evidence["items"][str(item_id)]["exact_recipe_floor"]
    assert canonical["price_evidence_ref"] == f"data/ah-collectible-price-evidence.json#items/{item_id}"

holiday_vendor = next(item for item in vendor["catalog"].values() if item["item_id"] == 17194)
holiday_collectible = next(item for item in sections["catalog"].values() if item["item_id"] == 17194)
assert holiday_vendor["target_copper"] == holiday_collectible["target_copper"] == 100
assert holiday_vendor["vendor_cost_copper"] // holiday_vendor["vendor_buy_count"] == holiday_collectible["vendor_cost_copper"] == 2

assert manifest["active_guide_count"] == len(manifest["guides"]) == 19
collectible_manifest = next(guide_record for guide_record in manifest["guides"] if guide_record["id"] == "collectibles")
assert collectible_manifest["file"] == GUIDE_PATH.name
assert len(collectible_manifest["navigation"][1]["children"]) == 3
assert len(collectible_manifest["navigation"][4]["children"]) == 11
assert index["guideCount"] == 19
assert Counter(item["guideId"] for item in index["items"])["collectibles"] == 133
assert guide.count('data-collectible-key="') == 133
assert guide.count('data-collectible-section="') == 21
assert guide.count("collectible-market-section--empty") == 6
assert guide.count('data-use-audience="general-use"') == 2
assert guide.count('data-use-audience="profession-restricted"') == 1
general_mounts = re.search(
    r'data-collectible-section="crafted-mounts-general-use".*?</section>',
    guide,
    re.DOTALL,
)
restricted_mounts = re.search(
    r'data-collectible-section="crafted-mounts-profession-required".*?</section>',
    guide,
    re.DOTALL,
)
assert general_mounts and general_mounts.group(0).count('data-collectible-key="') == 2
assert restricted_mounts and restricted_mounts.group(0).count('data-collectible-key="') == 3
assert "Engineering 375 required to use." in restricted_mounts.group(0)
assert "Engineering 300 required to use." in restricted_mounts.group(0)
assert "Tailoring 300 required to use." in restricted_mounts.group(0)
assert "Updated 2026-08-10" in guide
assert "Magic Rooster Egg" in guide and "Wooly White Rhino" in guide and "Blazing Hippogryph" in guide
assert re.search(r"Holiday Spices.*Exact vendor cost: 2c", guide, re.DOTALL)

assert eligibility["rules"]["allowed_bonding"] == [0, 2, 3]
assert eligibility["source_counts"]["collectible_item_ids"] == 133
assert all(str(item_id) in eligibility["items"] for item_id in crafted_ids)

print("Validated 133 evidence-priced collectible rows across 21 acquisition and seasonal sections.")
