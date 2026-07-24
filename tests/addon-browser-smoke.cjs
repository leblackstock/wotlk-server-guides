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
    assert.equal(await desktop.locator(".addon-card").count(), 16, "Default catalog should show sixteen addons");
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
    const chatterCard = desktop.locator('.addon-card[data-addon-id="chatter"]');
    assert.equal(await chatterCard.locator(".addon-badge-warning").count(), 0, "Server-sensitive warning should stay out of the card headline");
    assert.equal(await chatterCard.locator(".addon-card-tag").first().textContent(), "Chat Enhancement");

    await desktop.locator("#addon-search-input").fill("auction house");
    await desktop.waitForTimeout(80);
    assert.equal(await desktop.locator(".addon-card h2").first().textContent(), "Auctioneer Suite");
    const auctioneerCard = desktop.locator('.addon-card[data-addon-id="auctioneer-suite"]');
    assert.equal(await auctioneerCard.locator(".addon-card-tag").first().textContent(), "Auction House");

    await desktop.locator("#addon-search-input").fill("addon manager");
    await desktop.waitForTimeout(80);
    assert.equal(await desktop.locator(".addon-card h2").first().textContent(), "Addon Control Panel");
    const acpCard = desktop.locator('.addon-card[data-addon-id="addon-control-panel"]');
    assert.equal(await acpCard.locator(".addon-card-tag").first().textContent(), "Addon Management");
    assert.equal(await acpCard.locator(".addon-card-tag", { hasText: "Not Yet Tested on Hellscream" }).count(), 1);


    await desktop.locator("#addon-search-input").fill("action bars");
    await desktop.waitForTimeout(80);
    assert.equal(await desktop.locator(".addon-card h2").first().textContent(), "Bartender4");
    const bartenderCard = desktop.locator('.addon-card[data-addon-id="bartender4"]');
    assert.equal(await bartenderCard.locator(".addon-card-tag").first().textContent(), "Action Bars");
    assert.equal(await bartenderCard.locator(".addon-card-tag", { hasText: "Tested on Hellscream" }).count(), 1);

    await desktop.locator("#addon-search-input").fill("gear sets");
    await desktop.waitForTimeout(80);
    assert.equal(await desktop.locator(".addon-card h2").first().textContent(), "Outfitter");
    const outfitterCard = desktop.locator('.addon-card[data-addon-id="outfitter"]');
    assert.equal(await outfitterCard.locator(".addon-card-tag").first().textContent(), "Equipment Sets");
    assert.equal(await outfitterCard.locator(".addon-card-tag", { hasText: "Tested on Hellscream" }).count(), 1);

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
    assert.match(chatterText, /Server-sensitive/);
    assert.equal(await desktop.locator('a[href="https://warperia.com/addon-wotlk/chatter/"]').count() > 0, true);

    await desktop.goto(`${base}/guides/addons.html?role=dps#addon=auctioneer-suite`, { waitUntil: "networkidle" });
    await desktop.waitForSelector("#addon-details-dialog[open]");
    assert.equal(await desktop.locator("#addon-dialog-title").textContent(), "Auctioneer Suite");
    const auctioneerText = await desktop.locator("#addon-dialog-content").textContent();
    assert.match(auctioneerText, /5\.9\.4961/);
    assert.match(auctioneerText, /Load out of date AddOns/);
    const moduleMap = desktop.locator(".addon-module-map");
    assert.equal(await moduleMap.locator("summary").textContent(), "Suite module map (43)");
    await moduleMap.locator("summary").click();
    assert.equal(await moduleMap.locator(".addon-module-group").count(), 5);
    assert.equal(await moduleMap.locator("dt").count(), 43);
    assert.equal(await moduleMap.locator("dt", { hasText: "BeanCounter" }).count(), 1);
    assert.equal(await moduleMap.locator("dt", { hasText: "Auc-Util-Appraiser" }).count(), 1);
    assert.equal(await desktop.locator('a[href="https://web.archive.org/web/20110112162840/http://auctioneeraddon.com/dl/Release/AuctioneerSuite-5.9.4961.zip"]').count() > 0, true);
    await noOverflow(desktop, "Auctioneer module drawer");


    await desktop.goto(`${base}/guides/addons.html?role=dps#addon=addon-control-panel`, { waitUntil: "networkidle" });
    await desktop.waitForSelector("#addon-details-dialog[open]");
    assert.equal(await desktop.locator("#addon-dialog-title").textContent(), "Addon Control Panel");
    const acpText = await desktop.locator("#addon-dialog-content").textContent();
    assert.match(acpText, /3\.3\.7/);
    assert.match(acpText, /not yet been tested on Hellscream/);
    assert.match(acpText, /Recommended/);
    assert.equal(await desktop.locator('a[href="https://www.curseforge.com/wow/addons/acp/files/471104"]').count() > 0, true);
    await noOverflow(desktop, "ACP details drawer");

    await desktop.goto(`${base}/guides/addons.html?role=dps#addon=bartender4`, { waitUntil: "networkidle" });
    await desktop.waitForSelector("#addon-details-dialog[open]");
    assert.equal(await desktop.locator("#addon-dialog-title").textContent(), "Bartender4");
    const bartenderText = await desktop.locator("#addon-dialog-content").textContent();
    assert.match(bartenderText, /4\.4\.2-12-g94f3b58/);
    assert.match(bartenderText, /No addon conflicts/);
    assert.match(bartenderText, /Vehicle action bars still need focused testing/);
    assert.match(bartenderText, /top action-bar recommendation/i);
    assert.equal(await desktop.locator('a[href="https://www.curseforge.com/wow/addons/bartender4/files/439962"]').count() > 0, true);
    await noOverflow(desktop, "Bartender4 details drawer");

    await desktop.goto(`${base}/guides/addons.html?role=healer#addon=outfitter`, { waitUntil: "networkidle" });
    await desktop.waitForSelector("#addon-details-dialog[open]");
    assert.equal(await desktop.locator("#addon-dialog-title").textContent(), "Outfitter");
    const outfitterText = await desktop.locator("#addon-dialog-content").textContent();
    assert.match(outfitterText, /5\.0/);
    assert.match(outfitterText, /No addon conflicts were noticed/);
    assert.match(outfitterText, /equipment-set manager/i);
    assert.equal(await desktop.locator('a[href="https://warperia.com/addon-wotlk/outfitter/"]').count() > 0, true);
    await noOverflow(desktop, "Outfitter details drawer");

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
    assert.equal(await desktop.locator(".addon-card").count(), 15);

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
