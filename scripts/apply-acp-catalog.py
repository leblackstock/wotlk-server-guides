#!/usr/bin/env python3
"""Add Addon Control Panel 3.3.7 as an untested catalog entry."""
from __future__ import annotations

from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"{label}: expected one match, found {count}")
    return text.replace(old, new, 1)


def main() -> None:
    data_path = ROOT / "data/addons.json"
    payload = json.loads(data_path.read_text(encoding="utf-8"))
    addon_id = "addon-control-panel"
    if any(addon.get("id") == addon_id for addon in payload["addons"]):
        raise RuntimeError("ACP already exists in catalog")

    if not any(tag.get("id") == "addon-management" for tag in payload["tags"]):
        payload["tags"].append({
            "id": "addon-management",
            "label": "Addon Management",
            "group": "feature",
            "description": "Manages enabled addons, dependencies, grouped modules, protected addons, and saved addon sets.",
            "searchAliases": ["addon manager", "addon sets", "enable disable addons", "acp"],
            "order": 140,
        })

    if not any(item.get("id") == "addon-management" for item in payload["purposes"]):
        payload["purposes"].append({
            "id": "addon-management",
            "label": "Addon Management",
            "icon": "▦",
            "order": 150,
        })

    payload["lastReviewed"] = "2026-07-24"
    payload["addons"].append({
        "id": addon_id,
        "name": "Addon Control Panel",
        "aliases": ["ACP", "ACP 3.3.7", "AddonControlPanel"],
        "searchTerms": [
            "addon manager", "manage addons in game", "enable disable addons",
            "addon sets", "addon profiles", "dependencies", "embedded libraries",
            "memory usage", "protect addons", "reload ui"
        ],
        "summary": "Manage enabled addons in game, inspect grouped modules and dependencies, protect essentials, and switch saved addon sets after a UI reload.",
        "does": [
            "Adds an AddOns panel to the main menu and opens directly with /acp.",
            "Enables or disables addons, groups multi-part suites, and shows dependencies, compatibility, libraries, and memory use.",
            "Saves addon sets, protects selected addons from Disable All, and applies changes through a UI reload."
        ],
        "doesNot": [
            "Does not hot-load every addon safely; most changes still require ReloadUI.",
            "Does not have a documented Hellscream test result for this exact 3.3.7 build yet."
        ],
        "generalSetup": [
            "Open the exact CurseForge file page below and download ACP-3.3.7.zip, not the project's current Retail download.",
            "Remove or rename an older ACP folder, then install so Interface\\AddOns\\ACP\\ACP.toc is the final path.",
            "Enable Load out of date AddOns at character select if the 3.3.5a client flags the folder.",
            "Open Escape → AddOns or type /acp and review grouped addons, dependencies, and protected entries.",
            "Test one harmless enable/disable change and one saved set, reload, then check Swatter before relying on it."
        ],
        "tags": [
            "all-roles", "interface", "addon-management", "beginner-friendly",
            "verified-335-download", "not-tested-hellscream"
        ],
        "featuredTags": [
            "addon-management", "verified-335-download", "not-tested-hellscream"
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
        "recommendations": [{
            "audience": {"roles": ["tank", "healer", "dps"]},
            "importance": "recommended",
            "purposes": ["addon-management"],
            "summary": "Manage a large addon collection without returning to the character-select addon list for every change.",
            "reason": "ACP is especially useful on 3.3.5 installations with multi-part suites, many optional modules, or different addon sets for raiding, farming, and troubleshooting."
        }],
        "customizations": [],
        "compatibility": {
            "client": "3.3.5a",
            "hellscreamTested": False,
            "lastReviewed": "2026-07-24",
            "downloadVersion": "3.3.7",
            "verifiedDownload": True,
            "serverSensitive": False,
            "maintenanceState": "wrath-era",
            "notes": [
                "CurseForge lists ACP-3.3.7.zip as supporting WoW 3.3.5 and 4.0.1.",
                "The 3.3.7 file changelog reports a fix for a self-anchoring interface error.",
                "This exact build has not yet been tested on Hellscream, so compatibility is based on the file metadata rather than an in-game server test.",
                "Use the linked 3.3.7 file page. The main ACP project download now targets modern clients and is not the intended archive."
            ]
        },
        "download": {
            "url": "https://www.curseforge.com/wow/addons/acp/files/471104",
            "source": "CurseForge",
            "notes": "Exact file page for ACP-3.3.7.zip, listed for WoW 3.3.5 and 4.0.1."
        },
        "icon": {
            "path": "assets/addons/icons/addon-control-panel.svg",
            "alt": "Addon list panel with switches and a check mark"
        },
        "screenshots": [],
        "videos": [],
        "relatedGuides": []
    })
    data_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    icon_path = ROOT / "assets/addons/icons/addon-control-panel.svg"
    icon_path.write_text('''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 128 128" role="img" aria-labelledby="title desc">
  <title id="title">Addon Control Panel</title>
  <desc id="desc">A settings panel with addon rows, switches, and a confirmation check.</desc>
  <rect x="8" y="8" width="112" height="112" rx="18" fill="#171b20" stroke="#a4a9a5" stroke-width="5"/>
  <rect x="24" y="27" width="80" height="72" rx="10" fill="#13181b" stroke="#dedcd6" stroke-width="4"/>
  <path d="M34 43h28M34 63h28M34 83h28" stroke="#dedcd6" stroke-width="6" stroke-linecap="round"/>
  <rect x="72" y="36" width="23" height="13" rx="6.5" fill="#414444" stroke="#a4a9a5" stroke-width="2"/>
  <circle cx="88" cy="42.5" r="5" fill="#cf4e17"/>
  <rect x="72" y="56" width="23" height="13" rx="6.5" fill="#414444" stroke="#a4a9a5" stroke-width="2"/>
  <circle cx="79" cy="62.5" r="5" fill="#a4a9a5"/>
  <path d="M72 82l7 7 16-19" fill="none" stroke="#cf4e17" stroke-width="7" stroke-linecap="round" stroke-linejoin="round"/>
</svg>
''', encoding="utf-8")

    validator = ROOT / "scripts/validate-addon-catalog.py"
    text = validator.read_text(encoding="utf-8")
    text = replace_once(text, '    "auctioneer-suite",\n}', '    "auctioneer-suite",\n    "addon-control-panel",\n}', "validator addon set")
    validator.write_text(text, encoding="utf-8")

    search_test = ROOT / "tests/addon-search.test.js"
    text = search_test.read_text(encoding="utf-8")
    text = replace_once(
        text,
        '  ["auctioneer", "auctioneer-suite"]\n];',
        '  ["auctioneer", "auctioneer-suite"],\n  ["addon control", "addon-control-panel"],\n  ["acp", "addon-control-panel"]\n];',
        "search cases",
    )
    text = replace_once(text, 'assert.equal(ids("").length, 13);', 'assert.equal(ids("").length, 14);', "search count")
    insertion = '''
const acp = addons.find((addon) => addon.id === "addon-control-panel");
assert.equal(acp.compatibility.downloadVersion, "3.3.7");
assert.equal(acp.compatibility.hellscreamTested, false);
assert.equal(acp.compatibility.verifiedDownload, true);
assert.ok(acp.tags.includes("not-tested-hellscream"));
assert.equal(acp.download.url, "https://www.curseforge.com/wow/addons/acp/files/471104");
assert.match(acp.compatibility.notes.join(" "), /not yet been tested on Hellscream/);
const acpRole = core.recommendationFor(acp, state("", { role: ["dps"] }), catalog);
assert.equal(acpRole.importance, "recommended");
assert.deepEqual(acpRole.purposes, ["addon-management"]);

'''
    text = replace_once(text, "const parsedLegacy = core.parseUrlState(", insertion + "const parsedLegacy = core.parseUrlState(", "search assertions")
    search_test.write_text(text, encoding="utf-8")

    browser_test = ROOT / "tests/addon-browser-smoke.cjs"
    text = browser_test.read_text(encoding="utf-8")
    text = replace_once(text, 'count(), 13, "Default catalog should show thirteen addons"', 'count(), 14, "Default catalog should show fourteen addons"', "browser count")
    text = replace_once(text, 'assert.equal(await desktop.locator(".addon-card").count(), 13);', 'assert.equal(await desktop.locator(".addon-card").count(), 14);', "browser reset count")
    card_marker = '    assert.equal(await auctioneerCard.locator(".addon-card-tag").first().textContent(), "Auction House");\n'
    card_checks = card_marker + '''
    await desktop.locator("#addon-search-input").fill("addon manager");
    await desktop.waitForTimeout(80);
    assert.equal(await desktop.locator(".addon-card h2").first().textContent(), "Addon Control Panel");
    const acpCard = desktop.locator('.addon-card[data-addon-id="addon-control-panel"]');
    assert.equal(await acpCard.locator(".addon-card-tag").first().textContent(), "Addon Management");
    assert.equal(await acpCard.locator(".addon-card-tag", { hasText: "Not Yet Tested on Hellscream" }).count(), 1);
'''
    text = replace_once(text, card_marker, card_checks, "browser ACP card")
    drawer_marker = '    await desktop.goto(`${base}/guides/addons.html?class=paladin&spec=paladin-protection&role=tank`, { waitUntil: "networkidle" });\n'
    drawer_checks = '''    await desktop.goto(`${base}/guides/addons.html?role=dps#addon=addon-control-panel`, { waitUntil: "networkidle" });
    await desktop.waitForSelector("#addon-details-dialog[open]");
    assert.equal(await desktop.locator("#addon-dialog-title").textContent(), "Addon Control Panel");
    const acpText = await desktop.locator("#addon-dialog-content").textContent();
    assert.match(acpText, /3\.3\.7/);
    assert.match(acpText, /not yet been tested on Hellscream/);
    assert.match(acpText, /Recommended/);
    assert.equal(await desktop.locator('a[href="https://www.curseforge.com/wow/addons/acp/files/471104"]').count() > 0, true);
    await noOverflow(desktop, "ACP details drawer");

'''
    text = replace_once(text, drawer_marker, drawer_checks + drawer_marker, "browser ACP drawer")
    browser_test.write_text(text, encoding="utf-8")

    html_path = ROOT / "guides/addons.html"
    html = html_path.read_text(encoding="utf-8")
    html = html.replace("20260724-auctioneer-v1", "20260724-acp-v1")
    html = replace_once(html, "The catalog currently has thirteen addons.", "The catalog currently has fourteen addons.", "noscript count")
    link_marker = '            <li><a href="https://web.archive.org/web/20110112162840/http://auctioneeraddon.com/dl/Release/AuctioneerSuite-5.9.4961.zip" target="_blank" rel="noopener">Auctioneer Suite ↗</a></li>\n'
    acp_link = link_marker + '            <li><a href="https://www.curseforge.com/wow/addons/acp/files/471104" target="_blank" rel="noopener">Addon Control Panel ↗</a></li>\n'
    html = replace_once(html, link_marker, acp_link, "noscript ACP link")
    html_path.write_text(html, encoding="utf-8")

    print("ACP catalog migration applied.")


if __name__ == "__main__":
    main()
