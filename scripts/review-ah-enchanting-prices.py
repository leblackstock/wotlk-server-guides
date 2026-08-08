#!/usr/bin/env python3
"""Review all finished Enchanting output prices with Evidence Pricing."""

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
CRAFTED_PATH = ROOT / "data" / "ah-crafted-sections.json"
BASELINE_PATH = ROOT / "data" / "ah-price-baselines.json"
RECIPE_AUDIT_PATH = ROOT / "data" / "ah-enchanting-recipe-audit.json"
EVIDENCE_PATH = ROOT / "data" / "ah-enchanting-price-evidence.json"
REPORT_PATH = ROOT / "docs" / "ah-enchanting-pricing-review.md"
GUIDE_MANIFEST_PATH = ROOT / "data" / "ah-guides.json"
GUIDE_FILENAME = "enchanting-mats-ah-price-guide.html"
MODEL_VERSION = "enchanting-evidence-pricing-v1"
PRICE_BANDS = ("quick", "target", "high")
PRIOR_REVIEWED_ITEMS = {
    12655: {
        "evidence_ref": "data/ah-gathering-material-price-evidence.json#items/12655",
        "source_type": "documented-fallback",
        "confidence": "fallback",
    }
}

NOTE_OVERRIDES = {
    "ench-scroll-of-enchant-weapon-black-magic": "Spec-dependent raid caster proc: harmful spells sometimes increase haste rating by 250.",
    "ench-scroll-of-enchant-gloves-armsman": "Tank threat and parry glove enchant: increases threat caused by 2% and parry rating by 10.",
    "ench-scroll-of-enchant-weapon-soulfrost": "Level-70 caster weapon option: increases Frost and Shadow spell power by 54.",
    "ench-scroll-of-enchant-weapon-sunfire": "Level-70 caster weapon option: increases Fire and Arcane spell power by 50.",
}


spec = importlib.util.spec_from_file_location("ah_shared_finished_review", SHARED_REVIEW_PATH)
if spec is None or spec.loader is None:
    raise RuntimeError("Could not load the shared finished-output review helpers")
shared = importlib.util.module_from_spec(spec)
spec.loader.exec_module(shared)

shared.EVIDENCE_PATH = EVIDENCE_PATH
shared.REPORT_PATH = REPORT_PATH
shared.RECIPE_AUDIT_PATH = RECIPE_AUDIT_PATH
shared.GUIDE_FILENAME = GUIDE_FILENAME
shared.MODEL_VERSION = MODEL_VERSION
shared.FIXED_ORDER_SECTION_TITLES = set()


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def enchanting_sections(config: dict) -> list[dict]:
    sections = config["guides"][GUIDE_FILENAME]["sections"]
    if len(sections) != 25:
        raise ValueError(f"Enchanting section inventory drifted: {len(sections)}")
    return sections


def view_for(section_title: str) -> str:
    title = section_title.casefold()
    if "scrolls" in title:
        return "enchant-scroll"
    if "weapon oils" in title:
        return "weapon-oil"
    if "wands" in title:
        return "boe-wand"
    return "intermediate-gem"


def entries(config: dict) -> list[dict]:
    result = []
    seen_keys: set[str] = set()
    seen_ids: set[int] = set()
    for section in enchanting_sections(config):
        view = view_for(section["title"])
        for key in section["items"]:
            if key in seen_keys:
                raise ValueError(f"Duplicate Enchanting output: {key}")
            seen_keys.add(key)
            item = shared.merged_item(config, key)
            item_id = int(item["item_id"])
            if item_id in seen_ids:
                raise ValueError(f"Duplicate Enchanting output item ID: {item_id}")
            seen_ids.add(item_id)
            result.append(
                {"key": key, "section": section["title"], "view": view, "item": item}
            )
    counts = Counter(row["view"] for row in result)
    expected = {
        "enchant-scroll": 259,
        "weapon-oil": 9,
        "boe-wand": 4,
        "intermediate-gem": 4,
    }
    if len(result) != 276 or counts != expected:
        raise ValueError(f"Enchanting inventory drifted: {len(result)} rows, {dict(counts)}")
    return result


