#!/usr/bin/env python3
"""Extract and apply the Addon Library build bundle."""
from __future__ import annotations

import base64
import io
import runpy
import tarfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CHUNKS = ROOT / ".addon-build"


def strip_trailing_whitespace(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    cleaned = "\n".join(line.rstrip() for line in text.splitlines()) + "\n"
    path.write_text(cleaned, encoding="utf-8", newline="\n")


def replace_once(text: str, old: str, new: str, label: str) -> str:
    if text.count(old) != 1:
        raise RuntimeError(f"Expected one {label} anchor, found {text.count(old)}")
    return text.replace(old, new, 1)


def patch_focus_restoration(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    text = replace_once(
        text,
        '    let originButton = null;\n    let dialogUrlWasPushed = false;\n',
        '    let originButton = null;\n    let originAddonId = "";\n    let pendingFocusAddonId = "";\n    let dialogUrlWasPushed = false;\n',
        "dialog focus state",
    )
    text = replace_once(
        text,
        '      originButton = button || document.querySelector(`[data-addon-id="${CSS.escape(addonId)}"] .addon-details-button`);\n      state.addon = addonId;\n',
        '      originButton = button || document.querySelector(`[data-addon-id="${CSS.escape(addonId)}"] .addon-details-button`);\n      originAddonId = addonId;\n      state.addon = addonId;\n',
        "dialog origin",
    )
    text = replace_once(
        text,
        '''    function closeDialog(updateHistory) {\n      if (dialog.open) dialog.close();\n      state.addon = "";\n      if (updateHistory) {\n        if (dialogUrlWasPushed) global.history.back();\n        else updateUrl("replace");\n      }\n      dialogUrlWasPushed = false;\n      if (originButton && document.contains(originButton)) originButton.focus();\n    }\n''',
        '''    function focusOrigin(addonId) {\n      const target = document.querySelector(`[data-addon-id="${CSS.escape(addonId)}"] .addon-details-button`);\n      if (target) target.focus();\n    }\n\n    function closeDialog(updateHistory) {\n      const focusAddonId = originAddonId || state.addon;\n      if (dialog.open) dialog.close();\n      state.addon = "";\n      if (updateHistory) {\n        if (dialogUrlWasPushed) {\n          pendingFocusAddonId = focusAddonId;\n          global.history.back();\n        } else {\n          updateUrl("replace");\n          focusOrigin(focusAddonId);\n        }\n      } else {\n        focusOrigin(focusAddonId);\n      }\n      dialogUrlWasPushed = false;\n    }\n''',
        "dialog close behavior",
    )
    text = replace_once(
        text,
        '''      render();\n      handlingHistory = false;\n    });\n''',
        '''      render();\n      if (pendingFocusAddonId) {\n        focusOrigin(pendingFocusAddonId);\n        pendingFocusAddonId = "";\n      }\n      handlingHistory = false;\n    });\n''',
        "history focus restoration",
    )
    path.write_text(text, encoding="utf-8", newline="\n")


def main() -> None:
    encoded = "".join(path.read_text(encoding="ascii") for path in sorted(CHUNKS.glob("chunk-*.txt")))
    if not encoded:
        raise RuntimeError("Addon Library bundle chunks are missing")
    with tarfile.open(fileobj=io.BytesIO(base64.b64decode(encoded)), mode="r:gz") as archive:
        for member in archive.getmembers():
            destination = (ROOT / member.name).resolve()
            if ROOT.resolve() not in destination.parents:
                raise RuntimeError(f"Unsafe bundled path: {member.name}")
        archive.extractall(ROOT, filter="data")
    runpy.run_path(str(ROOT / "scripts" / "apply-addon-library.py"), run_name="__main__")
    patch_focus_restoration(ROOT / "assets" / "addon-catalog.js")
    strip_trailing_whitespace(ROOT / "internal" / "color-system.html")


if __name__ == "__main__":
    main()
