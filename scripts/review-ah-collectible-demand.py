#!/usr/bin/env python3
"""Build and validate demand/turnover evidence for the collectible AH guide."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from collections import Counter
from datetime import date, datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
AUDIT_PATH = ROOT / "data" / "ah-collectible-audit.json"
PRICE_EVIDENCE_PATH = ROOT / "data" / "ah-collectible-price-evidence.json"
DEMAND_EVIDENCE_PATH = ROOT / "data" / "ah-collectible-demand-evidence.json"
SECTIONS_PATH = ROOT / "data" / "ah-collectible-sections.json"
REPORT_PATH = ROOT / "docs" / "ah-collectible-demand-review.md"
CROSS_SERVER_PATH = ROOT / "data" / "ah-dropped-gear-cross-server-diagnostics.json"
BASE_REVIEW_PATH = ROOT / "scripts" / "review-ah-blacksmithing-prices.py"
IMPORTER_PATH = ROOT / "scripts" / "import-ah-dropped-gear-evidence.py"
BEANCOUNTER_PATH = Path(
    r"D:\Hellscream WoW\launcher\WTF\Account\LEBLACKSTOCK\SavedVariables\BeanCounter.lua"
)
SCAN_PATH = Path(
    r"D:\Hellscream WoW\launcher\WTF\Account\LEBLACKSTOCK\SavedVariables\Auc-ScanData.lua"
)
MODEL_VERSION = "collectible-demand-turnover-v1"
EXPECTED_MARKETS = 6
PROMOTIONAL_EXCLUSIONS = {22781: "Polar Bear Collar"}


KNOWN_DRIVERS = {
    "pet-50": {
        "label": "50-pet collection achievement",
        "url": "https://www.wowhead.com/wotlk/achievement=1250/shop-smart-shop-pet-smart",
    },
    "pet-75": {
        "label": "75-pet collection achievement",
        "url": "https://www.wowhead.com/wotlk/achievement=2516/lil-game-hunter",
    },
    "mount-50": {
        "label": "50-mount collection achievement",
        "url": "https://www.wowhead.com/wotlk/achievement=2143/leading-the-cavalry",
    },
    "mount-100": {
        "label": "100-mount collection achievement",
        "url": "https://www.wowhead.com/wotlk/achievement=2536/mountain-o-mounts",
    },
    "shafted": {
        "label": "Shafted! event achievement",
        "url": "https://www.wowhead.com/wotlk/achievement=1188/shafted",
    },
    "fistful-of-love": {
        "label": "Fistful of Love event achievement",
        "url": "https://www.wowhead.com/wotlk/achievement=1699/fistful-of-love",
    },
    "torch-juggler": {
        "label": "Torch Juggler event achievement",
        "url": "https://www.wowhead.com/wotlk/achievement=272/torch-juggler",
    },
    "frenzied-firecracker": {
        "label": "Frenzied Firecracker event achievement",
        "url": "https://www.wowhead.com/wotlk/achievement=1552/frenzied-firecracker",
    },
    "rocket-red-glare": {
        "label": "The Rocket's Red Glare event achievement",
        "url": "https://www.wowhead.com/wotlk/achievement=1281/the-rockets-red-glare",
    },
    "passenger-motorcycle": {
        "label": "General-use passenger motorcycle utility",
        "url": "https://www.wowhead.com/wotlk/item=41508/mechano-hog",
    },
    "dalaran-portal": {
        "label": "Jaina's Locket Dalaran portal utility",
        "url": "https://www.wowhead.com/wotlk/item=52251/jainas-locket",
    },
}

SEASONAL_ACHIEVEMENT_DRIVERS = {
    22200: "shafted",
    22218: "fistful-of-love",
    34599: "torch-juggler",
    21747: "frenzied-firecracker",
    21576: "rocket-red-glare",
}
SEASONAL_APPAREL = {6833, 6835, 19028, 22276, 22277, 22278, 22279, 22280, 22281, 22282}
SEASONAL_MEDIUM = {17194, 21301, 21305, 21308, 21309}
SEASONAL_LOW_MEDIUM = {21213, 34258, 50163}
MOTORCYCLES = {41508, 44413}
PROFESSION_MOUNTS = {34060, 34061, 44554}
COMMON_FARMED_PETS = {8492, 39896, 39898, 39899}


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load {path.name}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


BASE = load_module("ah_collectible_demand_base", BASE_REVIEW_PATH)
IMPORTER = load_module("ah_collectible_demand_importer", IMPORTER_PATH)


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def source_snapshot(path: Path) -> dict:
    return {
        "provided": path.is_file(),
        "sha256": hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else None,
        "modified_utc": (
            datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc)
            .replace(microsecond=0)
            .isoformat()
            if path.is_file()
            else None
        ),
        "raw_path_saved": False,
        "identity_names_saved": False,
    }


def known_driver_ids(item: dict) -> list[str]:
    item_id = int(item["item_id"])
    drivers: list[str] = []
    if not item.get("season") and item["kind"] == "Companion":
        drivers.extend(("pet-50", "pet-75"))
    if item["kind"] == "Mount":
        drivers.extend(("mount-50", "mount-100"))
    if item_id in MOTORCYCLES:
        drivers.append("passenger-motorcycle")
    if item_id == 52251:
        drivers.append("dalaran-portal")
    seasonal_driver = SEASONAL_ACHIEVEMENT_DRIVERS.get(item_id)
    if seasonal_driver:
        drivers.append(seasonal_driver)
    return drivers


def assessment(item: dict, external_supply: dict, local_sales: dict | None) -> dict:
    item_id = int(item["item_id"])
    group = item["group"]
    units = int(external_supply["total_units"])

    if group == "vendor-unlimited":
        demand, demand_class, turnover = "Low-Med", "med", "Slow / steady"
        rationale = "Pet-count achievements create broad collector utility, while unlimited vendor supply limits urgency; the resale is mainly route and faction convenience."
    elif group == "vendor-limited":
        demand, demand_class, turnover = "Med", "med", "Slow"
        sale_note = " One valid local completed buyout supports real, but still sparse, demand." if local_sales else ""
        rationale = "Pet-count achievements plus a verified stock cap and restock timer support stronger convenience demand than unlimited vendors." + sale_note
    elif group == "vendor-token":
        demand, demand_class, turnover = "Med-High", "hi", "Slow"
        rationale = "Pet-count achievements and faction-gated Argent Tournament acquisition support collector interest, but the 40-seal input constrains supply and sale frequency."
    elif group == "companion-drops":
        if item_id in COMMON_FARMED_PETS:
            demand, demand_class, turnover = "Low-Med", "med", "Slow"
            scarcity = "common or saturated"
        elif 0 < units <= 12:
            demand, demand_class, turnover = "High", "hi", "Very slow"
            scarcity = "scarce"
        elif 0 < units <= 40:
            demand, demand_class, turnover = "Med-High", "hi", "Very slow"
            scarcity = "thin"
        else:
            demand, demand_class, turnover = "Low-Med", "med", "Slow"
            scarcity = "common or saturated"
        rationale = f"Pet-count achievements create collector demand; comparison-market supply is {scarcity}. Scarcity raises interest, but rare-pet buyers remain infrequent."
    elif group == "companion-quest-rewards":
        demand, demand_class, turnover = "High", "hi", "Very slow"
        rationale = "Pet-count achievements and the long OOX quest-chain route support prestige collector interest; comparison-market supply is scarce."
    elif group == "crafted-collectibles" and item_id in MOTORCYCLES:
        demand, demand_class, turnover = "High", "hi", "Slow"
        rationale = "Mount-count achievements, passenger utility, and no profession requirement create broad interest, while the high craft floor slows conversion."
    elif group == "crafted-collectibles" and item_id in PROFESSION_MOUNTS:
        demand, demand_class, turnover = "Med", "med", "Slow"
        rationale = "Mount-count achievements support interest, but the Engineering or Tailoring use requirement materially narrows the buyer pool."
    elif group == "crafted-collectibles":
        demand, demand_class, turnover = "Med", "med", "Slow"
        rationale = "Pet-count achievements support repeat collector demand; recipe access and craft cost constrain supply without making sales fast."
    elif group == "quest-accessories" and item_id in {52200, 52251}:
        demand, demand_class, turnover = "High", "hi", "Very slow"
        rationale = (
            "Mount-count achievements and prestige support strong interest in the Crimson Deathcharger."
            if item_id == 52200
            else "The reusable Dalaran portal and Shadowmourne provenance support strong utility and prestige interest."
        )
    elif group == "quest-accessories" and item_id in {52252, 52253}:
        demand, demand_class, turnover = "Med-High", "hi", "Very slow"
        rationale = "Shadowmourne provenance plus appearance or vanity utility supports collector interest, but the high-ticket buyer pool is thin."
    elif group == "quest-accessories":
        demand, demand_class, turnover = "Med", "med", "Very slow"
        rationale = "Shadowmourne provenance supports collector interest, but novelty-only utility and a high-ticket market limit buyer frequency."
    elif item_id in SEASONAL_ACHIEVEMENT_DRIVERS:
        demand, demand_class, turnover = "High in season", "hi", "Seasonal"
        rationale = "A named holiday achievement consumes or requires this item, creating a concentrated demand window during the event; expect Very Low interest off-season."
    elif item_id in SEASONAL_APPAREL:
        demand, demand_class, turnover = "Med in season", "med", "Seasonal"
        rationale = "Tradeable event apparel has cosmetic and roleplay demand during the holiday window; expect Low interest off-season."
    elif item_id in SEASONAL_MEDIUM:
        demand, demand_class, turnover = "Med in season", "med", "Seasonal"
        rationale = "Season-specific companion, recipe, or gift utility supports a limited event-window market; expect Low interest off-season."
    elif item_id in SEASONAL_LOW_MEDIUM:
        demand, demand_class, turnover = "Low-Med in season", "med", "Seasonal"
        rationale = "Recognizable holiday utility supports some event-window demand, but there is no saved direct sales history; expect Very Low interest off-season."
    else:
        demand, demand_class, turnover = "Low in season", "low", "Seasonal"
        rationale = "This is a tradeable event novelty without a saved direct sales history or a verified achievement requirement; expect Very Low interest off-season."

    confidence = "low-medium" if local_sales else "low"
    return {
        "demand": demand,
        "demand_class": demand_class,
        "turnover": turnover,
        "confidence": confidence,
        "rationale": rationale,
    }


def build_evidence() -> dict:
    audit = load(AUDIT_PATH)
    cross_server = load(CROSS_SERVER_PATH)
    items = {int(item_id): item for item_id, item in audit["items"].items()}
    item_ids = set(items)

    sales, sales_meta = BASE.load_sales(item_ids)
    supply = {}
    scan_meta = {
        "provided": False,
        "listing_prices_saved": False,
        "listings_treated_as_sales": False,
    }
    if BEANCOUNTER_PATH.is_file() and SCAN_PATH.is_file():
        owned = IMPORTER.parse_characters(BEANCOUNTER_PATH, "Garrosh")
        listings, parsed = IMPORTER.parse_scan(SCAN_PATH, "Garrosh", item_ids, owned)
        supply = {item_id: IMPORTER.supply_record(listings.get(item_id, [])) for item_id in item_ids}
        scan_meta = {"provided": True, **parsed, "listings_treated_as_sales": False}

    tasks = []
    query_items = {item_id: item["name"] for item_id, item in items.items()} | PROMOTIONAL_EXCLUSIONS
    for source_key, (realm_id, faction_id) in BASE.SOURCE_IDS.items():
        for item_id, name in query_items.items():
            tasks.append((source_key, item_id, name, realm_id, faction_id, 1.0))
    observations, retry_summary = BASE.fetch_observations_with_retries(tasks)

    sources = {}
    for source_key in BASE.SOURCE_IDS:
        source = cross_server["sources"][source_key]
        sources[source_key] = {
            "realm": source["realm"],
            "faction": source["faction"],
            "progression": source["progression"],
            "source_url": source["source_url"],
        }

    def external_rows_for(item_id: int) -> list[dict]:
        rows = []
        for source_key in BASE.SOURCE_IDS:
            observation = observations[item_id][source_key]
            source = sources[source_key]
            rows.append({
                "source": source_key,
                "realm": source["realm"],
                "faction": source["faction"],
                "present": bool(observation["present"]),
                "quantity": int(observation["quantity"]),
                "scan_timestamp": observation.get("scan_timestamp"),
                "source_url": observation["source_url"],
            })
        return rows

    records = {}
    demand_counts = Counter()
    turnover_counts = Counter()
    for item_id, item in sorted(items.items()):
        external_rows = external_rows_for(item_id)
        markets_present = sum(row["present"] for row in external_rows)
        external_supply = {
            "markets_checked": len(external_rows),
            "markets_present": markets_present,
            "realms_present": len({row["realm"] for row in external_rows if row["present"]}),
            "total_units": sum(row["quantity"] for row in external_rows),
            "observations": external_rows,
            "classification": "current-listing-supply-only",
            "proves_completed_sales": False,
        }
        item_sales = sales.get(item_id)
        item_assessment = assessment(item, external_supply, item_sales)
        demand_counts[item_assessment["demand"]] += 1
        turnover_counts[item_assessment["turnover"]] += 1
        records[str(item_id)] = {
            "item_id": item_id,
            "name": item["name"],
            "group": item["group"],
            "season": item.get("season"),
            "kind": item["kind"],
            "known_demand_driver_ids": known_driver_ids(item),
            "local_completed_sales": item_sales,
            "local_current_supply": supply.get(item_id, {
                "auction_rows": 0,
                "units": 0,
                "distinct_sellers": 0,
                "largest_seller_unit_share": None,
                "rows_with_buyout": 0,
                "owned_account_rows_excluded": 0,
                "owned_account_units_excluded": 0,
                "classification": "snapshot-unavailable",
                "diagnostic_only": True,
            }),
            "external_supply": external_supply,
            "assessment": item_assessment,
        }

    return {
        "version": 1,
        "reviewed": date.today().isoformat(),
        "model_version": MODEL_VERSION,
        "scope": f"Buyer-interest and conservative turnover assessments for all {len(records)} active collectible-guide rows after promotional exclusions.",
        "rules": {
            "demand_means": "Expected breadth of buyer interest from known use and collection drivers; it is not a measured sale rate.",
            "turnover_means": "Conservative expected speed on a low-population realm; only completed sales can directly confirm turnover.",
            "external_listings_prove_sales": False,
            "external_listings_used_as_supply_only": True,
            "external_prices_saved": False,
            "external_prices_used": False,
            "single_snapshot_establishes_turnover": False,
            "absence_proves_no_demand": False,
            "seasonal_labels_apply": "During the named event; use the stated off-season expectation outside that window.",
            "prices_changed_by_this_model": False,
        },
        "known_demand_drivers": KNOWN_DRIVERS,
        "source_snapshots": {
            "beancounter": {**source_snapshot(BEANCOUNTER_PATH), **sales_meta},
            "auction_scan": {**source_snapshot(SCAN_PATH), **scan_meta},
            "external_supply": {
                "source": "https://ah.nerfed.net/servers/base?id=7",
                "markets": sources,
                "retry_summary": retry_summary,
                "listing_prices_saved": False,
                "listings_treated_as_sales": False,
            },
        },
        "summary": {
            "items_reviewed": len(records),
            "markets_checked_per_item": EXPECTED_MARKETS,
            "active_item_comparison_requests": len(records) * EXPECTED_MARKETS,
            "promotional_exclusion_requests": len(PROMOTIONAL_EXCLUSIONS) * EXPECTED_MARKETS,
            "comparison_requests": retry_summary["initial_requests"],
            "final_failed_comparison_requests": retry_summary["final_failed_requests"],
            "items_with_local_completed_sales": sum(bool(record["local_completed_sales"]) for record in records.values()),
            "items_present_in_local_supply": sum(record["local_current_supply"]["auction_rows"] > 0 for record in records.values()),
            "items_present_in_any_comparison_market": sum(record["external_supply"]["markets_present"] > 0 for record in records.values()),
            "demand_labels": dict(sorted(demand_counts.items())),
            "turnover_labels": dict(sorted(turnover_counts.items())),
        },
        "excluded_items": {
            str(item_id): {
                "item_id": item_id,
                "name": name,
                "status": "excluded-promotional",
                "reason": "The pinned acquisition route is the iCoke promotional voucher quest, and no direct Hellscream enablement evidence is saved.",
                "external_supply": {
                    "markets_checked": EXPECTED_MARKETS,
                    "markets_present": sum(row["present"] for row in external_rows_for(item_id)),
                    "total_units": sum(row["quantity"] for row in external_rows_for(item_id)),
                    "observations": external_rows_for(item_id),
                    "proves_server_enablement": False,
                },
            }
            for item_id, name in PROMOTIONAL_EXCLUSIONS.items()
        },
        "items": records,
    }


def reclassify_saved(data: dict) -> dict:
    audit = load(AUDIT_PATH)
    demand_counts = Counter()
    turnover_counts = Counter()
    for item_id, record in data["items"].items():
        item_assessment = assessment(
            audit["items"][item_id],
            record["external_supply"],
            record.get("local_completed_sales"),
        )
        record["assessment"] = item_assessment
        demand_counts[item_assessment["demand"]] += 1
        turnover_counts[item_assessment["turnover"]] += 1
    data["reviewed"] = date.today().isoformat()
    data["model_version"] = MODEL_VERSION
    data["summary"]["demand_labels"] = dict(sorted(demand_counts.items()))
    data["summary"]["turnover_labels"] = dict(sorted(turnover_counts.items()))
    return data


def report(data: dict) -> str:
    summary = data["summary"]
    retry = data["source_snapshots"]["external_supply"]["retry_summary"]
    lines = [
        "# Companions, Mounts & Accessories Demand and Turnover Review",
        "",
        f"- Review date: `{data['reviewed']}`",
        f"- Active rows reviewed: `{summary['items_reviewed']}`",
        f"- Comparison markets per item: `{summary['markets_checked_per_item']}`",
        f"- Active item/market checks: `{summary['active_item_comparison_requests']}`",
        f"- Promotional-exclusion checks: `{summary['promotional_exclusion_requests']}`",
        f"- Total comparison requests: `{retry['initial_requests']}` initial / `{retry['final_failed_requests']}` final failures",
        f"- Items with valid local completed sales: `{summary['items_with_local_completed_sales']}`",
        f"- Items present in the current local supply snapshot: `{summary['items_present_in_local_supply']}`",
        f"- Items present in at least one comparison market: `{summary['items_present_in_any_comparison_market']}`",
        "",
        "## Interpretation",
        "",
        "Demand is buyer-interest breadth, not guaranteed sales speed. Turnover is shown separately and remains conservative for a low-population realm. The external comparison pages expose current listings, so they establish supply breadth and scarcity only; they do not prove a completed sale, sell-through rate, cancellation, or expiration. One snapshot cannot measure turnover.",
        "",
        "The only valid local completed-sale evidence in this scope is one Wood Frog Box buyout from one buyer on one day. It supports real but sparse demand and does not justify calling the category fast-moving.",
        "",
        "## Demand label distribution",
        "",
        "| Label | Rows |",
        "|---|---:|",
    ]
    for label, count in summary["demand_labels"].items():
        lines.append(f"| {label} | {count} |")
    lines.extend(["", "## Turnover label distribution", "", "| Label | Rows |", "|---|---:|"])
    for label, count in summary["turnover_labels"].items():
        lines.append(f"| {label} | {count} |")
    lines.extend([
        "",
        "## Classification policy",
        "",
        "- Unlimited vendor pets: Low-Med interest, Slow / steady turnover. Collection achievements create utility, but unlimited stock makes this primarily convenience arbitrage.",
        "- True limited-stock pets: Med interest, Slow turnover. Stock caps and restock timers support a stronger convenience market; Wood Frog also has one sparse local sale.",
        "- Argent Tournament pets: Med-High interest, Slow turnover. Pet-count achievements and faction-gated, time-gated supply support collector interest.",
        "- Farmed pets: Low-Med through High interest according to current comparison-market scarcity, with Slow or Very slow turnover. Scarcity is not itself a sale.",
        "- Crafted companions: Med interest, Slow turnover. Profession-restricted mounts remain Med because their buyer pool is narrower.",
        "- Mechano-hog and Mekgineer's Chopper: High interest, Slow turnover because they combine mount-count progress, passenger utility, and a high craft floor.",
        "- Crimson Deathcharger and Jaina's Locket: High interest, Very slow turnover. The former advances mount collection; the latter adds reusable Dalaran portal utility. Both are high-ticket prestige rewards.",
        "- Seasonal achievement consumables: High in season, Seasonal turnover, and expected Very Low interest off-season.",
        "- Seasonal apparel: Med in season, Seasonal turnover, and expected Low interest off-season. Pure novelty rows remain lower.",
        "",
        "## Known demand sources",
        "",
    ])
    for driver in data["known_demand_drivers"].values():
        lines.append(f"- [{driver['label']}]({driver['url']})")
    lines.extend([
        "",
        "## Comparison supply source",
        "",
        "- [Nerfed AH server index](https://ah.nerfed.net/servers/base?id=7): Icecrown, Lordaeron, and Onyxia; Horde and Alliance snapshots for each realm.",
        "- Per-item quantities, market presence, scan timestamps, and direct page URLs are saved in `data/ah-collectible-demand-evidence.json`.",
        "- Nominal external gold values are neither saved nor used. This demand review changes no Quick, Target, or High price.",
        "",
        "## Promotional exclusion",
        "",
        f"Polar Bear Collar is excluded from the active guide. Its pinned route is the iCoke promotional voucher quest, there is no saved Hellscream enablement evidence, and the saved exclusion check found it in `{data['excluded_items']['22781']['external_supply']['markets_present']}` of six comparison markets.",
        "",
        "## Reproduction",
        "",
        "```powershell",
        "python scripts/review-ah-collectible-demand.py --check",
        "```",
        "",
    ])
    return "\n".join(lines)


def validate(data: dict, sections: dict | None = None) -> None:
    audit = load(AUDIT_PATH)
    expected_ids = set(audit["items"])
    if data.get("model_version") != MODEL_VERSION:
        raise ValueError("Collectible demand model is stale")
    if set(data.get("items", {})) != expected_ids:
        raise ValueError("Demand evidence does not match the active collectible inventory")
    if "22781" in data["items"]:
        raise ValueError("Promotional Polar Bear Collar must not be active demand evidence")
    if data["rules"].get("external_listings_prove_sales") is not False:
        raise ValueError("External listings must not be presented as completed sales")
    if data["rules"].get("external_prices_saved") is not False or data["rules"].get("external_prices_used") is not False:
        raise ValueError("External gold values must not enter demand evidence")
    retry = data["source_snapshots"]["external_supply"]["retry_summary"]
    if retry["initial_requests"] != (len(expected_ids) + len(PROMOTIONAL_EXCLUSIONS)) * EXPECTED_MARKETS:
        raise ValueError("Demand comparison request coverage drifted")
    if retry["final_failed_requests"] != 0:
        raise ValueError("Demand evidence has failed comparison requests")
    for item_id, record in data["items"].items():
        external = record["external_supply"]
        if external["markets_checked"] != EXPECTED_MARKETS or len(external["observations"]) != EXPECTED_MARKETS:
            raise ValueError(f"{record['name']}: comparison-market coverage drifted")
        if any("median_buyout_copper" in row for row in external["observations"]):
            raise ValueError(f"{record['name']}: external price leaked into demand evidence")
        if not record["assessment"]["demand"] or not record["assessment"]["turnover"]:
            raise ValueError(f"{record['name']}: demand assessment is incomplete")
    if set(data.get("excluded_items", {})) != {str(item_id) for item_id in PROMOTIONAL_EXCLUSIONS}:
        raise ValueError("Promotional exclusion evidence drifted")
    for record in data["excluded_items"].values():
        external = record["external_supply"]
        if external["markets_checked"] != EXPECTED_MARKETS or len(external["observations"]) != EXPECTED_MARKETS:
            raise ValueError(f"{record['name']}: promotional exclusion coverage drifted")
        if any("median_buyout_copper" in row for row in external["observations"]):
            raise ValueError(f"{record['name']}: external price leaked into exclusion evidence")
    if sections is None:
        return
    price_evidence = load(PRICE_EVIDENCE_PATH)
    catalog_by_id = {str(item["item_id"]): item for item in sections["catalog"].values()}
    if set(catalog_by_id) != expected_ids:
        raise ValueError("Applied collectible catalog does not match demand evidence")
    for item_id, record in data["items"].items():
        item = catalog_by_id[item_id]
        assessment_record = record["assessment"]
        if item["demand"] != assessment_record["demand"] or item["turnover"] != assessment_record["turnover"]:
            raise ValueError(f"{item['name']}: applied demand or turnover label drifted")
        price_band = price_evidence["items"][item_id]["proposal"]["band"]
        for band in ("quick", "target", "high"):
            if item[f"{band}_copper"] != price_band[band]:
                raise ValueError(f"{item['name']}: demand review changed the {band} price")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--refresh", action="store_true")
    group.add_argument("--reclassify", action="store_true")
    group.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if args.refresh:
        data = build_evidence()
        validate(data)
        DEMAND_EVIDENCE_PATH.write_text(
            json.dumps(data, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
            newline="\n",
        )
        REPORT_PATH.write_text(report(data), encoding="utf-8", newline="\n")
        print(json.dumps(data["summary"], indent=2))
        return 0
    if args.reclassify:
        data = reclassify_saved(load(DEMAND_EVIDENCE_PATH))
        validate(data)
        DEMAND_EVIDENCE_PATH.write_text(
            json.dumps(data, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
            newline="\n",
        )
        REPORT_PATH.write_text(report(data), encoding="utf-8", newline="\n")
        print(json.dumps(data["summary"], indent=2))
        return 0
    data = load(DEMAND_EVIDENCE_PATH)
    sections = load(SECTIONS_PATH)
    validate(data, sections)
    if REPORT_PATH.read_text(encoding="utf-8") != report(data):
        raise ValueError("Collectible demand report is stale")
    print(f"Collectible demand evidence is current for {len(data['items'])} active rows.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
