# Container Pricing Review

- Reviewed: `2026-08-08`
- Missing drop and quest-reward containers reviewed: `22`
- Containers with qualified or sparse completed sales: `0`
- Present in the current local supply snapshot after owned-account exclusion: `3`
- Seen on at least two comparison realms: `22`
- Comparison requests: `132` initial / `0` final failures after the 2-, 5-, and 10-second retry rule
- Active Hellscream listings used to set prices: `no`
- External nominal or normalized gold copied into prices: `no`
- Publication status: `local only — not published`

## Method

The fixed gold scale comes from the already-reviewed Classic crafted bags with the same exact capacity. Gold-normalized Lordaeron, Icecrown, and Onyxia observations can change only within-capacity relative rank. The one current Hellscream scan is a supply diagnostic and never a valuation input. With no completed sales for these items, all 22 additions remain fallback-confidence starting bands.

## Frozen capacity anchors

| Capacity | Hellscream Target anchor | Existing reviewed comparables |
|---:|---:|---|
| 6 slots | 2g | item 4238: 2g 5s, item 5762: 1g 95s |
| 8 slots | 2g 30s | item 4240: 2g 30s, item 4241: 2g 65s, item 5763: 2g 20s |
| 10 slots | 2g 55s | item 4245: 2g 75s, item 5764: 2g 55s, item 5765: 2g 40s |
| 12 slots | 3g | item 10050: 2g 90s, item 10051: 3g 10s |
| 14 slots | 3g | item 14046: 3g |
| 16 slots | 3g 35s | item 14155: 3g 35s |

## Reviewed additions

| ID | Item | Route | Capacity | Realms | Local supply rows | Quick / Target / High | Confidence |
|---:|---|---|---:|---:|---:|---:|---|
| 4500 | Traveler's Backpack | drop | 16 | 3 | 0 | 2g 50s / 3g 35s / 5g 5s | fallback |
| 19291 | Darkmoon Storage Box | quest-reward | 14 | 3 | 0 | 2g 65s / 3g 50s / 5g 25s | fallback |
| 3914 | Journeyman's Backpack | drop | 14 | 3 | 0 | 2g 60s / 3g 45s / 5g 20s | fallback |
| 1685 | Troll-hide Bag | drop | 14 | 3 | 0 | 1g 90s / 2g 55s / 3g 85s | fallback |
| 1725 | Large Knapsack | drop | 12 | 3 | 1 | 1g 90s / 2g 55s / 3g 85s | fallback |
| 1652 | Sturdy Lunchbox | drop | 12 | 3 | 0 | 2g 60s / 3g 45s / 5g 20s | fallback |
| 932 | Fel Steed Saddlebags | drop | 10 | 3 | 0 | 2g 20s / 2g 95s / 4g 45s | fallback |
| 804 | Large Blue Sack | drop | 10 | 3 | 0 | 1g 60s / 2g 15s / 3g 25s | fallback |
| 5576 | Large Brown Sack | drop | 10 | 3 | 0 | 1g 75s / 2g 30s / 3g 45s | fallback |
| 5575 | Large Green Sack | drop | 10 | 3 | 0 | 1g 90s / 2g 55s / 3g 85s | fallback |
| 857 | Large Red Sack | drop | 10 | 3 | 0 | 1g 80s / 2g 40s / 3g 60s | fallback |
| 933 | Large Rucksack | drop | 10 | 3 | 0 | 2g 5s / 2g 70s / 4g 5s | fallback |
| 1470 | Murloc Skin Bag | drop | 10 | 3 | 0 | 2g 10s / 2g 80s / 4g 20s | fallback |
| 856 | Blue Leather Bag | drop | 8 | 3 | 1 | 1g 45s / 1g 95s / 2g 95s | fallback |
| 3233 | Gnoll Hide Sack | drop | 8 | 3 | 0 | 2g / 2g 65s / 4g | fallback |
| 5573 | Green Leather Bag | drop | 8 | 3 | 0 | 1g 75s / 2g 30s / 3g 45s | fallback |
| 2657 | Red Leather Bag | drop | 8 | 3 | 0 | 1g 60s / 2g 15s / 3g 25s | fallback |
| 5574 | White Leather Bag | drop | 8 | 3 | 1 | 1g 85s / 2g 45s / 3g 70s | fallback |
| 5571 | Small Black Pouch | drop | 6 | 3 | 0 | 1g 45s / 1g 90s / 2g 85s | fallback |
| 828 | Small Blue Pouch | drop | 6 | 3 | 0 | 1g 75s / 2g 30s / 3g 45s | fallback |
| 5572 | Small Green Pouch | drop | 6 | 3 | 0 | 1g 30s / 1g 70s / 2g 55s | fallback |
| 805 | Small Red Pouch | drop | 6 | 3 | 0 | 1g 60s / 2g 10s / 3g 15s | fallback |

## Evidence limits

- BeanCounter contained no records for these 22 item IDs, so none can claim a locally proven sale value.
- The Auctioneer snapshot excludes the user's identifiable account rows, but friend and guild identities are unavailable; it is diagnostic only.
- Cross-server pages report listings, not completed sales. They set relative order only and do not set the Hellscream gold scale.
- The pinned source verifies acquisition and eligibility, not current Hellscream custom drop rates or vendor modifications.

## Reproduction

```powershell
python scripts/review-ah-container-prices.py --check
```

Publishing is a separate step and was not authorized.
