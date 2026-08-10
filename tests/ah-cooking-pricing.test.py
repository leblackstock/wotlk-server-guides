#!/usr/bin/env python3
"""Validate the completed Cooking Evidence Pricing review."""

from __future__ import annotations

import json
import re
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CRAFTED_PATH = ROOT / "data" / "ah-crafted-sections.json"
RECIPE_PATH = ROOT / "data" / "ah-crafted-recipe-audit.json"
USE_PATH = ROOT / "data" / "ah-profession-use-audit.json"
EVIDENCE_PATH = ROOT / "data" / "ah-cooking-price-evidence.json"
STATUS_PATH = ROOT / "data" / "ah-evidence-pricing-review-status.json"
REPORT_PATH = ROOT / "docs" / "ah-cooking-pricing-review.md"
PLAN_PATH = ROOT / "docs" / "ah-profession-plans" / "cooking.md"
GUIDE_PATH = ROOT / "guides" / "fishing-cooking-materials-ah-price-guide.html"
INDEX_PATH = ROOT / "assets" / "ah-search-index.js"
GUIDE_FILENAME = GUIDE_PATH.name
PRICE_BANDS = ("quick", "target", "high")
EVIDENCE_PREFIX = "data/ah-cooking-price-evidence.json#items/"

EXPECTED_VIEWS = {
    "classic-foods": 82,
    "outland-foods": 30,
    "restricted-feasts": 4,
    "rogue-utility": 1,
    "seasonal-foods": 3,
    "wrath-foods": 42,
}


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def merged_item(config: dict, key: str) -> dict:
    raw = config["catalog"][key]
    return config["catalog_defaults"] | config["price_profiles"][raw["profile"]] | raw


config = load(CRAFTED_PATH)
recipes = load(RECIPE_PATH)["recipes"]
use_audit = load(USE_PATH)
evidence = load(EVIDENCE_PATH)
status = load(STATUS_PATH)
report = REPORT_PATH.read_text(encoding="utf-8")
plan = PLAN_PATH.read_text(encoding="utf-8")
guide = GUIDE_PATH.read_text(encoding="utf-8")
search = INDEX_PATH.read_text(encoding="utf-8")

guide_config = config["guides"][GUIDE_FILENAME]
cooking_keys = [key for section in guide_config["sections"] for key in section["items"]]
cooking_items = {key: merged_item(config, key) for key in cooking_keys}

assert len(cooking_keys) == len(set(cooking_keys)) == 162
assert set(evidence["items"]) == {
    str(int(cooking_items[key]["item_id"])) for key in cooking_keys
}
assert {record["canonical_key"] for record in evidence["items"].values()} == set(
    cooking_keys
)

summary = evidence["summary"]
assert evidence["method"] == "Evidence Pricing"
assert evidence["model_version"] == "cooking-evidence-pricing-v1"
assert summary["items_reviewed"] == 162
assert summary["preserved_material_intermediates"] == 0
assert summary["view_counts"] == EXPECTED_VIEWS
assert summary["bands_changed"] == 162
assert summary["completed_sale_items"] == 0
assert summary["medium_confidence_sale_items"] == 0
assert summary["items_seen_on_three_realms"] == 159
assert summary["items_seen_on_two_realms"] == 3
assert summary["items_seen_on_one_realm"] == 0
assert summary["items_seen_on_no_realms"] == 0
assert summary["fetch_failed_observations"] == 0
assert summary["items_retained_for_source_unavailability"] == 0
assert summary["target_changes_over_fifty_percent"] == 70
assert summary["proposals_below_reagent_floor"] == 50
assert summary["targets_raised"] == 88
assert summary["targets_lowered"] == 71
assert summary["targets_unchanged"] == 3
assert summary["decision_counts"] == {"cohort-rank-starter-estimate": 162}
assert summary["external_gold_values_copied"] is False
assert evidence["rules"]["active_hellscream_listing_prices_used"] is False
assert evidence["rules"]["external_gold_values_copied"] is False
assert "wait 2, 5, and 10 seconds" in evidence["rules"]["comparison_retry_rule"]
assert evidence["sources"]["comparison_retry_summary"] == {
    "initial_requests": 972,
    "retry_delays_seconds": [2, 5, 10],
    "retry_rounds_used": 0,
    "final_failed_requests": 0,
}

