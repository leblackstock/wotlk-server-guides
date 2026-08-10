# Tailoring AH Expansion Plan

- Status: `complete — Phase 2 plus collectible addendum, 2026-08-10`
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
- Include the tradeable Flying Carpet in a dedicated Tailor-only mount section;
  exclude its BoP upgrade variants, profession-only embroidery applications,
  BoP gear, and other self-only outputs.

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
- [x] The tradeable Flying Carpet is restricted to its actual Tailoring buyer;
  BoP carpet upgrades and self-only embroidery outputs are absent.
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
  only section. The exact recipe model now covers 148 direct inputs; four missing
  tradeable inputs were added as fallback-confidence references, four dyes use
  exact unlimited-vendor costs, and BoP Ogre Tannin remains an explicit access-
  cost fallback rather than a market claim.
- Completion summary: Added 17 price-sorted crafted sections covering bags,
  spellthreads, nets, cloth intermediates, Wrath/Outland/Classic cloth gear,
  cosmetic shirts, and utility. All 406 rows have rarity-colored names, exact
  recipe-mat mouseovers, one shared pricing note, and item-specific use or market
  notes. The complete Python, Node, desktop, and mobile validation suites passed.
- Material-baseline refresh — 2026-08-06: Phase 1B rechecked 58 cloth, bolt,
  specialty-cloth, silk, thread, dye, and overlapping reagent references.
  Eleven inherit Phase 1A, eleven retain exact vendor pricing, and 36 newly
  reviewed material bands changed. Finished Tailoring outputs remain outside
  this phase except material intermediates explicitly owned by the input market.
- Phase 2 start — 2026-08-08: Froze all 406 tradeable Tailoring outputs across
  17 sections. The 17 cloth intermediates retain their completed Phase 1B
  evidence, leaving 389 finished outputs for this review: three Tailor-only
  nets, 33 bags, eight spellthreads, 314 cloth gear pieces, 30 cosmetic shirts,
  and one tradeable utility item. All 406 outputs retain exact saved recipes;
  the three nets remain isolated in the profession-restricted section. The 17
  First Aid outputs sharing this guide remain outside this Tailoring batch.
  Phase 1 input baselines stay frozen, current listings remain competition-only
  evidence, and exact recipe cost remains a separate craftability diagnostic.
  Nothing has been published.
- Phase 2 completion — 2026-08-08: Completed the final comparison retry for all
  389 finished Tailoring outputs, and all 2,334 comparison requests resolved.
  No item had completed-sale evidence. The retry recovered usable relative-rank
  evidence for 377 outputs: 331 had three-realm support, 38 had two-realm
  support, eight had one-realm support, and 12 had no listings on the comparison
  realms. The pass changed 384 price bands; 183 Targets rose, 190 fell, and 16
  stayed unchanged. Of the 144 Target candidates whose movement exceeded 50%,
  139 had at least two-realm support and were accepted, while five lacked enough
  coverage and retained their frozen bands. One hundred ninety-two final
  estimates remain below at least one exact
  recipe-floor band and retain the shared do-not-craft warning. The 17 Phase 1B
  cloth intermediates and all 17 First Aid outputs remained unchanged. Evidence
  references, shared notes, exact recipes, profession-use sections, ordering,
  search metadata, and the guide footer were refreshed locally. Refresh this
  phase when useful Hellscream completed-sale history becomes available or a
  later scheduled evidence refresh is due. Nothing was published.
- Container coverage addendum — 2026-08-08: Reconciled every pinned storage
  item with the 33 existing Tailoring-crafted containers. All recipe-backed
  Tailoring bags were already present. Added seven general vendor bags to this
  guide as deterministic convenience references, including the mixed-source
  Small Brown Pouch, whose unlimited 5s vendor route prevents drop-scarcity
  pricing. No crafted Tailoring band changed and nothing was published.
- Collectible coverage addendum — 2026-08-10: Added the tradeable Flying Carpet
  in a dedicated Tailor-only crafted-mount section. Its Tailoring 300 use
  requirement, exact one-item recipe, and recursively audited craft floor are
  saved; its sale band is delegated to the collectible Evidence Pricing review
  so the completed 406-output Tailoring Phase 2 snapshot remains frozen. The
  BoP Magnificent Flying Carpet and Frosty Flying Carpet remain excluded.
  Active listings did not set value. Nothing was published.
