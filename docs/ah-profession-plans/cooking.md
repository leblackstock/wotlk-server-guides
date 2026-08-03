# Cooking AH Expansion Plan

- Status: `planned`
- Existing guide: `guides/fishing-cooking-materials-ah-price-guide.html`
- Work type: full crafted catalog
- Suggested order: 5

> Hard gate: finish and record the baseline evidence audit before adding crafted
> rows. Follow [the shared Gate 0](README.md#gate-0-establish-non-circular-baselines-before-adding-crafteds).

## Baseline Evidence Audit

- Audit the current finished-food/drink rows and every fish, meat, egg, spice,
  and vendor ingredient that feeds a Cooking recipe in the 147-row shared guide.
- Reconcile raw fish/meat prices with their other guide appearances and vendor
  ingredients with the canonical vendor catalog.
- Recheck current feasts and level-80 buff foods before expanding older tiers.
- Verify whether the server changes Northern Spices, cooking-token recipes,
  output quantities, food buffs, feast behavior, or stack sizes.

## Crafted Coverage

- All tradeable deterministic Cooking outputs from Wrath, Outland, and Classic:
  stat food, feasts, recovery food, pet food, utility food/drink, and recipe-
  relevant quest or novelty food that can actually be auctioned.
- Separate level-80 raid/PvP buff food from leveling, pet, achievement, quest,
  and novelty markets.
- Keep raw catches under Fishing and raw meats under material coverage even
  when Cooking uses them.
- Exclude conjured food, non-tradeable quest outputs, invalid recipes, and food
  created by another profession or fixed vendor source.

## Profession-Specific Price Checks

- Verify the minimum guaranteed output for every recipe. Divide total input
  cost by the actual batch yield before assigning a per-food price.
- Use exact spice, fish, meat, and vendor quantities. Similar buffs from
  different recipes retain different floors because their inputs differ.
- Compare finished-food bands with raw-input opportunity cost and live finished
  competition; flag markets trading below craft cost.
- Do not assume random bonus yields or server-specific Cooking procs.

## Notes to Verify

- State the exact stat/effect, duration, level requirement, and well-fed status
  where relevant.
- Identify raid role or use precisely: tank, healer, caster DPS, melee, hunter,
  PvP, pet, leveling, achievement, or novelty.
- Feasts need exact party/raid coverage and buff behavior. Put shared server
  caveats in one note.
- Recommend stacks based on likely consumption: raid batches for staples and
  singles/small stacks for niche or achievement foods.

## Acceptance Checks

- [ ] Baseline evidence audit completed and recorded.
- [ ] Every valid tradeable Cooking output has an include/exclude decision.
- [ ] Batch yields and per-item costs are verified by recipe.
- [ ] Level-80 buff-food notes identify exact stats and likely roles.
- [ ] Fishing materials and Cooking outputs remain clearly owned.
- [ ] Shared validation in `README.md` passes.

## Evidence Log

- Audit date:
- Listing concentration observations (not valuation evidence):
- Recipe/item sources checked:
- Output/server findings:
- Decisions and unresolved items:
- Completion summary:
