"""Build the viewer data for a bookmark -> review/data_<model>/: cad/bookmark.py (?model=bookmark), or the one traced
from Amir's picture: see build_bookmarks.py (?model=bookmarks, the sunflower on the plate)."""
import contextlib, io, json, os, sys, time, traceback

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path[:0] = [os.path.join(ROOT, "cad"), ROOT]


def main(module="bookmark", data="data_bookmark", title="Bookmark (capability test)", inside="olive branch, cut through"):
    DATA = os.path.join(HERE, data)

    def write(name, obj):
        tmp = os.path.join(DATA, name + ".tmp")
        with open(tmp, "w") as f:
            json.dump(obj, f)
        os.replace(tmp, os.path.join(DATA, name))

    os.makedirs(DATA, exist_ok=True)
    for f in os.listdir(DATA):
        if f.endswith(".stl"):
            os.remove(os.path.join(DATA, f))
    version = str(int(time.time() * 1000))
    t0 = time.time()
    write("status.json", dict(state="building", version=version, started=time.time()))
    try:
        import importlib, board, bookmark
        importlib.reload(board); importlib.reload(bookmark)
        bm = importlib.reload(importlib.import_module(module))
        from build123d import export_stl
        s = bm.build()
        export_stl(s, os.path.join(DATA, "bookmark.stl"), tolerance=0.01, angular_tolerance=0.1)
        bb = s.bounding_box()
        info = dict(bookmark=dict(label=f"bookmark (brass, {bm.T:g} mm)", color="#d4a73c", side="C", group="brass",
                                  checker=False, metal=False, valid=s.is_valid,
                                  size=[round(bb.size.X, 1), round(bb.size.Y, 1), round(bb.size.Z, 1)]))
        kin = dict(T=bm.T, W=round(bb.size.X, 1), L=round(bb.size.Y, 1), cx=board.CARVERA_X, cy=board.CARVERA_Y, fold=False, bedx=0)
        model = dict(version=version, built=time.time(), build_seconds=round(time.time() - t0, 1), parts=info, kin=kin,
                     title=title,
                     params=dict(kv=[["Size", f"{bb.size.X:.0f} × {bb.size.Y:.0f} × {bm.T:g} mm, ring tab on top"],
                                     ["Inside", inside],
                                     ["Name", f"\"{bm.NAME}\", {getattr(bm, 'FONT_FILE', getattr(bm, 'FONT', '')).split('/')[-1]}, "
                                              f"{bm.TEXT_H:g} mm, engraved {bm.TEXT_D:g} deep"],
                                     ["Cut", f"{bookmark.TOOL_D:g} mm end mill (brass), or the laser (3 mm wood)"]]))
        write("model.json", model)
        write("collisions.json", dict(version=version, state="running"))
        write("status.json", dict(state="ok", version=version, seconds=model["build_seconds"]))
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            ok = bm.check()
        lines = [l.rstrip() for l in buf.getvalue().splitlines()]
        write("collisions.json", dict(version=version, state="done", ok=bool(ok), lines=lines, seconds=round(time.time() - t0, 1)))
    except Exception:
        write("status.json", dict(state="error", version=version, error=traceback.format_exc()[-4000:]))
        raise


if __name__ == "__main__":
    main()
