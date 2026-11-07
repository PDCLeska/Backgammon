# Handoff: from the desktop session to the laptop at the Carvera (2026-11-06)

For the Claude session on Amir's laptop. Read this first, then `CLAUDE.md` and `docs/DOCUMENTATION.md` section 1.
It covers what the desktop session did since 2026-10-28 that the laptop doesn't know, and what is open.

Both computers' work is merged on GitHub (`main`, merge commit `1ba6ec2`): the laptop's pin-flip coaster work
(docs section 4) and the desktop's bookmarks. Before working: `git pull`. After: commit and `git push`.

---

## 0. Update from the cloud session (2026-11-07)
- **Plate now 100 x 200 x 3 mm brass** (Amir). `T = 3.0`, `PLATE = (100, 200)`. The bookmark stays 40.1 x 115.3, 3 mm
  from the left edge, centred on the 200 length (x 3.0-43.1, y 42.4-157.6); 55.9 x 200 left for a second try.
- **DXF now closed shapes** (`sunflower_on_plate.dxf`): `outline` 1 closed polyline, `cut` 47 closed polylines (one per
  cut-out), `engrave` 18 closed letter outlines, `plate` reference. (Was 2,410 loose lines + 377 splines.)
- **The name without the font:** `art/sunflower_name.json` holds the letter outlines (Edwardian Script, from the
  desktop's export; overlaps resolved even-odd). `name_loops()` uses the font when installed (and refreshes the json),
  else the json. All letters valid; STEP valid.
- **Bits for 3 mm brass:** the 1 mm end mill is too short (~3 mm flute). Plan: **rough** the cut-outs with the 1/8"
  (3.175) **metal** end mill (2D Pocket: clears 86 % of the cut-out area), **finish** with the **1.5 x 8 mm** metal end
  mill (2D Contour inside; 9 spots end slightly rounder at petal tips / corners; scaling up doesn't remove them).
  Outline with the 1.5 (outside, tabs). Contour, not pocket, for the finish: pocketing all with the small bit ~3 h+.
  Estimate ~2-3 h total; test speeds on a scrap corner. Full-area painter's tape + CA under the bookmark area so the
  slugs stay put (thin brass peels off; not like the stiff tooling board).
- Ring hole: ~4.0 mm (traced, 3.8 x 4.1), ~2 mm of brass round it: a 1.5-2 mm cord singly. Could be made a clean 4.5.
- Finish: sand the bottom burrs on 400/600 on glass, polish (Brasso / Flitz), alcohol, then Incralac / clear lacquer or
  Renaissance Wax; optional black paint in the name before polishing.

## 1. Where things stand

| Thing | State |
|---|---|
| **Sunflower bookmark** | **Next to cut** (Amir). Designed, all checks pass, placed on his brass plate. No toolpaths yet. Section 2. |
| Olive bookmark (`cad/bookmark.py`) | A first capability test with our own olive branch. Works, checks pass, not wanted for cutting. |
| Olive bookmark from Amir's picture | **Dropped** (Amir: "sunflower only"). The picture (`art/olive.png`) has 0.3-1 mm slits: too fine for a 1 mm end mill; a clean redraw was started and abandoned. |
| Hydrangea bookmark (a picture Amir showed, not saved) | Not started. Assessed only: the flowers are a 3D relief (impossible in 0.8 mm brass); a flat version (cut-outs + engraved petal lines) would be no harder than the sunflower. |
| Board, coaster, back map | Unchanged by the desktop session since 2026-10-28, except the wood-buying notes (docs 1, "Wood to buy"). |
| GitHub repo | **Public** (Amir chose to push it public, 2026-11-06). It holds the seller's two bookmark pictures and the teacher's name. Amir may make it private later. |

---

## 2. The sunflower bookmark

### What it is
- Traced from Amir's picture `art/sunflower.png`: a bought brass bookmark (round ends, ring tab on top, a blank name
  band down the left, sunflowers and flowers cut through). **The design is the seller's: for Amir himself (a gift for
  his son's teacher), not for sale.**
- **40.1 x 115.3 x 0.8 mm**, brass. One piece (nothing falls out when cut).
- Inner lines thinned from the picture's ~2.0 mm to **~1.5 mm** (Amir: "a bit thinner"); the outer frame (~3 mm) and
  the name band keep their full width. Every gap is wide enough for a **1 mm end mill**.
- Name: **"Mrs. Poirier"** (Amir's son's teacher), **Edwardian Script** (`C:/Windows/Fonts/ITCEDSCR.TTF`, the closest
  installed font to the script Amir showed), sized to fill the blank band with 1.5 mm round it (font size 9.2, 37 mm
  long), centred on the band, **engraved 0.2 deep**. Its hairlines are very thin: they may engrave faint. A bolder
  script (e.g. the free Google font Great Vibes, closer to Amir's sample) is an option; not downloaded.
- **On Amir's plate, 100 x 150 (x 0.8 assumed)**: the bookmark along the 150 side, **3 mm from the left edge**, centred
  along the length (x 3.0-43.1, y 17.4-132.6). The right **56 x 150** is left for a second try (Amir: "if we fail we
  try" again). Amir also said "try 1mm": read as the second try; if he meant a 1 mm thick plate, change `T`.

### Files (`export/bookmarks/`)
| File | What |
|---|---|
| `sunflower_on_plate.dxf` | **For Makera Studio.** Origin (0,0) = the plate's **front-left corner**. Layers: `plate` (the plate's edge, reference, not cut), `outline` (bookmark outer edge), `cut` (47 cut-outs), `engrave` (the name, filled letter outlines). |
| `sunflower_on_plate.png` | The layout picture. |
| `bookmark_sunflower.dxf` / `.step` / `.stl` | The bookmark alone, centred on 0,0 (STEP / STL with the name engraved). |

### The code
- `cad/bookmark_sunflower.py check export` (run with `C:/Users/leska/cadenv/Scripts/python`, from the repo root).
- How it works: the picture -> a gold / white mask (saturation > 0.35 or dark = brass; the name band rectangle
  `BAND_PX` filled solid so the picture's name is gone) -> clean-up (specks < 0.3 mm2 dropped) -> thinning (`THIN`
  0.25 mm a side, frame and band kept) -> contours (smoothed, simplified to 0.02 mm) -> build123d face -> extrude `T`,
  name cut `TEXT_D` deep. Scale: the picture's width = 40 mm.
- Parameters to change: `T` (plate thickness), `PLATE`, `MARGIN`, `THIN`, `NAME`, `FONT_FILE`, `NAME_MARGIN`, `TEXT_D`.
- The checks (`bookmark.check`, shared with `cad/bookmark.py`): fits the bed; one piece; gaps narrower than the end
  mill (`TOOL_D` 1.0) that would stay uncut; brass thinner than `MIN_W` 1.0 over more than 2.5 mm; plus on the plate:
  inside with the tool's room, and room for another. Last run: **ALL OK**. (Small round leftovers in sharp inside
  corners, under ~1.2 mm2, are fine: the tool's radius.)
- Total path length: cut-outs ~1.22 m, outline ~0.28 m, name ~0.32 m.
- Viewer: `review/serve.py --port=8771`, then http://localhost:8771/review/?model=bookmarks (the bookmark on the
  plate). `?model=bookmark` = the olive capability test.

### Cutting it (a plan, not tried yet)
Before brass: **run the same file in MDF or wood first** (the laptop's coaster notes apply).

**Check first**
1. **Is there a 1 mm (or smaller) flat end mill?** The design needs one: the laptop notes list the set's 1/8"
   (3.175) end mill, which is **far too big** for the bookmark's gaps. Look in the 26-bit Essential set; if it has
   no 1 mm, buy one (single or two flute, for non-ferrous / brass). If only bigger bits: the design would have to be
   scaled up or laser-cut in thin wood instead.
2. **Measure the plate** (thickness: 0.8 assumed; and 100 x 150).
3. Are the bits fine for brass? Makera sells metal (aluminium / brass) bits separately; a wood bit will cut brass slowly
   but dulls faster.

**Holding** (from the laptop's notes): 2 mm MDF spoil board flat on the bed; the plate on **3-4 short strips** of
double-sided tape (tape over the whole bottom held far too hard), or painter's tape + CA. Thin brass must not lift or
buzz: press it flat; keep auto leveling on (the laptop found 0.22 mm out of level over 137 x 91).

**Zero:** XY = the plate's front-left corner (the DXF origin), Z on top of the plate.

**Toolpaths in Makera Studio (2D), in this order:**
| # | Layer | Path | Bit | Depth |
|---|---|---|---|---|
| 1 | `engrave` | 2D Pocket (or engrave along the outline) | engraving bit (fine V) | 0.2 |
| 2 | `cut` | 2D Contour, **inside** | 1 mm flat end mill | 0.8 + ~0.1 into the spoil board |
| 3 | `outline` | 2D Contour, **outside**, with **3-4 tabs** (short, ~0.3 high) | 1 mm flat end mill | 0.8 + ~0.1 |
| - | `plate` | none (reference only) | | |

Brass starting points (no test yet: try in the spare area first): step-down ~0.1 mm (8 passes), slow feed
(~150-250 mm/min), slow plunge, a drop of lubricant (WD-40 / cutting oil), clear chips. Time: about 1.5 m of cutting x
8 passes = ~12 m: **roughly 45-60 min**, plus a few minutes for the name.

**Known Makera Studio issues (from the laptop):** the 2D Chamfer path wrote G-code with no feed ("Alarm: Undefined feed
rate"); Studio has no V-carve path. Neither is used here.

**After:** cut the tabs, file / sand the burrs, polish.

---

## 3. Other things from the desktop session

- **Wood buying** (Amir is in **Cary, NC**, has **no saw**): the cut list and shops are in docs section 1 ("Wood to
  buy"). Local: Capitol City Lumber (Raleigh, 919-832-6492, cuts to size), Woodcraft Raleigh (919-781-1911), Anchor
  Hardwoods, The Hardwood Store of NC (Gibsonville). Online: MakerStock (3/4 walnut only 4-1/2 wide, min 12" = 305 mm:
  too long for a 300 mm bed without a saw), Woodworkers Source (Arizona, ships; custom cuts by quote). Amir was writing
  to Capitol City; nothing confirmed bought. Board halves: 4/4 walnut S2S, **7-3/4 x 11-5/8, no bigger** (300 x 200
  bed).
- **Inlay vs epoxy:** Amir asked about the YouTube method (one plug per colour, hammered in). It is a V-carve inlay;
  explained, epoxy kept (the turquoise look; more forgiving). No change to the board.
- **Epoxy for hot mugs:** most tabletop epoxy softens at 50-60 C; a heat-resistant epoxy for a coaster.
- **Amir writes in English and sometimes asks for Hebrew** (he asked for one explanation in Hebrew).
- `review/serve.py` now serves: `board` (default), `coaster`, `bookmark`, `bookmarks`.
- `requirements.txt` + README "On another computer" section: how to set up the Python env on the laptop.

## 4. Open questions for Amir
1. A 1 mm end mill: does he have one? (Blocks the bookmark.)
2. The plate: 0.8 thick? And did "try 1mm" mean a 1 mm plate?
3. Keep Edwardian Script, or download a bolder script (Great Vibes)?
4. Make the GitHub repo private?
