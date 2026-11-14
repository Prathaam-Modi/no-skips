"""No Skips range V2: print parts (STL) and display scenes for the new and redesigned pieces.
Scenes use the same solids as the STLs, only moved. Run: python3 build.py"""
import math, json, sys
from ns import *

W50 = [0.16,0.27,0.96,0.97,0.98,0.96,0.97,0.96,0.35,0.28,0.36,0.42,0.87,1.0,1.0,1.0,0.95,0.98,0.99,0.99,0.78,0.52,0.42,0.41,0.4,0.41,0.42,0.43,0.43,0.45,0.44,0.12,0.26,0.99,0.97,0.98,0.93,0.94,0.97,0.98,0.95,0.87,0.99,0.94,0.98,0.98,0.99,0.98,1.0,0.73]
RAISE = 0.6
T = math.tan; R = math.radians
def dove(x0, neck, tip, d, cy=0.0, sign=1):
    return Polygon([(x0, cy - neck / 2), (x0 + sign * d, cy - tip / 2), (x0 + sign * d, cy + tip / 2), (x0, cy + neck / 2)])
def flip(m, h=4.0):          # turn a flat piece of overall height h face down, keeping the group together
    return mv(rot(m, 0, 180, 0), 0, 0, h)
def place(items, rx=0, ry=0, rz=0, x=0, y=0, z=0):
    return [(mv(rot(m, rx, ry, rz), x, y, z), c) for m, c in items]
P = {}

# ------------------------------------------------------------------ tags (A5 Track Tag, B3 Alias)
def strap():
    s = unary_union([rrect(104, 4.2, 2, 0, 0), pill(-56, 0, 16, 8.4), box(51, -5.5, 54.2, 5.5).buffer(0.6)])
    s = s.difference(pill(-56.5, 0, 8.5, 3.3))
    return body(s, 1.2, c=0.3, steps=1)
def tag(L, front, back, accent_front, accent_back):
    """Shared tag body: a raised rim stands 0.4 above the artwork so keys rub the rim, not the code."""
    outline = rrect(L, 30, 5)
    hole = circle(4.2, -L / 2 + 9, 0)
    base = body(outline.difference(hole), 3.0, bottom=True, top=False)
    rim = ext(outline.difference(outline.buffer(-1.4)).union(circle(5.6, -L / 2 + 9, 0).difference(hole)).intersection(outline), 1.0, 3.0)
    art = ext(front, RAISE, 3.0)
    inlay = ext(back, 0.4, 0.0)                 # back text is a flush inlay, printed in the first two layers
    black = U([base, rim]) - inlay
    return black, art, inlay
def build_tags():
    p = Product("A5", "track_tag", "Track Tag")
    front = code_art("Starboy|The Weeknd", 6, 0, 56)
    back_txt = affinity.scale(unary_union([fit_text("Starboy", 4.6, 54, -6, 4.2), fit_text("The Weeknd", 3.0, 54, -6, -4.6)]), -1, 1, origin=(0, 0))
    blk, art, inl = tag(80, front, back_txt, IVORY, RED)
    p.part("tag_body", blk, BLACK, infill=1.0); p.part("front_code", art, IVORY, infill=1.0); p.part("back_text_inlay", inl, RED, infill=1.0)
    st = strap(); p.part("loop_strap", st, BLACK, infill=1.0)
    one = [(blk, BLACK), (art, IVORY), (inl, RED)]
    p.scene("songtag", place(one, rz=14, x=-4, y=10) + place([(st, BLACK)], rz=-8, x=6, y=-26))
    backside = [(flip(m), c) for m, c in one]
    p.scene("songtag_sides", place(one, rz=6, y=22) + place(backside, rz=-5, y=-20))
    p.scene("bp_A5", one + place([(st, BLACK)], y=-30))
    p.scene("bpo_A5", one)
    p.note = "Rev B. Print face up. Rim 1.0 mm, code 0.6 mm, so the code sits 0.4 mm below the rim. Back text is a first-layer inlay: reads correctly when the tag is turned over."
    P["A5"] = p

    p = Product("B3", "alias_tag", "Alias")
    front = unary_union([fit_text("Dimo", 5.0, 40, 6, 6.6), fit_text("Mähtarp", 5.0, 40, 6, -0.4), wave(W20, -13.6, -9.2, 2.06, 1.3, 5.2, 1.3)])
    blk, art, inl = tag(70, front, Polygon(), RED, None)
    p.part("tag_body", blk, BLACK, infill=1.0); p.part("front_name", art, RED, infill=1.0); p.part("loop_strap", strap(), BLACK, infill=1.0)
    one = [(blk, BLACK), (art, RED)]
    p.scene("nametag", place(one, rz=12, x=-2, y=10) + place([(strap(), BLACK)], rz=-8, x=6, y=-26))
    p.scene("bp_B3", one + place([(strap(), BLACK)], y=-30)); p.scene("bpo_B3", one)
    p.note = "Rev B. Same body as the Track Tag, 10 mm shorter. Name is raised 0.6 mm inside a 1.0 mm rim."
    P["B3"] = p

