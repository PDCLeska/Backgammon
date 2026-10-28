# Backgammon board: documentation

A wooden folding backgammon board, Amir's first Carvera Air project. Repo: `C:\Users\leska\backgammon`. Amir gives the
specs and tests; Claude writes, runs and verifies everything (same way of working as `C:\Users\leska\wave-machine`).

---

## 1. Status (2026-10-28)  ->  START THE NEXT SESSION HERE

| Area | Status |
|---|---|
| Board v0 | Draft CAD (`cad/board.py`), checks pass. **Every choice below is a proposal until Amir decides.** |
| Viewer | `review/serve.py --port=8771` -> http://localhost:8771/review/ (fold slider, Carvera bed outline, checks). |
| Points (Amir, 2026-10-28) | **Wood inlays**: the board one wood, the points two other woods (12 + 12). Pockets, fitted pieces, nested cutting sheet done (2.2). |
| Cut files | `make.py export` -> `export/bg_*.step / .stl`, `bg_inlay_sheet.dxf`. No toolpaths yet. |

### Next steps
1. Amir decides (2.3): size, checkers. (Woods decided: walnut, maple, padauk.)
2. A first test cut in pine / MDF: one corner of a half (rim, field pocket, one point pocket + its piece, a hinge
   mortise, a magnet hole) to learn the Carvera and to tune `INLAY_FIT` before cutting hardwood.
3. Toolpaths in Makera CAM, then the real halves.

### Missing info
| What | For | Value now |
|---|---|---|
| Carvera Air work area: 300 x 200 (retailers) or 360 x 240 (Makera page) | Half size | 300 x 200 |
| Wood: species, thickness after surfacing, blank size | T, colours | 18 mm walnut, maple / padauk inlays |
| Hinges: a small brass butt hinge (length, leaf width, leaf thickness, knuckle) | Mortises | 30 x 12 x 1, knuckle 4 |
| Magnets | Rim pockets | 8 x 3 discs |
| Tools Amir has (end mills, V-bits) | Inside corners, point tips | 1/8" end mill, 1 mm for the points |
| Inlay wood thickness (>= 2.8 mm) | `INLAY_STOCK` | 3 mm (maple + padauk) |
| Inlay fit on the real machine and wood | `INLAY_FIT` | 0.08 a side (test cut) |

---

## 2. Design

### 2.1 Layout
Open board flat, white at the front. Each half has 12 points (6 front, 6 back); the two inner rims meet at the hinge
and form the bar (18 mm). Point pitch 27.5 mm, 112 long; checkers 21 x 6 (6 in a row reach 126 of the 131 mm to the middle: 10 mm between two full rows); a 38 mm strip across the middle for the dice.
Closed, the fields face each other: 20 mm inside, the checkers and dice travel in it.

### 2.2 How it is made (all from the top face, no flipping)
- Each half: one hardwood blank, outline cut with a 1/8" end mill (tool path 289 x 189: 11 mm to spare on the bed).
- Field pocket 10 deep (1.6 mm inside corners); point pockets 1.5 deep in its finished floor.
- Points = wood inlays (Amir): one wood for the board, two others for the points. An end mill can't cut a sharp inside
  corner, so every corner of a point pocket is rounded to the inlay end mill (r 0.5 with a 1 mm mill; the tip ends
  ~4 mm short of the sharp triangle). Each piece is the pocket's outline 0.08 smaller all round (glue line), so it
  drops in with glue. All 24 points are the same shape: one nested sheet (12 pieces, alternately up / down, 4.3 apart,
  215 x 112 on a 223 x 120 x 3 blank) cut once in each inlay wood (`bg_inlay_sheet.dxf / .step`); small tabs in CAM.
- Inlay order, one half:
  1. Cut the outline, the field 9.5 deep (0.5 shallow), the point pockets 2.0 below that, hinge mortises, magnet holes.
  2. Leave the half clamped (or mark the zero): glue in the 12 pieces, alternating woods, 1.0 mm proud.
  3. When dry, face the field floor to its full 10 mm: takes the 0.5 of floor and the pieces flush in one pass.
- Hinges: the leaves recessed flush into both inner rims, the knuckle in a half-round cove on the hinge line; open, the
  board lies flat; closed, the rims meet face to face (checked: nothing collides at 90, 135, 180 deg).
- Magnets: 2 per half in the outer rims, pressed + glued; they meet when closed.

### 2.3 Open choices (Amir)
- **Size.** v0 = travel size (26 mm checkers), each half one piece on the bed. Full size (38-40 mm checkers, open about
  500 x 400) means each half glued up from 2 milled pieces (or a frame + panels).
- Woods (decided 2026-10-28): walnut board, maple + padauk points. Padauk dust stains maple: shellac the board
  before the facing pass (or vacuum constantly).
- **Checkers:** milled from the same woods (15 + 15), or bought.
- Extras: bear-off trays, dice cups, a doubling cube, a handle / clasp, engraving on the lid.

### 2.4 History
- 2026-10-28: v0 draft (this file).
- 2026-10-28 (Amir): no storage pockets (no room at this size: the checkers travel loose in the closed box); points
  as wood inlays in two woods on a board of a third. Then: walnut board, maple + padauk points. Bug fixed: the back
  row's point pockets were cut 1.5 mm too deep (hidden under the floor); `check` now tests every inlay's depth. Checkers 26 -> 21 mm: 6 fit on a point.
