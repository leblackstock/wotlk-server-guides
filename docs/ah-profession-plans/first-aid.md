# First Aid AH Expansion Plan

- Status: `complete — Phase 2 Evidence Pricing, 2026-08-08`
- Existing guide: shared placement in `guides/tailoring-cloth-ah-price-guide.html`
- Work type: small full catalog plus guide-placement decision
- Suggested order: 7

> Hard gate: audit current cloth prices and any existing bandage/anti-venom rows
> before adding crafted rows. Follow [the shared Gate 0](README.md#gate-0-establish-non-circular-baselines-before-adding-crafteds).

## Baseline Evidence Audit

- Audit every cloth input in `guides/tailoring-cloth-ah-price-guide.html` and
  reconcile duplicates before calculating bandage prices.
- Search all AH guides for bandages, anti-venoms, venom sacs, and related
  reagents; correct or consolidate any existing rows first.
- Record active supply and seller concentration separately from completed sales.
  Thin listings cannot establish a baseline or broad price confidence.
- Verify server-specific tradeability, stack sizes, healing values, level
  requirements, and whether First Aid behavior matches 3.3.5.

## Placement Decision

Choose and record one option before implementation:

- Create `guides/first-aid-ah-price-guide.html` if the verified catalog and AH
  demand support a useful standalone page; or
- Add a clearly labeled First Aid crafted block to the Tailoring cloth guide if
  the catalog is too small for a dedicated page.

Do not mix First Aid outputs into Tailoring's crafted source of truth merely
because both consume cloth.

## Crafted Coverage

- Verify all normal and heavy bandage ranks from Linen through Frostweave.
- Verify Anti-Venom, Strong Anti-Venom, Powerful Anti-Venom, and any other
  apparent First Aid outputs individually; include only valid tradeable 3.3.5
  items with a real recipe spell.
- Exclude quest-only medical items, battleground-only supplies, conjured items,
  invalid ranks, and non-tradeable outputs.

## Profession-Specific Price Checks

- Calculate exact cloth or venom-sac cost per finished item using the guaranteed
  recipe yield.
- Compare finished bandage value with the cloth opportunity cost; explicitly
  flag convenience-only listings that trade below material value.
- Keep demand conservative and use small stacks unless live evidence supports
  larger PvP, leveling, or achievement purchases.

## Notes to Verify

- State healing/cleansing effect, channel duration if relevant, required level,
  and likely PvP/leveling/achievement use.
- Distinguish normal and heavy ranks clearly; do not reuse a generic note for
  all bandages.
- Explain weak or obsolete demand honestly.

## Acceptance Checks

- [x] Current cloth/reagent price audit completed and recorded.
- [x] Guide placement is decided and documented.
- [x] Every First Aid recipe has an include/exclude decision.
- [x] Output quantities, effects, levels, binding, and rarity are verified.
- [x] Thin-market/fallback prices are clearly labeled.
- [x] Shared validation in `README.md` passes.

## Evidence Log

- Phase 2 completion — 2026-08-08: Reviewed all 17 tradeable First Aid
  outputs. All 102 comparison requests resolved on the initial pass, and every
  item had three-realm relative-rank coverage. No completed-sale history was
  available. All five Target changes over 50% passed the coverage safeguard and
  were accepted. The pass changed all 17 bands; nine Targets rose, seven fell,
  and one stayed unchanged. Four final estimates fall below at least one exact
  recipe-floor band and retain shared do-not-craft guidance. The 15 hard First
  Aid requirements remain in three restricted sections; Anti-Venom and Strong
  Anti-Venom remain general-use. Evidence references, exact output quantities,
  notes, ordering, search metadata, and the shared guide copy were refreshed
  locally. Nothing was published.
- Phase 2 start — 2026-08-08: Froze all 17 tradeable First Aid outputs across
  four sections: 14 bandages and three anti-venoms. All seven cloth inputs retain
  their completed Phase 1B evidence, and the three venom-sac inputs retain their
  documented non-circular fallbacks. This batch reviews finished-output sale
  value separately from exact per-output recipe cost, excludes active Hellscream
  listings and external nominal gold, and uses the required 2-, 5-, and
  10-second waited retries for failed comparison requests. Nothing has been
  published.
- Audit date: 2026-08-03.
- Placement decision: First Aid is a separately owned canonical catalog inside
  `data/ah-crafted-sections.json`, rendered as four clearly labeled sections at
  the top of the Tailoring/cloth guide. A separate page was rejected because
  the complete catalog contains only 17 tradeable outputs and shares the cloth
  buying path; the combined page avoids a thin guide without mislabeling First
  Aid items as Tailoring crafts.
- Listing concentration observations (not valuation evidence): The AH was not
  rescanned for valuation. The user and friends are known to control at least
  half of many markets, so active listings remain competition evidence only and
  were excluded from every First Aid baseline and finished-price calculation.
- Recipe/item sources checked: WotLKDB's 3.3.5 First Aid spell list and
  individual item/recipe pages supplied spell IDs, reagents, guaranteed output,
  effects, channels, cooldowns, and First Aid-use ranks. AzerothCore item
  templates at commit `e0fe11ba46b885a01e4a4038001e0055822cc7ba`
  confirmed rarity, binding, stack size, tradeability, and absence of separate
  character-level requirements. All seven saved cloth baselines and all AH
  guides were audited for duplicate bandage, anti-venom, and reagent coverage.
- Server-specific findings: No Hellscream-specific First Aid override was
  verified. The catalog therefore documents standard 3.3.5 behavior and does
  not claim a custom recipe, output, or use requirement.
- Decisions and unresolved items: Twenty-three First Aid spell records were
  reviewed. Seventeen produce valid tradeable items: 14 bandages and three
  anti-venoms. Six rank/header records produce no item and were excluded.
  Fifteen outputs require First Aid to use and occupy dedicated restricted
  sections; Anti-Venom and Strong Anti-Venom are separately labeled general-use
  items. All 17 are common, unbound, tradeable, and have no separate character-
  level requirement. Cloth prices retain the frozen pre-scan low-confidence
  references. Small, Large, and Huge Venom Sacs received explicit fallback
  ranges anchored above exact vendor liquidation values; no listing price was
  used. Those three provisional ranges remain unresolved until qualifying
  realized-sale or measured-acquisition evidence exists.
- Completion summary: Added all 17 valid outputs with exact recipe mouseovers,
  rarity colors, effects, use restrictions, conservative stack guidance, and
  exact same-band craft floors. The catalog is divided into Wrath, Outland, and
  Classic First Aid-only sections plus a general-use anti-venom section. The
  shared page now contains 423 crafted rows across 21 sections, ordered by
  target buyout within each section.
