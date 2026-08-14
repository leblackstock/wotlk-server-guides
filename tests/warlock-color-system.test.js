const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const { JSDOM } = require("jsdom");

const root = path.resolve(__dirname, "..");
const colorCss = fs.readFileSync(path.join(root, "assets", "guide-color-system.css"), "utf8");
const referenceCss = fs.readFileSync(path.join(root, "assets", "warlock-color-reference.css"), "utf8");
const sharedReferenceCss = fs.readFileSync(path.join(root, "assets", "internal-color-reference.css"), "utf8");
const deathKnightCss = fs.readFileSync(path.join(root, "assets", "death-knight-color-system.css"), "utf8");
const referenceHtml = fs.readFileSync(path.join(root, "internal", "warlock-color-system.html"), "utf8");
const referenceDocument = new JSDOM(referenceHtml).window.document;
const hunterReferenceHtml = fs.readFileSync(path.join(root, "internal", "hunter-color-system.html"), "utf8");
const hunterReferenceDocument = new JSDOM(hunterReferenceHtml).window.document;
const colorHubHtml = fs.readFileSync(path.join(root, "internal", "color-reference.html"), "utf8");
const colorHubDocument = new JSDOM(colorHubHtml).window.document;
const hunterSpecimenHtml = fs.readFileSync(path.join(root, "internal", "marksmanship-hunter-visual-system.html"), "utf8");
const hunterConfig = JSON.parse(fs.readFileSync(path.join(root, "templates", "spec-guide", "marksmanship-hunter.config.json"), "utf8"));
const cardSurface = "#121820";
const warlockGuideCacheKey = "20260814-warlock-standard-v2";
const guideIdentityCacheKey = "20260812-guide-identity-card-v3";

function cssValue(token) {
  const match = colorCss.match(new RegExp(`--${token}:\\s*([^;]+);`));
  assert.ok(match, `missing --${token}`);
  return match[1].trim().toLowerCase();
}

function linearChannel(value) {
  const channel = value / 255;
  return channel <= 0.04045 ? channel / 12.92 : ((channel + 0.055) / 1.055) ** 2.4;
}

function relativeLuminance(hex) {
  const channels = [1, 3, 5].map((index) => linearChannel(Number.parseInt(hex.slice(index, index + 2), 16)));
  return channels[0] * 0.2126 + channels[1] * 0.7152 + channels[2] * 0.0722;
}

function contrastRatio(first, second) {
  const values = [relativeLuminance(first), relativeLuminance(second)].sort((a, b) => b - a);
  return (values[0] + 0.05) / (values[1] + 0.05);
}

function oklabFromLinear([red, green, blue]) {
  const long = 0.4122214708 * red + 0.5363325363 * green + 0.0514459929 * blue;
  const medium = 0.2119034982 * red + 0.6806995451 * green + 0.1073969566 * blue;
  const short = 0.0883024619 * red + 0.2817188376 * green + 0.6299787005 * blue;
  const [longRoot, mediumRoot, shortRoot] = [long, medium, short].map(Math.cbrt);
  return [
    0.2104542553 * longRoot + 0.793617785 * mediumRoot - 0.0040720468 * shortRoot,
    1.9779984951 * longRoot - 2.428592205 * mediumRoot + 0.4505937099 * shortRoot,
    0.0259040371 * longRoot + 0.7827717662 * mediumRoot - 0.808675766 * shortRoot
  ];
}

function oklab(hex) {
  return oklabFromLinear(
    [1, 3, 5].map((index) => linearChannel(Number.parseInt(hex.slice(index, index + 2), 16)))
  );
}

function perceptualDistance(first, second) {
  const firstLab = oklab(first);
  const secondLab = oklab(second);
  return Math.hypot(...firstLab.map((value, index) => value - secondLab[index]));
}

function simulatedDistance(first, second, matrix) {
  function simulate(hex) {
    const channels = [1, 3, 5].map((index) => linearChannel(Number.parseInt(hex.slice(index, index + 2), 16)));
    return oklabFromLinear(
      matrix.map((row) => Math.max(0, Math.min(1, row.reduce((total, value, index) => total + value * channels[index], 0))))
    );
  }
  const firstLab = simulate(first);
  const secondLab = simulate(second);
  return Math.hypot(...firstLab.map((value, index) => value - secondLab[index]));
}

