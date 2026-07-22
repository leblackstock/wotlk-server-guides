#!/usr/bin/env python3
"""Migrate the addon catalog to class-qualified specs and resolved context inference."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "addons.json"
CORE = ROOT / "assets" / "addon-search-core.js"
UI = ROOT / "assets" / "addon-catalog.js"
CSS = ROOT / "assets" / "addon-catalog.css"
SEARCH_TESTS = ROOT / "tests" / "addon-search.test.js"
BROWSER_TESTS = ROOT / "tests" / "addon-browser-smoke.cjs"
ADDONS_HTML = ROOT / "guides" / "addons.html"
TANKADIN_HTML = ROOT / "guides" / "protection-paladin-setting-up.html"

SPEC_DEFS = [
    ("paladin-protection", "Protection (Paladin)", "Protection", "paladin", ["tank"], ["prot", "tankadin", "prot pally", "protection paladin"]),
    ("paladin-holy", "Holy (Paladin)", "Holy", "paladin", ["healer"], ["holy paladin", "holy pally"]),
    ("paladin-retribution", "Retribution", "Retribution", "paladin", ["dps"], ["ret", "ret paladin", "ret pally"]),
    ("warrior-protection", "Protection (Warrior)", "Protection", "warrior", ["tank"], ["prot warrior", "protection warrior"]),
    ("warrior-arms", "Arms", "Arms", "warrior", ["dps"], ["arms warrior"]),
    ("warrior-fury", "Fury", "Fury", "warrior", ["dps"], ["fury warrior"]),
    ("death-knight-blood", "Blood", "Blood", "death-knight", ["tank", "dps"], ["blood dk", "blood death knight"]),
    ("death-knight-frost", "Frost (Death Knight)", "Frost", "death-knight", ["tank", "dps"], ["frost dk", "frost death knight"]),
    ("death-knight-unholy", "Unholy", "Unholy", "death-knight", ["tank", "dps"], ["unholy dk", "unholy death knight"]),
    ("druid-balance", "Balance", "Balance", "druid", ["dps"], ["boomkin", "balance druid"]),
    ("druid-feral", "Feral", "Feral", "druid", ["tank", "dps"], ["feral druid", "bear", "cat"]),
    ("druid-restoration", "Restoration (Druid)", "Restoration", "druid", ["healer"], ["resto druid", "restoration druid"]),
    ("priest-discipline", "Discipline", "Discipline", "priest", ["healer"], ["disc", "disc priest", "discipline priest"]),
    ("priest-holy", "Holy (Priest)", "Holy", "priest", ["healer"], ["holy priest"]),
    ("priest-shadow", "Shadow", "Shadow", "priest", ["dps"], ["shadow priest", "spriest"]),
    ("shaman-elemental", "Elemental", "Elemental", "shaman", ["dps"], ["ele", "elemental shaman"]),
    ("shaman-enhancement", "Enhancement", "Enhancement", "shaman", ["dps"], ["enh", "enhancement shaman"]),
    ("shaman-restoration", "Restoration (Shaman)", "Restoration", "shaman", ["healer"], ["resto shaman", "restoration shaman"]),
    ("mage-arcane", "Arcane", "Arcane", "mage", ["dps"], ["arcane mage"]),
    ("mage-fire", "Fire", "Fire", "mage", ["dps"], ["fire mage"]),
    ("mage-frost", "Frost (Mage)", "Frost", "mage", ["dps"], ["frost mage"]),
    ("warlock-affliction", "Affliction", "Affliction", "warlock", ["dps"], ["aff", "affliction warlock"]),
    ("warlock-demonology", "Demonology", "Demonology", "warlock", ["dps"], ["demo", "demonology warlock"]),
    ("warlock-destruction", "Destruction", "Destruction", "warlock", ["dps"], ["destro", "destruction warlock"]),
    ("rogue-assassination", "Assassination", "Assassination", "rogue", ["dps"], ["mut", "mutilate", "assassination rogue"]),
    ("rogue-combat", "Combat", "Combat", "rogue", ["dps"], ["combat rogue"]),
    ("rogue-subtlety", "Subtlety", "Subtlety", "rogue", ["dps"], ["sub", "subtlety rogue"]),
    ("hunter-beast-mastery", "Beast Mastery", "Beast Mastery", "hunter", ["dps"], ["bm", "beast mastery hunter"]),
    ("hunter-marksmanship", "Marksmanship", "Marksmanship", "hunter", ["dps"], ["marksman", "mm", "marksmanship hunter"]),
    ("hunter-survival", "Survival", "Survival", "hunter", ["dps"], ["sv", "survival hunter"]),
]

LEGACY_BY_CLASS = {
    "paladin": {"protection": "paladin-protection", "holy": "paladin-holy", "retribution": "paladin-retribution"},
    "warrior": {"protection": "warrior-protection", "arms": "warrior-arms", "fury": "warrior-fury"},
    "death-knight": {"blood": "death-knight-blood", "frost": "death-knight-frost", "unholy": "death-knight-unholy"},
    "druid": {"balance": "druid-balance", "feral": "druid-feral", "restoration": "druid-restoration"},
    "priest": {"discipline": "priest-discipline", "holy": "priest-holy", "shadow": "priest-shadow"},
    "shaman": {"elemental": "shaman-elemental", "enhancement": "shaman-enhancement", "restoration": "shaman-restoration"},
    "mage": {"arcane": "mage-arcane", "fire": "mage-fire", "frost": "mage-frost"},
    "warlock": {"affliction": "warlock-affliction", "demonology": "warlock-demonology", "destruction": "warlock-destruction"},
    "rogue": {"assassination": "rogue-assassination", "combat-rogue": "rogue-combat", "subtlety": "rogue-subtlety"},
    "hunter": {"beast-mastery": "hunter-beast-mastery", "marksmanship": "hunter-marksmanship", "survival": "hunter-survival"},
}
OLD_SPEC_IDS = {value for mapping in LEGACY_BY_CLASS.values() for value in mapping}
NEW_SPEC_IDS = {item[0] for item in SPEC_DEFS}

ROLE_TO_SPEC = {
    "paladin": {"tank": "paladin-protection", "healer": "paladin-holy", "dps": "paladin-retribution"},
    "warrior": {"tank": "warrior-protection"},
    "priest": {"dps": "priest-shadow"},
    "shaman": {"healer": "shaman-restoration"},
    "druid": {"tank": "druid-feral", "healer": "druid-restoration"},
}

AMBIGUITY_CHOICES = {
    "warrior": {"dps": ["warrior-arms", "warrior-fury"]},
    "priest": {"healer": ["priest-discipline", "priest-holy"]},
    "shaman": {"dps": ["shaman-elemental", "shaman-enhancement"]},
    "druid": {"dps": ["druid-balance", "druid-feral"]},
    "hunter": {"dps": ["hunter-beast-mastery", "hunter-marksmanship", "hunter-survival"]},
    "mage": {"dps": ["mage-arcane", "mage-fire", "mage-frost"]},
    "rogue": {"dps": ["rogue-assassination", "rogue-combat", "rogue-subtlety"]},
    "warlock": {"dps": ["warlock-affliction", "warlock-demonology", "warlock-destruction"]},
    "death-knight": {
        "tank": ["death-knight-blood", "death-knight-frost", "death-knight-unholy"],
        "dps": ["death-knight-blood", "death-knight-frost", "death-knight-unholy"],
    },
}


def qualify(value: str, classes: list[str]) -> str:
    if value in NEW_SPEC_IDS:
        return value
    matches = {LEGACY_BY_CLASS[class_id][value] for class_id in classes if value in LEGACY_BY_CLASS.get(class_id, {})}
    if len(matches) == 1:
        return matches.pop()
    global_matches = {mapping[value] for mapping in LEGACY_BY_CLASS.values() if value in mapping}
    if len(global_matches) == 1:
        return global_matches.pop()
    return value


def migrate_catalog() -> None:
    payload = json.loads(DATA.read_text(encoding="utf-8"))
    tags = payload["tags"]
    first_spec = next(index for index, tag in enumerate(tags) if tag.get("group") == "specialization")
    non_specs = [tag for tag in tags if tag.get("group") != "specialization"]
    spec_tags = []
    for order, (tag_id, label, short_label, class_id, role_ids, aliases) in enumerate(SPEC_DEFS, start=1):
        spec_tags.append({
            "id": tag_id,
            "label": label,
            "shortLabel": short_label,
            "group": "specialization",
            "classId": class_id,
            "roleIds": role_ids,
            "description": f"Targeted setup or recommendation for {short_label} {next(tag['label'] for tag in tags if tag['id'] == class_id)}.",
            "searchAliases": aliases,
            "order": order * 10,
        })
    payload["tags"] = non_specs[:first_spec] + spec_tags + non_specs[first_spec:]
    payload["contextResolution"] = {
        "version": 1,
        "legacySpecAliasesByClass": LEGACY_BY_CLASS,
        "roleToSpec": ROLE_TO_SPEC,
        "ambiguityChoices": AMBIGUITY_CHOICES,
    }

    for addon in payload["addons"]:
        scope = addon.get("scope", {})
        scope_classes = scope.get("classes", [])
        for key in ("tags", "featuredTags"):
            addon[key] = [qualify(value, scope_classes) if value in OLD_SPEC_IDS else value for value in addon.get(key, [])]
        scope["specs"] = [qualify(value, scope_classes) for value in scope.get("specs", [])]
        for collection_name in ("recommendations", "customizations"):
            for record in addon.get(collection_name, []):
                audience = record.get("audience", {})
                audience["specs"] = [qualify(value, audience.get("classes", [])) for value in audience.get("specs", [])]

    used_old = []
    for addon in payload["addons"]:
        for key in ("tags", "featuredTags"):
            used_old.extend(value for value in addon.get(key, []) if value in OLD_SPEC_IDS)
        used_old.extend(value for value in addon.get("scope", {}).get("specs", []) if value in OLD_SPEC_IDS)
        for collection_name in ("recommendations", "customizations"):
            for record in addon.get(collection_name, []):
                used_old.extend(value for value in record.get("audience", {}).get("specs", []) if value in OLD_SPEC_IDS)
    if used_old:
        raise RuntimeError(f"Unmigrated specialization IDs remain: {sorted(set(used_old))}")

    DATA.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")


CORE_SOURCE = r'''(function (global) {
  "use strict";

  const CONTEXT_KEYS = {
    classes: "class",
    specs: "specialization",
    roles: "role",
    professions: "profession",
    activities: "activity",
    raids: "raid",
    encounters: "encounter"
  };
  const IMPORTANCE_RANK = { essential: 0, recommended: 1, optional: 2 };

  function normalize(value) {
    return String(value || "")
      .normalize("NFKD")
      .replace(/[\u0300-\u036f]/g, "")
      .toLowerCase()
      .replace(/[’']/g, "")
      .replace(/&/g, " and ")
      .replace(/defence/g, "defense")
      .replace(/[^a-z0-9]+/g, " ")
      .trim()
      .replace(/\s+/g, " ");
  }

  function editDistance(left, right) {
    if (left === right) return 0;
    if (!left.length) return right.length;
    if (!right.length) return left.length;
    let previous = Array.from({ length: right.length + 1 }, (_, index) => index);
    for (let leftIndex = 1; leftIndex <= left.length; leftIndex += 1) {
      const current = [leftIndex];
      for (let rightIndex = 1; rightIndex <= right.length; rightIndex += 1) {
        const substitution = previous[rightIndex - 1] + (left[leftIndex - 1] === right[rightIndex - 1] ? 0 : 1);
        current[rightIndex] = Math.min(previous[rightIndex] + 1, current[rightIndex - 1] + 1, substitution);
      }
      previous = current;
    }
    return previous[right.length];
  }

  function subsequencePenalty(needle, haystack) {
    let needleIndex = 0;
    let firstMatch = -1;
    let lastMatch = -1;
    for (let index = 0; index < haystack.length && needleIndex < needle.length; index += 1) {
      if (haystack[index] === needle[needleIndex]) {
        if (firstMatch < 0) firstMatch = index;
        lastMatch = index;
        needleIndex += 1;
      }
    }
    if (needleIndex !== needle.length) return Number.POSITIVE_INFINITY;
    return firstMatch + Math.max(0, lastMatch - firstMatch + 1 - needle.length);
  }

  function tokenScore(queryToken, candidateToken) {
    if (queryToken === candidateToken) return 0;
    if (candidateToken.startsWith(queryToken)) return 2 + (candidateToken.length - queryToken.length) * 0.06;
    if (candidateToken.includes(queryToken)) return 7 + candidateToken.indexOf(queryToken) * 0.15;
    const allowed = queryToken.length <= 4 ? 1 : queryToken.length <= 8 ? 2 : 3;
    if (Math.abs(queryToken.length - candidateToken.length) <= allowed) {
      const distance = editDistance(queryToken, candidateToken);
      if (distance <= allowed) return 15 + distance * 5;
    }
    if (queryToken.length >= 4) {
      const penalty = subsequencePenalty(queryToken, candidateToken);
      if (Number.isFinite(penalty) && penalty <= Math.max(3, Math.floor(candidateToken.length / 3))) return 29 + penalty;
    }
    return Number.POSITIVE_INFINITY;
  }

  function scoreText(rawQuery, rawCandidate) {
    const query = normalize(rawQuery);
    const candidate = normalize(rawCandidate);
    if (!query || !candidate) return Number.POSITIVE_INFINITY;
    if (candidate === query) return 0;
    if (candidate.startsWith(query)) return 1.5 + (candidate.length - query.length) * 0.02;
    if (candidate.includes(query)) return 5 + candidate.indexOf(query) * 0.12;
    const queryTokens = query.split(" ");
    const candidateTokens = candidate.split(" ");
    let total = 0;
    for (const queryToken of queryTokens) {
      let best = tokenScore(queryToken, candidate.replace(/\s/g, ""));
      for (const candidateToken of candidateTokens) best = Math.min(best, tokenScore(queryToken, candidateToken));
      if (!Number.isFinite(best)) return Number.POSITIVE_INFINITY;
      total += best;
    }
    return total + Math.max(0, candidateTokens.length - queryTokens.length) * 0.35;
  }

  function tagMaps(catalog) {
    const tags = new Map(((catalog && catalog.tags) || []).map((tag) => [tag.id, tag]));
    const groups = new Map(((catalog && catalog.tagGroups) || []).map((group) => [group.id, group]));
    return { tags, groups };
  }

  function cloneState(state) {
    return {
      query: (state && state.query) || "",
      sort: (state && state.sort) || "smart",
      addon: (state && state.addon) || "",
      filters: Object.fromEntries(Object.entries((state && state.filters) || {}).map(([group, values]) => [group, Array.isArray(values) ? [...values] : []]))
    };
  }

  function selectedValues(state, group) {
    return Array.isArray(state && state.filters && state.filters[group]) ? state.filters[group] : [];
  }

  function specTag(catalog, id) {
    const tag = tagMaps(catalog).tags.get(id);
    return tag && tag.group === "specialization" ? tag : null;
  }

  function canonicalSpecId(value, classIds, catalog) {
    if (specTag(catalog, value)) return value;
    const aliases = (catalog && catalog.contextResolution && catalog.contextResolution.legacySpecAliasesByClass) || {};
    if (classIds.length === 1 && aliases[classIds[0]] && aliases[classIds[0]][value]) return aliases[classIds[0]][value];
    const matches = new Set();
    Object.values(aliases).forEach((mapping) => {
      if (mapping[value]) matches.add(mapping[value]);
    });
    return matches.size === 1 ? Array.from(matches)[0] : value;
  }

  function canonicalizeLegacySpecs(state, catalog) {
    const next = cloneState(state);
    const specs = selectedValues(next, "specialization");
    if (specs.length) {
      next.filters.specialization = Array.from(new Set(specs.map((value) => canonicalSpecId(value, selectedValues(next, "class"), catalog))));
    }
    return next;
  }

  function resolveContext(state, catalog) {
    const resolved = canonicalizeLegacySpecs(state, catalog);
    const inferred = [];
    const { tags } = tagMaps(catalog);
    const config = (catalog && catalog.contextResolution) || {};

    function add(group, value, source) {
      if (!value || selectedValues(resolved, group).length) return false;
      resolved.filters[group] = [value];
      inferred.push({ group, value, source });
      return true;
    }

    for (let pass = 0; pass < 4; pass += 1) {
      let changed = false;
      const specs = selectedValues(resolved, "specialization");
      if (specs.length === 1) {
        const tag = specTag(catalog, specs[0]);
        if (tag) {
          changed = add("class", tag.classId, "specialization") || changed;
          if (Array.isArray(tag.roleIds) && tag.roleIds.length === 1) changed = add("role", tag.roleIds[0], "specialization") || changed;
        }
      }
      const classes = selectedValues(resolved, "class");
      const roles = selectedValues(resolved, "role");
      if (classes.length === 1 && roles.length === 1 && selectedValues(resolved, "specialization").length === 0) {
        const inferredSpec = config.roleToSpec && config.roleToSpec[classes[0]] && config.roleToSpec[classes[0]][roles[0]];
        changed = add("specialization", inferredSpec, "class-role") || changed;
      }
      if (!changed) break;
    }

    const classes = selectedValues(resolved, "class");
    const specs = selectedValues(resolved, "specialization");
    const roles = selectedValues(resolved, "role");
    const classTag = classes.length === 1 ? tags.get(classes[0]) : null;
    const specializationTag = specs.length === 1 ? specTag(catalog, specs[0]) : null;
    const roleTag = roles.length === 1 ? tags.get(roles[0]) : null;
    let label = "";
    if (classTag && specializationTag) label = `${specializationTag.shortLabel || specializationTag.label} ${classTag.label}`;
    else if (classTag && roleTag) label = `${classTag.label} ${roleTag.label}`;
    else label = (classTag && classTag.label) || (specializationTag && specializationTag.label) || (roleTag && roleTag.label) || "";

    const notes = [];
    inferred.forEach((entry) => {
      const tag = tags.get(entry.value);
      if (!tag) return;
      if (entry.group === "specialization" && entry.source === "class-role" && classTag && roleTag) {
        notes.push(`${tag.shortLabel || tag.label} inferred from ${classTag.label} + ${roleTag.label}.`);
      } else if (entry.group === "role" && entry.source === "specialization" && specializationTag && classTag) {
        notes.push(`${tag.label} inferred from ${specializationTag.shortLabel || specializationTag.label} ${classTag.label}.`);
      } else if (entry.group === "class" && entry.source === "specialization" && specializationTag) {
        notes.push(`${tag.label} inferred from ${specializationTag.label}.`);
      }
    });

    if (classTag && roleTag && !specializationTag) {
      const choices = config.ambiguityChoices && config.ambiguityChoices[classTag.id] && config.ambiguityChoices[classTag.id][roleTag.id];
      if (Array.isArray(choices) && choices.length) {
        const labels = choices.map((id) => specTag(catalog, id)).filter(Boolean).map((tag) => tag.shortLabel || tag.label);
        notes.push(`Choose ${labels.join(labels.length > 2 ? ", " : " or ").replace(/, ([^,]+)$/, ", or $1")} for more specialized setup information.`);
      }
    } else if (classTag && specializationTag && !roleTag && Array.isArray(specializationTag.roleIds) && specializationTag.roleIds.length > 1) {
      const labels = specializationTag.roleIds.map((id) => tags.get(id)?.label).filter(Boolean);
      notes.push(`Choose ${labels.join(" or ")} for more specialized setup information.`);
    }

    return { state: resolved, label, note: Array.from(new Set(notes)).join(" "), inferred };
  }

  function audienceSearchText(audience, catalog) {
    const { tags } = tagMaps(catalog);
    const values = [];
    Object.entries(audience || {}).forEach(([key, ids]) => {
      const group = CONTEXT_KEYS[key];
      (ids || []).forEach((id) => {
        const tag = tags.get(id);
        if (tag) values.push(tag.label, tag.shortLabel || "", ...(tag.searchAliases || []));
        else if (group) values.push(id);
      });
    });
    return values.join(" ");
  }

  function searchableFields(addon, catalog) {
    const { tags } = tagMaps(catalog);
    const fields = [
      { text: addon.name, weight: 0 },
      ...(addon.aliases || []).map((text) => ({ text, weight: 4 })),
      ...(addon.searchTerms || []).map((text) => ({ text, weight: 6 })),
      ...(addon.tags || []).map((id) => {
        const tag = tags.get(id);
        return { text: tag ? [tag.label, tag.shortLabel || "", ...(tag.searchAliases || [])].join(" ") : id, weight: 11 };
      }),
      { text: addon.summary, weight: 18 },
      ...(addon.does || []).map((text) => ({ text, weight: 20 })),
      ...(addon.doesNot || []).map((text) => ({ text, weight: 24 })),
      ...(addon.generalSetup || []).map((text) => ({ text, weight: 27 }))
    ];
    (addon.recommendations || []).forEach((record) => {
      fields.push({ text: audienceSearchText(record.audience, catalog), weight: 9 });
      fields.push({ text: record.summary, weight: 14 });
      fields.push({ text: record.reason, weight: 22 });
    });
    (addon.customizations || []).forEach((record) => {
      fields.push({ text: `${record.title} ${audienceSearchText(record.audience, catalog)}`, weight: 9 });
      fields.push({ text: record.summary, weight: 14 });
      (record.setup || []).forEach((text) => fields.push({ text, weight: 22 }));
      (record.does || []).forEach((text) => fields.push({ text, weight: 20 }));
      (record.doesNot || []).forEach((text) => fields.push({ text, weight: 24 }));
      (record.notes || []).forEach((text) => fields.push({ text, weight: 26 }));
    });
    return fields.filter((field) => normalize(field.text));
  }

  function scoreAddon(addon, query, catalog) {
    const normalizedQuery = normalize(query);
    if (!normalizedQuery) return 0;
    let best = Number.POSITIVE_INFINITY;
    for (const field of searchableFields(addon, catalog)) {
      const score = scoreText(normalizedQuery, field.text);
      if (Number.isFinite(score)) best = Math.min(best, score + field.weight);
    }
    return best;
  }

  function hasAudienceContext(state) {
    return ["class", "specialization", "role", "profession", "activity", "raid", "encounter"]
      .some((group) => selectedValues(state, group).length > 0);
  }

  function audienceMatchesResolved(audience, state, requireEveryDimension = true) {
    if (!hasAudienceContext(state)) return false;
    let compared = 0;
    for (const [key, audienceValues] of Object.entries(audience || {})) {
      if (!Array.isArray(audienceValues) || !audienceValues.length) continue;
      const group = CONTEXT_KEYS[key];
      if (!group) continue;
      const selected = selectedValues(state, group);
      if (!selected.length) {
        if (requireEveryDimension) return false;
        continue;
      }
      compared += 1;
      if (!audienceValues.some((value) => selected.includes(value))) return false;
    }
    return compared > 0;
  }

  function audienceMatches(audience, state, requireEveryDimension = true, catalog) {
    if (typeof requireEveryDimension !== "boolean") {
      catalog = requireEveryDimension;
      requireEveryDimension = true;
    }
    const resolved = catalog ? resolveContext(state, catalog).state : state;
    return audienceMatchesResolved(audience, resolved, requireEveryDimension);
  }

  function audienceSpecificity(audience) {
    return Object.values(audience || {}).reduce((score, values) => score + (Array.isArray(values) && values.length ? 10 - Math.min(values.length, 8) : 0), 0);
  }

  function bestAudienceRecord(records, state, catalog) {
    const resolved = catalog ? resolveContext(state, catalog).state : state;
    return (records || [])
      .filter((record) => audienceMatchesResolved(record.audience, resolved, true))
      .sort((left, right) => audienceSpecificity(right.audience) - audienceSpecificity(left.audience))[0] || null;
  }

  function recommendationFor(addon, state, catalog) {
    return bestAudienceRecord(addon.recommendations, state, catalog);
  }

  function customizationFor(addon, state, catalog) {
    return bestAudienceRecord(addon.customizations, state, catalog);
  }

  function recordAudienceValues(addon, group) {
    const key = Object.keys(CONTEXT_KEYS).find((candidate) => CONTEXT_KEYS[candidate] === group);
    if (!key) return [];
    const values = [];
    for (const collection of [addon.recommendations || [], addon.customizations || []]) {
      collection.forEach((record) => values.push(...((record.audience || {})[key] || [])));
    }
    return values;
  }

  function facetValues(addon, group, catalog) {
    const { tags } = tagMaps(catalog);
    const values = new Set((addon.tags || []).filter((id) => tags.get(id)?.group === group));
    const scope = addon.scope || {};
    if (group === "class") {
      if (scope.universalClasses) (catalog.tags || []).filter((tag) => tag.group === "class").forEach((tag) => values.add(tag.id));
      else (scope.classes || []).forEach((value) => values.add(value));
      recordAudienceValues(addon, group).forEach((value) => values.add(value));
    } else if (group === "specialization") {
      (scope.specs || []).forEach((value) => values.add(value));
      recordAudienceValues(addon, group).forEach((value) => values.add(value));
    } else if (group === "role") {
      (scope.roles || []).forEach((value) => values.add(value));
      recordAudienceValues(addon, group).forEach((value) => values.add(value));
    } else if (group === "profession") {
      (scope.professions || []).forEach((value) => values.add(value));
      recordAudienceValues(addon, group).forEach((value) => values.add(value));
    } else if (group === "activity") {
      (scope.activities || []).forEach((value) => values.add(value));
      recordAudienceValues(addon, group).forEach((value) => values.add(value));
    }
    return Array.from(values);
  }

  function matchesFiltersResolved(addon, state, catalog) {
    const filters = (state && state.filters) || {};
    for (const [group, selected] of Object.entries(filters)) {
      if (!Array.isArray(selected) || !selected.length) continue;
      if (group === "importance") {
        const recommendation = bestAudienceRecord(addon.recommendations, state, null);
        if (!recommendation || !selected.includes(recommendation.importance)) return false;
        continue;
      }
      if (group === "purpose") {
        const recommendation = bestAudienceRecord(addon.recommendations, state, null);
        if (!recommendation || !recommendation.purposes.some((purpose) => selected.includes(purpose))) return false;
        continue;
      }
      const values = facetValues(addon, group, catalog);
      if (!selected.some((value) => values.includes(value))) {
        if (group === "specialization" && addon.scope?.universalSpecs && selected.length) continue;
        return false;
      }
    }
    return true;
  }

  function matchesFilters(addon, state, catalog) {
    return matchesFiltersResolved(addon, resolveContext(state, catalog).state, catalog);
  }

  function filterAndSort(addons, state, catalog) {
    const resolved = resolveContext(state, catalog).state;
    const query = normalize(state && state.query);
    const sort = (state && state.sort) || "smart";
    return (addons || [])
      .map((addon) => ({ addon, score: query ? scoreAddon(addon, query, catalog) : 0, recommendation: bestAudienceRecord(addon.recommendations, resolved, null) }))
      .filter((entry) => matchesFiltersResolved(entry.addon, resolved, catalog))
      .filter((entry) => !query || Number.isFinite(entry.score))
      .sort((left, right) => {
        if (sort === "name") return left.addon.name.localeCompare(right.addon.name);
        if (query && left.score !== right.score) return left.score - right.score;
        const leftRank = left.recommendation ? IMPORTANCE_RANK[left.recommendation.importance] ?? 9 : 9;
        const rightRank = right.recommendation ? IMPORTANCE_RANK[right.recommendation.importance] ?? 9 : 9;
        return leftRank - rightRank || left.addon.name.localeCompare(right.addon.name);
      })
      .map((entry) => ({ ...entry.addon, _searchScore: entry.score, _recommendation: entry.recommendation }));
  }

  function emptyState() {
    return { query: "", filters: {}, sort: "smart", addon: "" };
  }

  function parseUrlState(urlLike, catalog) {
    const url = typeof urlLike === "string" ? new URL(urlLike, "https://example.invalid/guides/addons.html") : urlLike;
    const state = emptyState();
    state.query = url.searchParams.get("q") || "";
    state.sort = url.searchParams.get("sort") === "name" ? "name" : "smart";
    const allowedGroups = new Set((catalog.tagGroups || []).map((group) => group.id));
    allowedGroups.add("importance");
    allowedGroups.add("purpose");
    for (const group of allowedGroups) {
      const parameter = group === "specialization" ? "spec" : group;
      const values = [...url.searchParams.getAll(parameter), ...(parameter !== group ? url.searchParams.getAll(group) : [])]
        .flatMap((value) => value.split(","))
        .map((value) => value.trim())
        .filter(Boolean);
      if (values.length) state.filters[group] = Array.from(new Set(values));
    }
    const hash = new URLSearchParams(url.hash.replace(/^#/, ""));
    state.addon = hash.get("addon") || "";
    return canonicalizeLegacySpecs(state, catalog);
  }

  function stateToUrl(state, currentUrl, catalog) {
    const visible = canonicalizeLegacySpecs(state, catalog);
    const url = new URL(currentUrl || "https://example.invalid/guides/addons.html", "https://example.invalid");
    url.search = "";
    if (normalize(visible.query)) url.searchParams.set("q", visible.query.trim());
    if (visible.sort === "name") url.searchParams.set("sort", "name");
    const groupOrder = [...(catalog.tagGroups || []).map((group) => group.id), "importance", "purpose"];
    groupOrder.forEach((group) => {
      const values = selectedValues(visible, group);
      const parameter = group === "specialization" ? "spec" : group;
      if (values.length) url.searchParams.set(parameter, values.join(","));
    });
    url.hash = visible.addon ? `addon=${encodeURIComponent(visible.addon)}` : "";
    return url;
  }

  function contextDetails(state, catalog) {
    const resolved = resolveContext(state, catalog);
    if (resolved.label) return { label: resolved.label, note: resolved.note, inferred: resolved.inferred, state: resolved.state };
    const { tags } = tagMaps(catalog);
    const firstLabel = (group) => tags.get(selectedValues(resolved.state, group)[0])?.label || "";
    return { label: firstLabel("activity"), note: resolved.note, inferred: resolved.inferred, state: resolved.state };
  }

  function contextLabel(state, catalog) {
    return contextDetails(state, catalog).label;
  }

  const api = {
    normalize,
    editDistance,
    scoreText,
    scoreAddon,
    audienceMatches,
    recommendationFor,
    customizationFor,
    facetValues,
    matchesFilters,
    filterAndSort,
    emptyState,
    parseUrlState,
    stateToUrl,
    contextLabel,
    contextDetails,
    resolveContext,
    hasAudienceContext
  };

  global.AddonSearchCore = api;
  if (typeof module !== "undefined" && module.exports) module.exports = api;
})(typeof window !== "undefined" ? window : globalThis);
'''

TEST_SOURCE = r'''"use strict";

const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const core = require("../assets/addon-search-core.js");
const catalog = JSON.parse(fs.readFileSync(path.join(__dirname, "../data/addons.json"), "utf8"));
const addons = catalog.addons;

function state(query = "", filters = {}, sort = "smart") {
  return { query, filters, sort, addon: "" };
}

function ids(query, filters = {}) {
  return core.filterAndSort(addons, state(query, filters), catalog).map((addon) => addon.id);
}

function first(query, filters = {}) {
  return ids(query, filters)[0];
}

const searchCases = [
  ["healbt", "healbot"],
  ["heal bot", "healbot"],
  ["paly power", "pallypower"],
  ["piss", "protection-is-surprisingly-stupendous"],
  ["thret meter", "omen3"],
  ["boss timer", "deadly-boss-mods"],
  ["cooldown numbers", "omnicc"],
  ["gear stats", "ratingbuster"],
  ["969 trainer", "protection-is-surprisingly-stupendous"]
];

for (const [query, expected] of searchCases) assert.equal(first(query), expected, `${query} should rank ${expected} first`);

const protResults = ids("prot pally");
assert.ok(protResults.includes("pallypower"));
assert.ok(protResults.includes("healbot"));

for (const list of [ids("righteous defense"), ids("righteous defence")]) {
  assert.ok(list.includes("healbot"));
  assert.ok(list.includes("tauntmaster"));
}

const canonicalProtection = { class: ["paladin"], specialization: ["paladin-protection"], role: ["tank"] };
const equivalentProtectionContexts = [
  canonicalProtection,
  { class: ["paladin"], role: ["tank"] },
  { class: ["paladin"], specialization: ["paladin-protection"] }
];
const canonicalIds = ids("", canonicalProtection);
for (const filters of equivalentProtectionContexts) {
  assert.deepEqual(ids("", filters), canonicalIds, `${JSON.stringify(filters)} should resolve to Protection Paladin Tank`);
  assert.deepEqual(ids("", { ...filters, importance: ["essential"] }), ["deadly-boss-mods", "pallypower"]);
}
assert.deepEqual(canonicalIds.slice(0, 2), ["deadly-boss-mods", "pallypower"]);

const pallyPower = addons.find((addon) => addon.id === "pallypower");
const healbot = addons.find((addon) => addon.id === "healbot");
for (const filters of equivalentProtectionContexts) {
  const current = state("", filters);
  assert.equal(core.recommendationFor(pallyPower, current, catalog).importance, "essential");
  assert.equal(core.customizationFor(healbot, current, catalog).id, "protection-paladin");
  assert.equal(core.contextLabel(current, catalog), "Protection Paladin");
}

const paladinTankResolved = core.resolveContext(state("", { class: ["paladin"], role: ["tank"] }), catalog);
assert.deepEqual(paladinTankResolved.state.filters.specialization, ["paladin-protection"]);
assert.match(paladinTankResolved.note, /Protection inferred/);
const paladinProtectionResolved = core.resolveContext(state("", { class: ["paladin"], specialization: ["paladin-protection"] }), catalog);
assert.deepEqual(paladinProtectionResolved.state.filters.role, ["tank"]);
assert.match(paladinProtectionResolved.note, /Tank inferred/);

const fixedInferenceCases = [
  [{ specialization: ["warrior-arms"] }, "warrior", "dps", "Arms Warrior"],
  [{ class: ["priest"], role: ["dps"] }, "priest", "dps", "Shadow Priest"],
  [{ class: ["shaman"], role: ["healer"] }, "shaman", "healer", "Restoration Shaman"],
  [{ class: ["druid"], role: ["tank"] }, "druid", "tank", "Feral Druid"]
];
for (const [filters, expectedClass, expectedRole, expectedLabel] of fixedInferenceCases) {
  const resolved = core.resolveContext(state("", filters), catalog);
  assert.deepEqual(resolved.state.filters.class, [expectedClass]);
  assert.deepEqual(resolved.state.filters.role, [expectedRole]);
  assert.equal(resolved.label, expectedLabel);
}

const ambiguityCases = [
  [{ class: ["warrior"], role: ["dps"] }, /Arms.*Fury/],
  [{ class: ["priest"], role: ["healer"] }, /Discipline.*Holy/],
  [{ class: ["shaman"], role: ["dps"] }, /Elemental.*Enhancement/],
  [{ class: ["druid"], role: ["dps"] }, /Balance.*Feral/],
  [{ class: ["hunter"], role: ["dps"] }, /Beast Mastery.*Marksmanship.*Survival/],
  [{ class: ["mage"], role: ["dps"] }, /Arcane.*Fire.*Frost/],
  [{ class: ["rogue"], role: ["dps"] }, /Assassination.*Combat.*Subtlety/],
  [{ class: ["warlock"], role: ["dps"] }, /Affliction.*Demonology.*Destruction/],
  [{ class: ["death-knight"], role: ["tank"] }, /Blood.*Frost.*Unholy/]
];
for (const [filters, pattern] of ambiguityCases) {
  const resolved = core.resolveContext(state("", filters), catalog);
  assert.equal(resolved.state.filters.specialization, undefined);
  assert.match(resolved.note, pattern);
}

const feralOnly = core.resolveContext(state("", { class: ["druid"], specialization: ["druid-feral"] }), catalog);
assert.equal(feralOnly.state.filters.role, undefined);
assert.match(feralOnly.note, /Tank or DPS/);
const frostDk = core.resolveContext(state("", { class: ["death-knight"], specialization: ["death-knight-frost"] }), catalog);
assert.equal(frostDk.state.filters.role, undefined, "WotLK Frost DK must not silently become Tank or DPS");
assert.match(frostDk.note, /Tank or DPS/);

const paladinTankRaid = ids("", { class: ["paladin"], role: ["tank"], activity: ["raids"] });
assert.ok(paladinTankRaid.includes("pallypower"));
assert.ok(paladinTankRaid.includes("deadly-boss-mods"));
assert.ok(paladinTankRaid.includes("ratingbuster"));
assert.ok(ids("", { role: ["tank"] }).includes("healbot"));
assert.ok(ids("", { activity: ["raids"] }).includes("deadly-boss-mods"));
assert.equal(ids("").length, 9);
assert.equal(ids("", { profession: ["alchemy"] }).length, 0);

const parsedLegacy = core.parseUrlState(
  "https://example.test/guides/addons.html?q=healbt&class=paladin&spec=protection&role=tank#import=ignored&addon=healbot",
  catalog
);
assert.equal(parsedLegacy.query, "healbt");
assert.deepEqual(parsedLegacy.filters.class, ["paladin"]);
assert.deepEqual(parsedLegacy.filters.specialization, ["paladin-protection"]);
assert.deepEqual(parsedLegacy.filters.role, ["tank"]);
assert.equal(parsedLegacy.addon, "healbot");

const serialized = core.stateToUrl(parsedLegacy, "https://example.test/guides/addons.html", catalog);
assert.equal(serialized.searchParams.get("spec"), "paladin-protection");
const restored = core.parseUrlState(serialized, catalog);
assert.deepEqual(restored.filters, parsedLegacy.filters);
assert.equal(restored.addon, "healbot");

const priestState = state("", { class: ["priest"], role: ["healer"] });
assert.equal(core.customizationFor(healbot, priestState, catalog), null);
assert.equal(core.recommendationFor(healbot, priestState, catalog), null);

console.log(`Addon search tests passed: ${searchCases.length} fuzzy cases plus canonical, inferred, ambiguous, URL, and isolation checks.`);
'''


def write_core_and_tests() -> None:
    CORE.write_text(CORE_SOURCE, encoding="utf-8", newline="\n")
    SEARCH_TESTS.write_text(TEST_SOURCE, encoding="utf-8", newline="\n")


def patch_ui() -> None:
    text = UI.read_text(encoding="utf-8")
    old_label = '''    function labelFor(group, id) {\n      if (group === "importance") return importanceMap.get(id)?.label || titleCase(id);\n      if (group === "purpose") return purposeMap.get(id)?.label || titleCase(id);\n      return tagMap.get(id)?.label || titleCase(id);\n    }'''
    new_label = '''    function labelFor(group, id) {\n      if (group === "importance") return importanceMap.get(id)?.label || titleCase(id);\n      if (group === "purpose") return purposeMap.get(id)?.label || titleCase(id);\n      const tag = tagMap.get(id);\n      if (group === "specialization" && tag?.shortLabel) {\n        const selectedClasses = state.filters.class || [];\n        if (selectedClasses.length === 1 && selectedClasses[0] === tag.classId) return tag.shortLabel;\n      }\n      return tag?.label || titleCase(id);\n    }'''
    if old_label not in text:
        raise RuntimeError("Could not find labelFor block")
    text = text.replace(old_label, new_label)
    text = text.replace("core.recommendationFor(addon, state)", "core.recommendationFor(addon, state, catalog)")
    text = text.replace("core.customizationFor(addon, state)", "core.customizationFor(addon, state, catalog)")
    old_banner = '''      const context = core.contextLabel(state, catalog);\n      contextBanner.hidden = !context;\n      contextBanner.textContent = context ? `Showing recommendations for ${context}` : "";'''
    new_banner = '''      const context = core.contextDetails(state, catalog);\n      contextBanner.hidden = !context.label;\n      contextBanner.replaceChildren();\n      if (context.label) {\n        contextBanner.append(make("strong", "", `Showing recommendations for ${context.label}`));\n        if (context.note) contextBanner.append(make("span", "addon-context-note", context.note));\n      }'''
    if old_banner not in text:
        raise RuntimeError("Could not find context banner block")
    text = text.replace(old_banner, new_banner)
    UI.write_text(text, encoding="utf-8", newline="\n")


def patch_css() -> None:
    text = CSS.read_text(encoding="utf-8")
    marker = '''.addon-context-banner {\n  margin-top: 14px;'''
    if marker not in text:
        raise RuntimeError("Could not find context banner CSS")
    addition = '''.addon-context-banner strong { display: block; }\n.addon-context-note {\n  display: block;\n  margin-top: 2px;\n  color: var(--text-muted);\n  font-size: 11px;\n  font-weight: 700;\n}\n'''
    if ".addon-context-note" not in text:
        end = text.index(".addon-results-head", text.index(marker))
        text = text[:end] + addition + text[end:]
    CSS.write_text(text, encoding="utf-8", newline="\n")


def patch_links_and_browser_tests() -> None:
    for path in (TANKADIN_HTML, BROWSER_TESTS):
        text = path.read_text(encoding="utf-8").replace("spec=protection", "spec=paladin-protection")
        path.write_text(text, encoding="utf-8", newline="\n")

    text = BROWSER_TESTS.read_text(encoding="utf-8")
    anchor = '''    assert.equal(await desktop.locator(".addon-badge-essential").count(), 2);\n'''
    addition = '''    assert.equal(await desktop.locator(".addon-badge-essential").count(), 2);\n\n    for (const equivalentUrl of [\n      `${base}/guides/addons.html?class=paladin&role=tank`,\n      `${base}/guides/addons.html?class=paladin&spec=paladin-protection`\n    ]) {\n      await desktop.goto(equivalentUrl, { waitUntil: "networkidle" });\n      await desktop.waitForSelector(".addon-card");\n      assert.match(await desktop.locator("#addon-context-banner").textContent(), /Showing recommendations for Protection Paladin/);\n      const equivalentFirstTwo = await desktop.locator(".addon-card h2").evaluateAll((nodes) => nodes.slice(0, 2).map((node) => node.textContent));\n      assert.deepEqual(equivalentFirstTwo, ["Deadly Boss Mods", "PallyPower"]);\n      assert.equal(await desktop.locator(".addon-badge-essential").count(), 2);\n    }\n\n    await desktop.goto(`${base}/guides/addons.html?class=warrior&role=dps`, { waitUntil: "networkidle" });\n    await desktop.waitForSelector("#addon-context-banner:not([hidden])");\n    assert.match(await desktop.locator("#addon-context-banner").textContent(), /Choose Arms or Fury/);\n'''
    if anchor not in text:
        raise RuntimeError("Could not find browser test anchor")
    text = text.replace(anchor, addition, 1)
    BROWSER_TESTS.write_text(text, encoding="utf-8", newline="\n")

    html = ADDONS_HTML.read_text(encoding="utf-8").replace("20260722-addons-v1", "20260722-addons-v2")
    ADDONS_HTML.write_text(html, encoding="utf-8", newline="\n")


def main() -> None:
    migrate_catalog()
    write_core_and_tests()
    patch_ui()
    patch_css()
    patch_links_and_browser_tests()
    print("Applied class-qualified specialization IDs and context inference rules.")


if __name__ == "__main__":
    main()
