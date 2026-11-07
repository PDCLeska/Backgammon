"""Sunflower bookmark traced from Amir's picture (art/sunflower.png, 2026-11-06): his photo's bookmark as it is, for
himself (the design is the seller's: not for sale). Gold in the picture = brass, white = cut out; the inner lines are
thinned a little, the name band filled in and the name engraved in a handwriting font.

Cut from Amir's 100 x 150 brass plate (0.8 mm): the bookmark sits along one long edge, so the rest of the plate is left
for a second try if the first fails.
Scale: 40 mm wide, like bookmark.py; same tool and checks (bookmark.check).
Run from the repo root:  C:/Users/leska/cadenv/Scripts/python cad/bookmark_sunflower.py [check] [export]
Out (export/bookmarks/): bookmark_sunflower.dxf / .step / .stl (the bookmark, centred on 0,0);
sunflower_on_plate.dxf (on the plate, origin at the plate's front-left corner: layers plate (the stock, not cut),
outline, cut, engrave); sunflower_on_plate.png (the layout).
"""
import os, sys
import numpy as np
from scipy import ndimage

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bookmark as bm
from bookmark import W

PICTURE = os.path.join(ROOT, "art", "sunflower.png")
BAND_PX = (50, 590, 210, 1490)  # the name band in the picture (x0, y0, x1, y1 px): filled solid, the old name gone
GOLD_SAT = 0.35                 # saturation above this = gold (the background is white / grey)
THIN = 0.25                     # mm taken off each side of the inner lines: the picture's ~2.0 mm lines -> ~1.5
FRAME_KEEP = 2.6                # the outer frame (about 3 mm wide) and the name band keep their full width
T = 3.0                         # brass sheet (Amir, 2026-11-07: 3 mm; was 0.8)
PLATE = (200.0, 100.0)          # Amir's brass plate, x by y (mm) (2026-11-07: 200 x 100, the long side along X)
ROT = -90                       # the bookmark on the plate turned this much (Amir: rotate 90): tab right, name upright
MARGIN = 3.0                    # bookmark to the plate's left edge: the 1 mm end mill passes outside the outline
NAME = "Mrs. Poirier"          # Amir's son's teacher
FONT_FILE = "C:/Windows/Fonts/ITCEDSCR.TTF"   # Edwardian Script: the closest installed to Amir's sample
NAME_MARGIN = 1.5               # the name fits inside the blank band with this much brass round it
TEXT_D = 0.2                    # engraving depth
TEXT_H = None                   # font size, set by name_text() to fit the band
HOLE_D = 6.0                    # the string hole (Amir, 2026-11-07: a 2.6 mm leather cord; 6 takes it doubled, as a loop)
RING = 3.0                      # brass round the hole (the tab's radius = HOLE_D / 2 + RING)
NECK = 2.5                      # brass between the hole and the first cut-out under it (the tab moves up for it)
SPECK = 0.3                     # mm2: smaller gold or white bits are picture noise
SIMPLIFY = 0.02                 # mm: outlines kept this close to the trace


def picture():
    from PIL import Image
    a = np.asarray(Image.open(PICTURE).convert("RGB")).astype(float) / 255
    mx, mn = a.max(2), a.min(2)
    gold = ((mx - mn) / np.maximum(mx, 1e-6) > GOLD_SAT) | (mx < 0.8)    # (dark grey = the shaded metal edges)
    x0, y0, x1, y1 = BAND_PX
    gold[y0:y1, x0:x1] = True
    ys, xs = np.where(gold)
    px = W / (xs.max() - xs.min())                       # mm a pixel
    return gold, px, (xs.min() + xs.max()) / 2, (ys.min() + ys.max()) / 2


def masks():
    gold, px, cx, cy = picture()
    gold = ndimage.binary_closing(gold, np.ones((3, 3)))
    lab, n = ndimage.label(gold)                           # drop gold specks
    keep = ndimage.sum(gold, lab, range(1, n + 1)) * px ** 2 >= SPECK
    gold = np.isin(lab, np.flatnonzero(keep) + 1)
    outer = ndimage.binary_fill_holes(gold)
    holes = outer & ~gold
    lab, n = ndimage.label(holes)                          # fill white specks
    small = ndimage.sum(holes, lab, range(1, n + 1)) * px ** 2 < SPECK
    holes &= ~np.isin(lab, np.flatnonzero(small) + 1)
    # thinner inner lines: brass within THIN of a cut-out goes, except the frame and the name band
    h, w = gold.shape
    x0, y0, x1, y1 = BAND_PX
    keep = ndimage.distance_transform_edt(outer) * px <= FRAME_KEEP
    keep[y0:y1, :x1] = True
    near = ndimage.distance_transform_edt(~holes) * px <= THIN
    holes |= outer & near & ~keep
    X, Y = np.meshgrid((np.arange(w) - cx) * px, -(np.arange(h) - cy) * px)
    return X[::-1], Y[::-1], (outer & ~holes)[::-1], holes[::-1]      # rows bottom -> top, like bookmark.masks


