(function (global) {
  "use strict";

  function directCell(row, column) {
    return Array.from(row.children).find(
      (cell) => cell.matches && cell.matches(`td[data-column="${column}"]`),
    ) || null;
  }

  function collapseTableDetails(table, exceptButton) {
    table.querySelectorAll('.ah-source-notes-toggle[aria-expanded="true"]').forEach((button) => {
      if (button === exceptButton) return;
      button.setAttribute("aria-expanded", "false");
      button.textContent = "Source & notes";
      const detail = document.getElementById(button.getAttribute("aria-controls"));
      if (detail) detail.hidden = true;
    });
  }

  function safeDisplayClone(node) {
    const clone = node.cloneNode(true);
    const elements = [];
    if (clone.nodeType === 1) elements.push(clone);
    if (clone.querySelectorAll) elements.push(...clone.querySelectorAll("*"));
    elements.forEach((element) => {
      element.removeAttribute("id");
      element.removeAttribute("class");
      Array.from(element.attributes).forEach((attribute) => {
        if (attribute.name.startsWith("data-")) element.removeAttribute(attribute.name);
        if (["aria-controls", "aria-describedby", "aria-labelledby", "aria-owns"].includes(attribute.name)) {
          element.removeAttribute(attribute.name);
        }
      });
    });
    return clone;
  }

  function initialize() {
    if (document.body?.dataset.guideSection !== "auction-house") return 0;

    const guideKey = document.body.dataset.ahGuide || "auction-house";
    const rows = Array.from(document.querySelectorAll("table > tbody > tr")).filter(
      (row) => directCell(row, "notes") && (directCell(row, "item") || row.cells[0]),
    );

    let enhanced = 0;
    rows.forEach((row, index) => {
      if (row.dataset.ahSourceNotesReady === "true") return;

      const table = row.closest("table");
      const itemCell = directCell(row, "item") || row.cells[0];
      const notesCell = directCell(row, "notes");
      if (!table || !itemCell || !notesCell) return;

      const itemName = itemCell.querySelector("strong")?.textContent?.trim()
        || itemCell.textContent.replace(/\s+/g, " ").trim()
        || `row ${index + 1}`;
      const detailId = `ah-source-notes-${guideKey}-${index + 1}`;

      const controls = document.createElement("div");
      controls.className = "ah-source-notes-controls";

      const toggle = document.createElement("button");
      toggle.type = "button";
      toggle.className = "ah-source-notes-toggle";
      toggle.textContent = "Source & notes";
      toggle.setAttribute("aria-expanded", "false");
      toggle.setAttribute("aria-controls", detailId);
      controls.append(toggle);
      itemCell.append(controls);

      const detail = document.createElement("tr");
      detail.id = detailId;
      detail.className = "ah-source-notes-detail";
      detail.hidden = true;

      const detailCell = document.createElement("td");
      detailCell.colSpan = row.cells.length;
      detailCell.dataset.column = "source-notes-detail";

      const panel = document.createElement("div");
      panel.className = "ah-source-notes-panel";
      panel.setAttribute("role", "region");
      panel.setAttribute("aria-label", `Source and selling notes for ${itemName}`);

      const heading = document.createElement("div");
      heading.className = "ah-source-notes-panel-heading";
      const title = document.createElement("strong");
      title.textContent = `${itemName} — source and selling notes`;
      heading.append(title);
      panel.append(heading);

      const close = document.createElement("button");
      close.type = "button";
      close.className = "ah-source-notes-close";
      close.textContent = "Close notes";
      panel.append(close);

      const body = document.createElement("div");
      body.className = "ah-source-notes-panel-body";
      Array.from(notesCell.childNodes).forEach((node) => body.append(safeDisplayClone(node)));
      panel.append(body);
      detailCell.append(panel);
      detail.append(detailCell);
      row.after(detail);

      function setExpanded(expanded) {
        toggle.setAttribute("aria-expanded", String(expanded));
        toggle.textContent = expanded ? "Hide notes" : "Source & notes";
        detail.hidden = !expanded;
      }

      toggle.addEventListener("click", () => {
        const expanded = toggle.getAttribute("aria-expanded") === "true";
        if (!expanded) collapseTableDetails(table, toggle);
        setExpanded(!expanded);
      });

      close.addEventListener("click", () => {
        setExpanded(false);
        toggle.focus();
      });

      row.dataset.ahSourceNotesReady = "true";
      table.classList.add("ah-source-notes-ready");
      enhanced += 1;
    });

    return enhanced;
  }

  global.AH_SOURCE_NOTES = Object.freeze({ initialize });
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initialize, { once: true });
  } else {
    initialize();
  }
})(window);
