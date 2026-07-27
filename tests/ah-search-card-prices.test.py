#!/usr/bin/env python3
"""Validate that every AH search card exposes target bid and buyout."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
INDEX_PATH = ROOT / "assets" / "ah-search-index.js"
SEARCH_SCRIPT_PATH = ROOT / "assets" / "ah-search.js"


subprocess.run(
    [sys.executable, "scripts/build-ah-search-index.py", "--check"],
    cwd=ROOT,
    check=True,
)

index_source = INDEX_PATH.read_text(encoding="utf-8").splitlines()[1]
index = json.loads(
    index_source.removeprefix("window.AH_SEARCH_INDEX=").removesuffix(";")
)
assert index["version"] == 2
assert index["itemCount"] == len(index["items"])
assert index["items"]

for item in index["items"]:
    assert "targetBid" in item, item["name"]
    assert "target" in item, item["name"]
    assert item["targetBid"], item["name"]
    assert item["target"], item["name"]

search_script = SEARCH_SCRIPT_PATH.read_text(encoding="utf-8")
assert '"Target Bid"' in search_script
assert '"Buyout"' in search_script
assert "item.targetBid" in search_script
assert "item.target" in search_script

print(
    f"Validated target bid and buyout fields for all "
    f"{index['itemCount']} AH search cards."
)
