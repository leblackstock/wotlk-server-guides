"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const { JSDOM } = require("jsdom");

globalThis.window = globalThis;
require("../assets/ah-search.js");
require("../assets/ah-search-index.js");

const {
  normalize,
  searchItems,
  uniqueItemCount
} = globalThis.AHSearchCore;
const index = globalThis.AH_SEARCH_INDEX;

const expectedUniqueCount = new Set(index.items.map((item) => normalize(item.name))).size;
assert.equal(uniqueItemCount(index.items), expectedUniqueCount);
assert.ok(expectedUniqueCount < index.itemCount);

const saronite = searchItems(index.items, "saronite");
assert.equal(saronite.length, 12);
assert.equal(new Set(saronite.map((item) => normalize(item.name))).size, saronite.length);

const saroniteBar = saronite.find((item) => item.name === "Saronite Bar");
assert.ok(saroniteBar);
assert.equal(saroniteBar.matches.length, 4);
assert.equal(new Set(saroniteBar.matches.map((item) => item.guide)).size, 3);
assert.deepEqual(new Set(saroniteBar.matches.map((item) => item.targetBid)), new Set(["1g 53s"]));
assert.deepEqual(new Set(saroniteBar.matches.map((item) => item.target)), new Set(["1g 80s"]));
assert.deepEqual(new Set(saroniteBar.matches.map((item) => item.stack)), new Set(["5 / 10 / 20"]));
assert.deepEqual(new Set(saroniteBar.matches.map((item) => item.demand)), new Set(["Very High"]));

const autumnsGlow = searchItems(index.items, "Autumn's Glow").find((item) => item.name === "Autumn's Glow");
assert.ok(autumnsGlow);
assert.equal(autumnsGlow.matches.length, 2);
assert.equal(new Set(autumnsGlow.matches.map((item) => item.target)).size, 1);

const broadSearch = searchItems(index.items, "bar");
assert.equal(broadSearch.length, 12);
assert.equal(new Set(broadSearch.map((item) => normalize(item.name))).size, broadSearch.length);

const root = path.resolve(__dirname, "..");
const engineeringGuide = fs.readFileSync(path.join(root, "guides", "engineering-materials-ah-price-guide.html"), "utf8");
const searchSource = fs.readFileSync(path.join(root, "assets", "ah-search.js"), "utf8");
const runtime = new JSDOM(engineeringGuide, {
  runScripts: "outside-only",
  url: "http://127.0.0.1/guides/engineering-materials-ah-price-guide.html",
});
runtime.window.HTMLElement.prototype.scrollIntoView = () => {};
runtime.window.eval(searchSource);
runtime.window.document.dispatchEvent(new runtime.window.Event("DOMContentLoaded"));

assert.equal(runtime.window.document.querySelector("tr.ah-row-selected"), null);
runtime.window.location.hash = "#ah-item=elemental-blasting-powder";
runtime.window.dispatchEvent(new runtime.window.Event("hashchange"));

const selectedRow = runtime.window.document.querySelector("tr.ah-row-selected");
assert.ok(selectedRow, "Same-page AH item links should select their destination row after the hash changes");
assert.equal(selectedRow.querySelector("td:first-child strong").textContent.trim(), "Elemental Blasting Powder");
assert.equal(selectedRow.getAttribute("aria-selected"), "true");
runtime.window.close();

console.log("Auction House search groups duplicate item rows and follows same-page item links.");
require("./ah-gem-finder.test.js");
