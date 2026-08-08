#!/usr/bin/env python3
"""Review Inscription finished-output prices with Evidence Pricing."""

from __future__ import annotations

import argparse
import importlib.util
import json
import re
import sys
from collections import Counter
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SHARED_REVIEW_PATH = ROOT / "scripts" / "review-ah-blacksmithing-prices.py"
EVIDENCE_PATH = ROOT / "data" / "ah-inscription-price-evidence.json"
MATERIAL_EVIDENCE_PATH = ROOT / "data" / "ah-profession-material-price-evidence.json"
REPORT_PATH = ROOT / "docs" / "ah-inscription-pricing-review.md"
CRAFTED_PATH = ROOT / "data" / "ah-crafted-sections.json"
BASELINE_PATH = ROOT / "data" / "ah-price-baselines.json"
RECIPE_AUDIT_PATH = ROOT / "data" / "ah-crafted-recipe-audit.json"
GUIDE_FILENAME = "inscription-materials-ah-price-guide.html"
MODEL_VERSION = "inscription-evidence-pricing-v1"
PRICE_BANDS = ("quick", "target", "high")
BOOK_ITEM_ID = "45912"

FIXED_ORDER_SECTION_TITLES = {
    "Nobles cards",
    "Chaos cards",
    "Prisms cards",
    "Undeath cards",
}
CARD_SECTION_TITLES = set(FIXED_ORDER_SECTION_TITLES)
GLYPH_SECTION_TITLES = {
    "Death Knight glyphs",
    "Druid glyphs",
    "Hunter glyphs",
    "Mage glyphs",
    "Paladin glyphs",
    "Priest glyphs",
    "Rogue glyphs",
    "Shaman glyphs",
    "Warlock glyphs",
    "Warrior glyphs",
}
EXPECTED_SECTION_COUNTS = {
    "Crafted buff scrolls": 6,
    "Crafted general-use utility and BoE equipment": 3,
    **{title: 6 for title in GLYPH_SECTION_TITLES},
    **{title: 8 for title in CARD_SECTION_TITLES},
    "Completed Northrend decks": 4,
}

spec = importlib.util.spec_from_file_location("ah_shared_finished_review", SHARED_REVIEW_PATH)
if spec is None or spec.loader is None:
    raise RuntimeError("Could not load the shared finished-output review helpers")
shared = importlib.util.module_from_spec(spec)
spec.loader.exec_module(shared)

shared.EVIDENCE_PATH = EVIDENCE_PATH
shared.REPORT_PATH = REPORT_PATH
shared.GUIDE_FILENAME = GUIDE_FILENAME
shared.RECIPE_AUDIT_PATH = RECIPE_AUDIT_PATH
shared.MODEL_VERSION = MODEL_VERSION
shared.FIXED_ORDER_SECTION_TITLES = FIXED_ORDER_SECTION_TITLES

SALE_GATE_BY_ITEM_ID: dict[int, str] = {}


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def validate_book_baseline(baseline: dict) -> None:
    book = baseline["items"][BOOK_ITEM_ID]
    if tuple(int(book[band]) for band in PRICE_BANDS) != (125_000, 250_000, 600_000):
        raise ValueError("Book of Glyph Mastery user-set band changed")
    reason = book.get("reason", "")
    if (
        book.get("source_type") != "realized-sales-history"
        or book.get("confidence") != "low"
        or "2026-08-03" not in reason
        or "150g quick, 300g target, 700g high" not in reason
        or "may be updated if later evidence differs" not in reason
    ):
        raise ValueError("Book of Glyph Mastery provenance or original baseline changed")


def preserved_item_ids(config: dict) -> set[str]:
    material = load(MATERIAL_EVIDENCE_PATH)
    crafted_ids = {
        str(int(shared.merged_item(config, key)["item_id"]))
        for section in config["guides"][GUIDE_FILENAME]["sections"]
        for key in section["items"]
    }
    material_ids = set(material["items"]) & crafted_ids
    if material_ids != {"43145", "43146"}:
        raise ValueError(f"Inscription preserved material scope drifted: {sorted(material_ids)}")
    return material_ids


