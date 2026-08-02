#!/usr/bin/env python3
"""Validate dropped-scroll prices, search rows, tooltips, and Inscription anchors."""

from __future__ import annotations

import json
import re
import subprocess
import sys
import unicodedata
from html.parser import HTMLParser
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "data" / "ah-dropped-scrolls.json"
GUIDE_PATH = ROOT / "guides" / "inscription-materials-ah-price-guide.html"
INDEX_PATH = ROOT / "assets" / "ah-search-index.js"
ITEM_IDS_PATH = ROOT / "assets" / "ah-item-ids.js"


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


class AnchorParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.ids: set[str] = set()
        self.jump_targets: list[str] = []
        self.category_headings = 0
        self.back_to_top_targets: list[str] = []
        self.in_jump_nav = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = {key: value or "" for key, value in attrs}
        if values.get("id"):
            self.ids.add(values["id"])
        if tag == "nav" and "ah-jump-nav" in values.get("class", "").split():
            self.in_jump_nav = True
        if tag == "h2" and "ah-category-heading" in values.get("class", "").split():
            self.category_headings += 1
        if tag == "a" and self.in_jump_nav and values.get("href", "").startswith("#"):
            self.jump_targets.append(values["href"][1:])
        if tag == "a" and "ah-back-to-top" in values.get("class", "").split():
            self.back_to_top_targets.append(values.get("href", ""))

    def handle_endtag(self, tag: str) -> None:
        if tag == "nav" and self.in_jump_nav:
            self.in_jump_nav = False


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

    config = json.loads(DATA_PATH.read_text(encoding="utf-8"))
    catalog = config["catalog"]
    rank_profiles = config["rank_profiles"]
    stat_profiles = config["stat_profiles"]
    defaults = config["catalog_defaults"]
    guide = config["guides"][GUIDE_PATH.name]
    shared_note = guide.get("shared_note")
    source = GUIDE_PATH.read_text(encoding="utf-8")
    index = generated_json(INDEX_PATH, "AH_SEARCH_INDEX")
    item_ids = generated_json(ITEM_IDS_PATH, "AH_ITEM_IDS")

    if len(catalog) != 42:
        fail(f"Expected six droppable scrolls for each of seven ranks, found {len(catalog)}")
    for rank in range(1, 8):
        rank_items = [item for item in catalog.values() if int(item["rank"]) == rank]
        if len(rank_items) != 6:
            fail(f"Rank {rank}: expected six scroll types, found {len(rank_items)}")
    if "Scroll of Protection VIII" in source:
        fail("Scroll of Protection VIII has no 3.3.5 loot source and must remain excluded")
    if not shared_note:
        fail("Dropped-scroll rows need one shared source and pricing note")
    if source.count(f'id="{shared_note["id"]}"') != 1:
        fail("Dropped-scroll shared source and pricing note must render exactly once")
    if source.count('class="dropped-scroll-note-ref"') != len(catalog):
        fail("Every dropped-scroll row must reference the shared note")
    if source.count('class="dropped-scroll-item-note"') != len(catalog):
        fail("Every dropped-scroll row must retain its item-specific selling note")
    repeated_source = (
        "Lower-level world drops, lockboxes, and reward containers."
    )
    if repeated_source in source:
        fail("Repeated row-level dropped-scroll source boilerplate remains")

    for key, raw_item in catalog.items():
        item = (
            defaults
            | rank_profiles[str(raw_item["rank"])]
            | stat_profiles[raw_item["stat"]]
            | raw_item
        )
        quick = int(item["quick_copper"])
        target = int(item["target_copper"])
        high = int(item["high_copper"])
        if not 0 < quick <= target <= high:
            fail(f"{key}: expected positive quick <= target <= high prices")
        row_match = re.search(
            rf'<tr data-dropped-scroll-key="{re.escape(key)}" '
            rf'data-market-source="drop">(.*?)</tr>',
            source,
            re.DOTALL,
        )
        if not row_match:
            fail(f"{key}: missing searchable dropped-scroll row")
        row = row_match.group(1)
        if f'<span class="buyout">{format_money(target)}</span>' not in row:
            fail(f"{key}: rendered target price is incorrect")
        note_reference = (
            f'class="dropped-scroll-note-ref" href="#{shared_note["id"]}" '
            f'aria-label="See {shared_note["label"]} note">'
            f'{shared_note["marker"]}</a>'
        )
        if note_reference not in row:
            fail(f"{key}: row is missing its shared source-note reference")
        if f'<span class="dropped-scroll-item-note">{item["notes"]}</span>' not in row:
            fail(f"{key}: item-specific selling note is missing or incorrect")

        matches = [
            entry
            for entry in index["items"]
            if entry["name"] == item["name"]
            and entry["href"].startswith(
                "./guides/inscription-materials-ah-price-guide.html#"
            )
            and entry["marketSource"] == "drop"
        ]
        if len(matches) != 1 or matches[0]["target"] != format_money(target):
            fail(f"{key}: expected one exact dropped-scroll search result")
        if item_ids.get(normalized_item_name(item["name"])) != int(item["item_id"]):
            fail(f"{key}: tooltip item ID is missing or incorrect")

    rank_eight_names = (
        "Scroll of Agility VIII",
        "Scroll of Intellect VIII",
        "Scroll of Spirit VIII",
        "Scroll of Stamina VIII",
        "Scroll of Strength VIII",
    )
    for name in rank_eight_names:
        if source.count(f">{name}</strong>") != 1:
            fail(f"{name}: expected one existing crafted/drop-identical Rank VIII row")

    anchors = AnchorParser()
    anchors.feed(source)
    if len(anchors.jump_targets) != 25:
        fail(f"Expected 25 category jump links, found {len(anchors.jump_targets)}")
    missing_targets = [target for target in anchors.jump_targets if target not in anchors.ids]
    if missing_targets:
        fail(f"Jump links target missing categories: {', '.join(missing_targets)}")
    if anchors.category_headings != 25 or anchors.back_to_top_targets != ["#top"] * 25:
        fail("Every category heading must have one right-aligned Back to top control")
    if "top" not in anchors.ids:
        fail("Back to top controls need a real #top destination")

    inscription_sections = {
        entry["section"]
        for entry in index["items"]
        if entry["href"].startswith("./guides/inscription-materials-ah-price-guide.html#")
    }
    if any("Top" in section for section in inscription_sections):
        fail("Back to top control text leaked into AH search section names")

    print("Dropped-scroll catalog, prices, search rows, tooltips, and jump links are valid.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
