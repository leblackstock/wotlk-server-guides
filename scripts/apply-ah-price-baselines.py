#!/usr/bin/env python3
"""Apply frozen AH baselines to static rows without touching crafted blocks."""

from __future__ import annotations

import argparse
import html
import importlib.util
import json
import re
import sys
import unicodedata
from pathlib import Path

from ah_section_ordering import load_policy, order_guide_source


ROOT = Path(__file__).resolve().parents[1]
GUIDES_DIR = ROOT / "guides"
BASELINE_PATH = ROOT / "data" / "ah-price-baselines.json"
CATALOG_PATH = ROOT / "data" / "ah-crafted-sections.json"
ITEM_IDS_PATH = ROOT / "assets" / "ah-item-ids.js"
RENDERER_PATH = ROOT / "scripts" / "render-ah-shared-sections.py"
PRICE_BANDS = ("quick", "target", "high")
CRAFTED_BLOCK = re.compile(
    r"(<!-- AH_CRAFTED_SECTION_START -->.*?<!-- AH_CRAFTED_SECTION_END -->)",
    re.DOTALL,
)
SECTION_ORDERING_POLICY = load_policy()
ROW_PATTERN = re.compile(r"<tr[^>]*>.*?</tr>", re.DOTALL)
ITEM_PATTERN = re.compile(
    r'<td[^>]*data-column="item"[^>]*>.*?<strong[^>]*>(.*?)</strong>',
    re.DOTALL,
)


def normalize(value: str) -> str:
    value = "".join(
        character
        for character in unicodedata.normalize("NFKD", value)
        if unicodedata.category(character) != "Mn"
    )
    value = value.casefold().replace("'", "").replace("’", "")
    value = value.replace("&", " and ")
    return " ".join(re.sub(r"[^a-z0-9]+", " ", value).split())


def load_renderer():
    spec = importlib.util.spec_from_file_location("ah_renderer", RENDERER_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("Could not load AH renderer")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_item_ids() -> dict[str, int]:
    source = ITEM_IDS_PATH.read_text(encoding="utf-8")
    match = re.search(r"window\.AH_ITEM_IDS=(\{.*?\});\n", source, re.DOTALL)
    if not match:
        raise RuntimeError("Could not parse AH item IDs")
    return {key: int(value) for key, value in json.loads(match.group(1)).items()}


def money_from_text(value: str) -> int:
    total = 0
    clean = " ".join(html.unescape(re.sub(r"<[^>]+>", "", value)).split())
    for amount, unit in re.findall(r"([\d,]+)\s*([gsc])", clean):
        total += int(amount.replace(",", "")) * {"g": 10_000, "s": 100, "c": 1}[unit]
    return total


def current_buyouts(row: str, renderer) -> dict[str, int]:
    values = {}
    for band in PRICE_BANDS:
        match = re.search(
            rf'<div class="pricepair {band}">.*?'
            rf'<span class="buyout">(.*?)</span>',
            row,
            re.DOTALL,
        )
        if match:
            values[band] = money_from_text(match.group(1))
    return values


def replace_row_prices(row: str, prices: dict[str, int], renderer) -> str:
    for band in PRICE_BANDS:
        replacement = renderer.render_price_pair(
            band,
            int(prices[band]),
            prices.get(f"{band}_bid_copper"),
        )
        row, count = re.subn(
            rf'<div class="pricepair {band}">.*?</div>\s*</div>',
            replacement,
            row,
            count=1,
            flags=re.DOTALL,
        )
        if count != 1:
            raise RuntimeError(f"Could not replace {band} price in static AH row")
    return row


def expected_prices() -> tuple[dict[int, dict[str, int]], dict[str, int]]:
    baseline = json.loads(BASELINE_PATH.read_text(encoding="utf-8"))
    prices = {
        int(item_id): {band: int(record[band]) for band in PRICE_BANDS}
        for item_id, record in baseline["items"].items()
    }
    catalog = json.loads(CATALOG_PATH.read_text(encoding="utf-8"))
    crafted_ids: dict[int, dict[str, int]] = {}
    for key, raw in catalog["catalog"].items():
        item = catalog.get("catalog_defaults", {}) | catalog["price_profiles"][raw["profile"]] | raw
        item_id = int(item["item_id"])
        if item_id not in prices:
            continue
        values = {band: int(item[f"{band}_copper"]) for band in PRICE_BANDS}
        for band in PRICE_BANDS:
            bid_key = f"{band}_bid_copper"
            if bid_key in item:
                values[bid_key] = int(item[bid_key])
        crafted_ids[item_id] = values
    prices.update(crafted_ids)
    return prices, {"baseline": len(baseline["items"]), "crafted": len(crafted_ids)}


def transform(source: str, prices: dict[int, dict[str, int]], item_ids: dict[str, int], renderer) -> tuple[str, int]:
    parts = CRAFTED_BLOCK.split(source)
    changed = 0

    def replace_row(match: re.Match[str]) -> str:
        nonlocal changed
        row = match.group(0)
        item_match = ITEM_PATTERN.search(row)
        if not item_match:
            return row
        name = " ".join(
            html.unescape(re.sub(r"<[^>]+>", "", item_match.group(1))).split()
        )
        item_id = item_ids.get(normalize(name))
        expected = prices.get(item_id or 0)
        if not expected:
            return row
        current = current_buyouts(row, renderer)
        if set(current) != set(PRICE_BANDS):
            return row
        target = {
            band: renderer.display_money_copper(int(expected[band]))
            for band in PRICE_BANDS
        }
        if current == target:
            return row
        changed += 1
        return replace_row_prices(row, expected, renderer)

    for index in range(0, len(parts), 2):
        parts[index] = ROW_PATTERN.sub(replace_row, parts[index])
    return "".join(parts), changed


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    renderer = load_renderer()
    prices, counts = expected_prices()
    item_ids = load_item_ids()
    stale: list[str] = []
    total_changed = 0
    total_reordered = 0
    for path in sorted(GUIDES_DIR.glob("*ah-price-guide.html")):
        source = path.read_text(encoding="utf-8")
        updated, changed = transform(source, prices, item_ids, renderer)
        updated, ordering_reports = order_guide_source(
            updated, path.name, SECTION_ORDERING_POLICY
        )
        reordered = [report for report in ordering_reports if report["changed"]]
        if updated == source:
            continue
        total_changed += changed
        total_reordered += len(reordered)
        if args.check:
            stale.append(
                f"{path.name}: {changed} stale static price rows, "
                f"{len(reordered)} stale price-order sections"
            )
        else:
            path.write_text(updated, encoding="utf-8", newline="\n")
            print(
                f"{path.name}: updated {changed} static price rows and "
                f"{len(reordered)} price-order sections"
            )
    if stale:
        print("\n".join(stale), file=sys.stderr)
        return 1
    action = "Validated" if args.check else "Updated"
    print(
        f"{action} frozen AH baselines: {counts['baseline']} baseline items, "
        f"{counts['crafted']} shared crafted outputs, {total_changed} stale rows, "
        f"{total_reordered} stale price-order sections."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
