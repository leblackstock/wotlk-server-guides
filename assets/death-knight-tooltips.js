(function () {
  "use strict";

  const spellIds = {
    "abomination's might": 53138,
    "anti-magic shell": 48707,
    "anticipation": 55133,
    "army of the dead": 42650,
    "black ice": 49664,
    "blade barrier": 64859,
    "bladed armor": 49393,
    "blood boil": 49941,
    "blood plague": 59879,
    "blood strike": 49930,
    "blood tap": 45529,
    "bloody vengeance": 49504,
    "chains of ice": 45524,
    "chill of the throne": 69127,
    "dark command": 56222,
    "dark conviction": 49480,
    "death and decay": 49938,
    "death coil": 49895,
    "death grip": 49576,
    "death pact": 48743,
    "death rune mastery": 50034,
    "death strike": 49998,
    "empower rune weapon": 47568,
    "frigid dreadplate": 51109,
    "frost fever": 59921,
    "frost presence": 48263,
    "horn of winter": 57623,
    "icebound fortitude": 48792,
    "icy touch": 49909,
    "improved death strike": 62908,
    "improved icy touch": 49471,
    "improved rune tap": 49489,
    "hysteria": 49016,
    "mark of blood": 49005,
    "mind freeze": 47528,
    "pestilence": 50842,
    "plague strike": 49921,
    "raise dead": 46584,
    "rune strike": 56815,
    "rune tap": 48982,
    "scent of blood": 49004,
    "spell deflection": 49497,
    "strangulate": 47476,
    "taunt": 355,
    "toughness": 49789,
    "two-handed weapon specialization": 55108,
    "vampiric blood": 55233,
    "veteran of the third war": 50029,
    "will of the necropolis": 50150,
    "glyph of disease": 64267
  };

  const itemIds = {
    "ashen band of endless courage": 50404,
    "austere earthsiege diamond": 41380,
    "bile-encrusted medallion": 50023,
    "blackened dragonfin": 42999,
    "boots of kingly upheaval": 49907,
    "broken ram skull helm": 49986,
    "cataclysmic chestguard": 50968,
    "cloak of peaceful resolutions": 44188,
    "clutch of fortification": 47731,
    "corroded skeleton key": 50356,
    "cryptmaker": 49919,
    "dragonfin filet": 43000,
    "eitrigg's oath": 47882,
    "fish feast": 43015,
    "flask of stoneblood": 46379,
    "gauntlets of the kraken": 50978,
    "glorenzelg, high-blade of the silver hand": 50070,
    "glyph of blood tap": 43535,
    "glyph of dark command": 43538,
    "glyph of icebound fortitude": 43545,
    "glyph of indomitability": 47735,
    "glyph of pestilence": 43672,
    "glyph of raise dead": 43673,
    "glyph of vampiric blood": 43554,
    "guardian's dreadstone": 40141,
    "indestructible potion": 40093,
    "nightmare tear": 49110,
    "oathbinder, charge of the ranger-general": 50425,
    "petrified twilight scale": 54571,
    "pillars of might": 49904,
    "ramaladni's blade of culling": 50798,
    "rhinolicious wormsteak": 42994,
    "runic healing potion": 33447,
    "sanctified scourgelord chestguard": 51134,
    "sanctified scourgelord faceguard": 51133,
    "sanctified scourgelord handguards": 51132,
    "sanctified scourgelord legguards": 51131,
    "sanctified scourgelord pauldrons": 51130,
    "scourgelord faceguard": 50855,
    "seal of the pantheon": 36993,
    "sindragosa's flawless fang": 50361,
    "snapper extreme": 42996,
    "solid dragon's eye": 42146,
    "solid majestic zircon": 40119,
    "the black heart": 47216,
    "unidentifiable organ": 50341,
    "verdigris chain belt": 50991
  };

  const normalize = (text) => text.trim().toLowerCase().replace(/\s+/g, " ");

  function enhance(selector, map, type) {
    document.querySelectorAll(selector).forEach((node) => {
      if (node.closest("a, code, button")) return;
      const id = map[normalize(node.textContent)];
      if (!id) return;
      const link = document.createElement("a");
      link.className = node.className;
      link.href = `https://www.wowhead.com/wotlk/${type}=${id}`;
      link.target = "_blank";
      link.rel = "noopener";
      link.innerHTML = node.innerHTML;
      node.replaceWith(link);
    });
  }

  function init() {
    enhance(".spell-name, .talent-name, .glyph-name", spellIds, "spell");
    enhance(".item-name", itemIds, "item");
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init, { once: true });
  } else {
    init();
  }
}());
