#!/usr/bin/env python3
"""Add the tested Chatter record and update catalog regression coverage."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "addons.json"
VALIDATOR = ROOT / "scripts" / "validate-addon-catalog.py"
HTML = ROOT / "guides" / "addons.html"
UNIT = ROOT / "tests" / "addon-search.test.js"
BROWSER = ROOT / "tests" / "addon-browser-smoke.cjs"
ICON = ROOT / "assets" / "addons" / "icons" / "chatter.svg"


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"{label}: expected one match, found {count}")
    return text.replace(old, new, 1)


def main() -> None:
    payload = json.loads(DATA.read_text(encoding="utf-8"))
    if not any(addon.get("id") == "chatter" for addon in payload["addons"]):
        if not any(tag.get("id") == "chat-enhancement" for tag in payload["tags"]):
            payload["tags"].append({
                "id": "chat-enhancement",
                "label": "Chat Enhancement",
                "group": "feature",
                "description": "Improves chat formatting, timestamps, links, copying, tabs, and related communication tools.",
                "searchAliases": ["chat addon", "chat formatting", "chat timestamps", "copy chat"],
                "order": 130,
            })
        if not any(purpose.get("id") == "communication" for purpose in payload["purposes"]):
            payload["purposes"].append({
                "id": "communication",
                "label": "Communication",
                "icon": "▤",
                "order": 130,
            })
        payload["addons"].append({
            "id": "chatter",
            "name": "Chatter",
            "aliases": ["Chatter 1.0", "Chatter chat addon"],
            "searchTerms": [
                "chat addon", "chat timestamps", "copy chat", "chat links", "chat tabs",
                "channel colors", "player names", "alt linking", "guild notes", "chat font"
            ],
            "summary": "A configurable chat overhaul with timestamps, copying, links, channel styling, player names, tabs, fonts, and other quality-of-life tools.",
            "does": [
                "Adds timestamps, chat copying, clickable links, channel colors, player-name options, and chat formatting controls.",
                "Provides configurable tabs, fonts, edit-box behavior, scrollback, highlights, and related chat modules.",
                "Lets players enable only the chat modules they actually want."
            ],
            "doesNot": [
                "Does not load cleanly with guild-note scanning enabled on the tested Hellscream setup.",
                "Does not require Alt Linking; that module can be partly or fully disabled while the rest of Chatter remains usable."
            ],
            "generalSetup": [
                "Install the archive so Interface\\AddOns\\Chatter\\Chatter.toc is the final path.",
                "Type /chatter, then open Modules → Alt Linking.",
                "Uncheck Use guildnotes, click Okay, and run /reload to prevent the confirmed login error.",
                "If alt-name linking is not needed, uncheck Enable Alt Linking to disable the entire module instead.",
                "Configure the remaining chat modules one at a time and check Swatter after reloading."
            ],
            "tags": [
                "all-roles", "interface", "chat-enhancement", "beginner-friendly",
                "verified-335-download", "tested-hellscream", "server-sensitive"
            ],
            "featuredTags": ["chat-enhancement", "tested-hellscream", "server-sensitive"],
            "scope": {
                "classes": [
                    "paladin", "warrior", "death-knight", "druid", "priest",
                    "shaman", "mage", "warlock", "rogue", "hunter"
                ],
                "specs": [],
                "roles": ["tank", "healer", "dps"],
                "activities": ["dungeons", "raids", "pvp", "leveling", "daily-weekly-quests"],
                "universalClasses": True,
                "universalSpecs": True,
            },
            "recommendations": [{
                "audience": {"roles": ["tank", "healer", "dps"]},
                "importance": "optional",
                "purposes": ["communication"],
                "summary": "Modernize and customize the old 3.3.5 chat window after applying the guild-note workaround.",
                "reason": "Chatter adds substantial chat convenience, but the tested build needs one optional guild-note feature disabled to avoid a login error."
            }],
            "customizations": [],
            "compatibility": {
                "client": "3.3.5a",
                "hellscreamTested": True,
                "hellscreamTestedDate": "2026-07-23",
                "lastReviewed": "2026-07-23",
                "downloadVersion": "1.0",
                "verifiedDownload": True,
                "serverSensitive": True,
                "maintenanceState": "wrath-era",
                "notes": [
                    "Hellscream test on July 23, 2026: Chatter loaded and its normal chat features appeared to work within a large addon setup.",
                    "Confirmed login error: Modules/AltNames.lua line 331 calls strlower on a missing guild-note value while Alt Linking scans guild notes.",
                    "Workaround: /chatter → Modules → Alt Linking → uncheck Use guildnotes → Okay → /reload.",
                    "Disabling Enable Alt Linking entirely also prevents that module from running while leaving the rest of Chatter available.",
                    "Because a confirmed error exists before applying the workaround, this is a tested-with-workaround record rather than a clean compatibility pass."
                ]
            },
            "download": {
                "url": "https://warperia.com/addon-wotlk/chatter/",
                "source": "Warperia",
                "notes": "Use the Wrath of the Lich King 3.3.5 download labeled 1.0."
            },
            "icon": {
                "path": "assets/addons/icons/chatter.svg",
                "alt": "Two overlapping chat bubbles"
            },
            "screenshots": [],
            "videos": [],
            "relatedGuides": []
        })
        DATA.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    ICON.parent.mkdir(parents=True, exist_ok=True)
    ICON.write_text('''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 128 128" role="img" aria-labelledby="title desc">
  <title id="title">Chatter chat addon</title>
  <desc id="desc">Two overlapping chat bubbles.</desc>
  <rect x="8" y="8" width="112" height="112" rx="18" fill="#171b20" stroke="#a4a9a5" stroke-width="5"/>
  <path d="M24 29h63a10 10 0 0 1 10 10v29a10 10 0 0 1-10 10H55L36 94l4-16H24a10 10 0 0 1-10-10V39a10 10 0 0 1 10-10z" fill="#dedcd6" stroke="#414444" stroke-width="4" stroke-linejoin="round"/>
  <path d="M61 55h42a10 10 0 0 1 10 10v25a10 10 0 0 1-10 10H91l3 13-17-13H61a10 10 0 0 1-10-10V65a10 10 0 0 1 10-10z" fill="#cf4e17" stroke="#414444" stroke-width="4" stroke-linejoin="round"/>
  <circle cx="68" cy="77" r="4" fill="#ebe9e3"/><circle cx="82" cy="77" r="4" fill="#ebe9e3"/><circle cx="96" cy="77" r="4" fill="#ebe9e3"/>
</svg>
''', encoding="utf-8")

    validator = VALIDATOR.read_text(encoding="utf-8")
    if '"chatter",' not in validator:
        validator = replace_once(validator, '    "skada",\n}', '    "skada",\n    "chatter",\n}', "validator addon set")
        validator = replace_once(validator, 'TESTED_HELLSCREAM_ADDONS = {"questie", "skada"}', 'TESTED_HELLSCREAM_ADDONS = {"questie", "skada", "chatter"}', "validator tested set")
        VALIDATOR.write_text(validator, encoding="utf-8")

    html = HTML.read_text(encoding="utf-8")
    if "20260723-chatter-v1" not in html:
        html = html.replace("20260723-skada-v1", "20260723-chatter-v1")
        html = replace_once(html, "The catalog currently has eleven addons.", "The catalog currently has twelve addons.", "noscript count")
        html = replace_once(
            html,
            '            <li><a href="https://warperia.com/addon-wotlk/skada-revisited/" target="_blank" rel="noopener">Skada Revisited ↗</a></li>',
            '            <li><a href="https://warperia.com/addon-wotlk/skada-revisited/" target="_blank" rel="noopener">Skada Revisited ↗</a></li>\n            <li><a href="https://warperia.com/addon-wotlk/chatter/" target="_blank" rel="noopener">Chatter ↗</a></li>',
            "noscript Chatter link",
        )
        HTML.write_text(html, encoding="utf-8")

    unit = UNIT.read_text(encoding="utf-8")
    if '["chat addon", "chatter"]' not in unit:
        unit = replace_once(unit, '  ["quest helper", "questie"]\n];', '  ["quest helper", "questie"],\n  ["chat addon", "chatter"],\n  ["chat timestamps", "chatter"]\n];', "unit search cases")
        unit = unit.replace('assert.equal(ids("").length, 11);', 'assert.equal(ids("").length, 12);')
        marker = 'const parsedLegacy = core.parseUrlState('
        chatter_tests = '''const chatter = addons.find((addon) => addon.id === "chatter");
assert.equal(chatter.compatibility.downloadVersion, "1.0");
assert.equal(chatter.compatibility.hellscreamTested, true);
assert.equal(chatter.compatibility.hellscreamTestedDate, "2026-07-23");
assert.ok(chatter.tags.includes("tested-hellscream"));
assert.match(chatter.compatibility.notes.join(" "), /Use guildnotes/);
assert.match(chatter.generalSetup.join(" "), /Modules.*Alt Linking/);
assert.equal(chatter.download.url, "https://warperia.com/addon-wotlk/chatter/");
const chatterRole = core.recommendationFor(chatter, state("", { role: ["healer"] }), catalog);
assert.equal(chatterRole.importance, "optional");
assert.deepEqual(chatterRole.purposes, ["communication"]);

'''
        unit = replace_once(unit, marker, chatter_tests + marker, "unit Chatter assertions")
        UNIT.write_text(unit, encoding="utf-8")

    browser = BROWSER.read_text(encoding="utf-8")
    if 'data-addon-id="chatter"' not in browser:
        browser = browser.replace("Default catalog should show eleven addons", "Default catalog should show twelve addons")
        browser = browser.replace('.count(), 11, "Default catalog', '.count(), 12, "Default catalog', 1)
        browser = replace_once(
            browser,
            '    assert.equal(await desktop.locator(".addon-card h2").first().textContent(), "Skada Revisited");\n',
            '    assert.equal(await desktop.locator(".addon-card h2").first().textContent(), "Skada Revisited");\n\n    await desktop.locator("#addon-search-input").fill("chat timestamps");\n    await desktop.waitForTimeout(80);\n    assert.equal(await desktop.locator(".addon-card h2").first().textContent(), "Chatter");\n',
            "browser Chatter search",
        )
        marker = '    await desktop.goto(`${base}/guides/addons.html?class=paladin&spec=paladin-protection&role=tank`, { waitUntil: "networkidle" });'
        chatter_browser = '''    await desktop.goto(`${base}/guides/addons.html?role=healer#addon=chatter`, { waitUntil: "networkidle" });
    await desktop.waitForSelector("#addon-details-dialog[open]");
    assert.equal(await desktop.locator("#addon-dialog-title").textContent(), "Chatter");
    const chatterText = await desktop.locator("#addon-dialog-content").textContent();
    assert.match(chatterText, /1\.0/);
    assert.match(chatterText, /Use guildnotes/);
    assert.match(chatterText, /Alt Linking/);
    assert.equal(await desktop.locator('a[href="https://warperia.com/addon-wotlk/chatter/"]').count() > 0, true);

'''
        browser = replace_once(browser, marker, chatter_browser + marker, "browser Chatter drawer")
        browser = browser.replace('assert.equal(await desktop.locator(".addon-card").count(), 11);', 'assert.equal(await desktop.locator(".addon-card").count(), 12);')
        BROWSER.write_text(browser, encoding="utf-8")

    print("Chatter catalog migration applied.")


if __name__ == "__main__":
    main()
