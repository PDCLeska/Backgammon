"""The coaster on the epoxy blank (Amir, 2026-11-04): the full practice piece, every technique, on Makera's epoxy tooling
board (150 x 101 x 10). Was the pin-flip test plate; Amir: "this is the coaster", do all of it.

  Back (setup 1): pin holes, back witness squares, the sea-floor lines (open sea, no islands, V-bit engraved), the back
  edge chamfered.
  Flip about the pin line (front to back).
  Face (setup 2): field pocket, 6 points + the diamond + the rim line V-carved (no epoxy this time: Amir), face witness
  squares, the outline chamfered, then the outline cut through with tabs (+ tape + CA under the blank).

Coaster 90 x 90 (the 110.5 design doesn't fit the 101 wide blank), corners r8, 10 thick, both edges chamfered 1.5
(Amir): the back edge in setup 1, the face edge in setup 2, both with the V-bit (2D Chamfer on the outline). Points 24 wide (the board's are
27.5: Amir chose smaller points to keep 3 a side).
Pins: 2 holes on the flip line, outside the coaster, not the same distance from the ends, so only the right turn fits.
Witness windows (outside the coaster): a square from the back, a smaller one from the face; they meet, and the ring
round the small one shows the flip's error (look in from the back; equal all round = no error).
The XY zero stays the same for both setups (the bracket corner): do not re-probe XY, only Z.

Frame (blank): x along the 150 side, y across (101), z up from the back (0) to the face (T); centre at x = y = 0.
The pins are on y = 0 (the flip line). Setup 1 lies back up: X = x, Y = -y (turned over about the x axis).
DXFs are in each setup's own frame as it lies on the bed, origin at the blank's front-left corner.
Run:  python cad/pintest.py [map] [check] [export]
"""
import json, os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path[:0] = [HERE, os.path.join(ROOT, "art")]
from build123d import *
from board import (CARVERA_X, CARVERA_Y, TOOL_D, VBIT_K, VBIT_D, FILL_P, PT_EDGE, LINE_W, LINE_GAP, LINE_D,
                   ENGRAVE_D, DIA_L, DIA_W, DIA_D, EDGE_CH)

# ---------------------------------------------------------------- blank
L, W, T = 150.0, 101.0, 10.0       # Amir measured 150 x 101 (Makera epoxy tooling board, 10 thick: check with calipers)

# ---------------------------------------------------------------- pins
PIN_D = 4.0                    # the Carvera Air's own 4 mm dowel pins (Amir)
PIN_FIT = 0.0                  # 4 mm circle, cut as a 2D Pocket with the 1/8" end mill (drilling can't: bit < hole)
PIN_X = (-62.0, 56.0)          # on the flip line, not symmetric: only the right turn fits the pins
PIN_INTO = 1.0                 # into the 2 mm MDF spoil board: 1 mm left above the aluminium bed
SPOIL = 2.0

# ---------------------------------------------------------------- the coaster
C = 90.0                       # 90 x 90
CORNER_R = 8.0
N_PTS = 3                      # points a side
PW = 24.0                      # point pitch (the board: 27.5)
PB = PW - 1.5                  # point base
FIELD = N_PTS * PW             # 72 square
POCKET = 3.0                   # field depth (holds a drip)
POCKET_R = TOOL_D / 2
MID = 16.0                     # between the two rows of tips: the diamond
PT_LEN = (FIELD - 2 * PT_EDGE - MID) / 2
PT_DEPTH = FILL_P              # V-carve depth below the field floor (the board's)
THROUGH = 0.3                  # the outline goes this far into the spoil board
TAB_W, TAB_H, N_TABS = 5.0, 1.5, 4    # tabs on the outline: length, height (left above the bottom), one per side

# ---------------------------------------------------------------- back: the map
MAP = 76.0                     # map square on the back, centred (inside the r8 corners with room)
MAP_CENTRE = (23.769, 37.152)  # lon, lat: open sea S of the Saronic Gulf (Amir: no islands, just lines),
                               # a ridge and small seamounts; found by searching the GMRT data for a land-free square
MAP_STEP = 100                 # a depth line every 100 m

# ---------------------------------------------------------------- witness windows (outside the coaster)
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
    depth = zs[(abs(X) <= h) & (abs(Y) <= h)]
    m = dict(info=dict(centre=MAP_CENTRE, size=MAP, step=MAP_STEP, n_lines=len(lines), close_share=round(gap, 3),
                       depth=[round(float(-depth.max())), round(float(-depth.min()))]),
             lines=lines)   # back view (as setup 1 lies), mm, origin at the blank centre
    json.dump(m, open(os.path.join(ROOT, "art", "pintest_map.json"), "w"))
    return m


