#!/usr/bin/env python3
"""Audit non-Enchanting crafted prices against exact 3.3.5 recipes.

Recipe metadata is refreshed deliberately from WotLKDB and stored in a local
snapshot. Normal checks are offline: they price each recipe from the guide
set's own quick/target/high reagent references, exact vendor costs, and a small
documented fallback table for recipe inputs not otherwise priced in the site.
"""

from __future__ import annotations

import argparse
import concurrent.futures
import datetime as dt
import html
import json
import math
import re
import sys
import unicodedata
import urllib.request
from decimal import Decimal, ROUND_CEILING
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CRAFTED_DATA_PATH = ROOT / "data" / "ah-crafted-sections.json"
RECIPE_AUDIT_PATH = ROOT / "data" / "ah-crafted-recipe-audit.json"
VENDOR_DATA_PATH = ROOT / "data" / "ah-vendor-sections.json"
ITEM_IDS_PATH = ROOT / "assets" / "ah-item-ids.js"
GUIDES_DIR = ROOT / "guides"

PROFESSION_SKILLS = {
    "inscription-materials-ah-price-guide.html": 773,
    "engineering-materials-ah-price-guide.html": 202,
    "alchemy-materials-ah-price-guide.html": 171,
    "blacksmithing-materials-ah-price-guide.html": 164,
}
PROFESSION_SKILL_FILTERS = {
    # The unfiltered Blacksmithing list contains 525 records but WotLKDB
    # truncates it at 300. These non-overlapping ranges return the complete set.
    164: ("maxrs=300", "minrs=301;maxrs=350", "minrs=351;maxrs=450"),
}
PRICE_BANDS = ("quick", "target", "high")
WOTLKDB_SKILL_URL = "https://wotlkdb.com/?spells=11.{skill_id}"
WOTLKDB_ITEM_URL = "https://wotlkdb.com/?item={item_id}"
USER_AGENT = "WotLK-guide-crafted-price-audit/1.0"

# Margins mirror the demand-sensitive method used by the audited Enchanting
# catalog. They are applied only after the exact reagent floor is known.
DEMAND_MARGINS = {
    "Low": {"quick": "1.03", "target": "1.10", "high": "1.20"},
    "Low-Med": {"quick": "1.04", "target": "1.12", "high": "1.24"},
    "Med": {"quick": "1.05", "target": "1.15", "high": "1.28"},
    "Med-High": {"quick": "1.06", "target": "1.18", "high": "1.31"},
    "High": {"quick": "1.07", "target": "1.21", "high": "1.34"},
    "Very High": {"quick": "1.08", "target": "1.25", "high": "1.38"},
}
DECK_COMPLETION_MARGINS = {
    "quick": Decimal("1.03"),
    "target": Decimal("1.05"),
    "high": Decimal("1.10"),
}

# These recipe inputs are not currently priced as normal rows elsewhere in the
# guide set. Vendor entries use exact unlimited-vendor cost. Market fallbacks
# are intentionally conservative low-pop bands and are named in the snapshot.
REAGENT_PRICE_OVERRIDES = {
    1288: {
        "name": "Large Venom Sac",
        "source_type": "market-fallback",
        "quick": 10_000,
        "target": 20_000,
        "high": 40_000,
        "reason": "Unpriced legacy mob-drop reagent.",
    },
    2901: {
        "name": "Mining Pick",
        "source_type": "coin-vendor",
        "quick": 81,
        "target": 81,
        "high": 81,
        "reason": "Exact unlimited-vendor cost.",
    },
    3164: {
        "name": "Discolored Worg Heart",
        "source_type": "market-fallback",
        "quick": 5_000,
        "target": 10_000,
        "high": 20_000,
        "reason": "Unpriced legacy mob-drop reagent.",
    },
    3819: {
        "name": "Wintersbite",
        "source_type": "market-fallback",
        "quick": 5_000,
        "target": 10_000,
        "high": 20_000,
        "reason": "Unpriced legacy herb; aligned to other scarce Classic herbs.",
    },
    4342: {
        "name": "Purple Dye",
        "source_type": "coin-vendor",
        "quick": 2_500,
        "target": 2_500,
        "high": 2_500,
        "reason": "Exact unlimited-vendor cost.",
    },
    5635: {
        "name": "Sharp Claw",
        "source_type": "market-fallback",
        "quick": 150,
        "target": 200,
        "high": 300,
        "reason": "Current Garrosh-Horde full scan: 10 listings at about 1s 66c each.",
    },
    5956: {
        "name": "Blacksmith Hammer",
        "source_type": "coin-vendor",
        "quick": 18,
        "target": 18,
        "high": 18,
        "reason": "Exact unlimited-vendor cost.",
    },
    7005: {
        "name": "Skinning Knife",
        "source_type": "coin-vendor",
        "quick": 82,
        "target": 82,
        "high": 82,
        "reason": "Exact unlimited-vendor cost.",
    },
    7972: {
        "name": "Ichor of Undeath",
        "source_type": "market-fallback",
        "quick": 800,
        "target": 1_300,
        "high": 2_500,
        "reason": "Current Garrosh-Horde full scan: four listings from 8s to about 13s each.",
    },
    9260: {
        "name": "Volatile Rum",
        "source_type": "market-fallback",
        "quick": 600,
        "target": 700,
        "high": 1_200,
        "reason": "Current Garrosh-Horde full scan: three listings / 15 units at 7s each.",
    },
    10286: {
        "name": "Heart of the Wild",
        "source_type": "market-fallback",
        "quick": 10_000,
        "target": 20_000,
        "high": 40_000,
        "reason": "Unpriced legacy mob-drop reagent.",
    },
    12938: {
        "name": "Blood of Heroes",
        "source_type": "market-fallback",
        "quick": 50_000,
        "target": 100_000,
        "high": 200_000,
        "reason": "Unpriced scarce open-world pickup.",
    },
    39970: {
        "name": "Fire Leaf",
        "source_type": "market-fallback",
        "quick": 12_000,
        "target": 18_000,
        "high": 28_000,
        "reason": "Unpriced Northrend herb; aligned to nearby herb bands.",
    },
    41814: {
        "name": "Glassfin Minnow",
        "source_type": "market-fallback",
        "quick": 6_000,
        "target": 10_000,
        "high": 17_500,
        "reason": "Unpriced Northrend fish; aligned to Fangtooth Herring.",
    },
    4255: {
        "name": "Green Leather Armor",
        "source_type": "market-fallback",
        "quick": 20_000,
        "target": 35_000,
        "high": 60_000,
        "reason": "Unpriced BoE Leatherworking input for one Classic Blacksmithing recipe.",
    },
    5966: {
        "name": "Guardian Gloves",
        "source_type": "market-fallback",
        "quick": 30_000,
        "target": 50_000,
        "high": 90_000,
        "reason": "Unpriced BoE Leatherworking input for one Classic Blacksmithing recipe.",
    },
    11754: {
        "name": "Black Diamond",
        "source_type": "market-fallback",
        "quick": 5_000,
        "target": 10_000,
        "high": 20_000,
        "reason": "Unpriced legacy dungeon-drop gem used by Darkrune Helm.",
    },
    12662: {
        "name": "Demonic Rune",
        "source_type": "bind-on-pickup-farming-estimate",
        "quick": 10_000,
        "target": 20_000,
        "high": 40_000,
        "reason": "BoP farmed reagent; valued only as an explicit access estimate.",
    },
    12753: {
        "name": "Skin of Shadow",
        "source_type": "bind-on-pickup-farming-estimate",
        "quick": 20_000,
        "target": 40_000,
        "high": 80_000,
        "reason": "BoP Scholomance reagent; valued only as an explicit access estimate.",
    },
    12809: {
        "name": "Guardian Stone",
        "source_type": "market-fallback",
        "quick": 20_000,
        "target": 40_000,
        "high": 80_000,
        "reason": "Unpriced scarce legacy mob-drop reagent.",
    },
    15417: {
        "name": "Devilsaur Leather",
        "source_type": "market-fallback",
        "quick": 20_000,
        "target": 35_000,
        "high": 60_000,
        "reason": "Unpriced legacy Skinning material used by Persuader.",
    },
    17012: {
        "name": "Core Leather",
        "source_type": "market-fallback",
        "quick": 20_000,
        "target": 40_000,
        "high": 70_000,
        "reason": "Unpriced Molten Core Skinning material.",
    },
    17203: {
        "name": "Sulfuron Ingot",
        "source_type": "market-fallback",
        "quick": 750_000,
        "target": 1_250_000,
        "high": 2_000_000,
        "reason": "Unpriced epic Molten Core drop used eight at a time by Sulfuron Hammer.",
    },
    19726: {
        "name": "Bloodvine",
        "source_type": "market-fallback",
        "quick": 30_000,
        "target": 50_000,
        "high": 90_000,
        "reason": "Unpriced Zul'Gurub gathering material.",
    },
    19774: {
        "name": "Souldarite",
        "source_type": "market-fallback",
        "quick": 20_000,
        "target": 35_000,
        "high": 60_000,
        "reason": "Unpriced Zul'Gurub ore used by Bloodsoul and Darksoul crafts.",
    },
    20520: {
        "name": "Dark Rune",
        "source_type": "market-fallback",
        "quick": 7_000,
        "target": 8_000,
        "high": 12_000,
        "reason": "Current Garrosh-Horde full scan: eight single-item listings at 80s each.",
    },
    22202: {
        "name": "Small Obsidian Shard",
        "source_type": "market-fallback",
        "quick": 10_000,
        "target": 20_000,
        "high": 40_000,
        "reason": "Unpriced Ahn'Qiraj crafting shard.",
    },
    22203: {
        "name": "Large Obsidian Shard",
        "source_type": "market-fallback",
        "quick": 30_000,
        "target": 50_000,
        "high": 90_000,
        "reason": "Unpriced Ahn'Qiraj crafting shard.",
    },
    22682: {
        "name": "Frozen Rune",
        "source_type": "market-fallback",
        "quick": 250_000,
        "target": 400_000,
        "high": 700_000,
        "reason": "Unpriced scarce legacy Naxxramas crafting rune.",
    },
    34664: {
        "name": "Sunmote",
        "source_type": "market-fallback",
        "quick": 200_000,
        "target": 350_000,
        "high": 600_000,
        "reason": "Unpriced scarce Sunwell crafting drop.",
    },
}


