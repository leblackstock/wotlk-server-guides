#!/usr/bin/env python3
"""Build the static Auction House item search index from the published guides."""

from __future__ import annotations

import argparse
import json
import math
import re
import sys
import unicodedata
from fractions import Fraction
from html.parser import HTMLParser
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
HUB_PATH = ROOT / "auction-house.html"
OUTPUT_PATH = ROOT / "assets" / "ah-search-index.js"
CANONICAL_VALUES_PATH = ROOT / "data" / "ah-search-canonical-values.json"
VENDOR_RECOMMENDATIONS_PATH = ROOT / "data" / "ah-vendor-recommendations.json"
ITEM_IDS_PATH = ROOT / "assets" / "ah-item-ids.js"
ELIGIBILITY_AUDIT_PATH = ROOT / "data" / "ah-auction-eligibility-audit.json"
COLLECTIBLE_AUDIT_PATH = ROOT / "data" / "ah-collectible-audit.json"
GUIDE_MANIFEST_PATH = ROOT / "data" / "ah-guides.json"
AH_GUIDE_SUFFIX = "ah-price-guide.html"
GENERATED_OBJECT = re.compile(r"window\.(\w+)=(\{.*?\});(?:\n|$)", re.DOTALL)
MONEY_PART = re.compile(r"([0-9][0-9,]*)\s*([gsc])")


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


def item_lookup_key(value: str) -> str:
    return item_slug(value).replace("-", " ")


def generated_json(path: Path, variable: str) -> dict[str, object]:
    source = path.read_text(encoding="utf-8")
    for match in GENERATED_OBJECT.finditer(source):
        if match.group(1) == variable:
            return json.loads(match.group(2))
    raise RuntimeError(f"Could not parse {variable} from {path.relative_to(ROOT)}")


def parse_money(value: str) -> int | None:
    value = value.strip()
    if not value or value == "—":
        return None
    matches = MONEY_PART.findall(value)
    remainder = MONEY_PART.sub("", value).strip()
    if not matches or remainder:
        raise RuntimeError(f"Unsupported AH money value: {value!r}")
    multipliers = {"g": 10_000, "s": 100, "c": 1}
    return sum(int(amount.replace(",", "")) * multipliers[unit] for amount, unit in matches)


def format_money(copper: int) -> str:
    if copper < 0:
        raise ValueError("Copper values cannot be negative")
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


def stack_counts(value: str) -> list[int]:
    if not value or value == "—":
        return [1]
    counts = [
        int(part.strip())
        for part in value.split("/")
        if re.fullmatch(r"[0-9]+", part.strip())
    ]
    if not counts or any(count < 1 for count in counts):
        raise RuntimeError(f"Unsupported AH stack recommendation: {value!r}")
    return counts


def price_basis_count(item: dict[str, object]) -> int:
    value = str(item.get("priceBasis", "")).strip()
    if not value:
        return 1
    match = re.fullmatch(r"Stack of ([0-9]+)", value)
    if not match:
        raise RuntimeError(f"Unsupported AH price basis: {value!r}")
    return int(match.group(1))


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
    def __init__(
        self,
        filename: str,
        guide_id: str,
        guide_title: str,
        vendor_recommendation_names: set[str] | None = None,
    ) -> None:
        super().__init__()
        self.filename = filename
        self.guide_id = guide_id
        self.guide_title = guide_title
        self.vendor_recommendation_names = vendor_recommendation_names or set()
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
        self.capture_price_basis = False
        self.price_basis_parts: list[str] = []
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
            self.price_basis_parts = []
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
            and self.cell_index == 0
            and "ah-price-stack-chip" in classes
        ):
            self.capture_price_basis = True
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
        elif tag == "span" and self.capture_price_basis:
            self.capture_price_basis = False
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
        if self.capture_price_basis:
            self.price_basis_parts.append(data)
        if self.capture_target_bid:
            self.target_bid_parts.append(data)
        if self.capture_target_buyout:
            self.target_buyout_parts.append(data)

    def _finish_row(self) -> None:
        name = clean_text(self.name_parts)
        if not name:
            return
        vendor_recommended = name in self.vendor_recommendation_names
        if self.search_excluded and not vendor_recommended:
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
            "guideId": self.guide_id,
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
        price_basis = clean_text(self.price_basis_parts)
        if price_basis:
            item["priceBasis"] = price_basis
        if self.search_excluded and vendor_recommended:
            item["_vendorReferencePromotion"] = True
        self.items.append(item)


