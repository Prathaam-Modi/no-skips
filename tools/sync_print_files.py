"""Mirror the No Skips print-ready files into an organised folder (owner's copy on D:\\No Skips).

Run it after every product update, once the sliced files are on main:
    python3 tools/sync_print_files.py --repo <repo root> --dest "<D:\\No Skips as mounted>" --note "what changed"

What it does
- Sorts every product into one folder, with three subfolders:
    print_ready/  sliced plates (*.gcode.3mf): open in Bambu Studio and send to the A1
    projects/     Bambu Studio projects (*.3mf): editable plates, slice again if the filament slots differ
    stl/          the parts as STLs
- Writes INDEX.txt into each print_ready folder (time, grams and filament per plate, read from the sliced file itself),
  00_README.txt at the top (structure and the whole table) and appends one line to SYNC_LOG.txt.
- Never deletes: a file that changed, or that is no longer in the repo, is moved to _superseded/<timestamp>/ first.
- A product folder the map does not know goes to 06_Unsorted (Pn products go to 01_Play by prefix) and is reported at the end.
"""
import argparse, datetime, hashlib, os, re, shutil, subprocess, sys, zipfile

IST = datetime.timezone(datetime.timedelta(hours=5, minutes=30))
SECTIONS = ["01_Play", "02_Range_V4", "03_Deferred", "04_Tests", "05_Settings", "06_Unsorted"]
SECTION_BLURB = {
    "01_Play": "Play line (games and tabletop), the current direction",
    "02_Range_V4": "Launch range V4 (B-Side, Ripple, Vol. 01, Track Plate, Bookends, planters)",
    "03_Deferred": "Sidelined products, kept for later",
    "04_Tests": "Fit coupon and retired tests",
    "05_Settings": "Slicer settings notes and the first-prints plan",
    "06_Unsorted": "Folders the sync did not recognise: tell the partner to file them",
}
# repo folder name -> (section, folder name in the mirror)
MAP = {
    "P1_crosses": ("01_Play", "P1_Crosses"),
    "P2_tangram": ("01_Play", "P2_Tangram"),
    "P3_chess": ("01_Play", "P3_Chess_Pieces"),
    "P3_chess_board": ("01_Play", "P3_Chess_Board"),
    "D8_b_side": ("02_Range_V4", "D8_B-Side"),
    "D18_ripple": ("02_Range_V4", "D18_Ripple"),
    "C1_studio_tray": ("02_Range_V4", "C1_Vol01_Studio_Tray"),
    "A1_track_plate": ("02_Range_V4", "A1_Track_Plate"),
    "D17_bookends": ("02_Range_V4", "D17_Bookends"),
    "H1_terrace": ("02_Range_V4", "H1_Terrace"),
    "H2_twist": ("02_Range_V4", "H2_Twist"),
    "H3_echo": ("02_Range_V4", "H3_Echo"),
    "00_fit_coupon": ("04_Tests", "00_Fit_Coupon"),
    "P3_pawn_test": ("04_Tests", "P3_Pawn_Test_retired"),
}
SLOT = {"1": "Black", "2": "Red", "3": "Ivory"}


def place(name, deferred):
    if deferred:
        return "03_Deferred", name
    if name in MAP:
        return MAP[name]
    if re.match(r"^C2_\d\d_", name):
        return "02_Range_V4", "C2_Studio_Minis/" + name
    if re.match(r"^P\d", name):
        return "01_Play", name
    return "06_Unsorted", name


def sha(p):
    h = hashlib.sha1()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def plate_info(path):
    """(seconds, grams, {slot: grams}) from a sliced .gcode.3mf, or None."""
    try:
        with zipfile.ZipFile(path) as z:
            t = z.read("Metadata/slice_info.config").decode("utf-8", "replace")
        sec = re.search(r'key="prediction" value="(\d+)"', t)
        wt = re.search(r'key="weight" value="([0-9.]+)"', t)
        fil = {m.group(1): float(m.group(2)) for m in re.finditer(r'<filament id="(\d+)"[^>]*?used_g="([0-9.]+)"', t)}
        return int(sec.group(1)), float(wt.group(1)), fil
    except Exception:
        return None


def hm(s):
    return f"{s // 3600} h {s % 3600 // 60:02d} min"


