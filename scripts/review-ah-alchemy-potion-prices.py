#!/usr/bin/env python3
"""Review every auctionable Alchemy potion price with Evidence Pricing."""

from __future__ import annotations

import argparse
import concurrent.futures
import json
import re
import statistics
import sys
import urllib.error
import urllib.request
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CRAFTED_PATH = ROOT / "data" / "ah-crafted-sections.json"
RECIPE_AUDIT_PATH = ROOT / "data" / "ah-crafted-recipe-audit.json"
CROSS_SERVER_PATH = ROOT / "data" / "ah-dropped-gear-cross-server-diagnostics.json"
BASELINE_PATH = ROOT / "data" / "ah-price-baselines.json"
EVIDENCE_PATH = ROOT / "data" / "ah-alchemy-potion-price-evidence.json"
REPORT_PATH = ROOT / "docs" / "ah-alchemy-potion-pricing-review.md"
GUIDE_FILENAME = "alchemy-materials-ah-price-guide.html"
MODEL_VERSION = "alchemy-potion-evidence-pricing-v2"
MODEL_ANCHORS = {
    "Crafted Wrath combat and recovery potions": 50_000,
    "Crafted Wrath protection potions": 40_000,
    "Crafted Outland potions": 15_000,
    "Alchemist-only potions": 20_000,
    "Crafted Outland protection potions": 15_000,
    "Crafted Classic endgame potions": 10_000,
    "Crafted Classic endgame protection potions": 12_500,
    "Crafted Classic leveling potions": 2_500,
    "Crafted Classic leveling protection potions": 4_000,
}
PRICE_BANDS = ("quick", "target", "high")
USER_AGENT = "Mozilla/5.0 (compatible; HellscreamGuideEvidenceReview/1.0)"
INPUT_IDS = {
    36901: "Goldclover",
    36903: "Adder's Tongue",
    36905: "Lichbloom",
    36906: "Icethorn",
    36907: "Talandra's Rose",
    40199: "Pygmy Suckerfish",
}

SOURCE_IDS = {
    "lordaeron-horde": (14, 1),
    "lordaeron-alliance": (14, 2),
    "icecrown-horde": (15, 1),
    "icecrown-alliance": (15, 2),
    "onyxia-horde": (17, 1),
    "onyxia-alliance": (17, 2),
}

ROW_PATTERN = re.compile(
    r"<td>\s*{label}\s*</td>\s*<td>(?P<value>.*?)</td>",
    re.IGNORECASE | re.DOTALL,
)
MONEY_PATTERN = re.compile(
    r"class=['\"]currency(?P<unit>gold|silver|copper)['\"]>\s*(?P<value>[\d,]+)\s*<",
    re.IGNORECASE,
)
SCAN_PATTERN = re.compile(
    r"<td>\s*(?P<scan>20\d\d-\d\d-\d\d \d\d:\d\d:\d\d)(?:[^<]*)</td>",
    re.IGNORECASE,
)


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def merged_item(config: dict, key: str) -> dict:
    raw = config["catalog"][key]
    return config.get("catalog_defaults", {}) | config["price_profiles"][raw["profile"]] | raw


def potion_entries(config: dict) -> list[tuple[str, str]]:
    guide = config["guides"][GUIDE_FILENAME]
    entries = []
    for section in guide["sections"]:
        title = section["title"]
        if title in MODEL_ANCHORS:
            entries.extend((title, key) for key in section["items"])
    if {title for title, _ in entries} != set(MODEL_ANCHORS):
        raise ValueError("Alchemy potion sections do not match the Evidence Pricing cohorts")
    if len(entries) != len({key for _, key in entries}):
        raise ValueError("An Alchemy potion appears in more than one pricing cohort")
    return entries


