#!/usr/bin/env python3
"""Build and validate the pinned auctionable collectibles inventory."""

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
AUDIT_PATH = ROOT / "data" / "ah-collectible-audit.json"
SEARCH_PATH = ROOT / "assets" / "ah-search-index.js"
DROP_SCRIPT = ROOT / "scripts" / "audit-ah-dropped-gear.py"
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
ALLOWED_BONDING = {0, 2, 3}
CONJURED_FLAG = 0x2
QUALITY_NAMES = {
    0: "poor",
    1: "common",
    2: "uncommon",
    3: "rare",
    4: "epic",
    5: "legendary",
}
BINDING_NAMES = {0: "none", 1: "pickup", 2: "equip", 3: "use", 4: "quest"}


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load {path.name}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


DROP = load_module("ah_collectible_drop_source", DROP_SCRIPT)


ITEM_GROUPS = {
    "vendor-unlimited": (
        8485, 8486, 8487, 8488, 8490, 8495, 8496, 8497, 8500, 8501,
        10360, 10361, 10392, 10393, 10394, 11023, 11026, 29363, 29364,
        29901, 29902, 29903, 29904, 29956, 29957, 29958, 44822, 46398,
        48120,
    ),
    "vendor-limited": (8489, 11027),
    "vendor-token": (
        44965, 44970, 44971, 44973, 44974, 44980, 44982, 44984, 45002,
        45606, 46820, 46821,
    ),
    "companion-drops": (
        8491, 8492, 8494, 8498, 8499, 10822, 20769, 29960, 34535,
        39896, 39898, 39899, 44721, 48112, 48114, 48116, 48118, 48122,
        48124, 48126,
    ),
    "companion-quest-rewards": (10398,),
    "crafted-collectibles": (4401, 11825, 11826, 15996, 21277, 34060, 34061, 41508, 44413, 44554),
    "quest-accessories": (52200, 52201, 52251, 52252, 52253),
    "season-winter-veil": (17194, 17202, 17303, 17304, 17307, 17405, 21213, 21301, 21305, 21308, 21309),
    "season-lunar-festival": (21557, 21558, 21559, 21561, 21562, 21571, 21574, 21576, 21589, 21590, 21592, 21593, 21595, 21713, 21747),
    "season-love-is-in-the-air": (22200, 22218, 22276, 22277, 22278, 22279, 22280, 22281, 22282, 34258, 49856, 49857, 49858, 49859, 49860, 49861, 50163),
    "season-noblegarden": (6833, 6835, 19028),
    "season-midsummer": (34599, 34850),
}

SEASON_LABELS = {
    "season-winter-veil": "Winter Veil",
    "season-lunar-festival": "Lunar Festival",
    "season-love-is-in-the-air": "Love is in the Air",
    "season-noblegarden": "Noblegarden",
    "season-midsummer": "Midsummer Fire Festival",
}
EMPTY_SEASONS = (
    "Children's Week",
    "Brewfest",
    "Hallow's End",
    "Pilgrim's Bounty",
    "Day of the Dead",
    "Pirates' Day",
)