def load_canonical_values() -> dict[str, object]:
    if not CANONICAL_VALUES_PATH.is_file():
        raise FileNotFoundError(
            f"Missing canonical AH search values: {CANONICAL_VALUES_PATH.relative_to(ROOT)}"
        )
    data = json.loads(CANONICAL_VALUES_PATH.read_text(encoding="utf-8"))
    if data.get("version") != 1:
        raise RuntimeError("Unsupported AH search canonical-values version")
    return data


def load_vendor_recommendations() -> dict[str, object]:
    if not VENDOR_RECOMMENDATIONS_PATH.is_file():
        raise FileNotFoundError(
            "Missing vendor recommendations: "
            f"{VENDOR_RECOMMENDATIONS_PATH.relative_to(ROOT)}"
        )
    data = json.loads(VENDOR_RECOMMENDATIONS_PATH.read_text(encoding="utf-8"))
    if data.get("version") != 2:
        raise RuntimeError("Unsupported vendor-recommendations version")
    return data


def load_vendor_sell_prices(audit: dict[str, object]) -> dict[str, int]:
    model = audit.get("margin_model")
    if not isinstance(model, dict):
        raise RuntimeError("Vendor recommendations are missing margin_model")

    item_ids = generated_json(ITEM_IDS_PATH, "AH_ITEM_IDS")
    eligibility = json.loads(ELIGIBILITY_AUDIT_PATH.read_text(encoding="utf-8"))
    source = eligibility.get("item_template_source")
    if not isinstance(source, dict) or source.get("commit") != model.get("sell_price_source_commit"):
        raise RuntimeError("Vendor margin model and eligibility SellPrice source do not match")
    records = eligibility.get("items")
    if not isinstance(records, dict):
        raise RuntimeError("Auction-eligibility audit is missing item records")

    name_ids = {str(key): int(raw_item_id) for key, raw_item_id in item_ids.items()}
    if COLLECTIBLE_AUDIT_PATH.is_file():
        collectible = json.loads(COLLECTIBLE_AUDIT_PATH.read_text(encoding="utf-8"))
        for raw_item_id, item in collectible.get("items", {}).items():
            if not isinstance(item, dict):
                raise RuntimeError("Collectible audit contains an invalid item record")
            key = item_lookup_key(str(item["name"]))
            item_id = int(raw_item_id)
            existing = name_ids.get(key)
            if existing is not None and existing != item_id:
                existing_record = records.get(str(existing))
                new_record = records.get(str(item_id))
                if (
                    not isinstance(existing_record, dict)
                    or not isinstance(new_record, dict)
                    or int(existing_record.get("sell_price_copper", -1))
                    != int(new_record.get("sell_price_copper", -2))
                ):
                    raise RuntimeError(
                        f"Same-name collectible IDs have different NPC SellPrice values for "
                        f"{key!r}: {existing} versus {item_id}"
                    )
                continue
            name_ids[key] = item_id

    prices: dict[str, int] = {}
    for key, raw_item_id in name_ids.items():
        item_id = str(raw_item_id)
        record = records.get(item_id)
        if not isinstance(record, dict) or "sell_price_copper" not in record:
            raise RuntimeError(f"Saved NPC SellPrice is missing for item {item_id} ({key})")
        sell_price = int(record["sell_price_copper"])
        if sell_price < 0:
            raise RuntimeError(f"Saved NPC SellPrice is invalid for item {item_id} ({key})")
        prices[str(key)] = sell_price
    return prices


