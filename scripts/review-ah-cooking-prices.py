#!/usr/bin/env python3
"""Review Cooking finished-output prices with Evidence Pricing."""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
LEATHERWORKING_REVIEW_PATH = ROOT / "scripts" / "review-ah-leatherworking-prices.py"
EVIDENCE_PATH = ROOT / "data" / "ah-cooking-price-evidence.json"
REPORT_PATH = ROOT / "docs" / "ah-cooking-pricing-review.md"
GUIDE_FILENAME = "fishing-cooking-materials-ah-price-guide.html"
MODEL_VERSION = "cooking-evidence-pricing-v1"
PROFESSION = "Cooking"
TOTAL_OUTPUTS = 162

VIEW_BY_SECTION = {
    "Cook-required feasts": "restricted-feasts",
    "Wrath stat-bonus and dual-recovery foods": "wrath-foods",
    "Wrath recovery foods and drinks": "wrath-foods",
    "Wrath pet, tracking, and critter utility": "wrath-foods",
    "Wrath achievement and novelty foods": "wrath-foods",
    "Outland stat-bonus and dual-recovery foods": "outland-foods",
    "Outland recovery and leveling foods": "outland-foods",
    "Outland achievement and utility foods": "outland-foods",
    "Classic combat, stat, and dual-recovery foods": "classic-foods",
    "Classic recovery and leveling foods": "classic-foods",
    "Classic novelty foods": "classic-foods",
    "Seasonal foods and drinks": "seasonal-foods",
    "Rogue-only utility": "rogue-utility",
}

EXPECTED_VIEW_COUNTS = {
    "classic-foods": 82,
    "outland-foods": 30,
    "restricted-feasts": 4,
    "rogue-utility": 1,
    "seasonal-foods": 3,
    "wrath-foods": 42,
}


def load_leatherworking_review():
    spec = importlib.util.spec_from_file_location(
        "ah_cooking_review_base", LEATHERWORKING_REVIEW_PATH
    )
    if spec is None or spec.loader is None:
        raise RuntimeError("Could not load the shared profession Evidence Pricing review")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


SHARED = load_leatherworking_review()
BASE = SHARED.BASE
BASE.EVIDENCE_PATH = EVIDENCE_PATH
BASE.REPORT_PATH = REPORT_PATH
BASE.GUIDE_FILENAME = GUIDE_FILENAME
BASE.MODEL_VERSION = MODEL_VERSION
BASE.VIEW_BY_SECTION = VIEW_BY_SECTION
BASE.EXPECTED_VIEW_COUNTS = EXPECTED_VIEW_COUNTS


def all_cooking_entries(config: dict) -> list[dict]:
    result = []
    seen = set()
    for section in config["guides"][GUIDE_FILENAME]["sections"]:
        title = section["title"]
        for key in section["items"]:
            if key in seen:
                raise ValueError(f"Duplicate Cooking output: {key}")
            seen.add(key)
            item = BASE.merged_item(config, key)
            if item.get("profession") != PROFESSION:
                raise ValueError(f"Non-Cooking output in Cooking catalog: {key}")
            result.append({"key": key, "section": title, "item": item})
    if len(result) != TOTAL_OUTPUTS:
        raise ValueError(f"Cooking inventory drifted: {len(result)} rows")
    return result


def entries(config: dict) -> list[dict]:
    result = []
    for row in all_cooking_entries(config):
        view = VIEW_BY_SECTION.get(row["section"])
        if view is None:
            raise ValueError(f"Unclassified Cooking section: {row['section']}")
        result.append(row | {"view": view})
    counts = Counter(row["view"] for row in result)
    if len(result) != TOTAL_OUTPUTS or counts != EXPECTED_VIEW_COUNTS:
        raise ValueError(
            f"Cooking review boundary drifted: {len(result)} rows, {dict(counts)}"
        )
    return result


BASE.all_tailoring_entries = all_cooking_entries
BASE.entries = entries


