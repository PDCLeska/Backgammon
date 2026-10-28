"""Backgammon board: checks and cut files (export/).
Run from the repo root:  C:/Users/leska/cadenv/Scripts/python cad/make.py [check] [export]
check  = parts valid; each half fits the Carvera Air; checkers fit the points; nothing collides open, folding
         (90, 135 deg) or closed; the dice fit in the closed box
export = STEP / STL per part for Makera CAM (2 halves, a checker); DXF of the epoxy outlines per half
"""
import os, sys, itertools
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path[:0] = [HERE, ROOT]
from build123d import *
import board as bd

FOLDS = [90, 135, 180]


def hit(a, b):
    A, B = a.bounding_box(), b.bounding_box()
    if not all(tuple(A.min)[i] < tuple(B.max)[i] and tuple(B.min)[i] < tuple(A.max)[i] for i in range(3)):
        return 0.0
    v = (a & b).volume
    return v if v > 0.005 else 0.0


def _skip(a, b):
    """Pairs that touch by design: leaves / magnets in their own tray, the knuckles in their coves.
    (The epoxy is not skipped: each fill must sit in its own pocket and touch nothing else.)"""
    for x, y in ((a, b), (b, a)):
        if x.startswith(("leaf", "mag")) and y.startswith("tray") and x[-1] == y[-1]:
            return True
        if x.startswith("barrel") and y.startswith("leaf") and x[-1] == y[-3]:
            return True                            # the knuckle wraps its leaves
    return False


def check(P=None, C=None):
    P = P or bd.build()
    C = C or bd.checkers()
    ok = True
    print("Parts")
    for n, (s, *_) in {**P, **C}.items():
        if not s.is_valid:
            print(f"  {n} INVALID"); ok = False
    print("  all valid" if ok else "  invalid parts above")

    print("Carvera Air (work area %.0f x %.0f x %.0f, %.3f mm tool around the outline)" % (bd.CARVERA_X, bd.CARVERA_Y, bd.CARVERA_Z, bd.TOOL_D))
    bb = P["tray_R"][0].bounding_box().size
    need = sorted([bb.X + bd.TOOL_D, bb.Y + bd.TOOL_D])
    room = sorted([bd.CARVERA_X, bd.CARVERA_Y])
    m = [room[i] - need[i] for i in range(2)]
    fits = min(m) >= 0
    ok &= fits
    print(f"  half {bb.X:.0f} x {bb.Y:.0f} x {bb.Z:.0f}: tool path {need[1]:.1f} x {need[0]:.1f}, "
          f"margin {m[1]:.1f} / {m[0]:.1f} mm  {'ok' if fits else 'TOO BIG'}")

    print("Play")
    gap = bd.PT_W - bd.CHK_D
    ok &= gap >= 1.0
    print(f"  point pitch {bd.PT_W:.1f}, checker {bd.CHK_D:.0f}: {gap:.1f} mm between checkers on neighbouring points  {'ok' if gap >= 1 else 'TOO TIGHT'}")
    stack = bd.STACK * bd.CHK_D
    mid = bd.FIELD_L - 2 * stack
    ok &= mid >= 5
    print(f"  {bd.STACK} checkers on a point reach {stack:.0f} of the {bd.FIELD_L / 2:.1f} mm to the middle: "
          f"{mid:.0f} mm between two full rows  {'ok' if mid >= 5 else 'NO SPACE'}")
    floor = bd.FIELD_Z - bd.D_FIN
    ok &= floor >= 5
    print(f"  wood under the points {floor:.1f} mm, under the magnets {bd.T - bd.MAG_T:.1f} mm")

    print("Epoxy points (12 turquoise + 12 deep blue, V-carved with the %.0f deg bit, sharp tips)" % bd.VBIT_ANGLE)
    reach = bd.VBIT_D / 2 / bd.VBIT_K
    vok = bd.FILL_P <= reach
    ok &= vok
    print(f"  V-bit ({bd.VBIT_D:.0f} mm wide) reaches {reach:.1f} deep: point pockets {bd.FILL_P:.1f}, rim line {bd.LINE_D:.2f}, diamonds {bd.DIA_D:.1f}  {'ok' if vok else 'TOO DEEP FOR THE BIT'}")
    try:
        flat = bd.point_face(0, True, bd.FACE - bd.FILL_P * bd.VBIT_K).bounding_box().size
        print(f"  pocket floor (flat, cleared by the V-bit): {flat.X:.1f} wide at the base, {flat.Y:.0f} long")
    except Exception:
        ok = False; print("  POCKET HAS NO FLAT FLOOR (too deep for the point's width)")
    lx = bd.RIM_IN + bd.FIELD_W + bd.LINE_GAP + bd.LINE_W                 # the line's outer edge on the side rim
    walls = dict(field_wall=bd.LINE_GAP, magnet=bd.MAG_X - bd.MAG_D / 2 - bd.MAG_FIT / 2 - lx,
                 diamond=bd.SIDE_X - bd.DIA_W / 2 - lx, chamfer=bd.HALF_W - bd.EDGE_CH - (bd.MAG_X + bd.MAG_D / 2),
                 front_rim_outside=bd.RIM_OUT - bd.LINE_GAP - bd.LINE_W)
    wok = min(walls.values()) >= 1.5
    ok &= wok
    print("  walnut round the rim line / magnets: " + ", ".join(f"{k.replace('_', ' ')} {v:.1f}" for k, v in walls.items())
          + f"  {'ok' if wok else 'TOO THIN (< 1.5: may break)'}")
    lo, hi = bd.FIELD_Z - bd.D_FIN, bd.FIELD_Z
    pts = {n: v for n, v in P.items() if n.startswith("fill")}
    wrong = [n for n, (s, *_) in pts.items() if abs(s.bounding_box().min.Z - lo) > 0.01 or abs(s.bounding_box().max.Z - hi) > 0.01]
    ok &= not wrong
    print(f"  {len(pts)} point fills, flush with the field floor, {bd.D_FIN:.1f} thick (z {lo:.1f} .. {hi:.1f})" if not wrong else f"  NOT IN THE FLOOR: {wrong}")
    gap = bd.PT_W - bd.PT_BASE - 2 * bd.FACE
    print(f"  walnut between two point pockets at the first floor: {gap:.1f} mm (finished {bd.PT_W - bd.PT_BASE:.1f})"
          f"{'  -> pour the two colours one after the other (docs 2.2)' if gap < 2 else ''}")
    left = bd.oflute_leftovers()
    near = [n for n, (s, sd, _) in pts.items() if sd == "R" and any(
        getattr(bd.point_face(bd.point_x(int(n[6:7])), n[5] == "f", bd.FACE) & l, "area", 0) > 0.001 for l in left)]
    print(f"  facing with the {bd.OFLUTE_D:.0f} mm O-flute leaves the field corners (r{bd.OFLUTE_D / 2:.0f}); "
          f"{len(near)} points per half reach into them: " + (f"{', '.join(n[:-2] for n in near)} -> 1/8\" corner clean-up pass after facing" if near else "none"))
    hits = []
    for (a, (sa, *_)), (b, (sb, *_)) in itertools.combinations({**P, **C}.items(), 2):
        if not _skip(a, b) and (v := hit(sa, sb)):
            hits.append(("open", a, b, round(v, 2)))
    for ang in FOLDS:
        M = {n: (bd.fold(s, ang) if side == "R" else s) for n, (s, side, _) in P.items()}
        for (a, sa), (b, sb) in itertools.combinations(M.items(), 2):
            if not _skip(a, b) and (v := hit(sa, sb)):
                hits.append((f"folded {ang}", a, b, round(v, 2)))
    inside = 2 * bd.POCKET
    ok &= inside >= bd.DIE + 1
    print(f"  closed: {inside:.0f} mm inside for {bd.CHK_T:.0f} mm checkers and {bd.DIE:.0f} mm dice  {'ok' if inside >= bd.DIE + 1 else 'TOO LOW'}")
    print("Collisions (open with checkers; folding 90 / 135; closed)")
    for h in hits:
        print("  HIT %s: %s x %s (%.2f mm3)" % h)
    if not hits:
        print("  none")
    ok &= not hits
    print("ALL OK" if ok else "PROBLEMS")
    return ok


