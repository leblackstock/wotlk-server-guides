#!/usr/bin/env python3
"""Render compact AH guide chrome, global search, and navigation data."""

from __future__ import annotations

import argparse
import html
import json
import re
import sys
from datetime import date
from pathlib import Path

from ah_guides import load_guide_manifest


ROOT = Path(__file__).resolve().parents[1]
GUIDES_DIR = ROOT / "guides"
HUB_PATH = ROOT / "auction-house.html"
MANIFEST_PATH = ROOT / "data" / "ah-guides.json"
NAV_DATA_PATH = ROOT / "assets" / "ah-guide-navigation-data.js"
GEM_FINDER_TEMPLATE_PATH = ROOT / "templates" / "ah-guide" / "gem-finder.html"
ASSET_VERSION = "20260810-ah-desktop-table-v2"
HUB_STYLE_VERSION = "20260810-ah-desktop-table-v2"
PAGE_SPECIFIC_ASSETS = {
    "jewelcrafting-gems-ah-price-guide.html": {
        "stylesheets": [("ah-gem-finder.css", "20260808-cut-gem-finder-v2")],
        "scripts": [("ah-gem-finder.js", "20260808-cut-gem-finder-v2")],
    },
}

UX_BLOCK = re.compile(
    r"<!-- AH_GUIDE_UX_START -->.*?<!-- AH_GUIDE_UX_END -->",
    re.DOTALL,
)
GEM_FINDER_BLOCK = re.compile(
    r'\s*<(?P<tag>section|details) class="ah-gem-finder"[^>]*data-ah-gem-finder.*?</(?P=tag)>',
    re.DOTALL,
)
HEADER_BLOCK = re.compile(r"<header(?:\s[^>]*)?>.*?</header>", re.DOTALL)
HEADER_INNER = re.compile(r"<header(?:\s[^>]*)?>(.*?)</header>", re.DOTALL)
NOTES_CONTENT = re.compile(
    r"<!-- AH_GUIDE_NOTES_CONTENT_START -->\s*(.*?)\s*"
    r"<!-- AH_GUIDE_NOTES_CONTENT_END -->",
    re.DOTALL,
)
OLD_JUMP_NAV = re.compile(r'<nav class="ah-jump-nav".*?</nav>', re.DOTALL)
SCRIPT_BLOCK = re.compile(
    r"\s*<!-- AH_GUIDE_SCRIPTS_START -->.*?<!-- AH_GUIDE_SCRIPTS_END -->",
    re.DOTALL,
)
HUB_GUIDE_BLOCK = re.compile(
    r"<!-- AH_GUIDE_CARDS_START -->.*?<!-- AH_GUIDE_CARDS_END -->",
    re.DOTALL,
)
LEGACY_SEARCH_SCRIPT = re.compile(
    r'\s*<script src="\.\./assets/ah-search\.js\?v=[^"]+" defer></script>',
    re.DOTALL,
)


def extract_notes(source: str, filename: str) -> str:
    existing = NOTES_CONTENT.search(source)
    if existing:
        return existing.group(1).strip()

    headers = list(HEADER_INNER.finditer(source))
    if len(headers) != 1:
        raise ValueError(f"{filename}: expected exactly one legacy header")
    inner = headers[0].group(1)
    starts = [
        index
        for token in (
            '<div class="note"',
            '<div class="prof-note"',
            '<div class="scope-note"',
            '<div class="legend"',
            "<!-- AH_BASELINE_NOTE_START -->",
        )
        if (index := inner.find(token)) >= 0
    ]
    if not starts:
        raise ValueError(f"{filename}: could not find pricing notes in the legacy header")
    notes = inner[min(starts) :].strip()
    return OLD_JUMP_NAV.sub("", notes).strip()


def search_icon(size: int) -> str:
    return (
        f'<svg viewBox="0 0 24 24" width="{size}" height="{size}" focusable="false">'
        '<circle cx="10.5" cy="10.5" r="5.75"></circle>'
        '<path d="m15 15 4.25 4.25"></path></svg>'
    )


