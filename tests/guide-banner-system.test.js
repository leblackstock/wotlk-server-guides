const assert = require("node:assert/strict");
const { spawnSync } = require("node:child_process");
const fs = require("node:fs");
const path = require("node:path");
const { JSDOM } = require("jsdom");

const root = path.resolve(__dirname, "..");
const families = {
  "protection-paladin": {
    specName: "Protection Paladin",
    nickname: "Tankadin",
    raidType: "Raid Tank Guide"
  },
  "holy-paladin": {
    specName: "Holy Paladin",
    nickname: "Holy Pally",
    raidType: "Raid Healer Guide"
  },
  "blood-death-knight": {
    specName: "Blood Death Knight",
    nickname: "Blood DK",
    quickStartType: "Heroic LK25 Tank",
    quickNavLabel: "LK25 Tank",
    raidType: "Heroic LK25 Tank Playbook"
  },
  "holy-priest": {
    specName: "Holy Priest",
    nickname: "Holy Priest",
    raidType: "Raid Healer Guide"
  },
  "shadow-priest": {
    specName: "Shadow Priest",
    nickname: "Shadow Priest",
    raidType: "Raid DPS Guide"
  },
  "marksmanship-hunter": {
    specName: "Marksmanship Hunter",
    nickname: "Marks Hunter",
    raidType: "Raid DPS Guide",
    quickStartUpdated: "2026-08-05"
  },
  "affliction-warlock": {
    specName: "Affliction Warlock",
    nickname: "Affliction",
    raidType: "Raid DPS Guide",
    quickStartUpdated: "2026-08-14"
  },
  "demonology-warlock": {
    specName: "Demonology Warlock",
    nickname: "Demo Lock",
    raidType: "Raid DPS Guide",
    quickStartUpdated: "2026-08-14"
  },
  "destruction-warlock": {
    specName: "Destruction Warlock",
    nickname: "Destro Lock",
    raidType: "Raid DPS Guide",
    quickStartUpdated: "2026-08-14"
  }
};
const pageTypes = {
  "pve-guide": "Quick Start",
  "playing": "Playing Guide",
  "setting-up": "Setup Guide",
  "gearing": "Build Guide",
  "gear-targets": "Gear Guide",
  "raiding": "Raid Guide"
};

let checked = 0;
for (const [prefix, family] of Object.entries(families)) {
  for (const [suffix, defaultType] of Object.entries(pageTypes)) {
    const relative = `guides/${prefix}-${suffix}.html`;
    const html = fs.readFileSync(path.join(root, relative), "utf8");
    const document = new JSDOM(html).window.document;
    const hero = document.querySelector("header.guide-hero");
    const rail = document.querySelector("nav.guide-jump-nav");
    const expectedType = suffix === "raiding"
      ? family.raidType
      : suffix === "pve-guide" && family.quickStartType
        ? family.quickStartType
        : defaultType;

    assert.ok(hero, `${relative}: shared guide hero is missing`);
    assert.equal(document.querySelectorAll("header.guide-hero").length, 1, `${relative}: expected one guide hero`);
    assert.equal(
      document.querySelectorAll('link[href*="/guide-hero.css"]').length,
      1,
      `${relative}: expected one shared banner stylesheet`
    );
    assert.equal(
      hero.querySelector(".page-kicker")?.textContent.trim(),
      `${family.specName} • WotLK 3.3.5 • Level 80+`,
      `${relative}: metadata line is not standardized`
    );
    assert.equal(
      hero.querySelector(".hero-spec-nickname")?.textContent.trim(),
      family.nickname,
      `${relative}: nickname is incorrect`
    );
    assert.equal(
      hero.querySelector(".hero-guide-type")?.textContent.trim(),
      expectedType,
      `${relative}: guide type is incorrect`
    );
    assert.equal(
      document.querySelector(`.site-nav a[href="${prefix}-pve-guide.html"]`)?.textContent.trim(),
      family.quickNavLabel || "Quick Start",
      `${relative}: first chapter navigation label is incorrect`
    );
    assert.ok(hero.querySelector(".sub")?.textContent.trim(), `${relative}: description is missing`);
    assert.equal(hero.querySelectorAll("img, svg").length, 0, `${relative}: banner must not contain icons`);
    assert.equal(hero.querySelector(".jump-nav"), null, `${relative}: jump chips must be outside the banner`);
    assert.ok(rail, `${relative}: detached jump-chip rail is missing`);
    assert.equal(hero.nextElementSibling, rail, `${relative}: chip rail must immediately follow the banner`);
    assert.equal(rail.querySelectorAll("img, svg").length, 0, `${relative}: chip rail must not contain icons`);

    const jumpLinks = [...rail.querySelectorAll('a[href^="#"]')];
    assert.ok(jumpLinks.length >= 2, `${relative}: expected at least two jump chips`);
    for (const link of jumpLinks) {
      const id = decodeURIComponent(link.getAttribute("href").slice(1));
      assert.ok(document.getElementById(id), `${relative}: unresolved jump target #${id}`);
    }

    assert.match(
      document.querySelector(".wrap > footer")?.textContent.trim() || "",
      /Updated \d{4}-\d{2}-\d{2}$/,
      `${relative}: footer update date is missing`
    );
    checked += 1;
  }
}

