# Reusable WotLK 3.3.5 Spec Guide Standard

This folder is the canonical template for building a complete class/spec guide family in this repository.

It captures the systems established by the Protection Paladin and Holy Paladin guides: class and specialization color planning, six-page information architecture, icons, mouseover tooltips, embedded talent trees, raid filters, verified links, Hellscream notes, accessibility, mobile behavior, print behavior, and release validation.

Do not begin a new guide by copying one existing spec and replacing nouns. Start from this standard and the generator so every guide shares the same bones without inheriting another spec's assumptions.

## 1. Output of one guide family

Every full spec guide must produce these public pages:

1. `guides/{{SPEC_SLUG}}-pve-guide.html` — Quick Start
2. `guides/{{SPEC_SLUG}}-playing.html` — moment-to-moment play
3. `guides/{{SPEC_SLUG}}-setting-up.html` — talents, glyphs, macros, addons, interface
4. `guides/{{SPEC_SLUG}}-gearing.html` — stat rules, caps, gems, enchants, professions
5. `guides/{{SPEC_SLUG}}-gear-targets.html` — named upgrades and special sets
6. `guides/{{SPEC_SLUG}}-raiding.html` — consumables, assignments, encounter notes

It must also produce:

- `assets/{{SPEC_SLUG}}.css`
- `assets/{{SPEC_SLUG}}.js`
- `assets/{{CLASS_SLUG}}-tooltips.js` or a deliberate extension of an existing class tooltip file
- `internal/{{SPEC_SLUG}}-visual-system.html` with `noindex`
- one Guide Hub card in `index.html`
- new class/spec/mechanic tokens in `assets/guide-color-system.css`

The generator creates safe starter files. Research and final copy remain deliberate work.

## 2. Naming rules

Use lower-case kebab-case filenames.

- Class slug: `death-knight`, `paladin`, `priest`
- Spec slug: include the class when ambiguity is possible, such as `blood-death-knight`, `holy-paladin`, `discipline-priest`
- Page title pattern: `Playing your {{SPEC_NAME}} | WotLK 3.3.5`
- Body attributes:

```html
<body data-guide-class="{{CLASS_SLUG}}" data-guide-spec="{{SPEC_KEY}}">
```

Use the same six navigation labels in the same order:

`Guide Hub · Quick Start · Playing · Setup · Building · Equipping · Raiding`

## 3. Voice and server wording

The pages are unofficial player-made guides for our Hellscream community.

Use:

- “our server”
- “the server”
- “this server”
- “Needs Hellscream test”
- “Verify the live tooltip and source”

Do not use “your server.”

Separate these categories clearly:

- standard WotLK 3.3.5 behavior
- confirmed Hellscream behavior
- suspected or untested private-server behavior

Never silently convert an uncertain interaction into a confident instruction. Put uncertainty in a restrained warning or collapsed Hellscream test note.

## 4. Information architecture

### Quick Start

The Quick Start is a compressed operating manual, not a miniature encyclopedia.

Required sections:

- three summary cards for the most important readiness, rotation/priority, assignment, resource, or gearing rules
- one larger “engine” or “combat loop” card
- Hellscream behavior note
- before-pull checklist
- first gearing rule
- five chapter cards linking to the rest of the guide
- source and verification section

A reader should understand the spec's basic job in approximately two minutes.

### Playing

Explain the actual decision system.

Required sections:

- core rotation, priority, healing engine, or resource loop
- preparation and maintenance effects
- focused playbook cards for common situations
- a verified WoW icon inside every ability/action chip in those playbook cards
- movement and target-switch recovery
- cooldowns and utility
- mistakes to avoid
- sources

Do not present a fake fixed rotation when the spec is priority-based. Do not hide encounter-critical exceptions inside prose soup.

### Setup

Required sections:

- complete baseline talent build
- embedded Wowhead WotLK talent calculator
- direct fallback calculator link
- core talents, subspec, and flexible points
- major and minor glyph table
- practical macros with exact 3.3.5 English spell names
- addon and interface recommendations
- role-specific click-casting or keybind guidance when useful
- sources

Talent tree markup must follow this pattern:

```html
<div class="guide-box" style="margin-top:12px">
  <div class="icon-heading">
    <img class="title-icon" src="https://wow.zamimg.com/images/wow/icons/large/{{TALENT_ICON}}.jpg" alt="" aria-hidden="true" onerror="this.remove()">
    <div>
      <span class="summary-label">Fully filled baseline</span>
      <h3 style="margin:0">{{TALENT_POINTS}} {{BUILD_NAME}}</h3>
    </div>
  </div>
  <p class="mini-note">{{BUILD_SUMMARY}}</p>
  <div class="talent-embed-wrap">
    <iframe class="talent-embed" title="Fully filled {{TALENT_POINTS}} {{SPEC_NAME}} talent tree" loading="lazy" src="https://www.wowhead.com/wotlk/talent-calc/embed/{{WOWHEAD_TALENT_PATH}}"></iframe>
  </div>
  <p class="talent-fallback">Tree not loading? <a href="https://www.wowhead.com/wotlk/talent-calc/{{WOWHEAD_TALENT_PATH}}" target="_blank" rel="noopener">Open the complete build in the Wowhead calculator.</a></p>
</div>
```

