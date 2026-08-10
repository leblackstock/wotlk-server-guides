#!/usr/bin/env python3
"""Review all finished Engineering output prices with Evidence Pricing."""

from __future__ import annotations

import argparse
import importlib.util
import json
import re
import statistics
import sys
from collections import Counter
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SHARED_REVIEW_PATH = ROOT / "scripts" / "review-ah-blacksmithing-prices.py"
EVIDENCE_PATH = ROOT / "data" / "ah-engineering-price-evidence.json"
REPORT_PATH = ROOT / "docs" / "ah-engineering-pricing-review.md"
CRAFTED_PATH = ROOT / "data" / "ah-crafted-sections.json"
BASELINE_PATH = ROOT / "data" / "ah-price-baselines.json"
GUIDE_FILENAME = "engineering-materials-ah-price-guide.html"
MODEL_VERSION = "engineering-evidence-pricing-v1"
PRICE_BANDS = ("quick", "target", "high")

FIXED_ORDER_SECTION_TITLES = {
    "Northrend crafted Engineering parts",
    "Outland crafted Engineering parts",
    "Classic crafted Engineering parts",
    "Engineer-only tools",
    "Blasting powders",
    "Ammo",
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
shared.FIXED_ORDER_SECTION_TITLES = FIXED_ORDER_SECTION_TITLES

PRICE_BASIS_BY_ITEM_ID: dict[int, int] = {}
SALE_GATE_BY_ITEM_ID: dict[int, str] = {}


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def entries(config: dict) -> list[dict]:
    result = []
    seen = set()
    sections = config["guides"][GUIDE_FILENAME]["sections"]
    for section in sections:
        title = section["title"]
        basis = int(section.get("price_basis_stack", 1))
        for key in section["items"]:
            if key in seen:
                raise ValueError(f"Duplicate Engineering output: {key}")
            seen.add(key)
            item = dict(shared.merged_item(config, key))
            if item.get("profession") != "Engineering":
                raise ValueError(f"Non-Engineering output in Engineering catalog: {key}")
            if item.get("price_evidence_ref", "").startswith(
                "data/ah-collectible-price-evidence.json#items/"
            ):
                continue
            item_id = int(item["item_id"])
            PRICE_BASIS_BY_ITEM_ID[item_id] = basis
            is_single = item.get("stack") == "1"
            SALE_GATE_BY_ITEM_ID[item_id] = "one-at-a-time" if is_single else "stackable"
            item["pricing_floor_copper"] = {
                band: int(item["pricing_floor_copper"][band]) * basis
                for band in PRICE_BANDS
            }
            result.append(
                {
                    "key": key,
                    "section": title,
                    "view": title,
                    "price_basis_quantity": basis,
                    "sale_gate": SALE_GATE_BY_ITEM_ID[item_id],
                    "item": item,
                }
            )
    if len(result) != 55:
        raise ValueError(f"Engineering inventory drifted: {len(result)} rows")
    return result


def ammo_tier(item: dict) -> str:
    detail = item.get("detail", "")
    if "ICC" in detail:
        return "ICC ammo"
    if "Wrath" in detail:
        return "Wrath ammo"
    if "TBC" in detail:
        return "Outland ammo"
    target = int(item["target_copper"])
    return "upper Classic ammo" if target >= 1_200 else "entry Classic ammo"


def cohort_key(row: dict) -> str:
    section = row["section"]
    item = row["item"]
    if section == "Ammo":
        return f"Ammo | {ammo_tier(item)}"
    if section in {
        "Northrend crafted Engineering parts",
        "Outland crafted Engineering parts",
        "Classic crafted Engineering parts",
        "General-use Engineering utility",
        "Engineer-only bombs, sapper charges, and decoys",
    }:
        return f"{section} | {shared.floor_bucket(int(item['pricing_floor_copper']['target']))}"
    return section


shared.entries = entries
shared.cohort_key = cohort_key

original_fetch_observation = shared.fetch_observation


def fetch_observation(task: tuple[str, int, str, int, int, float]) -> tuple[str, int, dict]:
    source_key, item_id, observation = original_fetch_observation(task)
    if observation.get("present"):
        observation["median_buyout_copper"] *= PRICE_BASIS_BY_ITEM_ID.get(item_id, 1)
    return source_key, item_id, observation


shared.fetch_observation = fetch_observation
original_load_sales = shared.load_sales


def load_sales(item_ids: set[int]) -> tuple[dict[int, dict], dict]:
    sales, source = original_load_sales(item_ids)
    for item_id, record in sales.items():
        basis = PRICE_BASIS_BY_ITEM_ID.get(item_id, 1)
        for field, value in record["gross_unit_copper"].items():
            if value is not None:
                record["gross_unit_copper"][field] = int(value) * basis
        common_gate = (
            record["completed_buyouts"] >= 4
            and record["distinct_buyers"] >= 2
            and record["distinct_days"] >= 2
            and (record["largest_buyer_unit_share"] or 0) <= 0.50
        )
        if SALE_GATE_BY_ITEM_ID[item_id] == "stackable":
            common_gate = common_gate and record["units"] >= 20
        record["gate_type"] = SALE_GATE_BY_ITEM_ID[item_id]
        record["evidence_gate"] = "medium" if common_gate else "low"
        record["coverage"] = "medium" if common_gate else "sparse-or-concentrated"
        record["price_basis_quantity"] = basis
    return sales, source


shared.load_sales = load_sales


def build_evidence() -> dict:
    evidence = shared.build_evidence()
    config = load(CRAFTED_PATH)
    rows = entries(config)
    row_by_key = {row["key"]: row for row in rows}
    counts = Counter(row["section"] for row in rows)
    records = list(evidence["items"].values())
    for cohort in evidence["cohorts"].values():
        cohort["anchor_source"] = cohort["anchor_source"].replace(
            "Blacksmithing", "Engineering"
        )
    for record in records:
        row = row_by_key[record["canonical_key"]]
        basis = int(row["price_basis_quantity"])
        record["view"] = row["section"]
        record["price_basis_quantity"] = basis
        record["pricing_unit"] = (
            f"per stated stack of {basis}" if basis > 1 else "per finished item"
        )
        record["sale_gate_type"] = row["sale_gate"]
        record["proposal"]["reason"] = (
            "Reviewed Engineering Evidence Pricing band. Qualified completed sales set "
            "the value when available; sparse sales are shrunk toward a fixed Hellscream "
            "comparable-cohort estimate. External asks set relative rank only and active "
            "Hellscream listings are excluded. Exact recipe cost remains a separate "
            "craftability diagnostic."
        )
    evidence["scope"] = "All 55 tradeable finished Engineering outputs"
    evidence["rules"] = {
        "active_hellscream_listing_prices_used": False,
        "external_gold_values_copied": False,
        "external_role": "Gold-normalized within-comparable-cohort relative rank only.",
        "gold_scale": "Fixed frozen Hellscream cohort anchors or qualified completed sales.",
        "reagent_floor_role": "Exact audited 3.3.5 recipe cost is a separate craftability diagnostic and does not automatically set market value.",
        "ammo_price_basis": "Ammo guide prices, external comparisons, completed-sale unit prices, and recipe floors are normalized to the displayed stack of 200.",
        "sparse_sale_rule": "Low-confidence completed sales receive 25% weight, or 50% when they span at least two buyers and two UTC days; the balance remains the reviewed cohort fallback.",
        "stackable_medium_gate": "At least 20 units across four completed buyouts, two distinct buyers, and two distinct UTC days, with largest-buyer unit share at most 0.50.",
        "one_at_a_time_medium_gate": "At least four completed buyouts, two distinct buyers, and two distinct UTC days, with largest-buyer unit share at most 0.50.",
    }
    evidence["summary"] = {
        "items_reviewed": len(records),
        "section_counts": dict(counts),
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
        "proposals_below_reagent_floor": sum(
            bool(record["proposal"]["below_reagent_floor_bands"]) for record in records
        ),
        "decision_counts": dict(
            sorted(Counter(record["proposal"]["decision"] for record in records).items())
        ),
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
        "# Engineering Evidence Pricing Review",
        "",
        f"- Reviewed: `{evidence['refreshed']}`",
        f"- Scope: `{evidence['scope']}`",
        f"- Finished outputs: `{summary['items_reviewed']}`",
        f"- Price bands changed: `{summary['bands_changed']}`",
        f"- Items with completed-sale evidence: `{summary['completed_sale_items']}`",
        f"- Items seen on all three comparison realms: `{summary['items_seen_on_three_realms']}`",
        f"- Manually reviewed Target changes over 50%: `{summary['target_changes_over_fifty_percent']}`",
        f"- Market proposals below at least one exact recipe-floor band: `{summary['proposals_below_reagent_floor']}`",
        "- Active Hellscream listing prices used: `no`",
        "- External gold copied into Hellscream prices: `no`",
        "- Publication status: `local only — not published`",
        "",
        "## Decision",
        "",
        "Every output keeps its exact audited 3.3.5 recipe floor as a separate craftability diagnostic. Qualified Hellscream completed buyouts may set market value; sparse sales are shrunk toward a fixed comparable-cohort estimate. Current Hellscream listings are excluded. External observations set relative rank only; fixed Hellscream cohort anchors set the gold scale.",
        "",
        "Ammo is normalized to the displayed stack of 200 in every comparison. A proposal below the matching recipe floor is intentional sale-value guidance, not a profitable-craft claim.",
        "",
        "## Item decisions",
        "",
        "| Section | Item | Basis | Old Q / T / H | Recipe floor Q / T / H | Proposed Q / T / H | Target change | Local sales | External coverage | Decision | Confidence | Review |",
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
            "- The external source reports listings and listing history, not verified completed sales.",
            "- External observations set relative rank only; nominal external gold is not saved or copied.",
            "- Current Hellscream listings are excluded because guide-driven auctions dominate the local market.",
            "- Recipe access, specialization, and server-specific Engineering rules remain notes rather than hidden premiums.",
            "",
            "## Reproduction",
            "",
            "```powershell",
            "python scripts/review-ah-engineering-prices.py --check",
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
        raise ValueError("Engineering Evidence Pricing method or model is stale")
    if set(evidence.get("items", {})) != expected_ids:
        raise ValueError("Engineering evidence does not cover all 55 outputs")
    if evidence["rules"].get("active_hellscream_listing_prices_used") is not False:
        raise ValueError("Active Hellscream listings must not set prices")
    if evidence["rules"].get("external_gold_values_copied") is not False:
        raise ValueError("External gold must not be copied")
    for record in evidence["items"].values():
        row = row_by_key[record["canonical_key"]]
        item = row["item"]
        floor = {band: int(item["pricing_floor_copper"][band]) for band in PRICE_BANDS}
        if record["reagent_floor"] != floor:
            raise ValueError(f"{record['name']}: saved price-basis recipe floor is stale")
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
            expected_ref = f"data/ah-engineering-price-evidence.json#items/{record['item_id']}"
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
        expected_ref = f"data/ah-engineering-price-evidence.json#items/{item_id}"
        updated["price_strategy"] = "evidence-pricing-market-value"
        updated["price_evidence_ref"] = expected_ref
        pattern = re.compile(rf'^(    "{re.escape(key)}": )\{{.*\}}(,?)$', re.MULTILINE)
        replacement = rf"\g<1>{json.dumps(updated, ensure_ascii=False, separators=(',', ':'))}\g<2>"
        source, count = pattern.subn(replacement, source, count=1)
        if count != 1:
            raise ValueError(f"Could not update canonical Engineering row: {key}")
        duplicate = baseline.get(str(item_id))
        if duplicate:
            for name in PRICE_BANDS:
                duplicate[name] = int(band[name])
            duplicate["source_type"] = evidence["items"][str(item_id)]["proposal"]["source_type"]
            duplicate["confidence"] = evidence["items"][str(item_id)]["proposal"]["confidence"]
            duplicate["reason"] = evidence["items"][str(item_id)]["proposal"]["reason"]
            duplicate["evidence_ref"] = expected_ref
    guide = config["guides"][GUIDE_FILENAME]
    for section in guide["sections"]:
        if any(key not in proposals for key in section["items"]):
            continue
        if section["title"] in FIXED_ORDER_SECTION_TITLES:
            continue
        ordered = sorted(
            section["items"],
            key=lambda key: (-int(proposals[key]["target"]), shared.merged_item(config, key)["name"].casefold()),
        )
        pattern = re.compile(
            r'(^\s*\{"title": "'
            + re.escape(section["title"])
            + r'".*?"items": )\[.*?\](\},?)$',
            re.MULTILINE,
        )
        item_array = json.dumps(ordered, ensure_ascii=False, separators=(",", ":"))
        source, count = pattern.subn(
            lambda match: match.group(1) + item_array + match.group(2),
            source,
            count=1,
        )
        if count != 1:
            raise ValueError(f"Could not reorder Engineering section: {section['title']}")
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
        print(f"items {len(rows)}")
        print(f"price-basis stacks {dict(sorted(Counter(row['price_basis_quantity'] for row in rows).items()))}")
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
        print("Refreshed Engineering recipe-floor diagnostics without changing prices.")
        return 0
    evidence = load(EVIDENCE_PATH)
    if args.apply:
        validate(evidence, require_applied=False)
        apply_catalog(evidence)
        validate(evidence, require_applied=True)
        print(f"Applied {len(evidence['items'])} reviewed Engineering price bands.")
        return 0
    validate(evidence, require_applied=True)
    if REPORT_PATH.read_text(encoding="utf-8") != render_report(evidence):
        print("Engineering Evidence Pricing report is stale.", file=sys.stderr)
        return 1
    print("Engineering Evidence Pricing review is current.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
