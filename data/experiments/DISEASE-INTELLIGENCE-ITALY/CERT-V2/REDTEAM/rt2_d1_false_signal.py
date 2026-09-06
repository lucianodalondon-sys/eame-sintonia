#!/usr/bin/env python3
"""RT2-D1 — make the instrument publish something it should not.

Four attacks, all inside the engine's own declared gate (MIN_SITES 8, MIN_BASE 5, 0.80/0.20,
MIN_POSITIVE_SITES 5 on HIGHER only):

  D1a  HOW THIN IS A PUBLISHED CELL? For every province-date the engine classifies, count the
       positive sites the class rests on. The HIGHER path has an effect-size floor; the LOWER
       path has none, so LOWER can be published off a baseline that is almost all zeros.
  D1b  ONE FRUIT. What magnitude does a "positive site" actually carry? A positive is
       max(value) > 0 and the sample is ~100 fruit, so 1.0 means ONE damaged drupe in one
       hundred. Counted.
  D1c  TEST-RETEST. Same grove, two visits <= 10 days apart, same season: how often does the
       binary >0 flag flip? That is the reliability of the quantity being percentiled.
  D1d  DOES EFFORT EXPLAIN THE CLASS? For each province, the walk-forward class at 6 September
       of each season is regressed (by rank correlation) on (i) the disease value and (ii) the
       number of sites and visits in the window and the number of organisations. If effort ranks
       the seasons as well as the disease does, the class is a statement about the programme.
"""
import json, glob, os, sys, collections, datetime as dt
from statistics import median, mean

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "ENGINE"))
sys.path.insert(0, os.path.join(ROOT, "CASES"))
import current_pressure as cp
import province_agreement as pa

OLIVE = os.path.join(ROOT, "CASES", "OLIVO-BACTROCERA-TOSCANA")
VINE = os.path.join(ROOT, "CASES", "VITE-OIDIO-TOSCANA")


def num(v):
    if v in (None, ""):
        return None
    try:
        return float(str(v).replace(",", "."))
    except ValueError:
        return None


def load(case, var, denom=True):
    den = {}
    if denom:
        for fn in glob.glob(os.path.join(case, "RAW", "*_v1_*.json")):
            for r in json.load(open(fn, encoding="utf-8")):
                den[str(r["id_survey"])] = num(r.get("val"))
    rows = []
    for fn in sorted(glob.glob(os.path.join(case, "RAW", f"*_v{var}_*.json"))):
        for r in json.load(open(fn, encoding="utf-8")):
            v = num(r.get("val"))
            if v is None or not r.get("date"):
                continue
            if denom and not den.get(str(r["id_survey"])):
                continue
            try:
                r["_d"] = dt.date.fromisoformat(r["date"])
            except ValueError:
                continue
            r["_v"] = v
            rows.append(r)
    return rows


if __name__ == "__main__":
    # ---------- D1a : how thin is a published cell ------------------------------------
    print("D1a — HOW THIN IS A PUBLISHED CELL? every classified province-date, "
          "olive var -1002 and vine var 39, six dates through 2026")
    print(f"  {'case':6s} {'as_of':10s} {'province':14s} {'class':20s} {'sites':>5s} "
          f"{'pos sites':>9s} {'base_n':>6s} {'base zeros':>10s} {'pct':>6s}")
    thin = []
    for tag, case, var in (("OLIVE", OLIVE, -1002), ("VINE", VINE, 39)):
        pre = cp.load_rows(case, var)
        for aso in ("2026-06-15", "2026-07-01", "2026-07-15", "2026-08-01",
                    "2026-08-15", "2026-09-06"):
            r = cp.current_pressure(case, var, dt.date.fromisoformat(aso), _pre=pre)
            for p, v in r["PROVINCES"].items():
                if v.get("STATE") not in (cp.HIGHER, cp.TYPICAL, cp.LOWER):
                    continue
                pos = round(v["n_sites"] * v["VALUE"], 1)
                # how many baseline seasons are identical to the current value
                bn = v["BASELINE_N"]
                print(f"  {tag:6s} {aso:10s} {p:14s} {v['STATE']:20s} {v['n_sites']:5d} "
                      f"{pos:9.1f} {bn:6d} {'-':>10s} {v.get('PERCENTILE'):6.3f}")
                if pos <= 3 and v["STATE"] != cp.LOWER:
                    thin.append((tag, aso, p, v["STATE"], pos, v["n_sites"]))
    print(f"  cells classed something other than LOWER on <= 3 positive sites: {len(thin)}")
    for t in thin:
        print("   ", t)

    # ---------- D1b : one fruit -------------------------------------------------------
    print("\nD1b — WHAT IS A 'POSITIVE SITE' MADE OF? distribution of the site-max value "
          "among positive site-windows (olive, 10 Aug-6 Sep, all seasons)")
    rows = load(OLIVE, -1002)
    st = collections.defaultdict(list)
    for r in rows:
        y = r["_d"].year
        try:
            lo, hi = dt.date(y, 8, 10), dt.date(y, 9, 6)
        except ValueError:
            continue
        if lo <= r["_d"] <= hi:
            st[(r["id_field"], y)].append(r["_v"])
    mx = [max(v) for v in st.values()]
    pos = [v for v in mx if v > 0]
    print(f"  site-windows {len(mx)}, positive {len(pos)}")
    for lab, lo_, hi_ in (("exactly 1 (one drupe in ~100)", 1, 1), ("2", 2, 2), ("3-5", 3, 5),
                          ("6-9 (source YELLOW)", 6, 9), (">=10 (source RED)", 10, 1e9)):
        n = sum(1 for v in pos if lo_ <= v <= hi_)
        print(f"    {lab:32s} {n:6d}/{len(pos)}  {n/len(pos):.4f}")
    print(f"  share of POSITIVE sites at or above the source's own RED action band: "
          f"{sum(1 for v in pos if v >= 10)}/{len(pos)} = {sum(1 for v in pos if v >= 10)/len(pos):.4f}")

    # ---------- D1c : test-retest -----------------------------------------------------
    print("\nD1c — TEST-RETEST of the binary '>0' flag: same grove, consecutive visits "
          "<= 10 days apart, same season")
    seq = collections.defaultdict(list)
    for r in rows:
        seq[(r["id_field"], r["_d"].year)].append((r["_d"], r["_v"]))
    n = flip = pos_then_zero = 0
    for k, s in seq.items():
        s.sort()
        for (d0, v0), (d1, v1) in zip(s, s[1:]):
            if (d1 - d0).days > 10:
                continue
            n += 1
            if (v0 > 0) != (v1 > 0):
                flip += 1
            if v0 > 0 and v1 <= 0:
                pos_then_zero += 1
    print(f"  consecutive pairs within 10 days: {n}")
    print(f"  the >0 flag FLIPS between the two visits: {flip}/{n} = {flip/n:.4f}")
    print(f"  positive then zero (the pest cannot leave the fruit): "
          f"{pos_then_zero}/{n} = {pos_then_zero/n:.4f}")
    # restrict to low readings, where a 100-fruit sample is a coin flip
    n2 = f2 = 0
    for k, s in seq.items():
        s.sort()
        for (d0, v0), (d1, v1) in zip(s, s[1:]):
            if (d1 - d0).days > 10 or not (0 < v0 <= 2):
                continue
            n2 += 1
            f2 += v1 <= 0
    print(f"  among visits reading 1-2 (one or two drupes in ~100), the NEXT visit within "
          f"10 days reads zero: {f2}/{n2} = {f2/n2:.4f}" if n2 else "")

    # ---------- D1d : does effort explain the class? ----------------------------------
    print("\nD1d — DOES EFFORT RANK THE SEASONS AS WELL AS THE DISEASE DOES? "
          "(6 September window, per province)")
    for tag, case, var in (("OLIVE", OLIVE, -1002), ("VINE", VINE, 39)):
        rws = load(case, var, denom=(tag == "OLIVE"))
        byp = collections.defaultdict(list)
        for r in rws:
            if r.get("nome_area"):
                byp[r["nome_area"]].append(r)
        print(f"  --- {tag}")
        print(f"  {'province':14s} {'n seasons':>9s} {'rho(inc, n_sites)':>18s} "
              f"{'rho(inc, visits/site)':>22s} {'rho(inc, n_orgs)':>17s}")
        agg = [[], [], []]
        for p in sorted(byp):
            xs = []
            for y in sorted({r["_d"].year for r in byp[p]}):
                try:
                    lo, hi = dt.date(y, 8, 10), dt.date(y, 9, 6)
                except ValueError:
                    continue
                w = [r for r in byp[p] if lo <= r["_d"] <= hi]
                s = collections.defaultdict(list)
                for r in w:
                    s[r["id_field"]].append(r["_v"])
                if len(s) < 8:
                    continue
                m = [max(v) for v in s.values()]
                xs.append((sum(1 for v in m if v > 0) / len(m), len(s), len(w) / len(s),
                           len({r.get("org_name") for r in w if r.get("org_name")})))
            if len(xs) >= 8:
                inc = [a for a, _, _, _ in xs]
                r1 = pa.spear(inc, [b for _, b, _, _ in xs])
                r2 = pa.spear(inc, [c for _, _, c, _ in xs])
                r3 = pa.spear(inc, [d for _, _, _, d in xs])
                for i, r_ in enumerate((r1, r2, r3)):
                    if r_ is not None:
                        agg[i].append(r_)
                print(f"  {p:14s} {len(xs):9d} {r1:18.3f} {r2:22.3f} {r3:17.3f}")
        print(f"  {'MEAN':14s} {'':9s} {mean(agg[0]):18.3f} {mean(agg[1]):22.3f} "
              f"{mean(agg[2]):17.3f}")