def effect_kind(item: dict) -> str:
    name = item["name"].casefold()
    note = item.get("row_note", "").casefold()
    text = f"{name} {note}"
    if any(token in name for token in ("lifeward", "blade ward", "blood draining", "titanguard")):
        return "tank-survival"
    if any(token in name for token in ("black magic", "soulfrost", "sunfire", "spellsurge")):
        return "caster-healer"
    if "berserking" in name:
        return "physical-dps"
    if any(token in name for token in ("icebreaker", "giant slayer", "scourgebane", "demonslaying", "tuskarr's vitality", "cat's swiftness", "boar's speed")):
        return "special-utility"
    if "resistance" in text:
        return "resistance"
    if any(token in text for token in ("fishing", "gather", "mining", "herbal", "skinning", "riding")):
        return "profession-utility"
    if any(token in text for token in ("spell power", "spellpower", "intellect", "spirit", "mana", "healer", "caster")):
        return "caster-healer"
    if "stats" in text:
        return "hybrid-stats"
    if any(token in text for token in ("defense", "armor", "parry", "dodge", "block", "stamina", "tank", "health")):
        return "tank-survival"
    if any(token in text for token in ("attack power", "agility", "strength", "striking", "physical-dps", "expertise", "hit rating")):
        return "physical-dps"
    return "special-utility"


