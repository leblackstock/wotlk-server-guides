# Class Color System Workflow

Use this workflow whenever adding a class color reference, revising an approved
class or specialization palette, or extending a class page to cover another
specialization. It turns the internal color references into a repeatable,
testable design process instead of a collection of one-off pages.

The goal is a complete class family: one shared class identity, every Wrath
specialization, a small set of recurring mechanic roles per specialization,
protected global semantics, an integrated Color Reference Hub entry, automated
regression coverage, and verified rendered behavior.

## Non-Negotiable Rules

- Keep every Wrath specialization for a class on one combined class reference
  page. Do not approve an isolated spec palette without showing its siblings.
- Treat existing colors, official class colors, and thematic associations as
  candidates—not automatic approval. Audit readability and semantic collisions.
- Shared production tokens belong in `assets/guide-color-system.css`. Reference
  layout belongs in `assets/internal-color-reference.css`; class-specific
  reference selectors belong in `assets/<class>-color-reference.css`.
- Class, specialization, mechanic, status, section, item-quality, and socket
  colors have different owners. Never reuse a visually similar token as a
  shortcut across those layers.
- Color is never the only carrier of meaning. Preserve labels, borders,
  position, icons, focus state, and explicit status or role wording.
- An approved internal palette does not authorize applying it to live guides,
  generators, Hub cards, or configs outside the internal color-reference site.
  Production rollout and publishing are separate user decisions.
- Preserve unrelated worktree changes. Record the starting Git state and keep
  the color batch narrow.

## 1. Open a Work Order

Copy [`docs/class-color-system-work-orders/_template.md`](class-color-system-work-orders/_template.md)
to `docs/class-color-system-work-orders/YYYY-MM-DD-<class>.md`.

Record before editing:

- class name and all Wrath specialization names;
- whether each specialization already has a live guide, draft, config, visual
  specimen, or no implementation;
- every existing class, spec, and mechanic token;
- all reference pages, stylesheets, and tests that form the current pattern;
- the current unstaged and staged file lists;
- whether production rollout or publication has been authorized.

Keep the work order current as each gate passes. Do not mark a palette approved
while a quantitative, integration, or browser check remains unresolved.

## 2. Gate A — Define the Semantic Model

Before choosing hex values, write the ownership model:

1. **Class identity** — broad framing shared by every specialization.
2. **Specialization identity** — selected navigation, spec-only labels, active
   controls, and technical emphasis.
3. **Mechanic lanes** — two to four concepts taught repeatedly by that spec.
4. **Fixed meanings** — global status, section, item-quality, and socket colors
   that the class system must not replace.
5. **Role or form labels** — explicit text and structure for cases such as
   tank/DPS or Cat/Bear; roles do not silently become extra specializations.

Mechanic lanes describe recurring decisions, not individual spells. Reuse a
specialization accent for its central mechanic only when the page documents
that ownership explicitly.

## 3. Gate B — Build and Audit the Palette

Every class and specialization identity needs:

- `accent`, `soft`, and `deep` hex values;
- `rgb` and `deep-rgb` channel values;
- a plain-language name and intended component ownership.

Every mechanic lane needs `accent`, `soft`, and `rgb` values. Then run the same
quantitative checks used by the class regression test:

- every class, specialization, and mechanic accent: at least `5.5:1` contrast
  against `--surface-card` (`#121820`);
- class plus specialization identities: at least `0.14` pairwise OKLab
  distance;
- specialization identities: at least `0.10` pairwise distance under both
  saved red-green color-vision simulations;
- mechanic lanes within one specialization: at least `0.085` pairwise OKLab
  distance, with `0.10` as the target for new work.

Also compare every proposed accent against:

- `--status-success`, `--status-warning`, `--status-danger`, and
  `--status-info`;
- Addons and Auction House section identities;
- item-quality and socket colors;
- existing class and specialization identities with the same hue family.

A close thematic relationship may remain only when token ownership is
different, the values are not identical, labels and structure carry the
meaning, and the class page documents the collision boundary explicitly.

## 4. Gate C — Implement the Canonical System

Update in this order:

1. Add class, specialization, mechanic, RGB, and deep-RGB tokens to
   `assets/guide-color-system.css`.
