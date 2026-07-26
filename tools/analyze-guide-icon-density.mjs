#!/usr/bin/env node
import fs from "node:fs";
import path from "node:path";
import process from "node:process";
import { JSDOM } from "jsdom";

const root = process.cwd();
const jsonOutput = process.argv.includes("--json");
const outArgIndex = process.argv.indexOf("--out");
const outFile = outArgIndex >= 0 ? process.argv[outArgIndex + 1] : null;

const families = [
  {
    key: "protection-paladin",
    label: "Protection Paladin",
    pages: ["pve-guide", "playing", "setting-up", "gearing", "gear-targets", "raiding"],
    runtimeScripts: []
  },
  {
    key: "holy-paladin",
    label: "Holy Paladin",
    pages: ["pve-guide", "playing", "setting-up", "gearing", "gear-targets", "raiding"],
    runtimeScripts: ["assets/holy-paladin.js"]
  },
  {
    key: "blood-death-knight",
    label: "Blood Death Knight",
    pages: ["pve-guide", "playing", "setting-up", "gearing", "gear-targets", "raiding"],
    runtimeScripts: ["assets/death-knight-tooltips.js", "assets/blood-death-knight.js"]
  }
];

const selectors = [
  ["sectionHeadings", "main .common > h2 img, main section > h2 img"],
  ["chapterCards", ".chapter-card img"],
  ["engineAndSummary", ".engine-step img, .summary-card img, .beacon-node img, .cooldown-group img"],
  ["playbooksAndActions", ".spec-card img, .heal-card img, .pull-card img, .ability-strip img, .spell-choice img, .cooldown-card img, .utility-card img"],
  ["talentsAndGlyphs", "#talents img, #glyphs img, .talent-panel img, .talent-embed-wrap + * img"],
  ["tables", "table img"],
  ["serverNotes", ".server-behavior > summary img"],
  ["raidSummaries", ".raid-encounter > summary img"],
  ["cardHeadings", ".guide-box > h3 img, .priority-card > h3 img, .phase-card > h3 img, .macro-card > h3 img"]
];

function wordsIn(node) {
  const text = String(node?.textContent || "").replace(/\s+/g, " ").trim();
  return text ? text.split(" ").length : 0;
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
    classCounts
  };
}

async function renderPage(family, suffix) {
  const file = path.join(root, "guides", `${family.key}-${suffix}.html`);
  const html = fs.readFileSync(file, "utf8");
  const dom = new JSDOM(html, {
    runScripts: "outside-only",
    url: `https://example.invalid/guides/${family.key}-${suffix}.html`,
    pretendToBeVisual: true
  });

  dom.window.HTMLElement.prototype.scrollIntoView ||= function () {};
  for (const scriptFile of family.runtimeScripts) {
    const code = fs.readFileSync(path.join(root, scriptFile), "utf8");
    dom.window.eval(`${code}\n//# sourceURL=${scriptFile}`);
  }
  dom.window.document.dispatchEvent(new dom.window.Event("DOMContentLoaded", { bubbles: true }));
  await new Promise((resolve) => dom.window.setTimeout(resolve, 25));

  const main = dom.window.document.querySelector("main");
  if (!main) throw new Error(`Missing <main> in ${path.relative(root, file)}`);
  const icons = classifyIcons(main);
  const result = {
    page: suffix,
    file: path.relative(root, file).replaceAll(path.sep, "/"),
    words: wordsIn(main),
    ...icons,
    contextualPer1000Words: Number(((icons.contextual / Math.max(wordsIn(main), 1)) * 1000).toFixed(1)),
    inlinePer1000Words: Number(((icons.inlineEntity / Math.max(wordsIn(main), 1)) * 1000).toFixed(1))
  };
  dom.window.close();
  return result;
}

function sumLocation(pages, key) {
  return pages.reduce((sum, page) => sum + (page.locations[key] || 0), 0);
}

const report = { generatedAt: new Date().toISOString(), methodology: "Rendered DOM after local guide icon scripts; counts only images inside <main>.", families: [] };
for (const family of families) {
  const pages = [];
  for (const suffix of family.pages) pages.push(await renderPage(family, suffix));
  const words = pages.reduce((sum, page) => sum + page.words, 0);
  const contextual = pages.reduce((sum, page) => sum + page.contextual, 0);
  const inlineEntity = pages.reduce((sum, page) => sum + page.inlineEntity, 0);
  const locations = Object.fromEntries([...selectors.map(([key]) => key), "otherContextual"].map((key) => [key, sumLocation(pages, key)]));
  report.families.push({
    key: family.key,
    label: family.label,
    pages,
    totals: {
      words,
      total: contextual + inlineEntity,
      contextual,
      inlineEntity,
      contextualPer1000Words: Number(((contextual / Math.max(words, 1)) * 1000).toFixed(1)),
      inlinePer1000Words: Number(((inlineEntity / Math.max(words, 1)) * 1000).toFixed(1)),
      locations
    }
  });
}

function markdown(data) {
  const lines = [
    "# Rendered guide icon-density report",
    "",
    data.methodology,
    "",
    "## Family totals",
    "",
    "| Guide family | Words | Contextual icons | Inline entity icons | Total icons | Contextual / 1,000 words | Inline / 1,000 words |",
    "|---|---:|---:|---:|---:|---:|---:|"
  ];
  for (const family of data.families) {
    const t = family.totals;
    lines.push(`| ${family.label} | ${t.words} | ${t.contextual} | ${t.inlineEntity} | ${t.total} | ${t.contextualPer1000Words} | ${t.inlinePer1000Words} |`);
  }
  for (const family of data.families) {
    lines.push("", `## ${family.label} by page`, "", "| Page | Words | Contextual | Inline | Total | Contextual / 1,000 words |", "|---|---:|---:|---:|---:|---:|");
    for (const page of family.pages) lines.push(`| ${page.page} | ${page.words} | ${page.contextual} | ${page.inlineEntity} | ${page.total} | ${page.contextualPer1000Words} |`);
    lines.push("", "Placement totals:", "");
    for (const [key, value] of Object.entries(family.totals.locations)) lines.push(`- ${key}: ${value}`);
  }
  return `${lines.join("\n")}\n`;
}

if (outFile) fs.writeFileSync(path.resolve(root, outFile), `${JSON.stringify(report, null, 2)}\n`, "utf8");
if (jsonOutput) process.stdout.write(`${JSON.stringify(report, null, 2)}\n`);
else process.stdout.write(markdown(report));
