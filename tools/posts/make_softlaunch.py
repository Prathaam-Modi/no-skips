#!/usr/bin/env python3
"""No Skips - soft launch kit generator (9 feed posts + 9 story versions).

Run:
    python3 tools/posts/make_softlaunch.py                    # all 9, both ratios
    python3 tools/posts/make_softlaunch.py 4 7                # only posts 4 and 7
    python3 tools/posts/make_softlaunch.py --out /some/dir
    python3 tools/posts/make_softlaunch.py 6 --bench-photo /path/to/photo.jpg
        # drops a real bench photo into the slot of post 6

Posts alternate charcoal and ivory so the 3 x 3 grid reads as a checkerboard.
Fonts: Archivo (headlines), Instrument Sans (body), DM Mono (specs), bundled
in tools/posts/fonts. Copy rule: no em dashes or en dashes anywhere.
"""
import argparse
import os

from PIL import Image, ImageDraw

from make_posts import IMG, HERE, load_font, cover, check_copy

W, M = 1080, 84
DARK = {"bg": (21, 20, 19), "ink": (239, 234, 224), "muted": (163, 158, 149),
        "line": (62, 58, 53), "red": (214, 44, 44), "name": "dark"}
LIGHT = {"bg": (241, 238, 230), "ink": (21, 20, 19), "muted": (105, 101, 95),
         "line": (198, 193, 184), "red": (200, 32, 43), "name": "light"}


def F_head(size):
    return load_font("Archivo-VF.ttf", size, {"wght": 800, "wdth": 118})


def F_body(size, wght=450):
    return load_font("InstrumentSans-VF.ttf", size, {"wght": wght, "wdth": 100})


def F_mono(size, medium=False):
    return load_font("DMMono-Medium.ttf" if medium else "DMMono-Regular.ttf", size)


class Canvas:
    def __init__(self, ratio, theme, n, label):
        self.ratio, self.t = ratio, theme
        self.H = 1350 if ratio == "4x5" else 1920
        self.im = Image.new("RGB", (W, self.H), theme["bg"])
        self.d = ImageDraw.Draw(self.im)
        top = M if ratio == "4x5" else 250          # stories keep clear of the UI zones
        bot = self.H - M if ratio == "4x5" else self.H - 300
        t = theme
        # top chrome: index, label, mark
        num = "%02d" % n
        self.mono((M, top), num, 22, t["red"], medium=True)
        self.mono((M + 44, top), "/ 09   " + label.upper(), 22, t["muted"])
        logo_mark(self.im, W - M - 40, top - 10, 40, t)
        self.d.line((M, top + 46, W - M, top + 46), fill=t["line"], width=1)
        # bottom chrome
        self.d.line((M, bot - 46, W - M, bot - 46), fill=t["line"], width=1)
        self.mono((M, bot - 22), "@NOSKIPS.IN", 22, t["muted"])
        self.mono((W - M, bot - 22), "BENGALURU", 22, t["muted"], anchor="r")
        self.ct, self.cb = top + 46 + 54, bot - 46 - 54

    # ---- text primitives -------------------------------------------------
    def tracked(self, xy, text, font, fill, track=0.0, anchor="l", draw=True):
        """Text with letter spacing (track in em). xy is the top of the line box."""
        check_copy(text)
        step = track * font.size
        width = font.getlength(text) + step * (len(text) - 1)
        x = xy[0] if anchor == "l" else xy[0] - width
        if draw:
            for i, ch in enumerate(text):
                self.d.text((x + font.getlength(text[:i]) + step * i, xy[1]), ch, font=font, fill=fill)
        return width

    def mono(self, xy, text, size, fill, anchor="l", medium=False):
        return self.tracked(xy, text, F_mono(size, medium), fill, 0.04, anchor)

    def headline(self, y, lines, size, fill=None, track=-0.03, lh=1.02, bar=False, max_w=W - 2 * M):
        """Big tight headline. Returns y after the block. bar=True adds the red bar after the last word."""
        fill = fill or self.t["ink"]
        f = F_head(size)
        while max(self.tracked((0, 0), ln, f, fill, track, draw=False) for ln in lines) > max_w - (size * 0.3 if bar else 0):
            size -= 2
            f = F_head(size)
        asc = f.getbbox("H")[1]
        cap = f.getbbox("H")[3] - asc
        for i, ln in enumerate(lines):
            w = self.tracked((M, y - asc), ln, f, fill, track)
            if bar and i == len(lines) - 1:
                bw = max(10, round(size * 0.13))
                x0 = M + w + size * 0.12
                self.d.rounded_rectangle((x0, y - cap * 0.16, x0 + bw, y + cap * 1.16), radius=bw / 2, fill=self.t["red"])
            y += size * lh if i < len(lines) - 1 else cap
        return y

    def body(self, y, text, size=36, fill=None, max_w=W - 2 * M, x=M, wght=450, lh=1.36):
        check_copy(text)
        f = F_body(size, wght)
        words, lines, cur = text.split(), [], ""
        for w in words:
            trial = (cur + " " + w).strip()
            if f.getlength(trial) <= max_w:
                cur = trial
            else:
                lines.append(cur)
                cur = w
        lines.append(cur)
        for ln in lines:
            self.d.text((x, y), ln, font=f, fill=fill or self.t["ink"])
            y += size * lh
        return y - size * (lh - 1)

    def red_bar(self, y, w=120, h=8):
        self.d.rectangle((M, y, M + w, y + h), fill=self.t["red"])
        return y + h

    def tag(self, x, y, text="3D RENDER"):
        """Small honest label that sits inside a render."""
        f = F_mono(20, True)
        w = f.getlength(text) + 0.04 * 20 * (len(text) - 1)
        self.d.rectangle((x, y - 40, x + w + 28, y), fill=(21, 20, 19))
        self.tracked((x + 14, y - 32), text, f, (239, 234, 224), 0.04)

    def hero(self, y0, y1, name, tag=True):
        """Render cropped to fill the full-width slot between y0 and y1, hairline frame."""
        box = (M, round(y0), W - M, round(y1))
        self.im.paste(cover(os.path.join(IMG, name + ".webp"), box[2] - box[0], box[3] - box[1]), box[:2])
        self.d.rectangle(box, outline=self.t["line"], width=1)
        if tag:
            self.tag(M, box[3])

    def rows(self, y0, y1, items, num_size=22, head_size=54, sub_size=30):
        """Numbered rows with hairlines, spread evenly between y0 and y1."""
        t = self.t
        step = (y1 - y0) / len(items)
        for i, (head, sub) in enumerate(items):
            y = y0 + i * step
            self.d.line((M, y, W - M, y), fill=t["line"], width=1)
            block = head_size + 14 + sub_size * 1.3
            yy = y + (step - block) / 2
            self.mono((M, yy + head_size * 0.3), "%02d" % (i + 1), num_size, t["red"], medium=True)
            f = F_head(head_size)
            self.tracked((M + 96, yy - f.getbbox("H")[1] + 4), head, f, t["ink"], -0.02)
            self.body(yy + head_size + 14, sub, sub_size, t["muted"], max_w=W - 2 * M - 96, x=M + 96)
        self.d.line((M, y1, W - M, y1), fill=t["line"], width=1)


def logo_mark(im, x, y, s, t):
    """The mark: rounded tile, two skip-forward chevrons, red bar. Drawn 4x then scaled."""
    k = 4 * s / 100.0
    tile = Image.new("RGBA", (4 * s, 4 * s), (0, 0, 0, 0))
    d = ImageDraw.Draw(tile)
    d.rounded_rectangle((0, 0, 4 * s - 1, 4 * s - 1), radius=22 * k, fill=t["ink"])
    wd = round(10 * k)
    for x0 in (17, 40):
        pts = [(x0 * k, 30 * k), ((x0 + 18) * k, 50 * k), (x0 * k, 70 * k)]
        d.line(pts, fill=t["bg"], width=wd, joint="curve")
        for px, py in pts:
            d.ellipse((px - wd / 2, py - wd / 2, px + wd / 2, py + wd / 2), fill=t["bg"])
    d.rounded_rectangle((71 * k, 20 * k, 81 * k, 80 * k), radius=5 * k, fill=t["red"])
    tile = tile.resize((s, s), Image.LANCZOS)
    im.paste(tile, (round(x), round(y)), tile)


def wordmark(c, x, y, width):
    """NO SK|PS with the red bar standing in for the I. y is the top of the letters. Returns bottom of bar."""
    u = width / 457.0                      # the site SVG is 457 units wide at a 100 unit em
    f = load_font("Poppins-Bold.ttf", 100 * u)
    top = f.getbbox("N")[1]
    cap = f.getbbox("N")[3] - top
    t = c.t

    def put(text, ink_left):
        b = f.getbbox(text)
        c.d.text((x + ink_left * u - b[0], y - top), text, font=f, fill=t["ink"])

    put("NO", 0)
    put("SK", 178.3)
    put("PS", 341.3)
    bx = x + 311.1 * u
    c.d.rounded_rectangle((bx, y - 16 * u, bx + 17 * u, y + cap + 16 * u), radius=8.5 * u, fill=t["red"])
    return y + cap + 16 * u


