"""P6A Deck box (28 Nov 2026). Card-table line. A slide-lid box for ONE poker size deck the customer already owns.
Idea: a ribbed tray with a flush dovetail lid that slides out the front. The lid is a single plain slab, printed TOP FACE DOWN on the
textured PEI, with one red bar inlaid in its first 1.2 mm (the only red element). The deck comes out through a stadium window in the
floor: lid off, push the deck up from below with one finger. Colourways: Night (black body and lid) and Bone (ivory body and lid).
Rails: 45 degree dovetail, 1.6 mm reach, lid land 1.0 mm. Rail cutter = resting lid grown by a half ellipsoid (0.30 mm sideways, 0.10 mm over the top).
Detent: a long 0.45 mm bump on each side of the lid near its front end. The bump only ever lives in the first 12 mm of the groove
(the lid never travels deeper), so that stretch carries a 0.30 mm pocket where the bump rests when closed; the plain groove wall in
front of it (0 to 6 mm) is the gate the bump climbs over: 0.15 mm interference per side, taken up by the side walls flexing. Over
the rest of the travel only the plain land runs in the groove, at the full 0.30 mm clearance, so the slide stays free. No snaps, no hinge, no added parts.
Side faces: fine horizontal ribs at 1.0 mm pitch, 0.2 mm deep (0.4 full, 0.4 inset, 0.2 chamfer at 45 degrees), plain band at the top.
Usage: NS_OUT=/tmp/p6a python3 build_p6a_deckbox.py"""
import math, json, os, sys
from ns import *
from build2 import logo

CARD_W, CARD_L, DECK = 63.5, 88.9, 20.0   # poker size; deck stack up to 20 mm (plastic 54-card decks 17 to 19.5)
CLR = 0.35                                # cavity clearance per side around the cards
HEAD = 0.6                                # headroom over a 20 mm deck
WALL, FLOOR = 3.4, 2.4
R_OUT, R_IN = 3.0, 1.0                    # outer corner radius; cavity corners (cards have ~3 mm corners, so they clear)
LID_T, LAND, REACH, CH = 3.0, 1.0, 1.6, 0.3   # lid thickness, vertical land, dovetail reach (45 deg), top edge chamfer
RAIL_A, RAIL_B = 0.30, 0.10               # rail clearance sideways (per side) and over the top (lid resting on the groove floor)
BUMP_H, POCKET = 0.45, 0.15               # detent: 0.45 bump on each lid side rests in a 0.30 deep pocket in the groove wall;
                                          # the 6 mm of plain groove wall in front of the pocket is the gate (0.15 interference per side)
POCKET_Y = (6.75, 11.8)                   # pocket span behind the front face. Starts where the bump ramp is 0.33 high, so when closed
                                          # the ramp rides about 0.04 onto the gate corner on both sides: the lid is pulled back into the seat
SEAT_L, SEAT_T = 8.0, 3.0                 # anti-rattle seat: last 8 mm of each groove, reached through a 3 mm taper
SEAT_A, SEAT_B = 0.06, 0.04               # seat clearance sideways (and at the back end) and over the top
RIB_D, RIB_TOP_GAP = 0.2, 1.0             # rib depth; ribs stop 1 mm under the groove floor (plain band around the lid line)
BAR = (40.0, 4.0, 10.0, 1.2)              # red bar: length, width, centre behind the front face, depth
WIN = (24.0, 40.0, 8.0, 6.0)
# Card grip: four flex leaves in pockets in the long walls hold the deck still (cards need 0.35 a side to drop in freely).
# Leaf strip centre line ends at x 31.675, so its inner corner sits 31.4 from the centre (a 62.8 gap): poker decks 63.0 to 63.6 wide push each tip 0.1 to 0.4 into its pocket
# (0.3 to 1.25% strain in the leaf, about 1 to 5 N a leaf; PLA springs back well under 2%).
LEAF_T, LEAF_RD, LEAF_TIP = 0.6, 1.4, 31.675         # leaf thickness (one 0.6 line), pocket depth into the wall, tip x
LEAF_Y = ((-26.0, 1), (26.0, -1))                     # leaf roots (y) and the direction each leaf runs (toward the middle)
LEAF_DY, LEAF_Z, LEAD = 5.0, (4.4, 18.4), 3.0         # leaf run along the wall, z span, top lead-in height              # floor window: w, l, corner radius, centre y

