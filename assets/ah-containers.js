(function () {
  "use strict";

  const form = document.querySelector("[data-container-filters]");
  const tbody = document.querySelector("[data-container-rows]");
  const status = document.getElementById("container-result-count");
  const empty = document.getElementById("container-empty-state");
  if (!form || !tbody || !status || !empty) return;

  const controls = {
    search: document.getElementById("container-search"),
    category: document.getElementById("container-category"),
    subtype: document.getElementById("container-subtype"),
    source: document.getElementById("container-source"),
    expansion: document.getElementById("container-expansion"),
    minSlots: document.getElementById("container-min-slots"),
    sort: document.getElementById("container-sort")
  };
  const rows = Array.from(tbody.querySelectorAll("[data-container-row]"));

  function normalize(value) {
    return String(value || "")
      .normalize("NFKD")
      .replace(/[\u0300-\u036f]/g, "")
      .toLowerCase()
      .replace(/[’']/g, "")
      .replace(/[^a-z0-9]+/g, " ")
      .trim();
  }

  function number(row, key) {
    return Number.parseInt(row.dataset[key] || "0", 10) || 0;
  }

  function compareRows(left, right, sort) {
    const nameOrder = left.dataset.name.localeCompare(right.dataset.name);
    if (sort === "target-desc") return number(right, "target") - number(left, "target") || nameOrder;
    if (sort === "target-asc") return number(left, "target") - number(right, "target") || nameOrder;
    if (sort === "name-asc") return nameOrder;
    return number(right, "capacity") - number(left, "capacity") ||
      number(right, "target") - number(left, "target") || nameOrder;
  }

  function apply() {
    const query = normalize(controls.search.value);
    const category = controls.category.value;
    const subtype = controls.subtype.value;
    const source = controls.source.value;
    const expansion = controls.expansion.value;
    const minSlots = Number.parseInt(controls.minSlots.value || "0", 10) || 0;
    const sort = controls.sort.value;
    let shown = 0;

    rows.sort((left, right) => compareRows(left, right, sort)).forEach((row) => {
      const matches = (!query || normalize(row.dataset.name).includes(query)) &&
        (!category || row.dataset.category === category) &&
        (!subtype || row.dataset.subtype === subtype) &&
        (!source || row.dataset.source === source) &&
        (!expansion || row.dataset.expansion === expansion) &&
        number(row, "capacity") >= minSlots;
      row.hidden = !matches;
      if (matches) shown += 1;
      tbody.appendChild(row);
    });

    status.textContent = `Showing ${shown} of ${rows.length}`;
    empty.hidden = shown !== 0;
  }

  form.addEventListener("input", apply);
  form.addEventListener("change", apply);
  form.addEventListener("reset", () => window.setTimeout(apply, 0));
  apply();
})();
