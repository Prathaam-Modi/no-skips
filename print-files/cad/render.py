"""Studio renders of scenes written by build.py. Usage: python3 render.py [--draft] scene[,scene...]"""
import sys, os, json, math
import numpy as np, bpy, trimesh
from mathutils import Vector

OUT = os.environ.get("NS_OUT", "/home/claude/out")
COL = {"black": (0.016, 0.015, 0.014, 0.52), "ivory": (0.60, 0.555, 0.47, 0.6), "red": (0.56, 0.022, 0.03, 0.5),
       "prop": (0.085, 0.085, 0.085, 0.35), "prop2": (0.50, 0.48, 0.44, 0.5), "brass": (0.70, 0.50, 0.17, 0.30), "steel": (0.62, 0.63, 0.66, 0.28), "sofa": (0.30, 0.27, 0.235, 1.0), "glass": (0.9, 0.93, 0.95, 0.05), "blue": (0.03, 0.17, 0.55, 0.32), "leaf": (0.05, 0.16, 0.045, 0.55), "soil": (0.045, 0.03, 0.02, 0.95)}
# scene: az (deg, 0 = straight on from the front, + = camera to the right), el, zoom (1 = fit), optional look-at shift
SHOTS = {
 "songtag": dict(az=-22, el=52, zoom=1.02), "songtag_sides": dict(az=0, el=62, zoom=1.0), "nametag": dict(az=-22, el=52, zoom=1.02),
 "plate": dict(az=-24, el=14, zoom=1.0), "plate_wave": dict(az=-24, el=14, zoom=1.0), "plate_build": dict(az=-18, el=48, zoom=1.0),
 "horn_slide": dict(az=-38, el=26, zoom=0.86), "standees": dict(az=-26, el=20, zoom=1.02), "standee_build": dict(az=-16, el=46, zoom=1.0),
 "fold": dict(az=-52, el=16, zoom=1.0), "fold_bare": dict(az=-52, el=20, zoom=1.0), "fold_flat": dict(az=-24, el=46, zoom=1.0),
 "channel": dict(az=-28, el=24, zoom=1.0), "channel_build": dict(az=-28, el=26, zoom=1.0),
 "bside": dict(az=-20, el=40, zoom=1.0), "bside_bare": dict(az=-20, el=40, zoom=1.0),
 "studio_set": dict(az=-24, el=40, zoom=1.0), "knob": dict(az=-20, el=34, zoom=1.0), "rail": dict(az=-22, el=12, zoom=1.0),
 "coasters": dict(az=-18, el=38, zoom=1.0), "amp": dict(az=-24, el=16, zoom=1.0), "amp_open": dict(az=-30, el=22, zoom=1.0),
 "riser": dict(az=24, el=14, zoom=1.0), "run": dict(az=-14, el=50, zoom=1.0), "phonestand": dict(az=-34, el=16, zoom=1.0), "horn_rings": dict(az=-42, el=10, zoom=1.0), "wedge": dict(az=-35, el=18, zoom=1.0), "wedge_phone": dict(az=-35, el=16, zoom=1.0), "wedge_back": dict(az=145, el=18, zoom=1.0), "wedge_build": dict(az=-30, el=22, zoom=1.0),
 "phonestand_horn_exploded": dict(az=-40, el=22, zoom=1.0), "cassettebox": dict(az=-20, el=40, zoom=1.0), "cassettebox_open": dict(az=-20, el=42, zoom=1.0),
 "vinylstand": dict(az=-38, el=18, zoom=1.0), "vinylstand_record": dict(az=-38, el=16, zoom=1.0), "headphonestand_bare": dict(az=-26, el=12, zoom=1.0),
 "studio_mini": dict(az=-14, el=30, zoom=1.0), "studio_mini2": dict(az=-14, el=30, zoom=1.0), "knob_build": dict(az=-18, el=24, zoom=1.0),
 "rail_build": dict(az=-30, el=14, zoom=1.0), "amp_build": dict(az=-34, el=22, zoom=1.0), "phonestand_horn_seat": dict(az=-14, el=66, zoom=1.25),
 "vinylstand_build": dict(az=-36, el=22, zoom=1.0), "headphonestand": dict(az=-24, el=12, zoom=1.0), "headphonestand_build": dict(az=-26, el=12, zoom=1.0),
 "eject": dict(az=-24, el=18, zoom=1.0), "eject_open": dict(az=-30, el=16, zoom=1.0), "eject_build": dict(az=-36, el=20, zoom=1.0),
 "standby_bare": dict(az=-34, el=20, zoom=1.0), "standby": dict(az=-40, el=16, zoom=1.0), "standby_build": dict(az=-30, el=22, zoom=1.0),
 "rotary": dict(az=-18, el=48, zoom=1.0), "rotary_open": dict(az=-18, el=50, zoom=1.0),
 "rotary_s1": dict(az=-24, el=30, zoom=0.78), "rotary_s2": dict(az=-30, el=36, zoom=0.7), "rotary_s3": dict(az=-30, el=32, zoom=0.72), "rotary_s4": dict(az=-18, el=52, zoom=0.72), "rotary_s5": dict(az=-30, el=34, zoom=0.74), "rotary_s6": dict(az=-24, el=40, zoom=0.8), "rotary_build": dict(az=-24, el=30, zoom=1.0),
 "crate": dict(az=-26, el=16, zoom=1.0), "crate_open": dict(az=-26, el=18, zoom=1.0), "crate_full": dict(az=-26, el=18, zoom=1.0), "crate_bare": dict(az=-24, el=14, zoom=1.0),
 "crate_section": dict(az=90, el=6, zoom=1.0), "crate_build": dict(az=-30, el=30, zoom=0.9),
 "crate_s1": dict(az=-14, el=40, zoom=1.12), "crate_back": dict(az=152, el=18, zoom=1.0), "crate_s2": dict(az=-30, el=26, zoom=1.0), "crate_s3": dict(az=-32, el=22, zoom=1.0), "crate_s4": dict(az=-28, el=22, zoom=1.0), "crate_s5": dict(az=-28, el=20, zoom=1.0),
 "cover": dict(az=-26, el=24, zoom=1.0), "cover_lifted": dict(az=-30, el=20, zoom=1.0), "cover_top": dict(az=0, el=89, zoom=1.0), "cover_tiles": dict(az=-24, el=40, zoom=1.0),
 "perch": dict(az=-36, el=30, zoom=1.0, focus=("black", "red", "glass", "prop")), "perch_flat": dict(az=-26, el=44, zoom=1.0),
 "terrace": dict(az=-24, el=16, zoom=0.95, soft=0.6), "twist": dict(az=-24, el=16, zoom=0.95, soft=0.85), "echo": dict(az=-24, el=16, zoom=0.95, soft=0.6),
 "terrace_black": dict(az=-24, el=16, zoom=0.95, soft=0.85), "twist_black": dict(az=-24, el=16, zoom=0.95, soft=0.85), "echo_black": dict(az=-24, el=16, zoom=0.95, soft=0.85),
 "terrace_bare": dict(az=-20, el=26, zoom=1.0, soft=0.6), "twist_bare": dict(az=-20, el=26, zoom=1.0, soft=0.6), "echo_bare": dict(az=-20, el=26, zoom=1.0, soft=0.6),
 "planters_family": dict(az=-14, el=14, zoom=1.0, soft=0.7),
 "crosses": dict(az=-20, el=48, zoom=1.0, soft=0.7), "crosses_one": dict(az=-22, el=40, zoom=1.0, soft=0.7), "crosses_stack": dict(az=-30, el=22, zoom=1.0, soft=0.7), "pawns": dict(az=-30, el=20, zoom=1.0, soft=0.7),
 "tangram": dict(az=-20, el=50, zoom=1.0, soft=0.7), "tangram_loose": dict(az=-20, el=52, zoom=0.9, soft=0.7),
 "ripple": dict(az=-24, el=34, zoom=1.0, soft=0.55), "ripple_black": dict(az=-24, el=34, zoom=1.0, soft=0.8), "ripple_top": dict(az=-8, el=62, zoom=1.0, soft=0.5), "ripple_black_top": dict(az=-8, el=62, zoom=1.0, soft=0.8),
}

