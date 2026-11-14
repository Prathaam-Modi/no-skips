"""Labels and arrows for the build images.

Reads a scene written by the CAD scripts, rebuilds the exact camera render.py used, projects 3D points (mm, scene
coordinates) onto the render, and draws numbered part labels, leader lines and direction arrows on top.

    from annotate import annotate
    annotate("rotary_s3", labels=[...], arrows=[...], out="rotary_s3_guide")

label : dict(text="PLATE B", at=(x, y, z), to=(dx, dy) px offset of the text box, tag="B")
arrow : dict(pts=[(x, y, z), ...], kind="move" | "turn" | "press", text="optional")   # polyline in 3D, head at the end
Colours follow the site: red for movement, ivory badge for parts, ink for text.
"""
import os, sys, json, math
import numpy as np, trimesh
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, os.path.dirname(__file__))
from render import SHOTS

OUT = os.environ.get("NS_OUT", "/home/claude/out")
FONT = "/usr/share/fonts/truetype/google-fonts/Poppins-Bold.ttf"
FONT_M = "/usr/share/fonts/truetype/google-fonts/Poppins-Medium.ttf"
RED = (214, 40, 48); INK = (24, 23, 22); IVORY = (246, 241, 230); WHITE = (255, 255, 255)

def camera(scene_name):
    """Same maths as render.py: returns a function mapping mm points to pixel coordinates (880 px square)."""
    sd = f"{OUT}/scenes/{scene_name}"; meta = json.load(open(sd + "/meta.json"))
    shot = SHOTS.get(scene_name, dict(az=-28, el=30, zoom=1.0)); focus = shot.get("focus")
    fb = []
    for fn, c in meta:
        t = trimesh.load(f"{sd}/{fn}", process=False)
        if focus is None or c in focus: fb.append(t.bounds * 0.001)
    b = np.array(fb); lo = b[:, 0, :].min(0); hi = b[:, 1, :].max(0)
    ctr = (lo + hi) / 2; rad = float(np.linalg.norm(hi - lo) / 2)
    az, el = math.radians(shot["az"]), math.radians(shot["el"])
    fov = 2 * math.atan(18 / 85)
    dist = rad / math.sin(fov / 2) * 1.08 / shot.get("zoom", 1.0)
    d = np.array([math.sin(az) * math.cos(el), -math.cos(az) * math.cos(el), math.sin(el)])
    tgt = ctr + np.array(shot.get("shift", (0, 0, 0))) * rad
    loc = tgt + d * dist
    fwd = (tgt - loc) / np.linalg.norm(tgt - loc)
    right = np.cross(fwd, [0, 0, 1.0]); right /= np.linalg.norm(right)
    up = np.cross(right, fwd)
    f = 85 / 36 * 880
    def proj(p):
        v = np.asarray(p, float) * 0.001 - loc
        z = v @ fwd
        return (440 + f * (v @ right) / z, 440 - f * (v @ up) / z)
    return proj

def _font(size, bold=True):
    try: return ImageFont.truetype(FONT if bold else FONT_M, size)
    except Exception: return ImageFont.load_default()

def _arrowhead(d, p0, p1, col, size):
    a = math.atan2(p1[1] - p0[1], p1[0] - p0[0])
    pts = [p1, (p1[0] - size * math.cos(a - 0.45), p1[1] - size * math.sin(a - 0.45)), (p1[0] - size * math.cos(a + 0.45), p1[1] - size * math.sin(a + 0.45))]
    d.polygon(pts, fill=col)