function assertPairwiseDistance(tokens, minimum, label) {
  for (let first = 0; first < tokens.length; first += 1) {
    for (let second = first + 1; second < tokens.length; second += 1) {
      const firstColor = cssValue(tokens[first]);
      const secondColor = cssValue(tokens[second]);
      assert.ok(
        perceptualDistance(firstColor, secondColor) >= minimum,
        `${label}: --${tokens[first]} and --${tokens[second]} are too similar`
      );
    }
  }
}

const warlockClass = {
  accent: "#8788ee",
  soft: "#c8c9ff",
  deep: "#30316b",
  rgb: "135, 136, 238"
};
const configs = [
  {
    specKey: "affliction",
    specShortName: "Affliction",
    specAccent: "#b46cff",
    specAccentSoft: "#e4c7ff",
    specAccentDeep: "#4b216e",
    specAccentRgb: "180, 108, 255",
    mechanics: [
      { key: "dots", color: "#b46cff", soft: "#e4c7ff", rgb: "180, 108, 255" },
      { key: "haunt", color: "#6fc7d8", soft: "#c6f0f6", rgb: "111, 199, 216" },
      { key: "execute", color: "#e07a9a", soft: "#f8cad8", rgb: "224, 122, 154" },
      { key: "resources", color: "#70c99a", soft: "#c9f0db", rgb: "112, 201, 154" }
    ]
  },
  {
    specKey: "demonology",
    specShortName: "Demonology",
    specAccent: "#aad372",
    specAccentSoft: "#ddf2be",
    specAccentDeep: "#405a28",
    specAccentRgb: "170, 211, 114",
    mechanics: [
      { key: "felguard", color: "#aad372", soft: "#ddf2be", rgb: "170, 211, 114" },
      { key: "procs", color: "#e5905a", soft: "#f8d4bd", rgb: "229, 144, 90" },
      { key: "metamorphosis", color: "#b37aee", soft: "#e5cef9", rgb: "179, 122, 238" },
      { key: "pact", color: "#7db5e8", soft: "#cce5fa", rgb: "125, 181, 232" }
    ]
  },
  {
    specKey: "destruction",
    specShortName: "Destruction",
    specAccent: "#f07b3f",
    specAccentSoft: "#ffd1b8",
    specAccentDeep: "#6d2d13",
    specAccentRgb: "240, 123, 63",
    mechanics: [
      { key: "immolate", color: "#f07b3f", soft: "#ffd1b8", rgb: "240, 123, 63" },
      { key: "bolts", color: "#77c9a5", soft: "#c9f0df", rgb: "119, 201, 165" },
      { key: "backdraft", color: "#e4b04e", soft: "#f8e3b5", rgb: "228, 176, 78" },
      { key: "imp", color: "#a88bf0", soft: "#ddd2fa", rgb: "168, 139, 240" }
    ]
  }
];