const discoveredGuideFiles = fs.readdirSync(path.join(root, "guides"))
  .filter((file) => /-(?:pve-guide|playing|setting-up|gearing|gear-targets|raiding)\.html$/.test(file));
assert.ok(discoveredGuideFiles.length >= checked, "current banner manifest pages are missing");
for (const file of discoveredGuideFiles) {
  const document = new JSDOM(fs.readFileSync(path.join(root, "guides", file), "utf8")).window.document;
  const hero = document.querySelector("header.guide-hero");
  const rail = document.querySelector("nav.guide-jump-nav");
  assert.ok(hero, `guides/${file}: discovered guide is missing the standard banner`);
  assert.ok(rail, `guides/${file}: discovered guide is missing the detached chip rail`);
  assert.equal(hero.nextElementSibling, rail, `guides/${file}: discovered guide has chips inside the banner`);
}

const hubDocument = new JSDOM(fs.readFileSync(path.join(root, "index.html"), "utf8")).window.document;
assert.equal(hubDocument.querySelectorAll(".class-guide-card").length, Object.keys(families).length);
assert.equal(
  hubDocument.querySelectorAll('link[href="./assets/guide-hero.css?v=20260812-guide-identity-card-v3"]').length,
  1,
  "index.html: shared guide-gradient stylesheet is missing"
);
for (const [prefix, family] of Object.entries(families)) {
  const card = hubDocument.querySelector(`.class-guide-card[href="./guides/${prefix}-pve-guide.html"]`);
  const landingDocument = new JSDOM(
    fs.readFileSync(path.join(root, "guides", `${prefix}-pve-guide.html`), "utf8")
  ).window.document;
  assert.ok(card, `index.html: ${prefix} class-guide card is missing`);
  assert.ok(card.classList.contains("guide-identity-gradient"), `index.html: ${prefix} card must reuse the guide-banner gradient`);
  assert.ok(card.classList.contains("guide-identity-gradient--card"), `index.html: ${prefix} card must use the subtle gradient variant`);
  assert.equal(
    card.querySelector(".guide-card-nickname")?.textContent.trim(),
    family.nickname,
    `index.html: ${prefix} card nickname is incorrect`
  );
  assert.equal(
    card.querySelector(".guide-card-type")?.textContent.trim(),
    family.quickStartType || pageTypes["pve-guide"],
    `index.html: ${prefix} card guide type is incorrect`
  );
  assert.equal(card.querySelectorAll(".guide-card-badges .badge").length, 2, `index.html: ${prefix} card needs class and spec chips`);
  assert.equal(
    card.querySelector(".guide-card-spec-badge")?.textContent.trim(),
    family.specName.split(" ")[0],
    `index.html: ${prefix} card spec chip is incorrect`
  );
  assert.equal(
    card.querySelector(".guide-action")?.textContent.trim(),
    "Open guide →",
    `index.html: ${prefix} card action is not neutral`
  );
  assert.equal(
    card.querySelector(".guide-note")?.textContent.trim(),
    landingDocument.querySelector("header.guide-hero .sub")?.textContent.trim(),
    `index.html: ${prefix} card sentence does not match its guide banner`
  );
}

