import fs from "node:fs";
import path from "node:path";

const TYPE_KEYS = new Map([
  ["item", "items"],
  ["spell", "spells"],
  ["skill", "skills"]
]);
const ICON_RE = /^[a-z0-9_]+$/;

export function resolveFromRoot(root, file) {
  return path.isAbsolute(file) ? file : path.join(root, file);
}

export function normalizeRegistry(raw, source = "entity registry") {
  const registry = {
    schemaVersion: raw.schemaVersion ?? 1,
    className: String(raw.className ?? "").trim(),
    classSlug: String(raw.classSlug ?? "").trim(),
    items: [],
    spells: [],
    skills: []
  };

  const problems = [];
  for (const [type, key] of TYPE_KEYS) {
    const rows = Array.isArray(raw[key]) ? raw[key] : [];
    rows.forEach((row, index) => {
      const id = Number(row.id);
      const names = Array.isArray(row.names)
        ? row.names.map((name) => String(name).trim()).filter(Boolean)
        : row.name
          ? [String(row.name).trim()]
          : [];
      const icon = row.icon ? String(row.icon).trim().replace(/\.jpg$/i, "") : "";
      const category = row.category ? String(row.category).trim() : "";

      if (!Number.isInteger(id) || id <= 0) {
        problems.push(`${source}: ${key}[${index}] must have a positive integer id.`);
      }
      if (!names.length) {
        problems.push(`${source}: ${key}[${index}] must have at least one exact name.`);
      }
      if (icon && !ICON_RE.test(icon)) {
        problems.push(`${source}: ${key}[${index}] icon must be a Wow icon filename without .jpg.`);
      }
      registry[key].push({ type, id, names, icon, category });
    });
  }

  const seen = new Map();
  for (const row of [...registry.items, ...registry.spells]) {
    for (const name of row.names) {
      const key = name.toLowerCase();
      const prior = seen.get(key);
      if (prior && (prior.type !== row.type || prior.id !== row.id)) {
        problems.push(`${source}: duplicate name "${name}" points to both ${prior.type}=${prior.id} and ${row.type}=${row.id}.`);
      } else {
        seen.set(key, row);
      }
    }
  }

  return { registry, problems };
}

export function loadRegistry(file) {
  const raw = JSON.parse(fs.readFileSync(file, "utf8"));
  const { registry, problems } = normalizeRegistry(raw, file);
  if (problems.length) {
    throw new Error(problems.join("\n"));
  }
  return registry;
}

export function registryEntities(registry) {
  return [...registry.items, ...registry.spells, ...registry.skills];
}

export function registryNameMap(registry) {
  const map = new Map();
  for (const entity of registryEntities(registry)) {
    for (const name of entity.names) map.set(name.toLowerCase(), entity);
  }
  return map;
}

function js(value) {
  return JSON.stringify(value);
}

