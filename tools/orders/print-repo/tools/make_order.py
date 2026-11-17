"""Turn one No Skips order into print-ready files for the Bambu Lab A1.

  python tools/make_order.py --ref NS-1711-AB12 --jobs '[{"product":"tag", ...}]'
  python tools/make_order.py --ref NS-1711-AB12 --jobs-file jobs.json --svg kit/test_code.svg   (local test, no download)
  python tools/make_order.py --ref NS-1711-AB12 --jobs '...' --no-slice     (build only)
  python tools/make_order.py --ref NS-1711-AB12 --slice-only                (slice what was built)

Writes orders/<ref>/<n>_<product>/ (STLs, preview.png, <ref>_<n>_<product>.3mf, .gcode.3mf when sliced),
orders/<ref>/summary.json and orders/<ref>/preview.png (all job previews side by side).
A bad job never stops the run: it is reported in summary.json with ok=false and the reason.
"""
import argparse, datetime, glob, json, os, re, shutil, subprocess, sys, time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bambu3mf  # noqa: E402

ROOT = bambu3mf.ROOT
KIT = os.path.join(ROOT, "kit", "code_to_print.py")
REF_RE = re.compile(r"^NS-(0[1-9]|[12][0-9]|3[01])(0[1-9]|1[0-2])-[A-Z0-9]{4}$")
LINK_RE = re.compile(r"^(https://open\.spotify\.com/(intl-[a-z]{2}(-[a-z]{2})?/)?(track|album|playlist|artist|episode)/[A-Za-z0-9]{22}"
                     r"(\?[A-Za-z0-9=&._-]*)?|spotify:(track|album|playlist|artist|episode):[A-Za-z0-9]{22})$")
PRODUCTS = {"plate": "A1 Track Plate", "tag": "A5 Track Tag", "alias": "B3 Alias"}
TEXT_FIELDS = ("title", "artist", "name", "line1", "line2")
MAX_JOBS, MAX_QTY = 20, 50
GLOBAL = {"curr_bed_type": "Textured PEI Plate", "sparse_infill_pattern": "gyroid", "ironing_type": "no ironing",
          "seam_position": "aligned", "brim_type": "no_brim"}


class JobError(Exception):
    pass


def rel(p):
    return os.path.relpath(p, ROOT).replace(os.sep, "/")


# ---------------------------------------------------------------- validation
def clean_job(j):
    if not isinstance(j, dict):
        raise JobError("Job is not an object.")
    product = str(j.get("product", "")).strip().lower()
    if product not in PRODUCTS:
        raise JobError("Unknown product %r. Use plate, tag or alias." % j.get("product"))
    out = {"product": product, "item": str(j.get("item") or PRODUCTS[product])[:60]}
    for k in TEXT_FIELDS:
        v = j.get(k) or ""
        if not isinstance(v, str):
            raise JobError("%s must be text." % k)
        out[k] = " ".join(v.split())[:80]
    accent = str(j.get("accent") or "red").strip().lower()
    if accent not in ("red", "ivory"):
        raise JobError("Accent must be red or ivory, not %r." % j.get("accent"))
    out["accent"] = accent
    try:
        qty = int(j.get("qty", 1) or 1)
    except (TypeError, ValueError):
        raise JobError("qty must be a whole number.")
    if not 1 <= qty <= MAX_QTY:
        raise JobError("qty must be between 1 and %d." % MAX_QTY)
    out["qty"] = qty
    link = str(j.get("link") or "").strip()
    if link and product != "alias" and not LINK_RE.match(link):
        raise JobError("That does not look like a Spotify link. In the Spotify app: Share > Copy song link.")
    out["link"] = link if product != "alias" else ""
    return out


# ---------------------------------------------------------------- per job
def run_kit(job, out_dir, svg):
    """Run the order kit with every input as its own argv entry (no shell)."""
    p = job["product"]
    cmd = [sys.executable, KIT, p]
    if p != "alias":
        if svg:
            cmd.append(svg)
        elif job["link"]:
            cmd.append("--link=" + job["link"])
        else:
            raise JobError("A %s needs a Spotify link for its code." % PRODUCTS[p])
    if p == "plate":
        cmd += ["--title=" + job["title"], "--artist=" + job["artist"]]
    elif p == "tag":
        cmd += ["--name=" + job["name"]] if job["name"] else ["--title=" + job["title"], "--artist=" + job["artist"]]
    else:
        cmd += ["--line1=" + (job["line1"] or job["name"]), "--line2=" + (job["line2"] if job["line1"] else "")]
    cmd += ["-o", out_dir]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
    if r.returncode != 0:
        lines = [l for l in (r.stderr or r.stdout).strip().splitlines() if l.strip()]
        raise JobError(lines[-1] if lines else "The order kit failed (exit %d)." % r.returncode)
    return [l for l in r.stdout.splitlines() if l.startswith("WARNING")]


def recolour_preview(path):
    """The kit draws accent parts red. For an ivory accent, repaint red (and its antialiased edge
    against the black body) as ivory so the customer sees the colour they ordered."""
    import numpy as np
    from PIL import Image
    im = np.asarray(Image.open(path).convert("RGB")).astype(float)
    r, g, b = im[..., 0], im[..., 1], im[..., 2]
    mask = (r - g > 40) & (r - b > 40)
    a = np.clip((r - 22.0) / (200.0 - 22.0), 0, 1)[..., None]
    black, ivory = np.array([22, 21, 20.0]), np.array([240, 235, 224.0])
    im[mask] = (a * ivory + (1 - a) * black)[mask]
    Image.fromarray(im.round().astype("uint8")).save(path)


def plan(job, d):
    """Objects, layer and process overrides for one job, from the range settings (PRINT_SETTINGS.md)."""
    acc = 2 if job["accent"] == "red" else 3
    slot = lambda f: {"BLACK": 1, "IVORY": 3, "ACCENT": acc}[f.rsplit("_", 1)[1][:-4]]
    f = lambda pat: sorted(glob.glob(os.path.join(d, pat)))
    part = lambda path: (path, slot(path), re.sub(r"^[A-Z]\d_\d_|_(BLACK|IVORY|ACCENT)\.stl$", "", os.path.basename(path)))
    solid = {"sparse_infill_density": "100%", "sparse_infill_pattern": "zig-zag"}
    p = job["product"]
    if p == "plate":      # A1: 0.16, 3 walls, 15% gyroid, plate solid
        groups = [("A1 plate", f("A1_1_*") + f("A1_2_*"), solid), ("A1 base bar", f("A1_3_*") + f("A1_4_*"), {})]
        layer, over = "0.16", {"wall_loops": "3", "sparse_infill_density": "15%"}
    elif p == "tag":      # A5: 0.12, 3 walls, 100%
        groups = [("A5 tag", f("A5_1_*") + f("A5_2_*") + f("A5_3_*"), {}), ("A5 strap", f("A5_4_*"), {})]
        layer, over = "0.12", dict(wall_loops="3", **solid)
    else:                 # B3: 0.16, 3 walls, 100%. B5 Run 50: 0.20, 3 walls, 100%, top 4 bottom 3
        b5 = job["item"].upper().startswith("B5")
        pid = "B5" if b5 else "B3"
        groups = [(pid + " tag", f("B3_1_*") + f("B3_2_*"), {}), (pid + " strap", f("B3_3_*"), {})]
        layer, over = ("0.20", dict(wall_loops="3", top_shell_layers="4", bottom_shell_layers="3", **solid)) if b5 \
            else ("0.16", dict(wall_loops="3", **solid))
    over = dict(GLOBAL, **over)
    objects = []
    for i in range(job["qty"]):
        for name, files, st in groups:
            if not files:
                raise JobError("The order kit did not write the %s files." % name)
            objects.append(dict(name=name + (" %d" % (i + 1) if job["qty"] > 1 else ""), parts=[part(x) for x in files], settings=st))
    return objects, layer, over


def build_job(ref, n, raw, order_dir, svg):
    e = {"n": n, "product": str(raw.get("product", ""))[:20] if isinstance(raw, dict) else "",
         "item": str(raw.get("item") or "")[:60] if isinstance(raw, dict) else "", "ok": False,
         "preview": None, "files": [], "sliced": None, "note": ""}
    try:
        job = clean_job(raw)
        e.update(product=job["product"], item=job["item"], qty=job["qty"], accent=job["accent"])
        d = os.path.join(order_dir, "%d_%s" % (n, job["product"]))
        shutil.rmtree(d, ignore_errors=True); os.makedirs(d)
        warn = run_kit(job, d, svg)
        if job["accent"] == "ivory":
            recolour_preview(os.path.join(d, "preview.png"))
        objects, layer, over = plan(job, d)
        proj = os.path.join(d, "%s_%d_%s.3mf" % (ref, n, job["product"]))
        plates = bambu3mf.seed(proj, objects, layer, over)
        e.update(ok=True, preview=rel(os.path.join(d, "preview.png")), plates=plates,
                 note=" ".join(warn + ["%d object(s) on %d plate(s), %s mm layers. Not sliced yet." % (len(objects), plates, layer)]))
        e["_plan"] = {"layer": layer, "over": over}
    except JobError as ex:
        e["error"] = str(ex)
    except Exception as ex:                      # keep going, report it
        e["error"] = "Unexpected error: %s" % ex
    if not e["ok"] and e["product"] in PRODUCTS:          # no half-made folder for a failed job
        shutil.rmtree(os.path.join(order_dir, "%d_%s" % (n, e["product"])), ignore_errors=True)
    if e["ok"]:
        e["files"] = sorted(rel(x) for x in glob.glob(os.path.join(order_dir, "%d_%s" % (n, e["product"]), "*")) if os.path.isfile(x))
    return e


def combined_preview(order_dir, jobs):
    from PIL import Image, ImageDraw, ImageFont
    cells = []
    for j in jobs:
        if j["ok"] and j.get("preview") and os.path.exists(os.path.join(ROOT, j["preview"])):
            im = Image.open(os.path.join(ROOT, j["preview"])).convert("RGB")
            k = 360 / im.height; im = im.resize((max(1, int(im.width * k)), 360), Image.LANCZOS)
            cells.append((im, "%d. %s%s" % (j["n"], j["item"], (" x%d" % j["qty"] if j.get("qty", 1) > 1 else "") + ", " + j.get("accent", "red") + " accent")))
    if not cells:
        return None
    font_path = os.path.join(ROOT, "kit", "Poppins-Bold.ttf")
    font = ImageFont.truetype(font_path, 26) if os.path.exists(font_path) else ImageFont.load_default()
    pad, lab = 30, 50
    rows, row, w = [], [], pad
    for c in cells:                               # wrap after about 2400 px
        if row and w + c[0].width + pad > 2800:
            rows.append(row); row, w = [], pad
        row.append(c); w += c[0].width + pad
    rows.append(row)
    W = max(pad + sum(c[0].width + pad for c in r) for r in rows)
    H = pad + len(rows) * (360 + lab + pad)
    out = Image.new("RGB", (W, H), "white"); dr = ImageDraw.Draw(out)
    y = pad
    for r in rows:
        x = pad
        for im, t in r:
            out.paste(im, (x, y)); dr.text((x + 6, y + 360 + 8), t, fill="#161514", font=font); x += im.width + pad
        y += 360 + lab + pad
    p = os.path.join(order_dir, "preview.png"); out.save(p, optimize=True)
    return rel(p)


def write_summary(order_dir, s):
    clean = dict(s, jobs=[{k: v for k, v in j.items() if not k.startswith("_")} for j in s["jobs"]])
    json.dump(clean, open(os.path.join(order_dir, "summary.json"), "w"), indent=2)
    json.dump(s, open(os.path.join(order_dir, ".plan.json"), "w"))       # for --slice-only, not committed


