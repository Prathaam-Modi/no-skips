"""No Skips order kit, rev B: turn a Spotify Code SVG (or a name) into print files.

Products
  plate   A1 Track Plate   140 x 70 plate, code + title + artist, slotted base bar
  tag     A5 Track Tag     80 x 30 tag, code on the front, song/artist or a name inlaid on the back
  alias   B3 Alias         70 x 30 name tag, no code

Per order
1. Spotify app: open the song > Share > Copy song link.
2. spotifycodes.com: paste the link, format SVG, background #000000, bar colour white, Download.
3. Run one of:
   python code_to_print.py plate code.svg --title "Blinding Lights" --artist "The Weeknd"
   python code_to_print.py tag   code.svg --title "Starboy" --artist "The Weeknd"
   python code_to_print.py tag   code.svg --name "Dimo"
   python code_to_print.py alias --line1 "Dimo" --line2 "Mahtarp"
4. Open preview.png. The front must show 23 bars and the logo, the back must read correctly.
5. Bambu Studio: load every STL in the output folder as ONE object with parts and set colours from
   the file names (BLACK body, IVORY code, ACCENT = the customer's accent colour).
   Fixed parts (base bar, strap) are copied in from fixed_parts/ so the order folder is complete.
6. Scan the printed code with the Spotify app before shipping. Never ship one that does not scan.

Needs: pip install trimesh shapely manifold3d matplotlib svgelements numpy
"""
import argparse, os, sys, re, shutil, math
import numpy as np, trimesh
import manifold3d as m3
from manifold3d import Manifold, CrossSection, FillRule
from shapely.geometry import Polygon, box
from shapely.ops import unary_union
from shapely import affinity
from matplotlib.textpath import TextPath
from matplotlib.font_manager import FontProperties

HERE = os.path.dirname(os.path.abspath(__file__))
FONT = FontProperties(fname=os.path.join(HERE, "Poppins-Bold.ttf"))
RAISE = 0.6          # code and text height above the face
RIM = 1.0            # tag rim height, 0.4 mm proud of the code so keys rub the rim
ALLOWED = re.compile(r"^[A-Za-zÀ-ÖØ-öø-ÿ0-9 .,'&!?()\-]*$")

# ---------------- 2D
def rrect(w, h, r=5.0, cx=0.0, cy=0.0):
    r = min(r, w / 2 - 1e-3, h / 2 - 1e-3)
    return box(cx - w / 2 + r, cy - h / 2 + r, cx + w / 2 - r, cy + h / 2 - r).buffer(r, quad_segs=12)
def circle(r, cx=0.0, cy=0.0, seg=96):
    a = np.linspace(0, 2 * math.pi, seg, endpoint=False)
    return Polygon(np.c_[cx + r * np.cos(a), cy + r * np.sin(a)])
W20 = [0.54,0.98,0.97,0.57,0.48,1.0,0.98,0.99,0.64,0.4,0.42,0.44,0.32,0.91,0.95,0.98,0.93,0.97,0.98,0.91]
def pill(cx, cy, w, h): return rrect(w, h, min(w, h) / 2 - 1e-3, cx, cy)
def wave(data, x0, cy, pitch, w, maxh, minh):
    return unary_union([pill(x0 + i * pitch, cy, w, minh + (maxh - minh) * v) for i, v in enumerate(data)])
MIN_TEXT = 4.0   # mm cap height, smallest text that prints clean (B-Side test, 20 Nov 2026)
def fit_text(s, cap, maxw, cx=0.0, cy=0.0):
    """Poppins Bold caps, cap height = cap (shrunk to fit maxw), centred on (cx, cy)."""
    tp = TextPath((0, 0), s.upper(), size=cap / 0.698, prop=FONT)
    g = Polygon()
    for ring in tp.to_polygons():
        if len(ring) >= 4: g = g.symmetric_difference(Polygon(ring).buffer(0))
    if g.is_empty: return g
    k = min(1.0, maxw / (g.bounds[2] - g.bounds[0]))
    if cap * k < MIN_TEXT - 1e-6:
        sys.exit(f"{s!r} would print {cap * k:.1f} mm tall. Below {MIN_TEXT} mm the letters smear on a 0.4 mm nozzle: shorten it.")
    g = affinity.scale(g, k, k, origin=(0, 0))
    x0, _, x1, _ = g.bounds
    return affinity.translate(g, cx - (x0 + x1) / 2, cy - cap * k / 2)

