"""No Skips: Crate, the DJ USB keeper (B6).
Run: python3 build4.py            (NS_OUT=<dir> sets the output folder)
Axes: x across the four slots, y front (-) to back (+), z up. Slots open at the top, sticks stand connector down.
Parts: shell (black, prints upright), spine (red, prints back face down), hood (black, prints front face down),
hood inlays (ivory and red, flush), four role tags with black word inlays (ivory), fit shims (red).
"""
import math, json, sys, os
from ns import *
from ns import _cs

R = math.radians
CX = [-36.3, -12.1, 12.1, 36.3]          # slot centres, pitch 24.2
W, D, H = 102.0, 18.0, 49.0               # shell outer
SLOT_W, CH_Y0, CH_Y1 = 22.6, -7.4, 6.0   # channel clear width and its y span (13.4 deep)
POCKET_W, POCKET_Y0, POCKET_Y1 = 14.5, -3.6, 2.2
SHOULDER = 13.0
FLOOR = 1.2
WIN_W, WIN_Z0, WIN_Z1 = 9.5, 2.0, 11.0
ENDT = 3.4
def xz(poly, depth, y0=0.0):
    """Profile in (x, z) extruded along +y from y0, readable from the front (-y)."""
    return mv(rot(Manifold.extrude(_cs(poly), depth), 90, 0, 0), 0, y0 + depth, 0)
def logo(cx, cy, s=1.0):
    ch = lambda x: Polygon([(x, 0), (x + 4 * s, 4 * s), (x, 8 * s), (x + 2.2 * s, 8 * s), (x + 6.2 * s, 4 * s), (x + 2.2 * s, 0)])
    chev = unary_union([ch(0), ch(4.6 * s)]); bar = box(11.6 * s, 0, 13.6 * s, 8 * s)
    return affinity.translate(chev, cx - 6.8 * s, cy - 4 * s), affinity.translate(bar, cx - 6.8 * s, cy - 4 * s)

def build_shell():
    parts = [cube(W, D, FLOOR, 0, 0, 0)]
    for s in (-1, 1): parts.append(cube(ENDT, D, H, s * (W / 2 - ENDT / 2), 0, 0))
    for x in (-24.2, 0.0, 24.2): parts.append(cube(1.6, CH_Y1 - CH_Y0, H, x, (CH_Y0 + CH_Y1) / 2, 0))
    parts.append(cube(W, 1.6, H, 0, -8.2, 0))                       # front wall, y -9 .. -7.4
    parts.append(cube(W, 3.8, SHOULDER, 0, -5.5, 0))                # front pocket block, y -7.4 .. -3.6
    for c in CX:
        for s in (-1, 1): parts.append(cube((SLOT_W - POCKET_W) / 2, POCKET_Y1 - POCKET_Y0, SHOULDER, c + s * (SLOT_W / 4 + POCKET_W / 4), (POCKET_Y0 + POCKET_Y1) / 2, 0))
        for s in (-1, 1): parts.append(cube(1.2, 0.6, 33, c + s * 6, CH_Y0 + 0.3 - 0.05, 14))   # crush ribs on the front wall
    for s in (-1, 1): parts.append(Manifold.sphere(0.7, 24).translate((s * W / 2, 0, 47.5)))      # hood detent bumps
    sh = U(parts)
    cuts = []
    for c in CX:
        cuts.append(cube(WIN_W, 6.2, WIN_Z1 - WIN_Z0, c, -6.2, WIN_Z0))                        # window through wall and block
        cuts.append(cube(21.8, 1.0, 10.4, c, -9 + 0.45, 14))                                     # tag recess, 0.9 deep
    for s in (-1, 1): cuts.append(cube(1.8, 1.7, H - FLOOR + 0.5, s * 48.5, 6.75, FLOOR))        # spine flange grooves in the end walls
    sh = sh - U(cuts)
    # raised numerals on the front, readable by touch
    nums = U([ext(text(str(i + 1), 4.4, c, 36), 0.5) for i, c in enumerate(CX)])               # extruded in z, stood up below
    nums = mv(rot(nums, 90, 0, 0), 0, 0, 0)
    num_parts = []
    for i, c in enumerate(CX):
        num_parts.append(xz(text(str(i + 1), 4.6, c, 36), 0.5, -9.0 - 0.5 + 0.02))
    return U([sh] + num_parts)

