#!/usr/bin/env python3
"""Validate the complete fresh-80 Priest and Hunter guide families."""

from __future__ import annotations

import re
from pathlib import Path
from urllib.parse import urlsplit


ROOT = Path(__file__).resolve().parents[1]
GUIDES = ROOT / "guides"
FAMILIES = {
    "holy-priest": ("priest", "priest-holy"),
    "shadow-priest": ("priest", "shadow"),
    "marksmanship-hunter": ("hunter", "marksmanship"),
}
SUFFIXES = (
    "pve-guide",
    "playing",
    "setting-up",
    "gearing",
    "gear-targets",
    "raiding",
)


def local_targets(source: str) -> list[str]:
    values = re.findall(r'(?:href|src)="([^"]+)"', source)
    return [
        value
        for value in values
        if not value.startswith(("http://", "https://", "data:", "mailto:", "#"))
    ]


for slug, (class_name, spec_name) in FAMILIES.items():
    expected_names = {f"{slug}-{suffix}.html" for suffix in SUFFIXES}
    actual_names = {path.name for path in GUIDES.glob(f"{slug}-*.html")}
    assert actual_names == expected_names, (slug, actual_names)

    for filename in sorted(expected_names):
        path = GUIDES / filename
        source = path.read_text(encoding="utf-8")
        assert "TODO" not in source, filename
        assert "data-template-placeholder" not in source, filename
        assert f'data-guide-class="{class_name}"' in source, filename
        assert f'data-guide-spec="{spec_name}"' in source, filename
        assert source.count('class="site-nav"') == 1, filename
        assert source.count('class="guide-hub-link"') == 1, filename
        assert source.count('aria-current="page"') == 1, filename
        assert 'id="sources"' in source, filename

        for target in local_targets(source):
            clean = urlsplit(target).path
            destination = (path.parent / clean).resolve()
            assert destination.exists(), f"{filename}: missing local target {target}"


hub = (ROOT / "index.html").read_text(encoding="utf-8")
for slug in FAMILIES:
    assert f'./guides/{slug}-pve-guide.html' in hub

hunter_pages = "\n".join(
    (GUIDES / f"marksmanship-hunter-{suffix}.html").read_text(encoding="utf-8")
    for suffix in SUFFIXES
)
assert "Trap Launcher: Explosive Trap" in hunter_pages
assert "traps are placed at the hunter's feet" in hunter_pages
assert "spell=82941" not in hunter_pages

print("Validated 18 complete fresh-80 Priest and Hunter pages, hub cards, and local links.")