def market_view(section: str) -> str:
    if section == "Crafted buff scrolls":
        return "scrolls"
    if section == "Crafted general-use utility and BoE equipment":
        return "utility-boe"
    if section in GLYPH_SECTION_TITLES:
        return "glyphs"
    if section in CARD_SECTION_TITLES:
        return "cards"
    if section == "Completed Northrend decks":
        return "decks"
    raise ValueError(f"Unexpected Inscription finished-output section: {section}")


def market_role(item: dict, view: str) -> str:
    detail = item.get("detail", "").casefold()
    if view == "glyphs":
        return "class glyph effect"
    if view == "scrolls":
        return "raid-wide Stamina substitute" if "raid-buff substitute" in detail else "single-target stat buff"
    if view == "utility-boe":
        return "slow BoE caster off-hand" if "off-hand" in detail else "Hunter pet-rename utility"
    if view == "cards":
        return "exact missing-rank deck component"
    if view == "decks":
        return "completed quest-starting eight-card deck"
    raise ValueError(view)


def entries(config: dict) -> list[dict]:
    excluded = preserved_item_ids(config)
    result = []
    seen = set()
    for section in config["guides"][GUIDE_FILENAME]["sections"]:
        title = section["title"]
        for key in section["items"]:
            item = dict(shared.merged_item(config, key))
            if str(int(item["item_id"])) in excluded:
                continue
            if key in seen:
                raise ValueError(f"Duplicate Inscription output: {key}")
            seen.add(key)
            if item.get("profession") != "Inscription":
                raise ValueError(f"Non-Inscription output in Inscription catalog: {key}")
            view = market_view(title)
            item_id = int(item["item_id"])
            sale_gate = "stackable" if view == "scrolls" else "one-at-a-time"
            SALE_GATE_BY_ITEM_ID[item_id] = sale_gate
            result.append(
                {
                    "key": key,
                    "section": title,
                    "view": view,
                    "sale_gate": sale_gate,
                    "market_role": market_role(item, view),
                    "item": item,
                }
            )
    counts = Counter(row["section"] for row in result)
    if len(result) != 105 or counts != Counter(EXPECTED_SECTION_COUNTS):
        raise ValueError(f"Inscription inventory drifted: {len(result)} rows, {dict(counts)}")
    view_counts = Counter(row["view"] for row in result)
    expected_views = {"glyphs": 60, "cards": 32, "scrolls": 6, "decks": 4, "utility-boe": 3}
    if view_counts != expected_views:
        raise ValueError(f"Inscription market views drifted: {dict(view_counts)}")
    return result


def cohort_key(row: dict) -> str:
    if row["view"] in {"glyphs", "cards"}:
        return row["section"]
    if row["view"] == "utility-boe":
        return f"{row['section']} | {row['market_role']}"
    return row["section"]


shared.entries = entries
shared.cohort_key = cohort_key

original_load_sales = shared.load_sales


def load_sales(item_ids: set[int]) -> tuple[dict[int, dict], dict]:
    sales, source = original_load_sales(item_ids)
    for item_id, record in sales.items():
        common_gate = (
            record["completed_buyouts"] >= 4
            and record["distinct_buyers"] >= 2
            and record["distinct_days"] >= 2
            and (record["largest_buyer_unit_share"] or 0) <= 0.50
        )
        if SALE_GATE_BY_ITEM_ID[item_id] == "stackable":
            common_gate = common_gate and record["units"] >= 12
        record["gate_type"] = SALE_GATE_BY_ITEM_ID[item_id]
        record["evidence_gate"] = "medium" if common_gate else "low"
        record["coverage"] = "medium" if common_gate else "sparse-or-concentrated"
    return sales, source


shared.load_sales = load_sales