for (const config of configs) {
  const prefix = `spec-warlock-${config.specKey}`;
  assert.equal(cssValue("class-warlock-accent"), warlockClass.accent);
  assert.equal(cssValue("class-warlock-soft"), warlockClass.soft);
  assert.equal(cssValue("class-warlock-deep"), warlockClass.deep);
  assert.equal(cssValue("class-warlock-rgb"), warlockClass.rgb);
  assert.equal(cssValue(`${prefix}-accent`), config.specAccent);
  assert.equal(cssValue(`${prefix}-soft`), config.specAccentSoft);
  assert.equal(cssValue(`${prefix}-deep`), config.specAccentDeep);
  assert.equal(cssValue(`${prefix}-rgb`), config.specAccentRgb);

  for (const mechanic of config.mechanics) {
    const mechanicPrefix = `mechanic-${config.specKey}-${mechanic.key}`;
    assert.equal(cssValue(mechanicPrefix), mechanic.color);
    assert.equal(cssValue(`${mechanicPrefix}-soft`), mechanic.soft);
    assert.equal(cssValue(`${mechanicPrefix}-rgb`), mechanic.rgb);
  }

  const guideConfig = JSON.parse(
    fs.readFileSync(path.join(root, "templates", "spec-guide", `${config.specKey}-warlock.config.json`), "utf8")
  );
  const specimenHtml = fs.readFileSync(
    path.join(root, "internal", `${config.specKey}-warlock-visual-system.html`),
    "utf8"
  ).toLowerCase();
  const normalizeRgb = (value) => value.replaceAll(" ", "");
  assert.equal(guideConfig.classAccent.toLowerCase(), warlockClass.accent);
  assert.equal(guideConfig.cacheKey, warlockGuideCacheKey);
  assert.equal(guideConfig.updatedDate, "2026-08-14");
  assert.equal(guideConfig.classAccentSoft.toLowerCase(), warlockClass.soft);
  assert.equal(guideConfig.classAccentDeep.toLowerCase(), warlockClass.deep);
  assert.equal(normalizeRgb(guideConfig.classAccentRgb), normalizeRgb(warlockClass.rgb));
  assert.equal(guideConfig.specAccent.toLowerCase(), config.specAccent);
  assert.equal(guideConfig.specAccentSoft.toLowerCase(), config.specAccentSoft);
  assert.equal(guideConfig.specAccentDeep.toLowerCase(), config.specAccentDeep);
  assert.equal(normalizeRgb(guideConfig.specAccentRgb), normalizeRgb(config.specAccentRgb));
  for (const mechanic of config.mechanics) {
    const configuredMechanic = guideConfig.mechanics.find((entry) => entry.key === mechanic.key);
    assert.ok(configuredMechanic, `${config.specShortName} config is missing ${mechanic.key}`);
    assert.equal(configuredMechanic.color.toLowerCase(), mechanic.color);
    assert.equal(configuredMechanic.soft.toLowerCase(), mechanic.soft);
    assert.equal(normalizeRgb(configuredMechanic.rgb), normalizeRgb(mechanic.rgb));
  }
  for (const color of [warlockClass.accent, config.specAccent, ...config.mechanics.map((mechanic) => mechanic.color)]) {
    assert.ok(specimenHtml.includes(color), `${config.specShortName} specimen must display ${color}`);
  }

  for (const pageSuffix of ["pve-guide", "playing", "setting-up", "gearing", "gear-targets", "raiding"]) {
    const pageFile = `${config.specKey}-warlock-${pageSuffix}.html`;
    const pageDocument = new JSDOM(fs.readFileSync(path.join(root, "guides", pageFile), "utf8")).window.document;
    assert.equal(
      pageDocument.querySelectorAll(`link[href="../assets/guide-color-system.css?v=${warlockGuideCacheKey}"]`).length,
      1,
      `${pageFile} must request the cache-safe approved Warlock color standard`
    );
    assert.equal(
      pageDocument.querySelectorAll(`link[href="../assets/guide-hero.css?v=${guideIdentityCacheKey}"]`).length,
      1,
      `${pageFile} must request the approved identity-gradient component`
    );
  }
}

const guideHubDocument = new JSDOM(fs.readFileSync(path.join(root, "index.html"), "utf8")).window.document;
assert.equal(
  guideHubDocument.querySelectorAll(`link[href="./assets/guide-color-system.css?v=${warlockGuideCacheKey}"]`).length,
  1,
  "Guide Hub must request the cache-safe approved Warlock color standard"
);

const accentTokens = [
  "class-warlock-accent",
  ...configs.flatMap((config) => [
    `spec-warlock-${config.specKey}-accent`,
    ...config.mechanics.map((mechanic) => `mechanic-${config.specKey}-${mechanic.key}`)
  ])
];
for (const token of accentTokens) {
  assert.ok(
    contrastRatio(cssValue(token), cardSurface) >= 5.5,
    `--${token} must retain at least 5.5:1 contrast against ${cardSurface}`
  );
}

