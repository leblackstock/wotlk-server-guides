#!/usr/bin/env python3
"""Validate Mining's completed Phase 1A Evidence Pricing coverage."""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CRAFTED_PATH = ROOT / "data" / "ah-crafted-sections.json"
RECIPE_PATH = ROOT / "data" / "ah-crafted-recipe-audit.json"
EVIDENCE_PATH = ROOT / "data" / "ah-gathering-material-price-evidence.json"
REPORT_PATH = ROOT / "docs" / "ah-mining-pricing-review.md"
GUIDE_FILENAME = "mining-smithing-ah-price-guide.html"
PRICE_BANDS = ("quick", "target", "high")
EVIDENCE_PREFIX = "data/ah-gathering-material-price-evidence.json#items/"
SHARED_KEYS = {"mining-mote-of-fire", "mining-mote-of-earth"}


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def merged_item(config: dict, key: str) -> dict:
    raw = config["catalog"][key]
    return config.get("catalog_defaults", {}) | config["price_profiles"][raw["profile"]] | raw


def inventory(config: dict) -> list[dict]:
    rows = []
    seen = set()
    for section in config["guides"][GUIDE_FILENAME]["sections"]:
        for key in section["items"]:
            if key in seen:
                raise ValueError(f"Duplicate Mining output: {key}")
            seen.add(key)
            item = merged_item(config, key)
            if item.get("profession") != "Mining":
                raise ValueError(f"Non-Mining output in Mining catalog: {key}")
            rows.append({"key": key, "section": section["title"], "item": item})
    if len(rows) != 24:
        raise ValueError(f"Mining inventory drifted: {len(rows)} rows")
    return rows


def band(item: dict) -> dict[str, int]:
    return {name: int(item[f"{name}_copper"]) for name in PRICE_BANDS}


def summarize() -> tuple[dict, list[dict]]:
    config = load(CRAFTED_PATH)
    evidence = load(EVIDENCE_PATH)
    rows = inventory(config)
    reviewed = []
    shared = []
    for row in rows:
        if row["key"] in SHARED_KEYS:
            shared.append(row)
            continue
        item_id = str(int(row["item"]["item_id"]))
        record = evidence["items"].get(item_id)
        if record is None or record["canonical_key"] != row["key"]:
            raise ValueError(f"{row['key']}: Phase 1A evidence is missing")
        reviewed.append(record)
    below_floor = 0
    for record in reviewed:
        item = merged_item(config, record["canonical_key"])
        proposal = record["proposal"]["proposed_band"]
        floor = {name: int(item["pricing_floor_copper"][name]) for name in PRICE_BANDS}
        if any(int(proposal[name]) < floor[name] for name in PRICE_BANDS):
            below_floor += 1
    deltas = [int(record["proposal"]["target_change_copper"]) for record in reviewed]
    summary = {
        "outputs": len(rows),
        "phase1a_reviewed": len(reviewed),
        "exact_shared_conversions": len(shared),
        "phase1a_bands_changed": sum(
            record["before_band"] != record["proposal"]["proposed_band"]
            for record in reviewed
        ),
        "completed_sale_items": sum(record["local_completed_sales"] is not None for record in reviewed),
        "three_realm_items": sum(
            int(record["external_relative_review"]["realm_coverage"]) == 3
            for record in reviewed
        ),
        "large_target_changes": sum(
            abs(float(record["proposal"]["target_change_percent"])) > 50.0
            for record in reviewed
        ),
        "below_recipe_floor": below_floor,
        "targets_raised": sum(delta > 0 for delta in deltas),
        "targets_lowered": sum(delta < 0 for delta in deltas),
        "targets_unchanged": sum(delta == 0 for delta in deltas),
        "decision_counts": dict(
            sorted(Counter(record["proposal"]["decision"] for record in reviewed).items())
        ),
        "closeout_price_changes": 0,
    }
    return summary, rows


