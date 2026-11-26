"""Seed the P3 Six Cuts test plate (ivory king at 15%, ivory king solid, ivory pawn) and queue only it. Run from the repo root."""
import os, sys, json
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools", "orders", "print-repo", "tools"))
import bambu3mf as b
S = os.path.join(ROOT, "print-files", "stl", "P3_chess"); A = os.path.join(ROOT, "print-files", "a1_ready")
t = lambda f: os.path.join(S, f)
ST = {"sparse_infill_density": "15%", "wall_loops": "3"}
# Bambu rejects 100% with the default grid pattern (code -18 on the board keys); zig-zag is valid at 100%
SOLID = {"sparse_infill_density": "100%", "sparse_infill_pattern": "zig-zag", "wall_loops": "3"}
king = lambda name, st: dict(name=name, parts=[(t("P3_15_king_i_IVORY.stl"), 3, "king"), (t("P3_16_king_top_i_RED.stl"), 2, "king_top")], settings=st)
objs = [king("P3 king 15pc", ST), king("P3 king solid", SOLID),
        dict(name="P3 pawn 15pc", parts=[(t("P3_9_pawn_i_IVORY_x8.stl"), 3, "pawn")], settings=ST)]
d = os.path.join(A, "P3_chess"); os.makedirs(d, exist_ok=True)
b.seed(os.path.join(d, "P3_test_kings_pawn.3mf"), objs, "0.20", {})
json.dump({"jobs": [{"project": "P3_chess/P3_test_kings_pawn.3mf", "layer": "0.20", "over": ST}]}, open(os.path.join(A, "SLICE_QUEUE.json"), "w"), indent=1)
print("ok")
