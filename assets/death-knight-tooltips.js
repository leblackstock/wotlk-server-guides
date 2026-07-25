/*
 * Shared WotLK Death Knight tooltip linker.
 * Each entry maps an exact Wrath name (plus deliberate aliases) to Wowhead.
 */
(function () {
  "use strict";

  const items = [
    [41380, "Austere Earthsiege Diamond"],
    [40119, "Solid Majestic Zircon"],
    [36767, "Solid Dragon's Eye", "Solid Dragon’s Eye"],
    [40141, "Guardian's Dreadstone", "Guardian’s Dreadstone"],
    [49110, "Nightmare Tear"],
    [40166, "Vivid Eye of Zul"],
    [40167, "Enduring Eye of Zul"],

    [44150, "Arcanum of the Stalwart Protector"],
    [44957, "Greater Inscription of the Gladiator"],
    [44136, "Greater Inscription of the Pinnacle"],
    [34207, "Glove Reinforcements"],
    [41611, "Eternal Belt Buckle"],
    [38373, "Frosthide Leg Armor"],
    [41118, "Nitro Boosts"],
    [49426, "Emblem of Frost", "Emblems of Frost", "Frost emblem", "Frost emblems", "Frost-emblem"],
    [47241, "Emblem of Triumph", "Emblems of Triumph", "Triumph emblem", "Triumph emblems"],
    [47556, "Crusader Orb", "Crusader Orbs"],
    [49908, "Primordial Saronite"],
    [52025, "Normal Vanquisher's Mark of Sanctification", "Normal Vanquisher’s Mark of Sanctification"],
    [52028, "Heroic Vanquisher's Mark of Sanctification", "Heroic Vanquisher’s Mark of Sanctification"],

    [45805, "Glyph of Disease"],
    [43554, "Glyph of Vampiric Blood"],
    [43538, "Glyph of Dark Command"],
    [43550, "Glyph of Rune Strike"],
    [43827, "Glyph of Death Strike"],
    [43542, "Glyph of Death and Decay"],
    [43545, "Glyph of Icebound Fortitude"],
    [43535, "Glyph of Blood Tap"],
    [43672, "Glyph of Pestilence"],
    [43673, "Glyph of Raise Dead"],
    [43544, "Glyph of Horn of Winter"],

    [47216, "The Black Heart"],
    [50356, "Corroded Skeleton Key"],
    [44188, "Cloak of Peaceful Resolutions"],
    [36993, "Seal of the Pantheon"],
    [47571, "Saronite Swordbreakers"],
    [45551, "Indestructible Plate Girdle"],
    [49907, "Boots of Kingly Upheaval"],
    [49904, "Pillars of Might"],
    [47735, "Glyph of Indomitability"],
    [47731, "Clutch of Fortification"],
    [47882, "Eitrigg's Oath", "Eitrigg’s Oath"],
    [50991, "Verdigris Chain Belt"],
    [50978, "Gauntlets of the Kraken"],
    [50968, "Cataclysmic Chestguard"],
    [51133, "Sanctified Scourgelord Faceguard"],
    [51134, "Sanctified Scourgelord Chestguard"],
    [51132, "Sanctified Scourgelord Handguards"],
    [51131, "Sanctified Scourgelord Legguards"],
    [51130, "Sanctified Scourgelord Pauldrons"],
    [50855, "Scourgelord Faceguard"],
    [50798, "Ramaladni's Blade of Culling", "Ramaladni’s Blade of Culling"],
    [49919, "Cryptmaker"],
    [50070, "Glorenzelg, High-Blade of the Silver Hand"],
    [50425, "Oathbinder, Charge of the Ranger-General"],
    [49623, "Shadowmourne"],
    [49986, "Broken Ram Skull Helm"],
    [50660, "Boneguard Commander's Pauldrons", "Boneguard Commander’s Pauldrons"],
    [50074, "Royal Crimson Cloak"],
    [49960, "Bracers of Dark Reckoning"],
    [50036, "Belt of Broken Bones"],
    [51787, "Scourge Fanged Stompers"],
    [50023, "Bile-Encrusted Medallion"],
    [50185, "Devium's Eternally Cold Ring", "Devium’s Eternally Cold Ring"],
    [50404, "Ashen Band of Endless Courage"],
    [54564, "Scion's Treads", "Scion’s Treads"],
    [50361, "Sindragosa's Flawless Fang", "Sindragosa’s Flawless Fang"],
    [50341, "Unidentifiable Organ"],
    [54571, "Petrified Twilight Scale"],

    [46379, "Flask of Stoneblood"],
    [42999, "Blackened Dragonfin"],
    [43000, "Dragonfin Filet"],
    [42994, "Rhinolicious Wormsteak"],
    [42996, "Snapper Extreme"],
    [43015, "Fish Feast"],
    [40093, "Indestructible Potion"],
    [40217, "Mighty Shadow Protection Potion"],
    [33447, "Runic Healing Potion"],
    [36892, "Fel Healthstone", "Healthstone"],
    [34722, "Heavy Frostweave Bandage"],
    [41119, "Saronite Bomb", "Saronite Bombs"],
    [42641, "Global Thermal Sapper Charge"],
    [5634, "Free Action Potion"],
    [2459, "Swiftness Potion"],
    [43237, "Anesthetic Poison II"]
  ];

  const spells = [
    [48263, "Frost Presence"],
    [48266, "Blood Presence"],
    [62158, "Rune of the Stoneskin Gargoyle", "Stoneskin Gargoyle"],
    [53323, "Rune of Swordshattering", "Swordshattering"],
    [53342, "Rune of Spellshattering", "Spellshattering"],
    [49909, "Icy Touch"],
    [49921, "Plague Strike"],
    [49998, "Death Strike"],
    [49930, "Blood Strike"],
    [50842, "Pestilence"],
    [49941, "Blood Boil"],
    [49938, "Death and Decay"],
    [56815, "Rune Strike"],
    [49895, "Death Coil"],
    [56222, "Dark Command"],
    [49576, "Death Grip"],
    [45524, "Chains of Ice"],
    [47528, "Mind Freeze"],
    [47476, "Strangulate"],
    [57623, "Horn of Winter"],
    [47568, "Empower Rune Weapon", "ERW"],
    [45529, "Blood Tap"],
    [48792, "Icebound Fortitude", "IBF"],
    [48707, "Anti-Magic Shell", "AMS"],
    [48982, "Rune Tap"],
    [55233, "Vampiric Blood", "VB"],
    [46584, "Raise Dead"],
    [48743, "Death Pact"],
    [42650, "Army of the Dead"],
    [59921, "Frost Fever"],
    [59879, "Blood Plague"],
    [69127, "Chill of the Throne"],

    [55226, "Blade Barrier"],
    [49393, "Bladed Armor"],
    [49004, "Scent of Blood"],
    [55108, "Two-Handed Weapon Specialization"],
    [49005, "Mark of Blood"],
    [49480, "Dark Conviction"],
    [50034, "Death Rune Mastery"],
    [49489, "Improved Rune Tap"],
    [49497, "Spell Deflection"],
    [50029, "Veteran of the Third War"],
    [49504, "Bloody Vengeance"],
    [49543, "Bloodworms"],
    [53138, "Abomination's Might", "Abomination’s Might"],
    [49016, "Hysteria", "Unholy Frenzy"],
    [62908, "Improved Death Strike"],
    [50150, "Will of the Necropolis"],
    [51456, "Improved Icy Touch"],
    [49789, "Toughness"],
    [49664, "Black Ice"],
    [50887, "Icy Talons"],
    [49657, "Endless Winter"],
    [51109, "Frigid Dreadplate"],
    [55133, "Anticipation"],
    [55262, "Heart Strike"],
    [50371, "Improved Blood Presence"],
    [49534, "Might of Mograine"],
    [61158, "Blood Gorged"],
    [49028, "Dancing Rune Weapon"],
    [49039, "Lichborne"],
    [55610, "Improved Icy Talons"],
    [49565, "Morbidity"],
    [49222, "Bone Shield"],
    [51052, "Anti-Magic Zone", "AMZ"],
    [49568, "Virulence"],

    [47672, "Enchant Cloak - Mighty Armor", "Mighty Armor"],
    [60663, "Enchant Cloak - Major Agility", "Major Agility"],
    [44591, "Enchant Cloak - Titanweave", "Titanweave"],
    [47900, "Enchant Chest - Super Health", "Super Health"],
    [60692, "Enchant Chest - Powerful Stats", "Powerful Stats"],
    [47766, "Enchant Chest - Greater Defense", "Greater Defense"],
    [62256, "Enchant Bracers - Major Stamina", "Major Stamina"],
    [57690, "Fur Lining - Stamina"],
    [63770, "Reticulated Armor Webbing"],
    [44625, "Enchant Gloves - Armsman", "Armsman"],
    [44488, "Enchant Gloves - Precision", "Precision"],
    [44484, "Enchant Gloves - Expertise"],
    [47901, "Enchant Boots - Tuskarr's Vitality", "Enchant Boots - Tuskarr’s Vitality", "Tuskarr's Vitality", "Tuskarr’s Vitality"],
    [44528, "Enchant Boots - Greater Fortitude", "Greater Fortitude"],
    [67839, "Mind Amplification Dish"],
    [59636, "Enchant Ring - Stamina"],
    [61119, "Master's Inscription of the Pinnacle", "Master’s Inscription of the Pinnacle"],
    [55628, "Socket Bracer"],
    [55641, "Socket Gloves"],
    [53042, "Mixology"],
    [53040, "Toughness (Mining)"],
    [55503, "Lifeblood"],
    [53666, "Master of Anatomy"],
    [19801, "Tranquilizing Shot"],

    [69409, "Soul Reaper"],
    [74074, "Plague Siphon"],
    [73529, "Shadow Trap"],
    [73539, "Summon Shadow Trap"],
    [70541, "Infest"],
    [70337, "Necrotic Plague"],
    [72149, "Shockwave"],
    [72143, "Enrage"],
    [28747, "Frenzy"],
    [72259, "Remorseless Winter"],
    [72133, "Pain and Suffering"],
    [69103, "Summon Ice Sphere", "Ice Sphere"],
    [69099, "Ice Pulse"],
    [69108, "Ice Burst"],
    [69201, "Raging Spirit", "Raging Spirits"],
    [69242, "Soul Shriek"],
    [72262, "Quake"],
    [72762, "Defile"],
    [73654, "Harvest Souls"],
    [70498, "Vile Spirits"],
    [70503, "Spirit Burst"],
    [73028, "Harvested Soul"],
    [72350, "Fury of Frostmourne"]
  ];

  const skills = [
    [776, "Runeforging"],
    [202, "Engineering"],
    [755, "Jewelcrafting"],
    [165, "Leatherworking"],
    [164, "Blacksmithing"],
    [333, "Enchanting"],
    [186, "Mining"],
    [171, "Alchemy"],
    [773, "Inscription"],
    [182, "Herbalism"],
    [393, "Skinning"]
  ];

  const entities = new Map();
  const phrases = [];
  const normalize = function (value) {
    return value.trim().toLowerCase().replace(/[’]/g, "'").replace(/\s+/g, " ");
  };

  function register(type, row) {
    const entity = { type: type, id: row[0] };
    row.slice(1).forEach(function (name) {
      entities.set(normalize(name), entity);
      phrases.push(name);
    });
  }

  items.forEach(function (row) { register("item", row); });
  spells.forEach(function (row) { register("spell", row); });
  skills.forEach(function (row) { register("skill", row); });

  function wowheadUrl(entity) {
    return "https://www.wowhead.com/wotlk/" + entity.type + "=" + entity.id;
  }

  function tooltipValue(entity) {
    return entity.type + "=" + entity.id + "&domain=wotlk";
  }

  function decorateAnchor(anchor, entity) {
    anchor.classList.add("wowhead-link");
    anchor.setAttribute("data-wowhead", tooltipValue(entity));
  }

  function makeAnchor(text, entity) {
    const anchor = document.createElement("a");
    anchor.href = wowheadUrl(entity);
    anchor.target = "_blank";
    anchor.rel = "noopener";
    anchor.textContent = text;
    decorateAnchor(anchor, entity);
    return anchor;
  }

  function entityFromWowheadHref(href) {
    const match = href.match(/\/wotlk\/(item|spell|skill)=(\d+)/i);
    return match ? { type: match[1].toLowerCase(), id: Number(match[2]) } : null;
  }

  function decorateExistingWowheadAnchors() {
    document.querySelectorAll('a[href*="wowhead.com/wotlk/"]').forEach(function (anchor) {
      const entity = entityFromWowheadHref(anchor.href);
      if (entity) decorateAnchor(anchor, entity);
    });
  }

  function decorateNamedEntities() {
    const selector = ".item-name, .spell-name, .talent-name, .glyph-name, .recipe-name, .enchant-name, .skill-name";
    document.querySelectorAll(selector).forEach(function (node) {
      if (node.closest("a[data-wowhead], code, button")) return;
      const entity = entities.get(normalize(node.textContent));
      if (!entity) return;
      if (node.tagName === "A") {
        node.href = wowheadUrl(entity);
        node.target = "_blank";
        node.rel = "noopener";
        decorateAnchor(node, entity);
        return;
      }
      const anchor = makeAnchor(node.textContent.trim(), entity);
      anchor.className += (anchor.className ? " " : "") + node.className;
      anchor.innerHTML = node.innerHTML;
      node.replaceWith(anchor);
    });
  }

  function escapeRegExp(value) {
    return value.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
  }

  function linkPhrases() {
    const ordered = Array.from(new Set(phrases)).sort(function (a, b) {
      return b.length - a.length;
    });
    const matcher = new RegExp(
      "(^|[^A-Za-z0-9'])((?:" + ordered.map(escapeRegExp).join("|") + "))(?=$|[^A-Za-z0-9'])",
      "gi"
    );
    const root = document.querySelector("main") || document.body;
    const walker = document.createTreeWalker(root, NodeFilter.SHOW_TEXT);
    const candidates = [];
    let textNode;

    while ((textNode = walker.nextNode())) {
      const parent = textNode.parentElement;
      if (!parent || !textNode.nodeValue.trim()) continue;
      if (parent.closest("a, code, pre, script, style, textarea, button, iframe, nav, .no-wowhead")) continue;
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
        if (start > cursor) {
          fragment.appendChild(document.createTextNode(node.nodeValue.slice(cursor, start)));
        }
        fragment.appendChild(makeAnchor(phrase, entities.get(normalize(phrase))));
        cursor = start + phrase.length;
      }
      if (cursor < node.nodeValue.length) {
        fragment.appendChild(document.createTextNode(node.nodeValue.slice(cursor)));
      }
      node.parentNode.replaceChild(fragment, node);
    });
  }

  function loadWowheadTooltips() {
    if (document.querySelector("script[data-death-knight-wowhead]")) return;
    window.whTooltips = { colorLinks: false, iconizeLinks: false, renameLinks: false };
    const script = document.createElement("script");
    script.src = "https://wow.zamimg.com/js/tooltips.js";
    script.async = true;
    script.dataset.deathKnightWowhead = "true";
    document.head.appendChild(script);
  }

  function init() {
    decorateExistingWowheadAnchors();
    decorateNamedEntities();
    linkPhrases();
    loadWowheadTooltips();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init, { once: true });
  } else {
    init();
  }
}());
