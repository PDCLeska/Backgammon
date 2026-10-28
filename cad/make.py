"""Backgammon board: checks and cut files (export/).
Run from the repo root:  C:/Users/leska/cadenv/Scripts/python cad/make.py [check] [export]
check  = parts valid; each half fits the Carvera Air; checkers fit the points; nothing collides open, folding
         (90, 135 deg) or closed; the dice fit in the closed box
export = STEP per part for Makera CAM (2 trays, the 2 inlay colours, a checker), STL of the same
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
    (Inlays are not skipped: each piece must sit in its pocket with the glue gap all round.)"""
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
    print(f"  wood under the inlays {floor:.1f} mm, under the magnets {bd.T - bd.MAG_T:.1f} mm")

    print("V-carve inlays (%d maple + %d padauk plugs, %.0f deg V-bit, sharp tips)" % (2 * bd.N_PTS, 2 * bd.N_PTS, bd.VBIT_ANGLE))
    reach = bd.VBIT_D / 2 / bd.VBIT_K
    h = bd.INLAY_P - bd.GLUE_GAP + bd.PLUG_START               # plug wall height
    vok = bd.INLAY_P <= reach and h <= reach
    ok &= vok
    print(f"  V-bit ({bd.VBIT_D:.0f} mm wide) reaches {reach:.1f} deep: pocket {bd.INLAY_P:.1f}, plug walls {h:.1f}  {'ok' if vok else 'TOO DEEP FOR THE BIT'}")
    try:
        flat = bd.point_face(0, True, bd.FACE - bd.INLAY_P * bd.VBIT_K).bounding_box().size
        print(f"  pocket floor (flat, cleared by the V-bit): {flat.X:.1f} wide at the base, {flat.Y:.0f} long")
    except Exception:
        ok = False; print("  POCKET HAS NO FLAT FLOOR (too deep for the point's width)")
    lo, hi = bd.FIELD_Z - bd.D_PLUG, bd.FIELD_Z
    wrong = [n for n, (s, _, c) in P.items() if c.startswith("inlay") and
             (abs(s.bounding_box().min.Z - lo) > 0.01 or abs(s.bounding_box().max.Z - hi) > 0.01)]
    ok &= not wrong
    n_in = sum(1 for _, _, c in P.values() if c.startswith("inlay"))
    print(f"  {n_in} plugs, all flush in the field floor, {bd.D_PLUG:.1f} thick when finished (z {lo:.1f} .. {hi:.1f})" if not wrong else f"  NOT IN THE FLOOR: {wrong}")
    print(f"  field first cut {bd.FACE:.1f} shallow; pockets {bd.INLAY_P:.1f} below that; a plug's walls wedge on the pocket's, "
          f"its end {bd.GLUE_GAP:.1f} above the pocket floor (glue); the facing pass takes the skirt, the {bd.PLUG_START:.1f} start and {bd.FACE:.1f} of floor")
    need_t = h + bd.SKIRT_T
    ok &= need_t <= bd.PLUG_STOCK
    print(f"  a plug + skirt is {need_t:.1f} tall: {bd.PLUG_STOCK:.0f} mm plug wood  {'ok' if need_t <= bd.PLUG_STOCK else 'TOO THIN'}")
    plugs, outlines = bd.inlay_sheet()
    clash = [k for k in range(len(outlines) - 1) if outlines[k].distance_to(outlines[k + 1]) < bd.SHEET_GAP - 0.01]
    sb = Compound(outlines).bounding_box().size
    need = sorted([sb.X + bd.TOOL_D, sb.Y + bd.TOOL_D]); room = sorted([bd.CARVERA_X, bd.CARVERA_Y])
    sfit = need[0] <= room[0] and need[1] <= room[1] and not clash
    ok &= sfit
    print(f"  plug sheet per wood: 12 plugs in {sb.X:.0f} x {sb.Y:.0f} (blank {sb.X + 2 * bd.SHEET_GAP:.0f} x {sb.Y + 2 * bd.SHEET_GAP:.0f} x {bd.PLUG_STOCK:.0f}), "
          f"skirts {bd.SHEET_GAP:.1f} apart  {'ok' if sfit else 'PROBLEM: ' + ('plugs too close ' + str(clash) if clash else 'too big for the bed')}")

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
    for f in ("bg_inlay_sheet.step", "bg_inlay_sheet.stl", "bg_inlay_sheet.dxf"):
        if os.path.exists(os.path.join(out, f)):
            os.remove(os.path.join(out, f))      # flat-bit inlay: replaced by the V-carve plug sheet
    plugs, outlines = bd.inlay_sheet()
    groups = {"half_right": [P["tray_R"][0]], "half_left": [P["tray_L"][0]], "checker": [bd.checker()],
              "plug_sheet": plugs}
    for name, shapes in groups.items():
        c = Compound(shapes)
        export_step(c, os.path.join(out, f"bg_{name}.step"))
        export_stl(c, os.path.join(out, f"bg_{name}.stl"), tolerance=0.02)
        print("  export/bg_%s.step / .stl" % name)
    # the points for the inlay software (VCarve / F-Engrave make the V toolpaths and the plugs from these):
    # outlines at the first field floor (FACE above the finished one), one layer per wood, in the half's own frame
    for side, sign in (("right", 1), ("left", -1)):
        dxf = ExportDXF()
        dxf.add_layer("field"); dxf.add_layer("maple"); dxf.add_layer("padauk")
        dxf.add_shape(Rectangle(bd.FIELD_W, bd.FIELD_L).located(Location((sign * (bd.RIM_IN + bd.FIELD_W / 2), 0))).wire(), layer="field")
        for n, (s, sd, c) in P.items():
            if c.startswith("inlay") and sd == side[0].upper():
                i, front = int(n.split("_")[1][1:]), n.split("_")[1][0] == "f"
                f = bd.point_face(bd.point_x(i), front, bd.FACE)
                f = mirror(f, Plane.YZ) if sign < 0 else f
                dxf.add_shape(f.faces()[0].outer_wire(), layer="maple" if c == "inlay0" else "padauk")
        dxf.write(os.path.join(out, f"bg_points_{side}.dxf"))
        print(f"  export/bg_points_{side}.dxf (field + 6 maple + 6 padauk point outlines, at the first floor)")


if __name__ == "__main__":
    args = sys.argv[1:] or ["check"]
    if "check" in args:
        check()
    if "export" in args:
        export()
