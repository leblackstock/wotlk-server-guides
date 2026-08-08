# Inscription AH Evidence Pricing Plan

- Status: `complete` — Phase 2 Evidence Pricing, 2026-08-06
- Active guide: `guides/inscription-materials-ah-price-guide.html`
- Work type: full finished-output price, random-output, use, and recipe audit
- Phase 2 order: 8

> Hard gate: finish and record the baseline evidence audit before repricing
> finished outputs. Follow [the shared Gate 0](README.md#gate-0-establish-non-circular-baselines-before-adding-crafteds).

## Gate 0 Baseline Audit

- Freeze the canonical catalog at 107 tradeable outputs across 18 sections.
- Preserve Armor Vellum III and Weapon Vellum III from the completed Phase 1B
  profession-material review; do not replace their saved market evidence.
- Review the remaining 105 outputs as one finished-market batch: 60 glyphs, six
  buff scrolls, three general-use utility or BoE items, 32 exact Darkmoon cards,
  and four completed Northrend decks.
- Reconcile every pigment, ink, parchment, Eternal, and other input against the
  frozen Phase 1 evidence or exact vendor catalog. Current Hellscream listings
  remain competition evidence only and never set a baseline.
- Preserve the Book of Glyph Mastery recipe-drop baseline at 12g 50s Quick, 25g
  Target, and 60g High. Its saved note records the user-reported average sale
  estimate from 2026-08-03 and the original 150g / 300g / 700g baseline.
- Keep exact audited 3.3.5 recipe diagnostics separate from estimated finished-
  item sale value.

## Finished-Output Coverage

- The 60 currently curated level-80 glyphs: six each for Death Knight, Druid,
  Hunter, Mage, Paladin, Priest, Rogue, Shaman, Warlock, and Warrior.
- Five stat scrolls plus Runescroll of Fortitude.
- Certificate of Ownership and the two level-77 BoE caster off-hands.
- All 32 possible exact outcomes from Darkmoon Card of the North: eight each
  from the Nobles, Chaos, Prisms, and Undeath sets.
- Nobles, Chaos, Prisms, and Undeath completed decks.
- Armor Vellum III and Weapon Vellum III remain covered by their saved Phase 1B
  review in the Enchanter-only section.
- Exclude BoP, self-only, nontradeable, temporary, conjured, or invalid outputs.

## Inscription-Specific Price Checks

- Compare glyphs within the same class and practical raid, PvP, leveling, or
  utility role. Their recipe floor is exact ink plus parchment cost, but learned
  recipe access is not an unsupported hidden premium.
- Compare buff scrolls by actual stat/effect and output quantity. Runescroll of
  Fortitude produces five scrolls per craft; all prices and sale evidence remain
  per finished scroll.
- Treat Certificate of Ownership as a one-at-a-time Hunter utility market and
  the two caster off-hands as slow one-at-a-time BoE gear.
- Darkmoon Card of the North is one random roll across 32 possible exact cards.
  Its ingredient cost is a random-roll diagnostic, not a guaranteed floor for
  any named card. Rank exact cards within their own set and preserve missing-rank
  scarcity without pretending a specific card can be crafted directly.
- Treat each completed deck as a deterministic eight-card combination. Its exact
  card opportunity cost remains separate from the deck's estimated sale value.
- Preserve qualified Hellscream completed sales when available. Shrink sparse
  or concentrated sales toward a fixed comparable-cohort estimate.
- Review every proposed Target change over 50%; retain the old frozen band when
  neither qualified local sales nor at least two comparison realms support it.

## Profession Use, Notes, and Ordering

- Recheck all 107 outputs against `data/ah-profession-use-audit.json`.
- Keep Armor Vellum III and Weapon Vellum III in their dedicated Enchanter-only
  section; the remaining 105 outputs have no hard profession requirement.
- Preserve exact glyph effects, class use, scroll effect, equipment stats,
  Darkmoon rank/set, and deck reward purpose in item-specific notes.
- Preserve the exact recipe-and-mats mouseover link for every row.
- Use one shared `*` Evidence Pricing and craft-diagnostic note for the guide;
  keep random-card and completed-deck rules there instead of repeating them.
- Sort every non-progression section by Target buyout per item, highest first.

## Acceptance Checks

- [x] Gate 0 inventory and evidence boundaries recorded.
- [x] All 105 remaining outputs have a saved before/after evidence review.
- [x] The two vellum bands and evidence references remain unchanged.
- [x] The Book of Glyph Mastery band and full user/original-baseline provenance
  remain unchanged.
- [x] All 107 exact recipes, output counts, item IDs, rarity, binding, stack,
  and auction-eligibility records are verified.
- [x] Random cards use a random-roll diagnostic; completed decks use exact
  eight-card opportunity cost.
- [x] All Target moves over 50% have an explicit reviewer decision.
- [x] One shared methodology note replaces repeated pricing boilerplate.
- [x] Canonical guide, ordering, search, tooltip, currency, rarity, profession
  eligibility, UTF-8, and desktop/mobile validation pass.

## Evidence Log

- Phase 2 Evidence Pricing started — 2026-08-06: the missing Inscription plan
  was added and the 107-output catalog was frozen. Armor Vellum III and Weapon
  Vellum III retain their completed Phase 1B evidence, leaving 105 outputs for
  this batch: 60 glyphs, six buff scrolls, three utility or BoE items, 32 exact
  random Darkmoon cards, and four completed decks. All 107 outputs have exact
  saved recipe records. The two vellums are the only hard profession
  requirements and already occupy the Enchanter-only section. The Book of Glyph
  Mastery remains outside the crafted catalog with its user-set 25g Target and
  original 150g / 300g / 700g baseline recorded. Phase 1 inputs remain frozen,
  current Hellscream listings remain competition-only evidence, and random-roll
  cost remains separate from exact-card sale value. Work is local and nothing
  has been published.
- Phase 2 Evidence Pricing completed — 2026-08-06: all 105 reviewed outputs
  received saved before/after bands, exact recipe or opportunity-cost
  diagnostics, sanitized completed-sale coverage, six-source comparison
  coverage, confidence, and an explicit reviewer decision. No item had
  completed-sale evidence; all 105 had three-realm comparison coverage. The
  only Target candidate over 50%, Runescroll of Fortitude, moved from 20g to
  5g 40s with three-realm support and remains above its 2g 95s per-scroll craft
  diagnostic. The pass changed all 105 bands; 51 Targets rose, 53 fell, and one
  stayed unchanged. Nine exact card estimates fall below at least one random-
  roll-cost band, which is valid because named cards are not directly
  craftable. Chaos Deck and Undeath Deck fall below their current eight-card
  opportunity cost and retain shared do-not-assemble guidance. A dependency-
  audit defect that forced Evidence-priced decks up to craft cost was fixed;
  deck sale bands now remain independent while their exact card totals stay
  visible. The two vellums and the Book of Glyph Mastery user baseline remained
  unchanged. The guide now uses one shared Evidence Pricing note, exact recipe
  mouseovers, item-specific effects, rarity colors, fixed Ace-through-Eight card
  order, target-price ordering elsewhere, and current search metadata. Work
  remains local and nothing has been published.
- Container coverage addendum — 2026-08-08: Added Scribe's Satchel as a
  vendor-owned 10-slot Inscription-supplies container. The pinned vendors carry
  two or three with a 2.5-hour restock, so the 1g Target is a limited-stock
  convenience reference rather than a crafted or scarcity claim. No crafted
  Inscription band changed and nothing was published.
