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
const cardSurface = "#121820";

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

function oklab(hex) {
  const [red, green, blue] = [1, 3, 5].map((index) => linearChannel(Number.parseInt(hex.slice(index, index + 2), 16)));
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

function perceptualDistance(first, second) {
  const firstLab = oklab(first);
  const secondLab = oklab(second);
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
    specAccent: "#63d0b0",
    specAccentSoft: "#c4f3e5",
    specAccentDeep: "#205d4c",
    specAccentRgb: "99, 208, 176",
    mechanics: [
      { key: "felguard", color: "#63d0b0", soft: "#c4f3e5", rgb: "99, 208, 176" },
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
}

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

console.log("Validated the three-spec Warlock color system and semantic boundaries.");
