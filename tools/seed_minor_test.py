"""Seed the P3 Six Cuts tiered-weight test plate: one ivory rook, knight and bishop at 40% infill, to compare with the solid king. Queues only it. Run from the repo root."""
import os, sys, json
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools", "orders", "print-repo", "tools"))
import bambu3mf as b
S = os.path.join(ROOT, "print-files", "stl", "P3_chess"); A = os.path.join(ROOT, "print-files", "a1_ready")
t = lambda f: os.path.join(S, f)
MID = {"sparse_infill_density": "40%", "wall_loops": "3"}
objs = [dict(name=f"P3 {n} 40pc", parts=[(t(f), 3, n)], settings=MID) for n, f in
        [("rook", "P3_10_rook_i_IVORY_x2.stl"), ("knight", "P3_11_knight_i_IVORY_x2.stl"), ("bishop", "P3_12_bishop_i_IVORY_x2.stl")]]
d = os.path.join(A, "P3_chess"); os.makedirs(d, exist_ok=True)
b.seed(os.path.join(d, "P3_test_minors_40.3mf"), objs, "0.20", {})
json.dump({"jobs": [{"project": "P3_chess/P3_test_minors_40.3mf", "layer": "0.20", "over": MID}]}, open(os.path.join(A, "SLICE_QUEUE.json"), "w"), indent=1)
print("ok")
