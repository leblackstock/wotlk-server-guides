#!/usr/bin/env python3
"""Guard the required AH item-addition workflow and work-order template."""

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / "docs" / "ah-item-addition-workflow.md"
TEMPLATE = ROOT / "docs" / "ah-item-additions" / "_template.md"


def require(source: str, values: tuple[str, ...], label: str) -> None:
    missing = [value for value in values if value not in source]
    if missing:
        raise AssertionError(f"{label} is missing required content: {missing}")


def main() -> int:
    workflow = WORKFLOW.read_text(encoding="utf-8")
    template = TEMPLATE.read_text(encoding="utf-8")
    agents = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
    profession_readme = (
        ROOT / "docs" / "ah-profession-plans" / "README.md"
    ).read_text(encoding="utf-8")
    methodology = (ROOT / "docs" / "ah-pricing-methodology.md").read_text(
        encoding="utf-8"
    )

    require(
        workflow,
        (
            "Active listings show competition only and never set or raise guide prices.",
            "Gate A — Identity, Tradeability, and Buyer Use",
            "Gate B — Establish Evidence Pricing",
            "Gate C — Craft Cost and Deterministic Floors",
            "Gate D — Choose the Canonical Owner",
            "Gate E — Write Useful Guide Content",
            "Gate F — Required Validation",
            "Separate proposal, review, and apply",
            "2, 5, and 10 seconds",
            "external_gold_values_copied: false",
            "used_to_set_prices: false",
            "data/ah-crafted-sections.json",
            "scripts/audit-ah-phase3-catalogs.py",
            "data/ah-dropped-gear.json",
            "python scripts/apply-ah-section-price-order.py --check",
            "python scripts/build-ah-search-index.py --check",
            "python scripts/apply-ah-item-tooltips.py --check",
            "python scripts/audit-ah-auction-eligibility.py --check",
            "Publish Only When Explicitly Authorized",
        ),
        "AH item-addition workflow",
    )
    require(
        template,
        (
            "Requested Items",
            "Identity and Eligibility",
            "Duplicate and Dependency Audit",
            "Completed Hellscream sales",
            "Current listings — diagnostic only",
            "Price Proposal and Review",
            "Craftability Diagnostic",
            "Canonical Implementation",
            "Guide Content Check",
            "Validation Record",
            "Acceptance Report",
            "Publication Record",
        ),
        "AH item-addition work-order template",
    )
    require(
        agents,
        (
            "docs/ah-item-addition-workflow.md",
            "docs/ah-item-additions/_template.md",
        ),
        "Repository instructions",
    )
    if "AH Item Addition Workflow" not in profession_readme:
        raise AssertionError("Profession-plan README does not link the item workflow")
    if "ah-item-addition-workflow.md" not in methodology:
        raise AssertionError("Evidence Pricing methodology does not link the item workflow")

    print("AH item-addition workflow, template, routing, evidence gates, and publish gate are current.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
