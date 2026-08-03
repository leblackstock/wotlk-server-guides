#!/usr/bin/env python3
"""Validate every canonical profession-crafted AH catalog."""

from __future__ import annotations

import html
import json
import re
import subprocess
import sys
import unicodedata
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "data" / "ah-crafted-sections.json"
RECIPE_AUDIT_PATH = ROOT / "data" / "ah-crafted-recipe-audit.json"
INDEX_PATH = ROOT / "assets" / "ah-search-index.js"
ITEM_IDS_PATH = ROOT / "assets" / "ah-item-ids.js"
EXPECTED_GUIDE_COUNTS = {
    "inscription-materials-ah-price-guide.html": 107,
    "engineering-materials-ah-price-guide.html": 55,
    "alchemy-materials-ah-price-guide.html": 206,
    "enchanting-mats-ah-price-guide.html": 276,
    "blacksmithing-materials-ah-price-guide.html": 453,
}


def fail(message: str) -> None:
    raise AssertionError(message)


def format_money(copper: int) -> str:
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


def generated_json(path: Path, variable: str) -> dict:
    source = path.read_text(encoding="utf-8")
    match = re.search(rf"window\.{variable}=(\{{.*?\}});\n", source, re.DOTALL)
    if not match:
        fail(f"Could not parse {variable} from {path.name}")
    return json.loads(match.group(1))


def normalized_item_name(value: str) -> str:
    value = "".join(
        character
        for character in unicodedata.normalize("NFKD", value)
        if unicodedata.category(character) != "Mn"
    )
    value = re.sub(r"['’]", "", value.casefold())
    return " ".join(re.sub(r"[^a-z0-9]+", " ", value).split())


def merged_item(config: dict, key: str) -> dict:
    raw_item = config["catalog"][key]
    return (
        config["catalog_defaults"]
        | config["price_profiles"][raw_item["profile"]]
        | raw_item
    )


def main() -> int:
    subprocess.run(
        [sys.executable, "scripts/render-ah-shared-sections.py", "--check"],
        cwd=ROOT,
        check=True,
    )
    subprocess.run(
        [sys.executable, "scripts/build-ah-search-index.py", "--check"],
        cwd=ROOT,
        check=True,
    )
    subprocess.run(
        [sys.executable, "scripts/audit-ah-crafted-prices.py", "--check"],
        cwd=ROOT,
        check=True,
    )

    config = json.loads(DATA_PATH.read_text(encoding="utf-8"))
    recipe_audit = json.loads(RECIPE_AUDIT_PATH.read_text(encoding="utf-8"))
    catalog = config["catalog"]
    guides = config["guides"]
    index = generated_json(INDEX_PATH, "AH_SEARCH_INDEX")
    item_ids = generated_json(ITEM_IDS_PATH, "AH_ITEM_IDS")

    expected_total = sum(EXPECTED_GUIDE_COUNTS.values())
    if len(catalog) != expected_total:
        fail(f"Expected {expected_total} curated crafted outputs, found {len(catalog)}")
    if set(guides) != set(EXPECTED_GUIDE_COUNTS):
        fail("Crafted guide configuration does not match the validated guide set")
    if len({item["item_id"] for item in catalog.values()}) != len(catalog):
        fail("Crafted item IDs must be unique")
    if len({item["name"].casefold() for item in catalog.values()}) != len(catalog):
        fail("Crafted item names must be unique")

    non_enchanting_keys = {
        key
        for filename, guide in guides.items()
        if filename != "enchanting-mats-ah-price-guide.html"
        for section in guide["sections"]
        for key in section["items"]
    }
    if len(non_enchanting_keys) != 821:
        fail(f"Expected 821 non-Enchanting recipe audits, found {len(non_enchanting_keys)}")
    if set(recipe_audit.get("recipes", {})) != non_enchanting_keys:
        fail("Non-Enchanting recipe snapshot does not match the crafted catalog")
    for key in non_enchanting_keys:
        item = merged_item(config, key)
        recipe = recipe_audit["recipes"][key]
        if int(item.get("source_spell_id", 0)) != int(recipe["source_spell_id"]):
            fail(f"{key}: source spell does not match the recipe audit")
        if int(recipe["output_item_id"]) != int(item["item_id"]):
            fail(f"{key}: recipe output item does not match the catalog item")
        if int(recipe["output_count"]) <= 0 or not recipe.get("reagents"):
            fail(f"{key}: recipe output or reagent snapshot is incomplete")
        floors = item.get("pricing_floor_copper") or {}
        if set(floors) != {"quick", "target", "high"}:
            fail(f"{key}: audited price floors are missing")
        for band in ("quick", "target", "high"):
            if (
                item.get("price_strategy") != "shared-market-reference"
                and int(item[f"{band}_copper"]) < int(floors[band])
            ):
                fail(f"{key}: {band} price falls below its audited craft floor")
        if item.get("price_strategy") == "shared-market-reference":
            if "below" not in item.get("row_note", "") or "skip" not in item.get("row_note", ""):
                fail(f"{key}: shared market pricing must explain the unprofitable craft route")

    used_keys: list[str] = []
    sources: dict[str, str] = {}
    for filename, guide in guides.items():
        source = (ROOT / "guides" / filename).read_text(encoding="utf-8")
        sources[filename] = source
        if source.count("<!-- AH_CRAFTED_SECTION_START -->") != 1:
            fail(f"{filename}: expected one generated crafted-market block")

        expected_order = [
            key
            for section in guide["sections"]
            for key in section["items"]
        ]
        if len(expected_order) != EXPECTED_GUIDE_COUNTS[filename]:
            fail(
                f"{filename}: expected {EXPECTED_GUIDE_COUNTS[filename]} configured "
                f"outputs, found {len(expected_order)}"
            )
        actual_order = re.findall(r'data-crafted-key="([^"]+)"', source)
        if actual_order != expected_order:
            fail(f"{filename}: rendered rows do not match canonical crafted order")
        used_keys.extend(expected_order)

        shared_note = guide.get("shared_note")
        if not shared_note:
            fail(f"{filename}: every crafted guide needs one shared pricing note")
        if source.count(f'id="{shared_note["id"]}"') != 1:
            fail(f"{filename}: shared pricing note must render exactly once")
        if source.count('class="crafted-note-ref"') != len(expected_order):
            fail(f"{filename}: every crafted row must reference the shared note")
        if source.count('class="crafted-item-note"') != len(expected_order):
            fail(f"{filename}: every crafted row must render an item-specific note")
        if source.count('class="crafted-recipe-link ') != len(expected_order):
            fail(f"{filename}: every crafted row must render a recipe hover link")
        if "<strong>Reagent floor:</strong>" in source:
            fail(f"{filename}: repeated row-level reagent-floor copy remains")

        for key in expected_order:
            item = merged_item(config, key)
            if not item["crafted"] or not item["tradeable"]:
                fail(f"{key}: every listed output must be crafted and tradeable")
            if item["binding"] not in {"none", "boe"}:
                fail(f"{key}: BoP or unknown binding is forbidden")

            quick = int(item["quick_copper"])
            target = int(item["target_copper"])
            high = int(item["high_copper"])
            if not 0 < quick <= target <= high:
                fail(f"{key}: expected positive quick <= target <= high prices")

            profession = re.escape(item["profession"])
            row_pattern = (
                rf'<tr data-crafted-key="{re.escape(key)}" '
                rf'data-market-source="crafted" data-profession="{profession}">'
                rf"(.*?)</tr>"
            )
            row_match = re.search(row_pattern, source, re.DOTALL)
            if not row_match:
                fail(f"{key}: missing standard crafted AH row metadata")
            row = row_match.group(1)

            for kind, value in (
                ("target", target),
                ("quick", quick),
                ("high", high),
            ):
                bid_value = int(
                    item.get(
                        f"{kind}_bid_copper",
                        max(1, round(value * 0.85)),
                    )
                )
                if not 0 < bid_value <= value:
                    fail(f"{key}: expected positive {kind} bid <= buyout")
                price_pattern = (
                    rf'<div class="pricepair {kind}">.*?'
                    rf'<span class="bid">{re.escape(format_money(bid_value))}</span>.*?'
                    rf'<span class="buyout">{re.escape(format_money(value))}</span>'
                )
                if not re.search(price_pattern, row, re.DOTALL):
                    fail(f"{key}: {kind} price does not match canonical data")
            note_reference = (
                f'class="crafted-note-ref" href="#{html.escape(shared_note["id"])}" '
                f'aria-label="See {html.escape(shared_note["label"])} note">'
                f'{html.escape(shared_note["marker"])}</a>'
            )
            if note_reference not in row:
                fail(f"{key}: row is missing its shared-note reference")
            row_note = item.get("row_note", "").strip()
            if not row_note:
                fail(f"{key}: item-specific use or market note is missing")
            if (
                f'<span class="crafted-item-note">{html.escape(row_note)}</span>'
                not in row
            ):
                fail(f"{key}: item-specific note does not match canonical data")
            source_spell_id = int(item.get("source_spell_id", 0))
            if source_spell_id <= 0:
                fail(f"{key}: source spell ID is missing")
            recipe_url = f"https://www.wowhead.com/wotlk/spell={source_spell_id}"
            recipe_link = (
                '<a class="crafted-recipe-link ah-item-tooltip '
                'ah-item-tooltip-label" '
                f'href="{recipe_url}" target="_blank" rel="noopener" '
                f'data-wowhead="spell={source_spell_id}&amp;domain=wotlk" '
                f'data-ah-wowhead-url="{recipe_url}" '
                f'aria-label="Open {html.escape(item["name"])} recipe and '
                'materials on Wowhead">Recipe &amp; mats ↗</a>'
            )
            if recipe_link not in row:
                fail(f"{key}: recipe hover link does not match its source spell")

            matches = [
                entry
                for entry in index["items"]
                if entry["name"] == item["name"]
                and entry["href"].startswith(f"./guides/{filename}#")
                and entry["marketSource"] == "crafted"
                and entry["profession"] == item["profession"]
            ]
            if len(matches) != 1:
                fail(f"{key}: expected one searchable crafted entry, found {len(matches)}")
            if matches[0]["target"] != format_money(target):
                fail(f"{key}: search target does not match canonical target")
            if item_ids.get(normalized_item_name(item["name"])) != int(item["item_id"]):
                fail(f"{key}: tooltip item ID is missing or incorrect")

    if len(used_keys) != len(set(used_keys)) or set(used_keys) != set(catalog):
        fail("Crafted catalog usage is duplicated or incomplete")

    inscription_block = sources[
        "inscription-materials-ah-price-guide.html"
    ].split("<!-- AH_CRAFTED_SECTION_START -->", 1)[1].split(
        "<!-- AH_CRAFTED_SECTION_END -->", 1
    )[0]
    for label in (
        "Scroll of Protection VIII",
        "Scroll of Recall",
        "Master's Inscription",
        "Darkmoon Card of the North",
        "Darkmoon Card: Greatness",
    ):
        if re.search(
            rf'<strong class="q-[^"]+">{re.escape(html.escape(label))}</strong>',
            inscription_block,
        ):
            fail(f"Excluded or non-tradeable Inscription output leaked in: {label}")

    engineering_names = {
        merged_item(config, key)["name"]
        for key in used_keys
        if key.startswith("eng-")
    }
    for label in (
        "Titansteel Bar",
        "Cobalt Bar",
        "Dense Stone",
        "Salvaged Iron Golem Parts",
    ):
        if label in engineering_names:
            fail(f"Engineering input or vendor component leaked into crafted outputs: {label}")

    alchemy_names = {
        merged_item(config, key)["name"]
        for key in used_keys
        if key.startswith("alch-")
    }
    for label in (
        "Frost Lotus",
        "Eternal Fire",
        "Scarlet Ruby",
        "Pygmy Suckerfish",
        "Crystal Vial",
        "Arcanite Bar",
    ):
        if label in alchemy_names:
            fail(f"Alchemy input, vendor item, or reference row leaked into crafted outputs: {label}")

    blacksmithing_items = {
        merged_item(config, key)["name"]: merged_item(config, key)
        for key in used_keys
        if key.startswith("bs-")
    }
    if len(blacksmithing_items) != 453:
        fail(f"Expected 453 distinct Blacksmithing output names, found {len(blacksmithing_items)}")
    for label in (
        "Dark Iron Plate",
        "Lionheart Executioner",
        "Stormherald",
        "Hard Khorium Battleplate",
        "Chestplate of Conquest",
        "Legplates of Conquest",
    ):
        if label in blacksmithing_items:
            fail(f"BoP Blacksmithing output leaked into the AH catalog: {label}")
    alliance_only_ids = {47570, 47572, 47574, 47589, 47591, 47593}
    leaked_alliance = alliance_only_ids & {
        int(item["item_id"]) for item in blacksmithing_items.values()
    }
    if leaked_alliance:
        fail(f"Alliance-only duplicate Blacksmithing records leaked in: {sorted(leaked_alliance)}")
    for item in blacksmithing_items.values():
        if "item-level 0" in item["detail"] or "weapon weapon" in item["detail"]:
            fail(f"Misclassified Blacksmithing utility remains: {item['name']}")

    for label in (
        "Elixir of Tongues (NYI)",
        "Philosopher's Stone",
        "Alchemist's Stone",
        "Mercurial Alchemist Stone",
        "Indestructible Alchemist's Stone",
        "Mighty Alchemist's Stone",
        "Endless Healing Potion",
        "Endless Mana Potion",
        "Flask of the North",
    ):
        if label in alchemy_names:
            fail(f"Non-tradeable or NYI Alchemy output leaked in: {label}")

    for label in (
        "Elixir of Accuracy",
        "Mighty Shadow Protection Potion",
        "Cardinal Ruby",
        "Flask of Relentless Assault",
        "Haste Potion",
        "Cauldron of Major Fire Protection",
        "Flask of Supreme Power",
        "Living Action Potion",
        "Free Action Potion",
        "Blackmouth Oil",
        "Goblin Rocket Fuel",
    ):
        if label not in alchemy_names:
            fail(f"Expanded Alchemy era/category coverage is missing: {label}")

    alchemy_sections = guides["alchemy-materials-ah-price-guide.html"]["sections"]
    if len(alchemy_sections) != 20:
        fail(f"Expected 20 expanded Alchemy sections, found {len(alchemy_sections)}")

    representative_non_enchanting_prices = {
        "chaos-deck": 10_250_000,
        "eng-khorium-power-core": 520_000,
        "alch-flask-endless-rage": 550_000,
        "alch-flask-frost-wyrm": 600_000,
        "alch-cardinal-ruby": 1_200_000,
        "bs-eternal-belt-buckle": 340_000,
        "bs-puresteel-legplates": 76_500_000,
    }
    for key, expected_target in representative_non_enchanting_prices.items():
        if int(merged_item(config, key)["target_copper"]) != expected_target:
            fail(f"{key}: audited target price changed unexpectedly")

    representative_non_enchanting_notes = {
        "glyph-disease": "refreshes disease durations",
        "chaos-deck": "price it separately from Nobles",
        "eng-khorium-power-core": "used in high-end devices",
        "alch-flask-endless-rage": "Increases attack power by 180",
        "alch-cardinal-ruby": "Uncut red epic gem",
        "bs-eternal-belt-buckle": "one permanent socket",
        "bs-puresteel-legplates": "ICC-era raid gearing",
    }
    for key, expected_fragment in representative_non_enchanting_notes.items():
        if expected_fragment not in merged_item(config, key)["row_note"]:
            fail(f"{key}: expected item-specific use or market context is missing")

    for filename in (
        "inscription-materials-ah-price-guide.html",
        "engineering-materials-ah-price-guide.html",
        "alchemy-materials-ah-price-guide.html",
        "blacksmithing-materials-ah-price-guide.html",
    ):
        keys = [
            key
            for section in guides[filename]["sections"]
            for key in section["items"]
        ]
        row_notes = [merged_item(config, key)["row_note"] for key in keys]
        if len(set(row_notes)) != len(row_notes):
            fail(f"{filename}: duplicated item-note boilerplate remains")

    for filename in (
        "inscription-materials-ah-price-guide.html",
        "engineering-materials-ah-price-guide.html",
        "alchemy-materials-ah-price-guide.html",
        "blacksmithing-materials-ah-price-guide.html",
    ):
        if "Updated 2026-08-02" not in sources[filename]:
            fail(f"{filename}: crafted-price audit footer date is stale")
        if "exact 3.3.5 recipe" not in sources[filename]:
            fail(f"{filename}: recipe-level pricing method is not explained")

    alchemy_source = sources["alchemy-materials-ah-price-guide.html"]
    alchemy_outside_block = (
        alchemy_source.split("<!-- AH_CRAFTED_SECTION_START -->", 1)[0]
        + alchemy_source.split("<!-- AH_CRAFTED_SECTION_END -->", 1)[1]
    )
    if re.search(
        r'<strong class="q-common">Pygmy Oil</strong>',
        alchemy_outside_block,
    ):
        fail("Pygmy Oil remains duplicated in the Alchemy input rows")
    if re.search(
        r'<strong class="q-uncommon">Primal Might</strong>',
        alchemy_outside_block,
    ):
        fail("Primal Might remains duplicated in the Alchemy input rows")
    if "Major finished flasks / potions" in alchemy_outside_block:
        fail("Legacy Alchemy finished-consumable section remains after migration")

    enchanting_names = {
        merged_item(config, key)["name"]
        for key in used_keys
        if key.startswith("ench-")
    }
    enchanting_scrolls = {
        name for name in enchanting_names if name.startswith("Scroll of Enchant ")
    }
    if len(enchanting_scrolls) != 259:
        fail(f"Expected 259 valid Enchanting scrolls, found {len(enchanting_scrolls)}")

    for label in (
        "Scroll of Enchant Weapon - Exceptional Striking",
        "Scroll of Enchant Weapon - Exceptional Intellect",
        "Scroll of Enchant Gloves - Exceptional Healing",
        "Scroll of Enchant Shield - Exceptional Stamina",
        "Scroll of Enchant Weapon - Exceptional Healing",
        "Scroll of Enchant Bracers - Major Healing",
        "Runed Titanium Rod",
        "Smoking Heart of the Mountain",
        "Arcane Dust",
        "Large Prismatic Shard",
        "Small Prismatic Shard",
    ):
        if label in enchanting_names:
            fail(f"Invalid, BoP, or duplicate Enchanting output leaked in: {label}")

    if any(name.startswith("Scroll of Enchant Ring") for name in enchanting_names):
        fail("Self-only ring enchants must not appear as auctionable scrolls")

    for label in (
        "Scroll of Enchant Weapon - Berserking",
        "Scroll of Enchant Weapon - Blade Ward",
        "Scroll of Enchant Chest - Powerful Stats",
        "Scroll of Enchant Boots - Icewalker",
        "Scroll of Enchant Weapon - Mongoose",
        "Scroll of Enchant Boots - Boar's Speed",
        "Scroll of Enchant Weapon - Crusader",
        "Scroll of Enchant Boots - Minor Speed",
        "Brilliant Wizard Oil",
        "Superior Mana Oil",
        "Greater Magic Wand",
        "Enchanted Thorium Bar",
        "Void Sphere",
    ):
        if label not in enchanting_names:
            fail(f"Expanded Enchanting era/category coverage is missing: {label}")

    enchanting_sections = guides["enchanting-mats-ah-price-guide.html"]["sections"]
    if len(enchanting_sections) != 25:
        fail(f"Expected 25 expanded Enchanting sections, found {len(enchanting_sections)}")

    enchanting_source = sources["enchanting-mats-ah-price-guide.html"]
    if "Updated 2026-08-02" not in enchanting_source:
        fail("Enchanting guide footer date was not updated")
    if enchanting_source.count('id="crafted-enchanting-pricing-note"') != 1:
        fail("Enchanting guide must contain exactly one shared pricing note")
    if enchanting_source.count('class="crafted-note-ref"') != 276:
        fail("Every Enchanting crafted row must reference the shared pricing note")
    if enchanting_source.count('class="crafted-item-note"') != 276:
        fail("Every Enchanting crafted row must render an item-specific note")
    if enchanting_source.count('class="crafted-recipe-link ') != 276:
        fail("Every Enchanting crafted row must render a recipe hover link")
    if enchanting_source.count("Recipe &amp; mats ↗</a>") != 276:
        fail("Every Enchanting recipe link must use the compact shared label")
    if enchanting_source.count("<strong>* Reagent floor and pricing:</strong>") != 1:
        fail("Enchanting reagent-floor copy must appear exactly once")
    if "Each price band was recalculated per item" not in enchanting_source:
        fail("Enchanting shared note must explain the per-item price method")
    for repeated_copy in (
        "Exact Northrend dust, essence, shard, crystal, and Weapon Vellum III cost",
        "Wrath weapon-enchant scroll. Prices vary sharply by recipe",
        "Legacy armor-enchant scroll. Test one listing at a time",
        "Legacy weapon oil. Confirm that the effect works",
    ):
        if repeated_copy in enchanting_source:
            fail(f"Repeated Enchanting row copy remains: {repeated_copy}")

    enchanting_keys = [
        key
        for section in enchanting_sections
        for key in section["items"]
    ]
    wrath_keys = [
        key
        for section in enchanting_sections[:7]
        for key in section["items"]
    ]
    if len(wrath_keys) != 72:
        fail(f"Expected 72 Wrath enchant rows, found {len(wrath_keys)}")

    for key in enchanting_keys:
        item = merged_item(config, key)
        if not item.get("row_note", "").strip():
            fail(f"{key}: every Enchanting output needs a specific market/effect note")
        if int(item.get("source_spell_id", 0)) <= 0:
            fail(f"{key}: source spell ID is missing")
        floors = item.get("pricing_floor_copper")
        if set(floors or {}) != {"quick", "target", "high"}:
            fail(f"{key}: audited price floors are missing")
        for band in ("quick", "target", "high"):
            if int(item[f"{band}_copper"]) < int(floors[band]):
                fail(f"{key}: {band} price falls below its audited craft floor")
        if item["name"].startswith("Scroll of ") and item.get("vellum_rank") not in {
            1,
            2,
            3,
        }:
            fail(f"{key}: compatible vellum rank is missing")

    enchanting_notes = [
        merged_item(config, key)["row_note"] for key in enchanting_keys
    ]
    if len(set(enchanting_notes)) != len(enchanting_notes):
        fail("Enchanting item notes must be specific rather than duplicated boilerplate")
    for repeated_note_fragment in (
        "Permanently enchant",
        "Prices vary sharply",
        "Post one at a time",
    ):
        if any(repeated_note_fragment in note for note in enchanting_notes):
            fail(f"Repeated Enchanting note boilerplate remains: {repeated_note_fragment}")

    representative_enchants = {
        "ench-scroll-of-enchant-weapon-berserking": (
            5_100_000,
            "Premium raid melee-DPS staple",
        ),
        "ench-scroll-of-enchant-chest-powerful-stats": (
            2_150_000,
            "Premier raid all-stats chest enchant",
        ),
        "ench-scroll-of-enchant-boots-tuskarrs-vitality": (
            760_000,
            "Raid movement-speed staple",
        ),
        "ench-scroll-of-enchant-gloves-armsman": (
            None,
            "Tank threat and parry glove enchant",
        ),
        "ench-scroll-of-enchant-cloak-superior-frost-resistance": (
            None,
            "Encounter-specific Frost resistance",
        ),
        "ench-scroll-of-enchant-gloves-angler": (
            None,
            "Fishing utility; not a raid enchant",
        ),
        "ench-superior-wizard-oil": (
            None,
            "not for Wrath raid gear",
        ),
    }
    for key, (expected_target, note_fragment) in representative_enchants.items():
        item = merged_item(config, key)
        if expected_target is not None and int(item["target_copper"]) != expected_target:
            fail(f"{key}: audited target price changed unexpectedly")
        if note_fragment not in item["row_note"]:
            fail(f"{key}: expected note context is missing")

    if merged_item(config, "ench-scroll-of-enchant-gloves-angler")["vellum_rank"] != 1:
        fail("Angler should use unrestricted Armor Vellum, not Armor Vellum III")
    if merged_item(config, "ench-scroll-of-enchant-weapon-mongoose")["vellum_rank"] != 2:
        fail("Mongoose should use Weapon Vellum II for its level-35 restriction")
    if merged_item(config, "ench-scroll-of-enchant-weapon-berserking")["vellum_rank"] != 3:
        fail("Berserking should use Weapon Vellum III")

    print(
        "Crafted-market catalog, rows, prices, search metadata, and tooltip IDs "
        "are valid for Inscription, Engineering, Alchemy, and Enchanting."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
