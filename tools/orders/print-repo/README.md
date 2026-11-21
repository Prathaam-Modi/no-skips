# No Skips orders

Private repo that turns one customer order into print-ready files for the Bambu Lab A1.
The admin page presses a button, GitHub runs the "Print files" workflow, and a minute or two later the
files for that order are committed here under `orders/<order number>/`.

## What it does

For each item in the order:

1. Runs the order kit (`kit/code_to_print.py`, rev B) for the product:
   - `plate` - A1 Track Plate: Spotify Code, title and artist.
   - `tag` - A5 Track Tag: Spotify Code on the front; title and artist, or a name, on the back.
   - `alias` - B3 Alias (or B5 Run 50): one name, or two lines. No code.
   - `engrave` - the Engrave add-on (Rs 99) on D1 Wedge, D2 Tape Case, D8 B-Side and D12 Rotary: one or two lines of text cut
     0.6 mm into the base (the face on the print bed), Poppins Bold caps at least 4.0 mm tall (`kit/engrave.py`). The product's other
     parts are copied from `kit/engrave/<ID>/` and the project keeps the first-print settings. `preview.png` shows the base as the
     customer will see it from underneath. Text that is too long, or would shrink below 4.0 mm, fails that job with a message.
   The Spotify Code is downloaded from the song link.
2. Builds a Bambu Studio project (`.3mf`) with every part placed on the bed and set to its AMS Lite slot
   (1 Black, 2 Red, 3 Ivory; accent parts go to slot 2 for a red accent, slot 3 for ivory), with `qty`
   copies spaced out. If they do not fit on one plate, the project gets more plates.
3. Slices it with the Bambu Studio command line (A1, 0.4 mm nozzle, Textured PEI, PLA Basic, the range
   settings: Track Tag 0.12 mm layers solid, Track Plate 0.16 mm with a solid plate, Alias 0.16 mm solid,
   Run 50 0.20 mm solid, 3 walls, gyroid where not solid) and records the print time and grams.
   Slicing is a bonus: if it fails, the project `.3mf` is still there and `summary.json` says why.

A bad item (not a Spotify link, download failed, text too long) does not stop the run. It shows up in
`summary.json` with `"ok": false` and the reason, and the other items are still made.

## Where the files appear

```
orders/NS-1711-AB12/
  summary.json              what happened, per item
  preview.png               all item previews side by side (for the customer email)
  1_tag/                    one folder per item: <n>_<product>
    A5_1_tag_body_BLACK.stl ... the STLs, colour in the name
    preview.png
    NS-1711-AB12_1_tag.3mf          open in Bambu Studio, check, Slice, Print
    NS-1711-AB12_1_tag.gcode.3mf    already sliced (when slicing worked): open and Print
```

`summary.json`:

```json
{"ref": "NS-1711-AB12", "created": "2026-11-17T10:00:00+00:00", "ok": true, "preview": "orders/NS-1711-AB12/preview.png",
 "jobs": [{"n": 1, "product": "tag", "item": "A5 Track Tag", "ok": true,
           "preview": "orders/NS-1711-AB12/1_tag/preview.png",
           "files": ["orders/NS-1711-AB12/1_tag/A5_1_tag_body_BLACK.stl", "..."],
           "sliced": {"time_s": 2811, "grams": 14.1}, "note": "...", "qty": 1, "accent": "red", "plates": 1}]}
```

A failed item has `"ok": false`, `"error": "<reason>"`, `"preview": null`, `"files": []`, `"sliced": null`.
Running the same order number again replaces its folder.

Before printing a coded piece: open `preview.png` (23 bars and the logo on the front, back reads
correctly), and scan the printed code with the Spotify app before shipping.

## Set up (once)

1. **Create the repo.** On GitHub: New repository, owner Prathaam-Modi, name `no-skips-orders`,
   Private, no README, no .gitignore, no licence. Create.
2. **Push these files** (from the folder holding this README):
   ```
   git remote add origin https://github.com/Prathaam-Modi/no-skips-orders.git
   git push -u origin main
   ```
