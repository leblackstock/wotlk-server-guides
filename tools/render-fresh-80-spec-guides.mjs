#!/usr/bin/env node
import fs from "node:fs";
import path from "node:path";

const root = process.cwd();
const updatedDate = new Intl.DateTimeFormat("en-CA", {
  timeZone: "America/New_York",
  year: "numeric",
  month: "2-digit",
  day: "2-digit"
}).format(new Date());
const esc = (value) => String(value)
  .replaceAll("&", "&amp;")
  .replaceAll("<", "&lt;")
  .replaceAll(">", "&gt;")
  .replaceAll('"', "&quot;");
const icon = (name, className = "spell-icon") =>
  `<img class="${className}" src="https://wow.zamimg.com/images/wow/icons/large/${esc(name)}.jpg" alt="" aria-hidden="true" onerror="this.remove()">`;
const operatingExampleLink = (example) => {
  const type = example.type || "spell";
  return `<a class="engine-spell-link wowhead-link" href="https://www.wowhead.com/wotlk/${type}=${example.id}" target="_blank" rel="noopener" data-wowhead="${type}=${example.id}&amp;domain=wotlk" aria-label="${esc(example.name)}">${icon(example.icon, "")}</a>`;
};
const operatingSequence = (mechanic) => mechanic.examples?.length
  ? `<div class="engine-spell-sequence" aria-label="${esc(mechanic.label)} spell sequence">${mechanic.examples.map((example, index) => `${index ? '<span class="engine-spell-separator" aria-hidden="true">—</span>' : ""}${operatingExampleLink(example)}`).join("")}</div>`
  : "";
const entity = (name, className = "ability-name", withIcon = false) =>
  `<span class="${className}"${withIcon ? ` data-entity-icon="${esc(name)}"` : ""}>${esc(name)}</span>`;
const item = (name, quality = "q-epic", withIcon = false) =>
  entity(name, `item-name ${quality}`, withIcon);
const list = (items, className = "clean-list") =>
  `<ul class="${className}">${items.map((entry) => `<li>${entry}</li>`).join("")}</ul>`;
const table = (headers, rows, className = "") =>
  `<div class="table-wrap"><table${className ? ` class="${className}"` : ""}><thead><tr>${headers.map((header) => `<th>${header}</th>`).join("")}</tr></thead><tbody>${rows.map((row) => `<tr>${row.map((cell) => `<td>${cell}</td>`).join("")}</tr>`).join("")}</tbody></table></div>`;
const uniconizedSections = new Set(["guide-pages", "sources", "mistakes", "professions", "special", "assignments"]);
const section = (spec, id, title, body, iconName = spec.icons.class, className = "common") =>
  `<section class="${className}" id="${id}"><h2 class="guide-category-heading">${uniconizedSections.has(id) ? "" : `${icon(iconName)} `}${title}<a class="guide-back-to-top" href="#top" aria-label="Back to top">↑ Top</a></h2>${body}</section>`;
const sourceList = (links) =>
  `<ul class="source-list">${links.map(([label, href]) => `<li><a href="${href}" target="_blank" rel="noopener">${label}</a></li>`).join("")}</ul>`;

const pageOrder = [
  ["quickStart", "Quick Start", "pve-guide"],
  ["playing", "Playing", "playing"],
  ["setup", "Setup", "setting-up"],
  ["building", "Building", "gearing"],
  ["equipping", "Equipping", "gear-targets"],
  ["raiding", "Raiding", "raiding"]
];

function href(spec, key) {
  const page = pageOrder.find(([pageKey]) => pageKey === key);
  return `${spec.slug}-${page[2]}.html`;
}

function nav(spec, current) {
  return `<nav class="site-nav" aria-label="${esc(spec.name)} guide pages"><a class="guide-hub-link" href="../index.html">Guide Hub</a>${pageOrder.map(([key, label]) => `<a href="${href(spec, key)}"${key === current ? ' aria-current="page"' : ""}>${label}</a>`).join("")}</nav>`;
}

function pager(spec, current) {
  const index = pageOrder.findIndex(([key]) => key === current);
  return `<nav class="page-pager" aria-label="Previous and next guide pages">${index > 0 ? `<a href="${href(spec, pageOrder[index - 1][0])}">← ${pageOrder[index - 1][1]}</a>` : "<span></span>"}${index < pageOrder.length - 1 ? `<a href="${href(spec, pageOrder[index + 1][0])}">${pageOrder[index + 1][1]} →</a>` : "<span></span>"}</nav>`;
}

function shell(spec, current, title, description, jumps, body) {
  return `<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="description" content="${esc(description)}">
  <title>${esc(title)} | WotLK 3.3.5</title>
  <link rel="icon" href="../assets/brand/hellscream-server-logo.ico" sizes="any">
  <link rel="icon" type="image/png" href="../assets/brand/hellscream-server-logo-32.png" sizes="32x32">
  <link rel="apple-touch-icon" href="../assets/brand/hellscream-server-logo-180.png">
  <link rel="stylesheet" href="../assets/guide-color-system.css?v=${spec.cacheKey}">
  <link rel="stylesheet" href="../assets/style.css?v=20260728-main-ux-v1">
  <link rel="stylesheet" href="../assets/${spec.slug}.css?v=${spec.cacheKey}">
  <link rel="stylesheet" href="../assets/guide-operating-manual.css?v=20260731-operating-manual-v1">
  <link rel="stylesheet" href="../assets/guide-hero.css?v=20260812-guide-identity-card-v3">
  <script src="../assets/${spec.tooltipFile}?v=${spec.cacheKey}" defer></script>
  <script src="../assets/${spec.slug}.js?v=${spec.cacheKey}" defer></script>
</head>
<body data-guide-class="${spec.classSlug}" data-guide-spec="${spec.specKey}"${spec.guideAudience ? ` data-guide-audience="${esc(spec.guideAudience)}"` : ""}>
  <div class="wrap" id="top">
    ${nav(spec, current)}
    <header class="guide-hero">
      <span class="page-kicker">${esc(spec.name)} • WotLK 3.3.5 • Level 80+</span>
      <h1 class="guide-hero-title"><span class="hero-spec-nickname">${esc(spec.nickname)}</span> <span class="hero-guide-type">${esc(spec.guideTypes[current])}</span></h1>
      <p class="sub">${esc(description)}</p>
    </header>
    <nav class="jump-nav jump-nav--detached guide-jump-nav" aria-label="Topics on this page">${jumps.map(([id, label]) => `<a href="#${id}">${esc(label)}</a>`).join("")}</nav>
    <main>${body}${pager(spec, current)}</main>
    <footer>Unofficial player-made Hellscream guide. Verify live tooltips, raid assignments, and server scripting. • Updated ${updatedDate}</footer>
  </div>
</body>
</html>
`;
}

function playbookCard(card) {
  return `<article class="spec-card">
    <div class="spec-card-header">
      <div><span class="spec-card-kicker">${esc(card.kicker)}</span><h3 data-entity-icon="${esc(card.iconEntity)}">${esc(card.title)}</h3></div>
      <span class="spec-card-tag">${esc(card.tag)}</span>
    </div>
    <div class="spec-card-body">
      <h4>Decision</h4>
      <p>${card.decision}</p>
      <div class="ability-strip">${card.actions.map((action, index) => `${index ? '<span class="ability-arrow">›</span>' : ""}${entity(action, "ability-choice ability-name", true)}`).join("")}</div>
      ${list(card.rules)}
    </div>
    <div class="spec-card-footer"><p><strong>Failure to avoid:</strong> ${card.failure}</p></div>
  </article>`;
}

function filterPanel(spec) {
  const group = (name, values) => `<div class="filter-row"><span class="filter-label">${name}</span><div class="filter-options">${values.map(([value, label], index) => `<button class="filter-button" type="button" data-filter-group="${name.toLowerCase()}" data-filter-value="${value}" aria-pressed="${index === 0}">${label}</button>`).join("")}</div></div>`;
  return `<div class="filter-panel" data-spec-filters>
    ${group("Size", [["all", "All"], ["10", "10-player"], ["25", "25-player"]])}
    ${group("Difficulty", [["all", "All"], ["normal", "Normal"], ["heroic", "Heroic"]])}
    ${group("Role", [["all", "All"], ...spec.roleFilters])}
    <p class="filter-status mini-note" role="status" aria-live="polite"></p>
  </div>`;
}

function renderQuickStart(spec) {
  const summaries = spec.quick.summaries.map((card) => `<div class="summary-card"><span class="summary-label">${esc(card.label)}</span><div class="summary-value">${card.value}</div><div class="summary-detail">${card.detail}</div></div>`).join("");
  const engine = `<div class="summary-card combat-engine operating-engine"><span class="summary-label">Combat engine</span><div class="summary-value">${esc(spec.quick.engineTitle)}</div><div class="engine-grid">${spec.mechanics.map((mechanic) => `<div class="engine-step mechanic-${mechanic.key}"><strong>${icon(mechanic.titleIcon || mechanic.examples?.[0]?.icon, "ability-icon")} ${esc(mechanic.label)}</strong><p>${esc(mechanic.use)}</p>${operatingSequence(mechanic)}</div>`).join("")}</div></div>`;
  const chapters = pageOrder.slice(1).map(([key, label], index) => `<a class="chapter-card" href="${href(spec, key)}"><span class="chapter-number">${index + 1}</span><h3>${icon(spec.icons[key])} ${label}</h3><p>${esc(spec.descriptions[key])}</p><span class="chapter-topics">${esc(spec.quick.chapterTopics[key])}</span></a>`).join("");
  const manualClass = `common operating-manual${spec.quick.summaries.length === 4 ? " operating-manual--four-summaries" : ""}${spec.guideAudience === "fresh-80" ? " fresh-80-starting-assumptions" : ""}`;
  const body =
    section(spec, "quick-start", "Two-minute operating manual", `<div class="summary-grid">${summaries}${engine}</div>
      <details class="server-behavior"><summary>${icon("inv_misc_wrench_01", "ability-icon")} Server behavior on Hellscream</summary><p>${esc(spec.serverNote)}</p></details>
      <div class="two-col"><div class="guide-box"><h3>${icon(spec.quick.beforeIcon, "ability-icon")} Before the pull</h3>${list(spec.quick.before, "checklist")}</div><div class="guide-box"><h3>${icon(spec.quick.firstIcon, "ability-icon")} First fresh-80 moves</h3>${list(spec.quick.firstMoves, "priority-list")}</div></div>`, spec.icons.quickStart, manualClass) +
    section(spec, "guide-pages", `Continue the ${esc(spec.shortName)} guide`, `<div class="chapter-grid">${chapters}</div>`, spec.icons.class) +
    section(spec, "sources", "Sources and verification", sourceList(spec.sources.quick), "inv_misc_book_11");
  return shell(spec, "quickStart", `${spec.name} Quick Start`, spec.descriptions.quickStart, [["quick-start", "Quick start"], ["guide-pages", "Guide pages"], ["sources", "Sources"]], body);
}

function renderPlaying(spec) {
  const engine = `<div class="engine-grid">${spec.mechanics.map((mechanic) => `<div class="engine-step mechanic-${mechanic.key}"><strong data-entity-icon="${esc(mechanic.iconEntity)}">${esc(mechanic.label)}</strong><p>${esc(mechanic.use)}</p></div>`).join("")}</div>
    <div class="note spec" style="margin-top:12px"><strong>Default priority:</strong> ${spec.playing.priority}</div>
    <div class="two-col" style="margin-top:12px"><div class="guide-box"><h3>${icon(spec.playing.openerIcon, "ability-icon")} Opener</h3>${list(spec.playing.opener)}</div><div class="guide-box"><h3>${icon(spec.playing.trackingIcon, "ability-icon")} Track this</h3>${list(spec.playing.tracking)}</div></div>`;
  const cards = spec.playing.cards.map(playbookCard).join("");
  const body =
    section(spec, "engine", "Core decision engine", engine, spec.icons.playing) +
    section(spec, "playbooks", "Situation playbooks", `<p class="muted">Select a card header to focus on one situation. Select it again—or press Escape—to restore all cards.</p><div class="spec-playbook-grid">${cards}</div>`, spec.icons.playing) +
    section(spec, "utility", "Cooldowns and utility", table(["Tool", "Primary job", "Timing rule"], spec.playing.utility), spec.icons.class) +
    section(spec, "mistakes", "Mistakes that cost pulls", `<div class="two-col"><div class="note warning"><strong>Mechanical mistakes</strong>${list(spec.playing.mistakes.slice(0, Math.ceil(spec.playing.mistakes.length / 2)))}</div><div class="note danger"><strong>${esc(spec.playing.mistakeGroupLabel || "Raid mistakes")}</strong>${list(spec.playing.mistakes.slice(Math.ceil(spec.playing.mistakes.length / 2)))}</div></div>`, "ability_creature_cursed_03") +
    section(spec, "sources", "Sources and verification", sourceList(spec.sources.playing), "inv_misc_book_11");
  return shell(spec, "playing", `Playing your ${spec.name}`, spec.descriptions.playing, [["engine", "Combat engine"], ["playbooks", "Playbooks"], ["utility", "Cooldowns"], ["mistakes", "Mistakes"], ["sources", "Sources"]], body);
}

function renderSetup(spec) {
  const talent = `<div class="note spec${spec.guideAudience === "fresh-80" ? " fresh-80-self-contained-talents" : ""}"><strong>Recommended baseline:</strong> ${esc(spec.talent.points)} ${esc(spec.talent.name)}.</div>
    <div class="guide-box" style="margin-top:12px"><div class="icon-heading">${icon(spec.icons.talent, "title-icon")}<div><span class="summary-label">Fully filled baseline</span><h3 style="margin:0">${esc(spec.talent.points)} ${esc(spec.talent.name)}</h3></div></div><p class="mini-note">${esc(spec.talent.summary)}</p><div class="talent-embed-wrap"><iframe class="talent-embed" title="Fully filled ${esc(spec.talent.points)} ${esc(spec.name)} talent tree" loading="lazy" src="https://www.wowhead.com/wotlk/talent-calc/embed/${esc(spec.talent.path)}"></iframe></div><p class="talent-fallback">Tree not loading? <a href="https://www.wowhead.com/wotlk/talent-calc/${esc(spec.talent.path)}" target="_blank" rel="noopener">Open the complete build in the Wowhead calculator.</a></p></div>
    <div class="three-col" style="margin-top:12px">${spec.setup.talentGroups.map((group) => `<div class="priority-card"><h3>${icon(group.icon, "ability-icon")} ${esc(group.title)}</h3>${list(group.items)}</div>`).join("")}</div>`;
  const macros = spec.setup.macros.map((macro) => `<div class="macro-card"><h3 data-entity-icon="${esc(macro.entity)}">${esc(macro.title)}</h3><p class="macro-purpose">${esc(macro.purpose)}</p><code class="macro-code">${esc(macro.code)}</code></div>`).join("");
  const glyphs = spec.setup.glyphs.map((row, index) => {
    if (index >= 4) return row;
    const marked = row[0].replace('class="', 'class="iconize-entity ');
    return [marked, ...row.slice(1)];
  });
  const addons = `<div class="two-col"><div class="guide-box"><h3>${icon("inv_misc_pocketwatch_01", "ability-icon")} Essential</h3>${list(spec.setup.essentialAddons)}</div><div class="guide-box"><h3>${icon("inv_misc_gear_01", "ability-icon")} Recommended</h3>${list(spec.setup.recommendedAddons)}</div></div><p class="mini-note">See the <a href="addons.html?class=${spec.classSlug}">Addon Library filtered for ${esc(spec.className)}</a> for compatibility notes and downloads.</p>`;
  const body =
    section(spec, "talents", "Talents", talent, spec.icons.setup) +
    (spec.setup.extraSection ? section(spec, spec.setup.extraSection.id, spec.setup.extraSection.title, spec.setup.extraSection.body, spec.setup.extraSection.icon) : "") +
    section(spec, "glyphs", "Glyphs", table(["Glyph", "Status", "Use", "Reason"], glyphs), "inv_inscription_tradeskill01") +
    section(spec, "macros", "Practical 3.3.5a macros", `<div class="macro-grid">${macros}</div><div class="note info" style="margin-top:12px"><strong>Client rule:</strong> these use original 3.3.5 macro conditionals and exact English spell names. Modern retail-only commands and cursor casting are intentionally excluded.</div>`, "inv_misc_note_01") +
    section(spec, "addons", "Addons and interface", addons, "inv_misc_gear_01") +
    section(spec, "sources", "Sources and verification", sourceList(spec.sources.setup), "inv_misc_book_11");
  const jumps = [["talents", "Talents"]];
  if (spec.setup.extraSection) jumps.push([spec.setup.extraSection.id, spec.setup.extraSection.short]);
  jumps.push(["glyphs", "Glyphs"], ["macros", "Macros"], ["addons", "Addons"], ["sources", "Sources"]);
  return shell(spec, "setup", `Setting up your ${spec.name}`, spec.descriptions.setup, jumps, body);
}

function renderBuilding(spec) {
  const stages = `<div class="three-col">${spec.building.stages.map((stage) => `<div class="guide-box"><h3>${icon(stage.icon, "ability-icon")} ${esc(stage.title)}</h3>${list(stage.items)}</div>`).join("")}</div>`;
  const body =
    `<div class="note spec"><strong>Ready for exact items?</strong> Open <a href="${href(spec, "equipping")}"><strong>Equipping your ${esc(spec.name)}</strong></a>.</div>` +
    section(spec, "stats", "Stats, caps, and tradeoffs", table(["Stat", "Practical priority", "What it does", "Important correction"], spec.building.stats), spec.icons.building) +
    section(spec, "path", "Fresh-80 gearing path", stages, "inv_misc_map_01", spec.guideAudience === "fresh-80" ? "common fresh-80-budget-path" : "common") +
    section(spec, "gems", "Gems", table(["Socket / job", "Default", "Alternative", "Use rule"], spec.building.gems), "inv_jewelcrafting_gem_42") +
    section(spec, "enchants", "Enchants", table(["Slot", "Recommended", "Alternative / note"], spec.building.enchants), "trade_engraving") +
    section(spec, "professions", "Professions", table(["Profession", "Combat value", "Practical verdict"], spec.building.professions), "trade_blacksmithing") +
    section(spec, "sources", "Sources and verification", sourceList(spec.sources.building), "inv_misc_book_11");
  return shell(spec, "building", `Building your ${spec.name}`, spec.descriptions.building, [["stats", "Stats"], ["path", "Gearing path"], ["gems", "Gems"], ["enchants", "Enchants"], ["professions", "Professions"], ["sources", "Sources"]], body);
}

function renderEquipping(spec) {
  const body =
    `<div class="note warning"><strong>Hellscream source warning:</strong> the named items and standard sources below are WotLK 3.3.5 references. Verify the live item tooltip, vendor, currency, difficulty, and custom alternatives before spending gold, emblems, or raid priority.</div>` +
    section(spec, "first", "First purchases and farms", table(["Priority", "Target", "Standard source", "Why it matters"], spec.equipping.first), spec.icons.equipping) +
    section(spec, "fresh", "Fresh-80 and crafted targets", table(["Slot", "Target", "Standard source", "Upgrade logic"], spec.equipping.fresh), "inv_hammer_20", spec.guideAudience === "fresh-80" ? "common fresh-80-immediate-targets" : "common") +
    section(spec, "emblems", "Emblems and tier", `<div class="three-col">${spec.equipping.emblems.map((group) => `<div class="guide-box"><h3>${icon(group.icon, "ability-icon")} ${esc(group.title)}</h3>${list(group.items)}</div>`).join("")}</div>`, "inv_misc_frostemblem_01") +
    section(spec, "toc", "Trial of the Crusader targets", table(["Item", "Source", "Role"], spec.equipping.toc), "achievement_boss_anubarak_01") +
    section(spec, "icc", "Icecrown Citadel targets", table(["Item", "Source", "Role"], spec.equipping.icc), "achievement_zone_icecrown_01") +
    section(spec, "special", "Keep these alternate tools", table(["Job", "Piece or set", "Why it stays"], spec.equipping.special), "inv_misc_bag_10") +
    section(spec, "sources", "Sources and verification", sourceList(spec.sources.equipping), "inv_misc_book_11");
  return shell(spec, "equipping", `Equipping your ${spec.name}`, spec.descriptions.equipping, [["first", "First targets"], ["fresh", "Fresh 80"], ["emblems", "Emblems"], ["toc", "ToC"], ["icc", "ICC"], ["special", "Special sets"], ["sources", "Sources"]], body);
}

function renderRaiding(spec) {
  const notes = spec.raiding.notes.map((note) => `<article class="raid-encounter"><h3>${icon(note.icon, "ability-icon")} ${esc(note.encounter)}</h3><div class="raid-note" data-size="${note.size}" data-difficulty="${note.difficulty}" data-role="${note.role}"><div class="raid-note-meta"><span class="raid-note-tag">${esc(note.sizeLabel)}</span><span class="raid-note-tag">${esc(note.difficultyLabel)}</span><span class="raid-note-tag">${esc(note.roleLabel)}</span>${note.verify ? '<span class="raid-note-tag raid-note-verify">Needs Hellscream test</span>' : ""}</div><p>${note.text}</p></div></article>`).join("");
  const body =
    (spec.raiding.entryNote ? `<div class="note spec${spec.guideAudience === "fresh-80" ? " fresh-80-later-progression" : ""}"><strong>Where this chapter fits:</strong> ${esc(spec.raiding.entryNote)}</div>` : "") +
    `<div class="note warning"><strong>Raid scope:</strong> these are ${esc(spec.name)} responsibilities, not full encounter guides. Raid-leader assignments override a generic playbook.</div>` +
    section(spec, "prepare", "Consumables and pull preparation", `<div class="two-col"><div class="guide-box"><h3>${icon("inv_alchemy_endlessflask_05", "ability-icon")} Consumables</h3>${list(spec.raiding.consumables)}</div><div class="guide-box"><h3>${icon(spec.raiding.assignmentIcon, "ability-icon")} Confirm before pull</h3>${list(spec.raiding.prePull)}</div></div>`, "inv_alchemy_endlessflask_05") +
    section(spec, "assignments", "Assignment rules", table(["Assignment", "What success looks like", "What to call"], spec.raiding.assignments), spec.raiding.assignmentIcon) +
    section(spec, "encounters", "Encounter notes", `${filterPanel(spec)}<div class="raid-filter-empty note warning" hidden>No encounter notes match this filter combination.</div><div class="raid-encounter-grid">${notes}</div>`, spec.icons.raiding) +
    section(spec, "sources", "Sources and verification", sourceList(spec.sources.raiding), "inv_misc_book_11");
  return shell(spec, "raiding", `Raiding with your ${spec.name}`, spec.descriptions.raiding, [["prepare", "Preparation"], ["assignments", "Assignments"], ["encounters", "Encounters"], ["sources", "Sources"]], body);
}

