#!/usr/bin/env python3
"""Add Outfitter 5.0 as a tested Hellscream equipment-set addon."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "addons.json"
HTML = ROOT / "guides" / "addons.html"
VALIDATOR = ROOT / "scripts" / "validate-addon-catalog.py"
SEARCH_TEST = ROOT / "tests" / "addon-search.test.js"
BROWSER_TEST = ROOT / "tests" / "addon-browser-smoke.cjs"
ICON = ROOT / "assets" / "addons" / "icons" / "outfitter.svg"


def replace_once(text: str, old: str, new: str, label: str) -> str:
    if text.count(old) != 1:
        raise RuntimeError(f"Expected exactly one {label} marker, found {text.count(old)}")
    return text.replace(old, new, 1)


def update_json() -> None:
    data = json.loads(DATA.read_text(encoding="utf-8"))
    if any(addon["id"] == "outfitter" for addon in data["addons"]):
        raise RuntimeError("Outfitter already exists")

    if not any(tag["id"] == "equipment-sets" for tag in data["tags"]):
        data["tags"].append({
            "id": "equipment-sets",
            "label": "Equipment Sets",
            "group": "feature",
            "description": "Creates, switches, and optionally automates named gear and weapon sets.",
            "searchAliases": [
                "gear sets",
                "equipment manager",
                "outfits",
                "automatic gear switching",
                "outfitter"
            ],
            "order": 150
        })

    if not any(purpose["id"] == "equipment-sets" for purpose in data["purposes"]):
        data["purposes"].append({
            "id": "equipment-sets",
            "label": "Equipment Sets",
            "icon": "♜",
            "order": 170
        })

    data["addons"].append({
        "id": "outfitter",
        "name": "Outfitter",
        "aliases": [
            "Outfitter 5.0",
            "Out Fitter"
        ],
        "searchTerms": [
            "gear sets",
            "equipment sets",
            "equipment manager",
            "outfit manager",
            "automatic gear switching",
            "switch gear hotkey",
            "fishing outfit",
            "pvp outfit",
            "tank set",
            "healing set",
            "weapon sets"
        ],
        "summary": "Create named equipment sets, switch them quickly, and optionally automate outfit changes for different activities.",
        "does": [
            "Creates named gear and weapon sets for different roles, activities, resistance needs, professions, or cosmetic outfits.",
            "Switches outfits from its menu or assigned controls and shows which items belong to each saved set.",
            "Supports optional automated equip and unequip behavior for configured situations and activities."
        ],
        "doesNot": [
            "Does not decide which items are best for a role or replace a stat-weight addon such as Pawn.",
            "Cannot bypass WoW's combat equipment restrictions, so some outfit changes must wait until combat ends."
        ],
        "generalSetup": [
            "Download Outfitter 5.0 from the WotLK 3.3.5 page linked below.",
            "Remove or rename an older Outfitter folder, then install so Interface\\AddOns\\Outfitter\\Outfitter.toc is the final path.",
            "Restart WoW completely after replacing the addon files; a reload alone may leave the old table-of-contents information cached.",
            "Create one simple outfit, switch away and back, reload the UI, and confirm the set and item choices persist.",
            "Test any automatic outfit rules separately in easy content before relying on them during raids, PvP, professions, or travel."
        ],
        "tags": [
            "all-roles",
            "interface",
            "equipment-sets",
            "beginner-friendly",
            "verified-335-download",
            "tested-hellscream"
        ],
        "featuredTags": [
            "equipment-sets",
            "verified-335-download",
            "tested-hellscream"
        ],
        "scope": {
            "classes": [
                "paladin", "warrior", "death-knight", "druid", "priest",
                "shaman", "mage", "warlock", "rogue", "hunter"
            ],
            "specs": [],
            "roles": ["tank", "healer", "dps"],
            "activities": [],
            "universalClasses": True,
            "universalSpecs": True
        },
        "recommendations": [
            {
                "audience": {"roles": ["tank", "healer", "dps"]},
                "importance": "recommended",
                "purposes": ["equipment-sets"],
                "summary": "A strong equipment-set manager for characters that regularly switch roles, activities, weapons, profession gear, or specialized sets.",
                "reason": "Outfitter provides faster organization and optional automation beyond basic manual gear swapping, and this exact build has worked on Hellscream alongside a large addon setup."
            }
        ],
        "customizations": [],
        "compatibility": {
            "client": "3.3.5a",
            "hellscreamTested": True,
            "hellscreamTestedDate": "2026-07-24",
            "lastReviewed": "2026-07-24",
            "downloadVersion": "5.0",
            "verifiedDownload": True,
            "serverSensitive": False,
            "maintenanceState": "wrath-era",
            "notes": [
                "Hellscream test reported July 24, 2026: Outfitter 5.0 worked during normal use with many other addons enabled.",
                "No addon conflicts were noticed or reported during that use.",
                "The exact companion-addon list was not recorded, so compatibility with every possible addon combination is not claimed.",
                "Warperia identifies the linked archive as Outfitter 5.0 for WotLK 3.3.5; an independent archive listing identifies Outfitter_5.0.zip with Interface 30300."
            ]
        },
        "download": {
            "url": "https://warperia.com/addon-wotlk/outfitter/",
            "source": "Warperia",
            "notes": "Outfitter 5.0 download page for WotLK 3.3.5."
        },
        "icon": {
            "path": "assets/addons/icons/outfitter.svg",
            "alt": "Armor chestpiece with circular equipment-switch arrows"
        },
        "screenshots": [],
        "videos": [],
        "relatedGuides": []
    })

    DATA.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def update_html() -> None:
    text = HTML.read_text(encoding="utf-8")
    text = text.replace("20260724-bartender4-v1", "20260724-outfitter-v1")
    text = replace_once(text, "The catalog currently has fifteen addons.", "The catalog currently has sixteen addons.", "noscript count")
    marker = '            <li><a href="https://www.curseforge.com/wow/addons/bartender4/files/439962" target="_blank" rel="noopener">Bartender4 ↗</a></li>\n'
    addition = marker + '            <li><a href="https://warperia.com/addon-wotlk/outfitter/" target="_blank" rel="noopener">Outfitter ↗</a></li>\n'
    text = replace_once(text, marker, addition, "Outfitter noscript link")
    HTML.write_text(text, encoding="utf-8")


def update_validator() -> None:
    text = VALIDATOR.read_text(encoding="utf-8")
    text = replace_once(text, '    "bartender4",\n}', '    "bartender4",\n    "outfitter",\n}', "required addon set")
    text = replace_once(
        text,
        'TESTED_HELLSCREAM_ADDONS = {"questie", "skada", "chatter", "auctioneer-suite", "bartender4"}',
        'TESTED_HELLSCREAM_ADDONS = {"questie", "skada", "chatter", "auctioneer-suite", "bartender4", "outfitter"}',
        "tested addon set"
    )
    VALIDATOR.write_text(text, encoding="utf-8")


def update_search_test() -> None:
    text = SEARCH_TEST.read_text(encoding="utf-8")
    text = replace_once(
        text,
        '  ["bartender", "bartender4"],\n  ["action bars", "bartender4"]',
        '  ["bartender", "bartender4"],\n  ["action bars", "bartender4"],\n  ["outfitter", "outfitter"],\n  ["gear sets", "outfitter"]',
        "search cases"
    )
    text = replace_once(text, 'assert.equal(ids("").length, 15);', 'assert.equal(ids("").length, 16);', "addon count")
    marker = 'assert.match(bartenderRole.summary, /top action-bar recommendation/i);\n'
    addition = marker + '''\nconst outfitter = addons.find((addon) => addon.id === "outfitter");
assert.equal(outfitter.compatibility.downloadVersion, "5.0");
assert.equal(outfitter.compatibility.hellscreamTested, true);
assert.equal(outfitter.compatibility.hellscreamTestedDate, "2026-07-24");
assert.equal(outfitter.download.url, "https://warperia.com/addon-wotlk/outfitter/");
assert.ok(outfitter.tags.includes("tested-hellscream"));
assert.match(outfitter.compatibility.notes.join(" "), /No addon conflicts were noticed/);
const outfitterRole = core.recommendationFor(outfitter, state("", { role: ["healer"] }), catalog);
assert.equal(outfitterRole.importance, "recommended");
assert.deepEqual(outfitterRole.purposes, ["equipment-sets"]);
'''
    text = replace_once(text, marker, addition, "Outfitter assertions")
    SEARCH_TEST.write_text(text, encoding="utf-8")


def update_browser_test() -> None:
    text = BROWSER_TEST.read_text(encoding="utf-8")
    text = replace_once(text, 'count(), 15, "Default catalog should show fifteen addons"', 'count(), 16, "Default catalog should show sixteen addons"', "browser addon count")
    marker = '    assert.equal(await bartenderCard.locator(".addon-card-tag", { hasText: "Tested on Hellscream" }).count(), 1);\n'
    addition = marker + '''
    await desktop.locator("#addon-search-input").fill("gear sets");
    await desktop.waitForTimeout(80);
    assert.equal(await desktop.locator(".addon-card h2").first().textContent(), "Outfitter");
    const outfitterCard = desktop.locator('.addon-card[data-addon-id="outfitter"]');
    assert.equal(await outfitterCard.locator(".addon-card-tag").first().textContent(), "Equipment Sets");
    assert.equal(await outfitterCard.locator(".addon-card-tag", { hasText: "Tested on Hellscream" }).count(), 1);
'''
    text = replace_once(text, marker, addition, "Outfitter card checks")
    drawer_marker = '    await noOverflow(desktop, "Bartender4 details drawer");\n'
    drawer_checks = drawer_marker + '''
    await desktop.goto(`${base}/guides/addons.html?role=healer#addon=outfitter`, { waitUntil: "networkidle" });
    await desktop.waitForSelector("#addon-details-dialog[open]");
    assert.equal(await desktop.locator("#addon-dialog-title").textContent(), "Outfitter");
    const outfitterText = await desktop.locator("#addon-dialog-content").textContent();
    assert.match(outfitterText, /5\.0/);
    assert.match(outfitterText, /No addon conflicts were noticed/);
    assert.match(outfitterText, /equipment-set manager/i);
    assert.equal(await desktop.locator('a[href="https://warperia.com/addon-wotlk/outfitter/"]').count() > 0, true);
    await noOverflow(desktop, "Outfitter details drawer");
'''
    text = replace_once(text, drawer_marker, drawer_checks, "Outfitter drawer checks")
    BROWSER_TEST.write_text(text, encoding="utf-8")


def write_icon() -> None:
    ICON.write_text('''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 128 128" role="img" aria-labelledby="title desc">
  <title id="title">Outfitter</title>
  <desc id="desc">Armor chestpiece surrounded by equipment-switch arrows.</desc>
  <rect x="8" y="8" width="112" height="112" rx="18" fill="#171b20" stroke="#a4a9a5" stroke-width="5"/>
  <path d="M43 31l12-8h18l12 8 13 10-10 18-10-7v42H50V52l-10 7-10-18z" fill="#414444" stroke="#dedcd6" stroke-width="4" stroke-linejoin="round"/>
  <path d="M54 25c2 8 18 8 20 0" fill="none" stroke="#cf4e17" stroke-width="5" stroke-linecap="round"/>
  <path d="M29 83c5 17 24 28 42 23" fill="none" stroke="#cf4e17" stroke-width="6" stroke-linecap="round"/>
  <path d="M62 98l11 8-12 7" fill="none" stroke="#cf4e17" stroke-width="6" stroke-linecap="round" stroke-linejoin="round"/>
  <path d="M99 45C92 28 73 19 55 25" fill="none" stroke="#a4a9a5" stroke-width="6" stroke-linecap="round"/>
  <path d="M64 33l-11-8 12-7" fill="none" stroke="#a4a9a5" stroke-width="6" stroke-linecap="round" stroke-linejoin="round"/>
</svg>\n''', encoding="utf-8")


def main() -> None:
    update_json()
    update_html()
    update_validator()
    update_search_test()
    update_browser_test()
    write_icon()
    print("Applied Outfitter catalog migration.")


if __name__ == "__main__":
    main()
