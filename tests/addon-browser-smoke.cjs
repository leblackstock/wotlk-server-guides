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
    assert.equal(await desktop.locator(".addon-card").count(), 18, "Default catalog should show eighteen addons");
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
    assert.equal(await acpCard.locator(".addon-card-tag", { hasText: "Tested on Hellscream" }).count(), 1);


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

    await desktop.locator("#addon-search-input").fill("stat weights");
    await desktop.waitForTimeout(80);
    assert.equal(await desktop.locator(".addon-card h2").first().textContent(), "Pawn");
    const pawnCard = desktop.locator('.addon-card[data-addon-id="pawn"]');
    assert.equal(await pawnCard.locator(".addon-card-tag").first().textContent(), "Gear Evaluation");
    assert.equal(await pawnCard.locator(".addon-card-tag", { hasText: "Tested on Hellscream" }).count(), 1);

    await desktop.locator("#addon-search-input").fill("custom loot");
    await desktop.waitForTimeout(80);
    assert.equal(await desktop.locator(".addon-card h2").first().textContent(), "AtlasLoot Enhanced for Hellscream");
    const atlasLootCard = desktop.locator('.addon-card[data-addon-id="atlasloot-hellscream"]');
    assert.equal(await atlasLootCard.locator(".addon-card-tag").first().textContent(), "Loot Database & Maps");
    assert.equal(await atlasLootCard.locator(".addon-card-tag", { hasText: "Tested on Hellscream" }).count(), 1);

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
    const skadaNotes = desktop.locator(".addon-compatibility-notes");
    assert.equal(await skadaNotes.evaluate((node) => node.open), false);
    assert.equal(await skadaNotes.locator(".addon-compatibility-note").first().isVisible(), false);
    assert.equal(await desktop.locator('a[href="https://warperia.com/addon-wotlk/skada-revisited/"]').count() > 0, true);

    await desktop.goto(`${base}/guides/addons.html?role=healer#addon=chatter`, { waitUntil: "networkidle" });
    await desktop.waitForSelector("#addon-details-dialog[open]");
    assert.equal(await desktop.locator("#addon-dialog-title").textContent(), "Chatter");
    const chatterText = await desktop.locator("#addon-dialog-content").textContent();
    assert.match(chatterText, /1\.0/);
    assert.match(chatterText, /Use guildnotes/);
    assert.match(chatterText, /Alt Linking/);
    assert.match(chatterText, /Server-sensitive/);
    assert.equal(await desktop.locator(".addon-important-note").isVisible(), true);
    assert.match(await desktop.locator(".addon-important-note").textContent(), /Use guildnotes/);
    assert.equal(await desktop.locator(".addon-compatibility-notes").evaluate((node) => node.open), false);
    assert.equal(await desktop.locator('a[href="https://warperia.com/addon-wotlk/chatter/"]').count() > 0, true);

    await desktop.goto(`${base}/guides/addons.html?role=dps#addon=auctioneer-suite`, { waitUntil: "networkidle" });
    await desktop.waitForSelector("#addon-details-dialog[open]");
    assert.equal(await desktop.locator("#addon-dialog-title").textContent(), "Auctioneer Suite");
    const auctioneerText = await desktop.locator("#addon-dialog-content").textContent();
    assert.match(auctioneerText, /5\.9\.4961/);
    assert.match(auctioneerText, /Load out of date AddOns/);
    const depositGuide = desktop.locator(".addon-configuration-guide");
    assert.equal(await depositGuide.locator("summary").textContent(), "Hellscream deposit-rate correction (10% rate, 1c minimum)");
    assert.equal(await depositGuide.evaluate((node) => node.closest("section.addon-dialog-section")?.querySelector(":scope > h3")?.textContent), "Troubleshooting");
    assert.equal(await depositGuide.evaluate((node) => node.open), false);
    await depositGuide.locator("summary").click();
    assert.match(await depositGuide.textContent(), /HELLSCREAM_DEPOSIT_DIVISOR = 10/);
    assert.match(await depositGuide.textContent(), /MINIMUM_DEPOSIT = 1/);
    assert.match(await depositGuide.textContent(), /launcher\\Interface\\AddOns\\Auc-Advanced\\CorePost\.lua/);
    assert.doesNotMatch(await depositGuide.textContent(), /[A-Z]:\\/);
    const auctioneerNotes = desktop.locator(".addon-compatibility-notes");
    assert.equal(await auctioneerNotes.locator("summary").textContent(), "Additional compatibility notes (5)");
    assert.equal(await auctioneerNotes.evaluate((node) => node.open), false);
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
    assert.match(acpText, /3\.3\.5/);
    assert.match(acpText, /extensively tested and works on the server/);
    assert.match(acpText, /ACP 3\.3\.7 is not compatible/);
    assert.match(acpText, /Recommended/);
    assert.equal(await desktop.locator('a[href="https://warperia.com/addon-wotlk/addon-control-panel/"]').count() > 0, true);
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

    await desktop.goto(`${base}/guides/addons.html?role=tank#addon=pawn`, { waitUntil: "networkidle" });
    await desktop.waitForSelector("#addon-details-dialog[open]");
    assert.equal(await desktop.locator("#addon-dialog-title").textContent(), "Pawn");
    const pawnText = await desktop.locator("#addon-dialog-content").textContent();
    assert.match(pawnText, /1\.3\.8/);
    assert.match(pawnText, /no errors are remembered/i);
    assert.match(pawnText, /\/pawn list Scale Name/);
    assert.match(pawnText, /copy the chosen built-in scale/i);
    assert.match(pawnText, /\/pawn import/);
    assert.match(pawnText, /caps/);
    assert.equal(await desktop.locator('a[href="https://warperia.com/addon-wotlk/pawn/"]').count() > 0, true);
    await noOverflow(desktop, "Pawn details drawer");

    await desktop.goto(`${base}/guides/addons.html?activity=raids#addon=atlasloot-hellscream`, { waitUntil: "networkidle" });
    await desktop.waitForSelector("#addon-details-dialog[open]");
    assert.equal(await desktop.locator("#addon-dialog-title").textContent(), "AtlasLoot Enhanced for Hellscream");
    const atlasLootText = await desktop.locator("#addon-dialog-content").textContent();
    assert.match(atlasLootText, /v5\.11\.04/);
    assert.match(atlasLootText, /February 5, 2026/);
    assert.match(atlasLootText, /Burning Crusade heroic items/);
    assert.match(atlasLootText, /Crimson Crusade reputation items/);
    assert.match(atlasLootText, /closing AtlasLoot.*reopening/i);
    assert.match(atlasLootText, /Stock AtlasLoot v5\.11\.04 fallback/);
    assert.match(atlasLootText, /Join the Hellscream Discord/);
    assert.match(atlasLootText, /button above/);
    assert.doesNotMatch(atlasLootText, /Discord below/);
    const atlasLootDrawer = desktop.locator("#addon-dialog-content");
    const joinDiscord = atlasLootDrawer.locator('a.addon-prerequisite-link[href="https://discord.gg/pe69BfNZG5"]');
    const downloadPost = atlasLootDrawer.locator('a.addon-dialog-download[href="https://discord.com/channels/608456284643262504/1328533521983340574/1469088948956434493"]');
    const stockFallback = atlasLootDrawer.locator('a[href="https://warperia.com/addon-wotlk/atlasloot-enhanced/"]');
    assert.equal(await joinDiscord.count(), 1);
    assert.equal(await downloadPost.count(), 1);
    assert.equal(await stockFallback.count(), 1);
    assert.equal(await desktop.locator(".addon-important-note").isVisible(), true);
    assert.match(await desktop.locator(".addon-important-note").textContent(), /same Hellscream package/);
    assert.equal(await desktop.locator(".addon-compatibility-notes").evaluate((node) => node.open), false);
    const joinBorder = await joinDiscord.evaluate((node) => getComputedStyle(node).borderColor);
    const downloadBorder = await downloadPost.evaluate((node) => getComputedStyle(node).borderColor);
    const fallbackBorder = await stockFallback.evaluate((node) => getComputedStyle(node).borderColor);
    assert.equal(joinBorder, downloadBorder, "Join Discord outline should use the download-post blue");
    assert.notEqual(joinBorder, fallbackBorder, "Join Discord should stand apart from the stock fallback");
    assert.match(atlasLootText, /Open the AtlasLoot Download Post/);
    assert.equal(await desktop.locator('a[href="https://discord.gg/pe69BfNZG5"]').count() > 0, true);
    assert.equal(await desktop.locator('a[href="https://discord.com/channels/608456284643262504/1328533521983340574/1469088948956434493"]').count() > 0, true);
    assert.equal(await desktop.locator('a[href="https://warperia.com/addon-wotlk/atlasloot-enhanced/"]').count() > 0, true);
    await noOverflow(desktop, "AtlasLoot details drawer");

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
    assert.equal(await desktop.locator(".addon-card").count(), 18);

    const mobile = await browser.newPage({ viewport: { width: 390, height: 844 }, isMobile: true });
    await mobile.goto(`${base}/guides/addons.html?class=paladin&spec=paladin-protection&role=tank#addon=healbot`, { waitUntil: "networkidle" });
    await mobile.waitForSelector("#addon-details-dialog[open]");
    await noOverflow(mobile, "Mobile catalog and drawer");
    assert.equal(await mobile.locator(".addon-grid").evaluate((node) => getComputedStyle(node).gridTemplateColumns.split(" ").length), 1);

    await mobile.goto(`${base}/guides/addons.html?activity=raids#addon=atlasloot-hellscream`, { waitUntil: "networkidle" });
    await mobile.waitForSelector("#addon-details-dialog[open]");
    assert.equal(await mobile.locator("#addon-dialog-title").textContent(), "AtlasLoot Enhanced for Hellscream");
    await noOverflow(mobile, "Mobile AtlasLoot drawer");

    console.log("Addon browser smoke tests passed at desktop and mobile widths.");
  } finally {
    await browser.close();
  }
})().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
