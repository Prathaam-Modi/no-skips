NO SKIPS - INSTAGRAM POST GENERATORS

Product posts:    python3 tools/posts/make_posts.py [CODES...] [--out DIR] [--fonts legacy|site]
Soft launch kit:  python3 tools/posts/make_softlaunch.py [1-9...] [--out DIR] [--bench-photo PHOTO.jpg]

make_posts.py draws the product posts (4x5 at 1080x1350 and 9x16 at 1080x1920) from the
PRODUCTS table at the top of the file: one row per product with code, name, kind, tagline,
price, phase and image. The PHASES table sets the chip, the price or COMING SOON, and the
footer for each phase (preorder, second, soon, live). Change a row, rerun, upload.
Default output is tools/posts/out (not for committing). Needs Python 3 and Pillow.
Default fonts are "legacy" (Poppins + DejaVu Sans Mono) so new posts match the ones already
on Drive; "--fonts site" uses Archivo, Instrument Sans and DM Mono. Fonts are in fonts/.

make_softlaunch.py draws the nine soft launch posts and their story versions. Post 6 is a
template with a photo slot until you pass --bench-photo with a real photo.

Copy rules: no em dashes or en dashes, prices as "Rs 1,299", no stock or delivery claims.
