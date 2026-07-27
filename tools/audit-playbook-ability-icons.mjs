#!/usr/bin/env node
import fs from "node:fs";
import path from "node:path";
import process from "node:process";
import { JSDOM } from "jsdom";

const args = process.argv.slice(2);
const configArg = args.find((arg) => !arg.startsWith("--"));
if (!configArg) {
  console.error("Usage: node tools/audit-playbook-ability-icons.mjs <config.json>");
  process.exit(1);
}

const root = process.cwd();
const configFile = path.resolve(root, configArg);
const config = JSON.parse(fs.readFileSync(configFile, "utf8"));
const playingFile = path.resolve(root, "guides", `${config.specSlug}-playing.html`);

if (!fs.existsSync(playingFile)) {
  console.error(`Playbook ability icon audit: ${config.specName}`);
  console.error(`  ERROR Missing guide page: ${path.relative(root, playingFile).replaceAll(path.sep, "/")}.`);
  console.error("Result: 1 error(s).");
  process.exit(1);
}

const html = fs.readFileSync(playingFile, "utf8");
const dom = new JSDOM(html, {
  runScripts: "outside-only",
  url: `https://example.invalid/guides/${config.specSlug}-playing.html`,
  pretendToBeVisual: true
});

dom.window.HTMLElement.prototype.scrollIntoView ||= function () {};

for (const script of dom.window.document.querySelectorAll("script[src]")) {
  const src = script.getAttribute("src").split("?")[0];
  if (!src.endsWith(".js") || /^https?:/i.test(src)) continue;
  const scriptFile = path.resolve(path.dirname(playingFile), src);
  if (!scriptFile.startsWith(root) || !fs.existsSync(scriptFile)) continue;
  dom.window.eval(`${fs.readFileSync(scriptFile, "utf8")}\n//# sourceURL=${path.relative(root, scriptFile)}`);
}

dom.window.document.dispatchEvent(new dom.window.Event("DOMContentLoaded", { bubbles: true }));
await new Promise((resolve) => dom.window.setTimeout(resolve, 30));

const cards = Array.from(dom.window.document.querySelectorAll(".spec-playbook-grid .spec-card"));
const chips = cards.flatMap((card) => Array.from(card.querySelectorAll(".ability-strip > .ability-choice")));
const failures = [];

for (const chip of chips) {
  const icons = Array.from(chip.querySelectorAll("img"));
  const icon = icons[0];
  const cardTitle = chip.closest(".spec-card")?.querySelector(".spec-card-header h3")?.textContent.trim() || "Untitled playbook";
  const ability = chip.textContent.replace(/\s+/g, " ").trim() || "Unnamed action";
  const src = icon?.getAttribute("src") || "";
  if (!icons.length || !/wow\.zamimg\.com\/images\/wow\/icons\/large\/[a-z0-9_]+\.jpg$/i.test(src)) {
    failures.push(`${cardTitle}: "${ability}" has no rendered WoW ability icon.`);
  } else if (icons.length !== 1) {
    failures.push(`${cardTitle}: "${ability}" renders ${icons.length} icons; every action chip must render exactly one.`);
  }
}

console.log(`Playbook ability icon audit: ${config.specName}`);
if (!cards.length) {
  console.log("  INFO  No .spec-card playbooks exist in this guide; this playbook style is not used.");
} else {
  console.log(`  INFO  Checked ${chips.length} ability/action chips across ${cards.length} playbook cards.`);
}
failures.forEach((failure) => console.error(`  ERROR ${failure}`));
console.log(`Result: ${failures.length} error(s).`);
dom.window.close();

if (failures.length) process.exit(1);
