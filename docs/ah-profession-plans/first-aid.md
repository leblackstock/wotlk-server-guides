# First Aid AH Expansion Plan

- Status: `planned`
- Existing guide: none dedicated
- Work type: small full catalog plus guide-placement decision
- Suggested order: 7

> Hard gate: audit current cloth prices and any existing bandage/anti-venom rows
> before adding crafted rows. Follow [the shared Gate 0](README.md#gate-0-audit-current-prices-before-adding-crafteds).

## Current-Price Audit

- Audit every cloth input in `guides/tailoring-cloth-ah-price-guide.html` and
  reconcile duplicates before calculating bandage prices.
- Search all AH guides for bandages, anti-venoms, venom sacs, and related
  reagents; correct or consolidate any existing rows first.
- Check the live AH for actual supply and sales. These items may be technically
  auctionable but too thin to justify broad price confidence.
- Verify server-specific tradeability, stack sizes, healing values, level
  requirements, and whether First Aid behavior matches 3.3.5.

## Placement Decision

Choose and record one option before implementation:

- Create `guides/first-aid-ah-price-guide.html` if the verified catalog and AH
  demand support a useful standalone page; or
- Add a clearly labeled First Aid crafted block to the Tailoring cloth guide if
  the catalog is too small for a dedicated page.

Do not mix First Aid outputs into Tailoring's crafted source of truth merely
because both consume cloth.

## Crafted Coverage

- Verify all normal and heavy bandage ranks from Linen through Frostweave.
- Verify Anti-Venom, Strong Anti-Venom, Powerful Anti-Venom, and any other
  apparent First Aid outputs individually; include only valid tradeable 3.3.5
  items with a real recipe spell.
- Exclude quest-only medical items, battleground-only supplies, conjured items,
  invalid ranks, and non-tradeable outputs.

## Profession-Specific Price Checks

- Calculate exact cloth or venom-sac cost per finished item using the guaranteed
  recipe yield.
- Compare finished bandage value with the cloth opportunity cost; explicitly
  flag convenience-only listings that trade below material value.
- Keep demand conservative and use small stacks unless live evidence supports
  larger PvP, leveling, or achievement purchases.

## Notes to Verify

- State healing/cleansing effect, channel duration if relevant, required level,
  and likely PvP/leveling/achievement use.
- Distinguish normal and heavy ranks clearly; do not reuse a generic note for
  all bandages.
- Explain weak or obsolete demand honestly.

## Acceptance Checks

- [ ] Current cloth/reagent price audit completed and recorded.
- [ ] Guide placement is decided and documented.
- [ ] Every First Aid recipe has an include/exclude decision.
- [ ] Output quantities, effects, levels, binding, and rarity are verified.
- [ ] Thin-market/fallback prices are clearly labeled.
- [ ] Shared validation in `README.md` passes.

## Evidence Log

- Audit date:
- Placement decision:
- Live AH observations:
- Recipe/item sources checked:
- Server-specific findings:
- Decisions and unresolved items:
- Completion summary:
