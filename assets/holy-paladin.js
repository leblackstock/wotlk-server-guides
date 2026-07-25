(function () {
  "use strict";

  const ICON_BASE = "https://wow.zamimg.com/images/wow/icons/large/";

  const icons = {
    "beacon of light": "ability_paladin_beaconoflight",
    "sacred shield": "ability_paladin_blessedmending",
    "holy light": "spell_holy_holybolt",
    "flash of light": "spell_holy_flashheal",
    "holy shock": "spell_holy_searinglight",
    "divine plea": "spell_holy_aspiration",
    "judgements of the pure": "ability_paladin_judgementofthepure",
    "seal of wisdom": "spell_holy_sealofwisdom",
    "divine favor": "spell_holy_heal",
    "divine illumination": "spell_holy_divineillumination",
    "aura mastery": "spell_holy_auramastery",
    "divine sacrifice": "spell_holy_powerwordbarrier",
    "divine guardian": "spell_holy_powerwordbarrier",
    "hand of sacrifice": "spell_holy_sealofsacrifice",
    "hand of protection": "spell_holy_sealofprotection",
    "hand of salvation": "spell_holy_sealofsalvation",
    "hand of freedom": "spell_holy_sealofvalor",
    "lay on hands": "spell_holy_layonhands",
    "cleanse": "spell_holy_renew",
    "divine protection": "spell_holy_restoration",
    "divine shield": "spell_holy_divineshield",
    "righteous fury": "spell_holy_sealoffury",
    "devotion aura": "spell_holy_devotionaura",
    "concentration aura": "spell_holy_mindsooth",
    "infusion of light": "ability_paladin_infusionoflight",
    "divine intellect": "spell_nature_sleep",
    "holy guidance": "spell_holy_holyguidance",
    "illumination": "spell_holy_greaterheal",
    "light's grace": "spell_holy_lightsgrace",
    "improved devotion aura": "spell_holy_devotionaura",
    "improved righteous fury": "spell_holy_sealoffury",
    "blessed hands": "ability_paladin_blessedhands",
    "improved lay on hands": "spell_holy_layonhands",
    "improved concentration aura": "spell_holy_mindsooth",
    "improved blessing of wisdom": "spell_holy_sealofwisdom",
    "intellect": "spell_nature_sleep",
    "haste": "spell_nature_invisibilty",
    "mp5": "spell_nature_manaregentotem",
    "spell power": "spell_holy_greaterheal",
    "critical strike": "spell_holy_holybolt",
    "stamina": "spell_holy_wordfortitude",
    "spirit": "spell_holy_divinespirit",
    "engineering": "trade_engineering",
    "jewelcrafting": "inv_misc_gem_01",
    "alchemy": "trade_alchemy",
    "blacksmithing": "trade_blacksmithing",
    "tailoring": "trade_tailoring",
    "leatherworking": "trade_leatherworking",
    "inscription / enchanting": "inv_inscription_tradeskill01",
    "mining / herbalism / skinning": "trade_mining"
  };

  const sectionIcons = {
    "quick start": "spell_holy_holybolt",
    "continue the holy paladin guide": "ability_paladin_beaconoflight",
    "the holy paladin healing engine": "ability_paladin_beaconoflight",
    "healing playbooks": "spell_holy_holybolt",
    "cooldowns, hands, and utility": "spell_holy_sealofsacrifice",
    "talents": "spell_holy_holyguidance",
    "glyphs": "inv_glyph_majorpaladin",
    "macros": "inv_misc_note_01",
    "addons and interface": "inv_misc_wrench_01",
    "stats, breakpoints, and tradeoffs": "spell_holy_divineillumination",
    "level-80 gearing path": "inv_chest_plate_03",
    "gems": "inv_jewelcrafting_gem_01",
    "enchants": "spell_holy_greaterheal",
    "professions": "trade_engineering",
    "consumables": "inv_alchemy_endlessflask_05",
    "assignments and cooldown planning": "ability_paladin_beaconoflight",
    "raid encounters": "achievement_boss_lichking",
    "specific raid encounter notes": "achievement_boss_lichking",
    "sources and verification": "inv_misc_book_09"
  };

  const headingIcons = {
    "playing": "spell_holy_holybolt",
    "setup": "spell_holy_devotionaura",
    "building": "spell_holy_divineillumination",
    "equipping": "inv_shield_06",
    "raiding": "spell_holy_powerwordbarrier",
    "before the pull": "ability_paladin_beaconoflight",
    "first gearing rule": "spell_nature_sleep",
    "maintain": "ability_paladin_blessedmending",
    "direct heal": "spell_holy_holybolt",
    "transfer": "ability_paladin_beaconoflight",
    "recover": "spell_holy_aspiration",
    "direct-heal target": "spell_holy_holybolt",
    "beacon target": "ability_paladin_beaconoflight",
    "always maintain": "ability_paladin_blessedmending",
    "choose the cast": "spell_holy_holybolt",
    "plan the mana": "spell_holy_aspiration",
    "routine tank damage": "spell_holy_holybolt",
    "two tanks taking damage": "ability_paladin_beaconoflight",
    "sudden tank spike": "spell_holy_searinglight",
    "heavy raid-wide damage": "spell_holy_holybolt",
    "movement phase": "spell_holy_searinglight",
    "mana trouble": "spell_holy_aspiration",
    "standard 51/20/0 reference": "spell_holy_holyguidance",
    "core holy talents": "ability_paladin_beaconoflight",
    "protection subspec": "spell_holy_powerwordbarrier",
    "flexible points": "ability_paladin_blessedhands",
    "mouseover heal": "spell_holy_holybolt",
    "beacon assignment": "ability_paladin_beaconoflight",
    "sacred shield assignment": "ability_paladin_blessedmending",
    "divine guardian cancel": "spell_holy_powerwordbarrier",
    "emergency self protection": "spell_holy_restoration",
    "aura mastery reminder": "spell_holy_auramastery",
    "cancel divine shield": "spell_holy_divineshield",
    "essential": "inv_misc_wrench_01",
    "recommended": "spell_holy_devotionaura",
    "recommended two-button healbot layout": "spell_holy_flashheal",
    "fresh level 80": "spell_holy_holybolt",
    "raid-ready base set": "spell_holy_devotionaura",
    "encounter-tuned sets": "spell_holy_powerwordbarrier",
    "physical damage": "inv_shield_06",
    "stamina and mixed damage": "spell_holy_wordfortitude",
    "magic burst": "spell_holy_powerwordbarrier",
    "mana and sustain": "spell_holy_aspiration",
    "throughput": "spell_holy_holybolt",
    "do not vendor yet": "inv_box_01"
  };

  const encounterIcons = {
    "lord marrowgar": "achievement_boss_lordmarrowgar",
    "lady deathwhisper": "achievement_boss_ladydeathwhisper",
    "gunship battle": "achievement_boss_gunshipbattle",
    "deathbringer saurfang": "achievement_boss_saurfang",
    "festergut": "achievement_boss_festergutrotface",
    "rotface": "achievement_boss_festergutrotface",
    "professor putricide": "achievement_boss_profputricide",
    "blood prince council": "achievement_boss_princetaldaram",
    "blood-queen lana'thel": "achievement_boss_bloodqueen_lanathel",
    "valithria dreamwalker": "achievement_boss_valithriadreamwalker",
    "sindragosa": "achievement_boss_sindragosa",
    "the lich king": "achievement_boss_lichking",
    "anub'arak": "achievement_boss_anubarak",
    "halion": "achievement_boss_halion"
  };

  function normalize(value) {
    return String(value || "").replace(/\s+/g, " ").trim().toLowerCase();
  }

  function makeIcon(icon, className) {
    const image = document.createElement("img");
    image.className = className;
    image.src = ICON_BASE + icon + ".jpg";
    image.alt = "";
    image.setAttribute("aria-hidden", "true");
    image.addEventListener("error", function () { image.remove(); }, {once:true});
    image.dataset.holyGuideIcon = "true";
    return image;
  }

  function spellIconFor(text) {
    const key = normalize(text).replace(/^glyph of /, "");
    if (icons[key]) return icons[key];
    if (key.includes("beacon")) return icons["beacon of light"];
    if (key.includes("sacred shield") || key.includes("maintain buff")) return icons["sacred shield"];
    if (key.includes("holy light") || key.includes("heal tank")) return icons["holy light"];
    if (key.includes("flash of light")) return icons["flash of light"];
    if (key.includes("holy shock")) return icons["holy shock"];
    if (key.includes("infusion")) return icons["infusion of light"];
    if (key.includes("divine plea") || key.includes("mana")) return icons["divine plea"];
    if (key.includes("aura mastery")) return icons["aura mastery"];
    if (key.includes("hand of sacrifice")) return icons["hand of sacrifice"];
    if (key.includes("hand of protection")) return icons["hand of protection"];
    if (key.includes("hand of salvation")) return icons["hand of salvation"];
    if (key.includes("hand of freedom")) return icons["hand of freedom"];
    if (key.includes("lay on hands")) return icons["lay on hands"];
    if (key.includes("cleanse")) return icons.cleanse;
    if (key.includes("divine favor")) return icons["divine favor"];
    if (key.includes("divine illumination")) return icons["divine illumination"];
    if (key.includes("divine guardian") || key.includes("divine sacrifice")) return icons["divine guardian"];
    if (key.includes("divine protection")) return icons["divine protection"];
    if (key.includes("divine shield")) return icons["divine shield"];
    if (key.includes("seal of wisdom")) return icons["seal of wisdom"];
    if (key.startsWith("glyph of ") || normalize(text).startsWith("glyph of ")) return "inv_glyph_majorpaladin";
    return null;
  }

  function addHeadingIcon(element, icon, className) {
    if (!element || !icon || element.dataset.holyIconized === "true") return;
    const marker = element.querySelector(":scope > .section-mark");
    if (marker) marker.remove();
    element.classList.add("icon-heading", "holy-icon-heading");
    element.style.display = "flex";
    element.style.alignItems = "center";
    element.style.gap = "8px";
    element.prepend(makeIcon(icon, className || "title-icon"));
    element.dataset.holyIconized = "true";
  }

  function wrapCellWithIcon(cell, icon) {
    if (!cell || !icon || cell.dataset.holyIconized === "true") return;
    const wrapper = document.createElement("span");
    wrapper.className = "icon-item";
    while (cell.firstChild) wrapper.appendChild(cell.firstChild);
    wrapper.prepend(makeIcon(icon, "item-icon"));
    cell.appendChild(wrapper);
    cell.dataset.holyIconized = "true";
  }

  function decorateSections() {
    document.querySelectorAll("main .common > h2").forEach(function (heading) {
      const key = normalize(heading.textContent);
      let icon = sectionIcons[key];
      if (!icon && key.includes("fresh") && key.includes("80")) icon = "spell_holy_holybolt";
      if (!icon && (key.includes("emblem") || key.includes("frost"))) icon = "spell_frost_frostarmor02";
      if (!icon && key.includes("assignment")) icon = "ability_paladin_beaconoflight";
      if (!icon && (key.includes("raid") || key.includes("encounter"))) icon = "achievement_boss_lichking";
      if (!icon && key.includes("trinket")) icon = "inv_jewelry_talisman_07";
      if (!icon && key.includes("libram")) icon = "inv_relics_libramofhope";
      if (!icon && key.includes("gear")) icon = "inv_chest_plate_03";
      addHeadingIcon(heading, icon, "spell-icon");
    });
  }

  function decorateCards() {
    document.querySelectorAll(".chapter-card h3, .priority-card > h3, .guide-box > h3, .macro-card > h3, .heal-card-header h3, main > h3").forEach(function (heading) {
      const key = normalize(heading.textContent);
      addHeadingIcon(heading, headingIcons[key] || spellIconFor(key), "title-icon");
    });

    document.querySelectorAll(".engine-step strong, .beacon-node strong").forEach(function (heading) {
      addHeadingIcon(heading, headingIcons[normalize(heading.textContent)], "ability-icon");
    });
  }

  function decorateSummaryCards() {
    const labelIcons = {
      "core assignment": "ability_paladin_beaconoflight",
      "default healing spell": "spell_holy_holybolt",
      "default major glyphs": "inv_glyph_majorpaladin",
      "healing engine": "ability_paladin_beaconoflight"
    };
    document.querySelectorAll(".summary-card").forEach(function (card) {
      const label = card.querySelector(".summary-label");
      const value = card.querySelector(".summary-value");
      addHeadingIcon(value, labelIcons[normalize(label && label.textContent)], "title-icon");
    });
  }

  function decorateSpellChoices() {
    document.querySelectorAll(".spell-choice").forEach(function (choice) {
      const icon = spellIconFor(choice.textContent);
      if (!icon || choice.dataset.holyIconized === "true") return;
      choice.prepend(makeIcon(icon, "ability-icon"));
      choice.dataset.holyIconized = "true";
    });
  }

  function decorateTables() {
    document.querySelectorAll(".table-wrap tbody tr").forEach(function (row) {
      const cell = row.cells && row.cells[0];
      if (!cell) return;
      const text = normalize(cell.textContent);
      const icon = spellIconFor(text) || icons[text];
      if (icon) wrapCellWithIcon(cell, icon);
    });
  }

  function decorateSpecialSummaries() {
    document.querySelectorAll(".server-behavior > summary").forEach(function (summary) {
      addHeadingIcon(summary, "inv_misc_wrench_01", "ability-icon");
    });

    document.querySelectorAll(".raid-encounter > summary").forEach(function (summary) {
      const title = summary.querySelector(".raid-summary-title") || summary;
      const key = normalize(title.textContent);
      const icon = encounterIcons[key] || "achievement_boss_lichking";
      if (summary.dataset.holyIconized === "true") return;
      summary.classList.add("icon-heading", "holy-summary-icon-row");
      summary.style.display = "flex";
      summary.style.alignItems = "center";
      summary.style.gap = "8px";
      summary.prepend(makeIcon(icon, "ability-icon"));
      summary.dataset.holyIconized = "true";
    });
  }

  function decorateIcons() {
    decorateSections();
    decorateCards();
    decorateSummaryCards();
    decorateSpellChoices();
    decorateTables();
    decorateSpecialSummaries();
  }

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

  function init() {
    decorateIcons();
    bindFilters();
    bindPlaybookFocus();
  }

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", init, {once:true}); else init();
}());
