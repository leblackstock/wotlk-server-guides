(function (global) {
  "use strict";

  /* AH item tooltip loader */
  (function loadAhItemTooltips() {
    if (typeof document === "undefined" || document.querySelector("script[data-ah-item-tooltips]")) return;
    const current = document.currentScript || Array.from(document.scripts).find((script) => /\/ah-search\.js(?:\?|$)/.test(script.src));
    if (!current || !current.src) return;
    const tooltipScript = document.createElement("script");
    tooltipScript.src = new URL("ah-item-tooltips.js?v=20260804-ah-guide-ux-v1", current.src).href;
    tooltipScript.async = false;
    tooltipScript.dataset.ahItemTooltips = "true";
    document.head.appendChild(tooltipScript);
  }());

  const MAX_RESULTS = 12;

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

  function slugify(value) {
    return normalize(value).replace(/\s+/g, "-");
  }

  function editDistance(left, right) {
    if (left === right) return 0;
    if (!left.length) return right.length;
    if (!right.length) return left.length;

    let previous = Array.from({ length: right.length + 1 }, (_, index) => index);
    for (let leftIndex = 1; leftIndex <= left.length; leftIndex += 1) {
      const current = [leftIndex];
      for (let rightIndex = 1; rightIndex <= right.length; rightIndex += 1) {
        const substitution = previous[rightIndex - 1] + (left[leftIndex - 1] === right[rightIndex - 1] ? 0 : 1);
        current[rightIndex] = Math.min(
          previous[rightIndex] + 1,
          current[rightIndex - 1] + 1,
          substitution
        );
      }
      previous = current;
    }
    return previous[right.length];
  }

  function subsequencePenalty(needle, haystack) {
    let needleIndex = 0;
    let firstMatch = -1;
    let lastMatch = -1;
    for (let index = 0; index < haystack.length && needleIndex < needle.length; index += 1) {
      if (haystack[index] === needle[needleIndex]) {
        if (firstMatch < 0) firstMatch = index;
        lastMatch = index;
        needleIndex += 1;
      }
    }
    if (needleIndex !== needle.length) return Number.POSITIVE_INFINITY;
    return firstMatch + Math.max(0, lastMatch - firstMatch + 1 - needle.length);
  }

  function tokenScore(queryToken, candidateToken) {
    if (queryToken === candidateToken) return 0;
    if (candidateToken.startsWith(queryToken)) return 3 + (candidateToken.length - queryToken.length) * 0.08;
    if (candidateToken.includes(queryToken)) return 8 + candidateToken.indexOf(queryToken);

    const allowedDistance = queryToken.length <= 4 ? 1 : queryToken.length <= 8 ? 2 : 3;
    if (Math.abs(queryToken.length - candidateToken.length) <= allowedDistance) {
      const distance = editDistance(queryToken, candidateToken);
      if (distance <= allowedDistance) return 18 + distance * 6;
    }

    if (queryToken.length >= 4) {
      const penalty = subsequencePenalty(queryToken, candidateToken);
      if (Number.isFinite(penalty) && penalty <= Math.max(3, Math.floor(candidateToken.length / 3))) {
        return 34 + penalty;
      }
    }
    return Number.POSITIVE_INFINITY;
  }

  function scoreItem(item, rawQuery) {
    const query = normalize(rawQuery);
    const name = normalize(item.name);
    if (!query || !name) return Number.POSITIVE_INFINITY;
    if (name === query) return 0;
    if (name.startsWith(query)) return 2 + (name.length - query.length) * 0.02;
    if (name.includes(query)) return 7 + name.indexOf(query) * 0.15;

    const queryTokens = query.split(" ");
    const candidateTokens = name.split(" ");
    let score = 0;
    for (const queryToken of queryTokens) {
      let best = tokenScore(queryToken, name.replace(/\s/g, ""));
      for (const candidateToken of candidateTokens) {
        best = Math.min(best, tokenScore(queryToken, candidateToken));
      }
      if (!Number.isFinite(best)) return Number.POSITIVE_INFINITY;
      score += best;
    }
    return score + Math.max(0, candidateTokens.length - queryTokens.length) * 0.4;
  }

  function searchItems(items, query, limit = MAX_RESULTS) {
    if (normalize(query).length < 2) return [];
    const rankedItems = items
      .map((item) => ({ item, score: scoreItem(item, query) }))
      .filter((result) => Number.isFinite(result.score))
      .sort((left, right) =>
        left.score - right.score ||
        left.item.name.localeCompare(right.item.name) ||
        left.item.guide.localeCompare(right.item.guide)
      );

    const groupedItems = new Map();
    rankedItems.forEach(({ item }) => {
      const key = normalize(item.name);
      const existing = groupedItems.get(key);
      if (existing) {
        existing.matches.push(item);
        return;
      }
      groupedItems.set(key, { ...item, matches: [item] });
    });

    return Array.from(groupedItems.values()).slice(0, limit);
  }

  function uniqueItemCount(items) {
    return new Set(items.map((item) => normalize(item.name)).filter(Boolean)).size;
  }

  function uniqueValues(items, key) {
    return Array.from(new Set(items.map((item) => item[key] || "—")));
  }

  function groupedLocations(matches) {
    const guides = new Set();
    return matches.filter((item) => {
      if (guides.has(item.guide)) return false;
      guides.add(item.guide);
      return true;
    });
  }

  function makeElement(tag, className, text) {
    const element = document.createElement(tag);
    if (className) element.className = className;
    if (text !== undefined) element.textContent = text;
    return element;
  }

  function resolveHref(href) {
    const root = document.body?.dataset.ahRoot;
    if (!root || !String(href).startsWith("./")) return href;
    return `${root.replace(/\/?$/, "/")}${String(href).slice(2)}`;
  }

  function initializeSearch() {
    const input = document.getElementById("ah-search-input");
    const resultsElement = document.getElementById("ah-search-results");
    const statusElement = document.getElementById("ah-search-status");
    const countElement = document.getElementById("ah-search-count");
    const index = global.AH_SEARCH_INDEX;
    if (!input || !resultsElement || !statusElement || !index || !Array.isArray(index.items)) return;

    if (countElement) {
      countElement.textContent = `${uniqueItemCount(index.items).toLocaleString()} unique items across ${index.guideCount} guides`;
    }
    let visibleResults = [];
    let activeIndex = -1;

    function resultLinks() {
      return Array.from(resultsElement.querySelectorAll(".ah-search-result"))
        .map((card) => card.querySelector("a.ah-search-result-primary, a.ah-search-location-link"))
        .filter(Boolean);
    }

    function setActiveResult(nextIndex) {
      const links = resultLinks();
      if (!links.length) return;
      activeIndex = (nextIndex + links.length) % links.length;
      resultsElement.querySelectorAll(".ah-search-result").forEach((card) => card.classList.remove("is-active"));
      links.forEach((link, indexValue) => link.classList.toggle("is-active", indexValue === activeIndex));
      links[activeIndex].closest(".ah-search-result")?.classList.add("is-active");
      links[activeIndex].scrollIntoView({ block: "nearest" });
    }

    function render() {
      const query = input.value.trim();
      resultsElement.replaceChildren();
      activeIndex = -1;

      if (normalize(query).length < 2) {
        visibleResults = [];
        resultsElement.hidden = true;
        statusElement.hidden = !query;
        statusElement.textContent = query ? "Keep typing — enter at least 2 characters." : "";
        return;
      }

      visibleResults = searchItems(index.items, query);
      if (!visibleResults.length) {
        resultsElement.hidden = false;
        resultsElement.append(makeElement("li", "ah-search-empty", `No AH items found for “${query}”.`));
        statusElement.hidden = false;
        statusElement.textContent = "No matching Auction House items.";
        return;
      }

      visibleResults.forEach((item) => {
        const matches = item.matches || [item];
        const guideCount = new Set(matches.map((match) => match.guide)).size;
        const bidValues = uniqueValues(matches, "targetBid");
        const buyoutValues = uniqueValues(matches, "target");
        const stackValues = uniqueValues(matches, "stack");
        const priceBasisValues = Array.from(new Set(matches.map((match) => match.priceBasis).filter(Boolean)));
        const demandValues = uniqueValues(matches, "demand");
        const vendorRecommended = matches.some((match) => match.vendorRecommended === true);
        const vendorSellValues = uniqueValues(matches, "vendorSell");
        const vendorMinimumTargetValues = uniqueValues(matches, "vendorMinimumTarget");
        const conversionHints = Array.from(new Set(matches.map((match) => match.conversionHint).filter(Boolean)));
        const targetBidValue = bidValues[0] || "—";
        const targetBuyoutValue = buyoutValues[0] || "—";
        const stackValue = stackValues[0] || "—";
        const priceBasisValue = priceBasisValues[0] || "";
        const demandValue = demandValues[0] || "—";
        const hasTargetPrice = targetBidValue !== "—" || targetBuyoutValue !== "—";
        const lowDemand = demandValue === "Low" && !vendorRecommended;
        const grouped = matches.length > 1;
        const listItem = makeElement("li", "ah-search-result-item");
        const card = makeElement("article", "ah-search-result");
        card.classList.add(`quality-${item.quality}`);
        const primary = makeElement(grouped ? "div" : "a", "ah-search-result-primary");
        if (!grouped) primary.href = resolveHref(item.href);

        const topLine = makeElement("span", "ah-search-result-top");
        topLine.append(makeElement("strong", `ah-search-item-name quality-${item.quality}`, item.name));
        const targetPrice = makeElement("span", "ah-search-target-price");
        const targetBid = makeElement("span", "ah-search-target-part ah-search-target-bid");
        targetBid.append(makeElement("span", "ah-search-target-label", "Target Bid"));
        targetBid.append(makeElement("strong", "ah-search-target-value", targetBidValue));
        const targetBuyout = makeElement("span", "ah-search-target-part ah-search-target-buyout");
        targetBuyout.append(makeElement("span", "ah-search-target-label", "Buyout"));
        targetBuyout.append(makeElement("strong", "ah-search-target-value", targetBuyoutValue));
        targetPrice.append(targetBid, targetBuyout);
        if (hasTargetPrice) topLine.append(targetPrice);
        primary.append(topLine);

        const locationSummary = `${matches.length} ${matches.length === 1 ? "entry" : "entries"} across ${guideCount} ${guideCount === 1 ? "guide" : "guides"}`;
        const demandSummary = demandValue !== "—" ? `${demandValue} demand` : "";
        const meta = [grouped ? locationSummary : item.section, demandSummary]
          .filter(Boolean)
          .join(" · ");
        const detailLine = makeElement("span", "ah-search-result-detail-line");
        detailLine.append(makeElement("span", "ah-search-result-meta", meta));
        const stackDetails = makeElement("span", "ah-search-stack-details");
        if (vendorRecommended) {
          const vendorChip = makeElement("span", "ah-vendor-chip ah-search-vendor-chip", "Vendor");
          if (
            vendorSellValues.length === 1
            && vendorSellValues[0] !== "—"
            && vendorMinimumTargetValues.length === 1
            && vendorMinimumTargetValues[0] !== "—"
          ) {
            const basisLabel = priceBasisValue ? ` per ${priceBasisValue.toLowerCase()}` : " per item";
            vendorChip.title = `Vendor instead: NPC sell value ${vendorSellValues[0]} per item; Target needs at least ${vendorMinimumTargetValues[0]}${basisLabel} for this demand and posting margin.`;
          } else {
            vendorChip.title = "Vendor instead: this listing does not justify the expected fees, deposit risk, and posting effort.";
          }
          stackDetails.append(vendorChip);
        }
        if (lowDemand) {
          stackDetails.append(makeElement("span", "ah-low-chip ah-search-low-chip", "Low"));
        }
        if (priceBasisValue) {
          stackDetails.append(makeElement("span", "ah-price-stack-chip ah-search-price-stack-chip", priceBasisValue));
        }
        if (stackValue !== "1" && stackValue !== "—") {
          const stack = makeElement("span", "ah-search-stack-summary");
          stack.append(makeElement("span", "ah-search-stack-label", "Stack"));
          stack.append(makeElement("strong", "ah-search-stack-value", stackValue));
          stackDetails.append(stack);
        }
        if (stackDetails.childElementCount) detailLine.append(stackDetails);
        primary.append(detailLine);

        if (conversionHints.length) {
          const conversionHint = conversionHints.length === 1
            ? conversionHints[0]
            : "Multiple conversion estimates; open a guide below.";
          primary.append(makeElement("span", "ah-search-conversion-hint", `Conversion check: ${conversionHint}`));
        }

        if (!grouped) {
          const footer = makeElement("span", "ah-search-result-footer");
          footer.append(makeElement("span", "ah-search-result-guide", item.guide));
          footer.append(makeElement("span", "ah-search-result-arrow", "→"));
          primary.append(footer);
        }
        card.append(primary);

        if (grouped) {
          const locations = makeElement("span", "ah-search-result-locations");
          locations.append(makeElement("span", "ah-search-location-label", "Open in"));
          const routes = groupedLocations(matches);
          const guideOccurrences = new Map();
          routes.forEach((route) => guideOccurrences.set(route.guide, (guideOccurrences.get(route.guide) || 0) + 1));
          routes.forEach((route) => {
            const routeLabel = guideOccurrences.get(route.guide) > 1 ? `${route.guide} — ${route.section}` : route.guide;
            const routeLink = makeElement("a", "ah-search-location-link");
            routeLink.href = resolveHref(route.href);
            routeLink.append(makeElement("span", "ah-search-location-name", routeLabel));
            locations.append(routeLink);
          });
          card.append(locations);
        }

        listItem.append(card);
        resultsElement.append(listItem);
      });

      resultsElement.hidden = false;
      statusElement.hidden = false;
      statusElement.textContent = `${visibleResults.length} best ${visibleResults.length === 1 ? "match" : "matches"}`;
    }

    input.addEventListener("input", render);
    input.addEventListener("keydown", (event) => {
      if (!visibleResults.length) return;
      if (event.key === "ArrowDown") {
        event.preventDefault();
        setActiveResult(activeIndex + 1);
      } else if (event.key === "ArrowUp") {
        event.preventDefault();
        setActiveResult(activeIndex - 1);
      } else if (event.key === "Enter") {
        event.preventDefault();
        const links = resultLinks();
        const target = links[Math.max(0, activeIndex)];
        if (target) global.location.href = target.href;
      } else if (event.key === "Escape") {
        input.value = "";
        render();
      }
    });
    render();
  }

  function rowSectionTitle(row) {
    const heading = row.closest("section")?.querySelector("h2");
    if (!heading) return "";
    const copy = heading.cloneNode(true);
    copy.querySelectorAll(".ah-back-to-top, .ah-back-to-parent, .ah-category-chip-nav, .profession-audience-chip")
      .forEach((element) => element.remove());
    return normalize(copy.textContent);
  }

  function initializeVendorNotes() {
    const index = global.AH_SEARCH_INDEX;
    const guideId = document.body?.dataset.ahGuide;
    if (!index || !Array.isArray(index.items) || !guideId) return { expected: 0, rendered: 0 };

    const recommendations = new Map();
    index.items
      .filter((item) => item.guideId === guideId && item.vendorRecommended === true)
      .forEach((item) => {
        const note = String(item.vendorRecommendationNote || "").trim();
        if (!note) return;
        const key = `${slugify(item.name)}\u0000${normalize(item.section)}`;
        const notes = recommendations.get(key) || [];
        notes.push(note);
        recommendations.set(key, notes);
      });

    let expected = 0;
    recommendations.forEach((notes) => { expected += notes.length; });
    let rendered = 0;
    const rows = Array.from(document.querySelectorAll(".table-wrap > table > tbody > tr"));
    rows.forEach((row) => {
      row.querySelector(".ah-item-vendor-note")?.remove();
      const name = row.querySelector("td:first-child strong");
      if (!name) return;
      const key = `${slugify(name.textContent)}\u0000${rowSectionTitle(row)}`;
      const notes = recommendations.get(key);
      if (!notes?.length) return;
      const notesCell = row.querySelector('td[data-column="notes"]');
      if (!notesCell) return;

      const note = notes.shift();
      const noteElement = makeElement("div", "ah-item-vendor-note");
      noteElement.append(makeElement("strong", "", "Vendor:"));
      noteElement.append(document.createTextNode(` ${note}`));
      notesCell.prepend(noteElement);
      rendered += 1;
    });
    return { expected, rendered };
  }

  const PROFESSION_AUDIENCE_LABELS = {
    "general-use": {
      label: "No profession required",
      title: "The finished item does not require the crafting profession. Other listed requirements still apply."
    },
    "profession-restricted": {
      label: "Profession required",
      title: "The buyer must meet the listed profession and rank requirement."
    },
    "profession-input": {
      label: "Profession buyers",
      title: "This item is mainly a profession tool, reagent, component, or specialty container."
    },
    "class-restricted": {
      label: "Class required",
      title: "The buyer must meet the listed class requirement."
    },
    "mixed-input-and-general-use": {
      label: "Mixed use",
      title: "This section contains both general-use items and profession inputs."
    }
  };

  function initializeProfessionAudienceLabels() {
    let rendered = 0;
    document.querySelectorAll("section[data-use-audience]").forEach((section) => {
      const audience = section.dataset.useAudience;
      const content = PROFESSION_AUDIENCE_LABELS[audience];
      const heading = Array.from(section.children).find((child) => child.tagName === "H2");
      if (!content || !heading) return;

      let chip = heading.querySelector(".profession-audience-chip");
      if (!chip) {
        chip = makeElement("span", `profession-audience-chip profession-audience-chip--${audience}`);
        const firstControl = heading.querySelector(".ah-back-to-parent, .ah-back-to-top");
        heading.insertBefore(chip, firstControl || null);
      }
      chip.textContent = content.label;
      chip.title = content.title;
      rendered += 1;
    });
    return rendered;
  }

  function initializeRowSelection() {
    const rows = Array.from(document.querySelectorAll(".table-wrap > table > tbody > tr"));
    if (!rows.length) return;

    let selectedRow = null;

    function clearSelectedRow() {
      if (!selectedRow) return;
      selectedRow.classList.remove("ah-row-selected", "ah-row-pulse");
      selectedRow.setAttribute("aria-selected", "false");
      selectedRow = null;
    }

    function selectRow(row, options = {}) {
      const { toggle = false, pulse = false, scroll = false } = options;
      if (!row) return;

      if (selectedRow === row && toggle) {
        clearSelectedRow();
        return;
      }

      if (selectedRow && selectedRow !== row) clearSelectedRow();
      selectedRow = row;
      selectedRow.classList.add("ah-row-selected");
      selectedRow.setAttribute("aria-selected", "true");

      if (pulse) {
        const pulsedRow = selectedRow;
        pulsedRow.classList.remove("ah-row-pulse");
        void pulsedRow.offsetWidth;
        pulsedRow.classList.add("ah-row-pulse");
        pulsedRow.addEventListener("animationend", () => pulsedRow.classList.remove("ah-row-pulse"), { once: true });
      }

      if (scroll) {
        const rowToScroll = selectedRow;
        rowToScroll.tabIndex = -1;
        global.setTimeout(() => {
          rowToScroll.focus({ preventScroll: true });
          rowToScroll.scrollIntoView({ behavior: "smooth", block: "center" });
        }, 40);
      }
    }

    rows.forEach((row) => {
      row.classList.add("ah-row-selectable");
      row.setAttribute("aria-selected", "false");
      row.addEventListener("click", (event) => {
        if (event.target instanceof Element && event.target.closest("a, button, input, select, textarea, label")) return;
        selectRow(row, { toggle: true, pulse: true });
      });
    });

    function selectRowFromHash() {
      if (!global.location || !global.location.hash.startsWith("#ah-item=")) return;
      const params = new URLSearchParams(global.location.hash.slice(1));
      const requestedSlug = params.get("ah-item");
      const requestedOccurrence = Math.max(1, Number.parseInt(params.get("occurrence") || "1", 10));
      if (!requestedSlug) return;

      let occurrence = 0;
      const targetRow = rows.find((row) => {
        const name = row.querySelector("td:first-child strong");
        if (!name || slugify(name.textContent) !== requestedSlug) return false;
        occurrence += 1;
        return occurrence === requestedOccurrence;
      });
      selectRow(targetRow, { pulse: true, scroll: true });
    }

    global.addEventListener("hashchange", selectRowFromHash);
    selectRowFromHash();
  }

  global.AHSearchCore = {
    normalize,
    scoreItem,
    searchItems,
    slugify,
    uniqueItemCount,
    initializeVendorNotes,
    initializeProfessionAudienceLabels
  };
  if (typeof document !== "undefined") {
    document.addEventListener("DOMContentLoaded", () => {
      initializeSearch();
      initializeVendorNotes();
      initializeProfessionAudienceLabels();
      initializeRowSelection();
    });
  }
})(typeof window !== "undefined" ? window : globalThis);
