#!/usr/bin/env python3
"""Review Jewelcrafting jewelry, component, and special-craft prices."""

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
EVIDENCE_PATH = ROOT / "data" / "ah-jewelcrafting-jewelry-price-evidence.json"
REPORT_PATH = ROOT / "docs" / "ah-jewelcrafting-jewelry-pricing-review.md"
CRAFTED_PATH = ROOT / "data" / "ah-crafted-sections.json"
BASELINE_PATH = ROOT / "data" / "ah-price-baselines.json"
GUIDE_MANIFEST_PATH = ROOT / "data" / "ah-guides.json"
GUIDE_FILENAME = "jewelcrafting-gems-ah-price-guide.html"
MODEL_VERSION = "jewelcrafting-jewelry-evidence-pricing-v1"
PRICE_BANDS = ("quick", "target", "high")

JEWELRY_SECTION_TITLES = {
    "Wrath special and random crafts",
    "Wrath BoE jewelry",
    "Outland special and random crafts",
    "Outland BoE jewelry",
    "Classic Jewelcrafting components",
    "Classic random gem conversion",
    "Classic BoE jewelry",
}
BOE_SECTION_TITLES = {
    "Wrath BoE jewelry",
    "Outland BoE jewelry",
    "Classic BoE jewelry",
}
SPECIAL_NOTE_OVERRIDES = {
    "jc-dark-jade-focusing-lens": "Projects a dark-green targeting beam; 40 charges. Cosmetic utility with narrow demand.",
    "jc-shadow-crystal-focusing-lens": "Projects a purple targeting beam; 40 charges. Cosmetic utility with narrow demand.",
    "jc-shadow-jade-focusing-lens": "Projects a purple-and-green targeting beam; 40 charges. Cosmetic utility with narrow demand.",
    "jc-delicate-copper-wire": "Early Classic jewelry intermediate; test stacks of 5 before larger batches.",
    "jc-bronze-setting": "Low-level Classic jewelry setting; test stacks of 5 before larger batches.",
    "jc-mithril-filigree": "Mid-level Classic jewelry intermediate; test stacks of 5 before larger batches.",
    "jc-thorium-setting": "High-level Classic jewelry setting; test stacks of 5 before larger batches.",
    "jc-mercurial-adamantite": "Outland jewelry intermediate; compare singles and stacks of 5 before batching.",
}

spec = importlib.util.spec_from_file_location("ah_shared_finished_review", SHARED_REVIEW_PATH)
if spec is None or spec.loader is None:
    raise RuntimeError("Could not load the shared finished-output review helpers")
shared = importlib.util.module_from_spec(spec)
spec.loader.exec_module(shared)

shared.EVIDENCE_PATH = EVIDENCE_PATH
shared.REPORT_PATH = REPORT_PATH
shared.GUIDE_FILENAME = GUIDE_FILENAME
shared.MODEL_VERSION = MODEL_VERSION
shared.FIXED_ORDER_SECTION_TITLES = set()


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def jewelry_sections(config: dict) -> list[dict]:
    sections = [
        section
        for section in config["guides"][GUIDE_FILENAME]["sections"]
        if section["title"] in JEWELRY_SECTION_TITLES
    ]
    if len(sections) != 7:
        raise ValueError(f"Jewelcrafting jewelry section inventory drifted: {len(sections)}")
    if {section["title"] for section in sections} != JEWELRY_SECTION_TITLES:
        raise ValueError("Jewelcrafting jewelry section titles drifted")
    return sections


