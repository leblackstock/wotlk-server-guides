# Leatherworking AH Expansion Plan

- Status: `complete — 2026-08-03`
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
