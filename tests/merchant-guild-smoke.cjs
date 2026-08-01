"use strict";

const { chromium } = require("playwright");
const assert = require("node:assert/strict");

const base = process.env.MERCHANT_GUILD_TEST_BASE || "http://127.0.0.1:4173";

async function noOverflow(page, label) {
  const overflow = await page.evaluate(() => document.documentElement.scrollWidth - document.documentElement.clientWidth);
  assert.ok(overflow <= 1, `${label} has ${overflow}px horizontal overflow`);
}

(async () => {
  const browser = await chromium.launch({ headless: true });
  try {
    const desktopContext = await browser.newContext({
      viewport: { width: 1280, height: 900 },
      permissions: ["clipboard-read", "clipboard-write"]
    });
    const desktop = await desktopContext.newPage();
    const pageErrors = [];
    desktop.on("pageerror", (error) => pageErrors.push(error.message));
    await desktop.goto(`${base}/guides/merchants-guild.html`, { waitUntil: "networkidle" });
    await desktop.waitForSelector(".copy-btn");

    assert.equal(await desktop.locator("h1").textContent(), "The Merchant’s Guild");
    assert.equal(await desktop.locator(".copy-btn").count(), 34);
    assert.equal(await desktop.locator(".merchant-jump-nav a").count(), 8);
    assert.equal(await desktop.locator(".merchant-emblem").evaluate((image) => image.complete && image.naturalWidth === 64 && image.naturalHeight === 64), true);

    const desktopCopyButtons = desktop.locator("[data-copy-target]");
    for (let index = 0; index < await desktopCopyButtons.count(); index += 1) {
      const button = desktopCopyButtons.nth(index);
      const targetId = await button.getAttribute("data-copy-target");
      await button.click();
      await desktop.waitForFunction(
        (id) => document.querySelector(`[data-copy-target="${id}"]`).classList.contains("is-copied"),
        targetId
      );
      assert.equal(await button.textContent(), "Copied", `${targetId}: button feedback is missing`);
      assert.equal(await button.locator("xpath=ancestor::article[1]").locator(".copy-status").textContent(), "Copied.", `${targetId}: live feedback is missing`);
      assert.equal(
        (await desktop.evaluate(() => navigator.clipboard.readText())).replace(/\r\n/g, "\n"),
        (await desktop.locator(`#${targetId}`).textContent()).replace(/\r\n/g, "\n"),
        `${targetId}: clipboard text differs from its visible copy block`
      );
    }

    const keyboardCopy = desktop.locator('[data-copy-target="chat-one-line"]');
    await desktop.evaluate(() => navigator.clipboard.writeText(""));
    await keyboardCopy.focus();
    await desktop.keyboard.press("Enter");
    await desktop.waitForFunction(
      (expected) => navigator.clipboard.readText().then((actual) => actual.replace(/\r\n/g, "\n") === expected.replace(/\r\n/g, "\n")),
      await desktop.locator("#chat-one-line").textContent()
    );
    assert.equal(await keyboardCopy.textContent(), "Copied");
    assert.equal(
      (await desktop.evaluate(() => navigator.clipboard.readText())).replace(/\r\n/g, "\n"),
      (await desktop.locator("#chat-one-line").textContent()).replace(/\r\n/g, "\n")
    );

    const macroChecks = await desktop.locator("[data-macro]").evaluateAll((nodes) => nodes.map((node) => {
      const counter = document.querySelector(`[data-char-count-for="${node.id}"]`);
      return { id: node.id, count: node.textContent.length, displayed: Number(counter.textContent) };
    }));
    assert.equal(macroChecks.length, 5);
    for (const macro of macroChecks) {
      assert.ok(macro.count <= 255, `${macro.id} exceeds the client limit`);
      assert.equal(macro.displayed, macro.count, `${macro.id} rendered the wrong count`);
    }
    await noOverflow(desktop, "Desktop Merchant’s Guild page");
    assert.deepEqual(pageErrors, []);
    await desktopContext.close();

    const mobileContext = await browser.newContext({
      viewport: { width: 390, height: 844 },
      isMobile: true,
      hasTouch: true,
      permissions: ["clipboard-read", "clipboard-write"]
    });
    const mobile = await mobileContext.newPage();
    await mobile.goto(`${base}/guides/merchants-guild.html`, { waitUntil: "networkidle" });
    await mobile.waitForSelector(".copy-btn");
    assert.equal(await mobile.locator(".copy-grid").first().evaluate((node) => getComputedStyle(node).gridTemplateColumns.split(" ").length), 1);
    assert.equal(await mobile.locator(".copy-btn").first().evaluate((node) => Math.round(node.getBoundingClientRect().height) >= 44), true);
    await mobile.locator('[data-copy-target="donation-unpaid"]').tap();
    await mobile.waitForFunction(() => document.querySelector('[data-copy-target="donation-unpaid"]').textContent === "Copied");
    assert.equal(await mobile.locator('[data-copy-target="donation-unpaid"]').textContent(), "Copied");
    await noOverflow(mobile, "Mobile Merchant’s Guild page");
    await mobileContext.close();

    const noScriptContext = await browser.newContext({ javaScriptEnabled: false, viewport: { width: 390, height: 844 } });
    const noScript = await noScriptContext.newPage();
    await noScript.goto(`${base}/guides/merchants-guild.html`, { waitUntil: "networkidle" });
    const selectableText = noScript.locator("#discord-short");
    assert.equal(await selectableText.isVisible(), true);
    assert.equal(await selectableText.evaluate((node) => getComputedStyle(node).userSelect), "text");
    assert.match(await selectableText.textContent(), /The Merchant’s Guild is recruiting/);
    await noScriptContext.close();

    console.log("Merchant’s Guild smoke tests passed at desktop and mobile widths, including all 34 Copy buttons and the no-JavaScript fallback.");
  } finally {
    await browser.close();
  }
})().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
