export const FRESH_80_POLICY_KEYS = Object.freeze([
  "selfContainedTalents",
  "externalRaidBuffsRequired",
  "capsAreProgressionGoals",
  "budgetBeforePremium",
  "raidContentIsLaterProgression"
]);

const expectedPolicy = Object.freeze({
  selfContainedTalents: true,
  externalRaidBuffsRequired: false,
  capsAreProgressionGoals: true,
  budgetBeforePremium: true,
  raidContentIsLaterProgression: true
});

export function validateFresh80Config(config) {
  const errors = [];
  if (config.guideAudience !== "fresh-80") {
    errors.push('guideAudience must be "fresh-80".');
  }

  const policy = config.fresh80Policy;
  if (!policy || typeof policy !== "object" || Array.isArray(policy)) {
    errors.push("fresh80Policy must be an object.");
  } else {
    for (const key of FRESH_80_POLICY_KEYS) {
      if (policy[key] !== expectedPolicy[key]) {
        errors.push(`fresh80Policy.${key} must be ${expectedPolicy[key]}.`);
      }
    }
  }

  if (config.guideTypes?.quickStart !== "Quick Start") {
    errors.push('guideTypes.quickStart must be "Quick Start" for a fresh-80 family.');
  }
  if (!/fresh|new level 80|newly capped/i.test(config.guideDescription || "")) {
    errors.push("guideDescription must identify the fresh or newly capped level-80 audience.");
  }
  if (!/level 80|fresh/i.test(config.pageDescriptions?.quickStart || "")) {
    errors.push("pageDescriptions.quickStart must identify the level-80 starting point.");
  }
  if (/\b(?:raid|icc|lich king|25[- ]?player|25[- ]?man|bis)\b/i.test(config.talent?.name || "")) {
    errors.push("talent.name must describe a self-contained fresh-80 baseline, not a raid-optimized build.");
  }
  if (/raid supplies|assum(?:e|es|ed|ing) (?:a |the )?(?:raid|blood death knight|enhancement shaman)/i.test(config.talent?.summary || "")) {
    errors.push("talent.summary must not require an external raid composition.");
  }

  return errors;
}
