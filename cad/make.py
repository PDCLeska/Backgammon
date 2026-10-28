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
    """Pairs that touch by design: inlays / leaves / magnets in their own tray, the knuckles in their coves."""
    for x, y in ((a, b), (b, a)):
        if x.startswith(("inlay", "leaf", "mag")) and y.startswith("tray") and x[-1] == y[-1]:
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
    stack = 5 * bd.CHK_D
    print(f"  5 checkers on a point reach {stack:.0f} of the {bd.FIELD_L / 2:.0f} mm to the middle  {'ok' if stack <= bd.FIELD_L / 2 else 'OVERLAP'}")
    floor = bd.FIELD_Z - bd.INLAY_D
    ok &= floor >= 5
    print(f"  wood under the inlays {floor:.1f} mm, under the magnets {bd.T - bd.MAG_T:.1f} mm")

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
    groups = {"half_right": [P["tray_R"][0]], "half_left": [P["tray_L"][0]],
              "inlays_light": [s for n, (s, _, c) in P.items() if c == "inlay0"],
              "inlays_dark": [s for n, (s, _, c) in P.items() if c == "inlay1"], "checker": [bd.checker()]}
    for name, shapes in groups.items():
        c = Compound(shapes)
        export_step(c, os.path.join(out, f"bg_{name}.step"))
        export_stl(c, os.path.join(out, f"bg_{name}.stl"), tolerance=0.02)
        print("  export/bg_%s.step / .stl" % name)


if __name__ == "__main__":
    args = sys.argv[1:] or ["check"]
    if "check" in args:
        check()
    if "export" in args:
        export()
