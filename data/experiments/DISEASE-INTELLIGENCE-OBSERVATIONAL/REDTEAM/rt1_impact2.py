#!/usr/bin/env python3
"""RT1 - the impact, with the era rule the stage data proves:
     seasons 2006-2019  the value is a COUNT   -> infested drupe-equivalents = value
     seasons 2020-2026  the value is a PERCENT -> infested drupe-equivalents = value*tot/100
The engine uses the COUNT rule for all 21 seasons.
"""
import os, sys, collections, statistics, datetime as dt
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import rt1_lib as L

SWITCH = 2020


def band(p):
    if p is None:
        return "NONE"
    if p == 0:
        return "white"
    if p < 0.01:
        return "NO_BAND"
    if p < 6:
        return "green"
    if p < 10:
        return "yellow"
    return "red"


def pools(rs, metric):
    """(engine_rate, era_correct_rate, n, den) on the engine's own usable set."""
    u = [r for r in rs if r["tot"] and r["tot"] > 0 and r[metric] is not None
         and 0 <= r[metric] <= r["tot"]]
    if not u:
        return None
    den = sum(r["tot"] for r in u)
    eng = 100.0 * sum(r[metric] for r in u) / den
    cor = 100.0 * sum((r[metric] * r["tot"] / 100.0) if r["year"] >= SWITCH else r[metric]
                      for r in u) / den
    return eng, cor, len(u), den


def main():
    rows = L.visit_table()
    as_of = dt.date(2026, 9, 6)
    lo = (as_of - dt.timedelta(days=27)).isoformat()
    hi = as_of.isoformat()

    print("== the published window 2026-08-10..2026-09-06 ==")
    print(f"  {'province':14s} {'metric':8s} {'engine %':>9} {'band':>7} "
          f"{'era-correct %':>14} {'band':>7} {'ratio':>7}")
    for metric in ("attiva", "dannosa", "totale"):
        for prov in sorted({r["province"] for r in rows if r["province"]}):
            w = [r for r in rows if r["province"] == prov and r["date"]
                 and lo <= r["date"] <= hi]
            p = pools(w, metric)
            if not p:
                continue
            e, c, n, d = p
            flag = "  <-- BAND CHANGES" if band(e) != band(c) else ""
            print(f"  {prov:14s} {metric:8s} {e:>9.4f} {band(e):>7} {c:>14.4f} "
                  f"{band(c):>7} {c/e if e else 0:>7.3f}{flag}")
        print()

    print("== every gate-passing province x 28-day window in the archive ==")
    byprov = collections.defaultdict(list)
    for r in rows:
        if r["province"] and r["date"]:
            byprov[r["province"]].append(r)
    for metric in ("attiva", "dannosa", "totale"):
        cells = flips = 0
        post = post_flips = 0
        worst = []
        for prov, rs in byprov.items():
            for d in sorted({r["date"] for r in rs}):
                h = dt.date.fromisoformat(d)
                l = (h - dt.timedelta(days=27)).isoformat()
                w = [r for r in rs if l <= r["date"] <= d]
                p = pools(w, metric)
                if not p:
                    continue
                e, c, n, den = p
                if n < 8 or den < 400:
                    continue
                cells += 1
                if h.year >= SWITCH:
                    post += 1
                if band(e) != band(c):
                    flips += 1
                    if h.year >= SWITCH:
                        post_flips += 1
                    worst.append((abs(c - e), prov, d, e, c, n, den))
        worst.sort(key=lambda t: -t[0])
        print(f"  {metric}: {cells} gate-passing windows, band differs in {flips} "
              f"({100.0*flips/cells:.3f}%); of the {post} windows in 2020+, "
              f"{post_flips} differ ({100.0*post_flips/post:.3f}%)")
        for x in worst[:8]:
            print(f"     {x[1]:14s} ending {x[2]}  engine {x[3]:.4f}% [{band(x[3])}] "
                  f"vs era-correct {x[4]:.4f}% [{band(x[4])}]  n={x[5]} den={int(x[6])}")
        print()

    print("== the baseline itself: 2026 (percent) compared against 2006-2019 (count) ==")
    print("  share of each season's visits with tot != 100, per province, since a pool of")
    print("  tot==100 visits alone is immune")
    for prov in sorted(byprov):
        line = []
        for y in range(2006, 2027):
            v = [r for r in byprov[prov] if r["year"] == y and r["tot"] is not None]
            if not v:
                line.append("  . ")
                continue
            k = sum(1 for r in v if r["tot"] != 100)
            line.append(f"{100.0*k/len(v):4.0f}")
        print(f"  {prov:14s} " + " ".join(line))
    print("  (columns 2006..2026, % of visits with tot != 100)")


if __name__ == "__main__":
    main()
