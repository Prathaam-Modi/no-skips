"""Seed the Play line test projects (P1 Crosses, P3 pawn test) from print-files/stl and queue them for slicing.
Run from the repo root: python3 tools/seed_play.py"""
import os, sys, json
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools", "orders", "print-repo", "tools"))
import bambu3mf as b
S = os.path.join(ROOT, "print-files", "stl"); A = os.path.join(ROOT, "print-files", "a1_ready")
s = lambda d: (lambda f: os.path.join(S, d, f))
ST = {"sparse_infill_density": "25%", "wall_loops": "3"}
queue = []
def seed(folder, fname, objs, layer="0.20"):
    os.makedirs(os.path.join(A, folder), exist_ok=True)
    b.seed(os.path.join(A, folder, fname), objs, layer, {})
    queue.append({"project": f"{folder}/{fname}", "layer": layer, "over": dict(ST)})
c = s("P1_crosses")
coaster = lambda i: dict(name=f"P1 coaster {i}", parts=[(c("P1_1_coaster_BLACK_x9.stl"), 1, "coaster"), (c("P1_2_x_inlay_IVORY_x9.stl"), 3, "x_inlay"), (c("P1_3_o_inlay_RED_x9.stl"), 2, "o_inlay")], settings=ST)
seed("P1_crosses", "P1_coasters_x3.3mf", [coaster(i) for i in range(1, 4)])   # print this plate three times for the set of nine
seed("P1_crosses", "P1_caddy.3mf", [dict(name="P1 caddy", parts=[(c("P1_4_caddy_BLACK.stl"), 1, "caddy")], settings=dict(ST, sparse_infill_density="20%"))])
p = s("P3_pawn_test")
# one colour per plate: a black and an ivory pawn together sliced at 7 h and 111 g (colour swap every layer)
seed("P3_pawn_test", "P3_pawn_black.3mf", [dict(name="P3 pawn black", parts=[(p("P3_1_pawn_BLACK.stl"), 1, "pawn")], settings=ST)])
seed("P3_pawn_test", "P3_pawn_ivory.3mf", [dict(name="P3 pawn ivory", parts=[(p("P3_1_pawn_BLACK.stl"), 3, "pawn")], settings=ST)])
seed("P3_pawn_test", "P3_pawns_black_x8.3mf", [dict(name=f"P3 pawn {i}", parts=[(p("P3_1_pawn_BLACK.stl"), 1, "pawn")], settings=ST) for i in range(1, 9)])
t = s("P2_tangram")
# one colour per plate: ivory pieces on one plate, the red piece alone (batch red pieces from several sets when printing for sale)
ivory = [("large_a", "P2_1_large_a_IVORY.stl"), ("large_b", "P2_2_large_b_IVORY.stl"), ("medium", "P2_3_medium_IVORY.stl"), ("small_a", "P2_4_small_a_IVORY.stl"), ("square", "P2_5_square_IVORY.stl"), ("small_b", "P2_7_small_b_IVORY.stl")]
seed("P2_tangram", "P2_pieces_ivory.3mf", [dict(name=f"P2 {n}", parts=[(t(f), 3, n)], settings=dict(ST)) for n, f in ivory])
seed("P2_tangram", "P2_piece_red.3mf", [dict(name="P2 para red", parts=[(t("P2_6_para_RED.stl"), 2, "para")], settings=dict(ST))])
seed("P2_tangram", "P2_frame.3mf", [dict(name="P2 frame", parts=[(t("P2_8_frame_BLACK.stl"), 1, "frame")], settings=dict(ST, sparse_infill_density="20%"))])
q = os.path.join(A, "SLICE_QUEUE.json"); json.dump({"jobs": queue}, open(q, "w"), indent=1)
print("ok", len(queue))
