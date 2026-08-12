#!/usr/bin/env node
import fs from "node:fs";
import path from "node:path";
import process from "node:process";
import { validateFresh80Config } from "./lib/fresh-80-policy.mjs";

const root = process.cwd();
const registryFile = path.resolve(root, "data/guide-audiences.json");
const registry = JSON.parse(fs.readFileSync(registryFile, "utf8"));
const errors = [];
const suffixes = {
  quickStart: "pve-guide",
  playing: "playing",
  setup: "setting-up",
  building: "gearing",
  equipping: "gear-targets",
  raiding: "raiding"
};
const requiredFreshMarkers = {
  quickStart: "fresh-80-starting-assumptions",
  setup: "fresh-80-self-contained-talents",
  building: "fresh-80-budget-path",
  equipping: "fresh-80-immediate-targets",
  raiding: "fresh-80-later-progression"
};

if (registry.schemaVersion !== 1) errors.push("data/guide-audiences.json must use schemaVersion 1.");
if (!Array.isArray(registry.families) || registry.families.length === 0) errors.push("The audience registry has no guide families.");

const registeredSlugs = new Set();
for (const family of registry.families || []) {
  const label = family.specName || family.specSlug || "Unknown family";
  if (!family.specSlug || registeredSlugs.has(family.specSlug)) {
    errors.push(`${label}: specSlug is missing or duplicated.`);
    continue;
  }
  registeredSlugs.add(family.specSlug);
  if (!["fresh-80", "specialized-raid"].includes(family.guideAudience)) {
    errors.push(`${label}: guideAudience must be fresh-80 or specialized-raid.`);
  }

  if (family.configFile) {
    const configPath = path.resolve(root, family.configFile);
    if (!fs.existsSync(configPath)) {
      errors.push(`${label}: missing config ${family.configFile}.`);
    } else {
      const config = JSON.parse(fs.readFileSync(configPath, "utf8"));
      if (config.guideAudience !== family.guideAudience) {
        errors.push(`${label}: config audience does not match the registry.`);
      }
      if (family.guideAudience === "fresh-80") {
        validateFresh80Config(config).forEach((error) => errors.push(`${label} config: ${error}`));
      }
    }
  }

  const pages = {};
  for (const [pageKey, suffix] of Object.entries(suffixes)) {
    const relative = `guides/${family.specSlug}-${suffix}.html`;
    const file = path.resolve(root, relative);
    if (!fs.existsSync(file)) {
      errors.push(`${label}: missing ${relative}.`);
      continue;
    }
    const html = fs.readFileSync(file, "utf8");
    pages[pageKey] = html;
    const audiencePattern = new RegExp(`data-guide-audience=["']${family.guideAudience}["']`, "i");
    if (!audiencePattern.test(html)) errors.push(`${relative}: audience attribute does not match ${family.guideAudience}.`);
    if (!/Updated \d{4}-\d{2}-\d{2}/.test(html)) errors.push(`${relative}: missing Updated YYYY-MM-DD footer.`);
  }

  if (family.guideAudience === "fresh-80") {
    for (const [pageKey, marker] of Object.entries(requiredFreshMarkers)) {
      const html = pages[pageKey];
      if (html && !new RegExp(`class=["'][^"']*\\b${marker}\\b`, "i").test(html)) {
        errors.push(`${label} ${pageKey}: missing .${marker}.`);
      }
    }
    if (pages.quickStart && !/normal and heroic dungeons/i.test(pages.quickStart)) {
      errors.push(`${label}: Quick Start must explicitly allow normal and heroic dungeons.`);
    }
    if (pages.setup && /Recommended (?:baseline|shape):[\s\S]{0,220}\b(?:raid|ICC|25[- ]?(?:player|man)|BiS) build\b/i.test(pages.setup)) {
      errors.push(`${label}: the recommended talent baseline is still labeled as a raid-optimized build.`);
    }
    if (pages.building && !/budget|cheaper|temporary/i.test(pages.building)) {
      errors.push(`${label}: Building must put budget or temporary-item options before premium upgrades.`);
    }
    if (pages.equipping && !/normal|heroic|reputation|crafted|BoE|emblem/i.test(pages.equipping)) {
      errors.push(`${label}: Equipping is missing immediate non-raid sources.`);
    }
    if (pages.raiding && !/later progression|not the starting expectation/i.test(pages.raiding)) {
      errors.push(`${label}: Raiding must be labeled as later progression.`);
    }
  } else if (family.guideAudience === "specialized-raid") {
    const landing = pages.quickStart || "";
    if (!family.specializedScope || !landing.includes(family.specializedScope)) {
      errors.push(`${label}: landing page must visibly match specializedScope.`);
    }
    for (const [pageKey, html] of Object.entries(pages)) {
      if (/fresh-80-(?:starting-assumptions|self-contained-talents|budget-path|immediate-targets|later-progression)/i.test(html)) {
        errors.push(`${label} ${pageKey}: specialized guide contains a fresh-80 workflow marker.`);
      }
    }
  }
}

for (const entry of fs.readdirSync(path.resolve(root, "guides"))) {
  const match = entry.match(/^(.*)-pve-guide\.html$/);
  if (match && !registeredSlugs.has(match[1])) errors.push(`Unregistered guide family: ${match[1]}.`);
}

console.log(`Guide audience audit: ${registeredSlugs.size} registered families.`);
errors.forEach((error) => console.error(`  ERROR ${error}`));
console.log(`Result: ${errors.length} error(s).`);
if (errors.length) process.exit(1);
