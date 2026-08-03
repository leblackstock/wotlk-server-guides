# Herbalism AH Audit Plan

- Status: `planned`
- Existing guide: `guides/herbalism-herbs-ah-price-guide.html`
- Work type: gathering-price audit; no normal crafted catalog
- Suggested order: 8

> Hard gate: complete the current-price audit before any herb-related crafted
> expansion is calculated elsewhere. Follow [the shared Gate 0](README.md#gate-0-audit-current-prices-before-adding-crafteds).

## Current-Price Audit

- Recheck all 53 current herb and vendor/convenience rows across Northrend,
  Outland, and Classic.
- Reconcile every duplicated herb with Alchemy and Inscription input references.
- Verify item IDs, rarity, stack size, zone/tier, normal gathering source, and
  whether any row is actually a vendor, quest, or special-source item.
- Use live supply depth as well as low buyout; scarce old herbs need wider,
  clearly evidenced bands rather than copied Northrend pricing.

## Profession Boundary

Herbalism has no normal tradeable crafted-item catalog in WotLK 3.3.5.
Lifeblood and profession passives are not AH items. The completed work should
therefore remain a material audit and dependency refresh, not invent crafted
Herbalism rows.

## Profession-Specific Price Checks

- Compare each herb's direct Alchemy use with its Inscription milling demand;
  this supports the demand label but does not create a guaranteed price floor.
- Check Frost Lotus and other scarce byproducts separately from ordinary zone
  herbs.
- When a herb feeds a current canonical crafted recipe, update the shared input
  reference before recalculating the finished item.
- Keep vendor/fixed-source prices separate from gathered-market observations.

## Notes to Verify

- State the major real demand driver: flask/elixir/potion tier, milling tier,
  leveling bottleneck, or scarce legacy recipe.
- Avoid repeating `used by Alchemy and Inscription` on every row. Use one shared
  note and reserve row notes for the herb's distinctive demand or scarcity.
- Do not claim a best farming zone without verified server spawn behavior.

## Acceptance Checks

- [ ] All current prices were rechecked and evidence recorded.
- [ ] Duplicate herb prices agree across guides.
- [ ] Alchemy/Inscription dependency references use the refreshed values.
- [ ] No non-item Herbalism spell is presented as a craftable AH item.
- [ ] Rarity, source, stack, demand, and notes are accurate.
- [ ] Shared validation in `README.md` passes.

## Evidence Log

- Audit date:
- Live AH observations:
- Item/source references checked:
- Server-specific gathering findings:
- Decisions and unresolved items:
- Completion summary:
