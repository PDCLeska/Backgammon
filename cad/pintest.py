"""Pin-flip test plate (Amir, 2026-11-04): a 100 x 150 x 10 epoxy blank that proves the three things the board needs:
  1. a small "board" on one side: a field pocket, 6 points V-carved (the board's width and V-bit), the rim line;
  2. the pin method for the flip: two pin holes on the flip line, OUTSIDE the board area, drilled through the blank
     into the 2 mm spoil board in the first setup; the second setup sits on the same pins. The pins are not the same
     distance from the middle, so the blank only fits back the right way round (a wrong turn doesn't go on the pins);
  3. the sea-floor lines engraved on the back (open sea, no islands, at the board's scale), V-bit engraving.
Plus two witness windows (outside the board area): a square cut from the back, a smaller one from the face; they
meet in the middle, and the ring round the small one shows the flip's error (equal all round = no error).

Order: setup 1 = BACK up (pins, back witnesses, map), flip about the pin line, setup 2 = FACE up (field, points,
rim line, face witnesses). The XY zero stays the same for both setups: do not re-probe XY, only Z.

Frame (blank): x along the 150 side, y across (100), z up from the back (0) to the face (T); centre at x = y = 0.
The pins are on y = 0 (the flip line). Setup 1 lies back up: X = x, Y = -y (turned over about the x axis).
DXFs are in each setup's own frame as it lies on the bed, origin at the blank's front-left corner.
Run:  python cad/pintest.py [check] [export]
"""
import json, os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path[:0] = [HERE, os.path.join(ROOT, "art")]
from build123d import *
from board import (CARVERA_X, CARVERA_Y, TOOL_D, VBIT_K, VBIT_D, FILL_P, PT_EDGE, PT_W, PT_BASE,
                   LINE_W, LINE_GAP, LINE_D, ENGRAVE_D)

# ---------------------------------------------------------------- blank (measure it: T sets the witness depths)
L, W, T = 150.0, 100.0, 10.0

# ---------------------------------------------------------------- pins (the kit's pins: MEASURE the diameter)
PIN_D = 4.0                    # the Carvera Air's own dowel pins (10 in the box, for the corner bracket): 4 mm (confirm)
PIN_FIT = 0.0                  # 4 mm circle, cut as a 2D Pocket with the 1/8" end mill (drilling can't: bit < hole)
PIN_X = (-62.0, 56.0)          # on the flip line, not symmetric: only the right turn fits the pins
PIN_INTO = 1.0                 # into the 2 mm MDF spoil board (Amir has 2 mm): 1 mm left above the aluminium bed.
SPOIL = 2.0                    # the pins only locate (tape + CA hold the blank), so 1 mm of grip is enough

# ---------------------------------------------------------------- face: a small board (the board's own sizes)
N_PTS = 3                      # points a side
FIELD = N_PTS * PT_W           # 82.5 square
POCKET = 2.0                   # field depth
POCKET_R = TOOL_D / 2
MID = 16.0                     # between the two rows of tips
PT_LEN = (FIELD - 2 * PT_EDGE - MID) / 2
PT_DEPTH = FILL_P              # V-carve depth below the field floor (the board's)
BOARD = FIELD / 2 + LINE_GAP + LINE_W     # the board area's half size (to the rim line's outer edge)

# ---------------------------------------------------------------- back: the map
MAP = 88.0                     # map square on the back, centred under the board
MAP_CENTRE = (23.769, 37.152)  # lon, lat: open sea S of the Saronic Gulf (Amir: no islands, just lines), 100-1080 m deep,
                               # a ridge and small seamounts; found by searching the GMRT data for a land-free square
MAP_STEP = 100                 # a depth line every 100 m

# ---------------------------------------------------------------- witness windows (outside the board area)
WIT = [(-66.0, 38.0), (66.0, -38.0)]      # blank frame, two opposite corners: shows shift and turn
WIT_BACK, WIT_BACK_D = 8.0, 6.0           # square from the back, depth
WIT_FACE, WIT_FACE_D = 5.0, 5.0           # square from the face: the two meet (overlap below)


