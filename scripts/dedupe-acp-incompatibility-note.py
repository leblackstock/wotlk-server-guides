#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

root = Path(__file__).resolve().parents[1]
path = root / "data" / "addons.json"
catalog = json.loads(path.read_text(encoding="utf-8"))
addon = next(item for item in catalog["addons"] if item["id"] == "addon-control-panel")
addon["doesNot"] = [
    "Does not hot-load every addon safely; most changes still require ReloadUI.",
    "Does not replace addon configuration panels or repair errors inside other addons.",
]
joined = json.dumps(addon, ensure_ascii=False)
if joined.count("3.3.7") != 1:
    raise SystemExit(f"Expected exactly one ACP 3.3.7 mention, found {joined.count('3.3.7')}")
path.write_text(json.dumps(catalog, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
print("Kept one ACP 3.3.7 incompatibility note.")
