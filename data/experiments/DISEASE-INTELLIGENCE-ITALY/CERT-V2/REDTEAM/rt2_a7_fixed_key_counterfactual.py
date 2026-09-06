#!/usr/bin/env python3
"""RT2-A7 — what changes if the denominator is joined on (season, id_survey) instead of id_survey.

Monkey-patches ENGINE/current_pressure.denominator_guard IN MEMORY ONLY (nothing on disk is
modified) with a version whose key carries the season, then re-runs today's sheet and the
walk-forward hindcast at 6 September of every season, and diffs them against the shipped code.
"""
import json, glob, os, sys, collections, datetime as dt

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "ENGINE"))
sys.path.insert(0, os.path.join(ROOT, "CASES"))
import current_pressure as cp

CASE = os.path.join(ROOT, "CASES", "OLIVO-BACTROCERA-TOSCANA")


def num(v):
    if v in (None, ""):
        return None
    try:
        return float(str(v).replace(",", "."))
    except ValueError:
        return None


def fixed_guard(rows, case_dir, denom_var):
    den = {}
    for fn in glob.glob(os.path.join(case_dir, "RAW", f"*_v{denom_var}_*.json")):
        y = int(os.path.basename(fn)[:-5].split("_")[-1])
        for r in json.load(open(fn, encoding="utf-8")):
            den[(y, str(r["id_survey"]))] = num(r.get("val"))
    kept = [r for r in rows if den.get((r["_d"].year, str(r.get("id_survey"))))]
    return kept, {"dropped_zero_or_unknown_denominator": len(rows) - len(kept),
                  "denominator_var": denom_var, "KEY": "(season, id_survey)"}


if __name__ == "__main__":
    real = cp.denominator_guard
    out = {}
    for tag, guard in (("SHIPPED_KEY_id_survey", real), ("FIXED_KEY_season_id_survey", fixed_guard)):
        cp.denominator_guard = guard
        pre = cp.load_rows(CASE, -1002)
        live = cp.current_pressure(CASE, -1002, dt.date(2026, 9, 6), _pre=pre)
        hind = cp.hindcast(CASE, -1002, 9, 6, range(2006, 2026))
        out[tag] = {"live": {p: v.get("STATE") for p, v in live["PROVINCES"].items()},
                    "vals": {p: v.get("VALUE") for p, v in live["PROVINCES"].items()},
                    "dropped": live["DENOMINATOR_GUARD"]["dropped_zero_or_unknown_denominator"],
                    "hind": {y: dict(v) for y, v in hind.items()}}
    cp.denominator_guard = real

    a, b = out["SHIPPED_KEY_id_survey"], out["FIXED_KEY_season_id_survey"]
    print(f"visits dropped by the guard:  shipped {a['dropped']}   fixed {b['dropped']}")
    print("\ntoday's cells, 2026-09-06")
    print(f"  {'province':14s} {'shipped':22s} {'val':>8s} | {'fixed':22s} {'val':>8s}")
    nd = 0
    for p in a["live"]:
        same = a["live"][p] == b["live"][p] and a["vals"][p] == b["vals"][p]
        nd += not same
        print(f"  {p:14s} {a['live'][p]:22s} {str(a['vals'][p]):>8s} | "
              f"{b['live'][p]:22s} {str(b['vals'][p]):>8s} {'' if same else '  <-- DIFFERS'}")
    print(f"  today's cells that differ: {nd}/{len(a['live'])}")

    diff = [(y, p, a["hind"][y].get(p), b["hind"][y].get(p))
            for y in a["hind"] for p in a["hind"][y]
            if a["hind"][y].get(p) != b["hind"][y].get(p)]
    tot = sum(len(v) for v in a["hind"].values())
    print(f"\nwalk-forward hindcast at 6 September, 2006-2025: {len(diff)}/{tot} cells differ")
    for d in diff:
        print("   ", d)
