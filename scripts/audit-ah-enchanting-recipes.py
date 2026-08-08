#!/usr/bin/env python3
"""Audit Enchanting outputs against exact WotLK 3.3.5 recipes and vellums."""

from __future__ import annotations

import argparse
import importlib.util
import json
import math
import re
import sys
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CRAFTED_PATH = ROOT / "data" / "ah-crafted-sections.json"
BASELINE_PATH = ROOT / "data" / "ah-price-baselines.json"
AUDIT_PATH = ROOT / "data" / "ah-enchanting-recipe-audit.json"
SHARED_AUDIT_PATH = ROOT / "scripts" / "audit-ah-crafted-prices.py"
GUIDE_FILENAME = "enchanting-mats-ah-price-guide.html"
PRICE_BANDS = ("quick", "target", "high")
SKILL_URLS = (
    "https://wotlkdb.com/?spells=11.333&filter=maxrs=300",
    "https://wotlkdb.com/?spells=11.333&filter=minrs=301;maxrs=350",
    "https://wotlkdb.com/?spells=11.333&filter=minrs=351;maxrs=450",
)

EXACT_VENDOR_INPUTS = {
    3371: ("Empty Vial", 20),
    3372: ("Leaded Vial", 200),
    4470: ("Simple Wood", 38),
    8925: ("Crystal Vial", 2_500),
    10648: ("Common Parchment", 125),
    11291: ("Star Wood", 4_500),
    17034: ("Maple Seed", 200),
    17035: ("Stranglethorn Seed", 400),
    18256: ("Imbued Vial", 20_000),
    39354: ("Light Parchment", 15),
    39501: ("Heavy Parchment", 1_250),
    39502: ("Resilient Parchment", 5_000),
}

VELLUM_RECIPES = {
    ("armor", 1): {
        "item_id": 38682,
        "name": "Armor Vellum",
        "source_spell_id": 52739,
        "output_count": 2,
        "reagents": ((39469, "Moonglow Ink", 1), (39354, "Light Parchment", 2)),
    },
    ("armor", 2): {
        "item_id": 37602,
        "name": "Armor Vellum II",
        "source_spell_id": 59499,
        "output_count": 2,
        "reagents": ((43120, "Celestial Ink", 1), (10648, "Common Parchment", 2)),
    },
    ("armor", 3): {
        "item_id": 43145,
        "name": "Armor Vellum III",
        "source_spell_id": 59500,
        "output_count": 2,
        "reagents": ((43126, "Ink of the Sea", 1), (39502, "Resilient Parchment", 2)),
    },
    ("weapon", 1): {
        "item_id": 39349,
        "name": "Weapon Vellum",
        "source_spell_id": 52840,
        "output_count": 2,
        "reagents": ((39774, "Midnight Ink", 3), (39354, "Light Parchment", 2)),
    },
    ("weapon", 2): {
        "item_id": 39350,
        "name": "Weapon Vellum II",
        "source_spell_id": 59488,
        "output_count": 2,
        "reagents": (
            (43121, "Fiery Ink", 1),
            (39501, "Heavy Parchment", 2),
            (43120, "Celestial Ink", 1),
        ),
    },
    ("weapon", 3): {
        "item_id": 43146,
        "name": "Weapon Vellum III",
        "source_spell_id": 59501,
        "output_count": 2,
        "reagents": ((43126, "Ink of the Sea", 3), (39502, "Resilient Parchment", 2)),
    },
}


spec = importlib.util.spec_from_file_location("ah_shared_recipe_audit", SHARED_AUDIT_PATH)
if spec is None or spec.loader is None:
    raise RuntimeError("Could not load the shared recipe-audit helpers")
shared = importlib.util.module_from_spec(spec)
spec.loader.exec_module(shared)


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def merged_item(config: dict, key: str) -> dict:
    raw = config["catalog"][key]
    return config["catalog_defaults"] | config["price_profiles"][raw["profile"]] | raw


def entries(config: dict) -> list[dict]:
    rows = []
    seen_keys: set[str] = set()
    seen_ids: set[int] = set()
    sections = config["guides"][GUIDE_FILENAME]["sections"]
    for section in sections:
        for key in section["items"]:
            if key in seen_keys:
                raise ValueError(f"Duplicate Enchanting key: {key}")
            seen_keys.add(key)
            item = merged_item(config, key)
            item_id = int(item["item_id"])
            if item_id in seen_ids:
                raise ValueError(f"Duplicate Enchanting output item ID: {item_id}")
            seen_ids.add(item_id)
            rows.append({"key": key, "section": section["title"], "item": item})
    if len(sections) != 25 or len(rows) != 276:
        raise ValueError(f"Enchanting inventory drifted: {len(rows)} rows in {len(sections)} sections")
    return rows


def scroll_kind(item: dict) -> str | None:
    if not item["name"].startswith("Scroll of Enchant "):
        return None
    return "weapon" if "weapon" in item["profile"] else "armor"


