#!/usr/bin/env python3
"""Correct Addon Control Panel to the tested 3.3.5 Hellscream build."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "addons.json"
VALIDATOR = ROOT / "scripts" / "validate-addon-catalog.py"
SEARCH_TEST = ROOT / "tests" / "addon-search.test.js"
BROWSER_TEST = ROOT / "tests" / "addon-browser-smoke.cjs"
GUIDE = ROOT / "guides" / "addons.html"

WARPERIA_URL = "https://warperia.com/addon-wotlk/addon-control-panel/"


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"{label}: expected one occurrence, found {count}")
    return text.replace(old, new, 1)


def update_catalog() -> None:
    catalog = json.loads(DATA.read_text(encoding="utf-8"))
    addon = next((item for item in catalog["addons"] if item["id"] == "addon-control-panel"), None)
    if addon is None:
        raise RuntimeError("Addon Control Panel record not found")

    addon["aliases"] = ["ACP", "ACP 3.3.5", "AddonControlPanel"]
    addon["doesNot"] = [
        "Does not hot-load every addon safely; most changes still require ReloadUI.",
        "ACP 3.3.7 is not compatible with the 3.3.5a client.",
    ]
    addon["generalSetup"] = [
        "Download Addon Control Panel 3.3.5 from the WotLK page linked below.",
        "Remove or rename an older ACP folder, then install so Interface\\AddOns\\ACP\\ACP.toc is the final path.",
        "At character select, enable ACP and confirm the installed addon reports version 3.3.5.",
        "Open Escape → AddOns or type /acp and review grouped addons, dependencies, and protected entries.",
        "Create one saved set, toggle one harmless addon, reload the UI, and confirm both changes persist before relying on the setup.",
    ]
    addon["tags"] = ["tested-hellscream" if tag == "not-tested-hellscream" else tag for tag in addon["tags"]]
    addon["featuredTags"] = ["tested-hellscream" if tag == "not-tested-hellscream" else tag for tag in addon["featuredTags"]]
    addon["compatibility"] = {
        "client": "3.3.5a",
        "hellscreamTested": True,
        "hellscreamTestedDate": "2026-07-25",
        "lastReviewed": "2026-07-25",
        "downloadVersion": "3.3.5",
        "verifiedDownload": True,
        "serverSensitive": False,
        "maintenanceState": "wrath-era",
        "notes": [
            "Hellscream test reported July 25, 2026: Addon Control Panel 3.3.5 has been extensively tested and works on the server.",
            "ACP 3.3.7 is not compatible with the 3.3.5a client.",
            "Warperia identifies the linked download as Addon Control Panel version 3.3.5 for WotLK 3.3.5.",
        ],
    }
    addon["download"] = {
        "url": WARPERIA_URL,
        "source": "Warperia",
        "notes": "Addon Control Panel 3.3.5 download page for WotLK 3.3.5.",
    }

    DATA.write_text(json.dumps(catalog, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def update_validator() -> None:
    text = VALIDATOR.read_text(encoding="utf-8")
    old = 'TESTED_HELLSCREAM_ADDONS = {"questie", "skada", "chatter", "auctioneer-suite", "bartender4", "outfitter"}'
    new = 'TESTED_HELLSCREAM_ADDONS = {"questie", "skada", "chatter", "auctioneer-suite", "addon-control-panel", "bartender4", "outfitter"}'
    text = replace_once(text, old, new, "tested Hellscream set")
    VALIDATOR.write_text(text, encoding="utf-8")


def update_search_tests() -> None:
    text = SEARCH_TEST.read_text(encoding="utf-8")
    old = '''const acp = addons.find((addon) => addon.id === "addon-control-panel");
assert.equal(acp.compatibility.downloadVersion, "3.3.7");
assert.equal(acp.compatibility.hellscreamTested, false);
assert.equal(acp.compatibility.verifiedDownload, true);
assert.ok(acp.tags.includes("not-tested-hellscream"));
assert.equal(acp.download.url, "https://www.curseforge.com/wow/addons/acp/files/471104");
assert.match(acp.compatibility.notes.join(" "), /not yet been tested on Hellscream/);
const acpRole = core.recommendationFor(acp, state("", { role: ["dps"] }), catalog);
assert.equal(acpRole.importance, "recommended");
assert.deepEqual(acpRole.purposes, ["addon-management"]);'''
    new = '''const acp = addons.find((addon) => addon.id === "addon-control-panel");
assert.equal(acp.compatibility.downloadVersion, "3.3.5");
assert.equal(acp.compatibility.hellscreamTested, true);
assert.equal(acp.compatibility.hellscreamTestedDate, "2026-07-25");
assert.equal(acp.compatibility.verifiedDownload, true);
assert.ok(acp.tags.includes("tested-hellscream"));
assert.ok(!acp.tags.includes("not-tested-hellscream"));
assert.equal(acp.download.url, "https://warperia.com/addon-wotlk/addon-control-panel/");
assert.match(acp.compatibility.notes.join(" "), /extensively tested and works on the server/);
assert.match(acp.compatibility.notes.join(" "), /ACP 3\.3\.7 is not compatible/);
const acpRole = core.recommendationFor(acp, state("", { role: ["dps"] }), catalog);
assert.equal(acpRole.importance, "recommended");
assert.deepEqual(acpRole.purposes, ["addon-management"]);'''
    text = replace_once(text, old, new, "ACP search assertions")
    SEARCH_TEST.write_text(text, encoding="utf-8")


def update_browser_tests() -> None:
    text = BROWSER_TEST.read_text(encoding="utf-8")
    text = replace_once(
        text,
        'assert.equal(await acpCard.locator(".addon-card-tag", { hasText: "Not Yet Tested on Hellscream" }).count(), 1);',
        'assert.equal(await acpCard.locator(".addon-card-tag", { hasText: "Tested on Hellscream" }).count(), 1);',
        "ACP card tested tag",
    )
    old = '''    assert.match(acpText, /3\.3\.7/);
    assert.match(acpText, /not yet been tested on Hellscream/);
    assert.match(acpText, /Recommended/);
    assert.equal(await desktop.locator('a[href="https://www.curseforge.com/wow/addons/acp/files/471104"]').count() > 0, true);'''
    new = '''    assert.match(acpText, /3\.3\.5/);
    assert.match(acpText, /extensively tested and works on the server/);
    assert.match(acpText, /ACP 3\.3\.7 is not compatible/);
    assert.match(acpText, /Recommended/);
    assert.equal(await desktop.locator('a[href="https://warperia.com/addon-wotlk/addon-control-panel/"]').count() > 0, true);'''
    text = replace_once(text, old, new, "ACP details checks")
    BROWSER_TEST.write_text(text, encoding="utf-8")


def update_guide() -> None:
    text = GUIDE.read_text(encoding="utf-8")
    text = text.replace("20260724-outfitter-v1", "20260725-acp335-v1")
    text = replace_once(
        text,
        'href="https://www.curseforge.com/wow/addons/acp/files/471104"',
        f'href="{WARPERIA_URL}"',
        "ACP noscript source",
    )
    GUIDE.write_text(text, encoding="utf-8")


def main() -> None:
    update_catalog()
    update_validator()
    update_search_tests()
    update_browser_tests()
    update_guide()
    print("Corrected Addon Control Panel to tested version 3.3.5.")


if __name__ == "__main__":
    main()
