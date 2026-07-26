#!/usr/bin/env python3
"""Correct AtlasLoot link directions and distinguish the Discord join action."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "addons.json"
HTML = ROOT / "guides" / "addons.html"
CATALOG_JS = ROOT / "assets" / "addon-catalog.js"
CATALOG_CSS = ROOT / "assets" / "addon-catalog.css"
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

catalog_js = CATALOG_JS.read_text(encoding="utf-8")
old_link = 'const link = make("a", "addon-download-link", source.cardLabel || source.label || `Open ${source.source} ↗`);'
new_link = 'const link = make("a", "addon-download-link addon-prerequisite-link", source.cardLabel || source.label || `Open ${source.source} ↗`);'
old_dialog_link = 'const link = make("a", "addon-download-link", source.label || `Open ${source.source} ↗`);'
new_dialog_link = 'const link = make("a", "addon-download-link addon-prerequisite-link", source.label || `Open ${source.source} ↗`);'
if catalog_js.count(old_link) != 1 or catalog_js.count(old_dialog_link) != 1:
    raise SystemExit("Unexpected prerequisite-link rendering state")
catalog_js = catalog_js.replace(old_link, new_link).replace(old_dialog_link, new_dialog_link)
CATALOG_JS.write_text(catalog_js, encoding="utf-8")

catalog_css = CATALOG_CSS.read_text(encoding="utf-8")
css_needle = '.addon-download-link { border: 1px solid var(--border-default); background: rgba(255,255,255,.035); color: var(--text-primary); }'
css_replacement = '\n'.join([
    css_needle,
    '.addon-prerequisite-link {',
    '  border-color: var(--section-addons-accent);',
    '  background: rgba(var(--section-addons-rgb), .08);',
    '  color: var(--section-addons-soft);',
    '}',
])
if css_needle not in catalog_css or ".addon-prerequisite-link" in catalog_css:
    raise SystemExit("Unexpected prerequisite-link CSS state")
CATALOG_CSS.write_text(catalog_css.replace(css_needle, css_replacement), encoding="utf-8")

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
    '    const atlasLootDrawer = desktop.locator("#addon-dialog-content");',
    '    const joinDiscord = atlasLootDrawer.locator(\'a.addon-prerequisite-link[href="https://discord.gg/pe69BfNZG5"]\');',
    '    const downloadPost = atlasLootDrawer.locator(\'a.addon-dialog-download[href="https://discord.com/channels/608456284643262504/1328533521983340574/1469088948956434493"]\');',
    '    const stockFallback = atlasLootDrawer.locator(\'a[href="https://warperia.com/addon-wotlk/atlasloot-enhanced/"]\');',
    '    assert.equal(await joinDiscord.count(), 1);',
    '    assert.equal(await downloadPost.count(), 1);',
    '    assert.equal(await stockFallback.count(), 1);',
    '    const joinBorder = await joinDiscord.evaluate((node) => getComputedStyle(node).borderColor);',
    '    const downloadBorder = await downloadPost.evaluate((node) => getComputedStyle(node).borderColor);',
    '    const fallbackBorder = await stockFallback.evaluate((node) => getComputedStyle(node).borderColor);',
    '    assert.equal(joinBorder, downloadBorder, "Join Discord outline should use the download-post blue");',
    '    assert.notEqual(joinBorder, fallbackBorder, "Join Discord should stand apart from the stock fallback");',
])
if needle not in browser or "Discord below" in browser:
    raise SystemExit("Unexpected AtlasLoot browser-test state")
BROWSER_TEST.write_text(browser.replace(needle, replacement), encoding="utf-8")
