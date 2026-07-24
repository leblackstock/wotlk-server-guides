#!/usr/bin/env python3
"""Add tested Auctioneer Suite 5.9.4961 and its complete module map."""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "addons.json"
GENERATED = ROOT / "assets" / "addon-catalog-data.js"
RENDERER = ROOT / "assets" / "addon-catalog.js"
CSS = ROOT / "assets" / "addon-catalog.css"
VALIDATOR = ROOT / "scripts" / "validate-addon-catalog.py"
UNIT = ROOT / "tests" / "addon-search.test.js"
BROWSER = ROOT / "tests" / "addon-browser-smoke.cjs"
HTML = ROOT / "guides" / "addons.html"
ICON = ROOT / "assets" / "addons" / "icons" / "auctioneer-suite.svg"
DOWNLOAD = "https://web.archive.org/web/20110112162840/http://auctioneeraddon.com/dl/Release/AuctioneerSuite-5.9.4961.zip"


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"{label}: expected one match, found {count}")
    return text.replace(old, new, 1)


MODULE_GROUPS = [
    {
        "label": "Main suite components",
        "items": [
            {"name": "Auc-Advanced", "description": "The core Auctioneer engine for scans, market data, pricing APIs, posting support, and module coordination."},
            {"name": "BeanCounter", "description": "Keeps a transaction journal for bids, purchases, postings, sales, auction mail, and item-specific profit history."},
            {"name": "Enchantrix", "description": "Estimates disenchanting, milling, and prospecting values and can assist with those item-processing workflows."},
            {"name": "Enchantrix-Barker", "description": "Builds chat advertisements for enchant services using Enchantrix material and pricing information."},
            {"name": "Informant", "description": "Adds item-tooltip information such as vendor values, item level, recipe or quest uses, and known vendor sources."},
            {"name": "Swatter", "description": "Captures Lua errors and stack traces so addon problems can be reviewed instead of disappearing into the fog."},
            {"name": "Stubby", "description": "Provides the shared loader, event, and hook framework used by the Auctioneer family of addons."},
            {"name": "SlideBar", "description": "Provides a shared movable tray for launcher and minimap-style buttons used by suite components."},
        ],
    },
    {
        "label": "Filters, matchers, and data",
        "items": [
            {"name": "Auc-Db", "description": "Internal database layer used to store and retrieve Auctioneer market information."},
            {"name": "Auc-ScanData", "description": "Stores and retrieves auction-house scan snapshots used by the core and statistic modules."},
            {"name": "Auc-Filter-Basic", "description": "Rejects invalid or unusable auction observations before they are accepted into market statistics."},
            {"name": "Auc-Filter-Outlier", "description": "Filters extreme price observations so unusual listings do not distort normal market calculations."},
            {"name": "Auc-Match-Undercut", "description": "Calculates competition-matching and undercut prices while respecting the configured minimums and limits."},
            {"name": "Auc-Stat-Classic", "description": "Provides the legacy Auctioneer Classic-style market-price estimate."},
            {"name": "Auc-Stat-Debug", "description": "Diagnostic statistic module intended for development and troubleshooting rather than normal pricing decisions."},
        ],
    },
    {
        "label": "Pricing and statistics",
        "items": [
            {"name": "Auc-Stat-Histogram", "description": "Calculates median and interquartile-range values from historical prices without discarding old observations."},
            {"name": "Auc-Stat-iLevel", "description": "Groups items by rarity, type, and item level, which is useful for random-suffix equipment with sparse exact matches."},
            {"name": "Auc-Stat-Purchased", "description": "Infers likely purchase prices when auctions disappear before their expected expiration time."},
            {"name": "Auc-Stat-Sales", "description": "Uses BeanCounter records to report actual historical purchase and sale prices."},
            {"name": "Auc-Stat-Simple", "description": "Produces simple averages and 3-, 7-, and 14-day exponential moving averages."},
            {"name": "Auc-Stat-StdDev", "description": "Uses the latest price observations and standard deviation to exclude outliers and estimate a normalized mean."},
            {"name": "Auc-Stat-WOWEcon", "description": "Imports price data from the separate WOWEcon addon when that optional source is installed."},
        ],
    },
    {
        "label": "Auction-house utilities",
        "items": [
            {"name": "Auc-Util-AHWindowControl", "description": "Coordinates Auctioneer tabs and controls with the Blizzard auction-house window."},
            {"name": "Auc-Util-Appraiser", "description": "Advanced posting interface that remembers prices, stack sizes, counts, competition settings, and batch-post queues."},
            {"name": "Auc-Util-AskPrice", "description": "Responds to configured chat price requests using Auctioneer's collected market data."},
            {"name": "Auc-Util-AutoMagic", "description": "Provides rule-based item handling and queues for vendor, disenchant, prospect, mill, and related workflows."},
            {"name": "Auc-Util-CompactUI", "description": "Replaces the browse list with a denser view, additional sorting, market comparisons, and price-level coloring."},
            {"name": "Auc-Util-EasyBuyout", "description": "Streamlines the normal auction buyout confirmation process."},
            {"name": "Auc-Util-FixAH", "description": "Applies compatibility fixes and workarounds for auction-house interface and API behavior."},
            {"name": "Auc-Util-Glypher", "description": "Analyzes glyph market and pricing opportunities for inscription sellers."},
            {"name": "Auc-Util-GlypherPost", "description": "Provides a specialized posting workflow for glyph inventories."},
            {"name": "Auc-Util-ItemSuggest", "description": "Suggests likely item names or matches while building auction-house searches."},
            {"name": "Auc-Util-PriceLevel", "description": "Compares and color-codes listings relative to the selected market-value statistic."},
            {"name": "Auc-Util-ScanButton", "description": "Adds auction-house controls for starting market scans."},
            {"name": "Auc-Util-ScanFinish", "description": "Handles notifications and follow-up behavior when a scan completes."},
            {"name": "Auc-Util-ScanProgress", "description": "Displays scan progress and current scan status."},
            {"name": "Auc-Util-ScanStart", "description": "Handles scan initialization, options, and start behavior."},
            {"name": "Auc-Util-SearchUI", "description": "Provides configurable bargain searches for resale, vendor profit, disenchanting, prospecting, and other deal types."},
            {"name": "Auc-Util-SimpleAuction", "description": "Provides a simpler posting tab for quickly listing singles or stacks."},
            {"name": "Auc-Util-VendMarkup", "description": "Calculates auction values from vendor price plus a configurable markup."},
        ],
    },
    {
        "label": "Shared support libraries",
        "items": [
            {"name": "Babylonian", "description": "Shared localization and translation library used by the suite."},
            {"name": "Configator", "description": "Shared configuration-window and control toolkit."},
            {"name": "DebugLib", "description": "Shared diagnostic and debugging support library."},
        ],
    },
]


