"""Seed the P6C Dealer button projects (28 Nov 2026). Run from the repo root: python3 tools/seed_p6c.py
Every button body is ivory, so a whole set (and several sets) share one plate and one wipe tower; the red and black inlays
live only in the first 3 layers. Solid: 100% zig-zag (Bambu rejects 100% with grid), 3 walls.
Writes the projects only; the slice queue jobs are printed, not written (SLICE_QUEUE.json is shared)."""
import os, sys, json
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools", "orders", "print-repo", "tools"))
import bambu3mf as b
S = os.path.join(ROOT, "print-files", "stl", "P6C_dealer_button"); A = os.path.join(ROOT, "print-files", "a1_ready")
t = lambda f: os.path.join(S, f)
SOLID = {"sparse_infill_density": "100%", "sparse_infill_pattern": "zig-zag", "wall_loops": "3"}
BLK, RED, IVO = 1, 2, 3
def dealer(i): return dict(name=f"P6C dealer {i}", parts=[(t("P6C_1_dealer_IVORY.stl"), IVO, "dealer"), (t("P6C_2_dealer_front_dealer_RED.stl"), RED, "dealer_text")], settings=SOLID)
def bb(i): return dict(name=f"P6C big blind {i}", parts=[(t("P6C_3_big_blind_IVORY.stl"), IVO, "big_blind"), (t("P6C_4_big_blind_front_bb_BLACK.stl"), BLK, "bb_text")], settings=SOLID)
def sb(i): return dict(name=f"P6C small blind {i}", parts=[(t("P6C_5_small_blind_IVORY.stl"), IVO, "small_blind"), (t("P6C_6_small_blind_front_sb_BLACK.stl"), BLK, "sb_text")], settings=SOLID)
def sets(n): return [f(i) for i in range(1, n + 1) for f in (dealer, bb, sb)]
PLATES = {
    "P6C_set_x1": sets(1),                       # one order, about 2.4 h
    "P6C_sets_x4": sets(4),                      # batch for stock, one tower for twelve buttons
    "P6C_dealer_x6": [dealer(i) for i in range(1, 7)],   # dealer button sold alone (ivory and red only)
}
if __name__ == "__main__":
    d = os.path.join(A, "P6C_dealer_button"); os.makedirs(d, exist_ok=True)
    jobs = []
    for name, objs in PLATES.items():
        n = b.seed(os.path.join(d, name + ".3mf"), objs, "0.20", {})
        assert n == 1, (name, n, "does not fit one plate")
        print(name, "objects:", len(objs), "plates:", n)
        jobs.append({"project": f"P6C_dealer_button/{name}.3mf", "layer": "0.20", "over": dict(SOLID)})
    print(json.dumps(jobs, indent=1))
