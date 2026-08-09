"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const { JSDOM } = require("jsdom");

const root = path.resolve(__dirname, "..");
const read = (relativePath) => fs.readFileSync(path.join(root, relativePath), "utf8");
const guideSource = read("guides/jewelcrafting-gems-ah-price-guide.html");
const finderSource = read("assets/ah-gem-finder.js");
const staticDocument = new JSDOM(guideSource).window.document;

assert.ok(staticDocument.querySelector('link[href="../assets/ah-gem-finder.css?v=20260808-cut-gem-finder-v2"]'));
assert.ok(staticDocument.querySelector('script[src="../assets/ah-gem-finder.js?v=20260808-cut-gem-finder-v2"]'));
assert.equal(staticDocument.querySelectorAll("[data-ah-gem-finder]").length, 1);
const staticFinder = staticDocument.querySelector("[data-ah-gem-finder]");
assert.equal(staticFinder.tagName, "DETAILS");
assert.equal(staticFinder.open, false, "The Cut Gem Finder must be collapsed by default");
assert.ok(staticFinder.querySelector("summary.ah-gem-finder-heading"));
assert.ok(staticFinder.querySelector("[data-gem-cut-count]"));
assert.equal(staticFinder.querySelector("summary .ah-back-to-top"), null);
assert.equal(staticDocument.querySelectorAll("[data-ah-gem-finder] [data-gem-stat]").length, 18);
assert.equal(staticDocument.querySelectorAll("[data-gem-filter-group='tier']").length, 4);
assert.equal(staticDocument.querySelectorAll("[data-gem-filter-group='socket']").length, 5);
assert.ok(
  guideSource.indexOf("data-ah-gem-finder") < guideSource.indexOf("<!-- AH_CRAFTED_SECTION_START -->"),
  "The page-specific finder must stay outside the generated crafted block",
);
assert.ok(
  guideSource.indexOf("data-ah-gem-finder") < guideSource.indexOf('<details class="common ah-guide-notes">'),
  "The page-specific finder must stay directly below the global AH search",
);
assert.ok(
  guideSource.indexOf('src="../assets/ah-gem-finder.js') > guideSource.indexOf("<!-- AH_GUIDE_SCRIPTS_START -->")
    && guideSource.indexOf('src="../assets/ah-gem-finder.js') < guideSource.indexOf("<!-- AH_GUIDE_SCRIPTS_END -->"),
  "The page-specific script must stay in the canonical shared-script block",
);

const runtime = new JSDOM(guideSource, {
  runScripts: "outside-only",
  url: "http://127.0.0.1/guides/jewelcrafting-gems-ah-price-guide.html",
});
runtime.window.HTMLElement.prototype.scrollIntoView = () => {};
runtime.window.eval(finderSource);
runtime.window.document.dispatchEvent(new runtime.window.Event("DOMContentLoaded"));

const document = runtime.window.document;
const finder = document.querySelector("[data-ah-gem-finder]");
const status = document.querySelector("#ah-gem-status");
const results = document.querySelector("#ah-gem-results");
const input = document.querySelector("#ah-gem-search-input");
const sourceCutCount = document.querySelectorAll(".ah-crafted-market tr[data-crafted-key]").length;
const click = (selector) => {
  const matches = document.querySelectorAll(selector);
  assert.equal(matches.length, 1, `Expected one control for ${selector}`);
  matches[0].click();
};

assert.equal(finder.dataset.gemFinderReady, "true");
assert.equal(Number(finder.dataset.cutCount), sourceCutCount);
assert.equal(finder.querySelector("[data-gem-cut-count]").textContent, `${sourceCutCount} cuts`);
assert.ok(sourceCutCount >= 350);
assert.equal(results.hidden, true);
assert.match(status.textContent, new RegExp(`^${sourceCutCount} cut gems available`));
assert.equal(runtime.window.AHGemFinderCore.normalize("ArP and MP5"), "armor penetration and mana every 5 seconds");
assert.equal(runtime.window.AHGemFinderCore.parseMoney("1,575g 50s"), 15755000);

click('[data-gem-stat="strength"]');
let resultCards = [...document.querySelectorAll(".ah-gem-result")];
assert.ok(resultCards.length > 0);
assert.ok(resultCards.every((card) => card.dataset.gemStats.split(" ").includes("strength")));
assert.equal(document.querySelector('[data-gem-stat="strength"]').getAttribute("aria-pressed"), "true");

click('[data-gem-stat="stamina"]');
resultCards = [...document.querySelectorAll(".ah-gem-result")];
assert.ok(resultCards.length > 0);
assert.ok(resultCards.every((card) => {
  const stats = card.dataset.gemStats.split(" ");
  return stats.includes("strength") && stats.includes("stamina");
}), "Multiple stat chips must use AND matching");

click('[data-gem-filter-group="tier"][data-gem-filter-value="epic"]');
click('[data-gem-filter-group="socket"][data-gem-filter-value="red"]');
resultCards = [...document.querySelectorAll(".ah-gem-result")];
assert.ok(resultCards.length > 0);
assert.ok(resultCards.every((card) => card.dataset.gemTier === "epic"));
assert.ok(resultCards.every((card) => card.dataset.gemSockets.split(" ").includes("red")));
assert.equal(document.querySelectorAll(".ah-gem-active-chip").length, 4);
assert.match(resultCards[0].getAttribute("href"), /^#ah-item=/);

click("#ah-gem-more-stats");
assert.equal(document.querySelector("#ah-gem-more-stats").getAttribute("aria-expanded"), "true");
assert.equal(document.querySelector("#ah-gem-extra-stats").hidden, false);

click("#ah-gem-clear");
assert.equal(input.value, "");
assert.equal(results.hidden, true);
assert.equal(document.querySelectorAll('[data-gem-stat][aria-pressed="true"]').length, 0);
assert.equal(document.querySelector('[data-gem-filter-group="tier"][aria-pressed="true"]').dataset.gemFilterValue, "all");
assert.equal(document.querySelector('[data-gem-filter-group="socket"][aria-pressed="true"]').dataset.gemFilterValue, "any");

input.value = "ArP";
input.dispatchEvent(new runtime.window.Event("input", { bubbles: true }));
resultCards = [...document.querySelectorAll(".ah-gem-result")];
assert.ok(resultCards.length > 0);
assert.ok(resultCards.every((card) => /Armor Penetration/i.test(card.querySelector(".ah-gem-result-effect").textContent)));

input.value = "strength stamina";
input.dispatchEvent(new runtime.window.Event("input", { bubbles: true }));
resultCards = [...document.querySelectorAll(".ah-gem-result")];
assert.ok(resultCards.length > 0);
assert.ok(resultCards.every((card) => {
  const effect = card.querySelector(".ah-gem-result-effect").textContent;
  return /Strength/i.test(effect) && /Stamina/i.test(effect);
}));

runtime.window.close();
console.log(`Cut Gem Finder filters ${sourceCutCount} rendered cuts by stats, tier, socket, aliases, and AND queries.`);
