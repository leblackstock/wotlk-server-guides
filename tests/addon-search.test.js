"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const core = require("../assets/addon-search-core.js");
const catalog = JSON.parse(fs.readFileSync(path.join(__dirname, "../data/addons.json"), "utf8"));
const addons = catalog.addons;
const specializationTags = catalog.tags.filter((tag) => tag.group === "specialization");
assert.equal(specializationTags.length, 30, "WotLK taxonomy should register thirty class-qualified specializations");
assert.ok(specializationTags.every((tag) => tag.classId && Array.isArray(tag.roleIds) && tag.id.startsWith(`${tag.classId}-`)));
assert.equal(catalog.tags.some((tag) => ["protection", "holy", "frost", "restoration"].includes(tag.id)), false);

function state(query = "", filters = {}, sort = "smart") {
  return { query, filters, sort, addon: "" };
}

function ids(query, filters = {}) {
  return core.filterAndSort(addons, state(query, filters), catalog).map((addon) => addon.id);
}

function first(query, filters = {}) {
  return ids(query, filters)[0];
}

const searchCases = [
  ["healbt", "healbot"],
  ["heal bot", "healbot"],
  ["paly power", "pallypower"],
  ["piss", "protection-is-surprisingly-stupendous"],
  ["thret meter", "omen3"],
  ["boss timer", "deadly-boss-mods"],
  ["cooldown numbers", "omnicc"],
  ["gear stats", "ratingbuster"],
  ["969 trainer", "protection-is-surprisingly-stupendous"],
  ["questi", "questie"],
  ["quest helper", "questie"]
];

for (const [query, expected] of searchCases) assert.equal(first(query), expected, `${query} should rank ${expected} first`);

const protResults = ids("prot pally");
assert.ok(protResults.includes("pallypower"));
assert.ok(protResults.includes("healbot"));

for (const list of [ids("righteous defense"), ids("righteous defence")]) {
  assert.ok(list.includes("healbot"));
  assert.ok(list.includes("tauntmaster"));
}

const canonicalProtection = { class: ["paladin"], specialization: ["paladin-protection"], role: ["tank"] };
const equivalentProtectionContexts = [
  canonicalProtection,
  { class: ["paladin"], role: ["tank"] },
  { class: ["paladin"], specialization: ["paladin-protection"] }
];
const canonicalIds = ids("", canonicalProtection);
for (const filters of equivalentProtectionContexts) {
  assert.deepEqual(ids("", filters), canonicalIds, `${JSON.stringify(filters)} should resolve to Protection Paladin Tank`);
  assert.deepEqual(ids("", { ...filters, importance: ["essential"] }), ["deadly-boss-mods", "pallypower"]);
}
assert.deepEqual(canonicalIds.slice(0, 2), ["deadly-boss-mods", "pallypower"]);

const pallyPower = addons.find((addon) => addon.id === "pallypower");
const healbot = addons.find((addon) => addon.id === "healbot");
for (const filters of equivalentProtectionContexts) {
  const current = state("", filters);
  assert.equal(core.recommendationFor(pallyPower, current, catalog).importance, "essential");
  assert.equal(core.customizationFor(healbot, current, catalog).id, "protection-paladin");
  assert.equal(core.contextLabel(current, catalog), "Protection Paladin");
}

const paladinTankResolved = core.resolveContext(state("", { class: ["paladin"], role: ["tank"] }), catalog);
assert.deepEqual(paladinTankResolved.state.filters.specialization, ["paladin-protection"]);
assert.match(paladinTankResolved.note, /Protection inferred/);
const paladinProtectionResolved = core.resolveContext(state("", { class: ["paladin"], specialization: ["paladin-protection"] }), catalog);
assert.deepEqual(paladinProtectionResolved.state.filters.role, ["tank"]);
assert.match(paladinProtectionResolved.note, /Tank inferred/);

const fixedInferenceCases = [
  [{ specialization: ["warrior-arms"] }, "warrior", "dps", "Arms Warrior"],
  [{ class: ["priest"], role: ["dps"] }, "priest", "dps", "Shadow Priest"],
  [{ class: ["shaman"], role: ["healer"] }, "shaman", "healer", "Restoration Shaman"],
  [{ class: ["druid"], role: ["tank"] }, "druid", "tank", "Feral Druid"]
];
for (const [filters, expectedClass, expectedRole, expectedLabel] of fixedInferenceCases) {
  const resolved = core.resolveContext(state("", filters), catalog);
  assert.deepEqual(resolved.state.filters.class, [expectedClass]);
  assert.deepEqual(resolved.state.filters.role, [expectedRole]);
  assert.equal(resolved.label, expectedLabel);
}