def parse_money(fragment: str) -> int | None:
    values = {"gold": 0, "silver": 0, "copper": 0}
    matches = list(MONEY_PATTERN.finditer(fragment))
    if not matches:
        return None
    for match in matches:
        values[match.group("unit").casefold()] = int(match.group("value").replace(",", ""))
    return values["gold"] * 10_000 + values["silver"] * 100 + values["copper"]


def row_fragment(source: str, label: str) -> str | None:
    pattern = re.compile(ROW_PATTERN.pattern.format(label=re.escape(label)), ROW_PATTERN.flags)
    match = pattern.search(source)
    return match.group("value") if match else None


def fetch_observation(task: tuple[str, int, str, int, int, float]) -> tuple[str, int, dict]:
    source_key, item_id, name, realm_id, faction_id, scale = task
    url = (
        f"https://ah.nerfed.net/item/index?id={item_id}"
        f"&faction={faction_id}&realm={realm_id}"
    )
    last_error: Exception | None = None
    for _ in range(3):
        try:
            request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
            with urllib.request.urlopen(request, timeout=25) as response:
                charset = response.headers.get_content_charset() or "utf-8"
                source = response.read().decode(charset, errors="replace")
            median_fragment = row_fragment(source, "Median Buyout Price")
            quantity_fragment = row_fragment(source, "Quantity On AH")
            median = parse_money(median_fragment or "")
            quantity_match = re.search(r"[\d,]+", quantity_fragment or "")
            if median is None or quantity_match is None:
                return source_key, item_id, {
                    "present": False,
                    "scan_timestamp": None,
                    "quantity": 0,
                    "normalized_ask_ratio_to_current_target": None,
                    "source_url": url,
                }
            scan_match = SCAN_PATTERN.search(source)
            return source_key, item_id, {
                "present": True,
                "scan_timestamp": scan_match.group("scan") if scan_match else None,
                "quantity": int(quantity_match.group(0).replace(",", "")),
                "median_buyout_copper": median,
                "economy_scale": scale,
                "source_url": url,
            }
        except (urllib.error.URLError, TimeoutError, ValueError) as exc:
            last_error = exc
    raise RuntimeError(f"Could not fetch {name} from {source_key}: {last_error}")


def midrank_percentile(values: list[float], value: float) -> float:
    if len(values) <= 1:
        return 0.5
    below = sum(candidate < value for candidate in values)
    equal = sum(candidate == value for candidate in values)
    return (below + (equal - 1) / 2) / (len(values) - 1)


def coverage_weight(realm_count: int) -> float:
    if realm_count >= 3:
        return 1.0
    if realm_count == 2:
        return 0.75
    if realm_count == 1:
        return 0.5
    return 0.0


def round_nice(copper: float) -> int:
    """Round starter values without implying unsupported copper precision."""
    step = 500 if copper < 10_000 else 5_000
    return max(step, int(copper / step + 0.5) * step)


def starter_band(target: int, realm_count: int) -> dict[str, int]:
    if realm_count >= 3:
        quick_factor, high_factor = 0.72, 1.60
    elif realm_count == 2:
        quick_factor, high_factor = 0.68, 1.75
    else:
        quick_factor, high_factor = 0.62, 2.00
    return {
        "quick": min(target, round_nice(target * quick_factor)),
        "target": target,
        "high": max(target, round_nice(target * high_factor)),
    }