# ------------------------------------------------------------------ posts
def p1(r, a):
    c = Canvas(r, DARK, 1, "Hello")
    t = c.t
    mark, ww = 250, W - 2 * M
    cap = 70.2 * ww / 457.0
    block = mark + 90 + cap
    foot = 150
    y = c.ct + (c.cb - foot - c.ct - block) / 2
    logo_mark(c.im, M, y, mark, t)
    wordmark(c, M, y + mark + 90, ww)
    yb = c.cb - foot + 20
    c.red_bar(yb)
    c.headline(yb + 40, ["Some things you do not skip."], 50, track=-0.02)
    c.mono((M, c.cb - 24), "MUSIC YOU CAN HOLD. PRINTED TO ORDER IN BENGALURU.", 22, t["muted"])
    return c.im


def p2(r, a):
    c = Canvas(r, LIGHT, 2, "What it is")
    t = c.t
    rows = [("WHAT", "DESK PIECES, COLLECTIBLES, DAILY GEAR"), ("MATERIAL", "PLA, BLACK WITH IVORY AND RED"),
            ("MADE", "TO ORDER, IN BENGALURU"), ("ORDERS", "WHATSAPP ONLY")]
    table_h = 62 * len(rows)
    y = c.headline(c.ct + 10, ["Music", "you can", "hold."], 196, lh=0.98, bar=True)
    y = c.body(y + 54, "Objects for people who live in their headphones. Drawn first, then printed to order in Bengaluru.", 38)
    y0 = c.cb - table_h
    for i, (k, v) in enumerate(rows):
        yy = y0 + i * 62
        c.d.line((M, yy, W - M, yy), fill=t["line"], width=1)
        c.mono((M, yy + 19), k, 22, t["muted"])
        c.mono((M + 250, yy + 19), v, 22, t["ink"])
    c.d.line((M, c.cb, W - M, c.cb), fill=t["line"], width=1)
    return c.im


def p3(r, a):
    c = Canvas(r, DARK, 3, "The drawing")
    t = c.t
    text_h = 250
    gap = c.cb - text_h - 44 - c.ct
    s = int(min(W - 2 * M, gap))
    bp = Image.open(os.path.join(IMG, "bp_D5.webp")).convert("RGB").resize((s, s), Image.LANCZOS)
    y0 = int(c.ct + (gap - s) / 2)
    c.im.paste(bp, (M, y0))
    c.d.rectangle((M, y0, M + s, y0 + s), outline=t["line"], width=1)
    if W - 2 * M - s >= 130:               # side notes when the sheet leaves a column
        x = M + s + 28
        for i, ln in enumerate(["SHEET", "D5 / V2", "", "HOLD", "HEADPHONE", "STAND", "", "ALL", "DIMS", "IN MM"]):
            c.mono((x, y0 + 4 + i * 32), ln, 20, t["muted"])
    y = c.cb - text_h
    c.red_bar(y)
    y = c.headline(y + 44, ["Drawn before", "it is printed."], 92)
    c.mono((M, c.cb - 24), "EVERY PIECE STARTS AS A DRAWING SHEET. THIS IS D5 HOLD.", 22, t["muted"])
    return c.im


def p4(r, a):
    c = Canvas(r, LIGHT, 4, "Vol. 01: The Studio")
    t = c.t
    text_h = 262
    c.hero(c.ct, c.cb - text_h - 44, "studio_set")
    y = c.cb - text_h
    c.red_bar(y)
    c.headline(y + 44, ["Six pieces. Fifty sets.", "No repress."], 78)
    c.mono((M, c.cb - 24), "COLLECTOR SET. EDITION OF 50. FIRST BATCH: 15 SETS.", 22, t["muted"])
    return c.im


def p5(r, a):
    c = Canvas(r, DARK, 5, "Design rules")
    y = c.headline(c.ct + 10, ["The rules."], 150, bar=True)
    c.rows(y + 64, c.cb, [
        ("Texture is the material.", "Filament only. No paint, no stickers."),
        ("The red bar does the work.", "One accent. It marks the part that matters."),
        ("One joint.", "One way for parts to fit. Learn it once."),
        ("No tools.", "Parts go together by hand. No glue."),
    ])
    return c.im


