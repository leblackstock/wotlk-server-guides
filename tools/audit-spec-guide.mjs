#!/usr/bin/env node
import fs from "node:fs";
import path from "node:path";
import process from "node:process";
import { spawnSync } from "node:child_process";
import { loadRegistry, registryEntities, registryNameMap } from "./lib/wowhead-entities.mjs";

const args = process.argv.slice(2);
const release = args.includes("--release");
const configArg = args.find((arg) => !arg.startsWith("--"));
if (!configArg) {
  console.error("Usage: node tools/audit-spec-guide.mjs <config.json> [--release]");
  process.exit(1);
}

const root = process.cwd();
const configFile = path.resolve(root, configArg);
const config = JSON.parse(fs.readFileSync(configFile, "utf8"));
const registryPath = path.resolve(root, config.entityRegistryFile || `data/${config.classSlug}-entities.json`);
const tooltipFile = config.tooltipFile || `${config.classSlug}-tooltips.js`;
const tooltipPath = path.resolve(root, "assets", tooltipFile);
const iconDensityStatus = config.iconDensityStatus || "required";
const iconDensityPolicyFile = config.iconDensityPolicyFile || "templates/spec-guide/icon-density-policy.json";
const registry = loadRegistry(registryPath);
const entityMap = registryNameMap(registry);
const entities = registryEntities(registry);
const errors = [];
const warnings = [];
const notes = [];

const pages = [
  `${config.specSlug}-pve-guide.html`,
  `${config.specSlug}-playing.html`,
  `${config.specSlug}-setting-up.html`,
  `${config.specSlug}-gearing.html`,
  `${config.specSlug}-gear-targets.html`,
  `${config.specSlug}-raiding.html`
].map((file) => path.join(root, "guides", file));

function rel(file) {
  return path.relative(root, file).replaceAll(path.sep, "/");
}

function decodeHtml(value) {
  return value
    .replaceAll("&amp;", "&")
    .replaceAll("&quot;", '"')
    .replaceAll("&#39;", "'")
    .replaceAll("&lt;", "<")
    .replaceAll("&gt;", ">");
}

function stripTags(value) {
  return decodeHtml(value.replace(/<[^>]*>/g, " ").replace(/\s+/g, " ").trim());
}

function attr(attrs, name) {
  const match = attrs.match(new RegExp(`\\b${name}=(?:"([^"]*)"|'([^']*)')`, "i"));
  return match ? (match[1] ?? match[2] ?? "") : "";
}

function mapped(name) {
  return entityMap.get(String(name).trim().toLowerCase());
}

function isPlaceholder(name, attrs = "") {
  return /\bTODO\b/i.test(name) || /data-template-placeholder/i.test(attrs);
}

function inspectMarkers(html, file) {
  const classes = [
    "game-entity", "item-name", "recipe-name", "consumable-name", "gem-name",
    "spell-name", "ability-name", "skill-name", "talent-name", "glyph-name", "enchant-name"
  ].join("|");
  const marker = new RegExp(`<([a-z0-9]+)\\b([^>]*\\bclass=(?:"[^"]*(?:${classes})[^"]*"|'[^']*(?:${classes})[^']*')[^>]*)>([\\s\\S]*?)<\\/\\1>`, "gi");
  let match;
  while ((match = marker.exec(html))) {
    const attrs = match[2];
    const explicit = attr(attrs, "data-entity-name");
    const name = explicit || stripTags(match[3]);
    if (!name || isPlaceholder(name, attrs)) continue;
    if (!mapped(name)) errors.push(`${rel(file)}: marked game entity "${name}" is missing from ${rel(registryPath)}.`);
  }

  const iconRequest = /\bdata-entity-icon=(?:"([^"]+)"|'([^']+)')/gi;
  while ((match = iconRequest.exec(html))) {
    const name = decodeHtml(match[1] ?? match[2] ?? "").trim();
    if (isPlaceholder(name)) continue;
    const entity = mapped(name);
    if (!entity) errors.push(`${rel(file)}: data-entity-icon="${name}" is not in the entity registry.`);
    else if (!entity.icon) errors.push(`${rel(file)}: "${name}" requests an icon but its registry entry has no icon filename.`);
  }
}

