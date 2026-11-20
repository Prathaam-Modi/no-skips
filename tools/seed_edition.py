"""Seed the Bengaluru edition Bambu projects (E1 coin, E2 rail) from print-files/stl. Run from repo root."""
import os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools", "orders", "print-repo", "tools"))
import bambu3mf as b
S = os.path.join(ROOT, "print-files", "stl"); A = os.path.join(ROOT, "print-files", "a1_ready")
full = {"sparse_infill_density": "100%", "sparse_infill_pattern": "zig-zag", "wall_loops": "3"}
c = lambda f: os.path.join(S, "E1_blr_coin", f); r = lambda f: os.path.join(S, "E2_blr_rail", f)
b.seed(os.path.join(A, "E1_blr_coin", "E1_blr_coin.3mf"), [
    dict(name="E1 coin", parts=[(c("E1_1_coin_BLACK.stl"), 1, "coin"), (c("E1_2_silhouette_RED.stl"), 2, "silhouette"), (c("E1_3_back_text_inlay_RED.stl"), 2, "back_text_inlay")], settings=full),
    dict(name="E1 frame", parts=[(c("E1_4_frame_BLACK.stl"), 1, "frame")], settings=dict(full, wall_loops="4")),
    dict(name="E1 foot", parts=[(c("E1_5_foot_BLACK.stl"), 1, "foot"), (c("E1_6_foot_mark_RED.stl"), 2, "foot_mark")], settings={"sparse_infill_density": "20%", "wall_loops": "3"}),
], "0.12", {})
b.seed(os.path.join(A, "E2_blr_rail", "E2_blr_rail_plate1_rail.3mf"), [
    dict(name="E2 rail", parts=[(r("E2_1_rail_BLACK.stl"), 1, "rail"), (r("E2_2_name_and_wave_RED.stl"), 2, "name_and_wave")], settings={"sparse_infill_density": "30%", "wall_loops": "3"})], "0.20", {})
b.seed(os.path.join(A, "E2_blr_rail", "E2_blr_rail_plate2_pegs_red.3mf"), [
    dict(name=f"E2 peg {i}", parts=[(r("E2_3_peg_RED_x3.stl"), 2, "peg")], settings=dict(full, wall_loops="4")) for i in (1, 2, 3)], "0.20", {})
print("ok")
