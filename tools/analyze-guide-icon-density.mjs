#!/usr/bin/env node
import fs from "node:fs";
import path from "node:path";
import process from "node:process";
import { JSDOM } from "jsdom";

const root = process.cwd();
const args = process.argv.slice(2);
const PAGE_SUFFIXES = ["pve-guide", "playing", "setting-up", "gearing", "gear-targets", "raiding"];
const jsonOutput = args.includes("--json");
const enforce = args.includes("--enforce");
const valueAfter = (flag) => {
  const index = args.indexOf(flag);
  return index >= 0 ? args[index + 1] : null;
};
const outFile = valueAfter("--out");
const configFile = valueAfter("--config");
const policyFile = valueAfter("--policy") || "templates/spec-guide/icon-density-policy.json";

const BASELINE_FAMILIES = [
  {
    key: "protection-paladin",
    label: "Protection Paladin",
    pages: PAGE_SUFFIXES,
    runtimeScripts: []
  },
  {
    key: "holy-paladin",
    label: "Holy Paladin",
    pages: PAGE_SUFFIXES,
    runtimeScripts: ["assets/holy-paladin.js"]
  },
  {
    key: "blood-death-knight",
    label: "Blood Death Knight",
    pages: PAGE_SUFFIXES,
    runtimeScripts: ["assets/death-knight-tooltips.js", "assets/blood-death-knight.js"]
  }
];

const selectors = [
  ["sectionHeadings", "main .common > h2 img, main section > h2 img"],
  ["chapterCards", ".chapter-card img"],
  ["engineAndSummary", ".engine-step img, .summary-card img, .beacon-node img, .cooldown-group img"],
  ["playbooksAndActions", ".spec-card img, .heal-card img, .pull-card img, .ability-strip img, .spell-choice img, .cooldown-card img, .utility-card img"],
  ["talentsAndGlyphs", "#talents img, #glyphs img, .talent-panel img"],
  ["tables", "table img"],
  ["serverNotes", ".server-behavior > summary img"],
  ["raidSummaries", ".raid-encounter > summary img"],
  ["cardHeadings", ".guide-box > h3 img, .priority-card > h3 img, .phase-card > h3 img, .macro-card > h3 img"]
];

const structureSelectors = {
  majorSections: "main .common > h2, main section > h2",
  chapterCards: ".chapter-card",
  engineNodes: ".engine-step, .summary-card, .beacon-node, .cooldown-group",
  playbookCards: ".spec-card, .heal-card, .pull-card, .cooldown-card, .utility-card",
  raidEncounters: ".raid-encounter",
  tableRows: "table tbody tr"
};

function wordsIn(node) {
  const text = String(node?.textContent || "").replace(/\s+/g, " ").trim();
  return text ? text.split(" ").length : 0;
}

function uniqueElements(rootNode, selector) {
  return Array.from(new Set(Array.from(rootNode.querySelectorAll(selector))));
}

function countStructures(main) {
  const structures = {};
  for (const [key, selector] of Object.entries(structureSelectors)) {
    const nodes = uniqueElements(main, selector);
    structures[key] = {
      total: nodes.length,
      withAnyIcon: nodes.filter((node) => node.querySelector("img")).length,
      withContextualIcon: nodes.filter((node) => node.querySelector("img:not(.entity-link-icon)")).length
    };
  }
  const inline = Array.from(main.querySelectorAll("img.entity-link-icon"));
  structures.inlineInParagraphs = inline.filter((img) => img.closest("p")).length;
  structures.inlineInListsOrTables = inline.filter((img) => img.closest("li,td,th,table")).length;
  return structures;
}

