# Game Entity Links, Mouseovers, and Icons

This workflow is mandatory for every generated spec guide. It exists because a guide can look complete while many items, enchants, recipes, talents, skills, and abilities remain plain text with no WotLK mouseover.

## The rule

Every named game entity used anywhere in the six-page guide family must be entered in the class entity registry before release.

This includes:

- equipment, weapons, armor, rings, trinkets, relics, and tier pieces
- gems, consumables, food, flasks, elixirs, potions, scrolls, and temporary items
- glyphs and recipe items such as Plans, Patterns, Recipes, Formulae, and Designs
- enchants and profession effects, which usually use a WotLK spell ID
- abilities, skills, talents, buffs, debuffs, cooldowns, and set-bonus spells
- canonical names plus every shortened or faction-specific alias displayed by the guide

Do not wait until the visual review. Build the registry while researching each page.

## Registry format

The config points to a shared class registry:

```json
"entityRegistryFile": "data/death-knight-entities.json",
"tooltipFile": "death-knight-tooltips.js"
```

Registry entries use one of three types:

```json
{
  "schemaVersion": 1,
  "className": "Example Class",
  "classSlug": "example-class",
  "items": [
    {
      "id": 12345,
      "names": ["Exact Item Name", "Displayed Alias"],
      "icon": "inv_example_icon",
      "category": "gear"
    }
  ],
  "spells": [
    {
      "id": 67890,
      "names": ["Exact Ability Name"],
      "icon": "spell_example_icon",
      "category": "ability"
    }
  ],
  "skills": [
    {
      "id": 202,
      "names": ["Engineering"],
      "icon": "trade_engineering",
      "category": "profession"
    }
  ]
}
```

The numbers above illustrate the structure only. Never copy example IDs into a real registry. Verify the actual WotLK item or spell page first.

### Type rules

- Gear, gems, consumables, glyph items, and recipe scrolls normally use `items`.
- Abilities, talents, buffs, debuffs, enchants, and profession effects normally use `spells`.
- Professions and Runeforging use `skills` when the verified WotLK page is a `skill=` record.
- Use the entity type shown by the verified WotLK Wowhead URL, not a guess based on the English name.
- IDs must be positive integers. Zero and retail IDs are release failures.
- Store icon filenames without `.jpg`.

## Automatic phrase linking

The generated class tooltip script uses the proven Paladin pattern:

1. It registers every exact name and alias.
2. It decorates existing entity links.
3. It links matching phrases throughout `<main>`, even when the author did not manually wrap them.
4. It avoids anchors, code, macros, buttons, navigation, and other unsafe nesting locations.
5. It loads `https://wow.zamimg.com/js/tooltips.js` automatically.
6. It sets WotLK `data-wowhead` values so links receive real mouseovers.

Marker classes are audit hints, not a requirement for automatic linking:

```html
<span class="item-name">Exact Item Name</span>
<span class="enchant-name">Exact Enchant Name</span>
<span class="recipe-name">Plans: Exact Recipe Name</span>
<span class="ability-name">Exact Ability Name</span>
```

Ordinary prose containing a registered phrase is linked automatically.

## Icons

Use a full icon URL only after verifying the filename:

```html
<img class="spell-icon"
     src="https://wow.zamimg.com/images/wow/icons/large/spell_example_icon.jpg"
     alt=""
     aria-hidden="true"
     onerror="this.remove()">
```

Required icon locations:

- major section headings
- Quick Start chapter cards and combat-engine steps where a clear icon exists
- talent-tree panel
- playbook ability choices
- glyph, cooldown, consumable, and gear-category callouts
- raid encounter summaries

Do not decorate every sentence. Icons should identify an action, category, encounter, or decision point.

### Registry-driven icons

An entity with a verified `icon` may be iconized without duplicating the filename in HTML:

```html
<span class="ability-choice ability-name" data-entity-icon="Death Strike">Death Strike</span>
<h3 data-entity-icon="Death Strike">Death Strike timing</h3>
```

The tooltip script prepends the icon and removes it cleanly if the image fails.

For a deliberately icon-rich guide, opt into compact icons on every linked entity outside headings and source lists:

```html
<body data-entity-icons="dense">
```

Dense mode is intentional, not the default. Use it only when repeated inline icons fit the guide’s visual direction and remain readable on mobile.

## Required workflow

### 1. Generate the guide family

```powershell
node tools/create-complete-spec-guide.mjs templates/spec-guide/my-spec.config.json --dry-run
node tools/create-complete-spec-guide.mjs templates/spec-guide/my-spec.config.json
```

For the first spec of a class, create the class registry and tooltip script. For additional specs, reuse and extend the same class registry.

### 2. Inventory entities page by page

Complete one pass for each page:

- Quick Start
- Playing
- Setup
- Building
- Equipping
- Raiding

For every named entity, record:

- exact displayed name
- aliases used elsewhere in the guide
- WotLK type and ID
- verified icon filename when an icon is appropriate
- source page used for verification

Recipes and enchants are not optional edge cases. They belong in this pass.

### 3. Rebuild the tooltip script

```powershell
node tools/build-wowhead-tooltips.mjs data/death-knight-entities.json assets/death-knight-tooltips.js
```

Do not hand-edit a generated tooltip script. Update the registry and rebuild it.

### 4. Run the audit during drafting

```powershell
node tools/audit-spec-guide.mjs templates/spec-guide/my-spec.config.json
node tools/audit-playbook-ability-icons.mjs templates/spec-guide/my-spec.config.json
```

The audit checks:

- all six pages load the class tooltip script
- the script phrase-links names and loads the Wowhead engine
- marked items, enchants, recipes, glyphs, talents, skills, and abilities exist in the registry
- macro spell names are represented
- requested entity icons have verified filenames
- major section headings and raid summaries have icons
- decorative icons have empty alt text, `aria-hidden`, and a failure fallback
- external links use safe attributes
- Wowhead links use the WotLK path

Warnings are an investigation queue, not decorative confetti.

### 5. Run the release audit

```powershell
node tools/audit-spec-guide.mjs templates/spec-guide/my-spec.config.json --release
```

Release mode also rejects:

- TODO and template placeholders
- an empty entity registry
- placeholder or zero entity IDs

Do not publish until the release audit passes and the visible mouseovers have been spot-checked in a browser.

## Pull request checklist

Every new guide PR must state:

- registry path and tooltip script path
- total verified item and spell entries
- whether phrase linking and Wowhead engine loading were tested
- which icon groups were added
- audit commands and results
- any named entities intentionally left unlinked, with a reason
- any server-specific entries still awaiting a Hellscream tooltip or scripting test
