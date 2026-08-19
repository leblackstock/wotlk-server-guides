# Repository Documentation

The `docs/` directory contains maintainer workflows, work orders, saved audit evidence, and reusable setup recipes. Player-facing HTML belongs in [`guides/`](../guides/), while visual-system references and implementation evidence belong in [`internal/`](../internal/README.md).

## Start Here

- [AH Item Addition Workflow](ah-item-addition-workflow.md) — required process for adding an item or item group to an Auction House guide.
- [AH Pricing Methodology](ah-pricing-methodology.md) — accepted evidence, confidence, and non-circular pricing rules.
- [AH Guide UX Standard](ah-guide-ux-standard.md) — approved presentation and interaction rules.
- [Class Color System Workflow](class-color-system-workflow.md) — required workflow for class and specialization color systems.

## Directory Map

- [`addon-recipes/`](addon-recipes/README.md) — validated addon configurations and reproducible setup instructions that are not public guide pages.
- [`ah-item-additions/`](ah-item-additions/) — individual AH addition work orders and the work-order template.
- [`ah-profession-plans/`](ah-profession-plans/README.md) — profession expansion plans, status, and evidence logs.
- [`class-color-system-work-orders/`](class-color-system-work-orders/) — color-system work orders and the reusable template.

## Saved Audit and Review Records

Files named `ah-*-pricing-review.md`, `ah-*-demand-review.md`, and `ah-*-pricing-plan.md` are reproducible evidence records generated or maintained alongside their canonical data and scripts. Keep them in `docs/` so the evidence stays separate from player-facing pages.

## Placement Rules

- Put public player guides in `guides/` and register them through the appropriate hub or manifest.
- Put canonical structured content in `data/`; do not use a Markdown review as the canonical source when a data file already owns the value.
- Put AH-oriented Python build and audit commands in `scripts/`.
- Put JavaScript guide-authoring and Fresh-80 audit utilities in `tools/`.
- Put automated checks in `tests/`.
- Put non-player-facing browser references, research matrices, and implementation checklists in `internal/`.
- Use lowercase kebab-case filenames except for conventional files such as `README.md`, `AGENTS.md`, and generated artifacts with an established name.
