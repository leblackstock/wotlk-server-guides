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
MANIFEST_PATH = ROOT / "data" / "ah-guides.json"
RECIPE_AUDIT_PATH = ROOT / "data" / "ah-crafted-recipe-audit.json"
GATHERING_EVIDENCE_PATH = ROOT / "data" / "ah-gathering-material-price-evidence.json"
PROFESSION_MATERIAL_EVIDENCE_PATH = ROOT / "data" / "ah-profession-material-price-evidence.json"
BLACKSMITHING_EVIDENCE_PATH = ROOT / "data" / "ah-blacksmithing-price-evidence.json"
ENGINEERING_EVIDENCE_PATH = ROOT / "data" / "ah-engineering-price-evidence.json"
JEWELCRAFTING_GEM_EVIDENCE_PATH = ROOT / "data" / "ah-jewelcrafting-gem-price-evidence.json"
JEWELCRAFTING_JEWELRY_EVIDENCE_PATH = ROOT / "data" / "ah-jewelcrafting-jewelry-price-evidence.json"
INSCRIPTION_EVIDENCE_PATH = ROOT / "data" / "ah-inscription-price-evidence.json"
TAILORING_EVIDENCE_PATH = ROOT / "data" / "ah-tailoring-price-evidence.json"
LEATHERWORKING_EVIDENCE_PATH = ROOT / "data" / "ah-leatherworking-price-evidence.json"
COOKING_EVIDENCE_PATH = ROOT / "data" / "ah-cooking-price-evidence.json"
FIRST_AID_EVIDENCE_PATH = ROOT / "data" / "ah-first-aid-price-evidence.json"
INDEX_PATH = ROOT / "assets" / "ah-search-index.js"
ITEM_IDS_PATH = ROOT / "assets" / "ah-item-ids.js"
EXPECTED_GUIDE_COUNTS = {
    "inscription-materials-ah-price-guide.html": 107,
    "engineering-materials-ah-price-guide.html": 64,
    "alchemy-materials-ah-price-guide.html": 206,
    "enchanting-mats-ah-price-guide.html": 276,
    "blacksmithing-materials-ah-price-guide.html": 453,
    "jewelcrafting-gems-ah-price-guide.html": 497,
    "tailoring-cloth-ah-price-guide.html": 424,
    "skinning-leatherworking-materials-ah-price-guide.html": 490,
    "fishing-cooking-materials-ah-price-guide.html": 162,
    "mining-smithing-ah-price-guide.html": 24,
}


def fail(message: str) -> None:
    raise AssertionError(message)


