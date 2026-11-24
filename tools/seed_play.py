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
seed("P3_pawn_test", "P3_pawn_test.3mf", [dict(name="P3 pawn black", parts=[(p("P3_1_pawn_BLACK.stl"), 1, "pawn")], settings=ST), dict(name="P3 pawn ivory", parts=[(p("P3_1_pawn_BLACK.stl"), 3, "pawn")], settings=ST)])
q = os.path.join(A, "SLICE_QUEUE.json"); json.dump({"jobs": queue}, open(q, "w"), indent=1)
print("ok", len(queue))
