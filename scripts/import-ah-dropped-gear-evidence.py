#!/usr/bin/env python3
"""Import sanitized dropped-gear sales and supply evidence from Auctioneer data.

The source SavedVariables files remain outside the repository. This importer
stores only aggregate evidence for audited dropped-gear item IDs; it never
stores character, buyer, seller, account, or source-path identifiers.
"""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
import re
import statistics
from collections import Counter, defaultdict
from datetime import date, datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CATALOG_PATH = ROOT / "data" / "ah-dropped-gear.json"
DEFAULT_OUTPUT = ROOT / "data" / "ah-dropped-gear-price-evidence.json"
SALE_SECTIONS = {"completedAuctions", "completedAuctionsNeutral"}
TABLE_KEY = re.compile(r'^\s*\["((?:\\.|[^"\\])*)"\]\s*=\s*\{')
STRING_VALUE = re.compile(r'^\s*("(?:\\.|[^"\\])*")')


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def utc_date(timestamp: int) -> str:
    return datetime.fromtimestamp(timestamp, tz=timezone.utc).date().isoformat()


def utc_datetime(timestamp: float) -> str:
    return datetime.fromtimestamp(timestamp, tz=timezone.utc).replace(microsecond=0).isoformat()


def quoted_value(source: str) -> str:
    """Decode a simple Lua %q string using its Python-compatible escapes."""
    try:
        return ast.literal_eval(source)
    except (SyntaxError, ValueError) as exc:
        raise ValueError("Unsupported quoted SavedVariables value") from exc


def nearest_quantile(values: list[int], fraction: float) -> int | None:
    if not values:
        return None
    ordered = sorted(values)
    index = round((len(ordered) - 1) * fraction)
    return ordered[index]


def price_summary(values: list[int]) -> dict[str, int | None]:
    if not values:
        return {"min": None, "q1": None, "median": None, "q3": None, "max": None}
    return {
        "min": min(values),
        "q1": nearest_quantile(values, 0.25),
        "median": round(statistics.median(values)),
        "q3": nearest_quantile(values, 0.75),
        "max": max(values),
    }


def ratio(numerator: int, denominator: int) -> float | None:
    if denominator <= 0:
        return None
    return round(numerator / denominator, 4)


def parse_characters(path: Path, realm: str) -> set[str]:
    characters: set[str] = set()
    current_realm: str | None = None
    with path.open(encoding="utf-8") as stream:
        for line in stream:
            tabs = len(line) - len(line.lstrip("\t"))
            match = TABLE_KEY.match(line)
            if not match:
                continue
            key = quoted_value(f'"{match.group(1)}"')
            if tabs == 1:
                current_realm = key
            elif tabs == 2 and current_realm == realm:
                characters.add(key.casefold())
    return characters


def parse_beancounter(path: Path, realm: str, item_ids: set[int]) -> tuple[dict[int, list[dict]], dict]:
    owned_characters = parse_characters(path, realm)
    sales: dict[int, list[dict]] = defaultdict(list)
    exclusions = Counter()
    seen: set[tuple[int, str, str]] = set()
    current_realm: str | None = None
    current_section: str | None = None
    current_item_id: int | None = None
    current_item_string: str | None = None
    records_seen = 0

    with path.open(encoding="utf-8") as stream:
        for line in stream:
            tabs = len(line) - len(line.lstrip("\t"))
            match = TABLE_KEY.match(line)
            if match:
                key = quoted_value(f'"{match.group(1)}"')
                if tabs == 1:
                    current_realm = key
                    current_section = None
                elif tabs == 3:
                    current_section = key
                    current_item_id = None
                elif tabs == 4:
                    try:
                        current_item_id = int(key)
                    except ValueError:
                        current_item_id = None
                elif tabs == 5:
                    current_item_string = key
                continue

            if (
                current_realm != realm
                or current_section not in SALE_SECTIONS
                or current_item_id not in item_ids
                or tabs < 6
            ):
                continue
            value_match = STRING_VALUE.match(line)
            if not value_match:
                continue
            records_seen += 1
            raw_record = quoted_value(value_match.group(1))
            signature = (current_item_id, current_item_string or "", raw_record)
            if signature in seen:
                exclusions["duplicate"] += 1
                continue
            seen.add(signature)
            fields = raw_record.split(";")
            if len(fields) < 8:
                exclusions["malformed"] += 1
                continue
            try:
                stack = int(fields[0])
                money = int(fields[1])
                deposit = int(fields[2])
                fee = int(fields[3])
                buyout = int(fields[4]) if fields[4] else 0
                buyer = fields[6]
                timestamp = int(fields[7])
            except ValueError:
                exclusions["malformed"] += 1
                continue
            if stack <= 0 or timestamp <= 0:
                exclusions["malformed"] += 1
                continue
            gross = money - deposit + fee
            if buyout <= 0 or gross != buyout:
                exclusions["bid_or_unmatched"] += 1
                continue
            if buyer.casefold() in owned_characters:
                exclusions["self_purchase"] += 1
                continue
            sales[current_item_id].append(
                {
                    "stack": stack,
                    "unit_price": round(gross / stack),
                    "buyer": buyer.casefold(),
                    "day": utc_date(timestamp),
                }
            )

    return sales, {
        "records_seen_for_catalog_items": records_seen,
        "valid_completed_buyouts": sum(len(rows) for rows in sales.values()),
        "excluded_records": dict(sorted(exclusions.items())),
        "owned_character_exclusions_available": True,
        "known_friend_or_guild_exclusions_available": False,
    }


