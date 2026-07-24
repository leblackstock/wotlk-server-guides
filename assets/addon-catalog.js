(function (global) {
  "use strict";

  const QUICK_FILTERS = [
    { group: "role", id: "tank" },
    { group: "class", id: "paladin" },
    { group: "activity", id: "raids" },
    { group: "primary-use", id: "interface" }
  ];

  const COMPATIBILITY_LABELS = {
    "maintained-port": "Maintained port",
    "wrath-era": "Wrath-era build",
    "old-unmaintained": "Old / unmaintained",
    "legacy-compatible": "Legacy compatibility build"
  };

  function make(tag, className, text) {
    const node = document.createElement(tag);
    if (className) node.className = className;
    if (text !== undefined) node.textContent = text;
    return node;
  }

  function appendList(parent, items, ordered) {
    if (!items || !items.length) return;
    const list = make(ordered ? "ol" : "ul");
    items.forEach((item) => list.append(make("li", "", item)));
    parent.append(list);
  }

  function titleCase(value) {
    return String(value || "")
      .replace(/[-_]+/g, " ")
      .replace(/\b\w/g, (letter) => letter.toUpperCase());
  }

  function initializeCatalog() {
    const catalog = global.ADDON_CATALOG;
    const core = global.AddonSearchCore;
    if (!catalog || !core || !Array.isArray(catalog.addons)) return;

    const tagMap = new Map(catalog.tags.map((tag) => [tag.id, tag]));
    const groupMap = new Map(catalog.tagGroups.map((group) => [group.id, group]));
    const importanceMap = new Map(catalog.importanceLevels.map((item) => [item.id, item]));
    const purposeMap = new Map(catalog.purposes.map((item) => [item.id, item]));
    const addonMap = new Map(catalog.addons.map((addon) => [addon.id, addon]));

    const input = document.getElementById("addon-search-input");
    const sort = document.getElementById("addon-sort");
    const quick = document.getElementById("addon-quick-filters");
    const filterToggle = document.getElementById("addon-all-filters");
    const filterPanel = document.getElementById("addon-filter-groups");
    const activeArea = document.getElementById("addon-active-area");
    const activeFilters = document.getElementById("addon-active-filters");
    const clearAll = document.getElementById("addon-clear-all");
    const count = document.getElementById("addon-result-count");
    const contextBanner = document.getElementById("addon-context-banner");
    const grid = document.getElementById("addon-grid");
    const empty = document.getElementById("addon-empty");
    const emptyClear = document.getElementById("addon-empty-clear");
    const dialog = document.getElementById("addon-details-dialog");
    const dialogClose = document.getElementById("addon-dialog-close");
    const dialogContent = document.getElementById("addon-dialog-content");
    if (![input, sort, quick, filterToggle, filterPanel, activeArea, activeFilters, clearAll, count, contextBanner, grid, empty, emptyClear, dialog, dialogClose, dialogContent].every(Boolean)) return;

    let state = core.parseUrlState(global.location.href, catalog);
    let originButton = null;
    let originAddonId = "";
    let pendingFocusAddonId = "";
    let dialogUrlWasPushed = false;
    let handlingHistory = false;

    function iconPath(addon) {
      return `../${addon.icon.path}`;
    }

    function labelFor(group, id) {
      if (group === "importance") return importanceMap.get(id)?.label || titleCase(id);
      if (group === "purpose") return purposeMap.get(id)?.label || titleCase(id);
      const tag = tagMap.get(id);
      if (group === "specialization" && tag?.shortLabel) {
        const selectedClasses = state.filters.class || [];
        if (selectedClasses.length === 1 && selectedClasses[0] === tag.classId) return tag.shortLabel;
      }
      return tag?.label || titleCase(id);
    }

    function cloneState() {
      return {
        query: state.query,
        sort: state.sort,
        addon: state.addon,
        filters: Object.fromEntries(Object.entries(state.filters || {}).map(([group, values]) => [group, [...values]]))
      };
    }

    function hasFilters() {
      return Object.values(state.filters || {}).some((values) => Array.isArray(values) && values.length);
    }

    function updateUrl(mode) {
      if (handlingHistory) return;
      const next = core.stateToUrl(state, global.location.href, catalog);
      const method = mode === "push" ? "pushState" : "replaceState";
      global.history[method]({}, "", `${next.pathname}${next.search}${next.hash}`);
    }

    function toggleFilter(group, id, pushHistory) {
      const values = new Set(state.filters[group] || []);
      if (values.has(id)) values.delete(id);
      else values.add(id);
      if (values.size) state.filters[group] = Array.from(values);
      else delete state.filters[group];
      state.addon = "";
      updateUrl(pushHistory ? "push" : "replace");
      render();
    }

    function clearFilters(pushHistory) {
      state.query = "";
      state.filters = {};
      state.sort = "smart";
      state.addon = "";
      input.value = "";
      sort.value = "smart";
      updateUrl(pushHistory ? "push" : "replace");
      render();
    }

    function countForOption(group, id) {
      const trial = cloneState();
      trial.filters[group] = [id];
      trial.addon = "";
      return core.filterAndSort(catalog.addons, trial, catalog).length;
    }

    function allPotentialOptions(group) {
      if (group === "importance") return catalog.importanceLevels.map((item) => item.id);
      if (group === "purpose") return catalog.purposes.map((item) => item.id);
      return catalog.tags
        .filter((tag) => tag.group === group)
        .sort((left, right) => left.order - right.order || left.label.localeCompare(right.label))
        .map((tag) => tag.id);
    }

    function isMeaningfulOption(group, id) {
      if (group !== "specialization") return true;
      const tag = tagMap.get(id);
      const selectedClasses = state.filters.class || [];
      if (selectedClasses.length === 1 && tag?.classId !== selectedClasses[0]) return false;
      return catalog.addons.some((addon) => {
        if ((addon.tags || []).includes(id) || (addon.scope?.specs || []).includes(id)) return true;
        return [addon.recommendations || [], addon.customizations || []].some((records) =>
          records.some((record) => (record.audience?.specs || []).includes(id))
        );
      });
    }

    function groupOptions(group) {
      return allPotentialOptions(group).filter((id) => {
        if ((state.filters[group] || []).includes(id)) return true;
        if (!isMeaningfulOption(group, id)) return false;
        return countForOption(group, id) > 0;
      });
    }

    function filterButton(group, id, includeCount) {
      const selected = (state.filters[group] || []).includes(id);
      const optionCount = countForOption(group, id);
      const button = make("button", "addon-filter-chip");
      button.type = "button";
      button.setAttribute("aria-pressed", String(selected));
      button.dataset.group = group;
      button.dataset.value = id;
      const label = make("span", "", labelFor(group, id));
      button.append(label);
      if (includeCount) button.append(make("span", "addon-filter-count", String(optionCount)));
      button.disabled = optionCount === 0 && !selected;
      button.addEventListener("click", () => toggleFilter(group, id, true));
      return button;
    }

    function renderQuickFilters() {
      quick.replaceChildren();
      QUICK_FILTERS.forEach(({ group, id }) => {
        if (countForOption(group, id) > 0 || (state.filters[group] || []).includes(id)) {
          quick.append(filterButton(group, id, false));
        }
      });
    }

    function availableGroups() {
      const groups = catalog.tagGroups
        .slice()
        .sort((left, right) => left.order - right.order)
        .filter((group) => groupOptions(group.id).length);
      if (core.hasAudienceContext(state)) {
        groups.push({ id: "importance", label: "Recommendation level", order: 110 });
        groups.push({ id: "purpose", label: "Recommendation purpose", order: 120 });
      }
      return groups.filter((group) => groupOptions(group.id).length);
    }

    function renderFilterPanel() {
      filterPanel.replaceChildren();
      availableGroups().forEach((group) => {
        const fieldset = make("fieldset", "addon-filter-group");
        fieldset.dataset.filterGroup = group.id;
        fieldset.append(make("legend", "", group.label));
        const row = make("div", "addon-chip-row");
        groupOptions(group.id).forEach((id) => row.append(filterButton(group.id, id, true)));
        fieldset.append(row);
        filterPanel.append(fieldset);
      });
    }

    function renderActiveFilters() {
      activeFilters.replaceChildren();
      const entries = [];
      Object.entries(state.filters || {}).forEach(([group, values]) => {
        values.forEach((id) => entries.push({ group, id, label: labelFor(group, id) }));
      });
      if (state.query.trim()) entries.unshift({ group: "query", id: "query", label: `Search: ${state.query.trim()}` });
      activeArea.hidden = entries.length === 0;
      entries.forEach((entry) => {
        const button = make("button", "addon-active-chip", `${entry.label} ×`);
        button.type = "button";
        button.setAttribute("aria-label", `Remove ${entry.label}`);
        button.addEventListener("click", () => {
          if (entry.group === "query") {
            state.query = "";
            input.value = "";
            updateUrl("push");
            render();
          } else toggleFilter(entry.group, entry.id, true);
        });
        activeFilters.append(button);
      });
    }

    function recommendationBadge(recommendation) {
      if (!recommendation) return null;
      const importance = importanceMap.get(recommendation.importance);
      const purposes = recommendation.purposes.map((id) => purposeMap.get(id)).filter(Boolean);
      const badge = make("span", `addon-badge addon-badge-${recommendation.importance}`);
      const purposeText = purposes.map((purpose) => purpose.label).join(" / ");
      badge.textContent = `${importance?.icon || ""} ${importance?.label || titleCase(recommendation.importance)} · ${purposeText}`.trim();
      return badge;
    }

    function compatibilityBadge(addon) {
      const compatibility = addon.compatibility;
      if (compatibility.maintenanceState === "old-unmaintained" || !compatibility.verifiedDownload) {
        return make("span", "addon-badge addon-badge-warning", "! Old / verify exact version");
      }
      return null;
    }

    function targetedSetupLabel(addon) {
      const labels = [];
      (addon.customizations || []).forEach((record) => {
        const classes = (record.audience.classes || []).map((id) => labelFor("class", id));
        const specs = (record.audience.specs || []).map((id) => labelFor("specialization", id));
        const combined = [...specs, ...classes].join(" ").trim();
        if (combined && !labels.includes(combined)) labels.push(combined);
      });
      return labels.length ? `Targeted setups: ${labels.join(", ")}` : "";
    }

    function renderCard(addon) {
      const recommendation = addon._recommendation || core.recommendationFor(addon, state, catalog);
      const card = make("article", "addon-card");
      card.dataset.addonId = addon.id;

      const head = make("div", "addon-card-head");
      const icon = make("img", "addon-icon");
      icon.src = iconPath(addon);
      icon.alt = addon.icon.alt;
      icon.width = 52;
      icon.height = 52;
      const titleWrap = make("div", "addon-title-wrap");
      titleWrap.append(make("h2", "", addon.name));
      if (!recommendation) {
        const targeted = targetedSetupLabel(addon);
        if (targeted) titleWrap.append(make("div", "addon-targeted", targeted));
      }
      head.append(icon, titleWrap);
      card.append(head);

      const badgeRow = make("div", "addon-badge-row");
      const recBadge = recommendationBadge(recommendation);
      const compatBadge = compatibilityBadge(addon);
      if (recBadge) badgeRow.append(recBadge);
      if (compatBadge) badgeRow.append(compatBadge);
      if (badgeRow.childElementCount) card.append(badgeRow);
      else card.append(make("div", "addon-badge-row"));

      card.append(make("p", "addon-card-summary", recommendation?.summary || addon.summary));

      const tags = make("div", "addon-card-tags");
      addon.featuredTags.slice(0, 3).forEach((id) => tags.append(make("span", "addon-card-tag", labelFor(tagMap.get(id)?.group || "", id))));
      const extra = Math.max(0, addon.tags.length - Math.min(3, addon.featuredTags.length));
      if (extra) tags.append(make("span", "addon-card-tag", `+${extra} more`));
      card.append(tags);

      const actions = make("div", "addon-card-actions");
      const details = make("button", "addon-details-button", "Details");
      details.type = "button";
      details.setAttribute("aria-haspopup", "dialog");
      details.addEventListener("click", () => openDialog(addon.id, details, true));
      const download = make("a", "addon-download-link", "Download ↗");
      download.href = addon.download.url;
      download.target = "_blank";
      download.rel = "noopener";
      download.setAttribute("aria-label", `Download ${addon.name} from ${addon.download.source} (opens in a new tab)`);
      actions.append(details, download);
      card.append(actions);
      return card;
    }

    function renderResults() {
      const results = core.filterAndSort(catalog.addons, state, catalog);
      grid.replaceChildren();
      results.forEach((addon) => grid.append(renderCard(addon)));
      grid.hidden = results.length === 0;
      empty.hidden = results.length !== 0;
      const noun = results.length === 1 ? "addon" : "addons";
      count.textContent = `${results.length} ${noun}${state.query.trim() ? ` matching “${state.query.trim()}”` : ""}`;
      const context = core.contextDetails(state, catalog);
      contextBanner.hidden = !context.label;
      contextBanner.replaceChildren();
      if (context.label) {
        contextBanner.append(make("strong", "", `Showing recommendations for ${context.label}`));
        if (context.note) contextBanner.append(make("span", "addon-context-note", context.note));
      }
    }

    function statusText(addon) {
      const compatibility = addon.compatibility;
      if (compatibility.maintenanceState === "old-unmaintained") return "Old / unmaintained";
      if (!compatibility.verifiedDownload) return "Verify exact version";
      if (compatibility.serverSensitive) return "Verified download; server-sensitive";
      return "Verified 3.3.5 download";
    }

    function dialogSection(title, items, ordered) {
      if (!items || !items.length) return null;
      const section = make("section", "addon-dialog-section");
      section.append(make("h3", "", title));
      appendList(section, items, ordered);
      return section;
    }

    function renderCustomization(record, heading) {
      const wrapper = make("div", "addon-dialog-section");
      wrapper.append(make("h3", "", heading || record.title));
      wrapper.append(make("p", "addon-dialog-callout", record.summary));
      if (record.setup?.length) {
        const section = make("div", "addon-dialog-section");
        section.append(make("h3", "", "Targeted setup"));
        appendList(section, record.setup, true);
        wrapper.append(section);
      }
      const does = dialogSection("What this setup helps with", record.does, false);
      const doesNot = dialogSection("What this setup cannot decide", record.doesNot, false);
      if (does) wrapper.append(does);
      if (doesNot) wrapper.append(doesNot);
      (record.notes || []).forEach((note) => wrapper.append(make("p", "addon-dialog-callout addon-dialog-warning", note)));
      return wrapper;
    }

    function renderModuleGroups(addon) {
      if (!Array.isArray(addon.moduleGroups) || !addon.moduleGroups.length) return null;
      const total = addon.moduleGroups.reduce((sum, group) => sum + (group.items || []).length, 0);
      const details = make("details", "addon-module-map");
      details.append(make("summary", "", `Suite module map (${total})`));
      const inner = make("div", "addon-module-map-inner");
      addon.moduleGroups.forEach((group) => {
        const section = make("section", "addon-module-group");
        section.append(make("h3", "", `${group.label} (${(group.items || []).length})`));
        const list = make("dl", "addon-module-list");
        (group.items || []).forEach((item) => {
          list.append(make("dt", "", item.name), make("dd", "", item.description));
        });
        section.append(list);
        inner.append(section);
      });
      details.append(inner);
      return details;
    }

    function renderDialog(addon) {
      dialogContent.replaceChildren();
      const recommendation = core.recommendationFor(addon, state, catalog);
      const customization = core.customizationFor(addon, state, catalog);
      const context = core.contextLabel(state, catalog);

      const header = make("div", "addon-dialog-header");
      const icon = make("img", "addon-icon");
      icon.src = iconPath(addon);
      icon.alt = addon.icon.alt;
      icon.width = 58;
      icon.height = 58;
      const titleWrap = make("div");
      const title = make("h2", "addon-dialog-title", addon.name);
      title.id = "addon-dialog-title";
      titleWrap.append(title);
      titleWrap.append(make("div", "addon-source-meta", `Reviewed ${addon.compatibility.lastReviewed}`));
      header.append(icon, titleWrap);
      dialogContent.append(header);
      dialogContent.append(make("p", "addon-dialog-summary", recommendation?.summary || addon.summary));

      const badges = make("div", "addon-badge-row");
      const recBadge = recommendationBadge(recommendation);
      const compatBadge = compatibilityBadge(addon);
      if (recBadge) badges.append(recBadge);
      if (compatBadge) badges.append(compatBadge);
      dialogContent.append(badges);

      const actions = make("div", "addon-dialog-actions");
      const download = make("a", "addon-dialog-download", `Download from ${addon.download.source} ↗`);
      download.href = addon.download.url;
      download.target = "_blank";
      download.rel = "noopener";
      actions.append(download);
      (addon.relatedGuides || []).forEach((guide) => {
        const link = make("a", "addon-download-link", guide.label);
        link.href = `../${guide.href}`;
        actions.append(link);
      });
      dialogContent.append(actions);
      dialogContent.append(make("p", "addon-source-meta", `${addon.download.source} · ${addon.compatibility.downloadVersion} · ${addon.download.notes}`));

      if (recommendation) {
        const importance = importanceMap.get(recommendation.importance)?.label || titleCase(recommendation.importance);
        const rec = make("section", "addon-dialog-section");
        rec.append(make("h3", "", `Why this is ${importance.toLowerCase()} for ${context || "this context"}`));
        rec.append(make("p", "addon-dialog-callout", recommendation.reason));
        dialogContent.append(rec);
      }

      const does = dialogSection("What it does", addon.does, false);
      const doesNot = dialogSection("What it does not do", addon.doesNot, false);
      const setup = dialogSection("General setup", addon.generalSetup, true);
      if (does) dialogContent.append(does);
      if (doesNot) dialogContent.append(doesNot);
      if (setup) dialogContent.append(setup);

      if (customization) dialogContent.append(renderCustomization(customization, customization.title));
      const otherCustomizations = (addon.customizations || []).filter((record) => record !== customization);
      if (otherCustomizations.length) {
        const details = make("details");
        const selectedContext = core.hasAudienceContext(state);
        details.append(make("summary", "", selectedContext ? "Show other class/spec setups" : "Show targeted setups"));
        const inner = make("div");
        otherCustomizations.forEach((record) => inner.append(renderCustomization(record, record.title)));
        details.append(inner);
        dialogContent.append(details);
      }

      const moduleMap = renderModuleGroups(addon);
      if (moduleMap) dialogContent.append(moduleMap);

      const compatibility = make("section", "addon-dialog-section");
      compatibility.append(make("h3", "", "Compatibility and server notes"));
      const meta = make("div", "addon-dialog-meta-grid");
      const metaItems = [
        ["WotLK client", addon.compatibility.client],
        ["Download", addon.compatibility.verifiedDownload ? "3.3.5 listing verified" : "Exact archive not verified"],
        ["Maintenance", COMPATIBILITY_LABELS[addon.compatibility.maintenanceState] || titleCase(addon.compatibility.maintenanceState)],
        ["Hellscream testing", addon.compatibility.hellscreamTested ? "Tested" : "Not yet tested"],
        ["Server-sensitive", addon.compatibility.serverSensitive ? "Yes" : "No"],
        ["Status", statusText(addon)]
      ];
      metaItems.forEach(([label, value]) => {
        const item = make("div", "addon-dialog-meta");
        item.append(make("strong", "", label), make("span", "", value));
        meta.append(item);
      });
      compatibility.append(meta);
      (addon.compatibility.notes || []).forEach((note) => compatibility.append(make("p", addon.compatibility.serverSensitive || addon.compatibility.maintenanceState === "old-unmaintained" ? "addon-dialog-callout addon-dialog-warning" : "addon-dialog-callout", note)));
      dialogContent.append(compatibility);

      if (addon.screenshots?.length) {
        const details = make("details");
        details.append(make("summary", "", `Media (${addon.screenshots.length})`));
        const inner = make("div");
        addon.screenshots.forEach((shot) => {
          const image = make("img");
          image.src = `../${shot.path}`;
          image.alt = shot.alt;
          image.loading = "lazy";
          inner.append(image, make("p", "addon-source-meta", shot.caption || ""));
        });
        details.append(inner);
        dialogContent.append(details);
      }

      if (addon.videos?.length) {
        const details = make("details");
        details.append(make("summary", "", `Player-made guides (${addon.videos.length})`));
        const inner = make("div");
        addon.videos.forEach((video) => {
          const link = make("a", "addon-download-link", `▶ ${video.title} ↗`);
          link.href = video.url;
          link.target = "_blank";
          link.rel = "noopener";
          inner.append(link, make("p", "addon-source-meta", [video.creator, video.duration, video.scope, video.compatibilityNote].filter(Boolean).join(" · ")));
        });
        details.append(inner);
        dialogContent.append(details);
      }

      const tags = make("details");
      tags.append(make("summary", "", `Full tag list (${addon.tags.length})`));
      const tagList = make("div", "addon-all-tags");
      addon.tags.forEach((id) => tagList.append(make("span", "addon-card-tag", tagMap.get(id)?.label || titleCase(id))));
      const inner = make("div");
      inner.append(tagList);
      tags.append(inner);
      dialogContent.append(tags);
    }

    function openDialog(addonId, button, pushHistory) {
      const addon = addonMap.get(addonId);
      if (!addon) return;
      originButton = button || document.querySelector(`[data-addon-id="${CSS.escape(addonId)}"] .addon-details-button`);
      originAddonId = addonId;
      state.addon = addonId;
      if (pushHistory) {
        updateUrl("push");
        dialogUrlWasPushed = true;
      } else {
        updateUrl("replace");
        dialogUrlWasPushed = false;
      }
      renderDialog(addon);
      if (!dialog.open) dialog.showModal();
      dialogClose.focus();
    }

    function focusOrigin(addonId) {
      const target = document.querySelector(`[data-addon-id="${CSS.escape(addonId)}"] .addon-details-button`);
      if (target) target.focus();
    }

    function closeDialog(updateHistory) {
      const focusAddonId = originAddonId || state.addon;
      if (dialog.open) dialog.close();
      state.addon = "";
      if (updateHistory) {
        if (dialogUrlWasPushed) {
          pendingFocusAddonId = focusAddonId;
          global.history.back();
        } else {
          updateUrl("replace");
          focusOrigin(focusAddonId);
        }
      } else {
        focusOrigin(focusAddonId);
      }
      dialogUrlWasPushed = false;
    }

    function syncDialogFromState() {
      if (state.addon && addonMap.has(state.addon)) {
        const currentTitle = dialogContent.querySelector(".addon-dialog-title")?.textContent;
        const addon = addonMap.get(state.addon);
        if (!dialog.open || currentTitle !== addon.name) openDialog(state.addon, null, false);
      } else if (dialog.open) closeDialog(false);
    }

    function render() {
      renderQuickFilters();
      renderFilterPanel();
      renderActiveFilters();
      renderResults();
      syncDialogFromState();
    }

    input.value = state.query;
    sort.value = state.sort;
    input.addEventListener("input", () => {
      state.query = input.value;
      state.addon = "";
      updateUrl("replace");
      render();
    });
    sort.addEventListener("change", () => {
      state.sort = sort.value === "name" ? "name" : "smart";
      updateUrl("push");
      render();
    });
    filterToggle.addEventListener("click", () => {
      const expanded = filterToggle.getAttribute("aria-expanded") === "true";
      filterToggle.setAttribute("aria-expanded", String(!expanded));
      filterPanel.hidden = expanded;
    });
    clearAll.addEventListener("click", () => clearFilters(true));
    emptyClear.addEventListener("click", () => clearFilters(true));
    dialogClose.addEventListener("click", () => closeDialog(true));
    dialog.addEventListener("cancel", (event) => {
      event.preventDefault();
      closeDialog(true);
    });
    dialog.addEventListener("click", (event) => {
      if (event.target === dialog) closeDialog(true);
    });
    global.addEventListener("popstate", () => {
      handlingHistory = true;
      state = core.parseUrlState(global.location.href, catalog);
      input.value = state.query;
      sort.value = state.sort;
      render();
      if (pendingFocusAddonId) {
        focusOrigin(pendingFocusAddonId);
        pendingFocusAddonId = "";
      }
      handlingHistory = false;
    });

    render();
  }

  document.addEventListener("DOMContentLoaded", initializeCatalog);
})(window);
