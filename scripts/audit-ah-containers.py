#!/usr/bin/env python3
"""Build and validate the complete pinned auctionable-container inventory."""

from __future__ import annotations

import argparse
import importlib.util
import json
import re
import urllib.request
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
AUDIT_PATH = ROOT / "data" / "ah-container-audit.json"
CONTAINER_PATH = ROOT / "data" / "ah-container-sections.json"
CRAFTED_PATH = ROOT / "data" / "ah-crafted-sections.json"
RECIPE_PATH = ROOT / "data" / "ah-crafted-recipe-audit.json"
VENDOR_PATH = ROOT / "data" / "ah-vendor-sections.json"
DROP_AUDIT_SCRIPT = ROOT / "scripts" / "audit-ah-dropped-gear.py"

SOURCE_COMMIT = "e0fe11ba46b885a01e4a4038001e0055822cc7ba"
SOURCE_ROOT = (
    "https://raw.githubusercontent.com/azerothcore/azerothcore-wotlk/"
    f"{SOURCE_COMMIT}/data/sql/base/db_world"
)
SOURCE_FILES = (
    "item_template.sql",
    "creature_loot_template.sql",
    "gameobject_loot_template.sql",
    "item_loot_template.sql",
    "reference_loot_template.sql",
    "creature_template.sql",
    "gameobject_template.sql",
    "npc_vendor.sql",
    "quest_template.sql",
)
CONTAINER_CLASSES = {1, 11}
ALLOWED_BONDING = {0, 2}
CONJURED_FLAG = 0x2
QUALITY_NAMES = {
    0: "poor",
    1: "common",
    2: "uncommon",
    3: "rare",
    4: "epic",
    5: "legendary",
}


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load {path.name}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


DROP = load_module("ah_container_drop_source", DROP_AUDIT_SCRIPT)


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def read_sources() -> dict[str, str]:
    sources: dict[str, str] = {}
    for filename in SOURCE_FILES:
        request = urllib.request.Request(
            f"{SOURCE_ROOT}/{filename}",
            headers={"User-Agent": "wotlk-server-guides-container-audit/1.0"},
        )
        with urllib.request.urlopen(request, timeout=120) as response:
            sources[filename] = response.read().decode("utf-8", errors="replace")
    return sources


def item_records(sql: str) -> dict[int, dict]:
    positions, rows = DROP.parse_table(sql, "item_template")
    required = {
        "entry",
        "name",
        "class",
        "subclass",
        "Quality",
        "Flags",
        "bonding",
        "duration",
        "stackable",
        "ContainerSlots",
        "BagFamily",
        "BuyPrice",
        "SellPrice",
        "RequiredLevel",
        "RequiredSkill",
        "RequiredSkillRank",
    }
    missing = required - positions.keys()
    if missing:
        raise ValueError(f"item_template is missing fields: {sorted(missing)}")
    result: dict[int, dict] = {}
    for row in rows:
        item_class = int(row[positions["class"]])
        capacity = int(row[positions["ContainerSlots"]])
        if item_class not in CONTAINER_CLASSES or capacity <= 0:
            continue
        item_id = int(row[positions["entry"]])
        quality_id = int(row[positions["Quality"]])
        result[item_id] = {
            "item_id": item_id,
            "name": row[positions["name"]],
            "item_class": item_class,
            "item_subclass": int(row[positions["subclass"]]),
            "quality_id": quality_id,
            "quality": QUALITY_NAMES.get(quality_id, "common"),
            "flags": int(row[positions["Flags"]]),
            "bonding": int(row[positions["bonding"]]),
            "duration": int(row[positions["duration"]]),
            "max_stack": int(row[positions["stackable"]]),
            "capacity": capacity,
            "bag_family": int(row[positions["BagFamily"]]),
            "buy_price_copper": int(row[positions["BuyPrice"]]),
            "sell_price_copper": int(row[positions["SellPrice"]]),
            "required_level": int(row[positions["RequiredLevel"]]),
            "required_skill_id": int(row[positions["RequiredSkill"]]),
            "required_skill_rank": int(row[positions["RequiredSkillRank"]]),
        }
    return result