def normalized_item_name(value: str) -> str:
    value = "".join(
        character
        for character in unicodedata.normalize("NFKD", value)
        if unicodedata.category(character) != "Mn"
    )
    value = re.sub(r"['’]", "", value.casefold())
    return " ".join(re.sub(r"[^a-z0-9]+", " ", value).split())


def money_from_text(value: str) -> int:
    total = 0
    clean = " ".join(html.unescape(re.sub(r"<[^>]+>", "", value)).split())
    for amount, unit in re.findall(r"([\d,]+)\s*([gsc])", clean):
        total += int(amount.replace(",", "")) * {"g": 10_000, "s": 100, "c": 1}[unit]
    return total


def fetch_text(url: str) -> str:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=30) as response:
        return response.read().decode("utf-8")


def listview_data(source: str, list_id: str) -> list[dict]:
    marker = f'new Listview({{"template":"spell","id":"{list_id}"'
    if marker not in source:
        return []
    start = source.index(marker)
    data_start = source.index('"data":', start) + len('"data":')
    data, _ = json.JSONDecoder().raw_decode(source[data_start:])
    return data


def wotlkdb_item_names(source: str) -> dict[int, str]:
    names: dict[int, str] = {}
    for match in re.finditer(r'_\[(\d+)\]=(\{"quality".*?\});', source):
        try:
            record = json.loads(match.group(2))
        except json.JSONDecodeError:
            continue
        name = record.get("name_enus")
        if name:
            names[int(match.group(1))] = name
    return names


def clean_spell_name(value: str) -> str:
    return re.sub(r"^[0-9@]", "", value)


def ordered_audited_keys(config: dict) -> list[str]:
    keys: list[str] = []
    for filename in PROFESSION_SKILLS:
        for section in config["guides"][filename]["sections"]:
            keys.extend(section["items"])
    return keys


