"""No Skips D14 Dock: two-controller dock for D5 Hold, the first Hold module. One controller in front, one behind.

A sleeve drops over the Hold post (before the saddle goes on) and rests on the base. An arm runs forward to a cradle:
a fence keeps the controller clear of the headphone cups, a red fader-cap lip slides onto the tip on a dovetail.
The controller hangs face out by the gap between its grips (DualSense, DualShock 4, Xbox, Switch Pro and most others).

Both parts are one side profile extruded 36 mm, so they print lying on their side: no supports, all bridges 10.4 mm or less,
and the layers run along the arm, which is the strong way for a cantilever.

Run: python3 build6.py                 build, check, export STLs and scenes   (NS_OUT=<dir> sets the output folder)
     python3 build6.py render [names]  studio renders
     python3 build6.py guides          labelled build and use pictures
     python3 build6.py blueprint       drawing sheet
"""
import math, json, sys, os
from ns import *
from shapely.geometry import Polygon, box
import build2

P = {}
W = 36.0                     # width across x (sleeve and arm)
BASE_TOP = 20.0              # Hold base top
FLOOR = 70.0                 # cradle floor height, world z: controller crotch sits here
# Hold post section (world): x +-15, y -5..5, front (-y) carries 0.6 ticks at |x| 5.75..10.25 and the red fader 16 wide, 3 proud
BORE_X, BORE_Y = 15.2, 5.2   # 0.2 clearance a side
RELIEF_X, RELIEF_Y = 10.8, 6.0   # clears the ticks by 0.4
CHAN_X, CHAN_Y = 8.6, 8.5        # lets the sleeve pass the fader on the way down (0.6 and 0.5 clear)
WALL = 2.4
Y_FRONT = -(CHAN_Y + WALL)   # -10.9
Y_BACK = BORE_Y + WALL       # 7.6
ARM_T = 9.0
FENCE_Y0, FENCE_Y1, FENCE_H = -46.0, -50.0, 10.0
TIP_Y = -110.0               # end of the floor, red cap starts here
CAP_D, CAP_H = 8.0, 12.0     # cap depth along y, lip height above the floor
DOVE = 0.12                  # dovetail clearance a side: set from the fit coupon dovetail (0.15 there = a free slide)

def tenon(grow=0.0):
    """Dovetail on the arm tip, in the (y, z) profile plane: narrow at the root, wide at the end."""
    zc = FLOOR - ARM_T / 2
    return Polygon([(TIP_Y + 0.01, zc - 2.0 - grow), (TIP_Y - 5.0 - grow, zc - 3.2 - grow),
                    (TIP_Y - 5.0 - grow, zc + 3.2 + grow), (TIP_Y + 0.01, zc + 2.0 + grow)])

def mirror_y(g):
    return affinity.scale(g, -1, 1, origin=(0, 0))

def dock_profile():
    """Side profile (y, z). Front arm and back arm are mirror images, so one controller each side balances the stand."""
    z0 = BASE_TOP
    sleeve = box(Y_FRONT, z0, Y_BACK, FLOOR)
    arm = box(TIP_Y, FLOOR - ARM_T, Y_FRONT + 0.5, FLOOR)
    gusset = Polygon([(Y_FRONT + 0.5, z0 + 12), (Y_FRONT + 0.5, FLOOR - ARM_T + 0.5), (-40.0, FLOOR - ARM_T + 0.5)])
    fence = rrect(abs(FENCE_Y1 - FENCE_Y0), FENCE_H * 2, 1.8, (FENCE_Y0 + FENCE_Y1) / 2, FLOOR)
    front = unary_union([arm, gusset, fence])
    back = affinity.translate(mirror_y(front), Y_BACK + Y_FRONT, 0)     # same arm, measured from the back wall
    g = fillet(unary_union([sleeve, front, back]), 1.2)                  # soft corners, including floor to fence
    return unary_union([g, tenon(), affinity.translate(mirror_y(tenon()), Y_BACK + Y_FRONT, 0)])

def cap_profile():
    zc = FLOOR - ARM_T / 2
    blk = rrect(CAP_D, ARM_T + CAP_H + 1.0, 1.6, TIP_Y - CAP_D / 2 - 0.0, (FLOOR - ARM_T - 0.5 + FLOOR + CAP_H) / 2)
    g = blk.difference(tenon(DOVE))
    # three grip grooves on the outer face, fader cap style
    for k in range(3):
        z = FLOOR + 1.5 + k * 3.4
        g = g.difference(rrect(2.4, 1.4, 0.6, TIP_Y - CAP_D, z))
    return g

def local_bore():
    """Bore as boxes in the local frame (u = world y, v = world z, w = world x + W/2)."""
    v0, h = BASE_TOP - 0.1, FLOOR - BASE_TOP + 0.2
    return U([Manifold.cube((2 * BORE_Y, h, 2 * BORE_X)).translate((-BORE_Y, v0, W / 2 - BORE_X)),
              Manifold.cube((RELIEF_Y - BORE_Y + 0.01, h, 2 * RELIEF_X)).translate((-RELIEF_Y, v0, W / 2 - RELIEF_X)),
              Manifold.cube((CHAN_Y - RELIEF_Y + 0.01, h, 2 * CHAN_X)).translate((-CHAN_Y, v0, W / 2 - CHAN_X))])

def logo2(cx, cy, s=1.0):
    return build2.logo(cx, cy, s)

def to_world(m):
    """Local (u, v, w) -> world (x = w - W/2, y = u, z = v)."""
    # rotate so local z (w) becomes world x, local x (u) world y, local y (v) world z
    M = [[0, 0, 1, -W / 2], [1, 0, 0, 0], [0, 1, 0, 0]]
    return m.transform(M)

def controller_prop():
    """Generic two-grip game controller, hanging face out (-y) by the gap between its grips (a stand-in, not any brand)."""
    T = 50.0; yb = FENCE_Y1 - 1.0; y0 = yb - T; lift = 0.3
    body2d = fillet(unary_union([rrect(148, 40, 18, 0, FLOOR + 20 + lift), rrect(100, 16, 7, 0, FLOOR + 42 + lift)]), 3.0)
    body3 = rot(body(body2d, T, c=4.0, steps=4, bottom=True), 90, 0, 0).translate((0, yb, 0))
    grips = []
    for s in (-1, 1):
        g2 = Polygon([(s * 18.5, FLOOR + 8), (s * 72, FLOOR + 10), (s * 70, FLOOR - 30), (s * 58, FLOOR - 56), (s * 40, FLOOR - 54), (s * 28, FLOOR - 26), (s * 21, FLOOR - 4)])
        g2 = fillet(g2.buffer(0), 9.0)
        grips.append(rot(body(g2, T - 8, c=5.0, steps=4, bottom=True), 90, 0, 0).translate((0, yb - 4, 0)))
    sticks = [U([cyl(5, 7, 0, s * 24, FLOOR + 12), cyl(9.5, 3, 7, s * 24, FLOOR + 12)]).rotate((90, 0, 0)).translate((0, y0 + 1.0, 0)) for s in (-1, 1)]
    pad = body(rrect(52, 26, 4, 0, FLOOR + 32), 2.0, c=0.8).rotate((90, 0, 0)).translate((0, y0 + 0.5, 0))
    btns = [cyl(4, 3, 0, 52 + dx, FLOOR + 26 + dz).rotate((90, 0, 0)).translate((0, y0 + 0.5, 0)) for dx, dz in ((0, 9), (0, -9), (9, 0), (-9, 0))]
    dpad = U([body(rrect(7, 20, 2, -52, FLOOR + 26), 3, c=0.6), body(rrect(20, 7, 2, -52, FLOOR + 26), 3, c=0.6)]).rotate((90, 0, 0)).translate((0, y0 + 0.5, 0))
    return U([body3] + grips + [pad]), U(sticks + btns + [dpad])

