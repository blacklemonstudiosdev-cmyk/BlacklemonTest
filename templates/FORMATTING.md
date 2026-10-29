# Adding content to BlackLemon Studios

Everything is folder-based. After you add or edit files, run:

    python3 scripts/build.py

That regenerates `data/data.js`, which the site reads. Then commit
everything (including `data/data.js`) to GitHub.

Keep JSON punctuation exactly as in the templates: the `{` `}`, the
`"`, the `:` and the `,`. Replace only the text. Check at
https://jsonlint.com if unsure.

---

## Product — folder in `products/`

```
products/my-product/
  text.json        copy from templates/product-website.json OR product-app.json
                   (Coming Soon versions: product-website-coming-soon.json /
                    product-app-coming-soon.json)
  mockup.png       the big UI image shown on the product page
  card1/           optional cards (any folder names, shown in order)
    text.json      copy from templates/card.json
    image.png
  card2/
    text.json
    image.png
```

- `type`: `"website"` (one "Open ..." button to `url`) or `"app"`
  (Mac Silicon/Intel dropdown + Windows button, from `mac` / `windows`).
- `font`: the title font (see "Choosing the title font" below). Leave it
  `""` to use the default site font.
- `fontWeight`: optional weight number for the title, e.g. `200` (thin),
  `400` (normal), `700` (bold). Leave `""` for the font's default.
- `status`: `"Available Now"` or `"Coming Soon"` (Coming Soon hides the
  buttons and shows a Coming Soon tag).
- `order`: lower numbers appear first.

### Choosing the title font

Three ways, pick one:

1. **Built-in font** — put one of these names in `font`, already styled:
   `nexus`, `blencrypt`, `waveform`, `imagetailor`, `revisionary`,
   `lemonstudio`.

2. **A web font (Google Fonts, Fontshare, etc.)** — add that font's
   `<link ...>` into the `<head>` of `index.html` (one line, copied from
   the font's site), then put the font's family name in `font`, e.g.
   `"font": "Boska"`. Set `fontWeight` to the weight you loaded.

3. **Your own font file** — drop a `.ttf`, `.otf`, `.woff` or `.woff2`
   file into the product's folder, and put its name in `font` (with or
   without the extension), e.g. file `MyFont.ttf` -> `"font": "MyFont"`.
   The build wires it up automatically. Set `fontWeight` if needed.

## Blog — folder in `blogs/`

```
blogs/my-post/
  blog.json        copy from templates/blog.json (any .json name)
  image-1.png      thumbnail + top image
  image-2.png      middle image
  image-3.png      end image
```

Reader layout: image-1 -> title -> author / date / year -> part of the
blog -> image-2 -> the rest -> image-3. Images are optional. Inside
`body`, a blank line starts a new paragraph; a line starting with `## `
is a subheading.

## Download counter (apps only)

Drop a `counter.json` file into an app's product folder to show a live
download counter above that product's cards:

```
products/my-app/
  counter.json     copy from templates/counter.json  -> { "baseline": 23 }
```

- `baseline` is the number it starts at right now (your current total).
- The build reads the real download counts of the app's GitHub release
  files (from the Mac/Windows links in text.json), anchors them to
  `baseline`, and the number grows as real downloads come in.
- It never touches your product cards — it renders as its own element.
- Refreshes when the GitHub Action runs (see .github/workflows/build.yml).
  Remove the file to remove the counter.
