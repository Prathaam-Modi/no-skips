"""Seed the P2 tangram NIGHT colourway (black pieces, ivory frame) and a double red-piece plate, and queue only them. Run from the repo root.
BONE (ivory pieces, black frame) already exists as P2_pieces_ivory + P2_frame. The red piece is the same in both, so two sets need the red plate twice.
Same settings as tools/seed_play.py (0.20 mm, 3 walls, pieces 25%, frame 20%)."""
import os, sys, json
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools", "orders", "print-repo", "tools"))
import bambu3mf as b
S = os.path.join(ROOT, "print-files", "stl", "P2_tangram"); A = os.path.join(ROOT, "print-files", "a1_ready", "P2_tangram")
t = lambda f: os.path.join(S, f)
ST = {"sparse_infill_density": "25%", "wall_loops": "3"}
pieces = [("large_a", "P2_1_large_a_IVORY.stl"), ("large_b", "P2_2_large_b_IVORY.stl"), ("medium", "P2_3_medium_IVORY.stl"),
          ("small_a", "P2_4_small_a_IVORY.stl"), ("square", "P2_5_square_IVORY.stl"), ("small_b", "P2_7_small_b_IVORY.stl")]
jobs = []
def seed(fname, objs):
    b.seed(os.path.join(A, fname), objs, "0.20", {})
    jobs.append({"project": f"P2_tangram/{fname}", "layer": "0.20", "over": dict(ST)})
seed("P2_pieces_black.3mf", [dict(name=f"P2 {n} black", parts=[(t(f), 1, n)], settings=dict(ST)) for n, f in pieces])
seed("P2_frame_ivory.3mf", [dict(name="P2 frame ivory", parts=[(t("P2_8_frame_BLACK.stl"), 3, "frame")], settings=dict(ST, sparse_infill_density="20%"))])
seed("P2_piece_red_x2.3mf", [dict(name=f"P2 para red {i}", parts=[(t("P2_6_para_RED.stl"), 2, "para")], settings=dict(ST)) for i in (1, 2)])
json.dump({"jobs": jobs}, open(os.path.join(ROOT, "print-files", "a1_ready", "SLICE_QUEUE.json"), "w"), indent=1)
print("ok")
