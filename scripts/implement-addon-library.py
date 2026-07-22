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


if __name__ == "__main__":
    main()