def recipe_record(
    key: str,
    spell: dict,
    names: dict[int, str],
    *,
    output_item_id: int | None = None,
    output_count: int | None = None,
    output_count_max: int | None = None,
    pricing_rule: str = "direct",
    reagents: list[list[int]] | None = None,
) -> dict:
    creates = spell.get("creates") or [output_item_id, 1, 1]
    final_output_id = int(output_item_id if output_item_id is not None else creates[0])
    final_output_count = int(output_count if output_count is not None else creates[1])
    final_output_count_max = int(
        output_count_max if output_count_max is not None else creates[2]
    )
    if final_output_count <= 0:
        raise ValueError(f"{key}: recipe output count must be positive")
    final_reagents = reagents if reagents is not None else spell.get("reagents", [])
    return {
        "source_spell_id": int(spell["id"]),
        "source_spell_name": clean_spell_name(spell["name"]),
        "output_item_id": final_output_id,
        "output_count": final_output_count,
        "output_count_max": final_output_count_max,
        "pricing_rule": pricing_rule,
        "reagents": [
            {
                "item_id": int(item_id),
                "name": names[int(item_id)],
                "count": int(count),
            }
            for item_id, count in final_reagents
        ],
    }


def refresh_recipe_audit(config: dict) -> dict:
    item_to_key: dict[int, tuple[str, str, int]] = {}
    for filename, skill_id in PROFESSION_SKILLS.items():
        for section in config["guides"][filename]["sections"]:
            for key in section["items"]:
                item_id = int(config["catalog"][key]["item_id"])
                item_to_key[item_id] = (key, filename, skill_id)

    names: dict[int, str] = {}
    matches: dict[str, dict] = {}
    profession_spells: dict[int, dict[int, dict]] = {}
    for filename, skill_id in PROFESSION_SKILLS.items():
        filters = PROFESSION_SKILL_FILTERS.get(skill_id, ())
        urls = (
            [
                WOTLKDB_SKILL_URL.format(skill_id=skill_id) + f"&filter={filter_value}"
                for filter_value in filters
            ]
            if filters
            else [WOTLKDB_SKILL_URL.format(skill_id=skill_id)]
        )
        spell_map: dict[int, dict] = {}
        for url in urls:
            source = fetch_text(url)
            names.update(wotlkdb_item_names(source))
            spell_map.update(
                {int(spell["id"]): spell for spell in listview_data(source, "spells")}
            )
        spells = list(spell_map.values())
        if skill_id == 164 and len(spells) != 525:
            raise ValueError(
                f"Expected 525 complete Blacksmithing spell records; got {len(spells)}"
            )
        profession_spells[skill_id] = {int(spell["id"]): spell for spell in spells}
        for spell in spells:
            creates = spell.get("creates")
            if not creates or int(creates[0]) not in item_to_key:
                continue
            key, item_filename, _ = item_to_key[int(creates[0])]
            if item_filename == filename:
                matches[key] = spell

    missing = [
        (item_id, key, filename, skill_id)
        for item_id, (key, filename, skill_id) in item_to_key.items()
        if key not in matches
    ]

    def fetch_missing(entry: tuple[int, str, str, int]) -> tuple[tuple[int, str, str, int], str]:
        item_id, _, _, _ = entry
        return entry, fetch_text(WOTLKDB_ITEM_URL.format(item_id=item_id))

    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
        for entry, source in executor.map(fetch_missing, missing):
            item_id, key, _, skill_id = entry
            names.update(wotlkdb_item_names(source))
            candidates = [
                spell
                for spell in listview_data(source, "created-by")
                if skill_id in spell.get("skill", [])
                and (
                    not spell.get("creates")
                    or int(spell["creates"][0]) in {item_id, 44318}
                )
            ]
            if candidates:
                matches[key] = candidates[0]

    recipes: dict[str, dict] = {}
    deck_keys = {"nobles-deck", "chaos-deck", "prisms-deck", "undeath-deck"}
    synthetic_keys = {
        "eng-saronite-bomb",
        "eng-adamantite-stinger",
        "eng-adamantite-shells",
    }
    for key in ordered_audited_keys(config):
        if key in deck_keys or key in synthetic_keys:
            continue
        spell = matches.get(key)
        if not spell:
            raise ValueError(f"No 3.3.5 recipe source found for {key}")
        item_id = int(config["catalog"][key]["item_id"])
        if key.startswith(("ace-", "two-", "three-", "four-", "five-", "six-", "seven-", "eight-")):
            recipes[key] = recipe_record(
                key,
                spell,
                names,
                output_item_id=item_id,
                output_count=1,
                output_count_max=1,
                pricing_rule="random-darkmoon-card",
            )
        else:
            recipes[key] = recipe_record(key, spell, names)

    for family, deck_key in (
        ("nobles", "nobles-deck"),
        ("chaos", "chaos-deck"),
        ("prisms", "prisms-deck"),
        ("undeath", "undeath-deck"),
    ):
        ranks = ("ace", "two", "three", "four", "five", "six", "seven", "eight")
        card_keys = [f"{rank}-{family}" for rank in ranks]
        card_ids = [int(config["catalog"][card_key]["item_id"]) for card_key in card_keys]
        deck_item_id = int(config["catalog"][deck_key]["item_id"])
        source = fetch_text(WOTLKDB_ITEM_URL.format(item_id=deck_item_id))
        names.update(wotlkdb_item_names(source))
        combine_spells = listview_data(source, "created-by")
        if not combine_spells:
            raise ValueError(f"No deck-combine spell found for {deck_key}")
        combine_spell = min(combine_spells, key=lambda spell: int(spell["id"]))
        recipes[deck_key] = recipe_record(
            deck_key,
            combine_spell,
            names,
            output_item_id=deck_item_id,
            output_count=1,
            output_count_max=1,
            pricing_rule="complete-eight-card-deck",
            reagents=[[item_id, 1] for item_id in card_ids],
        )

    box_spell = matches["eng-box-of-bombs"]
    recipes["eng-saronite-bomb"] = recipe_record(
        "eng-saronite-bomb",
        box_spell,
        names,
        output_item_id=41119,
        output_count=10,
        output_count_max=14,
        pricing_rule="crafted-container-minimum-output",
    )

    charged_outputs = {
        "eng-adamantite-stinger": (43676, 33803),
        "eng-adamantite-shells": (30347, 23773),
    }
    for key, (spell_id, output_item_id) in charged_outputs.items():
        spell = profession_spells[202].get(spell_id)
        if not spell:
            raise ValueError(f"Missing Engineering source spell {spell_id} for {key}")
        recipes[key] = recipe_record(
            key,
            spell,
            names,
            output_item_id=output_item_id,
            output_count=1_000,
            output_count_max=1_000,
            pricing_rule="five-charge-device-times-200",
        )

    expected = set(ordered_audited_keys(config))
    if set(recipes) != expected:
        missing_keys = sorted(expected - set(recipes))
        extra_keys = sorted(set(recipes) - expected)
        raise ValueError(f"Recipe snapshot mismatch; missing={missing_keys}, extra={extra_keys}")

    ordered_recipes = {key: recipes[key] for key in ordered_audited_keys(config)}
    return {
        "version": 1,
        "refreshed": dt.date.today().isoformat(),
        "recipe_source": {
            "name": "WotLKDB 3.3.5a profession and item records",
            "profession_url_template": WOTLKDB_SKILL_URL,
            "item_url_template": WOTLKDB_ITEM_URL,
            "complete_skill_filters": {
                str(skill_id): list(filters)
                for skill_id, filters in PROFESSION_SKILL_FILTERS.items()
            },
        },
        "pricing_method": {
            "reagent_reference": "Highest matching quick, target, and high material row outside generated crafted blocks; exact vendor cost where applicable.",
            "crafted_intermediates": "Recursively priced from their own audited recipe floors; canonical Enchanting outputs use their current crafted-catalog bands.",
            "output_quantity": "Minimum guaranteed output; charged devices use all guaranteed charges.",
            "market_margin": "Demand-sensitive margin with upward convenience rounding; existing higher guide prices and matching output rows elsewhere in the guide set remain the baseline.",
            "complete_decks": "At least the sum of all eight audited card prices plus a small completion premium.",
        },
        "reagent_price_overrides": {
            str(item_id): record for item_id, record in REAGENT_PRICE_OVERRIDES.items()
        },
        "recipes": ordered_recipes,
    }