def vendor_sources(npc_vendor_sql: str, creature_sql: str) -> dict[int, list[dict]]:
    positions, rows = DROP.parse_table(npc_vendor_sql, "npc_vendor")
    creature_positions, creature_rows = DROP.parse_table(
        creature_sql, "creature_template"
    )
    names = {
        int(row[creature_positions["entry"]]): row[creature_positions["name"]]
        for row in creature_rows
    }
    result: dict[int, list[dict]] = defaultdict(list)
    for row in rows:
        item_id = int(row[positions["item"]])
        if item_id <= 0:
            continue
        entry = int(row[positions["entry"]])
        result[item_id].append(
            {
                "entry": entry,
                "name": names.get(entry, f"Vendor {entry}"),
                "max_count": int(row[positions["maxcount"]]),
                "restock_seconds": int(row[positions["incrtime"]]),
                "extended_cost": int(row[positions["ExtendedCost"]]),
            }
        )
    return result


def quest_reward_sources(sql: str) -> dict[int, list[dict]]:
    positions, rows = DROP.parse_table(sql, "quest_template")
    result: dict[int, list[dict]] = defaultdict(list)
    reward_columns = [
        *(f"RewardItem{index}" for index in range(1, 5)),
        *(f"RewardChoiceItemID{index}" for index in range(1, 7)),
    ]
    for row in rows:
        quest_id = int(row[positions["ID"]])
        title = row[positions["LogTitle"]]
        for column in reward_columns:
            item_id = int(row[positions[column]])
            if item_id <= 0:
                continue
            if column.startswith("RewardChoice"):
                amount_column = column.replace("ItemID", "ItemQuantity")
                choice = True
            else:
                amount_column = column.replace("Item", "Amount")
                choice = False
            result[item_id].append(
                {
                    "quest_id": quest_id,
                    "title": title,
                    "choice_reward": choice,
                    "amount": int(row[positions[amount_column]]),
                }
            )
    return result


def invalid_name(name: str) -> bool:
    folded = name.casefold()
    return "deprecated" in folded or "test" in folded


def technically_auctionable(item: dict) -> bool:
    return (
        int(item["bonding"]) in ALLOWED_BONDING
        and int(item["duration"]) == 0
        and not int(item["flags"]) & CONJURED_FLAG
    )


def guide_memberships(
    config: dict, *, sections: bool, allow_multiple: bool = False
) -> dict[str, str]:
    memberships: dict[str, str] = {}
    for filename, guide in config.get("guides", {}).items():
        keys: list[str] = []
        if sections:
            for section in guide.get("sections", []):
                keys.extend(section.get("items", []))
        else:
            keys.extend(guide.get("items", []))
            for section in guide.get("restricted_sections", []):
                keys.extend(section.get("items", []))
        for key in keys:
            if key in memberships and not allow_multiple:
                raise ValueError(f"Canonical key appears in two guide locations: {key}")
            memberships.setdefault(key, filename)
    return memberships


def compact_loot(sources: list[dict]) -> dict:
    evidence: list[str] = []
    for source in sources:
        for label in source.get("evidence", []):
            if label and label not in evidence:
                evidence.append(label)
    cohorts = sorted(
        {
            label
            for label in evidence
            if "Bags " in label and "Level Range" in label
        }
    )
    representative = [
        label
        for label in evidence
        if "World Loot Level" not in label
        and "ReferenceTable" not in label
        and label not in cohorts
    ][:8]
    return {
        "source_rows": len(sources),
        "source_types": sorted({source["source_type"] for source in sources}),
        "world_loot_cohorts": cohorts,
        "representative_evidence": representative,
    }


def compact_vendors(sources: list[dict]) -> dict:
    return {
        "vendor_rows": len(sources),
        "unlimited_vendor_rows": sum(source["max_count"] == 0 for source in sources),
        "limited_stock_values": sorted(
            {source["max_count"] for source in sources if source["max_count"] > 0}
        ),
        "restock_seconds": sorted(
            {source["restock_seconds"] for source in sources if source["restock_seconds"] > 0}
        ),
        "extended_cost_ids": sorted(
            {source["extended_cost"] for source in sources if source["extended_cost"] > 0}
        ),
        "representative_vendors": [source["name"] for source in sources[:8]],
    }


