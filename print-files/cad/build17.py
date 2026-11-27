"""P3 chess board (25 Nov 2026): four 180 mm quadrants (4 x 4 squares of 45 mm), printed TOP FACE DOWN on the textured PEI bed so the
board surface gets the matte bed finish (owner request). z = 0 is the board top; the underside faces up and carries the logo and pockets.
Squares: black body, ivory squares inlaid in the first 0.6 mm (the only layers with two colours).
Joints: 8 printed bow-tie keys drop into matching pockets in the underside across each seam (vertical drop, so any quadrant can go in last).
NOTE (correction to the chat): rotating a checker quadrant by 90 degrees inverts its colours, so the board needs TWO inlay layouts:
  A = BL and TR quadrants, B = BR and TL quadrants (same body, inverted ivory squares). Print each twice.
Usage: NS_OUT=/tmp/out python3 build17.py"""
import math, json
from shapely.geometry import box, Polygon, Point
from ns import *
from build2 import logo
from build13 import GRID
import build16 as c16

Q = 4 * GRID          # 180 mm quadrant
T = 6.0               # board thickness
BAND = 1.2            # inlay depth, 6 layers (was 0.6: black body showed through the ivory squares, owner report 27 Nov)
INSET = 0.1           # inner edges pulled in 0.1 mm each, so two quadrants leave 0.2 mm at the seam
KEY_T, POCKET_D = 3.0, 3.2
KEY_GROW = 0.175     # production keys are grown by this: gap 0.025 mm per side (owner picked the 4-dot test key on 27 Nov)
CLR = 0.2             # pocket clearance per side (snug: a 0.3 key lets the seam open about 0.6 mm). Round 1 test keys (0.15/0.20/0.25) were all loose; round 2 tests 0.10/0.075/0.05/0.025
KEY_AT = (GRID, 3 * GRID)   # keys sit on the square lines 45 and 135 mm from the corner

def outline():
    """BL quadrant: outer corner (0,0) rounded, inner edges x = Q and y = Q pulled in by INSET."""
    s = box(0, 0, Q - INSET, Q - INSET).difference(box(0, 0, 8, 8)).union(Point(8, 8).buffer(8.0, quad_segs=16))
    return s.buffer(0)

def key2d():
    half = Polygon([(0, -4), (-10, -8), (-10, 8), (0, 4)])
    k = unary_union([half, affinity.scale(half, -1, 1, origin=(0, 0))])
    return k.buffer(-0.8, join_style=2).buffer(0.8, quad_segs=6)

def pockets():
    k = key2d().buffer(CLR, quad_segs=6)
    out = []
    for a in KEY_AT:
        out.append(affinity.translate(k, Q, a))                                   # seam along the x = Q edge
        out.append(affinity.translate(affinity.rotate(k, 90, origin=(0, 0)), a, Q))   # seam along the y = Q edge
    return unary_union(out)

def squares(variant):
    sq = []
    for i in range(4):
        for j in range(4):
            if (i + j) % 2 == (1 if variant == "A" else 0):
                sq.append(box(i * GRID, j * GRID, (i + 1) * GRID, (j + 1) * GRID))
    return unary_union(sq)

def quadrant(variant):
    o = outline()
    m = body(o, T, c=0.6, top=True, bottom=True)
    m = m - ext(pockets().intersection(o.buffer(5)), POCKET_D + 0.01, T - POCKET_D)
    cx, cy = (o.bounds[0] + o.bounds[2]) / 2, (o.bounds[1] + o.bounds[3]) / 2     # logo sits on the true centre of the quadrant (was 15 mm off on both axes until 27 Nov)
    lg = ext(affinity.translate(logo(0, 0, 1.3), cx, cy), 0.61, T - 0.6)     # reads from the underside, unmirrored
    m = m - lg
    inl = squares(variant).intersection(o.buffer(-0.0))
    ivory = ext(inl, BAND, 0.0)
    return m - ivory, ivory

