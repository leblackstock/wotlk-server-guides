#!/usr/bin/env python3
"""Validate Phase 3 Turn-in and Recipe Drop audits, pricing, notes, and search."""

from __future__ import annotations

import json
import re
import subprocess
import sys
import unicodedata
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load(path: str) -> dict:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def generated(path: str, variable: str) -> dict:
    source = (ROOT / path).read_text(encoding="utf-8")
    match = re.search(rf"window\.{variable}=(\{{.*?\}});\n", source, re.DOTALL)
    if not match:
        raise AssertionError(f"Could not parse {variable}")
    return json.loads(match.group(1))


def normalize(value: str) -> str:
    value = "".join(
        char
        for char in unicodedata.normalize("NFKD", value)
        if not unicodedata.combining(char)
    )
    value = value.casefold().replace("’", "").replace("'", "").replace("&", " and ")
    return " ".join(re.sub(r"[^a-z0-9]+", " ", value).split())


subprocess.run(
    [sys.executable, "scripts/audit-ah-phase3-catalogs.py", "--check"],
    cwd=ROOT,
    check=True,
)
for market in ("turn-ins", "recipes"):
    subprocess.run(
        [sys.executable, "scripts/review-ah-phase3-static-prices.py", "--market", market, "--check"],
        cwd=ROOT,
        check=True,
    )
subprocess.run(
    [sys.executable, "scripts/render-ah-phase3-static-guides.py", "--check"],
    cwd=ROOT,
    check=True,
)

turn_catalog = load("data/ah-turn-in-catalog.json")
turn_evidence = load("data/ah-turn-in-price-evidence.json")
recipe_audit = load("data/ah-recipe-drop-audit.json")
recipe_evidence = load("data/ah-recipe-drop-price-evidence.json")
baseline = load("data/ah-price-baselines.json")["items"]
index = generated("assets/ah-search-index.js", "AH_SEARCH_INDEX")
item_ids = generated("assets/ah-item-ids.js", "AH_ITEM_IDS")

assert turn_catalog["summary"] == {
    "auctionable_items": 74,
    "removed_nonauctionable": 3,
    "sections": 10,
}
assert {record["item_id"] for record in turn_catalog["removed_nonauctionable"]} == {
    24407,
    21377,
    21383,
}
assert turn_evidence["summary"]["items_reviewed"] == 74
assert turn_evidence["summary"]["items_seen_on_three_realms"] == 74
assert turn_evidence["summary"]["fetch_failed_observations"] == 0
assert turn_evidence["summary"]["decision_counts"] == {
    "cohort-rank-starter-estimate": 70,
    "preserve-shared-material-evidence": 4,
}
assert turn_evidence["sources"]["comparison_retry_summary"] == {
    "initial_requests": 444,
    "retry_delays_seconds": [2, 5, 10],
    "retry_rounds_used": 0,
    "final_failed_requests": 0,
}

assert recipe_audit["summary"]["items"] == 90
assert recipe_audit["summary"]["items_with_saved_loot_sources"] == 85
assert recipe_audit["summary"]["trainer_or_vendor_competitors"] == 5
assert recipe_evidence["summary"]["items_reviewed"] == 90
assert recipe_evidence["summary"]["items_seen_on_three_realms"] == 89
assert recipe_evidence["summary"]["items_seen_on_two_realms"] == 1
assert recipe_evidence["summary"]["fetch_failed_observations"] == 0
assert recipe_evidence["sources"]["comparison_retry_summary"] == {
    "initial_requests": 540,
    "retry_delays_seconds": [2, 5, 10],
    "retry_rounds_used": 0,
    "final_failed_requests": 0,
}
assert recipe_evidence["summary"]["decision_counts"] == {
    "cohort-rank-starter-estimate": 84,
    "limited-vendor-cost-correction": 5,
    "preserve-user-reported-sale-anchor": 1,
}

vendor_ids = {
    item_id
    for item_id, record in recipe_audit["items"].items()
    if record["trainer_or_vendor_competition"]
}
assert vendor_ids == {"15758", "16221", "18652", "7742", "10602"}
for item_id in vendor_ids:
    assert recipe_audit["items"][item_id]["vendor_sources"]
    assert recipe_evidence["items"][item_id]["proposal"]["decision"] == "limited-vendor-cost-correction"

book = recipe_evidence["items"]["45912"]
assert book["proposal"]["decision"] == "preserve-user-reported-sale-anchor"
assert book["proposal"]["proposed_band"] == {"quick": 125_000, "target": 250_000, "high": 600_000}
assert "Replaced original 2026-08-02 frozen baseline: 150g quick, 300g target, 700g high." in baseline["45912"]["reason"]

for evidence in (turn_evidence, recipe_evidence):
    assert evidence["rules"]["active_hellscream_listing_prices_used"] is False
    assert evidence["rules"]["external_gold_values_copied"] is False
    for item_id, record in evidence["items"].items():
        proposal = record["proposal"]
        assert {key: int(baseline[item_id][key]) for key in ("quick", "target", "high")} == proposal["proposed_band"]
        assert baseline[item_id]["source_type"] == proposal["source_type"]
        assert baseline[item_id]["confidence"] == proposal["confidence"]

search_counts = Counter(item["guideId"] for item in index["items"])
assert search_counts["turn-ins"] == 74
assert search_counts["recipe-pattern-drops"] == 90
for guide_id, evidence in (("turn-ins", turn_evidence), ("recipe-pattern-drops", recipe_evidence)):
    names = {record["name"] for record in evidence["items"].values()}
    indexed = {item["name"] for item in index["items"] if item["guideId"] == guide_id}
    assert indexed == names
    for name in names:
        assert item_ids.get(normalize(name))

for item in index["items"]:
    if item["guideId"] == "turn-ins" and item["name"].startswith("Shredder Operating Manual - Page"):
        assert item["stack"] == "—"

turn_guide = (ROOT / "guides/drop-turn-in-quest-page-items-ah-price-guide.html").read_text(encoding="utf-8")
recipe_guide = (ROOT / "guides/gear-pattern-drops-ah-price-guide.html").read_text(encoding="utf-8")
assert "Timbermaw repeatable drops" not in turn_guide
assert "Every priced row is one real auctionable item" in turn_guide
assert "non-stackable Shredder pages show no stack recommendation" in turn_guide
assert turn_guide.count("<tbody><tr") == 10
assert recipe_guide.count("Limited vendor:") == 5
assert "Eighty-five have pinned loot paths; five limited-vendor recipes" in recipe_guide
assert "Requires Inscription 425" in recipe_guide
assert "Updated 2026-08-08</footer>" in turn_guide
assert "Updated 2026-08-08</footer>" in recipe_guide
assert "Active listings show competition only and never set or raise guide prices." in turn_guide
assert "Active listings show competition only and never set or raise guide prices." in recipe_guide

print("Phase 3 Turn-in and Recipe Drop audits, prices, notes, search, and tooltips are valid.")
