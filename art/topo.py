"""Sea-floor contour map for the back of the board (Amir: ocean topography, Saronic Gulf to Syros).

Data: GMRT (Global Multi-Resolution Topography, gmrt.org), art/gmrt_aegean.asc, ~120 m grid.
The map runs across both backs, in "back view": the open board turned face down (about the hinge line), so the
right half is on the left. Closed, the right half's back is the lid: it shows the Saronic Gulf, the left half's
back (underneath) the Cyclades.
Out: art/back_map.json (polylines in mm, back view, origin at the hinge line / board centre), art/back_map.svg,
export/bg_back_right.dxf / bg_back_left.dxf (each half's own back-view frame, for the engraving setup).
Run:  C:/Users/leska/cadenv/Scripts/python art/topo.py
"""
import json, os, sys
import numpy as np
from math import cos, radians, hypot
from scipy.ndimage import gaussian_filter
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path[:0] = [os.path.join(ROOT, "cad")]
import board as bd

LON, LAT = (23.28, 25.06), (36.98, 38.02)     # the area (cropped to the map's shape below)
LEVELS = [0] + [-d for d in range(100, 2001, 100)]   # coast + every 100 m of depth
SMOOTH = 2.0                   # grid cells (gaussian): calmer lines
MARGIN = 12.0                  # map edge to the board edge (all round; the map runs on across the hinge)
MIN_LEN = 6.0                  # drop contour bits shorter than this (mm)


def load():
    with open(os.path.join(HERE, "gmrt_aegean.asc")) as f:
        hdr = {k: float(v) for k, v in (next(f).split() for _ in range(6))}
    z = np.loadtxt(os.path.join(HERE, "gmrt_aegean.asc"), skiprows=6)[::-1]   # rows south -> north
    lon = hdr["xllcorner"] + hdr["cellsize"] * np.arange(int(hdr["ncols"]))
    lat = hdr["yllcorner"] + hdr["cellsize"] * np.arange(int(hdr["nrows"]))
    return lon, lat, z


def frame():
    """lon/lat -> mm (back view): the area scaled to fit the backs inside MARGIN, centred."""
    k = cos(radians(sum(LAT) / 2))
    w_deg, h_deg = (LON[1] - LON[0]) * k, LAT[1] - LAT[0]
    W, H = 2 * bd.HALF_W - 2 * MARGIN, bd.HALF_L - 2 * MARGIN
    s = min(W / w_deg, H / h_deg)
    c_lon, c_lat = sum(LON) / 2, sum(LAT) / 2
    return (lambda lo, la: ((lo - c_lon) * k * s, (la - c_lat) * s)), s, k, W, H


def contours(lon, lat, z, to_mm, W, H):
    zs = gaussian_filter(z, SMOOTH)
    X, Y = to_mm(*np.meshgrid(lon, lat))
    cs = plt.contour(X, Y, zs, levels=sorted(LEVELS))
    lines = []
    for lev, segs in zip(cs.levels, cs.allsegs):
        for p in segs:
            if len(p) < 3:
                continue
            L = np.sum(np.hypot(*np.diff(p, axis=0).T))
            if L >= MIN_LEN:
                lines.append(dict(level=float(lev), pts=np.round(p[::2] if len(p) > 40 else p, 2).tolist()))
    plt.close("all")
    return lines


def clip_runs(lines, W, H):
    """Contours cut at the map edge break into separate runs (no line jumping across the gap)."""
    out = []
    for l in lines:
        run = []
        for x, y in l["pts"]:
            if abs(x) <= W / 2 and abs(y) <= H / 2:
                run.append([x, y])
            elif len(run) > 1:
                out.append(dict(level=l["level"], pts=run)); run = []
            else:
                run = []
        if len(run) > 1:
            out.append(dict(level=l["level"], pts=run))
    return out


def min_gap(lines, close=0.6):
    """How much of the lines runs closer than `close` mm to another line (steep slopes: the engraved lines merge
    there into one heavier line) -> (share of the length, where the most is)."""
    from scipy.spatial import cKDTree
    pts, ids = [], []
    for i, l in enumerate(lines):
        p = np.array(l["pts"])
        # resample at 0.25 mm so the check sees the whole line
        d = np.hypot(*np.diff(p, axis=0).T); c = np.concatenate([[0], np.cumsum(d)])
        t = np.arange(0, c[-1], 0.25)
        pts.append(np.c_[np.interp(t, c, p[:, 0]), np.interp(t, c, p[:, 1])]); ids.append(np.full(len(t), i))
    P, I = np.vstack(pts), np.concatenate(ids)
    tree = cKDTree(P)
    pairs = tree.query_pairs(close, output_type="ndarray")
    pairs = pairs[I[pairs[:, 0]] != I[pairs[:, 1]]]
    near = np.unique(pairs.ravel()) if len(pairs) else np.array([], int)
    if not len(near):
        return 0.0, None
    return len(near) / len(P), np.median(P[near], axis=0).round(0).tolist()


