"""P6B "Hand rack" (28 Nov 2026): a table-standing card holder for poker (63.5 x 88.9) and bridge (57 x 89) cards, 1 to 22 cards.
One piece, no joints, no supports. Card-table line, sits with the deck box and the dealer button.

Form: a 180 x 45 mm footprint (4 x 1 modules of the 45 mm grid) bent on a gentle 700 mm arc, so the hand reads as a fan.
Cross-section, front (player) to back:
  lip      5 mm rail leaning back 18 deg, its front face carries fine horizontal ribs (hides layer lines). Its top 1.0 mm is the
           ONE red element: a red line along the front, printed as the last 5 layers (one colour change per plate).
  slot     7.4 mm wide, leaning back 18 deg. The floor is square to the lean (it slopes down to the back wall), so the bottom edge
           of every card slides into the back corner: one card or 22 cards all lean at the same 18 deg. Closed 6 mm short of
           each end so cards cannot slide out sideways. 45 deg lead-in on both lips.
  backrest the back wall of the slot, its land 1.2 mm below the lip (so the red cap is the only thing in the last layers).
  tail     a low flat tail to the back of the footprint for stability.
Storage: racks stack. A 45 deg V channel under the front locates on the red lip of the rack below, the flat underside lands on
the backrest of the rack below. Same arc, so a stack of 2 or 4 lines up.
Edges: profile corners rounded 0.6, end edges 0.6 stepped bevel, plan corners 1.0. Logo debossed 0.6 underneath.
Usage: NS_OUT=/tmp/p6b python3 build_p6b_handrack.py"""
import math, json, os, sys
from shapely.geometry import Polygon, box
from ns import *
from build2 import logo

A = math.radians(18.0)                 # lean
SA, CA, TA = math.sin(A), math.cos(A), math.tan(A)
R0 = 700.0                             # arc radius at the front foot (centre on the player's side)
D = 45.0                               # footprint depth, one module
L = 180.0                              # overall length (chord at the back edge), four modules
ZF = 5.0                               # slot floor at the back corner
ZT = 23.0                              # top of the lip (top of the part)
CAP = 1.0                              # red cap: last 1.0 mm (5 layers at 0.20)
ZB = ZT - 1.2                          # backrest land
SW = 7.4                               # slot width, square to the lean
TL = 5.0                               # lip thickness, horizontal
LAND = 3.5                             # backrest land width
ZTAIL = 7.0                            # tail height
BACKF = math.radians(70.0)             # back face angle from horizontal
END = 6.0                              # slot closed this far from each end
LEAD = 1.0                             # slot lead-in chamfer
C = 0.6                                # edge bevel / round
RIB_P, RIB_D = 1.6, 0.3                # front and back face ribs: pitch, depth (90 deg V)
YB = TL + SW / CA + ZF * TA            # back wall at the floor (y of the back corner)
HALF = math.asin(L / 2 / (R0 + D))     # half span angle
n_u = (-CA, SA)                        # across the slot, toward the front
w_v = (SA, CA)                         # along the lean, up
def P(u, v): return (YB + u * n_u[0] + v * w_v[0], ZF + u * n_u[1] + v * w_v[1])
def y_front_wall(z): return YB - SW / CA + (z - ZF) * TA   # front wall of the slot at height z (u = SW line)
def y_back_wall(z): return YB + (z - ZF) * TA
def y_mid(z): return YB - SW / 2 / CA + (z - ZF) * TA

# ---------------------------------------------------------------- 2D profile (y = back from the front foot, z = up)
def outline(ext_below=0.0):
    ye = y_back_wall(ZB) + LAND
    ybf = ye + (ZB - ZTAIL) / math.tan(BACKF)
    pts = [(-ext_below * TA, -ext_below), (D, -ext_below), (D, ZTAIL), (ybf, ZTAIL), (ye, ZB),
           (y_mid(ZB), ZB), (y_mid(ZT), ZT), (ZT * TA, ZT)]          # the lip-to-land step sits mid-slot, so the slot cut removes it cleanly
    return Polygon(pts), ybf, ye
