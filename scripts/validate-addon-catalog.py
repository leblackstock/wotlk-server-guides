#!/usr/bin/env python3
"""Validate the WotLK addon catalog, generated data, local assets, and key links."""
from __future__ import annotations

import argparse
import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "data" / "addons.json"
GENERATED = ROOT / "assets" / "addon-catalog-data.js"
REQUIRED_ADDONS = {
    "pallypower",
    "protection-is-surprisingly-stupendous",
    "deadly-boss-mods",
    "omen3",
    "tauntmaster",
    "healbot",
    "omnicc",
    "weakauras",
    "ratingbuster",
    "questie",
    "skada",
    "chatter",
    "auctioneer-suite",
}
TESTED_HELLSCREAM_ADDONS = {"questie", "skada", "chatter", "auctioneer-suite"}
AUDIENCE_KEYS = {
    "classes": "class",
    "specs": "specialization",
    "roles": "role",
    "professions": "profession",
    "activities": "activity",
    "raids": None,
    "encounters": None,
}


class LinkParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.links: list[tuple[str, str]] = []
        self.images: list[tuple[str, str]] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = {key: value or "" for key, value in attrs}
        if tag in {"a", "link", "script"}:
            key = "href" if tag in {"a", "link"} else "src"
            if values.get(key):
                self.links.append((tag, values[key]))
        if tag == "img":
            self.images.append((values.get("src", ""), values.get("alt", "")))


