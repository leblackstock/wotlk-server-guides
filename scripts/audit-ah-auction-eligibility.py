#!/usr/bin/env python3
"""Audit every AH item against pinned AzerothCore auction eligibility fields."""

from __future__ import annotations

import argparse
import csv
import datetime as dt
import json
import re
import urllib.request
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
INDEX_PATH = ROOT / "assets" / "ah-search-index.js"
ITEM_IDS_PATH = ROOT / "assets" / "ah-item-ids.js"
CRAFTED_PATH = ROOT / "data" / "ah-crafted-sections.json"
VENDOR_PATH = ROOT / "data" / "ah-vendor-sections.json"
BASELINE_PATH = ROOT / "data" / "ah-price-baselines.json"
COLLECTIBLE_AUDIT_PATH = ROOT / "data" / "ah-collectible-audit.json"
AUDIT_PATH = ROOT / "data" / "ah-auction-eligibility-audit.json"

ITEM_TEMPLATE_COMMIT = "e0fe11ba46b885a01e4a4038001e0055822cc7ba"
ITEM_TEMPLATE_URL = (
    "https://raw.githubusercontent.com/azerothcore/azerothcore-wotlk/"
    f"{ITEM_TEMPLATE_COMMIT}/data/sql/base/db_world/item_template.sql"
)
CONJURED_FLAG = 0x00000002
ALLOWED_BONDING = {0, 2, 3}
GENERATED_PAYLOAD = re.compile(r"window\.(\w+)=(\{.*?\});\n", re.DOTALL)


def generated_json(path: Path, variable: str) -> dict:
    source = path.read_text(encoding="utf-8")
    for match in GENERATED_PAYLOAD.finditer(source):
        if match.group(1) == variable:
            return json.loads(match.group(2))
    raise ValueError(f"Could not parse {variable} from {path.relative_to(ROOT)}")


def read_item_template(path: Path | None) -> str:
    if path:
        return path.read_text(encoding="utf-8", errors="replace")
    request = urllib.request.Request(
        ITEM_TEMPLATE_URL,
        headers={"User-Agent": "wotlk-server-guides-ah-eligibility-audit/1.0"},
    )
    with urllib.request.urlopen(request, timeout=120) as response:
        return response.read().decode("utf-8", errors="replace")


def parse_item_template(sql: str, target_ids: set[int]) -> dict[int, dict]:
    try:
        schema = sql.split("CREATE TABLE `item_template` (", 1)[1].split(
            "  PRIMARY KEY", 1
        )[0]
    except IndexError as error:
        raise ValueError("Could not locate the item_template schema") from error
    columns = re.findall(r"^  `([^`]+)` ", schema, re.MULTILINE)
    positions = {name: index for index, name in enumerate(columns)}
    required = {"entry", "name", "Flags", "bonding", "duration"}
    if not required <= positions.keys():
        raise ValueError(f"item_template schema is missing fields: {sorted(required - positions.keys())}")

    records: dict[int, dict] = {}
    for line in sql.splitlines():
        if not line.startswith("("):
            continue
        if line.endswith("),") or line.endswith(");"):
            body = line[1:-2]
        else:
            continue
        values = next(
            csv.reader(
                [body],
                delimiter=",",
                quotechar="'",
                escapechar="\\",
                doublequote=False,
                strict=True,
            )
        )
        if len(values) != len(columns):
            raise ValueError(
                f"Unexpected item_template field count: {len(values)} instead of {len(columns)}"
            )
        item_id = int(values[positions["entry"]])
        if item_id not in target_ids:
            continue
        records[item_id] = {
            "name": values[positions["name"]],
            "flags": int(values[positions["Flags"]]),
            "bonding": int(values[positions["bonding"]]),
            "duration": int(values[positions["duration"]]),
        }

    missing = sorted(target_ids - records.keys())
    if missing:
        raise ValueError(f"AzerothCore item_template is missing audited IDs: {missing}")
    return records


def merged_crafted_item(config: dict, key: str) -> dict:
    raw = config["catalog"][key]
    return (
        config.get("catalog_defaults", {})
        | config["price_profiles"][raw["profile"]]
        | raw
    )