def outline(hx, y0, y1, r):
    """Lid outline: back corners rounded r, front corners square (the front end is the visible end face)."""
    g = rrect(2 * hx, y1 - y0, r, 0, (y0 + y1) / 2)
    return unary_union([g, box(-hx, y0, hx, (y0 + y1) / 2)])

class Box:
    def __init__(s, cav_l=CARD_L + 2 * CLR, deck=DECK, ribs=True, window=True, mark=True, seat=True, leaves=True):
        s.cx, s.cy = (CARD_W + 2 * CLR) / 2, cav_l / 2
        s.X, s.Y = 2 * (s.cx + WALL), 2 * (s.cy + WALL)
        s.yF = -s.Y / 2
        s.zg = FLOOR + deck + HEAD                   # groove floor = lid underside when the lid rests
        s.H = s.zg + LID_T                           # lid top flush with the body top
        s.ribs, s.window, s.mark, s.seat, s.leaves = ribs, window, mark, seat, leaves

    def lid_core(s, z0, shrink=0.0, run=0.0):
        """Convex lid: hull of the land, the 45 deg bevel, a short vertical and the 0.3 top chamfer.
        run > 0 stretches it out through the front face (used for the rail cutter)."""
        yf = s.yF - run
        L = outline(s.cx + REACH - shrink, yf, s.cy + REACH - shrink, 1.0 + REACH)
        T = outline(s.cx - shrink, yf, s.cy - shrink, 1.0)
        Tc = outline(s.cx - shrink - CH, yf + (0 if run else CH), s.cy - shrink - CH, 1.0)
        e = 0.01
        # 0.2 edge break under the land keeps its corner off the rounded root of the groove
        sl = [ext(L.buffer(-0.2, join_style=2), e, z0), ext(L, e, z0 + 0.2), ext(L, e, z0 + LAND - e), ext(T, e, z0 + LAND + REACH - e),
              ext(T, e, z0 + LID_T - CH - e), ext(Tc, e, z0 + LID_T - e)]
        return Manifold.batch_hull(sl)

    def cutter(s):
        """Lid at rest (on the groove floor) grown by the upper half of an ellipsoid: 0.30 sideways at every height, 0.10 over
        the top, nothing under it (the lid bears on the floor). Runs out through the front face."""
        rest = s.lid_core(s.zg, run=20.0)
        ell = lambda a, b: Manifold.sphere(1.0, 24).scale((a, a, b)).trim_by_plane((0, 0, 1), 0.0)
        loose, tight = rest.minkowski_sum(ell(RAIL_A, RAIL_B)), rest.minkowski_sum(ell(SEAT_A, SEAT_B))
        if not s.seat: return loose
        # The lid's back end only reaches the last SEAT_L of the groove when it is closed, so the groove can be tight there
        # (0.06 a side) without making the slide stiff: the rest of the travel keeps the full 0.30.
        y1 = s.cy + REACH - SEAT_L; y0 = y1 - SEAT_T
        lo = loose.trim_by_plane((0, -1, 0), -y0)                                   # y <= y0
        a = loose.trim_by_plane((0, 1, 0), y0 - 0.01).trim_by_plane((0, -1, 0), -y0)
        b = tight.trim_by_plane((0, 1, 0), y1).trim_by_plane((0, -1, 0), -(y1 + 0.01))
        return U([lo, (a + b).hull(), tight.trim_by_plane((0, 1, 0), y1 - 0.005)])

    def bump(s, z0, shrink=0.0):
        """Long 0.30 bump on each lid side: full 7.0..8.5 mm behind the front face, ramps to zero at 4.7 and 10.8.
        Its face toward the bevel is chamfered 45 deg so it needs no support when the lid prints upside down."""
        x0 = s.cx + REACH - shrink
        pts = []
        for y, h in ((4.7, 0.0), (7.0, BUMP_H), (8.5, BUMP_H), (10.8, 0.0)):
            for z in (z0 + 0.2, z0 + LAND):               # starts above the 0.2 edge break, clear of the groove root
                pts.append((x0 - 0.3, s.yF + y, z))
            if h > 0:
                pts += [(x0 + h, s.yF + y, z0 + 0.25), (x0 + h, s.yF + y, z0 + LAND - h - 0.05)]
        b = Manifold.hull_points(pts)
        return U([b, b.mirror((1, 0, 0))])

    def pocket(s):
        """0.30 deep pocket in the outer wall of each groove where the bump rests when closed. Its ceiling is a 45 deg chamfer."""
        xw = s.cx + REACH + RAIL_A
        y0, y1 = s.yF + POCKET_Y[0], s.yF + POCKET_Y[1]
        pts = []
        for y in (y0, y1):
            pts += [(xw - 0.4, y, s.zg + 0.1), (xw + POCKET, y, s.zg + 0.1), (xw + POCKET, y, s.zg + 0.5),
                    (xw - 0.4, y, s.zg + 0.8 + 0.4), (xw, y, s.zg + 0.8)]
        k = Manifold.hull_points(pts)
        return U([k, k.mirror((1, 0, 0))])

    def leaf_geo(s):
        """Pockets and leaves on both long walls. Built from 0.2 mm slices (one per layer): each slice of a leaf is a 0.6 strip
        from its root, buried 0.3 in the pocket end wall, to its tip. Bottom: each slice may reach 0.2 further than the one below
        (45 deg, no support). Top: over the last LEAD mm the tip backs off to the wall face, so cards slide in from above."""
        from shapely.geometry import LineString
        pockets, leaves = [], []
        z0, z1 = LEAF_Z
        for side in (1, -1):
            for yr, d in LEAF_Y:
                xr = s.cx + LEAF_RD
                yt = yr + d * LEAF_DY
                p = box(s.cx - 0.01, min(yr, yt + d * 1.2), xr, max(yr, yt + d * 1.2))
                top = box(s.cx - 0.01, p.bounds[1], s.cx, p.bounds[3])
                pk = Manifold.batch_hull([ext(p, z1 - z0 + 0.3, z0), ext(top, 0.01, z1 + LEAF_RD + 0.3)])   # 45 deg ceiling
                strips = []
                z = z0
                while z < z1 - 1e-6:
                    k = min(1.0, max(0.0, (z1 - z) / LEAD))                  # 1 below the lead-in, 0 at the top
                    tip = (s.cx + 0.05 - (s.cx + 0.05 - LEAF_TIP) * k, yt)
                    root = (xr + 0.3, yr - d * 0.3)
                    L = math.dist(root, tip); reach = min(L, 0.6 + (z - z0))  # 45 deg underneath
                    end = (root[0] + (tip[0] - root[0]) * reach / L, root[1] + (tip[1] - root[1]) * reach / L)
                    strips.append(ext(LineString([root, end]).buffer(LEAF_T / 2, cap_style=2), 0.2 + 0.005, z))
                    z += 0.2
                lf = U(strips)
                if side < 0: pk, lf = pk.mirror((1, 0, 0)), lf.mirror((1, 0, 0))
                pockets.append(pk); leaves.append(lf)
        return U(pockets), U(leaves)

    def shell(s):
        full = rrect(s.X, s.Y, R_OUT); inset = full.buffer(-RIB_D, quad_segs=12)
        if not s.ribs:
            return body(full, s.H, c=0.6, top=True, bottom=True)
        rtop = s.zg - RIB_TOP_GAP
        parts = [body(full, 2.0 + 0.01, c=0.6, top=False, bottom=True)]
        z = 2.0
        while z < rtop - 1e-6:
            parts += [ext(full, 0.42, z - 0.01), ext(inset, 0.42, z + 0.39),
                      Manifold.batch_hull([ext(inset, 0.01, z + 0.8), ext(full, 0.01, z + 1.0 - 0.01)])]
            z += 1.0
        parts.append(body(full, s.H - rtop, z0=rtop - 0.01, c=0.6, top=True))
        return U(parts)

    def build(s):
        b = s.shell() - s.cutter()
        b = b - ext(rrect(2 * s.cx, 2 * s.cy, R_IN), s.zg - FLOOR + 0.2, FLOOR)
        if s.leaves:
            pk, lf = s.leaf_geo()
            b = U([b - pk, lf])
        if s.window:
            w, l, r, cy = WIN
            b = b - ext(rrect(w, l, r, 0, cy), FLOOR + 1.0, -0.5)
        if s.mark:   # No Skips mark, ~10 mm wide, debossed 0.6 under the floor, mirrored so it reads from below
            b = b - ext(affinity.scale(logo(0, -32.0, 10.0 / 13.6), -1, 1, origin=(0, 0)), 0.6, -0.01)
        return (b - s.pocket()).set_tolerance(1e-3)   # 1 micron: lets manifold collapse the zero-area slivers of the cuts

    def lid(s, shrink=0.0, bar=True, label=None, face=None, name=None):
        """Lid in use position, resting on the groove floor. face K/Q/J engraves a crown, name engraves a line under it (0.4 deep)."""
        z0 = s.zg
        m = U([s.lid_core(z0, shrink), s.bump(z0, shrink)])
        art = Polygon()
        if face: art = unary_union([art, affinity.translate(emblem(face), 0, s.yF + FACE_Y)])
        if name: art = unary_union([art, name_shape(name, 0, s.yF + (NAME_Y if face else FACE_Y - 8))])
        if not art.is_empty: m = m - ext(art, ENG_D + 0.01, s.H - ENG_D)
        red = Manifold()
        if bar:
            bl, bw, by, bd = BAR
            g = rrect(bl, bw, 0.6, 0, s.yF + by)
            red = ext(g, bd, s.H - bd)
            m = m - ext(g, bd + 0.01, s.H - bd)
        if label:   # coupon lids: clearance number debossed 0.4 on the underside, mirrored to read from below
            m = m - ext(affinity.scale(text(label, 4.0, 0, 0), -1, 1, origin=(0, 0)), 0.4, z0 - 0.01)
        return m.set_tolerance(1e-3), red