def render_ux(guide: dict, notes: str) -> str:
    title = html.escape(guide["title"])
    description = html.escape(guide["description"])
    icon = html.escape(guide["icon"])
    page_feature = ""
    if guide["file"] == "jewelcrafting-gems-ah-price-guide.html":
        page_feature = f'\n\n{GEM_FINDER_TEMPLATE_PATH.read_text(encoding="utf-8").strip()}'
    return f'''<!-- AH_GUIDE_UX_START -->
<header class="ah-guide-hero">
  <div class="ah-guide-heading">
    <img class="ah-guide-page-icon" src="../assets/ah-guide-icons/{icon}" width="64" height="64" alt="">
    <div class="ah-guide-heading-copy">
      <span class="ah-guide-eyebrow">WotLK 3.3.5 · Auction House</span>
      <h1>{title}</h1>
      <p class="sub">{description}</p>
    </div>
  </div>
</header>

<section class="common ah-search-section ah-guide-search-section" aria-label="Auction House lookup">
  <div class="ah-search-heading">
    <span class="ah-search-mark" aria-hidden="true">{search_icon(22)}</span>
    <span>
      <span class="ah-search-eyebrow">Search every AH guide</span>
      <span class="ah-search-count" id="ah-search-count"></span>
    </span>
  </div>
  <label class="visually-hidden" for="ah-search-input">Search by Auction House item name</label>
  <div class="ah-search-input-wrap">
    <span class="ah-search-icon" aria-hidden="true">{search_icon(19)}</span>
    <input id="ah-search-input" class="ah-search-input" type="search"
      placeholder="Try Saronite Bar, Cardinal Ruby, or Frozen Orb…"
      autocomplete="off" autocapitalize="off" spellcheck="false"
      aria-describedby="ah-search-status" aria-controls="ah-search-results">
  </div>
  <nav class="ah-guide-major-nav" data-ah-major-nav aria-label="Jump to a major category"></nav>
  <p class="ah-search-status" id="ah-search-status" role="status" aria-live="polite" hidden></p>
  <ol class="ah-search-results" id="ah-search-results" hidden></ol>
</section>{page_feature}

<details class="common ah-guide-notes">
  <summary><span>Pricing notes &amp; legend</span><span class="ah-guide-notes-hint">Read before posting</span></summary>
  <div class="ah-guide-notes-content">
<!-- AH_GUIDE_NOTES_CONTENT_START -->
{notes}
<!-- AH_GUIDE_NOTES_CONTENT_END -->
  </div>
</details>
<!-- AH_GUIDE_UX_END -->'''


def render_scripts(guide: dict) -> str:
    extra_scripts = "".join(
        f'\n<script src="../assets/{html.escape(filename)}?v={html.escape(version)}" defer></script>'
        for filename, version in PAGE_SPECIFIC_ASSETS.get(guide["file"], {}).get("scripts", [])
    )
    return f'''<!-- AH_GUIDE_SCRIPTS_START -->
<script src="../assets/ah-search-index.js?v={ASSET_VERSION}" defer></script>
<script src="../assets/ah-guide-navigation-data.js?v={ASSET_VERSION}" defer></script>
<script src="../assets/ah-guide-navigation.js?v={ASSET_VERSION}" defer></script>
<script src="../assets/ah-search.js?v={ASSET_VERSION}" defer></script>
<script src="../assets/ah-source-notes.js?v={ASSET_VERSION}" defer></script>{extra_scripts}
<!-- AH_GUIDE_SCRIPTS_END -->'''


