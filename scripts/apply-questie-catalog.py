#!/usr/bin/env python3
"""Add the tested Questie 3.3.5a record and its catalog support files."""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "addons.json"
VALIDATOR = ROOT / "scripts" / "validate-addon-catalog.py"
HTML = ROOT / "guides" / "addons.html"
UNIT = ROOT / "tests" / "addon-search.test.js"
BROWSER = ROOT / "tests" / "addon-browser-smoke.cjs"
ICON = ROOT / "assets" / "addons" / "icons" / "questie.svg"


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"Expected exactly one {label} match, found {count}")
    return text.replace(old, new, 1)


payload = json.loads(DATA.read_text(encoding="utf-8"))
if any(addon.get("id") == "questie" for addon in payload.get("addons", [])):
    raise RuntimeError("Questie already exists in the catalog")

payload["lastReviewed"] = "2026-07-23"

if not any(tag.get("id") == "quest-tracking" for tag in payload["tags"]):
    payload["tags"].append(
        {
            "id": "quest-tracking",
            "label": "Quest Tracking",
            "group": "feature",
            "description": "Shows quest starts, turn-ins, objectives, progress, or related map information.",
            "searchAliases": ["quest tracker", "quest helper", "quest objectives"],
            "order": 120,
        }
    )

if not any(purpose.get("id") == "leveling" for purpose in payload["purposes"]):
    payload["purposes"].append(
        {
            "id": "leveling",
            "label": "Leveling",
            "icon": "↟",
            "order": 120,
        }
    )

all_classes = [
    "paladin",
    "warrior",
    "death-knight",
    "druid",
    "priest",
    "shaman",
    "mage",
    "warlock",
    "rogue",
    "hunter",
]

payload["addons"].append(
    {
        "id": "questie",
        "name": "Questie",
        "aliases": ["Questie-335", "Quest Helper"],
        "searchTerms": [
            "quest helper",
            "quest tracker",
            "quest markers",
            "quest objectives",
            "quest givers",
            "turn ins",
            "leveling guide",
            "map quests",
        ],
        "summary": "Shows quest givers, turn-ins, objectives, progress, and searchable quest information on the map and tracker.",
        "does": [
            "Shows quest start, turn-in, and objective notes on the map and minimap.",
            "Expands quest tracking and adds useful quest, NPC, object, and party-progress tooltips.",
            "Provides waypoints, zone quest lists, journey history, and a searchable quest database.",
        ],
        "doesNot": [
            "Does not guarantee accurate markers for custom, moved, or modified Hellscream quests.",
            "Does not replace reading quest text when an objective or script behaves differently on the server.",
        ],
        "generalSetup": [
            "Install the 9.6.2-335 archive so Questie-335.toc sits directly inside Interface\\AddOns\\Questie-335.",
            "Enable Questie-335 at character select and reload the interface.",
            "Left-click the minimap button for settings and adjust map or minimap note density.",
            "Right-click the minimap button for journey, zone quest, and search tools.",
        ],
        "tags": [
            "all-roles",
            "questing",
            "interface",
            "map",
            "leveling",
            "daily-weekly-quests",
            "quest-tracking",
            "beginner-friendly",
            "verified-335-download",
            "tested-hellscream",
            "server-sensitive",
        ],
        "featuredTags": ["quest-tracking", "leveling", "map"],
        "scope": {
            "classes": all_classes,
            "specs": [],
            "roles": ["tank", "healer", "dps"],
            "activities": ["leveling", "daily-weekly-quests"],
            "universalClasses": True,
            "universalSpecs": True,
        },
        "recommendations": [
            {
                "audience": {"activities": ["leveling"]},
                "importance": "essential",
                "purposes": ["leveling"],
                "summary": "See quest givers, turn-ins, objectives, and progress while leveling.",
                "reason": "Questie removes much of the blind searching from standard leveling. Version 9.6.2-335 completed several Hellscream quests without Lua errors during a focused test.",
            }
        ],
        "customizations": [],
        "compatibility": {
            "client": "3.3.5a",
            "hellscreamTested": True,
            "hellscreamTestedDate": "2026-07-23",
            "lastReviewed": "2026-07-23",
            "downloadVersion": "9.6.2-335",
            "verifiedDownload": True,
            "serverSensitive": True,
            "maintenanceState": "maintained-port",
            "notes": [
                "Hellscream test on July 23, 2026: the addon loaded normally, several standard quests were completed, and Swatter recorded no Lua errors.",
                "The test environment included only Questie and Swatter, so broader addon compatibility and conflict testing is not yet confirmed.",
                "Custom quests, party progress sharing, and large addon combinations remain unverified.",
            ],
        },
        "download": {
            "url": "https://warperia.com/addon-wotlk/questie/",
            "source": "Warperia",
            "notes": "Use the Wrath of the Lich King 3.3.5 download labeled 9.6.2-335.",
        },
        "icon": {
            "path": "assets/addons/icons/questie.svg",
            "alt": "Quest marker with an exclamation point",
        },
        "screenshots": [],
        "videos": [],
        "relatedGuides": [],
    }
)

