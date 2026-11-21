"""No Skips: the classic range, rebuilt from scratch on the same CAD base as build.py.
C1/C2 Studio minis and tray, C5 Gain, A3 Rail, A4 45s, B1 Stack, B2 Lift, B5 Run 50,
D1 Horn, D2 Tape Case, D4 Sleeve, D5 Hold.

Every part is exported in print orientation. Scenes show the assembled product.
Run: python3 build2.py            (all)
     python3 build2.py C5 A3      (some)
Options (environment): NS_SET=07 tray number for C1, NS_RAIL="Front Row", NS_TAPE="Side A", NS_ACT="Your Act"
"""
import math, json, sys, os
from shapely.geometry import LineString
from ns import *
from ns import _cs

RAISE = 0.6
R = math.radians
P = {}
SET_NO = os.environ.get("NS_SET", "01")
RAIL_TXT = os.environ.get("NS_RAIL", "Front Row")
TAPE_TXT = os.environ.get("NS_TAPE", "Side A")
ACT_TXT = os.environ.get("NS_ACT", "Your Act")
W50 = [0.16,0.27,0.96,0.97,0.98,0.96,0.97,0.96,0.35,0.28,0.36,0.42,0.87,1.0,1.0,1.0,0.95,0.98,0.99,0.99,0.78,0.52,0.42,0.41,0.4,0.41,0.42,0.43,0.43,0.45,0.44,0.12,0.26,0.99,0.97,0.98,0.93,0.94,0.97,0.98,0.95,0.87,0.99,0.94,0.98,0.98,0.99,0.98,1.0,0.73]

def place(items, rx=0, ry=0, rz=0, x=0, y=0, z=0):
    return [(mv(rot(m, rx, ry, rz), x, y, z), c) for m, c in items]
def seg(x0, y0, x1, y1, w):
    return LineString([(x0, y0), (x1, y1)]).buffer(w / 2, quad_segs=8)
def radial(r0, r1, ang, w):
    a = R(ang)
    return seg(r0 * math.cos(a), r0 * math.sin(a), r1 * math.cos(a), r1 * math.sin(a), w)
def ring(r_out, r_in, cx=0.0, cy=0.0, seg_=SEG):
    return circle(r_out, cx, cy, seg_).difference(circle(r_in, cx, cy, seg_))
def number(s, size=4.0, cx=0.0, cy=0.0):      # rev B (21 Nov 2026): 4 mm minimum, was 2.4 to 3.0
    TEXT_LOG.append((s, size))
    """Number debossed 0.4 mm into the underside, mirrored so it reads from below."""
    return ext(affinity.scale(text(s, size, cx, cy), -1, 1, origin=(cx, cy)), 0.6, -0.01)
def holes_ring(n, r, rr, z0, h):
    return U([cyl(rr, h, z0, r * math.cos(2 * math.pi * i / n), r * math.sin(2 * math.pi * i / n), seg=24) for i in range(n)])
def logo(cx, cy, s=1.0):
    """No Skips mark: two chevrons running into a bar."""
    ch = lambda x: Polygon([(x, 0), (x + 4 * s, 4 * s), (x + 4 * s, 4 * s + 0.01), (x, 8 * s), (x + 2.2 * s, 8 * s), (x + 6.2 * s, 4 * s), (x + 2.2 * s, 0)])
    g = unary_union([ch(0), ch(4.6 * s), box(11.6 * s, 0, 13.6 * s, 8 * s)])
    return affinity.translate(g, cx - 6.8 * s, cy - 4 * s)

# ================================================================== C1 / C2 Studio minis
def mini_turntable():
    blk = body(rrect(58, 46, 3), 8.0, c=0.6, bottom=True)
    plat = ext(circle(18, -7, 0), 1.2, 8.0)
    for r in (16.0, 13.5, 11.0):
        plat = plat - ext(ring(r + 0.25, r - 0.25, -7, 0), 0.5, 8.7)
    blk = U([blk, plat]) - number("01/06")
    red = U([ext(circle(6, -7, 0).difference(circle(0.8, -7, 0)), RAISE, 9.2),
             ext(unary_union([circle(3.2, 19, 13), seg(19, 13, 13, -8, 2.2), rrect(4, 3, 0.8, 12.4, -9.4)]), 1.0, 8.0),
             ext(rrect(6, 4, 1, 21, -15), 1.0, 8.0)])
    return [(blk, BLACK), (red, RED)]
def mini_synth():
    blk = body(rrect(62, 30, 3), 8.0, c=0.6, bottom=True)
    whites = [rrect(3.6, 15, 0.6, -26 + i * 4, -5.5) for i in range(14)]
    blacks = unary_union([rrect(2.4, 8, 0.5, -24 + i * 4, -2.0) for i in (0, 1, 3, 4, 5, 7, 8, 10, 11, 12)])
    ivory = ext(unary_union(whites).difference(blacks.buffer(0.3)), 1.0, 8.0)
    ivory = U([ivory, ext(rrect(11, 4.4, 1, 21, 8.5), RAISE, 8.0)])
    blk = U([blk, ext(blacks, 2.0, 8.0), *[cyl(1.8, 2.0, 8.0, -26 + i * 5, 8.5, seg=32) for i in range(5)]]) - number("02/06")
    return [(blk, BLACK), (ivory, IVORY)]
def mini_drums():
    blk = body(rrect(50, 50, 3), 9.0, c=0.6, bottom=True)
    blk = U([blk, *[cyl(1.8, 1.8, 9.0, x, 19, seg=32) for x in (-17, -11, -5)]]) - number("03/06")
    pads = unary_union([rrect(8.4, 8.4, 1.2, -15 + i * 10, -19 + j * 10) for i in range(4) for j in range(4)])
    red = ext(pads.union(rrect(13, 4, 1, 13, 19)), 1.2, 9.0)
    return [(blk, BLACK), (red, RED)]
def mini_mixer():
    blk = body(rrect(46, 56, 3), 9.0, c=0.6, bottom=True)
    xs = (-15, -5, 5, 15)
    blk = U([blk, *[cyl(1.6, 2.0, 9.0, x, y, seg=32) for x in xs for y in (21, 13)]])
    blk = blk - ext(unary_union([rrect(1.4, 28, 0.6, x, -9) for x in xs]), 1.0, 8.01) - number("04/06")
    caps = unary_union([rrect(5.2, 3.2, 0.8, x, y) for x, y in zip(xs, (-3, -14, -8, -18))])
    return [(blk, BLACK), (ext(caps, 1.6, 9.0), IVORY)]
