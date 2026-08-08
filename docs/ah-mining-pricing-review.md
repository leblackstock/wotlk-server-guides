# Mining Evidence Pricing Coverage Review

- Reviewed: `2026-08-08`
- Scope: `All 24 Mining-owned outputs across four sections`
- Outputs with completed Phase 1A Evidence Pricing: `22`
- Exact reversible 10:1 conversions: `2`
- Phase 1A price bands changed: `18`
- New price changes in this closeout: `0`
- Items with completed-sale evidence: `0`
- Evidence-priced items with all-three-realm coverage: `22`
- Saved Target changes over 50%: `6`
- Market estimates below at least one current recipe-floor band: `5`
- Active Hellscream listing prices used: `no`
- External gold copied into Hellscream prices: `no`
- Publication status: `local only — not published`

## Decision

Mining required a coverage closeout, not a second comparison fetch. The 22 bars and alloys were already reviewed in the Phase 1A gathering/material batch, and their canonical rows still match those saved decisions. Mote of Fire and Mote of Earth remain exact reversible 10:1 conversions tied to their canonical mote values without a convenience markup.

The saved Phase 1A snapshot is `2026-08-05`. It changed 18 Mining bands: seven Targets rose, seven fell, and eight stayed unchanged. All 22 market-reviewed outputs had three-realm relative-rank coverage. Six Target moves exceeded 50% and retained explicit reviewer acceptance. No completed Mining-output sale history was available.

Five market estimates fall below at least one current exact recipe-cost band. Those are sale-value estimates, not profitable-smelting claims; the guide keeps the shared instruction to avoid buying inputs for an unprofitable conversion.

## Reproduction

```powershell
python scripts/review-ah-mining-prices.py --check
```

Publishing is a separate step and is not part of this review.
