# AH Item Addition Workflow

Use this workflow whenever adding one item or a group of items to any Auction
House guide. It is the operational companion to
[Evidence Pricing](ah-pricing-methodology.md) and the profession plans under
[`docs/ah-profession-plans/`](ah-profession-plans/README.md).

The goal is not merely to make a row appear. A complete addition has pinned
item identity, auction eligibility, buyer-use classification, non-circular
price evidence, an explicit confidence level, canonical data, generated guide
output, search and tooltip coverage, ordering, tests, and a separate publishing
decision.

## Non-Negotiable Rules

- Active listings show competition only and never set or raise guide prices.
  Hellscream asks may still describe availability, concentration, and posting
  conditions.
- The guide's own suggested prices cannot become evidence when they appear in a
  later scan.
- Update canonical data and its renderer. Do not hand-edit a generated table
  unless inspection proves that the HTML section is intentionally canonical.
- Every priced item must resolve to one exact WotLK 3.3.5 item ID.
- BoP, nontradeable, self-only, conjured, temporary, and invalid outputs do not
  belong in AH listings.
- `quick <= target <= high`. Record whether the price is per item, per craft,
  or for a stated stack.
- Current competitor prices may change the posting decision, stack size, or
  timing—not the saved baseline.
- A price estimate below its exact craft floor is allowed only when the market
  estimate and craftability diagnostic remain separate and the guide warns the
  player not to craft from purchased inputs.
- Publishing is a separate step and requires explicit user authorization.

## 1. Open a Work Order

Copy [`docs/ah-item-additions/_template.md`](ah-item-additions/_template.md) to
`docs/ah-item-additions/YYYY-MM-DD-<short-slug>.md` and fill it in while the
work advances.

Record before editing:

- requested item names and exact item IDs;
- target guide, section, and intended buyer;
- market type: material, vendor input, crafted output, turn-in, recipe or
  pattern, Level-80 BoE, or sought-after world drop;
- whether the request is one independent item or a coupled batch;
- every current guide location and baseline/evidence record for the same item;
- current Git status so unrelated worktree changes remain untouched.

### Choose the correct batch boundary

Use an **individual work order** when the item has an independent acquisition
path, evidence set, and buyer market, and adding it cannot change a shared
conversion, reagent baseline, price basis, or comparable cohort.

Use a **group work order** when any of these are true:

- the items share one recipe family, random output, reversible conversion, or
  batch yield;
- one input-baseline change can alter several craft floors;
- the rows represent one progression whose fixed order matters;
- the items need one shared buyer-restriction section;
- external relative ranks are meaningful only inside the same expansion,
  quality, item-level, slot, source, or use cohort;
- a grouped guide label must be resolved into multiple exact item IDs.

Do not split a coupled market merely to make the first item easier to price. Do
not expand an independent request into an unrelated profession-wide refresh.

## 2. Gate A — Identity, Tradeability, and Buyer Use

Pin each item against the saved AzerothCore WotLK item template or a refreshed
snapshot from the same source. Record:

- exact item ID and canonical name;
- quality ID and displayed rarity color;
- bonding, flags, duration, and auction eligibility;
- maximum stack and whether the item is non-stackable;
- required profession and skill, if any;
- vendor buy/sell price, limited stock, and restock time, when applicable;
- spell or recipe ID, guaranteed output quantity, and learned output for a
  crafted item or recipe;
- quest quantity, repeatability, faction, event, standing, or level limits for
  a turn-in;
- item level, required level, slot, stats, sockets, effects, and source cohort
  for gear.

Then:

1. Search every AH guide, canonical data file, search index, and tooltip map for
   the exact name and item ID.
2. Reconcile duplicate rows to one per-unit price band unless a documented
   stack or form difference requires separate records.
3. Check `data/ah-profession-use-audit.json`. Hard profession requirements go
   in a dedicated restricted section. Practical tools usable by anyone stay in
   the general market with their real buyer described.
4. Give a non-stackable item no published Stack recommendation. Otherwise,
   every suggested quantity must be at or below the pinned maximum stack and
   should reflect a real craft, quest, raid, or consumption quantity.
5. Stop the addition if the item cannot be auctioned. Record the exclusion and
   reason in the work order instead of inventing a price.

Validate the saved eligibility snapshot after canonical edits:

```powershell
python scripts/audit-ah-auction-eligibility.py --check
```

## 3. Gate B — Establish Evidence Pricing

### 3.1 Start with the existing baseline

Inspect `data/ah-price-baselines.json` and the matching market evidence file.
For a new item, identify the independent evidence or fixed Hellscream cohort
that will anchor it before adding a guide row. For an existing duplicate, use
the strongest already-reviewed record instead of creating a second price.

Never silently replace stronger saved coverage with a newer but weaker fetch.

### 3.2 Rank accepted evidence correctly

Use evidence in this order:

1. Exact unlimited-vendor cost or deterministic conversion with independently
   anchored inputs (`high`).
2. Qualified completed Hellscream sales (`medium`).
3. Sparse completed sales blended toward a fixed fallback (`low`).
4. A documented acquisition fallback or approved low-pop starter estimate
   (`fallback`).

For stackable items, `medium` requires at least 20 units, four completed
auctions, two buyers, and two UTC sale days without buyer concentration. For a
non-stackable BoE, `medium` requires four completed buyouts, two buyers, and two
UTC sale days with no buyer controlling more than 50% of units.

Exclude guild/friend transfers, test purchases, bids, cancellations, and
expired listings. Record units, completed auctions, buyers, days, price range,
and concentration in the work order.

### 3.3 Keep active listings diagnostic-only

Current listings may record:

- independent seller count;
- listed units and stack sizes;
- seller concentration after known-account exclusions;
- whether posting now would create excess supply.

Set `used_to_set_prices: false`. Do not copy the lowest ask, median, or empty-AH
premium into a baseline. The market is especially unsuitable for valuation
when the user and known friends control at least 30% of units, one seller
controls at least 25%, fewer than three independent sellers remain, or only one
snapshot exists.

### 3.4 Use external comparisons only for relative rank

When the approved low-pop model is necessary:

1. Keep the Hellscream gold scale fixed with a recorded local cohort anchor.
2. Normalize external realms with saved shared-commodity economy scales.
3. Use the result only to rank the item inside a comparable expansion, quality,
   item-level, slot, source, and buyer cohort.
4. Never copy raw or normalized external gold into the Hellscream band.
5. Keep the decision at `fallback` confidence.

After the initial comparison batch, preserve successful responses and retry
only failures after 2, 5, and 10 seconds. A resolved request with no listing is
absence evidence, not a host failure. Record final failure only after all three
waited retries fail.

### 3.5 Separate proposal, review, and apply

Every evidence record must save:

- prior Quick / Target / High band;
- proposed band and per-item or stack basis;
- source type and confidence;
- completed-sale counts, buyers, days, and concentration;
- comparison coverage and `external_gold_values_copied: false`;
- current-listing diagnostic with `used_to_set_prices: false`;
- reviewer decision and reason;
- exact evidence/report reference written into the baseline.

Do not apply a proposal until the report is readable and the work order records
the review decision. A Target move greater than 50% needs an explicit manual
review:

- materials and crafts: acquisition tier, exact floor, output quantity, buyer,
  use, comparable cohort, and comparison coverage;
- recipes: profession, required skill, learned-output market, source, vendor
  competition, and coverage;
- gear: slot, stats/sockets/effects, required level, buyer, source cohort, and
  coverage.

## 4. Gate C — Craft Cost and Deterministic Floors

For crafted items, verify the exact 3.3.5 recipe before pricing the output:

- every reagent ID and quantity;
- minimum guaranteed output or displayed stack yield;
- compatible vellum for enchant scrolls;
- vendor and BoP overrides;
- reversible conversion parity;
- the saved Quick, Target, and High input baseline for each band.

Calculate same-band floors from frozen inputs. Do not use the user's current AH
purchase price as a new ingredient baseline. If an input is missing, add and
review that input first or save an explicit fallback; never cost it as zero.

After any input-baseline or recipe change, regenerate dependent floors:

```powershell
python scripts/audit-ah-crafted-prices.py --write
python scripts/audit-ah-crafted-prices.py --check
```

The market band answers “what is a useful opening sale estimate?” The recipe
floor answers “what does this cost to reproduce from saved inputs?” Keep both.

## 5. Gate D — Choose the Canonical Owner

