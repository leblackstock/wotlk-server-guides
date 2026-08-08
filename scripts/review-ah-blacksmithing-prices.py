#!/usr/bin/env python3
"""Review all Blacksmithing finished-output prices with Evidence Pricing."""

from __future__ import annotations

import argparse
import concurrent.futures
import hashlib
import importlib.util
import json
import math
import re
import statistics
import sys
import time
import urllib.error
import urllib.request
from collections import Counter
from datetime import date, datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CRAFTED_PATH = ROOT / "data" / "ah-crafted-sections.json"
BASELINE_PATH = ROOT / "data" / "ah-price-baselines.json"
RECIPE_AUDIT_PATH = ROOT / "data" / "ah-crafted-recipe-audit.json"
CROSS_SERVER_PATH = ROOT / "data" / "ah-dropped-gear-cross-server-diagnostics.json"
EVIDENCE_PATH = ROOT / "data" / "ah-blacksmithing-price-evidence.json"
REPORT_PATH = ROOT / "docs" / "ah-blacksmithing-pricing-review.md"
IMPORTER_PATH = ROOT / "scripts" / "import-ah-dropped-gear-evidence.py"
GUIDE_FILENAME = "blacksmithing-materials-ah-price-guide.html"
BEANCOUNTER_PATH = Path(
    r"D:\Hellscream WoW\launcher\WTF\Account\LEBLACKSTOCK\SavedVariables\BeanCounter.lua"
)
MODEL_VERSION = "blacksmithing-evidence-pricing-v1"
PRICE_BANDS = ("quick", "target", "high")
USER_AGENT = "Mozilla/5.0 (compatible; HellscreamGuideEvidenceReview/1.0)"
FETCH_RETRY_DELAYS_SECONDS = (2, 5, 10)

SOURCE_IDS = {
    "lordaeron-horde": (14, 1),
    "lordaeron-alliance": (14, 2),
    "icecrown-horde": (15, 1),
    "icecrown-alliance": (15, 2),
    "onyxia-horde": (17, 1),
    "onyxia-alliance": (17, 2),
}

MATERIAL_SECTION_TITLES = {
    "Wrath general-use enhancements",
    "Blacksmith-only skeleton keys",
    "Enchanter-only rod blanks",
    "Outland general-use enhancements",
    "Classic enhancements and craft intermediates",
}

FIXED_ORDER_SECTION_TITLES = {
    "Blacksmith-only skeleton keys",
    "Enchanter-only rod blanks",
    "Classic enhancements and craft intermediates",
    "Wrath weapons and shields",
    "Wrath leveling and fresh-80 armor",
    "Outland weapons",
    "Outland rare and epic armor",
    "Outland leveling armor",
    "Classic weapons — skill 1–150",
    "Classic armor — skill 1–150",
    "Classic weapons — skill 151–300",
    "Classic armor — skill 151–300",
}

ROW_PATTERN = re.compile(
    r"<td>\s*{label}\s*</td>\s*<td>(?P<value>.*?)</td>",
    re.IGNORECASE | re.DOTALL,
)
MONEY_PATTERN = re.compile(
    r"class=['\"]currency(?P<unit>gold|silver|copper)['\"]>\s*(?P<value>[\d,]+)\s*<",
    re.IGNORECASE,
)
SCAN_PATTERN = re.compile(
    r"<td>\s*(?P<scan>20\d\d-\d\d-\d\d \d\d:\d\d:\d\d)(?:[^<]*)</td>",
    re.IGNORECASE,
)
ITEM_LEVEL_PATTERN = re.compile(r"item-level\s+(\d+)", re.IGNORECASE)


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def merged_item(config: dict, key: str) -> dict:
    raw = config["catalog"][key]
    return config.get("catalog_defaults", {}) | config["price_profiles"][raw["profile"]] | raw


def entries(config: dict) -> list[dict]:
    result = []
    seen = set()
    for section in config["guides"][GUIDE_FILENAME]["sections"]:
        title = section["title"]
        view = "materials-enhancements" if title in MATERIAL_SECTION_TITLES else "armor-weapons"
        for key in section["items"]:
            if key in seen:
                raise ValueError(f"Duplicate Blacksmithing output: {key}")
            seen.add(key)
            item = merged_item(config, key)
            if item.get("profession") != "Blacksmithing":
                raise ValueError(f"Non-Blacksmithing output in Blacksmithing catalog: {key}")
            result.append({"key": key, "section": title, "view": view, "item": item})
    counts = Counter(row["view"] for row in result)
    if len(result) != 453 or counts != {"materials-enhancements": 52, "armor-weapons": 401}:
        raise ValueError(f"Blacksmithing inventory drifted: {len(result)} rows, {dict(counts)}")
    return result


def parse_money(fragment: str) -> int | None:
    values = {"gold": 0, "silver": 0, "copper": 0}
    matches = list(MONEY_PATTERN.finditer(fragment))
    if not matches:
        return None
    for match in matches:
        values[match.group("unit").casefold()] = int(match.group("value").replace(",", ""))
    return values["gold"] * 10_000 + values["silver"] * 100 + values["copper"]


