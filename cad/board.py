"""Backgammon board v0: a folding case, each half milled on the Carvera Air.

The machine cuts 300 x 200 mm (Z 130), so a one-piece board can't be made: the board is two halves, each one
solid tray (walnut, 18 mm) with the playing field pocketed 10 mm deep, the 12 points V-carved into the
field floor and filled with epoxy (two colours, 90 deg V-bit, sharp tips), 2 butt hinges recessed into the inner rims, 2 magnets in the outer rims. Closed,
the two fields face each other: a 36 mm box that holds the checkers and dice.

Frame: open board lying flat, the white player at the front (-Y). X left-right, the hinge line at x = 0 (the bar),
Z up, table at 0. The right half folds over onto the left about the hinge axis (y, at x = 0, z = T).
Points (white's numbering): 1-6 front right (1 at the right edge), 7-12 front left, 13-18 back left, 19-24 back right.
Bought-part sizes (hinges, magnets) are placeholders until chosen: see docs "Missing info".
"""
from math import atan, cos, tan, radians
from build123d import *

# ---------------------------------------------------------------- machine (Carvera Air, 3-axis)
CARVERA_X, CARVERA_Y, CARVERA_Z = 300.0, 200.0, 130.0   # work area (retail spec sheets; confirm on the machine)
TOOL_D = 3.175                 # outline / pocket end mill (1/8")
VBIT_ANGLE, VBIT_D = 90.0, 6.0 # Makera 90 deg chamfering bit, 6 mm shank (cutting diameter: listing, check): the point pockets
VBIT_K = tan(radians(VBIT_ANGLE / 2))   # the V's walls: sideways per mm of depth (1.0 at 90 deg)
OFLUTE_D = 6.0                 # Spiral 'O' single-flute bit: faces the field (walnut + epoxy) after the pour

# ---------------------------------------------------------------- halves
HALF_W, HALF_L, T = 190.0, 286.0, 18.0     # one half: across (X) x along (Y) x thick
CORNER_R = 8.0                 # outer corners only (the hinge side stays square: the halves meet there)
RIM_OUT, RIM_IN = 12.0, 9.0    # front / back rims; inner rim at the hinge (bar = 2 x RIM_IN)
RIM_SIDE = 16.0                # outer side rim: the rim line, then the magnets and the diamond outboard of it
POCKET = 10.0                  # field depth below the rim
POCKET_R = TOOL_D / 2          # the field pocket's inside corners (end mill radius)
# Epoxy points: each point is V-carved into the field floor (sharp tips), sealed, filled with tinted epoxy a little
# proud, and the field is faced flush when it has cured
FACE = 0.5                     # the field is first cut this much shallow; the facing pass after the pour takes it off
FILL_P = 2.5                   # pocket depth below that first floor (<= the V-bit's reach)
PT_EDGE = 1.0                  # walnut between the field wall and a point's base (the V needs room at the wall)
# Amir's reference photo: turquoise + deep blue points, a thin turquoise line on the rim top round the field (not along
# the bar), a turquoise diamond in the middle of each outer side rim, chamfered outer edges
LINE_W, LINE_GAP = 1.6, 3.0    # rim line: width (V-groove), walnut between it and the field wall (Amir: keep it
                               # away from the wall so that strip can't break off)
LINE_D = LINE_W / 2 / VBIT_K - 0.05      # its depth (a hair of flat bottom left)
DIA_L, DIA_W, DIA_D = 12.0, 6.0, 1.5     # rim diamond: along the rim, across, V-carved depth
ENGRAVE_D = 0.4                # the back: sea-floor contour map engraved across both halves (art/topo.py)
EDGE_CH = 1.5                  # chamfer on the outer top edges (the hinge side stays square)
N_PTS = 6
FIELD_W = HALF_W - RIM_SIDE - RIM_IN
FIELD_L = HALF_L - 2 * RIM_OUT
PT_W = FIELD_W / N_PTS         # point pitch
PT_BASE = PT_W - 1.5           # triangle base (a 1.5 mm field strip between points)
PT_LEN = 112.0                 # point length, from its base (sharp tip: V-carved)

# ---------------------------------------------------------------- checkers, dice
STACK = 6                      # checkers in a row on one point (Amir: 6, with a small space left in the middle)
MID_SPACE = 10.0               # between two full rows meeting in the middle of the field
CHK_D = (FIELD_L - MID_SPACE) / 2 / STACK   # 21.0
CHK_T, CHK_CH = 6.0, 0.8
DIE = 12.0

# ---------------------------------------------------------------- hardware (placeholders)
HINGE_L, HINGE_LEAF, HINGE_T, HINGE_BARREL = 30.0, 12.0, 1.0, 4.0   # small brass butt hinge: length, leaf from axis, leaf t, knuckle
HINGE_Y = HALF_L / 2 - 50.0
FIT_HW = 0.3                   # around bought parts in pockets (hinge leaves, knuckle cove)
MAG_D, MAG_T, MAG_FIT = 6.0, 3.0, 0.1                                 # 6 x 3 neodymium discs (Amir has them), pressed + glued
MAG_Y = HALF_L / 2 - 30.0
SIDE_X = (RIM_IN + FIELD_W + LINE_GAP + LINE_W + HALF_W - EDGE_CH) / 2   # middle of the side rim outboard of the line
MAG_X = SIDE_X