def apply_inscription_diagnostics(evidence: dict) -> dict:
    records = list(evidence["items"].values())
    for record in records:
        proposal = record["proposal"]
        band = proposal["proposed_band"]
        floor = record["reagent_floor"]
        if record["view"] == "cards":
            record["recipe_diagnostic_kind"] = "random-roll-cost"
            proposal["bands_below_random_roll_cost"] = [
                name for name in PRICE_BANDS if band[name] < floor[name]
            ]
            proposal["below_reagent_floor_bands"] = []
        elif record["view"] == "decks":
            record["recipe_diagnostic_kind"] = "eight-card-opportunity-cost"
            proposal.pop("bands_below_random_roll_cost", None)
            proposal["below_reagent_floor_bands"] = [
                name for name in PRICE_BANDS if band[name] < floor[name]
            ]
        else:
            record["recipe_diagnostic_kind"] = "exact-recipe-cost"
            proposal.pop("bands_below_random_roll_cost", None)
            proposal["below_reagent_floor_bands"] = [
                name for name in PRICE_BANDS if band[name] < floor[name]
            ]
    evidence["summary"]["proposals_below_reagent_floor"] = sum(
        bool(record["proposal"]["below_reagent_floor_bands"])
        for record in records
    )
    evidence["summary"]["exact_cards_below_random_roll_cost"] = sum(
        bool(record["proposal"].get("bands_below_random_roll_cost"))
        for record in records
    )
    return evidence


def build_evidence() -> dict:
    evidence = shared.build_evidence()
    config = load(CRAFTED_PATH)
    rows = entries(config)
    row_by_key = {row["key"]: row for row in rows}
    recipe_audit = load(RECIPE_AUDIT_PATH)["recipes"]
    records = list(evidence["items"].values())
    for cohort in evidence["cohorts"].values():
        cohort["anchor_source"] = cohort["anchor_source"].replace(
            "Blacksmithing", "Inscription finished-output"
        )
    for record in records:
        row = row_by_key[record["canonical_key"]]
        record["view"] = row["view"]
        record["market_role"] = row["market_role"]
        record["sale_gate_type"] = row["sale_gate"]
        record["pricing_unit"] = {
            "glyphs": "per finished glyph",
            "scrolls": "per finished scroll",
            "utility-boe": "per finished item",
            "cards": "per exact named card",
            "decks": "per completed eight-card deck",
        }[row["view"]]
        record["recipe"]["pricing_rule"] = recipe_audit[record["canonical_key"]]["pricing_rule"]
        record["proposal"]["reason"] = (
            "Reviewed Inscription Evidence Pricing band. Qualified completed sales set "
            "value when available; sparse sales are shrunk toward a fixed Hellscream "
            "comparable-cohort estimate. External asks set relative rank only and active "
            "Hellscream listings are excluded. Exact recipe or opportunity cost remains "
            "a separate craftability diagnostic; named Darkmoon cards use random-roll "
            "cost rather than a guaranteed exact-card floor."
        )
    evidence["scope"] = (
        "The 105 previously unreviewed Inscription outputs: 60 glyphs, six buff scrolls, "
        "three utility or BoE items, 32 exact random Darkmoon cards, and four completed decks"
    )
    evidence["rules"] = {
        "active_hellscream_listing_prices_used": False,
        "external_gold_values_copied": False,
        "external_role": "Gold-normalized within-comparable-cohort relative rank only.",
        "gold_scale": "Fixed frozen Hellscream cohort anchors or qualified completed sales.",
        "recipe_floor_role": "Exact audited 3.3.5 recipe cost is a separate craftability diagnostic and does not automatically set market value.",
        "random_card_rule": "Darkmoon Card of the North creates one random card among 32 possible named outcomes; its input cost is a per-roll diagnostic, never a guaranteed exact-card floor.",
        "completed_deck_rule": "Each completed deck consumes one of every rank in its eight-card set; saved card opportunity cost remains separate from deck sale value.",
        "book_baseline_rule": "Book of Glyph Mastery stays at the user-estimated 2026-08-03 band of 12g 50s / 25g / 60g with the original 150g / 300g / 700g baseline recorded.",
        "sparse_sale_rule": "Low-confidence completed sales receive 25% weight, or 50% when they span at least two buyers and two UTC days; the balance remains the reviewed cohort fallback.",
        "stackable_medium_gate": "At least 12 units across four completed buyouts, two distinct buyers, and two distinct UTC days, with largest-buyer unit share at most 0.50.",
        "one_at_a_time_medium_gate": "At least four completed buyouts, two distinct buyers, and two distinct UTC days, with largest-buyer unit share at most 0.50.",
        "preserved_scope": "Armor Vellum III and Weapon Vellum III retain their completed Phase 1B evidence and are excluded from this batch.",
    }
    evidence["summary"] = {
        "items_reviewed": len(records),
        "view_counts": dict(sorted(Counter(record["view"] for record in records).items())),
        "section_counts": dict(Counter(record["section"] for record in records)),
        "bands_changed": sum(record["before_band"] != record["proposal"]["proposed_band"] for record in records),
        "completed_sale_items": sum(record["local_completed_sales"] is not None for record in records),
        "medium_confidence_sale_items": sum(record["proposal"]["decision"] == "direct-completed-sales" for record in records),
        "items_seen_on_three_realms": sum(record["external_relative_review"]["realm_count"] == 3 for record in records),
        "items_seen_on_two_realms": sum(record["external_relative_review"]["realm_count"] == 2 for record in records),
        "items_seen_on_one_realm": sum(record["external_relative_review"]["realm_count"] == 1 for record in records),
        "items_seen_on_no_realms": sum(record["external_relative_review"]["realm_count"] == 0 for record in records),
        "target_changes_over_fifty_percent": sum(record["proposal"]["requires_large_change_review"] for record in records),
        "proposals_below_reagent_floor": 0,
        "exact_cards_below_random_roll_cost": 0,
        "decision_counts": dict(sorted(Counter(record["proposal"]["decision"] for record in records).items())),
        "external_gold_values_copied": False,
    }
    return apply_inscription_diagnostics(evidence)