def build_dock():
    p = Product("D14", "dock", "Dock")
    prof = dock_profile()
    dock_l = ext(prof, W) - local_bore()
    # small chevron mark debossed 0.4 into the outer side face (the face up on the plate)
    mark = ext(logo2(-28.0, FLOOR - ARM_T / 2, 0.55), 0.41, W - 0.4)
    dock_l = dock_l - mark
    cap_l = ext(cap_profile(), W)
    # print orientation: profile flat on the bed (local frame as built)
    p.part("dock", dock_l, BLACK, infill=0.3)
    p.part("cap", cap_l, RED, qty=2, infill=1.0)
    dock_w = to_world(dock_l)
    OFF = Y_BACK + Y_FRONT                      # back arm is the front arm mirrored about y = OFF / 2
    cap_f = to_world(cap_l); cap_b = cap_f.mirror((0, 1, 0)).translate((0, OFF, 0))
    cap_w = U([cap_f, cap_b])
    p.dock_w, p.cap_w = dock_w, cap_w
    # Hold, from the classic range build
    build2.build_hold(); h = build2.P["D5"]
    hold_built = h.scenes["headphonestand_bare"]; hold_full = h.scenes["headphonestand"]
    pad_f, st_f = controller_prop()
    pad_b, st_b = [m.mirror((0, 1, 0)).translate((0, OFF, 0)) for m in (pad_f, st_f)]
    pad, sticks = U([pad_f, pad_b]), U([st_f, st_b])
    built = hold_built + [(dock_w, BLACK), (cap_w, RED)]
    p.scene("dock", [(dock_w, BLACK), (cap_w, RED)])
    p.scene("dock_hold", built)
    p.scene("dock_use", hold_full + [(dock_w, BLACK), (cap_w, RED), (pad, PROP), (sticks, PROP2)])
    p.scene("bpo_D14", [(dock_w, BLACK), (cap_w, RED)])
    # exploded: base and post, dock lifted above the post top, cap pulled out sideways, saddle higher still
    base_post = hold_built[:4]; saddle = hold_built[4:]
    lift = 232.0 - BASE_TOP + 8.0
    ex = base_post + [(mv(dock_w, 0, 0, lift), BLACK), (mv(cap_f, 46, -10, lift), RED), (mv(cap_b, 46, 10, lift), RED)] + [(mv(m, 0, 0, 120), c) for m, c in saddle]
    p.scene("dock_build", ex)
    # step pictures: 1 saddle off and dock over the post, 2 caps on and saddle back
    p.scene("dock_s1", base_post + [(mv(dock_w, 0, 0, 60), BLACK)] + [(mv(m, 0, 0, 150), c) for m, c in saddle])
    p.scene("dock_s2", base_post + [(dock_w, BLACK), (mv(cap_f, 75, 0, 0), RED), (mv(cap_b, 75, 0, 0), RED)] + [(mv(m, 0, 0, 45), c) for m, c in saddle])
    p.scene("bp_D14", [(dock_w, BLACK), (cap_f, RED), (cap_b, RED)])
    # checks
    post_w = tm(hold_built[2][0]); fader = tm(hold_built[3][0])
    clash = {}
    for nm, m in (("post", hold_built[2][0]), ("fader_and_ticks", hold_built[3][0]), ("base", hold_built[0][0]), ("dial", hold_built[1][0])):
        clash[nm] = round(float((dock_w ^ m).volume()), 4)
    # dock dropped to every height on the way down must miss the fader and ticks
    sweep = max(float((mv(dock_w, 0, 0, dz) ^ hold_built[3][0]).volume()) for dz in np.arange(0, 200, 4.0))
    clash["fader_sweep"] = round(sweep, 4)
    clash["cap_vs_dock"] = round(float((dock_w ^ cap_w).volume()), 4)
    clash["controller_vs_hold_and_dock"] = round(float((pad ^ U([m for m, c in hold_full if c != PROP] + [dock_w, cap_w])).volume()), 2)
    clash["controller_vs_headphones"] = round(float((pad ^ U([m for m, c in hold_full if c == PROP])).volume()), 2)
    pb = tm(pad_f).bounds
    # tipping: moments about the base edge (radius 58) with one controller (worst case) and with two; 280 g each
    gh, gd = 183.0, None
    p.checks = clash
    yc = float(tm(pad_f).center_mass[1]); gd = grams(dock_l, 0.3) + 2 * grams(cap_l, 1.0)
    restore = gh * 58 + gd * 58          # dock is symmetric, its weight sits over the post
    p.tip = dict(controller_cg_y=round(yc, 1), one_controller_safety=round(restore / (280 * (abs(yc) - 58)), 2),
                 two_controllers="balanced, front and back cancel")
    p.info = dict(controller_lowest_z=round(float(pb[0][2]), 1), controller_top_z=round(float(pb[1][2]), 1),
                  controller_y=[round(float(pb[0][1]), 1), round(float(pb[1][1]), 1)], floor_z=FLOOR,
                  cradle_span=round(abs(TIP_Y - FENCE_Y1), 1), reach_from_post=round(abs(TIP_Y - CAP_D) - 5.0, 1))
    b = tm(U([dock_w, cap_w])).bounds; p.info["size"] = [round(float(x), 1) for x in (b[1] - b[0])]
    p.note = (f"Holds two controllers, one in front and one behind the post, so the weight balances. Drops over the Hold post before the saddle and rests on the base. {p.info['size'][0]:g} x {p.info['size'][1]:g} x {p.info['size'][2]:g} mm. "
              f"Cradle floor {FLOOR - BASE_TOP:g} mm above the base, {p.info['cradle_span']:g} mm between the fence and the red lip, arm {W:g} mm wide "
              "(fits between the grips of DualSense, DualShock 4, Xbox and Switch Pro controllers). Bore 30.4 x 10.4 with a front channel that passes the Hold fader. "
              "Both parts print lying on the side with the chevron face up, no supports. Two red caps (print 2) slide onto the dovetails from the side; a drop of superglue if it is loose.")
    P["D14"] = p

# ------------------------------------------------------------------ pictures
SHOTS6 = {"dock": dict(az=-38, el=22, zoom=1.0), "dock_hold": dict(az=-34, el=12, zoom=1.0), "dock_use": dict(az=-62, el=22, zoom=1.0),
          "dock_s1": dict(az=-58, el=12, zoom=1.0), "dock_s2": dict(az=-58, el=16, zoom=1.0),
          "dock_build": dict(az=-34, el=10, zoom=1.0)}
