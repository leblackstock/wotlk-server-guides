"use strict";

const { chromium } = require("playwright");
const assert = require("node:assert/strict");

const base = process.env.AH_HUB_TEST_BASE || "http://127.0.0.1:4173";

async function noOverflow(page, label) {
  const overflow = await page.evaluate(() => document.documentElement.scrollWidth - document.documentElement.clientWidth);
  assert.ok(overflow <= 1, `${label} has ${overflow}px horizontal overflow`);
}

async function verifyAuditedCraftedGuide(page, options) {
  const { filename, rows, sections, key, target, recipeSpell, notePattern, label } = options;
  await page.goto(`${base}/guides/${filename}`, { waitUntil: "networkidle" });
  assert.equal(await page.locator('[data-market-source="crafted"]').count(), rows);
  assert.equal(await page.locator(".crafted-market-section").count(), sections);
  assert.match(await page.locator(".crafted-market-intro").textContent(), /exact 3\.3\.5 recipe/);
  assert.equal(await page.locator(".crafted-market-shared-note").count(), 1);
  assert.equal(await page.locator(".crafted-note-ref").count(), rows);
  assert.equal(await page.locator(".crafted-item-note").count(), rows);
  assert.equal(await page.locator(".crafted-recipe-link").count(), rows);
  assert.equal(await page.locator('[data-column="notes"] strong', { hasText: "Reagent floor:" }).count(), 0);
  const representativeRow = page.locator(`[data-crafted-key="${key}"]`);
  assert.equal(
    await representativeRow.locator('[data-column="target"] .buyout').textContent(),
    target
  );
  assert.match(await representativeRow.locator(".crafted-item-note").textContent(), notePattern);
  const recipeLink = representativeRow.locator(".crafted-recipe-link");
  assert.equal(await recipeLink.textContent(), "Recipe & mats ↗");
  assert.equal(await recipeLink.getAttribute("href"), `https://www.wowhead.com/wotlk/spell=${recipeSpell}`);
  assert.equal(await recipeLink.getAttribute("data-wowhead"), `spell=${recipeSpell}&domain=wotlk`);
  assert.equal(await recipeLink.getAttribute("target"), "_blank");
  assert.equal(await recipeLink.getAttribute("rel"), "noopener");
  assert.match(await page.locator("footer").textContent(), /Updated 2026-08-03/);
  await noOverflow(page, label);
}

