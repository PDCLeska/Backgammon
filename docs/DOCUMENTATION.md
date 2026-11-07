# Backgammon board: documentation

A wooden folding backgammon board, Amir's first Carvera Air project. Repo: `C:\Users\leska\backgammon`. Amir gives the
specs and tests; Claude writes, runs and verifies everything (same way of working as `C:\Users\leska\wave-machine`).

---

## 1. Status (2026-10-28)  ->  START THE NEXT SESSION HERE

| Area | Status |
|---|---|
| Board v0 | Draft CAD (`cad/board.py`), checks pass. Walnut halves, epoxy points (turquoise + deep blue), checkers 21 x 6. |
| Points | **Epoxy fill** (Amir): V-carved pockets (90 deg bit, sharp tips), two epoxy colours, faced flush (2.2). Look from Amir's photo: a turquoise line round the field on the rim, a diamond on each outer rim, chamfered edges. |
| Back | **Sea-floor contour map** engraved across both backs (Amir's photo): Saronic Gulf to Syros, coast + every 100 m, 1:442,000, from GMRT data (`art/topo.py`). No route (Amir). |
| Viewer | `review/serve.py --port=8771` -> http://localhost:8771/review/ (fold slider, Carvera bed outline, back view + map, checks). |
| Cut files | `make.py export` -> `export/`: halves, checker (STEP / STL); `bg_points_left/right.dxf` (point, rim line and diamond outlines, a layer per colour); `bg_back_left/right.dxf` (the map, per half). No toolpaths yet. |
| Tools | Ordered from Makera (2.5), + the laser module (Amir has it). |
| **Coaster** | **First: the practice piece** (Amir), every board technique on cheap-to-lose wood (section 3). `cad/coaster.py check export`; viewer http://localhost:8771/review/?model=coaster. |
| Bookmark | Capability test (Amir, 2026-11-06), not part of the board: 40 x 130 x 1 brass (or 3 mm wood, laser), ring tab, name band, our own olive branch cut through. `cad/bookmark.py check export`; viewer `?model=bookmark`. |
| Sunflower bookmark | **The one to cut** (Amir, 2026-11-06): traced from his picture `art/sunflower.png` (the seller's design, for himself only), lines thinned to ~1.5, 0.8 mm brass, "Mrs. Poirier" (his son's teacher) engraved in Edwardian Script. On his 100 x 150 plate, 3 mm from the left edge, the rest kept for a second try. `cad/bookmark_sunflower.py check export` -> `export/bookmarks/`; viewer `?model=bookmarks`. |

### Wood to buy (Amir is in Cary, NC; no saw, so pieces are bought cut to size)
Amir was writing to Capitol City Lumber (Raleigh, 919-832-6492) for these; nothing confirmed as bought yet.
| Piece | Inches | mm | Wood |
|---|---|---|---|
| Board halves x 2 | 7-3/4 x 11-5/8, no bigger | 197 x 295 | 4/4 walnut S2S (dressed 13/16 to 7/8 = 20.6 to 22.2), flat, one clean face |
| Coasters x 4 | 4-3/4 x 6 | 121 x 152 | 1/2" walnut, or 4/4 |
| Tests x 3 | 4-3/4 x 6 | 121 x 152 | Poplar / pine / 1/2" MDF (Home Depot or Lowe's cut it) |

Measure the bed first: if it is really 360 x 240, the board blanks can be 8 x 12.

### Next steps
**Now (2026-11-04): the coaster on the epoxy blank** (section 4): 90 x 90, every technique, 2D in Makera Studio.
0. **The coaster first** (section 3): learn the settings there, then the board. Amir wants something more basic before
   that: a 100 x 100 MDF test plate (a 3 mm pocket, V-carved lines and one point, the outline last with tabs; not
   modelled yet), then the coaster in walnut without epoxy, then the full coaster.
1. When the tools come: measure the 90 deg chamfering bit (cutting diameter -> `VBIT_D`; the model assumes 6, so 3 mm deep).
2. Check Makera CAM can V-carve the point outlines (sharp tips, flat bottom cleared); if not, F-Engrave or VCarve.
3. **Test cut + pour in pine / MDF, then in walnut offcut**: two points of each colour, a piece of rim line, a corner.
   Learn the seal, the pour (bubbles, how proud), cure time, and the facing pass (finish, corner clean-up).
4. Then the real halves (2.2 order).

### Missing info
| What | For | Value now |
|---|---|---|
| Carvera Air work area: 300 x 200 (retailers) or 360 x 240 (Makera page) | Half size | 300 x 200 |
| The bed's real size, and where clamps can go | Blank size (extra wood for the clamps) | unknown: with 300 x 200 travel the tool has only ~5 mm to spare round a half |
| Engraving bit for the map (from the bit set: angle, tip) | Line width | ~0.3 mm lines, 0.4 deep |
| 90 deg chamfering bit: cutting diameter, real tip | `VBIT_D`, inlay depths | 6 mm (3 mm reach) |
| Walnut: thickness after flattening, blank size | `T` | 18.5 mm (faced to 18 after the pour), 2 blanks: half + extra wood for the clamps |
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

### 2.2 How it is made (back first, then one flip; the face side in one clamping)
- Each half: one walnut blank, outline cut last with a 1/8" end mill (half 190 x 286, tool path 289 x 193: 7 mm to
  spare on a 300 x 200 bed).
