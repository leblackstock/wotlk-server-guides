import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import { spawnSync } from "node:child_process";
import { fileURLToPath } from "node:url";
import { validateFresh80Config } from "../tools/lib/fresh-80-policy.mjs";

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const configPath = path.join(root, "templates/spec-guide/marksmanship-hunter.config.json");
const config = JSON.parse(fs.readFileSync(configPath, "utf8"));
assert.deepEqual(validateFresh80Config(config), []);

const invalid = structuredClone(config);
invalid.fresh80Policy.externalRaidBuffsRequired = true;
invalid.talent.name = "25-player raid build";
assert.ok(validateFresh80Config(invalid).length >= 2);

for (const configFile of [
  "templates/spec-guide/holy-priest.config.json",
  "templates/spec-guide/shadow-priest.config.json",
  "templates/spec-guide/marksmanship-hunter.config.json"
]) {
  const freshConfig = JSON.parse(fs.readFileSync(path.join(root, configFile), "utf8"));
  assert.deepEqual(validateFresh80Config(freshConfig), [], configFile);
  const audit = spawnSync(process.execPath, ["tools/audit-fresh-80-guide.mjs", configFile], {
    cwd: root,
    encoding: "utf8"
  });
  assert.equal(audit.status, 0, `${configFile}\n${audit.stdout}\n${audit.stderr}`);
}

for (const file of [
  "templates/spec-guide/NEW_LEVEL_80_GUIDE_WORKFLOW.md",
  "tools/create-fresh-80-spec-guide.mjs",
  "tools/audit-fresh-80-guide.mjs"
]) {
  assert.ok(fs.existsSync(path.join(root, file)), `${file} is missing`);
}

console.log("Fresh-80 workflow policy and all config-backed fresh-80 family audits passed.");