def back_map():
    p = os.path.join(ROOT, "art", "pintest_map.json")
    m = json.load(open(p)) if os.path.exists(p) else None
    return m if m and m["info"]["size"] == MAP and m["info"].get("centre") == list(MAP_CENTRE) else make_map()


# ---------------------------------------------------------------- face geometry
def point_x(i):
    return -FIELD / 2 + PW * (i + 0.5)


def point_tri(i, front):
    x = point_x(i)
    y0 = -(FIELD / 2 - PT_EDGE) if front else FIELD / 2 - PT_EDGE
    s = 1 if front else -1
    c = [(x - PB / 2, y0), (x + PB / 2, y0), (x, y0 + s * PT_LEN)]
    return c if front else c[::-1]


def diamond_pts():
    return [(-DIA_L / 2, 0), (0, -DIA_W / 2), (DIA_L / 2, 0), (0, DIA_W / 2)]


def grown(pts, g):
    f = Polygon(*pts, align=None)
    return f if g == 0 else offset(f, g, kind=Kind.INTERSECTION).faces()[0]


def v_pocket(pts, z0, depth):
    """V-carved pocket (90 deg bit): the outline at z0, walls at 45 deg, a flat floor `depth` down."""
    return loft([Pos(0, 0, z0 + 0.01) * grown(pts, 0.01 * VBIT_K), Pos(0, 0, z0 - depth) * grown(pts, -depth * VBIT_K)])


def rim_band():
    g = Rectangle(FIELD, FIELD)
    return (offset(g, LINE_GAP + LINE_W, kind=Kind.ARC) - offset(g, LINE_GAP, kind=Kind.ARC)).faces()[0]


def outline_face():
    return fillet(Rectangle(C, C).vertices(), CORNER_R).faces()[0]


def coaster():
    """The finished coaster (centred, back at z = 0). The map lines are engraved from the DXF (not modelled)."""
    b = extrude(outline_face(), T)
    b = chamfer([e for e in b.edges() if e.center().Z > T - 0.01 or e.center().Z < 0.01], EDGE_CH)   # both edges (Amir)
    field = Pos(0, 0, T - POCKET / 2 + 0.5) * Box(FIELD, FIELD, POCKET + 1)
    b -= fillet(field.edges().filter_by(Axis.Z), POCKET_R)
    floor = T - POCKET
    for i in range(N_PTS):
        for front in (True, False):
            b -= v_pocket(point_tri(i, front), floor, PT_DEPTH)
    b -= v_pocket(diamond_pts(), floor, DIA_D - 0.05)
    b -= Pos(0, 0, T + 0.01) * extrude(rim_band(), LINE_D + 0.01, dir=(0, 0, -1), taper=45 - 0.01)
    return b