const holyPriest = {
  className: "Priest",
  classSlug: "priest",
  name: "Holy Priest",
  shortName: "Holy Priest",
  nickname: "Holy Priest",
  guideTypes: {
    quickStart: "Quick Start",
    playing: "Playing Guide",
    setup: "Setup Guide",
    building: "Build Guide",
    equipping: "Gear Guide",
    raiding: "Raid Healer Guide"
  },
  slug: "holy-priest",
  specKey: "priest-holy",
  guideAudience: "fresh-80",
  fresh80Policy: {
    selfContainedTalents: true,
    externalRaidBuffsRequired: false,
    capsAreProgressionGoals: true,
    budgetBeforePremium: true,
    raidContentIsLaterProgression: true
  },
  tooltipFile: "priest-tooltips.js",
  cacheKey: "20260726-holy-priest-v2-color-icons",
  serverNote: "Standard original-client WotLK 3.3.5a behavior is the baseline. Hellscream may alter sources, tuning, cooldown resets, or encounter scripting; uncertain interactions are labeled for live testing.",
  icons: {
    class: "inv_staff_30",
    quickStart: "spell_holy_guardianspirit",
    playing: "spell_holy_circleofrenewal",
    setup: "spell_holy_blessedrecovery",
    building: "spell_holy_holyprotection",
    equipping: "inv_chest_cloth_18",
    raiding: "achievement_boss_lichking",
    talent: "spell_holy_guardianspirit"
  },
  descriptions: {
    quickStart: "Start at level 80 with the healing engine, first gearing rules, pull checklist, and a clear route through the complete guide.",
    playing: "Turn Prayer of Mending, Circle of Healing, Serendipity, Renew, cooldowns, and mana tools into a deliberate healing priority.",
    setup: "Install the 18/53/0 build, glyphs, mouseover macros, HealBot bindings, addons, and information tracking.",
    building: "Build enough mana to stay active, then balance haste, spell power, crit, spirit, gems, enchants, and professions.",
    equipping: "Target practical crafted, dungeon, emblem, ToC, ICC, and Ruby Sanctum upgrades from a fresh level 80 starting point.",
    raiding: "Handle raid healing, tank support, dispels, movement, recovery cooldowns, and encounter assignments by size and difficulty."
  },
  mechanics: [
    {
      key: "triage",
      label: "Triage",
      iconEntity: "Flash Heal",
      titleIcon: "spell_holy_flashheal",
      use: "Use the smallest spell that lands safely before the next damage.",
      examples: [
        { name: "Flash Heal", id: 48071, icon: "spell_holy_flashheal" },
        { name: "Binding Heal", id: 48120, icon: "spell_holy_blindingheal" }
      ]
    },
    {
      key: "serendipity",
      label: "Serendipity",
      iconEntity: "Serendipity",
      titleIcon: "spell_holy_serendipity",
      use: "Build with Flash Heal or Binding Heal; spend on Prayer of Healing or Greater Heal.",
      examples: [
        { name: "Flash Heal", id: 48071, icon: "spell_holy_flashheal" },
        { name: "Serendipity", id: 63730, icon: "spell_holy_serendipity" },
        { name: "Prayer of Healing", id: 48072, icon: "spell_holy_prayerofhealing02" }
      ]
    },
    {
      key: "prayer",
      label: "Prayer",
      iconEntity: "Prayer of Mending",
      titleIcon: "spell_holy_prayerofmendingtga",
      use: "Aim Prayer of Mending and Circle of Healing where several players will take damage.",
      examples: [
        { name: "Prayer of Mending", id: 48113, icon: "spell_holy_prayerofmendingtga" },
        { name: "Circle of Healing", id: 48089, icon: "spell_holy_circleofrenewal" }
      ]
    },
    {
      key: "mana",
      label: "Mana",
      iconEntity: "Shadowfiend",
      titleIcon: "spell_shadow_shadowfiend",
      use: "Plan Inner Focus, Shadowfiend, Hymn of Hope, and lower-cost fillers early.",
      examples: [
        { name: "Inner Focus", id: 14751, icon: "spell_frost_windwalkon" },
        { name: "Shadowfiend", id: 34433, icon: "spell_shadow_shadowfiend" },
        { name: "Hymn of Hope", id: 64901, icon: "spell_holy_symbolofhope" }
      ]
    }
  ],
  roleFilters: [["raid-healing", "Raid healing"], ["tank-support", "Tank support"], ["utility", "Dispel / utility"], ["cooldown", "Cooldown"], ["special", "Special assignment"]],
  quick: {
    summaries: [
      { label: "Core job", value: "Prevent the next death", detail: "Holy is a flexible group and raid healer. Choose by damage pattern, not by a rigid rotation." },
      { label: "Default rhythm", value: "PoM → CoH → triage", detail: "Keep Prayer of Mending moving, use Circle of Healing on real clusters, then fill intelligently." },
      { label: "Fresh-80 rule", value: "Mana first, speed second", detail: "A healer with empty mana has zero throughput. Add haste after sustained activity is comfortable." }
    ],
    engineTitle: "Predict → choose → land → recover",
    beforeIcon: "spell_holy_prayerofmendingtga",
    firstIcon: "inv_misc_coin_01",
    before: [
      `Use ${entity("Inner Fire")} and your available Fortitude, Spirit, and Shadow Protection buffs; carry candles for group prayers.`,
      `Identify the tank, keep party or raid frames visible, and know which magic effects and diseases you can dispel.`,
      `Pre-place ${entity("Lightwell")} only where the group can actually click it safely.`,
      `Cast ${entity("Prayer of Mending")} on the pull target and pre-${entity("Renew")} active tanks when damage is imminent.`
    ],
    firstMoves: [
      `Train every rank-80 heal and install raid frames that show range, aggro, diseases, and dispellable magic.`,
      `Buy or farm a mana trinket; enchant usable gear instead of waiting for a fantasy best-in-slot set.`,
      `Run normal and heroic dungeons, including normal Trial of the Champion, while replacing weak slots and learning triage.`,
      `Treat raids as later progression once the set is coherent, enchanted, and comfortable in five-player content.`
    ],
    chapterTopics: {
      playing: "Triage · Serendipity · movement · mana",
      setup: "18/53/0 · glyphs · HealBot · macros",
      building: "Intellect · haste · spirit · enchants",
      equipping: "Dungeons · emblems · ToC · ICC",
      raiding: "Assignments · filters · boss notes"
    }
  },
  playing: {
    priority: `${entity("Prayer of Mending")} where it can bounce → ${entity("Circle of Healing")} on three or more injured players → emergency save → group ${entity("Prayer of Healing")} with ${entity("Serendipity")} → ${entity("Flash Heal")}/${entity("Binding Heal")} triage → predictive ${entity("Renew")}.`,
    openerIcon: "spell_holy_prayerofmendingtga",
    trackingIcon: "spell_holy_serendipity",
    opener: [
      `Pre-cast ${entity("Prayer of Mending")} on the first tank.`,
      `Pre-${entity("Renew")} active tanks if it will tick into real damage.`,
      `Place ${entity("Lightwell")} before combat when the raid has agreed to use it.`,
      `Do not manufacture overhealing just to look busy; begin with mana and cooldowns intact.`
    ],
    tracking: [
      `${entity("Prayer of Mending")} target and remaining charges.`,
      `${entity("Circle of Healing")} cooldown and injured-player clusters.`,
      `${entity("Serendipity")} stacks and duration.`,
      `${entity("Surge of Light")} and ${entity("Holy Concentration")} procs.`,
      `Mana percentage, ${entity("Shadowfiend")}, ${entity("Hymn of Hope")}, and ${entity("Inner Focus")}.`
    ],
    cards: [
      {
        kicker: "Routine raid damage", title: "Bounce and cluster healing", tag: "Default", iconEntity: "Prayer of Mending",
        decision: "Spend one global where it can heal several people, then return to spot triage.",
        actions: ["Prayer of Mending", "Circle of Healing", "Flash Heal"],
        rules: ["Aim Circle of Healing at a player standing inside the injured cluster.", "Recast Prayer of Mending when charges are exhausted or it is stranded away from damage."],
        failure: "pressing Circle of Healing on cooldown into one injured player and paying full mana for decorative green numbers."
      },
      {
        kicker: "Group burst", title: "Spend Serendipity", tag: "Burst", iconEntity: "Serendipity",
        decision: "When three or more people in one party are hurt, convert stored Serendipity into a fast Prayer of Healing.",
        actions: ["Binding Heal", "Flash Heal", "Prayer of Healing"],
        rules: ["Binding Heal builds the same stack while fixing both the priest and the target.", "Check party grouping; Prayer of Healing is party-based in 3.3.5a."],
        failure: "casting a slow, naked Prayer of Healing after the damage instead of preparing stacks before it."
      },
      {
        kicker: "Single target", title: "Stabilize a tank", tag: "Support", iconEntity: "Guardian Spirit",
        decision: "Use fast spot heals for danger, a Serendipity Greater Heal for a predictable hole, and Guardian Spirit before the lethal event.",
        actions: ["Prayer of Mending", "Flash Heal", "Greater Heal", "Guardian Spirit"],
        rules: ["Maintain Inspiration through critical direct heals when assigned to tank support.", "Guardian Spirit also increases healing received; it is valuable before death prevention triggers."],
        failure: "holding Guardian Spirit until the target is already dead or another healer has already committed the same cooldown."
      },
      {
        kicker: "Self plus ally", title: "Use Binding Heal", tag: "Efficiency", iconEntity: "Binding Heal",
        decision: "When both the priest and another player need healing, Binding Heal is two useful heals and one Serendipity stack.",
        actions: ["Binding Heal", "Circle of Healing", "Prayer of Healing"],
        rules: ["Use it during shared aura damage.", "Do not cast it when the self-heal will be pure overheal."],
        failure: "spamming Flash Heal on others while remaining injured and forcing another healer to repair the priest."
      },
      {
        kicker: "Movement", title: "Move without going idle", tag: "Mobile", iconEntity: "Renew",
        decision: "Use instant globals while relocating, but arrive ready to cast rather than extending movement for another Renew.",
        actions: ["Prayer of Mending", "Circle of Healing", "Renew", "Power Word: Shield"],
        rules: ["Coordinate Power Word: Shield with a Discipline Priest before using Body and Soul.", "Move during existing global cooldowns and stop in range of the assigned group."],
        failure: "blanketing Renew indiscriminately and arriving with less mana but no better coverage."
      },
      {
        kicker: "Mana emergency", title: "Recover before empty", tag: "Recovery", iconEntity: "Shadowfiend",
        decision: "Use mana cooldowns while there is enough fight remaining for the returned mana to matter.",
        actions: ["Inner Focus", "Shadowfiend", "Hymn of Hope"],
        rules: ["Use Inner Focus with Divine Hymn or Prayer of Healing for a high-cost free cast.", "Shadowfiend benefits from a safe, attackable target and haste effects; Hymn of Hope needs a safe channel window."],
        failure: "waiting for zero mana, then discovering the boss is untargetable or movement cancels Hymn of Hope."
      }
    ],
    utility: [
      [entity("Guardian Spirit"), "Planned tank or special-target external", "Call it before the spike; the glyph shortens the cooldown only when the death-prevention effect is not consumed."],
      [entity("Divine Hymn"), "Emergency raid recovery", "Use with Inner Focus when possible and channel only from a safe position."],
      [entity("Hymn of Hope"), "Group mana recovery", "Coordinate with other healers; the channel costs several globals."],
      [entity("Mass Dispel"), "Large-area magic removal", "Expensive and slow; use it for mechanics that justify it, not ordinary single dispels."],
      [entity("Fear Ward"), "Prevent a known fear", "Assign it before the pull and track the target."],
      [entity("Fade"), "Temporary threat reduction", "Use early enough to prevent caster or healing aggro from becoming a chase scene."]
    ],
    mistakes: [
      "Treating healing as a fixed rotation instead of matching spell shape to damage shape.",
      "Ignoring party boundaries when aiming Prayer of Healing.",
      "Overwriting a Discipline Priest's shields or Weakened Soul plan.",
      "Letting Serendipity expire repeatedly instead of converting it into planned burst.",
      "Dispelling a positioned disease or transfer mechanic without the raid leader's call.",
      "Dying with Guardian Spirit, Divine Hymn, Shadowfiend, and a mana potion unused."
    ]
  },
  talent: {
    points: "18/53/0",
    name: "fresh-80 self-contained Holy baseline",
    summary: "This version keeps the crucial Discipline mana tools and the complete Holy healing engine. Treat composition-based flex points as later optimization, not a starting requirement.",
    path: "priest/05032031103-234501032002151530000331351"
  },
  setup: {
    talentGroups: [
      {
        title: "Core engine", icon: "spell_holy_serendipity",
        items: [`${entity("Serendipity")} converts spot healing into fast group or large single-target healing.`, `${entity("Circle of Healing")}, Divine Providence, and ${entity("Prayer of Mending")} form the mobile raid-healing core.`, `${entity("Guardian Spirit")} is the defining external cooldown.`]
      },
      {
        title: "Mana foundation", icon: "spell_nature_sleep",
        items: [`Meditation allows Spirit regeneration while casting.`, `${entity("Inner Focus")} removes the mana cost of one expensive spell.`, `Mental Agility reduces the cost of the instant spells used constantly.`]
      },
      {
        title: "Real flex points", icon: "spell_holy_blessedrecovery",
        items: [`Body and Soul is useful only when coordinated with any Discipline Priest.`, `${entity("Lightwell")} is valuable when the raid will click it; otherwise the point is wasted.`, `Empowered Renew and Test of Faith shift value with spell usage and progression damage.`]
      }
    ],
    glyphs: [
      [entity("Glyph of Circle of Healing", "glyph-name"), '<span class="must">Default</span>', "All raid sizes", "Adds a sixth Circle of Healing target; especially strong in 25-player raids."],
      [entity("Glyph of Prayer of Healing", "glyph-name"), '<span class="must">Default</span>', "Group burst", "Adds a six-second heal-over-time equal to 20% of Prayer of Healing."],
      [entity("Glyph of Guardian Spirit", "glyph-name"), '<span class="must">Progression</span>', "Planned externals", "Reduces the cooldown when the death-prevention effect does not trigger."],
      [entity("Glyph of Flash Heal", "glyph-name"), '<span class="optional">Mana swap</span>', "Fresh-80 sustain", "Reduces Flash Heal mana cost when mana is the limiting problem."],
      [entity("Glyph of Shadowfiend", "glyph-name"), '<span class="optional">Minor</span>', "All content", "Refunds mana if the fiend dies to damage."],
      [entity("Glyph of Fortitude", "glyph-name"), '<span class="optional">Minor</span>', "Rebuffing", "Cuts the mana cost of Fortitude buffs."],
      [entity("Glyph of Levitate", "glyph-name"), '<span class="optional">Minor</span>', "Quality of life", "Removes the Light Feather reagent."],
      [entity("Glyph of Shadow Protection", "glyph-name"), '<span class="optional">Minor</span>', "Shadow-heavy raids", "Extends Shadow Protection duration."]
    ],
    macros: [
      { title: "Mouseover Flash Heal", entity: "Flash Heal", purpose: "Heal the mouseover without losing the hostile or assigned target.", code: "#showtooltip Flash Heal\n/cast [@mouseover,help,nodead][help,nodead][@player] Flash Heal" },
      { title: "Mouseover Prayer of Mending", entity: "Prayer of Mending", purpose: "Start or redirect the bounce quickly.", code: "#showtooltip Prayer of Mending\n/cast [@mouseover,help,nodead][help,nodead][@player] Prayer of Mending" },
      { title: "Guardian Spirit priority", entity: "Guardian Spirit", purpose: "Mouseover first, then focus, then current friendly target.", code: "#showtooltip Guardian Spirit\n/cast [@mouseover,help,nodead][@focus,help,nodead][help,nodead] Guardian Spirit" },
      { title: "Self-or-mouseover Dispel Magic", entity: "Dispel Magic", purpose: "Dispel a friendly mouseover; hold Alt to guarantee self.", code: "#showtooltip Dispel Magic\n/cast [mod:alt,@player][@mouseover,help,nodead][help,nodead] Dispel Magic" }
    ],
    essentialAddons: [
      `<a href="addons.html?search=Deadly%20Boss%20Mods">Deadly Boss Mods</a> for predictable damage and movement timers.`,
      `<a href="addons.html?search=HealBot">HealBot</a> or equivalent raid frames for range, debuffs, aggro, and click-casting.`,
      `<a href="addons.html?search=Decursive">Decursive</a> for fast magic and disease assignment visibility.`
    ],
    recommendedAddons: [
      `WeakAuras/TellMeWhen for ${entity("Serendipity")}, ${entity("Surge of Light")}, Prayer of Mending charges, and mana cooldowns.`,
      `Details/Recount to review deaths, overhealing, spell mix, and cooldown use—not to race another healer.`,
      `Clique only if it is confirmed compatible with the chosen raid frames and 3.3.5a client.`
    ]
  },
  building: {
    stats: [
      ["Intellect", '<span class="must">Fresh-80 sustain priority</span>', "Larger mana pool, crit, and more return from percentage-based mana tools.", "Once the fight ends with comfortable mana, throughput stats gain relative value."],
      ["Spell Power", "Reliable throughput", "Raises every heal's output.", "It does not fix late casts, wrong targets, or empty mana."],
      ["Haste", "Best speed stat after sustain", "Shortens cast times and the global cooldown.", "There is no useful universal fresh-80 haste cap. A one-second GCD requires 50% total haste before multiplicative raid buffs."],
      ["Spirit", "Strong regeneration and throughput", "Feeds Meditation, Holy Concentration, and Spiritual Guidance.", "Spirit is not automatically better than Intellect for a mana-starved fresh 80."],
      ["Crit", "Useful but less controllable", "Triggers Inspiration, Surge of Light, and Holy Concentration while increasing average healing.", "Do not chase crit at the cost of large Intellect, haste, or item-level gains."],
      ["MP5", "Direct in-combat regeneration", "Works regardless of the five-second rule.", "Good on a usable upgrade, but Spirit and Intellect usually interact with more of the Holy kit."]
    ],
    stages: [
      { title: "Fresh level 80", icon: "inv_misc_coin_01", items: ["Equip coherent spell-power gear with Intellect and useful secondaries.", "Secure two functional trinkets, a strong weapon, and budget gems and enchants for temporary gear.", "Prefer mana stability over copying an ICC haste target or buying premium materials too early."] },
      { title: "Raid-ready base", icon: "achievement_boss_general_nazgrim", items: ["Finish the 18/53/0 setup and glyphs.", "Practice sustained heroic-dungeon pulls without drinking after every pack.", "Carry mana potions and know the planned Shadowfiend/Hymn window."] },
      { title: "Encounter tuning", icon: "inv_misc_gear_01", items: ["Favor extra haste and spell power for short burst fights.", "Favor Intellect, Spirit, and mana trinkets for long progression pulls.", "Keep a throughput set for Valithria where encounter mechanics can solve mana."] }
    ],
    gems: [
      ["Meta", item("Insightful Earthsiege Diamond", "q-rare"), "None for general progression", "Activate with one red, one yellow, and one blue gem."],
      ["Red", "Rare-quality spell-power gem", item("Runed Cardinal Ruby"), "Use the affordable equivalent on temporary gear; upgrade to epic spell power only when mana is comfortable and the item will last."],
      ["Yellow", "Rare-quality spell power / Intellect gem", item("Luminous Ametrine"), "Use the affordable equivalent while stabilizing, then upgrade worthwhile sockets later."],
      ["Blue", "Rare-quality spell power / Spirit gem", item("Purified Dreadstone"), "Use the minimum needed for the meta unless a strong socket bonus justifies more."],
      ["Any color", "Keep a correctly activated budget meta", item("Nightmare Tear"), "Nightmare Tear is a later convenience, not a required first purchase."]
    ],
    enchants: [
      ["Head", item("Arcanum of Burning Mysteries"), "Kirin Tor revered in standard Wrath."],
      ["Shoulders", item("Greater Inscription of the Storm"), "Sons of Hodir exalted; use the lower inscription while progressing reputation."],
      ["Back", entity("Enchant Cloak - Greater Speed", "enchant-name"), `${entity("Lightweave Embroidery", "enchant-name")} for Tailoring throughput.`],
      ["Chest", entity("Enchant Chest - Powerful Stats", "enchant-name"), "A cheaper all-stats enchant is acceptable on a temporary chest."],
      ["Wrists", entity("Enchant Bracers - Superior Spellpower", "enchant-name"), "Prioritize this on a piece expected to survive several upgrades."],
      ["Hands", entity("Enchant Gloves - Exceptional Spellpower", "enchant-name"), "Use Hyperspeed Accelerators if Engineering and the timing is deliberate."],
      ["Waist", item("Eternal Belt Buckle", "q-rare"), "Always add the extra socket to a lasting belt."],
      ["Feet", entity("Enchant Boots - Tuskarr's Vitality", "enchant-name"), "Movement speed prevents more deaths than a tiny stationary stat gain."],
      ["Weapon", entity("Enchant Weapon - Mighty Spellpower", "enchant-name"), "Major Intellect is a valid long-fight mana alternative."]
    ],
    professions: [
      ["Engineering", "Hyperspeed Accelerators, Nitro Boosts, and utility.", "Excellent control and movement; strongest when cooldowns are actually bound and planned."],
      ["Jewelcrafting", "Three stronger Dragon's Eye gems.", "Flexible Intellect or spell-power tuning."],
      ["Tailoring", "Lightweave Embroidery proc and strong crafted cloth.", "High throughput but the proc is less controllable than a static cloak enchant."],
      ["Alchemy", "Stronger and longer flask plus an improved mana potion.", "Practical on a low-pop economy and helpful for progression supplies."],
      ["Enchanting / Inscription", "Static ring enchants or shoulder inscription.", "Reliable value with profession convenience; choose for the whole account, not a one-stat spreadsheet."]
    ]
  },
  equipping: {
    first: [
      ['<span class="must">Farm first</span>', item("Tears of the Vanquished", "q-rare"), "Black Knight, normal Trial of the Champion", "A practical early mana trinket with Intellect and a mana-return proc."],
      ['<span class="must">Weapon</span>', item("War Mace of Unrequited Love", "q-rare"), "Keristrasza, heroic Nexus", "A strong pre-raid one-hander with Intellect, Spirit, spell power, and haste."],
      ['<span class="must">Staff option</span>', item("Staff of Draconic Combat", "q-rare"), "Cache of Eregos, heroic Oculus", "Excellent early haste and a simple one-item weapon slot."],
      ['<span class="optional">Craft</span>', item("Titansteel Guardian"), "Blacksmithing BoE", "High spell power and a dependable path when dungeon drops refuse to cooperate."],
      ['<span class="optional">BoE</span>', item("Darkmoon Card: Greatness"), "Nobles Deck / Darkmoon Faire", "The Intellect version is broadly useful, but price matters on a low-pop server."]
    ],
    fresh: [
      ["Off-hand", item("Faces of Doom"), "Inscription BoE", "Pairs with a one-handed weapon and supplies strong early stats; compare the local price before buying."],
      ["Armor gaps", "Highest usable normal or heroic dungeon healing piece", "Northrend five-player dungeons", "Replace quest and leveling pieces before paying for endgame crafts."],
      ["Reputation slot", "Best affordable faction healing reward", "Northrend reputation vendors", "Use deterministic reputation rewards when dungeon drops refuse to cooperate."],
      ["Crafted option", "Affordable spell-power cloth with Intellect or Spirit", "Tailoring BoE / Auction House", "Buy only when the price beats the next reachable dungeon or emblem upgrade."],
      ["Trinket", item("Talisman of Resurgence"), "50 Emblems of Triumph", "Large Intellect plus an on-use spell-power window."],
      ["Any weak slot", "Highest usable heroic / reputation upgrade", "Heroics and Northrend factions", "Replace severe item-level holes before optimizing secondary-stat perfection."]
    ],
    emblems: [
      { title: "Triumph", icon: "spell_holy_summonchampion", items: [`Buy ${item("Talisman of Resurgence")} when both trinkets are weak.`, "Use T9 pieces to repair the weakest armor slots and establish useful set bonuses.", "Do not buy around a final BiS list while wearing quest greens elsewhere."] },
      { title: "Frost", icon: "inv_misc_frostemblem_01", items: ["Build toward useful T10 healing bonuses.", `${item("Purified Lunar Dust")} is usable, but compare it against strong mana trinkets before spending.`, "Buy the largest immediate upgrade rather than banking emblems indefinitely."] },
      { title: "Tier logic", icon: "inv_chest_cloth_18", items: ["Evaluate set bonuses and the actual replacement piece together.", "Keep haste-heavy offset pieces when forcing tier would weaken the whole set.", "Save old mana pieces for long progression fights."] }
    ],
    toc: [
      [item("Solace of the Defeated"), "Lord Jaraxxus, 25-player", "One of the strongest sustained-mana trinkets; Horde/Alliance and heroic versions use different IDs."],
      [item("Talisman of Resurgence"), "Triumph vendor", "Reliable Intellect while progressing through ToC."],
      ["T9 healing tier", "Triumph vendors and Trophy of the Crusade routes", "Efficient armor progression before ICC."],
      ["High-item-level Spirit/haste weapon", "Anub'arak and tribute routes", "Take the clean upgrade; do not reserve an empty hand for a perfect drop."]
    ],
    icc: [
      [item("Frozen Bonespike"), "Lord Marrowgar, 10-player", "Accessible ICC caster weapon with useful healer stats."],
      [item("Althor's Abacus"), "Gunship Armory, 25-player", "General raid-healing throughput trinket."],
      [item("Royal Scepter of Terenas II"), "The Lich King, 25-player", "Top one-handed healer weapon family."],
      [item("Archus, Greatstaff of Antonidas"), "The Lich King, 25-player", "Powerful staff option when a two-handed allocation fits the raid."],
      [item("Purified Lunar Dust"), "Frost emblem vendor", "Accessible throughput/regeneration option, not an automatic best trinket."]
    ],
    special: [
      ["Long progression pull", "Intellect/Spirit pieces plus mana trinkets", "Sustained activity beats a larger theoretical heal after the mana bar is empty."],
      ["Short burst fight", "Haste/spell-power set", "Faster landing heals matter when mana will not be exhausted."],
      ["Valithria Dreamwalker", "Maximum throughput pieces", "Portal stacks and encounter mana support change the normal gearing problem."],
      ["Heavy movement", "Movement-speed boots", "Tuskarr's Vitality remains valuable even when a stationary enchant has more paper throughput."]
    ]
  },
  raiding: {
    entryNote: "This is a later progression chapter, not the starting expectation for a new level 80. Finish the self-contained setup, practice in normal and heroic dungeons, and enter raids only after the character and player are ready.",
    assignmentIcon: "spell_holy_guardianspirit",
    consumables: [
      `${item("Flask of the Frost Wyrm")} for general throughput.`,
      `${item("Firecracker Salmon")} or ${item("Fish Feast")} for spell power; use an Intellect or haste alternative when the set needs it.`,
      `${item("Runic Mana Potion")} for progression sustain; ${item("Potion of Wild Magic")} only when mana is already secure.`,
      "Candles, personal food, repaired gear, and enough glyphs for planned swaps."
    ],
    prePull: [
      "Raid-healing or tank-support assignment.",
      "Which player receives Guardian Spirit and which mechanic triggers it.",
      "Who dispels magic, who removes diseases, and which debuffs must wait for positioning.",
      "Shadowfiend and Hymn of Hope timing.",
      "Valithria portal team, if applicable."
    ],
    assignments: [
      ["Raid healing", "Prayer of Mending bounces through incoming damage; Circle of Healing hits real clusters; Serendipity is ready for party bursts.", "Call range gaps, party-layout problems, and Divine Hymn."],
      ["Tank support", "Inspiration and direct heals cover the assigned tank without abandoning raid spikes.", "Call Guardian Spirit and any handoff."],
      ["Dispel / disease", "The correct debuff is removed at the correct location and time.", "Call inability, range, or a deliberate delayed dispel."],
      ["Recovery cooldown", "Divine Hymn and Hymn of Hope are used in safe windows instead of dying unused.", "Call the channel so other healers cover the priest."],
      ["Special target", "The encounter objective—especially Valithria—receives planned throughput and cooldowns.", "Call portal stacks, Guardian Spirit, and range."]
    ],
    notes: [
      { encounter: "Trial of the Crusader", icon: "achievement_reputation_argentchampion", size: "10 25", difficulty: "normal heroic", role: "raid-healing utility", sizeLabel: "10 / 25", difficultyLabel: "Normal / Heroic", roleLabel: "Raid / utility", verify: false, text: `Keep ${entity("Prayer of Mending")} moving through predictable raid damage, use ${entity("Abolish Disease")} on Paralytic Toxin targets during Anub'arak, and preserve mana for the long final phase. On heroic, avoid panic-overhealing Penetrating Cold targets before assignments are clear.` },
      { encounter: "Lord Marrowgar", icon: "achievement_boss_lordmarrowgar", size: "10 25", difficulty: "normal heroic", role: "raid-healing cooldown", sizeLabel: "10 / 25", difficultyLabel: "Normal / Heroic", roleLabel: "Raid healing", verify: false, text: `Preload ${entity("Prayer of Mending")} for Bone Slice and Bone Storm, heal Bone Spike targets immediately, and keep moving during Storm with instant spells. Reserve ${entity("Guardian Spirit")} for an assigned tank or trapped player rather than reacting after lethal damage.` },
      { encounter: "Lady Deathwhisper", icon: "achievement_boss_ladydeathwhisper", size: "10 25", difficulty: "normal heroic", role: "raid-healing utility", sizeLabel: "10 / 25", difficultyLabel: "Normal / Heroic", roleLabel: "Raid / dispel", verify: false, text: `Stay spread, step out of Death and Decay, dispel removable magic effects on assignment, and help stabilize add tanks during waves. In modes with Dominate Mind, keep fast control and dispel communication separate from ordinary raid triage.` },
      { encounter: "Deathbringer Saurfang", icon: "achievement_boss_saurfang", size: "10 25", difficulty: "normal heroic", role: "tank-support raid-healing cooldown", sizeLabel: "10 / 25", difficultyLabel: "Normal / Heroic", roleLabel: "Marks / tank", verify: false, text: `Support the active tank and assigned Mark of the Fallen Champion targets. Do not blanket the raid simply because marks exist; use efficient direct heals, ${entity("Prayer of Mending")}, and a planned ${entity("Guardian Spirit")} as mark count rises.` },
      { encounter: "Festergut and Rotface", icon: "achievement_boss_festergutrotface", size: "10 25", difficulty: "normal heroic", role: "raid-healing tank-support utility", sizeLabel: "10 / 25", difficultyLabel: "Normal / Heroic", roleLabel: "Raid / tank / disease", verify: false, text: `On Festergut, prepare group burst for Pungent Blight and tank damage at high Inhale stacks. On Rotface, remove Mutated Infection only at the raid leader's called drop location; an early disease removal creates the ooze in the wrong place.` },
      { encounter: "Professor Putricide", icon: "achievement_boss_profputricide", size: "10 25", difficulty: "normal heroic", role: "raid-healing utility cooldown", sizeLabel: "10 / 25", difficultyLabel: "Normal / Heroic", roleLabel: "Raid / utility", verify: false, text: `Heal through ooze and gas target pressure while moving early for Malleable Goo and slime pools. Unbound Plague on heroic is a transfer mechanic, not a routine dispel; follow the raid's handoff route and use cooldowns on the actual damage peak.` },
      { encounter: "Blood Prince Council and Blood-Queen Lana'thel", icon: "achievement_boss_lanathel", size: "10 25", difficulty: "normal heroic", role: "raid-healing tank-support utility", sizeLabel: "10 / 25", difficultyLabel: "Normal / Heroic", roleLabel: "Raid / tank", verify: false, text: `Support the Keleseth tank during empowered windows, spread for Shock Vortex, and move promptly for Pact or Swarming Shadows. ${entity("Fear Ward")} can cover a planned fear target for Blood-Queen; do not let the fear interrupt assigned healing.` },
      { encounter: "Valithria Dreamwalker", icon: "achievement_boss_valithriadreamwalker", size: "10 25", difficulty: "normal heroic", role: "special cooldown", sizeLabel: "10 / 25", difficultyLabel: "Normal / Heroic", roleLabel: "Portal healer", verify: true, text: `If assigned to portals, collect every safe Dream Cloud stack, return in range, and pour stacked throughput into Valithria. Use ${entity("Guardian Spirit")} for its healing-received bonus when the server permits it on the encounter target; verify Hellscream's exact interaction before planning around it.` },
      { encounter: "Sindragosa", icon: "achievement_boss_sindragosa", size: "10 25", difficulty: "normal heroic", role: "raid-healing tank-support utility", sizeLabel: "10 / 25", difficultyLabel: "Normal / Heroic", roleLabel: "Raid / tank", verify: false, text: `Manage Unchained Magic and Instability deliberately—stop casting before the stack becomes lethal. In phase three, use Ice Tombs to reset Mystic Buffet while remaining in range of the active tank and marked targets.` },
      { encounter: "The Lich King", icon: "achievement_boss_lichking", size: "10 25", difficulty: "normal heroic", role: "raid-healing tank-support utility cooldown", sizeLabel: "10 / 25", difficultyLabel: "Normal / Heroic", roleLabel: "All healing", verify: false, text: `Prepare for Infest, move before Defile, and remove Necrotic Plague only on the raid's explicit call and route. Coordinate ${entity("Guardian Spirit")} with Soul Reaper tank cooldowns, keep Val'kyr victims alive, and enter transitions with mana tools already planned.` },
      { encounter: "Halion", icon: "achievement_boss_halion", size: "10 25", difficulty: "normal heroic", role: "raid-healing tank-support utility", sizeLabel: "10 / 25", difficultyLabel: "Normal / Heroic", roleLabel: "Realm healing", verify: false, text: `Stay with the assigned realm, move early for combustion or consumption drops, and keep the tank covered through cutter movement. In the twilight realm, position so Twilight Cutters do not force a long out-of-range sweep.` }
    ]
  },
  sources: {
    quick: [
      ["Holy Priest talents and glyphs", "https://www.wowhead.com/wotlk/guide/classes/priest/holy/healer-talent-builds-glyphs-pve"],
      ["Holy Priest abilities and healing priorities", "https://www.wowhead.com/wotlk/guide/classes/priest/holy/healer-rotation-cooldowns-abilities-pve"]
    ],
    playing: [
      ["Holy Priest rotation, cooldowns, and abilities", "https://www.wowhead.com/wotlk/guide/classes/priest/holy/healer-rotation-cooldowns-abilities-pve"],
      ["Prayer of Mending rank 3", "https://www.wowhead.com/wotlk/spell=48113"],
      ["Serendipity rank 3", "https://www.wowhead.com/wotlk/spell=63730"],
      ["Guardian Spirit", "https://www.wowhead.com/wotlk/spell=47788"]
    ],
    setup: [
      ["Holy Priest 18/53/0 talent and glyph reference", "https://www.wowhead.com/wotlk/guide/classes/priest/holy/healer-talent-builds-glyphs-pve"],
      ["Filled 18/53/0 talent calculator", "https://www.wowhead.com/wotlk/talent-calc/priest/05032031103-234501032002151530000331351"]
    ],
    building: [
      ["Holy Priest stat priority", "https://www.wowhead.com/wotlk/guide/classes/priest/holy/healer-stat-priority-attributes-pve"],
      ["Holy Priest gems and enchants", "https://www.wowhead.com/wotlk/guide/classes/priest/holy/healer-enchants-gems-pve"]
    ],
    equipping: [
      ["Holy Priest pre-raid gear", "https://www.wowhead.com/wotlk/guide/classes/priest/holy/healer-bis-gear-pre-raid-pve"],
      ["Holy Priest phase-four gear", "https://www.wowhead.com/wotlk/guide/classes/priest/holy/healer-bis-gear-pve-phase-4"],
      ["Tears of the Vanquished item record", "https://www.wowhead.com/wotlk/item=47215"],
      ["Althor's Abacus item record", "https://www.wowhead.com/wotlk/item=50359"]
    ],
    raiding: [
      ["Icecrown Citadel raid overview", "https://www.wowhead.com/wotlk/zone=4812/icecrown-citadel"],
      ["Trial of the Crusader raid overview", "https://www.wowhead.com/wotlk/zone=4722/trial-of-the-crusader"],
      ["Ruby Sanctum raid overview", "https://www.wowhead.com/wotlk/zone=4987/the-ruby-sanctum"],
      ["Guardian Spirit spell data", "https://www.wowhead.com/wotlk/spell=47788"]
    ]
  }
};

