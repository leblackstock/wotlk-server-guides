#!/usr/bin/env python3
"""Review Tailoring finished-output prices with Evidence Pricing."""

from __future__ import annotations

import argparse
import importlib.util
import json
import re
import sys
from collections import Counter
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CRAFTED_PATH = ROOT / "data" / "ah-crafted-sections.json"
BASELINE_PATH = ROOT / "data" / "ah-price-baselines.json"
RECIPE_AUDIT_PATH = ROOT / "data" / "ah-crafted-recipe-audit.json"
MATERIAL_EVIDENCE_PATH = ROOT / "data" / "ah-profession-material-price-evidence.json"
EVIDENCE_PATH = ROOT / "data" / "ah-tailoring-price-evidence.json"
REPORT_PATH = ROOT / "docs" / "ah-tailoring-pricing-review.md"
COMMON_REVIEW_PATH = ROOT / "scripts" / "review-ah-blacksmithing-prices.py"
GUIDE_FILENAME = "tailoring-cloth-ah-price-guide.html"
MODEL_VERSION = "tailoring-evidence-pricing-v1"
PRICE_BANDS = ("quick", "target", "high")
MATERIAL_EVIDENCE_PREFIX = "data/ah-profession-material-price-evidence.json#items/"
ITEM_LEVEL_PATTERN = re.compile(r"item-level\s+(\d+)", re.IGNORECASE)

VIEW_BY_SECTION = {
    "Tailor-only nets": "nets",
    "Wrath bags": "bags",
    "Outland bags": "bags",
    "Classic bags": "bags",
    "Wrath spellthreads": "spellthreads",
    "Outland spellthreads": "spellthreads",
    "Wrath raid cloth gear": "gear",
    "Wrath leveling cloth gear": "gear",
    "Outland epic and premium cloth gear": "gear",
    "Outland leveling cloth gear": "gear",
    "Classic raid and premium cloth gear": "gear",
    "Classic leveling cloth gear": "gear",
    "Cosmetic shirts": "shirts",
    "Tradeable Tailoring utility": "utility",
}

