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
  assert.match(await page.locator(".crafted-market-intro").textContent(), /exact 3\.3\.5 (?:recipe|reagent)/);
  assert.equal(await page.locator(".crafted-market-shared-note").count(), 1);
  assert.equal(await page.locator(".ah-crafted-market .crafted-note-ref").count(), rows);
  assert.equal(await page.locator(".ah-crafted-market .crafted-item-note").count(), rows);
  assert.equal(await page.locator(".ah-crafted-market .crafted-recipe-link").count(), rows);
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
  assert.match(await page.locator("footer").textContent(), /Updated 2026-08-04/);
  await noOverflow(page, label);
}

async function verifyGuideNavigation(page) {
  await page.goto(`${base}/guides/alchemy-materials-ah-price-guide.html`, { waitUntil: "networkidle" });
  await page.waitForSelector("[data-ah-major-nav] .ah-category-chip");
  assert.equal(await page.locator(".ah-guide-hero").count(), 1);
  assert.equal(await page.locator(".ah-guide-page-icon").getAttribute("width"), "64");
  assert.equal(await page.locator("details.ah-guide-notes").getAttribute("open"), null);
  assert.equal(await page.locator("[data-ah-major-nav] .ah-category-chip").count(), 6);
  const heroBox = await page.locator(".ah-guide-hero").boundingBox();
  const searchBox = await page.locator(".ah-guide-search-section").boundingBox();
  const inputBox = await page.locator("#ah-search-input").boundingBox();
  const chipsBox = await page.locator("[data-ah-major-nav]").boundingBox();
  assert.ok(heroBox && searchBox && inputBox && chipsBox);
  assert.ok(heroBox.height <= 150, `Compact guide banner is ${heroBox.height}px tall`);
  assert.ok(heroBox.y + heroBox.height <= searchBox.y + 1, "Guide search must follow the banner");
  assert.ok(inputBox.y + inputBox.height <= chipsBox.y + 1, "Major-category chips must follow the search field");

  const potions = page.locator('[data-ah-major-nav] .ah-category-chip', { hasText: /^Potions & Cauldrons$/ });
  const potionsTarget = (await potions.getAttribute("href")).slice(1);
  assert.ok(await page.locator(`#${potionsTarget}`).count());
  assert.ok(await page.locator(`#${potionsTarget} .ah-category-chip`).count() >= 2);

  await page.locator("#ah-search-input").fill("Saronite Bar");
  await page.waitForSelector(".ah-search-result");
  const guideSaroniteBar = page.locator(".ah-search-result", {
    has: page.locator(".ah-search-item-name", { hasText: /^Saronite Bar$/ }),
  });
  assert.match(
    await guideSaroniteBar.locator("a.ah-search-location-link").first().getAttribute("href"),
    /^\.\.\/guides\//,
    "Guide-level search results must resolve from the guides directory",
  );

  await page.goto(`${base}/guides/jewelcrafting-gems-ah-price-guide.html`, { waitUntil: "networkidle" });
  await page.waitForSelector("#jewelcrafting-wrath-cuts .ah-category-chip");
  assert.equal(await page.locator("#jewelcrafting-wrath-cuts > .ah-category-chip-nav .ah-category-chip").count(), 4);
  const epicTarget = (
    await page.locator('#jewelcrafting-wrath-cuts .ah-category-chip', { hasText: /^Epic$/ }).getAttribute("href")
  ).slice(1);
  assert.ok(await page.locator(`#${epicTarget} .ah-category-chip`).count() >= 6);
  const firstEpicLeaf = page.locator(`#${epicTarget} .ah-category-chip`).first();
  const firstEpicLeafTarget = (await firstEpicLeaf.getAttribute("href")).slice(1);
  assert.equal(await page.locator(`#${firstEpicLeafTarget} .ah-back-to-parent`).count(), 1);

  await page.goto(`${base}/guides/utility-recipe-drops-ah-price-guide.html`, { waitUntil: "networkidle" });
  await page.waitForURL(/gear-pattern-drops-ah-price-guide\.html#ah-category=recipe-utility$/);
  await page.goto(`${base}/guides/consumable-misc-recipe-drops-ah-price-guide.html#ah-item=book-of-glyph-mastery`, { waitUntil: "networkidle" });
  await page.waitForURL(/gear-pattern-drops-ah-price-guide\.html#ah-item=book-of-glyph-mastery$/);
}

async function verifyDroppedGearGuides(page, labelPrefix) {
  await page.goto(`${base}/guides/level-80-boe-epics-ah-price-guide.html`, { waitUntil: "networkidle" });
  await page.waitForSelector("[data-ah-major-nav] .ah-category-chip");
  assert.equal(await page.locator('[data-market-source="dropped"]').count(), 85);
  assert.equal(await page.locator("[data-ah-major-nav] .ah-category-chip").count(), 3);
  assert.equal(await page.locator("#boe80-armor > .ah-category-chip-nav .ah-category-chip").count(), 5);
  await page.locator("#ah-search-input").fill("Wodin's Lucky Necklace");
  const wodin = page.locator(".ah-search-result", {
    has: page.locator(".ah-search-item-name", { hasText: /^Wodin's Lucky Necklace$/ }),
  });
  assert.equal(await wodin.count(), 1);
  assert.deepEqual(await wodin.locator(".ah-search-target-value").allTextContents(), ["2,125g", "2,500g"]);
  const wodinRow = page.locator('[data-dropped-gear-key="wodins-lucky-necklace"]');
  assert.match(await wodinRow.locator(".mini").textContent(), /Epic · Req 80 · iLvl 264 · Neck/);
  assert.equal(await wodinRow.locator(".market-tag").textContent(), "Provisional fallback");
  assert.match(await wodinRow.locator('[data-column="notes"]').textContent(), /ICC-era iLvl 264 necklace/);
  assert.match(await wodinRow.locator('[data-column="notes"]').textContent(), /Sack of Frosty Treasures supply is episodic/);
  assert.match(await page.locator("footer").textContent(), /Updated 2026-08-05/);
  await noOverflow(page, `${labelPrefix} Level 80 BoE guide`);

  await page.goto(`${base}/guides/sought-after-world-drops-ah-price-guide.html`, { waitUntil: "networkidle" });
  await page.waitForSelector("[data-ah-major-nav] .ah-category-chip");
  assert.equal(await page.locator('[data-market-source="dropped"]').count(), 262);
  assert.equal(await page.locator("[data-ah-major-nav] .ah-category-chip").count(), 3);
  for (const category of ["world-classic", "world-outland", "world-northrend"]) {
    assert.equal(await page.locator(`#${category} > .ah-category-chip-nav .ah-category-chip`).count(), 3);
  }
  await page.locator("#ah-search-input").fill("Shadowfang");
  const shadowfang = page.locator(".ah-search-result", {
    has: page.locator(".ah-search-item-name", { hasText: /^Shadowfang$/ }),
  });
  assert.equal(await shadowfang.count(), 1);
  assert.deepEqual(await shadowfang.locator(".ah-search-target-value").allTextContents(), ["170g", "200g"]);
  const shadowfangRow = page.locator('[data-dropped-gear-key="shadowfang"]');
  assert.match(await shadowfangRow.locator(".mini").textContent(), /Rare · Req 19 · iLvl 24 · One-Hand/);
  assert.equal(await shadowfangRow.locator(".market-tag").textContent(), "Provisional fallback");
  assert.match(await shadowfangRow.locator('[data-column="notes"]').textContent(), /Fixed-stat level 19 one-handed weapon/);
  assert.match(await shadowfangRow.locator('[data-column="notes"]').textContent(), /Shadowfang Keep trash farming/);
  assert.match(await page.locator("footer").textContent(), /Updated 2026-08-05/);
  await noOverflow(page, `${labelPrefix} world-drop guide`);
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
    assert.equal(await desktop.locator(".guide-card.has-guide-icon").count(), 16, "Auction House hub should present eighteen guides across sixteen cards");
    assert.equal(await desktop.locator(".ah-hub-route-card").count(), 4);
    assert.equal(await desktop.locator(".ah-hub-link-card").count(), 1);
    const blacksmithingCard = desktop.locator('[data-ah-hub-card="blacksmithing"]');
    assert.equal(await blacksmithingCard.evaluate((node) => node.tagName), "ARTICLE");
    assert.deepEqual(
      (await blacksmithingCard.locator(".ah-hub-card-chip").allTextContents()).map((label) => label.replace("→", "").trim()),
      ["Materials & Enhancements", "Armor & Weapons"],
    );
    const jewelcraftingCard = desktop.locator('[data-ah-hub-card="jewelcrafting"]');
    assert.deepEqual(
      (await jewelcraftingCard.locator(".ah-hub-card-chip").allTextContents()).map((label) => label.replace("→", "").trim()),
      ["Gems & Cuts", "Jewelry & Components"],
    );
    const boeDropsCard = desktop.locator('[data-ah-hub-card="boe-gear-drops"]');
    assert.deepEqual(
      (await boeDropsCard.locator(".ah-hub-card-chip").allTextContents()).map((label) => label.replace("→", "").trim()),
      ["Level 80 BoE Epics", "Sought-After World Drops"],
    );
    const skinningLinkCard = desktop.locator('[data-ah-hub-card="skinning-materials-link"]');
    const skinningMaterialsChip = skinningLinkCard.locator(".ah-hub-card-chip");
    assert.equal(await skinningMaterialsChip.getAttribute("href"), "./guides/skinning-leatherworking-materials-ah-price-guide.html#ah-category=leatherworking-materials");
    await skinningMaterialsChip.click();
    await desktop.waitForURL(/skinning-leatherworking-materials-ah-price-guide\.html#ah-category=leatherworking-materials$/);
    await desktop.waitForSelector("#leatherworking-materials");
    const skinningCategoryBox = await desktop.locator("#leatherworking-materials").boundingBox();
    assert.ok(skinningCategoryBox && skinningCategoryBox.y >= 0 && skinningCategoryBox.y < 160, "Skinning link card must scroll to its materials category");
    await desktop.goBack({ waitUntil: "networkidle" });
    await desktop.waitForSelector("#ah-search-input");
    assert.equal(await desktop.locator(".ah-search-quick-links .library-hub-chip").count(), 5);
    const expectedUniqueItems = await desktop.evaluate(() => window.AHSearchCore.uniqueItemCount(window.AH_SEARCH_INDEX.items));
    assert.equal(await desktop.locator("#ah-search-count").textContent(), `${expectedUniqueItems.toLocaleString()} unique items across 18 guides`);

    await desktop.locator("#ah-search-input").fill("Sanguine Hibiscus");
    await desktop.waitForSelector(".ah-search-result");
    assert.match(await desktop.locator(".ah-search-item-name").first().textContent(), /Sanguine Hibiscus/);
    assert.deepEqual(await desktop.locator(".ah-search-result").first().locator(".ah-search-target-label").allTextContents(), ["Target Bid", "Buyout"]);
    assert.equal(await desktop.locator(".ah-search-result").first().locator(".ah-search-stack-label").textContent(), "Stack");
    assert.equal(await desktop.locator(".ah-search-result").first().locator(".ah-search-stack-value").textContent(), "5 / 10 / 20");
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
    assert.equal(await saroniteBar.locator(".ah-search-stack-value").textContent(), "5 / 10 / 20");
    assert.match(await saroniteBar.locator(".ah-search-result-meta").textContent(), /Very High demand/);
    const saroniteMetaBox = await saroniteBar.locator(".ah-search-result-meta").boundingBox();
    const saroniteStackBox = await saroniteBar.locator(".ah-search-stack-summary").boundingBox();
    assert.ok(saroniteMetaBox && saroniteStackBox);
    assert.ok(Math.abs(saroniteMetaBox.y - saroniteStackBox.y) <= 2);
    assert.equal(await saroniteBar.locator(".ah-search-location-meta").count(), 0);
    await desktop.locator("#ah-search-input").press("ArrowDown");
    assert.equal(await saroniteBar.evaluate((card) => card.classList.contains("is-active")), true);
    await desktop.locator("#ah-search-input").press("ArrowDown");
    assert.equal(await saroniteCards.nth(1).evaluate((card) => card.classList.contains("is-active")), true);

    await desktop.locator("#ah-search-input").fill("truesilver bar");
    const truesilverBar = desktop.locator(".ah-search-result", {
      has: desktop.locator(".ah-search-item-name", { hasText: /^Truesilver Bar$/ })
    });
    assert.equal(await truesilverBar.count(), 1);
    assert.deepEqual(await truesilverBar.locator(".ah-search-target-value").allTextContents(), ["1g 49s", "1g 75s"]);
    assert.equal(await truesilverBar.locator(".ah-search-stack-value").textContent(), "1 / 5 / 10");
    assert.equal(await truesilverBar.getByText(/Varies/i).count(), 0);

    await desktop.locator("#ah-search-input").fill("Book of Glyph Mastery");
    const glyphBook = desktop.locator(".ah-search-result", {
      has: desktop.locator(".ah-search-item-name", { hasText: /^Book of Glyph Mastery$/ })
    });
    assert.equal(await glyphBook.count(), 1);
    assert.equal(await glyphBook.locator(".ah-search-stack-summary").count(), 0);

    await desktop.locator("#ah-search-input").fill("Autumn's Glow");
    const autumnsGlow = desktop.locator(".ah-search-result", {
      has: desktop.locator(".ah-search-item-name", { hasText: /^Autumn's Glow$/ })
    });
    assert.equal(await autumnsGlow.count(), 1);
    assert.deepEqual(await autumnsGlow.locator(".ah-search-target-value").allTextContents(), ["8g 50s", "10g"]);
    assert.equal(await autumnsGlow.locator(".ah-search-location-link").count(), 2);
    assert.equal(await autumnsGlow.locator(".ah-search-location-meta").count(), 0);

    await desktop.locator("#ah-search-input").fill("Heavy Borean Leather");
    const heavyBoreanLeather = desktop.locator(".ah-search-result", {
      has: desktop.locator(".ah-search-item-name", { hasText: /^Heavy Borean Leather$/ })
    });
    assert.equal(await heavyBoreanLeather.count(), 1);
    assert.equal(
      await heavyBoreanLeather.locator(".ah-search-conversion-hint").textContent(),
      "Conversion check: 6 Borean ≈4g 20s → target 6g 50s"
    );
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
    assert.match(await desktop.locator("footer").textContent(), /Updated 2026-08-04/);
    await noOverflow(desktop, "Desktop Enchanting guide");
    await verifyGuideNavigation(desktop);
    await verifyDroppedGearGuides(desktop, "Desktop");

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
      rows: 52,
      sections: 5,
      key: "bs-eternal-belt-buckle",
      target: "35g",
      recipeSpell: 55656,
      notePattern: /one permanent socket/,
      label: "Desktop Blacksmithing materials guide"
    });
    await verifyAuditedCraftedGuide(desktop, {
      filename: "blacksmithing-gear-ah-price-guide.html",
      rows: 401,
      sections: 13,
      key: "bs-puresteel-legplates",
      target: "7,650g",
      recipeSpell: 70562,
      notePattern: /ICC-era raid gearing/,
      label: "Desktop Blacksmithing gear guide"
    });
    await verifyAuditedCraftedGuide(desktop, {
      filename: "jewelcrafting-gems-ah-price-guide.html",
      rows: 360,
      sections: 38,
      key: "jc-delicate-cardinal-ruby",
      target: "150g",
      recipeSpell: 66448,
      notePattern: /\+20 Agility/,
      label: "Desktop Jewelcrafting gems guide"
    });
    await verifyAuditedCraftedGuide(desktop, {
      filename: "jewelcrafting-jewelry-ah-price-guide.html",
      rows: 137,
      sections: 7,
      key: "jc-bloodstone-band",
      target: "2g",
      recipeSpell: 56193,
      notePattern: /physical-DPS gearing/,
      label: "Desktop Jewelcrafting jewelry guide"
    });
    await verifyAuditedCraftedGuide(desktop, {
      filename: "tailoring-cloth-ah-price-guide.html",
      rows: 423,
      sections: 21,
      key: "firstaid-heavy-frostweave-bandage",
      target: "1g 10s",
      recipeSpell: 45546,
      notePattern: /Heals 5,800 damage/,
      label: "Desktop Tailoring + First Aid guide"
    });
    await verifyAuditedCraftedGuide(desktop, {
      filename: "skinning-leatherworking-materials-ah-price-guide.html",
      rows: 490,
      sections: 29,
      key: "lw-drums-of-battle",
      target: "31g",
      recipeSpell: 35543,
      notePattern: /Cannot affect targets level 80 or higher/,
      label: "Desktop Leatherworking guide"
    });
    await verifyAuditedCraftedGuide(desktop, {
      filename: "fishing-cooking-materials-ah-price-guide.html",
      rows: 162,
      sections: 13,
      key: "cook-fish-feast",
      target: "20g 50s",
      recipeSpell: 57423,
      notePattern: /80 Attack Power, 46 Spell Power and 40 Stamina/,
      label: "Desktop Cooking guide"
    });

    await desktop.goto(`${base}/guides/tailoring-cloth-ah-price-guide.html`, { waitUntil: "networkidle" });
    assert.equal(await desktop.locator("#tailor-only-nets").count(), 1);
    assert.equal(await desktop.locator("#tailor-only-nets tbody tr").count(), 3);
    assert.match(
      await desktop.locator('[data-crafted-key="tailor-frostweave-net"] [data-column="notes"]').textContent(),
      /Requires Tailoring 350 to use/
    );
    assert.equal(await desktop.locator("#first-aid-only-wrath-bandages").count(), 1);
    assert.equal(await desktop.locator("#first-aid-only-outland-bandages").count(), 1);
    assert.equal(await desktop.locator("#first-aid-only-classic-supplies").count(), 1);
    assert.equal(await desktop.locator("#general-use-anti-venoms").count(), 1);
    assert.match(
      await desktop.locator('[data-crafted-key="firstaid-heavy-frostweave-bandage"] [data-column="notes"]').textContent(),
      /Requires First Aid 400 to use/
    );
    assert.match(
      await desktop.locator('[data-crafted-key="firstaid-strong-anti-venom"] [data-column="notes"]').textContent(),
      /No profession required/
    );
    await noOverflow(desktop, "Desktop profession-separated Tailoring + First Aid guide");

    await desktop.goto(`${base}/guides/skinning-leatherworking-materials-ah-price-guide.html`, { waitUntil: "networkidle" });
    assert.equal(await desktop.locator("#leatherworker-only-drums").count(), 1);
    assert.equal(await desktop.locator("#leatherworker-only-drums tbody tr").count(), 5);
    assert.match(
      await desktop.locator('[data-crafted-key="lw-drums-of-battle"] [data-column="notes"]').textContent(),
      /Requires Leatherworking 350 to use/
    );
    assert.equal(await desktop.locator('[data-use-audience="profession-input"] tbody tr').count(), 6);
    assert.match(
      await desktop.locator('[data-crafted-key="lw-drums-of-forgotten-kings"] [data-column="notes"]').textContent(),
      /No profession required/
    );
    await noOverflow(desktop, "Desktop profession-separated Leatherworking guide");

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
    assert.equal(await desktop.locator("#cook-required-feasts tbody tr").count(), 4);
    assert.match(await desktop.locator("#cook-required-feasts").textContent(), /Requires Cooking 425 to place/);
    assert.equal(await desktop.locator("#rogue-only-utility tbody tr").count(), 1);
    assert.match(await desktop.locator("#rogue-only-utility").textContent(), /Rogue only/);
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
    assert.equal(await mobile.locator(".ah-hub-card-chip").count(), 7);
    await mobile.locator("#ah-search-input").fill("saronite");
    assert.equal(await mobile.locator(".ah-search-result").count(), 12);
    const mobileSaroniteBar = mobile.locator(".ah-search-result", {
      has: mobile.locator(".ah-search-item-name", { hasText: /^Saronite Bar$/ })
    });
    assert.equal(await mobileSaroniteBar.locator(".ah-search-stack-label").textContent(), "Stack");
    assert.equal(await mobileSaroniteBar.locator(".ah-search-stack-value").textContent(), "5 / 10 / 20");
    await mobile.locator("#ah-search-input").fill("Heavy Borean Leather");
    const mobileHeavyBoreanLeather = mobile.locator(".ah-search-result", {
      has: mobile.locator(".ah-search-item-name", { hasText: /^Heavy Borean Leather$/ })
    });
    assert.equal(await mobileHeavyBoreanLeather.count(), 1);
    assert.equal(
      await mobileHeavyBoreanLeather.locator(".ah-search-conversion-hint").textContent(),
      "Conversion check: 6 Borean ≈4g 20s → target 6g 50s"
    );
    await noOverflow(mobile, "Mobile Auction House hub");
    await verifyDroppedGearGuides(mobile, "Mobile");

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
      rows: 52,
      sections: 5,
      key: "bs-eternal-belt-buckle",
      target: "35g",
      recipeSpell: 55656,
      notePattern: /one permanent socket/,
      label: "Mobile Blacksmithing materials guide"
    });
    await verifyAuditedCraftedGuide(mobile, {
      filename: "blacksmithing-gear-ah-price-guide.html",
      rows: 401,
      sections: 13,
      key: "bs-puresteel-legplates",
      target: "7,650g",
      recipeSpell: 70562,
      notePattern: /ICC-era raid gearing/,
      label: "Mobile Blacksmithing gear guide"
    });
    await verifyAuditedCraftedGuide(mobile, {
      filename: "jewelcrafting-gems-ah-price-guide.html",
      rows: 360,
      sections: 38,
      key: "jc-delicate-cardinal-ruby",
      target: "150g",
      recipeSpell: 66448,
      notePattern: /\+20 Agility/,
      label: "Mobile Jewelcrafting gems guide"
    });
    await verifyAuditedCraftedGuide(mobile, {
      filename: "jewelcrafting-jewelry-ah-price-guide.html",
      rows: 137,
      sections: 7,
      key: "jc-bloodstone-band",
      target: "2g",
      recipeSpell: 56193,
      notePattern: /physical-DPS gearing/,
      label: "Mobile Jewelcrafting jewelry guide"
    });
    await verifyAuditedCraftedGuide(mobile, {
      filename: "tailoring-cloth-ah-price-guide.html",
      rows: 423,
      sections: 21,
      key: "firstaid-heavy-frostweave-bandage",
      target: "1g 10s",
      recipeSpell: 45546,
      notePattern: /Heals 5,800 damage/,
      label: "Mobile Tailoring + First Aid guide"
    });
    await verifyAuditedCraftedGuide(mobile, {
      filename: "skinning-leatherworking-materials-ah-price-guide.html",
      rows: 490,
      sections: 29,
      key: "lw-drums-of-battle",
      target: "31g",
      recipeSpell: 35543,
      notePattern: /Cannot affect targets level 80 or higher/,
      label: "Mobile Leatherworking guide"
    });
    await verifyAuditedCraftedGuide(mobile, {
      filename: "fishing-cooking-materials-ah-price-guide.html",
      rows: 162,
      sections: 13,
      key: "cook-fish-feast",
      target: "20g 50s",
      recipeSpell: 57423,
      notePattern: /80 Attack Power, 46 Spell Power and 40 Stamina/,
      label: "Mobile Cooking guide"
    });
    await verifyAuditedCraftedGuide(mobile, {
      filename: "mining-smithing-ah-price-guide.html",
      rows: 24,
      sections: 4,
      key: "mining-titansteel-bar",
      target: "84g",
      recipeSpell: 55208,
      notePattern: /Standard 3\.3\.5 data shows no cooldown/,
      label: "Mobile Mining guide"
    });

    console.log("Auction House hub, both dropped-gear guides, compact guide UX, nested category chips, redirects, and all twelve crafted guide views passed desktop/mobile smoke tests.");
  } finally {
    await browser.close();
  }
})().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
