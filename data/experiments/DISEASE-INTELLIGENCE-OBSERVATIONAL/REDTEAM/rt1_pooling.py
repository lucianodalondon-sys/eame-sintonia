#!/usr/bin/env python3
"""RT1 - ACCUSATION 7: the pooled rate. Who actually makes the number?

sum(infested)/sum(sampled) over a 28-day window, per province, vs the mean and the median
of per-visit rates; and the concentration of the numerator in single groves and single
organisations.
"""
import os, sys, collections, statistics, datetime as dt
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import rt1_lib as L

METRIC = "attiva"
AS_OF = dt.date(2026, 9, 6)


def usable(rows, metric):
    return [r for r in rows if r["tot"] and r["tot"] > 0 and r[metric] is not None
            and 0 <= r[metric] <= r["tot"]]


def main():
    rows = L.visit_table()
    lo = (AS_OF - dt.timedelta(days=27)).isoformat()
    hi = AS_OF.isoformat()
    win = [r for r in rows if r["date"] and lo <= r["date"] <= hi]
    print(f"window {lo}..{hi}, metric {METRIC}\n")

    print(f"{'province':14s} {'n':>4} {'pooled%':>8} {'mean%':>8} {'median%':>8} "
          f"{'p90%':>7} {'max%':>7} {'zero visits':>12} {'top grove share of numerator':>30}")
    for prov in sorted({r["province"] for r in win if r["province"]}):
        u = usable([r for r in win if r["province"] == prov], METRIC)
        if not u:
            continue
        num = sum(r[METRIC] for r in u)
        den = sum(r["tot"] for r in u)
        per = sorted(100.0 * r[METRIC] / r["tot"] for r in u)
        zero = sum(1 for x in per if x == 0)
        bysite = collections.Counter()
        byorg = collections.Counter()
        for r in u:
            bysite[r["id_field"]] += r[METRIC]
            byorg[r["org"]] += r[METRIC]
        top = bysite.most_common(1)[0] if num else (None, 0)
        top3 = sum(v for _, v in bysite.most_common(3))
        p90 = per[int(0.9 * (len(per) - 1))]
        print(f"{prov:14s} {len(u):>4} {100.0*num/den:>8.4f} {statistics.mean(per):>8.4f} "
              f"{statistics.median(per):>8.4f} {p90:>7.3f} {per[-1]:>7.3f} "
              f"{zero:>5} of {len(per):<4} "
              f"grove {top[0]} = {100.0*top[1]/num if num else 0:>5.1f}% "
              f"(top3 {100.0*top3/num if num else 0:.1f}%)")
    print()

    print("== per province: how many visits carry the whole numerator ==")
    for prov in sorted({r["province"] for r in win if r["province"]}):
        u = usable([r for r in win if r["province"] == prov], METRIC)
        num = sum(r[METRIC] for r in u)
        if not num:
            print(f"  {prov:14s} numerator is 0 across {len(u)} visits")
            continue
        vals = sorted((r[METRIC] for r in u), reverse=True)
        run = 0
        k = 0
        for v in vals:
            run += v
            k += 1
            if run >= 0.5 * num:
                break
        nz = sum(1 for v in vals if v > 0)
        print(f"  {prov:14s} {k} of {len(u)} visits carry half the numerator; "
              f"only {nz} visits are non-zero at all; numerator {num:g} drupes")
    print()

    print("== organisation concentration ==")
    for prov in ("Grosseto", "Firenze", "Siena", "Livorno", "Lucca"):
        u = usable([r for r in win if r["province"] == prov], METRIC)
        num = sum(r[METRIC] for r in u)
        byorg_n = collections.Counter()
        byorg_d = collections.Counter()
        for r in u:
            byorg_n[r["org"]] += r[METRIC]
            byorg_d[r["org"]] += r["tot"]
        print(f"  {prov}: numerator {num:g}")
        for o in sorted(byorg_d, key=lambda o: -byorg_d[o]):
            print(f"     {str(o):16s} {byorg_d[o]:>7g} drupes "
                  f"({100.0*byorg_d[o]/sum(byorg_d.values()):>5.1f}% of denominator), "
                  f"{byorg_n[o]:>6g} infested "
                  f"({100.0*byorg_n[o]/num if num else 0:>5.1f}% of numerator), "
                  f"own rate {100.0*byorg_n[o]/byorg_d[o]:.4f}%")
    print()

    print("== drop the single largest contributing grove and re-pool ==")
    for prov in sorted({r["province"] for r in win if r["province"]}):
        u = usable([r for r in win if r["province"] == prov], METRIC)
        num = sum(r[METRIC] for r in u)
        den = sum(r["tot"] for r in u)
        if not num or not den:
            continue
        bysite = collections.Counter()
        for r in u:
            bysite[r["id_field"]] += r[METRIC]
        top = bysite.most_common(1)[0][0]
        u2 = [r for r in u if r["id_field"] != top]
        n2 = sum(r[METRIC] for r in u2)
        d2 = sum(r["tot"] for r in u2)
        print(f"  {prov:14s} with grove {top}: {100.0*num/den:.4f}%   "
              f"without it: {100.0*n2/d2:.4f}%   "
              f"({100.0*(n2/d2)/(num/den)-100:+.1f}%)")


if __name__ == "__main__":
    main()
