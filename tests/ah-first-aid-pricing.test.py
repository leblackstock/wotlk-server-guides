#!/usr/bin/env python3
"""Validate the completed First Aid Evidence Pricing review."""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CRAFTED_PATH = ROOT / "data" / "ah-crafted-sections.json"
RECIPE_PATH = ROOT / "data" / "ah-crafted-recipe-audit.json"
USE_PATH = ROOT / "data" / "ah-profession-use-audit.json"
EVIDENCE_PATH = ROOT / "data" / "ah-first-aid-price-evidence.json"
STATUS_PATH = ROOT / "data" / "ah-evidence-pricing-review-status.json"
REPORT_PATH = ROOT / "docs" / "ah-first-aid-pricing-review.md"
PLAN_PATH = ROOT / "docs" / "ah-profession-plans" / "first-aid.md"
GUIDE_PATH = ROOT / "guides" / "tailoring-cloth-ah-price-guide.html"
INDEX_PATH = ROOT / "assets" / "ah-search-index.js"
GUIDE_FILENAME = GUIDE_PATH.name
PRICE_BANDS = ("quick", "target", "high")
EVIDENCE_PREFIX = "data/ah-first-aid-price-evidence.json#items/"

EXPECTED_VIEWS = {
    "classic-supplies": 11,
    "general-anti-venoms": 2,
    "outland-bandages": 2,
    "wrath-bandages": 2,
}


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def merged_item(config: dict, key: str) -> dict:
    raw = config["catalog"][key]
    return config.get("catalog_defaults", {}) | config["price_profiles"][raw["profile"]] | raw


config = load(CRAFTED_PATH)
recipes = load(RECIPE_PATH)["recipes"]
use_audit = load(USE_PATH)
evidence = load(EVIDENCE_PATH)
status = load(STATUS_PATH)
report = REPORT_PATH.read_text(encoding="utf-8")
plan = PLAN_PATH.read_text(encoding="utf-8")
guide = GUIDE_PATH.read_text(encoding="utf-8")
search = INDEX_PATH.read_text(encoding="utf-8")

sections = config["guide_supplements"][GUIDE_FILENAME]["prepend_sections"]
first_aid_keys = [key for section in sections for key in section["items"]]
items = {key: merged_item(config, key) for key in first_aid_keys}

assert len(first_aid_keys) == len(set(first_aid_keys)) == 17
assert set(evidence["items"]) == {str(int(items[key]["item_id"])) for key in first_aid_keys}
assert {record["canonical_key"] for record in evidence["items"].values()} == set(first_aid_keys)

summary = evidence["summary"]
assert evidence["method"] == "Evidence Pricing"
assert evidence["model_version"] == "first-aid-evidence-pricing-v1"
assert summary["items_reviewed"] == 17
assert summary["preserved_material_intermediates"] == 0
assert summary["view_counts"] == EXPECTED_VIEWS
assert summary["bands_changed"] == 17
assert summary["completed_sale_items"] == 0
assert summary["medium_confidence_sale_items"] == 0
assert summary["items_seen_on_three_realms"] == 17
assert summary["items_seen_on_two_realms"] == 0
assert summary["items_seen_on_one_realm"] == 0
assert summary["items_seen_on_no_realms"] == 0
assert summary["fetch_failed_observations"] == 0
assert summary["items_retained_for_source_unavailability"] == 0
assert summary["target_changes_over_fifty_percent"] == 5
assert summary["proposals_below_reagent_floor"] == 4
assert summary["targets_raised"] == 9
assert summary["targets_lowered"] == 7
assert summary["targets_unchanged"] == 1
assert summary["decision_counts"] == {"cohort-rank-starter-estimate": 17}
assert summary["external_gold_values_copied"] is False
assert evidence["rules"]["active_hellscream_listing_prices_used"] is False
assert evidence["rules"]["external_gold_values_copied"] is False
assert "wait 2, 5, and 10 seconds" in evidence["rules"]["comparison_retry_rule"]
assert evidence["sources"]["comparison_retry_summary"] == {
    "initial_requests": 102,
    "retry_delays_seconds": [2, 5, 10],
    "retry_rounds_used": 0,
    "final_failed_requests": 0,
}