const shadowPriest = {
  className: "Priest",
  classSlug: "priest",
  name: "Shadow Priest",
  shortName: "Shadow Priest",
  nickname: "Shadow Priest",
  guideTypes: {
    quickStart: "Quick Start",
    playing: "Playing Guide",
    setup: "Setup Guide",
    building: "Build Guide",
    equipping: "Gear Guide",
    raiding: "Raid DPS Guide"
  },
  slug: "shadow-priest",
  specKey: "shadow",
  guideAudience: "fresh-80",
  fresh80Policy: {
    selfContainedTalents: true,
    externalRaidBuffsRequired: false,
    capsAreProgressionGoals: true,
    budgetBeforePremium: true,
    raidContentIsLaterProgression: true
  },
  tooltipFile: "priest-tooltips.js",
  cacheKey: "20260726-shadow-priest-v2-color-icons",
  serverNote: "Standard original-client WotLK 3.3.5a behavior is the baseline. Shadow Word: Pain snapshot details, channel timing, boss immunities, and custom encounter scripting should be verified on Hellscream when observed behavior differs.",
  icons: {
    class: "inv_staff_30",
    quickStart: "spell_shadow_shadowform",
    playing: "spell_shadow_siphonmana",
    setup: "spell_shadow_twilight",
    building: "spell_shadow_shadowpower",
    equipping: "inv_chest_cloth_38",
    raiding: "achievement_boss_lichking",
    talent: "spell_shadow_dispersion"
  },
  descriptions: {
    quickStart: "Start at level 80 with the hit target, five-stack opener, DoT rules, raid utility, and guide path.",
    playing: "Execute the Shadow priority, preserve DoT value, channel Mind Flay cleanly, move without going idle, and recover mana.",
    setup: "Install the 14/0/57 build, glyphs, macros, dot tracking, addons, and keybinds for original WotLK 3.3.5a.",
    building: "Reach the boss spell-hit target, then compare spell power, haste, crit, spirit, gems, enchants, and professions honestly.",
    equipping: "Target practical crafted, dungeon, emblem, ToC, ICC, and Ruby Sanctum upgrades without blindly copying a final-tier BiS list.",
    raiding: "Apply damage, Replenishment, Dispersion soaks, Mass Dispel, add control, and encounter assignments by size and difficulty."
  },
  mechanics: [
    {
      key: "dots",
      label: "DoTs",
      iconEntity: "Vampiric Touch",
      titleIcon: "spell_holy_stoicism",
      use: "Maintain Vampiric Touch and Devouring Plague without clipping their final ticks.",
      examples: [
        { name: "Vampiric Touch", id: 48160, icon: "spell_holy_stoicism" },
        { name: "Devouring Plague", id: 48300, icon: "spell_shadow_blackplague" }
      ]
    },
    {
      key: "weaving",
      label: "Shadow Weaving",
      iconEntity: "Shadow Weaving",
      titleIcon: "spell_shadow_blackplague",
      use: "Reach five stacks before the lasting Shadow Word: Pain application.",
      examples: [
        { name: "Shadow Weaving", id: 15258, icon: "spell_shadow_blackplague" },
        { name: "Shadow Word: Pain", id: 48125, icon: "spell_shadow_shadowwordpain" }
      ]
    },
    {
      key: "channel",
      label: "Channel",
      iconEntity: "Mind Flay",
      titleIcon: "spell_shadow_siphonmana",
      use: "Fit complete Mind Flay ticks between higher-priority events.",
      examples: [
        { name: "Mind Flay", id: 48156, icon: "spell_shadow_siphonmana" }
      ]
    },
    {
      key: "mana",
      label: "Mana & support",
      iconEntity: "Dispersion",
      titleIcon: "spell_shadow_dispersion",
      use: "Use Shadowfiend, Dispersion, Replenishment, and Hymn of Hope deliberately.",
      examples: [
        { name: "Shadowfiend", id: 34433, icon: "spell_shadow_shadowfiend" },
        { name: "Dispersion", id: 47585, icon: "spell_shadow_dispersion" },
        { name: "Hymn of Hope", id: 64901, icon: "spell_holy_symbolofhope" }
      ]
    }
  ],
  roleFilters: [["single-target", "Single target"], ["multi-dot", "Adds / multi-DoT"], ["utility", "Utility / dispel"], ["soak", "Dispersion soak"], ["special", "Special assignment"]],
  quick: {
    summaries: [
      { label: "Level-83 hit goal", value: "Work toward 17% total", detail: "With 3/3 Shadow Focus and personal Misery, a Horde priest eventually needs 11% from gear: 289 rating. Start dungeons before reaching it." },
      { label: "Opener rule", value: "Five stacks, then Pain", detail: "Build Shadow Weaving before the long-lived Shadow Word: Pain that Mind Flay will refresh." },
      { label: "Fresh-80 rule", value: "Cap hit before greed", detail: "A missed Vampiric Touch, Mind Blast, or DoT costs more than a small uncapped throughput gain." }
    ],
    engineTitle: "Apply → stack → snapshot → maintain",
    beforeIcon: "spell_shadow_shadowform",
    firstIcon: "inv_misc_coin_01",
    before: [
      `Activate ${entity("Shadowform")} and ${entity("Inner Fire")}; confirm Fortitude, Spirit, and Shadow Protection assignments.`,
      `Identify the tank and first damage target; work toward the level-83 hit goal without treating it as a gate for five-player content.`,
      `Know when the group needs ${entity("Vampiric Embrace")}, ${entity("Mass Dispel")}, ${entity("Silence")}, or ${entity("Dispersion")}.`,
      `Save pre-potting for a planned boss pull; it is optional during the fresh-80 dungeon path.`
    ],
    firstMoves: [
      "Install visible DoT timers and begin building toward the level-83 spell-hit target.",
      `Farm ${item("Abyssal Rune", "q-rare")} and another functional trinket before chasing expensive ICC pieces.`,
      "Practice a five-stack opener on a training dummy until Shadow Word: Pain is never applied early.",
      "Run normal and heroic dungeons, including normal Trial of the Champion, while buying emblem upgrades for the weakest slots."
    ],
    chapterTopics: {
      playing: "DoTs · channels · movement · mana",
      setup: "14/0/57 · glyphs · macros · tracking",
      building: "Hit · spell power · haste · spirit",
      equipping: "Heroics · emblems · ToC · ICC",
      raiding: "Adds · Dispersion · utility · bosses"
    }
  },
  playing: {
    priority: `${entity("Vampiric Touch")} and ${entity("Devouring Plague")} maintained → ${entity("Mind Blast")} on cooldown when Replenishment or damage value justifies it → ${entity("Shadow Word: Death")} when movement or execute timing favors it → ${entity("Mind Flay")} as the channel filler. Apply ${entity("Shadow Word: Pain")} only after five ${entity("Shadow Weaving")} stacks.`,
    openerIcon: "spell_shadow_shadowform",
    trackingIcon: "spell_shadow_blackplague",
    opener: [
      `${entity("Vampiric Touch")} → ${entity("Devouring Plague")} → ${entity("Mind Blast")} → ${entity("Mind Flay")} until five ${entity("Shadow Weaving")} stacks.`,
      `Apply ${entity("Shadow Word: Pain")} at five stacks, ideally during the intended opening proc window.`,
      `Continue the priority; ${entity("Pain and Suffering")} refreshes Shadow Word: Pain through Mind Flay.`,
      `Do not delay required movement or mechanics to force a prettier opener.`
    ],
    tracking: [
      `${entity("Vampiric Touch")} and ${entity("Devouring Plague")} remaining duration.`,
      `${entity("Shadow Word: Pain")} and the five-stack ${entity("Shadow Weaving")} condition used for its first cast.`,
      `${entity("Mind Blast")} cooldown and ${entity("Replenishment")} need.`,
      `${entity("Shadowfiend")}, ${entity("Dispersion")}, ${entity("Hymn of Hope")}, and mana percentage.`,
      `The current Mind Flay tick so a channel is not broken accidentally.`
    ],
    cards: [
      {
        kicker: "Opening sequence", title: "Build five stacks first", tag: "Snapshot", iconEntity: "Shadow Weaving",
        decision: "The durable Shadow Word: Pain application waits until Shadow Weaving reaches five stacks.",
        actions: ["Vampiric Touch", "Devouring Plague", "Mind Blast", "Mind Flay", "Shadow Word: Pain"],
        rules: ["Pain and Suffering updates spell power on refresh but preserves important initial-state effects including the Shadow Weaving state.", "Do not rebuild the opener after every short mechanic; only reapply when Pain actually falls."],
        failure: "casting Shadow Word: Pain at four stacks and carrying an 8% Shadow Weaving bonus through the entire refresh chain."
      },
      {
        kicker: "Single target", title: "Protect DoT ticks", tag: "Priority", iconEntity: "Vampiric Touch",
        decision: "Refresh Vampiric Touch and Devouring Plague after their final tick, not several seconds early.",
        actions: ["Vampiric Touch", "Devouring Plague", "Mind Blast", "Mind Flay"],
        rules: ["Begin the cast early enough for the new Vampiric Touch to land after expiration.", "Use Mind Flay as elastic filler; preserve higher-priority cooldowns."],
        failure: "clipping repeated final ticks because the timer tracks cast start instead of aura expiration."
      },
      {
        kicker: "Channel control", title: "Count Mind Flay ticks", tag: "Execution", iconEntity: "Mind Flay",
        decision: "Choose one, two, or three ticks based on the next DoT or cooldown, then break only after the intended tick lands.",
        actions: ["Mind Flay", "Mind Blast", "Vampiric Touch"],
        rules: ["Latency and the 3.3.5 client change how close the next cast can be queued.", "A visible tick bar is more reliable than guessing from the animation."],
        failure: "mashing the next spell and repeatedly losing a tick without gaining a faster high-priority cast."
      },
      {
        kicker: "Multiple targets", title: "Multi-DoT with a death clock", tag: "Adds", iconEntity: "Devouring Plague",
        decision: "DoT only targets that will live long enough; direct damage wins on short-lived priority adds.",
        actions: ["Vampiric Touch", "Devouring Plague", "Mind Sear"],
        rules: ["Vampiric Touch on several durable targets can be excellent.", "Devouring Plague is limited to one target; put it where the full duration matters.", "Mind Sear needs enough nearby targets and a safe channel."],
        failure: "spending three globals on an add that dies before the second tick."
      },
      {
        kicker: "Movement", title: "Pre-position and spend instants", tag: "Mobile", iconEntity: "Shadow Word: Death",
        decision: "Move during global cooldowns, refresh only legitimately due DoTs, and use Shadow Word: Death when its recoil is safe.",
        actions: ["Devouring Plague", "Shadow Word: Death", "Power Word: Shield"],
        rules: ["Do not clip a healthy DoT simply to have something to press.", "Fade removes movement-impairing effects only with Improved Shadowform."],
        failure: "standing still for one more Mind Flay tick and dropping the encounter mechanic on the raid."
      },
      {
        kicker: "Survival and mana", title: "Use Dispersion deliberately", tag: "Soak", iconEntity: "Dispersion",
        decision: "Dispersion is a 90% damage-reduction and mana tool, not immunity; schedule it where lost casts buy survival or assignment value.",
        actions: ["Shadowfiend", "Dispersion", "Hymn of Hope"],
        rules: ["Use Shadowfiend on a target it can reach and survive.", "Dispersion can cover movement or a planned soak while restoring mana.", "Hymn of Hope needs a safe channel and raid awareness."],
        failure: "treating Dispersion as immunity and discovering the mechanic still applies, knocks back, or kills through its remaining damage."
      }
    ],
    utility: [
      [entity("Misery"), "3% spell-hit raid debuff plus personal scaling", "It does not stack with Improved Faerie Fire's spell-hit component."],
      [entity("Replenishment"), "Mana return to ten raid members", "Triggered when Mind Blast hits a target carrying Vampiric Touch."],
      [entity("Vampiric Embrace"), "Group healing from Shadow damage", "It heals the priest and party, not the entire raid in original 3.3.5a."],
      [entity("Dispersion"), "Survival, soak, and mana recovery", "Reduces damage by 90%; it is not Divine Shield."],
      [entity("Mass Dispel"), "Area magic removal", "Expensive and assignment-specific; do not abandon lethal movement to finish it."],
      [entity("Silence"), "Interrupt plus silence", "Requires the talent; the raid build may omit it because the path costs damage points."]
    ],
    mistakes: [
      "Applying Shadow Word: Pain before five Shadow Weaving stacks.",
      "Clipping Vampiric Touch or Devouring Plague before the last tick.",
      "Treating Mind Flay like a three-tick prison instead of an elastic filler.",
      "Ignoring the 17% boss spell-hit requirement and blaming random misses on scripting.",
      "Multi-DoTing targets too short-lived to repay the globals.",
      "Using Dispersion as if it grants immunity or saving Shadowfiend until the boss becomes untargetable."
    ]
  },
  talent: {
    points: "14/0/57",
    name: "fresh-80 self-contained Shadow baseline",
    summary: "The complete baseline covers every core damage and mana talent without requiring a particular party or raid composition. The remaining choices are narrow utility trades.",
    path: "priest/05032031--325023051223010223152301351"
  },
  setup: {
    talentGroups: [
      {
        title: "Core damage", icon: "spell_shadow_shadowform",
        items: [`${entity("Shadowform")}, ${entity("Vampiric Touch")}, ${entity("Pain and Suffering")}, and ${entity("Dispersion")} are non-negotiable.`, `${entity("Shadow Weaving")} and Twisted Faith define the opener and stat interactions.`, `Improved Devouring Plague, Darkness, and Shadow Power are direct damage.`]
      },
      {
        title: "Discipline value", icon: "spell_holy_innerfire",
        items: [`Improved ${entity("Inner Fire")} adds spell power as long as charges remain.`, `Meditation plus Spirit Tap improves sustain.`, `${entity("Inner Focus")} is a small free-cast tool and a legitimate one-point flex.`]
      },
      {
        title: "Real flex points", icon: "spell_shadow_impphaseshift",
        items: [`Improved Shadowform protects channels from pushback and lets ${entity("Fade")} break movement impairing effects.`, `Focused Mind and Veiled Shadows trade mana and Shadowfiend frequency.`, `${entity("Silence")} is useful, but reaching it costs several points.`]
      }
    ],
    glyphs: [
      [entity("Glyph of Shadow", "glyph-name"), '<span class="must">Default</span>', "All content", "Non-periodic spell crits grant spell power equal to 30% of Spirit for ten seconds."],
      [entity("Glyph of Mind Flay", "glyph-name"), '<span class="must">Default</span>', "Single target", "Increases Mind Flay damage while Shadow Word: Pain is present."],
      [entity("Glyph of Dispersion", "glyph-name"), '<span class="must">Progression</span>', "Mana / soaking", "Reduces Dispersion's cooldown, increasing defensive and recovery availability."],
      [entity("Glyph of Shadow Word: Death", "glyph-name"), '<span class="optional">Damage swap</span>', "Execute-heavy fights", "Adds damage under 35% health but increases the value of safe recoil management."],
      [entity("Glyph of Shadowfiend", "glyph-name"), '<span class="optional">Minor</span>', "All content", "Refunds mana when the Shadowfiend dies to damage."],
      [entity("Glyph of Fortitude", "glyph-name"), '<span class="optional">Minor</span>', "Rebuffing", "Cuts Fortitude buff cost."],
      [entity("Glyph of Shadow Protection", "glyph-name"), '<span class="optional">Minor</span>', "Shadow-heavy raids", "Extends Shadow Protection duration."],
      [entity("Glyph of Levitate", "glyph-name"), '<span class="optional">Minor</span>', "Quality of life", "Removes the Light Feather reagent."]
    ],
    macros: [
      { title: "Mind Flay without target loss", entity: "Mind Flay", purpose: "Stop the channel manually; avoid a castsequence that hides priority decisions.", code: "#showtooltip Mind Flay\n/cast [harm,nodead] Mind Flay" },
      { title: "Mouseover Dispel Magic", entity: "Dispel Magic", purpose: "Dispel an ally without dropping the boss target.", code: "#showtooltip Dispel Magic\n/cast [@mouseover,help,nodead][help,nodead] Dispel Magic" },
      { title: "Focus Silence", entity: "Silence", purpose: "Interrupt the focus when talented; otherwise cast on the current hostile target.", code: "#showtooltip Silence\n/cast [@focus,harm,nodead][] Silence" },
      { title: "Self-or-mouseover Power Word: Shield", entity: "Power Word: Shield", purpose: "Emergency movement protection without changing target.", code: "#showtooltip Power Word: Shield\n/cast [mod:alt,@player][@mouseover,help,nodead][help,nodead][@player] Power Word: Shield" }
    ],
    essentialAddons: [
      `<a href="addons.html?search=Deadly%20Boss%20Mods">Deadly Boss Mods</a> for movement, add, and soak timing.`,
      "A 3.3.5-compatible DoT timer that shows tenths near expiration.",
      "A cast/channel bar with latency and visible Mind Flay ticks."
    ],
    recommendedAddons: [
      `WeakAuras/TellMeWhen for five ${entity("Shadow Weaving")} stacks, ${entity("Shadowfiend")}, ${entity("Dispersion")}, and trinket procs.`,
      `Details/Recount to review DoT uptime, missed spells, channel clipping, target damage, and utility.`,
      `Decursive for assigned friendly magic removal without turning the DPS UI into healer clutter.`
    ]
  },
  building: {
    stats: [
      ["Spell Hit", '<span class="must">Cap first</span>', "Prevents misses against level-83 raid bosses.", "Boss cap is 17% total. With 3% Shadow Focus and 3% Misery, Horde needs 11% gear hit: 288.55 rating, rounded up to 289."],
      ["Spell Power", "Primary uncapped throughput", "Raises DoTs, Mind Flay, Mind Blast, and Shadow Word: Death.", "Spell power remains valuable at every stage; compare whole items rather than socket color alone."],
      ["Haste", "Strong after hit", "Adds DoT ticks through haste scaling and shortens casts/channels and the GCD.", "Shadow Word: Pain is the important exception: it can crit in Shadowform but does not gain haste ticks."],
      ["Crit", "Strong secondary", "Increases direct spell crits, periodic crits allowed by Shadowform, and Glyph of Shadow uptime.", "Crit is valuable but not a reason to miss the hit cap or take a large item-level loss."],
      ["Spirit", "Real DPS plus mana", "Twisted Faith converts 20% of Spirit to spell power; Glyph of Shadow adds temporary value.", "Spirit is not equal to raw spell power point-for-point."],
      ["Intellect", "Secondary mana and crit", "Expands the mana pool and slightly increases crit.", "Do not gem pure Intellect for damage."]
    ],
    stages: [
      { title: "Fresh level 80", icon: "inv_misc_coin_01", items: ["Start normal and heroic dungeons while building toward 289 hit rating for a Horde level-83 boss set with 3/3 Shadow Focus and Misery.", "Equip spell power and haste after hit; accept Spirit on strong cloth pieces.", "Use budget gems and enchants on temporary gear, and farm a usable weapon and two trinkets before expensive optimization."] },
      { title: "Raid-ready base", icon: "spell_shadow_shadowform", items: ["Use the 14/0/57 build and correct glyphs.", "Maintain near-complete Vampiric Touch and Devouring Plague uptime on a dummy.", "Carry a mana plan and a utility assignment."] },
      { title: "Encounter tuning", icon: "inv_misc_gear_01", items: ["Keep a hit-capped set through every swap.", "Use burst pieces for short adds and sustained pieces for long bosses.", "Do not break strong tier bonuses for a tiny single-item stat gain."] }
    ],
    gems: [
      ["Meta", item("Chaotic Skyflare Diamond", "q-rare"), "None for general damage", "Requires two blue gems; plan activation before socketing the rest."],
      ["Red", "Rare-quality spell-power gem", item("Runed Cardinal Ruby"), "Use the affordable equivalent on temporary gear; upgrade lasting pieces later."],
      ["Yellow", "Rare-quality spell power / haste gem", item("Reckless Ametrine"), "Collect worthwhile bonuses without overspending early."],
      ["Blue", "Rare-quality spell power / Spirit gem", item("Purified Dreadstone"), "Meet the meta with the least damage loss; Nightmare Tear is a later convenience."],
      ["Hit repair", "Rare-quality spell power / hit gem", item("Veiled Ametrine"), "Use only until the exact set reaches its current target; replace excess hit after upgrades."]
    ],
    enchants: [
      ["Head", item("Arcanum of Burning Mysteries"), "Kirin Tor revered."],
      ["Shoulders", item("Greater Inscription of the Storm"), "Sons of Hodir exalted."],
      ["Back", entity("Enchant Cloak - Greater Speed", "enchant-name"), `${entity("Lightweave Embroidery", "enchant-name")} is the Tailoring throughput option.`],
      ["Chest", entity("Enchant Chest - Powerful Stats", "enchant-name"), "A cheaper all-stats enchant is acceptable on a temporary chest."],
      ["Wrists", entity("Enchant Bracers - Superior Spellpower", "enchant-name"), "Static throughput."],
      ["Hands", entity("Enchant Gloves - Exceptional Spellpower", "enchant-name"), "Engineering may use Hyperspeed Accelerators."],
      ["Waist", item("Eternal Belt Buckle", "q-rare"), "Use the extra socket to repair hit or add spell power."],
      ["Feet", entity("Enchant Boots - Tuskarr's Vitality", "enchant-name"), "Movement speed is usually worth more than a minor stationary gain."],
      ["Weapon", entity("Enchant Weapon - Mighty Spellpower", "enchant-name"), `${entity("Enchant Weapon - Black Magic", "enchant-name")} is a haste-proc alternative that must be compared against the whole set.`]
    ],
    professions: [
      ["Engineering", "Hyperspeed Accelerators, Nitro Boosts, and bombs.", "Excellent for controlled haste and movement; requires active use."],
      ["Tailoring", "Lightweave Embroidery.", "Strong spell-power proc and convenient caster crafts."],
      ["Jewelcrafting", "Three stronger Dragon's Eye gems.", "Flexible spell-power or hit repair."],
      ["Alchemy", "Improved flask and potion value.", "Strong practical choice for low-pop consumable supply."],
      ["Enchanting / Inscription", "Static ring enchants or shoulder inscription.", "Reliable, uncomplicated value."]
    ]
  },
  equipping: {
    first: [
      ['<span class="must">Farm first</span>', item("Abyssal Rune", "q-rare"), "Normal Trial of the Champion", "Haste plus a spell-power proc; unusually accessible and useful deep into progression."],
      ['<span class="must">Hit repair</span>', item("Sundial of the Exiled"), "40 Emblems of Heroism", "A reliable early spell-power proc when trinkets are weak."],
      ['<span class="must">Weapon</span>', item("Staff of Draconic Combat", "q-rare"), "Cache of Eregos, heroic Oculus", "Spirit, spell power, and haste in one early weapon slot."],
      ['<span class="optional">Burst trinket</span>', item("Nevermelting Ice Crystal"), "Devourer of Souls, heroic Forge of Souls", "Useful crit on-use and a server-testing tool for Shadow Word: Pain behavior; not automatically best."],
      ['<span class="optional">Triumph</span>', item("Talisman of Resurgence"), "50 Emblems of Triumph", "Large Intellect and controllable spell power while gearing."]
    ],
    fresh: [
      ["Chest", item("Merlin's Robe"), "Tailoring BoE", "Strong spell-power and haste craft, but only when its local price is reasonable for a new 80."],
      ["Armor gaps", "Highest usable normal or heroic dungeon caster piece", "Northrend five-player dungeons", "Replace quest and leveling pieces before buying endgame crafts."],
      ["Reputation slot", "Best affordable faction caster reward", "Northrend reputation vendors", "Use deterministic rewards to repair hit or a weak armor slot."],
      ["Crafted option", "Affordable spell-power cloth with hit, haste, or Spirit", "Tailoring BoE / Auction House", "Compare the price with reachable dungeon and emblem alternatives."],
      ["Trinket", item("Talisman of Resurgence"), "50 Emblems of Triumph", "An accessible stat stick and controllable spell-power window while stronger drops are unavailable."],
      ["Any weak slot", "Highest hit-capped heroic or reputation upgrade", "Heroics and Northrend factions", "The best item is often the one that removes a quest-green hole without breaking hit."]
    ],
    emblems: [
      { title: "Triumph", icon: "spell_holy_summonchampion", items: [`Use ${item("Talisman of Resurgence")} if trinkets are poor.`, "Build T9 Shadow tier while repairing weak armor.", "Recalculate hit after every purchase."] },
      { title: "Frost", icon: "inv_misc_frostemblem_01", items: ["Work toward T10 Shadow bonuses.", "Buy strong offset pieces when they solve a weak slot without breaking set bonuses.", "Do not bank emblems while wearing severe gaps."] },
      { title: "Tier logic", icon: "inv_chest_cloth_38", items: ["Evaluate two-piece and four-piece bonuses as part of the whole set.", "Keep hit alternatives in the bank.", "A lower-item-level tier piece can beat a higher isolated offset when the bonus is strong."] }
    ],
    toc: [
      ["Reign of the Dead / Reign of the Unliving", "Anub'arak, 25-player", "Strong caster trinket family; faction and difficulty change the exact item."],
      [item("Talisman of Resurgence"), "Triumph vendor", "Controllable spell-power burst and easy acquisition."],
      ["T9 Shadow tier", "Triumph and Trophy routes", "Efficient bridge into ICC."],
      ["Hit/haste weapons and jewelry", "ToC bosses and tribute chest", "Prioritize a complete hit-capped set over a single theoretical ranking."]
    ],
    icc: [
      [item("Frozen Bonespike"), "Lord Marrowgar, 10-player", "Accessible one-handed caster weapon."],
      [item("Nibelung"), "Lady Deathwhisper, 25-player", "Proc staff with encounter-dependent value."],
      [item("Dislodged Foreign Object"), "Rotface, 25-player", "Exceptional haste plus stacking spell-power proc."],
      [item("Phylactery of the Nameless Lich"), "Sindragosa, 25-player", "High-value crit and spell-power proc trinket."],
      [item("Bloodsurge, Kel'Thuzad's Blade of Agony"), "The Lich King, 25-player", "End-tier one-handed caster weapon."],
      [item("Charred Twilight Scale"), "Halion, 25-player", "Ruby Sanctum spell-power proc trinket."]
    ],
    special: [
      ["Boss set", "Exactly hit-capped pieces", "A stable cap prevents every later swap from creating misses."],
      ["Trash / lower-level adds", "Less hit, more throughput", "Level-80 to level-82 targets require less hit than a raid boss."],
      ["Short-lived adds", "Burst trinkets and direct-damage bias", "A full DoT package may never repay its globals."],
      ["Shadow Word: Pain testing", item("Nevermelting Ice Crystal"), "Useful for testing initial-crit-state behavior on Hellscream; do not assume every Classic-era snapshot interaction matches."]
    ]
  },
  raiding: {
    entryNote: "This is a later progression chapter, not the starting expectation for a new level 80. Finish the self-contained setup, practice in normal and heroic dungeons, and enter raids only after the character and player are ready.",
    assignmentIcon: "spell_shadow_dispersion",
    consumables: [
      `${item("Flask of the Frost Wyrm")} for spell power.`,
      `${item("Firecracker Salmon")} or ${item("Fish Feast")}; use hit food only to repair a temporary cap deficit.`,
      `${item("Potion of Wild Magic")} for an opening proc window; ${item("Runic Mana Potion")} when progression sustain is the real limit.`,
      "Candles for raid prayers, repaired gear, and a hit-capped boss set."
    ],
    prePull: [
      "Which target receives the five-stack Shadow Word: Pain opener.",
      "Whether Mind Blast must maintain Replenishment.",
      "Mass Dispel, Silence, Mind Control, or Fear Ward assignment.",
      "Dispersion soak and whether it has been confirmed on Hellscream.",
      "Priority-add order and which targets live long enough for DoTs."
    ],
    assignments: [
      ["Single target", "High Vampiric Touch and Devouring Plague uptime with clean Mind Flay ticks.", "Call forced downtime or a target becoming immune."],
      ["Adds / multi-DoT", "Only durable targets receive DoTs; short priority adds die to direct damage.", "Call the focus target and any crowd control."],
      ["Utility", "Replenishment, Mass Dispel, friendly dispels, and Fear Ward happen without missed mechanics.", "Call the cast and any cooldown conflict."],
      ["Dispersion soak", "The mechanic is survived and the raid knows Dispersion is committed.", "Call start, end, and any unexpected server behavior."],
      ["Special assignment", "Mind Control, interrupt, orb, or realm duty is prioritized over personal meters.", "Call failure, immunity, or range."]
    ],
    notes: [
      { encounter: "Trial of the Crusader", icon: "achievement_reputation_argentchampion", size: "10 25", difficulty: "normal heroic", role: "single-target multi-dot utility", sizeLabel: "10 / 25", difficultyLabel: "Normal / Heroic", roleLabel: "Damage / utility", verify: false, text: `Multi-DoT durable targets on Twin Val'kyr only when raid strategy and target health justify it. On Anub'arak, use ${entity("Mind Sear")} for stacked adds when assigned, keep boss DoTs running, and save ${entity("Dispersion")} for movement, mana, or a planned Penetrating Cold survival window.` },
      { encounter: "Lord Marrowgar", icon: "achievement_boss_lordmarrowgar", size: "10 25", difficulty: "normal heroic", role: "single-target multi-dot", sizeLabel: "10 / 25", difficultyLabel: "Normal / Heroic", roleLabel: "Boss / spikes", verify: false, text: `Maintain boss DoTs, swap immediately to Bone Spikes, and use direct spells when a spike will die too quickly for full DoTs. Move during instant globals in Bone Storm and never trade player safety for one more channel tick.` },
      { encounter: "Lady Deathwhisper", icon: "achievement_boss_ladydeathwhisper", size: "10 25", difficulty: "normal heroic", role: "multi-dot utility", sizeLabel: "10 / 25", difficultyLabel: "Normal / Heroic", roleLabel: "Adds / utility", verify: false, text: `Follow add priority instead of blanketing every target. Use ${entity("Silence")} only if the build includes it and the interrupt is assigned; help dispel friendly magic effects while staying out of Death and Decay.` },
      { encounter: "Deathbringer Saurfang", icon: "achievement_boss_saurfang", size: "10 25", difficulty: "normal heroic", role: "single-target utility", sizeLabel: "10 / 25", difficultyLabel: "Normal / Heroic", roleLabel: "Boss / beasts", verify: false, text: `Keep boss DoTs active and use Mind Flay's slow or direct damage on Blood Beasts only when assigned. Do not spread long DoTs to beasts that should die quickly and must not reach melee players.` },
      { encounter: "Festergut and Rotface", icon: "achievement_boss_festergutrotface", size: "10 25", difficulty: "normal heroic", role: "single-target soak", sizeLabel: "10 / 25", difficultyLabel: "Normal / Heroic", roleLabel: "Boss / soak", verify: true, text: `Preserve DoTs while moving for spores, slime, and infection drops. ${entity("Dispersion")} can reduce Pungent Blight damage but is not immunity; only skip a spore if the raid has confirmed that exact Hellscream strategy.` },
      { encounter: "Professor Putricide", icon: "achievement_boss_profputricide", size: "10 25", difficulty: "normal heroic", role: "multi-dot utility soak", sizeLabel: "10 / 25", difficultyLabel: "Normal / Heroic", roleLabel: "Adds / survival", verify: false, text: `Switch hard to Volatile Ooze and Gas Cloud; DoT only if the add will live long enough. Move before Malleable Goo, follow the heroic Unbound Plague transfer route, and use Dispersion to survive movement pressure—not to ignore the handoff.` },
      { encounter: "Blood Prince Council and Blood-Queen Lana'thel", icon: "achievement_boss_lanathel", size: "10 25", difficulty: "normal heroic", role: "single-target utility", sizeLabel: "10 / 25", difficultyLabel: "Normal / Heroic", roleLabel: "Swap / bite", verify: false, text: `On Princes, damage only the active prince and use quick direct spells on Kinetic Bombs if assigned. On Blood-Queen, follow bite order exactly, move early for Pact and Swarming Shadows, and keep casting through movement with legitimate instant globals.` },
      { encounter: "Valithria Dreamwalker", icon: "achievement_boss_valithriadreamwalker", size: "10 25", difficulty: "normal heroic", role: "multi-dot utility special", sizeLabel: "10 / 25", difficultyLabel: "Normal / Heroic", roleLabel: "Add damage", verify: false, text: `Prioritize Blazing Skeletons and Suppressors, interrupt Frostbolt Volley only when talented and assigned, and use Mind Sear on stacked adds that will live through the channel. This is an add-control fight, not a boss-DoT uptime contest.` },
      { encounter: "Sindragosa", icon: "achievement_boss_sindragosa", size: "10 25", difficulty: "normal heroic", role: "single-target utility", sizeLabel: "10 / 25", difficultyLabel: "Normal / Heroic", roleLabel: "Boss / tombs", verify: false, text: `Manage Unchained Magic and Instability; stop casting before the stack becomes lethal. Do not let lingering DoTs destroy an Ice Tomb early, and use tomb line-of-sight to reset Mystic Buffet in phase three.` },
      { encounter: "The Lich King", icon: "achievement_boss_lichking", size: "10 25", difficulty: "normal heroic", role: "single-target multi-dot utility soak special", sizeLabel: "10 / 25", difficultyLabel: "Normal / Heroic", roleLabel: "All roles", verify: true, text: `Keep boss DoTs through predictable movement, burn Val'kyr and Raging Spirits by priority, and use ${entity("Mass Dispel")} only for an assigned mechanic. A ${entity("Dispersion")} Vile Spirit soak can be valuable, but exact spirit targeting and damage must be confirmed on Hellscream before making it a raid plan.` },
      { encounter: "Halion", icon: "achievement_boss_halion", size: "10 25", difficulty: "normal heroic", role: "single-target utility soak", sizeLabel: "10 / 25", difficultyLabel: "Normal / Heroic", roleLabel: "Realm damage", verify: false, text: `Stay in the assigned realm, maintain DoTs while moving early for combustion or consumption, and use Dispersion only for a planned survival job. In twilight, pre-position around cutter rotation so Mind Flay channels do not pull the priest into a lethal line.` }
    ]
  },
  sources: {
    quick: [
      ["Shadow Priest talents and glyphs", "https://www.wowhead.com/wotlk/guide/classes/priest/shadow/dps-talent-builds-glyphs-pve"],
      ["Shadow Priest stat priority and hit cap", "https://www.wowhead.com/wotlk/guide/classes/priest/shadow/dps-stat-priority-attributes-pve"]
    ],
    playing: [
      ["Shadow Priest rotation and abilities", "https://www.wowhead.com/wotlk/guide/classes/priest/shadow/dps-rotation-cooldowns-abilities-pve"],
      ["Pain and Suffering spell data", "https://www.wowhead.com/wotlk/spell=47580"],
      ["Dispersion spell data", "https://www.wowhead.com/wotlk/spell=47585"]
    ],
    setup: [
      ["Shadow Priest 14/0/57 talent and glyph reference", "https://www.wowhead.com/wotlk/guide/classes/priest/shadow/dps-talent-builds-glyphs-pve"],
      ["Filled 14/0/57 talent calculator", "https://www.wowhead.com/wotlk/talent-calc/priest/05032031--325023051223010223152301351"]
    ],
    building: [
      ["Shadow Priest stat priority", "https://www.wowhead.com/wotlk/guide/classes/priest/shadow/dps-stat-priority-attributes-pve"],
      ["Shadow Priest gems and enchants", "https://www.wowhead.com/wotlk/guide/classes/priest/shadow/dps-enchants-gems-pve"]
    ],
    equipping: [
      ["Shadow Priest pre-raid gear", "https://www.wowhead.com/wotlk/guide/classes/priest/shadow/dps-bis-gear-pre-raid-pve"],
      ["Shadow Priest phase-four gear", "https://www.wowhead.com/wotlk/guide/classes/priest/shadow/dps-bis-gear-pve-phase-4"],
      ["Abyssal Rune item record", "https://www.wowhead.com/wotlk/item=47213"],
      ["Dislodged Foreign Object item record", "https://www.wowhead.com/wotlk/item=50353"]
    ],
    raiding: [
      ["Icecrown Citadel raid overview", "https://www.wowhead.com/wotlk/zone=4812/icecrown-citadel"],
      ["Trial of the Crusader raid overview", "https://www.wowhead.com/wotlk/zone=4722/trial-of-the-crusader"],
      ["Ruby Sanctum raid overview", "https://www.wowhead.com/wotlk/zone=4987/the-ruby-sanctum"],
      ["Dispersion spell data", "https://www.wowhead.com/wotlk/spell=47585"]
    ]
  }
};