# ------------------------------------------------------------------ A1 Track Plate
def build_plate():
    p = Product("A1", "track_plate", "Track Plate")
    out = rrect(140, 70, 5)
    plate = body(out, 3.0, bottom=True)
    code = ext(code_art("Blinding Lights|The Weeknd", 0, 11, 120), RAISE, 3.0)
    txt = ext(unary_union([fit_text("Blinding Lights", 6.2, 110, 0, -14.5), fit_text("The Weeknd", 3.8, 100, 0, -24)]), RAISE, 3.0)
    wav = ext(wave(W50, -58.8, 10, 2.4, 1.6, 34, 2.4), RAISE, 3.0)
    wtxt = ext(unary_union([fit_text("Knowing", 6.0, 66, -60, -22, "l"), fit_text("Dimo Mähtarp", 3.6, 56, 60, -22, "r")]), RAISE, 3.0)
    # one base bar replaces the two loose feet. Slot leans back 12 degrees.
    TH = 12.0; slot_y = 3.0; floor = 5.0
    cutter = mv(rot(cube(141.0, 3.5, 30, 0, 0, 0), -TH, 0, 0), 0, slot_y, floor)
    bar = body(rrect(150, 30, 5), 14.0) - cutter
    stripe = ext(pill(0, -8.5, 120, 3.0), RAISE, 14.0)
    p.part("plate", plate, BLACK, infill=1.0); p.part("code_and_title", U([code, txt]), IVORY, infill=1.0)
    p.part("base_bar", bar, BLACK); p.part("base_stripe", stripe, RED, infill=1.0)
    def stood(items):
        return [(mv(rot(mv(rot(m, 90, 0, 0), 0, 1.5 + 0.0, 35), -TH, 0, 0), 0, slot_y, floor + 0.2), c) for m, c in items]
    base = [(bar, BLACK), (stripe, RED)]
    p.scene("plate", stood([(plate, BLACK), (code, IVORY), (txt, IVORY)]) + base)
    p.scene("plate_wave", stood([(plate, BLACK), (wav, RED), (wtxt, RED)]) + base)
    p.scene("plate_build", place([(plate, BLACK), (code, IVORY), (txt, IVORY)], rz=-6, y=30) + place(base, rz=4, y=-52))
    p.scene("bp_A1", stood([(plate, BLACK), (code, IVORY), (txt, IVORY)]) + base); p.scene("bpo_A1", p.scenes["bp_A1"])
    p.note = "Rev B. One slotted base bar (150 x 30 x 14) replaces the two feet. Plate unchanged at 140 x 70 x 3. Slot 3.5 mm wide, leans back 12 degrees. Wave version: print the wave and title in red instead of the code part."
    P["A1"] = p

# ------------------------------------------------------------------ C3 Gig Coin
def dj():
    head = circle(4.3, 0, 4.2, 48)
    band = circle(6.5, 0, 4.6, 64).difference(circle(5.3, 0, 4.6, 64)).intersection(box(-9, 4.2, 9, 14))
    cups = unary_union([rrect(3.0, 5.6, 1.3, -5.9, 3.6), rrect(3.0, 5.6, 1.3, 5.9, 3.6)])
    neck = box(-2.0, -3.2, 2.0, 1.0)
    sh = affinity.scale(circle(1, 0, 0, 64), 12.5, 7.5); sh = affinity.translate(sh, 0, -9.2).intersection(box(-20, -12.6, 20, 0))
    deck = rrect(26, 2.2, 1.0, 0, -14.2)
    return unary_union([head, band, cups, neck, sh, deck]).intersection(circle(17.6))
