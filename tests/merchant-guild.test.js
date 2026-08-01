"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const { JSDOM } = require("jsdom");

const root = path.resolve(__dirname, "..");
const pagePath = path.join(root, "guides", "merchants-guild.html");
const html = fs.readFileSync(pagePath, "utf8");
const document = new JSDOM(html).window.document;

assert.equal(document.documentElement.lang, "en");
assert.equal(document.title, "The Merchant’s Guild | Hellscream Community AH Project");
assert.match(document.querySelector('meta[name="description"]')?.content || "", /copy-ready recruitment posts/i);
assert.equal(document.querySelector("h1")?.textContent.trim(), "The Merchant’s Guild");
assert.match(document.querySelector(".wrap > footer")?.textContent || "", /Updated 2026-07-31$/);

const emblem = document.querySelector(".merchant-emblem");
assert.equal(emblem?.getAttribute("src"), "../assets/merchant-guild-emblem.png");
assert.equal(emblem?.getAttribute("width"), "64");
assert.equal(emblem?.getAttribute("height"), "64");
const emblemBytes = fs.readFileSync(path.join(root, "assets", "merchant-guild-emblem.png"));
assert.equal(emblemBytes.subarray(1, 4).toString("ascii"), "PNG");
assert.equal(emblemBytes.readUInt32BE(16), 64);
assert.equal(emblemBytes.readUInt32BE(20), 64);

const jumpLinks = [...document.querySelectorAll('.merchant-jump-nav a[href^="#"]')];
assert.equal(jumpLinks.length, 8);
for (const link of jumpLinks) {
  assert.ok(document.getElementById(link.getAttribute("href").slice(1)), `Missing jump target ${link.getAttribute("href")}`);
}

const copyButtons = [...document.querySelectorAll("[data-copy-target]")];
const copyTexts = [...document.querySelectorAll(".copy-text")];
assert.equal(copyButtons.length, 34, "Every post, reply, and macro needs one Copy button");
assert.equal(copyTexts.length, copyButtons.length, "Copy target and button counts differ");
assert.equal(new Set(copyTexts.map((node) => node.id)).size, copyTexts.length, "Copy target IDs must be unique");
for (const button of copyButtons) {
  const targetId = button.getAttribute("data-copy-target");
  const target = document.getElementById(targetId);
  assert.ok(target, `Missing Copy target #${targetId}`);
  assert.equal(button.getAttribute("aria-controls"), targetId, `${targetId}: Copy control is not associated with its text`);
  assert.ok(button.closest(".copy-card")?.querySelector('.copy-status[role="status"][aria-live="polite"]'), `${targetId}: live Copy feedback is missing`);
}

const macros = [...document.querySelectorAll("[data-macro]")];
assert.equal(macros.length, 5);
for (const macro of macros) {
  const count = macro.textContent.length;
  const counter = document.querySelector(`[data-char-count-for="${macro.id}"]`);
  assert.ok(count <= 255, `${macro.id} exceeds the 255-character macro limit (${count})`);
  assert.equal(Number(counter?.textContent), count, `${macro.id} displays the wrong character count`);
  assert.equal(Buffer.byteLength(macro.textContent, "utf8"), count, `${macro.id} should remain ASCII for unambiguous 3.3.5a counting`);
}

for (const message of document.querySelectorAll("[data-chat-limit]")) {
  assert.ok(message.textContent.length <= 255, `${message.id} exceeds its 255-character chat limit`);
  assert.ok(Buffer.byteLength(message.textContent, "utf8") <= 255, `${message.id} exceeds 255 UTF-8 bytes`);
}

const visibleText = document.body.textContent.replace(/\s+/g, " ");
for (const required of [
  /barely 800 auctions/i,
  /more than 5,000/i,
  /Donations are currently unpaid/,
  /vendor value plus 10%/i,
  /Zalania is the guild leader/,
  /Valdora supports the project and can answer general questions but is not a member/,
  /#garrosh-player-guides/,
  /No public roster connects bank alts or auction alts to mains/
]) {
  assert.match(visibleText, required);
}

const approvedShort = document.getElementById("discord-short")?.textContent || "";
assert.equal(
  approvedShort,
  "The Merchant’s Guild is recruiting bank alts and auction alts. The AH has grown from about 800 listings to over 5,000, and they’re trying to keep it going.\n\nThey also accept donated items that would otherwise be vendored and will post them on the AH. Privacy is respected.\n\nMessage Zalania for invites or donations. Message Valdora with questions."
);

const donationCopy = [...document.querySelectorAll("#donations .copy-text")].map((node) => node.textContent).join("\n");
assert.doesNotMatch(donationCopy, /Valdora/i, "Donation instructions must not route players to Valdora");
for (const target of copyTexts) {
  const text = target.textContent;
  assert.doesNotMatch(text, /mail (?:items|donations?) to Valdora/i, `${target.id}: donations were routed to Valdora`);
  assert.doesNotMatch(text, /message Valdora for (?:an? )?(?:invite|invitation|donation)/i, `${target.id}: Valdora was given the wrong role`);
  assert.doesNotMatch(text, /\b(?:we|our|I)\b/, `${target.id}: unintended first-person wording found`);
}

for (const href of [...document.querySelectorAll("a[href]")].map((link) => link.getAttribute("href"))) {
  if (href.startsWith("#")) continue;
  if (/^(?:https?:|mailto:)/.test(href)) continue;
  const localTarget = href.split(/[?#]/)[0];
  assert.ok(fs.existsSync(path.resolve(path.dirname(pagePath), localTarget)), `Broken internal link: ${href}`);
}

const scripts = [...document.querySelectorAll("script[src]")].map((script) => script.getAttribute("src"));
assert.deepEqual(scripts, ["../assets/merchant-guild.js?v=20260731-merchants-guild-v1"]);
for (const asset of ["assets/merchant-guild.css", "assets/merchant-guild.js", "assets/merchant-guild-emblem-source.md"]) {
  assert.ok(fs.existsSync(path.join(root, asset)), `${asset} is missing`);
}

for (const hub of ["index.html", "auction-house.html"]) {
  const hubDocument = new JSDOM(fs.readFileSync(path.join(root, hub), "utf8")).window.document;
  assert.equal(hubDocument.querySelectorAll('a[href="./guides/merchants-guild.html"]').length, 1, `${hub}: Merchant’s Guild navigation link is missing`);
}

console.log(`Merchant’s Guild page: ${copyTexts.length} copy blocks and ${macros.length} macros passed static validation.`);
