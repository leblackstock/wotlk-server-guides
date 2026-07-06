# WotLK Server Guides

Static GitHub Pages site for unofficial WotLK 3.3.5 private server Auction House guides. The guides are made for guild/server Discord sharing and should be treated as player-made starting points, not official or permanent price lists.

## Structure

- `index.html` - main guide hub
- `guides/` - individual self-contained HTML guide pages
- `assets/` - shared assets for the guide hub
- `README.md` - maintenance notes

## Add A New Guide

1. Save the guide HTML in `guides/`.
2. Use a clean lowercase kebab-case filename, such as `alchemy-materials-ah-price-guide.html`.
3. Keep the guide self-contained unless it intentionally uses a shared asset.
4. Add a link and short description to `index.html`.
5. Include the standard player-made disclaimer near the bottom of the guide.
6. Use public wording such as `our server`, `this server`, or `the server`. Avoid second-person server wording.

## Rename Files Safely

1. Rename the file in `guides/` using lowercase kebab-case.
2. Update the matching link in `index.html`.
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

- Every guide link on `index.html` should open.
- Every guide should have a `Guide Hub` link back to `../index.html`.
- No public-facing page should use second-person server wording.
- No local machine paths should appear in published files.
- Filenames should stay clean, lowercase, and Discord-friendly.
