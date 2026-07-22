"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const core = require("../assets/addon-search-core.js");
const catalog = JSON.parse(fs.readFileSync(path.join(__dirname, "../data/addons.json"), "utf8"));
const addons = catalog.addons;

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
  ["969 trainer", "protection-is-surprisingly-stupendous"]
];

for (const [query, expected] of searchCases) {
  assert.equal(first(query), expected, `${query} should rank ${expected} first`);
}

const protResults = ids("prot pally");
assert.ok(protResults.includes("pallypower"), "prot pally should find Paladin-specific addons");
assert.ok(protResults.includes("healbot"), "prot pally should find targeted universal addons");

const righteousUs = ids("righteous defense");
const righteousUk = ids("righteous defence");
for (const list of [righteousUs, righteousUk]) {
  assert.ok(list.includes("healbot"), "Righteous Defense should find HealBot");
  assert.ok(list.includes("tauntmaster"), "Righteous Defense should find TauntMaster");
}

assert.deepEqual(
  ids("", { class: ["paladin"], specialization: ["protection"], role: ["tank"] }).slice(0, 2),
  ["deadly-boss-mods", "pallypower"],
  "Essential Protection results should sort first"
);

const paladinTankRaid = ids("", { class: ["paladin"], role: ["tank"], activity: ["raids"] });
assert.ok(paladinTankRaid.includes("pallypower"));
assert.ok(paladinTankRaid.includes("deadly-boss-mods"));
assert.ok(paladinTankRaid.includes("ratingbuster"), "Gearing tools remain relevant to raid-filtered Protection context");

const tankOnly = ids("", { role: ["tank"] });
assert.ok(tankOnly.includes("healbot"));
assert.ok(tankOnly.includes("omen3"));
assert.ok(tankOnly.includes("deadly-boss-mods"));

const raidOnly = ids("", { activity: ["raids"] });
assert.ok(raidOnly.includes("deadly-boss-mods"));
assert.ok(raidOnly.includes("omen3"));

const essential = ids("", { class: ["paladin"], specialization: ["protection"], role: ["tank"], importance: ["essential"] });
assert.deepEqual(new Set(essential), new Set(["pallypower", "deadly-boss-mods"]));

assert.equal(ids("").length, 9, "No filters should return all nine launch addons");
assert.equal(ids("", { profession: ["alchemy"] }).length, 0, "A populated URL with an unused future facet should have no results");
assert.equal(ids("", {}).length, 9, "Clearing filters should restore every addon");

const parsed = core.parseUrlState(
  "https://example.test/guides/addons.html?q=healbt&class=paladin&spec=protection&role=tank#import=ignored&addon=healbot",
  catalog
);
assert.equal(parsed.query, "healbt");
assert.deepEqual(parsed.filters.class, ["paladin"]);
assert.deepEqual(parsed.filters.specialization, ["protection"]);
assert.deepEqual(parsed.filters.role, ["tank"]);
assert.equal(parsed.addon, "healbot");

const serialized = core.stateToUrl(parsed, "https://example.test/guides/addons.html", catalog);
const restored = core.parseUrlState(serialized, catalog);
assert.equal(restored.query, parsed.query);
assert.deepEqual(restored.filters, parsed.filters);
assert.equal(restored.addon, "healbot");

const priestState = state("", { class: ["priest"], role: ["healer"] });
const healbot = addons.find((addon) => addon.id === "healbot");
assert.equal(core.customizationFor(healbot, priestState), null, "Priest Healer must not auto-select Protection Paladin setup");
assert.equal(core.recommendationFor(healbot, priestState), null, "Priest Healer must not receive Protection Paladin recommendation");

const protState = state("", { class: ["paladin"], specialization: ["protection"], role: ["tank"] });
assert.equal(core.customizationFor(healbot, protState).id, "protection-paladin");
assert.equal(core.recommendationFor(healbot, protState).importance, "recommended");

console.log(`Addon search tests passed: ${searchCases.length} fuzzy cases plus filter, URL, and context checks.`);
