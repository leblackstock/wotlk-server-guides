(function (global) {
  "use strict";

  const MAX_RESULTS = 6;

  function make(tag, className, text) {
    const node = document.createElement(tag);
    if (className) node.className = className;
    if (text !== undefined) node.textContent = text;
    return node;
  }

  function resultHref(addon, query) {
    const encodedQuery = encodeURIComponent(query.trim());
    const encodedAddon = encodeURIComponent(addon.id);
    return `./guides/addons.html?q=${encodedQuery}#addon=${encodedAddon}`;
  }

  function initializeAddonHubSearch() {
    const catalog = global.ADDON_CATALOG;
    const core = global.AddonSearchCore;
    const input = document.getElementById("addon-hub-search-input");
    const resultsElement = document.getElementById("addon-hub-search-results");
    const statusElement = document.getElementById("addon-hub-search-status");
    const browseLink = document.getElementById("addon-hub-browse");
    if (!catalog || !core || !input || !resultsElement || !statusElement || !browseLink) return;

    const tags = new Map(catalog.tags.map((tag) => [tag.id, tag]));
    let visibleResults = [];
    let activeIndex = -1;

    function updateBrowseLink(query) {
      const cleanQuery = query.trim();
      browseLink.href = cleanQuery
        ? `./guides/addons.html?q=${encodeURIComponent(cleanQuery)}`
        : "./guides/addons.html";
    }

    function setActiveResult(nextIndex) {
      const links = Array.from(resultsElement.querySelectorAll("a.addon-hub-search-result"));
      if (!links.length) return;
      activeIndex = (nextIndex + links.length) % links.length;
      links.forEach((link, index) => link.classList.toggle("is-active", index === activeIndex));
      links[activeIndex].scrollIntoView({ block: "nearest" });
    }

    function renderResult(addon, query) {
      const item = make("li", "ah-search-result-item");
      const link = make("a", "ah-search-result addon-hub-search-result");
      link.href = resultHref(addon, query);

      const top = make("span", "addon-hub-result-top");
      const icon = make("img", "addon-hub-result-icon");
      icon.src = `./${addon.icon.path}`;
      icon.alt = "";
      icon.width = 38;
      icon.height = 38;
      const identity = make("span", "addon-hub-result-identity");
      identity.append(make("strong", "ah-search-item-name", addon.name));
      const featured = (addon.featuredTags || [])
        .slice(0, 2)
        .map((id) => tags.get(id)?.label)
        .filter(Boolean)
        .join(" · ");
      if (featured) identity.append(make("span", "addon-hub-result-tags", featured));
      top.append(icon, identity);
      link.append(top);

      link.append(make("span", "ah-search-result-meta", addon.summary));
      const footer = make("span", "ah-search-result-footer");
      footer.append(make("span", "ah-search-result-guide", "Open addon details"));
      footer.append(make("span", "ah-search-result-arrow", "→"));
      link.append(footer);

      item.append(link);
      return item;
    }

    function render() {
      const query = input.value.trim();
      updateBrowseLink(query);
      resultsElement.replaceChildren();
      activeIndex = -1;

      if (core.normalize(query).length < 2) {
        visibleResults = [];
        resultsElement.hidden = true;
        statusElement.hidden = !query;
        statusElement.textContent = query ? "Keep typing — enter at least 2 characters." : "";
        return;
      }

      visibleResults = core
        .filterAndSort(catalog.addons, { query, filters: {}, sort: "smart", addon: "" }, catalog)
        .slice(0, MAX_RESULTS);

      if (!visibleResults.length) {
        resultsElement.hidden = false;
        resultsElement.append(make("li", "ah-search-empty", `No addons found for “${query}”.`));
        statusElement.hidden = false;
        statusElement.textContent = "No matching addons.";
        return;
      }

      visibleResults.forEach((addon) => resultsElement.append(renderResult(addon, query)));
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
        if (target) global.location.href = resultHref(target, input.value);
      } else if (event.key === "Escape") {
        input.value = "";
        render();
      }
    });
    render();
  }

  if (typeof document !== "undefined") {
    document.addEventListener("DOMContentLoaded", initializeAddonHubSearch);
  }
})(typeof window !== "undefined" ? window : globalThis);