def build_coin():
    p = Product("C3", "gig_coin", "Gig Coin")
    a = np.linspace(0, 2 * math.pi, 720, endpoint=False)
    rr = 21.0 - 0.32 * (1 + np.cos(72 * a)) / 2
    reeded = Polygon(np.c_[rr * np.cos(a), rr * np.sin(a)])
    back = affinity.scale(unary_union([fit_text("Dimo Mähtarp", 3.4, 30, 0, 5.4), fit_text("Bengaluru 2026", 2.3, 28, 0, -1.0), fit_text("07/50", 3.0, 16, 0, -8.2)]), -1, 1, origin=(0, 0))
    inlay = ext(back, 0.4, 0)
    coin = U([body(reeded, 3.3, bottom=True, top=False, c=0.4, steps=2), ext(circle(20.4).difference(circle(18.6)), 0.7, 3.3)]) - inlay
    sil = ext(dj(), 0.5, 3.3)
    # frame: a split ring. Standing it in the foot squeezes the two half tabs together and locks the coin.
    ring = circle(24.4).difference(circle(21.3)).union(box(-7, -29.5, 7, -21.6)).union(circle(5.6, 0, 27.6))
    ring = ring.difference(circle(21.3)).difference(circle(2.6, 0, 28.4)).difference(box(-0.6, -30, 0.6, -20.5))
    frame = body(ring, 4.0, c=0.4, steps=2, bottom=True)
    lip = ext(circle(21.5).difference(circle(20.75)), 0.5, 0) + ext(circle(21.5).difference(circle(20.75)), 0.5, 3.5)
    frame = frame + (lip - cube(1.4, 10, 5, 0, -21, 0))
    foot = body(rrect(40, 18, 5), 9.0) - cube(14.5, 4.4, 7.0, 0, 0, 2.2)
    mark = ext(pill(0, -6.0, 26, 1.8), RAISE, 9.0)
    p.part("coin", coin, BLACK, infill=1.0); p.part("silhouette", sil, RED, infill=1.0); p.part("back_text_inlay", inlay, RED, infill=1.0)
    p.part("frame", frame, BLACK, infill=1.0); p.part("foot", foot, BLACK, infill=0.3); p.part("foot_mark", mark, RED, infill=1.0)
    one = [(coin, BLACK), (sil, RED), (inlay, RED)]
    inframe = [(mv(m, 0, 0, 0.0), c) for m, c in one] + [(frame, BLACK)]
    stoodc = [(mv(rot(m, 90, 0, 0), 0, 2.0, 2.2 + 29.5), c) for m, c in inframe]
    p.scene("coin", place(stoodc + [(foot, BLACK), (mark, RED)], rz=-14, x=-16, y=8) + place([(flip(m), c) for m, c in one], rz=10, x=34, y=-22))
    # exploded for the build guide: coin above the frame, foot in front of the frame's two tabs
    p.scene("coin_build", [(mv(m, 0, 0, 30), c) for m, c in one] + [(frame, BLACK), (mv(foot, 0, -52, 0), BLACK), (mv(mark, 0, -52, 0), RED)])
    p.scene("bp_C3", stoodc + [(foot, BLACK), (mark, RED)]); p.scene("bpo_C3", one + [(frame, BLACK)])
    p.note = "Rev B. Reeded edge, rim 0.7 mm above a 0.5 mm silhouette, back text as a first-layer inlay. New snap frame with bag loop and a foot that locks the frame shut."
    P["C3"] = p

