#!/usr/bin/env python3
"""
RED TEAM / CORE HARNESS.

Rebuilds the CERT-V2 step-4 sweep (3 crops x 30 dates x provinces) but keeps, for every
emitted cell, the things the shipped output THROWS AWAY and that every attack below needs:

  - the full baseline vector (year, INCIDENCE, n_sites, integer positive-site count)
  - the exact decomposition of the percentile: n_below, n_equal, n_above
  - the integer number of positive sites in the current window (not the rounded product)

Nothing under ENGINE/ or CASES/ is modified. The window/summary/percentile arithmetic below
is a transcription of ENGINE/current_pressure.py (_window_value + the baseline loop), verified
row-for-row against the shipped function in rt_verify.py.

Out: REDTEAM/rt_cells.json
"""
import json, os, sys, glob, datetime as dt, collections
from statistics import mean

HERE = os.path.dirname(os.path.abspath(__file__))
CERT = os.path.dirname(HERE)
ROOT = os.path.dirname(CERT)
sys.path.insert(0, os.path.join(ROOT, "ENGINE"))
sys.path.insert(0, os.path.join(ROOT, "CASES"))
import current_pressure as cp

CASES = [("TOSCANA", "OLIVE", "BACTROCERA_OLEAE_DAMAGING",
          os.path.join(ROOT, "CASES", "OLIVO-BACTROCERA-TOSCANA"), -1002),
         ("TOSCANA", "VINE", "OIDIO_LEAF",
          os.path.join(ROOT, "CASES", "VITE-OIDIO-TOSCANA"), 39),
         ("TOSCANA", "WHEAT", "SEPTORIA",
          os.path.join(ROOT, "CASES", "FRUMENTO-SEPTORIA-TOSCANA"), 372)]

DATES_2026 = [dt.date(2026, m, d) for m, d in
              [(3, 15), (4, 15), (5, 15), (6, 1), (6, 15), (7, 1), (7, 15),
               (8, 1), (8, 15), (9, 1), (9, 6)]]
SAME_DAY_PRIOR = [dt.date(y, 9, 6) for y in range(2007, 2026)]
ALL_DATES = DATES_2026 + SAME_DAY_PRIOR


def window_value(rows, scale, lo, hi, mode):
    """cp._window_value, plus the integer positive-site count it discards."""
    sites = collections.defaultdict(list)
    n_visits = 0
    for r in rows:
        if not (lo <= r["_d"] <= hi):
            continue
        v = cp.read_value(r, scale, mode)
        if v is None:
            continue
        sites[r["id_field"]].append(v)
        n_visits += 1
    if not sites:
        return None
    vals = [max(v) for v in sites.values()]
    pos = sum(1 for v in vals if v > 0)
    return {"n_sites": len(vals), "n_visits": n_visits, "n_pos": pos,
            "INCIDENCE": round(pos / len(vals), 4),
            "INCIDENCE_RAW": pos / len(vals),
            "SEVERITY": round(mean(vals), 4)}


def load_case(case_dir, var_id):
    rows, scale, meta = cp.load_rows(case_dir, var_id)
    idx = json.load(open(os.path.join(case_dir, "collection_index.json")))
    denom_var = idx.get("DENOMINATOR_VAR")
    if denom_var is not None:
        rows, _ = cp.denominator_guard(rows, case_dir, denom_var)
    return rows, scale, meta["VALUE_MODE"]


