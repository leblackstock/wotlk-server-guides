# AH Crafted-Item Profession-Use Audit

Audited: 2026-08-03

This audit separates the profession that crafts an item from the profession,
if any, required to use the finished item. The canonical decisions are stored
in `data/ah-profession-use-audit.json`.

## Rules

- General-use finished items stay in the ordinary crafted market even when a
  profession makes them.
- A finished item with a hard profession-rank requirement belongs in a clearly
  labeled restricted section.
- An item with no hard gate but only a profession-tool or profession-reagent
  purpose belongs in a clearly labeled profession-audience section.
- Raw materials and recipes stay in their existing input/recipe sections.
  `RequiredSkill` can describe milling, prospecting, learning, or crafting and
  does not make the raw item exclusive to that profession.
- BoP, nontradeable, self-only, conjured, temporary, and invalid outputs do not
  belong in an AH guide.

## New or Renamed Sections

### Alchemy

- **Alchemist-only potions:** Crazy Alchemist's Potion; Mad Alchemist's Potion.
- General Wrath and Outland potion sections now explicitly exclude those two.
- Protection cauldrons remain general-use because the finished items have no
  Alchemy requirement.

### Blacksmithing

- **Blacksmith-only skeleton keys:** Silver, Golden, Truesilver, Arcanite,
  Cobalt, and Titanium Skeleton Keys.
- **Enchanter-only rod blanks:** Silver, Golden, Truesilver, Arcanite, Fel Iron,
  Adamantite, Eternium, and Titanium Rods.
- Wrath and Outland general-use enhancement sections no longer mix in keys or
  rod blanks; Classic intermediates remain explicitly labeled as inputs.

### Engineering

- **General-use Engineering utility:** Mana Injector Kit; Gnomish Army Knife.
- **Engineer-only bombs, sapper charges, and decoys:** Explosive Decoy,
  Saronite Bomb, Global Thermal Sapper Charge, Cobalt Frag Bomb, and Box of
  Bombs.
- **Engineer-only tools:** Arclight Spanner; Gyromatic Micro-Adjustor.
- **Engineer-only mount components:** Salvaged Iron Golem Parts,
  Goblin-machined Piston, and Elementium-plated Exhaust Pipe.
- Ammunition remains general-use. Engineering parts and blasting powders remain
  explicitly labeled profession inputs.

### Inscription

- **Enchanter-only blank vellums:** Armor Vellum III; Weapon Vellum III.
- Certificate of Ownership, Iron-bound Tome, and Faces of Doom remain in the
  general-use utility/equipment section.

### Cooking

- **Cook-required feasts:** Great Feast, Fish Feast, Gigantic Feast, and Small
  Feast. The
  character placing the feast needs Cooking; characters eating from it do not.
- **Rogue-only utility:** Thistle Tea is tradeable but only Rogues can use it.
- Ordinary finished foods and drinks remain in general-use crafted sections.

### Jewelcrafting

- **Jewelcrafter-only Dragon's Eye:** the raw tradeable gem is separated from
  unrestricted epic gems. BoP jeweler-only cuts remain excluded.

### Leatherworking

- **Leatherworker-only drums:** Drums of War, Battle, Speed, Restoration, and
  Panic retain their finished-item Leatherworking requirements.
- Specialty profession-material bags are labeled for their actual profession
  buyer rather than presented as ordinary general-use bags.
- Drums of Forgotten Kings and Drums of the Wild do not require Leatherworking
  on the finished item.

### Tailoring

- **Tailor-only nets:** Netherweave Net, Heavy Netherweave Net, and Frostweave
  Net retain their finished-item Tailoring requirements.
- Tradeable cloth, bags, equipment, and spellthreads remain in general-use
  sections; self-only embroidery and BoP carpets remain excluded.

## Profession Guides With No Restricted Finished-Item Move

- Enchanting: completed enchant scrolls, oils, and tradeable wands are usable
  without Enchanting; profession intermediates were already isolated.
- Mining: the guide contains ores, bars, stones, and smelting outputs rather
  than profession-locked consumer items.
- Herbalism, Skinning, and Fishing raw-material sections remain input markets.
- Recipe-drop guides already group recipes by the profession and rank required
  to learn them.

## Removed Items

- **Bright Baubles:** removed instead of creating a one-row restricted section
  for an unlimited low-cost Fishing vendor lure.
- **Virtuoso Inking Set:** removed from the Herbalism and Inscription guides
  instead of listing an unlimited low-cost Scribe-only vendor tool.
- **Jeweler's Kit** and **Simple Grinder:** removed instead of preserving a
  dedicated section for unlimited low-cost Jewelcrafting vendor tools.

No tradeable crafted output was removed. The removals are low-cost vendor tools
that added noise without a defensible specialist AH market.

## Excluded Crafted Outputs

- **Clamlette Magnifique:** Bind on Pickup Cooking quest output.
- **Bread of the Dead:** Bind on Pickup seasonal Cooking output.

These were excluded during complete recipe discovery because neither item can
be listed on the Auction House; they were not removed from an existing AH row.
