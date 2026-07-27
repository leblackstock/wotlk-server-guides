#!/usr/bin/env node
import fs from "node:fs";
import path from "node:path";

const root = process.cwd();
const esc = (value) => String(value)
  .replaceAll("&", "&amp;")
  .replaceAll("<", "&lt;")
  .replaceAll(">", "&gt;")
  .replaceAll('"', "&quot;");
const icon = (name, className = "spell-icon") =>
  `<img class="${className}" src="https://wow.zamimg.com/images/wow/icons/large/${esc(name)}.jpg" alt="" aria-hidden="true" onerror="this.remove()">`;
const entity = (name, className = "ability-name", withIcon = false) =>
  `<span class="${className}"${withIcon ? ` data-entity-icon="${esc(name)}"` : ""}>${esc(name)}</span>`;
const item = (name, quality = "q-epic", withIcon = false) =>
  entity(name, `item-name ${quality}`, withIcon);
const list = (items, className = "clean-list") =>
  `<ul class="${className}">${items.map((entry) => `<li>${entry}</li>`).join("")}</ul>`;
const table = (headers, rows, className = "") =>
  `<div class="table-wrap"><table${className ? ` class="${className}"` : ""}><thead><tr>${headers.map((header) => `<th>${header}</th>`).join("")}</tr></thead><tbody>${rows.map((row) => `<tr>${row.map((cell) => `<td>${cell}</td>`).join("")}</tr>`).join("")}</tbody></table></div>`;
const uniconizedSections = new Set(["guide-pages", "sources", "mistakes", "professions", "special", "assignments"]);
const section = (spec, id, title, body, iconName = spec.icons.class) =>
  `<section class="common" id="${id}"><h2 class="guide-category-heading">${uniconizedSections.has(id) ? "" : `${icon(iconName)} `}${title}<a class="guide-back-to-top" href="#top" aria-label="Back to top">↑ Top</a></h2>${body}</section>`;
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
  <link rel="stylesheet" href="../assets/style.css?v=20260726-global-top-links-v1">
  <link rel="stylesheet" href="../assets/${spec.slug}.css?v=${spec.cacheKey}">
  <script src="../assets/${spec.tooltipFile}?v=${spec.cacheKey}" defer></script>
  <script src="../assets/${spec.slug}.js?v=${spec.cacheKey}" defer></script>
</head>
<body data-guide-class="${spec.classSlug}" data-guide-spec="${spec.specKey}">
  <div class="wrap" id="top">
    ${nav(spec, current)}
    <header>
      <span class="page-kicker">${esc(spec.name)} • Fresh level 80</span>
      <h1>WotLK 3.3.5 <span>${esc(title)}</span></h1>
      <p class="sub">${esc(description)}</p>
      <div class="jump-nav" aria-label="Topics on this page">${jumps.map(([id, label]) => `<a href="#${id}">${esc(label)}</a>`).join("")}</div>
    </header>
    <main>${body}${pager(spec, current)}</main>
    <footer>Unofficial player-made Hellscream guide. Verify live tooltips, raid assignments, and server scripting.</footer>
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
  const engine = `<div class="summary-card combat-engine"><span class="summary-label">Combat engine</span><div class="summary-value">${esc(spec.quick.engineTitle)}</div><div class="engine-grid">${spec.mechanics.map((mechanic) => `<div class="engine-step mechanic-${mechanic.key}"><strong data-entity-icon="${esc(mechanic.iconEntity)}">${esc(mechanic.label)}</strong><p>${esc(mechanic.use)}</p></div>`).join("")}</div></div>`;
  const chapters = pageOrder.slice(1).map(([key, label], index) => `<a class="chapter-card" href="${href(spec, key)}"><span class="chapter-number">${index + 1}</span><h3>${icon(spec.icons[key])} ${label}</h3><p>${esc(spec.descriptions[key])}</p><span class="chapter-topics">${esc(spec.quick.chapterTopics[key])}</span></a>`).join("");
  const body =
    section(spec, "quick-start", "Two-minute operating manual", `<div class="summary-grid">${summaries}${engine}</div>
      <details class="server-behavior"><summary>${icon("inv_misc_wrench_01", "ability-icon")} Server behavior on Hellscream</summary><p>${esc(spec.serverNote)}</p></details>
      <div class="two-col" style="margin-top:12px"><div class="guide-box"><h3>${icon(spec.quick.beforeIcon, "ability-icon")} Before the pull</h3>${list(spec.quick.before, "checklist")}</div><div class="guide-box"><h3>${icon(spec.quick.firstIcon, "ability-icon")} First fresh-80 moves</h3>${list(spec.quick.firstMoves, "priority-list")}</div></div>`, spec.icons.quickStart) +
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
    section(spec, "mistakes", "Mistakes that cost pulls", `<div class="two-col"><div class="note warning"><strong>Mechanical mistakes</strong>${list(spec.playing.mistakes.slice(0, Math.ceil(spec.playing.mistakes.length / 2)))}</div><div class="note danger"><strong>Raid mistakes</strong>${list(spec.playing.mistakes.slice(Math.ceil(spec.playing.mistakes.length / 2)))}</div></div>`, "ability_creature_cursed_03") +
    section(spec, "sources", "Sources and verification", sourceList(spec.sources.playing), "inv_misc_book_11");
  return shell(spec, "playing", `Playing your ${spec.name}`, spec.descriptions.playing, [["engine", "Combat engine"], ["playbooks", "Playbooks"], ["utility", "Cooldowns"], ["mistakes", "Mistakes"], ["sources", "Sources"]], body);
}