# ------------------------------------------------------------------ C4 Side A
def build_sidea():
    p = Product("C4", "side_a", "Side A")
    songs = ["Starboy", "Save Your Tears", "Jungle", "adore u"]
    def cassette(title, acc):
        out = rrect(60, 38, 3)
        holes = unary_union([circle(4.4, -12.5, -4.5, 48), circle(4.4, 12.5, -4.5, 48)])
        b = body(out.difference(holes), 4.0, bottom=True)
        label = rrect(52, 11, 2, 0, 11.2).difference(fit_text(title, 4.2, 46, 0, 11.2))
        rings = unary_union([circle(7.4, -12.5, -4.5, 48).difference(circle(6.2, -12.5, -4.5, 48)), circle(7.4, 12.5, -4.5, 48).difference(circle(6.2, 12.5, -4.5, 48))])
        win = rrect(11, 5, 1.2, 0, -4.5).difference(rrect(8.6, 2.6, 0.6, 0, -4.5))
        trap = Polygon([(-20, -17.2), (20, -17.2), (16.5, -12.4), (-16.5, -12.4)]); trap = trap.difference(trap.buffer(-1.1))
        return b, ext(unary_union([label, rings, win, trap]), RAISE, 4.0)
    TH = 8.0; PITCH = 66.0
    def section():
        s = box(-66, -17, 66, 17).buffer(-2).buffer(2)
        s = s.union(dove(66, 8.0, 12.0, 4.0)).difference(dove(-66, 8.5, 12.5, 4.25).buffer(0.0))
        m = body(s, 10.0, c=0.4, steps=2)
        for cx in (-33, 33):
            m = m - mv(rot(cube(60.6, 4.4, 20, 0, 0, 0), -TH, 0, 0), cx, 4.0, 4.0)
        return m, ext(unary_union([pill(-33, -10.5, 46, 2.4), pill(33, -10.5, 46, 2.4)]), RAISE, 10.0)
    sec, bar = section()
    cs = [cassette(t, RED if i % 2 == 0 else IVORY) for i, t in enumerate(songs)]
    p.part("cassette_body", cs[0][0], BLACK, qty=4, infill=1.0); p.part("cassette_face_example", cs[0][1], RED, qty=4, infill=1.0)
    p.part("rail_section", sec, BLACK, qty=2, infill=0.2); p.part("rail_bar", bar, RED, qty=2, infill=1.0)
    def stand(i, items):
        cx = -99 + i * PITCH
        return [(mv(rot(mv(rot(m, 90, 0, 0), 0, 2.0, 19), -TH, 0, 0), cx, 4.0, 4.2), c) for m, c in items]
    row = []
    for i, (b, f) in enumerate(cs): row += stand(i, [(b, BLACK), (f, RED if i % 2 == 0 else IVORY)])
    rails = place([(sec, BLACK), (bar, RED)], x=-66) + place([(sec, BLACK), (bar, RED)], x=66)
    p.scene("standees", row + rails)
    p.scene("standee_build", place([(sec, BLACK), (bar, RED)], x=-74, y=6) + place([(sec, BLACK), (bar, RED)], x=70, y=-2, rz=-7)
            + place([(cs[0][0], BLACK), (cs[0][1], RED)], rz=12, x=-40, y=-52) + place([(cs[1][0], BLACK), (cs[1][1], IVORY)], rz=-8, x=36, y=-58))
    p.scene("bp_C4", row + rails); p.scene("bpo_C4", stand(1.5, [(cs[0][0], BLACK), (cs[0][1], RED)])[0:0] + place([(sec, BLACK), (bar, RED)]) +
            [(mv(rot(mv(rot(m, 90, 0, 0), 0, 2.0, 19), -TH, 0, 0), -33, 4.0, 4.2), c) for m, c in [(cs[0][0], BLACK), (cs[0][1], RED)]])
    p.note = "Rev B. The four loose feet become two linking rail sections (132 x 34 x 10, two cassettes each). Sliding dovetail, 0.25 mm clearance a side. Add sections to grow the row. Cassettes unchanged at 60 x 38 x 4."
    P["C4"] = p

