"""Canonical active-guide discovery for the Auction House site."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = ROOT / "data" / "ah-guides.json"
GUIDES_DIR = ROOT / "guides"


def load_guide_manifest(path: Path = MANIFEST_PATH) -> dict:
    manifest = json.loads(path.read_text(encoding="utf-8"))
    if int(manifest.get("version", 0)) != 1:
        raise ValueError("Unsupported AH guide manifest version")
    guides = manifest.get("guides", [])
    expected = int(manifest.get("active_guide_count", 0))
    if len(guides) != expected:
        raise ValueError(f"Expected {expected} active AH guides, found {len(guides)}")
    ids = [str(guide["id"]) for guide in guides]
    files = [str(guide["file"]) for guide in guides]
    if len(ids) != len(set(ids)):
        raise ValueError("AH guide manifest contains duplicate stable IDs")
    if len(files) != len(set(files)):
        raise ValueError("AH guide manifest contains duplicate active filenames")
    redirect_files = {str(redirect["file"]) for redirect in manifest.get("redirects", [])}
    overlap = sorted(set(files) & redirect_files)
    if overlap:
        raise ValueError(f"AH guide files cannot be both active and redirects: {overlap}")
    return manifest


def active_guide_paths(
    manifest: dict | None = None,
    guides_dir: Path = GUIDES_DIR,
) -> list[Path]:
    manifest = manifest or load_guide_manifest()
    paths = [guides_dir / str(guide["file"]) for guide in manifest["guides"]]
    missing = [path for path in paths if not path.is_file()]
    if missing:
        labels = ", ".join(str(path) for path in missing)
        raise FileNotFoundError(f"Missing active AH guide pages: {labels}")
    return paths


def guide_by_file(manifest: dict | None = None) -> dict[str, dict]:
    manifest = manifest or load_guide_manifest()
    return {str(guide["file"]): guide for guide in manifest["guides"]}
