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

const locationSelectors = [
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
  talentGlyphUnits: "#talents .talent-panel, #talents .priority-card, #talents .guide-box, #talents tbody tr, #glyphs .priority-card, #glyphs .guide-box, #glyphs tbody tr",
  raidEncounters: ".raid-encounter",
  cardHeadings: ".guide-box > h3, .priority-card > h3, .phase-card > h3, .macro-card > h3",
  serverNotes: ".server-behavior > summary",
  tableRows: "table tbody tr",
  entityLinks: "a[data-wowhead], a.wowhead-link"
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

  for (const [key, selector] of locationSelectors) {
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
    denseMode: dom.window.document.body?.dataset.entityIcons === "dense",
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
    configPath: path.relative(root, path.resolve(root, configPath)).replaceAll(path.sep, "/"),
    entityIconMode: config.entityIconMode || "selective",
    allowDenseEntityIcons: config.allowDenseEntityIcons === true
  };
}

function loadPolicy() {
  const absolute = path.resolve(root, policyFile);
  if (!fs.existsSync(absolute)) return null;
  return JSON.parse(fs.readFileSync(absolute, "utf8"));
}

function opportunityScore(words, structures, policy) {
  const weights = policy?.opportunities?.weights || {};
  let score = 0;
  const breakdown = {};
  for (const [key, weight] of Object.entries(weights)) {
    const total = Number(structures[key]?.total || 0);
    const points = Number((total * Number(weight)).toFixed(2));
    breakdown[key] = { total, weight: Number(weight), points };
    score += points;
  }
  const wordBlockSize = Number(policy?.opportunities?.wordBlockSize || 750);
  const wordBlockWeight = Number(policy?.opportunities?.wordBlockWeight || 0);
  const wordBlocks = words / Math.max(wordBlockSize, 1);
  const wordPoints = Number((wordBlocks * wordBlockWeight).toFixed(2));
  breakdown.wordBlocks = { total: Number(wordBlocks.toFixed(2)), weight: wordBlockWeight, points: wordPoints };
  score += wordPoints;
  return { score: Number(score.toFixed(2)), breakdown };
}

function complexityLabel(score, policy) {
  const simpleMax = Number(policy?.opportunities?.tiers?.simpleMax ?? 54.99);
  const standardMax = Number(policy?.opportunities?.tiers?.standardMax ?? 84.99);
  if (score <= simpleMax) return "simple";
  if (score <= standardMax) return "standard";
  return "complex";
}

function derivedBudget(score, rule, floorOverride = null) {
  const floor = floorOverride ?? Number(rule.floor || 0);
  const minimum = Math.max(floor, Math.ceil(score * Number(rule.minimumRatio || 0)));
  const preferredMin = Math.max(minimum, Math.ceil(score * Number(rule.preferredMinimumRatio ?? rule.minimumRatio ?? 0)));
  const preferredMax = Math.max(preferredMin, Math.ceil(score * Number(rule.preferredMaximumRatio ?? rule.maximumRatio ?? 1)));
  const calculatedMaximum = Math.ceil(score * Number(rule.maximumRatio || 1) + Number(rule.maximumPadding || 0));
  const absoluteMaximum = Number(rule.absoluteMaximum || Number.MAX_SAFE_INTEGER);
  const maximum = Math.max(preferredMax, Math.min(absoluteMaximum, calculatedMaximum));
  return { minimum, preferredMin, preferredMax, maximum };
}

function pageFloor(page, policy) {
  const pageRule = policy.pages;
  return page.words < Number(pageRule.smallPageWordThreshold || 350)
    ? Number(pageRule.smallPageFloor || 2)
    : Number(pageRule.standardPageFloor || 4);
}

