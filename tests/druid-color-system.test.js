const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const { JSDOM } = require("jsdom");

const root = path.resolve(__dirname, "..");
const colorCss = fs.readFileSync(path.join(root, "assets", "guide-color-system.css"), "utf8");
const referenceCss = fs.readFileSync(path.join(root, "assets", "druid-color-reference.css"), "utf8");
const sharedReferenceCss = fs.readFileSync(path.join(root, "assets", "internal-color-reference.css"), "utf8");
const referenceHtml = fs.readFileSync(path.join(root, "internal", "druid-color-system.html"), "utf8");
const referenceDocument = new JSDOM(referenceHtml).window.document;
const colorHubDocument = new JSDOM(
  fs.readFileSync(path.join(root, "internal", "color-reference.html"), "utf8")
).window.document;
const cardSurface = "#121820";
const sharedCacheKey = "20260814-druid-standard-v1";
const druidReferenceCacheKey = "20260814-druid-color-v1";

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
      assert.ok(
        perceptualDistance(cssValue(tokens[first]), cssValue(tokens[second])) >= minimum,
        `${label}: --${tokens[first]} and --${tokens[second]} are too similar`
      );
    }
  }
}

const druidClass = {
  accent: "#e58b43",
  soft: "#ffd5b0",
  deep: "#713c1d",
  rgb: "229, 139, 67",
  deepRgb: "113, 60, 29"
};
const specs = [
  {
    key: "balance",
    accent: "#8c9fe8",
    soft: "#d5dcff",
    deep: "#3b456f",
    rgb: "140, 159, 232",
    deepRgb: "59, 69, 111",
    mechanics: [
      { key: "lunar", accent: "#79b6e8", soft: "#cce8fb", rgb: "121, 182, 232" },
      { key: "solar", accent: "#e4b75b", soft: "#f9e4af", rgb: "228, 183, 91" },
      { key: "dots", accent: "#c783b4", soft: "#f0cce5", rgb: "199, 131, 180" },
      { key: "mana-movement", accent: "#78c6aa", soft: "#c9efe2", rgb: "120, 198, 170" }
    ]
  },
  {
    key: "feral",
    accent: "#d6c2a6",
    soft: "#f5eadc",
    deep: "#64513e",
    rgb: "214, 194, 166",
    deepRgb: "100, 81, 62",
    mechanics: [
      { key: "forms", accent: "#d6c2a6", soft: "#f5eadc", rgb: "214, 194, 166" },
      { key: "resources", accent: "#dfad42", soft: "#f6dfa6", rgb: "223, 173, 66" },
      { key: "bleeds", accent: "#d07b91", soft: "#f3c6d2", rgb: "208, 123, 145" },
      { key: "survival", accent: "#78b8d2", soft: "#c9e8f2", rgb: "120, 184, 210" }
    ]
  },
  {
    key: "restoration",
    accent: "#54a67a",
    soft: "#bfe8d1",
    deep: "#23513a",
    rgb: "84, 166, 122",
    deepRgb: "35, 81, 58",
    mechanics: [
      { key: "hots", accent: "#54a67a", soft: "#bfe8d1", rgb: "84, 166, 122" },
      { key: "lifebloom", accent: "#d0bd5e", soft: "#f2e8ad", rgb: "208, 189, 94" },
      { key: "raid-healing", accent: "#75b9dc", soft: "#c8e8f8", rgb: "117, 185, 220" },
      { key: "mana-procs", accent: "#aa8fe0", soft: "#ddd2f7", rgb: "170, 143, 224" }
    ]
  }
];

for (const [suffix, value] of Object.entries(druidClass)) {
  const tokenSuffix = suffix === "accent" ? "accent" : suffix.replace(/[A-Z]/g, (letter) => `-${letter.toLowerCase()}`);
  assert.equal(cssValue(`class-druid-${tokenSuffix}`), value);
}
assert.ok(contrastRatio(druidClass.accent, cardSurface) >= 5.5, "Druid class accent must retain 5.5:1 contrast");

for (const spec of specs) {
  const prefix = `spec-druid-${spec.key}`;
  assert.equal(cssValue(`${prefix}-accent`), spec.accent);
  assert.equal(cssValue(`${prefix}-soft`), spec.soft);
  assert.equal(cssValue(`${prefix}-deep`), spec.deep);
  assert.equal(cssValue(`${prefix}-rgb`), spec.rgb);
  assert.equal(cssValue(`${prefix}-deep-rgb`), spec.deepRgb);
  assert.ok(contrastRatio(spec.accent, cardSurface) >= 5.5, `${spec.key} accent must retain 5.5:1 contrast`);

  for (const mechanic of spec.mechanics) {
    const mechanicPrefix = `mechanic-${spec.key}-${mechanic.key}`;
    assert.equal(cssValue(mechanicPrefix), mechanic.accent);
    assert.equal(cssValue(`${mechanicPrefix}-soft`), mechanic.soft);
    assert.equal(cssValue(`${mechanicPrefix}-rgb`), mechanic.rgb);
    assert.ok(contrastRatio(mechanic.accent, cardSurface) >= 5.5, `${mechanicPrefix} must retain 5.5:1 contrast`);
  }

  assertPairwiseDistance(
    spec.mechanics.map((mechanic) => `mechanic-${spec.key}-${mechanic.key}`),
    0.1,
    `${spec.key} mechanic lanes`
  );
}

assertPairwiseDistance(
  ["class-druid-accent", ...specs.map((spec) => `spec-druid-${spec.key}-accent`)],
  0.14,
  "Druid class and specialization identities"
);