def concise_recommendation_note(entry: dict[str, object], label: str) -> str:
    note = str(entry.get("vendor_note", "")).strip()
    if not note:
        raise RuntimeError(f"{label} is missing vendor_note")
    if "\n" in note or len(note) > 60:
        raise RuntimeError(f"{label} vendor_note must be one short line: {note!r}")
    return note


def recommendation_notes(data: dict[str, object]) -> dict[tuple[str, str], str]:
    recommendations = data.get("item_recommendations")
    if not isinstance(recommendations, list) or not recommendations:
        raise RuntimeError("Manual item vendor recommendations must not be empty")

    notes: dict[tuple[str, str], str] = {}
    for entry in recommendations:
        if not isinstance(entry, dict):
            raise RuntimeError("Every manual item vendor recommendation must be an object")
        key = (str(entry.get("guide_id", "")), str(entry.get("name", "")))
        if not all(key):
            raise RuntimeError("Every vendor recommendation needs guide_id and name")
        if key in notes:
            raise RuntimeError(f"Duplicate manual item vendor recommendation: {key!r}")
        notes[key] = concise_recommendation_note(entry, f"Item recommendation {key!r}")
    return notes


def recommendation_keys(data: dict[str, object]) -> set[tuple[str, str]]:
    return set(recommendation_notes(data))


def section_recommendation_notes(data: dict[str, object]) -> dict[tuple[str, str], str]:
    recommendations = data.get("section_recommendations")
    if not isinstance(recommendations, list) or not recommendations:
        raise RuntimeError("Manual section vendor recommendations must not be empty")

    notes: dict[tuple[str, str], str] = {}
    for entry in recommendations:
        if not isinstance(entry, dict):
            raise RuntimeError("Every low-demand section recommendation must be an object")
        key = (str(entry.get("guide_id", "")), str(entry.get("section", "")))
        if not all(key):
            raise RuntimeError("Every section recommendation needs guide_id and section")
        if key in notes:
            raise RuntimeError(f"Duplicate low-demand section recommendation: {key!r}")
        notes[key] = concise_recommendation_note(entry, f"Section recommendation {key!r}")
    return notes


def section_recommendation_keys(data: dict[str, object]) -> set[tuple[str, str]]:
    return set(section_recommendation_notes(data))


def grouped_items(
    items: list[dict[str, str | int]],
) -> dict[str, list[dict[str, str | int]]]:
    groups: dict[str, list[dict[str, str | int]]] = {}
    for item in items:
        groups.setdefault(item_slug(str(item["name"])), []).append(item)
    return groups


def apply_canonical_field(
    groups: dict[str, list[dict[str, str | int]]],
    entries: dict[str, dict[str, str | int]],
    field: str,
) -> None:
    for name, entry in entries.items():
        group = groups.get(item_slug(name))
        if not group:
            raise RuntimeError(f"Canonical {field} item is absent from the search index: {name}")

        source_guide = str(entry.get("source_guide_id") or entry.get("source_guide"))
        value = str(entry["value"])
        source_values = {
            str(item[field])
            for item in group
            if str(item.get("guideId", item["guide"])) == source_guide
        }
        if not source_values:
            raise RuntimeError(
                f"Canonical {field} source guide is absent for {name}: {source_guide}"
            )
        if source_values != {value}:
            raise RuntimeError(
                f"Canonical {field} for {name} is {value!r}, but {source_guide} has "
                f"{sorted(source_values)!r}"
            )

        if field == "stack":
            max_stack = int(entry["max_stack"])
            stack_counts = [int(part.strip()) for part in value.split("/")]
            if max_stack < 1 or any(count < 1 or count > max_stack for count in stack_counts):
                raise RuntimeError(
                    f"Canonical stack for {name} exceeds its verified max stack "
                    f"{max_stack}: {value}"
                )
            for item in group:
                raw_value = str(item[field])
                raw_counts = [int(part.strip()) for part in raw_value.split("/")]
                if any(count < 1 or count > max_stack for count in raw_counts):
                    raise RuntimeError(
                        f"Stack recommendation for {name} in {item['guide']} exceeds its "
                        f"verified max stack {max_stack}: {raw_value}"
                    )

        for item in group:
            item[field] = value


