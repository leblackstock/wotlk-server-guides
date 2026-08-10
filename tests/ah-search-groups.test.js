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
const indexSource = fs.readFileSync(path.join(root, "assets", "ah-search-index.js"), "utf8");
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
assert.equal(
  runtime.window.document.querySelector('[data-use-audience="general-use"] .profession-audience-chip').textContent,
  "No profession required",
);
assert.equal(
  runtime.window.document.querySelector('[data-use-audience="profession-restricted"] .profession-audience-chip').textContent,
  "Profession required",
);
assert.equal(
  runtime.window.document.querySelector('[data-use-audience="profession-input"] .profession-audience-chip').textContent,
  "Profession buyers",
);
runtime.window.close();

const hubSource = fs.readFileSync(path.join(root, "auction-house.html"), "utf8");
const vendorRuntime = new JSDOM(hubSource, {
  runScripts: "outside-only",
  url: "http://127.0.0.1/auction-house.html",
});
vendorRuntime.window.eval(indexSource);
vendorRuntime.window.eval(searchSource);
vendorRuntime.window.document.dispatchEvent(new vendorRuntime.window.Event("DOMContentLoaded"));
const vendorSearch = vendorRuntime.window.document.querySelector("#ah-search-input");
vendorSearch.value = "Core Felcloth Bag";
vendorSearch.dispatchEvent(new vendorRuntime.window.Event("input", { bubbles: true }));
let vendorChip = vendorRuntime.window.document.querySelector(".ah-search-vendor-chip");
assert.ok(vendorChip);
assert.match(vendorChip.title, /NPC sell value 8g per item/);
assert.match(vendorChip.title, /Target needs at least 8g 85s 62c per item/);

vendorSearch.value = "Raw Spinefin Halibut";
vendorSearch.dispatchEvent(new vendorRuntime.window.Event("input", { bubbles: true }));
vendorChip = vendorRuntime.window.document.querySelector(".ah-search-vendor-chip");
assert.ok(vendorChip);
assert.match(vendorChip.title, /does not justify the expected fees/);
assert.doesNotMatch(vendorChip.title, /—/);
vendorRuntime.window.close();

const manifest = JSON.parse(fs.readFileSync(path.join(root, "data", "ah-guides.json"), "utf8"));
let renderedVendorNotes = 0;
let renderedAudienceLabels = 0;
const audienceLabels = {
  "general-use": "No profession required",
  "profession-restricted": "Profession required",
  "profession-input": "Profession buyers",
  "class-restricted": "Class required",
  "mixed-input-and-general-use": "Mixed use",
};
for (const guide of manifest.guides) {
  const expectedNotes = index.items
    .filter((item) => item.guideId === guide.id && item.vendorRecommended === true)
    .map((item) => `Vendor: ${item.vendorRecommendationNote}`)
    .sort();
  const guideRuntime = new JSDOM(
    fs.readFileSync(path.join(root, "guides", guide.file), "utf8"),
    {
      runScripts: "outside-only",
      url: `http://127.0.0.1/guides/${guide.file}`,
    },
  );
  guideRuntime.window.AH_SEARCH_INDEX = index;
  guideRuntime.window.eval(searchSource);
  const audienceSections = [...guideRuntime.window.document.querySelectorAll("section[data-use-audience]")];
  assert.equal(
    guideRuntime.window.AHSearchCore.initializeProfessionAudienceLabels(),
    audienceSections.length,
    `${guide.file}: wrong profession-audience label count`,
  );
  for (const section of audienceSections) {
    const chips = section.querySelectorAll(":scope > h2 .profession-audience-chip");
    assert.equal(chips.length, 1, `${guide.file}: profession-audience label missing or duplicated`);
    assert.equal(chips[0].textContent, audienceLabels[section.dataset.useAudience]);
  }
  renderedAudienceLabels += audienceSections.length;
  const result = guideRuntime.window.AHSearchCore.initializeVendorNotes();
  const actualNotes = [...guideRuntime.window.document.querySelectorAll(".ah-item-vendor-note")]
    .map((note) => note.textContent.replace(/\s+/g, " ").trim())
    .sort();
  assert.equal(result.expected, expectedNotes.length, `${guide.file}: wrong expected Vendor-note count`);
  assert.equal(result.rendered, expectedNotes.length, `${guide.file}: not every Vendor note found its item row`);
  assert.deepEqual(actualNotes, expectedNotes, `${guide.file}: rendered Vendor notes drifted`);
  renderedVendorNotes += actualNotes.length;
  guideRuntime.window.close();
}
assert.equal(renderedVendorNotes, index.vendorRecommendationCount);
assert.ok(renderedAudienceLabels > 0);

console.log("Auction House search groups duplicate items, follows row links, and renders every Vendor reason in item notes.");
require("./ah-gem-finder.test.js");
