# Leatherworking AH Expansion Plan

- Status: `complete — Phase 2 Evidence Pricing, 2026-08-08`
- Existing guide: `guides/skinning-leatherworking-materials-ah-price-guide.html`
- Work type: full crafted catalog
- Suggested order: 4

> Hard gate: finish and record the baseline evidence audit before adding crafted
> rows. Follow [the shared Gate 0](README.md#gate-0-establish-non-circular-baselines-before-adding-crafteds).

## Baseline Evidence Audit

- Recheck all 58 current rows, including Northrend leather/hides/scales,
  Arctic Fur, scraps, older materials, Eternals, salt, leg armors, kits, and
  drums.
- Reconcile shared reagents with cross-profession, Skinning, Mining, and
  Enchanting rows before costing finished items.
- Recalculate current Heavy Borean Leather and every listed armor kit, leg
  armor, and drum from exact recipe counts.
- Verify any server-specific scrap conversion, Arctic Fur exchange, and
  specialization behavior separately from AH prices.

## Crafted Coverage

- All tradeable leather conversions, armor kits, leg armors, drums, quivers or
  ammo pouches that exist in 3.3.5, and other deterministic utility outputs.
- Tradeable BoE leather/mail gear across Wrath, Outland, and Classic, including
  trainer, specialization, reputation, world-drop, and raid patterns.
- Keep Skinning drops in material sections and Leatherworking conversions in
  the crafted source of truth.
- Exclude self-only fur linings, BoP gear, invalid specialization records, and
  temporary applications that do not create an auctionable item.

## Profession-Specific Price Checks

- Resolve scraps-to-leather, leather-to-heavy-leather, cured hides, and other
  intermediates recursively before pricing finished goods.
- Price kits and leg armors from their exact recipes and actual level/use
  restrictions; do not copy one margin across all ranks.
- Price specialization and raid-pattern gear at exact craft cost, but describe
  access and slow turnover separately.
- Account for expensive Eternals, orbs, scales, and specialty hides at their
  reconciled current bands.

## Notes to Verify

- Kits/leg armors: exact effect, eligible slot/type, level restrictions, and
  likely tank, physical DPS, caster, healer, or PvP buyer.
- Drums: exact buff/effect, group use, and any server-rule caveat in one shared
  note rather than every row.
- Gear: armor type, slot, role, tier, binding, specialization access, and
  realistic turnover.

## Acceptance Checks

- [x] Baseline evidence audit completed and recorded.
- [x] All material conversions are canonical and recursively priced.
- [x] Every tradeable Leatherworking output has an include/exclude decision.
- [x] Self-only fur linings and BoP crafts are absent.
- [x] Existing leg armor/kit/drum rows were recalculated, not merely retained.
- [x] Shared validation in `README.md` passes.

## Evidence Log

- Phase 2 start — 2026-08-08: Froze all 490 tradeable Leatherworking outputs
  across 29 sections. Fourteen leather and cured-hide intermediates retain
  completed Phase 1B material evidence, leaving 476 finished outputs for this
  review. Phase 1 inputs remain frozen, active Hellscream listings remain
  competition-only evidence, and exact recipe cost remains a separate
  craftability diagnostic. The shared comparison fetcher now waits and retries
  failed requests three times before recording a final failure. Nothing has
  been published.
- Phase 2 completion — 2026-08-08: Reviewed all 476 finished outputs. All
  2,856 comparison requests resolved on the initial pass, so no waited retry
  was needed. Coverage reached all three realms for 394 outputs, two realms for
  67, one realm for nine, and no realm listings for six. One Tough Scorpid
  Shoulders sale was low-confidence and received 25% weight; no sale passed the
  medium-confidence gate. Of 128 Target candidates whose movement exceeded
  50%, 125 had at least two-realm support and were accepted, while three lacked
  enough coverage and retained their frozen bands. The pass changed 473 price
  bands; 231 Targets rose, 220 fell, and 25 stayed unchanged. Two hundred
  eighty-four final estimates remain below at least one exact recipe-floor band
  and retain shared do-not-craft guidance. The 14 Phase 1B leather and
  cured-hide intermediates remained unchanged. Evidence references, shared
  notes, exact recipes, profession-use sections, ordering, search metadata, and
  the guide footer were refreshed locally. Nothing was published.
- Audit date: 2026-08-03.
- Listing concentration observations (not valuation evidence): The saved Horde
  scan remains unusable for valuation because the user and friends control at
  least 50% of listed units. No current listing price entered the baseline or
  set a crafted band.
- Recipe/item sources checked: WotLKDB's complete Leatherworking skill list in
  six non-overlapping rank windows (548 spell records), exact recipe and output
  quantities, and AzerothCore WotLK `item_template` build 12340 for item IDs,
  rarity, binding, skill gates, bag family, stack limit, and equipment data.
- Conversion/server findings: Gate 0 passed against 662 pre-expansion frozen
  references and 68 shared crafted outputs. The live guide contained 53 priced
  rows rather than the plan's stale estimate of 58. The finished catalog uses
  saved opportunity cost for tradeable leather and exact minimum guaranteed
  outputs. It covers 165 direct inputs; 28 previously absent legacy inputs were
  added as explicit fallback-confidence references, never as current values.
- Decisions and unresolved items: Included 490 distinct tradeable outputs in
  29 sections. Excluded 30 Bind on Pickup items, eight duplicate Alliance Trial
  records, and the Gordok Ogre Suit already owned by Tailoring. Ten self-only
  fur-lining or leg-reinforcement spells create no tradeable item and remain
  excluded. Five Outland drums are isolated as Leatherworker-only; six specialty
  bags are labeled for Leatherworking, Mining, or Inscription buyers; the two
  Wrath raid drums remain explicitly general-use. All 28 new input fallbacks
  remain provisional pending qualifying realized sales or measured yields.
- Completion summary: Canonical data, 2,214-output non-Enchanting recipe audit,
  shared price reconciliation, recipe mouseovers, item tooltips, rarity colors,
  search index, price ordering, profession-use sections, and the 2026-08-03
  footer were regenerated. All Python tests, `npm test`, and the desktop/mobile
  Playwright smoke test passed. Cooking is the next planned profession.
- Material-baseline refresh — 2026-08-06: Phase 1B rechecked 51 leather, hide,
  scale, scrap, salt, combine, and vendor references. Seven inherit Phase 1A,
  six retain exact vendor pricing, and 38 newly reviewed material bands changed.
  Finished Leatherworking outputs remain outside this phase except material
  intermediates explicitly owned by the input market.
