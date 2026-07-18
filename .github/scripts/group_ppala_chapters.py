from pathlib import Path
from html.parser import HTMLParser

root = Path(__file__).resolve().parents[2]
guide = root / "guides/protection-paladin-pve-guide.html"
tmp = root / ".github/tmp/ppala-chapters"
text = guide.read_text(encoding="utf-8")


def load(name):
    return (tmp / name).read_text(encoding="utf-8").rstrip("\n")


def replace_block(start, end, replacement, label):
    global text
    a = text.find(start)
    b = text.find(end, a + len(start))
    if a < 0 or b < 0:
        raise SystemExit(f"Missing {label} markers")
    text = text[:a] + replacement + text[b + len(end):]


css_anchor = "    @media (max-width: 1040px) {"
if text.count(css_anchor) != 1 or ".chapter-divider {" in text:
    raise SystemExit("Chapter CSS cannot be inserted safely")
text = text.replace(css_anchor, load("chapter-style.css") + "\n\n" + css_anchor, 1)

replace_block(
    '  <nav class="site-nav" aria-label="Guide navigation">',
    "  </nav>",
    load("site-nav.html"),
    "site navigation",
)
replace_block(
    '    <div class="jump-nav" aria-label="Page sections">',
    "    </div>",
    load("topic-nav.html"),
    "topic navigation",
)

current = [
    "quick-start", "rotation", "cooldowns", "stats", "gearing-path",
    "talents", "glyphs", "macros", "addons", "gems", "enchants",
    "professions", "consumables", "encounter-tuning",
]
markers = [f'<section class="common" id="{item}">' for item in current]
positions = [text.find(marker) for marker in markers]
end_marker = '<details class="common correction-section" id="corrections">'
end_pos = text.find(end_marker)
if any(pos < 0 for pos in positions) or end_pos < 0 or positions != sorted(positions):
    raise SystemExit("Main section markers are missing or out of order")

blocks = {}
for index, item in enumerate(current):
    stop = positions[index + 1] if index + 1 < len(positions) else end_pos
    blocks[item] = text[positions[index]:stop].strip()


def divider(anchor, number, title, note):
    return f'''  <div class="chapter-divider" id="{anchor}">
    <span class="chapter-kicker">Part {number} of 4</span>
    <h2>{title}</h2>
    <p>{note}</p>
  </div>'''

chapters = [
    ("playing", 1, "Playing your Tankadin", "Pulling, 969, cooldowns, seals, and moment-to-moment tank control.", ["quick-start", "rotation", "cooldowns"]),
    ("setting-up", 2, "Setting up your Tankadin", "Talents, glyphs, macros, and addons that shape how the character plays.", ["talents", "glyphs", "macros", "addons"]),
    ("gearing", 3, "Gearing your Tankadin", "Stats, progression, gems, enchants, and professions from fresh level 80 onward.", ["stats", "gearing-path", "gems", "enchants", "professions"]),
    ("raiding", 4, "Raiding with your Tankadin", "Consumables, swap sets, and encounter-specific adjustments for Hellscream.", ["consumables", "encounter-tuning"]),
]
parts = []
for anchor, number, title, note, section_ids in chapters:
    parts.append(divider(anchor, number, title, note))
    parts.extend(blocks[item] for item in section_ids)

start = positions[0]
text = text[:start] + "\n\n".join(parts) + "\n\n" + text[end_pos:]

final_order = [
    "playing", "quick-start", "rotation", "cooldowns",
    "setting-up", "talents", "glyphs", "macros", "addons",
    "gearing", "stats", "gearing-path", "gems", "enchants", "professions",
    "raiding", "consumables", "encounter-tuning", "corrections",
]
final_positions = [text.find(f'id="{item}"') for item in final_order]
if any(pos < 0 for pos in final_positions) or final_positions != sorted(final_positions):
    raise SystemExit("Final chapter order is invalid")
for anchor in ("playing", "setting-up", "gearing", "raiding"):
    if text.count(f'id="{anchor}"') != 1:
        raise SystemExit(f"Duplicate or missing chapter anchor: {anchor}")

class Parser(HTMLParser):
    pass

Parser().feed(text)
guide.write_text(text, encoding="utf-8", newline="\n")