def load_item_ids() -> dict[str, int]:
    source = ITEM_IDS_PATH.read_text(encoding="utf-8")
    match = re.search(r"window\.AH_ITEM_IDS=(\{.*?\});\n", source, re.DOTALL)
    if not match:
        raise ValueError("Could not parse AH item ID map")
    return {key: int(value) for key, value in json.loads(match.group(1)).items()}


def guide_reagent_references() -> dict[int, dict[str, int]]:
    item_ids = load_item_ids()
    candidates: dict[int, list[dict[str, int]]] = {}
    crafted_block = re.compile(
        r"<!-- AH_CRAFTED_SECTION_START -->.*?<!-- AH_CRAFTED_SECTION_END -->",
        re.DOTALL,
    )
    row_pattern = re.compile(r"<tr[^>]*>.*?</tr>", re.DOTALL)
    item_pattern = re.compile(
        r'<td[^>]*data-column="item"[^>]*>.*?<strong[^>]*>(.*?)</strong>',
        re.DOTALL,
    )
    for path in GUIDES_DIR.glob("*ah-price-guide.html"):
        source = crafted_block.sub("", path.read_text(encoding="utf-8"))
        for row_match in row_pattern.finditer(source):
            row = row_match.group(0)
            item_match = item_pattern.search(row)
            if not item_match:
                continue
            name = " ".join(
                html.unescape(re.sub(r"<[^>]+>", "", item_match.group(1))).split()
            )
            item_id = item_ids.get(normalized_item_name(name))
            if not item_id:
                continue
            values: dict[str, int] = {}
            for band in PRICE_BANDS:
                price_match = re.search(
                    rf'<div class="pricepair {band}">.*?'
                    rf'<span class="buyout">(.*?)</span>',
                    row,
                    re.DOTALL,
                )
                if price_match:
                    values[band] = money_from_text(price_match.group(1))
            if set(values) == set(PRICE_BANDS):
                candidates.setdefault(item_id, []).append(values)

    return {
        item_id: {
            band: max(candidate[band] for candidate in item_candidates)
            for band in PRICE_BANDS
        }
        for item_id, item_candidates in candidates.items()
    }


