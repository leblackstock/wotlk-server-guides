/*
 * Tankadin WotLK tooltip prototype.
 *
 * Every entry is deliberately keyed to one Wrath item or spell ID. Generic
 * labels without a single correct entity (for example, "Healthstone" or an
 * entire armor set family) remain plain text rather than showing a misleading
 * tooltip.
 */
(function () {
  "use strict";

  const items = [
    [41380, "Austere Earthsiege Diamond"],
    [40119, "Solid Majestic Zircon"],
    [36767, "Solid Dragon's Eye"],
    [40167, "Enduring Eye of Zul"],
    [40166, "Vivid Eye of Zul"],
    [40130, "Shifting Dreadstone"],
    [40141, "Guardian's Dreadstone"],
    [40129, "Sovereign Dreadstone"],
    [44150, "Arcanum of the Stalwart Protector"],
    [44957, "Greater Inscription of the Gladiator"],
    [44136, "Greater Inscription of the Pinnacle"],
    [34207, "Glove Reinforcements"],
    [41611, "Eternal Belt Buckle"],
    [38373, "Frosthide Leg Armor"],
    [41118, "Nitro Boosts"],
    [44936, "Titanium Plating"],
    [47664, "Libram of Defiance"],
    [50461, "Libram of the Eternal Tower"],
    [47216, "The Black Heart"],
    [47735, "Glyph of Indomitability"],
    [47731, "Clutch of Fortification"],
    [50311, "Second Helm of the Executioner"],
    [45821, "Shard of the Crystal Forest"],
    [48656, "Liadrin's Shoulderguards of Conquest"],
    [49832, "Eerie Runeblade Polisher"],
    [50285, "Icebound Bronze Cuirass"],
    [40734, "Bracers of Dalaran's Parapets"],
    [48653, "Liadrin's Handguards of Conquest"],
    [45825, "Shieldwarder Girdle"],
    [48655, "Liadrin's Legguards of Conquest"],
    [50207, "Black Spire Sabatons"],
    [47243, "Mark of the Relentless"],
    [50268, "Rimefang's Claw"],
    [49835, "Splintered Door of the Citadel"],
    [50466, "Sentinel's Winter Cloak"],
    [50991, "Verdigris Chain Belt"],
    [50356, "Corroded Skeleton Key"],
    [50404, "Ashen Band of Endless Courage"],
    [49904, "Pillars of Might"],
    [50968, "Cataclysmic Chestguard"],
    [50760, "Bonebreaker Scepter"],
    [50794, "Neverending Winter"],
    [50341, "Unidentifiable Organ"],
    [50361, "Sindragosa's Flawless Fang"],
    [54571, "Petrified Twilight Scale"],
    [46379, "Flask of Stoneblood"],
    [42999, "Blackened Dragonfin"],
    [43000, "Dragonfin Filet"],
    [43015, "Fish Feast"],
    [42996, "Snapper Extreme"],
    [42994, "Rhinolicious Wormsteak"],
    [40093, "Indestructible Potion"],
    [40211, "Potion of Speed"],
    [44325, "Elixir of Accuracy"],
    [44329, "Elixir of Expertise"],
    [33447, "Runic Healing Potion"],
    [45745, "Glyph of Divine Plea"],
    [43869, "Glyph of Seal of Vengeance"],
    [41100, "Glyph of Righteous Defense"],
    [45747, "Glyph of Salvation"],
    [41092, "Glyph of Judgement"],
    [45742, "Glyph of Hammer of the Righteous"],
    [41101, "Glyph of Avenger's Shield"],
    [43368, "Glyph of Sense Undead"],
    [43367, "Glyph of Lay on Hands"],
    [43365, "Glyph of Blessing of Kings"],
    [43369, "Glyph of the Wise"]
  ];

  const spells = [
    [48952, "Holy Shield"],
    [48819, "Consecration"],
    [53595, "Hammer of the Righteous"],
    [61411, "Shield of Righteousness"],
    [25780, "Righteous Fury"],
    [54428, "Divine Plea"],
    [53601, "Sacred Shield"],
    [48827, "Avenger's Shield"],
    [62124, "Hand of Reckoning"],
    [31789, "Righteous Defense"],
    [498, "Divine Protection"],
    [642, "Divine Shield"],
    [64205, "Divine Sacrifice"],
    [1038, "Hand of Salvation"],
    [10278, "Hand of Protection"],
    [6940, "Hand of Sacrifice"],
    [1044, "Hand of Freedom"],
    [48788, "Lay on Hands"],
    [31884, "Avenging Wrath"],
    [4987, "Cleanse"],
    [48806, "Hammer of Wrath"],
    [48801, "Exorcism"],
    [48817, "Holy Wrath"],
    [31801, "Seal of Vengeance"],
    [53736, "Seal of Corruption"],
    [20375, "Seal of Command"],
    [20166, "Seal of Wisdom"],
    [20165, "Seal of Light"],
    [53408, "Judgement of Wisdom"],
    [20271, "Judgement of Light"],
    [53407, "Judgement of Justice"],
    [20911, "Blessing of Sanctuary", "Sanctuary"],
    [25899, "Greater Blessing of Sanctuary"],
    [48942, "Devotion Aura"],
    [48945, "Frost Resistance Aura"],
    [48943, "Shadow Resistance Aura"],
    [48947, "Fire Resistance Aura"],
    [25956, "Improved Judgements"],
    [60663, "Mighty Armor", "225 Armor"],
    [44500, "Major Agility", "22 Agility"],
    [44591, "Titanweave", "16 Defense"],
    [60692, "Powerful Stats", "10 All Stats"],
    [47900, "Super Health", "275 Health"],
    [47766, "Greater Defense", "22 Defense"],
    [62256, "Major Stamina", "40 Stamina"],
    [57690, "Fur Lining - Stamina", "102 Stamina"],
    [44625, "Armsman"],
    [44488, "Precision"],
    [63770, "Reticulated Armor Webbing", "240 Armor"],
    [47901, "Tuskarr's Vitality"],
    [44528, "Greater Fortitude", "22 Stamina"],
    [27984, "Mongoose"],
    [64579, "Blood Draining"],
    [59619, "Accuracy"],
    [64441, "Blade Ward"],
    [44489, "Enchant Shield - Defense", "20 Defense"]
  ];

  const entities = new Map();
  const phrases = [];

  function register(type, row) {
    const entity = { type, id: row[0] };
    row.slice(1).forEach(function (name) {
      entities.set(name, entity);
      phrases.push(name);
    });
  }

  items.forEach(function (row) { register("item", row); });
  spells.forEach(function (row) { register("spell", row); });

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

  function decorateNamedItems() {
    document.querySelectorAll(".item-name").forEach(function (node) {
      const name = node.textContent.trim();
      const entity = entities.get(name);
      if (!entity || node.closest("[data-wowhead]")) return;

      if (node.tagName === "A") {
        decorateAnchor(node, entity);
        return;
      }

      const anchor = makeAnchor(name, entity);
      node.textContent = "";
      node.appendChild(anchor);
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
      "g"
    );
    const root = document.querySelector("main") || document.body;
    const walker = document.createTreeWalker(root, NodeFilter.SHOW_TEXT);
    const candidates = [];
    let textNode;

    while ((textNode = walker.nextNode())) {
      const parent = textNode.parentElement;
      if (!parent || !textNode.nodeValue.trim()) continue;
      if (parent.closest("a, code, pre, script, style, textarea, button, iframe, nav, .item-name")) continue;
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
        const phraseStart = match.index + prefix.length;
        if (phraseStart > cursor) fragment.appendChild(document.createTextNode(node.nodeValue.slice(cursor, phraseStart)));
        fragment.appendChild(makeAnchor(phrase, entities.get(phrase)));
        cursor = phraseStart + phrase.length;
      }

      if (cursor < node.nodeValue.length) fragment.appendChild(document.createTextNode(node.nodeValue.slice(cursor)));
      node.parentNode.replaceChild(fragment, node);
    });
  }

  function loadWowheadTooltips() {
    if (document.querySelector('script[data-tankadin-wowhead]')) return;
    window.whTooltips = {
      colorLinks: false,
      iconizeLinks: false,
      renameLinks: false
    };
    const script = document.createElement("script");
    script.src = "https://wow.zamimg.com/js/tooltips.js";
    script.async = true;
    script.dataset.tankadinWowhead = "true";
    document.head.appendChild(script);
  }

  function init() {
    decorateNamedItems();
    linkPhrases();
    loadWowheadTooltips();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init, { once: true });
  } else {
    init();
  }
}());
