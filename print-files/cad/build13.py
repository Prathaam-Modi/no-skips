"""Play line (24 Nov 2026): tabletop objects on one 45 mm grid, black and ivory with one red element.
P1 Crosses: nine double-sided 90 mm coasters (2 x 2 grid modules). Ivory X inlaid in one face, red O in the other, black body.
           Stacked in the caddy they are coasters; dealt out on the table they are a tic-tac-toe board.
P3 pawn test: Bauhaus chess pawn sized for 45 mm squares, cylinder plus sphere, hidden steel washer for weight.
Rules kept: no supports, colour details only in height bands (first and last 0.6 mm), no joints, logo underneath, no text.
Usage: NS_OUT=/tmp/out python3 build13.py"""
import math, json, os
import numpy as np
from ns import *
from build2 import logo

GRID = 45.0                     # the Play module
# ------------------------------------------------------------------ P1 Crosses
CS = 2 * GRID                   # coaster side, 90 mm
CT = 5.0                        # coaster thickness
BAND = 0.6                      # inlay depth: 3 layers at 0.2 mm
def x_mark():
    bar = rrect(58, 9.5, 4.7)
    return unary_union([affinity.rotate(bar, 45, origin=(0, 0)), affinity.rotate(bar, -45, origin=(0, 0))])
def o_mark():
    return circle(26.0, seg=160).difference(circle(16.5, seg=160))

# House texture (owner, 24 Nov 11:20 pm: "follow the same texture"): B-Side record grooves on flat faces
# (1.3 mm wide, 0.45 mm deep, 3.4 mm pitch) and bookend-style vertical flutes on upright faces.
GW, GD, GP = 1.3, 0.45, 3.4
def groove_rings():
    """Rounded-square rings following the coaster outline, clear of the X and O marks."""
    rings = []
    h = 30.0
    while h + GW <= CS / 2 - 4.5:
        rings.append(rrect(2 * (h + GW), 2 * (h + GW), 8.0 * (h + GW) / (CS / 2)).difference(rrect(2 * h, 2 * h, 8.0 * h / (CS / 2))))
        h += GP
    return unary_union(rings)
def flutes(points, r, z0, h, seg=24):
    return U([cyl(r, h, z0, x, y, seg=seg) for x, y in points])

def coaster():
    sq = rrect(CS, CS, 8.0)
    blk = body(sq, CT, c=0.6, top=True, bottom=True)
    g = groove_rings()
    blk = blk - ext(g, GD + 0.01, CT - GD) - ext(g, GD, -0.01)
    # O lies in the bed face, mirrored so it reads right way round when flipped (a ring is symmetric anyway)
    o = ext(o_mark(), BAND, 0.0)
    x = ext(x_mark(), BAND + 0.01, CT - BAND)
    return blk - o - x, x, o

def caddy():
    """Base plate with two L posts at opposite corners; coasters drop in, grab from the open sides."""
    inner = CS + 1.6                      # 0.8 mm clearance each side
    t = 4.0; base_h = 4.0; post_h = base_h + 9 * CT + 3.0
    outer = inner + 2 * t
    base = body(rrect(outer, outer, 9.0), base_h, c=0.6, top=True, bottom=False)
    arm = 26.0
    def L(sx, sy):
        cx, cy = sx * (outer / 2 - t / 2), sy * (outer / 2 - t / 2)
        a = rrect(t, arm, 1.2, cx, cy - sy * (arm / 2 - t / 2))
        b = rrect(arm, t, 1.2, cx - sx * (arm / 2 - t / 2), cy)
        return unary_union([a, b, rrect(t + 0.01, t + 0.01, 0.01, cx, cy)])
    posts_2d = unary_union([L(-1, 1), L(1, -1)]).intersection(rrect(outer, outer, 9.0))
    posts = body(posts_2d, post_h - base_h + 0.02, base_h - 0.02, c=0.6, top=True)
    m = U([base, posts])
    # vertical flutes on the two outer faces of each L post, 4 mm pitch like the bookends
    fl = []
    for sx, sy in ((-1, 1), (1, -1)):
        edge_x, edge_y = sx * outer / 2, sy * outer / 2
        for k in range(5):
            d = 4.5 + 4.0 * k
            fl.append((edge_x, edge_y - sy * d))          # face along y
            fl.append((edge_x - sx * d, edge_y))          # face along x
    m = m - flutes(fl, 0.8, base_h + 2.0, post_h - base_h)
    lg = ext(affinity.scale(logo(0, 0, 0.9), -1, 1, origin=(0, 0)), 0.6, -0.01)
    pads = U([cyl(6.1, 0.8, -0.01, sx * (outer / 2 - 12), sy * (outer / 2 - 12)) for sx in (-1, 1) for sy in (-1, 1)])
    return m - lg - pads, base_h

