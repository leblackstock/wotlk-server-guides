# AH Item Addition Work Order — Cooking stat and dual-recovery foods

- **Date:** 2026-08-10
- **Status:** complete and published — 2026-08-11
- **Requested scope:** coupled batch
- **Market type:** crafted
- **Target guide and section:** `guides/fishing-cooking-materials-ah-price-guide.html`; expansion-specific stat-food sections
- **Profession plan or evidence-status owner:** `docs/ah-profession-plans/cooking.md`
- **Publishing authorized:** yes — 2026-08-11

## Requested Items

| Item ID | Canonical name | Intended buyer/use | Price basis | Group reason |
|---:|---|---|---|---|
| 34759 | Smoked Rockfin | Northrend dual health-and-mana recovery | per item | dual recovery |
| 34760 | Grilled Bonescale | Northrend dual health-and-mana recovery | per item | dual recovery |
| 34761 | Sauteed Goby | Northrend dual health-and-mana recovery | per item | dual recovery |
| 45932 | Black Jelly | Northrend dual health-and-mana recovery | per item | dual recovery |
| 24105 | Roasted Moongraze Tenderloin | Outland leveling Stamina and Spirit food | per item | stat bonus |
| 27635 | Lynx Steak | Outland leveling Stamina and Spirit food | per item | stat bonus |
| 27636 | Bat Bites | Outland leveling Stamina and Spirit food | per item | stat bonus |
| 27651 | Buzzard Bites | Outland leveling Stamina and Spirit food | per item | stat bonus |
| 33053 | Hot Buttered Trout | Outland dual health-and-mana recovery | per item | dual recovery |
| 2682 | Cooked Crab Claw | Classic dual health-and-mana recovery | per item | dual recovery |

## Gate A — Identity and Eligibility

All ten items are already part of the audited 162-output Cooking catalog. Their
item IDs, common quality, tradeability, stack size, recipe spell, guaranteed
output, and effects are pinned in the existing Cooking item/recipe audit.

- **Pinned item-template source and commit:** Existing AzerothCore build-12340 item baseline recorded by the Cooking plan
- **Vendor stock/restock, if any:** Not applicable; these are crafted outputs
- **Recipe/spell and guaranteed output, if any:** `data/ah-crafted-recipe-audit.json`
- **Quest or gear-use facts, if any:** Not applicable
- **Restricted buyer section required:** No
- **Exclusions and reasons:** Pure health-only and pure mana-only recovery foods stay in recovery sections

## Duplicate and Dependency Audit

Each item already has one canonical catalog row, one Cooking recipe audit, one
evidence record, and one guide appearance. This correction moves the guide
appearance and evidence section label without adding duplicates or changing
ingredient dependencies.

## Gate B — Evidence

- **Completed Hellscream sales:** No qualifying completed Cooking sales were available in the saved Phase 2 review
- **Current listings used to set prices:** false
- **Fixed Hellscream cohort anchor:** Preserved from the completed Cooking Evidence Pricing review
- **External realms/factions covered:** Icecrown, Lordaeron, and Onyxia; both factions where saved
- **Comparison retry result:** All 972 saved comparison requests resolved
- **`external_gold_values_copied`:** false
- **Saved evidence file/report:** `data/ah-cooking-price-evidence.json`; `docs/ah-cooking-pricing-review.md`

## Gate C — Price Proposal and Review

No price proposal is required. The saved Evidence Pricing bands, demand labels,
recipe floors, source observations, and confidence decisions remain unchanged.
Only section ownership and explanatory copy change.

## Canonical Implementation

- **Canonical source files:** `data/ah-crafted-sections.json`
- **Evidence/report files:** `data/ah-cooking-price-evidence.json`; `docs/ah-cooking-pricing-review.md`
- **Renderer/reviewer files:** Existing shared AH renderers and `scripts/review-ah-cooking-prices.py`
- **Generated guides/assets:** `guides/fishing-cooking-materials-ah-price-guide.html`; AH search and tooltip assets
- **Profession plan/status log updated:** complete locally
- **Changed guide footer date:** 2026-08-11

## Validation Record

| Command/check | Result | Notes |
|---|---|---|
| Market-specific reviewer/catalog `--check` | passed | 162 evidence decisions current |
| Canonical renderer checks | passed | Shared sections and guide UX current |
| AH Python regression suite | passed | All 40 passed on 2026-08-10; all 39 applicable release-day tests passed on 2026-08-11, with only the untouched collectibles page's date-dynamic renderer excluded |
| `npm test` | passed | Full site suite passed on 2026-08-11 |
| Local desktop/mobile AH smoke | passed | Local and public checks at 1280 × 800 and 390 × 844; no page overflow or console errors |
| Auction eligibility | passed | 3,920 unique item IDs valid; one existing cost-only exception |
| Duplicate price/rarity/stack consistency | passed | Cross-guide consistency test passed |
| Section price ordering | passed | All 347 priced tables valid |
| Search and tooltip coverage | passed | 4,088 search entries; tooltip assets current |
| UTF-8/mojibake scan | passed | Changed files clean |
| `git diff --check` | passed | No whitespace errors |

## Acceptance Report

- **Items added:** 0 new catalog rows; 10 existing qualifying rows promoted into stat-food sections
- **Items excluded:** Health-only and mana-only foods remain recovery-only
- **Bands changed:** 0
- **Confidence distribution:** Preserved from saved Cooking Evidence Pricing
- **Large changes reviewed:** Not applicable; no price changes
- **Comparison requests and final failures:** 972 saved requests; 0 final failures
- **Search/index result:** All 10 promoted rows remain indexed; 4,088 total AH search entries
- **Local or live status:** published and publicly verified
- **Unrelated worktree changes left untouched:** yes

## Publication Record

- **Commit:** `670de1c` (`feat: group useful cooked foods`)
- **Push target:** `origin/main`
- **Ahead/behind:** `0 / 0` after the content push
- **Pages deployment:** run `31457583668` succeeded for `670de1c` on 2026-08-11
- **Public smoke result:** pass — all three corrected headings and all ten promoted rows are live; desktop and mobile have no page overflow or console errors
- **Live URL:** `https://leblackstock.github.io/wotlk-server-guides/guides/fishing-cooking-materials-ah-price-guide.html`
