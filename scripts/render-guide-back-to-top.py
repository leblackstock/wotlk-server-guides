#!/usr/bin/env python3
"""Keep category back-to-top controls current on long guides with jump navigation."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
GUIDES_DIR = ROOT / "guides"
STYLE_VERSION = "20260728-main-ux-v1"
EXPECTED_LONG_GUIDES = 35


def transform(source: str, filename: str) -> str:
    source, wrap_count = re.subn(
        r'<div class="wrap"(?: id="top")?>',
        '<div class="wrap" id="top">',
        source,
        count=1,
    )
    if wrap_count != 1:
        raise ValueError(f"{filename}: expected exactly one page wrapper")

    def decorate(match: re.Match[str]) -> str:
        attributes, content = match.groups()
        content = re.sub(
            r'<a class="guide-back-to-top"[^>]*>.*?</a>\s*$',
            "",
            content,
            flags=re.DOTALL,
        )
        if 'class="' in attributes:
            attributes = re.sub(
                r'class="([^"]*)"',
                lambda class_match: (
                    f'class="{class_match.group(1)} guide-category-heading"'
                    if "guide-category-heading" not in class_match.group(1).split()
                    else class_match.group(0)
                ),
                attributes,
                count=1,
            )
        else:
            attributes += ' class="guide-category-heading"'
        return (
            f"<h2{attributes}>{content}"
            '<a class="guide-back-to-top" href="#top" aria-label="Back to top">↑ Top</a>'
            "</h2>"
        )

    source, heading_count = re.subn(
        r"<h2([^>]*)>(.*?)</h2>", decorate, source, flags=re.DOTALL
    )
    if heading_count == 0:
        raise ValueError(f"{filename}: expected at least one category heading")

    return re.sub(
        r"style\.css(?:\?v=[^\"\s]+)?",
        f"style.css?v={STYLE_VERSION}",
        source,
        count=1,
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Fail if guide controls are stale")
    args = parser.parse_args()

    paths = sorted(
        path
        for path in GUIDES_DIR.glob("*.html")
        if 'class="jump-nav"' in path.read_text(encoding="utf-8")
    )
    if len(paths) != EXPECTED_LONG_GUIDES:
        raise ValueError(
            f"Expected {EXPECTED_LONG_GUIDES} long guides with jump navigation, found {len(paths)}"
        )

    changed: list[str] = []
    for path in paths:
        source = path.read_text(encoding="utf-8")
        expected = transform(source, path.name)
        if expected == source:
            continue
        if args.check:
            print(f"Stale category controls: {path.relative_to(ROOT)}", file=sys.stderr)
            return 1
        path.write_text(expected, encoding="utf-8", newline="\n")
        changed.append(str(path.relative_to(ROOT)))

    if changed:
        print("Updated guide category controls in:")
        for path in changed:
            print(f"- {path}")
    else:
        print("Guide category controls are current.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
