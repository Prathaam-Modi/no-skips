"""No Skips: slim everyday pieces (Eject, Standby, Rotary).
Run: python3 build3.py            (all)
     python3 build3.py D10 D12    (some)
"""
import math, json, sys, os
from ns import *
from ns import _cs
from shapely.geometry import LineString

RAISE = 0.6
R = math.radians
P = {}
W20 = [0.54, 0.98, 0.97, 0.57, 0.48, 1.0, 0.98, 0.99, 0.64, 0.4, 0.42, 0.44, 0.32, 0.91, 0.95, 0.98, 0.93, 0.97, 0.98, 0.91]

def place(items, rx=0, ry=0, rz=0, x=0, y=0, z=0):
    return [(mv(rot(m, rx, ry, rz), x, y, z), c) for m, c in items]
def yz(poly, length, x0=0.0):
    """Profile drawn in (y, z), extruded along +x from x0."""
    return mv(rot(Manifold.extrude(_cs(poly), length), 90, 0, 90), x0, 0, 0)
def xz(poly, depth, y0=0.0):
    """Profile drawn in (x, z), extruded along +y from y0."""
    return mv(rot(Manifold.extrude(_cs(poly), depth), 90, 0, 0), 0, y0 + depth, 0)
def ring(ro, ri, cx=0.0, cy=0.0, seg_=SEG):
    return circle(ro, cx, cy, seg_).difference(circle(ri, cx, cy, seg_))
def logo(cx, cy, s=1.0):
    ch = lambda x: Polygon([(x, 0), (x + 4 * s, 4 * s), (x, 8 * s), (x + 2.2 * s, 8 * s), (x + 6.2 * s, 4 * s), (x + 2.2 * s, 0)])
    g = unary_union([ch(0), ch(4.6 * s), box(11.6 * s, 0, 13.6 * s, 8 * s)])
    return affinity.translate(g, cx - 6.8 * s, cy - 4 * s)
def eject_symbol(cx, cy, w):
    tri = Polygon([(cx - w / 2, cy - w * 0.05), (cx + w / 2, cy - w * 0.05), (cx, cy + w * 0.5)])
    return unary_union([tri, box(cx - w / 2, cy - w * 0.38, cx + w / 2, cy - w * 0.2)])

