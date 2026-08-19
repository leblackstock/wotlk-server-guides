# AH Item Addition Work Order — Primal Nether Hellscream repricing

- **Date:** 2026-08-19
- **Status:** published
- **Requested scope:** individual existing-item correction
- **Market type:** shared material
- **Target guide and section:** Mining & Smithing — Metal-adjacent smithing reagents; Cross-Profession Materials — Outland premium cross-profession mats; Blacksmithing Materials — shared Outland material row
- **Profession plan or evidence-status owner:** `data/ah-gathering-material-price-evidence.json` and `docs/ah-gathering-material-pricing-review.md`
- **Publishing authorized:** yes — user authorized live publication on 2026-08-19

## Requested Items

| Item ID | Canonical name | Intended buyer/use | Price basis | Group reason |
|---:|---|---|---|---|
| 23572 | Primal Nether | Buyers making legacy TBC Blacksmithing, Leatherworking, and Tailoring crafts | Per item | Independent server-specific supply correction |

## Gate A — Identity and Eligibility

| Item ID | Quality | Binding | Duration/flags | Max stack | Profession/skill | Auctionable | Decision |
|---:|---|---|---|---:|---|---|---|
| 23572 | Rare | None (`bonding=0`) | Permanent; `flags=0` | 20 | None to trade; legacy profession reagent | Yes | Retain and reprice |

- **Pinned item-template source and commit:** AzerothCore WotLK `item_template` at `e0fe11ba46b885a01e4a4038001e0055822cc7ba`
- **Vendor stock/restock, if any:** Not a vendor purchase; exact vendor liquidation value is 1g 60s per item.
- **Recipe/spell and guaranteed output, if any:** Not crafted in the canonical catalog; used by 57 audited dependent recipes.
- **Quest or gear-use facts, if any:** Hellscream-specific acquisition rule supplied by the user: level-80 upscaled TBC heroics award Primal Nether instead of Frozen Orb.
- **Restricted buyer section required:** No. The item is tradeable and buyers span several professions.
- **Exclusions and reasons:** None.

## Duplicate and Dependency Audit

| Item ID | Existing guide/data locations | Existing Q / T / H | Canonical owner | Downstream crafts/rows |
|---:|---|---|---|---|
| 23572 | Three guide rows; baseline; gathering evidence; eligibility audit | 4g / 6g / 10g | `data/ah-price-baselines.json` | 57 audited recipes plus search/index occurrences |

The gathering reviewer inventories the Mining & Smithing and Cross-Profession rows. The Blacksmithing Materials occurrence is a shared downstream row and must remain price-consistent.

## Gate B — Evidence

### Completed Hellscream sales

| Item ID | Units | Auctions | Buyers | UTC days | Price range | Concentration | Gate |
|---:|---:|---:|---:|---:|---|---|---|
| 23572 | 0 | 0 | 0 | 0 | — | — | fallback |

- **Known-account and invalid-transaction exclusions:** BeanCounter has no completed Primal Nether buyout to qualify. It records six failed or expired single-unit auctions between 5g 94s and 6g 9s 99c. Posting records without a completed outcome are not counted as sales.

### Current listings — diagnostic only

| Item ID | Independent sellers | Units | Largest seller | User/friends share | Posting implication |
|---:|---:|---:|---:|---:|---|
| 23572 | 2 | 18 | 94.4% | Unknown | Excess supply; post singles only and do not treat the 5g 98s wall as value |

- **Snapshot:** 2026-08-18 Horde scan. All 18 listings were single items at 5g 98s 40c. Auctioneer's 14-day statistic recorded 63 observed units with averages near 5g 99s, but this is listing history rather than realized-sale evidence.
- **`used_to_set_prices`:** false

### Deterministic and external evidence

- **Exact vendor/conversion/acquisition anchor:** Exact vendor liquidation value is 1g 60s. The custom heroic reward is a repeatable supply path, but no measured drop yield or gold-per-hour study exists.
- **Fixed Hellscream cohort anchor:** None defensible for this custom reward mechanic.
- **External realms/factions covered:** Three realms and six faction observations are retained as supply context only.
- **Comparison retry result:** Existing saved comparison retained; no new fetch was required for this user-reviewed correction.
- **`external_gold_values_copied`:** false
- **Saved evidence file/report:** `data/ah-gathering-material-price-evidence.json` and `docs/ah-gathering-material-pricing-review.md`

## Gate C — Price Proposal and Review

| Item ID | Before Q / T / H | Proposed Q / T / H | Source type | Confidence | Target change | Reviewer decision |
|---:|---|---|---|---|---:|---|
| 23572 | 4g / 6g / 10g | 2g / 2g 50s / 3g 50s | documented-fallback | fallback | -58.33% | Accepted |

Manual large-change review: the item has a 1g 60s liquidation floor, repeatable level-80 byproduct acquisition, narrow legacy-craft demand, zero completed local sales, six failed auctions near 6g, two active sellers, and 94.4% concentration in one seller. The accepted band is deliberately labeled a price-discovery fallback. Qualifying completed Hellscream sales should replace it.

