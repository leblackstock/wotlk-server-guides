#!/usr/bin/env python3
"""Evidence-price, report, apply, and validate Phase 3 Turn-ins and recipes."""

from __future__ import annotations

import argparse
import importlib.util
import json
import statistics
from collections import Counter
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE_SCRIPT = ROOT / "scripts" / "review-ah-blacksmithing-prices.py"
BASELINE_PATH = ROOT / "data" / "ah-price-baselines.json"
CROSS_SERVER_PATH = ROOT / "data" / "ah-dropped-gear-cross-server-diagnostics.json"
TURN_IN_CATALOG_PATH = ROOT / "data" / "ah-turn-in-catalog.json"
RECIPE_AUDIT_PATH = ROOT / "data" / "ah-recipe-drop-audit.json"
PRICE_BANDS = ("quick", "target", "high")
PRESERVED_SHARED_MATERIAL_IDS = {11382, 17010, 17011, 17012}
BOOK_OF_GLYPH_MASTERY_REASON = (
    "User-reported average realized-sale estimate on 2026-08-03 set the 25g target; "
    "transaction counts, buyers, and days were not supplied, so confidence remains low "
    "and the value may be updated if later evidence differs. Quick and high retain the "
    "prior relative spread with the high band rounded. Replaced original 2026-08-02 "
    "frozen baseline: 150g quick, 300g target, 700g high."
)
SHARED_MATERIAL_REASONS = {
    11382: "Frozen from the guide revision before the 2026-08-02 listing scan; provisional until independent sales or acquisition evidence replaces it.",
    17010: "Reviewed fallback Evidence Pricing estimate using the fixed Shared: Molten Core cores Hellscream anchor. Current external observations set within-cohort rank only (0.0%); 3 realm coverage controls band width. No external gold or active Hellscream ask was copied.",
    17011: "Reviewed fallback Evidence Pricing estimate using the fixed Shared: Molten Core cores Hellscream anchor. Current external observations set within-cohort rank only (100.0%); 3 realm coverage controls band width. No external gold or active Hellscream ask was copied.",
    17012: "Preserved the completed Phase 1 shared-material Core Leather band for cross-guide consistency; the Turn-in review did not reprice this crafting material.",
}
MARKETS = {
    "turn-ins": {
        "evidence": ROOT / "data" / "ah-turn-in-price-evidence.json",
        "report": ROOT / "docs" / "ah-turn-in-pricing-review.md",
        "model": "turn-in-evidence-pricing-v1",
        "guide": "drop-turn-in-quest-page-items-ah-price-guide.html",
    },
    "recipes": {
        "evidence": ROOT / "data" / "ah-recipe-drop-price-evidence.json",
        "report": ROOT / "docs" / "ah-recipe-drop-pricing-review.md",
        "model": "recipe-drop-evidence-pricing-v1",
        "guide": "gear-pattern-drops-ah-price-guide.html",
    },
}