def coupon():
    """Joint test: the seam corner of two quadrants around one key, black only. Print this before four full quadrants."""
    qa, ia = quadrant("A"); solid = U([qa, ia])
    a = solid ^ cube(28, 40, T + 2, Q - 14 - INSET, GRID, -1)
    b = a.mirror((1, 0, 0)).translate((2 * Q, 0, 0))          # the neighbour: pockets are symmetric about the seam
    return a, b

KEY_PROD_T = 3.1     # production key: 0.1 mm shy of the 3.2 pocket, so it reads flush with a hairline reveal (test keys stay 3.0)
def key(grow=0.0, dots=0, t=KEY_T):
    """grow > 0 makes a tighter test key. dots = small marks on top to tell test keys apart."""
    m = body(key2d().buffer(grow, quad_segs=6), t, c=0.4, top=True, bottom=True)
    for d in range(dots):
        m = m - cyl(0.9, 0.61, KEY_T - 0.6, -7.5, (d - (dots - 1) / 2) * 3.2, seg=24)
    return m

def audit():
    o = outline(); k = key2d(); p = pockets()
    rep = {}
    # key against its pocket, measured from the polygons
    pk = k.buffer(CLR, quad_segs=6)
    rep["key_to_pocket_mm"] = round(pk.exterior.hausdorff_distance(k.exterior), 3)
    rep["key_depth_gap_mm"] = round(POCKET_D - KEY_T, 2)
    rep["top_skin_over_pocket_mm"] = round(T - POCKET_D, 2)
    rep["seam_gap_mm"] = round(2 * INSET, 2)
    # pockets stay clear of the logo and of the outer edges
    lg = affinity.translate(logo(0, 0, 1.3), (o.bounds[0] + o.bounds[2]) / 2, (o.bounds[1] + o.bounds[3]) / 2)
    rep["pocket_to_logo_mm"] = round(p.distance(lg), 1)
    rep["pocket_to_outer_edge_mm"] = round(min(q.bounds[0] for q in [p]) if p.bounds[0] > 0 else 0, 1)
    # every pocket must sit across a seam: half of it inside the body, half over the gap
    rep["pocket_overlap_with_body_mm2"] = round(p.intersection(o).area, 1)
    return rep

def overhang(m, zmin=0.8):
    t = tm(m); nz = t.face_normals[:, 2]; cz = t.triangles_center[:, 2]
    return float(t.area_faces[(nz < -0.7072) & (cz > zmin)].sum())

