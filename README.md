# BlackLemon Studios

A data-driven static site. All content (products, cards, blogs, images)
lives in folders; a small build step turns those folders into
`data/data.js`, which `index.html` reads.

## Deploy
Push the whole folder to your GitHub repo (everything sits at the repo
root, exactly like your current setup) and deploy on Vercel. No build
configuration is required on Vercel — you commit the generated
`data/data.js` yourself (see below).

## The one command you need
After adding or editing anything in `products/` or `blogs/`, run:

    python3 scripts/build.py

That regenerates `data/data.js`. Commit `data/data.js` along with your
new files. (Python 3 only, no packages to install.)

## Adding content
See `templates/FORMATTING.md` for the full guide. In short:

- **A website product:** copy `templates/product-website.json` to
  `products/<slug>/text.json`, add `mockup.png`, optional `cardN/` folders.
- **An app product** (Mac Silicon/Intel + Windows buttons): copy
  `templates/product-app.json`. Put the real Windows link in the
  `windows` field when it's ready — until then leave
  `REPLACE_WITH_WINDOWS_LINK` and the Windows button shows as disabled.
- **A blog:** copy `templates/blog.json` to `blogs/<slug>/blog.json`,
  add `image-1.png`, `image-2.png`, `image-3.png`.

Then run the build and commit.

## Things to replace
- `products/nexus/text.json` → `windows` (currently the placeholder).
- `products/bl-encrypt/card1` and `card2` → your real card text/images.
- `products/slate/mockup.png` → a real mockup when slate. is ready.
- `products/nexus/card1|card2/image.png` and any other placeholder images.
- `blogs/welcome/` → delete it whenever (it's just a demo).

## Fonts available for a product's `font` field
`nexus`, `slate`, `blencrypt`, `waveform`, `imagetailor`.
