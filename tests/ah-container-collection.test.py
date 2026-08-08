#!/usr/bin/env python3
"""Guard the generated 93-row Bags & Containers collection."""

from __future__ import annotations

import importlib.util
import json
import re
import subprocess
import sys
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PAGE_PATH = ROOT / "guides" / "bags-containers-ah-guide.html"
AUDIT_PATH = ROOT / "data" / "ah-container-audit.json"
VENDOR_PATH = ROOT / "data" / "ah-vendor-sections.json"
MANIFEST_PATH = ROOT / "data" / "ah-guides.json"
RENDERER_PATH = ROOT / "scripts" / "render-ah-container-collection.py"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


subprocess.run([sys.executable, str(RENDERER_PATH), "--check"], cwd=ROOT, check=True)

spec = importlib.util.spec_from_file_location("container_collection_renderer", RENDERER_PATH)
renderer = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(renderer)
collection, canonical_rows = renderer.build_rows()

audit = load(AUDIT_PATH)
vendor = load(VENDOR_PATH)
manifest = load(MANIFEST_PATH)
source = PAGE_PATH.read_text(encoding="utf-8")

included_ids = {
    int(item_id)
    for item_id, item in audit["items"].items()
    if item["decision"].startswith("included-")
}
assert len(included_ids) == 93
assert len(canonical_rows) == 93
assert {row["item_id"] for row in canonical_rows} == included_ids
assert Counter(row["source_type"] for row in canonical_rows) == {
    "crafted": 52,
    "vendor": 19,
    "drop": 21,
    "quest-reward": 1,
}
assert Counter(row["category_key"] for row in canonical_rows) == {
    "general": 48,
    "profession": 27,
    "hunter": 18,
}
assert {row["expansion"] for row in canonical_rows} == {"Classic", "Outland", "Wrath"}
assert all(row["quick_copper"] <= row["target_copper"] for row in canonical_rows)
assert all(
    row["high_copper"] is None or row["target_copper"] <= row["high_copper"]
    for row in canonical_rows
)
assert all(row["owner_href"].startswith("./") and "#ah-item=" in row["owner_href"] for row in canonical_rows)

row_tags = re.findall(r"<tr data-container-row\b[^>]*>", source)
assert len(row_tags) == 93
rendered_ids = {
    int(re.search(r'data-item-id="(\d+)"', tag).group(1))
    for tag in row_tags
}
assert rendered_ids == included_ids
assert source.count('class="container-item-link"') == 93
assert source.count('class="container-owner-link"') == 93
assert source.count('data-column="target" data-label="Target"') == 93
assert source.count('data-column="slots" data-label="Slots"') == 93
assert source.count('data-column="item" data-label="Item"') == 93
assert source.count('data-ah-container-collection-link') == 0
assert "data-stack" not in source
assert "One collection, one price owner" in source
assert "Vendor cost" in source
assert "Updated 2026-08-08</footer>" in source
assert '../assets/ah-containers.css?v=20260808-container-collection-v1' in source
assert '../assets/ah-containers.js?v=20260808-container-collection-v1' in source
assert '../assets/ah-item-tooltips.js?v=20260808-container-collection-v1' in source
for quality in {row["quality"] for row in canonical_rows}:
    assert f'class="q-{quality}"' in source

collections = [item for item in manifest["collections"] if item["id"] == "bags-containers"]
assert len(collections) == 1
assert collections[0]["file"] == PAGE_PATH.name
assert PAGE_PATH.name not in {guide["file"] for guide in manifest["guides"]}

vendor_ids = {
    int(item_id)
    for item_id, item in audit["items"].items()
    if item["primary_source"] == "vendor"
}
vendor_rows = [item for item in vendor["catalog"].values() if int(item["item_id"]) in vendor_ids]
assert len(vendor_rows) == 19
assert all(item["expansion"] in {"Classic", "Outland", "Wrath"} for item in vendor_rows)

for filename in ("index.html", "auction-house.html"):
    hub = (ROOT / filename).read_text(encoding="utf-8")
    assert hub.count("data-ah-container-collection-link") == 1
    assert 'href="./guides/bags-containers-ah-guide.html">Bags</a>' in hub

print(
    "Bags & Containers collection is current: 93 canonical rows, four source types, "
    "three buyer categories, three expansions, and two AH Library shortcuts."
)