# ------------------------------------------------------------------ D6 Fold laptop stand
def build_fold():
    p = Product("D6", "fold", "Fold")
    TK = 6.0; ANG = 16.0; L = 236.0; s = T(R(ANG))
    inc = lambda x: 20 + (x - 14) * s
    prof = Polygon([(0, 0), (L, 0), (L, inc(L)), (8, inc(8)), (8, 36), (0, 36)])
    prof = fillet(prof, 2.5)
    slots = []
    xs = np.linspace(66, 216, 14)
    for i, x in enumerate(xs):
        top = inc(x) - 11; h = max(6, (top - 12) * (0.45 + 0.55 * W20[i]))
        slots.append(pill(x, 12 + (top - 12) / 2, 6.0, h))
    NW = 6.35; ND = 12.0
    notch = [box(x - NW / 2, -1, x + NW / 2, ND) for x in (40.0, 226.0 - 20)]
    rib = body(prof.difference(unary_union(slots + notch)), TK, c=0.5, steps=2, bottom=True)
    BL, BH = 240.0, 24.0
    bp_ = fillet(box(0, 0, BL, BH), 2.5).difference(unary_union([box(x - NW / 2, BH - ND, x + NW / 2, BH + 1) for x in (20.0, 220.0)]))
    brace = body(bp_, TK, c=0.5, steps=2, bottom=True)
    bar = ext(pill(BL / 2, 8.5, 120, 4.0), RAISE, TK)
    p.part("side_rib", rib, BLACK, qty=2, infill=0.25); p.part("cross_brace", brace, BLACK, qty=2, infill=0.25); p.part("brace_bar", bar, RED, qty=2, infill=1.0)
    # assembled: ribs stand in x-z at y = +-100, braces stand in y-z at x = 40 and 206
    ribs = [(mv(stand_xz(rib), 0, yy + TK / 2, 0), BLACK) for yy in (-100, 100)]
    def br(x):
        f = lambda m: mv(rot(stand_xz(m), 0, 0, -90), x + TK / 2, 120, 0)
        return [(f(brace), BLACK), (f(bar), RED)]
    asm = ribs + br(40.0) + br(206.0)
    asm = place(asm, rz=90, x=0, y=-118)                         # lip toward the viewer
    lap = cube(315, 218, 15, 0, 109, 0)
    lid = mv(rot(cube(315, 210, 5, 0, 105, 0), 74, 0, 0), 0, 216, 14)      # open screen, hinged at the back edge
    lap = U([lap, lid])
    lap_t = mv(rot(lap, ANG, 0, 0), 0, -118 + 8.6, inc(8) + 0.3)
    p.scene("fold", asm + [(lap_t, PROP)])
    p.scene("fold_bare", asm)
    flat = place([(rib, BLACK)], x=-118, y=-44) + place([(rib, BLACK)], x=-106, y=-58, z=TK + 0.3, rz=4) \
         + place([(brace, BLACK), (bar, RED)], x=-120, y=62) + place([(brace, BLACK), (bar, RED)], x=-112, y=94, rz=-3)
    p.scene("fold_flat", flat)
    p.scene("bp_D6", asm); p.scene("bpo_D6", asm)
    p.note = "Four flat parts, 6 mm thick. Ribs press down onto the two braces with half-lap notches (6.35 mm slot for a 6.0 mm plate). 16 degree tilt, 36 mm front lip. Print every part flat, 4 walls, 25% infill."
    P["D6"] = p

# ------------------------------------------------------------------ D7 Channel desk organiser
def build_channel():
    p = Product("D7", "channel", "Channel")
    WALL, FL, GAP = 2.0, 2.0, 3.6
    def module(w, h, label_levels, dividers=()):
        out = rrect(w, 60, 5); inn = out.buffer(-WALL)
        male = dove(w / 2, 8.0, 12.0, 3.0)
        fem_block = box(-w / 2 - GAP, -10, -w / 2, 10).difference(dove(-w / 2 - GAP, 8.5, 12.5, 3.25, 0, 1))
        shell = body(out, h - 1.2, c=0.4, steps=2, bottom=True, top=False) - ext(inn, h, FL)
        for dx in dividers: shell = shell + cube(WALL, 60 - 2 * WALL + 0.2, h - 6, dx, 0, FL - 0.1)
        links = ext(male, 20.0) + ext(fem_block, 20.0)
        # fader on the front wall: a recessed track with ticks and a raised cap
        relief = Manifold(); caps = Manifold()
        n = len(label_levels)
        for i, lv in enumerate(label_levels):
            cx = (i - (n - 1) / 2) * 20.0
            z0, z1 = 9.0, h - 9.0
            track = mv(cube(2.4, 1.2, z1 - z0, cx, -30 + 0.3, z0), 0, 0, 0)
            ticks = U([cube(7.0 if j % 2 == 0 else 4.4, 1.2, 0.8, cx, -30 + 0.3, z0 + (z1 - z0) * j / 6 - 0.4) for j in range(7)]) if h > 40 else Manifold()
            relief = relief + track + ticks
            zc = z0 + (z1 - z0) * lv
            cap = Manifold.extrude(_cs_trap(), 9.0).rotate((0, 90, 0)).translate((cx - 4.5, -30, zc)) if h > 40 else Manifold()
            caps = caps + cap
        shell = (shell - relief) + caps + links
        band = ext(out.difference(inn), 1.2, h - 1.2)
        return shell, band
    tall, tb = module(60, 100, [0.72]); mid, mb = module(60, 60, [0.38]); tray, yb = module(120, 24, [], dividers=(18,))
    p.part("tall_cup", tall, BLACK); p.part("tall_cup_rim", tb, RED, infill=1.0)
    p.part("mid_cup", mid, BLACK); p.part("mid_cup_rim", mb, IVORY, infill=1.0)
    p.part("tray", tray, BLACK); p.part("tray_rim", yb, RED, infill=1.0)
    xs = (-60 - GAP - 30, -30, 60 + GAP + 0 * 30)     # tall | mid | tray, linked left to right
    xs = (-(60 + GAP) - 30, -30.0, 30 + GAP + 30)
    row = place([(tall, BLACK), (tb, RED)], x=xs[0]) + place([(mid, BLACK), (mb, IVORY)], x=xs[1]) + place([(tray, BLACK), (yb, RED)], x=xs[2] + 0)
    pens = []
    for (dx, dy, tx, ty, col, ln) in [(-6, 8, 9, 5, PROP, 150), (9, -4, -7, 9, PROP2, 142), (4, 14, 4, -8, PROP, 136)]:
        pens.append((mv(rot(cyl(3.6, ln, 0, seg=24) + cyl(3.6, 9, ln, r2=0.5, seg=24), tx, ty, 0), xs[0] + dx, dy, 3), col))
    for (dx, dy, tx, ty, col, ln) in [(-8, 6, 12, -6, PROP2, 118), (10, -6, -10, 8, PROP, 110)]:
        pens.append((mv(rot(cyl(5.0, ln, 0, seg=24), tx, ty, 0), xs[1] + dx, dy, 3), col))
    case = mv(body(rrect(54, 44, 12), 14, c=2.0, steps=5, bottom=True), xs[2] + 12 + 16, 0, FL + 0.2)
    p.scene("channel", row + pens + [(case, PROP)])
    apart = place([(tall, BLACK), (tb, RED)], x=xs[0] - 16, y=10) + place([(mid, BLACK), (mb, IVORY)], x=xs[1], z=34) + place([(tray, BLACK), (yb, RED)], x=xs[2] + 16, y=-6)
    p.scene("channel_build", apart)
    p.scene("bp_D7", row); p.scene("bpo_D7", row)
    p.note = "Three modules, 60 mm deep: tall cup 60 x 100, mid cup 60 x 60, tray 120 x 24. Each has a male dovetail on its right side and a socket on its left, 20 mm tall, 0.25 mm clearance. Lower one module beside the next to link. Print upright, no supports. The rim band is the last 1.2 mm: one filament change."
    P["D7"] = p
def _cs_trap():
    # fader cap section (in the print's y-z plane): 1.6 proud, chamfered underneath so it prints without support
    from ns import _cs
    return _cs(Polygon([(-3.0, 0.2), (-3.0, -1.6), (1.4, -1.6), (3.0, 0.0), (3.0, 0.2)]))