# ------------------------------------------------------------------ P3 pawn
PAWN = dict(rb=14.0, hb=6.0, rs=7.2, zs=24.0, R=10.0)
WASH = dict(r=8.3, h=1.8, z=1.2)          # M8 flat washer (16 mm OD, 1.6 mm) sealed in by a pause
def pawn():
    rb, hb, rs, zs, R = PAWN["rb"], PAWN["hb"], PAWN["rs"], PAWN["zs"], PAWN["R"]
    assert rs >= 0.7 * R, "sphere underside would overhang past 45 degrees"
    prof = [(0, 0), (rb - 0.6, 0), (rb, 0.6), (rb, hb - 1.0), (rb - 1.0, hb), (rs + 3.0, hb), (rs, hb + 3.0), (rs, zs + 0.5), (0, zs + 0.5)]
    stem = revolve(prof, 160)
    zc = zs + math.sqrt(R * R - rs * rs)
    head = Manifold.sphere(R, 160).translate((0, 0, zc))
    m = U([stem, head])
    # flutes round the base disk, between the bed chamfer and the top chamfer
    n = 28
    fl = [(rb * math.cos(2 * math.pi * k / n), rb * math.sin(2 * math.pi * k / n)) for k in range(n)]
    m = m - flutes(fl, 0.7, 1.2, hb - 2.4, seg=20)
    lg = ext(affinity.scale(logo(0, 0, 0.75), -1, 1, origin=(0, 0)), 0.6, -0.01)
    cav = cyl(WASH["r"], WASH["h"], WASH["z"], seg=96)
    return m - lg - cav, zc + R

def checker(n=2):
    """Render prop: a 2 x 2 patch of the 45 mm board."""
    sq = []
    for i in range(n):
        for j in range(n):
            c = IVORY if (i + j) % 2 == 0 else BLACK
            sq.append((ext(rrect(GRID - 0.6, GRID - 0.6, 0.8, (i - (n - 1) / 2) * GRID, (j - (n - 1) / 2) * GRID), 4.0, -4.0), c))
    return sq

if __name__ == "__main__":
    rep = {}
    # P1
    p = Product("P1", "crosses", "Crosses")
    blk, x, o = coaster()
    p.part("coaster", blk, BLACK, qty=9, infill=0.25)
    p.part("x_inlay", x, IVORY, qty=9, on="coaster")
    p.part("o_inlay", o, RED, qty=9, on="coaster")
    cad, base_h = caddy()
    p.part("caddy", cad, BLACK, infill=0.2)
    flip = lambda m: m.rotate((180, 0, 0)).translate((0, 0, CT))
    lay = [1, 0, 2, 0, 1, 0, 2, 1, 0]          # 1 = X up, 2 = O up, 0 = empty spot
    sc = []
    for k, v in enumerate(lay):
        if not v: continue
        cx, cy = (k % 3 - 1) * (CS + 6), (1 - k // 3) * (CS + 6)
        if v == 1: parts = [(blk, BLACK), (x, IVORY), (o, RED)]
        else: parts = [(flip(blk), BLACK), (flip(x), IVORY), (flip(o), RED)]
        sc += [(mv(m, cx, cy, 0), c) for m, c in parts]
    ox = 1.5 * (CS + 6) + CS / 2 + 30
    sc.append((mv(cad, ox, 60, 0), BLACK))
    for i in range(4):
        sc += [(mv(m, ox, 60, base_h + i * CT), c) for m, c in [(blk, BLACK), (x, IVORY), (o, RED)]]
    p.scene("crosses", sc)
    p.scene("crosses_one", [(blk, BLACK), (x, IVORY), (o, RED)])
    stack = [(cad, BLACK)] + [(mv(m, 0, 0, base_h + i * CT), c) for i in range(9) for m, c in [(blk, BLACK), (x, IVORY), (o, RED)]]
    p.scene("crosses_stack", stack)
    rep["P1"] = p.export()
    # P3 pawn test
    q = Product("P3", "pawn_test", "Bauhaus pawn test")
    pw, H = pawn()
    q.part("pawn", pw, BLACK, infill=0.25)
    q.note = f"Pawn height {H:.1f} mm. Pause at Z {WASH['z'] + WASH['h']:.1f} mm to drop in an M8 washer."
    q.scene("pawns", checker() + [(mv(pw, -GRID / 2, -GRID / 2, 0), BLACK), (mv(pw, GRID / 2, GRID / 2, 0), IVORY)])
    rep["P3"] = q.export(); rep["P3"]["height"] = round(H, 1)
    for k, r in rep.items(): print(k, r["grams"], [(x["file"], x["size"], x["grams"]) for x in r["parts"]])
    json.dump(rep, open(f"{OUT}/play_report.json", "w"), indent=1)