def update_summary(evidence: dict) -> None:
    SHARED._base_update_summary(evidence)
    evidence["summary"]["preserved_material_intermediates"] = 0
    evidence["summary"].pop("first_aid_outputs_outside_batch", None)


BASE.update_summary = update_summary


def build_evidence(*, frozen_evidence: dict | None = None) -> dict:
    evidence = SHARED._base_build_evidence(frozen_evidence=frozen_evidence)
    evidence["scope"] = "All 162 auctionable Cooking outputs across 13 sections"
    evidence["rules"].update(
        {
            "preserved_phase1b_intermediates": 0,
            "comparison_retry_rule": (
                "After the initial batch, wait 2, 5, and 10 seconds and retry only "
                "failed comparison requests before recording a final failure."
            ),
            "batch_yield_rule": (
                "Exact recipe cost is divided by the minimum guaranteed food output; "
                "random bonus yields and server-specific procs are excluded."
            ),
        }
    )
    evidence["rules"].pop("first_aid_included", None)
    for record in evidence["items"].values():
        record["proposal"]["reason"] = (
            "Reviewed Cooking Evidence Pricing band. Qualified Hellscream completed "
            "sales set market value when available; sparse sales are shrunk toward a "
            "fixed Hellscream comparable-cohort estimate. External asks set relative "
            "rank only, active Hellscream listings are excluded, and the exact "
            "minimum-output recipe floor remains a separate craftability diagnostic."
        )
    return evidence


BASE.build_evidence = build_evidence


def guide_copy(evidence: dict) -> dict[str, str]:
    summary = evidence["summary"]
    covered = summary["items_reviewed"] - summary["items_seen_on_no_realms"]
    retained = summary["decision_counts"].get(
        "retain-reviewed-band-insufficient-coverage", 0
    ) + summary["items_retained_for_source_unavailability"]
    request_total = summary["items_reviewed"] * len(BASE.COMMON.SOURCE_IDS)
    request_status = (
        f"All {request_total:,} comparison requests resolved"
        if summary["fetch_failed_observations"] == 0
        else (
            f"{summary['fetch_failed_observations']:,} of {request_total:,} comparison "
            "requests still failed after three waited retries"
        )
    )
    sale_status = (
        "no completed Cooking sales were found"
        if summary["completed_sale_items"] == 0
        else (
            f"{summary['completed_sale_items']} outputs had sanitized completed-sale "
            "evidence with confidence safeguards"
        )
    )
    review_sentence = (
        f"The Evidence Pricing review found usable relative-rank evidence for {covered} "
        f"outputs and changed {summary['bands_changed']} bands after coverage safeguards; "
        f"{retained} insufficient-coverage candidates retained their prior values. "
        f"{request_status}; {sale_status}, no current Hellscream listing set price, and "
        "external gold was not copied."
    )
    base_intro = (
        "This catalog covers all 162 distinct auctionable Cooking outputs in the "
        "standard WotLK 3.3.5 recipe list across Wrath, Outland, Classic, and seasonal "
        "content. "
        + review_sentence
        + " Exact 3.3.5 recipe quantities and minimum guaranteed batch yields remain "
        "separate craftability diagnostics. Two Bind-on-Pickup foods and the five "
        "duration-limited Pilgrim's Bounty foods remain excluded; faction-alternate "
        "recipes are consolidated by finished item."
    )
    base_note = (
        review_sentence
        + " Exact 3.3.5 recipe floors use minimum guaranteed output and remain separate "
        "craftability diagnostics: skip batches priced below purchased-input cost. "
        "Bonus procs are not assumed. Food effects, user restrictions, and seasonal "
        "behavior remain item-specific below."
    )
    return {
        "label": "Evidence Pricing and craft diagnostics",
        "base_intro": base_intro,
        "base_note": base_note,
        "combined_intro": base_intro,
        "combined_note": base_note,
    }


BASE.guide_copy = guide_copy


