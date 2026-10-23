# BattleTech Roster

A browser app for running BattleTech games: a roster for each house, a damage record sheet for every 'Mech,
movement, weapon fire with GATOR to-hit numbers, physical attacks, heat, and a War Chest between battles.

**Use it online:** https://beatfreak80.github.io/battletech-roster/

Games are saved in your own browser. Use **Save** to keep named games, or download a game file to move it to
another device.

## Building

`index.html` is built from `template.html` and the `data_*.json` drawing data:

```
python build.py
```

`build.py` also simplifies each drawing's line art (`simplify_art.py`) as it goes; the data files keep the original.

Each chassis folder holds its record-sheet drawing and the scripts that turn it into location shapes
(`render.py`, `seg.py`, `make_data.py`). To add a 'Mech from its SVG drawing, see
[ADDING-A-MECH.md](ADDING-A-MECH.md).

## Disclaimer

Unofficial fan project, free and non-commercial. BattleTech, 'Mech names and artwork are trademarks and
copyright of their respective owners (Catalyst Game Labs / The Topps Company). Not affiliated with or endorsed by them.
