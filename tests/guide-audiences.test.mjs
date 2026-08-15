import assert from "node:assert/strict";
import path from "node:path";
import { spawnSync } from "node:child_process";
import { fileURLToPath } from "node:url";

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const audit = spawnSync(process.execPath, ["tools/audit-guide-audiences.mjs"], {
  cwd: root,
  encoding: "utf8"
});

assert.equal(audit.status, 0, `${audit.stdout}\n${audit.stderr}`);
assert.match(audit.stdout, /13 registered families/);

const densityReport = spawnSync(process.execPath, [
  "tools/analyze-guide-icon-density.mjs",
  "--config", "templates/spec-guide/holy-priest.config.json",
  "--policy", "templates/spec-guide/icon-density-policy.json",
  "--enforce"
], {
  cwd: root,
  encoding: "utf8"
});
assert.equal(densityReport.status, 0, `${densityReport.stdout}\n${densityReport.stderr}`);
assert.match(densityReport.stdout, /Counts never force icons to be added or removed/);
console.log("Guide audience registry and rendered family classifications passed.");
