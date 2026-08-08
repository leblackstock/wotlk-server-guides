#!/usr/bin/env python3
"""Review the first gathering/material AH batch with Evidence Pricing."""

from __future__ import annotations

import argparse
import concurrent.futures
import hashlib
import html
import importlib.util
import json
import math
import re
import statistics
import sys
import unicodedata
import urllib.error
import urllib.request
from collections import Counter, defaultdict
from datetime import date, datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
GUIDES_DIR = ROOT / "guides"
BASELINE_PATH = ROOT / "data" / "ah-price-baselines.json"
CRAFTED_PATH = ROOT / "data" / "ah-crafted-sections.json"
VENDOR_PATH = ROOT / "data" / "ah-vendor-sections.json"
CONTAINER_AUDIT_PATH = ROOT / "data" / "ah-container-audit.json"
ITEM_IDS_PATH = ROOT / "assets" / "ah-item-ids.js"
CROSS_SERVER_PATH = ROOT / "data" / "ah-dropped-gear-cross-server-diagnostics.json"
IMPORTER_PATH = ROOT / "scripts" / "import-ah-dropped-gear-evidence.py"
EVIDENCE_PATH = ROOT / "data" / "ah-gathering-material-price-evidence.json"
REPORT_PATH = ROOT / "docs" / "ah-gathering-material-pricing-review.md"
PHASE_1A_EVIDENCE_PATH = ROOT / "data" / "ah-gathering-material-price-evidence.json"
GUIDE_FILES = (
    "mining-smithing-ah-price-guide.html",
    "herbalism-herbs-ah-price-guide.html",
    "cross-profession-materials-ah-price-guide.html",
)
PRICE_BANDS = ("quick", "target", "high")
MODEL_VERSION = "gathering-material-evidence-pricing-v2"
ACTIVE_PHASE = "phase1a"
INCLUDED_SECTIONS: dict[str, set[str]] | None = None
EXPECTED_COUNTS: tuple[int, int] | None = (198, 189)
EXCLUDED_ITEM_NAMES: set[str] = set()
USER_AGENT = "Mozilla/5.0 (compatible; HellscreamGuideEvidenceReview/1.0)"

SOURCE_IDS = {
    "lordaeron-horde": (14, 1),
    "lordaeron-alliance": (14, 2),
    "icecrown-horde": (15, 1),
    "icecrown-alliance": (15, 2),
    "onyxia-horde": (17, 1),
    "onyxia-alliance": (17, 2),
}

# The gold scale comes from frozen Hellscream cohort anchors, while current
# external observations affect within-cohort order only. Anchors are copper per
# item and remain fixed until direct Hellscream evidence replaces them.
COHORTS = {
    "Mining: Northrend common ore": (7_500, (36909, 36912)),
    "Mining: Outland common ore": (3_250, (23424, 23425)),
    "Mining: Outland rare ore": (36_500, (23426, 23427)),
    "Mining: Classic common ore": (1_000, (2770, 2771, 2772, 3858, 10620)),
    "Mining: Classic rare ore": (5_500, (2775, 2776, 7911)),
    "Mining: low and mid stone": (500, (2835, 2836, 2838)),
    "Mining: high stone": (1_150, (7912, 12365)),
    "Herbalism: high Northrend herbs": (50_000, (36903, 36905, 36906)),
    "Herbalism: common Northrend herbs": (
        16_000,
        (36901, 36904, 36907, 37921, 39970),
    ),
    "Herbalism: high Outland herbs": (
        20_000,
        (22788, 22789, 22790, 22791, 22792, 22793),
    ),
    "Herbalism: common Outland herbs": (10_000, (22785, 22786, 22787)),
    "Herbalism: Classic endgame herbs": (
        17_500,
        (8845, 8846, 13463, 13464, 13465, 13466, 13467),
    ),
    "Herbalism: Classic mid-high herbs": (8_000, (4625, 8831, 8836, 8838, 8839)),
    "Herbalism: Classic mid herbs": (
        7_500,
        (2452, 3355, 3356, 3357, 3358, 3369, 3818, 3820, 3821),
    ),
    "Herbalism: Classic starter herbs": (2_250, (765, 785, 2447, 2449, 2450, 2453)),
    "Shared: Northrend quest mojos": (30_000, (35799, 35836, 36743, 36758, 38303)),
    "Shared: Eternals": (70_000, (35622, 35623, 35624, 35625, 35627, 36860)),
    "Shared: Primals": (40_000, (21884, 21885, 21886, 22451, 22452, 22456, 22457)),
    "Shared: Outland pearls": (12_500, (24478, 24479)),
    "Shared: Classic raw elementals": (3_750, (7067, 7068, 7069, 7070)),
    "Shared: Classic essences": (27_500, (7076, 7078, 7080, 7082, 12803, 12808)),
    "Shared: Classic secondary elementals": (6_000, (7075, 7077, 7079, 7081)),
    "Shared: Molten Core cores": (35_000, (17010, 17011)),
    "Shared: Classic ordinary pearls": (13_750, (5498, 5500, 7971, 4611)),
    "Shared: Classic mojos": (9_000, (8151, 8152, 12804, 19943)),
    "Crafted materials: Wrath base bars": (13_250, (36913, 36916)),
    "Crafted materials: Outland base bars": (20_000, (23445, 23446, 23447)),
    "Crafted materials: Outland premium bars": (142_500, (23448, 23449, 23573)),
    "Crafted materials: Classic common bars": (
        3_000,
        (2840, 2841, 3575, 3576, 3859, 3860, 12359),
    ),
    "Crafted materials: Classic rare bars": (10_000, (2842, 3577, 6037)),
    "Crafted materials: low grinding stones": (2_000, (3470, 3478, 3486)),
    "Crafted materials: high grinding stones": (5_500, (7966, 12644)),
    "Crafted materials: Classic rod blanks": (30_000, (6338, 11128, 11144)),
    "Crafted materials: Outland rod blanks": (92_500, (25843, 25844, 25845)),
}

# These forms have an exact reversible ten-to-one relationship in 3.3.5.
DERIVED_TEN_TO_ONE = {
    37702: 36860,
    37700: 35623,
    37705: 35622,
    37704: 35625,
    37703: 35627,
    37701: 35624,
    22574: 21884,
    22572: 22451,
    22576: 22457,
    22578: 21885,
    22575: 21886,
    22577: 22456,
    22573: 22452,
}
DERIVED_THREE_TO_ONE: dict[int, int] = {}

PHASE_1B_GUIDE_FILES = (
    "enchanting-mats-ah-price-guide.html",
    "jewelcrafting-gems-ah-price-guide.html",
    "tailoring-cloth-ah-price-guide.html",
    "skinning-leatherworking-materials-ah-price-guide.html",
    "fishing-cooking-materials-ah-price-guide.html",
    "alchemy-materials-ah-price-guide.html",
    "inscription-materials-ah-price-guide.html",
    "engineering-materials-ah-price-guide.html",
    "blacksmithing-materials-ah-price-guide.html",
)

