#!/usr/bin/env python3
"""
RED TEAM / EFFORT INVARIANCE.

INCIDENCE is the share of sites whose MAXIMUM value over the 28-day window is > 0. A max over
more visits is never smaller than a max over fewer, so the metric is mechanically monotonic in
survey effort. If the number of visits per site differs between the current window and the
baseline windows, part of the percentile is a statement about scouting intensity.

Decisive test: recompute the whole sweep with an EFFORT-INVARIANT metric — exactly ONE visit
per site (the earliest in the window) — and count how many published labels change.

Out: REDTEAM/rt_effort.json (+ stdout)
"""
import json, os, sys, datetime as dt, collections
from statistics import mean

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "ENGINE"))
sys.path.insert(0, os.path.join(ROOT, "CASES"))
import current_pressure as cp
import rt_core

HIGHER, TYPICAL, LOWER = cp.HIGHER, cp.TYPICAL, cp.LOWER
CLASSED = (HIGHER, TYPICAL, LOWER)


def window_value_first_visit(rows, scale, lo, hi, mode):
    """One visit per site: the earliest readable observation inside the window."""
    best = {}
    for r in rows:
        if not (lo <= r["_d"] <= hi):
            continue
        v = cp.read_value(r, scale, mode)
        if v is None:
            continue
        k = r["id_field"]
        if k not in best or r["_d"] < best[k][0]:
            best[k] = (r["_d"], v)
    if not best:
        return None
    vals = [v for _, v in best.values()]
    pos = sum(1 for v in vals if v > 0)
    return {"n_sites": len(vals), "n_visits": len(vals), "n_pos": pos,
            "INCIDENCE": round(pos / len(vals), 4)}


def cells(rows, scale, mode, as_of, wv):
    hi_, lo = as_of, as_of - dt.timedelta(days=cp.WINDOW_DAYS - 1)
    by_prov = collections.defaultdict(list)
    for r in rows:
        p = r.get("nome_area")
        if p:
            by_prov[p].append(r)
    out = {}
    for prov, prows in sorted(by_prov.items()):
        cur = wv(prows, scale, lo, hi_, mode)
        if cur is None or cur["n_sites"] < cp.MIN_SITES:
            out[prov] = {"STATE": cp.UNKNOWN_NO_DATA}
            continue
        base = []
        for y in sorted({r["_d"].year for r in prows}):
            if y >= as_of.year:
                continue
            b = wv(prows, scale, cp._shift_year(lo, y), cp._shift_year(hi_, y), mode)
            if b and b["n_sites"] >= cp.MIN_SITES:
                base.append(b["INCIDENCE"])
        if len(base) < cp.MIN_BASE:
            out[prov] = {"STATE": cp.UNKNOWN_NO_BASELINE}
            continue
        v = cur["INCIDENCE"]
        p = (sum(1 for b in base if b < v) + 0.5 * sum(1 for b in base if b == v)) / len(base)
        st = HIGHER if p >= cp.HIGH_P else (LOWER if p <= cp.LOW_P else TYPICAL)
        if st == HIGHER and cur["n_sites"] * v < cp.MIN_POSITIVE_SITES:
            st = TYPICAL
        out[prov] = {"STATE": st, "VALUE": v, "PERCENTILE": round(p, 4),
                     "n_sites": cur["n_sites"], "n_pos": cur["n_pos"]}
    return out


shipped, invariant, effort = {}, {}, []
for region, crop, issue, case, var in rt_core.CASES:
    rows, scale, mode = rt_core.load_case(case, var)
    for as_of in rt_core.ALL_DATES:
        a = cells(rows, scale, mode, as_of, rt_core.window_value)
        b = cells(rows, scale, mode, as_of, window_value_first_visit)
        for p in a:
            shipped[(crop, as_of.isoformat(), p)] = a[p]
            invariant[(crop, as_of.isoformat(), p)] = b.get(p, {"STATE": None})
    print("  done", crop, flush=True)

both = [k for k in shipped
        if shipped[k]["STATE"] in CLASSED and invariant[k]["STATE"] in CLASSED]
chg = [k for k in both if shipped[k]["STATE"] != invariant[k]["STATE"]]
lost = [k for k in shipped if shipped[k]["STATE"] in CLASSED
        and invariant[k]["STATE"] not in CLASSED]
mat = collections.Counter((shipped[k]["STATE"], invariant[k]["STATE"]) for k in both)
hi_ship = [k for k in both if shipped[k]["STATE"] == HIGHER]
OUT = {
    "METRIC_COMPARED": "shipped site-max over every visit in the window  vs  one visit per "
                       "site (the earliest in the window)",
    "CELLS_CLASSIFIED_UNDER_BOTH": len(both),
    "LABEL_CHANGES": f"{len(chg)}/{len(both)}",
    "CELLS_THAT_STOP_BEING_CLASSIFIABLE": len(lost),
    "CONFUSION": {f"{a}->{b}": v for (a, b), v in sorted(mat.items())},
    "HIGHER_UNDER_SHIPPED_METRIC": len(hi_ship),
    "OF_THOSE_STILL_HIGHER_WITH_ONE_VISIT_PER_SITE":
        sum(1 for k in hi_ship if invariant[k]["STATE"] == HIGHER),
    "CHANGED_ROWS": [{"CROP": k[0], "DATE": k[1], "PROVINCE": k[2],
                      "SHIPPED": shipped[k]["STATE"], "ONE_VISIT_PER_SITE": invariant[k]["STATE"],
                      "VALUE_shipped": shipped[k].get("VALUE"),
                      "VALUE_one_visit": invariant[k].get("VALUE")} for k in chg][:40]}
print(json.dumps({k: v for k, v in OUT.items() if k != "CHANGED_ROWS"}, indent=1))
json.dump(OUT, open(os.path.join(HERE, "rt_effort.json"), "w"), indent=1, default=str)
print("wrote rt_effort.json")
