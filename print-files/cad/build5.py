"""No Skips: Drumroll, the hand rolling machine (D13). King size slim by default.

Run: python3 build5.py                 build, check, export STLs and scenes   (NS_OUT=<dir> sets the output folder)
     python3 build5.py render [names]  studio renders (render.py, shots injected from here)
     python3 build5.py guides          labelled build and use pictures (annotate.py)
     python3 build5.py blueprint       drawing sheet (blueprint.py)
     NS_PAPER=78 python3 build5.py     a "regular" 78 mm machine (also set NS_PAPER_W=36 if you want the prop to match)

Axes: x along the rollers, y front (-, the user) to back (+), z up. Section drawings are in (y, z).
Mechanism: belt (apron) runs round three rods that all sit INSIDE the belt loop.
  Roller A  front, fixed bearings, flanged so the belt cannot walk.
  Roller B  rear, its two hub pins ride in a J slot: back = OPEN, forward and down into the seat = CLOSED.
  Capstan   idler under the pocket. It carries the return span below the pocket, so belt never rubs on belt
            (TPU on TPU grabs) and the pocket diameter is set by belt length alone.
Turning both rollers toward you drags the rear roller toward the front one, so rolling holds it shut.
Everything is PLA except the belt (TPU 95A, printed standing as a seamless loop).
"""
import math, json, sys, os
from ns import *
from ns import _cs
from shapely.geometry import LineString

# ------------------------------------------------------------------ parameters (edit these)
PAPER_L   = float(os.environ.get("NS_PAPER", 110.0))   # longest paper the machine takes (king size slim 108 to 110)
PAPER_W   = float(os.environ.get("NS_PAPER_W", 44.0))  # paper width, render prop only
DIAS      = (7.0, 8.0, 9.0)          # target roll diameters, one belt each
DIA_NOM   = 8.0
BELT_T    = 0.45                     # belt wall, one 0.45 mm line of TPU 95A
BELT_SIDE = 0.5                      # belt edge to flange, each side
ROLL_D    = 10.0                     # rollers A and B
ROLL_FLAT = 4.0                      # axis height above the bed when printed lying down (flat is 6 wide, 1 deep)
IDLER_D   = 8.4
IDLER_FLAT = 3.5
NIP       = 2.0                      # gap between bare rollers when closed (two belt walls 0.9 + 1.1 for the paper)
TRAVEL    = 10.0                     # how far roller B slides back to open
SEAT      = 1.2                      # roller B drops this far into its closed seat (the detent)
FLANGE_T, FLANGE_H = 1.2, 1.2        # flange thickness and height above the roller surface (A and capstan)
PIN_D     = 5.0                      # hub journal
PIN_CL    = 0.25                     # journal clearance a side in the plate holes and slot
HEX_AF, HEX_CL = 4.2, 0.15           # hub drive: hex key into the roller end, clearance a side
RIB       = 0.10                     # crush rib interference (holds the hub in the roller)
HEX_L, SOCK_L = 8.0, 8.6
PLATE_T   = 3.0
END_GAP   = 0.3                      # roller end to plate, and plate to hub, each
HUB_D, HUB_T = 11.0, 2.4
FLOOR, WALL, WALL_H = 1.4, 1.4, 9.0
POKER, POKER_CL = 4.0, 0.25          # square stick and its clearance a side

BELT_W   = PAPER_L + 0.6
ROLLER_L = BELT_W + 2 * BELT_SIDE + 2 * FLANGE_T
r, ri, t = ROLL_D / 2, IDLER_D / 2, BELT_T
RA = RB = r + t / 2; RI = ri + t / 2                    # belt centreline radii
C = ROLL_D + NIP                                         # closed centre distance
A0 = np.array([-C / 2, 0.0]); B_CLOSED = np.array([C / 2, 0.0]); B_OPEN = np.array([C / 2 + TRAVEL, 0.0])
SLOT = [(C / 2, 0.0), (C / 2 + 0.7, SEAT), (C / 2 + TRAVEL - 0.8, SEAT), (C / 2 + TRAVEL, SEAT - 0.6)]   # path of roller B's axis
B_OPEN = np.array(SLOT[-1])
def pocket_depth(d):                 # pocket centre below the roller axes, closed
    return math.sqrt((r + t + d / 2) ** 2 - (C / 2) ** 2)
ZI = -(pocket_depth(max(DIAS)) + max(DIAS) / 2 + t + 1.0 + t + ri)      # capstan axis: 1 mm of air under the biggest pocket
I0 = np.array([0.0, ZI])
XI = ROLLER_L / 2 + END_GAP; XO = XI + PLATE_T           # plate inner and outer faces
ZF = ZI - max(ri + t, ri + FLANGE_H) - 1.0               # floor top
Z0 = ZF - FLOOR; Z1 = SEAT + PIN_D / 2 + PIN_CL + 2.4
Y0 = -C / 2 - r - t - 2.0; Y1 = C / 2 + TRAVEL + PIN_D / 2 + PIN_CL + 3.0
YP, ZP = Y0 + WALL + POKER_CL + POKER / 2 + 0.1, ZF + POKER / 2 + 0.1   # poker lane centre

