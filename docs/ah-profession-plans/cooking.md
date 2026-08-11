# Cooking AH Expansion Plan

- Status: `complete — stat and dual-recovery coverage correction, 2026-08-10`
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

- Publication — 2026-08-11: Commit `670de1c` (`feat: group useful cooked
  foods`) was pushed to `origin/main`. GitHub Pages deployment run
  `31457583668` succeeded, and the public guide was verified at desktop and
  mobile widths with all three corrected headings, all ten promoted rows, the
  `2026-08-11` footer, no page overflow, and no console errors.
- Stat and dual-recovery coverage correction completion — 2026-08-10: Moved
  all ten qualifying rows into accurately named expansion-specific stat-bonus
  and dual-recovery sections. The recovery sections now retain health-only and
  mana-only foods. Canonical data, saved evidence section labels, the evidence
  report, rendered guide, search index, and tooltip assets agree. A comparison
  with the prior revision confirmed zero price-band, recipe-floor, demand, or
  demand-class changes. All 40 AH regression tests, the full site test suite,
  and local desktop/mobile browser checks passed. Nothing was published.
- Stat and dual-recovery coverage correction start — 2026-08-10: Audited all
  162 Cooking rows by their saved item effects. Ten qualifying foods were
  already evidence-priced but were filed under recovery-only sections: four
  Wrath foods that restore both health and mana, four Outland foods that grant
  Stamina and Spirit, one Outland food that restores both resources, and one
  Classic food that restores both resources. They move into their expansion's
  stat-food section without changing price bands, demand labels, recipe floors,
  or evidence confidence. Pure health-only and pure mana-only foods remain in
  recovery sections. Nothing has been published.
- Phase 2 completion — 2026-08-08: Reviewed all 162 auctionable Cooking
  outputs. All 972 comparison requests resolved on the initial pass; coverage
  reached all three realms for 159 outputs and two realms for three. No
  completed-sale history was available. All 70 Target changes over 50% had at
  least two-realm support and were accepted. The pass changed all 162 price
  bands; 88 Targets rose, 71 fell, and three stayed unchanged. Fifty final
  estimates fall below at least one exact recipe-floor band and retain shared
  do-not-craft guidance. The four Cook-required feasts and Rogue-only Thistle
  Tea remain isolated in their correct buyer sections. Evidence references,
  exact recipes, notes, ordering, search metadata, and the guide footer were
  refreshed locally. Nothing was published.
- Phase 2 start — 2026-08-08: Froze all 162 auctionable Cooking outputs across
  13 sections. Phase 1B already reviewed the 118 fish, meat, egg, spice,
  clam/pearl, and vendor references shared with Fishing; no finished Cooking
  output is owned by that material batch, so all 162 outputs enter this review.
  The four feast objects remain isolated in the Cook-required section and
  Thistle Tea remains Rogue-only. Phase 1 inputs stay frozen, current Hellscream
  listings remain competition-only evidence, exact batch yields remain in the
  recipe floor, and failed comparisons receive the required 2-, 5-, and
  10-second waited retries. Nothing has been published.
- Audit date: 2026-08-03
- Listing concentration observations (not valuation evidence): The saved Horde
  scan remains unusable for valuation because the user and friends account for
  at least half of listed units. No active listing set or raised a Cooking
  baseline or finished-food price.
- Recipe/item sources checked: WotLKDB's complete 181-record Cooking spell list
  and recipe quantities; Wowhead WotLK item tooltips for binding, rarity,
  requirements, stack size, and effects; AzerothCore's build-12340 item baseline
  for canonical item identity and tradeability.
- Baseline findings: The corrected 162-recipe catalog consumes 141 distinct
  ingredients. Twelve have exact coin-vendor records and ten use clearly
  labeled comparison-based fallback bands; every other tradeable input remains
  covered by its saved baseline or recursively audited crafted value. None came
  from active listings.
- Output/server findings: 174 Cooking spells create 169 distinct item outputs.
  Clamlette Magnifique and Bread of the Dead are Bind on Pickup. Pumpkin Pie,
  Spice Bread Stuffing, Slow-Roasted Turkey, Candied Sweet Potato, and Cranberry
  Chutney have seven-day real-time durations, which AzerothCore rejects from AH
  posting, leaving 162 auctionable outputs. No verified Hellscream override was
  available, so the catalog documents standard 3.3.5 behavior and keeps server
  checks explicit.
- Decisions and unresolved items: Great Feast, Fish Feast, Gigantic Feast, and
  Small Feast are isolated because placing them requires Cooking. Thistle Tea
  has its own Rogue-only section. Raw fish, meats, eggs, spices, and vendor
  ingredients remain in material/vendor coverage only when they are auctionable.
  Sparkling Apple Cider remains a cost-only Hot Apple Cider input because its
  two-day duration prevents auctioning. Provisional fallback inputs should be
  replaced only by qualifying realized-sale or measured-yield evidence.
- Completion summary: Added 162 crafted rows in 13 sections with exact effect
  notes, recipe-and-material mouseovers, common-quality rarity coloring,
  non-circular price bands, price-descending section order, and current search
  and tooltip assets. The complete AH validation and desktop/mobile browser
  smoke suite passed before publication.
- Eligibility correction — 2026-08-04: Removed the five duration-limited
  Pilgrim's Bounty outputs, their five vendor rows, and the now-unused Wild
  Turkey baseline. Sparkling Apple Cider remains only as an explicit cost
  input. The 2,417-recipe non-Enchanting snapshot was refreshed, and a pinned
  AzerothCore
  auction-eligibility audit to prevent duration, conjured, or invalid-binding
  items from returning.
- Material-baseline refresh — 2026-08-06: Phase 1B rechecked 118 fish, meat,
  egg, spice, clam/pearl, and vendor references shared with Fishing. Four
  inherit Phase 1A, 13 retain exact vendor pricing, and 101 newly reviewed
  material bands changed. Finished Cooking outputs remain outside this phase.
