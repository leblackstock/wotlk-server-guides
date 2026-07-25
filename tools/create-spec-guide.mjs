#!/usr/bin/env node
import path from "node:path";
import process from "node:process";
import { spawnSync } from "node:child_process";

console.warn("tools/create-spec-guide.mjs now runs the complete production workflow, including the entity registry, Wowhead mouseovers, icon gates, and release audit checklist.");
const result = spawnSync(process.execPath, [path.resolve(process.cwd(), "tools/create-complete-spec-guide.mjs"), ...process.argv.slice(2)], {
  cwd: process.cwd(),
  stdio: "inherit"
});
process.exit(result.status ?? 1);