# ------------------------------------------------------------------ belt maths
def _ang(v): return math.atan2(v[1], v[0])
def _tan(Ci, Ri, Cj, Rj):
    """Outward normal angle of the outer tangent from circle i to circle j, loop taken anticlockwise."""
    d = Cj - Ci; return _ang(d) - math.pi / 2 + math.asin((Ri - Rj) / np.linalg.norm(d))
def _arc(Cn, R, a0, a1, ccw=True, step=math.radians(2)):
    sw = (a1 - a0) % (2 * math.pi) if ccw else (a0 - a1) % (2 * math.pi)
    n = max(2, int(sw / step) + 1)
    aa = [a0 + (1 if ccw else -1) * sw * i / n for i in range(n + 1)]
    return [(Cn[0] + R * math.cos(a), Cn[1] + R * math.sin(a)) for a in aa], R * sw
def belt_path(B, rp=None, lower=True):
    """Belt centreline with roller B's axis at B. rp = radius of the pocket or trough arc (belt centreline),
    None = no slack. Returns (points, length, pocket centre). Loop order: A, capstan, B, pocket."""
    nAI, nIB = _tan(A0, RA, I0, RI), _tan(I0, RI, B, RB)
    if rp is None:
        nBA = _tan(B, RB, A0, RA); P = None
        a, la = _arc(A0, RA, nBA, nAI); i, li = _arc(I0, RI, nAI, nIB); b, lb = _arc(B, RB, nIB, nBA)
        pts = a + i + b; L = la + li + lb
    else:
        d = np.linalg.norm(B - A0); u = (B - A0) / d
        k = ((RA + rp) ** 2 - (RB + rp) ** 2 + d * d) / (2 * d); h = math.sqrt(max((RA + rp) ** 2 - k * k, 0.0))
        P = A0 + k * u + (-h if lower else h) * np.array([-u[1], u[0]])
        a, la = _arc(A0, RA, _ang(P - A0), nAI); i, li = _arc(I0, RI, nAI, nIB); b, lb = _arc(B, RB, nIB, _ang(P - B))
        p, lp = _arc(P, rp, _ang(B - P), _ang(A0 - P), ccw=False)
        pts = a + i + b + p; L = la + li + lb + lp
    L += np.linalg.norm(np.array(a[-1]) - i[0]) + np.linalg.norm(np.array(i[-1]) - b[0])
    if rp is None: L += np.linalg.norm(np.array(b[-1]) - a[0])
    return pts, L, P
def belt_length(d):
    """Belt length for a roll of diameter d: the closed path with the pocket arc wrapped round the fill."""
    return belt_path(B_CLOSED, d / 2 + t / 2)[1]
def belt_at(B, L):
    """Shape a belt of length L takes with roller B at B and all its slack in the trough between the rollers."""
    taut = belt_path(B)[1]
    if L <= taut: return None
    rmin = (np.linalg.norm(B - A0) - RA - RB) / 2 + 1e-6
    f = lambda rp, lo: belt_path(B, rp, lo)[1] - L
    if rmin > 0 and f(rmin, True) > 0:            # shallow trough: arc centre above the roller axes
        lo, hi = rmin, 2000.0
        for _ in range(80):
            mid = (lo + hi) / 2
            if f(mid, False) > 0: lo = mid
            else: hi = mid
        return belt_path(B, lo, False)
    lo, hi = max(rmin, 0.2), 200.0                # deep trough or pocket: arc centre below
    for _ in range(80):
        mid = (lo + hi) / 2
        if f(mid, True) > 0: hi = mid
        else: lo = mid
    return belt_path(B, lo, True)
BELTS = {d: belt_length(d) for d in DIAS}

# ------------------------------------------------------------------ solids
def yz(shape, length, x0=0.0):
    """A profile drawn in (y, z) extruded along +x from x0."""
    return ext(shape, length).transform([[0, 0, 1, x0], [1, 0, 0, 0], [0, 1, 0, 0]])
def hexagon(af, cy=0.0, cz=0.0):
    R = af / math.sqrt(3)
    return Polygon([(cy + R * math.cos(math.radians(60 * i)), cz + R * math.sin(math.radians(60 * i))) for i in range(6)])
def logo(cx, cy, s=1.0):
    ch = lambda x: Polygon([(x, 0), (x + 4 * s, 4 * s), (x, 8 * s), (x + 2.2 * s, 8 * s), (x + 6.2 * s, 4 * s), (x + 2.2 * s, 0)])
    chev = unary_union([ch(0), ch(4.6 * s)]); bar = box(11.6 * s, 0, 13.6 * s, 8 * s)
    return affinity.translate(chev, cx - 6.8 * s, cy - 4 * s), affinity.translate(bar, cx - 6.8 * s, cy - 4 * s)

def rod(d, flat, length, flange=False):
    """Roller in print orientation: lying along x, flat on the bed (bed at z = -flat), hex socket in each end."""
    prof = circle(d / 2).intersection(box(-50, -flat, 50, 50))
    m = yz(prof, length, -length / 2)
    if flange:
        fp = circle(d / 2 + FLANGE_H).intersection(box(-50, -flat, 50, 50))
        m = U([m] + [yz(fp, FLANGE_T, s * (length / 2 - FLANGE_T / 2) - FLANGE_T / 2) for s in (-1, 1)])
    sock = hexagon(HEX_AF + 2 * HEX_CL)
    return m - U([yz(sock, SOCK_L + 0.01, s * (length / 2 - SOCK_L / 2) - SOCK_L / 2 - (0.01 if s < 0 else 0)) for s in (-1, 1)])

