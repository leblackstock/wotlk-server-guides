# Fresh-80 Druid Guide Research Matrix

Status: implementation source sheet
Audience: newly capped level-80 Druids on an original-client WotLK 3.3.5a baseline
Server boundary: standard Wrath behavior is documented as the baseline; uncertain Hellscream behavior remains labeled `Needs Hellscream test`.

## Shared audience contract

- Normal and heroic dungeons are the entry path. Raid-boss caps and final-tier sets are progression goals, not entry requirements.
- Every baseline uses all 71 talent points and works without assuming a Draenei aura, another Druid, or another class supplying a required buff or debuff.
- Mark of the Wild or Gift of the Wild, Thorns where useful, an appropriate form, reagents for Rebirth, repaired gear, and role-appropriate consumables are ordinary preparation.
- Innervate and Rebirth are assignments, not automatic personal cooldowns. The player confirms the target and timing before a pull.
- Cat and Bear are separate guide families because their talent, gearing, and encounter responsibilities diverge. Both remain one Feral specialization identity and use the approved Feral palette.
- All four families keep advanced raid optimizations, premium consumables, epic gems, Tier 9/Tier 10 transitions, ICC items, and Ruby Sanctum items in later-progression sections.

## Balance Druid

### Baseline

- Talent build: 55/0/16 fresh-80 dungeon and solo baseline.
- Calculator: `druid/5012203125331003213305301231--205003312`.
- The build retains the complete Eclipse and Starfall engine while investing in the Restoration tree for self-contained mana support.
- Major glyphs: Glyph of Starfall, Glyph of Starfire, and Glyph of Moonfire as the stable starting set. Glyph of Insect Swarm, Glyph of Focus, and Glyph of Rebirth are later encounter comparisons.
- Minor glyphs: Glyph of Unburdened Rebirth and Glyph of the Wild first; the final slot is convenience.

### Decision engine

1. Maintain Moonkin Form, Mark or Gift of the Wild, and the assigned Faerie Fire effect.
2. Use Force of Nature and Starfall only when their full value is safe; Starfall must not pull inactive packs.
3. Maintain Moonfire and Insect Swarm when the target will live long enough.
4. Cast Wrath to trigger Lunar Eclipse, then cast Starfire during Lunar Eclipse.
5. Cast Starfire to trigger Solar Eclipse, then cast Wrath during Solar Eclipse.
6. Use Typhoon, Hurricane, roots, dispels, Innervate, and Rebirth for the group rather than as damage-padding distractions.

### Fresh-80 teaching emphasis

- With Balance of Power and Improved Faerie Fire active, the level-83 spell-hit progression target is 10% from gear, about 263 hit rating. The full 17% spell-hit requirement is about 446 rating before talents and effects.
- Explain Eclipse as a state machine rather than a fixed cast sequence.
- Treat the haste point where raid-buffed Wrath approaches the one-second global floor as a later set calculation, not a fresh-80 shopping requirement.
- Put mana stability, safe Starfall use, movement globals, and emergency utility before endgame snapshot or set-bonus optimization.

## Feral Cat Druid

### Baseline

- Talent build: 0/55/16 pure Cat baseline.
- Calculator: `druid/-553201132322010053120030310511-203503012`.
- Major glyphs: Glyph of Rip, Glyph of Shred, and Glyph of Savage Roar. Glyph of Berserk is a later short-fight comparison.
- Minor glyphs: Glyph of Dash and Glyph of Unburdened Rebirth first; Glyph of the Wild is convenience unless a specific tested proc strategy is deliberately adopted.

### Decision engine

1. Enter Cat Form, approach from a safe position, and keep Savage Roar active.
2. Maintain the Mangle bleed-damage effect when no equivalent effect is assigned.
3. Maintain Rake and a five-combo-point Rip on targets that will live long enough.
4. Build with Shred from behind; use Mangle when Shred positioning is unavailable.
5. Pool Energy before refresh windows instead of pressing every ability immediately.
6. Use Ferocious Bite only when Rip and Savage Roar are safe, and use Swipe (Cat) only on a stable pack that will live long enough.

### Fresh-80 teaching emphasis

- Teach ordinary Cat play before optional bearweaving or Gift-of-the-Wild Clearcasting fishing. Those are later, server-sensitive optimizations.
- Physical special attacks need 8% hit against a level-83 boss, about 263 rating. The 26-expertise dodge soft cap is about 214 expertise rating before Primal Precision and other effects are counted.
- Hit and expertise are valuable reliability stats, not mandatory dungeon-entry gates and not automatic gem-to-cap commands.
- Keep Armor Penetration proc soft caps and the 1,400-rating hard cap in a later transition supported by an actual gear set.

