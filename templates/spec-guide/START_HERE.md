# Start Here: Complete Spec Guide Workflow

Use the complete wrapper for every new spec guide:

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

1. `CONFIGURATION.md`
2. `ENTITY_LINKS_AND_ICONS.md`
3. `ICON_DENSITY_APPROVAL.md`
4. the generated implementation checklist
5. `README.md` for the full content, color, layout, accessibility, and release standard

Before review:

```powershell
node tools/build-wowhead-tooltips.mjs data/<class>-entities.json assets/<class>-tooltips.js
node tools/audit-spec-guide.mjs templates/spec-guide/my-spec.config.json
npm install --no-save --no-package-lock jsdom@24
node tools/analyze-guide-icon-density.mjs --config templates/spec-guide/my-spec.config.json --policy templates/spec-guide/icon-density-policy.json
node tools/audit-playbook-ability-icons.mjs templates/spec-guide/my-spec.config.json
```

Before release, run one canonical command:

```powershell
node tools/audit-spec-guide.mjs templates/spec-guide/my-spec.config.json --release
```

The release audit first invokes and enforces the rendered complexity-based icon analysis, then runs the non-negotiable playbook ability-icon audit. CI independently repeats that order. The playbook gate checks every production guide config, including an icon-density baseline explicitly documented as `grandfathered`.

A release cannot pass by omitting an icon-density flag or by using one card-heading icon to hide bare ability chips. Every ability/action chip in a `.spec-card` playbook must render its own verified WoW icon. Visible Wowhead mouseovers and icon loading must still be spot-checked in a browser.