def entries(config: dict) -> list[dict]:
    result = []
    seen_keys = set()
    seen_ids = set()
    for section in jewelry_sections(config):
        for key in section["items"]:
            if key in seen_keys:
                raise ValueError(f"Duplicate Jewelcrafting jewelry output: {key}")
            seen_keys.add(key)
            item = shared.merged_item(config, key)
            item_id = int(item["item_id"])
            if item_id in seen_ids:
                raise ValueError(f"Duplicate Jewelcrafting jewelry item ID: {item_id}")
            seen_ids.add(item_id)
            if item.get("profession") != "Jewelcrafting":
                raise ValueError(f"Non-Jewelcrafting output in jewelry inventory: {key}")
            result.append(
                {
                    "key": key,
                    "section": section["title"],
                    "view": "boe-equipment" if section["title"] in BOE_SECTION_TITLES else "components-special",
                    "item": item,
                }
            )
    counts = Counter(row["view"] for row in result)
    if len(result) != 137 or counts != {"boe-equipment": 121, "components-special": 16}:
        raise ValueError(f"Jewelcrafting jewelry inventory drifted: {len(result)} rows, {dict(counts)}")
    return result


def special_kind(item: dict) -> str:
    name = item["name"].casefold()
    detail = item.get("detail", "").casefold()
    if "focusing lens" in name:
        return "focusing-lens"
    if name in {"icy prism", "brilliant glass", "prismatic black diamond"}:
        return "sealed-random-result"
    if "component" in detail or "intermediate" in detail:
        return "tradeable-intermediate"
    if "gem" in detail or "socket cut" in detail:
        return "special-socket-gem"
    return "utility"


def cohort_key(row: dict) -> str:
    item = row["item"]
    if row["view"] == "boe-equipment":
        return f"{row['section']} | {item['quality']} | {shared.level_bucket(shared.item_level(item))}"
    kind = special_kind(item)
    if kind == "tradeable-intermediate":
        floor = int(item["pricing_floor_copper"]["target"])
        return f"{row['section']} | {kind} | {shared.floor_bucket(floor)}"
    if kind == "special-socket-gem":
        return f"{row['section']} | {kind} | {item['quality']}"
    return f"{row['section']} | {kind}"


shared.entries = entries
shared.cohort_key = cohort_key
original_load_sales = shared.load_sales


def load_sales(item_ids: set[int]) -> tuple[dict[int, dict], dict]:
    sales, source = original_load_sales(item_ids)
    config = load(CRAFTED_PATH)
    stackable_ids = {
        int(row["item"]["item_id"])
        for row in entries(config)
        if row["item"].get("stack", "1") != "1"
    }
    for item_id, record in sales.items():
        stackable = item_id in stackable_ids
        qualifies = (
            record["completed_buyouts"] >= 4
            and record["distinct_buyers"] >= 2
            and record["distinct_days"] >= 2
            and (record["largest_buyer_unit_share"] or 0) <= 0.50
            and (not stackable or record["units"] >= 12)
        )
        record["gate_type"] = "stackable-finished-item" if stackable else "single-finished-item"
        record["evidence_gate"] = "medium" if qualifies else "low"
        record["coverage"] = "medium" if qualifies else "sparse-or-concentrated"
    return sales, source


shared.load_sales = load_sales


def item_level(item: dict) -> int:
    match = re.search(r"item(?:-|\s+)level\s+(\d+)", item.get("detail", ""), re.IGNORECASE)
    return int(match.group(1)) if match else 0


shared.item_level = item_level


def proposal_source(local_sales: dict | None) -> tuple[str, str, str]:
    if local_sales and local_sales["evidence_gate"] == "medium":
        return "direct-completed-sales", "realized-sales-history", "medium"
    if local_sales:
        return (
            "sparse-completed-sales-shrunk",
            "realized-sales-history-plus-documented-fallback",
            "low",
        )
    return "cohort-rank-starter-estimate", "documented-fallback", "fallback"