def export():
    out = os.path.join(ROOT, "export")
    os.makedirs(out, exist_ok=True)
    P = bd.build()
    for f in ("bg_inlay_sheet.step", "bg_inlay_sheet.stl", "bg_inlay_sheet.dxf", "bg_plug_sheet.step", "bg_plug_sheet.stl"):
        if os.path.exists(os.path.join(out, f)):
            os.remove(os.path.join(out, f))      # wood plugs: replaced by the epoxy fill
    groups = {"half_right": [P["tray_R"][0]], "half_left": [P["tray_L"][0]], "checker": [bd.checker()]}
    for name, shapes in groups.items():
        c = Compound(shapes)
        export_step(c, os.path.join(out, f"bg_{name}.step"))
        export_stl(c, os.path.join(out, f"bg_{name}.stl"), tolerance=0.02)
        print("  export/bg_%s.step / .stl" % name)
    # the points for the V-carve toolpaths (Makera CAM / VCarve / F-Engrave), one layer per colour (= per pour):
    # outlines at the first field floor (FACE above the finished one), one layer per wood, in the half's own frame
    for side, sign in (("right", 1), ("left", -1)):
        dxf = ExportDXF()
        dxf.add_layer("field"); dxf.add_layer("turquoise"); dxf.add_layer("blue")
        dxf.add_shape(Rectangle(bd.FIELD_W, bd.FIELD_L).located(Location((sign * (bd.RIM_IN + bd.FIELD_W / 2), 0))).wire(), layer="field")
        for n, (s, sd, c) in P.items():
            if n.startswith("fill") and sd == side[0].upper():
                i, front = int(n.split("_")[1][1:]), n.split("_")[1][0] == "f"
                f = bd.point_face(bd.point_x(i), front, bd.FACE)
                f = mirror(f, Plane.YZ) if sign < 0 else f
                dxf.add_shape(f.faces()[0].outer_wire(), layer="turquoise" if c == "fill0" else "blue")
        for n in ("line", "diamond"):                # on the rim top (the outline at the top: the V-groove's width)
            f = Pos(0, 0, -bd.T) * (bd.rim_line() if n == "line" else bd.diamond()).faces().sort_by(Axis.Z)[-1]
            f = mirror(f, Plane.YZ).faces()[0] if sign < 0 else f
            for w in [f.outer_wire(), *f.inner_wires()]:
                dxf.add_shape(w, layer="turquoise")
        dxf.write(os.path.join(out, f"bg_points_{side}.dxf"))
        print(f"  export/bg_points_{side}.dxf (field + 6 turquoise + 6 blue points at the first floor; rim line + diamond)")


if __name__ == "__main__":
    args = sys.argv[1:] or ["check"]
    if "check" in args:
        check()
    if "export" in args:
        export()
