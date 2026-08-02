#!/usr/bin/env python3
"""Guard AH item identity, duplicate pricing, rarity, notes, and tooltips."""

from __future__ import annotations

import html
import json
import re
import unicodedata
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
INDEX_PATH = ROOT / "assets" / "ah-search-index.js"
ITEM_IDS_PATH = ROOT / "assets" / "ah-item-ids.js"

INTENTIONAL_AGGREGATE_LABELS = {
    "Aldor premium drop",
    "Ashenvale Shredder Manual pages",
    "Blackrock / Core drops",
    "Budget uncommon cuts",
    "Cenarion Expedition armaments",
    "Cenarion Expedition plant drops",
    "Darkmoon Tier 1 animal parts",
    "Darkmoon Tier 2 animal parts",
    "Darkmoon Tier 3 animal parts",
    "Darkmoon Tier 4 animal parts",
    "Darkmoon Tier 5 animal parts",
    "Green Hills of Stranglethorn pages",
    "Hakkari Bijous",
    "High-demand epic blue cuts",
    "High-demand epic orange cuts",
    "High-demand epic red cuts",
    "High-demand epic yellow cuts",
    "High-demand rare cuts",
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

    forbidden_names = {"Firethorn", "Saronite Skeleton Key", "Toughened Flesh"}
    leaked = forbidden_names & grouped.keys()
    if leaked:
        fail(f"Invalid or post-Wrath item labels remain: {', '.join(sorted(leaked))}")

    required_ids = {
        "Fire Leaf": 39970,
        "Titanium Skeleton Key": 43853,
        "Design: Etched Monarch Topaz": 41777,
        "Design: Glinting Monarch Topaz": 41582,
        "Design: Shining Forest Emerald": 41782,
    }
    for name, item_id in required_ids.items():
        if name not in grouped:
            fail(f"Corrected 3.3.5 item is missing from search: {name}")
        if item_ids.get(normalized_item_name(name)) != item_id:
            fail(f"{name}: expected tooltip item ID {item_id}")

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
    for path in sorted((ROOT / "guides").glob("*-ah-price-guide.html")):
        source = path.read_text(encoding="utf-8")
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
