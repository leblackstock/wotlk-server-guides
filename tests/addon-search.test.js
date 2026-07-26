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
  ["quest helper", "questie"],
  ["skadaa", "skada"],
  ["dps meter", "skada"],
  ["chat addon", "chatter"],
  ["chat timestamps", "chatter"],
  ["auction house", "auctioneer-suite"],
  ["auctioneer", "auctioneer-suite"],
  ["addon control", "addon-control-panel"],
  ["acp", "addon-control-panel"],
  ["bartender", "bartender4"],
  ["action bars", "bartender4"],
  ["outfitter", "outfitter"],
  ["gear sets", "outfitter"],
  ["pawn", "pawn"],
  ["stat weights", "pawn"],
  ["upgrade score", "pawn"],
  ["atlas loot", "atlasloot-hellscream"],
  ["custom loot", "atlasloot-hellscream"],
  ["dungeon maps", "atlasloot-hellscream"]
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
assert.equal(ids("").length, 18);
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

const skada = addons.find((addon) => addon.id === "skada");
assert.ok(ids("", { activity: ["raids"] }).includes("skada"));
assert.ok(ids("", { role: ["healer"] }).includes("skada"));
const skadaRaid = core.recommendationFor(skada, state("", { activity: ["raids"] }), catalog);
assert.equal(skadaRaid.importance, "recommended");
assert.deepEqual(skadaRaid.purposes, ["performance"]);
assert.equal(skada.compatibility.downloadVersion, "1.8.87");
assert.equal(skada.compatibility.hellscreamTested, true);
assert.equal(skada.compatibility.hellscreamTestedDate, "2026-07-23");
assert.ok(skada.tags.includes("tested-hellscream"));

const chatter = addons.find((addon) => addon.id === "chatter");
assert.equal(chatter.compatibility.downloadVersion, "1.0");
assert.equal(chatter.compatibility.hellscreamTested, true);
assert.equal(chatter.compatibility.hellscreamTestedDate, "2026-07-23");
assert.ok(chatter.tags.includes("tested-hellscream"));
assert.match(chatter.compatibility.notes.join(" "), /Use guildnotes/);
assert.match(chatter.generalSetup.join(" "), /Modules.*Alt Linking/);
assert.equal(chatter.download.url, "https://warperia.com/addon-wotlk/chatter/");
const chatterRole = core.recommendationFor(chatter, state("", { role: ["healer"] }), catalog);
assert.equal(chatterRole.importance, "optional");
assert.deepEqual(chatterRole.purposes, ["communication"]);

const auctioneer = addons.find((addon) => addon.id === "auctioneer-suite");
assert.equal(auctioneer.compatibility.downloadVersion, "5.9.4961");
assert.equal(auctioneer.compatibility.hellscreamTested, true);
assert.equal(auctioneer.compatibility.hellscreamTestedDate, "2026-07-24");
assert.equal(auctioneer.download.url, "https://web.archive.org/web/20110112162840/http://auctioneeraddon.com/dl/Release/AuctioneerSuite-5.9.4961.zip");
assert.equal(auctioneer.moduleGroups.length, 5);
assert.equal(auctioneer.moduleGroups.flatMap((group) => group.items).length, 43);
assert.ok(auctioneer.moduleGroups.flatMap((group) => group.items).some((item) => item.name === "BeanCounter" && /transaction journal/.test(item.description)));
assert.ok(auctioneer.moduleGroups.flatMap((group) => group.items).some((item) => item.name === "Auc-Util-Appraiser" && /Advanced posting/.test(item.description)));
const auctioneerRole = core.recommendationFor(auctioneer, state("", { role: ["dps"] }), catalog);
assert.equal(auctioneerRole.importance, "recommended");
assert.deepEqual(auctioneerRole.purposes, ["economy"]);


const acp = addons.find((addon) => addon.id === "addon-control-panel");
assert.equal(acp.compatibility.downloadVersion, "3.3.5");
assert.equal(acp.compatibility.hellscreamTested, true);
assert.equal(acp.compatibility.hellscreamTestedDate, "2026-07-25");
assert.equal(acp.compatibility.verifiedDownload, true);
assert.ok(acp.tags.includes("tested-hellscream"));
assert.ok(!acp.tags.includes("not-tested-hellscream"));
assert.equal(acp.download.url, "https://warperia.com/addon-wotlk/addon-control-panel/");
assert.match(acp.compatibility.notes.join(" "), /extensively tested and works on the server/);
assert.match(acp.compatibility.notes.join(" "), /ACP 3\.3\.7 is not compatible/);
const acpRole = core.recommendationFor(acp, state("", { role: ["dps"] }), catalog);
assert.equal(acpRole.importance, "recommended");
assert.deepEqual(acpRole.purposes, ["addon-management"]);

