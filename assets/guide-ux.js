(function () {
  "use strict";

  function enhanceTables() {
    document.querySelectorAll(".table-wrap").forEach(function (wrapper) {
      wrapper.dataset.mobileScrollHint = "true";
      if (!wrapper.hasAttribute("role")) wrapper.setAttribute("role", "region");
      if (!wrapper.hasAttribute("tabindex")) wrapper.tabIndex = 0;
      if (!wrapper.hasAttribute("aria-label")) wrapper.setAttribute("aria-label", "Scrollable guide table");
    });
  }

  function enhanceTalentTrees() {
    document.querySelectorAll(".talent-embed-wrap").forEach(function (embedWrapper) {
      if (embedWrapper.closest(".talent-tree-details")) return;

      const fallback = embedWrapper.nextElementSibling &&
        embedWrapper.nextElementSibling.matches(".talent-fallback")
        ? embedWrapper.nextElementSibling
        : null;
      const fallbackLink = fallback && fallback.querySelector("a[href]");
      const parent = embedWrapper.parentElement;
      if (!parent) return;

      if (fallbackLink) {
        const primaryLink = document.createElement("p");
        primaryLink.className = "talent-tree-primary-link";
        const label = document.createElement("strong");
        label.textContent = "Interactive calculator:";
        const link = fallbackLink.cloneNode(true);
        link.textContent = "Open the complete build in Wowhead";
        primaryLink.append(label, document.createTextNode(" "), link);
        parent.insertBefore(primaryLink, embedWrapper);
      }

      const details = document.createElement("details");
      details.className = "talent-tree-details";
      const summary = document.createElement("summary");
      summary.textContent = "View interactive talent tree";
      details.appendChild(summary);
      parent.insertBefore(details, embedWrapper);
      details.appendChild(embedWrapper);
      if (fallback) details.appendChild(fallback);
      parent.classList.add("has-collapsible-talent-tree");
    });
  }

  function addHolyPaladinPager() {
    if (!document.body.matches('[data-guide-class="paladin"][data-guide-spec="holy"]')) return;
    const main = document.querySelector("main");
    if (!main || main.querySelector(".page-pager")) return;

    const guideLinks = Array.from(document.querySelectorAll(".site-nav > a"))
      .filter(function (link) { return !link.classList.contains("guide-hub-link"); });
    const currentIndex = guideLinks.findIndex(function (link) {
      return link.getAttribute("aria-current") === "page";
    });
    if (currentIndex < 0) return;

    const pager = document.createElement("nav");
    pager.className = "page-pager";
    pager.setAttribute("aria-label", "Previous and next guide pages");

    const previous = guideLinks[currentIndex - 1];
    const next = guideLinks[currentIndex + 1];
    if (previous) {
      const link = document.createElement("a");
      link.href = previous.getAttribute("href");
      link.textContent = "← " + previous.textContent.trim();
      pager.appendChild(link);
    } else {
      pager.appendChild(document.createElement("span"));
    }

    if (next) {
      const link = document.createElement("a");
      link.href = next.getAttribute("href");
      link.textContent = next.textContent.trim() + " →";
      pager.appendChild(link);
    } else {
      pager.appendChild(document.createElement("span"));
    }

    main.appendChild(pager);
  }

  function setEncounterOpen(encounter, open) {
    const button = encounter.querySelector(":scope > h3 > .raid-encounter-toggle");
    const body = encounter.querySelector(":scope > .raid-encounter-body");
    if (!button || !body) return;
    button.setAttribute("aria-expanded", String(open));
    body.hidden = !open;
    encounter.classList.toggle("is-open", open);
  }

  function enhanceRaidEncounters() {
    if (!document.body.matches('[data-guide-class="priest"], [data-guide-class="hunter"]')) return;
    const grid = document.querySelector(".raid-encounter-grid");
    if (!grid || grid.dataset.accordionReady === "true") return;

    const encounters = Array.from(grid.querySelectorAll(":scope > .raid-encounter"));
    if (!encounters.length) return;

    encounters.forEach(function (encounter, index) {
      const heading = encounter.querySelector(":scope > h3");
      if (!heading) return;

      const body = document.createElement("div");
      body.className = "raid-encounter-body";
      body.id = "raid-encounter-body-" + (index + 1);
      while (heading.nextSibling) body.appendChild(heading.nextSibling);

      const button = document.createElement("button");
      button.type = "button";
      button.className = "raid-encounter-toggle";
      button.setAttribute("aria-expanded", "false");
      button.setAttribute("aria-controls", body.id);
      while (heading.firstChild) button.appendChild(heading.firstChild);

      const chevron = document.createElement("span");
      chevron.className = "raid-encounter-chevron";
      chevron.setAttribute("aria-hidden", "true");
      chevron.textContent = "▾";
      button.appendChild(chevron);
      heading.appendChild(button);
      encounter.appendChild(body);

      button.addEventListener("click", function () {
        setEncounterOpen(encounter, button.getAttribute("aria-expanded") !== "true");
      });
      setEncounterOpen(encounter, false);
    });

    const actions = document.createElement("div");
    actions.className = "raid-accordion-actions";
    actions.setAttribute("aria-label", "Encounter display controls");

    const expand = document.createElement("button");
    expand.type = "button";
    expand.textContent = "Expand visible";
    const collapse = document.createElement("button");
    collapse.type = "button";
    collapse.textContent = "Collapse all";
    actions.append(expand, collapse);
    grid.parentElement.insertBefore(actions, grid);

    expand.addEventListener("click", function () {
      encounters.forEach(function (encounter) {
        if (!encounter.hidden) setEncounterOpen(encounter, true);
      });
    });
    collapse.addEventListener("click", function () {
      encounters.forEach(function (encounter) { setEncounterOpen(encounter, false); });
    });

    grid.dataset.accordionReady = "true";
  }

  function init() {
    enhanceTables();
    enhanceTalentTrees();
    addHolyPaladinPager();
    enhanceRaidEncounters();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init, { once: true });
  } else {
    init();
  }
}());
