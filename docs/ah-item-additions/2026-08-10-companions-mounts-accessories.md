# AH Item Addition Work Order — Companions, Mounts & Accessories

- **Date:** 2026-08-10
- **Status:** complete locally — promotional/TCG availability correction not published
- **Requested scope:** coupled batch
- **Market type:** vendor | crafted | quest/reward | world drop | seasonal | promotional
- **Target guide and section:** `guides/companions-mounts-accessories-ah-price-guide.html`; separate limited vendor, unlimited vendor, token vendor, drop, crafted, quest/reward, accessory, and per-event seasonal sections
- **Profession plan or evidence-status owner:** `docs/ah-evidence-pricing-library-plan.md`; Engineering and Tailoring addenda for delegated crafted rows
- **Publishing authorized:** no

## Requested Items

The complete exact-name inventory is generated in `data/ah-collectible-audit.json`. The coupled batch starts from these pinned item IDs:

| Market group | Exact item IDs | Intended buyer/use | Price basis | Group reason |
|---|---|---|---|---|
| Unlimited coin-vendor companions | 8485, 8486, 8487, 8488, 8490, 8495, 8496, 8497, 8500, 8501, 10360, 10361, 10392, 10393, 10394, 11023, 11026, 29363, 29364, 29901, 29902, 29903, 29904, 29956, 29957, 29958, 44822, 46398, 48120 | Companion collectors; faction/travel convenience | per item | Exact vendor cost and unlimited supply require one shared arbitrage rule |
| Limited coin-vendor companions | 8489, 11027 | Companion collectors | per item | Stock and restock create a distinct convenience market |
| Token/reputation companions | 44965, 44970, 44971, 44973, 44974, 44980, 44982, 44984, 45002, 45606, 46820, 46821 | Argent Tournament collectors | per item | Forty Champion's Seals are an acquisition fact, not a coin-vendor floor |
| Farmed companion drops | 8491, 8492, 8494, 8498, 8499, 10822, 20769, 29960, 34535, 39896, 39898, 39899, 44721, 48112, 48114, 48116, 48118, 48122, 48124, 48126 | Companion collectors | per item | Loot rates and source access form comparable scarcity cohorts |
| Quest/reward companions | 10398, 22781 | Companion collectors | per item | One-time or quest-gated acquisition |
| Crafted companions and mounts | 4401, 11825, 11826, 15996, 21277, 34060, 34061, 41508, 44413, 44554 | Collectors; Engineer- or Tailor-restricted mount users where stated | per item | Exact recipe floors and shared collectible demand must remain coupled |
| Promotional and TCG mounts excluded | 49282, 49283, 49284, 49285, 49286, 49290, 54068, 54069 | Not listed | none | No direct Hellscream acquisition evidence is saved; a generic base-database route is not proof that a reward is enabled on this server |
| Shadowmourne quest rewards and accessories | 52200, 52201, 52251, 52252, 52253 | Mount, tabard, toy, and roleplay collectors | per item | One shared quest source and slow-sale prestige market |
| Winter Veil | 17194, 17202, 17303, 17304, 17307, 17405, 21213, 21301, 21305, 21308, 21309 | Seasonal collectors and novelty buyers | per item or valid small stack | One event calendar and gift/vendor supply window |
| Lunar Festival | 21557, 21558, 21559, 21561, 21562, 21571, 21574, 21576, 21589, 21590, 21592, 21593, 21595, 21713, 21747 | Firework and roleplay buyers | per item or valid small stack | One event-vendor and event-loot market |
| Love is in the Air | 22200, 22218, 22276, 22277, 22278, 22279, 22280, 22281, 22282, 34258, 49856, 49857, 49858, 49859, 49860, 49861, 50163 | Cosmetic, roleplay, and novelty buyers | per item or valid small stack | Event currency, gift boxes, and cosmetic rewards share one availability window |
| Noblegarden | 6833, 6835, 19028 | Cosmetic and achievement buyers | per item | Egg drops and Noblegarden Chocolate costs form one event market |
| Midsummer Fire Festival | 34599, 34850 | Novelty and event buyers | per item or valid small stack | Event token/quest and coin-vendor routes |

## Gate A — Identity and Eligibility

- **Pinned item-template source and commit:** AzerothCore WotLK `item_template` at `e0fe11ba46b885a01e4a4038001e0055822cc7ba`
- **Vendor stock/restock, if any:** White Kitten is stock 1 with a 1-hour restock; Wood Frog is stock 1 with a 30-minute restock. Unlimited and extended-cost vendors remain separate.
- **Recipe/spell and guaranteed output, if any:** Ten one-item Engineering/Tailoring recipes are pinned in the collectible audit and delegated to `data/ah-crafted-sections.json`.
- **Quest or gear-use facts, if any:** Shadowmourne sealed-chest rewards are Bind on Use/Equip and tradeable before use; crafted Flying Machine and Flying Carpet rows carry their profession-use restrictions.
- **Restricted buyer section required:** yes — Engineering and Tailoring mount requirements are explicit.
- **Exclusions and reasons:** ordinary racial/reputation mounts, most event pets/mounts, pet toys, and temporary brooms are BoP, duration-limited, or otherwise auction-ineligible. All eight promotional/TCG mounts in scope remain excluded until direct Hellscream acquisition is verified; a generic base-database loot route is insufficient.

## Duplicate and Dependency Audit

| Item or family | Existing guide/data locations | Canonical owner | Decision |
|---|---|---|---|
| Holiday Spices (17194) | Fishing & Cooking guide; shared vendor data/search/tooltip | existing vendor row | Render as a linked overlap with the same band; do not create a second baseline |
| Ten crafted collectibles | Missing finished rows; related schematics/components already appear in Engineering, Tailoring, or Recipe Drops | crafted catalog and exact recipe audit | Add canonical crafted rows, then render the collectibles guide from those owners |
| All other included IDs | No exact-name current AH guide row found | new collectible catalog | New canonical records |