3. **Let the workflow push.** Settings > Actions > General > Workflow permissions: "Read and write
   permissions", Save. (The workflow also asks for `contents: write` itself.)
4. **Give the admin page a key.** GitHub > your picture > Settings > Developer settings > Personal access
   tokens > Fine-grained tokens > Generate new token:
   - Repository access: Only select repositories > `no-skips-orders`.
   - Repository permissions: **Actions: Read and write** (to start the workflow and read its runs),
     **Contents: Read and write** (to read the files). Metadata: Read-only is added by itself.
   - Set an expiry, generate, and paste the token into the admin page settings. Never commit it.

## Run an order by hand

Actions tab > Print files > Run workflow. Fill in:

- `ref`: the order number, `NS-DDMM-XXXX` (for example `NS-1711-AB12`).
- `jobs`: one line of JSON, for example

```json
[{"product":"tag","link":"https://open.spotify.com/track/0VjIjW4GlUZAMYd2vXMi3b","title":"","artist":"","name":"Dimo","line1":"","line2":"","accent":"red","qty":2,"item":"A5 Track Tag"},{"product":"plate","link":"https://open.spotify.com/track/0VjIjW4GlUZAMYd2vXMi3b","title":"Blinding Lights","artist":"The Weeknd","name":"","line1":"","line2":"","accent":"red","qty":1,"item":"A1 Track Plate"},{"product":"alias","link":"","title":"","artist":"","name":"","line1":"Dimo","line2":"Mahtarp","accent":"ivory","qty":1,"item":"B3 Alias"}]
```

Fields: `product` plate, tag or alias; `link` the Spotify share link (Share > Copy song link; needed for
plate and tag); `title`/`artist` (plate, and tag back); `name` (tag back instead of title and artist, or
a one-line alias); `line1`/`line2` (two-line alias); `accent` red or ivory; `qty` 1 to 50; `item` the
shop name (an item starting with "B5" is sliced as Run 50). Limits are the kit's: plate text 40
characters, tag back 18 (name 14), alias lines 10; letters, numbers, spaces and . , ' & ! ? ( ) - only.

The admin page starts the same thing with
`POST /repos/Prathaam-Modi/no-skips-orders/actions/workflows/print-files.yml/dispatches`
and body `{"ref":"main","inputs":{"ref":"NS-1711-AB12","jobs":"<the JSON above as a string>"}}`,
then finds the run by its name `Print files NS-1711-AB12` and reads `orders/NS-1711-AB12/summary.json`.
Runs queue one at a time, so two orders never push at once. Files over 1 MB come back from the contents
API without inline content; fetch them with the `Accept: application/vnd.github.raw` header.

## Run it on a computer

```
pip install -r requirements.txt
python tools/make_order.py --ref NS-1711-TEST --jobs-file jobs.json --svg kit/test_code.svg
```

`--svg` uses that file instead of downloading the code (`kit/test_code.svg` is a dummy and will not scan).
`--no-slice` skips slicing. To slice, point `BAMBU_STUDIO_DIR` at an extracted Bambu Studio AppImage
(the folder with `AppRun` and `bin/`; default `.bambu/squashfs-root`). Do not commit test orders.

## What is in here

- `.github/workflows/print-files.yml` - the workflow.
- `kit/` - the order kit, font and fixed parts (base bar, stripe, straps). Keep it in step with the main repo.
- `tools/make_order.py` - reads the order, runs the kit, builds and slices, writes `summary.json` and the previews.
- `tools/bambu3mf.py` - writes the Bambu project 3MF (layout, slots, settings) and runs the slicer.
- `tools/flatten_profiles.py` - rebuilds `profiles/` from a newer Bambu Studio, if ever needed.
- `profiles/` - A1 machine, PLA Basic and process settings (0.12, 0.16, 0.20) for Bambu Studio 2.02.

Bambu Studio 2.02 (`v02.02.02.56`) is downloaded from its GitHub release on the first run and cached.
If that download ever breaks, set a repository variable `BAMBU_APPIMAGE_URL` (Settings > Secrets and
variables > Actions > Variables) to a direct AppImage link.
