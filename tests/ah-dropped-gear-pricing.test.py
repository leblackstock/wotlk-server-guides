#!/usr/bin/env python3
"""Guard dropped-gear evidence privacy, normalization, and reviewed prices."""

from __future__ import annotations

import json
import re
import subprocess
import sys
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE_PATH = ROOT / "data" / "ah-dropped-gear-price-evidence.json"
CROSS_PATH = ROOT / "data" / "ah-dropped-gear-cross-server-diagnostics.json"
BASELINE_PATH = ROOT / "data" / "ah-price-baselines.json"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    subprocess.run(
        [sys.executable, "scripts/estimate-ah-dropped-gear-prices.py", "--check"],
        cwd=ROOT,
        check=True,
    )
    evidence = load(EVIDENCE_PATH)
    cross = load(CROSS_PATH)
    baseline = load(BASELINE_PATH)["items"]

    assert evidence["privacy"] == {
        "raw_savedvariables_committed": False,
        "source_paths_committed": False,
        "character_names_committed": False,
        "buyer_or_seller_names_committed": False,
        "identity_hashes_committed": False,
        "only_aggregate_identity_counts_committed": True,
    }
    evidence_source = EVIDENCE_PATH.read_text(encoding="utf-8")
    cross_source = CROSS_PATH.read_text(encoding="utf-8")
    assert not re.search(r"[A-Za-z]:\\", evidence_source + cross_source)
    assert "SavedVariables" not in evidence_source
    assert evidence["rules"]["active_listings_used_to_set_prices"] is False
    assert evidence["rules"]["normalized_cross_server_gold_copied_to_baselines"] is False
    assert evidence["rules"]["normalized_cross_server_relative_rank_used_for_reviewed_estimates"] is True
    assert evidence["rules"]["live_snapshot_auto_repricing_enabled"] is False
    assert cross["rules"]["external_asks_used_to_set_prices"] is False
    assert len(evidence["items"]) == len(cross["items"]) == 347

    decisions = Counter(
        record["proposal"]["decision"] for record in evidence["items"].values()
    )
    assert decisions == Counter(
        {"accept-reviewed-starter-estimate": 345, "accept-sparse-direct-sale": 2}
    )
    assert evidence["review"]["model_acceptance"] == "user-directed-reviewed-starter-estimates"
    assert evidence["review"]["starter_estimate_model_deployed"] is True
    assert evidence["review"]["starter_estimate_model_version"] == "hellscream-low-pop-relative-rank-v1"
    assert evidence["review"]["external_diagnostics"]["used_to_set_prices"] is False
    assert evidence["review"]["external_diagnostics"]["used_for_relative_rank"] is True
    assert evidence["review"]["external_diagnostics"]["external_gold_values_copied"] is False

    assert set(cross["sources"]) == {
        "lordaeron-horde",
        "lordaeron-alliance",
        "icecrown-horde",
        "icecrown-alliance",
        "onyxia-horde",
        "onyxia-alliance",
    }
    for source in cross["sources"].values():
        assert re.fullmatch(r"[0-9a-f]{64}", source["snapshot_sha256"])
        scale = source["scale"]
        assert scale["external_gold_per_hellscream_gold"] > 0
        assert scale["benchmarks_available"] >= 5
        assert scale["benchmarks_used"] >= 3
        assert scale["confidence"] == "diagnostic-only"

    assert cross["summary"]["items_seen_on_at_least_two_realms"] == 305
    assert sum(cross["summary"]["diagnostics"].values()) == 347
    for item_id, record in evidence["items"].items():
        proposal = record["proposal"]
        diagnostic = proposal["cross_server_diagnostic"]
        assert diagnostic == cross["items"][item_id]
        assert diagnostic["used_to_set_price"] is False
        applied = baseline[item_id]
        assert {key: int(applied[key]) for key in ("quick", "target", "high")} == proposal["proposed_band"]
        assert applied["source_type"] == proposal["source_type"]
        assert applied["confidence"] == proposal["confidence"]
        if proposal["decision"] == "accept-reviewed-starter-estimate":
            model = proposal["starter_model"]
            assert model["version"] == "hellscream-low-pop-relative-rank-v1"
            assert model["external_gold_value_copied"] is False
            assert proposal["source_type"] == "documented-fallback"
            assert proposal["confidence"] == "fallback"

    sandals = evidence["items"]["37752"]
    assert sandals["realized_sales"]["gross_unit_copper"]["median"] == 95_653
    assert sandals["proposal"]["proposed_band"] == {
        "quick": 86_088,
        "target": 95_653,
        "high": 119_566,
    }
    zoms = evidence["items"]["44313"]
    assert zoms["realized_sales"]["gross_unit_copper"]["median"] == 3_500_000
    assert zoms["proposal"]["proposed_band"] == {
        "quick": 2_975_000,
        "target": 3_500_000,
        "high": 4_550_000,
    }
    assert evidence["items"]["1121"]["proposal"]["proposed_band"] == {
        "quick": 300_000,
        "target": 400_000,
        "high": 650_000,
    }
    assert evidence["items"]["50447"]["proposal"]["proposed_band"] == {
        "quick": 10_500_000,
        "target": 15_500_000,
        "high": 27_000_000,
    }

    print("Dropped-gear price evidence and normalized cross-server diagnostics are valid.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