def cells_for_date(rows, scale, mode, as_of, min_sites=cp.MIN_SITES):
    hi, lo = as_of, as_of - dt.timedelta(days=cp.WINDOW_DAYS - 1)
    by_prov = collections.defaultdict(list)
    for r in rows:
        p = r.get("nome_area")
        if p:
            by_prov[p].append(r)
    out = []
    for prov, prows in sorted(by_prov.items()):
        cur = window_value(prows, scale, lo, hi, mode)
        years = sorted({r["_d"].year for r in prows})
        # every season present, prior AND later, so the permutation null has the full set
        allseason = []
        for y in years:
            b = window_value(prows, scale, cp._shift_year(lo, y), cp._shift_year(hi, y), mode)
            if b:
                allseason.append({"year": y, "INCIDENCE": b["INCIDENCE"], "n_sites": b["n_sites"],
                                  "n_pos": b["n_pos"], "n_visits": b["n_visits"],
                                  "usable": b["n_sites"] >= min_sites})
        prior = [s for s in allseason if s["year"] < as_of.year and s["usable"]]
        rec = {"PROVINCE": prov, "DATE": as_of.isoformat(),
               "n_sites": (cur or {}).get("n_sites", 0),
               "n_visits": (cur or {}).get("n_visits", 0),
               "n_pos": (cur or {}).get("n_pos", 0),
               "VALUE": (cur or {}).get("INCIDENCE"),
               "SEASONS_ALL": allseason, "BASELINE_PRIOR_USABLE": prior}
        if cur is None or cur["n_sites"] < min_sites:
            rec["STATE"] = cp.UNKNOWN_NO_DATA
            rec["STATE_NO_FLOOR"] = cp.UNKNOWN_NO_DATA
            out.append(rec)
            continue
        v = cur["INCIDENCE"]
        n = len(prior)
        rec["BASELINE_N"] = n
        if n < cp.MIN_BASE:
            rec["STATE"] = cp.UNKNOWN_NO_BASELINE
            rec["STATE_NO_FLOOR"] = cp.UNKNOWN_NO_BASELINE
            out.append(rec)
            continue
        below = sum(1 for s in prior if s["INCIDENCE"] < v)
        equal = sum(1 for s in prior if s["INCIDENCE"] == v)
        above = n - below - equal
        p = (below + 0.5 * equal) / n
        rec.update({"N_BELOW": below, "N_EQUAL": equal, "N_ABOVE": above,
                    "PERCENTILE": round(p, 4),
                    "PERCENTILE_STRICT_ONLY": round(below / n, 4),
                    "BASELINE_MEDIAN": round(sorted(s["INCIDENCE"] for s in prior)[n // 2], 4),
                    "BASELINE_ALL_ZERO": all(s["INCIDENCE"] == 0 for s in prior),
                    "BASELINE_ZEROS": sum(1 for s in prior if s["INCIDENCE"] == 0)})
        st = cp.HIGHER if p >= cp.HIGH_P else (cp.LOWER if p <= cp.LOW_P else cp.TYPICAL)
        rec["STATE_NO_FLOOR"] = st
        if st == cp.HIGHER and (cur["n_sites"] * v) < cp.MIN_POSITIVE_SITES:
            st = cp.TYPICAL
            rec["WITHHELD_BY_FLOOR"] = True
        rec["STATE"] = st
        rec["FLOOR_PRODUCT"] = round(cur["n_sites"] * v, 6)
        out.append(rec)
    return out


def main():
    all_cells = []
    for region, crop, issue, case, var in CASES:
        rows, scale, mode = load_case(case, var)
        print(f"  loaded {crop}: {len(rows)} rows mode={mode}", flush=True)
        for as_of in ALL_DATES:
            for c in cells_for_date(rows, scale, mode, as_of):
                c.update({"REGION": region, "CROP": crop, "ISSUE": issue})
                all_cells.append(c)
        print(f"  {crop} done: {len(all_cells)} cells so far", flush=True)
    json.dump({"N_CELLS": len(all_cells), "CELLS": all_cells},
              open(os.path.join(HERE, "rt_cells.json"), "w"), indent=1, default=str)
    c = collections.Counter(x["STATE"] for x in all_cells)
    print("STATE:", dict(c))
    c = collections.Counter(x["STATE_NO_FLOOR"] for x in all_cells)
    print("STATE_NO_FLOOR:", dict(c))


if __name__ == "__main__":
    main()
