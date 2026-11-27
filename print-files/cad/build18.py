"""P3 chess case (27 Nov 2026, concept for owner review). One tray plus one lid, printed from two models, hold the whole set (32 pieces)
lying on their sides. The tray is a grid: columns are the files a to h, rows are black back rank, black pawns, ivory pawns, ivory back rank.
Every pocket is the convex hull of its piece, grown by CLR_P, cut down to the piece's axis plane so walls only widen going up (no overhang).
The lid is a hollow cover (roof 1.6 mm, walls 3.6 mm) printed roof down. A raised ridge on the tray
rim sits in a groove in the lid for registration. Pieces are not clipped: it is a lie-flat case, carry it flat.
Usage: NS_OUT=/tmp/out python3 build18.py"""
import math, json
from ns import *
import build16 as c16

CLR_P = 0.3                      # pocket clearance per side (storage, not a fit)
FLOOR = 2.4                      # floor under the deepest pocket
THK = c16.S                      # 22: every piece but the pawn lies 22 mm thick
T = FLOOR + CLR_P + THK / 2      # tray height = plane of the piece axes = 13.7
PITCH = 26.0                     # one file
GAP = 3.5                        # wall between rows
M = 5.0                          # outer margin to the first pocket
RIDGE_W, RIDGE_H, RIDGE_IN = 1.2, 1.5, 2.0   # ridge on the tray rim; groove in the lid is 0.2 wider per side and 0.3 deeper
BACK = ["rook", "knight", "bishop", "queen", "king", "bishop", "knight", "rook"]
ROWS = [("black", BACK), ("black", ["pawn"] * 8), ("ivory", ["pawn"] * 8), ("ivory", BACK)]

def pieces():
    P = {n: getattr(c16, n)() for n in c16.ORDER}
    for n in ("queen", "king"): P[n] = P[n][0]
    return P
def lying(m, name):
    """Piece lies on its side, front face up, base toward -y, centred on x = 0 and z = 0."""
    L = m.rotate((-90, 0, 0))
    if name == "pawn":                                   # the pyramid rests on a sloped back face: level it
        best = None
        for s in (1, -1):
            for a in (math.degrees(math.atan((c16.PB - 1.6) / 2 / c16.H["pawn"])),):
                t = L.rotate((s * a, 0, 0)); b = t.bounding_box(); th = b[5] - b[2]
                if best is None or th < best[0]: best = (th, t)
        L = best[1]
    b = L.bounding_box()
    return L.translate((-(b[0] + b[3]) / 2, -b[1], -(b[2] + b[5]) / 2))   # x centred, base end at y = 0, axis plane at z = 0
def pocket(L, lid=False):
    """Grown convex hull of the lying piece, as seen from the printed face of the tray (lid: turned over, front down)."""
    h = (L.rotate((0, 180, 0)) if lid else L).hull()
    return h.minkowski_sum(Manifold.sphere(CLR_P, 16))

ROWLEN = [max(c16.H[n] for n in names) + 2 * CLR_P for _, names in ROWS]
W_ = 7 * PITCH + 22 + 2 * CLR_P + 2 * M
D_ = sum(ROWLEN) + GAP * (len(ROWS) - 1) + 2 * M
X0 = -(W_ / 2) + M + 11 + CLR_P            # x of file a (tray frame)
def row_y(i): return M + sum(ROWLEN[:i]) + GAP * i

def shell(lid):
    b = body(rrect(W_, D_, 5.0, W_ / 2, D_ / 2), T, c=0.6, top=False, bottom=True)
    ring = lambda inset, w: rrect(W_ - 2 * inset, D_ - 2 * inset, max(1.0, 5.0 - inset), W_ / 2, D_ / 2).difference(
        rrect(W_ - 2 * (inset + w), D_ - 2 * (inset + w), max(0.8, 5.0 - inset - w), W_ / 2, D_ / 2))
    if lid:
        g = RIDGE_IN - 0.2
        b = b - ext(ring(g, RIDGE_W + 0.4), RIDGE_H + 0.3 + 0.01, T - RIDGE_H - 0.3)
    else:
        b = b + ext(ring(RIDGE_IN, RIDGE_W), RIDGE_H, T - 0.01)
    return b