## Feral Bear Druid

### Baseline

- Talent build: 0/60/11 mono-Bear baseline.
- Calculator: `druid/-503232132322010353120303013511-20350001`.
- Major glyphs: Glyph of Maul and Glyph of Survival Instincts first; Glyph of Mangle is the stable single-target third slot, with Glyph of Frenzied Regeneration, Glyph of Berserk, and Glyph of Growl as encounter comparisons.
- Minor glyphs: Glyph of Challenging Roar, Glyph of Dash, and Glyph of Unburdened Rebirth.

### Decision engine

1. Enter Dire Bear Form before contact and establish the pull with Faerie Fire (Feral), Feral Charge, or line-of-sight positioning.
2. Keep Demoralizing Roar active when no stronger attack-power reduction is confirmed.
3. Use Mangle (Bear) on cooldown, maintain Lacerate on durable targets, and use Faerie Fire (Feral) whenever it adds useful threat.
4. Queue Maul only when Rage remains available for the next required global.
5. Use Swipe (Bear) and tab-targeted attacks across packs; Growl, Bash, Feral Charge, and Challenging Roar recover escapes.
6. Plan Barkskin, Survival Instincts, and Frenzied Regeneration around incoming damage rather than stacking every cooldown after health has already collapsed.

### Fresh-80 teaching emphasis

- Survival of the Fittest supplies critical-strike immunity in Bear Form; a Feral tank does not pursue the plate-tank 540 Defense rule.
- Stamina, Agility, and armor form the early survival package. Hit and expertise improve reliability but do not replace effective health.
- The standard mono-Bear build does not improve every group debuff. The guide must tell a solo or five-player Bear to maintain baseline Demoralizing Roar and must show exact later talent swaps if the group needs stronger attack-power or attack-speed coverage.
- Threat starts with controlled pulls, target coverage, and Rage discipline—not a raid-only offensive set.

## Restoration Druid

### Baseline

- Talent build: 11/0/60 self-contained Tree of Life baseline.
- Calculator: `druid/05320001--230033312031512531153313051`.
- Major glyphs: Glyph of Swiftmend, Glyph of Wild Growth, and Glyph of Nourish as the flexible five-player starting set. Glyph of Rejuvenation, Glyph of Rapid Rejuvenation, Glyph of Innervate, and Glyph of Rebirth are later assignment comparisons.
- Minor glyphs: Glyph of Unburdened Rebirth and Glyph of the Wild first; the final slot is convenience.

### Decision engine

1. Maintain Tree of Life and Mark or Gift of the Wild.
2. Keep Rejuvenation on the tank and pre-HoT players who are about to take predictable damage.
3. Use Wild Growth when several nearby players need healing; placement and target choice determine coverage.
4. Use Lifebloom deliberately—roll it only when sustained tank damage justifies the mana, or let it bloom for healing and the mana refund.
5. Use Swiftmend for urgent burst without consuming the HoT when glyphed, and Nourish when a HoT-covered target needs direct healing.
6. Reserve Nature's Swiftness plus Healing Touch, Tranquility, Barkskin, Innervate, and Rebirth for planned or called recovery jobs.

### Fresh-80 teaching emphasis

- Healing is a triage system, not a rotation. Five-player tank stability and emergency recovery come before raid blanketing.
- Spell Power is the first uncapped throughput stat. Haste, Spirit, MP5, and Intellect are balanced against actual mana stability.
- The one-second global-cooldown goals—735 haste with Celestial Focus or 856 without it under their stated raid-buff assumptions—are later progression references, not dungeon-entry requirements.
- Premium haste sets, Rapid Rejuvenation breakpoints, and raid-wide Rejuvenation blanketing wait until the player has the gear and encounter knowledge to support them.

## Shared gearing path

### Immediate and inexpensive

- Replace leveling greens through level-80 normal dungeons, heroic dungeons, reputation rewards, inexpensive BoEs, crafts, and emblems.
- Balance prioritizes a credible caster weapon, enough hit for the content being attempted, and two functioning trinkets.
- Cat prioritizes weapon DPS/Feral Attack Power, Agility or Strength according to the whole set, and reliable uptime before an Armor Penetration transition.
- Bear prioritizes Stamina, Agility, armor, and dependable threat tools; a defensive set and a threat set may share pieces without becoming one final BiS list.
- Restoration prioritizes a credible healing weapon, Spell Power, sustainable mana, and enough Haste to make the character feel responsive before chasing a raid GCD cap.
- Rare gems and budget enchants belong on temporary gear. Epic gems and premium enchants belong on pieces expected to last.

### Later progression

