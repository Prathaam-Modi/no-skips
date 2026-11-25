"""P3 minimal chess set (25 Nov 2026). Six turned forms on one shared base language, solid PLA, no metal, no supports.
Shared base: a disc with a 0.6 mm bottom bevel, a 1 mm top chamfer and a 45 degree flare into the stem (same as the pawn test).
  pawn    cylinder stem + sphere
  rook    plain cylinder, one slot across the top
  knight  plain cylinder, top cut on a slope (the slope faces the opponent)
  bishop  tapered stem, elongated dome, one tilted slit
  queen   tapered neck, flat cap, shallow round dish in the top
  king    same body as the queen, taller, flat top with a red cross inlay (0.6 mm)
Usage: NS_OUT=/tmp/out python3 build15.py"""
import math, json, os
import numpy as np
from ns import *
from build2 import logo
from build13 import GRID, checker

HB = 6.0                       # base disc height
FL = 3.0                       # 45 degree flare height under the stem
BAND = 0.6                     # red inlay depth (3 layers at 0.2 mm)
SPEC = {   # name: (base radius, stem start radius, height)
    "pawn": (14.0, 7.2, 40.9), "rook": (15.0, 10.0, 46.0), "knight": (15.0, 10.0, 50.0),
    "bishop": (15.0, 10.0, 56.0), "queen": (16.0, 10.5, 62.0), "king": (16.0, 10.5, 72.0),
}

def base_pts(rb, r0):
    assert rb - 1.0 >= r0 + FL, "flare would run into the base chamfer"
    return [(0, 0), (rb - 0.6, 0), (rb, 0.6), (rb, HB - 1.0), (rb - 1.0, HB), (r0 + FL, HB), (r0, HB + FL)]

def logo_cut(): return ext(affinity.scale(logo(0, 0, 0.75), -1, 1, origin=(0, 0)), 0.6, -0.01)

def finish(m): return m - logo_cut()

def pawn():
    rb, rs, H = SPEC["pawn"]; zs, R = 24.0, 10.0
    assert rs >= 0.7 * R, "sphere underside would overhang past 45 degrees"
    stem = revolve(base_pts(rb, rs) + [(rs, zs + 0.5), (0, zs + 0.5)], 160)
    zc = zs + math.sqrt(R * R - rs * rs)
    return finish(U([stem, Manifold.sphere(R, 160).translate((0, 0, zc))])), zc + R

def rook():
    rb, r0, H = SPEC["rook"]
    m = revolve(base_pts(rb, r0) + [(r0, H - 0.6), (r0 - 0.6, H), (0, H)], 160)
    slot = cube(40, 3.2, 6.5, 0, 0, H - 6.0)
    return finish(m - slot), H

def knight():
    rb, r0, H = SPEC["knight"]
    full = revolve(base_pts(rb, r0) + [(r0, 70.0), (0, 70.0)], 160)
    # slope: 30 degrees, high edge at the back (-y), falling toward the front (+y); back edge at height H
    t = math.tan(math.radians(30)); zc = H - r0 * t        # plane height at y = 0
    n = (0.0, t, 1.0); ln = math.sqrt(1 + t * t); n = tuple(c / ln for c in n)
    m = full.trim_by_plane(tuple(-c for c in n), -zc / ln)   # keep the side below the plane
    return finish(m), H

def bishop():
    rb, r0, H = SPEC["bishop"]; zd = 34.0; rd = 7.8; b = H - zd
    dome = [(rd * math.cos(math.radians(a)), zd + b * math.sin(math.radians(a))) for a in range(0, 90, 5)] + [(0, H)]
    m = revolve(base_pts(rb, r0) + [(rd, zd)] + dome[1:], 160)
    # one slit tilted 40 degrees from vertical (its walls stay inside the 45 degree no-support limit)
    slab = Manifold.cube((2.0, 40.0, 60.0)).translate((-1.0, -20.0, -30.0)).rotate((0, 40, 0)).translate((0, 0, H - 9.0))
    clip = cube(60, 60, 30, 0, 0, H - 18.0)
    return finish(m - (slab ^ clip)), H

def royal(kind):
    rb, r0, H = SPEC[kind]; rn = 7.5; ze = H - 13.6          # neck ends, 45 degree-ish flare to the cap
    rc = 11.5
    prof = base_pts(rb, r0) + [(rn, ze), (rc, ze + 4.4), (rc, H - 1.0), (rc - 1.0, H), (0, H)]
    m = revolve(prof, 160)
    return m, H

def queen():
    m, H = royal("queen")
    dish = Manifold.sphere(14.0, 160).translate((0, 0, H + 14.0 - 2.4))
    return finish(m - dish), H

def cross2d(): return unary_union([rrect(17.0, 3.6, 1.0), rrect(3.6, 17.0, 1.0)])

def king():
    m, H = royal("king")
    recess = ext(cross2d(), BAND + 0.01, H - BAND)
    inlay = ext(cross2d(), BAND, H - BAND)
    return finish(m - recess), inlay, H

def overhang_area(m, zmin=0.8):
    """Area (mm2) of faces tipped past 45 degrees from vertical, facing down, above the bed layer."""
    t = tm(m); nz = t.face_normals[:, 2]; cz = t.triangles_center[:, 2]
    bad = (nz < -0.7072) & (cz > zmin)
    return float(t.area_faces[bad].sum())

if __name__ == "__main__":
    P = {}
    P["pawn"] = pawn(); P["rook"] = rook(); P["knight"] = knight(); P["bishop"] = bishop(); P["queen"] = queen()
    kb, inlay, kH = king(); P["king"] = (kb, kH)
    rep = {}
    # ---- print product: two colour sets, solid
    q = Product("P3", "chess", "Minimal chess set")
    QTY = {"pawn": 8, "rook": 2, "knight": 2, "bishop": 2, "queen": 1, "king": 1}
    INF = 1.0
    for colour, sfx in ((BLACK, "b"), (IVORY, "i")):
        for name in ("pawn", "rook", "knight", "bishop", "queen", "king"):
            q.part(f"{name}_{sfx}", P[name][0], colour, qty=QTY[name], infill=INF)
            if name == "king": q.part(f"king_cross_{sfx}", inlay, RED, qty=1, on=f"king_{sfx}")
    # ---- render scenes
    def row(y, colour, names, face=1):
        out = []
        for i, nme in enumerate(names):
            m = P[nme][0]
            if nme == "knight" and face < 0: m = m.rotate((0, 0, 180))
            out.append((mv(m, (i - (len(names) - 1) / 2) * GRID, y, 0), colour))
        return out
    board = []
    names = ["rook", "knight", "bishop", "queen", "king", "pawn"]
    for i in range(len(names)):
        for j in range(2):
            c = IVORY if (i + j) % 2 == 0 else BLACK
            board.append((ext(rrect(GRID - 0.6, GRID - 0.6, 0.8, (i - (len(names) - 1) / 2) * GRID, (j - 0.5) * GRID), 4.0, -4.0), c))
    # the king's red cross only shows in the render when it is added as a RED mesh at the top
    def kcross(x, y): return (mv(inlay, x, y, 0), RED)
    sc = list(board)
    sc += row(GRID / 2, BLACK, names, -1); sc += row(-GRID / 2, IVORY, names, 1)
    kx = (names.index("king") - (len(names) - 1) / 2) * GRID
    sc += [kcross(kx, GRID / 2), kcross(kx, -GRID / 2)]
    q.scene("chess_set", sc)
    # the six forms side by side, ivory, no board, so the silhouettes read
    f = []
    order = ["pawn", "rook", "knight", "bishop", "queen", "king"]
    for i, nme in enumerate(order):
        x = (i - 2.5) * 40.0
        f.append((mv(P[nme][0], x, 0, 0), IVORY))
    f.append((mv(inlay, 2.5 * 40.0, 0, 0), RED))
    q.scene("chess_forms", f)
    rep = q.export()
    # ---- checks
    print("PIECE        H mm   base mm  grams solid  hours  overhang mm2  tip angle")
    for name in order:
        m, H = P[name]
        t = tm(m); com = t.center_mass
        rb = SPEC[name][0]
        tip = math.degrees(math.atan(rb / com[2]))
        g = grams(m, 1.0)
        print(f"{name:8s} {H:7.1f} {2*rb:8.1f} {g:11.1f} {hours(g):7.2f} {overhang_area(m):13.2f} {tip:9.1f}")
    assert all(overhang_area(P[n][0]) < 3.0 for n in order), "overhang above the logo ceiling allowance"
    print("set grams per colour", round(sum(grams(P[n][0], 1.0) * QTY[n] for n in order), 1))
    print("both colours", rep["grams"])
    json.dump(rep, open(f"{OUT}/chess_report.json", "w"), indent=1)
