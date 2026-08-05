const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");
const { JSDOM } = require("jsdom");

const root = path.resolve(__dirname, "..");
const read = (relativePath) => fs.readFileSync(path.join(root, relativePath), "utf8");
const manifest = JSON.parse(read("data/ah-guides.json"));
const version = "20260804-ah-dropped-gear-v1";
const navDataSource = read("assets/ah-guide-navigation-data.js");
const navSource = read("assets/ah-guide-navigation.js");

assert.equal(manifest.version, 1);
assert.equal(manifest.active_guide_count, 18);
assert.equal(manifest.guides.length, 18);
assert.equal(manifest.groups.length, 3);
assert.equal(new Set(manifest.guides.map((guide) => guide.id)).size, 18);
assert.equal(new Set(manifest.guides.map((guide) => guide.file)).size, 18);
assert.equal(
  manifest.redirects.some((redirect) => manifest.guides.some((guide) => guide.file === redirect.file)),
  false,
  "Active guides and compatibility redirects must not overlap",
);

const hub = new JSDOM(read("auction-house.html")).window.document;
assert.match(hub.querySelector("header .sub").textContent, /all 18 pricing guides/);
const hubGroups = [...hub.querySelectorAll("[data-ah-guide-group]")];
assert.equal(hubGroups.length, manifest.groups.length);
assert.ok(hub.querySelector('link[href="./assets/style.css?v=20260804-ah-dropped-gear-hub-v1"]'));
assert.ok(hub.querySelector('link[href="./assets/ah-guide-icons.css?v=20260804-ah-dropped-gear-v1"]'));
assert.deepEqual(
  hubGroups.map((group) => group.dataset.ahGuideGroup),
  [...manifest.groups].sort((a, b) => a.order - b.order).map((group) => group.id),
);