const hubInlineCss = hubDocument.querySelector("style")?.textContent || "";
assert.match(
  hubInlineCss,
  /\.class-guide-card::before\{[^}]*background:var\(--class-guide-class-accent\)/,
  "index.html: class-guide side bar must use the class color token"
);
for (const [cardClass, classToken] of Object.entries({
  "paladin-protection": "class-paladin-accent",
  "paladin-holy": "class-paladin-accent",
  "death-knight-blood": "class-death-knight-accent",
  "priest-holy": "class-priest-accent",
  "priest-shadow": "class-priest-accent",
  "hunter-marksmanship": "class-hunter-accent",
  "warlock-affliction": "class-warlock-accent",
  "warlock-demonology": "class-warlock-accent",
  "warlock-destruction": "class-warlock-accent"
})) {
  assert.match(
    hubInlineCss,
    new RegExp(`\\.class-guide-card\\.${cardClass}\\{[^}]*--class-guide-class-accent:var\\(--${classToken}\\)`),
    `index.html: ${cardClass} side bar does not use its class color`
  );
}
for (const [cardClass, deepTokens] of Object.entries({
  "paladin-protection": ["class-paladin-deep-rgb", "spec-paladin-protection-deep-rgb"],
  "paladin-holy": ["class-paladin-deep-rgb", "spec-paladin-holy-deep-rgb"],
  "death-knight-blood": ["class-death-knight-deep-rgb", "spec-death-knight-blood-deep-rgb"],
  "priest-holy": ["class-priest-deep-rgb", "spec-priest-holy-deep-rgb"],
  "priest-shadow": ["class-priest-deep-rgb", "spec-priest-shadow-deep-rgb"],
  "hunter-marksmanship": ["class-hunter-deep-rgb", "spec-hunter-marksmanship-deep-rgb"],
  "warlock-affliction": ["class-warlock-deep-rgb", "spec-warlock-affliction-deep-rgb"],
  "warlock-demonology": ["class-warlock-deep-rgb", "spec-warlock-demonology-deep-rgb"],
  "warlock-destruction": ["class-warlock-deep-rgb", "spec-warlock-destruction-deep-rgb"]
})) {
  assert.match(
    hubInlineCss,
    new RegExp(`\\.class-guide-card\\.${cardClass}\\{[^}]*--guide-banner-class-deep-rgb:var\\(--${deepTokens[0]}\\)[^}]*--guide-banner-spec-deep-rgb:var\\(--${deepTokens[1]}\\)`),
    `index.html: ${cardClass} gradient must use its guide-banner class and spec colors`
  );
}

