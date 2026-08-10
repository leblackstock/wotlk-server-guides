"use strict";

const { chromium } = require("playwright");
const assert = require("node:assert/strict");

const base = process.env.AH_HUB_TEST_BASE || "http://127.0.0.1:4173";
const guideUrl = `${base}/guides/companions-mounts-accessories-ah-price-guide.html`;

async function noOverflow(page, label) {
  const overflow = await page.evaluate(
    () => document.documentElement.scrollWidth - document.documentElement.clientWidth,
  );
  assert.ok(overflow <= 1, `${label} has ${overflow}px horizontal overflow`);
}

async function verifyGuide(page, label) {
  await page.goto(guideUrl, { waitUntil: "networkidle" });
  assert.equal(await page.locator('[data-collectible-key]').count(), 128);
  assert.equal(await page.locator('[data-collectible-section]').count(), 20);
  assert.equal(await page.getByRole('heading', { name: 'Promotional and TCG mounts' }).count(), 0);
  assert.equal(await page.locator('.collectible-market-section--empty').count(), 6);
  assert.equal(
    await page.locator('[data-collectible-section="vendor-unlimited"] [data-collectible-key]').count(),
    29,
  );
  assert.equal(
    await page.locator('[data-collectible-section="vendor-limited"] [data-collectible-key]').count(),
    2,
  );
  assert.deepEqual(
    await page.locator('[data-collectible-section^="season-"] > h2').allTextContents().then(
      (values) => values.map((value) => value.replace(/↑ Top|← Seasonal/g, "").trim()),
    ),
    [
      "Love is in the Air",
      "Noblegarden",
      "Children's Week",
      "Midsummer Fire Festival",
      "Brewfest",
      "Hallow's End",
      "Day of the Dead",
      "Pilgrim's Bounty",
      "Winter Veil",
      "Lunar Festival",
      "Pirates' Day",
    ],
  );
  const holidaySpices = page.locator('[data-collectible-key="holiday-spices"]');
  assert.match(await holidaySpices.textContent(), /Exact vendor cost: 2c/);
  const woodFrog = page.locator('[data-collectible-key="wood-frog-box"]');
  assert.match(await woodFrog.textContent(), /Flik: stock 1, 30-minute restock/);
  const carpet = page.locator('[data-collectible-key="flying-carpet"]');
  assert.match(await carpet.textContent(), /Tailoring 300/);
  assert.equal(
    await page.locator('[data-collectible-section="crafted-mounts-general-use"] .profession-audience-chip').textContent(),
    "No profession required",
  );
  assert.equal(
    await page.locator('[data-collectible-section="crafted-mounts-profession-required"] .profession-audience-chip').textContent(),
    "Profession required",
  );
  assert.match(await page.locator("footer").textContent(), /Updated 2026-08-10/);
  await noOverflow(page, label);
}

(async () => {
  const browser = await chromium.launch({ headless: true });
  try {
    const desktop = await browser.newPage({ viewport: { width: 1440, height: 1000 } });
    await desktop.goto(`${base}/auction-house.html`, { waitUntil: "networkidle" });
    const card = desktop.locator('[data-ah-guide-card="collectibles"]');
    assert.equal(await card.count(), 1);
    assert.match(
      await card.getAttribute("href"),
      /companions-mounts-accessories-ah-price-guide\.html$/,
    );
    await desktop.locator("#ah-search-input").fill("Wood Frog Box");
    await desktop.waitForSelector(".ah-search-result");
    assert.match(await desktop.locator(".ah-search-item-name").first().textContent(), /Wood Frog Box/);
    await verifyGuide(desktop, "desktop collectible guide");

    const mobile = await browser.newPage({ viewport: { width: 390, height: 844 } });
    await verifyGuide(mobile, "mobile collectible guide");
    console.log("Collectible AH guide passed desktop/mobile hub, search, section, evidence, and overflow smoke checks.");
  } finally {
    await browser.close();
  }
})().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
