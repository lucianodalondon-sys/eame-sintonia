#!/usr/bin/env python3
"""Cell-for-cell equality between the red team's transcription (rt_cells.json) and the
certification's own sweep (p4_cell_state_by_date.json). If this does not print
MISMATCHES 0 on every field, every number in the report below is worthless."""
import json, os

HERE = os.path.dirname(os.path.abspath(__file__))
CERT = os.path.dirname(HERE)

mine = {(c["CROP"], c["DATE"], c["PROVINCE"]): c
        for c in json.load(open(os.path.join(HERE, "rt_cells.json")))["CELLS"]}
theirs = {(r["CROP"], r["DATE"], r["PROVINCE"]): r
          for r in json.load(open(os.path.join(CERT, "p4_cell_state_by_date.json")))["ROWS"]}

print("keys mine/theirs:", len(mine), len(theirs), "same set:", set(mine) == set(theirs))
bad = {"STATE": 0, "STATE_NO_FLOOR": 0, "VALUE": 0, "PERCENTILE": 0,
       "BASELINE_N": 0, "n_sites": 0, "n_visits": 0, "BASELINE_MEDIAN": 0}
examples = []
for k in theirs:
    a, b = mine[k], theirs[k]
    pairs = [("STATE", a.get("STATE"), b.get("STATE")),
             ("STATE_NO_FLOOR", a.get("STATE_NO_FLOOR"), b.get("STATE_WITHOUT_FLOOR")),
             ("VALUE", a.get("VALUE"), b.get("VALUE")),
             ("PERCENTILE", a.get("PERCENTILE"), b.get("PERCENTILE")),
             ("BASELINE_N", a.get("BASELINE_N"), b.get("BASELINE_N")),
             ("n_sites", a.get("n_sites"), b.get("n_sites")),
             ("n_visits", a.get("n_visits"), b.get("n_visits")),
             ("BASELINE_MEDIAN", a.get("BASELINE_MEDIAN"), b.get("BASELINE_MEDIAN"))]
    for name, x, y in pairs:
        if x != y:
            bad[name] += 1
            if len(examples) < 8:
                examples.append((k, name, x, y))
print("MISMATCHES", bad)
for e in examples:
    print("  ", e)

# the integer positive-site count vs the certification's rounded product
diff = [(k, mine[k]["n_pos"], theirs[k]["n_positive_sites"]) for k in theirs
        if theirs[k]["n_positive_sites"] is not None
        and mine[k]["n_pos"] != round(theirs[k]["n_positive_sites"])]
print("n_positive_sites disagreeing with the true integer count:", len(diff))
for d in diff[:10]:
    print("  ", d)