def reagent_record(item_id: int, name: str, count: int) -> dict:
    return {"item_id": int(item_id), "name": name, "count": int(count)}


def refresh_recipe_audit(config: dict) -> dict:
    names: dict[int, str] = {}
    spells: dict[int, dict] = {}
    for url in SKILL_URLS:
        source = shared.fetch_text(url)
        names.update(shared.wotlkdb_item_names(source))
        spells.update(
            {int(spell["id"]): spell for spell in shared.listview_data(source, "spells")}
        )
    if len(spells) != 306:
        raise ValueError(f"Expected 306 complete Enchanting spell records; got {len(spells)}")

    recipes = {}
    for row in entries(config):
        key = row["key"]
        item = row["item"]
        spell_id = int(item["source_spell_id"])
        spell = spells.get(spell_id)
        if not spell:
            raise ValueError(f"Missing Enchanting spell {spell_id} for {key}")
        kind = scroll_kind(item)
        creates = spell.get("creates")
        if kind:
            output_count = 1
            vellum_rank = int(item["vellum_rank"])
            vellum = VELLUM_RECIPES[(kind, vellum_rank)]
        else:
            if not creates or int(creates[0]) != int(item["item_id"]):
                raise ValueError(f"{key}: recipe output does not match canonical item")
            # WotLKDB reports zero for several valid Enchanting item crafts even
            # though the spell deterministically creates one finished item.
            output_count = int(creates[1]) or 1
            vellum_rank = None
            vellum = None
        reagents = []
        for item_id, count in spell.get("reagents", []):
            item_id = int(item_id)
            if item_id not in names:
                raise ValueError(f"{key}: missing reagent name for item {item_id}")
            reagents.append(reagent_record(item_id, names[item_id], count))
        recipes[key] = {
            "source_spell_id": spell_id,
            "source_spell_name": shared.clean_spell_name(spell["name"]),
            "output_item_id": int(item["item_id"]),
            "output_count": output_count,
            "pricing_rule": "enchant-scroll-plus-vellum" if kind else "direct",
            "reagents": reagents,
            **(
                {
                    "vellum": {
                        "kind": kind,
                        "rank": vellum_rank,
                        "item_id": int(vellum["item_id"]),
                        "name": vellum["name"],
                        "source_spell_id": int(vellum["source_spell_id"]),
                    }
                }
                if vellum
                else {}
            ),
        }
    return {
        "version": 1,
        "refreshed": date.today().isoformat(),
        "scope": "All 276 tradeable finished Enchanting outputs in the canonical AH guide",
        "recipe_source": {
            "name": "WotLKDB Enchanting skill 333",
            "urls": list(SKILL_URLS),
            "records": len(spells),
            "role": "Exact WotLK 3.3.5 spell IDs, reagents, output item IDs, and minimum guaranteed output counts.",
        },
        "pricing_policy": {
            "active_hellscream_listings_used": False,
            "baseline_role": "Frozen non-circular ingredient bands or exact unlimited-vendor prices.",
            "crafted_input_role": "Saved Evidence Pricing bands are the opportunity cost for tradeable crafted inputs consumed by an enchant recipe.",
            "vellum_role": "Each scroll adds one exact cheapest compatible vellum, priced from that vellum's own deterministic two-output Inscription recipe.",
            "floor_role": "Recipe floors are craftability diagnostics and do not set finished-output sale value.",
        },
        "exact_vendor_inputs": {
            str(item_id): {"name": name, "unit_copper": price}
            for item_id, (name, price) in EXACT_VENDOR_INPUTS.items()
        },
        "vellum_recipes": {
            f"{kind}-{rank}": {
                "kind": kind,
                "rank": rank,
                "item_id": int(record["item_id"]),
                "name": record["name"],
                "source_spell_id": int(record["source_spell_id"]),
                "output_count": int(record["output_count"]),
                "reagents": [reagent_record(*reagent) for reagent in record["reagents"]],
            }
            for (kind, rank), record in VELLUM_RECIPES.items()
        },
        "recipes": recipes,
    }


def input_references(config: dict, audit: dict) -> dict[int, dict[str, int]]:
    baseline = shared.baseline_reagent_references()
    references = dict(baseline)
    for item_id, record in audit["exact_vendor_inputs"].items():
        value = int(record["unit_copper"])
        references[int(item_id)] = {band: value for band in PRICE_BANDS}
    for key, raw in config["catalog"].items():
        item = merged_item(config, key)
        values = {band: int(item[f"{band}_copper"]) for band in PRICE_BANDS}
        if not all(value > 0 for value in values.values()):
            continue
        references.setdefault(
            int(item["item_id"]),
            values,
        )
    return references


