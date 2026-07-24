#!/usr/bin/env python3
"""Add Bartender4 as a tested Hellscream action-bar addon."""
from __future__ import annotations

from pathlib import Path
import json
import re

ROOT = Path(__file__).resolve().parents[1]


def replace_once(text: str, old: str, new: str, label: str) -> str:
    if old not in text:
        raise RuntimeError(f"{label} marker not found")
    return text.replace(old, new, 1)


def main() -> None:
    data_path = ROOT / "data/addons.json"
    payload = json.loads(data_path.read_text(encoding="utf-8"))
    addon_id = "bartender4"
    if any(addon.get("id") == addon_id for addon in payload["addons"]):
        raise RuntimeError("Bartender4 already exists in catalog")

    if not any(tag.get("id") == "action-bars" for tag in payload["tags"]):
        payload["tags"].append({
            "id": "action-bars",
            "label": "Action Bars",
            "group": "feature",
            "description": "Replaces, arranges, pages, hides, and configures player action bars and related controls.",
            "searchAliases": ["action bar", "hotbars", "button bars", "bartender"],
            "order": 150,
        })

    if not any(item.get("id") == "action-bars" for item in payload["purposes"]):
        payload["purposes"].append({
            "id": "action-bars",
            "label": "Action Bars",
            "icon": "▥",
            "order": 160,
        })

    payload["lastReviewed"] = "2026-07-24"
    payload["addons"].append({
        "id": addon_id,
        "name": "Bartender4",
        "aliases": ["Bartender 4", "BT4", "Bartender4 4.4.2"],
        "searchTerms": [
            "action bar addon", "best action bars", "hotbar replacement", "button bars",
            "move action bars", "hide action bars", "bar paging", "keybind mode",
            "stance bars", "pet bar", "vehicle bar", "possess bar"
        ],
        "summary": "Our highest-recommended action-bar addon for moving, resizing, paging, hiding, and configuring WoW action bars without replacing the rest of the interface.",
        "does": [
            "Replaces the default action-bar layout with movable and configurable bars, including bar size, scale, spacing, visibility, and paging options.",
            "Provides quick keybinding mode and flexible layouts for class abilities, consumables, professions, mounts, and utility buttons.",
            "Manages related bars such as pet, stance, bag, menu, and experience or reputation controls when enabled."
        ],
        "doesNot": [
            "Does not replace unit frames, raid frames, cooldown tracking, or encounter alerts.",
            "Vehicle action-bar behavior has not yet received focused Hellscream testing and should not be treated as fully verified."
        ],
        "generalSetup": [
            "Download the regular Bartender4-4.4.2-12-g94f3b58.zip package from the exact CurseForge file page below, not the nolib archive.",
            "Remove or rename an older Bartender4 folder, then install so Interface\\AddOns\\Bartender4\\Bartender4.toc is the final path.",
            "Type /bt4 or open Interface Options → AddOns → Bartender4, unlock bars, and arrange the layout before binding buttons.",
            "Use Bartender4 keybinding mode to bind buttons, then lock the bars and test paging, stance or pet bars, and combat visibility in easy content.",
            "Do additional testing in several vehicle encounters before relying on vehicle buttons, exit controls, or temporary action bars."
        ],
        "tags": [
            "all-roles", "interface", "action-bars", "beginner-friendly",
            "verified-335-download", "tested-hellscream"
        ],
        "featuredTags": ["action-bars", "verified-335-download", "tested-hellscream"],
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
        "recommendations": [{
            "audience": {"roles": ["tank", "healer", "dps"]},
            "importance": "recommended",
            "purposes": ["action-bars"],
            "summary": "The top action-bar recommendation for players who want a dependable, highly configurable replacement for the default bars.",
            "reason": "Bartender4 provides broad layout and binding control without forcing a complete UI replacement, and this exact build has worked on Hellscream alongside a large addon setup."
        }],
        "customizations": [],
        "compatibility": {
            "client": "3.3.5a",
            "hellscreamTested": True,
            "hellscreamTestedDate": "2026-07-24",
            "lastReviewed": "2026-07-24",
            "downloadVersion": "4.4.2-12-g94f3b58",
            "verifiedDownload": True,
            "serverSensitive": False,
            "maintenanceState": "wrath-era",
            "notes": [
                "Hellscream test reported July 24, 2026: Bartender4 worked during normal play with many other addons enabled.",
                "No addon conflicts were observed or reported during that use.",
                "The exact companion-addon list was not recorded, so compatibility with every possible addon combination is not claimed.",
                "Vehicle action bars still need focused testing across several vehicle encounters before vehicle behavior is considered fully verified.",
                "CurseForge lists the linked full package for WoW 3.3.5; use the regular archive rather than the nolib package."
            ]
        },
        "download": {
            "url": "https://www.curseforge.com/wow/addons/bartender4/files/439962",
            "source": "CurseForge",
            "notes": "Exact file page for the full Bartender4-4.4.2-12-g94f3b58.zip package supporting WoW 3.3.5."
        },
        "icon": {
            "path": "assets/addons/icons/bartender4.svg",
            "alt": "Three configurable action bars made of square ability buttons"
        },
        "screenshots": [],
        "videos": [],
        "relatedGuides": []
    })
    data_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    icon_path = ROOT / "assets/addons/icons/bartender4.svg"
    icon_path.write_text('''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 128 128" role="img" aria-labelledby="title desc">
  <title id="title">Bartender4</title>
  <desc id="desc">Three rows of configurable action-bar buttons with a highlighted center button.</desc>
  <rect x="8" y="8" width="112" height="112" rx="18" fill="#171b20" stroke="#a4a9a5" stroke-width="5"/>
  <g fill="#13181b" stroke="#dedcd6" stroke-width="3">
    <rect x="21" y="28" width="18" height="18" rx="3"/><rect x="45" y="28" width="18" height="18" rx="3"/><rect x="69" y="28" width="18" height="18" rx="3"/><rect x="93" y="28" width="18" height="18" rx="3"/>
    <rect x="21" y="55" width="18" height="18" rx="3"/><rect x="45" y="55" width="18" height="18" rx="3" fill="#cf4e17"/><rect x="69" y="55" width="18" height="18" rx="3"/><rect x="93" y="55" width="18" height="18" rx="3"/>
    <rect x="21" y="82" width="18" height="18" rx="3"/><rect x="45" y="82" width="18" height="18" rx="3"/><rect x="69" y="82" width="18" height="18" rx="3"/><rect x="93" y="82" width="18" height="18" rx="3"/>
  </g>
</svg>\n''', encoding="utf-8")

    validator = ROOT / "scripts/validate-addon-catalog.py"
    text = validator.read_text(encoding="utf-8")
    text = replace_once(text, '    "addon-control-panel",\n}', '    "addon-control-panel",\n    "bartender4",\n}', "validator required addons")
    text = replace_once(
        text,
        'TESTED_HELLSCREAM_ADDONS = {"questie", "skada", "chatter", "auctioneer-suite"}',
        'TESTED_HELLSCREAM_ADDONS = {"questie", "skada", "chatter", "auctioneer-suite", "bartender4"}',
        "validator tested addons",
    )
    validator.write_text(text, encoding="utf-8")

    search_test = ROOT / "tests/addon-search.test.js"
    text = search_test.read_text(encoding="utf-8")
    text = replace_once(
        text,
        '  ["acp", "addon-control-panel"]\n];',
        '  ["acp", "addon-control-panel"],\n  ["bartender", "bartender4"],\n  ["action bars", "bartender4"]\n];',
        "search cases",
    )
    text = replace_once(text, 'assert.equal(ids("").length, 14);', 'assert.equal(ids("").length, 15);', "search addon count")
    bartender_assertions = '''const bartender4 = addons.find((addon) => addon.id === "bartender4");
assert.equal(bartender4.compatibility.downloadVersion, "4.4.2-12-g94f3b58");
assert.equal(bartender4.compatibility.hellscreamTested, true);
assert.equal(bartender4.compatibility.hellscreamTestedDate, "2026-07-24");
assert.equal(bartender4.download.url, "https://www.curseforge.com/wow/addons/bartender4/files/439962");
assert.ok(bartender4.tags.includes("tested-hellscream"));
assert.match(bartender4.compatibility.notes.join(" "), /No addon conflicts/);
assert.match(bartender4.compatibility.notes.join(" "), /Vehicle action bars still need focused testing/);
const bartenderRole = core.recommendationFor(bartender4, state("", { role: ["dps"] }), catalog);
assert.equal(bartenderRole.importance, "recommended");
assert.deepEqual(bartenderRole.purposes, ["action-bars"]);
assert.match(bartenderRole.summary, /top action-bar recommendation/i);

'''
    text = replace_once(text, "const parsedLegacy = core.parseUrlState(", bartender_assertions + "const parsedLegacy = core.parseUrlState(", "search assertions")
    search_test.write_text(text, encoding="utf-8")

    browser_test = ROOT / "tests/addon-browser-smoke.cjs"
    text = browser_test.read_text(encoding="utf-8")
    text = replace_once(
        text,
        'count(), 14, "Default catalog should show fourteen addons"',
        'count(), 15, "Default catalog should show fifteen addons"',
        "browser initial count",
    )
    text = replace_once(
        text,
        'assert.equal(await desktop.locator(".addon-card").count(), 14);',
        'assert.equal(await desktop.locator(".addon-card").count(), 15);',
        "browser restored count",
    )
    acp_card_marker = '    assert.equal(await acpCard.locator(".addon-card-tag", { hasText: "Not Yet Tested on Hellscream" }).count(), 1);\n'
    bartender_card_checks = acp_card_marker + '''

    await desktop.locator("#addon-search-input").fill("action bars");
    await desktop.waitForTimeout(80);
    assert.equal(await desktop.locator(".addon-card h2").first().textContent(), "Bartender4");
    const bartenderCard = desktop.locator('.addon-card[data-addon-id="bartender4"]');
    assert.equal(await bartenderCard.locator(".addon-card-tag").first().textContent(), "Action Bars");
    assert.equal(await bartenderCard.locator(".addon-card-tag", { hasText: "Tested on Hellscream" }).count(), 1);
'''
    text = replace_once(text, acp_card_marker, bartender_card_checks, "browser Bartender card")

    drawer_marker = '    await desktop.goto(`${base}/guides/addons.html?class=paladin&spec=paladin-protection&role=tank`, { waitUntil: "networkidle" });\n'
    bartender_drawer_checks = '''    await desktop.goto(`${base}/guides/addons.html?role=dps#addon=bartender4`, { waitUntil: "networkidle" });
    await desktop.waitForSelector("#addon-details-dialog[open]");
    assert.equal(await desktop.locator("#addon-dialog-title").textContent(), "Bartender4");
    const bartenderText = await desktop.locator("#addon-dialog-content").textContent();
    assert.match(bartenderText, /4\.4\.2-12-g94f3b58/);
    assert.match(bartenderText, /No addon conflicts/);
    assert.match(bartenderText, /Vehicle action bars still need focused testing/);
    assert.match(bartenderText, /top action-bar recommendation/i);
    assert.equal(await desktop.locator('a[href="https://www.curseforge.com/wow/addons/bartender4/files/439962"]').count() > 0, true);
    await noOverflow(desktop, "Bartender4 details drawer");

'''
    text = replace_once(text, drawer_marker, bartender_drawer_checks + drawer_marker, "browser Bartender drawer")
    browser_test.write_text(text, encoding="utf-8")

    html_path = ROOT / "guides/addons.html"
    html = html_path.read_text(encoding="utf-8")
    html = re.sub(r'(?<=\?v=)[^"\']+', "20260724-bartender4-v1", html)
    html = replace_once(html, "The catalog currently has fourteen addons.", "The catalog currently has fifteen addons.", "noscript count")
    acp_link = '            <li><a href="https://www.curseforge.com/wow/addons/acp/files/471104" target="_blank" rel="noopener">Addon Control Panel ↗</a></li>\n'
    bartender_link = acp_link + '            <li><a href="https://www.curseforge.com/wow/addons/bartender4/files/439962" target="_blank" rel="noopener">Bartender4 ↗</a></li>\n'
    html = replace_once(html, acp_link, bartender_link, "noscript Bartender link")
    html_path.write_text(html, encoding="utf-8")


if __name__ == "__main__":
    main()