def review_saved_evidence(evidence: dict) -> dict:
    evidence = shared.review_saved_evidence(evidence)
    records = list(evidence["items"].values())
    for record in records:
        proposal = record["proposal"]
        sales = record["local_completed_sales"]
        if (
            proposal["requires_large_change_review"]
            and sales
            and sales.get("evidence_gate") == "medium"
        ):
            candidate = dict(proposal["model_proposed_band_before_manual_review"])
            proposal["proposed_band"] = candidate
            proposal["decision"] = "direct-completed-sales"
            proposal["source_type"] = "realized-sales-history"
            proposal["confidence"] = "medium"
            proposal["reviewer_decision"] = "accept"
            proposal["reviewer_note"] = (
                "Accepted after manual large-change review because the qualified local "
                "completed-sale gate passed; external coverage is not needed to copy gold."
            )
            before = record["before_band"]
            change = candidate["target"] / before["target"] - 1.0
            proposal["target_change_copper"] = candidate["target"] - before["target"]
            proposal["target_change_percent"] = round(change * 100, 4)
    evidence["summary"]["bands_changed"] = sum(
        record["before_band"] != record["proposal"]["proposed_band"] for record in records
    )
    evidence["summary"]["decision_counts"] = dict(
        sorted(Counter(record["proposal"]["decision"] for record in records).items())
    )
    evidence["summary"]["medium_confidence_sale_items"] = sum(
        record["proposal"]["decision"] == "direct-completed-sales" for record in records
    )
    return apply_inscription_diagnostics(evidence)


def format_money(copper: int) -> str:
    return shared.format_money(copper)


def format_band(band: dict) -> str:
    return shared.format_band(band)


