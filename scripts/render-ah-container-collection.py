#!/usr/bin/env python3
"""Render the all-containers AH collection from existing canonical owners."""

from __future__ import annotations

import argparse
import html
import json
import re
import sys
import unicodedata
from collections import Counter
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
AUDIT_PATH = ROOT / "data" / "ah-container-audit.json"
CRAFTED_PATH = ROOT / "data" / "ah-crafted-sections.json"
VENDOR_PATH = ROOT / "data" / "ah-vendor-sections.json"
CONTAINER_PATH = ROOT / "data" / "ah-container-sections.json"
MANIFEST_PATH = ROOT / "data" / "ah-guides.json"
GUIDES_DIR = ROOT / "guides"
HUB_PATHS = (ROOT / "index.html", ROOT / "auction-house.html")
ASSET_VERSION = "20260808-container-collection-v2"
COLLECTION_LINK = (
    '<a class="library-hub-chip" data-ah-container-collection-link '
    'href="./guides/bags-containers-ah-guide.html">Bags</a>'
)
COLLECTION_LINK_PATTERN = re.compile(
    r'<a class="library-hub-chip" data-ah-container-collection-link[^>]*>.*?</a>'
)
HERBS_LINK_PATTERN = re.compile(
    r'(?P<indent>\s*)<a class="library-hub-chip" '
    r'href="\./guides/herbalism-herbs-ah-price-guide\.html">Herbs</a>'
)


BAG_FAMILIES = {
    0: ("General bag", "General bags", "general", "general"),
    1: ("Quiver", "Hunter ammo", "hunter", "quiver"),
    2: ("Ammo pouch", "Hunter ammo", "hunter", "ammo-pouch"),
    4: ("Soul shard bag", "Profession bags", "profession", "soul-shards"),
    8: ("Leatherworking bag", "Profession bags", "profession", "skinning-leatherworking"),
    16: ("Inscription bag", "Profession bags", "profession", "inscription"),
    32: ("Herb bag", "Profession bags", "profession", "herbs"),
    64: ("Enchanting bag", "Profession bags", "profession", "enchanting"),
    128: ("Engineering bag", "Profession bags", "profession", "engineering"),
    512: ("Jewelcrafting bag", "Profession bags", "profession", "jewelcrafting"),
    1024: ("Mining bag", "Profession bags", "profession", "mining"),
}

RESTRICTION_CHIPS = (
    ("general", "General"),
    ("enchanting", "Enchanting"),
    ("engineering", "Engineering"),
    ("herbs", "Herbs"),
    ("inscription", "Inscription"),
    ("jewelcrafting", "Jewelcrafting"),
    ("skinning-leatherworking", "Skinning / Leatherworking"),
    ("mining", "Mining"),
    ("soul-shards", "Soul Shards"),
    ("quiver", "Quiver"),
    ("ammo-pouch", "Ammo Pouch"),
)


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def item_slug(value: str) -> str:
    value = "".join(
        character
        for character in unicodedata.normalize("NFKD", value)
        if unicodedata.category(character) != "Mn"
    )
    value = re.sub(r"['’]", "", value.lower())
    value = value.replace("&", " and ")
    return re.sub(r"[^a-z0-9]+", "-", value).strip("-")


def merged_crafted_catalog(config: dict) -> dict[int, tuple[str, dict]]:
    catalog: dict[int, tuple[str, dict]] = {}
    defaults = config.get("catalog_defaults", {})
    profiles = config.get("price_profiles", {})
    for key, raw in config["catalog"].items():
        item = defaults | profiles.get(raw.get("profile"), {}) | raw
        item_id = int(item["item_id"])
        if item_id in catalog:
            raise ValueError(f"Duplicate crafted item ID {item_id}")
        catalog[item_id] = (key, item)
    return catalog


def indexed_catalog(config: dict) -> dict[int, tuple[str, dict]]:
    result: dict[int, tuple[str, dict]] = {}
    for key, item in config["catalog"].items():
        item_id = int(item["item_id"])
        if item_id in result:
            raise ValueError(f"Duplicate catalog item ID {item_id}")
        result[item_id] = (key, item)
    return result


def container_owners(config: dict) -> dict[int, tuple[str, str, dict]]:
    owners: dict[int, tuple[str, str, dict]] = {}
    for guide_file, guide in config["guides"].items():
        for section in guide["sections"]:
            for key in section["items"]:
                item = config["catalog"][key]
                item_id = int(item["item_id"])
                if item_id in owners:
                    raise ValueError(f"Duplicate container-section item ID {item_id}")
                owners[item_id] = (key, guide_file, item)
    return owners


