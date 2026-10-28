"""Coffee coaster: the practice piece before the walnut board (Amir), made with every technique of the board.

A small square tray: a field pocketed 3 deep, 6 points (3 a side, the board's width and V-bit, sharp tips) poured in
two epoxy colours, a turquoise diamond in the middle, the turquoise rim line round the field, chamfered edges; the
back a square of the sea-floor map round Aegina (art/coaster_map.py): the land cut in as flat recesses, the depth
lines lasered. Made like a board half: back first, one flip, blue pour, turquoise pour, facing, outline last.

Frame: x across, y front-back, z up, the table at 0, the coaster's centre at x = y = 0. The back is drawn in back view
(the coaster turned over about y: u = -x), as for the board.
"""
import json, os
from build123d import *
from board import (CARVERA_X, CARVERA_Y, TOOL_D, VBIT_ANGLE, VBIT_D, VBIT_K, OFLUTE_D, FACE, FILL_P, PT_EDGE,
                   LINE_W, LINE_GAP, LINE_D, DIA_L, DIA_W, DIA_D, EDGE_CH, PT_W, PT_BASE)

ART = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "art")

N_PTS = 3                      # points a side (the board's pitch and width: the same V-carve as the real thing)
FIELD = N_PTS * PT_W           # 82.5 square: a mug's base sits inside
RIM = 14.0                     # rim all round: the rim line, then walnut out to the chamfer
W = FIELD + 2 * RIM            # 110.5 square
CORNER_R = 8.0
T = 12.0                       # finished (blank 12.5: the top is faced 0.5 after the pours)
POCKET = 3.0                   # field depth: holds a drip, and teaches the field pocket + facing of the board
POCKET_R = TOOL_D / 2
FIELD_Z = T - POCKET
MID = 16.0                     # between the two rows of tips: the diamond
PT_LEN = (FIELD - 2 * PT_EDGE - MID) / 2
ISLAND_D = 0.8                 # the back: land recessed this deep (V-bit coast, flat floor)
D_FIN = FILL_P - FACE


def point_x(i):
    return -FIELD / 2 + PT_W * (i + 0.5)


def point_face(x=0.0, front=True, grow=0.0):
    y0 = -(FIELD / 2 - PT_EDGE) if front else FIELD / 2 - PT_EDGE
    s = 1 if front else -1
    corners = [(x - PT_BASE / 2, y0), (x + PT_BASE / 2, y0), (x, y0 + s * PT_LEN)]
    face = Polygon(*(corners if front else corners[::-1]), align=None)
    return face if grow == 0 else offset(face, grow, kind=Kind.INTERSECTION).faces()[0]


def frustum(face_at, z0, g0, z1, g1):
    return loft([Pos(0, 0, z0) * face_at(g0), Pos(0, 0, z1) * face_at(g1)])


def pocket(x, front):
    return frustum(lambda g: point_face(x, front, g), FIELD_Z + 0.01, 0.01 * VBIT_K, FIELD_Z - D_FIN, -D_FIN * VBIT_K)


def fill(x, front):
    return frustum(lambda g: point_face(x, front, g), FIELD_Z, 0.0, FIELD_Z - D_FIN, -D_FIN * VBIT_K)


def diamond_face(grow=0.0):
    d = Polygon((-DIA_L / 2, 0), (0, -DIA_W / 2), (DIA_L / 2, 0), (0, DIA_W / 2), align=None)
    return d if grow == 0 else offset(d, grow, kind=Kind.INTERSECTION).faces()[0]


def diamond(over=0.0):
    """In the middle of the field, V-carved to a ridge (= its epoxy, over = 0)."""
    return frustum(diamond_face, FIELD_Z + over, over, FIELD_Z - DIA_D, -(DIA_D - 0.05) * VBIT_K)


def rim_line(over=0.0):
    """The turquoise line all round the field on the rim top, LINE_GAP off the field wall (= its epoxy, over = 0)."""
    g = Rectangle(FIELD, FIELD)
    band = offset(g, LINE_GAP + LINE_W + 2 * over, kind=Kind.ARC) - offset(g, LINE_GAP - 2 * over, kind=Kind.ARC)
    return Pos(0, 0, T + over) * extrude(band.faces()[0], LINE_D + 2 * over, dir=(0, 0, -1), taper=45 - 0.01)


