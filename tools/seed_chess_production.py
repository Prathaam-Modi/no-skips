"""Seed the remaining P3 Six Cuts production plates (28 Nov): ivory pawns and queen, and the whole black set. Queues only these. Run from the repo root.
Tiered infill: king, queen, pawns solid (zig-zag, Bambu rejects 100% with grid); rook, knight, bishop 40%. Same colour-pair pieces share a plate so the wipe tower is paid once."""
import os, sys, json
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools", "orders", "print-repo", "tools"))
import bambu3mf as b
S = os.path.join(ROOT, "print-files", "stl", "P3_chess"); A = os.path.join(ROOT, "print-files", "a1_ready")
t = lambda f: os.path.join(S, f)
SOLID = {"sparse_infill_density": "100%", "sparse_infill_pattern": "zig-zag", "wall_loops": "3"}
MID = {"sparse_infill_density": "40%", "wall_loops": "3"}
BLK, IVO, RED = 1, 3, 2
def one(name, parts, st): return dict(name=name, parts=parts, settings=st)
PLATES = {
 "P3_ivory_pawns_x8": [one(f"P3 ivory pawn {i}", [(t("P3_9_pawn_i_IVORY_x8.stl"), IVO, "pawn")], SOLID) for i in range(1, 9)],
 "P3_ivory_queen": [one("P3 ivory queen", [(t("P3_13_queen_i_IVORY.stl"), IVO, "queen"), (t("P3_14_queen_dot_i_RED.stl"), RED, "queen_dot")], SOLID)],
 "P3_black_pawns_x8": [one(f"P3 black pawn {i}", [(t("P3_1_pawn_b_BLACK_x8.stl"), BLK, "pawn")], SOLID) for i in range(1, 9)],
 "P3_black_minors_40": [one(f"P3 black {n} {i}", [(t(f), BLK, n)], MID) for n, f in
        [("rook", "P3_2_rook_b_BLACK_x2.stl"), ("knight", "P3_3_knight_b_BLACK_x2.stl"), ("bishop", "P3_4_bishop_b_BLACK_x2.stl")] for i in (1, 2)],
 "P3_black_king_queen": [one("P3 black king", [(t("P3_7_king_b_BLACK.stl"), BLK, "king"), (t("P3_8_king_top_b_RED.stl"), RED, "king_top")], SOLID),
                         one("P3 black queen", [(t("P3_5_queen_b_BLACK.stl"), BLK, "queen"), (t("P3_6_queen_dot_b_RED.stl"), RED, "queen_dot")], SOLID)],
}
d = os.path.join(A, "P3_chess"); os.makedirs(d, exist_ok=True)
jobs = []
for name, objs in PLATES.items():
    n = b.seed(os.path.join(d, name + ".3mf"), objs, "0.20", {})
    print(name, "plates:", n)
    jobs.append({"project": f"P3_chess/{name}.3mf", "layer": "0.20", "over": MID if "minors" in name else SOLID})
json.dump({"jobs": jobs}, open(os.path.join(A, "SLICE_QUEUE.json"), "w"), indent=1)
print("ok", len(jobs))
