#!/usr/bin/env python3
"""Review, report, check, and apply dropped-gear price evidence."""

from __future__ import annotations

import argparse
import json
import math
import statistics
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CATALOG_PATH = ROOT / "data" / "ah-dropped-gear.json"
AUDIT_PATH = ROOT / "data" / "ah-dropped-gear-audit.json"
EVIDENCE_PATH = ROOT / "data" / "ah-dropped-gear-price-evidence.json"
CROSS_SERVER_PATH = ROOT / "data" / "ah-dropped-gear-cross-server-diagnostics.json"
BASELINE_PATH = ROOT / "data" / "ah-price-baselines.json"
REPORT_PATH = ROOT / "docs" / "ah-dropped-gear-repricing-review.md"
GUIDE_FIRST_PUBLISHED = "2026-08-05"
MODEL_VERSION = "hellscream-low-pop-relative-rank-v1"
MODEL_ANCHORS = {
    "level-80/200-205": 2_500_000,
    "level-80/206-212": 3_500_000,
    "level-80/213-218": 4_500_000,
    "level-80/219-225": 6_500_000,
    "level-80/226-239": 9_000_000,
    "level-80/245-258": 13_000_000,
    "level-80/264+": 20_000_000,
    "classic/rare": 300_000,
    "classic/epic": 750_000,
    "outland/rare": 150_000,
    "outland/epic": 1_000_000,
    "northrend/rare/71-73": 250_000,
    "northrend/rare/74-76": 350_000,
    "northrend/rare/77-79": 500_000,
}


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def band(record: dict) -> dict[str, int]:
    return {name: int(record[name]) for name in ("quick", "target", "high")}


def cohort(item: dict) -> str:
    section = item["section_id"]
    kind = section.rsplit("-", 1)[-1]
    if item["guide_id"] == "level-80-boe-epics":
        item_level = int(item["item_level"])
        if item_level >= 264:
            tier = "264+"
        elif item_level >= 245:
            tier = "245-258"
        elif item_level >= 226:
            tier = "226-239"
        elif item_level >= 213:
            tier = "213-225"
        else:
            tier = "200-212"
        return f"level-80/{tier}/{kind}"
    era = section.split("-")[1]
    return f"{era}/{item['quality']}/{kind}/req-{item['required_level']}"


def model_group(item: dict) -> str:
    if item["guide_id"] == "level-80-boe-epics":
        item_level = int(item["item_level"])
        if item_level >= 264:
            tier = "264+"
        elif item_level >= 245:
            tier = "245-258"
        elif item_level >= 226:
            tier = "226-239"
        elif item_level >= 219:
            tier = "219-225"
        elif item_level >= 213:
            tier = "213-218"
        elif item_level >= 206:
            tier = "206-212"
        else:
            tier = "200-205"
        return f"level-80/{tier}"

    era = item["section_id"].split("-")[1]
    if era in {"classic", "outland"}:
        return f"{era}/{item['quality']}"
    required_level = int(item["required_level"])
    if required_level <= 73:
        bracket = "71-73"
    elif required_level <= 76:
        bracket = "74-76"
    else:
        bracket = "77-79"
    return f"northrend/rare/{bracket}"


def external_rank_score(old_target: int, diagnostic: dict) -> float | None:
    ratio = diagnostic["normalized_ask_ratio_to_hellscream_target"]
    if ratio is None and diagnostic.get("normalized_ratio_range"):
        ratio = diagnostic["normalized_ratio_range"][0]
    return None if ratio is None else float(old_target) * float(ratio)


def midrank_percentile(values: list[float], value: float) -> float:
    if len(values) <= 1:
        return 0.5
    below = sum(candidate < value for candidate in values)
    equal = sum(candidate == value for candidate in values)
    return (below + (equal - 1) / 2) / (len(values) - 1)