def build_evidence() -> dict:
    config = load(CRAFTED_PATH)
    recipe_audit = load(RECIPE_AUDIT_PATH)
    cross_server = load(CROSS_SERVER_PATH)
    baseline = load(BASELINE_PATH)["items"]
    entries = potion_entries(config)
    keys = [key for _, key in entries]
    cohort_by_key = {key: title for title, key in entries}
    items = {key: merged_item(config, key) for key in keys}

    tasks = []
    external_items = {
        int(item["item_id"]): item["name"] for item in items.values()
    } | INPUT_IDS
    for source_key, (realm_id, faction_id) in SOURCE_IDS.items():
        scale = float(
            cross_server["sources"][source_key]["scale"]["external_gold_per_hellscream_gold"]
        )
        for item_id, name in external_items.items():
            tasks.append(
                (
                    source_key,
                    item_id,
                    name,
                    realm_id,
                    faction_id,
                    scale,
                )
            )

    observations: dict[int, dict[str, dict]] = {item_id: {} for item_id in external_items}
    with concurrent.futures.ThreadPoolExecutor(max_workers=6) as executor:
        for source_key, item_id, observation in executor.map(fetch_observation, tasks):
            observations[item_id][source_key] = observation

    normalized_scores = {}
    realm_records = {}
    for key, item in items.items():
        item_id = int(item["item_id"])
        by_realm: dict[str, list[float]] = {}
        for source_key, observation in observations[item_id].items():
            if not observation["present"]:
                continue
            realm = cross_server["sources"][source_key]["realm"]
            by_realm.setdefault(realm, []).append(
                observation["median_buyout_copper"] / observation["economy_scale"]
            )
        normalized_by_realm = {
            realm: statistics.median(values) for realm, values in by_realm.items()
        }
        normalized_scores[key] = (
            statistics.median(normalized_by_realm.values())
            if normalized_by_realm
            else None
        )
        realm_records[key] = normalized_by_realm

    ranked_values = {
        cohort: [
            normalized_scores[key]
            for key in keys
            if cohort_by_key[key] == cohort and normalized_scores[key] is not None
        ]
        for cohort in MODEL_ANCHORS
    }
    records = {}
    for key in keys:
        item = items[key]
        item_id = int(item["item_id"])
        score = normalized_scores[key]
        realms = realm_records[key]
        cohort = cohort_by_key[key]
        raw_rank = (
            midrank_percentile(ranked_values[cohort], score)
            if score is not None
            else 0.5
        )
        weight = coverage_weight(len(realms))
        adjusted_rank = 0.5 + (raw_rank - 0.5) * weight
        band = {name: int(item[f"{name}_copper"]) for name in PRICE_BANDS}
        floor = {name: int(item["pricing_floor_copper"][name]) for name in PRICE_BANDS}
        target_ratios = [value / band["target"] for value in realms.values()]
        rank_multiplier = 0.6 + 0.8 * adjusted_rank
        proposed = starter_band(
            round_nice(MODEL_ANCHORS[cohort] * rank_multiplier),
            len(realms),
        )
        below_floor = [
            name for name in PRICE_BANDS if proposed[name] < floor[name]
        ]
        records[str(item_id)] = {
            "item_id": item_id,
            "canonical_key": key,
            "name": item["name"],
            "cohort": cohort,
            "demand": item["demand"],
            "reagent_floor": floor,
            "before_band": band,
            "proposal": {
                "proposed_band": proposed,
                "decision": "accept-reviewed-starter-estimate",
                "confidence": "fallback",
                "anchor_target_copper": MODEL_ANCHORS[cohort],
                "rank_multiplier": round(rank_multiplier, 6),
                "below_reagent_floor_bands": below_floor,
                "reason": (
                    "Reviewed low-pop starter estimate using the fixed Hellscream cohort anchor "
                    "and the gold-normalized within-cohort external rank. External gold "
                    "was not copied. Where the market estimate is below the low-confidence "
                    "reagent replacement cost, the row is sale-value guidance and a warning not "
                    "to craft from purchased inputs at the saved baseline."
                ),
            },
            "external_relative_review": {
                "realms_present": sorted(realms),
                "realm_count": len(realms),
                "faction_snapshots_present": sum(
                    observation["present"] for observation in observations[item_id].values()
                ),
                "raw_relative_rank_percentile": round(raw_rank, 6),
                "coverage_weight": weight,
                "adjusted_relative_rank_percentile": round(adjusted_rank, 6),
                "normalized_ask_ratio_to_current_target": (
                    round(statistics.median(target_ratios), 4)
                    if len(target_ratios) >= 2
                    else None
                ),
                "normalized_ratio_range": (
                    [round(min(target_ratios), 4), round(max(target_ratios), 4)]
                    if target_ratios
                    else None
                ),
                "used_to_set_gold_value": False,
            },
            "source_observations": {
                source_key: {
                    "present": observation["present"],
                    "scan_timestamp": observation["scan_timestamp"],
                    "quantity": observation["quantity"],
                    "source_url": observation["source_url"],
                }
                for source_key, observation in sorted(observations[item_id].items())
            },
            "recipe": {
                "source_spell_id": int(recipe_audit["recipes"][key]["source_spell_id"]),
                "output_count": int(recipe_audit["recipes"][key]["output_count"]),
                "reagents": recipe_audit["recipes"][key]["reagents"],
            },
        }

    input_scores = {}
    input_realms = {}
    for item_id in INPUT_IDS:
        by_realm: dict[str, list[float]] = {}
        for source_key, observation in observations[item_id].items():
            if not observation["present"]:
                continue
            realm = cross_server["sources"][source_key]["realm"]
            by_realm.setdefault(realm, []).append(
                observation["median_buyout_copper"] / observation["economy_scale"]
            )
        input_realms[item_id] = {
            realm: statistics.median(values) for realm, values in by_realm.items()
        }
        input_scores[item_id] = (
            statistics.median(input_realms[item_id].values())
            if input_realms[item_id]
            else None
        )
    ranked_inputs = [value for value in input_scores.values() if value is not None]
    input_records = {}
    for item_id, name in INPUT_IDS.items():
        current = baseline[str(item_id)]
        realms = input_realms[item_id]
        target_ratios = [value / int(current["target"]) for value in realms.values()]
        raw_rank = (
            midrank_percentile(ranked_inputs, input_scores[item_id])
            if input_scores[item_id] is not None
            else 0.5
        )
        weight = coverage_weight(len(realms))
        input_records[str(item_id)] = {
            "item_id": item_id,
            "name": name,
            "baseline_band": {band: int(current[band]) for band in PRICE_BANDS},
            "source_type": current["source_type"],
            "confidence": current["confidence"],
            "external_relative_review": {
                "realms_present": sorted(realms),
                "realm_count": len(realms),
                "faction_snapshots_present": sum(
                    observation["present"] for observation in observations[item_id].values()
                ),
                "raw_relative_rank_percentile": round(raw_rank, 6),
                "coverage_weight": weight,
                "adjusted_relative_rank_percentile": round(
                    0.5 + (raw_rank - 0.5) * weight, 6
                ),
                "normalized_ask_ratio_to_current_target": (
                    round(statistics.median(target_ratios), 4)
                    if len(target_ratios) >= 2
                    else None
                ),
                "normalized_ratio_range": (
                    [round(min(target_ratios), 4), round(max(target_ratios), 4)]
                    if target_ratios
                    else None
                ),
                "used_to_set_gold_value": False,
            },
        }

    return {
        "version": 1,
        "refreshed": date.today().isoformat(),
        "scope": "All 84 auctionable Alchemy potions in nine era/use cohorts",
        "method": "Evidence Pricing",
        "model_version": MODEL_VERSION,
        "rules": {
            "active_hellscream_listings_used_to_set_prices": False,
            "external_gold_values_copied": False,
            "external_observations_used_for_relative_rank": True,
            "reagent_floor_source": "Exact audited 3.3.5 recipes priced from the frozen non-circular Hellscream reagent baseline.",
            "gold_scale": "Same six saved Lordaeron, Icecrown, and Onyxia faction scale indexes used by the dropped-gear Evidence Pricing review.",
            "proposal_rule": "Map each coverage-weighted within-cohort rank onto its fixed Hellscream potion target anchor. Three-realm rows use 72% Quick and 160% High; sparser rows use wider bands. Reagent floors remain separate craftability diagnostics.",
        },
        "sources": {
            source_key: {
                "realm": cross_server["sources"][source_key]["realm"],
                "faction": cross_server["sources"][source_key]["faction"],
                "economy_scale": cross_server["sources"][source_key]["scale"][
                    "external_gold_per_hellscream_gold"
                ],
                "scale_snapshot_sha256": cross_server["sources"][source_key][
                    "snapshot_sha256"
                ],
                "price_source": "https://ah.nerfed.net/servers/base?id=7",
            }
            for source_key in sorted(SOURCE_IDS)
        },
        "summary": {
            "items_reviewed": len(records),
            "inputs_reviewed": len(input_records),
            "bands_changed": sum(
                record["before_band"] != record["proposal"]["proposed_band"]
                for record in records.values()
            ),
            "items_seen_on_three_realms": sum(
                record["external_relative_review"]["realm_count"] == 3
                for record in records.values()
            ),
            "external_gold_values_copied": False,
        },
        "items": records,
        "inputs": input_records,
    }