CRAFTED_RECIPES = {
    4401: {"profession": "Engineering", "spell_id": 3928, "spell_name": "Mechanical Squirrel Box", "skill": 75, "reagents": ((4363, 1), (4359, 1), (2840, 1), (774, 2))},
    11825: {"profession": "Engineering", "spell_id": 15628, "spell_name": "Pet Bombling", "skill": 205, "reagents": ((4394, 1), (7077, 1), (7191, 1), (3860, 6))},
    11826: {"profession": "Engineering", "spell_id": 15633, "spell_name": "Lil' Smoky", "skill": 205, "reagents": ((7075, 1), (4389, 2), (7191, 1), (3860, 2), (6037, 1))},
    15996: {"profession": "Engineering", "spell_id": 19793, "spell_name": "Lifelike Mechanical Toad", "skill": 265, "reagents": ((12803, 1), (15994, 4), (10558, 1), (8170, 1))},
    21277: {"profession": "Engineering", "spell_id": 26011, "spell_name": "Tranquil Mechanical Yeti", "skill": 250, "reagents": ((15407, 1), (15994, 4), (7079, 2), (18631, 2), (10558, 1))},
    34060: {"profession": "Engineering", "spell_id": 44155, "spell_name": "Flying Machine", "skill": 300, "reagents": ((23782, 2), (23781, 20), (23783, 20), (11291, 8))},
    34061: {"profession": "Engineering", "spell_id": 44157, "spell_name": "Turbo-Charged Flying Machine", "skill": 375, "reagents": ((23784, 4), (23786, 8), (23787, 8), (34249, 1))},
    41508: {"profession": "Engineering", "spell_id": 60866, "spell_name": "Mechano-hog", "skill": 450, "faction": "Horde", "reagents": ((37663, 12), (39681, 40), (44128, 2), (44499, 1), (44501, 8), (44500, 1))},
    44413: {"profession": "Engineering", "spell_id": 60867, "spell_name": "Mekgineer's Chopper", "skill": 450, "faction": "Alliance", "reagents": ((37663, 12), (39681, 40), (44128, 2), (44499, 1), (44501, 8), (44500, 1))},
    44554: {"profession": "Tailoring", "spell_id": 60969, "spell_name": "Flying Carpet", "skill": 300, "reagents": ((21840, 6), (23112, 4), (22445, 4), (8343, 5))},
}

CURRENCY_COSTS = {
    **{item_id: "40 Champion's Seals" for item_id in ITEM_GROUPS["vendor-token"]},
    34599: "5 Burning Blossoms",
    22200: "5 Love Tokens",
    22218: "2 Love Tokens",
    34258: "5 Love Tokens",
    49856: "1 Love Token",
    49857: "1 Love Token",
    49858: "1 Love Token",
    49859: "1 Love Token",
    49860: "1 Love Token",
    49861: "1 Love Token",
    50163: "5 Love Tokens",
    6833: "25 Noblegarden Chocolates",
    6835: "25 Noblegarden Chocolates",
    19028: "50 Noblegarden Chocolates",
}

EXCLUSIONS = {
    "unverified-hellscream-promotional-companions": {
        "item_ids": [22781],
        "names": ["Polar Bear Collar"],
        "reason": "The only pinned acquisition route is quest 9273, Redeem iCoke Prize Voucher. No direct Hellscream enablement evidence is saved, and the item was absent from all six comparison markets in the 2026-08-10 demand snapshot.",
    },
    "unverified-hellscream-promotional-mounts": {
        "item_ids": [49282, 49283, 49284, 49285, 49286, 49290, 54068, 54069],
        "names": [
            "Big Battle Bear",
            "Reins of the Spectral Tiger",
            "Reins of the Swift Spectral Tiger",
            "X-51 Nether-Rocket",
            "X-51 Nether-Rocket X-TREME",
            "Magic Rooster Egg",
            "Wooly White Rhino",
            "Blazing Hippogryph",
        ],
        "reason": "No direct Hellscream acquisition evidence is saved. A generic base-database loot route is not proof that a promotional or TCG reward is enabled on this server.",
    },
    "auction-ineligible-examples": {
        "item_ids": [37431, 37460, 43352, 43626, 44820, 33182, 33184, 37012, 50250],
        "names": ["Fetch Ball", "Rope Pet Leash", "Pet Grooming Kit", "Happy Pet Snack", "Red Ribbon Pet Leash", "Swift Flying Broom", "Swift Magic Broom", "The Horseman's Reins", "Big Love Rocket"],
        "reason": "Bind on Pickup, duration-limited, or otherwise nontradeable before Auction House listing.",
    },
}


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def read_sources(source_dir: Path | None) -> dict[str, str]:
    if source_dir:
        return {name: (source_dir / name).read_text(encoding="utf-8") for name in SOURCE_FILES}
    result = {}
    for name in SOURCE_FILES:
        request = urllib.request.Request(
            f"{SOURCE_ROOT}/{name}",
            headers={"User-Agent": "wotlk-server-guides-collectible-audit/1.0"},
        )
        with urllib.request.urlopen(request, timeout=120) as response:
            result[name] = response.read().decode("utf-8", errors="replace")
    return result


