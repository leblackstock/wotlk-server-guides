(function () {
  "use strict";

  function initFilters() {
    const panel = document.querySelector("[data-spec-filters]");
    if (!panel) return;

    const buttons = [...panel.querySelectorAll("[data-filter-group]")];
    const notes = [...document.querySelectorAll(".raid-note[data-size]")];
    const encounters = [...document.querySelectorAll(".raid-encounter")];
    const status = panel.querySelector(".filter-status");
    const empty = document.querySelector(".raid-filter-empty");
    const state = { size: "all", difficulty: "all", role: "all" };

    function matches(note, key) {
      return state[key] === "all" || (note.dataset[key] || "").split(" ").includes(state[key]);
    }

    function apply() {
      let shown = 0;
      notes.forEach((note) => {
        note.hidden = !(matches(note, "size") && matches(note, "difficulty") && matches(note, "role"));
        if (!note.hidden) shown += 1;
      });
      encounters.forEach((encounter) => {
        encounter.hidden = ![...encounter.querySelectorAll(".raid-note")].some((note) => !note.hidden);
      });
      if (empty) empty.hidden = shown !== 0;
      if (status) status.textContent = `${shown} Lich King assignment note${shown === 1 ? "" : "s"} shown.`;
    }

    buttons.forEach((button) => {
      button.addEventListener("click", () => {
        const group = button.dataset.filterGroup;
        state[group] = button.dataset.filterValue;
        panel.querySelectorAll(`[data-filter-group="${group}"]`).forEach((candidate) => {
          candidate.setAttribute("aria-pressed", String(candidate === button));
        });
        apply();
      });
    });
    apply();
  }

  function initPlaybookCards() {
    const cards = [...document.querySelectorAll(".spec-card")];
    if (!cards.length) return;

    function showAll() {
      document.body.classList.remove("spec-card-focus");
      cards.forEach((card) => {
        card.hidden = false;
        const header = card.querySelector(".spec-card-header");
        if (header) header.setAttribute("aria-pressed", "false");
      });
    }

    cards.forEach((card) => {
      const header = card.querySelector(".spec-card-header");
      if (!header) return;
      header.tabIndex = 0;
      header.setAttribute("role", "button");
      header.setAttribute("aria-pressed", "false");
      header.setAttribute("aria-label", `${header.querySelector("h3")?.textContent || "Playbook"}: focus or restore all playbooks`);

      function toggle() {
        const isFocused = document.body.classList.contains("spec-card-focus") && !card.hidden;
        if (isFocused) {
          showAll();
        } else {
          document.body.classList.add("spec-card-focus");
          cards.forEach((candidate) => {
            candidate.hidden = candidate !== card;
            const candidateHeader = candidate.querySelector(".spec-card-header");
            if (candidateHeader) candidateHeader.setAttribute("aria-pressed", String(candidate === card));
          });
        }
      }

      header.addEventListener("click", toggle);
      header.addEventListener("keydown", (event) => {
        if (event.key === "Enter" || event.key === " ") {
          event.preventDefault();
          toggle();
        }
      });
    });

    document.addEventListener("keydown", (event) => {
      if (event.key === "Escape" && document.body.classList.contains("spec-card-focus")) showAll();
    });
  }

  function init() {
    initFilters();
    initPlaybookCards();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init, { once: true });
  } else {
    init();
  }
}());