def coverage_weight(diagnostic: dict) -> float:
    if (
        int(diagnostic["realm_count"]) >= 3
        and diagnostic["leave_one_realm_out"] == "stable-classification"
    ):
        return 1.0
    if int(diagnostic["realm_count"]) >= 2:
        return 0.75
    if int(diagnostic["realm_count"]) == 1:
        return 0.5
    return 0.0


def nice_step(copper: float) -> int:
    gold = copper / 10_000
    if gold < 10:
        return 5_000
    if gold < 25:
        return 10_000
    if gold < 100:
        return 50_000
    if gold < 500:
        return 100_000
    if gold < 1_000:
        return 250_000
    if gold < 5_000:
        return 500_000
    return 1_000_000


def round_nice(copper: float) -> int:
    step = nice_step(copper)
    return max(step, math.floor(copper / step + 0.5) * step)


def starter_band(target: int, diagnostic: dict) -> tuple[dict[str, int], str]:
    if (
        int(diagnostic["realm_count"]) >= 3
        and diagnostic["leave_one_realm_out"] == "stable-classification"
    ):
        quick_factor, high_factor = 0.72, 1.60
        spread_rule = "stable three-realm rank: 72% quick and 160% high"
    elif int(diagnostic["realm_count"]) >= 2:
        quick_factor, high_factor = 0.68, 1.75
        spread_rule = "multi-realm rank with sensitivity: 68% quick and 175% high"
    else:
        quick_factor, high_factor = 0.62, 2.00
        spread_rule = "single- or zero-realm rank: 62% quick and 200% high"
    return {
        "quick": round_nice(target * quick_factor),
        "target": target,
        "high": round_nice(target * high_factor),
    }, spread_rule


