# Repository Rules

## AH Profession Expansion Plans

- Before adding an individual item or item group to any AH guide, read `docs/ah-item-addition-workflow.md` and create a work order from `docs/ah-item-additions/_template.md`.
- Before adding or expanding profession-crafted AH content, read `docs/ah-profession-plans/README.md` and the matching profession plan.
- Complete the plan's non-circular baseline audit before adding crafted rows. Reconcile duplicate prices across guides and verify the saved ingredient baselines used for craft-cost calculations.
- Active AH listings are competition evidence only and must never automatically set a baseline. Record source type and confidence in `data/ah-price-baselines.json` under `docs/ah-pricing-methodology.md`.
- Before presenting a crafted output as general-use, check `data/ah-profession-use-audit.json`. Hard profession requirements belong in a dedicated restricted section; practical profession tools and inputs must be labeled for their actual buyer. BoP, nontradeable, self-only, conjured, temporary, and invalid outputs stay out of AH listings.
- Within each AH section, order rows by target buyout per item from highest to lowest unless `data/ah-section-ordering.json` records a meaningful fixed progression. After any price or row change, run `python scripts/apply-ah-section-price-order.py` and its `--check` mode.
- Update the matching plan's status and evidence log as the work advances. Do not treat a listing, low-confidence reference, or fallback as verified current value.
- Publishing remains a separate step and requires explicit user authorization.

## Guide Footer Dates

- When editing any published guide HTML file under `guides/`, update that page's footer `Updated YYYY-MM-DD` date in the same change.
- Do the footer date update before staging or committing, so the commit reflects the actual page update date.
- Use the current local date in `YYYY-MM-DD` format. If multiple guide pages are changed, update each changed guide's footer.
- Do not change footer dates for untouched pages.