def validate() -> dict:
    config = load(CRAFTED_PATH)
    recipes = load(RECIPE_PATH)["recipes"]
    evidence = load(EVIDENCE_PATH)
    summary, rows = summarize()
    expected = {
        "outputs": 24,
        "phase1a_reviewed": 22,
        "exact_shared_conversions": 2,
        "phase1a_bands_changed": 18,
        "completed_sale_items": 0,
        "three_realm_items": 22,
        "large_target_changes": 6,
        "below_recipe_floor": 5,
        "targets_raised": 7,
        "targets_lowered": 7,
        "targets_unchanged": 8,
        "decision_counts": {
            "cohort-rank-starter-estimate": 18,
            "retain-reviewed-band": 4,
        },
        "closeout_price_changes": 0,
    }
    if summary != expected:
        raise ValueError(f"Mining coverage summary drifted: {summary}")
    for row in rows:
        key = row["key"]
        item = row["item"]
        if key not in recipes:
            raise ValueError(f"{key}: exact recipe is missing")
        if int(recipes[key]["source_spell_id"]) != int(item["source_spell_id"]):
            raise ValueError(f"{key}: recipe spell drifted")
        item_id = str(int(item["item_id"]))
        record = evidence["items"][item_id]
        if key in SHARED_KEYS:
            if item.get("price_strategy") != "shared-market-reference":
                raise ValueError(f"{key}: reversible conversion must share market value")
            if record["proposal"]["decision"] != "deterministic-ten-to-one":
                raise ValueError(f"{key}: deterministic evidence decision drifted")
            if int(recipes[key]["output_count"]) != 10:
                raise ValueError(f"{key}: reversible conversion output drifted")
        else:
            if item.get("price_evidence_ref") != f"{EVIDENCE_PREFIX}{item_id}":
                raise ValueError(f"{key}: Phase 1A evidence reference drifted")
        if band(item) != {name: int(record["proposal"]["proposed_band"][name]) for name in PRICE_BANDS}:
            raise ValueError(f"{key}: applied band differs from saved evidence")
        if record["external_relative_review"].get("used_to_set_gold_value") is not False:
            raise ValueError(f"{key}: external gold leaked into the saved decision")
    return summary


def render_report() -> str:
    evidence = load(EVIDENCE_PATH)
    summary = validate()
    return "\n".join(
        [
            "# Mining Evidence Pricing Coverage Review",
            "",
            "- Reviewed: `2026-08-08`",
            "- Scope: `All 24 Mining-owned outputs across four sections`",
            f"- Outputs with completed Phase 1A Evidence Pricing: `{summary['phase1a_reviewed']}`",
            f"- Exact reversible 10:1 conversions: `{summary['exact_shared_conversions']}`",
            f"- Phase 1A price bands changed: `{summary['phase1a_bands_changed']}`",
            f"- New price changes in this closeout: `{summary['closeout_price_changes']}`",
            f"- Items with completed-sale evidence: `{summary['completed_sale_items']}`",
            f"- Evidence-priced items with all-three-realm coverage: `{summary['three_realm_items']}`",
            f"- Saved Target changes over 50%: `{summary['large_target_changes']}`",
            f"- Market estimates below at least one current recipe-floor band: `{summary['below_recipe_floor']}`",
            "- Active Hellscream listing prices used: `no`",
            "- External gold copied into Hellscream prices: `no`",
            "- Publication status: `local only — not published`",
            "",
            "## Decision",
            "",
            "Mining required a coverage closeout, not a second comparison fetch. The 22 bars and alloys were already reviewed in the Phase 1A gathering/material batch, and their canonical rows still match those saved decisions. Mote of Fire and Mote of Earth remain exact reversible 10:1 conversions tied to their canonical mote values without a convenience markup.",
            "",
            f"The saved Phase 1A snapshot is `{evidence['refreshed']}`. It changed 18 Mining bands: seven Targets rose, seven fell, and eight stayed unchanged. All 22 market-reviewed outputs had three-realm relative-rank coverage. Six Target moves exceeded 50% and retained explicit reviewer acceptance. No completed Mining-output sale history was available.",
            "",
            "Five market estimates fall below at least one current exact recipe-cost band. Those are sale-value estimates, not profitable-smelting claims; the guide keeps the shared instruction to avoid buying inputs for an unprofitable conversion.",
            "",
            "## Reproduction",
            "",
            "```powershell",
            "python scripts/review-ah-mining-prices.py --check",
            "```",
            "",
            "Publishing is a separate step and is not part of this review.",
            "",
        ]
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--write", action="store_true")
    group.add_argument("--check", action="store_true")
    args = parser.parse_args()
    report = render_report()
    if args.write:
        REPORT_PATH.write_text(report, encoding="utf-8", newline="\n")
        print("Wrote the Mining Phase 2 coverage review without changing prices.")
        return 0
    if not REPORT_PATH.exists() or REPORT_PATH.read_text(encoding="utf-8") != report:
        print("Mining coverage report is stale.", file=sys.stderr)
        return 1
    print("Mining Evidence Pricing coverage is current.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
