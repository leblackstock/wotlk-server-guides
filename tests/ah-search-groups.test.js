"use strict";

const assert = require("node:assert/strict");

globalThis.window = globalThis;
require("../assets/ah-search.js");
require("../assets/ah-search-index.js");

const { normalize, searchItems, uniqueItemCount } = globalThis.AHSearchCore;
const index = globalThis.AH_SEARCH_INDEX;

const expectedUniqueCount = new Set(index.items.map((item) => normalize(item.name))).size;
assert.equal(uniqueItemCount(index.items), expectedUniqueCount);
assert.ok(expectedUniqueCount < index.itemCount);

const saronite = searchItems(index.items, "saronite");
assert.equal(saronite.length, 5);
assert.equal(new Set(saronite.map((item) => normalize(item.name))).size, saronite.length);

const saroniteBar = saronite.find((item) => item.name === "Saronite Bar");
assert.ok(saroniteBar);
assert.equal(saroniteBar.matches.length, 4);
assert.equal(new Set(saroniteBar.matches.map((item) => item.guide)).size, 3);
assert.deepEqual(new Set(saroniteBar.matches.map((item) => item.targetBid)), new Set(["1g 28s"]));
assert.deepEqual(new Set(saroniteBar.matches.map((item) => item.target)), new Set(["1g 50s"]));

const autumnsGlow = searchItems(index.items, "Autumn's Glow").find((item) => item.name === "Autumn's Glow");
assert.ok(autumnsGlow);
assert.equal(autumnsGlow.matches.length, 2);
assert.equal(new Set(autumnsGlow.matches.map((item) => item.target)).size, 1);

const broadSearch = searchItems(index.items, "bar");
assert.equal(broadSearch.length, 12);
assert.equal(new Set(broadSearch.map((item) => normalize(item.name))).size, broadSearch.length);

console.log("Auction House search groups duplicate item rows into unique results.");