def render_report(evidence: dict) -> str:
    summary = evidence["summary"]
    coverage_text = BASE.coverage_review_text(summary)
    request_total = summary["items_reviewed"] * len(BASE.COMMON.SOURCE_IDS)
    lines = [
        "# Cooking Evidence Pricing Review",
        "",
        f"- Reviewed: `{evidence['refreshed']}`",
        f"- Scope: `{evidence['scope']}`",
        f"- Outputs reviewed: `{summary['items_reviewed']}`",
        f"- Price bands changed: `{summary['bands_changed']}`",
        f"- Items with completed-sale evidence: `{summary['completed_sale_items']}`",
        f"- Items seen on all three comparison realms: `{summary['items_seen_on_three_realms']}`",
        f"- Comparison requests that failed after retries: `{summary['fetch_failed_observations']:,}`",
        f"- Manually reviewed Target changes over 50%: `{summary['target_changes_over_fifty_percent']}`",
        f"- Market proposals below at least one exact recipe-floor band: `{summary['proposals_below_reagent_floor']}`",
        "- Active Hellscream listing prices used: `no`",
        "- External gold copied into Hellscream prices: `no`",
        "- Publication status: `local only — not published`",
        "",
        "## Decision",
        "",
        "Finished-food sale value is reviewed separately from exact recipe cost. Qualified Hellscream completed buyouts may set a market band; sparse histories are shrunk toward a fixed comparable-cohort estimate. Current Hellscream listings are excluded. Gold-normalized external observations set relative rank only, while the frozen Hellscream cohort anchor sets the scale.",
        "",
        "Every exact recipe floor uses the minimum guaranteed batch yield. A finished food priced below its floor is not a profitable-craft claim: use cheaper owned inputs or skip that batch.",
        "",
        coverage_text,
        "",
        "## Item decisions",
        "",
        "| View | Section | Item | Old Q / T / H | Recipe floor Q / T / H | Proposed Q / T / H | Target change | Local sales | External coverage | Decision | Confidence | Review |",
        "|---|---|---|---:|---:|---:|---:|---:|---:|---|---|---|",
    ]
    records = sorted(
        evidence["items"].values(),
        key=lambda record: (
            record["view"],
            record["section"],
            -record["proposal"]["proposed_band"]["target"],
            record["name"],
        ),
    )
    for record in records:
        sales = record["local_completed_sales"]
        sales_text = (
            f"{sales['completed_buyouts']} buyouts / {sales['units']} units / "
            f"{sales['distinct_buyers']} buyers / {sales['distinct_days']} days"
            if sales
            else "none"
        )
        coverage = record["external_relative_review"]
        proposal = record["proposal"]
        lines.append(
            "| "
            + " | ".join(
                [
                    record["view"],
                    record["section"],
                    record["name"],
                    BASE.format_band(record["before_band"]),
                    BASE.format_band(record["reagent_floor"]),
                    BASE.format_band(proposal["proposed_band"]),
                    f"{proposal['target_change_percent']:+.2f}%",
                    sales_text,
                    f"{coverage['realm_count']} realms / {coverage['faction_snapshots_present']} factions",
                    proposal["decision"],
                    proposal["confidence"],
                    proposal["reviewer_decision"],
                ]
            )
            + " |"
        )
    lines.extend(["", "## Manual review of Target changes over 50%", ""])
    large = [
        record
        for record in records
        if record["proposal"]["requires_large_change_review"]
    ]
    if not large:
        lines.append("No Target changes exceeded 50%.")
    for record in large:
        proposal = record["proposal"]
        candidate = proposal["model_proposed_band_before_manual_review"]
        lines.append(
            f"- **{record['name']}**: model candidate "
            f"{BASE.format_money(record['before_band']['target'])} → "
            f"{BASE.format_money(candidate['target'])} "
            f"({proposal['model_target_change_percent']:+.2f}%); final "
            f"{BASE.format_money(proposal['proposed_band']['target'])}. Decision: "
            f"`{proposal['reviewer_decision']}`. {proposal['reviewer_note']}"
        )
    request_limit = (
        f"- All {request_total:,} comparison requests resolved in the saved refresh."
        if summary["fetch_failed_observations"] == 0
        else (
            f"- {summary['fetch_failed_observations']:,} of {request_total:,} comparison "
            "requests still failed after three waited retries."
        )
    )
    lines.extend(
        [
            "",
            "## Evidence limits",
            "",
            "- The external source reports listings and listing history, not verified completed sales.",
            request_limit,
            "- External observations set relative rank only; nominal external gold values are not saved or copied.",
            "- Current Hellscream listings are excluded because guide-driven auctions dominate the local market.",
            "- Exact effects, role, user restrictions, feast behavior, achievement use, and seasonal duration remain explicit notes rather than hidden premiums.",
            "",
            "## Reproduction",
            "",
            "```powershell",
            "python scripts/review-ah-cooking-prices.py --check",
            "```",
            "",
            "Publishing is a separate step and is not part of this review.",
            "",
        ]
    )
    return "\n".join(lines)