def proposal_for(
    item: dict,
    audit: dict,
    evidence: dict,
    old: dict,
    diagnostic: dict,
    group_scores: dict[str, list[float]],
) -> dict:
    sales = evidence["realized_sales"]
    supply = evidence["current_supply"]
    old_band = band(old)
    last_sale = sales["last_sale_date_utc"]
    predates_guide = bool(last_sale and last_sale < GUIDE_FIRST_PUBLISHED)
    feature_summary = {
        "stat_count": len(audit.get("stats", [])),
        "socket_count": len(audit.get("sockets", [])),
        "spell_count": len(audit.get("spells", [])),
        "source_rows": int(audit.get("loot_profile", {}).get("source_rows", 0)),
        "distinct_source_entries": int(
            audit.get("loot_profile", {}).get("distinct_source_entries", 0)
        ),
    }

    if sales["evidence_gate"] == "low" and predates_guide:
        target = int(sales["gross_unit_copper"]["median"])
        if int(sales["completed_buyouts"]) >= 2:
            quick = round(target * 0.90)
            high = round(target * 1.25)
            spread_rule = "Two same-price sparse sales: 90% quick and 125% high review bounds."
        else:
            quick = round(target * 0.85)
            high = round(target * 1.30)
            spread_rule = "One sparse sale: 85% quick and 130% high review bounds."
        proposed = {"quick": quick, "target": target, "high": high}
        reason = (
            f"Low-confidence Hellscream realized-sale band from {sales['completed_buyouts']} "
            f"completed buyout{'s' if sales['completed_buyouts'] != 1 else ''}, "
            f"{sales['distinct_buyers']} buyer, and {sales['distinct_days']} UTC sale day "
            f"ending {last_sale}; the sale history predates this guide's first publication. "
            f"Target is the exact gross unit median. {spread_rule} Active listing prices "
            "were not used."
        )
        return {
            "cohort": cohort(item),
            "features": feature_summary,
            "before_band": old_band,
            "proposed_band": proposed,
            "source_type": "realized-sales-history",
            "confidence": "low",
            "decision": "accept-sparse-direct-sale",
            "review_state": "accepted-local-evidence-pass",
            "requires_large_change_review": abs(proposed["target"] / old_band["target"] - 1) > 0.5,
            "unique_effect_reviewed": feature_summary["spell_count"] > 0,
            "reason": reason,
        }

    group = model_group(item)
    anchor = MODEL_ANCHORS[group]
    score = external_rank_score(old_band["target"], diagnostic)
    raw_percentile = (
        midrank_percentile(group_scores[group], score) if score is not None else 0.5
    )
    weight = coverage_weight(diagnostic)
    adjusted_percentile = 0.5 + (raw_percentile - 0.5) * weight
    rank_multiplier = 0.6 + 0.8 * adjusted_percentile
    unrounded_target = anchor * rank_multiplier
    target = round_nice(unrounded_target)
    proposed, spread_rule = starter_band(target, diagnostic)
    if score is None:
        rank_text = (
            "No usable cross-server rank was available, so the reviewed group midpoint was used"
        )
    else:
        rank_text = (
            f"Gold-normalized cross-server listing evidence placed the item at the "
            f"{raw_percentile * 100:.1f}% point on the within-group rank scale; "
            f"{diagnostic['realm_count']}-realm coverage received a {weight:.2f} reliability weight"
        )
    reason = (
        f"Reviewed Hellscream low-pop starter estimate using the {group} "
        f"{format_money(anchor)} anchor. {rank_text}, producing a {rank_multiplier:.3f}x "
        f"anchor before clean rounding; {spread_rule}. External asks informed relative order "
        "only—no external gold value was copied. Confidence remains fallback until Hellscream "
        "completed sales replace the estimate."
    )
    return {
        "cohort": cohort(item),
        "features": feature_summary,
        "before_band": old_band,
        "proposed_band": proposed,
        "source_type": "documented-fallback",
        "confidence": "fallback",
        "decision": "accept-reviewed-starter-estimate",
        "review_state": "accepted-user-directed-low-pop-estimate",
        "requires_large_change_review": abs(proposed["target"] / old_band["target"] - 1) > 0.5,
        "unique_effect_reviewed": feature_summary["spell_count"] > 0,
        "starter_model": {
            "version": MODEL_VERSION,
            "anchor_group": group,
            "anchor_target_copper": anchor,
            "cross_server_rank_available": score is not None,
            "raw_relative_rank_percentile": round(raw_percentile, 6),
            "coverage_weight": weight,
            "adjusted_rank_percentile": round(adjusted_percentile, 6),
            "rank_multiplier": round(rank_multiplier, 6),
            "unrounded_target_copper": round(unrounded_target),
            "rounding_step_copper": nice_step(unrounded_target),
            "external_gold_value_copied": False,
        },
        "reason": reason,
    }


