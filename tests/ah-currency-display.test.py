#!/usr/bin/env python3
"""Guard the site-wide two-currency AH display rule."""

from __future__ import annotations

import importlib.util
import json
import re
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
GUIDES = ROOT / "guides"
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from ah_guides import active_guide_paths  # noqa: E402

RENDERER_PATH = ROOT / "scripts" / "render-ah-shared-sections.py"
INDEX_PATH = ROOT / "assets" / "ah-search-index.js"
MONEY_SPAN = re.compile(r'<span class="(?:bid|buyout)">([^<]+)</span>')
THREE_CURRENCIES = re.compile(r'\d[\d,]*g\s+\d+s\s+\d+c')


def load_renderer():
    sys.path.insert(0, str(ROOT / "scripts"))
    spec = importlib.util.spec_from_file_location("ah_renderer", RENDERER_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("Could not load AH renderer")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


subprocess.run(
    [sys.executable, "scripts/render-ah-shared-sections.py", "--check"],
    cwd=ROOT,
    check=True,
)
subprocess.run(
    [sys.executable, "scripts/build-ah-search-index.py", "--check"],
    cwd=ROOT,
    check=True,
)

renderer = load_renderer()
assert renderer.format_money(0) == "0c"
assert renderer.format_money(85) == "85c"
assert renderer.format_money(9_999) == "99s 99c"
assert renderer.format_money(10_000) == "1g"
assert renderer.format_money(14_849) == "1g 48s"
assert renderer.format_money(14_850) == "1g 49s"
assert renderer.format_money(14_875) == "1g 49s"
assert renderer.format_money(999_999) == "100g"

guide_paths = active_guide_paths(guides_dir=GUIDES)
assert len(guide_paths) == 18
price_count = 0
for path in guide_paths:
    source = path.read_text(encoding="utf-8")
    assert not THREE_CURRENCIES.search(source), path.name
    expected_date = (
        "2026-08-08"
        if path.name in {
            "tailoring-cloth-ah-price-guide.html",
            "skinning-leatherworking-materials-ah-price-guide.html",
            "fishing-cooking-materials-ah-price-guide.html",
            "mining-smithing-ah-price-guide.html",
            "cross-profession-materials-ah-price-guide.html",
            "drop-turn-in-quest-page-items-ah-price-guide.html",
            "gear-pattern-drops-ah-price-guide.html",
            "level-80-boe-epics-ah-price-guide.html",
            "sought-after-world-drops-ah-price-guide.html",
        }
        else "2026-08-06"
    )
    assert f"Updated {expected_date}" in source, path.name
    for label in MONEY_SPAN.findall(source):
        units = re.findall(r"[gsc]", label)
        assert len(units) <= 2, (path.name, label)
        assert not ("g" in units and "c" in units), (path.name, label)
        price_count += 1

index_source = INDEX_PATH.read_text(encoding="utf-8").splitlines()[1]
index = json.loads(
    index_source.removeprefix("window.AH_SEARCH_INDEX=").removesuffix(";")
)
truesilver = [item for item in index["items"] if item["name"] == "Truesilver Bar"]
assert len(truesilver) == 2
assert {item["targetBid"] for item in truesilver} == {"55s 25c"}
assert {item["target"] for item in truesilver} == {"65s"}

print(
    f"Two-currency display rule passed for {price_count} AH bid/buyout values; "
    "rounding-equivalent Truesilver Bar entries agree."
)
