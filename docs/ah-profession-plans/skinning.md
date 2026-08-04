# Skinning AH Audit Plan

- Status: `complete` — 2026-08-04
- Existing guide: `guides/skinning-leatherworking-materials-ah-price-guide.html`
- Work type: gathering-price audit; conversions belong to Leatherworking
- Suggested order: 9

> Hard gate: complete the baseline evidence audit before Leatherworking crafted
> prices are calculated. Follow [the shared Gate 0](README.md#gate-0-establish-non-circular-baselines-before-adding-crafteds).

## Baseline Evidence Audit

- Audit the 37 searchable raw/supply rows and 5 conversion-reference rows in
  the current combined guide; Leatherworking crafted blocks remain separate.
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

- [x] Every saved raw-material baseline has a source type and confidence.
- [x] Duplicate prices agree across guides.
- [x] Raw materials and Leatherworking conversions have clear ownership.
- [x] Leatherworking's ingredient references use refreshed values.
- [x] Item rarity, stack, source, and demand notes are accurate.
- [x] Shared validation in `README.md` passes.

## Evidence Log

- Audit date: 2026-08-04
- Listing concentration observations (not valuation evidence): The user reported that their auctions plus friends' auctions make up approximately 50% of all AH listings. This fails the 30% concentration guard, so no active listing price was used.
- Item/source references checked: Audited 37 searchable rows: 31 frozen pre-scan baselines and 6 canonical vendor rows, plus 5 reference-only conversion checks. Verified exact item IDs, rarity, maximum stack, and binding against AzerothCore `item_template` commit `e0fe11ba46b885a01e4a4038001e0055822cc7ba`; reconciled shared inputs with Leatherworking and cross-profession rows.
- Server-specific gathering findings: No measured skinning route or qualifying realized-sale dataset was available. No custom-server drop rate or active-listing median was introduced.
- Decisions and unresolved items: No price bands changed; all 37 searchable rows already matched the accepted frozen/vendor evidence. Corrected Arctic Fur to rare, Green Whelp Scale to its true 5-item maximum, and Crystallized Water/Shadow to their true 10-item maximum across every guide. Conversion values remain tied to the saved per-item baselines.
- Completion summary: Skinning remains a raw-material audit. All Leatherworking conversions and finished outputs stay in the Leatherworking-owned reference/crafted sections; baseline coverage, duplicate prices, item metadata, ownership, and conversion estimates passed validation.