def exact_vendor_prices() -> dict[int, int]:
    config = json.loads(VENDOR_DATA_PATH.read_text(encoding="utf-8"))
    prices: dict[int, int] = {}
    for item in config["catalog"].values():
        if item["source_type"] != "coin-vendor":
            continue
        total_cost = int(item["vendor_cost_copper"])
        buy_count = int(item.get("vendor_buy_count", 1))
        if buy_count <= 0 or total_cost % buy_count:
            raise ValueError(f"Invalid vendor bundle for {item['name']}")
        prices[int(item["item_id"])] = total_cost // buy_count
    return prices


def canonical_crafted_references(config: dict) -> dict[int, dict[str, int]]:
    references: dict[int, dict[str, int]] = {}
    for key, raw in config["catalog"].items():
        item = config.get("catalog_defaults", {}) | config["price_profiles"][raw["profile"]] | raw
        values = {band: int(item[f"{band}_copper"]) for band in PRICE_BANDS}
        if all(value > 0 for value in values.values()):
            references[int(item["item_id"])] = values
    return references


def merged_item(config: dict, key: str) -> dict:
    raw = config["catalog"][key]
    return config["catalog_defaults"] | config["price_profiles"][raw["profile"]] | raw


def calculate_floors(config: dict, audit: dict) -> dict[str, dict[str, int]]:
    recipes = audit["recipes"]
    guide_prices = guide_reagent_references()
    vendor_prices = exact_vendor_prices()
    crafted_prices = canonical_crafted_references(config)
    overrides = {
        int(item_id): {band: int(record[band]) for band in PRICE_BANDS}
        for item_id, record in audit["reagent_price_overrides"].items()
    }
    output_keys = {
        int(config["catalog"][key]["item_id"]): key for key in recipes
    }
    memo: dict[tuple[str, str], int] = {}
    active: set[tuple[str, str]] = set()

    def raw_price(item_id: int, band: str) -> int:
        if item_id in vendor_prices:
            return vendor_prices[item_id]
        if item_id in guide_prices:
            return int(guide_prices[item_id][band])
        if item_id in crafted_prices:
            return int(crafted_prices[item_id][band])
        if item_id in overrides:
            return int(overrides[item_id][band])
        raise ValueError(f"No {band} reagent reference for item {item_id}")

    def floor_for(key: str, band: str) -> int:
        token = (key, band)
        if token in memo:
            return memo[token]
        if token in active:
            raise ValueError(f"Crafted reagent cycle detected at {key} ({band})")
        active.add(token)
        recipe = recipes[key]
        total = 0
        for reagent in recipe["reagents"]:
            item_id = int(reagent["item_id"])
            dependency = output_keys.get(item_id)
            unit_cost = floor_for(dependency, band) if dependency else raw_price(item_id, band)
            total += unit_cost * int(reagent["count"])
        output_count = int(recipe["output_count"])
        memo[token] = math.ceil(total / output_count)
        active.remove(token)
        return memo[token]

    return {
        key: {band: floor_for(key, band) for band in PRICE_BANDS}
        for key in recipes
    }


def rounded_market_price(value: Decimal) -> int:
    copper = int(value.to_integral_value(rounding=ROUND_CEILING))
    if copper < 10_000:
        step = 500
    elif copper < 50_000:
        step = 1_000
    elif copper < 150_000:
        step = 2_500
    elif copper < 250_000:
        step = 5_000
    elif copper < 1_000_000:
        step = 10_000
    elif copper < 5_000_000:
        step = 50_000
    elif copper < 10_000_000:
        step = 100_000
    elif copper < 25_000_000:
        step = 250_000
    else:
        step = 500_000
    return math.ceil(copper / step) * step


def recommended_prices(
    config: dict,
    audit: dict,
    floors: dict[str, dict[str, int]],
) -> dict[str, dict[str, int]]:
    prices: dict[str, dict[str, int]] = {}
    output_references = guide_reagent_references()
    for key, item_floors in floors.items():
        item = merged_item(config, key)
        item_id = int(item["item_id"])
        demand = item["demand"]
        if demand not in DEMAND_MARGINS:
            raise ValueError(f"{key}: unknown demand band {demand}")
        prices[key] = {}
        for band in PRICE_BANDS:
            margin = Decimal(DEMAND_MARGINS[demand][band])
            floor_with_margin = rounded_market_price(Decimal(item_floors[band]) * margin)
            matching_output = output_references.get(item_id, {}).get(band, 0)
            if item.get("price_strategy") == "shared-market-reference":
                if not matching_output:
                    raise ValueError(
                        f"{key}: shared-market-reference has no matching AH market row"
                    )
                prices[key][band] = int(matching_output)
                continue
            current_price = (
                0
                if item.get("profession") == "Blacksmithing"
                else int(item[f"{band}_copper"])
            )
            prices[key][band] = max(current_price, int(matching_output), floor_with_margin)
    output_keys = {
        int(config["catalog"][key]["item_id"]): key for key in floors
    }
    for key, recipe in audit["recipes"].items():
        if recipe["pricing_rule"] != "complete-eight-card-deck":
            continue
        for band in PRICE_BANDS:
            card_total = sum(
                prices[output_keys[int(reagent["item_id"])]][band]
                * int(reagent["count"])
                for reagent in recipe["reagents"]
            )
            completed_deck = rounded_market_price(
                Decimal(card_total) * DECK_COMPLETION_MARGINS[band]
            )
            prices[key][band] = max(prices[key][band], completed_deck)
    return prices


def compact_catalog_object(record: dict) -> str:
    return json.dumps(record, ensure_ascii=False, separators=(",", ":"))


def ordered_audit_item(
    record: dict,
    source_spell_id: int,
    floors: dict[str, int],
    prices: dict[str, int],
) -> dict:
    result: dict = {}
    inserted_audit = False
    inserted_prices = False
    for field, value in record.items():
        if field in {"source_spell_id", "pricing_floor_copper"}:
            continue
        if field in {f"{band}_copper" for band in PRICE_BANDS}:
            if not inserted_prices:
                for band in PRICE_BANDS:
                    result[f"{band}_copper"] = int(prices[band])
                inserted_prices = True
            continue
        result[field] = value
        if field == "detail":
            result["source_spell_id"] = int(source_spell_id)
            result["pricing_floor_copper"] = {
                band: int(floors[band]) for band in PRICE_BANDS
            }
            inserted_audit = True
            if not inserted_prices:
                for band in PRICE_BANDS:
                    result[f"{band}_copper"] = int(prices[band])
                inserted_prices = True
    if not inserted_audit:
        result["source_spell_id"] = int(source_spell_id)
        result["pricing_floor_copper"] = {
            band: int(floors[band]) for band in PRICE_BANDS
        }
    if not inserted_prices:
        for band in PRICE_BANDS:
            result[f"{band}_copper"] = int(prices[band])
    return result


