#!/usr/bin/env python3
"""Render canonical navigation, vendor, crafted-market, and dropped-scroll sections."""

from __future__ import annotations

import argparse
import html
import json
import re
import sys
from pathlib import Path

from ah_section_ordering import load_policy, order_guide_source


ROOT = Path(__file__).resolve().parents[1]
GUIDES_DIR = ROOT / "guides"
VENDOR_DATA_PATH = ROOT / "data" / "ah-vendor-sections.json"
CRAFTED_DATA_PATH = ROOT / "data" / "ah-crafted-sections.json"
PROFESSION_USE_AUDIT_PATH = ROOT / "data" / "ah-profession-use-audit.json"
DROPPED_SCROLL_DATA_PATH = ROOT / "data" / "ah-dropped-scrolls.json"
NAV_TEMPLATE_PATH = ROOT / "templates" / "ah-guide" / "navigation.html"
BASELINE_NOTE_TEMPLATE_PATH = ROOT / "templates" / "ah-guide" / "baseline-note.html"
VENDOR_TEMPLATE_PATH = ROOT / "templates" / "ah-guide" / "vendor-convenience-section.html"
CRAFTED_TEMPLATE_PATH = ROOT / "templates" / "ah-guide" / "crafted-market-section.html"
DROPPED_SCROLL_TEMPLATE_PATH = ROOT / "templates" / "ah-guide" / "dropped-scrolls-section.html"
AH_GUIDE_GLOB = "*ah-price-guide.html"
AH_STYLESHEET_VERSION = "20260801-ah-rarity-v1"
SECTION_ORDERING_POLICY = load_policy()

NAV_BLOCK = re.compile(
    r"(?:<!-- AH_SHARED_NAV_START -->\s*)?"
    r"<nav class=\"site-nav(?: ah-guide-nav)?\" aria-label=\"Guide navigation\">.*?</nav>"
    r"(?:\s*<!-- AH_SHARED_NAV_END -->)?",
    re.DOTALL,
)
BASELINE_NOTE_BLOCK = re.compile(
    r"<!-- AH_BASELINE_NOTE_START -->\s*"
    r"<aside class=\"note ah-baseline-note\">.*?</aside>"
    r"\s*<!-- AH_BASELINE_NOTE_END -->",
    re.DOTALL,
)
VENDOR_BLOCK = re.compile(
    r"<!-- AH_VENDOR_SECTION_START -->.*?<!-- AH_VENDOR_SECTION_END -->",
    re.DOTALL,
)
CRAFTED_BLOCK = re.compile(
    r"<!-- AH_CRAFTED_SECTION_START -->\s*"
    r"<div class=\"ah-crafted-market\" data-ah-template=\"[^\"]+\">.*?</div>"
    r"\s*<!-- AH_CRAFTED_SECTION_END -->",
    re.DOTALL,
)
DROPPED_SCROLL_BLOCK = re.compile(
    r"<!-- AH_DROPPED_SCROLLS_START -->\s*"
    r"<section class=\"common dropped-scrolls-section\".*?</section>"
    r"\s*<!-- AH_DROPPED_SCROLLS_END -->",
    re.DOTALL,
)
LEGACY_INSCRIPTION_CRAFTED_BLOCK = re.compile(
    r"<section class=\"common\"><h2>Darkmoon cards / decks</h2>.*?</section>\s*"
    r"<section class=\"common ref-compact\"><h2>Vellums</h2>.*?</section>",
    re.DOTALL,
)


def format_money(copper: int) -> str:
    if copper < 0:
        raise ValueError("Money cannot be negative")
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


def source_cost(item: dict) -> str:
    if item["source_type"] != "coin-vendor":
        return html.escape(item["source_cost_label"])

    cost = int(item["vendor_cost_copper"])
    count = int(item.get("vendor_buy_count", 1))
    if count <= 0 or cost % count:
        raise ValueError(f"Invalid vendor bundle for {item['name']}")
    if count == 1:
        return f"Vendor: {format_money(cost)} each"
    return (
        f"Vendor: {format_money(cost)} per {count} "
        f"({format_money(cost // count)} each)"
    )


def target_bid(target_copper: int) -> int:
    """Match the 85% target-bid convention used by the regular AH rows."""
    return max(1, round(target_copper * 0.85))


def anchor_slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.casefold()).strip("-")


def render_vendor_row(key: str, item: dict, use_audit: dict) -> str:
    name = html.escape(item["name"])
    source_label = html.escape(item["source_label"])
    target_copper = int(item["target_copper"])
    bid = format_money(target_bid(target_copper))
    target = format_money(target_copper)
    stack = html.escape(item["stack"])
    notes = html.escape(item["notes"])
    cost = source_cost(item)
    requirement = use_audit.get("vendor_hard_requirements", {}).get(key)
    audience_attribute = ""
    requirement_note = ""
    if requirement:
        skill = html.escape(requirement["skill"])
        rank = int(requirement["rank"])
        audience_attribute = ' data-use-audience="profession-restricted"'
        requirement_note = (
            f'<strong class="profession-use-requirement">'
            f'Requires {skill} {rank} to use.</strong> '
        )
    return (
        f'        <tr data-vendor-key="{html.escape(key)}"{audience_attribute}>\n'
        f'          <td data-column="item" data-label="Item">'
        f'<strong class="q-common">{name}</strong>'
        f'<div class="mini">{source_label}</div></td>\n'
        f'          <td data-column="target" data-label="Target Price">'
        f'<div class="pricepair target">\n'
        f'            <div><span class="label">Bid</span>'
        f'<span class="bid">{bid}</span></div>\n'
        f'            <div><span class="label">Buyout</span>'
        f'<span class="buyout">{target}</span></div>\n'
        f'          </div></td>\n'
        f'          <td data-column="stack" data-label="Stack Size">{stack}</td>\n'
        f'          <td data-column="demand" data-label="Demand">'
        f'<span class="demand low">Low</span></td>\n'
        f'          <td data-column="notes" data-label="Use / Selling Notes">'
        f'{requirement_note}<strong>Source / cost:</strong> {cost}. {notes}</td>\n'
        f"        </tr>"
    )


def load_vendor_config() -> dict:
    config = json.loads(VENDOR_DATA_PATH.read_text(encoding="utf-8"))
    use_audit = json.loads(PROFESSION_USE_AUDIT_PATH.read_text(encoding="utf-8"))
    catalog = config.get("catalog", {})
    guides = config.get("guides", {})
    if not catalog or not guides:
        raise ValueError("Vendor data must define catalog and guides")

    used: set[str] = set()
    for filename, guide in guides.items():
        path = GUIDES_DIR / filename
        if not path.is_file():
            raise FileNotFoundError(f"Missing AH guide: {path.relative_to(ROOT)}")
        item_keys = list(guide.get("items", []))
        for section in guide.get("restricted_sections", []):
            item_keys.extend(section.get("items", []))
        for key in item_keys:
            if key not in catalog:
                raise KeyError(f"{filename} references unknown vendor item: {key}")
            used.add(key)

    unused = sorted(set(catalog) - used)
    if unused:
        raise ValueError(f"Unused vendor catalog entries: {', '.join(unused)}")
    for key, requirement in use_audit.get("vendor_hard_requirements", {}).items():
        if key not in catalog:
            raise KeyError(f"Profession-use audit references unknown vendor item: {key}")
        if int(requirement["item_id"]) != int(catalog[key]["item_id"]):
            raise ValueError(f"Profession-use audit item ID mismatch for vendor item {key}")
    config["_profession_use_audit"] = use_audit
    return config


def render_vendor_section(
    template: str,
    guide: dict,
    catalog: dict,
    use_audit: dict,
) -> str:
    rows = "\n".join(
        render_vendor_row(key, catalog[key], use_audit)
        for key in guide.get("items", [])
    )
    rendered = template.replace("{{ROWS}}", rows)
    restricted_blocks: list[str] = []
    for section in guide.get("restricted_sections", []):
        section_id = html.escape(section["id"])
        title = html.escape(section["title"])
        description = html.escape(section["description"])
        restricted_rows = "\n".join(
            render_vendor_row(key, catalog[key], use_audit)
            for key in section["items"]
        )
        restricted_blocks.append(
            f'<section class="common vendor-compact profession-use-section" '
            f'id="{section_id}" data-ah-template="vendor-convenience-v2" '
            f'data-use-audience="profession-restricted">\n'
            f'  <h2>{title}</h2>\n'
            f'  <p class="small">{description}</p>\n'
            f'  <div class="table-wrap"><table class="ah-market-table '
            f'ah-market-table--standard ah-vendor-table" data-table-family="market">'
            f'<thead><tr><th data-column="item">Item</th>'
            f'<th data-column="target">Target Price</th>'
            f'<th data-column="stack">Stack Size</th>'
            f'<th data-column="demand">Demand</th>'
            f'<th data-column="notes">Use / Selling Notes</th>'
            f'</tr></thead><tbody>\n{restricted_rows}\n'
            f'      </tbody></table></div>\n</section>'
        )
    if restricted_blocks:
        rendered = rendered.replace(
            "<!-- AH_VENDOR_SECTION_END -->",
            "\n".join(restricted_blocks) + "\n<!-- AH_VENDOR_SECTION_END -->",
        )
    return rendered


def remove_legacy_vendor_sections(source: str, guide: dict, filename: str) -> str:
    for title in guide.get("legacy_section_removals", []):
        pattern = re.compile(
            r'<section class="common(?:\s[^"]*)?">'
            r'<h2 class="ah-category-heading">'
            + re.escape(html.escape(title, quote=False))
            + r".*?</section>\s*",
            re.DOTALL,
        )
        source, count = pattern.subn("", source, count=1)
        if count > 1:
            raise ValueError(f"{filename}: duplicate legacy vendor section {title!r}")
    return source


def decorate_category_headings(source: str, filename: str) -> str:
    """Give every AH category one consistent, right-aligned back-to-top control."""
    source, wrap_count = re.subn(
        r'<div class="wrap"(?: id="top")?>',
        '<div class="wrap" id="top">',
        source,
        count=1,
    )
    if wrap_count != 1:
        raise ValueError(f"{filename}: expected exactly one page wrapper")

    def decorate(match: re.Match[str]) -> str:
        attributes, content = match.groups()
        content = re.sub(
            r'<a class="ah-back-to-top"[^>]*>.*?</a>\s*$',
            "",
            content,
            flags=re.DOTALL,
        )
        if 'class="' in attributes:
            attributes = re.sub(
                r'class="([^"]*)"',
                lambda class_match: (
                    f'class="{class_match.group(1)} ah-category-heading"'
                    if "ah-category-heading" not in class_match.group(1).split()
                    else class_match.group(0)
                ),
                attributes,
                count=1,
            )
        else:
            attributes += ' class="ah-category-heading"'
        return (
            f"<h2{attributes}>{content}"
            '<a class="ah-back-to-top" href="#top" aria-label="Back to top">↑ Top</a>'
            "</h2>"
        )

    source, heading_count = re.subn(
        r"<h2([^>]*)>(.*?)</h2>", decorate, source, flags=re.DOTALL
    )
    if heading_count == 0:
        raise ValueError(f"{filename}: expected at least one category heading")

    return re.sub(
        r"ah-guide-icons\.css\?v=[^\"\s]+",
        f"ah-guide-icons.css?v={AH_STYLESHEET_VERSION}",
        source,
        count=1,
    )


def load_crafted_config() -> dict:
    config = json.loads(CRAFTED_DATA_PATH.read_text(encoding="utf-8"))
    use_audit = json.loads(PROFESSION_USE_AUDIT_PATH.read_text(encoding="utf-8"))
    catalog = config.get("catalog", {})
    profiles = config.get("price_profiles", {})
    guides = config.get("guides", {})
    defaults = config.get("catalog_defaults", {})
    if not catalog or not profiles or not guides:
        raise ValueError("Crafted data must define catalog, price_profiles, and guides")

    used: set[str] = set()
    item_ids: set[int] = set()
    for key, item in catalog.items():
        profile_key = item.get("profile")
        if profile_key not in profiles:
            raise KeyError(f"{key} references unknown crafted profile: {profile_key}")
        item_id = int(item["item_id"])
        if item_id <= 0 or item_id in item_ids:
            raise ValueError(f"{key}: invalid or duplicate crafted item ID {item_id}")
        item_ids.add(item_id)
        merged = defaults | profiles[profile_key] | item
        if not merged.get("crafted") or not merged.get("tradeable"):
            raise ValueError(f"{key}: crafted catalog items must be crafted and tradeable")
        if merged.get("binding") not in {"none", "boe"}:
            raise ValueError(f"{key}: BoP or unknown binding is not allowed")

    for filename, guide in guides.items():
        path = GUIDES_DIR / filename
        if not path.is_file():
            raise FileNotFoundError(f"Missing AH guide: {path.relative_to(ROOT)}")
        shared_note = guide.get("shared_note")
        if shared_note:
            required_note_fields = {"id", "marker", "label", "text"}
            missing_note_fields = required_note_fields - set(shared_note)
            if missing_note_fields:
                raise ValueError(
                    f"{filename}: shared crafted note is missing "
                    f"{', '.join(sorted(missing_note_fields))}"
                )
            if not re.fullmatch(r"[a-z0-9-]+", shared_note["id"]):
                raise ValueError(f"{filename}: shared crafted note ID is not anchor-safe")
        for section in guide.get("sections", []):
            for key in section.get("items", []):
                if key not in catalog:
                    raise KeyError(f"{filename} references unknown crafted item: {key}")
                if key in used:
                    raise ValueError(f"Crafted item is used more than once: {key}")
                used.add(key)

    unused = sorted(set(catalog) - used)
    if unused:
        raise ValueError(f"Unused crafted catalog entries: {', '.join(unused)}")
    classified_keys: set[str] = set()
    for group_name in (
        "canonical_hard_requirements",
        "canonical_profession_audience",
        "canonical_general_use_exceptions",
    ):
        for key, requirement in use_audit.get(group_name, {}).items():
            if key in classified_keys:
                raise ValueError(f"Profession-use audit classifies {key} more than once")
            classified_keys.add(key)
            if key not in catalog:
                raise KeyError(f"Profession-use audit references unknown crafted item: {key}")
            if int(requirement["item_id"]) != int(catalog[key]["item_id"]):
                raise ValueError(f"Profession-use audit item ID mismatch for {key}")
    config["_profession_use_audit"] = use_audit
    return config


def load_dropped_scroll_config() -> dict:
    config = json.loads(DROPPED_SCROLL_DATA_PATH.read_text(encoding="utf-8"))
    catalog = config.get("catalog", {})
    rank_profiles = config.get("rank_profiles", {})
    stat_profiles = config.get("stat_profiles", {})
    guides = config.get("guides", {})
    defaults = config.get("catalog_defaults", {})
    if not catalog or not rank_profiles or not stat_profiles or not guides:
        raise ValueError(
            "Dropped-scroll data must define catalog, rank profiles, stat profiles, and guides"
        )

    item_ids: set[int] = set()
    used: set[str] = set()
    for key, item in catalog.items():
        rank = str(item.get("rank", ""))
        stat = item.get("stat")
        if rank not in rank_profiles or stat not in stat_profiles:
            raise KeyError(f"{key}: unknown dropped-scroll rank or stat profile")
        item_id = int(item["item_id"])
        if item_id <= 0 or item_id in item_ids:
            raise ValueError(f"{key}: invalid or duplicate dropped-scroll item ID {item_id}")
        item_ids.add(item_id)
        merged = defaults | rank_profiles[rank] | stat_profiles[stat] | item
        if (
            merged.get("source_type") != "world-drop"
            or not merged.get("tradeable")
            or merged.get("binding") != "none"
        ):
            raise ValueError(f"{key}: scroll must be an unbound tradeable world drop")

    for filename, guide in guides.items():
        path = GUIDES_DIR / filename
        if not path.is_file():
            raise FileNotFoundError(f"Missing AH guide: {path.relative_to(ROOT)}")
        for key in guide.get("items", []):
            if key not in catalog:
                raise KeyError(f"{filename} references unknown dropped scroll: {key}")
            if key in used:
                raise ValueError(f"Dropped scroll is used more than once: {key}")
            used.add(key)
    if used != set(catalog):
        raise ValueError("Dropped-scroll catalog and guide usage do not match")
    return config


def render_price_pair(
    kind: str,
    buyout_copper: int,
    bid_copper: int | None = None,
) -> str:
    bid = format_money(
        target_bid(buyout_copper)
        if bid_copper is None
        else int(bid_copper)
    )
    buyout = format_money(buyout_copper)
    return (
        f'<div class="pricepair {kind}">\n'
        f'<div><span class="label">Bid</span><span class="bid">{bid}</span></div>\n'
        f'<div><span class="label">Buyout</span><span class="buyout">{buyout}</span></div>\n'
        f"</div>"
    )


def crafted_item(config: dict, key: str) -> dict:
    item = config["catalog"][key]
    return (
        config.get("catalog_defaults", {})
        | config["price_profiles"][item["profile"]]
        | item
    )


