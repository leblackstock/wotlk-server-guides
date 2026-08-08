# AH Item Addition Work Order — <short title>

- **Date:** YYYY-MM-DD
- **Status:** planned | in progress | complete locally | published
- **Requested scope:** individual | coupled batch
- **Market type:** material | vendor | crafted | turn-in | recipe | Level-80 BoE | world drop
- **Target guide and section:**
- **Profession plan or evidence-status owner:**
- **Publishing authorized:** no

## Requested Items

| Item ID | Canonical name | Intended buyer/use | Price basis | Group reason |
|---:|---|---|---|---|
| 0 | Example |  | per item | independent |

## Gate A — Identity and Eligibility

| Item ID | Quality | Binding | Duration/flags | Max stack | Profession/skill | Auctionable | Decision |
|---:|---|---|---|---:|---|---|---|
| 0 |  |  |  |  |  |  |  |

- **Pinned item-template source and commit:**
- **Vendor stock/restock, if any:**
- **Recipe/spell and guaranteed output, if any:**
- **Quest or gear-use facts, if any:**
- **Restricted buyer section required:**
- **Exclusions and reasons:**

## Duplicate and Dependency Audit

| Item ID | Existing guide/data locations | Existing Q / T / H | Canonical owner | Downstream crafts/rows |
|---:|---|---|---|---|
| 0 |  |  |  |  |

## Gate B — Evidence

### Completed Hellscream sales

| Item ID | Units | Auctions | Buyers | UTC days | Price range | Concentration | Gate |
|---:|---:|---:|---:|---:|---|---|---|
| 0 | 0 | 0 | 0 | 0 | — | — | fallback |

- **Known-account and invalid-transaction exclusions:**

### Current listings — diagnostic only

| Item ID | Independent sellers | Units | Largest seller | User/friends share | Posting implication |
|---:|---:|---:|---:|---:|---|
| 0 |  |  |  |  |  |

- **`used_to_set_prices`:** false

### Deterministic and external evidence

- **Exact vendor/conversion/acquisition anchor:**
- **Fixed Hellscream cohort anchor:**
- **External realms/factions covered:**
- **Comparison retry result:** initial + 2s + 5s + 10s
- **`external_gold_values_copied`:** false
- **Saved evidence file/report:**

## Gate C — Price Proposal and Review

| Item ID | Before Q / T / H | Proposed Q / T / H | Source type | Confidence | Target change | Reviewer decision |
|---:|---|---|---|---|---:|---|
| 0 | — |  | documented-fallback | fallback | — | pending |

For every Target change greater than 50%, record the explicit acquisition,
buyer/use, exact-floor or item-fact, comparable-cohort, and coverage review.

## Craftability Diagnostic

| Item ID | Exact recipe/yield | Quick floor | Target floor | High floor | Market below floor? | Guide warning |
|---:|---|---:|---:|---:|---|---|
| 0 |  |  |  |  |  |  |

## Canonical Implementation

- **Canonical source files:**
- **Evidence/report files:**
- **Renderer/reviewer files:**
- **Generated guides/assets:**
- **Profession plan/status log updated:**
- **Changed guide footer date:**

## Guide Content Check

- [ ] Exact name and pinned rarity color
- [ ] Per-item or stack price basis is explicit
- [ ] Quick, Target, and High are ordered
- [ ] Buyer/use/demand note is item-specific
- [ ] Profession restriction is in a dedicated section when required
- [ ] Stack recommendation is valid or omitted for non-stackable item
- [ ] WotLK item tooltip resolves
- [ ] Recipe and materials mouseover link exists when applicable
- [ ] Shared methodology is referenced once with `*`, not repeated per row
- [ ] Published price uses no more than two currency units

## Validation Record

| Command/check | Result | Notes |
|---|---|---|
| Market-specific reviewer/catalog `--check` | pending |  |
| Canonical renderer checks | pending |  |
| AH Python regression suite | pending |  |
| `npm test` | pending |  |
| Local desktop/mobile AH smoke | pending |  |
| Auction eligibility | pending |  |
| Duplicate price/rarity/stack consistency | pending |  |
| Section price ordering | pending |  |
| Search and tooltip coverage | pending |  |
| UTF-8/mojibake scan | pending |  |
| `git diff --check` | pending |  |

## Acceptance Report

- **Items added:**
- **Items excluded:**
- **Bands changed:**
- **Confidence distribution:**
- **Large changes reviewed:**
- **Comparison requests and final failures:**
- **Search/index result:**
- **Local or live status:**
- **Unrelated worktree changes left untouched:**

## Publication Record

Complete only after explicit authorization.

- **Commit:**
- **Push target:**
- **Ahead/behind:**
- **Pages deployment:**
- **Public smoke result:**
- **Live URL:**