def back_map():
    with open(os.path.join(ART, "coaster_map.json")) as f:
        return json.load(f)


def islands():
    """The land recesses in the back (model frame: x = -u), straight-walled here (the V-bit coast is the CAM's)."""
    out = []
    for p in back_map()["land"]:
        try:
            f = Face(Wire.make_polygon([(-u, v, 0) for u, v in p], close=True))
            out.append(extrude(f, ISLAND_D, dir=(0, 0, 1)))
        except Exception:
            pass
    return out


def body():
    b = Box(W, W, T, align=(Align.CENTER, Align.CENTER, Align.MIN))
    b = fillet(b.edges().filter_by(Axis.Z), CORNER_R)
    b = chamfer([e for e in b.edges() if e.center().Z > T - 0.01], EDGE_CH)
    field = Pos(0, 0, FIELD_Z + POCKET / 2 + 0.5) * Box(FIELD, FIELD, POCKET + 1)
    b -= fillet(field.edges().filter_by(Axis.Z), POCKET_R)
    for i in range(N_PTS):
        for front in (True, False):
            b -= pocket(point_x(i), front)
    b -= diamond(0.01)
    b -= rim_line(0.01)
    for isl in islands():
        b -= isl
    return b


def build():
    """{name: (shape, side, colour key)}: the same colour keys as the board."""
    P = {"tray_C": (body(), "C", "tray")}
    for i in range(N_PTS):
        P[f"fill_f{i}"] = (fill(point_x(i), True), "C", f"fill{i % 2}")
        P[f"fill_b{i}"] = (fill(point_x(i), False), "C", f"fill{(i + 1) % 2}")
    P["diamond"] = (diamond(), "C", "fill0")
    P["line"] = (rim_line(), "C", "fill0")
    return P


def leftovers():
    """Field corners the 6 mm facing bit can't reach (outside its circle)."""
    r, out = OFLUTE_D / 2, []
    for sx in (-1, 1):
        for sy in (-1, 1):
            cx, cy = sx * FIELD / 2, sy * FIELD / 2
            sq = Pos(cx - sx * r / 2, cy - sy * r / 2) * Rectangle(r, r)
            out.append((sq - Pos(cx - sx * r, cy - sy * r) * Circle(r)).faces()[0])
    return out


def check(P=None):
    P = P or build()
    ok = all(s.is_valid for s, *_ in P.values())
    print("Parts\n  " + ("all valid" if ok else "INVALID: " + ", ".join(n for n, (s, *_) in P.items() if not s.is_valid)))
    print(f"Coaster {W:.1f} x {W:.1f} x {T:.0f} (blank {T + FACE:.1f} thick), field {FIELD:.1f} square, {POCKET:.0f} deep")
    m = min(CARVERA_X, CARVERA_Y) - (W + TOOL_D)
    print(f"  on the Carvera: {m:.0f} mm to spare  {'ok' if m >= 0 else 'TOO BIG'}"); ok &= m >= 0
    print("Points + epoxy (the board's settings)")
    reach = VBIT_D / 2 / VBIT_K
    vok = FILL_P <= reach and DIA_D <= reach
    ok &= vok
    print(f"  V-bit reaches {reach:.1f}: points {FILL_P}, diamond {DIA_D}, rim line {LINE_D:.2f}  {'ok' if vok else 'TOO DEEP'}")
    print(f"  6 points {PT_BASE:.0f} wide x {PT_LEN:.1f} long (the board's width), colours alternating, opposite across")
    tips = FIELD / 2 - PT_EDGE - PT_LEN
    gap = tips - DIA_W / 2 - 2 * FACE
    print(f"  diamond to the point tips {gap:.1f} at the first floor  {'ok' if gap >= 1.5 else 'TOO CLOSE'}"); ok &= gap >= 1.5
    walls = dict(field_wall=LINE_GAP, outside=RIM - LINE_GAP - LINE_W - EDGE_CH)
    wok = min(walls.values()) >= 1.5; ok &= wok
    print("  walnut round the rim line: " + ", ".join(f"{k.replace('_', ' ')} {v:.1f}" for k, v in walls.items()) + f"  {'ok' if wok else 'TOO THIN'}")
    left = leftovers()
    near = [i for i in range(N_PTS) for f in (True, False)
            if any(getattr(point_face(point_x(i), f, FACE) & l, "area", 0) > 0.001 for l in left)]
    print(f"  facing with the {OFLUTE_D:.0f} mm O-flute: {len(near)} points reach into the corners it can't -> 1/8\" corner clean-up"
          if near else "  facing: no point in the corners the O-flute can't reach")
    floor = FIELD_Z - D_FIN - ISLAND_D
    ok &= floor >= 5
    print(f"  wood under the points {floor:.1f} mm (where an island is cut in under one)  {'ok' if floor >= 5 else 'TOO THIN'}")
    bm = back_map()["info"]
    isl = islands()
    print(f"Back: map round Aegina, {bm['size']:.0f} mm square: {len(isl)} of {bm['n_land']} land recesses built ({ISLAND_D} deep), "
          f"{bm['n_sea']} laser lines (every {bm['step']} m)")
    ok &= len(isl) == bm["n_land"]
    print("ALL OK" if ok else "PROBLEMS")
    return ok


