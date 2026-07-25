#!/usr/bin/env node
import fs from "node:fs";
import path from "node:path";
import process from "node:process";
import { spawnSync } from "node:child_process";
import { buildTooltipScript, createEmptyRegistry, loadRegistry } from "./lib/wowhead-entities.mjs";

const args = process.argv.slice(2);
const dryRun = args.includes("--dry-run");
const configArg = args.find((arg) => !arg.startsWith("--"));
if (!configArg) {
  console.error("Usage: node tools/create-complete-spec-guide.mjs <config.json> [--force] [--dry-run]");
  process.exit(1);
}

const root = process.cwd();
const configFile = path.resolve(root, configArg);
const config = JSON.parse(fs.readFileSync(configFile, "utf8"));
const registryFile = config.entityRegistryFile || `data/${config.classSlug}-entities.json`;
const tooltipFile = config.tooltipFile || `${config.classSlug}-tooltips.js`;
const registryPath = path.resolve(root, registryFile);
const tooltipPath = path.resolve(root, "assets", tooltipFile);
const checklistPath = path.resolve(root, "internal", `${config.specSlug}-implementation-checklist.md`);

const generator = spawnSync(process.execPath, [path.resolve(root, "tools/create-spec-guide-scaffold.mjs"), ...args], {
  cwd: root,
  stdio: "inherit"
});
if (generator.status !== 0) process.exit(generator.status ?? 1);

if (dryRun) {
  if (!fs.existsSync(registryPath)) console.log(`[dry-run] ${registryFile}`);
  console.log(`[dry-run] rebuild assets/${tooltipFile} from ${registryFile}`);
  console.log(`[dry-run] extend internal/${config.specSlug}-implementation-checklist.md with entity audit gates`);
  process.exit(0);
}

if (!fs.existsSync(registryPath)) {
  if (config.createEntityRegistry === false) {
    throw new Error(`Missing shared entity registry: ${registryFile}`);
  }
  fs.mkdirSync(path.dirname(registryPath), { recursive: true });
  fs.writeFileSync(registryPath, `${JSON.stringify(createEmptyRegistry(config), null, 2)}\n`, "utf8");
  console.log(`Wrote ${registryFile}`);
}

const registry = loadRegistry(registryPath);
fs.mkdirSync(path.dirname(tooltipPath), { recursive: true });
fs.writeFileSync(tooltipPath, buildTooltipScript(registry, { classSlug: config.classSlug }), "utf8");
console.log(`Rebuilt assets/${tooltipFile} from ${registryFile}`);

const entityChecklist = `

## Mandatory game-entity links and icons
- [ ] Inventory every named item, enchant, recipe, glyph, gem, consumable, skill, talent, and ability across all six pages
- [ ] Verify every WotLK item/spell ID, displayed alias, source, and appropriate icon filename
- [ ] Add all verified entities to ${registryFile}
- [ ] Rebuild assets/${tooltipFile} with \`node tools/build-wowhead-tooltips.mjs ${registryFile} assets/${tooltipFile}\`
- [ ] Confirm registered phrases link in ordinary prose without manual wrappers
- [ ] Confirm Wowhead's WotLK tooltip engine loads and mouseovers work
- [ ] Add icons to major headings, talent panels, playbook choices, gear/consumable callouts, and raid summaries where appropriate
- [ ] Run \`node tools/audit-spec-guide.mjs ${path.relative(root, configFile).replaceAll(path.sep, "/")}\`
- [ ] Run the same audit with \`--release\` before final review
`;
if (fs.existsSync(checklistPath)) {
  const current = fs.readFileSync(checklistPath, "utf8");
  if (!current.includes("## Mandatory game-entity links and icons")) {
    fs.writeFileSync(checklistPath, `${current.trimEnd()}${entityChecklist}\n`, "utf8");
    console.log(`Extended ${path.relative(root, checklistPath).replaceAll(path.sep, "/")}`);
  }
}
