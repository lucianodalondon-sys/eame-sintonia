#!/usr/bin/env python3
"""RT2-A2 — the unit of var -1002, and the values that cannot exist in that unit.

A1 showed min = -3.0 and max = 140.0. Neither is possible for a percentage of sampled fruit,
and neither is possible for a count of infested fruit out of 100. This script counts them and
shows what the engine does with them, because the engine's INCIDENCE test is `value > 0`:
a NEGATIVE infestation is silently filed as "no infestation present", i.e. as a clean grove.
"""
import json, glob, os, collections
from statistics import mean

CASE = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                    "..", "..", "CASES", "OLIVO-BACTROCERA-TOSCANA")


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
    D, T, A, TOT = load(-1002), load(-1003), load(-1001), load(1)
    keys = sorted(D)

    neg = [(k, num(D[k]["val"]), num(TOT.get(k, {}).get("val")), D[k]["date"],
            D[k].get("nome_area")) for k in keys if (num(D[k]["val"]) or 0) < 0]
    over = [(k, num(D[k]["val"]), num(TOT.get(k, {}).get("val")), D[k]["date"],
             D[k].get("nome_area")) for k in keys if (num(D[k]["val"]) or 0) > 100]
    readable = [k for k in keys if num(D[k]["val"]) is not None]
    print(f"IMPOSSIBLE VALUES in var -1002, over {len(readable)} readable of {len(keys)} visits")
    print(f"  NEGATIVE  : {len(neg)}   {[(x[1], x[3], x[4]) for x in neg][:12]}")
    print(f"  > 100      : {len(over)}   {[(x[1], x[2], x[3], x[4]) for x in over]}")
    print(f"  engine rule is INCIDENCE = share of sites with max(value) > 0, so every NEGATIVE "
          f"visit is read as ABSENCE OF THE PEST")

    # same audit on the ACTIVE variable, which is the one an advisor would act on
    for name, M in (("-1001 attiva", A), ("-1003 totale", T)):
        r = [num(M[k]["val"]) for k in M if num(M[k]["val"]) is not None]
        print(f"  {name}: n={len(r)} min={min(r)} max={max(r)} "
              f"neg={sum(1 for v in r if v < 0)} gt100={sum(1 for v in r if v > 100)}")

    # ---- UNIT: percent-of-tot, or count-of-fruit? -----------------------------------------
    print("\nUNIT TEST, split by the declared denominator var 1 'Olive campionate'")
    by_tot = collections.defaultdict(lambda: [0, 0, 0])   # tot -> [n, n_percent_consistent, n_pos]
    for k in keys:
        v, t = num(D[k]["val"]), num(TOT.get(k, {}).get("val"))
        if v is None or not t or v <= 0:
            continue
        step = 100.0 / t
        by_tot[t][0] += 1
        by_tot[t][1] += abs(v / step - round(v / step)) < 1e-6
        by_tot[t][2] += 1
    rows = sorted(by_tot.items(), key=lambda kv: -kv[1][0])[:12]
    print(f"  {'tot':>8s} {'n_pos_visits':>13s} {'consistent_with_%_of_tot':>26s}")
    for t, (n, cons, _) in rows:
        print(f"  {t:8.0f} {n:13d} {cons:>19d}/{n}")
    nott = [(t, v) for t, v in by_tot.items() if t != 100.0]
    n_all = sum(v[0] for v in by_tot.values())
    n_not100 = sum(v[0] for _, v in nott)
    cons_not100 = sum(v[1] for _, v in nott)
    print(f"  positive visits whose denominator is NOT 100 : {n_not100}/{n_all}")
    print(f"     of those, value is a valid percentage of tot: {cons_not100}/{n_not100}")

    # ---- WHAT THE 28-DAY-WINDOW PUBLISHED VALUE IS MADE OF, 2026-08-10..2026-09-06 --------
    import datetime as dt
    lo, hi = dt.date(2026, 8, 10), dt.date(2026, 9, 6)
    prov = collections.defaultdict(lambda: collections.defaultdict(list))
    for k in keys:
        d = D[k].get("date")
        if not d:
            continue
        try:
            dd = dt.date.fromisoformat(d)
        except ValueError:
            continue
        if not (lo <= dd <= hi):
            continue
        t = num(TOT.get(k, {}).get("val"))
        if not t:                                   # engine's denominator guard drops these
            continue
        v = num(D[k]["val"])
        if v is None:
            continue
        prov[D[k].get("nome_area")][D[k]["id_field"]].append(v)
    print(f"\nTHE PUBLISHED WINDOW {lo}..{hi}: what the positive sites actually scored")
    print(f"  {'province':14s} {'sites':>5s} {'pos':>4s} {'INCIDENCE':>10s} "
          f"{'sites>=6%':>10s} {'sites>=10%(RED)':>16s} {'max value seen':>15s}")
    tp = tpos = tred = 0
    for p in sorted(prov):
        if not p:
            continue
        mx = [max(v) for v in prov[p].values()]
        pos = sum(1 for v in mx if v > 0)
        yel = sum(1 for v in mx if v >= 6)
        red = sum(1 for v in mx if v >= 10)
        tp += len(mx); tpos += pos; tred += red
        print(f"  {p:14s} {len(mx):5d} {pos:4d} {pos/len(mx):10.4f} {yel:10d} {red:16d} "
              f"{max(mx):15.1f}")
    print(f"  TOTAL sites {tp}  positive {tpos}  at-or-above the source's RED band {tred}")
