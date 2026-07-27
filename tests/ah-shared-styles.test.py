#!/usr/bin/env python3
"""Validate that AH guide styles remain shared and scoped."""

from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
GUIDES_DIR = ROOT / "guides"
STYLES_PATH = ROOT / "assets" / "ah-price-guide.css"


guide_paths = sorted(GUIDES_DIR.glob("*ah-price-guide.html"))
assert len(guide_paths) == 16

inline_style_guides = [
    path.name
    for path in guide_paths
    if re.search(r"<style(?:\s|>)", path.read_text(encoding="utf-8"), re.IGNORECASE)
]
assert not inline_style_guides, (
    "AH guide styles must live in the shared stylesheet: "
    + ", ".join(inline_style_guides)
)

styles = STYLES_PATH.read_text(encoding="utf-8")
required_selectors = (
    'body[data-guide-section="auction-house"] .ah-item-link',
    'body[data-guide-section="auction-house"] .ah-item-link:hover',
    'body[data-guide-section="auction-house"] .ah-item-link:focus-visible',
    'body[data-guide-section="auction-house"] .ah-item-icon',
)
for selector in required_selectors:
    assert selector in styles, f"Missing shared selector: {selector}"

print("Validated shared, scoped styling across 16 AH guides.")
