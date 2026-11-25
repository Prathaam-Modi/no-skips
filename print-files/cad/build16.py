"""P3 chess v2 "Six Cuts" (25 Nov 2026, owner: more minimal, pawn as a lean four-sided pyramid, engraving welcome).
Idea: every piece is the same 22 mm square block, cut a different way. Each piece also carries its move as an engraved glyph
on its front and back faces, so the set teaches itself. Heights rise 4 mm per rank.
  pawn    lean square pyramid (18 mm base)          glyph |   one step forward
  rook    plain block, flat top                      glyph +   straight lines
  knight  block with a stepped top (head and snout)  glyph L
  bishop  block with a roof whose ridge runs corner to corner (the diagonal)   glyph x
  queen   block with a pyramid cap (the pawn, promoted onto a column)          glyph * (+ and x)
  king    tallest block, flat top, red square inlay on top                     glyph square (one step any way)
Rules: no supports, no metal, logo debossed underneath, glyph grooves 1.2 mm wide and 0.6 mm deep.
Usage: NS_OUT=/tmp/out python3 build16.py"""
import math, json, os
from shapely.geometry import LineString
from ns import *
from build2 import logo
from build13 import GRID

S, RC, C = 22.0, 1.0, 0.6          # block side, corner radius, bevel
PB = 18.0                          # pawn base
D, W = 0.6, 1.2                    # engraving depth and stroke
H = dict(pawn=32.0, rook=36.0, knight=40.0, bishop=44.0, queen=48.0, king=52.0)
ORDER = ["pawn", "rook", "knight", "bishop", "queen", "king"]

# ---------------------------------------------------------------- glyphs (2D, v = up the face)
def bar(x0, y0, x1, y1): return LineString([(x0, y0), (x1, y1)]).buffer(W / 2, cap_style=2, join_style=2)
def g_plus(a=5.0): return unary_union([bar(-a, 0, a, 0), bar(0, -a, 0, a)])
def g_cross(a=5.0): return affinity.rotate(g_plus(a), 45, origin=(0, 0))
GLYPH = {
    "pawn": bar(0, -3.5, 0, 3.5),
    "rook": g_plus(),
    # an L as you read it; mirrored because the cutter's x runs right to left when seen from outside the face
    "knight": affinity.scale(affinity.translate(unary_union([bar(0, -4.4, 0, 4.4), bar(-W / 2, -3.8, 4.0, -3.8)]), -1.75, 0), -1, 1, origin=(0, 0)),
    "bishop": g_cross(),
    "queen": unary_union([g_plus(), g_cross()]),
    "king": rrect(8.4, 8.4, 0.6).difference(rrect(8.4 - 2 * W, 8.4 - 2 * W, 0.2)),
}

def engrave(m, g2d, zc, half, phi=0.0):
    """Cut the glyph into the +y and -y faces. half = distance from the axis to the face at height zc; phi = face lean."""
    cut = ext(g2d, D + 1.0, -1.0)                       # local z: outside (-1) to D inside the face
    c = cut.rotate((90 + math.degrees(phi), 0, 0)).translate((0, half, zc))
    return m - U([c, c.rotate((0, 0, 180))])

def underside(m, scale=1.0):
    return m - ext(affinity.scale(logo(0, 0, scale), -1, 1, origin=(0, 0)), 0.6, -0.01)

def block(h, top=True): return body(rrect(S, S, RC), h, c=C, top=top, bottom=True)
def keep_below(m, n, c):
    """Keep the part of m where n . p <= c."""
    l = math.sqrt(sum(x * x for x in n)); n = tuple(x / l for x in n)
    return m.trim_by_plane(tuple(-x for x in n), -c / l)

# ---------------------------------------------------------------- pieces
def pawn():
    h = H["pawn"]; top = 1.6
    m = Manifold.cylinder(h, PB / math.sqrt(2), top / math.sqrt(2), 4).rotate((0, 0, 45))
    phi = math.atan((PB - top) / 2 / h); zc = 12.0
    m = engrave(m, GLYPH["pawn"], zc, PB / 2 - zc * math.tan(phi), phi)
    return underside(m, 0.85)

def rook():
    return underside(engrave(block(H["rook"]), GLYPH["rook"], 22.0, S / 2))