const hunterClass = {
  accent: "#67a85f",
  soft: "#cbe7c6",
  deep: "#26472b",
  rgb: "103, 168, 95",
  deepRgb: "38, 71, 43"
};
const hunterSpecs = [
  { key: "beast-mastery", accent: "#d0bda5", soft: "#f1e7db", deep: "#594b3f", rgb: "208, 189, 165", deepRgb: "89, 75, 63" },
  { key: "marksmanship", accent: "#78a9d4", soft: "#c9e4f8", deep: "#2e5270", rgb: "120, 169, 212", deepRgb: "46, 82, 112" },
  { key: "survival", accent: "#df7d4f", soft: "#ffc6a9", deep: "#71371f", rgb: "223, 125, 79", deepRgb: "113, 55, 31" }
];
const hunterMechanics = [
  { key: "sting", accent: "#cd87ad", soft: "#f3c8de", rgb: "205, 135, 173" },
  { key: "shots", accent: "#78a9d4", soft: "#c9e4f8", rgb: "120, 169, 212" },
  { key: "movement", accent: "#adb5bd", soft: "#e1e7ec", rgb: "173, 181, 189" },
  { key: "pet", accent: "#78cfa8", soft: "#c8f1de", rgb: "120, 207, 168" }
];
assert.equal(cssValue("class-hunter-accent"), hunterClass.accent);
assert.equal(cssValue("class-hunter-soft"), hunterClass.soft);
assert.equal(cssValue("class-hunter-deep"), hunterClass.deep);
assert.equal(cssValue("class-hunter-rgb"), hunterClass.rgb);
assert.equal(cssValue("class-hunter-deep-rgb"), hunterClass.deepRgb);
assert.ok(
  contrastRatio(hunterClass.accent, cardSurface) >= 5.5,
  `--class-hunter-accent must retain at least 5.5:1 contrast against ${cardSurface}`
);
for (const spec of hunterSpecs) {
  assert.equal(cssValue(`spec-hunter-${spec.key}-accent`), spec.accent);
  assert.equal(cssValue(`spec-hunter-${spec.key}-soft`), spec.soft);
  assert.equal(cssValue(`spec-hunter-${spec.key}-deep`), spec.deep);
  assert.equal(cssValue(`spec-hunter-${spec.key}-rgb`), spec.rgb);
  assert.equal(cssValue(`spec-hunter-${spec.key}-deep-rgb`), spec.deepRgb);
  assert.ok(contrastRatio(spec.accent, cardSurface) >= 6, `Hunter ${spec.key} must retain at least 6:1 contrast`);
}
for (const mechanic of hunterMechanics) {
  assert.equal(cssValue(`mechanic-marksmanship-${mechanic.key}`), mechanic.accent);
  assert.equal(cssValue(`mechanic-marksmanship-${mechanic.key}-soft`), mechanic.soft);
  assert.equal(cssValue(`mechanic-marksmanship-${mechanic.key}-rgb`), mechanic.rgb);
  assert.ok(contrastRatio(mechanic.accent, cardSurface) >= 6, `Hunter ${mechanic.key} must retain at least 6:1 contrast`);
}
assertPairwiseDistance(hunterSpecs.map((spec) => `spec-hunter-${spec.key}-accent`), 0.14, "Hunter specialization identities");
assertPairwiseDistance(hunterMechanics.map((mechanic) => `mechanic-marksmanship-${mechanic.key}`), 0.08, "Marksmanship mechanic lanes");
assert.ok(perceptualDistance(hunterClass.accent, cssValue("spec-warlock-demonology-accent")) >= 0.12, "Hunter forest must remain distinct from fel green");
assert.ok(perceptualDistance(cssValue("mechanic-marksmanship-sting"), cssValue("spec-warlock-demonology-accent")) >= 0.12, "Sting must remain distinct from fel green");
assert.ok(perceptualDistance(cssValue("mechanic-marksmanship-movement"), cssValue("status-info")) >= 0.085, "Movement must remain distinct from global information cyan");

const redGreenMatrices = [
  [[0.152286, 1.052583, -0.204868], [0.114503, 0.786281, 0.099216], [-0.003882, -0.048116, 1.051998]],
  [[0.367322, 0.860646, -0.227968], [0.280085, 0.672501, 0.047413], [-0.01182, 0.04294, 0.968881]]
];
for (const matrix of redGreenMatrices) {
  assert.ok(
    simulatedDistance(cssValue("spec-hunter-beast-mastery-accent"), cssValue("spec-hunter-survival-accent"), matrix) >= 0.1,
    "Beast Mastery and Survival must remain distinct under red-green color-vision simulation"
  );
}