def p6(r, a):
    c = Canvas(r, LIGHT, 6, "On the bench")
    t = c.t
    y = c.headline(c.ct + 10, ["On the bench."], 124, bar=True)
    y = c.body(y + 40, "Every design gets test printed and fit checked before it goes on sale. Nothing skips the bench.", 36)
    y0, y1 = round(y + 48), round(c.cb - 64)
    box = (M, y0, W - M, y1)
    if a.bench_photo:
        c.im.paste(cover(a.bench_photo, box[2] - box[0], box[3] - box[1]), box[:2])
        c.d.rectangle(box, outline=t["line"], width=1)
    else:
        c.d.rectangle(box, fill=(232, 228, 219))
        x = box[0]
        while x < box[2]:                   # dashed hairline frame
            x2 = min(x + 14, box[2])
            c.d.line((x, y0, x2, y0), fill=t["muted"], width=1)
            c.d.line((x, y1, x2, y1), fill=t["muted"], width=1)
            x += 24
        yy = y0
        while yy < y1:
            y2 = min(yy + 14, y1)
            c.d.line((box[0], yy, box[0], y2), fill=t["muted"], width=1)
            c.d.line((box[2], yy, box[2], y2), fill=t["muted"], width=1)
            yy += 24
        for cx, cy, sx, sy in ((box[0], y0, 1, 1), (box[2], y0, -1, 1), (box[0], y1, 1, -1), (box[2], y1, -1, -1)):
            c.d.line((cx + 22 * sx, cy + 22 * sy, cx + 70 * sx, cy + 22 * sy), fill=t["red"], width=3)
            c.d.line((cx + 22 * sx, cy + 22 * sy, cx + 22 * sx, cy + 70 * sy), fill=t["red"], width=3)
        mid = (y0 + y1) / 2
        f = F_head(54)
        tw = c.tracked((0, 0), "Photo slot", f, t["ink"], -0.02, draw=False)
        c.tracked(((W - tw) / 2, mid - 70), "Photo slot", f, t["ink"], -0.02)
        for i, ln in enumerate(["REAL PHOTO OR VIDEO GOES HERE", "THE PRINTER, OR THE FIRST TEST PRINT", "DO NOT POST THIS TEMPLATE AS IT IS"]):
            fm = F_mono(21)
            lw = fm.getlength(ln) + 0.04 * 21 * (len(ln) - 1)
            c.mono(((W - lw) / 2, mid + 14 + i * 34), ln, 21, t["red"] if i == 2 else t["muted"])
    c.mono((M, c.cb - 24), "TEST PRINT. FIT TEST. THEN IT GOES ON SALE.", 22, t["muted"])
    return c.im


def p8(r, a):
    c = Canvas(r, LIGHT, 8, "How ordering works")
    y = c.headline(c.ct + 10, ["How ordering", "works."], 112, bar=True)
    c.rows(y + 60, c.cb, [
        ("Pick.", "Choose a piece on the site. Link in bio."),
        ("WhatsApp.", "Send the order. We confirm it in the chat."),
        ("UPI.", "Pay once we confirm. Shipping is quoted first."),
        ("Printed for you.", "Made to order in Bengaluru, then sent out."),
    ], head_size=50)
    return c.im


def p9(r, a):
    c = Canvas(r, DARK, 9, "Early access")
    t = c.t
    y = c.headline(c.ct + 10, ["The first", "batch is", "small."], 178, lh=0.98, bar=True)
    c.body(y + 54, "Pre-orders open soon. Message us on WhatsApp and you hear the day they do.", 38)
    yb = c.cb - 150
    c.d.rectangle((M, yb, W - M, yb + 10), fill=t["red"])
    c.headline(yb + 54, ["Early access. Link in bio."], 60, track=-0.02)
    c.mono((M, c.cb - 24), "NOTHING IS PRINTED UNTIL YOU ORDER IT.", 22, t["muted"])
    return c.im


POSTS = [(1, "Logo-Reveal", p1), (2, "Music-You-Can-Hold", p2), (3, "Drawn-First", p3),
         (4, "Vol-01-Teaser", p4), (5, "Design-Rules", p5), (6, "On-The-Bench", p6),
         (8, "How-Ordering-Works", p8), (9, "Early-Access", p9)]


def main():
    ap = argparse.ArgumentParser(description="Generate the No Skips soft launch kit.")
    ap.add_argument("posts", nargs="*", type=int, help="post numbers 1 to 9, 7 retired (default: all)")
    ap.add_argument("--out", default=os.path.join(HERE, "out", "softlaunch"))
    ap.add_argument("--bench-photo", help="real photo for the slot in post 6")
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    for n, slug, fn in POSTS:
        if a.posts and n not in a.posts:
            continue
        if n == 6 and not a.bench_photo:
            slug += "_TEMPLATE"
        for r in ("4x5", "9x16"):
            path = os.path.join(a.out, "SoftLaunch_%02d_%s_%s.jpg" % (n, slug, r))
            fn(r, a).save(path, quality=93, subsampling=0, optimize=True)
            print(path)


if __name__ == "__main__":
    main()