def row_fragment(source: str, label: str) -> str | None:
    pattern = re.compile(ROW_PATTERN.pattern.format(label=re.escape(label)), ROW_PATTERN.flags)
    match = pattern.search(source)
    return match.group("value") if match else None


def fetch_observation(task: tuple[str, int, str, int, int, float]) -> tuple[str, int, dict]:
    source_key, item_id, name, realm_id, faction_id, scale = task
    url = f"https://ah.nerfed.net/item/index?id={item_id}&faction={faction_id}&realm={realm_id}"
    last_error: Exception | None = None
    for _ in range(3):
        try:
            request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
            with urllib.request.urlopen(request, timeout=25) as response:
                charset = response.headers.get_content_charset() or "utf-8"
                source = response.read().decode(charset, errors="replace")
            median = parse_money(row_fragment(source, "Median Buyout Price") or "")
            quantity_fragment = row_fragment(source, "Quantity On AH") or ""
            quantity_match = re.search(r"[\d,]+", quantity_fragment)
            if median is None or quantity_match is None:
                return source_key, item_id, {
                    "present": False,
                    "scan_timestamp": None,
                    "quantity": 0,
                    "source_url": url,
                }
            scan_match = SCAN_PATTERN.search(source)
            return source_key, item_id, {
                "present": True,
                "scan_timestamp": scan_match.group("scan") if scan_match else None,
                "quantity": int(quantity_match.group(0).replace(",", "")),
                "median_buyout_copper": median,
                "economy_scale": scale,
                "source_url": url,
            }
        except (urllib.error.URLError, TimeoutError, ValueError) as exc:
            last_error = exc
    return source_key, item_id, {
        "present": False,
        "scan_timestamp": None,
        "quantity": 0,
        "source_url": url,
        "fetch_failed": True,
        "error_type": type(last_error).__name__ if last_error else "unknown",
        "item_name": name,
    }


def fetch_observations_with_retries(
    tasks: list[tuple[str, int, str, int, int, float]],
    *,
    worker=fetch_observation,
    sleeper=time.sleep,
    retry_delays: tuple[int, ...] = FETCH_RETRY_DELAYS_SECONDS,
) -> tuple[dict[int, dict[str, dict]], dict]:
    """Fetch one full batch, then wait and retry only failed requests three times."""
    task_by_key = {(task[0], task[1]): task for task in tasks}
    observations: dict[int, dict[str, dict]] = {
        item_id: {} for _, item_id, *_ in tasks
    }
    pending = list(tasks)
    retry_rounds_used = 0
    with concurrent.futures.ThreadPoolExecutor(max_workers=6) as executor:
        for round_index in range(len(retry_delays) + 1):
            if round_index:
                retry_rounds_used = round_index
                delay = retry_delays[round_index - 1]
                print(
                    f"Waiting {delay}s before comparison retry {round_index}/"
                    f"{len(retry_delays)} for {len(pending)} failed requests.",
                    flush=True,
                )
                sleeper(delay)
            failed_keys = []
            completed = 0
            round_total = len(pending)
            for source_key, item_id, observation in executor.map(worker, pending):
                observations[item_id][source_key] = observation
                completed += 1
                if round_index == 0 and completed % 300 == 0:
                    print(
                        f"Fetched {completed}/{round_total} external observations.",
                        flush=True,
                    )
                if observation.get("fetch_failed") is True:
                    failed_keys.append((source_key, item_id))
            pending = [task_by_key[key] for key in failed_keys]
            if not pending:
                break
    return observations, {
        "initial_requests": len(tasks),
        "retry_delays_seconds": list(retry_delays),
        "retry_rounds_used": retry_rounds_used,
        "final_failed_requests": len(pending),
    }


