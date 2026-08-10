#!/usr/bin/env python3
"""Validate the completed Leatherworking Evidence Pricing review."""

from __future__ import annotations

import json
import re
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CRAFTED_PATH = ROOT / "data" / "ah-crafted-sections.json"
RECIPE_PATH = ROOT / "data" / "ah-crafted-recipe-audit.json"
USE_PATH = ROOT / "data" / "ah-profession-use-audit.json"
MATERIAL_EVIDENCE_PATH = ROOT / "data" / "ah-profession-material-price-evidence.json"
EVIDENCE_PATH = ROOT / "data" / "ah-leatherworking-price-evidence.json"
STATUS_PATH = ROOT / "data" / "ah-evidence-pricing-review-status.json"
REPORT_PATH = ROOT / "docs" / "ah-leatherworking-pricing-review.md"
PLAN_PATH = ROOT / "docs" / "ah-profession-plans" / "leatherworking.md"
GUIDE_PATH = ROOT / "guides" / "skinning-leatherworking-materials-ah-price-guide.html"
INDEX_PATH = ROOT / "assets" / "ah-search-index.js"
GUIDE_FILENAME = GUIDE_PATH.name
PRICE_BANDS = ("quick", "target", "high")
MATERIAL_PREFIX = "data/ah-profession-material-price-evidence.json#items/"
EVIDENCE_PREFIX = "data/ah-leatherworking-price-evidence.json#items/"

EXPECTED_VIEWS = {
    "bags": 19,
    "enhancements": 29,
    "gear": 420,
    "restricted-drums": 5,
    "utility": 3,
}


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def merged_item(config: dict, key: str) -> dict:
    raw = config["catalog"][key]
    return config["catalog_defaults"] | config["price_profiles"][raw["profile"]] | raw


config = load(CRAFTED_PATH)
recipes = load(RECIPE_PATH)["recipes"]
use_audit = load(USE_PATH)
material_evidence = load(MATERIAL_EVIDENCE_PATH)["items"]
evidence = load(EVIDENCE_PATH)
status = load(STATUS_PATH)
report = REPORT_PATH.read_text(encoding="utf-8")
plan = PLAN_PATH.read_text(encoding="utf-8")
guide = GUIDE_PATH.read_text(encoding="utf-8")
search = INDEX_PATH.read_text(encoding="utf-8")

guide_config = config["guides"][GUIDE_FILENAME]
leatherworking_keys = [
    key for section in guide_config["sections"] for key in section["items"]
]
leatherworking_items = {
    key: merged_item(config, key) for key in leatherworking_keys
}
preserved_keys = {
    key
    for key, item in leatherworking_items.items()
    if item.get("price_evidence_ref", "").startswith(MATERIAL_PREFIX)
}
reviewed_keys = set(leatherworking_keys) - preserved_keys

assert len(leatherworking_keys) == len(set(leatherworking_keys)) == 490
assert len(reviewed_keys) == 476
assert len(preserved_keys) == 14
assert set(evidence["items"]) == {
    str(int(leatherworking_items[key]["item_id"])) for key in reviewed_keys
}
assert {record["canonical_key"] for record in evidence["items"].values()} == reviewed_keys

summary = evidence["summary"]
assert evidence["method"] == "Evidence Pricing"
assert evidence["model_version"] == "leatherworking-evidence-pricing-v1"
assert summary["items_reviewed"] == 476
assert summary["preserved_material_intermediates"] == 14
assert summary["view_counts"] == EXPECTED_VIEWS
assert summary["bands_changed"] == 473
assert summary["completed_sale_items"] == 1
assert summary["medium_confidence_sale_items"] == 0
assert summary["items_seen_on_three_realms"] == 394
assert summary["items_seen_on_two_realms"] == 67
assert summary["items_seen_on_one_realm"] == 9
assert summary["items_seen_on_no_realms"] == 6
assert summary["fetch_failed_observations"] == 0
assert summary["items_retained_for_source_unavailability"] == 0
assert summary["target_changes_over_fifty_percent"] == 128
assert summary["proposals_below_reagent_floor"] == 284
assert summary["targets_raised"] == 231
assert summary["targets_lowered"] == 220
assert summary["targets_unchanged"] == 25
assert summary["decision_counts"] == {
    "cohort-rank-starter-estimate": 472,
    "retain-reviewed-band-insufficient-coverage": 3,
    "sparse-completed-sales-shrunk": 1,
}
assert summary["external_gold_values_copied"] is False
assert evidence["rules"]["active_hellscream_listing_prices_used"] is False
assert evidence["rules"]["external_gold_values_copied"] is False
assert "wait 2, 5, and 10 seconds" in evidence["rules"]["comparison_retry_rule"]
assert evidence["sources"]["comparison_retry_summary"] == {
    "initial_requests": 2856,
    "retry_delays_seconds": [2, 5, 10],
    "retry_rounds_used": 0,
    "final_failed_requests": 0,
}

view_counts = Counter()
for item_id, record in evidence["items"].items():
    key = record["canonical_key"]
    item = leatherworking_items[key]
    proposal = record["proposal"]
    view_counts[record["view"]] += 1
    assert record["external_relative_review"]["realm_count"] in {0, 1, 2, 3}
    assert len(record["source_observations"]) == 6
    assert all(
        "median_buyout_copper" not in observation
        and "economy_scale" not in observation
        for observation in record["source_observations"].values()
    )
    assert proposal["decision"] in {
        "cohort-rank-starter-estimate",
        "retain-reviewed-band-insufficient-coverage",
        "sparse-completed-sales-shrunk",
    }
    if proposal["decision"] == "retain-reviewed-band-insufficient-coverage":
        assert proposal["reviewer_decision"] == "retain"
        assert proposal["proposed_band"] == record["before_band"]
        assert proposal["target_change_copper"] == 0
    else:
        assert proposal["reviewer_decision"] == "accept"
    assert int(item_id) == int(item["item_id"])
    assert key in recipes
    assert int(record["recipe"]["source_spell_id"]) == int(
        recipes[key]["source_spell_id"]
    )
    current = {band: int(item[f"{band}_copper"]) for band in PRICE_BANDS}
    assert current == proposal["proposed_band"]
    assert item["price_strategy"] == "evidence-pricing-market-value"
    assert item["price_evidence_ref"] == f"{EVIDENCE_PREFIX}{item_id}"
assert dict(sorted(view_counts.items())) == EXPECTED_VIEWS

for key in preserved_keys:
    item = leatherworking_items[key]
    item_id = str(int(item["item_id"]))
    assert item_id in material_evidence
    assert item["price_evidence_ref"] == f"{MATERIAL_PREFIX}{item_id}"
    expected = material_evidence[item_id]["proposal"]["proposed_band"]
    assert {
        band: int(item[f"{band}_copper"]) for band in PRICE_BANDS
    } == expected

sparse = [
    record
    for record in evidence["items"].values()
    if record["proposal"]["decision"] == "sparse-completed-sales-shrunk"
]
assert len(sparse) == 1
assert sparse[0]["canonical_key"] == "lw-tough-scorpid-shoulders"
assert sparse[0]["local_completed_sales"]["completed_buyouts"] == 1
assert sparse[0]["proposal"]["direct_sale_weight"] == 0.25

hard = use_audit["canonical_hard_requirements"]
leatherworking_hard = {
    key for key, value in hard.items() if value["skill"] == "Leatherworking"
}
assert leatherworking_hard == {
    "lw-drums-of-war",
    "lw-drums-of-battle",
    "lw-drums-of-speed",
    "lw-drums-of-restoration",
    "lw-drums-of-panic",
}
restricted_sections = [
    section
    for section in guide_config["sections"]
    if section.get("audience") == "profession-restricted"
]
assert len(restricted_sections) == 1
assert set(restricted_sections[0]["items"]) == leatherworking_hard

assert status["updated"] == "2026-08-10"
assert status["current_phase"] == "All three Evidence Pricing phases complete locally; scheduled refreshes next"
assert status["publishing_status"] == "local only — not published"
assert status["guides"]["skinning-leatherworking"]["status"] == "Phase 2 complete locally"
assert status["guides"]["skinning-leatherworking"]["evidence_ref"] == "data/ah-leatherworking-price-evidence.json"
assert "complete — Phase 2 Evidence Pricing, 2026-08-08" in plan
assert "2,856 comparison requests resolved" in plan
assert "Publication status: `local only — not published`" in report
assert "394 on three realms, 67 on two, and 9 on one" in report
assert "All 2,856 individual comparison requests resolved" in report

assert "Updated 2026-08-08" in guide
assert guide.count('id="crafted-leatherworking-pricing-note"') == 1
assert "The Evidence Pricing review found usable relative-rank evidence for 470 finished outputs" in guide
assert len(re.findall(r'class="crafted-recipe-link ', guide)) == 490
assert len(re.findall(r'class="crafted-note-ref"', guide)) == 490
for key in (
    "lw-drums-of-battle",
    "lw-frosthide-leg-armor",
    "lw-mammoth-mining-bag",
    "lw-lightning-infused-leggings",
):
    assert f'data-crafted-key="{key}"' in guide
    assert json.dumps(leatherworking_items[key]["name"], ensure_ascii=False) in search

representative_targets = {
    "29529": 175000,
    "38373": 1950000,
    "49633": 1300000,
    "38347": 850000,
    "45553": 7550000,
    "49900": 68800000,
}
for item_id, target in representative_targets.items():
    assert evidence["items"][item_id]["proposal"]["proposed_band"]["target"] == target

print("Leatherworking Evidence Pricing review is current.")
print(
    "Validated 476 finished-output decisions, 473 changed bands, 3 safeguarded "
    "retains, 14 preserved Phase 1B intermediates, retry metadata, recipes, use, "
    "notes, ordering, and search output."
)