const colorReferenceDocument = new JSDOM(fs.readFileSync(path.join(root, "internal", "color-reference.html"), "utf8")).window.document;
assert.match(colorReferenceDocument.querySelector("#workflow")?.textContent || "", /Reuse the identity gradient/);
const identityExamplePages = {
  "color-reference.html": {
    key: "warlock-demonology",
    heading: "Class-to-spec gradient examples",
    intro: "Both examples use the same Demonology tokens, angle, stops, and neutral surface anchors. Only the approved component strength changes.",
    title: "Demo Lock Quick Start",
    bannerCopy: "Use the default strength for the large identity banner at the top of a guide.",
    cardCopy: "Use the half-strength card modifier when the gradient supports a compact surface."
  },
  "color-system.html": {
    key: "core",
    heading: "Core identity-gradient examples",
    intro: "Both examples use the same neutral foundation and Core reference tokens, angle, stops, and surface anchors. Only the approved component strength changes.",
    title: "Core Guide Color Standard",
    bannerCopy: "Use the default strength for a large shared-system banner.",
    cardCopy: "Use the card modifier when the shared system identity supports a compact surface."
  },
  "paladin-color-system.html": {
    key: "paladin-protection",
    heading: "Paladin class-to-spec gradient examples",
    intro: "Both examples use the same Paladin and Protection tokens, angle, stops, and neutral surface anchors. Only the approved component strength changes.",
    title: "Prot Pally Quick Start",
    bannerCopy: "Use the default strength for the large Protection guide banner.",
    cardCopy: "Use the card modifier when the Protection identity supports a compact Hub surface."
  },
  "death-knight-color-system.html": {
    key: "death-knight-blood",
    heading: "Death Knight class-to-spec gradient examples",
    intro: "Both examples use the same Death Knight and Blood tokens, angle, stops, and neutral surface anchors. Only the approved component strength changes.",
    title: "Blood DK Quick Start",
    bannerCopy: "Use the default strength for the large Blood guide banner.",
    cardCopy: "Use the card modifier when the Blood identity supports a compact Hub surface."
  },
  "druid-color-system.html": {
    key: "druid-restoration",
    heading: "Druid class-to-spec gradient examples",
    intro: "Both examples use the same Druid and Restoration tokens, angle, stops, and neutral surface anchors. Only the approved component strength changes.",
    title: "Restoration Druid Quick Start",
    bannerCopy: "Use the default strength for the large Restoration guide banner.",
    cardCopy: "Use the card modifier when the Restoration identity supports a compact Hub surface."
  },
  "priest-color-system.html": {
    key: "priest-holy",
    heading: "Priest class-to-spec gradient examples",
    intro: "Both examples use the same Priest and Holy tokens, angle, stops, and neutral surface anchors. Only the approved component strength changes.",
    title: "Holy Priest Quick Start",
    bannerCopy: "Use the default strength for the large Holy guide banner.",
    cardCopy: "Use the card modifier when the Holy identity supports a compact Hub surface."
  },
  "hunter-color-system.html": {
    key: "hunter-marksmanship",
    heading: "Hunter class-to-spec gradient examples",
    intro: "Both examples use the same Hunter and Marksmanship tokens, angle, stops, and neutral surface anchors. Only the approved component strength changes.",
    title: "MM Hunter Quick Start",
    bannerCopy: "Use the default strength for the large Marksmanship guide banner.",
    cardCopy: "Use the card modifier when the Marksmanship identity supports a compact Hub surface."
  },
  "warlock-color-system.html": {
    key: "warlock-demonology",
    heading: "Warlock class-to-spec gradient examples",
    intro: "Both examples use the same Warlock and Demonology tokens, angle, stops, and neutral surface anchors. Only the approved component strength changes.",
    title: "Demo Lock Quick Start",
    bannerCopy: "Use the default strength for the large Demonology guide banner.",
    cardCopy: "Use the card modifier when the Demonology identity supports a compact Hub surface."
  },
  "color-system-addons-ah.html": {
    key: "addons-auction-house",
    heading: "Section identity-gradient examples",
    intro: "Both examples use the same Addons and Auction House section tokens, angle, stops, and neutral surface anchors. Only the approved component strength changes.",
    title: "Addons + Auction House",
    bannerCopy: "Use the default strength for a large cross-section banner.",
    cardCopy: "Use the card modifier when the Addons + Auction House identity supports a compact surface."
  }
};
for (const [pageFile, expected] of Object.entries(identityExamplePages)) {
  const pageDocument = new JSDOM(fs.readFileSync(path.join(root, "internal", pageFile), "utf8")).window.document;
  const section = pageDocument.querySelector("#identity-examples");
  const examples = [...(section?.querySelectorAll(".guide-identity-gradient") || [])];
  const normalizeText = (element) => (element?.textContent || "").replace(/\s+/g, " ").trim();

  assert.ok(section, `internal/${pageFile}: explicit gradient examples are missing`);
  assert.equal(
    pageDocument.querySelectorAll('link[href="../assets/guide-color-system.css?v=20260814-druid-standard-v1"]').length,
    1,
    `internal/${pageFile}: contextual color tokens are missing`
  );
  assert.equal(
    pageDocument.querySelectorAll('link[href="../assets/internal-color-reference.css?v=20260814-druid-standard-v1"]').length,
    1,
    `internal/${pageFile}: shared specimen stylesheet is missing`
  );
  assert.equal(
    pageDocument.querySelectorAll('link[href="../assets/guide-hero.css?v=20260812-guide-identity-card-v3"]').length,
    1,
    `internal/${pageFile}: shared identity-gradient stylesheet is missing`
  );
  assert.equal(examples.length, 2, `internal/${pageFile}: both approved strengths must be shown`);
  assert.equal(section.querySelectorAll(".guide-identity-gradient--card").length, 1, `internal/${pageFile}: exactly one compact card example is required`);
  assert.equal(examples[0].classList.contains("guide-identity-gradient--card"), false, `internal/${pageFile}: banner example must use default strength`);
  assert.equal(examples[1].classList.contains("guide-identity-gradient--card"), true, `internal/${pageFile}: compact example must use the card modifier`);
  assert.equal(section.getAttribute("data-identity-example"), expected.key, `internal/${pageFile}: wrong contextual color mapping`);
  assert.equal(examples.filter((example) => example.hasAttribute("style")).length, 0, `internal/${pageFile}: specimen tokens must not be duplicated inline`);
  assert.equal(section.querySelector("h2")?.textContent.trim(), expected.heading);
  assert.equal(normalizeText(section.querySelector(":scope > p")), expected.intro);
  assert.equal(examples[0].querySelector(".identity-example-label")?.textContent.trim(), "Guide banner · 42% / 34%");
  assert.equal(examples[1].querySelector(".identity-example-label")?.textContent.trim(), "Compact Hub card · 14% / 11%");
  assert.equal(normalizeText(examples[0].querySelector("strong")), expected.title);
  assert.equal(normalizeText(examples[1].querySelector("strong")), expected.title);
  assert.equal(normalizeText(examples[0].querySelector("p")), expected.bannerCopy);
  assert.equal(normalizeText(examples[1].querySelector("p")), expected.cardCopy);
  assert.match(normalizeText(section.querySelector(".reference-note")), /Approved usage: banners use \.guide-identity-gradient\. Compact cards add \.guide-identity-gradient--card\. Never duplicate or locally alter the formula\./);
}