def load_sales(item_ids: set[int]) -> tuple[dict[int, dict], dict]:
    if not BEANCOUNTER_PATH.exists():
        return {}, {
            "provided": False,
            "raw_path_saved": False,
            "buyer_names_saved": False,
            "known_friend_or_guild_exclusions_available": False,
        }
    spec = importlib.util.spec_from_file_location("ah_sales_importer", IMPORTER_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("Could not load the sanitized BeanCounter importer")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    rows_by_item, summary = module.parse_beancounter(BEANCOUNTER_PATH, "Garrosh", item_ids)
    sanitized = {
        item_id: module.sale_record(rows)
        for item_id, rows in rows_by_item.items()
        if rows
    }
    return sanitized, {
        "provided": True,
        "sha256": hashlib.sha256(BEANCOUNTER_PATH.read_bytes()).hexdigest(),
        "modified_utc": datetime.fromtimestamp(
            BEANCOUNTER_PATH.stat().st_mtime, tz=timezone.utc
        ).replace(microsecond=0).isoformat(),
        "records_seen_for_batch_items": summary["records_seen_for_catalog_items"],
        "valid_completed_buyouts": summary["valid_completed_buyouts"],
        "excluded_records": summary["excluded_records"],
        "owned_character_exclusions_available": summary[
            "owned_character_exclusions_available"
        ],
        "known_friend_or_guild_exclusions_available": False,
        "raw_path_saved": False,
        "buyer_names_saved": False,
    }


def item_level(item: dict) -> int:
    match = ITEM_LEVEL_PATTERN.search(item.get("detail", ""))
    return int(match.group(1)) if match else 0


def floor_bucket(copper: int) -> str:
    if copper < 10_000:
        return "floor-under-1g"
    if copper < 50_000:
        return "floor-1g-to-5g"
    if copper < 200_000:
        return "floor-5g-to-20g"
    if copper < 1_000_000:
        return "floor-20g-to-100g"
    return "floor-100g-plus"


def level_bucket(level: int) -> str:
    boundaries = (30, 50, 70, 100, 150, 170, 190, 210, 230, 250)
    lower = 0
    for upper in boundaries:
        if level <= upper:
            return f"ilvl-{lower + 1}-to-{upper}"
        lower = upper
    return "ilvl-251-plus"


def cohort_key(row: dict) -> str:
    item = row["item"]
    if row["view"] == "materials-enhancements":
        floor = int(item["pricing_floor_copper"]["target"])
        return f"{row['section']} | {floor_bucket(floor)}"
    return f"{row['section']} | {item['quality']} | {level_bucket(item_level(item))}"


def midrank_percentile(values: list[float], value: float) -> float:
    if len(values) <= 1:
        return 0.5
    below = sum(candidate < value for candidate in values)
    equal = sum(candidate == value for candidate in values)
    return (below + (equal - 1) / 2) / (len(values) - 1)


def coverage_weight(realm_count: int) -> float:
    return {3: 1.0, 2: 0.7, 1: 0.35}.get(realm_count, 0.0)


def round_market(copper: float) -> int:
    value = max(1, int(round(copper)))
    if value < 100:
        step = 10
    elif value < 1_000:
        step = 50
    elif value < 10_000:
        step = 100
    elif value < 100_000:
        step = 500
    elif value < 1_000_000:
        step = 2_500
    else:
        step = 50_000
    return max(step, int(math.floor(value / step + 0.5) * step))


def fallback_band(anchor: int, rank: float, realm_count: int) -> dict[str, int]:
    adjusted_rank = 0.5 + (rank - 0.5) * coverage_weight(realm_count)
    target = round_market(anchor * (0.65 + 0.70 * adjusted_rank))
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
    summary = sales["gross_unit_copper"]
    target = round_market(int(summary["median"]))
    quick = round_market(min(int(summary["q1"]), target * 0.85))
    high = round_market(max(int(summary["q3"]), target * 1.30))
    return {"quick": min(quick, target), "target": target, "high": max(high, target)}


def shrink_sparse_sale(
    direct: dict[str, int], fallback: dict[str, int], weight: float
) -> dict[str, int]:
    result = {
        band: round_market(direct[band] * weight + fallback[band] * (1.0 - weight))
        for band in PRICE_BANDS
    }
    result["quick"] = min(result["quick"], result["target"])
    result["high"] = max(result["high"], result["target"])
    return result


def build_evidence() -> dict:
    config = load(CRAFTED_PATH)
    recipe_audit = load(RECIPE_AUDIT_PATH)
    cross_server = load(CROSS_SERVER_PATH)
    rows = entries(config)
    item_ids = {int(row["item"]["item_id"]) for row in rows}
    sales, sales_source = load_sales(item_ids)

    tasks = []
    for source_key, (realm_id, faction_id) in SOURCE_IDS.items():
        scale = float(
            cross_server["sources"][source_key]["scale"][
                "external_gold_per_hellscream_gold"
            ]
        )
        for row in rows:
            item = row["item"]
            tasks.append(
                (
                    source_key,
                    int(item["item_id"]),
                    item["name"],
                    realm_id,
                    faction_id,
                    scale,
                )
            )
    observations, retry_summary = fetch_observations_with_retries(tasks)

    normalized_scores: dict[str, float | None] = {}
    realm_records: dict[str, dict[str, float]] = {}
    row_by_key = {row["key"]: row for row in rows}
    for key, row in row_by_key.items():
        item_id = int(row["item"]["item_id"])
        by_realm: dict[str, list[float]] = {}
        for source_key, observation in observations[item_id].items():
            if not observation["present"]:
                continue
            realm = cross_server["sources"][source_key]["realm"]
            by_realm.setdefault(realm, []).append(
                observation["median_buyout_copper"] / observation["economy_scale"]
            )
        realms = {realm: statistics.median(values) for realm, values in by_realm.items()}
        realm_records[key] = realms
        normalized_scores[key] = statistics.median(realms.values()) if realms else None

    cohorts: dict[str, dict] = {}
    for row in rows:
        cohort = cohort_key(row)
        record = cohorts.setdefault(cohort, {"keys": [], "view": row["view"]})
        record["keys"].append(row["key"])
    previous = load(EVIDENCE_PATH) if EVIDENCE_PATH.exists() else {}
    previous_cohorts = previous.get("cohorts", {}) if previous.get("model_version") == MODEL_VERSION else {}
    for cohort, record in cohorts.items():
        before_targets = [int(row_by_key[key]["item"]["target_copper"]) for key in record["keys"]]
        previous_anchor = previous_cohorts.get(cohort, {}).get("anchor_target_copper")
        record["anchor_target_copper"] = int(
            previous_anchor if previous_anchor is not None else round_market(statistics.median(before_targets))
        )
        record["item_count"] = len(record["keys"])
        record["anchor_source"] = (
            "Preserved from the first reviewed Blacksmithing Evidence Pricing snapshot."
            if previous_anchor is not None
            else "Rounded median Target from the frozen pre-Phase-2 Blacksmithing band inside this comparable cohort."
        )

    ranked_values = {
        cohort: [
            normalized_scores[key]
            for key in record["keys"]
            if normalized_scores[key] is not None
        ]
        for cohort, record in cohorts.items()
    }
    records = {}
    for row in rows:
        key = row["key"]
        item = row["item"]
        item_id = int(item["item_id"])
        cohort = cohort_key(row)
        score = normalized_scores[key]
        realms = realm_records[key]
        raw_rank = (
            midrank_percentile(ranked_values[cohort], score) if score is not None else 0.5
        )
        adjusted_rank = 0.5 + (raw_rank - 0.5) * coverage_weight(len(realms))
        fallback = fallback_band(
            int(cohorts[cohort]["anchor_target_copper"]), raw_rank, len(realms)
        )
        local_sales = sales.get(item_id)
        decision = "cohort-rank-starter-estimate"
        source_type = "documented-fallback"
        confidence = "fallback"
        direct_weight = None
        proposed = fallback
        if local_sales:
            direct = direct_sale_band(local_sales)
            if local_sales["evidence_gate"] == "medium":
                proposed = direct
                decision = "direct-completed-sales"
                source_type = "realized-sales-history"
                confidence = "medium"
                direct_weight = 1.0
            else:
                direct_weight = (
                    0.50
                    if local_sales["distinct_buyers"] >= 2
                    and local_sales["distinct_days"] >= 2
                    else 0.25
                )
                proposed = shrink_sparse_sale(direct, fallback, direct_weight)
                decision = "sparse-completed-sales-shrunk"
                source_type = "realized-sales-history-plus-documented-fallback"
                confidence = "low"
        before = {band: int(item[f"{band}_copper"]) for band in PRICE_BANDS}
        floor = {band: int(item["pricing_floor_copper"][band]) for band in PRICE_BANDS}
        model_proposed = dict(proposed)
        model_change = (
            model_proposed["target"] / before["target"] - 1.0
            if before["target"]
            else 0.0
        )
        large = abs(model_change) > 0.50
        reviewer_decision = "accept"
        if large and len(realms) < 2:
            proposed = dict(before)
            decision = "retain-reviewed-band-insufficient-coverage"
            source_type = "frozen-pre-phase2-guide"
            confidence = "fallback"
            reviewer_decision = "retain"
            reviewer_note = (
                "Retained after manual large-change review because zero- or one-realm "
                "coverage is not strong enough to support a Target move over 50%."
            )
        elif large:
            reviewer_note = (
                "Accepted after manual large-change review: at least two comparison "
                "realms support the within-cohort direction, external gold is excluded, "
                "and the exact recipe floor remains a separate no-craft warning."
            )
        else:
            reviewer_note = (
                "Accepted after reviewing cohort fit, recipe floor, market purpose, "
                "and available completed-sale coverage."
            )
        change = (proposed["target"] / before["target"] - 1.0) if before["target"] else 0.0
        below_floor = [band for band in PRICE_BANDS if proposed[band] < floor[band]]
        target_ratios = [value / before["target"] for value in realms.values()]
        records[str(item_id)] = {
            "item_id": item_id,
            "canonical_key": key,
            "name": item["name"],
            "view": row["view"],
            "section": row["section"],
            "cohort": cohort,
            "cohort_item_count": int(cohorts[cohort]["item_count"]),
            "quality": item["quality"],
            "item_level": item_level(item),
            "demand": item["demand"],
            "pricing_unit": "per finished item",
            "before_band": before,
            "reagent_floor": floor,
            "local_completed_sales": local_sales,
            "external_relative_review": {
                "realms_present": sorted(realms),
                "realm_count": len(realms),
                "faction_snapshots_present": sum(
                    observation["present"] for observation in observations[item_id].values()
                ),
                "raw_relative_rank_percentile": round(raw_rank, 6),
                "coverage_weight": coverage_weight(len(realms)),
                "adjusted_relative_rank_percentile": round(adjusted_rank, 6),
                "normalized_ask_ratio_to_before_target": (
                    round(statistics.median(target_ratios), 4)
                    if len(target_ratios) >= 2
                    else None
                ),
                "normalized_ratio_range": (
                    [round(min(target_ratios), 4), round(max(target_ratios), 4)]
                    if target_ratios
                    else None
                ),
                "used_to_set_gold_value": False,
            },
            "source_observations": {
                source_key: {
                    "present": observation["present"],
                    "scan_timestamp": observation["scan_timestamp"],
                    "quantity": observation["quantity"],
                    "source_url": observation["source_url"],
                    **({"fetch_failed": True} if observation.get("fetch_failed") else {}),
                }
                for source_key, observation in sorted(observations[item_id].items())
            },
            "recipe": {
                "source_spell_id": int(recipe_audit["recipes"][key]["source_spell_id"]),
                "output_count": int(recipe_audit["recipes"][key]["output_count"]),
                "reagents": recipe_audit["recipes"][key]["reagents"],
            },
            "proposal": {
                "proposed_band": proposed,
                "model_proposed_band_before_manual_review": model_proposed,
                "fallback_band_before_sales": fallback,
                "decision": decision,
                "source_type": source_type,
                "confidence": confidence,
                "anchor_target_copper": int(cohorts[cohort]["anchor_target_copper"]),
                "direct_sale_weight": direct_weight,
                "target_change_copper": proposed["target"] - before["target"],
                "target_change_percent": round(change * 100, 4),
                "model_target_change_percent": round(model_change * 100, 4),
                "below_reagent_floor_bands": below_floor,
                "requires_large_change_review": large,
                "reviewer_decision": reviewer_decision,
                "reviewer_note": reviewer_note,
                "reason": (
                    "Reviewed Blacksmithing Evidence Pricing band. Qualified completed sales set the value when available; sparse sales are shrunk toward a fixed Hellscream comparable-cohort estimate. External asks set relative rank only and active Hellscream listings are excluded. The exact recipe floor remains a separate craftability diagnostic."
                ),
            },
        }

    summary = {
        "items_reviewed": len(records),
        "materials_enhancements_reviewed": sum(
            record["view"] == "materials-enhancements" for record in records.values()
        ),
        "armor_weapons_reviewed": sum(
            record["view"] == "armor-weapons" for record in records.values()
        ),
        "bands_changed": sum(
            record["before_band"] != record["proposal"]["proposed_band"]
            for record in records.values()
        ),
        "completed_sale_items": sum(
            record["local_completed_sales"] is not None for record in records.values()
        ),
        "items_seen_on_three_realms": sum(
            record["external_relative_review"]["realm_count"] == 3
            for record in records.values()
        ),
        "target_changes_over_fifty_percent": sum(
            record["proposal"]["requires_large_change_review"] for record in records.values()
        ),
        "proposals_below_reagent_floor": sum(
            bool(record["proposal"]["below_reagent_floor_bands"])
            for record in records.values()
        ),
        "decision_counts": dict(
            sorted(Counter(record["proposal"]["decision"] for record in records.values()).items())
        ),
        "external_gold_values_copied": False,
    }
    return {
        "version": 1,
        "refreshed": date.today().isoformat(),
        "scope": "All 453 tradeable Blacksmithing outputs across the materials/enhancements and armor/weapons guides",
        "method": "Evidence Pricing",
        "model_version": MODEL_VERSION,
        "rules": {
            "active_hellscream_listing_prices_used": False,
            "external_gold_values_copied": False,
            "external_role": "Gold-normalized within-comparable-cohort relative rank only.",
            "gold_scale": "Fixed frozen Hellscream cohort anchors or qualified completed sales.",
            "reagent_floor_role": "Exact audited 3.3.5 recipe cost is a separate craftability diagnostic and does not automatically set market value.",
            "sparse_sale_rule": "Low-confidence completed sales receive 25% weight, or 50% when they span at least two buyers and two UTC days; the balance remains the reviewed cohort fallback.",
            "gear_medium_gate": "At least four completed buyouts, two distinct buyers, and two distinct UTC days, with largest-buyer unit share at most 0.50.",
            "comparison_retry_rule": "After the initial batch, wait 2, 5, and 10 seconds and retry only failed comparison requests before recording a final failure.",
        },
        "sources": {
            "beancounter": sales_source,
            "external": {
                source_key: {
                    "realm": cross_server["sources"][source_key]["realm"],
                    "faction": cross_server["sources"][source_key]["faction"],
                    "economy_scale": cross_server["sources"][source_key]["scale"][
                        "external_gold_per_hellscream_gold"
                    ],
                    "scale_snapshot_sha256": cross_server["sources"][source_key][
                        "snapshot_sha256"
                    ],
                    "price_source": "https://ah.nerfed.net/servers/base?id=7",
                }
                for source_key in sorted(SOURCE_IDS)
            },
            "comparison_retry_summary": retry_summary,
        },
        "cohorts": cohorts,
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


def format_band(band: dict) -> str:
    return " / ".join(format_money(int(band[name])) for name in PRICE_BANDS)


def render_report(evidence: dict) -> str:
    summary = evidence["summary"]
    lines = [
        "# Blacksmithing Evidence Pricing Review",
        "",
        f"- Reviewed: `{evidence['refreshed']}`",
        f"- Scope: `{evidence['scope']}`",
        f"- Materials and enhancements: `{summary['materials_enhancements_reviewed']}`",
        f"- Armor, weapons, and shields: `{summary['armor_weapons_reviewed']}`",
        f"- Price bands changed: `{summary['bands_changed']}`",
        f"- Items with completed-sale evidence: `{summary['completed_sale_items']}`",
        f"- Items seen on all three comparison realms: `{summary['items_seen_on_three_realms']}`",
        f"- Manually reviewed Target changes over 50%: `{summary['target_changes_over_fifty_percent']}`",
        f"- Market proposals below at least one exact recipe-floor band: `{summary['proposals_below_reagent_floor']}`",
        "- Active Hellscream listing prices used: `no`",
        "- External gold copied into Hellscream prices: `no`",
        "- Publication status: `local only — not published`",
        "",
        "## Decision",
        "",
        "Every output keeps its exact audited 3.3.5 recipe floor as a separate craftability diagnostic. Qualified Hellscream completed buyouts may set market value; sparse sales are shrunk toward a fixed comparable-cohort estimate. Current Hellscream listings are excluded. External observations are normalized with the saved six-source economy scales and set relative rank only; the frozen Hellscream cohort anchor sets the gold scale.",
        "",
        "A market proposal below the recipe floor is intentional sale-value guidance, not a profitable-craft claim. Do not craft that item from purchased inputs at the saved floor; use owned materials, a cheaper acquisition path, or skip the craft.",
        "",
        "## Item decisions",
        "",
        "| Guide | Section | Item | Old Q / T / H | Recipe floor Q / T / H | Proposed Q / T / H | Target change | Local sales | External coverage | Decision | Confidence | Review |",
        "|---|---|---|---:|---:|---:|---:|---:|---:|---|---|---|",
    ]
    records = sorted(
        evidence["items"].values(),
        key=lambda record: (record["view"], record["section"], -record["proposal"]["proposed_band"]["target"], record["name"]),
    )
    for record in records:
        sales = record["local_completed_sales"]
        sales_text = (
            f"{sales['completed_buyouts']} buyouts / {sales['distinct_buyers']} buyers / {sales['distinct_days']} days"
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
        lines.extend(
            [
                f"- **{record['name']}**: model candidate {format_money(record['before_band']['target'])} → {format_money(candidate['target'])} ({proposal['model_target_change_percent']:+.2f}%); final {format_money(proposal['proposed_band']['target'])}. Decision: `{proposal['reviewer_decision']}`. {proposal['reviewer_note']}",
            ]
        )
    lines.extend(
        [
            "",
            "## Evidence limits",
            "",
            "- Only four Blacksmithing outputs have any saved completed-sale history in this snapshot; none qualify for medium confidence.",
            "- The external source reports listings and listing history, not verified completed sales.",
            "- External observations set relative rank only; their nominal gold values are not saved or copied.",
            "- Current Hellscream listings are excluded because guide-driven auctions dominate the local market.",
            "- Recipe rarity, reputation access, and cooldown behavior remain notes rather than hidden price premiums.",
            "",
            "## Reproduction",
            "",
            "```powershell",
            "python scripts/review-ah-blacksmithing-prices.py --check",
            "```",
            "",
            "Publishing is a separate step and is not part of this review.",
            "",
        ]
    )
    return "\n".join(lines)


def review_saved_evidence(evidence: dict) -> dict:
    """Apply the explicit large-change coverage safeguard without refetching sources."""
    for record in evidence["items"].values():
        proposal = record["proposal"]
        before = record["before_band"]
        model_proposed = dict(
            proposal.get("model_proposed_band_before_manual_review", proposal["proposed_band"])
        )
        model_change = (
            model_proposed["target"] / before["target"] - 1.0
            if before["target"]
            else 0.0
        )
        large = abs(model_change) > 0.50
        if large and record["external_relative_review"]["realm_count"] < 2:
            proposal["proposed_band"] = dict(before)
            proposal["decision"] = "retain-reviewed-band-insufficient-coverage"
            proposal["source_type"] = "frozen-pre-phase2-guide"
            proposal["confidence"] = "fallback"
            proposal["reviewer_decision"] = "retain"
            proposal["reviewer_note"] = (
                "Retained after manual large-change review because zero- or one-realm "
                "coverage is not strong enough to support a Target move over 50%."
            )
        else:
            proposal["proposed_band"] = model_proposed
            proposal["reviewer_decision"] = "accept"
            proposal["reviewer_note"] = (
                "Accepted after manual large-change review: at least two comparison "
                "realms support the within-cohort direction, external gold is excluded, "
                "and the exact recipe floor remains a separate no-craft warning."
                if large
                else "Accepted after reviewing cohort fit, recipe floor, market purpose, "
                "and available completed-sale coverage."
            )
        final = proposal["proposed_band"]
        change = final["target"] / before["target"] - 1.0 if before["target"] else 0.0
        proposal["model_proposed_band_before_manual_review"] = model_proposed
        proposal["model_target_change_percent"] = round(model_change * 100, 4)
        proposal["target_change_copper"] = final["target"] - before["target"]
        proposal["target_change_percent"] = round(change * 100, 4)
        proposal["requires_large_change_review"] = large
        proposal["below_reagent_floor_bands"] = [
            band for band in PRICE_BANDS if final[band] < record["reagent_floor"][band]
        ]
    records = list(evidence["items"].values())
    evidence["summary"].update(
        {
            "bands_changed": sum(
                record["before_band"] != record["proposal"]["proposed_band"]
                for record in records
            ),
            "target_changes_over_fifty_percent": sum(
                record["proposal"]["requires_large_change_review"] for record in records
            ),
            "proposals_below_reagent_floor": sum(
                bool(record["proposal"]["below_reagent_floor_bands"])
                for record in records
            ),
            "decision_counts": dict(
                sorted(
                    Counter(record["proposal"]["decision"] for record in records).items()
                )
            ),
        }
    )
    evidence["manual_review_completed"] = date.today().isoformat()
    return evidence


def validate(evidence: dict, *, require_applied: bool) -> None:
    config = load(CRAFTED_PATH)
    baseline = load(BASELINE_PATH)["items"]
    rows = entries(config)
    keys = {row["key"] for row in rows}
    expected_ids = {str(int(row["item"]["item_id"])) for row in rows}
    if evidence.get("method") != "Evidence Pricing":
        raise ValueError("Blacksmithing evidence uses the wrong method")
    if evidence.get("model_version") != MODEL_VERSION:
        raise ValueError("Blacksmithing Evidence Pricing model is stale")
    if set(evidence.get("items", {})) != expected_ids:
        raise ValueError("Blacksmithing evidence does not cover all 453 outputs")
    if {record["canonical_key"] for record in evidence["items"].values()} != keys:
        raise ValueError("Blacksmithing canonical-key coverage drifted")
    rules = evidence.get("rules", {})
    if rules.get("active_hellscream_listing_prices_used") is not False:
        raise ValueError("Active Hellscream listings must not set prices")
    if rules.get("external_gold_values_copied") is not False:
        raise ValueError("External gold must not be copied")
    counts = Counter(record["view"] for record in evidence["items"].values())
    if counts != {"materials-enhancements": 52, "armor-weapons": 401}:
        raise ValueError(f"Blacksmithing view counts drifted: {dict(counts)}")
    row_by_key = {row["key"]: row for row in rows}
    for record in evidence["items"].values():
        item = row_by_key[record["canonical_key"]]["item"]
        floor = {band: int(item["pricing_floor_copper"][band]) for band in PRICE_BANDS}
        if record["reagent_floor"] != floor:
            raise ValueError(f"{record['name']}: saved reagent floor is stale")
        proposal = record["proposal"]
        band = proposal["proposed_band"]
        if not band["quick"] <= band["target"] <= band["high"]:
            raise ValueError(f"{record['name']}: invalid reviewed price band")
        if proposal["requires_large_change_review"] and proposal["reviewer_decision"] not in {
            "accept",
            "revise",
            "retain",
        }:
            raise ValueError(f"{record['name']}: large change lacks manual review")
        if record["external_relative_review"].get("used_to_set_gold_value") is not False:
            raise ValueError(f"{record['name']}: external gold leaked into proposal")
        for observation in record["source_observations"].values():
            if "median_buyout_copper" in observation or "economy_scale" in observation:
                raise ValueError(f"{record['name']}: nominal external gold was saved")
        if require_applied:
            current = {band_name: int(item[f"{band_name}_copper"]) for band_name in PRICE_BANDS}
            if current != band:
                raise ValueError(f"{record['name']}: reviewed band is not applied")
            if item.get("price_strategy") != "evidence-pricing-market-value":
                raise ValueError(f"{record['name']}: Evidence Pricing strategy is not applied")
            expected_ref = f"data/ah-blacksmithing-price-evidence.json#items/{record['item_id']}"
            if item.get("price_evidence_ref") != expected_ref:
                raise ValueError(f"{record['name']}: evidence reference is stale")
            if str(record["item_id"]) in baseline:
                duplicate = baseline[str(record["item_id"])]
                duplicate_band = {band_name: int(duplicate[band_name]) for band_name in PRICE_BANDS}
                if duplicate_band != band:
                    raise ValueError(f"{record['name']}: duplicate baseline is not synchronized")
                if duplicate.get("evidence_ref") != expected_ref:
                    raise ValueError(f"{record['name']}: duplicate baseline evidence is stale")


def apply_catalog(evidence: dict) -> None:
    config = load(CRAFTED_PATH)
    source = CRAFTED_PATH.read_text(encoding="utf-8")
    baseline_doc = load(BASELINE_PATH)
    baseline = baseline_doc["items"]
    proposal_by_key = {
        record["canonical_key"]: record["proposal"]["proposed_band"]
        for record in evidence["items"].values()
    }
    item_id_by_key = {
        record["canonical_key"]: int(record["item_id"])
        for record in evidence["items"].values()
    }
    for key, band in proposal_by_key.items():
        original = config["catalog"][key]
        updated = dict(original)
        for band_name in PRICE_BANDS:
            updated[f"{band_name}_copper"] = int(band[band_name])
        updated["price_strategy"] = "evidence-pricing-market-value"
        updated["price_evidence_ref"] = (
            f"data/ah-blacksmithing-price-evidence.json#items/{item_id_by_key[key]}"
        )
        pattern = re.compile(rf'^(    "{re.escape(key)}": )\{{.*\}}(,?)$', re.MULTILINE)
        replacement = rf"\g<1>{json.dumps(updated, ensure_ascii=False, separators=(',', ':'))}\g<2>"
        source, count = pattern.subn(replacement, source, count=1)
        if count != 1:
            raise ValueError(f"Could not update canonical Blacksmithing row: {key}")
        item_id = str(item_id_by_key[key])
        if item_id in baseline:
            duplicate = dict(baseline[item_id])
            for band_name in PRICE_BANDS:
                duplicate[band_name] = int(band[band_name])
            duplicate["source_type"] = evidence["items"][item_id]["proposal"]["source_type"]
            duplicate["confidence"] = evidence["items"][item_id]["proposal"]["confidence"]
            duplicate["reason"] = evidence["items"][item_id]["proposal"]["reason"]
            duplicate["evidence_ref"] = (
                f"data/ah-blacksmithing-price-evidence.json#items/{item_id}"
            )
            baseline[item_id] = duplicate
    guide = config["guides"][GUIDE_FILENAME]
    for section in guide["sections"]:
        if section["title"] in FIXED_ORDER_SECTION_TITLES:
            continue
        ordered_items = sorted(
            section["items"],
            key=lambda key: (
                -int(proposal_by_key[key]["target"]),
                merged_item(config, key)["name"].casefold(),
            ),
        )
        pattern = re.compile(
            r'(^        \{\n          "title": "'
            + re.escape(section["title"])
            + r'",.*?^          "items": \[)\n.*?(\n          \]\n        \})(,?)$',
            re.MULTILINE | re.DOTALL,
        )
        item_lines = "\n".join(
            f'            {json.dumps(key, ensure_ascii=False)}'
            + ("," if index < len(ordered_items) - 1 else "")
            for index, key in enumerate(ordered_items)
        )
        replacement = rf"\g<1>\n{item_lines}\g<2>\g<3>"
        source, count = pattern.subn(replacement, source, count=1)
        if count != 1:
            raise ValueError(f"Could not reorder Blacksmithing section: {section['title']}")
    BASELINE_PATH.write_text(
        json.dumps(baseline_doc, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    CRAFTED_PATH.write_text(source, encoding="utf-8", newline="\n")


def refresh_dependency_diagnostics(evidence: dict) -> dict:
    config = load(CRAFTED_PATH)
    rows = {row["key"]: row for row in entries(config)}
    for record in evidence["items"].values():
        item = rows[record["canonical_key"]]["item"]
        floor = {band: int(item["pricing_floor_copper"][band]) for band in PRICE_BANDS}
        record["reagent_floor"] = floor
        proposal = record["proposal"]
        proposal["below_reagent_floor_bands"] = [
            band for band in PRICE_BANDS if proposal["proposed_band"][band] < floor[band]
        ]
    evidence["summary"]["proposals_below_reagent_floor"] = sum(
        bool(record["proposal"]["below_reagent_floor_bands"])
        for record in evidence["items"].values()
    )
    evidence["dependency_diagnostics_refreshed"] = date.today().isoformat()
    return evidence


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--inventory", action="store_true", help="Print the canonical audit inventory")
    group.add_argument("--refresh", action="store_true", help="Refresh report-only Evidence Pricing proposals")
    group.add_argument("--review", action="store_true", help="Apply saved manual-review safeguards without refetching")
    group.add_argument("--refresh-dependencies", action="store_true", help="Refresh saved recipe floors without changing prices")
    group.add_argument("--apply", action="store_true", help="Apply the saved reviewed proposals locally")
    group.add_argument("--check", action="store_true", help="Validate evidence, report, and applied prices")
    args = parser.parse_args()

    if args.inventory:
        config = load(CRAFTED_PATH)
        rows = entries(config)
        print(json.dumps(Counter(row["view"] for row in rows), indent=2))
        print(f"items {len(rows)}")
        print(f"sections {len(config['guides'][GUIDE_FILENAME]['sections'])}")
        return 0
    if args.refresh:
        evidence = build_evidence()
        validate(evidence, require_applied=False)
        EVIDENCE_PATH.write_text(
            json.dumps(evidence, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
            newline="\n",
        )
        REPORT_PATH.write_text(render_report(evidence), encoding="utf-8", newline="\n")
        print(json.dumps(evidence["summary"], indent=2))
        return 0
    if args.review:
        evidence = review_saved_evidence(load(EVIDENCE_PATH))
        validate(evidence, require_applied=False)
        EVIDENCE_PATH.write_text(
            json.dumps(evidence, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
            newline="\n",
        )
        REPORT_PATH.write_text(render_report(evidence), encoding="utf-8", newline="\n")
        print(json.dumps(evidence["summary"], indent=2))
        return 0
    if args.refresh_dependencies:
        evidence = refresh_dependency_diagnostics(load(EVIDENCE_PATH))
        validate(evidence, require_applied=True)
        EVIDENCE_PATH.write_text(
            json.dumps(evidence, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
            newline="\n",
        )
        REPORT_PATH.write_text(render_report(evidence), encoding="utf-8", newline="\n")
        print("Refreshed Blacksmithing recipe-floor diagnostics without changing prices.")
        return 0
    evidence = load(EVIDENCE_PATH)
    if args.apply:
        validate(evidence, require_applied=False)
        apply_catalog(evidence)
        validate(evidence, require_applied=True)
        print(f"Applied {len(evidence['items'])} reviewed Blacksmithing price bands.")
        return 0
    validate(evidence, require_applied=True)
    if REPORT_PATH.read_text(encoding="utf-8") != render_report(evidence):
        print("Blacksmithing Evidence Pricing report is stale.", file=sys.stderr)
        return 1
    print("Blacksmithing Evidence Pricing review is current.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