def build() -> dict:
    sql = read_sources()
    items = item_records(sql["item_template.sql"])
    drop_items = DROP.parse_items(sql["item_template.sql"])
    loot = DROP.build_loot_sources(sql, drop_items)
    vendors = vendor_sources(sql["npc_vendor.sql"], sql["creature_template.sql"])
    quest_rewards = quest_reward_sources(sql["quest_template.sql"])

    recipes = load(RECIPE_PATH)["recipes"]
    recipe_by_output: dict[int, list[dict]] = defaultdict(list)
    for key, recipe in recipes.items():
        recipe_by_output[int(recipe["output_item_id"])].append(
            {
                "canonical_key": key,
                "source_spell_id": int(recipe["source_spell_id"]),
                "source_spell_name": recipe["source_spell_name"],
                "minimum_output": int(recipe["output_count"]),
                "maximum_output": int(recipe["output_count_max"]),
            }
        )

    crafted = load(CRAFTED_PATH)
    crafted_locations = guide_memberships(crafted, sections=True)
    crafted_by_id = {
        int(item["item_id"]): {
            "canonical_key": key,
            "guide_file": crafted_locations[key],
        }
        for key, item in crafted["catalog"].items()
        if int(item["item_id"]) in items
    }
    vendor_config = load(VENDOR_PATH)
    vendor_locations = guide_memberships(
        vendor_config, sections=False, allow_multiple=True
    )
    vendor_by_id = {
        int(item["item_id"]): {
            "canonical_key": key,
            "guide_file": vendor_locations.get(key),
        }
        for key, item in vendor_config["catalog"].items()
        if not item.get("cost_only") and int(item["item_id"]) in items
    }

    records: dict[str, dict] = {}
    decisions = Counter()
    primary_sources = Counter()
    for item_id, item in sorted(items.items()):
        auctionable = technically_auctionable(item)
        item_recipes = recipe_by_output.get(item_id, [])
        item_vendors = vendors.get(item_id, [])
        item_loot = loot.get(item_id, [])
        item_quests = quest_rewards.get(item_id, [])
        if not auctionable:
            decision = "excluded-not-auctionable"
            primary_source = None
        elif invalid_name(item["name"]):
            decision = "excluded-invalid-name"
            primary_source = None
        elif item_recipes:
            decision = "included-existing-crafted"
            primary_source = "crafted"
        elif item_vendors:
            decision = "included-vendor"
            primary_source = "vendor"
        elif item_loot:
            decision = "included-drop"
            primary_source = "drop"
        elif item_quests:
            decision = "included-quest-reward"
            primary_source = "quest-reward"
        else:
            decision = "excluded-unverified-acquisition"
            primary_source = None
        decisions[decision] += 1
        if primary_source:
            primary_sources[primary_source] += 1
        records[str(item_id)] = {
            **item,
            "technically_auctionable": auctionable,
            "acquisition_types": [
                source_type
                for source_type, present in (
                    ("crafted", bool(item_recipes)),
                    ("vendor", bool(item_vendors)),
                    ("drop", bool(item_loot)),
                    ("quest-reward", bool(item_quests)),
                )
                if present
            ],
            "primary_source": primary_source,
            "decision": decision,
            "recipe_sources": item_recipes,
            "vendor_sources": compact_vendors(item_vendors) if item_vendors else None,
            "loot_sources": compact_loot(item_loot) if item_loot else None,
            "quest_reward_sources": item_quests,
            "canonical_coverage": (
                crafted_by_id.get(item_id)
                if primary_source == "crafted"
                else vendor_by_id.get(item_id)
                if primary_source == "vendor"
                else None
            ),
        }

    return {
        "version": 1,
        "refreshed": date.today().isoformat(),
        "scope": "Every pinned WotLK item-class Container, Quiver, or Ammo Pouch record with at least one storage slot.",
        "source": {
            "name": "AzerothCore WotLK base world data",
            "repository": "azerothcore/azerothcore-wotlk",
            "commit": SOURCE_COMMIT,
            "files": [f"{SOURCE_ROOT}/{filename}" for filename in SOURCE_FILES],
        },
        "rules": {
            "container_item_classes": sorted(CONTAINER_CLASSES),
            "minimum_container_slots": 1,
            "allowed_bonding": sorted(ALLOWED_BONDING),
            "required_duration": 0,
            "conjured_flag": CONJURED_FLAG,
            "source_priority": ["crafted", "vendor", "drop", "quest-reward"],
            "mixed_source_rule": "A deterministic unlimited vendor route owns pricing when the same item also drops.",
            "unverified_acquisition_rule": "Technically tradeable item-template records with no pinned recipe, vendor, loot, or quest-reward route remain excluded.",
        },
        "summary": {
            "container_records": len(records),
            "technically_auctionable_records": sum(
                record["technically_auctionable"] for record in records.values()
            ),
            "included_obtainable_auctionable_records": sum(
                record["decision"].startswith("included-") for record in records.values()
            ),
            "decisions": dict(sorted(decisions.items())),
            "primary_sources": dict(sorted(primary_sources.items())),
        },
        "items": records,
    }