const internalColorReferenceCss = fs.readFileSync(path.join(root, "assets", "internal-color-reference.css"), "utf8");
for (const key of new Set(Object.values(identityExamplePages).map((page) => page.key))) {
  assert.match(
    internalColorReferenceCss,
    new RegExp(`#identity-examples\\[data-identity-example="${key}"\\]\\s*\\{[^}]*--guide-banner-class-deep-rgb:[^}]*--guide-banner-spec-deep-rgb:[^}]*--identity-example-class-soft:[^}]*--identity-example-spec-accent:[^}]*--identity-example-spec-rgb:`),
    `assets/internal-color-reference.css: ${key} specimen mapping is incomplete`
  );
}
assert.match(internalColorReferenceCss, /border:\s*1px solid rgba\(var\(--identity-example-spec-rgb\), \.26\)/);
assert.match(internalColorReferenceCss, /color:\s*var\(--identity-example-class-soft\)/);
assert.match(internalColorReferenceCss, /\.identity-gradient-example strong span \{ color:\s*var\(--identity-example-spec-accent\); \}/);

const operatingManuals = {
  "protection-paladin": { id: "quick-start", summaryCards: 4, sequences: 3 },
  "holy-paladin": { id: "quick-start", summaryCards: 4, sequences: 4 },
  "blood-death-knight": { id: "verdict", summaryCards: 4, sequences: 4 },
  "holy-priest": { id: "quick-start", summaryCards: 4, sequences: 4 },
  "shadow-priest": { id: "quick-start", summaryCards: 4, sequences: 4 },
  "marksmanship-hunter": { id: "quick-start", summaryCards: 5, sequences: 4, fourSummaries: true },
  "affliction-warlock": { id: "quick-start", summaryCards: 4, sequences: 4 },
  "demonology-warlock": { id: "quick-start", summaryCards: 4, sequences: 4 },
  "destruction-warlock": { id: "quick-start", summaryCards: 4, sequences: 4 }
};
for (const [prefix, expected] of Object.entries(operatingManuals)) {
  const relative = `guides/${prefix}-pve-guide.html`;
  const document = new JSDOM(fs.readFileSync(path.join(root, relative), "utf8")).window.document;
  const manual = document.querySelector(`#${expected.id}.operating-manual`);
  const heading = manual?.querySelector(":scope > h2.guide-category-heading");
  const headingCopy = heading?.cloneNode(true);
  headingCopy?.querySelector(".guide-back-to-top")?.remove();

  assert.ok(manual, `${relative}: shared Two-minute operating manual is missing`);
  assert.equal(document.querySelectorAll(".operating-manual").length, 1, `${relative}: expected one operating manual`);
  assert.equal(
    document.querySelectorAll('link[href*="/guide-operating-manual.css"]').length,
    1,
    `${relative}: shared operating-manual stylesheet is missing`
  );
  assert.equal(headingCopy?.textContent.trim(), "Two-minute operating manual", `${relative}: operating-manual title changed`);
  assert.ok(heading?.querySelector(".spell-icon"), `${relative}: operating-manual title icon is missing`);
  assert.equal(heading?.querySelector(".guide-back-to-top")?.getAttribute("href"), "#top", `${relative}: Top control is missing`);
  assert.equal(
    manual?.querySelectorAll(":scope > .summary-grid > .summary-card").length,
    expected.summaryCards,
    `${relative}: summary-card count changed`
  );
  assert.equal(Boolean(manual?.classList.contains("operating-manual--four-summaries")), Boolean(expected.fourSummaries), `${relative}: four-summary layout flag is incorrect`);
  assert.equal(manual?.querySelectorAll(".operating-engine").length, 1, `${relative}: operating engine is missing`);
  assert.equal(manual?.querySelectorAll(".operating-engine .engine-step").length, 4, `${relative}: four-step engine is missing`);
  assert.equal(manual?.querySelectorAll(".operating-engine .engine-step > strong .ability-icon").length, 4, `${relative}: engine title icons are missing`);
  assert.equal(manual?.querySelectorAll(".engine-spell-sequence").length, expected.sequences, `${relative}: icon-sequence count changed`);
  for (const sequence of manual?.querySelectorAll(".engine-spell-sequence") || []) {
    const links = [...sequence.querySelectorAll(".engine-spell-link")];
    assert.ok(links.length >= 1, `${relative}: an icon sequence is empty`);
    assert.equal(sequence.querySelectorAll(".engine-spell-separator").length, links.length - 1, `${relative}: icon-sequence dashes do not match its icons`);
    assert.ok(
      links.every((link) => link.classList.contains("wowhead-link") && link.hasAttribute("data-wowhead") && link.querySelector("img")),
      `${relative}: icon sequences must use Wowhead hover links`
    );
  }
  assert.ok(manual?.querySelector(".server-behavior"), `${relative}: collapsed server behavior is missing`);
  assert.ok(manual?.querySelector(".guide-box .checklist"), `${relative}: checkmark list is missing`);
  assert.ok(manual?.querySelector(".guide-box .priority-list"), `${relative}: numbered list is missing`);
  const expectedFooterDate = families[prefix].quickStartUpdated || "2026-08-12";
  assert.match(document.querySelector(".wrap > footer")?.textContent || "", new RegExp(`Updated ${expectedFooterDate}$`), `${relative}: footer date is stale`);
}