async function analyzeFamily(family, policy) {
  const pages = [];
  for (const suffix of family.pages) pages.push(await renderPage(family, suffix));

  for (const page of pages) {
    const opportunity = opportunityScore(page.words, page.structures, policy);
    page.opportunityScore = opportunity.score;
    page.opportunityBreakdown = opportunity.breakdown;
    page.complexity = complexityLabel(opportunity.score, policy);
    page.contextualBudget = derivedBudget(opportunity.score, policy.pages, pageFloor(page, policy));
  }

  const words = pages.reduce((sum, page) => sum + page.words, 0);
  const contextual = pages.reduce((sum, page) => sum + page.contextual, 0);
  const inlineEntity = pages.reduce((sum, page) => sum + page.inlineEntity, 0);
  const locations = Object.fromEntries([...locationSelectors.map(([key]) => key), "otherContextual"].map((key) => [key, sumLocation(pages, key)]));
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

  const opportunity = opportunityScore(words, structures, policy);
  const contextualBudget = derivedBudget(opportunity.score, policy.family);
  const entityLinkCount = structures.entityLinks.total;
  const inlinePreferredMax = Math.min(
    Number(policy.inlineEntity.absolutePreferredMaximum),
    Math.max(Number(policy.inlineEntity.minimumPreferredMaximum), Math.ceil(entityLinkCount * Number(policy.inlineEntity.preferredLinkRatio)))
  );
  const inlineHardMax = Math.min(
    Number(policy.inlineEntity.absoluteHardMaximum),
    Math.max(Number(policy.inlineEntity.minimumHardMaximum), Math.ceil(entityLinkCount * Number(policy.inlineEntity.hardLinkRatio)))
  );

  return {
    key: family.key,
    label: family.label,
    configPath: family.configPath || null,
    entityIconMode: family.entityIconMode || (pages.some((page) => page.denseMode) ? "dense" : "selective"),
    allowDenseEntityIcons: family.allowDenseEntityIcons === true,
    pages,
    totals: {
      words,
      total: contextual + inlineEntity,
      contextual,
      inlineEntity,
      entityLinkCount,
      contextualPer1000Words: Number(((contextual / Math.max(words, 1)) * 1000).toFixed(1)),
      inlinePer1000Words: Number(((inlineEntity / Math.max(words, 1)) * 1000).toFixed(1)),
      maxPageContextualShare: Number((Math.max(...pages.map((page) => page.contextual)) / Math.max(contextual, 1)).toFixed(3)),
      opportunityScore: opportunity.score,
      opportunityBreakdown: opportunity.breakdown,
      complexity: complexityLabel(opportunity.score, policy),
      contextualBudget,
      inlineBudget: { preferredMax: inlinePreferredMax, hardMax: inlineHardMax },
      locations,
      structures
    }
  };
}

function checkDerivedBudget(problems, warnings, label, value, budget) {
  if (value < budget.minimum) problems.push(`${label}: ${value} is below the complexity-based minimum ${budget.minimum}.`);
  if (value > budget.maximum) problems.push(`${label}: ${value} is above the complexity-based maximum ${budget.maximum}.`);
  if (value >= budget.minimum && value < budget.preferredMin) warnings.push(`${label}: ${value} passes but is below the preferred ${budget.preferredMin}.`);
  if (value <= budget.maximum && value > budget.preferredMax) warnings.push(`${label}: ${value} passes but is above the preferred ${budget.preferredMax}.`);
}

function checkCoverage(problems, label, structure, minimum) {
  if (!structure || structure.total === 0) return;
  const ratio = structure.withContextualIcon / structure.total;
  if (ratio < minimum) problems.push(`${label}: ${structure.withContextualIcon}/${structure.total} (${Math.round(ratio * 100)}%) is below ${Math.round(minimum * 100)}%.`);
}

