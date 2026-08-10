# Engineering AH Evidence Pricing Plan

- Status: `complete` — Phase 2 plus collectible addendum, 2026-08-10
- Active guide: `guides/engineering-materials-ah-price-guide.html`
- Work type: full finished-output price audit
- Phase 2 order: 3

> Hard gate: finish and record the baseline evidence audit before repricing
> finished outputs. Follow [the shared Gate 0](README.md#gate-0-establish-non-circular-baselines-before-adding-crafteds).

## Baseline Evidence Audit

- Inventory all 55 canonical finished Engineering outputs and identify shared
  components wherever they also appear as material baselines or guide rows.
- Recheck every recipe input against the completed Phase 1 material evidence;
  keep exact recipe cost separate from estimated finished-item sale value.
- Confirm that prices are per item, while ammunition and multi-output recipes
  use the minimum guaranteed output quantity in their craft-floor calculation.
- Record sanitized Hellscream completed-sale coverage separately from active
  listings. Active listings are competition evidence only and never establish
  or update the price baseline.
- Use cross-server observations only for within-cohort relative rank, normalized
  to fixed Hellscream cohort anchors. Never copy external nominal gold prices.

## Finished-Output Coverage

- Crafted parts from Northrend, Outland, and Classic.
- Blasting powders, ammunition, explosives, target dummies, and decoys.
- General-use devices, profession tools, and mount components.
- Five general-use crafted companions, two Engineer-only flying mounts, and two
  faction-specific general-use motorcycles.
- Engineer-restricted devices, tools, ammunition, explosives, and mount parts
  in their dedicated restricted sections.
- Exclude BoP, nontradeable, self-only, temporary, conjured, invalid, and
  otherwise auction-ineligible outputs.

## Engineering-Specific Price Checks

- Compare components only with components of similar tier and practical use;
  do not rank a rare mount component against leveling blasting powder.
- Price ammunition per item and verify the displayed suggested stack sizes
  against both the real stack limit and normal purchase quantities.
- Treat explosives and consumable devices as stackable material-like markets;
  require broad unit and buyer coverage before completed sales can dominate.
- Treat reusable tools, devices, and mount components as one-at-a-time BoE-like
  markets with the stricter completed-sale evidence gate.
- Preserve an explicit do-not-craft warning when the evidence-based sale band
  falls below its exact recipe-cost diagnostic.
- Review every proposed Target change over 50%; retain the prior fallback when
  independent comparison coverage is too weak.

## Profession-Use and Notes Checks

- Verify every finished output against `data/ah-profession-use-audit.json`.
  Hard Engineering requirements stay in dedicated Engineer-only sections.
- Keep genuinely general-use outputs, including the Gnomish Army Knife and
  Mana Injector Kit, in general-use sections when their item records have no
  direct Engineering skill requirement.
- Give each row an item-specific buyer, effect, purchase-quantity, or turnover
  note plus the exact recipe mouseover link.
- Use one shared `*` Evidence Pricing and craft-floor note for the guide; do not
  repeat methodology boilerplate in row notes.

## Acceptance Checks

- [x] Gate 0 baseline audit completed and recorded.
- [x] All 55 finished outputs have a saved before/after evidence review.
- [x] Every exact recipe, guaranteed output count, item ID, rarity, and auction
  eligibility record is verified.
- [x] Shared components and duplicate display rows are synchronized.
- [x] Profession-restricted outputs are separated from general-use items.
- [x] Ammo units and stack recommendations are correct.
- [x] All Target moves over 50% have an explicit reviewer decision.
- [x] Generated guide, ordering, search, tooltip, and full AH validation pass.
- [x] Collectible companions and mounts are separated by actual buyer
  requirement and share the dedicated collectible evidence snapshot.

## Evidence Log

- Phase 2 Evidence Pricing started — 2026-08-06: the required Engineering plan
  was added because the canonical guide existed without a matching profession
  plan. The audit begins with all 55 finished outputs. Completed Phase 1 input
  baselines remain fixed; current Hellscream listings remain competition-only
  evidence. Work is local and nothing has been published.
- Phase 2 Evidence Pricing completed — 2026-08-06: all 55 finished outputs
  received saved before/after bands, exact current recipe-floor diagnostics,
  sanitized completed-sale coverage, six-source comparison coverage,
  confidence, and an explicit reviewer decision. No Engineering output had a
  qualifying local completed sale. Fifty-one outputs had all-three-realm
  comparison coverage, three had two-realm coverage, and Box of Bombs retained
  its fixed cohort anchor without external coverage. All 11 Target candidates
  over 50% had three-realm support and were accepted after manual review. Every
  price band changed; Targets increased for 25 outputs, decreased for 21, and
  remained unchanged for nine. Twenty-three Target estimates are below their
  exact price-basis recipe floors and are labeled as do-not-craft diagnostics.
  All 13 ammunition rows were normalized to the displayed stack of 200. The
  guide, search index, tooltips, ordering, notes, and recipe links were
  regenerated locally. Nothing was published.
- Container coverage addendum — 2026-08-08: Added Heavy Toolbox as a
  vendor-owned 20-slot Engineering-supplies container. The pinned source is
  limited to one per vendor with a 2-hour restock at Fabian Lanzonelli and
  12-hour restocks at the other listed innkeepers. Exact vendor cost sets the
  floor; active listings did not set value. Nothing was published.
- Collectible coverage addendum — 2026-08-10: Added five tradeable mechanical
  companions, the two Engineer-only flying machines, and the Horde/Alliance
  motorcycles. Exact recipes and recursively audited craft floors are saved;
  the nine sale-value bands are delegated to the collectible Evidence Pricing
  review so the completed 55-output Engineering Phase 2 snapshot remains
  frozen. Mechano-hog is explicitly below its Quick craft floor and carries a
  do-not-craft warning. Active listings did not set value. Nothing was
  published.
