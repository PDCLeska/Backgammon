"""The coaster's back (the practice piece, Amir: same techniques as the board): a square of the sea-floor map round
Aegina, at the board's scale. Land (Aegina, Angistri, the Methana / Epidaurus coast) is cut in as flat recesses
(V-carved coast, flat floor); the sea's depth lines are lasered.

Uses the board map's data and contours (art/topo.py). Out: art/coaster_map.json, art/coaster_map.png (back view, mm,
origin at the coaster's centre).
Run:  C:/Users/leska/cadenv/Scripts/python art/coaster_map.py
"""
import json, os, sys
import numpy as np
from math import cos, radians
from scipy.ndimage import gaussian_filter
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path[:0] = [HERE, os.path.join(ROOT, "cad")]
import topo

CENTRE = (23.47, 37.70)        # lon, lat: Aegina a little north of the middle, Angistri, Methana
SIZE = 92.0                    # map square on the coaster's back (mm)
STEP = 50                      # a depth line every 50 m (the Saronic Gulf is shallow: 100 m gives only a few)
MIN_ISLAND = 4.0               # land smaller than this (mm2) isn't recessed (too small to cut): its coast is lasered


def main():
    lon, lat, z = topo.load()
    _, s, k, *_ = topo.frame()                           # the board map's scale (mm per degree of latitude)
    to_mm = lambda lo, la: ((lo - CENTRE[0]) * k * s, (la - CENTRE[1]) * s)
    half = SIZE / 2
    zs = gaussian_filter(z, topo.SMOOTH)
    X, Y = to_mm(*np.meshgrid(lon, lat))
    win = (abs(X) <= half + 3) & (abs(Y) <= half + 3)
    r0, r1 = np.where(win.any(1))[0][[0, -1]]; c0, c1 = np.where(win.any(0))[0][[0, -1]]
    X, Y, zs = X[r0:r1 + 1, c0:c1 + 1], Y[r0:r1 + 1, c0:c1 + 1], zs[r0:r1 + 1, c0:c1 + 1]
    # sea depth lines (laser)
    levels = [-d for d in range(STEP, int(-zs.min()) + 1, STEP)][::-1]
    cs = plt.contour(X, Y, zs, levels=levels)
    sea = []
    for lev, segs in zip(cs.levels, cs.allsegs):
        for p in segs:
            sea += [dict(level=float(lev), pts=r["pts"]) for r in topo.clip_runs([dict(level=lev, pts=p.tolist())], SIZE, SIZE)]
    sea = [l for l in sea if np.sum(np.hypot(*np.diff(np.array(l["pts"]), axis=0).T)) >= topo.MIN_LEN / 2]
    # land: filled areas above 0, the map's edge closing them (recesses)
    cf = plt.contourf(X, Y, np.clip(zs, -1, 1), levels=[0, 2])
    from build123d import Face, Wire, Rectangle
    box = Rectangle(SIZE, SIZE)
    land, small = [], []
    for poly in cf.allsegs[0]:
        p = np.round(poly[::2] if len(poly) > 60 else poly, 2)
        p = p[np.r_[True, np.hypot(*np.diff(p, axis=0).T) > 0.05]]
        if np.hypot(*(p[0] - p[-1])) < 0.05:
            p = p[:-1]
        if len(p) < 3:
            continue
        f = Face(Wire.make_polygon([(x, y, 0) for x, y in p], close=True))
        if not f.is_valid:
            continue
        for g in (f & box).faces():                   # clipped by the map's square (an exact cut, no spikes)
            q = [(round((e @ 0).X, 2), round((e @ 0).Y, 2)) for e in g.outer_wire().order_edges()]   # in path order
            (land if g.area >= MIN_ISLAND else small).append(q)
    plt.close("all")
    # coast of the islets too small to recess: lasered with the sea
    sea += [dict(level=0.0, pts=p) for p in small]
    info = dict(centre=CENTRE, size=SIZE, step=STEP, n_sea=len(sea), n_land=len(land), n_islets=len(small))
    json.dump(dict(info=info, sea=sea, land=land), open(os.path.join(HERE, "coaster_map.json"), "w"))
    fig, ax = plt.subplots(figsize=(4, 4), dpi=150)
    ax.add_patch(plt.Rectangle((-half, -half), SIZE, SIZE, fc="#6b4329"))
    for p in land:
        p = np.array(p); ax.fill(p[:, 0], p[:, 1], fc="#7d5236", ec="#e8d6b8", lw=0.6)
    for l in sea:
        p = np.array(l["pts"]); ax.plot(p[:, 0], p[:, 1], color="#1d120a", lw=0.5)
    ax.set_xlim(-half, half); ax.set_ylim(-half, half); ax.set_aspect("equal"); ax.axis("off")
    fig.savefig(os.path.join(HERE, "coaster_map.png"), bbox_inches="tight", pad_inches=0.02)
    plt.close(fig)
    print(f"coaster map {SIZE:.0f} mm square round Aegina: {len(land)} land recesses, {len(sea)} laser lines "
          f"(every {STEP} m; {len(small)} islets lasered as outlines)")


if __name__ == "__main__":
    main()