function classifyIcons(main) {
  const all = Array.from(main.querySelectorAll("img"));
  const inline = all.filter((img) => img.classList.contains("entity-link-icon"));
  const contextual = all.filter((img) => !img.classList.contains("entity-link-icon"));
  const assigned = new Set();
  const locations = {};

  for (const [key, selector] of selectors) {
    const matches = new Set(Array.from(main.querySelectorAll(selector)).filter((img) => contextual.includes(img)));
    let count = 0;
    for (const img of matches) {
      if (assigned.has(img)) continue;
      assigned.add(img);
      count += 1;
    }
    locations[key] = count;
  }
  locations.otherContextual = contextual.length - assigned.size;

  const classCounts = {};
  for (const className of ["spell-icon", "title-icon", "ability-icon", "item-icon", "entity-link-icon"]) {
    classCounts[className] = all.filter((img) => img.classList.contains(className)).length;
  }

  return {
    total: all.length,
    contextual: contextual.length,
    inlineEntity: inline.length,
    locations,
    classCounts,
    structures: countStructures(main)
  };
}

function runtimeScriptsFor(dom, file, family) {
  if (Array.isArray(family.runtimeScripts)) return family.runtimeScripts;
  const scripts = [];
  for (const node of dom.window.document.querySelectorAll("script[src]")) {
    const src = node.getAttribute("src").split("?")[0];
    if (!src.endsWith(".js") || /^https?:/i.test(src)) continue;
    const absolute = path.resolve(path.dirname(file), src);
    if (!absolute.startsWith(root) || !fs.existsSync(absolute)) continue;
    scripts.push(path.relative(root, absolute).replaceAll(path.sep, "/"));
  }
  return scripts;
}

async function renderPage(family, suffix) {
  const file = path.join(root, "guides", `${family.key}-${suffix}.html`);
  if (!fs.existsSync(file)) throw new Error(`Missing guide page: ${path.relative(root, file)}`);
  const html = fs.readFileSync(file, "utf8");
  const dom = new JSDOM(html, {
    runScripts: "outside-only",
    url: `https://example.invalid/guides/${family.key}-${suffix}.html`,
    pretendToBeVisual: true
  });

  dom.window.HTMLElement.prototype.scrollIntoView ||= function () {};
  for (const scriptFile of runtimeScriptsFor(dom, file, family)) {
    const code = fs.readFileSync(path.join(root, scriptFile), "utf8");
    dom.window.eval(`${code}\n//# sourceURL=${scriptFile}`);
  }
  dom.window.document.dispatchEvent(new dom.window.Event("DOMContentLoaded", { bubbles: true }));
  await new Promise((resolve) => dom.window.setTimeout(resolve, 30));

  const main = dom.window.document.querySelector("main");
  if (!main) throw new Error(`Missing <main> in ${path.relative(root, file)}`);
  const words = wordsIn(main);
  const icons = classifyIcons(main);
  const result = {
    page: suffix,
    file: path.relative(root, file).replaceAll(path.sep, "/"),
    words,
    ...icons,
    contextualPer1000Words: Number(((icons.contextual / Math.max(words, 1)) * 1000).toFixed(1)),
    inlinePer1000Words: Number(((icons.inlineEntity / Math.max(words, 1)) * 1000).toFixed(1))
  };
  dom.window.close();
  return result;
}

function sumLocation(pages, key) {
  return pages.reduce((sum, page) => sum + (page.locations[key] || 0), 0);
}

function sumStructure(pages, key, field) {
  return pages.reduce((sum, page) => sum + Number(page.structures[key]?.[field] || 0), 0);
}

function familyFromConfig(configPath) {
  const config = JSON.parse(fs.readFileSync(path.resolve(root, configPath), "utf8"));
  return {
    key: config.specSlug,
    label: config.specName,
    pages: PAGE_SUFFIXES,
    runtimeScripts: null,
    configPath: path.relative(root, path.resolve(root, configPath)).replaceAll(path.sep, "/")
  };
}