# ---------------- 3D (manifold: watertight by construction)
def _cs(shape):
    polys = [shape] if isinstance(shape, Polygon) else list(getattr(shape, "geoms", []))
    rings = []
    for p in polys:
        if p.is_empty or not isinstance(p, Polygon): continue
        rings.append(np.asarray(p.exterior.coords)[:-1])
        rings += [np.asarray(i.coords)[:-1] for i in p.interiors]
    return CrossSection(rings, FillRule.EvenOdd)
def U(parts):
    parts = [p for p in parts if not p.is_empty()]
    return Manifold.batch_boolean(parts, m3.OpType.Add) if len(parts) > 1 else parts[0]
def ext(shape, h, z0=0.0):
    return Manifold.extrude(_cs(shape.buffer(0)), h).translate((0, 0, z0))
def body(shape, h, c=0.6, steps=3, top=True, bottom=False):
    dz = c / steps; lo = c if bottom else 0.0; hi = h - (c if top else 0.0)
    parts = [ext(shape, hi - lo, lo)]
    for i in range(steps):
        inset = shape.buffer(-c * (i + 1) / steps, quad_segs=8)
        if top: parts.append(ext(inset, dz + 0.02, hi + i * dz - 0.02))      # 0.02 overlap: one solid, not stacked slabs
        if bottom: parts.append(ext(inset, dz + 0.02, lo - (i + 1) * dz))
    return U(parts)
def to_mesh(m):
    mesh = m.to_mesh()
    t = trimesh.Trimesh(np.asarray(mesh.vert_properties)[:, :3], np.asarray(mesh.tri_verts), process=False)
    assert t.is_watertight, "mesh is not watertight"
    return t

# ---------------- Spotify Code SVG
def read_code(path):
    import svgelements as se
    svg = se.SVG.parse(path, reify=True)
    vb = svg.viewbox; W = vb.width if vb else svg.width; H = vb.height if vb else svg.height
    shapes = []
    for e in svg.elements():
        if not isinstance(e, se.Shape) or e.fill is None or e.fill.value is None: continue
        polys = []
        for sp in se.Path(e).as_subpaths():
            sp = se.Path(sp)
            if sp.length() < 1e-6: continue
            n = max(24, int(sp.length() * 4))
            pts = [(float(q[0]), -float(q[1])) for q in sp.npoint(np.linspace(0, 1, n))]
            if len(pts) >= 4: polys.append(Polygon(pts).buffer(0))
        g = Polygon()
        for q in sorted(polys, key=lambda x: -x.area): g = g.symmetric_difference(q)     # even-odd
        if not g.is_empty: shapes.append((str(e.fill), g))
    if not shapes: sys.exit("No shapes found in the SVG.")
    bg = max(shapes, key=lambda s: s[1].area)
    if bg[1].area < 0.6 * W * H: sys.exit("Could not find the code background. Download the SVG with a background colour.")
    code = unary_union([g for c, g in shapes if c != bg[0]])
    parts = list(code.geoms) if code.geom_type == "MultiPolygon" else [code]
    bars = [p for p in parts if (p.bounds[2] - p.bounds[0]) < 0.06 * W]
    logo = [p for p in parts if (p.bounds[2] - p.bounds[0]) >= 0.06 * W]
    print(f"read {os.path.basename(path)}: {len(bars)} bars, {len(logo)} logo shape(s)")
    if len(bars) != 23 or len(logo) != 1:
        print("WARNING: a Spotify Code has 23 bars and one logo. Check preview.png before printing.")
    return code
