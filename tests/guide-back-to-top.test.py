#!/usr/bin/env python3
"""Validate category back-to-top controls on long guides."""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
GUIDES_DIR = ROOT / "guides"
EXCLUDED_GUIDES = {"protection-paladin-pve-guide.html"}


def has_jump_navigation(source: str) -> bool:
    return 'guide-jump-nav' in source or 'class="jump-nav"' in source


subprocess.run(
    [sys.executable, "scripts/render-guide-back-to-top.py", "--check"],
    cwd=ROOT,
    check=True,
)

paths = sorted(
    path
    for path in GUIDES_DIR.glob("*.html")
    if path.name not in EXCLUDED_GUIDES
    and has_jump_navigation(path.read_text(encoding="utf-8"))
)
assert len(paths) >= 35

for path in paths:
    source = path.read_text(encoding="utf-8")
    assert source.count('id="top"') == 1, path.name
    headings = re.findall(r"<h2([^>]*)>(.*?)</h2>", source, flags=re.DOTALL)
    links = re.findall(
        r'<a class="guide-back-to-top" href="#top" aria-label="Back to top">↑ Top</a>',
        source,
    )
    assert headings, path.name
    assert len(links) == len(headings), path.name
    for attributes, content in headings:
        assert "guide-category-heading" in attributes, path.name
        assert content.endswith(
            '<a class="guide-back-to-top" href="#top" '
            'aria-label="Back to top">↑ Top</a>'
        ), path.name

print(f"Validated category controls on {len(paths)} long guides.")
