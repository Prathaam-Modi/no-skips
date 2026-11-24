"""D16 Lean: simple phone stand (Range V3 everyday, 24 Nov 2026). Replaces the Wedge as the everyday phone stand.
An A-frame profile extruded across the width: hollow inside so it is light and fast, prints upright as it stands with no
supports (front face 25 degrees off vertical, back leg 18 degrees, triangular hollow peaks at the top).
The top 4 mm is red: one colour change at one height (the red bar), no per-layer swaps.
Cable drops through a notch in the lip and runs out the back in a channel under the base (13 mm bridge).
Logo debossed underneath, mirrored to read from below. Usage: python3 build9.py"""
import math, json, os, sys
from ns import *
from ns import _cs
from build2 import logo
R = math.radians

def build_lean():
    p = Product("D16", "lean", "Lean")
    W = 70.0; ANG = 65.0; BACK = 72.0; H = 88.0; T = 3.6; BASE = 4.0; CAP = 4.0
    GROOVE = 12.0; SEAT = 6.0; LIP = 13.0; LIPT = 4.5
    yf = -48.0                                  # front of the lip
    ys = yf + LIPT + GROOVE                     # where the phone face starts (back of the groove)
    ya = ys + (H - SEAT) / math.tan(R(ANG))     # top of the phone face
    yb = ya + 5.0                               # 5 mm flat ridge on top
    yk = yb + H / math.tan(R(BACK))             # back foot
    prof = Polygon([(yf, 0), (yf, LIP - 1.5), (yf + 1.5, LIP), (yf + LIPT, LIP), (yf + LIPT, SEAT), (ys, SEAT),
                    (ya, H), (yb, H), (yk, 0)])
    prof = fillet(prof, 1.2)
    hollow = prof.buffer(-T, join_style=2).intersection(box(-200, BASE, 200, 300))
    shape = prof.difference(hollow)
    def yzw(poly, w): return mv(rot(Manifold.extrude(_cs(poly), w), 90, 0, 90), -w / 2, 0, 0)
    foot = box(-200, -1, 200, 0.6)
    def inset(d): return shape.buffer(-d, join_style=2).union(shape.intersection(foot))
    solid = U([yzw(shape, W - 1.2), yzw(inset(0.3), W - 0.6), yzw(inset(0.6), W)])
    # cable: notch through the lip and groove floor down to the bed, then a channel under the base out of the back
    CW = 13.0
    cable = U([cube(CW, ys - yf + 2, LIP + 2, 0, (yf + ys) / 2, -0.5), cube(CW, yk - ys + 4, 5.0, 0, (ys + yk) / 2 + 1, -0.5)])
    # logo underneath (about 10 mm wide), mirrored so it reads from below; right of the channel
    lx, ly = 20.0, (ys + yk) / 2
    mark = ext(affinity.scale(logo(lx, ly, 0.75), -1, 1, origin=(lx, ly)), 0.6, -0.01)
    # fine flutes up the back leg (range rule: ribbed faces on large plain surfaces)
    a = math.degrees(math.atan((yk - yb) / H)); z0 = 8.0; L = (H - 14.0) / math.cos(R(a))
    yz0 = yk - z0 * (yk - yb) / H
    flutes = U([mv(rot(U([cyl(1.1, L, 0, seg=24), cyl(1.1, 2.6, L - 0.01, r2=0.05, seg=24)]), a, 0, 0), x, yz0, z0) for x in np.arange(-W / 2 + 6.0, W / 2 - 5.9, 4.0)])
    stand = solid - cable - mark - flutes
    top = cube(W + 4, 400, 100, 0, 0, H - CAP)
    body_, cap = stand - top, stand ^ top
    p.part("stand", body_, BLACK, infill=0.15)
    p.part("ridge", cap, RED, infill=0.15, on="stand")
    # prop phone 75 x 160 x 9 leaning on the face
    ph = mv(rot(body(rrect(75, 160, 9), 9.0, c=1.5, steps=3, bottom=True), 90, 0, 0), 0, 0, 80)
    ph = mv(rot(ph, -(90 - ANG), 0, 0), 0, ys - 0.3, SEAT + 0.2)
    built = [(body_, BLACK), (cap, RED)]
    built_ivory = [(body_, IVORY), (cap, RED)]
    p.scene("lean", built); p.scene("lean_phone", built + [(ph, PROP)])
    p.scene("lean_back", built); p.scene("lean_ivory", built_ivory + [(ph, PROP)]); p.scene("lean_ivory_back", built_ivory)
    p.scene("bp_D16", built); p.scene("bpo_D16", built)
    g = grams(body_, 0.15) + grams(cap, 0.15)
    p.note = (f"D16 Lean. {W:g} x {yk - yf:.0f} x {H:g} mm, A-frame hollow profile, prints upright, no supports. "
              f"Face at {ANG:g} degrees, {GROOVE:g} mm groove (phones up to about 11 mm with case), {LIP:g} mm lip. "
              f"Fluted back leg. Black or ivory body (customer picks), red top {CAP:g} mm by one colour change. Cable notch {CW:g} mm and channel under the base. Logo 10 mm debossed underneath. "
              f"Estimate {g:.0f} g, {hours(g, colours=2):.1f} h.")
    return p, g

if __name__ == "__main__":
    p, g = build_lean()
    rep = p.export()
    print(json.dumps(rep, indent=1)); print("est hours", round(hours(g, colours=2), 2))
