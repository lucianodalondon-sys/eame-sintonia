#!/usr/bin/env python3
"""RT3-E2. The baseline window is built with _shift_year on BOTH ends independently.
When the current window crosses 31 Dec, lo.year != hi.year, and shifting both to the same
prior year y produces lo > hi -- an EMPTY interval that can never match a row.

This script proves the arithmetic, then measures how reachable it is in the real archives.
Read-only: it imports the shipped engine and never writes to ENGINE/ or CASES/.
"""
import sys, os, json, glob, datetime as dt, collections

ENG = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "ENGINE")
CAS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "CASES")
sys.path.insert(0, os.path.abspath(ENG))
import current_pressure as cp

OUT = {}

# ---------------------------------------------------------------- 1. pure arithmetic
arith = []
for as_of in [dt.date(2026, 1, 1), dt.date(2026, 1, 15), dt.date(2026, 1, 28),
              dt.date(2026, 2, 1), dt.date(2025, 12, 31), dt.date(2026, 3, 27),
              dt.date(2024, 2, 29), dt.date(2024, 3, 27), dt.date(2023, 3, 1)]:
    hi, lo = as_of, as_of - dt.timedelta(days=cp.WINDOW_DAYS - 1)
    y = as_of.year - 1
    blo, bhi = cp._shift_year(lo, y), cp._shift_year(hi, y)
    arith.append({
        "AS_OF": as_of.isoformat(),
        "CURRENT_WINDOW": [lo.isoformat(), hi.isoformat()],
        "CURRENT_WINDOW_DAYS": (hi - lo).days + 1,
        "BASELINE_WINDOW_y_minus_1": [blo.isoformat(), bhi.isoformat()],
        "BASELINE_WINDOW_DAYS": (bhi - blo).days + 1,
        "BASELINE_IS_EMPTY_INTERVAL": blo > bhi,
        "CROSSES_YEAR_BOUNDARY": lo.year != hi.year,
    })
OUT["ARITHMETIC"] = arith

# ---------------------------------------------------------------- 2. month coverage of archives
cases = [("OLIVO-BACTROCERA-TOSCANA", -1002), ("VITE-OIDIO-TOSCANA", 39),
         ("FRUMENTO-SEPTORIA-TOSCANA", 372)]
cover = {}
for cname, var in cases:
    d = os.path.join(CAS, cname)
    rows, scale, meta = cp.load_rows(d, var)
    months = collections.Counter(r["_d"].month for r in rows)
    readable = collections.Counter(r["_d"].month for r in rows
                                   if cp.read_value(r, scale, meta["VALUE_MODE"]) is not None)
    cover[cname] = {
        "VALUE_MODE": meta["VALUE_MODE"],
        "TOTAL_ROWS": len(rows),
        "ROWS_BY_MONTH": {str(m): months.get(m, 0) for m in range(1, 13)},
        "READABLE_ROWS_BY_MONTH": {str(m): readable.get(m, 0) for m in range(1, 13)},
        "ROWS_IN_DEC_OR_JAN": months.get(12, 0) + months.get(1, 0),
        "ROWS_ON_FEB_29": sum(1 for r in rows if r["_d"].month == 2 and r["_d"].day == 29),
    }
OUT["ARCHIVE_MONTH_COVERAGE"] = cover

# ------------------------------------------------- 3. live effect: run the engine on 1 Jan etc.
live = {}
for cname, var in cases[:2]:
    d = os.path.join(CAS, cname)
    pre = cp.load_rows(d, var)
    per_date = {}
    for as_of in [dt.date(2026, 1, 15), dt.date(2025, 12, 20), dt.date(2025, 7, 15),
                  dt.date(2024, 2, 29), dt.date(2024, 3, 20)]:
        try:
            r = cp.current_pressure(d, var, as_of, _pre=pre)
            st = collections.Counter(v["STATE"] for v in r["PROVINCES"].values())
            per_date[as_of.isoformat()] = {
                "WINDOW": r["WINDOW"],
                "STATES": dict(st),
                "BASELINE_N_BY_PROV": {p: v.get("BASELINE_N") for p, v in r["PROVINCES"].items()},
                "N_PROV_WITH_A_CLASS": sum(
                    1 for v in r["PROVINCES"].values()
                    if v["STATE"] in (cp.HIGHER, cp.TYPICAL, cp.LOWER)),
                "N_PROV_TOTAL": len(r["PROVINCES"]),
            }
        except Exception as e:
            per_date[as_of.isoformat()] = {"RAISED": f"{type(e).__name__}: {e}"}
    live[cname] = per_date
OUT["LIVE_RUNS"] = live

# ------------------------- 4. counterfactual: what a year-boundary-correct baseline would give
# Rebuild the SAME as_of but shifting the whole window as an interval (lo keeps its own offset
# from hi) instead of shifting each endpoint into the same calendar year.
def correct_baseline_window(lo, hi, y):
    """Shift hi into year y, keep the window length. This is what 'same calendar window' means."""
    bhi = cp._shift_year(hi, y)
    return bhi - dt.timedelta(days=(hi - lo).days), bhi

cf = {}
for cname, var in cases[:2]:
    d = os.path.join(CAS, cname)
    pre = cp.load_rows(d, var)
    rows, scale, meta = pre
    mode = meta["VALUE_MODE"]
    by_prov = collections.defaultdict(list)
    for r in rows:
        if r.get("nome_area"):
            by_prov[r["nome_area"]].append(r)
    per_date = {}
    for as_of in [dt.date(2026, 1, 15), dt.date(2025, 12, 20)]:
        hi, lo = as_of, as_of - dt.timedelta(days=cp.WINDOW_DAYS - 1)
        shipped_n, correct_n = {}, {}
        for prov, prows in sorted(by_prov.items()):
            cur = cp._window_value(prows, scale, lo, hi, mode)
            if cur is None or cur["n_sites"] < cp.MIN_SITES:
                continue
            sb, cb = [], []
            for y in sorted({r["_d"].year for r in prows}):
                if y >= as_of.year:
                    continue
                b1 = cp._window_value(prows, scale, cp._shift_year(lo, y), cp._shift_year(hi, y), mode)
                if b1 and b1["n_sites"] >= cp.MIN_SITES:
                    sb.append(y)
                blo, bhi = correct_baseline_window(lo, hi, y)
                b2 = cp._window_value(prows, scale, blo, bhi, mode)
                if b2 and b2["n_sites"] >= cp.MIN_SITES:
                    cb.append(y)
            shipped_n[prov], correct_n[prov] = len(sb), len(cb)
        per_date[as_of.isoformat()] = {
            "PROV_WITH_ENOUGH_CURRENT_SITES": len(shipped_n),
            "SHIPPED_BASELINE_N": shipped_n,
            "INTERVAL_SHIFT_BASELINE_N": correct_n,
            "PROV_PUBLISHABLE_SHIPPED": sum(1 for v in shipped_n.values() if v >= cp.MIN_BASE),
            "PROV_PUBLISHABLE_IF_FIXED": sum(1 for v in correct_n.values() if v >= cp.MIN_BASE),
        }
    cf[cname] = per_date
OUT["COUNTERFACTUAL_INTERVAL_SHIFT"] = cf

here = os.path.dirname(os.path.abspath(__file__))
json.dump(OUT, open(os.path.join(here, "rt3_e2_year_boundary.json"), "w"), indent=1)
print(json.dumps(OUT, indent=1)[:7000])
