#!/usr/bin/env python3
"""Run the observational pilot for one AS_OF and print every province cell."""
import os, sys, json, datetime as dt
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import di_core, di_observe
HERE = os.path.dirname(os.path.abspath(__file__))
CASE = os.path.abspath(os.path.join(HERE, "..", "..", "DISEASE-INTELLIGENCE-ITALY",
                                    "CASES", "OLIVO-BACTROCERA-TOSCANA"))
METRIC = sys.argv[2] if len(sys.argv) > 2 else "ACTIVE_INFESTATION_COUNT"
as_of = dt.date.fromisoformat(sys.argv[1]) if len(sys.argv) > 1 else dt.date(2026, 9, 6)
sheet = di_core.load_sheet()
loaded = di_core.load_visits(CASE, sheet, as_of)
provs = sorted({v["province"] for v in loaded["visits"] if v["province"]})
cells = [di_observe.cell(loaded["visits"], sheet, p, METRIC, as_of) for p in provs]
print(f"AS_OF {as_of}   metric {METRIC}   visits {loaded['n_visits']:,} "
      f"(usable {loaded['n_visits_usable_for_rates']:,})")
print(f"{'province':15s} {'rate%':>7} {'band':>22} {'n_vis':>6} {'sites':>6} {'drupes':>8} "
      f"{'hist':>18} {'base_med%':>9} {'trend':>20} {'pub':>5} {'matched':>7}")
for c in cells:
    o, a, q = c["observation"], c["analysis"], c["quality"]
    print(f"{c['province']:15s} {str(o.get('value_pct')):>7} "
          f"{str((o.get('source_band') or {}).get('label')):>22} "
          f"{o.get('n_visits',0):>6} {o.get('n_sites',0):>6} {o.get('drupes_sampled',0):>8} "
          f"{a['historical_state']:>18} {str(a.get('baseline_rate_pct_median')):>9} "
          f"{a['observed_trend']:>20} {str(q['publishable']):>5} "
          f"{a['matched_panel_seasons']:>7}")
out = {"loaded": {k: v for k, v in loaded.items() if k != "visits"}, "cells": cells}
json.dump(out, open(os.path.join(HERE, os.path.join("..","OUT",f"pilot_{METRIC}_{as_of}.json")), "w",
                    encoding="utf-8"), indent=1, default=str)
