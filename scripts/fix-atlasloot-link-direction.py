#!/usr/bin/env python3
"""Correct AtlasLoot setup directions now that Discord links appear above the text."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "addons.json"
HTML = ROOT / "guides" / "addons.html"
SEARCH_TEST = ROOT / "tests" / "addon-search.test.js"
BROWSER_TEST = ROOT / "tests" / "addon-browser-smoke.cjs"

OLD = "Not in the Hellscream Discord yet? Use Join the Hellscream Discord below, complete any required screening, then open the AtlasLoot download post and download AtlasLoot.7z."
NEW = "Not in the Hellscream Discord yet? Use the Join the Hellscream Discord button above, complete any required screening, then return and open the AtlasLoot download post."

payload = json.loads(DATA.read_text(encoding="utf-8"))
atlas = next(addon for addon in payload["addons"] if addon["id"] == "atlasloot-hellscream")
if atlas["generalSetup"][0] != OLD:
    raise SystemExit(f"Unexpected AtlasLoot setup sentence: {atlas['generalSetup'][0]!r}")
atlas["generalSetup"][0] = NEW
DATA.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

html = HTML.read_text(encoding="utf-8")
old_cache = "20260726-atlasloot-discord-v1"
new_cache = "20260726-atlasloot-discord-v2"
if old_cache not in html:
    raise SystemExit("Expected AtlasLoot Discord cache key was not found")
HTML.write_text(html.replace(old_cache, new_cache), encoding="utf-8")

search = SEARCH_TEST.read_text(encoding="utf-8")
needle = 'assert.match(atlasLoot.generalSetup[0], /Join the Hellscream Discord/);'
replacement = '\n'.join([
    needle,
    'assert.match(atlasLoot.generalSetup[0], /button above/);',
    'assert.doesNotMatch(atlasLoot.generalSetup[0], /below/);',
])
if needle not in search or "button above" in search:
    raise SystemExit("Unexpected AtlasLoot search-test state")
SEARCH_TEST.write_text(search.replace(needle, replacement), encoding="utf-8")

browser = BROWSER_TEST.read_text(encoding="utf-8")
needle = '    assert.match(atlasLootText, /Join the Hellscream Discord/);'
replacement = '\n'.join([
    needle,
    '    assert.match(atlasLootText, /button above/);',
    '    assert.doesNotMatch(atlasLootText, /Discord below/);',
])
if needle not in browser or "Discord below" in browser:
    raise SystemExit("Unexpected AtlasLoot browser-test state")
BROWSER_TEST.write_text(browser.replace(needle, replacement), encoding="utf-8")