def setup_xy(x, y, setup):
    """Blank frame -> the setup's DXF frame (origin front-left corner of the blank as it lies)."""
    return (x + L / 2, (-y if setup == 1 else y) + W / 2)


# ---------------------------------------------------------------- map (art/topo.py data and scale)
def make_map():
    import topo
    from scipy.ndimage import gaussian_filter
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    lon, lat, z = topo.load()
    _, s, k, *_ = topo.frame()
    X, Y = np.meshgrid((lon - MAP_CENTRE[0]) * k * s, (lat - MAP_CENTRE[1]) * s)
    zs = gaussian_filter(z, topo.SMOOTH)
    h = MAP / 2
    win = (abs(X) <= h + 3) & (abs(Y) <= h + 3)
    r0, r1 = np.where(win.any(1))[0][[0, -1]]; c0, c1 = np.where(win.any(0))[0][[0, -1]]
    X, Y, zs = X[r0:r1 + 1, c0:c1 + 1], Y[r0:r1 + 1, c0:c1 + 1], zs[r0:r1 + 1, c0:c1 + 1]
    assert zs[(abs(X) <= h) & (abs(Y) <= h)].max() < 0, "land in the map square"
    levels = sorted(-d for d in range(MAP_STEP, int(-zs.min()) + 1, MAP_STEP))
    cs = plt.contour(X, Y, zs, levels=levels)
    lines = []
    for lev, segs in zip(cs.levels, cs.allsegs):
        for p in segs:
            if len(p) > 1:
                lines += topo.clip_runs([dict(level=float(lev), pts=np.round(p, 2).tolist())], MAP, MAP)
    plt.close("all")
    lines = [l for l in lines if np.sum(np.hypot(*np.diff(np.array(l["pts"]), axis=0).T)) >= topo.MIN_LEN / 2]
    gap, where = topo.min_gap(lines)
    m = dict(info=dict(centre=MAP_CENTRE, size=MAP, step=MAP_STEP, n_lines=len(lines), close_share=round(gap, 3)),
             lines=lines)   # back view (as setup 1 lies), mm, origin at the blank centre
    json.dump(m, open(os.path.join(ROOT, "art", "pintest_map.json"), "w"))
    return m


def back_map():
    p = os.path.join(ROOT, "art", "pintest_map.json")
    return json.load(open(p)) if os.path.exists(p) else make_map()


# ---------------------------------------------------------------- face geometry
def point_x(i):
    return -FIELD / 2 + PT_W * (i + 0.5)


def point_tri(i, front):
    x = point_x(i)
    y0 = -(FIELD / 2 - PT_EDGE) if front else FIELD / 2 - PT_EDGE
    s = 1 if front else -1
    c = [(x - PT_BASE / 2, y0), (x + PT_BASE / 2, y0), (x, y0 + s * PT_LEN)]
    return c if front else c[::-1]


def point_face(i, front, grow=0.0):
    f = Polygon(*point_tri(i, front), align=None)
    return f if grow == 0 else offset(f, grow, kind=Kind.INTERSECTION).faces()[0]


def point_pocket(i, front):
    z0 = T - POCKET
    top = Pos(0, 0, z0 + 0.01) * point_face(i, front, 0.01 * VBIT_K)
    bot = Pos(0, 0, z0 - PT_DEPTH) * point_face(i, front, -PT_DEPTH * VBIT_K)
    return loft([top, bot])


def rim_band():
    g = Rectangle(FIELD, FIELD)
    return (offset(g, LINE_GAP + LINE_W, kind=Kind.ARC) - offset(g, LINE_GAP, kind=Kind.ARC)).faces()[0]