def export():
    root = os.path.dirname(ART)
    out = os.path.join(root, "export")
    os.makedirs(out, exist_ok=True)
    P = build()
    c = P["tray_C"][0]
    export_step(c, os.path.join(out, "coaster.step")); export_stl(c, os.path.join(out, "coaster.stl"), tolerance=0.02)
    import ezdxf
    o = W / 2
    # top: the V-carves, a layer per pour, at the first field floor (FACE above the finished one); origin front-left
    doc = ezdxf.new(); msp = doc.modelspace()
    for l in ("outline", "field", "blue", "turquoise"):
        doc.layers.add(l)
    msp.add_lwpolyline([(0, 0), (W, 0), (W, W), (0, W)], close=True, dxfattribs={"layer": "outline"})
    msp.add_lwpolyline([(o - FIELD / 2, o - FIELD / 2), (o + FIELD / 2, o - FIELD / 2), (o + FIELD / 2, o + FIELD / 2),
                        (o - FIELD / 2, o + FIELD / 2)], close=True, dxfattribs={"layer": "field"})
    wire = lambda f: [(v.X + o, v.Y + o) for v in f.outer_wire().vertices()]
    for n, (s, _, col) in P.items():
        if n.startswith("fill"):
            i, front = int(n[6]), n[5] == "f"
            msp.add_lwpolyline(wire(point_face(point_x(i), front, FACE)), close=True,
                               dxfattribs={"layer": "turquoise" if col == "fill0" else "blue"})
    msp.add_lwpolyline(wire(diamond_face(FACE)), close=True, dxfattribs={"layer": "turquoise"})
    top = rim_line().faces().sort_by(Axis.Z)[-1]
    for w in [top.outer_wire(), *top.inner_wires()]:
        msp.add_lwpolyline([(p.X + o, p.Y + o) for p in w.positions(
            [k / 400 for k in range(401)])], dxfattribs={"layer": "turquoise"})
    doc.saveas(os.path.join(out, "coaster_top.dxf"))
    # back, as it lies back up (back view): origin front-left
    doc = ezdxf.new(); msp = doc.modelspace()
    for l in ("outline", "islands", "laser"):
        doc.layers.add(l)
    msp.add_lwpolyline([(0, 0), (W, 0), (W, W), (0, W)], close=True, dxfattribs={"layer": "outline"})
    bm = back_map()
    for p in bm["land"]:
        msp.add_lwpolyline([(u + o, v + o) for u, v in p], close=True, dxfattribs={"layer": "islands"})
    for l in bm["sea"]:
        msp.add_lwpolyline([(u + o, v + o) for u, v in l["pts"]], dxfattribs={"layer": "laser"})
    doc.saveas(os.path.join(out, "coaster_back.dxf"))
    print("  export/coaster.step / .stl, coaster_top.dxf (blue / turquoise layers), coaster_back.dxf (islands / laser layers)")


if __name__ == "__main__":
    import sys
    args = sys.argv[1:] or ["check"]
    if "check" in args:
        check()
    if "export" in args:
        export()