if __name__ == "__main__":
    qa, ia = quadrant("A"); qb, ib = quadrant("B"); ky = key(KEY_GROW, 0, KEY_PROD_T)
    q = Product("P3", "chess_board", "Chess board quadrants")
    q.part("quad_A", qa, BLACK, qty=2, infill=0.15); q.part("quad_A_ivory", ia, IVORY, qty=2, on="quad_A")
    q.part("quad_B", qb, BLACK, qty=2, infill=0.15); q.part("quad_B_ivory", ib, IVORY, qty=2, on="quad_B")
    q.part("key", ky, IVORY, qty=8, infill=1.0)
    ca, cb = coupon()
    q.part("coupon_left", ca, BLACK, infill=0.15); q.part("coupon_right", cb, BLACK, infill=0.15)
    # Round 2 (27 Nov): every key of round 1 (gaps 0.15, 0.20, 0.25 per side) was loose, so the fit is tighter than 0.15.
    # grow = CLR - gap. 1 dot = 0.10 mm gap per side, 2 dots = 0.075, 3 dots = 0.05, 4 dots = 0.025.
    for n, g in ((1, 0.10), (2, 0.125), (3, 0.15), (4, 0.175)):
        q.part(f"testkey_{n}dot", key(g, n), BLACK, infill=1.0)
    # render scene: board face up, start position
    # turning the printed quadrant over along its diagonal: (x, y, z) -> (y, x, T - z). Outline, pockets and squares are all
    # symmetric about x = y, so the top you see is exactly the layout designed here.
    flip = lambda m: m.transform([[0, 1, 0, 0], [1, 0, 0, 0], [0, 0, -1, T]])
    def place(m, x, y, rz=0): return m.rotate((0, 0, rz)).translate((x, y, 0))
    sc = []
    # BL = A at origin; BR = B rotated 90 about its centre; TL = B rotated -90; TR = A rotated 180
    def quad(m, i, rz):
        c = Q / 2
        return mv(m.translate((-c, -c, 0)).rotate((0, 0, rz)).translate((c, c, 0)), i[0] * Q, i[1] * Q, 0)
    for (m, iv), pos, rz in ((((qa, ia)), (0, 0), 0), ((qb, ib), (1, 0), 90), ((qb, ib), (0, 1), -90), ((qa, ia), (1, 1), 180)):
        sc.append((quad(flip(m), pos, rz), BLACK)); sc.append((quad(flip(iv), pos, rz), IVORY))
    ox, oy = -2 * Q / 2 * 0, 0
    P = {n: getattr(c16, n)() for n in c16.ORDER[:-1]}; kb, kin = c16.king(); P["king"] = kb
    if isinstance(P["queen"], tuple): P["queen"] = P["queen"][0]   # queen() returns (body, red dot) since 25 Nov; the board scene uses the body
    back = ["rook", "knight", "bishop", "queen", "king", "bishop", "knight", "rook"]
    pieces = []
    for i in range(8):
        pieces.append((back[i], i, 0, IVORY, 0)); pieces.append(("pawn", i, 1, IVORY, 0))
        pieces.append((back[i], i, 7, BLACK, 180)); pieces.append(("pawn", i, 6, BLACK, 180))
    for n, i, j, col, rz in pieces:
        x, y = (i + 0.5) * GRID, (j + 0.5) * GRID
        sc.append((mv(P[n].rotate((0, 0, rz)), x, y, T), col))
        if n == "king": sc.append((mv(c16.king()[1].rotate((0, 0, rz)), x, y, T), RED))
    q.scene("chess_board", sc)
    q.scene("chess_board_bare", [s for s in sc[:8]])
    # underside preview (27 Nov): four quadrants as printed (underside up), keys ivory and near flush across every seam
    ux = lambda m, dx, dy, rz: mv(m.translate((-Q / 2, -Q / 2, 0)).rotate((0, 0, rz)).translate((Q / 2, Q / 2, 0)), dx, dy, 0)
    under = []
    for (m, pos, rz) in ((qa, (0, 0), 0), (qb, (1, 0), 90), (qb, (0, 1), -90), (qa, (1, 1), 180)):
        under.append((ux(m, pos[0] * Q, pos[1] * Q, rz), BLACK))
    kf = key(KEY_GROW, 0, KEY_PROD_T).translate((0, 0, T - POCKET_D + 0.1))
    for a in KEY_AT:
        under.append((kf.translate((Q, a, 0)), IVORY)); under.append((kf.rotate((0, 0, 90)).translate((a, Q, 0)), IVORY))
        under.append((kf.translate((Q, 2 * Q - a, 0)), IVORY)); under.append((kf.rotate((0, 0, 90)).translate((2 * Q - a, Q, 0)), IVORY))
    q.scene("board_underside", under)
    rep = q.export()
    print("quadrant files:", [(p["file"], p["size"], p["grams"]) for p in rep["parts"]])
    print("total g (4 quadrants + 8 keys):", rep["grams"])
    print("AUDIT", json.dumps(audit()))
    print("overhang mm2 (quadrant A, key):", round(overhang(qa), 1), round(overhang(ky), 1))
    ga = grams(qa, 0.15); print("one quadrant g @15%:", round(ga, 1), "h:", round(hours(ga, 1, 2), 2))
    json.dump(rep, open(f"{OUT}/board_report.json", "w"), indent=1)