def canonicalize_and_validate(items: list[dict[str, str | int]]) -> None:
    canonical = load_canonical_values()
    groups = grouped_items(items)
    apply_canonical_field(groups, canonical.get("canonical_stack", {}), "stack")
    apply_canonical_field(groups, canonical.get("canonical_demand", {}), "demand")

    conflicts: list[str] = []
    for group in groups.values():
        if len(group) < 2:
            continue
        for field in ("targetBid", "target", "stack", "demand"):
            values = sorted({str(item[field]) for item in group})
            if len(values) > 1:
                conflicts.append(f"{group[0]['name']} {field}: {values!r}")
    if conflicts:
        details = "\n  - ".join(conflicts)
        raise RuntimeError(
            "Duplicate AH search entries need a single canonical value. "
            "Fix the source rows or data/ah-search-canonical-values.json:\n  - " + details
        )


def vendor_margin_evaluation(
    item: dict[str, object],
    sell_price_copper: int,
    model: dict[str, object],
) -> dict[str, int | Fraction]:
    target_copper = parse_money(str(item["target"]))
    if target_copper is None:
        raise RuntimeError(f"Cannot evaluate an unpriced AH row: {item['name']}")
    basis_count = price_basis_count(item)
    listing_count = max(stack_counts(str(item["stack"])))
    if listing_count < basis_count or listing_count % basis_count:
        raise RuntimeError(
            f"Recommended stack does not align with the price basis for {item['name']}: "
            f"{listing_count} versus {basis_count}"
        )

    cut_bp = int(model["auction_cut_basis_points"])
    standard_deposit_bp = int(model["standard_12h_deposit_basis_points"])
    server_deposit_multiplier_bp = int(model["hellscream_deposit_multiplier_basis_points"])
    minimum_deposit = int(model["minimum_deposit_copper"])
    effort_floor = int(model["minimum_expected_profit_copper_per_listing"])
    probabilities = model.get("sale_probability_basis_points_by_demand")
    if not isinstance(probabilities, dict) or str(item["demand"]) not in probabilities:
        raise RuntimeError(f"Vendor margin model has no sale likelihood for {item['demand']!r}")
    sale_probability_bp = int(probabilities[str(item["demand"])])
    if not 0 < sale_probability_bp <= 10_000:
        raise RuntimeError(f"Invalid sale probability for {item['demand']!r}")
    if not 0 <= cut_bp < 10_000:
        raise RuntimeError("Invalid AH cut in vendor margin model")

    target_listing_copper = Fraction(target_copper * listing_count, basis_count)
    vendor_listing_copper = sell_price_copper * listing_count
    deposit_copper = max(
        minimum_deposit,
        vendor_listing_copper * standard_deposit_bp * server_deposit_multiplier_bp
        // 100_000_000,
    )
    sale_probability = Fraction(sale_probability_bp, 10_000)
    net_success = target_listing_copper * Fraction(10_000 - cut_bp, 10_000)
    expected_profit = (
        sale_probability * net_success
        + (1 - sale_probability) * (vendor_listing_copper - deposit_copper)
        - vendor_listing_copper
    )
    required_listing_gross = (
        vendor_listing_copper
        + Fraction(10_000 - sale_probability_bp, sale_probability_bp) * deposit_copper
        + Fraction(10_000, sale_probability_bp) * effort_floor
    ) / Fraction(10_000 - cut_bp, 10_000)
    minimum_target_copper = math.ceil(required_listing_gross * basis_count / listing_count)
    return {
        "target_copper": target_copper,
        "minimum_target_copper": minimum_target_copper,
        "listing_count": listing_count,
        "deposit_copper": deposit_copper,
        "target_listing_copper": target_listing_copper,
        "vendor_listing_copper": vendor_listing_copper,
        "net_success_copper": net_success,
        "expected_profit": expected_profit,
    }


