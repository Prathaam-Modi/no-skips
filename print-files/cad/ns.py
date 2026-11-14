"""No Skips CAD helpers. Units mm, z up, front of a product faces -y.
Everything is built as manifold3d solids so every STL is watertight by construction."""
import math, json, os
import numpy as np
import manifold3d as m3
from manifold3d import Manifold, CrossSection, FillRule
from shapely.geometry import Polygon, MultiPolygon, box, Point
from shapely.ops import unary_union
from shapely import affinity
from matplotlib.textpath import TextPath
from matplotlib.font_manager import FontProperties
import trimesh

OUT = os.environ.get("NS_OUT", "/home/claude/out")
FONT = "/usr/share/fonts/truetype/google-fonts/Poppins-Bold.ttf"
BLACK, IVORY, RED, PROP, PROP2 = "black", "ivory", "red", "prop", "prop2"
SEG = 96
# waveform from "Knowing", the same data the site draws
W20 = [0.54,0.98,0.97,0.57,0.48,1.0,0.98,0.99,0.64,0.4,0.42,0.44,0.32,0.91,0.95,0.98,0.93,0.97,0.98,0.91]

# ---------- 2D ----------
def rrect(w, h, r=5.0, cx=0.0, cy=0.0):
    r = min(r, w / 2 - 1e-3, h / 2 - 1e-3)
    return box(cx - w / 2 + r, cy - h / 2 + r, cx + w / 2 - r, cy + h / 2 - r).buffer(r, quad_segs=12)
def circle(r, cx=0.0, cy=0.0, seg=SEG):
    a = np.linspace(0, 2 * math.pi, seg, endpoint=False)
    return Polygon(np.c_[cx + r * np.cos(a), cy + r * np.sin(a)])
def pill(cx, cy, w, h):
    return rrect(w, h, min(w, h) / 2 - 1e-3, cx, cy)
def fillet(p, r):
    return p.buffer(r, quad_segs=10).buffer(-2 * r, quad_segs=10).buffer(r, quad_segs=10)
def text(s, size, cx=0.0, cy=0.0, anchor="c"):
    """Poppins Bold caps as a shapely shape, cap height = size, vertically centred on cy."""
    k = size / 0.698                       # Poppins cap height is about 0.698 em
    tp = TextPath((0, 0), s.upper(), size=k, prop=FontProperties(fname=FONT))
    g = Polygon()
    for ring in tp.to_polygons():
        if len(ring) >= 4: g = g.symmetric_difference(Polygon(ring).buffer(0))
    if g.is_empty: return g
    x0, y0, x1, y1 = g.bounds
    dx = {"c": -(x0 + x1) / 2, "l": -x0, "r": -x1}[anchor]
    return affinity.translate(g, cx + dx, cy - size / 2)
def fit_text(s, size, maxw, cx=0.0, cy=0.0, anchor="c"):
    g = text(s, size, 0, size / 2, "c")
    if g.is_empty: return g
    k = min(1.0, maxw / (g.bounds[2] - g.bounds[0]))
    g = affinity.scale(g, k, k, origin=(0, 0))
    x0, x1 = g.bounds[0], g.bounds[2]
    dx = {"c": cx - (x0 + x1) / 2, "l": cx - x0, "r": cx - x1}[anchor]
    return affinity.translate(g, dx, cy - size * k / 2)
def wave(data, x0, cy, pitch, w, maxh, minh):
    return unary_union([pill(x0 + i * pitch, cy, w, minh + (maxh - minh) * v) for i, v in enumerate(data)])
def code_art(seed, cx, cy, w):
    """Stand-in for a Spotify Code: disc plus 23 bars. The real code comes from Spotify per order."""
    h = 2166136261
    lv = []
    for i in range(23):
        for ch in f"{seed}#{i}":
            h ^= ord(ch); h = (h * 16777619) & 0xFFFFFFFF
        lv.append(h % 8)
    lv[0] = 0; lv[11] = 7; lv[22] = 0
    k = w / 339.0; x0 = cx - w / 2 - 20 * k
    shapes = [circle(30 * k, x0 + 50 * k, cy)]
    for i, l in enumerate(lv):
        shapes.append(pill(x0 + (103 + i * 11.5) * k, cy, 6 * k, (6 + 54 * l / 7) * k))
    return unary_union(shapes)

# ---------- 3D ----------
def _cs(shape):
    polys = [shape] if isinstance(shape, Polygon) else list(getattr(shape, "geoms", []))
    rings = []
    for p in polys:
        if p.is_empty or not isinstance(p, Polygon): continue
        rings.append(np.asarray(p.exterior.coords)[:-1])
        for i in p.interiors: rings.append(np.asarray(i.coords)[:-1])
    return CrossSection(rings, FillRule.EvenOdd)
def ext(shape, h, z0=0.0):
    if shape.is_empty: return Manifold()
    return Manifold.extrude(_cs(shape.buffer(0)), h).translate((0, 0, z0))
