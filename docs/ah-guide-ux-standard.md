# Auction House Guide UX Standard

Status: approved permanent standard; live rollout implemented 2026-08-10.

Last reviewed: 2026-08-10.

## Scope

This standard applies to Auction House market and reference guides that display a source or selling-notes field. It records the approved interaction and visual behavior. Future changes must continue through the shared assets, renderers, and canonical sources rather than page-specific copies.

## Source and selling notes

- On desktop widths above 1000 px, hide the wide source/selling-notes table column and place exactly one teal action labeled **Source & notes** with each item.
- Do not add a separate source-type, acquisition-type, vendor-type, or similar chip beside the action.
- Activating **Source & notes** opens the row's complete source and selling notes in a full-width panel immediately below that row. Do not abbreviate or discard any of the original note content.
- While open, the action label changes to **Hide notes**. A separate **Close notes** action closes the panel and returns keyboard focus to the originating action.
- Only one source-notes panel may be open within a table at a time.
- At widths of 1000 px and below, use the full card layout, keep source and selling notes visible in the card, and hide the desktop disclosure action and panel row.
- Preserve semantic buttons, `aria-expanded`, `aria-controls`, a labeled notes region, keyboard operation, and reduced-motion behavior.

## Search-result row highlighting

- Search selection and pulse highlighting must apply to the whole table row on desktop and the whole card on tablet/mobile.
- Individual cells must not animate or carry their own highlight backgrounds, filters, shadows, or transitions while the containing row/card is selected or pulsing.
- Preserve existing search deep links, row selection, keyboard behavior, and navigation behavior.

## Coverage and reference placement

- Do not include a redundant **Coverage & Sources** entry or banner in the top shopping navigation.
- Preserve the substantive coverage and verification material in the bottom reference area; do not delete it to shorten the top navigation.
- Keep the bottom reference sections in this order: **Excluded and pending verification**, **What is covered**, **Sources**, then **Disclaimer**.
- Place **What is covered** immediately before **Sources**.
- Do not include back-links to a removed **Coverage & Sources** banner. Retain the section's **↑ Top** control.

## Section-heading navigation controls

- Place navigation controls inside the section heading area, beside the section title rather than below the section content or in a separate navigation block.
- For a nested section, show the contextual parent control first and the top control second: **← Parent category**, then **↑ Top**. For example: **← Seasonal** followed by **↑ Top**.
- On desktop, keep the controls together at the right side of the heading line. The contextual parent control starts the control group, and **↑ Top** sits directly beside it.
- When only **↑ Top** applies, keep it in the same right-side heading position.
- On narrow screens, allow the controls to wrap cleanly within the heading area without horizontal page overflow. Preserve their order and keep them visually associated with the heading.
- Use the actual parent category name in the contextual label and link it to that category's stable anchor. Link **↑ Top** to the page's `#top` anchor.
- Preserve semantic links, descriptive accessible names, keyboard operation, and visible hover and focus states.

## Implementation boundary

- Keep source and selling-note content in its canonical data source. Do not duplicate or hand-maintain note text in generated guide HTML.
- Implement this behavior centrally through the appropriate shared renderer, stylesheet, and script so every applicable AH guide receives the same behavior.
- Treat the current collectibles test page and its dedicated assets as prototype evidence only. Do not copy prototype-only code directly into individual live guide pages.
- Before rollout, identify every affected AH guide and generator, then verify all generated outputs and shared navigation/search behavior.
- Publishing remains a separate step and requires explicit user authorization.

## Acceptance criteria

- Exactly one teal **Source & notes** action appears for each eligible desktop row, and no source-type chip appears.
- The complete note opens immediately below the correct row, only one panel per table remains open, and closing restores focus.
- Tablet/mobile cards retain visible notes without the disclosure action.
- Search highlighting and pulse animation affect the whole row/card, never its individual cells.
- The top shopping navigation has no redundant **Coverage & Sources** entry, and the approved bottom reference order is preserved.
- Nested section headings show **← Parent category** immediately followed by **↑ Top** in the approved heading position.
- There is no horizontal page overflow at 1440 px, 1024 px, 1000 px, or 800 px viewport widths.
- Keyboard navigation, accessibility attributes, reduced-motion behavior, search links, and existing guide navigation continue to work.
- The repository's AH validation, rendering, ordering, search, and browser smoke tests pass for all affected guides.

## Approval and rollout record

- Approved on 2026-08-10 with a teal **Source & notes** action, no source-type chip, and whole-row/card pulse highlighting.
- Coverage/reference placement approved on 2026-08-10 after review of the collectibles prototype.
- Section-heading placement and ordering of **← Parent category** and **↑ Top** approved on 2026-08-10 from the existing collectibles navigation pattern.
- Rolled out through `assets/ah-source-notes.js`, `assets/ah-price-guide.css`, and `scripts/render-ah-guide-ux.py` across all applicable active AH guides on 2026-08-10.