async function analyzeFamily(family) {
  const pages = [];
  for (const suffix of family.pages) pages.push(await renderPage(family, suffix));
  const words = pages.reduce((sum, page) => sum + page.words, 0);
  const contextual = pages.reduce((sum, page) => sum + page.contextual, 0);
  const inlineEntity = pages.reduce((sum, page) => sum + page.inlineEntity, 0);
  const locations = Object.fromEntries([...selectors.map(([key]) => key), "otherContextual"].map((key) => [key, sumLocation(pages, key)]));
  const structures = {};
  for (const key of Object.keys(structureSelectors)) {
    structures[key] = {
      total: sumStructure(pages, key, "total"),
      withAnyIcon: sumStructure(pages, key, "withAnyIcon"),
      withContextualIcon: sumStructure(pages, key, "withContextualIcon")
    };
  }
  structures.inlineInParagraphs = pages.reduce((sum, page) => sum + page.structures.inlineInParagraphs, 0);
  structures.inlineInListsOrTables = pages.reduce((sum, page) => sum + page.structures.inlineInListsOrTables, 0);
  return {
    key: family.key,
    label: family.label,
    configPath: family.configPath || null,
    pages,
    totals: {
      words,
      total: contextual + inlineEntity,
      contextual,
      inlineEntity,
      contextualPer1000Words: Number(((contextual / Math.max(words, 1)) * 1000).toFixed(1)),
      inlinePer1000Words: Number(((inlineEntity / Math.max(words, 1)) * 1000).toFixed(1)),
      maxPageContextualShare: Number((Math.max(...pages.map((page) => page.contextual)) / Math.max(contextual, 1)).toFixed(3)),
      locations,
      structures
    }
  };
}

function loadPolicy() {
  const absolute = path.resolve(root, policyFile);
  if (!fs.existsSync(absolute)) return null;
  return JSON.parse(fs.readFileSync(absolute, "utf8"));
}

function checkRange(problems, warnings, label, value, rule) {
  if (!rule) return;
  if (rule.min !== undefined && value < rule.min) problems.push(`${label}: ${value} is below ${rule.min}.`);
  if (rule.max !== undefined && value > rule.max) problems.push(`${label}: ${value} is above ${rule.max}.`);
  if (rule.preferredMin !== undefined && value < rule.preferredMin && value >= (rule.min ?? -Infinity)) warnings.push(`${label}: ${value} passes but is below the preferred ${rule.preferredMin}.`);
  if (rule.preferredMax !== undefined && value > rule.preferredMax && value <= (rule.max ?? Infinity)) warnings.push(`${label}: ${value} passes but is above the preferred ${rule.preferredMax}.`);
}

function checkCoverage(problems, label, structure, minimum) {
  if (!structure || structure.total === 0) {
    problems.push(`${label}: required structure is missing.`);
    return;
  }
  const ratio = structure.withAnyIcon / structure.total;
  if (ratio < minimum) problems.push(`${label}: ${structure.withAnyIcon}/${structure.total} (${Math.round(ratio * 100)}%) is below ${Math.round(minimum * 100)}%.`);
}

