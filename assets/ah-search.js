(function (global) {
  "use strict";

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
    return items
      .map((item) => ({ item, score: scoreItem(item, query) }))
      .filter((result) => Number.isFinite(result.score))
      .sort((left, right) =>
        left.score - right.score ||
        left.item.name.localeCompare(right.item.name) ||
        left.item.guide.localeCompare(right.item.guide)
      )
      .slice(0, limit)
      .map((result) => result.item);
  }

  function makeElement(tag, className, text) {
    const element = document.createElement(tag);
    if (className) element.className = className;
    if (text !== undefined) element.textContent = text;
    return element;
  }

  function initializeSearch() {
    const input = document.getElementById("ah-search-input");
    const resultsElement = document.getElementById("ah-search-results");
    const statusElement = document.getElementById("ah-search-status");
    const countElement = document.getElementById("ah-search-count");
    const index = global.AH_SEARCH_INDEX;
    if (!input || !resultsElement || !statusElement || !index || !Array.isArray(index.items)) return;

    if (countElement) {
      countElement.textContent = `${index.itemCount.toLocaleString()} items across ${index.guideCount} guides`;
    }
    let visibleResults = [];
    let activeIndex = -1;

    function setActiveResult(nextIndex) {
      const links = Array.from(resultsElement.querySelectorAll("a"));
      if (!links.length) return;
      activeIndex = (nextIndex + links.length) % links.length;
      links.forEach((link, indexValue) => link.classList.toggle("is-active", indexValue === activeIndex));
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
        const listItem = makeElement("li", "ah-search-result-item");
        const link = makeElement("a", "ah-search-result");
        link.href = item.href;
        link.classList.add(`quality-${item.quality}`);

        const topLine = makeElement("span", "ah-search-result-top");
        topLine.append(makeElement("strong", `ah-search-item-name quality-${item.quality}`, item.name));
        const targetPrice = makeElement("span", "ah-search-target-price");
        targetPrice.append(makeElement("span", "ah-search-target-label", "Target"));
        targetPrice.append(makeElement("strong", "ah-search-target-value", item.target));
        topLine.append(targetPrice);
        link.append(topLine);

        const meta = [item.section, item.demand !== "—" ? `${item.demand} demand` : ""]
          .filter(Boolean)
          .join(" · ");
        link.append(makeElement("span", "ah-search-result-meta", meta));

        const footer = makeElement("span", "ah-search-result-footer");
        footer.append(makeElement("span", "ah-search-result-guide", item.guide));
        footer.append(makeElement("span", "ah-search-result-arrow", "→"));
        link.append(footer);
        listItem.append(link);
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
        const target = visibleResults[Math.max(0, activeIndex)];
        if (target) global.location.href = target.href;
      } else if (event.key === "Escape") {
        input.value = "";
        render();
      }
    });
    render();
  }

  function initializeRowHighlight() {
    if (!global.location || !global.location.hash.startsWith("#ah-item=")) return;
    const params = new URLSearchParams(global.location.hash.slice(1));
    const requestedSlug = params.get("ah-item");
    const requestedOccurrence = Math.max(1, Number.parseInt(params.get("occurrence") || "1", 10));
    if (!requestedSlug) return;

    let occurrence = 0;
    const targetRow = Array.from(document.querySelectorAll("table tbody tr")).find((row) => {
      const name = row.querySelector("td:first-child strong");
      if (!name || slugify(name.textContent) !== requestedSlug) return false;
      occurrence += 1;
      return occurrence === requestedOccurrence;
    });
    if (!targetRow) return;

    const style = document.createElement("style");
    style.textContent = `
      tr.ah-search-target td { background: rgba(240,193,90,.17) !important; }
      tr.ah-search-target td:first-child { box-shadow: inset 4px 0 #f0c15a; }
      tr.ah-search-target { animation: ah-search-pulse 1.4s ease-out 1; }
      @keyframes ah-search-pulse { 0%,35% { filter: brightness(1.45); } 100% { filter: none; } }
      @media (prefers-reduced-motion: reduce) { tr.ah-search-target { animation: none; } }
    `;
    document.head.append(style);
    targetRow.classList.add("ah-search-target");
    targetRow.tabIndex = -1;
    global.setTimeout(() => {
      targetRow.focus({ preventScroll: true });
      targetRow.scrollIntoView({ behavior: "smooth", block: "center" });
    }, 40);
  }

  global.AHSearchCore = { normalize, scoreItem, searchItems, slugify };
  if (typeof document !== "undefined") {
    document.addEventListener("DOMContentLoaded", () => {
      initializeSearch();
      initializeRowHighlight();
    });
  }
})(typeof window !== "undefined" ? window : globalThis);