def mini_mic():
    base = body(circle(15), 4.0, c=0.6, bottom=True) - number("05/06")
    post = cyl(2.4, 30, 3.9, seg=48)
    prof = [(0, 28.9), (2.4, 28.9), (6.5, 33.0)] + [(6.5 * math.cos(a), 47.0 + 6.5 * math.sin(a)) for a in np.linspace(0, math.pi / 2, 16)]   # rev B: 45 degree neck, no supports
    head = revolve(prof, 64)
    band = cyl(6.85, 2.5, 38.0, seg=64)
    blk = U([base, post, head]) - band
    red = U([band, ext(ring(13, 10.8), RAISE, 4.0)])
    return [(blk, BLACK), (red, RED)]
def headphone_band():
    """Profile in the plane of the band. Printed lying flat, 10 mm thick."""
    arch = ring(23, 19.6, 0, 14).intersection(box(-30, 14, 30, 40))
    cups = unary_union([rrect(8, 18, 2.2, s * 21.3, 7) for s in (-1, 1)])
    legs = unary_union([box(s * 19.6, 12, s * 23, 16) if s > 0 else box(-23, 12, -19.6, 16) for s in (-1, 1)])
    prof = unary_union([arch, cups, legs])
    pads = unary_union([box(s * 25.31, 3, s * 24.1, 13) if s > 0 else box(-25.31, 3, -24.1, 13) for s in (-1, 1)])
    ivory = ext(pads, 6.0, 2.0)
    blk = ext(prof, 10.0) - ext(pads.buffer(0.01), 6.0, 2.0)
    return blk, ivory
def mini_headphones():
    base = body(rrect(50, 20, 3), 5.0, c=0.6, bottom=True)
    base = base - U([cube(8.2, 10.2, 3.6, s * 21.3, 0, 1.41) for s in (-1, 1)]) - number("06/06")
    blk, ivory = headphone_band()
    return [(base, BLACK)], [(blk, BLACK), (ivory, IVORY)]
def stood_band(items):
    # band lies flat in print (profile in xy, 10 thick in z): stand it up, cups into the pockets
    return [(mv(rot(m, 90, 0, 0), 0, 5, 1.5), c) for m, c in items]