def load_base():
    spec = importlib.util.spec_from_file_location("ah_phase3_price_base", BASE_SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError("Could not load shared Evidence Pricing helpers")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


BASE = load_base()


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def band(record: dict) -> dict[str, int]:
    return {key: int(record[key]) for key in PRICE_BANDS}


def recipe_cohort(record: dict) -> str:
    source = record["guide_source"].casefold()
    if record["trainer_or_vendor_competition"]:
        era = "limited-vendor"
    elif "ulduar" in source:
        era = "ulduar"
    elif "wrath" in source:
        era = "wrath"
    elif "tbc" in source:
        era = "outland"
    else:
        era = "classic"
    return f"{record['section']} | {era}"


def rows_for_market(market: str, baseline: dict, previous: dict | None) -> list[dict]:
    rows = []
    previous_items = (previous or {}).get("items", {})
    if market == "turn-ins":
        source = load(TURN_IN_CATALOG_PATH)
        for item_id, record in source["items"].items():
            current = baseline.get(item_id)
            before = (
                previous_items.get(item_id, {}).get("before_band")
                or (band(current) if current else band(record["seed_band"]))
            )
            rows.append(
                {
                    "item_id": int(item_id),
                    "name": record["name"],
                    "section": record["section"],
                    "cohort": record["cohort"],
                    "before_band": before,
                    "record": record,
                    "current_baseline": current,
                }
            )
        return rows

    source = load(RECIPE_AUDIT_PATH)
    for item_id, record in source["items"].items():
        current = baseline.get(item_id)
        if current is None:
            raise ValueError(f"Recipe baseline is missing: {record['name']}")
        before = previous_items.get(item_id, {}).get("before_band") or band(current)
        rows.append(
            {
                "item_id": int(item_id),
                "name": record["name"],
                "section": record["section"],
                "cohort": recipe_cohort(record),
                "before_band": before,
                "record": record,
                "current_baseline": current,
            }
        )
    return rows


def external_review(rows: list[dict], cross: dict) -> tuple[dict[int, dict], dict]:
    tasks = []
    for source_key, (realm_id, faction_id) in BASE.SOURCE_IDS.items():
        scale = float(
            cross["sources"][source_key]["scale"]["external_gold_per_hellscream_gold"]
        )
        for row in rows:
            tasks.append(
                (source_key, row["item_id"], row["name"], realm_id, faction_id, scale)
            )
    observations, retry_summary = BASE.fetch_observations_with_retries(tasks)
    review = {}
    for row in rows:
        by_realm: dict[str, list[float]] = {}
        by_source = observations[row["item_id"]]
        for source_key, observation in by_source.items():
            if not observation["present"]:
                continue
            realm = cross["sources"][source_key]["realm"]
            by_realm.setdefault(realm, []).append(
                observation["median_buyout_copper"] / observation["economy_scale"]
            )
        realms = {realm: statistics.median(values) for realm, values in by_realm.items()}
        ratios = [value / row["before_band"]["target"] for value in realms.values()]
        review[row["item_id"]] = {
            "realm_values": realms,
            "realm_count": len(realms),
            "faction_snapshots_present": sum(obs["present"] for obs in by_source.values()),
            "normalized_score": statistics.median(realms.values()) if realms else None,
            "normalized_ask_ratio_to_before_target": (
                round(statistics.median(ratios), 4) if len(ratios) >= 2 else None
            ),
            "normalized_ratio_range": (
                [round(min(ratios), 4), round(max(ratios), 4)] if ratios else None
            ),
            "source_observations": {
                source_key: {
                    "present": observation["present"],
                    "scan_timestamp": observation["scan_timestamp"],
                    "quantity": observation["quantity"],
                    "source_url": observation["source_url"],
                    **({"fetch_failed": True} if observation.get("fetch_failed") else {}),
                }
                for source_key, observation in sorted(by_source.items())
            },
        }
    return review, retry_summary


def vendor_band(record: dict) -> dict[str, int]:
    cost = int(record["buy_price"])
    result = {
        "quick": BASE.round_market(cost * 1.25),
        "target": BASE.round_market(cost * 2.0),
        "high": BASE.round_market(cost * 4.0),
    }
    result["quick"] = min(result["quick"], result["target"])
    result["high"] = max(result["high"], result["target"])
    return result


def build_evidence(market: str) -> dict:
    config = MARKETS[market]
    baseline = load(BASELINE_PATH)["items"]
    previous = load(config["evidence"]) if config["evidence"].exists() else None
    rows = rows_for_market(market, baseline, previous)
    cross = load(CROSS_SERVER_PATH)
    sales, sales_source = BASE.load_sales({row["item_id"] for row in rows})
    external, retry_summary = external_review(rows, cross)

    previous_cohorts = (
        previous.get("cohorts", {})
        if previous and previous.get("model_version") == config["model"]
        else {}
    )
    cohorts = {}
    for row in rows:
        cohorts.setdefault(row["cohort"], []).append(row)
    cohort_records = {}
    for cohort, members in cohorts.items():
        old_anchor = previous_cohorts.get(cohort, {}).get("anchor_target_copper")
        anchor = int(
            old_anchor
            if old_anchor is not None
            else BASE.round_market(statistics.median(member["before_band"]["target"] for member in members))
        )
        cohort_records[cohort] = {
            "anchor_target_copper": anchor,
            "item_count": len(members),
            "anchor_source": (
                "Preserved from the first reviewed Phase 3 Evidence Pricing snapshot."
                if old_anchor is not None
                else "Rounded median Target from the frozen pre-Phase-3 guide cohort."
            ),
        }

    ranked_scores = {
        cohort: sorted(
            value
            for member in members
            if (value := external[member["item_id"]]["normalized_score"]) is not None
        )
        for cohort, members in cohorts.items()
    }
    records = {}
    for row in rows:
        item_id = row["item_id"]
        before = row["before_band"]
        ext = external[item_id]
        score = ext["normalized_score"]
        raw_rank = (
            BASE.midrank_percentile(ranked_scores[row["cohort"]], score)
            if score is not None
            else 0.5
        )
        fallback = BASE.fallback_band(
            cohort_records[row["cohort"]]["anchor_target_copper"],
            raw_rank,
            ext["realm_count"],
        )
        local_sales = sales.get(item_id)
        proposed = fallback
        decision = "cohort-rank-starter-estimate"
        source_type = "documented-fallback"
        confidence = "fallback"
        direct_weight = None
        reviewer_note = "Accepted after reviewing buyer use, source limits, and comparison coverage."

        if market == "turn-ins" and item_id in PRESERVED_SHARED_MATERIAL_IDS:
            proposed = dict(before)
            decision = "preserve-shared-material-evidence"
            source_type = row["current_baseline"]["source_type"]
            confidence = row["current_baseline"]["confidence"]
            reviewer_note = "Preserved the already-audited shared-material band to prevent cross-guide divergence."
        elif market == "recipes" and item_id == 45912:
            proposed = dict(before)
            decision = "preserve-user-reported-sale-anchor"
            source_type = row["current_baseline"]["source_type"]
            confidence = row["current_baseline"]["confidence"]
            reviewer_note = "Preserved the user-reported 25g average-sale Target recorded on 2026-08-03."
        elif local_sales:
            direct = BASE.direct_sale_band(local_sales)
            if local_sales["evidence_gate"] == "medium":
                proposed = direct
                decision = "direct-completed-sales"
                source_type = "realized-sales-history"
                confidence = "medium"
                direct_weight = 1.0
            else:
                direct_weight = (
                    0.50
                    if local_sales["distinct_buyers"] >= 2 and local_sales["distinct_days"] >= 2
                    else 0.25
                )
                proposed = BASE.shrink_sparse_sale(direct, fallback, direct_weight)
                decision = "sparse-completed-sales-shrunk"
                source_type = "realized-sales-history-plus-documented-fallback"
                confidence = "low"
        elif market == "recipes" and row["record"]["trainer_or_vendor_competition"]:
            proposed = vendor_band(row["record"])
            decision = "limited-vendor-cost-correction"
            source_type = "deterministic-vendor-cost-plus-documented-fallback"
            confidence = "low"
            reviewer_note = (
                "Accepted because the pinned database proves a limited-stock vendor source; "
                "the exact vendor cost sets the acquisition anchor, not an AH listing."
            )

        model_proposed = dict(proposed)
        model_change = proposed["target"] / before["target"] - 1.0
        large = abs(model_change) > 0.50
        protected_decisions = {
            "preserve-shared-material-evidence",
            "preserve-user-reported-sale-anchor",
            "limited-vendor-cost-correction",
            "direct-completed-sales",
        }
        reviewer_decision = "accept"
        if large and ext["realm_count"] < 2 and decision not in protected_decisions:
            proposed = dict(before)
            decision = "retain-reviewed-band-insufficient-coverage"
            source_type = "frozen-pre-phase3-guide"
            confidence = "fallback"
            reviewer_decision = "retain"
            reviewer_note = (
                "Retained after manual large-change review because zero- or one-realm "
                "coverage is insufficient for a Target move over 50%."
            )
        elif large and decision not in protected_decisions:
            reviewer_note = (
                "Accepted after manual large-change review because at least two comparison "
                "realms support the within-cohort direction and external gold was excluded."
            )
        change = proposed["target"] / before["target"] - 1.0
        records[str(item_id)] = {
            "item_id": item_id,
            "name": row["name"],
            "section": row["section"],
            "cohort": row["cohort"],
            "before_band": before,
            "local_completed_sales": local_sales,
            "external_relative_review": {
                "realms_present": sorted(ext["realm_values"]),
                "realm_count": ext["realm_count"],
                "faction_snapshots_present": ext["faction_snapshots_present"],
                "raw_relative_rank_percentile": round(raw_rank, 6),
                "coverage_weight": BASE.coverage_weight(ext["realm_count"]),
                "normalized_ask_ratio_to_before_target": ext["normalized_ask_ratio_to_before_target"],
                "normalized_ratio_range": ext["normalized_ratio_range"],
                "used_to_set_gold_value": False,
            },
            "source_observations": ext["source_observations"],
            "use_audit": (
                {
                    "max_stack": row["record"]["max_stack"],
                    "recommended_stack": row["record"]["recommended_stack"],
                    "restriction": row["record"]["restriction"],
                    "quest_records": row["record"]["quests"],
                }
                if market == "turn-ins"
                else {
                    "profession": row["record"]["profession"],
                    "required_skill_rank": row["record"]["required_skill_rank"],
                    "market": row["record"]["market"],
                    "loot_source_rows": len(row["record"]["loot_sources"]),
                    "vendor_sources": row["record"]["vendor_sources"],
                    "buy_price": row["record"]["buy_price"],
                }
            ),
            "proposal": {
                "proposed_band": proposed,
                "model_proposed_band_before_manual_review": model_proposed,
                "fallback_band_before_sales": fallback,
                "decision": decision,
                "source_type": source_type,
                "confidence": confidence,
                "anchor_target_copper": cohort_records[row["cohort"]]["anchor_target_copper"],
                "direct_sale_weight": direct_weight,
                "target_change_copper": proposed["target"] - before["target"],
                "target_change_percent": round(change * 100, 4),
                "model_target_change_percent": round(model_change * 100, 4),
                "requires_large_change_review": large,
                "reviewer_decision": reviewer_decision,
                "reviewer_note": reviewer_note,
                "reason": (
                    SHARED_MATERIAL_REASONS[item_id]
                    if market == "turn-ins" and item_id in PRESERVED_SHARED_MATERIAL_IDS
                    else BOOK_OF_GLYPH_MASTERY_REASON
                    if market == "recipes" and item_id == 45912
                    else f"Reviewed Phase 3 {market} Evidence Pricing band. Qualified completed sales "
                    "take precedence; sparse sales shrink toward a fixed Hellscream comparable-cohort "
                    "estimate. External asks set relative rank only, active Hellscream listings are "
                    "excluded, and exact quest, source, or vendor facts remain separate diagnostics."
                ),
            },
        }

    values = list(records.values())
    summary = {
        "items_reviewed": len(values),
        "bands_changed": sum(r["before_band"] != r["proposal"]["proposed_band"] for r in values),
        "completed_sale_items": sum(r["local_completed_sales"] is not None for r in values),
        "items_seen_on_three_realms": sum(r["external_relative_review"]["realm_count"] == 3 for r in values),
        "items_seen_on_two_realms": sum(r["external_relative_review"]["realm_count"] == 2 for r in values),
        "items_seen_on_one_realm": sum(r["external_relative_review"]["realm_count"] == 1 for r in values),
        "items_seen_on_no_realms": sum(r["external_relative_review"]["realm_count"] == 0 for r in values),
        "target_changes_over_fifty_percent": sum(r["proposal"]["requires_large_change_review"] for r in values),
        "target_increases": sum(r["proposal"]["proposed_band"]["target"] > r["before_band"]["target"] for r in values),
        "target_decreases": sum(r["proposal"]["proposed_band"]["target"] < r["before_band"]["target"] for r in values),
        "target_unchanged": sum(r["proposal"]["proposed_band"]["target"] == r["before_band"]["target"] for r in values),
        "decision_counts": dict(sorted(Counter(r["proposal"]["decision"] for r in values).items())),
        "fetch_failed_observations": retry_summary["final_failed_requests"],
        "external_gold_values_copied": False,
    }
    return {
        "version": 1,
        "refreshed": date.today().isoformat(),
        "scope": (
            "All 74 exact tradeable Turn-in items"
            if market == "turn-ins"
            else "All 90 tradeable Recipe and Pattern guide items"
        ),
        "method": "Evidence Pricing",
        "market": market,
        "model_version": config["model"],
        "rules": {
            "active_hellscream_listing_prices_used": False,
            "external_gold_values_copied": False,
            "external_role": "Gold-normalized within-comparable-cohort relative rank only.",
            "gold_scale": "Frozen Hellscream cohort anchors, qualified completed sales, or exact limited-vendor cost.",
            "large_change_rule": "Fallback Target moves over 50% require at least two comparison realms; direct sales and deterministic vendor corrections are reviewed separately.",
            "comparison_retry_rule": "After the initial batch, wait 2, 5, and 10 seconds and retry only failed comparison requests before recording a final failure.",
        },
        "sources": {
            "beancounter": sales_source,
            "external": {
                source_key: {
                    "realm": cross["sources"][source_key]["realm"],
                    "faction": cross["sources"][source_key]["faction"],
                    "economy_scale": cross["sources"][source_key]["scale"]["external_gold_per_hellscream_gold"],
                    "scale_snapshot_sha256": cross["sources"][source_key]["snapshot_sha256"],
                    "price_source": "https://ah.nerfed.net/servers/base?id=7",
                }
                for source_key in sorted(BASE.SOURCE_IDS)
            },
            "comparison_retry_summary": retry_summary,
        },
        "cohorts": cohort_records,
        "summary": summary,
        "items": records,
    }


def format_money(copper: int) -> str:
    gold, remainder = divmod(int(copper), 10_000)
    silver, copper = divmod(remainder, 100)
    if gold:
        return f"{gold:,}g {silver}s"
    if silver:
        return f"{silver}s {copper}c"
    return f"{copper}c"


def format_band(values: dict) -> str:
    return " / ".join(format_money(values[key]) for key in PRICE_BANDS)


def render_report(evidence: dict) -> str:
    summary = evidence["summary"]
    market = evidence["market"]
    title = "Turn-in" if market == "turn-ins" else "Recipe and Pattern Drop"
    request_total = summary["items_reviewed"] * len(BASE.SOURCE_IDS)
    lines = [
        f"# {title} Evidence Pricing Review",
        "",
        f"- Reviewed: `{evidence['refreshed']}`",
        f"- Scope: `{evidence['scope']}`",
        f"- Items reviewed: `{summary['items_reviewed']}`",
        f"- Price bands changed: `{summary['bands_changed']}`",
        f"- Target movement: `{summary['target_increases']}` up / `{summary['target_decreases']}` down / `{summary['target_unchanged']}` unchanged",
        f"- Items with completed-sale evidence: `{summary['completed_sale_items']}`",
        f"- Three-realm comparison coverage: `{summary['items_seen_on_three_realms']}`",
        f"- Comparison requests failed after retries: `{summary['fetch_failed_observations']}` of `{request_total}`",
        f"- Manually reviewed Target candidates over 50%: `{summary['target_changes_over_fifty_percent']}`",
        "- Active Hellscream listing prices used: `no`",
        "- External gold copied into Hellscream prices: `no`",
        "- Publication status: `local only — not published`",
        "",
        "## Decision",
        "",
        (
            "The grouped 26-row Turn-in table was replaced by exact item-level evidence for 74 tradeable items. Exact quest quantities, stack limits, repeatability, standing or event restrictions, and three BoP removals are separate use and eligibility facts; they do not silently become sale prices."
            if market == "turn-ins"
            else "Every recipe keeps its exact profession and skill requirement, learned-output market, pinned loot-source evidence, and vendor competition as separate buyer and acquisition facts. Five entries are limited-vendor recipes rather than drops, so exact vendor cost replaces the false drop-scarcity anchor."
        ),
        "",
        "Qualified local completed sales take precedence. Sparse sales shrink toward fixed Hellscream cohort anchors. External observations set relative rank only; their nominal gold values are not stored or copied. Active Hellscream listings remain excluded because guide-driven auctions dominate the local market.",
        "",
        "## Coverage",
        "",
        f"The saved refresh covers {summary['items_seen_on_three_realms']} items on three realms, {summary['items_seen_on_two_realms']} on two, {summary['items_seen_on_one_realm']} on one, and {summary['items_seen_on_no_realms']} on none. The fetcher made {request_total} initial requests and used the required 2-, 5-, and 10-second retry sequence only for failures.",
        "",
        "## Item decisions",
        "",
        "| Section | Item | Old Q / T / H | Proposed Q / T / H | Target change | Sales | Coverage | Decision | Confidence | Review |",
        "|---|---|---:|---:|---:|---:|---:|---|---|---|",
    ]
    records = sorted(
        evidence["items"].values(),
        key=lambda record: (record["section"], -record["proposal"]["proposed_band"]["target"], record["name"]),
    )
    for record in records:
        proposal = record["proposal"]
        sales = record["local_completed_sales"]
        lines.append(
            "| "
            + " | ".join(
                [
                    record["section"],
                    record["name"],
                    format_band(record["before_band"]),
                    format_band(proposal["proposed_band"]),
                    f"{proposal['target_change_percent']:+.2f}%",
                    str(sales["completed_buyouts"]) if sales else "none",
                    f"{record['external_relative_review']['realm_count']} realms / {record['external_relative_review']['faction_snapshots_present']} factions",
                    proposal["decision"],
                    proposal["confidence"],
                    proposal["reviewer_decision"],
                ]
            )
            + " |"
        )
    lines.extend(["", "## Manual review of Target candidates over 50%", ""])
    large = [record for record in records if record["proposal"]["requires_large_change_review"]]
    if not large:
        lines.append("No model Target candidate moved more than 50%.")
    for record in large:
        proposal = record["proposal"]
        candidate = proposal["model_proposed_band_before_manual_review"]
        lines.append(
            f"- **{record['name']}**: {format_money(record['before_band']['target'])} → "
            f"{format_money(candidate['target'])} ({proposal['model_target_change_percent']:+.2f}%); "
            f"final {format_money(proposal['proposed_band']['target'])}. "
            f"Decision: `{proposal['reviewer_decision']}`. {proposal['reviewer_note']}"
        )
    lines.extend(
        [
            "",
            "## Evidence limits",
            "",
            "- External pages report asks, not verified sales; only within-cohort relative rank is used.",
            "- Current Hellscream listings are excluded from price setting and confidence.",
            "- Pinned quest, loot, binding, skill, and vendor records establish identity and acquisition facts, not guaranteed sale value.",
            "- Estimates without qualifying completed sales remain fallback or low confidence.",
            "",
            "## Reproduction",
            "",
            "```powershell",
            f"python scripts/review-ah-phase3-static-prices.py --market {market} --check",
            "```",
            "",
            "Publishing is a separate step and is not part of this review.",
            "",
        ]
    )
    return "\n".join(lines)


def validate(evidence: dict, market: str, *, require_applied: bool) -> None:
    expected = 74 if market == "turn-ins" else 90
    config = MARKETS[market]
    if evidence.get("method") != "Evidence Pricing" or evidence.get("market") != market:
        raise ValueError(f"{market}: evidence method or market is invalid")
    if evidence.get("model_version") != config["model"]:
        raise ValueError(f"{market}: model version is stale")
    if len(evidence.get("items", {})) != expected or evidence["summary"]["items_reviewed"] != expected:
        raise ValueError(f"{market}: expected {expected} reviewed items")
    if evidence["rules"].get("active_hellscream_listing_prices_used") is not False:
        raise ValueError(f"{market}: active listings must not set prices")
    if evidence["rules"].get("external_gold_values_copied") is not False:
        raise ValueError(f"{market}: external gold must not be copied")
    retry = evidence["sources"].get("comparison_retry_summary", {})
    if retry.get("retry_delays_seconds") != [2, 5, 10]:
        raise ValueError(f"{market}: comparison retry rule is missing")
    baseline = load(BASELINE_PATH)["items"]
    for item_id, record in evidence["items"].items():
        proposal = record["proposal"]
        values = proposal["proposed_band"]
        if not values["quick"] <= values["target"] <= values["high"]:
            raise ValueError(f"{record['name']}: invalid price band")
        if record["external_relative_review"].get("used_to_set_gold_value") is not False:
            raise ValueError(f"{record['name']}: external gold leaked into price")
        for observation in record["source_observations"].values():
            if "median_buyout_copper" in observation or "economy_scale" in observation:
                raise ValueError(f"{record['name']}: nominal external gold was saved")
        if require_applied:
            current = baseline.get(item_id)
            if current is None or band(current) != values:
                raise ValueError(f"{record['name']}: reviewed band is not applied")
            if current.get("source_type") != proposal["source_type"]:
                raise ValueError(f"{record['name']}: applied source type differs")
            if current.get("confidence") != proposal["confidence"]:
                raise ValueError(f"{record['name']}: applied confidence differs")


def apply(evidence: dict, market: str) -> None:
    baseline = load(BASELINE_PATH)
    for source_type in (
        "deterministic-vendor-cost-plus-documented-fallback",
        "frozen-pre-phase3-guide",
    ):
        if source_type not in baseline["allowed_evidence"]:
            baseline["allowed_evidence"].append(source_type)
    for item_id, record in evidence["items"].items():
        proposal = record["proposal"]
        current = baseline["items"].setdefault(item_id, {"name": record["name"]})
        current["name"] = record["name"]
        current.update(proposal["proposed_band"])
        current["source_type"] = proposal["source_type"]
        current["confidence"] = proposal["confidence"]
        current["reason"] = proposal["reason"]
    BASELINE_PATH.write_text(json.dumps(baseline, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")


def sync_use_audit(evidence: dict, market: str) -> None:
    """Refresh deterministic use facts without refetching saved market observations."""
    source = load(TURN_IN_CATALOG_PATH if market == "turn-ins" else RECIPE_AUDIT_PATH)
    for item_id, evidence_record in evidence["items"].items():
        record = source["items"][item_id]
        if market == "turn-ins":
            evidence_record["use_audit"] = {
                "max_stack": record["max_stack"],
                "recommended_stack": record["recommended_stack"],
                "restriction": record["restriction"],
                "quest_records": record["quests"],
            }
            if int(item_id) in PRESERVED_SHARED_MATERIAL_IDS:
                evidence_record["proposal"]["reason"] = SHARED_MATERIAL_REASONS[int(item_id)]
        else:
            evidence_record["use_audit"] = {
                "profession": record["profession"],
                "required_skill_rank": record["required_skill_rank"],
                "market": record["market"],
                "loot_source_rows": len(record["loot_sources"]),
                "vendor_sources": record["vendor_sources"],
                "buy_price": record["buy_price"],
            }
            if int(item_id) == 45912:
                evidence_record["proposal"]["reason"] = BOOK_OF_GLYPH_MASTERY_REASON


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--market", choices=sorted(MARKETS), required=True)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--refresh", action="store_true")
    group.add_argument("--apply", action="store_true")
    group.add_argument("--check", action="store_true")
    args = parser.parse_args()
    config = MARKETS[args.market]

    if args.refresh:
        evidence = build_evidence(args.market)
        validate(evidence, args.market, require_applied=False)
        config["evidence"].write_text(json.dumps(evidence, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
        config["report"].write_text(render_report(evidence), encoding="utf-8", newline="\n")
        print(json.dumps(evidence["summary"], indent=2))
        return 0

    evidence = load(config["evidence"])
    sync_use_audit(evidence, args.market)
    validate(evidence, args.market, require_applied=args.check)
    expected_report = render_report(evidence)
    if args.apply:
        apply(evidence, args.market)
        config["evidence"].write_text(
            json.dumps(evidence, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
            newline="\n",
        )
        config["report"].write_text(expected_report, encoding="utf-8", newline="\n")
        print(f"Applied {len(evidence['items'])} reviewed {args.market} decisions.")
        return 0
    if config["report"].read_text(encoding="utf-8") != expected_report:
        raise ValueError(f"{args.market}: review report is stale")
    print(f"Phase 3 {args.market} evidence, report, and baselines are current.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