def item_records(sql: str) -> dict[int, dict]:
    positions, rows = DROP.parse_table(sql, "item_template")
    wanted = {item_id for ids in ITEM_GROUPS.values() for item_id in ids}
    wanted |= {item_id for group in EXCLUSIONS.values() for item_id in group["item_ids"]}
    result = {}
    for row in rows:
        item_id = int(row[positions["entry"]])
        if item_id not in wanted:
            continue
        quality_id = int(row[positions["Quality"]])
        result[item_id] = {
            "item_id": item_id,
            "name": row[positions["name"]],
            "item_class": int(row[positions["class"]]),
            "item_subclass": int(row[positions["subclass"]]),
            "quality_id": quality_id,
            "quality": QUALITY_NAMES.get(quality_id, "common"),
            "bonding": int(row[positions["bonding"]]),
            "binding": BINDING_NAMES.get(int(row[positions["bonding"]]), "unknown"),
            "flags": int(row[positions["Flags"]]),
            "duration": int(row[positions["duration"]]),
            "max_stack": max(1, int(row[positions["stackable"]])),
            "buy_count": max(1, int(row[positions["BuyCount"]])),
            "buy_price_copper": int(row[positions["BuyPrice"]]),
            "vendor_unit_cost_copper": (
                int(row[positions["BuyPrice"]])
                + max(1, int(row[positions["BuyCount"]]))
                - 1
            ) // max(1, int(row[positions["BuyCount"]])),
            "sell_price_copper": int(row[positions["SellPrice"]]),
            "required_skill_id": int(row[positions["RequiredSkill"]]),
            "required_skill_rank": int(row[positions["RequiredSkillRank"]]),
        }
    missing = wanted - result.keys()
    if missing:
        raise ValueError(f"Pinned item_template is missing IDs: {sorted(missing)}")
    return result


def vendor_sources(npc_sql: str, creature_sql: str) -> dict[int, list[dict]]:
    positions, rows = DROP.parse_table(npc_sql, "npc_vendor")
    cpos, crows = DROP.parse_table(creature_sql, "creature_template")
    names = {int(row[cpos["entry"]]): row[cpos["name"]] for row in crows}
    result: dict[int, list[dict]] = defaultdict(list)
    for row in rows:
        item_id = int(row[positions["item"]])
        if item_id <= 0:
            continue
        entry = int(row[positions["entry"]])
        result[item_id].append({
            "entry": entry,
            "name": names.get(entry, f"Vendor {entry}"),
            "max_count": int(row[positions["maxcount"]]),
            "restock_seconds": int(row[positions["incrtime"]]),
            "extended_cost": int(row[positions["ExtendedCost"]]),
        })
    return result


def quest_sources(sql: str) -> dict[int, list[dict]]:
    positions, rows = DROP.parse_table(sql, "quest_template")
    result: dict[int, list[dict]] = defaultdict(list)
    columns = [*(f"RewardItem{i}" for i in range(1, 5)), *(f"RewardChoiceItemID{i}" for i in range(1, 7))]
    for row in rows:
        for column in columns:
            item_id = int(row[positions[column]])
            if item_id <= 0:
                continue
            result[item_id].append({"quest_id": int(row[positions["ID"]]), "title": row[positions["LogTitle"]]})
    return result


def technically_auctionable(item: dict) -> bool:
    return (
        item["bonding"] in ALLOWED_BONDING
        and item["duration"] == 0
        and not item["flags"] & CONJURED_FLAG
    )


