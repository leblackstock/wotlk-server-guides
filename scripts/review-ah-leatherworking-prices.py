#!/usr/bin/env python3
"""Review Leatherworking finished-output prices with Evidence Pricing."""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE_PATH = ROOT / "scripts" / "review-ah-tailoring-prices.py"
EVIDENCE_PATH = ROOT / "data" / "ah-leatherworking-price-evidence.json"
REPORT_PATH = ROOT / "docs" / "ah-leatherworking-pricing-review.md"
GUIDE_FILENAME = "skinning-leatherworking-materials-ah-price-guide.html"
MODEL_VERSION = "leatherworking-evidence-pricing-v1"
PRICE_BANDS = ("quick", "target", "high")
MATERIAL_EVIDENCE_PREFIX = "data/ah-profession-material-price-evidence.json#items/"
PROFESSION = "Leatherworking"
TOTAL_OUTPUTS = 490
PRESERVED_INTERMEDIATES = 14
REVIEWED_OUTPUTS = 476

VIEW_BY_SECTION = {
    "Leatherworker-only drums": "restricted-drums",
    "Wrath leg armors": "enhancements",
    "Wrath armor kits": "enhancements",
    "General-use raid drums": "enhancements",
    "Wrath profession-material bags": "bags",
    "Wrath bags, quivers, and ammo pouches": "bags",
    "Wrath raid leather gear": "gear",
    "Wrath leveling leather gear": "gear",
    "Wrath raid mail gear": "gear",
    "Wrath leveling mail gear": "gear",
    "Wrath cloaks": "gear",
    "Outland leg armors": "enhancements",
    "Outland armor kits": "enhancements",
    "Outland profession-material bags": "bags",
    "Outland bags, quivers, and ammo pouches": "bags",
    "Outland premium leather gear": "gear",
    "Outland premium mail gear": "gear",
    "Outland cloaks": "gear",
    "Classic armor kits": "enhancements",
    "Classic bags, quivers, and ammo pouches": "bags",
    "Classic premium leather gear": "gear",
    "Classic leveling leather gear": "gear",
    "Classic premium mail gear": "gear",
    "Classic leveling mail gear": "gear",
    "Classic cloaks": "gear",
    "Tradeable Leatherworking utility": "utility",
}

EXPECTED_VIEW_COUNTS = {
    "bags": 19,
    "enhancements": 29,
    "gear": 420,
    "restricted-drums": 5,
    "utility": 3,
}