def _inject():
    import render, blueprint
    render.SHOTS.update(SHOTS6)
    blueprint.SHEETS["D14"] = dict(piece="DOCK 2-CONTROLLER DOCK FOR HOLD", parts="DOCK, 2 CAPS",
                                   cap=f"ISOMETRIC.  DROPS OVER THE HOLD POST.  CRADLE {abs(TIP_Y - FENCE_Y1):g} DEEP, ARM {W:g} WIDE.  VIEWS: BUILT", iso=dict(az=-38, el=22))
    return render, blueprint

def guides():
    from annotate import annotate
    _inject()
    top = 232.0; lift = top - BASE_TOP + 8.0
    G = {}
    sad = 232.0 - 22.0 - 13.0 + 56.0                  # saddle top as built
    G["dock_s1"] = dict(banner="1  Saddle off, Dock down over the post", labels=[
        dict(text="Saddle", sub="pull it straight up and off", tag="A", at=(30, 0, sad + 150 - 20), to=(150, -40)),
        dict(text="Dock", sub="fits one way: wide channel to the fader", tag="B", at=(0, -40, FLOOR + 60 - 4), to=(-280, -60)),
        dict(text="Post", sub="red fader faces the front", tag="D", at=(15, -5, 160), to=(160, 30)),
        dict(text="Base", sub="the Dock rests on it", tag="E", at=(40, -40, 18), to=(150, 40)),
    ], arrows=[
        dict(pts=[(0, 0, sad + 150 - 70), (0, 0, sad + 150 - 30)], step=1, text="up", text_off=(16, -20)),
        dict(pts=[(-24, -60, FLOOR + 60 - 14), (-24, -60, FLOOR + 6)], step=2, text="down to the base", text_off=(-170, 0)),
    ])
    G["dock_s2"] = dict(banner="2  Red caps on, saddle back on", labels=[
        dict(text="Red cap, front", sub="slides on from the side", tag="C", at=(93, TIP_Y - 4, FLOOR - 2), to=(-60, 150)),
        dict(text="Red cap, back", sub="same again", tag="C", at=(93, -TIP_Y + 2.7, FLOOR - 2), to=(130, -170)),
        dict(text="Saddle", sub="press it back on the post", tag="A", at=(30, 0, sad + 45 - 20), to=(150, -60)),
    ], arrows=[
        dict(pts=[(70, TIP_Y - 4, FLOOR + 14), (24, TIP_Y - 4, FLOOR + 14)], step=3),
        dict(pts=[(70, -TIP_Y + 2.7, FLOOR + 14), (24, -TIP_Y + 2.7, FLOOR + 14)], step=3),
        dict(pts=[(0, 0, sad + 45 - 30), (0, 0, sad + 4)], step=4, text="press down", text_off=(16, -10)),
    ])
    out = {}
    for n, g in G.items():
        out[n] = annotate(n, g.get("labels", ()), g.get("arrows", ()), banner=g.get("banner"))
    out["use"] = annotate("dock_use", labels=[
        dict(text="Controller 1", sub="hangs face out by the gap between its grips", tag="", at=(-40, -102, FLOOR + 30), to=(150, 190)),
        dict(text="Controller 2", sub="same on the back, the weight balances", tag="", at=(70, 80, FLOOR + 30), to=(-230, -190)),
        dict(text="Red lip", sub="stops it sliding off", tag="C", at=(18, TIP_Y - 4, FLOOR + 10), to=(170, 60)),
    ], arrows=[],
        banner="Dock: headphones up top, two controllers below", out=f"{OUT}/r/dock_use_guide")
    for k, v in out.items(): print(k, v)

if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "build"
    if mode == "render":
        render, _ = _inject()
        for s in (sys.argv[2].split(",") if len(sys.argv) > 2 and not sys.argv[2].startswith("--") else list(SHOTS6)): render.render(s, "--draft" in sys.argv)
    elif mode == "guides": guides()
    elif mode == "blueprint":
        _, blueprint = _inject(); blueprint.sheet("D14")
    else:
        build_dock()
        rep = {}
        for k, p in P.items():
            rep[k] = p.export(); print(k, p.name, rep[k]["grams"], "g")
            for x in rep[k]["parts"]: print("  ", x["file"], x["size"], x["grams"])
            print("  checks", p.checks); print("  info", p.info); print("  tip", p.tip)
            rep[k]["checks"] = p.checks; rep[k]["info"] = p.info
        old = {}
        try: old = json.load(open(f"{OUT}/report.json"))
        except Exception: pass
        old.update(rep); os.makedirs(OUT, exist_ok=True); json.dump(old, open(f"{OUT}/report.json", "w"), indent=1)
