#!/usr/bin/env python3
"""Guard the complete Phase 2 Alchemy Evidence Pricing review."""

from __future__ import annotations

import json
import subprocess
import sys
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE_PATH = ROOT / "data" / "ah-alchemy-finished-price-evidence.json"
POTION_EVIDENCE_PATH = ROOT / "data" / "ah-alchemy-potion-price-evidence.json"
MATERIAL_EVIDENCE_PATH = ROOT / "data" / "ah-profession-material-price-evidence.json"
REPORT_PATH = ROOT / "docs" / "ah-alchemy-finished-pricing-review.md"
CATALOG_PATH = ROOT / "data" / "ah-crafted-sections.json"
RECIPE_PATH = ROOT / "data" / "ah-crafted-recipe-audit.json"
USE_AUDIT_PATH = ROOT / "data" / "ah-profession-use-audit.json"
STATUS_PATH = ROOT / "data" / "ah-evidence-pricing-review-status.json"
GUIDE_PATH = ROOT / "guides" / "alchemy-materials-ah-price-guide.html"
SEARCH_PATH = ROOT / "assets" / "ah-search-index.js"
GUIDE_FILENAME = "alchemy-materials-ah-price-guide.html"
PRICE_BANDS = ("quick", "target", "high")

subprocess.run(
    [sys.executable, "scripts/review-ah-alchemy-finished-prices.py", "--check"],
    cwd=ROOT,
    check=True,
)

evidence = json.loads(EVIDENCE_PATH.read_text(encoding="utf-8"))
potions = json.loads(POTION_EVIDENCE_PATH.read_text(encoding="utf-8"))
materials = json.loads(MATERIAL_EVIDENCE_PATH.read_text(encoding="utf-8"))
config = json.loads(CATALOG_PATH.read_text(encoding="utf-8"))
recipes = json.loads(RECIPE_PATH.read_text(encoding="utf-8"))["recipes"]
use_audit = json.loads(USE_AUDIT_PATH.read_text(encoding="utf-8"))
status = json.loads(STATUS_PATH.read_text(encoding="utf-8"))
summary = evidence["summary"]

assert evidence["method"] == "Evidence Pricing"
assert evidence["model_version"] == "alchemy-finished-evidence-pricing-v1"
assert evidence["dependency_diagnostics_refreshed"] == "2026-08-08"
assert summary == {
    "items_reviewed": 98,
    "view_counts": {
        "cauldrons": 5,
        "elixirs": 76,
        "flasks": 16,
        "transmutes": 1,
    },
    "section_counts": {
        "Crafted Wrath flasks": 6,
        "Crafted Wrath elixirs": 17,
        "Crafted Wrath transmutes": 1,
        "Crafted Outland flasks": 6,
        "Crafted Outland elixirs": 19,
        "Crafted Outland protection cauldrons": 5,
        "Crafted Classic flasks": 4,
        "Crafted Classic endgame elixirs": 18,
        "Crafted Classic leveling elixirs": 22,
    },
    "bands_changed": 98,
    "completed_sale_items": 0,
    "medium_confidence_sale_items": 0,
    "items_seen_on_three_realms": 97,
    "items_seen_on_two_realms": 0,
    "items_seen_on_one_realm": 0,
    "items_seen_on_no_realms": 1,
    "target_changes_over_fifty_percent": 20,
    "proposals_below_reagent_floor": 30,
    "decision_counts": {"cohort-rank-starter-estimate": 98},
    "external_gold_values_copied": False,
}
assert evidence["rules"]["active_hellscream_listing_prices_used"] is False
assert evidence["rules"]["external_gold_values_copied"] is False
assert evidence["sources"]["beancounter"]["raw_path_saved"] is False
assert evidence["sources"]["beancounter"]["buyer_names_saved"] is False
assert status["current_phase"] == "All three Evidence Pricing phases complete locally; scheduled refreshes next"
assert status["guides"]["alchemy"]["status"] == "Phase 2 complete locally"

guide_sections = config["guides"][GUIDE_FILENAME]["sections"]
guide_keys = [key for section in guide_sections for key in section["items"]]
guide_id_to_key = {
    str(int(config["catalog"][key]["item_id"])): key for key in guide_keys
}
finished_records = list(evidence["items"].values())
assert len(finished_records) == 98
assert Counter(record["view"] for record in finished_records) == {
    "elixirs": 76,
    "flasks": 16,
    "cauldrons": 5,
    "transmutes": 1,
}
assert Counter(record["proposal"]["reviewer_decision"] for record in finished_records) == {
    "accept": 98
}
assert all(record["local_completed_sales"] is None for record in finished_records)
large = [record for record in finished_records if record["proposal"]["requires_large_change_review"]]
assert len(large) == 20
assert all(record["external_relative_review"]["realm_count"] == 3 for record in large)
assert all(record["proposal"]["reviewer_decision"] == "accept" for record in large)
no_coverage = [record for record in finished_records if record["external_relative_review"]["realm_count"] == 0]
assert [record["name"] for record in no_coverage] == ["Eternal Might"]
assert no_coverage[0]["proposal"]["proposed_band"]["target"] == 450_000

