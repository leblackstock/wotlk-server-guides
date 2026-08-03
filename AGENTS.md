# Repository Rules

## AH Profession Expansion Plans

- Before adding or expanding profession-crafted AH content, read `docs/ah-profession-plans/README.md` and the matching profession plan.
- Complete the plan's current-price audit before adding crafted rows. Reconcile duplicate prices across guides and verify the ingredient prices used for craft-cost calculations.
- Update the matching plan's status and evidence log as the work advances. Do not treat an unverified price as current.
- Publishing remains a separate step and requires explicit user authorization.

## Guide Footer Dates

- When editing any published guide HTML file under `guides/`, update that page's footer `Updated YYYY-MM-DD` date in the same change.
- Do the footer date update before staging or committing, so the commit reflects the actual page update date.
- Use the current local date in `YYYY-MM-DD` format. If multiple guide pages are changed, update each changed guide's footer.
- Do not change footer dates for untouched pages.
