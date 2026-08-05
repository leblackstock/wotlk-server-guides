#!/usr/bin/env python3
"""Guard AH item identity, duplicate pricing, rarity, notes, and tooltips."""

from __future__ import annotations

import html
import json
import re
import sys
import unicodedata
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
INDEX_PATH = ROOT / "assets" / "ah-search-index.js"
ITEM_IDS_PATH = ROOT / "assets" / "ah-item-ids.js"
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from ah_guides import active_guide_paths  # noqa: E402

INTENTIONAL_AGGREGATE_LABELS = {
    "Aldor premium drop",
    "Ashenvale Shredder Manual pages",
    "Blackrock / Core drops",
    "Cenarion Expedition armaments",
    "Cenarion Expedition plant drops",
    "Darkmoon Tier 1 animal parts",
    "Darkmoon Tier 2 animal parts",
    "Darkmoon Tier 3 animal parts",
    "Darkmoon Tier 4 animal parts",
    "Darkmoon Tier 5 animal parts",
    "Green Hills of Stranglethorn pages",
    "Hakkari Bijous",
    "High-tier marks/signets",
    "Low-tier marks/signets",
    "Lower City feather drops",
    "Other Argent Dawn parts",
    "Scryer premium drop",
    "Timbermaw repeatable drops",
    "ZG coin sets",
}


def fail(message: str) -> None:
    raise AssertionError(message)


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
    value = value.casefold().replace("'", "").replace(chr(0x2019), "")
    value = value.replace("&", " and ")
    return " ".join(re.sub(r"[^a-z0-9]+", " ", value).split())


def main() -> int:
    index = generated_json(INDEX_PATH, "AH_SEARCH_INDEX")
    item_ids = generated_json(ITEM_IDS_PATH, "AH_ITEM_IDS")
    grouped: dict[str, list[dict]] = defaultdict(list)
    for entry in index["items"]:
        grouped[entry["name"]].append(entry)

    for name, entries in grouped.items():
        priced = [entry for entry in entries if re.search(r"\d", entry["target"])]
        targets = {entry["target"] for entry in priced}
        if len(targets) > 1:
            fail(f"{name}: duplicate AH rows disagree on target price: {sorted(targets)}")
        qualities = {entry["quality"] for entry in entries}
        if len(entries) > 1 and len(qualities) > 1:
            fail(f"{name}: duplicate AH rows disagree on rarity: {sorted(qualities)}")

    forbidden_names = {
        "Basilisk Meat",
        "Firethorn",
        "Saronite Skeleton Key",
        "Toughened Flesh",
    }
    leaked = forbidden_names & grouped.keys()
    if leaked:
        fail(f"Invalid or post-Wrath item labels remain: {', '.join(sorted(leaked))}")

    required_ids = {
        "Chunk o' Basilisk": 27677,
        "Fire Leaf": 39970,
        "Titanium Skeleton Key": 43853,
        "Design: Etched Monarch Topaz": 41777,
        "Design: Shining Forest Emerald": 41782,
    }
    for name, item_id in required_ids.items():
        if name not in grouped:
            fail(f"Corrected 3.3.5 item is missing from search: {name}")
        if item_ids.get(normalized_item_name(name)) != item_id:
            fail(f"{name}: expected tooltip item ID {item_id}")

    verified_qualities = {
        "Arctic Fur": "rare",
        "Black Lotus": "uncommon",
        "Dark Herring": "uncommon",
        "Fel Lotus": "uncommon",
        "Frost Lotus": "uncommon",
        "Hot Spices": "poor",
        "Siren's Tear": "rare",
        "Soothing Spices": "poor",
    }
    for name, quality in verified_qualities.items():
        if not grouped.get(name):
            fail(f"Verified rarity item is missing: {name}")
        actual = {entry["quality"] for entry in grouped[name]}
        if actual != {quality}:
            fail(f"{name}: expected {quality} rarity, found {sorted(actual)}")

    verified_max_stacks = {
        "Bear Flank": 20,
        "Crystallized Shadow": 10,
        "Crystallized Water": 10,
        "Green Whelp Scale": 5,
        "Okra": 10,
    }
    for name, max_stack in verified_max_stacks.items():
        for entry in grouped.get(name, []):
            counts = [int(part.strip()) for part in entry["stack"].split("/")]
            if any(count > max_stack for count in counts):
                fail(f"{name}: stack recommendation exceeds {max_stack}: {entry['stack']}")

    unresolved = {
        entry["name"]
        for entry in index["items"]
        if normalized_item_name(entry["name"]) not in item_ids
    }
    if unresolved != INTENTIONAL_AGGREGATE_LABELS:
        missing = sorted(INTENTIONAL_AGGREGATE_LABELS - unresolved)
        unexpected = sorted(unresolved - INTENTIONAL_AGGREGATE_LABELS)
        fail(
            "Tooltip resolution drifted; "
            f"missing intentional labels={missing}, unexpected unresolved items={unexpected}"
        )

    short_notes: list[str] = []
    forbidden_copy = (
        "Enchanting rod blank. Singles only.",
        "TBC leveling gem.",
        "Lower-level world drops, lockboxes, and reward containers.",
    )
    for path in active_guide_paths(guides_dir=ROOT / "guides"):
        source = path.read_text(encoding="utf-8")
        stale_labels = [
            name
            for name in forbidden_names
            if f">{name}</strong>" in source
        ]
        stale_labels.extend(
            name
            for name in (
                "Design: Etched Twilight Opal",
                "Design: Glinting Twilight Opal",
                "Design: Lightning Forest Emerald",
            )
            if name in source
        )
        if stale_labels:
            fail(f"{path.name}: stale item labels remain: {', '.join(stale_labels)}")
        for phrase in forbidden_copy:
            if phrase in source:
                fail(f"{path.name}: repeated or vague AH note remains: {phrase}")
        for match in re.finditer(
            r'<tr[^>]*>.*?<td data-column="notes"[^>]*>(.*?)</td></tr>',
            source,
            re.DOTALL,
        ):
            note = html.unescape(re.sub(r"<[^>]+>", " ", match.group(1)))
            note = " ".join(note.split())
            if note and len(note) < 25:
                short_notes.append(f"{path.name}: {note}")
    if short_notes:
        fail("Vague short AH notes remain:\n" + "\n".join(short_notes))

    print("AH duplicate prices, rarities, identities, notes, and tooltip mappings are consistent.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