- **Back: sea-floor contour map** (Amir's photo: ocean topography). `art/topo.py` makes it from GMRT depth data
  (gmrt.org, ~120 m grid, `art/gmrt_aegean.asc`, not in git: the download URL is in the script): the Saronic Gulf
  (Aegina, Attica) to the Cyclades (Kea, Kythnos, Syros, Tinos), the coast + a line every 100 m of depth, smoothed;
  one map running across both backs (356 x 262, 12 mm margin; it carries on over the hinge). Closed, the lid (the right
  half's back) shows the Saronic Gulf, the underside the Cyclades. Engraved ~0.4 deep with a fine V engraving bit
  (~0.3 mm lines); 0.4% of the line length runs closer than 0.6 mm to the next line (steep slopes: they merge into
  one heavier line there). `bg_back_right.dxf` / `bg_back_left.dxf`: each half's lines in its own frame, back up.
  Preview: `art/back_map.png`; in the viewer, the Back button.
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
- Two pours, and each colour's pockets are cut just before its own pour: two point pockets are only 0.5 mm apart at
  the first floor (1.5 when finished), so liquid epoxy would creep into the other colour's open pocket. Cut after
  the first pour has cured, the second colour's pockets take any spill away with the walnut.
- Holding (Amir: keep it scratch-free, load it as few times as possible): clamps and the L bracket only on extra wood
  round the half (cut away with the outline), masking tape or cork under the jaws; painter's tape + CA glue between the
  blank and the spoil board as well; vacuum the bed and the blank first (a chip underneath dents the walnut); tape the
  spoil board round the blank (epoxy running down would glue it to the bed). How much extra wood fits: measure the
  bed (missing info).
- Order, one half (blank 18.5 thick, edges square):
  1. **Back up**: push the blank into the L bracket corner, mark which edge is against it. Engrave the map.
  2. **Flip** end over end about the long edge on the bracket (the same edge back against it), painter's tape under
     the engraved back. From here to step 9 the blank stays clamped: the epoxy cures on the machine, the zero stays.
  3. Field pocket 9.5 deep (0.5 shallow).
  4. V-carve the 6 blue points.
  5. Seal the walnut (thin shellac, or a thin epoxy coat brushed in: stops bleed and bubbles). Pour blue a little proud
     (0.3-0.5 mm), heat-gun the bubbles, cure (as the product says, often 24-72 h).
  6. V-carve the 6 turquoise points, the rim line and the diamond (all from 0.5 above their finished surface).
  7. Seal, pour turquoise, cure.
  8. Face with the Spiral 'O' bit: the field to its full 10 mm, the top to 18 (walnut + epoxy in one pass, light last
     pass 0.1-0.2, sharp bit). The 6 mm bit can't reach the field's corners (r3 against the r1.6 left by the 1/8"
     bit), and 4 points per half reach into them (`make.py check`): a 1/8" clean-up pass round the field corners.
     Then the hinge mortises and magnet holes.
  9. **Outline last**, with small tabs; chamfer the outer top edges.
  10. Off the machine: cut the tabs, sand (320-400 on the epoxy), oil. Press in the magnets, fit the hinges. Keep the
      finished halves covered. The other half the same, mirrored.
- Hinges: the leaves recessed flush into both inner rims, the knuckle in a half-round cove on the hinge line; open, the
  board lies flat; closed, the rims meet face to face (checked: nothing collides at 90, 135, 180 deg).
- Magnets: 2 per half in the outer rims, outboard of the rim line, pressed + glued; they meet when closed.

### 2.3 Open choices (Amir)
- **Size.** Travel size: each half one piece on the bed. Full size (38-40 mm checkers, open about 500 x 400) means
  each half glued up from 2 milled pieces (or a frame + panels).
- **Checkers:** milled from the same woods (15 + 15), or bought.
- Extras: dice cups, a doubling cube, a handle / clasp.
- The map lines: plain engraved, or filled (dark / blue epoxy; the back then needs a 0.5 facing pass, blank 19).

### 2.4 History
- 2026-10-28: v0 draft.
- 2026-10-28 (Amir): no storage pockets (no room at this size: the checkers travel loose in the closed box); points
  as wood inlays: walnut board, maple + padauk points. Bug fixed: the back row's point pockets were cut 1.5 mm too
  deep (hidden under the floor); `check` now tests every inlay's depth. Checkers 26 -> 21 mm: 6 fit on a point.
- 2026-10-28 (Amir): the inlays as V-carve inlays (his earlier plan) instead of flat-bit pockets with rounded tips.
- 2026-10-28 (Amir): walnut + **epoxy fill** instead of maple / padauk plugs (the plug sheet dropped). His reference
  photo: turquoise + deep blue points, a turquoise rim line, rim diamonds, chamfered edges. Magnets 8 -> 6 mm. Amir: the line
  3 mm off the field wall (not 1.2) so it can't break: outer side rim 12 -> 16, half 186 -> 190 wide.
- 2026-10-28 (Amir): magnets 6 x 3 (he has them). Order: each colour's pockets cut just before its pour, blue first;
  the outline last; one clamping for the face side (scratches). The back engraved first (one flip): a sea-floor
  contour map, Saronic Gulf to Syros (his photo + map); the Aegina -> Syros route tried, then dropped (Amir).

### 2.5 Tools and supplies (Amir's list)
From Makera: Essential Milling Bit Set (Standard, 26 bits: flat, ball nose, engraving, 2 x 90 deg V), 6 mm spindle
collet, 90 deg chamfering bit (6 mm shank) x 2 (the points' V-bit: the set's small V-bits reach only ~1.5 mm), Spiral
'O' single-flute bit (6 mm shank, facing after the pour), thick L bracket + side clamp set (holding the 18-20 mm
blanks), 2 mm MDF spoil boards, double-sided tape. Later: dust extraction (Cyclone Lite or a shop vac).
Elsewhere: walnut; pine / MDF for tests; epoxy (coating / tabletop, UV-stable) + turquoise and deep blue pigment
(mica powder), mixing cups, sticks, a heat gun or torch, shellac (sealer); painter's tape + CA glue (holding); sandpaper 120-400; Danish oil or wax; 2 small brass hinges + magnets; dice and cups.

---

## 3. Coffee coaster: the practice piece (Amir, 2026-10-28)

Before the walnut board: one coaster made with every technique of the board, so the settings, the pours and the
flip are learned on a piece that costs little to lose. Make it in pine / poplar first if you like, then walnut.

- 110.5 x 110.5 x 12 (blank 12.5 thick, about 125 x 125 with extra wood for the clamps), corners r8, top edges
  chamfered 1.5. A field 82.5 square, 3 deep (a mug's base sits in it; it holds a drip).
- Top, the board's own features at the board's sizes: 6 points (26 wide, the board's width; 32 long), 3 a side,
  colours alternating and opposite across; a turquoise diamond in the middle; the turquoise rim line all round,
  3 mm off the field wall. Same V-bit, depths, seal, pours, facing (and the O-flute's corner clean-up: 4 points
  reach into the corners).
- Back (`art/coaster_map.py`): a 92 mm square of the sea-floor map round Aegina at the board's scale. The land
  (Aegina, Angistri, Methana, the mainland corner) cut in 0.8 deep as flat recesses (V-bit coast, small end mill
  for the floor; islets under 4 mm2 only lasered as outlines); the sea's depth lines lasered every 50 m (the Saronic
  Gulf is shallow: 100 m gives only a few). The back is the side on the table: it's practice for the board's back.
- Files: `export/coaster.step` / `.stl`; `coaster_top.dxf` (layers `field`, `blue`, `turquoise`; origin front-left);
  `coaster_back.dxf` (layers `islands`, `laser`; as it lies back up, origin front-left).
- Order (the board's, small):
  1. Back up, against the L bracket corner (mark the edge). Skim 0.2-0.3 with the O-flute (flat for the laser and
     the recesses), cut the islands, laser the depth lines (masking tape over the area against smoke stains; try
     power / speed on an offcut first: walnut burns dark on dark).
  2. Flip end over end about the edge on the bracket; painter's tape + CA glue, clamps on the extra wood only.
  3. Field 2.5 deep (0.5 shallow). V-carve the 3 blue points; seal; pour blue; cure.
  4. V-carve the 3 turquoise points, the diamond, the rim line; seal; pour turquoise; cure.
  5. Face: field to 3, top to 12 (O-flute), 1/8" corner clean-up.
  6. Outline with tabs, chamfer. Off: tabs, sand, oil (food-safe finish is not needed: the cup doesn't touch the wood
     long, but a hard oil or wax keeps rings off).
- What to note down for the board: V-bit depth vs real width, how proud to pour and how many bubbles, cure time,
  facing feeds and the finish on walnut + epoxy, the flip's error (look at the outline against the back map), laser
  power / speed for a good line on walnut.
- **Hot cups:** most tabletop epoxies soften at 50-60 C, and a fresh coffee mug's base can be hotter: use a
  heat-resistant epoxy for the coaster (or accept a faint ring on the points); for the board it doesn't matter.

---

## 4. The coaster on the epoxy blank (Amir, 2026-11-04)

The practice piece, every technique, on Makera's epoxy tooling board **150 x 101 x 10** (Amir measured 150 x 101).
Was the pin-flip test plate; Amir: "this is the coaster", do all of it. `cad/pintest.py check export`; pictures
`art/pintest.png` (both sides), `art/pintest_setup.png` (on the bed). Amir: **2D** in Makera Studio (two DXFs, two WCS).

- **Coaster 90 x 90**, corners r8, 10 thick, **both edges chamfered 1.2** (Amir: back as the face; V-bit, 2D Chamfer) (the 110.5 design doesn't fit the 101 blank).
- **Face:** field 72 square, 3 deep; 6 points 22.5 x 27 (24 pitch; the board's are 27.5: Amir chose smaller points to
  keep 3 a side), V-carved 1.4 below the floor; the diamond (12 x 6, 1.4 deep); the rim line (1.6 wide, 3 off the
  field wall). **No epoxy this time** (Amir): V-carve only.
- **Bits: all on the 1/8" collet today** (Amir: no collet change): 1/8" end mill, the set's engraving bit, the set's
  small 90 deg V-bit (reaches ~1.5: hence 1.4 deep V-cuts and 1.2 chamfers). Amir has the 6 mm collet, the 6 mm 90 deg
  chamfering bit and the 6 x 22 O-flute: the collet change is for the next project (the board).
- **Back:** 76 mm square of open sea, no islands (Amir): south of the Saronic Gulf, 23.77 E 37.15 N, 157-1079 m deep,
  a ridge and small seamounts, a line every 100 m (32 lines), engraved 0.4 deep with the engraving bit.
- **Pins:** the Carvera Air's own 4 mm dowel pins. Holes at **X 13 and X 131, Y 50.5** (front-left zero), the same spot
  in both setups, on the flip line; 13 and 19 mm from the ends, so a wrong turn is 6 mm off and can't go on.
  Through the blank + 1 mm into the 2 mm spoil board (the pins only locate; tape + CA hold).
- **Witness windows** (outside the coaster): an 8 mm square 6 deep from the back, a 5 mm square 5 deep from the face.
  Look in from the back: the ring round the 5 mm hole is 1.5 all round if the flip is perfect.
- **Outline:** 2D Contour outside, 10.3 deep (0.3 into the spoil board), 4 tabs (5 long, 1.5 high, mid-side).

Files (origin = the blank's front-left corner as it lies; both setups):
| File | Setup | Layers -> paths |
|---|---|---|
| `export/pintest_1_back.dxf` | WCS1, back up | `pins` -> 2D Pocket 11 deep, 1/8" end mill; `witness` -> 2D Pocket 6 deep; `engrave` -> engrave 0.4, engraving bit; `outline` -> 2D Chamfer 1.2, the set's 90 deg V-bit (only the chamfer here, no cut through) |
| `export/pintest_2_face.dxf` | WCS2, face up | `field` -> 2D Pocket 3; `witness` -> 2D Pocket 5; `points` -> V-carve 1.4 below the field floor (start at 3), the set's 90 deg V-bit; `diamond` -> V-carve 1.4 (start at 3); `rim_line` -> V-carve (from the top); `outline` -> 2D Chamfer 1.2, then 2D Contour outside 10.3 with tabs; `pins` = reference only |
| `export/pintest_pins.dxf` | - | the blank + the 2 pin circles only |
| `export/pintest.step` / `.stl` | - | the finished coaster, to look at (the map lines are not in it) |

Order:
1. **Spoil board** (2 mm MDF) flat on the bed, the **L bracket** at Anchor 1 (front-left) screwed through it; the far
   end held down. It stays put until the coaster is done.
2. **Setup 1, back up:** blank into the bracket corner, painter's tape + CA. XY zero = the bracket corner (Anchor 1,
   offset 0); Z zero on the top. Cut WCS1: pins, back witnesses (1/8" end mill), the map (engraving bit), the back edge chamfer (V-bit).
3. **Flip** front to back (about the pin line). Pins into the spoil board's holes, blank down on them and into the
   bracket corner, tape + CA again. If it won't go on the pins, it's turned the wrong way.
4. **Setup 2, face up:** same XY zero (don't re-probe XY), new Z zero on the top. Cut WCS2: field, face witnesses
   (1/8" end mill); points, diamond, rim line (90 deg V-bit); chamfer on the outline (V-bit); outline with tabs
   (1/8" end mill) last.
5. Off: cut the tabs (knife / flush saw), sand. Read the witness rings from the back; note the flip error here.

Note down for the board: V-bit depth vs real width, how the tooling board cuts (finish, chips), the flip error.

**What happened (2026-11-05, side 1):**
- Pin holes at 4.0 were **too tight** for the 4 mm pins, and 1 mm into the spoil board **didn't hold** them. Amir did the
  flip on the **L bracket** instead (front to back: X exact, Y as exact as the blank's 101 width). Files now: holes 4.1,
  2.5 into the two stacked 2 mm spoil boards (1.5 left above the bed).
- Makera Studio's **2D Chamfer** path wrote G-code with no feed ("Alarm: Undefined feed rate", twice): use a **2D Contour,
  on line** with the 90 deg bit for chamfers instead.
- Studio has **no V-carve** path: the points / diamond were pocketed with the flat 1/8" end mill (rounded tips). For the
  board's epoxy points, find a V-carve route (another CAM, or Studio's 3D) before cutting walnut.
- Double-sided tape over the whole bottom held far too hard: use 3-4 short strips.
- Auto leveling found the blank's top 0.22 mm out of level over 137 x 91: keep leveling on for shallow cuts.
- Face file: `rim_center` layer added = the rim line's centre (one 2D Contour on line, 90 deg bit, 0.75 deep fills the
  1.6 band between the two `rim_line` edges).