const multiGuideCards = manifest.hub_cards.filter((card) => card.type === "multi-guide");
const groupedGuideIds = new Set(multiGuideCards.flatMap((card) => card.links.map((link) => link.guide_id)));
const expectedHubCardCount = manifest.guides.length - groupedGuideIds.size + manifest.hub_cards.length;
const hubCards = [...hub.querySelectorAll(".guide-card.has-guide-icon")];
assert.equal(hubCards.length, expectedHubCardCount);
assert.equal(hub.querySelectorAll(".ah-hub-route-card").length, 4);
assert.equal(hub.querySelectorAll(".ah-hub-route-card:not(.ah-hub-link-card)").length, 3);
assert.equal(hub.querySelectorAll(".ah-hub-link-card").length, 1);
assert.ok(hub.querySelector('script[src="./assets/ah-search-index.js?v=20260804-ah-dropped-gear-v1"]'));
assert.ok(hub.querySelector('script[src="./assets/ah-search.js?v=20260804-ah-dropped-gear-v1"]'));
for (const guide of manifest.guides) {
  if (groupedGuideIds.has(guide.id)) {
    const chip = hub.querySelector(`.ah-hub-card-chip[data-ah-guide-id="${guide.id}"]`);
    assert.ok(chip, `${guide.file}: missing grouped hub destination`);
    assert.equal(chip.getAttribute("href"), `./guides/${guide.file}`);
  } else {
    const card = hub.querySelector(`[data-ah-guide-card="${guide.id}"]`);
    assert.ok(card, `${guide.file}: missing hub card`);
    assert.equal(card.getAttribute("href"), `./guides/${guide.file}`);
    assert.equal(card.querySelector(".guide-title").textContent.trim(), guide.title);
    assert.equal(card.querySelector(".guide-note").textContent.trim(), guide.description);
    assert.equal(card.querySelector("img").getAttribute("src"), `./assets/ah-guide-icons/${guide.icon}`);
  }
}
for (const cardConfig of manifest.hub_cards) {
  const card = hub.querySelector(`[data-ah-hub-card="${cardConfig.id}"]`);
  assert.ok(card, `${cardConfig.id}: missing hub route card`);
  assert.equal(card.tagName, "ARTICLE");
  assert.equal(card.querySelector(".guide-title").textContent.trim(), cardConfig.title);
  assert.equal(card.querySelector(".guide-note").textContent.trim(), cardConfig.description);
  assert.equal(card.querySelector(".badge").textContent.trim(), cardConfig.badge);
  const chips = [...card.querySelectorAll(".ah-hub-card-chip")];
  assert.equal(chips.length, cardConfig.links.length);
  cardConfig.links.forEach((link, index) => {
    const guide = manifest.guides.find((candidate) => candidate.id === link.guide_id);
    const fragment = link.category ? `#ah-category=${link.category}` : "";
    assert.equal(chips[index].textContent.replace(/→/g, "").trim(), link.label);
    assert.equal(chips[index].getAttribute("href"), `./guides/${guide.file}${fragment}`);
  });
}
assert.match(read("assets/style.css"), /\.ah-hub-card-chip\s*\{/);

for (const guide of manifest.guides) {
  const document = new JSDOM(read(`guides/${guide.file}`)).window.document;
  const body = document.body;
  assert.equal(body.dataset.guideSection, "auction-house", guide.file);
  assert.equal(body.dataset.ahGuide, guide.id, guide.file);
  assert.equal(body.dataset.ahRoot, "../", guide.file);
  assert.equal(document.querySelectorAll(".ah-guide-hero").length, 1, guide.file);
  assert.equal(document.querySelector(".ah-guide-hero h1").textContent.trim(), guide.title, guide.file);
  assert.equal(document.querySelector(".ah-guide-hero .sub").textContent.trim(), guide.description, guide.file);
  assert.equal(document.querySelector(".ah-guide-hero img").getAttribute("width"), "64", guide.file);
  assert.equal(document.querySelectorAll("#ah-search-input").length, 1, guide.file);
  assert.equal(document.querySelectorAll("[data-ah-major-nav]").length, 1, guide.file);
  assert.equal(document.querySelectorAll("details.ah-guide-notes").length, 1, guide.file);
  assert.equal(document.querySelector("details.ah-guide-notes").hasAttribute("open"), false, guide.file);
  assert.equal(document.querySelectorAll(".ah-baseline-note").length, 1, guide.file);
  assert.equal(document.querySelectorAll("footer").length, 1, guide.file);
  const expectedUpdatedDate = new Set(["level-80-boe-epics", "sought-after-world-drops"]).has(guide.id)
    ? "2026-08-05"
    : "2026-08-04";
  assert.ok(document.querySelector("footer").textContent.endsWith(`Updated ${expectedUpdatedDate}`), guide.file);
  assert.equal(document.title, `${guide.title} AH Price Guide — WotLK 3.3.5 Low Pop`, guide.file);
  assert.ok(
    document.querySelector(`link[href="../assets/ah-guide-icons.css?v=${version}"]`),
    `${guide.file}: missing shared guide stylesheet`,
  );
  for (const asset of [
    "ah-search-index.js",
    "ah-guide-navigation-data.js",
    "ah-guide-navigation.js",
    "ah-search.js",
  ]) {
    assert.ok(
      document.querySelector(`script[src="../assets/${asset}?v=${version}"]`),
      `${guide.file}: missing ${asset}`,
    );
  }

  const runtime = new JSDOM(read(`guides/${guide.file}`), {
    runScripts: "dangerously",
    url: `http://127.0.0.1/guides/${guide.file}`,
  });
  runtime.window.eval(navDataSource);
  runtime.window.eval(navSource);
  if (!runtime.window.document.querySelector("[data-ah-major-nav] .ah-category-chip")) {
    runtime.window.document.dispatchEvent(new runtime.window.Event("DOMContentLoaded"));
  }
  const runtimeDocument = runtime.window.document;
  const chips = [...runtimeDocument.querySelectorAll(".ah-category-chip")];
  assert.ok(chips.length, `${guide.file}: category navigation rendered no chips`);
  for (const chip of chips) {
    assert.ok(
      runtimeDocument.getElementById(chip.getAttribute("href").slice(1)),
      `${guide.file}: category chip has a missing target: ${chip.textContent.trim()}`,
    );
  }
  const sectionTitle = (section) => {
    const heading = section.querySelector("h2").cloneNode(true);
    heading.querySelectorAll(".ah-back-to-top, .ah-back-to-parent, .ah-category-chip-nav").forEach((node) => node.remove());
    return heading.textContent.replace(/\s+/g, " ").trim();
  };
  const uncovered = [...runtimeDocument.querySelectorAll("section.common")]
    .filter((section) => !section.classList.contains("ah-guide-search-section"))
    .filter((section) => !section.classList.contains("ah-category-banner"))
    .filter((section) => !section.classList.contains("ah-dropped-gear-summary"))
    .filter((section) => !section.classList.contains("crafted-market-intro"))
    .filter((section) => [...section.children].some((child) => child.tagName === "H2"))
    .filter((section) => !/^(Sources|Disclaimer)$/.test(sectionTitle(section)))
    .filter((section) => section.dataset.ahNavCovered !== "true")
    .map(sectionTitle);
  assert.deepEqual(uncovered, [], `${guide.file}: guide categories missing from chip navigation`);
}

for (const redirect of manifest.redirects) {
  const source = read(`guides/${redirect.file}`);
  const document = new JSDOM(source).window.document;
  assert.equal(document.querySelector('meta[http-equiv="refresh"]').getAttribute("content"), `0; url=${redirect.target}`);
  assert.equal(document.querySelector('link[rel="canonical"]').getAttribute("href"), redirect.target);
  assert.equal(document.querySelector("main a").getAttribute("href"), redirect.target);
  assert.match(source, /location\.hash\.startsWith\("#ah-item="\)/);
}

const navContext = { window: {} };
vm.runInNewContext(navDataSource, navContext);
assert.deepEqual(
  Object.keys(navContext.window.AH_GUIDE_NAVIGATION.guides).sort(),
  manifest.guides.map((guide) => guide.id).sort(),
);

const indexContext = { window: {} };
vm.runInNewContext(read("assets/ah-search-index.js"), indexContext);
const searchIndex = indexContext.window.AH_SEARCH_INDEX;
assert.equal(searchIndex.version, 5);
assert.equal(searchIndex.guideCount, 18);
assert.equal(searchIndex.itemCount, 3860);
assert.equal(new Set(searchIndex.items.map((item) => item.name)).size, 3634);
assert.equal(new Set(searchIndex.items.map((item) => item.guideId)).size, 18);

const counts = Object.fromEntries(
  manifest.guides.map((guide) => [
    guide.id,
    searchIndex.items.filter((item) => item.guideId === guide.id).length,
  ]),
);
assert.equal(counts["blacksmithing-materials"], 110);
assert.equal(counts["blacksmithing-gear"], 401);
assert.equal(counts["jewelcrafting-gems"], 418);
assert.equal(counts["jewelcrafting-jewelry"], 142);
assert.equal(counts["recipe-pattern-drops"], 90);
assert.equal(counts["level-80-boe-epics"], 85);
assert.equal(counts["sought-after-world-drops"], 262);

console.log("AH manifest, hub cards, compact guide UX, redirects, and split/merged index counts are current.");
