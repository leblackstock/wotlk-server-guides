# Class Color System Work Order — <class>

- **Date:** YYYY-MM-DD
- **Status:** planned | in progress | complete locally | rolled out | published
- **Class:**
- **Wrath specializations:**
- **Production rollout authorized:** no
- **Publishing authorized:** no
- **Starting staged files:**
- **Starting unstaged files:**

## Existing-System Audit

- **Reference pattern inspected:**
- **Existing class/spec/mechanic tokens:**
- **Existing live guides/configs/specimens:**
- **Concurrent work to preserve:**

## Gate A — Semantic Model

| Layer | Name | Intended ownership | Must not replace |
|---|---|---|---|
| Class |  |  |  |
| Spec |  |  |  |
| Mechanic |  |  |  |

- **Role/form distinctions that require labels:**

## Gate B — Palette

| Token family | Accent | Soft | Deep | RGB | Deep RGB | Card contrast | Decision |
|---|---|---|---|---|---|---:|---|
| Class |  |  |  |  |  |  | pending |
| Spec |  |  |  |  |  |  | pending |

| Spec | Mechanic | Accent | Soft | RGB | Card contrast | Decision |
|---|---|---|---|---|---:|---|
|  |  |  |  |  |  | pending |

- [ ] Class + spec pairwise OKLab distance is at least 0.14
- [ ] Spec red-green simulation distance is at least 0.10
- [ ] Mechanic pairwise OKLab distance is at least 0.085; 0.10 target reviewed
- [ ] Status, section, item-quality, socket, and existing-class collisions reviewed
- [ ] Every retained close relationship has explicit labels and boundary text

## Gate C — Canonical Implementation

- [ ] Shared tokens and data-attribute mappings
- [ ] Class-specific reference stylesheet
- [ ] Combined class page with every Wrath spec
- [ ] Two to four mechanic lanes per spec
- [ ] Class, audit, specs, mechanics, boundaries, and matrix sections
- [ ] Banner and compact-card gradient specimens
- [ ] Identity-gradient mapping
- [ ] Cache keys updated everywhere the changed shared assets are requested

## Gate D — Color Reference Hub

- [ ] Hub loads the class stylesheet
- [ ] Hub directory card and accurate status
- [ ] Shared nav contains the class exactly once on every canonical page
- [ ] Previous and next pagers form an unbroken sequence
- [ ] Hub and class page request cache-safe assets

## Gate E — Automated Coverage

- [ ] Class token/contrast/separation test
- [ ] All-spec and mechanic-card coverage
- [ ] Semantic-boundary coverage
- [ ] Hub/nav/pager/cache integration coverage
- [ ] Shared gradient regression list
- [ ] `npm run test:color-system` includes the class test

## Gate F — Validation Record

| Command/check | Result | Notes |
|---|---|---|
| `npm run test:color-system` | pending |  |
| `npm run test:guide-banner` | pending |  |
| `npm test` | pending |  |
| Strict UTF-8/mojibake scan | pending |  |
| `git diff --check` | pending |  |
| Desktop Hub and class page | pending |  |
| Mobile Hub and class page | pending |  |
| Computed tokens and gradients | pending |  |
| Navigation, keyboard, overflow, console, assets | pending |  |

## Acceptance and Handoff

- **Approved class identity:**
- **Approved specialization identities:**
- **Approved mechanic lanes:**
- **Semantic boundaries:**
- **Files changed:**
- **Known limitations:**
- **Local/rollout/published status:**
- **Unrelated worktree changes left untouched:**

## Production Rollout Record

Complete only after explicit authorization.

- **Configs/styles/renderers:**
- **Generated guides and footer dates:**
- **Spec-specific release audits:**
- **Commit:**
- **Push and remote sync:**
- **Public render verification:**