def build_review() -> dict:
    catalog = load(CATALOG_PATH)
    audit = load(AUDIT_PATH)
    evidence = load(EVIDENCE_PATH)
    cross_server = load(CROSS_SERVER_PATH)
    baseline = load(BASELINE_PATH)
    by_id = {str(item["item_id"]): item for item in catalog["catalog"].values()}
    if set(by_id) != set(evidence["items"]) or set(by_id) != set(audit["items"]):
        raise ValueError("Dropped-gear catalog, audit, and evidence item sets differ")

    old_records = {}
    for item_id in by_id:
        prior_proposal = evidence["items"][item_id].get("proposal")
        old_record = dict(baseline["items"][item_id])
        if prior_proposal:
            old_record.update(prior_proposal["before_band"])
        old_records[item_id] = old_record

    group_scores: dict[str, list[float]] = defaultdict(list)
    for item_id, item in by_id.items():
        score = external_rank_score(
            int(old_records[item_id]["target"]), cross_server["items"][item_id]
        )
        if score is not None:
            group_scores[model_group(item)].append(score)
    for scores in group_scores.values():
        scores.sort()

    for item_id, item in by_id.items():
        evidence["items"][item_id]["proposal"] = proposal_for(
            item,
            audit["items"][item_id],
            evidence["items"][item_id],
            old_records[item_id],
            cross_server["items"][item_id],
            group_scores,
        )
        evidence["items"][item_id]["proposal"]["cross_server_diagnostic"] = (
            cross_server["items"][item_id]
        )
    decisions = Counter(
        record["proposal"]["decision"] for record in evidence["items"].values()
    )
    evidence["review"] = {
        "completed": date.today().isoformat(),
        "reviewed_items": len(evidence["items"]),
        "decisions": dict(sorted(decisions.items())),
        "first_guide_publication_date": GUIDE_FIRST_PUBLISHED,
        "cohort_model_deployed": False,
        "starter_estimate_model_deployed": True,
        "starter_estimate_model_version": MODEL_VERSION,
        "model_acceptance": "user-directed-reviewed-starter-estimates",
        "model_note": (
            "No item passed the medium realized-sales gate, so no realized-sales cohort model "
            "was deployed. The user explicitly requested practical starter prices for a low-pop "
            "market. The reviewed fallback model maps gold-normalized cross-server relative rank "
            "onto fixed Hellscream anchors; it never copies external gold and cannot promote "
            "confidence above fallback."
        ),
        "external_diagnostics": {
            "used_to_set_prices": False,
            "used_for_relative_rank": True,
            "external_gold_values_copied": False,
            "status": "gold-scale-normalized-relative-rank-review-complete",
            "source": "https://ah.nerfed.net/servers/base?id=7",
            "source_count": cross_server["summary"]["sources"],
            "realm_count": cross_server["summary"]["realms"],
            "items_seen_on_at_least_two_realms": cross_server["summary"][
                "items_seen_on_at_least_two_realms"
            ],
            "diagnostics": cross_server["summary"]["diagnostics"],
            "reason": (
                "Six Lordaeron, Icecrown, and Onyxia faction snapshots were normalized separately "
                "against six shared commodities with actual Hellscream completed sales. Their "
                "relative ordering within comparable gear groups informed a one-time reviewed "
                "starter estimate. Raw or normalized external gold prices, downloads, and seller "
                "identities were not committed or copied into a Hellscream band."
            ),
        },
    }
    evidence["rules"]["normalized_cross_server_gold_copied_to_baselines"] = False
    evidence["rules"]["normalized_cross_server_relative_rank_used_for_reviewed_estimates"] = True
    evidence["rules"]["live_snapshot_auto_repricing_enabled"] = False
    return evidence


def format_money(copper: int) -> str:
    gold, remainder = divmod(int(copper), 10_000)
    silver, copper = divmod(remainder, 100)
    if gold:
        return f"{gold:,}g {silver}s {copper}c"
    if silver:
        return f"{silver}s {copper}c"
    return f"{copper}c"


def format_band(values: dict) -> str:
    return " / ".join(format_money(int(values[key])) for key in ("quick", "target", "high"))


