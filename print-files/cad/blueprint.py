"""Blueprint sheets drawn from the print solids. Hidden-line views come from Cycles id, depth and normal passes.
Usage: python3 blueprint.py D6,D7"""
import sys, os, json, math
import numpy as np, bpy, trimesh
from mathutils import Vector
from PIL import Image, ImageDraw, ImageFont

OUT = os.environ.get("NS_OUT", "/home/claude/out")
MONO = "/tmp/DMMono-Regular.ttf"; MONOM = "/tmp/DMMono-Medium.ttf"; POP = "/usr/share/fonts/truetype/google-fonts/Poppins-Bold.ttf"
SS = 2
BG, GRID, FRAME, INK, MUTED, REDC = (18, 17, 16), (27, 25, 24), (58, 54, 50), (233, 228, 218), (143, 138, 130), (200, 32, 43)
FILL = {"black": (30, 28, 27), "ivory": (112, 108, 101), "red": (74, 22, 26)}
SHEETS = {
 "A1": dict(piece="TRACK PLATE", parts="PLATE + BASE BAR", cap="ISOMETRIC  PLATE IN BASE BAR.  REV B"),
 "A5": dict(piece="TRACK TAG", parts="1 + LOOP", cap="ISOMETRIC  TAG + LOOP.  RIM STANDS 0.4 ABOVE THE CODE.  REV B", iso=dict(az=-30, el=40)),
 "B3": dict(piece="ALIAS NAME TAG", parts="1 + LOOP", cap="ISOMETRIC  TAG + LOOP.  REV B", iso=dict(az=-30, el=40)),
 "C4": dict(piece="SIDE A MIXTAPE SET", parts="4 + 2 RAILS", cap="ISOMETRIC  FOUR ON TWO LINKED RAILS.  VIEWS: ONE RAIL.  REV B"),
 "D6": dict(piece="FOLD LAPTOP STAND", parts="2 RIBS + 2 BRACES", cap="ISOMETRIC  ASSEMBLED.  ALL PARTS 6 THICK, PACK FLAT", iso=dict(az=-50, el=24)),
 "D7": dict(piece="CHANNEL DESK SET", parts="3 MODULES", cap="ISOMETRIC  TALL CUP, MID CUP, TRAY LINKED BY DOVETAIL"),
 "D8": dict(piece="B-SIDE CATCH-ALL TRAY", parts="1", cap="ISOMETRIC  ONE PIECE, GROOVED FLOOR", iso=dict(az=-30, el=38)),
 "C1": dict(piece="VOL. 01: THE STUDIO", parts="6 + TRAY", cap="ISOMETRIC  SIX MINIS ON THE NUMBERED TRAY.  VIEWS: SET", iso=dict(az=-30, el=36)),
 "C2": dict(piece="STUDIO MINI", parts="1 (06: 3)", cap="ISOMETRIC  ALL SIX MINIS.  VIEWS: 01 TURNTABLE", iso=dict(az=-30, el=36)),
 "C5": dict(piece="GAIN FIDGET KNOB", parts="KNOB + BASE", cap="EXPLODED  KNOB + BASE.  SPLIT POST SNAPS INTO THE KNOB.  VIEWS: ASSEMBLED"),
 "A3": dict(piece="RAIL WRISTBAND DISPLAY", parts="1 + 5 PEGS", cap="EXPLODED  RAIL + PEGS.  VIEWS: ON THE WALL", iso=dict(az=-30, el=16)),
 "A4": dict(piece="45s RECORD COASTERS", parts="4 + 4 LABELS", cap="ISOMETRIC  SET.  VIEWS: ONE COASTER.  COMING SOON", iso=dict(az=-24, el=34)),
 "B1": dict(piece="STACK PICK AMP", parts="5", cap="EXPLODED  HEAD / BASE / DRAWER / KNOBS / HANDLE.  VIEWS: BUILT", iso=dict(az=-34, el=22)),
 "B2": dict(piece="LIFT CONTROLLER RISERS", parts="2", cap="ISOMETRIC  PAIR.  VIEWS: ONE WEDGE", iso=dict(az=-36, el=22)),
 "B5": dict(piece="RUN 50 MERCH TAGS", parts="50 + LOOPS", cap="ISOMETRIC  12 OF 50.  VIEWS: ONE TAG", iso=dict(az=-20, el=46)),
 "D1": dict(piece="WEDGE PHONE STAND", parts="BODY + RED LIP", cap="ISOMETRIC.  80 x 77 x 105.  FACE 68 DEG, 14 GROOVE, DOVETAIL LIP, FLUTED BACK.  REV E", iso=dict(az=-36, el=22)),
 "D2": dict(piece="TAPE CASE", parts="TRAY + LID", cap="ISOMETRIC  CLOSED.  LID PRESSES ON", iso=dict(az=-28, el=34)),
 "D4": dict(piece="SLEEVE VINYL STAND", parts="LEDGE + 2 FEET", cap="EXPLODED  LEDGE + RECORD FEET.  VIEWS: BUILT", iso=dict(az=-36, el=22)),
 "D5": dict(piece="HOLD HEADPHONE STAND", parts="BASE, POST, SADDLE", cap="EXPLODED  BASE + POST + SADDLE.  VIEWS: BUILT", iso=dict(az=-28, el=14)),
 "D10": dict(piece="EJECT CARD WALLET", parts="FRONT, BACK PLATE, SLIDER", cap="EXPLODED  FRONT + BACK PLATE + SLIDER.  PUSH THE TAB: CARDS FAN OUT.  SPRING BARS HOLD THEM.  VIEWS: CLOSED", iso=dict(az=-36, el=20)),
 "D11": dict(piece="STANDBY LAPTOP RACK", parts="BASE + 3 FINS", cap="ISOMETRIC  FINS SLIDE IN THE DOVETAIL CHANNEL.  VIEWS: BUILT", iso=dict(az=-34, el=22)),
 "D12": dict(piece="ROTARY KEY ORGANISER", parts="2 PLATES, 2 POSTS", cap="EXPLODED  PLATES + SNAP POSTS + LOOP + SPACERS.  VIEWS: BUILT", iso=dict(az=-24, el=30)),
 "X1": dict(piece="CUE COVER  XDJ-RX3", parts="6 TILES, 2 HOODS", cap="EXPLODED  SIX TILES + SCREEN HOOD.  BOW-TIE KEYS UNDERNEATH.  VIEWS: COVER", iso=dict(az=-24, el=40)),
 "B6": dict(piece="CRATE USB KEEPER", parts="SHELL, SPINE, HOOD + 8", cap="ISOMETRIC  HOOD ON.  4 SLOTS AT 24.2 PITCH.  VIEWS: CLOSED", iso=dict(az=-26, el=18)),
 "D9": dict(piece="PERCH SOFA ARM TRAY", parts="TABLE, 4 SLATS, 4 PINS", cap="ISOMETRIC  LAID FLAT.  CONCEPT, NOT RELEASED", iso=dict(az=-32, el=40)),
 "D16": dict(piece="LEAN PHONE STAND", parts="STAND + RED RIDGE", cap="ISOMETRIC  HOLLOW A-FRAME, FACE AT 65 DEG, 12 GROOVE.  PRINTS UPRIGHT", iso=dict(az=-36, el=22)),
 "D17": dict(piece="BOOKENDS (PAIR)", parts="2 + 2 STEEL PLATES", cap="ISOMETRIC  ONE BOOKEND.  STEEL PLATE SEALED IN THE BASE.  VIEWS: ONE", iso=dict(az=-36, el=24)),
 "D18": dict(piece="RIPPLE KEY TRAY", parts="TRAY + RED DOT", cap="ISOMETRIC  RIPPLE GROOVES FROM A RED PRESS-IN DOT", iso=dict(az=-30, el=38)),
 "D19": dict(piece="KEY RAIL", parts="RAIL + 3 HOOKS", cap="ISOMETRIC  RAIL AND PLUG-INS.  45 DEG DOVETAIL, SLIDE IN FROM THE TOP", iso=dict(az=-30, el=20)),
 "G1": dict(piece="PATCHED IN KEYCHAINS", parts="PLUG + SOCKET", cap="ISOMETRIC  PLUG AND SOCKET APART.  CLICK TOGETHER", iso=dict(az=-30, el=30)),
 "RS1": dict(piece="DESK SET (RESERVE)", parts="CHANNEL + 4 STAGE TILES", cap="ISOMETRIC  CHANNEL ON FOUR STAGE TILES.  63.6 GRID", iso=dict(az=-32, el=30)),
}