EXPECTED_VIEW_COUNTS = {
    "nets": 3,
    "bags": 33,
    "spellthreads": 8,
    "gear": 314,
    "shirts": 30,
    "utility": 1,
}


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def load_common_review():
    spec = importlib.util.spec_from_file_location("ah_evidence_pricing_common", COMMON_REVIEW_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("Could not load the shared Evidence Pricing implementation")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


COMMON = load_common_review()


def merged_item(config: dict, key: str) -> dict:
    raw = config["catalog"][key]
    return config.get("catalog_defaults", {}) | config["price_profiles"][raw["profile"]] | raw


def all_tailoring_entries(config: dict) -> list[dict]:
    result = []
    seen = set()
    for section in config["guides"][GUIDE_FILENAME]["sections"]:
        title = section["title"]
        for key in section["items"]:
            if key in seen:
                raise ValueError(f"Duplicate Tailoring output: {key}")
            seen.add(key)
            item = merged_item(config, key)
            if item.get("profession") != "Tailoring":
                raise ValueError(f"Non-Tailoring output in Tailoring catalog: {key}")
            result.append({"key": key, "section": title, "item": item})
    if len(result) != 406:
        raise ValueError(f"Tailoring inventory drifted: {len(result)} rows")
    return result


def entries(config: dict) -> list[dict]:
    result = []
    preserved = []
    for row in all_tailoring_entries(config):
        evidence_ref = row["item"].get("price_evidence_ref", "")
        if evidence_ref.startswith(MATERIAL_EVIDENCE_PREFIX):
            preserved.append(row)
            continue
        view = VIEW_BY_SECTION.get(row["section"])
        if view is None:
            raise ValueError(f"Unclassified Tailoring section: {row['section']}")
        result.append(row | {"view": view})
    counts = Counter(row["view"] for row in result)
    if len(preserved) != 17 or len(result) != 389 or counts != EXPECTED_VIEW_COUNTS:
        raise ValueError(
            "Tailoring review boundary drifted: "
            f"{len(result)} reviewed, {len(preserved)} preserved, {dict(counts)}"
        )
    return result


def item_level(item: dict) -> int:
    match = ITEM_LEVEL_PATTERN.search(item.get("detail", ""))
    return int(match.group(1)) if match else 0


def cohort_key(row: dict) -> str:
    item = row["item"]
    view = row["view"]
    if view == "gear":
        return f"{row['section']} | {item['quality']} | {COMMON.level_bucket(item_level(item))}"
    if view == "shirts":
        return f"{row['section']} | {item['quality']}"
    return row["section"]


def is_stackable(item: dict) -> bool:
    return item.get("stack", "1").strip() != "1"


def sale_passes_medium(sales: dict, item: dict) -> bool:
    base_gate = (
        sales["completed_buyouts"] >= 4
        and sales["distinct_buyers"] >= 2
        and sales["distinct_days"] >= 2
        and float(sales.get("largest_buyer_unit_share") or 1.0) <= 0.50
    )
    if not base_gate:
        return False
    return int(sales["units"]) >= 20 if is_stackable(item) else True


def update_summary(evidence: dict) -> None:
    records = list(evidence["items"].values())
    deltas = [record["proposal"]["target_change_copper"] for record in records]
    observations = [
        observation
        for record in records
        for observation in record["source_observations"].values()
    ]
    evidence["summary"] = {
        "items_reviewed": len(records),
        "preserved_material_intermediates": 17,
        "first_aid_outputs_outside_batch": 17,
        "view_counts": dict(sorted(Counter(record["view"] for record in records).items())),
        "section_counts": dict(sorted(Counter(record["section"] for record in records).items())),
        "bands_changed": sum(
            record["before_band"] != record["proposal"]["proposed_band"] for record in records
        ),
        "completed_sale_items": sum(record["local_completed_sales"] is not None for record in records),
        "medium_confidence_sale_items": sum(
            record["proposal"]["confidence"] == "medium" for record in records
        ),
        "items_seen_on_three_realms": sum(
            record["external_relative_review"]["realm_count"] == 3 for record in records
        ),
        "items_seen_on_two_realms": sum(
            record["external_relative_review"]["realm_count"] == 2 for record in records
        ),
        "items_seen_on_one_realm": sum(
            record["external_relative_review"]["realm_count"] == 1 for record in records
        ),
        "items_seen_on_no_realms": sum(
            record["external_relative_review"]["realm_count"] == 0 for record in records
        ),
        "fetch_failed_observations": sum(
            observation.get("fetch_failed") is True for observation in observations
        ),
        "items_retained_for_source_unavailability": sum(
            record["proposal"]["decision"] == "retain-reviewed-band-source-unavailable"
            for record in records
        ),
        "target_changes_over_fifty_percent": sum(
            record["proposal"]["requires_large_change_review"] for record in records
        ),
        "proposals_below_reagent_floor": sum(
            bool(record["proposal"]["below_reagent_floor_bands"]) for record in records
        ),
        "targets_raised": sum(delta > 0 for delta in deltas),
        "targets_lowered": sum(delta < 0 for delta in deltas),
        "targets_unchanged": sum(delta == 0 for delta in deltas),
        "decision_counts": dict(
            sorted(Counter(record["proposal"]["decision"] for record in records).items())
        ),
        "external_gold_values_copied": False,
    }


def apply_source_availability_safeguard(evidence: dict) -> dict:
    """Retain the frozen band when every comparison request failed."""
    for record in evidence["items"].values():
        observations = list(record["source_observations"].values())
        all_fetches_failed = bool(observations) and all(
            observation.get("fetch_failed") is True for observation in observations
        )
        if not all_fetches_failed or record["local_completed_sales"] is not None:
            continue
        proposal = record["proposal"]
        before = record["before_band"]
        candidate = dict(
            proposal.get("model_proposed_band_before_manual_review", proposal["proposed_band"])
        )
        model_change = candidate["target"] / before["target"] - 1.0 if before["target"] else 0.0
        proposal.update(
            proposed_band=dict(before),
            model_proposed_band_before_manual_review=candidate,
            decision="retain-reviewed-band-source-unavailable",
            source_type="frozen-pre-phase2-guide",
            confidence="fallback",
            direct_sale_weight=None,
            target_change_copper=0,
            target_change_percent=0.0,
            model_target_change_percent=round(model_change * 100, 4),
            requires_large_change_review=abs(model_change) > 0.50,
            reviewer_decision="retain",
            reviewer_note=(
                "Retained after evidence review because all six comparison requests failed "
                "and there is no local completed-sale history. Empty external evidence must "
                "not manufacture a new value."
            ),
            below_reagent_floor_bands=[
                band
                for band in PRICE_BANDS
                if before[band] < record["reagent_floor"][band]
            ],
        )
    update_summary(evidence)
    return evidence


def review_saved_evidence(evidence: dict) -> dict:
    evidence = COMMON.review_saved_evidence(evidence)
    return apply_source_availability_safeguard(evidence)


def build_evidence(*, frozen_evidence: dict | None = None) -> dict:
    # Reuse the already-validated fetch, sale-sanitization, normalization, and
    # fixed-anchor ranking primitives; profession boundaries and validation stay local.
    COMMON.GUIDE_FILENAME = GUIDE_FILENAME
    COMMON.EVIDENCE_PATH = EVIDENCE_PATH
    COMMON.MODEL_VERSION = MODEL_VERSION
    if frozen_evidence is None:
        COMMON.entries = entries
    else:
        frozen_bands = {
            record["canonical_key"]: record["before_band"]
            for record in frozen_evidence["items"].values()
        }

        def frozen_entries(config: dict) -> list[dict]:
            rows = entries(config)
            for row in rows:
                item = dict(row["item"])
                for band in PRICE_BANDS:
                    item[f"{band}_copper"] = int(frozen_bands[row["key"]][band])
                row["item"] = item
            return rows

        COMMON.entries = frozen_entries
    COMMON.item_level = item_level
    COMMON.cohort_key = cohort_key
    evidence = COMMON.build_evidence()

    config = load(CRAFTED_PATH)
    row_by_id = {
        int(row["item"]["item_id"]): row for row in entries(config)
    }
    for record in evidence["items"].values():
        item = row_by_id[int(record["item_id"])]["item"]
        record["stack"] = item["stack"]
        proposal = record["proposal"]
        sales = record["local_completed_sales"]
        if sales:
            direct = COMMON.direct_sale_band(sales)
            fallback = proposal["fallback_band_before_sales"]
            if sale_passes_medium(sales, item):
                proposed = direct
                proposal.update(
                    decision="direct-completed-sales",
                    source_type="realized-sales-history",
                    confidence="medium",
                    direct_sale_weight=1.0,
                )
            else:
                weight = (
                    0.50
                    if sales["distinct_buyers"] >= 2 and sales["distinct_days"] >= 2
                    else 0.25
                )
                proposed = COMMON.shrink_sparse_sale(direct, fallback, weight)
                proposal.update(
                    decision="sparse-completed-sales-shrunk",
                    source_type="realized-sales-history-plus-documented-fallback",
                    confidence="low",
                    direct_sale_weight=weight,
                )
            proposal["model_proposed_band_before_manual_review"] = proposed
            proposal["proposed_band"] = proposed
        proposal["reason"] = (
            "Reviewed Tailoring Evidence Pricing band. Qualified Hellscream completed sales "
            "set market value when available; sparse sales are shrunk toward a fixed "
            "Hellscream comparable-cohort estimate. External asks set relative rank only, "
            "active Hellscream listings are excluded, and the exact recipe floor remains a "
            "separate craftability diagnostic."
        )

    evidence["scope"] = (
        "389 finished Tailoring outputs; 17 Phase 1B cloth intermediates and "
        "17 First Aid outputs are preserved outside this batch"
    )
    evidence["rules"] = {
        "active_hellscream_listing_prices_used": False,
        "external_gold_values_copied": False,
        "external_role": "Gold-normalized within-comparable-cohort relative rank only.",
        "gold_scale": "Fixed frozen Hellscream cohort anchors or qualified completed sales.",
        "reagent_floor_role": "Exact audited 3.3.5 recipe cost is a separate craftability diagnostic and does not automatically set market value.",
        "sparse_sale_rule": "Low-confidence completed sales receive 25% weight, or 50% when they span at least two buyers and two UTC days; the balance remains the reviewed cohort fallback.",
        "stackable_medium_gate": "At least 20 units across four completed auctions, two buyers, and two UTC days, with largest-buyer unit share at most 0.50.",
        "boe_medium_gate": "At least four completed buyouts, two buyers, and two UTC days, with largest-buyer unit share at most 0.50.",
        "comparison_retry_rule": "After the initial batch, wait 2, 5, and 10 seconds and retry only failed comparison requests before recording a final failure.",
        "preserved_phase1b_intermediates": 17,
        "first_aid_included": False,
    }
    return review_saved_evidence(evidence)


def retry_coverage_metrics(evidence: dict) -> dict[str, int]:
    records = list(evidence["items"].values())
    realm_counts = [
        int(record["external_relative_review"]["realm_count"])
        for record in records
    ]
    return {
        "realm_support_total": sum(realm_counts),
        "items_with_two_or_more_realms": sum(count >= 2 for count in realm_counts),
        "items_with_no_realms": sum(count == 0 for count in realm_counts),
        "faction_snapshots_present": sum(
            int(record["external_relative_review"]["faction_snapshots_present"])
            for record in records
        ),
        "fetch_failed_observations": int(
            evidence["summary"]["fetch_failed_observations"]
        ),
    }


def retry_improves_coverage(current: dict, candidate: dict) -> tuple[bool, dict]:
    current_metrics = retry_coverage_metrics(current)
    candidate_metrics = retry_coverage_metrics(candidate)
    non_regressing = (
        candidate_metrics["realm_support_total"]
        >= current_metrics["realm_support_total"]
        and candidate_metrics["items_with_two_or_more_realms"]
        >= current_metrics["items_with_two_or_more_realms"]
        and candidate_metrics["items_with_no_realms"]
        <= current_metrics["items_with_no_realms"]
    )
    improved = non_regressing and any(
        (
            candidate_metrics["realm_support_total"]
            > current_metrics["realm_support_total"],
            candidate_metrics["items_with_two_or_more_realms"]
            > current_metrics["items_with_two_or_more_realms"],
            candidate_metrics["items_with_no_realms"]
            < current_metrics["items_with_no_realms"],
            candidate_metrics["faction_snapshots_present"]
            > current_metrics["faction_snapshots_present"],
            candidate_metrics["fetch_failed_observations"]
            < current_metrics["fetch_failed_observations"],
        )
    )
    return improved, {
        "accepted": improved,
        "current": current_metrics,
        "candidate": candidate_metrics,
        "reason": (
            "candidate improved comparison coverage without regressing aggregate realm support"
            if improved
            else "candidate did not improve comparison coverage without regression; current evidence was preserved"
        ),
    }


def format_money(copper: int) -> str:
    return COMMON.format_money(copper)


def format_band(band: dict) -> str:
    return COMMON.format_band(band)


def coverage_review_text(summary: dict) -> str:
    covered = summary["items_reviewed"] - summary["items_seen_on_no_realms"]
    request_total = summary["items_reviewed"] * len(COMMON.SOURCE_IDS)
    if summary["items_retained_for_source_unavailability"] == summary["items_reviewed"]:
        return (
            "All six comparison requests failed for every item in this snapshot. "
            "With no local completed-sale history, the review therefore retains every "
            "frozen finished-output band."
        )
    request_status = (
        f"All {request_total:,} individual comparison requests resolved."
        if summary["fetch_failed_observations"] == 0
        else (
            f"{summary['fetch_failed_observations']:,} of {request_total:,} individual comparison "
            "requests still failed."
        )
    )
    return (
        f"The retry produced usable relative-rank evidence for {covered} outputs: "
        f"{summary['items_seen_on_three_realms']} on three realms, "
        f"{summary['items_seen_on_two_realms']} on two, and "
        f"{summary['items_seen_on_one_realm']} on one; "
        f"{summary['items_seen_on_no_realms']} had no realm coverage. "
        f"{request_status} Coverage weighting and the large-change safeguard were applied "
        "before accepting any band."
    )


def guide_copy(evidence: dict) -> dict[str, str]:
    summary = evidence["summary"]
    covered = summary["items_reviewed"] - summary["items_seen_on_no_realms"]
    request_total = summary["items_reviewed"] * len(COMMON.SOURCE_IDS)
    retained = summary["decision_counts"].get(
        "retain-reviewed-band-insufficient-coverage", 0
    ) + summary["items_retained_for_source_unavailability"]
    request_status = (
        f"All {request_total:,} comparison requests resolved"
        if summary["fetch_failed_observations"] == 0
        else f"{summary['fetch_failed_observations']:,} of {request_total:,} comparison requests still failed"
    )
    review_sentence = (
        f"The latest Evidence Pricing refresh found usable relative-rank evidence for "
        f"{covered} finished outputs and changed {summary['bands_changed']} bands after "
        f"coverage safeguards; {retained} insufficient-coverage candidates retained "
        f"their prior values. {request_status}; no completed Tailoring sales were found, external gold "
        "was not copied, and active Hellscream listings never set price."
    )
    base_intro = (
        "This complete Horde-first catalog covers all 406 distinct tradeable Tailoring "
        "outputs in the WotLK 3.3.5 profession data: bags, spellthreads, nets, cloth "
        "intermediates, cosmetic shirts, utility, and BoE cloth gear across Wrath, "
        "Outland, and Classic. "
        + review_sentence
        + " The 17 cloth intermediates retain Phase 1B material evidence, and exact "
        "recipes remain separate craftability diagnostics. Twelve Bind on Pickup "
        "outputs, the Tailor-only Flying Carpet, four duplicate Alliance-only Trial "
        "records, and self-only applications remain excluded."
    )
    base_note = (
        review_sentence
        + " The 17 cloth intermediates retain reviewed Phase 1B material evidence. "
        "Exact 3.3.5 recipe floors remain separate craftability diagnostics: do not "
        "craft from purchased inputs when sale value is below cost. Specialty-cloth "
        "floors assume one guaranteed output without specialization bonuses."
    )
    combined_intro = (
        "This shared cloth-market page contains two separately owned catalogs: all 406 "
        "distinct tradeable Tailoring outputs plus all 17 tradeable outputs from the "
        "standard WotLK 3.3.5 First Aid spell list. "
        + review_sentence
        + " The 17 cloth intermediates retain Phase 1B material evidence. First Aid "
        "remains outside this batch and retains its exact-recipe pricing. Fifteen First "
        "Aid items require the stated rank, while Anti-Venom and Strong Anti-Venom do not."
    )
    combined_note = (
        review_sentence
        + " The 17 cloth intermediates keep Phase 1B evidence. The exact 3.3.5 recipe "
        "cost stays separate, so skip crafts priced below purchased-input cost. First "
        "Aid remains outside this batch and retains exact per-output craft pricing: "
        "Anti-Venom and Strong Anti-Venom create three, while bandages and Powerful "
        "Anti-Venom create one."
    )
    return {
        "base_intro": base_intro,
        "base_note": base_note,
        "combined_intro": combined_intro,
        "combined_note": combined_note,
    }


def render_report(evidence: dict) -> str:
    summary = evidence["summary"]
    coverage_text = coverage_review_text(summary)
    request_total = summary["items_reviewed"] * len(COMMON.SOURCE_IDS)
    lines = [
        "# Tailoring Evidence Pricing Review",
        "",
        f"- Reviewed: `{evidence['refreshed']}`",
        f"- Scope: `{evidence['scope']}`",
        f"- Finished outputs reviewed: `{summary['items_reviewed']}`",
        f"- Phase 1B cloth intermediates preserved: `{summary['preserved_material_intermediates']}`",
        f"- First Aid outputs outside this batch: `{summary['first_aid_outputs_outside_batch']}`",
        f"- Price bands changed: `{summary['bands_changed']}`",
        f"- Items with completed-sale evidence: `{summary['completed_sale_items']}`",
        f"- Items seen on all three comparison realms: `{summary['items_seen_on_three_realms']}`",
        f"- Comparison requests that failed: `{summary['fetch_failed_observations']:,}`",
        f"- Items retained because every comparison request failed: `{summary['items_retained_for_source_unavailability']}`",
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
        "The 17 cloth intermediates retain their completed Phase 1B evidence. A finished item priced below its recipe floor is not a profitable-craft claim: use cheaper owned inputs or skip that craft. The 17 First Aid outputs sharing the page remain unchanged for their own later review.",
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
                    format_band(record["before_band"]),
                    format_band(record["reagent_floor"]),
                    format_band(proposal["proposed_band"]),
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
            f"- **{record['name']}**: model candidate {format_money(record['before_band']['target'])} → "
            f"{format_money(candidate['target'])} ({proposal['model_target_change_percent']:+.2f}%); "
            f"final {format_money(proposal['proposed_band']['target'])}. Decision: "
            f"`{proposal['reviewer_decision']}`. {proposal['reviewer_note']}"
        )
    lines.extend(
        [
            "",
            "## Evidence limits",
            "",
            "- The external source reports listings and listing history, not verified completed sales.",
            (
                f"- All {request_total:,} comparison requests resolved in the saved refresh; coverage counts and safeguards are recorded per item."
                if summary["fetch_failed_observations"] == 0
                else f"- {summary['fetch_failed_observations']:,} of {request_total:,} comparison requests failed in the saved refresh; coverage counts and safeguards are recorded per item."
            ),
            "- External observations set relative rank only; nominal external gold values are not saved or copied.",
            "- Current Hellscream listings are excluded because guide-driven auctions dominate the local market.",
            "- Bag capacity, spellthread effect, recipe rarity, reputation access, and cloth cooldown behavior remain explicit notes rather than hidden premiums.",
            "",
            "## Reproduction",
            "",
            "```powershell",
            "python scripts/review-ah-tailoring-prices.py --check",
            "```",
            "",
            "Publishing is a separate step and is not part of this review.",
            "",
        ]
    )
    return "\n".join(lines)


def validate(evidence: dict, *, require_applied: bool) -> None:
    config = load(CRAFTED_PATH)
    recipe_audit = load(RECIPE_AUDIT_PATH)["recipes"]
    material_evidence = load(MATERIAL_EVIDENCE_PATH)["items"]
    baseline = load(BASELINE_PATH)["items"]
    reviewed = entries(config)
    preserved = [
        row for row in all_tailoring_entries(config)
        if row["item"].get("price_evidence_ref", "").startswith(MATERIAL_EVIDENCE_PREFIX)
    ]
    keys = {row["key"] for row in reviewed}
    expected_ids = {str(int(row["item"]["item_id"])) for row in reviewed}
    if evidence.get("method") != "Evidence Pricing" or evidence.get("model_version") != MODEL_VERSION:
        raise ValueError("Tailoring evidence method or model is stale")
    if set(evidence.get("items", {})) != expected_ids:
        raise ValueError("Tailoring evidence does not cover all 389 finished outputs")
    if {record["canonical_key"] for record in evidence["items"].values()} != keys:
        raise ValueError("Tailoring canonical-key coverage drifted")
    if evidence["summary"]["view_counts"] != dict(sorted(EXPECTED_VIEW_COUNTS.items())):
        raise ValueError("Tailoring view counts drifted")
    rules = evidence.get("rules", {})
    if rules.get("active_hellscream_listing_prices_used") is not False:
        raise ValueError("Active Hellscream listings must not set Tailoring prices")
    if rules.get("external_gold_values_copied") is not False:
        raise ValueError("External gold must not be copied")

    row_by_key = {row["key"]: row for row in reviewed}
    for row in all_tailoring_entries(config):
        if row["key"] not in recipe_audit:
            raise ValueError(f"{row['key']}: exact recipe is missing")
    for row in preserved:
        item = row["item"]
        item_id = str(int(item["item_id"]))
        if item_id not in material_evidence:
            raise ValueError(f"{item['name']}: Phase 1B material evidence is missing")
        if item["price_evidence_ref"] != f"{MATERIAL_EVIDENCE_PREFIX}{item_id}":
            raise ValueError(f"{item['name']}: Phase 1B evidence reference drifted")

    for record in evidence["items"].values():
        row = row_by_key[record["canonical_key"]]
        item = row["item"]
        floor = {band: int(item["pricing_floor_copper"][band]) for band in PRICE_BANDS}
        if record["reagent_floor"] != floor:
            raise ValueError(f"{record['name']}: saved recipe floor is stale")
        if int(recipe_audit[record["canonical_key"]]["source_spell_id"]) != int(record["recipe"]["source_spell_id"]):
            raise ValueError(f"{record['name']}: saved recipe spell is stale")
        proposal = record["proposal"]
        band = proposal["proposed_band"]
        if not band["quick"] <= band["target"] <= band["high"]:
            raise ValueError(f"{record['name']}: invalid reviewed band")
        if proposal["requires_large_change_review"] and proposal["reviewer_decision"] not in {"accept", "revise", "retain"}:
            raise ValueError(f"{record['name']}: large change lacks manual review")
        if record["external_relative_review"].get("used_to_set_gold_value") is not False:
            raise ValueError(f"{record['name']}: external gold leaked into proposal")
        for observation in record["source_observations"].values():
            if "median_buyout_copper" in observation or "economy_scale" in observation:
                raise ValueError(f"{record['name']}: nominal external gold was saved")
        if require_applied:
            current = {name: int(item[f"{name}_copper"]) for name in PRICE_BANDS}
            if current != band:
                raise ValueError(f"{record['name']}: reviewed band is not applied")
            expected_ref = f"{EVIDENCE_PATH.relative_to(ROOT).as_posix()}#items/{record['item_id']}"
            if item.get("price_strategy") != "evidence-pricing-market-value" or item.get("price_evidence_ref") != expected_ref:
                raise ValueError(f"{record['name']}: Evidence Pricing metadata is stale")
            if str(record["item_id"]) in baseline:
                duplicate = baseline[str(record["item_id"])]
                duplicate_band = {name: int(duplicate[name]) for name in PRICE_BANDS}
                if duplicate_band != band or duplicate.get("evidence_ref") != expected_ref:
                    raise ValueError(f"{record['name']}: duplicate baseline is not synchronized")


def apply_catalog(evidence: dict) -> None:
    config = load(CRAFTED_PATH)
    source = CRAFTED_PATH.read_text(encoding="utf-8")
    baseline_doc = load(BASELINE_PATH)
    baseline = baseline_doc["items"]
    for record in evidence["items"].values():
        key = record["canonical_key"]
        item_id = str(record["item_id"])
        band = record["proposal"]["proposed_band"]
        updated = dict(config["catalog"][key])
        for name in PRICE_BANDS:
            updated[f"{name}_copper"] = int(band[name])
        evidence_ref = f"{EVIDENCE_PATH.relative_to(ROOT).as_posix()}#items/{item_id}"
        updated["price_strategy"] = "evidence-pricing-market-value"
        updated["price_evidence_ref"] = evidence_ref
        pattern = re.compile(rf'^(    "{re.escape(key)}": )\{{.*\}}(,?)$', re.MULTILINE)
        replacement = rf"\g<1>{json.dumps(updated, ensure_ascii=False, separators=(',', ':'))}\g<2>"
        source, count = pattern.subn(replacement, source, count=1)
        if count != 1:
            raise ValueError(f"Could not update canonical Tailoring row: {key}")
        if item_id in baseline:
            duplicate = dict(baseline[item_id])
            for name in PRICE_BANDS:
                duplicate[name] = int(band[name])
            duplicate["source_type"] = record["proposal"]["source_type"]
            duplicate["confidence"] = record["proposal"]["confidence"]
            duplicate["reason"] = record["proposal"]["reason"]
            duplicate["evidence_ref"] = evidence_ref
            baseline[item_id] = duplicate
    copy = guide_copy(evidence)
    guide = config["guides"][GUIDE_FILENAME]
    copy_updates = [
        (guide["intro_description"], copy["base_intro"]),
        (guide["shared_note"]["text"], copy["base_note"]),
    ]
    supplement = config.get("guide_supplements", {}).get(GUIDE_FILENAME, {}).get("overrides")
    if supplement:
        copy_updates.extend(
            [
                (supplement["intro_description"], copy["combined_intro"]),
                (supplement["shared_note"]["text"], copy["combined_note"]),
            ]
        )
    for old, new in copy_updates:
        count = source.count(old)
        if count != 1:
            raise ValueError(f"Tailoring guide copy matched {count} times: {old[:60]}")
        source = source.replace(old, new)
    if copy.get("label") and guide["shared_note"]["label"] != copy["label"]:
        note_id = re.escape(guide["shared_note"]["id"])
        old_label = re.escape(json.dumps(guide["shared_note"]["label"], ensure_ascii=False))
        label_pattern = re.compile(
            rf'("id"\s*:\s*"{note_id}"[\s\S]*?"label"\s*:\s*){old_label}'
        )
        source, count = label_pattern.subn(
            rf'\g<1>{json.dumps(copy["label"], ensure_ascii=False)}',
            source,
            count=1,
        )
        if count != 1:
            raise ValueError("Could not update the profession shared-note label")
    CRAFTED_PATH.write_text(source, encoding="utf-8", newline="\n")
    BASELINE_PATH.write_text(
        json.dumps(baseline_doc, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def refresh_dependency_diagnostics(evidence: dict) -> dict:
    config = load(CRAFTED_PATH)
    rows = {row["key"]: row for row in entries(config)}
    for record in evidence["items"].values():
        item = rows[record["canonical_key"]]["item"]
        floor = {band: int(item["pricing_floor_copper"][band]) for band in PRICE_BANDS}
        record["reagent_floor"] = floor
        record["proposal"]["below_reagent_floor_bands"] = [
            band for band in PRICE_BANDS
            if record["proposal"]["proposed_band"][band] < floor[band]
        ]
    evidence["dependency_diagnostics_refreshed"] = date.today().isoformat()
    update_summary(evidence)
    return evidence


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
    group.add_argument("--refresh-if-improved", action="store_true")
    group.add_argument("--review", action="store_true")
    group.add_argument("--refresh-dependencies", action="store_true")
    group.add_argument("--apply", action="store_true")
    group.add_argument("--check", action="store_true")
    args = parser.parse_args()

    if args.inventory:
        rows = entries(load(CRAFTED_PATH))
        print(json.dumps(Counter(row["view"] for row in rows), indent=2))
        print(f"reviewed items {len(rows)}")
        print("preserved Phase 1B intermediates 17")
        print("First Aid outputs outside batch 17")
        return 0
    if args.refresh:
        evidence = build_evidence()
        validate(evidence, require_applied=False)
        write_outputs(evidence)
        print(json.dumps(evidence["summary"], indent=2))
        return 0
    if args.refresh_if_improved:
        current = load(EVIDENCE_PATH)
        candidate = build_evidence(frozen_evidence=current)
        validate(candidate, require_applied=False)
        accepted, outcome = retry_improves_coverage(current, candidate)
        outcome["candidate_summary"] = candidate["summary"]
        if accepted:
            write_outputs(candidate)
        print(json.dumps(outcome, indent=2))
        return 0
    if args.review:
        evidence = review_saved_evidence(load(EVIDENCE_PATH))
        validate(evidence, require_applied=False)
        write_outputs(evidence)
        print(json.dumps(evidence["summary"], indent=2))
        return 0
    if args.refresh_dependencies:
        evidence = refresh_dependency_diagnostics(load(EVIDENCE_PATH))
        validate(evidence, require_applied=True)
        write_outputs(evidence)
        print("Refreshed Tailoring recipe-floor diagnostics without changing prices.")
        return 0
    evidence = load(EVIDENCE_PATH)
    if args.apply:
        validate(evidence, require_applied=False)
        apply_catalog(evidence)
        validate(evidence, require_applied=True)
        print(f"Applied {len(evidence['items'])} reviewed Tailoring price bands.")
        return 0
    validate(evidence, require_applied=True)
    if REPORT_PATH.read_text(encoding="utf-8") != render_report(evidence):
        print("Tailoring Evidence Pricing report is stale.", file=sys.stderr)
        return 1
    print("Tailoring Evidence Pricing review is current.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
