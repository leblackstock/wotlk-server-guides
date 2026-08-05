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
for (const [prefix, family] of Object.entries(families)) {
  const card = hubDocument.querySelector(`.class-guide-card[href="./guides/${prefix}-pve-guide.html"]`);
  const landingDocument = new JSDOM(
    fs.readFileSync(path.join(root, "guides", `${prefix}-pve-guide.html`), "utf8")
  ).window.document;
  assert.ok(card, `index.html: ${prefix} class-guide card is missing`);
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
  "hunter-marksmanship": "class-hunter-accent"
})) {
  assert.match(
    hubInlineCss,
    new RegExp(`\\.class-guide-card\\.${cardClass}\\{[^}]*--class-guide-class-accent:var\\(--${classToken}\\)`),
    `index.html: ${cardClass} side bar does not use its class color`
  );
}

const operatingManuals = {
  "protection-paladin": { id: "quick-start", summaryCards: 4, sequences: 3 },
  "holy-paladin": { id: "quick-start", summaryCards: 4, sequences: 4 },
  "blood-death-knight": { id: "verdict", summaryCards: 4, sequences: 4 },
  "holy-priest": { id: "quick-start", summaryCards: 4, sequences: 4 },
  "shadow-priest": { id: "quick-start", summaryCards: 4, sequences: 4 },
  "marksmanship-hunter": { id: "quick-start", summaryCards: 5, sequences: 4, fourSummaries: true }
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
  const expectedFooterDate = families[prefix].quickStartUpdated || "2026-07-31";
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
  tankadinPlayingDocument.querySelector(".wrap > footer")?.textContent.trim().endsWith("Updated 2026-07-30"),
  true,
  "Tankadin Playing: footer date was not updated with the page"
);

const css = fs.readFileSync(path.join(root, "assets/guide-hero.css"), "utf8");
assert.match(css, /--guide-type-color:\s*#ffffff;/, "shared guide-type color token is missing");
assert.match(css, /\.hero-guide-type\s*\{[\s\S]*color:\s*var\(--guide-type-color\)/, "guide type does not use the shared color token");
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
