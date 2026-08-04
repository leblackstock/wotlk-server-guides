# Fishing AH Audit Plan

- Status: `complete` — 2026-08-04
- Existing guide: `guides/fishing-cooking-materials-ah-price-guide.html`
- Work type: gathering-price audit; finished food belongs to Cooking
- Suggested order: 10

> Hard gate: complete the baseline evidence audit before Cooking crafted prices are
> calculated. Follow [the shared Gate 0](README.md#gate-0-establish-non-circular-baselines-before-adding-crafteds).

## Baseline Evidence Audit

- Audit raw fish, clams, pearls, quest fish, rare catches, junk/vendor items,
  and fishing-source utility rows across 146 searchable rows and 4
  reference-only rows in the current combined guide.
- Reconcile raw fish and pearl prices with Cooking, Jewelcrafting, and
  cross-profession references.
- Separate current per-fish, per-clam, per-pearl, and per-stack values; correct
  any unit/stack ambiguity before Cooking uses the inputs.
- Verify tradeability, rarity, stack size, catch/source, quest status, and actual
  live supply. Do not force an AH band onto items that should normally be
  vendored or cannot be auctioned.

## Profession Boundary

Fishing has no normal recipe-based crafted output catalog. Cooked food belongs
to Cooking; crafted lures and devices belong to Engineering; poles, hats,
lines, journals, and vendor lures retain their actual drop, quest, or vendor
source. Do not describe these as Fishing-crafted items.

## Profession-Specific Price Checks

- Refresh every fish used by Cooking before calculating the finished food.
- Price clams by the clam item itself. Pearl expected value may inform a value
  note, but no individual clam guarantees a specific pearl.
- Treat rare catches and quest fish as thin, purpose-specific markets rather
  than copying ordinary food-fish bands.
- Keep vendor trash and low-demand catches clearly separated from realistic AH
  listings.

## Notes to Verify

- State the distinctive use: raid food input, pet food, quest/turn-in,
  achievement, off-hand/novelty, pearl source, or vendor value.
- Put general fishing/Cooking linkage in one shared note and keep each row's
  note specific.
- Avoid unsupported best-pool, catch-rate, or best-zone claims on a custom
  server.

## Acceptance Checks

- [x] Every saved Fishing-domain baseline has a source type and confidence.
- [x] Cooking ingredient references use refreshed fish prices.
- [x] Random clam contents are not priced as guaranteed output.
- [x] Utility items retain their true profession/source ownership.
- [x] Non-tradeable and vendor-only items are clearly handled.
- [x] Shared validation in `README.md` passes.

## Evidence Log

- Audit date: 2026-08-04
- Listing concentration observations (not valuation evidence): The user reported that their auctions plus friends' auctions make up approximately 50% of all AH listings. This fails the 30% concentration guard, so no active listing price was used.
- Item/source references checked: Audited 146 searchable rows: 127 frozen pre-scan baselines and 19 canonical vendor rows, plus 4 reference-only catches. Verified exact item IDs, rarity, maximum stack, and binding against AzerothCore `item_template` commit `e0fe11ba46b885a01e4a4038001e0055822cc7ba`; reconciled fish, meat, pearl, and clam references with Cooking, Jewelcrafting, and cross-profession rows.
- Server-specific fishing findings: No measured catch dataset or qualifying realized-sale dataset was available. No custom-server pool, catch-rate, or active-listing median was introduced.
- Decisions and unresolved items: No price bands changed; all 146 searchable rows already matched the accepted frozen/vendor evidence. Restored the exact item name Chunk o' Basilisk; corrected Dark Herring and Siren's Tear rarity, Hot/Soothing Spices rarity, and impossible Bear Flank/Okra stack sizes. Random clam contents remain value context only, never guaranteed pearl output.
- Completion summary: Fishing remains the gathering/source side of the combined guide; all finished food stays Cooking-owned. Baseline coverage, duplicate prices, unit handling, item metadata, ownership, vendor separation, rare-catch notes, and Cooking dependencies passed validation.