def render_crafted_row(
    config: dict,
    key: str,
    shared_note: dict | None = None,
) -> str:
    item = crafted_item(config, key)
    profession = html.escape(item["profession"])
    name = html.escape(item["name"])
    detail = html.escape(item["detail"])
    stack = html.escape(item["stack"])
    demand = html.escape(item["demand"])
    demand_class = html.escape(item["demand_class"])
    materials = html.escape(item["materials"])
    notes = html.escape(item["notes"])
    row_note = html.escape(item.get("row_note", "").strip())
    quality = html.escape(item["quality"])
    search_hint = html.escape(item.get("search_hint", "").strip(), quote=True)
    search_hint_attribute = (
        f' data-search-hint="{search_hint}"' if search_hint else ""
    )
    requirement = config["_profession_use_audit"].get(
        "canonical_hard_requirements", {}
    ).get(key)
    general_use_exception = config["_profession_use_audit"].get(
        "canonical_general_use_exceptions", {}
    ).get(key)
    requirement_note = ""
    if requirement:
        skill = html.escape(requirement["skill"])
        rank = int(requirement["rank"])
        action = "place" if item["name"].endswith("Feast") else "use"
        requirement_note = (
            f'<strong class="profession-use-requirement">'
            f'Requires {skill} {rank} to {action}.</strong>'
        )
    if shared_note:
        note_id = html.escape(shared_note["id"])
        marker = html.escape(shared_note["marker"])
        note_label = html.escape(shared_note["label"])
        note_reference = (
            f'<a class="crafted-note-ref" href="#{note_id}" '
            f'aria-label="See {note_label} note">{marker}</a>'
        )
        note_parts = []
        if requirement_note:
            note_parts.append(requirement_note)
        if general_use_exception and general_use_exception.get("show_note"):
            reason = html.escape(general_use_exception["reason"])
            note_parts.append(
                f'<strong class="profession-use-exception">'
                f'No profession required:</strong> {reason}'
            )
        if row_note:
            note_parts.append(f'<span class="crafted-item-note">{row_note}</span>')
        source_spell_id = int(item.get("source_spell_id", 0))
        if source_spell_id > 0:
            recipe_url = f"https://www.wowhead.com/wotlk/spell={source_spell_id}"
            note_parts.append(
                f'<a class="crafted-recipe-link ah-item-tooltip ah-item-tooltip-label" '
                f'href="{recipe_url}" target="_blank" rel="noopener" '
                f'data-wowhead="spell={source_spell_id}&amp;domain=wotlk" '
                f'data-ah-wowhead-url="{recipe_url}" '
                f'aria-label="Open {name} recipe and materials on Wowhead">'
                f'Recipe &amp; mats ↗</a>'
            )
        note_parts.append(note_reference)
        notes_cell = " ".join(note_parts)
    else:
        notes_cell = f'<strong>Reagent floor:</strong> {materials}. {notes}'
    return (
        f'<tr data-crafted-key="{html.escape(key)}" data-market-source="crafted" '
        f'data-profession="{profession}"{search_hint_attribute}>'
        f'<td data-column="item" data-label="Item"><strong class="q-{quality}">{name}</strong>'
        f'<div class="mini">{detail}</div></td>'
        f'<td data-column="target" data-label="Target Price">'
        f'{render_price_pair("target", int(item["target_copper"]), item.get("target_bid_copper"))}</td>'
        f'<td data-column="quick" data-label="Quick Price">'
        f'{render_price_pair("quick", int(item["quick_copper"]), item.get("quick_bid_copper"))}</td>'
        f'<td data-column="high" data-label="High / Scarce">'
        f'{render_price_pair("high", int(item["high_copper"]), item.get("high_bid_copper"))}</td>'
        f'<td data-column="stack" data-label="Stack Size">{stack}</td>'
        f'<td data-column="demand" data-label="Demand">'
        f'<span class="demand {demand_class}">{demand}</span></td>'
        f'<td data-column="notes" data-label="Use / Selling Notes">'
        f'{notes_cell}</td></tr>'
    )


def render_crafted_section(
    config: dict,
    section: dict,
    shared_note: dict | None = None,
) -> str:
    title = html.escape(section["title"])
    section_id = html.escape(section.get("id") or anchor_slug(section["title"]))
    description = html.escape(section["description"])
    audience = section.get("audience")
    audience_attribute = (
        f' data-use-audience="{html.escape(audience)}"' if audience else ""
    )
    rows = "\n".join(
        render_crafted_row(config, key, shared_note)
        for key in section["items"]
    )
    return (
        f'<section class="common crafted-market-section" id="{section_id}"'
        f'{audience_attribute}>\n'
        f'<h2 class="ah-category-heading">{title}'
        f'<a class="ah-back-to-top" href="#top" aria-label="Back to top">↑ Top</a></h2>\n'
        f'<p class="small">{description}</p>\n'
        f'<div class="table-wrap"><table class="ah-market-table ah-market-table--standard" '
        f'data-table-family="market"><thead><tr>'
        f'<th data-column="item">Item</th><th data-column="target">Target Price</th>'
        f'<th data-column="quick">Quick Price</th><th data-column="high">High / Scarce</th>'
        f'<th data-column="stack">Stack Size</th><th data-column="demand">Demand</th>'
        f'<th data-column="notes">Use / Selling Notes</th></tr></thead>'
        f'<tbody>{rows}</tbody></table></div>\n'
        f"</section>"
    )