- Trial of the Champion and the Icecrown five-player dungeons are catch-up paths before raid drops.
- Tier 9 and Tier 10 bonuses are progression systems, not the first shopping list.
- Armor Penetration transitions for Cat and haste-cap transitions for Restoration require a complete, explicitly stated set and buff model.
- ICC and Ruby Sanctum items remain later targets with raid size, difficulty, and server source verified before publication.

## Original-client macro boundaries

- Use exact English 3.3.5a spell names.
- Supported patterns include `#showtooltip`, `[@focus]`, `[@mouseover]`, `[help]`, `[harm]`, `[stance]`, `[nostance]`, `/cast`, and `/cancelform` where the original client supports them.
- Do not use Retail-only cursor casting, modern talent-loadout commands, or macros that claim to make rotation, healing, dispel, or tanking decisions.
- Form macros must state when a key changes form and when that change can remove the player from the current role or resource state.

## Hellscream verification queue

- Shared: Rebirth reset behavior, reagent requirements, Innervate scaling, form transitions, threat modifiers, taunt hit behavior, and encounter-specific dispel or crowd-control immunities.
- Balance: Eclipse proc and internal-cooldown behavior, Starfall target selection, Force of Nature pathing, Typhoon knockback rules, and any custom Improved Faerie Fire behavior.
- Cat: Omen of Clarity proc rules, Gift-of-the-Wild proc fishing, Rip extension, Savage Roar scaling, bearweaving, and any custom Armor Penetration behavior.
- Bear: Survival of the Fittest critical-strike immunity, Savage Defense absorption, Maul queueing, Growl hit behavior, Infected Wounds immunity, and Lacerate threat.
- Restoration: Lifebloom mana return, Wild Growth target selection, Swiftmend consumption with its glyph, Rejuvenation haste behavior, Revitalize, and Tranquility party-versus-raid behavior.

## Primary implementation references

### Balance

- [Talent builds and glyphs](https://www.wowhead.com/wotlk/guide/classes/druid/balance/dps-talent-builds-glyphs-pve)
- [Rotation, cooldowns, and abilities](https://www.wowhead.com/wotlk/guide/classes/druid/balance/dps-rotation-cooldowns-abilities-pve)
- [Stats and hit assumptions](https://www.wowhead.com/wotlk/guide/classes/druid/balance/dps-stat-priority-attributes-pve)
- [Pre-raid gear](https://www.wowhead.com/wotlk/guide/classes/druid/balance/dps-bis-gear-pre-raid-pve)

### Feral Cat

- [Talent builds and glyphs](https://www.wowhead.com/wotlk/guide/classes/druid/feral/dps-talent-builds-glyphs-pve)
- [Rotation, cooldowns, and abilities](https://www.wowhead.com/wotlk/guide/classes/druid/feral/dps-rotation-cooldowns-abilities-pve)
- [Stats and caps](https://www.wowhead.com/wotlk/guide/classes/druid/feral/dps-stat-priority-attributes-pve)
- [Pre-raid gear](https://www.wowhead.com/wotlk/guide/classes/druid/feral/dps-bis-gear-pre-raid-pve)

### Feral Bear

- [Talent builds and glyphs](https://www.wowhead.com/wotlk/guide/classes/druid/feral/tank-talent-builds-glyphs-pve)
- [Rotation, cooldowns, and abilities](https://www.wowhead.com/wotlk/guide/classes/druid/feral/tank-rotation-cooldowns-abilities-pve)
- [Stats and mitigation assumptions](https://www.wowhead.com/wotlk/guide/classes/druid/feral/tank-stat-priority-attributes-pve)
- [Pre-raid gear](https://www.wowhead.com/wotlk/guide/classes/druid/feral/tank-bis-gear-pre-raid-pve)

### Restoration

- [Talent builds and glyphs](https://www.wowhead.com/wotlk/guide/classes/druid/restoration/healer-talent-builds-glyphs-pve)
- [Rotation, cooldowns, and abilities](https://www.wowhead.com/wotlk/guide/classes/druid/restoration/healer-rotation-cooldowns-abilities-pve)
- [Stats and haste assumptions](https://www.wowhead.com/wotlk/guide/classes/druid/restoration/healer-stat-priority-attributes-pve)
- [Pre-raid gear](https://www.wowhead.com/wotlk/guide/classes/druid/restoration/healer-bis-gear-pre-raid-pve)

### Shared raids

- [Trial of the Crusader](https://www.wowhead.com/wotlk/zone=4722/trial-of-the-crusader)
- [Icecrown Citadel](https://www.wowhead.com/wotlk/zone=4812/icecrown-citadel)
- [Ruby Sanctum](https://www.wowhead.com/wotlk/zone=4987/the-ruby-sanctum)
