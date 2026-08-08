(function () {
  "use strict";

  const form = document.querySelector("[data-container-filters]");
  const tbody = document.querySelector("[data-container-rows]");
  const status = document.getElementById("container-result-count");
  const empty = document.getElementById("container-empty-state");
  const activeFilters = document.getElementById("container-active-filters");
  const activeFilterList = document.getElementById("container-active-filter-list");
  if (!form || !tbody || !status || !empty || !activeFilters || !activeFilterList) return;

  const controls = {
    search: document.getElementById("container-search"),
    source: document.getElementById("container-source"),
    expansion: document.getElementById("container-expansion"),
    mobileSort: document.getElementById("container-mobile-sort")
  };
  const rows = Array.from(tbody.querySelectorAll("[data-container-row]"));
  const restrictionChips = Array.from(form.querySelectorAll("[data-container-restriction]"));
  const sortHeadings = Array.from(document.querySelectorAll("[data-container-sort-key]"));
  const moreFilters = form.querySelector(".container-more-filters");
  const defaultDirections = {
    name: "asc",
    slots: "desc",
    type: "asc",
    expansion: "desc",
    source: "asc",
    quick: "desc",
    target: "desc",
    high: "desc"
  };
  const expansionRanks = { classic: 1, outland: 2, wrath: 3 };
  let sortKey = "slots";
  let sortDirection = "desc";

  function normalize(value) {
    return String(value || "")
      .normalize("NFKD")
      .replace(/[\u0300-\u036f]/g, "")
      .toLowerCase()
      .replace(/[’']/g, "")
      .replace(/[^a-z0-9]+/g, " ")
      .trim();
  }

  function number(row, key, optional) {
    const raw = row.dataset[key];
    if (optional && !raw) return null;
    return Number.parseInt(raw || "0", 10) || 0;
  }

  function compareStrings(left, right, direction) {
    const order = left.localeCompare(right);
    return direction === "asc" ? order : -order;
  }

  function compareNumbers(left, right, direction) {
    if (left === null && right === null) return 0;
    if (left === null) return 1;
    if (right === null) return -1;
    return direction === "asc" ? left - right : right - left;
  }

  function compareRows(left, right) {
    const normalizedLeftName = normalize(left.dataset.name);
    const normalizedRightName = normalize(right.dataset.name);
    const nameOrder = normalizedLeftName.localeCompare(normalizedRightName);
    let order = 0;
    if (sortKey === "name") order = compareStrings(normalizedLeftName, normalizedRightName, sortDirection);
    if (sortKey === "slots") order = compareNumbers(number(left, "capacity"), number(right, "capacity"), sortDirection);
    if (sortKey === "type") order = compareStrings(left.dataset.subtype, right.dataset.subtype, sortDirection);
    if (sortKey === "expansion") {
      order = compareNumbers(expansionRanks[left.dataset.expansion], expansionRanks[right.dataset.expansion], sortDirection);
    }
    if (sortKey === "source") order = compareStrings(left.dataset.source, right.dataset.source, sortDirection);
    if (sortKey === "quick") order = compareNumbers(number(left, "quick"), number(right, "quick"), sortDirection);
    if (sortKey === "target") order = compareNumbers(number(left, "target"), number(right, "target"), sortDirection);
    if (sortKey === "high") order = compareNumbers(number(left, "high", true), number(right, "high", true), sortDirection);
    if (order) return order;
    if (sortKey === "slots") {
      return compareNumbers(number(left, "target"), number(right, "target"), "desc") || nameOrder;
    }
    return nameOrder;
  }

  function selectedRestrictions() {
    return new Set(
      restrictionChips
        .filter((chip) => chip.getAttribute("aria-pressed") === "true")
        .map((chip) => chip.dataset.containerRestriction)
    );
  }

  function matchesBaseFilters(row) {
    const query = normalize(controls.search.value);
    return (!query || normalize(row.dataset.name).includes(query)) &&
      (!controls.source.value || row.dataset.source === controls.source.value) &&
      (!controls.expansion.value || row.dataset.expansion === controls.expansion.value);
  }

  function updateChipCounts() {
    restrictionChips.forEach((chip) => {
      const count = rows.filter((row) =>
        matchesBaseFilters(row) && row.dataset.restriction === chip.dataset.containerRestriction
      ).length;
      const counter = chip.querySelector("[data-container-chip-count]");
      if (counter) counter.textContent = String(count);
    });
  }

  function cleanOptionLabel(control) {
    return control.selectedOptions[0]?.textContent.replace(/\s+\(\d+\)$/, "") || "";
  }

  function addActiveFilter(label, type, value) {
    const button = document.createElement("button");
    button.type = "button";
    button.className = "container-active-filter";
    button.dataset.containerRemoveFilter = type;
    button.dataset.filterValue = value;
    button.textContent = `${label} ×`;
    button.setAttribute("aria-label", `Remove ${label} filter`);
    activeFilterList.appendChild(button);
  }

  function updateActiveFilters(restrictions) {
    activeFilterList.replaceChildren();
    restrictionChips
      .filter((chip) => restrictions.has(chip.dataset.containerRestriction))
      .forEach((chip) => {
        addActiveFilter(
          chip.querySelector("span")?.textContent || chip.textContent,
          "restriction",
          chip.dataset.containerRestriction
        );
      });
    if (controls.source.value) addActiveFilter(cleanOptionLabel(controls.source), "source", controls.source.value);
    if (controls.expansion.value) addActiveFilter(cleanOptionLabel(controls.expansion), "expansion", controls.expansion.value);
    activeFilters.hidden = activeFilterList.childElementCount === 0;
  }

  function updateSortControls() {
    const sortValue = `${sortKey}-${sortDirection}`;
    if (controls.mobileSort.value !== sortValue) controls.mobileSort.value = sortValue;
    sortHeadings.forEach((button) => {
      const heading = button.closest("th");
      const active = button.dataset.containerSortKey === sortKey;
      heading.setAttribute("aria-sort", active ? (sortDirection === "asc" ? "ascending" : "descending") : "none");
      const indicator = button.querySelector("span");
      if (indicator) indicator.textContent = active ? (sortDirection === "asc" ? "↑" : "↓") : "↕";
    });
  }

  function setSort(nextKey, nextDirection) {
    sortKey = nextKey;
    sortDirection = nextDirection;
    updateSortControls();
    apply();
  }

  function apply() {
    const restrictions = selectedRestrictions();
    let shown = 0;

    rows.sort(compareRows).forEach((row) => {
      const matches = matchesBaseFilters(row) &&
        (restrictions.size === 0 || restrictions.has(row.dataset.restriction));
      row.hidden = !matches;
      if (matches) shown += 1;
      tbody.appendChild(row);
    });

    status.textContent = `Showing ${shown} of ${rows.length} containers`;
    empty.hidden = shown !== 0;
    updateChipCounts();
    updateActiveFilters(restrictions);
  }

  restrictionChips.forEach((chip) => {
    chip.addEventListener("click", () => {
      chip.setAttribute("aria-pressed", chip.getAttribute("aria-pressed") === "true" ? "false" : "true");
      apply();
    });
  });
  sortHeadings.forEach((button) => {
    button.addEventListener("click", () => {
      const nextKey = button.dataset.containerSortKey;
      const nextDirection = nextKey === sortKey
        ? (sortDirection === "asc" ? "desc" : "asc")
        : defaultDirections[nextKey];
      setSort(nextKey, nextDirection);
    });
  });
  controls.mobileSort.addEventListener("change", () => {
    const separator = controls.mobileSort.value.lastIndexOf("-");
    setSort(controls.mobileSort.value.slice(0, separator), controls.mobileSort.value.slice(separator + 1));
  });
  activeFilterList.addEventListener("click", (event) => {
    const button = event.target.closest("[data-container-remove-filter]");
    if (!button) return;
    if (button.dataset.containerRemoveFilter === "restriction") {
      const chip = restrictionChips.find((candidate) =>
        candidate.dataset.containerRestriction === button.dataset.filterValue
      );
      if (chip) chip.setAttribute("aria-pressed", "false");
    } else {
      controls[button.dataset.containerRemoveFilter].value = "";
    }
    apply();
  });
  form.addEventListener("input", apply);
  form.addEventListener("change", apply);
  form.addEventListener("reset", () => {
    restrictionChips.forEach((chip) => chip.setAttribute("aria-pressed", "false"));
    sortKey = "slots";
    sortDirection = "desc";
    if (moreFilters) moreFilters.open = false;
    window.setTimeout(() => {
      updateSortControls();
      apply();
    }, 0);
  });
  updateSortControls();
  apply();
})();
