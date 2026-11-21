"""No Skips D15 Stage: ribbed desk base tile for D7 Channel (the riser the band stands on).

One tile size fits the whole Channel range: tiles sit on a 63.6 mm pitch (module width 60 + joint gap 3.6), so a cup
sits on one tile and the tray spans two. Tiles link to each other with the Channel dovetail (male on the right, socket
on the left, lower the next tile on from above). A 1.2 mm recess locates the modules front to back; a front ledge
holds a phone face down, earbuds or keys. Fluted front and back, flutes on the same rhythm across joins, and a red
line inlaid along the ledge that runs on from tile to tile. Prints upright as it sits, no supports.

Run: python3 build8.py                build, check, export STLs and scenes
     python3 build8.py render [names] studio renders
     python3 build8.py guides         labelled build picture
     python3 build8.py blueprint      drawing sheet
"""
import math, json, sys, os
from ns import *
from shapely.geometry import Polygon, box
import build

P = {}
TW = 63.6                 # tile pitch = Channel module 60 + joint gap 3.6
H = 16.0                  # tile height (lift)
REC = 1.2                 # module recess depth
YB, YF = 34.3, -52.3      # back and front faces (modules sit on y -30 .. 30)
NFL = 14                  # flutes per tile face (pitch 4.543, same rhythm across joins)

def tile():
    out = box(-TW / 2, YF, TW / 2, YB)
    t = body(out, H, c=0.6, steps=3)
    t = t - cube(TW + 2, 60.6, REC + 1, 0, 0, H - REC)                                   # module recess, front to back
    male = ext(build.dove(TW / 2 - 0.01, 8.0, 12.0, 3.0), 11.5)                       # links to the next tile on the right
    sock = ext(build.dove(-TW / 2 - 0.01, 8.5, 12.5, 3.26, 0, 1), 12.0, -0.1)          # takes the tile on the left (open below)
    pitch = TW / NFL
    fl = U([cyl(1.4, H - 2.4, -0.1, -TW / 2 + pitch * (i + 0.5), y, seg=24) for i in range(NFL) for y in (YF, YB)])
    bar = box(-TW / 2 + 1.2, -47.6, TW / 2 - 1.2, -45.2)                               # red line on the ledge
    t = (t + male) - sock - fl - ext(bar, 0.61, H - 0.6)
    red = ext(bar, 0.6, H - 0.6)
    return t, red

def build_stage():
    p = Product("D15", "stage", "Stage")
    t, red = tile()
    p.part("tile", t, BLACK, infill=0.15)
    p.part("ledge_line", red, RED, infill=1.0)
    # checks against the Channel modules on a four-tile row
    build.build_channel()
    ch = {l: m for l, m, c, q, i in build.P["D7"].parts}
    xs = (-(60 + 3.6) - 30, -30.0, 30 + 3.6 + 30)
    mods = [(mv(ch["tall_cup"], xs[0], 0, H - REC), BLACK), (mv(ch["tall_cup_rim"], xs[0], 0, H - REC), RED),
            (mv(ch["mid_cup"], xs[1], 0, H - REC), BLACK), (mv(ch["mid_cup_rim"], xs[1], 0, H - REC), IVORY),
            (mv(ch["tray"], xs[2], 0, H - REC), BLACK), (mv(ch["tray_rim"], xs[2], 0, H - REC), RED)]
    tx = [-TW * 1.5, -TW * 0.5, TW * 0.5, TW * 1.5]
    row = [(mv(t, x, 0, 0), BLACK) for x in tx] + [(mv(red, x, 0, 0), RED) for x in tx]
    tiles_u = U([m for m, c in row if c == BLACK]); mods_u = U([m for m, c in mods])
    p.checks = {"modules vs tiles mm3": round((tiles_u ^ mods_u).volume(), 3),
                "tile vs next tile mm3": round((mv(t, 0, 0, 0) ^ mv(t, TW, 0, 0)).volume(), 3)}
    p.scene("stage", row + mods)
    p.scene("stage_tiles", [(mv(t, x * 1.0, 0, 0), BLACK) for x in (-TW / 2, TW / 2)] + [(mv(red, x, 0, 0), RED) for x in (-TW / 2, TW / 2)])
    p.scene("stage_build", [(mv(t, -TW / 2, 0, 0), BLACK), (mv(red, -TW / 2, 0, 0), RED), (mv(t, TW / 2, 0, 40), BLACK), (mv(red, TW / 2, 0, 40), RED)])
    p.scene("bp_D15", row[:2] + row[4:6]); p.scene("bpo_D15", row[:2] + row[4:6])
    p.note = (f"Tile {TW:g} x {YB - YF:g} x {H:g} mm on a {TW:g} mm pitch. Channel cups sit on one tile, the tray on two. "
              "Tiles link with the Channel dovetail (lower the next tile on from above). 1.2 mm recess, front ledge 22 mm, fluted front and back, "
              "red line inlaid on the ledge. Prints upright, no supports. Four tiles take a full Channel row.")
    P["D15"] = p

SHOTS8 = {"stage": dict(az=-30, el=24, zoom=1.0), "stage_tiles": dict(az=-30, el=28, zoom=1.0), "stage_build": dict(az=-30, el=24, zoom=1.0)}

def _inject():
    import render, blueprint
    render.SHOTS.update(SHOTS8)
    blueprint.SHEETS["D15"] = dict(piece="STAGE DESK BASE TILE", parts="TILE + RED LINE",
                                   cap=f"ISOMETRIC  TWO TILES LINKED.  {TW:g} PITCH, {H:g} HIGH, 1.2 RECESS, CHANNEL DOVETAIL.  REV A", iso=dict(az=-34, el=24))
    return render, blueprint

def guides():
    from annotate import annotate
    _inject()
    G = {"stage_build": dict(banner="Stage: link the tiles, set the Channel on top", labels=[
        dict(text="Tile", sub="dovetail on the right", tag="A", at=(-TW / 2 - 10, YF + 6, H), to=(-170, 110)),
        dict(text="Next tile", sub="socket on the left, lower it on", tag="B", at=(TW / 2 + 10, YF + 6, H + 40), to=(150, -110)),
        dict(text="Recess", sub="Channel cups and tray sit in it", tag="C", at=(-TW / 2, 0, H), to=(-150, -130)),
    ], arrows=[dict(pts=[(TW / 2 - 28, 0, H + 34), (TW / 2 - 28, 0, H + 6)], step=1, text="lower", text_off=(16, -10))])}
    for n, g in G.items():
        print(annotate(n, g["labels"], g["arrows"], banner=g["banner"], src=f"/home/claude/no-skips/img/{n}.webp"))

if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "build"
    if mode == "render":
        render, _ = _inject()
        for s in (sys.argv[2].split(",") if len(sys.argv) > 2 else list(SHOTS8)): render.render(s)
    elif mode == "guides": guides()
    elif mode == "blueprint":
        _, blueprint = _inject(); blueprint.sheet("D15")
    else:
        build_stage()
        for k, p in P.items():
            rep = p.export(); print(k, p.name, rep["grams"], "g", [(x["file"], x["size"], x["grams"]) for x in rep["parts"]])
            print("  checks", p.checks)