def load(scene_name):
    sd = f"{OUT}/scenes/{scene_name}"; meta = json.load(open(sd + "/meta.json"))
    return [(trimesh.load(f"{sd}/{fn}", process=True), c) for fn, c in meta]

def passes(items, right, up, fwd, s2):
    """Orthographic id, depth and normal images. right/up/fwd are world unit vectors, fwd points into the scene."""
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    allv = np.vstack([t.vertices for t, _ in items])
    R = np.array([right, up, fwd], float)
    pv = allv @ R.T
    lo, hi = pv.min(0), pv.max(0); ctr_v = (lo + hi) / 2
    w_mm, h_mm = hi[0] - lo[0], hi[1] - lo[1]
    pad = 6
    W = int(math.ceil(w_mm * s2)) + 2 * pad; H = int(math.ceil(h_mm * s2)) + 2 * pad
    for i, (t, c) in enumerate(items):
        me = bpy.data.meshes.new("m"); me.from_pydata((t.vertices * 0.001).tolist(), [], t.faces.tolist()); me.update()
        ob = bpy.data.objects.new("o", me); sc.collection.objects.link(ob)
        m = bpy.data.materials.new("m"); m.use_nodes = True; nt = m.node_tree; nt.nodes.clear()
        out = nt.nodes.new("ShaderNodeOutputMaterial"); em = nt.nodes.new("ShaderNodeEmission")
        ob["nsid"] = i + 1; me.materials.append(m)
        nt.links.new(em.outputs[0], out.inputs[0])
    cam = bpy.data.cameras.new("c"); cam.type = "ORTHO"; cam.ortho_scale = max(W, H) / s2 * 0.001
    co = bpy.data.objects.new("c", cam); sc.collection.objects.link(co); sc.camera = co
    ctr_w = R.T @ ctr_v
    depth = (hi[2] - lo[2]) + 200
    loc = ctr_w - np.array(fwd) * (depth / 2 + 50)
    co.location = Vector((loc * 0.001).tolist())
    from mathutils import Matrix
    M = Matrix((right, up, (-np.array(fwd)).tolist())).transposed()     # camera looks down its -Z
    co.rotation_euler = M.to_euler()
    cam.clip_start = 0.001; cam.clip_end = 10
    r = sc.render; r.engine = "CYCLES"; r.resolution_x = W; r.resolution_y = H; r.resolution_percentage = 100
    sc.cycles.samples = 1; sc.cycles.use_denoising = False; sc.cycles.pixel_filter_type = "BOX"; sc.cycles.filter_width = 0.01
    sc.cycles.max_bounces = 0; r.film_transparent = True
    sc.view_settings.view_transform = "Raw"
    r.image_settings.file_format = "OPEN_EXR"; r.image_settings.color_depth = "32"
    res = {}
    for mode in ("id", "nrm"):
        for ob in sc.objects:
            if ob.type != "MESH": continue
            nt = ob.data.materials[0].node_tree
            em = [n for n in nt.nodes if n.type == "EMISSION"][0]
            for n in [n for n in nt.nodes if n.type not in ("EMISSION", "OUTPUT_MATERIAL")]: nt.nodes.remove(n)
            if mode == "id":
                cd = nt.nodes.new("ShaderNodeCameraData"); comb = nt.nodes.new("ShaderNodeCombineColor")
                comb.inputs[0].default_value = ob["nsid"] / 64.0; comb.inputs[2].default_value = 0
                nt.links.new(cd.outputs["View Z Depth"], comb.inputs[1]); nt.links.new(comb.outputs[0], em.inputs[0])
            else:
                g = nt.nodes.new("ShaderNodeNewGeometry"); vm = nt.nodes.new("ShaderNodeVectorMath"); vm.operation = "MULTIPLY_ADD"
                vm.inputs[1].default_value = (0.5, 0.5, 0.5); vm.inputs[2].default_value = (0.5, 0.5, 0.5)
                nt.links.new(g.outputs["True Normal"], vm.inputs[0]); nt.links.new(vm.outputs[0], em.inputs[0])
        r.filepath = f"/tmp/bp_{mode}.exr"; bpy.ops.render.render(write_still=True)
        im = bpy.data.images.load(r.filepath); a = np.empty(W * H * 4, np.float32); im.pixels.foreach_get(a)
        res[mode] = a.reshape(H, W, 4)[::-1].copy(); bpy.data.images.remove(im)
    return res, (w_mm, h_mm), pad

def lineart(items, right, up, fwd, s2):
    res, size, pad = passes(items, right, up, fwd, s2)
    idd = res["id"]; alpha = idd[:, :, 3] > 0.5
    pid = np.where(alpha, np.rint(idd[:, :, 0] * 64).astype(int), 0)
    dep = np.where(alpha, idd[:, :, 1] * 1000.0, 1e6)
    nrm = res["nrm"][:, :, :3] * 2 - 1
    cols = [None] + [c for _, c in items]
    H, W = pid.shape
    img = np.zeros((H, W, 4), np.uint8)
    for i in range(1, len(cols)):
        m = pid == i
        img[m, :3] = FILL.get(cols[i], FILL["black"]); img[m, 3] = 255
    edge = np.zeros((H, W), bool); rededge = np.zeros((H, W), bool)
    isred = np.array([False] + [c == "red" for c in cols[1:]])
    for dy, dx in ((0, 1), (1, 0)):
        a_id, b_id = pid[: H - dy, : W - dx], pid[dy:, dx:]
        a_d, b_d = dep[: H - dy, : W - dx], dep[dy:, dx:]
        a_n, b_n = nrm[: H - dy, : W - dx], nrm[dy:, dx:]
        both = (a_id > 0) & (b_id > 0)
        e = (a_id != b_id) | (both & (np.abs(a_d - b_d) > 0.9)) | (both & ((a_n * b_n).sum(-1) < 0.90))
        red = e & (isred[a_id] | isred[b_id])
        edge[: H - dy, : W - dx] |= e; edge[dy:, dx:] |= e
        rededge[: H - dy, : W - dx] |= red; rededge[dy:, dx:] |= red
    img[edge, :3] = INK; img[edge, 3] = 255
    img[rededge, :3] = REDC
    return Image.fromarray(img, "RGBA"), size, pad

def sheet(pid):
    cfg = SHEETS[pid]; S = 1200 * SS
    im = Image.new("RGB", (S, S), BG); d = ImageDraw.Draw(im)
    for g in range(0, S, 24 * SS):
        d.line([(g, 0), (g, S)], fill=GRID, width=1); d.line([(0, g), (S, g)], fill=GRID, width=1)
    M = 24 * SS; d.rectangle([M, M, S - M, S - M], outline=FRAME, width=SS)
    f = lambda n, med=False: ImageFont.truetype(MONOM if med else MONO, int(n * SS))
    d.text((52 * SS, 44 * SS), f"DRAWING NS-{pid}", font=f(10.5), fill=MUTED)
    t = "ALL DIMENSIONS IN MM"; d.text((S - 52 * SS - d.textlength(t, font=f(10.5)), 44 * SS), t, font=f(10.5), fill=MUTED)
    # isometric
    iso = cfg.get("iso", dict(az=-32, el=30)); az, el = math.radians(iso["az"]), math.radians(iso["el"])
    dirv = np.array([math.sin(az) * math.cos(el), -math.cos(az) * math.cos(el), math.sin(el)])     # from target to camera
    fwd = -dirv; right = np.cross(fwd, [0, 0, 1]); right /= np.linalg.norm(right); up = np.cross(right, fwd)
    items = load("bp_" + pid)
    allv = np.vstack([t.vertices for t, _ in items]); pr = np.c_[allv @ right, allv @ up]
    ext = pr.max(0) - pr.min(0)
    s_iso = min(1000 * SS / ext[0], 420 * SS / ext[1])
    art, _, pad = lineart(items, right.tolist(), up.tolist(), fwd.tolist(), s_iso)
    im.paste(art, (S // 2 - art.size[0] // 2, (80 + 230) * SS - art.size[1] // 2), art)
    d.text((52 * SS, 556 * SS), cfg["cap"], font=f(9.5), fill=MUTED)
    # orthographic views of one piece
    oi = load("bpo_" + pid)
    v = np.vstack([t.vertices for t, _ in oi]); lo, hi = v.min(0), v.max(0); w, dp, h = (hi - lo)
    gap = 96 * SS
    lay_row = min((1010 * SS - 2 * gap) / (2 * w + dp), 390 * SS / max(dp, h))
    lay_stk = min((1010 * SS - gap) / (w + dp), (420 * SS - 70 * SS) / (dp + h))
    stacked = lay_stk > lay_row; s = min(max(lay_row, lay_stk), 5.2 * SS)
    views = {"TOP": ((1, 0, 0), (0, 1, 0), (0, 0, -1), w, dp), "FRONT": ((1, 0, 0), (0, 0, 1), (0, 1, 0), w, h), "SIDE": ((0, 1, 0), (0, 0, 1), (-1, 0, 0), dp, h)}
    arts = {k: lineart(oi, r_, u_, f_, s)[0] for k, (r_, u_, f_, _, _) in views.items()}
    x0 = 110 * SS; ytop = 610 * SS; ybot = 1050 * SS
    pos = {}
    if stacked:
        tot_h = (dp + h) * s + 70 * SS; y = ytop + (ybot - ytop - tot_h) / 2
        tot_w = (w + dp) * s + gap; x = x0 + (1010 * SS - tot_w) / 2
        pos["TOP"] = (x, y); pos["FRONT"] = (x, y + dp * s + 70 * SS); pos["SIDE"] = (x + w * s + gap, y + dp * s + 70 * SS)
    else:
        tot_w = (2 * w + dp) * s + 2 * gap; x = x0 + (1010 * SS - tot_w) / 2
        yb = ytop + (ybot - ytop) / 2 + max(dp, h) * s / 2
        pos["TOP"] = (x, yb - dp * s); pos["FRONT"] = (x + w * s + gap, yb - h * s); pos["SIDE"] = (x + 2 * w * s + 2 * gap, yb - h * s)
    fmt = lambda q: (f"{q:.1f}".rstrip("0").rstrip("."))
    for k, (r_, u_, f_, vw, vh) in views.items():
        a = arts[k]; x, y = pos[k]; im.paste(a, (int(x - pad), int(y - pad)), a)
        X0, X1, Y0, Y1 = x, x + vw * s, y, y + vh * s
        d.text((X1 + 8 * SS, Y0 - 4 * SS), k, font=f(8.5), fill=MUTED)
        yd = Y1 + 20 * SS                                           # width dimension under the view
        d.line([(X0, yd), (X1, yd)], fill=REDC, width=SS); d.line([(X0, yd - 5 * SS), (X0, yd + 5 * SS)], fill=REDC, width=SS); d.line([(X1, yd - 5 * SS), (X1, yd + 5 * SS)], fill=REDC, width=SS)
        t = fmt(vw); tw = d.textlength(t, font=f(10, True)); d.rectangle([(X0 + X1) / 2 - tw / 2 - 5 * SS, yd - 8 * SS, (X0 + X1) / 2 + tw / 2 + 5 * SS, yd + 8 * SS], fill=BG)
        d.text(((X0 + X1) / 2 - tw / 2, yd - 7 * SS), t, font=f(10, True), fill=INK)
        xd = X0 - 20 * SS                                           # height dimension left of the view
        d.line([(xd, Y0), (xd, Y1)], fill=REDC, width=SS); d.line([(xd - 5 * SS, Y0), (xd + 5 * SS, Y0)], fill=REDC, width=SS); d.line([(xd - 5 * SS, Y1), (xd + 5 * SS, Y1)], fill=REDC, width=SS)
        t = fmt(vh); tw = d.textlength(t, font=f(10, True))
        ti = Image.new("RGBA", (int(tw + 10 * SS), int(16 * SS)), BG + (255,)); ImageDraw.Draw(ti).text((5 * SS, 1 * SS), t, font=f(10, True), fill=INK)
        ti = ti.rotate(90, expand=True); im.paste(ti, (int(xd - ti.size[0] / 2), int((Y0 + Y1) / 2 - ti.size[1] / 2)))
    # title block
    ty0, ty1 = 1100 * SS, 1160 * SS; tx0, tx1 = 52 * SS, S - 52 * SS
    d.rectangle([tx0, ty0, tx1, ty1], outline=FRAME, width=SS, fill=BG)
    cols = [tx0 + 150 * SS, tx0 + 600 * SS, tx0 + 830 * SS, tx0 + 990 * SS]
    for cx in cols: d.line([(cx, ty0), (cx, ty1)], fill=FRAME, width=SS)
    pf = ImageFont.truetype(POP, 17 * SS); d.text((tx0 + 22 * SS, ty0 + 15 * SS), "NO SKIPS", font=pf, fill=INK)
    d.line([(tx0 + 22 * SS, ty0 + 44 * SS), (tx0 + 112 * SS, ty0 + 44 * SS)], fill=REDC, width=3 * SS)
    full = np.vstack([t.vertices for t, _ in items]); e = full.max(0) - full.min(0)
    cells = [("PIECE", f"{pid}  {cfg['piece']}"), ("ENVELOPE", f"{fmt(round(e[0], 1))} x {fmt(round(e[1], 1))} x {fmt(round(e[2], 1))}"), ("PARTS", cfg["parts"]), ("SHEET", f"{pid} / V2")]
    for (lab, val), cx in zip(cells, [cols[0], cols[1], cols[2], cols[3]]):
        d.text((cx + 14 * SS, ty0 + 10 * SS), lab, font=f(7.5), fill=MUTED)
        fs = 11
        while d.textlength(val, font=f(fs, True)) > ((tx1 if cx == cols[3] else cols[cols.index(cx) + 1]) - cx - 24 * SS) and fs > 7: fs -= 0.5
        d.text((cx + 14 * SS, ty0 + 30 * SS), val, font=f(fs, True), fill=INK)
    os.makedirs(f"{OUT}/bp", exist_ok=True)
    im = im.resize((1200, 1200), Image.LANCZOS); im.save(f"{OUT}/bp/bp_{pid}.png")
    print("SHEET", pid, flush=True)

if __name__ == "__main__":
    for p in sys.argv[1].split(","): sheet(p)
