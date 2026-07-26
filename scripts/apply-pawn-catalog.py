#!/usr/bin/env python3
"""Add Pawn 1.3.8 to the addon catalog and its tests."""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "addons.json"
HTML = ROOT / "guides" / "addons.html"
VALIDATOR = ROOT / "scripts" / "validate-addon-catalog.py"
SEARCH_TEST = ROOT / "tests" / "addon-search.test.js"
BROWSER_TEST = ROOT / "tests" / "addon-browser-smoke.cjs"
ICON = ROOT / "assets" / "addons" / "icons" / "pawn.svg"


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"{label}: expected one match, found {count}")
    return text.replace(old, new, 1)


def update_catalog() -> None:
    payload = json.loads(DATA.read_text(encoding="utf-8"))
    if any(addon.get("id") == "pawn" for addon in payload["addons"]):
        raise RuntimeError("Pawn already exists")

    payload["tags"].append({
        "id": "gear-evaluation",
        "label": "Gear Evaluation",
        "group": "feature",
        "description": "Scores and compares equipment using a selected set of stat weights.",
        "searchAliases": [
            "stat weights",
            "item scoring",
            "upgrade score",
            "pawn scale",
            "which item is better"
        ],
        "order": 160
    })
    payload["purposes"].append({
        "id": "gear-evaluation",
        "label": "Gear Evaluation",
        "icon": "⚖",
        "order": 180
    })

    payload["addons"].append({
        "id": "pawn",
        "name": "Pawn",
        "aliases": [
            "Pawn 1.3.8",
            "Pawn Addon"
        ],
        "searchTerms": [
            "stat weights",
            "item scoring",
            "gear score",
            "upgrade score",
            "which item is better",
            "tooltip values",
            "gear evaluation",
            "custom scale",
            "pawn scale",
            "compare gear"
        ],
        "summary": "Scores equipment with configurable stat weights and adds comparison values to item tooltips for quick upgrade screening.",
        "does": [
            "Calculates item values from the stat weights in the selected Pawn scale and adds those values to equipment tooltips.",
            "Supports multiple named scales for different roles, specs, PvE or PvP priorities, and specialized gear sets.",
            "Lets players inspect, copy, edit, import, export, rename, and reset scales."
        ],
        "doesNot": [
            "Does not automatically understand defense, hit, expertise, haste, or other caps; linear weights can overvalue a stat after a cap is reached.",
            "Does not prove that an item is best in slot or correctly value every proc, set bonus, socket choice, encounter need, or survivability tradeoff."
        ],
        "generalSetup": [
            "Download Pawn 1.3.8 from the WotLK 3.3.5 page below and install it so Interface\\AddOns\\Pawn\\Pawn.toc is the final path.",
            "Type /pawn and open the Scale tab. Select a scale to see which stat weights it uses and whether that scale is shown on tooltips.",
            "For a quick text view, use /pawn list to list every scale, or /pawn list Scale Name to print every stat and weight in one exact-named scale.",
            "To modify weights, copy the chosen built-in scale first, select the editable copy, and change the listed stat values. Use 0 for a stat you want the scale to ignore.",
            "Use /pawn import to paste a shared scale or /pawn export Scale Name to copy one. Reload the UI, re-open Pawn, and verify the scale and tooltip values were saved."
        ],
        "tags": [
            "all-roles",
            "interface",
            "gear-evaluation",
            "setup-required",
            "verified-335-download",
            "tested-hellscream"
        ],
        "featuredTags": [
            "gear-evaluation",
            "verified-335-download",
            "tested-hellscream"
        ],
        "scope": {
            "classes": [
                "paladin",
                "warrior",
                "death-knight",
                "druid",
                "priest",
                "shaman",
                "mage",
                "warlock",
                "rogue",
                "hunter"
            ],
            "specs": [],
            "roles": [
                "tank",
                "healer",
                "dps"
            ],
            "activities": [
                "dungeons",
                "raids",
                "pvp",
                "leveling"
            ],
            "universalClasses": True,
            "universalSpecs": True
        },
        "recommendations": [
            {
                "audience": {
                    "roles": [
                        "tank",
                        "healer",
                        "dps"
                    ]
                },
                "importance": "recommended",
                "purposes": [
                    "gear-evaluation"
                ],
                "summary": "A useful first-pass gear comparison tool when the active scale matches the character, role, and current stat needs.",
                "reason": "Pawn makes frequent item comparisons faster and this exact build has been used on Hellscream without remembered errors, but its score should remain a screening aid rather than the final gearing decision."
            }
        ],
        "customizations": [],
        "compatibility": {
            "client": "3.3.5a",
            "hellscreamTested": True,
            "hellscreamTestedDate": "2026-07-25",
            "lastReviewed": "2026-07-25",
            "downloadVersion": "1.3.8",
            "verifiedDownload": True,
            "serverSensitive": False,
            "maintenanceState": "wrath-era",
            "notes": [
                "Hellscream use reported July 25, 2026: Pawn 1.3.8 has been used during normal play and no errors are remembered.",
                "No specific addon conflict or tooltip problem is remembered, but this was not a fresh isolated compatibility test against every installed addon and tooltip source.",
                "Warperia identifies the linked download as Pawn version 1.3.8 for WotLK 3.3.5.",
                "Pawn scores are only as reliable as the selected scale; verify caps, special effects, set bonuses, and encounter needs separately."
            ]
        },
        "download": {
            "url": "https://warperia.com/addon-wotlk/pawn/",
            "source": "Warperia",
            "notes": "Pawn 1.3.8 download page for WotLK 3.3.5."
        },
        "icon": {
            "path": "assets/addons/icons/pawn.svg",
            "alt": "Two equipment cards balanced on a stat-weight scale"
        },
        "screenshots": [],
        "videos": [],
        "relatedGuides": []
    })

    DATA.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def update_validator() -> None:
    text = VALIDATOR.read_text(encoding="utf-8")
    text = replace_once(text, '    "outfitter",\n}', '    "outfitter",\n    "pawn",\n}', "required addon")
    text = replace_once(
        text,
        'TESTED_HELLSCREAM_ADDONS = {"questie", "skada", "chatter", "auctioneer-suite", "addon-control-panel", "bartender4", "outfitter"}',
        'TESTED_HELLSCREAM_ADDONS = {"questie", "skada", "chatter", "auctioneer-suite", "addon-control-panel", "bartender4", "outfitter", "pawn"}',
        "tested addon set"
    )
    VALIDATOR.write_text(text, encoding="utf-8")


