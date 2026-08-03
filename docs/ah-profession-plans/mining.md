# Mining AH Expansion Plan

- Status: `planned`
- Existing guide: `guides/mining-smithing-ah-price-guide.html`
- Work type: smelting-output catalog
- Suggested order: 6

> Hard gate: finish and record the baseline evidence audit before adding smelted
> outputs. Follow [the shared Gate 0](README.md#gate-0-establish-non-circular-baselines-before-adding-crafteds).

## Baseline Evidence Audit

- Recheck all current ore, bar, alloy, and stone rows in the 88-row guide before
  changing or expanding smelting coverage.
- Reconcile ores/bars with Blacksmithing and Engineering, Eternals with cross-
  profession materials, and rod/stone rows with their owning professions.
- Compare every current bar price with the exact current ore input cost. Record
  profitable conversions and bars trading below ore opportunity cost.
- Verify the server's Titansteel cooldown behavior and any custom smelting
  ratios or recipes.

## Crafted Coverage

- All valid tradeable smelted bars and alloys from Wrath, Outland, and Classic,
  including multi-metal and elemental recipes.
- Keep raw ore and mining-node value as Mining material/reference coverage.
- Blacksmithing stones, rods, keys, gear, and enhancements belong to the
  Blacksmithing plan even if they remain visible in the combined guide.
- Exclude Mining self-buffs, learned passive effects, and any spell without a
  tradeable item output.

## Profession-Specific Price Checks

- Use exact ore/bar ratios and guaranteed bar yield. Check recipes that produce
  multiple bars or consume existing bars rather than raw ore.
- Price alloys recursively from their component bars and elementals.
- Show when smelting destroys value: the floor is the current opportunity cost
  of inputs, but the note should recommend buying rather than smelting if the
  live finished market is persistently lower.
- Keep cooldown/access information separate from the deterministic material
  calculation.
- Recheck mining-node averages after ore, stone, gem, and elemental inputs move.

## Notes to Verify

- Identify the major downstream buyers: Blacksmithing, Engineering,
  Jewelcrafting, or legacy leveling.
- State exact smelting ratios where they help buyers compare ore and bars.
- Mark cooldown, trainer, reputation, or rare-recipe access only when verified.
- Recommend bar stacks that match common recipe quantities, not just max stack.

## Acceptance Checks

- [ ] Baseline evidence audit completed and recorded.
- [ ] Every smelting spell has an include/exclude decision.
- [ ] Ore-to-bar and alloy calculations use exact outputs.
- [ ] Blacksmithing-owned crafts are not duplicated as Mining outputs.
- [ ] Node-value reference math was refreshed after material changes.
- [ ] Shared validation in `README.md` passes.

## Evidence Log

- Audit date:
- Listing concentration observations (not valuation evidence):
- Recipe/item sources checked:
- Smelting/cooldown findings:
- Decisions and unresolved items:
- Completion summary:
