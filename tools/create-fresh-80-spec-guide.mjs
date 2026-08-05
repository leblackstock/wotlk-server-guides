#!/usr/bin/env node
import fs from "node:fs";
import path from "node:path";
import process from "node:process";
import { spawnSync } from "node:child_process";
import { validateFresh80Config } from "./lib/fresh-80-policy.mjs";

const args = process.argv.slice(2);
const configArg = args.find((arg) => !arg.startsWith("--"));
if (!configArg) {
  console.error("Usage: node tools/create-fresh-80-spec-guide.mjs <config.json> [--force] [--dry-run]");
  process.exit(1);
}

const root = process.cwd();
const configFile = path.resolve(root, configArg);
const config = JSON.parse(fs.readFileSync(configFile, "utf8"));
const errors = validateFresh80Config(config);
if (errors.length) {
  errors.forEach((error) => console.error(`Fresh-80 config error: ${error}`));
  process.exit(1);
}

const result = spawnSync(process.execPath, [
  path.resolve(root, "tools/create-complete-spec-guide.mjs"),
  ...args
], {
  cwd: root,
  stdio: "inherit"
});

process.exit(result.status ?? 1);