def render_report(evidence: dict) -> str:
    direct_sales = [
        record for record in evidence["items"].values()
        if record["proposal"]["decision"] == "accept-sparse-direct-sale"
    ]
    modeled = [
        record for record in evidence["items"].values()
        if record["proposal"]["decision"] == "accept-reviewed-starter-estimate"
    ]
    changed = sum(
        record["proposal"]["before_band"] != record["proposal"]["proposed_band"]
        for record in modeled
    )
    large_changes = sum(
        record["proposal"]["requires_large_change_review"] for record in modeled
    )
    supply_present = evidence["summary"]["items_present_in_current_supply_snapshot"]
    external = evidence["review"]["external_diagnostics"]
    external_counts = external["diagnostics"]
    lines = [
        "# Dropped-Gear Repricing Review",
        "",
        f"- Reviewed: `{evidence['review']['completed']}`",
        f"- Items reviewed: `{len(evidence['items'])}`",
        f"- Low-confidence direct-sale bands: `{len(direct_sales)}`",
        f"- Reviewed low-pop starter estimates: `{len(modeled)}`",
        f"- Starter estimates numerically changed: `{changed}`",
        f"- Target changes greater than 50%: `{large_changes}`",
        f"- Items present in the one local supply snapshot: `{supply_present}`",
        "- Realized-sales cohort model deployed: `no` — zero items passed the medium sales gate.",
        "- External gold values copied into bands: `no`",
        "- Gold-normalized cross-server relative rank used: `yes`",
        f"- Cross-server normalized coverage: `{external['items_seen_on_at_least_two_realms']}` items on at least two realms",
        f"- Normalized external diagnostic: `{external_counts.get('normalized-asks-below-hellscream-target', 0)}` below / "
        f"`{external_counts.get('normalized-asks-broadly-aligned', 0)}` aligned / "
        f"`{external_counts.get('normalized-asks-above-hellscream-target', 0)}` above / "
        f"`{external_counts.get('insufficient-external-coverage', 0)}` insufficient",
        "- Publication status: `local only — not published`",
        "",
        "## Decision",
        "",
        evidence["review"]["model_note"],
        "",
        "The purpose is a useful opening market, not a claim that every item already has a proven "
        "sale value. Fixed Hellscream anchors establish the gold scale. Gold-normalized external "
        "listings establish relative order only within comparable item groups. Coverage-sensitive "
        "ranks are pulled toward the group midpoint, clean price rounding avoids false precision, "
        "and wide Quick / Target / High bands leave room for the local market to decide. All 345 "
        "modeled rows remain `fallback` confidence until Hellscream completed sales replace them.",
        "",
        "## Hellscream starter anchors",
        "",
        "| Comparable group | Midpoint target | Ranked range before rounding |",
        "|---|---:|---:|",
    ]
    for group, anchor in MODEL_ANCHORS.items():
        lines.append(
            f"| {group} | {format_money(anchor)} | "
            f"{format_money(round(anchor * 0.6))}–{format_money(round(anchor * 1.4))} |"
        )
    lines.extend(
        [
        "",
        "## Direct-sale overrides",
        "",
        "| Item | Sales / buyers / days | Old Q / T / H | New Q / T / H | Target change | Review |",
        "|---|---:|---:|---:|---:|---|",
        ]
    )
    for record in direct_sales:
        proposal = record["proposal"]
        old = proposal["before_band"]
        new = proposal["proposed_band"]
        change = (new["target"] / old["target"] - 1) * 100
        sales = record["realized_sales"]
        lines.append(
            f"| {record['name']} | {sales['completed_buyouts']} / {sales['distinct_buyers']} / "
            f"{sales['distinct_days']} | {format_band(old)} | {format_band(new)} | "
            f"{change:+.1f}% | {'Large-change review accepted' if proposal['requires_large_change_review'] else 'Accepted'} |"
        )
    lines.extend(
        [
            "",
            "## Evidence limits",
            "",
            "- BeanCounter had three valid completed buyouts for catalog items: two for Sandals "
            "of Broken Dreams and one for Zom's Crackling Bulwark.",
            "- Both histories are sparse and buyer/day-concentrated, so neither reaches `medium`.",
            "- One current local snapshot is insufficient to classify stable supply or turnover.",
            "- Known account characters were excluded where identifiable; friend/guild identities "
            "were unavailable and are recorded as such.",
            "- No qualifying measured acquisition routes were supplied.",
            "- Six current Warmane faction snapshots were normalized by their measured commodity "
            "economy indexes. The source's lifetime charts are listing-price/volume history, not "
            "verified completed sales.",
            "- External listing values set relative rank only. Fixed Hellscream anchors set the "
            "gold scale; no external nominal or normalized gold value was copied.",
            "- No external completed-sale dataset or seven-day multi-snapshot series was available. "
            "That limitation is why every modeled estimate remains fallback-confidence.",
            "",
            "## All item decisions",
            "",
            "Prices are exact copper rendered as Quick / Target / High. `Present` is independent "
            "auction rows after known-account exclusion, not a valuation input.",
            "",
            "| ID | Item | Cohort | Sales | Buyers / days | Present | Relative-rank input | Old Q / T / H | Proposed Q / T / H | Decision | Confidence |",
            "|---:|---|---|---:|---:|---:|---|---:|---:|---|---|",
        ]
    )
    for item_id in sorted(evidence["items"], key=int):
        record = evidence["items"][item_id]
        proposal = record["proposal"]
        sales = record["realized_sales"]
        supply = record["current_supply"]
        cross = proposal["cross_server_diagnostic"]
        model = proposal.get("starter_model")
        if model:
            cross_label = (
                f"{model['anchor_group']}; rank {model['adjusted_rank_percentile'] * 100:.1f}%; "
                f"{cross['realm_count']} realms"
            )
        else:
            cross_label = f"direct local sale; {cross['realm_count']} external realms observed"
        lines.append(
            f"| {item_id} | {record['name']} | {proposal['cohort']} | "
            f"{sales['completed_buyouts']} | {sales['distinct_buyers']} / {sales['distinct_days']} | "
            f"{supply['auction_rows']} | {cross_label} | {format_band(proposal['before_band'])} | "
            f"{format_band(proposal['proposed_band'])} | {proposal['decision']} | "
            f"{proposal['confidence']} |"
        )
    lines.extend(
        [
            "",
            "## Reproduction",
            "",
            "```powershell",
            "python scripts/estimate-ah-dropped-gear-prices.py --check",
            "```",
            "",
            "Publishing is a separate step and is not part of this review.",
            "",
        ]
    )
    return "\n".join(lines)