def lua_row_tokens(source: str):
    """Yield scalar tokens for every first-level row in a packed scan rope."""
    start = source.find("{")
    if start < 0:
        return
    depth = 0
    in_string = False
    escaped = False
    row_start: int | None = None
    for index in range(start, len(source)):
        char = source[index]
        if in_string:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                in_string = False
            continue
        if char == '"':
            in_string = True
        elif char == "{":
            depth += 1
            if depth == 2:
                row_start = index + 1
        elif char == "}":
            if depth == 2 and row_start is not None:
                yield split_lua_scalars(source[row_start:index])
                row_start = None
            depth -= 1


def split_lua_scalars(row: str) -> list[str]:
    fields: list[str] = []
    start = 0
    in_string = False
    escaped = False
    for index, char in enumerate(row):
        if in_string:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                in_string = False
        elif char == '"':
            in_string = True
        elif char == ",":
            fields.append(row[start:index].strip())
            start = index + 1
    if row[start:].strip():
        fields.append(row[start:].strip())
    return fields


def parse_scan(
    path: Path,
    realm: str,
    item_ids: set[int],
    owned_characters: set[str],
) -> tuple[dict[int, list[dict]], dict]:
    listings: dict[int, list[dict]] = defaultdict(list)
    current_realm: str | None = None
    current_faction: str | None = None
    in_ropes = False
    scan_timestamps: dict[str, int] = {}
    malformed_rows = 0
    total_rows = 0

    with path.open(encoding="utf-8") as stream:
        for line in stream:
            tabs = len(line) - len(line.lstrip("\t"))
            match = TABLE_KEY.match(line)
            if match:
                key = quoted_value(f'"{match.group(1)}"')
                if tabs == 2:
                    current_realm = key
                    current_faction = None
                    in_ropes = False
                elif tabs == 3 and current_realm == realm:
                    current_faction = key
                    in_ropes = False
                elif tabs == 4 and key == "ropes" and current_realm == realm:
                    in_ropes = True
                continue
            if current_realm != realm or current_faction is None:
                continue
            timestamp_match = re.match(r'^\s*\["LastFullScan"\]\s*=\s*(\d+)', line)
            if timestamp_match:
                scan_timestamps[current_faction] = int(timestamp_match.group(1))
                continue
            if in_ropes and tabs == 5:
                value_match = STRING_VALUE.match(line)
                if not value_match:
                    continue
                rope = quoted_value(value_match.group(1))
                for fields in lua_row_tokens(rope):
                    total_rows += 1
                    if len(fields) < 23:
                        malformed_rows += 1
                        continue
                    try:
                        count = int(fields[10])
                        buyout = int(fields[16])
                        item_id = int(fields[22])
                    except ValueError:
                        malformed_rows += 1
                        continue
                    if item_id not in item_ids or count <= 0:
                        continue
                    seller = fields[19]
                    if seller.startswith('"') and seller.endswith('"'):
                        seller = quoted_value(seller).casefold()
                    else:
                        seller = ""
                    listings[item_id].append(
                        {
                            "faction": current_faction,
                            "count": count,
                            "seller": seller,
                            "owned_account": seller in owned_characters,
                            "has_buyout": buyout > 0,
                        }
                    )

    return listings, {
        "auction_rows_in_snapshot": total_rows,
        "malformed_rows": malformed_rows,
        "faction_scan_dates_utc": {
            faction: utc_date(timestamp) for faction, timestamp in sorted(scan_timestamps.items())
        },
        "listing_prices_saved": False,
        "listing_prices_used_to_set_baselines": False,
        "known_account_exclusions_available": bool(owned_characters),
        "known_friend_or_guild_exclusions_available": False,
    }


