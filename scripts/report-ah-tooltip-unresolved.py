#!/usr/bin/env python3
"""List AH index labels that do not resolve to one exact WotLK item ID."""

from __future__ import annotations

import json
import re
import unicodedata
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX_PATH = ROOT / "assets" / "ah-search-index.js"
MAP_PATH = ROOT / "assets" / "ah-item-ids.js"
INDEX_PAYLOAD = re.compile(r"window\.AH_SEARCH_INDEX=(\{.*\});\s*$", re.DOTALL)
MAP_PAYLOAD = re.compile(r"window\.AH_ITEM_IDS=(\{.*?\});", re.DOTALL)


def normalize(value: str) -> str:
    value = unicodedata.normalize("NFKD", value)
    value = "".join(character for character in value if not unicodedata.combining(character))
    value = value.lower().replace("’", "").replace("'", "").replace("&", " and ")
    value = re.sub(r"[^a-z0-9]+", " ", value).strip()
    return re.sub(r"\s+", " ", value)


def parse(path: Path, pattern: re.Pattern[str]) -> dict:
    match = pattern.search(path.read_text(encoding="utf-8"))
    if not match:
        raise RuntimeError(f"Unexpected generated wrapper in {path.relative_to(ROOT)}")
    return json.loads(match.group(1))


def main() -> int:
    index = parse(INDEX_PATH, INDEX_PAYLOAD)
    item_ids = parse(MAP_PATH, MAP_PAYLOAD)
    unresolved: dict[str, list[dict]] = defaultdict(list)

    for item in index.get("items", []):
        key = normalize(item.get("name", ""))
        if key and key not in item_ids:
            unresolved[key].append(item)

    print(f"Unresolved unique labels: {len(unresolved)}")
    print()
    for key in sorted(unresolved):
        entries = unresolved[key]
        name = entries[0].get("name", key)
        guides = ", ".join(sorted({entry.get("guide", "") for entry in entries if entry.get("guide")}))
        details = "; ".join(sorted({entry.get("detail", "") for entry in entries if entry.get("detail")}))
        print(f"- {name} | guides: {guides or '—'} | detail: {details or '—'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