def apply_review_safeguards(evidence: dict) -> dict:
    for record in evidence["items"].values():
        proposal = record["proposal"]
        before = record["before_band"]
        candidate = dict(
            proposal.get("model_proposed_band_before_manual_review", proposal["proposed_band"])
        )
        local_sales = record["local_completed_sales"]
        realms = int(record["external_relative_review"]["realm_count"])
        model_change = candidate["target"] / before["target"] - 1.0
        large = abs(model_change) > 0.50
        decision, source_type, confidence = proposal_source(local_sales)
        if local_sales and local_sales["evidence_gate"] == "medium":
            final = candidate
            review = "accept"
            reviewer_note = (
                "Accepted from qualifying completed Hellscream sales; comparison-realm "
                "coverage is not required to establish this medium-confidence local value."
            )
        elif not local_sales and realms == 0:
            final = dict(before)
            decision = "retain-reviewed-band-no-comparison-coverage"
            source_type = "frozen-pre-phase2-guide"
            confidence = "fallback"
            review = "retain"
            reviewer_note = (
                "Retained because no completed sale or comparison realm supports a new market value."
            )
        elif large and realms < 2:
            final = dict(before)
            decision = "retain-reviewed-band-insufficient-coverage"
            source_type = "frozen-pre-phase2-guide"
            confidence = "low" if local_sales else "fallback"
            review = "retain"
            reviewer_note = (
                "Retained after large-change review because sparse local sales plus zero- or "
                "one-realm comparison coverage are not enough for a Target move over 50%."
            )
        else:
            final = candidate
            review = "accept"
            reviewer_note = (
                "Accepted after reviewing the comparable BoE or like-purpose craft cohort, exact "
                "recipe diagnostic, buyer use, and completed-sale or comparison coverage. External "
                "gold remains excluded."
            )
        proposal["proposed_band"] = final
        proposal["model_proposed_band_before_manual_review"] = candidate
        proposal["decision"] = decision
        proposal["source_type"] = source_type
        proposal["confidence"] = confidence
        proposal["reviewer_decision"] = review
        proposal["reviewer_note"] = reviewer_note
        proposal["model_target_change_percent"] = round(model_change * 100, 4)
        final_change = final["target"] / before["target"] - 1.0
        proposal["target_change_copper"] = final["target"] - before["target"]
        proposal["target_change_percent"] = round(final_change * 100, 4)
        proposal["requires_large_change_review"] = large
        proposal["below_reagent_floor_bands"] = [
            band for band in PRICE_BANDS if final[band] < record["reagent_floor"][band]
        ]
    return evidence


def update_summary(evidence: dict) -> None:
    records = list(evidence["items"].values())
    evidence["summary"].update(
        {
            "bands_changed": sum(
                record["before_band"] != record["proposal"]["proposed_band"]
                for record in records
            ),
            "target_changes_over_fifty_percent": sum(
                record["proposal"]["requires_large_change_review"] for record in records
            ),
            "large_changes_accepted": sum(
                record["proposal"]["requires_large_change_review"]
                and record["proposal"]["reviewer_decision"] == "accept"
                for record in records
            ),
            "large_changes_retained": sum(
                record["proposal"]["requires_large_change_review"]
                and record["proposal"]["reviewer_decision"] == "retain"
                for record in records
            ),
            "proposals_below_reagent_floor": sum(
                bool(record["proposal"]["below_reagent_floor_bands"])
                for record in records
            ),
            "decision_counts": dict(
                sorted(Counter(record["proposal"]["decision"] for record in records).items())
            ),
        }
    )