view_counts = Counter()
for item_id, record in evidence["items"].items():
    key = record["canonical_key"]
    item = cooking_items[key]
    proposal = record["proposal"]
    view_counts[record["view"]] += 1
    assert record["external_relative_review"]["realm_count"] in {2, 3}
    assert len(record["source_observations"]) == 6
    assert all(
        "median_buyout_copper" not in observation
        and "economy_scale" not in observation
        for observation in record["source_observations"].values()
    )
    assert proposal["decision"] == "cohort-rank-starter-estimate"
    assert proposal["reviewer_decision"] == "accept"
    assert int(item_id) == int(item["item_id"])
    assert key in recipes
    assert int(record["recipe"]["source_spell_id"]) == int(
        recipes[key]["source_spell_id"]
    )
    assert int(record["recipe"]["output_count"]) == int(recipes[key]["output_count"])
    assert record["recipe"]["reagents"] == recipes[key]["reagents"]
    current = {band: int(item[f"{band}_copper"]) for band in PRICE_BANDS}
    assert current == proposal["proposed_band"]
    assert item["price_strategy"] == "evidence-pricing-market-value"
    assert item["price_evidence_ref"] == f"{EVIDENCE_PREFIX}{item_id}"
assert dict(sorted(view_counts.items())) == EXPECTED_VIEWS

hard = use_audit["canonical_hard_requirements"]
cooking_hard = {key for key, value in hard.items() if value["skill"] == "Cooking"}
assert cooking_hard == {
    "cook-great-feast",
    "cook-fish-feast",
    "cook-gigantic-feast",
    "cook-small-feast",
}
restricted_sections = [
    section
    for section in guide_config["sections"]
    if section.get("audience") == "profession-restricted"
]
assert len(restricted_sections) == 1
assert set(restricted_sections[0]["items"]) == cooking_hard
class_sections = [
    section
    for section in guide_config["sections"]
    if section.get("audience") == "class-restricted"
]
assert len(class_sections) == 1
assert class_sections[0]["items"] == ["cook-thistle-tea"]
assert use_audit["canonical_profession_audience"]["cook-thistle-tea"]["audience"] == "Rogue"

assert status["updated"] == "2026-08-10"
assert status["current_phase"] == "All three Evidence Pricing phases complete locally; scheduled refreshes next"
assert status["publishing_status"] == "local only — not published"
assert status["guides"]["fishing-cooking"]["status"] == "Phase 2 complete locally"
assert status["guides"]["fishing-cooking"]["evidence_ref"] == EVIDENCE_PATH.relative_to(ROOT).as_posix()
assert "complete — Phase 2 Evidence Pricing, 2026-08-08" in plan
assert "All 972 comparison requests resolved" in plan
assert "Publication status: `local only — not published`" in report
assert "159 on three realms, 3 on two, and 0 on one" in report
assert "All 972 individual comparison requests resolved" in report

assert "Updated 2026-08-10" in guide
assert guide.count('id="crafted-cooking-pricing-note"') == 1
assert "usable relative-rank evidence for 162 outputs" in guide
assert len(re.findall(r'class="crafted-recipe-link ', guide)) == 162
assert len(re.findall(r'class="crafted-note-ref"', guide)) == 162
for key in (
    "cook-fish-feast",
    "cook-dragonfin-filet",
    "cook-delicious-chocolate-cake",
    "cook-thistle-tea",
):
    assert f'data-crafted-key="{key}"' in guide
    assert json.dumps(cooking_items[key]["name"], ensure_ascii=False) in search

representative_targets = {
    "33924": 17500,
    "43000": 57000,
    "43015": 122500,
    "34753": 91000,
    "6657": 15000,
    "7676": 12000,
}
for item_id, target in representative_targets.items():
    assert evidence["items"][item_id]["proposal"]["proposed_band"]["target"] == target

print("Cooking Evidence Pricing review is current.")
print(
    "Validated 162 finished-output decisions, 162 changed bands, retry metadata, "
    "exact batch-yield recipes, profession and class restrictions, notes, ordering, "
    "and search output."
)
