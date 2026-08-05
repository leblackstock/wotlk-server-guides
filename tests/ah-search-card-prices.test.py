#!/usr/bin/env python3
"""Validate that every AH search row can populate grouped-card bid and buyout values."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
INDEX_PATH = ROOT / "assets" / "ah-search-index.js"
SEARCH_SCRIPT_PATH = ROOT / "assets" / "ah-search.js"
CANONICAL_VALUES_PATH = ROOT / "data" / "ah-search-canonical-values.json"


subprocess.run(
    [sys.executable, "scripts/build-ah-search-index.py", "--check"],
    cwd=ROOT,
    check=True,
)

index_source = INDEX_PATH.read_text(encoding="utf-8").splitlines()[1]
index = json.loads(
    index_source.removeprefix("window.AH_SEARCH_INDEX=").removesuffix(";")
)
assert index["version"] == 5
assert index["itemCount"] == len(index["items"])
assert index["items"]

canonical = json.loads(CANONICAL_VALUES_PATH.read_text(encoding="utf-8"))

for item in index["items"]:
    assert "targetBid" in item, item["name"]
    assert "target" in item, item["name"]
    assert "stack" in item, item["name"]
    assert item["targetBid"], item["name"]
    assert item["target"], item["name"]
    assert item["stack"], item["name"]
    assert item["stack"] != "—", item["name"]

groups: dict[str, list[dict[str, object]]] = {}
for item in index["items"]:
    groups.setdefault(item["name"].casefold(), []).append(item)

for name, matches in groups.items():
    if len(matches) < 2:
        continue
    for field in ("targetBid", "target", "stack", "demand"):
        values = {item[field] for item in matches}
        assert len(values) == 1, (name, field, values)

for field, entries in (
    ("stack", canonical["canonical_stack"]),
    ("demand", canonical["canonical_demand"]),
):
    for name, entry in entries.items():
        matches = groups[name.casefold()]
        assert {item[field] for item in matches} == {entry["value"]}, name
        assert any(item["guideId"] == entry["source_guide_id"] for item in matches), name
        if field == "stack":
            stack_counts = [int(part.strip()) for part in entry["value"].split("/")]
            assert all(1 <= count <= entry["max_stack"] for count in stack_counts), name

search_script = SEARCH_SCRIPT_PATH.read_text(encoding="utf-8")
assert '"Target Bid"' in search_script
assert '"Buyout"' in search_script
assert 'uniqueValues(matches, "targetBid")' in search_script
assert 'uniqueValues(matches, "target")' in search_script
assert 'uniqueValues(matches, "stack")' in search_script
assert 'uniqueValues(matches, "demand")' in search_script
assert 'const targetBidValue = bidValues[0] || "—"' in search_script
assert 'const targetBuyoutValue = buyoutValues[0] || "—"' in search_script
assert 'const stackValue = stackValues[0] || "—"' in search_script
assert 'const demandValue = demandValues[0] || "—"' in search_script
assert '"Stack"' in search_script
assert '"Recommended stack"' not in search_script
assert '"Varies"' not in search_script
assert '"Varies by guide"' not in search_script
assert '"Demand varies by guide"' not in search_script
assert "summarizePriceValues" not in search_script
assert "summarizeStackValues" not in search_script
assert "summarizeDemandValues" not in search_script
assert 'stackValue !== "1"' in search_script

print(
    f"Validated canonical price, stack, and demand fields for all "
    f"{index['itemCount']} AH search-index entries."
)
