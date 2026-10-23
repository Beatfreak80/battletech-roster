# Adding a 'Mech

How a 'Mech's SVG line drawing becomes a record sheet in the app. Every 'Mech in the app went through these steps,
so a new drawing processed the same way will look and behave like the rest.

```
<Mech>.svg ──render.py──▶ PNG ──seg.py──▶ hit locations ──make_data.py──▶ data_xxx.json
                                                                              │
          template.html  (+ CHASSIS, UNITS, ROSTER entries) ◀──────────────────┘
                   │
                   └──build.py──▶ index.html   (line art simplified at this step)
```

## 1. The SVG

What the scripts expect from a drawing:

- **A 1920 × 1080 canvas** (`viewBox="0 0 1920 1080"`), the 'Mech seen straight from the front, black lines on white.
  All the existing drawings share the same scale, so a new one drawn at the same scale sits well beside them.
- **Lines as `<polyline points="…">` elements.** Nothing else is read (step 2 covers converting anything else).
- **Line thickness 4** (`stroke-width:4` in each line's style). The newer drawings use 4 and the older ones 6.
  Either works, as long as steps 3 and 4 use the same number.

## 2. Copy the drawing into a chassis folder

Make a folder here named after the 'Mech (for example `locust/`) and copy the SVG into it.

The scripts read only `<polyline points="…">` elements, in the SVG's 1920 × 1080 coordinates. Check the file first:

- **Lines with a `transform="…"`** must be baked into plain coordinates. See `cicada/prep.py`.
- **`<path>` elements** (circles, say, like the Catapult's missile tubes) must be turned into polylines. See
  `catapult/prep.py`.

```
grep -c "transform=" locust/Locust.svg      # want 0
grep -c "<path" locust/Locust.svg           # want 0
```

## 3. Render and mark the hit locations

**`render.py`** draws the polylines into a 1920 × 1080 PNG with 6 px lines, and prints the drawing's bounding box.
If the art uses 4 px lines, also keep **`render4.py`**, the same with 4 px lines. Copy both from `locust/` and
change the file names.

**`seg.py`** works out which pixels belong to which of the eight locations (HD, CT, RT, LT, RA, LA, RL, LL). Copy
`locust/seg.py` and edit:

1. **`P`**: a rough polygon for each location, in the 1920 × 1080 coordinates. Use the bounding box from
   `render.py`, and look at the PNG to place the edges. The polygons only need to be roughly right. Each area
   enclosed by lines is given to whichever location covers at least 85% of it, so the colours follow the drawing's
   own lines. Only areas that straddle two polygons get split along the polygon edge.
2. **`draw`**: the order the polygons are painted in. Later ones overwrite earlier ones, which is handy for a head
   or centre torso inside a bigger shape.
3. **Enclosed background**: gaps fully surrounded by lines (between an arm and the torso, say) would be coloured
   like armour. List a point inside each one in the `for x,y in [...]:border.add(lab[y,x])` line.

Rules every 'Mech follows:

- **The 'Mech's right is the image's left**, as on the record sheet.
- **The torsos stop at the waist.** The waist band itself is torso.
- **Everything below the waist, pelvis and crotch included, is split down the middle** between RL and LL. No
  centre-torso colour should show between the legs.

Run it from inside the chassis folder:

```
cd locust
python render.py
python render4.py      # only for 4 px art
python seg.py          # writes full.npy, order.json and preview.png
```

Open **`preview.png`**: each location is a different colour. Adjust `P` and run `seg.py` again until the borders are
where you want them.

## 4. Build the drawing data

Copy `locust/make_data.py`, then change the paths, the output file name and the **box**. The box is the area kept,
`(left, top, right, bottom)` in 1920 × 1080 coordinates: the bounding box from `render.py` with a little margin.
Keep `grow=2` (it overlaps neighbouring areas by 2 px so no seam shows where two locations meet without a line
between them). Keep `d['sw']=4` for 4 px art, and remove it for 6 px art.

Run it from the ChaosApp folder:

```
python locust/make_data.py      # writes data_lct.json
```

`data_xxx.json` holds the line art, one mask per location, the tap map and where each location's label sits. It's
the original line art: the simplifying happens later, in `build.py`.

## 5. Add the 'Mech to the app

All in `template.html`:

1. **A `CHASSIS` entry**, filled in from the record sheet PDF. Copy a similar 'Mech's entry. It holds name, model,
   tons, BV, walk and jump MP, heat sinks, armour (front, and rear for torsos), structure, every critical slot
   (`S(name, group)`, with `leg()` and `rep()` helpers), weapons and ammo bins, and `data:__DATA_XXX__`. A weapon's
   `g` must match its crit slots' group, and each ammo bin's key must match its slots' group. Add `drawTons` only if
   the roster thumbnail looks too small (tall aerials, say).
2. **A `UNITS` entry**: a unit id (two letters and a number, such as `lc1`), its chassis and a storage key
   (`unit-lc1`).
3. **A `ROSTER` entry**: add `{unit:'lc1'}` to the house's list.

Then add `('__DATA_XXX__','data_xxx.json')` to the list in **`build.py`**.

## 6. Build and check

```
python build.py
node --check chk.js
```

`build.py` runs every drawing through **`simplify_art.py`**. That joins lines that meet end to end, drops points
that don't change the shape, drops tiny pieces already covered by other lines, and writes the art as one compact
path. It makes the drawings about 10× smaller with no visible change. The `data_*.json` files are never changed.

To check a new drawing came through cleanly:

```
python compare_art.py data_lct.json
```

This renders the original and the simplified drawing in Chrome. It prints how much ink moved (under about 1% is
invisible), and writes `art-compare/lct.png`: original, simplified and the difference. Look at the picture anyway.
It needs Playwright (`pip install playwright`) and Google Chrome.

Finally, open `index.html` and look at the 'Mech: the roster card, the record sheet, and a tap on each location.
