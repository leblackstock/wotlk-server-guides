"use strict";

const { chromium } = require("playwright");
const assert = require("node:assert/strict");

const base = process.env.DRUID_GUIDE_TEST_BASE || "http://127.0.0.1:4173";
const slugs = ["balance-druid", "feral-cat-druid", "feral-bear-druid", "restoration-druid"];
const suffixes = ["pve-guide", "playing", "setting-up", "gearing", "gear-targets", "raiding"];

(async () => {
  const browser = await chromium.launch({ headless: true });
  let checked = 0;

  try {
    const desktop = await browser.newPage({ viewport: { width: 1280, height: 900 } });
    const pageErrors = [];
    desktop.on("pageerror", (error) => pageErrors.push(error.message));

    for (const slug of slugs) {
      for (const suffix of suffixes) {
        const response = await desktop.goto(`${base}/guides/${slug}-${suffix}.html`, { waitUntil: "domcontentloaded" });
        assert.equal(response.status(), 200, `${slug}-${suffix}: HTTP status`);
        await desktop.waitForSelector("header.guide-hero");
        assert.ok(await desktop.locator(".guide-jump-nav a").count() >= 2, `${slug}-${suffix}: jump navigation`);
        assert.match((await desktop.locator(".wrap > footer").textContent()).trim(), /Updated 2026-08-14$/, `${slug}-${suffix}: footer date`);
        const overflow = await desktop.evaluate(() => document.documentElement.scrollWidth - document.documentElement.clientWidth);
        assert.ok(overflow <= 1, `${slug}-${suffix}: ${overflow}px desktop overflow`);
        checked += 1;
      }

      await desktop.goto(`${base}/guides/${slug}-playing.html`, { waitUntil: "domcontentloaded" });
      await desktop.waitForFunction(() => document.querySelectorAll('.spec-card-header[role="button"]').length === 6);
      const header = desktop.locator(".spec-card-header").first();
      await header.focus();
      await header.press("Enter");
      assert.equal(await desktop.locator(".spec-card:visible").count(), 1, `${slug}: Enter focuses one playbook card`);
      await desktop.keyboard.press("Escape");
      assert.equal(await desktop.locator(".spec-card:visible").count(), 6, `${slug}: Escape restores playbook cards`);
      assert.ok(
        await desktop.locator("span.ability-choice[data-entity-icon] > img.entity-icon").count() >= 18,
        `${slug}: playbook action icons are linked`
      );
      assert.ok(await desktop.locator("span.ability-choice[data-entity-icon] > a.wowhead-link[data-wowhead]").count() >= 18, `${slug}: playbook action hover links`);

      await desktop.goto(`${base}/guides/${slug}-setting-up.html`, { waitUntil: "domcontentloaded" });
      assert.match(await desktop.locator(".talent-embed").getAttribute("src"), /wowhead\.com\/wotlk\/talent-calc\/embed\/druid\//, `${slug}: talent embed`);
      assert.match(await desktop.locator(".talent-fallback a").getAttribute("href"), /wowhead\.com\/wotlk\/talent-calc\/druid\//, `${slug}: talent fallback`);

      await desktop.goto(`${base}/guides/${slug}-raiding.html`, { waitUntil: "domcontentloaded" });
      assert.equal(await desktop.locator(".raid-encounter").count(), 10, `${slug}: encounter count`);
      await desktop.locator(".raid-note").first().evaluate((node) => { node.hidden = true; });
      assert.equal(await desktop.locator(".raid-note").first().evaluate((node) => getComputedStyle(node).display), "none", `${slug}: screen filter state`);
      await desktop.emulateMedia({ media: "print" });
      assert.notEqual(await desktop.locator(".raid-note").first().evaluate((node) => getComputedStyle(node).display), "none", `${slug}: print restores filtered notes`);
      assert.equal(await desktop.locator(".filter-panel").evaluate((node) => getComputedStyle(node).display), "none", `${slug}: print hides controls`);
      await desktop.emulateMedia({ media: "screen" });
    }

    assert.deepEqual(pageErrors, [], `Druid browser page errors: ${pageErrors.join("; ")}`);

    const mobile = await browser.newPage({ viewport: { width: 390, height: 844 }, isMobile: true });
    for (const slug of slugs) {
      await mobile.goto(`${base}/guides/${slug}-pve-guide.html`, { waitUntil: "domcontentloaded" });
      await mobile.waitForSelector(".operating-manual");
      const overflow = await mobile.evaluate(() => document.documentElement.scrollWidth - document.documentElement.clientWidth);
      assert.ok(overflow <= 1, `${slug}: ${overflow}px mobile overflow`);
      assert.equal(await mobile.locator(".engine-grid .engine-step").count(), 4, `${slug}: mobile engine steps`);
    }

    await mobile.goto(`${base}/index.html`, { waitUntil: "domcontentloaded" });
    assert.equal(await mobile.locator(".class-guide-card").count(), 13, "Hub guide-family card count");
    assert.equal(await mobile.locator('.class-guide-card[href*="druid"]').count(), 4, "Hub Druid card count");
    assert.ok(
      await mobile.evaluate(() => document.documentElement.scrollWidth - document.documentElement.clientWidth) <= 1,
      "Hub mobile overflow"
    );

    console.log(`Druid browser smoke tests passed for ${checked} pages plus keyboard, talent fallback, print, and mobile checks.`);
  } finally {
    await browser.close();
  }
})().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
