# AH Evidence Pricing Library Audit Plan

- Status: `complete locally — all three Evidence Pricing phases audited; scheduled refreshes next`
- Recorded: `2026-08-05`
- Last updated: `2026-08-10`
- Scope: `All 19 active Auction House guides`
- Required order: `Gathering and materials → professions → drops`
- Governing method: [Evidence Pricing](ah-pricing-methodology.md)
- Publishing rule: each implementation batch remains local until the user explicitly says to make it live.

## Objective

Verify every Quick, Target, and High price in the Auction House library with the strongest independent evidence available, improve weak fallback estimates, and preserve an honest confidence label when Hellscream does not have enough completed-sale history.

This is a baseline audit, not a live-AH repricer. The user's and friends' auctions can represent much of the local market, so current Hellscream asks must never set or automatically update a guide price. Active listings may describe competition, seller concentration, stack sizes, and item availability; they do not prove value.

## Evidence Rules

Use evidence in this order:

1. Exact unlimited-vendor prices and deterministic conversions.
2. Qualifying Hellscream completed sales, excluding self purchases, known friend or guild transfers, tests, bids, cancellations, and expirations.
3. Measured acquisition or farming results with route, elapsed time, output, and opportunity-cost assumptions recorded.
4. Sparse Hellscream completed sales, manually reviewed and kept at low confidence.
5. Cross-server observations used only for within-cohort relative rank. Fixed Hellscream anchors set the gold scale; external gold values are never copied.
6. A documented fallback estimate when no stronger evidence exists.

Additional guards:

- Current Hellscream listings are competition evidence only.
- Recipe cost is a craftability diagnostic, not automatic proof of sale value.
- A sale band below a low-confidence reagent floor requires an explicit Evidence Pricing override and a do-not-craft warning.
- Every evidence snapshot records source type, as-of date, coverage, exclusions, confidence, and rationale.
- Existing Alchemy potion and dropped-gear evidence must be revalidated, not silently treated as permanently current.

## Gate 0 — Freeze and Inventory the Library

Before changing any price:

- Export all 19 guides into one deterministic inventory keyed by item ID and canonical item key.
- Record guide, section, expansion, item type, rarity, stack limit, suggested stacks, demand, current Quick/Target/High, target bid, source type, confidence, evidence date, and note.
- Record every duplicate item across guides and identify its canonical owner.
- Confirm whether each displayed price is per item, per craft, or per stated stack.
- Verify item ID, rarity color, auction eligibility, binding, profession-use restriction, maximum stack, and tooltip mapping.
- Identify unresolved `Varies`, missing stack information, three-currency displays, repeated boilerplate notes, missing recipe links, and stale footer dates.
- Save a before report. Evidence collection must not mutate canonical prices.

## Phase 1 — Gathering and Material Baselines

This phase locks the input economy before any finished craft is repriced. Material rows are audited first even when they share a page with later profession outputs.

### Phase 1A: foundational gathering guides

| Order | Guide | Evidence and pricing checks |
|---:|---|---|
| 1 | `mining-smithing-ah-price-guide.html` | Ore, bars, alloys, stone, exact smelting ratios, elemental conversions, vendor liquidation, and per-unit versus per-stack consistency. Detect circular ore/bar pricing and impossible conversion arbitrage. |
| 2 | `herbalism-herbs-ah-price-guide.html` | Herb tiers, Frost Lotus, milling and Alchemy demand, measured gathering evidence where available, and cross-era comparables. Do not infer value from potions already priced from these herbs. |
| 3 | `cross-profession-materials-ah-price-guide.html` | Eternals, Primals, motes, orbs, pearls, elemental materials, deterministic combines/splits, vendor references, and duplicate values used by multiple professions. |

### Phase 1B: material sections inside profession guides

Audit these input families in dependency order:

1. `enchanting-mats-ah-price-guide.html` — dust, essences, shards, crystals, conversions, and exact vellum vendor costs.
2. `jewelcrafting-gems-ah-price-guide.html` — raw and uncut gems, prospecting diagnostics, vendor/token paths, and cut-versus-uncut opportunity cost.
3. `tailoring-cloth-ah-price-guide.html` — cloth, bolts, thread, dyes, cooldown cloth, and specialization assumptions.
4. `skinning-leatherworking-materials-ah-price-guide.html` — scraps, leather, hides, scales, combines, and specialty-drop acquisition evidence.
5. `fishing-cooking-materials-ah-price-guide.html` — fish, meat, eggs, spices, event ingredients, vendor inputs, and recipe output quantities.
6. `alchemy-materials-ah-price-guide.html` — vials, repeated herb references, oils, fish inputs, and transmute inputs without using finished potion prices as evidence.
7. `inscription-materials-ah-price-guide.html` — pigments, inks, parchment vendor costs, ink exchanges, and milling expected-value diagnostics.
8. `engineering-materials-ah-price-guide.html` — raw metals, stone, volatile ingredients, vendor tools, and component dependencies.
9. `blacksmithing-materials-ah-price-guide.html` — bars, stone, rod inputs, and shared material references reconciled to their canonical guides.

### Phase 1 completion gate

- Every recipe ingredient has a saved baseline or an explicitly documented missing-evidence fallback.
- Duplicate materials agree across guides after display rounding.
- Deterministic conversions reconcile without circular inputs.
- Vendor prices and guaranteed output quantities are exact.
- Material confidence is not promoted by an active listing.
- A material before/after report is reviewed before applying changes.

## Phase 2 — Profession Markets

After Phase 1 baselines are frozen, audit finished outputs in this order:

| Order | Profession guide | Special checks |
|---:|---|---|
| 1 | `blacksmithing-materials-ah-price-guide.html` | Enhancements, keys, rods, intermediates, buyer restrictions, exact recipes, and convenience margin. |
| 2 | `blacksmithing-gear-ah-price-guide.html` | Raid crafts, leveling gear, weapons, shields, stats/effects, replacement alternatives, recipe access, and one-at-a-time sale evidence. |
| 3 | `engineering-materials-ah-price-guide.html` | Components, ammo per stated stack, explosives, devices, tools, mounts, profession restrictions, and server-specific usability. |
| 4 | `jewelcrafting-gems-ah-price-guide.html` | Cut-gem demand by useful stat, token/vendor supply, prospecting diagnostics, rarity, and cut-versus-uncut value. |
| 5 | `jewelcrafting-jewelry-ah-price-guide.html` | Jewelry, statues, components, gear utility, socket/stat quality, slow-sale risk, and profession-use gates. |
| 6 | `enchanting-mats-ah-price-guide.html` | Every scroll's exact recipe and vellum, raid/PvP/leveling use, recipe access, market estimate, and one shared craft-floor note. |
| 7 | `alchemy-materials-ah-price-guide.html` | Flasks, elixirs, all 84 potions, oils, cauldrons, intermediates, and transmutes. Refresh the saved potion Evidence Pricing snapshot rather than rebuilding from local asks. |
| 8 | `inscription-materials-ah-price-guide.html` | Glyphs, scrolls, off-hands, cards/decks, random-output expected value, Book of Glyph Mastery user baseline, and recipe access. |
| 9 | `tailoring-cloth-ah-price-guide.html` | Bags, bolts, cooldown cloth, spellthreads, gear, specialty assumptions, and finished-item demand independent of input cost. |
| 10 | `skinning-leatherworking-materials-ah-price-guide.html` | Armor kits, drums, bags, gear, profession restrictions, specialty leather assumptions, and slow legacy crafts. |
| 11 | `fishing-cooking-materials-ah-price-guide.html` | Buff food, feasts, pet/novelty outputs, event recipes, minimum output, raid consumption, and low-demand routing. |

Profession rules:

- Verify the exact WotLK 3.3.5 recipe, minimum guaranteed output, and source spell for every craft.
- Exclude specialization procs from the guaranteed floor and document them separately.
- Keep recipe rarity, cooldowns, and reputation access in notes instead of hiding arbitrary premiums in the floor.
- Separate profession-restricted finished items from general-use outputs.
- Link every craft to its exact recipe with the existing mouseover pattern.
- Use one shared `*` methodology note per guide; row notes contain only item-specific information.
- Sort non-progression sections by Target buyout per item, highest first.
- Calculate bids consistently from the approved buyout rule and display no more than two currency types.

