# Cooking AH Expansion Plan

- Status: `complete` — 2026-08-03
- Existing guide: `guides/fishing-cooking-materials-ah-price-guide.html`
- Work type: full crafted catalog
- Suggested order: 5

> Hard gate: finish and record the baseline evidence audit before adding crafted
> rows. Follow [the shared Gate 0](README.md#gate-0-establish-non-circular-baselines-before-adding-crafteds).

## Baseline Evidence Audit

- Audit the current finished-food/drink rows and every fish, meat, egg, spice,
  and vendor ingredient that feeds a Cooking recipe in the existing shared guide.
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

- [x] Baseline evidence audit completed and recorded.
- [x] Every valid tradeable Cooking output has an include/exclude decision.
- [x] Batch yields and per-item costs are verified by recipe.
- [x] Level-80 buff-food notes identify exact stats and likely roles.
- [x] Fishing materials and Cooking outputs remain clearly owned.
- [x] Shared validation in `README.md` passes.

## Evidence Log

- Audit date: 2026-08-03
- Listing concentration observations (not valuation evidence): The saved Horde
  scan remains unusable for valuation because the user and friends account for
  at least half of listed units. No active listing set or raised a Cooking
  baseline or finished-food price.
- Recipe/item sources checked: WotLKDB's complete 181-record Cooking spell list
  and recipe quantities; Wowhead WotLK item tooltips for binding, rarity,
  requirements, stack size, and effects; AzerothCore's build-12340 item baseline
  for canonical item identity and tradeability.
- Baseline findings: The 167 included recipes consume 148 distinct ingredients:
  118 already had frozen references, three already had exact vendor records,
  two are recursively audited crafted inputs, 14 received exact vendor records,
  and 11 received clearly labeled comparison-based fallback bands. None came
  from active listings.
- Output/server findings: 174 Cooking spells create 169 distinct item outputs.
  Five Pilgrim's Bounty outputs have faction-alternate recipes and were
  consolidated to one output each using the Horde ingredient route. Clamlette
  Magnifique and Bread of the Dead are Bind on Pickup, leaving 167 distinct
  tradeable outputs. No verified Hellscream override was available, so the
  catalog documents standard 3.3.5 behavior and keeps server checks explicit.
- Decisions and unresolved items: Great Feast, Fish Feast, Gigantic Feast, and
  Small Feast are isolated because placing them requires Cooking. Thistle Tea
  has its own Rogue-only section. Raw fish, meats, eggs, spices, and vendor
  ingredients remain in material/vendor coverage. Provisional fallback inputs
  should be replaced only by qualifying realized-sale or measured-yield
  evidence.
- Completion summary: Added 167 crafted rows in 13 sections with exact effect
  notes, recipe-and-material mouseovers, common-quality rarity coloring,
  non-circular price bands, price-descending section order, and current search
  and tooltip assets. The complete AH validation and desktop/mobile browser
  smoke suite passed before publication.
