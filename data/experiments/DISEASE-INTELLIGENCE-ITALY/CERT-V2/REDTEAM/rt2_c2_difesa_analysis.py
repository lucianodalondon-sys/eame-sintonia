#!/usr/bin/env python3
"""RT2-C2 — what the defence regime does to the baseline.

Uses CERT-V2/REDTEAM/DIFESA/difesa_map.json (fetched by rt2_c1) joined on id_survey to the
archive the pilot published from.

Three questions:
  1. COVERAGE. For how many seasons does the source carry the stratum at all?
  2. MIX. Does the biologico/integrato mix move between the seasons being compared?
  3. EFFECT. Inside the same province and the same 28-day window, does the regime change the
     published number? If it does, and the mix moved, the baseline is not comparable.
"""
import json, glob, os, sys, collections, datetime as dt
from statistics import median, mean

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
CASE = os.path.join(ROOT, "CASES", "OLIVO-BACTROCERA-TOSCANA")
VAR = -1002
LO, HI = dt.date(2026, 8, 10), dt.date(2026, 9, 6)


def num(v):
    if v in (None, ""):
        return None
    try:
        return float(str(v).replace(",", "."))
    except ValueError:
        return None


def load():
    den = {}
    for fn in glob.glob(os.path.join(CASE, "RAW", "*_v1_*.json")):
        for r in json.load(open(fn, encoding="utf-8")):
            den[str(r["id_survey"])] = num(r.get("val"))
    rows = []
    for fn in sorted(glob.glob(os.path.join(CASE, "RAW", f"*_v{VAR}_*.json"))):
        for r in json.load(open(fn, encoding="utf-8")):
            v = num(r.get("val"))
            if v is None or not r.get("date") or not den.get(str(r["id_survey"])):
                continue
            try:
                r["_d"] = dt.date.fromisoformat(r["date"])
            except ValueError:
                continue
            r["_v"] = v
            rows.append(r)
    return rows


if __name__ == "__main__":
    M = json.load(open(os.path.join(HERE, "DIFESA", "difesa_map.json"), encoding="utf-8"))
    reg = {}
    for y, d in M.items():
        for k, v in d.items():
            for i in v["ids"]:
                reg[i] = k
    rows = load()
    for r in rows:
        r["_reg"] = reg.get(str(r["id_survey"]), "NOT_DECLARED")

    print("1. COVERAGE of the defence-regime stratum, by season "
          "(rows that survive the engine's denominator guard)")
    print(f"  {'year':>5s} {'rows':>7s} {'bio':>7s} {'integrato':>10s} {'NOT_DECLARED':>13s} "
          f"{'labelled share':>15s} {'bio share of labelled':>22s}")
    per_y = collections.defaultdict(collections.Counter)
    for r in rows:
        per_y[r["_d"].year][r["_reg"]] += 1
    for y in sorted(per_y):
        c = per_y[y]
        n = sum(c.values())
        lab = c["bio"] + c["integrato"]
        print(f"  {y:5d} {n:7d} {c['bio']:7d} {c['integrato']:10d} {c['NOT_DECLARED']:13d} "
              f"{lab/n:15.4f} {(c['bio']/lab if lab else float('nan')):22.4f}")
    print("  NOTE: 2006-2019 return ok=true with ZERO rows for every regime — the stratum does "
          "not exist for 14 of the 20 baseline seasons, so its stability there is NOT KNOWN.")

    print("\n2. REGIME EFFECT inside the same province and the same 10 Aug - 6 Sep window")
    print(f"  {'year':>5s} {'province':14s} {'bio n':>6s} {'bio inc':>8s} {'int n':>6s} "
          f"{'int inc':>8s} {'bio - int':>10s}")
    diffs = []
    for y in range(2020, 2027):
        try:
            lo, hi = LO.replace(year=y), HI.replace(year=y)
        except ValueError:
            continue
        pw = collections.defaultdict(lambda: collections.defaultdict(
            lambda: collections.defaultdict(list)))
        for r in rows:
            if lo <= r["_d"] <= hi and r.get("nome_area"):
                pw[r["nome_area"]][r["_reg"]][r["id_field"]].append(r["_v"])
        for p in sorted(pw):
            b, i = pw[p].get("bio", {}), pw[p].get("integrato", {})
            if len(b) >= 8 and len(i) >= 8:
                bi = sum(1 for v in b.values() if max(v) > 0) / len(b)
                ii = sum(1 for v in i.values() if max(v) > 0) / len(i)
                diffs.append(bi - ii)
                print(f"  {y:5d} {p:14s} {len(b):6d} {bi:8.3f} {len(i):6d} {ii:8.3f} "
                      f"{bi-ii:+10.3f}")
    if diffs:
        print(f"  province-windows with >=8 sites in BOTH regimes: {len(diffs)}")
        print(f"  biologico reads higher in {sum(1 for d in diffs if d > 0)}/{len(diffs)}; "
              f"median difference {median(diffs):+.3f}, mean {mean(diffs):+.3f}, "
              f"max {max(diffs):+.3f}, min {min(diffs):+.3f}")

    print("\n3. WHOLE-SEASON regime effect (all weeks, 2020-2026), pooled over Toscana")
    print(f"  {'year':>5s} {'bio sites':>10s} {'bio inc':>8s} {'int sites':>10s} {'int inc':>8s} "
          f"{'ND sites':>9s} {'ND inc':>7s}")
    for y in range(2020, 2027):
        st = collections.defaultdict(lambda: collections.defaultdict(list))
        for r in rows:
            if r["_d"].year == y:
                st[r["_reg"]][r["id_field"]].append(r["_v"])
        def f(k):
            s = st.get(k, {})
            return len(s), (sum(1 for v in s.values() if max(v) > 0) / len(s)) if s else float("nan")
        bn, bi = f("bio"); inn, ii = f("integrato"); nn, ni = f("NOT_DECLARED")
        print(f"  {y:5d} {bn:10d} {bi:8.3f} {inn:10d} {ii:8.3f} {nn:9d} {ni:7.3f}")

    print("\n4. THE 2026 PUBLISHED WINDOW, split by regime")
    st = collections.defaultdict(lambda: collections.defaultdict(list))
    for r in rows:
        if LO <= r["_d"] <= HI and r.get("nome_area"):
            st[r["nome_area"]][r["_reg"]] = st[r["nome_area"]].get(r["_reg"], [])
    pw = collections.defaultdict(lambda: collections.defaultdict(
        lambda: collections.defaultdict(list)))
    for r in rows:
        if LO <= r["_d"] <= HI and r.get("nome_area"):
            pw[r["nome_area"]][r["_reg"]][r["id_field"]].append(r["_v"])
    print(f"  {'province':14s} " + "".join(f"{k:>22s}" for k in
                                           ("bio n/inc", "integrato n/inc", "NOT_DECLARED n/inc")))
    for p in sorted(pw):
        cells = []
        for k in ("bio", "integrato", "NOT_DECLARED"):
            s = pw[p].get(k, {})
            cells.append(f"{len(s)}/"
                         f"{(sum(1 for v in s.values() if max(v) > 0)/len(s)) if s else float('nan'):.3f}")
        print(f"  {p:14s} " + "".join(f"{c:>22s}" for c in cells))