const tankadinPreviewDocument = new JSDOM(
  fs.readFileSync(path.join(root, "guides", "protection-paladin-pve-guide.html"), "utf8")
).window.document;
const tankadinPreviewSection = tankadinPreviewDocument.querySelector("#quick-start");
const tankadinPreviewHeading = tankadinPreviewSection?.querySelector(":scope > h2.guide-category-heading");
assert.equal(tankadinPreviewDocument.querySelector(".wrap")?.id, "top", "Tankadin preview: Top target is missing");
assert.equal(
  tankadinPreviewHeading?.childNodes[1]?.textContent.trim(),
  "Two-minute operating manual",
  "Tankadin preview: B-style section title is missing"
);
assert.match(
  tankadinPreviewHeading?.querySelector(".spell-icon")?.getAttribute("src") || "",
  /spell_holy_devotionaura\.jpg$/,
  "Tankadin preview: Protection section icon is missing"
);
assert.equal(
  tankadinPreviewHeading?.querySelector(".guide-back-to-top")?.getAttribute("href"),
  "#top",
  "Tankadin preview: B-style Top control is missing"
);
assert.equal(tankadinPreviewSection?.querySelectorAll(".summary-grid > .summary-card").length, 4, "Tankadin preview: B-style summary-card count changed");
assert.equal(tankadinPreviewSection?.querySelectorAll(".combat-engine .engine-step").length, 4, "Tankadin preview: B-style four-step engine is missing");
assert.equal(tankadinPreviewSection?.querySelectorAll(".combat-engine .engine-step .ability-icon").length, 4, "Tankadin preview: engine-step icons are missing");
assert.equal(
  tankadinPreviewSection?.querySelector(".combat-engine .summary-value")?.textContent.trim(),
  "Ready → 9-second → 6-second → repeat",
  "Tankadin preview: combat-engine sequence is incorrect"
);
assert.equal(
  tankadinPreviewSection?.querySelector(".mechanic-ready p")?.textContent.trim(),
  "Turn on Righteous Fury and Divine Plea; have Sacred Shield ready before contact.",
  "Tankadin preview: Ready card guidance is incorrect"
);
assert.deepEqual(
  [...tankadinPreviewSection.querySelectorAll(".mechanic-ready .engine-spell-link")].map((link) => link.getAttribute("aria-label")),
  ["Righteous Fury", "Divine Plea", "Sacred Shield"],
  "Tankadin preview: Ready icon sequence is incorrect"
);
assert.deepEqual(
  [...tankadinPreviewSection.querySelectorAll(".mechanic-ready .engine-spell-link")].map((link) => link.getAttribute("data-wowhead")),
  ["spell=25780&domain=wotlk", "spell=54428&domain=wotlk", "spell=53601&domain=wotlk"],
  "Tankadin preview: Ready icon hover links are incorrect"
);
assert.deepEqual(
  [...tankadinPreviewSection.querySelectorAll(".mechanic-nine .engine-spell-link")].map((link) => link.getAttribute("aria-label")),
  ["Holy Shield", "Judgement of Wisdom", "Consecration"],
  "Tankadin preview: 9-second icon sequence is incorrect"
);
const tankadinWisdomLink = tankadinPreviewSection.querySelector(".mechanic-nine .engine-spell-link[aria-label='Judgement of Wisdom']");
assert.equal(
  tankadinWisdomLink?.getAttribute("href"),
  "https://www.wowhead.com/wotlk/spell=53408",
  "Tankadin preview: Judgement of Wisdom does not use the correct hover link"
);
assert.equal(
  tankadinWisdomLink?.getAttribute("data-wowhead"),
  "spell=53408&domain=wotlk",
  "Tankadin preview: Judgement of Wisdom hover data is incorrect"
);
assert.equal(
  tankadinWisdomLink?.getAttribute("title"),
  "Judgement of Wisdom",
  "Tankadin preview: Judgement of Wisdom native hover label is missing"
);
const tankadinAssignedJudgementLink = tankadinPreviewSection.querySelector(".mechanic-nine p .wowhead-link");
assert.equal(
  tankadinAssignedJudgementLink?.textContent.trim(),
  "assigned Judgement",
  "Tankadin preview: assigned Judgement mouseover text changed"
);
assert.equal(
  tankadinAssignedJudgementLink?.getAttribute("href"),
  "https://www.wowhead.com/wotlk/spell=53408",
  "Tankadin preview: assigned Judgement does not use the Wisdom hover link"
);
assert.equal(
  tankadinAssignedJudgementLink?.getAttribute("data-wowhead"),
  "spell=53408&domain=wotlk",
  "Tankadin preview: assigned Judgement Wisdom hover data is incorrect"
);
assert.equal(
  tankadinAssignedJudgementLink?.getAttribute("title"),
  "Judgement of Wisdom",
  "Tankadin preview: assigned Judgement native hover label is missing"
);
assert.deepEqual(
  [...tankadinPreviewSection.querySelectorAll(".mechanic-six .engine-spell-link")].map((link) => link.getAttribute("aria-label")),
  ["Hammer of the Righteous", "Shield of Righteousness"],
  "Tankadin preview: 6-second icon sequence is incorrect"
);
assert.equal(tankadinPreviewSection.querySelectorAll(".mechanic-ready .engine-spell-separator").length, 2, "Tankadin preview: Ready dashes are missing");
assert.equal(tankadinPreviewSection.querySelectorAll(".mechanic-nine .engine-spell-separator").length, 2, "Tankadin preview: 9-second dashes are missing");
assert.equal(tankadinPreviewSection.querySelectorAll(".mechanic-six .engine-spell-separator").length, 1, "Tankadin preview: 6-second dash is missing");
assert.ok(
  [...tankadinPreviewSection.querySelectorAll(".engine-spell-link")].every((link) => link.classList.contains("wowhead-link") && link.hasAttribute("data-wowhead")),
  "Tankadin preview: spell icons must keep A-style Wowhead hover links"
);
assert.equal(tankadinPreviewSection?.querySelector(".rotation-card"), null, "Tankadin preview: old A-style rotation block remains");
assert.equal(
  tankadinPreviewSection?.querySelector(".summary-detail a[href='protection-paladin-setting-up.html#glyphs']")?.textContent.trim(),
  "Open the glyph guide.",
  "Tankadin preview: A-style guide link changed"
);
assert.equal(tankadinPreviewSection?.querySelectorAll(".guide-box .checklist > li").length, 6, "Tankadin preview: A-style checklist changed");
assert.equal(tankadinPreviewSection?.querySelectorAll(".guide-box .priority-list > li").length, 4, "Tankadin preview: A-style numbered list changed");

