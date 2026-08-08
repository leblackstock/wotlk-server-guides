#!/usr/bin/env python3
"""Validate the split Auction House hub and main-hub entry point."""

from __future__ import annotations

from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse


ROOT = Path(__file__).resolve().parents[1]
MAIN_HUB = ROOT / "index.html"
AH_HUB = ROOT / "auction-house.html"


class PageParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.ids: list[str] = []
        self.links: list[tuple[str, set[str]]] = []
        self.guide_card_count = 0
        self.route_card_count = 0
        self.link_card_count = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = {key: value or "" for key, value in attrs}
        if values.get("id"):
            self.ids.append(values["id"])
        classes = set(values.get("class", "").split())
        if "guide-card" in classes:
            self.guide_card_count += 1
        if "ah-hub-route-card" in classes:
            self.route_card_count += 1
        if "ah-hub-link-card" in classes:
            self.link_card_count += 1
        if tag == "a" and values.get("href"):
            self.links.append((values["href"], classes))


def parse(path: Path) -> PageParser:
    parser = PageParser()
    parser.feed(path.read_text(encoding="utf-8"))
    return parser


def local_target(page: Path, raw_href: str) -> Path | None:
    parsed = urlparse(raw_href)
    if parsed.scheme or parsed.netloc or not parsed.path:
        return None
    return (page.parent / parsed.path).resolve()


def main() -> int:
    errors: list[str] = []
    main_hub = parse(MAIN_HUB)
    ah_hub = parse(AH_HUB)
    ah_hub_source = AH_HUB.read_text(encoding="utf-8")

    if len(main_hub.ids) != len(set(main_hub.ids)):
        errors.append("index.html contains duplicate IDs")
    if len(ah_hub.ids) != len(set(ah_hub.ids)):
        errors.append("auction-house.html contains duplicate IDs")
    if "Active listings show competition only and never set or raise guide prices." not in ah_hub_source:
        errors.append("auction-house.html is missing the non-circular pricing notice")
    if "These are suggested starting prices, not live AH data." in ah_hub_source:
        errors.append("auction-house.html still contains the superseded live-AH price notice")

    browse_links = [
        href
        for href, classes in main_hub.links
        if "ah-hub-browse" in classes
    ]
    if browse_links != ["./auction-house.html"]:
        errors.append("Main hub must contain one AH Browse button linking to ./auction-house.html")

    for required_id in ("ah-search-input", "ah-search-status", "ah-search-results"):
        if required_id not in main_hub.ids:
            errors.append(f"index.html is missing #{required_id}")
        if required_id not in ah_hub.ids:
            errors.append(f"auction-house.html is missing #{required_id}")

    for required_id in ("addon-hub-search-input", "addon-hub-search-status", "addon-hub-search-results", "addon-hub-browse"):
        if required_id not in main_hub.ids:
            errors.append(f"index.html is missing #{required_id}")

    main_ah_chips = [
        href
        for href, classes in main_hub.links
        if "library-hub-chip" in classes and "addons.html" not in href
    ]
    if len(main_ah_chips) != 6:
        errors.append(f"Main AH search must contain six popular-guide chips; found {len(main_ah_chips)}")
    if "./guides/bags-containers-ah-guide.html" not in main_ah_chips:
        errors.append("Main AH search must link to the Bags & Containers collection")
    if "./guides/merchants-guild.html" not in main_ah_chips:
        errors.append("Main AH search must link to The Merchant’s Guild page")

    ah_page_chips = [
        href
        for href, classes in ah_hub.links
        if "library-hub-chip" in classes
    ]
    if ah_page_chips != main_ah_chips:
        errors.append("Main and dedicated AH searches must use the same popular-guide chips")

    addon_chips = [
        href
        for href, classes in main_hub.links
        if "library-hub-chip" in classes and "addons.html" in href
    ]
    if len(addon_chips) != 4:
        errors.append(f"Main Addon search must contain four popular-filter chips; found {len(addon_chips)}")

    main_ah_cards = [
        href
        for href, classes in main_hub.links
        if "guide-card" in classes and href.endswith("ah-price-guide.html")
    ]
    if main_ah_cards:
        errors.append("AH guide cards must not remain on index.html")

    ah_cards = [
        href
        for href, classes in ah_hub.links
        if ("guide-card" in classes or "ah-hub-card-chip" in classes)
        and urlparse(href).path.endswith("ah-price-guide.html")
    ]
    ah_card_paths = [urlparse(href).path for href in ah_cards]
    if ah_hub.guide_card_count != 17:
        errors.append(f"auction-house.html must contain 17 visible cards; found {ah_hub.guide_card_count}")
    if ah_hub.route_card_count != 4 or ah_hub.link_card_count != 1:
        errors.append("auction-house.html must contain three grouped cards and one category link card")
    if len(ah_cards) != 19 or len(set(ah_card_paths)) != 18:
        errors.append(
            "auction-house.html must expose 18 active guide routes plus the Skinning category link"
        )
    skinning_path = "./guides/skinning-leatherworking-materials-ah-price-guide.html"
    if ah_card_paths.count(skinning_path) != 2:
        errors.append("Skinning & Leatherworking must have one full-guide route and one materials shortcut")
    if (
        skinning_path + "#ah-category=leatherworking-materials"
        not in ah_cards
    ):
        errors.append("Gathering must link directly to the Skinning materials category")
    container_cards = [
        href
        for href, classes in ah_hub.links
        if "ah-hub-collection-card" in classes
    ]
    if container_cards != ["./guides/bags-containers-ah-guide.html"]:
        errors.append("Drops must contain one Bags & Containers collection card")

    for page, parsed in ((MAIN_HUB, main_hub), (AH_HUB, ah_hub)):
        for href, _ in parsed.links:
            target = local_target(page, href)
            if target and not target.exists():
                errors.append(f"{page.name} has broken local link {href}")

    if errors:
        print("Auction House hub validation failed:")
        for error in errors:
            print(f" - {error}")
        return 1

    print("Hub validation passed: 18 active guides plus the Bags & Containers collection across 17 cards.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
