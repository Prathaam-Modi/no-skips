"""No Skips order kit: engraved base for D8 B-Side, D2 Tape Case, D12 Rotary and D1 Wedge (the "Engrave" add-on).

The customer's text is cut 0.6 mm into the face that sits on the print bed: one colour, no supports, no extra colour change,
nothing else about the print changes. Letters are Poppins Bold caps, at least 4.0 mm tall (below that they smear on a 0.4 mm nozzle),
one or two lines. If the text would have to shrink below 4.0 mm to fit, the job stops with a message instead of printing it small.

  python engrave.py D8 --line1 "Home sweet home" --line2 "Since 2026" -o out_folder

Writes every part of the product (the engraved one replaced) with the usual BLACK / RED names, preview.png (the base seen from
underneath, as the customer will see it) and plan.json (objects, layer and settings for the Bambu project).
Needs: pip install trimesh shapely manifold3d matplotlib numpy
"""
import argparse, json, os, shutil, sys
import numpy as np, trimesh
import manifold3d as m3
from manifold3d import Manifold
from shapely.geometry import Polygon, box
from shapely.ops import unary_union
from shapely import affinity

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from code_to_print import fit_text, ext, to_mesh, check, ALLOWED, MIN_TEXT   # noqa: E402

DEPTH = 0.6            # engraving depth into the bed face
SOLID = {"sparse_infill_density": "100%", "sparse_infill_pattern": "zig-zag"}
BRIM = {"brim_type": "outer_only", "brim_width": "5"}

# box = text area on the bed face as the customer sees it from underneath (u right, v up), centre and size.
#   (cx, cy, w, h). rot 90 = the text runs along v. limit = characters a line (the site uses the same numbers).
SPECS = {
    "D8":  dict(item="D8 B-Side",     cut="D8_1_tray_BLACK.stl",    box=(0, 0, 112, 34),    rot=0,  cap=7.0, limit=18, where="underneath the tray"),
    "D2":  dict(item="D2 Tape Case",  cut="D2_1_tray_BLACK.stl",    box=(0, 0, 88, 36),     rot=0,  cap=5.5, limit=16, where="underneath the case"),
    "D12": dict(item="D12 Rotary",    cut="D12_1_plate_a_BLACK.stl", box=(0, 0, 50, 15),    rot=0,  cap=5.0, limit=12, where="on the back plate"),
    "D1":  dict(item="D1 Wedge",      cut="D1_1_stand_BLACK.stl",   box=(23.75, -1.5, 28.5, 63), rot=90, cap=4.5, limit=14, where="underneath the stand"),
}
# objects as the first-print projects have them: (object name, [(stl file, AMS slot, part name)], per-object settings)
PLANS = {
    "D8": dict(layer="0.20", over={"wall_loops": "3", "sparse_infill_density": "15%"}, objects=[
        ("D8 tray", [("D8_1_tray_BLACK.stl", 1, "tray"), ("D8_2_label_RED.stl", 2, "label")], {})]),
    "D2": dict(layer="0.20", over={"wall_loops": "3", "sparse_infill_density": "15%"}, objects=[
        ("D2 tray", [("D2_1_tray_BLACK.stl", 1, "tray")], {}),
        ("D2 lid", [("D2_2_lid_BLACK.stl", 1, "lid"), ("D2_3_label_inlay_RED.stl", 2, "label_inlay")], {})]),
    "D12": dict(layer="0.16", over=dict({"wall_loops": "3"}, **SOLID), objects=[
        ("D12 plate_a", [("D12_1_plate_a_BLACK.stl", 1, "plate_a")], {}),
        ("D12 plate_b", [("D12_2_plate_b_BLACK.stl", 1, "plate_b"), ("D12_2_pointer_inlay_RED.stl", 2, "pointer_inlay")], {}),
        ("D12 post_long 1", [("D12_5_post_long_BLACK_x2.stl", 1, "post_long")], BRIM),
        ("D12 post_long 2", [("D12_5_post_long_BLACK_x2.stl", 1, "post_long")], BRIM),
        ("D12 post_short 1", [("D12_4_post_short_BLACK_x2.stl", 1, "post_short")], BRIM),
        ("D12 post_short 2", [("D12_4_post_short_BLACK_x2.stl", 1, "post_short")], BRIM),
        ("D12 loop", [("D12_6_loop_BLACK.stl", 1, "loop")], {})] +
        [("D12 spacer %d" % i, [("D12_7_spacer_BLACK_x6.stl", 1, "spacer")], {}) for i in range(1, 7)]),
    "D1": dict(layer="0.20", over={"wall_loops": "3", "sparse_infill_density": "15%"}, objects=[
        ("D1 Wedge body (upright, no supports)", [("D1_1_stand_BLACK.stl", 1, "stand")], {"sparse_infill_density": "12%", "wall_loops": "3"}),
        ("D1 Wedge lip", [("D1_2_lip_RED.stl", 2, "lip")], dict(SOLID, wall_loops="3"))]),
}


