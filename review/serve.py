"""Backgammon board review server (the CAD model).

Serves the viewer at http://localhost:8771/ and rebuilds the viewer data whenever a
model source file changes:
cad/*.py -> review/data/.
POST /rebuild forces a rebuild.
"""
import glob, os, subprocess, sys, threading, time, webbrowser
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
PORT = int(next((a.split("=")[1] for a in sys.argv if a.startswith("--port=")), os.environ.get("REVIEW_PORT", 8771)))
PY = sys.executable
_lock = threading.Lock()
_procs = {}
# model -> (source glob, builder script, data dir)
MODELS = {"board": (os.path.join("cad", "*.py"), "build_data.py", "data"),
          "coaster": (os.path.join("cad", "*.py"), "build_coaster.py", "data_coaster"),
          "bookmark": (os.path.join("cad", "*.py"), "build_bookmark.py", "data_bookmark"),
          "bookmarks": (os.path.join("cad", "*.py"), "build_bookmarks.py", "data_bookmarks")}


def sources(model):
    return {p: os.path.getmtime(p) for p in glob.glob(os.path.join(ROOT, MODELS[model][0]))}


def rebuild(reason, model="board"):
    """Start a build; if one is running, kill it and start over with the newest source."""
    with _lock:
        proc = _procs.get(model)
        if proc and proc.poll() is None:
            proc.kill()
            proc.wait()
        print(f"[review] rebuilding {model} ({reason})", flush=True)
        _procs[model] = subprocess.Popen([PY, os.path.join(HERE, MODELS[model][1])], cwd=ROOT)


def watcher():
    seen = {m: sources(m) for m in MODELS}
    for m in MODELS:
        if not os.path.exists(os.path.join(HERE, MODELS[m][2], "model.json")):
            rebuild("no data yet", m)
    while True:
        time.sleep(1.0)
        for m in MODELS:
            now = sources(m)
            if now != seen[m]:
                changed = [os.path.basename(p) for p in now if now.get(p) != seen[m].get(p)]
                seen[m] = now
                time.sleep(0.3)          # let the editor finish writing
                rebuild("changed: " + ", ".join(changed), m)


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *a, **kw):
        super().__init__(*a, directory=ROOT, **kw)

    def end_headers(self):
        self.send_header("Cache-Control", "no-store")
        super().end_headers()

    def do_GET(self):
        if self.path in ("/", "/index.html"):
            self.send_response(302)
            self.send_header("Location", "/review/")
            self.end_headers()
            return
        return super().do_GET()

    def do_POST(self):
        if self.path.split("?")[0] == "/rebuild":
            m = self.path.split("model=")[1].split("&")[0] if "model=" in self.path else "board"
            rebuild("requested from viewer", m if m in MODELS else "board")
            self.send_response(204)
            self.end_headers()
        else:
            self.send_error(404)

    def log_message(self, *a):
        pass


if __name__ == "__main__":
    threading.Thread(target=watcher, daemon=True).start()
    url = f"http://localhost:{PORT}/"
    print(f"[review] serving {url}  (Ctrl+C to stop)", flush=True)
    if "--no-browser" not in sys.argv:
        threading.Timer(1.0, lambda: webbrowser.open(url)).start()
    ThreadingHTTPServer(("127.0.0.1", PORT), Handler).serve_forever()
