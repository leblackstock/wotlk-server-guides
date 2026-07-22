(function (global) {
  "use strict";

  const scriptElement = document.currentScript || Array.from(document.scripts).find((script) => /\/ah-item-tooltips\.js(?:\?|$)/.test(script.src));
  const scriptUrl = scriptElement && scriptElement.src ? new URL(scriptElement.src) : null;
  const ITEM_SELECTOR = "table tbody tr td:first-child strong, .ah-search-item-name";
  const touchOnlyPointer = typeof global.matchMedia === "function" &&
    global.matchMedia("(hover: none)").matches &&
    global.matchMedia("(pointer: coarse)").matches;
  let activeMobileWowheadUrl = "";

  function normalize(value) {
    return String(value || "")
      .normalize("NFKD")
      .replace(/[\u0300-\u036f]/g, "")
      .toLowerCase()
      .replace(/[’']/g, "")
      .replace(/&/g, " and ")
      .replace(/[^a-z0-9]+/g, " ")
      .trim()
      .replace(/\s+/g, " ");
  }

  function loadScript(src, marker) {
    const existing = document.querySelector(`script[${marker}]`);
    if (existing) {
      return new Promise((resolve, reject) => {
        if (existing.dataset.loaded === "true") resolve(existing);
        else {
          existing.addEventListener("load", () => resolve(existing), { once: true });
          existing.addEventListener("error", reject, { once: true });
        }
      });
    }

    return new Promise((resolve, reject) => {
      const script = document.createElement("script");
      script.src = src;
      script.async = false;
      script.setAttribute(marker, "true");
      script.addEventListener("load", () => {
        script.dataset.loaded = "true";
        resolve(script);
      }, { once: true });
      script.addEventListener("error", reject, { once: true });
      document.head.appendChild(script);
    });
  }

  function ensureStyles() {
    if (document.getElementById("ah-item-tooltip-styles")) return;
    const style = document.createElement("style");
    style.id = "ah-item-tooltip-styles";
    style.textContent = `
      .ah-item-tooltip-label {
        text-decoration-line: underline;
        text-decoration-style: dotted;
        text-decoration-thickness: 1px;
        text-decoration-color: rgba(240, 193, 90, .64);
        text-underline-offset: 3px;
      }
      a.ah-item-tooltip,
      a.ah-item-tooltip:visited {
        color: inherit;
      }
      a.ah-item-tooltip:hover .ah-item-tooltip-label,
      a.ah-item-tooltip:focus-visible .ah-item-tooltip-label,
      a.ah-item-tooltip.ah-item-tooltip-label:hover,
      a.ah-item-tooltip.ah-item-tooltip-label:focus-visible {
        text-decoration-style: solid;
        text-decoration-color: var(--gold, #f0c15a);
      }
      @media (hover: none) and (pointer: coarse) {
        a.ah-item-tooltip {
          touch-action: manipulation;
        }
        .wowhead-tooltip-screen-inner-wrapper {
          bottom: 72px !important;
          overflow-x: hidden !important;
          overflow-y: auto !important;
          -webkit-overflow-scrolling: touch;
        }
        .wowhead-tooltip-screen-inner {
          box-sizing: border-box !important;
          display: flex !important;
          align-items: center !important;
          justify-content: flex-start !important;
          min-width: 0 !important;
          padding: 62px 12px 18px !important;
        }
        .wowhead-tooltip-screen-inner-box {
          box-sizing: border-box !important;
          margin: auto !important;
          max-width: 430px !important;
          min-width: 0 !important;
          width: 100% !important;
        }
        .wowhead-tooltip-screen-inner .wowhead-tooltip {
          box-sizing: border-box !important;
          margin: 0 auto !important;
          max-width: calc(100vw - 24px) !important;
          min-width: 0 !important;
          overflow: visible !important;
          position: static !important;
          width: 100% !important;
        }
        .wowhead-tooltip-screen-inner .wowhead-tooltip:not([data-visible="yes"]) {
          display: none !important;
        }
        .wowhead-tooltip-screen-inner .wowhead-tooltip[data-visible="yes"] {
          display: block !important;
        }
        .wowhead-tooltip-screen-inner .wowhead-tooltip > table {
          box-sizing: border-box !important;
          max-width: 100% !important;
          width: 100% !important;
        }
        .wowhead-tooltip-screen-inner .wowhead-tooltip table,
        .wowhead-tooltip-screen-inner .wowhead-tooltip tbody,
        .wowhead-tooltip-screen-inner .wowhead-tooltip tr,
        .wowhead-tooltip-screen-inner .wowhead-tooltip td,
        .wowhead-tooltip-screen-inner .wowhead-tooltip th {
          max-width: 100% !important;
          white-space: normal !important;
        }
        .wowhead-tooltip-screen-inner .wowhead-tooltip td,
        .wowhead-tooltip-screen-inner .wowhead-tooltip th,
        .wowhead-tooltip-screen-inner .wowhead-tooltip b,
        .wowhead-tooltip-screen-inner .wowhead-tooltip span,
        .wowhead-tooltip-screen-inner .wowhead-tooltip div {
          overflow-wrap: anywhere !important;
          white-space: normal !important;
          word-break: normal !important;
        }
        .wowhead-tooltip-screen-caption {
          bottom: max(7px, env(safe-area-inset-bottom)) !important;
          left: 9px !important;
          position: fixed !important;
          right: 9px !important;
        }
      }
    `;
    document.head.appendChild(style);
  }

  function addTooltipMetadata(link, itemId) {
    const wowheadUrl = `https://www.wowhead.com/wotlk/item=${itemId}`;
    link.dataset.ahWowheadUrl = wowheadUrl;
    link.setAttribute("data-wowhead", `item=${itemId}&domain=wotlk`);
  }

  function decorateNameNode(nameNode) {
    if (!(nameNode instanceof Element) || nameNode.dataset.ahTooltipDecorated === "true") return;
    const itemId = global.AH_ITEM_IDS && global.AH_ITEM_IDS[normalize(nameNode.textContent)];
    if (!itemId) return;

    const existingLink = nameNode.closest("a");
    if (existingLink) {
      existingLink.classList.add("ah-item-tooltip");
      addTooltipMetadata(existingLink, itemId);
      nameNode.classList.add("ah-item-tooltip-label");
    } else {
      const link = document.createElement("a");
      link.href = `https://www.wowhead.com/wotlk/item=${itemId}`;
      link.target = "_blank";
      link.rel = "noopener";
      link.className = "ah-item-tooltip ah-item-tooltip-label";
      addTooltipMetadata(link, itemId);
      while (nameNode.firstChild) link.appendChild(nameNode.firstChild);
      nameNode.appendChild(link);
    }
    nameNode.dataset.ahTooltipDecorated = "true";
  }

  function decorateWithin(root) {
    if (!(root instanceof Element || root instanceof Document)) return;
    if (root instanceof Element && root.matches(ITEM_SELECTOR)) decorateNameNode(root);
    root.querySelectorAll(ITEM_SELECTOR).forEach(decorateNameNode);
  }

  function observeNewResults() {
    const observer = new MutationObserver((mutations) => {
      mutations.forEach((mutation) => {
        mutation.addedNodes.forEach((node) => {
          if (node instanceof Element) decorateWithin(node);
        });
      });
    });
    observer.observe(document.body, { childList: true, subtree: true });
  }

  function enableMobileSecondTap() {
    if (!touchOnlyPointer) return;

    document.addEventListener("click", (event) => {
      const itemLink = event.target.closest && event.target.closest("a.ah-item-tooltip");
      if (itemLink && itemLink.dataset.ahWowheadUrl) {
        activeMobileWowheadUrl = itemLink.dataset.ahWowheadUrl;
        return;
      }

      const tooltipPanel = event.target.closest && event.target.closest(
        ".wowhead-tooltip-screen-inner-box .wowhead-tooltip[data-visible='yes']"
      );
      if (!tooltipPanel || !activeMobileWowheadUrl) return;
      if (event.target.closest(".wowhead-touch-tooltip-closer, a, button")) return;

      event.preventDefault();
      event.stopPropagation();
      global.location.assign(activeMobileWowheadUrl);
    }, true);
  }

  function loadWowheadTooltips() {
    if (document.querySelector('script[src*="wow.zamimg.com/js/tooltips.js"]')) return Promise.resolve();
    global.whTooltips = Object.assign({}, global.whTooltips, {
      colorLinks: false,
      iconizeLinks: false,
      renameLinks: false
    });
    return loadScript("https://wow.zamimg.com/js/tooltips.js", "data-ah-wowhead-script");
  }

  async function initialize() {
    if (!scriptUrl) return;
    try {
      await loadScript(new URL("ah-item-ids.js?v=20260722-ah-items-v1", scriptUrl).href, "data-ah-item-id-map");
      ensureStyles();
      decorateWithin(document);
      observeNewResults();
      enableMobileSecondTap();
      await loadWowheadTooltips();
    } catch (error) {
      console.warn("AH item tooltips could not be initialized.", error);
    }
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initialize, { once: true });
  } else {
    initialize();
  }
})(typeof window !== "undefined" ? window : globalThis);