def body():
    b = Box(L, W, T, align=(Align.CENTER, Align.CENTER, Align.MIN))
    for px in PIN_X:
        b -= Pos(px, 0, T / 2) * Cylinder((PIN_D + PIN_FIT) / 2, T + 1)
    for wx, wy in WIT:
        b -= Pos(wx, wy, WIT_BACK_D / 2 - 0.5) * Box(WIT_BACK, WIT_BACK, WIT_BACK_D + 1)
        b -= Pos(wx, wy, T - WIT_FACE_D / 2 + 0.5) * Box(WIT_FACE, WIT_FACE, WIT_FACE_D + 1)
    field = Pos(0, 0, T - POCKET / 2 + 0.5) * Box(FIELD, FIELD, POCKET + 1)
    b -= fillet(field.edges().filter_by(Axis.Z), POCKET_R)
    for i in range(N_PTS):
        for front in (True, False):
            b -= point_pocket(i, front)
    b -= Pos(0, 0, T + 0.01) * extrude(rim_band(), LINE_D + 0.01, dir=(0, 0, -1), taper=45 - 0.01)
    return b


# ---------------------------------------------------------------- check
def check():
    ok = True
    flag = lambda c: "ok" if c else "PROBLEM"
    print(f"Blank {L:.0f} x {W:.0f} x {T:.0f} epoxy")
    m = min(CARVERA_X - L, CARVERA_Y - W) - TOOL_D
    print(f"  on the Carvera: {m:.0f} mm to spare  {flag(m >= 0)}"); ok &= m >= 0
    print("Pins")
    pr = (PIN_D + PIN_FIT) / 2
    out = min(abs(px) for px in PIN_X) - pr - BOARD
    edge = L / 2 - max(abs(px) for px in PIN_X) - pr
    print(f"  {PIN_D} pins (the Carvera Air's kit pins), holes {PIN_D + PIN_FIT:.2f} at x = {PIN_X[0]:+.0f} / {PIN_X[1]:+.0f}"
          f" on the flip line, {PIN_INTO:.1f} into the {SPOIL:.0f} mm spoil board ({SPOIL - PIN_INTO:.1f} left above the bed)")
    ok &= SPOIL - PIN_INTO >= 0.8
    print(f"  outside the board area by {out:.1f}, blank end {edge:.1f}  {flag(out >= 5 and edge >= 5)}"); ok &= out >= 5 and edge >= 5
    wrong = min(abs(-a - b) for a in PIN_X for b in PIN_X)
    print(f"  wrong turn (end for end): pins {wrong:.0f} mm off their holes, it can't go on  {flag(wrong >= 3)}"); ok &= wrong >= 3
    print("Witness windows")
    ov = WIT_BACK_D + WIT_FACE_D - T
    ring = (WIT_BACK - WIT_FACE) / 2
    wo = min(max(abs(wx), abs(wy)) for wx, wy in WIT) - WIT_BACK / 2 - BOARD
    print(f"  back {WIT_BACK:.0f} sq x {WIT_BACK_D:.0f} deep, face {WIT_FACE:.0f} sq x {WIT_FACE_D:.0f}: overlap {ov:.1f}"
          f" (open up to a {WIT_BACK_D + WIT_FACE_D:.0f} thick blank), ring {ring:.1f} = flip error you can read  {flag(ov > 0)}")
    ok &= ov > 0
    near_pin = min(np.hypot(wx - px, wy) for wx, wy in WIT for px in PIN_X) - WIT_BACK / 2 * 1.42 - pr
    print(f"  outside the board area by {wo:.1f}, clear of the pins by {near_pin:.1f}  {flag(wo >= 3 and near_pin >= 3)}")
    ok &= wo >= 3 and near_pin >= 3
    print("Face: small board")
    reach = VBIT_D / 2 / VBIT_K
    print(f"  field {FIELD:.1f} square, {POCKET:.0f} deep; 6 points {PT_BASE:.0f} x {PT_LEN:.1f}, V-carved {PT_DEPTH} below"
          f" the floor (V-bit reaches {reach:.1f})  {flag(PT_DEPTH <= reach)}"); ok &= PT_DEPTH <= reach
    side = W / 2 - BOARD
    print(f"  rim line {LINE_W} wide, {LINE_GAP:.0f} off the field wall; board area {2 * BOARD:.1f} sq, {side:.1f} to the long edges"
          f"  {flag(side >= 2)}"); ok &= side >= 2
    under = T - POCKET - PT_DEPTH - ENGRAVE_D
    print(f"  epoxy left under the points (back engraved {ENGRAVE_D}): {under:.1f}  {flag(under >= 4)}"); ok &= under >= 4
    bm = back_map()["info"]
    print(f"Back: open-sea map (no land), {bm['size']:.0f} mm square, every {bm['step']} m: {bm['n_lines']} lines,"
          f" {100 * bm['close_share']:.1f}% of the length closer than 0.6 mm")
    ok &= MAP / 2 <= W / 2 - 2
    b = body()
    print(f"Model {'valid' if b.is_valid else 'INVALID'}"); ok &= b.is_valid
    print("ALL OK" if ok else "PROBLEMS")
    return ok


