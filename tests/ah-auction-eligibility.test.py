#!/usr/bin/env python3
"""Require every AH source item to pass the pinned auction-eligibility audit."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    subprocess.run(
        [sys.executable, "scripts/audit-ah-auction-eligibility.py", "--check"],
        cwd=ROOT,
        check=True,
    )
    print("All public and canonical AH items pass the saved AzerothCore eligibility audit.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
