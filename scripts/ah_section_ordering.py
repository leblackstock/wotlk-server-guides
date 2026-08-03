#!/usr/bin/env python3
"""Shared target-buyout ordering logic for Auction House guide tables."""

from __future__ import annotations

import html
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
POLICY_PATH = ROOT / "data" / "ah-section-ordering.json"

TABLE_PATTERN = re.compile(
    r"(?P<open><table\b[^>]*>.*?<tbody\b[^>]*>)"
    r"(?P<body>.*?)"
    r"(?P<close></tbody>.*?</table>)",
    re.DOTALL | re.IGNORECASE,
)
ROW_PATTERN = re.compile(r"<tr\b[^>]*>.*?</tr>", re.DOTALL | re.IGNORECASE)
SECTION_OPEN_PATTERN = re.compile(r"<section\b(?P<attrs>[^>]*)>", re.IGNORECASE)
SECTION_ID_PATTERN = re.compile(r'\bid="([^"]+)"', re.IGNORECASE)
HEADING_PATTERN = re.compile(r"<h[23]\b[^>]*>(.*?)</h[23]>", re.DOTALL | re.IGNORECASE)
BACK_TO_TOP_PATTERN = re.compile(
    r'<a\b[^>]*class="[^"]*\bah-back-to-top\b[^"]*"[^>]*>.*?</a>',
    re.DOTALL | re.IGNORECASE,
)
ITEM_PATTERN = re.compile(
    r'<td\b[^>]*data-column="item"[^>]*>.*?<strong\b[^>]*>(.*?)</strong>',
    re.DOTALL | re.IGNORECASE,
)
TARGET_CELL_PATTERN = re.compile(
    r'<td\b[^>]*data-column="target"[^>]*>(.*?)</td>',
    re.DOTALL | re.IGNORECASE,
)
BUYOUT_PATTERN = re.compile(
    r'<span\b[^>]*class="[^"]*\bbuyout\b[^"]*"[^>]*>(.*?)</span>',
    re.DOTALL | re.IGNORECASE,
)
TAG_PATTERN = re.compile(r"<[^>]+>", re.DOTALL)


def load_policy(path: Path = POLICY_PATH) -> dict:
    policy = json.loads(path.read_text(encoding="utf-8"))
    if int(policy.get("version", 0)) != 1:
        raise ValueError("Unsupported AH section-ordering policy version")
    default = policy.get("default_order", {})
    if (
        default.get("field") != "target_buyout_copper"
        or default.get("direction") != "descending"
        or default.get("unit") != "per item"
        or default.get("tie_behavior") != "stable"
        or default.get("non_numeric_behavior") != "bottom-stable"
    ):
        raise ValueError("AH section-ordering policy has an unsupported default order")
    fixed_selectors(policy)
    return policy


def fixed_selectors(policy: dict) -> dict[tuple[str, str, str], dict]:
    selectors: dict[tuple[str, str, str], dict] = {}
    for group in policy.get("fixed_order_groups", []):
        guide = group["guide"]
        for selector_type, field in (("id", "section_ids"), ("title", "section_titles")):
            for value in group.get(field, []):
                selector = (guide, selector_type, value)
                if selector in selectors:
                    raise ValueError(
                        f"Duplicate fixed-order selector: {guide} {selector_type}={value!r}"
                    )
                selectors[selector] = {
                    "order": group["order"],
                    "reason": group["reason"],
                }
    return selectors


def clean_text(fragment: str) -> str:
    return " ".join(html.unescape(TAG_PATTERN.sub("", fragment)).split())


def money_from_text(fragment: str) -> int:
    text = clean_text(fragment)
    values = re.findall(r"([\d,]+)\s*([gsc])", text, re.IGNORECASE)
    if text.casefold() == "not ah":
        return 0
    if not values:
        raise ValueError(f"Could not parse AH money value: {text!r}")
    multipliers = {"g": 10_000, "s": 100, "c": 1}
    return sum(
        int(amount.replace(",", "")) * multipliers[unit.casefold()]
        for amount, unit in values
    )


def section_context(source: str, table_start: int, filename: str) -> tuple[str | None, str]:
    matches = list(SECTION_OPEN_PATTERN.finditer(source, 0, table_start))
    if not matches:
        raise ValueError(f"{filename}: priced AH table is outside a section")
    section_match = matches[-1]
    if source.rfind("</section>", 0, table_start) > section_match.start():
        raise ValueError(f"{filename}: could not resolve the priced table's section")
    attributes = section_match.group("attrs")
    id_match = SECTION_ID_PATTERN.search(attributes)
    section_id = html.unescape(id_match.group(1)) if id_match else None
    heading_match = HEADING_PATTERN.search(source, section_match.end(), table_start)
    if not heading_match:
        raise ValueError(f"{filename}: priced AH section is missing a heading")
    heading_fragment = BACK_TO_TOP_PATTERN.sub("", heading_match.group(1))
    title = clean_text(heading_fragment)
    if not title:
        raise ValueError(f"{filename}: priced AH section has an empty heading")
    return section_id, title


