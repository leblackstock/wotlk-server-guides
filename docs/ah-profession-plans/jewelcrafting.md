# Jewelcrafting AH Expansion Plan

- Status: `complete` — Phase 2 gems and jewelry complete locally, 2026-08-06
- Active guides:
  - `guides/jewelcrafting-gems-ah-price-guide.html`
  - `guides/jewelcrafting-jewelry-ah-price-guide.html`
- Work type: full crafted catalog
- Suggested order: 2

> Hard gate: finish and record the baseline evidence audit before adding crafted
> rows. Follow [the shared Gate 0](README.md#gate-0-establish-non-circular-baselines-before-adding-crafteds).

## Baseline Evidence Audit

- Recheck all 80 current rows: epic/rare/uncommon raw gems, meta bases and cut
  metas, Dragon's Eye, prospecting ores, older gems, stone, and settings.
- Reconcile ores with Mining, Eternals with cross-profession materials, and
  raw-gem prices wherever the same gem appears in another guide.
- Verify the server's binding/tradeability rules for Dragon's Eye and
  jewelcrafter-only cuts before retaining or pricing them.
- Audit existing cut-gem values against the current uncut-gem opportunity cost.

## Crafted Coverage

- All valid tradeable cuts for Wrath epic, rare, uncommon, and meta gems, with
  exact cut item IDs and recipe spell IDs.
- Tradeable rings, necklaces, crowns, trinkets, statues, settings, and other
  deterministic Jewelcrafting outputs across Wrath, Outland, and Classic.
- Review Icy Prism and other random-output crafts separately; list outputs in
  their normal material sections, not as deterministic finished crafts.
- Exclude BoP figurines, jewelcrafter-only results that are not auctionable,
  self-only effects, and invalid duplicate spell records.

## Profession-Specific Price Checks

- A cut gem consumes the sale value of its uncut gem. Calculate the floor from
  that exact color/quality, then add only a demand-supported cutting premium.
- Do not assign the full Icy Prism or prospecting input cost to each possible
  gem. Use documented expected value if those conversions are analyzed.
- Check whether identical stats exist in multiple colors or qualities; price
  each from its own input and demand, not by copying a same-stat result.
- Price jewelry from exact gems, settings, bars, and vendor components; keep
  slow BoE gear in singles.

## Notes to Verify

- For gems, give the exact stat combination and likely role/build without
  claiming universal best-in-slot status.
- Call out meta activation requirements in concise item-specific notes when
  they materially affect demand.
- For jewelry, state slot, level, role, binding, and whether the market is
  gearing, twink, leveling, or collection driven.

## Acceptance Checks

- [x] Baseline evidence audit completed and recorded.
- [x] Every valid tradeable cut has an item ID, recipe ID, rarity, and price.
- [x] Raw-versus-cut opportunity costs are tested.
- [x] Random-output conversions use an explicit model or remain unpriced.
- [x] BoP and jewelcrafter-only non-AH outputs are excluded.
- [x] Shared validation in `README.md` passes.

## Phase 2 Gem Evidence Pricing Acceptance

- [x] All 360 cut and special-gem outputs have a saved before/after review.
- [x] Every cut consumes exactly one reviewed uncut gem and preserves that
  opportunity cost as a separate diagnostic.
- [x] Same expansion, quality, and color define each comparison cohort.
- [x] All Target candidates over 50% have an explicit reviewer decision.
- [x] Six duplicated meta-gem baselines remain synchronized.
- [x] Repeated cut-gem boilerplate is removed while exact stats, socket colors,
  and meta activation requirements remain.
- [x] Gem guide, search, ordering, tooltip, currency, rarity, eligibility, and
  desktop/mobile validation pass.
- [x] The 137 jewelry, component, setting, and sealed random-result outputs have
  completed their separate Phase 2 review.

## Evidence Log

- Audit date: 2026-08-03.
- Baseline audit: The pre-expansion guide contained 80 priced rows. Seventy-four
  resolved to real item IDs and all 74 had frozen non-circular references; the
  remaining six were synthetic cut-gem pricing rules and were replaced by
  individual finished items. Of those 74 references, 73 were low-confidence
  frozen pre-scan values and Solid Stone was the one medium-confidence
  realized-sales reference. All 32 items duplicated in another guide agreed
  with their canonical bands. Per-item/stack semantics and `quick <= target <=
  high` checks passed.
- Listing concentration observations (not valuation evidence): The saved
  2026-08-02 diagnostic remains heavily concentrated, including the user's
  report that the user and friends account for at least half the listings. No
  active listing price was imported into a baseline or craft calculation.
- Recipe/item sources checked: Complete WotLKDB 3.3.5 Jewelcrafting skill 755
  list using six non-overlapping skill ranges (566 spells, 558 outputs), exact
  recipe reagents and spell IDs, WotLKDB item tooltips for exact gem effects and
  meta requirements, and AzerothCore `item_template` build 12340 for item ID,
  quality, binding, class, required level, item level, and RequiredSkill.
- Ingredient coverage: Existing frozen baselines and canonical crafted/vendor
  sources covered all but nine direct inputs. Added documented fallbacks for
  Arcane Crystal, Adamantite Powder, and the six tradeable Outland epic uncut
  gems; each is explicitly fallback confidence and no listing set its value.
  Purified Draenic Water uses its exact unlimited-vendor cost of 12s 80c each.
- Server-specific binding findings: 497 outputs are tradeable (376 unbound and
  121 Bind on Equip) and none has a hard Jewelcrafting-use requirement. The 61
  Bind on Pickup outputs are excluded, including Dragon's Eye cuts, figurines,
  statues, and faction-bound gem rewards. Raw Dragon's Eye remains in the
  existing Jewelcrafter-only material section.
- Random-output method: Brilliant Glass and Icy Prism are priced only as sealed
  finished items from their exact recipes. Prismatic Black Diamond is priced
  from one Black Diamond; its eventual cut is explicitly random. No possible
  gem result inherits the full random craft cost.
- Decisions and unresolved items: Cut-gem floors use the saved sale value of
  the exact uncut gem before applying the demand margin, rather than the raw
  gem's cheapest recursive production cost. Eight new market inputs remain
  documented fallbacks until independent realized sales or measured acquisition
  evidence replaces them.
- Completion summary: Added all 497 tradeable outputs in 45 price-sorted
  sections: 366 cut/special gems, 120 jewelry or other armor pieces, five
  components, five utilities/random-result items, and one weapon. Every row has
  a rarity color, exact item ID, item-specific use/effect note, recipe-and-mats
  mouseover link, exact recipe floor, and a reference to one shared `*`
  craft-cost note. The six generic pricing rows and eleven duplicate legacy
  crafted rows were removed from the static portion of the guide.
- Presentation split: on 2026-08-04, the 560-row indexed guide was split into
  `Jewelcrafting Gems & Cuts` (418 indexed rows, including 360 canonical crafted
  outputs) and `Jewelcrafting Jewelry & Components` (142 indexed rows, including
  137 canonical crafted outputs). Both pages remain filtered views of the same
  canonical Jewelcrafting catalog, so all recipe, pricing, and profession-use
  audits continue to run against one source of truth.
- Material-baseline refresh — 2026-08-06: Phase 1B rechecked 58 ore, raw-gem,
  uncut-gem, meta-base, and Dragon's Eye references. Ten ore inputs inherit the
  completed Phase 1A review and 48 newly reviewed gem/material bands changed.
  Cut gems and finished jewelry remain outside this phase.
- Phase 2 gem Evidence Pricing started — 2026-08-06: the gem-view inventory is
  frozen at 360 tradeable cut outputs across 38 sections. The 137 jewelry,
  component, setting, and sealed random-result outputs are reserved for the
  following phase. Exact uncut-gem opportunity costs remain separate
  craftability diagnostics; current Hellscream listings remain competition-only
  evidence. Six cut metas duplicate legacy baseline rows and must remain
  synchronized. Work is local and nothing has been published.
- Phase 2 gem Evidence Pricing completed — 2026-08-06: all 360 cut outputs
  received saved before/after bands, exact uncut-gem opportunity-cost
  diagnostics, sanitized completed-sale coverage, six-source comparison
  coverage, confidence, and explicit reviewer decisions. No cut had qualifying
  local completed-sale history. Three hundred forty-two cuts had all-three-realm
  comparison coverage and 18 had two-realm coverage. All three Target candidates
  over 50% had three-realm support and were accepted. Every price band changed;
  171 Targets rose, 174 fell, and 15 stayed unchanged. One hundred twenty-eight
  final estimates are below at least one uncut opportunity-cost band and retain
  do-not-cut guidance. Six legacy meta-gem baselines were synchronized. Repeated
  row boilerplate was removed from all 360 cuts, while exact effects, socket
  matching, meta requirements, and nine true same-stat aliases remain explicit.
  The 137 companion jewelry/component outputs were not repriced. Work remains
  local and nothing has been published.
- Phase 2 jewelry Evidence Pricing started — 2026-08-06: the companion
  inventory is frozen at 137 tradeable jewelry, component, setting, utility,
  weapon, and sealed random-result outputs across seven sections. Phase 1
  ingredient baselines remain frozen, current Hellscream listings remain
  competition-only evidence, and exact recipe cost remains a separate
  craftability diagnostic. Work is local and nothing has been published.
- Phase 2 jewelry Evidence Pricing completed — 2026-08-06: all 137 outputs
  received saved before/after bands, exact recipe-cost diagnostics, sanitized
  completed-sale coverage, six-source comparison coverage, confidence, and
  explicit reviewer decisions. Six outputs had completed-sale history; one
  passed the medium-confidence gate and five remained sparse, shrunk evidence.
  One hundred thirteen outputs had all-three-realm comparison coverage, 12 had
  two-realm coverage, seven had one-realm coverage, and five had none. All 38
  Target candidates over 50% had at least two-realm support and were accepted.
  One hundred thirty-two price bands changed; 61 Targets rose, 58 fell, and 18
  stayed unchanged. Fifty-five final estimates are below at least one exact
  recipe-floor band and retain shared do-not-craft guidance. Five legacy
  baselines were synchronized. Repeated sales boilerplate was removed from all
  121 BoE notes, while exact slot, level, stats, effects, and random-suffix
  warnings remain. Work remains local and nothing has been published.
