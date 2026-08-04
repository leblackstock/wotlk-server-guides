#!/usr/bin/env python3
"""Guard the non-circular AH baseline and profession repricing model."""

from __future__ import annotations

import json
import re
import subprocess
import sys
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASELINE_PATH = ROOT / "data" / "ah-price-baselines.json"
CATALOG_PATH = ROOT / "data" / "ah-crafted-sections.json"
AUDIT_PATH = ROOT / "data" / "ah-crafted-recipe-audit.json"
VENDOR_PATH = ROOT / "data" / "ah-vendor-sections.json"


def fail(message: str) -> None:
    raise AssertionError(message)


def merged_item(config: dict, key: str) -> dict:
    raw = config["catalog"][key]
    return config.get("catalog_defaults", {}) | config["price_profiles"][raw["profile"]] | raw


def main() -> int:
    subprocess.run(
        [sys.executable, "scripts/apply-ah-price-baselines.py", "--check"],
        cwd=ROOT,
        check=True,
    )
    baseline = json.loads(BASELINE_PATH.read_text(encoding="utf-8"))
    config = json.loads(CATALOG_PATH.read_text(encoding="utf-8"))
    audit = json.loads(AUDIT_PATH.read_text(encoding="utf-8"))
    vendor = json.loads(VENDOR_PATH.read_text(encoding="utf-8"))

    if baseline.get("diagnostic_observations", {}).get("used_to_set_prices") is not False:
        fail("Active-listing diagnostics must be excluded from baseline prices")
    if len(baseline.get("items", {})) != 701:
        fail("Frozen baseline must contain 650 pre-scan references plus 51 documented profession-input fallbacks")
    confidence = Counter(record["confidence"] for record in baseline["items"].values())
    if confidence != Counter({"low": 649, "medium": 1, "fallback": 51}):
        fail(f"Unexpected initial baseline confidence distribution: {confidence}")
    for item_id, record in baseline["items"].items():
        if record["source_type"] not in baseline["allowed_evidence"]:
            fail(f"{item_id}: unapproved baseline evidence {record['source_type']}")
        if record["confidence"] not in baseline["confidence_levels"]:
            fail(f"{item_id}: invalid confidence {record['confidence']}")
        if not int(record["quick"]) <= int(record["target"]) <= int(record["high"]):
            fail(f"{item_id}: invalid baseline band ordering")
    for item_id, record in audit["reagent_price_overrides"].items():
        expected_confidence = "high" if record["source_type"] == "coin-vendor" else "fallback"
        if record.get("confidence") != expected_confidence:
            fail(f"{item_id}: reagent override confidence is missing or incorrect")

    solid_stone = baseline["items"]["7912"]
    if solid_stone["source_type"] != "realized-sales-history" or solid_stone["target"] != 900:
        fail("Solid Stone realized-sale validation is missing")
    glyph_book = baseline["items"]["45912"]
    if tuple(glyph_book[band] for band in ("quick", "target", "high")) != (
        125_000,
        250_000,
        600_000,
    ):
        fail("Book of Glyph Mastery user-estimated sale band is missing")
    if (
        glyph_book["source_type"] != "realized-sales-history"
        or glyph_book["confidence"] != "low"
        or "2026-08-03" not in glyph_book["reason"]
        or "150g quick, 300g target, 700g high" not in glyph_book["reason"]
        or "may be updated if later evidence differs" not in glyph_book["reason"]
    ):
        fail("Book of Glyph Mastery provenance or original baseline note is missing")
    expected_inputs = {
        "36912": (4_500, 7_000, 11_000),
        "36913": (9_000, 15_000, 22_000),
        "2835": (100, 200, 400),
        "4338": (700, 1_000, 1_600),
        "32227": (80_000, 120_000, 200_000),
        "32229": (70_000, 100_000, 180_000),
        "24243": (10_000, 20_000, 37_500),
    }
    for item_id, expected in expected_inputs.items():
        record = baseline["items"][item_id]
        actual = tuple(int(record[band]) for band in ("quick", "target", "high"))
        if actual != expected:
            fail(f"{record['name']}: frozen pre-scan baseline drifted")

    forbidden = "Current Garrosh-Horde full scan"
    if forbidden in AUDIT_PATH.read_text(encoding="utf-8"):
        fail("Active scan provenance remains in the recipe audit")
    if forbidden in (ROOT / "scripts" / "audit-ah-crafted-prices.py").read_text(encoding="utf-8"):
        fail("Active scan provenance remains in the pricing code")

    recipes = audit["recipes"]
    output_ids = {int(recipe["output_item_id"]) for recipe in recipes.values()}
    baseline_ids = {int(item_id) for item_id in baseline["items"]}
    override_ids = {int(item_id) for item_id in audit["reagent_price_overrides"]}
    vendor_ids = {
        int(item["item_id"])
        for item in vendor["catalog"].values()
        if item["source_type"] == "coin-vendor"
    }
    canonical_ids = {int(item["item_id"]) for item in config["catalog"].values()}
    missing = {}
    for key, recipe in recipes.items():
        for reagent in recipe["reagents"]:
            item_id = int(reagent["item_id"])
            if item_id not in output_ids | baseline_ids | override_ids | vendor_ids | canonical_ids:
                missing.setdefault(item_id, set()).add(key)
    if missing:
        fail(f"Recipe inputs lack non-circular coverage: {missing}")

    blacksmithing_inputs = {
        int(reagent["item_id"])
        for key, recipe in recipes.items()
        if key.startswith("bs-")
        for reagent in recipe["reagents"]
    }
    if len(blacksmithing_inputs) != 149:
        fail(f"Expected 149 direct Blacksmithing inputs, found {len(blacksmithing_inputs)}")
    tailoring_inputs = {
        int(reagent["item_id"])
        for key, recipe in recipes.items()
        if key.startswith("tailor-")
        for reagent in recipe["reagents"]
    }
    if len(tailoring_inputs) != 147:
        fail(f"Expected 147 direct Tailoring inputs, found {len(tailoring_inputs)}")
    leatherworking_inputs = {
        int(reagent["item_id"])
        for key, recipe in recipes.items()
        if key.startswith("lw-")
        for reagent in recipe["reagents"]
    }
    if len(leatherworking_inputs) != 165:
        fail(f"Expected 165 direct Leatherworking inputs, found {len(leatherworking_inputs)}")
    cooking_inputs = {
        int(reagent["item_id"])
        for key, recipe in recipes.items()
        if key.startswith("cook-")
        for reagent in recipe["reagents"]
    }
    if len(cooking_inputs) != 148:
        fail(f"Expected 148 direct Cooking inputs, found {len(cooking_inputs)}")
    for item_id in ("12607", "15409", "15410", "20381", "25699", "25719"):
        record = baseline["items"][item_id]
        if record["source_type"] != "documented-fallback" or record["confidence"] != "fallback":
            fail(f"{record['name']}: Leatherworking fallback evidence is mislabeled")
    for item_id in (
        "3172",
        "3174",
        "5471",
        "12206",
        "22644",
        "23676",
        "27676",
        "41800",
        "41801",
        "43501",
        "44834",
    ):
        record = baseline["items"][item_id]
        if record["source_type"] != "documented-fallback" or record["confidence"] != "fallback":
            fail(f"{record['name']}: Cooking fallback evidence is mislabeled")

    representative_targets = {
        "bs-eternal-belt-buckle": 350_000,
        "bs-titanium-rod": 180_000,
        "bs-saronite-defender": 125_000,
        "bs-puresteel-legplates": 76_500_000,
        "bs-rough-grinding-stone": 800,
    }
    for key, expected in representative_targets.items():
        actual = int(merged_item(config, key)["target_copper"])
        if actual != expected:
            fail(f"{key}: non-circular target changed unexpectedly ({actual})")

    guide = config["guides"]["blacksmithing-materials-ah-price-guide.html"]
    note = guide["shared_note"]["text"]
    if "Active AH listings never set or raise the baseline" not in note:
        fail("Blacksmithing guide does not explain the listing-price guard")
    methodology = (ROOT / "docs" / "ah-pricing-methodology.md").read_text(encoding="utf-8")
    if not re.search(r"No script may automatically update.*active\s+listings", methodology, re.DOTALL):
        fail("Saved methodology does not prohibit automatic listing repricing")

    print(
        "Non-circular AH baseline is valid: 701 frozen references and documented fallbacks, "
        "149 Blacksmithing, 147 Tailoring, 165 Leatherworking, and 148 Cooking inputs covered; active scans excluded."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