def profile(e=0.0):
    """Solid profile eroded by e (for the stepped end bevel). The bottom is never eroded: it stays flat on the bed."""
    p, _, _ = outline(6.0)
    p = p.buffer(2.0, quad_segs=12).buffer(-2.0, quad_segs=12)          # concave corners r 2
    p = p.buffer(-C, quad_segs=10).buffer(C, quad_segs=10)              # convex corners r 0.6
    if e > 0: p = p.buffer(-e, quad_segs=10).intersection(p.buffer(-0.01))   # strictly inside the full profile: no slivers poking out
    return p.intersection(box(-10, 0, D + 10, ZT + 5))
def ribs():
    """Fine 90 deg V grooves across the front face (leaning) and the steep back face. Kept clear of the rounded edges."""
    _, ybf, ye = outline()
    g = []
    def along(p0, p1, normal_out):
        lx, lz = p1[0] - p0[0], p1[1] - p0[1]; ln = math.hypot(lx, lz); tx, tz = lx / ln, lz / ln
        nx, nz = normal_out
        k = 0; s = 2.2
        while s < ln - 2.2:
            cx, cz = p0[0] + tx * s, p0[1] + tz * s
            g.append(Polygon([(cx + tx * RIB_D + nx * 0.3, cz + tz * RIB_D + nz * 0.3), (cx - nx * RIB_D, cz - nz * RIB_D),
                              (cx - tx * RIB_D + nx * 0.3, cz - tz * RIB_D + nz * 0.3)]))
            s += RIB_P
    along((0, 0), (ZT * TA, ZT), (-CA, SA))                               # front face, outward normal toward the player
    nb = (math.sin(BACKF), math.cos(BACKF))
    along((ybf, ZTAIL), (ye, ZB), nb)                                     # back face
    return unary_union(g)
def slot2d():
    s = Polygon([P(0, 0), P(SW, 0), P(SW, 40), P(0, 40)])
    s = s.buffer(-0.3, quad_segs=6).buffer(0.3, quad_segs=6)            # 0.3 mm round in the floor corners
    yb_top, yf_top = y_back_wall(ZB), y_front_wall(ZT)
    lead = unary_union([Polygon([(yb_top - SA * LEAD, ZB - CA * LEAD), (yb_top + LEAD, ZB), (yb_top + LEAD, ZB + 2), (yb_top - 3, ZB + 2)]),
                        Polygon([(yf_top - LEAD, ZT), (yf_top - SA * LEAD, ZT - CA * LEAD), (yf_top + 3, ZT), (yf_top + 3, ZT + 2), (yf_top - LEAD, ZT + 2)])])
    return unary_union([s, lead]).intersection(box(-10, 0.5, D + 10, ZT + 3))
V_HW = 3.00                                                               # V channel half width at the underside (tuned by stack_check: seats on the lip, both sides touching)
V_Y = 9.55                                                                # under the lip (tuned with V_HW, the lip leans so its centre is not the top centre)
def vgroove(hw=V_HW, yc=V_Y):
    return Polygon([(yc - hw - 1, -1), (yc + hw + 1, -1), (yc, hw)])     # 45 deg sides
def full2d(hw=V_HW):
    return profile().difference(slot2d()).difference(ribs()).difference(vgroove(hw))

# ---------------------------------------------------------------- 3D
SEGS = 1800                                                               # 0.2 deg per segment
def rev(shape2d, half_deg):
    """Revolve a (y, z) shape about the arc centre, centred on the +y axis, then move so the front foot centre is y = 0."""
    q = affinity.translate(shape2d, R0, 0)
    m = Manifold.revolve(ns_cs(q), SEGS, 2 * half_deg)
    return m.rotate((0, 0, 90 - half_deg)).translate((0, -R0, 0))
def ns_cs(shape):
    from ns import _cs
    return _cs(shape)
def sector(r0, r1, half, rc=0.0):
    a = np.linspace(math.pi / 2 - half, math.pi / 2 + half, 241)
    pts = [(r1 * math.cos(t), r1 * math.sin(t) - R0) for t in a] + [(r0 * math.cos(t), r0 * math.sin(t) - R0) for t in a[::-1]]
    p = Polygon(pts)
    return p.buffer(-rc, quad_segs=8).buffer(rc, quad_segs=8) if rc else p
def rack(half=HALF, closed=True):
    hd = math.degrees(half) + 1.0
    plan = sector(R0 - 2, R0 + D + 2, half)                              # radially oversize: the revolve owns the front and back faces, the plan only cuts the ends
    steps = 3; parts = []
    for k in range(steps + 1):
        eP, eQ = C * k / steps, C * (steps - k) / steps
        pq = plan.buffer(-eQ, quad_segs=8).intersection(plan.buffer(-0.01)) if eQ > 0 else plan
        parts.append(rev(profile(eP), hd) ^ ext(pq, ZT + 2, -1))
    m = U(parts)
    m = m - rev(ribs(), hd) - rev(vgroove(), hd)
    if closed:
        sh = half - END / (R0 + YB)
        m = m - (rev(slot2d(), hd) ^ ext(sector(R0 - 5, R0 + D + 5, sh), ZT + 4, -1))
    else:
        m = m - rev(slot2d(), hd)
    return m
def underside_logo(m, y=36.0):
    g = affinity.scale(logo(0, 0, 10.0 / 13.6), -1, 1, origin=(0, 0))
    return m - ext(affinity.translate(g, 0, y), 0.6, -0.01)
def split_cap(m):
    """Body and red cap. simplify() folds the sub-micron slivers the booleans leave, so the float32 STL stays one closed body."""
    z = ZT - CAP
    return one(m.trim_by_plane((0, 0, -1), -z).simplify(0.01)), one(m.trim_by_plane((0, 0, 1), z).simplify(0.01))
def one(m):
    """Keep the main body; anything else must be dust (asserted)."""
    ps = sorted(m.decompose(), key=lambda p: -p.volume())
    assert sum(p.volume() for p in ps[1:]) < 0.05, [p.volume() for p in ps[:5]]
    return ps[0]

# ---------------------------------------------------------------- checks
def stack_check(hw=V_HW):
    """2D: drop an identical profile onto another and find where it seats (same arc, so 2D is exact along the length)."""
    lo = full2d(hw); lo_solid = lo
    def hits(dz): return lo_solid.intersection(affinity.translate(lo, 0, dz)).area > 1e-4
    a, b = ZB - 1.0, ZT + 0.5
    for _ in range(50):
        mid = (a + b) / 2
        if hits(mid): a = mid
        else: b = mid
    return b, b - ZB                                                      # pitch, gap above the backrest land
def min_wall_under_slot(hw=V_HW):
    from shapely.geometry import LineString
    s = slot2d(); v = vgroove(hw)
    return s.distance(v)
CARD_T, CARD_G = 0.30, 1.80                                               # thickness mm, mass g (poker card, paper)
def card_sag(r, w=63.5): return w * w / (8 * r)

def card(w=63.5, h=88.9, t=0.3):
    return ext(rrect(w, h, 3.2), t)
def card_in_slot(theta, k, w=63.5, h=88.9, t=0.3):
    """Render prop: card number k from the back wall, its centre at angle theta (rad, 0 = middle). The flat blank is bent onto
    the slot's cone (0.7 mm over its width, as a real card settles), so neighbours stay 0.42 mm apart and never cross."""
    c = card(w, h, t).translate((0, h / 2, 0)).refine_to_length(2.0)       # x across, y up the card, z thickness 0..t
    u0 = 0.05 + k * 0.42
    def f(p):
        x, yc, zt = p
        Y, Z = P(u0 + zt, yc + 0.12)
        r = R0 + Y; ph = theta + x / r
        return (r * math.sin(ph), r * math.cos(ph) - R0, Z)
    return c.warp(f)