def calculate_floors(config: dict, audit: dict) -> tuple[dict[str, dict[str, int]], dict[str, dict[str, int]]]:
    references = input_references(config, audit)

    def recipe_cost(reagents: list[dict], output_count: int, band: str) -> int:
        total = 0
        for reagent in reagents:
            item_id = int(reagent["item_id"])
            if item_id not in references:
                raise ValueError(f"No {band} Enchanting input reference for item {item_id}")
            total += references[item_id][band] * int(reagent["count"])
        return math.ceil(total / int(output_count))

    vellum_costs = {
        key: {
            band: recipe_cost(record["reagents"], int(record["output_count"]), band)
            for band in PRICE_BANDS
        }
        for key, record in audit["vellum_recipes"].items()
    }
    floors = {}
    for key, recipe in audit["recipes"].items():
        costs = {
            band: recipe_cost(recipe["reagents"], int(recipe["output_count"]), band)
            for band in PRICE_BANDS
        }
        if recipe["pricing_rule"] == "enchant-scroll-plus-vellum":
            vellum_key = f"{recipe['vellum']['kind']}-{recipe['vellum']['rank']}"
            costs = {
                band: costs[band] + vellum_costs[vellum_key][band]
                for band in PRICE_BANDS
            }
        floors[key] = costs
    return floors, vellum_costs


def compact_catalog_object(record: dict) -> str:
    return json.dumps(record, ensure_ascii=False, separators=(",", ":"))


def apply_floors(config: dict, floors: dict[str, dict[str, int]]) -> None:
    source = CRAFTED_PATH.read_text(encoding="utf-8")
    for key, floor in floors.items():
        updated = dict(config["catalog"][key])
        updated["pricing_floor_copper"] = {band: int(floor[band]) for band in PRICE_BANDS}
        pattern = re.compile(rf'^(    "{re.escape(key)}": )\{{.*\}}(,?)$', re.MULTILINE)
        replacement = rf"\g<1>{compact_catalog_object(updated)}\g<2>"
        source, count = pattern.subn(replacement, source, count=1)
        if count != 1:
            raise ValueError(f"Could not update Enchanting recipe floor for {key}")
    CRAFTED_PATH.write_text(source, encoding="utf-8", newline="\n")


def validate(config: dict, audit: dict, *, require_applied: bool) -> dict:
    rows = entries(config)
    keys = {row["key"] for row in rows}
    if set(audit.get("recipes", {})) != keys:
        raise ValueError("Enchanting recipe snapshot does not cover all canonical outputs")
    if audit.get("pricing_policy", {}).get("active_hellscream_listings_used") is not False:
        raise ValueError("Active Hellscream listings must not set recipe inputs")
    floors, vellum_costs = calculate_floors(config, audit)
    scrolls = 0
    non_scrolls = 0
    for row in rows:
        key = row["key"]
        item = row["item"]
        recipe = audit["recipes"][key]
        if int(recipe["source_spell_id"]) != int(item["source_spell_id"]):
            raise ValueError(f"{key}: source spell drifted")
        if int(recipe["output_item_id"]) != int(item["item_id"]):
            raise ValueError(f"{key}: output item drifted")
        if recipe["pricing_rule"] == "enchant-scroll-plus-vellum":
            scrolls += 1
            if int(recipe["vellum"]["rank"]) != int(item["vellum_rank"]):
                raise ValueError(f"{key}: vellum rank drifted")
        else:
            non_scrolls += 1
        if require_applied:
            current = {band: int(item["pricing_floor_copper"][band]) for band in PRICE_BANDS}
            if current != floors[key]:
                raise ValueError(f"{key}: exact recipe floor is stale")
    if scrolls != 259 or non_scrolls != 17:
        raise ValueError(f"Enchanting type counts drifted: {scrolls} scrolls, {non_scrolls} other")
    return {"items": len(rows), "scrolls": scrolls, "other": non_scrolls, "vellum_costs": vellum_costs}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--refresh-recipes", action="store_true")
    group.add_argument("--apply-floors", action="store_true")
    group.add_argument("--check", action="store_true")
    parser.add_argument("--write", action="store_true", help="Write a refreshed recipe snapshot")
    args = parser.parse_args()

    config = load(CRAFTED_PATH)
    if args.refresh_recipes:
        audit = refresh_recipe_audit(config)
        summary = validate(config, audit, require_applied=False)
        if args.write:
            AUDIT_PATH.write_text(
                json.dumps(audit, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
                newline="\n",
            )
        print(json.dumps(summary, ensure_ascii=False, indent=2))
        return 0
    if not AUDIT_PATH.exists():
        print("Enchanting recipe snapshot is missing; refresh it first.", file=sys.stderr)
        return 1
    audit = load(AUDIT_PATH)
    if args.apply_floors:
        floors, _ = calculate_floors(config, audit)
        apply_floors(config, floors)
        config = load(CRAFTED_PATH)
        summary = validate(config, audit, require_applied=True)
        print(f"Applied {summary['items']} exact Enchanting recipe floors.")
        return 0
    summary = validate(config, audit, require_applied=True)
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