# ================================================================== D10 Eject: card wallet with a thumb slider (rev B)
# Rev B: the front is ONE piece (face, walls and floor), so nothing can peel off the front. The back plate snaps in
# on four spring bars, and the same bars grip the card edges, so cards stay put in any position (hold, shake, upside down).
def build_eject():
    p = Product("D10", "eject", "Eject")
    W, H = 92.0, 66.6            # outer width (x) and height (z)
    XW = 44.2                    # cavity half width (wall inner face); cards are 85.6 wide, half 42.8
    FRONT, CAV_Y, BACK, FLOOR = 1.2, 5.0, 1.2, 1.4
    GRIP = float(os.environ.get("NS_GRIP", "0.3"))    # how far each spring pad sits inside the card edge when empty
    BT, BL, SLIT = 1.2, 15.0, 0.8                     # spring bar thickness, length, slit width
    XP = 42.8 - GRIP; XO = XP + BT                    # pad face (touches the card) and outer face of the bar
    NX = 44.7                                         # nose tip; pocket floor is 44.8
    LOWER = (19.0, 34.0, "low"); UPPER = (39.0, 54.0, "up")   # bar z range; low bar is anchored at its top, upper at its bottom
    sil = unary_union([rrect(W, H, 4.0, 0, H / 2), rrect(W, 12.0, 1.0, 0, H - 6.0)])      # round at the bottom, square at the top
    # ---- front body: face wall, side walls, floor; open at the top (cards) and at the back (plate)
    front = U([xz(sil, FRONT, -FRONT), xz(sil, CAV_Y + 0.01, -0.01)])
    front = front - cube(2 * XW, CAV_Y + 0.03, H + 2.0, 0, CAV_Y / 2, FLOOR)
    sym = eject_symbol(33.5, 9.0, 9.0)
    front = front - xz(sym, 0.62, -FRONT - 0.01)
    sym_in = xz(sym, 0.6, -FRONT)
    pockets = []
    for s in (-1, 1):
        for zc in (22.0, 51.0):
            pk = Polygon([(XW - 0.02, 0.3), (44.8, 0.3), (44.8, 2.97), (XW - 0.02, 3.25)])
            if s < 0: pk = affinity.scale(pk, -1, 1, origin=(0, 0))
            pockets.append(ext(pk, 5.0, zc - 2.5))
    front = front - U(pockets)
    # ---- back plate with four spring bars (grip + snap)
    plate = xz(sil, BACK, CAV_Y)
    plate = plate - cube(8.4, BACK + 0.2, 25.0, 0, CAV_Y + BACK / 2, 1.3)                  # slot for the slider tab, 18 mm travel
    plate = plate - mv(rot(cyl(9, 4, 0, seg=64), 90, 0, 0), 0, CAV_Y + BACK + 1, H + 3.5)  # thumb dip
    slits, blades = [], []
    for s in (-1, 1):
        for (z0, z1, kind) in (LOWER, UPPER):
            xc = s * (XP + XO) / 2
            lo, hi = (z0 - SLIT, z1) if kind == "low" else (z0, z1 + SLIT)
            slits.append(cube(SLIT, BACK + 0.04, hi - lo, s * (XP - SLIT / 2), CAV_Y + BACK / 2, lo))     # inner slit
            slits.append(cube(SLIT, BACK + 0.04, hi - lo, s * (XO + SLIT / 2), CAV_Y + BACK / 2, lo))     # outer slit
            ez = (z0 - SLIT) if kind == "low" else z1
            slits.append(cube(BT + 2 * SLIT, BACK + 0.04, SLIT, xc, CAV_Y + BACK / 2, ez))                # free-end slit
            blade = cube(BT, CAV_Y - 0.4 + 0.02, BL, xc, (0.4 + CAV_Y + 0.02) / 2, z0)
            zn = 20.0 if kind == "low" else 49.0                                                          # nose near the free end
            nose = Polygon([(XO - 0.05, 0.4), (XO, 0.4), (NX, 2.0), (NX, 2.9), (XO, 3.2), (XO - 0.05, 3.2)])
            if s < 0: nose = affinity.scale(nose, -1, 1, origin=(0, 0))
            blade = U([blade, ext(nose, 4.0, zn)])
            ch = Polygon([(XP - 0.02, z1 - 1.6), (XP + 0.9, z1 + 0.02), (XP - 0.02, z1 + 0.02)])            # lead-in at the top end, pad side
            if s < 0: ch = affinity.scale(ch, -1, 1, origin=(0, 0))
            blade = blade - xz(ch, CAV_Y - 0.2, 0.3)
            blades.append(blade)
    plate_all = U([plate - U(slits)] + blades)
    # ---- slider: ramp lifts the front card highest, so the stack fans out when pushed
    ramp = Polygon([(0.1, 0), (4.9, 0), (4.9, 2.0), (1.0, 10.6), (0.1, 10.6)])   # rev B1: 0.9 mm flat top, no knife edge
    car = yz(ramp, 83.6, -41.8)
    tab = cube(8.0, BACK + 2.2, 6.0, 0, 4.9 + (BACK + 2.2) / 2 - 0.05, 0)
    car = U([car, tab]) - U([cube(8.2, 0.5, 0.6, 0, 4.9 + BACK + 2.2 - 0.25, 1.0 + i * 1.6) for i in range(3)])
    # ---- print orientations: front face down, back plate outer face down (bars stand up), slider as it is
    p.part("front_body", mv(rot(front, 90, 0, 0), 0, 0, FRONT), BLACK, infill=1.0)
    p.part("eject_inlay", mv(rot(sym_in, 90, 0, 0), 0, 0, FRONT), IVORY, infill=1.0)
    p.part("back_plate", mv(rot(plate_all, -90, 0, 0), 0, 0, CAV_Y + BACK), BLACK, infill=1.0)
    p.part("slider", car, RED, infill=1.0)
    car_w = mv(car, 0, 0, FLOOR)
    cards = []
    for i in range(6):
        y0 = i * 0.78 + 0.02
        h = 2.0 + (4.9 - (y0 + 0.1)) / 4.8 * 9.0 if y0 > 0.1 else 11.0
        cards.append(cube(85.6, 0.76, 54.0, 0, y0 + 0.38, FLOOR + min(11.0, h)))
    shell = [(front, BLACK), (sym_in, IVORY), (plate_all, BLACK)]
    p.scene("eject", shell + [(car_w, RED)] + [(c, PROP if i % 2 else PROP2) for i, c in enumerate(cards)])
    lift = 18.0
    p.scene("eject_open", place(shell + [(mv(car_w, 0, 0, lift), RED)] + [(mv(c, 0, 0, lift), PROP if i % 2 else PROP2) for i, c in enumerate(cards)], rz=180))
    p.scene("eject_build", place([(front, BLACK), (sym_in, IVORY), (mv(plate_all, 0, 34, 0), BLACK), (mv(car_w, 0, 14, 66), RED)], rz=180))
    p.scene("bp_D10", p.scenes["eject_build"]); p.scene("bpo_D10", shell + [(car_w, RED)])
    p.checks = dict(front=front, plate=plate_all, car=car_w, cards=cards, XP=XP, XO=XO)
    p.note = ("92 x 67 x 7.4 mm. Holds up to 6 flat cards (embossed cards take two slots). Push the red tab on the back up 18 mm: "
              "the ramp lifts the front card highest so the stack fans out. Four spring bars on the back plate grip the card edges, so cards stay "
              "put when held any way up; push them back down with your thumb. Front prints face down with the ivory eject mark inlaid, "
              "back plate prints outer face down (bars stand up), slider as it is. Drop the slider in from the back, then press the back plate on "
              "until the four noses click into the side pockets.")
    P["D10"] = p