def render_report(evidence: dict) -> str:
    summary = evidence["summary"]
    lines = [
        "# Inscription Evidence Pricing Review",
        "",
        f"- Reviewed: `{evidence['refreshed']}`",
        f"- Scope: `{evidence['scope']}`",
        f"- Finished outputs: `{summary['items_reviewed']}`",
        f"- Price bands changed: `{summary['bands_changed']}`",
        f"- Items with completed-sale evidence: `{summary['completed_sale_items']}`",
        f"- Items seen on all three comparison realms: `{summary['items_seen_on_three_realms']}`",
        f"- Manually reviewed Target changes over 50%: `{summary['target_changes_over_fifty_percent']}`",
        f"- Deterministic outputs below at least one exact recipe/opportunity-cost band: `{summary['proposals_below_reagent_floor']}`",
        f"- Exact cards below at least one random-roll-cost band: `{summary['exact_cards_below_random_roll_cost']}`",
        "- Preserved companion review: `Armor Vellum III and Weapon Vellum III`",
        "- Preserved Book of Glyph Mastery Target: `25g`",
        "- Active Hellscream listing prices used: `no`",
        "- External gold copied into Hellscream prices: `no`",
        "- Publication status: `local only — not published`",
        "",
        "## Decision",
        "",
        "Glyphs, scrolls, utility items, BoE off-hands, exact cards, and completed decks use the same Evidence Pricing safeguards as the other profession markets. Qualified Hellscream completed buyouts may set market value; sparse sales are shrunk toward fixed comparable-cohort estimates. Current Hellscream listings are excluded. External observations set relative rank only, while frozen Hellscream cohort anchors set the gold scale.",
        "",
        "Darkmoon Card of the North creates one random named card. Its full input cost is a per-roll diagnostic and is not a guaranteed floor for any exact card. Completed decks instead use the current eight exact cards as their opportunity-cost diagnostic. The Book of Glyph Mastery remains a separate recipe-drop baseline at the user-set 25g Target.",
        "",
        "## Item decisions",
        "",
        "| Section | Item | Role | Basis | Old Q / T / H | Recipe / roll diagnostic Q / T / H | Proposed Q / T / H | Target change | Local sales | External coverage | Decision | Confidence | Review |",
        "|---|---|---|---|---:|---:|---:|---:|---:|---:|---|---|---|",
    ]
    records = sorted(
        evidence["items"].values(),
        key=lambda record: (record["section"], -record["proposal"]["proposed_band"]["target"], record["name"]),
    )
    for record in records:
        sales = record["local_completed_sales"]
        sales_text = (
            f"{sales['completed_buyouts']} buyouts / {sales['units']} units / {sales['distinct_buyers']} buyers / {sales['distinct_days']} days"
            if sales
            else "none"
        )
        coverage = record["external_relative_review"]
        proposal = record["proposal"]
        lines.append(
            "| "
            + " | ".join(
                [
                    record["section"],
                    record["name"],
                    record["market_role"],
                    record["pricing_unit"],
                    format_band(record["before_band"]),
                    format_band(record["reagent_floor"]),
                    format_band(proposal["proposed_band"]),
                    f"{proposal['target_change_percent']:+.2f}%",
                    sales_text,
                    f"{coverage['realm_count']} realms / {coverage['faction_snapshots_present']} factions",
                    proposal["decision"],
                    proposal["confidence"],
                    proposal["reviewer_decision"],
                ]
            )
            + " |"
        )
    lines.extend(["", "## Manual review of Target changes over 50%", ""])
    large = [record for record in records if record["proposal"]["requires_large_change_review"]]
    if not large:
        lines.append("No Target changes exceeded 50%.")
    for record in large:
        proposal = record["proposal"]
        candidate = proposal["model_proposed_band_before_manual_review"]
        lines.append(
            f"- **{record['name']}**: model candidate {format_money(record['before_band']['target'])} → "
            f"{format_money(candidate['target'])} ({proposal['model_target_change_percent']:+.2f}%); "
            f"final {format_money(proposal['proposed_band']['target'])}. Decision: "
            f"`{proposal['reviewer_decision']}`. {proposal['reviewer_note']}"
        )
    lines.extend(
        [
            "",
            "## Evidence limits",
            "",
            "- Armor Vellum III, Weapon Vellum III, and the Book of Glyph Mastery baseline were preserved rather than refetched or rebuilt.",
            "- The external source reports listings and listing history, not verified completed sales.",
            "- External observations set relative rank only; nominal external gold is not saved or copied.",
            "- Current Hellscream listings are excluded because guide-driven auctions dominate the local market.",
            "- Glyph discovery and Book of Glyph Mastery access remain supply notes rather than hidden premiums.",
            "- Random-card crafting profitability depends on the combined expected value of all 32 outcomes, not one exact card row.",
            "",
            "## Reproduction",
            "",
            "```powershell",
            "python scripts/review-ah-inscription-prices.py --check",
            "```",
            "",
            "Publishing is a separate step and is not part of this review.",
            "",
        ]
    )
    return "\n".join(lines)


