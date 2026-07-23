#!/usr/bin/env python3
"""Add the tested Skada Revisited record and update catalog regression coverage."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "addons.json"
VALIDATOR = ROOT / "scripts" / "validate-addon-catalog.py"
HTML = ROOT / "guides" / "addons.html"
UNIT = ROOT / "tests" / "addon-search.test.js"
BROWSER = ROOT / "tests" / "addon-browser-smoke.cjs"
ICON = ROOT / "assets" / "addons" / "icons" / "skada.svg"


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"{label}: expected one occurrence, found {count}")
    return text.replace(old, new, 1)


def ensure_tag(payload: dict, tag: dict) -> None:
    if not any(item.get("id") == tag["id"] for item in payload["tags"]):
        payload["tags"].append(tag)


def ensure_purpose(payload: dict, purpose: dict) -> None:
    if not any(item.get("id") == purpose["id"] for item in payload["purposes"]):
        payload["purposes"].append(purpose)


def main() -> int:
    payload = json.loads(DATA.read_text(encoding="utf-8"))
    if any(addon.get("id") == "skada" for addon in payload.get("addons", [])):
        print("Skada already present; migration is idempotent.")
        return 0

    payload["lastReviewed"] = "2026-07-23"
    ensure_tag(payload, {
        "id": "combat-meter",
        "label": "Combat Meter",
        "group": "feature",
        "description": "Records and analyzes damage, healing, threat, deaths, interrupts, dispels, and related combat data.",
        "searchAliases": ["damage meter", "dps meter", "healing meter", "combat analysis"],
        "order": 120
    })
    ensure_purpose(payload, {
        "id": "performance",
        "label": "Performance",
        "icon": "▥",
        "order": 120
    })

    payload["addons"].append({
        "id": "skada",
        "name": "Skada Revisited",
        "aliases": ["Skada", "Skada Damage Meter", "Skada Revisited 1.8.87"],
        "searchTerms": [
            "damage meter", "dps meter", "healing meter", "combat log", "deaths",
            "interrupts", "dispels", "threat meter", "absorbs", "damage taken"
        ],
        "summary": "A modular combat meter for damage, healing, threat, deaths, interrupts, dispels, mitigation, absorbs, and detailed fight review.",
        "does": [
            "Records damage, healing, absorbs, threat, deaths, interrupts, dispels, and other combat details.",
            "Separates fights into segments and provides player, spell, and target breakdowns.",
            "Supports configurable windows and modules for lightweight or detailed use."
        ],
        "doesNot": [
            "Does not prove that the highest meter number came from correct encounter play.",
            "Does not guarantee identical combat-log accuracy for every custom or unusually scripted encounter."
        ],
        "generalSetup": [
            "Remove older Skada folders before installing this build; do not run two Skada versions together.",
            "Install the archive so Interface\\AddOns\\Skada\\Skada.toc is the final path.",
            "Open Skada settings and enable only the modules and windows you actually use.",
            "Test fight segments, resets, threat, healing, deaths, interrupts, and report links in easy content first."
        ],
        "tags": [
            "all-roles", "combat", "raiding", "interface", "dungeons", "raids", "pvp",
            "combat-meter", "lightweight", "verified-335-download", "tested-hellscream", "server-sensitive"
        ],
        "featuredTags": ["combat-meter", "raids", "tested-hellscream"],
        "scope": {
            "classes": ["paladin", "warrior", "death-knight", "druid", "priest", "shaman", "mage", "warlock", "rogue", "hunter"],
            "specs": [],
            "roles": ["tank", "healer", "dps"],
            "activities": ["dungeons", "raids", "pvp"],
            "universalClasses": True,
            "universalSpecs": True
        },
        "recommendations": [
            {
                "audience": {"activities": ["dungeons", "raids", "pvp"]},
                "importance": "recommended",
                "purposes": ["performance"],
                "summary": "Review damage, healing, threat, deaths, interrupts, dispels, and fight breakdowns.",
                "reason": "Skada makes group performance and encounter mistakes easier to inspect without requiring a heavyweight modern meter."
            },
            {
                "audience": {"roles": ["tank", "healer", "dps"]},
                "importance": "recommended",
                "purposes": ["performance"],
                "summary": "Track the combat information most useful to your current role.",
                "reason": "Every combat role benefits from reviewing more than raw damage, including threat, healing, deaths, mitigation, interrupts, and dispels."
            }
        ],
        "customizations": [],
        "compatibility": {
            "client": "3.3.5a",
            "hellscreamTested": True,
            "hellscreamTestedDate": "2026-07-23",
            "lastReviewed": "2026-07-23",
            "downloadVersion": "1.8.87",
            "verifiedDownload": True,
            "serverSensitive": True,
            "maintenanceState": "maintained-port",
            "notes": [
                "Hellscream test reported July 23, 2026: Skada recorded combat successfully through many battles while a larger addon setup was enabled.",
                "No addon conflicts were observed or reported during that use.",
                "The exact companion-addon list and every module combination were not recorded, so compatibility with every possible setup is not claimed."
            ]
        },
        "download": {
            "url": "https://warperia.com/addon-wotlk/skada-revisited/",
            "source": "Warperia",
            "notes": "Use the Wrath of the Lich King 3.3.5 download labeled 1.8.87."
        },
        "icon": {
            "path": "assets/addons/icons/skada.svg",
            "alt": "Combat meter bars with a sword marker"
        },
        "screenshots": [],
        "videos": [],
        "relatedGuides": []
    })
    DATA.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")

    validator = VALIDATOR.read_text(encoding="utf-8")
    validator = replace_once(validator, '    "questie",\n}', '    "questie",\n    "skada",\n}', "validator approved addons")
    validator = replace_once(validator, 'TESTED_HELLSCREAM_ADDONS = {"questie"}', 'TESTED_HELLSCREAM_ADDONS = {"questie", "skada"}', "validator tested set")
    VALIDATOR.write_text(validator, encoding="utf-8", newline="\n")

    html = HTML.read_text(encoding="utf-8")
    html = html.replace("20260723-questie-v1", "20260723-skada-v1")
    html = replace_once(html, "The catalog currently has ten addons.", "The catalog currently has eleven addons.", "noscript count")
    questie_link = '            <li><a href="https://warperia.com/addon-wotlk/questie/" target="_blank" rel="noopener">Questie ↗</a></li>\n'
    skada_link = questie_link + '            <li><a href="https://warperia.com/addon-wotlk/skada-revisited/" target="_blank" rel="noopener">Skada Revisited ↗</a></li>\n'
    html = replace_once(html, questie_link, skada_link, "Skada noscript link")
    HTML.write_text(html, encoding="utf-8", newline="\n")

    unit = UNIT.read_text(encoding="utf-8")
    unit = replace_once(unit, '  ["quest helper", "questie"]\n];', '  ["quest helper", "questie"],\n  ["skadaa", "skada"],\n  ["dps meter", "skada"]\n];', "Skada fuzzy tests")
    unit = replace_once(unit, 'assert.equal(ids("").length, 10);', 'assert.equal(ids("").length, 11);', "unit catalog count")
    anchor = 'assert.ok(questie.tags.includes("tested-hellscream"));\n'
    addition = anchor + '\nconst skada = addons.find((addon) => addon.id === "skada");\nassert.ok(ids("", { activity: ["raids"] }).includes("skada"));\nassert.ok(ids("", { role: ["healer"] }).includes("skada"));\nconst skadaRaid = core.recommendationFor(skada, state("", { activity: ["raids"] }), catalog);\nassert.equal(skadaRaid.importance, "recommended");\nassert.deepEqual(skadaRaid.purposes, ["performance"]);\nassert.equal(skada.compatibility.downloadVersion, "1.8.87");\nassert.equal(skada.compatibility.hellscreamTested, true);\nassert.equal(skada.compatibility.hellscreamTestedDate, "2026-07-23");\nassert.ok(skada.tags.includes("tested-hellscream"));\n'
    unit = replace_once(unit, anchor, addition, "Skada unit assertions")
    UNIT.write_text(unit, encoding="utf-8", newline="\n")

    browser = BROWSER.read_text(encoding="utf-8")
    browser = browser.replace('count(), 10, "Default catalog should show ten addons"', 'count(), 11, "Default catalog should show eleven addons"')
    browser = replace_once(browser, '    assert.equal(await desktop.locator(".addon-card h2").first().textContent(), "HealBot");\n', '    assert.equal(await desktop.locator(".addon-card h2").first().textContent(), "HealBot");\n\n    await desktop.locator("#addon-search-input").fill("dps meter");\n    await desktop.waitForTimeout(80);\n    assert.equal(await desktop.locator(".addon-card h2").first().textContent(), "Skada Revisited");\n', "Skada browser search")
    raid_anchor = '    assert.equal(await desktop.locator(\'.addon-card[data-addon-id="questie"] .addon-badge-essential\').count(), 1);\n'
    raid_addition = raid_anchor + '\n    await desktop.goto(`${base}/guides/addons.html?activity=raids#addon=skada`, { waitUntil: "networkidle" });\n    await desktop.waitForSelector("#addon-details-dialog[open]");\n    assert.equal(await desktop.locator("#addon-dialog-title").textContent(), "Skada Revisited");\n    assert.match(await desktop.locator("#addon-dialog-content").textContent(), /1\\.8\\.87/);\n    assert.match(await desktop.locator("#addon-dialog-content").textContent(), /many battles/);\n    assert.match(await desktop.locator("#addon-dialog-content").textContent(), /No addon conflicts/);\n    assert.equal(await desktop.locator(\'a[href="https://warperia.com/addon-wotlk/skada-revisited/"]\').count() > 0, true);\n'
    browser = replace_once(browser, raid_anchor, raid_addition, "Skada browser details")
    browser = replace_once(browser, 'assert.equal(await desktop.locator(".addon-card").count(), 10);', 'assert.equal(await desktop.locator(".addon-card").count(), 11);', "browser reset count")
    BROWSER.write_text(browser, encoding="utf-8", newline="\n")

    ICON.parent.mkdir(parents=True, exist_ok=True)
    ICON.write_text('''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 128 128" role="img" aria-labelledby="title desc">
  <title id="title">Skada combat meter</title>
  <desc id="desc">Three combat meter bars with a small sword marker.</desc>
  <rect x="8" y="8" width="112" height="112" rx="18" fill="#171b20" stroke="#a4a9a5" stroke-width="5"/>
  <rect x="22" y="30" width="76" height="14" rx="7" fill="#cf4e17"/>
  <rect x="22" y="55" width="58" height="14" rx="7" fill="#dedcd6"/>
  <rect x="22" y="80" width="42" height="14" rx="7" fill="#a4a9a5"/>
  <path d="M94 48l8-8 8 8-7 7 10 10-7 7-10-10-7 7-8-8 13-13z" fill="#ebe9e3" stroke="#414444" stroke-width="3" stroke-linejoin="round"/>
</svg>\n''', encoding="utf-8", newline="\n")

    print("Added Skada Revisited 1.8.87 and updated catalog tests.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