Never link only to a general talent article when a filled calculator can be embedded.

### Building

Required sections:

- stat table with practical priority and corrections
- exact caps or breakpoints with assumptions stated
- gearing path by stage
- gem table
- enchant table
- profession table
- special encounter exceptions
- sources

A cap must state what it caps, the buffs assumed, and whether it is a floor, soft cap, or hard cap. Avoid orphan numbers.

### Equipping

Required sections:

- first purchases and farms
- fresh-80 and crafted targets
- emblem and tier priorities
- ToC/ToGC targets
- ICC targets
- Ruby Sanctum targets when relevant
- trinket, weapon, relic, and special-purpose sets
- “do not vendor yet” guidance where alternate gear matters
- sources

Named items should be linked when an authoritative item ID is known.

Preferred Hellscream item link:

```html
<a class="item-name q-epic" href="https://www.hellscreamwow.com/item/1/{{ITEM_ID}}" target="_blank" rel="noopener">{{ITEM_NAME}}</a>
```

Use Wowhead WotLK links in the sources section and when Hellscream does not expose a useful record.

Do not invent item IDs. Verify item name, difficulty, raid size, boss, faction variant, heroic/normal state, and currency before publishing.

### Raiding

Required sections:

- Hellscream-wide raid caveats, including removed ICC buff where applicable
- consumables
- assignment rules
- encounter notes
- raid-size filter: All / 10 / 25
- difficulty filter: All / Normal / Heroic
- role or assignment filter suited to the spec
- exact encounter roles instead of generic MT/OT when useful
- “Needs Hellscream test” labels for uncertain scripting
- sources

Encounter notes are spec responsibilities, not complete raid guides.

Each note should answer:

- Who or what is my assignment?
- What must be maintained?
- What damage or mechanic is coming?
- Which cooldown, dispel, movement tool, or target swap matters?
- What differs by 10/25 or Normal/Heroic?

## 5. Color system

Color is semantic, not decorative confetti.

Every guide uses four layers:

1. **Class identity** — stable across every spec of the class
2. **Spec accent** — active specialization, selected controls, technical emphasis
3. **Mechanic colors** — two to four named concepts used repeatedly in diagrams and playbooks
4. **Status colors** — fixed success, warning, danger, and info colors shared across the site

Add named tokens to `assets/guide-color-system.css`. Do not scatter raw hex values through page HTML.

Minimum token plan:

```css
body[data-guide-class="{{CLASS_SLUG}}"] {
  --class-accent: {{CLASS_ACCENT}};
  --class-accent-soft: {{CLASS_ACCENT_SOFT}};
  --class-accent-deep: {{CLASS_ACCENT_DEEP}};
  --class-accent-rgb: {{CLASS_ACCENT_RGB}};
}

body[data-guide-spec="{{SPEC_KEY}}"] {
  --theme-accent: {{SPEC_ACCENT}};
  --theme-accent-soft: {{SPEC_ACCENT_SOFT}};
  --theme-accent-deep: {{SPEC_ACCENT_DEEP}};
  --theme-accent-rgb: {{SPEC_ACCENT_RGB}};
}

:root {
  --mechanic-{{MECHANIC_1}}: {{MECHANIC_1_COLOR}};
  --mechanic-{{MECHANIC_1}}-soft: {{MECHANIC_1_SOFT}};
  --mechanic-{{MECHANIC_1}}-deep: {{MECHANIC_1_DEEP}};
  --mechanic-{{MECHANIC_1}}-rgb: {{MECHANIC_1_RGB}};
}
```

Rules:

- Class color frames the page.
- Spec color owns active navigation, filters, selected cards, and chapter emphasis.
- Mechanic colors identify concepts consistently across pages.
- Warning red/yellow must not be repurposed as spec decoration.
- Color must never be the only way information is communicated.
- Keep saturation restrained so icons and text remain readable.

Document the palette in the internal visual-system page before polishing all six public pages.

## 6. Icons

Use Wrath-style game icons from:

`https://wow.zamimg.com/images/wow/icons/large/{{ICON_NAME}}.jpg`

Every image must fail quietly:

```html
<img class="spell-icon" src="..." alt="" aria-hidden="true" onerror="this.remove()">
```

Icon hierarchy:

- `.spell-icon` — 32×32, major section or important spell chip
- `.title-icon` — 30×30, panel and card heading
- `.item-icon` — 28×28, item/glyph/tool table entry
- `.ability-icon` — 26×26, compact abilities and notes
- raid summary icon — approximately 26×26

Use icons for:

- major section headings
- chapter cards
- rotation or priority strips
- maintenance/resource engine steps
- glyph and cooldown tables
- raid encounter summaries
- important consumable or equipment categories

Do not place an icon beside every sentence. The page should look like a guide, not a bag exploded in Dalaran.

## 7. Tooltips and links

Every spell, talent, glyph, and named item that benefits from identification should have a valid mouseover or click target.

Tooltip script requirements:

- map normalized visible names to verified spell or item IDs
- do not rewrite existing links
- skip code, buttons, headings where tooltip insertion would damage semantics
- use the WotLK endpoint, not Retail
- support keyboard focus on generated links
- avoid duplicate nested anchors

Source links must use:

```html
target="_blank" rel="noopener"
```

Link standards:

- Wowhead WotLK for spell, talent, glyph, item, and guide references
- Hellscream item pages for server-facing named equipment when IDs are known
- direct talent calculator URL in addition to the embedded calculator
- no shortened URLs
- no generic search-result links
- no links to unrelated expansion versions

## 8. Filters and focused cards

Raid filters must be accessible buttons with `aria-pressed`, not decorative tags pretending to be controls.

Filtering state should be explicit:

```js
const state = { size: "all", difficulty: "all", role: "all" };
```

After filtering:

- hide nonmatching notes
- hide encounters with zero visible notes
- show a live count in an `aria-live` status line
- show a useful empty-state message

Focused playbook cards must support click, Enter, and Space. Clicking the selected card again restores the full grid.

## 9. Accessibility, mobile, and print

Required:

- semantic headings in order
- visible keyboard focus
- minimum comfortable touch targets
- meaningful `aria-label` on filters and interactive cards
- decorative icons use empty alt and `aria-hidden="true"`
- tables wrapped in horizontally scrollable containers
- no information conveyed by color alone
- mobile single-column layouts
- print removes site navigation and decorative backgrounds
- internal visual specimen uses `noindex, nofollow`

Test at approximately:

- 360px phone width
- 680px breakpoint
- 900–1000px tablet/small desktop
- full desktop
- black-and-white print preview

## 10. Research and factual verification

Before publishing a spec guide, verify:

- patch 3.3.5 spell behavior
- talent ranks and interactions
- glyph text and item IDs
- exact talent calculator point total
- stat conversions, caps, and raid-buff assumptions
- macros on an English 3.3.5 client
- item names, IDs, sources, raid size, and difficulty
- encounter differences for 10/25 and Normal/Heroic
- Hellscream custom or uncertain behavior

Use multiple authoritative references for encounter mechanics. Preserve uncertainty instead of averaging conflicting claims into a confident sentence.

For each page, include a compact “Sources and verification” section. Sources support the guide but do not replace clear original explanation.

## 11. Generator usage

1. Copy the example config:

```powershell
Copy-Item templates/spec-guide/spec-guide.config.example.json templates/spec-guide/my-spec.config.json
```

2. Edit every placeholder and icon mapping.

3. Run:

```powershell
node tools/create-spec-guide.mjs templates/spec-guide/my-spec.config.json
```

4. The generator creates the six guide pages, spec CSS/JS, class tooltip starter, internal visual specimen, and an implementation checklist.

5. Fill the research placeholders, add color tokens to the central color sheet, update the Guide Hub, then validate.

The generator refuses to overwrite files unless `--force` is supplied.

## 12. Validation checklist

### Structure

- [ ] Six public pages exist.
- [ ] Navigation is identical across all six pages.
- [ ] Correct page has `aria-current="page"`.
- [ ] Every jump link resolves.
- [ ] No duplicate HTML IDs.
- [ ] Previous/next pager links resolve.

### Visual system

- [ ] Class and spec colors are documented.
- [ ] Mechanic colors have names and defined jobs.
- [ ] No status color is reused as decoration.
- [ ] Icons follow the size hierarchy.
- [ ] Missing icons remove themselves cleanly.
- [ ] Mobile and print views remain readable.

### Content

- [ ] Quick Start can be understood in roughly two minutes.
- [ ] Playing explains decisions, not only buttons.
- [ ] Setup contains a filled talent-tree embed and fallback.
- [ ] Building states cap assumptions.
- [ ] Equipping verifies every named source.
- [ ] Raiding separates 10/25 and Normal/Heroic differences.
- [ ] Uncertain behavior is marked for Hellscream testing.

### Links and scripts

- [ ] Tooltip IDs are verified.
- [ ] Item IDs are verified.
- [ ] External links use `noopener`.
- [ ] No Retail or wrong-expansion links slipped in.
- [ ] JavaScript passes `node --check`.
- [ ] Filter controls work with keyboard input.
- [ ] Cache-busting query strings are updated.

### Release

- [ ] Guide Hub card added.
- [ ] Changed-file scope reviewed.
- [ ] Existing guides remain untouched unless intentionally sharing an asset.
- [ ] Branch is not behind `main`.
- [ ] Pull request explains standard behavior versus Hellscream uncertainty.
- [ ] Live GitHub Pages checked after merge.

## 13. Definition of done

A guide is complete when a new level-80 player can:

- understand the spec's job
- set up a valid talent build and glyphs
- bind and recognize the important abilities
- follow the correct combat decision system
- build an initial gear set
- identify realistic upgrades
- prepare consumables
- understand their encounter responsibility
- distinguish confirmed mechanics from server-dependent behavior

Polished colors without correct mechanics are not done. Accurate mechanics buried in an unreadable wall are also not done. The standard requires both.