# ---------------------------------------------------------------- export
def export():
    import ezdxf
    out = os.path.join(ROOT, "export")
    os.makedirs(out, exist_ok=True)
    b = body()
    export_step(b, os.path.join(out, "pintest.step")); export_stl(b, os.path.join(out, "pintest.stl"), tolerance=0.02)
    sq = lambda cx, cy, a, s: [setup_xy(cx + dx * a / 2, cy + dy * a / 2, s) for dx, dy in ((-1, -1), (1, -1), (1, 1), (-1, 1))]
    blank = [(0, 0), (L, 0), (L, W), (0, W)]

    # setup 1: back up
    doc = ezdxf.new(); msp = doc.modelspace()
    for n in ("blank", "pins", "witness", "engrave"):
        doc.layers.add(n)
    msp.add_lwpolyline(blank, close=True, dxfattribs={"layer": "blank"})
    for px in PIN_X:
        msp.add_circle(setup_xy(px, 0, 1), (PIN_D + PIN_FIT) / 2, dxfattribs={"layer": "pins"})
    for wx, wy in WIT:
        msp.add_lwpolyline(sq(wx, wy, WIT_BACK, 1), close=True, dxfattribs={"layer": "witness"})
    for l in back_map()["lines"]:      # map in back view = setup 1 as it lies: X = u, Y = v
        msp.add_lwpolyline([(u + L / 2, v + W / 2) for u, v in l["pts"]], dxfattribs={"layer": "engrave"})
    doc.saveas(os.path.join(out, "pintest_1_back.dxf"))

    # the pin holes alone (Amir makes them in the CAM): the blank outline + 2 circles, setup 1 frame
    doc = ezdxf.new(); msp = doc.modelspace()
    msp.add_lwpolyline(blank, close=True)
    for px in PIN_X:
        msp.add_circle(setup_xy(px, 0, 1), (PIN_D + PIN_FIT) / 2)
    doc.saveas(os.path.join(out, "pintest_pins.dxf"))

    # setup 2: face up
    doc = ezdxf.new(); msp = doc.modelspace()
    for n in ("blank", "pins", "witness", "field", "points", "rim_line"):
        doc.layers.add(n)
    msp.add_lwpolyline(blank, close=True, dxfattribs={"layer": "blank"})
    for px in PIN_X:
        msp.add_circle(setup_xy(px, 0, 2), (PIN_D + PIN_FIT) / 2, dxfattribs={"layer": "pins"})
    for wx, wy in WIT:
        msp.add_lwpolyline(sq(wx, wy, WIT_FACE, 2), close=True, dxfattribs={"layer": "witness"})
    f = fillet(Rectangle(FIELD, FIELD).vertices(), POCKET_R).faces()[0]
    for w in (f.outer_wire(),):
        msp.add_lwpolyline([setup_xy(p.X, p.Y, 2) for p in w.positions([k / 200 for k in range(201)])],
                           close=True, dxfattribs={"layer": "field"})
    for i in range(N_PTS):
        for front in (True, False):
            msp.add_lwpolyline([setup_xy(x, y, 2) for x, y in point_tri(i, front)], close=True,
                               dxfattribs={"layer": "points"})
    band = rim_band()
    for w in [band.outer_wire(), *band.inner_wires()]:
        msp.add_lwpolyline([setup_xy(p.X, p.Y, 2) for p in w.positions([k / 400 for k in range(401)])],
                           close=True, dxfattribs={"layer": "rim_line"})
    doc.saveas(os.path.join(out, "pintest_2_face.dxf"))
    preview()
    print("  export/pintest.step / .stl, pintest_pins.dxf, pintest_1_back.dxf, pintest_2_face.dxf, art/pintest.png")


