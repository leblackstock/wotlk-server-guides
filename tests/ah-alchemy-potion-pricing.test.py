#!/usr/bin/env python3
"""Guard the complete Alchemy potion Evidence Pricing review."""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CATALOG_PATH = ROOT / "data" / "ah-crafted-sections.json"
EVIDENCE_PATH = ROOT / "data" / "ah-alchemy-potion-price-evidence.json"
REVIEW_PATH = ROOT / "docs" / "ah-alchemy-potion-pricing-review.md"
RENDERER_PATH = ROOT / "scripts" / "render-ah-shared-sections.py"


subprocess.run(
    [sys.executable, "scripts/review-ah-alchemy-potion-prices.py", "--check"],
    cwd=ROOT,
    check=True,
)

config = json.loads(CATALOG_PATH.read_text(encoding="utf-8"))
evidence = json.loads(EVIDENCE_PATH.read_text(encoding="utf-8"))
assert evidence["method"] == "Evidence Pricing"
assert evidence["summary"]["items_reviewed"] == 84
assert evidence["summary"]["bands_changed"] == 84
assert evidence["summary"]["external_gold_values_copied"] is False
assert len({record["cohort"] for record in evidence["items"].values()}) == 9
assert len(evidence["inputs"]) == 6

reviewed_keys = {record["canonical_key"] for record in evidence["items"].values()}
assert len(reviewed_keys) == 84
for record in evidence["items"].values():
    raw = config["catalog"][record["canonical_key"]]
    assert raw["price_strategy"] == "evidence-pricing-market-value"
    assert {
        band: int(raw[f"{band}_copper"])
        for band in ("quick", "target", "high")
    } == record["proposal"]["proposed_band"]
    assert record["proposal"]["confidence"] == "fallback"
    assert record["external_relative_review"]["used_to_set_gold_value"] is False

for key, raw in config["catalog"].items():
    for field in ("quick_bid_copper", "target_bid_copper", "high_bid_copper"):
        assert field not in raw, (key, field)

expected_targets = {
    "alch-potion-wild-magic": 70_000,
    "alch-runic-mana-potion": 65_000,
    "alch-potion-speed": 60_000,
    "alch-indestructible-potion": 50_000,
    "alch-runic-healing-potion": 30_000,
}
for key, target in expected_targets.items():
    assert config["catalog"][key]["target_copper"] == target

renderer = RENDERER_PATH.read_text(encoding="utf-8")
assert "quick_bid_copper" not in renderer
assert "target_bid_copper" not in renderer
assert "high_bid_copper" not in renderer
assert re.search(r"def target_bid\(target_copper: int\).*?0\.85", renderer, re.DOTALL)

review = REVIEW_PATH.read_text(encoding="utf-8")
assert "Items reviewed: `84`" in review
assert "Buyout bands changed: `84`" in review
assert "External gold copied into Hellscream prices: `no`" in review

print("Validated Evidence Pricing and canonical 85% bids for all 84 Alchemy potions.")
