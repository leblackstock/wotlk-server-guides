# Blacksmithing AH Expansion Plan

- Status: `complete` — 2026-08-02
- Existing guide: `guides/blacksmithing-materials-ah-price-guide.html`
- Work type: full crafted catalog
- Suggested order: 1

> Hard gate: finish and record the current-price audit before adding crafted
> rows. Follow [the shared Gate 0](README.md#gate-0-audit-current-prices-before-adding-crafteds).

## Current-Price Audit

- Recheck all 88 current rows, especially Primordial Saronite, Crusader/Runed/
  Frozen Orbs, Titansteel and Titanium, Saronite, Eternals, Infinite Dust, and
  the existing Wrath utility items.
- Reconcile duplicated bars, ores, stone, rods, and cross-profession reagents
  with the Mining/Smithing, Enchanting, and cross-profession guides.
- Recalculate the current belt buckle, weapon chain, shield plating, stones,
  keys, and rod blanks from verified inputs before using them as examples.
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
- Use one shared craft-cost `*` note and one exact recipe mouseover per row.

## Acceptance Checks

- [x] Current-price audit completed and recorded.
- [x] Every tradeable Blacksmithing output has an include/exclude decision.
- [x] All recursive bar/rod costs and guaranteed output counts are tested.
- [x] Self-only sockets and BoP crafts are absent.
- [x] Gear notes identify slot, role, tier, and turnover risk.
- [x] Shared validation in `README.md` passes.

## Evidence Log

- Audit date: 2026-08-02.
- Live AH observations: the same-day Garrosh-Horde Auctioneer full scan contained
  3,294 auction rows and 12,616 units. Strong clusters used in the input audit
  included Saronite Ore (35 listings / 407 units; 1g 26s low and about 1g 30s
  median), Mageweave Cloth (19 listings / 154 units at 16s), Rough Stone (8
  listings / 54 units around 5s), Sharp Claw (10 listings around 1s 66c), Ichor
  of Undeath (4 listings from 8s to about 13s), Volatile Rum (3 listings / 15
  units at 7s), and Dark Rune (8 singles at 80s). Thin one-listing outliers were
  not used to reset a band.
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
  legacy reagents without current listings retain documented conservative
  fallbacks, and the 423 finished outputs absent from this scan still require a
  live competition check before stock is crafted.
- Completion summary: 16 crafted sections now cover Wrath, Outland, and Classic
  enhancements, intermediates, weapons, shields, and BoE armor. Every crafted
  row has a rarity color, item-specific market/use note, exact recipe mouseover,
  and one shared craft-cost `*` reference. Duplicate rod and grinding-stone rows
  in Mining + Smithing were synchronized to the same prices and recipe links.
