from pathlib import Path
from html.parser import HTMLParser

ROOT = Path(__file__).resolve().parents[2]
GUIDE = ROOT / "guides/protection-paladin-pve-guide.html"
FRAGS = ROOT / ".github/tmp/ppala-level80"
text = GUIDE.read_text(encoding="utf-8")


def frag(name: str) -> str:
    return (FRAGS / name).read_text(encoding="utf-8").rstrip("\n")


def once(old: str, new: str, label: str) -> None:
    global text
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected one match, found {count}")
    text = text.replace(old, new, 1)


sub = "    <p class=\"sub\">A practical raid-and-dungeon reference for our server. Built from Brotalnia's fast-paced 3.3.5 video guide, then cleaned up, expanded, and corrected where the captions, comments, or original advice were incomplete.</p>"
once(sub, sub + "\n\n" + frag("level-note.html"), "level note")

once(
    '      <a href="#stats">Stats &amp; caps</a>\n      <a href="#talents">Talents</a>',
    '      <a href="#stats">Stats &amp; caps</a>\n      <a href="#gearing-path">Gearing path</a>\n      <a href="#talents">Talents</a>',
    "gearing nav",
)
once(
    '      <a href="#consumables">Consumables</a>\n      <a href="#corrections">Video corrections</a>',
    '      <a href="#consumables">Consumables</a>\n      <a href="#encounter-tuning">Encounter tuning</a>\n      <a href="#corrections">Video corrections</a>',
    "encounter nav",
)

once(
    '<h3 style="margin:16px 0 4px">Clean opening sequence</h3>',
    '<h3 style="margin:16px 0 4px">Clean 969 sequence</h3>',
    "rotation heading",
)

old_pull = '''      <div class="spell-card">
        <h3>Single-target pull</h3>
        <ol class="priority-list">
          <li>Use Seal of Corruption/Vengeance, Righteous Fury, Blessing of Sanctuary, Divine Plea, and Sacred Shield.</li>
          <li>Pre-cast Holy Shield. Use Avenging Wrath if the encounter allows it and you will not need an immunity during Forbearance.</li>
          <li>At range, use Exorcism only when you are safe to stand still; otherwise use Avenger's Shield.</li>
          <li>Hand of Reckoning adds snap damage when you do not already have threat.</li>
          <li>Enter 969 and keep the boss faced away from the group.</li>
        </ol>
      </div>'''
once(old_pull, frag("flexible-pull.html"), "flexible pull")

once(
    '    </div>\n\n    <div class="note warning"><strong>Rotation macros are training wheels.</strong>',
    '    </div>\n\n' + frag("rotation-recovery.html") + '\n\n    <div class="note warning"><strong>Rotation macros are training wheels.</strong>',
    "rotation recovery",
)

shield = '''      <div class="spell-card">
        <h3>Divine Shield</h3>
        <p>Use a bubble-cancel to clear specific debuffs only when the encounter allows it. Divine Shield does not erase your stored threat, but enemies stop treating you as a valid attack target while immune.</p>
        <div class="tag-row"><span class="tag warn">Tank-swap risk</span><span class="tag info">Debuff clear</span></div>
      </div>'''
once(shield, shield + "\n\n" + frag("extra-cooldown-cards.html"), "cooldown cards")

once(
    '  </section>\n\n  <section class="common" id="talents">',
    '  </section>\n\n' + frag("gearing-path.html") + '\n\n  <section class="common" id="talents">',
    "gearing section",
)

profession_note = "    <p class=\"mini-note\">The video's Jewelcrafting/Leatherworking recommendation is defensible for raw stamina. Engineering often wins in real encounters because movement and on-use utility solve problems that spreadsheet stamina cannot.</p>"
once(profession_note, profession_note + "\n\n" + frag("engineering-tools.html"), "engineering tools")

once(
    '          <tr><td><strong>Food</strong></td><td><span class="item-name q-common">Blackened Dragonfin</span></td><td><span class="item-name q-common">Dragonfin Filet</span> or <span class="item-name q-common">Fish Feast</span></td><td>Agility adds armor and avoidance; strength favors threat/block value; feast is convenient raid coverage.</td></tr>',
    frag("food-row.html"),
    "food row",
)
once(
    '          <tr><td><strong>Armor potion</strong></td><td><span class="item-name q-common">Indestructible Potion</span></td><td>None for physical survival</td><td>Pre-pot before the pull and use another later when the encounter allows. Excellent on predictable melee bursts.</td></tr>',
    frag("potion-row.html"),
    "potion row",
)

threat_row = '          <tr><td><strong>Threat potion</strong></td><td><span class="item-name q-common">Potion of Speed</span></td><td><span class="item-name q-common">Indestructible Potion</span></td><td>Use only when snap threat is the real problem.</td></tr>'
once(threat_row, threat_row + "\n" + frag("elixir-row.html"), "elixir row")

once(
    '    </div>\n  </section>\n\n  <details class="common correction-section" id="corrections">',
    '    </div>\n\n' + frag("consumable-extra-and-encounter.html") + '\n\n  <details class="common correction-section" id="corrections">',
    "encounter section",
)

source_anchor = '      <li><a href="https://www.wowhead.com/wotlk/spell=53592/touched-by-the-light" target="_blank" rel="noopener">Wowhead WotLK — Touched by the Light</a>. Final 3.3.5 scaling is based on Strength.</li>'
once(source_anchor, source_anchor + "\n" + frag("source-additions.html"), "source additions")
once("Updated July 16, 2026", "Updated July 18, 2026", "footer date")

required = [
    "Starts at level 80:", 'id="gearing-path"', "Flexible single-target pull",
    "Recovering 969 after movement", "Avenging Wrath</h3>",
    "Engineering tools worth testing on Hellscream", "Snapper Extreme",
    "Rhinolicious Wormsteak", 'id="encounter-tuning"',
    "Warmane-specific gearing, raid assignments, and tuning were intentionally excluded",
]
missing = [token for token in required if token not in text]
if missing:
    raise SystemExit(f"Missing required content: {missing}")
if any(token in text for token in ("Dirge's Kickin'", ">LoD<", ">Bane<")):
    raise SystemExit("Warmane-specific content leaked into the guide")
if text.count('id="gearing-path"') != 1 or text.count('id="encounter-tuning"') != 1:
    raise SystemExit("New section IDs are not unique")

class Parser(HTMLParser):
    pass

Parser().feed(text)
GUIDE.write_text(text, encoding="utf-8", newline="\n")