def kind_for(item: dict) -> str:
    if item["item_class"] == 15 and item["item_subclass"] == 2:
        return "Companion"
    if item["item_class"] == 15 and item["item_subclass"] == 5:
        return "Mount"
    if item["item_class"] == 4 and item["name"] == "Tabard of the Lightbringer":
        return "Tabard"
    if item["item_class"] == 4:
        return "Cosmetic apparel"
    if "Wrapping Paper" in item["name"]:
        return "Wrapping paper"
    if any(term in item["name"] for term in ("Perfume", "Cologne", "Petals", "Rose", "Candle")):
        return "Vanity accessory"
    if item["item_class"] == 15 and item["item_subclass"] == 4:
        return "Toy / accessory"
    return "Seasonal novelty"


def compact_loot(sources: list[dict]) -> dict | None:
    if not sources:
        return None
    evidence = []
    for source in sources:
        for label in source.get("evidence", []):
            if label not in evidence:
                evidence.append(label)
    return {
        "source_rows": len(sources),
        "source_types": sorted({source["source_type"] for source in sources}),
        "representative_evidence": evidence[:10],
        "chance_range": [min(source["chance"] for source in sources), max(source["chance"] for source in sources)],
    }


def search_occurrences() -> dict[str, list[dict]]:
    if not SEARCH_PATH.exists():
        return {}
    source = SEARCH_PATH.read_text(encoding="utf-8")
    data = json.loads(source[source.find("{"): source.rfind("}") + 1])
    result: dict[str, list[dict]] = defaultdict(list)
    for item in data["items"]:
        if item["guideId"] == "collectibles":
            continue
        result[item["name"].casefold()].append({"guide_id": item["guideId"], "href": item["href"]})
    return result


def build(source_dir: Path | None = None) -> dict:
    sql = read_sources(source_dir)
    items = item_records(sql["item_template.sql"])
    vendors = vendor_sources(sql["npc_vendor.sql"], sql["creature_template.sql"])
    quests = quest_sources(sql["quest_template.sql"])
    loot_items = DROP.parse_items(sql["item_template.sql"])
    loot = DROP.build_loot_sources(sql, loot_items)
    occurrences = search_occurrences()
    records = {}
    decisions = Counter()
    for group, item_ids in ITEM_GROUPS.items():
        for item_id in item_ids:
            item = dict(items[item_id])
            if not technically_auctionable(item):
                raise ValueError(f"Requested collectible is not auctionable: {item_id} {item['name']}")
            item_vendors = vendors.get(item_id, [])
            item_loot = loot.get(item_id, [])
            item_quests = quests.get(item_id, [])
            recipe = CRAFTED_RECIPES.get(item_id)
            if group == "vendor-unlimited" and not any(v["max_count"] == 0 and v["extended_cost"] == 0 for v in item_vendors):
                raise ValueError(f"Unlimited vendor route missing: {item['name']}")
            if group == "vendor-limited" and not any(v["max_count"] > 0 and v["extended_cost"] == 0 for v in item_vendors):
                raise ValueError(f"Limited vendor route missing: {item['name']}")
            if group == "vendor-token" and not any(v["extended_cost"] > 0 for v in item_vendors):
                raise ValueError(f"Token vendor route missing: {item['name']}")
            if group == "companion-drops" and not item_loot:
                raise ValueError(f"Drop route missing: {item['name']}")
            if group == "crafted-collectibles" and not recipe:
                raise ValueError(f"Craft recipe missing: {item['name']}")
            if group in {"companion-quest-rewards", "quest-accessories"} and not item_quests:
                raise ValueError(f"Quest route missing: {item['name']}")
            season = SEASON_LABELS.get(group)
            records[str(item_id)] = {
                **item,
                "group": group,
                "season": season,
                "kind": kind_for(item),
                "auctionable": True,
                "vendor_sources": item_vendors,
                "loot_sources": compact_loot(item_loot),
                "quest_sources": item_quests,
                "crafted_recipe": recipe,
                "currency_cost": CURRENCY_COSTS.get(item_id),
                "existing_guide_occurrences": occurrences.get(item["name"].casefold(), []),
                "canonical_owner": (
                    "data/ah-crafted-sections.json" if recipe
                    else "data/ah-vendor-sections.json" if item_id == 17194
                    else "data/ah-collectible-sections.json"
                ),
            }
            decisions[group] += 1
    return {
        "version": 1,
        "refreshed": date.today().isoformat(),
        "scope": "Verified auctionable WotLK companions, mounts, collectible accessories, and event novelties selected for the Hellscream low-pop AH guide.",
        "source": {
            "name": "AzerothCore WotLK base world data",
            "repository": "azerothcore/azerothcore-wotlk",
            "commit": SOURCE_COMMIT,
            "files": [f"{SOURCE_ROOT}/{name}" for name in SOURCE_FILES],
            "crafted_cross_check": "WotLKDB 3.3.5a item pages, refreshed 2026-08-10",
        },
        "rules": {
            "allowed_bonding": sorted(ALLOWED_BONDING),
            "bond_on_use_rule": "Unused Bind on Use items are tradeable; AzerothCore auction creation checks instance bound state, not future binding type.",
            "required_duration": 0,
            "conjured_flag": CONJURED_FLAG,
            "active_listings_set_prices": False,
            "source_priority": ["crafted", "unlimited coin vendor", "limited coin vendor", "token vendor", "quest/reward", "drop"],
        },
        "summary": {
            "included_items": len(records),
            "groups": dict(sorted(decisions.items())),
            "existing_exact_name_overlaps": sum(bool(item["existing_guide_occurrences"]) for item in records.values()),
            "empty_seasons": len(EMPTY_SEASONS),
        },
        "empty_seasons": list(EMPTY_SEASONS),
        "exclusions": EXCLUSIONS,
        "items": records,
    }