DATA.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

validator = VALIDATOR.read_text(encoding="utf-8")
validator = replace_once(
    validator,
    '    "ratingbuster",\n}',
    '    "ratingbuster",\n    "questie",\n}\nTESTED_HELLSCREAM_ADDONS = {"questie"}',
    "validator addon set",
)
validator = replace_once(
    validator,
    '    if set(addon_ids) != REQUIRED_ADDONS or len(addons) != 9:\n        fail(errors, f"Launch catalog must contain exactly the nine approved addons; found {addon_ids!r}")',
    '    if set(addon_ids) != REQUIRED_ADDONS or len(addons) != len(REQUIRED_ADDONS):\n        fail(errors, f"Catalog must contain exactly the approved addons; found {addon_ids!r}")',
    "validator count",
)
validator = replace_once(
    validator,
    '        compatibility = addon.get("compatibility", {})\n        if compatibility.get("hellscreamTested"):\n            fail(errors, f"{addon_id}: Hellscream-tested claim lacks documented launch evidence")\n        if compatibility.get("lastReviewed") != payload.get("lastReviewed"):\n            fail(errors, f"{addon_id}: last-reviewed date must match catalog review date")',
    '        compatibility = addon.get("compatibility", {})\n        if compatibility.get("hellscreamTested"):\n            if addon_id not in TESTED_HELLSCREAM_ADDONS:\n                fail(errors, f"{addon_id}: Hellscream-tested claim lacks documented evidence")\n            if "tested-hellscream" not in addon.get("tags", []):\n                fail(errors, f"{addon_id}: Hellscream-tested record needs the tested-hellscream tag")\n            if not re.fullmatch(r"\\d{4}-\\d{2}-\\d{2}", compatibility.get("hellscreamTestedDate", "")):\n                fail(errors, f"{addon_id}: Hellscream-tested record needs an ISO test date")\n        if not re.fullmatch(r"\\d{4}-\\d{2}-\\d{2}", compatibility.get("lastReviewed", "")):\n            fail(errors, f"{addon_id}: last-reviewed date must use YYYY-MM-DD")',
    "validator compatibility rules",
)
VALIDATOR.write_text(validator, encoding="utf-8")

html = HTML.read_text(encoding="utf-8")
html = html.replace("20260722-addons-v2", "20260723-questie-v1")
html = replace_once(html, "The full catalog still has nine launch addons.", "The catalog currently has ten addons.", "noscript count")
html = replace_once(
    html,
    '            <li><a href="https://warperia.com/addon-wotlk/ratingbuster/" target="_blank" rel="noopener">RatingBuster ↗</a></li>',
    '            <li><a href="https://warperia.com/addon-wotlk/ratingbuster/" target="_blank" rel="noopener">RatingBuster ↗</a></li>\n            <li><a href="https://warperia.com/addon-wotlk/questie/" target="_blank" rel="noopener">Questie ↗</a></li>',
    "noscript Questie link",
)
HTML.write_text(html, encoding="utf-8")