PHASE_1B_INCLUDED_SECTIONS = {
    "enchanting-mats-ah-price-guide.html": {
        "Northrend / WotLK mats — 375–450",
        "Outland / TBC mats — 300–375",
        "Classic / old-world mats — 1–300",
    },
    "jewelcrafting-gems-ah-price-guide.html": {
        "Epic Northrend gems",
        "Meta gems / popular cut metas",
        "Jewelcrafter-only Dragon's Eye",
        "Rare Northrend gems",
        "Uncommon Northrend gems / Icy Prism materials",
        "Prospecting ore / JC input ore",
        "Outland / TBC gems and meta bases",
        "Classic / old-world gems",
    },
    "tailoring-cloth-ah-price-guide.html": {
        "Wrath cloth intermediates",
        "Outland cloth intermediates",
        "Classic cloth intermediates",
        "Tailoring-relevant extra reagents",
        "Cloth drops",
        "Spider silks / market-priced tailoring supplies",
        "Vendor & convenience items",
    },
    "skinning-leatherworking-materials-ah-price-guide.html": {
        "Northrend skinning materials",
        "Wrath Leatherworking reagent overlap",
        "Outland / TBC skinning materials",
        "Classic leather",
        "Classic hides",
        "Classic specialty scales",
        "Wrath leather intermediates",
        "Outland leather intermediates",
        "Classic leather intermediates",
        "Salt drops / curing materials",
        "Vendor & convenience items",
    },
    "fishing-cooking-materials-ah-price-guide.html": {
        "Northrend raw fish",
        "Northrend meats / cooking mats",
        "Outland / Classic raw and quest fish",
        "Outland / Classic meats / eggs / odd cooking mats",
        "Rare catches / pearls / clam value",
        "Vendor & convenience items",
    },
    "alchemy-materials-ah-price-guide.html": {
        "Northrend herbs / Alchemy materials",
        "Northrend Eternals / transmute inputs",
        "Outland / TBC Alchemy materials",
        "Classic Alchemy materials",
        "Crafted Wrath oils and intermediates",
        "Crafted Outland intermediates and transmutes",
        "Crafted Classic oils and intermediates",
        "Vendor & convenience items",
    },
    "inscription-materials-ah-price-guide.html": {
        "Northrend inks / pigments / card inputs",
        "Classic and Outland inks / pigments",
        "Enchanter-only blank vellums",
        "Vendor & convenience items",
    },
    "engineering-materials-ah-price-guide.html": {
        "Northrend raw Engineering inputs",
        "Outland raw Engineering inputs",
        "Raw stone inputs",
        "Practical raw metal bars",
        "Practical cloth / leather / gem inputs",
        "Vendor & convenience items",
    },
    "blacksmithing-materials-ah-price-guide.html": {
        "High-end craft bottlenecks / Wrath premium inputs",
        "Wrath leveling / common BS inputs",
        "Outland / TBC Blacksmithing inputs",
        "Classic bars / old-world metals",
        "Raw stone",
        "Practical non-metal overlap",
        "Vendor & convenience items",
    },
}

# Phase 1B keeps its gold scale in explicit, frozen Hellscream material-family
# anchors. Current external observations may rank items inside these cohorts,
# but their nominal gold values never become Hellscream guide prices.
PHASE_1B_COHORTS = {
    "Enchanting: Wrath dust": (18_000, (34054,)),
    "Enchanting: Outland dust": (7_500, (22445,)),
    "Enchanting: Strange Dust": (300, (10940,)),
    "Enchanting: Soul Dust": (1_000, (11083,)),
    "Enchanting: Classic mid and high dust": (2_500, (11137, 11176, 16204)),
    "Enchanting: Wrath greater essence": (80_000, (34055,)),
    "Enchanting: Outland greater essence": (45_000, (22446,)),
    "Enchanting: Classic low greater essences": (3_500, (10939, 11082)),
    "Enchanting: Classic mid greater essences": (18_000, (11135, 11175)),
    "Enchanting: Classic high greater essence": (85_000, (16203,)),
    "Enchanting: Wrath shards": (80_000, (34053, 34052)),
    "Enchanting: Wrath crystal": (300_000, (34057,)),
    "Enchanting: Outland shards": (50_000, (22448, 22449)),
    "Enchanting: Outland crystal": (60_000, (22450,)),
    "Enchanting: Classic glimmering shards": (3_000, (10978, 11084)),
    "Enchanting: Classic glowing shards": (8_000, (11138, 11139)),
    "Enchanting: Classic high shards": (30_000, (11177, 11178, 14343, 14344)),
    "Enchanting: Classic crystal": (50_000, (20725,)),
    "Jewelcrafting: Wrath epic gems": (700_000, (36919, 36922, 36931, 36928, 36925, 36934)),
    "Jewelcrafting: Wrath meta bases": (250_000, (41334, 41266)),
    "Jewelcrafting: Dragon's Eye": (950_000, (42225,)),
    "Jewelcrafting: Wrath rare gems": (100_000, (36918, 36921, 36930, 36924, 36927, 36933)),
    "Jewelcrafting: Wrath uncommon gems": (10_000, (36923, 36917, 36932, 36929, 36926, 36920)),
    "Jewelcrafting: Outland meta bases": (350_000, (25868, 25867)),
    "Jewelcrafting: Outland rare gems": (25_000, (23436, 23440, 23439, 23438, 23441, 23437)),
    "Jewelcrafting: Outland uncommon gems": (2_500, (23077, 23112, 23117, 21929, 23107, 23079)),
    "Jewelcrafting: Classic high gems": (25_000, (12800, 12364, 12361, 12799, 7910)),
    "Jewelcrafting: Classic mid gems": (7_500, (7909, 1206, 1705, 1529, 3864)),
    "Jewelcrafting: Classic starter gems": (1_000, (1210, 818, 774)),
    "Tailoring: Wrath cooldown cloth": (350_000, (41595, 41594, 41593)),
    "Tailoring: Wrath imbued bolt": (95_000, (41511,)),
    "Tailoring: Wrath basic bolt": (26_000, (41510,)),
    "Tailoring: Outland cooldown cloth": (180_000, (24271, 24272, 21845)),
    "Tailoring: Outland specialty bolts": (70_000, (21844, 21842)),
    "Tailoring: Outland basic bolt": (7_000, (21840,)),
    "Tailoring: Classic mooncloth": (60_000, (14342,)),
    "Tailoring: Classic high bolts": (5_500, (4339, 14048)),
    "Tailoring: Classic mid bolts": (3_000, (2997, 4305)),
    "Tailoring: Bolt of Linen Cloth": (500, (2996,)),
    "Tailoring: Wrath cloth": (4_500, (33470,)),
    "Tailoring: Outland cloth": (1_000, (21877,)),
    "Tailoring: Classic special cloth": (10_000, (14256,)),
    "Tailoring: Classic high cloth": (1_000, (14047, 4338)),
    "Tailoring: Classic mid cloth": (700, (4306, 2592)),
    "Tailoring: Linen Cloth": (200, (2589,)),
    "Tailoring: Wrath spider silk": (40_000, (42253,)),
    "Tailoring: Outland spider silk": (20_000, (21881,)),
    "Tailoring: Classic spider silks": (12_000, (14227, 4337, 10285, 3182)),
    "Leatherworking: Wrath rare fur": (400_000, (44128,)),
    "Leatherworking: Wrath scales and chitin": (40_000, (38558, 38557, 38561)),
    "Leatherworking: Wrath scraps": (1_500, (33567,)),
    "Leatherworking: Outland rare skins": (30_000, (29539, 25707, 25708, 29547, 29548, 25700)),
    "Leatherworking: Outland scraps": (1_000, (25649,)),
    "Leatherworking: Classic scraps": (200, (2934,)),
    "Leatherworking: Rugged Hide": (17_500, (8171,)),
    "Leatherworking: Thick Hide": (10_000, (8169,)),
    "Leatherworking: Heavy Hide": (5_000, (4235,)),
    "Leatherworking: Medium Hide": (3_500, (4232,)),
    "Leatherworking: Light Hide": (2_000, (783,)),
    "Leatherworking: Classic specialty scales": (12_000, (15416, 6470, 7392, 8167)),
    "Leatherworking: Heavy Borean Leather": (65_000, (38425,)),
    "Leatherworking: Borean Leather": (8_500, (33568,)),
    "Leatherworking: Heavy Knothide Leather": (32_000, (23793,)),
    "Leatherworking: Knothide Leather": (6_000, (21887,)),
    "Leatherworking: Rugged leather and hide": (50_000, (15407, 8170)),
    "Leatherworking: Thick leather and hide": (18_000, (8172, 4304)),
    "Leatherworking: Heavy leather and hide": (7_000, (4234, 4236)),
    "Leatherworking: Medium leather and hide": (4_000, (2319, 4233)),
    "Leatherworking: Light leather and hide": (1_500, (2318, 4231)),
    "Leatherworking: Deeprock Salt": (10_000, (8150,)),
    "Cooking: Northrend fish": (15_000, (41807, 45909, 41806, 41809, 41813, 41802, 40199, 41808, 41810, 41805, 41803, 41812)),
    "Cooking: Northern Spices": (30_000, (43007,)),
    "Cooking: Northrend meats": (9_000, (43013, 43012, 43010, 43009, 34736, 43011, 36782)),
    "Cooking: Outland fish": (9_000, (27439, 27515, 27516, 27438, 27435, 27429, 33824, 33823, 27425, 27437, 27422)),
    "Cooking: Deviate Fish": (20_000, (6522,)),
    "Cooking: Classic endgame fish": (12_000, (13755, 13888, 13422, 13889, 13759, 13893, 13756, 13760, 13754, 13758, 13757)),
    "Cooking: Classic mid fish": (6_500, (21153, 4603, 6359, 21071, 6358, 8365)),
    "Cooking: Classic starter fish": (3_000, (6362, 6308, 6361, 6289)),
    "Cooking: Outland meats": (7_500, (27678, 31671, 31670, 27682, 27674, 27681, 27677, 27671, 24477)),
    "Cooking: Classic rare ingredients": (20_000, (21024, 18255, 20424)),
    "Cooking: Small Egg": (10_000, (6889,)),
    "Cooking: Classic high ingredients": (6_000, (12208, 12207, 7974, 3712, 12184, 3685, 35562, 12037, 12203, 12204, 12202, 4655)),
    "Cooking: Classic mid ingredients": (4_000, (3667, 3731, 723, 3730, 3404, 12205, 1015, 5504, 5470, 1081, 2251, 1468, 2924, 2677, 1080, 5051)),
    "Cooking: Classic starter ingredients": (2_500, (3173, 5467, 2674, 2675, 5469)),
    "Fishing: Siren's Tear": (180_000, (36784,)),
    "Fishing: Northsea Pearl": (25_000, (36783,)),
    "Alchemy: Wrath oils": (22_500, (44958, 40195)),
    "Alchemy: Mercurial Stone": (110_000, (31080,)),
    "Alchemy: Gurubashi Mojo Madness": (185_000, (19931,)),
    "Alchemy: Classic premium oils and dye": (60_000, (3824, 3829, 9210)),
    "Alchemy: Classic common oils": (18_000, (8956, 9061, 6371, 13423, 6370)),
    "Inscription: Wrath common ink and pigment": (25_000, (43126, 39343)),
    "Inscription: Wrath rare ink and pigment": (90_000, (43127, 43109)),
    "Inscription: Outland common ink and pigment": (8_000, (43124, 39342)),
    "Inscription: Outland rare ink and pigment": (25_000, (43125, 43108)),
    "Inscription: Classic common inks": (5_000, (43123, 43120, 43118, 43116, 39774, 39469)),
    "Inscription: Classic rare inks": (12_000, (43122, 43121, 43119, 43117, 43115)),
    "Inscription: rank III vellums": (60_000, (43146, 43145)),
}