def transform_page(source: str, guide: dict, updated_date: str | None = None) -> str:
    filename = guide["file"]
    notes = extract_notes(source, filename)
    source = GEM_FINDER_BLOCK.sub("", source)
    ux = render_ux(guide, notes)
    if UX_BLOCK.search(source):
        source, count = UX_BLOCK.subn(ux, source, count=1)
    else:
        source, count = HEADER_BLOCK.subn(ux, source, count=1)
    if count != 1:
        raise ValueError(f"{filename}: expected exactly one guide UX insertion point")

    page_title = html.escape(f'{guide["title"]} AH Price Guide — WotLK 3.3.5 Low Pop')
    source, title_count = re.subn(r"<title>.*?</title>", f"<title>{page_title}</title>", source, count=1)
    if title_count != 1:
        raise ValueError(f"{filename}: expected exactly one title")

    body_open = re.search(r"<body\b[^>]*>", source)
    if not body_open:
        raise ValueError(f"{filename}: body is missing")
    body = body_open.group(0)
    body = re.sub(r'\sdata-guide-section="[^"]*"', "", body)
    body = re.sub(r'\sdata-ah-guide="[^"]*"', "", body)
    body = re.sub(r'\sdata-ah-root="[^"]*"', "", body)
    body = body[:-1] + (
        f' data-guide-section="auction-house" data-ah-guide="{html.escape(guide["id"])}"'
        ' data-ah-root="../">'
    )
    source = source[: body_open.start()] + body + source[body_open.end() :]

    source = re.sub(
        r"ah-guide-icons\.css\?v=[^\"\s]+",
        f"ah-guide-icons.css?v={ASSET_VERSION}",
        source,
        count=1,
    )
    if '../assets/style.css' not in source:
        stylesheet = f'  <link rel="stylesheet" href="../assets/style.css?v={ASSET_VERSION}">\n'
        marker = '  <link rel="stylesheet" href="../assets/ah-guide-icons.css'
        if marker not in source:
            raise ValueError(f"{filename}: AH guide stylesheet is missing")
        source = source.replace(marker, stylesheet + marker, 1)
    else:
        source = re.sub(
            r"style\.css\?v=[^\"\s]+",
            f"style.css?v={ASSET_VERSION}",
            source,
            count=1,
        )
    for filename, version in PAGE_SPECIFIC_ASSETS.get(guide["file"], {}).get("stylesheets", []):
        asset_pattern = rf"{re.escape(filename)}(?:\?v=[^\"\s]+)?"
        asset_value = f"{filename}?v={version}"
        if re.search(asset_pattern, source):
            source = re.sub(asset_pattern, asset_value, source, count=1)
        else:
            stylesheet = f'  <link rel="stylesheet" href="../assets/{asset_value}">\n'
            if source.count("</head>") != 1:
                raise ValueError(f"{guide['file']}: expected one head closing tag")
            source = source.replace("</head>", f"{stylesheet}</head>", 1)
    source = SCRIPT_BLOCK.sub("", source)
    source = LEGACY_SEARCH_SCRIPT.sub("", source)
    scripts = render_scripts(guide)
    if source.count("</body>") != 1:
        raise ValueError(f"{filename}: expected exactly one body closing tag")
    source = source.replace("</body>", f"{scripts}\n</body>", 1)

    footer_match = re.search(r"<footer>.*?Updated (\d{4}-\d{2}-\d{2})</footer>", source, re.DOTALL)
    if not footer_match:
        raise ValueError(f"{filename}: expected an Updated footer date")
    updated_date = updated_date or footer_match.group(1)
    footer = (
        f'<footer>WotLK 3.3.5 {html.escape(guide["title"])} AH Guide '
        f'• Hellscream / Garrosh • Created by Valdora • Updated {updated_date}</footer>'
    )
    source, footer_count = re.subn(r"<footer>.*?</footer>", footer, source, count=1, flags=re.DOTALL)
    if footer_count != 1:
        raise ValueError(f"{filename}: expected exactly one footer")
    return source


def navigation_asset(manifest: dict) -> str:
    payload = {
        "version": manifest["version"],
        "guides": {
            guide["id"]: {
                "title": guide["title"],
                "file": guide["file"],
                "navigation": guide["navigation"],
            }
            for guide in manifest["guides"]
        },
    }
    encoded = json.dumps(payload, ensure_ascii=False, separators=(",", ":"))
    return (
        "/* Generated by scripts/render-ah-guide-ux.py. Do not edit directly. */\n"
        f"window.AH_GUIDE_NAVIGATION={encoded};\n"
    )


