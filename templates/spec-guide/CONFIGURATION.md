# Spec Guide Generator Configuration

Use `spec-guide.config.example.json` as the starting point.

## Identity fields

- `className` — display name, such as `Death Knight`
- `classSlug` — class-level filename and body key, such as `death-knight`
- `specName` — full public name, such as `Blood Death Knight`
- `specShortName` — compact label used in copy, such as `Blood DK`
- `specSlug` — public filename stem, such as `blood-death-knight`
- `specKey` — short specialization key used by color tokens, such as `blood`
- `role` — Tank, Healer, Melee DPS, Ranged DPS, or a more precise public label
- `levelLabel` — normally `Level 80+`

All slug and key fields must use lower-case kebab-case.

## Shared class assets

For the first guide created for a class:

```json
"createClassSharedCss": true,
"createTooltipStarter": true,
"tooltipFile": "death-knight-tooltips.js"
```

For an additional spec of a class that already has shared CSS and tooltips:

```json
"createClassSharedCss": false,
"createTooltipStarter": false,
"tooltipFile": "death-knight-tooltips.js"
```

Then extend the existing class tooltip file deliberately instead of overwriting it.

The generator refuses to overwrite existing paths unless `--force` is supplied. Treat `--force` as a demolition lever, not a convenience switch.

## Cache key

Set `cacheKey` to the intended release date or version token. Update it again after final CSS or JavaScript changes.

Example:

```json
"cacheKey": "20260725"
```

## Color fields

Class colors remain stable across all specs of a class. Spec colors identify the active specialization. Mechanic colors identify repeated concepts such as resources, direct healing, maintenance, mitigation, threat, combo points, diseases, pets, or proc states.

Every color needs:

- main hex
- soft hex for readable text and highlights
- deep hex for gradients and dark surfaces
- comma-separated RGB values for alpha backgrounds

The generator creates CSS that references central tokens. It does not edit `assets/guide-color-system.css` automatically because the palette must be reviewed in the context of the entire site.

## Mechanics

Use two to four mechanics. Each object requires:

- `key` — short kebab-case token
- `label` — reader-facing name
- `color`, `soft`, `deep`, and `rgb`
- `use` — the exact semantic job of the color

Do not create separate colors for every ability school. Choose concepts that recur across several pages.

## Icons

Icon values are Wow icon filenames without `.jpg`.

Example:

```json
"playing": "spell_deathknight_deathstrike"
```

Generated URLs use:

`https://wow.zamimg.com/images/wow/icons/large/<icon>.jpg`

All generated icons remove themselves when loading fails.

## Talent build

`wowheadPath` is everything after `/wotlk/talent-calc/` in a filled calculator URL.

Example full URL:

`https://www.wowhead.com/wotlk/talent-calc/death-knight/005512153330030320102013-305050500002-02`

Config value:

```json
"wowheadPath": "death-knight/005512153330030320102013-305050500002-02"
```

Verify that the visible total matches `points`. The generator embeds the tree and creates the direct fallback link automatically.

## Raid role filters

Choose labels that match the spec's actual responsibilities.

Good examples:

- Main tank, Add tank, Keleseth tank, Abomination Driver
- Tank healer, Beacon split, Raid support, Utility / dispel
- Single target, Cleave, Interrupt, Special assignment
- Ranged stack, Portal team, Orb control, Execute phase

Avoid generic labels when the encounter role can be named precisely.

## Generated files

A normal first-spec run creates 12 files:

- six public guide pages
- one spec stylesheet
- one spec script
- one class-shared stylesheet
- one class tooltip starter
- one internal visual specimen
- one implementation checklist

An additional spec normally creates 10 files because it reuses the class-shared stylesheet and tooltip file.

## Safe workflow

```powershell
Copy-Item templates/spec-guide/spec-guide.config.example.json templates/spec-guide/my-spec.config.json
node tools/create-spec-guide.mjs templates/spec-guide/my-spec.config.json --dry-run
node tools/create-spec-guide.mjs templates/spec-guide/my-spec.config.json
```

After generation, start with the internal visual specimen and implementation checklist. Do not add the Guide Hub card until the research placeholders are removed and the guide family is ready for review.