function evaluateFamily(family, policy) {
  const problems = [];
  const warnings = [];
  if (!policy) return { passed: true, problems, warnings };
  const totals = family.totals;

  checkRange(problems, warnings, "Family contextual icons", totals.contextual, policy.family.contextual);
  checkRange(problems, warnings, "Contextual icons per 1,000 words", totals.contextualPer1000Words, policy.family.contextualPer1000Words);
  checkRange(problems, warnings, "Inline entity icons", totals.inlineEntity, policy.family.inlineEntity);
  checkRange(problems, warnings, "Inline icons per 1,000 words", totals.inlinePer1000Words, policy.family.inlinePer1000Words);
  if (totals.maxPageContextualShare > policy.family.maxPageContextualShare) problems.push(`Largest page owns ${Math.round(totals.maxPageContextualShare * 100)}% of contextual icons; maximum is ${Math.round(policy.family.maxPageContextualShare * 100)}%.`);

  for (const page of family.pages) checkRange(problems, warnings, `${page.page} contextual icons`, page.contextual, policy.pages[page.page]);
  for (const [key, rule] of Object.entries(policy.placements)) checkRange(problems, warnings, `${key} contextual icons`, totals.locations[key] || 0, rule);

  checkCoverage(problems, "Chapter-card icon coverage", totals.structures.chapterCards, policy.coverage.chapterCards);
  checkCoverage(problems, "Combat-engine/summary icon coverage", totals.structures.engineNodes, policy.coverage.engineNodes);
  checkCoverage(problems, "Playbook-card icon coverage", totals.structures.playbookCards, policy.coverage.playbookCards);
  checkCoverage(problems, "Raid-summary icon coverage", totals.structures.raidEncounters, policy.coverage.raidEncounters);
  checkCoverage(problems, "Major-section icon coverage", totals.structures.majorSections, policy.coverage.majorSections);

  if (totals.inlineEntity > 0) {
    const proseShare = totals.structures.inlineInParagraphs / totals.inlineEntity;
    if (proseShare > policy.inlinePlacement.maxParagraphShare) problems.push(`Inline icons in paragraphs are ${Math.round(proseShare * 100)}% of inline icons; maximum is ${Math.round(policy.inlinePlacement.maxParagraphShare * 100)}%. Use lists, tables, chips, and callouts instead.`);
  }
  return { passed: problems.length === 0, problems, warnings };
}

const selectedFamilies = configFile ? [familyFromConfig(configFile)] : BASELINE_FAMILIES;
const report = {
  generatedAt: new Date().toISOString(),
  methodology: "Rendered DOM after local guide icon scripts; counts only images inside <main> and separates contextual icons from inline entity icons.",
  policyFile: fs.existsSync(path.resolve(root, policyFile)) ? policyFile : null,
  families: []
};
const policy = loadPolicy();
for (const family of selectedFamilies) {
  const analyzed = await analyzeFamily(family);
  analyzed.approval = evaluateFamily(analyzed, policy);
  report.families.push(analyzed);
}

function markdown(data) {
  const lines = [
    "# Rendered guide icon-density report",
    "",
    data.methodology,
    "",
    "## Family totals",
    "",
    "| Guide family | Words | Contextual icons | Inline entity icons | Total icons | Contextual / 1,000 words | Inline / 1,000 words | Approval |",
    "|---|---:|---:|---:|---:|---:|---:|---|"
  ];
  for (const family of data.families) {
    const t = family.totals;
    lines.push(`| ${family.label} | ${t.words} | ${t.contextual} | ${t.inlineEntity} | ${t.total} | ${t.contextualPer1000Words} | ${t.inlinePer1000Words} | ${family.approval.passed ? "Pass" : "Needs work"} |`);
  }
  for (const family of data.families) {
    lines.push("", `## ${family.label} by page`, "", "| Page | Words | Contextual | Inline | Total | Contextual / 1,000 words |", "|---|---:|---:|---:|---:|---:|");
    for (const page of family.pages) lines.push(`| ${page.page} | ${page.words} | ${page.contextual} | ${page.inlineEntity} | ${page.total} | ${page.contextualPer1000Words} |`);
    lines.push("", "Placement totals:", "");
    for (const [key, value] of Object.entries(family.totals.locations)) lines.push(`- ${key}: ${value}`);
    if (family.approval.problems.length) lines.push("", "Approval failures:", "", ...family.approval.problems.map((item) => `- ${item}`));
    if (family.approval.warnings.length) lines.push("", "Approval notes:", "", ...family.approval.warnings.map((item) => `- ${item}`));
  }
  return `${lines.join("\n")}\n`;
}

if (outFile) fs.writeFileSync(path.resolve(root, outFile), `${JSON.stringify(report, null, 2)}\n`, "utf8");
if (jsonOutput) process.stdout.write(`${JSON.stringify(report, null, 2)}\n`);
else process.stdout.write(markdown(report));
if (enforce && report.families.some((family) => !family.approval.passed)) process.exit(1);