def build_spine():
    sp = [cube(94.8, 1.5, H - FLOOR, 0, 8.25, FLOOR), cube(98.5, 1.5, H - FLOOR, 0, 6.75, FLOOR)]
    for c in CX: sp.append(cube(22.3, 3.8, SHOULDER - FLOOR, c, 4.1, FLOOR))                   # red foot: back wall of each connector pocket
    return U(sp)

HOOD_IN_W, HOOD_IN_D, HOOD_T = 102.5, 18.5, 1.6
HOOD_Z0 = 43.0
def build_hood():
    ow, od = HOOD_IN_W + 2 * HOOD_T, HOOD_IN_D + 2 * HOOD_T
    top_in = 69.0
    out = cube(ow, od, top_in + HOOD_T - HOOD_Z0, 0, 0, HOOD_Z0)
    inn = cube(HOOD_IN_W, HOOD_IN_D, top_in - HOOD_Z0 + 0.1, 0, 0, HOOD_Z0 - 0.1)
    hd = out - inn
    fy = -od / 2                                                         # front outer face
    dim = [Manifold.sphere(0.85, 24).translate((s * (HOOD_IN_W / 2 + 0.2), 0, 47.5)) for s in (-1, 1)]
    hd = hd - U(dim)
    chev, bar = logo(-33.0, 57.0, 0.95)
    word = text("NO SKIPS", 5.4, 10.0, 57.0)
    rule = box(-44.0, 49.6, 44.0, 51.0).buffer(0)
    pk = lambda g: xz(g, 0.6, fy - 0.01)
    iv, rd = unary_union([chev, word]), bar
    hd = hd - pk(iv.buffer(0.05)) - pk(rd.buffer(0.05))
    return hd, xz(iv, 0.6, fy), xz(rd, 0.6, fy), fy

def stick(c, body_len, w=21.0, t=10.0, y=-0.7, z0=SHOULDER):
    body = ext(rrect(w, t, 2.2), body_len, z0).translate((c, y, 0))
    conn = cube(12.0, 4.5, SHOULDER - 1.4, c, y, 1.4)
    return body, conn
def conn_c(c, y=-0.7):
    return cube(8.4, 2.6, SHOULDER - 1.4, c, y, 1.4)

