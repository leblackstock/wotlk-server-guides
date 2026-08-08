#!/usr/bin/env python3
"""Guard the complete Phase 2 Inscription Evidence Pricing review."""

from __future__ import annotations

import json
import subprocess
import sys
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE_PATH = ROOT / "data" / "ah-inscription-price-evidence.json"
MATERIAL_EVIDENCE_PATH = ROOT / "data" / "ah-profession-material-price-evidence.json"
REPORT_PATH = ROOT / "docs" / "ah-inscription-pricing-review.md"
CATALOG_PATH = ROOT / "data" / "ah-crafted-sections.json"
RECIPE_PATH = ROOT / "data" / "ah-crafted-recipe-audit.json"
USE_AUDIT_PATH = ROOT / "data" / "ah-profession-use-audit.json"
BASELINE_PATH = ROOT / "data" / "ah-price-baselines.json"
STATUS_PATH = ROOT / "data" / "ah-evidence-pricing-review-status.json"
GUIDE_PATH = ROOT / "guides" / "inscription-materials-ah-price-guide.html"
SEARCH_PATH = ROOT / "assets" / "ah-search-index.js"
GUIDE_FILENAME = "inscription-materials-ah-price-guide.html"
PRICE_BANDS = ("quick", "target", "high")

subprocess.run(
    [sys.executable, "scripts/review-ah-inscription-prices.py", "--check"],
    cwd=ROOT,
    check=True,
)

evidence = json.loads(EVIDENCE_PATH.read_text(encoding="utf-8"))
materials = json.loads(MATERIAL_EVIDENCE_PATH.read_text(encoding="utf-8"))
config = json.loads(CATALOG_PATH.read_text(encoding="utf-8"))
recipes = json.loads(RECIPE_PATH.read_text(encoding="utf-8"))["recipes"]
use_audit = json.loads(USE_AUDIT_PATH.read_text(encoding="utf-8"))
baseline = json.loads(BASELINE_PATH.read_text(encoding="utf-8"))["items"]
status = json.loads(STATUS_PATH.read_text(encoding="utf-8"))
summary = evidence["summary"]

assert evidence["method"] == "Evidence Pricing"
assert evidence["model_version"] == "inscription-evidence-pricing-v1"
assert evidence["dependency_diagnostics_refreshed"] == "2026-08-08"
assert summary == {
    "items_reviewed": 105,
    "view_counts": {
        "cards": 32,
        "decks": 4,
        "glyphs": 60,
        "scrolls": 6,
        "utility-boe": 3,
    },
    "section_counts": {
        "Crafted buff scrolls": 6,
        "Crafted general-use utility and BoE equipment": 3,
        "Death Knight glyphs": 6,
        "Druid glyphs": 6,
        "Hunter glyphs": 6,
        "Mage glyphs": 6,
        "Paladin glyphs": 6,
        "Priest glyphs": 6,
        "Rogue glyphs": 6,
        "Shaman glyphs": 6,
        "Warlock glyphs": 6,
        "Warrior glyphs": 6,
        "Nobles cards": 8,
        "Chaos cards": 8,
        "Prisms cards": 8,
        "Undeath cards": 8,
        "Completed Northrend decks": 4,
    },
    "bands_changed": 105,
    "completed_sale_items": 0,
    "medium_confidence_sale_items": 0,
    "items_seen_on_three_realms": 105,
    "items_seen_on_two_realms": 0,
    "items_seen_on_one_realm": 0,
    "items_seen_on_no_realms": 0,
    "target_changes_over_fifty_percent": 1,
    "proposals_below_reagent_floor": 2,
    "exact_cards_below_random_roll_cost": 9,
    "decision_counts": {"cohort-rank-starter-estimate": 105},
    "external_gold_values_copied": False,
}
assert evidence["rules"]["active_hellscream_listing_prices_used"] is False
assert evidence["rules"]["external_gold_values_copied"] is False
assert evidence["sources"]["beancounter"]["raw_path_saved"] is False
assert evidence["sources"]["beancounter"]["buyer_names_saved"] is False
assert status["current_phase"] == "All three Evidence Pricing phases complete locally; scheduled refreshes next"
assert status["guides"]["inscription"]["status"] == "Phase 2 complete locally"

guide_sections = config["guides"][GUIDE_FILENAME]["sections"]
guide_keys = [key for section in guide_sections for key in section["items"]]
records = list(evidence["items"].values())
assert len(guide_keys) == 107
assert len(records) == 105
assert Counter(record["view"] for record in records) == {
    "glyphs": 60,
    "cards": 32,
    "scrolls": 6,
    "decks": 4,
    "utility-boe": 3,
}
assert Counter(record["proposal"]["reviewer_decision"] for record in records) == {
    "accept": 105
}
assert all(record["local_completed_sales"] is None for record in records)
large = [record for record in records if record["proposal"]["requires_large_change_review"]]
assert [record["name"] for record in large] == ["Runescroll of Fortitude"]
assert large[0]["external_relative_review"]["realm_count"] == 3
assert large[0]["proposal"]["reviewer_decision"] == "accept"

for record in records:
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
        f"data/ah-inscription-price-evidence.json#items/{record['item_id']}"
    )
    recipe = recipes[record["canonical_key"]]
    assert record["recipe"]["source_spell_id"] == int(recipe["source_spell_id"])
    assert record["recipe"]["output_count"] == int(recipe["output_count"])
    assert record["recipe"]["reagents"] == recipe["reagents"]
    assert record["recipe"]["pricing_rule"] == recipe["pricing_rule"]