## Gate B — Evidence

- **Known-account and invalid-transaction exclusions:** use the existing privacy-preserving BeanCounter importer; current scan asks remain diagnostic only.
- **`used_to_set_prices`:** false
- **Exact vendor/conversion/acquisition anchor:** coin cost, stock/restock, 40 Champion's Seals, Noblegarden Chocolate/Love Token/Burning Blossom costs, exact recipe reagents, or pinned loot/quest path as applicable.
- **Fixed Hellscream cohort anchor:** one sparse Wood Frog sale plus reviewed cosmetic/crafted comparables and documented low-pop collectible starter anchors.
- **External realms/factions covered:** Icecrown, Lordaeron, and Onyxia; both factions.
- **Comparison retry result:** 336 initial requests; all resolved on the initial
  pass, so the saved 2s + 5s + 10s retry ladder had zero final failures
- **`external_gold_values_copied`:** false
- **Saved evidence file/report:** `data/ah-collectible-price-evidence.json`; `docs/ah-collectible-pricing-review.md`

## Gate C — Price Proposal and Review

- Vendor cost is a deterministic floor, not proof of the resale premium.
- Qualified completed Hellscream sales take priority. Sparse sales are shrunk toward a fixed cohort.
- External observations may set relative rank only. All unsupported opening prices remain `fallback` confidence.
- Every proposed Target is new; all 128 decisions are recorded in the saved
  evidence report and were reviewed before apply.

## Canonical Implementation

- **Canonical source files:** `data/ah-collectible-sections.json`, plus ten
  delegated crafts in `data/ah-crafted-sections.json`, one shared vendor row in
  `data/ah-vendor-sections.json`, and the Big Iron Bomb dependency in
  `data/ah-price-baselines.json`
- **Evidence/report files:** `data/ah-collectible-audit.json`,
  `data/ah-collectible-price-evidence.json`, and
  `docs/ah-collectible-pricing-review.md`
- **Renderer/reviewer files:** `scripts/audit-ah-collectibles.py`,
  `scripts/review-ah-collectible-prices.py`, and
  `scripts/render-ah-collectibles.py`
- **Generated guides/assets:** the new guide, icon, 19-guide manifest/hub,
  navigation data, 4,089-row search index, and tooltip/eligibility snapshots
- **Profession plan/status log updated:** yes — Engineering, Tailoring, and the
  library-wide Evidence Pricing status record
- **Changed guide footer date:** 2026-08-10 on the new guide and the two edited
  profession guides only

## Guide Content Check

- [x] Exact name and pinned rarity color
- [x] Per-item or stack price basis is explicit
- [x] Quick, Target, and High are ordered
- [x] Buyer/use/demand note is item-specific
- [x] Profession restriction is in a dedicated section when required
- [x] Stack recommendation is valid or omitted for non-stackable item
- [x] WotLK item tooltip resolves
- [x] Recipe and materials mouseover link exists when applicable
- [x] Shared methodology is referenced once with `*`, not repeated per row
- [x] Displayed prices use no more than two currency units

## Validation Record

| Command/check | Result | Notes |
|---|---|---|
| Collectible audit/reviewer `--check` | pass | 128 eligible items; 20 sections; evidence, applied data, and guide current |
| Canonical renderer checks | pass | Shared sections, profession-use blocks, guide UX, search, and tooltip assets current |
| AH Python regression suite | pass | All 40 `tests/ah-*.test.py` files passed |
| `npm test` | pass | Node, guide-banner, fresh-80 workflow, and guide-audience suites passed |
| Local desktop/mobile AH smoke | pass | Hub card, search, all 20 sections, 128 rows, six empty seasons, and overflow checked |
| Auction eligibility | pass | 3,921 unique IDs; 128 collectible IDs; unused Bind on Use accepted; one explicit cost-only exception |
| Duplicate price/rarity/stack consistency | pass | Ten crafted owners and Holiday Spices synchronize; all exact collectible identities pass |
| Section price ordering | pass | 19 guides; 347 priced tables; 286 price-ordered and 61 fixed-order tables |
| Search and tooltip coverage | pass | 4,089 search rows; all 128 collectible names resolve to pinned item IDs |
| UTF-8/mojibake scan | pass | No mojibake found in the files changed for this work order |
| `git diff --check` | pass | No whitespace errors in the working-tree diff |

## Acceptance Report

- **Items added:** 128 collectible-guide rows; ten also added to their canonical
  Engineering/Tailoring catalogs and Holiday Spices remains vendor-owned
- **Items excluded:** nine pinned auction-ineligible examples plus all eight
  promotional/TCG mounts pending direct Hellscream availability evidence
- **Bands changed:** 128 collectible bands; no active listing price was
  imported and the existing Holiday Spices Target remained synchronized at 1s
- **Confidence distribution:** 44 high exact unlimited-vendor decisions, 83
  fallback estimates, and one low-confidence sparse-sale decision
- **Large changes reviewed:** zero prior-band comparisons; all 128 proposals
  carry an explicit `accept` decision
- **Comparison requests and final failures:** 336 initial / 0 final failures
- **Search/index result:** 4,089 rows across 19 guides, including all 128
  collectible rows
- **Local or live status:** local only; publishing not authorized
- **Unrelated worktree changes left untouched:** existing addon, guide-audience, and spec-guide work remains unstaged

## Publication Record

Complete only after explicit authorization.

- **Commit:** not authorized
- **Push target:** not authorized
- **Ahead/behind:** not checked for publication
- **Pages deployment:** not authorized
- **Public smoke result:** not run
- **Live URL:** not published
