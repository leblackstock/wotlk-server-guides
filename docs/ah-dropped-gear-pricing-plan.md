# Dropped-Gear Repricing Plan

- Status: `Phase 3 revalidated locally on 2026-08-08 — not published`
- Recorded: `2026-08-05`
- Guides:
  - `guides/level-80-boe-epics-ah-price-guide.html`
  - `guides/sought-after-world-drops-ah-price-guide.html`
- Canonical catalog: `data/ah-dropped-gear.json`
- Canonical price file: `data/ah-price-baselines.json`
- Governing method: [Non-Circular AH Pricing Methodology](ah-pricing-methodology.md)
- Implementation result: the full 347-item evidence/review layer is complete.
  Two pre-guide sparse-sale bands use direct Hellscream evidence at `low`
  confidence. The other 345 rows now use reviewed low-pop starter estimates at
  `fallback` confidence. Public pages have not been published.

## Objective

Replace the broad tier fallbacks with defensible item-level estimates while
preserving a clear distinction between completed sales, measured acquisition,
current competition, cross-server context, and unsupported fallback judgment.

The finished pass must improve accuracy without pretending that a current
asking price is a completed sale. Every proposed Quick, Target, and High / Scarce
band must be reproducible from saved evidence and must retain an honest
confidence label.

## Recorded Starting Point

- At plan recording, all 347 dropped-gear rows used `documented-fallback` evidence with
  `fallback` confidence.
- The Level 80 BoE guide has 85 items but only seven distinct price bands. Its
  current fallback is driven mainly by item level.
- The World Drops guide has 262 items but only eleven distinct price bands:
  87 Northrend, 73 Outland, and 102 Classic items. Its current fallback is
  driven mainly by rarity and required-level bracket.
- The original model did not price exact stat quality, role coverage, bracket
  strength, unique effects, replacement alternatives, measured turnover, or
  item-specific supply.
- The AzerothCore audit already records item identity, rarity, binding,
  required level, item level, slot, vendor value, source type, and source
  evidence. It does not yet preserve every stat, effect, drop chance, or
  measured acquisition-time field needed for item-level valuation.

This makes the present values useful placeholders, not sufficiently granular
market estimates.

## Non-Negotiable Evidence Rules

1. Hellscream/Garrosh completed sales are the strongest market evidence.
2. Measured acquisition can establish a supply anchor only when route, elapsed
   time, quantity, and opportunity-cost assumptions are recorded.
3. Active Hellscream listings describe supply and competition. They do not set
   price bands automatically and cannot promote confidence.
4. Other servers' active listings are cross-server diagnostics only. Their raw
   or normalized asking prices do not become Hellscream baselines. A separately
   approved fallback review may use only their within-group relative rank, with
   a fixed Hellscream anchor establishing the gold scale.
5. Other servers' completed sales, if genuinely identifiable, may inform a
   low-confidence relative comparison after normalization, but cannot promote a
   Hellscream estimate above `low` without local support.
6. A single sale, listing, buyer, seller, day, or server never establishes a
   general-use target by itself.
7. Self purchases, known friend/guild transfers, test auctions, bids,
   cancellations, and expirations are excluded from realized-sale evidence.
8. Raw SavedVariables, character names, buyer names, and account identifiers
   remain outside the repository. Only sanitized aggregates and evidence
   hashes may be recorded.
9. Publishing remains a separate step and requires explicit authorization.

## Evidence Precedence

| Evidence | May change the numerical baseline? | Maximum initial confidence | Use |
|---|---:|---:|---|
| Direct Hellscream completed sales | Yes, after the gate | `medium` | Primary item valuation |
| Direct measured acquisition | Yes, after the gate | `medium` | Supply/value anchor |
| Sparse Hellscream item sales | Manual only | `low` | Shrunk toward a validated cohort |
| Hellscream cohort sales | Manual fallback estimate | `fallback` | Price an unsold but comparable item |
| Cross-server completed sales | Manual relative check | `low` | Normalized sanity check only |
| Cross-server active listings/history | Relative rank only after explicit review | `fallback` | Order items within fixed Hellscream starter anchors; never copy gold values |
| Hellscream active listings | No direct baseline import | none | Posting timing and concentration |
| Existing tier formula | Yes, only as last resort | `fallback` | Preserve coverage when evidence is absent |

