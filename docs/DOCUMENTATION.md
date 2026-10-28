# Backgammon board: documentation

A wooden folding backgammon board, Amir's first Carvera Air project. Repo: `C:\Users\leska\backgammon`. Amir gives the
specs and tests; Claude writes, runs and verifies everything (same way of working as `C:\Users\leska\wave-machine`).

---

## 1. Status (2026-10-28)  ->  START THE NEXT SESSION HERE

| Area | Status |
|---|---|
| Board v0 | Draft CAD (`cad/board.py`), checks pass. **Every choice below is a proposal until Amir decides.** |
| Viewer | `review/serve.py --port=8771` -> http://localhost:8771/review/ (fold slider, Carvera bed outline, checks). |
| Cut files | `make.py export` -> `export/bg_*.step / .stl`. No toolpaths yet. |

### Next steps
1. Amir decides the big ones (2.3): size, wood, how the points are made, checkers.
2. A first test cut in pine / MDF: one corner of a half (rim, field pocket, one point inlay, a hinge mortise, a magnet
   hole) to learn the Carvera, the fits and the inlay method before cutting hardwood.
3. Toolpaths in Makera CAM, then the real halves.

### Missing info
| What | For | Value now |
|---|---|---|
| Carvera Air work area: 300 x 200 (retailers) or 360 x 240 (Makera page) | Half size | 300 x 200 |
| Wood: species, thickness after surfacing, blank size | T, colours | 18 mm walnut, maple / padauk inlays |
| Hinges: a small brass butt hinge (length, leaf width, leaf thickness, knuckle) | Mortises | 30 x 12 x 1, knuckle 4 |
| Magnets | Rim pockets | 8 x 3 discs |
| Tools Amir has (end mills, V-bits) | Inside corners, point tips | 1/8" end mill, 1 mm for the points |

---

## 2. Design

### 2.1 Layout
Open board flat, white at the front. Each half has 12 points (6 front, 6 back); the two inner rims meet at the hinge
and form the bar (18 mm). Point pitch 27.5 mm, 112 long; checkers 26 x 6; a 38 mm strip across the middle for the dice.
Closed, the fields face each other: 20 mm inside, the checkers and dice travel in it.

### 2.2 How it is made (all from the top face, no flipping)
- Each half: one hardwood blank, outline cut with a 1/8" end mill (tool path 289 x 189: 11 mm to spare on the bed).
- Field pocket 10 deep (1.6 mm inside corners); point pockets 1.5 deep in its floor (tips rounded to the tool).
- Points: contrasting wood inlays cut to the same outline (or a V-carve inlay: sharp tips, needs a V-bit).
- Hinges: the leaves recessed flush into both inner rims, the knuckle in a half-round cove on the hinge line; open, the
  board lies flat; closed, the rims meet face to face (checked: nothing collides at 90, 135, 180 deg).
- Magnets: 2 per half in the outer rims, pressed + glued; they meet when closed.

### 2.3 Open choices (Amir)
- **Size.** v0 = travel size (26 mm checkers), each half one piece on the bed. Full size (38-40 mm checkers, open about
  500 x 400) means each half glued up from 2 milled pieces (or a frame + panels).
- **Wood** and colours.
- **Points:** wood inlay / V-carve inlay / V-carved outline + paint / laser (the Air has a laser module option).
- **Checkers:** milled from the same woods (15 + 15), or bought.
- Extras: bear-off trays, dice cups, a doubling cube, a handle / clasp, engraving on the lid.

### 2.4 History
- 2026-10-28: v0 draft (this file).
