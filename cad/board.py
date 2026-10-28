"""Backgammon board v0: a folding case, each half milled on the Carvera Air.

The machine cuts 300 x 200 mm (Z 130), so a one-piece board can't be made: the board is two halves, each one
solid tray (walnut, 18 mm) with the playing field pocketed 10 mm deep, the 12 points V-carve inlaid into the
field floor (maple and padauk plugs, 90 deg V-bit, sharp tips), 2 butt hinges recessed into the inner rims, 2 magnets in the outer rims. Closed,
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
VBIT_ANGLE, VBIT_D = 90.0, 6.0 # Makera 90 deg chamfering bit, 6 mm shank (cutting diameter: listing, check): the inlays
VBIT_K = tan(radians(VBIT_ANGLE / 2))   # the V's walls: sideways per mm of depth (1.0 at 90 deg)

# ---------------------------------------------------------------- halves
HALF_W, HALF_L, T = 186.0, 286.0, 18.0     # one half: across (X) x along (Y) x thick
CORNER_R = 8.0                 # outer corners only (the hinge side stays square: the halves meet there)
RIM_OUT, RIM_IN = 12.0, 9.0    # outer rims (front, back, outer side) / inner rim at the hinge (bar = 2 x RIM_IN)
POCKET = 10.0                  # field depth below the rim
POCKET_R = TOOL_D / 2          # the field pocket's inside corners (end mill radius)
# V-carve inlay (VCarve / F-Engrave terms): the points are V-carved into the field floor, the plugs are V-carved as
# raised islands in the plug wood, flipped and glued in; their 45 deg walls wedge into the pocket's (no side gap)
FACE = 0.5                     # the field is first cut this much shallow; the facing pass after glue-up takes it off
INLAY_P = 2.5                  # pocket depth below that first floor ("flat depth"; <= the V-bit's reach)
GLUE_GAP = 0.5                 # the plug's narrow end stops this far above the pocket floor (room for glue)
PLUG_START = 1.0               # the plug carries on this far above the first floor ("start depth"), then its skirt
SKIRT, SKIRT_T = 1.0, 2.0      # each plug is cut free with a 1 mm-wide, 2 mm-thick skirt round its base
PLUG_STOCK = 10.0              # plug wood thickness (maple, padauk)
PT_EDGE = 1.0                  # walnut between the field wall and a point's base (the V needs room at the wall)
SHEET_GAP = TOOL_D + 1.0       # between plugs on a plug sheet: the outline tool + 1 mm
N_PTS = 6
FIELD_W = HALF_W - RIM_OUT - RIM_IN
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
MAG_D, MAG_T, MAG_FIT = 8.0, 3.0, 0.1                                 # 8 x 3 neodymium discs, pressed + glued
MAG_Y = HALF_L / 2 - 30.0

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


D_FIN = INLAY_P - FACE         # pocket depth below the finished floor
D_PLUG = D_FIN - GLUE_GAP      # finished inlay thickness (the plug below the finished floor)


def triangle(x, front):
    """The V-carved pocket for a point, below the finished field floor (above it, the facing pass took the rest)."""
    return frustum(x, front, FIELD_Z + 0.01, 0.01 * VBIT_K, FIELD_Z - D_FIN, -D_FIN * VBIT_K)


def inlay_piece(x, front):
    """A plug in its pocket, as finished: faced flush, its walls on the pocket's, GLUE_GAP above the pocket floor."""
    return frustum(x, front, FIELD_Z, 0.0, FIELD_Z - D_PLUG, -D_PLUG * VBIT_K)


def plug_blank(x=0.0, front=True):
    """One plug as carved in its blank (z = 0 the blank's bottom, PLUG_STOCK its top), before it is flipped:
    the narrow end on top, walls widening down to the start depth, then the skirt it is cut free with."""
    h = INLAY_P - GLUE_GAP + PLUG_START                       # V-walled height
    g_top = FACE - (INLAY_P - GLUE_GAP) * VBIT_K              # outline relative to the finished point
    g_base = FACE + PLUG_START * VBIT_K
    island = frustum(x, front, PLUG_STOCK, g_top, PLUG_STOCK - h, g_base)
    skirt = Pos(0, 0, PLUG_STOCK - h - SKIRT_T) * extrude(point_face(x, front, g_base + SKIRT), SKIRT_T)
    return island + skirt


