"""Rebuild Bambu projects in print-files/a1_ready/<folder> from the current STLs, keeping objects, slots and settings, and queue them for slicing.
Run from the repo root: python3 tools/reseed_projects.py D10_eject D12_rotary"""
import sys, os, re, json, zipfile, glob
import xml.etree.ElementTree as ET
sys.path.insert(0, "tools/orders/print-repo/tools")
import bambu3mf as b
A = "print-files/a1_ready"; S = "print-files/stl"
REN = {"tag_backup": "tag_bkup", "tag_backup_word": "tag_bkup_word"}
def stl_for(folder, part):
    part = REN.get(part, part)
    for f in sorted(glob.glob(f"{S}/{folder}/*.stl")):
        if re.match(rf"^[A-Z0-9]+(?:_\d\d)?_\d+_{re.escape(part)}_[A-Z]+(_x\d+)?\.stl$", os.path.basename(f)): return f
    raise SystemExit(f"no stl for {folder} {part}")
jobs = []
NOSUP = "--no-supports" in sys.argv   # drop per-object support settings (part redesigned to print without supports)
for folder in [a for a in sys.argv[1:] if not a.startswith("--")]:
    for p in sorted(glob.glob(f"{A}/{folder}/*.3mf")):
        if p.endswith(".gcode.3mf"): continue
        z = zipfile.ZipFile(p)
        ps = json.loads(z.read("Metadata/project_settings.config"))
        layer = ps["layer_height"]; layer = layer[0] if isinstance(layer, list) else layer
        layer = "%.2f" % float(layer)
        over = {"wall_loops": str(ps["wall_loops"]), "sparse_infill_density": str(ps["sparse_infill_density"])}
        if over["sparse_infill_density"] == "100%": over["sparse_infill_pattern"] = "zig-zag"   # Bambu refuses gyroid at 100%
        root = ET.fromstring(z.read("Metadata/model_settings.config"))
        objs = []
        for o in root.findall("object"):
            md = {m.get("key"): m.get("value") for m in o.findall("metadata")}
            sett = {k: v for k, v in md.items() if k not in ("name", "extruder") and not (NOSUP and str(k).startswith(("support", "enable_support")))}
            parts = []
            for pt in o.findall("part"):
                pm = {m.get("key"): m.get("value") for m in pt.findall("metadata")}
                parts.append((stl_for(folder, pm["name"]), int(pm.get("extruder", md.get("extruder", "1"))), REN.get(pm["name"], pm["name"])))
            objs.append(dict(name=md["name"].replace("tag_backup", "tag_bkup"), parts=parts, settings=sett))
        z.close()
        n = b.seed(p, objs, layer, over)
        print(p, layer, over, len(objs), "objects", n, "plate(s)")
        jobs.append({"project": p[len(A) + 1:], "layer": layer, "over": over})
q = json.load(open(f"{A}/SLICE_QUEUE.json"))
have = {j["project"] for j in q["jobs"]}
q["jobs"] += [j for j in jobs if j["project"] not in have]
json.dump(q, open(f"{A}/SLICE_QUEUE.json", "w"), indent=1)
