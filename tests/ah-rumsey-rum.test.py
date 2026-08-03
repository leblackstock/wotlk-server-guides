#!/usr/bin/env python3
"""Validate Rumsey Rum Black Label pricing and placement."""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
GUIDE_PATH = ROOT / "guides" / "fishing-cooking-materials-ah-price-guide.html"
INDEX_PATH = ROOT / "assets" / "ah-search-index.js"
CATEGORY = "Finished foods and utility drinks"


subprocess.run(
    [sys.executable, "scripts/build-ah-search-index.py", "--check"],
    cwd=ROOT,
    check=True,
)

source = GUIDE_PATH.read_text(encoding="utf-8")
assert source.count(">Rumsey Rum Black Label<") == 1
assert CATEGORY in source
assert "item=21151/rumsey-rum-black-label" in source

row_match = re.search(
    r"<tr><td[^>]*><strong[^>]*>Rumsey Rum Black Label</strong>.*?</tr>",
    source,
    flags=re.DOTALL,
)
assert row_match is not None
row = row_match.group(0)
for expected in (
    '<span class="bid">8s 50c</span>',
    '<span class="buyout">10s</span>',
    '<span class="bid">4s 25c</span>',
    '<span class="buyout">5s</span>',
    '<span class="bid">17s</span>',
    '<span class="buyout">20s</span>',
    'data-label="Stack Size">1 / 5 / 10',
    "bought for 2s each",
    "Vendor for 50c each if it returns twice",
):
    assert expected in row

index_source = INDEX_PATH.read_text(encoding="utf-8").splitlines()[1]
index = json.loads(
    index_source.removeprefix("window.AH_SEARCH_INDEX=").removesuffix(";")
)
matches = [
    item
    for item in index["items"]
    if item["name"] == "Rumsey Rum Black Label"
]
assert len(matches) == 1
item = matches[0]
assert item["guide"] == "Fishing + Cooking"
assert item["section"] == CATEGORY
assert item["targetBid"] == "8s 50c"
assert item["target"] == "10s"

print("Rumsey Rum Black Label placement, pricing, decision rule, and search data are valid.")
