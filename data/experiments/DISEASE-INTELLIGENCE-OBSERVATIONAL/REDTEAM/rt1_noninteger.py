#!/usr/bin/env python3
"""RT1 - ACCUSATION 4: the non-integer infestation values.

A "count of drupes" cannot be 0.2. What are these rows, what is their tot, and do they
survive the engine's sanity rules and enter a published pool?
"""
import os, sys, collections
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import rt1_lib as L


def main():
    rows = L.visit_table()
    for c in ("attiva", "dannosa", "totale"):
        have = [r for r in rows if r[c] is not None]
        ni = [r for r in have if r[c] != int(r[c])]
        print(f"{c}: non-integer in {len(ni)} of {len(have)} readable "
              f"({100.0*len(ni)/len(have):.3f}%)")
        tots = collections.Counter(r["tot"] for r in ni)
        print(f"   their tot values, most common: "
              f"{[(f'{v:g}' if v is not None else 'null', k) for v, k in tots.most_common(8)]}")
        at100 = sum(1 for r in ni if r["tot"] == 100)
        print(f"   of those, tot == 100 in {at100} of {len(ni)}")
        survive = [r for r in ni if r["tot"] and r["tot"] > 0 and 0 <= r[c] <= r["tot"]]
        print(f"   passing the engine's sanity rules (tot>0, 0<=v<=tot): "
              f"{len(survive)} of {len(ni)}")
        yrs = collections.Counter(r["year"] for r in ni)
        print(f"   by season: {sorted(yrs.items())}")
        ex = sorted(ni, key=lambda r: -(r[c] % 1))[:5]
        for r in ex:
            print(f"     e.g. {r['date']} field {r['id_field']} {r['province']} "
                  f"org={r['org']} tot={r['tot']:g} {c}={r[c]}")
        print()

    print("== do non-integers land inside the 2026 publication window? ==")
    win = [r for r in rows if r["date"] and "2026-08-10" <= r["date"] <= "2026-09-06"]
    print(f"  visits in 2026-08-10..2026-09-06: {len(win)}")
    for c in ("attiva", "dannosa", "totale"):
        ni = [r for r in win if r[c] is not None and r[c] != int(r[c])]
        print(f"  {c}: {len(ni)} non-integer in the window")
        for r in ni:
            print(f"     {r['date']} field {r['id_field']} {r['province']} "
                  f"tot={r['tot']:g} {c}={r[c]}")
    print()

    print("== engine truncation: pooled numerator is int(num) ==")
    print("  di_observe.pooled does num += c  then reports int(num).")
    print("  Any fractional value in a pool is silently truncated in the printed "
          "numerator while the rate uses the untruncated sum.")


if __name__ == "__main__":
    main()
