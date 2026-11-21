#!/usr/bin/env python3
"""No Skips - Instagram product post generator.

Rebuilds the product posts (4x5 feed at 1080x1350, 9x16 story at 1080x1920)
in the established dark-panel layout: render on top, charcoal panel below with
code / kind, name, tagline, phase chip, price or COMING SOON, footer line and
the NO SKIPS wordmark. The 9x16 version adds the blueprint thumbnail.

Run (from anywhere):
    python3 tools/posts/make_posts.py                 # every product in PRODUCTS
    python3 tools/posts/make_posts.py C1 A3           # only these codes
    python3 tools/posts/make_posts.py --out /some/dir # choose the output folder
    python3 tools/posts/make_posts.py --fonts site    # Archivo / Instrument Sans / DM Mono
                                                      # (default "legacy" = Poppins + DejaVu Mono,
                                                      #  which matches the posts already on Drive)

To change a post, edit its row in PRODUCTS (or the PHASES defaults) and rerun.
Needs Pillow only. Fonts are bundled in tools/posts/fonts (all open licences).
Copy rule: no em dashes or en dashes anywhere, prices as "Rs 1,299".
"""
import argparse
import os
import sys

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
IMG = os.path.join(REPO, "img")
FONTS = os.path.join(HERE, "fonts")

W = 1080
PANEL = (18, 17, 15)        # charcoal panel
IVORY = (243, 241, 236)     # headline text on the panel
SOFT = (214, 210, 204)      # tagline text
MUTED = (147, 146, 142)     # mono labels
RED = (212, 40, 40)         # accent on dark
LINE = (59, 58, 56)         # hairline on dark

# ---------------------------------------------------------------- phases
# chip: small outlined label top right (None = no chip)
# right: "price" shows the price, "soon" shows COMING SOON
# footer: line next to the red bar
PHASES = {
    "preorder": {"chip": "PRE-ORDER", "right": "price",
                 "footer": "Pre-order on WhatsApp. Link in bio."},
    "second":   {"chip": "SECOND DROP", "right": "soon",
                 "footer": "Second drop. Opens before Valentine's."},
    "soon":     {"chip": None, "right": "soon",
                 "footer": "Coming soon. Link in bio."},
    "live":     {"chip": None, "right": "price",
                 "footer": "Order on WhatsApp. Link in bio."},
}

# ---------------------------------------------------------------- products
# One row per product. Any of chip / footer / right can be set on a row to
# override the phase default. image and blueprint are file names in img/
# (without .webp). note is an optional small mono line (keep it short).
PRODUCTS = [
    # --- first phase: limited pre-order -------------------------------
    {"code": "C1", "slug": "Vol-01-The-Studio", "name": "Vol. 01: The Studio",
     "kind": "Collector set", "tagline": "Six pieces. Fifty sets. No repress.",
     "price": 1999, "phase": "preorder", "image": "studio_set",
     "note": "FIRST BATCH: 15 SETS. EDITION OF 50."},
    {"code": "C2", "slug": "Studio-Mini", "name": "Studio Mini",
     "kind": "Single piece", "tagline": "Start with one.",
     "price": 399, "phase": "preorder", "image": "studio_mini"},
    {"code": "C3", "slug": "Gig-Coin", "name": "Gig Coin",
     "kind": "Show token", "tagline": "You were there. Carry the proof.",
     "price": 499, "phase": "preorder", "image": "coin"},
    {"code": "A3", "slug": "Rail", "name": "Rail",
     "kind": "Wristband display", "tagline": "Every band earned its place.",
     "price": 1299, "phase": "preorder", "image": "rail"},
    {"code": "D2", "slug": "Tape-Case", "name": "Tape Case",
     "kind": "Small storage box", "tagline": "A tape that holds your small things.",
     "price": 849, "phase": "preorder", "image": "cassettebox"},
    {"code": "D5", "slug": "Hold", "name": "Hold",
     "kind": "Headphone stand", "tagline": "Hang them up properly.",
     "price": 2199, "phase": "preorder", "image": "headphonestand"},
    # --- second drop ---------------------------------------------------
    {"code": "A1", "slug": "Track-Plate", "name": "Track Plate",
     "kind": "Scannable song display", "tagline": "Scan it. It still hits.",
     "price": 1799, "phase": "second", "image": "plate"},
    {"code": "A5", "slug": "Track-Tag", "name": "Track Tag",
     "kind": "Song keytag", "tagline": "One song. Always on you.",
     "price": 549, "phase": "second", "image": "songtag"},
    {"code": "C4", "slug": "Side-A", "name": "Side A",
     "kind": "Mixtape set of 4", "tagline": "Four songs that explain you.",
     "price": 1299, "phase": "second", "image": "standees"},
    # --- moved to coming soon ------------------------------------------
    {"code": "B1", "slug": "Stack", "name": "Stack",
     "kind": "Pick amp with drawer", "tagline": "Always one pick ahead.",
     "price": 1399, "phase": "soon", "image": "amp"},
    {"code": "D8", "slug": "B-Side", "name": "B-Side",
     "kind": "Catch-all tray", "tagline": "Everything you drop at the door.",
     "price": 1099, "phase": "soon", "image": "bside"},
    {"code": "D14", "slug": "Dock", "name": "Dock",
     "kind": "Two-controller dock for Hold", "tagline": "Headphones up top. Both controllers below.",
     "price": 999, "phase": "soon", "image": "dock_use", "note": "FITS HOLD. THE FIRST ADD-ON."},
    {"code": "D1", "slug": "Wedge", "name": "Wedge",
     "kind": "Phone stand", "tagline": "A stage monitor for your phone.",
     "price": 899, "phase": "soon", "image": "wedge_phone"},
    {"code": "D10", "slug": "Eject", "name": "Eject",
     "kind": "Slim card wallet", "tagline": "Push the tab. Cards fan out. Stay put.",
     "price": 599, "phase": "soon", "image": "eject_open"},
    # Add further products here in the same shape, for example:
    # {"code": "D7", "slug": "Channel", "name": "Channel", "kind": "Modular desk set",
    #  "tagline": "Your desk, mixed down.", "price": 1799, "phase": "soon", "image": "channel"},
]

# ---------------------------------------------------------------- fonts
FONTSETS = {
    "legacy": {"bold": ("Poppins-Bold.ttf", None), "body": ("Poppins-Regular.ttf", None),
               "mono": ("DejaVuSansMono.ttf", None), "k": 1.0},
    "site":   {"bold": ("Archivo-VF.ttf", {"wght": 800, "wdth": 112}),
               "body": ("InstrumentSans-VF.ttf", {"wght": 400, "wdth": 100}),
               "mono": ("DMMono-Regular.ttf", None), "k": 1.0},
}
_AXIS_ORDER = {"Archivo-VF.ttf": ("wght", "wdth"), "InstrumentSans-VF.ttf": ("wdth", "wght")}


def load_font(file, size, axes=None):
    f = ImageFont.truetype(os.path.join(FONTS, file), int(round(size)))
    if axes:
        f.set_variation_by_axes([axes[a] for a in _AXIS_ORDER[file]])
    return f


class Type:
    def __init__(self, name):
        self.set = FONTSETS[name]

    def __call__(self, role, size):
        file, axes = self.set[role]
        return load_font(file, size, axes)


def inr(n):
    return "Rs {:,}".format(int(n))


def check_copy(*texts):
    for t in texts:
        if t and any(ch in t for ch in "–—"):
            raise ValueError("dash found in copy: %r" % t)


def cover(path, w, h):
    """Scale to cover w x h, centre crop."""
    im = Image.open(path).convert("RGB")
    s = max(w / im.width, h / im.height)
    im = im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS)
    x = (im.width - w) // 2
    y = (im.height - h) // 2
    return im.crop((x, y, x + w, y + h))


def text_top(d, xy, text, font, fill, anchor="l"):
    """Draw text so the top of its ink sits at xy[1]; anchor l or r on xy[0]."""
    b = font.getbbox(text)
    x = xy[0] - b[0] if anchor == "l" else xy[0] - b[2]
    d.text((x, xy[1] - b[1]), text, font=font, fill=fill)
    return b[2] - b[0]


def fit_font(T, role, size, text, max_w):
    f = T(role, size)
    while f.getbbox(text)[2] - f.getbbox(text)[0] > max_w and size > 20:
        size -= 2
        f = T(role, size)
    return f


