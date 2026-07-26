#!/usr/bin/env python3
"""Add the Hellscream-specific AtlasLoot package to the addon catalog."""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "addons.json"
HTML = ROOT / "guides" / "addons.html"
CATALOG_JS = ROOT / "assets" / "addon-catalog.js"
VALIDATOR = ROOT / "scripts" / "validate-addon-catalog.py"
SEARCH_TEST = ROOT / "tests" / "addon-search.test.js"
BROWSER_TEST = ROOT / "tests" / "addon-browser-smoke.cjs"
ICON = ROOT / "assets" / "addons" / "icons" / "atlasloot-hellscream.svg"

DISCORD_URL = "https://discord.com/channels/608456284643262504/1328533521983340574/1469088948956434493"
WARPERIA_URL = "https://warperia.com/addon-wotlk/atlasloot-enhanced/"
ADDON_ID = "atlasloot-hellscream"


def replace_once(text: str, old: str, new: str, label: str) -> str:
    if new in text:
        return text
    if old not in text:
        raise RuntimeError(f"Could not find {label} marker")
    return text.replace(old, new, 1)


def update_data() -> None:
    payload = json.loads(DATA.read_text(encoding="utf-8"))

    if not any(tag.get("id") == "loot-database" for tag in payload["tags"]):
        payload["tags"].append({
            "id": "loot-database",
            "label": "Loot Database & Maps",
            "group": "feature",
            "description": "Browses boss loot, custom server rewards, collections, and instance maps from inside the game.",
            "searchAliases": [
                "atlas loot",
                "loot tables",
                "boss drops",
                "dungeon maps",
                "custom loot",
                "where does item drop",
            ],
            "order": 170,
        })

    if not any(item.get("id") == "loot-reference" for item in payload["purposes"]):
        payload["purposes"].append({
            "id": "loot-reference",
            "label": "Loot Database & Dungeon Maps",
            "icon": "▧",
            "order": 190,
        })

    if not any(addon.get("id") == ADDON_ID for addon in payload["addons"]):
        payload["addons"].append({
            "id": ADDON_ID,
            "name": "AtlasLoot Enhanced for Hellscream",
            "aliases": [
                "AtlasLoot",
                "Atlas Loot",
                "AtlasLoot Enhanced",
                "AtlasLoot for Hellscream",
                "AtlasLoot v5.11.04",
            ],
            "searchTerms": [
                "atlas loot",
                "boss loot",
                "loot tables",
                "boss drops",
                "dungeon maps",
                "instance maps",
                "custom loot",
                "hellscream content",
                "heroic ragefire chasm",
                "heroic shadowfang keep",
                "heroic stockade",
                "heroic sunken temple",
                "heroic zul farrak",
                "heroic zul gurub",
                "bumble",
                "crimson crusade",
                "where does item drop",
            ],
            "summary": "The recommended Hellscream loot and map reference, combining AtlasLoot v5.11.04 with server-specific loot tables, custom content, and Atlas maps.",
            "does": [
                "Browses dungeon, raid, profession, PvP, faction, collection, and boss loot tables without visiting each source in person.",
                "Adds Hellscream-specific custom-content menus and loot records while bundling compatible Atlas instance maps and supporting modules.",
                "Provides item filtering, wishlists, source browsing, and a quick reference for planning upgrades and farming routes.",
            ],
            "doesNot": [
                "Does not provide a complete live database; the February 2026 post says some Burning Crusade heroic and Crimson Crusade reputation items are still missing.",
                "Does not guarantee every custom item is already cached; a question-mark item may require closing AtlasLoot and reopening it.",
            ],
            "generalSetup": [
                "Open the Hellscream Discord post below and download AtlasLoot.7z; Discord sign-in and membership in the server may be required.",
                "Exit WoW completely, then remove or rename older Atlas and AtlasLoot folders so files from different releases cannot mix.",
                "Extract every included Atlas and AtlasLoot folder together into Interface\\AddOns; do not place the AtlasLoot.7z archive itself in AddOns.",
                "At character select, enable the bundled Atlas and AtlasLoot modules and confirm AtlasLoot reports the v5.11.04 base version.",
                "Open AtlasLoot with /atlasloot or /al, confirm Hellscream Content and Atlas maps appear, then test a custom loot page before relying on it.",
            ],
            "tags": [
                "all-roles",
                "interface",
                "loot-database",
                "setup-required",
                "verified-335-download",
                "tested-hellscream",
                "server-sensitive",
            ],
            "featuredTags": [
                "loot-database",
                "verified-335-download",
                "tested-hellscream",
            ],
            "scope": {
                "classes": [
                    "paladin", "warrior", "death-knight", "druid", "priest",
                    "shaman", "mage", "warlock", "rogue", "hunter",
                ],
                "specs": [],
                "roles": ["tank", "healer", "dps"],
                "activities": ["dungeons", "raids", "pvp", "leveling"],
                "universalClasses": True,
                "universalSpecs": True,
            },
            "recommendations": [{
                "audience": {"roles": ["tank", "healer", "dps"]},
                "importance": "recommended",
                "purposes": ["loot-reference"],
                "summary": "The recommended loot database and dungeon-map package for Hellscream because it includes server-specific content absent from the stock release.",
                "reason": "The custom package keeps the familiar AtlasLoot and Atlas workflow while adding Hellscream loot tables and custom-content menus. Use it as a planning reference, but keep the documented coverage gaps in mind.",
            }],
            "customizations": [],
            "compatibility": {
                "client": "3.3.5a",
                "hellscreamTested": True,
                "hellscreamTestedDate": "2026-07-25",
                "lastReviewed": "2026-07-25",
                "downloadVersion": "Hellscream 2026-02-05 · base v5.11.04",
                "verifiedDownload": True,
                "serverSensitive": True,
                "maintenanceState": "server-custom",
                "notes": [
                    "Hellscream use confirmed July 25, 2026: this custom package works during normal play with no remembered errors or addon conflicts.",
                    "The recommended package is the Hellscream-specific build posted February 5, 2026, based on AtlasLoot Enhanced v5.11.04; it should not be confused with the stock public release.",
                    "Install all folders from the same package together. Mixing Atlas, AtlasLoot, or data modules from another release can produce missing menus, stale loot, or silent errors.",
                    "The February 2026 maintainer post says some Burning Crusade heroic items and Crimson Crusade reputation items remain missing, with more server content still to be added.",
                    "Older maintainer guidance notes that a question-mark item may resolve after closing the AtlasLoot window and reopening it.",
                    "The Discord message is the authoritative source post and may require signing in or joining the Hellscream Discord before its attachment is visible.",
                    "The inspected AtlasLoot.7z package is 13,036,815 bytes with SHA-256 c28eaa13b2c73d00f885178cae5f0eb7f4936b1e4d7c85afea5da8eceec36a73.",
                ],
            },
            "download": {
                "url": DISCORD_URL,
                "source": "Hellscream Discord",
                "notes": "February 5, 2026 message containing the recommended AtlasLoot.7z Hellscream package; sign-in or server membership may be required.",
            },
            "alternateDownloads": [{
                "url": WARPERIA_URL,
                "source": "Warperia",
                "label": "Stock AtlasLoot v5.11.04 fallback ↗",
                "notes": "WotLK 3.3.5 fallback only. It does not include Hellscream custom loot tables, custom-content menus, or the server-matched Atlas package.",
            }],
            "icon": {
                "path": "assets/addons/icons/atlasloot-hellscream.svg",
                "alt": "Open loot chest over a folded dungeon map with a Hellscream ember",
            },
            "screenshots": [],
            "videos": [],
            "relatedGuides": [],
        })

    DATA.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def update_html() -> None:
    text = HTML.read_text(encoding="utf-8")
    text = re.sub(r'(\.\./assets/[^"\']+\?v=)[^"\']+', r'\g<1>20260725-atlasloot-v1', text)
    text = text.replace("The catalog currently has seventeen addons.", "The catalog currently has eighteen addons.")
    marker = '            <li><a href="https://warperia.com/addon-wotlk/pawn/" target="_blank" rel="noopener">Pawn ↗</a></li>\n'
    addition = marker + f'            <li><a href="{DISCORD_URL}" target="_blank" rel="noopener">AtlasLoot Enhanced for Hellscream ↗</a></li>\n'
    text = replace_once(text, marker, addition, "AtlasLoot no-JavaScript link")
    HTML.write_text(text, encoding="utf-8")


