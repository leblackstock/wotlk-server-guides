#!/usr/bin/env python3
"""Build the static Auction House item search index from the published guides."""

from __future__ import annotations

import argparse
import json
import re
import sys
import unicodedata
from html.parser import HTMLParser
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
HUB_PATH = ROOT / "auction-house.html"
OUTPUT_PATH = ROOT / "assets" / "ah-search-index.js"
AH_GUIDE_SUFFIX = "ah-price-guide.html"


def attr_map(attrs: list[tuple[str, str | None]]) -> dict[str, str]:
    return {key: value or "" for key, value in attrs}


def class_names(attrs: list[tuple[str, str | None]]) -> set[str]:
    return set(attr_map(attrs).get("class", "").split())


def clean_text(parts: list[str]) -> str:
    return " ".join("".join(parts).split())


def item_slug(value: str) -> str:
    value = "".join(
        character
        for character in unicodedata.normalize("NFKD", value)
        if unicodedata.category(character) != "Mn"
    )
    value = re.sub(r"['’]", "", value.lower())
    value = value.replace("&", " and ")
    return re.sub(r"[^a-z0-9]+", "-", value).strip("-")


class HubGuideParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.current_href: str | None = None
        self.capture_title = False
        self.title_parts: list[str] = []
        self.guides: dict[str, str] = {}

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = attr_map(attrs)
        if tag == "a" and "guide-card" in class_names(attrs):
            href = values.get("href", "")
            if href.endswith(AH_GUIDE_SUFFIX):
                self.current_href = href
        elif tag == "span" and self.current_href and "guide-title" in class_names(attrs):
            self.capture_title = True
            self.title_parts = []

    def handle_endtag(self, tag: str) -> None:
        if tag == "span" and self.capture_title:
            self.capture_title = False
            filename = Path(self.current_href or "").name
            self.guides[filename] = clean_text(self.title_parts)
        elif tag == "a":
            self.current_href = None

    def handle_data(self, data: str) -> None:
        if self.capture_title:
            self.title_parts.append(data)