def fit_code(code, width, cx, cy):
    x0, y0, x1, y1 = code.bounds; k = width / (x1 - x0)
    g = affinity.scale(code, k, k, origin=(x0, y0))
    return affinity.translate(g, cx - width / 2 - x0, cy - (y1 - y0) * k / 2 - y0)
def check(label, s, limit):
    if not s: sys.exit(f"{label} is empty.")
    if not ALLOWED.match(s): sys.exit(f"{label} has characters we cannot print: {s!r}")
    if len(s) > limit: sys.exit(f"{label} is {len(s)} characters. The limit is {limit}.")

# ---------------- products (same geometry as the rev B range files)
def tag_body(L, front, back):
    outline = rrect(L, 30, 5); hole = circle(4.2, -L / 2 + 9, 0)
    base = body(outline.difference(hole), 3.0, bottom=True, top=False)
    ring = outline.difference(outline.buffer(-1.4)).union(circle(5.6, -L / 2 + 9, 0).difference(hole)).intersection(outline)
    rim = ext(ring, RIM, 3.0)
    inlay = ext(back, 0.4, 0.0) if not back.is_empty else None
    black = U([base, rim])
    if inlay is not None: black = black - inlay
    return black, ext(front, RAISE, 3.0), inlay, outline

def plate(code, title, artist):
    check("Song title", title, 28); check("Artist", artist, 26)
    out = rrect(140, 70, 5)
    art = unary_union([fit_code(code, 120, 0, 11), fit_text(title, 6.2, 110, 0, -14.5), fit_text(artist, 4.0, 100, 0, -24)])
    files = {"A1_1_plate_BLACK.stl": body(out, 3.0, bottom=True), "A1_2_code_and_title_IVORY.stl": ext(art, RAISE, 3.0)}
    return files, [("front", out, art, "#f0ebe0")], ["A1_3_base_bar_BLACK.stl", "A1_4_base_stripe_ACCENT.stl"]

def tag(code, title, artist, name):
    front = fit_code(code, 58, 6, 0)          # code sits between the hole ring and the rim
    if name:
        check("Name", name, 14); back = fit_text(name, 5.0, 54, -6, 0)
    else:
        check("Song title", title, 14); check("Artist", artist, 14)
        back = unary_union([fit_text(title, 5.0, 54, -6, 5.2), fit_text(artist, 4.0, 54, -6, -3.6)])   # as read: hole is on the right
    back_m = affinity.scale(back, -1, 1, origin=(0, 0))      # mirrored: printed face down on the bed
    black, art, inlay, out = tag_body(80, front, back_m)
    out = out.difference(circle(4.2, -31, 0))
    files = {"A5_1_tag_body_BLACK.stl": black, "A5_2_front_code_IVORY.stl": art, "A5_3_back_inlay_ACCENT.stl": inlay}
    flip = affinity.scale(out, -1, 1, origin=(0, 0))
    return files, [("front", out, front, "#f0ebe0"), ("back (as read)", flip, back, "#c8102e")], ["A5_4_loop_strap_BLACK.stl"]

def alias(l1, l2):
    check("Line 1", l1, 10)
    if l2:
        check("Line 2", l2, 10)
        front = unary_union([fit_text(l1, 5.0, 40, 6, 6.6), fit_text(l2, 5.0, 40, 6, -0.4)])
    else:
        front = fit_text(l1, 6.0, 44, 6, 3.6)
    front = front.union(wave(W20, -13.6, -9.2, 2.06, 1.3, 5.2, 1.3))       # the No Skips waveform strip
    black, art, _, out = tag_body(70, front, Polygon())
    out = out.difference(circle(4.2, -26, 0))
    files = {"B3_1_tag_body_BLACK.stl": black, "B3_2_front_name_ACCENT.stl": art}
    return files, [("front", out, front, "#c8102e")], ["B3_3_loop_strap_BLACK.stl"]

def preview(views, path):
    import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
    fig, axs = plt.subplots(1, len(views), figsize=(5.5 * len(views), 3.4))
    for ax, (t, out, g, col) in zip(np.atleast_1d(axs), views):
        ax.fill(*out.exterior.xy, color="#161514")
        for p in out.interiors: ax.fill(*p.xy, color="white")
        for p in ([g] if g.geom_type == "Polygon" else list(g.geoms)):
            ax.fill(*p.exterior.xy, color=col)
            for i in p.interiors: ax.fill(*i.xy, color="#161514")
        x0, y0, x1, y1 = out.bounds
        ax.set_xlim(x0 - 2, x1 + 2); ax.set_ylim(y0 - 2, y1 + 2); ax.set_aspect("equal"); ax.axis("off"); ax.set_title(t)
    fig.savefig(path, dpi=160, bbox_inches="tight", facecolor="white"); plt.close(fig)

SPOTIFY_RE = re.compile(r"(?:open\.spotify\.com/(?:intl-[a-z]{2}(?:-[a-z]{2})?/)?(track|album|playlist|artist|episode)/|spotify:(track|album|playlist|artist|episode):)([A-Za-z0-9]{22})")

def spotify_uri(link):
    """Spotify share link or URI -> spotify:<kind>:<id>."""
    m = SPOTIFY_RE.search(link.strip())
    if not m: sys.exit("That does not look like a Spotify link. In the Spotify app: Share > Copy song link.")
    return "spotify:%s:%s" % (m.group(1) or m.group(2), m.group(3))

def fetch_code(link, out_dir):
    """Download the code SVG (black background, white bars) from Spotify's code service."""
    import urllib.request
    uri = spotify_uri(link)
    url = "https://scannables.scdn.co/uri/plain/svg/000000/white/640/" + uri
    os.makedirs(out_dir, exist_ok=True)
    dest = os.path.join(out_dir, "code.svg")
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=20) as r: data = r.read()
        if b"<svg" not in data[:400]: raise ValueError("not an SVG")
    except Exception as e:
        sys.exit("Could not download the code (%s). Make it by hand at spotifycodes.com (SVG, background #000000, "
                 "bars white) and give the file instead of --link." % e)
    open(dest, "wb").write(data); print("downloaded", uri, "->", dest)
    return dest

if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="No Skips order kit, rev B")
    ap.add_argument("product", choices=["plate", "tag", "alias"]); ap.add_argument("svg", nargs="?")
    ap.add_argument("--title", default=""); ap.add_argument("--artist", default=""); ap.add_argument("--name", default="")
    ap.add_argument("--line1", default=""); ap.add_argument("--line2", default="")
    ap.add_argument("-o", "--out", default="print_files")
    ap.add_argument("--link", default="", help="Spotify song link: downloads the code for you")
    a = ap.parse_args()
    if a.link:
        if a.product == "alias": sys.exit("Alias has no code, so it takes no --link.")
        a.svg = fetch_code(a.link, a.out)
    if a.product != "alias" and not a.svg: sys.exit("Give the Spotify Code SVG file.")
    if a.product == "plate": files, views, fixed = plate(read_code(a.svg), a.title, a.artist)
    elif a.product == "tag": files, views, fixed = tag(read_code(a.svg), a.title, a.artist, a.name)
    else: files, views, fixed = alias(a.line1 or a.name, a.line2)
    os.makedirs(a.out, exist_ok=True)
    for fn, m in files.items():
        t = to_mesh(m); t.export(os.path.join(a.out, fn)); print("wrote", fn, [round(float(v), 1) for v in t.extents])
    for fn in fixed:
        shutil.copy(os.path.join(HERE, "fixed_parts", fn), os.path.join(a.out, fn)); print("copied", fn)
    preview(views, os.path.join(a.out, "preview.png")); print("wrote preview.png")