PHASE_1B_DERIVED_THREE_TO_ONE = {
    34056: 34055,
    22447: 22446,
    10938: 10939,
    10998: 11082,
    11134: 11135,
    11174: 11175,
    16202: 16203,
}


def configure_phase(phase: str) -> None:
    global ACTIVE_PHASE, GUIDE_FILES, INCLUDED_SECTIONS, EXPECTED_COUNTS
    global EVIDENCE_PATH, REPORT_PATH, MODEL_VERSION
    global EXCLUDED_ITEM_NAMES, COHORTS, DERIVED_TEN_TO_ONE, DERIVED_THREE_TO_ONE
    ACTIVE_PHASE = phase
    if phase == "phase1a":
        return
    GUIDE_FILES = PHASE_1B_GUIDE_FILES
    INCLUDED_SECTIONS = PHASE_1B_INCLUDED_SECTIONS
    EXPECTED_COUNTS = None
    EXCLUDED_ITEM_NAMES = {"Dark Herring", "Sea Turtle", "Giant Sewer Rat"}
    EVIDENCE_PATH = ROOT / "data" / "ah-profession-material-price-evidence.json"
    REPORT_PATH = ROOT / "docs" / "ah-profession-material-pricing-review.md"
    MODEL_VERSION = "profession-material-evidence-pricing-v1"
    COHORTS = PHASE_1B_COHORTS
    DERIVED_TEN_TO_ONE = {}
    DERIVED_THREE_TO_ONE = PHASE_1B_DERIVED_THREE_TO_ONE

ROW_PATTERN = re.compile(r"<tr[^>]*>.*?</tr>", re.DOTALL)
ITEM_PATTERN = re.compile(
    r'<td[^>]*data-column="item"[^>]*>.*?<strong[^>]*>(.*?)</strong>',
    re.DOTALL,
)
SECTION_OR_ROW = re.compile(r"<h2[^>]*>(.*?)</h2>|(<tr[^>]*>.*?</tr>)", re.DOTALL)
ROW_VALUE = re.compile(
    r"<td>\s*{label}\s*</td>\s*<td>(?P<value>.*?)</td>",
    re.IGNORECASE | re.DOTALL,
)
MONEY_TOKEN = re.compile(r"([\d,]+)\s*(Gold|Silver|Copper)", re.IGNORECASE)
CURRENCY_SPAN = re.compile(
    r"class=['\"]currency(?P<unit>gold|silver|copper)['\"][^>]*>\s*"
    r"(?P<value>[\d,]+)\s*</span>",
    re.IGNORECASE,
)
SCAN_PATTERN = re.compile(
    r"<td>\s*(?:Data Fetched at|Scan date:)\s*</td>\s*"
    r"<td>\s*(?P<scan>[^<]+)",
    re.IGNORECASE,
)


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def normalize(value: str) -> str:
    value = "".join(
        character
        for character in unicodedata.normalize("NFKD", value)
        if unicodedata.category(character) != "Mn"
    )
    value = value.casefold().replace("'", "").replace("’", "")
    value = value.replace("&", " and ")
    return " ".join(re.sub(r"[^a-z0-9]+", " ", value).split())


def clean_text(value: str) -> str:
    text = " ".join(html.unescape(re.sub(r"<[^>]+>", " ", value)).split())
    return text.replace("↑ Top", "").strip()


def load_item_ids() -> dict[str, int]:
    source = ITEM_IDS_PATH.read_text(encoding="utf-8")
    match = re.search(r"window\.AH_ITEM_IDS=(\{.*?\});\n", source, re.DOTALL)
    if not match:
        raise RuntimeError("Could not parse AH item IDs")
    return {key: int(value) for key, value in json.loads(match.group(1)).items()}


def merged_catalog(config: dict) -> dict[int, tuple[str, dict]]:
    merged = {}
    for key, raw in config["catalog"].items():
        item = config.get("catalog_defaults", {}) | config["price_profiles"][raw["profile"]] | raw
        merged[int(item["item_id"])] = (key, item)
    return merged


