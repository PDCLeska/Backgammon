# Backgammon board: documentation

A wooden folding backgammon board, Amir's first Carvera Air project. Repo: `C:\Users\leska\backgammon`. Amir gives the
specs and tests; Claude writes, runs and verifies everything (same way of working as `C:\Users\leska\wave-machine`).

---

## 1. Status (2026-10-28)  ->  START THE NEXT SESSION HERE

| Area | Status |
|---|---|
| Board v0 | Draft CAD (`cad/board.py`), checks pass. Walnut halves, epoxy points (turquoise + deep blue), checkers 21 x 6. |
| Points | **Epoxy fill** (Amir): V-carved pockets (90 deg bit, sharp tips), two epoxy colours, faced flush (2.2). Look from Amir's photo: a turquoise line round the field on the rim, a diamond on each outer rim, chamfered edges. |
| Viewer | `review/serve.py --port=8771` -> http://localhost:8771/review/ (fold slider, Carvera bed outline, checks). |
| Cut files | `make.py export` -> `export/`: halves, checker (STEP / STL); `bg_points_left/right.dxf` (point, rim line and diamond outlines, a layer per colour). No toolpaths yet. |
| Tools | Ordered from Makera (2.5). |

### Next steps
1. When the tools come: measure the 90 deg chamfering bit (cutting diameter -> `VBIT_D`; the model assumes 6, so 3 mm deep).
2. Check Makera CAM can V-carve the point outlines (sharp tips, flat bottom cleared); if not, F-Engrave or VCarve.
3. **Test cut + pour in pine / MDF, then in walnut offcut**: two points of each colour, a piece of rim line, a corner.
   Learn the seal, the pour (bubbles, how proud), cure time, and the facing pass (finish, corner clean-up).
4. Then the real halves (2.2 order).

### Missing info
| What | For | Value now |
|---|---|---|
| Carvera Air work area: 300 x 200 (retailers) or 360 x 240 (Makera page) | Half size | 300 x 200 |
| 90 deg chamfering bit: cutting diameter, real tip | `VBIT_D`, inlay depths | 6 mm (3 mm reach) |
| Walnut: thickness after flattening, blank size | `T` | 18.5 mm (faced to 18 after the pour), 2 blanks ~200 x 300 |
| Epoxy: product, colours (turquoise, deep blue pigment / mica) | Pour depth | 2.5 mm pours (coating / tabletop epoxy is fine) |
| Hinges: a small brass butt hinge (length, leaf width, leaf thickness, knuckle) | Mortises | 30 x 12 x 1, knuckle 4 |
| Magnets | Rim pockets | 6 x 3 discs: Amir has them (measure one: diameter for the press fit) |

---

## 2. Design

### 2.1 Layout
Open board flat, white at the front. Each half has 12 points (6 front, 6 back); the two inner rims meet at the hinge
and form the bar (18 mm). Point pitch 27.5 mm, 112 long, base 1 mm off the field wall; checkers 21 x 6 (6 in a row
reach 126 of the 131 mm to the middle: 10 mm between two full rows); a 38 mm strip across the middle for the dice.
Closed, the fields face each other: 20 mm inside, the checkers and dice travel in it.

### 2.2 How it is made (the halves all from the top face, no flipping)
- Each half: one walnut blank, outline cut with a 1/8" end mill (half 190 x 286, tool path 289 x 193: 7 mm to spare on the bed).
- Field pocket 10 deep (1.6 mm inside corners).
- **Points: epoxy fill** (Amir). An end mill can't cut a sharp inside corner; the 90 deg V-bit can, so every pocket is
  V-carved (45 deg walls, flat bottom cleared) and the tips stay sharp. The look follows Amir's reference photo:
  - 24 points, turquoise and deep blue alternating; V-carved 2.5 deep into the first field floor (2.0 when finished).
  - A turquoise **rim line** on the rim top, 1.6 wide (V-groove), 3 mm outside the field wall (Amir: away from the
    wall, so the strip between can't break), round the front, back and outer rims (not along the bar: the hinges).
    The outer side rim is 16 wide (the others 12) to fit the line, then the magnets and the diamond outboard of it;
    `make.py check` reports the walnut left round them (>= 1.5).
  - A turquoise **diamond** (12 x 6, V-carved 1.5) in the middle of each outer side rim.
  - Outer top edges chamfered 1.5 (the hinge side square).
  - `bg_points_right.dxf` / `bg_points_left.dxf`: the outlines for the V-carve toolpaths, layers `turquoise` / `blue`.
- Two pours, because two point pockets are only 0.5 mm apart at the first floor (1.5 when finished): one colour would
  run into the next pocket.
- Order, one half (blank 18.5 thick; leave it clamped from step 1 to 6, don't lose the zero):
  1. Cut the outline (chamfer last), the field 9.5 deep (0.5 shallow).
  2. V-carve the 12 turquoise pockets, the rim line and the diamond (all from 0.5 above their finished surface).
  3. Seal the walnut (thin shellac or a thin epoxy coat brushed in; stops bleed and bubbles). Pour turquoise a little
     proud (0.3-0.5 mm), torch / heat-gun the bubbles, cure (as the product says, often 24-72 h).
  4. V-carve the 6 blue pockets (the cured turquoise overflow is cut away with them), seal, pour blue, cure.
  5. Face with the Spiral 'O' bit: the field to its full 10 mm, the rim top to 18 (walnut + epoxy in one pass, light last
     pass 0.1-0.2, sharp bit). The 6 mm bit can't reach the field's corners (r3 against the r1.6 left by the 1/8"
     bit), and 4 points per half reach into them (`make.py check`): a 1/8" clean-up pass round the field corners.
  6. Hinge mortises, magnet holes. Sand (to 320-400 on the epoxy), oil the walnut.
- Hinges: the leaves recessed flush into both inner rims, the knuckle in a half-round cove on the hinge line; open, the
  board lies flat; closed, the rims meet face to face (checked: nothing collides at 90, 135, 180 deg).
- Magnets: 2 per half in the outer rims, outboard of the rim line, pressed + glued; they meet when closed.

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
- 2026-10-28 (Amir): walnut + **epoxy fill** instead of maple / padauk plugs (the plug sheet dropped). His reference
  photo: turquoise + deep blue points, a turquoise rim line, rim diamonds, chamfered edges. Magnets 8 -> 6 mm. Amir: the line
  3 mm off the field wall (not 1.2) so it can't break: outer side rim 12 -> 16, half 186 -> 190 wide.

### 2.5 Tools and supplies (Amir's list)
From Makera: Essential Milling Bit Set (Standard, 26 bits: flat, ball nose, engraving, 2 x 90 deg V), 6 mm spindle
collet, 90 deg chamfering bit (6 mm shank) x 2 (the points' V-bit: the set's small V-bits reach only ~1.5 mm), Spiral
'O' single-flute bit (6 mm shank, facing after the pour), thick L bracket + side clamp set (holding the 18-20 mm
blanks), 2 mm MDF spoil boards, double-sided tape. Later: dust extraction (Cyclone Lite or a shop vac).
Elsewhere: walnut; pine / MDF for tests; epoxy (coating / tabletop, UV-stable) + turquoise and deep blue pigment
(mica powder), mixing cups, sticks, a heat gun or torch, shellac (sealer); sandpaper 120-400; Danish oil or wax; 2 small brass hinges + magnets; dice and cups.