const marksmanshipHunter = {
  className: "Hunter",
  classSlug: "hunter",
  name: "Marksmanship Hunter",
  shortName: "Marksman Hunter",
  nickname: "Marks Hunter",
  guideTypes: {
    quickStart: "Quick Start",
    playing: "Playing Guide",
    setup: "Setup Guide",
    building: "Build Guide",
    equipping: "Gear Guide",
    raiding: "Raid DPS Guide"
  },
  slug: "marksmanship-hunter",
  specKey: "marksmanship",
  guideAudience: "fresh-80",
  fresh80Policy: {
    selfContainedTalents: true,
    externalRaidBuffsRequired: false,
    capsAreProgressionGoals: true,
    budgetBeforePremium: true,
    raidContentIsLaterProgression: true
  },
  tooltipFile: "hunter-tooltips.js",
  cacheKey: "20260805-marksman-v3-fresh80",
  serverNote: "Standard original-client WotLK 3.3.5a behavior is the baseline. The later WotLK Classic Trap Launcher: Explosive Trap spell is not assumed; traps are placed at the hunter's feet unless Hellscream explicitly adds a custom launcher.",
  icons: {
    class: "inv_weapon_bow_07",
    quickStart: "ability_hunter_chimerashot2",
    playing: "ability_hunter_focusedaim",
    setup: "ability_hunter_mastermarksman",
    building: "ability_hunter_lockandload",
    equipping: "inv_chest_chain_13",
    raiding: "achievement_boss_lichking",
    talent: "ability_hunter_chimerashot2"
  },
  descriptions: {
    quickStart: "Start at level 80 with the hit cap, Agility-first gearing rule, shot priority, pet checklist, and complete guide path.",
    playing: "Run the original 3.3.5a shot priority, preserve Auto Shot uptime, use Readiness correctly, move cleanly, and control the pet.",
    setup: "Install the 7/57/7 build, glyphs, shot macros, Misdirection tools, pet talents, addons, and tracking.",
    building: "Cap hit, remain Agility-first while fresh, understand Armor Penetration thresholds, and choose gems, enchants, and professions.",
    equipping: "Target practical crafted, dungeon, emblem, ToC, ICC, and Ruby Sanctum upgrades with weapon, trinket, and tier priorities.",
    raiding: "Deliver ranged damage, Misdirection, Tranquilizing Shot, interrupts, traps, kiting, and add assignments by size and difficulty."
  },
  mechanics: [
    {
      key: "sting",
      label: "Sting",
      iconEntity: "Serpent Sting",
      titleIcon: "ability_hunter_quickshot",
      use: "Apply Serpent Sting once, then protect it with timely Chimera Shot refreshes.",
      examples: [
        { name: "Serpent Sting", id: 49001, icon: "ability_hunter_quickshot" },
        { name: "Chimera Shot", id: 53209, icon: "ability_hunter_chimerashot2" }
      ]
    },
    {
      key: "shots",
      label: "Shot priority",
      iconEntity: "Chimera Shot",
      titleIcon: "ability_hunter_chimerashot2",
      use: "Protect Kill Shot, Chimera Shot, and Aimed Shot cooldowns before filling with Steady Shot.",
      examples: [
        { name: "Kill Shot", id: 61006, icon: "ability_hunter_assassinate2" },
        { name: "Chimera Shot", id: 53209, icon: "ability_hunter_chimerashot2" },
        { name: "Aimed Shot", id: 49050, icon: "inv_spear_07" },
        { name: "Steady Shot", id: 49052, icon: "ability_hunter_steadyshot" }
      ]
    },
    {
      key: "movement",
      label: "Movement",
      iconEntity: "Disengage",
      titleIcon: "ability_rogue_feint",
      use: "Move during instant-shot globals and stop long enough for Auto Shot and Steady Shot.",
      examples: [
        { name: "Disengage", id: 781, icon: "ability_rogue_feint" },
        { name: "Auto Shot", id: 75, icon: "ability_whirlwind" },
        { name: "Steady Shot", id: 49052, icon: "ability_hunter_steadyshot" }
      ]
    },
    {
      key: "pet",
      label: "Pet & utility",
      iconEntity: "Furious Howl",
      titleIcon: "ability_hunter_pet_wolf",
      use: "Keep the wolf alive, control its cooldowns, and use Misdirection, traps, and interrupts as assignments.",
      examples: [
        { name: "Furious Howl", id: 64495, icon: "ability_hunter_pet_wolf" },
        { name: "Misdirection", id: 34477, icon: "ability_hunter_misdirection" },
        { name: "Tranquilizing Shot", id: 19801, icon: "spell_nature_drowsy" }
      ]
    }
  ],
  talent: {
    points: "7/57/7",
    name: "Fresh-80 self-contained Careful Aim build",
    summary: "Start with 3/3 Focused Aim, 1/1 Trueshot Aura, and 2/3 Improved Hunter's Mark. This baseline assumes no external 10% attack-power buff; change that aura point only after a raid leader confirms equivalent coverage.",
    path: "hunter/502-035325131030013233135031051-5000002"
  },
  roleFilters: [
    ["boss-damage", "Boss damage"],
    ["add-control", "Adds / control"],
    ["utility", "Misdirect / tranq"],
    ["interrupt", "Interrupt"],
    ["special", "Special assignment"]
  ],
  quick: {
    summaries: [
      { label: "Level-83 hit goal", value: '<span class="must">8% / 263 rating</span>', detail: "With 3/3 Focused Aim, work toward 5% from gear, or 164 rating. Start normal and heroic dungeons while you build toward it." },
      { label: "Fresh-80 rule", value: "Agility first", detail: "Cap hit, then build a coherent Agility set. Do not gem Armor Penetration because an endgame list does." },
      { label: "Pet", value: "Wolf • Ferocity", detail: `${entity("Furious Howl")} and ${entity("Call of the Wild")} add real group damage; a dead or passive pet does not.` },
      { label: "Core glyphs", value: `${item("Glyph of Serpent Sting", "q-rare")} • ${item("Glyph of Steady Shot", "q-rare")}`, detail: `${item("Glyph of Chimera Shot", "q-rare")} is the usual third major when latency permits the shorter cycle.` }
    ],
    engineTitle: "Sting → priority shots → movement weave → pet",
    beforeIcon: "ability_hunter_snipershot",
    firstIcon: "inv_misc_coin_01",
    before: [
      `${entity("Aspect of the Dragonhawk")} active; switch to ${entity("Aspect of the Viper")} only when mana requires it.`,
      `${entity("Trueshot Aura")} learned and active, ammo stocked, weapon durability checked, and the correct tracking type enabled.`,
      `Wolf summoned, fed, talented, healed, and on the intended passive/defensive setting.`,
      `${entity("Hunter's Mark")} applied by you unless the group assigns another hunter; set the tank as your ${entity("Misdirection")} focus.`,
      "Current hit checked after talents and gear. Count Heroic Presence only while a Draenei is actually in your party."
    ],
    firstMoves: [
      `Buy or farm a reliable ranged weapon; weapon DPS dominates small secondary-stat debates.`,
      `Build toward the level-83 hit cap without delaying normal or heroic dungeons while early gear fills in.`,
      `Learn ${entity("Serpent Sting")} → ${entity("Chimera Shot")} refresh timing on a target dummy.`,
      `Bind pet attack, pet follow, ${entity("Misdirection")}, ${entity("Feign Death")}, and ${entity("Tranquilizing Shot")}.`,
      `Practice moving during instant shots and stopping long enough for ${entity("Auto Shot")} and ${entity("Steady Shot")}.`
    ],
    chapterTopics: {
      playing: "Shot priority • opener • movement • Readiness • utility",
      setup: "7/57/7 talents • glyphs • wolf • macros • addons",
      building: "Hit cap • Agility • Armor Penetration • gems • enchants",
      equipping: "Fresh-80 weapons • trinkets • tier • ToC • ICC",
      raiding: "Misdirection • Tranq Shot • traps • kiting • encounter jobs"
    }
  },
  playing: {
    mistakeGroupLabel: "Group / raid mistakes",
    priority: `${entity("Kill Shot")} when usable → keep ${entity("Serpent Sting")} active through ${entity("Chimera Shot")} → ${entity("Chimera Shot")} → ${entity("Aimed Shot")} → ${entity("Arcane Shot")} in a fresh/low-Armor-Penetration set → ${entity("Steady Shot")}. Fire ${entity("Silencing Shot")} for damage only when it is not reserved for an interrupt.`,
    openerIcon: "ability_hunter_chimerashot2",
    trackingIcon: "ability_hunter_mastermarksman",
    opener: [
      `Apply ${entity("Hunter's Mark")} yourself unless the group assigns another hunter, and set the tank as focus.`,
      `Use ${entity("Misdirection")} during the countdown. Pre-pot ${item("Potion of Speed")} only for a planned boss attempt where the cost is worthwhile.`,
      `Send the pet, apply ${entity("Serpent Sting")}, then fire ${entity("Chimera Shot")} and ${entity("Aimed Shot")}.`,
      `Use ${entity("Rapid Fire")} and racial/on-use cooldowns in the first stable damage window.`,
      `After the first cooldown cycle, use ${entity("Readiness")} to reset key shots and ${entity("Rapid Fire")}; do not waste already-ready cooldowns.`
    ],
    tracking: [
      `${entity("Serpent Sting")} duration and the next ${entity("Chimera Shot")} cooldown.`,
      `${entity("Kill Shot")}, ${entity("Chimera Shot")}, ${entity("Aimed Shot")}, and ${entity("Readiness")} availability.`,
      `${entity("Auto Shot")} timer so movement ends before the next ranged swing.`,
      `${entity("Aspect of the Viper")} uptime—leave it immediately when the required mana has been recovered.`,
      `Pet health, target, range, ${entity("Furious Howl")}, and ${entity("Call of the Wild")}.`
    ],
    cards: [
      {
        kicker: "Normal cycle",
        title: "Single target",
        iconEntity: "Chimera Shot",
        tag: "Boss",
        decision: `Protect the ${entity("Chimera Shot")} refresh and never delay an available execute for a filler.`,
        actions: ["Serpent Sting", "Chimera Shot", "Aimed Shot", "Arcane Shot", "Steady Shot"],
        rules: [
          `${entity("Kill Shot")} jumps to the front below 20%.`,
          `${entity("Arcane Shot")} belongs in a fresh Agility set; a mature high-ArP set may drop it after testing.`,
          `${entity("Steady Shot")} fills real empty time—it does not outrank a ready signature shot.`
        ],
        failure: "Refreshing Serpent Sting manually after the opener, delaying Chimera, or hard-casting Steady while a higher-priority shot is ready."
      },
      {
        kicker: "Execution",
        title: "Movement and Auto Shot",
        iconEntity: "Auto Shot",
        tag: "Uptime",
        decision: "Spend instant-shot globals while moving, then plant before the next ranged swing or Steady cast.",
        actions: ["Aimed Shot", "Chimera Shot", "Disengage", "Auto Shot"],
        rules: [
          `${entity("Auto Shot")} fires while stationary and is not clipped by ${entity("Steady Shot")} in Wrath.`,
          `Use short stutter steps around the swing timer instead of running continuously.`,
          `${entity("Disengage")} is a positioning tool; verify the landing space before pressing it.`
        ],
        failure: "Treating every movement mechanic as continuous movement and losing several Auto Shots."
      },
      {
        kicker: "Cooldown reset",
        title: "Rapid Fire and Readiness",
        iconEntity: "Readiness",
        tag: "Burst",
        decision: "Spend the cooldowns Readiness can reset before pressing it, then use the second window where the boss permits full uptime.",
        actions: ["Rapid Fire", "Chimera Shot", "Aimed Shot", "Readiness", "Rapid Fire"],
        rules: [
          `Do not press ${entity("Readiness")} while ${entity("Rapid Fire")} and both main shots are already available.`,
          `Keep enough fight time after the reset to realize the second haste window.`,
          `A later boss mechanic can be a better Readiness anchor than the pull.`
        ],
        failure: "Resetting unused cooldowns or activating Rapid Fire immediately before forced movement."
      },
      {
        kicker: "Area damage",
        title: "Adds and cleave",
        iconEntity: "Volley",
        tag: "Multi-target",
        decision: "Burn priority adds first; use Volley only when several targets will remain stacked through the channel.",
        actions: ["Misdirection", "Multi-Shot", "Volley", "Explosive Trap"],
        rules: [
          `${entity("Multi-Shot")} is quick cleave but must not break crowd control.`,
          `${entity("Volley")} wins on stable packs, not on targets about to scatter or die.`,
          `${entity("Explosive Trap")} is feet-placement in baseline 3.3.5a; pre-position only when safe.`
        ],
        failure: "Channeling Volley while a priority add lives or assuming the later Classic ranged trap launcher exists."
      },
      {
        kicker: "Threat control",
        title: "Misdirection and survival",
        iconEntity: "Misdirection",
        tag: "Utility",
        decision: "Move initial or add threat to the assigned tank, then shed personal threat before it becomes an emergency.",
        actions: ["Misdirection", "Feign Death", "Deterrence", "Disengage"],
        rules: [
          `${entity("Misdirection")} is an assignment, not permission to shoot before the tank is ready.`,
          `${entity("Feign Death")} needs a deliberate cancel/stand-up plan so the hunter resumes damage.`,
          `${entity("Deterrence")} is a survival cooldown; confirm which raid mechanics it can actually deflect on Hellscream.`
        ],
        failure: "Misdirecting the wrong unit, feigning after the mob reaches the hunter, or gambling on an untested immunity."
      },
      {
        kicker: "Mana and pet",
        title: "Sustain the whole kit",
        iconEntity: "Aspect of the Viper",
        tag: "Resource",
        decision: "Recover only the mana needed while keeping the wolf alive and attacking the correct target.",
        actions: ["Aspect of the Viper", "Mend Pet", "Call of the Wild", "Aspect of the Dragonhawk"],
        rules: [
          `${entity("Aspect of the Viper")} is a temporary recovery state with a large damage penalty.`,
          `Use ${entity("Mend Pet")} before lethal pet damage, not after the wolf is already dead.`,
          `${entity("Call of the Wild")} belongs in a planned boss burst window rather than on an arbitrary trash pull; coordinate it once you begin raiding.`
        ],
        failure: "Leaving Viper active, losing the pet to avoidable damage, or letting the pet attack the wrong add."
      }
    ],
    utility: [
      [entity("Misdirection"), "Transfer opening or add threat to the assigned tank.", "Set focus before pull; verify the fallback target instead of silently misdirecting the pet."],
      [entity("Tranquilizing Shot"), "Remove an enrage or magic effect that the encounter requires.", "Fire on assignment and call a miss, immunity, or cooldown conflict."],
      [entity("Silencing Shot"), "Interrupt a cast or add off-global damage.", "If the raid assigned the interrupt, never bury it in every damage macro."],
      [entity("Frost Trap"), "Slow and control a route.", "Place before the add reaches the lane; traps arm after placement and baseline traps are dropped at the hunter."],
      [entity("Freezing Arrow"), "Ranged crowd control.", "Coordinate target and break protection; this is separate from the later Explosive Trap launcher."],
      [entity("Master's Call"), "Remove movement impairing effects and grant brief immunity.", "Use on the assigned player or self; confirm line and pet range."],
      [entity("Deterrence"), "Emergency physical/ranged avoidance.", "Treat encounter-specific coverage as a Hellscream test, not a universal immunity."],
      [entity("Feign Death"), "Drop threat and escape some target selections.", "Do not rely on it for a scripted mechanic until tested live."]
    ],
    mistakes: [
      "Starting a boss set below the real hit cap or carrying large wasted hit above it.",
      "Letting Chimera Shot drift and forcing a manual Serpent Sting refresh.",
      "Gemming Armor Penetration before the gear has enough native ArP to support it.",
      "Moving through Auto Shot windows instead of stutter-stepping around instant shots.",
      "Leaving Aspect of the Viper active after mana recovery.",
      "Treating the pet as passive background damage and losing Furious Howl or Call of the Wild.",
      "Macroing Silencing Shot into every attack when the raid expects a real interrupt.",
      "Copying WotLK Classic Trap Launcher advice into an original 3.3.5a client."
    ]
  },
  setup: {
    talentGroups: [
      { title: "Marksmanship core", icon: "ability_hunter_chimerashot2", items: [`${entity("Chimera Shot")}, ${entity("Aimed Shot")}, and ${entity("Readiness")} define the cycle.`, `${entity("Trueshot Aura")} is included because a fresh 80 cannot assume another class supplies the 10% attack-power buff.`, "Piercing Shots, Wild Quiver, and Improved Steady Shot reward clean weapon uptime."] },
      { title: "Fresh-80 support", icon: "ability_hunter_focusedaim", items: ["3/3 Focused Aim removes 3% from the level-83 hit requirement.", "Use 2/3 Improved Hunter's Mark so the self-contained build can include Trueshot Aura.", "Reallocate Focused Aim only after the character remains capped in the actual boss set."] },
      { title: "Survival branch", icon: "ability_hunter_lockandload", items: ["Improved Tracking rewards selecting the correct creature tracking.", "Survival Instincts improves core shots and survivability.", "This baseline avoids modern talents or Classic-era trap-launcher assumptions."] }
    ],
    extraSection: {
      id: "pet",
      short: "Pet",
      title: "Wolf and Ferocity setup",
      icon: "ability_hunter_pet_wolf",
      body: `<div class="two-col"><div class="guide-box"><h3>${icon("ability_hunter_pet_wolf", "ability-icon")} Recommended level-80 pet</h3>${list([
        `Wolf for ${entity("Furious Howl")}. Keep it alive, fed, and in range.`,
        `Use a level-80 Ferocity build centered on Cobra Reflexes, Dash, Bloodthirsty, Spiked Collar, Boar's Speed, Culling the Herd, Spider's Bite, Rabid, and ${entity("Call of the Wild")}.`,
        `${entity("Heart of the Phoenix")} is a strong progression recovery point; move only with a deliberate alternate plan.`
      ])}</div><div class="guide-box"><h3>${icon("ability_physical_taunt", "ability-icon")} Control rules</h3>${list([
        `Bind pet attack and pet follow separately. Do not make every ability permanently issue /petattack.`,
        `Keep Growl off for bosses. Leave ${entity("Cower")} off autocast unless pet survival demands it.`,
        `Use ${entity("Mend Pet")} early and pull the pet out of lethal ground effects.`,
        `Save ${entity("Call of the Wild")} for a planned boss burst; follow the raid's timing later when one is assigned.`
      ])}</div></div>`
    },
    glyphs: [
      [item("Glyph of Serpent Sting", "q-rare"), '<span class="must">Major • default</span>', "Extends Serpent Sting.", "Improves Chimera Shot's Serpent component and reduces refresh risk."],
      [item("Glyph of Steady Shot", "q-rare"), '<span class="must">Major • default</span>', "Raises Steady Shot damage while Serpent Sting is present.", "Serpent Sting should remain active for the full boss cycle."],
      [item("Glyph of Chimera Shot", "q-rare"), '<span class="must">Major • common</span>', "Shortens Chimera Shot cooldown by one second.", "Strong when latency and execution consistently support the tighter cycle."],
      [item("Glyph of Kill Shot", "q-rare"), '<span class="optional">Major • swap</span>', "Shortens Kill Shot cooldown.", "Valuable when the encounter has a long execute phase."],
      [item("Glyph of Feign Death", "q-rare"), '<span class="optional">Minor</span>', "Shortens Feign Death cooldown.", "Useful threat and encounter utility."],
      [item("Glyph of Mend Pet", "q-rare"), '<span class="optional">Minor</span>', "Improves pet happiness while Mend Pet ticks.", "Convenient pet upkeep."],
      [item("Glyph of Revive Pet", "q-rare"), '<span class="optional">Minor</span>', "Reduces pushback while reviving.", "Progression recovery when Heart of the Phoenix is unavailable."]
    ],
    macros: [
      { title: "Misdirection to focus", entity: "Misdirection", purpose: "Use a friendly focus; fall back to the living pet.", code: "#showtooltip Misdirection\n/cast [@focus,help,nodead][@pet,exists,nodead] Misdirection" },
      { title: "Mouseover Tranquilizing Shot", entity: "Tranquilizing Shot", purpose: "Tranq a hostile mouseover without dropping the boss target.", code: "#showtooltip Tranquilizing Shot\n/cast [@mouseover,harm,nodead][] Tranquilizing Shot" },
      { title: "Chimera plus free Silencing Shot", entity: "Chimera Shot", purpose: "Use only when Silencing Shot is not reserved for an interrupt.", code: "#showtooltip Chimera Shot\n/cast Silencing Shot\n/cast Chimera Shot" },
      { title: "Controlled pet attack", entity: "Kill Command", purpose: "Send the pet deliberately and trigger Kill Command when available.", code: "#showtooltip Kill Command\n/petattack [harm,nodead]\n/cast Kill Command" },
      { title: "Pet retreat", entity: "Mend Pet", purpose: "Pull the pet out immediately and start recovery.", code: "#showtooltip Mend Pet\n/petfollow\n/cast Mend Pet" },
      { title: "Aspect toggle", entity: "Aspect of the Viper", purpose: "Toggle between normal damage and temporary mana recovery.", code: "#showtooltip Aspect of the Viper\n/castsequence reset=10 Aspect of the Viper, Aspect of the Dragonhawk" }
    ],
    essentialAddons: [
      `<a href="addons.html?search=Deadly%20Boss%20Mods">Deadly Boss Mods</a> for movement, add, enrage, and target timers.`,
      `<a href="addons.html?search=WeakAuras">WeakAuras</a> or TellMeWhen for sting, shot cooldowns, Auto Shot, Viper, and pet buffs.`,
      `<a href="addons.html?search=Omen">Omen</a> for threat before and after Misdirection.`
    ],
    recommendedAddons: [
      "A swing timer that explicitly supports Auto Shot on the 3.3.5a client.",
      "Details/Recount for shot mix, pet uptime, aspect uptime, target swaps, and avoidable deaths.",
      "A range display and raid-frame setup that makes Misdirection, Master's Call, and Tranq assignments visible."
    ]
  },
  building: {
    stats: [
      ["Hit", '<span class="must">Build toward 8%</span>', "Prevents ranged attacks from missing a level-83 raid boss.", "8% is 262.32 rating, so use 263. With 3/3 Focused Aim, the eventual gear target is 5%, or 164 rating. Do not postpone normal or heroic dungeons while building it; count Heroic Presence only when the Draenei is in your party."],
      ["Weapon DPS", '<span class="must">Highest upgrade lever</span>', "Scales Auto Shot and weapon-based shots.", "A strong ranged-weapon upgrade can beat a cosmetically perfect secondary-stat item."],
      ["Agility", "Fresh-80 default", "Adds attack power and crit, and scales with percentage buffs when they are present.", "Gem Agility until a real simulation and sufficiently strong native-ArP set justify changing strategy."],
      ["Armor Penetration", "Powerful only with enough gear", "Raises physical damage by bypassing armor, up to 1,400 rating for 100%.", "Do not treat 1,400 as a fresh-80 target. Common proc soft caps are 722 with Needle-Encrusted Scorpion, 735 with Mjolnir Runestone, and 788 with Grim Toll."],
      ["Critical Strike", "Strong secondary", "Increases direct-shot damage and supports Piercing Shots.", "Crit remains valuable but does not replace hit or weapon DPS."],
      ["Attack Power", "Reliable throughput", "Raises shot, Auto Shot, and pet damage.", "Agility usually offers a stronger fresh-80 package after raid scaling."],
      ["Haste", "Lower priority", "Speeds Auto Shot and Steady Shot.", "Once Steady approaches the one-second global floor with raid effects, extra haste loses much of its filler value."]
    ],
    stages: [
      { title: "Fresh level 80", icon: "inv_misc_coin_01", items: ["Start normal and heroic dungeons while building toward the level-83 hit cap and a credible ranged weapon.", "Gem Agility, not an endgame Armor Penetration target.", "Use budget gems and enchants on temporary pieces; spend premium materials only on upgrades that will last."] },
      { title: "Raid-ready base", icon: "achievement_boss_general_nazgrim", items: ["Maintain 100% Serpent Sting through Chimera Shot.", "Keep the wolf alive and active for a full heroic or target-dummy session.", "Carry ammo, pet food, flasks, food, and speed potions."] },
      { title: "ArP transition", icon: "inv_misc_gear_01", items: ["Acquire strong native Armor Penetration gear first.", "Model the exact set, buffs, trinket proc, and latency before regemming.", "Keep the Agility gems if the tested gain is small or the set changes frequently."] }
    ],
    gems: [
      ["Meta", item("Relentless Earthsiege Diamond", "q-rare"), "Keep the current meta on a temporary helm", `Activate cheaply with ${item("Shifting Twilight Opal", "q-rare")} plus ${item("Deadly Monarch Topaz", "q-rare")}; use one ${item("Nightmare Tear")} later when the convenience is worth the cost.`],
      ["Red", item("Delicate Scarlet Ruby", "q-rare"), `${item("Delicate Cardinal Ruby")} on lasting gear`, "Use Agility by default. Consider Fractured Cardinal Ruby only after a validated Armor Penetration transition."],
      ["Yellow", item("Deadly Monarch Topaz", "q-rare"), `${item("Deadly Ametrine")} or a hit gem when needed`, "Match worthwhile Agility/crit bonuses or use hit only until capped; keep rare gems in temporary gear."],
      ["Blue", item("Shifting Twilight Opal", "q-rare"), item("Nightmare Tear"), "Use one efficient blue activator for the meta; ignore weak blue bonuses and do not overspend on a temporary item."],
      ["Profession", "Delicate Dragon's Eye", "Fractured Dragon's Eye", "Keep the same Agility-versus-ArP logic as ordinary gems."]
    ],
    enchants: [
      ["Head", item("Arcanum of Torment"), "Knights of the Ebon Blade revered in standard Wrath."],
      ["Shoulders", item("Greater Inscription of the Axe"), "Sons of Hodir exalted; use the lower inscription while progressing reputation."],
      ["Back", entity("Enchant Cloak - Major Agility", "enchant-name"), "Flexweave Underlay is a practical Engineering alternative."],
      ["Chest", entity("Enchant Chest - Powerful Stats", "enchant-name"), "Use a cheaper stats enchant on a temporary chest."],
      ["Wrists", entity("Enchant Bracers - Greater Assault", "enchant-name"), "Attack power is the standard damage option."],
      ["Hands", entity("Enchant Gloves - Crusher", "enchant-name"), `${entity("Enchant Gloves - Greater Assault", "enchant-name")} is the budget option; use Hyperspeed Accelerators for Engineering.`],
      ["Waist", item("Eternal Belt Buckle", "q-rare"), "Always add the extra socket to a lasting belt."],
      ["Legs", item("Icescale Leg Armor"), `${item("Nerubian Leg Armor", "q-rare")} is the fresh-80 budget option.`],
      ["Feet", entity("Enchant Boots - Tuskarr's Vitality", "enchant-name"), `${entity("Enchant Boots - Icewalker", "enchant-name")} only when the hit is genuinely needed.`],
      ["Two-handed weapon", entity("Enchant 2H Weapon - Massacre", "enchant-name"), `${entity("Enchant 2H Weapon - Greater Savagery", "enchant-name")} is the budget option; Scourgebane is only a narrow undead alternative.`],
      ["Ranged weapon", item("Heartseeker Scope"), "Use a cheaper valid scope on a temporary weapon; save Heartseeker for one that will last."]
    ],
    professions: [
      ["Engineering", "Hyperspeed Accelerators, Nitro Boosts, bombs, and Flexweave.", "Exceptional control and movement for a ranged physical DPS."],
      ["Jewelcrafting", "Three stronger Dragon's Eye gems.", "Flexible hit, Agility, or eventual ArP tuning."],
      ["Blacksmithing", "Two extra sockets.", "Flexible and scales with epic gems."],
      ["Leatherworking", "Fur Lining attack power and access to useful crafts.", "Strong static value and practical on a mail wearer."],
      ["Alchemy", "Stronger, longer flask and cheaper supplies.", "A sensible Hellscream economy choice even when not the paper maximum."]
    ]
  },
  equipping: {
    first: [
      ['<span class="must">Ranged weapon</span>', item("Drake-Mounted Crossbow", "q-rare"), "Cache of Eregos, heroic Oculus", "A strong first heroic target; weapon DPS matters immediately."],
      ['<span class="must">Ranged alternative</span>', item("Nesingwary 4000"), "Engineering BoE", "Crafted access when dungeon drops or the local loot path are unreliable."],
      ['<span class="must">Trinket</span>', item("Mirror of Truth"), "40 Emblems of Heroism", "Accessible crit with an attack-power proc."],
      ['<span class="must">Trinket</span>', item("Banner of Victory", "q-rare"), "Trial of the Champion, normal", "A practical Armor Penetration trinket that remains useful during gearing."],
      ['<span class="optional">BoE</span>', item("Darkmoon Card: Greatness"), "Nobles Deck / Darkmoon Faire", "The Agility version is excellent, but do not overpay on a low-pop economy."]
    ],
    fresh: [
      ["Ranged weapon", item("Felglacier Bolter"), "Pit of Saron, heroic", "Accessible high-item-level crossbow with useful physical stats."],
      ["Legs", item("Giantmaim Legguards"), "Leatherworking BoE", "Crafted mail with high Agility and Armor Penetration."],
      ["Wrists", item("Giantmaim Bracers"), "Leatherworking BoE", "An accessible crafted mail upgrade with Agility and Armor Penetration."],
      ["Trinket", item("Needle-Encrusted Scorpion"), "Devourer of Souls, heroic Forge of Souls", "ArP proc trinket; do not gem to its soft cap until the whole set supports it."],
      ["Any weak slot", "Highest usable heroic, reputation, or emblem upgrade", "Heroics and Northrend factions", "Repair item-level holes before forcing a theoretical endgame stat ratio."]
    ],
    emblems: [
      { title: "Heroism / Triumph", icon: "spell_holy_summonchampion", items: [`Buy ${item("Mirror of Truth")} if both trinkets are weak.`, "Use T9 to repair weak armor slots and establish the four-piece bonus.", "Keep enough hit while replacing early dungeon pieces."] },
      { title: "Frost", icon: "inv_misc_frostemblem_01", items: [`${item("Herkuml War Token")} is a stable haste/AP option, but compare it to raid trinkets.`, "Build toward the useful T10 set bonuses before scattering emblems across marginal offset pieces.", "Buy the largest real upgrade for the current set."] },
      { title: "Tier logic", icon: "inv_chest_chain_13", items: ["Marksmanship values the shot-focused T9/T10 bonuses.", "Compare the set bonus and replacement offset piece as one change.", "Keep alternate hit pieces so a tier upgrade does not break the cap."] }
    ],
    toc: [
      [item("Death's Verdict"), "Faction-specific 25-player Trial of the Crusader", "One of the strongest Agility/AP proc trinket families."],
      [item("Death's Head Crossbow"), "10-player Trial of the Crusader", "Strong raid-entry ranged weapon."],
      ["T9 Windrunner tier", "Triumph vendor / Trophy of the Crusade routes", "Efficient set progression with valuable shot bonuses."],
      ["High-item-level Agility and Armor Penetration mail", "ToC bosses and tribute routes", "Build native ArP without sacrificing the hit cap."]
    ],
    icc: [
      [item("Zod's Repeating Longbow"), "Lady Deathwhisper, 25-player", "Strong ICC ranged weapon with an extra-damage proc."],
      [item("Njorndar Bone Bow"), "Lady Deathwhisper, 10-player heroic", "Excellent ICC bow with Armor Penetration."],
      [item("Deathbringer's Will"), "Deathbringer Saurfang, 25-player", "Defining physical-DPS proc trinket with several class-appropriate outcomes."],
      [item("Whispering Fanged Skull"), "Lady Deathwhisper, 10-player", "Excellent crit and attack-power proc trinket."],
      [item("Fal'inrush, Defender of Quel'thalas"), "The Lich King, 25-player", "End-tier ranged weapon family."],
      [item("Sharpened Twilight Scale"), "Halion, 25-player", "Ruby Sanctum Armor Penetration proc trinket."]
    ],
    special: [
      ["Boss set", "Exactly hit-capped pieces", "Stable hit makes every later comparison trustworthy."],
      ["Proc soft-cap set", `${item("Needle-Encrusted Scorpion")}, ${item("Mjolnir Runestone")}, or ${item("Grim Toll")}`, "Only one exact soft-cap plan should drive gems; model the trinket and set together."],
      ["Kiting / utility", "Stamina, movement speed, and reliable hit", "The assignment succeeds before the damage meter matters."],
      ["Pet-danger fight", "Pet survival talents and manual control", "A living wolf preserves damage, Furious Howl, and Call of the Wild."]
    ]
  },
  raiding: {
    assignmentIcon: "ability_hunter_misdirection",
    entryNote: "This is a later progression chapter, not the starting expectation for a new level 80. Finish the self-contained setup, practice in normal and heroic dungeons, and enter raids only after the character and player are ready.",
    consumables: [
      `${item("Flask of Endless Rage")} for attack power.`,
      `${item("Blackened Dragonfin")} for Agility or ${item("Hearty Rhino")} for Armor Penetration only when the set's model supports it.`,
      `${item("Potion of Speed")} immediately before combat and again in the best legal burst window.`,
      `${item("Saronite Razorheads")} or the server's best valid ammunition, pet food, and a repaired ranged weapon.`
    ],
    prePull: [
      "Misdirection target and whether the pull or a later add wave receives it.",
      "Tranquilizing Shot and Silencing Shot assignments.",
      "Trap location, crowd-control target, and kiting route.",
      "Rapid Fire, Readiness, Call of the Wild, and potion timing.",
      "Pet target rules and any phase where the pet must be recalled."
    ],
    assignments: [
      ["Boss damage", "Serpent Sting remains active through Chimera; signature shots and Auto Shot retain high uptime.", "Call forced downtime or a target becoming immune."],
      ["Adds / control", "Priority adds die first and slows or traps protect the raid route.", "Call trap position, resist, broken control, or loose add."],
      ["Misdirection / Tranq", "Threat reaches the correct tank and required enrages are removed.", "Call the target and any miss, immunity, or cooldown."],
      ["Interrupt", "Silencing Shot stops the assigned cast instead of being consumed by a damage macro.", "Call successful interrupt and the next backup."],
      ["Special assignment", "Kiting, orb, suppressor, or realm duty succeeds without improvising a route.", "Call range, pet loss, target change, or route failure."]
    ],
    notes: [
      { encounter: "Trial of the Crusader", icon: "achievement_reputation_argentchampion", size: "10 25", difficulty: "normal heroic", role: "boss-damage add-control utility interrupt", sizeLabel: "10 / 25", difficultyLabel: "Normal / Heroic", roleLabel: "Damage / control", verify: false, text: `Use ${entity("Tranquilizing Shot")} on assigned enrages, spread for Legion Flame, and keep the pet out of avoidable hazards. On Anub'arak, help control burrowers with ${entity("Frost Trap")} when assigned and use ${entity("Volley")} only when stacked adds—not a priority target—justify it.` },
      { encounter: "Lord Marrowgar", icon: "achievement_boss_lordmarrowgar", size: "10 25", difficulty: "normal heroic", role: "boss-damage add-control", sizeLabel: "10 / 25", difficultyLabel: "Normal / Heroic", roleLabel: "Boss / spikes", verify: false, text: `Maintain boss damage, switch instantly to Bone Spikes, and use instant shots while relocating in Bone Storm. Recall or reposition the pet if its path would cross Coldflame; do not channel ${entity("Volley")} into a single urgent spike.` },
      { encounter: "Lady Deathwhisper", icon: "achievement_boss_ladydeathwhisper", size: "10 25", difficulty: "normal heroic", role: "add-control utility interrupt", sizeLabel: "10 / 25", difficultyLabel: "Normal / Heroic", roleLabel: "Adds / interrupt", verify: false, text: `Misdirect add waves to the assigned tank, follow physical-versus-magic add priority, and preserve ${entity("Silencing Shot")} for the assigned cast. Stay spread and move early from Death and Decay rather than finishing Steady Shot.` },
      { encounter: "Deathbringer Saurfang", icon: "achievement_boss_saurfang", size: "10 25", difficulty: "normal heroic", role: "boss-damage add-control special", sizeLabel: "10 / 25", difficultyLabel: "Normal / Heroic", roleLabel: "Boss / beasts", verify: false, text: `Use ${entity("Frost Trap")} or an assigned slow route before Blood Beasts reach the ranged group, switch immediately, and never let the pet or hunter be struck. Misdirection can stabilize beast pickup only if that is the raid's plan.` },
      { encounter: "Festergut and Rotface", icon: "achievement_boss_festergutrotface", size: "10 25", difficulty: "normal heroic", role: "boss-damage utility", sizeLabel: "10 / 25", difficultyLabel: "Normal / Heroic", roleLabel: "Boss / movement", verify: false, text: `Stutter-step to spores, slime, and infection drop points while protecting Auto Shot. Use ${entity("Deterrence")} only as a confirmed survival tool; it does not replace the required spore, movement, or raid positioning.` },
      { encounter: "Professor Putricide", icon: "achievement_boss_profputricide", size: "10 25", difficulty: "normal heroic", role: "add-control utility special", sizeLabel: "10 / 25", difficultyLabel: "Normal / Heroic", roleLabel: "Adds / utility", verify: false, text: `Misdirect and burst Volatile Ooze or Gas Cloud by priority, move before Malleable Goo, and trap only where placement will not endanger the raid. Baseline ${entity("Explosive Trap")} is dropped at the hunter's feet—there is no assumed ranged launcher.` },
      { encounter: "Blood Prince Council and Blood-Queen Lana'thel", icon: "achievement_boss_lanathel", size: "10 25", difficulty: "normal heroic", role: "boss-damage utility special", sizeLabel: "10 / 25", difficultyLabel: "Normal / Heroic", roleLabel: "Swap / bite", verify: false, text: `On Princes, damage only the empowered target and handle Kinetic Bombs if assigned without sending the pet across unsafe paths. On Blood-Queen, follow bite order, move early for Pact and Swarming Shadows, and plan cooldowns around the air phase.` },
      { encounter: "Valithria Dreamwalker", icon: "achievement_boss_valithriadreamwalker", size: "10 25", difficulty: "normal heroic", role: "add-control utility interrupt", sizeLabel: "10 / 25", difficultyLabel: "Normal / Heroic", roleLabel: "Adds / interrupt", verify: false, text: `Prioritize Blazing Skeletons and Suppressors, interrupt Frostbolt Volley when assigned, and Misdirect dangerous spawns. ${entity("Volley")} is useful on stable stacked packs but never outranks a Skeleton threatening Lay Waste.` },
      { encounter: "Sindragosa", icon: "achievement_boss_sindragosa", size: "10 25", difficulty: "normal heroic", role: "boss-damage utility special", sizeLabel: "10 / 25", difficultyLabel: "Normal / Heroic", roleLabel: "Boss / tombs", verify: false, text: `Stop shots before Instability becomes lethal, control pet uptime around air phases, and break only assigned Ice Tombs. In phase three, use tomb line-of-sight to reset Mystic Buffet and do not let uncontrolled pet attacks finish a tomb early.` },
      { encounter: "The Lich King", icon: "achievement_boss_lichking", size: "10 25", difficulty: "normal heroic", role: "boss-damage add-control utility interrupt special", sizeLabel: "10 / 25", difficultyLabel: "Normal / Heroic", roleLabel: "All roles", verify: true, text: `Misdirect Shambling Horrors or transition adds as assigned, ${entity("Tranquilizing Shot")} Enrage, burn Val'kyr, and control Raging Spirits. A hunter may kite or soak Vile Spirits with an encounter-specific plan, but ${entity("Deterrence")}, target behavior, and server scripting must be tested on Hellscream first.` },
      { encounter: "Halion", icon: "achievement_boss_halion", size: "10 25", difficulty: "normal heroic", role: "boss-damage utility special", sizeLabel: "10 / 25", difficultyLabel: "Normal / Heroic", roleLabel: "Realm damage", verify: false, text: `Stay in the assigned realm, move early with Fiery Combustion or Soul Consumption, and recall the pet before dangerous pathing. In twilight, plant between cutter rotations so Auto Shot and Steady Shot resume without drifting into the next beam.` }
    ]
  },
  sources: {
    quick: [
      ["Marksmanship Hunter talents and glyphs", "https://www.wowhead.com/wotlk/guide/classes/hunter/marksmanship/dps-talent-builds-glyphs-pve"],
      ["Marksmanship Hunter stat priority and hit cap", "https://www.wowhead.com/wotlk/guide/classes/hunter/marksmanship/dps-stat-priority-attributes-pve"]
    ],
    playing: [
      ["Marksmanship Hunter rotation and abilities", "https://www.wowhead.com/wotlk/guide/classes/hunter/marksmanship/dps-rotation-cooldowns-abilities-pve"],
      ["Chimera Shot spell data", "https://www.wowhead.com/wotlk/spell=53209"],
      ["Readiness spell data", "https://www.wowhead.com/wotlk/spell=23989"],
      ["Trap Launcher: Explosive Trap patch history", "https://warcraft.wiki.gg/wiki/Trap_Launcher%3A_Explosive_Trap"]
    ],
    setup: [
      ["Marksmanship Hunter 7/57/7 talent and glyph reference", "https://www.wowhead.com/wotlk/guide/classes/hunter/marksmanship/dps-talent-builds-glyphs-pve"],
      ["Filled fresh-80 7/57/7 talent calculator", "https://www.wowhead.com/wotlk/talent-calc/hunter/502-035325131030013233135031051-5000002"],
      ["Wolf pet family record", "https://www.wowhead.com/wotlk/pet=1/wolf"]
    ],
    building: [
      ["Marksmanship Hunter stat priority", "https://www.wowhead.com/wotlk/guide/classes/hunter/marksmanship/dps-stat-priority-attributes-pve"],
      ["Marksmanship Hunter gems and enchants", "https://www.wowhead.com/wotlk/guide/classes/hunter/marksmanship/dps-enchants-gems-pve"]
    ],
    equipping: [
      ["Marksmanship Hunter pre-raid gear", "https://www.wowhead.com/wotlk/guide/classes/hunter/marksmanship/dps-bis-gear-pre-raid-pve"],
      ["Marksmanship Hunter phase-four gear", "https://www.wowhead.com/wotlk/guide/classes/hunter/marksmanship/dps-bis-gear-pve-phase-4"],
      ["Needle-Encrusted Scorpion item record", "https://www.wowhead.com/wotlk/item=50198"],
      ["Deathbringer's Will item record", "https://www.wowhead.com/wotlk/item=50362"]
    ],
    raiding: [
      ["Icecrown Citadel raid overview", "https://www.wowhead.com/wotlk/zone=4812/icecrown-citadel"],
      ["Trial of the Crusader raid overview", "https://www.wowhead.com/wotlk/zone=4722/trial-of-the-crusader"],
      ["Ruby Sanctum raid overview", "https://www.wowhead.com/wotlk/zone=4987/the-ruby-sanctum"],
      ["Trap Launcher: Explosive Trap patch history", "https://warcraft.wiki.gg/wiki/Trap_Launcher%3A_Explosive_Trap"]
    ]
  }
};

function loadWarlockConfig(slug) {
  return JSON.parse(fs.readFileSync(path.join(root, "templates", "spec-guide", `${slug}.config.json`), "utf8"));
}

function warlockBuilding(specKey) {
  const hitCorrection = specKey === "affliction"
    ? "The 55/0/16 baseline includes 3/3 Suppression, so 14% from gear (about 367 rating) completes the self-contained level-83 target. Recalculate whenever talents or group effects change."
    : "The baseline has no personal spell-hit talent. Work toward 17% from gear (about 446 rating) for a level-83 target, then subtract only effects actually present.";
  const specStat = specKey === "demonology"
    ? ["Spirit", "Support-sensitive secondary", "Fel Armor and Demonic Aegis convert Spirit into personal spell power, which also strengthens Demonic Pact.", "Do not sacrifice large hit, spell-power, haste, or item-level gains merely to collect Spirit."]
    : ["Spirit", "Useful secondary", "Fel Armor and Glyph of Life Tap convert part of Spirit into spell power.", "Spirit is useful, not a reason to take healer gear from a stronger overall upgrade."];

  return {
    stats: [
      ["Spell hit", '<span class="must">First raid-boss progression target</span>', "Prevents offensive spells from missing the selected target.", hitCorrection],
      ["Spell Power", "First uncapped throughput stat", specKey === "demonology" ? "Raises personal damage and the spell power shared through Demonic Pact." : "Raises direct spells, damage-over-time effects, and most pet scaling.", "A larger item with several useful stats can beat a smaller piece that has only the preferred secondary."],
      ["Haste", "Strong after hit and spell power", "Shortens casts and the global cooldown; Glyph of Quick Decay also lets haste affect Corruption.", "32.79 haste rating is about 1% haste at level 80. Haste does not create a universal one-number cap for this Fresh-80 path."],
      ["Critical strike", "Useful secondary", "Raises direct-spell criticals and spec-specific procs; Affliction also gains periodic criticals through Pandemic.", "45.91 crit rating is about 1% spell crit at level 80, so compare the entire item rather than one rating line."],
      specStat,
      ["Intellect", "Useful but lower priority", "Adds mana and a small amount of spell critical chance; pets inherit part of it.", "Life Tap means mana pool size is rarely worth sacrificing major throughput upgrades."]
    ],
    stages: [
      { title: "Fresh level 80", icon: "inv_misc_coin_01", items: ["Enter normal and heroic dungeons immediately with trained spells, a controlled pet, Fel Armor, and a complete talent tree.", "Repair hit with ordinary dungeon, reputation, crafted, and inexpensive BoE pieces; use rare-quality gems and budget enchants on temporary gear.", "Replace leveling greens and empty trinket slots before chasing a final raid stat profile."] },
      { title: "Raid-ready base", icon: "achievement_boss_general_nazgrim", items: ["Know the exact level-83 hit target for the current talents and group.", "Carry complete glyphs, consumables, Soul Shards, a Healthstone, and a Soulstone.", "Practice pet recall, target swaps, movement globals, and threat recovery in heroic dungeons."] },
      { title: "Later progression", icon: "inv_misc_gear_01", items: ["Move into epic gems and premium enchants only when the piece will last.", "Maintain a small hit-swap set so upgrades do not silently move the character above or below the current cap.", "Compare set bonuses, trinket timing, and encounter-specific pet uptime as a complete loadout."] }
    ],
    gems: [
      ["Meta", item("Chaotic Skyflare Diamond", "q-rare"), "None for general damage", "Activate it with the required blue gems; verify the live tooltip before final socket planning."],
      ["Red", item("Runed Scarlet Ruby", "q-rare"), item("Runed Cardinal Ruby"), "Use the rare version on temporary gear and the epic version on lasting pieces."],
      ["Yellow hit repair", item("Veiled Monarch Topaz", "q-rare"), item("Veiled Ametrine"), "Use only until the exact set reaches its current hit target."],
      ["Yellow haste", "Rare-quality spell power / haste gem", item("Reckless Ametrine"), "Match a worthwhile socket bonus after hit is solved."],
      ["Blue / meta", item("Purified Twilight Opal", "q-rare"), item("Purified Dreadstone"), "Meet the meta with the least throughput loss; Nightmare Tear is a later convenience."],
      ["Any color", "Correctly colored budget gem", item("Nightmare Tear"), "Do not buy this merely to avoid planning two inexpensive gems."]
    ],
    enchants: [
      ["Head", item("Arcanum of Burning Mysteries"), "Kirin Tor revered in standard Wrath."],
      ["Shoulders", item("Greater Inscription of the Storm"), "Use the lower Sons of Hodir inscription while reputation is unfinished."],
      ["Back", entity("Enchant Cloak - Greater Speed", "enchant-name"), "A cheaper haste enchant is acceptable on a temporary cloak."],
      ["Chest", entity("Enchant Chest - Powerful Stats", "enchant-name"), "Use a cheaper all-stats enchant on a short-lived chest."],
      ["Wrists", entity("Enchant Bracers - Superior Spellpower", "enchant-name"), "Prioritize it on a bracer expected to survive several upgrades."],
      ["Hands", entity("Enchant Gloves - Exceptional Spellpower", "enchant-name"), "Engineering may use Hyperspeed Accelerators when the activation is deliberately timed."],
      ["Waist", item("Eternal Belt Buckle", "q-rare"), "Add the extra socket to a belt worth keeping."],
      ["Legs", item("Shining Spellthread", "q-rare"), `${item("Brilliant Spellthread")} is the later premium option.`],
      ["Feet", entity("Enchant Boots - Tuskarr's Vitality", "enchant-name"), "Movement speed commonly saves more damage and lives than a small stationary gain."],
      ["Weapon", entity("Enchant Weapon - Mighty Spellpower", "enchant-name"), `${entity("Enchant Weapon - Black Magic", "enchant-name")} is a later haste-proc comparison, not an automatic Fresh-80 purchase.`]
    ],
    professions: [
      ["Engineering", "Hyperspeed Accelerators, Nitro Boosts, bombs, and utility.", "Excellent when the active tools are actually bound and planned; never an assumed requirement."],
      ["Tailoring", "Lightweave Embroidery and useful caster crafts.", "Strong throughput with practical gearing value."],
      ["Jewelcrafting", "Three stronger Dragon's Eye gems.", "Flexible spell-power or hit repair."],
      ["Alchemy", "Improved flask and potion value.", "A practical low-population-server option for sustaining personal supplies."],
      ["Enchanting / Inscription", "Static ring enchants or a personal shoulder inscription.", "Reliable value; choose professions for the whole character and account, not one theoretical stat line."]
    ]
  };
}

function warlockEquipping(specKey) {
  const gearReason = specKey === "demonology"
    ? "Spell power and reliable pet uptime support both personal damage and Demonic Pact."
    : specKey === "affliction"
      ? "Hit, spell power, and haste stabilize the DoT and execute engine."
      : "Hit, spell power, and haste stabilize the short-cooldown fire priority.";
  return {
    first: [
      ['<span class="must">Hit trinket</span>', item("Mark of the War Prisoner", "q-rare"), "Cyanigosa, heroic Violet Hold", "A large early hit repair plus an on-use spell-power window."],
      ['<span class="must">Weapon</span>', item("Flameheart Spell Scalpel", "q-rare"), "Kirin Tor revered", "A deterministic reputation weapon when dungeon drops refuse to cooperate."],
      ['<span class="must">Off-hand</span>', item("Ward of the Violet Citadel", "q-epic"), "25 Emblems of Heroism", "A durable early off-hand that pairs with several accessible one-handed weapons."],
      ['<span class="optional">Throughput trinket</span>', item("Sundial of the Exiled", "q-epic"), "40 Emblems of Heroism", "A practical early critical-strike and spell-power proc trinket."],
      ['<span class="optional">Dungeon trinket</span>', item("Forge Ember", "q-rare"), "Sjonnir, heroic Halls of Stone", "A no-raid spell-power alternative while emblems go elsewhere."]
    ],
    fresh: [
      ["Shoulders", item("Dark Runic Mantle", "q-rare"), "Bind-on-equip world drop", "Compare its local price with the next reachable dungeon drop."],
      ["Chest", item("Spellweave Robe", "q-epic"), "Tailoring BoE", "A strong craft, but not worth bankrupting a character that still has several weak slots."],
      ["Hands", item("Ebonweave Gloves", "q-epic"), "Tailoring BoE", "Useful hit repair when the whole set needs it."],
      ["Feet", item("Sandals of Crimson Fury", "q-epic"), "Wyrmrest Accord exalted", "A deterministic reputation endpoint for an otherwise unreliable slot."],
      ["Ring", item("Ring of Northern Tears", "q-rare"), "Jewelcrafting BoE", "An accessible socketed hit option; buy only at a sensible local price."],
      ["Any weak slot", "Best normal, heroic, reputation, or affordable BoE upgrade", "Northrend five-player and faction progression", gearReason]
    ],
    emblems: [
      { title: "Heroism and Triumph", icon: "spell_holy_summonchampion", items: [`Use ${item("Ward of the Violet Citadel")} or ${item("Sundial of the Exiled")} when those slots are still weak.`, "Use Triumph catch-up pieces to repair the largest armor gaps.", "Do not save every emblem while wearing leveling gear."] },
      { title: "Tier progression", icon: "inv_chest_cloth_43", items: ["Build T9 as an accessible bridge, then compare T10 bonuses against the actual offset pieces available.", "Keep a coherent set first; a partial late-tier plan does not replace missing gems, enchants, or hit.", "Evaluate Affliction, Demonology, and Destruction set-bonus value separately."] },
      { title: "Frost", icon: "inv_misc_frostemblem_01", items: ["Buy the largest reliable upgrade or required tier piece first.", "Confirm that a purchase does not create an unplanned hit deficit.", "Retain useful old pieces for hit swaps or a second Warlock specialization."] }
    ],
    toc: [
      [item("Abyssal Rune", "q-rare"), "Normal Trial of the Champion", "Excellent catch-up haste proc with no raid lockout."],
      ["T9 Warlock set", "Triumph vendor and Trial of the Crusader routes", "Accessible set progression after the immediate five-player path."],
      ["Reign caster trinket family", "Anub'arak, 25-player", "Later direct-damage proc option; verify faction, mode, and exact item ID."],
      ["High-item-level weapon or off-hand", "Trial of the Crusader bosses", "Take the clean upgrade instead of waiting for one perfect list item."]
    ],
    icc: [
      [item("Nevermelting Ice Crystal", "q-epic"), "Scourgelord Tyrannus, heroic Pit of Saron", specKey === "affliction" ? "A catch-up critical-strike on-use with special Affliction snapshot considerations; test Hellscream behavior." : "A catch-up option whose on-use must be compared with ordinary trinket uptime."],
      [item("Muradin's Spyglass"), "Gunship Battle, 10-player", "A strong stack-building spell-power trinket for sustained casting."],
      [item("Dislodged Foreign Object"), "Rotface, 25-player", "A major later haste and spell-power proc target."],
      [item("Phylactery of the Nameless Lich"), "Sindragosa, 25-player", "A later critical-strike and spell-power proc target."],
      [item("Charred Twilight Scale"), "Halion, 25-player", "Ruby Sanctum endgame target; verify normal versus heroic item ID and raid priority."]
    ],
    special: [
      ["Hit repair", "Mark of the War Prisoner, Ebonweave Gloves, Ring of Northern Tears, and loose hit pieces", "Swap enough pieces to reach the current target without carrying large excess hit."],
      ["Movement", "Tuskarr's Vitality boots", "A small paper-stat loss can preserve full casts, pet control, and survival."],
      ["Second specialization", "Haste/crit and hit variants", "Do not vendor a useful alternate piece until the other Warlock spec's cap and priority are checked."],
      ["Pet-hostile encounter", "Personal-throughput trinket or offset", specKey === "demonology" ? "Felguard loss is a severe damage and Demonic Pact loss; solve pet survival before changing the whole set." : "Keep an alternative when pet uptime or proc behavior makes the normal choice unreliable."]
    ]
  };
}

const warlockEncounterBase = [
  ["toc", "Trial of the Crusader", "achievement_reputation_argentchampion", "single-target burst execute aoe pet utility"],
  ["marrowgar", "Lord Marrowgar", "achievement_boss_lordmarrowgar", "single-target burst multi-dot pet utility"],
  ["deathwhisper", "Lady Deathwhisper", "achievement_boss_ladydeathwhisper", "burst multi-dot aoe pet utility"],
  ["saurfang", "Deathbringer Saurfang", "achievement_boss_saurfang", "single-target burst execute pet utility"],
  ["putricide", "Professor Putricide", "achievement_boss_profputricide", "burst multi-dot execute pet utility"],
  ["blood-wing", "Blood Prince Council and Blood-Queen Lana'thel", "achievement_boss_lanathel", "single-target burst multi-dot pet utility"],
  ["valithria", "Valithria Dreamwalker", "achievement_boss_valithriadreamwalker", "burst multi-dot execute aoe pet utility"],
  ["sindragosa", "Sindragosa", "achievement_boss_sindragosa", "single-target burst pet utility"],
  ["lich-king", "The Lich King", "achievement_boss_lichking", "single-target burst multi-dot execute aoe pet utility special"],
  ["halion", "Halion", "achievement_boss_halion", "single-target burst pet utility special"]
];

function warlockRaiding(specKey, advice) {
  return {
    entryNote: "This chapter is later progression, not the starting expectation for a new level 80. Complete the self-contained setup, practice the priority and pet controls in normal and heroic dungeons, and enter raids only after the character and player are ready.",
    assignmentIcon: specKey === "affliction" ? "ability_warlock_haunt" : specKey === "demonology" ? "spell_shadow_demonicpact" : "ability_warlock_chaosbolt",
    consumables: [
      `${item("Flask of the Frost Wyrm")} for planned raid progression; it is not required for ordinary dungeon entry.`,
      `${item("Firecracker Salmon")} or ${item("Fish Feast")} for a practical spell-power food option.`,
      `${item("Potion of Speed")} for a planned haste window; ${item("Potion of Wild Magic")} is a critical-strike/spell-power alternative whose timing depends on the specialization.`,
      "Soul Shards, a Healthstone, a Soulstone, repaired gear, and the correct pet before the pull."
    ],
    prePull: [
      "Which curse or debuff the Warlock is responsible for and who covers it after a death or target swap.",
      "Primary target, add priority, crowd-control assignment, and whether the pet stays on the boss or swaps.",
      "Demonic Circle location and the movement mechanic it is intended to solve.",
      specKey === "demonology" ? "Metamorphosis windows, safe proximity opportunities, and Demonic Pact expectations." : specKey === "affliction" ? "Execute timing, long-lived multi-DoT targets, and any approved Corruption rollover plan." : "Imp Firebolt control, short-cooldown timing, and Shadowfury assignments.",
      "Soulstone target, Healthstone availability, and Soulshatter timing."
    ],
    assignments: [
      ["Boss damage", advice.assignmentBoss, "Call forced downtime, an immunity, or an unexpected target change."],
      ["Adds / swaps", advice.assignmentAdds, "Call the priority, crowd control, and whether the pet follows."],
      ["Curse / utility", "Maintain the assigned curse, use Banish or Fear only on designated targets, and keep Demonic Circle available for the planned mechanic.", "Call a resist, immunity, broken control, or missing debuff."],
      ["Pet control", advice.assignmentPet, "Call a pet death, pathing failure, or required recall."],
      ["Special phase", advice.assignmentSpecial, "Call execute, cooldown, realm, or soak readiness before the window starts."]
    ],
    notes: warlockEncounterBase.map(([key, encounter, iconName, role]) => ({
      encounter,
      icon: iconName,
      size: "10 25",
      difficulty: "normal heroic",
      role,
      sizeLabel: "10 / 25",
      difficultyLabel: "Normal / Heroic",
      roleLabel: key === "lich-king" ? "All roles" : "Damage / utility",
      verify: advice.verify.includes(key),
      text: advice.notes[key]
    }))
  };
}