def build_crate():
    p = Product("B6", "crate", "Crate")
    shell, spine = build_shell(), build_spine()
    hood, hin, hrd, fy = build_hood()
    shim = cube(19.5, 3.0, 36.0, 0, 0, 0)
    # tags: ivory plate 21.4 x 0.85 x 10, black word inlaid flush on the front face. Reverse is blank to write on.
    words = ["MAIN", "BKUP", "REC", "SPARE"]
    tag_pl = cube(21.4, 0.85, 10.0, 0, 0.425, 0)
    tag_ws = []
    tags_w = []
    for i, wd in enumerate(words):
        g = fit_text(wd, 4.0, 19.0, 0, 5.0)
        wm = xz(g, 0.4, 0.0)
        tag_ws.append(wm)
    # print orientations
    p.part("shell", shell, BLACK, infill=0.2)
    p.part("spine", rot(spine, -90, 0, 0), RED, infill=1.0)
    ho_p = rot(hood, 90, 0, 0); p.part("hood", ho_p, BLACK, infill=0.2)
    p.part("hood_mark", rot(hin, 90, 0, 0), IVORY, infill=1.0)
    p.part("hood_bar", rot(hrd, 90, 0, 0), RED, infill=1.0)
    for i, wd in enumerate(words):
        p.part(f"tag_{wd.lower()}", rot(tag_pl - tag_ws[i].translate((0, -0.001, 0)), 90, 0, 0), IVORY, infill=1.0)
        p.part(f"tag_{wd.lower()}_word", rot(tag_ws[i], 90, 0, 0), BLACK, infill=1.0)
    p.part("fit_shim", rot(shim, 90, 0, 0), RED, qty=4, infill=1.0)

    # ---------------- fit and clearance checks on the real solids
    def vol(a, b): return (a ^ b).volume()
    checks = {}
    base = U([shell, spine])
    checks["spine into shell"] = vol(shell, spine)
    # largest and smallest sticks (L 66 x 22 x 13 and L 52 x 12 x 6), USB A and USB C, at each slot
    big = U(list(stick(CX[1], 66 - 11.6, 22.0, 13.0, y=-0.7 + (CH_Y1 + CH_Y0) / 2 + 0.7 - 0.7)))  # placeholder, overwritten below
    def fits(c, bl, w, t, yc, conn):
        b, cn = stick(c, bl, w, t, yc)
        return vol(base, b), vol(base, cn if conn == "A" else conn_c(c, yc))
    yc_mid = (CH_Y0 + CH_Y1) / 2
    for nm, (bl, w, t) in {"52x12x6": (52 - 11.6, 12.0, 6.0), "57x21x10": (57 - 11.6, 21.0, 10.0), "66x22x13": (66 - 11.6, 22.0, 13.0)}.items():
        for conn in ("A", "C"):
            vb, vc = fits(CX[2], bl, w, t, yc_mid if t > 10 else -0.7, conn)
            checks[f"stick {nm} conn {conn}"] = round(vb + vc, 4)
    # hood over the shell with the tallest stick (top at 67.4) in every slot
    tall = [stick(c, 66 - 11.6, 22.0, 13.0, yc_mid)[0] for c in CX]
    checks["hood vs shell"] = vol(hood, base)
    checks["hood vs tallest sticks"] = vol(hood, U(tall))
    shell_nobump = shell
    # tags into their recesses
    for i, c in enumerate(CX):
        t = (tag_pl - tag_ws[i]).translate((c, -9.0, 14.0))
        checks[f"tag {i + 1} into recess"] = round(vol(shell, t), 4)
    checks["shim between stick and spine"] = round(vol(base, shim.translate((12.1, 4.5, 13.0))), 4)
    for k, v in checks.items(): print("  check", k, "->", v, "mm3", "OK" if v < 0.01 else "CONTACT")
    p.checks = checks

    # ---------------- scenes for renders
    def props(ids, lens, cols):
        out = []
        for i, bl, col in zip(ids, lens, cols):
            b, cn = stick(CX[i], bl)
            out += [(b, col), (cn, "steel")]
        return out
    tagsw = []
    for i, c in enumerate(CX):
        tagsw += [((tag_pl - tag_ws[i]).translate((c, -9.0 + 0.04, 14.0)), IVORY), (tag_ws[i].translate((c, -9.0 + 0.04, 14.0)), BLACK)]
    built = [(shell, BLACK), (spine, RED)] + tagsw
    sticks3 = props([0, 1, 2], [53.0 - 11.6, 62.0 - 11.6, 57.0 - 11.6], ["prop", "blue", "prop2"])
    hood_on = [(hood, BLACK), (hin, IVORY), (hrd, RED)]
    p.scene("crate", built + sticks3 + hood_on)
    p.scene("crate_open", built + sticks3)
    p.scene("crate_full", built + props([0, 1, 2, 3], [53.0 - 11.6, 62.0 - 11.6, 57.0 - 11.6, 49.0 - 11.6], ["prop", "blue", "prop2", "prop"]))
    p.scene("crate_bare", built)
    cutbox = cube(80, 60, 140, -12.1 - 40, 0, -5)
    p.scene("crate_section", [(m ^ cutbox, c) for m, c in built + sticks3])
    tag_set = [((tag_pl - tag_ws[i]).translate((c, -9.0, 14.0)), IVORY) for i, c in enumerate(CX)]
    tag_flat = lambda dy, dz: [(mv(m, 0, dy, dz), IVORY) for m, _ in tag_set] + [(mv(tag_ws[i].translate((c, -9.0, 14.0)), 0, dy, dz), BLACK) for i, c in enumerate(CX)]
    p.scene("crate_build", [(shell, BLACK), (mv(spine, 0, 0, 52), RED)] + [(mv(hood, 0, 0, 70), BLACK), (mv(hin, 0, 0, 70), IVORY), (mv(hrd, 0, 0, 70), RED)]
            + [(mv(shim, x, -55, 0), RED) for x in (-30, -10, 10, 30)] + tag_flat(-85, -14))
    p.scene("crate_back", built + sticks3 + hood_on)
    p.scene("bp_B6", built + hood_on)
    p.scene("bpo_B6", built + sticks3 + hood_on)
    # step pictures
    p.scene("crate_s1", [(shell, BLACK), (mv(spine, -128, 0, 0), RED), (mv(hood, 128, 0, 0), BLACK), (mv(hin, 128, 0, 0), IVORY), (mv(hrd, 128, 0, 0), RED)]
            + [(mv(shim, x, -52, 0), RED) for x in (-75, -55, -35, -15)] + tag_flat(-52, -14)[0:0]
            + [(mv(m, 52, -52 + 9, -14 + 0), c) for m, c in tag_flat(0, 0)])
    p.scene("crate_s2", [(shell, BLACK), (mv(spine, 0, 0, 38), RED)])
    p.scene("crate_s3", [(shell, BLACK), (spine, RED)] + tagsw[:6] + [((tag_pl - tag_ws[3]).translate((CX[3], -9.0 - 22, 14.0)), IVORY), (tag_ws[3].translate((CX[3], -9.0 - 22, 14.0)), BLACK)])
    p.scene("crate_s4", built + props([0, 1], [53.0 - 11.6, 62.0 - 11.6], ["prop", "blue"]) + [(mv(stick(CX[2], 57.0 - 11.6)[0], 0, 0, 30), "prop2"), (mv(stick(CX[2], 57.0 - 11.6)[1], 0, 0, 30), "steel")])
    p.scene("crate_s5", built + sticks3 + [(mv(hood, 0, 0, 42), BLACK), (mv(hin, 0, 0, 42), IVORY), (mv(hrd, 0, 0, 42), RED)])
    p.note = ("102 x 18 x 49 mm shell, 71 mm with the hood on. Four slots, 24.2 mm pitch. Sticks stand connector down in a sealed pocket on a shoulder; "
              "a window in front of each pocket shows the silver connector when the stick is home and the red spine foot when the slot is empty. "
              "Takes sticks 52 to 66 mm long, 12 to 22 wide, 6 to 13 thick, USB A or C. Shell prints upright, spine back face down, hood front face down "
              "with the lockup inlaid flush, tags front face down with the word inlaid. Slide the spine in from the top, press the tags in, drop the sticks in, press the hood on.")
    P["B6"] = p

P = {}
if __name__ == "__main__":
    build_crate()
    rep = {}
    for k, p in P.items():
        rep[k] = p.export(); print(k, p.name, rep[k]["grams"], "g")
        for x in rep[k]["parts"]: print("  ", x["file"], x["size"], x["grams"])
    old = {}
    try: old = json.load(open(f"{OUT}/report.json"))
    except Exception: pass
    old.update(rep); os.makedirs(OUT, exist_ok=True); json.dump(old, open(f"{OUT}/report.json", "w"), indent=1)