def body(shape, h, z0=0.0, c=0.6, steps=3, top=True, bottom=False):
    """Extrusion with the fine stepped bevel used across the range."""
    dz = c / steps
    lo = c if bottom else 0.0; hi = h - (c if top else 0.0)
    parts = [ext(shape, hi - lo, z0 + lo)]
    for i in range(steps):
        inset = shape.buffer(-c * (i + 1) / steps, quad_segs=8)
        # each step overlaps the one before by 0.02 mm so the union is one solid, not slabs touching face to face
        if top: parts.append(ext(inset, dz + 0.02, z0 + hi + i * dz - 0.02))
        if bottom: parts.append(ext(inset, dz + 0.02, z0 + lo - (i + 1) * dz))
    return U(parts)
def U(parts):
    parts = [p for p in parts if p is not None and not p.is_empty()]
    return Manifold.batch_boolean(parts, m3.OpType.Add) if len(parts) > 1 else (parts[0] if parts else Manifold())
def cyl(r, h, z0=0.0, cx=0.0, cy=0.0, r2=None, seg=SEG):
    return Manifold.cylinder(h, r, r if r2 is None else r2, seg).translate((cx, cy, z0))
def cube(x, y, z, cx=0.0, cy=0.0, z0=0.0):
    return Manifold.cube((x, y, z)).translate((cx - x / 2, cy - y / 2, z0))
def revolve(profile_rz, seg=128):
    return Manifold.revolve(_cs(Polygon(profile_rz)), seg)
def rot(m, rx=0, ry=0, rz=0): return m.rotate((rx, ry, rz))
def mv(m, x=0, y=0, z=0): return m.translate((x, y, z))
def stand_xz(m):
    """A shape extruded along z becomes a plate standing in the x-z plane (its thickness along y)."""
    return m.rotate((90, 0, 0))
def tm(m):
    mesh = m.to_mesh()
    return trimesh.Trimesh(np.asarray(mesh.vert_properties)[:, :3], np.asarray(mesh.tri_verts), process=False)

# ---------- print estimate ----------
DENSITY = 1.24e-3            # g per mm3, PLA
def grams(m, infill=0.15, shell=1.2):
    """Shell plus sparse infill estimate. Thin parts print solid."""
    v, a = m.volume(), m.surface_area()
    shell_v = min(v, a * shell * 0.92)
    return (shell_v + (v - shell_v) * infill) * DENSITY
def hours(g, plates=1, colours=1):
    return 0.25 * plates + g / 19.0 + 0.15 * (colours - 1)

# ---------- product container ----------
class Product:
    def __init__(self, pid, key, name):
        self.id, self.key, self.name = pid, key, name
        self.parts = []      # print parts: (file label, manifold in print orientation, colour, qty, infill)
        self.scenes = {}     # scene name -> list of (manifold, colour)
        self.note = ""
    def part(self, label, m, colour, qty=1, infill=0.15):
        self.parts.append((label, m, colour, qty, infill)); return m
    def scene(self, name, items):
        self.scenes[name] = [(m, c) for m, c in items if not m.is_empty()]
    def export(self):
        d = f"{OUT}/stl/{self.id}_{self.key}"; os.makedirs(d, exist_ok=True)
        rep = {"id": self.id, "name": self.name, "parts": [], "note": self.note}
        tot = 0.0; plates = set()
        for i, (label, m, colour, qty, infill) in enumerate(self.parts, 1):
            mesh = tm(m)
            assert mesh.is_watertight, (self.id, label)
            b = mesh.bounds; mesh.apply_translation((-(b[0][0] + b[1][0]) / 2, -(b[0][1] + b[1][1]) / 2, -b[0][2]))
            fn = f"{self.id}_{i}_{label}_{colour.upper()}" + (f"_x{qty}" if qty > 1 else "") + ".stl"
            mesh.export(f"{d}/{fn}")
            g = grams(m, infill) * qty; tot += g
            ex = mesh.extents
            assert max(ex[0], ex[1]) <= 256 and min(ex[0], ex[1]) <= 256 and ex[2] <= 256, (fn, ex)
            rep["parts"].append({"file": fn, "colour": colour, "qty": qty, "size": [round(float(x), 1) for x in ex], "grams": round(g, 1), "watertight": True})
        rep["grams"] = round(tot, 1)
        os.makedirs(f"{OUT}/scenes", exist_ok=True)
        for sn, items in self.scenes.items():
            sd = f"{OUT}/scenes/{sn}"; os.makedirs(sd, exist_ok=True)
            meta = []
            for j, (m, c) in enumerate(items):
                tm(m).export(f"{sd}/{j:02d}_{c}.stl"); meta.append([f"{j:02d}_{c}.stl", c])
            json.dump(meta, open(f"{sd}/meta.json", "w"))
        return rep