# ================================================================== D11 Standby: rack for closed laptops
def build_standby():
    p = Product("D11", "standby", "Standby")
    L, D, H = 230.0, 110.0, 12.0
    CY = 8.0
    base = body(rrect(L, D, 6), H, c=0.6, bottom=True)
    chan = yz(Polygon([(CY - 12.5, H - 6.0), (CY + 12.5, H - 6.0), (CY + 10.0, H + 0.1), (CY - 10.0, H + 0.1)]), L + 2, -L / 2 - 1)
    base = base - chan
    base = base - U([cyl(5.5, H + 1, -0.5, x, D / 2, seg=48) for x in (-70, 0, 70)])       # cable notches at the back
    # hollow underside: open pockets with ribs every 50 mm keep it light and still flat on the desk
    pockets = []
    for x0 in np.arange(-105, 105, 50):
        x1 = min(x0 + 46, 105)
        pockets += [box(x0, -D / 2 + 3, x1, CY - 12.5 - 3), box(x0, CY + 12.5 + 3, x1, D / 2 - 3), box(x0, CY - 12.5 - 1, x1, CY + 12.5 + 1)]
    deep = ext(unary_union(pockets[0::3] + pockets[1::3]).difference(unary_union([circle(8.5, x, D / 2) for x in (-70, 0, 70)])), H - 2.4, -0.01)
    shallow = ext(unary_union(pockets[2::3]), H - 6.0 - 2.0, -0.01)
    # The open underside pockets needed 45 mm bridges under the show face. On an FDM printer sparse infill
    # does the lightening, so the base is left solid. Set NS_STANDBY_POCKETS=1 to bring the pockets back.
    if os.environ.get("NS_STANDBY_POCKETS") == "1": base = base - deep - shallow
    base = base - ext(text("STANDBY", 4.0, -98, -42, "l"), 0.5, H - 0.49)
    dot = ext(circle(2.2, -103.5, -42), RAISE, H)
    # fin: slab on a dovetail key with a sprung split
    prof = unary_union([rrect(92, 118, 14, 3, 71), box(-43, H, 49, 40)])
    cuts = unary_union([pill(-32 + i * 8, 78, 4.6, 20 + 52 * W20[i + 4]) for i in range(9)])
    fin = mv(rot(Manifold.extrude(_cs(prof.difference(cuts)), 5.0), 90, 0, 90), -2.5, 0, 0)
    key = yz(Polygon([(CY - 12.5, H - 5.85), (CY + 12.5, H - 5.85), (CY + 9.85, H + 0.01), (CY - 9.85, H + 0.01)]), 18.0, -9.0)   # bottom 0.15 over size a side: the split springs it
    key = key - cube(20, 1.0, 4.5, 0, CY, H - 5.9)
    fin = U([fin, key])
    fin_print = mv(fin, 0, 0, -(H - 5.85))
    p.part("base", base, BLACK, infill=0.15); p.part("standby_dot", dot, RED, infill=1.0)
    p.part("fin", fin_print, BLACK, qty=3, infill=0.15)
    xs = (-20.4, 1.4, 19.7)
    fins = [(mv(fin, x, 0, 0), BLACK) for x in xs]
    lap1 = mv(rot(body(rrect(304, 214, 10), 16.0, c=1.5, steps=3, bottom=True), 0, 90, 0), -78 + 4 + 0.6, 0, H + 107)
    lap1 = mv(rot(rot(body(rrect(214, 304, 10), 16.0, c=1.5, steps=3, bottom=True), 0, 90, 0), 0, 0, 0), -20.4 + 2.5 + 0.4, 0, H + 107)
    lap2 = mv(rot(body(rrect(196, 288, 10), 12.5, c=1.5, steps=3, bottom=True), 0, 90, 0), 1.4 + 2.5 + 0.4, 0, H + 98)
    tab = mv(rot(body(rrect(178, 250, 12), 6.5, c=1.2, steps=3, bottom=True), 0, -90, 0), 40 - 3 - 0.4 - 6.5, 0, H + 89)
    built = [(base, BLACK), (dot, RED)] + fins
    p.scene("standby_bare", built)
    p.scene("standby", built + [(lap1, PROP), (lap2, PROP2)])
    p.scene("standby_build", [(base, BLACK), (dot, RED), (mv(fin, -40, 0, 0), BLACK), (mv(fin, -150, 0, 40), BLACK), (mv(fin, 30, 0, 0), BLACK)])
    p.scene("bp_D11", p.scenes["standby_build"]); p.scene("bpo_D11", built)
    p.note = ("Base 230 x 110 x 12 with a dovetail channel; three fins 92 x 130 slide in from either end and hold by a sprung split key. "
              "Set the gaps to your laptops (10 to 30 mm), slide a fin in, done. Base and fins print upright. Cable notches at the back.")
    P["D11"] = p

