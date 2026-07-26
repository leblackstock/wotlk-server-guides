# Spec Guide Icon-Density Approval

This is the mandatory visual-density standard for new spec guides.

The goal is not to make every guide contain the same number of icons. The goal is to give each guide enough visual anchors for the amount of information and number of decisions it actually contains, without turning the page into an icon mosaic.

The analyzer renders the pages with their local JavaScript before counting, so JavaScript-added icons are included.

## 1. Two separate icon systems

### Contextual icons

Contextual icons explain structure or decisions:

- major section headings
- Quick Start chapter cards
- combat-engine and summary nodes
- playbook cards and ability choices
- talent and glyph groups
- selected gear, consumable, and comparison rows
- server-behavior notes
- raid encounter summaries
- guide, priority, phase, and macro card headings

These are required in proportion to the guide's actual complexity.

### Inline entity icons

Inline entity icons sit beside linked items, spells, talents, glyphs, enchants, recipes, consumables, professions, or skills.

They are optional. Mouseover links remain mandatory, but an icon does not need to accompany every link.

Favicons, logos, images outside `<main>`, talent-calculator contents, and failed images that remove themselves are not counted.

## 2. Why the old fixed range was removed

The first version required 120–150 contextual icons for every six-page guide. That worked as a reaction to the three existing guide families, but it was too rigid.

A mechanically dense progression tank guide can naturally support many decision cards, cooldown groups, swap sets, and encounter assignments. A straightforward damage spec may have fewer meaningful decisions and fewer places where an icon improves navigation.

Forcing both guides to reach the same total would either leave the complex guide under-illustrated or make the simple guide decorate ordinary prose merely to satisfy a number.

The current standard therefore calculates the required range from **icon opportunities**, not from the class or role name and not from a fixed family total.

## 3. Icon-opportunity score

The analyzer counts the actual structures present in the rendered guide and applies these weights:

| Structure | Opportunity points each |
|---|---:|
| Major section | 1.00 |
| Quick Start chapter card | 1.00 |
| Combat-engine or summary node | 0.75 |
| Playbook card | 1.00 |
| Talent or glyph unit | 0.75 |
| Raid encounter group | 1.00 |
| Secondary guide/card heading | 0.50 |
| Server-behavior note | 1.00 |

Longer guides receive a small additional allowance of **0.75 opportunity points per 750 words**. Word count is deliberately a light influence. A long paragraph does not deserve the same icon allowance as several distinct combat decisions.

The score is reported as:

- **Simple:** up to 55 opportunity points
- **Standard:** over 55 through 85
- **Complex:** over 85

These labels describe the guide's rendered structure. They are not manually assigned by class, specialization, role, or reputation.

## 4. Dynamic family budget

The contextual-icon budget is calculated from the opportunity score:

- minimum: 62% of opportunity score, with a six-page floor of 28
- preferred minimum: 75% of opportunity score
- preferred maximum: 105% of opportunity score
- maximum: 125% of opportunity score plus 8
- absolute maximum: 150 contextual icons

Examples:

| Opportunity score | Complexity | Passing range | Preferred range |
|---:|---|---:|---:|
| 45 | Simple | 28–65 | 34–48 |
| 70 | Standard | 44–96 | 53–74 |
| 100 | Complex | 62–133 | 75–105 |

A concise Feral DPS guide with a score near 45 could therefore pass with roughly 30–50 well-placed contextual icons. It would not be required to imitate a progression tank guide.

Contextual density above **24 icons per 1,000 words** fails. Density below **6 per 1,000 words** produces a review note rather than an automatic failure, because structural coverage is the more reliable test.

## 5. Dynamic page budgets

Each page receives its own opportunity score and budget.

For pages under 350 words:

- minimum floor: 2 contextual icons

For longer pages:

- minimum floor: 4 contextual icons

The remainder is calculated from that page's opportunities:

- minimum: 50% of page opportunity score
- preferred: 70–110%
- maximum: 150% plus 3
- absolute maximum: 45 icons on one page

A short Setup page with only a few meaningful groups may need only a handful of icons. A large Playing page containing multiple playbooks and decision engines receives a larger allowance automatically.

No page may hoard more than 45% of the family's contextual icons once the family contains at least 20 contextual icons.

## 6. Coverage matters more than raw count

The analyzer checks coverage only for structures that actually exist.

Required coverage:

- 60% of major sections
- all Quick Start chapter cards that exist
- 65% of combat-engine or summary nodes
- 70% of playbook cards
- 60% of talent and glyph units
- 70% of raid encounter groups
- 55% of secondary card headings
- all server-behavior notes that exist

A guide with no combat-engine diagram does not fail for lacking combat-engine icons. A guide with ten playbook cards must iconize enough of those cards to preserve visual navigation.

Counts and coverage must both pass. Loading thirty icons into one gear table does not compensate for bare playbooks or encounter summaries.

## 7. Concentration safeguards

To prevent number-gaming:

- table icons may not exceed 35% of contextual icons
- unclassified contextual locations may not exceed 15%
- no page may exceed the family concentration limit
- one contextual icon is normally enough for one heading or decision unit
- do not duplicate the same icon twice on the same visual line

## 8. Inline entity-icon budget

Inline icons scale with the number of eligible Wowhead-linked entity mentions.

- preferred maximum: 25% of eligible entity links
- hard maximum: 45% of eligible entity links
- preferred allowance never needs to exceed 120
- hard allowance never exceeds 180
- hard density maximum: 25 per 1,000 words
- no more than 10% may appear inside ordinary paragraphs

Small guides receive a practical allowance of at least 16 preferred and 24 maximum inline icons, even when they contain few links.

Prefer inline icons in:

- compact ability strips
- gear and consumable tables
- short comparison lists
- glyph and enchant rows
- decision callouts

Do not iconize every prose mention. A mouseover link remains useful without adding a picture to every sentence.

`data-entity-icons="dense"` requires both:

- `entityIconMode: "dense"`
- `allowDenseEntityIcons: true`

Dense mode must still pass all calculated limits.

## 9. Per-component rules

- One contextual icon per heading.
- Add an icon when it improves recognition, scanning, or decision grouping.
- Do not add an icon merely because a noun appears in the text.
- A named item or spell may have a mouseover link without an inline icon.
- Avoid icons in source lists, navigation, long paragraphs, or warnings that already have a clear symbol.
- Repeated encounter mechanics may reuse an icon when consistency is useful.
- Verify icon filenames.
- Decorative icons use empty alt text, `aria-hidden="true"`, and a clean failure fallback such as `onerror="this.remove()"`.

## 10. Approval commands

Install the temporary rendered-DOM analyzer when needed:

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

The report shows:

- family and page complexity tiers
- opportunity scores and score breakdowns
- calculated passing and preferred ranges
- contextual and inline counts
- location and coverage results
- concentration failures and review notes

The GitHub Actions workflow runs the same rendered analysis for retained configs with `"enforceIconDensity": true`.

## 11. Existing guides

Protection Paladin, Holy Paladin, and Blood Death Knight supplied the original visual baseline. They are not silently rewritten by this policy.

Future guide families must pass the opportunity-based standard. A deliberate exception requires a pull-request explanation identifying the failed threshold and why the exception improves readability.
