#!/usr/bin/env python3
"""Review all Jewelcrafting cut-gem prices with Evidence Pricing."""

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
EVIDENCE_PATH = ROOT / "data" / "ah-jewelcrafting-gem-price-evidence.json"
REPORT_PATH = ROOT / "docs" / "ah-jewelcrafting-gem-pricing-review.md"
CRAFTED_PATH = ROOT / "data" / "ah-crafted-sections.json"
BASELINE_PATH = ROOT / "data" / "ah-price-baselines.json"
GUIDE_MANIFEST_PATH = ROOT / "data" / "ah-guides.json"
GUIDE_FILENAME = "jewelcrafting-gems-ah-price-guide.html"
MODEL_VERSION = "jewelcrafting-gem-evidence-pricing-v1"
PRICE_BANDS = ("quick", "target", "high")

NON_GEM_SECTION_TITLES = {
    "Wrath special and random crafts",
    "Wrath BoE jewelry",
    "Outland special and random crafts",
    "Outland BoE jewelry",
    "Classic Jewelcrafting components",
    "Classic random gem conversion",
    "Classic BoE jewelry",
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


def gem_sections(config: dict) -> list[dict]:
    sections = [
        section
        for section in config["guides"][GUIDE_FILENAME]["sections"]
        if section["title"] not in NON_GEM_SECTION_TITLES
    ]
    if len(sections) != 38:
        raise ValueError(f"Jewelcrafting gem section inventory drifted: {len(sections)}")
    return sections


def entries(config: dict) -> list[dict]:
    result = []
    seen = set()
    for section in gem_sections(config):
        for key in section["items"]:
            if key in seen:
                raise ValueError(f"Duplicate Jewelcrafting gem output: {key}")
            seen.add(key)
            item = shared.merged_item(config, key)
            if item.get("profession") != "Jewelcrafting":
                raise ValueError(f"Non-Jewelcrafting output in gem inventory: {key}")
            if "cut" not in item.get("detail", "").casefold():
                raise ValueError(f"Non-cut output leaked into gem phase: {key}")
            result.append(
                {
                    "key": key,
                    "section": section["title"],
                    "view": section["title"],
                    "item": item,
                }
            )
    if len(result) != 360:
        raise ValueError(f"Jewelcrafting gem inventory drifted: {len(result)} rows")
    return result


def cohort_key(row: dict) -> str:
    return row["section"]


shared.entries = entries
shared.cohort_key = cohort_key
original_load_sales = shared.load_sales


def load_sales(item_ids: set[int]) -> tuple[dict[int, dict], dict]:
    sales, source = original_load_sales(item_ids)
    for record in sales.values():
        qualifies = (
            record["units"] >= 20
            and record["completed_buyouts"] >= 4
            and record["distinct_buyers"] >= 2
            and record["distinct_days"] >= 2
            and (record["largest_buyer_unit_share"] or 0) <= 0.50
        )
        record["gate_type"] = "stackable-cut-gem"
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
        if local_sales and local_sales["evidence_gate"] == "medium":
            final = candidate
            review = "accept"
            reviewer_note = (
                "Accepted from qualifying completed Hellscream sales; external comparison "
                "coverage is not required to establish this medium-confidence local value."
            )
        elif not local_sales and realms == 0:
            final = dict(before)
            decision = "retain-reviewed-band-no-comparison-coverage"
            source_type = "frozen-pre-phase2-guide"
            confidence = "fallback"
            review = "retain"
            reviewer_note = (
                "Retained because no completed sale or comparison realm supports a new cut-gem value."
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
                "Accepted after reviewing the exact uncut-gem opportunity cost, useful stat, "
                "gem tier, and completed-sale or comparison coverage. External gold remains excluded."
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


def uncut_dependency(record: dict, baselines: dict) -> dict:
    reagents = record["recipe"]["reagents"]
    if len(reagents) != 1 or int(reagents[0]["count"]) != 1:
        raise ValueError(f"{record['name']}: cut gem does not consume exactly one uncut gem")
    reagent = reagents[0]
    baseline = baselines.get(str(reagent["item_id"]))
    return {
        "item_id": int(reagent["item_id"]),
        "name": reagent["name"],
        "count": 1,
        "saved_baseline_present": baseline is not None,
        "saved_baseline_confidence": baseline.get("confidence") if baseline else None,
        "opportunity_cost_band": dict(record["reagent_floor"]),
    }


def build_evidence() -> dict:
    evidence = shared.build_evidence()
    evidence = apply_review_safeguards(evidence)
    config = load(CRAFTED_PATH)
    baselines = load(BASELINE_PATH)["items"]
    rows = entries(config)
    row_by_key = {row["key"]: row for row in rows}
    records = list(evidence["items"].values())
    for cohort in evidence["cohorts"].values():
        cohort["anchor_source"] = cohort["anchor_source"].replace(
            "Blacksmithing", "Jewelcrafting cut-gem"
        )
    for record in records:
        row = row_by_key[record["canonical_key"]]
        record["view"] = "gems-cuts"
        record["pricing_unit"] = "per cut gem"
        record["sale_gate_type"] = "stackable-cut-gem"
        record["uncut_dependency"] = uncut_dependency(record, baselines)
        record["proposal"]["reason"] = (
            "Reviewed Jewelcrafting cut-gem Evidence Pricing band. Qualified completed "
            "sales set value when available; sparse sales are shrunk toward a fixed "
            "same-tier and same-color cohort estimate. External asks set relative rank "
            "only and active Hellscream listings are excluded. The exact uncut-gem "
            "opportunity cost remains a separate craftability diagnostic."
        )
    decisions = Counter(record["proposal"]["decision"] for record in records)
    evidence["scope"] = "All 360 tradeable Jewelcrafting cut and special-gem outputs"
    evidence["rules"] = {
        "active_hellscream_listing_prices_used": False,
        "external_gold_values_copied": False,
        "external_role": "Gold-normalized within same expansion, quality, and color cohort relative rank only.",
        "gold_scale": "Fixed frozen Hellscream gem-cohort anchors or qualified completed sales.",
        "uncut_opportunity_cost_role": "The exact reviewed uncut gem is a separate craftability diagnostic and does not automatically set cut-gem sale value.",
        "sparse_sale_rule": "Low-confidence completed sales receive 25% weight, or 50% when they span at least two buyers and two UTC days; the balance remains the reviewed cohort fallback.",
        "cut_gem_medium_gate": "At least 20 gems across four completed buyouts, two distinct buyers, and two distinct UTC days, with largest-buyer unit share at most 0.50.",
        "no_coverage_rule": "Without completed sales or external comparison coverage, retain the frozen pre-Phase-2 band.",
        "large_change_rule": "A fallback or sparse-sale Target move over 50% requires at least two comparison realms; qualified local completed sales may stand independently.",
    }
    evidence["summary"] = {
        "items_reviewed": len(records),
        "sections_reviewed": len(gem_sections(config)),
        "quality_counts": dict(sorted(Counter(record["quality"] for record in records).items())),
        "bands_changed": sum(
            record["before_band"] != record["proposal"]["proposed_band"]
            for record in records
        ),
        "completed_sale_items": sum(record["local_completed_sales"] is not None for record in records),
        "medium_confidence_sale_items": sum(
            record["proposal"]["decision"] == "direct-completed-sales" for record in records
        ),
        "items_seen_on_three_realms": sum(
            record["external_relative_review"]["realm_count"] == 3 for record in records
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
        "proposals_below_uncut_floor": sum(
            bool(record["proposal"]["below_reagent_floor_bands"]) for record in records
        ),
        "decision_counts": dict(sorted(decisions.items())),
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
        "# Jewelcrafting Gem Evidence Pricing Review",
        "",
        f"- Reviewed: `{evidence['refreshed']}`",
        f"- Scope: `{evidence['scope']}`",
        f"- Cut gems: `{summary['items_reviewed']}` across `{summary['sections_reviewed']}` sections",
        f"- Price bands changed: `{summary['bands_changed']}`",
        f"- Items with completed-sale evidence: `{summary['completed_sale_items']}`",
        f"- Items seen on all three comparison realms: `{summary['items_seen_on_three_realms']}`",
        f"- Manually reviewed Target candidates over 50%: `{summary['target_changes_over_fifty_percent']}`",
        f"- Large changes accepted / retained: `{summary['large_changes_accepted']}` / `{summary['large_changes_retained']}`",
        f"- Final proposals below at least one uncut opportunity-cost band: `{summary['proposals_below_uncut_floor']}`",
        "- Active Hellscream listing prices used: `no`",
        "- External gold copied into Hellscream prices: `no`",
        "- Publication status: `local only — not published`",
        "",
        "## Decision",
        "",
        "Each cut is compared only with gems from the same expansion, quality, and color family. Qualified Hellscream completed buyouts may set value; sparse sales are shrunk toward a fixed comparable-gem estimate. External observations set relative rank only, while fixed Hellscream cohort anchors set the gold scale.",
        "",
        "The exact reviewed uncut gem is retained as a separate opportunity-cost diagnostic. A cut priced below that floor is not a recommendation to buy the uncut gem and cut it; use cheaper owned inputs, charge for commission work, or skip that cut.",
        "",
        "## Item decisions",
        "",
        "| Section | Cut gem | Uncut input | Old Q / T / H | Uncut floor Q / T / H | Proposed Q / T / H | Target change | Local sales | External coverage | Decision | Confidence | Review |",
        "|---|---|---|---:|---:|---:|---:|---:|---:|---|---|---|",
    ]
    records = sorted(
        evidence["items"].values(),
        key=lambda record: (
            record["section"],
            -record["proposal"]["proposed_band"]["target"],
            record["name"],
        ),
    )
    for record in records:
        sales = record["local_completed_sales"]
        sales_text = (
            f"{sales['completed_buyouts']} buyouts / {sales['units']} gems / "
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
                    record["uncut_dependency"]["name"],
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
            "- External observations rank cuts only within the same gem family; nominal external gold is not saved or copied.",
            "- Current Hellscream listings are excluded because guide-driven auctions dominate the local market.",
            "- Recipe access and token/vendor supply affect availability, but are not hidden premiums without sale evidence.",
            "- The companion jewelry and component outputs remain outside this phase.",
            "",
            "## Reproduction",
            "",
            "```powershell",
            "python scripts/review-ah-jewelcrafting-gem-prices.py --check",
            "```",
            "",
            "Publishing is a separate step and is not part of this review.",
            "",
        ]
    )
    return "\n".join(lines)


def cleaned_cut_notes(config: dict) -> dict[str, str]:
    cleaned: dict[str, str] = {}
    order: list[str] = []
    for row in entries(config):
        key = row["key"]
        item = row["item"]
        suffix = re.compile(
            rf"\s+{re.escape(item['name'])} is an? .*? socket market; post singles first\.$",
            re.IGNORECASE,
        )
        note, _ = suffix.subn("", item["row_note"], count=1)
        cleaned[key] = note.strip()
        order.append(key)
    groups: dict[str, list[str]] = {}
    for key in order:
        groups.setdefault(cleaned[key], []).append(key)
    for keys in groups.values():
        if len(keys) <= 1:
            continue
        canonical = keys[0]
        canonical_name = shared.merged_item(config, canonical)["name"]
        for key in keys[1:]:
            cleaned[key] += (
                f" Same stats as {canonical_name}; use this exact item name when listing."
            )
    if len(set(cleaned.values())) != len(cleaned):
        raise ValueError("Cut-gem note cleanup left duplicated notes")
    return cleaned


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
            "proposals_below_uncut_floor": sum(
                bool(record["proposal"]["below_reagent_floor_bands"])
                for record in records
            ),
            "decision_counts": dict(
                sorted(Counter(record["proposal"]["decision"] for record in records).items())
            ),
        }
    )


