# New Level-80 Guide Workflow

This is the required workflow for a guide whose reader has just reached level 80. It does not apply to a deliberately specialized guide such as a Heroic LK25 tank playbook, which must declare `guideAudience: "specialized-raid"` instead.

## Audience contract

A new-80 guide assumes the reader:

- may still wear leveling, quest, normal-dungeon, or inexpensive Auction House gear;
- has limited gold, emblems, reputation, professions, and consumables;
- has no guaranteed raid spot, raid assignment, external raid buff, Draenei aura, or specific party composition;
- needs a complete self-contained talent and ability setup before optimization;
- is learning normal and heroic dungeons before later raid progression.

Put this contract in the config:

```json
"guideAudience": "fresh-80",
"fresh80Policy": {
  "selfContainedTalents": true,
  "externalRaidBuffsRequired": false,
  "capsAreProgressionGoals": true,
  "budgetBeforePremium": true,
  "raidContentIsLaterProgression": true
}
```

## Creation sequence

1. Start from the closest approved fresh-80 config, never from a specialized raid guide.
2. Define the nickname, guide types, class color, spec color, and concise banner sentence before writing sections.
3. Run the fresh-80 wrapper in dry-run mode:

   ```powershell
   node tools/create-fresh-80-spec-guide.mjs templates/spec-guide/my-spec.config.json --dry-run
   ```

4. Research a fully allocated talent tree. Verify every point in the calculator and confirm that the build works without another class supplying a mandatory buff or debuff.
5. Write the six pages in audience order: immediate operation, playing, setup, building, equipping, then later raiding.
6. Add verified entities to the class registry and rebuild the tooltip script.
7. Run the ordinary draft audits plus the fresh-80 audit.
8. Review desktop and mobile layouts. Check real mouseovers, talent fallback links, navigation, collapsed notes, and keyboard behavior.
9. Update only the footers of guide pages changed that day.
10. Run the canonical release audit, stage only the intended guide family, push `main`, and verify the public GitHub Pages result.

## What every page should have

### Quick Start

- The shared banner and detached jump chips.
- One Two-minute operating manual with the approved summary, engine, checklist, and numbered-first-moves pattern.
- A plain statement of what the player can do immediately after reaching 80.
- Caps described as targets to work toward, not automatic gates blocking normal or heroic dungeons.
- Self-buffs, basic consumables, pet or stance setup, and group-safe defaults that do not require raid coordination.

### Playing

- A default priority or decision engine and the exceptions that actually change it.
- Solo, normal-dungeon, heroic-dungeon, movement, resource, survival, and group-utility situations where relevant.
- Boss consumables and pre-potting labeled as planned or optional, not basic entry requirements.
- Group instructions first; raid assignments may appear as later extensions.

### Setup

- One fully filled, verified, self-contained talent baseline.
- The default build must include essential buffs or utility the new player cannot assume another class provides.
- Raid-composition optimizations belong in a clearly labeled later swap note, including exactly which point moves where and why.
- Default glyphs, affordable alternatives, pet setup when relevant, practical original-client macros, addons, and required tracking.

### Building

- Exact stat conversions and target-level assumptions.
- A fresh-80 stage, a later raid-ready stage, and any endgame transition as separate concepts.
- Rare or affordable gems and budget enchants for temporary gear before epic gems and premium enchants.
- Endgame thresholds such as Armor Penetration soft caps shown only as later transitions supported by an actual set.
- Professions presented as optional choices, never assumed character prerequisites.

### Equipping

- Immediate normal-dungeon, heroic-dungeon, reputation, crafted, inexpensive BoE, and emblem options first.
- Weapon and trinket priorities where those slots disproportionately affect performance.
- ToC, ICC, Ruby Sanctum, heroic, and 25-player items retained only as later progression targets in separate sections.
- No final-tier BiS list presented as the new player's shopping list.

### Raiding

- A visible statement that the chapter is later progression, not the starting expectation.
- Consumables, assignments, filters, and encounter responsibilities only after the entry-path chapters are complete.
- Clear separation of 10-player, 25-player, normal, heroic, and server-specific behavior.

## What a new-80 guide should not have

- A recommended baseline titled “raid build,” “ICC build,” “25-player build,” or “BiS build.”
- Talents that require a Blood DK, Enhancement Shaman, Draenei, or any other external buff to make the baseline complete.
- A hit, defense, expertise, haste, or Armor Penetration target presented without the target level and talent assumptions.
- Language implying the player must be raid-ready before starting normal or heroic dungeons.
- Epic gems, premium enchants, flasks, pre-pots, expensive crafts, or final-tier gear treated as immediate requirements.
- Raid assignments in place of basic solo and group instructions.
- WotLK Classic features assumed to exist in the original 3.3.5a client.
- Unverified private-server behavior presented as fact.
- Icons added to satisfy a quota. The icon system verifies required placements and IDs; it does not decide content by count.

## Required checks

```powershell
node tools/build-wowhead-tooltips.mjs data/<class>-entities.json assets/<class>-tooltips.js
node tools/audit-fresh-80-guide.mjs templates/spec-guide/my-spec.config.json
node tools/audit-spec-guide.mjs templates/spec-guide/my-spec.config.json --release
```

The release audit automatically reruns the fresh-80 audit when `guideAudience` is `fresh-80`, then enforces rendered icon placement and playbook action icons.