def hub(sprocket=True, ribs=True):
    """Print orientation: outer face on the bed, pin up. Disc, round journal, hex key with three crush ribs."""
    j = 2 * END_GAP + PLATE_T
    hx = affinity.rotate(hexagon(HEX_AF), 90, origin=(0, 0))        # vertices on the y axis, to match the roller sockets
    parts = [cyl(HUB_D / 2, HUB_T), cyl(PIN_D / 2, j + 0.01, HUB_T - 0.01), ext(hx, HEX_L - 0.8, HUB_T + j - 0.01),
             Manifold.extrude(_cs(hx), 0.8, 1, 0, (0.72, 0.72)).translate((0, 0, HUB_T + j + HEX_L - 0.8 - 0.02))]
    if ribs:
        for k in range(3):
            rb = cube(HEX_AF / 2 + HEX_CL + RIB, 0.6, HEX_L - 2.0, (HEX_AF / 2 + HEX_CL + RIB) / 2, 0, HUB_T + j + 0.6)
            parts.append(rot(rb, 0, 0, 120 * k))
    m = U(parts)
    if sprocket:                                                    # cassette reel: ring, six teeth, spindle
        rec = circle(4.3).difference(circle(1.5))
        teeth = unary_union([affinity.rotate(box(2.7, -0.7, 4.6, 0.7), 60 * k, origin=(0, 0)) for k in range(6)])
        m = m - ext(rec.difference(teeth), 0.8, -0.01)
    else:                                                           # capstan cap: plain, one small dimple
        m = m - cyl(1.6, 0.6, -0.01)
    return m
def place_hub(h, side, yc, zc):
    """Hub from print orientation to the outside of an end plate (side = +1 right, -1 left), pin pointing in."""
    return mv(rot(h, 0, -90 * side, 0), side * (XO + END_GAP + HUB_T), yc, zc)

def slot2d(grow=0.0):
    return LineString(SLOT).buffer(PIN_D / 2 + PIN_CL + grow, quad_segs=24)
def build_frame():
    outline = rrect(Y1 - Y0, Z1 - Z0, 3.0, (Y0 + Y1) / 2, (Z0 + Z1) / 2)
    ph = box(YP - POKER / 2 - POKER_CL, ZF, YP + POKER / 2 + POKER_CL, ZF + POKER + 2 * POKER_CL)
    plate = outline.difference(unary_union([circle(PIN_D / 2 + PIN_CL, A0[0], A0[1]), circle(PIN_D / 2 + PIN_CL, I0[0], I0[1]), slot2d(), ph]))
    tray = outline.difference(outline.buffer(-WALL, quad_segs=12)).intersection(box(-99, -99, 99, ZF + WALL_H))
    tray = unary_union([tray, outline.intersection(box(-99, -99, 99, ZF))]).difference(ph)      # square lane for the poker
    fence = box(YP + POKER / 2 + POKER_CL + 0.1, ZF - 0.1, YP + POKER / 2 + POKER_CL + 1.3, ZF + POKER + 0.4)
    fr = U([yz(plate, PLATE_T, XI), yz(plate, PLATE_T, -XO), yz(unary_union([tray, fence]), 2 * XI + 0.2, -XI - 0.1)])
    # lockup under the floor, mirrored so it reads when you turn the machine over. First 0.6 mm, flush inlay.
    k = min(1.0, (ROLLER_L - 20) / 76.0)
    chev, bar = logo(-31.0 * k, 0, 0.95 * k); word = text("NO SKIPS", 5.4 * k, 9.0 * k, 0)
    flip = lambda g: affinity.translate(affinity.scale(g, 1, -1, origin=(0, 0)), 0, (Y0 + Y1) / 2)
    iv, rd = flip(unary_union([chev, word])), flip(bar)
    fr = fr - ext(iv.buffer(0.05), 0.6, Z0 - 0.01) - ext(rd.buffer(0.05), 0.6, Z0 - 0.01)
    return fr, ext(iv, 0.6, Z0), ext(rd, 0.6, Z0)

def build_poker(bumps=True):
    """Print orientation = stowed orientation: square stick lying on its side, head at +x outside the right plate."""
    Ls = 2 * XO - 0.6
    plan = Polygon([(XO, -POKER / 2), (XO - Ls + 12, -POKER / 2), (XO - Ls, -1.2), (XO - Ls, 1.2), (XO - Ls + 12, POKER / 2), (XO, POKER / 2)])
    m = [ext(plan, POKER), ext(rrect(HUB_T, 6.0, 0.8, XO + HUB_T / 2, 0), 6.4)]
    if bumps:                                                       # two soft bumps that wedge in the plate hole
        for s in (-1, 1): m.append(cyl(0.9, POKER - 1.0, 0.5, XO - PLATE_T / 2, s * (POKER / 2 + POKER_CL + 0.07 - 0.9), seg=32))
    return mv(U(m), 0, YP, ZF + 0.1)

def belt_tube(L):
    rm = L / (2 * math.pi)
    return ext(circle(rm + t / 2, seg=256).difference(circle(rm - t / 2, seg=256)), BELT_W)
def belt_solid(pts):
    ring = LineString(list(pts) + [pts[0]]).buffer(t / 2, quad_segs=6)
    return yz(ring, BELT_W, -BELT_W / 2)
def xcyl(rad, length, yc, zc, x0):
    return yz(circle(rad, yc, zc, 48), length, x0)

P = {}
INFO = {}
def build_drumroll():
    p = Product("D13", "drumroll", "Drumroll")
    frame, mark_iv, mark_rd = build_frame()
    rA = rod(ROLL_D, ROLL_FLAT, ROLLER_L, flange=True); rBm = rod(ROLL_D, ROLL_FLAT, ROLLER_L)
    rI = rod(IDLER_D, IDLER_FLAT, ROLLER_L, flange=True)
    hb, cap = hub(True), hub(False); hb0 = hub(True, ribs=False)
    poker, poker0 = build_poker(), build_poker(False)
    # print parts
    p.part("base", frame, BLACK, infill=0.15)
    p.part("base_mark", mark_iv, IVORY, infill=1.0)
    p.part("base_bar", mark_rd, RED, infill=1.0)
    p.part("roller_a_flanged", rA, BLACK, infill=0.25)
    p.part("roller_b_plain", rBm, BLACK, infill=0.25)
    p.part("capstan", rI, BLACK, infill=0.25)
    p.part("capstan_cap", cap, BLACK, qty=2, infill=1.0)
    p.part("reel_hub", hb, RED, qty=4, infill=1.0)
    p.part("poker", poker, RED, infill=1.0)
    for d in DIAS: p.part(f"belt_{d:g}mm", belt_tube(BELTS[d]), "tpu", infill=1.0)

    # ---------------- assembly
    at = lambda m, c: mv(m, 0, float(c[0]), float(c[1]))
    def hubs(c, h=hb): return [place_hub(h, s, float(c[0]), float(c[1])) for s in (-1, 1)]
    def machine(B, with_poker=True, ribs=True):
        h1, c1 = (hb, cap) if ribs else (hb0, hub(False, ribs=False))
        it = [(frame, BLACK), (mark_iv, IVORY), (mark_rd, RED), (at(rA, A0), BLACK), (at(rBm, B), BLACK), (at(rI, I0), BLACK)]
        it += [(m, RED) for m in hubs(A0, h1) + hubs(B, h1)] + [(m, BLACK) for m in hubs(I0, c1)]
        if with_poker: it.append((poker if ribs else poker0, RED))
        return it

    # ---------------- interference checks on the real solids (belt excluded: it is flexible, checked separately)
    vol = lambda a, b: (a ^ b).volume()
    chk = {}
    def pairs(tag, items):
        worst = 0.0; who = ""
        for i in range(len(items)):
            for j in range(i + 1, len(items)):
                if items[i][2] == items[j][2] == "inlayset": continue
                v = vol(items[i][0], items[j][0])
                if v > worst: worst, who = v, f"{items[i][1]} x {items[j][1]}"
        chk[tag] = (round(worst, 4), who)
    def named(B):
        cap0 = hub(False, ribs=False)
        return [(frame, "base", ""), (at(rA, A0), "roller A", ""), (at(rBm, B), "roller B", ""), (at(rI, I0), "capstan", ""), (poker0, "poker", "")] + \
               [(m, "hub A", "") for m in hubs(A0, hb0)] + [(m, "hub B", "") for m in hubs(B, hb0)] + [(m, "cap", "") for m in hubs(I0, cap0)]
    path = LineString(SLOT); n = 13
    for i in range(n):
        q = path.interpolate(i / (n - 1), normalized=True); B = np.array([q.x, q.y])
        tag = "closed" if i == 0 else "open" if i == n - 1 else f"travel {i}/{n - 1}"
        pairs(f"rigid parts, roller B {tag} ({B[0]:.1f}, {B[1]:.1f})", named(B))
    # roller B pushed hard against each end of its slop while closed, and each roller rotated so its flat faces the other
    for dy in (-PIN_CL, PIN_CL):
        pairs(f"closed, B shoved {dy:+.2f} in its seat", named(B_CLOSED + np.array([dy, 0])))
    spun = [(frame, "base", ""), (at(rot(rA, 77, 0, 0), A0), "roller A", ""), (at(rot(rBm, 200, 0, 0), B_CLOSED), "roller B", ""), (at(rot(rI, 131, 0, 0), I0), "capstan", "")]
    spun += [(rot(m, 0, 0, 0), "hub", "") for m in []]
    pairs("closed, rollers turned to odd angles", spun)
    # designed press fits, reported so they are not mistaken for clashes
    chk["DESIGNED crush ribs, one hub in its roller (mm3)"] = (round(vol(place_hub(hb, 1, float(A0[0]), 0), at(rA, A0)), 3), "press fit")
    chk["DESIGNED poker bumps in the plate hole (mm3)"] = (round(vol(poker, frame), 3), "press fit")
    # belt against everything rigid except the three rods it runs on, for every belt, closed full and open
    rigid_closed = U([frame, poker0] + hubs(A0, hb0) + hubs(B_CLOSED, hb0))
    rigid_open = U([frame, poker0] + hubs(A0, hb0) + hubs(B_OPEN, hb0))
    shapes = {}
    for d in DIAS:
        pc, Lc, Pc = belt_path(B_CLOSED, d / 2 + t / 2)
        po, Lo, Po = belt_at(B_OPEN, BELTS[d])
        shapes[d] = (pc, Pc, po, Po)
        chk[f"belt {d:g} closed vs base, poker, hubs"] = (round(vol(belt_solid(pc), rigid_closed), 4), "")
        chk[f"belt {d:g} open vs base, poker, hubs"] = (round(vol(belt_solid(po), rigid_open), 4), "")
    ok = True
    for k, (v, who) in chk.items():
        good = v < 0.01 or k.startswith("DESIGNED"); ok &= good
        print("  check", k, "->", v, "mm3", "OK" if good else "CLASH " + who)
    # clearances worth knowing
    cl = {}
    cl["flange of A to roller B, closed"] = round(C - (r + FLANGE_H) - r, 2)
    cl["hub A to hub B, closed"] = round(C - HUB_D, 2)
    cl["journal in hole or slot, a side"] = PIN_CL
    cl["roller end float, total"] = round(2 * END_GAP, 2)
    cl["paper gap in the nip"] = round(NIP - 2 * t, 2)
    for d in DIAS:
        pc, Pc, po, Po = shapes[d]
        cl[f"belt {d:g}: pocket bottom to return belt on the capstan"] = round((Pc[1] - d / 2 - t) - (ZI + ri + t), 2)
        zs = [q[1] for q in po]; lowtrough = min(z for (y, z) in po if A0[0] + 2 < y < B_OPEN[0] - 2 and z > ZI + ri + t - 0.01) if True else 0
        cl[f"belt {d:g}: open trough depth below the roller tops"] = round(r + t - lowtrough, 1)
        cl[f"belt {d:g}: open trough bottom above the capstan belt"] = round(lowtrough - (ZI + ri + t), 2)
        cl[f"belt {d:g}: slack when open (belt minus taut path)"] = round(BELTS[d] - belt_path(B_OPEN)[1], 1)
    cl["belt lowest point to floor"] = round(ZI - ri - t - ZF, 2)
    cl["roller length vs gap between plates"] = f"{ROLLER_L:.1f} in {2 * XI:.1f}"
    for k, v in cl.items(): print("  clearance", k, "=", v)
    p.checks, p.clear, p.ok = chk, cl, ok

    # ---------------- scenes
    BELT, MIX, PAPER, TIP = "belt", "mix", "paper", "tip"
    pc8, Pc8, po8, Po8 = shapes[DIA_NOM]
    bc, bo = belt_solid(pc8), belt_solid(po8)
    ptaut = belt_path(B_CLOSED)[0]
    closed = machine(B_CLOSED) + [(bc, BELT)]
    opened = machine(B_OPEN) + [(bo, BELT)]
    ytr = (A0[0] + B_OPEN[0]) / 2; ztr = min(z for (y, z) in po8 if abs(y - ytr) < 2 and z > ZI + ri + 1) + t / 2
    TIP_L = 22.0
    load = [(xcyl(3.3, TIP_L, ytr, ztr + 3.3, -PAPER_L / 2 + 1), TIP), (xcyl(3.6, PAPER_L - TIP_L - 3, ytr, ztr + 3.6, -PAPER_L / 2 + 1 + TIP_L + 0.5), MIX)]
    def paper(z_lo, z_hi, lean=16):
        sh = cube(PAPER_L - 2, 0.3, z_hi - z_lo, 0, 0, z_lo); gum = cube(PAPER_L - 2, 0.12, 4.0, 0, -0.2, z_hi - 4.0)
        f = lambda m: mv(rot(m, -lean, 0, 0), 0, 0.0, 0)
        return [(f(sh), PAPER), (f(gum), "gum")]
    loose_paper = [(cube(PAPER_L - 2, PAPER_W, 0.3, 0, Y0 - 12 - PAPER_W / 2, Z0), PAPER), (cube(PAPER_L - 2, 4.0, 0.12, 0, Y0 - 12 - 2.0, Z0 + 0.3), "gum")]
    roll = xcyl(DIA_NOM / 2, PAPER_L - 2, 0, 0, -PAPER_L / 2 + 1)
    p.scene("drumroll", closed)
    p.scene("drumroll_open", opened + load + loose_paper)
    p.scene("drumroll_s1", opened + load)
    p.scene("drumroll_s2", closed)
    p.scene("drumroll_s3", closed)
    p.scene("drumroll_s4", closed + paper(-1.0, PAPER_W - 1.0))
    p.scene("drumroll_s5", closed + paper(-1.0, 7.0))
    p.scene("drumroll_s6", opened + [(mv(roll, 0, ytr, ztr + DIA_NOM / 2 + 14), PAPER), (xcyl(DIA_NOM / 2 + 0.02, TIP_L, ytr, ztr + DIA_NOM / 2 + 14, -PAPER_L / 2 + 0.5), TIP)])
    # exploded: base at the bottom, rods lifted with the belt looped round them, hubs pulled out sideways
    LIFT, OUT_X = 46.0, 22.0
    ex = [(frame, BLACK), (mark_iv, IVORY), (mark_rd, RED)]
    ex += [(mv(at(rA, A0), 0, 0, LIFT), BLACK), (mv(at(rBm, B_OPEN), 0, 0, LIFT), BLACK), (mv(at(rI, I0), 0, 0, LIFT), BLACK), (mv(bo, 0, 0, LIFT), BELT)]
    for c, h, col in ((A0, hb, RED), (B_OPEN, hb, RED), (I0, cap, BLACK)):
        ex += [(mv(place_hub(h, s, float(c[0]), float(c[1])), s * OUT_X, 0, 0), col) for s in (-1, 1)]
    ex.append((mv(poker, 40.0, Y0 - 16 - YP, 0), RED))
    spare = [(mv(rot(belt_tube(BELTS[d]), 0, 90, 0), -BELT_W / 2, Y1 + 30 + i * 0, Z0 + BELTS[d] / (2 * math.pi) + 1), BELT) for i, d in enumerate(DIAS) if d != DIA_NOM][:0]
    p.scene("drumroll_parts", ex)
    p.scene("drumroll_build", ex)
    p.scene("bp_D13", closed); p.scene("bpo_D13", closed)
    # section through the middle, for the belt path picture
    cut = cube(200, 200, 200, -100 - 2, 0, -100)
    sec = lambda items: [(m ^ cut, c) for m, c in items]
    fill = (xcyl(DIA_NOM / 2 - 0.15, PAPER_L - 2, float(Pc8[0]), float(Pc8[1]), -PAPER_L / 2 + 1), MIX)
    p.scene("drumroll_section", sec(closed + [fill]))
    p.scene("drumroll_section_open", sec(opened + load))

    # ---------------- numbers
    bb = lambda items: (lambda v: v.max(0) - v.min(0))(np.vstack([tm(m).bounds for m, _ in items]))
    INFO.update(size_closed=[round(float(x), 1) for x in bb(closed)], size_open=[round(float(x), 1) for x in bb(opened)],
                belts={f"{d:g}": round(L, 1) for d, L in BELTS.items()}, belt_w=round(BELT_W, 1), roller_l=round(ROLLER_L, 1),
                pocket8=[round(float(x), 2) for x in Pc8], trough=[round(ytr, 2), round(ztr, 2)], ZI=round(ZI, 2), ZF=round(ZF, 2), Z0=round(Z0, 2), Z1=round(Z1, 2), Y0=round(Y0, 2), Y1=round(Y1, 2),
                XO=round(XO, 2), taut_closed=round(belt_path(B_CLOSED)[1], 1), taut_open=round(belt_path(B_OPEN)[1], 1), YP=round(YP, 2), ZP=round(ZP, 2),
                A=[float(A0[0]), 0.0], Bc=[float(B_CLOSED[0]), 0.0], Bo=[float(B_OPEN[0]), float(B_OPEN[1])])
    p.note = (f"{INFO['size_closed'][0]:g} x {INFO['size_closed'][1]:g} x {INFO['size_closed'][2]:g} mm. Takes papers up to {PAPER_L:g} mm long. "
              f"Belt (apron) runs round roller A (front, fixed, flanged), roller B (rear, slides {TRAVEL:g} mm back in a J slot and drops {SEAT:g} mm into a seat to lock shut) "
              f"and a capstan under the pocket that keeps the return belt off the roll. Rollers {ROLL_D:g} mm, {NIP:g} mm apart when closed. "
              f"Belts: " + ", ".join(f"{d:g} mm roll = {L:.1f} mm loop" for d, L in BELTS.items()) + f", {BELT_W:g} wide, {BELT_T:g} wall. "
              "BELTS ARE TPU 95A: feed from the external spool (not the AMS Lite), one wall 0.45 mm, no top or bottom layers, or spiral vase one at a time, 25 mm/s. "
              "Start with the 8 mm belt. Base prints as is with the lockup inlaid under the floor. The three rods print lying on their flats, 4 walls. "
              "Hubs, caps print face down, pin up. No supports anywhere. Build: loop the belt round the three rods, lower them between the end plates, "
              "push a black cap into each end of the capstan (bottom), a red hub into each end of roller A (front hole) and roller B (slot). Poker slides in through the square hole.")
    P["D13"] = p

