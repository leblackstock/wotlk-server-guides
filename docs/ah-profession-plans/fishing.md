# Fishing AH Audit Plan

- Status: `planned`
- Existing guide: `guides/fishing-cooking-materials-ah-price-guide.html`
- Work type: gathering-price audit; finished food belongs to Cooking
- Suggested order: 10

> Hard gate: complete the current-price audit before Cooking crafted prices are
> calculated. Follow [the shared Gate 0](README.md#gate-0-audit-current-prices-before-adding-crafteds).

## Current-Price Audit

- Audit raw fish, clams, pearls, quest fish, rare catches, junk/vendor items,
  and fishing-source utility rows in the current 147-row combined guide.
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

- [ ] All current Fishing-domain prices were rechecked and recorded.
- [ ] Cooking ingredient references use refreshed fish prices.
- [ ] Random clam contents are not priced as guaranteed output.
- [ ] Utility items retain their true profession/source ownership.
- [ ] Non-tradeable and vendor-only items are clearly handled.
- [ ] Shared validation in `README.md` passes.

## Evidence Log

- Audit date:
- Live AH observations:
- Item/source references checked:
- Server-specific fishing findings:
- Decisions and unresolved items:
- Completion summary:
