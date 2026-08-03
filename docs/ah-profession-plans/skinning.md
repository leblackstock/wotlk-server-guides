# Skinning AH Audit Plan

- Status: `planned`
- Existing guide: `guides/skinning-leatherworking-materials-ah-price-guide.html`
- Work type: gathering-price audit; conversions belong to Leatherworking
- Suggested order: 9

> Hard gate: complete the baseline evidence audit before Leatherworking crafted
> prices are calculated. Follow [the shared Gate 0](README.md#gate-0-establish-non-circular-baselines-before-adding-crafteds).

## Baseline Evidence Audit

- Audit the raw leather, hide, scale, scrap, and specialty-drop rows in the
  current 58-row combined guide.
- Reconcile duplicates with Leatherworking and cross-profession material rows.
- Verify item ID, rarity, stack size, expansion/tier, creature/source category,
  and tradeability for every raw material.
- Check live market depth and per-unit values; hides and rare scales often have
  thin markets where one listing is not a reliable target.

## Profession Boundary

Skinning itself has no normal tradeable crafted outputs. Scrap-to-leather,
heavy-leather, cured-hide, armor-kit, drum, leg-armor, and gear recipes belong
to the Leatherworking plan even when their inputs come from Skinning.

## Profession-Specific Price Checks

- Compare scraps and their converted leather by exact recipe ratio, but store
  the conversion under Leatherworking ownership.
- Check raw versus heavy leather, regular versus cured hides, and common versus
  specialty scales without assuming a profitable conversion.
- Refresh Arctic Fur and other rare-material prices before any high-end
  Leatherworking calculation.
- Keep salt and other non-Skinning reagents tied to their correct drop/vendor
  source.

## Notes to Verify

- State the main Leatherworking tier/use or scarcity driver without repeating a
  generic profession note on every row.
- Distinguish gathered materials from Leatherworking-created intermediates.
- Avoid unsupported farming-rate claims on a custom server.

## Acceptance Checks

- [ ] Every saved raw-material baseline has a source type and confidence.
- [ ] Duplicate prices agree across guides.
- [ ] Raw materials and Leatherworking conversions have clear ownership.
- [ ] Leatherworking's ingredient references use refreshed values.
- [ ] Item rarity, stack, source, and demand notes are accurate.
- [ ] Shared validation in `README.md` passes.

## Evidence Log

- Audit date:
- Listing concentration observations (not valuation evidence):
- Item/source references checked:
- Server-specific gathering findings:
- Decisions and unresolved items:
- Completion summary:
