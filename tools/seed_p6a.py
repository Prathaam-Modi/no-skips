"""Seed the P6A Deck box Bambu projects (28 Nov 2026). Run from the repo root after print-files/cad/build_p6a_deckbox.py.
One plate per colourway: body upright (floor on the PEI) and lid top face down, its red bar in the first 1.2 mm (the only colour
change on the plate). Plus the rail fit coupon (short body and two short lids at 0.30 and 0.35 mm a side), print it first.
Does not touch SLICE_QUEUE.json: it prints the jobs to add."""
import os, sys, json
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools", "orders", "print-repo", "tools"))
import bambu3mf as b
S = os.path.join(ROOT, "print-files", "stl", "P6A_deck_box"); A = os.path.join(ROOT, "print-files", "a1_ready")
t = lambda f: os.path.join(S, f)
BLK, RED, IVO = 1, 2, 3
ST = {"wall_loops": "3", "sparse_infill_density": "15%"}
OVER = {"wall_loops": "3", "sparse_infill_density": "15%", "seam_position": "back"}
def one(name, parts): return dict(name=name, parts=parts, settings=ST)
PLATES = {
 "P6A_night": [one("P6A Night body", [(t("P6A_1_body_night_BLACK.stl"), BLK, "body")]),
               one("P6A Night lid", [(t("P6A_2_lid_night_BLACK.stl"), BLK, "lid"), (t("P6A_3_lid_bar_night_RED.stl"), RED, "red_bar")])],
 "P6A_bone": [one("P6A Bone body", [(t("P6A_4_body_bone_IVORY.stl"), IVO, "body")]),
              one("P6A Bone lid", [(t("P6A_5_lid_bone_IVORY.stl"), IVO, "lid"), (t("P6A_6_lid_bar_bone_RED.stl"), RED, "red_bar")])],
 "P6A_rail_coupon": [one("P6A coupon body", [(t("P6A_7_coupon_body_BLACK.stl"), BLK, "coupon_body")]),
                     one("P6A coupon lid 0.30", [(t("P6A_8_coupon_lid_30_BLACK.stl"), BLK, "lid_30")]),
                     one("P6A coupon lid 0.35", [(t("P6A_9_coupon_lid_35_BLACK.stl"), BLK, "lid_35")])],
}
d = os.path.join(A, "P6A_deck_box"); os.makedirs(d, exist_ok=True)
jobs = []
for name, objs in PLATES.items():
    n = b.seed(os.path.join(d, name + ".3mf"), objs, "0.20", OVER)
    assert n == 1, (name, n)
    print(name, "plates:", n)
    jobs.append({"project": f"P6A_deck_box/{name}.3mf", "layer": "0.20", "over": OVER})
print(json.dumps(jobs))