def validate(evidence: dict, *, require_applied: bool) -> None:
    config = load(CRAFTED_PATH)
    baseline_doc = load(BASELINE_PATH)
    validate_book_baseline(baseline_doc)
    baseline = baseline_doc["items"]
    rows = entries(config)
    row_by_key = {row["key"]: row for row in rows}
    expected_ids = {str(int(row["item"]["item_id"])) for row in rows}
    if evidence.get("method") != "Evidence Pricing" or evidence.get("model_version") != MODEL_VERSION:
        raise ValueError("Inscription Evidence Pricing method or model is stale")
    if set(evidence.get("items", {})) != expected_ids:
        raise ValueError("Inscription evidence does not cover exactly 105 outputs")
    if evidence["rules"].get("active_hellscream_listing_prices_used") is not False:
        raise ValueError("Active Hellscream listings must not set prices")
    if evidence["rules"].get("external_gold_values_copied") is not False:
        raise ValueError("External gold must not be copied")
    for record in evidence["items"].values():
        row = row_by_key[record["canonical_key"]]
        item = row["item"]
        floor = {band: int(item["pricing_floor_copper"][band]) for band in PRICE_BANDS}
        if record["reagent_floor"] != floor:
            raise ValueError(f"{record['name']}: saved recipe diagnostic is stale")
        proposal = record["proposal"]
        band = proposal["proposed_band"]
        if not band["quick"] <= band["target"] <= band["high"]:
            raise ValueError(f"{record['name']}: invalid reviewed price band")
        if proposal["requires_large_change_review"] and proposal["reviewer_decision"] not in {"accept", "revise", "retain"}:
            raise ValueError(f"{record['name']}: large change lacks manual review")
        if record["external_relative_review"].get("used_to_set_gold_value") is not False:
            raise ValueError(f"{record['name']}: external gold leaked into proposal")
        for observation in record["source_observations"].values():
            if "median_buyout_copper" in observation or "economy_scale" in observation:
                raise ValueError(f"{record['name']}: nominal external gold was saved")
        if record["view"] == "cards":
            if record["recipe"]["pricing_rule"] != "random-darkmoon-card":
                raise ValueError(f"{record['name']}: random-card recipe rule is missing")
            if proposal["below_reagent_floor_bands"]:
                raise ValueError(f"{record['name']}: random-roll cost was treated as an exact-card floor")
        elif record["view"] == "decks" and record["recipe"]["pricing_rule"] != "complete-eight-card-deck":
            raise ValueError(f"{record['name']}: eight-card deck recipe rule is missing")
        if require_applied:
            raw = config["catalog"][record["canonical_key"]]
            current = {name: int(raw[f"{name}_copper"]) for name in PRICE_BANDS}
            if current != band:
                raise ValueError(f"{record['name']}: reviewed band is not applied")
            if raw.get("price_strategy") != "evidence-pricing-market-value":
                raise ValueError(f"{record['name']}: Evidence Pricing strategy is not applied")
            expected_ref = f"data/ah-inscription-price-evidence.json#items/{record['item_id']}"
            if raw.get("price_evidence_ref") != expected_ref:
                raise ValueError(f"{record['name']}: evidence reference is stale")
            duplicate = baseline.get(str(record["item_id"]))
            if duplicate:
                duplicate_band = {name: int(duplicate[name]) for name in PRICE_BANDS}
                if duplicate_band != band or duplicate.get("evidence_ref") != expected_ref:
                    raise ValueError(f"{record['name']}: duplicate baseline is not synchronized")


