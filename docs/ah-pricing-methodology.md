# Non-Circular AH Pricing Methodology

The guide must not learn its prices from auctions posted from the guide. Active
Auction House listings describe competition and availability; they do not prove
value, demand, or a completed sale.

## Three Separate Evidence Layers

1. **Frozen baseline:** the saved quick, target, and high reference in
   `data/ah-price-baselines.json`. Crafted-price calculations may consume only
   this layer, exact vendor costs, deterministic conversions, and documented
   fallbacks.
2. **Realized sales:** completed BeanCounter transactions. These can validate or
   replace a baseline only after the minimum evidence gate below is met.
3. **Current listings:** seller count, unit count, stack sizes, concentration,
   and competing asks. Use this only to decide whether, when, and how much to
   post. Never copy a listing median into the baseline.

## Accepted Baseline Evidence

Evidence is strongest in this order:

- `high`: exact unlimited-vendor cost or a deterministic conversion whose every
  input is independently anchored.
- `medium`: realized sales covering at least 20 units, four completed auctions,
  two distinct buyers, and two distinct days, without a known guild/friend
  transfer or one buyer controlling most of the volume.
- `low`: a frozen pre-scan reference, limited realized history, or a conversion
  containing low-confidence inputs.
- `fallback`: no independent price evidence; the number exists only so a rare
  recipe can be costed and must be treated as provisional.

Measured farming or acquisition yields may establish a baseline only when the
record includes the route, elapsed time, output quantity, and explicit gold-per-
hour opportunity-cost assumption. Do not invent a farming yield.

## Seller-Concentration Guard

Record active-listing concentration before interpreting a scan. Mark the scan
as unusable for valuation when any of these apply:

- the user and known friends control 30% or more of listed units;
- one seller controls 25% or more of listed units;
- fewer than three independent sellers remain after known-account exclusions;
- the market has only one snapshot and no completed-sale history.

Even a well-distributed scan remains competition evidence only. Passing these
guards does not promote listing prices into the baseline.

## Feedback-Loop Guard

- No script may automatically update `data/ah-price-baselines.json` from active
  listings.
- A guide-generated posting price cannot be used as evidence merely because it
  appears in a later scan.
- Completed sales may validate the band, but baseline replacement is manual and
  must record counts, buyers, days, price range, and confidence.
- Friend transfers, test purchases, cancelled auctions, bids, and expired
  listings are not realized-market evidence.
- When evidence is insufficient, freeze the prior baseline and lower its
  confidence instead of manufacturing a new current price.

## Price-Band Meaning

- **Quick:** conservative sale band or exact recipe floor plus the smallest
  margin. It is not an instruction to undercut an observed listing.
- **Target:** normal posting goal supported by the saved baseline and demand
  margin.
- **High / scarce:** patient ask for genuine scarcity or slow turnover; it is
  not automatically justified by an empty AH.

For crafted items, exact same-band reagent cost and minimum guaranteed output
come first. Demand margins are modest and deterministic. Current competitors
may tell the player not to craft or not to post, but they do not rewrite the
cost model.

## Display Currency Rule

Saved baselines and craft calculations retain their exact copper values. The
published AH guides and search cards use no more than two currency units:

- Prices below 1g display silver and copper (`S & C`) without rounding.
- Prices of 1g or more round to the nearest silver and display gold and silver
  (`G & S`); copper is never shown with gold.
- Fifty copper rounds up, and rounding carries normally into the next gold.
- Grouped search results compare these displayed values, so sub-silver rounding
  differences do not incorrectly produce a `Varies` label.

## Required Workflow

1. Audit baseline coverage and confidence before adding a profession.
2. Record BeanCounter realized-sale coverage separately from active scans.
3. Record scan concentration without importing scan prices.
4. Recalculate exact crafted floors from the frozen baseline.
5. Apply canonical baseline and shared crafted-output prices to static rows.
6. Regenerate the crafted sections, search index, and tooltip assets.
7. Run baseline, cross-guide, crafted-market, and browser checks.
8. Update a baseline only when the accepted-evidence record is saved with it.

The initial 2026-08-02 baseline is intentionally conservative: 650 pre-scan
guide references are frozen as low confidence, with stronger classifications
added only where independent evidence exists. This stops circular repricing
immediately while preserving usable provisional posting bands.

The 2026-08-03 Jewelcrafting expansion added eight explicit fallback-confidence
input references that were absent from the pre-scan guide set. They are retained
as documented fallbacks—not current-price claims—until realized sales or measured
acquisition evidence supports replacement.

The 2026-08-03 Tailoring expansion added four more fallback-confidence inputs:
Long Elegant Feather, Naga Scale, Morrowgrain, and Soul Essence. Exact unlimited-
vendor dye costs remain vendor overrides, while BoP Ogre Tannin uses a separately
identified access-cost fallback. None of these values came from active listings.

The 2026-08-03 Leatherworking expansion added 28 fallback-confidence inputs for
legacy scales, hides, feathers, carapaces, and other specialty drops that were not
in the frozen pre-scan guide set. Their provisional bands are anchored to saved
comparable material tiers and explicit acquisition constraints—not active
listings—and must be replaced when qualifying realized-sale or measured-yield
evidence becomes available.

The 2026-08-03 Cooking expansion added 11 fallback-confidence inputs for missing
legacy meats, quest drops, Northrend fish, Northern Egg, and event-limited Wild
Turkey. Fourteen other missing recipe inputs received exact coin-vendor records,
including Horde Pilgrim's Bounty ingredients. The fallback bands use saved
comparable ingredient tiers and event availability; no active listing was used.

The 2026-08-03 Mining expansion added one fallback-confidence input, Elementium
Ore. Its 10g quick band equals the exact 3.3.5 vendor liquidation value; the 20g
target and 40g high bands are provisional scarcity ranges used only to cost
Elementium Bar. No active listing was used, and the bands must be replaced when
qualifying realized-sale or measured-acquisition evidence becomes available.

The 2026-08-03 First Aid expansion added three fallback-confidence venom-sac
inputs. Small Venom Sac uses 20s / 40s / 80s and is anchored above its exact 82c
vendor liquidation value. Large and Huge Venom Sacs use 1g / 2g / 4g, anchored
above exact 1s 85c and 15s liquidation values respectively. These provisional
ranges make the three anti-venom recipes costable without importing active AH
listings; they must be replaced when qualifying realized sales or measured
acquisition evidence becomes available.