# ------------------------------------------------------------------ D8 B-Side catch-all tray
def build_bside():
    p = Product("D8", "b_side", "B-Side")
    Ro, H, FLr = 80.0, 20.0, 2.8
    prof = [(0, 0), (Ro - 2.5, 0), (Ro, 2.5), (Ro, H - 1.5), (Ro - 1.5, H), (Ro - 2.6, H), (Ro - 4.2, H - 1.6), (Ro - 4.2, FLr + 4)]
    for k in range(1, 7): prof.append((Ro - 4.2 - 4 * math.sin(R(15 * k)), FLr + 4 - 4 * (1 - math.cos(R(15 * k))) / 1.0 * 1.0))
    prof += [(0, FLr)]
    dish = revolve(prof, 160)
    grooves = U([revolve([(r, FLr - 0.45), (r + 1.3, FLr - 0.45), (r + 1.3, FLr + 0.1), (r, FLr + 0.1)], 160) for r in np.arange(31.0, 69.0, 3.4)])
    dish = dish - grooves
    label = ext(circle(26.0).difference(circle(3.6)).difference(fit_text("B-Side", 3.6, 30, 0, 11.5)).difference(fit_text("No Skips", 2.2, 26, 0, -12.5)), RAISE, FLr)
    p.part("tray", dish, BLACK); p.part("label", label, RED, infill=1.0)
    case = mv(rot(body(rrect(62, 48, 14), 22, c=3.0, steps=6, bottom=True), 0, 0, 24), -30, 22, FLr + 0.2)
    ringp = mv(Manifold.revolve(_cs2(circle(1.6, 9.5, 0, 24)), 64), 34, -30, FLr + 1.7)
    pick = mv(rot(ext(fillet(Polygon([(-11, 9), (11, 9), (0, -13)]), 4.0), 0.9), 0, 0, -30), 30, 26, FLr + 0.2)
    p.scene("bside", [(dish, BLACK), (label, RED), (case, PROP), (ringp, PROP2), (pick, IVORY)])
    p.scene("bside_bare", [(dish, BLACK), (label, RED)])
    p.scene("bp_D8", [(dish, BLACK), (label, RED)]); p.scene("bpo_D8", p.scenes["bp_D8"])
    p.note = "One piece, 160 mm across, 20 mm rim. Grooves are cut 0.45 mm into the floor so the raised centre label is the only second colour: one filament change. Print as is, no supports."
    P["D8"] = p
def _cs2(shape):
    from ns import _cs
    return _cs(shape)