def render_hub_cards(manifest: dict) -> str:
    guides_by_id = {guide["id"]: guide for guide in manifest["guides"]}
    grouped_guide_ids = {
        link["guide_id"]
        for card in manifest.get("hub_cards", [])
        if card["type"] == "multi-guide"
        for link in card["links"]
    }
    entries_by_group: dict[str, list[dict]] = {}
    for guide in manifest["guides"]:
        if guide["id"] in grouped_guide_ids:
            continue
        entries_by_group.setdefault(guide["group"], []).append(
            {"type": "guide", "order": guide["order"], "id": guide["id"], "guide": guide}
        )
    for card in manifest.get("hub_cards", []):
        entries_by_group.setdefault(card["group"], []).append(
            {"type": card["type"], "order": card["order"], "id": card["id"], "card": card}
        )
    for collection in manifest.get("collections", []):
        if not collection.get("group"):
            continue
        entries_by_group.setdefault(collection["group"], []).append(
            {
                "type": "collection",
                "order": collection["order"],
                "id": collection["id"],
                "collection": collection,
            }
        )

    group_badges = {
        "gathering": ("Materials", "gold"),
        "professions": ("Profession", "purple"),
        "drops": ("Drops", "green"),
        "collectibles": ("Collectibles", "purple"),
    }
    sections: list[str] = []
    for group in sorted(manifest["groups"], key=lambda item: int(item["order"])):
        cards: list[str] = []
        badge, badge_class = group_badges[group["id"]]
        entries = sorted(
            entries_by_group.get(group["id"], []),
            key=lambda item: (int(item["order"]), str(item["id"])),
        )
        for entry in entries:
            if entry["type"] == "guide":
                guide = entry["guide"]
                cards.append(
                    f'''        <a class="guide-card has-guide-icon" data-ah-guide-card="{html.escape(guide["id"])}" href="./guides/{html.escape(guide["file"])}"><img class="guide-card-icon" src="./assets/ah-guide-icons/{html.escape(guide["icon"])}" width="56" height="56" alt="">
          <span class="badge {badge_class}">{badge}</span>
          <span class="guide-title">{html.escape(guide["title"])}</span>
          <span class="guide-note">{html.escape(guide["description"])}</span>
          <span class="guide-action">Open guide →</span>
        </a>'''
                )
                continue

            if entry["type"] == "collection":
                collection = entry["collection"]
                cards.append(
                    f'''        <a class="guide-card has-guide-icon ah-hub-collection-card" data-ah-collection-card="{html.escape(collection["id"])}" href="./guides/{html.escape(collection["file"])}"><img class="guide-card-icon" src="./assets/ah-guide-icons/{html.escape(collection["icon"])}" width="56" height="56" alt="">
          <span class="badge {badge_class}">{html.escape(collection.get("badge", "Collection"))}</span>
          <span class="guide-title">{html.escape(collection["title"])}</span>
          <span class="guide-note">{html.escape(collection["description"])}</span>
          <span class="guide-action">Open collection →</span>
        </a>'''
                )
                continue

            card = entry["card"]
            card_classes = "guide-card has-guide-icon ah-hub-route-card"
            if card["type"] == "category-link":
                card_classes += " ah-hub-link-card"
            links: list[str] = []
            for link in card["links"]:
                guide = guides_by_id[link["guide_id"]]
                href = f'./guides/{html.escape(guide["file"])}'
                if link.get("category"):
                    href += f'#ah-category={html.escape(str(link["category"]))}'
                links.append(
                    f'''            <a class="ah-hub-card-chip" data-ah-guide-id="{html.escape(guide["id"])}" href="{href}">{html.escape(link["label"])} <span aria-hidden="true">→</span></a>'''
                )
            cards.append(
                f'''        <article class="{card_classes}" data-ah-hub-card="{html.escape(card["id"])}"><img class="guide-card-icon" src="./assets/ah-guide-icons/{html.escape(card["icon"])}" width="56" height="56" alt="">
          <span class="badge {badge_class}">{html.escape(card["badge"])}</span>
          <span class="guide-title">{html.escape(card["title"])}</span>
          <span class="guide-note">{html.escape(card["description"])}</span>
          <nav class="ah-hub-card-links" aria-label="{html.escape(card["title"])} destinations">
{chr(10).join(links)}
          </nav>
        </article>'''
            )

        compact = " compact-grid" if group["id"] in {"gathering", "drops"} else ""
        sections.append(
            f'''    <section class="common ah-guide-group" data-ah-guide-group="{html.escape(group["id"])}">
      <h2>{html.escape(group["title"])}</h2>
      <p class="small ah-guide-group-description">{html.escape(group["description"])}</p>
      <div class="guide-grid{compact}">
{chr(10).join(cards)}
      </div>
    </section>'''
        )
    return "<!-- AH_GUIDE_CARDS_START -->\n" + "\n\n".join(sections) + "\n<!-- AH_GUIDE_CARDS_END -->"