def money_from_html(value: str) -> int:
    total = 0
    clean = clean_text(value)
    for amount, unit in re.findall(r"([\d,]+)\s*([gsc])", clean):
        total += int(amount.replace(",", "")) * {"g": 10_000, "s": 100, "c": 1}[unit]
    return total


def row_band(row: str) -> dict[str, int]:
    result = {}
    for band in PRICE_BANDS:
        match = re.search(
            rf'<div class="pricepair {band}">.*?<span class="buyout">(.*?)</span>',
            row,
            re.DOTALL,
        )
        if match:
            result[band] = money_from_html(match.group(1))
    return result


def inventory() -> dict[int, dict]:
    item_ids = load_item_ids()
    baseline = load(BASELINE_PATH)["items"]
    container_vendor_ids = {
        int(item_id)
        for item_id, item in load(CONTAINER_AUDIT_PATH)["items"].items()
        if item["primary_source"] == "vendor"
    }
    crafted_config = load(CRAFTED_PATH)
    crafted = merged_catalog(crafted_config)
    vendors = {
        int(record["item_id"]): (key, record)
        for key, record in load(VENDOR_PATH)["catalog"].items()
    }
    records: dict[int, dict] = {}
    occurrences = 0
    for filename in GUIDE_FILES:
        source = (GUIDES_DIR / filename).read_text(encoding="utf-8")
        section = ""
        for match in SECTION_OR_ROW.finditer(source):
            if match.group(1) is not None:
                section = clean_text(match.group(1))
                continue
            row = match.group(2)
            if (
                INCLUDED_SECTIONS is not None
                and section not in INCLUDED_SECTIONS.get(filename, set())
            ):
                continue
            if "pricepair target" not in row:
                continue
            item_match = ITEM_PATTERN.search(row)
            if not item_match:
                continue
            name = clean_text(item_match.group(1))
            if name in EXCLUDED_ITEM_NAMES:
                continue
            item_id = item_ids.get(normalize(name))
            if not item_id:
                raise ValueError(f"Could not resolve item ID for {name}")
            if item_id in container_vendor_ids:
                continue
            occurrences += 1
            catalog_entry = crafted.get(item_id)
            if item_id in vendors:
                owner = "vendor"
                canonical_key = vendors[item_id][0]
                canonical = vendors[item_id][1]
            elif catalog_entry and catalog_entry[1].get("price_strategy") != "shared-market-reference":
                owner = "crafted"
                canonical_key, canonical = catalog_entry
            elif str(item_id) in baseline:
                owner = "baseline"
                canonical_key = str(item_id)
                canonical = baseline[str(item_id)]
            else:
                raise ValueError(f"No canonical price owner for {name} ({item_id})")
            canonical_band = (
                {band: int(canonical[f"{band}_copper"]) for band in PRICE_BANDS}
                if owner == "crafted"
                else {band: int(canonical[band]) for band in PRICE_BANDS}
                if owner == "baseline"
                else {"target": int(canonical["target_copper"])}
            )
            record = records.setdefault(
                item_id,
                {
                    "item_id": item_id,
                    "name": name,
                    "owner": owner,
                    "canonical_key": canonical_key,
                    "before_band": canonical_band,
                    "source_type": canonical.get("source_type"),
                    "confidence": canonical.get("confidence"),
                    "before_reason": canonical.get("reason"),
                    "occurrences": [],
                    "pricing_floor_before": (
                        canonical.get("pricing_floor_copper") if owner == "crafted" else None
                    ),
                },
            )
            if record["before_band"] != canonical_band:
                raise ValueError(f"Duplicate canonical bands disagree for {name}")
            record["occurrences"].append({"guide": filename, "section": section})
    if EXPECTED_COUNTS is not None and (occurrences, len(records)) != EXPECTED_COUNTS:
        raise ValueError(
            f"{ACTIVE_PHASE} inventory drifted: {occurrences} occurrences, "
            f"{len(records)} unique items"
        )
    return records


def row_fragment(source: str, label: str) -> str | None:
    pattern = re.compile(ROW_VALUE.pattern.format(label=re.escape(label)), ROW_VALUE.flags)
    match = pattern.search(source)
    return match.group("value") if match else None


def parse_money(value: str) -> int | None:
    span_matches = list(CURRENCY_SPAN.finditer(value))
    if span_matches:
        values = {"gold": 0, "silver": 0, "copper": 0}
        for match in span_matches:
            values[match.group("unit").casefold()] = int(
                match.group("value").replace(",", "")
            )
        return values["gold"] * 10_000 + values["silver"] * 100 + values["copper"]
    matches = list(MONEY_TOKEN.finditer(clean_text(value)))
    if not matches:
        return None
    values = {"gold": 0, "silver": 0, "copper": 0}
    for match in matches:
        values[match.group(2).casefold()] = int(match.group(1).replace(",", ""))
    return values["gold"] * 10_000 + values["silver"] * 100 + values["copper"]


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
    return source_key, item_id, {
        "present": False,
        "scan_timestamp": None,
        "quantity": 0,
        "source_url": url,
        "fetch_failed": True,
        "error_type": type(last_error).__name__ if last_error else "unknown",
    }


def weighted_quantile(rows: list[dict], fraction: float) -> int | None:
    weighted = sorted((int(row["unit_price"]), int(row["stack"])) for row in rows)
    total = sum(weight for _, weight in weighted)
    if total <= 0:
        return None
    threshold = max(1, math.ceil(total * fraction))
    seen = 0
    for value, weight in weighted:
        seen += weight
        if seen >= threshold:
            return value
    return weighted[-1][0]


