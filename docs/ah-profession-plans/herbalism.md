# Herbalism AH Audit Plan

- Status: `complete` — 2026-08-04
- Existing guide: `guides/herbalism-herbs-ah-price-guide.html`
- Work type: gathering-price audit; no normal crafted catalog
- Suggested order: 8

> Hard gate: complete the baseline evidence audit before any herb-related crafted
> expansion is calculated elsewhere. Follow [the shared Gate 0](README.md#gate-0-establish-non-circular-baselines-before-adding-crafteds).

## Baseline Evidence Audit

- Recheck all 52 searchable herb and vendor/convenience rows across Northrend,
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

- [x] Every saved baseline has a source type and confidence.
- [x] Duplicate herb prices agree across guides.
- [x] Alchemy/Inscription dependency references use the refreshed values.
- [x] No non-item Herbalism spell is presented as a craftable AH item.
- [x] Rarity, source, stack, demand, and notes are accurate.
- [x] Shared validation in `README.md` passes.

## Evidence Log

- Audit date: 2026-08-04
- Listing concentration observations (not valuation evidence): The user reported that their auctions plus friends' auctions make up approximately 50% of all AH listings. This fails the 30% concentration guard, so no active listing price was used.
- Item/source references checked: Audited 52 searchable rows: 47 frozen pre-scan baselines and 5 canonical vendor rows. Verified exact item IDs, rarity, maximum stack, and binding against AzerothCore `item_template` commit `e0fe11ba46b885a01e4a4038001e0055822cc7ba`; reconciled 35 duplicated herb/supply names with Alchemy and Inscription.
- Server-specific gathering findings: No measured route or qualifying realized-sale dataset was available. No custom-server farming rate, spawn claim, or active-listing median was introduced.
- Decisions and unresolved items: No price bands changed; all 52 rows already matched the accepted frozen/vendor evidence. Corrected Frost Lotus, Fel Lotus, and Black Lotus to uncommon rarity in both Herbalism and Alchemy, and replaced three generic herb notes with specific flask, pigment, and milling demand.
- Completion summary: Herbalism remains a 52-row gathering/supply guide with no invented crafted outputs. Baselines, duplicate prices, ownership, rarity, stacks, demand notes, and dependent Alchemy/Inscription references passed validation.