function renderSetup(spec) {
  const talent = `<div class="note spec"><strong>Recommended baseline:</strong> ${esc(spec.talent.points)} ${esc(spec.talent.name)}.</div>
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
    section(spec, "path", "Fresh-80 gearing path", stages, "inv_misc_map_01") +
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
    section(spec, "fresh", "Fresh-80 and crafted targets", table(["Slot", "Target", "Standard source", "Upgrade logic"], spec.equipping.fresh), "inv_hammer_20") +
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
  slug: "holy-priest",
  specKey: "priest-holy",
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
    { key: "triage", label: "Triage", iconEntity: "Flash Heal", use: "Use the smallest spell that lands safely before the next damage." },
    { key: "serendipity", label: "Serendipity", iconEntity: "Serendipity", use: "Build with Flash Heal or Binding Heal; spend on Prayer of Healing or Greater Heal." },
    { key: "prayer", label: "Prayer", iconEntity: "Prayer of Mending", use: "Aim Prayer of Mending and Circle of Healing where several players will take damage." },
    { key: "mana", label: "Mana", iconEntity: "Shadowfiend", use: "Plan Inner Focus, Shadowfiend, Hymn of Hope, and lower-cost fillers early." }
  ],
  roleFilters: [["raid-healing", "Raid healing"], ["tank-support", "Tank support"], ["utility", "Dispel / utility"], ["cooldown", "Cooldown"], ["special", "Special assignment"]],
  quick: {
    summaries: [
      { label: "Core job", value: "Prevent the next death", detail: "Holy is a flexible raid healer. Choose by damage pattern, not by a rigid rotation." },
      { label: "Default rhythm", value: "PoM → CoH → triage", detail: "Keep Prayer of Mending moving, use Circle of Healing on real clusters, then fill intelligently." },
      { label: "Fresh-80 rule", value: "Mana first, speed second", detail: "A healer with empty mana has zero throughput. Add haste after sustained activity is comfortable." }
    ],
    engineTitle: "Predict → choose → land → recover",
    beforeIcon: "spell_holy_prayerofmendingtga",
    firstIcon: "inv_misc_coin_01",
    before: [
      `Use ${entity("Inner Fire")} and the assigned raid prayers; carry candles for group buffs.`,
      `Confirm raid-healing, tank-support, dispel, and ${entity("Guardian Spirit")} assignments.`,
      `Pre-place ${entity("Lightwell")} only where the raid can actually click it safely.`,
      `Cast ${entity("Prayer of Mending")} on the pull target and pre-${entity("Renew")} active tanks when damage is imminent.`
    ],
    firstMoves: [
      `Train every rank-80 heal and install raid frames that show range, aggro, diseases, and dispellable magic.`,
      `Buy or farm a mana trinket; enchant usable gear instead of waiting for a fantasy best-in-slot set.`,
      `Run normal Trial of the Champion, heroic dungeons, daily randoms, and weekly raids for Triumph and Frost emblems.`,
      `Enter raids once the set is coherent and enchanted; execution beats another week of shopping.`
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
    name: "standard fresh-80 Holy raid build",
    summary: "This version keeps the crucial Discipline mana tools and the full Holy raid-healing engine. Move flex points only when raid composition and actual logs show a reason.",
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
      { title: "Fresh level 80", icon: "inv_misc_coin_01", items: ["Equip coherent spell-power gear with Intellect and useful secondaries.", "Secure two functional trinkets, a strong weapon, and all inexpensive enchants.", "Prefer mana stability over copying an ICC haste target."] },
      { title: "Raid-ready base", icon: "achievement_boss_general_nazgrim", items: ["Finish the 18/53/0 setup and glyphs.", "Practice sustained heroic-dungeon pulls without drinking after every pack.", "Carry mana potions and know the planned Shadowfiend/Hymn window."] },
      { title: "Encounter tuning", icon: "inv_misc_gear_01", items: ["Favor extra haste and spell power for short burst fights.", "Favor Intellect, Spirit, and mana trinkets for long progression pulls.", "Keep a throughput set for Valithria where encounter mechanics can solve mana."] }
    ],
    gems: [
      ["Meta", item("Insightful Earthsiege Diamond", "q-rare"), "None for general progression", "Activate with one red, one yellow, and one blue gem."],
      ["Red", item("Runed Cardinal Ruby"), item("Luminous Ametrine"), "Use pure spell power after mana is comfortable; use spell power/Intellect while stabilizing."],
      ["Yellow", item("Luminous Ametrine"), item("Quick King's Amber"), "Match worthwhile Intellect or haste bonuses."],
      ["Blue", item("Purified Dreadstone"), item("Sparkling Majestic Zircon"), "Use the minimum needed for the meta unless a strong socket bonus justifies more."],
      ["Any color", item("Nightmare Tear"), "Profession gem if applicable", "One Nightmare Tear efficiently satisfies all three meta colors."]
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
      ["Off-hand", item("Faces of Doom"), "Inscription BoE", "Pairs with a one-handed weapon and supplies strong early stats."],
      ["Wrists", item("Bejeweled Wizard's Bracers"), "Tailoring BoE", "A costly but long-lived haste piece; confirm faction version and local material price."],
      ["Legs", item("Lightweave Leggings"), "ICC tailoring craft", "High-level healer cloth that can bridge deep into ICC."],
      ["Feet", item("Sandals of Consecration"), "ICC tailoring craft", "Strong healer boots when Primordial Saronite is realistic."],
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
      ["Holy Priest gems and enchants", "https://www.wowhead.com/wotlk/guide/classes/priest/holy/healer-enchants-consumables-pve"]
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
  slug: "shadow-priest",
  specKey: "shadow",
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
    { key: "dots", label: "DoTs", iconEntity: "Vampiric Touch", use: "Maintain Vampiric Touch and Devouring Plague without clipping their final ticks." },
    { key: "weaving", label: "Shadow Weaving", iconEntity: "Shadow Weaving", use: "Reach five stacks before the lasting Shadow Word: Pain application." },
    { key: "channel", label: "Channel", iconEntity: "Mind Flay", use: "Fit complete Mind Flay ticks between higher-priority events." },
    { key: "mana", label: "Mana & support", iconEntity: "Dispersion", use: "Use Shadowfiend, Dispersion, Replenishment, and Hymn of Hope deliberately." }
  ],
  roleFilters: [["single-target", "Single target"], ["multi-dot", "Adds / multi-DoT"], ["utility", "Utility / dispel"], ["soak", "Dispersion soak"], ["special", "Special assignment"]],
  quick: {
    summaries: [
      { label: "Boss hit target", value: "17% total spell hit", detail: "With 3/3 Shadow Focus and personal Misery, a Horde priest needs 11% from gear: 289 rating." },
      { label: "Opener rule", value: "Five stacks, then Pain", detail: "Build Shadow Weaving before the long-lived Shadow Word: Pain that Mind Flay will refresh." },
      { label: "Fresh-80 rule", value: "Cap hit before greed", detail: "A missed Vampiric Touch, Mind Blast, or DoT costs more than a small uncapped throughput gain." }
    ],
    engineTitle: "Apply → stack → snapshot → maintain",
    beforeIcon: "spell_shadow_shadowform",
    firstIcon: "inv_misc_coin_01",
    before: [
      `Activate ${entity("Shadowform")} and ${entity("Inner Fire")}; confirm Fortitude, Spirit, and Shadow Protection assignments.`,
      `Confirm the boss target, required utility, and that the equipped boss set reaches its spell-hit target.`,
      `Confirm whether the raid needs ${entity("Vampiric Embrace")}, ${entity("Mass Dispel")}, ${entity("Silence")}, or a ${entity("Dispersion")} soak.`,
      `Pre-pot only when the encounter and pull timer make the potion window safe.`
    ],
    firstMoves: [
      "Reach the boss spell-hit target and install visible DoT timers.",
      `Farm ${item("Abyssal Rune", "q-rare")} and another functional trinket before chasing expensive ICC pieces.`,
      "Practice a five-stack opener on a training dummy until Shadow Word: Pain is never applied early.",
      "Run heroics and Trial of the Champion while buying Triumph upgrades for the weakest slots."
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
    name: "standard Shadow raid build",
    summary: "The damage engine is tight: core Shadow talents, Improved Inner Fire, Meditation, and Inner Focus leave only narrow flex around pushback protection, range, mana, and Silence.",
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
      { title: "Fresh level 80", icon: "inv_misc_coin_01", items: ["Reach 289 hit rating for a Horde boss set with 3/3 Shadow Focus and Misery.", "Equip spell power and haste after hit; accept Spirit on strong cloth pieces.", "Farm a usable weapon and two trinkets before expensive optimization."] },
      { title: "Raid-ready base", icon: "spell_shadow_shadowform", items: ["Use the 14/0/57 build and correct glyphs.", "Maintain near-complete Vampiric Touch and Devouring Plague uptime on a dummy.", "Carry a mana plan and a utility assignment."] },
      { title: "Encounter tuning", icon: "inv_misc_gear_01", items: ["Keep a hit-capped set through every swap.", "Use burst pieces for short adds and sustained pieces for long bosses.", "Do not break strong tier bonuses for a tiny single-item stat gain."] }
    ],
    gems: [
      ["Meta", item("Chaotic Skyflare Diamond", "q-rare"), "None for general damage", "Requires two blue gems; plan activation before socketing the rest."],
      ["Red", item("Runed Cardinal Ruby"), "Profession spell-power gem", "Default when the bonus is weak."],
      ["Yellow", item("Reckless Ametrine"), item("Quick King's Amber"), "Use spell power/haste to collect worthwhile bonuses."],
      ["Blue", item("Purified Dreadstone"), item("Nightmare Tear"), "Meet the meta with the least damage loss and collect strong spell-power bonuses."],
      ["Hit repair", item("Veiled Ametrine"), item("Rigid King's Amber"), "Use only until the exact set reaches cap; replace excess hit after upgrades."]
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
      ["Chest", item("Merlin's Robe"), "Tailoring BoE", "Strong spell-power and haste craft; use the correct faction version."],
      ["Wrists", item("Bejeweled Wizard's Bracers"), "Tailoring BoE", "High-item-level haste craft that can survive into ICC."],
      ["Legs", item("Leggings of Woven Death"), "ICC tailoring craft", "Powerful caster legs with sockets and offensive secondaries."],
      ["Feet", item("Deathfrost Boots"), "ICC tailoring craft", "Strong caster boots when Primordial Saronite is affordable."],
      ["Trinket", item("Illustration of the Dragon Soul"), "Sartharion 25", "Stacking spell power with strong sustained value."],
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
      ["Shadow Priest enchants and consumables", "https://www.wowhead.com/wotlk/guide/classes/priest/shadow/dps-enchants-consumables-pve"]
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
  slug: "marksmanship-hunter",
  specKey: "marksmanship",
  tooltipFile: "hunter-tooltips.js",
  cacheKey: "20260726-marksman-v2-color-icons",
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
    { key: "sting", label: "Sting", iconEntity: "Serpent Sting", use: "Apply Serpent Sting once, then protect it with timely Chimera Shot refreshes." },
    { key: "shots", label: "Shot priority", iconEntity: "Chimera Shot", use: "Protect Kill Shot, Chimera Shot, and Aimed Shot cooldowns before filling with Steady Shot." },
    { key: "movement", label: "Movement", iconEntity: "Disengage", use: "Move during instant-shot globals and stop long enough for Auto Shot and Steady Shot." },
    { key: "pet", label: "Pet & utility", iconEntity: "Furious Howl", use: "Keep the wolf alive, control its cooldowns, and use Misdirection, traps, and interrupts as assignments." }
  ],
  talent: {
    points: "7/57/7",
    name: "Fresh-80 Careful Aim raid build",
    summary: "Start with Focused Aim while gear is short on hit, then move only the points your actual character sheet no longer needs.",
    path: "hunter/502-035335131030013233035031051-5000002"
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
      { label: "Boss hit cap", value: '<span class="must">8% / 263 rating</span>', detail: "Subtract 1% for each point in Focused Aim; 3/3 leaves 5% from gear, or 164 rating." },
      { label: "Fresh-80 rule", value: "Agility first", detail: "Cap hit, then build a coherent Agility set. Do not gem Armor Penetration because an endgame list does." },
      { label: "Pet", value: "Wolf • Ferocity", detail: `${entity("Furious Howl")} and ${entity("Call of the Wild")} add real raid damage; a dead or passive pet does not.` },
      { label: "Core glyphs", value: `${item("Glyph of Serpent Sting", "q-rare")} • ${item("Glyph of Steady Shot", "q-rare")}`, detail: `${item("Glyph of Chimera Shot", "q-rare")} is the usual third major when latency permits the shorter cycle.` }
    ],
    engineTitle: "Sting → priority shots → movement weave → pet",
    beforeIcon: "ability_hunter_snipershot",
    firstIcon: "inv_misc_coin_01",
    before: [
      `${entity("Aspect of the Dragonhawk")} active; switch to ${entity("Aspect of the Viper")} only when mana requires it.`,
      `${entity("Trueshot Aura")} covered, ammo stocked, weapon durability checked, and the correct tracking type enabled.`,
      `Wolf summoned, fed, talented, healed, and on the intended passive/defensive setting.`,
      `${entity("Hunter's Mark")} ownership and ${entity("Misdirection")} target agreed before the countdown.`,
      "Hit cap checked against a level-83 target after talents, racial party aura, food, and gear."
    ],
    firstMoves: [
      `Buy or farm a reliable ranged weapon; weapon DPS dominates small secondary-stat debates.`,
      `Reach the correct hit cap without wasting rating above it.`,
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
    priority: `${entity("Kill Shot")} when usable → keep ${entity("Serpent Sting")} active through ${entity("Chimera Shot")} → ${entity("Chimera Shot")} → ${entity("Aimed Shot")} → ${entity("Arcane Shot")} in a fresh/low-Armor-Penetration set → ${entity("Steady Shot")}. Fire ${entity("Silencing Shot")} for damage only when it is not reserved for an interrupt.`,
    openerIcon: "ability_hunter_chimerashot2",
    trackingIcon: "ability_hunter_mastermarksman",
    opener: [
      `Pre-mark with ${entity("Hunter's Mark")} if assigned and set the tank as focus.`,
      `Use ${entity("Misdirection")} during the countdown and pre-pot ${item("Potion of Speed")}.`,
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
          `A progression mechanic can be a better Readiness anchor than the pull.`
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
          `${entity("Call of the Wild")} belongs in the raid's burst plan rather than on an arbitrary trash pull.`
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
      { title: "Marksmanship core", icon: "ability_hunter_chimerashot2", items: [`${entity("Chimera Shot")}, ${entity("Aimed Shot")}, and ${entity("Readiness")} define the cycle.`, `${entity("Trueshot Aura")} covers the physical raid buff when no stronger equivalent is present.`, "Piercing Shots, Wild Quiver, and Improved Steady Shot reward clean weapon uptime."] },
      { title: "Fresh-80 support", icon: "ability_hunter_focusedaim", items: ["3/3 Focused Aim removes 3% from the gear hit requirement.", "Careful Aim converts Intellect into attack power and favors coherent mail upgrades.", "Reallocate Focused Aim only after the character remains capped in the actual boss set."] },
      { title: "Survival branch", icon: "ability_hunter_lockandload", items: ["Improved Tracking rewards selecting the correct creature tracking.", "Survival Instincts improves core shots and survivability.", "This baseline avoids modern talents or Classic-era trap-launcher assumptions."] }
    ],
    extraSection: {
      id: "pet",
      short: "Pet",
      title: "Wolf and Ferocity setup",
      icon: "ability_hunter_pet_wolf",
      body: `<div class="two-col"><div class="guide-box"><h3>${icon("ability_hunter_pet_wolf", "ability-icon")} Recommended raid pet</h3>${list([
        `Wolf for ${entity("Furious Howl")}. Keep it alive, fed, and in range.`,
        `Use a level-80 Ferocity build centered on Cobra Reflexes, Dash, Bloodthirsty, Spiked Collar, Boar's Speed, Culling the Herd, Spider's Bite, Rabid, and ${entity("Call of the Wild")}.`,
        `${entity("Heart of the Phoenix")} is a strong progression recovery point; move only with a deliberate alternate plan.`
      ])}</div><div class="guide-box"><h3>${icon("ability_physical_taunt", "ability-icon")} Control rules</h3>${list([
        `Bind pet attack and pet follow separately. Do not make every ability permanently issue /petattack.`,
        `Keep Growl off for bosses. Leave ${entity("Cower")} off autocast unless pet survival demands it.`,
        `Use ${entity("Mend Pet")} early and pull the pet out of lethal ground effects.`,
        `Save ${entity("Call of the Wild")} for the pull or the raid's chosen burst phase.`
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
      ["Hit", '<span class="must">Cap first: 8%</span>', "Prevents ranged attacks from missing a level-83 raid boss.", "8% is 262.32 rating, so use 263. Each Focused Aim point removes 1%; 3/3 leaves 5%, or 164 rating. A Draenei aura can remove another 1% when actually present."],
      ["Weapon DPS", '<span class="must">Highest upgrade lever</span>', "Scales Auto Shot and weapon-based shots.", "A strong ranged-weapon upgrade can beat a cosmetically perfect secondary-stat item."],
      ["Agility", "Fresh-80 default", "Adds attack power, crit, and scales with raid buffs.", "Gem Agility until a real simulation and sufficiently strong native-ArP set justify changing strategy."],
      ["Armor Penetration", "Powerful only with enough gear", "Raises physical damage by bypassing armor, up to 1,400 rating for 100%.", "Do not treat 1,400 as a fresh-80 target. Common proc soft caps are 722 with Needle-Encrusted Scorpion, 735 with Mjolnir Runestone, and 788 with Grim Toll."],
      ["Critical Strike", "Strong secondary", "Increases direct-shot damage and supports Piercing Shots.", "Crit remains valuable but does not replace hit or weapon DPS."],
      ["Attack Power", "Reliable throughput", "Raises shot, Auto Shot, and pet damage.", "Agility usually offers a stronger fresh-80 package after raid scaling."],
      ["Haste", "Lower priority", "Speeds Auto Shot and Steady Shot.", "Once Steady approaches the one-second global floor with raid effects, extra haste loses much of its filler value."]
    ],
    stages: [
      { title: "Fresh level 80", icon: "inv_misc_coin_01", items: ["Reach the hit cap and secure a credible ranged weapon.", "Gem Agility, not an endgame Armor Penetration target.", "Enchant every piece expected to survive more than a few runs."] },
      { title: "Raid-ready base", icon: "achievement_boss_general_nazgrim", items: ["Maintain 100% Serpent Sting through Chimera Shot.", "Keep the wolf alive and active for a full heroic or target-dummy session.", "Carry ammo, pet food, flasks, food, and speed potions."] },
      { title: "ArP transition", icon: "inv_misc_gear_01", items: ["Acquire strong native Armor Penetration gear first.", "Model the exact set, buffs, trinket proc, and latency before regemming.", "Keep the Agility gems if the tested gain is small or the set changes frequently."] }
    ],
    gems: [
      ["Meta", item("Relentless Earthsiege Diamond", "q-rare"), "None for raid damage", `Activate efficiently with one ${item("Nightmare Tear")}.`],
      ["Red", item("Delicate Cardinal Ruby"), item("Fractured Cardinal Ruby"), "Agility by default; Fractured only after a validated Armor Penetration transition."],
      ["Yellow", item("Deadly Ametrine"), item("Rigid King's Amber"), "Match strong Agility/crit bonuses or use hit only until capped."],
      ["Blue", item("Nightmare Tear"), "Delicate Cardinal Ruby in a red-equivalent socket", "Use one Tear to activate the meta; ignore weak blue bonuses."],
      ["Profession", "Delicate Dragon's Eye", "Fractured Dragon's Eye", "Keep the same Agility-versus-ArP logic as ordinary gems."]
    ],
    enchants: [
      ["Head", item("Arcanum of Torment"), "Knights of the Ebon Blade revered in standard Wrath."],
      ["Shoulders", item("Greater Inscription of the Axe"), "Sons of Hodir exalted; use the lower inscription while progressing reputation."],
      ["Back", entity("Enchant Cloak - Major Agility", "enchant-name"), "Flexweave Underlay is a practical Engineering alternative."],
      ["Chest", entity("Enchant Chest - Powerful Stats", "enchant-name"), "Use a cheaper stats enchant on a temporary chest."],
      ["Wrists", entity("Enchant Bracers - Greater Assault", "enchant-name"), "Attack power is the standard damage option."],
      ["Hands", entity("Enchant Gloves - Crusher", "enchant-name"), "Hyperspeed Accelerators for Engineering."],
      ["Waist", item("Eternal Belt Buckle", "q-rare"), "Always add the extra socket to a lasting belt."],
      ["Legs", item("Icescale Leg Armor"), "Premium attack power and crit leg enchant."],
      ["Feet", entity("Enchant Boots - Tuskarr's Vitality", "enchant-name"), `${entity("Enchant Boots - Icewalker", "enchant-name")} only when the hit is genuinely needed.`],
      ["Two-handed weapon", entity("Enchant 2H Weapon - Massacre", "enchant-name"), "Scourgebane is only a narrow undead alternative."],
      ["Ranged weapon", item("Heartseeker Scope"), "Use the best available scope on a weapon that will last."]
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
      ["Filled 7/57/7 talent calculator", "https://www.wowhead.com/wotlk/talent-calc/hunter/502-035335131030013233035031051-5000002"],
      ["Wolf pet family record", "https://www.wowhead.com/wotlk/pet=1/wolf"]
    ],
    building: [
      ["Marksmanship Hunter stat priority", "https://www.wowhead.com/wotlk/guide/classes/hunter/marksmanship/dps-stat-priority-attributes-pve"],
      ["Marksmanship Hunter enchants and consumables", "https://www.wowhead.com/wotlk/guide/classes/hunter/marksmanship/dps-enchants-consumables-pve"]
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

const specs = [holyPriest, shadowPriest, marksmanshipHunter];
const renderers = {
  quickStart: renderQuickStart,
  playing: renderPlaying,
  setup: renderSetup,
  building: renderBuilding,
  equipping: renderEquipping,
  raiding: renderRaiding
};

for (const spec of specs) {
  for (const [pageKey, , fileSuffix] of pageOrder) {
    const destination = path.join(root, "guides", `${spec.slug}-${fileSuffix}.html`);
    fs.writeFileSync(destination, renderers[pageKey](spec), "utf8");
  }
}

console.log(`Rendered ${specs.length * pageOrder.length} complete fresh-80 guide pages.`);
