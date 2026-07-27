"use strict";

const { chromium } = require("playwright");
const assert = require("node:assert/strict");

const base = process.env.AH_HUB_TEST_BASE || "http://127.0.0.1:4173";

async function noOverflow(page, label) {
  const overflow = await page.evaluate(() => document.documentElement.scrollWidth - document.documentElement.clientWidth);
  assert.ok(overflow <= 1, `${label} has ${overflow}px horizontal overflow`);
}

(async () => {
  const browser = await chromium.launch({ headless: true });
  try {
    const desktop = await browser.newPage({ viewport: { width: 1280, height: 900 } });
    await desktop.goto(`${base}/index.html`, { waitUntil: "networkidle" });
    await desktop.waitForSelector("#ah-search-input");

    assert.equal(await desktop.locator(".ah-hub-browse").getAttribute("href"), "./auction-house.html");
    assert.equal(await desktop.locator(".guide-card.has-guide-icon").count(), 0, "AH guide cards should not remain on the main hub");
    assert.equal(await desktop.locator(".library-hub-ah .library-hub-chip").count(), 4);
    assert.equal(await desktop.locator(".library-hub-addons .library-hub-chip").count(), 4);

    const searchBox = await desktop.locator(".library-hub-ah .ah-search-input-wrap").boundingBox();
    const browseButton = await desktop.locator(".ah-hub-browse").boundingBox();
    assert.ok(searchBox && browseButton, "Search and Browse controls should be visible");
    assert.ok(Math.abs(searchBox.y - browseButton.y) <= 1, "Browse button should align with the search bar");
    assert.equal(Math.round(browseButton.height), 44, "Browse button should match the search-bar height");

    await desktop.locator("#ah-search-input").fill("Dark Iron Scraps");
    await desktop.waitForSelector(".ah-search-result");
    assert.match(await desktop.locator(".ah-search-item-name").first().textContent(), /Dark Iron Scraps/);
    assert.deepEqual(await desktop.locator(".ah-search-result").first().locator(".ah-search-target-label").allTextContents(), ["Target Bid", "Buyout"]);
    assert.equal(await desktop.locator(".ah-search-result").first().locator(".ah-search-target-value").count(), 2);
    await noOverflow(desktop, "Desktop main hub");

    await desktop.locator("#addon-hub-search-input").fill("healbt");
    await desktop.waitForSelector("#addon-hub-search-results .addon-hub-search-result");
    assert.equal(await desktop.locator("#addon-hub-search-results .ah-search-item-name").first().textContent(), "HealBot");
    assert.match(await desktop.locator("#addon-hub-search-results .addon-hub-search-result").first().getAttribute("href"), /#addon=healbot$/);
    assert.equal(await desktop.locator("#addon-hub-browse").getAttribute("href"), "./guides/addons.html?q=healbt");

    const addonSearchBox = await desktop.locator(".library-hub-addons .ah-search-input-wrap").boundingBox();
    const addonBrowseButton = await desktop.locator("#addon-hub-browse").boundingBox();
    assert.ok(addonSearchBox && addonBrowseButton, "Addon Search and Browse controls should be visible");
    assert.ok(Math.abs(addonSearchBox.y - addonBrowseButton.y) <= 1, "Addon Browse button should align with the search bar");
    assert.equal(Math.round(addonBrowseButton.height), 44, "Addon Browse button should match the search-bar height");

    await desktop.locator(".ah-hub-browse").click();
    await desktop.waitForURL(`${base}/auction-house.html`);
    assert.equal(await desktop.locator(".guide-card.has-guide-icon").count(), 16, "Auction House hub should list all sixteen guides");
    assert.equal(await desktop.locator(".ah-search-quick-links .library-hub-chip").count(), 4);
    assert.match(await desktop.locator("#ah-search-count").textContent(), /^[\d,]+ items across 16 guides$/);

    await desktop.locator("#ah-search-input").fill("Sanguine Hibiscus");
    await desktop.waitForSelector(".ah-search-result");
    assert.match(await desktop.locator(".ah-search-item-name").first().textContent(), /Sanguine Hibiscus/);
    assert.deepEqual(await desktop.locator(".ah-search-result").first().locator(".ah-search-target-label").allTextContents(), ["Target Bid", "Buyout"]);
    assert.match(await desktop.locator(".ah-search-result").first().getAttribute("href"), /^\.\/guides\//);
    await noOverflow(desktop, "Desktop Auction House hub");

    const mobile = await browser.newPage({ viewport: { width: 390, height: 844 }, isMobile: true });
    await mobile.goto(`${base}/index.html`, { waitUntil: "networkidle" });
    await mobile.waitForSelector(".ah-hub-browse");
    const mobileSearchRows = mobile.locator(".library-hub-search-row");
    assert.equal(await mobileSearchRows.count(), 2);
    for (let index = 0; index < 2; index += 1) {
      assert.equal(await mobileSearchRows.nth(index).evaluate((node) => getComputedStyle(node).gridTemplateColumns.split(" ").length), 1);
    }
    await noOverflow(mobile, "Mobile main hub");

    await mobile.goto(`${base}/auction-house.html`, { waitUntil: "networkidle" });
    assert.equal(await mobile.locator(".guide-card.has-guide-icon").count(), 16);
    await noOverflow(mobile, "Mobile Auction House hub");

    console.log("Auction House hub smoke tests passed at desktop and mobile widths.");
  } finally {
    await browser.close();
  }
})().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