def knight():
    h = H["knight"]; drop = 13.0; back = 0.45 * S          # tall head at the back (-y), lower snout toward the opponent (+y)
    m = block(h) - cube(S + 2, S - back + 1, drop + 2, 0, -S / 2 + back + (S - back + 1) / 2, h - drop)
    return underside(engrave(m, GLYPH["knight"], 15.5, S / 2))

def bishop():
    h = H["bishop"]; t = math.tan(math.radians(30)); k = t / math.sqrt(2)
    m = block(h + 1, top=False)
    m = keep_below(m, (k, -k, 1.0), h); m = keep_below(m, (-k, k, 1.0), h)   # ridge along x = y
    return underside(engrave(m, GLYPH["bishop"], 20.0, S / 2))

def queen():
    h = H["queen"]; cap = 10.0
    col = block(h - cap + 0.01, top=False)
    pyr = Manifold.cylinder(cap, S / math.sqrt(2), 1.2 / math.sqrt(2), 4).rotate((0, 0, 45)).translate((0, 0, h - cap))
    pyr = pyr ^ ext(rrect(S, S, RC), cap + 1, h - cap - 0.5)
    return underside(engrave(U([col, pyr]), GLYPH["queen"], 22.0, S / 2))

KTOP = rrect(10.0, 10.0, 0.8)
def king():
    h = H["king"]
    m = block(h) - ext(KTOP, D + 0.01, h - D)
    return underside(engrave(m, GLYPH["king"], 26.0, S / 2)), ext(KTOP, D, h - D)

# ---------------------------------------------------------------- checks
def overhang(m, zmin=0.8):
    t = tm(m); nz = t.face_normals[:, 2]; cz = t.triangles_center[:, 2]
    bad = (nz < -0.7072) & (cz > zmin)
    return float(t.area_faces[bad].sum())

if __name__ == "__main__":
    P = {n: globals()[n]() for n in ORDER[:-1]}
    kb, kin = king(); P["king"] = kb
    QTY = {"pawn": 8, "rook": 2, "knight": 2, "bishop": 2, "queen": 1, "king": 1}
    q = Product("P3", "chess", "Six Cuts chess set")
    for colour, sfx in ((BLACK, "b"), (IVORY, "i")):
        for n in ORDER:
            q.part(f"{n}_{sfx}", P[n], colour, qty=QTY[n], infill=0.15)
            if n == "king": q.part(f"king_top_{sfx}", kin, RED, on=f"king_{sfx}")
    # scenes
    names = ["rook", "knight", "bishop", "queen", "king", "pawn"]
    xs = [(i - 2.5) * GRID for i in range(6)]
    board = [(ext(rrect(GRID - 0.6, GRID - 0.6, 0.8, xs[i], (j - 0.5) * GRID), 4.0, -4.0), IVORY if (i + j) % 2 == 0 else BLACK)
             for i in range(6) for j in range(2)]
    sc = list(board)
    for y, col, rz in ((-GRID / 2, IVORY, 0), (GRID / 2, BLACK, 180)):
        for i, n in enumerate(names):
            sc.append((mv(P[n].rotate((0, 0, rz)), xs[i], y, 0), col))
            if n == "king": sc.append((mv(kin, xs[i], y, 0), RED))
    q.scene("chess2_set", sc)
    f = []
    for i, n in enumerate(ORDER):
        x = (i - 2.5) * 34.0
        f.append((mv(P[n], x, 0, 0), IVORY))
        if n == "king": f.append((mv(kin, x, 0, 0), RED))
    q.scene("chess2_forms", f)
    rep = q.export()
    print("piece     H    foot  grams15  grams100  overhang_mm2  tip_deg")
    for n in ORDER:
        t = tm(P[n]); com = t.center_mass; foot = PB if n == "pawn" else S
        print(f"{n:7s} {H[n]:5.1f} {foot:5.1f} {grams(P[n], 0.15):8.1f} {grams(P[n], 1.0):9.1f} {overhang(P[n]):13.2f} {math.degrees(math.atan(foot / 2 / com[2])):8.1f}")
    print("both colours g @15%:", rep["grams"])
    json.dump(rep, open(f"{OUT}/chess2_report.json", "w"), indent=1)