def validate(data: dict) -> None:
    if data.get("version") != 1:
        raise ValueError("Unsupported collectible-audit version")
    if data.get("source", {}).get("commit") != SOURCE_COMMIT:
        raise ValueError("Collectible audit uses the wrong pinned source commit")
    expected = sum(len(ids) for ids in ITEM_GROUPS.values())
    if data.get("summary", {}).get("included_items") != expected or len(data.get("items", {})) != expected:
        raise ValueError(f"Expected {expected} collectible records")
    if set(data.get("empty_seasons", [])) != set(EMPTY_SEASONS):
        raise ValueError("Empty-season coverage drifted")
    seen = set()
    for item_id, item in data["items"].items():
        if int(item_id) != item["item_id"] or item["item_id"] in seen:
            raise ValueError(f"Collectible ID drift or duplicate: {item_id}")
        seen.add(item["item_id"])
        if not item.get("auctionable"):
            raise ValueError(f"Non-auctionable item included: {item['name']}")
        if item["bonding"] not in ALLOWED_BONDING or item["duration"] != 0 or item["flags"] & CONJURED_FLAG:
            raise ValueError(f"Eligibility fields drifted: {item['name']}")
        if item["buy_count"] < 1 or item["vendor_unit_cost_copper"] < 0:
            raise ValueError(f"Vendor unit fields drifted: {item['name']}")
    for required_id in (8489, 11027):
        sources = data["items"][str(required_id)]["vendor_sources"]
        if not any(source["max_count"] > 0 and source["restock_seconds"] > 0 for source in sources):
            raise ValueError("Limited-stock companion lost stock/restock evidence")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--refresh", action="store_true")
    group.add_argument("--check", action="store_true")
    parser.add_argument("--source-dir", type=Path)
    args = parser.parse_args()
    if args.refresh:
        data = build(args.source_dir)
        validate(data)
        AUDIT_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
        print(json.dumps(data["summary"], indent=2))
        return 0
    data = load(AUDIT_PATH)
    validate(data)
    print(f"Collectible audit is valid for {len(data['items'])} included items and {len(data['empty_seasons'])} explicit no-row seasons.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