# ------------------------------------------------------------------ D9 Perch sofa arm tray (coming soon)
def build_perch():
    p = Product("D9", "perch", "Perch")
    LEN, TH_, RK, PIN = 240.0, 8.0, 4.0, 3.0
    NSEG = 5; SL = LEN / NSEG
    def panel(w, sides):
        """Flat hinged panel. Body spans x = -w/2..w/2 with bullnose edges; hinge axes sit 5 mm outside the body."""
        sec = fillet(box(-w / 2, 0, w / 2, TH_), 3.2)
        m = rot(Manifold.extrude(_cs2(sec), LEN), 90, 0, 0).translate((0, LEN / 2, 0))
        m = mv(m, 0, 0, 0)
        for sgn, par in sides:
            ax = sgn * (w / 2 + 5.0)
            for k in range(NSEG):
                if k % 2 != par: continue
                y0 = -LEN / 2 + k * SL + 0.3; ln = SL - 0.6
                kn = fillet(unary_union([circle(RK, ax, TH_ / 2, 32), box(min(ax, sgn * (w / 2 - 4)), 0, max(ax, sgn * (w / 2 - 4)), TH_)]), 0.01)
                m = m + rot(Manifold.extrude(_cs2(kn), ln), 90, 0, 0).translate((0, y0 + ln, 0))
            m = m - rot(cyl(PIN / 2 + 0.2, LEN + 2, seg=24), 90, 0, 0).translate((ax, LEN / 2 + 1, TH_ / 2))
        return m
    slat_w, table_w = 28.0, 112.0
    table = panel(table_w, [(-1, 0), (1, 0)])
    rim_o = rrect(table_w - 6, LEN - 8, 8); rim = ext(rim_o.difference(rim_o.buffer(-2.4)), 9.0, TH_ - 0.1)
    well = ext(circle(41).difference(circle(38.6)), 3.0, TH_ - 0.1).translate((0, 62, 0))
    table = table + rim + well
    mark = ext(pill(0, -70, 60, 3.2), RAISE, TH_)
    inner = panel(slat_w, [(-1, 1), (1, 0)])       # links table (parity 0) on one edge, outer slat on the other
    outer = panel(slat_w, [(-1, 1)])
    pin = cyl(PIN / 2, LEN - 2, seg=24) + cyl(3.4, 1.6, seg=24)
    p.part("table", table, BLACK, infill=0.15); p.part("table_mark", mark, RED, infill=1.0)
    p.part("inner_slat", inner, BLACK, qty=2); p.part("outer_slat", outer, BLACK, qty=2); p.part("hinge_pin", rot(pin, 90, 0, 0), BLACK, qty=4, infill=1.0)
    # drape over a sofa arm: table flat, inner slats 25 degrees, outer slats 85 degrees
    PITCH_T = table_w / 2 + 5.0; PITCH_S = slat_w / 2 + 5.0
    items = [(table, BLACK), (mark, RED)]
    def chain(sgn):
        out = []
        ax1 = np.array([sgn * PITCH_T, TH_ / 2]); a1 = 24.0; a2 = 84.0
        def tr(m, mirror, pivot_local, pivot_world, ang):
            mm = m if not mirror else rot(m, 0, 0, 180)
            mm = mv(mm, -pivot_local[0], 0, -pivot_local[1])
            mm = rot(mm, 0, sgn * ang, 0)
            return mv(mm, pivot_world[0], 0, pivot_world[1])
        # inner slat: its table-side axis is local x = -19 (unmirrored, for sgn=+1)
        loc_in = (-PITCH_S, TH_ / 2); loc_out = (PITCH_S, TH_ / 2)
        mir = sgn < 0
        s1 = tr(inner, mir, (sgn * loc_in[0], loc_in[1]), ax1, a1)
        d = 2 * PITCH_S
        ax2 = ax1 + np.array([sgn * d * math.cos(R(a1)), -d * math.sin(R(a1))])
        s2 = tr(outer, mir, (sgn * loc_in[0], loc_in[1]), ax2, a2)
        return [(s1, BLACK), (s2, BLACK)]
    worn = items + chain(1) + chain(-1)
    arm_sec = fillet(box(-88, -260, 88, -1.2), 26)
    arm = rot(Manifold.extrude(_cs2(arm_sec), 520), 90, 0, 0).translate((0, 300, 0))
    glass = mv(cyl(33, 96, seg=64, r2=37) - cyl(31, 96, 3, seg=64, r2=35), 0, 62, TH_ + 0.2)
    remote = mv(rot(body(rrect(40, 150, 8), 12, c=2, steps=4, bottom=True), 0, 0, 6), 6, -44, TH_ + 0.2)
    p.scene("perch", worn + [(arm, "sofa"), (glass, "glass"), (remote, PROP)])
    flat = items + place([(inner, BLACK)], x=PITCH_T + PITCH_S) + place([(rot(inner, 0, 0, 180), BLACK)], x=-(PITCH_T + PITCH_S)) \
         + place([(outer, BLACK)], x=PITCH_T + 3 * PITCH_S) + place([(rot(outer, 0, 0, 180), BLACK)], x=-(PITCH_T + 3 * PITCH_S))
    p.scene("perch_flat", flat)
    p.scene("bp_D9", flat); p.scene("bpo_D9", flat)
    p.note = "Concept, not released. Table 122 x 240 with a 9 mm rim and a cup well, two hinged slats a side, four 3 mm hinge pins that slide in by hand. Needs a PETG print and a hot-cup test before sale."
    P["D9"] = p

if __name__ == "__main__":
    only = sys.argv[1:]
    for f in (build_tags, build_plate, build_coin, build_sidea, build_fold, build_channel, build_bside, build_perch): f()
    rep = {}
    for k, p in P.items():
        if only and k not in only: continue
        rep[k] = p.export()
        print(k, p.name, rep[k]["grams"], "g", [(x["file"], x["size"], x["grams"]) for x in rep[k]["parts"]])
    old = {}
    try: old = json.load(open(f"{OUT}/report.json"))
    except Exception: pass
    old.update(rep); json.dump(old, open(f"{OUT}/report.json", "w"), indent=1)