def update_catalog_renderer() -> None:
    text = CATALOG_JS.read_text(encoding="utf-8")
    state_marker = '    "legacy-compatible": "Legacy compatibility build"\n'
    state_addition = '    "legacy-compatible": "Legacy compatibility build",\n    "server-custom": "Server-custom Hellscream build"\n'
    text = replace_once(text, state_marker, state_addition, "server-custom maintenance label")

    action_marker = '      actions.append(download);\n      (addon.relatedGuides || []).forEach((guide) => {\n'
    action_addition = '''      actions.append(download);\n      (addon.alternateDownloads || []).forEach((source) => {\n        const link = make("a", "addon-download-link", source.label || `Alternate download from ${source.source} ↗`);\n        link.href = source.url;\n        link.target = "_blank";\n        link.rel = "noopener";\n        actions.append(link);\n      });\n      (addon.relatedGuides || []).forEach((guide) => {\n'''
    text = replace_once(text, action_marker, action_addition, "alternate download links")

    meta_marker = '      dialogContent.append(make("p", "addon-source-meta", `${addon.download.source} · ${addon.compatibility.downloadVersion} · ${addon.download.notes}`));\n\n'
    meta_addition = '''      dialogContent.append(make("p", "addon-source-meta", `${addon.download.source} · ${addon.compatibility.downloadVersion} · ${addon.download.notes}`));\n      (addon.alternateDownloads || []).forEach((source) => {\n        dialogContent.append(make("p", "addon-source-meta", `${source.source} fallback · ${source.notes}`));\n      });\n\n'''
    text = replace_once(text, meta_marker, meta_addition, "alternate download notes")
    CATALOG_JS.write_text(text, encoding="utf-8")