def format_money(copper: int | None) -> str:
    if copper is None:
        return "—"
    if copper >= 10_000:
        copper = ((copper + 50) // 100) * 100
    gold, remainder = divmod(copper, 10_000)
    silver, copper = divmod(remainder, 100)
    parts: list[str] = []
    if gold:
        parts.append(f"{gold:,}g")
    if silver:
        parts.append(f"{silver}s")
    if copper or not parts:
        parts.append(f"{copper}c")
    return " ".join(parts)


def expansion_from_detail(detail: str) -> str:
    expansion = detail.partition(" • ")[0].strip()
    if expansion not in {"Classic", "Outland", "Wrath"}:
        raise ValueError(f"Could not derive expansion from detail: {detail!r}")
    return expansion


def build_rows() -> tuple[dict, list[dict]]:
    audit = load(AUDIT_PATH)
    crafted = merged_crafted_catalog(load(CRAFTED_PATH))
    vendors = indexed_catalog(load(VENDOR_PATH))
    section_owners = container_owners(load(CONTAINER_PATH))
    manifest = load(MANIFEST_PATH)
    guides = {guide["file"]: guide for guide in manifest["guides"]}
    collections = [
        collection
        for collection in manifest.get("collections", [])
        if collection["id"] == "bags-containers"
    ]
    if len(collections) != 1:
        raise ValueError("Expected exactly one bags-containers collection config")
    collection = collections[0]
    if collection.get("source_audit") != str(AUDIT_PATH.relative_to(ROOT)).replace("\\", "/"):
        raise ValueError("Container collection config points at the wrong audit")

    rows: list[dict] = []
    included = {
        int(item_id): item
        for item_id, item in audit["items"].items()
        if str(item["decision"]).startswith("included-")
    }
    for item_id, audited in included.items():
        source_type = audited["primary_source"]
        if source_type == "crafted":
            key, canonical = crafted[item_id]
            guide_file = audited["canonical_coverage"]["guide_file"]
            quick = int(canonical["quick_copper"])
            target = int(canonical["target_copper"])
            high = int(canonical["high_copper"])
            detail = str(canonical["detail"])
            expansion = expansion_from_detail(detail)
            source_detail = f'Crafted by {canonical["profession"]}'
            lower_label = "Quick"
        elif source_type == "vendor":
            key, canonical = vendors[item_id]
            guide_file = audited["canonical_coverage"]["guide_file"]
            quick = int(canonical["vendor_cost_copper"])
            target = int(canonical["target_copper"])
            high = None
            expansion = str(canonical["expansion"])
            source_detail = str(canonical["source_label"])
            lower_label = "Vendor cost"
        elif source_type in {"drop", "quest-reward"}:
            key, guide_file, canonical = section_owners[item_id]
            quick = int(canonical["quick_copper"])
            target = int(canonical["target_copper"])
            high = int(canonical["high_copper"])
            detail = str(canonical["detail"])
            expansion = expansion_from_detail(detail)
            source_detail = str(canonical["source"])
            lower_label = "Quick"
        else:
            raise ValueError(f"Unsupported primary source {source_type!r} for {item_id}")

        if guide_file not in guides:
            raise ValueError(f"Unknown canonical owner guide {guide_file!r} for {item_id}")
        if not quick <= target or (high is not None and not target <= high):
            raise ValueError(f"Invalid price order for {audited['name']} ({item_id})")
        family = BAG_FAMILIES.get(int(audited["bag_family"]))
        if family is None:
            raise ValueError(f"Unknown bag family {audited['bag_family']} for {item_id}")
        subtype, category_label, category_key, restriction_key = family
        rows.append(
            {
                "item_id": item_id,
                "name": audited["name"],
                "quality": audited["quality"],
                "capacity": int(audited["capacity"]),
                "subtype": subtype,
                "category": category_label,
                "category_key": category_key,
                "restriction_key": restriction_key,
                "expansion": expansion,
                "source_type": source_type,
                "source_label": {
                    "crafted": "Crafted",
                    "vendor": "Vendor",
                    "drop": "Drop",
                    "quest-reward": "Quest reward",
                }[source_type],
                "source_detail": source_detail,
                "quick_copper": quick,
                "lower_label": lower_label,
                "target_copper": target,
                "high_copper": high,
                "owner_guide": guides[guide_file]["title"],
                "owner_href": f'./{guide_file}#ah-item={item_slug(audited["name"])}',
                "canonical_key": key,
            }
        )

    expected = int(audit["summary"]["included_obtainable_auctionable_records"])
    if len(rows) != expected:
        raise ValueError(f"Expected {expected} included containers, built {len(rows)}")
    if len({row["item_id"] for row in rows}) != len(rows):
        raise ValueError("Container collection contains duplicate item IDs")
    rows.sort(key=lambda row: (-row["capacity"], -row["target_copper"], row["name"].casefold()))
    return collection, rows


def render_price(copper: int | None, label: str) -> str:
    if copper is None:
        return '<span class="container-price-empty" aria-label="Not applicable">—</span>'
    return (
        f'<span class="container-price">{html.escape(format_money(copper))}</span>'
        f'<span class="container-price-label">{html.escape(label)}</span>'
    )


def render_row(row: dict) -> str:
    high_value = "" if row["high_copper"] is None else str(row["high_copper"])
    return (
        f'<tr data-container-row data-item-id="{row["item_id"]}" '
        f'data-name="{html.escape(row["name"].casefold(), quote=True)}" '
        f'data-category="{row["category_key"]}" '
        f'data-subtype="{html.escape(row["subtype"], quote=True)}" '
        f'data-restriction="{row["restriction_key"]}" '
        f'data-source="{row["source_type"]}" '
        f'data-expansion="{row["expansion"].lower()}" '
        f'data-capacity="{row["capacity"]}" '
        f'data-target="{row["target_copper"]}" '
        f'data-quick="{row["quick_copper"]}" data-high="{high_value}">'
        '<td data-column="item" data-label="Item">'
        f'<a class="container-item-link" href="{html.escape(row["owner_href"], quote=True)}">'
        f'<strong class="q-{html.escape(row["quality"])}">{html.escape(row["name"])}</strong></a>'
        f'<span class="container-item-meta">Item {row["item_id"]} • {html.escape(row["quality"].title())}</span></td>'
        f'<td data-column="slots" data-label="Slots"><strong>{row["capacity"]}</strong></td>'
        f'<td data-column="type" data-label="Contents"><strong>{html.escape(row["subtype"])}</strong>'
        f'<span class="container-cell-note">{html.escape(row["category"])}</span></td>'
        f'<td data-column="expansion" data-label="Expansion">{html.escape(row["expansion"])}</td>'
        f'<td data-column="source" data-label="Source"><strong>{html.escape(row["source_label"])}</strong>'
        f'<span class="container-cell-note">{html.escape(row["source_detail"])}</span></td>'
        f'<td data-column="quick" data-label="Quick / Cost">{render_price(row["quick_copper"], row["lower_label"])}</td>'
        f'<td data-column="target" data-label="Target">{render_price(row["target_copper"], "Target")}</td>'
        f'<td data-column="high" data-label="High">{render_price(row["high_copper"], "High")}</td>'
        '<td data-column="owner" data-label="Canonical guide">'
        f'<a class="container-owner-link" href="{html.escape(row["owner_href"], quote=True)}">'
        f'{html.escape(row["owner_guide"])} <span aria-hidden="true">→</span></a></td></tr>'
    )


def render_page(collection: dict, rows: list[dict]) -> str:
    source_counts = Counter(row["source_type"] for row in rows)
    category_counts = Counter(row["category_key"] for row in rows)
    restriction_counts = Counter(row["restriction_key"] for row in rows)
    restriction_chips = "\n".join(
        f'          <button class="container-filter-chip" type="button" '
        f'data-container-restriction="{key}" aria-pressed="false">'
        f'<span>{html.escape(label)}</span>'
        f'<span class="container-filter-chip-count" data-container-chip-count>{restriction_counts[key]}</span>'
        f'</button>'
        for key, label in RESTRICTION_CHIPS
    )
    rendered_rows = "\n".join(render_row(row) for row in rows)
    today = date.today().isoformat()
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{html.escape(collection["title"])} AH Collection — WotLK 3.3.5 Low Pop</title>
  <link rel="icon" href="../assets/brand/hellscream-server-logo.ico" sizes="any">
  <link rel="icon" type="image/png" href="../assets/brand/hellscream-server-logo-32.png" sizes="32x32">
  <link rel="apple-touch-icon" href="../assets/brand/hellscream-server-logo-180.png">
  <link rel="stylesheet" href="../assets/style.css?v={ASSET_VERSION}">
  <link rel="stylesheet" href="../assets/ah-containers.css?v={ASSET_VERSION}">
</head>
<body data-guide-section="auction-house" data-ah-collection="bags-containers" data-ah-root="../">
  <div class="wrap" id="top">
    <nav class="site-nav ah-guide-nav" aria-label="Guide navigation">
      <a class="guide-hub-link" href="../index.html">Guide Hub</a>
      <a class="ah-hub-link" href="../auction-house.html">AH Hub</a>
      <span aria-current="page">Bags &amp; Containers</span>
    </nav>

    <header class="container-collection-hero">
      <img class="container-collection-icon" src="../assets/ah-guide-icons/{html.escape(collection["icon"])}" width="72" height="72" alt="">
      <div>
        <span class="container-collection-eyebrow">Auction House collection</span>
        <h1>{html.escape(collection["title"])}</h1>
        <p class="sub">{html.escape(collection["description"])}</p>
      </div>
    </header>

    <section class="container-summary-grid" aria-label="Container coverage summary">
      <div><strong>{len(rows)}</strong><span>auctionable containers</span></div>
      <div><strong>{category_counts["general"]}</strong><span>general bags</span></div>
      <div><strong>{category_counts["profession"]}</strong><span>profession bags</span></div>
      <div><strong>{category_counts["hunter"]}</strong><span>quivers and ammo pouches</span></div>
    </section>

    <aside class="container-method-note">
      <strong>* One collection, one price owner:</strong> This page reads the existing canonical profession and drop records. It does not maintain a second price list. Target is the recommended opening buyout; vendor rows show exact vendor cost instead of a Quick estimate and intentionally have no High band. Active listings never set these values.
    </aside>

    <section class="common container-browser" aria-labelledby="container-browser-heading">
      <div class="container-browser-heading">
        <div>
          <span class="container-browser-kicker">Compare all containers</span>
          <h2 id="container-browser-heading">Find the right capacity and contents</h2>
        </div>
        <p class="container-result-count" id="container-result-count" role="status" aria-live="polite">Showing {len(rows)} of {len(rows)} containers</p>
      </div>

      <form class="container-filters" data-container-filters>
        <div class="container-primary-controls">
          <label class="container-filter container-filter-search">
            <span>Search</span>
            <input id="container-search" type="search" placeholder="Bag or container name" autocomplete="off" spellcheck="false">
          </label>
          <label class="container-filter container-mobile-sort">
            <span>Sort by</span>
            <select id="container-mobile-sort">
              <option value="slots-desc">Slots: high to low</option>
              <option value="slots-asc">Slots: low to high</option>
              <option value="name-asc">Item: A to Z</option>
              <option value="name-desc">Item: Z to A</option>
              <option value="type-asc">Contents: A to Z</option>
              <option value="type-desc">Contents: Z to A</option>
              <option value="expansion-desc">Expansion: Wrath to Classic</option>
              <option value="expansion-asc">Expansion: Classic to Wrath</option>
              <option value="source-asc">Source: A to Z</option>
              <option value="source-desc">Source: Z to A</option>
              <option value="quick-desc">Quick / Cost: high to low</option>
              <option value="quick-asc">Quick / Cost: low to high</option>
              <option value="target-desc">Target: high to low</option>
              <option value="target-asc">Target: low to high</option>
              <option value="high-desc">High: high to low</option>
              <option value="high-asc">High: low to high</option>
            </select>
          </label>
          <button class="container-reset" type="reset">Clear all</button>
        </div>

        <fieldset class="container-restriction-filter">
          <legend>Container restrictions <span>Select one or more. Selected types are combined with OR.</span></legend>
          <div class="container-filter-chip-row">
{restriction_chips}
          </div>
        </fieldset>

        <details class="container-more-filters">
          <summary><span>More filters</span><span class="container-more-filter-summary">Source and expansion</span></summary>
          <div class="container-advanced-grid">
            <label class="container-filter">
              <span>Source</span>
              <select id="container-source">
                <option value="">All sources</option>
                <option value="crafted">Crafted ({source_counts["crafted"]})</option>
                <option value="vendor">Vendor ({source_counts["vendor"]})</option>
                <option value="drop">Drop ({source_counts["drop"]})</option>
                <option value="quest-reward">Quest reward ({source_counts["quest-reward"]})</option>
              </select>
            </label>
            <label class="container-filter">
              <span>Expansion</span>
              <select id="container-expansion">
                <option value="">All expansions</option>
                <option value="wrath">Wrath</option>
                <option value="outland">Outland</option>
                <option value="classic">Classic</option>
              </select>
            </label>
          </div>
        </details>

        <div class="container-active-filters" id="container-active-filters" hidden>
          <span class="container-active-filter-label">Active filters</span>
          <div class="container-active-filter-list" id="container-active-filter-list"></div>
        </div>
      </form>

      <div class="container-table-wrap">
        <table class="container-collection-table">
          <thead><tr>
            <th data-column="item" aria-sort="none"><button class="container-sort-heading" type="button" data-container-sort-key="name">Item<span aria-hidden="true">↕</span></button></th>
            <th data-column="slots" aria-sort="descending"><button class="container-sort-heading" type="button" data-container-sort-key="slots">Slots<span aria-hidden="true">↓</span></button></th>
            <th data-column="type" aria-sort="none"><button class="container-sort-heading" type="button" data-container-sort-key="type">Contents<span aria-hidden="true">↕</span></button></th>
            <th data-column="expansion" aria-sort="none"><button class="container-sort-heading" type="button" data-container-sort-key="expansion">Expansion<span aria-hidden="true">↕</span></button></th>
            <th data-column="source" aria-sort="none"><button class="container-sort-heading" type="button" data-container-sort-key="source">Source<span aria-hidden="true">↕</span></button></th>
            <th data-column="quick" aria-sort="none"><button class="container-sort-heading" type="button" data-container-sort-key="quick">Quick / Cost<span aria-hidden="true">↕</span></button></th>
            <th data-column="target" aria-sort="none"><button class="container-sort-heading" type="button" data-container-sort-key="target">Target<span aria-hidden="true">↕</span></button></th>
            <th data-column="high" aria-sort="none"><button class="container-sort-heading" type="button" data-container-sort-key="high">High<span aria-hidden="true">↕</span></button></th>
            <th data-column="owner">Canonical guide</th>
          </tr></thead>
          <tbody data-container-rows>
{rendered_rows}
          </tbody>
        </table>
        <p class="container-empty-state" id="container-empty-state" hidden>No containers match the selected types with the current search, source, and expansion filters.</p>
      </div>
    </section>

    <section class="common container-collection-help">
      <h2>How to use this collection</h2>
      <p>Sort the Slots heading to keep equal capacities together. Restriction chips show any selected type, while Search, Source, and Expansion narrow those results together. Select the item name or Canonical guide link for its full pricing and acquisition note. Crafted rows retain their recipe and materials mouseover in the owning profession guide.</p>
    </section>

    <footer>WotLK 3.3.5 Bags &amp; Containers AH Collection • Hellscream / Garrosh • Created by Valdora • Updated {today}</footer>
  </div>
  <script src="../assets/ah-item-tooltips.js?v={ASSET_VERSION}" defer></script>
  <script src="../assets/ah-containers.js?v={ASSET_VERSION}" defer></script>
</body>
</html>
'''


def render_shortcut(source: str, path: Path) -> str:
    if COLLECTION_LINK_PATTERN.search(source):
        return COLLECTION_LINK_PATTERN.sub(COLLECTION_LINK, source, count=1)
    matches = list(HERBS_LINK_PATTERN.finditer(source))
    if len(matches) != 1:
        raise ValueError(f"{path.name}: expected one Herbs quick link")
    match = matches[0]
    replacement = match.group(0) + match.group("indent") + COLLECTION_LINK
    return source[: match.start()] + replacement + source[match.end() :]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Fail when the collection is stale")
    args = parser.parse_args()

    collection, rows = build_rows()
    output_path = GUIDES_DIR / collection["file"]
    expected_page = render_page(collection, rows)
    changes: list[tuple[Path, str]] = []
    if not output_path.is_file() or output_path.read_text(encoding="utf-8") != expected_page:
        changes.append((output_path, expected_page))
    for path in HUB_PATHS:
        source = path.read_text(encoding="utf-8")
        expected = render_shortcut(source, path)
        if source != expected:
            changes.append((path, expected))

    if args.check:
        if changes:
            for path, _ in changes:
                print(f"Stale container collection output: {path.relative_to(ROOT)}", file=sys.stderr)
            return 1
        print(f"Container collection is current: {len(rows)} canonical rows and two Bags shortcuts.")
        return 0

    for path, content in changes:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8", newline="\n")
    print(f"Rendered Bags & Containers collection with {len(rows)} canonical rows.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
