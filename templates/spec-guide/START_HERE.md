# Start Here: Complete Spec Guide Workflow

First classify the audience:

- For a newly capped level-80 guide, read `NEW_LEVEL_80_GUIDE_WORKFLOW.md` and use the fresh-80 wrapper.
- For a deliberately specialized guide such as a Heroic LK25 playbook, use the complete wrapper below and document that narrower audience explicitly.

Use this command for a new level-80 guide:

```powershell
node tools/create-fresh-80-spec-guide.mjs templates/spec-guide/my-spec.config.json --dry-run
node tools/create-fresh-80-spec-guide.mjs templates/spec-guide/my-spec.config.json
```

Use the complete wrapper for other new spec guides:

```powershell
Copy-Item templates/spec-guide/spec-guide.config.example.json templates/spec-guide/my-spec.config.json
node tools/create-complete-spec-guide.mjs templates/spec-guide/my-spec.config.json --dry-run
node tools/create-complete-spec-guide.mjs templates/spec-guide/my-spec.config.json
```

The generated pages automatically use the shared banner in
`assets/guide-hero.css`. Set `guideNickname` and all six `guideTypes` values in
the config; do not duplicate banner styles in the new spec stylesheet.

Do not use `tools/create-spec-guide.mjs` by itself for a production guide. That compatibility command routes into the same complete production workflow, but `create-complete-spec-guide.mjs` is the canonical entrypoint.

The production generator treats complexity-based icon approval as mandatory. A missing `iconDensityStatus` defaults to `required`, and the generator refuses to create a new guide marked `grandfathered`.

Then follow these documents in order:

1. `NEW_LEVEL_80_GUIDE_WORKFLOW.md` when the audience is newly capped level 80
2. `CONFIGURATION.md`
3. `ENTITY_LINKS_AND_ICONS.md`
4. `ICON_DENSITY_APPROVAL.md`
5. the generated implementation checklist
6. `README.md` for the full content, color, layout, accessibility, and release standard

Before review:

```powershell
node tools/build-wowhead-tooltips.mjs data/<class>-entities.json assets/<class>-tooltips.js
node tools/audit-fresh-80-guide.mjs templates/spec-guide/my-spec.config.json
node tools/audit-spec-guide.mjs templates/spec-guide/my-spec.config.json
npm install --no-save --no-package-lock jsdom@24
node tools/analyze-guide-icon-density.mjs --config templates/spec-guide/my-spec.config.json --policy templates/spec-guide/icon-density-policy.json
node tools/audit-playbook-ability-icons.mjs templates/spec-guide/my-spec.config.json
```

Before release, run one canonical command:

```powershell
node tools/audit-spec-guide.mjs templates/spec-guide/my-spec.config.json --release
```

For a `fresh-80` config, the release audit first enforces the audience policy. It then invokes the rendered complexity-based icon analysis and the non-negotiable playbook ability-icon audit. CI independently repeats the workflow test. The playbook gate checks every production guide config, including an icon-density baseline explicitly documented as `grandfathered`.

A release cannot pass by omitting an icon-density flag or by using one card-heading icon to hide bare ability chips. Every ability/action chip in a `.spec-card` playbook must render its own verified WoW icon. Visible Wowhead mouseovers and icon loading must still be spot-checked in a browser.
