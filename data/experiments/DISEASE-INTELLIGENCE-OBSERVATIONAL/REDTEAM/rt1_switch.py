#!/usr/bin/env python3
"""RT1 - ACCUSATION 13: the unit CHANGES between the baseline seasons and now.

On the visits where tot != 100 (the only ones that can tell the two apart), decide
COUNT vs PERCENT season by season, and find the year the source switched.
The engine compares 2026 against 2006 with one formula for both.
"""
import os, sys, collections
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import rt1_lib as L

CORE = ["u", "l1v", "l1m", "l2v", "l2m", "l3v", "l3m", "pv", "pm", "fu"]
ATT = ["u", "l1v", "l2v"]
DAN = ["l3v", "l3m", "pv", "pm", "fu"]


def close(a, b, tol=0.101):
    return abs(a - b) <= tol


def main():
    yrs = sorted({int(os.path.basename(f).rsplit("_", 1)[1][:4])
                  for f in os.listdir(L.FETCH) if f.startswith("c2_s1_v")})
    print(f"stage seasons fetched from the live API: {yrs}")
    rows = L.visit_table(years=set(yrs), with_stages=True)
    full = [r for r in rows if all(r.get(c) is not None for c in CORE)
            and all(r.get(c) is not None for c in ("tot", "attiva", "dannosa", "totale"))
            and r["tot"] > 0]
    print(f"{len(full)} visits with every stage column and every published column readable")
    print()
    for metric, cols in (("totale", CORE), ("attiva", ATT), ("dannosa", DAN)):
        print(f"===== {metric} : separating visits only (tot != 100 and stage sum > 0) =====")
        print(f"  {'year':>5} {'n':>5} {'PERCENT':>16} {'COUNT':>16}  verdict")
        tp = tc = tn = 0
        for y in yrs:
            sub = [r for r in full if r["year"] == y and r["tot"] != 100
                   and sum(r[c] for c in cols) > 0]
            if not sub:
                print(f"  {y:>5} {0:>5}  no separating visit")
                continue
            p = sum(1 for r in sub
                    if close(100.0 * sum(r[c] for c in cols) / r["tot"], r[metric]))
            c = sum(1 for r in sub if close(sum(r[c] for c in cols), r[metric]))
            tp += p
            tc += c
            tn += len(sub)
            v = ("PERCENT" if p > c else "COUNT" if c > p else "tie")
            print(f"  {y:>5} {len(sub):>5} {p:>6} ({100.0*p/len(sub):>5.1f}%) "
                  f"{c:>6} ({100.0*c/len(sub):>5.1f}%)  {v}")
        print(f"  TOTAL {tn:>5} {tp:>6} ({100.0*tp/tn:>5.1f}%) {tc:>6} "
              f"({100.0*tc/tn:>5.1f}%)")
        print()

    print("== consequence for the engine's own baseline ==")
    print("  di_observe.cell compares the 28-day window at as_of with the SAME calendar")
    print("  window in every season back to first_year=2006, using one formula: value/tot.")
    print("  On tot != 100 visits that formula is right in the early seasons and wrong now.")
    early = [r for r in full if r["year"] <= 2015 and r["tot"] != 100]
    late = [r for r in full if r["year"] >= 2020 and r["tot"] != 100]
    print(f"  visits with tot != 100 in the fetched seasons: "
          f"{len(early)} up to 2015, {len(late)} from 2020")


if __name__ == "__main__":
    main()