def apply_vendor_recommendations(
    items: list[dict[str, str | int | bool]],
    audit: dict[str, object],
) -> int:
    item_notes = recommendation_notes(audit)
    section_notes = section_recommendation_notes(audit)
    keys = set(item_notes)
    section_keys = set(section_notes)
    model = audit.get("margin_model")
    if not isinstance(model, dict):
        raise RuntimeError("Vendor recommendations are missing margin_model")
    sell_prices = load_vendor_sell_prices(audit)
    vendor_resale_names = {
        item_lookup_key(str(item["name"]))
        for item in items
        if item["section"] == "Vendor & convenience items"
        or "coin vendor" in str(item.get("conversionHint", "")).casefold()
    }
    matched_keys: set[tuple[str, str]] = set()
    matched_section_keys: set[tuple[str, str]] = set()
    manual_count = 0
    automatic_count = 0
    below_vendor_after_cut_count = 0
    close_margin_count = 0
    recommendation_count = 0
    resolved_sell_price_count = 0
    zero_sell_price_count = 0
    vendor_resale_excluded_count = 0
    margin_evaluated_count = 0
    unpriced_reference_count = 0
    for item in items:
        key = (str(item["guideId"]), str(item["name"]))
        section_key = (str(item["guideId"]), str(item["section"]))
        manual = key in keys or section_key in section_keys
        manual_note = item_notes.get(key) or section_notes.get(section_key)
        if manual:
            manual_count += 1
            if key in matched_keys and key in keys:
                raise RuntimeError(f"Vendor recommendation matched multiple search rows: {key!r}")
            if item["section"] == "Vendor & convenience items":
                raise RuntimeError(f"NPC-vendor resale item cannot be a liquidation recommendation: {key!r}")
            if key in keys:
                matched_keys.add(key)
            if section_key in section_keys:
                matched_section_keys.add(section_key)

        lookup_key = item_lookup_key(str(item["name"]))
        sell_price = sell_prices.get(lookup_key)
        target_copper = parse_money(str(item["target"]))
        automatic = False
        automatic_note = ""
        evaluation: dict[str, int | Fraction] | None = None
        if sell_price is None:
            if not manual or target_copper is not None:
                raise RuntimeError(f"AH row lacks a saved item ID and NPC SellPrice: {key!r}")
            unpriced_reference_count += 1
        else:
            resolved_sell_price_count += 1
            if lookup_key in vendor_resale_names:
                vendor_resale_excluded_count += 1
            elif sell_price == 0:
                zero_sell_price_count += 1
            elif target_copper is None:
                if not manual:
                    raise RuntimeError(f"Priced AH row unexpectedly lacks a Target: {key!r}")
                unpriced_reference_count += 1
            else:
                margin_evaluated_count += 1
                evaluation = vendor_margin_evaluation(item, sell_price, model)
                automatic = int(evaluation["target_copper"]) < int(
                    evaluation["minimum_target_copper"]
                )
                if automatic:
                    automatic_count += 1
                    if evaluation["net_success_copper"] <= evaluation["vendor_listing_copper"]:
                        below_vendor_after_cut_count += 1
                        automatic_note = "AH net is below NPC value."
                    else:
                        close_margin_count += 1
                        automatic_note = "Expected profit is too small."

        if manual or automatic:
            item["vendorRecommended"] = True
            item["vendorRecommendationNote"] = automatic_note or manual_note
            if not item["vendorRecommendationNote"]:
                raise RuntimeError(f"Vendor recommendation lacks a short note: {key!r}")
            recommendation_count += 1
            if manual and automatic:
                item["vendorRecommendationSource"] = "manual-and-margin"
            elif manual:
                item["vendorRecommendationSource"] = "manual"
            else:
                item["vendorRecommendationSource"] = "margin"
            if automatic and evaluation is not None and sell_price is not None:
                item["vendorSell"] = format_money(sell_price)
                item["vendorMinimumTarget"] = format_money(
                    int(evaluation["minimum_target_copper"])
                )

    if matched_keys != keys:
        missing = sorted(keys - matched_keys)
        raise RuntimeError(f"Vendor recommendations are absent from the search index: {missing!r}")
    if matched_section_keys != section_keys:
        missing = sorted(section_keys - matched_section_keys)
        raise RuntimeError(
            f"Vendor-recommended sections are absent from the search index: {missing!r}"
        )

    by_name = grouped_items(items)
    for group in by_name.values():
        flags = {item.get("vendorRecommended", False) for item in group}
        if len(flags) > 1:
            raise RuntimeError(
                f"Grouped item mixes Vendor and normal recommendations: {group[0]['name']}"
            )

    scope = audit.get("reviewed_scope")
    if not isinstance(scope, dict):
        raise RuntimeError("Vendor recommendation audit is missing reviewed_scope")
    low_items = [item for item in items if item["demand"] == "Low"]
    low_names = {item_slug(str(item["name"])) for item in low_items}
    promoted_reference_count = sum(
        item.get("_vendorReferencePromotion") is True for item in items
    )
    expected_counts = {
        "search_index_version": 5,
        "search_entry_count": len(items),
        "resolved_sell_price_entry_count": resolved_sell_price_count,
        "unpriced_reference_entry_count": unpriced_reference_count,
        "npc_vendor_resale_excluded_entry_count": vendor_resale_excluded_count,
        "zero_vendor_sell_price_entry_count": zero_sell_price_count,
        "margin_evaluated_entry_count": margin_evaluated_count,
        "low_entry_count_after_promotions": len(low_items),
        "low_unique_name_count_after_promotions": len(low_names),
        "promoted_reference_entry_count": promoted_reference_count,
        "manual_vendor_recommendation_count": manual_count,
        "automatic_margin_vendor_recommendation_count": automatic_count,
        "below_vendor_after_cut_entry_count": below_vendor_after_cut_count,
        "close_margin_vendor_recommendation_count": close_margin_count,
        "above_margin_entry_count": margin_evaluated_count - automatic_count,
        "vendor_recommendation_count": recommendation_count,
    }
    if scope != expected_counts:
        raise RuntimeError(
            "Vendor recommendation reviewed_scope is stale: "
            f"saved={scope!r}, found={expected_counts!r}"
        )
    for item in items:
        item.pop("_vendorReferencePromotion", None)
    return recommendation_count


