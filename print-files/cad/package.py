"""Collect every print file into one folder and zip it: python3 package.py"""
import json, os, shutil, glob, zipfile, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ns import hours

OUT = "/home/claude/out"; DST = "/home/claude/pkg/no_skips_print_files"
ORDER = [("COLLECTIBLES", ["C1", "C2_01", "C2_02", "C2_03", "C2_04", "C2_05", "C2_06", "C3", "C4", "C5"]),
         ("LISTEN", ["A1", "A5", "A3", "A4"]), ("MAKE", ["B1", "B2", "B3", "B5"]),
         ("DAILY", ["D10", "D12", "D11", "D1", "D6", "D7", "D8", "D2", "D4", "D5", "D9"])]
STATUS = {"A4": "COMING SOON (heat test)", "D9": "COMING SOON (heat test)"}
PLATES = {"C1": 1, "C3": 2, "C4": 2, "A1": 2, "A3": 1, "A4": 2, "B1": 2, "B2": 1, "B5": 6, "D1": 2, "D6": 2, "D7": 2, "D4": 2, "D5": 2, "D9": 3, "D10": 1, "D11": 1, "D12": 1}

rep = json.load(open(f"{OUT}/report.json"))
if os.path.exists(DST): shutil.rmtree(DST)
os.makedirs(DST)
shutil.copytree(f"{OUT}/stl", f"{DST}/stl", ignore=shutil.ignore_patterns("README*", "X1_*"))   # collab files stay private
os.makedirs(f"{DST}/blueprints"); [shutil.copy(f, f"{DST}/blueprints/") for f in sorted(glob.glob(f"{OUT}/bp/bp_*.png")) if "bp_X1" not in f]
os.makedirs(f"{DST}/cad")
for f in ("ns.py", "build.py", "build2.py", "build3.py", "render.py", "blueprint.py", "package.py"): shutil.copy(f"/home/claude/cad/{f}", f"{DST}/cad/")
shutil.copytree("/home/claude/kit2", f"{DST}/order_kit", ignore=shutil.ignore_patterns("__pycache__", "print_files"))

L = ["NO SKIPS - PRINT FILES, FULL RANGE", "",
     "Every product in one place: V2 pieces from cad/build.py, the classic range in cad/build2.py, Eject, Standby and Rotary in cad/build3.py.",
     "Nothing here has been test-printed. Weights and hours are model estimates (1.2 mm shell, sparse infill, 19 g an hour",
     "plus 15 minutes a plate). Fit-test every joint before selling and replace the numbers with slicer figures.", "",
     "Folders",
     "  stl/<ID>_<name>/   print parts, already in print orientation. The file name ends in the filament colour;",
     "                     _x4 means print four. Load all parts of a folder as ONE object with parts in Bambu Studio.",
     "  blueprints/        drawing sheets, the same ones the site shows.",
     "  order_kit/         per-order files for Track Plate, Track Tag, Alias and Run 50 (real Spotify Codes, names).",
     "  cad/               the scripts that make all of it. pip install manifold3d trimesh shapely matplotlib numpy;",
     "                     renders and blueprints also need Blender's bpy and pillow.",
     "                     python3 build.py && python3 build2.py && python3 build3.py, then python3 package.py.",
     "                     Options: NS_SET=07 (Vol. 01 tray number), NS_RAIL='Front Row', NS_TAPE='Side A', NS_ACT='Your Act'.",
     "", "Colours: BLACK body, IVORY and RED accents. ACCENT means the customer's chosen colour.", ""]
for line, ids in ORDER:
    L += ["=" * 100, line, "=" * 100, ""]
    for pid in ids:
        r = rep.get(pid)
        if not r: continue
        cols = len({p["colour"] for p in r["parts"]})
        h = hours(r["grams"], PLATES.get(pid, 1), cols)
        L.append(f"{pid} {r['name'].upper()}  about {round(r['grams'])} g, {h:.1f} h" + (f"  [{STATUS[pid]}]" if pid in STATUS else ""))
        if r.get("note"): L.append("  " + r["note"])
        for p in r["parts"]:
            s = p["size"]; L.append(f"  - {p['file']}  {s[0]} x {s[1]} x {s[2]} mm, {p['grams']} g")
        L.append("")
open(f"{DST}/README_PRINT.txt", "w").write("\n".join(L))
zp = "/home/claude/out/no_skips_print_files.zip"
if os.path.exists(zp): os.remove(zp)
with zipfile.ZipFile(zp, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as z:
    for f in sorted(glob.glob(f"{DST}/**/*", recursive=True)):
        if os.path.isfile(f): z.write(f, os.path.relpath(f, os.path.dirname(DST)))
n = len([f for f in glob.glob(f"{DST}/stl/**/*.stl", recursive=True)])
print("zip", zp, round(os.path.getsize(zp) / 1e6, 1), "MB,", n, "STLs")