LID_ROOF, LID_WALL, LID_IN = 1.6, 3.6, 11.8     # roof thickness, wall thickness, inside depth above the plane (pieces stand 11.3 proud)
def lid_shell():
    """Hollow cover, printed roof down. Walls rest on the tray rim, the tray ridge enters a groove in the wall's bottom edge."""
    Hh = LID_ROOF + LID_IN
    b = body(rrect(W_, D_, 5.0, W_ / 2, D_ / 2), Hh, c=0.6, top=False, bottom=True)
    b = b - ext(rrect(W_ - 2 * LID_WALL, D_ - 2 * LID_WALL, 1.4, W_ / 2, D_ / 2), LID_IN + 0.01, LID_ROOF)
    ring = lambda inset, w: rrect(W_ - 2 * inset, D_ - 2 * inset, max(1.0, 5.0 - inset), W_ / 2, D_ / 2).difference(
        rrect(W_ - 2 * (inset + w), D_ - 2 * (inset + w), max(0.8, 5.0 - inset - w), W_ / 2, D_ / 2))
    return b - ext(ring(RIDGE_IN - 0.2, RIDGE_W + 0.4), RIDGE_H + 0.3 + 0.01, Hh - RIDGE_H - 0.3)

def case(lid=False, with_pieces=False):
    if lid: return lid_shell()
    P = pieces(); L = {n: lying(P[n], n) for n in P}
    b = shell(False); cuts = []; placed = []
    for i, (col, names) in enumerate(ROWS):
        for j, n in enumerate(names):
            x = X0 + j * PITCH
            if lid: x = -x
            y = row_y(i) + CLR_P
            cuts.append(pocket(L[n], lid).translate((x + W_ / 2, y, T)))
            if with_pieces: placed.append((L[n].translate((x + W_ / 2, y, T)), col, n))
    # pockets cut in one boolean; the pawn's thinner body keeps the plane at T so its floor is thicker
    cut = U(cuts)
    b = b - cut
    return (b, placed) if with_pieces else b

def overhang(m, zmin=0.8):
    t = tm(m); nz = t.face_normals[:, 2]; cz = t.triangles_center[:, 2]
    return float(t.area_faces[(nz < -0.7072) & (cz > zmin)].sum())

if __name__ == "__main__":
    tray, pl = case(False, True); lid = case(True)
    q = Product("P3", "chess_case", "Chess case: tray and lid")
    q.part("tray", tray, BLACK, infill=0.15); q.part("lid", lid, BLACK, infill=0.15)
    P = pieces()
    def stand(m, name): return m
    sc = [(tray, BLACK)]
    for L, col, n in pl:
        sc.append((L, IVORY if col == "ivory" else BLACK))
    q.scene("chess_tray", sc)
    q.scene("chess_tray_bare", [(tray, BLACK)])
    # exploded: lid hovering above the tray, turned over exactly as it sits when closed (printed frame: x' = -x, z' = T - z)
    Hh = LID_ROOF + LID_IN
    flip = lid.transform([[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, -1, Hh]]).translate((0, 0, T + 30))   # turned over: open side faces the tray
    q.scene("chess_case_exploded", sc + [(flip, BLACK)])
    rep = q.export()
    print("case:", round(W_, 1), "x", round(D_, 1), "x", T, "per half; closed height", round(2 * T, 1))
    for lab, m in (("tray", tray), ("lid", lid)):
        t = tm(m); print(lab, "watertight", t.is_watertight, "bodies", len(t.split(only_watertight=False)), "g@15%", round(grams(m, 0.15), 1),
                         "h", round(hours(grams(m, 0.15)), 2), "overhang mm2", round(overhang(m), 1), "bbox", [round(v, 1) for v in t.bounds[1] - t.bounds[0]])
    json.dump(rep, open(f"{OUT}/chess_case_report.json", "w"), indent=1)