const ambiguityCases = [
  [{ class: ["warrior"], role: ["dps"] }, /Arms.*Fury/],
  [{ class: ["priest"], role: ["healer"] }, /Discipline.*Holy/],
  [{ class: ["shaman"], role: ["dps"] }, /Elemental.*Enhancement/],
  [{ class: ["druid"], role: ["dps"] }, /Balance.*Feral/],
  [{ class: ["hunter"], role: ["dps"] }, /Beast Mastery.*Marksmanship.*Survival/],
  [{ class: ["mage"], role: ["dps"] }, /Arcane.*Fire.*Frost/],
  [{ class: ["rogue"], role: ["dps"] }, /Assassination.*Combat.*Subtlety/],
  [{ class: ["warlock"], role: ["dps"] }, /Affliction.*Demonology.*Destruction/],
  [{ class: ["death-knight"], role: ["tank"] }, /Blood.*Frost.*Unholy/]
];
for (const [filters, pattern] of ambiguityCases) {
  const resolved = core.resolveContext(state("", filters), catalog);
  assert.equal(resolved.state.filters.specialization, undefined);
  assert.match(resolved.note, pattern);
}

const feralOnly = core.resolveContext(state("", { class: ["druid"], specialization: ["druid-feral"] }), catalog);
assert.equal(feralOnly.state.filters.role, undefined);
assert.match(feralOnly.note, /Tank or DPS/);
const frostDk = core.resolveContext(state("", { class: ["death-knight"], specialization: ["death-knight-frost"] }), catalog);
assert.equal(frostDk.state.filters.role, undefined, "WotLK Frost DK must not silently become Tank or DPS");
assert.match(frostDk.note, /Tank or DPS/);

const paladinTankRaid = ids("", { class: ["paladin"], role: ["tank"], activity: ["raids"] });
assert.ok(paladinTankRaid.includes("pallypower"));
assert.ok(paladinTankRaid.includes("deadly-boss-mods"));
assert.ok(paladinTankRaid.includes("ratingbuster"));
assert.ok(ids("", { role: ["tank"] }).includes("healbot"));
assert.ok(ids("", { activity: ["raids"] }).includes("deadly-boss-mods"));
assert.equal(ids("").length, 10);
assert.equal(ids("", { profession: ["alchemy"] }).length, 0);

const questie = addons.find((addon) => addon.id === "questie");
assert.ok(ids("", { activity: ["leveling"] }).includes("questie"));
const questieLeveling = core.recommendationFor(questie, state("", { activity: ["leveling"] }), catalog);
assert.equal(questieLeveling.importance, "essential");
assert.deepEqual(questieLeveling.purposes, ["leveling"]);
assert.equal(questie.compatibility.downloadVersion, "9.6.2-335");
assert.equal(questie.compatibility.hellscreamTested, true);
assert.equal(questie.compatibility.hellscreamTestedDate, "2026-07-23");
assert.ok(questie.tags.includes("tested-hellscream"));

const parsedLegacy = core.parseUrlState(
  "https://example.test/guides/addons.html?q=healbt&class=paladin&spec=protection&role=tank#import=ignored&addon=healbot",
  catalog
);
assert.equal(parsedLegacy.query, "healbt");
assert.deepEqual(parsedLegacy.filters.class, ["paladin"]);
assert.deepEqual(parsedLegacy.filters.specialization, ["paladin-protection"]);
assert.deepEqual(parsedLegacy.filters.role, ["tank"]);
assert.equal(parsedLegacy.addon, "healbot");

const serialized = core.stateToUrl(parsedLegacy, "https://example.test/guides/addons.html", catalog);
assert.equal(serialized.searchParams.get("spec"), "paladin-protection");
const restored = core.parseUrlState(serialized, catalog);
assert.deepEqual(restored.filters, parsedLegacy.filters);
assert.equal(restored.addon, "healbot");

const priestState = state("", { class: ["priest"], role: ["healer"] });
assert.equal(core.customizationFor(healbot, priestState, catalog), null);
assert.equal(core.recommendationFor(healbot, priestState, catalog), null);

console.log(`Addon search tests passed: ${searchCases.length} fuzzy cases plus canonical, inferred, ambiguous, URL, and isolation checks.`);