function evaluateFamily(family, policy) {
  const problems = [];
  const warnings = [];
  if (!policy) return { passed: true, problems, warnings };
  const totals = family.totals;

  checkDerivedBudget(problems, warnings, "Family contextual icons", totals.contextual, totals.contextualBudget);
  if (totals.contextualPer1000Words > Number(policy.family.maximumPer1000Words)) {
    problems.push(`Contextual density: ${totals.contextualPer1000Words} per 1,000 words is above ${policy.family.maximumPer1000Words}.`);
  } else if (totals.contextualPer1000Words < Number(policy.family.warningBelowPer1000Words)) {
    warnings.push(`Contextual density: ${totals.contextualPer1000Words} per 1,000 words is low; verify that the guide still has enough visual anchors.`);
  }

  if (totals.contextual >= Number(policy.concentration.applyPageShareAfterContextualIcons) && totals.maxPageContextualShare > Number(policy.concentration.maxPageShare)) {
    problems.push(`Largest page owns ${Math.round(totals.maxPageContextualShare * 100)}% of contextual icons; maximum is ${Math.round(policy.concentration.maxPageShare * 100)}%.`);
  }

  for (const page of family.pages) checkDerivedBudget(problems, warnings, `${page.page} contextual icons`, page.contextual, page.contextualBudget);

  for (const [key, minimum] of Object.entries(policy.coverage)) {
    checkCoverage(problems, `${key} contextual icon coverage`, totals.structures[key], Number(minimum));
  }

  const tableShare = totals.contextual ? totals.locations.tables / totals.contextual : 0;
  if (tableShare > Number(policy.concentration.maxTableShare)) {
    problems.push(`Table icons are ${Math.round(tableShare * 100)}% of contextual icons; maximum is ${Math.round(policy.concentration.maxTableShare * 100)}%.`);
  }
  const otherShare = totals.contextual ? totals.locations.otherContextual / totals.contextual : 0;
  if (otherShare > Number(policy.concentration.maxOtherContextualShare)) {
    problems.push(`Unclassified contextual icons are ${Math.round(otherShare * 100)}% of contextual icons; maximum is ${Math.round(policy.concentration.maxOtherContextualShare * 100)}%.`);
  }

  if (totals.inlineEntity > totals.inlineBudget.hardMax) {
    problems.push(`Inline entity icons: ${totals.inlineEntity} exceeds the complexity-based maximum ${totals.inlineBudget.hardMax} for ${totals.entityLinkCount} eligible links.`);
  } else if (totals.inlineEntity > totals.inlineBudget.preferredMax) {
    warnings.push(`Inline entity icons: ${totals.inlineEntity} passes but is above the preferred ${totals.inlineBudget.preferredMax}.`);
  }
  if (totals.inlinePer1000Words > Number(policy.inlineEntity.maximumPer1000Words)) {
    problems.push(`Inline icon density: ${totals.inlinePer1000Words} per 1,000 words is above ${policy.inlineEntity.maximumPer1000Words}.`);
  }
  if (totals.inlineEntity > 0) {
    const proseShare = totals.structures.inlineInParagraphs / totals.inlineEntity;
    if (proseShare > Number(policy.inlineEntity.maxParagraphShare)) {
      problems.push(`Inline icons in paragraphs are ${Math.round(proseShare * 100)}% of inline icons; maximum is ${Math.round(policy.inlineEntity.maxParagraphShare * 100)}%. Use lists, tables, chips, and callouts instead.`);
    }
  }
  if (family.entityIconMode === "dense" && !family.allowDenseEntityIcons) {
    problems.push("Dense entity-icon mode is active without allowDenseEntityIcons: true in the guide config.");
  }

  return { passed: problems.length === 0, problems, warnings };
}

const policy = loadPolicy();
const selectedFamilies = configFile ? [familyFromConfig(configFile)] : BASELINE_FAMILIES;
const report = {
  generatedAt: new Date().toISOString(),
  methodology: "Rendered DOM after local guide icon scripts; derives each guide's contextual icon budget from its actual icon-worthy structures and separates optional inline entity icons.",
  policyFile: fs.existsSync(path.resolve(root, policyFile)) ? policyFile : null,
  families: []
};
for (const family of selectedFamilies) {
  const analyzed = await analyzeFamily(family, policy);
  analyzed.approval = evaluateFamily(analyzed, policy);
  report.families.push(analyzed);
}

function budgetText(budget) {
  return `${budget.minimum}–${budget.maximum} (preferred ${budget.preferredMin}–${budget.preferredMax})`;
}

function markdown(data) {
  const lines = [
    "# Rendered guide icon-density report",
    "",
    data.methodology,
    "",
    "## Family totals",
    "",
    "| Guide family | Complexity | Opportunity score | Words | Contextual | Required contextual range | Inline | Inline maximum | Approval |",
    "|---|---|---:|---:|---:|---:|---:|---:|---|"
  ];
  for (const family of data.families) {
    const t = family.totals;
    lines.push(`| ${family.label} | ${t.complexity} | ${t.opportunityScore} | ${t.words} | ${t.contextual} | ${budgetText(t.contextualBudget)} | ${t.inlineEntity} | ${t.inlineBudget.hardMax} | ${family.approval.passed ? "Pass" : "Needs work"} |`);
  }
  for (const family of data.families) {
    lines.push("", `## ${family.label} by page`, "", "| Page | Complexity | Opportunity score | Words | Contextual | Required range | Inline |", "|---|---|---:|---:|---:|---:|---:|");
    for (const page of family.pages) {
      lines.push(`| ${page.page} | ${page.complexity} | ${page.opportunityScore} | ${page.words} | ${page.contextual} | ${budgetText(page.contextualBudget)} | ${page.inlineEntity} |`);
    }
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
