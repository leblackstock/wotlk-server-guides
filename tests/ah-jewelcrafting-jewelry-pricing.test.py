#!/usr/bin/env python3
"""Guard the complete Phase 2 Jewelcrafting jewelry Evidence Pricing review."""

from __future__ import annotations

import json
import subprocess
import sys
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE_PATH = ROOT / "data" / "ah-jewelcrafting-jewelry-price-evidence.json"
REPORT_PATH = ROOT / "docs" / "ah-jewelcrafting-jewelry-pricing-review.md"
CATALOG_PATH = ROOT / "data" / "ah-crafted-sections.json"
BASELINE_PATH = ROOT / "data" / "ah-price-baselines.json"
STATUS_PATH = ROOT / "data" / "ah-evidence-pricing-review-status.json"
GEM_GUIDE_PATH = ROOT / "guides" / "jewelcrafting-gems-ah-price-guide.html"
JEWELRY_GUIDE_PATH = ROOT / "guides" / "jewelcrafting-jewelry-ah-price-guide.html"
SEARCH_PATH = ROOT / "assets" / "ah-search-index.js"

subprocess.run(
    [sys.executable, "scripts/review-ah-jewelcrafting-jewelry-prices.py", "--check"],
    cwd=ROOT,
    check=True,
)

evidence = json.loads(EVIDENCE_PATH.read_text(encoding="utf-8"))
config = json.loads(CATALOG_PATH.read_text(encoding="utf-8"))
baseline = json.loads(BASELINE_PATH.read_text(encoding="utf-8"))["items"]
status = json.loads(STATUS_PATH.read_text(encoding="utf-8"))
summary = evidence["summary"]

assert evidence["method"] == "Evidence Pricing"
assert evidence["model_version"] == "jewelcrafting-jewelry-evidence-pricing-v1"
assert evidence["dependency_diagnostics_refreshed"] == "2026-08-08"
assert evidence["manual_review_completed"] == "2026-08-06"
assert summary == {
    "items_reviewed": 137,
    "sections_reviewed": 7,
    "boe_equipment_reviewed": 121,
    "components_special_reviewed": 16,
    "quality_counts": {"common": 4, "epic": 15, "rare": 58, "uncommon": 60},
    "bands_changed": 132,
    "completed_sale_items": 6,
    "medium_confidence_sale_items": 1,
    "items_seen_on_three_realms": 113,
    "target_changes_over_fifty_percent": 38,
    "large_changes_accepted": 38,
    "large_changes_retained": 0,
    "proposals_below_reagent_floor": 55,
    "legacy_baseline_duplicates": 5,
    "decision_counts": {
        "cohort-rank-starter-estimate": 126,
        "direct-completed-sales": 1,
        "retain-reviewed-band-no-comparison-coverage": 5,
        "sparse-completed-sales-shrunk": 5,
    },
    "external_gold_values_copied": False,
}
assert evidence["rules"]["active_hellscream_listing_prices_used"] is False
assert evidence["rules"]["external_gold_values_copied"] is False
assert evidence["sources"]["beancounter"]["raw_path_saved"] is False
assert evidence["sources"]["beancounter"]["buyer_names_saved"] is False
assert status["current_phase"] == "All three Evidence Pricing phases complete locally; scheduled refreshes next"
assert status["guides"]["jewelcrafting-gems"]["status"] == "Phase 2 complete locally"
assert status["guides"]["jewelcrafting-jewelry"]["status"] == "Phase 2 complete locally"

records = list(evidence["items"].values())
assert len(records) == 137
assert Counter(record["view"] for record in records) == {
    "boe-equipment": 121,
    "components-special": 16,
}
assert Counter(record["quality"] for record in records) == {
    "uncommon": 60,
    "rare": 58,
    "epic": 15,
    "common": 4,
}
assert Counter(record["external_relative_review"]["realm_count"] for record in records) == {
    3: 113,
    2: 12,
    1: 7,
    0: 5,
}
assert Counter(record["proposal"]["reviewer_decision"] for record in records) == {
    "accept": 132,
    "retain": 5,
}
large = [record for record in records if record["proposal"]["requires_large_change_review"]]
assert len(large) == 38
assert all(record["external_relative_review"]["realm_count"] >= 2 for record in large)
assert all(record["proposal"]["reviewer_decision"] == "accept" for record in large)

