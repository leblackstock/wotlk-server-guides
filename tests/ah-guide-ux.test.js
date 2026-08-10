const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");
const { JSDOM } = require("jsdom");

const root = path.resolve(__dirname, "..");
const read = (relativePath) => fs.readFileSync(path.join(root, relativePath), "utf8");
const manifest = JSON.parse(read("data/ah-guides.json"));
const version = "20260810-ah-desktop-table-v2";
const hubSearchVersion = "20260810-ah-desktop-table-v2";
const navDataSource = read("assets/ah-guide-navigation-data.js");
const navSource = read("assets/ah-guide-navigation.js");
const sourceNotesSource = read("assets/ah-source-notes.js");
const ahPriceGuideCss = read("assets/ah-price-guide.css");

assert.equal(manifest.version, 1);
assert.equal(manifest.active_guide_count, 19);
assert.equal(manifest.guides.length, 19);
assert.equal(manifest.groups.length, 4);
assert.equal(new Set(manifest.guides.map((guide) => guide.id)).size, 19);
assert.equal(new Set(manifest.guides.map((guide) => guide.file)).size, 19);
assert.equal(
  manifest.redirects.some((redirect) => manifest.guides.some((guide) => guide.file === redirect.file)),
  false,
  "Active guides and compatibility redirects must not overlap",
);

const hub = new JSDOM(read("auction-house.html")).window.document;
assert.match(hub.querySelector("header .sub").textContent, /all 19 pricing guides/);
const hubGroups = [...hub.querySelectorAll("[data-ah-guide-group]")];
assert.equal(hubGroups.length, manifest.groups.length);
assert.ok(hub.querySelector(`link[href="./assets/style.css?v=${hubSearchVersion}"]`));
assert.ok(hub.querySelector(`link[href="./assets/ah-guide-icons.css?v=${version}"]`));
assert.deepEqual(
  hubGroups.map((group) => group.dataset.ahGuideGroup),
  [...manifest.groups].sort((a, b) => a.order - b.order).map((group) => group.id),
);