def load_sources() -> dict:
    index = generated_json(INDEX_PATH, "AH_SEARCH_INDEX")
    item_ids = generated_json(ITEM_IDS_PATH, "AH_ITEM_IDS")
    crafted = json.loads(CRAFTED_PATH.read_text(encoding="utf-8"))
    vendor = json.loads(VENDOR_PATH.read_text(encoding="utf-8"))
    baseline = json.loads(BASELINE_PATH.read_text(encoding="utf-8"))
    collectible = (
        json.loads(COLLECTIBLE_AUDIT_PATH.read_text(encoding="utf-8"))
        if COLLECTIBLE_AUDIT_PATH.is_file()
        else {"items": {}}
    )

    indexed_names = {item["name"] for item in index.get("items", [])}
    search_ids = {int(item_id) for item_id in item_ids.values()}
    crafted_ids = {int(item["item_id"]) for item in crafted["catalog"].values()}
    vendor_ids = {int(item["item_id"]) for item in vendor["catalog"].values()}
    baseline_ids = {int(item_id) for item_id in baseline["items"]}
    collectible_ids = {int(item_id) for item_id in collectible["items"]}
    target_ids = search_ids | crafted_ids | vendor_ids | baseline_ids | collectible_ids

    memberships: dict[int, set[str]] = defaultdict(set)
    for label, item_set in {
        "search": search_ids,
        "crafted": crafted_ids,
        "vendor": vendor_ids,
        "baseline": baseline_ids,
        "collectible": collectible_ids,
    }.items():
        for item_id in item_set:
            memberships[item_id].add(label)

    guide_vendor_keys = {
        key
        for guide in vendor["guides"].values()
        for key in guide.get("items", [])
    }
    cost_only_ids: set[int] = set()
    for key, item in vendor["catalog"].items():
        item_id = int(item["item_id"])
        if item.get("cost_only"):
            if item.get("auctionable") is not False:
                raise ValueError(f"{key}: cost-only vendor item must set auctionable=false")
            if key in guide_vendor_keys:
                raise ValueError(f"{key}: cost-only vendor item leaked into a rendered guide")
            if item_id in search_ids or item_id in crafted_ids or item_id in baseline_ids:
                raise ValueError(f"{key}: cost-only vendor item leaked into an auctionable source")
            cost_only_ids.add(item_id)
        elif item.get("auctionable") is False:
            raise ValueError(f"{key}: non-auctionable vendor item is not marked cost_only")

    return {
        "index": index,
        "indexed_names": indexed_names,
        "item_ids": item_ids,
        "crafted": crafted,
        "vendor": vendor,
        "baseline": baseline,
        "collectible": collectible,
        "target_ids": target_ids,
        "memberships": memberships,
        "cost_only_ids": cost_only_ids,
    }


def eligibility_reasons(record: dict) -> list[str]:
    reasons: list[str] = []
    if int(record["bonding"]) not in ALLOWED_BONDING:
        reasons.append(f"bonding={record['bonding']}")
    if int(record["duration"]) != 0:
        reasons.append(f"duration={record['duration']}")
    if int(record["flags"]) & CONJURED_FLAG:
        reasons.append("conjured")
    return reasons


def build_audit(records: dict[int, dict], sources: dict) -> dict:
    return {
        "version": 1,
        "refreshed": dt.date.today().isoformat(),
        "item_template_source": {
            "name": "AzerothCore WotLK item_template",
            "commit": ITEM_TEMPLATE_COMMIT,
            "url": ITEM_TEMPLATE_URL,
        },
        "rules": {
            "allowed_bonding": sorted(ALLOWED_BONDING),
            "conjured_flag": CONJURED_FLAG,
            "required_duration": 0,
            "cost_only_exception": "A non-auctionable vendor input must set cost_only=true and auctionable=false and must not render or appear in search.",
        },
        "source_counts": {
            "search_item_ids": len({int(value) for value in sources["item_ids"].values()}),
            "crafted_item_ids": len(
                {int(item["item_id"]) for item in sources["crafted"]["catalog"].values()}
            ),
            "vendor_item_ids": len(
                {int(item["item_id"]) for item in sources["vendor"]["catalog"].values()}
            ),
            "baseline_item_ids": len({int(item_id) for item_id in sources["baseline"]["items"]}),
            "collectible_item_ids": len(
                {int(item_id) for item_id in sources["collectible"]["items"]}
            ),
            "unique_audited_item_ids": len(records),
        },
        "items": {str(item_id): records[item_id] for item_id in sorted(records)},
    }