(async () => {
  const browser = await chromium.launch({ headless: true });
  try {
    const desktop = await browser.newPage({ viewport: { width: 1280, height: 900 } });
    await desktop.goto(`${base}/index.html`, { waitUntil: "networkidle" });
    await desktop.waitForSelector("#ah-search-input");

    const hubLogoLink = desktop.locator(".hub-logo-link");
    assert.equal(await hubLogoLink.getAttribute("href"), "./index.html");
    assert.equal(await hubLogoLink.getAttribute("aria-label"), "Reload Guide Hub");
    await Promise.all([
      desktop.waitForNavigation({ waitUntil: "networkidle" }),
      hubLogoLink.click()
    ]);
    assert.equal(desktop.url(), `${base}/index.html`);

    assert.equal(await desktop.locator(".ah-hub-browse").getAttribute("href"), "./auction-house.html");
    assert.equal(await desktop.locator(".guide-card.has-guide-icon").count(), 0, "AH guide cards should not remain on the main hub");
    assert.equal(await desktop.locator(".library-hub-ah .library-hub-chip").count(), 5);
    assert.equal(await desktop.locator(".library-hub-addons .library-hub-chip").count(), 4);

    const merchantGuildLink = desktop.locator(".library-hub-secret-link");
    assert.equal(await merchantGuildLink.count(), 1);
    assert.equal(await merchantGuildLink.getAttribute("href"), "./guides/merchants-guild.html");
    assert.equal(await merchantGuildLink.getAttribute("aria-label"), "Open The Merchant’s Guild");
    const hiddenGuildWidth = (await merchantGuildLink.boundingBox()).width;
    assert.ok(Number(await merchantGuildLink.evaluate((node) => getComputedStyle(node).opacity)) < 0.5);
    await merchantGuildLink.hover();
    await desktop.waitForTimeout(200);
    const revealedGuildWidth = (await merchantGuildLink.boundingBox()).width;
    assert.ok(revealedGuildWidth > hiddenGuildWidth + 40, "Merchant’s Guild label should reveal on hover");

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
    assert.match(await desktop.locator("a.ah-search-result-primary").first().getAttribute("href"), /^\.\/guides\//);
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
    assert.equal(await desktop.locator(".ah-search-quick-links .library-hub-chip").count(), 5);
    const expectedUniqueItems = await desktop.evaluate(() => window.AHSearchCore.uniqueItemCount(window.AH_SEARCH_INDEX.items));
    assert.equal(await desktop.locator("#ah-search-count").textContent(), `${expectedUniqueItems.toLocaleString()} unique items across 16 guides`);

    await desktop.locator("#ah-search-input").fill("Sanguine Hibiscus");
    await desktop.waitForSelector(".ah-search-result");
    assert.match(await desktop.locator(".ah-search-item-name").first().textContent(), /Sanguine Hibiscus/);
    assert.deepEqual(await desktop.locator(".ah-search-result").first().locator(".ah-search-target-label").allTextContents(), ["Target Bid", "Buyout"]);
    assert.match(await desktop.locator("a.ah-search-result-primary").first().getAttribute("href"), /^\.\/guides\//);

    await desktop.locator("#ah-search-input").fill("saronite");
    const saroniteCards = desktop.locator(".ah-search-result");
    assert.equal(await saroniteCards.count(), 12);
    const saroniteNames = await desktop.locator(".ah-search-item-name").allTextContents();
    assert.equal(new Set(saroniteNames).size, 12);
    const saroniteBar = desktop.locator(".ah-search-result", {
      has: desktop.locator(".ah-search-item-name", { hasText: /^Saronite Bar$/ })
    });
    assert.equal(await saroniteBar.count(), 1);
    assert.match(await saroniteBar.locator(".ah-search-result-meta").textContent(), /4 entries across 3 guides/);
    assert.equal(await saroniteBar.locator(".ah-search-location-link").count(), 3);
    await desktop.locator("#ah-search-input").press("ArrowDown");
    assert.equal(await saroniteBar.evaluate((card) => card.classList.contains("is-active")), true);
    await desktop.locator("#ah-search-input").press("ArrowDown");
    assert.equal(await saroniteCards.nth(1).evaluate((card) => card.classList.contains("is-active")), true);

    await desktop.locator("#ah-search-input").fill("Autumn's Glow");
    const autumnsGlow = desktop.locator(".ah-search-result", {
      has: desktop.locator(".ah-search-item-name", { hasText: /^Autumn's Glow$/ })
    });
    assert.equal(await autumnsGlow.count(), 1);
    assert.deepEqual(await autumnsGlow.locator(".ah-search-target-value").allTextContents(), ["8g 50s", "10g"]);
    assert.equal(await autumnsGlow.locator(".ah-search-location-link").count(), 2);
    assert.equal(await autumnsGlow.locator(".ah-search-location-meta").count(), 2);
    await noOverflow(desktop, "Desktop Auction House hub");

    await desktop.locator("#ah-search-input").fill("Scroll of Enchant Weapon - Berserking");
    const berserkingScroll = desktop.locator(".ah-search-result", {
      has: desktop.locator(".ah-search-item-name", { hasText: /^Scroll of Enchant Weapon - Berserking$/ })
    });
    assert.equal(await berserkingScroll.count(), 1);
    assert.match(
      await berserkingScroll.locator("a.ah-search-result-primary").getAttribute("href"),
      /enchanting-mats-ah-price-guide\.html/
    );

    await desktop.goto(`${base}/guides/enchanting-mats-ah-price-guide.html`, { waitUntil: "networkidle" });
    assert.equal(await desktop.locator('[data-crafted-key^="ench-"]').count(), 276);
    assert.equal(await desktop.locator(".crafted-market-section").count(), 25);
    assert.equal(await desktop.locator("#crafted-enchanting-pricing-note").count(), 1);
    assert.equal(await desktop.locator(".crafted-note-ref").count(), 276);
    assert.equal(await desktop.locator(".crafted-item-note").count(), 276);
    assert.equal(await desktop.locator(".crafted-recipe-link").count(), 276);
    const berserkingGuideRow = desktop.locator('[data-crafted-key="ench-scroll-of-enchant-weapon-berserking"]');
    assert.equal(await berserkingGuideRow.locator('[data-column="target"] .buyout').textContent(), "510g");
    assert.match(await berserkingGuideRow.locator(".crafted-item-note").textContent(), /Premium raid melee-DPS staple/);
    const berserkingRecipeLink = berserkingGuideRow.locator(".crafted-recipe-link");
    assert.equal(await berserkingRecipeLink.textContent(), "Recipe & mats ↗");
    assert.equal(await berserkingRecipeLink.getAttribute("href"), "https://www.wowhead.com/wotlk/spell=59621");
    assert.equal(await berserkingRecipeLink.getAttribute("data-wowhead"), "spell=59621&domain=wotlk");
    assert.equal(await berserkingRecipeLink.getAttribute("target"), "_blank");
    assert.equal(await berserkingRecipeLink.getAttribute("rel"), "noopener");
    const tuskarrGuideRow = desktop.locator('[data-crafted-key="ench-scroll-of-enchant-boots-tuskarrs-vitality"]');
    assert.match(await tuskarrGuideRow.locator(".crafted-item-note").textContent(), /Raid movement-speed staple/);
    const legacyOilGuideRow = desktop.locator('[data-crafted-key="ench-superior-wizard-oil"]');
    assert.match(await legacyOilGuideRow.locator(".crafted-item-note").textContent(), /not for Wrath raid gear/);
    const rarityColors = await desktop.evaluate(() => ["common", "uncommon", "rare", "epic"].map((quality) => {
      const itemName = document.querySelector(`strong.q-${quality}`);
      return itemName ? getComputedStyle(itemName).color : "";
    }));
    assert.equal(rarityColors.every(Boolean), true, "Enchanting guide should render all four item rarities");
    assert.equal(new Set(rarityColors).size, 4, "Each item rarity should have a distinct name color");
    assert.match(await desktop.locator("footer").textContent(), /Updated 2026-08-02/);
    await noOverflow(desktop, "Desktop Enchanting guide");

    await verifyAuditedCraftedGuide(desktop, {
      filename: "inscription-materials-ah-price-guide.html",
      rows: 107,
      sections: 18,
      key: "chaos-deck",
      target: "1,025g",
      recipeSpell: 60265,
      notePattern: /price it separately from Nobles/,
      label: "Desktop Inscription guide"
    });
    await verifyAuditedCraftedGuide(desktop, {
      filename: "engineering-materials-ah-price-guide.html",
      rows: 55,
      sections: 8,
      key: "eng-khorium-power-core",
      target: "52g",
      recipeSpell: 30308,
      notePattern: /used in high-end devices/,
      label: "Desktop Engineering guide"
    });
    await verifyAuditedCraftedGuide(desktop, {
      filename: "alchemy-materials-ah-price-guide.html",
      rows: 206,
      sections: 21,
      key: "alch-cardinal-ruby",
      target: "120g",
      recipeSpell: 66659,
      notePattern: /Uncut red epic gem/,
      label: "Desktop Alchemy guide"
    });
    await verifyAuditedCraftedGuide(desktop, {
      filename: "blacksmithing-materials-ah-price-guide.html",
      rows: 453,
      sections: 18,
      key: "bs-eternal-belt-buckle",
      target: "35g",
      recipeSpell: 55656,
      notePattern: /one permanent socket/,
      label: "Desktop Blacksmithing guide"
    });

    await desktop.goto(`${base}/guides/engineering-materials-ah-price-guide.html`, { waitUntil: "networkidle" });
    assert.equal(await desktop.locator("#general-use-engineering-utility").count(), 1);
    assert.equal(await desktop.locator("#engineer-only-tools").count(), 1);
    assert.equal(await desktop.locator("#engineer-only-mount-components").count(), 1);
    assert.match(
      await desktop.locator('[data-crafted-key="eng-gnomish-army-knife"] [data-column="notes"]').textContent(),
      /No profession required/
    );
    assert.match(
      await desktop.locator('[data-vendor-key="goblin-machined-piston"] [data-column="notes"]').textContent(),
      /Requires Engineering 450 to use/
    );
    await noOverflow(desktop, "Desktop profession-separated Engineering guide");

    await desktop.goto(`${base}/guides/fishing-cooking-materials-ah-price-guide.html`, { waitUntil: "networkidle" });
    assert.equal(await desktop.locator("#cook-required-feasts").count(), 1);
    assert.equal(await desktop.locator("#cook-required-feasts tbody tr").count(), 3);
    assert.match(await desktop.locator("#cook-required-feasts").textContent(), /Requires Cooking 425 to place/);
    await noOverflow(desktop, "Desktop profession-separated Cooking guide");

    await desktop.goto(`${base}/guides/jewelcrafting-gems-ah-price-guide.html`, { waitUntil: "networkidle" });
    assert.equal(await desktop.locator("#jewelcrafter-only-dragons-eye").count(), 1);
    assert.match(await desktop.locator("#jewelcrafter-only-dragons-eye").textContent(), /Requires Jewelcrafting 350 to use/);
    await noOverflow(desktop, "Desktop profession-separated Jewelcrafting guide");

    const mobile = await browser.newPage({ viewport: { width: 390, height: 844 }, isMobile: true });
    await mobile.goto(`${base}/index.html`, { waitUntil: "networkidle" });
    await mobile.waitForSelector(".ah-hub-browse");
    const mobileSearchRows = mobile.locator(".library-hub-search-row");
    assert.equal(await mobileSearchRows.count(), 2);
    for (let index = 0; index < 2; index += 1) {
      assert.equal(await mobileSearchRows.nth(index).evaluate((node) => getComputedStyle(node).gridTemplateColumns.split(" ").length), 1);
    }
    const mobileGuildLink = mobile.locator(".library-hub-secret-link");
    assert.equal(await mobileGuildLink.isVisible(), true);
    assert.ok((await mobileGuildLink.boundingBox()).width <= 34, "Merchant’s Guild link should remain discreet on mobile");
    await noOverflow(mobile, "Mobile main hub");

    await mobile.goto(`${base}/auction-house.html`, { waitUntil: "networkidle" });
    assert.equal(await mobile.locator(".guide-card.has-guide-icon").count(), 16);
    await mobile.locator("#ah-search-input").fill("saronite");
    assert.equal(await mobile.locator(".ah-search-result").count(), 12);
    await noOverflow(mobile, "Mobile Auction House hub");

    await mobile.goto(`${base}/guides/enchanting-mats-ah-price-guide.html`, { waitUntil: "networkidle" });
    assert.equal(await mobile.locator('[data-crafted-key^="ench-"]').count(), 276);
    assert.equal(await mobile.locator(".crafted-market-section").count(), 25);
    assert.equal(await mobile.locator("#crafted-enchanting-pricing-note").count(), 1);
    assert.equal(await mobile.locator(".crafted-note-ref").count(), 276);
    assert.equal(await mobile.locator(".crafted-item-note").count(), 276);
    assert.equal(await mobile.locator(".crafted-recipe-link").count(), 276);
    await noOverflow(mobile, "Mobile Enchanting guide");

    await verifyAuditedCraftedGuide(mobile, {
      filename: "inscription-materials-ah-price-guide.html",
      rows: 107,
      sections: 18,
      key: "chaos-deck",
      target: "1,025g",
      recipeSpell: 60265,
      notePattern: /price it separately from Nobles/,
      label: "Mobile Inscription guide"
    });
    await verifyAuditedCraftedGuide(mobile, {
      filename: "engineering-materials-ah-price-guide.html",
      rows: 55,
      sections: 8,
      key: "eng-khorium-power-core",
      target: "52g",
      recipeSpell: 30308,
      notePattern: /used in high-end devices/,
      label: "Mobile Engineering guide"
    });
    await verifyAuditedCraftedGuide(mobile, {
      filename: "alchemy-materials-ah-price-guide.html",
      rows: 206,
      sections: 21,
      key: "alch-cardinal-ruby",
      target: "120g",
      recipeSpell: 66659,
      notePattern: /Uncut red epic gem/,
      label: "Mobile Alchemy guide"
    });
    await verifyAuditedCraftedGuide(mobile, {
      filename: "blacksmithing-materials-ah-price-guide.html",
      rows: 453,
      sections: 18,
      key: "bs-eternal-belt-buckle",
      target: "35g",
      recipeSpell: 55656,
      notePattern: /one permanent socket/,
      label: "Mobile Blacksmithing guide"
    });

    console.log("Auction House hub and all five crafted guides passed desktop/mobile smoke tests.");
  } finally {
    await browser.close();
  }
})().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