# ---------------------------------------------------------------- check
def check():
    ok = True
    flag = lambda c: "ok" if c else "PROBLEM"
    print(f"Blank {L:.0f} x {W:.0f} x {T:.0f} epoxy tooling board; coaster {C:.0f} x {C:.0f} x {T:.0f}, corners r{CORNER_R:.0f}")
    side = W / 2 - C / 2 - TOOL_D
    print(f"  outline + the bit inside the blank: {side:.1f} to the long edges  {flag(side >= 1.5)}"); ok &= side >= 1.5
    print("Pins")
    pr = (PIN_D + PIN_FIT) / 2
    out = min(abs(px) for px in PIN_X) - pr - (C / 2 + TOOL_D)
    edge = L / 2 - max(abs(px) for px in PIN_X) - pr
    print(f"  {PIN_D:.0f} mm pins, holes at X {setup_xy(PIN_X[0], 0, 1)[0]:.0f} / {setup_xy(PIN_X[1], 0, 1)[0]:.0f}, Y {W / 2:.1f};"
          f" {PIN_INTO:.0f} into the {SPOIL:.0f} mm spoil board ({SPOIL - PIN_INTO:.0f} left above the bed)")
    print(f"  clear of the outline cut by {out:.1f}, blank end {edge:.1f}  {flag(out >= 3 and edge >= 5)}"); ok &= out >= 3 and edge >= 5
    wrong = min(abs(-a - b) for a in PIN_X for b in PIN_X)
    print(f"  wrong turn (end for end): pins {wrong:.0f} mm off their holes, it can't go on  {flag(wrong >= 3)}"); ok &= wrong >= 3
    print("Witness windows")
    ov = WIT_BACK_D + WIT_FACE_D - T
    wo = min(max(abs(wx), abs(wy)) for wx, wy in WIT) - WIT_BACK / 2 - (C / 2 + TOOL_D)
    print(f"  back {WIT_BACK:.0f} sq x {WIT_BACK_D:.0f}, face {WIT_FACE:.0f} sq x {WIT_FACE_D:.0f}: overlap {ov:.1f},"
          f" ring {(WIT_BACK - WIT_FACE) / 2:.1f}; clear of the outline cut by {wo:.1f}  {flag(ov > 0 and wo >= 3)}")
    ok &= ov > 0 and wo >= 3
    print("Face")
    reach = VBIT_D / 2 / VBIT_K
    print(f"  field {FIELD:.0f} square, {POCKET:.0f} deep; 6 points {PB:.1f} x {PT_LEN:.1f} V-carved {PT_DEPTH} below the floor,"
          f" diamond {DIA_L:.0f} x {DIA_W:.0f} x {DIA_D}; V-bit reaches {reach:.1f}  {flag(max(PT_DEPTH, DIA_D) <= reach)}")
    ok &= max(PT_DEPTH, DIA_D) <= reach
    tips = FIELD / 2 - PT_EDGE - PT_LEN
    gap = tips - DIA_W / 2
    print(f"  diamond to the point tips {gap:.1f}  {flag(gap >= 1.5)}"); ok &= gap >= 1.5
    rim = (C - FIELD) / 2
    outside = rim - LINE_GAP - LINE_W - EDGE_CH
    print(f"  both edges chamfered {EDGE_CH} (back: setup 1, face: setup 2)")
    print(f"  rim {rim:.0f}: field wall | {LINE_GAP:.0f} | rim line {LINE_W} | {outside:.1f} | chamfer {EDGE_CH}  {flag(outside >= 1.5)}")
    ok &= outside >= 1.5
    under = T - POCKET - PT_DEPTH - ENGRAVE_D
    print(f"  under the points (map engraved {ENGRAVE_D} on the back): {under:.1f}  {flag(under >= 3.5)}"); ok &= under >= 3.5
    print(f"  outline: {T + THROUGH:.1f} deep ({THROUGH} into the spoil board), {N_TABS} tabs {TAB_W:.0f} long x {TAB_H} high")
    bm = back_map()["info"]
    mc = np.hypot(MAP / 2 - (C / 2 - CORNER_R), MAP / 2 - (C / 2 - CORNER_R)) + 1 <= CORNER_R - EDGE_CH   # inside the back chamfer
    print(f"Back: open-sea map (no land), {MAP:.0f} mm square, {bm['depth'][0]}-{bm['depth'][1]} m, a line every {bm['step']} m:"
          f" {bm['n_lines']} lines, {100 * bm['close_share']:.1f}% closer than 0.6 mm; inside the round corners  {flag(mc)}")
    ok &= mc
    b = coaster()
    print(f"Model {'valid' if b.is_valid else 'INVALID'}"); ok &= b.is_valid
    print("ALL OK" if ok else "PROBLEMS")
    return ok