2. Add `[data-guide-class]` and `[data-guide-spec]` mappings in the same file.
3. Add `assets/<class>-color-reference.css` for the reference-page theme,
   Color Reference Hub card, and all spec-card mappings.
4. Add `internal/<class>-color-system.html` with:
   - `noindex, nofollow`;
   - one shared navigation bar;
   - the approved banner and compact-card identity-gradient specimens;
   - class identity and boundary;
   - palette audit;
   - all specialization cards;
   - two to four named mechanic cards for every specialization;
   - semantic boundaries;
   - a complete usage matrix;
   - correct previous/next pager links;
   - an explicit implementation status.
5. Add the identity-gradient mapping to
   `assets/internal-color-reference.css`.
6. Bump the cache key for every changed shared stylesheet and update every
   canonical internal reference page and exact-key regression assertion.

Do not add live guide colors, configs, generated pages, or public Guide Hub
cards during this gate unless the user separately authorized production
rollout.

## 5. Gate D — Update the Color Reference Hub

The class is not integrated until all of these are true:

- `internal/color-reference.html` loads the class reference stylesheet;
- the reference directory has one class card with an accurate status;
- every canonical reference page links the class exactly once in the shared
  navigation and in the same order;
- the previous and next class pagers form an unbroken sequence;
- the class page shows both approved identity-gradient strengths;
- the Hub and class page request cache-safe shared and class-specific assets.

When adding a class between two existing pages, update both neighboring pagers.

## 6. Gate E — Add Automated Coverage

Create or extend `tests/<class>-color-system.test.js`. At minimum, assert:

- every declared token and RGB value;
- contrast, normal-vision separation, and color-vision simulation thresholds;
- every required section and exactly one card for each specialization;
- two to four mechanic cards for every specialization and matching CSS token
  use;
- explicit text for every close semantic boundary;
- reference stylesheet mappings for the body, Hub card, and all specs;
- the gradient mapping, two specimens, and shared cache keys;
- one Hub card, shared navigation coverage, and neighboring pager links.

Add the page to the shared identity-gradient regression list and add the class
test to `npm run test:color-system`. A test must fail when a future class is an
orphan page, a spec is omitted, a token drifts, or cache wiring is incomplete.

## 7. Gate F — Validate the Rendered Reference

Run the focused tests first, then the complete suite:

```powershell
npm run test:color-system
npm run test:guide-banner
npm test
git diff --check
```

Scan every edited text file as strict UTF-8. Reject replacement characters and
known mojibake sequences.

Serve the repo locally and inspect both the Hub and new class page at desktop
and mobile widths. Record:

- exact computed class and spec values;
- both gradient specimens and their distinct strengths;
- all spec and mechanic swatches;
- navigation, Hub card, jump links, and pager links;
- keyboard focus visibility;
- no horizontal overflow;
- no console errors or failed local asset requests.

Do not claim mobile validation unless the reported browser viewport actually
matches the requested width.

## 8. Gate G — Accept and Hand Off

The internal color system is complete locally only when:

- all Wrath specs and their recurring mechanics are present;
- the palette passes the quantitative and semantic-collision gates;
- the Hub, navigation, pagers, gradients, and cache keys are integrated;
- focused, full-suite, UTF-8, diff, desktop, and mobile checks pass;
- the work order records exact results and remaining limitations;
- production rollout and publication status are explicit.

Report the chosen palette, semantic boundaries, files, tests, browser results,
and whether the work is local-only. If production rollout was not authorized,
stop before changing live guides or public Guide Hub cards.

## 9. Production Rollout and Publishing

Only after explicit authorization:

1. Update the matching spec configs, class/spec styles, renderers, and cache
   keys from the approved tokens.
2. Regenerate every intended guide page; do not hand-edit generated output.
3. Update the footer date on every changed `guides/*.html` page.
4. Run spec-specific audits plus the color, banner, full, UTF-8, diff, desktop,
   mobile, keyboard, and print checks.
5. Stage only the intended class batch, inspect it, commit, push, verify remote
   sync, and confirm the public render.

Publishing remains a separate step even when the internal standard is marked
approved for implementation.
