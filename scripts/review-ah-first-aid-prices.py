#!/usr/bin/env python3
"""Review First Aid finished-output prices with Evidence Pricing."""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
LEATHERWORKING_REVIEW_PATH = ROOT / "scripts" / "review-ah-leatherworking-prices.py"
EVIDENCE_PATH = ROOT / "data" / "ah-first-aid-price-evidence.json"
REPORT_PATH = ROOT / "docs" / "ah-first-aid-pricing-review.md"
GUIDE_FILENAME = "tailoring-cloth-ah-price-guide.html"
MODEL_VERSION = "first-aid-evidence-pricing-v1"
PROFESSION = "First Aid"
TOTAL_OUTPUTS = 17

VIEW_BY_SECTION = {
    "First Aid-only Wrath bandages": "wrath-bandages",
    "First Aid-only Outland bandages": "outland-bandages",
    "First Aid-only Classic bandages and poison cure": "classic-supplies",
    "General-use anti-venoms": "general-anti-venoms",
}

EXPECTED_VIEW_COUNTS = {
    "classic-supplies": 11,
    "general-anti-venoms": 2,
    "outland-bandages": 2,
    "wrath-bandages": 2,
}


def load_leatherworking_review():
    spec = importlib.util.spec_from_file_location(
        "ah_first_aid_review_base", LEATHERWORKING_REVIEW_PATH
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


def all_first_aid_entries(config: dict) -> list[dict]:
    supplement = config["guide_supplements"][GUIDE_FILENAME]
    result = []
    seen = set()
    for section in supplement["prepend_sections"]:
        title = section["title"]
        for key in section["items"]:
            if key in seen:
                raise ValueError(f"Duplicate First Aid output: {key}")
            seen.add(key)
            item = BASE.merged_item(config, key)
            if item.get("profession") != PROFESSION:
                raise ValueError(f"Non-First Aid output in First Aid catalog: {key}")
            result.append({"key": key, "section": title, "item": item})
    if len(result) != TOTAL_OUTPUTS:
        raise ValueError(f"First Aid inventory drifted: {len(result)} rows")
    return result


def entries(config: dict) -> list[dict]:
    result = []
    for row in all_first_aid_entries(config):
        view = VIEW_BY_SECTION.get(row["section"])
        if view is None:
            raise ValueError(f"Unclassified First Aid section: {row['section']}")
        result.append(row | {"view": view})
    counts = Counter(row["view"] for row in result)
    if len(result) != TOTAL_OUTPUTS or counts != EXPECTED_VIEW_COUNTS:
        raise ValueError(
            f"First Aid review boundary drifted: {len(result)} rows, {dict(counts)}"
        )
    return result


BASE.all_tailoring_entries = all_first_aid_entries
BASE.entries = entries


def update_summary(evidence: dict) -> None:
    SHARED._base_update_summary(evidence)
    evidence["summary"]["preserved_material_intermediates"] = 0
    evidence["summary"].pop("first_aid_outputs_outside_batch", None)


BASE.update_summary = update_summary


def build_evidence(*, frozen_evidence: dict | None = None) -> dict:
    evidence = SHARED._base_build_evidence(frozen_evidence=frozen_evidence)
    evidence["scope"] = "All 17 tradeable First Aid outputs across four sections"
    evidence["rules"].update(
        {
            "preserved_phase1b_intermediates": 0,
            "first_aid_included": True,
            "comparison_retry_rule": (
                "After the initial batch, wait 2, 5, and 10 seconds and retry only "
                "failed comparison requests before recording a final failure."
            ),
            "batch_yield_rule": (
                "Bandages and Powerful Anti-Venom create one finished item; Anti-Venom "
                "and Strong Anti-Venom create three. Exact recipe cost is divided by "
                "the minimum guaranteed output."
            ),
        }
    )
    for record in evidence["items"].values():
        record["proposal"]["reason"] = (
            "Reviewed First Aid Evidence Pricing band. Qualified Hellscream completed "
            "sales set market value when available; sparse sales are shrunk toward a "
            "fixed Hellscream comparable-cohort estimate. External asks set relative "
            "rank only, active Hellscream listings are excluded, and exact per-output "
            "recipe cost remains a separate craftability diagnostic."
        )
    return evidence


BASE.build_evidence = build_evidence


def review_sentence(evidence: dict) -> str:
    summary = evidence["summary"]
    covered = summary["items_reviewed"] - summary["items_seen_on_no_realms"]
    retained = summary["decision_counts"].get(
        "retain-reviewed-band-insufficient-coverage", 0
    ) + summary["items_retained_for_source_unavailability"]
    request_total = summary["items_reviewed"] * len(BASE.COMMON.SOURCE_IDS)
    request_status = (
        f"All {request_total:,} First Aid comparison requests resolved"
        if summary["fetch_failed_observations"] == 0
        else (
            f"{summary['fetch_failed_observations']:,} of {request_total:,} First Aid "
            "comparison requests still failed after three waited retries"
        )
    )
    sale_status = (
        "no completed First Aid sales were found"
        if summary["completed_sale_items"] == 0
        else (
            f"{summary['completed_sale_items']} outputs had sanitized completed-sale "
            "evidence with confidence safeguards"
        )
    )
    return (
        f"The First Aid review found usable relative-rank evidence for {covered} "
        f"outputs and changed {summary['bands_changed']} bands after coverage safeguards; "
        f"{retained} insufficient-coverage candidates retained their prior values. "
        f"{request_status}; {sale_status}."
    )


def guide_copy(evidence: dict) -> dict[str, str]:
    config = BASE.load(BASE.CRAFTED_PATH)
    base_guide = config["guides"][GUIDE_FILENAME]
    first_aid_review = review_sentence(evidence)
    combined_intro = (
        "This shared cloth-market page contains two separately owned catalogs: all "
        "406 distinct tradeable Tailoring outputs plus all 17 tradeable outputs from "
        "the standard WotLK 3.3.5 First Aid spell list. The Tailoring review found "
        "usable relative-rank evidence for 377 finished outputs and changed 384 bands; "
        "five insufficient-coverage candidates retained their prior values. All 2,334 "
        "Tailoring comparison requests resolved. "
        + first_aid_review
        + " External gold was not copied, and active Hellscream listings never set "
        "price. The 17 cloth intermediates retain Phase 1B material evidence. Fifteen "
        "First Aid items require the stated rank, while Anti-Venom and Strong Anti-Venom do not."
    )
    combined_note = (
        "The Tailoring review found usable relative-rank evidence for 377 finished "
        "outputs and changed 384 bands; five insufficient-coverage candidates retained "
        "their prior values. All 2,334 Tailoring comparison requests resolved. "
        + first_aid_review
        + " External gold was not copied, and active Hellscream listings never set "
        "price. Exact 3.3.5 recipe cost stays separate: skip crafts priced below "
        "purchased-input cost. Anti-Venom and Strong Anti-Venom create three; bandages "
        "and Powerful Anti-Venom create one."
    )
    return {
        "label": "Evidence Pricing and craft diagnostics",
        "base_intro": base_guide["intro_description"],
        "base_note": base_guide["shared_note"]["text"],
        "combined_intro": combined_intro,
        "combined_note": combined_note,
    }


BASE.guide_copy = guide_copy


def render_report(evidence: dict) -> str:
    summary = evidence["summary"]
    request_total = summary["items_reviewed"] * len(BASE.COMMON.SOURCE_IDS)
    lines = [
        "# First Aid Evidence Pricing Review",
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
        "Finished First Aid sale value is reviewed separately from exact cloth or venom-sac cost. Qualified Hellscream completed buyouts may set a market band; sparse histories are shrunk toward a fixed comparable-cohort estimate. Current Hellscream listings are excluded. Gold-normalized external observations set relative rank only, while the frozen Hellscream cohort anchor sets the scale.",
        "",
        "Exact recipe floors use guaranteed output: one for every bandage and Powerful Anti-Venom, three for Anti-Venom and Strong Anti-Venom. A finished item below its floor is not a profitable-craft claim.",
        "",
        BASE.coverage_review_text(summary),
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
    large = [record for record in records if record["proposal"]["requires_large_change_review"]]
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
            "- Healing, poison-cleanse rank, user restriction, cooldown, and output quantity remain explicit item notes rather than hidden premiums.",
            "",
            "## Reproduction",
            "",
            "```powershell",
            "python scripts/review-ah-first-aid-prices.py --check",
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


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--inventory", action="store_true")
    group.add_argument("--refresh", action="store_true")
    group.add_argument("--review", action="store_true")
    group.add_argument("--refresh-dependencies", action="store_true")
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
        print("Refreshed First Aid recipe-floor diagnostics without changing prices.")
        return 0
    evidence = BASE.load(EVIDENCE_PATH)
    if args.apply:
        BASE.validate(evidence, require_applied=False)
        BASE.apply_catalog(evidence)
        BASE.validate(evidence, require_applied=True)
        print(f"Applied {len(evidence['items'])} reviewed First Aid price bands.")
        return 0
    BASE.validate(evidence, require_applied=True)
    if REPORT_PATH.read_text(encoding="utf-8") != render_report(evidence):
        print("First Aid Evidence Pricing report is stale.", file=sys.stderr)
        return 1
    print("First Aid Evidence Pricing review is current.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