def render_crafted_market(template: str, guide: dict, config: dict) -> str:
    shared_note = guide.get("shared_note")
    sections = "\n".join(
        render_crafted_section(config, section, shared_note)
        for section in guide["sections"]
    )
    intro_note = ""
    if shared_note:
        note_id = html.escape(shared_note["id"])
        marker = html.escape(shared_note["marker"])
        note_label = html.escape(shared_note["label"])
        note_text = html.escape(shared_note["text"])
        intro_note = (
            f'\n    <p class="small crafted-market-shared-note" id="{note_id}">'
            f'<strong>{marker} {note_label}:</strong> {note_text}</p>'
        )
    return (
        template.replace("{{INTRO_TITLE}}", html.escape(guide["intro_title"]))
        .replace(
            "{{INTRO_DESCRIPTION}}",
            html.escape(guide["intro_description"]),
        )
        .replace("{{INTRO_NOTE}}", intro_note)
        .replace("{{SECTIONS}}", sections)
    )


def remove_legacy_crafted_rows(
    source: str,
    filename: str,
    removals: dict[str, list[str]],
) -> str:
    """Remove priced craftable rows that were mixed into broader input sections."""
    for section_title, item_names in removals.items():
        section_pattern = re.compile(
            r'<section class="common(?: [^"]*)?"><h2 class="ah-category-heading">'
            + re.escape(html.escape(section_title))
            + r'<a class="ah-back-to-top".*?</section>',
            re.DOTALL,
        )
        section_matches = list(section_pattern.finditer(source))
        if len(section_matches) != 1:
            raise ValueError(
                f"{filename}: expected one legacy row-removal section for {section_title}"
            )

        section_match = section_matches[0]
        section_source = section_match.group(0)
        for item_name in item_names:
            row_pattern = re.compile(
                r'<tr><td data-column="item" data-label="Item">'
                r'<strong class="q-[^"]+">'
                + re.escape(html.escape(item_name))
                + r"</strong>.*?</tr>",
                re.DOTALL,
            )
            section_source, row_count = row_pattern.subn("", section_source, count=1)
            if row_count != 1:
                raise ValueError(
                    f"{filename}: expected one legacy crafted row for {item_name}"
                )

        source = (
            source[: section_match.start()]
            + section_source
            + source[section_match.end() :]
        )
    return source


def replace_legacy_crafted_sections(
    source: str,
    expected: str,
    filename: str,
    titles: list[str],
) -> str:
    matches: list[re.Match[str]] = []
    for title in titles:
        pattern = re.compile(
            r'(?:<!-- AH_PROFESSION_USE_SECTION_START [a-z0-9-]+ -->\s*)?'
            r'<section class="common(?:\s[^"]*)?"[^>]*><h2 class="ah-category-heading">'
            + re.escape(html.escape(title))
            + r'<a class="ah-back-to-top".*?</section>'
            r'(?:\s*<!-- AH_PROFESSION_USE_SECTION_END [a-z0-9-]+ -->)?',
            re.DOTALL,
        )
        title_matches = list(pattern.finditer(source))
        if len(title_matches) != 1:
            raise ValueError(
                f"{filename}: expected one legacy crafted section for {title}"
            )
        matches.extend(title_matches)

    first_start = min(match.start() for match in matches)
    for match in sorted(matches, key=lambda current: current.start(), reverse=True):
        replacement = expected if match.start() == first_start else ""
        source = source[: match.start()] + replacement + source[match.end() :]
    return source


def dropped_scroll_item(config: dict, key: str) -> dict:
    item = config["catalog"][key]
    return (
        config.get("catalog_defaults", {})
        | config["rank_profiles"][str(item["rank"])]
        | config["stat_profiles"][item["stat"]]
        | item
    )