def update_search_test() -> None:
    text = SEARCH_TEST.read_text(encoding="utf-8")
    text = replace_once(
        text,
        '  ["outfitter", "outfitter"],\n  ["gear sets", "outfitter"]',
        '  ["outfitter", "outfitter"],\n  ["gear sets", "outfitter"],\n  ["pawn", "pawn"],\n  ["stat weights", "pawn"],\n  ["upgrade score", "pawn"]',
        "Pawn search cases"
    )
    text = text.replace('assert.equal(ids("").length, 16);', 'assert.equal(ids("").length, 17);')
    marker = 'assert.deepEqual(outfitterRole.purposes, ["equipment-sets"]);\n'
    addition = marker + '''\nconst pawn = addons.find((addon) => addon.id === "pawn");
assert.equal(pawn.compatibility.downloadVersion, "1.3.8");
assert.equal(pawn.compatibility.hellscreamTested, true);
assert.equal(pawn.compatibility.hellscreamTestedDate, "2026-07-25");
assert.equal(pawn.download.url, "https://warperia.com/addon-wotlk/pawn/");
assert.ok(pawn.tags.includes("tested-hellscream"));
assert.match(pawn.compatibility.notes.join(" "), /no errors are remembered/i);
assert.match(pawn.generalSetup.join(" "), /\\/pawn list Scale Name/);
assert.match(pawn.generalSetup.join(" "), /copy the chosen built-in scale/i);
assert.match(pawn.generalSetup.join(" "), /\\/pawn import/);
const pawnRole = core.recommendationFor(pawn, state("", { role: ["tank"] }), catalog);
assert.equal(pawnRole.importance, "recommended");
assert.deepEqual(pawnRole.purposes, ["gear-evaluation"]);
'''
    text = replace_once(text, marker, addition, "Pawn assertions")
    SEARCH_TEST.write_text(text, encoding="utf-8")


