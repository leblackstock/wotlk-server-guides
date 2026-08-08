#!/usr/bin/env python3
"""Build and validate the pinned 3.3.5 Turn-in and Recipe Drop audits."""

from __future__ import annotations

import argparse
import importlib.util
import json
import re
import unicodedata
import urllib.request
from collections import Counter
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
GUIDES_DIR = ROOT / "guides"
TURN_IN_OUTPUT = ROOT / "data" / "ah-turn-in-catalog.json"
RECIPE_OUTPUT = ROOT / "data" / "ah-recipe-drop-audit.json"
ITEM_IDS_PATH = ROOT / "assets" / "ah-item-ids.js"
DROP_AUDIT_PATH = ROOT / "scripts" / "audit-ah-dropped-gear.py"
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
    "quest_template_addon.sql",
)
QUALITY_NAMES = {1: "common", 2: "uncommon", 3: "rare", 4: "epic"}
SKILL_NAMES = {
    164: "Blacksmithing",
    165: "Leatherworking",
    171: "Alchemy",
    185: "Cooking",
    197: "Tailoring",
    202: "Engineering",
    333: "Enchanting",
    755: "Jewelcrafting",
    773: "Inscription",
}
PRICE_BANDS = ("quick", "target", "high")
TURN_IN_STACK_OVERRIDES = {
    11382: "1",
    17010: "1 / 2 / 5",
    17011: "1 / 2 / 5",
}


def band(quick: int, target: int, high: int) -> dict[str, int]:
    return {"quick": quick, "target": target, "high": high}


