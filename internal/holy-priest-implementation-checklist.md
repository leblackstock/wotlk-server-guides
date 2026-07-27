# Holy Priest Implementation Checklist

- [x] Add class, spec, and mechanic tokens to assets/guide-color-system.css
- [x] Replace every TODO and template-todo marker
- [x] Verify 18/53/0 talent point total and calculator URL
- [x] Verify spell, glyph, item, source, raid size, and difficulty data
- [x] Extend assets/priest-tooltips.js with verified IDs
- [x] Add the Guide Hub card to index.html
- [x] Check all navigation, pagers, anchors, icons, filters, keyboard controls, mobile, and print
- [x] Run node --check assets/holy-priest.js
- [x] Run node --check assets/priest-tooltips.js
- [x] Mark uncertain private-server behavior as Needs Hellscream test
- [x] Update cache keys before release

## Mandatory game-entity links and icons
- [x] Inventory every named item, enchant, recipe, glyph, gem, consumable, skill, talent, and ability across all six pages
- [x] Verify every WotLK item/spell ID, displayed alias, source, and appropriate icon filename
- [x] Add all verified entities to data/priest-entities.json
- [x] Rebuild assets/priest-tooltips.js with `node tools/build-wowhead-tooltips.mjs data/priest-entities.json assets/priest-tooltips.js`
- [x] Confirm registered phrases link in ordinary prose without manual wrappers
- [x] Confirm Wowhead's WotLK tooltip engine loads and mouseovers work
- [x] Use selective inline icons by default; dense mode requires explicit config approval
- [x] Add contextual icons only where they improve scanning, recognition, or decision grouping
- [x] Confirm the analyzer's opportunity score and complexity tier match the guide's actual rendered structure
- [x] Confirm every page falls inside its calculated contextual-icon range
- [x] Confirm required coverage passes only for structures that actually exist
- [x] Confirm inline entity icons stay inside the calculated link-based allowance and below 25 per 1,000 words
- [x] Run `node tools/audit-spec-guide.mjs templates/spec-guide/holy-priest.config.json` during drafting
- [x] Run `node tools/analyze-guide-icon-density.mjs --config templates/spec-guide/holy-priest.config.json --policy templates/spec-guide/icon-density-policy.json` while tuning visual density
- [x] Run `node tools/audit-spec-guide.mjs templates/spec-guide/holy-priest.config.json --release`; this automatically runs and enforces the rendered complexity-based icon audit

The checked state records the release audit for this complete six-page family. Hellscream-specific behavior remains explicitly test-labeled in the public guide.