def sale_record(rows: list[dict]) -> dict:
    buyer_units = Counter()
    for row in rows:
        buyer_units[row["buyer"]] += row["stack"]
    units = sum(row["stack"] for row in rows)
    buyers = len(buyer_units)
    days = sorted({row["day"] for row in rows})
    max_share = ratio(max(buyer_units.values(), default=0), units)
    if len(rows) >= 4 and buyers >= 2 and len(days) >= 2 and (max_share or 0) <= 0.5:
        gate = "medium"
        coverage = "stronger-medium" if len(rows) >= 8 and buyers >= 4 and len(days) >= 4 else "medium"
    elif rows:
        gate = "low"
        coverage = "sparse-or-concentrated"
    else:
        gate = "fallback"
        coverage = "none"
    return {
        "completed_buyouts": len(rows),
        "units": units,
        "distinct_buyers": buyers,
        "distinct_days": len(days),
        "first_sale_date_utc": days[0] if days else None,
        "last_sale_date_utc": days[-1] if days else None,
        "largest_buyer_unit_share": max_share,
        "gross_unit_copper": price_summary([row["unit_price"] for row in rows]),
        "evidence_gate": gate,
        "coverage": coverage,
    }


def supply_record(rows: list[dict]) -> dict:
    independent_rows = [row for row in rows if not row["owned_account"]]
    seller_units = Counter()
    for row in independent_rows:
        seller_units[row["seller"] or "unknown"] += row["count"]
    units = sum(row["count"] for row in independent_rows)
    owned_rows = [row for row in rows if row["owned_account"]]
    return {
        "auction_rows": len(independent_rows),
        "units": units,
        "distinct_sellers": len(seller_units),
        "largest_seller_unit_share": ratio(max(seller_units.values(), default=0), units),
        "rows_with_buyout": sum(row["has_buyout"] for row in independent_rows),
        "owned_account_rows_excluded": len(owned_rows),
        "owned_account_units_excluded": sum(row["count"] for row in owned_rows),
        "classification": "present-one-snapshot" if independent_rows else "absent-one-snapshot",
        "diagnostic_only": True,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--beancounter", required=True, type=Path)
    parser.add_argument("--scan", required=True, type=Path)
    parser.add_argument("--realm", default="Garrosh")
    parser.add_argument("--out", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    catalog = json.loads(CATALOG_PATH.read_text(encoding="utf-8"))
    by_id = {int(item["item_id"]): (key, item) for key, item in catalog["catalog"].items()}
    item_ids = set(by_id)
    for source in (args.beancounter, args.scan):
        if not source.is_file():
            parser.error(f"Input does not exist: {source}")

    owned_characters = parse_characters(args.beancounter, args.realm)
    sales, sales_summary = parse_beancounter(args.beancounter, args.realm, item_ids)
    listings, scan_summary = parse_scan(args.scan, args.realm, item_ids, owned_characters)
    items = {}
    for item_id in sorted(item_ids):
        key, item = by_id[item_id]
        items[str(item_id)] = {
            "item_id": item_id,
            "canonical_key": key,
            "name": item["name"],
            "guide_id": item["guide_id"],
            "section_id": item["section_id"],
            "realized_sales": sale_record(sales.get(item_id, [])),
            "current_supply": supply_record(listings.get(item_id, [])),
        }

    gate_counts = Counter(record["realized_sales"]["evidence_gate"] for record in items.values())
    present = sum(record["current_supply"]["auction_rows"] > 0 for record in items.values())
    output = {
        "version": 1,
        "refreshed": date.today().isoformat(),
        "scope": "Sanitized Hellscream/Garrosh realized-sales and one-snapshot supply evidence for the 347 audited dropped-gear items.",
        "privacy": {
            "raw_savedvariables_committed": False,
            "source_paths_committed": False,
            "character_names_committed": False,
            "buyer_or_seller_names_committed": False,
            "identity_hashes_committed": False,
            "only_aggregate_identity_counts_committed": True,
        },
        "rules": {
            "gross_sale_copper": "BeanCounter money - deposit + fee; accepted only when equal to recorded buyout.",
            "unit_price": "Gross completed-buyout copper divided by stack size.",
            "gear_medium_gate": "At least 4 completed buyouts, 2 distinct buyers, and 2 distinct UTC days, with largest buyer unit share at most 0.50.",
            "gear_stronger_medium_coverage": "At least 8 completed buyouts, 4 distinct buyers, and 4 distinct UTC days, while still passing the medium concentration gate.",
            "active_listings_used_to_set_prices": False,
        },
        "source_snapshots": {
            "beancounter": {
                "sha256": file_sha256(args.beancounter),
                "modified_utc": utc_datetime(args.beancounter.stat().st_mtime),
                **sales_summary,
            },
            "auction_scan": {
                "sha256": file_sha256(args.scan),
                "modified_utc": utc_datetime(args.scan.stat().st_mtime),
                **scan_summary,
            },
        },
        "summary": {
            "catalog_items": len(items),
            "items_by_realized_sales_gate": dict(sorted(gate_counts.items())),
            "items_present_in_current_supply_snapshot": present,
            "items_absent_from_current_supply_snapshot": len(items) - present,
        },
        "items": items,
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(output, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(output["summary"], indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
