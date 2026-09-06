#!/usr/bin/env python3
"""RT2-B3 — is a "province" the same set of groves across the seasons being compared?

The baseline is "the same calendar window in prior seasons, same province". That is only a
comparison of SEASONS if the panel is stable. Three measurements:

  1. PANEL OVERLAP. Jaccard of the id_field sets inside the 10 Aug - 6 Sep window, 2026 vs each
     prior season, per province. If the panel rotates, "Siena in 2026" and "Siena in 2011" are
     different groves and the percentile is a comparison of places, not of years.
  2. ORGANISATIONS. How many scouting organisations contribute to each province-window, which
     ones, and whether the set changes. An organisation is a protocol: different crews, different
     grove lists, different diligence.
  3. EFFORT. Visits per site and sites per province inside the window, by season, and the
     province-agreement test of CASES/effort_confound.py re-run for olive and vine.
"""
import json, glob, os, sys, collections, datetime as dt, itertools
from statistics import mean, median

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "CASES"))
import province_agreement as pa
import effort_confound as ec

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
    rows = load()
    byp = collections.defaultdict(list)
    for r in rows:
        if r.get("nome_area"):
            byp[r["nome_area"]].append(r)

    def win(p, y):
        try:
            lo, hi = LO.replace(year=y), HI.replace(year=y)
        except ValueError:
            return []
        return [r for r in byp[p] if lo <= r["_d"] <= hi]

    print("1. PANEL OVERLAP inside the 10 Aug - 6 Sep window: 2026 vs each baseline season")
    print(f"  {'province':14s} {'2026 sites':>10s} {'median Jaccard vs 20 baselines':>31s} "
          f"{'best':>6s} {'worst':>6s} {'median shared sites':>20s}")
    for p in sorted(byp):
        cur = {r["id_field"] for r in win(p, 2026)}
        if not cur:
            continue
        js, sh = [], []
        for y in range(2006, 2026):
            b = {r["id_field"] for r in win(p, y)}
            if len(b) >= 8:
                js.append(len(cur & b) / len(cur | b))
                sh.append(len(cur & b))
        if js:
            print(f"  {p:14s} {len(cur):10d} {median(js):31.3f} {max(js):6.3f} {min(js):6.3f} "
                  f"{median(sh):20.1f}")

    print("\n   the same, but adjacent seasons only (2025 vs 2026 etc) — panel turnover per year")
    tj = []
    for p in sorted(byp):
        js = []
        for y in range(2007, 2027):
            a = {r["id_field"] for r in win(p, y - 1)}
            b = {r["id_field"] for r in win(p, y)}
            if len(a) >= 8 and len(b) >= 8:
                js.append(len(a & b) / len(a | b))
        if js:
            tj += js
            print(f"  {p:14s} median year-on-year Jaccard {median(js):.3f} over {len(js)} pairs")
    if tj:
        print(f"  ALL PROVINCES median year-on-year Jaccard {median(tj):.3f} over {len(tj)} pairs")

    print("\n2. ORGANISATIONS scouting inside the window, by season")
    orgs_y = collections.defaultdict(set)
    for r in rows:
        y = r["_d"].year
        try:
            lo, hi = LO.replace(year=y), HI.replace(year=y)
        except ValueError:
            continue
        if lo <= r["_d"] <= hi and r.get("org_name"):
            orgs_y[y].add(r["org_name"])
    prev = None
    print(f"  {'year':>5s} {'n_orgs':>7s} {'entered':>40s} {'left':>40s}")
    for y in sorted(orgs_y):
        s = orgs_y[y]
        ent = sorted(s - prev) if prev else sorted(s)
        lef = sorted(prev - s) if prev else []
        print(f"  {y:5d} {len(s):7d} {','.join(ent)[:38]:>40s} {','.join(lef)[:38]:>40s}")
        prev = s
    print(f"  organisations ever seen in this window: {len(set().union(*orgs_y.values()))}")

    print("\n   per-province org count inside the window, 2026 vs baseline median")
    for p in sorted(byp):
        cur = {r.get("org_name") for r in win(p, 2026) if r.get("org_name")}
        base = []
        for y in range(2006, 2026):
            o = {r.get("org_name") for r in win(p, y) if r.get("org_name")}
            if o:
                base.append(len(o))
        if base:
            print(f"  {p:14s} 2026 n_orgs {len(cur):2d}  baseline median {median(base):.1f}  "
                  f"2026 orgs {sorted(cur)}")

    print("\n3. EFFORT inside the window, by season (visits per site), and sites per province")
    print(f"  {'province':14s} {'2026 sites':>10s} {'base med sites':>15s} "
          f"{'2026 visits/site':>17s} {'base med visits/site':>21s}")
    for p in sorted(byp):
        c = win(p, 2026)
        if not c:
            continue
        cs = len({r["id_field"] for r in c})
        cv = len(c) / cs if cs else 0
        bs, bv = [], []
        for y in range(2006, 2026):
            b = win(p, y)
            s = len({r["id_field"] for r in b})
            if s >= 8:
                bs.append(s); bv.append(len(b) / s)
        if bs:
            print(f"  {p:14s} {cs:10d} {median(bs):15.1f} {cv:17.2f} {median(bv):21.2f}")

    print("\n4. CASES/effort_confound.py re-run — does EFFORT agree across provinces more "
          "than the DISEASE does?")
    for name, d, var in (("OIDIO", os.path.join(ROOT, "CASES", "VITE-OIDIO-TOSCANA"), 39),
                         ("BACTROCERA", CASE, -1002),
                         ("BACTROCERA_attiva", CASE, -1001)):
        E, D = ec.series(d, var)
        ne, pe, re_ = ec.agreement(E)
        nd, pd, rd = ec.agreement(D)
        print(f"  {name:18s} EFFORT pairs={ne:3d} pos={pe:3d} rho={re_:+.3f} | "
              f"DISEASE pairs={nd:3d} pos={pd:3d} rho={rd:+.3f} | "
              f"{'EFFORT WINS' if (re_ or 0) > (rd or 0) else 'disease exceeds effort'}")
