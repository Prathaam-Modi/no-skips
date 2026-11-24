"""Seed the V3 Bambu projects (D16 Lean, D17 Bookends, D18 Ripple, D19 Key rail, G1 Patched In) from print-files/stl and queue them for slicing.
Run from the repo root: python3 tools/seed_v3.py"""
import os, sys, json
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools", "orders", "print-repo", "tools"))
import bambu3mf as b
S = os.path.join(ROOT, "print-files", "stl"); A = os.path.join(ROOT, "print-files", "a1_ready")
s = lambda d: (lambda f: os.path.join(S, d, f))
ST = {"sparse_infill_density": "20%", "wall_loops": "3"}
queue = []
def seed(folder, fname, objs, layer="0.20", over=None):
    p = os.path.join(A, folder, fname); b.seed(p, objs, layer, over or {})
    queue.append({"project": f"{folder}/{fname}", "layer": layer, "over": {"wall_loops": ST["wall_loops"], "sparse_infill_density": ST["sparse_infill_density"]}})
l = s("D16_lean")
seed("D16_lean", "D16_lean.3mf", [dict(name="D16 Lean", parts=[(l("D16_1_stand_BLACK.stl"), 1, "stand"), (l("D16_2_ridge_RED.stl"), 2, "ridge")], settings=ST)])
k = s("D17_bookends")
seed("D17_bookends", "D17_bookends.3mf", [dict(name=f"D17 bookend {i}", parts=[(k("D17_1_bookend_BLACK_x2.stl"), 1, "bookend"), (k("D17_2_ridge_RED_x2.stl"), 2, "ridge")], settings=ST) for i in (1, 2)])
r = s("D18_ripple")
seed("D18_ripple", "D18_ripple.3mf", [dict(name="D18 tray", parts=[(r("D18_1_tray_IVORY.stl"), 3, "tray")], settings=ST), dict(name="D18 dot", parts=[(r("D18_2_dot_RED.stl"), 2, "dot")], settings=dict(ST, wall_loops="4"))])
d = s("D19_keyrail")
seed("D19_keyrail", "D19_keyrail.3mf", [dict(name="D19 rail", parts=[(d("D19_1_rail_BLACK.stl"), 1, "rail")], settings=ST)] + [dict(name=f"D19 key hook {i}", parts=[(d("D19_2_key_hook_RED_x3.stl"), 2, "key_hook")], settings=dict(ST, wall_loops="4")) for i in (1, 2, 3)])
g = s("G1_patched_in")
seed("G1_patched_in", "G1_plug.3mf", [dict(name="G1 plug", parts=[(g("G1_1_plug_BLACK.stl"), 1, "plug"), (g("G1_2_plug_collar_RED.stl"), 2, "collar")], settings=dict(ST, wall_loops="4"))], "0.12")
seed("G1_patched_in", "G1_socket.3mf", [dict(name="G1 socket", parts=[(g("G1_3_socket_IVORY.stl"), 3, "socket")], settings=dict(ST, wall_loops="4"))], "0.12")
q = os.path.join(A, "SLICE_QUEUE.json"); json.dump({"jobs": queue}, open(q, "w"), indent=1)
print("ok", len(queue))
