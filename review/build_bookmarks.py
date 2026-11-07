"""Viewer data for the sunflower bookmark on Amir's brass plate (cad/bookmark_sunflower.py) -> review/data_bookmarks/.
Open the viewer with ?model=bookmarks."""
import contextlib, io, json, os, sys, time, traceback

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DATA = os.path.join(HERE, "data_bookmarks")
sys.path[:0] = [os.path.join(ROOT, "cad"), ROOT]


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
        import importlib, board, bookmark, bookmark_sunflower as bs
        importlib.reload(board); importlib.reload(bookmark); importlib.reload(bs)
        from build123d import export_stl, Pos, Box, Align
        mv = bs.on_plate()
        s = mv * bs.build()
        plate = Pos(0, 0, -0.05) * Box(*bs.PLATE, 0.05, align=(Align.MIN, Align.MIN, Align.MIN))   # the stock, under it
        info = {}
        for n, solid, lab, col in (("sunflower", s, f"sunflower bookmark (brass, {bs.T:g} mm)", "#d4a73c"),
                                   ("plate", plate, f"brass plate {bs.PLATE[0]:.0f} × {bs.PLATE[1]:.0f} (stock)", "#efe3c2")):
            export_stl(solid, os.path.join(DATA, f"{n}.stl"), tolerance=0.01, angular_tolerance=0.1)
            bb = solid.bounding_box()
            info[n] = dict(label=lab, color=col, side="C", group=n, checker=False, metal=False, valid=solid.is_valid,
                           size=[round(bb.size.X, 1), round(bb.size.Y, 1), round(bb.size.Z, 1)])
        bb = s.bounding_box()
        kin = dict(T=bs.T, W=bs.PLATE[0], L=bs.PLATE[1], cx=board.CARVERA_X, cy=board.CARVERA_Y, fold=False, bedx=0)
        model = dict(version=version, built=time.time(), build_seconds=round(time.time() - t0, 1), parts=info, kin=kin,
                     title="Sunflower bookmark on the brass plate",
                     params=dict(kv=[["Bookmark", f"{bb.size.X:.1f} × {bb.size.Y:.1f} × {bs.T:g} mm, traced from Amir's picture"],
                                     ["On the plate", f"{bs.MARGIN:g} mm from the left edge, centred along it: "
                                                      f"x {bb.min.X:.1f}–{bb.max.X:.1f}, y {bb.min.Y:.1f}–{bb.max.Y:.1f}"],
                                     ["Name", f"\"{bs.NAME}\", {bs.FONT_FILE.split('/')[-1]}, {bs.TEXT_H:g} mm, "
                                              f"engraved {bs.TEXT_D:g} deep"],
                                     ["Cut", f"{bookmark.TOOL_D:g} mm end mill; the rest of the plate for a second try"]]))
        write("model.json", model)
        write("collisions.json", dict(version=version, state="running"))
        write("status.json", dict(state="ok", version=version, seconds=model["build_seconds"]))
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            ok = bs.check()
        lines = [l.rstrip() for l in buf.getvalue().splitlines()]
        write("collisions.json", dict(version=version, state="done", ok=bool(ok), lines=lines, seconds=round(time.time() - t0, 1)))
    except Exception:
        write("status.json", dict(state="error", version=version, error=traceback.format_exc()[-4000:]))
        raise


if __name__ == "__main__":
    main()