TURN_IN_SECTIONS = (
    {
        "id": "turnin-northrend",
        "title": "Northrend reputation turn-ins",
        "items": ((42780, "Relic of Ulduar"),),
        "seed_band": band(5_000, 10_000, 20_000),
        "cohort": "northrend-reputation",
        "stack": "10 / 50 / 100 / 200",
        "demand": "High",
        "detail": "Sons of Hodir • Storm Peaks drop",
        "restriction": "Requires the Sons of Hodir quest chain; the repeatable turn-in consumes 10.",
    },
    {
        "id": "turnin-aldor-scryer-premium",
        "title": "Aldor / Scryer drops",
        "items": ((29740, "Fel Armament"), (29739, "Arcane Tome")),
        "seed_band": band(50_000, 90_000, 160_000),
        "cohort": "outland-premium-reputation",
        "stack": "1 / 5 / 10",
        "demand": "Very High",
        "detail": "Aldor / Scryer premium reputation item",
        "restriction": "Faction choice is mutually exclusive; each repeatable turn-in consumes 1.",
    },
    {
        "id": "turnin-aldor-scryer-high",
        "title": "Aldor / Scryer drops",
        "items": ((30809, "Mark of Sargeras"), (30810, "Sunfury Signet")),
        "seed_band": band(3_500, 6_500, 12_000),
        "cohort": "outland-high-reputation",
        "stack": "10 / 50 / 100 / 250",
        "demand": "High",
        "detail": "Aldor / Scryer high-tier reputation item",
        "restriction": "Faction choice is mutually exclusive; bulk repeatables consume 10 and single-item quests exist.",
    },
    {
        "id": "turnin-aldor-scryer-low",
        "title": "Aldor / Scryer drops",
        "items": ((29425, "Mark of Kil'jaeden"), (29426, "Firewing Signet")),
        "seed_band": band(1_500, 3_000, 6_000),
        "cohort": "outland-low-reputation",
        "stack": "10 / 50 / 100 / 250",
        "demand": "Med-High",
        "detail": "Aldor / Scryer lower-tier reputation item",
        "restriction": "Faction choice is mutually exclusive and standing-limited; bulk repeatables consume 10.",
    },
    {
        "id": "turnin-cenarion-armaments",
        "title": "Cenarion Expedition / Lower City drops",
        "items": ((24368, "Coilfang Armaments"),),
        "seed_band": band(30_000, 50_000, 90_000),
        "cohort": "outland-premium-reputation",
        "stack": "1 / 5 / 10",
        "demand": "High",
        "detail": "Cenarion Expedition reputation item",
        "restriction": "The repeatable turn-in consumes 1 after the introductory quest.",
    },
    {
        "id": "turnin-cenarion-plants",
        "title": "Cenarion Expedition / Lower City drops",
        "items": ((24401, "Unidentified Plant Parts"),),
        "seed_band": band(3_500, 7_000, 15_000),
        "cohort": "outland-bulk-reputation",
        "stack": "10 / 50 / 100 / 200",
        "demand": "High",
        "detail": "Cenarion Expedition early reputation item",
        "restriction": "The repeatable turn-in consumes 10 and is standing-limited.",
    },
    {
        "id": "turnin-lower-city-feathers",
        "title": "Cenarion Expedition / Lower City drops",
        "items": ((25719, "Arakkoa Feather"),),
        "seed_band": band(2_500, 5_000, 10_000),
        "cohort": "outland-bulk-reputation",
        "stack": "30 / 60 / 120 / 250",
        "demand": "High",
        "detail": "Lower City reputation item",
        "restriction": "The repeatable turn-in consumes 30 and is useful only through Honored.",
    },
    {
        "id": "turnin-sporeggar",
        "title": "Sporeggar / Underbog drops",
        "items": ((24246, "Sanguine Hibiscus"),),
        "seed_band": band(5_000, 10_000, 20_000),
        "cohort": "outland-bulk-reputation",
        "stack": "5 / 20 / 50 / 200",
        "demand": "Med-High",
        "detail": "Sporeggar • Underbog drop and ground spawn",
        "restriction": "At Friendly, the repeatable turn-in consumes 5 for 750 reputation and remains available through Exalted.",
    },
    {
        "id": "turnin-darkmoon-tier1",
        "title": "Darkmoon Faire drop turn-ins only",
        "items": ((5134, "Small Furry Paw"),),
        "seed_band": band(500, 1_000, 2_000),
        "cohort": "darkmoon-animal-parts",
        "stack": "5",
        "demand": "Low",
        "detail": "Darkmoon Faire tier 1 animal part",
        "restriction": "Faire event only; consumes 5 for 1 ticket and is reputation-tier limited.",
    },
    {
        "id": "turnin-darkmoon-tier2",
        "title": "Darkmoon Faire drop turn-ins only",
        "items": ((11407, "Torn Bear Pelt"),),
        "seed_band": band(2_000, 4_000, 8_000),
        "cohort": "darkmoon-animal-parts",
        "stack": "5 / 10",
        "demand": "Low-Med",
        "detail": "Darkmoon Faire tier 2 animal part",
        "restriction": "Faire event only; consumes 5 for 4 tickets and is reputation-tier limited.",
    },
    {
        "id": "turnin-darkmoon-tier3",
        "title": "Darkmoon Faire drop turn-ins only",
        "items": ((4582, "Soft Bushy Tail"),),
        "seed_band": band(3_500, 7_000, 15_000),
        "cohort": "darkmoon-animal-parts",
        "stack": "5",
        "demand": "Med",
        "detail": "Darkmoon Faire tier 3 animal part",
        "restriction": "Faire event only; consumes 5 for 8 tickets and is reputation-tier limited.",
    },
    {
        "id": "turnin-darkmoon-tier4",
        "title": "Darkmoon Faire drop turn-ins only",
        "items": ((5117, "Vibrant Plume"),),
        "seed_band": band(4_500, 8_000, 15_000),
        "cohort": "darkmoon-animal-parts",
        "stack": "5 / 10",
        "demand": "Med-High",
        "detail": "Darkmoon Faire tier 4 animal part",
        "restriction": "Faire event only; consumes 5 for 12 tickets and is reputation-tier limited.",
    },
    {
        "id": "turnin-darkmoon-tier5",
        "title": "Darkmoon Faire drop turn-ins only",
        "items": ((11404, "Evil Bat Eye"), (19933, "Glowing Scorpid Blood")),
        "seed_band": band(7_500, 15_000, 30_000),
        "cohort": "darkmoon-animal-parts",
        "stack": "10",
        "demand": "Med-High",
        "detail": "Darkmoon Faire repeatable animal part",
        "restriction": "Faire event only; consumes 10 for 20 tickets and remains repeatable.",
    },
    {
        "id": "turnin-argent",
        "title": "Argent Dawn / Plaguelands drops",
        "items": (
            (22525, "Crypt Fiend Parts"),
            (22526, "Bone Fragments"),
            (22527, "Core of Elements"),
            (22528, "Dark Iron Scraps"),
            (22529, "Savage Frond"),
        ),
        "seed_band": band(2_500, 6_000, 12_500),
        "cohort": "classic-bulk-reputation",
        "stack": "30 / 60 / 120 / 250",
        "demand": "Med",
        "detail": "Argent Dawn / Light's Hope turn-in",
        "restriction": "The repeatable turn-in consumes 30 after the one-time introduction.",
    },
    {
        "id": "turnin-zg-bijou",
        "title": "Zandalar Tribe / Zul'Gurub drops",
        "items": tuple(
            (item_id, f"{color} Hakkari Bijou")
            for item_id, color in zip(range(19707, 19716), ("Red", "Blue", "Yellow", "Orange", "Green", "Purple", "Bronze", "Silver", "Gold"))
        ),
        "seed_band": band(20_000, 40_000, 80_000),
        "cohort": "zg-bijou",
        "stack": "1 / 5 / 10",
        "demand": "Med-High",
        "detail": "Zandalar Tribe reputation item",
        "restriction": "Destroy 1 at the altar for reputation and a Zandalar Honor Token; no exact color set is required.",
    },
    {
        "id": "turnin-zg-coins",
        "title": "Zandalar Tribe / Zul'Gurub drops",
        "items": (
            (19698, "Zulian Coin"), (19699, "Razzashi Coin"), (19700, "Hakkari Coin"),
            (19701, "Gurubashi Coin"), (19702, "Vilebranch Coin"), (19703, "Witherbark Coin"),
            (19704, "Sandfury Coin"), (19705, "Skullsplitter Coin"), (19706, "Bloodscalp Coin"),
        ),
        "seed_band": band(7_500, 15_000, 30_000),
        "cohort": "zg-coins",
        "stack": "1 / 5 / 10",
        "demand": "Med-High",
        "detail": "Zandalar Tribe three-coin set component",
        "restriction": "Each repeatable quest consumes one coin from its exact three-coin set.",
    },
    {
        "id": "turnin-thorium-cores",
        "title": "Thorium Brotherhood / Blackrock drops",
        "items": ((17010, "Fiery Core"), (17011, "Lava Core"), (11382, "Blood of the Mountain")),
        "seed_band": band(40_000, 80_000, 160_000),
        "cohort": "classic-premium-reputation",
        "stack": "1 / 5 / 10",
        "demand": "Med",
        "detail": "Thorium Brotherhood premium turn-in and crafting material",
        "restriction": "Revered-to-Exalted repeatables consume 1; crafting demand is the primary price comparison.",
    },
    {
        "id": "turnin-thorium-leather",
        "title": "Thorium Brotherhood / Blackrock drops",
        "items": ((17012, "Core Leather"),),
        "seed_band": band(40_000, 80_000, 160_000),
        "cohort": "classic-premium-reputation",
        "stack": "2 / 10 / 20",
        "demand": "Med",
        "detail": "Thorium Brotherhood turn-in and crafting material",
        "restriction": "The repeatable consumes 2; crafting demand is the primary price comparison.",
    },
    {
        "id": "turnin-thorium-scales",
        "title": "Thorium Brotherhood / Blackrock drops",
        "items": ((18944, "Incendosaur Scale"),),
        "seed_band": band(2_500, 6_000, 12_500),
        "cohort": "classic-bulk-reputation",
        "stack": "2 / 10 / 20 / 100",
        "demand": "Med",
        "detail": "Thorium Brotherhood early reputation item",
        "restriction": "Neutral-to-Friendly repeatables consume 2 plus the named companion materials.",
    },
    {
        "id": "turnin-thorium-residue",
        "title": "Thorium Brotherhood / Blackrock drops",
        "items": ((18945, "Dark Iron Residue"),),
        "seed_band": band(2_500, 6_000, 12_500),
        "cohort": "classic-bulk-reputation",
        "stack": "4 / 20 / 100",
        "demand": "Med",
        "detail": "Thorium Brotherhood Friendly-to-Honored item",
        "restriction": "After What the Flux?, turn in 4 for 25 reputation or 100 for 625.",
    },
    {
        "id": "turnin-ungoro-soil",
        "title": "Un'Goro / Morrowgrain odd turn-ins",
        "items": ((11018, "Un'Goro Soil"),),
        "seed_band": band(1_000, 2_000, 4_000),
        "cohort": "classic-quest-convenience",
        "stack": "5 / 20 / 100",
        "demand": "Low-Med",
        "detail": "Un'Goro quest and Morrowgrain input",
        "restriction": "Direct quests consume 5 or 20; Evergreen Pouch use also consumes soil with seeds.",
    },
    {
        "id": "turnin-green-hills-pages",
        "title": "Quest page drops / buyable quest completion items",
        "items": tuple(
            (item_id, f"Green Hills of Stranglethorn - Page {page}")
            for item_id, page in ((2725, 1), (2728, 4), (2730, 6), (2732, 8), (2734, 10), (2735, 11), (2738, 14), (2740, 16), (2742, 18), (2744, 20), (2745, 21), (2748, 24), (2749, 25), (2750, 26), (2751, 27))
        ),
        "seed_band": band(1_000, 3_500, 20_000),
        "cohort": "classic-quest-pages",
        "stack": "1",
        "demand": "Med-High",
        "detail": "Green Hills of Stranglethorn chapter page",
        "restriction": "Each chapter quest consumes one copy of its four pages, except Chapter IV, which consumes three.",
    },
    {
        "id": "turnin-shredder-pages",
        "title": "Quest page drops / buyable quest completion items",
        "items": tuple((16644 + page, f"Shredder Operating Manual - Page {page}") for page in range(1, 13)),
        "seed_band": band(1_000, 2_500, 10_000),
        "cohort": "classic-quest-pages",
        "stack": None,
        "demand": "Med",
        "detail": "Ashenvale Shredder Operating Manual page",
        "restriction": "Use pages 1–4, 5–8, or 9–12 to assemble a chapter; the pages do not stack.",
    },
)

