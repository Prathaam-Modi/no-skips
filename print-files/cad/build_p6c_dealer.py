"""P6C Dealer button set (28 Nov 2026): dealer button plus small and big blind buttons, card-table line.
Sizes run down the 45 mm Play grid: dealer 45 mm (one module, sits square on a chess or tangram cell), big blind 40 mm,
small blind 36 mm, so rank reads by size and the three stack as a neat tiered column (9 + 7 + 7 = 23 mm).
Colour: every body is ivory, so a whole set shares ONE plate and swaps happen only in the first 3 layers.
  front (prints down on the textured PEI, matte): inlay 0.6 mm (3 layers) - DEALER in red (the set's one red element),
        SB and BB in black. Black and red are opaque at 3 layers; the ivory body behind them never shows through.
  back (smooth top face): tone-on-tone deboss, 0.6 mm - DEALER / SMALL BLIND / BIG BLIND spelled out, plus the No Skips mark
        10 mm wide. Costs no colour swaps.
  rim: 0.6 mm stepped bevel top and bottom, and a fine coin reeding (1 mm pitch, 0.3 mm deep) on the wall that hides layer lines
       and gives the fingers something to catch on felt.
Solid parts (100% zig-zag). No supports, no added parts.
Usage: python3 build_p6c_dealer.py   (writes STLs to print-files/stl/P6C_dealer_button/, scenes to NS_OUT/scenes)"""
import math, json, os, shutil
os.environ.setdefault("NS_OUT", "/tmp/p6c_out")
from ns import *
from build2 import logo

HERE = os.path.dirname(os.path.abspath(__file__))
STL_DIR = os.path.join(HERE, "..", "stl", "P6C_dealer_button")
GRID = 45.0
BAND = 0.6            # front inlay depth: 3 layers at 0.2 mm
DEB = 0.6             # back deboss depth
C = 0.6               # stepped bevel
REED_P, REED_D = 1.0, 0.3
LOGO_W = 10.0
SPEC = {   # name: diameter, thickness, front word, front cap height, front colour, back lines, back cap height
    "dealer": dict(d=GRID, h=9.0, front="DEALER", cap=7.5, col=RED, back=["DEALER"], bcap=5.0),
    "big_blind": dict(d=40.0, h=7.0, front="BB", cap=12.0, col=BLACK, back=["BIG", "BLIND"], bcap=4.6),
    "small_blind": dict(d=36.0, h=7.0, front="SB", cap=11.0, col=BLACK, back=["SMALL", "BLIND"], bcap=4.4),
}

def reeded(d):
    """Disc outline with coin reeding: N round notches at about 1 mm pitch."""
    R = d / 2; n = int(round(math.pi * d / REED_P))
    rn = 0.33                                   # notch radius; centre placed so the notch is REED_D deep
    notches = [circle(rn, (R + rn - REED_D) * math.cos(2 * math.pi * k / n), (R + rn - REED_D) * math.sin(2 * math.pi * k / n), seg=14)
               for k in range(n)]
    return circle(R, seg=360).difference(unary_union(notches)), n

def word(s, cap):
    """Poppins Bold caps, cap height = cap, centred on the origin."""
    g = text(s, cap, 0, 0)
    return affinity.translate(g, -(g.bounds[0] + g.bounds[2]) / 2, -(g.bounds[1] + g.bounds[3]) / 2)

def back_art(sp):
    """Back face art (as seen from above): lines of text stacked above the logo, the block centred on the face."""
    lines = [word(s, sp["bcap"]) for s in sp["back"]]
    lg = logo(0, 0, LOGO_W / 13.6)
    gap_t, gap_l = 0.45 * sp["bcap"], 3.0
    hs = [g.bounds[3] - g.bounds[1] for g in lines] + [lg.bounds[3] - lg.bounds[1]]
    gaps = [gap_t] * (len(lines) - 1) + [gap_l]
    tot = sum(hs) + sum(gaps); y = tot / 2; out = []
    for g, h, gp in zip(lines + [lg], hs, gaps + [0]):
        cy = y - h / 2
        out.append(affinity.translate(g, -(g.bounds[0] + g.bounds[2]) / 2, cy - (g.bounds[1] + g.bounds[3]) / 2))
        y -= h + gp
    return out

def button(sp):
    outline, n = reeded(sp["d"])
    solid = body(outline, sp["h"], c=C, top=True, bottom=True)
    # front: seen from below, so the word is mirrored in x in the model
    f2d = affinity.scale(word(sp["front"], sp["cap"]), -1, 1, origin=(0, 0))
    inlay = solid ^ ext(f2d, BAND + 0.01, -0.01)                      # exactly the pocket: same solid, so flush with zero gap
    b2d = back_art(sp)
    deb = ext(unary_union(b2d), DEB + 0.01, sp["h"] - DEB)
    shell = solid - deb
    pocketed = shell - inlay
    return dict(solid=solid, shell=shell, body=pocketed, inlay=inlay, front2d=word(sp["front"], sp["cap"]), back2d=b2d, reeds=n)

# ------------------------------------------------------------------ checks
def stroke(g):
    """Mean stroke = 2 area / perimeter; min stroke >= 2 r if every glyph part survives an erosion by r."""
    parts = list(getattr(g, "geoms", [g]))
    mean = 2 * g.area / g.length
    r = 0.0
    while r < 3 and all(not p.buffer(-(r + 0.05)).is_empty for p in parts): r += 0.05
    return round(mean, 2), round(2 * r, 2)

def check(name, sp, B):
    out = {}
    fr = B["front2d"]; out["front_cap_mm"] = round(fr.bounds[3] - fr.bounds[1], 2); out["front_w_mm"] = round(fr.bounds[2] - fr.bounds[0], 2)
    out["front_stroke_mean_min"] = stroke(fr)
    out["back_caps_mm"] = [round(g.bounds[3] - g.bounds[1], 2) for g in B["back2d"][:-1]]
    out["back_stroke_min"] = min(stroke(g)[1] for g in B["back2d"][:-1])
    out["logo_w_mm"] = round(B["back2d"][-1].bounds[2] - B["back2d"][-1].bounds[0], 2)
    # art stays clear of the bevel and reeding: farthest point from the centre vs usable radius
    R_use = sp["d"] / 2 - REED_D - C
    far = max(max(math.hypot(x, y) for x, y in (p.exterior.coords)) for g in [fr] + B["back2d"] for p in getattr(g, "geoms", [g]))
    out["art_clearance_mm"] = round(R_use - far, 2)
    ib = B["inlay"].bounding_box(); out["inlay_thick_mm"] = round(ib[5] - ib[2], 3)
    # flush and complementary: body + inlay == shell, overlap zero
    ov = (B["body"] ^ B["inlay"]).volume()
    out["overlap_mm3"] = round(ov, 4)
    out["gap_mm3"] = round(B["shell"].volume() - B["body"].volume() - B["inlay"].volume(), 4)
    out["inlay_flush"] = abs(ib[2] - 0.0) < 1e-6           # inlay face is on z = 0 with the body face
    for k in ("body", "inlay"):
        t = tm(B[k]); out[f"{k}_watertight"] = bool(t.is_watertight)
        out[f"{k}_bodies"] = len(t.split(only_watertight=False)) if k == "body" else B[k].decompose().__len__()
    out["grams_body"] = round(B["body"].volume() * DENSITY, 1); out["grams_inlay"] = round(B["inlay"].volume() * DENSITY, 2)
    out["reeds"] = B["reeds"]
    return out

if __name__ == "__main__":
    p = Product("P6C", "dealer_button", "Dealer button set")
    B = {k: button(sp) for k, sp in SPEC.items()}
    for k, sp in SPEC.items():
        p.part(k, B[k]["body"], IVORY, infill=1.0)
        p.part(f"{k}_front_{sp['front'].lower()}", B[k]["inlay"], sp["col"], infill=1.0, on=k)
    # scenes: front faces up (rotate about y, so the mirrored front reads right way round from above)
    up = lambda m, h: m.rotate((0, 180, 0)).translate((0, 0, h))
    def piece(k, x=0, y=0, z=0, front=True, rz=0):
        sp = SPEC[k]; items = [(B[k]["body"], IVORY), (B[k]["inlay"], sp["col"])]
        return [(mv((up(m, sp["h"]) if front else m).rotate((0, 0, rz)), x, y, z), c) for m, c in items]
    table = [(ext(rrect(260, 170, 2), 3.0, -3.0), PROP)]          # charcoal felt slab
    cards = [(mv(ext(rrect(63, 88, 3), 0.5, 0).rotate((0, 0, a)), x, y, z), c) for a, x, y, z, c in [(-8, -64, 30, 0.0, IVORY), (7, -50, 36, 0.5, BLACK)]]
    sc = table + cards + piece("dealer", 8, 6, rz=-10) + piece("big_blind", 62, 20, rz=12) + piece("small_blind", 46, -32, rz=-4) \
        + piece("dealer", -60, -38, front=False, rz=20)
    p.scene("dealer_set", sc)
    p.scene("dealer_close", [(ext(rrect(150, 110, 2), 3.0, -3.0), PROP)] + piece("dealer", -14, -6, rz=-6) + [
        (mv(m, 34, 26, 0), c) for m, c in piece("dealer", front=False, rz=14)])
    rep = p.export()
    if os.path.isdir(STL_DIR): shutil.rmtree(STL_DIR)
    shutil.copytree(f"{OUT}/stl/P6C_dealer_button", STL_DIR)
    rep["checks"] = {k: check(k, sp, B[k]) for k, sp in SPEC.items()}
    rep["text_log"] = TEXT_LOG
    json.dump(rep, open(os.path.join(STL_DIR, "P6C_report.json"), "w"), indent=1)
    print(json.dumps(rep, indent=1))
