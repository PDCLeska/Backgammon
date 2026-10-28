# Backgammon board: project context

Amir's first project on his new Makera Carvera Air (desktop CNC): a wooden backgammon board, folding case, checkers.
Same way of working as `C:\Users\leska\wave-machine` and `C:\Users\leska\nightstand`: Amir gives the specs and tests;
Claude writes, runs and verifies everything. Keep updates short and plain. Every mistake costs wood: test cuts in
cheap stock (pine / MDF) first. Start the next session from `docs/DOCUMENTATION.md` section 1.

## Machine
- Carvera Air, 3-axis work area 300 x 200 x 130 mm (retail spec sheets; Makera's own page says 360 x 240: confirm on
  the machine). Every part must fit that with the tool around its outline: `make.py check` says the margin.
- CAM: Makera CAM / Makera Studio takes STEP, STL, SVG, DXF. `make.py export` writes STEP + STL per part.

## Decisions (2026-10-28, v0 draft: all open until Amir says)
- Two halves, one solid tray each (186 x 286 x 18), field pocketed 10 deep, points inlaid 1.5 deep, butt hinges
  recessed into the inner rims (all milled from the top face), magnets in the outer rims. Open 372 x 286, closed
  186 x 286 x 36 (checkers and dice inside).
- Checkers 21 x 6 (Amir, 2026-10-28: 6 in a row on a point, 10 mm left in the middle between two full rows).
- Amir (2026-10-28): **points are wood inlays**, one wood for the board, two others for the points; **no storage
  pockets** (no room at this size). Inlay order and the cutting sheet: docs 2.2.
- Amir (2026-10-28): **walnut board, maple + padauk points.**

## CAD
- Env: `C:\Users\leska\cadenv` (build123d). `cad\board.py` = model, `cad\make.py check export`.
- Viewer: `review\serve.py --port=8771` -> http://localhost:8771/review/ (rebuilds on save; fold slider, Carvera bed outline).
- Run `check` before handing over any geometry change; say which files changed.
- Bought-part sizes (hinges, magnets) are placeholders until chosen / measured: docs "Missing info".
- Ask before changing things he said to hold ("let's talk first" means no edits yet).