# ---------------------------------------------------------------- engraving (lid top face, printed face down: no supports, like the red bar)
ENG_D = 0.4                      # recess depth: two 0.2 layers, floor stays smooth against the textured PEI face
NAME_CAP, NAME_MAXW = 4.0, 48.0  # name cap height (4 mm is the smallest that prints clean on a 0.4 nozzle), max width
FACE_Y, NAME_Y = 60.0, 34.0      # emblem and name centres behind the front face
def soft(g, r=0.5): return g.buffer(r, quad_segs=8).buffer(-r, quad_segs=8)   # rounds inside corners so no feature is thinner than ~1 mm
def emblem(face):
    """Minimal face-card crowns as solid silhouettes, ~16 mm wide. K: three-point crown. Q: tiara of five beads. J: band with one plume."""
    band = box(-8, 0, 8, 2.4)
    if face == "K":
        peaks = [Polygon([(cx - 2.8, 2.3), (cx + 2.8, 2.3), (cx, h)]) for cx, h in ((-5.2, 7.2), (0, 9.6), (5.2, 7.2))]
        g = unary_union([band] + peaks)
        g = unary_union([g] + [circle(0.9, cx, h - 0.2) for cx, h in ((-5.2, 7.2), (0, 9.6), (5.2, 7.2))])
    elif face == "Q":
        beads = [circle(r, cx, 2.4 + dy) for cx, r, dy in ((-6.4, 1.2, 1.0), (-3.2, 1.5, 2.3), (0, 2.0, 3.6), (3.2, 1.5, 2.3), (6.4, 1.2, 1.0))]
        g = unary_union([band] + beads)
    else:   # J
        g = unary_union([box(-6, 0, 6, 2.4), box(-1.0, 2.0, 1.0, 4.0), Polygon([(0, 3.6), (3.4, 7.6), (0, 11.6), (-3.4, 7.6)])])
    g = soft(g)
    x0, y0, x1, y1 = g.bounds
    return affinity.scale(affinity.translate(g, -(x0 + x1) / 2, -(y0 + y1) / 2), 1.4, 1.4, origin=(0, 0))
