"""Bookmark (Amir, capability test): a flat pierced bookmark in the style of his photos (brass, fully rounded ends, a
ring tab on top for a tassel, a name band down the middle of the left side, the rest open with a design inside). Our
own design inside, not a copy of the photo's: an olive branch, for the Greek theme.

Cut through from a 1 mm brass sheet with a 1 mm end mill (the Carvera mills brass), or from 3 mm walnut / plywood with
the laser: the same outlines. The name is engraved into the band.
Run from the repo root:  C:/Users/leska/cadenv/Scripts/python cad/bookmark.py [check] [export]
Out: export/bookmark.dxf (layers outline / cut / engrave), bookmark.step / .stl, art/bookmark.png (preview).
"""
import os, sys
import numpy as np
from scipy.interpolate import CubicSpline
from scipy import ndimage

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from board import CARVERA_X, CARVERA_Y

NAME = "Amir"
W, L, T = 40.0, 130.0, 1.0      # brass sheet; 3.0 for laser-cut wood
END_R = W / 2                   # ends fully round
FRAME = 2.5                     # border all round
BAND_W, BAND_LEN = 8.0, 70.0    # name band on the left, across the middle
TAB_R, TAB_HOLE = 6.0, 3.5      # ring tab on top (radius) and its hole (diameter) for a tassel or ribbon
TAB_Y = L / 2 + 1.5             # tab centre
TOOL_D = 1.0                    # end mill for the cut-through (brass); the gaps must be wider
MIN_W = 1.0                     # thinnest brass that's still stiff enough
TEXT_H, TEXT_D = 5.5, 0.25      # name: letter height, engraving depth
FONT = "Georgia"

X0, X1 = -W / 2 + FRAME + BAND_W, W / 2 - FRAME          # the window beside the band, across
Y0, Y1 = -L / 2 + FRAME, L / 2 - FRAME                     # the window, along

# olive branch: the stem (x, y) runs from the bottom frame to the top frame; leaves and olives hang off it
STEM = [(3.0, Y0 - 2), (6.5, -40), (3.0, -16), (7.0, 8), (4.5, 32), (2.0, Y1 + 2)]
STEM_W = (2.4, 1.4)             # width at the bottom, at the top
# (where along the stem 0..1, side +1 right / -1 left, angle off the stem in deg, length, width)
LEAVES = [(0.06, 1, 44, 13, 4.6), (0.13, -1, 42, 15, 4.8), (0.24, 1, 40, 15, 4.8), (0.33, -1, 40, 15, 4.8),
          (0.44, 1, 38, 15, 4.8), (0.55, -1, 38, 15, 4.6), (0.66, 1, 36, 14, 4.6), (0.76, -1, 36, 14, 4.4),
          (0.86, 1, 38, 12, 4.2), (0.92, -1, 50, 9, 3.6)]
LEAF_BEND = 0.12                # leaves curve up towards the tip (share of their length)
# olives hang back down from the stem: (where along the stem, side, stalk angle off the stem, stalk length,
# olive length, olive width)
OLIVES = [(0.275, -1, 100, 4.5, 6.8, 4.4), (0.585, 1, 100, 4.5, 6.6, 4.3), (0.705, -1, 100, 4.0, 6.2, 4.0)]


def stem_curve(n=200):
    p = np.array(STEM)
    s = np.r_[0, np.cumsum(np.hypot(*np.diff(p, axis=0).T))]
    cs = CubicSpline(s / s[-1], p, bc_type="natural")
    t = np.linspace(0, 1, n)
    return t, cs(t), cs(t, 1)


def ribbon(pts, w0, w1):
    """A strip along a polyline, tapering w0 -> w1."""
    d = np.gradient(pts, axis=0)
    nrm = np.c_[-d[:, 1], d[:, 0]] / np.hypot(*d.T)[:, None]
    w = np.linspace(w0, w1, len(pts))[:, None] / 2
    return np.vstack([pts + nrm * w, (pts - nrm * w)[::-1]])


def at(t):
    ts, P, D = stem_curve(400)
    i = int(round(t * (len(ts) - 1)))
    return P[i], np.degrees(np.arctan2(D[i, 1], D[i, 0]))


def leaf(base, ang, length, width, bend=0.0, n=40):
    """Pointed both ends, widest a third of the way out, the midline curving by `bend` (+ = left of the leaf's
    direction); the base starts inside the stem."""
    s = np.linspace(-0.08, 1, n)
    h = width / 2 * np.sin(np.pi * np.clip(s, 0, 1)) ** 0.9 * (1 - 0.35 * np.clip(s, 0, 1))
    m = bend * length * np.clip(s, 0, 1) ** 2
    pts = np.vstack([np.c_[s * length, m + h], np.c_[s * length, m - h][::-1]])
    a = np.radians(ang)
    R = np.array([[np.cos(a), -np.sin(a)], [np.sin(a), np.cos(a)]])
    return pts @ R.T + base


def ellipse(c, ang, a, b, n=48):
    t = np.linspace(0, 2 * np.pi, n, endpoint=False)
    pts = np.c_[a / 2 * np.cos(t), b / 2 * np.sin(t)]
    r = np.radians(ang)
    return pts @ np.array([[np.cos(r), np.sin(r)], [-np.sin(r), np.cos(r)]]) + c


def branch():
    """The branch as polygons (mm): stem, leaves, olive stalks, olives."""
    _, P, _ = stem_curve()
    polys = [ribbon(P, *STEM_W)]
    for t, side, off, ln, wd in LEAVES:
        p, a = at(t)
        polys.append(leaf(p, a - side * off, ln, wd, side * LEAF_BEND))
    for t, side, off, sl, ol, ow in OLIVES:
        p, a = at(t)
        ang = a - side * off
        tip = p + sl * np.array([np.cos(np.radians(ang)), np.sin(np.radians(ang))])
        polys.append(ribbon(np.linspace(p, tip, 12), 1.3, 1.2))
        polys.append(ellipse(tip + (ol / 2 - 0.6) * np.array([np.cos(np.radians(ang)), np.sin(np.radians(ang))]),
                             ang, ol, ow))
    return polys


# ---------- 2D mask (for the checks and the preview) ----------
PX = 0.05                       # mm per pixel


def rrect(X, Y, cx, cy, w, h, r):
    dx = np.maximum(abs(X - cx) - (w / 2 - r), 0)
    dy = np.maximum(abs(Y - cy) - (h / 2 - r), 0)
    return dx ** 2 + dy ** 2 <= r ** 2


def masks():
    from matplotlib.path import Path
    xs = np.arange(-W / 2 - 1, W / 2 + 1, PX)
    ys = np.arange(-L / 2 - 1, TAB_Y + TAB_R + 1, PX)
    X, Y = np.meshgrid(xs, ys)
    tab = np.hypot(X, Y - TAB_Y)
    outer = rrect(X, Y, 0, 0, W, L, END_R) | (tab <= TAB_R)
    band = (X < X0) & (abs(Y) <= BAND_LEN / 2)
    win = rrect(X, Y, 0, 0, W - 2 * FRAME, L - 2 * FRAME, END_R - FRAME) & ~band
    hole = tab <= TAB_HOLE / 2
    pts = np.c_[X.ravel(), Y.ravel()]
    br = np.zeros(X.shape, bool)
    for p in branch():
        br |= Path(p).contains_points(pts).reshape(X.shape)
    holes = (win & ~br) | hole
    return X, Y, outer & ~holes, holes


def disk(d, px=PX):
    r = int(round(d / 2 / px))
    y, x = np.ogrid[-r:r + 1, -r:r + 1]
    return x * x + y * y <= r * r


def check(m=None, PX=PX):
    """The cut checks on a 2D mask (X, Y, metal, holes) at PX mm a pixel: this bookmark's, or a traced one's."""
    X, Y, metal, holes = m or masks()
    ok = True
    ys, xs = np.where(metal)
    w, l = (xs.max() - xs.min()) * PX, (ys.max() - ys.min()) * PX
    print(f"bookmark {w:.0f} x {l:.0f} x {T:g} mm; bed {CARVERA_X:.0f} x {CARVERA_Y:.0f}: fits "
          f"{'OK' if w + TOOL_D < CARVERA_Y and l + TOOL_D < CARVERA_X else 'NO'}")
    lab, n = ndimage.label(metal)
    n = int((ndimage.sum(metal, lab, range(1, n + 1)) * PX ** 2 > 0.1).sum())     # (single pixels at tips: raster noise)
    print(f"  one piece (nothing falls out when cut): {n} piece(s)  {'OK' if n == 1 else 'NO'}")
    ok &= n == 1
    # holes the end mill can't get into: what's left after opening with the tool's disk
    miss = holes & ~ndimage.binary_opening(holes, disk(TOOL_D, PX))
    ml, mn = ndimage.label(miss)
    # where a leaf meets the stem the corner is sharp: the tool leaves a small round fillet there (under ~1.2 mm2,
    # can't be seen). Anything bigger is a real slot too narrow for the tool: two shapes would be joined.
    area = ndimage.sum(miss, ml, range(1, mn + 1)) * PX ** 2
    big = [s for s, a in zip(ndimage.find_objects(ml), area) if a > 1.2]
    print(f"  inside corners left round by the {TOOL_D:g} mm end mill: {mn} (largest {max(area, default=0):.2f} mm2)")
    print(f"  gaps narrower than the end mill (would stay uncut): {len(big)}  {'OK' if not big else 'NO'}")
    for s in big[:6]:
        print(f"    near x {X[s][0, 0]:.1f} .. {X[s][0, -1]:.1f}, y {Y[s][0, 0]:.1f} .. {Y[s][-1, 0]:.1f}")
    ok &= not big
    # brass thinner than MIN_W (leaf tips are always pointed: count only the longer bits)
    thin = metal & ~ndimage.binary_opening(metal, disk(MIN_W, PX))
    tl, tn = ndimage.label(thin)
    longs = [s for s in ndimage.find_objects(tl) if max(s[0].stop - s[0].start, s[1].stop - s[1].start) * PX > 2.5]
    print(f"  brass thinner than {MIN_W:g} mm for more than 2.5 mm (besides the pointed tips): {len(longs)}  "
          f"{'OK' if not longs else 'NO'}")
    for s in longs[:6]:
        print(f"    near x {X[s][0, 0]:.1f} .. {X[s][0, -1]:.1f}, y {Y[s][0, 0]:.1f} .. {Y[s][-1, 0]:.1f}")
    ok &= not longs
    print("ALL OK" if ok else "SOMETHING TO FIX")
    return ok