# ------------------------------------------------------------------ pictures
SHOTS5 = {
 "drumroll": dict(az=-34, el=24, zoom=1.0), "drumroll_open": dict(az=-30, el=46, zoom=1.0), "drumroll_parts": dict(az=-36, el=26, zoom=1.0),
 "drumroll_build": dict(az=-36, el=26, zoom=1.0), "drumroll_section": dict(az=-78, el=10, zoom=1.0), "drumroll_section_open": dict(az=-78, el=10, zoom=1.0),
 "drumroll_s1": dict(az=-30, el=46, zoom=1.0), "drumroll_s2": dict(az=-34, el=24, zoom=1.0), "drumroll_s3": dict(az=-34, el=24, zoom=1.0),
 "drumroll_s4": dict(az=-40, el=22, zoom=1.0), "drumroll_s5": dict(az=-34, el=30, zoom=1.0), "drumroll_s6": dict(az=-34, el=30, zoom=1.0),
}
COL5 = {"belt": (0.06, 0.06, 0.065, 0.42), "mix": (0.33, 0.27, 0.17, 0.95), "paper": (0.74, 0.72, 0.66, 0.8), "tip": (0.80, 0.70, 0.52, 0.8), "gum": (0.78, 0.74, 0.64, 0.25), "tpu": (0.06, 0.06, 0.065, 0.42)}
def _inject():
    import render, blueprint
    render.SHOTS.update(SHOTS5); render.COL.update(COL5)
    blueprint.SHEETS["D13"] = dict(piece="DRUMROLL ROLLING MACHINE", parts="BASE, 3 RODS, 6 HUBS, 3 BELTS, POKER",
                                   cap=f"ISOMETRIC  CLOSED.  ROLLERS {ROLL_D:g}, NIP {NIP:g}, BELT {BELT_W:g} WIDE.  VIEWS: CLOSED", iso=dict(az=-34, el=24))
    blueprint.FILL.update(belt=(44, 42, 40), tpu=(44, 42, 40))
    return render, blueprint
def turn(x, c, rad, a0=35, a1=165, n=14):
    """Arc in the (y, z) plane round an axis at c: a0 to a1 degrees, 90 = top, 180 = the front (toward you)."""
    return [(x, c[0] + rad * math.cos(math.radians(a0 + (a1 - a0) * i / n)), c[1] + rad * math.sin(math.radians(a0 + (a1 - a0) * i / n))) for i in range(n + 1)]

def guides():
    from annotate import annotate
    _inject(); info = json.load(open(f"{OUT}/drumroll_info.json"))
    A, Bc, Bo = info["A"], info["Bc"], info["Bo"]; xo = info["XO"]; xl = -xo - 3.0
    tr = info["trough"]; L = 46.0
    G = {}
    G["drumroll_build"] = dict(banner="Drumroll: how it goes together", labels=[
        dict(text="Belt", sub="loop it round all three rods first", tag="A", at=(10, (A[0] + Bo[0]) / 2, L + 6), to=(120, -150)),
        dict(text="Roller A", sub="flanged, front hole", tag="B", at=(-30, A[0], L + 5), to=(-250, -60)),
        dict(text="Roller B", sub="plain, goes in the slot", tag="C", at=(30, Bo[0], L + 5), to=(170, -85)),
        dict(text="Capstan", sub="thin rod, bottom hole", tag="D", at=(52, 0, L + info["ZI"] - 4), to=(200, 30)),
        dict(text="Base", sub="slot = back", tag="E", at=(-20, info["Y0"], info["Z0"] + 5), to=(-220, 110)),
        dict(text="Red hubs x4", sub="rollers A and B", tag="F", at=(xl - 22, A[0], 0), to=(-150, -170)),
        dict(text="Black caps x2", sub="capstan", tag="G", at=(xl - 22, 0, info["ZI"]), to=(-170, 60)),
        dict(text="Poker", sub="slides into the square hole", tag="H", at=(60, info["Y0"] - 16, info["ZF"] + 2), to=(60, 150)),
    ], arrows=[
        dict(pts=[(-44, 3, L - 26), (-44, 3, L - 46)], step=1),
        dict(pts=[(xl - 16, 0, info["ZI"]), (xl - 2, 0, info["ZI"])], step=2),
        dict(pts=[(xl - 16, A[0], 0), (xl - 2, A[0], 0)], step=3),
        dict(pts=[(xl - 16, Bo[0], Bo[1]), (xl - 2, Bo[0], Bo[1])], step=4),
    ])
    rot2 = lambda c, rad=12.0: [dict(pts=turn(x, c, rad), kind="turn") for x in (-30.0, 30.0)]
    G["drumroll_s1"] = dict(banner="1  Open it and load the trough", labels=[
        dict(text="Roller B", sub="lift and slide it back", tag="C", at=(40, Bo[0], Bo[1] + 5.4), to=(140, -120)),
        dict(text="Filter tip", sub="at one end", tag="1", at=(-44, tr[0], tr[1] + 6), to=(-190, -110)),
        dict(text="Your mix", sub="spread it evenly", tag="2", at=(5, tr[0], tr[1] + 7), to=(-20, -170)),
        dict(text="Roller A", sub="stays put", tag="B", at=(-20, A[0], 5.4), to=(-170, 130)),
    ], arrows=[dict(pts=[(56, Bc[0], 12), (56, Bo[0] + 3, 12)], step=1, text="back", text_off=(10, -44))])
    G["drumroll_s2"] = dict(banner="2  Close it: slide forward until it drops", labels=[
        dict(text="Roller B", sub="drops into its seat and stays", tag="C", at=(30, Bc[0], 5.4), to=(150, -120)),
        dict(text="Red hub", sub="rides the slot, sits at the front end", tag="F", at=(xl, Bc[0], 0), to=(-170, -150)),
    ], arrows=[dict(pts=[(56, Bo[0] + 6, 13), (56, Bc[0] + 1, 13), (56, Bc[0] + 1, 7)], step=2, text="forward, then down", text_off=(14, -50))])
    G["drumroll_s3"] = dict(banner="3  Roll both toward you to tamp", labels=[
        dict(text="Thumbs on both rollers", sub="one full turn toward you", tag="", at=(0, Bc[0], 5.4), to=(60, -190)),
        dict(text="Hubs turn with the rollers", tag="F", at=(xl, A[0], 0), to=(-150, 150)),
    ], arrows=rot2(((A[0] + Bc[0]) / 2, 0), 13.0) + [dict(pts=turn(xl - 0.5, A, 8.5, 20, 200), kind="turn", text="toward you", text_off=(-150, -40))])
    G["drumroll_s4"] = dict(banner="4  Feed the paper, gum strip last and facing you", labels=[
        dict(text="Paper", sub="drops into the gap between the rollers", tag="P", at=(20, 8, 24), to=(150, -60)),
        dict(text="Gum strip", sub="top edge, on the side facing you", tag="G", at=(-20, 10.4, 38), to=(-210, -30)),
    ], arrows=[dict(pts=[(-40, 9, 30), (-40, 4, 12)], step=4)] + [dict(pts=turn(40.0, ((A[0] + Bc[0]) / 2, 0), 13.0), kind="turn", text="toward you", text_off=(20, 10))])
    G["drumroll_s5"] = dict(banner="5  Roll until only the gum shows, wet it, roll through", labels=[
        dict(text="Gum strip", sub="wet it, then keep rolling", tag="G", at=(0, 1.5, 5.5), to=(40, -180)),
    ], arrows=rot2(((A[0] + Bc[0]) / 2, 0), 13.0) + [dict(pts=turn(xl - 0.5, A, 8.5, 20, 200), kind="turn", text="toward you", text_off=(-150, -40))])
    G["drumroll_s6"] = dict(banner="6  Open and lift it out", labels=[
        dict(text="Done", sub="tip at one end", tag="", at=(0, tr[0], tr[1] + 22), to=(150, -80)),
        dict(text="Roller B", sub="lift and slide back", tag="C", at=(40, Bo[0], Bo[1] + 5.4), to=(170, 60)),
    ], arrows=[dict(pts=[(-20, tr[0], tr[1] + 4), (-20, tr[0], tr[1] + 13)], step=6), dict(pts=[(56, Bc[0], 12), (56, Bo[0] + 3, 12)], step=5)])
    out = {}
    for n, g in G.items():
        out[n] = annotate(n, g.get("labels", ()), g.get("arrows", ()), banner=g.get("banner"))
    # how it works picture, drawn on the hero render
    out["use"] = annotate("drumroll", labels=[
        dict(text="Roller B", sub="slides back to open", tag="C", at=(30, Bc[0], 5.4), to=(170, -130)),
        dict(text="Roller A", sub="fixed", tag="B", at=(0, A[0], 5.4), to=(-60, 190)),
        dict(text="Reel hubs", sub="turn as you roll", tag="F", at=(xl, Bc[0], 0), to=(-160, -150)),
        dict(text="Poker", sub="pull it out by the red head", tag="H", at=(xo + 2, info["YP"], info["ZP"]), to=(100, 150)),
    ], arrows=rot2(((A[0] + Bc[0]) / 2, 0), 13.0) + [dict(pts=turn(xl - 0.5, A, 8.5, 20, 200), kind="turn", text="roll toward you", text_off=(-190, -40))],
        banner="Drumroll: both rollers turn toward you", out=f"{OUT}/r/drumroll_use")
    for k, v in out.items(): print(k, v)

if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "build"
    if mode == "render":
        render, _ = _inject()
        for s in (sys.argv[2].split(",") if len(sys.argv) > 2 and not sys.argv[2].startswith("--") else list(SHOTS5)): render.render(s, "--draft" in sys.argv)
    elif mode == "guides": guides()
    elif mode == "blueprint":
        _, blueprint = _inject(); blueprint.sheet("D13")
    else:
        build_drumroll()
        rep = {}
        for k, p in P.items():
            rep[k] = p.export(); print(k, p.name, rep[k]["grams"], "g")
            for x in rep[k]["parts"]: print("  ", x["file"], x["size"], x["grams"])
            by = {}
            for x in rep[k]["parts"]: by[x["colour"]] = round(by.get(x["colour"], 0) + x["grams"], 1)
            PLATES = 3                                     # black (with the inlay), red, TPU
            INFO.update(grams=by, grams_total=rep[k]["grams"], plates=PLATES, hours=round(hours(rep[k]["grams"], PLATES, 1), 1),
                        checks={a: b[0] for a, b in p.checks.items()}, clearances=p.clear, all_clear=bool(p.ok))
            print("  by material", by, "hours", INFO["hours"], "closed", INFO["size_closed"], "open", INFO["size_open"])
            print("  belts", INFO["belts"], "taut closed", INFO["taut_closed"], "taut open", INFO["taut_open"])
        old = {}
        try: old = json.load(open(f"{OUT}/report.json"))
        except Exception: pass
        old.update(rep); os.makedirs(OUT, exist_ok=True); json.dump(old, open(f"{OUT}/report.json", "w"), indent=1)
        json.dump(INFO, open(f"{OUT}/drumroll_info.json", "w"), indent=1)