def do_slice(order_dir, s, budget):
    t_end = time.time() + budget
    for j in s["jobs"]:
        if not j["ok"]:
            continue
        d = os.path.join(order_dir, "%d_%s" % (j["n"], j["product"]))
        proj = os.path.join(d, "%s_%d_%s.3mf" % (s["ref"], j["n"], j["product"]))
        left = int(t_end - time.time())
        base = j["note"].replace(" Not sliced yet.", "")
        if left < 30:
            j["note"] = base + " Not sliced: out of time for slicing on this run."; continue
        plan_ = j["_plan"]
        r = bambu3mf.slice_(proj, proj[:-4] + ".gcode.3mf", plan_["layer"], plan_["over"], timeout=left)
        if r["ok"]:
            j["sliced"] = {"time_s": r["time_s"], "grams": r["grams"]}
            j["note"] = base + " Sliced: A1 0.4 mm, Textured PEI, PLA Basic, %.1f h, %.1f g with purge." % (r["time_s"] / 3600, r["grams"])
        else:
            j["note"] = base + " Not sliced: %s. The project .3mf is ready; open it in Bambu Studio and press Slice." % r["error"]
        j["files"] = sorted(rel(x) for x in glob.glob(os.path.join(d, "*")) if os.path.isfile(x))
        write_summary(order_dir, s)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--ref", required=True)
    ap.add_argument("--jobs", help="JSON array of jobs")
    ap.add_argument("--jobs-file", help="file holding the JSON array")
    ap.add_argument("--svg", help="use this Spotify Code SVG for every coded job instead of downloading (testing)")
    ap.add_argument("--no-slice", action="store_true")
    ap.add_argument("--slice-only", action="store_true")
    ap.add_argument("--budget", type=int, default=int(os.environ.get("SLICE_BUDGET_S", "540")), help="seconds for all slicing")
    a = ap.parse_args()
    if not REF_RE.match(a.ref):
        sys.exit("Order number must look like NS-DDMM-XXXX (for example NS-1711-AB12), got %r." % a.ref)
    order_dir = os.path.join(ROOT, "orders", a.ref)

    if a.slice_only:
        pf = os.path.join(order_dir, ".plan.json")
        if not os.path.exists(pf):
            sys.exit("Nothing built for %s yet." % a.ref)
        s = json.load(open(pf))
    else:
        text = open(a.jobs_file).read() if a.jobs_file else (a.jobs or "")
        shutil.rmtree(order_dir, ignore_errors=True); os.makedirs(order_dir)
        s = {"ref": a.ref, "created": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"), "ok": False, "jobs": []}
        try:
            jobs = json.loads(text)
            if isinstance(jobs, dict):
                jobs = [jobs]
            if not isinstance(jobs, list) or not jobs:
                raise ValueError("jobs must be a non-empty JSON array")
            if len(jobs) > MAX_JOBS:
                raise ValueError("at most %d jobs per run" % MAX_JOBS)
        except ValueError as ex:
            s["error"] = "Could not read the jobs: %s" % ex
            write_summary(order_dir, s); print(json.dumps(s, indent=2)); return
        svg = os.path.abspath(a.svg) if a.svg else None
        for n, raw in enumerate(jobs, 1):
            e = build_job(a.ref, n, raw, order_dir, svg)
            print("job %d %s: %s" % (n, e["product"], "ok" if e["ok"] else e.get("error")))
            s["jobs"].append(e)
        s["ok"] = all(j["ok"] for j in s["jobs"])
        s["preview"] = combined_preview(order_dir, s["jobs"])
        for j in s["jobs"]:
            if not j["ok"]:
                j["note"] = "Fix the order details and run it again."
        write_summary(order_dir, s)
    if not a.no_slice:
        do_slice(order_dir, s, a.budget)
        write_summary(order_dir, s)
    print(json.dumps({k: v for k, v in s.items() if k != "jobs"}))
    for j in s["jobs"]:
        print(" ", j["n"], j["product"], "ok" if j["ok"] else "ERROR " + j.get("error", ""), "|", j["note"])


if __name__ == "__main__":
    main()
