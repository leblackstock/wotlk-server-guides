# AH Item Addition Work Order — All Auctionable Containers

- **Date:** 2026-08-08
- **Status:** complete and published — 2026-08-08
- **Requested scope:** coupled batch
- **Market type:** vendor | crafted | quest reward | world drop
- **Target guide and section:** Profession guides, Sought-After World Drops, and Drop / Turn-In / Quest-Page Items
- **Profession plan or evidence-status owner:** Tailoring, Leatherworking, Engineering, Enchanting, Inscription, Mining, Herbalism, and Jewelcrafting plans plus the container-specific evidence review
- **Publishing authorized:** yes — 2026-08-08

## Requested Items

The pinned inventory contains 175 bag, pouch, quiver, ammo-pouch, and profession-container records with storage slots. Of those, 93 are both auction-eligible and obtainable in the pinned data: 52 recipe-backed crafted containers already covered by the profession guides, 19 vendor containers, 21 drop-owned containers, and one quest-reward container. The remaining records are non-auctionable, deprecated/test, or lack a verified acquisition source.

| Item group | Items | Intended buyer/use | Price basis | Group reason |
|---|---:|---|---|---|
| Existing crafted containers | 52 | General storage, profession-material storage, and Hunter ammunition | Per item | Verify complete profession coverage and comparable prices |
| Missing vendor containers | 19 | General storage, profession-material storage, and Hunter ammunition | Per item | Exact vendor cost, stock, and restock are deterministic evidence |
| Missing dropped containers | 21 | Leveling characters, alts, and appearance/name collectors | Per item | Same acquisition cohort and capacity-based comparable market |
| Missing quest-reward container | 1 | General 14-slot storage | Per item | Verified 50-ticket Darkmoon Faire reward |

## Gate A — Identity and Eligibility

- **Pinned item-template source and commit:** AzerothCore WotLK `item_template` at `e0fe11ba46b885a01e4a4038001e0055822cc7ba`
- **Vendor stock/restock, if any:** Saved per item from the pinned `npc_vendor` table; unlimited and limited-stock routes remain distinct.
- **Recipe/spell and guaranteed output, if any:** Reconciled against `data/ah-crafted-recipe-audit.json`; all 52 recipe-backed containers already have one canonical crafted row.
- **Quest or gear-use facts, if any:** Darkmoon Storage Box is the guaranteed reward from quest 7934, `50 Tickets - Darkmoon Storage Box`.
- **Restricted buyer section required:** No hard profession skill is required to equip the verified vendor containers. Specialty bags are labeled for their actual profession-material buyer.
- **Exclusions and reasons:** Deprecated/test records are excluded. Records with no recipe, loot, vendor, or quest-reward route in the pinned source remain excluded as acquisition-unverified.

## Duplicate and Dependency Audit

| Group | Existing guide/data locations | Canonical owner | Decision |
|---|---|---|---|
| 52 crafted containers | `data/ah-crafted-sections.json` | Crafting profession guide | Retain; do not duplicate |
| Small Brown Pouch | Pinned vendor and loot tables | Tailoring vendor/convenience section | Use deterministic vendor ownership and mention the secondary drop route |
| 18 other vendor containers | Not yet in guide data | Actual profession buyer or Tailoring general-bag market | Add once each |
| 21 drop-owned containers | Not yet in guide data | Sought-After World Drops | Add once each |
| Darkmoon Storage Box | Not yet in guide data | Drop / Turn-In / Quest-Page Items | Add once |

## Gate B — Evidence

### Completed Hellscream sales

The sanitized BeanCounter pass found zero records for the 22 non-vendor additions. Confidence therefore remains fallback unless later completed sales replace it.

- **Known-account and invalid-transaction exclusions:** Existing sanitized importer rules applied; no buyer or seller identities are saved.

### Current listings — diagnostic only

The current Auctioneer snapshot will be saved only as aggregate presence and seller-concentration diagnostics. Listing prices will not be saved or used to set a price.

- **`used_to_set_prices`:** false

### Deterministic and external evidence

- **Exact vendor/conversion/acquisition anchor:** Pinned vendor cost, stock, and restock for vendor containers; exact 50-ticket reward route for Darkmoon Storage Box.
- **Fixed Hellscream cohort anchor:** Existing reviewed crafted-container Targets grouped by capacity and allowed contents.
- **External realms/factions covered:** Lordaeron, Icecrown, and Onyxia, both factions, for relative rank only.
- **Comparison retry result:** 132 initial requests, zero retry rounds needed, zero final failures; the saved rule remains initial + 2s + 5s + 10s
- **`external_gold_values_copied`:** false
- **Saved evidence file/report:** `data/ah-container-price-evidence.json` and `docs/ah-container-pricing-review.md`

## Gate C — Price Proposal and Review

All 19 vendor containers use pinned vendor cost, stock, and restock facts with explicit convenience margins. The 21 dropped containers and Darkmoon Storage Box use frozen Hellscream capacity anchors from the already-reviewed crafted bags; external comparisons rank items only within their capacity cohort and do not supply gold values. No completed Hellscream sale qualified, so all 22 non-vendor additions remain clearly labeled starter estimates with fallback confidence.

## Craftability Diagnostic

No new crafted rows are being introduced. Existing recipe-backed containers retain their saved exact recipe floors and recipe links.

## Canonical Implementation

