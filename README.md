# No Skips

Music-themed 3D printed collectibles and daily gear, printed to order in Bangalore. Orders via WhatsApp.

Static catalogue site: `index.html` plus `img/`. Served with GitHub Pages.

Product pictures and blueprints in `img/` are generated from the print files in `print-files/`: STLs for every product (one folder each, colour in the file name), drawing sheets, the per-order kit for Spotify Code and name products, and the CAD scripts that build all of it. See `print-files/README_PRINT.txt`.

## Launch phase

`stock.json` drives the whole site and is edited from `admin.html` (no code changes needed):

- `phase`: `"waitlist"` (nothing can be ordered, buttons collect early access interest), `"preorder"` (the launch set is orderable as pre-orders) or `"live"`. A missing or broken file means `"waitlist"`.
- `shipFrom`: text shown in the pre-order phase, for example `"January 2027"`. `preorderNote` is optional.
- `drop.claimed`: Vol. 01 sets sold. `drop.batch`: sets released so far (first batch is 15 of the 50). `drop.batchName` is optional, default `"first batch"`.
- `items`: stock per product id, `{"s":"low","n":3}` or `{"s":"out"}`. A missing id means in stock.

A product in `index.html` with a `soon:"..."` text sits on the bench. A product without it is in the launch set.
Deep links: `#p-<id>` opens a product, `#build-<key>` opens a build guide, `#terms` opens the terms.