# ---------------------------------------------------------------- export
def export():
    import ezdxf
    out = os.path.join(ROOT, "export")
    os.makedirs(out, exist_ok=True)
    b = coaster()
    export_step(b, os.path.join(out, "pintest.step")); export_stl(b, os.path.join(out, "pintest.stl"), tolerance=0.02)
    sq = lambda cx, cy, a, s: [setup_xy(cx + dx * a / 2, cy + dy * a / 2, s) for dx, dy in ((-1, -1), (1, -1), (1, 1), (-1, 1))]
    blank = [(0, 0), (L, 0), (L, W), (0, W)]
    wire_pts = lambda w, s, n=400: [setup_xy(p.X, p.Y, s) for p in w.positions([k / n for k in range(n + 1)])]
    ol = outline_face().outer_wire()

    # setup 1: back up
    doc = ezdxf.new(); msp = doc.modelspace()
    for n in ("blank", "pins", "witness", "engrave", "outline"):
        doc.layers.add(n)
    msp.add_lwpolyline(blank, close=True, dxfattribs={"layer": "blank"})
    for px in PIN_X:
        msp.add_circle(setup_xy(px, 0, 1), (PIN_D + PIN_FIT) / 2, dxfattribs={"layer": "pins"})
    for wx, wy in WIT:
        msp.add_lwpolyline(sq(wx, wy, WIT_BACK, 1), close=True, dxfattribs={"layer": "witness"})
    for l in back_map()["lines"]:      # map in back view = setup 1 as it lies: X = u, Y = v
        msp.add_lwpolyline([(u + L / 2, v + W / 2) for u, v in l["pts"]], dxfattribs={"layer": "engrave"})
    msp.add_lwpolyline(wire_pts(ol, 1), close=True, dxfattribs={"layer": "outline"})   # 2D Chamfer 1.5 (not cut through here)
    doc.saveas(os.path.join(out, "pintest_1_back.dxf"))

    # the pin holes alone
    doc = ezdxf.new(); msp = doc.modelspace()
    msp.add_lwpolyline(blank, close=True)
    for px in PIN_X:
        msp.add_circle(setup_xy(px, 0, 1), (PIN_D + PIN_FIT) / 2)
    doc.saveas(os.path.join(out, "pintest_pins.dxf"))

    # setup 2: face up
    doc = ezdxf.new(); msp = doc.modelspace()
    for n in ("blank", "pins", "witness", "field", "points", "diamond", "rim_line", "outline"):
        doc.layers.add(n)
    msp.add_lwpolyline(blank, close=True, dxfattribs={"layer": "blank"})
    for px in PIN_X:
        msp.add_circle(setup_xy(px, 0, 2), (PIN_D + PIN_FIT) / 2, dxfattribs={"layer": "pins"})
    for wx, wy in WIT:
        msp.add_lwpolyline(sq(wx, wy, WIT_FACE, 2), close=True, dxfattribs={"layer": "witness"})
    f = fillet(Rectangle(FIELD, FIELD).vertices(), POCKET_R).faces()[0]
    msp.add_lwpolyline(wire_pts(f.outer_wire(), 2, 200), close=True, dxfattribs={"layer": "field"})
    for i in range(N_PTS):
        for front in (True, False):
            msp.add_lwpolyline([setup_xy(x, y, 2) for x, y in point_tri(i, front)], close=True, dxfattribs={"layer": "points"})
    msp.add_lwpolyline([setup_xy(x, y, 2) for x, y in diamond_pts()], close=True, dxfattribs={"layer": "diamond"})
    band = rim_band()
    for w in [band.outer_wire(), *band.inner_wires()]:
        msp.add_lwpolyline(wire_pts(w, 2), close=True, dxfattribs={"layer": "rim_line"})
    msp.add_lwpolyline(wire_pts(ol, 2), close=True, dxfattribs={"layer": "outline"})
    doc.saveas(os.path.join(out, "pintest_2_face.dxf"))
    preview()
    print("  export/pintest.step / .stl (the coaster), pintest_1_back.dxf, pintest_2_face.dxf, pintest_pins.dxf, art/pintest.png")


def preview():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import Rectangle as R, Circle as Ci, Polygon as P
    fig, axs = plt.subplots(1, 2, figsize=(12, 4.6), dpi=130)
    ol = np.array([(p.X, p.Y) for p in outline_face().outer_wire().positions([k / 300 for k in range(301)])])
    for ax, s, title in ((axs[0], 1, "Setup 1: BACK up (first)"), (axs[1], 2, "Setup 2: FACE up (after the flip)")):
        ax.add_patch(R((0, 0), L, W, fc="#e4e1da", ec="k"))
        q = np.array([setup_xy(x, y, s) for x, y in ol])
        ax.add_patch(P(q, fc="#cfe3e6", ec="#1f7f86", lw=1.2))
        for px in PIN_X:
            ax.add_patch(Ci(setup_xy(px, 0, s), (PIN_D + PIN_FIT) / 2, fc="#c33"))
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
            ax.add_patch(P([setup_xy(x, y, 2) for x, y in diamond_pts()], fc="#1fb5b0"))
            band = rim_band()
            for w in [band.outer_wire(), *band.inner_wires()]:
                q = np.array([setup_xy(p.X, p.Y, 2) for p in w.positions([k / 200 for k in range(201)])])
                ax.plot(q[:, 0], q[:, 1], color="#1fb5b0", lw=0.8)
            for k in range(N_TABS):       # tabs, mid-side
                ang = k * np.pi / 2
                x, y = setup_xy(np.cos(ang) * (C / 2 + TOOL_D / 2), np.sin(ang) * (C / 2 + TOOL_D / 2), 2)
                ax.add_patch(R((x - 2.5, y - 2.5), 5, 5, fc="#e60", alpha=0.8))
        ax.text(2, W + 3, "front-left = XY zero (both setups)", fontsize=7)
        ax.set_title(title, fontsize=10); ax.set_xlim(-5, L + 5); ax.set_ylim(-5, W + 8); ax.set_aspect("equal")
        ax.set_xticks([0, 13, 75, 131, 150]); ax.set_yticks([0, W / 2, W])
    fig.suptitle(f"Coaster {C:.0f} x {C:.0f} on the epoxy blank: flip about the red dotted pin line; orange = tabs", fontsize=10)
    fig.savefig(os.path.join(ROOT, "art", "pintest.png"), bbox_inches="tight")
    plt.close(fig)


if __name__ == "__main__":
    args = sys.argv[1:] or ["check"]
    if "map" in args:
        make_map()
    if "check" in args:
        check()
    if "export" in args:
        export()