def mat(name):
    r, g, b, rough = COL[name]
    m = bpy.data.materials.new(name); m.use_nodes = True
    p = m.node_tree.nodes["Principled BSDF"]
    p.inputs["Base Color"].default_value = (r, g, b, 1); p.inputs["Roughness"].default_value = rough
    if name in ("brass", "steel"): p.inputs["Metallic"].default_value = 0.9
    if name == "glass":
        p.inputs["Transmission Weight"].default_value = 1.0; p.inputs["IOR"].default_value = 1.45
    else:
        p.inputs["Specular IOR Level"].default_value = 0.35
    return m

def render(scene_name, draft=False, res=880):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    sd = f"{OUT}/scenes/{scene_name}"; meta = json.load(open(sd + "/meta.json"))
    mats = {}; pts = []; fpts = []
    shot = SHOTS.get(scene_name, dict(az=-28, el=30, zoom=1.0)); focus = shot.get("focus")
    for fn, c in meta:
        t = trimesh.load(f"{sd}/{fn}", process=True)
        me = bpy.data.meshes.new(fn); me.from_pydata((t.vertices * 0.001).tolist(), [], t.faces.tolist()); me.update()
        me.shade_smooth()
        try: me.set_sharp_from_angle(angle=math.radians(32))
        except Exception: pass
        ob = bpy.data.objects.new(fn, me); sc.collection.objects.link(ob)
        if c not in mats: mats[c] = mat(c)
        me.materials.append(mats[c])
        pts.append(t.bounds * 0.001)
        if focus is None or c in focus: fpts.append(t.bounds * 0.001)
    b = np.array(fpts); lo = b[:, 0, :].min(0); hi = b[:, 1, :].max(0)
    ctr = (lo + hi) / 2; rad = float(np.linalg.norm(hi - lo) / 2)
    # floor
    bpy.ops.mesh.primitive_plane_add(size=60, location=(0, 0, float(np.array(pts)[:, 0, 2].min()) - 0.00005))
    fl = bpy.context.object; fm = bpy.data.materials.new("floor"); fm.use_nodes = True
    fp = fm.node_tree.nodes["Principled BSDF"]; fp.inputs["Base Color"].default_value = (0.78, 0.76, 0.72, 1); fp.inputs["Roughness"].default_value = 0.9
    fp.inputs["Specular IOR Level"].default_value = 0.1
    fl.data.materials.append(fm); fl.is_shadow_catcher = True; r0 = sc.render; r0.film_transparent = True
    w = bpy.data.worlds.new("w"); sc.world = w; w.use_nodes = True
    bg = w.node_tree.nodes["Background"]; bg.inputs[0].default_value = (0.80, 0.78, 0.74, 1); bg.inputs[1].default_value = 0.42
    # camera
    az, el = math.radians(shot["az"]), math.radians(shot["el"])
    cam = bpy.data.cameras.new("c"); cam.lens = 85; cam.sensor_width = 36
    co = bpy.data.objects.new("c", cam); sc.collection.objects.link(co); sc.camera = co
    fov = 2 * math.atan(18 / 85)
    dist = rad / math.sin(fov / 2) * 1.08 / shot.get("zoom", 1.0)
    d = Vector((math.sin(az) * math.cos(el), -math.cos(az) * math.cos(el), math.sin(el)))
    tgt = Vector(ctr.tolist()) + Vector(shot.get("shift", (0, 0, 0))) * rad
    co.location = tgt + d * dist
    co.rotation_euler = (tgt - co.location).to_track_quat("-Z", "Y").to_euler()
    cam.clip_start = 0.01; cam.clip_end = 100
    # lights: big soft key from upper left, low fill from the right, a rim from behind
    def area(loc, size, power, color=(1, 1, 1)):
        l = bpy.data.lights.new("l", "AREA"); l.size = size * rad; l.energy = power * rad * rad; l.color = color
        o = bpy.data.objects.new("l", l); sc.collection.objects.link(o)
        o.location = tgt + Vector(loc) * rad; o.rotation_euler = (tgt - o.location).to_track_quat("-Z", "Y").to_euler()
    sf = shot.get("soft", 1.0)
    area((-2.6, -2.2, 3.6), 3.2, 380 * sf, (1.0, 0.97, 0.93))
    area((3.2, -1.6, 1.6), 3.0, 95 * (1.5 if sf < 1 else 1))
    area((0.6, 3.4, 2.6), 2.4, 170)
    r = sc.render; r.engine = "CYCLES"; r.resolution_x = r.resolution_y = res; r.resolution_percentage = 50 if draft else 100
    sc.cycles.samples = 24 if draft else 72; sc.cycles.use_denoising = True; sc.cycles.device = "CPU"
    try: sc.cycles.denoiser = "OPENIMAGEDENOISE"
    except Exception: pass
    sc.cycles.max_bounces = 6; sc.cycles.use_adaptive_sampling = True; sc.cycles.adaptive_threshold = 0.03
    sc.view_settings.view_transform = "Standard"; sc.view_settings.look = "None"
    sc.view_settings.exposure = 0.0; sc.view_settings.gamma = 1.0
    r.image_settings.file_format = "PNG"; r.filepath = f"{OUT}/r/{scene_name}.png"
    os.makedirs(f"{OUT}/r", exist_ok=True)
    bpy.ops.render.render(write_still=True)
    from PIL import Image, ImageFilter
    im = Image.open(r.filepath).convert("RGBA"); n = im.size[0]
    yy, xx = np.mgrid[0:n, 0:n] / (n - 1.0)
    v = 1.0 - 0.10 * np.clip(((xx - 0.5) ** 2 + (yy - 0.45) ** 2) / 0.5, 0, 1)
    bgc = np.array([228, 225, 219], float)[None, None, :] * v[:, :, None]
    bgi = Image.fromarray(bgc.astype(np.uint8)).convert("RGBA")
    Image.alpha_composite(bgi, im).convert("RGB").save(f"{OUT}/r/{scene_name}.jpg", quality=92)
    print("DONE", scene_name, flush=True)

if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    for s in args[0].split(","): render(s, "--draft" in sys.argv)