## Phase 3 — Drops, Recipes, and Turn-Ins

| Order | Guide | Evidence and pricing checks |
|---:|---|---|
| 1 | `drop-turn-in-quest-page-items-ah-price-guide.html` | Exact turn-in quantities, reputation/quest value, repeatability, level relevance, source availability, stack purchasing behavior, and event or faction restrictions. |
| 2 | `gear-pattern-drops-ah-price-guide.html` | Recipe ownership, profession and skill requirement, learned-output value, source/drop chance, rarity, trainer/vendor competition, and recipe-specific buyer pool. |
| 3 | `level-80-boe-epics-ah-price-guide.html` | Refresh direct sales and supply diagnostics, verify stats/effects/slot alternatives, preserve the one-at-a-time BoE evidence gate, and recheck every large change. |
| 4 | `sought-after-world-drops-ah-price-guide.html` | Separate Northrend leveling, twink/bracket, Outland level-70, Classic iconic, container, world-boss, and raid-trash cohorts. Revalidate existing relative-rank evidence and fixed Hellscream anchors. |

Drop rules:

- Source/drop-rate and acquisition evidence are separate from sale evidence.
- An empty AH does not justify the High price.
- Modern transmog demand must not be imported into a WotLK market.
- Sparse BoE sales remain low confidence and shrink toward reviewed comparable cohorts.
- Cross-server listings may rank comparable items only; they never set Hellscream gold values.

## Per-Guide Work Cycle

Every guide or tightly coupled guide pair follows the same cycle:

1. **Inventory:** freeze rows, evidence, duplicates, and current bands.
2. **Refresh evidence:** verify vendor/conversion facts, completed-sale coverage, measured acquisition, and relative-rank diagnostics before proposing prices.
3. **Report only:** generate old/new bands, percentage changes, evidence class, confidence, coverage, and rationale without editing canonical prices.
4. **Manual review:** require explicit decisions for Target changes over 50%, confidence promotions, missing evidence, wide bands, unusual conversions, and unique items.
5. **Apply locally:** update only approved canonical sources, then regenerate guide HTML, ordering, search data, and tooltips.
6. **Validate:** run guide-specific tests plus complete AH baseline, duplicate, eligibility, rarity, stack, currency, search, ordering, and desktop/mobile suites.
7. **Report:** list changed, retained, unresolved, and excluded items. Keep the work local.
8. **Publish separately:** commit only that approved batch after the user explicitly says to make it live; verify remote sync, Actions, and public Pages.

## Required Item Review Record

Each saved review record contains:

- canonical key, item ID, guide, and section;
- old and proposed Quick/Target/High bands;
- absolute and percentage Target change;
- pricing unit or stack basis;
- evidence types, as-of dates, coverage, and exclusions;
- acquisition evidence and cross-server relative-rank coverage, when used;
- fixed Hellscream cohort anchor, when used;
- reagent or conversion diagnostic, when applicable;
- confidence, plain-language rationale, and reviewer decision.

Reviewer decisions are `accept`, `revise`, `retain fallback`, or `exclude`.

## Library-Wide Quality Checks

- No unresolved `Varies` caused by duplicate canonical data.
- No display uses gold, silver, and copper together.
- Non-stackable items show no stack recommendation.
- Suggested stacks respect the real maximum and likely purchase quantity.
- Search cards match canonical price, demand, rarity, stack, and target bid.
- Item names use the correct rarity color.
- Recipe links and mouseover tooltips resolve correctly.
- No invalid, BoP, conjured, temporary, self-only, or nontradeable output appears as an AH listing.
- Hard profession requirements are in labeled restricted sections.
- Repeated methodology notes appear once per guide, not in each row.
- Every section is price-sorted or has a recorded fixed progression.
- Every edited guide footer uses the actual edit date.
- Generated files are reproducible and all `--check` modes pass.

## Definition of Done