def load_sales(path: Path | None, item_ids: set[int]) -> tuple[dict[int, dict], dict]:
    if path is None:
        return {}, {
            "provided": False,
            "raw_path_saved": False,
            "known_friend_or_guild_exclusions_available": False,
        }
    spec = importlib.util.spec_from_file_location("ah_sales_importer", IMPORTER_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("Could not load the sanitized BeanCounter importer")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    sales, summary = module.parse_beancounter(path, "Garrosh", item_ids)
    sanitized = {}
    for item_id, rows in sales.items():
        if not rows:
            continue
        buyer_units = Counter()
        days = set()
        for row in rows:
            buyer_units[row["buyer"]] += int(row["stack"])
            days.add(row["day"])
        units = sum(buyer_units.values())
        max_share = max(buyer_units.values(), default=0) / units if units else None
        gate = (
            "medium"
            if units >= 20
            and len(rows) >= 4
            and len(buyer_units) >= 2
            and len(days) >= 2
            and (max_share or 0) <= 0.5
            else "low"
        )
        sanitized[item_id] = {
            "completed_buyouts": len(rows),
            "units": units,
            "distinct_buyers": len(buyer_units),
            "distinct_days": len(days),
            "largest_buyer_unit_share": round(max_share, 4) if max_share is not None else None,
            "price_summary_copper": {
                "min": weighted_quantile(rows, 0.0),
                "q1": weighted_quantile(rows, 0.25),
                "median": weighted_quantile(rows, 0.5),
                "q3": weighted_quantile(rows, 0.75),
                "max": weighted_quantile(rows, 1.0),
            },
            "confidence_gate": gate,
        }
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    source = {
        "provided": True,
        "sha256": digest,
        "modified_utc": datetime.fromtimestamp(
            path.stat().st_mtime, tz=timezone.utc
        ).replace(microsecond=0).isoformat(),
        "records_seen_for_batch_items": summary["records_seen_for_catalog_items"],
        "valid_completed_buyouts": summary["valid_completed_buyouts"],
        "excluded_records": summary["excluded_records"],
        "owned_character_exclusions_available": summary[
            "owned_character_exclusions_available"
        ],
        "known_friend_or_guild_exclusions_available": False,
        "raw_path_saved": False,
        "buyer_names_saved": False,
    }
    return sanitized, source


def midrank_percentile(values: list[float], value: float) -> float:
    if len(values) <= 1:
        return 0.5
    below = sum(candidate < value for candidate in values)
    equal = sum(candidate == value for candidate in values)
    return (below + (equal - 1) / 2) / (len(values) - 1)


def round_market(copper: float) -> int:
    value = max(1, int(round(copper)))
    if value < 100:
        step = 10
    elif value < 1_000:
        step = 50
    elif value < 10_000:
        step = 100
    elif value < 100_000:
        step = 500
    elif value < 1_000_000:
        step = 2_500
    else:
        step = 50_000
    return max(step, int(math.floor(value / step + 0.5) * step))


def direct_sale_proposal(sales: dict) -> dict[str, int]:
    summary = sales["price_summary_copper"]
    target = round_market(int(summary["median"]))
    quick = round_market(min(int(summary["q1"]), target * 0.85))
    high = round_market(max(int(summary["q3"]), target * 1.35))
    return {"quick": min(quick, target), "target": target, "high": max(high, target)}


def shrink_sparse_sale(
    direct: dict[str, int], fallback: dict[str, int], direct_weight: float
) -> dict[str, int]:
    blended = {
        band: round_market(
            int(direct[band]) * direct_weight
            + int(fallback[band]) * (1.0 - direct_weight)
        )
        for band in PRICE_BANDS
    }
    blended["quick"] = min(blended["quick"], blended["target"])
    blended["high"] = max(blended["high"], blended["target"])
    return blended


def rank_model_proposal(anchor: int, rank: float, realms: int) -> dict[str, int]:
    reliability = {3: 1.0, 2: 0.7, 1: 0.35}.get(realms, 0.0)
    adjusted_rank = 0.5 + (rank - 0.5) * reliability
    target = round_market(anchor * (0.65 + 0.70 * adjusted_rank))
    if realms >= 3:
        quick_factor, high_factor = 0.75, 1.50
    elif realms == 2:
        quick_factor, high_factor = 0.70, 1.70
    else:
        quick_factor, high_factor = 0.60, 2.00
    quick = round_market(target * quick_factor)
    high = round_market(target * high_factor)
    return {"quick": min(quick, target), "target": target, "high": max(high, target)}


def evidence_reason(record: dict, proposal: dict) -> str:
    decision = proposal["decision"]
    if decision == "direct-completed-sales":
        sales = record["local_completed_sales"]
        return (
            f"Reviewed completed Hellscream buyouts: {sales['units']} units across "
            f"{sales['completed_buyouts']} auctions, {sales['distinct_buyers']} buyers, "
            f"and {sales['distinct_days']} UTC days. Largest-buyer share is "
            f"{sales['largest_buyer_unit_share']:.1%}; confidence remains "
            f"{proposal['confidence']}. Current listings were not used."
        )
    if decision == "sparse-completed-sales-shrunk":
        sales = record["local_completed_sales"]
        return (
            f"Reviewed {sales['completed_buyouts']} completed Hellscream buyout covering "
            f"{sales['units']} units, but the evidence came from only "
            f"{sales['distinct_buyers']} buyer on {sales['distinct_days']} UTC day. The "
            f"direct-sale band therefore receives only {proposal['direct_weight']:.0%} "
            f"weight and is shrunk toward the fixed {proposal['cohort']} cohort estimate. "
            "Confidence remains low; current listings were not used."
        )
    if decision == "deterministic-ten-to-one":
        return (
            f"Exact reversible 10:1 conversion from {proposal['parent_name']}; each band "
            "is one tenth of the reviewed parent material band."
        )
    if decision == "deterministic-three-to-one":
        return (
            f"Exact reversible 3:1 conversion from {proposal['parent_name']}; each band "
            "is one third of the reviewed parent essence band."
        )
    if decision == "cohort-rank-starter-estimate":
        review = record["external_relative_review"]
        return (
            f"Reviewed fallback Evidence Pricing estimate using the fixed "
            f"{proposal['cohort']} Hellscream anchor. Current external observations set "
            f"within-cohort rank only ({review['rank_percentile']:.1%}); "
            f"{review['realm_coverage']} realm coverage controls band width. No external "
            "gold or active Hellscream ask was copied."
        )
    if decision == "exact-vendor":
        return "Exact vendor/convenience policy retained; no market model applied."
    if decision == "inherit-phase1a":
        return record.get("before_reason") or (
            "Retained from the completed Phase 1A material review without collecting or "
            "applying a second market estimate."
        )
    return (
        "Reviewed and retained because no qualifying direct sales or defensible comparable "
        "cohort supports replacing the saved band. External data is diagnostic only."
    )


def build_evidence(beancounter: Path | None) -> dict:
    records = inventory()
    cross_server = load(CROSS_SERVER_PATH)
    inherited_evidence = (
        load(PHASE_1A_EVIDENCE_PATH) if ACTIVE_PHASE == "phase1b" else {"items": {}}
    )
    inherited_ids = set(records) & {int(item_id) for item_id in inherited_evidence["items"]}
    review_item_ids = {
        item_id
        for item_id, record in records.items()
        if record["owner"] != "vendor" and item_id not in inherited_ids
    }
    sales, sales_source = load_sales(beancounter, review_item_ids)
    tasks = []
    for source_key, (realm_id, faction_id) in SOURCE_IDS.items():
        scale = float(
            cross_server["sources"][source_key]["scale"][
                "external_gold_per_hellscream_gold"
            ]
        )
        for item_id, record in records.items():
            if record["owner"] == "vendor" or item_id in inherited_ids:
                continue
            tasks.append(
                (source_key, item_id, record["name"], realm_id, faction_id, scale)
            )
    observations: dict[str, dict[int, dict]] = defaultdict(dict)
    with concurrent.futures.ThreadPoolExecutor(max_workers=16) as executor:
        for source_key, item_id, observation in executor.map(fetch_observation, tasks):
            observations[source_key][item_id] = observation

    scores = {}
    realm_scores: dict[int, dict[str, float]] = {}
    for item_id, record in records.items():
        by_realm: dict[str, list[float]] = defaultdict(list)
        if record["owner"] != "vendor" and item_id not in inherited_ids:
            for source_key in SOURCE_IDS:
                observation = observations[source_key][item_id]
                if not observation.get("present"):
                    continue
                realm = cross_server["sources"][source_key]["realm"]
                by_realm[realm].append(
                    observation["median_buyout_copper"]
                    / observation["economy_scale"]
                )
        realm_scores[item_id] = {
            realm: statistics.median(values) for realm, values in by_realm.items()
        }
        if realm_scores[item_id]:
            scores[item_id] = statistics.median(realm_scores[item_id].values())

    cohort_by_item = {}
    rank_by_item = {}
    for cohort, (anchor, item_ids) in COHORTS.items():
        available = [scores[item_id] for item_id in item_ids if item_id in scores]
        for item_id in item_ids:
            if item_id in cohort_by_item:
                raise ValueError(f"Item {item_id} belongs to more than one cohort")
            cohort_by_item[item_id] = (cohort, anchor)
            rank_by_item[item_id] = (
                midrank_percentile(available, scores[item_id])
                if item_id in scores and available
                else 0.5
            )

    if ACTIVE_PHASE == "phase1b":
        derived_ids = set(DERIVED_TEN_TO_ONE) | set(DERIVED_THREE_TO_ONE)
        missing_cohorts = sorted(review_item_ids - set(cohort_by_item) - derived_ids)
        if missing_cohorts:
            missing = ", ".join(
                f"{records[item_id]['name']} ({item_id})" for item_id in missing_cohorts
            )
            raise ValueError(f"Phase 1B items lack reviewed cohorts: {missing}")

    proposals = {}
    for item_id, record in records.items():
        if record["owner"] == "vendor":
            proposal = {
                "proposed_band": record["before_band"],
                "decision": "exact-vendor",
                "source_type": "coin-vendor",
                "confidence": "high",
            }
        elif item_id in inherited_ids:
            proposal = {
                "proposed_band": record["before_band"],
                "decision": "inherit-phase1a",
                "source_type": record.get("source_type") or "documented-fallback",
                "confidence": record.get("confidence") or "fallback",
                "inherited_evidence_ref": (
                    "data/ah-gathering-material-price-evidence.json#items/" + str(item_id)
                ),
            }
        elif item_id in sales:
            direct = direct_sale_proposal(sales[item_id])
            if (
                ACTIVE_PHASE == "phase1b"
                and sales[item_id]["confidence_gate"] == "low"
                and item_id in cohort_by_item
            ):
                cohort, anchor = cohort_by_item[item_id]
                fallback = rank_model_proposal(
                    anchor, rank_by_item[item_id], len(realm_scores[item_id])
                )
                direct_weight = (
                    0.25
                    if sales[item_id]["distinct_buyers"] == 1
                    or sales[item_id]["distinct_days"] == 1
                    else 0.50
                )
                proposal = {
                    "proposed_band": shrink_sparse_sale(
                        direct, fallback, direct_weight
                    ),
                    "decision": "sparse-completed-sales-shrunk",
                    "source_type": "realized-sales-history-plus-documented-fallback",
                    "confidence": "low",
                    "cohort": cohort,
                    "anchor_target_copper": anchor,
                    "direct_weight": direct_weight,
                }
            else:
                proposal = {
                    "proposed_band": direct,
                    "decision": "direct-completed-sales",
                    "source_type": "realized-sales-history",
                    "confidence": sales[item_id]["confidence_gate"],
                }
        elif item_id in DERIVED_TEN_TO_ONE or item_id in DERIVED_THREE_TO_ONE:
            continue
        elif item_id in cohort_by_item:
            cohort, anchor = cohort_by_item[item_id]
            proposal = {
                "proposed_band": rank_model_proposal(
                    anchor, rank_by_item[item_id], len(realm_scores[item_id])
                ),
                "decision": "cohort-rank-starter-estimate",
                "source_type": "documented-fallback",
                "confidence": "fallback",
                "cohort": cohort,
                "anchor_target_copper": anchor,
            }
        else:
            proposal = {
                "proposed_band": record["before_band"],
                "decision": "retain-reviewed-band",
                "source_type": record.get("source_type") or "documented-fallback",
                "confidence": record.get("confidence") or "fallback",
            }
        proposals[item_id] = proposal

    for child_id, parent_id in DERIVED_TEN_TO_ONE.items():
        if child_id not in records:
            continue
        parent = proposals[parent_id]
        proposals[child_id] = {
            "proposed_band": {
                band: max(1, round(parent["proposed_band"][band] / 10))
                for band in PRICE_BANDS
            },
            "decision": "deterministic-ten-to-one",
            "source_type": "deterministic-conversion",
            "confidence": parent["confidence"],
            "parent_item_id": parent_id,
            "parent_name": records[parent_id]["name"],
        }

    for child_id, parent_id in DERIVED_THREE_TO_ONE.items():
        if child_id not in records:
            continue
        parent = proposals[parent_id]
        proposals[child_id] = {
            "proposed_band": {
                band: max(1, round(parent["proposed_band"][band] / 3))
                for band in PRICE_BANDS
            },
            "decision": "deterministic-three-to-one",
            "source_type": "deterministic-conversion",
            "confidence": parent["confidence"],
            "parent_item_id": parent_id,
            "parent_name": records[parent_id]["name"],
        }

    output_items = {}
    for item_id, record in records.items():
        stripped_observations = {}
        if record["owner"] != "vendor" and item_id not in inherited_ids:
            for source_key in SOURCE_IDS:
                raw = observations[source_key][item_id]
                stripped_observations[source_key] = {
                    key: value
                    for key, value in raw.items()
                    if key not in {"median_buyout_copper", "economy_scale"}
                }
        external_review = {
            "realm_coverage": len(realm_scores[item_id]),
            "faction_observations": sum(
                1
                for source_key in SOURCE_IDS
                if observations.get(source_key, {}).get(item_id, {}).get("present")
            ),
            "rank_percentile": round(rank_by_item.get(item_id, 0.5), 4),
            "used_to_set_relative_rank": item_id in cohort_by_item
            and item_id not in sales
            and item_id not in DERIVED_TEN_TO_ONE
            and item_id not in DERIVED_THREE_TO_ONE
            and item_id not in inherited_ids,
            "used_to_set_gold_value": False,
        }
        record = record | {
            "pricing_unit": "per item",
            "measured_acquisition_evidence": None,
            "local_completed_sales": sales.get(item_id),
            "external_relative_review": external_review,
            "source_observations": stripped_observations,
            "proposal": proposals[item_id],
        }
        old_target = int(record["before_band"]["target"])
        new_target = int(record["proposal"]["proposed_band"]["target"])
        record["proposal"]["target_change_copper"] = new_target - old_target
        record["proposal"]["target_change_percent"] = round(
            (new_target / old_target - 1) * 100, 2
        )
        if record["proposal"]["decision"] == "retain-reviewed-band":
            record["proposal"]["reviewer_decision"] = "retain fallback"
        else:
            record["proposal"]["reviewer_decision"] = "accept"
        if abs(record["proposal"]["target_change_percent"]) > 50:
            if record["proposal"]["decision"] == "direct-completed-sales":
                record["proposal"]["reviewer_note"] = (
                    "Accepted after manual large-change review because the sanitized "
                    "Hellscream completed-sale median supports the move; confidence remains "
                    "low because buyer concentration fails the medium gate."
                )
            elif record["proposal"]["decision"] == "sparse-completed-sales-shrunk":
                record["proposal"]["reviewer_note"] = (
                    "Revised after manual large-change review: the one-buyer sale is recorded, "
                    "but receives only 25% weight while the three-realm cohort fallback carries "
                    "the remaining weight. Confidence remains low."
                )
            else:
                record["proposal"]["reviewer_note"] = (
                    "Accepted after manual large-change review because the item has broad "
                    "three-realm relative-rank coverage inside its fixed Hellscream cohort; "
                    "the result remains a fallback estimate."
                )
        review_reason = evidence_reason(record, record["proposal"])
        record["proposal"]["review_reason"] = review_reason
        record["proposal"]["reason"] = (
            record.get("before_reason")
            if record["proposal"]["decision"] == "retain-reviewed-band"
            and record.get("before_reason")
            else review_reason
        )
        output_items[str(item_id)] = record

    changed = sum(
        record["before_band"] != record["proposal"]["proposed_band"]
        for record in output_items.values()
        if record["owner"] != "vendor"
    )
    decision_counts = Counter(
        record["proposal"]["decision"] for record in output_items.values()
    )
    return {
        "version": 1,
        "refreshed": date.today().isoformat(),
        "method": "Evidence Pricing",
        "model_version": MODEL_VERSION,
        "scope": {
            "phase": ACTIVE_PHASE,
            "label": (
                "Mining, Herbalism, and Shared Crafting Materials"
                if ACTIVE_PHASE == "phase1a"
                else "Profession material sections across nine AH guides"
            ),
            "guides": list(GUIDE_FILES),
            "occurrences": sum(len(record["occurrences"]) for record in records.values()),
            "unique_items": len(records),
            "publishing_status": "local only — not published",
        },
        "rules": {
            "active_hellscream_listing_prices_used": False,
            "external_gold_values_copied": False,
            "external_role": "Within-cohort relative rank only.",
            "gold_scale": "Fixed frozen Hellscream cohort anchors or direct completed sales.",
            "materials_medium_gate": "At least 20 units, four completed auctions, two buyers, and two UTC days, with largest-buyer unit share at most 0.50.",
            "deterministic_forms": (
                "Crystallized/Eternal and Mote/Primal forms preserve exact reversible "
                "10:1 parity in Phase 1A; lesser/greater enchanting essences preserve "
                "exact reversible 3:1 parity in Phase 1B."
            ),
        },
        "cohorts": {
            cohort: {"anchor_target_copper": anchor, "item_ids": list(item_ids)}
            for cohort, (anchor, item_ids) in COHORTS.items()
        },
        "sources": {
            "local_completed_sales": sales_source,
            "external": {
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
        },
        "summary": {
            "items_reviewed": len(output_items),
            "bands_changed": changed,
            "direct_sale_items": len(sales),
            "inherited_phase1a_items": len(inherited_ids),
            "items_seen_on_three_realms": sum(
                record["external_relative_review"]["realm_coverage"] == 3
                for record in output_items.values()
            ),
            "target_changes_over_fifty_percent": sum(
                abs(record["proposal"]["target_change_percent"]) > 50
                for record in output_items.values()
                if record["owner"] != "vendor"
            ),
            "decision_counts": dict(sorted(decision_counts.items())),
            "external_gold_values_copied": False,
        },
        "items": output_items,
    }


def format_money(copper: int) -> str:
    copper = int(copper)
    if copper >= 10_000:
        silver_total = (copper + 50) // 100
        gold, silver = divmod(silver_total, 100)
        return f"{gold:,}g" + (f" {silver}s" if silver else "")
    silver, remainder = divmod(copper, 100)
    return f"{silver}s" + (f" {remainder}c" if remainder else "")


def format_band(band: dict[str, int]) -> str:
    if set(band) == {"target"}:
        return format_money(int(band["target"])) + " exact vendor"
    return " / ".join(format_money(int(band[key])) for key in PRICE_BANDS)


def render_report(evidence: dict) -> str:
    summary = evidence["summary"]
    phase1b = evidence["scope"].get("phase") == "phase1b"
    lines = [
        (
            "# Profession Material Evidence Pricing Review"
            if phase1b
            else "# Gathering and Material Evidence Pricing Review"
        ),
        "",
        f"- Reviewed: `{evidence['refreshed']}`",
        f"- Scope: `{evidence['scope'].get('label', 'Mining, Herbalism, and Shared Crafting Materials')}`",
        f"- Unique items reviewed: `{summary['items_reviewed']}`",
        *(
            [f"- Items inherited from Phase 1A: `{summary.get('inherited_phase1a_items', 0)}`"]
            if phase1b
            else []
        ),
        f"- Proposed bands changed: `{summary['bands_changed']}`",
        f"- Items with completed-sale evidence: `{summary['direct_sale_items']}`",
        f"- Items seen on all three comparison realms: `{summary['items_seen_on_three_realms']}`",
        f"- Manually reviewed Target changes over 50%: `{summary['target_changes_over_fifty_percent']}`",
        "- External gold copied into Hellscream prices: `no`",
        f"- Publication status: `{evidence['scope']['publishing_status']}`",
        "",
        "## Decision",
        "",
        (
            "The review uses sanitized Hellscream completed buyouts first. Current Hellscream listing prices are excluded. Six external faction observations are normalized with the saved economy indexes and set within-cohort rank only; fixed frozen Hellscream anchors set the gold scale. Lesser and greater enchanting essences remain locked at the exact reversible 3:1 ratio."
            if phase1b
            else "The review uses sanitized Hellscream completed buyouts first. Current Hellscream listing prices are excluded. Six external faction observations are normalized with the saved economy indexes and set within-cohort rank only; fixed frozen Hellscream anchors set the gold scale. Exact reversible elemental conversions remain locked at 10:1."
        ),
        "",
        "All rank-modeled values remain fallback confidence. Direct sales remain low unless they pass the material volume, auction, buyer, day, and concentration gate. Crafted outputs keep their recipe cost as a separate craftability diagnostic; a market band does not promise that buying inputs and crafting will be profitable.",
        "",
        "## Item decisions",
        "",
        "| Guide / Section | Item | Owner | Old Q / T / H | Proposed Q / T / H | Target change | Local sales | External coverage | Decision | Confidence | Review |",
        "|---|---|---|---:|---:|---:|---:|---:|---|---|---|",
    ]
    records = list(evidence["items"].values())
    records.sort(
        key=lambda record: (
            record["occurrences"][0]["guide"],
            record["occurrences"][0]["section"],
            -record["proposal"]["proposed_band"]["target"],
            record["name"],
        )
    )
    for record in records:
        first = record["occurrences"][0]
        sales = record.get("local_completed_sales")
        sales_label = (
            f"{sales['units']}u / {sales['completed_buyouts']} auctions"
            if sales
            else "none"
        )
        coverage = record["external_relative_review"]
        lines.append(
            "| "
            + " | ".join(
                [
                    f"{first['guide']}<br>{first['section']}",
                    record["name"].replace("|", "\\|"),
                    record["owner"],
                    format_band(record["before_band"]),
                    format_band(record["proposal"]["proposed_band"]),
                    f"{record['proposal']['target_change_percent']:+.2f}%",
                    sales_label,
                    f"{coverage['realm_coverage']} realms / {coverage['faction_observations']} factions",
                    record["proposal"]["decision"],
                    record["proposal"]["confidence"],
                    record["proposal"]["reviewer_decision"],
                ]
            )
            + " |"
        )
    lines.extend(
        [
            "",
            "## Manual review of Target changes over 50%",
            "",
        ]
    )
    large_changes = [
        record
        for record in records
        if record["owner"] != "vendor"
        and abs(record["proposal"]["target_change_percent"]) > 50
    ]
    large_changes.sort(
        key=lambda record: abs(record["proposal"]["target_change_percent"]),
        reverse=True,
    )
    for record in large_changes:
        proposal = record["proposal"]
        lines.append(
            f"- **{record['name']}:** {format_money(record['before_band']['target'])} "
            f"→ {format_money(proposal['proposed_band']['target'])} "
            f"({proposal['target_change_percent']:+.2f}%). "
            f"Decision: `{proposal['reviewer_decision']}`. "
            f"{proposal['reviewer_note']}"
        )
    lines.extend(
        [
            "",
            "## Review notes",
            "",
            "- Every changed Target over 50% is visible in the complete table above and remains fallback unless direct Hellscream sales support it.",
            "- Exact coin-vendor rows are retained and excluded from the market-rank model.",
            "- Singleton and non-comparable rare materials retain their reviewed saved bands rather than being forced into a weak cohort.",
            "- The saved evidence contains source URLs, scan timestamps, quantities, coverage, cohort anchors, and sanitized local sale aggregates, but no buyer names, seller names, local source paths, or external nominal prices.",
            "",
        ]
    )
    return "\n".join(lines)


def compact_catalog_object(record: dict) -> str:
    return json.dumps(record, ensure_ascii=False, separators=(",", ":"))


def apply_proposals(evidence: dict) -> None:
    baseline_doc = load(BASELINE_PATH)
    baseline = baseline_doc["items"]
    crafted_doc = load(CRAFTED_PATH)
    crafted_source = CRAFTED_PATH.read_text(encoding="utf-8")
    for item_id, record in evidence["items"].items():
        if record["owner"] == "vendor" or record["proposal"]["decision"] == "inherit-phase1a":
            continue
        proposal = record["proposal"]
        band = proposal["proposed_band"]
        if item_id in baseline:
            current = dict(baseline[item_id])
            for price_band in PRICE_BANDS:
                current[price_band] = int(band[price_band])
            current["source_type"] = proposal["source_type"]
            current["confidence"] = proposal["confidence"]
            current["reason"] = proposal["reason"]
            current["evidence_ref"] = (
                EVIDENCE_PATH.relative_to(ROOT).as_posix() + "#items/" + item_id
            )
            baseline[item_id] = current
        if record["owner"] == "baseline":
            continue
        key = record["canonical_key"]
        original = crafted_doc["catalog"][key]
        updated = dict(original)
        for price_band in PRICE_BANDS:
            updated[f"{price_band}_copper"] = int(band[price_band])
            updated.pop(f"{price_band}_bid_copper", None)
        updated["price_strategy"] = "evidence-pricing-market-value"
        updated["price_evidence_ref"] = (
            EVIDENCE_PATH.relative_to(ROOT).as_posix() + "#items/" + item_id
        )
        pattern = re.compile(rf'^(    "{re.escape(key)}": )\{{.*\}}(,?)$', re.MULTILINE)
        replacement = rf"\g<1>{compact_catalog_object(updated)}\g<2>"
        crafted_source, count = pattern.subn(replacement, crafted_source, count=1)
        if count != 1:
            raise ValueError(f"Could not update canonical catalog line for {key}")
    BASELINE_PATH.write_text(
        json.dumps(baseline_doc, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    CRAFTED_PATH.write_text(crafted_source, encoding="utf-8", newline="\n")


def validate(evidence: dict, *, require_applied: bool) -> None:
    current_inventory = inventory()
    blacksmithing_successors = {}
    blacksmithing_path = ROOT / "data" / "ah-blacksmithing-price-evidence.json"
    if blacksmithing_path.exists():
        blacksmithing_successors = load(blacksmithing_path).get("items", {})
    if evidence.get("method") != "Evidence Pricing":
        raise ValueError("Gathering/material evidence uses the wrong method")
    if evidence.get("model_version") != MODEL_VERSION:
        raise ValueError("Gathering/material evidence model is stale")
    if set(evidence.get("items", {})) != {str(item_id) for item_id in current_inventory}:
        raise ValueError("Gathering/material evidence does not match the guide inventory")
    if evidence["rules"].get("active_hellscream_listing_prices_used") is not False:
        raise ValueError("Active Hellscream listing prices leaked into the review")
    if evidence["summary"].get("external_gold_values_copied") is not False:
        raise ValueError("External nominal gold leaked into the review")
    for item_id, record in evidence["items"].items():
        proposal = record["proposal"]
        band = proposal["proposed_band"]
        if record["owner"] == "vendor":
            if set(band) != {"target"} or int(band["target"]) <= 0:
                raise ValueError(f"{record['name']}: invalid exact-vendor price")
            continue
        if not int(band["quick"]) <= int(band["target"]) <= int(band["high"]):
            raise ValueError(f"{record['name']}: invalid proposal order")
        if record["external_relative_review"].get("used_to_set_gold_value") is not False:
            raise ValueError(f"{record['name']}: external gold leaked into proposal")
        if record.get("local_completed_sales"):
            forbidden = {"buyer", "seller", "buyers", "sellers", "path"}
            if forbidden & set(record["local_completed_sales"]):
                raise ValueError(f"{record['name']}: private sales identity leaked")
        if (
            proposal["decision"] == "retain-reviewed-band"
            and record["owner"] == "baseline"
            and proposal.get("reason") != record.get("before_reason")
        ):
            raise ValueError(f"{record['name']}: retained provenance was overwritten")
        if require_applied:
            current = current_inventory[int(item_id)]["before_band"]
            if current != band:
                successor = blacksmithing_successors.get(item_id)
                if (
                    successor is None
                    or current != successor["proposal"]["proposed_band"]
                    or successor["canonical_key"] != record["canonical_key"]
                ):
                    raise ValueError(f"{record['name']}: applied band is stale")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument("--refresh", action="store_true")
    action.add_argument("--apply", action="store_true")
    action.add_argument("--check", action="store_true")
    action.add_argument("--inventory", action="store_true")
    parser.add_argument("--phase", choices=("phase1a", "phase1b"), default="phase1a")
    parser.add_argument("--beancounter", type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    configure_phase(args.phase)
    if args.inventory:
        records = inventory()
        inherited_ids = (
            set(records)
            & {
                int(item_id)
                for item_id in load(PHASE_1A_EVIDENCE_PATH).get("items", {})
            }
            if ACTIVE_PHASE == "phase1b"
            else set()
        )
        cohort_ids = {
            item_id for _, item_ids in COHORTS.values() for item_id in item_ids
        }
        derived_ids = set(DERIVED_TEN_TO_ONE) | set(DERIVED_THREE_TO_ONE)
        missing_cohorts = sorted(
            item_id
            for item_id, record in records.items()
            if record["owner"] != "vendor"
            and item_id not in inherited_ids
            and item_id not in cohort_ids
            and item_id not in derived_ids
        )
        output = [
            {
                "item_id": item_id,
                "name": record["name"],
                "owner": record["owner"],
                "canonical_key": record["canonical_key"],
                "before_band": record["before_band"],
                "occurrences": record["occurrences"],
            }
            for item_id, record in sorted(records.items())
        ]
        print(json.dumps(output, ensure_ascii=True, indent=2))
        print(
            f"inventory_occurrences {sum(len(row['occurrences']) for row in records.values())}"
        )
        print(f"inventory_unique_items {len(records)}")
        print(f"inventory_inherited_phase1a {len(inherited_ids)}")
        print(f"inventory_missing_cohorts {len(missing_cohorts)}")
        for item_id in missing_cohorts:
            print(f"missing_cohort {item_id} {records[item_id]['name']}")
        return 0
    if args.refresh:
        if args.beancounter and not args.beancounter.is_file():
            raise ValueError("BeanCounter input does not exist")
        evidence = build_evidence(args.beancounter)
        EVIDENCE_PATH.write_text(
            json.dumps(evidence, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
            newline="\n",
        )
        REPORT_PATH.write_text(
            render_report(evidence), encoding="utf-8", newline="\n"
        )
        summary = evidence["summary"]
        print(f"items_reviewed {summary['items_reviewed']}")
        print(f"bands_changed {summary['bands_changed']}")
        print(f"direct_sale_items {summary['direct_sale_items']}")
        print(
            "items_seen_on_three_realms "
            f"{summary['items_seen_on_three_realms']}"
        )
        print("external_gold_values_copied false")
        return 0
    evidence = load(EVIDENCE_PATH)
    if args.apply:
        validate(evidence, require_applied=False)
        apply_proposals(evidence)
        evidence["scope"]["application_status"] = "applied locally"
        EVIDENCE_PATH.write_text(
            json.dumps(evidence, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
            newline="\n",
        )
        REPORT_PATH.write_text(
            render_report(evidence), encoding="utf-8", newline="\n"
        )
        validate(evidence, require_applied=True)
        print(f"Applied {evidence['summary']['bands_changed']} reviewed price-band changes.")
        return 0
    validate(evidence, require_applied=True)
    if REPORT_PATH.read_text(encoding="utf-8") != render_report(evidence):
        raise ValueError("Gathering/material review report is stale")
    print("Gathering and material Evidence Pricing review is current.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
