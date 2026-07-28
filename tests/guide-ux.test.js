const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const { JSDOM } = require("jsdom");

const root = path.resolve(__dirname, "..");
const script = fs.readFileSync(path.join(root, "assets", "guide-ux.js"), "utf8");

function render(body, bodyAttributes = "") {
  const dom = new JSDOM(`<!doctype html><html><body ${bodyAttributes}>${body}</body></html>`, {
    runScripts: "outside-only",
    url: "https://example.invalid/guides/test.html",
    pretendToBeVisual: true
  });
  dom.window.eval(script);
  dom.window.document.dispatchEvent(new dom.window.Event("DOMContentLoaded", { bubbles: true }));
  return dom;
}

{
  const dom = render(`
    <nav class="site-nav">
      <a class="guide-hub-link" href="../index.html">Guide Hub</a>
      <a href="quick.html">Quick Start</a>
      <a href="playing.html" aria-current="page">Playing</a>
      <a href="setup.html">Setup</a>
    </nav>
    <main><div class="table-wrap"><table><tr><td>Cell</td></tr></table></div></main>
  `, 'data-guide-class="paladin" data-guide-spec="holy"');
  const table = dom.window.document.querySelector(".table-wrap");
  assert.equal(table.getAttribute("role"), "region");
  assert.equal(table.getAttribute("tabindex"), "0");
  assert.equal(table.dataset.mobileScrollHint, "true");
  const pagerLinks = [...dom.window.document.querySelectorAll(".page-pager a")];
  assert.deepEqual(pagerLinks.map((link) => link.textContent), ["← Quick Start", "Setup →"]);
  dom.window.close();
}

{
  const dom = render(`
    <main>
      <div class="guide-box">
        <div class="talent-embed-wrap"><iframe class="talent-embed"></iframe></div>
        <p class="talent-fallback"><a href="https://example.invalid/build">Open build</a></p>
      </div>
    </main>
  `);
  const details = dom.window.document.querySelector(".talent-tree-details");
  assert.ok(details);
  assert.equal(details.open, false);
  assert.ok(details.querySelector(".talent-embed-wrap"));
  assert.ok(dom.window.document.querySelector(".talent-tree-primary-link a"));
  dom.window.close();
}

{
  const dom = render(`
    <main>
      <div class="raid-encounter-grid">
        <article class="raid-encounter">
          <h3>Lord Marrowgar</h3>
          <div class="raid-note">Switch to spikes.</div>
        </article>
      </div>
    </main>
  `, 'data-guide-class="hunter"');
  const button = dom.window.document.querySelector(".raid-encounter-toggle");
  const body = dom.window.document.querySelector(".raid-encounter-body");
  assert.ok(button);
  assert.equal(body.hidden, true);
  button.click();
  assert.equal(button.getAttribute("aria-expanded"), "true");
  assert.equal(body.hidden, false);
  dom.window.document.querySelector(".raid-accordion-actions button:last-child").click();
  assert.equal(body.hidden, true);
  dom.window.close();
}

console.log("Validated shared guide UX enhancements.");