view_counts = Counter()
for item_id, record in evidence["items"].items():
    key = record["canonical_key"]
    item = items[key]
    proposal = record["proposal"]
    view_counts[record["view"]] += 1
    assert record["external_relative_review"]["realm_count"] == 3
    assert len(record["source_observations"]) == 6
    assert all(
        "median_buyout_copper" not in observation
        and "economy_scale" not in observation
        for observation in record["source_observations"].values()
    )
    assert proposal["decision"] == "cohort-rank-starter-estimate"
    assert proposal["reviewer_decision"] == "accept"
    assert key in recipes
    assert int(record["recipe"]["source_spell_id"]) == int(recipes[key]["source_spell_id"])
    assert int(record["recipe"]["output_count"]) == int(recipes[key]["output_count"])
    assert record["recipe"]["reagents"] == recipes[key]["reagents"]
    assert {band: int(item[f"{band}_copper"]) for band in PRICE_BANDS} == proposal["proposed_band"]
    assert item["price_strategy"] == "evidence-pricing-market-value"
    assert item["price_evidence_ref"] == f"{EVIDENCE_PREFIX}{item_id}"
assert dict(sorted(view_counts.items())) == EXPECTED_VIEWS

hard = use_audit["canonical_hard_requirements"]
first_aid_hard = {key for key, value in hard.items() if value["skill"] == "First Aid"}
assert len(first_aid_hard) == 15
assert first_aid_hard == set(first_aid_keys) - {
    "firstaid-anti-venom",
    "firstaid-strong-anti-venom",
}
general = use_audit["canonical_general_use_exceptions"]
assert {key for key in general if key.startswith("firstaid-")} == {
    "firstaid-anti-venom",
    "firstaid-strong-anti-venom",
}

assert status["updated"] == "2026-08-08"
assert status["current_phase"] == "All three Evidence Pricing phases complete locally; scheduled refreshes next"
assert status["publishing_status"] == "local only — not published"
assert status["guides"]["tailoring"]["status"] == "Phase 2 complete locally"
assert status["guides"]["tailoring"]["first_aid_evidence_ref"] == EVIDENCE_PATH.relative_to(ROOT).as_posix()
assert status["guides"]["tailoring"]["first_aid_report_ref"] == REPORT_PATH.relative_to(ROOT).as_posix()
assert "complete — Phase 2 Evidence Pricing, 2026-08-08" in plan
assert "All 102 comparison requests resolved" in plan
assert "Publication status: `local only — not published`" in report
assert "All 102 comparison requests resolved" in report

assert "Updated 2026-08-08" in guide
assert guide.count('id="crafted-tailoring-pricing-note"') == 1
assert "The First Aid review found usable relative-rank evidence for 17 outputs" in guide
assert guide.count('data-crafted-key="firstaid-') == 17
for key in (
    "firstaid-heavy-frostweave-bandage",
    "firstaid-powerful-anti-venom",
    "firstaid-strong-anti-venom",
):
    assert f'data-crafted-key="{key}"' in guide
    assert json.dumps(items[key]["name"], ensure_ascii=False) in search

representative_targets = {
    "6452": 2900,
    "6453": 6100,
    "14530": 1900,
    "19440": 2000,
    "34721": 5400,
    "34722": 11000,
}
for item_id, target in representative_targets.items():
    assert evidence["items"][item_id]["proposal"]["proposed_band"]["target"] == target

print("First Aid Evidence Pricing review is current.")
print(
    "Validated 17 finished-output decisions, 17 changed bands, retry metadata, "
    "output-aware recipes, profession restrictions, notes, ordering, and search output."
)