cards = [record for record in records if record["view"] == "cards"]
assert len(cards) == 32
assert all(record["recipe"]["source_spell_id"] == 59504 for record in cards)
assert all(record["recipe"]["pricing_rule"] == "random-darkmoon-card" for record in cards)
assert all(record["recipe_diagnostic_kind"] == "random-roll-cost" for record in cards)
assert all(not record["proposal"]["below_reagent_floor_bands"] for record in cards)
assert sum(bool(record["proposal"]["bands_below_random_roll_cost"]) for record in cards) == 9

decks = [record for record in records if record["view"] == "decks"]
assert len(decks) == 4
assert all(record["recipe"]["pricing_rule"] == "complete-eight-card-deck" for record in decks)
assert all(record["recipe_diagnostic_kind"] == "eight-card-opportunity-cost" for record in decks)
item_id_to_key = {int(config["catalog"][key]["item_id"]): key for key in guide_keys}
for record in decks:
    expected_floor = {
        band: sum(
            int(config["catalog"][item_id_to_key[int(reagent["item_id"])]] [f"{band}_copper"])
            * int(reagent["count"])
            for reagent in recipes[record["canonical_key"]]["reagents"]
        )
        for band in PRICE_BANDS
    }
    assert record["reagent_floor"] == expected_floor
below_decks = {record["name"] for record in decks if record["proposal"]["below_reagent_floor_bands"]}
assert below_decks == {"Chaos Deck", "Undeath Deck"}

runescroll = next(record for record in records if record["canonical_key"] == "runescroll-fortitude")
assert runescroll["recipe"]["output_count"] == 5
assert runescroll["proposal"]["proposed_band"] == {
    "quick": 40_500,
    "target": 54_000,
    "high": 81_000,
}

# Preserve the two reviewed vellums and their hard profession-use boundary.
for item_id, key in (("43145", "armor-vellum"), ("43146", "weapon-vellum")):
    raw = config["catalog"][key]
    proposal = materials["items"][item_id]["proposal"]["proposed_band"]
    assert {band: int(raw[f"{band}_copper"]) for band in PRICE_BANDS} == proposal
    assert raw["price_evidence_ref"] == (
        f"data/ah-profession-material-price-evidence.json#items/{item_id}"
    )
    assert key in use_audit["canonical_hard_requirements"]
restricted = next(section for section in guide_sections if section["title"] == "Enchanter-only blank vellums")
assert restricted["audience"] == "profession-restricted"
assert restricted["items"] == ["armor-vellum", "weapon-vellum"]

# Preserve the user's Book of Glyph Mastery estimate and original baseline note.
book = baseline["45912"]
assert tuple(int(book[band]) for band in PRICE_BANDS) == (125_000, 250_000, 600_000)
assert book["source_type"] == "realized-sales-history"
assert book["confidence"] == "low"
assert "2026-08-03" in book["reason"]
assert "150g quick, 300g target, 700g high" in book["reason"]
assert "may be updated if later evidence differs" in book["reason"]

fixed_card_sections = {"Nobles cards", "Chaos cards", "Prisms cards", "Undeath cards"}
rank_prefixes = ["Ace", "Two", "Three", "Four", "Five", "Six", "Seven", "Eight"]
for section in guide_sections:
    if section["title"] in fixed_card_sections:
        assert [config["catalog"][key]["name"].split(" of ", 1)[0] for key in section["items"]] == rank_prefixes
    elif section["title"] != "Enchanter-only blank vellums":
        targets = [int(config["catalog"][key]["target_copper"]) for key in section["items"]]
        assert targets == sorted(targets, reverse=True), section["title"]

representative_targets = {
    "runescroll-fortitude": 54_000,
    "scroll-stamina-viii": 48_500,
    "glyph-death-strike": 145_000,
    "faces-doom": 2_950_000,
    "six-nobles": 1_900_000,
    "nobles-deck": 14_050_000,
    "chaos-deck": 6_750_000,
    "prisms-deck": 11_600_000,
    "undeath-deck": 9_200_000,
}
for key, target in representative_targets.items():
    assert int(config["catalog"][key]["target_copper"]) == target

serialized = EVIDENCE_PATH.read_text(encoding="utf-8")
assert r"D:\Hellscream WoW" not in serialized
assert '"buyer":' not in serialized
assert '"seller":' not in serialized
report = REPORT_PATH.read_text(encoding="utf-8")
assert "Finished outputs: `105`" in report
assert "Manually reviewed Target changes over 50%: `1`" in report
assert "Preserved Book of Glyph Mastery Target: `25g`" in report
assert "Publication status: `local only — not published`" in report

guide = GUIDE_PATH.read_text(encoding="utf-8")
assert "Updated 2026-08-06" in guide
assert guide.count("<strong>* Evidence Pricing and craft diagnostics:</strong>") == 1
assert guide.count('class="crafted-recipe-link ') == 107
assert guide.count('class="crafted-note-ref"') == 107
assert "Darkmoon Card of the North creates one random named card" in guide
assert "active Hellscream asks never set price" in guide
assert "Glyph discovery and Book of Glyph Mastery access are supply constraints" in guide

search = SEARCH_PATH.read_text(encoding="utf-8")
assert '"name":"Runescroll of Fortitude"' in search
assert '"target":"5g 40s"' in search
assert '"name":"Nobles Deck"' in search
assert '"target":"1,405g"' in search
assert '"name":"Book of Glyph Mastery"' in search
assert '"target":"25g"' in search

print(
    "Validated all 107 Inscription crafts: 105 finished-output decisions, two "
    "preserved vellums, the user-set Book baseline, random-card and deck opportunity "
    "cost rules, exact recipes, profession use, ordering, notes, and search output."
)