def row_details(
    row: str,
    filename: str,
    section_label: str,
    allow_formula_price: bool = False,
) -> tuple[str, int | None]:
    item_match = ITEM_PATTERN.search(row)
    target_match = TARGET_CELL_PATTERN.search(row)
    if not item_match:
        raise ValueError(f"{filename}: incomplete priced row in {section_label!r}")
    name = clean_text(item_match.group(1))
    if not name:
        raise ValueError(f"{filename}: item name missing in {section_label!r}")
    if not target_match:
        if allow_formula_price:
            return name, None
        raise ValueError(f"{filename}: target price missing in {section_label!r}")
    buyout_match = BUYOUT_PATTERN.search(target_match.group(1))
    if not buyout_match:
        if allow_formula_price:
            return name, None
        raise ValueError(f"{filename}: target buyout missing in {section_label!r}")
    return name, money_from_text(buyout_match.group(1))


def reordered_body(body: str, rows: list[re.Match[str]], order: list[int]) -> str:
    if len(rows) < 2:
        return body
    prefix = body[: rows[0].start()]
    suffix = body[rows[-1].end() :]
    gaps = [body[rows[index].end() : rows[index + 1].start()] for index in range(len(rows) - 1)]
    if any(gap.strip() for gap in gaps):
        raise ValueError("Unexpected non-whitespace content between AH table rows")
    separator = "\n" if any("\n" in gap for gap in gaps) else ""
    if separator:
        indentation = re.search(r"\n([ \t]*)$", gaps[0]) if gaps else None
        if indentation:
            separator += indentation.group(1)
    row_sources = [match.group(0) for match in rows]
    return prefix + separator.join(row_sources[index] for index in order) + suffix


def order_guide_source(source: str, filename: str, policy: dict) -> tuple[str, list[dict]]:
    selectors = fixed_selectors(policy)
    output: list[str] = []
    cursor = 0
    reports: list[dict] = []

    for table_match in TABLE_PATTERN.finditer(source):
        if not re.search(
            r'class="[^"]*\bah-market-table\b[^"]*"',
            table_match.group("open"),
            re.IGNORECASE,
        ):
            continue
        if not re.search(
            r'data-column="target"', table_match.group("open"), re.IGNORECASE
        ):
            continue
        section_id, title = section_context(source, table_match.start(), filename)
        section_label = section_id or title
        body = table_match.group("body")
        rows = list(ROW_PATTERN.finditer(body))
        if not rows:
            raise ValueError(f"{filename}: priced AH table in {section_label!r} has no rows")
        leftover = ROW_PATTERN.sub("", body)
        if leftover.strip():
            raise ValueError(f"{filename}: unexpected content in {section_label!r} table body")

        fixed_selector = None
        if section_id and (filename, "id", section_id) in selectors:
            fixed_selector = (filename, "id", section_id)
        elif (filename, "title", title) in selectors:
            fixed_selector = (filename, "title", title)

        details = [
            row_details(
                match.group(0),
                filename,
                section_label,
                allow_formula_price=fixed_selector is not None,
            )
            for match in rows
        ]
        names = [name for name, _ in details]
        prices = [price for _, price in details]

        descending = None
        if all(price is not None for price in prices):
            numeric_prices = [int(price) for price in prices]
            descending = all(
                numeric_prices[index] >= numeric_prices[index + 1]
                for index in range(len(numeric_prices) - 1)
            )
        order = list(range(len(rows)))
        if fixed_selector is None:
            order.sort(key=lambda index: -int(prices[index]))
        updated_body = reordered_body(body, rows, order)
        changed = updated_body != body
        reports.append(
            {
                "filename": filename,
                "section_id": section_id,
                "title": title,
                "row_count": len(rows),
                "names": names,
                "prices": prices,
                "fixed_selector": fixed_selector,
                "descending_before": descending,
                "changed": changed,
                "moved_rows": sum(index != ordered_index for index, ordered_index in enumerate(order)),
            }
        )
        output.append(source[cursor : table_match.start("body")])
        output.append(updated_body)
        cursor = table_match.end("body")

    output.append(source[cursor:])
    return "".join(output), reports


def validate_inventory(policy: dict, guide_reports: dict[str, list[dict]]) -> None:
    scope = policy["scope"]
    expected_guides = int(scope["expected_guide_count"])
    expected_tables = int(scope["expected_priced_table_count"])
    actual_guides = len(guide_reports)
    actual_tables = sum(len(reports) for reports in guide_reports.values())
    if actual_guides != expected_guides:
        raise ValueError(f"Expected {expected_guides} AH guides, found {actual_guides}")
    if actual_tables != expected_tables:
        raise ValueError(f"Expected {expected_tables} priced AH tables, found {actual_tables}")

    expected_fixed = set(fixed_selectors(policy))
    matched_fixed = {
        report["fixed_selector"]
        for reports in guide_reports.values()
        for report in reports
        if report["fixed_selector"] is not None
    }
    missing = sorted(expected_fixed - matched_fixed)
    if missing:
        labels = ", ".join(f"{guide} {kind}={value!r}" for guide, kind, value in missing)
        raise ValueError(f"Fixed-order policy selectors did not match a table: {labels}")
