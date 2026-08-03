#!/usr/bin/env python3
"""Render profession-restricted static AH rows into canonical sections."""

from __future__ import annotations

import argparse
import html
import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
GUIDES_DIR = ROOT / "guides"
AUDIT_PATH = ROOT / "data" / "ah-profession-use-audit.json"

REQUIREMENT_NOTE = re.compile(
    r'<strong class="profession-use-requirement">.*?</strong>\s*',
    re.DOTALL,
)


def row_pattern(item_name: str) -> re.Pattern[str]:
    return re.compile(
        r'<tr(?:\s[^>]*)?>(?:(?!</tr>).)*?'
        r'<strong class="q-[^"]+">'
        + re.escape(html.escape(item_name, quote=False))
        + r"</strong>(?:(?!</tr>).)*?</tr>",
        re.DOTALL,
    )


def section_pattern(section_id: str) -> re.Pattern[str]:
    escaped = re.escape(section_id)
    return re.compile(
        rf"<!-- AH_PROFESSION_USE_SECTION_START {escaped} -->.*?"
        rf"<!-- AH_PROFESSION_USE_SECTION_END {escaped} -->\s*",
        re.DOTALL,
    )


def add_requirement_note(row: str, requirement: dict) -> str:
    row = REQUIREMENT_NOTE.sub("", row)
    skill = html.escape(requirement["skill"])
    rank = int(requirement["rank"])
    action = "place" if requirement["name"].endswith("Feast") else "use"
    note = (
        f'<strong class="profession-use-requirement">'
        f'Requires {skill} {rank} to {action}.</strong> '
    )
    return re.sub(
        r'(<td data-column="notes" data-label="Use / Selling Notes">)',
        rf"\1{note}",
        row,
        count=1,
    )


def render_section(section_id: str, section: dict, rows: list[str]) -> str:
    title = html.escape(section["title"])
    description = html.escape(section["description"])
    return (
        f"<!-- AH_PROFESSION_USE_SECTION_START {section_id} -->\n"
        f'<section class="common profession-use-section" id="{section_id}" '
        f'data-use-audience="profession-restricted">'
        f'<h2 class="ah-category-heading">{title}'
        f'<a class="ah-back-to-top" href="#top" aria-label="Back to top">↑ Top</a>'
        f"</h2>\n"
        f'<p class="small">{description}</p>\n'
        f'<div class="table-wrap"><table class="ah-market-table '
        f'ah-market-table--standard" data-table-family="market"><thead><tr>'
        f'<th data-column="item">Item</th>'
        f'<th data-column="target">Target Price</th>'
        f'<th data-column="quick">Quick Price</th>'
        f'<th data-column="high">High / Scarce</th>'
        f'<th data-column="stack">Stack Size</th>'
        f'<th data-column="demand">Demand</th>'
        f'<th data-column="notes">Use / Selling Notes</th>'
        f"</tr></thead><tbody>{''.join(rows)}</tbody></table></div></section>\n"
        f"<!-- AH_PROFESSION_USE_SECTION_END {section_id} -->"
    )


def insert_before_heading(source: str, heading: str, block: str, filename: str) -> str:
    pattern = re.compile(
        r'(<section class="common(?:\s[^"]*)?">'
        r'<h2 class="ah-category-heading">'
        + re.escape(html.escape(heading))
        + r")"
    )
    source, count = pattern.subn(block + r"\n\1", source, count=1)
    if count != 1:
        raise ValueError(f"{filename}: missing insertion heading {heading!r}")
    return source


def transform_guide(source: str, filename: str, audit: dict) -> str:
    requirements = {
        entry["name"]: entry
        for entry in audit["static_hard_requirements"]
        if entry["guide"] == filename
    }
    configured_sections = [
        (section_id, section)
        for section_id, section in audit["static_sections"].items()
        if section["guide"] == filename
    ]
    if not configured_sections:
        return source

    captured: dict[str, str] = {}
    for _, section in configured_sections:
        for item_name in section["items"]:
            matches = row_pattern(item_name).findall(source)
            if len(matches) != 1:
                raise ValueError(
                    f"{filename}: expected exactly one row for {item_name}, found {len(matches)}"
                )
            captured[item_name] = matches[0]

    for item_name, row in captured.items():
        source = source.replace(row, "", 1)
    for section_id, _ in configured_sections:
        source = section_pattern(section_id).sub("", source, count=1)

    replacements = audit.get("static_heading_replacements", {}).get(filename, {})
    for old_heading, new_heading in replacements.items():
        old = (
            f'<h2 class="ah-category-heading">'
            f'{html.escape(old_heading, quote=False)}<a'
        )
        new = (
            f'<h2 class="ah-category-heading">'
            f'{html.escape(new_heading, quote=False)}<a'
        )
        if old in source:
            source = source.replace(old, new, 1)
        elif new not in source:
            raise ValueError(f"{filename}: missing heading {old_heading!r}")

    for section_id, section in configured_sections:
        rows = [
            add_requirement_note(captured[item_name], requirements[item_name])
            for item_name in section["items"]
        ]
        block = render_section(section_id, section, rows)
        insertion_heading = replacements.get(
            section["insert_before_heading"], section["insert_before_heading"]
        )
        source = insert_before_heading(source, insertion_heading, block, filename)

    return source


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Fail if static use sections are stale")
    args = parser.parse_args()

    audit = json.loads(AUDIT_PATH.read_text(encoding="utf-8"))
    guide_names = sorted(
        {section["guide"] for section in audit.get("static_sections", {}).values()}
    )
    changed: list[str] = []
    for filename in guide_names:
        path = GUIDES_DIR / filename
        source = path.read_text(encoding="utf-8")
        expected = transform_guide(source, filename, audit)
        if expected == source:
            continue
        if args.check:
            print(f"Stale profession-use sections: {path.relative_to(ROOT)}", file=sys.stderr)
            return 1
        path.write_text(expected, encoding="utf-8", newline="\n")
        changed.append(str(path.relative_to(ROOT)))

    if changed:
        print("Updated profession-use sections in:")
        for path in changed:
            print(f"- {path}")
    else:
        print("Profession-use sections are current.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