def format_money(copper: int) -> str:
    gold, remainder = divmod(int(copper), 10_000)
    silver, copper = divmod(remainder, 100)
    if gold:
        return f"{gold}g {silver}s"
    if silver:
        return f"{silver}s {copper}c"
    return f"{copper}c"


def format_band(band: dict) -> str:
    return " / ".join(format_money(int(band[name])) for name in PRICE_BANDS)


def format_ratio(value: float | None) -> str:
    return "n/a" if value is None else f"{value:.2f}x"


def render_report(evidence: dict) -> str:
    lines = [
        "# Alchemy Potion Evidence Pricing Review",
        "",
        f"- Reviewed: `{evidence['refreshed']}`",
        f"- Scope: `{evidence['scope']}`",
        f"- Items reviewed: `{evidence['summary']['items_reviewed']}`",
        f"- Buyout bands changed: `{evidence['summary']['bands_changed']}`",
        "- External gold copied into Hellscream prices: `no`",
        "- Publication status: `local only — not published`",
        "",
        "## Decision",
        "",
        "The six external faction snapshots are normalized with the same saved economy indexes "
        "used in the dropped-gear review. Their within-cohort order is mapped onto fixed "
        "Hellscream anchors for nine era/use groups; no external nominal or normalized gold value "
        "is copied. Stable three-realm rows use 72% Quick and 160% High, with wider bands when "
        "coverage is sparse.",
        "",
        "With no qualifying independent Hellscream completed-sale history for this batch, every "
        "buyout remains fallback confidence. A market estimate below the frozen low-confidence "
        "reagent floor means do not craft from purchased inputs at those saved input values; it "
        "does not rewrite the ingredient baseline. The separate bid audit removes stale "
        "hand-entered overrides.",
        "",
        "## Item decisions",
        "",
        "| Cohort | Item | Demand | Reagent floor Q / T / H | Old Q / T / H | Proposed Q / T / H | External rank | Normalized ask / old target | Coverage | Decision |",
        "|---|---|---|---:|---:|---:|---:|---:|---:|---|",
    ]
    records = sorted(
        evidence["items"].values(),
        key=lambda record: (
            -record["external_relative_review"]["adjusted_relative_rank_percentile"],
            record["name"],
        ),
    )
    for record in records:
        relative = record["external_relative_review"]
        lines.append(
            f"| {record['cohort']} | {record['name']} | {record['demand']} | {format_band(record['reagent_floor'])} | "
            f"{format_band(record['before_band'])} | "
            f"{format_band(record['proposal']['proposed_band'])} | "
            f"{relative['adjusted_relative_rank_percentile'] * 100:.1f}% | "
            f"{format_ratio(relative['normalized_ask_ratio_to_current_target'])} | "
            f"{relative['realm_count']} realms / {relative['faction_snapshots_present']} factions | "
            f"Reviewed cohort-anchor starter estimate |"
        )
    lines.extend(
        [
            "",
            "## Reagent baseline diagnostics",
            "",
            "These ratios are diagnostics only. They identify inputs whose frozen low-confidence "
            "baseline merits a separate review; they do not automatically change the baseline.",
            "",
            "| Input | Current Q / T / H | External rank | Normalized ask / target | Coverage |",
            "|---|---:|---:|---:|---:|",
        ]
    )
    for record in sorted(
        evidence["inputs"].values(),
        key=lambda row: -row["external_relative_review"]["adjusted_relative_rank_percentile"],
    ):
        relative = record["external_relative_review"]
        lines.append(
            f"| {record['name']} | {format_band(record['baseline_band'])} | "
            f"{relative['adjusted_relative_rank_percentile'] * 100:.1f}% | "
            f"{format_ratio(relative['normalized_ask_ratio_to_current_target'])} | "
            f"{relative['realm_count']} realms / {relative['faction_snapshots_present']} factions |"
        )
    lines.extend(
        [
            "",
            "## Evidence limits",
            "",
            "- The external source reports listings and listing history, not verified completed sales.",
            "- External observations set relative rank only; their gold values are not copied.",
            "- Current Hellscream listings are excluded because guide-driven auctions dominate the local scan.",
            "- Qualifying independent Hellscream completed sales may replace these fallback bands later.",
            "",
            "## Reproduction",
            "",
            "```powershell",
            "python scripts/review-ah-alchemy-potion-prices.py --check",
            "```",
            "",
            "Publishing is a separate step and is not part of this review.",
            "",
        ]
    )
    return "\n".join(lines)


