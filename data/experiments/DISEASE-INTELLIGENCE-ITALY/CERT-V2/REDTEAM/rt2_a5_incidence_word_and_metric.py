#!/usr/bin/env python3
"""RT2-A5 — the word INCIDENCE, and the magnitude the engine throws away.

The source measures a FRUIT-level rate: var -1002 is the damaging-infestation reading on a
destructive sample whose size is declared in var 1 ("Olive campionate", 100 in 92.6% of visits).
That is an incidence in the agronomic sense: affected units / units examined.

The engine discards the magnitude and computes
      INCIDENCE = share of monitored SITES whose maximum reading in the window exceeds 0
and publishes it under METRIC = "INCIDENCE". The unit of the denominator changed from FRUIT to
SITE, and the word did not.

This script prints today's sheet, then re-runs the identical engine with metric="SEVERITY"
(the mean of the site-max readings, i.e. the source's own magnitude) so the cost of discarding
the magnitude is a table of classes.
"""
import json, os, sys, collections, datetime as dt

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "ENGINE"))
sys.path.insert(0, os.path.join(ROOT, "CASES"))
import current_pressure as cp
from answer_sheet import answer_sheet

CASE = os.path.join(ROOT, "CASES", "OLIVO-BACTROCERA-TOSCANA")
ASOF = dt.date(2026, 9, 6)

if __name__ == "__main__":
    a = answer_sheet(CASE, -1002, ASOF, "damaging olive-fly infestation", "olive", "Toscana")
    print("THE SHEET AS PUBLISHED TODAY")
    print("  1 WHAT HAPPENED :", a["1_WHAT_HAPPENED"]["STATEMENT"])
    print("  3 HOW MUCH units:",
          next(iter(a["3_HOW_MUCH"].values()))["UNITS"] if a["3_HOW_MUCH"] else "-")
    print("  METRIC key emitted by the engine:",
          cp.current_pressure(CASE, -1002, ASOF)["METRIC"])

    print("\nSAME ENGINE, SAME DAY, the source's own magnitude instead of the binary")
    print(f"  {'province':14s} {'INCIDENCE class':22s} {'val':>8s} | "
          f"{'SEVERITY class':22s} {'val (mean % of drupes)':>22s} {'baseline median':>16s}")
    ri = cp.current_pressure(CASE, -1002, ASOF, "INCIDENCE")
    rs = cp.current_pressure(CASE, -1002, ASOF, "SEVERITY")
    diff = 0
    for p in ri["PROVINCES"]:
        i, s = ri["PROVINCES"][p], rs["PROVINCES"][p]
        diff += i.get("STATE") != s.get("STATE")
        print(f"  {p:14s} {i.get('STATE',''):22s} {str(i.get('VALUE')):>8s} | "
              f"{s.get('STATE',''):22s} {str(s.get('VALUE')):>22s} "
              f"{str(s.get('BASELINE_MEDIAN')):>16s}")
    print(f"  provinces whose class changes when the magnitude is kept: {diff}/"
          f"{len(ri['PROVINCES'])}")

    print("\nWHAT THE SOURCE'S OWN LEGEND SAYS ABOUT THOSE SEVERITY NUMBERS")
    print("  0 Nessuna Infestazione | 0.01-6 green | 6-10 yellow | >=10 RED")
    for p, s in rs["PROVINCES"].items():
        v = s.get("VALUE")
        if v is None:
            continue
        band = ("NESSUNA" if v == 0 else "GREEN" if v < 6 else "YELLOW" if v < 10 else "RED")
        bm = s.get("BASELINE_MEDIAN")
        bband = ("-" if bm is None else "NESSUNA" if bm == 0 else "GREEN" if bm < 6
                 else "YELLOW" if bm < 10 else "RED")
        print(f"  {p:14s} today {v:6.3f} -> {band:8s}   usual {str(bm):>7s} -> {bband}")
