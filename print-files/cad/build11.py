"""Range V3 (24 Nov 2026): D18 Ripple key tray, D19 Key rail with plug-ins, G1 Patched In keychains.
All PLA, all print with no supports, logo mark debossed on the underside or back.
Usage: python3 build11.py            (optional NS_NAME_A / NS_NAME_B for the keychain names, NS_TRAY for the tray name)"""
import math, json, os
from ns import *
from ns import _cs
from build2 import logo
R = math.radians

def under_logo(x, y, s=0.75):
    return ext(affinity.scale(logo(x, y, s), -1, 1, origin=(x, y)), 0.6, -0.01)

# ================================================================== D18 Ripple key tray
TW, TD, TH, TR = 170.0, 95.0, 18.0, 14.0      # outside size and corner radius
WALL, FLOOR, LIPW = 4.0, 3.2, 12.0            # side walls, floor, wide flat front lip for the name

def tray_shell(name=None):
    outer = rrect(TW, TD, TR)
    inner = rrect(TW - 2 * WALL, TD - WALL - LIPW, TR - WALL, 0, (LIPW - WALL) / 2)   # pocket pushed back: front lip is wider
    shell = body(outer, TH, c=0.6, bottom=True) - ext(fillet(inner, 3.0), TH, FLOOR)
    # ripples: rounded-rect grooves spreading from a centre dot, 1.2 mm wide, 0.7 mm deep, 4 mm apart
    cx, cy = 0.0, (LIPW - WALL) / 2
    pocket = inner.buffer(-2.5)
    rings = []
    for k in range(1, 12):
        r = 6.0 + 4.0 * k
        o = rrect(2 * r + 40, 2 * r, r - 0.01, cx, cy)
        rings.append(o.difference(o.buffer(-1.2)))
    grooves = unary_union(rings).intersection(pocket)
    shell = shell - ext(grooves, 0.71, FLOOR - 0.7)
    # press-in red dot socket at the centre: 8.3 mm, 2 mm deep (dot is 8.0 mm, 0.15 mm a side)
    shell = shell - cyl(4.15, 2.01, FLOOR - 2.0, cx, cy, seg=64)
    # underside: logo, four 12 mm felt pads in 0.8 mm recesses
    shell = shell - under_logo(0.0, 10.0) - U([cyl(6.0, 0.8, -0.01, x, y) for x in (-68, 68) for y in (-30, 30)])
    if name:
        shell = shell - ext(fit_text(name, 6.0, 120, 0, -TD / 2 + LIPW / 2 + 0.6), 0.6, TH - 0.6)
    return shell

def build_ripple():
    p = Product("D18", "ripple", "Ripple")
    name = os.environ.get("NS_TRAY", "MEERA")
    plain = tray_shell(); named = tray_shell(name)
    dot = body(circle(4.0, seg=64), 2.6, c=0.4, steps=2)       # sits 0.6 mm proud of the floor
    cy = (LIPW - WALL) / 2
    p.part("tray", plain, IVORY, infill=0.15)
    p.part("dot", dot, RED, infill=1.0)
    dot_in = mv(dot, 0, cy, FLOOR - 2.0)
    keys = [(mv(rot(U([cyl(11, 2.2, 0), cube(48, 7, 2.2, 32, 0, 0)]), 0, 0, 25), -35, 10, FLOOR + 0.4), "brass"),
            (mv(rot(U([cyl(12, 2.2, 0), cube(50, 7, 2.2, 34, 0, 0)]), 0, 0, -160), 55, 12, FLOOR + 0.4), "steel")]
    p.scene("ripple", [(named, IVORY), (dot_in, RED)] + keys)
    p.scene("ripple_top", [(named, IVORY), (dot_in, RED)])
    p.scene("ripple_black", [(named, BLACK), (dot_in, RED)] + keys)
    p.scene("ripple_black_top", [(named, BLACK), (dot_in, RED)])
    p.scene("bp_D18", [(named, IVORY), (dot_in, RED)]); p.scene("bpo_D18", [(plain, IVORY), (dot_in, RED)])
    g = grams(plain, 0.15) + grams(dot, 1.0)
    p.note = (f"D18 Ripple. {TW:g} x {TD:g} x {TH:g} mm, matte ivory, prints flat as it sits, no supports. "
              f"Ripple grooves 1.2 mm wide, 0.7 deep, 4 mm apart, from a red press-in dot (8 mm, 0.15 mm a side). "
              f"{LIPW:g} mm front lip takes a name, up to 12 letters at 6 mm, 0.6 deep (engrave per order). Felt pads x4 and logo underneath. "
              f"Estimate {g:.0f} g.")
    return p, g

# ================================================================== D19 Key rail and plug-ins
# Wall coordinates: x along the wall, z up the wall, the rail's front face at y = 0, wall behind at y = RT.
RL, RHt, RT = 200.0, 36.0, 10.0
SLOTS = (-80.0, -40.0, 0.0, 40.0, 80.0)
NECK, DEPTH, CLR = 8.0, 2.8, 0.25
TIP = NECK + 2 * DEPTH            # tenon; the slot adds CLR a side and 0.2 mm depth
STOP = 4.0                                              # slots are open at the top, closed 4 mm above the bottom edge

def trap(neck, tip, d, x0=0.0):
    """Dovetail section in the x-y plane: neck at y = 0, tip at y = d (into the rail). Flanks at 45 degrees (tip = neck + 2d), so
    the slot prints face up and the tenon prints on its side, both with no support."""
    return Polygon([(x0 - neck / 2, 0), (x0 + neck / 2, 0), (x0 + tip / 2, d), (x0 - tip / 2, d)])

def prism_z(poly, z0, z1):
    return mv(ext(poly, z1 - z0), 0, 0, z0)

def build_keyrail():
    p = Product("D19", "keyrail", "Key rail")
    # rail as a plan shape in x-y, extruded up the wall (z)
    rail = mv(ext(rrect(RL, RT, 3.0, 0, RT / 2), RHt), 0, 0, -RHt / 2)
    edge = U([mv(ext(rrect(RL - 1.2, RT - 1.2, 2.4, 0, RT / 2), RHt + 0.01), 0, 0, -RHt / 2)])
    rail = rail ^ U([edge, mv(ext(rrect(RL, RT, 3.0, 0, RT / 2), RHt - 1.2), 0, 0, -RHt / 2 + 0.6)])   # softened top and bottom
    slots = U([prism_z(trap(NECK + 2 * CLR, TIP + 2 * CLR + 0.4, DEPTH + 0.2, x).buffer(0.01), -RHt / 2 + STOP, RHt / 2 + 1) for x in SLOTS])
    # lead-in chamfer at each slot mouth so plug-ins find the slot from above
    lead = U([mv(rot(cyl(TIP / 2 + 1.2, 2.0, 0, r2=TIP / 2, seg=4), 0, 0, 45), x, 1.2, RHt / 2 - 2.0) for x in SLOTS])
    holes = U([mv(rot(U([cyl(2.2, RT + 1, -0.5), cyl(4.4, 2.21, -0.01, r2=2.2)]), -90, 0, 0), x, -0.0, 0) for x in (-60.0, 60.0)])
    rail = rail - slots - (lead ^ mv(ext(box(-RL, -1, RL, 3.0), RHt), 0, 0, -RHt / 2)) - holes
    # logo on the back face (against the wall), reads from behind
    back = mv(rot(ext(affinity.scale(logo(30, 0, 0.75), -1, 1, origin=(30, 0)), 0.61), -90, 0, 0), 0, RT + 0.01, 0)
    rail = rail - back
    # red line: a 2 mm flush strip along the top edge of the front face, printed as the top layers when the rail lies face up
    # (kept simple: the hooks carry the red, the rail stays one colour)
    tenon = lambda z0, z1: prism_z(trap(NECK, TIP, DEPTH), z0, z1)

    def plate(w, z0, z1):
        return mv(ext(rrect(w, 4.0, 1.2, 0, -2.0), z1 - z0), 0, 0, z0)

    # 1. jack-plug key hook: a plug lying out from the plate, tip turned up so keys stay on
    def jack_hook():
        z0 = -RHt / 2 + STOP + 0.4                      # sits on the slot stop
        pl = plate(14.0, z0 - 2.0, z0 + 30.0)
        # side profile (y out from the wall is negative, z up): sleeve, two ring grooves, neck, then the tip turned up
        prof = Polygon([(0, 0), (-8, 0), (-8.6, -0.6), (-9.4, -0.6), (-10, 0), (-12, 0), (-12.6, -0.6), (-13.4, -0.6), (-14, 0),
                        (-16, 0), (-16, -1.2), (-24, -1.2), (-24, 4.5), (-27.5, 4.5), (-27.5, -3.5), (-25, -7), (-16, -7), (-16, -6),
                        (-14, -6), (-13.4, -6.6), (-12.6, -6.6), (-12, -6), (-10, -6), (-9.4, -6.6), (-8.6, -6.6), (-8, -6), (0, -6), (0, -9)])
        prof = fillet(prof, 0.5)
        hook = mv(rot(ext(affinity.translate(prof, -4, 0), 14.0), 90, 0, 90), -7.0, 0, 0)   # profile in y-z, full plate width
        hook = mv(hook, 0, 0, z0 + 16.0)
        return U([pl, hook, tenon(z0, z0 + 26.0)])
    # 2. wide hook for a bag or headphones
    def wide_hook():
        z0 = -RHt / 2 + STOP + 0.4
        pl = plate(30.0, z0 - 2.0, z0 + 34.0)
        prof = fillet(Polygon([(0, 0), (-38, 0), (-38, 12), (-32, 12), (-32, 6), (0, 6)]), 1.5)
        hook = mv(rot(ext(prof, 30.0), 90, 0, 90), -15.0, -4.0 + 0.01, 0)
        hook = mv(hook, 0, 0, z0 - 2.0)
        return U([pl, hook, tenon(z0, z0 + 30.0)])
    # 3. ledge: 70 x 50 shelf with a 6 mm lip, two gussets, for sunglasses, wallet, earbuds
    def ledge():
        z0 = -RHt / 2 + STOP + 0.4
        pl = plate(70.0, z0 - 2.0, z0 + 34.0)
        # shelf with a 6 mm lip and a 45 degree brace under it, all in one profile across the full width
        prof = fillet(Polygon([(0, 14), (-16, 30), (-50, 30), (-50, 38), (-46, 38), (-46, 34), (0, 34)]), 0.8)
        shelf = mv(rot(ext(prof, 70.0), 90, 0, 90), -35.0, -4.0 + 0.01, z0 - 2.0)
        # two tenons, so the ledge spans two slots (40 mm apart) and sits on the rail without blocking a neighbour
        two = U([prism_z(trap(NECK, TIP, DEPTH, x), z0, z0 + 30.0) for x in (-20.0, 20.0)])
        return U([pl, shelf, two])
    jh, wh = jack_hook(), wide_hook()
    lg = ledge()
    # print orientations: rail face up; plug-ins on their side (width along z), so the dovetail and hooks need no support
    rail_p = rot(rail, -90, 0, 0)
    side = lambda m: rot(m, 0, 90, 0)
    p.part("rail", rail_p, BLACK, infill=0.25)
    p.part("key_hook", side(jh), RED, qty=3, infill=0.4)
    p.part("wide_hook", side(wh), RED, infill=0.4)
    p.part("ledge", side(lg), BLACK, infill=0.2)
    # wall scenes: wall coordinates are already the display orientation (front = -y, up = z); lift the rail to eye level
    lift = lambda m: mv(m, 0, 0, 120)
    wall = mv(cube(420, 6, 300, 0, RT + 3, 0), 0, 0, 0)
    keys = [(lift(mv(U([cyl(10, 2.0, -1.0), cube(46, 6, 2.0, 0, 0, -1.0)]) , 0, 0, 0)), "brass")]
    def key_on(x, col):
        k = U([mv(rot(ring_m(9.0, 7.6, 2.0), 90, 0, 0), 0, 0, 0), mv(rot(U([cyl(8, 2.0, -1.0), cube(6, 2.0, 40, 0, 0, -48)]), 90, 0, 0), 0, 0, -14)])
        return (lift(mv(k, x, -21.0, -RHt / 2 + STOP + 10.0 + 2.0)), col)
    items = [(lift(rail), BLACK), (lift(mv(jh, -80, 0, 0)), RED), (lift(mv(jh, -40, 0, 0)), RED), (lift(mv(wh, 0, 0, 0)), RED)]
    ledge_items = [(lift(mv(lg, 60, 0, 0)), BLACK)]          # ledge takes the 40 and 80 slots
    p.scene("keyrail", items + ledge_items + [key_on(-80, "brass"), key_on(-40, "steel"), (wall, "prop2")])
    p.scene("keyrail_bare", [(rail, BLACK)])
    loose = [(rail, BLACK), (mv(jh, -80, 0, 34), RED), (mv(wh, 0, 0, 34), RED), (mv(lg, 60, -0, 34), BLACK)]
    p.scene("keyrail_build", loose)
    p.scene("bp_D19", loose); p.scene("bpo_D19", items + ledge_items)
    g_rail = grams(rail, 0.25); g_jh = grams(jh, 0.4); g_wh = grams(wh, 0.4); g_lg = grams(lg, 0.2)
    p.note = (f"D19 Key rail. Rail {RL:g} x {RHt:g} x {RT:g} mm, five dovetail slots on a 40 mm pitch (open at the top, closed {STOP:g} mm "
              f"above the bottom), two countersunk 4 mm screw holes 120 mm apart or 3M strips, logo on the back. Plug-ins slide down from the top: "
              f"jack-plug key hook, wide hook (bags, headphones), ledge 70 x 50 with a 6 mm lip (black, two tenons, takes two slots). Rail prints face up; plug-ins print on their side. No supports. "
              f"Estimates: rail {g_rail:.0f} g, key hook {g_jh:.0f} g, wide hook {g_wh:.0f} g, ledge {g_lg:.0f} g.")
    return p, dict(rail=g_rail, key_hook=g_jh, wide_hook=g_wh, ledge=g_lg)

