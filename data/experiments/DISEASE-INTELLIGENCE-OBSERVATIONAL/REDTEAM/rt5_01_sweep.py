#!/usr/bin/env python3
"""RT5 · accusation 1. One-at-a-time sweep of all nine declared parameters.

For every value of every parameter the ten province verdicts (historical_state
and observed_trend) are recomputed and compared against what the tool publishes
today. Output: which parameters move verdicts, which never do, and over what
fraction of its own plausible range each published verdict survives."""
import os, sys, json, datetime as dt
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import rt5_lib as L

AS_OF = dt.date(2026, 9, 6)
idx, raw = L.get_index("ACTIVE_INFESTATION_COUNT")
PROV = idx.provinces

BASE = L.all_cells(idx, AS_OF)
PUB_H = {c["province"]: c["historical_state"] for c in BASE}
PUB_T = {c["province"]: c["observed_trend"] for c in BASE}

GRID = {
    "WINDOW_DAYS":        [7, 10, 14, 17, 21, 24, 28, 31, 35, 42, 49, 56, 63, 70, 84, 91],
    "MIN_VISITS":         [0, 1, 2, 3, 4, 5, 6, 7, 8, 10, 12, 15, 20, 25, 30, 40, 60],
    "MIN_DRUPES":         [0, 100, 200, 300, 400, 500, 800, 1000, 1500, 2000, 3000, 5000,
                           10000, 20000],
    "MIN_BASELINE_SEASONS": [1, 2, 3, 4, 5, 6, 7, 8, 10, 12, 14, 15, 17, 18, 20],
    "HIGH_PCTL":          [0.50, 0.55, 0.60, 0.65, 0.70, 0.75, 0.80, 0.85, 0.90, 0.95, 1.00],
    "LOW_PCTL":           [0.00, 0.05, 0.10, 0.15, 0.20, 0.25, 0.30, 0.35, 0.40, 0.45, 0.50],
    "TREND_MIN_WINDOWS":  [2, 3, 4, 5, 6, 7, 8, 10, 12],
    "TREND_MIN_ABS_CHANGE_PCT": [0.0, 0.05, 0.1, 0.2, 0.3, 0.5, 0.75, 1.0, 1.5, 2.0, 3.0, 5.0],
    "MIN_PANEL_OVERLAP_FOR_LIKE_FOR_LIKE":
                          [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 12, 14, 16, 18, 20, 25, 30, 40],
}

results = {}
for name, vals in GRID.items():
    rows = []
    for v in vals:
        P = dict(L.PARAMS)
        P[name] = v
        cells = L.all_cells(idx, AS_OF, P=P)
        h = {c["province"]: c["historical_state"] for c in cells}
        t = {c["province"]: c["observed_trend"] for c in cells}
        rows.append({
            "value": v,
            "hist": h, "trend": t,
            "n_hist_differ": sum(1 for p in PROV if h[p] != PUB_H[p]),
            "n_trend_differ": sum(1 for p in PROV if t[p] != PUB_T[p]),
            "n_speaking": sum(1 for p in PROV if h[p] != "INSUFFICIENT_DATA"),
            "n_below": sum(1 for p in PROV if h[p] == "BELOW_HISTORICAL"),
            "n_above": sum(1 for p in PROV if h[p] == "ABOVE_HISTORICAL"),
            "n_typical": sum(1 for p in PROV if h[p] == "TYPICAL"),
            "firenze": h["Firenze"], "siena": h["Siena"], "arezzo": h["Arezzo"],
            "firenze_trend": t["Firenze"], "siena_trend": t["Siena"],
        })
    results[name] = {"grid": vals, "rows": rows,
                     "hist_changed_at": [r["value"] for r in rows if r["n_hist_differ"]],
                     "trend_changed_at": [r["value"] for r in rows if r["n_trend_differ"]],
                     "load_bearing_hist": any(r["n_hist_differ"] for r in rows),
                     "load_bearing_trend": any(r["n_trend_differ"] for r in rows)}

print(f"published today: {PUB_H}")
print(f"published trend: {PUB_T}\n")
hdr = f"{'parameter':38s} {'n_vals':>6} {'hist moves':>10} {'trend moves':>11}  {'FI stable over':>16} {'SI stable over':>16} {'AR stable over':>16}"
print(hdr)
for name, r in results.items():
    rows = r["rows"]
    fi = sum(1 for x in rows if x["firenze"] == PUB_H["Firenze"])
    si = sum(1 for x in rows if x["siena"] == PUB_H["Siena"])
    ar = sum(1 for x in rows if x["arezzo"] == PUB_H["Arezzo"])
    n = len(rows)
    print(f"{name:38s} {n:>6} "
          f"{sum(1 for x in rows if x['n_hist_differ']):>10} "
          f"{sum(1 for x in rows if x['n_trend_differ']):>11}  "
          f"{f'{fi}/{n}':>16} {f'{si}/{n}':>16} {f'{ar}/{n}':>16}")

print("\n--- detail: values at which any province verdict differs from published ---")
for name, r in results.items():
    if not r["load_bearing_hist"] and not r["load_bearing_trend"]:
        print(f"{name:38s} DECORATION: no value in {r['grid']} changes any verdict")
        continue
    print(f"\n{name}")
    for x in r["rows"]:
        flag = "  <== published default" if x["value"] == L.PARAMS[name] else ""
        if x["n_hist_differ"] or x["n_trend_differ"] or x["value"] == L.PARAMS[name]:
            print(f"   {str(x['value']):>8}  speak={x['n_speaking']:>2} "
                  f"below={x['n_below']} above={x['n_above']} typ={x['n_typical']}  "
                  f"FI={x['firenze']:<17} SI={x['siena']:<17} AR={x['arezzo']:<17}"
                  f" dH={x['n_hist_differ']} dT={x['n_trend_differ']}{flag}")

json.dump({"as_of": AS_OF.isoformat(), "published_hist": PUB_H, "published_trend": PUB_T,
           "results": results},
          open(os.path.join(HERE, "rt5_01_sweep.json"), "w"), indent=1)
