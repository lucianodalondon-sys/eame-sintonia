#!/usr/bin/env python3
"""RT2-A1 — WHAT IS var -1002, IN UNITS?

The published sentence says scouts "scored N visits for damaging olive-fly infestation".
That sentence is only true if -1002 is (a) a measurement of damage, (b) on a declared scale,
(c) with a denominator. This script reads the raw rows and answers all three from the archive,
never from the case name.

Joins the four olive variables on id_survey (one visit):
   -1003 Totale, -1002 Dannosa, -1001 Attiva, 1 tot = "Olive campionate"
"""
import json, glob, os, sys, collections
from statistics import median

CASE = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                    "..", "..", "CASES", "OLIVO-BACTROCERA-TOSCANA")


def load(var):
    out = {}
    for fn in sorted(glob.glob(os.path.join(CASE, "RAW", f"*_v{var}_*.json"))):
        y = int(os.path.basename(fn)[:-5].split("_")[-1])
        for r in json.load(open(fn, encoding="utf-8")):
            out[r["id_survey"]] = (r.get("val"), y, r.get("date"), r.get("nome_area"),
                                   r.get("id_field"))
    return out


def num(v):
    if v in (None, ""):
        return None
    try:
        return float(str(v).replace(",", "."))
    except ValueError:
        return None


if __name__ == "__main__":
    V = {v: load(v) for v in (-1003, -1002, -1001, 1)}
    keys = set(V[-1002])
    print(f"visits carrying var -1002 : {len(keys)}")
    for v in (-1003, -1001, 1):
        print(f"  also carrying var {v:>5d}  : {len(keys & set(V[v]))}")

    # --- 1. RANGE AND SHAPE OF THE PUBLISHED VARIABLE -------------------------------------
    vals = [num(V[-1002][k][0]) for k in keys]
    ok = [v for v in vals if v is not None]
    print(f"\n-1002 readable {len(ok)} of {len(vals)}  "
          f"min={min(ok)} max={max(ok)} median={median(ok)}")
    print(f"  values > 100 : {sum(1 for v in ok if v > 100)}")
    print(f"  non-integer  : {sum(1 for v in ok if abs(v - round(v)) > 1e-9)}")
    c = collections.Counter(ok)
    print("  10 commonest values:", c.most_common(10))

    # --- 2. DENOMINATOR: is it the fixed n=100 the census claims? --------------------------
    tots = [num(V[1][k][0]) for k in keys & set(V[1])]
    tok = [t for t in tots if t is not None]
    ct = collections.Counter(tok)
    print(f"\nvar 1 'Olive campionate' readable {len(tok)} of {len(tots)}")
    print("  commonest denominators:", ct.most_common(8))
    print(f"  share exactly 100 : {sum(1 for t in tok if t == 100)}/{len(tok)} "
          f"= {sum(1 for t in tok if t == 100)/len(tok):.4f}")
    print(f"  denominators == 0 : {sum(1 for t in tok if t == 0)}/{len(tok)}")

    # denominator by season, so an era break is visible
    per_y = collections.defaultdict(collections.Counter)
    for k in keys & set(V[1]):
        t = num(V[1][k][0])
        per_y[V[1][k][1]][t] += 1
    print("\n  year  n   share_tot=100  modal_tot  n_distinct_tot")
    for y in sorted(per_y):
        cc = per_y[y]
        n = sum(cc.values())
        print(f"  {y}  {n:6d}   {cc[100.0]/n:12.4f}  {cc.most_common(1)[0][0]!s:>9s}  "
              f"{len([x for x in cc if x is not None]):>3d}")

    # --- 3. IS -1002 A COUNT OR A PERCENT? ------------------------------------------------
    # If it is a COUNT of infested fruit it can never exceed tot.
    # If it is a PERCENT it can never exceed 100 and must be a multiple of 100/tot.
    gt_tot = mult = tested = 0
    for k in keys & set(V[1]):
        v, t = num(V[-1002][k][0]), num(V[1][k][0])
        if v is None or not t:
            continue
        tested += 1
        if v > t:
            gt_tot += 1
        step = 100.0 / t
        if abs((v / step) - round(v / step)) < 1e-6:
            mult += 1
    print(f"\nCOUNT-vs-PERCENT test on {tested} visits with both -1002 and a non-zero tot")
    print(f"  -1002 > tot (impossible for a count)          : {gt_tot}/{tested}")
    print(f"  -1002 is an exact multiple of 100/tot (percent): {mult}/{tested}")

    # discriminating subset: visits whose denominator is NOT 100 (there count != percent)
    sub = [(num(V[-1002][k][0]), num(V[1][k][0])) for k in keys & set(V[1])
           if num(V[1][k][0]) not in (None, 0, 100.0) and num(V[-1002][k][0])]
    print(f"  visits with tot NOT 100 and -1002 > 0          : {len(sub)}")
    if sub:
        pmult = sum(1 for v, t in sub if abs((v / (100.0 / t)) - round(v / (100.0 / t))) < 1e-6)
        print(f"     of those, -1002 an exact multiple of 100/tot: {pmult}/{len(sub)}")
        print(f"     of those, -1002 > tot                        : "
              f"{sum(1 for v, t in sub if v > t)}/{len(sub)}")
        print("     first 12 (dannosa, tot):", sub[:12])

    # --- 4. ORDERING: attiva <= dannosa <= totale ? ----------------------------------------
    both = keys & set(V[-1001]) & set(V[-1003])
    a_le_d = d_le_t = sum_eq = n = 0
    for k in both:
        a, d, t = num(V[-1001][k][0]), num(V[-1002][k][0]), num(V[-1003][k][0])
        if None in (a, d, t):
            continue
        n += 1
        a_le_d += a <= d
        d_le_t += d <= t
        sum_eq += abs((a + d) - t) < 1e-6
    print(f"\nSTAGE ALGEBRA on {n} visits with all three")
    print(f"  attiva <= dannosa : {a_le_d}/{n}")
    print(f"  dannosa <= totale : {d_le_t}/{n}")
    print(f"  attiva + dannosa == totale : {sum_eq}/{n}")

    # --- 5. HOW MUCH OF THE PUBLISHED SIGNAL IS AT THE SOURCE'S OWN ACTION BAND? -----------
    # source legend for this variable: 0 nessuna | 0.01-6 green | 6-10 yellow | >=10 red
    bands = collections.Counter()
    for v in ok:
        bands["0_NESSUNA" if v == 0 else
              "GREEN_0-6" if v < 6 else
              "YELLOW_6-10" if v < 10 else "RED_>=10"] += 1
    print("\nSOURCE'S OWN LEGEND BANDS over all readable -1002 values:")
    for b in ("0_NESSUNA", "GREEN_0-6", "YELLOW_6-10", "RED_>=10"):
        print(f"  {b:12s} {bands[b]:7d}/{len(ok)}  {bands[b]/len(ok):.4f}")