def transform_hub(source: str, manifest: dict) -> str:
    block = render_hub_cards(manifest)
    if HUB_GUIDE_BLOCK.search(source):
        source = HUB_GUIDE_BLOCK.sub(block, source, count=1)
    else:
        start_token = '    <section class="common">\n      <h2>Core Materials &amp; Professions</h2>'
        start = source.find(start_token)
        end = source.find("\n\n    <footer>", start)
        if start < 0 or end < 0:
            raise ValueError("auction-house.html: could not find the legacy AH guide-card block")
        source = source[:start] + block + source[end:]
    source = re.sub(
        r"browse all \d+ pricing guides",
        f'browse all {int(manifest["active_guide_count"])} pricing guides',
        source,
        count=1,
    )
    source = re.sub(
        r"style\.css\?v=[^\"\s]+",
        f"style.css?v={HUB_STYLE_VERSION}",
        source,
        count=1,
    )
    source = re.sub(
        r"ah-guide-icons\.css\?v=[^\"\s]+",
        f"ah-guide-icons.css?v={ASSET_VERSION}",
        source,
        count=1,
    )
    for asset in ("ah-search-index.js", "ah-search.js"):
        source = re.sub(
            rf"{re.escape(asset)}\?v=[^\"\s]+",
            f"{asset}?v={HUB_STYLE_VERSION}",
            source,
            count=1,
        )
    return source


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Fail when guide UX is stale")
    parser.add_argument(
        "--updated-date",
        help="Set the Updated footer date on every rendered guide (YYYY-MM-DD)",
    )
    args = parser.parse_args()

    if args.updated_date:
        date.fromisoformat(args.updated_date)

    manifest = load_guide_manifest(MANIFEST_PATH)
    if len(manifest["guides"]) != int(manifest["active_guide_count"]):
        raise ValueError("AH guide manifest active count does not match its guide list")

    stale: list[str] = []
    updates: list[tuple[Path, str]] = []
    for guide in manifest["guides"]:
        path = GUIDES_DIR / guide["file"]
        if not path.is_file():
            raise FileNotFoundError(path)
        source = path.read_text(encoding="utf-8")
        expected = transform_page(source, guide, updated_date=args.updated_date)
        if expected != source:
            stale.append(str(path.relative_to(ROOT)))
            updates.append((path, expected))

    expected_asset = navigation_asset(manifest)
    current_asset = NAV_DATA_PATH.read_text(encoding="utf-8") if NAV_DATA_PATH.is_file() else ""
    if current_asset != expected_asset:
        stale.append(str(NAV_DATA_PATH.relative_to(ROOT)))
        updates.append((NAV_DATA_PATH, expected_asset))

    hub_source = HUB_PATH.read_text(encoding="utf-8")
    expected_hub = transform_hub(hub_source, manifest)
    if expected_hub != hub_source:
        stale.append(str(HUB_PATH.relative_to(ROOT)))
        updates.append((HUB_PATH, expected_hub))

    if args.check and stale:
        for label in stale:
            print(f"Stale AH guide UX: {label}", file=sys.stderr)
        return 1

    for path, content in updates:
        path.write_text(content, encoding="utf-8", newline="\n")
    if stale:
        print("Updated AH guide UX in:")
        for label in stale:
            print(f"- {label}")
    else:
        print("AH guide UX is current.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