function warlockSources(specKey) {
  const title = specKey[0].toUpperCase() + specKey.slice(1);
  const base = `https://www.wowhead.com/wotlk/guide/classes/warlock/${specKey}`;
  return {
    quick: [[`${title} Warlock talents and glyphs`, `${base}/dps-talent-builds-glyphs-pve`], [`${title} Warlock stats and hit assumptions`, `${base}/dps-stat-priority-attributes-pve`]],
    playing: [[`${title} Warlock rotation, cooldowns, and abilities`, `${base}/dps-rotation-cooldowns-abilities-pve`], ["Warlock spell records", "https://www.wowhead.com/wotlk/spells/abilities/warlock"]],
    setup: [[`${title} Warlock talents and glyphs`, `${base}/dps-talent-builds-glyphs-pve`], [`Filled ${title} talent calculator`, `https://www.wowhead.com/wotlk/talent-calc/${loadWarlockConfig(`${specKey}-warlock`).talent.wowheadPath}`]],
    building: [[`${title} Warlock stat priority`, `${base}/dps-stat-priority-attributes-pve`], [`${title} Warlock gems and enchants`, `${base}/dps-enchants-gems-pve`]],
    equipping: [[`${title} Warlock pre-raid gear`, `${base}/dps-bis-gear-pre-raid-pve`], [`${title} Warlock phase-four gear`, `${base}/dps-bis-gear-pve-phase-4`], ["Abyssal Rune item record", "https://www.wowhead.com/wotlk/item=47213"], ["Charred Twilight Scale item record", "https://www.wowhead.com/wotlk/item=54572"]],
    raiding: [["Icecrown Citadel raid overview", "https://www.wowhead.com/wotlk/zone=4812/icecrown-citadel"], ["Trial of the Crusader raid overview", "https://www.wowhead.com/wotlk/zone=4722/trial-of-the-crusader"], ["Ruby Sanctum raid overview", "https://www.wowhead.com/wotlk/zone=4987/the-ruby-sanctum"], ["Demonic Circle: Teleport spell record", "https://www.wowhead.com/wotlk/spell=48020"]]
  };
}

function makeWarlockSpec(config, content) {
  return {
    className: config.className,
    classSlug: config.classSlug,
    name: config.specName,
    shortName: config.specShortName,
    nickname: config.guideNickname,
    guideTypes: config.guideTypes,
    slug: config.specSlug,
    specKey: config.specKey,
    guideAudience: config.guideAudience,
    fresh80Policy: config.fresh80Policy,
    tooltipFile: config.tooltipFile,
    cacheKey: config.cacheKey,
    serverNote: config.serverNote,
    icons: config.icons,
    descriptions: config.pageDescriptions,
    mechanics: config.mechanics.map((mechanic) => ({ ...mechanic, iconEntity: mechanic.examples[0].name })),
    roleFilters: config.raidRoleFilters.map(({ value, label }) => [value, label]),
    talent: {
      points: config.talent.points,
      name: config.talent.name,
      summary: config.talent.summary,
      path: config.talent.wowheadPath
    },
    building: warlockBuilding(config.specKey),
    equipping: warlockEquipping(config.specKey),
    sources: warlockSources(config.specKey),
    ...content
  };
}

const afflictionWarlock = makeWarlockSpec(loadWarlockConfig("affliction-warlock"), {
  quick: {
    summaries: [
      { label: "Core job", value: "Keep valuable DoTs working", detail: "Choose targets by remaining life, maintain Haunt, and convert the final quarter into Drain Soul damage." },
      { label: "Default priority", value: "Haunt and DoTs before filler", detail: "Use Shadow Bolt only after required effects are established and likely to finish useful ticks." },
      { label: "Fresh-80 rule", value: "Build the set, not one cap", detail: "Work toward the correct hit target while replacing weak gear through normal and heroic dungeons." }
    ],
    engineTitle: "Prepare → establish → maintain → execute",
    beforeIcon: "spell_shadow_summonfelhunter",
    firstIcon: "inv_misc_coin_01",
    before: [
      `Use ${entity("Fel Armor")}, summon the ${entity("Felhunter")}, create a ${entity("Healthstone")}, and place a ${entity("Soulstone")} on the agreed target.`,
      `Carry enough Soul Shards for stones, summons, and ${entity("Drain Soul")} without filling every bag.`,
      `Confirm the assigned curse; use ${entity("Curse of the Elements")} when the group lacks the equivalent spell-damage debuff.`,
      `Set the pet to a controlled state and know the key for attack, follow, and ${entity("Spell Lock")}.`
    ],
    firstMoves: [
      "Train every level-80 rank and install the complete 55/0/16 baseline and glyph set.",
      "Enter normal and heroic dungeons immediately; the level-83 raid-boss hit cap is a progression target, not a five-player entry requirement.",
      "Replace leveling gear, secure two useful trinkets, and apply affordable gems and enchants to pieces that will last.",
      "Practice DoT life judgment and the 25% Drain Soul transition before advanced Corruption rollover optimization."
    ],
    chapterTopics: {
      playing: "DoTs · Haunt · execute · movement",
      setup: "55/0/16 · glyphs · pet · macros",
      building: "Hit · spell power · haste · budget",
      equipping: "Dungeons · emblems · ToC · ICC",
      raiding: "Curses · swaps · execute · boss notes"
    }
  },
  playing: {
    priority: `${entity("Fel Armor")} and the ${entity("Glyph of Life Tap")} buff → assigned curse → ${entity("Shadow Bolt")} to establish ${entity("Shadow Embrace")} → ${entity("Haunt")} → ${entity("Unstable Affliction")} → ${entity("Corruption")} → ${entity("Shadow Bolt")} filler above 25% → ${entity("Drain Soul")} filler below 25%.`,
    openerIcon: "ability_warlock_haunt",
    trackingIcon: "spell_shadow_abominationexplosion",
    opener: [
      `Use a safe pre-pull ${entity("Life Tap")} when ${entity("Glyph of Life Tap")} is equipped; enter combat with ${entity("Fel Armor")} and the Felhunter ready.`,
      `Precast ${entity("Shadow Bolt")} when the pull timer and tank allow it.`,
      `Apply ${entity("Haunt")}, ${entity("Unstable Affliction")}, the assigned curse, and ${entity("Corruption")} after the opening debuffs are established.`,
      "Do not delay the whole opener waiting for a raid buff or proc that may never arrive."
    ],
    tracking: [
      `${entity("Haunt")}, ${entity("Unstable Affliction")}, ${entity("Corruption")}, the assigned curse, and ${entity("Shadow Embrace")}.`,
      `${entity("Glyph of Life Tap")} buff, mana, health, threat, and ${entity("Soulshatter")}.`,
      "Target health at 35% and 25%, plus enough remaining life for each new DoT.",
      `Felhunter target, health, range, and ${entity("Spell Lock")} availability.`
    ],
    cards: [
      { kicker: "Durable target", title: "Build the full engine", tag: "Default", iconEntity: "Haunt", decision: "Use the complete priority when the target will live long enough for every maintenance global to pay back.", actions: ["Shadow Bolt", "Haunt", "Unstable Affliction", "Corruption"], rules: ["Establish Shadow Embrace before evaluating the opening Corruption.", "Refresh Haunt early enough that travel time does not create a debuff gap."], failure: "recasting every DoT early and replacing damaging ticks with maintenance globals." },
      { kicker: "Target below 25%", title: "Drain Soul execute", tag: "Execute", iconEntity: "Drain Soul", decision: "Replace Shadow Bolt filler with Drain Soul while required effects stay active.", actions: ["Haunt", "Unstable Affliction", "Drain Soul"], rules: ["Break the channel immediately after a tick when a required effect must be refreshed.", "Restart Drain Soul after movement or a refresh; never wait for a full 15-second channel."], failure: "clipping before ticks or letting Haunt and Unstable Affliction disappear during the strongest phase." },
      { kicker: "Second durable target", title: "Multi-DoT with a reason", tag: "Cleave", iconEntity: "Corruption", decision: "Add effects only when the target will survive long enough and the primary assignment remains safe.", actions: ["Corruption", "Unstable Affliction", "Haunt"], rules: ["Corruption is the cheapest durable extension; add longer setup only when life expectancy supports it.", "Haunt cannot reliably cover many targets; prioritize the assigned target."], failure: "blanketing short-lived adds and losing boss Haunt, execute ticks, or the required target swap." },
      { kicker: "Short-lived add", title: "Skip slow setup", tag: "Swap", iconEntity: "Shadow Bolt", decision: "Use direct damage or a minimal DoT package when the add will die before a full ramp pays back.", actions: ["Shadow Bolt", "Haunt", "Drain Soul"], rules: ["Use Drain Soul on an eligible dying target when it supports the assignment and shard supply.", "Follow the raid's kill target instead of padding durable side targets."], failure: "finishing a five-global setup after the add is already dead." },
      { kicker: "Forced movement", title: "Move on useful globals", tag: "Mobile", iconEntity: "Life Tap", decision: "Refresh only effects genuinely due, tap safely, command the pet, or reposition through Demonic Circle.", actions: ["Life Tap", "Corruption", "Demonic Circle: Teleport"], rules: ["Place Demonic Circle before the mechanic, not after movement has already begun.", "Do not Life Tap into lethal incoming damage."], failure: "manufacturing early DoT refreshes every time movement begins." },
      { kicker: "Stacked pack", title: "Seed stable targets", tag: "AoE", iconEntity: "Seed of Corruption", decision: "Use Seed of Corruption on a target likely to remain inside the pack until detonation.", actions: ["Seed of Corruption", "Rain of Fire", "Shadowfury"], rules: ["Choose Rain of Fire when the pack will die before repeated Seeds detonate.", "Respect crowd control and tank threat before opening with AoE."], failure: "seeding a target that leaves the stack or breaking assigned control." }
    ],
    utility: [
      [entity("Spell Lock"), "Felhunter interrupt", "Keep manual control when an assigned cast matters; pet range and target determine availability."],
      [entity("Curse of the Elements"), "Spell-damage debuff", "Use it when no equivalent effect is actually present; do not assume raid composition."],
      [entity("Demonic Circle: Teleport"), "Planned displacement", "Place the circle before the pull where it solves a known mechanic."],
      [entity("Soulshatter"), "Threat reduction", "Use before threat forces the tank or raid to react, not after the boss turns."],
      [entity("Banish"), "Demon or elemental control", "Coordinate the target and never refresh through a kill call."],
      [entity("Shadow Ward"), "Shadow mitigation", "Use for known shadow damage without treating it as immunity."]
    ],
    mistakes: [
      "Treating the priority as a fixed rotation and refreshing effects early.",
      "Using long DoTs on targets that will die before their final ticks.",
      "Missing Drain Soul ticks by clipping at arbitrary times.",
      "Allowing Haunt to fall because travel time was ignored.",
      "Life Tapping immediately before predictable lethal damage.",
      "Losing the Felhunter or assigned Spell Lock to uncontrolled pet movement."
    ]
  },
  setup: {
    talentGroups: [
      { title: "Affliction engine", icon: "ability_warlock_haunt", items: [`${entity("Everlasting Affliction")} lets Shadow Bolt, Haunt, and Drain Soul refresh Corruption.`, `${entity("Pandemic")} enables critical Corruption and Unstable Affliction ticks.`, `${entity("Death's Embrace")} and Drain Soul define the execute transition.`] },
      { title: "Self-contained hit", icon: "spell_shadow_unsummonbuilding", items: [`Three points in ${entity("Suppression")} provide 3% spell hit for all schools in Wrath.`, "The baseline therefore needs 14% from gear for a level-83 target before counting real group effects.", "Do not remove Suppression until the replacement set and group assumptions are explicit."] },
      { title: "Legitimate flex", icon: "spell_shadow_shadowbolt", items: ["Threat, range, and pushback talents can be adjusted for a known encounter or stable raid environment.", "Any later swap must preserve 71 allocated points and state the new hit requirement.", "Advanced Corruption snapshot tools belong after the basic priority is reliable."] }
    ],
    glyphs: [
      [entity("Glyph of Life Tap", "glyph-name"), '<span class="must">Default</span>', "All content", "Converts a portion of Spirit into a timed spell-power buff after Life Tap."],
      [entity("Glyph of Quick Decay", "glyph-name"), '<span class="must">Default</span>', "All content", "Allows haste to shorten Corruption's tick interval."],
      [entity("Glyph of Haunt", "glyph-name"), '<span class="must">Default</span>', "Single target", "Raises Haunt's periodic-damage bonus."],
      [entity("Glyph of Drain Soul", "glyph-name"), '<span class="optional">Minor</span>', "Shard supply", "Adds a chance to gain an extra Soul Shard from Drain Soul."],
      [entity("Glyph of Unending Breath", "glyph-name"), '<span class="optional">Minor</span>', "Convenience", "Adds swim speed to Unending Breath."],
      [entity("Glyph of Souls", "glyph-name"), '<span class="optional">Minor</span>', "Group setup", "Reduces the mana cost of Ritual of Souls."]
    ],
    extraSection: { id: "pet", short: "Pet", title: "Felhunter control", icon: "spell_shadow_summonfelhunter", body: `<div class="two-col"><div class="guide-box"><h3>Default state</h3>${list(["Use the Felhunter for sustained damage and Spell Lock utility.", "Bind pet attack, follow, and passive so target swaps and hazards do not decide for you.", "Keep Spell Lock available manually when assigned to interrupt."])}</div><div class="guide-box"><h3>When the pet is unsafe</h3>${list(["Recall before transitions and ground hazards.", "Resummon only when the cast or Soul Shard cost will not fail the current mechanic.", "Report pet death when it removes an interrupt or meaningful damage."])}</div></div>` },
    macros: [
      { title: "Focus Spell Lock", entity: "Spell Lock", purpose: "Interrupt the focus without changing the damage target; fall back to the current hostile target.", code: "#showtooltip Spell Lock\n/cast [@focus,harm,nodead][] Spell Lock" },
      { title: "Controlled pet attack", entity: "Shadow Bolt", purpose: "Start the filler and send the Felhunter to the selected target.", code: "#showtooltip Shadow Bolt\n/petattack [harm,nodead]\n/cast Shadow Bolt" },
      { title: "Stop and follow", entity: "Summon Felhunter", purpose: "Recall the pet immediately from a hazardous target or path.", code: "/petpassive\n/petfollow" },
      { title: "Demonic Circle return", entity: "Demonic Circle: Teleport", purpose: "Return to the pre-placed circle without a modern cursor command.", code: "#showtooltip Demonic Circle: Teleport\n/cast Demonic Circle: Teleport" }
    ],
    essentialAddons: [`<a href="addons.html?search=Deadly%20Boss%20Mods">Deadly Boss Mods</a> for movement, phase, and execute timing.`, "A 3.3.5-compatible DoT timer that separates each target and shows Haunt travel or expiration clearly.", "A cast/channel bar that exposes Drain Soul ticks and latency."],
    recommendedAddons: [`WeakAuras/TellMeWhen for ${entity("Shadow Embrace")}, ${entity("Glyph of Life Tap")}, execute health, and pet state.`, "Details/Recount to review target damage, DoT uptime, execute damage, misses, threat, and pet uptime.", "A threat display that makes Soulshatter timing visible before aggro is lost."]
  },
  raiding: warlockRaiding("affliction", {
    assignmentBoss: "Haunt, required DoTs, and the assigned curse remain active; Drain Soul takes over below 25%.",
    assignmentAdds: "Long-lived secondary targets receive deliberate DoTs; urgent short-lived adds receive immediate useful damage.",
    assignmentPet: "The Felhunter stays alive, attacks the approved target, and keeps Spell Lock available when assigned.",
    assignmentSpecial: "Execute, multi-DoT, and Demonic Circle plans are chosen before the phase begins.",
    verify: ["lich-king"],
    notes: {
      toc: `Maintain the assigned curse and durable DoTs, but respect target immunities and kill order. On Anub'arak, prepare ${entity("Drain Soul")} for the boss execute while using ${entity("Seed of Corruption")} only on controlled stacked adds that will live to detonate.`,
      marrowgar: `Keep boss effects running, switch immediately to Bone Spikes, and use movement globals during Bone Storm. The ${entity("Felhunter")} must not chase through Coldflame or delay a required ${entity("Spell Lock")}.`,
      deathwhisper: `Follow the add priority instead of blanketing every target. Maintain useful effects on the shielded boss only when the assignment permits, preserve Spell Lock for the called caster, and move early from Death and Decay.`,
      saurfang: `Keep the full boss engine active and use direct damage on Blood Beasts only when assigned. Do not place long DoTs on beasts that must die quickly and must never reach a player.`,
      putricide: `Switch hard to Volatile Ooze and Gas Cloud; apply DoTs only when the add will live long enough. Place ${entity("Demonic Circle: Summon")} for planned movement, avoid Malleable Goo, and follow the heroic plague route.`,
      "blood-wing": `On Princes, damage only the empowered target and avoid slow ramp on Kinetic Bombs. On Blood-Queen, maintain effects through movement, follow bite order, and use instant globals while dropping Swarming Shadows.`,
      valithria: `Prioritize Blazing Skeletons and Suppressors, use ${entity("Seed of Corruption")} only on stable stacked packs, and preserve Spell Lock for an assigned Frostbolt Volley. This is add control, not a meter-padding multi-DoT exercise.`,
      sindragosa: `Manage Unchained Magic and Instability; stop casting before stacks become lethal. Do not allow lingering DoTs to destroy an Ice Tomb early, and use the tomb line for Mystic Buffet resets.`,
      "lich-king": `Maintain boss effects through predictable movement, burn Val'kyr and Raging Spirits by priority, and begin ${entity("Drain Soul")} below 25% only when mechanics permit the channel. Verify Hellscream's Corruption rollover and Vile Spirit targeting before building a special plan around them.`,
      halion: `Stay in the assigned realm, maintain the boss package while moving early for combustion or consumption, and pre-place Demonic Circle around cutter movement. Keep the Felhunter inside a safe path and on the correct realm target.`
    }
  })
});

const demonologyWarlock = makeWarlockSpec(loadWarlockConfig("demonology-warlock"), {
  quick: {
    summaries: [
      { label: "Core job", value: "Keep the Felguard and caster working", detail: "The specialization loses personal damage and raid support when the pet is dead, idle, or attacking the wrong target." },
      { label: "Default priority", value: "DoTs → proc filler → execute", detail: "Shadow Bolt normally, Incinerate for Molten Core, then Soul Fire during Decimation." },
      { label: "Fresh-80 rule", value: "Safe demon windows first", detail: "Metamorphosis is valuable at range; Immolation Aura is optional when proximity is actually safe." }
    ],
    engineTitle: "Control pet → maintain → react → transform",
    beforeIcon: "spell_shadow_summonfelguard",
    firstIcon: "inv_misc_coin_01",
    before: [
      `Use ${entity("Fel Armor")}, summon the ${entity("Felguard")}, create a ${entity("Healthstone")}, and place a ${entity("Soulstone")} on the agreed target.`,
      `Bind pet attack, follow, passive, ${entity("Cleave")}, and ${entity("Intercept")} rather than trusting every automatic decision.`,
      `Confirm the assigned curse; use ${entity("Curse of the Elements")} when the group lacks the equivalent spell-damage debuff.`,
      `Know the first ${entity("Metamorphosis")} window and whether approaching the target is safe or unnecessary.`
    ],
    firstMoves: [
      "Train every level-80 rank and install the complete 0/56/15 baseline and glyph set.",
      "Enter normal and heroic dungeons immediately; practice keeping the Felguard alive and on the selected target.",
      "Replace leveling gear and work toward the level-83 hit target without treating it as a dungeon-entry gate.",
      "Learn the three filler states before attempting close-range Metamorphosis optimization."
    ],
    chapterTopics: {
      playing: "Felguard · Molten Core · Decimation · Meta",
      setup: "0/56/15 · glyphs · pet · macros",
      building: "Hit · spell power · Spirit · haste",
      equipping: "Dungeons · emblems · ToC · ICC",
      raiding: "Demonic Pact · Meta · execute · boss notes"
    }
  },
  playing: {
    priority: `${entity("Fel Armor")} and ${entity("Glyph of Life Tap")} buff → ${entity("Metamorphosis")} in a useful planned window → assigned curse → ${entity("Corruption")} → ${entity("Immolate")} → ${entity("Shadow Bolt")} filler → ${entity("Incinerate")} during ${entity("Molten Core")} → ${entity("Soul Fire")} during ${entity("Decimation")}.`,
    openerIcon: "spell_shadow_demonform",
    trackingIcon: "ability_warlock_moltencore",
    opener: [
      `Use a safe pre-pull ${entity("Life Tap")} when ${entity("Glyph of Life Tap")} is equipped; start with Fel Armor and the Felguard ready.`,
      `Precast ${entity("Shadow Bolt")} when the tank and pull timer allow it, then send the Felguard.`,
      `Apply the assigned curse, ${entity("Corruption")}, and ${entity("Immolate")}.`,
      `Use ${entity("Metamorphosis")} early only when the full window will connect; proximity abilities are a separate safety decision.`
    ],
    tracking: [
      `${entity("Corruption")}, ${entity("Immolate")}, assigned curse, ${entity("Molten Core")}, and ${entity("Decimation")}.`,
      `${entity("Metamorphosis")}, ${entity("Demonic Empowerment")}, ${entity("Glyph of Life Tap")}, mana, health, and threat.`,
      `Felguard target, health, range, ${entity("Cleave")}, and movement path.`,
      `${entity("Demonic Pact")} presence as a diagnostic; reliable pet uptime comes before proc micromanagement.`
    ],
    cards: [
      { kicker: "Ordinary target", title: "Run the base priority", tag: "Default", iconEntity: "Shadow Bolt", decision: "Maintain the required effects and use Shadow Bolt while no stronger proc state is active.", actions: ["Corruption", "Immolate", "Shadow Bolt"], rules: ["Corruption remains valuable because it can trigger Molten Core.", "Use Curse of Doom only when it has time to complete; otherwise choose the assigned utility or shorter damage curse."], failure: "casting Incinerate without Molten Core or losing Corruption while waiting for a proc." },
      { kicker: "Molten Core active", title: "Switch to Incinerate", tag: "Proc", iconEntity: "Molten Core", decision: "Use the proc on Incinerate while maintaining higher-priority effects.", actions: ["Molten Core", "Incinerate", "Immolate"], rules: ["Do not let the proc distract from an urgent target switch or expiring effect.", "If Decimation is active, Soul Fire takes precedence."], failure: "continuing Shadow Bolt through the proc or consuming the phase on a dying target." },
      { kicker: "Target below 35%", title: "Soul Fire execute", tag: "Execute", iconEntity: "Decimation", decision: "Use instant-access Decimation procs to make Soul Fire the filler while required effects stay active.", actions: ["Decimation", "Soul Fire", "Corruption"], rules: ["A low-health add can activate Decimation for damage on the assigned target.", "Keep Corruption and Immolate only when their remaining ticks justify the globals."], failure: "ignoring Decimation or spamming Soul Fire after the proc has fallen." },
      { kicker: "Planned cooldown", title: "Use Metamorphosis safely", tag: "Cooldown", iconEntity: "Metamorphosis", decision: "Choose a window with continuous target access; add proximity abilities only if the position is safe.", actions: ["Metamorphosis", "Immolation Aura", "Shadow Cleave"], rules: ["Metamorphosis still grants ranged damage even when melee range is unsafe.", "Demon Charge costs a global and is a movement tool, not a mandatory opener."], failure: "charging into a lethal mechanic to chase optional Immolation Aura ticks." },
      { kicker: "Pet movement", title: "Protect the Felguard", tag: "Pet", iconEntity: "Summon Felguard", decision: "Recall or redirect before the pet crosses hazards, attacks an immune target, or misses the next assigned enemy.", actions: ["Demonic Empowerment", "Cleave", "Intercept"], rules: ["Use Demonic Empowerment when the pet can actually attack.", "Turn off automatic Intercept when an unintended charge would kill or misposition the pet."], failure: "losing both Felguard damage and Demonic Pact because follow was never bound." },
      { kicker: "Stacked enemies", title: "Choose controlled AoE", tag: "AoE", iconEntity: "Seed of Corruption", decision: "Use Seed on durable stacks and Metamorphosis proximity tools only where tank threat and mechanics permit.", actions: ["Seed of Corruption", "Metamorphosis", "Immolation Aura"], rules: ["Rain of Fire is a simpler ranged choice when Seeds will not detonate reliably.", "Keep the Felguard on the approved target instead of letting Cleave break control."], failure: "opening at close range before threat exists or breaking crowd control with pet Cleave." }
    ],
    utility: [
      [entity("Demonic Empowerment"), "Felguard throughput cooldown", "Use when the Felguard is in range and attacking; it is off the global cooldown."],
      [entity("Demonic Pact"), "Raid spell-power support", "It follows Felguard critical hits and the Warlock's spell power; pet uptime is the first requirement."],
      [entity("Demonic Circle: Teleport"), "Planned displacement", "Place the circle before the mechanic where it preserves casting or exits proximity safely."],
      [entity("Soulshatter"), "Threat reduction", "Use before Metamorphosis or execute threat becomes a tank problem."],
      [entity("Banish"), "Demon or elemental control", "Coordinate the target and pet Cleave before applying it."],
      [entity("Shadow Ward"), "Shadow mitigation", "Use for known shadow damage; it does not make unsafe proximity acceptable."]
    ],
    mistakes: [
      "Treating Shadow Bolt, Incinerate, and Soul Fire as interchangeable fillers.",
      "Letting Corruption fall and then wondering why Molten Core never appears.",
      "Using Metamorphosis during forced downtime or an immediate target immunity.",
      "Charging into melee range when ranged Metamorphosis was the safe choice.",
      "Allowing the Felguard to die, idle, or attack an immune target.",
      "Chasing a larger Demonic Pact number before personal setup and pet uptime are reliable."
    ]
  },
  setup: {
    talentGroups: [
      { title: "Pet foundation", icon: "spell_shadow_summonfelguard", items: [`${entity("Summon Felguard")} supplies the specialization's primary pet.`, `${entity("Demonic Knowledge")} turns inherited pet stats into personal spell power.`, `${entity("Demonic Empowerment")} is a frequent off-global pet cooldown.`] },
      { title: "Proc engine", icon: "ability_warlock_moltencore", items: [`${entity("Molten Core")} turns Corruption ticks into stronger, faster fire fillers.`, `${entity("Decimation")} makes Soul Fire the execute filler below 35%.`, `${entity("Demonic Pact")} converts reliable Felguard criticals into raid support.`] },
      { title: "Real flex points", icon: "spell_shadow_demonform", items: ["Pet healing, pushback, and threat options can move for a known environment.", "Early hit talents are an explicit alternate build and change the gear requirement; they are not silently assumed here.", "Any swap must preserve the complete Felguard, Demonic Pact, and Metamorphosis engine."] }
    ],
    glyphs: [
      [entity("Glyph of Life Tap", "glyph-name"), '<span class="must">Default</span>', "All content", "Converts a portion of Spirit into a timed spell-power buff."],
      [entity("Glyph of Felguard", "glyph-name"), '<span class="must">Default</span>', "Pet uptime", "Raises Felguard attack power and therefore its sustained damage."],
      [entity("Glyph of Quick Decay", "glyph-name"), '<span class="must">Default</span>', "Proc engine", "Lets haste accelerate Corruption and its Molten Core opportunities."],
      [entity("Glyph of Metamorphosis", "glyph-name"), '<span class="optional">Encounter swap</span>', "Long cooldown window", "Extends Metamorphosis; compare it only when the full extra duration remains useful."],
      [entity("Glyph of Drain Soul", "glyph-name"), '<span class="optional">Minor</span>', "Shard supply", "Adds a chance to gain an extra Soul Shard from Drain Soul."],
      [entity("Glyph of Souls", "glyph-name"), '<span class="optional">Minor</span>', "Group setup", "Reduces Ritual of Souls mana cost."]
    ],
    extraSection: { id: "pet", short: "Pet", title: "Felguard control", icon: "spell_shadow_summonfelguard", body: `<div class="two-col"><div class="guide-box"><h3>Damage controls</h3>${list(["Bind attack, follow, passive, Cleave, and Intercept.", "Use Demonic Empowerment when the Felguard has target uptime.", "Pet criticals maintain Demonic Pact; an idle pet provides neither damage nor support."])}</div><div class="guide-box"><h3>Survival controls</h3>${list(["Recall before transitions, void zones, and unsafe pathing.", "Disable automatic Intercept when a charge would cross mechanics.", "Resummon only when the current assignment can spare the cast and shard."])}</div></div>` },
    macros: [
      { title: "Empowered Shadow Bolt", entity: "Shadow Bolt", purpose: "Use the ordinary filler, command the Felguard, and activate Demonic Empowerment when available.", code: "#showtooltip Shadow Bolt\n/petattack [harm,nodead]\n/cast Demonic Empowerment\n/cast Shadow Bolt" },
      { title: "Controlled Soul Fire", entity: "Soul Fire", purpose: "Use the execute filler without changing the Felguard's selected target automatically.", code: "#showtooltip Soul Fire\n/cast Soul Fire" },
      { title: "Stop and follow", entity: "Summon Felguard", purpose: "Recall the Felguard immediately from a hazard or immune target.", code: "/petpassive\n/petfollow" },
      { title: "Demonic Circle return", entity: "Demonic Circle: Teleport", purpose: "Exit a planned proximity window or mechanic through the pre-placed circle.", code: "#showtooltip Demonic Circle: Teleport\n/cast Demonic Circle: Teleport" }
    ],
    essentialAddons: [`<a href="addons.html?search=Deadly%20Boss%20Mods">Deadly Boss Mods</a> for Metamorphosis access, movement, and execute timing.`, "A pet frame with clear health, target, range, and action feedback.", "A 3.3.5-compatible proc display for Molten Core and Decimation."],
    recommendedAddons: [`WeakAuras/TellMeWhen for ${entity("Molten Core")}, ${entity("Decimation")}, ${entity("Metamorphosis")}, and ${entity("Demonic Empowerment")}.`, "Details/Recount to review player and Felguard damage, pet target uptime, misses, and execute usage.", "A threat display for planned Soulshatter before Metamorphosis or execute windows."]
  },
  raiding: warlockRaiding("demonology", {
    assignmentBoss: "Corruption, Immolate, the assigned curse, and the correct filler state remain active; Metamorphosis is used in a full useful window.",
    assignmentAdds: "Priority adds are switched immediately, low-health targets supply Decimation only when the raid assignment permits, and Soul Fire returns to the approved target.",
    assignmentPet: "The Felguard remains alive and on target so personal damage and Demonic Pact remain reliable.",
    assignmentSpecial: "Metamorphosis proximity, execute targets, Demonic Circle, and pet recall are decided before the phase.",
    verify: ["toc", "lich-king"],
    notes: {
      toc: `Maintain the assigned curse and pet uptime across target changes. On Anub'arak, use low-health adds for ${entity("Decimation")} only when the raid's damage plan permits, and verify Hellscream's proc behavior before relying on a specific execute-sniping route.`,
      marrowgar: `Keep boss effects running, switch to Bone Spikes immediately, and preserve the Felguard through Coldflame and Bone Storm. Use ${entity("Metamorphosis")} at range if melee access is unsafe.`,
      deathwhisper: `Follow add priority, keep the Felguard on the called target, and avoid uncontrolled Cleave around crowd control. Save a Metamorphosis window for a wave only when it does not sacrifice continuous boss or priority-add access.`,
      saurfang: `Keep the Felguard on the boss unless the raid explicitly assigns pet swaps. Use direct damage on Blood Beasts, exploit ${entity("Decimation")} only without compromising control, and never approach for Immolation Aura.`,
      putricide: `Switch hard to Volatile Ooze and Gas Cloud, keep the pet out of slime and bad paths, and move before Malleable Goo. A safe full ranged Metamorphosis window is better than a short lethal proximity attempt.`,
      "blood-wing": `On Princes, damage only the empowered target and redirect the Felguard promptly. On Blood-Queen, follow bite order, preserve pet uptime through movement, and align Metamorphosis with a full ground phase rather than the air transition.`,
      valithria: `Prioritize Blazing Skeletons and Suppressors, use ${entity("Seed of Corruption")} on stable stacks, and redirect the Felguard without cleaving controlled targets. Low-health adds can feed Decimation for the next priority target.`,
      sindragosa: `Manage Unchained Magic and Instability, recall the Felguard for unsafe air transitions, and break only assigned tombs. Use Metamorphosis at range if phase-three proximity cannot be maintained safely.`,
      "lich-king": `Keep boss effects and the Felguard active, burn Val'kyr and Raging Spirits by priority, and use ${entity("Decimation")} from eligible adds only within the raid plan. Verify Hellscream pet pathing, Demonic Pact overwrites, and Vile Spirit behavior before adopting a specialized proximity route.`,
      halion: `Stay in the assigned realm, pre-place Demonic Circle for cutter movement, and recall the Felguard before dangerous realm or path transitions. Treat Immolation Aura as optional; ranged Metamorphosis damage remains useful.`
    }
  })
});

const destructionWarlock = makeWarlockSpec(loadWarlockConfig("destruction-warlock"), {
  quick: {
    summaries: [
      { label: "Core job", value: "Keep the fire priority moving", detail: "Maintain Immolate, use Conflagrate and Chaos Bolt on useful cooldowns, and fill with Incinerate." },
      { label: "Default priority", value: "Immolate → Conflag → Chaos Bolt", detail: "The sequence is a priority, not a loop; target life and cooldown readiness decide the next cast." },
      { label: "Fresh-80 rule", value: "Control the Imp", detail: "The pet contributes damage and Blood Pact only while alive, in range, and attacking the approved target." }
    ],
    engineTitle: "Prepare → maintain → burst → fill",
    beforeIcon: "spell_shadow_summonimp",
    firstIcon: "inv_misc_coin_01",
    before: [
      `Use ${entity("Fel Armor")}, summon the ${entity("Imp")}, create a ${entity("Healthstone")}, and place a ${entity("Soulstone")} on the agreed target.`,
      `Bind pet attack, follow, and passive; decide whether ${entity("Firebolt")} is manually queued or left automatic.`,
      `Confirm the assigned curse; use ${entity("Curse of the Elements")} when the group lacks the equivalent spell-damage debuff.`,
      `Know whether ${entity("Shadowfury")} is a damage button or an assigned control tool on the next pull.`
    ],
    firstMoves: [
      "Train every level-80 rank and install the fully allocated 0/19/52 baseline and glyph set.",
      "Enter normal and heroic dungeons immediately; the level-83 hit target is later raid progression, not a five-player entrance exam.",
      "Replace leveling gear, secure two useful trinkets, and practice moving during Life Tap or instant-cast globals.",
      "Learn the short-cooldown priority and Imp recall before adding advanced cooldown stacking."
    ],
    chapterTopics: {
      playing: "Immolate · Conflagrate · Chaos Bolt · Imp",
      setup: "0/19/52 · glyphs · pet · macros",
      building: "Hit · spell power · haste · budget",
      equipping: "Dungeons · emblems · ToC · ICC",
      raiding: "Burst · swaps · control · boss notes"
    }
  },
  playing: {
    priority: `${entity("Fel Armor")} and ${entity("Glyph of Life Tap")} buff → assigned curse → ${entity("Immolate")} → ${entity("Conflagrate")} → ${entity("Chaos Bolt")} → ${entity("Incinerate")} filler → refresh effects only when needed.`,
    openerIcon: "ability_warlock_chaosbolt",
    trackingIcon: "ability_warlock_backdraft",
    opener: [
      `Use a safe pre-pull ${entity("Life Tap")} when ${entity("Glyph of Life Tap")} is equipped; start with Fel Armor and the Imp ready.`,
      `Precast ${entity("Immolate")} only when the tank and pull timer allow it; otherwise establish the assigned curse first.`,
      `Use ${entity("Conflagrate")} once Immolate is active, then ${entity("Chaos Bolt")}.`,
      `Fill with ${entity("Incinerate")} and keep the Imp casting ${entity("Firebolt")} on the approved target.`
    ],
    tracking: [
      `${entity("Immolate")}, ${entity("Conflagrate")}, ${entity("Chaos Bolt")}, ${entity("Backdraft")}, and the assigned curse.`,
      `${entity("Glyph of Life Tap")}, mana, health, threat, and ${entity("Soulshatter")}.`,
      `Imp target, health, range, ${entity("Firebolt")}, ${entity("Empowered Imp")}, and ${entity("Blood Pact")}.`,
      `${entity("Shadowfury")} assignment, target life, and whether a new Immolate can deliver meaningful value.`
    ],
    cards: [
      { kicker: "Durable target", title: "Run the fire priority", tag: "Default", iconEntity: "Immolate", decision: "Maintain Immolate, use the short cooldowns, then fill with Incinerate.", actions: ["Immolate", "Conflagrate", "Chaos Bolt", "Incinerate"], rules: ["Conflagrate requires Immolate and does not consume it with Glyph of Conflagrate.", "Cooldowns remain subordinate to an urgent movement or control assignment."], failure: "casting Incinerate into a target without Immolate or delaying short cooldowns through several fillers." },
      { kicker: "Backdraft active", title: "Spend fast casts well", tag: "Proc", iconEntity: "Backdraft", decision: "Use Backdraft charges on useful Destruction casts rather than movement, an unnecessary refresh, or downtime.", actions: ["Conflagrate", "Backdraft", "Chaos Bolt", "Incinerate"], rules: ["Plan movement before Conflagrate when the next globals would otherwise be lost.", "Do not hold Conflagrate indefinitely for a perfect Backdraft sequence."], failure: "triggering Backdraft immediately before a mechanic that prevents casting." },
      { kicker: "Urgent target", title: "Burst before setup expires", tag: "Swap", iconEntity: "Chaos Bolt", decision: "Use immediate useful damage and add Immolate only when the target will live long enough for Conflagrate and ticks.", actions: ["Shadowfury", "Chaos Bolt", "Conflagrate"], rules: ["Shadowfury can create control time before damage when the target is stunnable.", "Do not recast a long curse on an add that will die in seconds."], failure: "spending the entire add lifetime preparing a full boss opener." },
      { kicker: "Forced movement", title: "Move without panic", tag: "Mobile", iconEntity: "Life Tap", decision: "Tap safely, use an available instant, command the Imp, or return through Demonic Circle.", actions: ["Life Tap", "Conflagrate", "Demonic Circle: Teleport"], rules: ["Do not force Conflagrate if Immolate is absent merely to have an instant cast.", "Use Demonic Circle only after placing it for a real mechanic."], failure: "Life Tapping into lethal damage or refreshing Immolate far too early during every movement." },
      { kicker: "Stacked pack", title: "Control before AoE", tag: "AoE", iconEntity: "Shadowfury", decision: "Stun when assigned, then use Seed or Rain of Fire according to pack life and movement.", actions: ["Shadowfury", "Seed of Corruption", "Rain of Fire"], rules: ["Seed durable stacks; use Rain of Fire for short stable packs.", "Respect crowd control and tank threat before opening."], failure: "breaking control or stunning before the tank can position the pack." },
      { kicker: "Pet hazard", title: "Keep the Imp casting", tag: "Pet", iconEntity: "Summon Imp", decision: "Recall before avoidable damage or transitions, then resend when a safe target is available.", actions: ["Firebolt", "Empowered Imp", "Blood Pact"], rules: ["Manual Firebolt queueing can reduce gaps, but never hide an assigned control spell inside the same key.", "Report pet death when it removes Blood Pact or meaningful damage."], failure: "leaving the Imp on an immune target or in a hazard because pet follow was never bound." }
    ],
    utility: [
      [entity("Shadowfury"), "Instant area stun", "Reserve it for assigned control when the stun matters more than incidental damage."],
      [entity("Blood Pact"), "Imp health buff", "Keep the Imp alive and in range; confirm overlap with the group's Warrior buff."],
      [entity("Demonic Circle: Teleport"), "Planned displacement", "Place the circle before the pull where it solves a known movement mechanic."],
      [entity("Soulshatter"), "Threat reduction", "Use before burst threat turns the boss or forces damage downtime."],
      [entity("Banish"), "Demon or elemental control", "Coordinate the target and avoid incidental AoE around it."],
      [entity("Shadow Ward"), "Shadow mitigation", "Use for predictable shadow damage without treating it as immunity."]
    ],
    mistakes: [
      "Treating the short-cooldown priority as one unchanging cast sequence.",
      "Attempting Conflagrate without Immolate or using the wrong glyph assumptions.",
      "Spending Backdraft charges during forced movement or on pointless refreshes.",
      "Using a full boss setup on a target that will die immediately.",
      "Hiding Shadowfury inside a damage macro when it is an assigned stun.",
      "Losing Imp damage and Blood Pact through uncontrolled pet positioning."
    ]
  },
  setup: {
    talentGroups: [
      { title: "Fire engine", icon: "ability_warlock_chaosbolt", items: [`${entity("Immolate")} enables Conflagrate and strengthens the ordinary fire priority.`, `${entity("Conflagrate")} supplies burst and ${entity("Backdraft")}.`, `${entity("Chaos Bolt")} is a high-priority short-cooldown direct spell.`] },
      { title: "Imp engine", icon: "spell_shadow_summonimp", items: [`The ${entity("Imp")} supplies ranged pet damage and ${entity("Blood Pact")}.`, `${entity("Empowered Imp")} rewards continuous Firebolt criticals.`, "Manual Firebolt queueing is useful only when pet control remains visible and safe."] },
      { title: "Fully allocated baseline", icon: "ability_warlock_improvedsoulleech", items: ["The 0/19/52 tree uses all 71 points instead of handing a new player five unexplained flex points.", `${entity("Improved Soul Leech")} supplies useful mana support without requiring another class.`, "Alternate hit, survivability, or Imp allocations are later whole-build decisions with their own gearing assumptions."] }
    ],
    glyphs: [
      [entity("Glyph of Conflagrate", "glyph-name"), '<span class="must">Default</span>', "All content", "Prevents Conflagrate from consuming Immolate or Shadowflame."],
      [entity("Glyph of Incinerate", "glyph-name"), '<span class="must">Default</span>', "Sustained damage", "Raises the ordinary filler spell's damage."],
      [entity("Glyph of Life Tap", "glyph-name"), '<span class="must">Fresh-80 default</span>', "Spirit conversion", "Converts a portion of Spirit into a timed spell-power buff."],
      [entity("Glyph of Immolate", "glyph-name"), '<span class="optional">Later comparison</span>', "Different gear sets", "Raises Immolate periodic damage and should be compared against Life Tap for the actual set."],
      [entity("Glyph of Drain Soul", "glyph-name"), '<span class="optional">Minor</span>', "Shard supply", "Adds a chance to gain an extra Soul Shard from Drain Soul."],
      [entity("Glyph of Souls", "glyph-name"), '<span class="optional">Minor</span>', "Group setup", "Reduces Ritual of Souls mana cost."]
    ],
    extraSection: { id: "pet", short: "Pet", title: "Imp control", icon: "spell_shadow_summonimp", body: `<div class="two-col"><div class="guide-box"><h3>Damage controls</h3>${list(["Bind pet attack, follow, and passive.", "Queue Firebolt deliberately when testing shows it reduces pet cast gaps.", "Keep the Imp on the approved target so Empowered Imp and damage remain useful."])}</div><div class="guide-box"><h3>Survival controls</h3>${list(["Recall before transitions and persistent ground hazards.", "Do not send the Imp across an immunity or realm boundary.", "Resummon only when the current assignment can spare the cast and shard."])}</div></div>` },
    macros: [
      { title: "Incinerate with Firebolt", entity: "Incinerate", purpose: "Queue the Imp's Firebolt while casting the ordinary filler.", code: "#showtooltip Incinerate\n/petattack [harm,nodead]\n/cast Firebolt\n/cast Incinerate" },
      { title: "Focus Shadowfury target", entity: "Shadowfury", purpose: "Cast the assigned area stun at the focused hostile target without changing the damage target.", code: "#showtooltip Shadowfury\n/cast [@focus,harm,nodead][] Shadowfury" },
      { title: "Stop and follow", entity: "Summon Imp", purpose: "Recall the Imp immediately from a hazard, immunity, or transition.", code: "/petpassive\n/petfollow" },
      { title: "Demonic Circle return", entity: "Demonic Circle: Teleport", purpose: "Return through the pre-placed circle using original-client spell behavior.", code: "#showtooltip Demonic Circle: Teleport\n/cast Demonic Circle: Teleport" }
    ],
    essentialAddons: [`<a href="addons.html?search=Deadly%20Boss%20Mods">Deadly Boss Mods</a> for movement, add spawns, and burst timing.`, "A 3.3.5-compatible timer for Immolate, Conflagrate, Chaos Bolt, and Backdraft.", "A visible pet frame for Imp health, range, target, and casting."],
    recommendedAddons: [`WeakAuras/TellMeWhen for ${entity("Backdraft")}, ${entity("Empowered Imp")}, ${entity("Glyph of Life Tap")}, and cooldown collisions.`, "Details/Recount to review target damage, misses, Imp uptime, Firebolt casts, and movement downtime.", "A threat display to time Soulshatter before burst becomes aggro loss."]
  },
  raiding: warlockRaiding("destruction", {
    assignmentBoss: "Immolate remains active; Conflagrate and Chaos Bolt land on useful cooldowns; Incinerate fills the gaps.",
    assignmentAdds: "Short-lived targets receive immediate burst and Shadowfury control instead of an oversized setup.",
    assignmentPet: "The Imp stays alive, in range, and casting Firebolt on the approved target so damage and Blood Pact remain available.",
    assignmentSpecial: "Shadowfury, Demonic Circle, burst targets, and pet recall are planned before the phase.",
    verify: ["lich-king"],
    notes: {
      toc: `Maintain the assigned curse and fire priority while following target order. Use ${entity("Shadowfury")} for assigned add control, and on Anub'arak choose ${entity("Seed of Corruption")} or ${entity("Rain of Fire")} only when stacked adds justify AoE.`,
      marrowgar: `Keep Immolate on the boss, switch immediately to Bone Spikes with direct burst, and use instant globals while relocating during Bone Storm. Recall the Imp before Coldflame or unsafe pathing removes it.`,
      deathwhisper: `Use burst on the called add, reserve Shadowfury for assigned control, and keep the Imp on the correct physical-or-magic target. Move early from Death and Decay rather than finishing Incinerate.`,
      saurfang: `Keep the boss priority active and use immediate direct damage on Blood Beasts only when assigned. Shadowfury can support control if the raid plans for it; do not send the Imp or apply slow setup to beasts indiscriminately.`,
      putricide: `Switch hard to Volatile Ooze and Gas Cloud, use short cooldowns for real burst, and move before Malleable Goo. Pre-place ${entity("Demonic Circle: Summon")} and protect the Imp from bad paths and slime.`,
      "blood-wing": `On Princes, damage only the empowered target and use direct spells on Kinetic Bombs when assigned. On Blood-Queen, follow bite order, maintain the fire priority through planned movement, and preserve the Imp during the air phase.`,
      valithria: `Prioritize Blazing Skeletons and Suppressors, use Shadowfury for planned control, and AoE only stable stacks. The Imp stays on the priority target rather than padding a harmless add.`,
      sindragosa: `Manage Unchained Magic and Instability; stop casting before stacks become lethal. Recall the Imp for unsafe air phases, break only assigned tombs, and use tomb line-of-sight to reset Mystic Buffet.`,
      "lich-king": `Maintain boss Immolate, burst Val'kyr and Raging Spirits, and preserve Shadowfury for an assigned control moment. Verify Hellscream Imp pathing, Empowered Imp, and Vile Spirit behavior before relying on a specialized pet or stun route.`,
      halion: `Stay in the assigned realm, pre-place Demonic Circle around cutter movement, and move early with combustion or consumption. Keep the Imp on the correct realm target and resume the short-cooldown priority only from a safe plant position.`
    }
  })
});

function loadDruidConfig(slug) {
  return JSON.parse(fs.readFileSync(path.join(root, "templates", "spec-guide", `${slug}.config.json`), "utf8"));
}

function druidSources(role, config) {
  const source = role === "balance"
    ? { segment: "balance", prefix: "dps", title: "Balance Druid" }
    : role === "cat"
      ? { segment: "feral", prefix: "dps", title: "Feral Druid DPS" }
      : role === "bear"
        ? { segment: "feral", prefix: "tank", title: "Feral Druid Tank" }
        : { segment: "restoration", prefix: "healer", title: "Restoration Druid" };
  const base = `https://www.wowhead.com/wotlk/guide/classes/druid/${source.segment}`;
  return {
    quick: [[`${source.title} talents and glyphs`, `${base}/${source.prefix}-talent-builds-glyphs-pve`], [`${source.title} stats and progression assumptions`, `${base}/${source.prefix}-stat-priority-attributes-pve`]],
    playing: [[`${source.title} rotation, cooldowns, and abilities`, `${base}/${source.prefix}-rotation-cooldowns-abilities-pve`], ["Druid spell records", "https://www.wowhead.com/wotlk/spells/abilities/druid"]],
    setup: [[`${source.title} talents and glyphs`, `${base}/${source.prefix}-talent-builds-glyphs-pve`], [`Filled ${config.talent.points} talent calculator`, `https://www.wowhead.com/wotlk/talent-calc/${config.talent.wowheadPath}`]],
    building: [[`${source.title} stat priority`, `${base}/${source.prefix}-stat-priority-attributes-pve`], [`${source.title} gems and enchants`, `${base}/${source.prefix}-enchants-gems-pve`]],
    equipping: [[`${source.title} pre-raid gear`, `${base}/${source.prefix}-bis-gear-pre-raid-pve`], [`${source.title} phase-four gear`, `${base}/${source.prefix}-bis-gear-pve-phase-4`], ["Trial of the Champion", "https://www.wowhead.com/wotlk/zone=4723/trial-of-the-champion"], ["Icecrown five-player dungeons", "https://www.wowhead.com/wotlk/guide/icecrown-citadel-dungeons-forge-of-souls-pit-of-saron-halls-of-reflection"]],
    raiding: [["Trial of the Crusader raid overview", "https://www.wowhead.com/wotlk/zone=4722/trial-of-the-crusader"], ["Icecrown Citadel raid overview", "https://www.wowhead.com/wotlk/zone=4812/icecrown-citadel"], ["Ruby Sanctum raid overview", "https://www.wowhead.com/wotlk/zone=4987/the-ruby-sanctum"], ["Rebirth spell record", "https://www.wowhead.com/wotlk/spell=48477"]]
  };
}

function druidBuilding(role) {
  const commonCasterProfessions = [
    ["Engineering", "Hyperspeed Accelerators, Nitro Boosts, bombs, and utility.", "Excellent when the active tools are bound and planned; never an assumed requirement."],
    ["Jewelcrafting", "Three stronger Dragon's Eye gems.", "Flexible throughput, hit, haste, or mana tuning."],
    ["Leatherworking", "Fur Lining and access to useful leather crafts.", "Strong static value with practical early gearing."],
    ["Alchemy", "Improved flask and potion value.", "A practical server-economy choice for sustaining personal supplies."],
    ["Enchanting / Inscription", "Static ring enchants or a personal shoulder inscription.", "Reliable value; choose for the whole character rather than one theoretical stat line."]
  ];
  const commonPhysicalProfessions = [
    ["Engineering", "Hyperspeed Accelerators, Nitro Boosts, bombs, and utility.", "Exceptional control and movement when the active tools are actually used."],
    ["Jewelcrafting", "Three stronger Dragon's Eye gems.", "Flexible Stamina, Agility, Strength, hit, expertise, or later Armor Penetration tuning."],
    ["Leatherworking", "Fur Lining and useful leather crafts.", "Strong static value and direct access to class armor crafts."],
    ["Blacksmithing", "Two extra sockets.", "Flexible and scales with the gems appropriate to the current role and set."],
    ["Alchemy", "Stronger, longer flasks and cheaper supplies.", "A sensible Hellscream economy choice even when it is not the paper maximum."]
  ];

  if (role === "balance") return {
    stats: [
      ["Spell hit", '<span class="must">First raid-boss progression target</span>', "Prevents offensive spells from missing the selected target.", "A level-83 boss needs 17% spell hit. Balance of Power and Improved Faerie Fire provide 7%, leaving 10% from gear—about 263 rating—when both are active. Do not delay normal or heroic dungeons while building it."],
      ["Spell Power", "First uncapped throughput stat", "Raises Wrath, Starfire, DoTs, Starfall, Hurricane, and healing utility.", "Compare the whole item; a larger upgrade can beat a smaller piece with one preferred secondary."],
      ["Haste", "Strong after hit and spell power", "Shortens casts and the global cooldown.", "32.79 haste rating is about 1% at level 80. The raid-buffed Wrath floor is a later set calculation, not a Fresh-80 requirement."],
      ["Critical strike", "Strong Eclipse secondary", "Raises direct-spell criticals, Moonkin Form mana return, and Eclipse reliability.", "45.91 crit rating is about 1% spell crit; do not sacrifice hit or large spell-power gains to collect it."],
      ["Spirit", "Useful secondary", "Improved Moonkin Form converts part of Spirit into spell power and Spirit supports out-of-cast regeneration.", "Useful caster gear may be cloth or leather; armor class alone does not make a weaker item better."],
      ["Intellect", "Mana and crit support", "Adds mana and a small amount of spell critical chance.", "A larger mana pool helps, but it does not replace active Eclipse, movement, and Innervate planning."]
    ],
    stages: [
      { title: "Fresh level 80", icon: "inv_misc_coin_01", items: ["Enter normal and heroic dungeons immediately with trained spells, Moonkin Form, the complete talent tree, and safe Starfall habits.", "Repair hit with ordinary dungeon, reputation, crafted, and inexpensive BoE pieces; use rare gems and budget enchants on temporary gear.", "Replace leveling weapons and empty trinket slots before chasing one final raid stat profile."] },
      { title: "Raid-ready base", icon: "achievement_boss_general_nazgrim", items: ["Know the exact level-83 hit target for the current talents and group.", "Maintain Faerie Fire, DoTs, and Eclipse through a full heroic without unsafe Starfall pulls.", "Carry reagents, role consumables, and a clear Innervate and Rebirth plan."] },
      { title: "Later progression", icon: "inv_misc_gear_01", items: ["Move into epic gems and premium enchants only when the piece will last.", "Compare haste, crit, set bonuses, and movement as a complete loadout.", "Keep a small hit-swap set so one upgrade does not silently break the current cap."] }
    ],
    gems: [
      ["Meta", item("Chaotic Skyflare Diamond", "q-rare"), "Keep the current working meta on a temporary helm", "Activate it with the least throughput loss."],
      ["Red", item("Runed Scarlet Ruby", "q-rare"), item("Runed Cardinal Ruby"), "Use the rare version on temporary gear and the epic version on lasting pieces."],
      ["Yellow hit repair", item("Veiled Monarch Topaz", "q-rare"), item("Veiled Ametrine"), "Use only until the exact set reaches its current hit target."],
      ["Yellow haste", "Rare spell power / haste gem", item("Reckless Ametrine"), "Match a worthwhile socket bonus after hit is solved."],
      ["Blue / meta", item("Purified Twilight Opal", "q-rare"), item("Purified Dreadstone"), "Meet the meta with the least throughput loss; Nightmare Tear is a later convenience."]
    ],
    enchants: [
      ["Head", item("Arcanum of Burning Mysteries"), "Kirin Tor revered in standard Wrath."],
      ["Shoulders", item("Greater Inscription of the Storm"), "Use the lower Sons of Hodir inscription while reputation is unfinished."],
      ["Back", entity("Enchant Cloak - Greater Speed", "enchant-name"), "A cheaper haste enchant is acceptable on a temporary cloak."],
      ["Chest", entity("Enchant Chest - Powerful Stats", "enchant-name"), "Use a cheaper all-stats enchant on a short-lived chest."],
      ["Wrists", entity("Enchant Bracers - Superior Spellpower", "enchant-name"), "Prioritize it on bracers expected to last."],
      ["Hands", entity("Enchant Gloves - Exceptional Spellpower", "enchant-name"), "Engineering may use Hyperspeed Accelerators when deliberately timed."],
      ["Waist", item("Eternal Belt Buckle", "q-rare"), "Add the extra socket to a belt worth keeping."],
      ["Legs", item("Shining Spellthread", "q-rare"), `${item("Brilliant Spellthread")} is the later premium option.`],
      ["Feet", entity("Enchant Boots - Tuskarr's Vitality", "enchant-name"), "Movement speed commonly saves more damage and lives than a small stationary gain."],
      ["Weapon", entity("Enchant Weapon - Mighty Spellpower", "enchant-name"), `${entity("Enchant Weapon - Black Magic", "enchant-name")} is a later haste-proc comparison.`]
    ],
    professions: commonCasterProfessions
  };

  if (role === "restoration") return {
    stats: [
      ["Spell Power", '<span class="must">First uncapped throughput stat</span>', "Raises every healing spell and emergency direct heal.", "A stronger spell-power item is useful immediately; a theoretical haste endpoint does not replace it."],
      ["Haste", "Responsiveness and later GCD goal", "Shortens cast times and the global cooldown of instant HoTs.", "735 with Celestial Focus or 856 without it are later raid-buffed goals under stated assumptions—not dungeon-entry gates."],
      ["Spirit", "Throughput and regeneration", "Improved Tree of Life converts part of Spirit into spell power while Intensity supports in-combat regeneration.", "Take enough regeneration for the actual healing assignment before optimizing a paper throughput set."],
      ["MP5", "Reliable regeneration", "Returns mana continuously and remains useful while casting.", "Compare Spirit and MP5 through the whole item and actual fight length."],
      ["Intellect", "Mana-pool support", "Adds mana, a small amount of crit, and value from percentage-based recovery.", "Mana stability is the goal; a large pool does not excuse wasteful Lifebloom or blanket healing."],
      ["Critical strike", "Lower-priority secondary", "Helps Regrowth, Nourish, Healing Touch, and talents tied to direct-heal criticals.", "Most ordinary HoT ticks do not crit without specific set effects, so do not prioritize crit over the core package."]
    ],
    stages: [
      { title: "Fresh level 80", icon: "inv_misc_coin_01", items: ["Enter normal and heroic dungeons with the complete Tree of Life build, working raid frames, mouseover heals, and enough water.", "Use rare gems and budget enchants while replacing leveling weapons and weak trinkets.", "Practice tank HoTs, Wild Growth placement, Lifebloom blooms, and emergency recovery before raid blanketing."] },
      { title: "Raid-ready base", icon: "achievement_boss_general_nazgrim", items: ["Sustain a heroic without running dry from unnecessary HoTs.", "Track Rejuvenation, Regrowth, Lifebloom stacks, Wild Growth, Swiftmend, Clearcasting, and Innervate.", "Carry reagents and know the Rebirth, dispel, and Innervate assignments."] },
      { title: "Later progression", icon: "inv_misc_gear_01", items: ["Choose a Celestial Focus or deep-Restoration haste model as a complete build-and-gear decision.", "Use epic gems and premium enchants only on pieces expected to last.", "Keep regen-heavy and haste-heavy alternatives for different healing assignments."] }
    ],
    gems: [
      ["Meta", item("Insightful Earthsiege Diamond", "q-rare"), "Keep the current working meta on a temporary helm", "Use the mana return until a tested alternative clearly fits the actual assignment better."],
      ["Red", item("Runed Scarlet Ruby", "q-rare"), item("Runed Cardinal Ruby"), "Use spell power by default after basic mana stability."],
      ["Yellow", "Rare spell power / haste gem", item("Reckless Ametrine"), "Use haste only toward the explicitly chosen build target."],
      ["Blue", item("Purified Twilight Opal", "q-rare"), item("Purified Dreadstone"), "Spirit and spell power support both throughput and regeneration."],
      ["Any color", "Correctly colored budget gem", item("Nightmare Tear"), "Do not buy the premium convenience gem for a short-lived item."]
    ],
    enchants: [
      ["Head", item("Arcanum of Blissful Mending"), "Wyrmrest Accord revered in standard Wrath."],
      ["Shoulders", item("Greater Inscription of the Crag"), "Use the lower Sons of Hodir healing inscription while reputation is unfinished."],
      ["Back", entity("Enchant Cloak - Greater Speed", "enchant-name"), "Haste supports responsiveness; a cheaper enchant is fine on a temporary cloak."],
      ["Chest", entity("Enchant Chest - Powerful Stats", "enchant-name"), "Use a cheaper all-stats enchant on a short-lived chest."],
      ["Wrists", entity("Enchant Bracers - Superior Spellpower", "enchant-name"), "Prioritize it on lasting bracers."],
      ["Hands", entity("Enchant Gloves - Exceptional Spellpower", "enchant-name"), "Engineering may use Hyperspeed Accelerators when the healing window is planned."],
      ["Waist", item("Eternal Belt Buckle", "q-rare"), "Add the extra socket to a belt worth keeping."],
      ["Legs", item("Sapphire Spellthread"), `${item("Brilliant Spellthread")} is a throughput alternative when regeneration is already stable.`],
      ["Feet", entity("Enchant Boots - Tuskarr's Vitality", "enchant-name"), "Movement speed protects both healing uptime and survival."],
      ["Weapon", entity("Enchant Weapon - Mighty Spellpower", "enchant-name"), "Use a cheaper spell-power enchant on a temporary weapon."]
    ],
    professions: commonCasterProfessions
  };

  if (role === "cat") return {
    stats: [
      ["Weapon DPS / Feral Attack Power", '<span class="must">First upgrade lever</span>', "Weapons supply Feral Attack Power from their DPS and amplify form damage.", "The displayed weapon damage is not swung in Cat Form; compare the form stats and whole item."],
      ["Hit", "Reliability, not a forced cap", "Reduces missed melee specials against the selected target.", "8% against a level-83 boss is about 263 rating. Do not sacrifice a clearly stronger whole item merely to display a capped number."],
      ["Expertise", "Strong below the dodge soft cap", "Reduces dodges and protects combo-point and finisher reliability.", "26 expertise is about 214 rating before Primal Precision; count talent expertise before choosing gems."],
      ["Strength and Agility", "Primary throughput package", "Strength supplies attack power; Agility supplies attack power and crit in Cat Form.", "Compare the whole set. Fresh-80 players do not need an endgame bearweaving stat model to begin dungeons."],
      ["Haste and critical strike", "Useful secondaries", "Haste speeds white attacks and Clearcasting opportunities; crit accelerates combo points through Primal Fury.", "Energy, debuff uptime, and position often matter more than a small paper-stat difference."],
      ["Armor Penetration", "Later set transition", "Raises physical damage by bypassing armor.", "The 1,400-rating hard cap and trinket soft caps are later whole-set goals, never a Fresh-80 gem command."]
    ],
    stages: [
      { title: "Fresh level 80", icon: "inv_misc_coin_01", items: ["Enter normal and heroic dungeons with the complete Cat build, trained abilities, and a working behind-target priority.", "Secure a credible Feral weapon and two useful trinkets before chasing a final raid stat profile.", "Use rare Strength or Agility gems and budget enchants on temporary gear."] },
      { title: "Raid-ready base", icon: "achievement_boss_general_nazgrim", items: ["Maintain Savage Roar, Mangle when assigned, Rake, and five-point Rip through a full heroic boss.", "Pool Energy and recover after movement without clipping finishers.", "Carry reagents and know the interrupt, Rebirth, and Innervate assignments."] },
      { title: "Later progression", icon: "inv_misc_gear_01", items: ["Model the complete set before changing Strength, Agility, or Armor Penetration gems.", "Move to premium enchants only when the piece will last.", "Keep utility, hit, expertise, and alternate trinket pieces until the actual set is tested."] }
    ],
    gems: [
      ["Meta", item("Relentless Earthsiege Diamond", "q-rare"), "Keep the current working meta on a temporary helm", "Activate it with the least loss to the current Strength or Agility plan."],
      ["Red Strength", item("Bold Scarlet Ruby", "q-rare"), item("Bold Cardinal Ruby"), "Use only when the whole fresh set supports the Strength plan."],
      ["Red Agility", item("Delicate Scarlet Ruby", "q-rare"), item("Delicate Cardinal Ruby"), "Agility is the simpler all-purpose alternative and supports survival utility."],
      ["Yellow", item("Deadly Monarch Topaz", "q-rare"), item("Deadly Ametrine"), "Match a worthwhile bonus or repair a real hit/expertise deficit with the correct hybrid."],
      ["Blue / meta", item("Shifting Twilight Opal", "q-rare"), item("Nightmare Tear"), "Meet the meta with the smallest useful blue commitment."]
    ],
    enchants: [
      ["Head", item("Arcanum of Torment"), "Knights of the Ebon Blade revered in standard Wrath."],
      ["Shoulders", item("Greater Inscription of the Axe"), "Use the lower Sons of Hodir inscription while progressing reputation."],
      ["Back", entity("Enchant Cloak - Major Agility", "enchant-name"), "Use a cheaper Agility enchant on a temporary cloak."],
      ["Chest", entity("Enchant Chest - Powerful Stats", "enchant-name"), "Use a cheaper stats enchant on a temporary chest."],
      ["Wrists", entity("Enchant Bracers - Greater Assault", "enchant-name"), "Attack power is the stable physical option."],
      ["Hands", entity("Enchant Gloves - Crusher", "enchant-name"), `${entity("Enchant Gloves - Greater Assault", "enchant-name")} is the budget option.`],
      ["Waist", item("Eternal Belt Buckle", "q-rare"), "Add the extra socket to a lasting belt."],
      ["Legs", item("Nerubian Leg Armor", "q-rare"), `${item("Icescale Leg Armor")} is the later premium option.`],
      ["Feet", entity("Enchant Boots - Tuskarr's Vitality", "enchant-name"), "Feral Swiftness already supplies Cat movement; use Icewalker only for a real cap repair."],
      ["Two-handed weapon", entity("Enchant 2H Weapon - Massacre", "enchant-name"), `${entity("Enchant Weapon - Berserking", "enchant-name")} is the premium proc comparison.`]
    ],
    professions: commonPhysicalProfessions
  };

  return {
    stats: [
      ["Stamina", '<span class="must">Primary effective-health stat</span>', "Raises the health buffer against physical and magical spikes.", "Gem Stamina when survival is the problem; do not turn every comparison into one universal ratio."],
      ["Agility", "Mitigation and threat package", "Adds armor, dodge, crit, and attack power in Bear Form.", "Dodge from gear is subject to diminishing returns; Agility remains useful because it does several jobs."],
      ["Armor", "Core physical mitigation", "Reduces physical damage and scales strongly in Dire Bear Form.", "Bonus armor on jewelry does not receive every Bear multiplier in the same way as leather armor; compare the exact item."],
      ["Expertise", "Strong threat below dodge cap", "Reduces dodges and parries, improving threat and reducing parry-haste exposure where active.", "26 expertise removes boss dodges; do not sacrifice a large survival budget to chase the 56 hard cap."],
      ["Hit", "Useful reliability", "Improves melee attacks and some tank actions.", "8% melee hit is about 263 rating, while Growl uses its own hit behavior. Verify taunts and glyphs on Hellscream."],
      ["Defense and crit immunity", "Do not chase 540 Defense", "Survival of the Fittest supplies critical-strike immunity in Dire Bear Form.", "Defense can still add avoidance, but the plate-tank 540 rule is not a Feral requirement."],
      ["Dodge, Strength, AP, haste, crit", "Secondary threat or avoidance", "These improve portions of survival or threat.", "Take them as part of a stronger item; effective health, armor, and controlled play remain the Fresh-80 foundation."]
    ],
    stages: [
      { title: "Fresh level 80", icon: "inv_misc_coin_01", items: ["Enter normal and heroic dungeons with the complete Bear build, Dire Bear Form, trained taunts, and a deliberate pull plan.", "Use Stamina-heavy rare gems and budget armor or Stamina enchants while replacing leveling leather.", "Secure a credible Feral weapon and survival trinkets before copying an ICC threat set."] },
      { title: "Raid-ready base", icon: "achievement_boss_general_nazgrim", items: ["Hold packs without starving required globals through Maul queues.", "Maintain Demoralizing Roar when assigned and plan Barkskin, Survival Instincts, and Frenzied Regeneration.", "Carry reagents and know the taunt-swap, add, Innervate, and Rebirth assignments."] },
      { title: "Later progression", icon: "inv_misc_gear_01", items: ["Build survival, threat, and resistance variants only for a named job.", "Use epic gems and premium enchants on pieces expected to last.", "Keep alternate trinkets, weapons, and armor pieces until each encounter set is tested."] }
    ],
    gems: [
      ["Meta", item("Austere Earthsiege Diamond", "q-rare"), "Keep the current defensive meta on a temporary helm", "Meet the requirement with the smallest useful off-color commitment."],
      ["Blue", item("Solid Sky Sapphire", "q-rare"), item("Solid Majestic Zircon"), "Stamina is the default when damage spikes are the limiting problem."],
      ["Red", item("Shifting Twilight Opal", "q-rare"), item("Shifting Dreadstone"), "Use Agility/Stamina when the socket bonus and whole item justify it."],
      ["Red expertise", item("Guardian's Twilight Opal", "q-rare"), item("Guardian's Dreadstone"), "Repair a real expertise problem without abandoning the survival budget."],
      ["Yellow", item("Vivid Forest Emerald", "q-rare"), item("Nightmare Tear"), "Use hit/Stamina only when the current set benefits; the unique Tear is a later convenience."]
    ],
    enchants: [
      ["Head", item("Arcanum of the Stalwart Protector"), "Argent Crusade revered in standard Wrath."],
      ["Shoulders", item("Greater Inscription of the Pinnacle"), "Use the lower Sons of Hodir tank inscription while reputation is unfinished."],
      ["Back", entity("Enchant Cloak - Mighty Armor", "enchant-name"), "Use a cheaper armor enchant on a temporary cloak."],
      ["Chest", entity("Enchant Chest - Powerful Stats", "enchant-name"), "Heavy Borean Armor Kit is a cheap Stamina alternative for temporary gear."],
      ["Wrists", entity("Enchant Bracers - Major Stamina", "enchant-name"), "Leatherworking may use Fur Lining - Stamina."],
      ["Hands", entity("Enchant Gloves - Armsman", "enchant-name"), "Use a cheaper Stamina or threat option on temporary gloves."],
      ["Waist", item("Eternal Belt Buckle", "q-rare"), "Add the extra socket to a lasting belt."],
      ["Legs", item("Nerubian Leg Armor", "q-rare"), `${item("Frosthide Leg Armor")} is the later premium survival option.`],
      ["Feet", entity("Enchant Boots - Tuskarr's Vitality", "enchant-name"), "Movement and Stamina are both practical tank stats."],
      ["Two-handed weapon", entity("Enchant 2H Weapon - Massacre", "enchant-name"), `${entity("Enchant Weapon - Mongoose", "enchant-name")} is an Agility proc comparison.`]
    ],
    professions: commonPhysicalProfessions
  };
}

function druidEquipping(role) {
  if (role === "balance") return {
    first: [
      ['<span class="must">Hit trinket</span>', item("Mark of the War Prisoner", "q-rare"), "Cyanigosa, heroic Violet Hold", "A large early hit repair plus an on-use spell-power window."],
      ['<span class="must">Weapon</span>', item("Flameheart Spell Scalpel", "q-rare"), "Kirin Tor revered", "A deterministic reputation weapon when dungeon drops refuse to cooperate."],
      ['<span class="must">Off-hand</span>', item("Ward of the Violet Citadel"), "25 Emblems of Heroism", "A durable early off-hand for accessible one-handed weapons."],
      ['<span class="optional">Throughput trinket</span>', item("Sundial of the Exiled"), "40 Emblems of Heroism", "A practical early crit and spell-power proc trinket."],
      ['<span class="optional">Dungeon trinket</span>', item("Forge Ember", "q-rare"), "Sjonnir, heroic Halls of Stone", "A no-raid spell-power alternative while emblems go elsewhere."]
    ],
    fresh: [
      ["Weapon", item("Titansteel Guardian"), "Blacksmithing BoE", "A strong craft only when the local price does not consume the whole gearing budget."],
      ["Head / chest / legs", "Best spell-power leather or cloth dungeon upgrade", "Northrend normal and heroic dungeons", "Replace leveling armor by total useful stats, not armor-class pride."],
      ["Wrists / belt / boots", "Hit, spell-power, haste, or crit upgrade", "Heroic, reputation, or affordable BoE", "Repair the weakest slot while keeping the current hit model visible."],
      ["Trinket", item("Abyssal Rune", "q-rare"), "Normal Trial of the Champion", "An accessible haste proc with no raid lockout."],
      ["Any weak slot", "Best affordable non-raid upgrade", "Reputation, craft, BoE, or emblems", "A broad upgrade beats waiting in leveling gear for one perfect list item."]
    ],
    emblems: [
      { title: "Heroism and Triumph", icon: "spell_holy_summonchampion", items: [`Use ${item("Ward of the Violet Citadel")} or ${item("Sundial of the Exiled")} when those slots are still weak.`, "Use Triumph catch-up pieces to repair the largest armor gaps.", "Do not save every emblem while wearing leveling gear."] },
      { title: "Tier progression", icon: "inv_chest_leather_13", items: ["Build T9 as an accessible bridge, then compare Balance T10 bonuses against actual offset pieces.", "Keep hit coherent while changing tier pieces.", "A set bonus does not replace missing gems, enchants, or movement discipline."] },
      { title: "Frost", icon: "inv_misc_frostemblem_01", items: ["Buy the largest reliable tier or off-set upgrade first.", "Confirm that a purchase does not create an unplanned hit deficit.", "Retain useful hit and haste swap pieces."] }
    ],
    toc: [[item("Abyssal Rune", "q-rare"), "Normal Trial of the Champion", "Immediate catch-up haste proc."], ["T9 Balance set", "Triumph vendor and Trial routes", "Accessible set progression."], [item("Talisman of Resurgence"), "Triumph vendor", "Later Intellect and spell-power on-use option."], ["High-item-level caster weapon", "Trial of the Crusader", "Later clean upgrade; verify faction and mode."]],
    icc: [[item("Nevermelting Ice Crystal"), "Scourgelord Tyrannus, heroic Pit of Saron", "Catch-up crit on-use; compare with ordinary proc uptime."], [item("Muradin's Spyglass"), "Gunship Battle, 10-player", "Sustained spell-power stacking."], [item("Phylactery of the Nameless Lich"), "Sindragosa, 25-player", "Later crit and spell-power proc."], [item("Charred Twilight Scale"), "Halion, 25-player", "Ruby Sanctum endgame target; verify mode and priority."]],
    special: [["Hit repair", "Mark of the War Prisoner and loose hit pieces", "Reach the current target without carrying large excess hit."], ["Movement", "Tuskarr's Vitality boots", "A small paper-stat loss can preserve entire Eclipse windows."], ["AoE safety", "Starfall and Hurricane control set", "The set never compensates for pulling inactive enemies."], ["Mana pressure", "Spirit, Intellect, and regen alternatives", "Keep until real encounter mana usage is known."]]
  };

  if (role === "restoration") return {
    first: [
      ['<span class="must">Weapon</span>', item("Titansteel Guardian"), "Blacksmithing BoE", "A strong deterministic healing weapon when sensibly priced."],
      ['<span class="must">Off-hand</span>', item("Handbook of Obscure Remedies"), "25 Emblems of Heroism", "A durable early healing off-hand with regeneration."],
      ['<span class="must">Mana trinket</span>', item("The Egg of Mortal Essence"), "40 Emblems of Heroism", "A practical haste proc and spell-power baseline."],
      ['<span class="optional">Dungeon trinket</span>', item("Soul Preserver", "q-rare"), "King Ymiron, normal Culling of Stratholme", "A no-raid mana-efficiency option while emblems go elsewhere."],
      ['<span class="optional">Reputation head enchant</span>', item("Arcanum of Blissful Mending"), "Wyrmrest Accord revered", "A deterministic healing upgrade tied to useful reputation progression."]
    ],
    fresh: [["Weapon / off-hand", "Best spell-power and regeneration pair", "Normal, heroic, reputation, craft, or emblems", "Weapon spell power usually delivers the largest immediate healing gain."], ["Armor", "Best spell-power, haste, Spirit, or MP5 leather/cloth", "Northrend five-player dungeons", "Use total healing value; do not wait in leveling leather for a perfect armor-class drop."], ["Trinket", item("Abyssal Rune", "q-rare"), "Normal Trial of the Champion", "Haste catch-up option when mana is already stable."], ["Belt / boots", "Affordable haste or Spirit upgrade", "Reputation, craft, or BoE", "Repair weak slots before forcing a one-second GCD set."], ["Any weak slot", "Best affordable non-raid upgrade", "Reputation, craft, BoE, or emblems", "A broad upgrade beats hoarding while the current item is weak."]],
    emblems: [{ title: "Heroism and Triumph", icon: "spell_holy_summonchampion", items: [`Use ${item("Handbook of Obscure Remedies")} or ${item("The Egg of Mortal Essence")} while those slots are weak.`, "Use Triumph catch-up armor to replace the largest healing gaps.", "Do not delay a major upgrade merely to save for a distant list."] }, { title: "Tier progression", icon: "inv_chest_leather_13", items: ["Build T9 as an accessible bridge, then compare Restoration T10 bonuses against actual offsets.", "Keep haste and mana stable while changing several tier slots.", "Preserve assignment-specific alternatives."] }, { title: "Frost", icon: "inv_misc_frostemblem_01", items: ["Buy the largest reliable tier or off-set upgrade first.", "Confirm the change against the selected haste model.", "Keep regen-heavy pieces for long or recovery-intensive fights."] }],
    toc: [[item("Abyssal Rune", "q-rare"), "Normal Trial of the Champion", "Catch-up haste when mana is stable."], ["T9 Restoration set", "Triumph vendor and Trial routes", "Accessible set progression."], [item("Talisman of Resurgence"), "Triumph vendor", "Large Intellect and planned spell-power on-use."], ["Solace trinket family", "Trial of the Crusader, 25-player", "Later regeneration target; verify faction and mode."]],
    icc: [[item("Nevermelting Ice Crystal"), "Scourgelord Tyrannus, heroic Pit of Saron", "Catch-up option, not an automatic healing trinket."], [item("Althor's Abacus"), "Gunship Battle, 25-player", "Later direct-healing proc target."], [item("Trauma"), "Rotface, 25-player", "Later weapon whose proc value depends on healing pattern."], [item("Glowing Twilight Scale"), "Halion, 25-player", "Ruby Sanctum endgame healing target; verify mode and priority."]],
    special: [["Mana stability", "Spirit, MP5, and Intellect variants", "Use when the assignment or fight length creates real mana pressure."], ["Haste progression", "Haste-heavy alternatives", "Use only against the explicitly chosen 735 or 856 model."], ["Tank support", "Nourish and direct-heal set", "Keep when five-player or raid tank healing is the job."], ["Movement", "Tuskarr's Vitality boots", "Reaching the next target is a healing throughput gain."]]
  };

  if (role === "cat") return {
    first: [['<span class="must">Dungeon weapon</span>', item("Staff of Trickery", "q-rare"), "Herald Volazj, heroic Ahn'kahet", "A farmable Feral weapon when crafted options are too expensive."], ['<span class="must">Crafted weapon</span>', item("Titansteel Destroyer"), "Blacksmithing BoE", "A strong early weapon only when the local price leaves gold for the rest of the character."], ['<span class="must">Emblem trinket</span>', item("Mirror of Truth"), "40 Emblems of Heroism", "A reliable crit and attack-power proc baseline."], ['<span class="optional">Dungeon trinket</span>', item("Meteorite Whetstone", "q-rare"), "King Ymiron, heroic Utgarde Pinnacle", "A farmable crit and haste-proc option."], ['<span class="premium">Expensive BoE</span>', item("Darkmoon Card: Greatness"), "Nobles Deck", "Powerful, but never the first purchase while several slots remain weak."]],
    fresh: [["Neck", item("Pendant of the Outcast Hero"), "25 Emblems of Heroism", "A durable physical-DPS neck after higher-impact needs are solved."], ["Back", item("Cloak of the Gushing Wound", "q-rare"), "Erekem, heroic Violet Hold", "A farmable Agility physical-DPS cloak."], ["Belt", item("Jorach's Crocolisk Skin Belt"), "40 Emblems of Heroism", "A strong emblem leather belt when the slot is weak."], ["Ring", item("Ring of Scarlet Shadows"), "Jewelcrafting BoE", "An accessible physical-DPS ring when sensibly priced."], ["Any armor slot", "Highest useful Agility leather upgrade", "Normal, heroic, reputation, or affordable BoE", "Item level and total useful stats usually beat waiting for one perfect secondary spread."]],
    emblems: [{ title: "Heroism and Triumph", icon: "spell_holy_summonchampion", items: [`Prioritize ${item("Mirror of Truth")} and a major weapon or armor gap.`, "Use Triumph catch-up pieces and T9 to replace leveling gear.", "Do not hoard every emblem while the current set cannot support the rotation."] }, { title: "Tier progression", icon: "inv_chest_leather_13", items: ["Build T9 as a bridge, then compare Cat T10 bonuses against actual offset pieces.", "Keep hit and expertise visible while changing multiple slots.", "Set bonuses do not replace uptime and Energy discipline."] }, { title: "Frost", icon: "inv_misc_frostemblem_01", items: ["Buy the largest reliable tier or off-set upgrade first.", "Herkuml War Token is a later sustained-melee option, not the automatic first purchase.", "Keep alternate hit, expertise, and trinket pieces."] }],
    toc: [[item("Banner of Victory", "q-rare"), "Normal Trial of the Champion", "Armor Penetration catch-up trinket; use only as part of the actual set."], ["T9 Feral set", "Triumph vendor and Trial routes", "Accessible set progression."], ["High-item-level Feral weapon", "Trial of the Crusader", "Weapon upgrades remain high priority."], ["Physical leather offset", "Trial bosses", "Take the clean upgrade rather than waiting for one perfect list item."]],
    icc: [[item("Needle-Encrusted Scorpion"), "Devourer of Souls, heroic Forge of Souls", "Catch-up Armor Penetration proc; model its soft cap before regemming."], [item("Herkuml War Token"), "60 Emblems of Frost", "Later sustained haste and attack-power option."], [item("Whispering Fanged Skull"), "Lady Deathwhisper, 10-player", "Later crit and attack-power proc target."], [item("Deathbringer's Will"), "Deathbringer Saurfang, 25-player", "Major later raid target, not a Fresh-80 shopping expectation."], [item("Sharpened Twilight Scale"), "Halion, 25-player", "Ruby Sanctum endgame physical trinket; verify mode and priority."]],
    special: [["Hit / expertise repair", "Loose reliability pieces", "Swap only enough to improve the actual set without losing a larger upgrade."], ["Armor Penetration", "Proc-trinket and native-ArP set", "Keep separate until the full set supports a validated transition."], ["Utility", "Survival or movement pieces", "Staying alive and reaching the target preserve more damage than a paper maximum."], ["Emergency Bear", "Stamina and armor alternatives", "Keep only for a named assignment; Cat remains the DPS role."]]
  };

  return {
    first: [['<span class="must">Dungeon weapon</span>', item("Staff of Trickery", "q-rare"), "Herald Volazj, heroic Ahn'kahet", "A farmable Feral weapon with useful form stats."], ['<span class="must">Health trinket</span>', item("Essence of Gossamer", "q-rare"), "Hadronox, heroic Azjol-Nerub", "A direct early health buffer with no raid requirement."], ['<span class="must">Crafted chest</span>', item("Polar Vest"), "Leatherworking BoE", "A high-Stamina option only when the craft is affordable and the physical-survival job warrants it."], ['<span class="optional">Dungeon bracers</span>', item("Bindings of the Tunneler", "q-rare"), "Skarvald, heroic Utgarde Keep", "A farmable leather tank option with useful stats."], ['<span class="optional">Dungeon cloak</span>', item("Cloak of the Gushing Wound", "q-rare"), "Erekem, heroic Violet Hold", "An accessible Agility cloak while a more defensive option is unavailable."]],
    fresh: [["Weapon", item("Titansteel Destroyer"), "Blacksmithing BoE", "A strong early Feral weapon when sensibly priced; survival gear still matters more than one luxury craft."], ["Chest", item("Crystal-Infused Tunic", "q-rare"), "Keristrasza, heroic Nexus", "A farmable leather alternative before expensive crafts."], ["Trinket", item("The Black Heart"), "Black Knight, normal Trial of the Champion", "A strong catch-up Stamina and armor-proc trinket."], ["Armor", "Highest useful Stamina, Agility, and armor leather", "Normal, heroic, reputation, or affordable BoE", "Replace leveling gear by total survival and threat value."], ["Any weak slot", "Best affordable tank upgrade", "Reputation, craft, BoE, or emblems", "A broad effective-health gain beats waiting for an ICC-shaped list."]],
    emblems: [{ title: "Heroism and Triumph", icon: "spell_holy_summonchampion", items: ["Replace the weakest survival slot instead of hoarding every emblem.", "Use Triumph catch-up armor and T9 as a bridge.", "Keep threat reliable, but do not buy offensive pieces while health and armor are clearly weak."] }, { title: "Tier progression", icon: "inv_chest_leather_13", items: ["Build a coherent Feral tank set and compare bonuses against actual offset armor.", "Keep survival and threat variants when both have named jobs.", "Never import a Cat gem plan into the Bear set without review."] }, { title: "Frost", icon: "inv_misc_frostemblem_01", items: [`${item("Corroded Skeleton Key")} is a direct later Stamina option.`, "Buy required tier or the largest survival gain first.", "Keep alternate trinkets for physical, magical, and threat-sensitive encounters."] }],
    toc: [[item("The Black Heart"), "Normal Trial of the Champion", "Immediate catch-up Stamina and armor proc."], ["T9 Feral tank pieces", "Triumph vendor and Trial routes", "Accessible set progression."], ["High-item-level Feral weapon", "Trial of the Crusader", "Threat and form-stat upgrade after survival basics."], [item("Glyph of Indomitability"), "50 Emblems of Triumph", "Later armor on-use option for physical damage."]],
    icc: [[item("Corroded Skeleton Key"), "60 Emblems of Frost", "Large Stamina plus an absorb on use."], [item("Unidentifiable Organ"), "Professor Putricide, 10-player", "Physical-survival trinket whose stacks require actual incoming hits."], [item("Sindragosa's Flawless Fang"), "Sindragosa, 10-player", "Later Stamina and resistance cooldown target."], [item("Petrified Twilight Scale"), "Halion, 25-player", "Ruby Sanctum endgame tank target; verify mode and priority."]],
    special: [["Physical survival", "Armor and Stamina set", "Use for sustained melee or burst physical damage."], ["Magic survival", "Stamina and resistance tools", "Use only for a named magical job; armor does not solve spell bursts."], ["Threat / pickup", "Hit, expertise, and offensive alternatives", "Use when survival is stable and pickup reliability is the actual problem."], ["Cat off-role", "Separate Cat weapon, trinkets, and gems", "Do not blur the Bear baseline into a compromised hybrid set."]]
  };
}

const druidEncounterBase = [
  ["toc", "Trial of the Crusader", "achievement_boss_anubarak_01"],
  ["marrowgar", "Lord Marrowgar", "achievement_boss_lordmarrowgar"],
  ["deathwhisper", "Lady Deathwhisper", "achievement_boss_ladydeathwhisper"],
  ["saurfang", "Deathbringer Saurfang", "achievement_boss_saurfang"],
  ["putricide", "Professor Putricide", "achievement_boss_profputricide"],
  ["blood-wing", "Blood Prince Council and Blood-Queen Lana'thel", "achievement_boss_lanathel"],
  ["valithria", "Valithria Dreamwalker", "achievement_boss_valithriadreamwalker"],
  ["sindragosa", "Sindragosa", "achievement_boss_sindragosa"],
  ["lich-king", "The Lich King", "achievement_boss_lichking"],
  ["halion", "Halion", "achievement_boss_halion"]
];

function druidRaiding(role, advice) {
  const tank = role === "bear";
  const healer = role === "restoration";
  return {
    entryNote: "This chapter is later progression, not the starting expectation for a new level 80. Complete the self-contained setup, practice the role in normal and heroic dungeons, and enter raids only after the character and player are ready.",
    assignmentIcon: advice.assignmentIcon,
    consumables: advice.consumables,
    prePull: advice.prePull,
    assignments: advice.assignments,
    notes: druidEncounterBase.map(([key, encounter, iconName]) => ({
      encounter,
      icon: iconName,
      size: "10 25",
      difficulty: "normal heroic",
      role: advice.roles,
      sizeLabel: "10 / 25",
      difficultyLabel: "Normal / Heroic",
      roleLabel: tank ? "Tank assignments" : healer ? "Healing assignments" : "Damage / utility",
      verify: advice.verify.includes(key),
      text: advice.notes[key]
    }))
  };
}

function makeDruidSpec(config, role, content) {
  return {
    className: config.className,
    classSlug: config.classSlug,
    name: config.specName,
    shortName: config.specShortName,
    nickname: config.guideNickname,
    guideTypes: config.guideTypes,
    slug: config.specSlug,
    specKey: config.specKey,
    guideAudience: config.guideAudience,
    fresh80Policy: config.fresh80Policy,
    tooltipFile: config.tooltipFile,
    cacheKey: config.cacheKey,
    serverNote: config.serverNote,
    icons: config.icons,
    descriptions: config.pageDescriptions,
    mechanics: config.mechanics.map((mechanic) => ({ ...mechanic, iconEntity: mechanic.examples[0].name })),
    roleFilters: config.raidRoleFilters.map(({ value, label }) => [value, label]),
    talent: { points: config.talent.points, name: config.talent.name, summary: config.talent.summary, path: config.talent.wowheadPath },
    building: druidBuilding(role),
    equipping: druidEquipping(role),
    sources: druidSources(role, config),
    ...content
  };
}

const balanceDruid = makeDruidSpec(loadDruidConfig("balance-druid"), "balance", {
  quick: {
    summaries: [
      { label: "Core job", value: "Move Eclipse without losing DoTs", detail: "Use the spell that can trigger the next Eclipse, then protect the empowered school while required effects remain useful." },
      { label: "Default priority", value: "Wrath → Lunar · Starfire → Solar", detail: "Maintain useful DoTs, use safe cooldowns, and return to the Eclipse engine instead of following a fixed rotation." },
      { label: "Fresh-80 rule", value: "Safe Starfall beats extra targets", detail: "A controlled cast that cannot wake, pull, or hit forbidden targets is worth more than a larger risky cast." }
    ],
    engineTitle: "Prepare → trigger → spend → recover",
    beforeIcon: "spell_nature_forceofnature",
    firstIcon: "inv_misc_coin_01",
    before: [
      `Enter ${entity("Moonkin Form")}, apply ${entity("Mark of the Wild")} or ${entity("Gift of the Wild")}, and place ${entity("Thorns")} on the tank when appropriate.`,
      `Confirm who supplies ${entity("Faerie Fire")}; use ${entity("Improved Faerie Fire")} only when its debuff is actually needed.`,
      `Check that ${entity("Starfall")} cannot reach inactive packs or controlled targets and that ${entity("Force of Nature")} can path safely.`,
      `Carry reagents, water, ${entity("Flask of the Frost Wyrm")}, food, and mana or speed potions appropriate to the content.`
    ],
    firstMoves: [
      "Train every level-80 rank and install the complete 55/0/16 baseline and glyph set.",
      "Enter normal and heroic dungeons immediately; practice Eclipse direction, safe Starfall use, and utility before treating raid caps as entrance requirements.",
      "Replace leveling gear, secure two useful trinkets, and build toward 10% spell hit from gear for level-83 raid targets under this self-contained build.",
      "Learn when a target will live long enough for both DoTs before adding cooldown stacking or advanced Eclipse timing."
    ],
    chapterTopics: {
      playing: "Eclipse · DoTs · movement · utility",
      setup: "55/0/16 · glyphs · macros · tracking",
      building: "Hit · spell power · haste · budget",
      equipping: "Dungeons · emblems · ToC · ICC",
      raiding: "Windows · swaps · control · boss notes"
    }
  },
  playing: {
    priority: `${entity("Moonkin Form")} and group buffs → required ${entity("Faerie Fire")} → useful ${entity("Moonfire")} and ${entity("Insect Swarm")} → safe ${entity("Force of Nature")} and ${entity("Starfall")} → ${entity("Wrath")} until Lunar Eclipse → ${entity("Starfire")} until Solar Eclipse → repeat.`,
    openerIcon: "ability_druid_eclipse",
    trackingIcon: "spell_nature_starfall",
    opener: [
      `Precast ${entity("Wrath")} only when the pull timer, travel time, and tank allow it.`,
      `Apply required ${entity("Faerie Fire")}, then ${entity("Moonfire")} and ${entity("Insect Swarm")} when the target will live for useful ticks.`,
      `Use ${entity("Force of Nature")} where the treants can connect and survive; use ${entity("Starfall")} only after checking its entire radius.`,
      `Continue ${entity("Wrath")} until Lunar Eclipse procs, then spend the window with ${entity("Starfire")}.`
    ],
    tracking: [
      `${entity("Eclipse")}: which direction can proc, which buff is active, and how much of the window remains.`,
      `${entity("Moonfire")}, ${entity("Insect Swarm")}, ${entity("Faerie Fire")}, and target life expectancy.`,
      `${entity("Starfall")}, ${entity("Force of Nature")}, mana, threat, and ${entity("Innervate")}.`,
      `Movement timers, ${entity("Nature's Grace")}, and whether the next cast can finish before displacement.`
    ],
    cards: [
      { kicker: "No Eclipse active", title: "Trigger the next window", tag: "Default", iconEntity: "Eclipse", decision: "Use the spell capable of triggering the available Eclipse while preserving required effects.", actions: ["Wrath", "Eclipse", "Starfire"], rules: ["Wrath criticals can trigger Lunar; Starfire criticals can trigger Solar.", "Do not alternate every cast—the proc state determines the filler."], failure: "casting the empowered school while trying to trigger its own locked Eclipse direction." },
      { kicker: "DoT decision", title: "Refresh for useful ticks", tag: "Maintain", iconEntity: "Moonfire", decision: "Apply or refresh only when the target will live long enough and the global will not waste a critical Eclipse window.", actions: ["Moonfire", "Insect Swarm", "Starfire"], rules: ["DoTs support sustained targets, movement, and debuffs.", "Avoid refreshing both automatically inside every Eclipse."], failure: "turning a strong Eclipse window into repeated early maintenance globals." },
      { kicker: "Stacked enemies", title: "Use controlled area damage", tag: "AoE", iconEntity: "Starfall", decision: "Choose Starfall, Hurricane, or direct focus damage according to pack safety, life, and movement.", actions: ["Starfall", "Hurricane", "Typhoon"], rules: ["Audit the full Starfall radius before casting.", "Use Typhoon knockback only when it helps the tank or saves a player."], failure: "pulling inactive enemies, breaking control, or scattering a positioned pack." },
      { kicker: "Forced movement", title: "Move on useful globals", tag: "Mobile", iconEntity: "Typhoon", decision: "Use genuinely due instant effects, utility, or planned movement rather than inventing early refreshes.", actions: ["Moonfire", "Insect Swarm", "Typhoon"], rules: ["Start moving before the hazard reaches you.", "Return to the Eclipse filler immediately after reaching safety."], failure: "standing still to finish a low-value cast or refreshing every effect far too early." },
      { kicker: "Mana pressure", title: "Recover before empty", tag: "Mana", iconEntity: "Innervate", decision: "Use Innervate early enough to gain its full value and continue the priority without a dry phase.", actions: ["Innervate", "Moonkin Form", "Wrath"], rules: ["Plan the first use from fight length instead of waiting for zero mana.", "A requested healer Innervate is an assignment decision, not an automatic default."], failure: "saving Innervate until the remaining fight is shorter than its useful return." },
      { kicker: "Control or recovery", title: "Use the Druid toolkit", tag: "Utility", iconEntity: "Rebirth", decision: "Interrupt the damage priority when an assigned control, cleanse, mana, or resurrection action prevents a wipe.", actions: ["Rebirth", "Remove Curse", "Cyclone"], rules: ["Confirm the resurrection target and safe location before casting.", "Coordinate control so immunity and diminishing returns do not waste the global."], failure: "protecting personal damage while the assigned utility action is missed." }
    ],
    utility: [
      [entity("Typhoon"), "Knockback and daze", "Use only when the displacement improves control; glyph it when knockback would be harmful."],
      [entity("Entangling Roots"), "Root control", "Use on eligible melee enemies with a clear break and movement plan."],
      [entity("Cyclone"), "Short immunity control", "Coordinate carefully because the target cannot be damaged or healed while cycloned."],
      [entity("Remove Curse"), "Curse removal", "Prioritize dangerous assigned curses over a damage global."],
      [entity("Abolish Poison"), "Repeated poison removal", "Use when recurring poison applications justify the ongoing effect."],
      [entity("Innervate"), "Mana recovery", "Assign before the pull and use early enough for the full return."],
      [entity("Rebirth"), "Combat resurrection", "Confirm the target, location, and follow-up healing before spending the reagent."],
      [entity("Barkskin"), "Personal mitigation", "Use before predictable damage and movement; it is not an immunity."]
    ],
    mistakes: [
      "Treating Eclipse as a two-spell alternating rotation instead of a proc state.",
      "Refreshing Moonfire and Insect Swarm automatically during every empowered window.",
      "Casting Starfall before checking nearby packs and controlled targets.",
      "Finishing a low-value cast while a movement mechanic reaches the character.",
      "Waiting until empty mana to plan Innervate.",
      "Ignoring an assigned cleanse, control, or Rebirth to preserve the damage meter."
    ]
  },
  setup: {
    talentGroups: [
      { title: "Eclipse engine", icon: "ability_druid_eclipse", items: [`${entity("Eclipse")} creates the alternating Lunar and Solar damage windows.`, `${entity("Nature's Grace")} rewards critical casts with haste.`, `${entity("Starfall")} and ${entity("Force of Nature")} provide planned cooldown damage.`] },
      { title: "Self-contained hit", icon: "spell_nature_faeriefire", items: [`${entity("Balance of Power")} supplies 4% spell hit and ${entity("Improved Faerie Fire")} supplies 3% when its debuff is active.`, "Against a level-83 raid target, the baseline therefore seeks 10%—about 263 rating—from gear before counting another player’s effects.", "That raid target is progression, not a normal-dungeon entry gate."] },
      { title: "Dungeon support", icon: "spell_nature_natureguardian", items: [`${entity("Intensity")} and ${entity("Omen of Clarity")} make the baseline functional without assumed raid-only mana support.`, "Later raid swaps must state which self-contained tool is removed and why.", "Preserve 71 allocated points whenever a flex choice is tested."] }
    ],
    glyphs: [
      [entity("Glyph of Starfire", "glyph-name"), '<span class="must">Default</span>', "Durable targets", "Starfire extends Moonfire so the DoT needs fewer maintenance globals."],
      [entity("Glyph of Moonfire", "glyph-name"), '<span class="must">Default</span>', "Sustained damage", "Strengthens Moonfire's periodic component while reducing its direct component."],
      [entity("Glyph of Starfall", "glyph-name"), '<span class="must">Default</span>', "Safe cooldown use", "Reduces Starfall cooldown for more planned windows."],
      [entity("Glyph of Insect Swarm", "glyph-name"), '<span class="optional">Raid swap</span>', "Damage-first assignment", "Raises Insect Swarm damage but removes its hit-reduction utility."],
      [entity("Glyph of Typhoon", "glyph-name"), '<span class="optional">Control swap</span>', "No knockback", "Removes knockback when displacement would disrupt the tank."],
      [entity("Glyph of the Wild", "glyph-name"), '<span class="optional">Minor</span>', "Buff recovery", "Reduces the mana cost of Mark and Gift of the Wild."]
    ],
    macros: [
      { title: "Mouseover Innervate", entity: "Innervate", purpose: "Give mana to a living friendly mouseover, otherwise use the current friendly target or self.", code: "#showtooltip Innervate\n/cast [@mouseover,help,nodead][help,nodead][@player] Innervate" },
      { title: "Focus Entangling Roots", entity: "Entangling Roots", purpose: "Root a hostile focus without losing the damage target; fall back to the current target.", code: "#showtooltip Entangling Roots\n/cast [@focus,harm,nodead][] Entangling Roots" },
      { title: "Mouseover Rebirth", entity: "Rebirth", purpose: "Combat-resurrect a dead friendly mouseover without changing the current target.", code: "#showtooltip Rebirth\n/cast [@mouseover,help,dead][help,dead] Rebirth" },
      { title: "Form-safe Barkskin", entity: "Barkskin", purpose: "Use personal mitigation without leaving Moonkin Form.", code: "#showtooltip Barkskin\n/cast Barkskin" }
    ],
    essentialAddons: [`<a href="addons.html?search=Deadly%20Boss%20Mods">Deadly Boss Mods</a> for movement and cooldown timing.`, "A 3.3.5-compatible Eclipse display that shows the active buff, the available trigger direction, and remaining duration.", "A DoT timer that keeps Moonfire and Insect Swarm distinct on the selected target."],
    recommendedAddons: [`WeakAuras/TellMeWhen for ${entity("Eclipse")}, ${entity("Nature's Grace")}, ${entity("Starfall")}, and ${entity("Innervate")}.`, "Details/Recount to review DoT uptime, Eclipse casts, misses, target damage, and avoidable deaths.", "A threat display so cooldown windows do not surprise the tank."]
  },
  raiding: druidRaiding("balance", {
    assignmentIcon: "ability_druid_eclipse",
    roles: "single-target aoe movement utility special",
    consumables: [`${entity("Flask of the Frost Wyrm")} for the default spell-power flask.`, `${entity("Fish Feast")} or equivalent spell-power food after verifying the available feast.`, `${entity("Potion of Speed")} for a planned casting window; mana potion when completion is otherwise at risk.`],
    prePull: ["Confirm Faerie Fire, Innervate, Rebirth, and control assignments.", "Inspect Starfall range, treant pathing, and the first movement timer.", "State the gear hit assumption rather than silently counting a raid debuff."],
    assignments: [["Sustained target", "Required DoTs and debuffs remain useful while Eclipse windows land on the assigned target.", "Call forced downtime or a target that will die before maintenance pays back."], ["Adds and AoE", "Priority targets receive immediate damage; Starfall and Hurricane stay inside the raid's control plan.", "Call unsafe radius, crowd control, or a target leaving the stack."], ["Druid utility", "Innervate, Rebirth, cleanses, roots, and Typhoon are used on the agreed target and timing.", "Call reagent, range, immunity, or cooldown conflicts before they become failures."]],
    verify: ["lich-king"],
    notes: {
      toc: `Maintain useful boss effects across target changes and reserve ${entity("Typhoon")} for an agreed control job. On Anub'arak, use ${entity("Starfall")} only when its radius cannot disrupt burrower control or scarabs.`,
      marrowgar: `Keep Eclipse moving, switch immediately to Bone Spikes, and use genuinely due instant globals during Bone Storm. Check ${entity("Starfall")} against nearby trash before the pull.`,
      deathwhisper: `Follow add priority, use ${entity("Remove Curse")} when assigned, and do not pad durable DoTs across controlled or low-priority targets. Preserve Typhoon for the raid's positioning plan.`,
      saurfang: `Keep damage on the boss unless assigned to Blood Beasts. Use roots or Typhoon only under the control plan; uncontrolled knockback can send a beast toward another player.`,
      putricide: `Switch hard to Volatile Ooze and Gas Cloud, move before Malleable Goo, and cast DoTs only when the add will live for useful ticks. Save instant globals for the planned route.`,
      "blood-wing": `On Princes, attack only the empowered target and help with Kinetic Bombs only when assigned. On Blood-Queen, protect Eclipse uptime by moving early and follow the bite order.`,
      valithria: `Prioritize Blazing Skeletons and Suppressors, control with roots or Typhoon only by assignment, and use ${entity("Hurricane")} on stable packs that the tanks have secured.`,
      sindragosa: `Respect Unchained Magic and Instability, stop casting before stacks become lethal, and break only assigned Ice Tombs. Use line-of-sight correctly for Mystic Buffet resets.`,
      "lich-king": `Burn Val'kyr and Raging Spirits by priority, use movement globals during Defile routes, and never let ${entity("Starfall")} replace the raid's Vile Spirit control plan. Verify Hellscream-specific targeting before relying on it.`,
      halion: `Remain in the assigned realm, move early for combustion or consumption, and keep Eclipse casts aligned around cutter movement. Typhoon and Starfall remain control-sensitive tools.`
    }
  })
});

const feralCatDruid = makeDruidSpec(loadDruidConfig("feral-cat-druid"), "cat", {
  quick: {
    summaries: [
      { label: "Core job", value: "Keep Roar and Rip purposeful", detail: "Build combo points, pool Energy, and refresh finishers without destroying the next decision window." },
      { label: "Default priority", value: "Roar → bleeds → Bite with room", detail: "Maintain Mangle's bleed support when required, keep Rake and Rip useful, and Bite only when the timers permit it." },
      { label: "Fresh-80 rule", value: "Reliable position beats paper DPS", detail: "A clean front-facing Mangle or target swap is better than losing several globals while forcing Shred access." }
    ],
    engineTitle: "Position → build → pool → finish",
    beforeIcon: "ability_druid_catform",
    firstIcon: "inv_misc_coin_01",
    before: [
      `Enter ${entity("Cat Form")}, apply ${entity("Mark of the Wild")} or ${entity("Gift of the Wild")}, and confirm who supplies the bleed-damage debuff.`,
      `Know whether the target allows rear access for ${entity("Shred")}; bind ${entity("Mangle (Cat)")} for forced frontal moments.`,
      `Confirm ${entity("Rebirth")}, ${entity("Innervate")}, interrupt or control, and emergency-Bear expectations.`,
      `Start with repaired gear, poisons and curses visible to the group, food or flask appropriate to the run, and free bag space for upgrades.`
    ],
    firstMoves: [
      "Train every level-80 rank and install the fully allocated 0/55/16 Cat baseline and glyph set.",
      "Enter normal and heroic dungeons immediately; practice rear access, Energy pooling, Savage Roar, and fast target swaps before treating raid caps as entry requirements.",
      "Replace leveling gear and obtain a level-80 Feral weapon; weapon form attack power is a major upgrade signal.",
      "Build reliability toward 8% physical special hit and 26 expertise for raid bosses without sacrificing obviously larger Agility upgrades just to display a cap."
    ],
    chapterTopics: {
      playing: "Energy · combo points · bleeds · position",
      setup: "0/55/16 · glyphs · forms · macros",
      building: "Agility · hit · expertise · ArP",
      equipping: "Dungeons · emblems · ToC · ICC",
      raiding: "Uptime · swaps · survival · boss notes"
    }
  },
  playing: {
    priority: `${entity("Cat Form")} and group buffs → ${entity("Faerie Fire (Feral)")} when assigned → required ${entity("Mangle (Cat)")} debuff → useful ${entity("Savage Roar")} → ${entity("Rake")} → ${entity("Rip")} at five combo points → ${entity("Shred")} builder from behind → ${entity("Ferocious Bite")} only with safe timer room.`,
    openerIcon: "ability_druid_savageroar",
    trackingIcon: "ability_druid_disembowel",
    opener: [
      `Use ${entity("Feral Charge - Cat")} only when the path is safe and its movement value is needed.`,
      `Apply ${entity("Faerie Fire (Feral)")} and ${entity("Mangle (Cat)")} when those effects are assigned and not already covered.`,
      `Build a short ${entity("Savage Roar")}, apply ${entity("Rake")}, then build toward a five-point ${entity("Rip")}.`,
      `Use ${entity("Tiger's Fury")} at low Energy without wasting its return; begin pooling before the next finisher collision.`
    ],
    tracking: [
      `${entity("Savage Roar")}, ${entity("Rip")}, ${entity("Rake")}, and the required ${entity("Mangle (Cat)")} debuff.`,
      `Energy, combo points, ${entity("Tiger's Fury")}, ${entity("Berserk")}, and ${entity("Omen of Clarity")}.`,
      `Rear access for ${entity("Shred")}, target life, travel time, and the raid's next forced movement.`,
      `${entity("Barkskin")}, ${entity("Survival Instincts")}, ${entity("Rebirth")}, and emergency-form expectations.`
    ],
    cards: [
      { kicker: "Durable target", title: "Build the maintenance engine", tag: "Default", iconEntity: "Savage Roar", decision: "Keep Roar, Rip, Rake, and required bleed support useful while spending Energy through deliberate builders.", actions: ["Savage Roar", "Rake", "Rip", "Shred"], rules: ["Pool before refresh collisions so the required finisher lands on time.", "Use five combo points for Rip whenever the target can live through it."], failure: "spending Energy immediately and then reaching a Roar or Rip deadline empty." },
      { kicker: "Timers collide", title: "Pool before the deadline", tag: "Resource", iconEntity: "Tiger's Fury", decision: "Stop unnecessary builders, preserve combo points, and enter the refresh window with enough Energy to act.", actions: ["Tiger's Fury", "Savage Roar", "Rip"], rules: ["Do not use Tiger's Fury near maximum Energy.", "Roar uptime normally takes priority over an optional Bite."], failure: "overcapping early, then starving exactly when two finishers need attention." },
      { kicker: "No rear access", title: "Stay active from the front", tag: "Position", iconEntity: "Mangle (Cat)", decision: "Use Mangle and assigned utility until safe rear access returns instead of circling through danger.", actions: ["Mangle (Cat)", "Rake", "Savage Roar"], rules: ["Do not expose the raid to cleaves merely to Shred.", "Return behind the target only through the planned safe side."], failure: "losing several globals or dying while chasing a positional attack." },
      { kicker: "Urgent target", title: "Match setup to target life", tag: "Swap", iconEntity: "Mangle (Cat)", decision: "Use immediate builders and only the maintenance effects that can pay back before the target dies.", actions: ["Feral Charge - Cat", "Mangle (Cat)", "Ferocious Bite"], rules: ["A short-lived add rarely deserves a full Rip setup.", "Follow the assigned kill target rather than preserving boss uptime at the raid's expense."], failure: "finishing a five-point bleed after the urgent target is already dead." },
      { kicker: "Stacked pack", title: "Swipe after threat", tag: "Adds", iconEntity: "Swipe (Cat)", decision: "Use Swipe on a stable pack after the tank controls it, while preserving enough Energy for the next priority target.", actions: ["Tiger's Fury", "Swipe (Cat)", "Mangle (Cat)"], rules: ["Wait for threat and respect crowd control.", "Return to priority damage immediately when the pack or assignment changes."], failure: "opening with Swipe, pulling threat, or spending all Energy before an urgent target appears." },
      { kicker: "Danger or utility", title: "Lose damage to save the pull", tag: "Survival", iconEntity: "Barkskin", decision: "Use mitigation, form changes, Rebirth, or Innervate when that action prevents a death or fulfills an assignment.", actions: ["Barkskin", "Survival Instincts", "Rebirth"], rules: ["Barkskin before predictable damage; Survival Instincts is temporary health, not immunity.", "Announce an emergency Bear transition because it changes threat and damage output."], failure: "remaining in the damage priority while a known survival or recovery action is missed." }
    ],
    utility: [
      [entity("Feral Charge - Cat"), "Fast target access", "Use when the landing point is safe and immediate uptime is worth the cooldown."],
      [entity("Maim"), "Combo-point stun", "Reserve combo points for an assigned interrupt or stun only when the target is eligible."],
      [entity("Dash"), "Movement cooldown", "Use proactively for long travel or mechanics, not after uptime is already lost."],
      [entity("Barkskin"), "Personal mitigation", "Use before predictable damage without leaving Cat Form."],
      [entity("Survival Instincts"), "Temporary health", "Use before a dangerous window and plan healing before it expires."],
      [entity("Rebirth"), "Combat resurrection", "Confirm the target and safe location; leaving form and casting has a real opportunity cost."],
      [entity("Innervate"), "Mana support", "Use on the assigned target when the raid value exceeds one damage global."],
      [entity("Remove Curse"), "Curse removal", "Leave form and cleanse when the assigned debuff is more dangerous than the lost damage."]
    ],
    mistakes: [
      "Treating the priority as a memorized cast sequence instead of reading timers and Energy.",
      "Using Ferocious Bite when Savage Roar or Rip cannot survive the Energy recovery.",
      "Chasing rear access through cleaves, hazards, or excessive travel.",
      "Applying full bleeds to targets that will die before they pay back.",
      "Opening Swipe before the tank establishes the pack.",
      "Refusing to use Barkskin, Rebirth, Innervate, or an emergency form because it lowers the meter."
    ]
  },
  setup: {
    talentGroups: [
      { title: "Cat engine", icon: "ability_druid_mangle2", items: [`${entity("Mangle")} unlocks the core bleed-support attack.`, `${entity("Savage Roar")} turns combo points into a sustained physical-damage buff.`, `${entity("Berserk")} creates a planned low-cost Energy window.`] },
      { title: "Resource control", icon: "ability_mount_jungletiger", items: [`${entity("Omen of Clarity")} creates free-action opportunities.`, `${entity("Primal Precision")} supplies 10 expertise and refunds Energy from missed finishers.`, `${entity("King of the Jungle")} improves Tiger's Fury and supports planned burst.`] },
      { title: "Self-contained utility", icon: "spell_nature_spiritwolf", items: [`${entity("Naturalist")} and ${entity("Master Shapeshifter")} support the complete dungeon baseline.`, "Later raid flex points must preserve 71 allocated points and state what reliability is being traded.", "This Cat page does not silently substitute the separate Bear tank baseline."] }
    ],
    glyphs: [
      [entity("Glyph of Savage Roar", "glyph-name"), '<span class="must">Default</span>', "All sustained combat", "Raises the damage bonus from the buff that anchors the Cat priority."],
      [entity("Glyph of Rip", "glyph-name"), '<span class="must">Default</span>', "Durable targets", "Extends Rip for more builder and refresh room."],
      [entity("Glyph of Shred", "glyph-name"), '<span class="must">Default</span>', "Rear-access targets", "Shred extends Rip within its glyph limit."],
      [entity("Glyph of Mangle", "glyph-name"), '<span class="optional">Position swap</span>', "Limited rear access", "Improves Mangle when the encounter prevents reliable Shred use."],
      [entity("Glyph of Dash", "glyph-name"), '<span class="optional">Minor</span>', "Movement", "Reduces Dash cooldown for repeat movement demands."],
      [entity("Glyph of Unburdened Rebirth", "glyph-name"), '<span class="optional">Minor</span>', "Recovery", "Removes the reagent requirement from Rebirth."]
    ],
    extraSection: { id: "forms", short: "Forms", title: "Form boundaries", icon: "ability_druid_catform", body: `<div class="two-col"><div class="guide-box"><h3>Stay Cat for damage</h3>${list(["Use Cat Form for the normal damage priority.", "Plan every utility cast that removes form, then return deliberately.", "Do not shift repeatedly without a reason; form changes consume mana and globals."])}</div><div class="guide-box"><h3>Bear is an emergency role</h3>${list(["Enter Dire Bear Form only for a named survival, pickup, or recovery job.", "Announce the transition because threat behavior changes.", "A Cat talent and gear set is not the dedicated Bear baseline."])}</div></div>` },
    macros: [
      { title: "Safe Cat opener", entity: "Cat Form", purpose: "Enter Cat Form when needed, then use the selected hostile ability normally.", code: "#showtooltip Cat Form\n/cast [nostance:3] Cat Form" },
      { title: "Focus Maim", entity: "Maim", purpose: "Stun a hostile focus without losing the damage target; fall back to the current target.", code: "#showtooltip Maim\n/cast [@focus,harm,nodead][] Maim" },
      { title: "Mouseover Rebirth", entity: "Rebirth", purpose: "Leave form and combat-resurrect a dead friendly mouseover or target.", code: "#showtooltip Rebirth\n/cancelform\n/cast [@mouseover,help,dead][help,dead] Rebirth" },
      { title: "Emergency Bear", entity: "Dire Bear Form", purpose: "Enter the survival form directly; defensive abilities remain separate decisions.", code: "#showtooltip Dire Bear Form\n/cast Dire Bear Form" }
    ],
    essentialAddons: [`<a href="addons.html?search=Deadly%20Boss%20Mods">Deadly Boss Mods</a> for movement and target-life planning.`, "A 3.3.5-compatible Cat timer that separates Savage Roar, Rip, Rake, and the Mangle debuff.", "An Energy and combo-point display placed near the target and mechanic timers."],
    recommendedAddons: [`WeakAuras/TellMeWhen for ${entity("Savage Roar")}, ${entity("Omen of Clarity")}, ${entity("Tiger's Fury")}, and ${entity("Berserk")}.`, "Details/Recount to review target uptime, misses, bleed uptime, deaths, and damage to assigned targets.", "A threat display for Berserk, Swipe, and emergency Bear transitions."]
  },
  raiding: druidRaiding("cat", {
    assignmentIcon: "ability_druid_savageroar",
    roles: "single-target adds movement utility special",
    consumables: [`${entity("Flask of Endless Rage")} for the default attack-power flask.`, `${entity("Fish Feast")} or equivalent Agility food after verifying the available feast.`, `${entity("Potion of Speed")} for a planned full-uptime window.`],
    prePull: ["Confirm Mangle or equivalent bleed-debuff coverage, Rebirth, Innervate, and emergency-Bear expectations.", "Identify rear access, cleave sides, charge paths, and the first forced movement.", "State target-swap and stun priorities before spending combo points."],
    assignments: [["Sustained target", "Savage Roar, useful bleeds, and required debuffs remain active while Energy is pooled for refreshes.", "Call loss of rear access or a timer collision that changes the normal priority."], ["Adds and swaps", "The raid's priority target receives immediate useful damage with setup matched to its remaining life.", "Call charge hazards, crowd control, or a target likely to die before a bleed pays back."], ["Feral utility", "Stuns, Rebirth, Innervate, mitigation, and emergency form changes happen on the agreed timing.", "Call a form change, reagent, range, immunity, or cooldown conflict." ]],
    verify: ["lich-king"],
    notes: {
      toc: `Maintain the Cat engine on durable targets and match bleed setup to each target's remaining life. On Anub'arak, wait for tank threat before ${entity("Swipe (Cat)")} and respect burrower control.`,
      marrowgar: `Attack from a safe rear quarter, switch immediately to Bone Spikes, and use ${entity("Dash")} or ${entity("Feral Charge - Cat")} only through a safe path during Bone Storm.`,
      deathwhisper: `Follow add priority and crowd control, use ${entity("Maim")} only when assigned, and avoid building full bleeds on targets that will die before their ticks matter.`,
      saurfang: `Remain on the boss unless assigned to Blood Beasts. Never chase a beast through another player's path; immediate Mangle damage and control matter more than a full bleed setup.`,
      putricide: `Switch hard to Volatile Ooze and Gas Cloud, move before Malleable Goo, and choose builders according to rear access and target life. Use Barkskin for predictable raid damage.`,
      "blood-wing": `On Princes, attack only the empowered target and preserve position through swaps. On Blood-Queen, follow bite order, move early for Swarming Shadows, and protect the next Roar or Rip deadline.`,
      valithria: `Prioritize Blazing Skeletons and Suppressors, use Swipe only on secured packs, and reserve Maim for an assigned eligible cast. This encounter rewards correct target selection over long boss-style setup.`,
      sindragosa: `Respect Chilled to the Bone stacks and movement, stop attacking when required, and break only assigned Ice Tombs. Plan Roar duration around air phases and phase-three resets.`,
      "lich-king": `Burn Val'kyr and Raging Spirits by priority, move early for Defile, and do not compromise positioning to preserve a bleed. Verify Hellscream charge and target behavior before depending on a specialized route.`,
      halion: `Stay in the assigned realm, use Barkskin before predictable pulses, and move early around cutters. Keep finishers aligned with periods of actual target access rather than the pull timer alone.`
    }
  })
});