def rdp(p, eps):
    """Douglas-Peucker: drop points within eps of the line through their neighbours."""
    if len(p) < 3:
        return p
    a, b = p[0], p[-1]
    d = b - a
    n = np.hypot(*d)
    dist = abs(d[0] * (p[:, 1] - a[1]) - d[1] * (p[:, 0] - a[0])) / n if n > 0 else np.hypot(*(p - a).T)
    i = int(np.argmax(dist))
    if dist[i] <= eps:
        return np.array([a, b])
    return np.vstack([rdp(p[:i + 1], eps)[:-1], rdp(p[i:], eps)])


def outlines():
    """The traced outlines in mm: (outer, [holes])."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    X, Y, metal, holes = masks()
    f = ndimage.gaussian_filter(metal.astype(float), 0.8)
    fig = plt.figure()                                   # its own figure: not drawn into a preview
    cs = fig.gca().contour(X, Y, f, levels=[0.5])
    rings = []
    for p in cs.allsegs[0]:
        if len(p) < 8:
            continue
        p = np.asarray(p)
        q = np.vstack([rdp(p[: len(p) // 2 + 1], SIMPLIFY)[:-1], rdp(p[len(p) // 2:], SIMPLIFY)])
        area = 0.5 * abs(np.dot(q[:, 0], np.roll(q[:, 1], 1)) - np.dot(q[:, 1], np.roll(q[:, 0], 1)))
        if len(q) >= 3 and area >= SPECK:
            rings.append((area, q))
    plt.close(fig)
    rings.sort(key=lambda r: -r[0])
    return retab(rings[0][1], [q for _, q in rings[1:]])


def retab(outer, holes):
    """The traced ring tab (~4 mm hole, 2 mm of brass) -> a round HOLE_D hole with RING of brass round it, moved up so
    NECK of brass is left above the cut-outs under it; the tab joins the frame (union)."""
    from shapely.geometry import Polygon, Point
    old = max(holes, key=lambda q: q[:, 1].mean())               # the string hole: the highest cut-out
    rest = [h for h in holes if h is not old]
    cx = old[:, 0].mean()
    under = max(h[np.abs(h[:, 0] - cx) < HOLE_D / 2 + 1][:, 1].max() for h in rest
                if (np.abs(h[:, 0] - cx) < HOLE_D / 2 + 1).any())
    cy = max(old[:, 1].mean(), under + NECK + HOLE_D / 2)
    body = Polygon(outer).buffer(0).union(Point(cx, cy).buffer(HOLE_D / 2 + RING, 128))
    if body.geom_type != "Polygon":
        body = max(body.geoms, key=lambda g: g.area)
    ring = lambda g: np.array(g.exterior.coords)[:-1]
    hole = np.array(Point(cx, cy).buffer(HOLE_D / 2, 128).exterior.coords)[:-1]
    return ring(body.simplify(SIMPLIFY)), [hole] + rest


def band():
    """The blank name band in mm: (x0, x1, y0, y1), from the outer edge to the cut-outs."""
    _, px, cx, cy = picture()
    x0, y0, x1, y1 = BAND_PX
    return -W / 2, (x1 - cx) * px, -(y1 - cy) * px, -(y0 - cy) * px


def name_text():
    """The name, reading up the band, as big as fits inside it (NAME_MARGIN all round), centred on it."""
    from build123d import Text, Pos, Rot
    bx0, bx1, by0, by1 = band()
    t = Rot(0, 0, 90) * Text(NAME, font_size=10, font_path=FONT_FILE)
    bb = t.bounding_box()
    k = min((bx1 - bx0 - 2 * NAME_MARGIN) / bb.size.X, (by1 - by0 - 2 * NAME_MARGIN) / bb.size.Y)
    global TEXT_H
    TEXT_H = round(10 * k, 1)
    t = Rot(0, 0, 90) * Text(NAME, font_size=TEXT_H, font_path=FONT_FILE)
    c = t.bounding_box().center()
    return Pos((bx0 + bx1) / 2 - c.X, (by0 + by1) / 2 - c.Y) * t


NAME_JSON = os.path.join(ROOT, "art", "sunflower_name.json")   # the name's letter outlines, for computers without the font


def name_loops():
    """The name as closed letter outlines (bookmark frame, mm): from the font when it is installed (and saved to
    NAME_JSON), else from NAME_JSON (the laptop and the cloud have no Edwardian Script)."""
    import json
    if os.path.exists(FONT_FILE):
        ring = lambda w: [(round(v.X, 4), round(v.Y, 4)) for v in w.positions(np.linspace(0, 1, 200))[:-1]]
        loops = [ring(w) for f in name_text().faces() for w in [f.outer_wire(), *f.inner_wires()]]
        json.dump(dict(name=NAME, font=os.path.basename(FONT_FILE), loops=loops), open(NAME_JSON, "w"))
        return [np.array(l) for l in loops]
    d = json.load(open(NAME_JSON))
    assert d["name"] == NAME, f"{NAME_JSON} holds {d['name']!r}: run once where {FONT_FILE} is installed"
    return [np.array(l) for l in d["loops"]]


def name_faces():
    """The letters as faces (counters as holes), from name_loops()."""
    from build123d import Face, Wire
    from matplotlib.path import Path
    loops = name_loops()
    area = lambda q: 0.5 * abs(np.dot(q[:, 0], np.roll(q[:, 1], 1)) - np.dot(q[:, 1], np.roll(q[:, 0], 1)))
    inside = lambda a, b: Path(b).contains_point(a[0])            # loop a inside loop b
    depth = [sum(inside(a, b) for b in loops if b is not a) for a in loops]
    wire = lambda q: Wire.make_polygon([(x, y, 0) for x, y in q], close=True)
    faces = []
    for a, da in zip(loops, depth):
        if da % 2 == 0:
            holes = [b for b, db in zip(loops, depth) if db == da + 1 and inside(b, a)]
            faces.append(Face(wire(a), [wire(h) for h in holes]))
    return faces


def face2d():
    from build123d import Face, Wire
    outer, holes = outlines()
    wire = lambda q: Wire.make_polygon([(x, y, 0) for x, y in q], close=True)
    return Face(wire(outer), [wire(q) for q in holes])


def build():
    from build123d import extrude, Pos
    body = extrude(face2d(), T)
    for f in name_faces():
        body -= Pos(0, 0, T - TEXT_D) * extrude(f, TEXT_D + 0.01)
    return body


def on_plate():
    """Where the bookmark goes on the plate: the move from its own frame (centred on 0,0) to the plate's (origin at
    the front-left corner): MARGIN from the left and front edges."""
    from build123d import Pos, Rot
    bb = (Rot(0, 0, ROT) * face2d()).bounding_box()
    return Pos(MARGIN - bb.min.X, MARGIN - bb.min.Y, 0) * Rot(0, 0, ROT)   # front-left corner (Amir): most plate left


def plate_xy(q):
    """Points in the bookmark's frame -> the plate's (on_plate(): turned ROT, then moved into the corner)."""
    loc = on_plate()
    a = np.radians(ROT)
    r = np.array([[np.cos(a), -np.sin(a)], [np.sin(a), np.cos(a)]])
    return np.asarray(q) @ r.T + np.array([loc.position.X, loc.position.Y])


def check():
    m = masks()
    X, Y, metal, holes = m
    px = W / (np.where(metal)[1].max() - np.where(metal)[1].min())
    dt = ndimage.distance_transform_edt(metal) * px
    ridge = (dt == ndimage.maximum_filter(dt, size=5)) & (dt > 0.2) & (dt < 1.4)
    bx0, bx1, by0, by1 = band()
    inner = (abs(X) < W / 2 - 4) & ~((X < bx1 + 0.5) & (Y > by0 - 0.5) & (Y < by1 + 0.5))
    lw = 2 * dt[ridge & inner]
    nl = np.vstack(name_loops())
    print(f"inner lines {np.median(lw):.2f} mm wide (most {np.percentile(lw, 10):.2f} to {np.percentile(lw, 90):.2f}), "
          f"plate {T:g} mm; name {NAME!r} {np.ptp(nl[:, 1]):.0f} mm long")
    bm.T = T
    ok = bm.check(m, PX=px)
    # on the plate: inside it with the tool's room all round, and the rest wide enough for a second try
    bb = (on_plate() * face2d()).bounding_box()
    fits = (bb.min.X >= bm.TOOL_D and bb.min.Y >= bm.TOOL_D and bb.max.X <= PLATE[0] - bm.TOOL_D
            and bb.max.Y <= PLATE[1] - bm.TOOL_D)
    rest = PLATE[0] - bb.max.X - bm.TOOL_D
    top = PLATE[1] - bb.max.Y - bm.TOOL_D
    o, hs = outlines()
    h = hs[0]
    print(f"string hole {np.ptp(h[:, 0]):.1f} mm, brass round it {RING:g}, above the cut-outs {NECK:g}; bookmark "
          f"{bb.size.X:.1f} x {bb.size.Y:.1f}; left over: {rest:.0f} x {PLATE[1]:.0f} beside it + {bb.size.X:.0f} x {top:.0f} above it")
    print(f"on the {PLATE[0]:.0f} x {PLATE[1]:.0f} plate: x {bb.min.X:.1f} .. {bb.max.X:.1f}, y {bb.min.Y:.1f} .. "
          f"{bb.max.Y:.1f}  {'OK' if fits else 'NO'}; left for a second try: {rest:.1f} x {PLATE[1]:.0f} mm "
          f"({'room for another' if rest >= bb.size.X + 2 * MARGIN else 'NOT enough for another'})")
    ok &= fits
    print("ALL OK" if ok else "SOMETHING TO FIX")
    return ok


def export():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from build123d import ExportDXF, export_step, export_stl, Unit, Rectangle, Pos
    out = os.path.join(ROOT, "export", "bookmarks")
    os.makedirs(out, exist_ok=True)
    import ezdxf
    outer, holes = outlines()
    names = name_loops()
    for fname, tf, plate in (("bookmark_sunflower", np.asarray, False), ("sunflower_on_plate", plate_xy, True)):
        doc = ezdxf.new(units=4); msp = doc.modelspace()          # units 4 = mm
        for l in (["plate"] if plate else []) + ["outline", "cut", "engrave"]:
            doc.layers.add(l)
        if plate:
            msp.add_lwpolyline([(0, 0), (PLATE[0], 0), PLATE, (0, PLATE[1])], close=True, dxfattribs={"layer": "plate"})
        poly = lambda q, layer: msp.add_lwpolyline([tuple(p) for p in tf(q)], close=True, dxfattribs={"layer": layer})
        poly(outer, "outline")                                    # one closed shape
        for q in holes:                                          # one closed shape per cut-out
            poly(q, "cut")
        for q in names:                                          # closed letter outlines (counters too)
            poly(q, "engrave")
        doc.saveas(os.path.join(out, fname + ".dxf"))
    f = face2d()
    s = build()
    export_step(s, os.path.join(out, "bookmark_sunflower.step"))
    export_stl(s, os.path.join(out, "bookmark_sunflower.stl"), tolerance=0.01, angular_tolerance=0.1)
    bb = s.bounding_box()
    print(f"  export/bookmarks/bookmark_sunflower.dxf ({len(f.inner_wires())} cut-outs), .step, .stl; "
          f"{bb.size.X:.1f} x {bb.size.Y:.1f} x {bb.size.Z:.1f} mm, valid: {s.is_valid}")
    print(f"  export/bookmarks/sunflower_on_plate.dxf (origin: the plate's front-left corner; closed shapes: 1 outline,"
          f" {len(holes)} cut-outs, {len(names)} letter outlines)")
    # preview: the plate, the bookmark on it as cut, the engraved name
    mv = on_plate()
    outer, holes = outlines()
    sh = plate_xy
    fig, ax = plt.subplots(figsize=(7, 4) if PLATE[0] > PLATE[1] else (4, 6), dpi=150)
    ax.add_patch(plt.Rectangle((0, 0), *PLATE, fc="#e7d3a0", ec="#8a7340", lw=0.8))
    ax.fill(*sh(outer).T, fc="#cda44a", ec="#3b2a10", lw=0.4)
    for q in holes:
        ax.fill(*sh(q).T, fc="#f4f1ea", lw=0)
    ring = lambda w: np.array([(v.X, v.Y) for v in w.positions(np.linspace(0, 1, 400))])
    for g in name_faces():
        g = mv * g
        ax.fill(*ring(g.outer_wire()).T, fc="#3b2a10", lw=0)
        for w in g.inner_wires():
            ax.fill(*ring(w).T, fc="#cda44a", lw=0)
    x1 = sh(outer)[:, 0].max()
    ax.text((x1 + PLATE[0]) / 2, PLATE[1] / 2, "left over", ha="center", va="center", color="#8a7340",
            fontsize=9)
    ax.set_xlim(-5, PLATE[0] + 5); ax.set_ylim(-5, PLATE[1] + 5); ax.set_aspect("equal")
    ax.set_xlabel("mm"); ax.set_title(f"Brass plate {PLATE[0]:.0f} x {PLATE[1]:.0f} x {T:g} mm (origin front-left)",
                                      fontsize=9)
    fig.savefig(os.path.join(out, "sunflower_on_plate.png"), bbox_inches="tight")
    plt.close(fig)
    print("  export/bookmarks/sunflower_on_plate.png")


if __name__ == "__main__":
    args = sys.argv[1:] or ["check"]
    if "check" in args:
        check()
    if "export" in args:
        export()