def validate_evidence(evidence: dict) -> None:
    if len(evidence.get("items", {})) != 347:
        raise ValueError("Expected 347 dropped-gear evidence records")
    if evidence.get("rules", {}).get("active_listings_used_to_set_prices") is not False:
        raise ValueError("Active listings must not set dropped-gear baselines")
    review = evidence.get("review", {})
    if review.get("reviewed_items") != 347:
        raise ValueError("All 347 dropped-gear items must be reviewed")
    if review.get("cohort_model_deployed") is not False:
        raise ValueError("A realized-sales cohort model cannot be deployed without eligible holdouts")
    if review.get("starter_estimate_model_deployed") is not True:
        raise ValueError("The reviewed low-pop starter-estimate model is missing")
    if review.get("starter_estimate_model_version") != MODEL_VERSION:
        raise ValueError("The reviewed low-pop starter-estimate model version is stale")
    if review.get("external_diagnostics", {}).get("used_to_set_prices") is not False:
        raise ValueError("Cross-server gold values must not be copied into prices")
    if review.get("external_diagnostics", {}).get("used_for_relative_rank") is not True:
        raise ValueError("Cross-server relative-rank review is missing")
    if review.get("external_diagnostics", {}).get("external_gold_values_copied") is not False:
        raise ValueError("An external gold value leaked into the starter estimates")
    for item_id, record in evidence["items"].items():
        proposal = record.get("proposal")
        if not proposal:
            raise ValueError(f"{item_id}: missing proposal")
        values = proposal["proposed_band"]
        if not int(values["quick"]) <= int(values["target"]) <= int(values["high"]):
            raise ValueError(f"{item_id}: invalid proposed band")
        cross = proposal.get("cross_server_diagnostic", {})
        if cross.get("used_to_set_price") is not False:
            raise ValueError(f"{item_id}: cross-server ask leaked into pricing")
        if proposal["decision"] == "accept-sparse-direct-sale":
            sales = record["realized_sales"]
            if sales["evidence_gate"] != "low":
                raise ValueError(f"{item_id}: sparse-sale decision has wrong evidence gate")
            if sales["last_sale_date_utc"] >= GUIDE_FIRST_PUBLISHED:
                raise ValueError(f"{item_id}: accepted sale does not predate the guide")
            if proposal["confidence"] != "low":
                raise ValueError(f"{item_id}: sparse direct sale must remain low confidence")
        elif proposal["decision"] == "accept-reviewed-starter-estimate":
            model = proposal.get("starter_model", {})
            if proposal["source_type"] != "documented-fallback":
                raise ValueError(f"{item_id}: starter estimate has wrong source type")
            if proposal["confidence"] != "fallback":
                raise ValueError(f"{item_id}: starter estimate must remain fallback confidence")
            if model.get("version") != MODEL_VERSION:
                raise ValueError(f"{item_id}: starter estimate model version is stale")
            group = model.get("anchor_group")
            if group not in MODEL_ANCHORS:
                raise ValueError(f"{item_id}: starter estimate group is invalid")
            if model.get("anchor_target_copper") != MODEL_ANCHORS[group]:
                raise ValueError(f"{item_id}: starter estimate anchor drifted")
            if model.get("external_gold_value_copied") is not False:
                raise ValueError(f"{item_id}: external gold was copied")
            if round_nice(model["unrounded_target_copper"]) != values["target"]:
                raise ValueError(f"{item_id}: starter estimate target was not cleanly rounded")
        else:
            raise ValueError(f"{item_id}: unsupported decision {proposal['decision']}")

    decisions = Counter(
        record["proposal"]["decision"] for record in evidence["items"].values()
    )
    if decisions != Counter(
        {"accept-reviewed-starter-estimate": 345, "accept-sparse-direct-sale": 2}
    ):
        raise ValueError(f"Unexpected dropped-gear review decisions: {decisions}")


