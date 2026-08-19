# Internal Guide References

The `internal/` directory contains authoring references and validation artifacts used to build and review the public guides. These files are not player-facing guide chapters or Guide Hub entries.

Because GitHub Pages publishes from the repository root, HTML files here can still be reachable by direct URL. Do not store secrets, account data, or machine-specific private information in this directory.

## Contents

- `color-reference.html` — hub for combined class color references.
- `*-color-system.html` — class-level palette and semantic-role references.
- `*-visual-system.html` — specialization-level visual specimens used during guide review.
- `*-implementation-checklist.md` — completed or active implementation validation records.
- `*-fresh-80-research.md` — source and decision matrices used to author Fresh-80 guide families.
- `color-system*.html` — shared cross-guide and cross-feature color references.

Player-facing pages belong in [`guides/`](../guides/). Maintainer workflows and saved audit records belong in [`docs/`](../docs/README.md).