assert.equal(hunterConfig.classAccent.toLowerCase(), hunterClass.accent);
assert.equal(hunterConfig.mechanics.find((mechanic) => mechanic.key === "sting").color.toLowerCase(), hunterMechanics[0].accent);
assert.equal(hunterConfig.mechanics.find((mechanic) => mechanic.key === "movement").color.toLowerCase(), hunterMechanics[2].accent);
for (const color of [hunterClass.accent, hunterSpecs[1].accent, ...hunterMechanics.map((mechanic) => mechanic.accent)]) {
  assert.ok(hunterSpecimenHtml.toLowerCase().includes(color), `Marksmanship specimen must display ${color}`);
}
assert.match(hunterReferenceDocument.querySelector("#audit").textContent, /color-vision differences/);
assert.match(hunterReferenceDocument.body.textContent, /Approved for implementation/i);
assert.match(referenceDocument.body.textContent, /Approved for implementation/i);
for (const system of ["hunter", "warlock"]) {
  assert.match(
    colorHubDocument.querySelector(`.directory-card.${system} .card-status`)?.textContent ?? "",
    /Implementation approved/i,
    `${system} color hub card must show implementation approval`
  );
}

assertPairwiseDistance(
  configs.map((config) => `spec-warlock-${config.specKey}-accent`),
  0.2,
  "Warlock specialization identities"
);
for (const config of configs) {
  assertPairwiseDistance(
    config.mechanics.map((mechanic) => `mechanic-${config.specKey}-${mechanic.key}`),
    0.085,
    `${config.specShortName} mechanic lanes`
  );
}

for (const id of ["class", "audit", "specs", "affliction", "demonology", "destruction", "boundaries", "matrix"]) {
  assert.ok(referenceDocument.getElementById(id), `Warlock standard is missing #${id}`);
}
assert.equal(referenceDocument.querySelectorAll(".spec-grid .spec-card").length, 3);
for (const spec of ["affliction", "demonology", "destruction"]) {
  assert.equal(referenceDocument.querySelectorAll(`#${spec} .mechanic-card`).length, 4, `${spec} needs four named mechanic lanes`);
  assert.match(referenceCss, new RegExp(`\\.spec-card\\.${spec}\\s*\\{`));
}

const boundaryText = referenceDocument.querySelector("#boundaries").textContent;
for (const protectedMeaning of ["epic rarity", "success", "Auction House teal", "warning", "legendary rarity"]) {
  assert.ok(boundaryText.includes(protectedMeaning), `missing semantic boundary for ${protectedMeaning}`);
}

const canonicalReferences = [
  "color-reference.html",
  "color-system.html",
  "paladin-color-system.html",
  "death-knight-color-system.html",
  "druid-color-system.html",
  "priest-color-system.html",
  "hunter-color-system.html",
  "warlock-color-system.html",
  "color-system-addons-ah.html"
];
for (const file of canonicalReferences) {
  const document = new JSDOM(fs.readFileSync(path.join(root, "internal", file), "utf8")).window.document;
  assert.equal(
    document.querySelectorAll('.reference-site-nav a[href="warlock-color-system.html"]').length,
    1,
    `${file} must link the Warlock standard once in its reference navigation`
  );
}

for (const file of canonicalReferences) {
  const document = new JSDOM(fs.readFileSync(path.join(root, "internal", file), "utf8")).window.document;
  assert.equal(
    document.querySelector('link[href="../assets/guide-color-system.css?v=20260814-druid-standard-v1"]')?.getAttribute("rel"),
    "stylesheet",
    `${file} must request the cache-safe contextual specimen release`
  );
}

assert.equal(cssValue("navigation-global-deep-rgb"), "57, 69, 84");
assert.equal(cssValue("section-addons-deep-rgb"), "45, 60, 107");
assert.equal(cssValue("section-ah-deep-rgb"), "34, 89, 78");

const deathKnightSoft = deathKnightCss.match(/--class-death-knight-soft:\s*([^;]+);/);
assert.ok(deathKnightSoft, "missing --class-death-knight-soft");
assert.match(
  sharedReferenceCss,
  /body\.color-reference-page\[data-guide-class="death-knight"\] \.reference-kicker\s*\{[^}]*color:\s*var\(--reference-soft\);/s,
  "Death Knight reference kicker must use the accessible soft class color"
);
for (const background of ["#171d24", "#0b0f14"]) {
  assert.ok(
    contrastRatio(deathKnightSoft[1].trim().toLowerCase(), background) >= 4.5,
    `Death Knight reference kicker must retain 4.5:1 contrast against ${background}`
  );
}

console.log("Validated the Warlock and Hunter color systems, contrast, and semantic boundaries.");