function inspectMacros(html, file) {
  const codeBlocks = [...html.matchAll(/<code\b[^>]*>([\s\S]*?)<\/code>/gi)].map((match) => decodeHtml(match[1].replace(/<br\s*\/?\s*>/gi, "\n")));
  for (const code of codeBlocks) {
    const candidates = [];
    for (const match of code.matchAll(/#showtooltip(?:\s+([^\r\n<]+))?/gi)) if (match[1]) candidates.push(match[1].trim());
    for (const match of code.matchAll(/^\s*\/cast(?:sequence)?\s+(?:reset=[^\s]+\s+)?(?:\[[^\]]*\]\s*)*([^;\r\n]+)/gim)) {
      const value = match[1].split(",")[0].trim();
      if (value) candidates.push(value);
    }
    for (const candidate of candidates) {
      const cleaned = candidate.replace(/^!/, "").replace(/\(Rank \d+\)$/i, "").trim();
      if (!cleaned || /TODO|null|13|14/i.test(cleaned)) continue;
      if (!mapped(cleaned)) warnings.push(`${rel(file)}: macro spell "${cleaned}" is not in the entity registry.`);
    }
  }
}

function inspectLinks(html, file) {
  const link = /<a\b([^>]*)>/gi;
  let match;
  while ((match = link.exec(html))) {
    const attrs = match[1];
    const href = attr(attrs, "href");
    if (!href) continue;
    if (/^https?:\/\//i.test(href)) {
      if (attr(attrs, "target") !== "_blank") errors.push(`${rel(file)}: external link lacks target="_blank": ${href}`);
      if (!/\bnoopener\b/i.test(attr(attrs, "rel"))) errors.push(`${rel(file)}: external link lacks rel="noopener": ${href}`);
    }
    if (/wowhead\.com\//i.test(href) && !/wowhead\.com\/wotlk(?:\/|$)/i.test(href)) {
      errors.push(`${rel(file)}: non-WotLK Wowhead link: ${href}`);
    }
  }
}

function inspectIcons(html, file) {
  const image = /<img\b([^>]*)>/gi;
  let match;
  while ((match = image.exec(html))) {
    const attrs = match[1];
    const src = attr(attrs, "src");
    if (!/wow\.zamimg\.com\/images\/wow\/icons\/large\//i.test(src)) continue;
    if (attr(attrs, "alt") !== "") errors.push(`${rel(file)}: decorative WoW icon must use alt="": ${src}`);
    if (attr(attrs, "aria-hidden") !== "true") errors.push(`${rel(file)}: decorative WoW icon must use aria-hidden="true": ${src}`);
    if (!/onerror=(?:"this\.remove\(\)"|'this\.remove\(\)')/i.test(attrs)) errors.push(`${rel(file)}: WoW icon lacks onerror="this.remove()": ${src}`);
  }
}

function inspectCandidateNames(html, file) {
  const text = stripTags(html);
  const patterns = [
    /\b(?:Glyph of|Flask of|Elixir of|Potion of|Arcanum of|Greater Inscription of) [A-Z][A-Za-z0-9'’:-]*(?: [A-Z][A-Za-z0-9'’:-]*){0,6}/g,
    /\b(?:Plans|Pattern|Recipe|Formula|Design): [A-Z][A-Za-z0-9'’:-]*(?: [A-Z][A-Za-z0-9'’:-]*){0,7}/g
  ];
  for (const pattern of patterns) {
    for (const match of text.matchAll(pattern)) {
      const name = match[0].trim();
      const normalized = name.toLowerCase();
      const related = [...entityMap.keys()].some((known) => known.startsWith(normalized) || normalized.startsWith(`${known} `));
      if (!mapped(name) && !related) warnings.push(`${rel(file)}: likely game entity "${name}" is not in the registry.`);
    }
  }
}

