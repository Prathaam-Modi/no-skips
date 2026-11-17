"""Bambu Studio project 3MF builder for No Skips orders.

seed()   writes a Bambu-flavoured project .3mf: every object and part placed on the bed (our own layout,
         so the file is right even without the slicer), parts assigned to AMS Lite slots, process
         settings saved in the project.
slice_() runs the Bambu Studio command line on that project and returns the sliced .gcode.3mf with
         the predicted time and grams.

Slots for the whole range: 1 Black, 2 Red, 3 Ivory.
Bambu Studio is found through BAMBU_STUDIO_DIR (an extracted AppImage, the folder holding AppRun and
bin/), default .bambu/squashfs-root in the repo (where the workflow extracts it).
"""
import json, math, os, re, shutil, subprocess, zipfile
import xml.etree.ElementTree as ET
from xml.sax.saxutils import escape

import numpy as np
import trimesh

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROFILES = os.path.join(ROOT, "profiles")
COLOURS = ["#000000", "#C12E1F", "#FFFFFF"]          # slot 1 Black, 2 Red, 3 Ivory
BED = 256.0                                          # A1 printable area 256 x 256
MARGIN = 6.0                                         # keep clear of the bed edge
GAP = 6.0                                            # between objects
# Prime tower (wipe_tower_x 15, y 211, width 35 in the A1 profile) plus room for its brim and depth.
KEEPOUT = (0.0, 168.0, 66.0, BED)
PLATE_GAP = 1.0 / 5.0                                # Bambu Studio LOGICAL_PART_PLATE_GAP
PROCESS = {"0.12": "process_012.json", "0.16": "process_016.json", "0.20": "process_020.json"}
META_KEYS = {"name", "inherits", "from", "type", "instantiation", "setting_id", "compatible_printers",
             "compatible_printers_condition", "version", "is_custom_defined", "print_settings_id"}


def bambu_dir():
    return os.environ.get("BAMBU_STUDIO_DIR") or os.path.join(ROOT, ".bambu", "squashfs-root")


# ---------------------------------------------------------------- layout
def _cols(count):
    """Bambu Studio compute_colum_count: plates are laid out in a near-square grid."""
    v = math.sqrt(count); r = round(v)
    return int(r + 1 if v > r else r)