def build_evidence() -> dict:
    evidence = apply_review_safeguards(shared.build_evidence())
    config = load(CRAFTED_PATH)
    rows = entries(config)
    row_by_key = {row["key"]: row for row in rows}
    baseline = load(BASELINE_PATH)["items"]
    records = list(evidence["items"].values())
    for cohort in evidence["cohorts"].values():
        cohort["anchor_source"] = cohort["anchor_source"].replace(
            "Blacksmithing", "Jewelcrafting jewelry"
        )
    for record in records:
        row = row_by_key[record["canonical_key"]]
        item = row["item"]
        stackable = item.get("stack", "1") != "1"
        record["view"] = row["view"]
        record["market_kind"] = "boe-equipment" if row["view"] == "boe-equipment" else special_kind(item)
        record["pricing_unit"] = "per finished item"
        record["sale_gate_type"] = "stackable-finished-item" if stackable else "single-finished-item"
        record["legacy_baseline_duplicate"] = str(record["item_id"]) in baseline
        record["proposal"]["reason"] = (
            "Reviewed Jewelcrafting jewelry and special-craft Evidence Pricing band. Qualified "
            "completed sales set value when available; sparse sales are shrunk toward a fixed "
            "comparable BoE or like-purpose craft estimate. External asks set relative rank only "
            "and active Hellscream listings are excluded. Exact recipe cost remains a separate "
            "craftability diagnostic."
        )
    evidence["scope"] = (
        "All 137 tradeable Jewelcrafting jewelry, equipment, component, setting, utility, "
        "weapon, and sealed random-result outputs"
    )
    evidence["rules"] = {
        "active_hellscream_listing_prices_used": False,
        "external_gold_values_copied": False,
        "external_role": "Gold-normalized relative rank within comparable BoE or like-purpose craft cohorts only.",
        "gold_scale": "Fixed frozen Hellscream cohort anchors or qualified completed sales.",
        "reagent_floor_role": "Exact audited 3.3.5 recipe cost is a separate craftability diagnostic and does not automatically set market value.",
        "random_result_rule": "Icy Prism, Brilliant Glass, and Prismatic Black Diamond are valued only as sealed finished items; possible contents never inherit the full input cost.",
        "sparse_sale_rule": "Low-confidence completed sales receive 25% weight, or 50% when they span at least two buyers and two UTC days; the balance remains the reviewed cohort fallback.",
        "single_item_medium_gate": "At least four completed buyouts, two distinct buyers, and two distinct UTC days, with largest-buyer unit share at most 0.50.",
        "stackable_medium_gate": "The single-item gate plus at least 12 completed units.",
        "no_coverage_rule": "Without completed sales or external comparison coverage, retain the frozen pre-Phase-2 band.",
        "large_change_rule": "A fallback or sparse-sale Target move over 50% requires at least two comparison realms; qualified local completed sales may stand independently.",
    }
    evidence["summary"] = {
        "items_reviewed": len(records),
        "sections_reviewed": len(jewelry_sections(config)),
        "boe_equipment_reviewed": sum(record["view"] == "boe-equipment" for record in records),
        "components_special_reviewed": sum(record["view"] == "components-special" for record in records),
        "quality_counts": dict(sorted(Counter(record["quality"] for record in records).items())),
        "bands_changed": 0,
        "completed_sale_items": sum(record["local_completed_sales"] is not None for record in records),
        "medium_confidence_sale_items": sum(
            record["proposal"]["decision"] == "direct-completed-sales" for record in records
        ),
        "items_seen_on_three_realms": sum(
            record["external_relative_review"]["realm_count"] == 3 for record in records
        ),
        "target_changes_over_fifty_percent": 0,
        "large_changes_accepted": 0,
        "large_changes_retained": 0,
        "proposals_below_reagent_floor": 0,
        "legacy_baseline_duplicates": sum(record["legacy_baseline_duplicate"] for record in records),
        "decision_counts": {},
        "external_gold_values_copied": False,
    }
    update_summary(evidence)
    return evidence


def format_money(copper: int) -> str:
    return shared.format_money(copper)


def format_band(band: dict) -> str:
    return shared.format_band(band)


def render_report(evidence: dict) -> str:
    summary = evidence["summary"]
    lines = [
        "# Jewelcrafting Jewelry Evidence Pricing Review",
        "",
        f"- Reviewed: `{evidence['refreshed']}`",
        f"- Scope: `{evidence['scope']}`",
        f"- BoE jewelry, equipment, and weapon outputs: `{summary['boe_equipment_reviewed']}`",
        f"- Components, settings, utilities, special gems, and sealed random crafts: `{summary['components_special_reviewed']}`",
        f"- Price bands changed: `{summary['bands_changed']}`",
        f"- Items with completed-sale evidence: `{summary['completed_sale_items']}`",
        f"- Items seen on all three comparison realms: `{summary['items_seen_on_three_realms']}`",
        f"- Manually reviewed Target candidates over 50%: `{summary['target_changes_over_fifty_percent']}`",
        f"- Large changes accepted / retained: `{summary['large_changes_accepted']}` / `{summary['large_changes_retained']}`",
        f"- Final proposals below at least one exact recipe-floor band: `{summary['proposals_below_reagent_floor']}`",
        f"- Legacy baseline duplicates synchronized: `{summary['legacy_baseline_duplicates']}`",
        "- Active Hellscream listing prices used: `no`",
        "- External gold copied into Hellscream prices: `no`",
        "- Publication status: `local only — not published`",
        "",
        "## Decision",
        "",
        "BoE outputs are compared by expansion section, rarity, and item-level cohort—the same Evidence Pricing structure used for other BoEs. Components, settings, special gems, utilities, and sealed random-result crafts are compared only with like-purpose outputs. Qualified Hellscream completed buyouts may set value; sparse sales are shrunk toward a fixed Hellscream cohort estimate. External observations set relative rank only, while the frozen Hellscream cohort anchor sets the gold scale.",
        "",
        "Exact recipe cost remains a separate craftability diagnostic. A sale estimate below that floor is not a profitable-craft claim: use cheaper owned inputs or skip the craft. Random-result crafts are valued only as sealed items.",
        "",
        "## Item decisions",
        "",
        "| Section | Item | Kind | Old Q / T / H | Recipe floor Q / T / H | Proposed Q / T / H | Target change | Local sales | External coverage | Decision | Confidence | Review |",
        "|---|---|---|---:|---:|---:|---:|---:|---:|---|---|---|",
    ]
    records = sorted(
        evidence["items"].values(),
        key=lambda record: (
            record["view"],
            record["section"],
            -record["proposal"]["proposed_band"]["target"],
            record["name"],
        ),
    )
    for record in records:
        sales = record["local_completed_sales"]
        sales_text = (
            f"{sales['completed_buyouts']} buyouts / {sales['units']} units / "
            f"{sales['distinct_buyers']} buyers / {sales['distinct_days']} days"
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
                    record["market_kind"],
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
    lines.extend(["", "## Manual review of Target candidates over 50%", ""])
    large = [record for record in records if record["proposal"]["requires_large_change_review"]]
    if not large:
        lines.append("No Target candidate exceeded 50%.")
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
            "- The external source reports listings and listing history, not verified completed sales.",
            "- Nominal external gold is not saved or copied; observations rank items only inside reviewed cohorts.",
            "- Current Hellscream listings are excluded because guide-driven auctions dominate the local market.",
            "- Rare recipes, random suffixes, and slow BoE turnover are not hidden premiums without completed-sale support.",
            "- The 360 cut-gem outputs remain in their already completed companion review.",
            "",
            "## Reproduction",
            "",
            "```powershell",
            "python scripts/review-ah-jewelcrafting-jewelry-prices.py --check",
            "```",
            "",
            "Publishing is a separate step and is not part of this review.",
            "",
        ]
    )
    return "\n".join(lines)


def cleaned_notes(config: dict) -> dict[str, str]:
    cleaned = {}
    order = []
    for row in entries(config):
        key = row["key"]
        item = row["item"]
        order.append(key)
        if key in SPECIAL_NOTE_OVERRIDES:
            cleaned[key] = SPECIAL_NOTE_OVERRIDES[key]
            continue
        note = item["row_note"].strip()
        if row["view"] == "boe-equipment":
            suffix = re.compile(
                rf"\s+{re.escape(item['name'])} targets .*? gearing, twink, or collection buyers; post one at a time\.$",
                re.IGNORECASE,
            )
            note, count = suffix.subn("", note, count=1)
            if count == 0 and "collection buyers; post one at a time" in note:
                raise ValueError(f"Could not remove repeated BoE note boilerplate: {item['name']}")
            note = re.sub(r";\s*(\d+)\s+ChargesSell Price:.*?\.$", r"; \1 charges.", note)
            note = note.replace("UniqueNeck;", "Unique;")
            if "<Random enchantment>" in note and "Inspect the rolled suffix before listing." not in note:
                note += " Inspect the rolled suffix before listing."
        cleaned[key] = note.strip()
    groups: dict[str, list[str]] = {}
    for key in order:
        groups.setdefault(cleaned[key], []).append(key)
    for keys in groups.values():
        if len(keys) <= 1:
            continue
        canonical_name = shared.merged_item(config, keys[0])["name"]
        for key in keys[1:]:
            cleaned[key] += (
                f" Same stats as {canonical_name}; use this exact item name when listing."
            )
    return cleaned


def validate(evidence: dict, *, require_applied: bool) -> None:
    config = load(CRAFTED_PATH)
    baseline = load(BASELINE_PATH)["items"]
    recipe_audit = load(ROOT / "data" / "ah-crafted-recipe-audit.json")
    rows = entries(config)
    row_by_key = {row["key"]: row for row in rows}
    expected_ids = {str(int(row["item"]["item_id"])) for row in rows}
    if evidence.get("method") != "Evidence Pricing" or evidence.get("model_version") != MODEL_VERSION:
        raise ValueError("Jewelcrafting jewelry Evidence Pricing method or model is stale")
    if set(evidence.get("items", {})) != expected_ids:
        raise ValueError("Jewelcrafting jewelry evidence does not cover all 137 outputs")
    if evidence["rules"].get("active_hellscream_listing_prices_used") is not False:
        raise ValueError("Active Hellscream listings must not set prices")
    if evidence["rules"].get("external_gold_values_copied") is not False:
        raise ValueError("External gold must not be copied")
    expected_notes = cleaned_notes(config) if require_applied else None
    duplicate_count = 0
    for record in evidence["items"].values():
        row = row_by_key[record["canonical_key"]]
        item = row["item"]
        floor = {band: int(item["pricing_floor_copper"][band]) for band in PRICE_BANDS}
        if record["reagent_floor"] != floor:
            raise ValueError(f"{record['name']}: saved recipe floor is stale")
        recipe = recipe_audit["recipes"][record["canonical_key"]]
        if int(recipe["output_count"]) != 1 or record["recipe"] != {
            "source_spell_id": int(recipe["source_spell_id"]),
            "output_count": 1,
            "reagents": recipe["reagents"],
        }:
            raise ValueError(f"{record['name']}: recipe evidence is stale")
        proposal = record["proposal"]
        band = proposal["proposed_band"]
        if not band["quick"] <= band["target"] <= band["high"]:
            raise ValueError(f"{record['name']}: invalid reviewed price band")
        if proposal["requires_large_change_review"] and proposal["reviewer_decision"] not in {
            "accept", "revise", "retain"
        }:
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
            expected_ref = f"data/ah-jewelcrafting-jewelry-price-evidence.json#items/{record['item_id']}"
            if raw.get("price_evidence_ref") != expected_ref:
                raise ValueError(f"{record['name']}: evidence reference is stale")
            if raw.get("row_note") != expected_notes[record["canonical_key"]]:
                raise ValueError(f"{record['name']}: row note is stale")
            if "collection buyers; post one at a time" in raw.get("row_note", ""):
                raise ValueError(f"{record['name']}: repeated BoE boilerplate remains")
            duplicate = baseline.get(str(record["item_id"]))
            if duplicate:
                duplicate_count += 1
                duplicate_band = {name: int(duplicate[name]) for name in PRICE_BANDS}
                if duplicate_band != band or duplicate.get("evidence_ref") != expected_ref:
                    raise ValueError(f"{record['name']}: duplicate baseline is not synchronized")
    if require_applied and duplicate_count != 5:
        raise ValueError(f"Expected five synchronized legacy baselines, found {duplicate_count}")