def validate(evidence: dict, *, require_applied: bool) -> None:
    config = load(CRAFTED_PATH)
    keys = [key for _, key in potion_entries(config)]
    expected_ids = {str(int(merged_item(config, key)["item_id"])) for key in keys}
    if evidence.get("method") != "Evidence Pricing":
        raise ValueError("Alchemy potion evidence uses the wrong method name")
    if evidence.get("model_version") != MODEL_VERSION:
        raise ValueError("Alchemy potion evidence model is stale")
    if set(evidence.get("items", {})) != expected_ids:
        raise ValueError("Alchemy potion evidence does not match the canonical section")
    if set(evidence.get("inputs", {})) != {str(item_id) for item_id in INPUT_IDS}:
        raise ValueError("Alchemy potion input evidence is incomplete")
    rules = evidence.get("rules", {})
    if rules.get("active_hellscream_listings_used_to_set_prices") is not False:
        raise ValueError("Active Hellscream listings must not set potion prices")
    if rules.get("external_gold_values_copied") is not False:
        raise ValueError("External gold must not be copied into potion prices")
    for record in evidence["items"].values():
        item = merged_item(config, record["canonical_key"])
        current = {name: int(item[f"{name}_copper"]) for name in PRICE_BANDS}
        floors = {name: int(item["pricing_floor_copper"][name]) for name in PRICE_BANDS}
        if record["reagent_floor"] != floors:
            raise ValueError(f"{record['name']}: saved reagent floor is stale")
        proposal = record["proposal"]
        relative = record["external_relative_review"]
        cohort = record["cohort"]
        if cohort not in MODEL_ANCHORS:
            raise ValueError(f"{record['name']}: invalid potion pricing cohort")
        expected_target = round_nice(
            MODEL_ANCHORS[cohort]
            * (0.6 + 0.8 * relative["adjusted_relative_rank_percentile"])
        )
        if proposal["proposed_band"] != starter_band(
            expected_target, relative["realm_count"]
        ):
            raise ValueError(f"{record['name']}: starter proposal is not reproducible")
        if require_applied and proposal["proposed_band"] != current:
            raise ValueError(f"{record['name']}: reviewed potion price is not applied")
        if record["external_relative_review"].get("used_to_set_gold_value") is not False:
            raise ValueError(f"{record['name']}: external gold leaked into the proposal")
    baseline = load(BASELINE_PATH)["items"]
    for item_id, record in evidence["inputs"].items():
        current = baseline[item_id]
        if record["baseline_band"] != {
            band: int(current[band]) for band in PRICE_BANDS
        }:
            raise ValueError(f"{record['name']}: saved input baseline is stale")
        if record["external_relative_review"].get("used_to_set_gold_value") is not False:
            raise ValueError(f"{record['name']}: external gold leaked into input pricing")