unit = UNIT.read_text(encoding="utf-8")
unit = replace_once(
    unit,
    '  ["969 trainer", "protection-is-surprisingly-stupendous"]',
    '  ["969 trainer", "protection-is-surprisingly-stupendous"],\n  ["questi", "questie"],\n  ["quest helper", "questie"]',
    "search cases",
)
unit = replace_once(unit, 'assert.equal(ids("").length, 9);', 'assert.equal(ids("").length, 10);', "unit addon count")
unit = replace_once(
    unit,
    'assert.equal(ids("", { profession: ["alchemy"] }).length, 0);',
    'assert.equal(ids("", { profession: ["alchemy"] }).length, 0);\n\nconst questie = addons.find((addon) => addon.id === "questie");\nassert.ok(ids("", { activity: ["leveling"] }).includes("questie"));\nconst questieLeveling = core.recommendationFor(questie, state("", { activity: ["leveling"] }), catalog);\nassert.equal(questieLeveling.importance, "essential");\nassert.deepEqual(questieLeveling.purposes, ["leveling"]);\nassert.equal(questie.compatibility.downloadVersion, "9.6.2-335");\nassert.equal(questie.compatibility.hellscreamTested, true);\nassert.equal(questie.compatibility.hellscreamTestedDate, "2026-07-23");\nassert.ok(questie.tags.includes("tested-hellscream"));',
    "Questie unit assertions",
)
UNIT.write_text(unit, encoding="utf-8")

browser = BROWSER.read_text(encoding="utf-8")
browser = browser.replace('count(), 9, "Default catalog should show nine addons"', 'count(), 10, "Default catalog should show ten addons"')
browser = replace_once(browser, 'assert.equal(await desktop.locator(".addon-card").count(), 9);', 'assert.equal(await desktop.locator(".addon-card").count(), 10);', "browser restored count")
browser = replace_once(
    browser,
    '    await desktop.locator("#addon-search-input").fill("healbt");\n    await desktop.waitForTimeout(80);\n    assert.equal(await desktop.locator(".addon-card h2").first().textContent(), "HealBot");',
    '    await desktop.locator("#addon-search-input").fill("healbt");\n    await desktop.waitForTimeout(80);\n    assert.equal(await desktop.locator(".addon-card h2").first().textContent(), "HealBot");\n\n    await desktop.goto(`${base}/guides/addons.html?activity=leveling`, { waitUntil: "networkidle" });\n    await desktop.waitForSelector(\'.addon-card[data-addon-id="questie"]\');\n    assert.match(await desktop.locator("#addon-context-banner").textContent(), /Leveling/);\n    assert.equal(await desktop.locator(".addon-card h2").first().textContent(), "Questie");\n    assert.equal(await desktop.locator(\'.addon-card[data-addon-id="questie"] .addon-badge-essential\').count(), 1);',
    "Questie browser assertions",
)
BROWSER.write_text(browser, encoding="utf-8")

ICON.parent.mkdir(parents=True, exist_ok=True)
ICON.write_text(
    '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64" role="img" aria-labelledby="title desc">
  <title id="title">Quest marker</title>
  <desc id="desc">A circular quest marker with an exclamation point over a folded map.</desc>
  <rect width="64" height="64" rx="14" fill="#101722"/>
  <path d="M12 17l13-5 14 5 13-5v35l-13 5-14-5-13 5z" fill="#273553" stroke="#8fa8f5" stroke-width="2" stroke-linejoin="round"/>
  <path d="M25 12v35M39 17v35" fill="none" stroke="#d4deff" stroke-opacity=".45" stroke-width="2"/>
  <circle cx="32" cy="29" r="15" fill="#18233a" stroke="#d4deff" stroke-width="2"/>
  <path d="M32 18v15" stroke="#f2cf56" stroke-width="7" stroke-linecap="round"/>
  <circle cx="32" cy="40" r="3.6" fill="#f2cf56"/>
</svg>
''',
    encoding="utf-8",
)

print("Questie catalog migration applied.")
