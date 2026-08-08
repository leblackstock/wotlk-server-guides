# Blacksmithing AH Expansion Plan

- Status: `complete` — Phase 2 Evidence Pricing, 2026-08-06
- Active guides:
  - `guides/blacksmithing-materials-ah-price-guide.html`
  - `guides/blacksmithing-gear-ah-price-guide.html`
- Work type: full crafted catalog
- Suggested order: 1

> Hard gate: finish and record the baseline evidence audit before adding crafted
> rows. Follow [the shared Gate 0](README.md#gate-0-establish-non-circular-baselines-before-adding-crafteds).

## Baseline Evidence Audit

- Recheck every existing material/reference row, especially Primordial Saronite, Crusader/Runed/
  Frozen Orbs, Titansteel and Titanium, Saronite, Eternals, Infinite Dust, and
  the existing Wrath utility items.
- Reconcile duplicated bars, ores, stone, rods, and cross-profession reagents
  with the Mining/Smithing, Enchanting, and cross-profession guides.
- Recalculate the belt buckle, weapon chain, shield plating, stones, keys, and
  rod blanks from saved input baselines before using them as examples.
- Record whether the server follows normal 3.3.5 Titansteel cooldown behavior;
  keep that access issue separate from raw reagent cost.

## Crafted Coverage

- Wrath: Eternal Belt Buckle, weapon chains, shield spikes/plating, skeleton
  keys, sharpening/weightstones, Enchanting rod blanks, shields, weapons, and
  tradeable BoE armor from normal, reputation, raid, and world-drop plans.
- Outland and Classic: useful tradeable weapons, armor, shield spikes, weapon
  chains, stones, keys, and rod blanks with a plausible leveling, transmog, or
  profession demand.
- Verify every socketing-related spell. Exclude self-only bracer/glove socket
  applications and every BoP result.
- Group gear by expansion and market purpose; do not bury level-80 BoE raid
  crafts among leveling items.

## Profession-Specific Price Checks

- Price one finished item from exact bar, elemental, orb, leather, cloth, and
  vendor counts. Resolve recursively crafted bars and rods first.
- For raid BoE gear, show craft cost but use conservative demand and single-item
  posting. Flag obsolete tiers and recipe-access risk.
- Keep enhancement item prices tied to their exact recipe rather than applying
  one blanket markup to buckles, chains, spikes, and plating.
- Treat rare-plan access as a note, not an invented reagent.

## Notes to Verify

- State the exact slot/type and intended buyer for gear; distinguish tank,
  physical DPS, caster plate, PvP, leveling, and collection markets.
- State what each buckle, chain, spike, plating, key, or stone actually does and
  whether level restrictions affect demand.
- Use one shared baseline-pricing `*` note and one exact recipe mouseover per row.

## Acceptance Checks

- [x] Baseline evidence audit completed and recorded.
- [x] Every tradeable Blacksmithing output has an include/exclude decision.
- [x] All recursive bar/rod costs and guaranteed output counts are tested.
- [x] Self-only sockets and BoP crafts are absent.
- [x] Gear notes identify slot, role, tier, and turnover risk.
- [x] Shared validation in `README.md` passes.

## Evidence Log

- Audit date: 2026-08-02.
- Listing concentration observations (not valuation evidence): the same-day
  Garrosh-Horde scan contained 3,294 auction rows and 12,616 units. Its top
  three sellers controlled 73.7% of all units. Saronite Ore (407 units), Rough
  Stone (54), and Thick Leather (4) were each supplied by only Cloudbreaker;
  Mageweave Cloth had only two sellers. No active-listing price was retained as
  baseline evidence.
- Realized-sales coverage: BeanCounter contained 126 completed-sale records,
  842 units, and 33 unique items. Only four of 149 direct Blacksmithing inputs
  and three Blacksmithing outputs had any completed sales. Solid Stone's frozen
  9s target was independently matched by 80 units across four auctions, two
  buyers, and two days, so that one baseline is medium confidence. The 695
  Saronite Ore units sold in one 13-minute window to two buyers were recorded
  as validation only and did not reset the baseline.
- Baseline decision: `data/ah-price-baselines.json` freezes 650 pre-scan item
  bands. Of those, 649 remain low confidence and one is medium confidence;
  exact vendor costs still override the file during recipe calculation. Active
  scans cannot update the file automatically.
- Recipe/item sources checked: the complete WotLKDB Blacksmithing spell list was
  retrieved in three non-truncated skill ranges (525 records), then recipes and
  exact minimum outputs were linked to Wowhead WotLK spell pages and checked
  against the AzerothCore 3.3.5 item baseline for item ID, binding, and rarity.
- Server-specific findings: the existing guide records shorter or absent
  Titansteel and Arcanite cooldowns on this server, so no normal cooldown
  scarcity premium was added.
- Decisions and unresolved items: 453 distinct Horde-relevant tradeable outputs
  were included. Fifty-three BoP outputs, six duplicate Alliance-only Trial of
  the Crusader records, and self-only socket applications were excluded. Rare
  legacy reagents without independent evidence retain documented conservative
  fallbacks. Current competition should still be checked before stock is
  crafted, but it cannot alter the saved valuation baseline.
- Completion summary: 16 crafted sections now cover Wrath, Outland, and Classic
  enhancements, intermediates, weapons, shields, and BoE armor. Every crafted
  row has a rarity color, item-specific market/use note, exact recipe mouseover,
  and one shared baseline-pricing `*` reference. The non-circular re-audit
  recalculated all 453 outputs: 103 changed, 94 target prices decreased, eight
  increased from frozen historical output references, and 350 were unchanged.
  Duplicate rod and grinding-stone rows in Mining + Smithing remain synchronized
  to the canonical output prices and recipe links.
- Presentation split: on 2026-08-04, the single 511-row indexed guide was split
  into `Blacksmithing Materials & Enhancements` (110 indexed rows, including 52
  canonical crafted outputs) and `Blacksmithing Armor & Weapons` (401 crafted
  outputs). Both pages are filtered views of the same canonical Blacksmithing
  catalog, so the split introduces no duplicate source data or pricing path.
- Material-baseline refresh — 2026-08-06: Phase 1B rechecked 58 Blacksmithing
  material references. Forty-seven inherit the completed Phase 1A review, five
  retain exact vendor pricing, and six newly reviewed overlapping material
  bands changed. Finished Blacksmithing outputs remain outside this phase.
- Phase 2 Evidence Pricing started — 2026-08-06: the 52 materials/enhancement
  outputs and 401 armor/weapon outputs are being reviewed as one coupled batch
  against the completed Phase 1 material baseline. Active Hellscream listings
  remain competition-only evidence; completed sales and normalized external
  comparisons are recorded separately.
- Phase 2 Evidence Pricing completed — 2026-08-06: all 453 tradeable outputs
  received saved before/after bands, exact current recipe floors, sanitized
  completed-sale aggregates, six-source comparison coverage, confidence, and
  an explicit decision. Four sparse-sale items were shrunk toward their
  comparable cohorts; no local sale qualified for medium confidence. Of 100
  model candidates over the 50% review threshold, 93 with at least two-realm
  support were accepted and seven with weaker coverage retained their prior
  bands. The accepted pass changed 445 bands and flagged 222 outputs whose
  estimated sale value is below at least one exact recipe-cost band. Twenty-nine
  duplicate baseline records and 12 Mining + Smithing display rows were
  synchronized to the reviewed Blacksmithing values. Work remains local.