def validate(evidence: dict, *, require_applied: bool) -> None:
    config = load(CRAFTED_PATH)
    baseline = load(BASELINE_PATH)["items"]
    rows = entries(config)
    row_by_key = {row["key"]: row for row in rows}
    expected_ids = {str(int(row["item"]["item_id"])) for row in rows}
    if evidence.get("method") != "Evidence Pricing" or evidence.get("model_version") != MODEL_VERSION:
        raise ValueError("Jewelcrafting gem Evidence Pricing method or model is stale")
    if set(evidence.get("items", {})) != expected_ids:
        raise ValueError("Jewelcrafting gem evidence does not cover all 360 outputs")
    if evidence["rules"].get("active_hellscream_listing_prices_used") is not False:
        raise ValueError("Active Hellscream listings must not set prices")
    if evidence["rules"].get("external_gold_values_copied") is not False:
        raise ValueError("External gold must not be copied")
    expected_notes = cleaned_cut_notes(config) if require_applied else None
    for record in evidence["items"].values():
        item = row_by_key[record["canonical_key"]]["item"]
        floor = {band: int(item["pricing_floor_copper"][band]) for band in PRICE_BANDS}
        if record["reagent_floor"] != floor:
            raise ValueError(f"{record['name']}: saved uncut opportunity cost is stale")
        dependency = record["uncut_dependency"]
        if dependency["opportunity_cost_band"] != floor:
            raise ValueError(f"{record['name']}: uncut dependency band is stale")
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
            expected_ref = f"data/ah-jewelcrafting-gem-price-evidence.json#items/{record['item_id']}"
            if raw.get("price_evidence_ref") != expected_ref:
                raise ValueError(f"{record['name']}: evidence reference is stale")
            if raw.get("row_note") != expected_notes[record["canonical_key"]]:
                raise ValueError(f"{record['name']}: repeated row-note boilerplate remains")
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
    notes = cleaned_cut_notes(config)
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
        expected_ref = f"data/ah-jewelcrafting-gem-price-evidence.json#items/{item_id}"
        updated["row_note"] = notes[key]
        updated["price_strategy"] = "evidence-pricing-market-value"
        updated["price_evidence_ref"] = expected_ref
        pattern = re.compile(rf'^(    "{re.escape(key)}": )\{{.*\}}(,?)$', re.MULTILINE)
        replacement = rf"\g<1>{json.dumps(updated, ensure_ascii=False, separators=(',', ':'))}\g<2>"
        source, count = pattern.subn(replacement, source, count=1)
        if count != 1:
            raise ValueError(f"Could not update canonical Jewelcrafting gem row: {key}")
        duplicate = baseline.get(str(item_id))
        if duplicate:
            for name in PRICE_BANDS:
                duplicate[name] = int(band[name])
            duplicate["source_type"] = evidence["items"][str(item_id)]["proposal"]["source_type"]
            duplicate["confidence"] = evidence["items"][str(item_id)]["proposal"]["confidence"]
            duplicate["reason"] = evidence["items"][str(item_id)]["proposal"]["reason"]
            duplicate["evidence_ref"] = expected_ref
    for section in gem_sections(config):
        ordered = sorted(
            section["items"],
            key=lambda key: (-int(proposals[key]["target"]), shared.merged_item(config, key)["name"].casefold()),
        )
        pattern = re.compile(
            r'(^\s*\{"title"\s*:\s*"'
            + re.escape(section["title"])
            + r'".*?"items"\s*:\s*)\[.*?\](\},?)$',
            re.MULTILINE,
        )
        item_array = json.dumps(ordered, ensure_ascii=False, separators=(",", ":"))
        source, count = pattern.subn(
            lambda match: match.group(1) + item_array + match.group(2),
            source,
            count=1,
        )
        if count != 1:
            raise ValueError(f"Could not reorder Jewelcrafting gem section: {section['title']}")
    old_note = '"label":"Craft-cost pricing","text":"Each price band uses the exact 3.3.5 reagent quantities, minimum guaranteed output, the uncut gem or tradeable intermediate\'s opportunity cost, and a modest demand margin. Active AH listings never set or raise the baseline; use them only for competition and timing. Most initial references are low-confidence frozen values until realized sales replace them. Random-result crafts are valued as sealed items, never as though every possible gem were guaranteed."'
    new_note = '"label":"Evidence Pricing and craft diagnostics","text":"Cut gems use Evidence Pricing from qualified completed sales or fixed same-tier and same-color fallbacks; active Hellscream listings never set their values. Exact uncut-gem opportunity cost remains a separate craftability diagnostic, so skip cuts priced below that floor unless your inputs are cheaper. Jewelry, components, settings, and sealed random crafts still use their exact 3.3.5 recipe-cost method until their companion phase is reviewed."'
    if old_note in source:
        source = source.replace(old_note, new_note, 1)
    elif new_note not in source:
        raise ValueError("Could not update the shared Jewelcrafting pricing note")
    CRAFTED_PATH.write_text(source, encoding="utf-8", newline="\n")
    BASELINE_PATH.write_text(
        json.dumps(baseline_doc, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def refresh_dependency_diagnostics(evidence: dict) -> dict:
    config = load(CRAFTED_PATH)
    baselines = load(BASELINE_PATH)["items"]
    rows = {row["key"]: row for row in entries(config)}
    for record in evidence["items"].values():
        floor = rows[record["canonical_key"]]["item"]["pricing_floor_copper"]
        record["reagent_floor"] = {band: int(floor[band]) for band in PRICE_BANDS}
        record["uncut_dependency"] = uncut_dependency(record, baselines)
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
        print(json.dumps(Counter(record["quality"] for record in (row["item"] for row in rows)), indent=2))
        print(f"items {len(rows)}")
        print(f"sections {len(gem_sections(config))}")
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
        print("Refreshed Jewelcrafting gem opportunity-cost diagnostics without changing prices.")
        return 0
    evidence = load(EVIDENCE_PATH)
    if args.apply:
        validate(evidence, require_applied=False)
        apply_catalog(evidence)
        validate(evidence, require_applied=True)
        print(f"Applied {len(evidence['items'])} reviewed Jewelcrafting gem price bands.")
        return 0
    validate(evidence, require_applied=True)
    if REPORT_PATH.read_text(encoding="utf-8") != render_report(evidence):
        print("Jewelcrafting gem Evidence Pricing report is stale.", file=sys.stderr)
        return 1
    print("Jewelcrafting gem Evidence Pricing review is current.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