sales = {record["name"]: record for record in records if record["local_completed_sales"]}
assert set(sales) == {
    "Citrine Ring of Rapid Healing",
    "Engraved Truesilver Ring",
    "Pendant of the Agate Shield",
    "Ring of Silver Might",
    "Ring of Twilight Shadows",
    "Tigerseye Band",
}
assert sales["Tigerseye Band"]["proposal"]["decision"] == "direct-completed-sales"
assert all(
    record["proposal"]["decision"] == "sparse-completed-sales-shrunk"
    for name, record in sales.items()
    if name != "Tigerseye Band"
)

for record in records:
    assert record["pricing_unit"] == "per finished item"
    assert record["sale_gate_type"] in {"single-finished-item", "stackable-finished-item"}
    assert record["recipe"]["output_count"] == 1
    assert record["external_relative_review"]["used_to_set_gold_value"] is False
    assert len(record["source_observations"]) == 6
    assert all(
        "median_buyout_copper" not in observation and "economy_scale" not in observation
        for observation in record["source_observations"].values()
    )
    raw = config["catalog"][record["canonical_key"]]
    proposal = record["proposal"]["proposed_band"]
    assert {
        band: int(raw[f"{band}_copper"]) for band in ("quick", "target", "high")
    } == proposal
    assert raw["price_strategy"] == "evidence-pricing-market-value"
    expected_ref = f"data/ah-jewelcrafting-jewelry-price-evidence.json#items/{record['item_id']}"
    assert raw["price_evidence_ref"] == expected_ref
    assert "collection buyers; post one at a time" not in raw["row_note"]

duplicate_ids = {49110, 20816, 20817, 20963, 21752}
assert duplicate_ids == {
    record["item_id"] for record in records if record["legacy_baseline_duplicate"]
}
for item_id in duplicate_ids:
    record = evidence["items"][str(item_id)]
    duplicate = baseline[str(item_id)]
    assert {
        band: int(duplicate[band]) for band in ("quick", "target", "high")
    } == record["proposal"]["proposed_band"]
    assert duplicate["evidence_ref"] == (
        f"data/ah-jewelcrafting-jewelry-price-evidence.json#items/{item_id}"
    )

representative_targets = {
    "jc-titanium-impact-choker": 7_400_000,
    "jc-blood-sun-necklace": 397_500,
    "jc-tigerseye-band": 850,
    "jc-delicate-copper-wire": 8_200,
    "jc-icy-prism": 360_000,
    "jc-nightmare-tear": 1_300_000,
}
for key, target in representative_targets.items():
    assert int(config["catalog"][key]["target_copper"]) == target

serialized = EVIDENCE_PATH.read_text(encoding="utf-8")
assert r"D:\Hellscream WoW" not in serialized
assert '"buyer":' not in serialized
assert '"seller":' not in serialized
report = REPORT_PATH.read_text(encoding="utf-8")
assert "BoE jewelry, equipment, and weapon outputs: `121`" in report
assert "Manually reviewed Target candidates over 50%: `38`" in report
assert "Publication status: `local only — not published`" in report

gem_guide = GEM_GUIDE_PATH.read_text(encoding="utf-8")
jewelry_guide = JEWELRY_GUIDE_PATH.read_text(encoding="utf-8")
assert "Updated 2026-08-09" in gem_guide
assert "Updated 2026-08-06" in jewelry_guide
assert jewelry_guide.count('class="crafted-recipe-link ') == 137
assert jewelry_guide.count('class="crafted-note-ref"') == 137
assert "collection buyers; post one at a time" not in jewelry_guide
assert "ChargesSell Price" not in jewelry_guide
assert jewelry_guide.count("Evidence Pricing and craft diagnostics") >= 1
assert "BoE gear is a slow market; list one at a time." in jewelry_guide

search = SEARCH_PATH.read_text(encoding="utf-8")
assert '"name":"Titanium Impact Choker"' in search
assert '"target":"740g"' in search
assert '"name":"Tigerseye Band"' in search
assert '"target":"8s 50c"' in search

print(
    "Validated all 137 Jewelcrafting jewelry Evidence Pricing decisions, 38 "
    "large-change reviews, six completed-sale records, exact recipe diagnostics, "
    "five duplicate baselines, concise notes, recipes, and search output."
)