def apply_catalog(evidence: dict) -> None:
    config = load(CRAFTED_PATH)
    source = CRAFTED_PATH.read_text(encoding="utf-8")
    reviewed_keys = {record["canonical_key"] for record in evidence["items"].values()}
    proposal_by_key = {
        record["canonical_key"]: record["proposal"]["proposed_band"]
        for record in evidence["items"].values()
    }
    for key, original in config["catalog"].items():
        updated = dict(original)
        for field in ("quick_bid_copper", "target_bid_copper", "high_bid_copper"):
            updated.pop(field, None)
        if key in reviewed_keys:
            record = next(
                row for row in evidence["items"].values()
                if row["canonical_key"] == key
            )
            updated["price_strategy"] = "evidence-pricing-market-value"
            for band in PRICE_BANDS:
                updated[f"{band}_copper"] = int(
                    record["proposal"]["proposed_band"][band]
                )
        if updated == original:
            continue
        pattern = re.compile(rf'^(    "{re.escape(key)}": )\{{.*\}}(,?)$', re.MULTILINE)
        replacement = (
            rf"\g<1>{json.dumps(updated, ensure_ascii=False, separators=(',', ':'))}\g<2>"
        )
        source, count = pattern.subn(replacement, source, count=1)
        if count != 1:
            raise ValueError(f"Could not update canonical Alchemy row: {key}")
    for section in config["guides"][GUIDE_FILENAME]["sections"]:
        if section["title"] not in MODEL_ANCHORS:
            continue
        updated_section = dict(section)
        updated_section["items"] = sorted(
            section["items"],
            key=lambda key: (
                -int(proposal_by_key[key]["target"]),
                config["catalog"][key]["name"].casefold(),
            ),
        )
        pattern = re.compile(
            r'^        \{"title": "'
            + re.escape(section["title"])
            + r'".*\}(,?)$',
            re.MULTILINE,
        )
        replacement = (
            "        "
            + json.dumps(updated_section, ensure_ascii=False)
            + r"\g<1>"
        )
        source, count = pattern.subn(replacement, source, count=1)
        if count != 1:
            raise ValueError(f"Could not reorder Alchemy section: {section['title']}")
    CRAFTED_PATH.write_text(source, encoding="utf-8", newline="\n")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--refresh", action="store_true", help="Refresh public relative-rank evidence")
    group.add_argument("--apply", action="store_true", help="Apply the saved reviewed potion prices")
    group.add_argument("--check", action="store_true", help="Validate saved evidence and report")
    args = parser.parse_args()

    if args.refresh:
        evidence = build_evidence()
        validate(evidence, require_applied=False)
        EVIDENCE_PATH.write_text(
            json.dumps(evidence, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
            newline="\n",
        )
        REPORT_PATH.write_text(render_report(evidence), encoding="utf-8", newline="\n")
        print(json.dumps(evidence["summary"], indent=2))
        return 0

    evidence = load(EVIDENCE_PATH)
    if args.apply:
        validate(evidence, require_applied=False)
        apply_catalog(evidence)
        validate(evidence, require_applied=True)
        print(f"Applied {len(evidence['items'])} reviewed Alchemy potion price bands.")
        return 0
    validate(evidence, require_applied=True)
    if REPORT_PATH.read_text(encoding="utf-8") != render_report(evidence):
        print("Alchemy potion Evidence Pricing report is stale.", file=sys.stderr)
        return 1
    print("Alchemy potion Evidence Pricing review is current.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