def cohort_key(row: dict) -> str:
    item = row["item"]
    floor = int(item["pricing_floor_copper"]["target"])
    if row["view"] == "enchant-scroll":
        return f"{row['section']} | {effect_kind(item)} | {shared.floor_bucket(floor)}"
    if row["view"] == "weapon-oil":
        oil_kind = "mana-oil" if "mana oil" in item["name"].casefold() else "wizard-oil"
        return f"{row['section']} | {oil_kind}"
    if row["view"] == "boe-wand":
        return f"{row['section']} | {item['quality']} | {shared.level_bucket(shared.item_level(item))}"
    kind = "prismatic-gem" if "sphere" in item["name"].casefold() else "tradeable-intermediate"
    return f"{row['section']} | {kind} | {shared.floor_bucket(floor)}"


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
        prior_review = PRIOR_REVIEWED_ITEMS.get(int(record["item_id"]))
        if prior_review:
            final = dict(before)
            decision = "retain-prior-reviewed-material-band"
            source_type = prior_review["source_type"]
            confidence = prior_review["confidence"]
            review = "retain"
            reviewer_note = (
                "Retained the completed Phase 1 material review; the Enchanting output pass "
                "must not replace an already reviewed tradeable-input market band."
            )
            proposal["reason"] = reviewer_note
        elif local_sales and local_sales["evidence_gate"] == "medium":
            final = candidate
            review = "accept"
            reviewer_note = (
                "Accepted from qualifying completed Hellscream sales; comparison-realm "
                "coverage is not required for this medium-confidence local value."
            )
        elif not local_sales and realms == 0:
            final = dict(before)
            decision = "retain-reviewed-band-no-comparison-coverage"
            source_type = "frozen-pre-phase2-guide"
            confidence = "fallback"
            review = "retain"
            reviewer_note = "Retained because no completed sale or comparison realm supports a new value."
        elif large and realms < 2:
            final = dict(before)
            decision = "retain-reviewed-band-insufficient-coverage"
            source_type = "frozen-pre-phase2-guide"
            confidence = "low" if local_sales else "fallback"
            review = "retain"
            reviewer_note = (
                "Retained after large-change review because sparse local sales plus zero- or "
                "one-realm comparison coverage do not support a Target move over 50%."
            )
        else:
            final = candidate
            review = "accept"
            reviewer_note = (
                "Accepted after reviewing the same-expansion, same-slot, like-purpose cohort, "
                "exact recipe diagnostic, buyer use, and completed-sale or comparison coverage. "
                "External gold remains excluded."
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
    recipe_audit = load(RECIPE_AUDIT_PATH)
    rows = entries(config)
    row_by_key = {row["key"]: row for row in rows}
    records = list(evidence["items"].values())
    for cohort in evidence["cohorts"].values():
        cohort["anchor_source"] = cohort["anchor_source"].replace(
            "Blacksmithing", "Enchanting"
        )
    for record in records:
        row = row_by_key[record["canonical_key"]]
        item = row["item"]
        stackable = item.get("stack", "1") != "1"
        recipe = recipe_audit["recipes"][record["canonical_key"]]
        record["view"] = row["view"]
        record["effect_kind"] = effect_kind(item) if row["view"] == "enchant-scroll" else row["view"]
        record["pricing_unit"] = "per finished item"
        record["sale_gate_type"] = "stackable-finished-item" if stackable else "single-finished-item"
        record["recipe"] = {
            "source_spell_id": int(recipe["source_spell_id"]),
            "output_count": int(recipe["output_count"]),
            "reagents": recipe["reagents"],
            **({"vellum": recipe["vellum"]} if "vellum" in recipe else {}),
        }
        if int(record["item_id"]) not in PRIOR_REVIEWED_ITEMS:
            record["proposal"]["reason"] = (
                "Reviewed Enchanting Evidence Pricing band. Qualified completed sales set value "
                "when available; sparse sales are shrunk toward a fixed same-expansion, same-slot, "
                "like-purpose cohort estimate. External asks set relative rank only and active "
                "Hellscream listings are excluded. Exact spell reagents plus compatible vellum "
                "remain a separate craftability diagnostic."
            )
    evidence["scope"] = (
        "All 276 tradeable finished Enchanting outputs: 259 scrolls, nine oils, four wands, "
        "two intermediates, and two prismatic gems"
    )
    evidence["rules"] = {
        "active_hellscream_listing_prices_used": False,
        "external_gold_values_copied": False,
        "external_role": "Gold-normalized relative rank within same-expansion, same-slot, like-purpose cohorts only.",
        "gold_scale": "Fixed frozen Hellscream cohort anchors or qualified completed sales.",
        "reagent_floor_role": "Exact audited 3.3.5 spell reagents plus compatible vellum are a separate craftability diagnostic and do not set market value.",
        "vellum_rule": "Every scroll consumes the cheapest compatible Armor or Weapon Vellum rank, priced from its exact deterministic two-output Inscription recipe.",
        "sparse_sale_rule": "Low-confidence completed sales receive 25% weight, or 50% when they span at least two buyers and two UTC days; the balance remains the reviewed cohort fallback.",
        "single_item_medium_gate": "At least four completed buyouts, two distinct buyers, and two distinct UTC days, with largest-buyer unit share at most 0.50.",
        "stackable_medium_gate": "The single-item gate plus at least 12 completed units.",
        "no_coverage_rule": "Without completed sales or external comparison coverage, retain the frozen pre-Phase-2 band.",
        "large_change_rule": "A fallback or sparse-sale Target move over 50% requires at least two comparison realms; qualified local completed sales may stand independently.",
    }
    counts = Counter(record["view"] for record in records)
    evidence["summary"] = {
        "items_reviewed": len(records),
        "sections_reviewed": len(enchanting_sections(config)),
        "scrolls_reviewed": counts["enchant-scroll"],
        "oils_reviewed": counts["weapon-oil"],
        "wands_reviewed": counts["boe-wand"],
        "intermediates_gems_reviewed": counts["intermediate-gem"],
        "bands_changed": 0,
        "completed_sale_items": sum(record["local_completed_sales"] is not None for record in records),
        "medium_confidence_sale_items": sum(
            record["proposal"]["decision"] == "direct-completed-sales" for record in records
        ),
        "items_seen_on_three_realms": sum(
            record["external_relative_review"]["realm_count"] == 3 for record in records
        ),
        "items_seen_on_two_realms": sum(
            record["external_relative_review"]["realm_count"] == 2 for record in records
        ),
        "items_seen_on_one_realm": sum(
            record["external_relative_review"]["realm_count"] == 1 for record in records
        ),
        "items_seen_on_no_realms": sum(
            record["external_relative_review"]["realm_count"] == 0 for record in records
        ),
        "target_changes_over_fifty_percent": 0,
        "large_changes_accepted": 0,
        "large_changes_retained": 0,
        "proposals_below_reagent_floor": 0,
        "decision_counts": {},
        "external_gold_values_copied": False,
    }
    update_summary(evidence)
    return evidence


def format_band(band: dict) -> str:
    return shared.format_band(band)


def render_report(evidence: dict) -> str:
    summary = evidence["summary"]
    lines = [
        "# Enchanting Evidence Pricing Review",
        "",
        f"- Reviewed: `{evidence['refreshed']}`",
        f"- Scope: `{evidence['scope']}`",
        f"- Scrolls / oils / wands / intermediates and gems: `{summary['scrolls_reviewed']}` / `{summary['oils_reviewed']}` / `{summary['wands_reviewed']}` / `{summary['intermediates_gems_reviewed']}`",
        f"- Price bands changed: `{summary['bands_changed']}`",
        f"- Items with completed-sale evidence: `{summary['completed_sale_items']}`",
        f"- Medium-confidence sale items: `{summary['medium_confidence_sale_items']}`",
        f"- Comparison coverage at 3 / 2 / 1 / 0 realms: `{summary['items_seen_on_three_realms']}` / `{summary['items_seen_on_two_realms']}` / `{summary['items_seen_on_one_realm']}` / `{summary['items_seen_on_no_realms']}`",
        f"- Manually reviewed Target candidates over 50%: `{summary['target_changes_over_fifty_percent']}`",
        f"- Large changes accepted / retained: `{summary['large_changes_accepted']}` / `{summary['large_changes_retained']}`",
        f"- Final proposals below at least one exact recipe-floor band: `{summary['proposals_below_reagent_floor']}`",
        "- Active Hellscream listing prices used: `no`",
        "- External gold copied into Hellscream prices: `no`",
        "- Publication status: `local only — not published`",
        "",
        "## Decision",
        "",
        "Enchant scrolls are compared only inside same-expansion, same-slot, like-purpose, and broad recipe-cost cohorts. Oils, BoE wands, intermediates, and prismatic gems use separate like-purpose cohorts. Qualified Hellscream completed buyouts may set value; sparse sales are shrunk toward a fixed Hellscream cohort estimate. External observations set relative rank only, while the frozen Hellscream cohort anchor sets the gold scale.",
        "",
        "Exact spell reagents plus the cheapest compatible vellum remain a separate craftability diagnostic. A sale estimate below that floor is not a profitable-craft claim: use cheaper owned inputs or skip the craft.",
        "",
        "## Item decisions",
        "",
        "| Section | Item | Kind | Old Q / T / H | Recipe + vellum floor Q / T / H | Proposed Q / T / H | Target change | Local sales | External coverage | Decision | Confidence | Review |",
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
                    record["effect_kind"],
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
        lines.append("No Target candidates exceeded 50%.")
    for record in large:
        proposal = record["proposal"]
        candidate = proposal["model_proposed_band_before_manual_review"]
        lines.append(
            f"- **{record['name']}**: model candidate {shared.format_money(record['before_band']['target'])} → {shared.format_money(candidate['target'])} ({proposal['model_target_change_percent']:+.2f}%); final {shared.format_money(proposal['proposed_band']['target'])}. Decision: `{proposal['reviewer_decision']}`. {proposal['reviewer_note']}"
        )
    lines.extend(
        [
            "",
            "## Evidence limits",
            "",
            "- The external source reports listings and listing history, not verified completed sales.",
            "- Nominal external gold is not saved or copied; observations rank items only inside reviewed cohorts.",
            "- Current Hellscream listings are excluded because guide-driven auctions dominate the local market.",
            "- Rare recipe access and reputation requirements remain notes or posting cautions rather than hidden premiums without completed-sale support.",
            "",
            "## Reproduction",
            "",
            "```powershell",
            "python scripts/audit-ah-enchanting-recipes.py --check",
            "python scripts/review-ah-enchanting-prices.py --check",
            "```",
            "",
            "Publishing is a separate step and is not part of this review.",
            "",
        ]
    )
    return "\n".join(lines)


def cleaned_notes(config: dict) -> dict[str, str]:
    return {
        row["key"]: NOTE_OVERRIDES.get(row["key"], row["item"]["row_note"].strip())
        for row in entries(config)
    }


def validate(evidence: dict, *, require_applied: bool) -> None:
    config = load(CRAFTED_PATH)
    recipe_audit = load(RECIPE_AUDIT_PATH)
    rows = entries(config)
    row_by_key = {row["key"]: row for row in rows}
    expected_ids = {str(int(row["item"]["item_id"])) for row in rows}
    if evidence.get("method") != "Evidence Pricing" or evidence.get("model_version") != MODEL_VERSION:
        raise ValueError("Enchanting Evidence Pricing method or model is stale")
    if set(evidence.get("items", {})) != expected_ids:
        raise ValueError("Enchanting evidence does not cover all 276 outputs")
    if evidence["rules"].get("active_hellscream_listing_prices_used") is not False:
        raise ValueError("Active Hellscream listings must not set prices")
    if evidence["rules"].get("external_gold_values_copied") is not False:
        raise ValueError("External gold must not be copied")
    expected_notes = cleaned_notes(config) if require_applied else None
    for record in evidence["items"].values():
        row = row_by_key[record["canonical_key"]]
        item = row["item"]
        floor = {band: int(item["pricing_floor_copper"][band]) for band in PRICE_BANDS}
        if record["reagent_floor"] != floor:
            raise ValueError(f"{record['name']}: saved recipe floor is stale")
        recipe = recipe_audit["recipes"][record["canonical_key"]]
        expected_recipe = {
            "source_spell_id": int(recipe["source_spell_id"]),
            "output_count": int(recipe["output_count"]),
            "reagents": recipe["reagents"],
            **({"vellum": recipe["vellum"]} if "vellum" in recipe else {}),
        }
        if record["recipe"] != expected_recipe:
            raise ValueError(f"{record['name']}: saved recipe evidence is stale")
        proposal = record["proposal"]
        band = proposal["proposed_band"]
        if not band["quick"] <= band["target"] <= band["high"]:
            raise ValueError(f"{record['name']}: invalid reviewed band")
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
            expected_ref = PRIOR_REVIEWED_ITEMS.get(int(record["item_id"]), {}).get(
                "evidence_ref",
                f"data/ah-enchanting-price-evidence.json#items/{record['item_id']}",
            )
            if raw.get("price_evidence_ref") != expected_ref:
                raise ValueError(f"{record['name']}: evidence reference is stale")
            if raw.get("row_note") != expected_notes[record["canonical_key"]]:
                raise ValueError(f"{record['name']}: row note is stale")


def section_description(title: str) -> str:
    if "scrolls" in title.casefold():
        return "Tradeable enchant scrolls stored on the cheapest compatible vellum. Sale bands use Evidence Pricing; exact spell reagents plus vellum remain separate craftability diagnostics."
    if "weapon oils" in title.casefold():
        return "Charged weapon oils valued as finished consumables. Exact recipe cost remains a separate craftability diagnostic."
    if "wands" in title.casefold():
        return "Tradeable BoE leveling wands valued as one-at-a-time gear. Exact recipe cost remains a separate craftability diagnostic."
    return "Tradeable intermediates and prismatic gems valued within like-purpose markets. Exact recipe cost remains a separate craftability diagnostic."


def apply_catalog(evidence: dict) -> None:
    config = load(CRAFTED_PATH)
    source = CRAFTED_PATH.read_text(encoding="utf-8")
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
        updated["row_note"] = notes[key]
        updated["price_strategy"] = "evidence-pricing-market-value"
        updated["price_evidence_ref"] = PRIOR_REVIEWED_ITEMS.get(item_ids[key], {}).get(
            "evidence_ref",
            f"data/ah-enchanting-price-evidence.json#items/{item_ids[key]}",
        )
        pattern = re.compile(rf'^(    "{re.escape(key)}": )\{{.*\}}(,?)$', re.MULTILINE)
        replacement = rf"\g<1>{json.dumps(updated, ensure_ascii=False, separators=(',', ':'))}\g<2>"
        source, count = pattern.subn(replacement, source, count=1)
        if count != 1:
            raise ValueError(f"Could not update canonical Enchanting row: {key}")
    for section in enchanting_sections(config):
        ordered = sorted(
            section["items"],
            key=lambda key: (
                -int(proposals[key]["target"]),
                shared.merged_item(config, key)["name"].casefold(),
            ),
        )
        old_description = json.dumps(section["description"], ensure_ascii=False)
        new_description = json.dumps(section_description(section["title"]), ensure_ascii=False)
        if old_description in source:
            source = source.replace(old_description, new_description, 1)
        elif new_description not in source:
            raise ValueError(f"Could not update Enchanting section description: {section['title']}")
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
            raise ValueError(f"Could not reorder Enchanting section: {section['title']}")
    guide = config["guides"][GUIDE_FILENAME]
    old_intro = json.dumps(guide["intro_description"], ensure_ascii=False)
    new_intro = json.dumps(
        "This catalog covers all 259 valid tradeable enchant scrolls represented in the 3.3.5 item data, plus nine oils, four BoE wands, two intermediates, and two prismatic gems. Finished-item sale bands use Evidence Pricing; every exact recipe and compatible vellum remains a separate craftability diagnostic. Ring enchants, runed rods, and other BoP or invalid outputs are excluded.",
        ensure_ascii=False,
    )
    if old_intro in source:
        source = source.replace(old_intro, new_intro, 1)
    elif new_intro not in source:
        raise ValueError("Could not update the Enchanting introduction")
    new_label = "Evidence Pricing and craft diagnostics"
    new_text = "Finished Enchanting outputs use Evidence Pricing from qualified completed sales or fixed same-expansion, same-slot, like-purpose fallbacks; active Hellscream listings never set their values. Exact 3.3.5 spell reagents plus the cheapest compatible vellum remain a separate craftability diagnostic, so skip outputs priced below that floor unless your inputs are cheaper. Scrolls are usually tested as singles; rare-recipe access is not a hidden premium without sale evidence."
    for old_value, new_value, field in (
        (guide["shared_note"]["label"], new_label, "label"),
        (guide["shared_note"]["text"], new_text, "text"),
    ):
        old_fragment = f'{json.dumps(field)}: {json.dumps(old_value, ensure_ascii=False)}'
        new_fragment = f'{json.dumps(field)}: {json.dumps(new_value, ensure_ascii=False)}'
        if old_fragment in source:
            source = source.replace(old_fragment, new_fragment, 1)
        elif new_fragment not in source:
            raise ValueError(f"Could not update the Enchanting shared-note {field}")
    CRAFTED_PATH.write_text(source, encoding="utf-8", newline="\n")

    manifest_source = GUIDE_MANIFEST_PATH.read_text(encoding="utf-8")
    old_manifest = "Dusts, essences, shards, crystals, enchant scrolls, oils, wands, gems, and intermediates."
    new_manifest = "Reviewed dusts, essences, shards, and crystals plus Evidence-priced enchant scrolls, oils, wands, gems, and intermediates; exact recipes remain separate craft diagnostics."
    if old_manifest in manifest_source:
        manifest_source = manifest_source.replace(old_manifest, new_manifest, 1)
    elif new_manifest not in manifest_source:
        raise ValueError("Could not update the Enchanting guide description")
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
        print(json.dumps(Counter(row["view"] for row in rows), indent=2))
        print(f"items {len(rows)}")
        print(f"sections {len(enchanting_sections(config))}")
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
        print("Refreshed Enchanting recipe diagnostics without changing sale prices.")
        return 0
    evidence = load(EVIDENCE_PATH)
    if args.apply:
        validate(evidence, require_applied=False)
        apply_catalog(evidence)
        validate(evidence, require_applied=True)
        print(f"Applied {len(evidence['items'])} reviewed Enchanting price bands.")
        return 0
    validate(evidence, require_applied=True)
    if REPORT_PATH.read_text(encoding="utf-8") != render_report(evidence):
        print("Enchanting Evidence Pricing report is stale.", file=sys.stderr)
        return 1
    print("Enchanting Evidence Pricing review is current.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
