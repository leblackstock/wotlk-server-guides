# Leatherworking AH Expansion Plan

- Status: `planned`
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

- [ ] Baseline evidence audit completed and recorded.
- [ ] All material conversions are canonical and recursively priced.
- [ ] Every tradeable Leatherworking output has an include/exclude decision.
- [ ] Self-only fur linings and BoP crafts are absent.
- [ ] Existing leg armor/kit/drum rows were recalculated, not merely retained.
- [ ] Shared validation in `README.md` passes.

## Evidence Log

- Audit date:
- Listing concentration observations (not valuation evidence):
- Recipe/item sources checked:
- Conversion/server findings:
- Decisions and unresolved items:
- Completion summary:
