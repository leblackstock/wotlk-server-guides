# Alchemy AH Evidence Pricing Plan

- Status: `complete` — Phase 2 Evidence Pricing, 2026-08-06
- Active guide: `guides/alchemy-materials-ah-price-guide.html`
- Work type: finish the saved potion review and audit every remaining finished output
- Phase 2 order: 7

> Hard gate: finish and record the baseline evidence audit before repricing
> finished outputs. Follow [the shared Gate 0](README.md#gate-0-establish-non-circular-baselines-before-adding-crafteds).

## Gate 0 Baseline Audit

- Freeze the canonical catalog at 206 tradeable outputs across 21 sections.
- Preserve the completed 84-potion Evidence Pricing snapshot in
  `data/ah-alchemy-potion-price-evidence.json`; do not rebuild it from current
  Hellscream asks.
- Preserve the 24 Alchemy outputs already reviewed with profession materials in
  `data/ah-profession-material-price-evidence.json`.
- Review the remaining 98 outputs as one finished-market batch: 16 flasks, 76
  elixirs, five sealed protection cauldrons, and Eternal Might.
- Reconcile every herb, fish, vial, elemental, oil, gem, bar, and other input
  against the frozen Phase 1 evidence. Active Hellscream listings remain
  competition evidence only and never set a baseline.
- Keep the exact audited 3.3.5 recipe floor separate from estimated finished-
  item sale value. Use minimum guaranteed output and exclude specialization
  procs from the floor.

## Finished-Output Coverage

- Wrath, Outland, and Classic flasks, including raid role and both-elixir-slot
  behavior.
- Wrath, Outland, and Classic Battle, Guardian, leveling, resistance, and
  utility elixirs.
- The five tradeable Outland protection cauldrons, valued as sealed 25-use
  finished items rather than as individual protection potions.
- Eternal Might as a tradeable transmute output with cooldown and input
  opportunity cost documented separately from its estimated market value.
- The 84 previously reviewed potions and 24 previously reviewed material or
  intermediate outputs remain covered by their existing evidence files.
- Exclude BoP, self-only, nontradeable, temporary, conjured, or invalid outputs.
  Crazy Alchemist's Potion and Mad Alchemist's Potion remain in their dedicated
  hard-restricted section.

## Alchemy-Specific Price Checks

- Compare flasks by expansion and practical role: physical damage,
  caster/healer, tank, regeneration, resistance, or leveling/PvP utility.
- Compare elixirs by expansion, Battle or Guardian slot, practical effect, and
  broad recipe-cost tier. Do not rank a niche detection elixir against a raid
  throughput elixir merely because both are consumables.
- Compare sealed cauldrons only with like-purpose cauldrons. Preserve their
  sealed-item value and do not multiply or divide the market estimate by a
  potion-row price.
- Treat Eternal Might as a distinct transmute market. Recipe cooldown and
  access belong in its item note, not as an unsupported hidden premium.
- Preserve qualified Hellscream completed sales when available. Shrink sparse
  or concentrated sales toward a fixed comparable-cohort estimate.
- Review every proposed Target change over 50%; retain the old frozen band when
  neither qualified local sales nor at least two comparison realms support it.
- Keep an exact recipe-floor do-not-craft diagnostic whenever the estimated
  sale band is below the purchased-input cost.

## Profession Use, Notes, and Ordering

- Recheck all 206 outputs against `data/ah-profession-use-audit.json`.
- Keep the two hard-restricted potions in the Alchemist-only section. The five
  cauldrons are saved general-use exceptions and remain in the public finished-
  output catalog.
- Preserve exact item effects, Battle/Guardian designation, raid or leveling
  use, resistance type, and cooldown/access facts in item-specific notes.
- Preserve the exact recipe-and-mats mouseover link for every row.
- Use one shared `*` Evidence Pricing and craft-diagnostic note for the guide;
  do not repeat pricing methodology in row notes.
- Sort each non-progression section by Target buyout per item, highest first.

## Acceptance Checks

- [x] Gate 0 inventory and evidence boundaries recorded.
- [x] All 98 remaining outputs have a saved before/after evidence review.
- [x] The existing 84 potion and 24 material/intermediate prices and evidence
  references remain unchanged.
- [x] All 206 exact recipes, output counts, item IDs, rarity, binding, stack,
  and auction-eligibility records are verified.
- [x] All Target moves over 50% have an explicit reviewer decision.
- [x] One shared methodology note replaces repeated pricing boilerplate.
- [x] Canonical guide, ordering, search, tooltip, currency, rarity, profession
  eligibility, UTF-8, and desktop/mobile validation pass.

## Evidence Log

- Phase 2 Evidence Pricing started — 2026-08-06: the missing Alchemy profession
  plan was added and the 206-output catalog was frozen. The completed 84-potion
  review and 24 material/intermediate records are disjoint and remain unchanged,
  leaving 98 finished outputs for this batch: 16 flasks, 76 elixirs, five
  sealed protection cauldrons, and Eternal Might. All 206 outputs already have
  exact saved recipes. The only hard profession requirements are the two
  potions already held in the Alchemist-only section; all five cauldrons are
  saved general-use exceptions. Phase 1 input baselines remain frozen, current
  Hellscream listings remain competition-only evidence, and exact recipe cost
  remains separate from estimated sale value. Work is local and nothing has
  been published.
- Phase 2 Evidence Pricing completed — 2026-08-06: all 98 remaining outputs
  received saved before/after bands, exact current recipe diagnostics,
  sanitized completed-sale coverage, six-source comparison coverage,
  confidence, and an explicit reviewer decision. No item had completed-sale
  evidence. Comparison coverage reached all three realms for 97 outputs;
  Eternal Might had no comparison coverage and retained its 45g Target anchor.
  All 20 Target candidates over 50% had three-realm support and were accepted
  after review. The pass changed all 98 bands; 44 Targets rose, 52 fell, and
  two stayed unchanged. Thirty final estimates fall below at least one exact
  recipe-floor band and retain shared do-not-craft guidance. The 84-potion and
  24 material/intermediate companion reviews remained unchanged. The guide now
  uses one shared Evidence Pricing note, sealed-item cauldron guidance, exact
  recipe mouseovers, item-specific effect notes, rarity colors, target-price
  ordering, and current search metadata. All 206 Alchemy crafts are now covered
  by saved market evidence. Work remains local and nothing has been published.
