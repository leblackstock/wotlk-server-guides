# Spec Guide Icon-Density Approval

This is the mandatory visual-density standard for every new six-page spec guide.

It was derived from the rendered pages of the live Protection Paladin, Holy Paladin, and Blood Death Knight guides. The analyzer executes each guide's local JavaScript before counting, so JavaScript-added icons are included.

## 1. What is counted

Icons are split into two different systems.

### Contextual icons

These explain page structure or decisions:

- major section headings
- Quick Start chapter cards
- combat-engine and summary cards
- playbook headers and ability choices
- talent and glyph panels
- selected table rows and callouts
- the Hellscream server note
- raid encounter summaries

These are required for approval.

### Inline entity icons

These are small icons inserted beside linked items, spells, talents, glyphs, enchants, recipes, consumables, professions, or skills.

They are optional. Mouseover links are mandatory, but an icon does not need to accompany every link. Dense inline icons are measured separately so hundreds of repeated item or spell icons cannot disguise weak page structure.

Favicons, logos, images outside `<main>`, talent-calculator contents, and failed images that remove themselves are not counted.

## 2. Rendered baseline

| Guide family | Words | Contextual | Inline entity | Total | Contextual per 1,000 words |
|---|---:|---:|---:|---:|---:|
| Protection Paladin | 9,067 | 122 | 0 | 122 | 13.5 |
| Holy Paladin | 4,883 | 112 | 0 | 112 | 22.9 |
| Blood Death Knight | 7,870 | 142 | 610 | 752 | 18.0 |

### What the three guides teach us

Protection has a reasonable family total, but the distribution is lopsided. Its Playing page contains 87 contextual icons while Building contains none. A large total alone therefore cannot earn approval.

Holy has the lowest contextual total, but it distributes icons across headings, healing-engine steps, playbooks, talents, glyphs, tables, professions, server notes, and raid summaries. It is the best placement model, although its Equipping page is too sparse for the new standard.

Blood has the strongest contextual page-to-page coverage at 142 contextual icons. Its additional 610 dense inline icons make 752 total icons, which is intentionally treated as the high-water warning rather than the target.

The future standard therefore uses the Holy-to-Blood contextual range and a separate, much smaller inline budget.

## 3. Family approval range

A full six-page guide must contain:

- **120 to 150 contextual icons**
- **125 to 140 contextual icons preferred**
- **15 to 23 contextual icons per 1,000 words**
- **17 to 21 per 1,000 words preferred**

No page may contain more than **38%** of the family's contextual icons.

This prevents both failure modes:

- a guide with a few lonely icons scattered through otherwise bare pages
- a guide that pours most of its icons into one playbook or table

## 4. Page budgets

| Page | Required contextual icons |
|---|---:|
| Quick Start | 15–30 |
| Playing | 24–45 |
| Setup | 20–35 |
| Building | 15–30 |
| Equipping | 12–25 |
| Raiding | 15–30 |

A page may not borrow another page's icon allowance. For example, an overloaded Playing page cannot compensate for an empty Building or Equipping page.

## 5. Placement requirements

Across the family, contextual icons must fall within these ranges:

| Placement | Required range |
|---|---:|
| Major section headings | 12–45 |
| Quick Start chapter cards | exactly 5 |
| Combat-engine and summary areas | 6–14 |
| Playbooks and action choices | 15–36 |
| Talents and glyphs | 8–18 |
| Selected table rows | 0–30 |
| Hellscream server notes | 1–3 |
| Raid encounter summaries | 6–24 |
| Guide, priority, phase, and macro card headings | 8–36 |
| Other contextual locations | no more than 10 |

Minimum coverage is also required:

- 65% of major sections have an icon
- all five Quick Start chapter cards have an icon
- 75% of combat-engine or summary nodes have an icon
- 75% of playbook cards have at least one contextual icon
- 75% of raid encounter summaries have an icon

Counts and coverage must both pass. Five copies of one icon in an unrelated table do not satisfy five missing encounter icons.

## 6. Inline entity-icon budget

Inline icons remain optional and default to selective placement.

When inline entity icons are used:

- preferred maximum: **140 across the family**
- hard maximum: **180 across the family**
- hard density maximum: **25 per 1,000 words**
- no more than **10%** of inline icons may appear inside ordinary paragraphs

Prefer inline icons in:

- ability strips
- gear and consumable tables
- short comparison lists
- glyph and enchant rows
- compact decision callouts

Do not iconize every ordinary prose mention. The mouseover link remains useful without turning each sentence into a row of postage stamps.

The `data-entity-icons="dense"` mode requires explicit reviewer approval and must still pass these limits. Selective markers such as `.iconize-entity` and `data-entity-icon` are the default.

## 7. Per-component rules

- One contextual icon per heading.
- A card heading and its ability strip may each have an icon, but do not duplicate the same icon twice in the same visual line.
- Use one icon for a category or decision point, not one for every sentence.
- A named item or spell may have a mouseover link without an inline icon.
- Do not add icons to source lists, navigation, long paragraphs, warnings that already have a clear symbol, or decorative filler.
- Repeated encounter mechanics may reuse an icon when the repeated visual language is helpful.
- Icons still require verified filenames, empty decorative alt text, `aria-hidden="true"`, and `onerror="this.remove()"`.

## 8. Approval commands

Install the temporary DOM analyzer when needed:

```powershell
npm install --no-save --no-package-lock jsdom@24
```

Analyze one guide family:

```powershell
node tools/analyze-guide-icon-density.mjs `
  --config templates/spec-guide/my-spec.config.json `
  --policy templates/spec-guide/icon-density-policy.json
```

Enforce approval before release:

```powershell
node tools/analyze-guide-icon-density.mjs `
  --config templates/spec-guide/my-spec.config.json `
  --policy templates/spec-guide/icon-density-policy.json `
  --enforce
```

The GitHub Actions icon-density workflow runs the same rendered analysis for every retained config with `"enforceIconDensity": true`.

## 9. Grandfathered guides

Protection, Holy, and Blood supplied the baseline. They are not silently rewritten by this policy.

Future guide families must meet the balanced standard. A deliberate exception requires an explanation in the pull request that identifies the page, the failed threshold, and the visual reason the exception improves readability.
