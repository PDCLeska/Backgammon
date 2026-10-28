"""Build the viewer data for the coffee coaster (cad/coaster.py) -> review/data_coaster/. Open the viewer with ?model=coaster."""
import contextlib, io, json, os, sys, time, traceback

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DATA = os.path.join(HERE, "data_coaster")
sys.path[:0] = [os.path.join(ROOT, "cad"), ROOT]
from build_data import LOOK

LOOK = {**LOOK, "tray": ("#5b3a24", "coaster (walnut, 12 mm)"), "fill0": (LOOK["fill0"][0], "turquoise epoxy (3 points, rim line, diamond)"),
        "fill1": (LOOK["fill1"][0], "3 points: deep blue epoxy")}


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
        import importlib, board, coaster as co
        importlib.reload(board); importlib.reload(co)
        from build123d import export_stl
        P = co.build()
        info = {}
        for n, (s, side, key) in P.items():
            col, lab = LOOK[key]
            export_stl(s, os.path.join(DATA, f"{n}.stl"), tolerance=0.02, angular_tolerance=0.2)
            bb = s.bounding_box()
            info[n] = dict(label=lab, color=col, side=side, group=key, checker=False, metal=False, valid=s.is_valid,
                           size=[round(bb.size.X, 1), round(bb.size.Y, 1), round(bb.size.Z, 1)])
        bm = co.back_map()
        laser = [[(-u, v) for u, v in l["pts"]] for l in bm["sea"]]      # back view -> model frame
        kin = dict(T=co.T, W=co.W, L=co.W, cx=board.CARVERA_X, cy=board.CARVERA_Y, fold=False, bedx=0)
        model = dict(version=version, built=time.time(), build_seconds=round(time.time() - t0, 1), parts=info, kin=kin,
                     title="Coffee coaster (practice piece)", back=dict(C=laser),
                     params=dict(kv=[["Size", f"{co.W:.1f} × {co.W:.1f} × {co.T:.0f} mm (blank {co.T + board.FACE:.1f})"],
                                     ["Field", f"{co.FIELD:.1f} square, {co.POCKET:.0f} deep"],
                                     ["Points", f"6, {board.PT_BASE:.0f} wide × {co.PT_LEN:.0f} long, epoxy {co.D_FIN} thick"],
                                     ["Back", f"Aegina, {bm['info']['size']:.0f} mm: land cut in {co.ISLAND_D}, depth lines lasered every {bm['info']['step']} m"]]))
        write("model.json", model)
        write("collisions.json", dict(version=version, state="running"))
        write("status.json", dict(state="ok", version=version, seconds=model["build_seconds"]))
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            ok = co.check(P)
        lines = [l.rstrip() for l in buf.getvalue().splitlines()]
        write("collisions.json", dict(version=version, state="done", ok=bool(ok), lines=lines, seconds=round(time.time() - t0, 1)))
    except Exception:
        write("status.json", dict(state="error", version=version, error=traceback.format_exc()[-4000:]))
        raise


if __name__ == "__main__":
    main()