def validate(audit: dict) -> None:
    if audit.get("version") != 1:
        raise ValueError("Unsupported container-audit version")
    if audit.get("source", {}).get("commit") != SOURCE_COMMIT:
        raise ValueError("Container audit uses the wrong pinned source commit")
    expected_summary = {
        "container_records": 175,
        "technically_auctionable_records": 115,
        "included_obtainable_auctionable_records": 93,
        "decisions": {
            "excluded-invalid-name": 12,
            "excluded-not-auctionable": 60,
            "excluded-unverified-acquisition": 10,
            "included-drop": 21,
            "included-existing-crafted": 52,
            "included-quest-reward": 1,
            "included-vendor": 19,
        },
        "primary_sources": {
            "crafted": 52,
            "drop": 21,
            "quest-reward": 1,
            "vendor": 19,
        },
    }
    if audit.get("summary") != expected_summary:
        raise ValueError(
            f"Pinned container inventory drifted: {audit.get('summary')} != {expected_summary}"
        )

    items = audit.get("items", {})
    for item_id, item in items.items():
        if int(item_id) != int(item["item_id"]):
            raise ValueError(f"Container item ID drifted: {item_id}")
        if item["decision"].startswith("included-"):
            if not item["technically_auctionable"] or not item["primary_source"]:
                raise ValueError(f"Included container lacks eligibility/source: {item['name']}")
            if int(item["max_stack"]) != 1:
                raise ValueError(f"Container unexpectedly stacks: {item['name']}")
        if item["primary_source"] in {"crafted", "vendor"} and not item["canonical_coverage"]:
            raise ValueError(f"Canonical container coverage is missing: {item['name']}")

    darkmoon = items["19291"]
    if darkmoon["decision"] != "included-quest-reward":
        raise ValueError("Darkmoon Storage Box is not classified as a quest reward")
    if darkmoon["quest_reward_sources"] != [
        {
            "quest_id": 7934,
            "title": "50 Tickets - Darkmoon Storage Box",
            "choice_reward": False,
            "amount": 1,
        }
    ]:
        raise ValueError("Darkmoon Storage Box quest source drifted")
    small_brown = items["4496"]
    if small_brown["primary_source"] != "vendor" or set(
        small_brown["acquisition_types"]
    ) != {"vendor", "drop"}:
        raise ValueError("Small Brown Pouch must retain vendor ownership and drop evidence")

    if CONTAINER_PATH.is_file():
        sections = load(CONTAINER_PATH)
        section_ids = {
            int(item["item_id"]) for item in sections.get("catalog", {}).values()
        }
        expected = {
            int(item_id)
            for item_id, item in items.items()
            if item["primary_source"] in {"drop", "quest-reward"}
        }
        if section_ids != expected:
            raise ValueError(
                f"Container section coverage drifted; missing={sorted(expected - section_ids)}, "
                f"extra={sorted(section_ids - expected)}"
            )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--refresh", action="store_true")
    group.add_argument("--check", action="store_true")
    args = parser.parse_args()

    if args.refresh:
        audit = build()
        AUDIT_PATH.write_text(
            json.dumps(audit, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
            newline="\n",
        )
        print(f"Updated {AUDIT_PATH.relative_to(ROOT)}")
    else:
        if not AUDIT_PATH.is_file():
            raise FileNotFoundError("Container audit is missing; run with --refresh")
        audit = load(AUDIT_PATH)

    validate(audit)
    summary = audit["summary"]
    print(
        "Container audit passed: "
        f"{summary['included_obtainable_auctionable_records']} obtainable auctionable "
        f"containers from {summary['container_records']} pinned storage records."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
