#!/usr/bin/env python3
"""Guard the completed Herbalism, Skinning, and Fishing material audits."""

from __future__ import annotations

import importlib.util
import json
import re
import unicodedata
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
GUIDES = ROOT / "guides"
PLANS = ROOT / "docs" / "ah-profession-plans"
ITEM_TEMPLATE_COMMIT = "e0fe11ba46b885a01e4a4038001e0055822cc7ba"
SPECS = {
    "herbalism": {
        "guide": "herbalism-herbs-ah-price-guide.html",
        "searchable": 52,
        "baseline": 47,
        "vendor": 5,
        "reference": 0,
    },
    "skinning": {
        "guide": "skinning-leatherworking-materials-ah-price-guide.html",
        "searchable": 37,
        "baseline": 31,
        "vendor": 6,
        "reference": 5,
    },
    "fishing": {
        "guide": "fishing-cooking-materials-ah-price-guide.html",
        "searchable": 146,
        "baseline": 127,
        "vendor": 19,
        "reference": 4,
    },
}
CRAFTED_BLOCK = re.compile(
    r"<!-- AH_CRAFTED_SECTION_START -->.*?<!-- AH_CRAFTED_SECTION_END -->",
    re.DOTALL,
)


def fail(message: str) -> None:
    raise AssertionError(message)


def normalize(value: str) -> str:
    value = "".join(
        character
        for character in unicodedata.normalize("NFKD", value)
        if unicodedata.category(character) != "Mn"
    )
    value = value.casefold().replace("'", "").replace(chr(0x2019), "")
    value = value.replace("&", " and ")
    return " ".join(re.sub(r"[^a-z0-9]+", " ", value).split())


def generated_json(path: Path, variable: str) -> dict:
    source = path.read_text(encoding="utf-8")
    match = re.search(rf"window\.{variable}=(\{{.*?\}});\n", source, re.DOTALL)
    if not match:
        fail(f"Could not parse {variable} from {path.name}")
    return json.loads(match.group(1))


def load_search_builder():
    path = ROOT / "scripts" / "build-ah-search-index.py"
    spec = importlib.util.spec_from_file_location("ah_search_builder", path)
    if spec is None or spec.loader is None:
        fail("Could not load AH search builder")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def reference_row_count(source: str) -> int:
    count = 0
    for table in re.findall(
        r'<table[^>]*data-table-family="reference"[^>]*>(.*?)</table>',
        source,
        re.DOTALL,
    ):
        body = re.search(r"<tbody>(.*?)</tbody>", table, re.DOTALL)
        if body:
            count += len(re.findall(r"<tr[^>]*>", body.group(1)))
    return count


def main() -> int:
    builder = load_search_builder()
    item_ids = generated_json(ROOT / "assets" / "ah-item-ids.js", "AH_ITEM_IDS")
    baselines = json.loads(
        (ROOT / "data" / "ah-price-baselines.json").read_text(encoding="utf-8")
    )["items"]
    vendor = json.loads(
        (ROOT / "data" / "ah-vendor-sections.json").read_text(encoding="utf-8")
    )

    total_searchable = 0
    total_baseline = 0
    total_vendor = 0
    for profession, spec in SPECS.items():
        filename = spec["guide"]
        source = (GUIDES / filename).read_text(encoding="utf-8")
        static_source = CRAFTED_BLOCK.sub("", source)
        if 'data-market-source="crafted"' in static_source:
            fail(f"{filename}: crafted output escaped its profession-owned block")

        parser = builder.AHGuideParser(filename, profession.title())
        parser.feed(static_source)
        rows = parser.items
        if len(rows) != spec["searchable"]:
            fail(f"{filename}: expected {spec['searchable']} searchable static rows, found {len(rows)}")
        if reference_row_count(static_source) != spec["reference"]:
            fail(f"{filename}: reference-row coverage drifted")

        vendor_keys = vendor["guides"][filename]["items"]
        vendor_ids = {int(vendor["catalog"][key]["item_id"]) for key in vendor_keys}
        baseline_count = 0
        vendor_count = 0
        for row in rows:
            item_id = item_ids.get(normalize(str(row["name"])))
            if item_id is None:
                fail(f"{filename}: missing exact item ID for {row['name']}")
            if item_id in vendor_ids:
                vendor_count += 1
                continue
            record = baselines.get(str(item_id))
            if not record:
                fail(f"{filename}: {row['name']} lacks a frozen baseline")
            if record["source_type"] != "frozen-pre-scan-guide" or record["confidence"] != "low":
                fail(f"{filename}: unexpected evidence layer for {row['name']}")
            if not int(record["quick"]) <= int(record["target"]) <= int(record["high"]):
                fail(f"{filename}: invalid price-band order for {row['name']}")
            baseline_count += 1

        if baseline_count != spec["baseline"] or vendor_count != spec["vendor"]:
            fail(
                f"{filename}: expected {spec['baseline']} baselines and {spec['vendor']} "
                f"vendor rows, found {baseline_count} and {vendor_count}"
            )
        if "Updated 2026-08-04" not in source:
            fail(f"{filename}: footer date is stale")

        plan = (PLANS / f"{profession}.md").read_text(encoding="utf-8")
        for marker in (
            "Status: `complete` — 2026-08-04",
            ITEM_TEMPLATE_COMMIT,
            "approximately 50%",
            "No price bands changed",
        ):
            if marker not in plan:
                fail(f"{profession}.md: missing completion evidence: {marker}")

        total_searchable += len(rows)
        total_baseline += baseline_count
        total_vendor += vendor_count

    tooltip_builder = (ROOT / "scripts" / "apply-ah-item-tooltips.py").read_text(
        encoding="utf-8"
    )
    if ITEM_TEMPLATE_COMMIT not in tooltip_builder or '"master/data/' in tooltip_builder:
        fail("AH tooltip item-template source is not pinned to the audited commit")

    if (total_searchable, total_baseline, total_vendor) != (235, 205, 30):
        fail("Gathering audit totals drifted")
    print(
        "Gathering profession audits are complete: 235 searchable rows, "
        "205 frozen baselines, 30 canonical vendor rows, and 9 reference checks."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