def tray_right():
    body = Pos(HALF_W / 2, 0, T / 2) * Box(HALF_W, HALF_L, T)
    body = fillet([e for e in body.edges().filter_by(Axis.Z) if e.center().X > HALF_W / 2], CORNER_R)
    field = Pos(RIM_IN + FIELD_W / 2, 0, FIELD_Z + POCKET / 2 + 0.5) * Box(FIELD_W, FIELD_L, POCKET + 1)
    field = fillet(field.edges().filter_by(Axis.Z), POCKET_R)
    body -= field
    for i in range(N_PTS):
        for front in (True, False):
            body -= triangle(point_x(i), front)
    for y in (-HINGE_Y, HINGE_Y):
        body -= Pos(HINGE_LEAF / 2 + FIT_HW / 2, y, T - HINGE_T / 2 + 0.5) * Box(HINGE_LEAF + FIT_HW, HINGE_L + FIT_HW, HINGE_T + 1)
        body -= Pos(0, y, T) * Rot(90, 0, 0) * Cylinder(HINGE_BARREL / 2 + FIT_HW, HINGE_L + FIT_HW)
    for y in (-MAG_Y, MAG_Y):
        body -= Pos(HALF_W - RIM_OUT / 2, y, T - MAG_T / 2 + 0.5) * Cylinder(MAG_D / 2 + MAG_FIT / 2, MAG_T + 1)
    return body


def inlays_right():
    """Point inlays, colour 0 / 1 alternating (across the board the colours swap)."""
    out = {}
    for i in range(N_PTS):
        out[f"inlay_f{i}"] = (inlay_piece(point_x(i), True), i % 2)
        out[f"inlay_b{i}"] = (inlay_piece(point_x(i), False), (i + 1) % 2)
    return out


def inlay_sheet():
    """One wood's 12 plugs nested on a PLUG_STOCK blank, alternately up and down, skirts SHEET_GAP apart.
    Returns (plugs, skirt outlines). All points are the same shape, so one layout serves both woods (cut it once
    per wood); a triangle is its own mirror image, so the flip onto the board changes nothing."""
    g = FACE + PLUG_START * VBIT_K + SKIRT
    outline = point_face(0, True, g)
    bb = outline.bounding_box()
    c = Pos(0, -(bb.min.Y + bb.max.Y) / 2, 0)                  # sharp triangle: its box centre turns it in line
    b = bb.size.X
    half = atan(b / 2 / bb.size.Y)                            # half the tip angle
    dx = b / 2 + SHEET_GAP / cos(half)                        # antiparallel neighbours: slanted sides SHEET_GAP apart
    place = [Pos(k * dx, 0, 0) * (Rot(0, 0, 180) if k % 2 else Rot()) * c for k in range(2 * N_PTS)]
    return [p * plug_blank() for p in place], [p * outline for p in place]


def hardware_right():
    out = {}
    for k, y in enumerate((-HINGE_Y, HINGE_Y)):
        out[f"leaf{k}"] = Pos(HINGE_BARREL / 2 + (HINGE_LEAF - HINGE_BARREL / 2) / 2, y, T - HINGE_T / 2) * Box(HINGE_LEAF - HINGE_BARREL / 2, HINGE_L, HINGE_T)
    for k, y in enumerate((-MAG_Y, MAG_Y)):
        out[f"mag{k}"] = Pos(HALF_W - RIM_OUT / 2, y, T - MAG_T / 2) * Cylinder(MAG_D / 2, MAG_T)
    return out


def barrels():
    return {f"barrel{k}": Pos(0, y, T) * Rot(90, 0, 0) * Cylinder(HINGE_BARREL / 2, HINGE_L) for k, y in enumerate((-HINGE_Y, HINGE_Y))}


MIRROR = lambda s: mirror(s, Plane.YZ)


def build():
    """The open board: {name: (shape, side, colour key)}; side R folds, L stays, X = the hinge knuckles."""
    P = {}
    tr = tray_right()
    P["tray_R"], P["tray_L"] = (tr, "R", "tray"), (MIRROR(tr), "L", "tray")
    for n, (s, c) in inlays_right().items():
        P[n + "_R"] = (s, "R", f"inlay{c}")
        P[n + "_L"] = (MIRROR(s), "L", f"inlay{1 - c}")      # colours alternate straight across the bar too
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
