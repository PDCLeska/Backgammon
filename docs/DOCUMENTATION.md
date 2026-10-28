# Backgammon board: documentation

A wooden folding backgammon board, Amir's first Carvera Air project. Repo: `C:\Users\leska\backgammon`. Amir gives the
specs and tests; Claude writes, runs and verifies everything (same way of working as `C:\Users\leska\wave-machine`).

---

## 1. Status (2026-10-28)  ->  START THE NEXT SESSION HERE

| Area | Status |
|---|---|
| Board v0 | Draft CAD (`cad/board.py`), checks pass. Walnut halves, maple + padauk points, checkers 21 x 6. |
| Points | **V-carve inlay** (Amir's plan): 90 deg V-bit, sharp tips; pockets in the field floor, plugs from 10 mm maple / padauk (2.2). |
| Viewer | `review/serve.py --port=8771` -> http://localhost:8771/review/ (fold slider, Carvera bed outline, plug sheet, checks). |
| Cut files | `make.py export` -> `export/`: halves, plug sheet, checker (STEP / STL); `bg_points_left/right.dxf` for the inlay software. No toolpaths yet. |
| Tools | Ordered from Makera (2.5). |

### Next steps
1. When the tools come: measure the 90 deg chamfering bit (cutting diameter -> `VBIT_D`; the model assumes 6, so 3 mm deep).
2. Choose the inlay software: F-Engrave (free) or VCarve Pro (paid, easier); Makera CAM's inlay support unconfirmed.
3. **Test cut in pine / MDF**: two points (pocket + plug), a piece of rim, a hinge mortise, a magnet hole. Tune the
   glue gap and start depth until the plugs seat and the facing pass leaves clean, sharp tips.
4. Then the real halves (2.2 order).

### Missing info
| What | For | Value now |
|---|---|---|
| Carvera Air work area: 300 x 200 (retailers) or 360 x 240 (Makera page) | Half size | 300 x 200 |
| 90 deg chamfering bit: cutting diameter, real tip | `VBIT_D`, inlay depths | 6 mm (3 mm reach) |
| Walnut: thickness after flattening, blank size | `T` | 18 mm, 2 blanks ~200 x 300 |
| Maple / padauk plug wood thickness | `PLUG_STOCK` | 10 mm (needs >= 5) |
| Glue gap and start depth that work on the real bit and wood | `GLUE_GAP`, `PLUG_START` | 0.5 / 1.0 (test cut) |
| Hinges: a small brass butt hinge (length, leaf width, leaf thickness, knuckle) | Mortises | 30 x 12 x 1, knuckle 4 |
| Magnets | Rim pockets | 8 x 3 discs |

---

## 2. Design

### 2.1 Layout
Open board flat, white at the front. Each half has 12 points (6 front, 6 back); the two inner rims meet at the hinge
and form the bar (18 mm). Point pitch 27.5 mm, 112 long, base 1 mm off the field wall; checkers 21 x 6 (6 in a row
reach 126 of the 131 mm to the middle: 10 mm between two full rows); a 38 mm strip across the middle for the dice.
Closed, the fields face each other: 20 mm inside, the checkers and dice travel in it.

### 2.2 How it is made (the halves all from the top face, no flipping)
- Each half: one walnut blank, outline cut with a 1/8" end mill (tool path 289 x 189: 11 mm to spare on the bed).
- Field pocket 10 deep (1.6 mm inside corners).
- **Points: V-carve inlay** (Amir's plan, from his earlier research; F-Engrave / VCarve "inlay" do the toolpaths).
  An end mill can't cut a sharp inside corner; a V-bit can, so the tips stay sharp. The 90 deg bit cuts 45 deg walls:
  - Pocket: V-carved 2.5 deep into the first field floor, flat bottom cleared (21.5 wide at the base, 93 long).
  - Plug: the same triangle carved as a raised island in 10 mm maple / padauk, walls 3.0 tall, a 1 mm x 2 mm skirt
    round its base, then cut free. Flipped into the pocket, its walls wedge on the pocket's (no side gap); its narrow
    end stops 0.5 above the pocket floor (glue gap).
  - One plug sheet per wood (`bg_plug_sheet.step`): 12 plugs, alternately up / down, skirts 4.2 apart, on a 260 x 145
    x 10 blank. A triangle is its own mirror image, so the flip changes nothing.
  - `bg_points_right.dxf` / `bg_points_left.dxf`: the field outline and the 12 point outlines of each half at the first
    floor, layers `maple` / `padauk`, for the inlay software.
- Order, one half:
  1. Cut the outline, the field 9.5 deep (0.5 shallow), hinge mortises, magnet holes; V-carve the 12 pockets.
  2. Leave the half clamped (or mark the zero). Glue in the 12 plugs (Titebond III), alternating woods; press them
     down (a caul across the field, clamps).
  3. Shellac the field (padauk dust stains maple). When dry, face the field to its full 10 mm with the O-flute bit: it
     takes the skirts, the 1.0 start and 0.5 of floor; the plugs end 1.5 thick and flush, tips sharp.
- Hinges: the leaves recessed flush into both inner rims, the knuckle in a half-round cove on the hinge line; open, the
  board lies flat; closed, the rims meet face to face (checked: nothing collides at 90, 135, 180 deg).
- Magnets: 2 per half in the outer rims, pressed + glued; they meet when closed.

### 2.3 Open choices (Amir)
- **Size.** Travel size: each half one piece on the bed. Full size (38-40 mm checkers, open about 500 x 400) means
  each half glued up from 2 milled pieces (or a frame + panels).
- **Checkers:** milled from the same woods (15 + 15), or bought.
- Extras: dice cups, a doubling cube, a handle / clasp, engraving on the lid.

### 2.4 History
- 2026-10-28: v0 draft.
- 2026-10-28 (Amir): no storage pockets (no room at this size: the checkers travel loose in the closed box); points
  as wood inlays: walnut board, maple + padauk points. Bug fixed: the back row's point pockets were cut 1.5 mm too
  deep (hidden under the floor); `check` now tests every inlay's depth. Checkers 26 -> 21 mm: 6 fit on a point.
- 2026-10-28 (Amir): the inlays as V-carve inlays (his earlier plan) instead of flat-bit pockets with rounded tips.

### 2.5 Tools and supplies (Amir's list)
From Makera: Essential Milling Bit Set (Standard, 26 bits: flat, ball nose, engraving, 2 x 90 deg V), 6 mm spindle
collet, 90 deg chamfering bit (6 mm shank) x 2 (the inlay V-bit: the set's small V-bits reach only ~1.5 mm), Spiral
'O' single-flute bit (6 mm shank, facing after glue-up), thick L bracket + side clamp set (holding the 18-20 mm
blanks), 2 mm MDF spoil boards, double-sided tape (the plug sheets). Later: dust extraction (Cyclone Lite or a shop vac).
Elsewhere: walnut, maple, padauk; pine / MDF for tests; Titebond III; 2-4 clamps; sandpaper 120-220; Danish oil or
wax; 2 small brass hinges + magnets; dice and cups.