def render_dropped_scroll_row(
    config: dict,
    key: str,
    shared_note: dict,
) -> str:
    item = dropped_scroll_item(config, key)
    name = html.escape(item["name"])
    rank = int(item["rank"])
    stat = html.escape(item["stat"])
    stack = html.escape(item["stack"])
    demand = html.escape(item["demand"])
    demand_class = html.escape(item["demand_class"])
    notes = html.escape(item["notes"])
    note_id = html.escape(shared_note["id"])
    marker = html.escape(shared_note["marker"])
    note_label = html.escape(shared_note["label"])
    note_reference = (
        f'<a class="dropped-scroll-note-ref" href="#{note_id}" '
        f'aria-label="See {note_label} note">{marker}</a>'
    )
    return (
        f'<tr data-dropped-scroll-key="{html.escape(key)}" data-market-source="drop">'
        f'<td data-column="item" data-label="Item"><strong class="q-common">{name}</strong>'
        f'<div class="mini">World drop • Rank {rank} {stat} scroll</div></td>'
        f'<td data-column="target" data-label="Target Price">'
        f'{render_price_pair("target", int(item["target_copper"]))}</td>'
        f'<td data-column="quick" data-label="Quick Price">'
        f'{render_price_pair("quick", int(item["quick_copper"]))}</td>'
        f'<td data-column="high" data-label="High / Scarce">'
        f'{render_price_pair("high", int(item["high_copper"]))}</td>'
        f'<td data-column="stack" data-label="Stack Size">{stack}</td>'
        f'<td data-column="demand" data-label="Demand">'
        f'<span class="demand {demand_class}">{demand}</span></td>'
        f'<td data-column="notes" data-label="Use / Selling Notes">'
        f'<span class="dropped-scroll-item-note">{notes}</span> '
        f"{note_reference}</td></tr>"
    )


def render_dropped_rank_table(
    config: dict,
    rank: int,
    item_keys: list[str],
    shared_note: dict,
) -> str:
    rows = "\n".join(
        render_dropped_scroll_row(config, key, shared_note)
        for key in item_keys
        if int(config["catalog"][key]["rank"]) == rank
    )
    return (
        f'<h3>Rank {rank}</h3>\n'
        f'<div class="table-wrap"><table class="ah-market-table ah-market-table--standard" '
        f'data-table-family="market"><thead><tr>'
        f'<th data-column="item">Item</th><th data-column="target">Target Price</th>'
        f'<th data-column="quick">Quick Price</th><th data-column="high">High / Scarce</th>'
        f'<th data-column="stack">Stack Size</th><th data-column="demand">Demand</th>'
        f'<th data-column="notes">Use / Selling Notes</th></tr></thead>'
        f"<tbody>{rows}</tbody></table></div>"
    )


def render_dropped_scroll_section(template: str, guide: dict, config: dict) -> str:
    shared_note = guide["shared_note"]
    rank_tables = "\n".join(
        render_dropped_rank_table(config, rank, guide["items"], shared_note)
        for rank in range(1, 8)
    )
    note_id = html.escape(shared_note["id"])
    marker = html.escape(shared_note["marker"])
    note_label = html.escape(shared_note["label"])
    note_text = html.escape(shared_note["text"])
    shared_note_html = (
        f'\n  <p class="small dropped-scroll-shared-note" id="{note_id}">'
        f'<strong>{marker} {note_label}:</strong> {note_text}</p>'
    )
    return (
        template.replace("{{TITLE}}", html.escape(guide["title"]))
        .replace("{{DESCRIPTION}}", html.escape(guide["description"]))
        .replace("{{SHARED_NOTE}}", shared_note_html)
        .replace("{{RANK_TABLES}}", rank_tables)
    )


