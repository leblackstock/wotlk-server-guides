# Companions, Mounts & Accessories AH Pricing Review

- Review date: `2026-08-10`
- Items reviewed: `128`
- Qualified or sparse Hellscream completed-sale histories: `1`
- Present in current Hellscream supply after owned-account exclusion: `2`
- Seen on at least two comparison realms: `55`
- Comparison requests: `336` initial / `0` final failures after the 2-, 5-, and 10-second retry rule

## Decision

Active Hellscream listings were used only as supply diagnostics and never set or raised a price. Exact unlimited-vendor costs, stock caps, restock timers, token quantities, and crafted recipe floors are recorded independently. Completed sales take priority when they pass the evidence gate. With only one sparse completed sale in this batch, nearly all non-vendor prices remain clearly labeled fallback estimates.

## Evidence hierarchy used

1. Exact unlimited coin-vendor cost or deterministic recipe floor.
2. Qualified Hellscream completed buyouts.
3. Sparse completed buyouts shrunk toward a fixed acquisition-cohort anchor.
4. Fixed Hellscream acquisition-cohort anchor, with cross-server observations used only for within-cohort relative rank.

## Saved fixed anchors

| Cohort | Target anchor | Basis |
|---|---:|---|
| vendor-token | 350g | Reviewed 350g Hellscream starter anchor for a 40 Champion's Seal faction companion. |
| companion-drops | 500g | Reviewed 500g Hellscream starter anchor for a farmed, nonstackable companion drop. |
| companion-quest-rewards | 300g | Reviewed 300g Hellscream starter anchor for a tradeable quest-chain companion reward. |
| crafted-companion | 75g | Reviewed 75g collectible-demand anchor; exact same-band recipe cost remains the minimum craftability diagnostic. |
| crafted-profession-mount | 1,000g | Reviewed 1,000g starter anchor for a profession-restricted crafted mount; exact recipe cost remains separate. |
| crafted-motorcycle | 18,000g | Reviewed 18,000g starter anchor for the general-use motorcycle market; exact vendor components and materials set the craft floor. |
| quest-accessories | 10,000g | Reviewed 10,000g Hellscream starter anchor for the tradeable Shadowmourne sealed-chest reward family. |
| seasonal-companion | 250g | Reviewed 250g Hellscream starter anchor for a tradeable event companion reward. |
| seasonal-apparel | 75g | Reviewed 75g Hellscream starter anchor for tradeable event apparel and appearance demand. |
| seasonal-novelty | 15g | Reviewed 15g Hellscream starter anchor for a tradeable event novelty without a coin or token floor. |

## Local completed-sale result

Wood Frog Box has one valid 20g completed buyout from one buyer on one day. It remains low confidence and receives 25% weight; the reviewed limited-vendor fallback receives 75%. No other included item has a valid completed buyout in the saved BeanCounter snapshot.

## Limits

- Comparison-realm pages report asks, not completed sales. Their nominal gold values are not saved or copied.
- A token requirement proves acquisition cost, but not a gold conversion; token-priced rows remain fallback confidence.
- Promotional and TCG mounts are excluded until direct Hellscream availability is verified; a generic base-database loot route is not proof that the rewards are enabled on this server.
- Shadowmourne reward prices are discovery bands for a thin market, not verified current values.
- Limited and unlimited vendors remain separate because a stock cap and restock timer materially change arbitrage risk.
- Every holiday is rendered separately, including explicit empty in-scope sections where only BoP, temporary, or unverified rewards exist.

## Reproduction

```powershell
python scripts/review-ah-collectible-prices.py --check
```

Publishing is a separate step and is not part of this review.