def name_shape(name, cx=0.0, cy=0.0):
    """Name in the printed-part face (Poppins Bold), keeps the case the customer typed, centred, cap height NAME_CAP."""
    k = NAME_CAP / 0.698
    tp = TextPath((0, 0), name, size=k, prop=FontProperties(fname=FONT))
    g = Polygon()
    for ring in tp.to_polygons():
        if len(ring) >= 4: g = g.symmetric_difference(Polygon(ring).buffer(0))
    x0, y0, x1, y1 = g.bounds
    w = x1 - x0
    if w > NAME_MAXW:
        raise SystemExit(f"name '{name}' is {w:.1f} mm wide at the {NAME_CAP} mm minimum cap height: max {NAME_MAXW} mm, shorten it")
    return affinity.translate(g, cx - (x0 + x1) / 2, cy - NAME_CAP / 2)

def flip(m): return m.rotate((180, 0, 0))     # lid prints top face down

def deck_prop(h=18.6, lift=0.0):
    return ext(rrect(CARD_W, CARD_L, 3.0), h, FLOOR + lift)

# ---------------------------------------------------------------- checks
def rattle(lid, body_, B):
    """How far the CLOSED lid can move before it touches the body: 6 straight moves and 3 tilts about its middle
    (0.003 lift first so resting on the groove floor is not counted). Zero everywhere means nothing can rattle."""
    hit = lambda m: touch(m.translate((0, 0, 0.003)), body_) > 1e-4
    out = {}
    for nm, v in (("back", (0, 1, 0)), ("forward", (0, -1, 0)), ("left", (-1, 0, 0)), ("right", (1, 0, 0)), ("up", (0, 0, 1))):
        d = 0.0
        while d < 2 and not hit(lid.translate(tuple(x * (d + 0.01) for x in v))): d += 0.01
        out[nm] = round(d, 2)
    c = (0, (B.yF + B.cy + REACH) / 2, B.zg + 1.5)
    for nm, ax in (("pitch", 0), ("yaw", 2), ("roll", 1)):
        worst = 0.0
        for sg in (1, -1):
            a = 0.0
            while a < 1:
                r = [0, 0, 0]; r[ax] = sg * (a + 0.01)
                if hit(lid.translate(tuple(-q for q in c)).rotate(tuple(r)).translate(c)): break
                a += 0.01
            worst = max(worst, a)
        out[nm + "_deg"] = round(worst, 2)
    return out