def preview():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import Rectangle as R, Circle as C, Polygon as P
    fig, axs = plt.subplots(1, 2, figsize=(12, 4.6), dpi=130)
    for ax, s, title in ((axs[0], 1, "Setup 1: BACK up (first)"), (axs[1], 2, "Setup 2: FACE up (after the flip)")):
        ax.add_patch(R((0, 0), L, W, fc="#cfe3e6", ec="k"))
        ax.add_patch(R(setup_xy(-BOARD, -BOARD, 2), 2 * BOARD, 2 * BOARD, fc="none", ec="#999", ls="--", lw=0.7))
        for px in PIN_X:
            ax.add_patch(C(setup_xy(px, 0, s), (PIN_D + PIN_FIT) / 2 + 0.6, fc="#c33"))
        ax.axhline(W / 2, color="#c33", lw=0.6, ls=":")
        a = WIT_BACK if s == 1 else WIT_FACE
        for wx, wy in WIT:
            x, y = setup_xy(wx, wy, s)
            ax.add_patch(R((x - a / 2, y - a / 2), a, a, fc="#555"))
        if s == 1:
            for l in back_map()["lines"]:
                p = np.array(l["pts"])
                ax.plot(p[:, 0] + L / 2, p[:, 1] + W / 2, color="#123", lw=0.6)
        else:
            x0, y0 = setup_xy(-FIELD / 2, -FIELD / 2, 2)
            ax.add_patch(R((x0, y0), FIELD, FIELD, fc="#b9d3d7", ec="#456"))
            for i in range(N_PTS):
                for front in (True, False):
                    col = "#1fb5b0" if (i + (0 if front else 1)) % 2 == 0 else "#123e7a"
                    ax.add_patch(P([setup_xy(x, y, 2) for x, y in point_tri(i, front)], fc=col))
            band = rim_band()
            for w in [band.outer_wire(), *band.inner_wires()]:
                q = np.array([setup_xy(p.X, p.Y, 2) for p in w.positions([k / 200 for k in range(201)])])
                ax.plot(q[:, 0], q[:, 1], color="#1fb5b0", lw=0.8)
        ax.text(2, W + 3, "front-left = XY zero (both setups)", fontsize=7)
        ax.set_title(title, fontsize=10); ax.set_xlim(-5, L + 5); ax.set_ylim(-5, W + 8); ax.set_aspect("equal")
        ax.set_xticks([0, 75, 150]); ax.set_yticks([0, 50, 100])
    fig.suptitle("Pin-flip test plate: flip about the red dotted pin line (pins not symmetric: only the right turn fits)", fontsize=10)
    fig.savefig(os.path.join(ROOT, "art", "pintest.png"), bbox_inches="tight")
    plt.close(fig)


if __name__ == "__main__":
    args = sys.argv[1:] or ["check"]
    if "map" in args or not os.path.exists(os.path.join(ROOT, "art", "pintest_map.json")):
        make_map()
    if "check" in args:
        check()
    if "export" in args:
        export()
