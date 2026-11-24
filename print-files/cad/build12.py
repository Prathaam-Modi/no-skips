"""Range V4, Room Tone (24 Nov 2026): sculptural cover planters H1 Terrace, H2 Twist, H3 Echo.
Cover pots: the plant stays in its plastic nursery pot, which drops into the bore. No drainage hole, so PLA is fine indoors.
Feel test: outer walls at least 4 mm everywhere, 8 mm base, felt pads and logo underneath, form gradient (no colour gradient).
Two sizes: S fits a 3 inch (7.5 to 8 cm) nursery pot, M fits a 4 inch (10 cm) pot. One body colour per print, no supports.
Usage: NS_OUT=/tmp/out python3 build12.py"""
import math, json, os
import numpy as np
from ns import *
from ns import _cs
from build2 import logo

BASE = 8.0          # solid base
SIZES = {           # bore diameter, bore depth (pot height + 4 mm), outer reference radius
    "S": dict(bore=86.0, depth=78.0, R=52.0),
    "M": dict(bore=110.0, depth=100.0, R=65.0),
}

def under(m, R):
    """Logo, four 12 mm felt pad recesses (0.8 mm) and three 2 mm risers inside so the nursery pot does not sit in drained water."""
    lg = ext(affinity.scale(logo(0, 0, 0.75), -1, 1, origin=(0, 0)), 0.6, -0.01)
    pads = U([cyl(6.1, 0.8, -0.01, (R - 14) * math.cos(a), (R - 14) * math.sin(a)) for a in np.radians([45, 135, 225, 315])])
    return m - lg - pads

def bore(sz):
    b, d = SIZES[sz]["bore"] / 2, SIZES[sz]["depth"]
    H = BASE + d
    # bore with a 3 mm fillet at the floor and a 1 mm lead-in chamfer at the rim
    prof = [(0, BASE), (b - 3, BASE), (b - 0.9, BASE + 0.9), (b, BASE + 3), (b, H - 1.0), (b + 1.2, H + 0.2), (0, H + 0.2)]
    cut = revolve(prof, 160)
    feet = U([cyl(4, 2.0, BASE, (b - 14) * math.cos(a), (b - 14) * math.sin(a), seg=32) for a in np.radians([90, 210, 330])])
    return cut, feet, H

def finish(outer, sz):
    cut, feet, H = bore(sz)
    return under(U([outer - cut, feet]), SIZES[sz]["R"]), H

# ------------------------------------------------------------------ H1 Terrace
def terrace(sz):
    """Stepped tiers that get shorter toward the rim; each step goes in at 45 degrees, so nothing overhangs."""
    b, d = SIZES[sz]["bore"] / 2, SIZES[sz]["depth"]
    H = BASE + d
    n = 6; step = 1.6
    R = b + 5.0 + n * step                 # the base is the widest point, the rim keeps a 5 mm wall
    w = np.array([1.0 * 0.82 ** i for i in range(n)]); heights = (H - n * step) * w / w.sum()   # tiers shrink upward
    r_top = R - n * step
    assert r_top - b >= 4.0, ("Terrace rim wall", r_top - b)
    pts = [(0, 0), (R - 0.6, 0), (R, 0.6)]
    z = 0.0; r = R
    for i, h in enumerate(heights):
        z += h; pts.append((r, z))
        if i < n - 1:
            pts.append((r - step, z + step)); r -= step; z += step
    # rounded rim: 1.2 mm bevel out and in
    pts += [(r, H - 1.2), (r - 1.2, H)]
    pts[-1] = (r - 1.2, H); pts += [(0, H)]
    return finish(revolve(pts, 192), sz)

# ------------------------------------------------------------------ H2 Twist
def twist(sz):
    """Twenty soft flutes that rotate 36 degrees from base to rim; flute depth grows toward the rim."""
    R, b, d = SIZES[sz]["R"], SIZES[sz]["bore"] / 2, SIZES[sz]["depth"]
    H = BASE + d
    N, a0, a1 = 20, 0.4, 2.2           # flute depth at the base and at the rim
    hz = H - 1.2
    nt, nz = 480, 90
    th = np.linspace(0, 2 * math.pi, nt, endpoint=False)
    V = []
    for k in range(nz + 1):
        z = hz * k / nz; t = z / hz
        a = a0 + (a1 - a0) * t ** 1.4
        phi = math.radians(36.0) * t
        rr = R - a1 + a * np.cos(N * (th - phi))
        if z < 0.6: rr = rr - (0.6 - z)           # 45 degree chamfer at the bed edge, no shelf
        V += list(zip(rr * np.cos(th), rr * np.sin(th), np.full(nt, z)))
    V += [(0, 0, 0), (0, 0, hz)]
    bot, top = len(V) - 2, len(V) - 1
    T = []
    for k in range(nz):
        for i in range(nt):
            a_, b_ = k * nt + i, k * nt + (i + 1) % nt
            c_, d_ = a_ + nt, b_ + nt
            T += [(a_, b_, d_), (a_, d_, c_)]
    for i in range(nt):
        T += [(bot, (i + 1) % nt, i), (top, nz * nt + i, nz * nt + (i + 1) % nt)]
    mesh = m3.Mesh(np.asarray(V, np.float32), np.asarray(T, np.uint32))
    body_ = Manifold(mesh)
    assert body_.status() == m3.Error.NoError and body_.volume() > 0, body_.status()
    trough = R - 2 * a1
    assert trough - b >= 4.0, ("Twist wall at the trough", trough - b)
    cap = cyl(trough, 1.22, hz - 0.01, r2=trough - 1.2, seg=192)   # rounded-in rim
    outer = U([body_, cap])
    return finish(outer, sz)