def load_base():
    spec = importlib.util.spec_from_file_location("ah_leatherworking_review_base", BASE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("Could not load the shared profession Evidence Pricing review")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


BASE = load_base()
BASE.EVIDENCE_PATH = EVIDENCE_PATH
BASE.REPORT_PATH = REPORT_PATH
BASE.GUIDE_FILENAME = GUIDE_FILENAME
BASE.MODEL_VERSION = MODEL_VERSION
BASE.VIEW_BY_SECTION = VIEW_BY_SECTION
BASE.EXPECTED_VIEW_COUNTS = EXPECTED_VIEW_COUNTS


def all_leatherworking_entries(config: dict) -> list[dict]:
    result = []
    seen = set()
    for section in config["guides"][GUIDE_FILENAME]["sections"]:
        title = section["title"]
        for key in section["items"]:
            if key in seen:
                raise ValueError(f"Duplicate Leatherworking output: {key}")
            seen.add(key)
            item = BASE.merged_item(config, key)
            if item.get("profession") != PROFESSION:
                raise ValueError(f"Non-Leatherworking output in Leatherworking catalog: {key}")
            result.append({"key": key, "section": title, "item": item})
    if len(result) != TOTAL_OUTPUTS:
        raise ValueError(f"Leatherworking inventory drifted: {len(result)} rows")
    return result


def entries(config: dict) -> list[dict]:
    result = []
    preserved = []
    for row in all_leatherworking_entries(config):
        if row["item"].get("price_evidence_ref", "").startswith(
            MATERIAL_EVIDENCE_PREFIX
        ):
            preserved.append(row)
            continue
        view = VIEW_BY_SECTION.get(row["section"])
        if view is None:
            raise ValueError(f"Unclassified Leatherworking section: {row['section']}")
        result.append(row | {"view": view})
    counts = Counter(row["view"] for row in result)
    if (
        len(preserved) != PRESERVED_INTERMEDIATES
        or len(result) != REVIEWED_OUTPUTS
        or counts != EXPECTED_VIEW_COUNTS
    ):
        raise ValueError(
            "Leatherworking review boundary drifted: "
            f"{len(result)} reviewed, {len(preserved)} preserved, {dict(counts)}"
        )
    return result


BASE.all_tailoring_entries = all_leatherworking_entries
BASE.entries = entries
_base_update_summary = BASE.update_summary


def update_summary(evidence: dict) -> None:
    _base_update_summary(evidence)
    evidence["summary"]["preserved_material_intermediates"] = PRESERVED_INTERMEDIATES
    evidence["summary"].pop("first_aid_outputs_outside_batch", None)


BASE.update_summary = update_summary
_base_build_evidence = BASE.build_evidence


def build_evidence(*, frozen_evidence: dict | None = None) -> dict:
    evidence = _base_build_evidence(frozen_evidence=frozen_evidence)
    evidence["scope"] = (
        "476 finished Leatherworking outputs; 14 completed Phase 1B leather and "
        "cured-hide intermediates are preserved outside this batch"
    )
    evidence["rules"].update(
        {
            "preserved_phase1b_intermediates": PRESERVED_INTERMEDIATES,
            "comparison_retry_rule": (
                "After the initial batch, wait 2, 5, and 10 seconds and retry only "
                "failed comparison requests before recording a final failure."
            ),
        }
    )
    evidence["rules"].pop("first_aid_included", None)
    for record in evidence["items"].values():
        record["proposal"]["reason"] = (
            "Reviewed Leatherworking Evidence Pricing band. Qualified Hellscream "
            "completed sales set market value when available; sparse sales are shrunk "
            "toward a fixed Hellscream comparable-cohort estimate. External asks set "
            "relative rank only, active Hellscream listings are excluded, and the exact "
            "recipe floor remains a separate craftability diagnostic."
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
    review_sentence = (
        f"The Evidence Pricing review found usable relative-rank evidence for {covered} "
        f"finished outputs and changed {summary['bands_changed']} bands after coverage "
        f"safeguards; {retained} insufficient-coverage candidates retained their prior "
        f"values. {request_status}; no current Hellscream listing set price and external "
        "gold was not copied."
    )
    base_intro = (
        "This complete Horde-first catalog covers all 490 distinct tradeable "
        "Leatherworking outputs in the WotLK 3.3.5 profession data: leather "
        "conversions, armor kits, leg armors, drums, profession bags, quivers, ammo "
        "pouches, utilities, cloaks, and BoE leather/mail gear across Wrath, Outland, "
        "and Classic. "
        + review_sentence
        + " Fourteen leather and cured-hide intermediates retain Phase 1B material "
        "evidence, and exact 3.3.5 recipe floors remain separate craftability diagnostics. Thirty "
        "Bind on Pickup outputs, eight duplicate Alliance-only Trial records, and the "
        "already-canonical Gordok Ogre Suit remain excluded. Self-only fur linings and "
        "leg reinforcements create no tradeable item and remain excluded."
    )
    base_note = (
        review_sentence
        + " Fourteen leather and cured-hide intermediates retain reviewed Phase 1B "
        "material evidence. Exact 3.3.5 recipe floors remain separate craftability "
        "diagnostics: do not craft from purchased inputs when sale value is below cost. "
        "Specialization or rare-pattern access belongs in the row note and never creates "
        "a hidden surcharge."
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
        "# Leatherworking Evidence Pricing Review",
        "",
        f"- Reviewed: `{evidence['refreshed']}`",
        f"- Scope: `{evidence['scope']}`",
        f"- Finished outputs reviewed: `{summary['items_reviewed']}`",
        f"- Phase 1B intermediates preserved: `{summary['preserved_material_intermediates']}`",
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
        "Finished-item sale value is reviewed separately from exact recipe cost. Qualified Hellscream completed buyouts may set a market band; sparse histories are shrunk toward a fixed comparable-cohort estimate. Current Hellscream listings are excluded. Gold-normalized external observations set relative rank only, while the frozen Hellscream cohort anchor sets the scale.",
        "",
        "The 14 leather and cured-hide intermediates retain their completed Phase 1B evidence. A finished item priced below its recipe floor is not a profitable-craft claim: use cheaper owned inputs or skip that craft.",
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
            "- Kit effects, bag capacity, ammo-container type, specialization access, recipe rarity, and slow legacy turnover remain explicit notes rather than hidden premiums.",
            "",
            "## Reproduction",
            "",
            "```powershell",
            "python scripts/review-ah-leatherworking-prices.py --check",
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
        print(f"preserved Phase 1B intermediates {PRESERVED_INTERMEDIATES}")
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
        print("Refreshed Leatherworking recipe-floor diagnostics without changing prices.")
        return 0
    evidence = BASE.load(EVIDENCE_PATH)
    if args.apply:
        BASE.validate(evidence, require_applied=False)
        BASE.apply_catalog(evidence)
        BASE.validate(evidence, require_applied=True)
        print(f"Applied {len(evidence['items'])} reviewed Leatherworking price bands.")
        return 0
    BASE.validate(evidence, require_applied=True)
    if REPORT_PATH.read_text(encoding="utf-8") != render_report(evidence):
        print("Leatherworking Evidence Pricing report is stale.", file=sys.stderr)
        return 1
    print("Leatherworking Evidence Pricing review is current.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