## Craftability Diagnostic

| Item ID | Exact recipe/yield | Quick floor | Target floor | High floor | Market below floor? | Guide warning |
|---:|---|---:|---:|---:|---|---|
| 23572 | Not crafted; heroic reward material | 1g 60s vendor floor | 1g 60s vendor floor | 1g 60s vendor floor | No | Post singles; do not infer demand from the concentrated 6g listing wall |

The material is consumed by 57 audited profession recipes. Their saved craftability diagnostics must be regenerated after this baseline change.

## Canonical Implementation

- **Canonical source files:** `data/ah-price-baselines.json`
- **Evidence/report files:** `data/ah-gathering-material-price-evidence.json`, `docs/ah-gathering-material-pricing-review.md`, and this work order
- **Renderer/reviewer files:** `scripts/review-ah-gathering-material-prices.py`, `scripts/apply-ah-price-baselines.py`, and the normal dependent craft/render chain
- **Generated guides/assets:** Three guide rows, `assets/ah-search-index.js`, dependent craft-floor evidence/reports, and vendor recommendations regenerated.
- **Profession plan/status log updated:** This work order is the item-specific evidence log; no profession expansion is being opened.
- **Changed guide footer date:** 2026-08-19 on all three changed guide pages.

The dependency refresh changed 57 recipes that directly consume Primal Nether. It also corrected one pre-existing stale Knothide Quiver reagent-floor diagnostic from the current canonical ingredient baselines; that item's market band did not change.

## Guide Content Check

- [x] Exact name and pinned rarity color
- [x] Per-item or stack price basis is explicit
- [x] Quick, Target, and High are ordered
- [x] Buyer/use/demand note is item-specific
- [x] Profession restriction is in a dedicated section when required (not required)
- [x] Stack recommendation is valid or omitted for non-stackable item
- [x] WotLK item tooltip resolves
- [x] Recipe and materials mouseover link exists when applicable (not applicable to this raw material row)
- [x] Shared methodology is referenced once with `*`, not repeated per row
- [x] Published price uses no more than two currency units

## Validation Record

| Command/check | Result | Notes |
|---|---|---|
| Gathering/material reviewer `--check` | passed | Both Phase 1A and Phase 1B evidence are current. |
| Canonical renderer checks | passed | Shared baseline, crafted-floor, dropped-row, ordering, UX, container, search, tooltip, and eligibility checks passed. |
| AH Python regression suite | passed | Full AH Python test suite passed. |
| `npm test` | passed | JavaScript tests passed with updated snapshots and counts. |
| Local desktop/mobile AH smoke | passed | Primal Nether Q / T / H, stack, demand, and server-mechanic note verified at both viewports. |
| Auction eligibility | passed | 3,920 auctionable IDs plus one cost-only item validated. |
| Duplicate price/rarity/stack consistency | passed | All three Primal Nether rows agree. |
| Section price ordering | passed | 19 guides and 347 tables current after regeneration. |
| Search and tooltip coverage | passed | 4,088 search entries; Primal Nether is current and receives the expected Vendor chip. |
| UTF-8/mojibake scan | passed | All 32 changed/new task files decode as strict UTF-8 with no known mojibake markers. |
| `git diff --check` | passed | No whitespace errors. |

## Acceptance Report

- **Items added:** None; existing item corrected.
- **Items excluded:** None.
- **Bands changed:** Primal Nether from 4g / 6g / 10g to 2g / 2g 50s / 3g 50s.
- **Confidence distribution:** One fallback-confidence correction.
- **Large changes reviewed:** Primal Nether Target reduced 58.33% after the explicit review above.
- **Comparison requests and final failures:** No new comparison request; existing saved coverage retained and did not set nominal gold.
- **Search/index result:** Complete; 4,088 entries and 486 Vendor-chip recommendations after regeneration.
- **Local or live status:** Live on GitHub Pages; public desktop/mobile smoke passed.
- **Unrelated worktree changes left untouched:** `docs/weakauras-combat-cursor-flame-trail.md`

## Publication Record

Complete only after explicit authorization.

- **Content commit:** `f6af04a` (`fix: reprice Primal Nether for Hellscream`)
- **Push target:** `origin/main`
- **Ahead/behind:** `0 / 0` after the content push
- **Pages deployment:** run `32226776813` succeeded for `f6af04a` on 2026-08-19
- **Repository validation:** run `32226778023` succeeded for `f6af04a` on 2026-08-19
- **Public smoke result:** pass — the AH Hub and all twelve crafted-guide views passed desktop/mobile smoke, including the new Primal Nether price and server-mechanic assertions
- **Live URLs:** `https://leblackstock.github.io/wotlk-server-guides/guides/mining-smithing-ah-price-guide.html`, `https://leblackstock.github.io/wotlk-server-guides/guides/cross-profession-materials-ah-price-guide.html`, and `https://leblackstock.github.io/wotlk-server-guides/guides/blacksmithing-materials-ah-price-guide.html`