def write_catalog_updates(
    config: dict,
    audit: dict,
    floors: dict[str, dict[str, int]],
    prices: dict[str, dict[str, int]],
) -> None:
    source = CRAFTED_DATA_PATH.read_text(encoding="utf-8")
    for key in audit["recipes"]:
        original = config["catalog"][key]
        updated = ordered_audit_item(
            original,
            int(audit["recipes"][key]["source_spell_id"]),
            floors[key],
            prices[key],
        )
        pattern = re.compile(rf'^(    "{re.escape(key)}": )\{{.*\}}(,?)$', re.MULTILINE)
        replacement = rf"\g<1>{compact_catalog_object(updated)}\g<2>"
        source, count = pattern.subn(replacement, source, count=1)
        if count != 1:
            raise ValueError(f"Could not update canonical catalog line for {key}")
    CRAFTED_DATA_PATH.write_text(source, encoding="utf-8", newline="\n")


def differences(
    config: dict,
    audit: dict,
    floors: dict[str, dict[str, int]],
    prices: dict[str, dict[str, int]],
) -> list[str]:
    problems: list[str] = []
    for key, recipe in audit["recipes"].items():
        item = config["catalog"][key]
        if int(item.get("source_spell_id", 0)) != int(recipe["source_spell_id"]):
            problems.append(f"{key}: source spell is stale")
        stored_floors = item.get("pricing_floor_copper") or {}
        for band in PRICE_BANDS:
            if int(stored_floors.get(band, -1)) != int(floors[key][band]):
                problems.append(f"{key}: {band} reagent floor is stale")
            if int(item.get(f"{band}_copper", -1)) != int(prices[key][band]):
                problems.append(f"{key}: {band} price is stale")
    return problems


def print_summary(
    config: dict,
    audit: dict,
    prices: dict[str, dict[str, int]],
) -> None:
    for filename in PROFESSION_SKILLS:
        keys = [
            key
            for section in config["guides"][filename]["sections"]
            for key in section["items"]
        ]
        changed = 0
        for key in keys:
            current = merged_item(config, key)
            if any(int(current[f"{band}_copper"]) != prices[key][band] for band in PRICE_BANDS):
                changed += 1
        print(f"{filename}: {len(keys)} recipes audited; {changed} price bands updated")
    print(f"Recipe snapshot: {len(audit['recipes'])} non-Enchanting crafted outputs")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--refresh-recipes",
        action="store_true",
        help="Refresh the stored 3.3.5 recipe snapshot from WotLKDB.",
    )
    parser.add_argument(
        "--write",
        action="store_true",
        help="Write the refreshed snapshot and canonical price corrections.",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Exit nonzero if the snapshot, price floors, or prices are stale.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    config = json.loads(CRAFTED_DATA_PATH.read_text(encoding="utf-8"))

    if args.refresh_recipes:
        audit = refresh_recipe_audit(config)
        if args.write:
            RECIPE_AUDIT_PATH.write_text(
                json.dumps(audit, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
                newline="\n",
            )
    else:
        if not RECIPE_AUDIT_PATH.is_file():
            print(
                "Recipe audit snapshot is missing. Run with --refresh-recipes --write.",
                file=sys.stderr,
            )
            return 1
        audit = json.loads(RECIPE_AUDIT_PATH.read_text(encoding="utf-8"))

    expected_keys = set(ordered_audited_keys(config))
    if set(audit.get("recipes", {})) != expected_keys:
        raise ValueError("Recipe audit snapshot does not match the non-Enchanting catalog")

    floors = calculate_floors(config, audit)
    prices = recommended_prices(config, audit, floors)
    print_summary(config, audit, prices)

    if args.write:
        write_catalog_updates(config, audit, floors, prices)
        return 0

    problems = differences(config, audit, floors, prices)
    if problems:
        for problem in problems[:50]:
            print(problem, file=sys.stderr)
        if len(problems) > 50:
            print(f"...and {len(problems) - 50} more", file=sys.stderr)
        return 1
    print("Non-Enchanting crafted recipe floors and prices are current.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