const multiGuideCards = manifest.hub_cards.filter((card) => card.type === "multi-guide");
const groupedGuideIds = new Set(multiGuideCards.flatMap((card) => card.links.map((link) => link.guide_id)));
const groupedCollections = manifest.collections.filter((collection) => collection.group);
const expectedHubCardCount = manifest.guides.length - groupedGuideIds.size + manifest.hub_cards.length + groupedCollections.length;
const hubCards = [...hub.querySelectorAll(".guide-card.has-guide-icon")];
assert.equal(hubCards.length, expectedHubCardCount);
assert.equal(hub.querySelectorAll(".ah-hub-route-card").length, 4);
assert.equal(hub.querySelectorAll(".ah-hub-route-card:not(.ah-hub-link-card)").length, 3);
assert.equal(hub.querySelectorAll(".ah-hub-link-card").length, 1);
assert.ok(hub.querySelector(`script[src="./assets/ah-search-index.js?v=${hubSearchVersion}"]`));
assert.ok(hub.querySelector(`script[src="./assets/ah-search.js?v=${hubSearchVersion}"]`));
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
for (const collection of groupedCollections) {
  const card = hub.querySelector(`[data-ah-collection-card="${collection.id}"]`);
  assert.ok(card, `${collection.file}: missing hub collection card`);
  assert.equal(card.tagName, "A");
  assert.equal(card.getAttribute("href"), `./guides/${collection.file}`);
  assert.equal(card.querySelector(".guide-title").textContent.trim(), collection.title);
  assert.equal(card.querySelector(".guide-note").textContent.trim(), collection.description);
  assert.equal(card.querySelector(".badge").textContent.trim(), collection.badge);
  assert.equal(card.querySelector("img").getAttribute("src"), `./assets/ah-guide-icons/${collection.icon}`);
  assert.equal(card.closest("[data-ah-guide-group]").dataset.ahGuideGroup, collection.group);
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
  assert.ok(document.querySelector("footer").textContent.endsWith("Updated 2026-08-10"), guide.file);
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
    "ah-source-notes.js",
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
  const runtimeDocument = runtime.window.document;
  const eligibleRows = [...runtimeDocument.querySelectorAll("table > tbody > tr")].filter((row) => {
    const cells = [...row.children];
    return cells.some((cell) => cell.matches('td[data-column="notes"]'))
      && (cells.some((cell) => cell.matches('td[data-column="item"]')) || row.cells[0]);
  });
  const originalNotes = eligibleRows.map((row) =>
    [...row.children].find((cell) => cell.matches('td[data-column="notes"]')).textContent.replace(/\s+/g, " ").trim()
  );
  runtime.window.eval(navDataSource);
  runtime.window.eval(navSource);
  runtime.window.eval(sourceNotesSource);
  if (!runtime.window.document.querySelector("[data-ah-major-nav] .ah-category-chip")) {
    runtime.window.document.dispatchEvent(new runtime.window.Event("DOMContentLoaded"));
  }
  runtime.window.AH_SOURCE_NOTES.initialize();

  assert.equal(
    runtimeDocument.querySelectorAll(".ah-source-notes-toggle").length,
    eligibleRows.length,
    `${guide.file}: source-notes action count`,
  );
  assert.equal(
    runtimeDocument.querySelectorAll(".ah-source-notes-detail").length,
    eligibleRows.length,
    `${guide.file}: source-notes detail count`,
  );
  assert.equal(
    runtimeDocument.querySelectorAll('[class*="source-type"], [class*="acquisition-type"]').length,
    0,
    `${guide.file}: source-type chips are not allowed`,
  );
  eligibleRows.forEach((row, index) => {
    const itemCell = [...row.children].find((cell) => cell.matches('td[data-column="item"]')) || row.cells[0];
    const toggle = itemCell.querySelector(".ah-source-notes-toggle");
    const detail = row.nextElementSibling;
    assert.equal(row.dataset.ahSourceNotesReady, "true", `${guide.file}: row ${index + 1} was not enhanced`);
    assert.ok(toggle, `${guide.file}: row ${index + 1} is missing its action`);
    assert.equal(toggle.textContent, "Source & notes", `${guide.file}: row ${index + 1} action label`);
    assert.equal(toggle.getAttribute("aria-expanded"), "false", `${guide.file}: row ${index + 1} initial state`);
    assert.equal(detail.id, toggle.getAttribute("aria-controls"), `${guide.file}: row ${index + 1} control target`);
    assert.equal(detail.className, "ah-source-notes-detail", `${guide.file}: row ${index + 1} detail class`);
    assert.equal(detail.hidden, true, `${guide.file}: row ${index + 1} detail must start closed`);
    assert.equal(
      detail.querySelector(".ah-source-notes-panel-body").textContent.replace(/\s+/g, " ").trim(),
      originalNotes[index],
      `${guide.file}: row ${index + 1} note content changed`,
    );
  });

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
    .filter((section) => !section.classList.contains("crafted-market-intro"))
    .filter((section) => [...section.children].some((child) => child.tagName === "H2"))
    .filter((section) => !/^(What is covered|Excluded and pending verification|Sources|Disclaimer)$/.test(sectionTitle(section)))
    .filter((section) => section.dataset.ahNavCovered !== "true")
    .map(sectionTitle);
  assert.deepEqual(uncovered, [], `${guide.file}: guide categories missing from chip navigation`);

  for (const back of runtimeDocument.querySelectorAll(".ah-category-heading .ah-back-to-parent")) {
    const top = back.parentElement.querySelector(".ah-back-to-top");
    assert.ok(top, `${guide.file}: parent control is missing its Top partner`);
    assert.equal(back.nextElementSibling, top, `${guide.file}: parent control must immediately precede Top`);
  }

  if (guide.id === "collectibles") {
    assert.equal(runtimeDocument.querySelector('.ah-guide-major-nav a[href="#collectibles-reference"]'), null);
    assert.equal(runtimeDocument.getElementById("collectibles-reference"), null);
    const excluded = runtimeDocument.getElementById("ah-section-excluded-and-pending-verification");
    const covered = runtimeDocument.getElementById("ah-section-what-is-covered");
    const sources = runtimeDocument.getElementById("ah-section-sources");
    const disclaimer = runtimeDocument.getElementById("ah-section-disclaimer");
    assert.equal(excluded.nextElementSibling, covered);
    assert.equal(covered.nextElementSibling, sources);
    assert.equal(sources.nextElementSibling, disclaimer);

    const expandableTable = [...runtimeDocument.querySelectorAll("table.ah-source-notes-ready")]
      .find((table) => table.querySelectorAll(".ah-source-notes-toggle").length >= 2);
    const toggles = [...expandableTable.querySelectorAll(".ah-source-notes-toggle")];
    const firstDetail = runtimeDocument.getElementById(toggles[0].getAttribute("aria-controls"));
    const secondDetail = runtimeDocument.getElementById(toggles[1].getAttribute("aria-controls"));
    toggles[0].click();
    assert.equal(firstDetail.hidden, false);
    assert.equal(toggles[0].textContent, "Hide notes");
    toggles[1].click();
    assert.equal(firstDetail.hidden, true);
    assert.equal(toggles[0].textContent, "Source & notes");
    assert.equal(secondDetail.hidden, false);
    secondDetail.querySelector(".ah-source-notes-close").click();
    assert.equal(secondDetail.hidden, true);
    assert.equal(runtimeDocument.activeElement, toggles[1]);
  }

  if (guide.id === "enchanting") {
    assert.equal(runtimeDocument.querySelectorAll(".crafted-note-ref").length, 276);
    assert.equal(runtimeDocument.querySelectorAll(".crafted-item-note").length, 276);
    assert.equal(runtimeDocument.querySelectorAll(".crafted-recipe-link").length, 276);
  }
}

