# Start Here: Complete Spec Guide Workflow

Use the complete wrapper for every new spec guide:

```powershell
Copy-Item templates/spec-guide/spec-guide.config.example.json templates/spec-guide/my-spec.config.json
node tools/create-complete-spec-guide.mjs templates/spec-guide/my-spec.config.json --dry-run
node tools/create-complete-spec-guide.mjs templates/spec-guide/my-spec.config.json
```

Do not use `tools/create-spec-guide.mjs` by itself for a production guide. That command creates the structural scaffold, but it does not create the verified class entity registry, rebuild the phrase-linking tooltip script, or add the mandatory entity and icon-density audit gates.

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

Before release:

```powershell
node tools/audit-spec-guide.mjs templates/spec-guide/my-spec.config.json --release
node tools/analyze-guide-icon-density.mjs --config templates/spec-guide/my-spec.config.json --policy templates/spec-guide/icon-density-policy.json --enforce
```

Both release audits must pass. The visible Wowhead mouseovers and a representative spread of contextual and inline icons must still be spot-checked in a browser.