const feralBearDruid = makeDruidSpec(loadDruidConfig("feral-bear-druid"), "bear", {
  quick: {
    summaries: [
      { label: "Core job", value: "Hold enemies and stay healable", detail: "Position the pack, keep threat on the right targets, and use survival tools before incoming damage becomes a rescue." },
      { label: "Default priority", value: "Mangle · Lacerate · Swipe · Maul", detail: "Maintain the required debuffs, queue Maul only with Rage to spare, and react immediately to loose enemies." },
      { label: "Fresh-80 rule", value: "Control beats the damage meter", detail: "A stable pull with safe positioning and planned mitigation is better than spending every Rage point on damage." }
    ],
    engineTitle: "Position → establish → maintain → survive",
    beforeIcon: "ability_racial_bearform",
    firstIcon: "inv_misc_coin_01",
    before: [
      `Enter ${entity("Dire Bear Form")}, apply ${entity("Mark of the Wild")} or ${entity("Gift of the Wild")}, and place ${entity("Thorns")} on yourself.`,
      `Mark a kill target, bind ${entity("Growl")}, ${entity("Feral Charge - Bear")}, ${entity("Bash")}, and ${entity("Challenging Roar")} separately.`,
      `Confirm whether ${entity("Demoralizing Roar")} and ${entity("Faerie Fire (Feral)")} are your assignments or covered elsewhere.`,
      `Inspect healer mana, patrols, line-of-sight corners, escape routes, and the first dangerous pull before engaging.`
    ],
    firstMoves: [
      "Train every level-80 rank and install the complete 0/60/11 dedicated Bear baseline and glyph set.",
      "Begin in normal and heroic dungeons as survival and control permit; practice line-of-sight pulls, Rage discipline, and cooldown calls before raid readiness.",
      "Replace leveling gear with Stamina, armor, Agility, and useful threat stats; Survival of the Fittest provides crit immunity without a 540 Defense requirement.",
      "Build a separate Cat set if an off-role is desired; do not weaken the tank baseline into one compromised hybrid set."
    ],
    chapterTopics: {
      playing: "Threat · Rage · packs · cooldowns",
      setup: "0/60/11 · glyphs · forms · macros",
      building: "Stamina · armor · Agility · threat",
      equipping: "Dungeons · emblems · ToC · ICC",
      raiding: "Assignments · swaps · survival · boss notes"
    }
  },
  playing: {
    priority: `${entity("Dire Bear Form")} and group buffs → position enemies safely → ${entity("Faerie Fire (Feral)")} at range → ${entity("Mangle (Bear)")} → maintain ${entity("Lacerate")} and required ${entity("Demoralizing Roar")} → ${entity("Swipe (Bear)")} for packs or filler → queue ${entity("Maul")} only when Rage remains for the next required action.`,
    openerIcon: "ability_druid_mangle2",
    trackingIcon: "ability_druid_lacerate",
    opener: [
      `Pull with ${entity("Faerie Fire (Feral)")} or use ${entity("Feral Charge - Bear")} only when the landing position is safe.`,
      `Face enemies away from the group, establish ${entity("Mangle (Bear)")}, and use ${entity("Swipe (Bear)")} while marking the priority target.`,
      `Build ${entity("Lacerate")} on a durable target and apply ${entity("Demoralizing Roar")} when the physical-damage reduction is assigned.`,
      `Queue ${entity("Maul")} only after reserving Rage for taunt recovery, interrupts, debuffs, and the next pack action.`
    ],
    tracking: [
      `Threat on every active enemy, the current kill target, ${entity("Growl")}, and ${entity("Challenging Roar")}.`,
      `Rage, ${entity("Mangle (Bear)")}, ${entity("Lacerate")}, ${entity("Demoralizing Roar")}, and ${entity("Faerie Fire (Feral)")}.`,
      `${entity("Savage Defense")}, health, healer mana, ${entity("Barkskin")}, ${entity("Survival Instincts")}, and ${entity("Frenzied Regeneration")}.`,
      `Boss swing or burst timers, tank-swap debuffs, frontal direction, and safe charge paths.`
    ],
    cards: [
      { kicker: "Single durable target", title: "Build reliable threat", tag: "Default", iconEntity: "Mangle (Bear)", decision: "Maintain the required debuffs and Lacerate while keeping enough Rage for reactions.", actions: ["Faerie Fire (Feral)", "Mangle (Bear)", "Lacerate", "Maul"], rules: ["Mangle has priority over filler when available.", "Queue Maul only when it cannot starve the next required action."], failure: "spending every Rage point on Maul and missing a taunt, debuff, or pickup." },
      { kicker: "Enemy pack", title: "Position before accelerating", tag: "Adds", iconEntity: "Swipe (Bear)", decision: "Gather enemies into a stable frontal pack, spread threat, and keep the marked target obvious.", actions: ["Faerie Fire (Feral)", "Swipe (Bear)", "Challenging Roar"], rules: ["Use line of sight to bring casters to the pack.", "Challenging Roar creates a recovery window; it does not establish durable threat by itself."], failure: "charging past the group, exposing frontals, or assuming one Swipe owns every enemy." },
      { kicker: "Low Rage", title: "Protect required actions", tag: "Resource", iconEntity: "Enrage", decision: "Stop queueing Maul, use Enrage only when the armor penalty is safe, and rebuild through incoming or dealt damage.", actions: ["Enrage", "Mangle (Bear)", "Swipe (Bear)"], rules: ["Never treat Enrage as free Rage during a dangerous physical burst.", "Prioritize control and debuffs over filler damage."], failure: "using Enrage into lethal melee damage or continuing to drain Rage with Maul." },
      { kicker: "Loose enemy", title: "Recover deliberately", tag: "Pickup", iconEntity: "Growl", decision: "Taunt the correct target, force immediate follow-up threat, and restore safe positioning.", actions: ["Growl", "Feral Charge - Bear", "Mangle (Bear)"], rules: ["Taunt copies threat temporarily; follow it with a real threat action.", "Charge only when the path and new facing are safe."], failure: "taunting without follow-up or turning the pack's frontal attacks through the group." },
      { kicker: "Physical burst", title: "Layer survival early", tag: "Survival", iconEntity: "Barkskin", decision: "Use the smallest sufficient cooldown before the burst and communicate what remains available.", actions: ["Barkskin", "Survival Instincts", "Frenzied Regeneration"], rules: ["Survival Instincts is temporary health and needs a plan for expiration.", "Frenzied Regeneration converts Rage, so account for the threat and control cost."], failure: "pressing every cooldown after health is already unrecoverable." },
      { kicker: "Magic or special damage", title: "Use the right defense", tag: "Special", iconEntity: "Survival Instincts", decision: "Favor health, timing, movement, resistance, or external help because armor does not solve most spell bursts.", actions: ["Survival Instincts", "Barkskin", "Feral Charge - Bear"], rules: ["Identify the damage school before choosing gear or cooldowns.", "Call for an external cooldown before the hit, not afterward."], failure: "equating high armor with complete protection from magical mechanics." }
    ],
    utility: [
      [entity("Growl"), "Single-target taunt", "Use on the correct hostile target and follow immediately with threat."],
      [entity("Challenging Roar"), "Area taunt window", "Use as planned control or emergency recovery, then establish threat on each enemy."],
      [entity("Feral Charge - Bear"), "Gap close and interrupt", "Use only when the landing position, facing, and path are safe."],
      [entity("Bash"), "Stun and cast stop", "Reserve it for an eligible assigned cast or dangerous enemy."],
      [entity("Demoralizing Roar"), "Physical damage reduction", "Maintain when assigned; the baseline version is not the enhanced raid debuff."],
      [entity("Barkskin"), "Short mitigation", "Use before predictable damage; keep stronger tools for larger windows."],
      [entity("Survival Instincts"), "Temporary maximum health", "Coordinate healing and the end of the effect."],
      [entity("Frenzied Regeneration"), "Rage-to-health recovery", "Use with enough Rage and a stated threat plan."]
    ],
    mistakes: [
      "Looking only at the current target's threat while another enemy attacks a healer.",
      "Queueing Maul until no Rage remains for control or recovery.",
      "Charging into a position that turns frontal attacks toward the group.",
      "Treating Challenging Roar as permanent threat rather than a short recovery window.",
      "Using Enrage during dangerous physical damage without accounting for its armor penalty.",
      "Waiting for critical health before communicating or activating survival cooldowns."
    ]
  },
  setup: {
    talentGroups: [
      { title: "Tank foundation", icon: "ability_druid_naturalperfection", items: [`${entity("Survival of the Fittest")} supplies the full 6% reduction to chance to be critically hit, so the Bear does not chase 540 Defense.`, `${entity("Thick Hide")} and ${entity("Protector of the Pack")} support physical survival.`, `${entity("Natural Reaction")} adds dodge, Rage from dodges, and damage reduction in Bear Form.`] },
      { title: "Threat and control", icon: "ability_druid_mangle2", items: [`${entity("Mangle")} anchors single-target threat and bleed support.`, `${entity("Berserk")} enables a planned multi-target Mangle window and breaks fear on use.`, `${entity("Primal Precision")} supplies 10 expertise and refunds missed finisher Energy for the shared Feral tree, though Bear values its expertise directly.`] },
      { title: "Known flex boundary", icon: "spell_nature_natureguardian", items: ["The mono-Bear baseline keeps core survival and threat complete.", `Enhanced ${entity("Demoralizing Roar")} requires explicit later talent swaps; never claim the baseline supplies the enhanced effect.`, "Any raid variant must preserve 71 points and document exactly which survival or threat tool moved."] }
    ],
    glyphs: [
      [entity("Glyph of Maul", "glyph-name"), '<span class="must">Default</span>', "Dungeons and adds", "Lets Maul strike an additional target for practical multi-target threat."],
      [entity("Glyph of Survival Instincts", "glyph-name"), '<span class="must">Default</span>', "Survival", "Raises the temporary-health gain from Survival Instincts."],
      [entity("Glyph of Frenzied Regeneration", "glyph-name"), '<span class="must">Default</span>', "Recovery", "Raises healing received while Frenzied Regeneration is active."],
      [entity("Glyph of Growl", "glyph-name"), '<span class="optional">Taunt swap</span>', "Progression taunts", "Adds hit chance to Growl when a missed taunt is the actual risk."],
      [entity("Glyph of Challenging Roar", "glyph-name"), '<span class="optional">Minor</span>', "Add recovery", "Reduces the cooldown of the area-taunt recovery tool."],
      [entity("Glyph of Unburdened Rebirth", "glyph-name"), '<span class="optional">Minor</span>', "Off-role recovery", "Removes Rebirth's reagent requirement when a safe form break is possible."]
    ],
    extraSection: { id: "debuffs", short: "Debuffs", title: "Debuff truth and raid variants", icon: "ability_druid_demoralizingroar", body: `<div class="two-col"><div class="guide-box"><h3>What the baseline supplies</h3>${list(["Faerie Fire (Feral) armor reduction when assigned.", "Baseline Demoralizing Roar attack-power reduction.", "Mangle's bleed-damage support when no equivalent effect is present."])}</div><div class="guide-box"><h3>What requires a declared swap</h3>${list(["Improved Demoralizing Roar is not silently included.", "Infected Wounds or other control variants change points and assignments.", "Document the exact points removed and verify all 71 remain allocated."])}</div></div>` },
    macros: [
      { title: "Mouseover Growl", entity: "Growl", purpose: "Taunt a hostile mouseover without losing the main target; fall back to the current target.", code: "#showtooltip Growl\n/cast [@mouseover,harm,nodead][] Growl" },
      { title: "Focus Bash", entity: "Bash", purpose: "Stun the hostile focus without changing the tank target; fall back normally.", code: "#showtooltip Bash\n/cast [@focus,harm,nodead][] Bash" },
      { title: "Direct Bear charge", entity: "Feral Charge - Bear", purpose: "Use the Bear charge on the current hostile target without adding an unsafe target change.", code: "#showtooltip Feral Charge - Bear\n/cast Feral Charge - Bear" },
      { title: "Emergency survival", entity: "Survival Instincts", purpose: "Activate temporary health; Barkskin and Frenzied Regeneration remain separate timing decisions.", code: "#showtooltip Survival Instincts\n/cast Survival Instincts" }
    ],
    essentialAddons: [`<a href="addons.html?search=Deadly%20Boss%20Mods">Deadly Boss Mods</a> for burst, swap, movement, and add timing.`, "Threat plates that show threat state on every visible enemy, not only the selected target.", "A clear boss frame and debuff display for tank-swap stacks and survival timers."],
    recommendedAddons: [`WeakAuras/TellMeWhen for ${entity("Savage Defense")}, ${entity("Lacerate")}, ${entity("Demoralizing Roar")}, and survival cooldowns.`, "Details/Recount to review deaths, damage taken, missed taunts, interrupts, and threat losses rather than damage rank.", "A healer-mana and external-cooldown display for pull pacing and planned burst coverage."]
  },
  raiding: druidRaiding("bear", {
    assignmentIcon: "ability_druid_naturalperfection",
    roles: "main-tank add-tank swap survival special",
    consumables: [`${entity("Flask of Stoneblood")} for the default health flask.`, `${entity("Fish Feast")} or equivalent Stamina food after verifying the available feast.`, `${entity("Indestructible Potion")} for a planned physical-damage window.`],
    prePull: ["Confirm main tank, add tank, taunt, interrupt, external-cooldown, and battle-resurrection assignments.", "Identify frontal direction, movement route, line-of-sight position, and the first survival window.", "State whether baseline or enhanced attack-power reduction is actually present."],
    assignments: [["Boss control", "The boss faces safely, required debuffs remain active, and threat is stable without exhausting Rage.", "Call forced movement, taunt immunity, threat risk, or a missing debuff."], ["Adds and pickups", "Each active enemy has a marked home, threat owner, and recovery path.", "Call a loose enemy, unsafe charge, crowd control, or area-taunt expiration."], ["Survival plan", "Personal and external cooldowns cover named damage windows without unnecessary overlap.", "Call the next burst, current cooldown, healer gap, or plan change early."]],
    verify: ["toc", "lich-king"],
    notes: {
      toc: `Face bosses away, plan taunts and cooldowns before each phase, and separate physical from magical survival needs. On Anub'arak, follow the assigned boss or burrower role and verify Hellscream add positioning and taunt behavior.`,
      marrowgar: `Keep Marrowgar faced away, call Saber Lash coverage, and reposition cleanly after Bone Storm. Pick up or control Bone Spikes only under the raid's tank plan.`,
      deathwhisper: `Gather assigned adds without dragging cleaves through the raid, interrupt eligible casts, and prepare the phase-two boss pickup before the shield breaks.`,
      saurfang: `Hold the boss stable, execute tank swaps on Rune of Blood, and never use uncontrolled movement or area threat that disrupts Blood Beast control.`,
      putricide: `Follow the assigned boss or Abomination role exactly. Move the boss ahead of slime and Malleable Goo, communicate mutation energy or swap changes, and plan cooldowns for phase three.`,
      "blood-wing": `On Princes, control only the assigned active target and preserve orb or add paths. On Blood-Queen, face safely, coordinate the opening link, and plan cooldowns around known tank damage.`,
      valithria: `Pick up assigned Abominations, Zombies, and other adds quickly, keep frontals away from healers, and use Bash or charge interrupts only on eligible priority casts.`,
      sindragosa: `Manage Frost Breath cooldowns and Mystic Buffet resets, position tombs according to the plan, and never turn the frontal or tail through the raid during phase-three movement.`,
      "lich-king": `Execute Soul Reaper cooldowns and taunt swaps, position Raging Spirits and Shamblings safely, and communicate every movement before Defile. Verify Hellscream-specific taunt and add behavior before relying on a narrow sequence.`,
      halion: `Stay in the assigned realm, face Halion away from the raid, move smoothly around cutters, and plan cooldowns for breaths and overlap. Do not allow realm movement to rotate the frontal through players.`
    }
  })
});

const restorationDruid = makeDruidSpec(loadDruidConfig("restoration-druid"), "restoration", {
  quick: {
    summaries: [
      { label: "Core job", value: "Put healing ahead of damage", detail: "Pre-HoT known danger, triage the next injury, and keep enough globals and mana for the mechanic that follows." },
      { label: "Default priority", value: "Rejuvenation → Wild Growth → Swiftmend", detail: "Use Lifebloom, Regrowth, Nourish, and emergency tools according to assignment and incoming damage—not as a fixed loop." },
      { label: "Fresh-80 rule", value: "Triage beats blanket casting", detail: "Cover players who will take damage; empty globals on safe targets create mana problems without preventing deaths." }
    ],
    engineTitle: "Anticipate → cover → triage → recover",
    beforeIcon: "spell_nature_rejuvenation",
    firstIcon: "inv_misc_coin_01",
    before: [
      `Apply ${entity("Mark of the Wild")} or ${entity("Gift of the Wild")} and confirm the tank has ${entity("Thorns")} when appropriate.`,
      `Confirm tank, raid, cleanse, ${entity("Innervate")}, ${entity("Rebirth")}, and emergency-cooldown assignments.`,
      `Place the tank, focus, raid frames, mana, ${entity("Clearcasting")}, and boss timers where all are visible together.`,
      `Carry reagents, water, ${entity("Flask of the Frost Wyrm")}, food, and mana potions appropriate to the run.`
    ],
    firstMoves: [
      "Train every level-80 rank and install the complete 11/0/60 self-contained Restoration baseline and glyph set.",
      "Enter normal and heroic dungeons immediately; practice pre-HoTs, Lifebloom decisions, Swiftmend, cleansing, and mana pacing before raid optimization.",
      "Replace leveling gear with spell power, useful haste, Spirit or MP5, and enough Intellect to finish pulls safely.",
      "Treat 735 haste with Celestial Focus or 856 without it as later raid goals under stated raid buffs—not as Fresh-80 dungeon gates."
    ],
    chapterTopics: {
      playing: "HoTs · triage · Lifebloom · mana",
      setup: "11/0/60 · glyphs · macros · frames",
      building: "Spell power · haste · Spirit · MP5",
      equipping: "Dungeons · emblems · ToC · ICC",
      raiding: "Assignments · recovery · utility · boss notes"
    }
  },
  playing: {
    priority: `Pre-place ${entity("Rejuvenation")} and assigned ${entity("Regrowth")} before known damage → use ${entity("Wild Growth")} on injured groups → ${entity("Swiftmend")} a HoT target needing immediate help → maintain assigned ${entity("Lifebloom")} stacks deliberately → use ${entity("Nourish")} or ${entity("Regrowth")} for direct triage → use ${entity("Nature's Swiftness")} and ${entity("Healing Touch")} for a planned emergency.`,
    openerIcon: "spell_nature_rejuvenation",
    trackingIcon: "ability_druid_flourish",
    opener: [
      `Pre-HoT the tank with ${entity("Rejuvenation")} and ${entity("Regrowth")} only close enough to the pull that useful duration remains.`,
      `Use ${entity("Lifebloom")} according to the tank assignment; refresh the stack intentionally or allow a planned bloom for mana return and healing.`,
      `Use ${entity("Wild Growth")} after real group damage or just ahead of a known clustered hit.`,
      `Preserve ${entity("Swiftmend")} and the ${entity("Nature's Swiftness")} emergency for actual triage rather than spending every tool at the pull.`
    ],
    tracking: [
      `${entity("Rejuvenation")}, ${entity("Regrowth")}, and ${entity("Lifebloom")} by target and remaining duration.`,
      `${entity("Wild Growth")}, ${entity("Swiftmend")}, ${entity("Nature's Swiftness")}, ${entity("Tranquility")}, and ${entity("Barkskin")}.`,
      `Mana, ${entity("Innervate")}, ${entity("Clearcasting")}, potion use, and the expected remaining encounter time.`,
      `Incoming-damage timers, range, movement, curses, poisons, and the assigned ${entity("Rebirth")} target.`
    ],
    cards: [
      { kicker: "Steady tank damage", title: "Build a sustainable tank layer", tag: "Tank", iconEntity: "Lifebloom", decision: "Maintain the assigned HoTs and use direct healing only when incoming damage exceeds their coverage.", actions: ["Rejuvenation", "Regrowth", "Lifebloom", "Nourish"], rules: ["Refresh Lifebloom intentionally; a bloom and mana return can be correct when planned.", "Nourish gains value from existing HoTs but should still answer real damage."], failure: "rolling an expensive stack without regard for mana, target swaps, or the next damage event." },
      { kicker: "Sudden injury", title: "Land the next safe heal", tag: "Triage", iconEntity: "Swiftmend", decision: "Use Swiftmend on an eligible HoT target, then choose Nourish, Regrowth, or the emergency based on time to death.", actions: ["Swiftmend", "Nourish", "Nature's Swiftness", "Healing Touch"], rules: ["The fastest available button is not automatically the smallest sufficient answer.", "Do not consume Nature's Swiftness for damage ordinary triage can cover."], failure: "continuing blanket HoTs while one assigned target will die before the next tick." },
      { kicker: "Group damage", title: "Heal the cluster that is hurt", tag: "Raid", iconEntity: "Wild Growth", decision: "Place Wild Growth on a target whose nearby group will receive useful jumps, then Rejuvenate players with continuing danger.", actions: ["Wild Growth", "Rejuvenation", "Swiftmend"], rules: ["Target position matters; do not assume the selected unit represents the injured cluster.", "Blanket only the players and duration supported by the actual damage pattern."], failure: "casting Wild Growth on an isolated player or covering safe groups while the damaged group falls." },
      { kicker: "Forced movement", title: "Move while preserving triage", tag: "Mobile", iconEntity: "Rejuvenation", decision: "Use instant heals, Swiftmend, utility, or Barkskin while moving and choose the destination before leaving range.", actions: ["Rejuvenation", "Swiftmend", "Barkskin"], rules: ["Move early so the mechanic does not force a panic route.", "Do not refresh every HoT early merely because an instant global is available."], failure: "ending movement out of range, out of line of sight, or without an emergency global." },
      { kicker: "Mana pressure", title: "Recover before the dry phase", tag: "Mana", iconEntity: "Innervate", decision: "Reduce low-value coverage, use Clearcasting intelligently, and activate Innervate early enough for full value.", actions: ["Clearcasting", "Innervate", "Lifebloom"], rules: ["A free cast should answer a useful healing need, not manufacture overheal.", "Match Lifebloom maintenance to the assignment instead of rolling every available tank."], failure: "maintaining maximum coverage until mana reaches zero and recovery comes too late." },
      { kicker: "Death or collapse", title: "Recover the raid deliberately", tag: "Recovery", iconEntity: "Rebirth", decision: "Stabilize living players, resurrect the agreed target in a safe location, and use Tranquility only where its channel can complete usefully.", actions: ["Rebirth", "Tranquility", "Barkskin"], rules: ["Confirm the target and healing follow-up before Rebirth.", "Use Barkskin before a vulnerable Tranquility channel when incoming damage is expected."], failure: "starting a long recovery cast while the remaining tank or healer is about to die." }
    ],
    utility: [
      [entity("Remove Curse"), "Curse removal", "Prioritize assigned lethal or control curses over another HoT global."],
      [entity("Abolish Poison"), "Repeated poison removal", "Use when recurring applications justify the ongoing dispel effect."],
      [entity("Innervate"), "Mana recovery", "Assign before the pull and use early enough to gain the full return."],
      [entity("Rebirth"), "Combat resurrection", "Confirm target, location, reagent, and immediate healing coverage."],
      [entity("Barkskin"), "Personal mitigation", "Use before predictable damage or a vulnerable channel."],
      [entity("Tranquility"), "Group recovery channel", "Use for sustained group damage when range, pushback, and movement permit the channel."],
      [entity("Entangling Roots"), "Root control", "Use on eligible melee enemies only within the tank and control plan."],
      [entity("Cyclone"), "Short immunity control", "Coordinate carefully because the target cannot receive damage or healing."]
    ],
    mistakes: [
      "Blanketing safe targets until mana becomes the emergency.",
      "Refreshing Lifebloom automatically instead of deciding whether the stack should roll or bloom.",
      "Holding Swiftmend and Nature's Swiftness until after the assigned target dies.",
      "Casting Wild Growth on a unit positioned away from the injured cluster.",
      "Moving late and ending outside healing range or line of sight.",
      "Starting Rebirth or Tranquility before stabilizing the players who must survive the cast."
    ]
  },
  setup: {
    talentGroups: [
      { title: "HoT foundation", icon: "spell_nature_rejuvenation", items: [`${entity("Tree of Life")} defines the healing form and reduces HoT mana costs.`, `${entity("Empowered Rejuvenation")} improves scaling for key periodic effects.`, `${entity("Swiftmend")} converts an active Rejuvenation or Regrowth into immediate triage.`] },
      { title: "Raid and tank tools", icon: "ability_druid_flourish", items: [`${entity("Wild Growth")} supplies efficient short-cooldown group healing.`, `${entity("Living Seed")} creates follow-up healing after critical direct heals.`, `${entity("Nature's Swiftness")} supports a planned instant Healing Touch emergency.`] },
      { title: "Self-contained mana", icon: "spell_nature_lightning", items: [`${entity("Omen of Clarity")} and ${entity("Intensity")} provide value without assumed raid-only support.`, `${entity("Celestial Focus")} supplies 3% haste in the displayed 11/0/60 baseline.`, "If those Balance points move later, the haste model changes from roughly 735 to roughly 856 under the stated raid buffs."] }
    ],
    glyphs: [
      [entity("Glyph of Swiftmend", "glyph-name"), '<span class="must">Default</span>', "All healing", "Prevents Swiftmend from consuming Rejuvenation or Regrowth."],
      [entity("Glyph of Wild Growth", "glyph-name"), '<span class="must">Default</span>', "Groups and raids", "Adds one target to Wild Growth."],
      [entity("Glyph of Rapid Rejuvenation", "glyph-name"), '<span class="must">Default</span>', "Haste-aware coverage", "Lets haste shorten Rejuvenation's tick interval; reassess against mana and assignments."],
      [entity("Glyph of Nourish", "glyph-name"), '<span class="optional">Tank-healing swap</span>', "Direct tank support", "Improves Nourish for each HoT already present on the target."],
      [entity("Glyph of Unburdened Rebirth", "glyph-name"), '<span class="optional">Minor</span>', "Recovery", "Removes the reagent requirement from Rebirth."],
      [entity("Glyph of the Wild", "glyph-name"), '<span class="optional">Minor</span>', "Buff recovery", "Reduces the mana cost of Mark and Gift of the Wild."]
    ],
    extraSection: { id: "frames", short: "Frames", title: "Raid-frame information", icon: "inv_misc_pocketwatch_01", body: `<div class="two-col"><div class="guide-box"><h3>Show clearly</h3>${list(["Health deficit and incoming heals.", "Your Rejuvenation, Regrowth, and Lifebloom duration and stacks.", "Curse and poison indicators, range, line of sight, and dead status."])}</div><div class="guide-box"><h3>Avoid noise</h3>${list(["Do not hide dangerous debuffs under oversized HoT icons.", "Separate your effects from other Druids where possible.", "Test every click or mouseover binding outside the raid before relying on it."])}</div></div>` },
    macros: [
      { title: "Mouseover Rejuvenation", entity: "Rejuvenation", purpose: "Heal a living friendly mouseover, then a friendly target, then self without changing targets.", code: "#showtooltip Rejuvenation\n/cast [@mouseover,help,nodead][help,nodead][@player] Rejuvenation" },
      { title: "Mouseover Swiftmend", entity: "Swiftmend", purpose: "Use immediate triage on a living friendly mouseover or target.", code: "#showtooltip Swiftmend\n/cast [@mouseover,help,nodead][help,nodead][@player] Swiftmend" },
      { title: "Mouseover Remove Curse", entity: "Remove Curse", purpose: "Cleanse a friendly mouseover without changing the healing target.", code: "#showtooltip Remove Curse\n/cast [@mouseover,help,nodead][help,nodead][@player] Remove Curse" },
      { title: "Mouseover Rebirth", entity: "Rebirth", purpose: "Combat-resurrect a dead friendly mouseover or target.", code: "#showtooltip Rebirth\n/cast [@mouseover,help,dead][help,dead] Rebirth" },
      { title: "Mouseover Innervate", entity: "Innervate", purpose: "Give mana to a living friendly mouseover, current friendly target, or self.", code: "#showtooltip Innervate\n/cast [@mouseover,help,nodead][help,nodead][@player] Innervate" }
    ],
    essentialAddons: [`<a href="addons.html?search=Deadly%20Boss%20Mods">Deadly Boss Mods</a> for incoming-damage and movement timing.`, "3.3.5-compatible raid frames that display your HoT durations, Lifebloom stacks, debuffs, range, and incoming heals.", "A mana and cooldown display visible beside the raid frames rather than at the edge of the screen."],
    recommendedAddons: [`WeakAuras/TellMeWhen for ${entity("Clearcasting")}, ${entity("Wild Growth")}, ${entity("Swiftmend")}, and ${entity("Innervate")}.`, "Details/Recount to review deaths, target coverage, overhealing, dispels, mana use, and cooldown timing.", "Clique or tested mouseover macros for direct bindings; never install a binding package without verifying original-client behavior."]
  },
  raiding: druidRaiding("restoration", {
    assignmentIcon: "ability_druid_flourish",
    roles: "tank-healing raid-healing movement utility special",
    consumables: [`${entity("Flask of the Frost Wyrm")} for the default spell-power flask.`, `${entity("Fish Feast")} or equivalent spell-power food after verifying the available feast.`, `${entity("Runic Mana Potion")} when mana completion matters; use a speed potion only for a named healing window.`],
    prePull: ["Confirm tank, raid, cleanse, Innervate, Rebirth, and major-recovery assignments.", "Identify the first damage event, movement route, safe Tranquility position, and range boundaries.", "State the selected haste model and actual raid buffs before comparing a cap."],
    assignments: [["Tank support", "Assigned tanks carry deliberate HoTs and receive direct triage before the next lethal hit.", "Call a tank swap, range loss, expiring stack, or cooldown gap."], ["Raid coverage", "Wild Growth and Rejuvenation land on players who will receive useful healing through the damage pattern.", "Call a spread group, movement gap, or recovery window that needs help."], ["Recovery and utility", "Cleanses, Innervate, Rebirth, Barkskin, and Tranquility occur on agreed targets and safe timings.", "Call target, range, reagent, channel, or mana conflicts early."]],
    verify: ["valithria", "lich-king"],
    notes: {
      toc: `Match HoTs to the active tank and damage pattern, cleanse assigned effects, and preserve mana across the encounter sequence. On Anub'arak, follow the phase-three healing plan rather than reflexively filling every health bar.`,
      marrowgar: `Pre-HoT assigned tanks, switch triage immediately to Bone Spike targets, and use instant spells while moving during Bone Storm. Re-establish tank coverage before Marrowgar reconnects.`,
      deathwhisper: `Heal the active add tank and threatened players, remove assigned curses, and move early from Death and Decay. Prepare coverage for the transition as the mana shield ends.`,
      saurfang: `Keep deliberate coverage on tanks and Mark targets, use Wild Growth only where jumps are valuable, and execute the Rune of Blood swap plan without wasting mana on harmless deficits.`,
      putricide: `Pre-HoT movement and target-swap damage, stay ahead of Malleable Goo, and keep range on the active tank through transitions. Coordinate plague handling and phase-three mana before the pull.`,
      "blood-wing": `On Princes, cover the active tank and movement damage without standing in unsafe range. On Blood-Queen, pre-HoT air-phase damage, follow the bite order, and move early with Swarming Shadows.`,
      valithria: `Follow the assigned portal or outside-healing role. Portal healers preserve stacks and route safely; outside healers stabilize tanks and priority targets. Verify Hellscream portal, buff, and direct-heal interactions before optimizing around them.`,
      sindragosa: `Manage Unchained Magic and Instability, use instant HoTs while repositioning, and reset Mystic Buffet behind the correct tomb. Stop casting before stacks become lethal.`,
      "lich-king": `Pre-HoT Infest targets according to the raid plan, cover tanks through Soul Reaper, and move early for Defile. Coordinate Rebirth and Tranquility rather than channeling through an unsafe mechanic; verify Hellscream Infest behavior.`,
      halion: `Stay in the assigned realm, cover tanks before breaths, and use instant healing while moving around cutters. Preserve line of sight and avoid beginning Tranquility immediately before forced movement.`
    }
  })
});

const specs = [holyPriest, shadowPriest, marksmanshipHunter, afflictionWarlock, demonologyWarlock, destructionWarlock, balanceDruid, feralCatDruid, feralBearDruid, restorationDruid];
const renderers = {
  quickStart: renderQuickStart,
  playing: renderPlaying,
  setup: renderSetup,
  building: renderBuilding,
  equipping: renderEquipping,
  raiding: renderRaiding
};

const cliArgs = process.argv.slice(2);
const quickStartOnly = cliArgs.includes("--quick-start-only");
const specArg = cliArgs.find((arg) => arg.startsWith("--spec="));
const requestedSpec = specArg?.slice("--spec=".length);
const pageArg = cliArgs.find((arg) => arg.startsWith("--page="));
const requestedPage = pageArg?.slice("--page=".length);
const selectedSpecs = requestedSpec ? specs.filter((spec) => spec.slug === requestedSpec) : specs;
if (requestedSpec && selectedSpecs.length === 0) {
  throw new Error(`Unknown spec slug: ${requestedSpec}`);
}
if (requestedPage && !pageOrder.some(([pageKey]) => pageKey === requestedPage)) {
  throw new Error(`Unknown page key: ${requestedPage}`);
}
const selectedPages = requestedPage
  ? pageOrder.filter(([pageKey]) => pageKey === requestedPage)
  : quickStartOnly
  ? pageOrder.filter(([pageKey]) => pageKey === "quickStart")
  : pageOrder;

for (const spec of selectedSpecs) {
  for (const [pageKey, , fileSuffix] of selectedPages) {
    const destination = path.join(root, "guides", `${spec.slug}-${fileSuffix}.html`);
    fs.writeFileSync(destination, renderers[pageKey](spec), "utf8");
  }
}

console.log(`Rendered ${selectedSpecs.length * selectedPages.length} complete fresh-80 guide pages.`);
