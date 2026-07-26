# Start Here: Complete Spec Guide Workflow

Use the complete wrapper for every new spec guide:

```powershell
Copy-Item templates/spec-guide/spec-guide.config.example.json templates/spec-guide/my-spec.config.json
node tools/create-complete-spec-guide.mjs templates/spec-guide/my-spec.config.json --dry-run
node tools/create-complete-spec-guide.mjs templates/spec-guide/my-spec.config.json
```

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
```

Before release, run one canonical command:

```powershell
node tools/audit-spec-guide.mjs templates/spec-guide/my-spec.config.json --release
```

The release audit automatically invokes and enforces the rendered complexity-based icon analysis. CI independently runs the same analyzer for every production guide config unless that exact pre-existing baseline is explicitly documented as `grandfathered`.

A release cannot pass by omitting an icon-density flag. Visible Wowhead mouseovers and a representative spread of contextual and inline icons must still be spot-checked in a browser.
