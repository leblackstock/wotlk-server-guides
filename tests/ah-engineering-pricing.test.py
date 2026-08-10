#!/usr/bin/env python3
"""Guard the complete Phase 2 Engineering Evidence Pricing review."""

from __future__ import annotations

import json
import subprocess
import sys
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE_PATH = ROOT / "data" / "ah-engineering-price-evidence.json"
REPORT_PATH = ROOT / "docs" / "ah-engineering-pricing-review.md"
CATALOG_PATH = ROOT / "data" / "ah-crafted-sections.json"
STATUS_PATH = ROOT / "data" / "ah-evidence-pricing-review-status.json"
GUIDE_PATH = ROOT / "guides" / "engineering-materials-ah-price-guide.html"
SEARCH_PATH = ROOT / "assets" / "ah-search-index.js"

subprocess.run(
    [sys.executable, "scripts/review-ah-engineering-prices.py", "--check"],
    cwd=ROOT,
    check=True,
)

evidence = json.loads(EVIDENCE_PATH.read_text(encoding="utf-8"))
config = json.loads(CATALOG_PATH.read_text(encoding="utf-8"))
status = json.loads(STATUS_PATH.read_text(encoding="utf-8"))
summary = evidence["summary"]

assert evidence["method"] == "Evidence Pricing"
assert evidence["model_version"] == "engineering-evidence-pricing-v1"
assert evidence["dependency_diagnostics_refreshed"] == "2026-08-08"
assert summary == {
    "items_reviewed": 55,
    "section_counts": {
        "Northrend crafted Engineering parts": 4,
        "General-use Engineering utility": 2,
        "Engineer-only bombs, sapper charges, and decoys": 5,
        "Ammo": 13,
        "Outland crafted Engineering parts": 7,
        "Classic crafted Engineering parts": 17,
        "Engineer-only tools": 2,
        "Blasting powders": 5,
    },
    "bands_changed": 55,
    "completed_sale_items": 0,
    "medium_confidence_sale_items": 0,
    "items_seen_on_three_realms": 51,
    "target_changes_over_fifty_percent": 11,
    "proposals_below_reagent_floor": 23,
    "decision_counts": {"cohort-rank-starter-estimate": 55},
    "external_gold_values_copied": False,
}
assert evidence["rules"]["active_hellscream_listing_prices_used"] is False
assert evidence["rules"]["external_gold_values_copied"] is False
assert evidence["sources"]["beancounter"]["raw_path_saved"] is False
assert evidence["sources"]["beancounter"]["buyer_names_saved"] is False
assert status["current_phase"] == (
    "All three Evidence Pricing phases complete locally; scheduled refreshes next"
)
assert status["guides"]["engineering"]["status"] == "Phase 2 complete locally"

records = list(evidence["items"].values())
assert len(records) == 55
assert Counter(record["proposal"]["reviewer_decision"] for record in records) == {
    "accept": 55
}
assert all(record["local_completed_sales"] is None for record in records)
large = [record for record in records if record["proposal"]["requires_large_change_review"]]
assert len(large) == 11
assert all(record["external_relative_review"]["realm_count"] == 3 for record in large)
assert all(record["proposal"]["reviewer_decision"] == "accept" for record in large)

for record in records:
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
    assert raw["price_evidence_ref"] == (
        f"data/ah-engineering-price-evidence.json#items/{record['item_id']}"
    )
    basis = int(record["price_basis_quantity"])
    assert record["reagent_floor"] == {
        band: int(raw["pricing_floor_copper"][band]) * basis
        for band in ("quick", "target", "high")
    }

ammo = [record for record in records if record["section"] == "Ammo"]
assert len(ammo) == 13
assert all(record["price_basis_quantity"] == 200 for record in ammo)
assert all(record["pricing_unit"] == "per stated stack of 200" for record in ammo)
assert all(record["sale_gate_type"] == "stackable" for record in ammo)

representative_targets = {
    "eng-handful-of-cobalt-bolts": 29_500,
    "eng-khorium-power-core": 202_500,
    "eng-felsteel-stabilizer": 417_500,
    "eng-handful-of-copper-bolts": 4_700,
    "eng-explosive-decoy": 13_000,
    "eng-arclight-spanner": 10_000,
    "eng-iceblade-arrow": 25_000,
    "eng-crafted-light-shot": 700,
}
for key, target in representative_targets.items():
    assert int(config["catalog"][key]["target_copper"]) == target

serialized = EVIDENCE_PATH.read_text(encoding="utf-8")
assert r"D:\Hellscream WoW" not in serialized
assert '"buyer":' not in serialized
assert '"seller":' not in serialized
report = REPORT_PATH.read_text(encoding="utf-8")
assert "Finished outputs: `55`" in report
assert "Manually reviewed Target changes over 50%: `11`" in report
assert "Publication status: `local only — not published`" in report

guide = GUIDE_PATH.read_text(encoding="utf-8")
assert "Updated 2026-08-10" in guide
assert guide.count("Evidence Pricing and craft floor") >= 1
assert guide.count('class="crafted-recipe-link ') == 64
assert guide.count('class="crafted-note-ref"') == 64
assert guide.count('<span class="ah-price-stack-chip">Stack of 200</span>') == 13
assert "current Hellscream listings never set them" in guide
assert "General-use all-in-one Mining, Skinning, and Blacksmithing tool" in guide
assert "General-use crafted Engineering companions" in guide
assert "Engineer-only crafted flying mounts" in guide
assert "General-use crafted motorcycles" in guide

search = SEARCH_PATH.read_text(encoding="utf-8")
assert '"name":"Khorium Power Core"' in search
assert '"target":"20g 25s"' in search

print(
    "Validated all 55 Engineering Evidence Pricing decisions, 11 large-change "
    "reviews, stack-of-200 ammo normalization, notes, recipes, and search output."
)
