# Backgammon board

A wooden folding backgammon board milled on a Makera Carvera Air: two solid halves with inlaid points, recessed
brass hinges and magnet catches; closed, it is a box for the checkers and dice.

Full documentation (status and next steps first): [docs/DOCUMENTATION.md](docs/DOCUMENTATION.md)

```
C:\Users\leska\cadenv\Scripts\python cad\make.py check export
C:\Users\leska\cadenv\Scripts\python review\serve.py --port=8771
```

## On another computer (the laptop at the Carvera)

The cut files are already in `export/`. To open them in Makera CAM you only need the repo:

```
git clone <this repo's URL>
```

To change the models or run the viewer, also make the Python environment (Python 3.14) once. The commands above and
`.claude/launch.json` assume it is at `C:\Users\leska\cadenv`; use that path on the laptop if you can, or change them.

```
python -m venv C:\Users\leska\cadenv
C:\Users\leska\cadenv\Scripts\python -m pip install -r requirements.txt
```

Before working: `git pull`. After working: commit and `git push`, so both computers stay the same.