if __name__ == "__main__":
    out = {}
    # tune the V so the rack above seats on the lip 0.15 mm above the backrest land
    pitch, gap = stack_check()
    out["stack_pitch_mm"] = round(pitch, 2); out["stack_gap_on_backrest_mm"] = round(gap, 2)
    out["web_slot_to_V_mm"] = round(min_wall_under_slot(), 2)
    m = underside_logo(rack())
    body_b, cap = split_cap(m)
    assert body_b.num_vert() and cap.num_vert()
    # coupon: a 40 mm slice, slot open at the ends, for the slot and stack test (print two)
    ch = math.asin(20.0 / (R0 + D))
    cp = rack(ch, closed=False)
    cp_b, cp_cap = split_cap(cp)

    q = Product("P6B", "hand_rack", "Hand rack")
    q.note = "One piece. Body black or ivory, red cap is the last 1.0 mm (one colour change)."
    q.part("rack_night", body_b, BLACK, infill=0.25)
    q.part("rack_cap_night", cap, RED, on="rack_night")
    q.part("rack_bone", body_b, IVORY, infill=0.25)
    q.part("rack_cap_bone", cap, RED, on="rack_bone")
    q.part("coupon", cp_b, BLACK, qty=2, infill=0.25)
    q.part("coupon_cap", cp_cap, RED, on="coupon")

    # scenes: a hand of 13 blanks fanned along the rail; four racks stacked
    span = 2 * (HALF - (END + 4) / (R0 + YB))
    pitch_a = (span * (R0 + YB) - 63.5) / 12 / (R0 + YB)
    cards = [card_in_slot(-(6 - i) * pitch_a, i) for i in range(13)]
    sc = [(body_b, BLACK), (cap, RED)] + [(c, "card") for c in cards]
    q.scene("handrack", sc)
    st = []
    for i, col in enumerate([IVORY, BLACK, IVORY, BLACK]):
        st += [(mv(body_b, 0, 0, i * pitch), col), (mv(cap, 0, 0, i * pitch), RED)]
    q.scene("handrack_stack", st)
    rep = q.export()

    # ---- numbers
    t = tm(U([body_b, cap]))
    out["bbox_mm"] = [round(float(x), 1) for x in t.extents]
    out["watertight"] = bool(t.is_watertight) and tm(body_b).is_watertight and tm(cap).is_watertight
    out["bodies"] = [len(tm(body_b).split(only_watertight=False)), len(tm(cap).split(only_watertight=False))]
    out["slot"] = dict(width_square_to_lean=SW, lean_deg=18.0, floor="square to the lean, slopes 18 deg down to the back wall",
                       back_wall_depth_along_lean=round((ZB - ZF) / CA, 1), front_wall_depth_along_lean=round((ZT - (ZF + SW * SA)) / CA, 1),
                       lead_in_mm=LEAD, length_mm=round(2 * (HALF - END / (R0 + YB)) * (R0 + YB), 1),
                       card_sag_63_5_mm=round(card_sag(R0 + YB), 2), card_sag_57_mm=round(card_sag(R0 + YB, 57), 2),
                       cards_squared_poker=int((SW - card_sag(R0 + YB)) / CARD_T), cards_squared_bridge=int((SW - card_sag(R0 + YB, 57)) / CARD_T),
                       card_showing_above_lip_mm=round(ZF + 88.9 * CA - ZT, 1))
    # tip-over: 21 cards in one squared stack (worst case, all at the back of the slot), uniform-density rack
    mr = grams(body_b, 0.25) + grams(cap, 1.0)
    vol = t.volume; com_r = t.center_mass
    u_mid = card_sag(R0 + YB) + 21 * CARD_T / 2
    cy, cz = P(u_mid, 88.9 / 2)
    # cards spread along the arc: average y drop of the arc over the slot span
    sh = HALF - END / (R0 + YB); arc_drop = (R0 + cy) * (1 - math.sin(sh) / sh)
    mc = 21 * CARD_G
    com = np.array([0.0, (com_r[1] * mr + (cy - arc_drop) * mc) / (mr + mc), (com_r[2] * mr + cz * mc) / (mr + mc)])
    foot = sector(R0, R0 + D, HALF)
    from shapely.geometry import Point
    pt = Point(com[0], com[1]); inside = foot.contains(pt); dist = foot.exterior.distance(pt)
    # backward tip is the risk: distance to the back edge at x = 0
    d_back = (D - com[1])
    out["tip"] = dict(rack_g=round(mr, 1), cards_g=mc, com_rack=[round(float(x), 1) for x in com_r], com_with_21=[round(float(x), 1) for x in com],
                      inside_footprint=bool(inside), margin_to_back_edge_mm=round(d_back, 1), margin_to_front_edge_mm=round(com[1] - 0, 1),
                      tilt_to_tip_back_deg=round(math.degrees(math.atan(d_back / com[2])), 1),
                      tilt_to_tip_front_deg=round(math.degrees(math.atan(com[1] / com[2])), 1))
    # print estimate per rack at 25% infill, 4 walls
    def g_at(m, inf): return grams(m, inf, shell=1.6)
    for inf in (0.15, 0.25, 0.40):
        out[f"grams_rack_{int(inf * 100)}"] = round(g_at(body_b, inf) + g_at(cap, 1.0), 1)
    out["grams_coupon_each"] = round(g_at(cp_b, 0.25) + g_at(cp_cap, 1.0), 1)
    out["report"] = rep
    print(json.dumps(out, indent=1))
    json.dump(out, open(f"{OUT}/p6b_report.json", "w"), indent=1)