assert.match(ahPriceGuideCss, /@media \(min-width: 761px\)/);
assert.match(ahPriceGuideCss, /@media \(max-width: 760px\)/);
assert.match(ahPriceGuideCss, /--ah-source-notes-action:\s*#79ddc7/);
assert.match(ahPriceGuideCss, /\.ah-category-heading \.ah-back-to-top\s*\{\s*margin-left:\s*auto;/);
assert.match(ahPriceGuideCss, /tr\.ah-row-pulse\s*\{\s*animation:\s*ah-row-pulse/);
assert.doesNotMatch(ahPriceGuideCss, /ah-row-pulse-cell/);

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
assert.deepEqual(
  Array.from(
    navContext.window.AH_GUIDE_NAVIGATION.guides["sought-after-world-drops"].navigation,
    (entry) => entry.id,
  ),
  ["world-northrend", "world-outland", "world-classic", "world-containers"],
);

const indexContext = { window: {} };
vm.runInNewContext(read("assets/ah-search-index.js"), indexContext);
const searchIndex = indexContext.window.AH_SEARCH_INDEX;
assert.equal(searchIndex.version, 5);
assert.equal(searchIndex.guideCount, 19);
assert.equal(searchIndex.itemCount, 4089);
assert.equal(searchIndex.vendorRecommendationCount, 483);
assert.equal(new Set(searchIndex.items.map((item) => item.name)).size, 3848);
assert.equal(new Set(searchIndex.items.map((item) => item.guideId)).size, 19);

const counts = Object.fromEntries(
  manifest.guides.map((guide) => [
    guide.id,
    searchIndex.items.filter((item) => item.guideId === guide.id).length,
  ]),
);
assert.equal(counts["blacksmithing-materials"], 110);
assert.equal(counts["blacksmithing-gear"], 401);
assert.equal(counts["jewelcrafting-gems"], 419);
assert.equal(counts["jewelcrafting-jewelry"], 142);
assert.equal(counts["turn-ins"], 75);
assert.equal(counts["recipe-pattern-drops"], 90);
assert.equal(counts["level-80-boe-epics"], 85);
assert.equal(counts["sought-after-world-drops"], 283);
assert.equal(counts.collectibles, 128);

console.log("AH manifest, hub cards, compact guide UX, redirects, and split/merged index counts are current.");