REMOVED_TURN_INS = (
    {
        "item_id": 24407,
        "name": "Uncatalogued Species",
        "reason": "bonding=1 (Bind on Pickup), so it cannot be auctioned",
    },
    {
        "item_id": 21377,
        "name": "Deadwood Headdress Feather",
        "reason": "bonding=1 (Bind on Pickup), so it cannot be auctioned",
    },
    {
        "item_id": 21383,
        "name": "Winterfall Spirit Beads",
        "reason": "bonding=1 (Bind on Pickup), so it cannot be auctioned",
    },
)

RECIPE_SECTION_PROFESSIONS = {
    "Blacksmithing gear-plan drops": "Blacksmithing",
    "Leatherworking gear-pattern drops": "Leatherworking",
    "Tailoring gear-pattern drops": "Tailoring",
    "Enchanting formula drops": "Enchanting",
    "Jewelcrafting BoE world-drop designs": "Jewelcrafting",
    "Engineering schematic drops": "Engineering",
    "Alchemy consumable recipe drops": "Alchemy",
    "Cooking recipe drops": "Cooking",
    "Inscription misc recipe drop": "Inscription",
}
RECIPE_NAME_ALIASES = {
    "formula enchant weapon spell power": "formula enchant weapon spellpower",
    "formula enchant weapon unholy weapon": "formula enchant weapon unholy",
}


