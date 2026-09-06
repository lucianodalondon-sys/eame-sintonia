#!/usr/bin/env python3
"""RT2-A3 — the pilot published the variable an advisor CANNOT act on.

Bactrocera oleae protocol (Toscana, survey_schema 1): the visit destructively samples fruit and
counts stages. The source derives three summaries:
    -1001 "attiva"  Infestazione Attiva   — the live, still-killable population
    -1002 "dannosa" Infestazione Dannosa  — damage already inflicted on the drupe
    -1003 "totale"  Totale
An adulticide/larvicide decision is taken on ATTIVA. DANNOSA is the receipt, not the decision.
The pilot publishes -1002.

This script (1) measures how often the two disagree in sign inside a visit, and (2) re-runs the
engine's own current_pressure on -1001 with everything else identical, so the cost of the
choice is a table of published classes, not an opinion.
"""
import json, glob, os, sys, collections, datetime as dt

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "ENGINE"))
sys.path.insert(0, os.path.join(ROOT, "CASES"))
import current_pressure as cp

CASE = os.path.join(ROOT, "CASES", "OLIVO-BACTROCERA-TOSCANA")


def load(var):
    out = {}
    for fn in sorted(glob.glob(os.path.join(CASE, "RAW", f"*_v{var}_*.json"))):
        for r in json.load(open(fn, encoding="utf-8")):
            out[str(r["id_survey"])] = r
    return out


def num(v):
    if v in (None, ""):
        return None
    try:
        return float(str(v).replace(",", "."))
    except ValueError:
        return None


if __name__ == "__main__":
    A, D = load(-1001), load(-1002)
    k = sorted(set(A) & set(D))
    pairs = [(num(A[i]["val"]), num(D[i]["val"]), A[i].get("date")) for i in k]
    pairs = [(a, d, t) for a, d, t in pairs if a is not None and d is not None]
    n = len(pairs)
    print(f"visits with BOTH attiva and dannosa readable: {n}")
    print(f"  attiva  > dannosa : {sum(1 for a, d, _ in pairs if a > d)}/{n}")
    print(f"  attiva == dannosa : {sum(1 for a, d, _ in pairs if a == d)}/{n}")
    print(f"  attiva  < dannosa : {sum(1 for a, d, _ in pairs if a < d)}/{n}")
    # the case that matters for a >0 incidence rule: one says PRESENT, the other says ABSENT
    ap_dz = sum(1 for a, d, _ in pairs if a > 0 and d <= 0)
    az_dp = sum(1 for a, d, _ in pairs if a <= 0 and d > 0)
    print(f"  ATTIVA present while DANNOSA reads zero : {ap_dz}/{n}   "
          f"(the engine files every one of these as 'no infestation')")
    print(f"  DANNOSA present while ATTIVA reads zero : {az_dp}/{n}")

    # by month, because the disagreement is phenological, not random
    by_m = collections.defaultdict(lambda: [0, 0, 0])
    for a, d, t in pairs:
        if not t:
            continue
        m = int(t[5:7])
        by_m[m][0] += 1
        by_m[m][1] += a > 0
        by_m[m][2] += d > 0
    print(f"\n{'month':>5s} {'visits':>8s} {'%visits attiva>0':>17s} {'%visits dannosa>0':>18s}")
    for m in sorted(by_m):
        t, ap, dp = by_m[m]
        print(f"{m:5d} {t:8d} {ap/t:17.4f} {dp/t:18.4f}")

    # ---- the same engine, the same day, the actionable variable --------------------------
    for var in (-1002, -1001):
        r = cp.current_pressure(CASE, var, dt.date(2026, 9, 6))
        c = collections.Counter(v["STATE"] for v in r["PROVINCES"].values())
        print(f"\n=== current_pressure var {var} as_of 2026-09-06 -> {dict(c)}")
        for p, v in r["PROVINCES"].items():
            print(f"   {p:14s} {v['STATE']:20s} val={str(v.get('VALUE')):7s} "
                  f"sites={v['n_sites']:3d} med={str(v.get('BASELINE_MEDIAN')):7s} "
                  f"pct={v.get('PERCENTILE','-')}")