# ================================================================== D12 Rotary: key organiser
def build_rotary():
    p = Product("D12", "rotary", "Rotary")
    T = 2.0; X = 30.0
    outline = pill(0, 0, 82, 20)
    def plate(cb_r, cb_d):
        m = ext(outline, T) - U([cyl(1.95, T + 0.2, -0.1, s * X, 0, seg=40) for s in (-1, 1)])
        return m - U([cyl(cb_r, cb_d + 0.01, -0.01, s * X, 0, seg=48) for s in (-1, 1)])   # counterbore on the outer (bed) face
    line = seg_ = LineString([(-14, 0), (14, 0)]).buffer(0.8, quad_segs=8)
    plate_a = plate(3.2, 0.8)
    inlay = ext(line, 0.6, 0.0)
    plate_b = plate(2.9, 0.9) - ext(line, 0.62, -0.01)
    def post(S):
        head = cyl(3.0, 0.8, 0, seg=48)
        shaft = cyl(1.8, T - 0.8 + S + T - 0.9 + 0.05, 0.79, seg=40)
        z_b = 0.8 + (T - 0.8) + S + (T - 0.9)
        barb = cyl(2.2, 0.9, z_b, r2=1.8, seg=40)
        m = U([head, shaft, barb])
        return m - cube(1.2, 8, 5.0, 0, 0, z_b + 0.9 - 5.0 + 0.01)   # rev B1 slit 1.2 x 5.0 (was 0.9 x 3.2)
    loop = pill(0, 0, 34, 14).difference(pill(5, 0, 18, 6.5)).difference(circle(1.95, -11, 0, 40))
    loop_m = body(loop, 2.4, c=0.4, steps=2, bottom=True)
    spacer = ext(ring(4.0, 2.0), 1.0)
    p.part("plate_a", plate_a, BLACK, infill=1.0)
    p.part("plate_b", plate_b, BLACK, infill=1.0); p.part("pointer_inlay", inlay, RED, infill=1.0)
    p.part("post_short", post(6.0), BLACK, qty=2, infill=1.0); p.part("post_long", post(10.0), BLACK, qty=2, infill=1.0)
    p.part("loop", loop_m, BLACK, infill=1.0); p.part("spacer", spacer, BLACK, qty=6, infill=1.0)
    S = 6.0
    a_w = [(plate_a, BLACK)]
    b_w = [(mv(rot(plate_b, 180, 0, 0), 0, 0, 2 * T + S), BLACK), (mv(rot(inlay, 180, 0, 0), 0, 0, 2 * T + S), RED)]
    posts = [(mv(post(S), s * X, 0, 0), BLACK) for s in (-1, 1)]
    # real keys for the renders: bow with pivot hole, shoulder, bitted blade with a milled groove. Brass and nickel, like a house set.
    def key2d(n):
        bow = unary_union([circle(8.6, 0, 0, 64), box(0, -3.6, 15, 3.6)])
        blade = Polygon([(12, 4.2), (50, 4.2), (55.5, 2.4), (55.5, -4.2), (12, -4.2)])
        cuts = [box(x0, -4.3, x0 + 3.1, -4.3 + d) for x0, d in zip(range(20, 52, 5), [2.1, 1.0, 2.8, 1.5, 2.4, 0.9][:6])]
        shape = unary_union([bow, blade]).difference(unary_union(cuts)).difference(circle(2.15, 0, 0, 40))
        return shape
    KT = 1.4                                            # key thickness, four keys fit a 6 mm post gap
    def keyblade(ang, lvl, col, flip=False, n=0):
        k = ext(key2d(n), KT) - ext(LineString([(17, 1.3), (47, 1.3)]).buffer(0.45, quad_segs=4), 0.45, KT - 0.4)
        return (mv(rot(k, 0, 0, ang), -X if flip else X, 0, T + 0.2 + lvl * 1.45), col)
    BR, NI = "brass", "steel"
    # levels 0 and 2 hang on the right post, 1 and 3 on the left, so the blades pass over each other, never through
    folded = [keyblade(178, 0, BR), keyblade(2, 1, NI, True), keyblade(176, 2, NI), keyblade(4, 3, BR, True)]
    built = a_w + b_w + posts
    p.scene("rotary_bare", built)
    p.scene("rotary", built + [keyblade(100, 0, BR), keyblade(2, 1, NI, True), keyblade(128, 2, NI), keyblade(30, 3, BR, True)])
    p.scene("rotary_open", built + [keyblade(58, 0, BR), keyblade(150, 1, NI, True), keyblade(92, 2, NI), keyblade(172, 3, BR, True)])
    pa = [(plate_a, BLACK)] + posts
    ex = [(m, c) for m, c in a_w] + [(mv(m, 0, 0, 30), c) for m, c in b_w] + \
         [(mv(post(6.0), -14, -28, 0), BLACK), (mv(post(10.0), 14, -28, 0), BLACK)] + [(mv(loop_m, 0, 32, 0), BLACK)] + [(mv(spacer, 40 + i * 9, 32, 0), BLACK) for i in range(3)]
    p.scene("rotary_build", ex); p.scene("bp_D12", ex); p.scene("bpo_D12", built)
    p.scene("rotary_s1", ex)
    # step 2: keys go on the posts. Two already on, one above the left post ready to drop, one spacer above the right post
    p.scene("rotary_s2", pa + [keyblade(178, 0, BR), keyblade(2, 1, NI, True), (mv(spacer, X, 0, 24), BLACK),
                               (mv(keyblade(176, 2, NI)[0], 0, 0, 10), NI)])
    p.scene("rotary_s3", pa + folded + [(mv(m, 0, 0, 22), c) for m, c in b_w])
    p.scene("rotary_s4", built + [keyblade(58, 0, BR), keyblade(2, 1, NI, True), keyblade(92, 2, NI), keyblade(4, 3, BR, True)])
    # the loop is a key-sized piece on a post: hole at the left end, slot for a ring at the right
    def loopat(px, ang, z):
        return mv(rot(mv(loop_m, 11, 0, 0), 0, 0, ang), px, 0, z)
    LZ = T + 0.2 + 2 * 1.45
    p.scene("rotary_s5", pa + [keyblade(178, 0, BR), keyblade(2, 1, NI, True), (loopat(-X, 0, LZ + 18), BLACK)])
    ang = 80.0; ca, sa = math.cos(math.radians(ang)), math.sin(math.radians(ang))
    sc_x, sc_y = -X + 16 * ca, 16 * sa                      # slot centre in the plan
    fob_ring = rot(rot(revolve([(8.0 + 0.7 * math.cos(t), 0.7 * math.sin(t)) for t in [i * math.pi / 12 for i in range(24)]], 64), 0, 90, 0), 0, 0, ang)
    fob_ring = mv(fob_ring, sc_x - sa * 8, sc_y + ca * 8, LZ + 1.2)  # centred one radius off the slot so one side of the ring passes through it
    fx, fy = sc_x - sa * 16, sc_y + ca * 16                  # far side of the ring
    fob_b = ext(rrect(40, 26, 6), 9.0) - cube(12, 3.2, 12, 0, -9.0, -1)   # hole for the ring near its end
    fob = mv(rot(fob_b, 0, 0, ang + 90), fx - sa * 17 - 0.0, fy + ca * 17, LZ + 1.2 - 4.5)
    p.scene("rotary_s6", built + [(loopat(-X, ang, LZ), BLACK), (fob_ring, NI), (fob, PROP)])
    p.note = ("82 x 20 mm plates, 2 mm thick. Two posts snap through: short posts for 2 to 4 keys, long posts for 4 to 7, spacers fill the gaps "
              "so the keys stay stiff when you swing them out. The loop takes a car fob. Plates print outer face down (red pointer inlay on plate B).")
    P["D12"] = p

ALL = [build_eject, build_standby, build_rotary]
if __name__ == "__main__":
    only = sys.argv[1:]
    want = lambda f: not only or any(o in f.__name__ or o in {"D10": "eject", "D11": "standby", "D12": "rotary"}.get(o, o) for o in only) or \
        any({"D10": "build_eject", "D11": "build_standby", "D12": "build_rotary"}.get(o) == f.__name__ for o in only)
    for f in ALL:
        if want(f): f()
    rep = {}
    for k, p in P.items():
        rep[k] = p.export()
        print(k, p.name, rep[k]["grams"], "g", [(x["file"], x["size"], x["grams"]) for x in rep[k]["parts"]], flush=True)
    old = {}
    try: old = json.load(open(f"{OUT}/report.json"))
    except Exception: pass
    old.update(rep); json.dump(old, open(f"{OUT}/report.json", "w"), indent=1)
