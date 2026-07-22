#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
UI = ROOT / "assets" / "addon-catalog.js"
UNIT = ROOT / "tests" / "addon-search.test.js"
BROWSER = ROOT / "tests" / "addon-browser-smoke.cjs"

text = UI.read_text(encoding="utf-8")
old = '''    function groupOptions(group) {\n      return allPotentialOptions(group).filter((id) => {\n        if ((state.filters[group] || []).includes(id)) return true;\n        return countForOption(group, id) > 0;\n      });\n    }'''
new = '''    function isMeaningfulOption(group, id) {\n      if (group !== "specialization") return true;\n      const tag = tagMap.get(id);\n      const selectedClasses = state.filters.class || [];\n      if (selectedClasses.length === 1 && tag?.classId !== selectedClasses[0]) return false;\n      return catalog.addons.some((addon) => {\n        if ((addon.tags || []).includes(id) || (addon.scope?.specs || []).includes(id)) return true;\n        return [addon.recommendations || [], addon.customizations || []].some((records) =>\n          records.some((record) => (record.audience?.specs || []).includes(id))\n        );\n      });\n    }\n\n    function groupOptions(group) {\n      return allPotentialOptions(group).filter((id) => {\n        if ((state.filters[group] || []).includes(id)) return true;\n        if (!isMeaningfulOption(group, id)) return false;\n        return countForOption(group, id) > 0;\n      });\n    }'''
if old not in text:
    raise SystemExit("Could not find groupOptions block")
UI.write_text(text.replace(old, new), encoding="utf-8", newline="\n")

text = UNIT.read_text(encoding="utf-8")
anchor = 'const addons = catalog.addons;\n'
addition = '''const addons = catalog.addons;\nconst specializationTags = catalog.tags.filter((tag) => tag.group === "specialization");\nassert.equal(specializationTags.length, 30, "WotLK taxonomy should register thirty class-qualified specializations");\nassert.ok(specializationTags.every((tag) => tag.classId && Array.isArray(tag.roleIds) && tag.id.startsWith(`${tag.classId}-`)));\nassert.equal(catalog.tags.some((tag) => ["protection", "holy", "frost", "restoration"].includes(tag.id)), false);\n'''
if "WotLK taxonomy should register thirty" not in text:
    if anchor not in text:
        raise SystemExit("Could not find unit test anchor")
    text = text.replace(anchor, addition, 1)
UNIT.write_text(text, encoding="utf-8", newline="\n")

text = BROWSER.read_text(encoding="utf-8")
anchor = '    assert.equal(await desktop.locator(".addon-card").count(), 9, "Default catalog should show nine addons");\n'
addition = '''    assert.equal(await desktop.locator(".addon-card").count(), 9, "Default catalog should show nine addons");\n    await desktop.locator("#addon-all-filters").click();\n    const launchSpecs = desktop.locator('[data-filter-group="specialization"] .addon-filter-chip');\n    assert.equal(await launchSpecs.count(), 1, "Only specializations with targeted launch records should be shown");\n    assert.match(await launchSpecs.first().textContent(), /Protection/);\n'''
if "Only specializations with targeted launch records" not in text:
    if anchor not in text:
        raise SystemExit("Could not find browser test anchor")
    text = text.replace(anchor, addition, 1)
BROWSER.write_text(text, encoding="utf-8", newline="\n")

print("Patched specialization facet visibility and regression tests.")
