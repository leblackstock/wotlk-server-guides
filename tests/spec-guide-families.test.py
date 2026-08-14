#!/usr/bin/env python3
"""Validate the complete config-backed fresh-80 guide families."""

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
    "affliction-warlock": ("warlock", "affliction"),
    "demonology-warlock": ("warlock", "demonology"),
    "destruction-warlock": ("warlock", "destruction"),
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
assert "hunter/502-035325131030013233135031051-5000002" in hunter_pages
assert "hunter/502-035335131030013233035031051-5000002" not in hunter_pages
assert "1/1 Trueshot Aura" in hunter_pages
assert "2/3 Improved Hunter's Mark" in hunter_pages
assert "later progression chapter, not the starting expectation" in hunter_pages
assert "Updated 2026-08-14" in (
    GUIDES / "marksmanship-hunter-gearing.html"
).read_text(encoding="utf-8")
assert hunter_pages.count("Updated 2026-08-05") == len(SUFFIXES) - 1

print("Validated 36 complete config-backed fresh-80 pages, hub cards, and local links.")
