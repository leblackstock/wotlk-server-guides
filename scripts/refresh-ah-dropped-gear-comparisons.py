#!/usr/bin/env python3
"""Refresh dropped-gear relative-rank diagnostics with three waited retries."""

from __future__ import annotations

import argparse
import importlib.util
import json
import statistics
from collections import Counter
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CATALOG_PATH = ROOT / "data" / "ah-dropped-gear.json"
BASELINE_PATH = ROOT / "data" / "ah-price-baselines.json"
CROSS_PATH = ROOT / "data" / "ah-dropped-gear-cross-server-diagnostics.json"
REVIEW_BASE_PATH = ROOT / "scripts" / "review-ah-blacksmithing-prices.py"
ANALYZER_PATH = ROOT / "scripts" / "analyze-ah-cross-server-diagnostics.py"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load {path.name}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


BASE = load_module("ah_dropped_comparison_base", REVIEW_BASE_PATH)
ANALYZER = load_module("ah_dropped_comparison_analyzer", ANALYZER_PATH)


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def build() -> dict:
    catalog = load(CATALOG_PATH)
    baseline = load(BASELINE_PATH)["items"]
    saved = load(CROSS_PATH)
    by_id = {int(item["item_id"]): item for item in catalog["catalog"].values()}
    tasks = []
    for source_key, (realm_id, faction_id) in BASE.SOURCE_IDS.items():
        scale = float(
            saved["sources"][source_key]["scale"]["external_gold_per_hellscream_gold"]
        )
        for item_id, item in by_id.items():
            tasks.append((source_key, item_id, item["name"], realm_id, faction_id, scale))
    observations, retry_summary = BASE.fetch_observations_with_retries(tasks)

    item_records = {}
    for item_id, item in sorted(by_id.items()):
        target = int(baseline[str(item_id)]["target"])
        realm_values: dict[str, list[float]] = {}
        for source_key, observation in observations[item_id].items():
            if not observation["present"]:
                continue
            realm = saved["sources"][source_key]["realm"]
            realm_values.setdefault(realm, []).append(
                observation["median_buyout_copper"] / observation["economy_scale"]
            )
        normalized_by_realm = {
            realm: statistics.median(values) for realm, values in realm_values.items()
        }
        realm_ratios = {
            realm: value / target for realm, value in normalized_by_realm.items()
        }
        ratios = list(realm_ratios.values())
        median_ratio = statistics.median(ratios) if len(ratios) >= 2 else None
        leave_one_out = []
        if len(ratios) >= 3:
            for omitted in sorted(realm_ratios):
                leave_one_out.append(
                    statistics.median(
                        value for realm, value in realm_ratios.items() if realm != omitted
                    )
                )
        sensitivity = (
            "stable-classification"
            if leave_one_out
            and len({ANALYZER.classify_ratio(value) for value in leave_one_out}) == 1
            else "sensitive-or-insufficient"
        )
        item_records[str(item_id)] = {
            "item_id": item_id,
            "name": item["name"],
            "realms_present": sorted(normalized_by_realm),
            "realm_count": len(normalized_by_realm),
            "faction_snapshots_present": sum(
                observation["present"] for observation in observations[item_id].values()
            ),
            "normalized_ask_ratio_to_hellscream_target": (
                round(median_ratio, 3) if median_ratio is not None else None
            ),
            "normalized_ratio_range": (
                [round(min(ratios), 3), round(max(ratios), 3)] if ratios else None
            ),
            "diagnostic": ANALYZER.classify_ratio(median_ratio),
            "leave_one_realm_out": sensitivity,
            "used_to_set_price": False,
        }

    source_refresh = {}
    for source_key in sorted(BASE.SOURCE_IDS):
        source_observations = [
            observations[item_id][source_key] for item_id in sorted(by_id)
        ]
        timestamps = sorted(
            observation["scan_timestamp"]
            for observation in source_observations
            if observation.get("scan_timestamp")
        )
        source_refresh[source_key] = {
            "items_present": sum(observation["present"] for observation in source_observations),
            "fetch_failures": sum(bool(observation.get("fetch_failed")) for observation in source_observations),
            "oldest_reported_scan": timestamps[0] if timestamps else None,
            "newest_reported_scan": timestamps[-1] if timestamps else None,
            "nominal_gold_saved": False,
        }

    saved["refreshed"] = date.today().isoformat()
    saved["rules"]["comparison_retry_rule"] = (
        "After the initial batch, wait 2, 5, and 10 seconds and retry only failed "
        "comparison requests before recording a final failure."
    )
    saved["rules"]["live_page_refresh_gold_saved"] = False
    saved["comparison_page_refresh"] = {
        "refreshed": date.today().isoformat(),
        "source": "https://ah.nerfed.net/servers/base?id=7",
        "role": "Current item-page asks refresh dimensionless coverage and relative rank only.",
        "saved_scale_role": "The six saved 2026-08-05 economy scales remain the fixed normalization calibration.",
        "retry_summary": retry_summary,
        "sources": source_refresh,
    }
    saved["summary"] = {
        "catalog_items": len(item_records),
        "sources": len(BASE.SOURCE_IDS),
        "realms": 3,
        "items_seen_on_at_least_two_realms": sum(
            record["realm_count"] >= 2 for record in item_records.values()
        ),
        "diagnostics": dict(
            sorted(Counter(record["diagnostic"] for record in item_records.values()).items())
        ),
        "final_failed_comparison_requests": retry_summary["final_failed_requests"],
    }
    saved["items"] = item_records
    return saved


def validate(data: dict) -> None:
    if len(data.get("items", {})) != 347:
        raise ValueError("Expected 347 dropped-gear comparison records")
    if data.get("rules", {}).get("external_asks_used_to_set_prices") is not False:
        raise ValueError("External asks must not set dropped-gear prices")
    if data.get("rules", {}).get("live_page_refresh_gold_saved") is not False:
        raise ValueError("Nominal comparison-page gold must not be saved")
    retry = data.get("comparison_page_refresh", {}).get("retry_summary", {})
    if retry.get("initial_requests") != 2_082:
        raise ValueError("Expected 2,082 dropped-gear comparison requests")
    if retry.get("retry_delays_seconds") != [2, 5, 10]:
        raise ValueError("Dropped-gear three-wait retry rule is missing")
    for item_id, record in data["items"].items():
        if int(item_id) != record["item_id"]:
            raise ValueError(f"Dropped-gear comparison ID drifted: {item_id}")
        if record.get("used_to_set_price") is not False:
            raise ValueError(f"External ask leaked into price: {record['name']}")
        if "normalized_gold" in record or "median_buyout_copper" in record:
            raise ValueError(f"Nominal external gold was saved: {record['name']}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--refresh", action="store_true")
    group.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if args.refresh:
        data = build()
        validate(data)
        CROSS_PATH.write_text(
            json.dumps(data, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
            newline="\n",
        )
        print(json.dumps({"summary": data["summary"], "retry": data["comparison_page_refresh"]["retry_summary"]}, indent=2))
        return 0
    data = load(CROSS_PATH)
    validate(data)
    print("Dropped-gear comparison refresh covers 347 items and the three-wait retry rule.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
