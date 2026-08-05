(function (global) {
  "use strict";

  function normalize(value) {
    return String(value || "")
      .normalize("NFKD")
      .replace(/[\u0300-\u036f]/g, "")
      .toLowerCase()
      .replace(/[’']/g, "")
      .replace(/&/g, " and ")
      .replace(/[^a-z0-9]+/g, " ")
      .trim();
  }

  function slugify(value) {
    return normalize(value).replace(/\s+/g, "-");
  }

  function headingFor(section) {
    return Array.from(section.children).find((child) => child.tagName === "H2") || null;
  }

  function headingText(heading) {
    const clone = heading.cloneNode(true);
    clone.querySelectorAll(".ah-back-to-top, .ah-back-to-parent, .ah-category-chip-nav").forEach((node) => node.remove());
    return clone.textContent.trim();
  }

  function matchesPatterns(title, patterns) {
    return (patterns || []).some((pattern) => new RegExp(pattern, "i").test(title));
  }

  function makeChip(label, targetId) {
    const link = document.createElement("a");
    link.className = "ah-category-chip";
    link.href = `#${targetId}`;
    link.textContent = label;
    return link;
  }

  function makeChipNav(label, nodes) {
    const nav = document.createElement("nav");
    nav.className = "ah-category-chip-nav";
    nav.setAttribute("aria-label", label);
    nodes.forEach((node) => nav.append(makeChip(node.label, node.target.id)));
    return nav;
  }

  function addBackControl(section, parentNode) {
    if (!parentNode || !section) return;
    const heading = headingFor(section);
    if (!heading || heading.querySelector(".ah-back-to-parent")) return;
    const top = heading.querySelector(".ah-back-to-top");
    const back = document.createElement("a");
    back.className = "ah-back-to-parent";
    back.href = `#${parentNode.target.id}`;
    back.setAttribute("aria-label", `Back to ${parentNode.label}`);
    back.textContent = `← ${parentNode.label}`;
    if (top) heading.insertBefore(back, top);
    else heading.append(back);
  }

  function initialize() {
    const manifest = global.AH_GUIDE_NAVIGATION;
    const guideId = document.body?.dataset.ahGuide;
    const guide = manifest?.guides?.[guideId];
    const majorNav = document.querySelector("[data-ah-major-nav]");
    if (!guide || !majorNav) return;

    const claimed = new Set();
    const realSections = Array.from(document.querySelectorAll("section.common"))
      .filter((section) => !section.classList.contains("ah-guide-search-section"))
      .filter((section) => !section.classList.contains("ah-category-banner"))
      .map((section) => {
        const heading = headingFor(section);
        if (!heading) return null;
        const title = headingText(heading);
        if (!section.id) section.id = `ah-section-${slugify(title)}`;
        return { section, heading, title };
      })
      .filter(Boolean);

    function createBanner(node, beforeSection, parentNode) {
      const section = document.createElement("section");
      section.className = "common ah-category-banner";
      section.id = node.id;
      section.dataset.ahCategory = node.id;

      const heading = document.createElement("h2");
      heading.className = "ah-category-heading";
      const title = document.createElement("span");
      title.className = "ah-category-title";
      title.textContent = node.label;
      heading.append(title);
      if (parentNode) {
        const back = document.createElement("a");
        back.className = "ah-back-to-parent";
        back.href = `#${parentNode.target.id}`;
        back.setAttribute("aria-label", `Back to ${parentNode.label}`);
        back.textContent = `← ${parentNode.label}`;
        heading.append(back);
      }
      const top = document.createElement("a");
      top.className = "ah-back-to-top";
      top.href = "#top";
      top.setAttribute("aria-label", "Back to top");
      top.textContent = "↑ Top";
      heading.append(top);
      section.append(heading);
      beforeSection.parentNode.insertBefore(section, beforeSection);
      return section;
    }

    function resolveNode(config, parentNode) {
      const node = { id: config.id, label: config.label, target: null, children: [] };
      if (Array.isArray(config.children) && config.children.length) {
        node.children = config.children
          .map((child) => resolveNode(child, null))
          .filter(Boolean);
        if (!node.children.length) return null;
        const first = node.children[0].target;
        node.target = createBanner(node, first, parentNode);
        node.target.append(makeChipNav(`${node.label} subcategories`, node.children));
        node.children.forEach((child) => addBackControl(child.target, node));
        return node;
      }

      const matches = realSections.filter((entry) =>
        !claimed.has(entry.section) && matchesPatterns(entry.title, config.patterns)
      );
      if (!matches.length) return null;
      matches.forEach((entry) => {
        claimed.add(entry.section);
        entry.section.dataset.ahNavCovered = "true";
      });
      if (matches.length === 1) {
        node.target = matches[0].section;
        addBackControl(node.target, parentNode);
        return node;
      }

      node.target = createBanner(node, matches[0].section, parentNode);
      const leaves = matches.map((entry) => ({
        id: entry.section.id,
        label: entry.title,
        target: entry.section
      }));
      node.target.append(makeChipNav(`${node.label} subcategories`, leaves));
      leaves.forEach((leaf) => addBackControl(leaf.target, node));
      return node;
    }

    const majors = guide.navigation.map((node) => resolveNode(node, null)).filter(Boolean);
    const label = document.createElement("span");
    label.className = "ah-category-chip-label";
    label.textContent = "Jump to category";
    majorNav.replaceChildren(label, ...majors.map((node) => makeChip(node.label, node.target.id)));

    const categoryPrefix = "#ah-category=";
    if (global.location.hash.startsWith(categoryPrefix)) {
      const requested = decodeURIComponent(global.location.hash.slice(categoryPrefix.length));
      const target = document.getElementById(requested);
      if (target) global.requestAnimationFrame(() => target.scrollIntoView({ block: "start" }));
    }
  }

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", initialize);
  else initialize();
}(window));