def normalized(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", value.lower()).strip()


def local_target(html_path: Path, raw: str) -> Path | None:
    if not raw or raw.startswith(("#", "mailto:", "tel:", "javascript:")):
        return None
    parsed = urlparse(raw)
    if parsed.scheme or parsed.netloc:
        return None
    clean = parsed.path
    if not clean:
        return None
    return (html_path.parent / clean).resolve()


def fail(errors: list[str], message: str) -> None:
    errors.append(message)


def main() -> int:
    parser_args = argparse.ArgumentParser(description=__doc__)
    parser_args.add_argument("--partial", action="store_true", help="Validate new catalog files before they are placed in the full repository")
    args = parser_args.parse_args()
    errors: list[str] = []
    payload = json.loads(SOURCE.read_text(encoding="utf-8"))
    addons = payload.get("addons", [])
    tags = payload.get("tags", [])
    groups = {group["id"]: group for group in payload.get("tagGroups", [])}
    tag_by_id = {tag["id"]: tag for tag in tags}
    importance_ids = {item["id"] for item in payload.get("importanceLevels", [])}
    purpose_ids = {item["id"] for item in payload.get("purposes", [])}

    addon_ids = [addon.get("id", "") for addon in addons]
    if set(addon_ids) != REQUIRED_ADDONS or len(addons) != len(REQUIRED_ADDONS):
        fail(errors, f"Catalog must contain exactly the approved addons; found {addon_ids!r}")
    if len(addon_ids) != len(set(addon_ids)):
        fail(errors, "Addon IDs must be unique")
    if len(tag_by_id) != len(tags):
        fail(errors, "Tag IDs must be unique")

    registered_values: dict[str, set[str]] = {}
    for tag in tags:
        if tag.get("group") not in groups:
            fail(errors, f"Tag {tag.get('id')} references unknown group {tag.get('group')}")
        registered_values.setdefault(tag.get("group", ""), set()).add(tag.get("id", ""))

    aliases: dict[str, str] = {}
    required_fields = {"id", "name", "summary", "does", "doesNot", "generalSetup", "tags", "scope", "compatibility", "download", "icon"}
    for addon in addons:
        addon_id = addon.get("id", "<missing>")
        missing = required_fields - addon.keys()
        if missing:
            fail(errors, f"{addon_id}: missing required fields {sorted(missing)}")
        if len(addon.get("summary", "")) > 180:
            fail(errors, f"{addon_id}: summary exceeds 180 characters")
        if len(addon.get("does", [])) > 3:
            fail(errors, f"{addon_id}: 'does' exceeds three bullets")
        if len(addon.get("doesNot", [])) > 2:
            fail(errors, f"{addon_id}: 'doesNot' exceeds two bullets")
        if len(addon.get("generalSetup", [])) > 5:
            fail(errors, f"{addon_id}: general setup exceeds five steps")
        module_names: list[str] = []
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

        unknown_tags = sorted(set(addon.get("tags", [])) - tag_by_id.keys())
        if unknown_tags:
            fail(errors, f"{addon_id}: unknown tags {unknown_tags}")
        unknown_featured = sorted(set(addon.get("featuredTags", [])) - set(addon.get("tags", [])))
        if unknown_featured:
            fail(errors, f"{addon_id}: featured tags are not assigned tags {unknown_featured}")

        for value in [addon.get("name", ""), *addon.get("aliases", [])]:
            key = normalized(value)
            if not key:
                continue
            prior = aliases.get(key)
            if prior and prior != addon_id:
                fail(errors, f"Ambiguous alias/name {value!r}: {prior} and {addon_id}")
            aliases[key] = addon_id

        download_url = addon.get("download", {}).get("url", "")
        parsed = urlparse(download_url)
        if parsed.scheme != "https" or not parsed.netloc:
            fail(errors, f"{addon_id}: invalid HTTPS download URL {download_url!r}")
        icon = addon.get("icon", {})
        icon_path = ROOT / icon.get("path", "")
        if not icon_path.is_file():
            fail(errors, f"{addon_id}: missing icon {icon_path.relative_to(ROOT) if icon_path.is_relative_to(ROOT) else icon_path}")
        if not icon.get("alt", "").strip():
            fail(errors, f"{addon_id}: icon alt text is required")

        compatibility = addon.get("compatibility", {})
        if compatibility.get("hellscreamTested"):
            if addon_id not in TESTED_HELLSCREAM_ADDONS:
                fail(errors, f"{addon_id}: Hellscream-tested claim lacks documented evidence")
            if "tested-hellscream" not in addon.get("tags", []):
                fail(errors, f"{addon_id}: Hellscream-tested record needs the tested-hellscream tag")
            if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", compatibility.get("hellscreamTestedDate", "")):
                fail(errors, f"{addon_id}: Hellscream-tested record needs an ISO test date")
        if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", compatibility.get("lastReviewed", "")):
            fail(errors, f"{addon_id}: last-reviewed date must use YYYY-MM-DD")

        for collection_name in ("recommendations", "customizations"):
            for record in addon.get(collection_name, []):
                audience = record.get("audience", {})
                for key, values in audience.items():
                    group = AUDIENCE_KEYS.get(key)
                    if key not in AUDIENCE_KEYS:
                        fail(errors, f"{addon_id}: unknown audience key {key}")
                    elif group:
                        unknown = sorted(set(values) - registered_values.get(group, set()))
                        if unknown:
                            fail(errors, f"{addon_id}: invalid {key} values {unknown}")
                if collection_name == "recommendations":
                    if record.get("importance") not in importance_ids:
                        fail(errors, f"{addon_id}: invalid importance {record.get('importance')}")
                    unknown_purposes = sorted(set(record.get("purposes", [])) - purpose_ids)
                    if unknown_purposes:
                        fail(errors, f"{addon_id}: invalid purposes {unknown_purposes}")
                    if len(record.get("reason", "")) > 320:
                        fail(errors, f"{addon_id}: recommendation reason is too long")
                else:
                    if len(record.get("setup", [])) > 5:
                        fail(errors, f"{addon_id}: targeted setup exceeds five steps")
                    if len(record.get("does", [])) > 3 or len(record.get("doesNot", [])) > 2:
                        fail(errors, f"{addon_id}: targeted content exceeds bullet limits")

        for media in addon.get("screenshots", []):
            path = ROOT / media.get("path", "")
            if not path.is_file():
                fail(errors, f"{addon_id}: missing screenshot {media.get('path')}")
            if not media.get("alt", "").strip():
                fail(errors, f"{addon_id}: screenshot alt text is required")
        for video in addon.get("videos", []):
            parsed_video = urlparse(video.get("url", ""))
            if parsed_video.scheme != "https" or not parsed_video.netloc:
                fail(errors, f"{addon_id}: invalid video URL")

    if GENERATED.is_file():
        expected = (
            "/* Generated by scripts/build-addon-catalog.py. Do not edit directly. */\n"
            f"window.ADDON_CATALOG={json.dumps(payload, ensure_ascii=False, separators=(',', ':'))};\n"
        )
        if GENERATED.read_text(encoding="utf-8") != expected:
            fail(errors, "Generated addon browser data does not match data/addons.json")
    else:
        fail(errors, "Missing generated assets/addon-catalog-data.js")

    html_files = [
        ROOT / "guides" / "addons.html",
        ROOT / "index.html",
        ROOT / "guides" / "protection-paladin-setting-up.html",
        ROOT / "internal" / "color-system.html",
    ]
    for html_path in html_files:
        if not html_path.is_file():
            if not args.partial:
                fail(errors, f"Missing required HTML file {html_path.relative_to(ROOT)}")
            continue
        text = html_path.read_text(encoding="utf-8")
        if "your server" in text.lower():
            fail(errors, f"{html_path.relative_to(ROOT)} uses prohibited public wording 'your server'")
        parser = LinkParser()
        parser.feed(text)
        for _, raw in parser.links:
            target = local_target(html_path, raw)
            if target and not target.exists() and not args.partial:
                fail(errors, f"{html_path.relative_to(ROOT)} has broken local link {raw}")
        for raw, alt in parser.images:
            target = local_target(html_path, raw)
            if target and not target.exists() and not args.partial:
                fail(errors, f"{html_path.relative_to(ROOT)} has missing local image {raw}")
            if html_path.name == "addons.html" and raw and not alt.strip():
                fail(errors, f"{html_path.relative_to(ROOT)} image {raw} lacks alt text")

    addon_html = (ROOT / "guides" / "addons.html").read_text(encoding="utf-8") if (ROOT / "guides" / "addons.html").is_file() else ""
    for required in ["addon-search-input", "addon-filter-groups", "addon-result-count", "addon-details-dialog"]:
        if f'id="{required}"' not in addon_html:
            fail(errors, f"guides/addons.html is missing required accessible control {required}")
    if "<noscript>" not in addon_html:
        fail(errors, "guides/addons.html needs a no-JavaScript fallback")

    if errors:
        print("Addon catalog validation failed:", file=sys.stderr)
        for error in errors:
            print(f" - {error}", file=sys.stderr)
        return 1
    print(f"Addon catalog validation passed: {len(addons)} addons, {len(tags)} registered tags.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
