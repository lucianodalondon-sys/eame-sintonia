#!/usr/bin/env python3
"""RT5 · accusation 6. The two silencing gates, swept together.

MIN_PANEL_OVERLAP_FOR_LIKE_FOR_LIKE = 8 and MIN_BASELINE_SEASONS = 5 between them
leave seven of ten provinces with no historical class. This is the full 2-D
trade-off surface: how many provinces speak, how many say BELOW / ABOVE / TYPICAL,
at every combination."""
import os, sys, json, datetime as dt
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import rt5_lib as L

AS_OF = dt.date(2026, 9, 6)
idx, raw = L.get_index("ACTIVE_INFESTATION_COUNT")
OV = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 12, 15, 20, 25]
SE = [1, 2, 3, 4, 5, 6, 8, 10, 12, 15]

grid = {}
print("rows = MIN_PANEL_OVERLAP, cols = MIN_BASELINE_SEASONS; cell = provinces speaking "
      "(of 10), and of those how many BELOW")
print(f"{'ov\\seas':>8} " + " ".join(f"{s:>8}" for s in SE))
for ov in OV:
    line = []
    for se in SE:
        P = dict(L.PARAMS)
        P["MIN_PANEL_OVERLAP_FOR_LIKE_FOR_LIKE"] = ov
        P["MIN_BASELINE_SEASONS"] = se
        cells = L.all_cells(idx, AS_OF, P=P)
        h = {c["province"]: c["historical_state"] for c in cells}
        sp = sum(1 for p in h if h[p] != "INSUFFICIENT_DATA")
        bl = sum(1 for p in h if h[p] == "BELOW_HISTORICAL")
        ab = sum(1 for p in h if h[p] == "ABOVE_HISTORICAL")
        ty = sum(1 for p in h if h[p] == "TYPICAL")
        grid[f"{ov}|{se}"] = {"speaking": sp, "below": bl, "above": ab, "typical": ty,
                              "hist": h,
                              "median_shared_groves_used": None}
        line.append(f"{sp:>2}/{bl:<2}{'*' if (ov, se) == (8, 5) else ' '}   ")
    print(f"{ov:>8} " + " ".join(f"{x:>8}" for x in line))

print("\n* = the declared configuration")
print("\nPROVINCES SPEAKING at each overlap, with MIN_BASELINE_SEASONS held at 5:")
for ov in OV:
    P = dict(L.PARAMS)
    P["MIN_PANEL_OVERLAP_FOR_LIKE_FOR_LIKE"] = ov
    cells = L.all_cells(idx, AS_OF, P=P)
    speak = [(c["province"], c["historical_state"], c.get("n_lower"), c.get("n_matched"))
             for c in cells if c["historical_state"] != "INSUFFICIENT_DATA"]
    print(f"  overlap {ov:>2}: {len(speak)} speak  " +
          "; ".join(f"{p} {s[0]}{s[1]} {a}/{b}" for p, s, a, b in speak))

# how much grove overlap actually exists
print("\nHOW MUCH PANEL OVERLAP EXISTS AT ALL (this window vs each prior season)")
lo, hi = L.win(AS_OF, L.PARAMS["WINDOW_DAYS"])
ovl = {}
for prov in idx.provinces:
    cur = idx.pooled(prov, lo, hi, as_of=AS_OF)
    if not cur:
        continue
    xs = []
    for y in range(2006, 2026):
        b = idx.pooled(prov, L.shift(lo, y), L.shift(hi, y), as_of=AS_OF)
        if b:
            xs.append((y, len(cur["sites"] & b["sites"]), len(b["sites"])))
    ovl[prov] = {"n_groves_now": cur["n_sites"], "per_season": xs,
                 "max_shared": max(x[1] for x in xs) if xs else 0}
    print(f"  {prov:15s} groves now {cur['n_sites']:>4}  shared with prior seasons: " +
          " ".join(f"{y}:{s}" for y, s, _ in xs))

json.dump({"grid": grid, "overlap_field": ovl},
          open(os.path.join(HERE, "rt5_06_gates.json"), "w"), indent=1)
print("\nwrote rt5_06_gates.json")