def apply_catalog(evidence: dict) -> None:
    config = load(CRAFTED_PATH)
    source = CRAFTED_PATH.read_text(encoding="utf-8")
    baseline_doc = load(BASELINE_PATH)
    validate_book_baseline(baseline_doc)
    baseline = baseline_doc["items"]
    proposals = {
        record["canonical_key"]: record["proposal"]["proposed_band"]
        for record in evidence["items"].values()
    }
    item_ids = {
        record["canonical_key"]: int(record["item_id"])
        for record in evidence["items"].values()
    }
    for key, band in proposals.items():
        updated = dict(config["catalog"][key])
        for name in PRICE_BANDS:
            updated[f"{name}_copper"] = int(band[name])
        item_id = item_ids[key]
        expected_ref = f"data/ah-inscription-price-evidence.json#items/{item_id}"
        updated["price_strategy"] = "evidence-pricing-market-value"
        updated["price_evidence_ref"] = expected_ref
        pattern = re.compile(rf'^(    "{re.escape(key)}": )\{{.*\}}(,?)$', re.MULTILINE)
        replacement = rf"\g<1>{json.dumps(updated, ensure_ascii=False, separators=(',', ':'))}\g<2>"
        source, count = pattern.subn(replacement, source, count=1)
        if count != 1:
            raise ValueError(f"Could not update canonical Inscription row: {key}")
        duplicate = baseline.get(str(item_id))
        if duplicate:
            for name in PRICE_BANDS:
                duplicate[name] = int(band[name])
            duplicate["source_type"] = evidence["items"][str(item_id)]["proposal"]["source_type"]
            duplicate["confidence"] = evidence["items"][str(item_id)]["proposal"]["confidence"]
            duplicate["reason"] = evidence["items"][str(item_id)]["proposal"]["reason"]
            duplicate["evidence_ref"] = expected_ref
    guide = config["guides"][GUIDE_FILENAME]
    reviewed_sections = {record["section"] for record in evidence["items"].values()}
    for section in guide["sections"]:
        if section["title"] not in reviewed_sections or section["title"] in FIXED_ORDER_SECTION_TITLES:
            continue
        ordered = sorted(
            section["items"],
            key=lambda key: (
                -int(proposals[key]["target"]),
                shared.merged_item(config, key)["name"].casefold(),
            ),
        )
        pattern = re.compile(
            r'(^\s*\{"title": "'
            + re.escape(section["title"])
            + r'".*?"items": )\[.*?\](\},?)$',
            re.MULTILINE,
        )
        item_array = json.dumps(ordered, ensure_ascii=False, separators=(",", ":"))
        source, count = pattern.subn(lambda match: match.group(1) + item_array + match.group(2), source, count=1)
        if count != 1:
            raise ValueError(f"Could not reorder Inscription section: {section['title']}")
    new_intro = (
        "This curated catalog covers 107 tradeable Inscription outputs: 60 level-80 glyphs, six buff scrolls, two Enchanter-only blank vellums, three utility or BoE items, 32 exact Northrend Darkmoon cards, and four completed decks. Finished-output sale bands use saved Evidence Pricing reviews, while exact 3.3.5 recipes remain separate craftability diagnostics. Darkmoon Card of the North input cost is a random-roll diagnostic rather than a guaranteed exact-card floor. Prices are per finished item."
    )
    new_note = {
        "id": "crafted-inscription-pricing-note",
        "marker": "*",
        "label": "Evidence Pricing and craft diagnostics",
        "text": "The 105 glyph, scroll, utility, BoE, exact-card, and completed-deck outputs use Evidence Pricing from qualified completed sales or fixed comparable Hellscream fallbacks; external observations set relative rank only and active Hellscream asks never set price. Armor Vellum III and Weapon Vellum III retain their reviewed material evidence. Exact recipe or card opportunity cost remains a separate craftability diagnostic, so skip deterministic outputs priced below that cost unless your inputs are cheaper. Darkmoon Card of the North creates one random named card: its input cost is per roll, not a guaranteed floor for an exact card. Completed decks use all eight exact cards. Glyph discovery and Book of Glyph Mastery access are supply constraints, not hidden premiums."
    }
    old_intro = guide["intro_description"]
    intro_pattern = re.compile(
        r'(^      "intro_description": )'
        + re.escape(json.dumps(old_intro, ensure_ascii=False))
        + r',$',
        re.MULTILINE,
    )
    source, count = intro_pattern.subn(
        lambda match: match.group(1) + json.dumps(new_intro, ensure_ascii=False) + ",",
        source,
        count=1,
    )
    if count != 1:
        raise ValueError("Could not update the Inscription crafted intro")
    note_pattern = re.compile(
        r'^      "shared_note": \{"id":"crafted-inscription-pricing-note".*\},$',
        re.MULTILINE,
    )
    note_json = json.dumps(new_note, ensure_ascii=False, separators=(",", ":"))
    source, count = note_pattern.subn(f'      "shared_note": {note_json},', source, count=1)
    if count != 1:
        raise ValueError("Could not update the Inscription shared Evidence Pricing note")
    CRAFTED_PATH.write_text(source, encoding="utf-8", newline="\n")
    BASELINE_PATH.write_text(
        json.dumps(baseline_doc, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def refresh_dependency_diagnostics(evidence: dict) -> dict:
    config = load(CRAFTED_PATH)
    recipe_audit = load(RECIPE_AUDIT_PATH)["recipes"]
    rows = {row["key"]: row for row in entries(config)}
    for record in evidence["items"].values():
        floor = rows[record["canonical_key"]]["item"]["pricing_floor_copper"]
        record["reagent_floor"] = {band: int(floor[band]) for band in PRICE_BANDS}
        record["recipe"]["pricing_rule"] = recipe_audit[record["canonical_key"]]["pricing_rule"]
    evidence["dependency_diagnostics_refreshed"] = date.today().isoformat()
    return apply_inscription_diagnostics(evidence)


def write_outputs(evidence: dict) -> None:
    EVIDENCE_PATH.write_text(
        json.dumps(evidence, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    REPORT_PATH.write_text(render_report(evidence), encoding="utf-8", newline="\n")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--inventory", action="store_true")
    group.add_argument("--refresh", action="store_true")
    group.add_argument("--review", action="store_true")
    group.add_argument("--refresh-dependencies", action="store_true")
    group.add_argument("--apply", action="store_true")
    group.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if args.inventory:
        rows = entries(load(CRAFTED_PATH))
        validate_book_baseline(load(BASELINE_PATH))
        print(json.dumps(Counter(row["section"] for row in rows), indent=2))
        print(json.dumps(Counter(row["view"] for row in rows), indent=2))
        print(json.dumps(Counter(cohort_key(row) for row in rows), indent=2))
        print(f"items {len(rows)}")
        return 0
    if args.refresh:
        evidence = build_evidence()
        validate(evidence, require_applied=False)
        write_outputs(evidence)
        print(json.dumps(evidence["summary"], indent=2))
        return 0
    if args.review:
        evidence = review_saved_evidence(load(EVIDENCE_PATH))
        validate(evidence, require_applied=False)
        write_outputs(evidence)
        print(json.dumps(evidence["summary"], indent=2))
        return 0
    if args.refresh_dependencies:
        evidence = refresh_dependency_diagnostics(load(EVIDENCE_PATH))
        validate(evidence, require_applied=True)
        write_outputs(evidence)
        print("Refreshed Inscription recipe and random-roll diagnostics without changing prices.")
        return 0
    evidence = load(EVIDENCE_PATH)
    if args.apply:
        validate(evidence, require_applied=False)
        apply_catalog(evidence)
        validate(evidence, require_applied=True)
        print(f"Applied {len(evidence['items'])} reviewed Inscription price bands.")
        return 0
    validate(evidence, require_applied=True)
    if REPORT_PATH.read_text(encoding="utf-8") != render_report(evidence):
        print("Inscription Evidence Pricing report is stale.", file=sys.stderr)
        return 1
    print("Inscription Evidence Pricing review is current.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
