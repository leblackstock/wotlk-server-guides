#!/usr/bin/env python3
"""Guard the complete Phase 1B profession-material Evidence Pricing review."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE_PATH = ROOT / "data" / "ah-profession-material-price-evidence.json"
BASELINE_PATH = ROOT / "data" / "ah-price-baselines.json"
CRAFTED_PATH = ROOT / "data" / "ah-crafted-sections.json"
STATUS_PATH = ROOT / "data" / "ah-evidence-pricing-review-status.json"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


subprocess.run(
    [
        sys.executable,
        str(ROOT / "scripts" / "review-ah-gathering-material-prices.py"),
        "--phase",
        "phase1b",
        "--check",
    ],
    cwd=ROOT,
    check=True,
)

evidence = load(EVIDENCE_PATH)
baseline = load(BASELINE_PATH)["items"]
crafted = load(CRAFTED_PATH)["catalog"]
status = load(STATUS_PATH)

assert evidence["method"] == "Evidence Pricing"
assert evidence["model_version"] == "profession-material-evidence-pricing-v1"
assert evidence["scope"]["phase"] == "phase1b"
assert evidence["scope"]["occurrences"] == 506
assert evidence["scope"]["unique_items"] == 423
assert evidence["scope"]["publishing_status"] == "local only — not published"
assert evidence["rules"]["active_hellscream_listing_prices_used"] is False
assert evidence["rules"]["external_gold_values_copied"] is False

summary = evidence["summary"]
assert summary["items_reviewed"] == 423
assert summary["bands_changed"] == 286
assert summary["direct_sale_items"] == 1
assert summary["inherited_phase1a_items"] == 106
assert summary["items_seen_on_three_realms"] == 286
assert summary["target_changes_over_fifty_percent"] == 39
assert summary["external_gold_values_copied"] is False
assert summary["decision_counts"] == {
    "cohort-rank-starter-estimate": 278,
    "deterministic-three-to-one": 7,
    "exact-vendor": 40,
    "inherit-phase1a": 97,
    "sparse-completed-sales-shrunk": 1,
}

three_to_one = {
    "34056": "34055",
    "22447": "22446",
    "10938": "10939",
    "10998": "11082",
    "11134": "11135",
    "11174": "11175",
    "16202": "16203",
}
for child_id, parent_id in three_to_one.items():
    child = evidence["items"][child_id]["proposal"]
    parent = evidence["items"][parent_id]["proposal"]
    assert child["decision"] == "deterministic-three-to-one"
    for band in ("quick", "target", "high"):
        assert child["proposed_band"][band] == round(parent["proposed_band"][band] / 3)

rugged = evidence["items"]["8170"]
assert rugged["name"] == "Rugged Leather"
assert rugged["proposal"]["decision"] == "sparse-completed-sales-shrunk"
assert rugged["proposal"]["direct_weight"] == 0.25
assert rugged["proposal"]["proposed_band"]["target"] == 25_000
assert rugged["proposal"]["confidence"] == "low"

for item_id, record in evidence["items"].items():
    proposal = record["proposal"]
    band = proposal["proposed_band"]
    if record["owner"] == "vendor":
        assert set(band) == {"target"}
        continue
    assert int(band["quick"]) <= int(band["target"]) <= int(band["high"])
    assert record["external_relative_review"]["used_to_set_gold_value"] is False
    for observation in record["source_observations"].values():
        assert "median_buyout_copper" not in observation
        assert "economy_scale" not in observation
    if proposal["decision"] == "inherit-phase1a":
        assert record["before_band"] == band
        continue
    if record["owner"] == "baseline":
        current = baseline[item_id]
        assert {name: int(current[name]) for name in ("quick", "target", "high")} == band
        assert current["evidence_ref"] == (
            f"data/ah-profession-material-price-evidence.json#items/{item_id}"
        )
    elif record["owner"] == "crafted":
        current = crafted[record["canonical_key"]]
        assert {
            name: int(current[f"{name}_copper"])
            for name in ("quick", "target", "high")
        } == band
        assert current["price_strategy"] == "evidence-pricing-market-value"
        assert current["price_evidence_ref"] == (
            f"data/ah-profession-material-price-evidence.json#items/{item_id}"
        )
        if item_id in baseline:
            duplicate = baseline[item_id]
            assert {
                name: int(duplicate[name]) for name in ("quick", "target", "high")
            } == band
            assert duplicate["evidence_ref"] == (
                f"data/ah-profession-material-price-evidence.json#items/{item_id}"
            )

assert status["updated"] == "2026-08-10"
assert status["current_phase"] == (
    "All three Evidence Pricing phases complete locally; scheduled refreshes next"
)
assert status["publishing_status"] == "local only — not published"

for filename in evidence["scope"]["guides"]:
    source = (ROOT / "guides" / filename).read_text(encoding="utf-8")
    expected_date = (
        "2026-08-14"
        if filename
        in {
            "fishing-cooking-materials-ah-price-guide.html",
            "mining-smithing-ah-price-guide.html",
        }
        else "2026-08-10"
    )
    assert f"Updated {expected_date}" in source, filename

print(
    "Validated 423 Phase 1B material items, 286 applied bands, exact 3:1 "
    "essence parity, and sparse-sale shrinkage."
)