def format_money(copper: int) -> str:
    if copper >= 10_000:
        copper = ((copper + 50) // 100) * 100
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


def apply_guide_supplements(config: dict) -> dict:
    for filename, supplement in config.get("guide_supplements", {}).items():
        guide = config["guides"][filename]
        guide.update(supplement.get("overrides", {}))
        guide["sections"] = (
            list(supplement.get("prepend_sections", []))
            + list(guide.get("sections", []))
            + list(supplement.get("append_sections", []))
        )
    return config


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
    subprocess.run(
        [sys.executable, "scripts/apply-ah-price-baselines.py", "--check"],
        cwd=ROOT,
        check=True,
    )

    config = apply_guide_supplements(
        json.loads(DATA_PATH.read_text(encoding="utf-8"))
    )
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    recipe_audit = json.loads(RECIPE_AUDIT_PATH.read_text(encoding="utf-8"))
    gathering_evidence = json.loads(
        GATHERING_EVIDENCE_PATH.read_text(encoding="utf-8")
    )
    profession_material_evidence = json.loads(
        PROFESSION_MATERIAL_EVIDENCE_PATH.read_text(encoding="utf-8")
    )
    blacksmithing_evidence = json.loads(
        BLACKSMITHING_EVIDENCE_PATH.read_text(encoding="utf-8")
    )
    engineering_evidence = json.loads(
        ENGINEERING_EVIDENCE_PATH.read_text(encoding="utf-8")
    )
    jewelcrafting_gem_evidence = json.loads(
        JEWELCRAFTING_GEM_EVIDENCE_PATH.read_text(encoding="utf-8")
    )
    jewelcrafting_jewelry_evidence = json.loads(
        JEWELCRAFTING_JEWELRY_EVIDENCE_PATH.read_text(encoding="utf-8")
    )
    inscription_evidence = json.loads(
        INSCRIPTION_EVIDENCE_PATH.read_text(encoding="utf-8")
    )
    tailoring_evidence = json.loads(
        TAILORING_EVIDENCE_PATH.read_text(encoding="utf-8")
    )
    leatherworking_evidence = json.loads(
        LEATHERWORKING_EVIDENCE_PATH.read_text(encoding="utf-8")
    )
    cooking_evidence = json.loads(
        COOKING_EVIDENCE_PATH.read_text(encoding="utf-8")
    )
    first_aid_evidence = json.loads(
        FIRST_AID_EVIDENCE_PATH.read_text(encoding="utf-8")
    )
    gathering_override_keys = {
        record["canonical_key"]
        for evidence in (gathering_evidence, profession_material_evidence)
        for record in evidence["items"].values()
        if record["owner"] == "crafted"
    }
    blacksmithing_override_keys = {
        record["canonical_key"] for record in blacksmithing_evidence["items"].values()
    }
    engineering_override_keys = {
        record["canonical_key"] for record in engineering_evidence["items"].values()
    }
    jewelcrafting_gem_override_keys = {
        record["canonical_key"]
        for record in jewelcrafting_gem_evidence["items"].values()
    }
    jewelcrafting_jewelry_override_keys = {
        record["canonical_key"]
        for record in jewelcrafting_jewelry_evidence["items"].values()
    }
    inscription_override_keys = {
        record["canonical_key"]
        for record in inscription_evidence["items"].values()
    }
    tailoring_override_keys = {
        record["canonical_key"]
        for record in tailoring_evidence["items"].values()
    }
    leatherworking_override_keys = {
        record["canonical_key"]
        for record in leatherworking_evidence["items"].values()
    }
    cooking_override_keys = {
        record["canonical_key"] for record in cooking_evidence["items"].values()
    }
    first_aid_override_keys = {
        record["canonical_key"] for record in first_aid_evidence["items"].values()
    }
    catalog = config["catalog"]
    guides = config["guides"]
    collectible_override_keys = {
        key for key, item in catalog.items()
        if item.get("price_evidence_ref", "").startswith(
            "data/ah-collectible-price-evidence.json#items/"
        )
    }
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
    if len(non_enchanting_keys) != 2427:
        fail(f"Expected 2427 non-Enchanting recipe audits, found {len(non_enchanting_keys)}")
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
                not config["pricing_policy"]["preserve_unreviewed_market_prices"]
                and
                item.get("price_strategy")
                not in {"shared-market-reference", "evidence-pricing-market-value"}
                and int(item[f"{band}_copper"]) < int(floors[band])
            ):
                fail(f"{key}: {band} price falls below its audited craft floor")
        if item.get("price_strategy") == "shared-market-reference":
            note = item.get("row_note", "")
            if key.startswith("mining-"):
                if "canonical" not in note or "without a convenience markup" not in note:
                    fail(f"{key}: reversible Mining conversion must explain shared pricing")
            elif "below" not in note or "skip" not in note:
                fail(f"{key}: shared market pricing must explain the unprofitable craft route")
        elif item.get("price_strategy") == "evidence-pricing-market-value":
            if (
                not key.startswith("alch-")
                and key not in gathering_override_keys
                and key not in blacksmithing_override_keys
                and key not in engineering_override_keys
                and key not in jewelcrafting_gem_override_keys
                and key not in jewelcrafting_jewelry_override_keys
                and key not in inscription_override_keys
                and key not in tailoring_override_keys
                and key not in leatherworking_override_keys
                and key not in cooking_override_keys
                and key not in first_aid_override_keys
                and key not in collectible_override_keys
            ):
                fail(f"{key}: Evidence Pricing override is outside a reviewed scope")

    used_keys: list[str] = []
    sources: dict[str, str] = {}
    rendered_filename_by_key: dict[str, str] = {}
    for filename, guide in guides.items():
        page_configs = [
            page
            for page in manifest["guides"]
            if page.get("crafted_source", page["file"]) == filename
        ]
        if not page_configs:
            fail(f"{filename}: no active rendered view exists")

        expected_order: list[str] = []
        source_parts: list[str] = []
        crafted_parts: list[str] = []
        for page in page_configs:
            source_part = (ROOT / "guides" / page["file"]).read_text(encoding="utf-8")
            if source_part.count("<!-- AH_CRAFTED_SECTION_START -->") != 1:
                fail(f"{page['file']}: expected one generated crafted-market block")
            sections = guide["sections"]
            if page.get("crafted_sections"):
                included = set(page["crafted_sections"])
                sections = [section for section in sections if section["title"] in included]
            elif page.get("crafted_exclude_sections"):
                excluded = set(page["crafted_exclude_sections"])
                sections = [section for section in sections if section["title"] not in excluded]
            view_order = [key for section in sections for key in section["items"]]
            actual_view_order = re.findall(r'data-crafted-key="([^"]+)"', source_part)
            if len(actual_view_order) != len(view_order) or set(actual_view_order) != set(view_order):
                fail(f"{page['file']}: rendered rows do not match its canonical filtered view")
            for key in view_order:
                if key in rendered_filename_by_key:
                    fail(f"{key}: crafted output is duplicated across active guide views")
                rendered_filename_by_key[key] = page["file"]
            expected_order.extend(view_order)
            source_parts.append(source_part)
            crafted_parts.append(
                source_part.split("<!-- AH_CRAFTED_SECTION_START -->", 1)[1].split(
                    "<!-- AH_CRAFTED_SECTION_END -->", 1
                )[0]
            )

        source = "\n".join(source_parts)
        sources[filename] = source
        if len(expected_order) != EXPECTED_GUIDE_COUNTS[filename]:
            fail(
                f"{filename}: expected {EXPECTED_GUIDE_COUNTS[filename]} configured "
                f"outputs, found {len(expected_order)}"
            )
        actual_order = re.findall(r'data-crafted-key="([^"]+)"', source)
        if len(actual_order) != len(expected_order) or set(actual_order) != set(expected_order):
            fail(f"{filename}: rendered rows do not match canonical crafted membership")
        used_keys.extend(expected_order)

        shared_note = guide.get("shared_note")
        if not shared_note:
            fail(f"{filename}: every crafted guide needs one shared pricing note")
        crafted_source = "\n".join(crafted_parts)
        if source.count(f'id="{shared_note["id"]}"') != len(page_configs):
            fail(f"{filename}: shared pricing note must render once per active view")
        if crafted_source.count('class="crafted-note-ref"') != len(expected_order):
            fail(f"{filename}: every crafted row must reference the shared note")
        if crafted_source.count('class="crafted-item-note"') != len(expected_order):
            fail(f"{filename}: every crafted row must render an item-specific note")
        if crafted_source.count('class="crafted-recipe-link ') != len(expected_order):
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
                rf'data-market-source="crafted" data-profession="{profession}"'
                rf'(?: data-search-hint="[^"]+")?>'
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
                and entry["href"].startswith(
                    f"./guides/{rendered_filename_by_key[key]}#"
                )
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

    jewelcrafting_items = {
        merged_item(config, key)["name"]: merged_item(config, key)
        for key in used_keys
        if key.startswith("jc-")
    }
    if len(jewelcrafting_items) != 497:
        fail(f"Expected 497 distinct tradeable Jewelcrafting outputs, found {len(jewelcrafting_items)}")
    for label in (
        "Bold Dragon's Eye",
        "Figurine - Monarch Crab",
        "Rough Stone Statue",
        "Don Julio's Heart",
    ):
        if label in jewelcrafting_items:
            fail(f"BoP Jewelcrafting output leaked into the AH catalog: {label}")
    for label in (
        "Delicate Cardinal Ruby",
        "Chaotic Skyflare Diamond",
        "Bold Scarlet Ruby",
        "Delicate Bloodstone",
        "Bold Crimson Spinel",
        "Bold Living Ruby",
        "Bold Blood Garnet",
        "Titanium Impact Band",
        "Mercurial Adamantite",
        "Icy Prism",
        "Prismatic Black Diamond",
        "Thorium Setting",
    ):
        if label not in jewelcrafting_items:
            fail(f"Expanded Jewelcrafting era/category coverage is missing: {label}")
    jewelcrafting_sections = guides["jewelcrafting-gems-ah-price-guide.html"]["sections"]
    if len(jewelcrafting_sections) != 45:
        fail(f"Expected 45 expanded Jewelcrafting sections, found {len(jewelcrafting_sections)}")
    if any(int(item.get("required_skill", 0)) for item in jewelcrafting_items.values()):
        fail("Profession-restricted finished Jewelcrafting item leaked into general-use sections")

    tailoring_items = {
        merged_item(config, key)["name"]: merged_item(config, key)
        for key in used_keys
        if key.startswith("tailor-")
    }
    if len(tailoring_items) != 407:
        fail(f"Expected 407 distinct tradeable Tailoring outputs, found {len(tailoring_items)}")
    for label in (
        "Robe of the Archmage",
        "Sunfire Robe",
        "Magnificent Flying Carpet",
        "Frosty Flying Carpet",
    ):
        if label in tailoring_items:
            fail(f"BoP, self-only, or excluded Tailoring output leaked in: {label}")
    alliance_tailoring_ids = {47585, 47587, 47603, 47605}
    leaked_tailoring_alliance = alliance_tailoring_ids & {
        int(item["item_id"]) for item in tailoring_items.values()
    }
    if leaked_tailoring_alliance:
        fail(
            "Alliance-only duplicate Tailoring records leaked in: "
            f"{sorted(leaked_tailoring_alliance)}"
        )
    for label in (
        "Spellweave",
        "Frostweave Bag",
        "Brilliant Spellthread",
        "Frostweave Net",
        "Leggings of Woven Death",
        "Spellfire Robe",
        "Bottomless Bag",
        "Mooncloth",
        "Rich Purple Silk Shirt",
        "Gordok Ogre Suit",
    ):
        if label not in tailoring_items:
            fail(f"Expanded Tailoring era/category coverage is missing: {label}")
    tailoring_sections = guides["tailoring-cloth-ah-price-guide.html"]["sections"]
    if len(tailoring_sections) != 22:
        fail(f"Expected 22 Tailoring and First Aid sections, found {len(tailoring_sections)}")
    restricted_tailoring = [
        section
        for section in tailoring_sections
        if section.get("audience") == "profession-restricted"
    ]
    tailor_only_sections = [
        section
        for section in restricted_tailoring
        if section["items"][0].startswith("tailor-")
    ]
    tailor_only_memberships = {section["title"]: set(section["items"]) for section in tailor_only_sections}
    if tailor_only_memberships != {
        "Tailor-only crafted mount": {"tailor-flying-carpet"},
        "Tailor-only nets": {
            "tailor-netherweave-net",
            "tailor-heavy-netherweave-net",
            "tailor-frostweave-net",
        },
    }:
        fail("Tailor-only mount and nets are not isolated in dedicated restricted sections")

    first_aid_items = {key for key in used_keys if key.startswith("firstaid-")}
    if len(first_aid_items) != 17:
        fail(f"Expected 17 distinct tradeable First Aid outputs, found {len(first_aid_items)}")
    first_aid_names = {merged_item(config, key)["name"] for key in first_aid_items}
    for label in (
        "Heavy Frostweave Bandage",
        "Heavy Netherweave Bandage",
        "Heavy Runecloth Bandage",
        "Anti-Venom",
        "Strong Anti-Venom",
        "Powerful Anti-Venom",
    ):
        if label not in first_aid_names:
            fail(f"Complete First Aid coverage is missing: {label}")
    first_aid_sections = [
        section
        for section in tailoring_sections
        if section["items"][0].startswith("firstaid-")
    ]
    if len(first_aid_sections) != 4:
        fail(f"Expected four separate First Aid sections, found {len(first_aid_sections)}")
    restricted_first_aid = {
        key
        for section in first_aid_sections
        if section.get("audience") == "profession-restricted"
        for key in section["items"]
    }
    if len(restricted_first_aid) != 15:
        fail("The 15 skill-gated First Aid outputs are not isolated in restricted sections")
    general_first_aid = {
        key
        for section in first_aid_sections
        if section.get("audience") == "general-use"
        for key in section["items"]
    }
    if general_first_aid != {"firstaid-anti-venom", "firstaid-strong-anti-venom"}:
        fail("General-use anti-venoms are not separated from skill-gated First Aid items")

    leatherworking_items = {
        merged_item(config, key)["name"]: merged_item(config, key)
        for key in used_keys
        if key.startswith("lw-")
    }
    if len(leatherworking_items) != 490:
        fail(
            "Expected 490 distinct tradeable Leatherworking outputs, found "
            f"{len(leatherworking_items)}"
        )
    for label in (
        "Netherstrike Breastplate",
        "Carapace of Sun and Shadow",
        "Fur Lining - Attack Power",
        "Cobrahide Leg Reinforcements",
        "Gordok Ogre Suit",
    ):
        if label in leatherworking_items:
            fail(f"BoP, self-only, or duplicate Leatherworking output leaked in: {label}")
    alliance_leatherworking_ids = {47576, 47579, 47581, 47583, 47595, 47597, 47599, 47602}
    leaked_leatherworking_alliance = alliance_leatherworking_ids & {
        int(item["item_id"]) for item in leatherworking_items.values()
    }
    if leaked_leatherworking_alliance:
        fail(
            "Alliance-only duplicate Leatherworking records leaked in: "
            f"{sorted(leaked_leatherworking_alliance)}"
        )
    for label in (
        "Heavy Borean Leather",
        "Frosthide Leg Armor",
        "Drums of Battle",
        "Drums of Forgotten Kings",
        "Mammoth Mining Bag",
        "Nerubian Reinforced Quiver",
        "Belt of Dragons",
        "Earthgiving Legguards",
        "Onyxia Scale Cloak",
        "Riding Crop",
        "Heavy Leather Ball",
    ):
        if label not in leatherworking_items:
            fail(f"Expanded Leatherworking era/category coverage is missing: {label}")
    leatherworking_sections = guides[
        "skinning-leatherworking-materials-ah-price-guide.html"
    ]["sections"]
    if len(leatherworking_sections) != 29:
        fail(
            "Expected 29 expanded Leatherworking sections, found "
            f"{len(leatherworking_sections)}"
        )
    restricted_leatherworking = [
        section
        for section in leatherworking_sections
        if section.get("audience") == "profession-restricted"
    ]
    if len(restricted_leatherworking) != 1 or set(
        restricted_leatherworking[0]["items"]
    ) != {
        "lw-drums-of-war",
        "lw-drums-of-battle",
        "lw-drums-of-speed",
        "lw-drums-of-restoration",
        "lw-drums-of-panic",
    }:
        fail("Leatherworker-only drums are not isolated in one restricted section")
    profession_bag_keys = {
        key
        for section in leatherworking_sections
        if section.get("audience") == "profession-input"
        for key in section["items"]
    }
    if profession_bag_keys != {
        "lw-leatherworkers-satchel",
        "lw-bag-of-many-hides",
        "lw-trappers-traveling-pack",
        "lw-reinforced-mining-bag",
        "lw-mammoth-mining-bag",
        "lw-pack-of-endless-pockets",
    }:
        fail("Leatherworking profession-material bags are not fully isolated")

    cooking_keys = {
        key
        for key in used_keys
        if key.startswith("cook-")
    }
    if len(cooking_keys) != 162:
        fail(f"Expected 162 distinct tradeable Cooking outputs, found {len(cooking_keys)}")
    cooking_names = {merged_item(config, key)["name"] for key in cooking_keys}
    for label in ("Clamlette Magnifique", "Bread of the Dead"):
        if label in cooking_names:
            fail(f"Bind-on-pickup Cooking output leaked in: {label}")
    for label in (
        "Pumpkin Pie",
        "Spice Bread Stuffing",
        "Slow-Roasted Turkey",
        "Candied Sweet Potato",
        "Cranberry Chutney",
    ):
        if label in cooking_names:
            fail(f"Duration-limited Cooking output leaked in: {label}")
    for label in (
        "Fish Feast",
        "Great Feast",
        "Dragonfin Filet",
        "Delicious Chocolate Cake",
        "Savory Deviate Delight",
        "Thistle Tea",
        "Hot Apple Cider",
    ):
        if label not in cooking_names:
            fail(f"Expanded Cooking era/category coverage is missing: {label}")
    cooking_sections = guides["fishing-cooking-materials-ah-price-guide.html"]["sections"]
    if len(cooking_sections) != 13:
        fail(f"Expected 13 expanded Cooking sections, found {len(cooking_sections)}")
    restricted_cooking = [
        section for section in cooking_sections
        if section.get("audience") == "profession-restricted"
    ]
    if len(restricted_cooking) != 1 or set(restricted_cooking[0]["items"]) != {
        "cook-great-feast",
        "cook-fish-feast",
        "cook-gigantic-feast",
        "cook-small-feast",
    }:
        fail("Cook-required feasts are not isolated in one restricted section")
    class_restricted_cooking = [
        section for section in cooking_sections
        if section.get("audience") == "class-restricted"
    ]
    if len(class_restricted_cooking) != 1 or class_restricted_cooking[0]["items"] != [
        "cook-thistle-tea"
    ]:
        fail("Thistle Tea is not isolated in one Rogue-only section")

    mining_keys = {key for key in used_keys if key.startswith("mining-")}
    if len(mining_keys) != 24:
        fail(f"Expected 24 Mining-owned tradeable outputs, found {len(mining_keys)}")
    mining_names = {merged_item(config, key)["name"] for key in mining_keys}
    for label in (
        "Titansteel Bar",
        "Hardened Khorium",
        "Elementium Bar",
        "Mote of Fire",
        "Mote of Earth",
        "Bronze Bar",
    ):
        if label not in mining_names:
            fail(f"Expanded Mining smelting coverage is missing: {label}")
    for shared_label in ("Titanium Bar", "Enchanted Thorium Bar"):
        if shared_label in mining_names:
            fail(f"Shared cross-profession output was duplicated in Mining: {shared_label}")
    mining_sections = guides["mining-smithing-ah-price-guide.html"]["sections"]
    if len(mining_sections) != 4:
        fail(f"Expected 4 Mining crafted sections, found {len(mining_sections)}")
    mining_source = sources["mining-smithing-ah-price-guide.html"]
    for fragment in (
        "Related shared and non-Mining metal conversions",
        "spell=55211",
        "spell=70524",
        "Elementium Ore",
    ):
        if fragment not in mining_source:
            fail(f"Mining shared-output or input coverage is missing: {fragment}")
    leatherworking_source = sources[
        "skinning-leatherworking-materials-ah-price-guide.html"
    ]
    if leatherworking_source.count(
        'data-column="estimate" data-label="Estimated Value"'
    ) != 5:
        fail("Leatherworking conversion checks must show five estimated values")
    for estimate in (
        "6 Borean input ≈4g 20s",
        "10 Heavy Borean ≈65g; 1 Arctic Fur ≈40g",
        "5 Knothide input ≈2g 75s",
        "Borean ≈85s; Knothide ≈60s; Light ≈10s",
        "≈25s / 45s / 60s / 2g 30s / 8g",
    ):
        if estimate not in leatherworking_source:
            fail(f"Leatherworking conversion estimate is missing: {estimate}")

    expected_leatherworking_search_hints = {
        "Arctic Fur": "10 Heavy Borean ≈65g vs Arctic Fur ≈40g",
        "Borean Leather": "5 Borean Scraps ≈70s → target 85s",
        "Cured Heavy Hide": "Heavy Hide + Salt ≈51s 50c → target 60s",
        "Cured Light Hide": "Light Hide + Salt ≈20s 50c → target 25s",
        "Cured Medium Hide": "Medium Hide + Salt ≈35s 50c → target 45s",
        "Cured Rugged Hide": "Rugged Hide + Refined Salt ≈6g 75s → target 8g",
        "Cured Thick Hide": "Thick Hide + Salt ≈2g → target 2g 30s",
        "Heavy Borean Leather": "6 Borean ≈4g 20s → target 6g 50s",
        "Heavy Knothide Leather": "5 Knothide ≈2g 75s → target 3g 20s",
        "Knothide Leather": "5 Knothide Scraps ≈50s → target 60s",
        "Light Leather": "3 Ruined Scraps ≈6s → target 10s",
    }
    actual_leatherworking_search_hints = {
        item["name"]: item["conversionHint"]
        for item in index["items"]
        if "skinning-leatherworking-materials-ah-price-guide.html" in item["href"]
        and "conversionHint" in item
    }
    if actual_leatherworking_search_hints != expected_leatherworking_search_hints:
        fail("Leatherworking conversion estimates are not attached to canonical search items")
    if any("value check" in item["name"].casefold() for item in index["items"]):
        fail("Reference-only value-check rows must stay out of AH search")

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
    if len(alchemy_sections) != 21:
        fail(f"Expected 21 expanded Alchemy sections, found {len(alchemy_sections)}")

    representative_non_enchanting_prices = {
        "chaos-deck": 6_750_000,
        "eng-khorium-power-core": 202_500,
        "alch-flask-endless-rage": 600_000,
        "alch-flask-frost-wyrm": 530_000,
        "alch-cardinal-ruby": 847_500,
        "bs-eternal-belt-buckle": 422_500,
        "bs-puresteel-legplates": 76_900_000,
        "jc-delicate-cardinal-ruby": 1_900_000,
        "jc-chaotic-skyflare-diamond": 385_000,
        "jc-nightmare-tear": 1_300_000,
        "jc-titanium-impact-band": 6_550_000,
        "jc-prismatic-black-diamond": 12_000,
        "tailor-spellweave": 350_000,
        "tailor-frostweave-bag": 1_750_000,
        "tailor-brilliant-spellthread": 550_000,
        "tailor-leggings-of-woven-death": 60_850_000,
        "firstaid-heavy-frostweave-bandage": 11_000,
        "firstaid-strong-anti-venom": 6_100,
        "firstaid-powerful-anti-venom": 2_000,
        "lw-drums-of-battle": 175_000,
        "lw-drums-of-forgotten-kings": 1_300_000,
        "lw-frosthide-leg-armor": 1_950_000,
        "lw-mammoth-mining-bag": 850_000,
        "lw-heavy-borean-leather": 65_000,
        "lw-belt-of-dragons": 7_550_000,
        "lw-lightning-infused-leggings": 68_800_000,
        "cook-fish-feast": 122_500,
        "cook-dragonfin-filet": 57_000,
        "cook-delicious-chocolate-cake": 17_500,
        "cook-thistle-tea": 12_000,
        "mining-titansteel-bar": 840_000,
        "mining-hardened-adamantite-bar": 142_500,
        "mining-elementium-bar": 3_400_000,
    }
    for key, expected_target in representative_non_enchanting_prices.items():
        if int(merged_item(config, key)["target_copper"]) != expected_target:
            fail(f"{key}: audited target price changed unexpectedly")
    cardinal_cut = merged_item(config, "jc-delicate-cardinal-ruby")
    if int(cardinal_cut["pricing_floor_copper"]["target"]) != 847_500:
        fail("Cardinal Ruby cut does not preserve the uncut gem's saved target opportunity cost")
    for key in ("jc-prismatic-black-diamond", "jc-icy-prism", "jc-brilliant-glass"):
        recipe = recipe_audit["recipes"][key]
        if int(recipe["output_count"]) != 1:
            fail(f"{key}: random sealed craft must use one guaranteed finished output")
    for key in ("nobles-deck", "chaos-deck", "prisms-deck", "undeath-deck"):
        item = merged_item(config, key)
        if item.get("price_strategy") == "evidence-pricing-market-value":
            expected_ref = f"data/ah-inscription-price-evidence.json#items/{item['item_id']}"
            if item.get("price_evidence_ref") != expected_ref:
                fail(f"{key}: Evidence-priced deck reference is stale")

    representative_non_enchanting_notes = {
        "glyph-disease": "refreshes disease durations",
        "chaos-deck": "price it separately from Nobles",
        "eng-khorium-power-core": "used in high-end devices",
        "alch-flask-endless-rage": "Increases attack power by 180",
        "alch-cardinal-ruby": "Uncut red epic gem",
        "bs-eternal-belt-buckle": "one permanent socket",
        "bs-puresteel-legplates": "ICC-era raid gearing",
        "jc-delicate-cardinal-ruby": "+20 Agility",
        "jc-chaotic-skyflare-diamond": "Requires at least 2 blue gems",
        "jc-nightmare-tear": "+10 All Stats",
        "jc-titanium-impact-band": "item level 200",
        "jc-prismatic-black-diamond": "eventual gem is random",
        "tailor-spellweave": "assumes one guaranteed output",
        "tailor-frostweave-bag": "20-slot general bag",
        "tailor-brilliant-spellthread": "spell power by 50 and Spirit by 20",
        "tailor-frostweave-net": "Tailoring 350 to use",
        "tailor-rich-purple-silk-shirt": "appearance and roleplay collectors",
        "firstaid-heavy-frostweave-bandage": "Heals 5,800 damage over an 8 sec channel",
        "firstaid-strong-anti-venom": "Cures poisons up to level 35",
        "firstaid-powerful-anti-venom": "requires First Aid to use",
        "lw-drums-of-battle": "Cannot affect targets level 80 or higher",
        "lw-drums-of-forgotten-kings": "requires no profession to use",
        "lw-frosthide-leg-armor": "Stamina by 55 and Agility by 22",
        "lw-mammoth-mining-bag": "32 slots of Mining supplies only",
        "lw-nerubian-reinforced-quiver": "28 slots of arrows",
        "lw-belt-of-dragons": "physical-DPS use",
        "lw-riding-crop": "Does not work for players above level 70",
        "cook-fish-feast": "80 Attack Power, 46 Spell Power and 40 Stamina",
        "cook-thistle-tea": "Rogue only",
        "cook-hot-apple-cider": "20 Stamina and Spirit",
        "mining-titansteel-bar": "Standard 3.3.5 data shows no cooldown",
        "mining-hardened-adamantite-bar": "ten-bar opportunity cost",
        "mining-elementium-bar": "Thunderfury quest material",
    }
    for key, expected_fragment in representative_non_enchanting_notes.items():
        if expected_fragment not in merged_item(config, key)["row_note"]:
            fail(f"{key}: expected item-specific use or market context is missing")

    for filename in (
        "inscription-materials-ah-price-guide.html",
        "engineering-materials-ah-price-guide.html",
        "alchemy-materials-ah-price-guide.html",
        "blacksmithing-materials-ah-price-guide.html",
        "jewelcrafting-gems-ah-price-guide.html",
        "tailoring-cloth-ah-price-guide.html",
        "skinning-leatherworking-materials-ah-price-guide.html",
        "mining-smithing-ah-price-guide.html",
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
        "jewelcrafting-gems-ah-price-guide.html",
        "tailoring-cloth-ah-price-guide.html",
        "skinning-leatherworking-materials-ah-price-guide.html",
        "fishing-cooking-materials-ah-price-guide.html",
        "mining-smithing-ah-price-guide.html",
    ):
        expected_date = (
            "2026-08-14"
            if filename
            in {
                "fishing-cooking-materials-ah-price-guide.html",
                "mining-smithing-ah-price-guide.html",
            }
            else "2026-08-10"
        )
        if f"Updated {expected_date}" not in sources[filename]:
            fail(f"{filename}: crafted-price audit footer date is stale")
        if not re.search(
            r"exact 3\.3\.5 (?:recipe|reagent)",
            sources[filename],
            flags=re.IGNORECASE,
        ):
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
    if "Updated 2026-08-10" not in enchanting_source:
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
    if enchanting_source.count("<strong>* Evidence Pricing and craft diagnostics:</strong>") != 1:
        fail("Enchanting Evidence Pricing copy must appear exactly once")
    if "Exact 3.3.5 spell reagents plus the cheapest compatible vellum" not in enchanting_source:
        fail("Enchanting shared note must separate market value from exact craft diagnostics")
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
        if item.get("price_strategy") != "evidence-pricing-market-value":
            fail(f"{key}: finished Enchanting output is missing Evidence Pricing")
        expected_ref = (
            "data/ah-gathering-material-price-evidence.json#items/12655"
            if int(item["item_id"]) == 12655
            else f"data/ah-enchanting-price-evidence.json#items/{item['item_id']}"
        )
        if item.get("price_evidence_ref") != expected_ref:
            fail(f"{key}: finished Enchanting evidence reference is stale")
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
            5_000_000,
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
        "are valid for Inscription, Engineering, Alchemy, Enchanting, Blacksmithing, Jewelcrafting, Tailoring, Leatherworking, Cooking, and Mining."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