- **Canonical source files:** `data/ah-crafted-sections.json`, `data/ah-vendor-sections.json`, and `data/ah-container-sections.json`
- **Evidence/report files:** `data/ah-container-audit.json`, `data/ah-container-price-evidence.json`, and `docs/ah-container-pricing-review.md`
- **Renderer/reviewer files:** `scripts/audit-ah-containers.py`, `scripts/review-ah-container-prices.py`, and `scripts/render-ah-container-sections.py`
- **Generated guides/assets:** Ten guide pages, `assets/ah-search-index.js`, `assets/ah-item-ids.js`, `assets/ah-guide-navigation-data.js`, and `auction-house.html`
- **Profession plan/status log updated:** yes — all eight affected profession plans include the 2026-08-08 container coverage addendum
- **Changed guide footer date:** yes — every changed guide footer is `Updated 2026-08-08`

## Guide Content Check

- [x] Exact name and pinned rarity color
- [x] Per-item price basis is explicit
- [x] Quick, Target, and High are ordered where applicable
- [x] Buyer/use/demand note is item-specific
- [x] Profession restriction is in a dedicated section when required
- [x] Stack recommendation is omitted for every non-stackable container
- [x] WotLK item tooltip resolves
- [x] Existing crafted recipe and materials mouseover links remain intact
- [x] Shared methodology is referenced once with `*`, not repeated per row
- [x] Published price uses no more than two currency units

## Validation Record

| Command/check | Result | Notes |
|---|---|---|
| Container audit/reviewer `--check` | pass | 93 obtainable auctionable containers; 22 non-vendor price reviews current |
| Canonical renderer checks | pass | Shared sections, container sections, and guide UX are mutually current |
| AH Python regression suite | pass | 38 of 38 tests, including the generated collection contract |
| `npm test` | pass | Node, guide banner, fresh-80 workflow, and audience suites |
| Local desktop/mobile AH smoke | pass | AH hub, Bags & Containers filters/sorts/tooltips, both drop guides, nested navigation, redirects, and all 12 crafted-guide views |
| Auction eligibility | pass | 93 included containers are auctionable and obtainable; excluded records remain out |
| Duplicate price/rarity/stack consistency | pass | Every included container has one canonical owner; all item names use pinned rarity; no stack suggestion is rendered |
| Section price ordering | pass | 18 guides, 329 priced tables, zero stale or moved rows |
| Search and tooltip coverage | pass | 3,949 rows, 3,720 unique names, and every included container resolves once in its owner guide |
| UTF-8/mojibake scan | pass | Task-owned files contain no replacement characters or known mojibake prefixes |
| `git diff --check` | pass | No whitespace errors |

## Acceptance Report

- **Items added:** 41 — 19 vendor containers, 21 drop-owned containers, and one quest-reward container
- **Items excluded:** 82 — 60 non-auctionable, 12 deprecated/test, and 10 technically tradeable records with no verified acquisition route
- **Existing coverage verified:** 52 crafted containers already present once in their profession guides
- **Bands changed:** 41 new canonical listings; zero existing container price bands changed
- **Confidence distribution:** 19 deterministic vendor-cost listings; 22 fallback capacity-cohort starter estimates
- **Large changes reviewed:** not applicable to new rows; no existing Target moved
- **Comparison requests and final failures:** 132 requests; zero final failures
- **Search/index result:** 3,949 guide rows and 3,720 unique item names; all 93 included containers resolve to one canonical owner guide with a tooltip ID
- **Local or live status:** live; current public desktop/mobile verification passed
- **Unrelated worktree changes left untouched:** yes

## Publication Record

Complete only after explicit authorization.

- **Commits:** `e388667` (container release) and `0d99cac` (canonical scope correction)
- **Push target:** `origin/main`
- **Ahead/behind:** `0 0` after the final release push
- **Pages deployment:** pass for `0d99cac`
- **Public smoke result:** pass — 93 collection rows plus desktop/mobile filters, sorting, tooltips, owner links, and all AH guide views
- **Live URL:** `https://leblackstock.github.io/wotlk-server-guides/guides/bags-containers-ah-guide.html`

## Collection View Follow-up — 2026-08-08

- **Status:** live — published and publicly verified 2026-08-08
- **Generated page:** `guides/bags-containers-ah-guide.html`
- **Canonical renderer:** `scripts/render-ah-container-collection.py`
- **Canonical inputs:** The existing container audit plus crafted, vendor, drop/quest, and guide-manifest owners; the collection does not own a second price record.
- **Coverage:** All 93 included containers: 48 general bags, 27 profession bags, and 18 quivers or ammo pouches.
- **Filters:** Name, category, exact contents, source, expansion, and minimum slot capacity.
- **Sorts:** Slot capacity, Target high-to-low, Target low-to-high, and item name.
- **Price display:** Quick / exact vendor cost, Target, and High where the canonical owner provides it. Vendor rows intentionally have no High band.
- **Navigation:** A generated `Bags` shortcut appears in both `index.html` and `auction-house.html`.
- **Owner links:** Every item name and Canonical guide link returns to the one profession or drop guide that owns the price and full note.
- **Tooltip behavior:** All item names retain WotLK item mouseovers without replacing their owner-guide links.
- **Validation:** Renderer `--check`, 93-row canonical test, and desktop/mobile filters, sorting, tooltips, links, and overflow checks passed.