function countEntityUsage(allHtml) {
  let used = 0;
  for (const entity of entities) {
    const count = entity.names.reduce((sum, name) => {
      const escaped = name.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
      return sum + (allHtml.match(new RegExp(escaped, "gi")) || []).length;
    }, 0);
    if (count) used += 1;
    else warnings.push(`Entity registry: unused ${entity.type}=${entity.id} (${entity.names.join(" / ")}).`);
  }
  notes.push(`${used}/${entities.length} registry entities appear in the six guide pages.`);
}

function runIconDensityReleaseAudit() {
  if (!release) return;
  if (iconDensityStatus === "grandfathered") {
    warnings.push(`Complexity-based icon approval is grandfathered for ${config.specName}. This exception is only for an existing baseline guide and must not be copied to a new guide.`);
    return;
  }
  if (iconDensityStatus !== "required") {
    errors.push(`Invalid iconDensityStatus "${iconDensityStatus}". New and updated guides default to "required"; only an explicitly documented existing baseline may use "grandfathered".`);
    return;
  }

  const analyzer = path.resolve(root, "tools/analyze-guide-icon-density.mjs");
  const result = spawnSync(process.execPath, [
    analyzer,
    "--config", rel(configFile),
    "--policy", iconDensityPolicyFile,
    "--enforce"
  ], {
    cwd: root,
    stdio: "inherit"
  });

  if (result.error) {
    errors.push(`Could not run the rendered icon-density audit: ${result.error.message}`);
    return;
  }
  if (result.status !== 0) {
    errors.push(`Complexity-based icon approval failed. Install jsdom with "npm install --no-save --no-package-lock jsdom@24" if the analyzer could not start, then correct the reported density, coverage, or concentration failures.`);
    return;
  }
  notes.push("Complexity-based rendered icon approval passed as part of the release audit.");
}

let allHtml = "";
for (const file of pages) {
  if (!fs.existsSync(file)) {
    errors.push(`Missing guide page: ${rel(file)}.`);
    continue;
  }
  const html = fs.readFileSync(file, "utf8");
  allHtml += `\n${html}`;
  if (!html.includes(`../assets/${tooltipFile}`)) errors.push(`${rel(file)}: does not load assets/${tooltipFile}.`);
  inspectMarkers(html, file);
  inspectMacros(html, file);
  inspectLinks(html, file);
  inspectIcons(html, file);
  inspectCandidateNames(html, file);
  if (release && /\bTODO\b|template-todo|data-template-placeholder/i.test(html)) errors.push(`${rel(file)}: release audit found TODO/template placeholders.`);
}

if (!fs.existsSync(tooltipPath)) {
  errors.push(`Missing tooltip script: ${rel(tooltipPath)}.`);
} else {
  const script = fs.readFileSync(tooltipPath, "utf8");
  for (const required of ["linkPhrases", "loadWowheadTooltips", "wow.zamimg.com/js/tooltips.js", "data-wowhead", "iconizeEntities"]) {
    if (!script.includes(required)) errors.push(`${rel(tooltipPath)}: missing required generated tooltip feature: ${required}.`);
  }
  if (/todo spell|todo item|["']?id["']?\s*:\s*0\b/i.test(script) && release) errors.push(`${rel(tooltipPath)}: release audit found placeholder or zero IDs.`);
}

if (!entities.length) {
  const message = `${rel(registryPath)} contains no verified entities.`;
  if (release) errors.push(message); else warnings.push(message);
}

countEntityUsage(allHtml);
if (release && errors.length === 0) runIconDensityReleaseAudit();
else if (release && iconDensityStatus !== "grandfathered") notes.push("Rendered icon approval was deferred because an earlier release-audit error must be fixed first.");

console.log(`Spec guide audit: ${config.specName}`);
notes.forEach((note) => console.log(`  INFO  ${note}`));
warnings.forEach((warning) => console.warn(`  WARN  ${warning}`));
errors.forEach((error) => console.error(`  ERROR ${error}`));
console.log(`Result: ${errors.length} error(s), ${warnings.length} warning(s).`);
if (errors.length) process.exit(1);
