#!/usr/bin/env python3
"""Guard the complete Phase 2 Jewelcrafting gem Evidence Pricing review."""

from __future__ import annotations

import json
import subprocess
import sys
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE_PATH = ROOT / "data" / "ah-jewelcrafting-gem-price-evidence.json"
REPORT_PATH = ROOT / "docs" / "ah-jewelcrafting-gem-pricing-review.md"
CATALOG_PATH = ROOT / "data" / "ah-crafted-sections.json"
BASELINE_PATH = ROOT / "data" / "ah-price-baselines.json"
STATUS_PATH = ROOT / "data" / "ah-evidence-pricing-review-status.json"
GEM_GUIDE_PATH = ROOT / "guides" / "jewelcrafting-gems-ah-price-guide.html"
JEWELRY_GUIDE_PATH = ROOT / "guides" / "jewelcrafting-jewelry-ah-price-guide.html"
SEARCH_PATH = ROOT / "assets" / "ah-search-index.js"

subprocess.run(
    [sys.executable, "scripts/review-ah-jewelcrafting-gem-prices.py", "--check"],
    cwd=ROOT,
    check=True,
)

evidence = json.loads(EVIDENCE_PATH.read_text(encoding="utf-8"))
config = json.loads(CATALOG_PATH.read_text(encoding="utf-8"))
baseline = json.loads(BASELINE_PATH.read_text(encoding="utf-8"))["items"]
status = json.loads(STATUS_PATH.read_text(encoding="utf-8"))
summary = evidence["summary"]

assert evidence["method"] == "Evidence Pricing"
assert evidence["model_version"] == "jewelcrafting-gem-evidence-pricing-v1"
assert evidence["dependency_diagnostics_refreshed"] == "2026-08-08"
assert summary == {
    "items_reviewed": 360,
    "sections_reviewed": 38,
    "quality_counts": {"epic": 111, "rare": 146, "uncommon": 103},
    "bands_changed": 360,
    "completed_sale_items": 0,
    "medium_confidence_sale_items": 0,
    "items_seen_on_three_realms": 342,
    "target_changes_over_fifty_percent": 3,
    "large_changes_accepted": 3,
    "large_changes_retained": 0,
    "proposals_below_uncut_floor": 128,
    "decision_counts": {"cohort-rank-starter-estimate": 360},
    "external_gold_values_copied": False,
}
assert evidence["rules"]["active_hellscream_listing_prices_used"] is False
assert evidence["rules"]["external_gold_values_copied"] is False
assert evidence["sources"]["beancounter"]["raw_path_saved"] is False
assert evidence["sources"]["beancounter"]["buyer_names_saved"] is False
assert status["current_phase"] == (
    "All three Evidence Pricing phases complete locally; scheduled refreshes next"
)
assert status["guides"]["jewelcrafting-gems"]["status"] == "Phase 2 complete locally"
assert status["guides"]["jewelcrafting-jewelry"]["status"] == "Phase 2 complete locally"

records = list(evidence["items"].values())
assert len(records) == 360
assert Counter(record["quality"] for record in records) == {
    "rare": 146,
    "epic": 111,
    "uncommon": 103,
}
assert Counter(record["proposal"]["reviewer_decision"] for record in records) == {
    "accept": 360
}
assert all(record["local_completed_sales"] is None for record in records)
assert Counter(record["external_relative_review"]["realm_count"] for record in records) == {
    3: 342,
    2: 18,
}
large = [record for record in records if record["proposal"]["requires_large_change_review"]]
assert {record["name"] for record in large} == {
    "Brutal Earthstorm Diamond",
    "Thundering Skyflare Diamond",
    "Forlorn Skyflare Diamond",
}
assert all(record["external_relative_review"]["realm_count"] == 3 for record in large)
assert all(record["proposal"]["reviewer_decision"] == "accept" for record in large)

for record in records:
    assert record["pricing_unit"] == "per cut gem"
    assert record["sale_gate_type"] == "stackable-cut-gem"
    assert record["uncut_dependency"]["count"] == 1
    assert record["uncut_dependency"]["saved_baseline_present"] is True
    assert record["uncut_dependency"]["opportunity_cost_band"] == record["reagent_floor"]
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
    expected_ref = f"data/ah-jewelcrafting-gem-price-evidence.json#items/{record['item_id']}"
    assert raw["price_evidence_ref"] == expected_ref
    assert "socket market; post singles first" not in raw["row_note"]

duplicate_meta_ids = {41285, 41333, 41401, 41397, 41398, 41380}
assert duplicate_meta_ids <= {record["item_id"] for record in records}
for item_id in duplicate_meta_ids:
    record = evidence["items"][str(item_id)]
    duplicate = baseline[str(item_id)]
    assert {
        band: int(duplicate[band]) for band in ("quick", "target", "high")
    } == record["proposal"]["proposed_band"]
    assert duplicate["evidence_ref"] == (
        f"data/ah-jewelcrafting-gem-price-evidence.json#items/{item_id}"
    )

representative_targets = {
    "jc-delicate-cardinal-ruby": 1_900_000,
    "jc-chaotic-skyflare-diamond": 385_000,
    "jc-brutal-earthstorm-diamond": 520_000,
    "jc-thundering-skyflare-diamond": 397_500,
    "jc-forlorn-skyflare-diamond": 375_000,
    "jc-balanced-dreadstone": 985_000,
    "jc-quick-king-s-amber": 1_250_000,
    "jc-solid-azure-moonstone": 4_100,
}
for key, target in representative_targets.items():
    assert int(config["catalog"][key]["target_copper"]) == target

serialized = EVIDENCE_PATH.read_text(encoding="utf-8")
assert r"D:\Hellscream WoW" not in serialized
assert '"buyer":' not in serialized
assert '"seller":' not in serialized
report = REPORT_PATH.read_text(encoding="utf-8")
assert "Cut gems: `360` across `38` sections" in report
assert "Manually reviewed Target candidates over 50%: `3`" in report
assert "Publication status: `local only — not published`" in report

gem_guide = GEM_GUIDE_PATH.read_text(encoding="utf-8")
jewelry_guide = JEWELRY_GUIDE_PATH.read_text(encoding="utf-8")
assert "Updated 2026-08-06" in gem_guide
assert "Updated 2026-08-06" in jewelry_guide
assert gem_guide.count('class="crafted-recipe-link ') == 360
assert gem_guide.count('class="crafted-note-ref"') == 360
assert "socket market; post singles first" not in gem_guide
assert gem_guide.count("Evidence Pricing and craft diagnostics") >= 1
assert "BoE gear is a slow market; list one at a time." in jewelry_guide
assert config["catalog"]["jc-bloodstone-band"].get("price_evidence_ref") != (
    "data/ah-jewelcrafting-gem-price-evidence.json#items/42336"
)

search = SEARCH_PATH.read_text(encoding="utf-8")
assert '"name":"Delicate Cardinal Ruby"' in search
assert '"target":"190g"' in search

print(
    "Validated all 360 Jewelcrafting gem Evidence Pricing decisions, three "
    "large-change reviews, uncut opportunity costs, six duplicate metas, concise "
    "notes, recipes, and search output."
)
