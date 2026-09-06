#!/usr/bin/env python3
"""RT3-E4. Does any baseline for season Y contain an observation dated year >= Y?

Method: wrap current_pressure._window_value so every call records (lo, hi) and the set of
calendar years of the rows it actually CONSUMED (rows that passed the date filter AND had a
readable value, i.e. rows that reached `sites`). Then drive hindcast() over every season and
check, for each current-season run at as_of year Y, that no window other than the current one
consumed a row dated >= Y, and that the current window consumed nothing dated > as_of.

Also audits the metadata channel: the code table and the survey-var table used to decode
season Y are the ones collected TODAY, which is a different kind of look-ahead.
"""
import sys, os, json, datetime as dt, collections

HERE = os.path.dirname(os.path.abspath(__file__))
ENG = os.path.abspath(os.path.join(HERE, "..", "..", "ENGINE"))
CAS = os.path.abspath(os.path.join(HERE, "..", "..", "CASES"))
sys.path.insert(0, ENG)
import current_pressure as cp

ORIG = cp._window_value
CALLS = []


def spy(rows, scale, lo, hi, mode="ORDINAL"):
    consumed_years, consumed_dates = set(), []
    for r in rows:
        if not (lo <= r["_d"] <= hi):
            continue
        if cp.read_value(r, scale, mode) is None:
            continue
        consumed_years.add(r["_d"].year)
        consumed_dates.append(r["_d"])
    CALLS.append({"lo": lo, "hi": hi, "years": consumed_years,
                  "max_date": max(consumed_dates) if consumed_dates else None,
                  "n": len(consumed_dates)})
    return ORIG(rows, scale, lo, hi, mode)


OUT = {}
CASES = [("OLIVO-BACTROCERA-TOSCANA", -1002), ("VITE-OIDIO-TOSCANA", 39)]

# ------------------------------------------------- 1. hindcast walk-forward leakage
for cname, var in CASES:
    d = os.path.join(CAS, cname)
    pre = cp.load_rows(d, var)
    years = sorted({r["_d"].year for r in pre[0]})
    per_year = {}
    for y in years:
        as_of = dt.date(y, 9, 6)
        CALLS.clear()
        cp._window_value = spy
        try:
            r = cp.current_pressure(d, var, as_of, _pre=pre)
        finally:
            cp._window_value = ORIG
        cur_calls = [c for c in CALLS if c["hi"] == as_of and c["lo"] == as_of - dt.timedelta(days=27)]
        base_calls = [c for c in CALLS if not (c["hi"] == as_of and
                                               c["lo"] == as_of - dt.timedelta(days=27))]
        base_years = set().union(*[c["years"] for c in base_calls]) if base_calls else set()
        cur_years = set().union(*[c["years"] for c in cur_calls]) if cur_calls else set()
        cur_max = max([c["max_date"] for c in cur_calls if c["max_date"]], default=None)
        base_max = max([c["max_date"] for c in base_calls if c["max_date"]], default=None)
        per_year[str(y)] = {
            "AS_OF": as_of.isoformat(),
            "N_WINDOW_CALLS": len(CALLS),
            "CURRENT_WINDOW_CONSUMED_YEARS": sorted(cur_years),
            "BASELINE_WINDOWS_CONSUMED_YEARS": sorted(base_years),
            "BASELINE_YEARS_AT_OR_AFTER_AS_OF_YEAR": sorted(x for x in base_years if x >= y),
            "CURRENT_MAX_DATE": cur_max.isoformat() if cur_max else None,
            "CURRENT_MAX_DATE_AFTER_AS_OF": bool(cur_max and cur_max > as_of),
            "BASELINE_MAX_DATE": base_max.isoformat() if base_max else None,
            "LEAK": bool([x for x in base_years if x >= y]) or bool(cur_max and cur_max > as_of),
        }
    OUT[cname] = {"PER_SEASON": per_year,
                  "N_SEASONS": len(per_year),
                  "N_SEASONS_WITH_LEAK": sum(1 for v in per_year.values() if v["LEAK"])}

# ------------------------------------------------- 2. recent_only lower-bound-only filter
rec = {}
for cname, var in CASES:
    d = os.path.join(CAS, cname)
    pre = cp.load_rows(d, var)
    years = sorted({r["_d"].year for r in pre[0]})
    y = years[len(years) // 2]
    N = 5
    sub = [r for r in pre[0] if r["_d"].year > y - 1 - N]
    rec[cname] = {
        "PROBE_SEASON": y, "recent_only": N,
        "FILTER_EXPRESSION": 'r["_d"].year > y - 1 - recent_only   (LOWER bound only)',
        "YEARS_SURVIVING_THE_FILTER": sorted({r["_d"].year for r in sub}),
        "YEARS_AT_OR_AFTER_PROBE_SEASON_STILL_PRESENT": sorted({r["_d"].year for r in sub if r["_d"].year >= y}),
        "N_ROWS_DATED_AFTER_PROBE_SEASON_STILL_PRESENT": sum(1 for r in sub if r["_d"].year > y),
        "NOTE": "rows from the future survive the subset; whether they REACH a number is the "
                "question the current_pressure baseline filter (y >= as_of.year -> continue) answers",
    }
OUT["RECENT_ONLY_FILTER"] = rec

# ------------------------------------------------- 3. metadata look-ahead
meta_audit = {}
for cname, var in CASES:
    d = os.path.join(CAS, cname)
    idx = json.load(open(os.path.join(d, "collection_index.json")))
    codes = idx.get("codes") or []
    reqs = idx["requests"]
    years_collected = sorted({r["year"] for r in reqs})
    meta_audit[cname] = {
        "N_CODES_IN_TABLE": len(codes),
        "CODE_TABLE_IS_PER_YEAR": False,
        "COLLECTED_YEARS": [years_collected[0], years_collected[-1]],
        "NOTE": "collect_generic keeps the MOST COMPLETE code table across all years and stores "
                "ONE table. Decoding season 2007 therefore uses a vocabulary that only existed "
                "in later years. This is metadata look-ahead, separate from row-level leakage.",
    }
OUT["METADATA_LOOKAHEAD"] = meta_audit

json.dump(OUT, open(os.path.join(HERE, "rt3_e4_leakage.json"), "w"), indent=1, default=str)

for cname, _ in CASES:
    v = OUT[cname]
    print(f"== {cname}: seasons={v['N_SEASONS']} seasons_with_leak={v['N_SEASONS_WITH_LEAK']}")
    for y, r in v["PER_SEASON"].items():
        flag = "LEAK" if r["LEAK"] else "ok  "
        print(f"   {y} {flag} cur_years={r['CURRENT_WINDOW_CONSUMED_YEARS']} "
              f"cur_max={r['CURRENT_MAX_DATE']} base_years>=Y={r['BASELINE_YEARS_AT_OR_AFTER_AS_OF_YEAR']} "
              f"base_max={r['BASELINE_MAX_DATE']}")
print()
print(json.dumps(OUT["RECENT_ONLY_FILTER"], indent=1))