def update_validator() -> None:
    text = VALIDATOR.read_text(encoding="utf-8")
    text = replace_once(text, '    "pawn",\n}', '    "pawn",\n    "atlasloot-hellscream",\n}', "required AtlasLoot addon")
    tested_old = 'TESTED_HELLSCREAM_ADDONS = {"questie", "skada", "chatter", "auctioneer-suite", "addon-control-panel", "bartender4", "outfitter", "pawn"}'
    tested_new = 'TESTED_HELLSCREAM_ADDONS = {"questie", "skada", "chatter", "auctioneer-suite", "addon-control-panel", "bartender4", "outfitter", "pawn", "atlasloot-hellscream"}'
    text = replace_once(text, tested_old, tested_new, "tested AtlasLoot set")

    marker = '''        if parsed.scheme != "https" or not parsed.netloc:\n            fail(errors, f"{addon_id}: invalid HTTPS download URL {download_url!r}")\n        icon = addon.get("icon", {})\n'''
    addition = '''        if parsed.scheme != "https" or not parsed.netloc:\n            fail(errors, f"{addon_id}: invalid HTTPS download URL {download_url!r}")\n        for alternate in addon.get("alternateDownloads", []):\n            alternate_url = alternate.get("url", "")\n            parsed_alternate = urlparse(alternate_url)\n            if parsed_alternate.scheme != "https" or not parsed_alternate.netloc:\n                fail(errors, f"{addon_id}: invalid alternate HTTPS download URL {alternate_url!r}")\n            if not alternate.get("source", "").strip() or not alternate.get("label", "").strip() or not alternate.get("notes", "").strip():\n                fail(errors, f"{addon_id}: alternate downloads need source, label, and notes")\n        icon = addon.get("icon", {})\n'''
    text = replace_once(text, marker, addition, "alternate download validation")
    VALIDATOR.write_text(text, encoding="utf-8")


