# WotLK Server Guides

Static GitHub Pages site for unofficial WotLK 3.3.5 private server Auction House guides. The guides are made for guild/server Discord sharing and should be treated as player-made starting points, not official or permanent price lists.

## Structure

- `index.html` - main guide hub
- `auction-house.html` - Auction House search and price-guide browser
- `guides/` - individual self-contained HTML guide pages
- `assets/` - shared assets for the guide hub
- `scripts/build-ah-search-index.py` - regenerates the fuzzy AH item search index
- `data/ah-vendor-sections.json` - canonical vendor/source costs and suggested AH buyouts
- `templates/ah-guide/` - shared AH guide navigation and vendor-section templates
- `scripts/render-ah-shared-sections.py` - applies the shared AH blocks to all pricing guides
- `assets/addon-hub-search.js` - powers the main-hub Addon Library search and query handoff
- `README.md` - maintenance notes

## Update Vendor & Convenience Prices

Vendor and fixed-source items use one canonical catalog so duplicate entries stay
identical across guides. Edit `data/ah-vendor-sections.json`, then render the
shared navigation and pricing sections:

```powershell
python scripts/render-ah-shared-sections.py
python scripts/build-ah-search-index.py
```

Verify that both generated layers are current:

```powershell
python scripts/render-ah-shared-sections.py --check
python scripts/build-ah-search-index.py --check
python tests/ah-vendor-pricing.test.py
```

The recorded vendor costs come from the AzerothCore WotLK `item_template`
baseline identified in the data file. Hellscream may customize availability or
cost, so unusual values should still be checked in game before repricing large
quantities.

## Update The AH Search Index

The main-hub and Auction House searches read a generated index of every item row in the AH guides. The generator discovers those guides from `auction-house.html`. Regenerate it after adding, removing, renaming, or repricing AH items:

```powershell
python scripts/build-ah-search-index.py
```

Verify that the committed index is current:

```powershell
python scripts/build-ah-search-index.py --check
```

Search results link to the exact item row. Every AH guide therefore loads `assets/ah-search.js`, which handles the row highlight after navigation.

## Add A New Guide

1. Save the guide HTML in `guides/`.
2. Use a clean lowercase kebab-case filename, such as `alchemy-materials-ah-price-guide.html`.
3. Keep the guide self-contained unless it intentionally uses a shared asset.
4. Add AH pricing guides to `auction-house.html`; add gameplay or reference guides to `index.html`.
5. Include the standard player-made disclaimer near the bottom of the guide.
6. Use public wording such as `our server`, `this server`, or `the server`. Avoid second-person server wording.

## Rename Files Safely

1. Rename the file in `guides/` using lowercase kebab-case.
2. Update the matching link in `auction-house.html` or `index.html`.
3. Search the repo for the old filename and update any remaining references.
4. Open the hub locally and click the renamed guide link.

## Preview Locally

From the repo root:

```powershell
python -m http.server 8000
```

Then open:

```text
http://localhost:8000/
```

You can also open `index.html` directly in a browser, but the local server is closer to how GitHub Pages serves the site.

## Publish With GitHub Pages

This repo is prepared to publish from the `main` branch using the root folder.

If GitHub Pages is not enabled yet:

1. Open the GitHub repository.
2. Go to `Settings`.
3. Go to `Pages`.
4. Under `Build and deployment`, choose `Deploy from a branch`.
5. Choose branch `main`.
6. Choose folder `/ (root)`.
7. Click `Save`.

The site URL should be:

```text
https://leblackstock.github.io/wotlk-server-guides/
```

## Pre-Publish Checks

- Every guide link on `index.html` and `auction-house.html` should open.
- Every AH guide should have the canonical `Guide Hub` and `AH Hub` buttons.
- No public-facing page should use second-person server wording.
- No local machine paths should appear in published files.
- Filenames should stay clean, lowercase, and Discord-friendly.