def apply_baselines(evidence: dict) -> None:
    baseline = load(BASELINE_PATH)
    for item_id, record in evidence["items"].items():
        proposal = record["proposal"]
        target = baseline["items"][item_id]
        target.update(proposal["proposed_band"])
        target["source_type"] = proposal["source_type"]
        target["confidence"] = proposal["confidence"]
        target["reason"] = proposal["reason"]
    BASELINE_PATH.write_text(
        json.dumps(baseline, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def check_applied(evidence: dict) -> None:
    baseline = load(BASELINE_PATH)
    for item_id, record in evidence["items"].items():
        proposal = record["proposal"]
        current = baseline["items"][item_id]
        if band(current) != proposal["proposed_band"]:
            raise ValueError(f"{item_id}: applied baseline differs from reviewed proposal")
        if current["source_type"] != proposal["source_type"]:
            raise ValueError(f"{item_id}: applied source type differs from reviewed proposal")
        if current["confidence"] != proposal["confidence"]:
            raise ValueError(f"{item_id}: applied confidence differs from reviewed proposal")
        if current["reason"] != proposal["reason"]:
            raise ValueError(f"{item_id}: applied reason differs from reviewed proposal")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--report", action="store_true", help="Write proposals and review report")
    group.add_argument("--apply", action="store_true", help="Apply the saved reviewed proposals")
    group.add_argument("--check", action="store_true", help="Validate evidence, report, and baselines")
    args = parser.parse_args()

    if args.report:
        evidence = build_review()
        validate_evidence(evidence)
        EVIDENCE_PATH.write_text(
            json.dumps(evidence, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
            newline="\n",
        )
        REPORT_PATH.write_text(render_report(evidence), encoding="utf-8", newline="\n")
        print(json.dumps(evidence["review"]["decisions"], indent=2))
        return 0

    evidence = load(EVIDENCE_PATH)
    validate_evidence(evidence)
    expected_report = render_report(evidence)
    if args.apply:
        apply_baselines(evidence)
        REPORT_PATH.write_text(expected_report, encoding="utf-8", newline="\n")
        print("Applied 347 reviewed dropped-gear decisions to the canonical baseline.")
        return 0

    if REPORT_PATH.read_text(encoding="utf-8") != expected_report:
        raise ValueError("Dropped-gear repricing review report is stale")
    check_applied(evidence)
    print("Dropped-gear pricing evidence, review report, and applied baselines are current.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