FIELD_Z = T - POCKET           # field floor


def point_x(i):
    """Centre of point i (0 = next to the bar) in the right half."""
    return RIM_IN + PT_W * (i + 0.5)


def point_face(x=0.0, front=True, grow=0.0):
    """A point as seen on the finished board (sharp triangle, base PT_EDGE off the field wall), grown outward by grow
    (negative: shrunk), corners kept sharp."""
    y0 = -(HALF_L / 2 - RIM_OUT - PT_EDGE) if front else HALF_L / 2 - RIM_OUT - PT_EDGE
    s = 1 if front else -1
    corners = [(x - PT_BASE / 2, y0), (x + PT_BASE / 2, y0), (x, y0 + s * PT_LEN)]
    face = Polygon(*(corners if front else corners[::-1]), align=None)   # counter-clockwise: normal up
    return face if grow == 0 else offset(face, grow, kind=Kind.INTERSECTION).faces()[0]


def frustum(x, front, z0, g0, z1, g1):
    """The V-walled solid between the outline grown g0 at height z0 and grown g1 at z1 (walls at the V-bit angle)."""
    return loft([Pos(0, 0, z0) * point_face(x, front, g0), Pos(0, 0, z1) * point_face(x, front, g1)])


D_FIN = FILL_P - FACE          # pocket depth below the finished floor = the finished epoxy's thickness


def triangle(x, front):
    """The V-carved pocket for a point, below the finished field floor (above it, the facing pass took the rest)."""
    return frustum(x, front, FIELD_Z + 0.01, 0.01 * VBIT_K, FIELD_Z - D_FIN, -D_FIN * VBIT_K)


def fill(x, front):
    """A point's epoxy, as finished: the pocket below the finished floor, faced flush."""
    return frustum(x, front, FIELD_Z, 0.0, FIELD_Z - D_FIN, -D_FIN * VBIT_K)


def tray_right():
    body = Pos(HALF_W / 2, 0, T / 2) * Box(HALF_W, HALF_L, T)
    body = fillet([e for e in body.edges().filter_by(Axis.Z) if e.center().X > HALF_W / 2], CORNER_R)
    body = chamfer([e for e in body.edges() if e.center().Z > T - 0.01 and e.center().X > 0.01], EDGE_CH)
    field = Pos(RIM_IN + FIELD_W / 2, 0, FIELD_Z + POCKET / 2 + 0.5) * Box(FIELD_W, FIELD_L, POCKET + 1)
    field = fillet(field.edges().filter_by(Axis.Z), POCKET_R)
    body -= field
    for i in range(N_PTS):
        for front in (True, False):
            body -= triangle(point_x(i), front)
    body -= rim_line(0.01)
    body -= diamond(0.01)
    for y in (-HINGE_Y, HINGE_Y):
        body -= Pos(HINGE_LEAF / 2 + FIT_HW / 2, y, T - HINGE_T / 2 + 0.5) * Box(HINGE_LEAF + FIT_HW, HINGE_L + FIT_HW, HINGE_T + 1)
        body -= Pos(0, y, T) * Rot(90, 0, 0) * Cylinder(HINGE_BARREL / 2 + FIT_HW, HINGE_L + FIT_HW)
    for y in (-MAG_Y, MAG_Y):
        body -= Pos(MAG_X, y, T - MAG_T / 2 + 0.5) * Cylinder(MAG_D / 2 + MAG_FIT / 2, MAG_T + 1)
    return body


def rim_line(over=0.0):
    """The rim line's V-groove (= its epoxy, over = 0): a band LINE_GAP outside the field on the front, back and outer
    rims, cut off where the bar's rim starts."""
    g = Pos(RIM_IN - 5 + (FIELD_W + 5) / 2, 0) * Rectangle(FIELD_W + 5, FIELD_L)    # run on past the bar: straight ends
    band = offset(g, LINE_GAP + LINE_W + 2 * over, kind=Kind.ARC) - offset(g, LINE_GAP - 2 * over, kind=Kind.ARC)
    band = (band & Pos(RIM_IN - 2 * over + HALF_W / 2, 0) * Rectangle(HALF_W, HALF_L)).faces()[0]
    return Pos(0, 0, T + over) * extrude(band, LINE_D + 2 * over, dir=(0, 0, -1), taper=45 - 0.01)


def diamond(over=0.0):
    """The diamond on the outer side rim (= its epoxy, over = 0), V-carved to a ridge."""
    x = SIDE_X
    d = Polygon((x, -DIA_L / 2), (x + DIA_W / 2, 0), (x, DIA_L / 2), (x - DIA_W / 2, 0), align=None)
    d = offset(d, over, kind=Kind.INTERSECTION).faces()[0] if over else d
    low = offset(d, -(DIA_D - 0.05) * VBIT_K, kind=Kind.INTERSECTION).faces()[0]
    return loft([Pos(0, 0, T + over) * d, Pos(0, 0, T - DIA_D) * low])