BASE.render_report = render_report


def write_outputs(evidence: dict) -> None:
    EVIDENCE_PATH.write_text(
        json.dumps(evidence, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    REPORT_PATH.write_text(render_report(evidence), encoding="utf-8", newline="\n")


def sync_section_metadata(evidence: dict) -> dict:
    """Align saved evidence section labels with the canonical Cooking catalog."""
    current = {
        str(int(row["item"]["item_id"])): row
        for row in entries(BASE.load(BASE.CRAFTED_PATH))
    }
    if set(current) != set(evidence["items"]):
        raise ValueError("Cooking evidence inventory drifted during section sync")
    for item_id, record in evidence["items"].items():
        record["section"] = current[item_id]["section"]
        record["view"] = current[item_id]["view"]
    update_summary(evidence)
    return evidence


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--inventory", action="store_true")
    group.add_argument("--refresh", action="store_true")
    group.add_argument("--review", action="store_true")
    group.add_argument("--refresh-dependencies", action="store_true")
    group.add_argument("--sync-sections", action="store_true")
    group.add_argument("--apply", action="store_true")
    group.add_argument("--check", action="store_true")
    args = parser.parse_args()

    if args.inventory:
        rows = entries(BASE.load(BASE.CRAFTED_PATH))
        print(json.dumps(Counter(row["view"] for row in rows), indent=2))
        print(f"reviewed items {len(rows)}")
        return 0
    if args.refresh:
        evidence = build_evidence()
        BASE.validate(evidence, require_applied=False)
        write_outputs(evidence)
        print(json.dumps(evidence["summary"], indent=2))
        return 0
    if args.review:
        evidence = BASE.review_saved_evidence(BASE.load(EVIDENCE_PATH))
        BASE.validate(evidence, require_applied=False)
        write_outputs(evidence)
        print(json.dumps(evidence["summary"], indent=2))
        return 0
    if args.refresh_dependencies:
        evidence = BASE.refresh_dependency_diagnostics(BASE.load(EVIDENCE_PATH))
        BASE.validate(evidence, require_applied=True)
        write_outputs(evidence)
        print("Refreshed Cooking recipe-floor diagnostics without changing prices.")
        return 0
    if args.sync_sections:
        evidence = sync_section_metadata(BASE.load(EVIDENCE_PATH))
        BASE.validate(evidence, require_applied=True)
        write_outputs(evidence)
        print("Synchronized Cooking evidence section labels without changing prices.")
        return 0
    evidence = BASE.load(EVIDENCE_PATH)
    if args.apply:
        BASE.validate(evidence, require_applied=False)
        BASE.apply_catalog(evidence)
        BASE.validate(evidence, require_applied=True)
        print(f"Applied {len(evidence['items'])} reviewed Cooking price bands.")
        return 0
    BASE.validate(evidence, require_applied=True)
    if REPORT_PATH.read_text(encoding="utf-8") != render_report(evidence):
        print("Cooking Evidence Pricing report is stale.", file=sys.stderr)
        return 1
    print("Cooking Evidence Pricing review is current.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
