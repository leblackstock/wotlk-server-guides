# AH Profession Expansion Plans

These files are the required starting point for profession expansions and the
saved evidence for completed canonical crafted-item passes. They keep price
research, recipe coverage, notes, links, and validation consistent from one
profession to the next.

## Required Use

For the next AH addition:

1. Read this file and the matching profession plan.
2. Change that plan's status to `in progress` and record the date.
3. Complete **Gate 0: non-circular baseline audit** before adding crafted rows.
4. Record sources, unresolved questions, and important decisions in the plan's
   evidence log while working.
5. Complete the plan's acceptance checks, then mark it `complete`.
6. Publish only after the user explicitly asks to make the work live.

Follow [the non-circular pricing methodology](../ah-pricing-methodology.md).
Freeze weak evidence as low confidence instead of replacing it with an active-
listing median. A documented fallback may cost a rare recipe, but it must never
be presented as a verified current price.

## Profession Registry and Suggested Order

| Order | Profession | Work type | Plan |
|---:|---|---|---|
| 1 | Blacksmithing | Complete — 2026-08-02 | [blacksmithing.md](blacksmithing.md) |
| 2 | Jewelcrafting | Full crafted catalog | [jewelcrafting.md](jewelcrafting.md) |
| 3 | Tailoring | Full crafted catalog | [tailoring.md](tailoring.md) |
| 4 | Leatherworking | Full crafted catalog | [leatherworking.md](leatherworking.md) |
| 5 | Cooking | Full crafted catalog | [cooking.md](cooking.md) |
| 6 | Mining | Smelting-output catalog | [mining.md](mining.md) |
| 7 | First Aid | Small full catalog and guide-placement decision | [first-aid.md](first-aid.md) |
| 8 | Herbalism | Gathering-price audit; no normal crafted outputs | [herbalism.md](herbalism.md) |
| 9 | Skinning | Gathering-price audit; conversions belong to Leatherworking | [skinning.md](skinning.md) |
| 10 | Fishing | Gathering-price audit; finished food belongs to Cooking | [fishing.md](fishing.md) |

Alchemy, Blacksmithing, Enchanting, Engineering, and Inscription have canonical
crafted catalogs in `data/ah-crafted-sections.json`. They remain comparison
models, not unfinished plans. Jewelcrafting is the next suggested expansion.

## Gate 0: Establish Non-Circular Baselines Before Adding Crafteds

This gate applies to every expansion plan, including the gathering-only audits.

- Inventory every existing row in the profession's current guide and identify
  the same item wherever it appears in another AH guide.
- Verify that prices are per item or per stated stack; correct accidental
  per-stack/per-unit mismatches.
- Audit the frozen reference in `data/ah-price-baselines.json`, its source type,
  and its confidence before changing any band.
- Record current AH seller count, units, and concentration separately. Active
  listings may guide posting timing and stack size, but never establish value.
- Record completed BeanCounter sales separately. Promote them into the baseline
  only when they pass the realized-sales gate in the shared methodology.
- Verify fixed vendor prices against the canonical vendor catalog and reconcile
  shared reagents with their canonical guide rows.
- Reconcile duplicate item names to one canonical quick, target, and high band
  unless a documented quantity or form difference explains the variation.
- Confirm `quick <= target <= high`, bid does not exceed buyout, values are
  plausible for the listed demand, and suggested stacks match the real max
  stack and likely purchase quantity.
- Confirm the item ID, expansion/tier, tradeability, binding, rarity class, and
  source note for every row touched.
- Check the finished item against `data/ah-profession-use-audit.json`. Put hard
  skill requirements in a dedicated profession-restricted section, label tools
  and inputs for their actual profession buyer, and keep genuinely general-use
  finished items separate even when another profession crafts them.
- Audit every ingredient that will feed the new crafted catalog. Crafted-price
  work may begin only after those inputs have a saved baseline, confidence, and
  internally consistent conversion path.
- Mark missing independent evidence as `low` or `fallback`; do not disguise an
  active listing or provisional band as a verified current price.

## Crafted Catalog Discovery

- Build the candidate list from the WotLK 3.3.5 profession spell list, then map
  each spell to its output item ID and minimum guaranteed quantity.
