#!/usr/bin/env python3
"""Add the official Hellscream Discord join path before the AtlasLoot download post."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "addons.json"
CATALOG_JS = ROOT / "assets" / "addon-catalog.js"
HTML = ROOT / "guides" / "addons.html"
VALIDATOR = ROOT / "scripts" / "validate-addon-catalog.py"
SEARCH_TEST = ROOT / "tests" / "addon-search.test.js"
BROWSER_TEST = ROOT / "tests" / "addon-browser-smoke.cjs"

INVITE_URL = "https://discord.gg/pe69BfNZG5"
MESSAGE_URL = "https://discord.com/channels/608456284643262504/1328533521983340574/1469088948956434493"


def replace_once(text: str, old: str, new: str, label: str) -> str:
    if text.count(old) != 1:
        raise RuntimeError(f"{label}: expected one marker, found {text.count(old)}")
    return text.replace(old, new, 1)


def update_data() -> None:
    payload = json.loads(DATA.read_text(encoding="utf-8"))
    addon = next(item for item in payload["addons"] if item["id"] == "atlasloot-hellscream")
    addon["prerequisiteLinks"] = [
        {
            "url": INVITE_URL,
            "source": "Official Hellscream website",
            "label": "Join the Hellscream Discord ↗",
            "cardLabel": "Join Discord ↗",
            "notes": "Official invite linked from the Hellscream Connect page. Join the server and complete any required screening before opening the AtlasLoot post.",
        }
    ]
    addon["download"]["label"] = "Open the AtlasLoot Download Post ↗"
    addon["download"]["cardLabel"] = "Open Download Post ↗"
    addon["download"]["notes"] = "February 5, 2026 message containing the recommended AtlasLoot.7z package. Join the Hellscream Discord first if the post is inaccessible."
    addon["generalSetup"][0] = "Not in the Hellscream Discord yet? Use Join the Hellscream Discord below, complete any required screening, then open the AtlasLoot download post and download AtlasLoot.7z."
    addon["compatibility"]["lastReviewed"] = "2026-07-26"
    note = "The current official Hellscream Connect page links to Discord invite pe69BfNZG5; the guide presents that join step before the private download-post link."
    if note not in addon["compatibility"]["notes"]:
        addon["compatibility"]["notes"].append(note)
    DATA.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def update_catalog_js() -> None:
    text = CATALOG_JS.read_text(encoding="utf-8")
    old_card = '''      const actions = make("div", "addon-card-actions");
      const details = make("button", "addon-details-button", "Details");
      details.type = "button";
      details.setAttribute("aria-haspopup", "dialog");
      details.addEventListener("click", () => openDialog(addon.id, details, true));
      const download = make("a", "addon-download-link", "Download ↗");
      download.href = addon.download.url;
      download.target = "_blank";
      download.rel = "noopener";
      download.setAttribute("aria-label", `Download ${addon.name} from ${addon.download.source} (opens in a new tab)`);
      actions.append(details, download);
'''
    new_card = '''      const actions = make("div", "addon-card-actions");
      const details = make("button", "addon-details-button", "Details");
      details.type = "button";
      details.setAttribute("aria-haspopup", "dialog");
      details.addEventListener("click", () => openDialog(addon.id, details, true));
      actions.append(details);
      (addon.prerequisiteLinks || []).forEach((source) => {
        const link = make("a", "addon-download-link", source.cardLabel || source.label || `Open ${source.source} ↗`);
        link.href = source.url;
        link.target = "_blank";
        link.rel = "noopener";
        actions.append(link);
      });
      const download = make("a", "addon-download-link", addon.download.cardLabel || "Download ↗");
      download.href = addon.download.url;
      download.target = "_blank";
      download.rel = "noopener";
      download.setAttribute("aria-label", `Download ${addon.name} from ${addon.download.source} (opens in a new tab)`);
      actions.append(download);
'''
    text = replace_once(text, old_card, new_card, "card prerequisite links")

    old_dialog = '''      const actions = make("div", "addon-dialog-actions");
      const download = make("a", "addon-dialog-download", `Download from ${addon.download.source} ↗`);
      download.href = addon.download.url;
      download.target = "_blank";
      download.rel = "noopener";
      actions.append(download);
'''
    new_dialog = '''      const actions = make("div", "addon-dialog-actions");
      (addon.prerequisiteLinks || []).forEach((source) => {
        const link = make("a", "addon-download-link", source.label || `Open ${source.source} ↗`);
        link.href = source.url;
        link.target = "_blank";
        link.rel = "noopener";
        actions.append(link);
      });
      const download = make("a", "addon-dialog-download", addon.download.label || `Download from ${addon.download.source} ↗`);
      download.href = addon.download.url;
      download.target = "_blank";
      download.rel = "noopener";
      actions.append(download);
'''
    text = replace_once(text, old_dialog, new_dialog, "dialog prerequisite links")

    old_meta = '''      dialogContent.append(make("p", "addon-source-meta", `${addon.download.source} · ${addon.compatibility.downloadVersion} · ${addon.download.notes}`));
'''
    new_meta = '''      (addon.prerequisiteLinks || []).forEach((source) => {
        dialogContent.append(make("p", "addon-source-meta", `${source.source} · ${source.notes}`));
      });
      dialogContent.append(make("p", "addon-source-meta", `${addon.download.source} · ${addon.compatibility.downloadVersion} · ${addon.download.notes}`));
'''
    text = replace_once(text, old_meta, new_meta, "prerequisite source notes")
    CATALOG_JS.write_text(text, encoding="utf-8")


def update_validator() -> None:
    text = VALIDATOR.read_text(encoding="utf-8")
    marker = '''        for alternate in addon.get("alternateDownloads", []):
'''
    addition = '''        for prerequisite in addon.get("prerequisiteLinks", []):
            prerequisite_url = prerequisite.get("url", "")
            parsed_prerequisite = urlparse(prerequisite_url)
            if parsed_prerequisite.scheme != "https" or not parsed_prerequisite.netloc:
                fail(errors, f"{addon_id}: invalid prerequisite HTTPS URL {prerequisite_url!r}")
            if not prerequisite.get("source", "").strip() or not prerequisite.get("label", "").strip() or not prerequisite.get("notes", "").strip():
                fail(errors, f"{addon_id}: prerequisite links need source, label, and notes")
        for alternate in addon.get("alternateDownloads", []):
'''
    text = replace_once(text, marker, addition, "prerequisite validation")
    VALIDATOR.write_text(text, encoding="utf-8")


def update_search_test() -> None:
    text = SEARCH_TEST.read_text(encoding="utf-8")
    marker = '''assert.equal(atlasLoot.download.url, "https://discord.com/channels/608456284643262504/1328533521983340574/1469088948956434493");
'''
    addition = marker + '''assert.equal(atlasLoot.prerequisiteLinks[0].url, "https://discord.gg/pe69BfNZG5");
assert.equal(atlasLoot.prerequisiteLinks[0].label, "Join the Hellscream Discord ↗");
assert.equal(atlasLoot.download.label, "Open the AtlasLoot Download Post ↗");
assert.match(atlasLoot.generalSetup[0], /Join the Hellscream Discord/);
'''
    text = replace_once(text, marker, addition, "AtlasLoot join assertions")
    SEARCH_TEST.write_text(text, encoding="utf-8")


def update_browser_test() -> None:
    text = BROWSER_TEST.read_text(encoding="utf-8")
    marker = '''    assert.match(atlasLootText, /Stock AtlasLoot v5\\.11\\.04 fallback/);
'''
    addition = marker + '''    assert.match(atlasLootText, /Join the Hellscream Discord/);
    assert.match(atlasLootText, /Open the AtlasLoot Download Post/);
    assert.equal(await desktop.locator('a[href="https://discord.gg/pe69BfNZG5"]').count() > 0, true);
'''
    text = replace_once(text, marker, addition, "browser join assertions")
    BROWSER_TEST.write_text(text, encoding="utf-8")


def update_html() -> None:
    text = HTML.read_text(encoding="utf-8")
    text = text.replace("20260725-atlasloot-v1", "20260726-atlasloot-discord-v1")
    old = '            <li><a href="https://discord.com/channels/608456284643262504/1328533521983340574/1469088948956434493" target="_blank" rel="noopener">AtlasLoot Enhanced for Hellscream ↗</a></li>'
    new = '            <li>AtlasLoot Enhanced for Hellscream: <a href="https://discord.gg/pe69BfNZG5" target="_blank" rel="noopener">Join the Hellscream Discord ↗</a> · <a href="https://discord.com/channels/608456284643262504/1328533521983340574/1469088948956434493" target="_blank" rel="noopener">Open the download post ↗</a></li>'
    text = replace_once(text, old, new, "no-JavaScript AtlasLoot links")
    HTML.write_text(text, encoding="utf-8")


def main() -> None:
    update_data()
    update_catalog_js()
    update_validator()
    update_search_test()
    update_browser_test()
    update_html()


if __name__ == "__main__":
    main()
