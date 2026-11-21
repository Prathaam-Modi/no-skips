"""No Skips Bengaluru edition (Dec 2026): E1 numbered coin and E2 three-peg wristband rail.

Both reuse the C3 coin and A3 rail geometry. No artist name, logo or artwork: city, date and a number only.
All text is at least 4 mm tall (ns.MIN_TEXT).

Run: python3 build7.py                      build, export STLs and scenes
     NS_NIGHT=13.12 NS_NO=042 python3 build7.py   one numbered coin (night 12.12 or 13.12, number 001 to 100)
"""
import math, json, sys, os
from ns import *
from shapely.geometry import Polygon, box
import build, build2

P = {}
FR_H = 4.9
RAISE = 0.6
R = math.radians
flip = build.flip
place = build.place
NIGHT = os.environ.get("NS_NIGHT", "12.12")
NUM = os.environ.get("NS_NO", "001")

def build_edition_coin():
    p = Product("E1", "blr_coin", "Bengaluru Coin")
    a = np.linspace(0, 2 * math.pi, 720, endpoint=False)
    rr = 21.0 - 0.32 * (1 + np.cos(72 * a)) / 2
    reeded = Polygon(np.c_[rr * np.cos(a), rr * np.sin(a)])
    # back: three lines, 6.5 / 6.5 / 4.2 mm tall, mirrored because the back face prints down
    lines = unary_union([fit_text("BLR", 6.5, 30, 0, 9.0), fit_text(NIGHT, 6.5, 30, 0, 0.0), fit_text(f"{NUM}/100", 4.4, 32, 0, -9.2)])
    back = affinity.scale(lines, -1, 1)
    inlay = ext(back, 0.4, 0)
    coin = U([body(reeded, 3.3, bottom=True, top=False, c=0.4, steps=2), ext(circle(20.0).difference(circle(18.2)), 0.7, 3.3)]) - inlay
    sil = ext(build.dj(), 0.5, 3.3)
    ring = circle(24.4).difference(circle(21.2)).union(box(-7, -29.5, 7, -21.6)).union(circle(5.6, 0, 27.6))
    ring = ring.difference(circle(21.2)).difference(circle(2.6, 0, 28.4)).difference(box(-0.6, -30, 0.6, -20.5))
    frame = body(ring, FR_H, c=0.4, steps=2, bottom=True)
    # coin seats on a 0.5 mm floor lip (overlaps the coin back by 0.6 to 0.9 mm) and under a 45 degree top lip (0.5 to 0.8 mm over the face), so it cannot fall out
    lip = ext(circle(21.5).difference(circle(20.1)), 0.5, 0) + (cyl(21.5, 1.1, 3.8, seg=180) - cyl(21.21, 1.01, 3.795, r2=20.2, seg=180) - cyl(20.2, 0.4, 4.7, seg=180))
    frame = frame + (lip - cube(1.4, 10, 6, 0, -21, 0))
    foot = body(rrect(40, 18, 5), 9.0) - cube(14.5, FR_H + 0.4, 7.0, 0, 0, 2.2)
    mark = ext(pill(0, -6.0, 26, 1.8), RAISE, 9.0)
    p.part("coin", coin, BLACK, infill=1.0); p.part("silhouette", sil, RED, infill=1.0); p.part("back_text_inlay", inlay, RED, infill=1.0)
    p.part("frame", frame, BLACK, infill=1.0); p.part("foot", foot, BLACK, infill=0.3); p.part("foot_mark", mark, RED, infill=1.0)
    one = [(coin, BLACK), (sil, RED), (inlay, RED)]
    inframe = [(mv(m, 0, 0, 0.5), c) for m, c in one] + [(frame, BLACK)]
    stoodc = [(mv(rot(m, 90, 0, 0), 0, FR_H / 2, 2.2 + 29.5), c) for m, c in inframe]
    p.scene("blr_coin", place(stoodc + [(foot, BLACK), (mark, RED)], rz=-14, x=-16, y=8) + place([(flip(m), c) for m, c in one], rz=10, x=34, y=-22))
    p.note = f"Bengaluru edition coin, night {NIGHT}, number {NUM} of 100. Same coin, frame and foot as C3 Gig Coin. Back text 6.5 / 6.5 / 4.2 mm."
    P["E1"] = p

def build_edition_rail():
    p = Product("E2", "blr_rail", "Bengaluru Rail")
    xs = (-35, 0, 35); L = 130.0
    rail = body(rrect(L, 36, 4), 8.0, c=0.6)
    rail = rail - U([cyl(3.15, 8.2, -0.1, x, -7, seg=40) for x in xs])
    rail = rail - U([cyl(2.2, 8.2, -0.1, x, -7, seg=32) + cyl(2.2, 2.41, 5.6, x, -7, r2=4.6, seg=32) for x in (-58, 58)])
    art = unary_union([fit_text(f"BLR {NIGHT}", 6.0, 70, -58, 8.5, "l"), wave(build2.W20, 14, 8.5, 2.1, 1.4, 12, 3)])
    red = ext(art, RAISE, 8.0)
    shaft = cyl(3.0, 7.5, 14.7, seg=40)
    ribs = U([mv(rot(cube(0.7, 0.7, 6.5, 0, 0, 0), 0, 0, k * 120), 3.0 * math.cos(R(k * 120)), 3.0 * math.sin(R(k * 120)), 14.7) for k in range(3)])
    peg = U([body(circle(6.5), 2.5, c=0.5, steps=2, bottom=True, top=False), cyl(3.5, 12.3, 2.45, seg=40), shaft, ribs])
    peg = peg - (cyl(4, 0.8, 21.4, seg=40) - cyl(3.0, 0.8, 21.4, r2=2.4, seg=40))
    p.part("rail", rail, BLACK, infill=0.3); p.part("name_and_wave", red, RED, infill=1.0); p.part("peg", peg, RED, qty=3, infill=1.0)
    pegs_on = [(mv(rot(peg, 180, 0, 0), x, -7, 22.7), RED) for x in xs]
    wall = [(mv(rot(m, 90, 0, 0), 0, 0, 60), c) for m, c in [(rail, BLACK), (red, RED)] + pegs_on]
    p.scene("blr_rail", wall)
    loose = [(mv(rot(peg, 180, 0, 0), x, -7, 22.7 + (0 if x < 0 else 28)), RED) for x in xs]
    p.scene("blr_rail_build", [(mv(rot(m, 90, 0, 0), 0, 0, 60), c) for m, c in [(rail, BLACK), (red, RED)] + loose])
    p.note = f"Bengaluru edition rail 130 x 36 x 8, three pegs 35 mm apart, text BLR {NIGHT}. Same pegs and sockets as A3 Rail. Screws 116 mm apart."
    P["E2"] = p

if __name__ == "__main__" and sys.argv[1:2] != ["render"]:
    build_edition_coin(); build_edition_rail()
    rep = {}
    for k, p in P.items():
        rep[k] = p.export(); print(k, p.name, rep[k]["grams"], "g")
        for x in rep[k]["parts"]: print("  ", x["file"], x["size"], x["grams"])
    mn = min((z for s, z in TEXT_LOG), default=99); print("smallest text", mn, "mm")

SHOTS7 = {"blr_coin": dict(az=-28, el=30, zoom=1.0), "blr_rail": dict(az=-30, el=22, zoom=1.0), "blr_rail_build": dict(az=-30, el=22, zoom=1.0)}
if __name__ == "__main__" and sys.argv[1:2] == ["render"]:
    build_edition_coin(); build_edition_rail()
    import render
    render.SHOTS.update(SHOTS7)
    for s in sys.argv[2].split(","): render.render(s)