| Market type | Canonical owner | Evidence/review owner | Primary renderer or audit |
|---|---|---|---|
| Raw, gathered, converted, or shared material | `data/ah-price-baselines.json`; existing non-generated material section after ownership inspection | `data/ah-gathering-material-price-evidence.json` or matching saved material evidence | `scripts/apply-ah-price-baselines.py`, then dependent craft audit |
| Vendor or convenience input | `data/ah-vendor-sections.json` plus baseline/override record | Exact vendor source in baseline or recipe audit | `scripts/render-ah-shared-sections.py` |
| Profession-crafted output | `data/ah-crafted-sections.json` | Matching `data/ah-<market>-price-evidence.json` and review report | Matching `scripts/review-ah-<market>-prices.py`, then shared renderer |
| Turn-in or quest item | `TURN_IN_SECTIONS` and related overrides in `scripts/audit-ah-phase3-catalogs.py`; generated `data/ah-turn-in-catalog.json` | `data/ah-turn-in-price-evidence.json` and report | Phase 3 catalog audit, reviewer, and static-guide renderer |
| Recipe or pattern | The exact recipe-guide row selection consumed by `scripts/audit-ah-phase3-catalogs.py`; generated `data/ah-recipe-drop-audit.json` | `data/ah-recipe-drop-price-evidence.json` and report | Phase 3 catalog audit, reviewer, and static-guide renderer |
| Level-80 BoE or sought-after world drop | `data/ah-dropped-gear.json` | Dropped-gear evidence, cross-server diagnostics, and review report | Comparison refresher, estimator, and dropped-gear renderer |
| Guide title, description, or navigation | `data/ah-guides.json` | Work-order decision | `scripts/render-ah-guide-ux.py` |

Before editing an HTML row, search for its generator and marker attributes. If
a renderer owns it, change the source and renderer. If no renderer owns a
legacy material section, record that ownership finding in the work order before
editing the guide.

## 6. Gate E — Write Useful Guide Content

Each new row must have:

- exact canonical item name colored by pinned rarity;
- Quick, Target, and High values with the correct per-item or stack basis;
- demand supported by buyer/use evidence, not listing volume alone;
- a real stack recommendation or no Stack display for non-stackable items;
- an item-specific note describing buyer, use, restriction, source, or selling
  behavior;
- a Wowhead WotLK item tooltip;
- a mouseover recipe/material link when a recipe applies.

Do not repeat the same pricing-methodology or reagent-floor paragraph in every
row. Put shared guidance in one clearly marked note and reference it with `*`.
Keep row notes specific to the item.

Published money labels must use no more than two currency units: `G & S` or
`S & C`, never `G & S & C`.

## 7. Apply and Render in Dependency Order

Run only the market-specific refresh that the work order authorizes. A one-item
addition must not opportunistically reprice an entire unrelated guide.

### Profession-crafted market

Check the matching reviewer's exact CLI first:

```powershell
python scripts/review-ah-<market>-prices.py --help
```

Most profession reviewers use this lifecycle where supported:

```text
inventory → refresh → review → refresh-dependencies → apply → check
```

Alchemy potions, gathering materials, and Mining have narrower command sets;
follow their `--help` output rather than inventing flags.

### Turn-ins or recipes

Update the audit script's Turn-in catalog definition or the audited recipe-guide
row selection first. Update the expected inventory count and its tests when the
scope intentionally grows. Never edit either generated audit JSON file as the
only source change.

```powershell
python scripts/audit-ah-phase3-catalogs.py --refresh
python scripts/audit-ah-phase3-catalogs.py --check
python scripts/review-ah-phase3-static-prices.py --market turn-ins --refresh
python scripts/review-ah-phase3-static-prices.py --market turn-ins --apply
python scripts/review-ah-phase3-static-prices.py --market turn-ins --check
python scripts/render-ah-phase3-static-guides.py
```

Use `--market recipes` for recipe and pattern additions. Review the saved report
between `--refresh` and `--apply`.

### Dropped gear

```powershell
python scripts/refresh-ah-dropped-gear-comparisons.py --refresh
python scripts/estimate-ah-dropped-gear-prices.py --report
# Review the saved large-change and evidence decisions here.
python scripts/estimate-ah-dropped-gear-prices.py --apply
python scripts/estimate-ah-dropped-gear-prices.py --check
python scripts/render-ah-dropped-gear.py
```