def load_drop_audit():
    spec = importlib.util.spec_from_file_location("ah_phase3_drop_base", DROP_AUDIT_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("Could not load dropped-gear audit helpers")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


DROP = load_drop_audit()


def normalize(value: str) -> str:
    value = "".join(
        char
        for char in unicodedata.normalize("NFKD", value)
        if not unicodedata.combining(char)
    )
    value = value.casefold().replace("’", "").replace("'", "").replace("&", " and ")
    return " ".join(re.sub(r"[^a-z0-9]+", " ", value).split())


def load_item_ids() -> dict[str, int]:
    source = ITEM_IDS_PATH.read_text(encoding="utf-8")
    match = re.search(r"window\.AH_ITEM_IDS=(\{.*?\});\n", source, re.DOTALL)
    if not match:
        raise RuntimeError("Could not parse AH item IDs")
    return {key: int(value) for key, value in json.loads(match.group(1)).items()}


def read_sources() -> dict[str, str]:
    result = {}
    for filename in SOURCE_FILES:
        request = urllib.request.Request(
            f"{SOURCE_ROOT}/{filename}",
            headers={"User-Agent": "wotlk-server-guides-phase3-audit/1.0"},
        )
        with urllib.request.urlopen(request, timeout=120) as response:
            result[filename] = response.read().decode("utf-8", errors="replace")
    return result


def item_records(item_sql: str) -> dict[int, dict]:
    positions, rows = DROP.parse_table(item_sql, "item_template")
    records = {}
    for row in rows:
        item_id = int(row[positions["entry"]])
        records[item_id] = {
            "item_id": item_id,
            "name": row[positions["name"]],
            "item_class": int(row[positions["class"]]),
            "item_subclass": int(row[positions["subclass"]]),
            "quality_id": int(row[positions["Quality"]]),
            "quality": QUALITY_NAMES.get(int(row[positions["Quality"]]), "common"),
            "bonding": int(row[positions["bonding"]]),
            "duration": int(row[positions["duration"]]),
            "max_stack": int(row[positions["stackable"]]),
            "flags": int(row[positions["Flags"]]),
            "required_level": int(row[positions["RequiredLevel"]]),
            "buy_price": int(row[positions["BuyPrice"]]),
            "sell_price": int(row[positions["SellPrice"]]),
            "required_skill_id": int(row[positions["RequiredSkill"]]),
            "required_skill_rank": int(row[positions["RequiredSkillRank"]]),
            "spell_ids": [
                int(row[positions[f"spellid_{index}"]])
                for index in range(1, 6)
                if int(row[positions[f"spellid_{index}"]])
            ],
        }
    return records


def quest_records(sql_by_file: dict[str, str], item_ids: set[int]) -> dict[int, list[dict]]:
    positions, rows = DROP.parse_table(sql_by_file["quest_template.sql"], "quest_template")
    addon_positions, addon_rows = DROP.parse_table(
        sql_by_file["quest_template_addon.sql"], "quest_template_addon"
    )
    addon = {
        int(row[addon_positions["ID"]]): int(row[addon_positions["SpecialFlags"]])
        for row in addon_rows
    }
    result = {item_id: [] for item_id in item_ids}
    for row in rows:
        quest_id = int(row[positions["ID"]])
        for index in range(1, 7):
            item_id = int(row[positions[f"RequiredItemId{index}"]])
            if item_id not in result:
                continue
            result[item_id].append(
                {
                    "quest_id": quest_id,
                    "title": row[positions["LogTitle"]],
                    "required_count": int(row[positions[f"RequiredItemCount{index}"]]),
                    "minimum_level": int(row[positions["MinLevel"]]),
                    "reward_faction_id": int(row[positions["RewardFactionID1"]]),
                    "reward_faction_value_index": int(row[positions["RewardFactionValue1"]]),
                    "reward_faction_override": int(row[positions["RewardFactionOverride1"]]),
                    "repeatable": bool(addon.get(quest_id, 0) & 1),
                }
            )
    return result


def vendor_sources(sql: str, creature_sql: str) -> dict[int, list[dict]]:
    positions, rows = DROP.parse_table(sql, "npc_vendor")
    creature_positions, creature_rows = DROP.parse_table(creature_sql, "creature_template")
    names = {
        int(row[creature_positions["entry"]]): row[creature_positions["name"]]
        for row in creature_rows
    }
    result: dict[int, list[dict]] = {}
    for row in rows:
        item_id = int(row[positions["item"]])
        if item_id <= 0:
            continue
        entry = int(row[positions["entry"]])
        result.setdefault(item_id, []).append(
            {
                "entry": entry,
                "name": names.get(entry, f"Vendor {entry}"),
                "max_count": int(row[positions["maxcount"]]),
                "restock_seconds": int(row[positions["incrtime"]]),
                "extended_cost": int(row[positions["ExtendedCost"]]),
            }
        )
    return result


def compact_sources(rows: list[dict]) -> list[dict]:
    compact = []
    for source in rows:
        compact.append(
            {
                key: source[key]
                for key in (
                    "source_type", "entry", "reference", "chance", "group_id",
                    "min_count", "max_count", "reference_item_chance",
                    "reference_item_group_id", "evidence",
                )
                if key in source
            }
        )
    return compact


def turn_in_catalog(items: dict[int, dict], quests: dict[int, list[dict]]) -> dict:
    sections: dict[str, dict] = {}
    catalog = {}
    for group in TURN_IN_SECTIONS:
        section = sections.setdefault(
            group["title"], {"id": normalize(group["title"]).replace(" ", "-"), "title": group["title"], "items": []}
        )
        for item_id, expected_name in group["items"]:
            source = items[item_id]
            if source["name"] != expected_name:
                raise ValueError(f"Turn-in identity drifted for {item_id}: {source['name']}")
            if source["bonding"] != 0 or source["duration"] != 0:
                raise ValueError(f"Non-auctionable Turn-in item entered catalog: {expected_name}")
            recommended = TURN_IN_STACK_OVERRIDES.get(item_id, group["stack"])
            if source["max_stack"] <= 1 and recommended is not None:
                raise ValueError(f"Non-stackable Turn-in item has a stack suggestion: {expected_name}")
            record = {
                **source,
                "section": group["title"],
                "cohort": group["cohort"],
                "detail": group["detail"],
                "recommended_stack": recommended,
                "demand": group["demand"],
                "restriction": group["restriction"],
                "seed_band": group["seed_band"],
                "quests": quests.get(item_id, []),
            }
            catalog[str(item_id)] = record
            section["items"].append(item_id)
    for removed in REMOVED_TURN_INS:
        source = items[removed["item_id"]]
        if source["bonding"] != 1:
            raise ValueError(f"Expected removed BoP item changed binding: {removed['name']}")
    return {
        "version": 1,
        "audited": date.today().isoformat(),
        "source": {
            "type": "pinned AzerothCore 3.3.5 database",
            "commit": SOURCE_COMMIT,
            "files": [f"{SOURCE_ROOT}/{name}" for name in ("item_template.sql", "quest_template.sql", "quest_template_addon.sql")],
        },
        "scope": "Exact tradeable items replacing the grouped Turn-ins and Quest Items guide rows.",
        "rules": {
            "bonding_allowed": [0],
            "duration_required": 0,
            "nonstackable_stack_suggestion": None,
            "active_listings_used_to_set_prices": False,
        },
        "removed_nonauctionable": list(REMOVED_TURN_INS),
        "sections": list(sections.values()),
        "summary": {
            "auctionable_items": len(catalog),
            "removed_nonauctionable": len(REMOVED_TURN_INS),
            "sections": len(sections),
        },
        "items": catalog,
    }


def parse_recipe_guide() -> list[dict]:
    source = (GUIDES_DIR / "gear-pattern-drops-ah-price-guide.html").read_text(encoding="utf-8")
    item_ids = load_item_ids()
    result = []
    section_pattern = re.compile(r'<section class="common">(?P<section>.*?)</section>', re.DOTALL)
    title_pattern = re.compile(r'<h2[^>]*>(?P<title>.*?)</h2>', re.DOTALL)
    body_pattern = re.compile(r'<tbody>(?P<body>.*?)</tbody>', re.DOTALL)
    row_pattern = re.compile(r"<tr>.*?</tr>", re.DOTALL)
    name_pattern = re.compile(r'<td[^>]*data-column="item"[^>]*>.*?<strong[^>]*>(.*?)</strong>', re.DOTALL)
    market_pattern = re.compile(r'<td[^>]*data-column="market"[^>]*>(.*?)</td>', re.DOTALL)
    source_pattern = re.compile(r'<td[^>]*data-column="source"[^>]*>(.*?)</td>', re.DOTALL)
    for section_match in section_pattern.finditer(source):
        section_source = section_match.group("section")
        title_match = title_pattern.search(section_source)
        body_match = body_pattern.search(section_source)
        if not title_match or not body_match:
            continue
        title = re.sub(r"<[^>]+>", "", title_match.group("title")).replace("↑ Top", "").strip()
        profession = RECIPE_SECTION_PROFESSIONS.get(title)
        if not profession:
            continue
        for row_match in row_pattern.finditer(body_match.group("body")):
            row = row_match.group(0)
            name_match = name_pattern.search(row)
            if not name_match:
                continue
            name = re.sub(r"<[^>]+>", "", name_match.group(1)).replace("&#x27;", "'")
            name = name.replace("&amp;", "&").strip()
            item_id = item_ids.get(normalize(name))
            if not item_id:
                raise ValueError(f"Recipe item ID is unresolved: {name}")
            market_match = market_pattern.search(row)
            source_match = source_pattern.search(row)
            result.append(
                {
                    "item_id": item_id,
                    "name": name,
                    "section": title,
                    "profession": profession,
                    "market": re.sub(r"<[^>]+>", "", market_match.group(1)).strip() if market_match else "",
                    "guide_source": re.sub(r"<[^>]+>", "", source_match.group(1)).strip() if source_match else "",
                }
            )
    if len(result) != 90:
        raise ValueError(f"Expected 90 recipe-drop rows, found {len(result)}")
    return result


def recipe_audit(
    items: dict[int, dict], loot_sources: dict[int, list[dict]], vendors: dict[int, list[dict]]
) -> dict:
    records = {}
    section_counts = Counter()
    for guide_row in parse_recipe_guide():
        item_id = guide_row["item_id"]
        source = items[item_id]
        source_key = normalize(source["name"])
        guide_key = RECIPE_NAME_ALIASES.get(normalize(guide_row["name"]), normalize(guide_row["name"]))
        if source_key != guide_key:
            raise ValueError(f"Recipe identity drifted for {item_id}: {source['name']}")
        if source["item_class"] != 9 or source["bonding"] != 0 or source["duration"] != 0:
            raise ValueError(f"Recipe is not a tradeable permanent recipe item: {source['name']}")
        required_skill = SKILL_NAMES.get(source["required_skill_id"], guide_row["profession"])
        if required_skill != guide_row["profession"]:
            raise ValueError(f"Recipe profession drifted for {source['name']}: {required_skill}")
        records[str(item_id)] = {
            **source,
            **guide_row,
            "required_skill": required_skill,
            "trainer_or_vendor_competition": item_id in vendors,
            "vendor_sources": vendors.get(item_id, []),
            "loot_sources": compact_sources(loot_sources.get(item_id, [])),
        }
        section_counts[guide_row["section"]] += 1
    vendor_competitors = sum(record["trainer_or_vendor_competition"] for record in records.values())
    return {
        "version": 1,
        "audited": date.today().isoformat(),
        "source": {
            "type": "pinned AzerothCore 3.3.5 database",
            "commit": SOURCE_COMMIT,
            "files": [f"{SOURCE_ROOT}/{name}" for name in SOURCE_FILES[:8]],
        },
        "scope": "All 90 tradeable recipe and pattern drops in the active combined guide.",
        "rules": {
            "item_class_required": 9,
            "bonding_allowed": [0],
            "duration_required": 0,
            "active_listings_used_to_set_prices": False,
            "loot_chance_role": "Acquisition evidence only; it does not directly set sale price.",
        },
        "summary": {
            "items": len(records),
            "sections": dict(sorted(section_counts.items())),
            "items_with_saved_loot_sources": sum(bool(record["loot_sources"]) for record in records.values()),
            "trainer_or_vendor_competitors": vendor_competitors,
        },
        "items": records,
    }


def validate(turn_ins: dict, recipes: dict) -> None:
    if turn_ins.get("source", {}).get("commit") != SOURCE_COMMIT:
        raise ValueError("Turn-in audit source commit drifted")
    if turn_ins.get("summary", {}).get("auctionable_items") != 74:
        raise ValueError("Expected 74 auctionable Turn-in items")
    if len(turn_ins.get("removed_nonauctionable", [])) != 3:
        raise ValueError("Expected three explicitly removed non-auctionable Turn-in items")
    if len(turn_ins.get("items", {})) != 74:
        raise ValueError("Turn-in item coverage drifted")
    for record in turn_ins["items"].values():
        if record["bonding"] != 0 or record["duration"] != 0:
            raise ValueError(f"Non-auctionable Turn-in item saved: {record['name']}")
        if record["max_stack"] <= 1 and record["recommended_stack"] is not None:
            raise ValueError(f"Non-stackable Turn-in item has a stack: {record['name']}")
        if not all(int(record["seed_band"][key]) > 0 for key in PRICE_BANDS):
            raise ValueError(f"Turn-in seed band is invalid: {record['name']}")
    if recipes.get("source", {}).get("commit") != SOURCE_COMMIT:
        raise ValueError("Recipe audit source commit drifted")
    if recipes.get("summary", {}).get("items") != 90 or len(recipes.get("items", {})) != 90:
        raise ValueError("Recipe-drop audit does not cover all 90 rows")
    if recipes.get("summary", {}).get("trainer_or_vendor_competitors") != 5:
        raise ValueError("Expected five recipe rows with pinned vendor competition")
    for record in recipes["items"].values():
        if record["item_class"] != 9 or record["bonding"] != 0 or record["duration"] != 0:
            raise ValueError(f"Invalid recipe audit record: {record['name']}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--refresh", action="store_true", help="Refresh both audits from the pinned database")
    group.add_argument("--check", action="store_true", help="Validate the saved audits")
    args = parser.parse_args()

    if args.refresh:
        sql_by_file = read_sources()
        items = item_records(sql_by_file["item_template.sql"])
        turn_in_ids = {item_id for group in TURN_IN_SECTIONS for item_id, _ in group["items"]}
        quests = quest_records(sql_by_file, turn_in_ids)
        loot_sources = DROP.build_loot_sources(sql_by_file, items)
        vendors = vendor_sources(
            sql_by_file["npc_vendor.sql"], sql_by_file["creature_template.sql"]
        )
        turn_ins = turn_in_catalog(items, quests)
        recipes = recipe_audit(items, loot_sources, vendors)
        validate(turn_ins, recipes)
        TURN_IN_OUTPUT.write_text(json.dumps(turn_ins, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
        RECIPE_OUTPUT.write_text(json.dumps(recipes, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
        print(json.dumps({"turn_ins": turn_ins["summary"], "recipes": recipes["summary"]}, indent=2))
        return 0

    turn_ins = json.loads(TURN_IN_OUTPUT.read_text(encoding="utf-8"))
    recipes = json.loads(RECIPE_OUTPUT.read_text(encoding="utf-8"))
    validate(turn_ins, recipes)
    guide_recipes = {(row["item_id"], row["name"]) for row in parse_recipe_guide()}
    saved_recipes = {(record["item_id"], record["name"]) for record in recipes["items"].values()}
    if guide_recipes != saved_recipes:
        raise ValueError("Recipe guide and saved pinned audit differ")
    print("Pinned Phase 3 catalog audits are current: 74 Turn-ins and 90 recipe drops.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
