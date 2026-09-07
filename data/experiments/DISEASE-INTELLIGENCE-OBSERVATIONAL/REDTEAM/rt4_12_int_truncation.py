#!/usr/bin/env python3
"""RT4-12  Where does int(num) actually reach a PUBLISHED field?

`infested_drupes` is published only for the CURRENT window (baseline entries carry rate_pct and
drupes_sampled, not infested_drupes). So: for each metric, is any CURRENT-window numerator
fractional, and does int() therefore under-report a number a human reads?
"""
import os, sys, json, datetime as dt
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "engine"))
import di_core, di_observe
CASE = os.path.abspath(os.path.join(HERE, "..", "..", "DISEASE-INTELLIGENCE-ITALY",
                                    "CASES", "OLIVO-BACTROCERA-TOSCANA"))
AS_OF = dt.date(2026, 9, 6)
DEN = "SAMPLE_SIZE / DENOMINATOR"
sheet = di_core.load_sheet()
L = di_core.load_visits(CASE, sheet, AS_OF)
visits = L["visits"]
provs = sorted({v["province"] for v in visits if v["province"]})
lo, hi = di_observe._win(AS_OF, di_observe.PARAMS["WINDOW_DAYS"])
rows = []
for m in ("ACTIVE_INFESTATION_COUNT", "DAMAGING_INFESTATION_COUNT",
          "TOTAL_INFESTATION_COUNT"):
    for p in provs:
        r = di_observe.pooled(visits, lo, hi, p, m)
        if not r:
            continue
        num = 0.0
        for v in visits:
            if v["province"] != p or not v["usable_for_rates"]:
                continue
            d = dt.date.fromisoformat(v["observation_date"])
            if not (lo <= d <= hi):
                continue
            c = v["measurements"][m]["value"]; t = v["measurements"][DEN]["value"]
            if c is None or t is None:
                continue
            num += c
        rows.append({"metric": m, "province": p, "float_numerator": repr(num),
                     "published_infested_drupes": r["infested_drupes"],
                     "is_fractional": num != int(num),
                     "lost_by_truncation": round(num - int(num), 12),
                     "published_rate_pct": r["rate_pct"]})
frac = [x for x in rows if x["is_fractional"]]
out = {"current_window": [lo.isoformat(), hi.isoformat()],
       "province_metric_cells_scored": len(rows),
       "cells_whose_published_infested_drupes_is_a_TRUNCATED_fraction": len(frac),
       "detail": frac,
       "MEANING": ("no published infested_drupes count in the current window is truncated at "
                   "this as_of: int() and round() agree on all of them"
                   if not frac else
                   "int() under-reports a published count a human reads")}
print(json.dumps(out, indent=1, default=str))
json.dump(out, open(os.path.join(HERE, "rt4_12_int_truncation.json"), "w",
                    encoding="utf-8"), indent=1, default=str)