### Common downstream regeneration

After the market-specific apply step:

```powershell
python scripts/apply-ah-price-baselines.py
python scripts/audit-ah-crafted-prices.py --write
python scripts/render-ah-shared-sections.py
python scripts/render-ah-phase3-static-guides.py
python scripts/render-ah-dropped-gear.py
python scripts/apply-ah-section-price-order.py
python scripts/render-ah-guide-ux.py
python scripts/render-ah-container-collection.py
python scripts/build-ah-search-index.py
python scripts/apply-ah-item-tooltips.py
python scripts/audit-ah-auction-eligibility.py
```

Some commands may make no change. Running the shared dependency chain prevents
an individual input or duplicate correction from leaving craft floors, search,
tooltips, or guide ordering stale.

Update the footer of every changed `guides/*.html` page to the current local
date after its final render. Do not change untouched guide footers.

## 8. Gate F — Required Validation

### Canonical checks

```powershell
python scripts/audit-ah-crafted-prices.py --check
python scripts/apply-ah-price-baselines.py --check
python scripts/render-ah-shared-sections.py --check
python scripts/render-ah-phase3-static-guides.py --check
python scripts/render-ah-dropped-gear.py --check
python scripts/apply-ah-section-price-order.py --check
python scripts/render-ah-guide-ux.py --check
python scripts/render-ah-container-collection.py --check
python scripts/build-ah-search-index.py --check
python scripts/apply-ah-item-tooltips.py --check
python scripts/audit-ah-auction-eligibility.py --check
```

Also run the matching market reviewer with `--check` and any route-specific
catalog/comparison check.

### AH Python regression suite

```powershell
$failed = @()
Get-ChildItem tests -Filter 'ah-*.test.py' | Sort-Object Name | ForEach-Object {
  python $_.FullName
  if ($LASTEXITCODE -ne 0) { $failed += $_.Name }
}
if ($failed.Count) { throw "Failed AH tests: $($failed -join ', ')" }
```

### Node and browser checks

```powershell
npm test
```

In one terminal:

```powershell
python -m http.server 4173 --bind 127.0.0.1
```

In a second terminal:

```powershell
$env:AH_HUB_TEST_BASE='http://127.0.0.1:4173'
node tests/ah-hub-smoke.cjs
```

### Final file checks

- Confirm every changed guide footer has today's date.
- Confirm every new search result has one true price, correct rarity, correct
  demand, and an allowed Stack display.
- Confirm all item names resolve in `assets/ah-item-ids.js`.
- Confirm all duplicate guide occurrences agree on price, rarity, and stack.
- Confirm section ordering is highest Target buyout first unless the section has
  a recorded fixed progression.
- Scan edited text as UTF-8 and reject mojibake or replacement characters.
- Run `git diff --check`.
- Verify the work-order acceptance checklist and record all command results.

## 9. Acceptance and Handoff

An addition is complete locally only when:

- every requested item is present or has a recorded, evidence-backed exclusion;
- every price has source type, confidence, before/after bands, and review;
- no active listing or external nominal gold set a baseline;
- all deterministic floors and downstream duplicates are current;
- rarity, tooltip, recipe link, buyer notes, stack behavior, and ordering are
  correct;
- canonical, regression, and browser checks pass;
- the matching profession plan or evidence-status file records the addition;
- all edits are saved locally and publishing status is explicit.

Report the items added, exclusions, price decisions, confidence, large-change
reviews, guide sections, files, and tests. If the user has not asked to publish,
stop with the changes local and unstaged.

## 10. Publish Only When Explicitly Authorized

When the user says to make the addition live:

1. Fetch and verify the branch is not behind or diverged.
2. Stage only the intended AH source, evidence, generated output, tests, and
   documentation. Leave unrelated worktree changes unstaged.
3. Run `git diff --cached --check` and inspect the staged file list.
4. Commit, push, and verify `origin/main` is at `0 0` ahead/behind.
5. Wait for GitHub Pages deployment.
6. Run the public desktop/mobile smoke test:

```powershell
$env:AH_HUB_TEST_BASE='https://leblackstock.github.io/wotlk-server-guides'
node tests/ah-hub-smoke.cjs
```

If Pages still serves an older asset, wait and retry before reporting failure.
The addition is live only after the public test sees the expected item and
passes.