class AHGuideParser(HTMLParser):
    def __init__(self, filename: str, guide_title: str) -> None:
        super().__init__()
        self.filename = filename
        self.guide_title = guide_title
        self.section = "Other"
        self.capture_heading = False
        self.capture_heading_action = False
        self.heading_parts: list[str] = []
        self.in_tbody = False
        self.in_row = False
        self.search_table_excluded = False
        self.cell_index = -1
        self.cell_parts: list[list[str]] = []
        self.cell_columns: list[str] = []
        self.current_cell_column = ""
        self.capture_name = False
        self.name_parts: list[str] = []
        self.capture_mini = False
        self.mini_parts: list[str] = []
        self.capture_target_bid = False
        self.target_bid_parts: list[str] = []
        self.capture_target_buyout = False
        self.target_buyout_parts: list[str] = []
        self.quality = "common"
        self.market_source = "market"
        self.profession = ""
        self.search_hint = ""
        self.search_excluded = False
        self.items: list[dict[str, str | int]] = []
        self.occurrences: dict[str, int] = {}

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = attr_map(attrs)
        classes = class_names(attrs)
        if tag == "h2":
            self.capture_heading = True
            self.heading_parts = []
        elif (
            tag == "a"
            and self.capture_heading
            and "ah-back-to-top" in classes
        ):
            self.capture_heading_action = True
        elif tag == "tbody":
            self.in_tbody = True
        elif tag == "table":
            self.search_table_excluded = values.get("data-table-family") == "reference"
        elif tag == "tr" and self.in_tbody:
            self.in_row = True
            self.market_source = values.get("data-market-source", "market")
            self.profession = values.get("data-profession", "")
            self.search_hint = values.get("data-search-hint", "").strip()
            self.search_excluded = (
                self.search_table_excluded
                or values.get("data-ah-search-exclude") == "true"
            )
            self.cell_index = -1
            self.cell_parts = []
            self.cell_columns = []
            self.current_cell_column = ""
            self.name_parts = []
            self.mini_parts = []
            self.target_bid_parts = []
            self.target_buyout_parts = []
            self.quality = "common"
        elif tag == "td" and self.in_row:
            self.cell_index += 1
            self.cell_parts.append([])
            self.current_cell_column = values.get("data-column", "")
            self.cell_columns.append(self.current_cell_column)
        elif tag == "strong" and self.in_row and self.cell_index == 0:
            quality_class = next((name for name in classes if name.startswith("q-")), "q-common")
            self.quality = quality_class.removeprefix("q-")
            self.capture_name = True
        elif tag == "div" and self.in_row and self.cell_index == 0 and "mini" in classes:
            self.capture_mini = True
        elif (
            tag == "span"
            and self.in_row
            and self.current_cell_column == "target"
            and "bid" in classes
        ):
            self.capture_target_bid = True
        elif (
            tag == "span"
            and self.in_row
            and self.current_cell_column == "target"
            and "buyout" in classes
        ):
            self.capture_target_buyout = True

    def handle_endtag(self, tag: str) -> None:
        if tag == "h2" and self.capture_heading:
            self.capture_heading = False
            self.capture_heading_action = False
            heading = clean_text(self.heading_parts)
            if heading:
                self.section = heading
        elif tag == "a" and self.capture_heading_action:
            self.capture_heading_action = False
        elif tag == "strong" and self.capture_name:
            self.capture_name = False
        elif tag == "div" and self.capture_mini:
            self.capture_mini = False
        elif tag == "span" and self.capture_target_bid:
            self.capture_target_bid = False
        elif tag == "span" and self.capture_target_buyout:
            self.capture_target_buyout = False
        elif tag == "tr" and self.in_row:
            self._finish_row()
            self.in_row = False
        elif tag == "tbody":
            self.in_tbody = False
        elif tag == "table":
            self.search_table_excluded = False

    def handle_data(self, data: str) -> None:
        if self.capture_heading and not self.capture_heading_action:
            self.heading_parts.append(data)
        if self.in_row and self.cell_index >= 0:
            self.cell_parts[self.cell_index].append(data)
        if self.capture_name:
            self.name_parts.append(data)
        if self.capture_mini:
            self.mini_parts.append(data)
        if self.capture_target_bid:
            self.target_bid_parts.append(data)
        if self.capture_target_buyout:
            self.target_buyout_parts.append(data)

    def _finish_row(self) -> None:
        if self.search_excluded:
            return
        name = clean_text(self.name_parts)
        if not name:
            return

        slug = item_slug(name)
        occurrence = self.occurrences.get(slug, 0) + 1
        self.occurrences[slug] = occurrence
        fragment = f"ah-item={slug}"
        if occurrence > 1:
            fragment += f"&occurrence={occurrence}"

        demand = ""
        if "demand" in self.cell_columns:
            demand = clean_text(self.cell_parts[self.cell_columns.index("demand")])
        stack = "1"
        if "stack" in self.cell_columns:
            stack = clean_text(self.cell_parts[self.cell_columns.index("stack")]) or "1"
        item: dict[str, str | int] = {
            "name": name,
            "detail": clean_text(self.mini_parts),
            "guide": self.guide_title,
            "section": self.section,
            "targetBid": clean_text(self.target_bid_parts) or "—",
            "target": clean_text(self.target_buyout_parts) or "—",
            "stack": stack,
            "demand": demand or "—",
            "quality": self.quality,
            "marketSource": self.market_source,
            "profession": self.profession,
            "href": f"./guides/{self.filename}#{fragment}",
            "occurrence": occurrence,
        }
        if self.search_hint:
            item["conversionHint"] = self.search_hint
        self.items.append(item)


def build_index() -> str:
    hub_parser = HubGuideParser()
    hub_parser.feed(HUB_PATH.read_text(encoding="utf-8"))
    if not hub_parser.guides:
        raise RuntimeError("No Auction House guide cards were found in auction-house.html")

    items: list[dict[str, str | int]] = []
    for filename, guide_title in hub_parser.guides.items():
        path = ROOT / "guides" / filename
        if not path.is_file():
            raise FileNotFoundError(f"Hub links to missing AH guide: {path.relative_to(ROOT)}")
        parser = AHGuideParser(filename, guide_title)
        parser.feed(path.read_text(encoding="utf-8"))
        if not parser.items:
            raise RuntimeError(f"No searchable item rows found in {path.relative_to(ROOT)}")
        items.extend(parser.items)

    items.sort(key=lambda item: (str(item["name"]).casefold(), str(item["guide"]).casefold()))
    payload = {
        "version": 4,
        "guideCount": len(hub_parser.guides),
        "itemCount": len(items),
        "items": items,
    }
    compact_json = json.dumps(payload, ensure_ascii=False, separators=(",", ":"))
    return (
        "/* Generated by scripts/build-ah-search-index.py. Do not edit directly. */\n"
        f"window.AH_SEARCH_INDEX={compact_json};\n"
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Fail if the committed index is stale")
    args = parser.parse_args()

    output = build_index()
    if args.check:
        if not OUTPUT_PATH.is_file() or OUTPUT_PATH.read_text(encoding="utf-8") != output:
            print("AH search index is stale. Run: python scripts/build-ah-search-index.py", file=sys.stderr)
            return 1
        print("AH search index is current.")
        return 0

    OUTPUT_PATH.write_text(output, encoding="utf-8", newline="\n")
    payload = json.loads(output.split("=", 1)[1].removesuffix(";\n"))
    print(f"Wrote {payload['itemCount']} items from {payload['guideCount']} guides to {OUTPUT_PATH.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