def collect(repo):
    """dest-relative path -> source path."""
    want, unknown = {}, set()
    pf = os.path.join(repo, "print-files")
    for deferred in (False, True):
        base = os.path.join(pf, "deferred") if deferred else pf
        for kind in ("a1_ready", "stl"):
            kd = os.path.join(base, kind)
            if not os.path.isdir(kd):
                continue
            for name in sorted(os.listdir(kd)):
                d = os.path.join(kd, name)
                if not os.path.isdir(d):
                    continue
                sec, folder = place(name, deferred)
                if sec == "06_Unsorted":
                    unknown.add(name)
                for fn in sorted(os.listdir(d)):
                    src = os.path.join(d, fn)
                    if not os.path.isfile(src):
                        continue
                    low = fn.lower()
                    if low.endswith(".gcode.3mf"):
                        sub = "print_ready"
                    elif low.endswith(".3mf"):
                        sub = "projects"
                    elif low.endswith(".stl"):
                        sub = "stl"
                    else:
                        continue
                    want[f"{sec}/{folder}/{sub}/{fn}"] = src
    # the turned v1 chess set lives straight under deferred/
    v1 = os.path.join(pf, "deferred", "P3_chess_turned_v1")
    if os.path.isdir(v1):
        for root, _, files in os.walk(v1):
            for fn in files:
                if fn.lower().endswith((".stl", ".3mf")):
                    sub = "print_ready" if fn.lower().endswith(".gcode.3mf") else ("projects" if fn.lower().endswith(".3mf") else "stl")
                    want[f"03_Deferred/P3_Chess_Turned_v1/{sub}/{fn}"] = os.path.join(root, fn)
    for fn in ("PRINT_SETTINGS.md", "FIRST_PRINTS.md"):
        p = os.path.join(pf, "a1_ready", fn)
        if os.path.isfile(p):
            want[f"05_Settings/{fn}"] = p
    p = os.path.join(pf, "README_PRINT.txt")
    if os.path.isfile(p):
        want["05_Settings/README_PRINT.txt"] = p
    return want, unknown


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", required=True)
    ap.add_argument("--dest", required=True)
    ap.add_argument("--note", default="")
    a = ap.parse_args()
    now = datetime.datetime.now(IST)
    stamp = now.strftime("%Y-%m-%d_%H%M")
    try:
        commit = subprocess.check_output(["git", "-C", a.repo, "log", "-1", "--format=%h %s"], text=True).strip()
    except Exception:
        commit = "unknown"
    want, unknown = collect(a.repo)
    os.makedirs(a.dest, exist_ok=True)
    arch = os.path.join(a.dest, "_superseded", stamp)
    n_add = n_upd = n_same = n_gone = 0

    def archive(rel):
        nonlocal arch
        tgt = os.path.join(arch, rel)
        os.makedirs(os.path.dirname(tgt), exist_ok=True)
        os.replace(os.path.join(a.dest, rel), tgt)

    for rel, src in want.items():
        dst = os.path.join(a.dest, rel)
        if os.path.exists(dst):
            if sha(src) == sha(dst):
                n_same += 1
                continue
            archive(rel)
            n_upd += 1
        else:
            n_add += 1
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copy2(src, dst)
    # files in the mirror the repo no longer has (INDEX.txt is generated below)
    for sec in SECTIONS:
        sd = os.path.join(a.dest, sec)
        for root, _, files in os.walk(sd):
            for fn in files:
                if fn == "INDEX.txt":
                    continue
                rel = os.path.relpath(os.path.join(root, fn), a.dest).replace(os.sep, "/")
                if rel not in want:
                    archive(rel)
                    n_gone += 1
    # indexes
    rows = []
    for sec in SECTIONS:
        sd = os.path.join(a.dest, sec)
        for root, dirs, files in os.walk(sd):
            if os.path.basename(root) != "print_ready":
                continue
            plates = sorted(f for f in files if f.lower().endswith(".gcode.3mf"))
            prod = os.path.relpath(os.path.dirname(root), a.dest).replace(os.sep, "/")
            lines = [f"{prod}: sliced plates (Bambu Studio 2.02, A1, 0.4 mm nozzle, textured PEI, PLA Basic)",
                     "AMS slots: 1 Black, 2 Red, 3 Ivory. Open the file in Bambu Studio and print; no re-slice needed if your slots match.", ""]
            for f in plates:
                info = plate_info(os.path.join(root, f))
                if info:
                    sec_s, g, fil = info
                    fs = ", ".join(f"{SLOT.get(k, 'slot ' + k)} {v:.1f} g" for k, v in sorted(fil.items()))
                    lines.append(f"{f}: {hm(sec_s)}, {g:.1f} g ({fs})")
                    rows.append((prod, f, hm(sec_s), f"{g:.1f}", fs))
                else:
                    lines.append(f"{f}: (could not read the slice details)")
            open(os.path.join(root, "INDEX.txt"), "w", encoding="utf-8").write("\n".join(lines) + "\n")
    # top README
    out = ["NO SKIPS - print-ready files", "",
           f"Last synced: {now.strftime('%d %b %Y, %I:%M %p')} IST",
           f"From the repo (github.com/Prathaam-Modi/no-skips, branch main): {commit}",
           f"Change: {a.note or '-'}", "",
           "Layout (every product folder has the same three subfolders):",
           "  print_ready/  sliced plates (.gcode.3mf). Open in Bambu Studio, send to the A1. INDEX.txt lists time, grams and filament per plate.",
           "  projects/     Bambu Studio projects (.3mf). Editable; use these to re-slice with your own filament slots.",
           "  stl/          the parts as STL files.", ""]
    for sec in SECTIONS:
        out.append(f"{sec}: {SECTION_BLURB[sec]}")
    out += ["", "Rules: one colour body per plate, no supports, AMS slots 1 Black, 2 Red, 3 Ivory.",
            "Old versions of any file that changed are kept in _superseded/<date and time>/ (nothing is deleted).",
            "This folder is a copy. The source of truth is the GitHub repo; ask the partner to re-sync after any update.", "",
            "All sliced plates:", ""]
    for prod, f, t, g, fs in sorted(rows):
        out.append(f"  {prod}/print_ready/{f}  |  {t}  |  {g} g  |  {fs}")
    if unknown:
        out += ["", "NOT SORTED YET (folders the sync did not recognise, now in 06_Unsorted): " + ", ".join(sorted(unknown))]
    open(os.path.join(a.dest, "00_README.txt"), "w", encoding="utf-8").write("\n".join(out) + "\n")
    with open(os.path.join(a.dest, "SYNC_LOG.txt"), "a", encoding="utf-8") as f:
        f.write(f"{now.strftime('%Y-%m-%d %H:%M')} IST | {commit} | +{n_add} new, ~{n_upd} updated, {n_same} unchanged, -{n_gone} retired | {a.note}\n")
    print(f"added {n_add}, updated {n_upd}, unchanged {n_same}, retired {n_gone}; plates indexed {len(rows)}; unsorted {sorted(unknown) or 'none'}")


if __name__ == "__main__":
    sys.exit(main())
