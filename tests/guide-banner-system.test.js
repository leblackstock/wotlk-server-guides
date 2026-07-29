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
    raidType: "Raid DPS Guide"
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
}

const css = fs.readFileSync(path.join(root, "assets/guide-hero.css"), "utf8");
assert.match(css, /--guide-type-color:\s*#ffffff;/, "shared guide-type color token is missing");
assert.match(css, /\.hero-guide-type\s*\{[\s\S]*color:\s*var\(--guide-type-color\)/, "guide type does not use the shared color token");

const scaffold = fs.readFileSync(path.join(root, "tools/create-spec-guide-scaffold.mjs"), "utf8");
for (const marker of [
  "guideNickname",
  "guideTypes",
  "guideNavLabels",
  "pageTitles",
  "../assets/guide-hero.css",
  'class="guide-hero"',
  'class="guide-hero-title"',
  "guide-jump-nav"
]) {
  assert.ok(scaffold.includes(marker), `future-guide scaffold is missing ${marker}`);
}

const renderer = fs.readFileSync(path.join(root, "tools/render-fresh-80-spec-guides.mjs"), "utf8");
for (const marker of ["../assets/guide-hero.css", 'class="guide-hero"', "guideTypes[current]", "guide-jump-nav"]) {
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