const bartender4 = addons.find((addon) => addon.id === "bartender4");
assert.equal(bartender4.compatibility.downloadVersion, "4.4.2-12-g94f3b58");
assert.equal(bartender4.compatibility.hellscreamTested, true);
assert.equal(bartender4.compatibility.hellscreamTestedDate, "2026-07-24");
assert.equal(bartender4.download.url, "https://www.curseforge.com/wow/addons/bartender4/files/439962");
assert.ok(bartender4.tags.includes("tested-hellscream"));
assert.match(bartender4.compatibility.notes.join(" "), /No addon conflicts/);
assert.match(bartender4.compatibility.notes.join(" "), /Vehicle action bars still need focused testing/);
const bartenderRole = core.recommendationFor(bartender4, state("", { role: ["dps"] }), catalog);
assert.equal(bartenderRole.importance, "recommended");
assert.deepEqual(bartenderRole.purposes, ["action-bars"]);
assert.match(bartenderRole.summary, /top action-bar recommendation/i);

const outfitter = addons.find((addon) => addon.id === "outfitter");
assert.equal(outfitter.compatibility.downloadVersion, "5.0");
assert.equal(outfitter.compatibility.hellscreamTested, true);
assert.equal(outfitter.compatibility.hellscreamTestedDate, "2026-07-24");
assert.equal(outfitter.download.url, "https://warperia.com/addon-wotlk/outfitter/");
assert.ok(outfitter.tags.includes("tested-hellscream"));
assert.match(outfitter.compatibility.notes.join(" "), /No addon conflicts were noticed/);
const outfitterRole = core.recommendationFor(outfitter, state("", { role: ["healer"] }), catalog);
assert.equal(outfitterRole.importance, "recommended");
assert.deepEqual(outfitterRole.purposes, ["equipment-sets"]);

const pawn = addons.find((addon) => addon.id === "pawn");
assert.equal(pawn.compatibility.downloadVersion, "1.3.8");
assert.equal(pawn.compatibility.hellscreamTested, true);
assert.equal(pawn.compatibility.hellscreamTestedDate, "2026-07-25");
assert.equal(pawn.download.url, "https://warperia.com/addon-wotlk/pawn/");
assert.ok(pawn.tags.includes("tested-hellscream"));
assert.match(pawn.compatibility.notes.join(" "), /no errors are remembered/i);
assert.match(pawn.generalSetup.join(" "), /\/pawn list Scale Name/);
assert.match(pawn.generalSetup.join(" "), /copy the chosen built-in scale/i);
assert.match(pawn.generalSetup.join(" "), /\/pawn import/);
const pawnRole = core.recommendationFor(pawn, state("", { role: ["tank"] }), catalog);
assert.equal(pawnRole.importance, "recommended");
assert.deepEqual(pawnRole.purposes, ["gear-evaluation"]);

const atlasLoot = addons.find((addon) => addon.id === "atlasloot-hellscream");
assert.equal(atlasLoot.compatibility.downloadVersion, "Hellscream 2026-02-05 · base v5.11.04");
assert.equal(atlasLoot.compatibility.hellscreamTested, true);
assert.equal(atlasLoot.compatibility.hellscreamTestedDate, "2026-07-25");
assert.equal(atlasLoot.download.url, "https://discord.com/channels/608456284643262504/1328533521983340574/1469088948956434493");
assert.equal(atlasLoot.prerequisiteLinks[0].url, "https://discord.gg/pe69BfNZG5");
assert.equal(atlasLoot.prerequisiteLinks[0].label, "Join the Hellscream Discord ↗");
assert.equal(atlasLoot.download.label, "Open the AtlasLoot Download Post ↗");
assert.match(atlasLoot.generalSetup[0], /Join the Hellscream Discord/);
assert.match(atlasLoot.generalSetup[0], /button above/);
assert.doesNotMatch(atlasLoot.generalSetup[0], /below/);
assert.equal(atlasLoot.alternateDownloads[0].url, "https://warperia.com/addon-wotlk/atlasloot-enhanced/");
assert.ok(atlasLoot.tags.includes("tested-hellscream"));
assert.ok(atlasLoot.tags.includes("server-sensitive"));
assert.match(atlasLoot.compatibility.notes.join(" "), /Burning Crusade heroic items/);
assert.match(atlasLoot.compatibility.notes.join(" "), /Crimson Crusade reputation items/);
assert.match(atlasLoot.generalSetup.join(" "), /install.*together|every included/i);
const atlasLootRole = core.recommendationFor(atlasLoot, state("", { role: ["dps"] }), catalog);
assert.equal(atlasLootRole.importance, "recommended");
assert.deepEqual(atlasLootRole.purposes, ["loot-reference"]);

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
