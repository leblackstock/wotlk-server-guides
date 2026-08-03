# Jewelcrafting AH Expansion Plan

- Status: `planned`
- Existing guide: `guides/jewelcrafting-gems-ah-price-guide.html`
- Work type: full crafted catalog
- Suggested order: 2

> Hard gate: finish and record the current-price audit before adding crafted
> rows. Follow [the shared Gate 0](README.md#gate-0-audit-current-prices-before-adding-crafteds).

## Current-Price Audit

- Recheck all 82 current rows: epic/rare/uncommon raw gems, meta bases and cut
  metas, Dragon's Eye, prospecting ores, older gems, stone, and settings.
- Reconcile ores with Mining, Eternals with cross-profession materials, and
  raw-gem prices wherever the same gem appears in another guide.
- Verify the server's binding/tradeability rules for Dragon's Eye and
  jewelcrafter-only cuts before retaining or pricing them.
- Audit existing cut-gem values against the current uncut-gem opportunity cost.

## Crafted Coverage

- All valid tradeable cuts for Wrath epic, rare, uncommon, and meta gems, with
  exact cut item IDs and recipe spell IDs.
- Tradeable rings, necklaces, crowns, trinkets, statues, settings, and other
  deterministic Jewelcrafting outputs across Wrath, Outland, and Classic.
- Review Icy Prism and other random-output crafts separately; list outputs in
  their normal material sections, not as deterministic finished crafts.
- Exclude BoP figurines, jewelcrafter-only results that are not auctionable,
  self-only effects, and invalid duplicate spell records.

## Profession-Specific Price Checks

- A cut gem consumes the sale value of its uncut gem. Calculate the floor from
  that exact color/quality, then add only a demand-supported cutting premium.
- Do not assign the full Icy Prism or prospecting input cost to each possible
  gem. Use documented expected value if those conversions are analyzed.
- Check whether identical stats exist in multiple colors or qualities; price
  each from its own input and demand, not by copying a same-stat result.
- Price jewelry from exact gems, settings, bars, and vendor components; keep
  slow BoE gear in singles.

## Notes to Verify

- For gems, give the exact stat combination and likely role/build without
  claiming universal best-in-slot status.
- Call out meta activation requirements in concise item-specific notes when
  they materially affect demand.
- For jewelry, state slot, level, role, binding, and whether the market is
  gearing, twink, leveling, or collection driven.

## Acceptance Checks

- [ ] Current-price audit completed and recorded.
- [ ] Every valid tradeable cut has an item ID, recipe ID, rarity, and price.
- [ ] Raw-versus-cut opportunity costs are tested.
- [ ] Random-output conversions use an explicit model or remain unpriced.
- [ ] BoP and jewelcrafter-only non-AH outputs are excluded.
- [ ] Shared validation in `README.md` passes.

## Evidence Log

- Audit date:
- Live AH observations:
- Recipe/item sources checked:
- Server-specific binding findings:
- Random-output method:
- Decisions and unresolved items:
- Completion summary:
