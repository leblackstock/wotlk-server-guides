# Tailoring AH Expansion Plan

- Status: `complete — 2026-08-03`
- Existing guide: `guides/tailoring-cloth-ah-price-guide.html`
- Work type: full crafted catalog
- Suggested order: 3

> Hard gate: finish and record the baseline evidence audit before adding crafted
> rows. Follow [the shared Gate 0](README.md#gate-0-establish-non-circular-baselines-before-adding-crafteds).

## Baseline Evidence Audit

- Recheck all 57 current rows, especially specialty cloth, bolts, raw cloth,
  spider silks, Eternals, and vendor thread/dyes.
- Reconcile cloth and cross-profession reagents wherever they are duplicated.
- Recalculate every bolt and specialty-cloth conversion from current component
  prices before using it in bags, spellthreads, or gear.
- Verify the server's Moonshroud, Spellweave, and Ebonweave cooldown and
  specialization behavior; do not assume bonus output.

## Crafted Coverage

- Wrath bags, spellthreads, nets and other tradeable utilities, plus tradeable
  BoE cloth gear from trainer, reputation, world-drop, and raid patterns.
- Outland and Classic bags, spellthreads, shirts, utility items, and selected
  BoE gear with real bag, leveling, twink, roleplay, or collection demand.
- Include bolts and specialty cloth as canonical intermediates without
  duplicating them in every finished-item section.
- Exclude flying carpets, profession-only embroidery applications, BoP gear,
  and other self-only outputs.

## Profession-Specific Price Checks

- Resolve cloth-to-bolt and bolt-to-specialty-cloth costs recursively using
  minimum guaranteed output.
- Keep cooldown opportunity and specialization access in notes. Never count a
  specialization proc in the guaranteed floor.
- Price bags by exact slot count and competition; similar-looking bags are not
  interchangeable if capacity or restrictions differ.
- Price spellthreads from exact recipes and intended level bracket; check their
  competition with reputation/vendor alternatives.

## Notes to Verify

- Bags: state capacity and any profession/class restriction.
- Spellthreads: state exact stat package and intended caster/healer/PvP use.
- Gear: state slot, armor role, item level/tier, binding, and whether demand is
  raid gearing, resistance, leveling, twink, or appearance driven.
- Shirts and novelty items need honest slow-sale notes rather than inflated
  demand labels.

## Acceptance Checks

- [x] Baseline evidence audit completed and recorded.
- [x] Cloth conversion and cooldown rules are documented and tested.
- [x] Every tradeable Tailoring output has an include/exclude decision.
- [x] Bag sizes/restrictions and spellthread effects are exact.
- [x] BoP, carpet, and self-only embroidery outputs are absent.
- [x] Shared validation in `README.md` passes.

## Evidence Log

- Audit date: 2026-08-03.
- Listing concentration observations (not valuation evidence): The existing
  concentration guard remains disqualified for valuation because the user and
  friends control at least half of listed units. No current listing price was
  imported. All 57 pre-expansion rows passed frozen-baseline, duplicate-price,
  rarity, identity, and note consistency checks before crafted rows were added.
- Recipe/item sources checked: WotLKDB's complete 439-record Tailoring spell
  list was fetched in six non-overlapping skill ranges. Its recipes were mapped
  to 423 unique output item records and cross-checked against the AzerothCore
  build-12340 `item_template` data for binding, rarity, item level, bag slots,
  profession requirements, and faction masks. Every included row links to its
  exact Wowhead WotLK recipe spell.
- Cooldown/specialization findings: Specialty cloth is costed from one minimum
  guaranteed output. No specialization bonus is included. Server-specific live
  cooldown behavior was not independently measured, so the shared and item notes
  tell the seller to verify the actual result instead of pricing assumed scarcity.
- Decisions and unresolved items: Included 406 distinct tradeable Horde-
  appropriate outputs. Excluded 12 BoP outputs, the skill-gated Flying Carpet,
  four duplicate Alliance-only Trial records, and self-only applications that
  create no tradeable item. The three tradeable nets are isolated in a Tailor-
  only section. The exact recipe model covers 147 direct inputs; four missing
  tradeable inputs were added as fallback-confidence references, four dyes use
  exact unlimited-vendor costs, and BoP Ogre Tannin remains an explicit access-
  cost fallback rather than a market claim.
- Completion summary: Added 17 price-sorted crafted sections covering bags,
  spellthreads, nets, cloth intermediates, Wrath/Outland/Classic cloth gear,
  cosmetic shirts, and utility. All 406 rows have rarity-colored names, exact
  recipe-mat mouseovers, one shared pricing note, and item-specific use or market
  notes. The complete Python, Node, desktop, and mobile validation suites passed.
