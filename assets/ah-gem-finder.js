(function (global) {
  "use strict";

  const MAX_RESULTS = 60;
  const DEMAND_RANK = {
    "very high": 6,
    high: 5,
    "med high": 4,
    med: 3,
    medium: 3,
    "low med": 2,
    low: 1,
  };
  const POPULAR_STATS = [
    ["strength", "Strength", ["strength"]],
    ["agility", "Agility", ["agility"]],
    ["spell-power", "Spell Power", ["spell power"]],
    ["hit", "Hit", ["hit rating"]],
    ["haste", "Haste", ["haste rating"]],
    ["crit", "Crit", ["critical strike", "critical damage"]],
    ["armor-penetration", "Armor Pen", ["armor penetration"]],
    ["stamina", "Stamina", ["stamina"]],
  ];
  const EXTRA_STATS = [
    ["attack-power", "Attack Power", ["attack power"]],
    ["expertise", "Expertise", ["expertise rating"]],
    ["defense", "Defense", ["defense rating"]],
    ["dodge", "Dodge", ["dodge rating"]],
    ["parry", "Parry", ["parry rating"]],
    ["resilience", "Resilience", ["resilience rating"]],
    ["intellect", "Intellect", ["intellect"]],
    ["spirit", "Spirit", ["spirit"]],
    ["mana-regen", "Mana Regen", ["mana every 5 seconds", "mana per 5 seconds"]],
    ["spell-penetration", "Spell Pen", ["spell penetration"]],
  ];
  const STAT_DEFINITIONS = [...POPULAR_STATS, ...EXTRA_STATS].map(([id, label, terms]) => ({
    id,
    label,
    terms,
  }));
  const STAT_BY_ID = new Map(STAT_DEFINITIONS.map((stat) => [stat.id, stat]));

  function normalize(value) {
    return String(value || "")
      .toLowerCase()
      .replace(/\barp\b/g, "armor penetration")
      .replace(/\bmp5\b/g, "mana every 5 seconds")
      .replace(/\bcrit\b/g, "critical")
      .replace(/\bsp\b/g, "spell power")
      .replace(/[^a-z0-9]+/g, " ")
      .trim()
      .replace(/\s+/g, " ");
  }

  function slugify(value) {
    if (global.AHSearchCore?.slugify) return global.AHSearchCore.slugify(value);
    return normalize(value).replace(/\s+/g, "-");
  }

  function parseMoney(value) {
    const text = String(value || "").replace(/,/g, "");
    const gold = Number.parseInt(text.match(/(\d+)g/)?.[1] || "0", 10);
    const silver = Number.parseInt(text.match(/(\d+)s/)?.[1] || "0", 10);
    const copper = Number.parseInt(text.match(/(\d+)c/)?.[1] || "0", 10);
    return (gold * 10000) + (silver * 100) + copper;
  }

  function socketMatches(detail, effect) {
    if (/meta-gem cut/i.test(detail) || /meta gem slot/i.test(effect)) return ["meta"];
    const matchText = effect.match(/matches?\s+(?:an?\s+)?(.+?)\s+sockets?\.?/i)?.[1] || "";
    return ["red", "yellow", "blue"].filter((color) => new RegExp(`\\b${color}\\b`, "i").test(matchText));
  }

  function qualityFromRow(row) {
    const qualityClass = Array.from(row.querySelector("td:first-child strong")?.classList || [])
      .find((className) => className.startsWith("q-"));
    return qualityClass ? qualityClass.slice(2) : "common";
  }

  function collectCuts(document) {
    return Array.from(document.querySelectorAll(".ah-crafted-market tr[data-crafted-key]"))
      .map((row, sourceIndex) => {
        const nameElement = row.querySelector("td:first-child strong");
        const detail = row.querySelector("td:first-child .mini")?.textContent.trim() || "";
        const effect = row.querySelector("[data-column='notes'] .crafted-item-note")?.textContent.trim() || "";
        if (!nameElement || !/cut/i.test(detail)) return null;
        const demand = row.querySelector("[data-column='demand'] .demand")?.textContent.trim() || "—";
        const target = row.querySelector("[data-column='target'] .buyout")?.textContent.trim() || "—";
        const sockets = socketMatches(detail, effect);
        const normalizedEffect = normalize(effect);
        const stats = new Set(
          STAT_DEFINITIONS
            .filter((stat) => stat.terms.some((term) => normalizedEffect.includes(normalize(term))))
            .map((stat) => stat.id),
        );
        const name = nameElement.textContent.trim();
        const quality = qualityFromRow(row);
        return {
          row,
          sourceIndex,
          name,
          detail,
          effect,
          demand,
          demandRank: DEMAND_RANK[normalize(demand)] || 0,
          target,
          targetCopper: parseMoney(target),
          sockets,
          socketLabel: sockets.length ? sockets.map((socket) => socket[0].toUpperCase() + socket.slice(1)).join(" / ") : "Special",
          quality,
          stats,
          href: `#ah-item=${slugify(name)}`,
          searchText: normalize(`${name} ${detail} ${effect} ${demand} ${sockets.join(" ")}`),
        };
      })
      .filter(Boolean);
  }

  function makeElement(document, tag, className, text) {
    const element = document.createElement(tag);
    if (className) element.className = className;
    if (text !== undefined) element.textContent = text;
    return element;
  }

  function initializeGemFinder() {
    const document = global.document;
    const finder = document?.querySelector("[data-ah-gem-finder]");
    if (!finder || finder.dataset.gemFinderReady === "true") return;

    const cuts = collectCuts(document);
    if (!cuts.length) return;

    const input = finder.querySelector("#ah-gem-search-input");
    const results = finder.querySelector("#ah-gem-results");
    const status = finder.querySelector("#ah-gem-status");
    const activeFilters = finder.querySelector("#ah-gem-active-filters");
    const activeRow = finder.querySelector("#ah-gem-active-row");
    const clearButton = finder.querySelector("#ah-gem-clear");
    const moreButton = finder.querySelector("#ah-gem-more-stats");
    const moreStats = finder.querySelector("#ah-gem-extra-stats");
    const sortSelect = finder.querySelector("#ah-gem-sort");
    if (!input || !results || !status || !activeFilters || !activeRow || !clearButton || !sortSelect) return;

    finder.dataset.gemFinderReady = "true";
    finder.dataset.cutCount = String(cuts.length);
    const state = {
      stats: new Set(),
      tier: "all",
      socket: "any",
      sort: "demand",
    };

    function chipButtons(group) {
      return Array.from(finder.querySelectorAll(`[data-gem-filter-group="${group}"]`));
    }

    function updatePressedStates() {
      finder.querySelectorAll("[data-gem-stat]").forEach((button) => {
        button.setAttribute("aria-pressed", String(state.stats.has(button.dataset.gemStat)));
      });
      chipButtons("tier").forEach((button) => {
        button.setAttribute("aria-pressed", String(state.tier === button.dataset.gemFilterValue));
      });
      chipButtons("socket").forEach((button) => {
        button.setAttribute("aria-pressed", String(state.socket === button.dataset.gemFilterValue));
      });
    }

    function activeFilterEntries(query) {
      const entries = [];
      if (query) entries.push({ type: "query", value: query, label: `Search: ${query}` });
      state.stats.forEach((statId) => entries.push({ type: "stat", value: statId, label: STAT_BY_ID.get(statId)?.label || statId }));
      if (state.tier !== "all") entries.push({ type: "tier", value: state.tier, label: `Tier: ${state.tier[0].toUpperCase()}${state.tier.slice(1)}` });
      if (state.socket !== "any") entries.push({ type: "socket", value: state.socket, label: `Socket: ${state.socket[0].toUpperCase()}${state.socket.slice(1)}` });
      return entries;
    }

    function renderActiveFilters(query) {
      const entries = activeFilterEntries(query);
      activeFilters.replaceChildren();
      entries.forEach((entry) => {
        const button = makeElement(document, "button", "ah-gem-active-chip", `${entry.label} ×`);
        button.type = "button";
        button.dataset.activeFilterType = entry.type;
        button.dataset.activeFilterValue = entry.value;
        button.setAttribute("aria-label", `Remove ${entry.label} filter`);
        activeFilters.append(button);
      });
      activeRow.hidden = entries.length === 0;
      clearButton.hidden = entries.length === 0;
    }

    function queryMatches(cut, rawQuery) {
      const query = normalize(rawQuery);
      if (!query) return true;
      return query.split(" ").every((token) => cut.searchText.includes(token));
    }

    function filteredCuts(rawQuery) {
      const matches = cuts.filter((cut) => (
        queryMatches(cut, rawQuery)
        && Array.from(state.stats).every((statId) => cut.stats.has(statId))
        && (state.tier === "all" || cut.quality === state.tier)
        && (state.socket === "any" || cut.sockets.includes(state.socket))
      ));
      return matches.sort((left, right) => {
        if (state.sort === "price-high") return right.targetCopper - left.targetCopper || left.name.localeCompare(right.name);
        if (state.sort === "price-low") return left.targetCopper - right.targetCopper || left.name.localeCompare(right.name);
        if (state.sort === "name") return left.name.localeCompare(right.name);
        return right.demandRank - left.demandRank || right.targetCopper - left.targetCopper || left.sourceIndex - right.sourceIndex;
      });
    }

    function repeatCurrentJump(event, cut) {
      if (global.location.hash !== cut.href) return;
      event.preventDefault();
      document.querySelectorAll("tr.ah-row-selected").forEach((row) => {
        if (row === cut.row) return;
        row.classList.remove("ah-row-selected", "ah-row-pulse");
        row.setAttribute("aria-selected", "false");
      });
      cut.row.classList.add("ah-row-selected", "ah-row-pulse");
      cut.row.setAttribute("aria-selected", "true");
      cut.row.tabIndex = -1;
      cut.row.focus({ preventScroll: true });
      cut.row.scrollIntoView({ behavior: "smooth", block: "center" });
    }

    function renderResult(cut) {
      const item = makeElement(document, "li", "ah-gem-result-item");
      const link = makeElement(document, "a", `ah-gem-result quality-${cut.quality}`);
      link.href = cut.href;
      link.dataset.gemTier = cut.quality;
      link.dataset.gemSockets = cut.sockets.join(" ");
      link.dataset.gemStats = Array.from(cut.stats).join(" ");
      link.addEventListener("click", (event) => repeatCurrentJump(event, cut));

      const top = makeElement(document, "span", "ah-gem-result-top");
      top.append(makeElement(document, "strong", `ah-gem-result-name q-${cut.quality}`, cut.name));
      const price = makeElement(document, "span", "ah-gem-result-price");
      price.append(makeElement(document, "span", "ah-gem-result-price-label", "Target"));
      price.append(makeElement(document, "strong", "ah-gem-result-price-value", cut.target));
      top.append(price);

      const effect = makeElement(document, "span", "ah-gem-result-effect", cut.effect);
      const meta = makeElement(document, "span", "ah-gem-result-meta");
      meta.append(makeElement(document, "span", "ah-gem-result-tag", cut.detail.replace(/ socket cut$/i, "")));
      meta.append(makeElement(document, "span", "ah-gem-result-tag", `${cut.socketLabel} socket`));
      meta.append(makeElement(document, "span", "ah-gem-result-demand", cut.demand));
      meta.append(makeElement(document, "span", "ah-gem-result-arrow", "→"));
      link.append(top, effect, meta);
      item.append(link);
      return item;
    }

    function render() {
      const rawQuery = input.value.trim();
      const hasFilter = Boolean(rawQuery || state.stats.size || state.tier !== "all" || state.socket !== "any");
      updatePressedStates();
      renderActiveFilters(rawQuery);
      results.replaceChildren();

      if (!hasFilter) {
        results.hidden = true;
        status.textContent = `${cuts.length.toLocaleString()} cut gems available. Choose a popular stat or use the finder.`;
        return;
      }

      const matches = filteredCuts(rawQuery);
      const visibleMatches = matches.slice(0, MAX_RESULTS);
      if (!matches.length) {
        results.hidden = false;
        results.append(makeElement(document, "li", "ah-gem-empty", "No exact cut matches. Remove a filter or try a broader stat."));
        status.textContent = "0 matching cuts";
        return;
      }

      visibleMatches.forEach((cut) => results.append(renderResult(cut)));
      results.hidden = false;
      status.textContent = matches.length > MAX_RESULTS
        ? `${matches.length} matching cuts · showing the first ${MAX_RESULTS}`
        : `${matches.length} matching ${matches.length === 1 ? "cut" : "cuts"}`;
    }

    finder.querySelectorAll("[data-gem-stat]").forEach((button) => {
      button.addEventListener("click", () => {
        const statId = button.dataset.gemStat;
        if (state.stats.has(statId)) state.stats.delete(statId);
        else state.stats.add(statId);
        render();
      });
    });
    chipButtons("tier").forEach((button) => {
      button.addEventListener("click", () => {
        state.tier = button.dataset.gemFilterValue;
        render();
      });
    });
    chipButtons("socket").forEach((button) => {
      button.addEventListener("click", () => {
        state.socket = button.dataset.gemFilterValue;
        render();
      });
    });
    activeFilters.addEventListener("click", (event) => {
      const button = event.target.closest("[data-active-filter-type]");
      if (!button) return;
      if (button.dataset.activeFilterType === "query") input.value = "";
      if (button.dataset.activeFilterType === "stat") state.stats.delete(button.dataset.activeFilterValue);
      if (button.dataset.activeFilterType === "tier") state.tier = "all";
      if (button.dataset.activeFilterType === "socket") state.socket = "any";
      render();
    });
    clearButton.addEventListener("click", () => {
      input.value = "";
      state.stats.clear();
      state.tier = "all";
      state.socket = "any";
      state.sort = "demand";
      sortSelect.value = "demand";
      render();
      input.focus();
    });
    input.addEventListener("input", render);
    sortSelect.addEventListener("change", () => {
      state.sort = sortSelect.value;
      render();
    });
    moreButton?.addEventListener("click", () => {
      const expanded = moreButton.getAttribute("aria-expanded") === "true";
      moreButton.setAttribute("aria-expanded", String(!expanded));
      moreStats.hidden = expanded;
    });

    render();
  }

  global.AHGemFinderCore = {
    collectCuts,
    normalize,
    parseMoney,
    socketMatches,
  };
  if (typeof document !== "undefined") {
    document.addEventListener("DOMContentLoaded", initializeGemFinder);
  }
})(typeof window !== "undefined" ? window : globalThis);