def vol(m): return m.volume() if not m.is_empty() else 0.0
def touch(a, b): return vol(a ^ b)
def play(lid, body_, axis, step=0.01, lim=2.0):
    """How far the lid can move along +axis before it hits the body (it rests on the groove floor, so it is lifted 0.02 first
    for the sideways test, and that 0.02 is added back for the lift test)."""
    if axis != 2: lid = lid.translate((0, 0, 0.02))
    d = 0.0 if axis != 2 else 0.02
    while d < lim:
        v = [0, 0, 0]; v[axis] = d + step
        if touch(lid.translate(tuple(v)), body_) > 1e-4: return round(d, 2)
        d += step
    return None

if __name__ == "__main__":
    B = Box(); body_ = B.build(); lid_, bar_ = B.lid(face="K")
    lid_bone_, _ = B.lid(face="Q", name=os.environ.get("NS_NAME", "Meera"))   # render sample: queen with a name
    C = Box(cav_l=22.0, deck=3.0, ribs=False, window=False, mark=False, leaves=False)
    cb = C.build(); l30, _ = C.lid(bar=False, label="30"); l35, _ = C.lid(shrink=0.05, bar=False, label="35")
    l27, _ = C.lid(shrink=-0.03, bar=False, label="27")
    p = Product("P6A", "deck_box", "Deck box")
    for col, sfx in ((BLACK, "night"), (IVORY, "bone")):
        p.part(f"body_{sfx}", body_, col, infill=0.15)
        p.part(f"lid_{sfx}", flip(lid_), col, infill=0.15)
        p.part(f"lid_bar_{sfx}", flip(bar_), RED, on=f"lid_{sfx}")
    p.part("coupon_body", cb, BLACK); p.part("coupon_lid_30", flip(l30), BLACK); p.part("coupon_lid_35", flip(l35), BLACK); p.part("coupon_lid_27", flip(l27), BLACK)
    for sfx, col in (("night", BLACK), ("bone", IVORY)):      # queen and jack lids: same bar, same body
        for fc in ("Q", "J"):
            lq, _ = B.lid(face=fc)
            p.part(f"lid_{sfx}_{fc.lower()}", flip(lq), col, infill=0.15)
            p.part(f"lid_bar_{sfx}_{fc.lower()}", flip(bar_), RED, on=f"lid_{sfx}_{fc.lower()}")
    # grip coupon: a 30 mm slice of the body (floor, both long walls, one leaf pair), ends open so a real deck lies across it.
    # Two strips: as designed (62.8 gap) and 0.2 looser (63.0 gap). Tells us how the leaves print before a full body.
    for lab, tip in (("628", LEAF_TIP), ("630", LEAF_TIP + 0.1)):
        import build_p6a_deckbox as _m
        old = _m.LEAF_TIP; _m.LEAF_TIP = tip; _m.LEAF_Y = ((-15.0, 1),)
        G = Box(); gb = G.build()
        _m.LEAF_TIP = old; _m.LEAF_Y = ((-26.0, 1), (26.0, -1))
        gb = (gb ^ ext(box(-G.X, -17.5, G.X, -2.5), LEAF_Z[1] + 2.5, -1)).translate((0, 10, 0))
        gb = gb - ext(affinity.scale(text(lab, 4.0, 0, 0), -1, 1, origin=(0, 0)), 0.4, -0.01)
        p.part(f"grip_coupon_{lab}", gb, BLACK)
    pn, _ = B.lid(face="K", name="No Skips")                   # name line check (widest typical name)
    p.part("sample_lid_name", flip(pn), BLACK)
    deck = deck_prop()
    p.scene("deckbox_closed", [(body_, BLACK), (lid_, BLACK), (bar_, RED),
                               (mv(body_, 84, 30, 0), IVORY), (mv(lid_bone_, 84, 30, 0), IVORY), (mv(bar_, 84, 30, 0), RED)])
    o = -52.0
    p.scene("deckbox_open", [(body_, BLACK), (mv(lid_, 0, o, 0), BLACK), (mv(bar_, 0, o, 0), RED), (deck, PROP2)])
    p.note = ("Body prints upright (floor on the PEI), lid prints top face down with the red bar in its first 1.2 mm. Slide the lid in "
              "from the front until it clicks over the gates. Lid off, push the deck up through the floor window.")
    rep = p.export()

    # ---------------- fit check
    nom_x = round(B.cx + REACH + RAIL_A - (B.cx + REACH), 3)
    fit = dict(
        outer_mm=[round(B.X, 1), round(B.Y, 1), round(B.H, 1)],
        cavity_mm=[round(2 * B.cx, 2), round(2 * B.cy, 2), round(B.zg - FLOOR, 2)],
        card_clearance_per_side_x=round(B.cx - CARD_W / 2, 3), card_clearance_per_side_y=round(B.cy - CARD_L / 2, 3),
        deck_allowance_over_20mm=round(B.zg - FLOOR - DECK, 2),
        rail_clearance_per_side_nominal=nom_x, rail_clearance_over_top=RAIL_B,
        lid_side_play_mid_travel_each_way=play(lid_.translate((0, -30, 0)), body_, 0), lid_side_play_closed_each_way=play(lid_, body_, 0),
        lid_lift_play_closed=play(lid_, body_, 2), lid_lift_play_mid_travel=play(lid_.translate((0, -30, 0)), body_, 2),
        lid_travel_to_free=round(B.cy + REACH - B.yF, 1),
        wall=dict(side_below_rail=WALL, behind_rail_land=round(WALL - REACH - RAIL_A, 2), top_rim=round(B.X / 2 - (B.cx + RAIL_A), 2),
                  back_rim=round(B.Y / 2 - (B.cy + RAIL_A), 2), floor=FLOOR, lid=LID_T, under_bar=round(LID_T - BAR[3], 2)),
        overlap_body_lid_closed=round(touch(body_, lid_), 4), overlap_body_bar=round(touch(body_, bar_), 4),
        overlap_deck_body=round(touch(deck_prop(DECK), body_), 4), overlap_deck_lid=round(touch(deck_prop(DECK), lid_), 4),
        detent_interference_per_side=round(BUMP_H - RAIL_A, 2), bump_free_in_pocket_per_side=round(RAIL_A + POCKET - BUMP_H, 2),
        detent_engaged_volume_mm3=round(touch(lid_.translate((0, -4.75, 0)), body_), 3),   # bump plateau over the gate
        coupon_overlap=round(touch(cb, l30) + touch(cb, l35), 4),
        seat=dict(length=SEAT_L, taper=SEAT_T, side_clearance=SEAT_A, top_clearance=SEAT_B),
        closed_lid_free_travel_mm=rattle(lid_, body_, B),
        detent_preload_closed_mm3=round(touch(lid_, body_), 4),
        leaf_gap_mm=round(2 * (LEAF_TIP - 0.275), 2),
        deck_63_5_vs_body_without_leaves=round(touch(deck_prop(18.0), Box(leaves=False).build()), 4),
    )
    stl_dir = f"{OUT}/stl/P6A_deck_box"
    import trimesh as T
    fit["stl"] = {}
    for f in sorted(os.listdir(stl_dir)):
        # manifold3d leaves a few zero-area slivers where cut faces meet; once vertices are merged they read as open edges.
        # Drop them and write the file again: same volume, one closed body.
        t = T.load(f"{stl_dir}/{f}")
        if not t.is_watertight:
            t.update_faces(t.nondegenerate_faces(height=1e-6)); t.remove_unreferenced_vertices(); t.merge_vertices()
        assert t.is_watertight and len(t.split(only_watertight=False)) == 1, f
        t.export(f"{stl_dir}/{f}"); t = T.load(f"{stl_dir}/{f}")
        fit["stl"][f] = dict(watertight=bool(t.is_watertight), bodies=len(t.split(only_watertight=False)), size=[round(x, 1) for x in t.extents])
    g = {}
    for label, m, colour, qty, infill in p.parts: g[label] = round(grams(m, infill), 1)
    fit["grams"] = g
    rep["fit"] = fit
    json.dump(rep, open(f"{OUT}/p6a_report.json", "w"), indent=1)
    print(json.dumps(fit, indent=1))
