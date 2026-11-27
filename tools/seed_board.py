"""Seed the P3 chess board projects (quadrants A and B, keys, joint test) and queue only them for slicing. Run from the repo root."""
import os, sys, json
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools", "orders", "print-repo", "tools"))
import bambu3mf as b
S = os.path.join(ROOT, "print-files", "stl", "P3_chess_board"); A = os.path.join(ROOT, "print-files", "a1_ready")
t = lambda f: os.path.join(S, f)
ST = {"sparse_infill_density": "15%", "wall_loops": "3"}
queue = []
ONLY = sys.argv[1] if len(sys.argv) > 1 else None   # e.g. "joint": seed and queue only the joint test (keeps the other slices untouched)
def seed(fname, objs, over):
    if ONLY and ONLY not in fname: return
    d = os.path.join(A, "P3_chess_board"); os.makedirs(d, exist_ok=True)
    b.seed(os.path.join(d, fname), objs, "0.20", {})
    queue.append({"project": f"P3_chess_board/{fname}", "layer": "0.20", "over": dict(over)})
b.GAP = 2.0   # a 180 mm quadrant only fits beside the A1 keep-out corner with a 2 mm jump
# board top prints face down on the textured PEI plate; ivory squares only in the first 0.6 mm (slot 3), body black (slot 1)
seed("P3_board_quad_A.3mf", [dict(name="P3 board quadrant A", parts=[(t("P3_1_quad_A_BLACK_x2.stl"), 1, "quad_A"), (t("P3_2_quad_A_ivory_IVORY_x2.stl"), 3, "quad_A_ivory")], settings=ST)], ST)
seed("P3_board_quad_B.3mf", [dict(name="P3 board quadrant B", parts=[(t("P3_3_quad_B_BLACK_x2.stl"), 1, "quad_B"), (t("P3_4_quad_B_ivory_IVORY_x2.stl"), 3, "quad_B_ivory")], settings=ST)], ST)
b.GAP = 6.0
K = dict(ST)   # 3 mm keys print solid from walls and top/bottom layers anyway; a 100% process override fails to slice (code -18)
seed("P3_board_keys_x8.3mf", [dict(name=f"P3 key {i}", parts=[(t("P3_5_key_IVORY_x8.stl"), 3, "key")], settings=K) for i in range(1, 9)], K)
seed("P3_board_joint_test.3mf", [dict(name="P3 coupon left", parts=[(t("P3_6_coupon_left_BLACK.stl"), 1, "coupon_left")], settings=ST),
     dict(name="P3 coupon right", parts=[(t("P3_7_coupon_right_BLACK.stl"), 1, "coupon_right")], settings=ST)] +
     [dict(name=f"P3 test key {n} dot", parts=[(t(f), 1, f"testkey_{n}")], settings=K) for n, f in ((1, "P3_8_testkey_1dot_BLACK.stl"), (2, "P3_9_testkey_2dot_BLACK.stl"), (3, "P3_10_testkey_3dot_BLACK.stl"), (4, "P3_11_testkey_4dot_BLACK.stl"))], ST)
json.dump({"jobs": queue}, open(os.path.join(A, "SLICE_QUEUE.json"), "w"), indent=1)
print("ok", len(queue))