const redGreenMatrices = [
  [[0.152286, 1.052583, -0.204868], [0.114503, 0.786281, 0.099216], [-0.003882, -0.048116, 1.051998]],
  [[0.367322, 0.860646, -0.227968], [0.280085, 0.672501, 0.047413], [-0.01182, 0.04294, 0.968881]]
];
for (const matrix of redGreenMatrices) {
  for (let first = 0; first < specs.length; first += 1) {
    for (let second = first + 1; second < specs.length; second += 1) {
      assert.ok(
        simulatedDistance(specs[first].accent, specs[second].accent, matrix) >= 0.12,
        `${specs[first].key} and ${specs[second].key} must remain distinct under red-green simulation`
      );
    }
  }
}

assert.ok(perceptualDistance(druidClass.accent, cssValue("quality-legendary")) >= 0.04);
assert.ok(perceptualDistance(specs[0].accent, cssValue("status-info")) >= 0.15);
assert.ok(perceptualDistance(specs[1].accent, cssValue("status-warning")) >= 0.085);
assert.notEqual(specs[2].accent, cssValue("status-success"));
assert.notEqual(specs[2].accent, cssValue("section-ah-accent"));

for (const id of ["identity-examples", "class", "audit", "specs", "balance", "feral", "restoration", "boundaries", "matrix"]) {
  assert.ok(referenceDocument.getElementById(id), `Druid standard is missing #${id}`);
}
assert.equal(referenceDocument.querySelectorAll(".spec-grid .spec-card").length, 3);
for (const spec of specs) {
  assert.equal(referenceDocument.querySelectorAll(`#${spec.key} .mechanic-card`).length, 4, `${spec.key} needs four mechanic lanes`);
  assert.match(referenceCss, new RegExp(`\\.spec-card\\.${spec.key}\\s*\\{`));
  for (const mechanic of spec.mechanics) {
    assert.ok(
      referenceHtml.includes(`var(--mechanic-${spec.key}-${mechanic.key})`),
      `Druid reference must show --mechanic-${spec.key}-${mechanic.key}`
    );
  }
}
assert.match(referenceDocument.body.textContent, /Approved for implementation/i);
assert.match(referenceDocument.querySelector("#audit").textContent, /red-green simulations/);
assert.match(referenceDocument.querySelector("#specs").textContent, /Cat and Bear remain role expressions/);

const boundaryText = referenceDocument.querySelector("#boundaries").textContent;
for (const protectedMeaning of ["legendary", "Destruction", "rarity", "information", "warning", "success", "Auction House teal"]) {
  assert.ok(boundaryText.includes(protectedMeaning), `missing semantic boundary for ${protectedMeaning}`);
}

assert.match(
  sharedReferenceCss,
  /#identity-examples\[data-identity-example="druid-restoration"\]\s*\{[^}]*--guide-banner-class-deep-rgb:[^}]*--guide-banner-spec-deep-rgb:[^}]*--identity-example-class-soft:[^}]*--identity-example-spec-accent:[^}]*--identity-example-spec-rgb:/s
);
assert.equal(referenceDocument.querySelector("#identity-examples")?.getAttribute("data-identity-example"), "druid-restoration");
assert.equal(referenceDocument.querySelectorAll("#identity-examples .guide-identity-gradient").length, 2);
assert.equal(referenceDocument.querySelectorAll("#identity-examples .guide-identity-gradient--card").length, 1);
assert.equal(referenceDocument.querySelectorAll(`link[href="../assets/guide-color-system.css?v=${sharedCacheKey}"]`).length, 1);
assert.equal(referenceDocument.querySelectorAll(`link[href="../assets/internal-color-reference.css?v=${sharedCacheKey}"]`).length, 1);
assert.equal(referenceDocument.querySelectorAll(`link[href="../assets/druid-color-reference.css?v=${druidReferenceCacheKey}"]`).length, 1);

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
    document.querySelectorAll('.reference-site-nav a[href="druid-color-system.html"]').length,
    1,
    `${file} must link the Druid standard once`
  );
  assert.equal(
    document.querySelector(`link[href="../assets/guide-color-system.css?v=${sharedCacheKey}"]`)?.getAttribute("rel"),
    "stylesheet",
    `${file} must request the cache-safe Druid token release`
  );
}

const druidHubCard = colorHubDocument.querySelector('.directory-card.druid[href="druid-color-system.html"]');
assert.ok(druidHubCard, "Color Reference Hub must include the Druid directory card");
assert.match(druidHubCard.querySelector(".card-status")?.textContent || "", /Implementation approved/i);
assert.equal(
  colorHubDocument.querySelectorAll(`link[href="../assets/druid-color-reference.css?v=${druidReferenceCacheKey}"]`).length,
  1,
  "Color Reference Hub must load the Druid reference styles"
);
assert.match(referenceCss, /\.directory-card\.druid\s*\{/);

const deathKnightDocument = new JSDOM(
  fs.readFileSync(path.join(root, "internal", "death-knight-color-system.html"), "utf8")
).window.document;
const priestDocument = new JSDOM(
  fs.readFileSync(path.join(root, "internal", "priest-color-system.html"), "utf8")
).window.document;
assert.equal(deathKnightDocument.querySelector('.reference-pager a:last-child')?.getAttribute("href"), "druid-color-system.html");
assert.equal(referenceDocument.querySelector('.reference-pager a:first-child')?.getAttribute("href"), "death-knight-color-system.html");
assert.equal(referenceDocument.querySelector('.reference-pager a:last-child')?.getAttribute("href"), "priest-color-system.html");
assert.equal(priestDocument.querySelector('.reference-pager a:first-child')?.getAttribute("href"), "druid-color-system.html");

console.log("Validated the Druid color system, all specs, Color Reference Hub integration, contrast, and semantic boundaries.");
