#!/usr/bin/env python3
"""Validate target-buyout-first ordering in every eligible AH guide section."""

from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from ah_guides import active_guide_paths  # noqa: E402
from ah_section_ordering import load_policy, order_guide_source, validate_inventory  # noqa: E402


def fail(message: str) -> None:
    raise AssertionError(message)


policy = load_policy()
reports_by_guide: dict[str, list[dict]] = {}
for path in active_guide_paths(guides_dir=ROOT / "guides"):
    source = path.read_text(encoding="utf-8")
    expected, reports = order_guide_source(source, path.name, policy)
    if expected != source:
        stale = ", ".join(report["title"] for report in reports if report["changed"])
        fail(f"{path.name}: stale target-buyout order in {stale}")
    reports_by_guide[path.name] = reports

validate_inventory(policy, reports_by_guide)

for reports in reports_by_guide.values():
    for report in reports:
        if report["fixed_selector"] is not None:
            continue
        prices = report["prices"]
        if any(prices[index] < prices[index + 1] for index in range(len(prices) - 1)):
            fail(f"{report['filename']}: {report['title']} is not highest-target-buyout first")


def report_for(filename: str, section_id: str) -> dict:
    matches = [
        report
        for report in reports_by_guide[filename]
        if report["section_id"] == section_id
    ]
    if len(matches) != 1:
        fail(f"{filename}: expected one section {section_id}, found {len(matches)}")
    return matches[0]


alchemy_flasks = report_for(
    "alchemy-materials-ah-price-guide.html", "crafted-wrath-flasks"
)
if alchemy_flasks["fixed_selector"] is not None:
    fail("Crafted Wrath flasks must use price-first ordering")

mount_parts = report_for(
    "engineering-materials-ah-price-guide.html", "engineer-only-mount-components"
)
if mount_parts["names"] != [
    "Elementium-plated Exhaust Pipe",
    "Goblin-machined Piston",
    "Salvaged Iron Golem Parts",
]:
    fail("Engineer-only mount components are not highest-target-buyout first")

skeleton_keys = report_for(
    "blacksmithing-materials-ah-price-guide.html", "blacksmith-only-skeleton-keys"
)
if skeleton_keys["fixed_selector"] is None:
    fail("Skeleton keys must remain a profession-rank progression")
if skeleton_keys["names"] != [
    "Silver Skeleton Key",
    "Golden Skeleton Key",
    "Truesilver Skeleton Key",
    "Arcanite Skeleton Key",
    "Cobalt Skeleton Key",
    "Titanium Skeleton Key",
]:
    fail("Skeleton-key profession progression changed")

total_tables = sum(len(reports) for reports in reports_by_guide.values())
fixed_tables = sum(
    report["fixed_selector"] is not None
    for reports in reports_by_guide.values()
    for report in reports
)
print(
    f"AH price-order policy is current across {len(reports_by_guide)} guides and "
    f"{total_tables} priced tables: {total_tables - fixed_tables} price-ordered and "
    f"{fixed_tables} fixed-order tables."
)
