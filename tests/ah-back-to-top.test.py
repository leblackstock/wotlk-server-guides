#!/usr/bin/env python3
"""Validate category back-to-top controls on every AH guide."""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
GUIDES_DIR = ROOT / "guides"
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from ah_guides import active_guide_paths  # noqa: E402


subprocess.run(
    [sys.executable, "scripts/render-ah-shared-sections.py", "--check"],
    cwd=ROOT,
    check=True,
)

paths = active_guide_paths(guides_dir=GUIDES_DIR)
assert len(paths) == 18

category_count = 0
for path in paths:
    source = path.read_text(encoding="utf-8")
    assert source.count('id="top"') == 1, path.name
    headings = re.findall(r"<h2([^>]*)>(.*?)</h2>", source, flags=re.DOTALL)
    links = re.findall(
        r'<a class="ah-back-to-top" href="#top" aria-label="Back to top">↑ Top</a>',
        source,
    )
    assert headings, path.name
    assert len(links) == len(headings), path.name
    for attributes, content in headings:
        assert "ah-category-heading" in attributes, path.name
        assert content.endswith(
            '<a class="ah-back-to-top" href="#top" '
            'aria-label="Back to top">↑ Top</a>'
        ), path.name
    category_count += len(headings)

print(f"Validated {category_count} category controls across {len(paths)} AH guides.")
