#!/usr/bin/env python3
"""Validate the shared three-wait comparison retry rule."""

from __future__ import annotations

import importlib.util
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = ROOT / "scripts" / "review-ah-blacksmithing-prices.py"

spec = importlib.util.spec_from_file_location("ah_evidence_retry", SCRIPT_PATH)
if spec is None or spec.loader is None:
    raise RuntimeError("Could not load the shared Evidence Pricing fetcher")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

task = ("test-source", 12345, "Test Item", 99, 1, 1.0)
calls = Counter()
sleeps = []


def succeeds_on_fourth(current_task):
    source_key, item_id, *_ = current_task
    calls[(source_key, item_id)] += 1
    attempt = calls[(source_key, item_id)]
    if attempt < 4:
        return source_key, item_id, {"present": False, "fetch_failed": True}
    return source_key, item_id, {"present": True, "fetch_failed": False}


observations, summary = module.fetch_observations_with_retries(
    [task],
    worker=succeeds_on_fourth,
    sleeper=sleeps.append,
)
assert calls[("test-source", 12345)] == 4
assert sleeps == [2, 5, 10]
assert observations[12345]["test-source"]["present"] is True
assert summary == {
    "initial_requests": 1,
    "retry_delays_seconds": [2, 5, 10],
    "retry_rounds_used": 3,
    "final_failed_requests": 0,
}

print("Shared comparison fetcher waits and retries failed requests three times.")