- [x] All 19 active AH guides have a completed evidence review.
- [x] Gathering and material baselines were completed before profession outputs.
- [ ] Profession outputs were completed before drop-market refreshes.
- [ ] Every changed price traces to saved independent evidence or an explicit fallback model.
- [ ] Active listings did not automatically set any price or confidence.
- [ ] Every retained fallback is labeled and dated.
- [ ] Duplicate items, units, stacks, rarity, eligibility, notes, and search metadata are consistent.
- [ ] Complete Python, Node, syntax, generated-asset, and desktop/mobile validation passes.
- [ ] Each publication batch has a focused commit, successful repository validation, `0 / 0` remote sync, and verified public Pages result.

## Planned Deliverables

- A deterministic library-wide before inventory.
- Phase-specific sanitized evidence files or extensions to existing evidence files.
- One review report per guide or tightly coupled guide pair.
- A master status table with `not started`, `evidence collected`, `reviewed`, `applied locally`, and `published` states.
- Reproducible `--report`, `--check`, and reviewed `--apply` workflows wherever a pricing model is used.
- A final summary listing confidence coverage, unresolved gaps, and the next evidence-refresh trigger for every guide.

## Evidence Log

- 2026-08-05: Master plan created for all 18 active AH guides. Work order is gathering and material baselines first, profession markets second, and drops/recipes/turn-ins last. No AH price or public guide was changed by creating this plan.
- 2026-08-05: Phase 1A reviewed 198 guide occurrences representing 189 unique Mining, Herbalism, and Shared Crafting Materials items. Sanitized Hellscream completed buyouts covered six items; 179 items had current comparison coverage on all three external realms, with external values used for within-cohort rank only. Nine exact vendor rows, 13 deterministic 10:1 conversions, 31 retained bands, six direct-sale decisions, and 130 fallback cohort decisions were recorded. All 31 Target moves over 50% received explicit accept decisions without confidence promotion. The accepted review changed 149 canonical bands locally, synchronized duplicate material rows, refreshed recipe-floor diagnostics, and preserved every unreviewed finished-profession market band. Nothing was published.
- 2026-08-06: Phase 1B inventoried 506 profession-guide material occurrences representing 423 unique items. It inherited 106 already-reviewed Phase 1A items, retained 40 exact vendor rows, locked seven lesser/greater Enchanting essence pairs to reversible 3:1 parity, and reviewed 279 remaining material markets with sanitized Hellscream completed sales plus six external faction snapshots. All 286 newly applied bands had three-realm comparison coverage; external nominal gold and active Hellscream asks were excluded. One 26-unit Rugged Leather sale came from one buyer on one day, so its direct result received only 25% weight and was shrunk toward the fixed cohort fallback. Thirty-nine Target moves over 50% were explicitly reviewed and remain fallback confidence. The accepted changes were applied locally across nine profession material families, dependent recipe floors and duplicate guide rows were regenerated, and no finished profession-market phase was started. Nothing was published.
- 2026-08-06: Phase 2 Blacksmithing reviewed all 453 tradeable outputs as one coupled batch: 52 materials/enhancements and 401 armor/weapons. Four items had sparse completed-sale evidence; none passed the medium-confidence gate, so their direct bands received 25% or 50% weight and were shrunk toward fixed Hellscream cohort estimates. Gold-normalized external observations covered all three comparison realms for 384 items and set relative rank only. One hundred model candidates moved Target by more than 50%; 93 with at least two-realm support were accepted after review, while seven with zero- or one-realm coverage retained their prior bands. The review changed 445 bands locally, identified 222 outputs whose sale estimate falls below at least one exact recipe-floor band, synchronized 29 duplicate baseline records and 12 Mining + Smithing display rows, and refreshed every downstream craft floor. Nothing was published.
- 2026-08-06: Phase 2 Engineering started with all 55 finished outputs after the missing profession plan was added. Phase 1 input baselines remain frozen, active Hellscream listings remain competition-only evidence, and exact recipe cost remains separate from estimated sale value. Nothing has been published.
- 2026-08-06: Phase 2 Engineering reviewed all 55 finished outputs across eight sections. No output had qualifying Hellscream completed-sale evidence. Fifty-one outputs had all-three-realm relative-rank coverage, three had two-realm coverage, and Box of Bombs retained its fixed cohort anchor without external coverage. All 11 Target candidates over 50% had three-realm support and were accepted after manual review. The pass changed all 55 price bands; 25 Targets rose, 21 fell, and nine stayed unchanged. Twenty-three Target estimates fall below their exact price-basis recipe floors and carry the shared do-not-craft guidance. All 13 ammunition rows were consistently normalized to the displayed stack of 200. The canonical guide, ordering, search data, tooltips, item-specific notes, recipe links, and missing Engineering profession plan were updated locally. Nothing was published.
- 2026-08-06: Phase 2 Jewelcrafting gems started with 360 cut and special-gem outputs across 38 sections. The 137 jewelry, component, setting, and sealed random-result outputs remain outside this batch. Phase 1 uncut-gem baselines stay frozen, current Hellscream listings remain competition-only evidence, and cut-versus-uncut opportunity cost remains a separate craftability diagnostic. Nothing has been published.
- 2026-08-06: Phase 2 Jewelcrafting gems reviewed all 360 cut outputs across 38 same-expansion, same-quality, and same-color cohorts. No cut had qualifying Hellscream completed-sale evidence. Three hundred forty-two cuts had all-three-realm relative-rank coverage and 18 had two-realm coverage. All three Target candidates over 50% had three-realm support and were accepted after manual review. Every price band changed; 171 Targets rose, 174 fell, and 15 stayed unchanged. One hundred twenty-eight final estimates fall below at least one exact uncut-gem opportunity-cost band and retain shared do-not-cut guidance. Six duplicate legacy meta-gem baselines were synchronized. Repeated market/posting boilerplate was removed from all 360 row notes while exact stats, socket matching, meta requirements, and nine true same-stat aliases remain explicit. The gem guide, companion shared-note rendering, search data, ordering, and tooltips were regenerated locally; 137 jewelry/component outputs remain unreviewed and unchanged. Nothing was published.
- 2026-08-06: Phase 2 Jewelcrafting jewelry started with 137 tradeable jewelry, component, setting, utility, weapon, and sealed random-result outputs across seven sections. Phase 1 ingredient baselines remain frozen, active Hellscream listings remain competition-only evidence, and exact recipe cost remains a separate craftability diagnostic. Nothing has been published.
- 2026-08-06: Phase 2 Jewelcrafting jewelry reviewed all 137 tradeable jewelry, equipment, component, setting, utility, weapon, and sealed random-result outputs across seven sections. Six outputs had sanitized Hellscream completed-sale history; Tigerseye Band passed the medium-confidence gate, while five sparse observations were shrunk toward fixed comparable-cohort estimates. Comparison coverage reached all three realms for 113 outputs, two realms for 12, one realm for seven, and no realm for five. All 38 Target candidates over 50% had at least two-realm support and were accepted after manual review. The pass changed 132 price bands; 61 Targets rose, 58 fell, and 18 stayed unchanged. Fifty-five final estimates fall below at least one exact recipe-floor band and retain shared do-not-craft guidance. Five legacy baselines were synchronized, repeated BoE sales boilerplate was replaced by one shared note, and exact item stats, effects, recipe links, rarity, ordering, search data, and tooltips were regenerated locally. Jewelcrafting's 497 finished outputs are now complete in Phase 2. Nothing was published.
- 2026-08-06: Phase 2 Enchanting started with all 276 finished outputs across 25 sections: 259 enchant scrolls, nine oils, four wands, two tradeable intermediates, and two prismatic gems. All saved spell IDs resolve in the complete WotLKDB Enchanting recipe list. The missing profession plan was added. Phase 1 input baselines remain frozen, active Hellscream listings remain competition-only evidence, and exact recipe plus compatible-vellum cost remains a separate craftability diagnostic. Nothing has been published.
- 2026-08-06: Phase 2 Enchanting reviewed all 276 finished outputs across 25 sections. No output had completed-sale evidence. Comparison coverage reached all three realms for 261 outputs, two realms for 13, one realm for one, and no realm for Titanguard. Twenty-three of 24 Target candidates over 50% had at least two-realm support and were accepted; Titanguard retained its prior band because it had no comparison coverage. The pass changed 274 price bands; Enchanted Thorium Bar retained its completed Phase 1 material band and evidence reference. Eighty-five Targets rose, 106 fell, and 85 remained unchanged. Seventy-two final estimates fall below at least one exact recipe plus compatible-vellum floor and retain shared do-not-craft guidance. All 276 exact recipes, six compatible vellum recipes, level-80 use notes, recipe links, rarity, ordering, search data, and tooltips were regenerated locally. Nothing was published.
- 2026-08-06: Phase 2 Alchemy started by freezing all 206 tradeable outputs across 21 sections. The completed 84-potion review and 24 profession-material records are disjoint and remain frozen, leaving 98 finished outputs for this batch: 16 flasks, 76 elixirs, five sealed protection cauldrons, and Eternal Might. All 206 outputs already have exact saved recipes. The two hard profession requirements remain in the Alchemist-only potion section; all five cauldrons are saved general-use exceptions. Phase 1 input baselines remain frozen, current Hellscream listings remain competition-only evidence, and exact recipe cost remains separate from estimated sale value. Nothing has been published.
- 2026-08-06: Phase 2 Alchemy reviewed all 98 remaining outputs: 16 flasks, 76 elixirs, five sealed protection cauldrons, and Eternal Might. No item had completed-sale evidence. Comparison coverage reached all three realms for 97 outputs; Eternal Might had no comparison coverage and retained its 45g Target anchor. All 20 Target candidates over 50% had three-realm support and were accepted after manual review. The pass changed all 98 bands; 44 Targets rose, 52 fell, and two stayed unchanged. Thirty final estimates fall below at least one exact recipe-floor band and retain shared do-not-craft guidance. The completed 84-potion and 24 material/intermediate reviews remained unchanged. All 206 Alchemy crafts now have saved market evidence, exact recipes, profession-use decisions, item-specific notes, recipe links, rarity, target-price ordering, and current search metadata. Nothing was published.
- 2026-08-06: Phase 2 Inscription started by freezing 107 tradeable outputs across 18 sections. Armor Vellum III and Weapon Vellum III retain their completed Phase 1B evidence, leaving 105 outputs for this batch: 60 glyphs, six buff scrolls, three utility or BoE items, 32 exact random Darkmoon cards, and four completed decks. All 107 outputs have exact saved recipes. The two vellums are the only hard profession requirements and remain in the Enchanter-only section. The Book of Glyph Mastery recipe-drop baseline remains locked to the user-set 25g Target with its original 150g / 300g / 700g baseline recorded. Phase 1 inputs remain frozen, current Hellscream listings remain competition-only evidence, and random-roll cost remains separate from exact-card sale value. Nothing has been published.
- 2026-08-06: Phase 2 Inscription reviewed all 105 previously unreviewed outputs: 60 glyphs, six buff scrolls, three utility or BoE items, 32 exact random Darkmoon cards, and four completed decks. No item had completed-sale evidence; all 105 had three-realm comparison coverage. The only Target candidate over 50%, Runescroll of Fortitude, moved from 20g to 5g 40s with full comparison support and remains above its exact 2g 95s per-scroll craft diagnostic. The pass changed all 105 bands; 51 Targets rose, 53 fell, and one stayed unchanged. Nine named-card estimates fall below at least one random-roll-cost band, which is valid because Darkmoon Card of the North cannot guarantee a named outcome. Chaos Deck and Undeath Deck fall below their current eight-card opportunity cost and retain shared do-not-assemble guidance. The dependency audit was corrected so Evidence-priced decks are no longer forced up to craft cost; their exact named-card opportunity totals remain separate diagnostics. Armor Vellum III, Weapon Vellum III, and the Book of Glyph Mastery user baseline remained unchanged. All 107 Inscription crafts now have saved evidence, exact recipes, profession-use decisions, item-specific notes, recipe links, rarity, intentional card-rank order, target-price ordering elsewhere, and current search metadata. Nothing was published.
- 2026-08-08: Phase 2 Tailoring started by freezing all 406 tradeable Tailoring outputs across 17 sections. Seventeen cloth intermediates retain their completed Phase 1B evidence, leaving 389 finished outputs for this batch: three Tailor-only nets, 33 bags, eight spellthreads, 314 cloth gear pieces, 30 cosmetic shirts, and one tradeable utility item. All 406 outputs retain exact saved recipes, and the three hard Tailoring requirements remain isolated in the Tailor-only net section. The 17 First Aid outputs sharing the guide remain outside this profession batch. Phase 1 input baselines remain frozen, current Hellscream listings remain competition-only evidence, and exact recipe cost remains separate from estimated sale value. Nothing has been published.
- 2026-08-08: Phase 2 Tailoring completed its final comparison retry for all 389 finished outputs, and all 2,334 comparison requests resolved. No item had completed-sale evidence. The retry recovered usable relative-rank evidence for 377 outputs: 331 had three-realm support, 38 had two-realm support, eight had one-realm support, and 12 had no listings on the comparison realms. The pass changed 384 price bands; 183 Targets rose, 190 fell, and 16 stayed unchanged. Of 144 Target candidates whose movement exceeded 50%, 139 had at least two-realm support and were accepted, while five lacked enough coverage and retained their frozen bands. One hundred ninety-two final estimates remain below at least one exact recipe-floor band and keep shared do-not-craft guidance. The 17 Phase 1B cloth intermediates and all 17 First Aid outputs remained unchanged. Evidence references, shared notes, exact recipes, profession-use sections, ordering, search metadata, and the Tailoring guide footer were refreshed locally. Refresh this profession when useful Hellscream completed-sale history becomes available or a later scheduled evidence refresh is due. Nothing was published.
- 2026-08-08: Added the shared comparison retry rule: after an initial batch, failed requests wait 2, 5, and 10 seconds and retry while successful responses are preserved. A request is reported as failed only after all three waited retries fail; weaker refreshes must not replace stronger saved coverage.
- 2026-08-08: Phase 2 Leatherworking reviewed 476 finished outputs while preserving 14 completed Phase 1B leather and cured-hide intermediates. All 2,856 comparison requests resolved on the initial pass. Coverage reached all three realms for 394 outputs, two realms for 67, one realm for nine, and no realm listings for six. One Tough Scorpid Shoulders sale was low-confidence and received 25% weight; no sale passed the medium-confidence gate. Of 128 Target candidates whose movement exceeded 50%, 125 had at least two-realm support and were accepted, while three lacked enough coverage and retained their frozen bands. The pass changed 473 price bands; 231 Targets rose, 220 fell, and 25 stayed unchanged. Two hundred eighty-four final estimates remain below at least one exact recipe-floor band and keep shared do-not-craft guidance. Evidence references, shared notes, exact recipes, profession-use sections, ordering, search metadata, and the Leatherworking guide footer were refreshed locally. Nothing was published.
- 2026-08-08: Phase 2 Cooking reviewed all 162 auctionable outputs across 13 sections. All 972 comparison requests resolved on the initial pass. Coverage reached all three realms for 159 outputs and two realms for three; no completed-sale history was available. All 70 Target changes over 50% had at least two-realm support and were accepted. Every price band changed; 88 Targets rose, 71 fell, and three stayed unchanged. Fifty final estimates remain below at least one exact recipe-floor band and keep shared do-not-craft guidance. The four Cook-required feasts and Rogue-only Thistle Tea remain in their dedicated buyer sections. Evidence references, exact batch-yield recipes, notes, ordering, search metadata, and the Cooking guide footer were refreshed locally. Nothing was published.
- 2026-08-08: Phase 2 Mining and First Aid closeout started. Mining's 22 bars and alloys retain completed Phase 1A Evidence Pricing decisions, while its two mote outputs retain exact reversible 10:1 conversion decisions; no redundant comparison refresh is needed. First Aid's 17 finished outputs enter a separate Evidence Pricing review while their completed Phase 1B cloth inputs and documented venom-sac fallbacks remain frozen. Active Hellscream listings remain competition-only evidence, exact recipe cost remains separate from sale value, and nothing has been published.
- 2026-08-08: Phase 2 Mining and First Aid closeout completed. All 24 Mining-owned outputs still match their saved evidence: 22 bars and alloys retain Phase 1A Evidence Pricing decisions with three-realm coverage, and Mote of Fire plus Mote of Earth retain exact reversible 10:1 conversion decisions. No Mining price changed in the closeout. First Aid reviewed all 17 tradeable outputs; all 102 comparison requests resolved on the initial pass with three-realm coverage for every item and no completed-sale history. All five Target changes over 50% were accepted with full coverage. Every First Aid band changed; nine Targets rose, seven fell, and one stayed unchanged. Four First Aid estimates remain below at least one exact recipe-floor band. Exact recipes, output quantities, restrictions, notes, ordering, search metadata, and both guide views were refreshed locally. Phase 2 profession markets are complete; Phase 3 begins with Turn-ins. Nothing was published.
- 2026-08-08: Phase 3 Turn-ins completed. The old 26 grouped price rows were resolved to 74 exact auctionable item IDs with pinned 3.3.5 binding, maximum-stack, quest-quantity, repeatability, level, faction/event/standing, and purchase-quantity facts. Uncatalogued Species, Deadwood Headdress Feather, and Winterfall Spirit Beads were removed because their pinned records bind on pickup; the now-empty Timbermaw section was removed. All 444 comparison requests resolved on the initial pass with three-realm coverage for all 74 items. Seventy bands changed; 35 Targets rose, 28 fell, and 11 stayed unchanged. Six Target candidates over 50% passed the full-coverage review. Fiery Core, Lava Core, Core Leather, and Blood of the Mountain retained their already-audited shared-material bands. Grouped aliases were replaced by exact rows, true stack behavior, resolved rarity/tooltips, and item-specific notes. Nothing was published.
- 2026-08-08: Phase 3 Recipe and Pattern Drops completed. All 90 tradeable recipe items were pinned to exact profession, required skill, binding, learned-output market, loot-source, and vendor records. Eighty-five have saved loot paths; five purported drops are actually limited-vendor recipes and now show the exact vendor, stock, restock, and deterministic vendor-cost correction instead of false drop scarcity. All 540 comparison requests resolved on the initial pass; 89 items had three-realm coverage and one had two-realm coverage. Eighty-nine bands changed; 34 Targets rose, 50 fell, and six stayed unchanged. Fifteen Target candidates over 50% were reviewed. The Book of Glyph Mastery retained the user-reported 25g Target and recorded original baseline. All row notes now state the exact profession skill and output market, the shared methodology appears once, price order and the 11-item Blacksmithing count were corrected, and every tooltip resolves. Nothing was published.
- 2026-08-08: Phase 3 dropped-gear revalidation completed for all 85 Level-80 BoEs and 262 sought-after world drops. Today's privacy-preserving Hellscream snapshot still contains only the same two low-confidence sale items and no medium-confidence cohort; independent local supply presence increased from 23 to 33 items but remained diagnostic only. All 2,082 fresh comparison requests resolved on the initial pass, improving at-least-two-realm coverage from 305 to all 347 items. The refresh changed 309 bands: 70 of 85 Level-80 bands and 239 of 262 world-drop bands. Nine Target changes over 50% passed explicit slot, stats/socket/effect, buyer, acquisition-cohort, and three-realm reviews. Buyer/source cohorts now separately record Northrend leveling, Classic brackets/iconics, Outland level-70/leveling, containers, world bosses, raid trash, special summons, and other level-80 drops. The two sparse direct-sale bands remain low confidence; the other 345 remain fallback confidence. Ordering, search metadata, tooltips, and all four Phase 3 guide footers were refreshed locally. All three Evidence Pricing phases are complete; scheduled refreshes are next. Nothing was published.
- 2026-08-10: Added a nineteenth active guide for 133 verified tradeable
  companions, mounts, accessories, and event novelties. Unlimited coin vendors,
  limited-stock vendors, token vendors, farmed drops, quest rewards, crafted
  items, promotional rewards, and each individual holiday are separate
  sections. Exact coin, stock/restock, token, recipe, quest, and loot facts are
  pinned to saved source evidence. One sparse Wood Frog sale received 25%
  weight and was shrunk toward its fixed Hellscream cohort; active listings
  remained supply-only evidence and external gold values were not copied.
  Nothing was published.
