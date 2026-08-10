#!/usr/bin/env python3
"""Guard the complete Phase 2 Blacksmithing Evidence Pricing review."""

from __future__ import annotations

import json
import subprocess
import sys
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE_PATH = ROOT / "data" / "ah-blacksmithing-price-evidence.json"
REPORT_PATH = ROOT / "docs" / "ah-blacksmithing-pricing-review.md"
CATALOG_PATH = ROOT / "data" / "ah-crafted-sections.json"
BASELINE_PATH = ROOT / "data" / "ah-price-baselines.json"
STATUS_PATH = ROOT / "data" / "ah-evidence-pricing-review-status.json"


subprocess.run(
    [sys.executable, "scripts/review-ah-blacksmithing-prices.py", "--check"],
    cwd=ROOT,
    check=True,
)

evidence = json.loads(EVIDENCE_PATH.read_text(encoding="utf-8"))
config = json.loads(CATALOG_PATH.read_text(encoding="utf-8"))
baseline = json.loads(BASELINE_PATH.read_text(encoding="utf-8"))["items"]
status = json.loads(STATUS_PATH.read_text(encoding="utf-8"))
summary = evidence["summary"]

assert evidence["method"] == "Evidence Pricing"
assert evidence["model_version"] == "blacksmithing-evidence-pricing-v1"
assert evidence["dependency_diagnostics_refreshed"] == "2026-08-08"
assert summary == {
    "items_reviewed": 453,
    "materials_enhancements_reviewed": 52,
    "armor_weapons_reviewed": 401,
    "bands_changed": 445,
    "completed_sale_items": 4,
    "items_seen_on_three_realms": 384,
    "target_changes_over_fifty_percent": 100,
    "proposals_below_reagent_floor": 222,
    "decision_counts": {
        "cohort-rank-starter-estimate": 442,
        "retain-reviewed-band-insufficient-coverage": 7,
        "sparse-completed-sales-shrunk": 4,
    },
    "external_gold_values_copied": False,
}
assert evidence["rules"]["active_hellscream_listing_prices_used"] is False
assert evidence["rules"]["external_gold_values_copied"] is False
assert evidence["sources"]["beancounter"]["raw_path_saved"] is False
assert evidence["sources"]["beancounter"]["buyer_names_saved"] is False
assert status["current_phase"] == (
    "All three Evidence Pricing phases complete locally; scheduled refreshes next"
)
assert status["guides"]["blacksmithing-materials"]["status"] == "Phase 2 complete locally"
assert status["guides"]["blacksmithing-gear"]["status"] == "Phase 2 complete locally"

records = list(evidence["items"].values())
assert len(records) == 453
assert Counter(record["view"] for record in records) == {
    "materials-enhancements": 52,
    "armor-weapons": 401,
}
assert Counter(record["proposal"]["reviewer_decision"] for record in records) == {
    "accept": 446,
    "retain": 7,
}
large = [record for record in records if record["proposal"]["requires_large_change_review"]]
assert len(large) == 100
assert sum(record["proposal"]["reviewer_decision"] == "accept" for record in large) == 93
assert all(
    record["external_relative_review"]["realm_count"] >= 2
    for record in large
    if record["proposal"]["reviewer_decision"] == "accept"
)
assert all(
    record["external_relative_review"]["realm_count"] < 2
    for record in large
    if record["proposal"]["reviewer_decision"] == "retain"
)

sale_records = [record for record in records if record["local_completed_sales"]]
assert {record["name"] for record in sale_records} == {
    "Cobalt Triangle Shield",
    "Tempered Saronite Belt",
    "Horned Cobalt Helm",
    "Rough Bronze Leggings",
}
assert all(record["local_completed_sales"]["evidence_gate"] == "low" for record in sale_records)
assert sorted(record["proposal"]["direct_sale_weight"] for record in sale_records) == [
    0.25,
    0.25,
    0.25,
    0.50,
]

for record in records:
    assert record["external_relative_review"]["used_to_set_gold_value"] is False
    assert len(record["source_observations"]) == 6
    assert all(
        "median_buyout_copper" not in observation and "economy_scale" not in observation
        for observation in record["source_observations"].values()
    )
    raw = config["catalog"][record["canonical_key"]]
    proposal = record["proposal"]["proposed_band"]
    assert {band: int(raw[f"{band}_copper"]) for band in ("quick", "target", "high")} == proposal
    assert raw["price_strategy"] == "evidence-pricing-market-value"
    expected_ref = f"data/ah-blacksmithing-price-evidence.json#items/{record['item_id']}"
    assert raw["price_evidence_ref"] == expected_ref
    assert record["reagent_floor"] == raw["pricing_floor_copper"]
    duplicate = baseline.get(str(record["item_id"]))
    if duplicate:
        assert {band: int(duplicate[band]) for band in ("quick", "target", "high")} == proposal
        assert duplicate["evidence_ref"] == expected_ref

representative_targets = {
    "bs-eternal-belt-buckle": 422_500,
    "bs-titanium-rod": 125_000,
    "bs-saronite-defender": 177_500,
    "bs-puresteel-legplates": 76_900_000,
    "bs-rough-grinding-stone": 1_500,
    "bs-horned-cobalt-helm": 105_000,
    "bs-cobalt-triangle-shield": 77_500,
}
for key, target in representative_targets.items():
    assert int(config["catalog"][key]["target_copper"]) == target

serialized = EVIDENCE_PATH.read_text(encoding="utf-8")
assert r"D:\Hellscream WoW" not in serialized
assert '"buyer":' not in serialized
assert '"seller":' not in serialized
report = REPORT_PATH.read_text(encoding="utf-8")
assert "Materials and enhancements: `52`" in report
assert "Armor, weapons, and shields: `401`" in report
assert "Manually reviewed Target changes over 50%: `100`" in report
assert "Publication status: `local only — not published`" in report

for filename in (
    "blacksmithing-materials-ah-price-guide.html",
    "blacksmithing-gear-ah-price-guide.html",
):
    source = (ROOT / "guides" / filename).read_text(encoding="utf-8")
    assert "Updated 2026-08-10" in source
    assert source.count("Evidence Pricing") >= 1

print(
    "Validated all 453 Blacksmithing Evidence Pricing decisions, 100 large-change reviews, "
    "four sparse-sale safeguards, duplicate baseline synchronization, and both rendered views."
)