def update_browser_test() -> None:
    text = BROWSER_TEST.read_text(encoding="utf-8")
    text = text.replace('count(), 16, "Default catalog should show sixteen addons"', 'count(), 17, "Default catalog should show seventeen addons"')
    text = text.replace('count(), 16);', 'count(), 17);')
    card_marker = '    assert.equal(await outfitterCard.locator(".addon-card-tag", { hasText: "Tested on Hellscream" }).count(), 1);\n'
    card_addition = card_marker + '''\n    await desktop.locator("#addon-search-input").fill("stat weights");
    await desktop.waitForTimeout(80);
    assert.equal(await desktop.locator(".addon-card h2").first().textContent(), "Pawn");
    const pawnCard = desktop.locator('.addon-card[data-addon-id="pawn"]');
    assert.equal(await pawnCard.locator(".addon-card-tag").first().textContent(), "Gear Evaluation");
    assert.equal(await pawnCard.locator(".addon-card-tag", { hasText: "Tested on Hellscream" }).count(), 1);
'''
    text = replace_once(text, card_marker, card_addition, "Pawn card checks")
    drawer_marker = '    await noOverflow(desktop, "Outfitter details drawer");\n'
    drawer_addition = drawer_marker + '''\n    await desktop.goto(`${base}/guides/addons.html?role=tank#addon=pawn`, { waitUntil: "networkidle" });
    await desktop.waitForSelector("#addon-details-dialog[open]");
    assert.equal(await desktop.locator("#addon-dialog-title").textContent(), "Pawn");
    const pawnText = await desktop.locator("#addon-dialog-content").textContent();
    assert.match(pawnText, /1\\.3\\.8/);
    assert.match(pawnText, /no errors are remembered/i);
    assert.match(pawnText, /\\/pawn list Scale Name/);
    assert.match(pawnText, /copy the chosen built-in scale/i);
    assert.match(pawnText, /\\/pawn import/);
    assert.match(pawnText, /caps/);
    assert.equal(await desktop.locator('a[href="https://warperia.com/addon-wotlk/pawn/"]').count() > 0, true);
    await noOverflow(desktop, "Pawn details drawer");
'''
    text = replace_once(text, drawer_marker, drawer_addition, "Pawn drawer checks")
    BROWSER_TEST.write_text(text, encoding="utf-8")


def update_html() -> None:
    text = HTML.read_text(encoding="utf-8")
    text = re.sub(r'(\\?v=)[0-9]{8}-[a-z0-9-]+', r'\g<1>20260725-pawn-v1', text)
    text = replace_once(text, 'The catalog currently has sixteen addons.', 'The catalog currently has seventeen addons.', "noscript count")
    marker = '            <li><a href="https://warperia.com/addon-wotlk/outfitter/" target="_blank" rel="noopener">Outfitter ↗</a></li>\n'
    addition = marker + '            <li><a href="https://warperia.com/addon-wotlk/pawn/" target="_blank" rel="noopener">Pawn ↗</a></li>\n'
    text = replace_once(text, marker, addition, "Pawn fallback link")
    HTML.write_text(text, encoding="utf-8")


def write_icon() -> None:
    ICON.write_text('''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 128 128" role="img" aria-labelledby="title desc">
  <title id="title">Pawn</title>
  <desc id="desc">Two equipment cards balanced on a stat-weight scale.</desc>
  <rect x="8" y="8" width="112" height="112" rx="18" fill="#171b20" stroke="#a4a9a5" stroke-width="5"/>
  <path d="M64 25v66M39 96h50M48 103h32" fill="none" stroke="#dedcd6" stroke-width="6" stroke-linecap="round"/>
  <path d="M29 43h70" fill="none" stroke="#cf4e17" stroke-width="6" stroke-linecap="round"/>
  <path d="M37 43 25 69h24L37 43Zm54 0L79 69h24L91 43Z" fill="#414444" stroke="#dedcd6" stroke-width="4" stroke-linejoin="round"/>
  <path d="M24 70c2 10 24 10 26 0M78 70c2 10 24 10 26 0" fill="none" stroke="#cf4e17" stroke-width="5" stroke-linecap="round"/>
  <circle cx="64" cy="43" r="8" fill="#cf4e17" stroke="#dedcd6" stroke-width="3"/>
</svg>\n''', encoding="utf-8")


def main() -> None:
    update_catalog()
    update_validator()
    update_search_test()
    update_browser_test()
    update_html()
    write_icon()
    print("Applied Pawn 1.3.8 catalog migration")


if __name__ == "__main__":
    main()
