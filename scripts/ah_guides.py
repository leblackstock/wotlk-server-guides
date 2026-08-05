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

    group_ids = {str(group["id"]) for group in manifest.get("groups", [])}
    guides_by_id = {str(guide["id"]): guide for guide in guides}
    hub_cards = manifest.get("hub_cards", [])
    hub_card_ids = [str(card["id"]) for card in hub_cards]
    if len(hub_card_ids) != len(set(hub_card_ids)):
        raise ValueError("AH guide manifest contains duplicate hub-card IDs")

    grouped_guide_ids: set[str] = set()
    for card in hub_cards:
        card_id = str(card["id"])
        card_type = str(card.get("type", ""))
        if card_type not in {"multi-guide", "category-link"}:
            raise ValueError(f"{card_id}: unsupported hub-card type {card_type!r}")
        if str(card.get("group", "")) not in group_ids:
            raise ValueError(f"{card_id}: unknown hub-card group")
        links = card.get("links", [])
        if not links:
            raise ValueError(f"{card_id}: hub card needs at least one link")
        if card_type == "category-link" and len(links) != 1:
            raise ValueError(f"{card_id}: category-link cards need exactly one link")
        if card_type == "multi-guide" and len(links) < 2:
            raise ValueError(f"{card_id}: multi-guide cards need at least two links")

        for link in links:
            guide_id = str(link.get("guide_id", ""))
            guide = guides_by_id.get(guide_id)
            if guide is None:
                raise ValueError(f"{card_id}: unknown guide ID {guide_id!r}")
            category = link.get("category")
            if card_type == "category-link" and not category:
                raise ValueError(f"{card_id}: category-link destination needs a category")
            if category:
                pending = list(guide.get("navigation", []))
                navigation_ids: set[str] = set()
                while pending:
                    node = pending.pop()
                    navigation_ids.add(str(node["id"]))
                    pending.extend(node.get("children", []))
                if str(category) not in navigation_ids:
                    raise ValueError(
                        f"{card_id}: unknown category {category!r} for {guide_id}"
                    )
            if card_type == "multi-guide":
                if guide_id in grouped_guide_ids:
                    raise ValueError(f"{guide_id}: guide appears in multiple multi-guide cards")
                grouped_guide_ids.add(guide_id)
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
