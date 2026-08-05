#!/usr/bin/env python3
"""Build and validate the audited BoE dropped-gear catalogs."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import urllib.request
import unicodedata
from collections import defaultdict
from datetime import date
from functools import lru_cache
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "data" / "ah-dropped-gear.json"
AUDIT_PATH = ROOT / "data" / "ah-dropped-gear-audit.json"
BASELINE_PATH = ROOT / "data" / "ah-price-baselines.json"
CRAFTED_PATH = ROOT / "data" / "ah-crafted-sections.json"
VENDOR_PATH = ROOT / "data" / "ah-vendor-sections.json"
SEARCH_INDEX_PATH = ROOT / "assets" / "ah-search-index.js"
ITEM_IDS_PATH = ROOT / "assets" / "ah-item-ids.js"

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
)

NEW_GUIDE_IDS = {"level-80-boe-epics", "sought-after-world-drops"}
TWINK_LEVELS = {19, 29, 39, 49, 59, 69, 70, 79}
QUALITY_NAMES = {3: "rare", 4: "epic"}

INVENTORY_NAMES = {
    1: "Head",
    2: "Neck",
    3: "Shoulders",
    4: "Shirt",
    5: "Chest",
    6: "Waist",
    7: "Legs",
    8: "Feet",
    9: "Wrists",
    10: "Hands",
    11: "Finger",
    12: "Trinket",
    13: "One-Hand",
    14: "Shield",
    15: "Ranged",
    16: "Back",
    17: "Two-Hand",
    20: "Robe",
    21: "Main-Hand",
    22: "Off-Hand",
    23: "Held In Off-Hand",
    25: "Thrown",
    26: "Ranged",
    28: "Relic",
}

ARMOR_NAMES = {
    0: "Accessory",
    1: "Cloth",
    2: "Leather",
    3: "Mail",
    4: "Plate",
    6: "Shield",
}

LEVEL_80_SECTIONS = (
    ("boe80-weapons-one-hand", "Level 80 one-handed weapons"),
    ("boe80-weapons-ranged", "Level 80 ranged weapons and wands"),
    ("boe80-armor-plate", "Level 80 plate armor"),
    ("boe80-armor-mail", "Level 80 mail armor"),
    ("boe80-armor-leather", "Level 80 leather armor"),
    ("boe80-armor-cloth", "Level 80 cloth armor"),
    ("boe80-armor-cloaks", "Level 80 cloaks"),
    ("boe80-accessories-neck", "Level 80 necklaces"),
    ("boe80-accessories-rings", "Level 80 rings"),
    ("boe80-accessories-trinkets", "Level 80 trinkets"),
    ("boe80-accessories-offhands", "Level 80 shields and off-hands"),
)

WORLD_SECTIONS = tuple(
    (f"world-{era}-{kind}", f"{label} {title}")
    for era, label in (
        ("northrend", "Northrend 71–79"),
        ("outland", "Outland"),
        ("classic", "Classic"),
    )
    for kind, title in (
        ("weapons", "weapons"),
        ("armor", "armor"),
        ("accessories", "jewelry and accessories"),
    )
)


def load_generated(path: Path, variable: str) -> dict:
    source = path.read_text(encoding="utf-8")
    match = re.search(rf"window\.{variable}=(\{{.*?\}});\n", source, re.DOTALL)
    if not match:
        raise ValueError(f"Could not parse {variable} from {path.relative_to(ROOT)}")
    return json.loads(match.group(1))


def normalize(value: str) -> str:
    value = "".join(
        character
        for character in unicodedata.normalize("NFKD", value)
        if not unicodedata.combining(character)
    )
    value = value.casefold().replace("’", "").replace("'", "").replace("&", " and ")
    return " ".join(re.sub(r"[^a-z0-9]+", " ", value).split())


def item_slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", normalize(value)).strip("-")


def read_source(filename: str, source_dir: Path | None) -> str:
    if source_dir:
        return (source_dir / filename).read_text(encoding="utf-8", errors="replace")
    request = urllib.request.Request(
        f"{SOURCE_ROOT}/{filename}",
        headers={"User-Agent": "wotlk-server-guides-dropped-gear-audit/1.0"},
    )
    with urllib.request.urlopen(request, timeout=120) as response:
        return response.read().decode("utf-8", errors="replace")


def parse_table(sql: str, table_name: str) -> tuple[dict[str, int], list[list[str]]]:
    try:
        schema = sql.split(f"CREATE TABLE `{table_name}` (", 1)[1].split(
            "  PRIMARY KEY", 1
        )[0]
    except IndexError as error:
        raise ValueError(f"Could not locate the {table_name} schema") from error
    columns = re.findall(r"^  `([^`]+)` ", schema, re.MULTILINE)
    positions = {name: index for index, name in enumerate(columns)}
    rows: list[list[str]] = []
    for line in sql.splitlines():
        if not line.startswith("(") or not (line.endswith("),") or line.endswith(");")):
            continue
        values = next(
            csv.reader(
                [line[1:-2]],
                delimiter=",",
                quotechar="'",
                escapechar="\\",
                doublequote=False,
                strict=True,
            )
        )
        if len(values) != len(columns):
            raise ValueError(
                f"Unexpected {table_name} field count: {len(values)} instead of {len(columns)}"
            )
        rows.append(values)
    return positions, rows


def parse_items(sql: str) -> dict[int, dict]:
    positions, rows = parse_table(sql, "item_template")
    fields = {
        "entry",
        "name",
        "class",
        "subclass",
        "Quality",
        "Flags",
        "bonding",
        "duration",
        "RequiredLevel",
        "ItemLevel",
        "InventoryType",
        "RandomProperty",
        "RandomSuffix",
        "SellPrice",
        "AllowableClass",
        "AllowableRace",
        "RequiredSkill",
        "RequiredSkillRank",
        "armor",
        "dmg_min1",
        "dmg_max1",
        "dmg_type1",
        "delay",
        "block",
        "socketBonus",
        "itemset",
        "HolidayId",
    }
    for index in range(1, 11):
        fields.update({f"stat_type{index}", f"stat_value{index}"})
    for index in range(1, 4):
        fields.update({f"socketColor_{index}", f"socketContent_{index}"})
    for index in range(1, 6):
        fields.update({f"spellid_{index}", f"spelltrigger_{index}"})
    missing = fields - positions.keys()
    if missing:
        raise ValueError(f"item_template is missing fields: {sorted(missing)}")
    records: dict[int, dict] = {}
    for row in rows:
        item_id = int(row[positions["entry"]])
        stats = [
            {
                "type": int(row[positions[f"stat_type{index}"]]),
                "value": int(row[positions[f"stat_value{index}"]]),
            }
            for index in range(1, 11)
            if int(row[positions[f"stat_type{index}"]])
            or int(row[positions[f"stat_value{index}"]])
        ]
        sockets = [
            {
                "color": int(row[positions[f"socketColor_{index}"]]),
                "content": int(row[positions[f"socketContent_{index}"]]),
            }
            for index in range(1, 4)
            if int(row[positions[f"socketColor_{index}"]])
            or int(row[positions[f"socketContent_{index}"]])
        ]
        spells = [
            {
                "id": int(row[positions[f"spellid_{index}"]]),
                "trigger": int(row[positions[f"spelltrigger_{index}"]]),
            }
            for index in range(1, 6)
            if int(row[positions[f"spellid_{index}"]])
        ]
        records[item_id] = {
            "item_id": item_id,
            "name": row[positions["name"]],
            "item_class": int(row[positions["class"]]),
            "item_subclass": int(row[positions["subclass"]]),
            "quality": int(row[positions["Quality"]]),
            "flags": int(row[positions["Flags"]]),
            "bonding": int(row[positions["bonding"]]),
            "duration": int(row[positions["duration"]]),
            "required_level": int(row[positions["RequiredLevel"]]),
            "item_level": int(row[positions["ItemLevel"]]),
            "inventory_type": int(row[positions["InventoryType"]]),
            "random_property": int(row[positions["RandomProperty"]]),
            "random_suffix": int(row[positions["RandomSuffix"]]),
            "sell_price": int(row[positions["SellPrice"]]),
            "allowable_class": int(row[positions["AllowableClass"]]),
            "allowable_race": int(row[positions["AllowableRace"]]),
            "required_skill": int(row[positions["RequiredSkill"]]),
            "required_skill_rank": int(row[positions["RequiredSkillRank"]]),
            "armor": int(row[positions["armor"]]),
            "weapon_damage_min": float(row[positions["dmg_min1"]]),
            "weapon_damage_max": float(row[positions["dmg_max1"]]),
            "weapon_damage_type": int(row[positions["dmg_type1"]]),
            "weapon_delay_ms": int(row[positions["delay"]]),
            "block": int(row[positions["block"]]),
            "stats": stats,
            "sockets": sockets,
            "socket_bonus_spell": int(row[positions["socketBonus"]]),
            "spells": spells,
            "item_set": int(row[positions["itemset"]]),
            "holiday_id": int(row[positions["HolidayId"]]),
        }
    return records


def parse_source_names(
    creature_sql: str, gameobject_sql: str
) -> tuple[dict[int, list[str]], dict[int, list[str]]]:
    positions, rows = parse_table(creature_sql, "creature_template")
    creatures: dict[int, list[str]] = defaultdict(list)
    for row in rows:
        loot_id = int(row[positions["lootid"]])
        if loot_id:
            label = row[positions["name"]]
            if label not in creatures[loot_id]:
                creatures[loot_id].append(label)

    positions, rows = parse_table(gameobject_sql, "gameobject_template")
    gameobjects: dict[int, list[str]] = defaultdict(list)
    for row in rows:
        loot_id = int(row[positions["Data1"]])
        if loot_id:
            label = row[positions["name"]]
            if label not in gameobjects[loot_id]:
                gameobjects[loot_id].append(label)
    return creatures, gameobjects


def build_loot_sources(sql_by_file: dict[str, str], items: dict[int, dict]) -> dict[int, list[dict]]:
    positions, rows = parse_table(
        sql_by_file["reference_loot_template.sql"], "reference_loot_template"
    )
    references: dict[int, list[tuple[int, int, float, int, int, int, str]]] = defaultdict(list)
    for row in rows:
        references[int(row[positions["Entry"]])].append(
            (
                int(row[positions["Item"]]),
                int(row[positions["Reference"]]),
                float(row[positions["Chance"]]),
                int(row[positions["GroupId"]]),
                int(row[positions["MinCount"]]),
                int(row[positions["MaxCount"]]),
                row[positions["Comment"]],
            )
        )

    @lru_cache(maxsize=None)
    def expand_reference(
        entry: int,
    ) -> tuple[tuple[int, tuple[str, ...], float, int, int, int], ...]:
        expanded: list[tuple[int, tuple[str, ...], float, int, int, int]] = []
        for item_id, reference, chance, group_id, min_count, max_count, comment in references.get(entry, []):
            comments = (comment,) if comment and comment != "NULL" else ()
            if item_id:
                expanded.append(
                    (item_id, comments, chance, group_id, min_count, max_count)
                )
            if reference and reference != entry:
                for (
                    nested_id,
                    nested_comments,
                    nested_chance,
                    nested_group_id,
                    nested_min_count,
                    nested_max_count,
                ) in expand_reference(reference):
                    expanded.append(
                        (
                            nested_id,
                            comments + nested_comments,
                            nested_chance,
                            nested_group_id,
                            nested_min_count,
                            nested_max_count,
                        )
                    )
        return tuple(expanded)

    creatures, gameobjects = parse_source_names(
        sql_by_file["creature_template.sql"],
        sql_by_file["gameobject_template.sql"],
    )
    sources: dict[int, list[dict]] = defaultdict(list)
    table_configs = (
        ("creature_loot_template.sql", "creature_loot_template", "creature", creatures),
        ("gameobject_loot_template.sql", "gameobject_loot_template", "gameobject", gameobjects),
        ("item_loot_template.sql", "item_loot_template", "container", None),
    )
    for filename, table_name, source_type, labels in table_configs:
        positions, rows = parse_table(sql_by_file[filename], table_name)
        for row in rows:
            entry = int(row[positions["Entry"]])
            direct_item = int(row[positions["Item"]])
            reference = int(row[positions["Reference"]])
            chance = float(row[positions["Chance"]])
            group_id = int(row[positions["GroupId"]])
            min_count = int(row[positions["MinCount"]])
            max_count = int(row[positions["MaxCount"]])
            comment = row[positions["Comment"]]
            if labels is None:
                entry_labels = [items.get(entry, {}).get("name", f"Item container {entry}")]
            else:
                entry_labels = labels.get(entry, [])[:5]
            evidence = [label for label in entry_labels if label]
            if comment and comment != "NULL":
                evidence.append(comment)
            if direct_item:
                sources[direct_item].append(
                    {
                        "source_type": source_type,
                        "entry": entry,
                        "chance": chance,
                        "group_id": group_id,
                        "min_count": min_count,
                        "max_count": max_count,
                        "evidence": evidence,
                    }
                )
            if reference:
                for (
                    item_id,
                    reference_comments,
                    item_chance,
                    item_group_id,
                    item_min_count,
                    item_max_count,
                ) in expand_reference(reference):
                    sources[item_id].append(
                        {
                            "source_type": source_type,
                            "entry": entry,
                            "reference": reference,
                            "chance": chance,
                            "group_id": group_id,
                            "min_count": min_count,
                            "max_count": max_count,
                            "reference_item_chance": item_chance,
                            "reference_item_group_id": item_group_id,
                            "reference_item_min_count": item_min_count,
                            "reference_item_max_count": item_max_count,
                            "evidence": evidence + list(reference_comments),
                        }
                    )
    return sources


def existing_guide_item_ids() -> set[int]:
    index = load_generated(SEARCH_INDEX_PATH, "AH_SEARCH_INDEX")
    item_ids = load_generated(ITEM_IDS_PATH, "AH_ITEM_IDS")
    existing: set[int] = set()
    for item in index.get("items", []):
        if item.get("guideId") in NEW_GUIDE_IDS:
            continue
        item_id = item_ids.get(normalize(str(item.get("name", ""))))
        if item_id:
            existing.add(int(item_id))
    return existing


def base_eligibility(record: dict) -> bool:
    return (
        record["item_class"] in {2, 4}
        and record["bonding"] == 2
        and record["duration"] == 0
        and not record["flags"] & 2
        and record["inventory_type"] != 0
    )


def excluded_name(name: str) -> bool:
    folded = name.casefold()
    return (
        folded.startswith("darkmoon card:")
        or "deprecated" in folded
        or "test " in folded
        or folded.startswith("test")
        or "[ph]" in folded
        or "(ph)" in folded
        or folded.startswith("90 epic")
    )


def source_text(sources: list[dict]) -> str:
    return " | ".join(
        str(value)
        for source in sources
        for value in source.get("evidence", [])
    ).casefold()


def source_label(record: dict, sources: list[dict], guide_id: str) -> str:
    evidence = source_text(sources)
    if "sack of frosty treasures" in evidence:
        return "Sack of Frosty Treasures"
    if "keg-shaped treasure chest" in evidence:
        return "Brewfest treasure chest"
    if "tiny titanium lockbox" in evidence:
        return "Tiny Titanium Lockbox"
    if "reinforced junkbox" in evidence:
        return "Reinforced Junkbox"
    if "strong junkbox" in evidence:
        return "Strong Junkbox"
    if "bag of fishing treasures" in evidence:
        return "Fishing treasure bag"
    if "shadowfang keep boes" in evidence:
        return "Shadowfang Keep trash"
    if "uldaman boes" in evidence:
        return "Uldaman trash"
    if "molten" in evidence and record["required_level"] == 60:
        return "Molten Core trash"
    if "doomwalker" in evidence or "doom lord kazzak" in evidence:
        return "Outland world boss"
    if "terokk" in evidence:
        return "Terokk"
    if guide_id == "level-80-boe-epics":
        item_level = record["item_level"]
        if item_level >= 264:
            return "Icecrown Citadel"
        if item_level >= 245:
            return "Trial of the Crusader"
        if item_level >= 219:
            return "Ulduar"
        if "sartharion" in evidence or "alexstrasza's gift" in evidence:
            return "Obsidian Sanctum"
        if item_level >= 213 or "gluth" in evidence or "naxxramas" in evidence:
            return "Naxxramas"
        return "Northrend world or container drop"
    required_level = record["required_level"]
    if required_level >= 71:
        return "Northrend world drop"
    if required_level >= 61:
        return "Outland world drop"
    return "Classic world drop"


def section_for(record: dict, guide_id: str) -> str:
    item_class = record["item_class"]
    inventory = record["inventory_type"]
    subclass = record["item_subclass"]
    if guide_id == "level-80-boe-epics":
        if item_class == 2:
            if inventory in {17}:
                return "boe80-weapons-two-hand"
            if inventory in {15, 25, 26} or subclass in {2, 3, 16, 18, 19}:
                return "boe80-weapons-ranged"
            return "boe80-weapons-one-hand"
        if inventory == 16:
            return "boe80-armor-cloaks"
        if inventory == 2:
            return "boe80-accessories-neck"
        if inventory == 11:
            return "boe80-accessories-rings"
        if inventory == 12:
            return "boe80-accessories-trinkets"
        if inventory in {14, 23} or subclass in {0, 6}:
            return "boe80-accessories-offhands"
        return {
            1: "boe80-armor-cloth",
            2: "boe80-armor-leather",
            3: "boe80-armor-mail",
            4: "boe80-armor-plate",
        }.get(subclass, "boe80-accessories-offhands")

    required_level = record["required_level"]
    era = "classic" if required_level <= 60 else "outland" if required_level <= 70 else "northrend"
    if item_class == 2:
        kind = "weapons"
    elif inventory in {2, 11, 12, 14, 23} or subclass in {0, 6}:
        kind = "accessories"
    else:
        kind = "armor"
    return f"world-{era}-{kind}"


def item_slot(record: dict) -> str:
    inventory = record["inventory_type"]
    slot = INVENTORY_NAMES.get(inventory, f"Inventory {inventory}")
    if record["item_class"] == 4 and record["item_subclass"] in ARMOR_NAMES:
        armor = ARMOR_NAMES[record["item_subclass"]]
        if armor not in {"Accessory", "Shield"} and inventory != 16:
            return f"{armor} {slot.casefold()}"
    return slot


def buyer_label(record: dict, guide_id: str) -> str:
    slot = item_slot(record)
    if guide_id == "level-80-boe-epics":
        return f"Level-80 {slot_sales_phrase(slot)} buyers"
    if record["quality"] == 3:
        if record["required_level"] >= 71:
            return "Northrend leveling and pre-80 gearing"
        return f"Level {record['required_level']} bracket players and collectors"
    if record["required_level"] >= 70:
        return "Legacy endgame gearing and collectors"
    return "Legacy leveling and collectors"


def demand_label(record: dict, guide_id: str) -> str:
    if guide_id == "level-80-boe-epics":
        if record["item_level"] >= 264:
            return "Very High"
        if record["item_level"] >= 226:
            return "High"
        if record["item_level"] >= 213:
            return "Med-High"
        return "Medium"
    if record["quality"] == 3 and record["required_level"] in {19, 29, 39}:
        return "Med-High"
    if record["quality"] == 4:
        return "Medium"
    return "Low-Med"


def slot_sales_phrase(slot: str) -> str:
    exact = {
        "One-Hand": "one-handed weapon",
        "Two-Hand": "two-handed weapon",
        "Main-Hand": "main-hand weapon",
        "Off-Hand": "off-hand weapon",
        "Held In Off-Hand": "caster off-hand",
        "Ranged": "ranged weapon",
        "Thrown": "thrown weapon",
        "Shield": "shield",
        "Finger": "ring",
        "Neck": "necklace",
        "Trinket": "trinket",
        "Back": "cloak",
    }
    if slot in exact:
        return exact[slot]
    armor, _, position = slot.partition(" ")
    armor_positions = {
        "head": "headpiece",
        "shoulders": "shoulder armor",
        "chest": "chestpiece",
        "robe": "robe",
        "waist": "belt",
        "legs": "leg armor",
        "feet": "boots",
        "wrists": "bracers",
        "hands": "gloves",
    }
    if position in armor_positions:
        return f"{armor.casefold()} {armor_positions[position]}"
    return slot.casefold()


def buyer_guidance(record: dict, guide_id: str, slot: str) -> str:
    phrase = slot_sales_phrase(slot)
    if guide_id == "level-80-boe-epics":
        item_level = record["item_level"]
        if item_level >= 264:
            tier = "ICC-era iLvl 264"
        elif item_level >= 245:
            tier = "Trial-era iLvl 245"
        elif item_level >= 226:
            tier = "iLvl 226"
        elif item_level >= 219:
            tier = "iLvl 219"
        elif item_level >= 213:
            tier = "Naxx-era iLvl 213"
        else:
            tier = f"Early level-80 iLvl {item_level}"
        return (
            f"{tier} {phrase} for level-80 gearing; the immediate tradeable upgrade "
            "and item level are the main reasons to pay a premium."
        )

    required_level = record["required_level"]
    if record["quality"] == 3 and required_level >= 71:
        return (
            f"Fixed-stat level {required_level} {phrase} for Northrend leveling and "
            "pre-80 gearing; sell on immediate upgrade value, not collector scarcity alone."
        )
    if record["quality"] == 3:
        return (
            f"Fixed-stat level {required_level} {phrase} for bracket players; exact-level "
            "upgrades have a narrow but motivated buyer pool."
        )
    if required_level >= 70:
        return (
            f"Required-level {required_level} epic {phrase} for legacy endgame gearing and "
            "collectors; expect selective demand rather than a routine leveling sale."
        )
    return (
        f"Required-level {required_level} epic {phrase} for legacy leveling sets and "
        "collectors; epic quality draws attention, but the sale may take time."
    )


def source_guidance(source: str) -> str:
    if source == "Brewfest treasure chest":
        return (
            "Brewfest treasure chest supply is seasonal; outside the event, hold for a "
            "patient buyer instead of racing a lone listing."
        )
    if source == "Sack of Frosty Treasures":
        return (
            "Sack of Frosty Treasures supply is episodic; list one at a time and wait "
            "through temporary clusters of competing auctions."
        )
    if source in {
        "Reinforced Junkbox",
        "Strong Junkbox",
        "Tiny Titanium Lockbox",
        "Fishing treasure bag",
    }:
        return (
            f"{source} supply follows farming and opening volume; post singly and do not "
            "treat a temporarily empty AH as proof of the high band."
        )
    if source in {"Shadowfang Keep trash", "Uldaman trash", "Molten Core trash"}:
        return (
            f"{source} farming can create short supply bursts; list one and wait rather "
            "than chasing every undercut."
        )
    if source in {
        "Icecrown Citadel",
        "Trial of the Crusader",
        "Ulduar",
        "Obsidian Sanctum",
        "Naxxramas",
    }:
        return (
            f"{source} BoE supply can arrive in raid-farm bursts; list singly and avoid "
            "repricing from one competing auction."
        )
    if source == "Outland world boss":
        return (
            "Outland world-boss supply is gated and sporadic; allow a longer sale window "
            "and compare completed sales when available."
        )
    if source == "Terokk":
        return (
            "Terokk farming controls supply; use a patient one-at-a-time listing and do "
            "not infer value from an empty AH."
        )
    if "world drop" in source.casefold():
        return (
            f"{source} supply is unpredictable; list one at a time and do not treat an "
            "empty AH as proof of the high band."
        )
    return (
        f"{source} supply is irregular; post singly, allow a longer sale window, and "
        "validate the starter estimate against completed sales when available."
    )


def selling_note(record: dict, guide_id: str, slot: str, source: str) -> str:
    if record["item_id"] == 37752:
        return (
            f"{buyer_guidance(record, guide_id, slot)} Two same-price completed sales "
            "support the current low-confidence band, but they came from one buyer on "
            "one day; Outland world-drop supply is unpredictable, so post singly and "
            "keep recording sales."
        )
    if record["item_id"] == 44313:
        return (
            f"{buyer_guidance(record, guide_id, slot)} One completed sale supports the "
            "current low-confidence band, but Northrend world-drop supply is irregular; "
            "post singly and keep recording completed sales before treating the band as "
            "stable."
        )
    return f"{buyer_guidance(record, guide_id, slot)} {source_guidance(source)}"


def fallback_band(record: dict, guide_id: str) -> tuple[int, int, int]:
    if guide_id == "level-80-boe-epics":
        tiers = (
            (264, (15_000_000, 25_000_000, 50_000_000)),
            (245, (9_000_000, 15_000_000, 30_000_000)),
            (226, (6_000_000, 10_000_000, 20_000_000)),
            (219, (4_500_000, 7_500_000, 15_000_000)),
            (213, (3_000_000, 5_000_000, 10_000_000)),
            (206, (2_400_000, 4_000_000, 8_000_000)),
            (0, (1_800_000, 3_000_000, 6_000_000)),
        )
        for minimum, band in tiers:
            if record["item_level"] >= minimum:
                return band
    if record["quality"] in {4, "epic"}:
        if record["required_level"] >= 71:
            return (3_000_000, 5_000_000, 10_000_000)
        if record["required_level"] >= 70:
            return (2_000_000, 3_500_000, 7_000_000)
        if record["required_level"] >= 60:
            return (1_500_000, 2_500_000, 5_000_000)
        if record["required_level"] >= 40:
            return (1_000_000, 2_000_000, 4_000_000)
        return (1_500_000, 3_000_000, 6_000_000)
    rare_bands = {
        19: (1_000_000, 2_000_000, 5_000_000),
        29: (900_000, 1_800_000, 4_000_000),
        39: (1_000_000, 2_000_000, 4_500_000),
        49: (800_000, 1_500_000, 3_000_000),
        59: (750_000, 1_400_000, 2_800_000),
        69: (1_000_000, 2_000_000, 4_000_000),
        70: (1_000_000, 2_000_000, 4_000_000),
        79: (1_500_000, 3_000_000, 6_000_000),
    }
    if 71 <= record["required_level"] <= 73:
        return (1_200_000, 2_400_000, 4_800_000)
    if 74 <= record["required_level"] <= 76:
        return (1_600_000, 3_000_000, 6_000_000)
    if 77 <= record["required_level"] <= 79:
        return (2_000_000, 4_000_000, 8_000_000)
    return rare_bands[record["required_level"]]


def catalog_item(record: dict, guide_id: str, sources: list[dict]) -> dict:
    slot = item_slot(record)
    source = source_label(record, sources, guide_id)
    return {
        "item_id": record["item_id"],
        "name": record["name"],
        "guide_id": guide_id,
        "section_id": section_for(record, guide_id),
        "quality": QUALITY_NAMES[record["quality"]],
        "required_level": record["required_level"],
        "item_level": record["item_level"],
        "slot": slot,
        "source": source,
        "buyer": buyer_label(record, guide_id),
        "demand": demand_label(record, guide_id),
        "notes": selling_note(record, guide_id, slot, source),
    }


def candidate_reason(
    record: dict,
    guide_id: str,
    loot_sources: dict[int, list[dict]],
    crafted_ids: set[int],
    vendor_ids: set[int],
    other_guide_ids: set[int],
) -> list[str]:
    reasons: list[str] = []
    item_id = record["item_id"]
    if item_id in crafted_ids:
        reasons.append("crafted-output")
    if item_id in vendor_ids:
        reasons.append("vendor-catalog")
    if item_id in other_guide_ids:
        reasons.append("existing-guide-coverage")
    if item_id not in loot_sources:
        reasons.append("no-audited-loot-source")
    if excluded_name(record["name"]):
        reasons.append("excluded-name-or-non-drop-reward")
    if guide_id == "sought-after-world-drops":
        if record["random_property"] or record["random_suffix"]:
            reasons.append("random-affix")
        if (
            record["quality"] == 3
            and record["required_level"] not in TWINK_LEVELS
            and not 71 <= record["required_level"] <= 79
        ):
            reasons.append("outside-curated-bracket-scope")
    return reasons


def build(source_dir: Path | None) -> tuple[dict, dict]:
    sql_by_file = {filename: read_source(filename, source_dir) for filename in SOURCE_FILES}
    items = parse_items(sql_by_file["item_template.sql"])
    loot_sources = build_loot_sources(sql_by_file, items)
    crafted = json.loads(CRAFTED_PATH.read_text(encoding="utf-8"))
    vendor = json.loads(VENDOR_PATH.read_text(encoding="utf-8"))
    crafted_ids = {int(item["item_id"]) for item in crafted["catalog"].values()}
    vendor_ids = {int(item["item_id"]) for item in vendor["catalog"].values()}
    other_guide_ids = existing_guide_item_ids()

    included: dict[int, tuple[str, dict]] = {}
    excluded: dict[str, dict] = {}
    candidate_counts = {"level_80_raw": 0, "world_raw": 0}
    for record in items.values():
        if not base_eligibility(record):
            continue
        guide_id = ""
        if record["quality"] == 4 and record["required_level"] == 80:
            guide_id = "level-80-boe-epics"
            candidate_counts["level_80_raw"] += 1
        elif (
            record["quality"] in {3, 4}
            and 1 <= record["required_level"] < 80
        ):
            guide_id = "sought-after-world-drops"
            candidate_counts["world_raw"] += 1
        if not guide_id:
            continue
        reasons = candidate_reason(
            record,
            guide_id,
            loot_sources,
            crafted_ids,
            vendor_ids,
            other_guide_ids,
        )
        if reasons:
            excluded[str(record["item_id"])] = {
                "name": record["name"],
                "candidate_guide": guide_id,
                "reasons": reasons,
            }
            continue
        included[record["item_id"]] = (guide_id, record)

    catalog: dict[str, dict] = {}
    audit_items: dict[str, dict] = {}
    seen_slugs: set[str] = set()
    for item_id, (guide_id, record) in sorted(included.items()):
        slug = item_slug(record["name"])
        if slug in seen_slugs:
            slug = f"{slug}-{item_id}"
        seen_slugs.add(slug)
        sources = loot_sources[item_id]
        source_chances = [
            float(source["chance"])
            for source in sources
            if float(source.get("chance", 0)) > 0
        ]
        reference_item_chances = [
            float(source["reference_item_chance"])
            for source in sources
            if float(source.get("reference_item_chance", 0)) > 0
        ]
        catalog[slug] = catalog_item(record, guide_id, sources)
        audit_items[str(item_id)] = {
            **record,
            "guide_id": guide_id,
            "section_id": section_for(record, guide_id),
            "source_types": sorted({source["source_type"] for source in sources}),
            "source_label": source_label(record, sources, guide_id),
            "loot_profile": {
                "source_rows": len(sources),
                "distinct_source_entries": len(
                    {(source["source_type"], source["entry"]) for source in sources}
                ),
                "direct_rows": sum("reference" not in source for source in sources),
                "reference_rows": sum("reference" in source for source in sources),
                "source_chance_min": min(source_chances) if source_chances else None,
                "source_chance_max": max(source_chances) if source_chances else None,
                "reference_item_chance_min": (
                    min(reference_item_chances) if reference_item_chances else None
                ),
                "reference_item_chance_max": (
                    max(reference_item_chances) if reference_item_chances else None
                ),
            },
            "source_evidence": sorted(
                {
                    str(value)
                    for source in sources
                    for value in source.get("evidence", [])
                    if value
                }
            )[:20],
        }

    fingerprint_lines = [
        f"{item['item_id']}|{item['guide_id']}|{item['section_id']}|{item['source']}"
        for item in catalog.values()
    ]
    fingerprint = hashlib.sha256("\n".join(sorted(fingerprint_lines)).encode("utf-8")).hexdigest()
    guide_counts = {
        guide_id: sum(item["guide_id"] == guide_id for item in catalog.values())
        for guide_id in sorted(NEW_GUIDE_IDS)
    }
    data = {
        "version": 1,
        "audit_commit": SOURCE_COMMIT,
        "scope": (
            "Drop-sourced level-80 epic BoEs plus pre-80 epic BoEs and fixed-stat rare "
            "BoEs at recognized bracket caps. Prices use completed-sale evidence where "
            "available and otherwise use reviewed Hellscream low-pop starter estimates."
        ),
        "guides": {
            "level-80-boe-epics": {
                "file": "level-80-boe-epics-ah-price-guide.html",
                "sections": [
                    {"id": section_id, "title": title}
                    for section_id, title in LEVEL_80_SECTIONS
                ],
            },
            "sought-after-world-drops": {
                "file": "sought-after-world-drops-ah-price-guide.html",
                "sections": [
                    {"id": section_id, "title": title}
                    for section_id, title in WORLD_SECTIONS
                ],
            },
        },
        "catalog": catalog,
    }
    audit = {
        "version": 1,
        "refreshed": date.today().isoformat(),
        "source": {
            "name": "AzerothCore WotLK base world database",
            "commit": SOURCE_COMMIT,
            "files": [f"{SOURCE_ROOT}/{filename}" for filename in SOURCE_FILES],
        },
        "rules": {
            "level_80": "quality=4, bonding=2, RequiredLevel=80, equipment class, audited loot source",
            "world": (
                "bonding=2, RequiredLevel<80, fixed stats, quality=4; quality=3 at "
                "levels 19/29/39/49/59/69/70 or throughout Northrend 71–79; audited loot source"
            ),
            "active_listings_used_for_prices": False,
        },
        "candidate_counts": candidate_counts,
        "included_counts": guide_counts,
        "fingerprint": fingerprint,
        "items": audit_items,
        "excluded": excluded,
    }
    return data, audit


def seed_baselines(data: dict) -> dict:
    baseline = json.loads(BASELINE_PATH.read_text(encoding="utf-8"))
    items = dict(baseline["items"])
    for catalog_item_record in data["catalog"].values():
        item_id = str(catalog_item_record["item_id"])
        if item_id in items:
            if items[item_id]["name"] != catalog_item_record["name"]:
                raise ValueError(f"{item_id}: baseline name does not match dropped-gear catalog")
            continue
        quick, target, high = fallback_band(
            catalog_item_record,
            catalog_item_record["guide_id"],
        )
        items[item_id] = {
            "name": catalog_item_record["name"],
            "quick": quick,
            "target": target,
            "high": high,
            "source_type": "documented-fallback",
            "confidence": "fallback",
            "reason": (
                "Provisional dropped-gear band derived from the audited item-quality, item-level, "
                "level-bracket, and buyer-use tier. No active listing was used; replace with "
                "qualifying realized sales or measured acquisition evidence."
            ),
        }
    baseline["items"] = {
        item_id: items[item_id]
        for item_id in sorted(items, key=lambda value: int(value))
    }
    return baseline


def validate(data: dict, audit: dict, baseline: dict) -> None:
    if data.get("version") != 1 or audit.get("version") != 1:
        raise ValueError("Unsupported dropped-gear data version")
    if data.get("audit_commit") != SOURCE_COMMIT:
        raise ValueError("Dropped-gear catalog uses the wrong source commit")
    if audit.get("source", {}).get("commit") != SOURCE_COMMIT:
        raise ValueError("Dropped-gear audit uses the wrong source commit")
    catalog = data.get("catalog", {})
    audit_items = audit.get("items", {})
    catalog_ids = {str(item["item_id"]) for item in catalog.values()}
    if catalog_ids != set(audit_items):
        raise ValueError("Dropped-gear catalog and audit item sets differ")
    if len(catalog_ids) != len(catalog):
        raise ValueError("Dropped-gear catalog contains duplicate item IDs")
    guide_counts = {
        guide_id: sum(item["guide_id"] == guide_id for item in catalog.values())
        for guide_id in sorted(NEW_GUIDE_IDS)
    }
    if guide_counts != audit.get("included_counts"):
        raise ValueError(f"Dropped-gear guide counts are stale: {guide_counts}")
    fingerprint_lines: list[str] = []
    distinct_notes: set[str] = set()
    for item in catalog.values():
        item_id = str(item["item_id"])
        record = audit_items[item_id]
        if record["bonding"] != 2 or record["item_class"] not in {2, 4}:
            raise ValueError(f"{item['name']}: non-BoE equipment leaked into dropped gear")
        if item["guide_id"] == "level-80-boe-epics":
            if record["quality"] != 4 or record["required_level"] != 80:
                raise ValueError(f"{item['name']}: level-80 epic rule failed")
        else:
            if not 1 <= record["required_level"] < 80:
                raise ValueError(f"{item['name']}: world-drop level rule failed")
            if (
                record["quality"] == 3
                and record["required_level"] not in TWINK_LEVELS
                and not 71 <= record["required_level"] <= 79
            ):
                raise ValueError(f"{item['name']}: rare world drop is outside bracket scope")
            if record["random_property"] or record["random_suffix"]:
                raise ValueError(f"{item['name']}: random-affix world drop leaked into the catalog")
        if not record.get("source_types"):
            raise ValueError(f"{item['name']}: audited loot source is missing")
        note = str(item.get("notes", ""))
        if not 180 <= len(note) <= 340:
            raise ValueError(f"{item['name']}: selling note is missing or poorly sized")
        if "Provisional fallback band. Post one at a time" in note:
            raise ValueError(f"{item['name']}: generic placeholder selling note returned")
        if "supply" not in note.casefold():
            raise ValueError(f"{item['name']}: selling note lacks source-supply guidance")
        if item["guide_id"] == "level-80-boe-epics":
            if f"iLvl {record['item_level']}" not in note or "level-80 gearing" not in note:
                raise ValueError(f"{item['name']}: level-80 note lacks item-level buyer guidance")
        elif record["quality"] == 3:
            if f"Fixed-stat level {record['required_level']}" not in note:
                raise ValueError(f"{item['name']}: rare note lacks fixed-stat level guidance")
        elif f"Required-level {record['required_level']} epic" not in note:
            raise ValueError(f"{item['name']}: epic note lacks required-level guidance")
        distinct_notes.add(note)
        price = baseline["items"].get(item_id)
        if not price:
            raise ValueError(f"{item['name']}: price baseline is missing")
        if price["source_type"] == "documented-fallback":
            if price["confidence"] != "fallback":
                raise ValueError(f"{item['name']}: fallback confidence changed")
        elif price["source_type"] == "realized-sales-history":
            if price["confidence"] not in {"low", "medium"}:
                raise ValueError(f"{item['name']}: realized-sale confidence is invalid")
        else:
            raise ValueError(f"{item['name']}: unsupported dropped-gear provenance")
        if not int(price["quick"]) <= int(price["target"]) <= int(price["high"]):
            raise ValueError(f"{item['name']}: invalid price-band order")
        fingerprint_lines.append(
            f"{item['item_id']}|{item['guide_id']}|{item['section_id']}|{item['source']}"
        )
    fingerprint = hashlib.sha256(
        "\n".join(sorted(fingerprint_lines)).encode("utf-8")
    ).hexdigest()
    if fingerprint != audit.get("fingerprint"):
        raise ValueError("Dropped-gear audited item fingerprint changed")
    if len(distinct_notes) < 250:
        raise ValueError("Dropped-gear selling notes are not sufficiently item-specific")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-dir", type=Path, help="Use downloaded AzerothCore SQL files")
    parser.add_argument("--check", action="store_true", help="Validate saved data without network access")
    args = parser.parse_args()

    if args.check:
        data = json.loads(DATA_PATH.read_text(encoding="utf-8"))
        audit = json.loads(AUDIT_PATH.read_text(encoding="utf-8"))
        baseline = json.loads(BASELINE_PATH.read_text(encoding="utf-8"))
    else:
        data, audit = build(args.source_dir)
        baseline = seed_baselines(data)
        DATA_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
        AUDIT_PATH.write_text(json.dumps(audit, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
        BASELINE_PATH.write_text(json.dumps(baseline, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")

    validate(data, audit, baseline)
    counts = audit["included_counts"]
    print(
        "Dropped-gear audit passed: "
        f"{counts['level-80-boe-epics']} level-80 epic BoEs and "
        f"{counts['sought-after-world-drops']} sought-after pre-80 drops."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
