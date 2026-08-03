#!/usr/bin/env python3
"""Sort non-progressive AH table rows by target buyout, highest first."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from ah_section_ordering import load_policy, order_guide_source, validate_inventory


ROOT = Path(__file__).resolve().parents[1]
GUIDES_DIR = ROOT / "guides"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Fail when a price-sortable table is stale")
    args = parser.parse_args()

    policy = load_policy()
    guide_paths = sorted(GUIDES_DIR.glob(policy["scope"]["guide_glob"]))
    reports_by_guide: dict[str, list[dict]] = {}
    updates: list[tuple[Path, str, list[dict]]] = []

    for path in guide_paths:
        source = path.read_text(encoding="utf-8")
        updated, reports = order_guide_source(source, path.name, policy)
        reports_by_guide[path.name] = reports
        if updated != source:
            updates.append((path, updated, [report for report in reports if report["changed"]]))

    validate_inventory(policy, reports_by_guide)
    if args.check and updates:
        for path, _, reports in updates:
            sections = ", ".join(report["title"] for report in reports)
            print(f"Stale AH price order: {path.relative_to(ROOT)} ({sections})", file=sys.stderr)
        return 1

    for path, updated, _ in updates:
        path.write_text(updated, encoding="utf-8", newline="\n")

    total_tables = sum(len(reports) for reports in reports_by_guide.values())
    fixed_tables = sum(
        report["fixed_selector"] is not None
        for reports in reports_by_guide.values()
        for report in reports
    )
    changed_sections = sum(len(reports) for _, _, reports in updates)
    moved_rows = sum(
        report["moved_rows"]
        for _, _, reports in updates
        for report in reports
    )
    action = "Validated" if args.check else "Applied"
    print(
        f"{action} AH section ordering across {len(guide_paths)} guides and {total_tables} priced tables: "
        f"{fixed_tables} fixed-order tables, {total_tables - fixed_tables} price-ordered tables, "
        f"{changed_sections} reordered sections, {moved_rows} moved rows."
    )
    if updates and not args.check:
        print("Updated guide order in:")
        for path, _, reports in updates:
            print(f"- {path.relative_to(ROOT)}: {len(reports)} sections")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
