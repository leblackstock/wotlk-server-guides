#!/usr/bin/env python3
"""Build gold-scale-normalized cross-server dropped-gear diagnostics.

Raw Web Auctioneer downloads remain outside the repository. The committed file
contains only source hashes, benchmark coverage, scale indexes, availability,
and dimensionless normalized ratios. External asks never update a baseline.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import math
import re
import statistics
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CATALOG_PATH = ROOT / "data" / "ah-dropped-gear.json"
BASELINE_PATH = ROOT / "data" / "ah-price-baselines.json"
OUTPUT_PATH = ROOT / "data" / "ah-dropped-gear-cross-server-diagnostics.json"
IMPORTER_PATH = ROOT / "scripts" / "import-ah-dropped-gear-evidence.py"

BENCHMARKS = {
    2770: "Copper Ore",
    7912: "Solid Stone",
    8170: "Rugged Leather",
    21886: "Primal Life",
    22452: "Primal Earth",
    36912: "Saronite Ore",
}

SOURCE_METADATA = {
    "lordaeron-horde": {
        "realm": "Lordaeron",
        "faction": "Horde",
        "progression": "WotLK 3.3.5 end state",
        "rates": "x1 realm; harder raid tuning; restricted gear shop",
    },
    "lordaeron-alliance": {
        "realm": "Lordaeron",
        "faction": "Alliance",
        "progression": "WotLK 3.3.5 end state",
        "rates": "x1 realm; harder raid tuning; restricted gear shop",
    },
    "icecrown-horde": {
        "realm": "Icecrown",
        "faction": "Horde",
        "progression": "WotLK 3.3.5 end state",
        "rates": "x7 experience and x3 gold/profession/reputation; gear shop present",
    },
    "icecrown-alliance": {
        "realm": "Icecrown",
        "faction": "Alliance",
        "progression": "WotLK 3.3.5 end state",
        "rates": "x7 experience and x3 gold/profession/reputation; gear shop present",
    },
    "onyxia-horde": {
        "realm": "Onyxia",
        "faction": "Horde",
        "progression": "progressive realm advancing toward WotLK",
        "rates": "x1 experience through level 80 per current Warmane FAQ",
    },
    "onyxia-alliance": {
        "realm": "Onyxia",
        "faction": "Alliance",
        "progression": "progressive realm advancing toward WotLK",
        "rates": "x1 experience through level 80 per current Warmane FAQ",
    },
}


def load_importer():
    spec = importlib.util.spec_from_file_location("ah_dropped_evidence_importer", IMPORTER_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("Could not load dropped-gear evidence importer")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def median_int(values: list[int]) -> int:
    return round(statistics.median(values))


def classify_ratio(value: float | None) -> str:
    if value is None:
        return "insufficient-external-coverage"
    if value < 0.5:
        return "normalized-asks-below-hellscream-target"
    if value > 2.0:
        return "normalized-asks-above-hellscream-target"
    return "normalized-asks-broadly-aligned"


def scan_prices(path: Path, item_ids: set[int], importer) -> tuple[dict[int, list[int]], dict]:
    prices: dict[int, list[int]] = defaultdict(list)
    current_realm: str | None = None
    current_faction: str | None = None
    in_ropes = False
    timestamps: list[int] = []
    total_rows = 0
    with path.open(encoding="utf-8") as stream:
        for line in stream:
            tabs = len(line) - len(line.lstrip("\t"))
            match = importer.TABLE_KEY.match(line)
            if match:
                key = importer.quoted_value(f'"{match.group(1)}"')
                if tabs == 2:
                    current_realm = key
                    current_faction = None
                    in_ropes = False
                elif tabs == 3:
                    current_faction = key
                    in_ropes = False
                elif tabs == 4 and key == "ropes":
                    in_ropes = True
                continue
            time_match = re.match(r'^\s*\["LastFullScan"\]\s*=\s*(\d+)', line)
            if time_match:
                timestamps.append(int(time_match.group(1)))
                continue
            if not in_ropes or tabs != 5:
                continue
            value_match = importer.STRING_VALUE.match(line)
            if not value_match:
                continue
            rope = importer.quoted_value(value_match.group(1))
            for fields in importer.lua_row_tokens(rope):
                total_rows += 1
                if len(fields) < 23:
                    continue
                try:
                    count = int(fields[10])
                    buyout = int(fields[16])
                    item_id = int(fields[22])
                except ValueError:
                    continue
                if item_id in item_ids and count > 0 and buyout > 0:
                    prices[item_id].append(round(buyout / count))
    return prices, {
        "embedded_realm": current_realm,
        "embedded_faction": current_faction,
        "latest_full_scan_timestamp": max(timestamps, default=None),
        "auction_rows": total_rows,
    }


def robust_scale(local_prices: dict[int, int], external_prices: dict[int, int]) -> dict:
    ratios = {
        item_id: external_prices[item_id] / local_prices[item_id]
        for item_id in sorted(set(local_prices) & set(external_prices))
        if local_prices[item_id] > 0 and external_prices[item_id] > 0
    }
    if len(ratios) < 3:
        raise ValueError("A cross-server source needs at least three benchmark items")
    logs = {item_id: math.log(value) for item_id, value in ratios.items()}
    center = statistics.median(logs.values())
    deviations = [abs(value - center) for value in logs.values()]
    mad = statistics.median(deviations)
    threshold = max(3 * 1.4826 * mad, math.log(4))
    kept = {item_id: value for item_id, value in logs.items() if abs(value - center) <= threshold}
    if len(kept) < 3:
        kept = logs
    index = math.exp(statistics.median(kept.values()))
    return {
        "external_gold_per_hellscream_gold": round(index, 4),
        "benchmarks_available": len(ratios),
        "benchmarks_used": len(kept),
        "benchmark_ids_used": sorted(kept),
        "benchmark_ids_excluded_as_log_outliers": sorted(set(logs) - set(kept)),
        "log_mad": round(mad, 4),
        "confidence": "diagnostic-only",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--beancounter", required=True, type=Path)
    parser.add_argument(
        "--source",
        action="append",
        default=[],
        metavar="KEY=PATH",
        help="External scan source; use each declared realm/faction key exactly once",
    )
    parser.add_argument("--out", type=Path, default=OUTPUT_PATH)
    args = parser.parse_args()
    provided: dict[str, Path] = {}
    for raw in args.source:
        key, separator, value = raw.partition("=")
        if not separator or key not in SOURCE_METADATA:
            parser.error(f"Invalid source {raw!r}")
        provided[key] = Path(value)
    if set(provided) != set(SOURCE_METADATA):
        parser.error("Provide every declared Lordaeron, Icecrown, and Onyxia faction source")

    importer = load_importer()
    catalog = json.loads(CATALOG_PATH.read_text(encoding="utf-8"))
    baseline = json.loads(BASELINE_PATH.read_text(encoding="utf-8"))["items"]
    catalog_by_id = {int(item["item_id"]): item for item in catalog["catalog"].values()}
    requested_ids = set(catalog_by_id) | set(BENCHMARKS)
    sales, _ = importer.parse_beancounter(args.beancounter, "Garrosh", set(BENCHMARKS))
    local_benchmark_prices = {
        item_id: median_int([row["unit_price"] for row in sales.get(item_id, [])])
        for item_id in BENCHMARKS
        if sales.get(item_id)
    }
    if len(local_benchmark_prices) < 5:
        raise ValueError("At least five Hellscream benchmark commodities need completed sales")

    external_prices: dict[str, dict[int, int]] = {}
    source_records = {}
    for key in sorted(provided):
        path = provided[key]
        if not path.is_file():
            parser.error(f"Missing source file for {key}: {path}")
        prices, scan = scan_prices(path, requested_ids, importer)
        medians = {item_id: median_int(values) for item_id, values in prices.items()}
        scale = robust_scale(local_benchmark_prices, medians)
        metadata = SOURCE_METADATA[key]
        if scan["embedded_realm"] != metadata["realm"] or scan["embedded_faction"] != metadata["faction"]:
            raise ValueError(f"{key}: embedded realm/faction does not match declared source")
        external_prices[key] = medians
        source_records[key] = {
            **metadata,
            "source_url": (
                "https://ah.nerfed.net/servers/base?id=7"
            ),
            "snapshot_sha256": sha256(path),
            "latest_full_scan_timestamp": scan["latest_full_scan_timestamp"],
            "auction_rows": scan["auction_rows"],
            "catalog_items_present": sum(item_id in medians for item_id in catalog_by_id),
            "scale": scale,
        }

    realm_values: dict[str, dict[int, list[float]]] = defaultdict(lambda: defaultdict(list))
    for key, medians in external_prices.items():
        source = source_records[key]
        scale = float(source["scale"]["external_gold_per_hellscream_gold"])
        realm = source["realm"]
        for item_id, price in medians.items():
            if item_id in catalog_by_id:
                realm_values[realm][item_id].append(price / scale)

    item_records = {}
    for item_id, item in sorted(catalog_by_id.items()):
        target = int(baseline[str(item_id)]["target"])
        normalized_by_realm = {
            realm: statistics.median(values)
            for realm, items in realm_values.items()
            if (values := items.get(item_id))
        }
        realm_ratios = {
            realm: value / target for realm, value in normalized_by_realm.items()
        }
        ratio_values = list(realm_ratios.values())
        median_ratio = statistics.median(ratio_values) if len(ratio_values) >= 2 else None
        leave_one_out = []
        if len(ratio_values) >= 3:
            for omitted in sorted(realm_ratios):
                values = [value for realm, value in realm_ratios.items() if realm != omitted]
                leave_one_out.append(statistics.median(values))
        sensitivity = (
            "stable-classification"
            if leave_one_out
            and len({classify_ratio(value) for value in leave_one_out}) == 1
            else "sensitive-or-insufficient"
        )
        item_records[str(item_id)] = {
            "item_id": item_id,
            "name": item["name"],
            "realms_present": sorted(normalized_by_realm),
            "realm_count": len(normalized_by_realm),
            "faction_snapshots_present": sum(
                item_id in medians for medians in external_prices.values()
            ),
            "normalized_ask_ratio_to_hellscream_target": (
                round(median_ratio, 3) if median_ratio is not None else None
            ),
            "normalized_ratio_range": (
                [round(min(ratio_values), 3), round(max(ratio_values), 3)]
                if ratio_values
                else None
            ),
            "diagnostic": classify_ratio(median_ratio),
            "leave_one_realm_out": sensitivity,
            "used_to_set_price": False,
        }

    output = {
        "version": 1,
        "refreshed": date.today().isoformat(),
        "scope": (
            "Dimensionless cross-server availability and relative-rank diagnostics. "
            "No external gold value, seller identity, or raw download is committed."
        ),
        "rules": {
            "external_asks_used_to_set_prices": False,
            "normalization": (
                "For each realm/faction, median external-to-Hellscream unit-price ratios are "
                "calculated in log space from six shared commodity benchmarks with actual local "
                "completed sales; log outliers beyond a robust MAD threshold are excluded."
            ),
            "item_comparison": (
                "External item asks are divided by their source economy index, combined by realm, "
                "then expressed only as a ratio to the saved Hellscream target."
            ),
            "history_limit": (
                "The source sites expose current auctions and listing-price/volume history, but "
                "do not identify disappearance as sale versus cancellation or expiration."
            ),
            "stability_limit": (
                "One snapshot per realm/faction cannot establish stable availability or turnover."
            ),
        },
        "benchmark_basket": {
            str(item_id): {
                "item_id": item_id,
                "name": BENCHMARKS[item_id],
                "local_completed_buyouts": len(sales.get(item_id, [])),
                "local_units": sum(row["stack"] for row in sales.get(item_id, [])),
                "local_distinct_buyers": len({row["buyer"] for row in sales.get(item_id, [])}),
                "local_distinct_days": len({row["day"] for row in sales.get(item_id, [])}),
            }
            for item_id in sorted(BENCHMARKS)
        },
        "sources": source_records,
        "summary": {
            "catalog_items": len(item_records),
            "sources": len(source_records),
            "realms": 3,
            "items_seen_on_at_least_two_realms": sum(
                record["realm_count"] >= 2 for record in item_records.values()
            ),
            "diagnostics": dict(
                sorted(Counter(record["diagnostic"] for record in item_records.values()).items())
            ),
        },
        "items": item_records,
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(output["summary"], indent=2))
    print(
        json.dumps(
            {
                key: record["scale"] for key, record in source_records.items()
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
