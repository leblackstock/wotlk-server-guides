#!/usr/bin/env python3
"""Build and apply Evidence Pricing for the collectible AH guide."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import math
import statistics
import unicodedata
import re
from collections import Counter, defaultdict
from datetime import date, datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
AUDIT_PATH = ROOT / "data" / "ah-collectible-audit.json"
EVIDENCE_PATH = ROOT / "data" / "ah-collectible-price-evidence.json"
DEMAND_EVIDENCE_PATH = ROOT / "data" / "ah-collectible-demand-evidence.json"
SECTIONS_PATH = ROOT / "data" / "ah-collectible-sections.json"
REPORT_PATH = ROOT / "docs" / "ah-collectible-pricing-review.md"
BASELINE_PATH = ROOT / "data" / "ah-price-baselines.json"
CRAFTED_PATH = ROOT / "data" / "ah-crafted-sections.json"
VENDOR_PATH = ROOT / "data" / "ah-vendor-sections.json"
CROSS_SERVER_PATH = ROOT / "data" / "ah-dropped-gear-cross-server-diagnostics.json"
BASE_REVIEW_PATH = ROOT / "scripts" / "review-ah-blacksmithing-prices.py"
IMPORTER_PATH = ROOT / "scripts" / "import-ah-dropped-gear-evidence.py"
BEANCOUNTER_PATH = Path(
    r"D:\Hellscream WoW\launcher\WTF\Account\LEBLACKSTOCK\SavedVariables\BeanCounter.lua"
)
SCAN_PATH = Path(
    r"D:\Hellscream WoW\launcher\WTF\Account\LEBLACKSTOCK\SavedVariables\Auc-ScanData.lua"
)
MODEL_VERSION = "collectible-acquisition-evidence-pricing-v1"
PRICE_BANDS = ("quick", "target", "high")


FIXED_ANCHORS = {
    "vendor-token": {
        "target_copper": 3_500_000,
        "basis": "Reviewed 350g Hellscream starter anchor for a 40 Champion's Seal faction companion.",
    },
    "companion-drops": {
        "target_copper": 5_000_000,
        "basis": "Reviewed 500g Hellscream starter anchor for a farmed, nonstackable companion drop.",
    },
    "companion-quest-rewards": {
        "target_copper": 3_000_000,
        "basis": "Reviewed 300g Hellscream starter anchor for a tradeable quest-chain companion reward.",
    },
    "crafted-companion": {
        "target_copper": 750_000,
        "basis": "Reviewed 75g collectible-demand anchor; exact same-band recipe cost remains the minimum craftability diagnostic.",
    },
    "crafted-profession-mount": {
        "target_copper": 10_000_000,
        "basis": "Reviewed 1,000g starter anchor for a profession-restricted crafted mount; exact recipe cost remains separate.",
    },
    "crafted-motorcycle": {
        "target_copper": 180_000_000,
        "basis": "Reviewed 18,000g starter anchor for the general-use motorcycle market; exact vendor components and materials set the craft floor.",
    },
    "quest-accessories": {
        "target_copper": 100_000_000,
        "basis": "Reviewed 10,000g Hellscream starter anchor for the tradeable Shadowmourne sealed-chest reward family.",
    },
    "seasonal-companion": {
        "target_copper": 2_500_000,
        "basis": "Reviewed 250g Hellscream starter anchor for a tradeable event companion reward.",
    },
    "seasonal-apparel": {
        "target_copper": 750_000,
        "basis": "Reviewed 75g Hellscream starter anchor for tradeable event apparel and appearance demand.",
    },
    "seasonal-novelty": {
        "target_copper": 150_000,
        "basis": "Reviewed 15g Hellscream starter anchor for a tradeable event novelty without a coin or token floor.",
    },
}

TOKEN_UNIT_ANCHORS = {
    "Champion's Seal": 87_500,
    "Love Token": 20_000,
    "Noblegarden Chocolate": 10_000,
    "Burning Blossom": 20_000,
}

SEASON_ORDER = [
    "Love is in the Air",
    "Noblegarden",
    "Children's Week",
    "Midsummer Fire Festival",
    "Brewfest",
    "Hallow's End",
    "Day of the Dead",
    "Pilgrim's Bounty",
    "Winter Veil",
    "Lunar Festival",
    "Pirates' Day",
]

SECTION_SPECS = [
    ("vendor-unlimited", "Unlimited-supply vendor arbitrage", "Exact coin cost plus a documented convenience margin. These are route-and-faction arbitrage items, not scarcity plays."),
    ("vendor-limited", "Limited-supply vendor arbitrage", "True stock caps and restock timers are verified separately from unlimited vendors."),
    ("vendor-token", "Token and reputation vendors", "The token requirement is exact; the gold band is a fallback estimate because time-gated currency has no deterministic gold conversion."),
    ("crafted-companions", "Crafted companions", "Tradeable Engineering companions that do not require Engineering to use, with exact recipe floors and collectible-demand estimates."),
    ("crafted-mounts-general-use", "Crafted mounts — no profession required", "The finished motorcycles do not require Engineering to use; normal faction and Riding 150 requirements still apply."),
    ("crafted-mounts-profession-required", "Crafted mounts — profession required", "The buyer must have the listed Engineering or Tailoring rank to use these finished flying mounts."),
    ("companion-drops", "Farmed companion drops", "Pinned loot routes, wide fallback bands, and one-at-a-time posting for thin collector demand."),
    ("companion-quest-rewards", "Quest-reward companions", "Tradeable quest-chain rewards whose acquisition route is verified independently of their price."),
    ("quest-accessories", "Shadowmourne quest rewards", "Tradeable sealed-chest rewards: one mount plus vanity and appearance accessories."),
]


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load {path.name}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


BASE = load_module("ah_collectible_evidence_base", BASE_REVIEW_PATH)
IMPORTER = load_module("ah_collectible_evidence_importer", IMPORTER_PATH)


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def slug(value: str) -> str:
    value = "".join(
        character
        for character in unicodedata.normalize("NFKD", value)
        if not unicodedata.combining(character)
    )
    return re.sub(r"[^a-z0-9]+", "-", value.casefold()).strip("-")


def round_market(value: float) -> int:
    copper = max(1, int(round(value)))
    if copper < 100:
        step = 10
    elif copper < 1_000:
        step = 50
    elif copper < 10_000:
        step = 100
    elif copper < 100_000:
        step = 500
    elif copper < 1_000_000:
        step = 2_500
    elif copper < 10_000_000:
        step = 50_000
    elif copper < 100_000_000:
        step = 250_000
    else:
        step = 1_000_000
    return max(step, int(math.floor(copper / step + 0.5) * step))


def format_money(copper: int) -> str:
    if copper >= 10_000:
        copper = ((copper + 50) // 100) * 100
    gold, remainder = divmod(copper, 10_000)
    silver, copper = divmod(remainder, 100)
    parts = []
    if gold:
        parts.append(f"{gold:,}g")
    if silver:
        parts.append(f"{silver}s")
    if copper or not parts:
        parts.append(f"{copper}c")
    return " ".join(parts)


def coverage_weight(realm_count: int) -> float:
    return {3: 1.0, 2: 0.7, 1: 0.35}.get(realm_count, 0.0)


def midrank(values: list[float], value: float) -> float:
    if len(values) <= 1:
        return 0.5
    below = sum(candidate < value for candidate in values)
    equal = sum(candidate == value for candidate in values)
    return (below + (equal - 1) / 2) / (len(values) - 1)


def ranked_band(anchor: int, rank: float, realm_count: int) -> dict[str, int]:
    adjusted = 0.5 + (rank - 0.5) * coverage_weight(realm_count)
    target = round_market(anchor * (0.70 + 0.60 * adjusted))
    quick_factor, high_factor = ({3: (0.75, 1.50), 2: (0.70, 1.70)}.get(realm_count, (0.60, 2.00)))
    return {
        "quick": min(target, round_market(target * quick_factor)),
        "target": target,
        "high": max(target, round_market(target * high_factor)),
    }


def direct_sale_band(sales: dict) -> dict[str, int]:
    prices = sales["gross_unit_copper"]
    target = round_market(prices["median"])
    return {
        "quick": min(target, round_market(min(prices["q1"], target * 0.85))),
        "target": target,
        "high": max(target, round_market(max(prices["q3"], target * 1.30))),
    }


def shrink_band(direct: dict, fallback: dict, weight: float) -> dict[str, int]:
    result = {
        band: round_market(direct[band] * weight + fallback[band] * (1 - weight))
        for band in PRICE_BANDS
    }
    result["quick"] = min(result["quick"], result["target"])
    result["high"] = max(result["high"], result["target"])
    return result


def vendor_band(cost: int, *, seasonal: bool = False) -> dict[str, int]:
    if cost >= 100_000:
        target = round_market(cost * 1.25)
    elif cost >= 10_000:
        target = round_market(cost * 1.50)
    else:
        minimum = 100 if seasonal else 20_000
        target = round_market(max(minimum, cost * (5 if seasonal else 3)))
    return {"quick": cost, "target": target, "high": round_market(target * 1.50)}


def coin_cost(item: dict) -> int | None:
    vendors = [source for source in item["vendor_sources"] if source["extended_cost"] == 0]
    unit_cost = int(item["vendor_unit_cost_copper"])
    return unit_cost if vendors and unit_cost > 0 else None


def currency_parts(label: str) -> tuple[int, str]:
    match = re.fullmatch(r"(\d+) (.+)", label)
    if not match:
        raise ValueError(f"Unrecognized currency cost: {label!r}")
    count = int(match.group(1))
    currency = match.group(2)
    if currency.endswith("ies"):
        currency = currency[:-3] + "y"
    elif currency.endswith("s"):
        currency = currency[:-1]
    return count, currency


def cohort(item: dict) -> str:
    group = item["group"]
    if group == "crafted-collectibles":
        if item["kind"] == "Companion":
            return "crafted-companion"
        if item["item_id"] in {41508, 44413}:
            return "crafted-motorcycle"
        return "crafted-profession-mount"
    if item.get("season"):
        if item["kind"] == "Companion":
            family = "seasonal-companion"
        elif item["kind"] == "Cosmetic apparel":
            family = "seasonal-apparel"
        else:
            family = "seasonal-novelty"
        return f"{item['season']} | {family}"
    return group


def anchor_for(item: dict, craft_floor: dict[str, int] | None) -> tuple[int, str]:
    key = cohort(item).split(" | ")[-1]
    record = FIXED_ANCHORS[key]
    anchor = int(record["target_copper"])
    if craft_floor:
        margin = 1.08 if key == "crafted-motorcycle" else 1.25
        anchor = max(anchor, round_market(craft_floor["target"] * margin))
    return anchor, record["basis"]


def price_index() -> dict[int, dict[str, int]]:
    result = {
        int(item_id): {band: int(item[band]) for band in PRICE_BANDS}
        for item_id, item in load(BASELINE_PATH)["items"].items()
    }
    crafted = load(CRAFTED_PATH)
    defaults = crafted.get("catalog_defaults", {})
    profiles = crafted.get("price_profiles", {})
    for raw in crafted["catalog"].values():
        merged = defaults | profiles.get(raw.get("profile"), {}) | raw
        result[int(merged["item_id"])] = {
            band: int(merged[f"{band}_copper"]) for band in PRICE_BANDS
        }
    for item in load(VENDOR_PATH)["catalog"].values():
        if "vendor_cost_copper" not in item:
            continue
        cost = int(item["vendor_cost_copper"])
        target = int(item["target_copper"])
        result[int(item["item_id"])] = {
            "quick": cost,
            "target": target,
            "high": round_market(target * 1.10),
        }
    return result


def crafted_floors(audit: dict) -> dict[int, dict[str, int]]:
    prices = price_index()
    crafted_config = load(CRAFTED_PATH)
    canonical_floors = {
        int(item["item_id"]): {band: int(item["pricing_floor_copper"][band]) for band in PRICE_BANDS}
        for item in crafted_config["catalog"].values()
        if item.get("price_evidence_ref", "").startswith("data/ah-collectible-price-evidence.json#items/")
    }
    # Pet Bombling consumes Big Iron Bombs. The pinned WotLK recipe creates at
    # least two from 3 Iron Bars, 3 Heavy Blasting Powders, and 1 Silver Contact.
    prices[4394] = {
        band: math.ceil((3 * prices[3575][band] + 3 * prices[4377][band] + prices[4404][band]) / 2)
        for band in PRICE_BANDS
    }
    prices[11291] = {band: 4_500 for band in PRICE_BANDS}  # Exact unlimited-vendor cost.
    prices[34249] = {band: 1_000_000 for band in PRICE_BANDS}  # Exact Griftah cost.
    result = {}
    for item_id, item in audit["items"].items():
        recipe = item.get("crafted_recipe")
        if not recipe:
            continue
        if int(item_id) in canonical_floors:
            result[int(item_id)] = canonical_floors[int(item_id)]
            continue
        reagents = [
            {"item_id": int(reagent[0]), "count": int(reagent[1])}
            if isinstance(reagent, list) else reagent
            for reagent in recipe["reagents"]
        ]
        missing = [reagent["item_id"] for reagent in reagents if reagent["item_id"] not in prices]
        if missing:
            raise ValueError(f"{item['name']}: missing reagent prices {missing}")
        result[int(item_id)] = {
            band: math.ceil(
                sum(prices[reagent["item_id"]][band] * reagent["count"] for reagent in reagents)
                / int(recipe.get("output_count", 1))
            )
            for band in PRICE_BANDS
        }
    return result


def source_snapshot(path: Path) -> dict:
    return {
        "provided": path.is_file(),
        "sha256": hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else None,
        "modified_utc": datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc).replace(microsecond=0).isoformat() if path.is_file() else None,
        "raw_path_saved": False,
        "identity_names_saved": False,
    }


def build_evidence() -> dict:
    audit = load(AUDIT_PATH)
    items = {int(item_id): item for item_id, item in audit["items"].items()}
    floors = crafted_floors(audit)
    sales, sales_meta = BASE.load_sales(set(items))

    supply = {}
    scan_meta = {"provided": False, "listing_prices_saved": False, "listing_prices_used_to_set_baselines": False}
    if BEANCOUNTER_PATH.is_file() and SCAN_PATH.is_file():
        owned = IMPORTER.parse_characters(BEANCOUNTER_PATH, "Garrosh")
        listings, parsed = IMPORTER.parse_scan(SCAN_PATH, "Garrosh", set(items), owned)
        supply = {item_id: IMPORTER.supply_record(listings.get(item_id, [])) for item_id in items}
        scan_meta = {"provided": True, **parsed}

    comparison_items = {
        item_id: item for item_id, item in items.items()
        if item["group"] not in {"vendor-unlimited", "vendor-limited"}
        and not item.get("currency_cost")
        and coin_cost(item) is None
    }
    cross_server = load(CROSS_SERVER_PATH)
    tasks = []
    for source_key, (realm_id, faction_id) in BASE.SOURCE_IDS.items():
        scale = float(cross_server["sources"][source_key]["scale"]["external_gold_per_hellscream_gold"])
        for item_id, item in comparison_items.items():
            tasks.append((source_key, item_id, item["name"], realm_id, faction_id, scale))
    observations, retry_summary = BASE.fetch_observations_with_retries(tasks)

    realm_scores = {}
    for item_id in items:
        by_realm = defaultdict(list)
        for source_key, observation in observations.get(item_id, {}).items():
            if observation["present"]:
                realm = cross_server["sources"][source_key]["realm"]
                by_realm[realm].append(observation["median_buyout_copper"] / observation["economy_scale"])
        realm_scores[item_id] = {realm: statistics.median(values) for realm, values in by_realm.items()}
    cohort_scores = defaultdict(list)
    for item_id, item in items.items():
        if realm_scores[item_id]:
            cohort_scores[cohort(item)].append(statistics.median(realm_scores[item_id].values()))

    records = {}
    decisions = Counter()
    for item_id, item in sorted(items.items()):
        realms = realm_scores[item_id]
        score = statistics.median(realms.values()) if realms else None
        rank = midrank(cohort_scores[cohort(item)], score) if score is not None else 0.5
        cost = coin_cost(item)
        source_type = "documented-fallback"
        confidence = "fallback"
        decision = "fixed-acquisition-cohort-estimate"
        anchor = None
        anchor_basis = None
        floor = floors.get(item_id)

        if item["group"] == "vendor-unlimited" or (item.get("season") and cost is not None):
            proposal = vendor_band(cost, seasonal=bool(item.get("season")))
            anchor = cost
            anchor_basis = "Exact pinned unlimited coin-vendor cost; Target and High are deterministic convenience bands."
            source_type = "exact-unlimited-vendor-cost-plus-convenience"
            confidence = "high"
            decision = "exact-unlimited-vendor-arbitrage"
        elif item.get("currency_cost"):
            currency_label = item["currency_cost"]
            count, unit_name = currency_parts(currency_label)
            unit_anchor = TOKEN_UNIT_ANCHORS[unit_name]
            anchor = count * unit_anchor
            anchor_basis = f"Exact {currency_label} acquisition requirement with a reviewed {format_money(unit_anchor)} per-currency fallback opportunity anchor."
            proposal = ranked_band(anchor, rank, len(realms))
            decision = "exact-token-cost-plus-fallback-opportunity-anchor"
        else:
            if item["group"] == "vendor-limited":
                anchor = 80_000 if item_id == 8489 else 120_000
                anchor_basis = "Exact coin cost, stock cap, and restock timer plus a reviewed limited-route convenience anchor."
            else:
                anchor, anchor_basis = anchor_for(item, floor)
            proposal = ranked_band(anchor, rank, len(realms))

        local_sales = sales.get(item_id)
        sales_weight = None
        if local_sales:
            direct = direct_sale_band(local_sales)
            medium = (
                local_sales["completed_buyouts"] >= 4
                and local_sales["distinct_buyers"] >= 2
                and local_sales["distinct_days"] >= 2
                and local_sales["largest_buyer_unit_share"] <= 0.50
            )
            if medium:
                proposal = direct
                decision = "direct-completed-sales"
                source_type = "realized-sales-history"
                confidence = "medium"
                sales_weight = 1.0
            else:
                sales_weight = 0.25
                proposal = shrink_band(direct, proposal, sales_weight)
                decision = "sparse-completed-sales-shrunk"
                source_type = "realized-sales-history-plus-documented-fallback"
                confidence = "low"
        decisions[decision] += 1
        records[str(item_id)] = {
            "item_id": item_id,
            "name": item["name"],
            "group": item["group"],
            "season": item.get("season"),
            "kind": item["kind"],
            "cohort": cohort(item),
            "fixed_anchor": {"target_copper": anchor, "basis": anchor_basis},
            "exact_vendor_cost_copper": cost,
            "exact_currency_cost": item.get("currency_cost"),
            "exact_recipe_floor": floor,
            "local_completed_sales": local_sales,
            "current_supply": supply.get(item_id, {
                "auction_rows": 0, "units": 0, "distinct_sellers": 0,
                "largest_seller_unit_share": None, "rows_with_buyout": 0,
                "owned_account_rows_excluded": 0, "owned_account_units_excluded": 0,
                "classification": "snapshot-unavailable", "diagnostic_only": True,
            }),
            "external_relative_review": {
                "realms_present": sorted(realms),
                "realm_count": len(realms),
                "faction_snapshots_present": sum(observation["present"] for observation in observations.get(item_id, {}).values()),
                "raw_relative_rank_percentile": round(rank, 6),
                "coverage_weight": coverage_weight(len(realms)),
                "used_to_set_gold_value": False,
                "external_gold_value_copied": False,
            },
            "proposal": {
                "band": proposal,
                "source_type": source_type,
                "confidence": confidence,
                "decision": decision,
                "sales_weight": sales_weight,
                "reason": f"{anchor_basis} External observations, where present, set within-cohort rank only; active Hellscream listings did not set price.",
                "requires_large_change_review": False,
                "reviewer_decision": "accept",
            },
        }

    return {
        "version": 1,
        "reviewed": date.today().isoformat(),
        "model_version": MODEL_VERSION,
        "scope": f"All {len(records)} verified auctionable companions, mounts, collectible accessories, and seasonal novelties in the guide. Promotional and TCG mounts are excluded until direct Hellscream availability is verified.",
        "rules": {
            "active_hellscream_listing_prices_used": False,
            "external_gold_values_copied": False,
            "external_role": "Gold-normalized comparisons set relative rank only inside a fixed Hellscream acquisition cohort.",
            "comparison_retry_rule": "Initial batch plus failed-request retries after 2, 5, and 10 seconds.",
            "limited_and_unlimited_vendor_sections_separate": True,
            "seasons_rendered_separately": True,
        },
        "fixed_anchors": FIXED_ANCHORS,
        "token_unit_anchors": TOKEN_UNIT_ANCHORS,
        "source_snapshots": {
            "beancounter": {**source_snapshot(BEANCOUNTER_PATH), **sales_meta},
            "auction_scan": {**source_snapshot(SCAN_PATH), **scan_meta},
            "external_comparisons": {
                "source": "https://ah.nerfed.net/servers/base?id=7",
                "retry_summary": retry_summary,
                "nominal_gold_saved": False,
            },
        },
        "summary": {
            "items_reviewed": len(records),
            "decisions": dict(sorted(decisions.items())),
            "items_with_completed_sales": sum(bool(record["local_completed_sales"]) for record in records.values()),
            "items_present_in_current_supply_snapshot": sum(record["current_supply"]["auction_rows"] > 0 for record in records.values()),
            "items_seen_on_at_least_two_external_realms": sum(record["external_relative_review"]["realm_count"] >= 2 for record in records.values()),
            "final_failed_comparison_requests": retry_summary["final_failed_requests"],
        },
        "items": records,
    }


def source_label(item: dict) -> str:
    if item["crafted_recipe"]:
        recipe = item["crafted_recipe"]
        return f"{recipe['profession']} {recipe['skill']} craft"
    if item["currency_cost"]:
        vendors = item["vendor_sources"]
        vendor = vendors[0]["name"] if vendors else "Event vendor"
        return f"{vendor}: {item['currency_cost']}"
    if item["vendor_sources"]:
        source = item["vendor_sources"][0]
        if source["max_count"]:
            minutes = source["restock_seconds"] // 60
            return f"{source['name']}: stock {source['max_count']}, {minutes}-minute restock"
        bundle = (
            f", {item['buy_price_copper']}c per {item['buy_count']} "
            f"({item['vendor_unit_cost_copper']}c each)"
            if item["buy_count"] > 1 and item["buy_price_copper"] > 0
            else ""
        )
        return f"{source['name']}: unlimited coin vendor{bundle}"
    if item["quest_sources"]:
        quest = item["quest_sources"][0]
        return f"Quest {quest['quest_id']}: {quest['title']}"
    if item["loot_sources"]:
        evidence = item["loot_sources"].get("representative_evidence", [])
        label = evidence[0] if evidence else "Pinned loot route"
        chance = item["loot_sources"]["chance_range"]
        return f"{label}; pinned chance range {chance[0]:g}%–{chance[1]:g}%"
    return "Pinned AzerothCore acquisition route"


def catalog_from_evidence(evidence: dict) -> dict:
    audit = load(AUDIT_PATH)
    demand_evidence = load(DEMAND_EVIDENCE_PATH)
    if set(demand_evidence.get("items", {})) != set(audit["items"]):
        raise ValueError("Collectible demand evidence does not match the audited inventory")
    catalog = {}
    for item_id, record in evidence["items"].items():
        item = audit["items"][item_id]
        band = record["proposal"]["band"]
        demand_record = demand_evidence["items"][item_id]
        assessment = demand_record["assessment"]
        stack = "1" if item["max_stack"] == 1 else f"1 / {min(5, item['max_stack'])} / {item['max_stack']}"
        key = slug(item["name"])
        if key in catalog:
            existing = catalog.pop(key)
            catalog[f"{key}-{existing['item_id']}"] = existing
            key = f"{key}-{item_id}"
        catalog[key] = {
            "item_id": int(item_id),
            "name": item["name"],
            "quality": item["quality"],
            "kind": item["kind"],
            "group": item["group"],
            "season": item.get("season"),
            "binding": item["binding"],
            "required_skill_id": item["required_skill_id"],
            "required_skill_rank": item["required_skill_rank"],
            "faction": (item.get("crafted_recipe") or {}).get("faction"),
            "quick_copper": int(band["quick"]),
            "target_copper": int(band["target"]),
            "high_copper": int(band["high"]),
            "vendor_cost_copper": record["exact_vendor_cost_copper"],
            "currency_cost": record["exact_currency_cost"],
            "recipe_floor_copper": record["exact_recipe_floor"],
            "stack": stack,
            "demand": assessment["demand"],
            "demand_class": assessment["demand_class"],
            "turnover": assessment["turnover"],
            "demand_confidence": assessment["confidence"],
            "demand_rationale": assessment["rationale"],
            "external_markets_present": demand_record["external_supply"]["markets_present"],
            "external_markets_checked": demand_record["external_supply"]["markets_checked"],
            "external_units": demand_record["external_supply"]["total_units"],
            "local_completed_buyouts": (demand_record.get("local_completed_sales") or {}).get("completed_buyouts", 0),
            "demand_evidence_ref": f"data/ah-collectible-demand-evidence.json#items/{item_id}",
            "source": source_label(item),
            "notes": record["proposal"]["reason"],
            "price_strategy": "evidence-pricing-market-value",
            "price_evidence_ref": f"data/ah-collectible-price-evidence.json#items/{item_id}",
            "canonical_owner": item["canonical_owner"],
        }
    return catalog


def sections_from_catalog(catalog: dict) -> list[dict]:
    by_group = defaultdict(list)
    by_season = defaultdict(list)
    for key, item in catalog.items():
        if item["season"]:
            by_season[item["season"]].append(key)
        else:
            by_group[item["group"]].append(key)
    sections = []
    for section_id, title, description in SECTION_SPECS:
        audience = None
        if section_id == "crafted-companions":
            keys = [key for key in by_group["crafted-collectibles"] if catalog[key]["kind"] == "Companion"]
            audience = "general-use"
        elif section_id == "crafted-mounts-general-use":
            keys = [key for key in by_group["crafted-collectibles"] if catalog[key]["kind"] == "Mount" and catalog[key]["required_skill_id"] == 762]
            audience = "general-use"
        elif section_id == "crafted-mounts-profession-required":
            keys = [key for key in by_group["crafted-collectibles"] if catalog[key]["kind"] == "Mount" and catalog[key]["required_skill_id"] in {197, 202}]
            audience = "profession-restricted"
        else:
            keys = by_group[section_id]
        keys.sort(key=lambda key: (-catalog[key]["target_copper"], catalog[key]["name"].casefold()))
        section = {"id": section_id, "title": title, "description": description, "items": keys}
        if audience:
            section["audience"] = audience
        sections.append(section)
    for season in SEASON_ORDER:
        keys = by_season[season]
        keys.sort(key=lambda key: (-catalog[key]["target_copper"], catalog[key]["name"].casefold()))
        sections.append({
            "id": f"season-{slug(season)}",
            "title": season,
            "description": "A separate event market. Event access is acquisition evidence, not proof of a scarcity premium.",
            "items": keys,
            "empty_reason": None if keys else "No verified auctionable companion, mount, or in-scope accessory row was found for this event. BoP and temporary rewards remain excluded.",
        })
    return sections


def build_sections(evidence: dict) -> dict:
    catalog = catalog_from_evidence(evidence)
    return {
        "version": 1,
        "source": {
            "audit": "data/ah-collectible-audit.json",
            "price_evidence": "data/ah-collectible-price-evidence.json",
            "demand_evidence": "data/ah-collectible-demand-evidence.json",
        },
        "pricing_unit": "per item",
        "catalog": catalog,
        "sections": sections_from_catalog(catalog),
    }


def report(evidence: dict) -> str:
    summary = evidence["summary"]
    retry = evidence["source_snapshots"]["external_comparisons"]["retry_summary"]
    lines = [
        "# Companions, Mounts & Accessories AH Pricing Review",
        "",
        f"- Review date: `{evidence['reviewed']}`",
        f"- Items reviewed: `{summary['items_reviewed']}`",
        f"- Qualified or sparse Hellscream completed-sale histories: `{summary['items_with_completed_sales']}`",
        f"- Present in current Hellscream supply after owned-account exclusion: `{summary['items_present_in_current_supply_snapshot']}`",
        f"- Seen on at least two comparison realms: `{summary['items_seen_on_at_least_two_external_realms']}`",
        f"- Comparison requests: `{retry['initial_requests']}` initial / `{retry['final_failed_requests']}` final failures after the 2-, 5-, and 10-second retry rule",
        "",
        "## Decision",
        "",
        "Active Hellscream listings were used only as supply diagnostics and never set or raised a price. Exact unlimited-vendor costs, stock caps, restock timers, token quantities, and crafted recipe floors are recorded independently. Completed sales take priority when they pass the evidence gate. With only one sparse completed sale in this batch, nearly all non-vendor prices remain clearly labeled fallback estimates.",
        "",
        "## Evidence hierarchy used",
        "",
        "1. Exact unlimited coin-vendor cost or deterministic recipe floor.",
        "2. Qualified Hellscream completed buyouts.",
        "3. Sparse completed buyouts shrunk toward a fixed acquisition-cohort anchor.",
        "4. Fixed Hellscream acquisition-cohort anchor, with cross-server observations used only for within-cohort relative rank.",
        "",
        "## Saved fixed anchors",
        "",
        "| Cohort | Target anchor | Basis |",
        "|---|---:|---|",
    ]
    for key, item in FIXED_ANCHORS.items():
        lines.append(f"| {key} | {format_money(item['target_copper'])} | {item['basis']} |")
    lines.extend([
        "",
        "## Local completed-sale result",
        "",
        "Wood Frog Box has one valid 20g completed buyout from one buyer on one day. It remains low confidence and receives 25% weight; the reviewed limited-vendor fallback receives 75%. No other included item has a valid completed buyout in the saved BeanCounter snapshot.",
        "",
        "## Limits",
        "",
        "- Comparison-realm pages report asks, not completed sales. Their nominal gold values are not saved or copied.",
        "- A token requirement proves acquisition cost, but not a gold conversion; token-priced rows remain fallback confidence.",
        "- The promotional Polar Bear Collar and promotional/TCG mounts are excluded until direct Hellscream availability is verified; a generic base-database quest or loot route is not proof that the rewards are enabled on this server.",
        "- The saved 336-request price snapshot predates removal of Polar Bear Collar and includes its six zero-result comparison checks. The active 127-item pricing records exclude it; the separate demand snapshot covers exactly the active scope.",
        "- Shadowmourne reward prices are discovery bands for a thin market, not verified current values.",
        "- Limited and unlimited vendors remain separate because a stock cap and restock timer materially change arbitrage risk.",
        "- Every holiday is rendered separately, including explicit empty in-scope sections where only BoP, temporary, or unverified rewards exist.",
        "",
        "## Reproduction",
        "",
        "```powershell",
        "python scripts/review-ah-collectible-prices.py --check",
        "```",
        "",
        "Publishing is a separate step and is not part of this review.",
        "",
    ])
    return "\n".join(lines)


def validate(evidence: dict, sections: dict | None = None) -> None:
    audit = load(AUDIT_PATH)
    if evidence.get("model_version") != MODEL_VERSION:
        raise ValueError("Collectible Evidence Pricing model is stale")
    expected_items = len(audit["items"])
    if len(evidence.get("items", {})) != expected_items or set(evidence["items"]) != set(audit["items"]):
        raise ValueError(f"Collectible evidence must cover all {expected_items} audited items")
    if evidence["rules"].get("active_hellscream_listing_prices_used") is not False:
        raise ValueError("Active Hellscream listings must not set collectible prices")
    if evidence["rules"].get("external_gold_values_copied") is not False:
        raise ValueError("External gold values must not be copied")
    for record in evidence["items"].values():
        band = record["proposal"]["band"]
        if not band["quick"] <= band["target"] <= band["high"]:
            raise ValueError(f"{record['name']}: invalid price band")
        if record["external_relative_review"].get("used_to_set_gold_value") is not False:
            raise ValueError(f"{record['name']}: external gold leaked into price")
    if sections:
        if len(sections["catalog"]) != expected_items:
            raise ValueError(f"Collectible catalog must contain {expected_items} rows")
        season_titles = [section["title"] for section in sections["sections"] if section["id"].startswith("season-")]
        if season_titles != SEASON_ORDER:
            raise ValueError("Season sections are missing or out of order")
        for section in sections["sections"]:
            targets = [sections["catalog"][key]["target_copper"] for key in section["items"]]
            if targets != sorted(targets, reverse=True):
                raise ValueError(f"{section['title']}: rows are not target-price sorted")
        demand_evidence = load(DEMAND_EVIDENCE_PATH)
        demand_by_id = demand_evidence["items"]
        for item in sections["catalog"].values():
            item_id = str(item["item_id"])
            assessment = demand_by_id[item_id]["assessment"]
            if item["demand"] != assessment["demand"] or item["turnover"] != assessment["turnover"]:
                raise ValueError(f"{item['name']}: applied demand evidence drifted")
            proposal = evidence["items"][item_id]["proposal"]["band"]
            if any(item[f"{band}_copper"] != proposal[band] for band in PRICE_BANDS):
                raise ValueError(f"{item['name']}: demand apply changed a price")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--refresh", action="store_true", help="Fetch evidence and save the review snapshot only.")
    parser.add_argument("--apply", action="store_true", help="Apply the saved evidence to collectible section data and report.")
    parser.add_argument("--check", action="store_true", help="Validate saved evidence and applied section data.")
    args = parser.parse_args()
    if sum((args.refresh, args.apply, args.check)) != 1:
        parser.error("Choose exactly one of --refresh, --apply, or --check")
    if args.refresh:
        evidence = build_evidence()
        validate(evidence)
        EVIDENCE_PATH.write_text(json.dumps(evidence, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
        print(f"Saved collectible evidence for {len(evidence['items'])} items.")
        return 0
    evidence = load(EVIDENCE_PATH)
    if args.apply:
        sections = build_sections(evidence)
        validate(evidence, sections)
        SECTIONS_PATH.write_text(json.dumps(sections, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
        REPORT_PATH.write_text(report(evidence), encoding="utf-8", newline="\n")
        print(f"Applied collectible Evidence Pricing to {len(sections['catalog'])} rows and {len(sections['sections'])} sections.")
        return 0
    sections = load(SECTIONS_PATH)
    validate(evidence, sections)
    expected_report = report(evidence)
    if REPORT_PATH.read_text(encoding="utf-8") != expected_report:
        raise ValueError("Collectible pricing report is stale")
    print("Collectible pricing evidence, sections, and report are current.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
