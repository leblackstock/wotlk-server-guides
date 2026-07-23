"use strict";

const { chromium } = require("playwright");
const assert = require("node:assert/strict");

const base = process.env.ADDON_TEST_BASE || "http://127.0.0.1:4173";

async function noOverflow(page, label) {
  const overflow = await page.evaluate(() => document.documentElement.scrollWidth - document.documentElement.clientWidth);
  assert.ok(overflow <= 1, `${label} has ${overflow}px horizontal overflow`);
}

(async () => {
  const browser = await chromium.launch({ headless: true });
  try {
    const desktop = await browser.newPage({ viewport: { width: 1280, height: 900 } });
    await desktop.goto(`${base}/guides/addons.html`, { waitUntil: "networkidle" });
    await desktop.waitForSelector(".addon-card");
    assert.equal(await desktop.locator(".addon-card").count(), 12, "Default catalog should show twelve addons");
    await desktop.locator("#addon-all-filters").click();
    const launchSpecs = desktop.locator('[data-filter-group="specialization"] .addon-filter-chip');
    assert.equal(await launchSpecs.count(), 1, "Only specializations with targeted launch records should be shown");
    assert.match(await launchSpecs.first().textContent(), /Protection/);
    assert.equal(await desktop.locator("#addon-active-area").isHidden(), true, "Active-filter row should stay hidden with no active state");
    await noOverflow(desktop, "Desktop catalog");

    await desktop.locator("#addon-search-input").fill("healbt");
    await desktop.waitForTimeout(80);
    assert.equal(await desktop.locator(".addon-card h2").first().textContent(), "HealBot");

    await desktop.locator("#addon-search-input").fill("dps meter");
    await desktop.waitForTimeout(80);
    assert.equal(await desktop.locator(".addon-card h2").first().textContent(), "Skada Revisited");

    await desktop.locator("#addon-search-input").fill("chat timestamps");
    await desktop.waitForTimeout(80);
    assert.equal(await desktop.locator(".addon-card h2").first().textContent(), "Chatter");

    await desktop.goto(`${base}/guides/addons.html?activity=leveling`, { waitUntil: "networkidle" });
    await desktop.waitForSelector('.addon-card[data-addon-id="questie"]');
    assert.match(await desktop.locator("#addon-context-banner").textContent(), /Leveling/);
    assert.equal(await desktop.locator(".addon-card h2").first().textContent(), "Questie");
    assert.equal(await desktop.locator('.addon-card[data-addon-id="questie"] .addon-badge-essential').count(), 1);

    await desktop.goto(`${base}/guides/addons.html?activity=raids#addon=skada`, { waitUntil: "networkidle" });
    await desktop.waitForSelector("#addon-details-dialog[open]");
    assert.equal(await desktop.locator("#addon-dialog-title").textContent(), "Skada Revisited");
    assert.match(await desktop.locator("#addon-dialog-content").textContent(), /1\.8\.87/);
    assert.match(await desktop.locator("#addon-dialog-content").textContent(), /many battles/);
    assert.match(await desktop.locator("#addon-dialog-content").textContent(), /No addon conflicts/);
    assert.equal(await desktop.locator('a[href="https://warperia.com/addon-wotlk/skada-revisited/"]').count() > 0, true);

    await desktop.goto(`${base}/guides/addons.html?role=healer#addon=chatter`, { waitUntil: "networkidle" });
    await desktop.waitForSelector("#addon-details-dialog[open]");
    assert.equal(await desktop.locator("#addon-dialog-title").textContent(), "Chatter");
    const chatterText = await desktop.locator("#addon-dialog-content").textContent();
    assert.match(chatterText, /1\.0/);
    assert.match(chatterText, /Use guildnotes/);
    assert.match(chatterText, /Alt Linking/);
    assert.equal(await desktop.locator('a[href="https://warperia.com/addon-wotlk/chatter/"]').count() > 0, true);

    await desktop.goto(`${base}/guides/addons.html?class=paladin&spec=paladin-protection&role=tank`, { waitUntil: "networkidle" });
    await desktop.waitForSelector(".addon-card");
    assert.match(await desktop.locator("#addon-context-banner").textContent(), /Protection Paladin/);
    const firstTwo = await desktop.locator(".addon-card h2").evaluateAll((nodes) => nodes.slice(0, 2).map((node) => node.textContent));
    assert.deepEqual(firstTwo, ["Deadly Boss Mods", "PallyPower"]);
    assert.equal(await desktop.locator(".addon-badge-essential").count(), 2);

    for (const equivalentUrl of [
      `${base}/guides/addons.html?class=paladin&role=tank`,
      `${base}/guides/addons.html?class=paladin&spec=paladin-protection`
    ]) {
      await desktop.goto(equivalentUrl, { waitUntil: "networkidle" });
      await desktop.waitForSelector(".addon-card");
      assert.match(await desktop.locator("#addon-context-banner").textContent(), /Showing recommendations for Protection Paladin/);
      const equivalentFirstTwo = await desktop.locator(".addon-card h2").evaluateAll((nodes) => nodes.slice(0, 2).map((node) => node.textContent));
      assert.deepEqual(equivalentFirstTwo, ["Deadly Boss Mods", "PallyPower"]);
      assert.equal(await desktop.locator(".addon-badge-essential").count(), 2);
    }

    await desktop.goto(`${base}/guides/addons.html?class=warrior&role=dps`, { waitUntil: "networkidle" });
    await desktop.waitForSelector("#addon-context-banner:not([hidden])");
    assert.match(await desktop.locator("#addon-context-banner").textContent(), /Choose Arms or Fury/);

    await desktop.goto(`${base}/guides/addons.html?class=paladin&spec=paladin-protection&role=tank`, { waitUntil: "networkidle" });
    await desktop.waitForSelector('.addon-card[data-addon-id="healbot"]');

    const healbotCard = desktop.locator('.addon-card[data-addon-id="healbot"]');
    const healbotDetails = healbotCard.locator(".addon-details-button");
    await healbotDetails.focus();
    await healbotDetails.click();
    await desktop.waitForSelector("#addon-details-dialog[open]");
    assert.match(await desktop.locator("#addon-dialog-content").textContent(), /Protection Paladin setup/);
    await desktop.keyboard.press("Escape");
    await desktop.waitForFunction(() => !document.getElementById("addon-details-dialog").open);
    assert.equal(await desktop.evaluate(() => document.activeElement?.closest(".addon-card")?.dataset.addonId), "healbot", "Focus should return to HealBot card");

    await desktop.goto(`${base}/guides/addons.html?class=paladin&spec=paladin-protection&role=tank#addon=healbot`, { waitUntil: "networkidle" });
    await desktop.waitForSelector("#addon-details-dialog[open]");
    assert.equal(await desktop.locator("#addon-dialog-title").textContent(), "HealBot");

    await desktop.goto(`${base}/guides/addons.html?class=priest&role=healer#addon=healbot`, { waitUntil: "networkidle" });
    await desktop.waitForSelector("#addon-details-dialog[open]");
    assert.doesNotMatch(await desktop.locator(".addon-dialog-summary").textContent(), /Righteous Defense|Protection Paladin/);
    const visibleProtectionHeadings = await desktop.locator("#addon-dialog-content h3:visible").filter({ hasText: "Protection Paladin" }).count();
    assert.equal(visibleProtectionHeadings, 0, "Protection setup should not be automatically exposed to Priest Healer context");

    await desktop.goto(`${base}/guides/addons.html?profession=alchemy`, { waitUntil: "networkidle" });
    await desktop.waitForSelector("#addon-empty:not([hidden])");
    assert.equal(await desktop.locator("#addon-grid").isHidden(), true, "Result grid should hide when filters produce no results");
    await desktop.locator("#addon-empty-clear").click();
    await desktop.waitForSelector(".addon-card");
    assert.equal(await desktop.locator(".addon-card").count(), 12);

    const mobile = await browser.newPage({ viewport: { width: 390, height: 844 }, isMobile: true });
    await mobile.goto(`${base}/guides/addons.html?class=paladin&spec=paladin-protection&role=tank#addon=healbot`, { waitUntil: "networkidle" });
    await mobile.waitForSelector("#addon-details-dialog[open]");
    await noOverflow(mobile, "Mobile catalog and drawer");
    assert.equal(await mobile.locator(".addon-grid").evaluate((node) => getComputedStyle(node).gridTemplateColumns.split(" ").length), 1);

    console.log("Addon browser smoke tests passed at desktop and mobile widths.");
  } finally {
    await browser.close();
  }
})().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
