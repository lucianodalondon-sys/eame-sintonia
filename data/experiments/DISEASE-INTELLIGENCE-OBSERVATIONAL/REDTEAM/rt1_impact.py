#!/usr/bin/env python3
"""RT1 - what the percent finding does to the numbers the engine publishes.

If the source value is already a percentage of tot, then:
  the correct pooled rate is  sum(value_i * tot_i) / sum(tot_i)      (tot-weighted mean %)
  the engine publishes        100 * sum(value_i) / sum(tot_i)
They coincide only where every tot in the pool is 100.

Also: what the sanity rule value<=tot throws away, and whether it throws away the worst.
"""
import os, sys, collections, statistics, datetime as dt
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import rt1_lib as L

METRIC = "attiva"


def pool(rows, metric):
    """engine rate, percent-reading rate, mean of per-visit values, median."""
    use = [r for r in rows
           if r["tot"] is not None and r["tot"] > 0 and r[metric] is not None
           and 0 <= r[metric] <= r["tot"]]                 # the engine's own gate
    if not use:
        return None
    num = sum(r[metric] for r in use)
    den = sum(r["tot"] for r in use)
    engine = 100.0 * num / den
    pct_w = sum(r[metric] * r["tot"] for r in use) / den   # tot-weighted mean of percents
    per = [r[metric] for r in use]                         # each already a percent
    return {"n": len(use), "engine_pct": engine, "percent_reading_pct": pct_w,
            "unweighted_mean_pct": statistics.mean(per),
            "median_pct": statistics.median(per),
            "drupes": den}


def main():
    rows = L.visit_table()
    as_of = dt.date(2026, 9, 6)
    lo = (as_of - dt.timedelta(days=27)).isoformat()
    hi = as_of.isoformat()
    win = [r for r in rows if r["date"] and lo <= r["date"] <= hi]
    print(f"== the published window {lo}..{hi}, metric {METRIC} ==")
    print(f"  {'province':14s} {'n':>5} {'engine %':>9} {'percent-reading %':>18} "
          f"{'ratio':>7} {'mean of visits %':>17} {'median %':>9}")
    for prov in sorted({r["province"] for r in win if r["province"]}):
        p = pool([r for r in win if r["province"] == prov], METRIC)
        if not p:
            continue
        ratio = p["percent_reading_pct"] / p["engine_pct"] if p["engine_pct"] else float("nan")
        print(f"  {prov:14s} {p['n']:>5} {p['engine_pct']:>9.4f} "
              f"{p['percent_reading_pct']:>18.4f} {ratio:>7.3f} "
              f"{p['unweighted_mean_pct']:>17.4f} {p['median_pct']:>9.4f}")
    print()

    print("== whole archive, per season, metric totale ==")
    print(f"  {'year':>5} {'n':>6} {'engine %':>9} {'percent-reading %':>18} {'ratio':>7}")
    for y in sorted({r["year"] for r in rows if r["year"]}):
        p = pool([r for r in rows if r["year"] == y], "totale")
        if not p:
            continue
        ratio = p["percent_reading_pct"] / p["engine_pct"] if p["engine_pct"] else 0
        print(f"  {y:>5} {p['n']:>6} {p['engine_pct']:>9.4f} "
              f"{p['percent_reading_pct']:>18.4f} {ratio:>7.3f}")
    print()

    print("== what the sanity rule value<=tot throws away ==")
    for metric in ("attiva", "dannosa", "totale"):
        drop = [r for r in rows if r["tot"] is not None and r["tot"] > 0
                and r[metric] is not None and r[metric] > r["tot"]]
        keep = [r for r in rows if r["tot"] is not None and r["tot"] > 0
                and r[metric] is not None and 0 <= r[metric] <= r["tot"]]
        if not drop:
            continue
        dv = [r[metric] for r in drop]
        kv = [r[metric] for r in keep]
        print(f"  {metric}: dropped {len(drop)} of {len(drop)+len(keep)}; "
              f"median value dropped {statistics.median(dv):g} vs median kept "
              f"{statistics.median(kv):g}")
        tots = collections.Counter(r["tot"] for r in drop)
        print(f"     tot of the dropped rows: "
              f"{[(f'{v:g}', k) for v, k in tots.most_common(6)]}")
    print()

    print("== how much of the archive is affected: pools that contain a tot != 100 ==")
    byprovyear = collections.defaultdict(list)
    for r in rows:
        if r["province"] and r["year"]:
            byprovyear[(r["province"], r["year"])].append(r)
    dirty = sum(1 for k, v in byprovyear.items()
                if any(r["tot"] not in (None, 100) for r in v))
    print(f"  province-seasons that contain at least one visit with tot != 100: "
          f"{dirty} of {len(byprovyear)}")
    worst = []
    for k, v in byprovyear.items():
        p = pool(v, "totale")
        if p and p["engine_pct"] > 0:
            worst.append((p["percent_reading_pct"] / p["engine_pct"], k, p))
    worst.sort(key=lambda t: -t[0])
    print("  the 10 province-seasons where the two readings diverge most:")
    for ratio, k, p in worst[:10]:
        print(f"    {k[0]:14s} {k[1]} n={p['n']:>4} engine {p['engine_pct']:>8.4f}% "
              f"vs percent-reading {p['percent_reading_pct']:>8.4f}%  x{ratio:.2f}")


if __name__ == "__main__":
    main()