def transform_guide(
    source: str,
    filename: str,
    nav_template: str,
    baseline_note_template: str,
    vendor_template: str,
    crafted_template: str,
    dropped_scroll_template: str,
    vendor_config: dict,
    crafted_config: dict,
    dropped_scroll_config: dict,
) -> str:
    source, nav_count = NAV_BLOCK.subn(nav_template, source, count=1)
    if nav_count != 1:
        raise ValueError(f"{filename}: expected exactly one guide navigation block")

    baseline_note_matches = len(BASELINE_NOTE_BLOCK.findall(source))
    if baseline_note_matches == 1:
        source = BASELINE_NOTE_BLOCK.sub(baseline_note_template, source, count=1)
    elif baseline_note_matches == 0:
        if source.count("</header>") != 1:
            raise ValueError(f"{filename}: expected exactly one header insertion point")
        source = source.replace(
            "</header>",
            f"{baseline_note_template}\n</header>",
            1,
        )
    else:
        raise ValueError(f"{filename}: expected at most one pricing-baseline note")

    guide_config = vendor_config["guides"].get(filename)
    vendor_matches = len(VENDOR_BLOCK.findall(source))
    if guide_config:
        source = remove_legacy_vendor_sections(source, guide_config, filename)
        if guide_config.get("remove"):
            if vendor_matches > 1:
                raise ValueError(f"{filename}: expected at most one vendor section")
            source = VENDOR_BLOCK.sub("", source, count=1)
        else:
            if vendor_matches != 1:
                raise ValueError(f"{filename}: expected exactly one vendor section")
            expected = render_vendor_section(
                vendor_template,
                guide_config,
                vendor_config["catalog"],
                vendor_config["_profession_use_audit"],
            )
            source = VENDOR_BLOCK.sub(expected, source, count=1)
    elif vendor_matches:
        raise ValueError(f"{filename}: vendor section exists but is absent from canonical data")

    crafted_guide = crafted_config["guides"].get(filename)
    crafted_matches = len(CRAFTED_BLOCK.findall(source))
    if crafted_guide:
        expected = render_crafted_market(crafted_template, crafted_guide, crafted_config)
        if crafted_matches == 1:
            source = CRAFTED_BLOCK.sub(expected, source, count=1)
        elif (
            filename == "inscription-materials-ah-price-guide.html"
            and crafted_matches == 0
            and len(LEGACY_INSCRIPTION_CRAFTED_BLOCK.findall(source)) == 1
        ):
            source = LEGACY_INSCRIPTION_CRAFTED_BLOCK.sub(expected, source, count=1)
        elif crafted_matches == 0 and crafted_guide.get("legacy_section_titles"):
            if crafted_guide.get("legacy_row_removals"):
                source = remove_legacy_crafted_rows(
                    source,
                    filename,
                    crafted_guide["legacy_row_removals"],
                )
            source = replace_legacy_crafted_sections(
                source,
                expected,
                filename,
                crafted_guide["legacy_section_titles"],
            )
        else:
            raise ValueError(f"{filename}: expected one crafted-market or legacy block")
    elif crafted_matches:
        raise ValueError(f"{filename}: crafted section exists but is absent from canonical data")

    dropped_guide = dropped_scroll_config["guides"].get(filename)
    dropped_matches = len(DROPPED_SCROLL_BLOCK.findall(source))
    if dropped_guide:
        expected = render_dropped_scroll_section(
            dropped_scroll_template, dropped_guide, dropped_scroll_config
        )
        if dropped_matches == 1:
            source = DROPPED_SCROLL_BLOCK.sub(expected, source, count=1)
        elif dropped_matches == 0:
            crafted_match = CRAFTED_BLOCK.search(source)
            if not crafted_match:
                raise ValueError(f"{filename}: missing dropped-scroll insertion point")
            source = (
                source[: crafted_match.start()]
                + expected
                + "\n"
                + source[crafted_match.start() :]
            )
        else:
            raise ValueError(f"{filename}: expected one dropped-scroll block")
    elif dropped_matches:
        raise ValueError(f"{filename}: dropped-scroll section is absent from canonical data")
    source = decorate_category_headings(source, filename)
    source, _ = order_guide_source(source, filename, SECTION_ORDERING_POLICY)
    return source


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Fail if generated guide blocks are stale")
    args = parser.parse_args()

    vendor_config = load_vendor_config()
    crafted_config = load_crafted_config()
    dropped_scroll_config = load_dropped_scroll_config()
    nav_template = NAV_TEMPLATE_PATH.read_text(encoding="utf-8").strip()
    baseline_note_template = BASELINE_NOTE_TEMPLATE_PATH.read_text(encoding="utf-8").strip()
    vendor_template = VENDOR_TEMPLATE_PATH.read_text(encoding="utf-8").strip()
    crafted_template = CRAFTED_TEMPLATE_PATH.read_text(encoding="utf-8").strip()
    dropped_scroll_template = DROPPED_SCROLL_TEMPLATE_PATH.read_text(encoding="utf-8").strip()
    changed: list[str] = []

    guide_paths = sorted(GUIDES_DIR.glob(AH_GUIDE_GLOB))
    if len(guide_paths) != 16:
        raise ValueError(f"Expected 16 AH guides, found {len(guide_paths)}")

    for path in guide_paths:
        source = path.read_text(encoding="utf-8")
        expected = transform_guide(
            source,
            path.name,
            nav_template,
            baseline_note_template,
            vendor_template,
            crafted_template,
            dropped_scroll_template,
            vendor_config,
            crafted_config,
            dropped_scroll_config,
        )
        if expected == source:
            continue
        if args.check:
            print(f"Stale generated AH blocks: {path.relative_to(ROOT)}", file=sys.stderr)
            return 1
        path.write_text(expected, encoding="utf-8", newline="\n")
        changed.append(str(path.relative_to(ROOT)))

    if changed:
        print("Updated canonical AH blocks in:")
        for path in changed:
            print(f"- {path}")
    else:
        print("Canonical AH blocks are current.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