def update_search_tests() -> None:
    text = SEARCH_TEST.read_text(encoding="utf-8")
    cases_marker = '  ["upgrade score", "pawn"]\n];\n'
    cases_addition = '  ["upgrade score", "pawn"],\n  ["atlas loot", "atlasloot-hellscream"],\n  ["custom loot", "atlasloot-hellscream"],\n  ["dungeon maps", "atlasloot-hellscream"]\n];\n'
    text = replace_once(text, cases_marker, cases_addition, "AtlasLoot search cases")
    text = text.replace('assert.equal(ids("").length, 17);', 'assert.equal(ids("").length, 18);')

    marker = '''const pawnRole = core.recommendationFor(pawn, state("", { role: ["tank"] }), catalog);\nassert.equal(pawnRole.importance, "recommended");\nassert.deepEqual(pawnRole.purposes, ["gear-evaluation"]);\n\n'''
    addition = marker + '''const atlasLoot = addons.find((addon) => addon.id === "atlasloot-hellscream");\nassert.equal(atlasLoot.compatibility.downloadVersion, "Hellscream 2026-02-05 · base v5.11.04");\nassert.equal(atlasLoot.compatibility.hellscreamTested, true);\nassert.equal(atlasLoot.compatibility.hellscreamTestedDate, "2026-07-25");\nassert.equal(atlasLoot.download.url, "https://discord.com/channels/608456284643262504/1328533521983340574/1469088948956434493");\nassert.equal(atlasLoot.alternateDownloads[0].url, "https://warperia.com/addon-wotlk/atlasloot-enhanced/");\nassert.ok(atlasLoot.tags.includes("tested-hellscream"));\nassert.ok(atlasLoot.tags.includes("server-sensitive"));\nassert.match(atlasLoot.compatibility.notes.join(" "), /Burning Crusade heroic items/);\nassert.match(atlasLoot.compatibility.notes.join(" "), /Crimson Crusade reputation items/);\nassert.match(atlasLoot.generalSetup.join(" "), /install.*together|every included/i);\nconst atlasLootRole = core.recommendationFor(atlasLoot, state("", { role: ["dps"] }), catalog);\nassert.equal(atlasLootRole.importance, "recommended");\nassert.deepEqual(atlasLootRole.purposes, ["loot-reference"]);\n\n'''
    text = replace_once(text, marker, addition, "AtlasLoot data assertions")
    SEARCH_TEST.write_text(text, encoding="utf-8")


