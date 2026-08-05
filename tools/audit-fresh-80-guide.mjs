#!/usr/bin/env node
import fs from "node:fs";
import path from "node:path";
import process from "node:process";
import { validateFresh80Config } from "./lib/fresh-80-policy.mjs";

const configArg = process.argv.slice(2).find((arg) => !arg.startsWith("--"));
if (!configArg) {
  console.error("Usage: node tools/audit-fresh-80-guide.mjs <config.json>");
  process.exit(1);
}

const root = process.cwd();
const configFile = path.resolve(root, configArg);
const config = JSON.parse(fs.readFileSync(configFile, "utf8"));
const errors = validateFresh80Config(config);
const suffixes = {
  quickStart: "pve-guide",
  playing: "playing",
  setup: "setting-up",
  building: "gearing",
  equipping: "gear-targets",
  raiding: "raiding"
};
const pages = {};

for (const [key, suffix] of Object.entries(suffixes)) {
  const file = path.resolve(root, "guides", `${config.specSlug}-${suffix}.html`);
  if (!fs.existsSync(file)) {
    errors.push(`Missing guide page: guides/${config.specSlug}-${suffix}.html.`);
    continue;
  }
  const html = fs.readFileSync(file, "utf8");
  pages[key] = html;
  if (!/data-guide-audience=["']fresh-80["']/i.test(html)) {
    errors.push(`guides/${config.specSlug}-${suffix}.html: missing data-guide-audience="fresh-80".`);
  }
}

const requiredMarkers = {
  quickStart: "fresh-80-starting-assumptions",
  setup: "fresh-80-self-contained-talents",
  building: "fresh-80-budget-path",
  equipping: "fresh-80-immediate-targets",
  raiding: "fresh-80-later-progression"
};
for (const [key, marker] of Object.entries(requiredMarkers)) {
  if (pages[key] && !new RegExp(`class=["'][^"']*\\b${marker}\\b`, "i").test(pages[key])) {
    errors.push(`The ${key} page is missing the required .${marker} workflow marker.`);
  }
}

const earlyPages = [pages.quickStart, pages.playing, pages.setup, pages.building, pages.equipping].filter(Boolean).join("\n");
if (/recommended baseline:[^<]{0,160}\b(?:raid build|25[- ]?player|25[- ]?man|icc)\b/i.test(earlyPages)) {
  errors.push("The entry-path pages label the recommended baseline as raid-optimized content.");
}
if (/raid supplies|requires? (?:a |the )?(?:blood death knight|enhancement shaman|25[- ]?(?:player|man) raid)/i.test(earlyPages)) {
  errors.push("The entry-path pages require an external raid composition.");
}
if (pages.building && !/budget|cheaper|temporary/i.test(pages.building)) {
  errors.push("The Building page must include a budget or temporary-gear path before premium upgrades.");
}
if (pages.quickStart && !/normal (?:and|or) heroic dungeons|normal or heroic dungeons/i.test(pages.quickStart)) {
  errors.push("The Quick Start must allow normal and heroic dungeon progression before raid readiness.");
}
if (pages.raiding && !/later progression|not the starting expectation|after .*ready/i.test(pages.raiding)) {
  errors.push("The Raiding page must explain that raid content is later progression.");
}

console.log(`Fresh-80 guide audit: ${config.specName}`);
errors.forEach((error) => console.error(`  ERROR ${error}`));
console.log(`Result: ${errors.length} error(s).`);
if (errors.length) process.exit(1);
