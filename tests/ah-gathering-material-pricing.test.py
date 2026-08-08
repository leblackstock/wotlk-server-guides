#!/usr/bin/env python3
"""Guard the Phase 1A gathering and material Evidence Pricing review."""

from __future__ import annotations

import json
import subprocess
import sys
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE_PATH = ROOT / "data" / "ah-gathering-material-price-evidence.json"
BASELINE_PATH = ROOT / "data" / "ah-price-baselines.json"
CRAFTED_PATH = ROOT / "data" / "ah-crafted-sections.json"
STATUS_PATH = ROOT / "data" / "ah-evidence-pricing-review-status.json"
REPORT_PATH = ROOT / "docs" / "ah-gathering-material-pricing-review.md"
BLACKSMITHING_EVIDENCE_PATH = ROOT / "data" / "ah-blacksmithing-price-evidence.json"
PRICE_BANDS = ("quick", "target", "high")


subprocess.run(
    [sys.executable, "scripts/review-ah-gathering-material-prices.py", "--check"],
    cwd=ROOT,
    check=True,
)
subprocess.run(
    [sys.executable, "scripts/audit-ah-crafted-prices.py", "--check"],
    cwd=ROOT,
    check=True,
)

evidence_text = EVIDENCE_PATH.read_text(encoding="utf-8")
evidence = json.loads(evidence_text)
baseline = json.loads(BASELINE_PATH.read_text(encoding="utf-8"))["items"]
crafted = json.loads(CRAFTED_PATH.read_text(encoding="utf-8"))
status = json.loads(STATUS_PATH.read_text(encoding="utf-8"))
blacksmithing_evidence = json.loads(
    BLACKSMITHING_EVIDENCE_PATH.read_text(encoding="utf-8")
)["items"]

assert evidence["method"] == "Evidence Pricing"
assert evidence["model_version"] == "gathering-material-evidence-pricing-v2"
assert evidence["scope"]["occurrences"] == 198
assert evidence["summary"]["items_reviewed"] == 189
assert evidence["summary"]["bands_changed"] == 149
assert evidence["summary"]["direct_sale_items"] == 6
assert evidence["summary"]["items_seen_on_three_realms"] == 179
assert evidence["summary"]["target_changes_over_fifty_percent"] == 31
assert evidence["rules"]["active_hellscream_listing_prices_used"] is False
assert evidence["summary"]["external_gold_values_copied"] is False
assert evidence["scope"]["application_status"] == "applied locally"

expected_decisions = {
    "cohort-rank-starter-estimate": 130,
    "deterministic-ten-to-one": 13,
    "direct-completed-sales": 6,
    "exact-vendor": 9,
    "retain-reviewed-band": 31,
}
assert evidence["summary"]["decision_counts"] == expected_decisions
assert Counter(
    record["proposal"]["decision"] for record in evidence["items"].values()
) == expected_decisions

direct_ids = {
    int(item_id)
    for item_id, record in evidence["items"].items()
    if record["local_completed_sales"]
}
assert direct_ids == {2770, 7912, 21886, 22452, 36909, 36912}

for item_id, record in evidence["items"].items():
    proposal = record["proposal"]
    band = proposal["proposed_band"]
    assert record["pricing_unit"] == "per item"
    assert record["measured_acquisition_evidence"] is None
    assert proposal["reviewer_decision"] in {"accept", "retain fallback"}
    if record["owner"] == "vendor":
        assert set(band) == {"target"}
        assert band == record["before_band"]
        continue
    assert band["quick"] <= band["target"] <= band["high"]
    if abs(proposal["target_change_percent"]) > 50:
        assert proposal["reviewer_decision"] == "accept"
        assert proposal["reviewer_note"]
    if record["owner"] == "baseline":
        current = baseline[item_id]
        assert {name: int(current[name]) for name in PRICE_BANDS} == band
        assert current["evidence_ref"].endswith("#items/" + item_id)
    else:
        current = crafted["catalog"][record["canonical_key"]]
        current_band = {
            name: int(current[f"{name}_copper"]) for name in PRICE_BANDS
        }
        successor = blacksmithing_evidence.get(item_id)
        if successor:
            assert current_band == successor["proposal"]["proposed_band"]
        else:
            assert current_band == band
        assert current["price_strategy"] == "evidence-pricing-market-value"
        if successor:
            assert current["price_evidence_ref"] == (
                f"data/ah-blacksmithing-price-evidence.json#items/{item_id}"
            )
        else:
            assert current["price_evidence_ref"].endswith("#items/" + item_id)
    for observation in record.get("source_observations", {}).values():
        assert "median_buyout_copper" not in observation
        assert "economy_scale" not in observation

for item_id, record in evidence["items"].items():
    proposal = record["proposal"]
    if proposal["decision"] != "deterministic-ten-to-one":
        continue
    parent = evidence["items"][str(proposal["parent_item_id"])]["proposal"]
    assert proposal["proposed_band"] == {
        name: max(1, round(parent["proposed_band"][name] / 10))
        for name in PRICE_BANDS
    }

assert crafted["pricing_policy"]["preserve_unreviewed_market_prices"] is True
assert "LEBLACKSTOCK" not in evidence_text
assert "D:\\Hellscream WoW" not in evidence_text
assert '"buyer":' not in evidence_text
assert '"seller":' not in evidence_text
assert "normalized_ask_ratio" not in evidence_text

assert len(status["guides"]) == 18
assert {
    guide_id
    for guide_id, record in status["guides"].items()
    if record["status"] == "applied locally"
} == {"herbalism", "shared-materials"}
assert status["publishing_status"] == "local only — not published"

report = REPORT_PATH.read_text(encoding="utf-8")
assert "Unique items reviewed: `189`" in report
assert "Proposed bands changed: `149`" in report
assert "Manually reviewed Target changes over 50%: `31`" in report
assert "External gold copied into Hellscream prices: `no`" in report

print("Validated the 189-item Phase 1A gathering/material Evidence Pricing review.")
