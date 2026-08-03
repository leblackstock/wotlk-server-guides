#!/usr/bin/env python3
"""Validate profession-restricted and general-use AH crafted sections."""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
GUIDES = ROOT / "guides"
AUDIT = json.loads((ROOT / "data" / "ah-profession-use-audit.json").read_text(encoding="utf-8"))
CRAFTED = json.loads((ROOT / "data" / "ah-crafted-sections.json").read_text(encoding="utf-8"))

subprocess.run(
    [sys.executable, str(ROOT / "scripts" / "render-ah-shared-sections.py"), "--check"],
    check=True,
    cwd=ROOT,
)
subprocess.run(
    [sys.executable, str(ROOT / "scripts" / "apply-ah-profession-use-sections.py"), "--check"],
    check=True,
    cwd=ROOT,
)

hard = AUDIT["canonical_hard_requirements"]
profession_audience = AUDIT["canonical_profession_audience"]
general_exceptions = AUDIT["canonical_general_use_exceptions"]
assert len(hard) == 15
assert len(profession_audience) == 10
assert len(general_exceptions) == 7
assert len(AUDIT["vendor_hard_requirements"]) == 3
assert len(AUDIT["static_hard_requirements"]) == 4
assert len(AUDIT["static_general_use_exceptions"]) == 2
assert len(AUDIT["excluded_items"]) == 4

locations: dict[str, tuple[str, dict]] = {}
for filename, guide in CRAFTED["guides"].items():
    for section in guide["sections"]:
        for key in section["items"]:
            assert key not in locations, f"Duplicate crafted item placement: {key}"
            locations[key] = (filename, section)

for key, requirement in hard.items():
    filename, section = locations[key]
    assert section.get("audience") == "profession-restricted", (
        f"{key} is not in a profession-restricted section"
    )
    assert int(CRAFTED["catalog"][key]["item_id"]) == int(requirement["item_id"])
    source = (GUIDES / filename).read_text(encoding="utf-8")
    row = re.search(
        rf'<tr data-crafted-key="{re.escape(key)}".*?</tr>', source, re.DOTALL
    )
    assert row, f"Missing rendered crafted row: {key}"
    expected = f'Requires {requirement["skill"]} {requirement["rank"]} to use.'
    assert row.group(0).count(expected) == 1, f"Missing exact requirement note: {key}"

for key in profession_audience:
    _, section = locations[key]
    assert section.get("audience") in {"profession-restricted", "profession-input"}, (
        f"{key} is incorrectly presented as general-use"
    )

for key in general_exceptions:
    _, section = locations[key]
    assert section.get("audience", "general-use") == "general-use", (
        f"{key} should remain general-use"
    )

engineering = (GUIDES / "engineering-materials-ah-price-guide.html").read_text(encoding="utf-8")
for name in ("Gnomish Army Knife", "Mana Injector Kit"):
    row = re.search(
        rf'<tr data-crafted-key="[^"]+".*?{re.escape(name)}.*?</tr>',
        engineering,
        re.DOTALL,
    )
    assert row and "No profession required:" in row.group(0)

for section_id, section in AUDIT["static_sections"].items():
    source = (GUIDES / section["guide"]).read_text(encoding="utf-8")
    assert source.count(f"AH_PROFESSION_USE_SECTION_START {section_id}") == 1
    block = re.search(
        rf'<!-- AH_PROFESSION_USE_SECTION_START {re.escape(section_id)} -->.*?'
        rf'<!-- AH_PROFESSION_USE_SECTION_END {re.escape(section_id)} -->',
        source,
        re.DOTALL,
    )
    assert block
    for name in section["items"]:
        requirement = next(
            entry for entry in AUDIT["static_hard_requirements"]
            if entry["guide"] == section["guide"] and entry["name"] == name
        )
        assert block.group(0).count(f">{name}</strong>") == 1
        action = "place" if name.endswith("Feast") else "use"
        expected = f'Requires {requirement["skill"]} {requirement["rank"]} to {action}.'
        assert expected in block.group(0)

fishing = (GUIDES / "fishing-cooking-materials-ah-price-guide.html").read_text(encoding="utf-8")
assert "Finished foods and utility drinks" in fishing
assert "Finished foods, feasts, and utility drinks" not in fishing
jewelcrafting = (GUIDES / "jewelcrafting-gems-ah-price-guide.html").read_text(encoding="utf-8")
assert ">Epic Northrend gems<a" in jewelcrafting
assert "Epic Northrend gems / Dragon's Eye" not in jewelcrafting

leatherworking = (GUIDES / "skinning-leatherworking-materials-ah-price-guide.html").read_text(encoding="utf-8")
for entry in AUDIT["static_general_use_exceptions"]:
    assert entry["name"] in leatherworking
assert leatherworking.count("No profession required:</strong> the finished drums") == 2

engineering_mounts = engineering[
    engineering.index('id="engineer-only-mount-components"'):
    engineering.index("<!-- AH_VENDOR_SECTION_END -->")
]
for key, requirement in AUDIT["vendor_hard_requirements"].items():
    assert f'data-vendor-key="{key}"' in engineering_mounts
    expected = f'Requires {requirement["skill"]} {requirement["rank"]} to use.'
    assert expected in engineering_mounts
assert "Mount / expensive special components" not in engineering

all_guide_source = "\n".join(
    path.read_text(encoding="utf-8")
    for path in sorted(GUIDES.glob("*ah-price-guide.html"))
)
for excluded in AUDIT["excluded_items"]:
    assert excluded["name"] not in all_guide_source, excluded["name"]

print(
    "Profession-use audit is current: "
    "22 hard-restricted finished items, 10 profession-audience items, "
    "and 9 documented general-use exceptions."
)