def _dashed(d, a, b, col, w, dash=14, gap=9):
    L = math.hypot(b[0] - a[0], b[1] - a[1]); n = max(1, int(L // (dash + gap)))
    ux, uy = (b[0] - a[0]) / L, (b[1] - a[1]) / L
    for i in range(n + 1):
        s = i * (dash + gap); e = min(s + dash, L)
        if s < L: d.line([(a[0] + ux * s, a[1] + uy * s), (a[0] + ux * e, a[1] + uy * e)], fill=col, width=w)

def annotate(scene_name, labels=(), arrows=(), out=None, banner=None, src=None, scale=2):
    proj = camera(scene_name)
    base = Image.open(src or f"{OUT}/r/{scene_name}.jpg").convert("RGB")
    W = base.size[0]; k = scale * W / 880.0
    im = base.resize((int(W * scale), int(W * scale)), Image.LANCZOS).convert("RGBA")
    ov = Image.new("RGBA", im.size, (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
    S = lambda p: (p[0] * k, p[1] * k)
    # arrows first so labels sit on top
    for a in arrows:
        pts = [S(proj(p)) for p in a["pts"]]
        col = RED
        w = int(6 * k)
        if a.get("kind") == "turn":
            for i in range(len(pts) - 1): d.line([pts[i], pts[i + 1]], fill=col, width=w, joint="curve")
        else:
            for i in range(len(pts) - 1):
                if a.get("dashed"): _dashed(d, pts[i], pts[i + 1], col, w, int(16 * k), int(10 * k))
                else: d.line([pts[i], pts[i + 1]], fill=col, width=w)
        for p in pts: d.ellipse([p[0] - w / 2, p[1] - w / 2, p[0] + w / 2, p[1] + w / 2], fill=col)
        _arrowhead(d, pts[-2], pts[-1], col, 24 * k)
        if a.get("step"):
            r = 17 * k; cx, cy = pts[0]
            d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=RED, outline=WHITE, width=int(3 * k))
            ff = _font(int(22 * k)); tt = d.textlength(str(a["step"]), font=ff)
            d.text((cx - tt / 2, cy - 17 * k), str(a["step"]), font=ff, fill=WHITE)
        if a.get("text"):
            f = _font(int(21 * k)); m = pts[len(pts) // 2] if len(pts) > 2 else ((pts[0][0] + pts[-1][0]) / 2, (pts[0][1] + pts[-1][1]) / 2)
            ox, oy = a.get("text_off", (14, -14)); tw = d.textlength(a["text"], font=f)
            x, y = m[0] + ox * k, m[1] + oy * k
            d.rounded_rectangle([x - 8 * k, y - 4 * k, x + tw + 8 * k, y + 28 * k], radius=14 * k, fill=RED)
            d.text((x, y - 1 * k), a["text"], font=f, fill=WHITE)
    for lb in labels:
        ax, ay = S(proj(lb["at"])); dx, dy = lb.get("to", (60, -60))
        tx, ty = ax + dx * k, ay + dy * k
        d.line([(ax, ay), (tx, ty)], fill=INK, width=int(2.6 * k))
        d.ellipse([ax - 6 * k, ay - 6 * k, ax + 6 * k, ay + 6 * k], fill=INK, outline=WHITE, width=int(2 * k))
        f = _font(int(22 * k)); fs = _font(int(17 * k), False)
        tag = lb.get("tag", ""); text = lb["text"]; sub = lb.get("sub", "")
        tw = max(d.textlength(text, font=f), d.textlength(sub, font=fs) if sub else 0)
        bw = tw + (46 * k if tag else 0) + 22 * k; bh = (34 + (24 if sub else 0)) * k
        x0 = tx - (bw if dx < 0 else 0); y0 = ty - bh / 2
        x0 = min(max(x0, 14 * k), im.size[0] - bw - 14 * k); y0 = min(max(y0, 14 * k), im.size[1] - bh - 14 * k)
        d.rounded_rectangle([x0, y0, x0 + bw, y0 + bh], radius=12 * k, fill=IVORY, outline=INK, width=int(2.2 * k))
        cx = x0 + 11 * k
        if tag:
            r = 15 * k
            d.ellipse([cx, y0 + bh / 2 - r, cx + 2 * r, y0 + bh / 2 + r], fill=INK)
            ff = _font(int(20 * k)); tt = d.textlength(tag, font=ff)
            d.text((cx + r - tt / 2, y0 + bh / 2 - 15 * k), tag, font=ff, fill=WHITE)
            cx += 2 * r + 9 * k
        d.text((cx, y0 + (4 if sub else 3) * k), text, font=f, fill=INK)
        if sub: d.text((cx, y0 + 29 * k), sub, font=fs, fill=(90, 86, 80))
    if banner:
        f = _font(int(26 * k)); tw = d.textlength(banner, font=f)
        d.rounded_rectangle([18 * k, 18 * k, 18 * k + tw + 34 * k, 18 * k + 48 * k], radius=24 * k, fill=INK)
        d.text((35 * k, 18 * k + 8 * k), banner, font=f, fill=WHITE)
    res = Image.alpha_composite(im, ov).convert("RGB").resize((W, W), Image.LANCZOS)
    out = out or f"{OUT}/r/{scene_name}_guide"
    res.save(out + ".jpg", quality=92); res.save(out + ".webp", quality=84, method=6)
    return out + ".webp"

def arc(center, r, a0, a1, z, n=10):
    """Points along an arc in the xy plane at height z, angles in degrees."""
    return [(center[0] + r * math.cos(math.radians(a0 + (a1 - a0) * i / n)), center[1] + r * math.sin(math.radians(a0 + (a1 - a0) * i / n)), z) for i in range(n + 1)]
