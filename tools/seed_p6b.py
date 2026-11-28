"""Seed the P6B Hand rack Bambu projects (28 Nov 2026). Run from the repo root after print-files/cad/build_p6b_handrack.py.
Each rack is one object: body (slot 1 Black or slot 3 Ivory) plus the red cap (slot 2), which is the last 1.0 mm of the part,
so a plate has ONE colour change. Pairs per plate (four do not fit beside the prime tower). Does not touch SLICE_QUEUE.json:
the jobs are printed for the owner to add."""
import os, sys, json
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools", "orders", "print-repo", "tools"))
import bambu3mf as b
S = os.path.join(ROOT, "print-files", "stl", "P6B_hand_rack"); A = os.path.join(ROOT, "print-files", "a1_ready", "P6B_hand_rack")
t = lambda f: os.path.join(S, f)
BLK, RED, IVO = 1, 2, 3
RACK = {"wall_loops": "4", "sparse_infill_density": "25%", "sparse_infill_pattern": "gyroid", "top_shell_layers": "5", "bottom_shell_layers": "4"}
def rack(name, body, slot, cap):
    return dict(name=name, parts=[(t(body), slot, "rack"), (t(cap), RED, "red_cap")], settings=RACK)
PLATES = {
    "P6B_night_pair": [rack(f"P6B Night rack {i}", "P6B_1_rack_night_BLACK.stl", BLK, "P6B_2_rack_cap_night_RED.stl") for i in (1, 2)],
    "P6B_bone_pair": [rack(f"P6B Bone rack {i}", "P6B_3_rack_bone_IVORY.stl", IVO, "P6B_4_rack_cap_bone_RED.stl") for i in (1, 2)],
    "P6B_coupon_pair": [dict(name=f"P6B slot and stack coupon {i}", parts=[(t("P6B_5_coupon_BLACK_x2.stl"), BLK, "coupon"),
                         (t("P6B_6_coupon_cap_RED.stl"), RED, "red_cap")], settings=RACK) for i in (1, 2)],
}
os.makedirs(A, exist_ok=True)
jobs = []
for name, objs in PLATES.items():
    n = b.seed(os.path.join(A, name + ".3mf"), objs, "0.20", {})
    assert n == 1, (name, n)
    print(name, "plates:", n)
    jobs.append({"project": f"P6B_hand_rack/{name}.3mf", "layer": "0.20", "over": {k: v for k, v in RACK.items()}})
print(json.dumps({"jobs": jobs}, indent=1))
