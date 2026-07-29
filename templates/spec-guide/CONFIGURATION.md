# Spec Guide Generator Configuration

Use `spec-guide.config.example.json` as the starting point.

## Identity fields

- `className` — display name, such as `Death Knight`
- `classSlug` — class-level filename and body key, such as `death-knight`
- `specName` — full public name, such as `Blood Death Knight`
- `specShortName` — compact label used in copy, such as `Blood DK`
- `guideNickname` — large banner nickname, such as `Tankadin`, `Holy Pally`, or `Blood DK`
- `guideTypes` — the white page-purpose label for each of the six pages
- `specSlug` — public filename stem, such as `blood-death-knight`
- `specKey` — short specialization key used by color tokens, such as `blood`
- `role` — Tank, Healer, Melee DPS, Ranged DPS, or a more precise public label
- `levelLabel` — must be `Level 80+` in the standard banner
- `updatedDate` — optional `YYYY-MM-DD` override; otherwise the generator uses the creation date

All slug and key fields must use lower-case kebab-case.

## Shared banner

Every public page and generated visual specimen uses `assets/guide-hero.css`.
The banner contract is:

1. full spec name, `WotLK 3.3.5`, and `Level 80+` in the metadata line
2. large spec nickname in the spec color
3. large guide type in the universal guide-type color
4. one concise page description
5. jump chips in a separate rail below the banner

Use all six `guideTypes` keys:

```json
"guideTypes": {
  "quickStart": "Quick Start",
  "playing": "Playing Guide",
  "setup": "Setup Guide",
  "building": "Build Guide",
  "equipping": "Gear Guide",
  "raiding": "Raid Tank Guide"
}
```

Guide types may be role-specific when that makes the page clearer, such as
`Raid Healer Guide` or `Heroic LK25 Tank Playbook`.

Do not add icons to the banner or jump-chip rail. To change the white guide-type
text across every guide, edit only `--guide-type-color` near the top of
`assets/guide-hero.css`.

## Shared class assets and entity registry

For the first guide created for a class:

```json
"createClassSharedCss": true,
"createTooltipStarter": true,
"createEntityRegistry": true,
"createTooltipScript": true,
"entityRegistryFile": "data/death-knight-entities.json",
"tooltipFile": "death-knight-tooltips.js"
```

For an additional spec of a class that already has shared CSS, a registry, and a tooltip script:

```json
"createClassSharedCss": false,
"createTooltipStarter": false,
"createEntityRegistry": false,
"createTooltipScript": false,
"entityRegistryFile": "data/death-knight-entities.json",
"tooltipFile": "death-knight-tooltips.js"
```

Then extend the existing class registry and rebuild the shared tooltip script:

```powershell
node tools/build-wowhead-tooltips.mjs data/death-knight-entities.json assets/death-knight-tooltips.js
```

`createTooltipStarter` is still required by the underlying scaffold generator. The complete wrapper immediately replaces that starter with the registry-built phrase linker.

The generator refuses to overwrite existing paths unless `--force` is supplied. Treat `--force` as a demolition lever, not a convenience switch.

## Permanent icon-density release gate

Every new production config uses:

```json
"iconDensityStatus": "required",
"iconDensityPolicyFile": "templates/spec-guide/icon-density-policy.json",
"entityIconMode": "selective",
"allowDenseEntityIcons": false
```

Rules:

- Omitting `iconDensityStatus` still defaults to `required`.
- The complete production generator rejects a new config marked `grandfathered`.
- `entityIconMode: "selective"` is the default for new guides.
- Dense inline icons require `entityIconMode: "dense"` and `allowDenseEntityIcons: true`, and must still pass the calculated limits.
- The complexity-based budget comes from the rendered guide’s actual sections, cards, playbooks, talent/glyph groups, encounter groups, and length. It is not assigned manually by role or class.
- `audit-spec-guide.mjs --release` automatically runs the rendered density analyzer with `--enforce`, then runs `audit-playbook-ability-icons.mjs`.
- CI enforces every retained `*.config.json` by default. It does not depend on an opt-in boolean.
- Playbook ability/action chips are a separate 100% coverage gate. Icon-density grandfathering never exempts them.

`grandfathered` is reserved for an explicitly documented guide that already existed before this workflow became permanent. It must not be copied into a new spec config.

## Entity registry requirements

The class registry is the source of truth for every named game entity used by any spec of that class.

Inventory all of the following while writing:

- gear, weapons, armor, rings, trinkets, relics, and tier pieces
- gems, consumables, food, flasks, elixirs, potions, and temporary items
- glyphs and recipe items such as Plans, Patterns, Recipes, Formulae, and Designs
- enchants and profession effects
- abilities, skills, talents, buffs, debuffs, cooldowns, and set bonuses
- canonical names plus every alias or shortened label displayed by the guide

Registry entries use `items`, `spells`, or `skills` based on the verified WotLK Wowhead entity type. IDs must be positive integers. Icon filenames omit `.jpg`.

See `ENTITY_LINKS_AND_ICONS.md` for the mandatory inventory, build, and audit workflow.

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

Config icon values are Wow icon filenames without `.jpg`.

Example:

```json
"playing": "spell_deathknight_deathstrike"
```

Generated URLs use:

`https://wow.zamimg.com/images/wow/icons/large/<icon>.jpg`

All generated decorative icons use empty alt text, `aria-hidden="true"`, and remove themselves when loading fails.

Entity registry entries may also carry an icon filename. The generated tooltip script can insert those icons into elements using either:

```html
<span class="ability-choice ability-name" data-entity-icon="Exact Ability Name">Exact Ability Name</span>
<h3 data-entity-icon="Exact Ability Name">Ability timing</h3>
```

Do not require every heading or encounter to carry an icon. The rendered complexity analyzer calculates coverage only for structures that actually exist and approves the guide from its opportunity score, per-page budgets, structure coverage, and concentration limits.

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

A normal first-spec run creates 13 files:

- six public guide pages
- one spec stylesheet
- one spec script
- one class-shared stylesheet
- one class entity registry
- one generated class tooltip script
- one internal visual specimen
- one implementation checklist

An additional spec normally creates ten files because it reuses the class-shared stylesheet, registry, and tooltip script.

## Safe workflow

```powershell
Copy-Item templates/spec-guide/spec-guide.config.example.json templates/spec-guide/my-spec.config.json
node tools/create-complete-spec-guide.mjs templates/spec-guide/my-spec.config.json --dry-run
node tools/create-complete-spec-guide.mjs templates/spec-guide/my-spec.config.json
```

After generation:

1. Start with the internal visual specimen.
2. Research and write the six pages.
3. Inventory every named game entity into the class registry.
4. Rebuild the tooltip script.
5. Run the draft audit.
6. Run the standalone icon analyzer while tuning the visual system.
7. Resolve all entity, icon, link, macro, density, coverage, and concentration warnings.
8. Run the release audit. It automatically enforces the complexity-based rendered icon analysis.
9. Add the Guide Hub card only when the guide family is review-ready.

Commands:

```powershell
node tools/build-wowhead-tooltips.mjs data/death-knight-entities.json assets/death-knight-tooltips.js
node tools/audit-spec-guide.mjs templates/spec-guide/my-spec.config.json
npm install --no-save --no-package-lock jsdom@24
node tools/analyze-guide-icon-density.mjs --config templates/spec-guide/my-spec.config.json --policy templates/spec-guide/icon-density-policy.json
node tools/audit-spec-guide.mjs templates/spec-guide/my-spec.config.json --release
```
