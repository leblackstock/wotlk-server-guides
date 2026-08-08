#!/usr/bin/env python3
"""Review missing dropped and quest-reward containers with Evidence Pricing."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import math
import re
import statistics
import unicodedata
from collections import Counter, defaultdict
from datetime import date, datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
AUDIT_PATH = ROOT / "data" / "ah-container-audit.json"
EVIDENCE_PATH = ROOT / "data" / "ah-container-price-evidence.json"
SECTIONS_PATH = ROOT / "data" / "ah-container-sections.json"
REPORT_PATH = ROOT / "docs" / "ah-container-pricing-review.md"
CROSS_SERVER_PATH = ROOT / "data" / "ah-dropped-gear-cross-server-diagnostics.json"
CRAFTED_PATH = ROOT / "data" / "ah-crafted-sections.json"
BASE_REVIEW_PATH = ROOT / "scripts" / "review-ah-blacksmithing-prices.py"
IMPORTER_PATH = ROOT / "scripts" / "import-ah-dropped-gear-evidence.py"
BEANCOUNTER_PATH = Path(
    r"D:\Hellscream WoW\launcher\WTF\Account\LEBLACKSTOCK\SavedVariables\BeanCounter.lua"
)
SCAN_PATH = Path(
    r"D:\Hellscream WoW\launcher\WTF\Account\LEBLACKSTOCK\SavedVariables\Auc-ScanData.lua"
)
MODEL_VERSION = "container-capacity-evidence-pricing-v1"
PRICE_BANDS = ("quick", "target", "high")

# Frozen from the already-reviewed Classic crafted-container Targets on
# 2026-08-08. These are capacity comparables, not current AH listings.
CAPACITY_ANCHORS = {
    6: {
        "target_copper": 20_000,
        "comparables": {4238: 20_500, 5762: 19_500},
    },
    8: {
        "target_copper": 23_000,
        "comparables": {4240: 23_000, 4241: 26_500, 5763: 22_000},
    },
    10: {
        "target_copper": 25_500,
        "comparables": {4245: 27_500, 5764: 25_500, 5765: 24_000},
    },
    12: {
        "target_copper": 30_000,
        "comparables": {10050: 29_000, 10051: 31_000},
    },
    14: {
        "target_copper": 30_000,
        "comparables": {14046: 30_000},
    },
    16: {
        "target_copper": 33_500,
        "comparables": {14155: 33_500},
    },
}
QUEST_REWARD_ANCHOR = {
    "target_copper": 35_000,
    "reason": (
        "The 14-slot Classic crafted-container anchor is 3g; the 50-ticket "
        "Darkmoon reward route receives only a modest acquisition premium because "
        "the bag still competes on ordinary 14-slot utility."
    ),
}


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load {path.name}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


BASE = load_module("ah_container_evidence_base", BASE_REVIEW_PATH)
IMPORTER = load_module("ah_container_evidence_importer", IMPORTER_PATH)


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def item_slug(value: str) -> str:
    value = "".join(
        character
        for character in unicodedata.normalize("NFKD", value)
        if not unicodedata.combining(character)
    )
    return re.sub(r"[^a-z0-9]+", "-", value.casefold()).strip("-")


def format_money(copper: int) -> str:
    if copper >= 10_000:
        copper = ((copper + 50) // 100) * 100
    gold, remainder = divmod(copper, 10_000)
    silver, copper = divmod(remainder, 100)
    parts: list[str] = []
    if gold:
        parts.append(f"{gold:,}g")
    if silver:
        parts.append(f"{silver}s")
    if copper or not parts:
        parts.append(f"{copper}c")
    return " ".join(parts)


def round_market(value: float) -> int:
    copper = max(1, int(round(value)))
    if copper < 100:
        step = 10
    elif copper < 1_000:
        step = 50
    elif copper < 10_000:
        step = 100
    elif copper < 100_000:
        step = 500
    else:
        step = 2_500
    return max(step, int(math.floor(copper / step + 0.5) * step))


def midrank_percentile(values: list[float], value: float) -> float:
    if len(values) <= 1:
        return 0.5
    below = sum(candidate < value for candidate in values)
    equal = sum(candidate == value for candidate in values)
    return (below + (equal - 1) / 2) / (len(values) - 1)


def coverage_weight(realm_count: int) -> float:
    return {3: 1.0, 2: 0.7, 1: 0.35}.get(realm_count, 0.0)


def fallback_band(anchor: int, rank: float, realm_count: int) -> dict[str, int]:
    adjusted_rank = 0.5 + (rank - 0.5) * coverage_weight(realm_count)
    target = round_market(anchor * (0.85 + 0.30 * adjusted_rank))
    if realm_count >= 3:
        quick_factor, high_factor = 0.75, 1.50
    elif realm_count == 2:
        quick_factor, high_factor = 0.70, 1.70
    else:
        quick_factor, high_factor = 0.60, 2.00
    return {
        "quick": min(target, round_market(target * quick_factor)),
        "target": target,
        "high": max(target, round_market(target * high_factor)),
    }


def direct_sale_band(sales: dict) -> dict[str, int]:
    prices = sales["gross_unit_copper"]
    target = round_market(int(prices["median"]))
    quick = round_market(min(int(prices["q1"]), target * 0.85))
    high = round_market(max(int(prices["q3"]), target * 1.30))
    return {
        "quick": min(quick, target),
        "target": target,
        "high": max(high, target),
    }


def shrink_sparse_sale(
    direct: dict[str, int], fallback: dict[str, int], weight: float
) -> dict[str, int]:
    result = {
        band: round_market(direct[band] * weight + fallback[band] * (1 - weight))
        for band in PRICE_BANDS
    }
    result["quick"] = min(result["quick"], result["target"])
    result["high"] = max(result["high"], result["target"])
    return result


def item_group(item: dict) -> str:
    if item["primary_source"] == "quest-reward":
        return "quest-reward/14-slot"
    return f"classic-drop/{item['capacity']}-slot"


def anchor_for(item: dict) -> tuple[int, dict]:
    if item["primary_source"] == "quest-reward":
        return int(QUEST_REWARD_ANCHOR["target_copper"]), QUEST_REWARD_ANCHOR
    capacity = int(item["capacity"])
    if capacity not in CAPACITY_ANCHORS:
        raise ValueError(f"Missing capacity anchor for {item['name']}")
    record = CAPACITY_ANCHORS[capacity]
    return int(record["target_copper"]), record


def source_label(item: dict) -> str:
    if item["primary_source"] == "quest-reward":
        return "Darkmoon Faire 50-ticket reward"
    loot = item["loot_sources"]
    cohorts = loot.get("world_loot_cohorts", [])
    if cohorts:
        label = cohorts[0].replace("Vanilla Bags ", "Classic level ").replace(
            " Level Range", " world/container drop"
        )
        if len(cohorts) > 1:
            label = "Classic level 41–62 world/container drop"
        return label
    evidence = [
        value
        for value in loot.get("representative_evidence", [])
        if value != item["name"] and " - " not in value
    ]
    return f"{evidence[0]} drop" if evidence else "Verified Classic creature drop"


def demand_for(item: dict) -> tuple[str, str]:
    capacity = int(item["capacity"])
    if capacity >= 16:
        return "Low-Med", "med"
    if capacity >= 14:
        return "Low-Med", "med"
    return "Low", "low"


def item_note(item: dict) -> str:
    capacity = int(item["capacity"])
    if item["primary_source"] == "quest-reward":
        return (
            f"{capacity}-slot general bag from the guaranteed reward for quest 7934, "
            "50 Tickets - Darkmoon Storage Box. Compare its ordinary storage utility "
            "with crafted 14-slot bags; the ticket source does not prove a large premium."
        )
    loot = item["loot_sources"]
    cohorts = loot.get("world_loot_cohorts", [])
    if cohorts:
        acquisition = source_label(item)
        return (
            f"{capacity}-slot general bag in the pinned {acquisition} cohort. It competes "
            f"by capacity with reviewed Classic crafted bags; post one at a time and do "
            "not treat an empty AH as proof of the High band."
        )
    direct = source_label(item).removesuffix(" drop")
    return (
        f"{capacity}-slot general bag with a verified pinned drop route from {direct}. "
        "The specific source may make supply thinner, but buyer value still comes mainly "
        "from capacity; post one at a time."
    )


def source_snapshot(path: Path) -> dict:
    return {
        "provided": path.is_file(),
        "sha256": hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else None,
        "modified_utc": (
            datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc)
            .replace(microsecond=0)
            .isoformat()
            if path.is_file()
            else None
        ),
        "raw_path_saved": False,
        "identity_names_saved": False,
    }


def build_evidence() -> dict:
    audit = load(AUDIT_PATH)
    cross_server = load(CROSS_SERVER_PATH)
    items = {
        int(item_id): item
        for item_id, item in audit["items"].items()
        if item["primary_source"] in {"drop", "quest-reward"}
    }
    item_ids = set(items)
    sales, sales_meta = BASE.load_sales(item_ids)

    owned_characters: set[str] = set()
    supply: dict[int, dict] = {}
    scan_meta = {
        "provided": False,
        "listing_prices_saved": False,
        "listing_prices_used_to_set_baselines": False,
        "known_friend_or_guild_exclusions_available": False,
    }
    if BEANCOUNTER_PATH.is_file() and SCAN_PATH.is_file():
        owned_characters = IMPORTER.parse_characters(BEANCOUNTER_PATH, "Garrosh")
        listings, parsed_scan_meta = IMPORTER.parse_scan(
            SCAN_PATH, "Garrosh", item_ids, owned_characters
        )
        supply = {
            item_id: IMPORTER.supply_record(listings.get(item_id, []))
            for item_id in item_ids
        }
        scan_meta = {"provided": True, **parsed_scan_meta}

    tasks = []
    for source_key, (realm_id, faction_id) in BASE.SOURCE_IDS.items():
        scale = float(
            cross_server["sources"][source_key]["scale"][
                "external_gold_per_hellscream_gold"
            ]
        )
        for item_id, item in items.items():
            tasks.append(
                (source_key, item_id, item["name"], realm_id, faction_id, scale)
            )
    observations, retry_summary = BASE.fetch_observations_with_retries(tasks)

    realm_scores: dict[int, dict[str, float]] = {}
    for item_id in sorted(items):
        by_realm: dict[str, list[float]] = defaultdict(list)
        for source_key, observation in observations[item_id].items():
            if observation["present"]:
                realm = cross_server["sources"][source_key]["realm"]
                by_realm[realm].append(
                    observation["median_buyout_copper"]
                    / observation["economy_scale"]
                )
        realm_scores[item_id] = {
            realm: statistics.median(values) for realm, values in by_realm.items()
        }

    group_scores: dict[str, list[float]] = defaultdict(list)
    for item_id, item in items.items():
        if realm_scores[item_id]:
            group_scores[item_group(item)].append(
                statistics.median(realm_scores[item_id].values())
            )

    records: dict[str, dict] = {}
    decisions = Counter()
    for item_id, item in sorted(items.items()):
        realms = realm_scores[item_id]
        score = statistics.median(realms.values()) if realms else None
        group = item_group(item)
        rank = (
            midrank_percentile(group_scores[group], score)
            if score is not None
            else 0.5
        )
        anchor, anchor_record = anchor_for(item)
        fallback = fallback_band(anchor, rank, len(realms))
        local_sales = sales.get(item_id)
        proposal = fallback
        decision = "capacity-cohort-starter-estimate"
        source_type = "documented-fallback"
        confidence = "fallback"
        sales_weight = None
        if local_sales:
            direct = direct_sale_band(local_sales)
            if local_sales["evidence_gate"] == "medium":
                proposal = direct
                decision = "direct-completed-sales"
                source_type = "realized-sales-history"
                confidence = "medium"
                sales_weight = 1.0
            else:
                sales_weight = (
                    0.50
                    if local_sales["distinct_buyers"] >= 2
                    and local_sales["distinct_days"] >= 2
                    else 0.25
                )
                proposal = shrink_sparse_sale(direct, fallback, sales_weight)
                decision = "sparse-completed-sales-shrunk"
                source_type = "realized-sales-history-plus-documented-fallback"
                confidence = "low"
        decisions[decision] += 1
        normalized_ratios = [value / anchor for value in realms.values()]
        records[str(item_id)] = {
            "item_id": item_id,
            "name": item["name"],
            "primary_source": item["primary_source"],
            "capacity": int(item["capacity"]),
            "quality": item["quality"],
            "cohort": group,
            "fixed_anchor": {
                "target_copper": anchor,
                "source": (
                    "Frozen 2026-08-08 reviewed Classic crafted-container comparables."
                    if item["primary_source"] == "drop"
                    else QUEST_REWARD_ANCHOR["reason"]
                ),
                "comparables": anchor_record.get("comparables", {}),
            },
            "local_completed_sales": local_sales,
            "current_supply": supply.get(
                item_id,
                {
                    "auction_rows": 0,
                    "units": 0,
                    "distinct_sellers": 0,
                    "largest_seller_unit_share": None,
                    "rows_with_buyout": 0,
                    "owned_account_rows_excluded": 0,
                    "owned_account_units_excluded": 0,
                    "classification": "snapshot-unavailable",
                    "diagnostic_only": True,
                },
            ),
            "external_relative_review": {
                "realms_present": sorted(realms),
                "realm_count": len(realms),
                "faction_snapshots_present": sum(
                    observation["present"]
                    for observation in observations[item_id].values()
                ),
                "raw_relative_rank_percentile": round(rank, 6),
                "coverage_weight": coverage_weight(len(realms)),
                "normalized_ask_ratio_to_fixed_anchor": (
                    round(statistics.median(normalized_ratios), 4)
                    if len(normalized_ratios) >= 2
                    else None
                ),
                "normalized_ratio_range": (
                    [round(min(normalized_ratios), 4), round(max(normalized_ratios), 4)]
                    if normalized_ratios
                    else None
                ),
                "used_to_set_gold_value": False,
                "external_gold_value_copied": False,
            },
            "proposal": {
                "band": proposal,
                "source_type": source_type,
                "confidence": confidence,
                "decision": decision,
                "sales_weight": sales_weight,
                "reason": (
                    f"Evidence Pricing used the fixed {format_money(anchor)} {group} "
                    f"Hellscream anchor and {len(realms)}-realm relative rank; external "
                    "gold was not copied and the active Hellscream snapshot did not set price."
                ),
                "reviewer_decision": "accept",
            },
        }

    return {
        "version": 1,
        "reviewed": date.today().isoformat(),
        "model_version": MODEL_VERSION,
        "scope": "The 21 verified drop-owned containers and one verified quest-reward container missing from the AH guides.",
        "rules": {
            "active_listings_used_to_set_prices": False,
            "external_gold_values_copied": False,
            "external_role": "Gold-normalized cross-server observations set within-capacity relative rank only; fixed Hellscream comparable anchors set the gold scale.",
            "comparison_retry_rule": "Initial batch plus failed-request retries after 2, 5, and 10 seconds.",
            "nonstackable_rule": "Every container has max stack 1; no stack recommendation is rendered.",
        },
        "fixed_capacity_anchors": CAPACITY_ANCHORS,
        "quest_reward_anchor": QUEST_REWARD_ANCHOR,
        "source_snapshots": {
            "beancounter": {**source_snapshot(BEANCOUNTER_PATH), **sales_meta},
            "auction_scan": {**source_snapshot(SCAN_PATH), **scan_meta},
            "external_comparisons": {
                "source": "https://ah.nerfed.net/servers/base?id=7",
                "retry_summary": retry_summary,
                "nominal_gold_saved": False,
            },
        },
        "summary": {
            "items_reviewed": len(records),
            "decisions": dict(sorted(decisions.items())),
            "items_with_completed_sales": sum(
                bool(record["local_completed_sales"]) for record in records.values()
            ),
            "items_present_in_current_supply_snapshot": sum(
                record["current_supply"]["auction_rows"] > 0
                for record in records.values()
            ),
            "items_seen_on_at_least_two_external_realms": sum(
                record["external_relative_review"]["realm_count"] >= 2
                for record in records.values()
            ),
            "final_failed_comparison_requests": retry_summary[
                "final_failed_requests"
            ],
        },
        "items": records,
    }


def catalog_from_evidence(evidence: dict) -> dict:
    audit = load(AUDIT_PATH)
    catalog: dict[str, dict] = {}
    for item_id, record in evidence["items"].items():
        source = audit["items"][item_id]
        demand, demand_class = demand_for(source)
        key = item_slug(source["name"])
        proposal = record["proposal"]
        catalog[key] = {
            "item_id": int(item_id),
            "name": source["name"],
            "quality": source["quality"],
            "capacity": int(source["capacity"]),
            "container_type": "general inventory bag",
            "primary_source": source["primary_source"],
            "detail": f"Classic • {source['capacity']}-slot general inventory bag",
            "source": source_label(source),
            "buyer": "Leveling characters and alts",
            "demand": demand,
            "demand_class": demand_class,
            "quick_copper": int(proposal["band"]["quick"]),
            "target_copper": int(proposal["band"]["target"]),
            "high_copper": int(proposal["band"]["high"]),
            "stack": None,
            "notes": item_note(source),
            "price_strategy": "evidence-pricing-market-value",
            "price_evidence_ref": f"data/ah-container-price-evidence.json#items/{item_id}",
        }
    drop_keys = [
        key for key, item in catalog.items() if item["primary_source"] == "drop"
    ]
    quest_keys = [
        key
        for key, item in catalog.items()
        if item["primary_source"] == "quest-reward"
    ]
    return {
        "version": 1,
        "source": {
            "audit": "data/ah-container-audit.json",
            "evidence": "data/ah-container-price-evidence.json",
        },
        "pricing_unit": "per item",
        "catalog": catalog,
        "guides": {
            "sought-after-world-drops-ah-price-guide.html": {
                "marker": "AH_CONTAINER_DROPS",
                "sections": [
                    {
                        "id": "dropped-bags-and-containers",
                        "title": "Dropped bags and containers",
                        "description": "Verified auctionable Classic bags with pinned loot routes. Prices are per bag and are compared with the existing crafted-container market by exact slot count.",
                        "items": drop_keys,
                    }
                ],
            },
            "drop-turn-in-quest-page-items-ah-price-guide.html": {
                "marker": "AH_CONTAINER_QUEST_REWARDS",
                "sections": [
                    {
                        "id": "quest-reward-containers",
                        "title": "Tradeable quest-reward containers",
                        "description": "Verified auctionable containers granted by a pinned quest reward. Price the storage utility separately from the acquisition route.",
                        "items": quest_keys,
                    }
                ],
            },
        },
    }


def format_band(record: dict) -> str:
    return " / ".join(format_money(int(record[band])) for band in PRICE_BANDS)


def render_report(evidence: dict) -> str:
    retry = evidence["source_snapshots"]["external_comparisons"]["retry_summary"]
    lines = [
        "# Container Pricing Review",
        "",
        f"- Reviewed: `{evidence['reviewed']}`",
        f"- Missing drop and quest-reward containers reviewed: `{evidence['summary']['items_reviewed']}`",
        f"- Containers with qualified or sparse completed sales: `{evidence['summary']['items_with_completed_sales']}`",
        f"- Present in the current local supply snapshot after owned-account exclusion: `{evidence['summary']['items_present_in_current_supply_snapshot']}`",
        f"- Seen on at least two comparison realms: `{evidence['summary']['items_seen_on_at_least_two_external_realms']}`",
        f"- Comparison requests: `{retry['initial_requests']}` initial / `{retry['final_failed_requests']}` final failures after the 2-, 5-, and 10-second retry rule",
        "- Active Hellscream listings used to set prices: `no`",
        "- External nominal or normalized gold copied into prices: `no`",
        "- Publication status: `local only — not published`",
        "",
        "## Method",
        "",
        "The fixed gold scale comes from the already-reviewed Classic crafted bags with the same exact capacity. Gold-normalized Lordaeron, Icecrown, and Onyxia observations can change only within-capacity relative rank. The one current Hellscream scan is a supply diagnostic and never a valuation input. With no completed sales for these items, all 22 additions remain fallback-confidence starting bands.",
        "",
        "## Frozen capacity anchors",
        "",
        "| Capacity | Hellscream Target anchor | Existing reviewed comparables |",
        "|---:|---:|---|",
    ]
    for capacity, anchor in sorted(CAPACITY_ANCHORS.items()):
        comparables = ", ".join(
            f"item {item_id}: {format_money(target)}"
            for item_id, target in anchor["comparables"].items()
        )
        lines.append(
            f"| {capacity} slots | {format_money(anchor['target_copper'])} | {comparables} |"
        )
    lines.extend(
        [
            "",
            "## Reviewed additions",
            "",
            "| ID | Item | Route | Capacity | Realms | Local supply rows | Quick / Target / High | Confidence |",
            "|---:|---|---|---:|---:|---:|---:|---|",
        ]
    )
    for item_id, record in sorted(
        evidence["items"].items(), key=lambda pair: (-pair[1]["capacity"], pair[1]["name"])
    ):
        lines.append(
            f"| {item_id} | {record['name']} | {record['primary_source']} | "
            f"{record['capacity']} | {record['external_relative_review']['realm_count']} | "
            f"{record['current_supply']['auction_rows']} | "
            f"{format_band(record['proposal']['band'])} | {record['proposal']['confidence']} |"
        )
    lines.extend(
        [
            "",
            "## Evidence limits",
            "",
            "- BeanCounter contained no records for these 22 item IDs, so none can claim a locally proven sale value.",
            "- The Auctioneer snapshot excludes the user's identifiable account rows, but friend and guild identities are unavailable; it is diagnostic only.",
            "- Cross-server pages report listings, not completed sales. They set relative order only and do not set the Hellscream gold scale.",
            "- The pinned source verifies acquisition and eligibility, not current Hellscream custom drop rates or vendor modifications.",
            "",
            "## Reproduction",
            "",
            "```powershell",
            "python scripts/review-ah-container-prices.py --check",
            "```",
            "",
            "Publishing is a separate step and was not authorized.",
            "",
        ]
    )
    return "\n".join(lines)


def validate(evidence: dict, sections: dict, report: str) -> None:
    if evidence.get("version") != 1 or evidence.get("model_version") != MODEL_VERSION:
        raise ValueError("Container Evidence Pricing model is missing or stale")
    if evidence.get("summary", {}).get("items_reviewed") != 22:
        raise ValueError("Expected 22 drop/quest-reward container price reviews")
    rules = evidence.get("rules", {})
    if rules.get("active_listings_used_to_set_prices") is not False:
        raise ValueError("Active Hellscream listings leaked into container pricing")
    if rules.get("external_gold_values_copied") is not False:
        raise ValueError("External gold leaked into container pricing")
    retry = evidence["source_snapshots"]["external_comparisons"]["retry_summary"]
    if retry.get("initial_requests") != 132 or retry.get("retry_delays_seconds") != [2, 5, 10]:
        raise ValueError("Container comparison refresh lacks the three-wait retry record")
    if len(sections.get("catalog", {})) != 22:
        raise ValueError("Container section catalog must contain 22 additions")
    expected_ids = {int(item_id) for item_id in evidence["items"]}
    actual_ids = {int(item["item_id"]) for item in sections["catalog"].values()}
    if expected_ids != actual_ids:
        raise ValueError("Container evidence and section item sets differ")
    for key, item in sections["catalog"].items():
        if item.get("stack") is not None:
            raise ValueError(f"Non-stackable container has a stack suggestion: {key}")
        evidence_band = evidence["items"][str(item["item_id"])]["proposal"]["band"]
        actual_band = {band: int(item[f"{band}_copper"]) for band in PRICE_BANDS}
        if evidence_band != actual_band:
            raise ValueError(f"Container price band drifted: {key}")
        if not actual_band["quick"] <= actual_band["target"] <= actual_band["high"]:
            raise ValueError(f"Container price order is invalid: {key}")
    expected_report = render_report(evidence)
    if report != expected_report:
        raise ValueError("Container pricing report is stale")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--refresh", action="store_true")
    group.add_argument("--check", action="store_true")
    args = parser.parse_args()

    if args.refresh:
        evidence = build_evidence()
        sections = catalog_from_evidence(evidence)
        report = render_report(evidence)
        EVIDENCE_PATH.write_text(
            json.dumps(evidence, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
            newline="\n",
        )
        SECTIONS_PATH.write_text(
            json.dumps(sections, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
            newline="\n",
        )
        REPORT_PATH.write_text(report, encoding="utf-8", newline="\n")
        print(json.dumps(evidence["summary"], indent=2))
    else:
        evidence = load(EVIDENCE_PATH)
        sections = load(SECTIONS_PATH)
        report = REPORT_PATH.read_text(encoding="utf-8")

    validate(evidence, sections, report)
    print("Container Evidence Pricing review passed for 22 missing non-vendor containers.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