export function buildTooltipScript(registry, options = {}) {
  const classSlug = options.classSlug || registry.classSlug || "spec-guide";
  const rows = registryEntities(registry).map((entity) => ({
    type: entity.type,
    id: entity.id,
    names: entity.names,
    icon: entity.icon || "",
    category: entity.category || ""
  }));

  return `/* Generated from the verified class entity registry. Do not hand-edit this file. */
(function () {
  "use strict";

  const rows = ${js(rows)};
  const entities = new Map();
  const entitiesByRef = new Map();
  const phrases = [];

  function normalize(value) {
    return String(value || "").trim().toLowerCase().replace(/[’]/g, "'").replace(/\\s+/g, " ");
  }

  rows.forEach(function (row) {
    entitiesByRef.set(row.type + "=" + row.id, row);
    row.names.forEach(function (name) {
      entities.set(normalize(name), row);
      phrases.push(name);
    });
  });

  function wowheadUrl(entity) {
    return "https://www.wowhead.com/wotlk/" + entity.type + "=" + entity.id;
  }

  function tooltipValue(entity) {
    return entity.type + "=" + entity.id + "&domain=wotlk";
  }

  function decorateAnchor(anchor, entity) {
    anchor.classList.add("wowhead-link");
    anchor.setAttribute("data-wowhead", tooltipValue(entity));
    if (!anchor.target) anchor.target = "_blank";
    const rel = new Set((anchor.rel || "").split(/\\s+/).filter(Boolean));
    rel.add("noopener");
    anchor.rel = Array.from(rel).join(" ");
  }

  function makeAnchor(text, entity) {
    const anchor = document.createElement("a");
    anchor.href = wowheadUrl(entity);
    anchor.textContent = text;
    decorateAnchor(anchor, entity);
    return anchor;
  }

  function entityForNode(node) {
    const requested = node.getAttribute("data-entity-name") || node.getAttribute("data-entity-icon") || node.textContent;
    return entities.get(normalize(requested));
  }

  function decorateNamedEntities() {
    const selector = [
      ".game-entity", ".item-name", ".recipe-name", ".consumable-name", ".gem-name",
      ".spell-name", ".ability-name", ".skill-name", ".talent-name", ".glyph-name", ".enchant-name"
    ].join(",");

    document.querySelectorAll(selector).forEach(function (node) {
      if (node.hasAttribute("data-template-placeholder")) return;
      const entity = entityForNode(node);
      if (!entity || node.closest("code,pre,button,textarea")) return;
      if (node.tagName === "A") {
        decorateAnchor(node, entity);
        return;
      }
      if (node.closest("a")) return;
      const anchor = makeAnchor("", entity);
      node.classList.forEach(function (className) { anchor.classList.add(className); });
      while (node.firstChild) anchor.appendChild(node.firstChild);
      node.appendChild(anchor);
    });
  }

  function decorateExistingWowheadLinks() {
    document.querySelectorAll('a[href*="wowhead.com/wotlk/"]').forEach(function (anchor) {
      if (anchor.hasAttribute("data-wowhead")) return;
      const match = anchor.href.match(/\\/(item|spell|skill)=(\\d+)/);
      if (!match) return;
      decorateAnchor(anchor, { type: match[1], id: Number(match[2]) });
    });
  }

  function escapeRegExp(value) {
    return value.replace(/[.*+?^$\\{\\}()|[\\]\\\\]/g, "\\\\$&");
  }

  function linkPhrases() {
    if (!phrases.length) return;
    const ordered = Array.from(new Set(phrases)).sort(function (a, b) { return b.length - a.length; });
    const matcher = new RegExp("(^|[^A-Za-z0-9'])((?:" + ordered.map(escapeRegExp).join("|") + "))(?=$|[^A-Za-z0-9'])", "gi");
    const root = document.querySelector("main") || document.body;
    const walker = document.createTreeWalker(root, NodeFilter.SHOW_TEXT);
    const candidates = [];
    let textNode;

    while ((textNode = walker.nextNode())) {
      const parent = textNode.parentElement;
      if (!parent || !textNode.nodeValue.trim()) continue;
      if (parent.closest("a,code,pre,script,style,textarea,button,iframe,nav,[data-no-entity-links],.game-entity,.item-name,.recipe-name,.consumable-name,.gem-name,.spell-name,.ability-name,.skill-name,.talent-name,.glyph-name,.enchant-name")) continue;
      matcher.lastIndex = 0;
      if (matcher.test(textNode.nodeValue)) candidates.push(textNode);
    }

    candidates.forEach(function (node) {
      const fragment = document.createDocumentFragment();
      let cursor = 0;
      let match;
      matcher.lastIndex = 0;

      while ((match = matcher.exec(node.nodeValue))) {
        const prefix = match[1];
        const phrase = match[2];
        const start = match.index + prefix.length;
        if (start > cursor) fragment.appendChild(document.createTextNode(node.nodeValue.slice(cursor, start)));
        const entity = entities.get(normalize(phrase));
        fragment.appendChild(entity ? makeAnchor(phrase, entity) : document.createTextNode(phrase));
        cursor = start + phrase.length;
      }

      if (cursor < node.nodeValue.length) fragment.appendChild(document.createTextNode(node.nodeValue.slice(cursor)));
      node.parentNode.replaceChild(fragment, node);
    });
  }

  function iconizeEntities() {
    document.querySelectorAll("[data-entity-icon],.iconize-entity").forEach(function (node) {
      if (node.querySelector(":scope > img.entity-icon")) return;
      const entity = entityForNode(node);
      if (!entity || !entity.icon) return;
      const image = document.createElement("img");
      image.className = node.getAttribute("data-icon-class") || "ability-icon entity-icon";
      image.src = "https://wow.zamimg.com/images/wow/icons/large/" + entity.icon + ".jpg";
      image.alt = "";
      image.setAttribute("aria-hidden", "true");
      image.onerror = function () { image.remove(); };
      node.prepend(image);
    });

    if (document.body && document.body.dataset.entityIcons === "dense") {
      document.querySelectorAll("a[data-wowhead].wowhead-link").forEach(function (anchor) {
      if (anchor.querySelector(":scope > img")) return;
      if (anchor.closest("h1,h2,h3,h4,summary,.chapter-card,.source-list,[data-no-entity-icons]")) return;
      const match = anchor.getAttribute("data-wowhead").match(/^(item|spell|skill)=(\\d+)/);
      if (!match) return;
      const entity = entitiesByRef.get(match[1] + "=" + match[2]);
      if (!entity || !entity.icon) return;
      const image = document.createElement("img");
      image.className = "entity-link-icon";
      image.src = "https://wow.zamimg.com/images/wow/icons/large/" + entity.icon + ".jpg";
      image.alt = "";
      image.setAttribute("aria-hidden", "true");
      image.onerror = function () { image.remove(); };
      anchor.prepend(image);
      anchor.classList.add("has-entity-icon");
      });
    }
  }

  function loadWowheadTooltips() {
    if (document.querySelector('script[data-${classSlug}-wowhead]')) return;
    window.whTooltips = { colorLinks: false, iconizeLinks: false, renameLinks: false };
    const script = document.createElement("script");
    script.src = "https://wow.zamimg.com/js/tooltips.js";
    script.async = true;
    script.dataset.${classSlug.replace(/-([a-z])/g, (_, c) => c.toUpperCase())}Wowhead = "true";
    document.head.appendChild(script);
  }

  function init() {
    decorateNamedEntities();
    linkPhrases();
    decorateExistingWowheadLinks();
    iconizeEntities();
    loadWowheadTooltips();
  }

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", init, { once: true });
  else init();
}());
`;
}

export function createEmptyRegistry(config) {
  return {
    schemaVersion: 1,
    className: config.className,
    classSlug: config.classSlug,
    items: [],
    spells: [],
    skills: []
  };
}