STUDIO_POS = {"01": (-53, -14), "03": (6, -14), "04": (59, -14), "05": (-60, 38), "06": (-2, 38), "02": (52, 38)}
def build_studio():
    minis = {"01": mini_turntable(), "02": mini_synth(), "03": mini_drums(), "04": mini_mixer(), "05": mini_mic()}
    hp_base, hp_band = mini_headphones()
    names = {"01": "turntable", "02": "synth", "03": "drum_machine", "04": "mixer", "05": "mic", "06": "headphones"}
    foot = {"01": rrect(58.6, 46.6, 3.3), "02": rrect(62.6, 30.6, 3.3), "03": rrect(50.6, 50.6, 3.3), "04": rrect(46.6, 56.6, 3.3),
            "05": circle(15.3), "06": rrect(50.6, 20.6, 3.3)}
    tray_out = rrect(196, 124, 6)
    tray = body(tray_out, 4.0, c=0.6, bottom=True)
    tray = tray - U([ext(affinity.translate(foot[k], *STUDIO_POS[k]), 1.1, 2.99) for k in foot])
    lip = unary_union([fit_text("Vol. 01 The Studio", 4.2, 80, -88, -53, "l"), fit_text(f"{SET_NO}/50", 4.2, 30, 88, -53, "r"),
                       pill(0, -45.5, 176, 1.4)])
    tray_red = ext(lip, RAISE, 4.0)
    for k in ("01", "02", "03", "04", "05", "06"):
        p = Product(f"C2_{k}", f"studio_mini_{names[k]}", f"Studio Mini {k}")
        if k == "06":
            p.part("base", hp_base[0][0], BLACK); p.part("band", hp_band[0][0], BLACK, infill=0.3); p.part("ear_pads", hp_band[1][0], IVORY, infill=1.0)
            p.scene(f"mini_{k}", hp_base + stood_band(hp_band))
        else:
            for i, (m, c) in enumerate(minis[k]):
                p.part("body" if i == 0 else "accents", m, c, infill=0.2 if i == 0 else 1.0)
            p.scene(f"mini_{k}", minis[k])
        extra = {"05": " Change to red at the band and at the base ring.", "06": " The band prints lying flat; its cups press into the two pockets of the base."}.get(k, "")
        p.note = f"Studio Mini {k}/06 ({names[k].replace('_', ' ')}). " + ("Prints upright, base down" if k == "05" else "Print flat") + ", number debossed underneath." + extra
        P[p.id] = p
    p = Product("C1", "studio_tray", "Vol. 01 tray")
    p.part("tray", tray, BLACK); p.part("tray_lettering", tray_red, RED, infill=1.0)
    scene = [(tray, BLACK), (tray_red, RED)]
    for k, (x, y) in STUDIO_POS.items():
        its = (hp_base + stood_band(hp_band)) if k == "06" else minis[k]
        scene += place(its, x=x, y=y, z=3.0)
    p.scene("studio_set", scene); p.scene("bp_C1", scene); p.scene("bpo_C1", scene)
    each = {k: ((hp_base + stood_band(hp_band)) if k == "06" else minis[k]) for k in STUDIO_POS}
    row = lambda ks, dx: [it for i, k in enumerate(ks) for it in place(each[k], rz=[-8, 4, 10][i], x=(i - 1) * dx)]
    p.scene("studio_mini", row(["01", "05", "02"], 70)); p.scene("studio_mini2", row(["03", "06", "04"], 64))
    p.scene("bp_C2", [it for i, k in enumerate(["01", "05", "02", "03", "06", "04"]) for it in place(each[k], x=(i % 3 - 1) * 72, y=(1 - i // 3) * 68)])
    p.scene("bpo_C2", each["01"])
    p.note = f"Tray 196 x 124 x 4 with 1 mm locating pockets for the six minis. Set number on the lip: {SET_NO}/50 (regenerate with NS_SET=07 python3 build2.py C1). The minis are the C2_* folders."
    P["C1"] = p

# ================================================================== C5 Gain
def build_gain():
    p = Product("C5", "gain", "Gain")
    base = body(circle(22), 4.0, c=0.6, bottom=True)
    marks = unary_union([radial(15.6, 19.4, a, 1.6) for a in np.linspace(-135, 135, 11) + 90])
    post = U([cyl(4.0, 10.2, 3.9, seg=48), cyl(4.8, 2.0, 14.0, seg=48), cyl(4.8, 0.6, 16.0, r2=4.0, seg=48)])
    post = post - cube(1.4, 12, 10.5, 0, 0, 7.0)
    base = U([base, post])
    # cap, local z from its own underside
    a = np.linspace(0, 2 * math.pi, 24, endpoint=False)
    flutes = unary_union([circle(1.0, 13.5 * math.cos(t), 13.5 * math.sin(t), 24) for t in a])
    cap = U([ext(circle(13.5).difference(flutes), 12.0), body(circle(13.2), 4.2, 12.0, c=0.8, steps=4)])
    cap = cap - cyl(4.3, 9.03, -0.01, seg=48) - cyl(5.2, 4.2, 9.0, seg=48)   # bore runs 0.02 into the head pocket: at 9.0 a 0.01 mm skin sealed the pocket off - cyl(5.2, 0.4, -0.01, r2=4.3, seg=48)
    ptr = ext(seg(0, 4.5, 0, 10.5, 1.8), RAISE, 16.2)
    p.part("base", base, BLACK, infill=0.4); p.part("level_marks", ext(marks, RAISE, 4.0), RED, infill=1.0)
    p.part("knob", cap, BLACK, infill=0.3); p.part("pointer", ptr, RED, infill=1.0)
    one = lambda acc, z=4.6: [(base, BLACK), (ext(marks, RAISE, 4.0), acc), (mv(cap, 0, 0, z), BLACK), (mv(ptr, 0, 0, z), acc)]
    p.scene("knob", place(one(RED), rz=-10, x=-27, y=-10) + place(one(IVORY), rz=30, x=27, y=18))
    p.scene("knob_build", one(RED, 30)); p.scene("bp_C5", one(RED, 30)); p.scene("bpo_C5", one(RED))
    p.note = "Base 44 mm, knob 27 mm, 20.8 mm tall. The split post snaps into the knob (head 9.6 mm through a 8.6 mm bore). Print both upright. Test the snap on the first print; if it is too tight, scale the post XY to 98%."
    P["C5"] = p

# ================================================================== A3 Rail
def build_rail():
    p = Product("A3", "rail", "Rail")
    xs = (-80, -40, 0, 40, 80)
    rail = body(rrect(200, 36, 4), 8.0, c=0.6)
    rail = rail - U([cyl(3.15, 8.2, -0.1, x, -7, seg=40) for x in xs])
    rail = rail - U([cyl(2.2, 8.2, -0.1, x, -7, seg=32) + cyl(2.2, 2.41, 5.6, x, -7, r2=4.6, seg=32) for x in (-60, 60)])
    art = unary_union([fit_text(RAIL_TXT, 6.0, 110, -90, 8.5, "l"), wave(W20, 33, 8.5, 2.85, 1.6, 12, 3)])
    red = ext(art, RAISE, 8.0)
    shaft = cyl(3.0, 7.5, 14.7, seg=40)
    ribs = U([mv(rot(cube(0.7, 0.7, 6.5, 0, 0, 0), 0, 0, k * 120), 3.0 * math.cos(R(k * 120)), 3.0 * math.sin(R(k * 120)), 14.7) for k in range(3)])
    peg = U([body(circle(6.5), 2.5, c=0.5, steps=2, bottom=True, top=False), cyl(3.5, 12.3, 2.45, seg=40), shaft, ribs])
    peg = peg - (cyl(4, 0.8, 21.4, seg=40) - cyl(3.0, 0.8, 21.4, r2=2.4, seg=40))
    p.part("rail", rail, BLACK, infill=0.3); p.part("name_and_wave", red, RED, infill=1.0); p.part("peg", peg, RED, qty=5, infill=1.0)
    pegs_on = [(mv(rot(peg, 180, 0, 0), x, -7, 22.7), RED) for x in xs]
    wall = [(mv(rot(m, 90, 0, 0), 0, 0, 60), c) for m, c in [(rail, BLACK), (red, RED)] + pegs_on]
    p.scene("rail", wall); p.scene("bpo_A3", wall)
    loose = [(mv(rot(peg, 180, 0, 0), x, -7, 22.7 + (0 if x < 0 else 28)), RED) for x in xs]
    p.scene("rail_build", [(mv(rot(m, 90, 0, 0), 0, 0, 60), c) for m, c in [(rail, BLACK), (red, RED)] + loose])
    p.scene("bp_A3", p.scenes["rail_build"])
    p.note = f"Rail 200 x 36 x 8 printed face up, name '{RAIL_TXT}' (NS_RAIL to change). Pegs print cap down; three crush ribs make them press-fit into the 6.3 mm sockets. Screw holes countersunk for 4 mm screws, 120 mm apart."
    P["A3"] = p

# ================================================================== A4 45s
def build_45s():
    p = Product("A4", "45s", "45s")
    disc = body(circle(45, seg=180), 4.6, c=0.6, bottom=True)
    grooves = unary_union([ring(r + 0.3, r - 0.3, seg_=180) for r in np.arange(16.0, 43.6, 1.4)])
    disc = disc - ext(grooves, 0.5, 4.11) - ext(circle(13, seg=96), 0.6, 4.01)
    disc = disc - ext(unary_union([ring(r + 0.6, r - 0.6, seg_=180) for r in (12, 20, 28, 36)]), 0.6, -0.01)
    label = ext(circle(13, seg=96).difference(circle(1.2)), 0.6, 4.0)
    p.part("coaster", disc, BLACK, qty=4, infill=0.3); p.part("label", label, RED, qty=4, infill=1.0)
    stack = [(mv(m, 0, 0, 4.6 * i), c) for i in range(3) for m, c in [(disc, BLACK), (label, RED if i % 2 == 0 else IVORY)]]
    p.scene("coasters", place(stack, x=-48) + place([(disc, BLACK), (label, IVORY)], x=50, y=10))
    p.scene("bp_A4", p.scenes["coasters"]); p.scene("bpo_A4", [(disc, BLACK), (label, RED)])
    p.note = "Coming soon. 90 mm, 4.6 mm thick, flush label inlay, ribbed underside. Print 2 labels red and 2 ivory per set. Release only after a PETG print and a hot-cup test."
    P["A4"] = p

# ================================================================== B1 Stack
def build_stack():
    p = Product("B1", "stack", "Stack")
    SX, SY = 27.0, 10.5
    sockets = [(sx * SX, sy * SY) for sx in (-1, 1) for sy in (-1, 1)]
    base = body(rrect(70, 35, 4), 34.0, c=0.6, bottom=True, top=False)
    base = base - cube(62, 33.1, 28, 0, -1.05, 3.0) - U([cyl(2.05, 3.2, 30.9, x, y, seg=32) for x, y in sockets])
    prof = unary_union([box(-35, 0, 35, 20), rrect(70, 40, 8, 0, 20)])
    head = mv(rot(Manifold.extrude(_cs(prof), 35), 90, 0, 0), 0, 17.5, 0)
    head = head - cube(52, 3.4, 26.2, 0, 2.0, 14.0)
    head = head - U([mv(rot(cyl(2.6, 6.2, 0, seg=32), 90, 0, 0), x, -11.4, 31) for x in (-16, 0, 16)])
    dots = [mv(rot(cyl(0.9, 1.4, 0, seg=12), 90, 0, 0), -24 + i * 3, -16.2, 6 + j * 3) for i in range(17) for j in range(7)]
    head = head - U(dots)
    head = U([head, *[cyl(1.95, 3.4, -3.4, x, y, seg=32) - cyl(2.2, 0.5, -3.41, x, y, r2=1.5, seg=32) for x, y in sockets]])
    # drawer: panel in front of the base, box behind it
    panel = mv(rot(body(rrect(66, 31, 2.5), 2.4, c=0.5, steps=2), 90, 0, 0), 0, -17.5, 17.0)
    panel = panel - U([mv(rot(cyl(1.55, 2.6, 0, seg=24), 90, 0, 0), x, -17.4, 17.0) for x in (-8, 8)])
    box_ = cube(61.2, 32.4, 27.4, 0, -1.3, 3.2) - cube(58.0, 29.2, 26.0, 0, -1.3, 4.8)
    drawer = U([panel, box_])
    handle = U([body(pill(0, 0, 26, 7), 4.0, c=0.5, steps=2), cyl(1.55, 3.0, -2.9, -8, 0, seg=24), cyl(1.55, 3.0, -2.9, 8, 0, seg=24)])
    knob = U([body(circle(5.2), 5.0, c=0.6, steps=2), cyl(2.6, 5.5, -5.4, seg=32)]) - ext(seg(0, 1.2, 0, 4.4, 0.8), 0.6, 4.41)
    picks = [(mv(rot(ext(Polygon([(-7, 6), (7, 6), (0, -10)]).buffer(2.5), 0.8), 90, 0, 0), x, 2.4, 61.5), RED) for x in (-14, 12)]
    # print orientations
    p.part("base", rot(base, -90, 0, 0), BLACK, infill=0.15)
    p.part("head", rot(head, 180, 0, 0), BLACK, infill=0.15)
    p.part("drawer", rot(drawer, -90, 0, 0), BLACK, infill=0.2)
    # knobs and handle print face down, pins up: stem-down left the cap and the bar hanging in the air
    p.part("knob", rot(knob, 180, 0, 0), IVORY, qty=3, infill=1.0)
    p.part("handle", rot(handle, 180, 0, 0), IVORY, infill=1.0)
    knobs_on = [(mv(rot(knob, 90, 0, 0), x, -17.5, 34 + 31), IVORY) for x in (-16, 0, 16)]
    handle_on = [(mv(rot(handle, 90, 0, 0), 0, -19.9, 17.0), IVORY)]
    built = [(base, BLACK), (mv(head, 0, 0, 34), BLACK), (drawer, BLACK)] + knobs_on + handle_on + picks
    p.scene("amp", built)
    p.scene("amp_open", [(base, BLACK), (mv(head, 0, 0, 34), BLACK), (mv(drawer, 0, -20, 0), BLACK)] + knobs_on + [(mv(m, 0, -20, 0), c) for m, c in handle_on] + picks)
    p.scene("bpo_B1", built[:-2])
    ex = [(base, BLACK), (mv(head, 0, 0, 34 + 30), BLACK), (mv(drawer, 0, -60, 0), BLACK)] + [(mv(m, 0, -25, 30), c) for m, c in knobs_on] + [(mv(m, 0, -82, 0), c) for m, c in handle_on]
    p.scene("amp_build", ex); p.scene("bp_B1", ex)
    p.note = "70 x 35 x 74. Base prints on its back, head upside down, drawer on its front panel, knobs and handle face down with their pins up. Pins 3.9 mm into 4.1 mm sockets; knob stems and handle pins press into nominal holes."
    P["B1"] = p

# ================================================================== B2 Lift
def build_lift():
    p = Product("B2", "lift", "Lift")
    t = math.tan(R(14))
    zf = 44.2 - 139 * t
    prof = fillet(Polygon([(-75, 0), (75, 0), (75, 18), (66, 18), (64, zf), (-75, 44.2)]), 1.2)
    wv = wave(W20, -58, 14, 3.0, 1.8, 18, 5)
    wedge = ext(prof, 41.0) - ext(wv, RAISE, -0.01)
    inlay = ext(wv, RAISE, 0.0)
    p.part("wedge", wedge, BLACK, qty=2, infill=0.12); p.part("wave_inlay", inlay, IVORY, qty=2, infill=1.0)
    up = [(rot(m, 90, 0, 0), c) for m, c in [(wedge, BLACK), (inlay, IVORY)]]          # spans y 0..-41, inlay on y = 0
    pair = [(mv(m, 0, 90, 0), c) for m, c in up] + [(mv(m.mirror((0, 1, 0)), 0, -90, 0), c) for m, c in up]
    ctrl = mv(rot(body(rrect(200, 186, 10), 22, c=2, steps=3, bottom=True), 0, 14, 0), -6, 0, 27.5)
    p.scene("riser", pair + [(ctrl, PROP)]); p.scene("riser_bare", pair); p.scene("bp_B2", pair); p.scene("bpo_B2", [(rot(m, 90, 0, 0), c) for m, c in [(wedge, BLACK), (inlay, IVORY)]])
    p.note = "Two identical wedges, 150 x 41 x 44.2, 14 degree slope, 18 mm front lip. Print lying on a side: the waveform is a flush inlay in the first layers, so it shows on the outer face of each wedge."
    P["B2"] = p

# ================================================================== B5 Run 50
def build_run50():
    import build as V2
    p = Product("B5", "run_50", "Run 50")
    front = unary_union([fit_text(ACT_TXT, 6.0, 44, 6, 3.6), wave(W20, -13.6, -9.2, 2.06, 1.3, 5.2, 1.3)])
    blk, art, _ = V2.tag(70, front, Polygon(), RED, None)
    p.part("tag_body", blk, BLACK, qty=50, infill=1.0); p.part("front_name", art, RED, qty=50, infill=1.0)
    p.part("loop_strap", V2.strap(), BLACK, qty=50, infill=1.0)
    p.scene("run", [(m, c) for i in range(3) for j in range(4) for m, c in place([(blk, BLACK), (art, RED if (i + j) % 2 == 0 else IVORY)], x=(j - 1.5) * 76, y=(i - 1) * 36)])
    p.scene("bp_B5", p.scenes["run"]); p.scene("bpo_B5", [(blk, BLACK), (art, RED)])
    p.note = f"Fifty Alias tags with one line '{ACT_TXT}' (NS_ACT to change, or use the order kit: alias --name). Same body as B3. Fill the A1 plate: 12 tags per plate."
    P["B5"] = p

# ================================================================== D1 Horn
def build_horn():
    p = Product("D1", "horn", "Horn")
    W = 70.0
    k = 1 / math.tan(R(71))
    yt = -9 + (108 - 29) * k
    prof = Polygon([(-25, 0), (25, 0), (25, 100), (yt + 1.0, 108), (yt, 108), (-9, 29), (-21, 29), (-21, 70), (-25, 70)])
    prof = fillet(prof, 0.8)
    yz = lambda poly: mv(rot(Manifold.extrude(_cs(poly), W), 90, 0, 90), -W / 2, 0, 0)    # (y,z) profile, extruded along x
    stand = yz(prof)
    # horn chamber with a walled cable shaft through it
    chamber = cube(60, 17, 22, 0, -12.5, 4) - cube(14.2, 17.2, 22.2, 0, -12.5, 3.9)
    slits = U([cube(19.5, 5.5, 3.4, s * 16.85, -15, 25.8) for s in (-1, 1)])
    shaft = cube(11, 11, 21.0, 0, -15, 9.0) + cube(11, 46.0, 11, 0, 2.5 + 0.5, 9.0)
    tear = unary_union([circle(10, 0, 0, 96), Polygon([(-7.071, 7.071), (7.071, 7.071), (3.34, 10.8), (-3.34, 10.8)])])   # flat-top teardrop: prints upright without supports
    throat = mv(rot(ext(tear, 4.2), 90, 0, 0), 0, -20.9, 16)
    mouth = mv(rot(cyl(14.5, 2.0, 0, seg=96), 90, 0, 0), 0, -23.0, 16)
    tweet = mv(rot(cyl(4.4, 1.6, 0, seg=48), 90, 0, 0), 0, -23.4, 39)
    bores = U([mv(rot(cyl(16.55, 0.9, 0, seg=128), 90, 0, 0), 0, -24.2, 16), mv(rot(cyl(5.95, 0.9, 0, seg=64), 90, 0, 0), 0, -24.2, 39)])   # seats for the red rings
    sock = yz(Polygon([(-25.1, -0.1), (25.1, -0.1), (25.1, 0), (-25.1, 0)])) # placeholder for orientation check
    dove = mv(rot(Manifold.extrude(_cs(Polygon([(-10.25, -0.01), (10.25, -0.01), (12.40, 5.6), (-12.40, 5.6)])), 50.4), 90, 0, 0), 0, 25.2, 0)   # 0.4 mm extra so a sagging bridge cannot rub the rail
    stand = stand - chamber - slits - shaft - throat - mouth - tweet - dove - bores
    # red rings press into 0.8 mm seats (0.1 mm tight on the outside) and stand 0.6 proud, so the stand prints black only, upright, with no supports
    ring_big = ext(ring(16.6, 14.5), 1.4); ring_small = ext(ring(6.0, 4.4), 1.4)
    red = U([mv(rot(ring_big, 90, 0, 0), 0, -24.2, 16), mv(rot(ring_small, 90, 0, 0), 0, -24.2, 39)])
    # plate: stand footprint at the front, tail behind
    plate = mv(body(rrect(70, 133, 5), 4.0, c=0.6, bottom=True), 0, 41.5, 0)
    rail = mv(rot(Manifold.extrude(_cs(Polygon([(-10, 0), (10, 0), (12, 5), (-12, 5)])), 49.0), 90, 0, 0), 0, 24.5, 4.0)
    rail = rail - mv(rot(Manifold.extrude(_cs(Polygon([(-12.5, 4.4), (12.5, 4.4), (12.5, 5.1), (-12.5, 5.1)])), 2), 90, 0, 0), 0, -23.5, 4.0)  # lead-in
    plate = U([plate, rail])
    mark = ext(affinity.rotate(logo(0, 0, 1.6), 90, origin=(0, 0)), RAISE, 4.0)
    mark = mv(mark, 0, 82, 0)
    p.part("stand", stand, BLACK, infill=0.15)                       # rev D: prints upright as it stands, no supports
    p.part("speaker_ring", ring_big, RED, infill=1.0); p.part("tweeter_ring", ring_small, RED, infill=1.0)
    p.part("plate", plate, BLACK, infill=0.4); p.part("plate_mark", mark, RED, infill=1.0)
    # phone: 9 mm thick, back face on the 71 degree ramp, bottom-back edge in the corner of the seat
    ph = mv(rot(body(rrect(75, 160, 9), 9.0, c=1.5, steps=3, bottom=True), 90, 0, 0), 0, 0, 80)     # thickness along -y, back face y = 0
    ph = mv(rot(ph, -(90 - 71), 0, 0), 0, -9.0 - 0.3, 29.0 + 4.0 + 0.3)
    built = [(mv(stand, 0, 0, 4.0), BLACK), (mv(red, 0, 0, 4.0), RED), (plate, BLACK), (mark, RED)]
    p.scene("phonestand", built + [(ph, PROP)])
    p.scene("bp_D1", built); p.scene("bpo_D1", built); p.scene("phonestand_horn_seat", built)
    p.scene("phonestand_horn_exploded", [(mv(stand, 0, -60, 30), BLACK), (mv(red, 0, -60, 30), RED), (plate, BLACK), (mark, RED)])
    # build picture: stand sits on the plate's tail, groove over the end of the rail, then slides forward onto the plate's front
    # build picture: the two red rings press into their seats on the front (stand shown upright, rings pulled 30 mm forward)
    p.scene("horn_rings", [(mv(stand, 0, 0, 4.0), BLACK), (mv(red, 0, -30, 4.0), RED), (plate, BLACK), (mark, RED)])
    p.scene("horn_slide", [(mv(stand, 0, 62, 4.0), BLACK), (mv(red, 0, 62, 4.0), RED), (plate, BLACK), (mark, RED)])
    p.note = "Rev D (21 Nov 2026): stand prints upright with no supports, red speaker and tweeter rings press into seats. Rev C rebuilt. Stand 70 x 50 x 108, plate 70 x 133 x 4 flat. Dovetail rail 20/24 x 5, socket 0.25 mm a side. Seat at 29 mm, ramp 71 degrees, phones 7 to 11.5 mm. Two 5.5 x 19.5 slits feed the chamber, D29 mouth. Cable shaft 11 x 11 runs down and out the back, walled off from the chamber."
    P["D1"] = p

# ================================================================== D1 Wedge (replaces the Horn, 21 Nov 2026)
def build_wedge():
    """Phone stand shaped like a stage monitor wedge. One black body that prints upright as it stands (no supports),
    a fluted back, 0.6 mm stepped side bevel, and a red lip that slides in on a dovetail (swap for ivory later).
    Phone leans back at 68 degrees, 14 mm groove takes phones up to about 13 mm thick with a case. Cable runs down a slot
    behind the lip and out of a tunnel at the back."""
    p = Product("D1", "wedge", "Wedge")
    W = 80.0; ANG = 68.0; SEAT = 14.0; TOP = 105.0
    k = 1 / math.tan(R(ANG)); y0 = -19.0; yt = y0 + (TOP - SEAT) * k
    prof = fillet(Polygon([(-42, 0), (35, 0), (35, 80), (25, TOP), (yt, TOP), (y0, SEAT), (-42, SEAT)]), 1.6)
    def yzw(poly, w): return mv(rot(Manifold.extrude(_cs(poly), w), 90, 0, 90), -w / 2, 0, 0)
    foot = box(-100, -1, 100, 0.6)
    def inset(d): return prof.buffer(-d, join_style=2).union(prof.intersection(foot))   # bottom edge stays on the bed
    body_ = U([yzw(prof, W - 1.2), yzw(inset(0.3), W - 0.6), yzw(inset(0.6), W)])
    # red lip: dovetail tenon in the base, 5 mm lip standing 10 mm above the seat
    tenon = Polygon([(-39.0, 8.5), (-32.0, 8.5), (-33.0, SEAT), (-38.0, SEAT)])
    lipp = fillet(unary_union([tenon, box(-38.0, SEAT - 0.01, -33.0, SEAT + 10.0)]), 0.6)
    lip = yzw(lipp, W - 0.6)
    slot = yzw(lipp.buffer(0.15, join_style=2).intersection(box(-100, 0, 100, SEAT + 0.01)).union(box(-38.15, SEAT - 0.02, -32.85, SEAT + 1)), W + 2)
    # cable: slot behind the lip down to the bed, tunnel out of the back (14 mm bridge)
    cable = U([cube(14, 12.6, SEAT + 1, 0, (-31.4 + y0) / 2, -0.5), cube(14, 70, 9, 0, 1.6, -0.5)])
    # fluted back, 16 half-round flutes
    flutes = U([cyl(1.4, 66, 7, x, 35, seg=24) for x in np.arange(-33, 33.1, 4.4)])
    word = ext(affinity.scale(text("NO SKIPS", 4.5, 23, 10), -1, 1, origin=(23, 10)), 0.6, -0.01)   # read from below
    stand = body_ - slot - cable - flutes - word
    p.part("stand", stand, BLACK, infill=0.12)
    p.part("lip", lip, RED, infill=1.0)
    # props: phone 75 x 160 x 9 leaning on the face
    ph = mv(rot(body(rrect(75, 160, 9), 9.0, c=1.5, steps=3, bottom=True), 90, 0, 0), 0, 0, 80)
    ph = mv(rot(ph, -(90 - ANG), 0, 0), 0, y0 - 0.3, SEAT + 0.2)
    built = [(stand, BLACK), (lip, RED)]
    p.scene("wedge", built); p.scene("wedge_back", built); p.scene("wedge_phone", built + [(ph, PROP)])
    p.scene("wedge_build", [(stand, BLACK), (mv(lip, -W - 10, 0, 0), RED)])
    p.scene("bp_D1", built); p.scene("bpo_D1", built)
    p.note = (f"Rev E Wedge (replaces the Horn). Body {W:g} x 77 x {TOP:g} mm prints upright, no supports. Phone face at {ANG:g} degrees, "
              "14 mm groove, red lip on a dovetail (0.15 mm a side) slides in from either side. Cable slot behind the lip, 14 mm tunnel out the back. "
              "Fluted back, 0.6 mm stepped side bevel, NO SKIPS 4.5 mm debossed underneath.")
    P["D1"] = p

# ================================================================== D2 Tape Case
def build_tape():
    p = Product("D2", "tape_case", "Tape Case")
    out = rrect(100, 64, 4)
    tray = body(out, 17.5, c=0.6, bottom=True, top=False)
    tray = tray - ext(rrect(96, 60, 2.4), 16.1, 1.5)
    tray = U([tray, cube(1.6, 60, 12.5, -12.2, 0, 1.5)])
    tray = tray - mv(rot(cyl(7.5, 6, 0, seg=64), 90, 0, 0), 0, -29, 17.5 + 2.5)
    # lid, modelled art-up (art face at z = 3.5, plug below)
    lid = body(out, 3.5, c=0.6) + (ext(rrect(95.5, 59.5, 2.3), 3.2, -3.19) - ext(rrect(92.3, 56.3, 1.2), 3.3, -3.3))
    label = rrect(72, 13, 2, 0, 18).difference(text(TAPE_TXT, 6.0, 0, 18))
    trap = Polygon([(-32, -11), (32, -11), (26, -26), (-26, -26)])
    lines = unary_union([trap.difference(trap.buffer(-1.2, join_style=2)), pill(0, -7.5, 88, 1.0)])
    red_art = unary_union([label, lines])
    hubs = unary_union([ring(6.4, 5.0, s * 20, 2) for s in (-1, 1)] + [radial(0, 4.6, a, 1.2) for a in range(0, 360, 60)]
                       + [affinity.translate(radial(0, 4.6, a, 1.2), -20, 2) for a in range(0, 360, 60)])
    hubs = unary_union([affinity.translate(unary_union([ring(6.4, 5.0)] + [radial(1.5, 4.6, a, 1.2) for a in range(0, 360, 60)]), s * 20, 2) for s in (-1, 1)])
    deb = unary_union([hubs, rrect(18, 7, 1.5, 0, 2).difference(rrect(16, 5, 1, 0, 2)),
                       *[circle(1.1, x, y, 24) for x, y in ((-46, 28.5), (46, 28.5), (-46, -28.5), (46, -28.5), (0, 29.5))],
                       *[circle(1.4, x, -19, 24) for x in (-8, 0, 8)], *[rrect(2.8, 2.8, 0.3, x, -19) for x in (-17, 17)]])
    lid = lid - ext(red_art, 0.62, 2.9) - ext(deb, 0.6, 2.91)
    inlay = ext(red_art, 0.6, 2.9)
    flip = lambda m: rot(m, 0, 180, 0)
    p.part("tray", tray, BLACK, infill=0.2)
    p.part("lid", flip(lid), BLACK, infill=0.3); p.part("label_inlay", flip(inlay), RED, infill=1.0)
    p.scene("cassettebox", [(tray, BLACK), (mv(lid, 0, 0, 17.5 + 0.0), BLACK), (mv(inlay, 0, 0, 17.5), RED)])
    p.scene("bp_D2", p.scenes["cassettebox"]); p.scene("bpo_D2", p.scenes["cassettebox"])
    p.scene("cassettebox_open", [(tray, BLACK), (mv(lid, 110, 0, 3.2), BLACK), (mv(inlay, 110, 0, 3.2), RED)])
    p.note = f"100 x 64 x 21 closed. Tray 17.5 tall, compartments 34 x 59 and 58 x 59, 16 deep. Lid prints art face down: the label '{TAPE_TXT}' (NS_TAPE) and lines are a 0.6 mm red inlay, hubs and screws debossed. Plug rim 0.25 mm clearance a side."
    P["D2"] = p

# ================================================================== D4 Sleeve
def build_sleeve():
    p = Product("D4", "sleeve", "Sleeve")
    T = 8.0; LEAN = math.tan(R(15))
    disc = circle(62, 18, 58, 160)
    lean = Polygon([(-12, 0), (-12 + 130 * LEAN, 130), (90, 130), (90, 0)])
    foot2d = unary_union([disc.intersection(lean).intersection(box(-60, 0, 90, 130)), box(-50, 0, 20, 14)])
    foot2d = fillet(foot2d, 1.0).difference(box(-44.2, 4, -37.8, 20))
    grooves = unary_union([ring(r + 0.6, r - 0.6, 18, 58, 160) for r in range(24, 59, 6)] + [circle(15, 18, 58).difference(circle(1.6, 18, 58))])
    grooves = grooves.intersection(foot2d.buffer(-1.6))
    foot = ext(foot2d, T) - ext(grooves, 0.62, -0.01)
    finlay = ext(grooves, 0.6, 0.0)
    # ledge, modelled face up: x along its length, y = height
    lprof = unary_union([rrect(170, 34, 4, 0, 17), box(-59.2, 0, -50.8, 4), box(50.8, 0, 59.2, 4)])
    lprof = box(-85, 0, 85, 34).intersection(rrect(170, 34, 4, 0, 17))
    ledge = body(lprof, 6.0, c=0.5, steps=2, bottom=True)
    art = unary_union([fit_text("Now Spinning", 7.0, 92, -76, 21, "l"), fit_text("33 RPM", 4.0, 30, -76, 8.5, "l"),
                       pill(-30, 13.5, 92, 1.2), wave(W20, 26, 19, 2.6, 1.4, 16, 4)])
    lart = ext(art, RAISE, 6.0)
    p.part("foot_left", foot, BLACK, infill=0.2); p.part("foot_left_inlay", finlay, RED, infill=1.0)
    p.part("foot_right", foot.mirror((1, 0, 0)), BLACK, infill=0.2); p.part("foot_right_inlay", finlay.mirror((1, 0, 0)), RED, infill=1.0)
    p.part("ledge", ledge, BLACK, infill=0.2); p.part("ledge_art", lart, RED, infill=1.0)
    stand_foot = lambda m, x, mirror: mv(rot(m.mirror((1, 0, 0)) if mirror else m, 90, 0, 90), x, 0, 0)
    # rot (90,0,90): print x -> world y, print y -> world z, print z -> world x
    L = [(stand_foot(foot, -55 - T / 2, False), BLACK), (stand_foot(finlay, -55 - T / 2, False), RED)]
    Rr = [(mv(rot(foot, 90, 0, 90).mirror((1, 0, 0)), 55 + T / 2, 0, 0), BLACK), (mv(rot(finlay, 90, 0, 90).mirror((1, 0, 0)), 55 + T / 2, 0, 0), RED)]
    led = [(mv(rot(m, 90, 0, 0), 0, -41.0 + 3.0, 4.0), c) for m, c in [(ledge, BLACK), (lart, RED)]]
    p.scene("vinylstand", L + Rr + led); p.scene("bpo_D4", L + Rr + led)
    p.scene("vinylstand_build", place(L, x=-12) + place(Rr, x=12) + [(mv(m, 0, -30, 40), c) for m, c in led]); p.scene("bp_D4", p.scenes["vinylstand_build"])
    sleeve = mv(rot(cube(315, 315, 4, 0, 0, 0), 0, 0, 0), 0, 0, 0)
    sl = mv(rot(mv(cube(315, 3.5, 315, 0, 0, 0), 0, -1.75, 0), -15, 0, 0), 0, -8.4, 14.2)
    p.scene("vinylstand_record", L + Rr + led + [(sl, PROP)])
    p.note = "Feet: two 8 mm record shapes (left and right are mirror parts, grooves inlaid on the outer face, printed face down). Ledge 170 x 34 x 6 face up. Ledge slots 6.4 mm wide, 10 deep. Sleeve rests on the 14 mm base and leans back 15 degrees."
    P["D4"] = p

# ================================================================== D5 Hold
def build_hold():
    p = Product("D5", "hold", "Hold")
    a = np.linspace(0, 2 * math.pi, 72, endpoint=False)
    knurl = circle(58, seg=240).difference(unary_union([circle(1.6, 58 * math.cos(t), 58 * math.sin(t), 20) for t in a]))
    base = body(knurl, 20.0, c=0.8, bottom=True) - cube(30.2, 10.2, 15.1, 0, 0, 5.0) - ext(ring(45, 44), 0.5, 19.51)
    ticks = unary_union([radial(47, 52.5, ang, 2.0) for ang in np.linspace(-45, 225, 12)] + [radial(20, 40, -60, 3.0)])
    bred = ext(ticks, RAISE, 20.0)
    L = 227.0
    post = body(rrect(30, L, 1.5, 0, L / 2), 10.0, c=0.5, steps=2, bottom=True) - ext(rrect(2.4, L - 50, 1.2, 0, L / 2 + 5), 1.0, 9.01)
    pticks = unary_union([rrect(4.5, 1.4, 0.5, s * 8, y) for s in (-1, 1) for y in np.arange(40, L - 25, 12)])
    fader = rrect(16, 11, 2, 0, 120)
    post = post - ext(fader.buffer(0.01), 0.01, 10.0)
    pred = U([ext(pticks.difference(fader.buffer(0.6)), RAISE, 10.0), body(fader, 3.0, 10.0, c=0.6, steps=2) - ext(box(-8, 119.4, 8, 120.6), 0.8, 12.21)])
    # saddle, profile with origin at the arc centre, extruded 34 deep, front face at z = 0
    sec = ring(56, 46, seg_=240).intersection(Polygon([(0, 0), (80, 80 * math.tan(R(15))), (80, 90), (-80, 90), (-80, 80 * math.tan(R(15)))]))
    ribs = unary_union([circle(1.5, 56 * math.cos(R(t)), 56 * math.sin(R(t)), 20) for t in np.arange(17, 164, 6)])
    sprof = unary_union([sec.difference(ribs), box(-16, 13, 16, 47)])
    stripe = ring(52, 50.5, seg_=240).intersection(Polygon([(0, 0), (80, 80 * math.tan(R(22))), (80, 90), (-80, 90), (-80, 80 * math.tan(R(22)))]))
    saddle = ext(sprof, 34.0) - cube(30.3, 22.0, 10.3, 0, 13 + 11 - 0.01, 17 - 5.15) - ext(stripe, 0.6, -0.01)
    sred = ext(stripe, 0.6, 0.0)
    p.part("base", base, BLACK, infill=0.15); p.part("dial", bred, RED, infill=1.0)
    p.part("post", post, BLACK, infill=0.3); p.part("fader_and_scale", pred, RED, infill=1.0)
    p.part("saddle", saddle, BLACK, infill=0.2); p.part("saddle_stripe", sred, RED, infill=1.0)
    post_w = lambda m: mv(rot(m, 90, 0, 0), 0, 5.0, 5.0)
    zc = 5.0 + L - 13.0 - 22.0 + 13.0 + 22.0 - 13.0 - 22.0 + 0.0
    zc = 5.0 + L - 22.0 - 13.0 + 0.3   # 0.3 mm clearance above the post top
    sad_w = lambda m: mv(rot(rot(m, 90, 0, 0), 0, 0, 180), 0, -17.0, zc)
    built = [(base, BLACK), (bred, RED), (post_w(post), BLACK), (post_w(pred), RED), (sad_w(saddle), BLACK), (sad_w(sred), RED)]
    p.scene("headphonestand_bare", built); p.scene("bpo_D5", built)
    ex = [(base, BLACK), (bred, RED), (mv(post_w(post), 0, 0, 30), BLACK), (mv(post_w(pred), 0, 0, 30), RED), (mv(sad_w(saddle), 0, 0, 60), BLACK), (mv(sad_w(sred), 0, 0, 60), RED)]
    p.scene("headphonestand_build", ex); p.scene("bp_D5", ex)
    top = zc + 56.0
    band = mv(rot(ext(ring(101, 95, seg_=200).intersection(box(-120, 0, 120, 120)), 30.0), 90, 0, 0), 0, 15, top - 95)
    cups = U([mv(rot(body(circle(38), 26, c=3, steps=3, bottom=True), 0, 90, 0), sx * 98 - (13 if sx > 0 else -13) * 0 + (0 if sx > 0 else 0), 0, top - 95 - 30) for sx in (-1, 1)])
    cupL = mv(rot(body(circle(38), 26, c=3, steps=3, bottom=True), 0, 90, 0), 92, 0, top - 125)
    cupR = mv(rot(body(circle(38), 26, c=3, steps=3, bottom=True), 0, -90, 0), -92, 0, top - 125)
    p.scene("headphonestand", built + [(band, PROP), (cupL, PROP), (cupR, PROP)])
    p.note = f"116 mm base, {round(zc + 56, 1)} mm tall, saddle 108 mm wide. Post 30 x 10 x 227 prints on its back, saddle on its front face (red stripe inlay), base upright. Slot and socket 0.1 mm clearance a side: tight press fit."
    P["D5"] = p

ALL = [build_studio, build_gain, build_rail, build_45s, build_stack, build_lift, build_run50, build_wedge, build_tape, build_sleeve, build_hold]
if __name__ == "__main__":
    only = sys.argv[1:]
    for f in ALL: f()
    rep = {}
    for k, p in P.items():
        if only and not any(k.startswith(o) for o in only): continue
        rep[k] = p.export()
        print(k, p.name, rep[k]["grams"], "g", [(x["file"], x["size"], x["grams"]) for x in rep[k]["parts"]], flush=True)
    old = {}
    try: old = json.load(open(f"{OUT}/report.json"))
    except Exception: pass
    old.update(rep); json.dump(old, open(f"{OUT}/report.json", "w"), indent=1)