# ---------- 3D + files ----------
def face2d():
    from build123d import Face, Wire, SlotOverall, Rectangle, Circle, Pos, Rot
    outer = Rot(0, 0, 90) * SlotOverall(L, W) + Pos(0, TAB_Y) * Circle(TAB_R)
    win = Rot(0, 0, 90) * SlotOverall(L - 2 * FRAME, W - 2 * FRAME)
    win -= Pos((X0 - W / 2) / 2, 0) * Rectangle(X0 + W / 2, BAND_LEN)     # band, run into the frame
    br = None
    for p in branch():
        f = Face(Wire.make_polygon([(x, y, 0) for x, y in p], close=True))
        br = f if br is None else br + f
    return outer - (win - br) - Pos(0, TAB_Y) * Circle(TAB_HOLE / 2)


def name_text():
    from build123d import Text, Pos, Rot
    cx = -W / 2 + FRAME + BAND_W / 2
    return Pos(cx, 0) * Rot(0, 0, 90) * Text(NAME, font_size=TEXT_H, font=FONT)


def build():
    from build123d import extrude, Pos
    body = extrude(face2d(), T)
    txt = Pos(0, 0, T - TEXT_D) * extrude(name_text(), TEXT_D + 0.01)
    return body - txt


def preview():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    X, Y, metal, _ = masks()
    img = np.zeros(metal.shape + (3,))
    img[:] = (0.93, 0.92, 0.89)
    img[metal] = (0.80, 0.64, 0.30)
    fig, ax = plt.subplots(figsize=(2.6, 7), dpi=160)
    ax.imshow(img, origin="lower", extent=(X[0, 0], X[0, -1], Y[0, 0], Y[-1, 0]))
    ax.text(-W / 2 + FRAME + BAND_W / 2, 0, NAME, rotation=90, ha="center", va="center",
            fontsize=TEXT_H * 2.2, family="Georgia", color="#3b2a10")
    ax.set_aspect("equal"); ax.axis("off")
    out = os.path.join(ROOT, "art", "bookmark.png")
    fig.savefig(out, bbox_inches="tight", pad_inches=0.05)
    plt.close(fig)
    print(f"  {os.path.relpath(out, ROOT)}")


def export():
    from build123d import ExportDXF, export_step, export_stl, Unit
    out = os.path.join(ROOT, "export")
    os.makedirs(out, exist_ok=True)
    fs = face2d().faces()
    assert len(fs) == 1, f"{len(fs)} faces: the bookmark should be one piece"
    f = fs[0]
    d = ExportDXF(unit=Unit.MM)
    d.add_layer("outline"); d.add_layer("cut"); d.add_layer("engrave")
    d.add_shape(f.outer_wire(), layer="outline")
    d.add_shape(f.inner_wires(), layer="cut")
    d.add_shape(name_text().faces(), layer="engrave")
    d.write(os.path.join(out, "bookmark.dxf"))
    s = build()
    export_step(s, os.path.join(out, "bookmark.step"))
    export_stl(s, os.path.join(out, "bookmark.stl"), tolerance=0.01, angular_tolerance=0.1)
    print(f"  export/bookmark.dxf ({len(f.inner_wires())} cut-outs), bookmark.step, bookmark.stl; valid: {s.is_valid}")
    preview()


if __name__ == "__main__":
    args = sys.argv[1:] or ["check"]
    if "check" in args:
        check()
    if "export" in args:
        export()