def ring_m(ro, ri, h):
    return cyl(ro, h, -h / 2, seg=48) - cyl(ri, h + 1, -h / 2 - 0.5, seg=48)

# ================================================================== G1 Patched In keychains
KW, KT, KB = 14.0, 10.0, 40.0            # barrel section 14 x 10, barrel length
PIN_R, COLLAR = 3.0, 3.0

def barrel(name, front_logo=False):
    sec = rrect(KW, KT, 3.0)
    b = body(sec, KB, c=0.6, bottom=True)
    # keyring hole through the thickness, 4 mm, near the bottom end
    b = b - mv(rot(cyl(2.0, KT + 2, -KT / 2 - 1, seg=32), 90, 0, 0), 0, 0, 5.5)
    # name debossed on the front (-y) face, running up the barrel, 5 mm caps (never under 4)
    t = fit_text(name, 5.0, KB - 13.0, 0, 0)
    t = affinity.rotate(t, 90, origin=(0, 0))
    tm_ = mv(rot(ext(t, 0.61), 90, 0, 0), 0, -KT / 2 + 0.6, 11.0 + (KB - 13.0) / 2)
    # logo on the back (+y) face
    lg = mv(rot(ext(affinity.rotate(affinity.scale(logo(0, 0, 0.55), -1, 1), 90, origin=(0, 0)), 0.61), -90, 0, 0), 0, KT / 2 - 0.6, KB - 12.0)
    return b - tm_ - lg

def build_patched():
    p = Product("G1", "patched_in", "Patched In")
    na = os.environ.get("NS_NAME_A", "AARAV"); nb = os.environ.get("NS_NAME_B", "MEERA")
    # plug: barrel, red collar (colour change at one height), pin with a groove and a rounded tip
    plug_b = barrel(na)
    collar = cyl(4.6, COLLAR, KB, seg=64)
    pin = U([cyl(PIN_R, 12.0, KB + COLLAR - 0.01, seg=48), cyl(PIN_R, 1.6, KB + COLLAR + 11.99, r2=1.4, seg=48)])
    groove = cyl(PIN_R + 1, 0.9, KB + COLLAR + 6.6, seg=48) - cyl(PIN_R - 0.45, 1.0, KB + COLLAR + 6.55, seg=48)
    pin = pin - groove
    plug = U([plug_b, collar, pin])
    red_band = cube(40, 40, COLLAR, 0, 0, KB)
    plug_body, plug_red = plug - red_band, plug ^ red_band
    # socket: barrel with a bore from the top, split into two jaws by a 1.2 mm slit so the plug clicks past a 0.35 mm ridge
    sock = barrel(nb)
    BORE = 14.6
    sock = sock - cyl(PIN_R + 0.25, BORE + 0.01, KB - BORE, seg=48) - cyl(PIN_R + 0.25, 1.5, KB - 1.49, r2=PIN_R + 1.0, seg=48)
    sock = sock - cube(KW + 2, 1.2, 10.0, 0, 0, KB - 10.0)
    ridge_z = KB - 6.6 - 0.9 / 2
    ridge = (cyl(PIN_R + 0.3, 0.9, ridge_z - 0.45, seg=48) - cyl(PIN_R - 0.1, 0.9, ridge_z - 0.45, r2=PIN_R - 0.1, seg=48))
    ridge = U([cyl(PIN_R + 0.3, 0.5, ridge_z - 0.25, seg=48), cyl(PIN_R + 0.3, 0.35, ridge_z - 0.6, r2=PIN_R + 0.3, seg=48)]) - U([
        cyl(PIN_R - 0.1, 0.5, ridge_z - 0.25, seg=48), cyl(PIN_R + 0.25, 0.35, ridge_z - 0.6, r2=PIN_R - 0.1, seg=48), cyl(PIN_R - 0.1, 0.35, ridge_z + 0.25, r2=PIN_R + 0.25, seg=48)])
    sock = U([sock, ridge - cube(KW + 2, 1.2, 10.0, 0, 0, KB - 10.0)])
    p.part("plug", plug_body, BLACK, infill=0.3)
    p.part("plug_collar", plug_red, RED, infill=1.0, on="plug")
    p.part("socket", sock, IVORY, infill=0.3)
    ringA = mv(rot(ring_m(12.0, 10.6, 1.6), 0, 0, 0), 0, 0, 0)
    def ring_at(x):
        return (mv(rot(ring_m(12.0, 10.6, 1.6), 90, 0, 0), x, 0, 5.5 - 12.0 + 2.0), "steel")
    pair_apart = [(mv(plug_body, -14, 0, 0), BLACK), (mv(plug_red, -14, 0, 0), RED), (mv(sock, 14, 0, 0), IVORY)]
    clicked = [(mv(rot(plug_body, 0, 180, 0), 0, 0, 2 * KB + COLLAR + 0.0), BLACK), (mv(rot(plug_red, 0, 180, 0), 0, 0, 2 * KB + COLLAR), RED), (sock, IVORY)]
    lay = lambda items, x=0, y=0: [(mv(rot(m, 0, 90, 0), x, y, KT / 2 + 2.0), c) for m, c in items]
    p.scene("patched", lay([(plug_body, BLACK), (plug_red, RED)], -10, -12) + lay([(sock, IVORY)], -10, 14))
    p.scene("patched_clicked", [(mv(rot(m, 0, 90, 0), -40, 0, KW / 2), c) for m, c in clicked])
    p.scene("patched_upright", pair_apart)
    p.scene("bp_G1", pair_apart); p.scene("bpo_G1", pair_apart)
    g = grams(plug_body, 0.3) + grams(plug_red, 1.0) + grams(sock, 0.3)
    p.note = (f"G1 Patched In. Plug {KW:g} x {KT:g} x {KB + COLLAR + 13.6:.0f} mm and socket {KW:g} x {KT:g} x {KB:g} mm, both print upright, no supports. "
              f"Plug black with a red {COLLAR:g} mm collar (one colour change and back); socket ivory, its top split into two jaws that click over the pin groove. "
              f"Name on the front face, up to 8 letters at 5 mm (never under 4), logo on the back, 4 mm keyring hole. Metal rings bought in. Estimate {g:.0f} g a pair.")
    return p, g

if __name__ == "__main__":
    out = {}
    for f in (build_ripple, build_keyrail, build_patched):
        p, g = f()
        rep = p.export(); out[p.id] = rep; print(json.dumps(rep, indent=1)); print(p.id, "grams", g)
    print("TEXT", TEXT_LOG)
