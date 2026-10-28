"""Build the viewer data for the backgammon board (cad/board.py) -> review/data/.

Every part is exported once in the open pose; the page folds the right half (side R) about the hinge axis
(y, at x = 0, z = T) with board.fold()'s rotation. Checkers ride with their half and hide while it folds.
"""
import contextlib, io, json, os, sys, time, traceback

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DATA = os.path.join(HERE, "data")
sys.path[:0] = [os.path.join(ROOT, "cad"), ROOT]

# colour key -> (colour, viewer group label)
LOOK = dict(tray=("#5b3a24", "2 halves (walnut, 18 mm)"), inlay0=("#e9d6b0", "12 points: maple inlay"),
            inlay1=("#c4512a", "12 points: padauk inlay"), leaf=("#c9a54a", "2 butt hinges (brass)"),
            barrel=("#c9a54a", "2 butt hinges (brass)"), mag=("#c7ccd4", "4 magnets (8 x 3)"),
            white=("#f1ead9", "15 light checkers"), black=("#2a2522", "15 dark checkers"), die=("#fbfaf6", "2 dice"))
GROUP = dict(barrel="leaf")


def write(name, obj):
    tmp = os.path.join(DATA, name + ".tmp")
    with open(tmp, "w") as f:
        json.dump(obj, f)
    os.replace(tmp, os.path.join(DATA, name))


def main():
    os.makedirs(DATA, exist_ok=True)
    for f in os.listdir(DATA):
        if f.endswith(".stl"):
            os.remove(os.path.join(DATA, f))
    version = str(int(time.time() * 1000))
    t0 = time.time()
    write("status.json", dict(state="building", version=version, started=time.time()))
    try:
        import importlib, board as bd, make
        importlib.reload(bd)
        importlib.reload(make)
        from build123d import export_stl
        P, C = bd.build(), bd.checkers()
        info = {}
        for n, (s, side, key) in {**P, **C}.items():
            col, lab = LOOK[key]
            export_stl(s, os.path.join(DATA, f"{n}.stl"), tolerance=0.03, angular_tolerance=0.2)
            bb = s.bounding_box()
            info[n] = dict(label=lab, color=col, side=side, group=GROUP.get(key, key), checker=n in C,
                           metal=key in ("leaf", "barrel", "mag"), valid=s.is_valid,
                           size=[round(bb.size.X, 1), round(bb.size.Y, 1), round(bb.size.Z, 1)])
        from build123d import Pos
        for k, p in enumerate(bd.inlay_sheet()[0]):        # the plug sheet, laid out in front of the board
            s = Pos(-125, -bd.HALF_L / 2 - 100, 0) * p
            export_stl(s, os.path.join(DATA, f"sheet{k:02d}.stl"), tolerance=0.03, angular_tolerance=0.2)
            bb = s.bounding_box()
            info[f"sheet{k:02d}"] = dict(label=f"V-carve plug sheet (12 plugs on {bd.PLUG_STOCK:.0f} mm; cut once per wood)",
                                         color="#e9d6b0", side="S", group="sheet", sheet=True,
                                         checker=False, metal=False, valid=s.is_valid,
                                         size=[round(bb.size.X, 1), round(bb.size.Y, 1), round(bb.size.Z, 1)])
        kin = dict(T=bd.T, W=bd.HALF_W, L=bd.HALF_L, cx=bd.CARVERA_X, cy=bd.CARVERA_Y)
        model = dict(version=version, built=time.time(), build_seconds=round(time.time() - t0, 1), parts=info, kin=kin,
                     params=dict(kv=[["Open", f"{2 * bd.HALF_W:.0f} × {bd.HALF_L:.0f} mm"],
                                     ["Closed", f"{bd.HALF_W:.0f} × {bd.HALF_L:.0f} × {2 * bd.T:.0f} mm"],
                                     ["Half", f"{bd.HALF_W:.0f} × {bd.HALF_L:.0f} × {bd.T:.0f} (bed {bd.CARVERA_X:.0f} × {bd.CARVERA_Y:.0f})"],
                                     ["Field", f"{bd.FIELD_W:.0f} × {bd.FIELD_L:.0f}, {bd.POCKET:.0f} deep"],
                                     ["Points", f"{bd.PT_W:.1f} pitch, {bd.PT_LEN:.0f} long, sharp tips, inlay {bd.D_PLUG} thick"],
                                     ["Inlays", f"V-carve, {bd.VBIT_ANGLE:.0f}° bit, pocket {bd.INLAY_P}, glue gap {bd.GLUE_GAP}, plugs from {bd.PLUG_STOCK:.0f} mm"],
                                     ["Checkers", f"Ø{bd.CHK_D:.0f} × {bd.CHK_T:.0f} mm"],
                                     ["Bar", f"{2 * bd.RIM_IN:.0f} mm (the two inner rims)"]]))
        write("model.json", model)
        write("collisions.json", dict(version=version, state="running"))
        write("status.json", dict(state="ok", version=version, seconds=model["build_seconds"]))
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            ok = make.check(P, C)
        lines = [l.rstrip() for l in buf.getvalue().splitlines()]
        write("collisions.json", dict(version=version, state="done", ok=bool(ok), lines=lines, seconds=round(time.time() - t0, 1)))
    except Exception:
        write("status.json", dict(state="error", version=version, error=traceback.format_exc()[-4000:]))
        raise


if __name__ == "__main__":
    main()