def fills_right():
    """Point fills, colour 0 / 1 alternating (across the board the colours swap)."""
    out = {}
    for i in range(N_PTS):
        out[f"fill_f{i}"] = (fill(point_x(i), True), i % 2)
        out[f"fill_b{i}"] = (fill(point_x(i), False), (i + 1) % 2)
    return out


def oflute_leftovers():
    """Where the facing bit can't reach: in each field corner, outside its circle (the first cut left r = POCKET_R)."""
    r = OFLUTE_D / 2
    out = []
    for cx, sx in ((RIM_IN, 1), (RIM_IN + FIELD_W, -1)):
        for cy, sy in ((-FIELD_L / 2, 1), (FIELD_L / 2, -1)):
            sq = Pos(cx + sx * r / 2, cy + sy * r / 2) * Rectangle(r, r)
            out.append((sq - Pos(cx + sx * r, cy + sy * r) * Circle(r)).faces()[0])
    return out


def hardware_right():
    out = {}
    for k, y in enumerate((-HINGE_Y, HINGE_Y)):
        out[f"leaf{k}"] = Pos(HINGE_BARREL / 2 + (HINGE_LEAF - HINGE_BARREL / 2) / 2, y, T - HINGE_T / 2) * Box(HINGE_LEAF - HINGE_BARREL / 2, HINGE_L, HINGE_T)
    for k, y in enumerate((-MAG_Y, MAG_Y)):
        out[f"mag{k}"] = Pos(MAG_X, y, T - MAG_T / 2) * Cylinder(MAG_D / 2, MAG_T)
    return out


def barrels():
    return {f"barrel{k}": Pos(0, y, T) * Rot(90, 0, 0) * Cylinder(HINGE_BARREL / 2, HINGE_L) for k, y in enumerate((-HINGE_Y, HINGE_Y))}


MIRROR = lambda s: mirror(s, Plane.YZ)


def build():
    """The open board: {name: (shape, side, colour key)}; side R folds, L stays, X = the hinge knuckles."""
    P = {}
    tr = tray_right()
    P["tray_R"], P["tray_L"] = (tr, "R", "tray"), (MIRROR(tr), "L", "tray")
    for n, (s, c) in fills_right().items():
        P[n + "_R"] = (s, "R", f"fill{c}")
        P[n + "_L"] = (MIRROR(s), "L", f"fill{1 - c}")      # colours alternate straight across the bar too
    for n, s in (("line", rim_line()), ("diamond", diamond())):
        P[n + "_R"], P[n + "_L"] = (s, "R", "fill0"), (MIRROR(s), "L", "fill0")
    for n, s in hardware_right().items():
        P[n + "_R"], P[n + "_L"] = (s, "R", n[:-1]), (MIRROR(s), "L", n[:-1])
    for n, s in barrels().items():
        P[n] = (s, "X", "barrel")
    return P


# ---------------------------------------------------------------- checkers in the starting position
START = {"white": {24: 2, 13: 5, 8: 3, 6: 5}, "black": {1: 2, 12: 5, 17: 3, 19: 5}}


def point_place(n):
    """(x, edge y, direction into the field) of point n, white's numbering."""
    if n <= 6:
        x = point_x(6 - n); front = True
    elif n <= 12:
        x = -point_x(n - 7); front = True
    elif n <= 18:
        x = -point_x(18 - n); front = False
    else:
        x = point_x(n - 19); front = False
    y0 = -(HALF_L / 2 - RIM_OUT) if front else HALF_L / 2 - RIM_OUT
    return x, y0, 1 if front else -1


def checker():
    c = Cylinder(CHK_D / 2, CHK_T)
    return chamfer(c.edges().filter_by(GeomType.CIRCLE), CHK_CH)


def checkers():
    out, c = {}, checker()
    for colour, pts in START.items():
        k = 0
        for n, count in pts.items():
            x, y0, s = point_place(n)
            for j in range(count):
                out[f"chk_{colour}{k:02d}"] = (Pos(x, y0 + s * (CHK_D / 2 + (j % STACK) * CHK_D), FIELD_Z + CHK_T / 2 + (j // STACK) * CHK_T) * c,
                                               "R" if x > 0 else "L", colour)
                k += 1
    die = fillet(Box(DIE, DIE, DIE).edges(), 1.2)
    for k, dx in enumerate((-9, 9)):
        out[f"die{k}"] = (Pos(HALF_W / 2 + 4 + dx, 0, FIELD_Z + DIE / 2) * Rot(0, 0, 12 * (k * 2 - 1)) * die, "R", "die")
    return out


def fold(shape, angle):
    """The right half folded by angle (0 = open, 180 = closed on the left half)."""
    return Pos(0, 0, T) * Rot(0, -angle, 0) * Pos(0, 0, -T) * shape
