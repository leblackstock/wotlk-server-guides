#!/usr/bin/env node
import fs from "node:fs";
import path from "node:path";
import process from "node:process";
import { buildTooltipScript, loadRegistry } from "./lib/wowhead-entities.mjs";

const [registryArg, outputArg] = process.argv.slice(2);
if (!registryArg || !outputArg) {
  console.error("Usage: node tools/build-wowhead-tooltips.mjs <entity-registry.json> <output.js>");
  process.exit(1);
}

const root = process.cwd();
const registryFile = path.resolve(root, registryArg);
const outputFile = path.resolve(root, outputArg);
const registry = loadRegistry(registryFile);
const script = buildTooltipScript(registry, { classSlug: registry.classSlug });

fs.mkdirSync(path.dirname(outputFile), { recursive: true });
fs.writeFileSync(outputFile, script, "utf8");
console.log(`Wrote ${path.relative(root, outputFile)} from ${path.relative(root, registryFile)}.`);
