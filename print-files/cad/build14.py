"""Play line P2 Tangram tray (24 Nov 2026): seven flat pieces in a black frame, six ivory and one red.
The solved picture is the square. Side S = 3 grid modules (135 mm). Rules kept: no supports, no joints, no text,
colour is a whole piece (one colour per plate), logo debossed under the frame.
Usage: NS_OUT=/tmp/out python3 build14.py"""
import math, json
from ns import *
from build2 import logo

GRID = 45.0
S = 3 * GRID                 # solved square, 135 mm
U4 = S / 4.0                 # tangram drawn on a 4 x 4 grid
PT = 5.0                     # piece thickness
GAP = 0.5                    # clearance between pieces and to the frame
FB, FR = 3.0, 2.0            # frame floor and rim height above the floor (pieces stand 3 mm proud)
FW = 6.0                     # frame wall
RC = 1.5                     # rounded piece corners

# piece outlines on the 4 x 4 grid; verified below to tile the square exactly
RAW = {
    "large_a":  [(0, 0), (4, 0), (2, 2)],
    "large_b":  [(0, 0), (2, 2), (0, 4)],
    "medium":   [(4, 4), (2, 4), (4, 2)],
    "small_a":  [(4, 0), (4, 2), (3, 1)],
    "square":   [(3, 1), (4, 2), (3, 3), (2, 2)],
    "para":     [(0, 4), (2, 4), (3, 3), (1, 3)],
    "small_b":  [(1, 3), (3, 3), (2, 2)],
}
def outline(name):
    return Polygon([((x - 2) * U4, (y - 2) * U4) for x, y in RAW[name]])
def piece2d(name):
    p = outline(name)
    return p.buffer(-(GAP / 2 + RC), join_style=2).buffer(RC, quad_segs=12)

def check_tiling():
    ps = [outline(n) for n in RAW]
    assert abs(sum(p.area for p in ps) - S * S) < 1e-6, "areas do not add up to the square"
    for i in range(len(ps)):
        for j in range(i + 1, len(ps)):
            assert ps[i].intersection(ps[j]).area < 1e-6, (i, j)
    assert abs(unary_union(ps).area - S * S) < 1e-6
check_tiling()

def piece(name):
    p = piece2d(name)
    c = p.centroid
    p = affinity.translate(p, -c.x, -c.y)
    return body(p, PT, c=0.6, top=True, bottom=True), (c.x, c.y)

def frame():
    inner = S + GAP * 2
    outer = inner + 2 * FW
    h = FB + FR
    m = body(rrect(outer, outer, 7.0), h, c=0.6, top=True, bottom=True)
    m = m - ext(rrect(inner, inner, 1.2), FR + 0.1, FB)
    lg = ext(affinity.scale(logo(0, 0, 1.2), -1, 1, origin=(0, 0)), 0.6, -0.01)
    return m - lg, outer, h

if __name__ == "__main__":
    p = Product("P2", "tangram", "Tangram tray")
    cols = {"large_a": IVORY, "large_b": IVORY, "medium": IVORY, "small_a": IVORY, "small_b": IVORY, "square": IVORY, "para": RED}
    pcs = {}
    for n in RAW:
        m, c = piece(n); pcs[n] = (m, c)
        p.part(n, m, cols[n], infill=0.25)
    fr, outer, fh = frame()
    p.part("frame", fr, BLACK, infill=0.2)
    p.note = f"Square {S:.0f} mm, frame {outer:.0f} x {outer:.0f} x {fh:.1f} mm, pieces {PT:.0f} mm thick. One colour per plate: frame black, six pieces ivory, one piece red."
    # scenes: solved square in the frame, and a rearranged "cat" is left to the shot list
    solved = [(mv(fr, 0, 0, 0), BLACK)]
    for n, (m, c) in pcs.items():
        solved.append((mv(m, c[0], c[1], FB), cols[n]))
    p.scene("tangram", solved)
    # puzzle shot: the empty frame with the pieces mid-play, rotated and spread on the table (render only)
    place = {"large_a": (-175, 30, 20), "large_b": (-125, -150, -35), "medium": (150, 90, 160), "small_a": (125, -110, 70), "small_b": (0, -135, 200), "square": (160, -5, 30), "para": (20, 125, -15)}
    loose = [(mv(fr, 0, 0, 0), BLACK)]
    for n, (m, c) in pcs.items():
        x, y, a = place[n]
        loose.append((mv(m.rotate((0, 0, a)), x, y, 0), cols[n]))
    p.scene("tangram_loose", loose)
    rep = p.export()
    print(rep["grams"], [(x["file"], x["size"], x["grams"]) for x in rep["parts"]])
    json.dump(rep, open(f"{OUT}/tangram_report.json", "w"), indent=1)
