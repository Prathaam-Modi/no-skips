"""Seed the P3 Six Cuts queen test plate (one ivory queen with the flush red dot, solid) and queue only it. Run from the repo root."""
import os, sys, json
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools", "orders", "print-repo", "tools"))
import bambu3mf as b
S = os.path.join(ROOT, "print-files", "stl", "P3_chess"); A = os.path.join(ROOT, "print-files", "a1_ready")
t = lambda f: os.path.join(S, f)
# queen is solid in the tiered plan (king, queen, pawns solid); zig-zag because Bambu rejects 100% with the default grid pattern
ST = {"sparse_infill_density": "100%", "sparse_infill_pattern": "zig-zag", "wall_loops": "3"}
objs = [dict(name="P3 queen solid", parts=[(t("P3_13_queen_i_IVORY.stl"), 3, "queen"), (t("P3_14_queen_dot_i_RED.stl"), 2, "queen_dot")], settings=ST)]
d = os.path.join(A, "P3_chess"); os.makedirs(d, exist_ok=True)
b.seed(os.path.join(d, "P3_test_queen.3mf"), objs, "0.20", {})
json.dump({"jobs": [{"project": "P3_chess/P3_test_queen.3mf", "layer": "0.20", "over": ST}]}, open(os.path.join(A, "SLICE_QUEUE.json"), "w"), indent=1)
print("ok")