const tankadinPlayingDocument = new JSDOM(
  fs.readFileSync(path.join(root, "guides", "protection-paladin-playing.html"), "utf8")
).window.document;
const tankadinFlexNote = tankadinPlayingDocument.querySelector("#cooldowns .seal-judgement-flex-note");
assert.ok(tankadinFlexNote, "Tankadin Playing: seal and Judgement flexibility note is missing");
assert.equal(
  tankadinFlexNote?.textContent.trim(),
  "Seals and Judgements are flexible. Swap either one when the encounter, target pattern, raid assignment, or mana needs change. This guide uses Judgement of Wisdom whenever an example needs a named Judgement, but use the Judgement your raid actually needs.",
  "Tankadin Playing: seal and Judgement flexibility guidance changed"
);
assert.equal(
  tankadinPlayingDocument.querySelector(".wrap > footer")?.textContent.trim().endsWith("Updated 2026-08-12"),
  true,
  "Tankadin Playing: footer date was not updated with the page"
);

const css = fs.readFileSync(path.join(root, "assets/guide-hero.css"), "utf8");
assert.match(css, /--guide-type-color:\s*#ffffff;/, "shared guide-type color token is missing");
assert.match(css, /\.hero-guide-type\s*\{[\s\S]*color:\s*var\(--guide-type-color\)/, "guide type does not use the shared color token");
assert.match(
  css,
  /\.guide-identity-gradient,\s*body header\.guide-hero\s*\{[\s\S]*--guide-identity-class-opacity:\s*\.42;[\s\S]*--guide-identity-spec-opacity:\s*\.34;[\s\S]*--guide-identity-background:\s*linear-gradient\(\s*135deg,[\s\S]*rgba\(var\(--guide-banner-class-deep-rgb\), var\(--guide-identity-class-opacity\)\) 46%,[\s\S]*rgba\(var\(--guide-banner-spec-deep-rgb\), var\(--guide-identity-spec-opacity\)\) 78%,[\s\S]*var\(--surface-card\) 100%[\s\S]*background:\s*var\(--guide-identity-background\)/,
  "shared guide identity gradient is missing or changed"
);
assert.match(
  css,
  /\.guide-identity-gradient--card\s*\{\s*--guide-identity-class-opacity:\s*\.14;\s*--guide-identity-spec-opacity:\s*\.11;/,
  "shared guide identity gradient is missing the subtle card variant"
);
assert.match(
  css,
  /\.guide-identity-gradient:hover,\s*\.guide-identity-gradient:focus-visible\s*\{\s*background:\s*var\(--guide-identity-background\)/,
  "shared guide identity gradient must survive hover and keyboard focus"
);
assert.match(
  css,
  /body header\.guide-hero\s*\{[\s\S]*--guide-banner-class-deep-rgb:\s*var\(--class-accent-deep-rgb\);[\s\S]*--guide-banner-spec-deep-rgb:\s*var\(--theme-accent-deep-rgb\);/,
  "guide banners do not bind the reusable gradient tokens"
);
const operatingCss = fs.readFileSync(path.join(root, "assets/guide-operating-manual.css"), "utf8");
for (const marker of [".operating-manual .operating-engine", ".engine-spell-sequence", ".checklist li::before", ".priority-list li::before", "@media (max-width: 680px)"]) {
  assert.ok(operatingCss.includes(marker), `shared operating-manual stylesheet is missing ${marker}`);
}

const scaffold = fs.readFileSync(path.join(root, "tools/create-spec-guide-scaffold.mjs"), "utf8");
for (const marker of [
  "guideNickname",
  "guideTypes",
  "guideNavLabels",
  "pageTitles",
  "../assets/guide-hero.css",
  "../assets/guide-operating-manual.css",
  'class="guide-hero"',
  'class="guide-hero-title"',
  "guide-jump-nav",
  "Two-minute operating manual",
  "operating-manual",
  "operating-engine",
  "engine-spell-sequence",
  "--operating-step-rgb"
]) {
  assert.ok(scaffold.includes(marker), `future-guide scaffold is missing ${marker}`);
}

const renderer = fs.readFileSync(path.join(root, "tools/render-fresh-80-spec-guides.mjs"), "utf8");
for (const marker of ["../assets/guide-hero.css", "../assets/guide-operating-manual.css", 'class="guide-hero"', "guideTypes[current]", "guide-jump-nav", "operating-manual", "operating-engine", "engine-spell-sequence", "--quick-start-only"]) {
  assert.ok(renderer.includes(marker), `fresh-80 renderer is missing ${marker}`);
}

const example = JSON.parse(
  fs.readFileSync(path.join(root, "templates/spec-guide/spec-guide.config.example.json"), "utf8")
);
assert.ok(example.guideNickname, "example config must require a banner nickname");
assert.deepEqual(
  Object.keys(example.guideTypes),
  ["quickStart", "playing", "setup", "building", "equipping", "raiding"],
  "example config must define all six guide types"
);

const scaffoldDryRun = spawnSync(
  process.execPath,
  [
    path.join(root, "tools/create-spec-guide-scaffold.mjs"),
    path.join(root, "templates/spec-guide/spec-guide.config.example.json"),
    "--dry-run",
    "--force"
  ],
  { cwd: root, encoding: "utf8" }
);
assert.equal(
  scaffoldDryRun.status,
  0,
  `future-guide scaffold dry run failed:\n${scaffoldDryRun.stderr || scaffoldDryRun.stdout}`
);
assert.match(scaffoldDryRun.stdout, /\[dry-run\] guides\/blood-death-knight-pve-guide\.html/);

console.log(`Guide banner system: ${checked} pages and both future-guide generators passed.`);
