# Feral Cat Druid Implementation Checklist

- [x] Add class, spec, and mechanic tokens to assets/guide-color-system.css
- [x] Replace every TODO and template-todo marker
- [x] Verify every Two-minute operating manual title icon, example icon, ID, and Wowhead type
- [x] Verify 0/55/16 talent point total and calculator URL
- [x] Verify spell, glyph, item, source, raid size, and difficulty data
- [x] Extend assets/druid-tooltips.js with verified IDs
- [x] Add the Guide Hub card to index.html
- [x] Check all navigation, pagers, anchors, icons, filters, keyboard controls, mobile, and print
- [x] Confirm every ability/action chip in every spec playbook card renders its own verified WoW icon
- [x] Confirm the baseline works without external raid buffs or a specific party composition
- [x] Present caps as progression goals and allow normal/heroic dungeon entry before raid readiness
- [x] Include affordable gems and enchants before premium options
- [x] Keep ToC, ICC, Ruby Sanctum, heroic, and 25-player targets in later progression sections
- [x] Run node tools/audit-fresh-80-guide.mjs templates/spec-guide/feral-cat-druid.config.json
- [x] Run node --check assets/feral-cat-druid.js
- [x] Run node --check assets/druid-tooltips.js
- [x] Run node tools/audit-playbook-ability-icons.mjs templates/spec-guide/feral-cat-druid.config.json after the regular icon-density audit
- [x] Mark uncertain private-server behavior as Needs Hellscream test
- [x] Update cache keys before release

## Mandatory game-entity links and icons
- [x] Inventory every named item, enchant, recipe, glyph, gem, consumable, skill, talent, and ability across all six pages
- [x] Verify every WotLK item/spell ID, displayed alias, source, and appropriate icon filename
- [x] Add all verified entities to data/druid-entities.json
- [x] Rebuild assets/druid-tooltips.js with `node tools/build-wowhead-tooltips.mjs data/druid-entities.json assets/druid-tooltips.js`
- [x] Confirm registered phrases link in ordinary prose without manual wrappers
- [x] Confirm Wowhead's WotLK tooltip engine loads and mouseovers work
- [x] Use selective inline icons by default; dense mode requires explicit config approval
- [x] Add contextual icons only where they improve scanning, recognition, or decision grouping
- [x] Confirm the analyzer's opportunity score and complexity tier match the guide's actual rendered structure
- [x] Confirm every page falls inside its calculated contextual-icon range
- [x] Confirm required coverage passes only for structures that actually exist
- [x] Confirm inline entity icons stay inside the calculated link-based allowance and below 25 per 1,000 words
- [x] Confirm every ability/action chip in every spec playbook card renders its own verified WoW icon
- [x] Run `node tools/audit-spec-guide.mjs templates/spec-guide/feral-cat-druid.config.json` during drafting
- [x] Run `node tools/analyze-guide-icon-density.mjs --config templates/spec-guide/feral-cat-druid.config.json --policy templates/spec-guide/icon-density-policy.json` while tuning visual density
- [x] Run `node tools/audit-playbook-ability-icons.mjs templates/spec-guide/feral-cat-druid.config.json` after the regular icon-density audit
- [x] Run `node tools/audit-spec-guide.mjs templates/spec-guide/feral-cat-druid.config.json --release`; this automatically enforces icon density first and playbook ability icons second