# ------------------------------------------------------------------ H3 Echo
def echo(sz):
    """Horizontal ripples, deep at the rim and fading toward the base, like an echo dying out.
    Max slope of the wave is kept under 45 degrees (2 pi A / L <= 0.95), so no supports."""
    R, b, d = SIZES[sz]["R"], SIZES[sz]["bore"] / 2, SIZES[sz]["depth"]
    H = BASE + d
    zs = np.linspace(0, H - 1.2, 900)
    t = zs / (H - 1.2)
    L = 13.0 - 7.0 * t                                   # ripples tighten toward the rim (13 mm to 6 mm pitch)
    phase = np.concatenate([[0], np.cumsum(np.diff(zs) / ((L[1:] + L[:-1]) / 2))]) * 2 * math.pi
    A = 0.95 * L / (2 * math.pi) * (0.15 + 0.85 * t ** 1.3)    # under 45 degrees at every height
    Amax = float(A.max())
    belly = 2.2 * np.sin(math.pi * np.clip(t * 1.15, 0, 1)) # soft shoulder, widest a little above the middle
    r = R - 2.2 - Amax + belly + A * np.sin(phase)
    assert (r.min() - b) >= 4.0, ("Echo wall", r.min() - b)
    pts = [(0, 0), (r[0] - 0.6, 0)] + list(zip(r, zs))[1:] + [(r[-1] - 1.2, H), (0, H)]
    pts[2] = (r[0], 0.6)
    return finish(revolve(pts, 192), sz)

FORMS = [("H1", "terrace", "Terrace", terrace), ("H2", "twist", "Twist", twist), ("H3", "echo", "Echo", echo)]

def plant(sz, H):
    """Render prop: a nursery pot rim, soil and a few leaves."""
    b = SIZES[sz]["bore"] / 2
    soil = cyl(b - 3, 2, H - 8, seg=96)
    leaves = []
    rng = np.random.default_rng(3)
    for i in range(9):
        a = 2 * math.pi * i / 9 + rng.uniform(-0.2, 0.2)
        L = b * rng.uniform(1.1, 1.6)
        lf = Manifold.sphere(1.0, 32).scale((L / 2, L / 7, 1.6))
        lf = lf.rotate((0, -rng.uniform(35, 65), 0)).translate((L / 2 * 0.55, 0, 0)).rotate((0, 0, math.degrees(a)))
        leaves.append(lf.translate((0, 0, H - 6 + L * 0.25)))
    return [(soil, "soil"), (U(leaves), "leaf")]

if __name__ == "__main__":
    out = {}
    trio = []
    for pid, key, name, f in FORMS:
        p = Product(pid, key, name); gs = {}
        for sz in ("S", "M"):
            m, H = f(sz)
            p.part(f"{key}_{sz}", m, IVORY if pid != "H2" else BLACK, infill=0.25)
            gs[sz] = round(grams(m, 0.25), 1)
            if sz == "M":
                pl = plant(sz, H)
                p.scene(f"{key}", [(m, IVORY)] + pl)
                p.scene(f"{key}_black", [(m, BLACK)] + pl)
                p.scene(f"{key}_bare", [(m, IVORY)])
                p.scene(f"bp_{pid}", [(m, IVORY)]); p.scene(f"bpo_{pid}", [(m, IVORY)])
            else:
                trio.append((m, H))
            print(pid, sz, "height", H, "grams", gs[sz], "est h", round(0.47 + gs[sz] / 41.7, 2))
        p.note = f"{pid} {name} planter. S fits a 3 inch nursery pot, M fits a 4 inch pot. Estimates (25% infill): S {gs['S']} g, M {gs['M']} g."
        rep = p.export(); rep["grams_by_size"] = gs; out[pid] = rep
    # family shot: the three S pots in a row, ivory, black, ivory
    xs = [-112, 0, 112]; cols = [IVORY, BLACK, IVORY]
    fam = []
    for (m, H), x, c in zip(trio, xs, cols):
        fam.append((mv(m, x, 0, 0), c))
        fam += [(mv(pm, x, 0, 0), pc) for pm, pc in plant("S", H)]
    p0 = Product("H0", "family", "Family"); p0.scene("planters_family", fam); p0.export()
    json.dump(out, open(f"{OUT}/planters_report.json", "w"), indent=1)
