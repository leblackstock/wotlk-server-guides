#!/usr/bin/env python3
"""Validate the completed Tailoring Evidence Pricing review."""

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
EVIDENCE_PATH = ROOT / "data" / "ah-tailoring-price-evidence.json"
STATUS_PATH = ROOT / "data" / "ah-evidence-pricing-review-status.json"
REPORT_PATH = ROOT / "docs" / "ah-tailoring-pricing-review.md"
PLAN_PATH = ROOT / "docs" / "ah-profession-plans" / "tailoring.md"
GUIDE_PATH = ROOT / "guides" / "tailoring-cloth-ah-price-guide.html"
INDEX_PATH = ROOT / "assets" / "ah-search-index.js"
GUIDE_FILENAME = GUIDE_PATH.name
PRICE_BANDS = ("quick", "target", "high")
MATERIAL_PREFIX = "data/ah-profession-material-price-evidence.json#items/"

EXPECTED_VIEWS = {
    "bags": 33,
    "gear": 314,
    "nets": 3,
    "shirts": 30,
    "spellthreads": 8,
    "utility": 1,
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
tailoring_keys = [key for section in guide_config["sections"] for key in section["items"]]
tailoring_items = {key: merged_item(config, key) for key in tailoring_keys}
preserved_keys = {
    key for key, item in tailoring_items.items()
    if item.get("price_evidence_ref", "").startswith(MATERIAL_PREFIX)
}
reviewed_keys = set(tailoring_keys) - preserved_keys
first_aid_keys = {key for key in config["catalog"] if key.startswith("firstaid-")}

assert len(tailoring_keys) == len(set(tailoring_keys)) == 406
assert len(reviewed_keys) == 389
assert len(preserved_keys) == 17
assert len(first_aid_keys) == 17
assert set(evidence["items"]) == {
    str(int(tailoring_items[key]["item_id"])) for key in reviewed_keys
}
assert {record["canonical_key"] for record in evidence["items"].values()} == reviewed_keys

summary = evidence["summary"]
assert evidence["method"] == "Evidence Pricing"
assert evidence["model_version"] == "tailoring-evidence-pricing-v1"
assert summary["items_reviewed"] == 389
assert summary["preserved_material_intermediates"] == 17
assert summary["first_aid_outputs_outside_batch"] == 17
assert summary["view_counts"] == EXPECTED_VIEWS
assert summary["bands_changed"] == 384
assert summary["completed_sale_items"] == 0
assert summary["medium_confidence_sale_items"] == 0
assert summary["items_seen_on_three_realms"] == 331
assert summary["items_seen_on_two_realms"] == 38
assert summary["items_seen_on_one_realm"] == 8
assert summary["items_seen_on_no_realms"] == 12
assert summary["fetch_failed_observations"] == 0
assert summary["items_retained_for_source_unavailability"] == 0
assert summary["target_changes_over_fifty_percent"] == 144
assert summary["proposals_below_reagent_floor"] == 192
assert summary["targets_raised"] == 183
assert summary["targets_lowered"] == 190
assert summary["targets_unchanged"] == 16
assert summary["decision_counts"] == {
    "cohort-rank-starter-estimate": 384,
    "retain-reviewed-band-insufficient-coverage": 5,
}
assert summary["external_gold_values_copied"] is False
assert evidence["rules"]["active_hellscream_listing_prices_used"] is False
assert evidence["rules"]["external_gold_values_copied"] is False
assert evidence["rules"]["first_aid_included"] is False

view_counts = Counter()
for item_id, record in evidence["items"].items():
    key = record["canonical_key"]
    item = tailoring_items[key]
    proposal = record["proposal"]
    view_counts[record["view"]] += 1
    assert record["local_completed_sales"] is None
    assert record["external_relative_review"]["realm_count"] in {0, 1, 2, 3}
    assert len(record["source_observations"]) == 6
    assert all(
        "median_buyout_copper" not in obs and "economy_scale" not in obs
        for obs in record["source_observations"].values()
    )
    assert proposal["decision"] in {
        "cohort-rank-starter-estimate",
        "retain-reviewed-band-insufficient-coverage",
    }
    if proposal["decision"] == "retain-reviewed-band-insufficient-coverage":
        assert proposal["reviewer_decision"] == "retain"
        assert proposal["proposed_band"] == record["before_band"]
        assert proposal["target_change_copper"] == 0
    else:
        assert proposal["reviewer_decision"] == "accept"
    assert int(item_id) == int(item["item_id"])
    assert key in recipes
    assert int(record["recipe"]["source_spell_id"]) == int(recipes[key]["source_spell_id"])
    current = {band: int(item[f"{band}_copper"]) for band in PRICE_BANDS}
    assert current == proposal["proposed_band"]
    assert item["price_strategy"] == "evidence-pricing-market-value"
    assert item["price_evidence_ref"] == f"data/ah-tailoring-price-evidence.json#items/{item_id}"
assert dict(sorted(view_counts.items())) == EXPECTED_VIEWS

for key in preserved_keys:
    item = tailoring_items[key]
    item_id = str(int(item["item_id"]))
    assert item_id in material_evidence
    assert item["price_evidence_ref"] == f"{MATERIAL_PREFIX}{item_id}"
    expected = material_evidence[item_id]["proposal"]["proposed_band"]
    assert {band: int(item[f"{band}_copper"]) for band in PRICE_BANDS} == expected

for key in first_aid_keys:
    item = merged_item(config, key)
    assert not item.get("price_evidence_ref", "").startswith(
        "data/ah-tailoring-price-evidence.json"
    )

hard = use_audit["canonical_hard_requirements"]
tailor_hard = {key for key, value in hard.items() if value["skill"] == "Tailoring"}
assert tailor_hard == {
    "tailor-netherweave-net",
    "tailor-heavy-netherweave-net",
    "tailor-frostweave-net",
    "tailor-flying-carpet",
}
base_tailor_hard = tailor_hard - {"tailor-flying-carpet"}
restricted_sections = [
    section for section in guide_config["sections"]
    if section.get("audience") == "profession-restricted"
]
assert len(restricted_sections) == 1
assert set(restricted_sections[0]["items"]) == base_tailor_hard
supplement_sections = config["guide_supplements"][GUIDE_FILENAME]["prepend_sections"]
carpet_section = next(
    section for section in supplement_sections if section["id"] == "tailor-only-crafted-mount"
)
assert carpet_section["audience"] == "profession-restricted"
assert carpet_section["items"] == ["tailor-flying-carpet"]

assert status["updated"] == "2026-08-10"
assert status["current_phase"] == "All three Evidence Pricing phases complete locally; scheduled refreshes next"
assert status["publishing_status"] == "local only — not published"
assert status["guides"]["tailoring"]["status"] == "Phase 2 complete locally"
assert status["guides"]["tailoring"]["evidence_ref"] == "data/ah-tailoring-price-evidence.json"
assert "complete — Phase 2 plus collectible addendum, 2026-08-10" in plan
assert "all 2,334 comparison requests resolved" in plan
assert "Publication status: `local only — not published`" in report
assert "331 on three realms, 38 on two, and 8 on one" in report
assert "All 2,334 comparison requests resolved" in report

assert "Updated 2026-08-10" in guide
assert 'data-crafted-key="tailor-flying-carpet"' in guide
assert "Requires Tailoring 300 to use." in guide
assert guide.count('id="crafted-tailoring-pricing-note"') == 1
assert "Evidence Pricing and craft diagnostics" in guide
assert "usable relative-rank evidence for 377 finished outputs" in guide
assert len(re.findall(r'class="crafted-recipe-link ', guide)) == 424
assert len(re.findall(r'class="crafted-note-ref"', guide)) == 424
for key in ("tailor-frostweave-bag", "tailor-brilliant-spellthread", "tailor-gordok-ogre-suit"):
    assert f'data-crafted-key="{key}"' in guide
    assert json.dumps(tailoring_items[key]["name"], ensure_ascii=False) in search
assert evidence["items"]["21841"]["proposal"]["proposed_band"]["target"] == 442500
assert evidence["items"]["2576"]["proposal"]["proposed_band"]["target"] == 11000

print("Tailoring Evidence Pricing review is current.")
print(
    "Validated 389 finished-output decisions, 384 changed bands, 5 safeguarded retains, "
    "17 preserved Phase 1B intermediates, 17 separately Evidence-priced First Aid outputs, recipes, use, notes, ordering, and search output."
)
