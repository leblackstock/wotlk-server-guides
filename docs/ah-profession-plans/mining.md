# Mining AH Expansion Plan

- Status: `complete — Phase 2 Evidence Pricing coverage, 2026-08-08`
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

- [x] Baseline evidence audit completed and recorded.
- [x] Every smelting spell has an include/exclude decision.
- [x] Ore-to-bar and alloy calculations use exact outputs.
- [x] Blacksmithing-owned crafts are not duplicated as Mining outputs.
- [x] Node-value reference math was refreshed after material changes.
- [x] Shared validation in `README.md` passes.

## Evidence Log

- Phase 2 completion — 2026-08-08: Revalidated all 24 Mining-owned outputs.
  Twenty-two bars and alloys still match their saved Phase 1A Evidence Pricing
  decisions, all with three-realm relative-rank coverage; 18 bands changed in
  that saved review, while four retained their prior values. The remaining two
  outputs, Mote of Fire and Mote of Earth, still match their exact reversible
  10:1 conversion decisions. Six saved Target changes over 50% retain explicit
  reviewer acceptance. Five current market estimates sit below at least one
  exact smelting floor and retain shared do-not-smelt guidance. No new price was
  needed during this closeout. Recipes, duplicates, notes, ordering, search
  metadata, and the guide footer were refreshed locally. Nothing was published.
- Phase 2 closeout start — 2026-08-08: Froze all 24 Mining-owned outputs.
  Twenty-two bars and alloys already retain completed Phase 1A Evidence Pricing
  decisions; Mote of Fire and Mote of Earth retain exact reversible 10:1
  conversion decisions. This pass audits those saved prices, exact recipes,
  duplicate guide rows, notes, ordering, and search metadata without fetching a
  redundant second market snapshot. Active Hellscream listings remain excluded,
  and nothing has been published.
- Audit date: 2026-08-03.
- Listing concentration observations (not valuation evidence): The AH was not
  rescanned for valuation. The previously recorded warning that the user and
  friends control at least half of many markets remains the reason active
  listings are excluded from all baseline calculations.
- Recipe/item sources checked: WotLKDB's 3.3.5 Mining spell list and individual
  smelting pages supplied spell IDs, ingredients, and guaranteed output counts.
  AzerothCore item templates at commit
  `e0fe11ba46b885a01e4a4038001e0055822cc7ba` confirmed item IDs, rarity,
  binding, stack size, and tradeability. The existing 88 guide rows and every
  duplicate ore, bar, stone, and elemental price in the AH guides were compared
  with the saved baseline file.
- Smelting/cooldown findings: 42 Mining spell records were reviewed. Twenty-six
  create a tradeable output: 24 are owned by Mining, while Titanium Bar and
  Enchanted Thorium Bar remain canonical Alchemy and Enchanting outputs and are
  shown as shared references. The other 16 records are ranks, tracking,
  smelting headers, or Toughness passives with no tradeable output. Standard
  3.3.5 Titansteel data uses 3 Titanium Bars plus one Eternal Fire, Earth, and
  Shadow and shows no cooldown. A Hellscream-specific override was not verified,
  so the row says to charge no cooldown premium unless the in-game UI shows one.
- Decisions and unresolved items: Arcanite Bar remains an Alchemy transmute;
  Blacksmithing stones, rods, and finished crafts remain Blacksmithing-owned.
  Elementium Ore was the only missing recipe input and received a documented
  fallback band of 10g / 20g / 40g: quick equals its exact vendor liquidation
  value, while target/high are provisional scarcity ranges. Its evidence remains
  unresolved until qualifying realized sales or measured acquisition data exist.
  Mining-node reference math was rechecked; no listed node value changed because
  the underlying ore, stone, gem, and elemental baselines used by those rows did
  not change. Elementium Ore is a raid drop rather than a mining-node output.
- Completion summary: Added 24 canonical Mining rows in four price-sorted
  sections, with exact recipe mouseovers, rarity colors, one shared pricing note,
  and item-specific buyer/use notes. Added shared Titanium and Enchanted Thorium
  references, retained the Alchemy-owned Arcanite reference, and added Elementium
  Ore. Corrected recipe-floor mismatches for Titansteel, Saronite, Khorium,
  Felsteel, Hardened Adamantite, Eternium, Fel Iron, and Elementium bars, then
  reconciled the duplicate bar prices in the Blacksmithing and Engineering
  guides. All prices derive from saved non-circular inputs, not current listings.
- Evidence Pricing refresh: On 2026-08-05 the Phase 1A review rechecked every
  Mining, bar, alloy, stone, and rod-reference row as part of the 189-item
  gathering/material batch. Sanitized completed Hellscream buyouts set the
  Cobalt, Copper, Saronite, and Solid Stone decisions; Saronite moved from a 70s
  Target to 1g 10s on 730 completed units, but remains low confidence because
  one buyer accounts for 83.56% of units. Six external faction observations set
  within-cohort rank only, fixed Hellscream anchors set gold, and 10:1 elemental
  forms remained exact. Accepted bands and duplicate references were applied
  locally; no active Hellscream ask was used and nothing was published.
