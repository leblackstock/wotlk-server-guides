# Spec Guide Icon Placement Verification and Density Report

This is the mandatory icon-verification standard for new spec guides. Density counts are advisory: they help compare pages, but they never force icons to be added or removed.

The goal is to verify approved icon placements, valid entity IDs, working mouseovers, and required action icons. The density report helps reviewers notice unusual concentration, but human section decisions control the design.

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

These appear only where the shared component or an approved section decision calls for them. No count or ratio creates a placement requirement.

### Inline entity icons

Inline entity icons sit beside linked items, spells, talents, glyphs, enchants, recipes, consumables, professions, or skills.

They are optional. Mouseover links remain mandatory, but an icon does not need to accompany every link.

Favicons, logos, images outside `<main>`, talent-calculator contents, and failed images that remove themselves are not counted.

## 2. Why the old fixed range was removed

The first version required 120–150 contextual icons for every six-page guide. That worked as a reaction to the three existing guide families, but it was too rigid.

A mechanically dense progression tank guide can naturally support many decision cards, cooldown groups, swap sets, and encounter assignments. A straightforward damage spec may have fewer meaningful decisions and fewer places where an icon improves navigation.

Forcing both guides to reach the same total would either leave the complex guide under-illustrated or make the simple guide decorate ordinary prose merely to satisfy a number.

The current report calculates an advisory reference range from **icon opportunities**. It is not a quota, a passing range, or an instruction to decorate content.

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

## 4. Advisory family reference

The contextual-icon budget is calculated from the opportunity score:

- minimum: 62% of opportunity score, with a six-page floor of 28
- preferred minimum: 75% of opportunity score
- preferred maximum: 105% of opportunity score
- maximum: 125% of opportunity score plus 8
- absolute maximum: 150 contextual icons

Examples:

| Opportunity score | Complexity | Advisory range | Preferred reference |
|---:|---|---:|---:|
| 45 | Simple | 28–65 | 34–48 |
| 70 | Standard | 44–96 | 53–74 |
| 100 | Complex | 62–133 | 75–105 |

A concise Feral DPS guide with a score near 45 may naturally land around 30–50 well-placed contextual icons. It is not required to reach that range or imitate a progression tank guide.

Contextual density above **24 icons per 1,000 words** or below **6 per 1,000 words** produces a review note only. Neither value is a release failure.

## 5. Advisory page references

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

A page owning more than 45% of the family's contextual icons receives an advisory review note once the family contains at least 20 contextual icons.

## 6. Coverage is a review signal

The analyzer checks coverage only for structures that actually exist.

Advisory coverage references:

- 60% of major sections
- all Quick Start chapter cards that exist
- 65% of combat-engine or summary nodes
- 70% of playbook cards
- 60% of talent and glyph units
- 70% of raid encounter groups
- 55% of secondary card headings
- all server-behavior notes that exist

A guide with no combat-engine diagram does not receive a combat-engine note. A guide with ten playbook cards may receive a low-coverage note, but the approved per-section design decides the correct placements.

Counts and coverage never determine release approval. Loading thirty icons into one gear table also does not compensate for a missing icon in a specifically required component.

### Playbook ability chips: 100% required

The percentage-based playbook-card coverage above applies to contextual card anchors. It does not permit bare action chips.

The density analyzer reports these mandatory action icons separately and excludes them from the optional contextual/inline report. `audit-playbook-ability-icons.mjs` renders the Playing page with its local tooltip/icon scripts and checks every direct `.spec-playbook-grid .spec-card .ability-strip > .ability-choice`. Every chip must contain its own verified WoW icon. One icon in the card heading, or one icon elsewhere in the action row, does not satisfy this gate.

This gate applies to every production config, including a guide whose overall icon-density baseline is explicitly grandfathered.

## 7. Concentration review signals

The report flags these patterns for human review:

- table icons above 35% of contextual icons
- unclassified contextual locations above 15%
- a page above the family concentration reference
- one contextual icon is normally enough for one heading or decision unit
- do not duplicate the same icon twice on the same visual line

## 8. Inline entity-icon budget

Inline icons scale with the number of eligible Wowhead-linked entity mentions.

- preferred maximum: 25% of eligible entity links
- upper reference: 45% of eligible entity links
- preferred allowance never needs to exceed 120
- hard allowance never exceeds 180
- density reference: 25 per 1,000 words
- paragraph-share reference: 10%

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

Dense mode still requires explicit approval, but calculated counts remain advisory.

## 9. Per-component rules

- One contextual icon per heading.
- Add an icon when it improves recognition, scanning, or decision grouping.
- Do not add an icon merely because a noun appears in the text.
- A named item or spell may have a mouseover link without an inline icon.
- Avoid icons in source lists, navigation, long paragraphs, or warnings that already have a clear symbol.
- Repeated encounter mechanics may reuse an icon when consistency is useful.
- Verify icon filenames.
- Decorative icons use empty alt text, `aria-hidden="true"`, and a clean failure fallback such as `onerror="this.remove()"`.

## 10. Permanent build and release workflow

New production configs use:

```json
"iconDensityStatus": "required",
"iconDensityPolicyFile": "templates/spec-guide/icon-density-policy.json",
"entityIconMode": "selective",
"allowDenseEntityIcons": false
```

The permanent rules are:

- Missing `iconDensityStatus` defaults to `required`.
- The production generator refuses to create a new guide marked `grandfathered`.
- Neither the ordinary draft audit nor the release audit forces an icon count.
- The release audit invokes the rendered analyzer for advisory reporting and verifies explicit placement/mode rules.
- GitHub Actions independently analyzes every retained production config by default.
- A new guide cannot opt out of icon verification by deleting or changing one boolean.
- A future exception requires a deliberate central workflow change in a reviewed pull request, not a self-declared config value.

Install the rendered-DOM dependency when working locally:

```powershell
npm install --no-save --no-package-lock jsdom@24
```

Run the analyzer directly while designing:

```powershell
node tools/analyze-guide-icon-density.mjs `
  --config templates/spec-guide/my-spec.config.json `
  --policy templates/spec-guide/icon-density-policy.json
```

Run the canonical release gate:

```powershell
node tools/audit-spec-guide.mjs templates/spec-guide/my-spec.config.json --release
```

That single release command runs the entity, link, macro, icon-asset, placeholder, and complexity-based rendered icon checks. The report shows:

- family and page complexity tiers
- opportunity scores and score breakdowns
- calculated passing and preferred ranges
- contextual and inline counts
- location and coverage results
- concentration failures and review notes

## 11. Existing guides

Protection Paladin, Holy Paladin, and Blood Death Knight supplied the original visual baseline. Their public pages are not silently rewritten by this policy.

The retained Blood Death Knight config carries the one explicit grandfathered marker because its dense inline-icon pass predates the permanent complexity budget. That exception is documented in the config and is not accepted by the new-guide generator.

Every future guide family defaults to and must pass the opportunity-based standard.
