"""D17 Bookends (Range V3 Reserve, 24 Nov 2026): weighted pair, numbered run of 25.
L-profile extruded across the width, prints standing on its base: no supports. A 80 x 70 x 5 mm steel plate (about 220 g)
is sealed inside the base: pause the print at the cavity floor+plate height, drop the plate in, resume (the lid then bridges
0.2 mm over the plate). Fluted back face, smooth book face, red top 4 mm (one colour change), felt feet in 1 mm recesses,
logo and run number debossed underneath (mirrored). The books rest on the base, so the base carries the weight.
Usage: python3 build10.py"""
import math, json, os
from ns import *
from ns import _cs
from build2 import logo
R = math.radians

W = 90.0; DEP = 84.0; TW = 6.0; H = 110.0; B = 8.4; CAP = 4.0
PLATE = (80.0, 60.0, 5.0); FLOOR = 2.0; PY = -42.0          # plate size, floor under it, plate centre y
PAUSE_Z = FLOOR + PLATE[2] + 0.2                             # cavity top = lid underside = where to pause

def bookend():
    prof = Polygon([(-DEP, 0), (TW, 0), (TW, H), (0, H), (0, B + 14), (-14, B), (-DEP, B)])
    prof = fillet(prof, 1.4)
    def yzw(poly, w): return mv(rot(Manifold.extrude(_cs(poly), w), 90, 0, 90), -w / 2, 0, 0)
    foot = box(-200, -1, 200, 0.6)
    def inset(d): return prof.buffer(-d, join_style=2).union(prof.intersection(foot))
    solid = U([yzw(prof, W - 1.2), yzw(inset(0.3), W - 0.6), yzw(inset(0.6), W)])
    pw, pl, pt = PLATE
    cavity = cube(pw + 0.4, pl + 0.4, pt + 0.2, 0, PY, FLOOR)                    # open ceiling, closed by the lid on resume
    feet = U([cyl(6.0, 0.8, -0.01, x, y) for x in (-32, 32) for y in (-20, -66)])   # 12 mm felt pads, 1 mm deep
    lx, ly = 0.0, -58.0
    mark = ext(affinity.scale(logo(lx, ly, 0.75), -1, 1, origin=(lx, ly)), 0.6, -0.01)
    num = fit_text("00/25", MIN_TEXT, 30.0, 0.0, -30.0)                             # placeholder, engraved per set
    num = ext(affinity.scale(num, -1, 1, origin=(0, -30.0)), 0.6, -0.01)
    flutes = U([cyl(1.1, H - 14 + 1, 14.0, x, TW) for x in np.arange(-W / 2 + 6.0, W / 2 - 5.9, 4.0)])
    be = solid - cavity - feet - mark - num - flutes
    top = cube(W + 4, 400, 100, 0, 0, H - CAP)
    return be - top, be ^ top

def build_bookends():
    p = Product("D17", "bookends", "Bookends")
    body_, cap = bookend()
    p.part("bookend", body_, BLACK, qty=2, infill=0.15)
    p.part("ridge", cap, RED, qty=2, infill=0.15, on="bookend")
    plate = cube(PLATE[0], PLATE[1], PLATE[2], 0, PY, FLOOR + 0.1)
    def at(m, x, rz): return mv(rot(m, 0, 0, rz), x, 0, 0)
    GAP = 150.0
    def pair(col):
        items = []
        for m, c in ((body_, col), (cap, RED)):
            items += [(at(m, -GAP / 2 - 0, 90), c), (at(m, GAP / 2, -90), c)]
        return items
    books = []
    xs = np.arange(-GAP / 2 + 3, GAP / 2 - 3, 1)
    hs = [118, 104, 126, 108, 120, 100]; ws = [22, 16, 24, 18, 20, 16]; x = -GAP / 2 + 2.0
    # books rest on the base: base top is z = B, wall front is at 0 so the row starts just inside the left bookend
    for i, (h, w) in enumerate(zip(hs, ws)):
        books.append((cube(w - 1.0, 80, h, x + w / 2, 0, B), PROP if i % 2 == 0 else PROP2)); x += w
    p.scene("bookends", pair(BLACK) + books)
    p.scene("bookends_ivory", pair(IVORY) + books)
    p.scene("bookends_single", [(body_, BLACK), (cap, RED)])
    p.scene("bookends_back", [(body_, BLACK), (cap, RED)])
    half = cube(200, 400, 400, 100, 0, -10)             # remove x > 0 to show the plate sealed in the base
    p.scene("bookends_cut", [(body_ - half, BLACK), (cap - half, RED), (plate, PROP2)])
    p.scene("bp_D17", [(body_, BLACK), (cap, RED)]); p.scene("bpo_D17", [(body_, BLACK), (cap, RED)])
    g = grams(body_, 0.15) + grams(cap, 0.15)
    p.note = (f"D17 Bookends, sold as a pair. Each {W:g} x {DEP + TW:.0f} x {H:g} mm, L profile, prints standing on its base, no supports. "
              f"Steel plate {PLATE[0]:g} x {PLATE[1]:g} x {PLATE[2]:g} mm sealed in the base (pause at z={PAUSE_Z:.1f} mm). Fluted back, smooth book face, red top {CAP:g} mm. "
              f"Felt feet 12 mm x4, logo and run number underneath. Plastic about {g:.0f} g each.")
    return p, g

if __name__ == "__main__":
    p, g = build_bookends()
    rep = p.export()
    print(json.dumps(rep, indent=1))
    pair_g = 2 * g
    print("plastic per bookend g", round(g, 1), "pair h (one plate, 2 colours, pause)", round(hours(pair_g, colours=2) + 0.2, 2))
    print("steel per plate g", round(PLATE[0] * PLATE[1] * PLATE[2] * 7.85e-3, 0), "pause z", PAUSE_Z)