def main() -> None:
    payload = json.loads(DATA.read_text(encoding="utf-8"))

    if not any(tag.get("id") == "auction-house" for tag in payload["tags"]):
        payload["tags"].append({
            "id": "auction-house",
            "label": "Auction House",
            "group": "feature",
            "description": "Scans, prices, posts, searches, or analyzes auction-house activity.",
            "searchAliases": ["auctioneer", "ah addon", "economy", "market", "pricing"],
            "order": 140,
        })
    if not any(purpose.get("id") == "economy" for purpose in payload["purposes"]):
        payload["purposes"].append({"id": "economy", "label": "Economy", "icon": "¤", "order": 140})

    if not any(addon.get("id") == "auctioneer-suite" for addon in payload["addons"]):
        payload["addons"].append({
            "id": "auctioneer-suite",
            "name": "Auctioneer Suite",
            "aliases": ["Auctioneer", "Auctioneer 5.9.4961", "AuctioneerSuite", "WhackyWallaby"],
            "searchTerms": [
                "auction house addon", "ah scanner", "market prices", "price database", "post auctions",
                "appraiser", "beancounter", "enchantrix", "informant", "deal finder", "sales history"
            ],
            "summary": "A complete auction-house toolkit for scanning, pricing, posting, deal searches, sales history, disenchant values, and detailed item information.",
            "does": [
                "Scans the Auction House and builds a local market-price database from observed listings.",
                "Adds advanced posting, compact browsing, bargain searches, transaction history, and pricing statistics.",
                "Bundles BeanCounter, Enchantrix, Informant, error reporting, and dozens of focused Auctioneer modules."
            ],
            "doesNot": [
                "Does not provide live server-wide prices before the player has collected enough scans.",
                "Does not make mixed Auctioneer versions safe; every suite folder should come from the same archive."
            ],
            "generalSetup": [
                "Download the exact AuctioneerSuite-5.9.4961 archive linked below.",
                "Extract every included folder into Interface\\AddOns; do not mix individual modules from other Auctioneer releases.",
                "At character select, enable Load out of date AddOns so this legacy compatibility build can load on the 3.3.5a client.",
                "Open the Auction House and collect scans over several days before trusting suggested market prices.",
                "Preserve the WTF folder and SavedVariables when reinstalling so BeanCounter records and accumulated price history survive."
            ],
            "tags": [
                "all-roles", "interface", "auction-house", "setup-required", "advanced",
                "verified-335-download", "tested-hellscream", "server-sensitive"
            ],
            "featuredTags": ["auction-house", "tested-hellscream", "setup-required"],
            "scope": {
                "classes": ["paladin", "warrior", "death-knight", "druid", "priest", "shaman", "mage", "warlock", "rogue", "hunter"],
                "specs": [],
                "roles": ["tank", "healer", "dps"],
                "activities": [],
                "universalClasses": True,
                "universalSpecs": True,
            },
            "recommendations": [{
                "audience": {"roles": ["tank", "healer", "dps"]},
                "importance": "recommended",
                "purposes": ["economy"],
                "summary": "Build a dependable local price history and gain powerful tools for buying, posting, and reviewing Auction House activity.",
                "reason": "Auctioneer is extremely capable for players who use the Auction House regularly, but its large suite and scan-dependent pricing are unnecessary for players who rarely trade."
            }],
            "customizations": [],
            "moduleGroups": MODULE_GROUPS,
            "compatibility": {
                "client": "3.3.5a (enable Load out of date AddOns)",
                "hellscreamTested": True,
                "hellscreamTestedDate": "2026-07-24",
                "lastReviewed": "2026-07-24",
                "downloadVersion": "5.9.4961",
                "verifiedDownload": True,
                "serverSensitive": True,
                "maintenanceState": "legacy-compatible",
                "notes": [
                    "Hellscream test reported July 24, 2026: the complete Auctioneer Suite 5.9.4961 installation works well during normal use in an established large-addon setup.",
                    "No specific addon conflict or Lua error was reported during that use.",
                    "This build is intentionally loaded as an out-of-date addon on the 3.3.5a client; that warning alone does not mean the tested archive is broken.",
                    "The suite contains many optional and internal modules. The overall installation passed normal use, but every module function was not individually isolated and tested.",
                    "Install all folders from the same archive. Mixing Auctioneer, BeanCounter, Enchantrix, or utility modules from other releases can create silent data and interface problems."
                ]
            },
            "download": {
                "url": DOWNLOAD,
                "source": "Auctioneer AddOn archive (Wayback Machine)",
                "notes": "Original AuctioneerSuite-5.9.4961.zip release archive preserved from auctioneeraddon.com."
            },
            "icon": {"path": "assets/addons/icons/auctioneer-suite.svg", "alt": "Auction gavel over stacked coins and a market chart"},
            "screenshots": [],
            "videos": [],
            "relatedGuides": []
        })
        payload["lastReviewed"] = "2026-07-24"
        DATA.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    ICON.parent.mkdir(parents=True, exist_ok=True)
    ICON.write_text('''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 128 128" role="img" aria-labelledby="title desc">
  <title id="title">Auctioneer Suite</title>
  <desc id="desc">An auction gavel above stacked coins and a rising market line.</desc>
  <rect x="8" y="8" width="112" height="112" rx="18" fill="#171b20" stroke="#a4a9a5" stroke-width="5"/>
  <path d="M23 91h82" stroke="#414444" stroke-width="5" stroke-linecap="round"/>
  <ellipse cx="40" cy="91" rx="18" ry="7" fill="#cf4e17" stroke="#dedcd6" stroke-width="3"/>
  <ellipse cx="40" cy="82" rx="18" ry="7" fill="#cf4e17" stroke="#dedcd6" stroke-width="3"/>
  <ellipse cx="40" cy="73" rx="18" ry="7" fill="#cf4e17" stroke="#dedcd6" stroke-width="3"/>
  <path d="M64 87l12-18 10 8 17-26" fill="none" stroke="#dedcd6" stroke-width="6" stroke-linecap="round" stroke-linejoin="round"/>
  <path d="M96 51h10v10" fill="none" stroke="#dedcd6" stroke-width="5" stroke-linecap="round" stroke-linejoin="round"/>
  <g transform="rotate(-35 55 42)"><rect x="28" y="32" width="50" height="17" rx="4" fill="#dedcd6" stroke="#414444" stroke-width="4"/><rect x="48" y="46" width="10" height="34" rx="4" fill="#a4a9a5" stroke="#414444" stroke-width="3"/></g>
</svg>\n''', encoding="utf-8")

    renderer = RENDERER.read_text(encoding="utf-8")
    if '"legacy-compatible"' not in renderer:
        renderer = replace_once(
            renderer,
            '    "old-unmaintained": "Old / unmaintained"\n',
            '    "old-unmaintained": "Old / unmaintained",\n    "legacy-compatible": "Legacy compatibility build"\n',
            "maintenance label",
        )
    if "function renderModuleGroups(addon)" not in renderer:
        module_renderer = '''    function renderModuleGroups(addon) {
      if (!Array.isArray(addon.moduleGroups) || !addon.moduleGroups.length) return null;
      const total = addon.moduleGroups.reduce((sum, group) => sum + (group.items || []).length, 0);
      const details = make("details", "addon-module-map");
      details.append(make("summary", "", `Suite module map (${total})`));
      const inner = make("div", "addon-module-map-inner");
      addon.moduleGroups.forEach((group) => {
        const section = make("section", "addon-module-group");
        section.append(make("h3", "", `${group.label} (${(group.items || []).length})`));
        const list = make("dl", "addon-module-list");
        (group.items || []).forEach((item) => {
          list.append(make("dt", "", item.name), make("dd", "", item.description));
        });
        section.append(list);
        inner.append(section);
      });
      details.append(inner);
      return details;
    }

'''
        renderer = replace_once(renderer, "    function renderDialog(addon) {\n", module_renderer + "    function renderDialog(addon) {\n", "module renderer")
    if "const moduleMap = renderModuleGroups(addon);" not in renderer:
        renderer = replace_once(
            renderer,
            '      const compatibility = make("section", "addon-dialog-section");\n',
            '      const moduleMap = renderModuleGroups(addon);\n      if (moduleMap) dialogContent.append(moduleMap);\n\n      const compatibility = make("section", "addon-dialog-section");\n',
            "module drawer insertion",
        )
    RENDERER.write_text(renderer, encoding="utf-8")

    css = CSS.read_text(encoding="utf-8")
    if ".addon-module-list" not in css:
        css = replace_once(
            css,
            ".addon-all-tags { display: flex; flex-wrap: wrap; gap: 6px; }\n",
            ".addon-all-tags { display: flex; flex-wrap: wrap; gap: 6px; }\n"
            ".addon-module-map-inner { display: grid; gap: 12px; }\n"
            ".addon-module-group { padding-top: 4px; }\n"
            ".addon-module-group + .addon-module-group { border-top: 1px solid var(--border-default); padding-top: 12px; }\n"
            ".addon-module-group h3 { margin: 0 0 8px; color: var(--text-strong); font-size: 14px; }\n"
            ".addon-module-list { display: grid; grid-template-columns: minmax(145px, .72fr) minmax(0, 1.8fr); margin: 0; gap: 0; }\n"
            ".addon-module-list dt, .addon-module-list dd { margin: 0; padding: 8px 0; border-top: 1px solid rgba(255,255,255,.055); font-size: 12px; }\n"
            ".addon-module-list dt { padding-right: 12px; color: var(--section-addons-soft); font-weight: 850; overflow-wrap: anywhere; }\n"
            ".addon-module-list dd { color: var(--text-muted); }\n",
            "module CSS",
        )
        css = replace_once(
            css,
            "  .addon-dialog-meta-grid { grid-template-columns: 1fr; }\n",
            "  .addon-dialog-meta-grid { grid-template-columns: 1fr; }\n  .addon-module-list { grid-template-columns: 1fr; }\n  .addon-module-list dt { padding-bottom: 2px; border-top: 1px solid rgba(255,255,255,.07); }\n  .addon-module-list dd { padding-top: 0; border-top: 0; }\n",
            "mobile module CSS",
        )
        CSS.write_text(css, encoding="utf-8")

    validator = VALIDATOR.read_text(encoding="utf-8")
    if '    "auctioneer-suite",\n' not in validator:
        validator = replace_once(validator, '    "chatter",\n}', '    "chatter",\n    "auctioneer-suite",\n}', "required addon")
    validator = validator.replace('TESTED_HELLSCREAM_ADDONS = {"questie", "skada", "chatter"}', 'TESTED_HELLSCREAM_ADDONS = {"questie", "skada", "chatter", "auctioneer-suite"}')
    if "moduleGroups" not in validator:
        module_validation = '''        module_names: list[str] = []
        for group in addon.get("moduleGroups", []):
            if not group.get("label", "").strip():
                fail(errors, f"{addon_id}: module group needs a label")
            for item in group.get("items", []):
                name = item.get("name", "").strip()
                description = item.get("description", "").strip()
                if not name or not description:
                    fail(errors, f"{addon_id}: every module needs a name and description")
                module_names.append(name)
        if len(module_names) != len(set(module_names)):
            fail(errors, f"{addon_id}: module names must be unique")
        if addon_id == "auctioneer-suite" and len(module_names) != 43:
            fail(errors, f"{addon_id}: expected complete 43-entry module map, found {len(module_names)}")

'''
        validator = replace_once(validator, '        unknown_tags = sorted(set(addon.get("tags", [])) - tag_by_id.keys())\n', module_validation + '        unknown_tags = sorted(set(addon.get("tags", [])) - tag_by_id.keys())\n', "module validation")
    VALIDATOR.write_text(validator, encoding="utf-8")

    html = HTML.read_text(encoding="utf-8")
    html = re.sub(r"202607\d{2}-[a-z0-9-]+-v\d+", "20260724-auctioneer-v1", html)
    html = html.replace("The catalog currently has twelve addons.", "The catalog currently has thirteen addons.")
    if DOWNLOAD not in html:
        html = replace_once(
            html,
            '            <li><a href="https://warperia.com/addon-wotlk/chatter/" target="_blank" rel="noopener">Chatter ↗</a></li>',
            '            <li><a href="https://warperia.com/addon-wotlk/chatter/" target="_blank" rel="noopener">Chatter ↗</a></li>\n            <li><a href="' + DOWNLOAD + '" target="_blank" rel="noopener">Auctioneer Suite ↗</a></li>',
            "noscript link",
        )
    HTML.write_text(html, encoding="utf-8")

    unit = UNIT.read_text(encoding="utf-8")
    if '["auction house", "auctioneer-suite"]' not in unit:
        unit = replace_once(
            unit,
            '  ["chat timestamps", "chatter"]\n];',
            '  ["chat timestamps", "chatter"],\n  ["auction house", "auctioneer-suite"],\n  ["auctioneer", "auctioneer-suite"]\n];',
            "search cases",
        )
    unit = unit.replace('assert.equal(ids("").length, 12);', 'assert.equal(ids("").length, 13);')
    if "const auctioneer = addons.find" not in unit:
        auctioneer_tests = '''const auctioneer = addons.find((addon) => addon.id === "auctioneer-suite");
assert.equal(auctioneer.compatibility.downloadVersion, "5.9.4961");
assert.equal(auctioneer.compatibility.hellscreamTested, true);
assert.equal(auctioneer.compatibility.hellscreamTestedDate, "2026-07-24");
assert.equal(auctioneer.download.url, "''' + DOWNLOAD + '''");
assert.equal(auctioneer.moduleGroups.length, 5);
assert.equal(auctioneer.moduleGroups.flatMap((group) => group.items).length, 43);
assert.ok(auctioneer.moduleGroups.flatMap((group) => group.items).some((item) => item.name === "BeanCounter" && /transaction journal/.test(item.description)));
assert.ok(auctioneer.moduleGroups.flatMap((group) => group.items).some((item) => item.name === "Auc-Util-Appraiser" && /Advanced posting/.test(item.description)));
const auctioneerRole = core.recommendationFor(auctioneer, state("", { role: ["dps"] }), catalog);
assert.equal(auctioneerRole.importance, "recommended");
assert.deepEqual(auctioneerRole.purposes, ["economy"]);

'''
        unit = replace_once(unit, "const parsedLegacy = core.parseUrlState(\n", auctioneer_tests + "const parsedLegacy = core.parseUrlState(\n", "auctioneer assertions")
    UNIT.write_text(unit, encoding="utf-8")

    browser = BROWSER.read_text(encoding="utf-8")
    browser = browser.replace("Default catalog should show twelve addons", "Default catalog should show thirteen addons")
    browser = browser.replace('.count(), 12, "Default catalog', '.count(), 13, "Default catalog', 1)
    browser = browser.replace('assert.equal(await desktop.locator(".addon-card").count(), 12);', 'assert.equal(await desktop.locator(".addon-card").count(), 13);')
    if 'data-addon-id="auctioneer-suite"' not in browser:
        search_marker = '    assert.equal(await chatterCard.locator(".addon-card-tag").first().textContent(), "Chat Enhancement");\n'
        auctioneer_search = search_marker + '''
    await desktop.locator("#addon-search-input").fill("auction house");
    await desktop.waitForTimeout(80);
    assert.equal(await desktop.locator(".addon-card h2").first().textContent(), "Auctioneer Suite");
    const auctioneerCard = desktop.locator('.addon-card[data-addon-id="auctioneer-suite"]');
    assert.equal(await auctioneerCard.locator(".addon-card-tag").first().textContent(), "Auction House");
'''
        browser = replace_once(browser, search_marker, auctioneer_search, "browser search")
        drawer_marker = '    await desktop.goto(`${base}/guides/addons.html?class=paladin&spec=paladin-protection&role=tank`, { waitUntil: "networkidle" });\n'
        auctioneer_drawer = '''    await desktop.goto(`${base}/guides/addons.html?role=dps#addon=auctioneer-suite`, { waitUntil: "networkidle" });
    await desktop.waitForSelector("#addon-details-dialog[open]");
    assert.equal(await desktop.locator("#addon-dialog-title").textContent(), "Auctioneer Suite");
    const auctioneerText = await desktop.locator("#addon-dialog-content").textContent();
    assert.match(auctioneerText, /5\.9\.4961/);
    assert.match(auctioneerText, /Load out of date AddOns/);
    const moduleMap = desktop.locator(".addon-module-map");
    assert.equal(await moduleMap.locator("summary").textContent(), "Suite module map (43)");
    await moduleMap.locator("summary").click();
    assert.equal(await moduleMap.locator(".addon-module-group").count(), 5);
    assert.equal(await moduleMap.locator("dt").count(), 43);
    assert.equal(await moduleMap.locator("dt", { hasText: "BeanCounter" }).count(), 1);
    assert.equal(await moduleMap.locator("dt", { hasText: "Auc-Util-Appraiser" }).count(), 1);
    assert.equal(await desktop.locator('a[href="''' + DOWNLOAD + '''"]').count() > 0, true);
    await noOverflow(desktop, "Auctioneer module drawer");

'''
        browser = replace_once(browser, drawer_marker, auctioneer_drawer + drawer_marker, "browser drawer")
    BROWSER.write_text(browser, encoding="utf-8")

    print("Auctioneer Suite catalog migration applied.")


if __name__ == "__main__":
    main()
