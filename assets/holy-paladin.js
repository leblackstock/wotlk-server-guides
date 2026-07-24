(function () {
  "use strict";

  function bindFilters() {
    const panel = document.querySelector("[data-holy-filters]");
    if (!panel) return;
    const buttons = Array.from(panel.querySelectorAll("[data-filter-group]"));
    const notes = Array.from(document.querySelectorAll(".raid-note[data-size]"));
    const status = panel.querySelector(".filter-status");
    const empty = document.querySelector(".raid-filter-empty");
    const encounters = Array.from(document.querySelectorAll(".raid-encounter"));
    const state = { size:"all", difficulty:"all", role:"all" };

    function apply() {
      let count = 0;
      notes.forEach(function (note) {
        const sizeOk = state.size === "all" || note.dataset.size.split(" ").includes(state.size);
        const difficultyOk = state.difficulty === "all" || note.dataset.difficulty.split(" ").includes(state.difficulty);
        const roleOk = state.role === "all" || note.dataset.role.split(" ").includes(state.role);
        note.hidden = !(sizeOk && difficultyOk && roleOk);
        if (!note.hidden) count += 1;
      });
      encounters.forEach(function (encounter) {
        const visible = Array.from(encounter.querySelectorAll(".raid-note")).some(function (note) { return !note.hidden; });
        encounter.hidden = !visible;
      });
      if (empty) empty.hidden = count !== 0;
      if (status) status.textContent = count + " encounter note" + (count === 1 ? "" : "s") + " shown.";
    }

    buttons.forEach(function (button) {
      button.addEventListener("click", function () {
        const group = button.dataset.filterGroup;
        state[group] = button.dataset.filterValue;
        panel.querySelectorAll('[data-filter-group="'+group+'"]').forEach(function (peer) {
          peer.setAttribute("aria-pressed", String(peer === button));
        });
        apply();
      });
    });
    apply();
  }

  function bindPlaybookFocus() {
    const cards = Array.from(document.querySelectorAll(".heal-card"));
    if (!cards.length) return;
    cards.forEach(function (card) {
      const header = card.querySelector(".heal-card-header");
      if (!header) return;
      header.tabIndex = 0;
      header.setAttribute("role","button");
      header.setAttribute("aria-label","Focus this healing situation");
      function focusCard() {
        const already = document.body.classList.contains("holy-card-focus") && !card.hidden;
        document.body.classList.toggle("holy-card-focus", !already);
        cards.forEach(function (peer) { peer.hidden = !already && peer !== card; });
        if (already) card.scrollIntoView({block:"nearest"});
      }
      header.addEventListener("click", focusCard);
      header.addEventListener("keydown", function (event) {
        if (event.key === "Enter" || event.key === " ") { event.preventDefault(); focusCard(); }
      });
    });
  }

  function init() { bindFilters(); bindPlaybookFocus(); }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", init, {once:true}); else init();
}());