## Phase 0 — Freeze and Inventory the Existing State

- Export a deterministic table for all 347 rows containing item ID, guide,
  section, rarity, required level, item level, slot, buyer, demand label, source,
  current band, source type, confidence, and reason.
- Record the current seven Level 80 bands and eleven World Drop bands as the
  comparison baseline.
- Verify that every row still passes auction eligibility and remains fixed-stat,
  BoE, non-temporary, and drop-sourced.
- Record duplicate prices and same-item references elsewhere in the AH guides.
- Do not edit the current baselines during evidence collection.

Output: a reproducible `before` report against which every later proposal is
compared.

## Phase 1 — Build a Sanitized Evidence Layer

Create a dedicated canonical evidence file rather than overloading the visible
guide catalog:

`data/ah-dropped-gear-price-evidence.json`

Recommended per-item fields:

- item ID and canonical key;
- evidence refresh date and source checksums;
- direct completed-sale count, units, distinct anonymized buyers, and distinct
  sale days;
- gross unit prices, net proceeds when available, and the rule used to reconcile
  auction cut or stack size;
- excluded-record counts and exclusion reasons;
- measured acquisition route, attempts, elapsed time, output, and assumed
  gold-per-hour;
- local listing snapshot counts, independent sellers, unit concentration, and
  known-account exclusions, stored as diagnostics only;
- external realm observations with server, realm, faction, progression, rates,
  timestamp, scan age, quantity, and source URL;
- comparable cohort and manually reviewed item features;
- proposed band, evidence class, confidence, rationale, and reviewer state.

Raw inputs should be processed from an ignored local working directory. The
repository receives only sanitized aggregates needed to reproduce a decision.

## Phase 2 — Import Hellscream Completed Sales

Build a read-only BeanCounter importer that:

- accepts copied SavedVariables rather than reading or modifying the live game
  installation;
- filters to the intended realm, faction/AH, item IDs, and successful sales;
- normalizes every record to gross copper per item;
- removes bids, cancelled/expired auctions, test records, duplicates, self
  purchases, and known friend/guild transfers;
- hashes buyer identity with a run-specific salt so distinct-buyer counts can
  be checked without committing names;
- produces coverage and exclusion reports before estimating any price;
- never writes directly to `data/ah-price-baselines.json`.

### Recommended rare-gear sales gate

The shared twenty-unit material gate is poorly matched to one-at-a-time BoE
gear. Before implementation, amend the shared methodology and tests with a
gear-specific rule. Recommended starting rule:

- `medium`: at least four completed item sales, two distinct buyers, and two
  distinct days, with no buyer controlling most observations;
- stronger medium coverage: at least eight sales, four buyers, and four days;
- `low`: one to three valid sales, or sales concentrated in one buyer/day;
- `fallback`: no qualifying direct sales.

This recommendation is not active policy until it is explicitly added to the
shared methodology and validated against the available sales volume.

## Phase 3 — Record Local Supply Without Circular Pricing

- Capture at least three full Hellscream snapshots across different days and
  time windows when practical.
- Record item presence, quantity, seller count, concentration, relist frequency,
  and time absent from the AH.
- Exclude the user's and known friends' auctions before calculating
  concentration.
- Mark seller concentration unknown when source data cannot identify sellers.
- Use the result to classify supply as persistent, episodic, bursty, or rarely
  observed.
- Use asking prices only for posting decisions and outlier diagnostics. No
  current listing statistic may automatically become Quick, Target, or High.

## Phase 4 — Add Cross-Server Live Context

Candidate public sources verified as accessible when this plan was recorded:

- [WoWAuctions](https://www.wowauctions.net/auctionHouse) exposes current
  realm scans and item pages, including ChromieCraft's merged AH, scan age,
  availability, and listing-price history.
- [Web Auctioneer](https://ah.nerfed.net/servers/base?id=7) exposes current
  Warmane realm/faction scans and offers downloadable scan data for Lordaeron,
  Icecrown, and Onyxia.

Revalidate availability, terms, realm progression, and data freshness before
execution. Use only public or explicitly authorized downloads and rate-limit
collection.

### Cross-server normalization

Other server economies must never be treated as one interchangeable market.
For each realm:

1. Record expansion/progression, population profile, XP/drop/gold rates,
   faction merging, custom vendors/store effects, and scan age.
2. Build a benchmark basket from liquid, shared WotLK items that also have
   independent Hellscream evidence.
3. Calculate a robust realm economy index from the basket using median log
   ratios; exclude custom-shop, phase-locked, manipulated, or unavailable items.
4. Compare a dropped item's relative rank against its realm's basket rather
   than copying its nominal gold price.
5. Require multiple snapshots across at least seven days before calling an
   external availability pattern stable.
6. Mark seller concentration unknown when the source exposes only aggregates;
   unknown concentration caps the observation at diagnostic weight.
7. Run leave-one-realm-out sensitivity. If removing one realm changes the
   diagnostic conclusion materially, flag the item for manual review.

External active-listing values must remain outside the estimator's automatic
price inputs. They may flag that a proposal is implausibly ordered or that an
item is commonly available elsewhere, but they do not prove a Hellscream sale.

## Phase 5 — Expand the Item and Supply Audit

Extend the pinned 3.3.5/AzerothCore audit to preserve, where applicable:

- stat types and values, armor, weapon damage/speed, sockets, socket bonus, and
  equip/use spell IDs;
- class or armor-type coverage and likely role/spec audience;
- direct and reference-loot chance, min/max count, source type, container type,
  and repeatability;
- raid trash, world boss, dungeon trash, chest, event, fishing/container, and
  ordinary world-drop distinctions;
- deterministic vendor liquidation value as a hard lower reference, not an AH
  target;
- verified server-specific drop or access changes, kept separate from the
  pinned base-game source.

Then manually audit unique-effect and iconic items whose value cannot be read
from item level alone.

## Phase 6 — Build Independent Comparable Cohorts

Do not use the current `demand` label as a model input; it was generated from
the same broad rules being replaced. Establish cohorts from independently
audited features.

### Level 80 BoE Epics

Group first by item level, then refine by:

- slot and armor class;
- tank, healer, caster, physical DPS, or multi-role usefulness;
- stat allocation quality, sockets, and unique effects;
- number of classes/specs able to use the item well;
- raid/fresh-80/catch-up alternatives in the same slot;
- source cadence: raid trash, event/container, world drop, or other gated source;
- direct completed-sale coverage and observed turnover.

### Sought-After World Drops

Model these markets separately:

1. Northrend levels 71–79: leveling/fresh-80 bridge value, item level, slot,
   replacement window, and role coverage.
2. Fixed-stat bracket rares: exact bracket, verified BiS/near-BiS standing,
   unique stats/effects, faction access, and source repeatability.
3. Level 70 Outland epics/rares: legacy endgame utility, twink value, unique
   effects, and availability of better deterministic alternatives.
4. Classic legacy epics: bracket/legacy utility, iconic or proc value, and
   source scarcity. Do not import modern transmog demand into WotLK pricing.
5. Containers, world bosses, raid trash, and special events: use a separate
   supply classification rather than treating every world drop alike.

Every item receives a cohort, but unique items may require a documented manual
override rather than a forced statistical fit.

## Phase 7 — Estimate and Calibrate Bands

Use a transparent hierarchical model rather than an opaque one-step score:

1. Direct qualifying Hellscream sales, when present.
2. Sparse direct sales shrunk toward a validated Hellscream cohort.
3. Cohort completed-sale evidence plus audited item/supply adjustments.
4. Measured acquisition anchors where valid.
5. Existing conservative fallback when the evidence above is insufficient.

Recommended calculations:

- work in log prices so multiplicative economy differences and extreme BoE
  values do not dominate the fit;
- use recency-weighted robust statistics, reporting both the full observation
  window and the effective sample size;
- set Target from the robust center of qualifying evidence;
- set Quick and High from supported lower/upper dispersion rather than fixed
  multipliers or an empty AH;
- shrink sparse estimates toward their cohort in proportion to evidence, never
  through an undocumented manual percentage;
- store exact copper and round only in the existing display layer.

### Model acceptance gate

- Use leave-one-item-out validation on items with adequate direct sales.
- Compare the proposed cohort model with the existing tier fallback on the same
  holdouts.
- Do not deploy a cohort model unless it reduces error versus the current
  fallback and shows no systematic bias by guide, era, slot, rarity, or item
  level.
- Report median absolute percentage/log error, worst outliers, and coverage;
  do not hide sparse or failed cohorts in one overall average.
- Flag every proposed Target change over 50%, every confidence promotion, and
  every unusually wide band for manual review.

## Phase 8 — Item-by-Item Review Order

1. All 85 Level 80 BoE epics because errors carry the largest gold impact.
2. The 87 Northrend world drops because they serve the broadest immediate
   leveling/fresh-80 market.
3. Fixed-stat bracket rares and iconic/unique-effect Classic items.
4. Outland level-70 gear and special-source drops.
5. Remaining slow-sale legacy epics.

For each item, the review report must show:

- old and proposed Quick/Target/High;
- absolute and percentage change;
- direct-sales coverage and exclusions;
- acquisition evidence, if any;
- cohort and comparable items;
- local supply classification;
- cross-server diagnostic result;
- proposed evidence class, confidence, and plain-language rationale;
- reviewer decision: accept, revise, or retain fallback.

## Phase 9 — Dry Run Before Any Price Edit

Implement the estimator with separate modes:

- `--report`: generate proposals and evidence summaries without editing data;
- `--check`: verify evidence, model, and generated report freshness;
- `--apply`: update approved baselines only after explicit review.

The first complete run must stop after `--report`. Review the 347-row diff and
resolve every flagged item before `--apply` is authorized.

## Anticipated Implementation Files

- `data/ah-dropped-gear-price-evidence.json` — sanitized evidence and approvals.
- `scripts/import-ah-beancounter-sales.py` — read-only sanitized sales importer.
- `scripts/audit-ah-dropped-gear.py` — expanded item/stat/drop evidence.
- `scripts/estimate-ah-dropped-gear-prices.py` — report/check/apply estimator.
- `tests/ah-dropped-gear-pricing.test.py` — provenance, model, confidence, and
  non-circularity guards.
- `docs/ah-pricing-methodology.md` — gear-specific sales gate, if approved.
- `data/ah-price-baselines.json` — changed only in the reviewed apply phase.
- Existing renderer, search index, ordering data, and both guides — regenerated
  only after approved price changes.

Exact filenames may be refined during implementation, but evidence must remain
separate from raw private exports and visible guide content.

## Validation and Definition of Done

- [x] All 347 items have a complete evidence record and review decision.
- [x] Raw private identities and SavedVariables are absent from the repository.
- [x] Every changed band traces to accepted evidence and a reproducible rule.
- [x] Every modeled starter estimate records its anchor, relative rank,
      coverage weight, rounding rule, and fallback confidence.
- [x] Active local or external listing prices never automatically update a
      baseline or confidence.
- [x] Cross-server observations include realm metadata, scan age, and
      normalization/sensitivity results.
- [x] No cohort model was deployed because no item passed the medium gate; there
      were no eligible holdouts on which to claim improved validation.
- [x] `quick <= target <= high` for every item, with exact copper retained.
- [x] Every confidence promotion passes the approved evidence gate.
- [x] Manual review is complete for all >50% Target changes and unique-effect
      items.
- [x] Price-sorted sections are regenerated and checked with
      `scripts/apply-ah-section-price-order.py`.
- [x] Dropped-gear data, price-baseline, cross-guide, currency, search,
      guide-UX, and desktop/mobile browser tests pass.
- [x] Both edited guide footers use the implementation date.
- [x] A final before/after report is recorded before publication.
- [x] Publishing remains gated behind a separate explicit “make it live” request,
      with unrelated work left unstaged and the public Pages result verified.

## Inputs Needed When Work Begins

- A copied, backed-up BeanCounter SavedVariables file for the intended
  Hellscream/Garrosh realm and faction, or a sanitized export containing the
  same completed-sale facts.
- Known self/friend/guild seller or buyer identities for local exclusion; these
  can remain local and be represented only by hashes in aggregates.
- At least three current Hellscream AH scans if local supply concentration and
  availability are to be audited.
- Confirmation of the intended auction house/faction scope and any known
  server-specific loot, drop-rate, event, or vendor changes.
- Approval of the rare-gear completed-sales gate before confidence promotions.

## Evidence Log

- 2026-08-05: Plan recorded. Repository inspection confirmed 347
  `documented-fallback`/`fallback` rows: 85 Level 80 items using seven distinct
  bands and 262 World Drops using eleven distinct bands.
- 2026-08-05: WoWAuctions was confirmed to expose current ChromieCraft item
  pages with scan timestamps, availability, and listing history. Web Auctioneer
  was confirmed to expose current Warmane Lordaeron, Icecrown, and Onyxia
  realm/faction scans plus downloadable data. These are candidate external
  diagnostics, not accepted Hellscream sale evidence.
- 2026-08-05: No guide price, confidence, footer, generated asset, or public page
  was changed as part of recording this plan.
- 2026-08-05: Imported a privacy-preserving Hellscream BeanCounter snapshot and
  current Auctioneer scan. Three valid completed buyouts covered two catalog
  items; 23 catalog items remained listed after known-account exclusions. No
  character, buyer, seller, account, or local path was committed.
- 2026-08-05: Expanded the pinned item audit with stats, sockets, spells,
  armor/weapon values, class restrictions, and declared loot-source structure.
- 2026-08-05: Downloaded six current Warmane Auctioneer snapshots outside the
  repository for Lordaeron, Icecrown, and Onyxia, split by faction. Each source
  received its own median-log economy index from six shared commodities with
  actual Hellscream sales. Only dimensionless coverage, relative-rank, and
  leave-one-realm-out diagnostics were retained; raw external prices and seller
  identities were not committed or used to set a band.
- 2026-08-05: Cross-server coverage reached at least two realms for 305 of 347
  items. After economy normalization, 270 external ask patterns were below the
  saved Hellscream target, 27 broadly aligned, eight were above, and 42 lacked
  sufficient realm coverage. These are review flags, not completed-sale proof.
- 2026-08-05: Completed all 347 review decisions. Sandals of Broken Dreams moved
  from 100g / 200g / 400g to 8g 60s 88c / 9g 56s 53c / 11g 95s 66c from two
  pre-guide completed buyouts. Zom's Crackling Bulwark moved from 180g / 300g /
  600g to 297g 50s / 350g / 455g from one pre-guide completed buyout. Both remain
  `low` confidence; the other 345 rows remain `fallback` confidence.
- 2026-08-05: The user clarified that the operational goal is the best practical
  first-post estimate for a low-pop server, so the market can discover the
  eventual price. Replaced all 345 generic tier fallbacks with reviewed starter
  bands. External observations determine relative rank only; fixed Hellscream
  anchors determine gold scale, limited coverage is shrunk toward each group
  midpoint, and external gold values are never copied. All 345 modeled bands
  changed numerically; 260 Target changes exceed 50% and are recorded in the
  complete before/after review.
- 2026-08-05: Recorded the complete before/after review in
  `docs/ah-dropped-gear-repricing-review.md`. Changes remain local and unpublished.
- 2026-08-05: All AH Python tests, static Node tests, guide-banner tests, ordering
  checks, generated-asset checks, and the desktop/mobile Auction House browser
  smoke suite passed.
- 2026-08-08: Reimported today's privacy-preserving Hellscream BeanCounter and
  Auctioneer snapshot. The same two items retain sparse completed-sale evidence;
  no item reached the medium gate. Independent supply presence increased from
  23 to 33 items but remains diagnostic only.
- 2026-08-08: Refreshed all 2,082 Lordaeron, Icecrown, and Onyxia item-page
  comparisons. Every request resolved on the initial pass under the required
  2-, 5-, and 10-second retry rule, improving at-least-two-realm coverage from
  305 to all 347 items. No external gold value was stored or copied.
- 2026-08-08: Revalidated all 347 bands and accepted nine Target changes over
  50% after explicit slot, stats/socket/effect, buyer, acquisition-cohort, and
  three-realm review. Seventy of 85 Level-80 bands and 239 of 262 world-drop
  bands changed. Separate buyer/source cohorts now cover Northrend leveling,
  Classic brackets/iconics, Outland level-70/leveling, containers, world bosses,
  raid trash, special summons, and other level-80 drops. Changes remain local.
