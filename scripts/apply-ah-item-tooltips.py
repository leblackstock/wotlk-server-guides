#!/usr/bin/env python3
"""Generate exact WotLK item IDs for AH guide rows and install the shared loader."""

from __future__ import annotations

import argparse
import json
import re
import unicodedata
import urllib.request
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX_PATH = ROOT / "assets" / "ah-search-index.js"
SEARCH_PATH = ROOT / "assets" / "ah-search.js"
OUTPUT_PATH = ROOT / "assets" / "ah-item-ids.js"
ITEM_TEMPLATE_URL = (
    "https://raw.githubusercontent.com/azerothcore/azerothcore-wotlk/"
    "master/data/sql/base/db_world/item_template.sql"
)

LOADER_MARKER = "/* AH item tooltip loader */"
LOADER_BLOCK = r'''

  /* AH item tooltip loader */
  (function loadAhItemTooltips() {
    if (typeof document === "undefined" || document.querySelector("script[data-ah-item-tooltips]")) return;
    const current = document.currentScript || Array.from(document.scripts).find((script) => /\/ah-search\.js(?:\?|$)/.test(script.src));
    if (!current || !current.src) return;
    const tooltipScript = document.createElement("script");
    tooltipScript.src = new URL("ah-item-tooltips.js?v=20260722-ah-items-v1", current.src).href;
    tooltipScript.async = false;
    tooltipScript.dataset.ahItemTooltips = "true";
    document.head.appendChild(tooltipScript);
  }());
'''

# Auctionable/craftable item classes beat same-name quest or internal records.
CLASS_PRIORITY = {
    7: 0,   # Trade Goods
    9: 1,   # Recipes
    3: 2,   # Gems
    0: 3,   # Consumables
    16: 4,  # Glyphs
    6: 5,   # Projectiles
    5: 6,   # Reagents
    1: 7,   # Containers
    13: 8,  # Keys
    15: 9,  # Miscellaneous
    12: 10, # Quest items
}
ALLOWED_CLASSES = set(CLASS_PRIORITY)
MANUAL_OVERRIDES = {
    "arcane dust": 22445,
    # The Hellscream guides are Horde-first. The two Battered Hilts share a
    # display name; 50380 is the Horde quest starter.
    "battered hilt": 50380,
}

ITEM_ROW = re.compile(
    r"^\((\d+),(\d+),(\d+),-?\d+,'((?:\\.|[^'])*)',\d+,(\d+),",
    re.MULTILINE,
)
INDEX_PAYLOAD = re.compile(r"window\.AH_SEARCH_INDEX=(\{.*\});\s*$", re.DOTALL)


def normalize(value: str) -> str:
    value = unicodedata.normalize("NFKD", value)
    value = "".join(character for character in value if not unicodedata.combining(character))
    value = value.lower().replace("’", "").replace("'", "").replace("&", " and ")
    value = re.sub(r"[^a-z0-9]+", " ", value).strip()
    return re.sub(r"\s+", " ", value)


def unescape_mysql(value: str) -> str:
    return value.replace("\\'", "'")


def read_index() -> dict:
    source = INDEX_PATH.read_text(encoding="utf-8")
    match = INDEX_PAYLOAD.search(source)
    if not match:
        raise RuntimeError(f"Unexpected AH index wrapper in {INDEX_PATH.relative_to(ROOT)}")
    return json.loads(match.group(1))


def read_item_template(path: Path | None) -> str:
    if path:
        return path.read_text(encoding="utf-8", errors="replace")

    request = urllib.request.Request(
        ITEM_TEMPLATE_URL,
        headers={"User-Agent": "wotlk-server-guides-ah-tooltip-builder/1.0"},
    )
    with urllib.request.urlopen(request, timeout=120) as response:
        return response.read().decode("utf-8", errors="replace")


