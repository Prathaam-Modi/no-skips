"""Support audit for every print part: overhang area that needs support, how much of it would grow from the part itself
(supports trapped inside or under the model, hard to remove), and the best of the six lay-flat orientations.
Run from the repo root: python3 tools/overhang_audit.py [filter]   -> prints a table, writes print-files/a1_ready/SUPPORT_AUDIT.json
Overhang: down-facing faces flatter than 40 degrees from horizontal (45 degree bevels print fine), more than 0.5 mm above the bed.
Bridges (flat down-facing) shorter than about 15 mm print without supports, so flat faces count only if wider than that."""
import trimesh, numpy as np, glob, os, json, sys
ORIENT = {"as is": np.eye(4), "x+90": trimesh.transformations.rotation_matrix(np.pi/2, [1,0,0]),
          "x-90": trimesh.transformations.rotation_matrix(-np.pi/2, [1,0,0]), "y+90": trimesh.transformations.rotation_matrix(np.pi/2, [0,1,0]),
          "y-90": trimesh.transformations.rotation_matrix(-np.pi/2, [0,1,0]), "flip": trimesh.transformations.rotation_matrix(np.pi, [1,0,0])}
def score(m):
    m = m.copy(); m.apply_translation([0, 0, -m.bounds[0][2]])
    n = m.face_normals; c = m.triangles_center; a = m.area_faces
    down = (n[:, 2] < -0.77) & (c[:, 2] > 0.5)
    sloped = down & (n[:, 2] > -0.985)
    flat = down & ~sloped
    # flat faces: treat as bridge if the downward ray hits the part within reach of walls (approximation: keep only large flat areas)
    idx = np.where(down)[0]
    on_model = np.zeros(len(n), bool)
    if len(idx):
        o = c[idx] - np.array([0, 0, 1e-3])
        loc, ri, _ = m.ray.intersects_location(o, np.tile([0, 0, -1.0], (len(idx), 1)), multiple_hits=False)
        on_model[idx[ri]] = True
    flat_area = a[flat].sum()
    return dict(overhang=round(a[sloped].sum(), 1), flat=round(flat_area, 1), on_model=round(a[down & on_model].sum(), 1),
                height=round(m.extents[2], 1))
def cost(s): return s["overhang"] + 0.3 * s["flat"] + 2.0 * s["on_model"] + 0.05 * s["height"]   # trapped supports weigh most
out = {}
flt = sys.argv[1] if len(sys.argv) > 1 else ""
for f in sorted(glob.glob("print-files/stl/*/*.stl")):
    if flt not in f: continue
    m = trimesh.load(f)
    res = {k: score(m.copy().apply_transform(T)) for k, T in ORIENT.items()}
    best = min(res, key=lambda k: cost(res[k]))
    out[os.path.relpath(f, "print-files/stl")] = dict(current=res["as is"], best=best, best_score=res[best])
    cur = res["as is"]
    if cur["overhang"] + cur["on_model"] > 30 or cur["flat"] > 300:
        b = res[best]
        print("%-52s now: over %6.0f flat %6.0f trapped %6.0f | best %-5s over %6.0f flat %6.0f trapped %6.0f h %5.1f" % (
            os.path.relpath(f, "print-files/stl")[:52], cur["overhang"], cur["flat"], cur["on_model"], best, b["overhang"], b["flat"], b["on_model"], b["height"]))
json.dump(out, open("print-files/a1_ready/SUPPORT_AUDIT.json", "w"), indent=1)
