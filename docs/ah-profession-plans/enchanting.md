# Enchanting AH Evidence Pricing Plan

- Status: `complete` — Phase 2 Evidence Pricing, 2026-08-06
- Active guide: `guides/enchanting-mats-ah-price-guide.html`
- Work type: full finished-output price and recipe audit
- Phase 2 order: 6

> Hard gate: finish and record the baseline evidence audit before repricing
> finished outputs. Follow [the shared Gate 0](README.md#gate-0-establish-non-circular-baselines-before-adding-crafteds).

## Baseline Evidence Audit

- Freeze the 276 canonical outputs in 25 sections: 259 enchant scrolls, nine
  weapon oils, four BoE wands, two tradeable intermediates, and two prismatic
  gems.
- Recheck every dust, essence, shard, crystal, bar, gem, oil, wood, vial,
  parchment, and ink input against the completed Phase 1 material evidence or
  an exact unlimited-vendor price.
- Reconstruct and save all 276 exact WotLK 3.3.5 recipes. For scrolls, add the
  exact cheapest compatible Armor or Weapon Vellum rank as a separate recipe
  input; do not infer that cost from the scroll's old price.
- Keep exact recipe cost separate from estimated finished-item sale value.
  Active Hellscream listings remain competition evidence only and never set a
  baseline.
- Record sanitized Hellscream completed sales separately. Use external AH
  observations only for within-cohort relative rank and never copy their
  nominal gold values.

## Finished-Output Coverage

- Wrath, Outland, and Classic weapon, shield, chest, cloak, bracer, glove, and
  boot enchant scrolls.
- Classic and Outland wizard and mana oils, including real charge count and
  item-level limits.
- Classic BoE leveling wands, tradeable Enchanting intermediates, and Outland
  prismatic gems.
- Exclude direct self-only enchant applications, nontradeable outputs, BoP
  outputs, temporary effects without a tradeable item, and invalid records.

## Enchanting-Specific Price Checks

- Compare scrolls only within the same expansion, equipment slot, practical
  buyer use, and broad recipe-cost tier. Do not rank a leveling resistance
  enchant against a current raid weapon enchant merely because both are
  scrolls.
- Preserve qualified completed-sale evidence when available. Shrink sparse or
  concentrated sales toward a fixed comparable-cohort estimate.
- Treat oils as charged consumables, wands as one-at-a-time BoE leveling gear,
  and intermediates or gems as like-purpose stackable markets.
- Review every proposed Target change over 50%; retain the old frozen band when
  neither qualified local sales nor at least two comparison realms support it.
- Keep the exact recipe plus vellum floor as a do-not-craft diagnostic whenever
  the estimated sale band falls below purchased-input cost.

## Profession-Use and Notes Checks

- Verify every finished output against `data/ah-profession-use-audit.json`.
  Finished enchant scrolls are usable without Enchanting; blank vellums remain
  in their dedicated Enchanter-only Inscription section.
- Give every level-80 enchant a concrete effect and defensible raid, PvP, tank,
  healer, caster, melee, or situational use note. Keep lower-tier rows concise
  and specific to their effect or leveling market.
- Preserve the exact recipe-and-mats mouseover link for every row.
- Use one shared `*` Evidence Pricing and craft-diagnostic note for the guide;
  do not repeat reagent-floor methodology in row notes.

## Acceptance Checks

- [x] Gate 0 baseline audit completed and recorded.
- [x] All 276 finished outputs have a saved before/after evidence review.
- [x] Every exact recipe, output count, vellum rank, item ID, rarity, binding,
  stack, and auction-eligibility record is verified.
- [x] All level-80 enchant notes state the exact effect and practical use.
- [x] All Target moves over 50% have an explicit reviewer decision.
- [x] One shared methodology note replaces repeated floor boilerplate.
- [x] Canonical guide, ordering, search, tooltip, currency, rarity, profession
  eligibility, UTF-8, and desktop/mobile validation pass.

## Evidence Log

- Phase 2 Evidence Pricing started — 2026-08-06: the required Enchanting plan
  was added because the canonical 276-output guide existed without a matching
  profession plan. The inventory contains 259 scrolls and 17 oils, wands,
  intermediates, or gems across 25 sections. All 276 saved spell IDs resolve in
  the complete 306-record WotLKDB Enchanting skill list. Phase 1 input baselines
  remain frozen, current Hellscream listings remain competition-only evidence,
  and exact recipe plus vellum cost remains separate from estimated sale value.
  Work is local and nothing has been published.
- Phase 2 Evidence Pricing completed — 2026-08-06: all 276 outputs received
  saved before/after bands, exact current recipe diagnostics, sanitized
  completed-sale coverage, six-source comparison coverage, confidence, and an
  explicit reviewer decision. No output had completed-sale evidence. Comparison
  coverage reached all three realms for 261 outputs, two realms for 13, one
  realm for one, and no realm for Titanguard. Twenty-three of 24 Target
  candidates over 50% had at least two-realm support and were accepted;
  Titanguard retained its prior band because it had no comparison coverage.
  The pass changed 274 price bands; Enchanted Thorium Bar retained its completed
  Phase 1 material band and evidence reference instead of being overwritten by
  the finished-output pass. Eighty-five Targets rose, 106 fell, and 85 remained
  unchanged. Seventy-two final estimates fall below at least one exact recipe
  plus vellum floor and retain the shared do-not-craft guidance. The guide now
  uses one shared Evidence Pricing note, exact recipe mouseovers, corrected
  level-80 use notes, rarity colors, target-price ordering, and current search
  metadata. Work remains local and nothing has been published.