def validate_audit(audit: dict, sources: dict) -> None:
    if int(audit.get("version", 0)) != 1:
        raise ValueError("Unsupported AH auction-eligibility audit version")
    source = audit.get("item_template_source", {})
    if source.get("commit") != ITEM_TEMPLATE_COMMIT:
        raise ValueError("Auction-eligibility audit uses the wrong AzerothCore commit")

    records = {int(item_id): record for item_id, record in audit.get("items", {}).items()}
    expected_ids = sources["target_ids"]
    if records.keys() != expected_ids:
        missing = sorted(expected_ids - records.keys())
        extra = sorted(records.keys() - expected_ids)
        raise ValueError(f"Auction-eligibility snapshot coverage changed; missing={missing}, extra={extra}")

    errors: list[str] = []
    for item_id, record in records.items():
        reasons = eligibility_reasons(record)
        if reasons and item_id not in sources["cost_only_ids"]:
            labels = ", ".join(sorted(sources["memberships"][item_id]))
            errors.append(f"{item_id} {record['name']} ({labels}): {', '.join(reasons)}")

    binding_names = {0: "none", 2: "boe", 3: "use"}
    crafted = sources["crafted"]
    for key, raw in crafted["catalog"].items():
        item_id = int(raw["item_id"])
        expected_binding = binding_names[int(records[item_id]["bonding"])]
        actual_binding = merged_crafted_item(crafted, key).get("binding", "none")
        if actual_binding != expected_binding:
            errors.append(
                f"{key}: binding metadata is {actual_binding}, expected {expected_binding}"
            )

    if errors:
        raise ValueError("Non-auctionable AH data remains:\n" + "\n".join(errors))

    expected_counts = {
        "search_item_ids": len({int(value) for value in sources["item_ids"].values()}),
        "crafted_item_ids": len(
            {int(item["item_id"]) for item in sources["crafted"]["catalog"].values()}
        ),
        "vendor_item_ids": len(
            {int(item["item_id"]) for item in sources["vendor"]["catalog"].values()}
        ),
        "baseline_item_ids": len({int(item_id) for item_id in sources["baseline"]["items"]}),
        "collectible_item_ids": len(
            {int(item_id) for item_id in sources["collectible"]["items"]}
        ),
        "unique_audited_item_ids": len(expected_ids),
    }
    if audit.get("source_counts") != expected_counts:
        raise ValueError(
            f"Auction-eligibility source counts are stale: {audit.get('source_counts')} != {expected_counts}"
        )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--item-template",
        type=Path,
        help="Use a local AzerothCore item_template.sql dump when refreshing.",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Validate the saved snapshot without network access or file writes.",
    )
    args = parser.parse_args()

    sources = load_sources()
    if args.check:
        if not AUDIT_PATH.is_file():
            raise ValueError("Auction-eligibility snapshot is missing")
        audit = json.loads(AUDIT_PATH.read_text(encoding="utf-8"))
    else:
        records = parse_item_template(read_item_template(args.item_template), sources["target_ids"])
        audit = build_audit(records, sources)
        AUDIT_PATH.write_text(
            json.dumps(audit, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
            newline="\n",
        )
        print(f"Updated {AUDIT_PATH.relative_to(ROOT)}")

    validate_audit(audit, sources)
    print(
        "AH auction eligibility is valid for "
        f"{len(sources['target_ids']):,} unique item IDs; "
        f"{len(sources['cost_only_ids'])} explicit cost-only exception."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