def update_browser_tests() -> None:
    text = BROWSER_TEST.read_text(encoding="utf-8")
    text = text.replace('17, "Default catalog should show seventeen addons"', '18, "Default catalog should show eighteen addons"')
    text = text.replace('assert.equal(await desktop.locator(".addon-card").count(), 17);', 'assert.equal(await desktop.locator(".addon-card").count(), 18);')

    card_marker = '''    assert.equal(await pawnCard.locator(".addon-card-tag", { hasText: "Tested on Hellscream" }).count(), 1);\n\n'''
    card_addition = card_marker + '''    await desktop.locator("#addon-search-input").fill("custom loot");\n    await desktop.waitForTimeout(80);\n    assert.equal(await desktop.locator(".addon-card h2").first().textContent(), "AtlasLoot Enhanced for Hellscream");\n    const atlasLootCard = desktop.locator('.addon-card[data-addon-id="atlasloot-hellscream"]');\n    assert.equal(await atlasLootCard.locator(".addon-card-tag").first().textContent(), "Loot Database & Maps");\n    assert.equal(await atlasLootCard.locator(".addon-card-tag", { hasText: "Tested on Hellscream" }).count(), 1);\n\n'''
    text = replace_once(text, card_marker, card_addition, "AtlasLoot card checks")

    drawer_marker = '''    assert.equal(await desktop.locator('a[href="https://warperia.com/addon-wotlk/pawn/"]').count() > 0, true);\n    await noOverflow(desktop, "Pawn details drawer");\n\n'''
    drawer_addition = drawer_marker + '''    await desktop.goto(`${base}/guides/addons.html?activity=raids#addon=atlasloot-hellscream`, { waitUntil: "networkidle" });\n    await desktop.waitForSelector("#addon-details-dialog[open]");\n    assert.equal(await desktop.locator("#addon-dialog-title").textContent(), "AtlasLoot Enhanced for Hellscream");\n    const atlasLootText = await desktop.locator("#addon-dialog-content").textContent();\n    assert.match(atlasLootText, /v5\.11\.04/);\n    assert.match(atlasLootText, /February 5, 2026/);\n    assert.match(atlasLootText, /Burning Crusade heroic items/);\n    assert.match(atlasLootText, /Crimson Crusade reputation items/);\n    assert.match(atlasLootText, /closing AtlasLoot.*reopening/i);\n    assert.match(atlasLootText, /Stock AtlasLoot v5\.11\.04 fallback/);\n    assert.equal(await desktop.locator('a[href="https://discord.com/channels/608456284643262504/1328533521983340574/1469088948956434493"]').count() > 0, true);\n    assert.equal(await desktop.locator('a[href="https://warperia.com/addon-wotlk/atlasloot-enhanced/"]').count() > 0, true);\n    await noOverflow(desktop, "AtlasLoot details drawer");\n\n'''
    text = replace_once(text, drawer_marker, drawer_addition, "AtlasLoot drawer checks")

    mobile_marker = '''    await noOverflow(mobile, "Mobile catalog and drawer");\n    assert.equal(await mobile.locator(".addon-grid").evaluate((node) => getComputedStyle(node).gridTemplateColumns.split(" ").length), 1);\n\n'''
    mobile_addition = mobile_marker + '''    await mobile.goto(`${base}/guides/addons.html?activity=raids#addon=atlasloot-hellscream`, { waitUntil: "networkidle" });\n    await mobile.waitForSelector("#addon-details-dialog[open]");\n    assert.equal(await mobile.locator("#addon-dialog-title").textContent(), "AtlasLoot Enhanced for Hellscream");\n    await noOverflow(mobile, "Mobile AtlasLoot drawer");\n\n'''
    text = replace_once(text, mobile_marker, mobile_addition, "AtlasLoot mobile checks")
    BROWSER_TEST.write_text(text, encoding="utf-8")


def write_icon() -> None:
    ICON.parent.mkdir(parents=True, exist_ok=True)
    ICON.write_text('''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 128 128" role="img" aria-labelledby="title desc">\n  <title id="title">AtlasLoot Enhanced for Hellscream</title>\n  <desc id="desc">An open loot chest over a folded dungeon map with a Hellscream ember.</desc>\n  <rect x="8" y="8" width="112" height="112" rx="18" fill="#171b20" stroke="#a4a9a5" stroke-width="5"/>\n  <path d="M22 80 45 65l22 12 38-22v42L68 112 44 99 22 111Z" fill="#414444" stroke="#dedcd6" stroke-width="4" stroke-linejoin="round"/>\n  <path d="M45 65v34M67 77v35M22 80l22 12 23-15 20 11 18-10" fill="none" stroke="#a4a9a5" stroke-width="3" stroke-linejoin="round"/>\n  <path d="M31 43h66v34H31Z" fill="#6b3b1d" stroke="#dedcd6" stroke-width="4"/>\n  <path d="M35 43c0-15 12-25 29-25s29 10 29 25Z" fill="#cf4e17" stroke="#dedcd6" stroke-width="4"/>\n  <path d="M31 56h66" stroke="#cf4e17" stroke-width="5"/>\n  <rect x="57" y="52" width="14" height="18" rx="3" fill="#dedcd6" stroke="#171b20" stroke-width="3"/>\n  <path d="M64 23c9 8 11 15 4 22 1-7-4-9-7-13-5 7-8 13-2 20-14-7-14-20 5-29Z" fill="#ff8a3d" stroke="#dedcd6" stroke-width="2"/>\n</svg>\n''', encoding="utf-8")


def main() -> None:
    update_data()
    update_html()
    update_catalog_renderer()
    update_validator()
    update_search_tests()
    update_browser_tests()
    write_icon()


if __name__ == "__main__":
    main()
