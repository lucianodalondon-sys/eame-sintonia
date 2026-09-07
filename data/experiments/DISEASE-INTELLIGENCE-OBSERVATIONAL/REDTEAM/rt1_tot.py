#!/usr/bin/env python3
"""RT1 - ACCUSATION 3: is `tot` really the sample size?

Distribution of tot, its behaviour where it is not 100, and whether the infestation
columns behave like counts out of it.
"""
import os, sys, collections, statistics
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import rt1_lib as L


def main():
    rows = L.visit_table()
    n = len(rows)
    print(f"visits in the archive: {n}")
    have = [r for r in rows if r["tot"] is not None]
    print(f"  tot readable: {len(have)}")
    c = collections.Counter(r["tot"] for r in have)
    print(f"  distinct tot values: {len(c)}")
    print("  the 25 most common:")
    for v, k in c.most_common(25):
        print(f"    tot={v:<10g} {k:>6} visits ({100.0*k/len(have):.3f}%)")
    non100 = [r for r in have if r["tot"] != 100]
    print(f"  tot != 100 in {len(non100)} of {len(have)} ({100.0*len(non100)/len(have):.2f}%)")
    print(f"  tot == 100 in {c.get(100.0,0)} of {len(have)} "
          f"({100.0*c.get(100.0,0)/len(have):.2f}%)")
    nonint = [r for r in have if r["tot"] != int(r["tot"])]
    print(f"  non-integer tot: {len(nonint)}")
    print()

    print("== where tot != 100 and != 0, do the infestation columns stay inside it? ==")
    grp = collections.defaultdict(lambda: {"n": 0, "over": 0, "maxratio": 0.0,
                                           "num": 0.0, "den": 0.0})
    for r in have:
        t = r["tot"]
        if t <= 0:
            continue
        tl = r["totale"]
        if tl is None:
            continue
        b = grp[t]
        b["n"] += 1
        b["num"] += tl
        b["den"] += t
        if tl > t:
            b["over"] += 1
        b["maxratio"] = max(b["maxratio"], tl / t)
    print(f"  {'tot':>8} {'visits':>7} {'totale>tot':>10} {'max totale/tot':>15} "
          f"{'pooled totale rate':>19}")
    for t in sorted(grp, key=lambda x: -grp[x]["n"])[:20]:
        b = grp[t]
        print(f"  {t:>8g} {b['n']:>7} {b['over']:>10} {b['maxratio']:>15.3f} "
              f"{100.0*b['num']/b['den']:>18.3f}%")
    print()

    print("== is tot a per-visit protocol constant, or does it drift per grove/org? ==")
    byorg = collections.defaultdict(collections.Counter)
    for r in have:
        byorg[r["org"]][r["tot"]] += 1
    for org in sorted(byorg, key=lambda o: -sum(byorg[o].values()))[:12]:
        cc = byorg[org]
        tot_n = sum(cc.values())
        top = cc.most_common(3)
        print(f"  org {str(org):10s} {tot_n:>6} visits, tot values "
              f"{[(f'{v:g}', k) for v, k in top]}, "
              f"share tot==100 {100.0*cc.get(100.0,0)/tot_n:.1f}%")
    print()

    print("== by season: median tot and the share at 100 ==")
    byyear = collections.defaultdict(list)
    for r in have:
        byyear[r["year"]].append(r["tot"])
    for y in sorted(byyear):
        v = byyear[y]
        at100 = sum(1 for x in v if x == 100)
        print(f"  {y} n={len(v):>5} median={statistics.median(v):>6g} "
              f"tot==100 {at100:>5}/{len(v)} ({100.0*at100/len(v):.1f}%)  "
              f"min={min(v):g} max={max(v):g}")
    print()

    print("== the large tot values: what are they? ==")
    big = sorted([r for r in have if r["tot"] > 100], key=lambda r: -r["tot"])[:15]
    for r in big:
        print(f"  tot={r['tot']:>7g} {r['date']} field {r['id_field']} {r['province']} "
              f"org={r['org']} attiva={r['attiva']} dannosa={r['dannosa']} "
              f"totale={r['totale']}")
    print()
    small = sorted([r for r in have if 0 < r["tot"] < 50], key=lambda r: r["tot"])[:15]
    print("== the small tot values ==")
    for r in small:
        print(f"  tot={r['tot']:>7g} {r['date']} field {r['id_field']} {r['province']} "
              f"org={r['org']} attiva={r['attiva']} dannosa={r['dannosa']} "
              f"totale={r['totale']}")


if __name__ == "__main__":
    main()