def build_index() -> str:
    manifest = json.loads(GUIDE_MANIFEST_PATH.read_text(encoding="utf-8"))
    vendor_audit = load_vendor_recommendations()
    vendor_keys = recommendation_keys(vendor_audit)
    guides = manifest.get("guides", [])
    if len(guides) != int(manifest.get("active_guide_count", 0)):
        raise RuntimeError("AH guide manifest active count does not match its guide list")

    items: list[dict[str, str | int]] = []
    for guide in guides:
        filename = str(guide["file"])
        guide_id = str(guide["id"])
        guide_title = str(guide["title"])
        path = ROOT / "guides" / filename
        if not path.is_file():
            raise FileNotFoundError(f"Manifest links to missing AH guide: {path.relative_to(ROOT)}")
        vendor_names = {
            name
            for recommended_guide_id, name in vendor_keys
            if recommended_guide_id == guide_id
        }
        parser = AHGuideParser(filename, guide_id, guide_title, vendor_names)
        parser.feed(path.read_text(encoding="utf-8"))
        if not parser.items:
            raise RuntimeError(f"No searchable item rows found in {path.relative_to(ROOT)}")
        items.extend(parser.items)

    canonicalize_and_validate(items)
    vendor_recommendation_count = apply_vendor_recommendations(items, vendor_audit)
    items.sort(key=lambda item: (str(item["name"]).casefold(), str(item["guideId"])))
    payload = {
        "version": 5,
        "guideCount": len(guides),
        "itemCount": len(items),
        "vendorRecommendationCount": vendor_recommendation_count,
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
