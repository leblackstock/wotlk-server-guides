(function (global) {
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