def build_candidates(sql: str) -> dict[str, list[tuple[int, int, int]]]:
    candidates: dict[str, list[tuple[int, int, int]]] = defaultdict(list)
    for match in ITEM_ROW.finditer(sql):
        item_id = int(match.group(1))
        item_class = int(match.group(2))
        subclass = int(match.group(3))
        if item_class not in ALLOWED_CLASSES:
            continue
        name = unescape_mysql(match.group(4))
        key = normalize(name)
        if key:
            candidates[key].append((item_id, item_class, subclass))
    return candidates


def choose_item_id(key: str, candidates: list[tuple[int, int, int]]) -> int:
    override = MANUAL_OVERRIDES.get(key)
    if override and any(item_id == override for item_id, _, _ in candidates):
        return override

    # Prefer the item class most likely to represent an AH listing. For true
    # same-class duplicates, use the later ID, which usually represents the
    # final/faction-specific 3.3.5 record rather than an earlier placeholder.
    return min(
        candidates,
        key=lambda row: (CLASS_PRIORITY.get(row[1], 99), -row[0]),
    )[0]


def build_payload(index: dict, candidates: dict[str, list[tuple[int, int, int]]]) -> tuple[dict[str, int], dict]:
    indexed_names = sorted({normalize(item.get("name", "")) for item in index.get("items", [])} - {""})
    resolved: dict[str, int] = {}
    unresolved: list[str] = []
    ambiguous = 0

    for key in indexed_names:
        matches = candidates.get(key, [])
        if not matches:
            unresolved.append(key)
            continue
        if len({item_id for item_id, _, _ in matches}) > 1:
            ambiguous += 1
        resolved[key] = choose_item_id(key, matches)

    meta = {
        "version": 1,
        "indexedNames": len(indexed_names),
        "resolvedNames": len(resolved),
        "unresolvedLabels": len(unresolved),
        "resolvedAmbiguousNames": ambiguous,
        "source": "AzerothCore WotLK item_template",
    }
    return resolved, meta


def render_output(mapping: dict[str, int], meta: dict) -> str:
    return (
        "/* Generated by scripts/apply-ah-item-tooltips.py. Do not edit directly. */\n"
        f"window.AH_ITEM_IDS={json.dumps(mapping, ensure_ascii=False, separators=(',', ':'), sort_keys=True)};\n"
        f"window.AH_ITEM_ID_META={json.dumps(meta, separators=(',', ':'), sort_keys=True)};\n"
    )


def render_search_with_loader() -> str:
    source = SEARCH_PATH.read_text(encoding="utf-8")
    if LOADER_MARKER in source:
        return source
    anchor = '  "use strict";'
    if anchor not in source:
        raise RuntimeError(f"Could not find insertion point in {SEARCH_PATH.relative_to(ROOT)}")
    return source.replace(anchor, anchor + LOADER_BLOCK, 1)


def write_or_check(path: Path, expected: str, check: bool) -> bool:
    current = path.read_text(encoding="utf-8") if path.exists() else None
    if current == expected:
        return False
    if check:
        raise RuntimeError(f"Generated file is stale: {path.relative_to(ROOT)}")
    path.write_text(expected, encoding="utf-8", newline="\n")
    return True


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--item-template", type=Path, help="Use a local AzerothCore item_template.sql dump")
    parser.add_argument("--check", action="store_true", help="Verify generated files without writing")
    args = parser.parse_args()

    index = read_index()
    sql = read_item_template(args.item_template)
    candidates = build_candidates(sql)
    mapping, meta = build_payload(index, candidates)

    changed = []
    if write_or_check(OUTPUT_PATH, render_output(mapping, meta), args.check):
        changed.append(str(OUTPUT_PATH.relative_to(ROOT)))
    if write_or_check(SEARCH_PATH, render_search_with_loader(), args.check):
        changed.append(str(SEARCH_PATH.relative_to(ROOT)))

    print(json.dumps(meta, indent=2))
    if changed:
        print("Updated: " + ", ".join(changed))
    else:
        print("AH tooltip assets are current.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