- Verify the exact recipe, reagent counts, output count, item rarity, and
  binding with WotLK-era data. Cross-check questionable records against the
  AzerothCore 3.3.5 item/spell baseline.
- Include tradeable deterministic outputs from Wrath, Outland, and Classic when
  they have a real AH use. Keep the sections tiered and scannable.
- Exclude BoP outputs, self-only applications, quest/conjured/temporary items,
  invalid or not-implemented records, and items owned by another profession.
- Treat random-output crafts separately. Never charge the entire input cost to
  every possible random result; use a documented expected-value allocation or
  omit an unsupported price.

## Crafted Price Method

For a deterministic recipe, calculate each band per finished item:

`sum(each reagent quantity × that reagent's same price band) ÷ minimum guaranteed output`

Then apply a modest, documented demand-sensitive margin. Use guaranteed output,
not specialization procs. Keep these checks explicit:

- A craft's quick band must not undercut its saved quick reagent baseline unless
  the row clearly documents a cheaper deterministic supply path.
- Opportunity cost applies when the recipe consumes a tradeable intermediate,
  uncut gem, cloth cooldown, bar, leather, or other saleable input.
- Cooldowns, rare recipes, reputation gates, and specialization access belong
  in notes. Do not hide an arbitrary access surcharge inside the reagent floor.
- Random crafts, discovery systems, prospecting, and similar conversion markets
  need their own explicit expected-value model.
- Expensive slow-sale gear should be priced and posted as singles. Do not imply
  that craft cost guarantees a buyer.

## Notes and Links Standard

- Add one shared `*` craft-cost note per guide or crafted block. Do not repeat
  the same reagent-floor paragraph in every row.
- Give each row only its useful difference: buyer/build, actual effect, raid or
  PvP relevance, leveling or collection use, purchase quantity, turnover risk,
  or a profession-specific warning.
- Link every crafted row to the exact WotLK recipe spell with the existing
  mouseover pattern: `Recipe & mats ↗`, Wowhead WotLK `spell=` URL,
  `data-wowhead`, accessible label, and the shared-note `*` link.
- Color every item name by actual item rarity with the correct `q-*` class.
- Avoid vague claims such as `best`, `raid`, or `high demand` unless the item
  effect and intended buyer make the claim defensible.
- Put shared server-rule caveats in one note. Keep row notes specific.

## Implementation and Validation

The preferred source of truth for a completed crafted pass is
`data/ah-crafted-sections.json`, rendered into the appropriate guide. Extend the
crafted-price audit configuration and recipe snapshot rather than hand-editing
hundreds of generated rows.

When a guide changes:

- Regenerate shared sections if canonical vendor/shared data changed.
- Regenerate `assets/ah-search-index.js`.
- Apply/verify item IDs and tooltip metadata in `assets/ah-item-ids.js` and the
  affected guide.
- Update only the edited guide's `Updated YYYY-MM-DD` footer.
- Run UTF-8/mojibake checks and `git diff --check`.
- Run at least:

```powershell
python scripts/render-ah-shared-sections.py --check
python scripts/apply-ah-profession-use-sections.py --check
python scripts/apply-ah-price-baselines.py --check
python scripts/build-ah-search-index.py --check
python scripts/apply-ah-item-tooltips.py --check
python scripts/audit-ah-crafted-prices.py --check
python tests/ah-crafted-market.test.py
python tests/ah-price-baseline.test.py
python tests/ah-cross-guide-consistency.test.py
python tests/ah-vendor-pricing.test.py
python tests/ah-hub-structure.test.py
node tests/ah-hub-smoke.cjs
```

Add profession-specific assertions when a new pricing rule, ownership boundary,
or random-output model would otherwise be easy to regress.

## Definition of Done

A profession is complete only when:

- Gate 0 and its evidence log are complete.
- The candidate recipe list has an inclusion or exclusion decision for every
  relevant tradeable output.
- Prices trace to saved input baselines, recorded confidence, and correct output quantities.
- Notes are specific, recipe links mouse over correctly, and rarity colors are
  accurate.
- Duplicate prices across guides agree.
- Generated assets are current and all relevant tests pass.
- The guide footer is current and the plan records what was changed.
- If publishing was requested, only intended files were committed and pushed,
  and the public GitHub Pages result was verified.
