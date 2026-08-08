#!/usr/bin/env python3
"""Review the remaining Alchemy finished-output prices with Evidence Pricing."""

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
EVIDENCE_PATH = ROOT / "data" / "ah-alchemy-finished-price-evidence.json"
POTION_EVIDENCE_PATH = ROOT / "data" / "ah-alchemy-potion-price-evidence.json"
MATERIAL_EVIDENCE_PATH = ROOT / "data" / "ah-profession-material-price-evidence.json"
REPORT_PATH = ROOT / "docs" / "ah-alchemy-finished-pricing-review.md"
CRAFTED_PATH = ROOT / "data" / "ah-crafted-sections.json"
BASELINE_PATH = ROOT / "data" / "ah-price-baselines.json"
RECIPE_AUDIT_PATH = ROOT / "data" / "ah-crafted-recipe-audit.json"
GUIDE_FILENAME = "alchemy-materials-ah-price-guide.html"
MODEL_VERSION = "alchemy-finished-evidence-pricing-v1"
PRICE_BANDS = ("quick", "target", "high")

EXPECTED_SECTION_COUNTS = {
    "Crafted Wrath flasks": 6,
    "Crafted Wrath elixirs": 17,
    "Crafted Wrath transmutes": 1,
    "Crafted Outland flasks": 6,
    "Crafted Outland elixirs": 19,
    "Crafted Outland protection cauldrons": 5,
    "Crafted Classic flasks": 4,
    "Crafted Classic endgame elixirs": 18,
    "Crafted Classic leveling elixirs": 22,
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
shared.FIXED_ORDER_SECTION_TITLES = set()

SALE_GATE_BY_ITEM_ID: dict[int, str] = {}


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def preserved_item_ids(config: dict) -> set[str]:
    potion = load(POTION_EVIDENCE_PATH)
    material = load(MATERIAL_EVIDENCE_PATH)
    potion_ids = set(potion["items"])
    crafted_ids = {
        str(int(shared.merged_item(config, key)["item_id"]))
        for section in config["guides"][GUIDE_FILENAME]["sections"]
        for key in section["items"]
    }
    material_ids = set(material["items"]) & crafted_ids
    if len(potion_ids) != 84:
        raise ValueError(f"Alchemy potion evidence drifted: {len(potion_ids)} items")
    if len(material_ids) != 24:
        raise ValueError(f"Alchemy material evidence drifted: {len(material_ids)} items")
    overlap = potion_ids & material_ids
    if overlap:
        raise ValueError(f"Alchemy preserved evidence scopes overlap: {sorted(overlap)}")
    return potion_ids | material_ids


def market_view(section: str) -> str:
    if "flasks" in section:
        return "flasks"
    if "elixirs" in section:
        return "elixirs"
    if "cauldrons" in section:
        return "cauldrons"
    if "transmutes" in section:
        return "transmutes"
    raise ValueError(f"Unexpected Alchemy finished-output section: {section}")


def elixir_slot(item: dict) -> str:
    note = item.get("row_note", "").casefold()
    if "battle elixir" in note:
        return "Battle"
    if "guardian elixir" in note:
        return "Guardian"
    return "utility"


def market_role(item: dict) -> str:
    text = f"{item['name']} {item.get('detail', '')} {item.get('row_note', '')}".casefold()
    if any(token in text for token in ("detect", "camouflage", "water walking", "water breathing", "dream vision", "catseye")):
        return "utility and detection"
    if any(token in text for token in ("resistance", "protection", "armor", "defense", "fortitude", "health", "damage taken", "stoneblood", "titans")):
        return "survival and resistance"
    if any(token in text for token in ("mana", "spirit", "intellect", "wisdom", "healing", "spell power", "spellpower", "mageblood", "pure mojo")):
        return "caster, healer, or regeneration"
    if any(token in text for token in ("attack power", "strength", "agility", "critical", "haste", "expertise", "accuracy", "armor penetration", "rage", "demonslaying", "firepower", "frost power", "shadow power")):
        return "physical or magical offense"
    return "general stat or niche effect"


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
                raise ValueError(f"Duplicate remaining Alchemy output: {key}")
            seen.add(key)
            if item.get("profession") != "Alchemy":
                raise ValueError(f"Non-Alchemy output in Alchemy catalog: {key}")
            view = market_view(title)
            item_id = int(item["item_id"])
            sale_gate = "one-at-a-time" if view == "cauldrons" else "stackable"
            SALE_GATE_BY_ITEM_ID[item_id] = sale_gate
            result.append(
                {
                    "key": key,
                    "section": title,
                    "view": view,
                    "sale_gate": sale_gate,
                    "market_role": market_role(item),
                    "elixir_slot": elixir_slot(item) if view == "elixirs" else None,
                    "item": item,
                }
            )
    counts = Counter(row["section"] for row in result)
    if len(result) != 98 or dict(counts) != EXPECTED_SECTION_COUNTS:
        raise ValueError(f"Alchemy remaining inventory drifted: {len(result)} rows, {dict(counts)}")
    view_counts = Counter(row["view"] for row in result)
    if view_counts != {"elixirs": 76, "flasks": 16, "cauldrons": 5, "transmutes": 1}:
        raise ValueError(f"Alchemy remaining market views drifted: {dict(view_counts)}")
    return result


def cohort_key(row: dict) -> str:
    if row["view"] == "elixirs":
        return f"{row['section']} | {row['elixir_slot']}"
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


def build_evidence() -> dict:
    evidence = shared.build_evidence()
    config = load(CRAFTED_PATH)
    rows = entries(config)
    row_by_key = {row["key"]: row for row in rows}
    records = list(evidence["items"].values())
    for cohort in evidence["cohorts"].values():
        cohort["anchor_source"] = cohort["anchor_source"].replace(
            "Blacksmithing", "Alchemy finished-output"
        )
    for record in records:
        row = row_by_key[record["canonical_key"]]
        record["view"] = row["view"]
        record["market_role"] = row["market_role"]
        record["elixir_slot"] = row["elixir_slot"]
        record["sale_gate_type"] = row["sale_gate"]
        record["pricing_unit"] = (
            "per sealed 25-use cauldron"
            if row["view"] == "cauldrons"
            else "per finished item"
        )
        record["proposal"]["reason"] = (
            "Reviewed Alchemy finished-output Evidence Pricing band. Qualified completed "
            "sales set value when available; sparse sales are shrunk toward a fixed "
            "Hellscream comparable-cohort estimate. External asks set relative rank only "
            "and active Hellscream listings are excluded. Exact recipe cost remains a "
            "separate craftability diagnostic."
        )
    evidence["scope"] = (
        "The 98 previously unreviewed Alchemy finished outputs: 16 flasks, 76 elixirs, "
        "five sealed protection cauldrons, and Eternal Might"
    )
    evidence["rules"] = {
        "active_hellscream_listing_prices_used": False,
        "external_gold_values_copied": False,
        "external_role": "Gold-normalized within-comparable-cohort relative rank only.",
        "gold_scale": "Fixed frozen Hellscream cohort anchors or qualified completed sales.",
        "recipe_floor_role": "Exact audited 3.3.5 recipe cost is a separate craftability diagnostic and does not automatically set market value.",
        "specialization_proc_role": "Alchemy specialization procs are excluded from guaranteed recipe output and do not lower the saved floor.",
        "cauldron_basis": "Each cauldron is valued as one sealed tradeable 25-use item, never as 25 separately auctionable potions.",
        "sparse_sale_rule": "Low-confidence completed sales receive 25% weight, or 50% when they span at least two buyers and two UTC days; the balance remains the reviewed cohort fallback.",
        "stackable_medium_gate": "At least 12 units across four completed buyouts, two distinct buyers, and two distinct UTC days, with largest-buyer unit share at most 0.50.",
        "one_at_a_time_medium_gate": "At least four completed buyouts, two distinct buyers, and two distinct UTC days, with largest-buyer unit share at most 0.50.",
        "preserved_scopes": "The 84-potion and 24 Alchemy material/intermediate evidence records are excluded from this batch and remain unchanged.",
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
        "proposals_below_reagent_floor": sum(bool(record["proposal"]["below_reagent_floor_bands"]) for record in records),
        "decision_counts": dict(sorted(Counter(record["proposal"]["decision"] for record in records).items())),
        "external_gold_values_copied": False,
    }
    return evidence


def format_money(copper: int) -> str:
    return shared.format_money(copper)


def format_band(band: dict) -> str:
    return shared.format_band(band)


def render_report(evidence: dict) -> str:
    summary = evidence["summary"]
    lines = [
        "# Alchemy Finished-Output Evidence Pricing Review",
        "",
        f"- Reviewed: `{evidence['refreshed']}`",
        f"- Scope: `{evidence['scope']}`",
        f"- Finished outputs: `{summary['items_reviewed']}`",
        f"- Price bands changed: `{summary['bands_changed']}`",
        f"- Items with completed-sale evidence: `{summary['completed_sale_items']}`",
        f"- Items seen on all three comparison realms: `{summary['items_seen_on_three_realms']}`",
        f"- Manually reviewed Target changes over 50%: `{summary['target_changes_over_fifty_percent']}`",
        f"- Market proposals below at least one exact recipe-floor band: `{summary['proposals_below_reagent_floor']}`",
        "- Preserved companion reviews: `84 potions and 24 materials/intermediates`",
        "- Active Hellscream listing prices used: `no`",
        "- External gold copied into Hellscream prices: `no`",
        "- Publication status: `local only — not published`",
        "",
        "## Decision",
        "",
        "The remaining flasks, elixirs, cauldrons, and Eternal Might use the same Evidence Pricing safeguards as the other profession markets. Qualified Hellscream completed buyouts may set market value; sparse sales are shrunk toward a fixed comparable-cohort estimate. Current Hellscream listings are excluded. External observations set relative rank only, while frozen Hellscream cohort anchors set the gold scale.",
        "",
        "Every output keeps its exact audited 3.3.5 recipe floor as a separate craftability diagnostic. Alchemy specialization procs are excluded from guaranteed output. Cauldrons are valued as sealed 25-use items, not as individual protection potions.",
        "",
        "## Item decisions",
        "",
        "| Section | Item | Role | Slot / basis | Old Q / T / H | Recipe floor Q / T / H | Proposed Q / T / H | Target change | Local sales | External coverage | Decision | Confidence | Review |",
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
        slot_basis = record["elixir_slot"] or record["pricing_unit"]
        lines.append(
            "| "
            + " | ".join(
                [
                    record["section"],
                    record["name"],
                    record["market_role"],
                    slot_basis,
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
            "- The 84-potion and 24 material/intermediate companion reviews were preserved rather than refetched or rebuilt.",
            "- The external source reports listings and listing history, not verified completed sales.",
            "- External observations set relative rank only; nominal external gold is not saved or copied.",
            "- Current Hellscream listings are excluded because guide-driven auctions dominate the local market.",
            "- Recipe discovery, reputation access, cooldowns, and specialization remain notes rather than hidden premiums.",
            "",
            "## Reproduction",
            "",
            "```powershell",
            "python scripts/review-ah-alchemy-finished-prices.py --check",
            "```",
            "",
            "Publishing is a separate step and is not part of this review.",
            "",
        ]
    )
    return "\n".join(lines)


def validate(evidence: dict, *, require_applied: bool) -> None:
    config = load(CRAFTED_PATH)
    baseline = load(BASELINE_PATH)["items"]
    rows = entries(config)
    row_by_key = {row["key"]: row for row in rows}
    expected_ids = {str(int(row["item"]["item_id"])) for row in rows}
    if evidence.get("method") != "Evidence Pricing" or evidence.get("model_version") != MODEL_VERSION:
        raise ValueError("Alchemy finished-output Evidence Pricing method or model is stale")
    if set(evidence.get("items", {})) != expected_ids:
        raise ValueError("Alchemy finished-output evidence does not cover exactly 98 outputs")
    if evidence["rules"].get("active_hellscream_listing_prices_used") is not False:
        raise ValueError("Active Hellscream listings must not set prices")
    if evidence["rules"].get("external_gold_values_copied") is not False:
        raise ValueError("External gold must not be copied")
    for record in evidence["items"].values():
        row = row_by_key[record["canonical_key"]]
        item = row["item"]
        floor = {band: int(item["pricing_floor_copper"][band]) for band in PRICE_BANDS}
        if record["reagent_floor"] != floor:
            raise ValueError(f"{record['name']}: saved recipe floor is stale")
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
        if require_applied:
            raw = config["catalog"][record["canonical_key"]]
            current = {name: int(raw[f"{name}_copper"]) for name in PRICE_BANDS}
            if current != band:
                raise ValueError(f"{record['name']}: reviewed band is not applied")
            if raw.get("price_strategy") != "evidence-pricing-market-value":
                raise ValueError(f"{record['name']}: Evidence Pricing strategy is not applied")
            expected_ref = f"data/ah-alchemy-finished-price-evidence.json#items/{record['item_id']}"
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
        expected_ref = f"data/ah-alchemy-finished-price-evidence.json#items/{item_id}"
        updated["price_strategy"] = "evidence-pricing-market-value"
        updated["price_evidence_ref"] = expected_ref
        pattern = re.compile(rf'^(    "{re.escape(key)}": )\{{.*\}}(,?)$', re.MULTILINE)
        replacement = rf"\g<1>{json.dumps(updated, ensure_ascii=False, separators=(',', ':'))}\g<2>"
        source, count = pattern.subn(replacement, source, count=1)
        if count != 1:
            raise ValueError(f"Could not update canonical Alchemy row: {key}")
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
        if section["title"] not in reviewed_sections:
            continue
        ordered = sorted(
            section["items"],
            key=lambda key: (
                -int(
                    proposals.get(
                        key,
                        {"target": shared.merged_item(config, key)["target_copper"]},
                    )["target"]
                ),
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
            raise ValueError(f"Could not reorder Alchemy section: {section['title']}")
    new_intro = (
        "This expanded catalog covers 206 tradeable Alchemy outputs across Wrath, Outland, and Classic: flasks, elixirs, potions, protection consumables, oils, cauldrons, intermediates, and selected transmutes. Every crafted output now uses a saved Evidence Pricing or reviewed material-market estimate, while exact 3.3.5 recipes and frozen non-circular inputs remain separate craftability diagnostics. Prices are per finished item unless a displayed stack says otherwise."
    )
    new_note = {
        "id": "crafted-alchemy-pricing-note",
        "marker": "*",
        "label": "Evidence Pricing and craft diagnostics",
        "text": "All 206 crafted Alchemy outputs use saved market reviews: the dedicated 84-potion snapshot, the 24 reviewed material/intermediate records, and the companion 98-output flask, elixir, cauldron, and Eternal Might review. Qualified completed sales may set value; sparse sales shrink toward fixed comparable Hellscream anchors, while external observations set relative rank only and active Hellscream asks never set price. Exact 3.3.5 recipe cost remains a separate craftability diagnostic, so skip outputs priced below that floor unless your inputs are cheaper. Specialization procs are excluded from guaranteed output. Cauldrons are valued as sealed 25-use items. Standard flasks occupy both elixir slots and persist through death."
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
        raise ValueError("Could not update the Alchemy crafted intro")
    note_pattern = re.compile(
        r'^      "shared_note": \{"id":"crafted-alchemy-pricing-note".*\},$',
        re.MULTILINE,
    )
    note_json = json.dumps(new_note, ensure_ascii=False, separators=(",", ":"))
    source, count = note_pattern.subn(f'      "shared_note": {note_json},', source, count=1)
    if count != 1:
        raise ValueError("Could not update the Alchemy shared Evidence Pricing note")
    CRAFTED_PATH.write_text(source, encoding="utf-8", newline="\n")
    BASELINE_PATH.write_text(
        json.dumps(baseline_doc, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def refresh_dependency_diagnostics(evidence: dict) -> dict:
    config = load(CRAFTED_PATH)
    rows = {row["key"]: row for row in entries(config)}
    for record in evidence["items"].values():
        floor = rows[record["canonical_key"]]["item"]["pricing_floor_copper"]
        record["reagent_floor"] = {band: int(floor[band]) for band in PRICE_BANDS}
        record["proposal"]["below_reagent_floor_bands"] = [
            band
            for band in PRICE_BANDS
            if record["proposal"]["proposed_band"][band] < record["reagent_floor"][band]
        ]
    evidence["summary"]["proposals_below_reagent_floor"] = sum(
        bool(record["proposal"]["below_reagent_floor_bands"])
        for record in evidence["items"].values()
    )
    evidence["dependency_diagnostics_refreshed"] = date.today().isoformat()
    return evidence


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
        evidence = shared.review_saved_evidence(load(EVIDENCE_PATH))
        validate(evidence, require_applied=False)
        write_outputs(evidence)
        print(json.dumps(evidence["summary"], indent=2))
        return 0
    if args.refresh_dependencies:
        evidence = refresh_dependency_diagnostics(load(EVIDENCE_PATH))
        validate(evidence, require_applied=True)
        write_outputs(evidence)
        print("Refreshed Alchemy finished-output recipe-floor diagnostics without changing prices.")
        return 0
    evidence = load(EVIDENCE_PATH)
    if args.apply:
        validate(evidence, require_applied=False)
        apply_catalog(evidence)
        validate(evidence, require_applied=True)
        print(f"Applied {len(evidence['items'])} reviewed Alchemy finished-output price bands.")
        return 0
    validate(evidence, require_applied=True)
    if REPORT_PATH.read_text(encoding="utf-8") != render_report(evidence):
        print("Alchemy finished-output Evidence Pricing report is stale.", file=sys.stderr)
        return 1
    print("Alchemy finished-output Evidence Pricing review is current.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