def apply_catalog(evidence: dict) -> None:
    config = load(CRAFTED_PATH)
    source = CRAFTED_PATH.read_text(encoding="utf-8")
    baseline_doc = load(BASELINE_PATH)
    baseline = baseline_doc["items"]
    notes = cleaned_notes(config)
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
        expected_ref = f"data/ah-jewelcrafting-jewelry-price-evidence.json#items/{item_id}"
        updated["row_note"] = notes[key]
        updated["price_strategy"] = "evidence-pricing-market-value"
        updated["price_evidence_ref"] = expected_ref
        pattern = re.compile(rf'^(    "{re.escape(key)}": )\{{.*\}}(,?)$', re.MULTILINE)
        replacement = rf"\g<1>{json.dumps(updated, ensure_ascii=False, separators=(',', ':'))}\g<2>"
        source, count = pattern.subn(replacement, source, count=1)
        if count != 1:
            raise ValueError(f"Could not update canonical Jewelcrafting jewelry row: {key}")
        duplicate = baseline.get(str(item_id))
        if duplicate:
            record = evidence["items"][str(item_id)]
            for name in PRICE_BANDS:
                duplicate[name] = int(band[name])
            duplicate["source_type"] = record["proposal"]["source_type"]
            duplicate["confidence"] = record["proposal"]["confidence"]
            duplicate["reason"] = record["proposal"]["reason"]
            duplicate["evidence_ref"] = expected_ref
    for section in jewelry_sections(config):
        ordered = sorted(
            section["items"],
            key=lambda key: (
                -int(proposals[key]["target"]),
                shared.merged_item(config, key)["name"].casefold(),
            ),
        )
        pattern = re.compile(
            r'(^\s*\{"title"\s*:\s*"'
            + re.escape(section["title"])
            + r'".*?"items"\s*:\s*)\[.*?\](\},?)$',
            re.MULTILINE,
        )
        source, count = pattern.subn(
            lambda match: match.group(1)
            + json.dumps(ordered, ensure_ascii=False, separators=(",", ":"))
            + match.group(2),
            source,
            count=1,
        )
        if count != 1:
            raise ValueError(f"Could not reorder Jewelcrafting jewelry section: {section['title']}")
    old_note = '"label":"Evidence Pricing and craft diagnostics","text":"Cut gems use Evidence Pricing from qualified completed sales or fixed same-tier and same-color fallbacks; active Hellscream listings never set their values. Exact uncut-gem opportunity cost remains a separate craftability diagnostic, so skip cuts priced below that floor unless your inputs are cheaper. Jewelry, components, settings, and sealed random crafts still use their exact 3.3.5 recipe-cost method until their companion phase is reviewed."'
    new_note = '"label":"Evidence Pricing and craft diagnostics","text":"Cut gems, jewelry, components, settings, utilities, and sealed random crafts use Evidence Pricing from qualified completed sales or fixed comparable-cohort fallbacks; active Hellscream listings never set their values. The exact 3.3.5 recipe cost or uncut-gem opportunity cost remains a separate craftability diagnostic, so skip outputs priced below that floor unless your inputs are cheaper. BoE gear is a slow market; list one at a time. Random-result crafts are valued only as sealed items."'
    if old_note in source:
        source = source.replace(old_note, new_note, 1)
    elif new_note not in source:
        raise ValueError("Could not find the pre-jewelry-review shared note")
    old_intro = "Prices use exact 3.3.5 recipes and frozen non-circular input references; random-result crafts are priced only as sealed finished items."
    new_intro = "Sale bands use the saved Jewelcrafting Evidence Pricing reviews, while exact 3.3.5 recipe costs remain separate craftability diagnostics; random-result crafts are valued only as sealed finished items."
    if old_intro in source:
        source = source.replace(old_intro, new_intro, 1)
    elif new_intro not in source:
        raise ValueError("Could not find the pre-jewelry-review Jewelcrafting introduction")
    CRAFTED_PATH.write_text(source, encoding="utf-8", newline="\n")
    BASELINE_PATH.write_text(
        json.dumps(baseline_doc, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )

    manifest_source = GUIDE_MANIFEST_PATH.read_text(encoding="utf-8")
    gem_old = "Evidence-priced cut and special gems across Wrath, Outland, and Classic. Each exact uncut-gem opportunity cost remains a separate craftability diagnostic; jewelry, components, settings, and sealed random crafts remain in the companion Jewelcrafting Jewelry & Components guide for the next review phase."
    gem_new = "Evidence-priced cut and special gems across Wrath, Outland, and Classic. Each exact uncut-gem opportunity cost remains a separate craftability diagnostic; Evidence-priced jewelry, components, settings, and sealed random crafts are in the companion Jewelcrafting Jewelry & Components guide."
    jewelry_old = "Tradeable outputs from exact 3.3.5 recipes: jewelry, equipment, components, settings, and sealed random-result crafts across Wrath, Outland, and Classic. Uncut gems and cut-gem markets remain in the companion Jewelcrafting Gems & Cuts guide."
    jewelry_new = "Evidence-priced jewelry, equipment, components, settings, utilities, and sealed random-result crafts across Wrath, Outland, and Classic. Exact recipe costs remain separate craftability diagnostics; uncut gems and cut-gem markets are in the companion Jewelcrafting Gems & Cuts guide."
    if gem_old in manifest_source:
        manifest_source = manifest_source.replace(gem_old, gem_new, 1)
    elif gem_new not in manifest_source:
        raise ValueError("Could not update the Jewelcrafting gem guide description")
    if jewelry_old in manifest_source:
        manifest_source = manifest_source.replace(jewelry_old, jewelry_new, 1)
    elif jewelry_new not in manifest_source:
        raise ValueError("Could not update the Jewelcrafting jewelry guide description")
    GUIDE_MANIFEST_PATH.write_text(manifest_source, encoding="utf-8", newline="\n")


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
    update_summary(evidence)
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
        config = load(CRAFTED_PATH)
        rows = entries(config)
        print(json.dumps(Counter(row["item"]["quality"] for row in rows), indent=2))
        print(json.dumps(Counter(row["view"] for row in rows), indent=2))
        print(f"items {len(rows)}")
        print(f"sections {len(jewelry_sections(config))}")
        return 0
    if args.refresh:
        evidence = build_evidence()
        validate(evidence, require_applied=False)
        write_outputs(evidence)
        print(json.dumps(evidence["summary"], indent=2))
        return 0
    if args.review:
        evidence = apply_review_safeguards(load(EVIDENCE_PATH))
        update_summary(evidence)
        evidence["manual_review_completed"] = date.today().isoformat()
        validate(evidence, require_applied=False)
        write_outputs(evidence)
        print(json.dumps(evidence["summary"], indent=2))
        return 0
    if args.refresh_dependencies:
        evidence = refresh_dependency_diagnostics(load(EVIDENCE_PATH))
        validate(evidence, require_applied=True)
        write_outputs(evidence)
        print("Refreshed Jewelcrafting jewelry recipe diagnostics without changing prices.")
        return 0
    evidence = load(EVIDENCE_PATH)
    if args.apply:
        validate(evidence, require_applied=False)
        apply_catalog(evidence)
        validate(evidence, require_applied=True)
        print(f"Applied {len(evidence['items'])} reviewed Jewelcrafting jewelry price bands.")
        return 0
    validate(evidence, require_applied=True)
    if REPORT_PATH.read_text(encoding="utf-8") != render_report(evidence):
        print("Jewelcrafting jewelry Evidence Pricing report is stale.", file=sys.stderr)
        return 1
    print("Jewelcrafting jewelry Evidence Pricing review is current.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
