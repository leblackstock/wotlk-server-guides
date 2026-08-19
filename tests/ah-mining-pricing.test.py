#!/usr/bin/env python3
"""Validate Mining's completed Evidence Pricing coverage."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
STATUS_PATH = ROOT / "data" / "ah-evidence-pricing-review-status.json"
PLAN_PATH = ROOT / "docs" / "ah-profession-plans" / "mining.md"
REPORT_PATH = ROOT / "docs" / "ah-mining-pricing-review.md"
GUIDE_PATH = ROOT / "guides" / "mining-smithing-ah-price-guide.html"

subprocess.run(
    [sys.executable, "scripts/review-ah-mining-prices.py", "--check"],
    cwd=ROOT,
    check=True,
)

status = json.loads(STATUS_PATH.read_text(encoding="utf-8"))
plan = PLAN_PATH.read_text(encoding="utf-8")
report = REPORT_PATH.read_text(encoding="utf-8")
guide = GUIDE_PATH.read_text(encoding="utf-8")

assert status["updated"] == "2026-08-10"
assert status["current_phase"] == "All three Evidence Pricing phases complete locally; scheduled refreshes next"
assert status["publishing_status"] == "local only — not published"
assert status["guides"]["mining-metals"]["status"] == "Phase 2 complete locally"
assert status["guides"]["mining-metals"]["report_ref"] == "docs/ah-mining-pricing-review.md"
assert "complete — Phase 2 Evidence Pricing coverage, 2026-08-08" in plan
assert "No new price was needed during this closeout" in " ".join(plan.split())
assert "Outputs with completed Phase 1A Evidence Pricing: `22`" in report
assert "Exact reversible 10:1 conversions: `2`" in report
assert "New price changes in this closeout: `0`" in report
assert "Publication status: `local only — not published`" in report

assert "Updated 2026-08-19" in guide
assert guide.count('id="crafted-mining-pricing-note"') == 1
assert "Twenty-two bars and alloys retain their completed Phase 1A Evidence Pricing decisions" in guide
assert guide.count('data-crafted-key="mining-') == 24
assert guide.count('class="crafted-recipe-link ') >= 24
assert guide.count('class="crafted-note-ref"') == 24

print("Mining Evidence Pricing coverage is current.")
print(
    "Validated 22 saved Phase 1A market decisions, two exact reversible conversions, "
    "all 24 recipes, notes, ordering, search output, and zero closeout reprices."
)