def render(p, ratio, T):
    ph = dict(PHASES[p["phase"]])
    for k in ("chip", "footer", "right"):
        if k in p:
            ph[k] = p[k]
    check_copy(p["name"], p["tagline"], p["kind"], ph["footer"], ph.get("chip"), p.get("note"))

    if ratio == "4x5":
        H, top = 1350, 860
        bar_y, foot_y, wm_y, ul_y = 1266, 1292, 1262, 1296
    else:
        H, top = 1920, 1080
        bar_y, foot_y, wm_y, ul_y = 1810, 1836, 1810, 1844

    im = Image.new("RGB", (W, H), PANEL)
    im.paste(cover(os.path.join(IMG, p["image"] + ".webp"), W, top), (0, 0))
    d = ImageDraw.Draw(im)

    # code / kind
    text_top(d, (60, top + 41), "%s  /  %s" % (p["code"], p["kind"].upper()), T("mono", 24), MUTED)

    # right column: chip, then price or COMING SOON
    right_w = 0
    if ph["chip"]:
        f = T("mono", 21)
        tw = f.getbbox(ph["chip"])[2] - f.getbbox(ph["chip"])[0]
        x1, x0 = 1020, 1020 - tw - 30
        y0 = top + 41
        d.rectangle((x0, y0, x1, y0 + 33), outline=RED, width=2)
        text_top(d, (x0 + 15, y0 + 9), ph["chip"], f, RED)
    if ph["right"] == "price":
        right_w = text_top(d, (1019, top + 97), inr(p["price"]), T("bold", 52), RED, "r")
    else:
        right_w = text_top(d, (1019, top + 93), "COMING SOON", T("bold", 30), IVORY, "r")

    # name and tagline
    name_font = fit_font(T, "bold", 76, p["name"], 1019 - right_w - 40 - 61)
    b = name_font.getbbox("H")
    d.text((60 - name_font.getbbox(p["name"])[0], top + 103 - b[1]), p["name"], font=name_font, fill=IVORY)
    tag_font = fit_font(T, "body", 34, p["tagline"], 960)
    b = tag_font.getbbox("H")
    d.text((60, top + 188 - b[1]), p["tagline"], font=tag_font, fill=SOFT)

    # optional note and (story only) the drawing block
    if ratio == "4x5":
        if p.get("note"):
            text_top(d, (61, top + 262), p["note"], T("mono", 22), MUTED)
    else:
        bp = os.path.join(IMG, "bp_%s.webp" % p.get("blueprint", p["code"]))
        if os.path.exists(bp):
            d.rectangle((59, 1369, 480, 1790), outline=LINE, width=1)
            im.paste(cover(bp, 420, 420), (60, 1370))
            text_top(d, (511, 1385), "THE DRAWING", T("mono", 22), MUTED)
            f = T("body", 28)
            d.text((510, 1420), "Every piece is drawn", font=f, fill=SOFT)
            d.text((510, 1458), "before it is printed.", font=f, fill=SOFT)
            if p.get("note"):
                d.line((511, 1540, 1019, 1540), fill=LINE, width=1)
                y = 1566
                for part in [s.strip() for s in p["note"].split(".") if s.strip()]:
                    text_top(d, (511, y), part + ".", T("mono", 22), MUTED)
                    y += 36
        elif p.get("note"):
            text_top(d, (61, top + 262), p["note"], T("mono", 22), MUTED)

    # footer: red bar, line, wordmark
    d.rectangle((60, bar_y, 140, bar_y + 3), fill=RED)
    foot_font = fit_font(T, "body", 28, ph["footer"], 760)
    b = foot_font.getbbox("O")
    d.text((59, foot_y + 2 - b[1]), ph["footer"], font=foot_font, fill=IVORY)
    wm = load_font("Poppins-Bold.ttf", 33)   # wordmark is always the logo face
    text_top(d, (1026, wm_y), "NO SKIPS", wm, IVORY, "r")
    d.rectangle((870, ul_y, 1020, ul_y + 5), fill=RED)
    return im


def main():
    ap = argparse.ArgumentParser(description="Regenerate No Skips product posts.")
    ap.add_argument("codes", nargs="*", help="product codes, e.g. C1 A3 (default: all in the table)")
    ap.add_argument("--out", default=os.path.join(HERE, "out"))
    ap.add_argument("--fonts", choices=sorted(FONTSETS), default="legacy")
    ap.add_argument("--ratio", choices=["4x5", "9x16", "both"], default="both")
    a = ap.parse_args()
    T = Type(a.fonts)
    want = [c.upper() for c in a.codes]
    known = {p["code"] for p in PRODUCTS}
    for c in want:
        if c not in known:
            sys.exit("unknown product code %s (known: %s)" % (c, ", ".join(sorted(known))))
    ratios = ["4x5", "9x16"] if a.ratio == "both" else [a.ratio]
    for r in ratios:
        os.makedirs(os.path.join(a.out, r), exist_ok=True)
    for p in PRODUCTS:
        if want and p["code"] not in want:
            continue
        for r in ratios:
            path = os.path.join(a.out, r, "NoSkips_%s_%s_%s.jpg" % (p["code"], p["slug"], r))
            render(p, r, T).save(path, quality=93, subsampling=0, optimize=True)
            print(path)


if __name__ == "__main__":
    main()