def plate_origin(i, count):
    cols = _cols(count)
    return ((i % cols) * BED * (1 + PLATE_GAP), -(i // cols) * BED * (1 + PLATE_GAP))


def _hits(x, y, w, h, rects):
    for (rx0, ry0, rx1, ry1) in rects:
        if x < rx1 + GAP and x + w + GAP > rx0 and y < ry1 + GAP and y + h + GAP > ry0:
            return (rx0, ry0, rx1, ry1)
    return None


def layout(sizes, keepout=True):
    """sizes: [(w, h)] footprints in mm. Returns [(plate_index, x0, y0)] lower-left corners on the bed.
    Bottom-left fill, largest first, opens a new plate when one is full."""
    order = sorted(range(len(sizes)), key=lambda i: (-sizes[i][1], -sizes[i][0]))
    plates = []                                       # per plate: list of placed rects
    out = [None] * len(sizes)
    lo, hi = MARGIN, BED - MARGIN
    for i in order:
        w, h = sizes[i]
        if w > hi - lo or h > hi - lo:
            raise ValueError("part of %.0f x %.0f mm does not fit the A1 bed" % (w, h))
        placed = False
        for p, rects in enumerate(plates + [[]]):
            if p == len(plates):
                plates.append(rects)
            blocked = rects + ([KEEPOUT] if keepout else [])
            y = lo
            while y + h <= hi and not placed:
                x = lo
                while x + w <= hi:
                    r = _hits(x, y, w, h, blocked)
                    if r is None:
                        rects.append((x, y, x + w, y + h)); out[i] = (p, x, y); placed = True
                        break
                    x = r[2] + GAP                    # jump past the blocker
                y += 1.0
            if placed:
                break
            if not rects:                             # an empty plate could not take it
                raise ValueError("part does not fit the A1 bed")
    return out, len(plates)


# ---------------------------------------------------------------- 3MF
def _process(layer, over):
    d = json.load(open(os.path.join(PROFILES, PROCESS[layer])))
    d.update(over)
    return d


def seed(path, objects, layer, over):
    """objects: list of dict(name, parts=[(stl_path, slot, part_name)], settings={}).
    Writes a project 3MF with every object placed. Returns the number of plates used."""
    meshes = []
    for ob in objects:
        ms = [trimesh.load(f, process=True) for (f, _, _) in ob["parts"]]
        lo = np.min([m.bounds[0] for m in ms], axis=0); hi = np.max([m.bounds[1] for m in ms], axis=0)
        meshes.append((ms, lo, hi))
    pos, nplates = layout([(hi[0] - lo[0], hi[1] - lo[1]) for (_, lo, hi) in meshes])

    res, build = [], []
    cfg = ['<?xml version="1.0" encoding="UTF-8"?>', "<config>"]
    oid = 0; per_plate = [[] for _ in range(nplates)]
    for k, (ob, (ms, lo, hi), (p, x0, y0)) in enumerate(zip(objects, meshes, pos)):
        pids = []
        for (f, slot, pn), m in zip(ob["parts"], ms):
            oid += 1; pids.append((oid, slot, pn, len(m.faces)))
            v = "".join('<vertex x="%.5f" y="%.5f" z="%.5f"/>' % tuple(q) for q in m.vertices)
            t = "".join('<triangle v1="%d" v2="%d" v3="%d"/>' % tuple(q) for q in m.faces)
            res.append(f'<object id="{oid}" type="model"><mesh><vertices>{v}</vertices><triangles>{t}</triangles></mesh></object>')
        oid += 1; wid = oid
        res.append(f'<object id="{wid}" type="model"><components>' + "".join(
            f'<component objectid="{q[0]}" transform="1 0 0 0 1 0 0 0 1 0 0 0"/>' for q in pids) + "</components></object>")
        ox, oy = plate_origin(p, nplates)
        tx, ty, tz = ox + x0 - lo[0], oy + y0 - lo[1], -lo[2]
        build.append(f'<item objectid="{wid}" transform="1 0 0 0 1 0 0 0 1 {tx:.4f} {ty:.4f} {tz:.4f}" printable="1"/>')
        cfg += [f'  <object id="{wid}">', f'    <metadata key="name" value="{escape(ob["name"])}"/>',
                f'    <metadata key="extruder" value="{pids[0][1]}"/>']
        for kk, vv in ob.get("settings", {}).items():
            cfg.append(f'    <metadata key="{kk}" value="{escape(str(vv))}"/>')
        for (pid, slot, pn, nf) in pids:
            cfg += [f'    <part id="{pid}" subtype="normal_part">', f'      <metadata key="name" value="{escape(pn)}"/>',
                    '      <metadata key="matrix" value="1 0 0 0 0 1 0 0 0 0 1 0 0 0 0 1"/>',
                    f'      <metadata key="extruder" value="{slot}"/>',
                    f'      <mesh_stat face_count="{nf}" edges_fixed="0" degenerate_facets="0" facets_removed="0" facets_reversed="0" backwards_edges="0"/>',
                    "    </part>"]
        cfg.append("  </object>"); per_plate[p].append(wid)
    n = 0
    for p, wids in enumerate(per_plate):
        cfg += ["  <plate>", f'    <metadata key="plater_id" value="{p + 1}"/>', '    <metadata key="plater_name" value=""/>',
                '    <metadata key="locked" value="false"/>']
        for w in wids:
            cfg += ["    <model_instance>", f'      <metadata key="object_id" value="{w}"/>', '      <metadata key="instance_id" value="0"/>',
                    f'      <metadata key="identify_id" value="{100 + n}"/>', "    </model_instance>"]
            n += 1
        cfg.append("  </plate>")
    cfg.append("</config>")

    # project settings: the range's machine + filament config, with this job's process settings
    proj = json.load(open(os.path.join(PROFILES, "seed_project_settings.config")))
    proc = _process(layer, over)
    for kk, vv in proc.items():
        if kk in proj and kk not in META_KEYS:
            proj[kk] = vv
    proj["print_settings_id"] = proc.get("name", proj.get("print_settings_id"))
    proj["filament_colour"] = COLOURS

    model = ('<?xml version="1.0" encoding="UTF-8"?>\n<model unit="millimeter" xml:lang="en-US" '
             'xmlns="http://schemas.microsoft.com/3dmanufacturing/core/2015/02" xmlns:BambuStudio="http://schemas.bambulab.com/package/2021">\n'
             '<metadata name="Application">BambuStudio-02.02.02.56</metadata>\n<metadata name="BambuStudio:3mfVersion">1</metadata>\n'
             "<resources>\n" + "\n".join(res) + "\n</resources>\n<build>\n" + "\n".join(build) + "\n</build>\n</model>\n")
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("[Content_Types].xml", '<?xml version="1.0" encoding="UTF-8"?>\n<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
                   '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
                   '<Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/>'
                   '<Default Extension="png" ContentType="image/png"/></Types>')
        z.writestr("_rels/.rels", '<?xml version="1.0" encoding="UTF-8"?>\n<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
                   '<Relationship Target="/3D/3dmodel.model" Id="rel-1" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>')
        z.writestr("3D/3dmodel.model", model)
        z.writestr("Metadata/project_settings.config", json.dumps(proj, indent=4))
        z.writestr("Metadata/model_settings.config", "\n".join(cfg))
    return nplates


# ---------------------------------------------------------------- slicing
def slice_(project, out_path, layer, over, timeout=540):
    """Slice every plate of project with the Bambu Studio CLI. Returns dict(ok, time_s, grams, error)."""
    B = bambu_dir(); exe = os.path.join(B, "bin", "bambu-studio")
    if not os.path.exists(exe):
        return dict(ok=False, error="Bambu Studio not found at %s" % B)
    outdir = os.path.dirname(os.path.abspath(out_path))
    work = os.path.join(outdir, ".slice_tmp"); shutil.rmtree(work, ignore_errors=True); os.makedirs(work)
    pj = os.path.join(work, "process.json")
    d = _process(layer, over); d["from"] = "system"; json.dump(d, open(pj, "w"), indent=1)
    P = PROFILES
    cmd = [exe, "--debug", "1", "--load-settings", f"{P}/machine.json;{pj}",
           "--load-filaments", ";".join([f"{P}/pla_basic.json"] * 3),
           "--curr-bed-type", "Textured PEI Plate", "--filament-colour", ";".join(COLOURS),
           "--filament-map", "1,1,1", "--allow-multicolor-oneplate", "--slice", "0",
           "--export-3mf", os.path.basename(out_path), "--outputdir", work, os.path.abspath(project)]
    env = dict(os.environ, LC_ALL="C", LD_LIBRARY_PATH=os.path.join(B, "bin"))
    try:
        r = subprocess.run(cmd, env=env, capture_output=True, text=True, timeout=timeout, cwd=work)
        log = (r.stdout or "") + (r.stderr or "")
    except subprocess.TimeoutExpired:
        shutil.rmtree(work, ignore_errors=True)
        return dict(ok=False, error="Bambu Studio timed out after %d s" % timeout)
    rj = os.path.join(work, "result.json")
    res = json.load(open(rj)) if os.path.exists(rj) else {"return_code": r.returncode, "error_string": log[-400:]}
    produced = os.path.join(work, os.path.basename(out_path))
    if res.get("return_code") != 0 or not os.path.exists(produced):
        shutil.rmtree(work, ignore_errors=True)
        return dict(ok=False, error="Bambu Studio: %s (code %s)" % (str(res.get("error_string", "")).strip()[:300], res.get("return_code")))
    shutil.move(produced, out_path); shutil.rmtree(work, ignore_errors=True)
    t, g, plates = read_sliced(out_path)
    return dict(ok=True, time_s=t, grams=g, plates=plates)


def read_sliced(path):
    """Total predicted seconds and grams over all plates of a .gcode.3mf."""
    with zipfile.ZipFile(path) as z:
        root = ET.fromstring(z.read("Metadata/slice_info.config"))
    t = g = 0.0; n = 0
    for pl in root.iter("plate"):
        md = {m.get("key"): m.get("value") for m in pl.findall("metadata")}
        t += float(md.get("prediction", 0) or 0); g += float(md.get("weight", 0) or 0); n += 1
    return int(round(t)), round(g, 1), n