def load(path):
    t = trimesh.load(path, force="mesh", process=True)
    return Manifold(m3.Mesh(vert_properties=np.asarray(t.vertices, dtype=np.float32), tri_verts=np.asarray(t.faces, dtype=np.uint32)))


def section(man, z):
    """Material at height z as a shapely shape (outer outlines minus holes)."""
    g = Polygon()
    for ring in man.slice(z).to_polygons():
        if len(ring) >= 3:
            g = g.symmetric_difference(Polygon(ring).buffer(0))
    return g


def layout(lines, spec):
    """Text in the customer's view (seen from underneath). Returns a shapely shape."""
    cx, cy, w, h = spec["box"]
    rot = spec["rot"]
    wl, hl = (w, h) if rot == 0 else (h, w)           # along the text, across the lines
    cap = spec["cap"]; pitch = cap * 1.75
    n = len(lines)
    ys = [(n - 1) / 2 * pitch - i * pitch for i in range(n)]
    shapes = []
    for s, y in zip(lines, ys):
        g = fit_text(s, cap, wl * 0.96, 0, y)
        shapes.append(g)
    block = unary_union(shapes)
    if block.bounds[3] - block.bounds[1] > hl:
        sys.exit("Two lines of text do not fit the base of the %s. Shorten it, or use one line." % spec["item"])
    if rot:
        block = affinity.rotate(block, rot, origin=(0, 0))
    return affinity.translate(block, cx, cy)


def preview(path, spec, outline, view_text, l1, l2):
    import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(6.5, 4.2))
    out = affinity.scale(outline, -1, 1, origin=(0, 0))                 # seen from underneath
    for p in ([out] if out.geom_type == "Polygon" else list(out.geoms)):
        ax.fill(*p.exterior.xy, color="#161514")
        for i in p.interiors: ax.fill(*i.xy, color="white")
    for p in ([view_text] if view_text.geom_type == "Polygon" else list(view_text.geoms)):
        ax.fill(*p.exterior.xy, color="#f0ebe0")
        for i in p.interiors: ax.fill(*i.xy, color="#161514")
    x0, y0, x1, y1 = out.bounds
    ax.set_xlim(x0 - 3, x1 + 3); ax.set_ylim(y0 - 3, y1 + 3); ax.set_aspect("equal"); ax.axis("off")
    ax.set_title("%s: engraved %s\n%s" % (spec["item"], spec["where"], " / ".join(x for x in (l1, l2) if x)), fontsize=10)
    fig.savefig(path, dpi=160, bbox_inches="tight", facecolor="white"); plt.close(fig)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("base", choices=sorted(SPECS)); ap.add_argument("--line1", required=True); ap.add_argument("--line2", default="")
    ap.add_argument("-o", "--out", default="print_files")
    a = ap.parse_args()
    spec = SPECS[a.base]
    l1, l2 = " ".join(a.line1.split()), " ".join(a.line2.split())
    check("Engraving line one", l1, spec["limit"])
    if l2: check("Engraving line two", l2, spec["limit"])
    src = os.path.join(HERE, "engrave", a.base)
    os.makedirs(a.out, exist_ok=True)
    cut_man = load(os.path.join(src, spec["cut"]))
    view = layout([x for x in (l1, l2) if x], spec)                       # as seen from underneath
    world = affinity.scale(view, -1, 1, origin=(0, 0))                    # as cut into the bed face (mirrored in x)
    mat = section(cut_man, 0.3)
    if world.is_empty or not world.within(mat.buffer(-0.35)):
        sys.exit("The engraving does not fit on the flat base of the %s. Shorten the text." % spec["item"])
    engraved = cut_man - ext(world, DEPTH + 0.02, -0.02)
    to_mesh(engraved).export(os.path.join(a.out, spec["cut"]))
    print("engraved", spec["cut"], "%.2f mm deep" % DEPTH)
    for fn in sorted(os.listdir(src)):
        if fn != spec["cut"] and fn.endswith(".stl"):
            shutil.copy(os.path.join(src, fn), os.path.join(a.out, fn))
    preview(os.path.join(a.out, "preview.png"), spec, mat, view, l1, l2)
    plan = PLANS[a.base]
    json.dump({"layer": plan["layer"], "over": plan["over"],
               "objects": [{"name": n, "parts": [list(p) for p in parts], "settings": st} for n, parts, st in plan["objects"]]},
              open(os.path.join(a.out, "plan.json"), "w"), indent=1)
    print("wrote preview.png and plan.json")


if __name__ == "__main__":
    main()