def split_halves(polys):
    """Back-view polylines -> {"R": [...], "L": [...]} in the model frame (x = -u: the board turned back over),
    each line cut where it crosses the hinge line."""
    out = {"R": [], "L": []}
    for p in polys:
        q = [(-u, v) for u, v in p]
        run = [q[0]]
        for a, b in zip(q, q[1:]):
            if (a[0] > 0) != (b[0] > 0) and a[0] != b[0]:
                t = a[0] / (a[0] - b[0]); m = (0.0, a[1] + t * (b[1] - a[1]))
                run.append(m); out["R" if a[0] > 0 else "L"].append(run); run = [m]
            run.append(b)
        if len(run) > 1:
            out["R" if sum(x for x, _ in run) > 0 else "L"].append(run)
    return {k: [np.round(r, 2).tolist() for r in v if len(r) > 1] for k, v in out.items()}


def write_dxf(halves):
    """One DXF per half, in that half's own frame as it lies on the bed back up for the engraving: origin at the
    blank's front-left corner of the half outline (back view), hinge edge at X = HALF_W (right half) / X = 0 (left)."""
    import ezdxf
    out = os.path.join(ROOT, "export")
    os.makedirs(out, exist_ok=True)
    for side, name in (("R", "right"), ("L", "left")):
        doc = ezdxf.new(); msp = doc.modelspace()
        doc.layers.add("outline"); doc.layers.add("engrave")
        msp.add_lwpolyline([(0, 0), (bd.HALF_W, 0), (bd.HALF_W, bd.HALF_L), (0, bd.HALF_L)], close=True, dxfattribs={"layer": "outline"})
        dx = bd.HALF_W if side == "R" else 0.0          # back view u = -x; right half u in [-HALF_W, 0]
        for run in halves[side]:
            msp.add_lwpolyline([(-x + dx, y + bd.HALF_L / 2) for x, y in run], dxfattribs={"layer": "engrave"})
        doc.saveas(os.path.join(out, f"bg_back_{name}.dxf"))
        print(f"  export/bg_back_{name}.dxf ({len(halves[side])} lines; hinge edge at X = {bd.HALF_W if side == 'R' else 0:.0f})")


def main():
    lon, lat, z = load()
    to_mm, s, k, W, H = frame()
    lines = clip_runs(contours(lon, lat, z, to_mm, W, H), W, H)
    gap, where = min_gap(lines)
    info = dict(area=dict(lon=LON, lat=LAT), size=[W, H], scale=round(1 / (s / 111.32e6)), levels=LEVELS,
                n_lines=len(lines), close_share=round(gap, 3))
    halves = split_halves([l["pts"] for l in lines])
    json.dump(dict(info=info, lines=lines, halves=halves), open(os.path.join(HERE, "back_map.json"), "w"))
    write_dxf(halves)
    # preview
    fig, ax = plt.subplots(figsize=(2 * bd.HALF_W / 25.4, bd.HALF_L / 25.4), dpi=110)
    ax.add_patch(plt.Rectangle((-bd.HALF_W, -bd.HALF_L / 2), 2 * bd.HALF_W, bd.HALF_L, fc="#6b4329"))
    for l in lines:
        p = np.array(l["pts"])
        ax.plot(p[:, 0], p[:, 1], color="#2b1a0f" if l["level"] < 0 else "#e8d6b8", lw=0.6 if l["level"] < 0 else 0.9)
    ax.axvline(0, color="#000", lw=0.4, ls=":")
    ax.set_xlim(-bd.HALF_W, bd.HALF_W); ax.set_ylim(-bd.HALF_L / 2, bd.HALF_L / 2); ax.set_aspect("equal"); ax.axis("off")
    fig.savefig(os.path.join(HERE, "back_map.png"), bbox_inches="tight", pad_inches=0.05)
    plt.close(fig)
    print(f"map {W:.0f} x {H:.0f} mm, 1:{info['scale']:,}, {len(lines)} contour lines (coast + every 100 m)")
    print(f"lines closer than 0.6 mm (merge when engraved): {100 * gap:.1f}% of the length" + (f", mostly near {where}" if where else ""))


if __name__ == "__main__":
    main()
