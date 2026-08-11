# Companions, Mounts & Accessories Demand and Turnover Review

- Review date: `2026-08-10`
- Active rows reviewed: `127`
- Comparison markets per item: `6`
- Active item/market checks: `762`
- Promotional-exclusion checks: `6`
- Total comparison requests: `768` initial / `0` final failures
- Items with valid local completed sales: `1`
- Items present in the current local supply snapshot: `2`
- Items present in at least one comparison market: `117`

## Interpretation

Demand is buyer-interest breadth, not guaranteed sales speed. Turnover is shown separately and remains conservative for a low-population realm. The external comparison pages expose current listings, so they establish supply breadth and scarcity only; they do not prove a completed sale, sell-through rate, cancellation, or expiration. One snapshot cannot measure turnover.

The only valid local completed-sale evidence in this scope is one Wood Frog Box buyout from one buyer on one day. It supports real but sparse demand and does not justify calling the category fast-moving.

## Demand label distribution

| Label | Rows |
|---|---:|
| High | 11 |
| High in season | 5 |
| Low in season | 25 |
| Low-Med | 34 |
| Low-Med in season | 3 |
| Med | 11 |
| Med in season | 15 |
| Med-High | 23 |

## Turnover label distribution

| Label | Rows |
|---|---:|
| Seasonal | 48 |
| Slow | 29 |
| Slow / steady | 29 |
| Very slow | 21 |

## Classification policy

- Unlimited vendor pets: Low-Med interest, Slow / steady turnover. Collection achievements create utility, but unlimited stock makes this primarily convenience arbitrage.
- True limited-stock pets: Med interest, Slow turnover. Stock caps and restock timers support a stronger convenience market; Wood Frog also has one sparse local sale.
- Argent Tournament pets: Med-High interest, Slow turnover. Pet-count achievements and faction-gated, time-gated supply support collector interest.
- Farmed pets: Low-Med through High interest according to current comparison-market scarcity, with Slow or Very slow turnover. Scarcity is not itself a sale.
- Crafted companions: Med interest, Slow turnover. Profession-restricted mounts remain Med because their buyer pool is narrower.
- Mechano-hog and Mekgineer's Chopper: High interest, Slow turnover because they combine mount-count progress, passenger utility, and a high craft floor.
- Crimson Deathcharger and Jaina's Locket: High interest, Very slow turnover. The former advances mount collection; the latter adds reusable Dalaran portal utility. Both are high-ticket prestige rewards.
- Seasonal achievement consumables: High in season, Seasonal turnover, and expected Very Low interest off-season.
- Seasonal apparel: Med in season, Seasonal turnover, and expected Low interest off-season. Pure novelty rows remain lower.

## Known demand sources

- [50-pet collection achievement](https://www.wowhead.com/wotlk/achievement=1250/shop-smart-shop-pet-smart)
- [75-pet collection achievement](https://www.wowhead.com/wotlk/achievement=2516/lil-game-hunter)
- [50-mount collection achievement](https://www.wowhead.com/wotlk/achievement=2143/leading-the-cavalry)
- [100-mount collection achievement](https://www.wowhead.com/wotlk/achievement=2536/mountain-o-mounts)
- [Shafted! event achievement](https://www.wowhead.com/wotlk/achievement=1188/shafted)
- [Fistful of Love event achievement](https://www.wowhead.com/wotlk/achievement=1699/fistful-of-love)
- [Torch Juggler event achievement](https://www.wowhead.com/wotlk/achievement=272/torch-juggler)
- [Frenzied Firecracker event achievement](https://www.wowhead.com/wotlk/achievement=1552/frenzied-firecracker)
- [The Rocket's Red Glare event achievement](https://www.wowhead.com/wotlk/achievement=1281/the-rockets-red-glare)
- [General-use passenger motorcycle utility](https://www.wowhead.com/wotlk/item=41508/mechano-hog)
- [Jaina's Locket Dalaran portal utility](https://www.wowhead.com/wotlk/item=52251/jainas-locket)

## Comparison supply source

- [Nerfed AH server index](https://ah.nerfed.net/servers/base?id=7): Icecrown, Lordaeron, and Onyxia; Horde and Alliance snapshots for each realm.
- Per-item quantities, market presence, scan timestamps, and direct page URLs are saved in `data/ah-collectible-demand-evidence.json`.
- Nominal external gold values are neither saved nor used. This demand review changes no Quick, Target, or High price.

## Promotional exclusion

Polar Bear Collar is excluded from the active guide. Its pinned route is the iCoke promotional voucher quest, there is no saved Hellscream enablement evidence, and the saved exclusion check found it in `0` of six comparison markets.

## Reproduction

```powershell
python scripts/review-ah-collectible-demand.py --check
```