for record in finished_records:
    assert record["external_relative_review"]["used_to_set_gold_value"] is False
    assert len(record["source_observations"]) == 6
    assert all(
        "median_buyout_copper" not in observation and "economy_scale" not in observation
        for observation in record["source_observations"].values()
    )
    raw = config["catalog"][record["canonical_key"]]
    proposal = record["proposal"]["proposed_band"]
    assert {band: int(raw[f"{band}_copper"]) for band in PRICE_BANDS} == proposal
    assert raw["price_strategy"] == "evidence-pricing-market-value"
    assert raw["price_evidence_ref"] == (
        f"data/ah-alchemy-finished-price-evidence.json#items/{record['item_id']}"
    )
    assert record["recipe"] == {
        "source_spell_id": int(recipes[record["canonical_key"]]["source_spell_id"]),
        "output_count": int(recipes[record["canonical_key"]]["output_count"]),
        "reagents": recipes[record["canonical_key"]]["reagents"],
    }

# The companion potion and profession-material reviews are deliberately frozen.
assert len(potions["items"]) == 84
for item_id, record in potions["items"].items():
    raw = config["catalog"][record["canonical_key"]]
    assert {band: int(raw[f"{band}_copper"]) for band in PRICE_BANDS} == record["proposal"]["proposed_band"]
    assert raw["price_strategy"] == "evidence-pricing-market-value"
    assert raw.get("price_evidence_ref") != f"data/ah-alchemy-finished-price-evidence.json#items/{item_id}"

material_ids = set(materials["items"]) & set(guide_id_to_key)
assert len(material_ids) == 24
assert material_ids.isdisjoint(potions["items"])
for item_id in material_ids:
    record = materials["items"][item_id]
    raw = config["catalog"][guide_id_to_key[item_id]]
    assert {band: int(raw[f"{band}_copper"]) for band in PRICE_BANDS} == record["proposal"]["proposed_band"]
    inherited_ref = record["proposal"].get("inherited_evidence_ref")
    if raw.get("price_strategy") == "shared-market-reference":
        assert raw.get("price_evidence_ref") is None
    elif inherited_ref:
        assert raw.get("price_evidence_ref") == inherited_ref
    else:
        assert raw.get("price_evidence_ref") == (
            f"data/ah-profession-material-price-evidence.json#items/{item_id}"
        )

assert len(guide_keys) == 206
assert set(recipes) >= set(guide_keys)
restricted = next(section for section in guide_sections if section["title"] == "Alchemist-only potions")
assert restricted["audience"] == "profession-restricted"
assert restricted["items"] == ["alch-crazy-alchemists-potion", "alch-mad-alchemist-s-potion"]
cauldron_keys = {
    "alch-cauldron-of-major-arcane-protection",
    "alch-cauldron-of-major-fire-protection",
    "alch-cauldron-of-major-frost-protection",
    "alch-cauldron-of-major-nature-protection",
    "alch-cauldron-of-major-shadow-protection",
}
assert cauldron_keys <= set(use_audit["canonical_general_use_exceptions"])
assert all(
    evidence["items"][str(config["catalog"][key]["item_id"])]["pricing_unit"]
    == "per sealed 25-use cauldron"
    for key in cauldron_keys
)

reviewed_sections = {record["section"] for record in finished_records}
for section in guide_sections:
    if section["title"] not in reviewed_sections:
        continue
    targets = [int(config["catalog"][key]["target_copper"]) for key in section["items"]]
    assert targets == sorted(targets, reverse=True), section["title"]

representative_targets = {
    "alch-flask-stoneblood": 667_500,
    "alch-flask-endless-rage": 600_000,
    "alch-lesser-flask-of-resistance": 460_000,
    "alch-cauldron-of-major-frost-protection": 460_000,
    "alch-eternal-might": 450_000,
    "alch-elixir-of-mighty-mageblood": 105_000,
}
for key, target in representative_targets.items():
    assert int(config["catalog"][key]["target_copper"]) == target

serialized = EVIDENCE_PATH.read_text(encoding="utf-8")
assert r"D:\Hellscream WoW" not in serialized
assert '"buyer":' not in serialized
assert '"seller":' not in serialized
report = REPORT_PATH.read_text(encoding="utf-8")
assert "Finished outputs: `98`" in report
assert "Manually reviewed Target changes over 50%: `20`" in report
assert "Publication status: `local only — not published`" in report

guide = GUIDE_PATH.read_text(encoding="utf-8")
assert "Updated 2026-08-10" in guide
assert guide.count("<strong>* Evidence Pricing and craft diagnostics:</strong>") == 1
assert guide.count('class="crafted-recipe-link ') == 206
assert guide.count('class="crafted-note-ref"') == 206
assert "Cauldrons are valued as sealed 25-use items" in guide
assert "active Hellscream asks never set price" in guide
assert "All 206 crafted Alchemy outputs use saved market reviews" in guide

search = SEARCH_PATH.read_text(encoding="utf-8")
assert '"name":"Flask of Stoneblood"' in search
assert '"target":"66g 75s"' in search
assert '"name":"Eternal Might"' in search
assert '"target":"45g"' in search

print(
    "Validated all 206 Alchemy crafts: 98 companion finished-output decisions, "
    "84 preserved potion decisions, 24 preserved material decisions, exact recipes, "
    "profession use, ordering, notes, and search output."
)
