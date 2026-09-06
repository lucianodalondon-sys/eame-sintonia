#!/usr/bin/env python3
"""RT2-B1 — the baseline is the SAME CALENDAR window, but not the same PHENOLOGICAL window.

Olive-fly damage climbs monotonically through the campaign: 0.7% of visits positive in ISO week
27, 62% in week 43 (measured in rt2_a4). The published window 10 Aug - 6 Sep sits on the steep
part of that ramp, so the value depends on WHEN INSIDE THE WINDOW the visits happened.

If the 2026 visits inside the window fall earlier than the baseline seasons' visits inside the
SAME window, part of "LOWER_THAN_USUAL" is calendar, not biology. This measures it three ways:
  1. mean ISO week of the visits inside the window, current season vs each baseline season;
  2. the counterfactual: re-weight the baseline seasons to the 2026 within-window week mix;
  3. the season-onset date (first date the province passes 10% site incidence), per season,
     to show how far the campaign's own timing moves between years.
"""
import json, glob, os, sys, collections, datetime as dt
from statistics import mean, median

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
CASE = os.path.join(ROOT, "CASES", "OLIVO-BACTROCERA-TOSCANA")
VAR, ASOF, WIN = -1002, dt.date(2026, 9, 6), 28


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
            if v is None or not r.get("date"):
                continue
            if not den.get(str(r["id_survey"])):      # engine's own denominator guard
                continue
            try:
                r["_d"] = dt.date.fromisoformat(r["date"])
            except ValueError:
                continue
            r["_v"] = v
            rows.append(r)
    return rows


def window(rows, lo, hi):
    st = collections.defaultdict(list)
    wk = collections.Counter()
    for r in rows:
        if lo <= r["_d"] <= hi:
            st[r["id_field"]].append(r["_v"])
            wk[r["_d"].isocalendar()[1]] += 1
    return st, wk


if __name__ == "__main__":
    rows = load()
    byp = collections.defaultdict(list)
    for r in rows:
        if r.get("nome_area"):
            byp[r["nome_area"]].append(r)
    lo, hi = ASOF - dt.timedelta(days=WIN - 1), ASOF

    print(f"WINDOW {lo}..{hi}  = ISO weeks "
          f"{lo.isocalendar()[1]}..{hi.isocalendar()[1]}")
    print("\n1. MEAN ISO WEEK OF THE VISITS INSIDE THE WINDOW, per province per season")
    print(f"  {'province':14s} {'2026 meanwk':>11s} {'baseline meanwk (median of 20)':>31s} "
          f"{'2026 shift in weeks':>20s}")
    shifts = {}
    for p in sorted(byp):
        st, wk = window(byp[p], lo, hi)
        if not wk:
            continue
        cur = sum(w * n for w, n in wk.items()) / sum(wk.values())
        base = []
        for y in range(2006, 2026):
            try:
                blo, bhi = lo.replace(year=y), hi.replace(year=y)
            except ValueError:
                continue
            _, bwk = window(byp[p], blo, bhi)
            if sum(bwk.values()) >= 8:
                base.append(sum(w * n for w, n in bwk.items()) / sum(bwk.values()))
        if len(base) >= 5:
            shifts[p] = cur - median(base)
            print(f"  {p:14s} {cur:11.2f} {median(base):31.2f} {cur-median(base):+20.2f}")
    if shifts:
        print(f"  mean |shift| = {mean(abs(v) for v in shifts.values()):.2f} weeks")

    print("\n2. THE WEEK-MIX COUNTERFACTUAL — baseline incidence recomputed using only the "
          "\n   ISO weeks 2026 actually has inside the window (like-for-like calendar position)")
    print(f"  {'province':14s} {'cur':>7s} {'base med AS PUBLISHED':>22s} "
          f"{'base med SAME-WEEKS':>20s} {'class as published':>20s} {'class same-weeks':>18s}")
    for p in sorted(byp):
        st, wk = window(byp[p], lo, hi)
        if len(st) < 8:
            continue
        mx = [max(v) for v in st.values()]
        cur = sum(1 for v in mx if v > 0) / len(mx)
        cur_weeks = set(wk)
        pub, same = [], []
        for y in range(2006, 2026):
            try:
                blo, bhi = lo.replace(year=y), hi.replace(year=y)
            except ValueError:
                continue
            bst, _ = window(byp[p], blo, bhi)
            if len(bst) >= 8:
                bm = [max(v) for v in bst.values()]
                pub.append(sum(1 for v in bm if v > 0) / len(bm))
            # same-weeks version
            s2 = collections.defaultdict(list)
            for r in byp[p]:
                if r["_d"].year == y and r["_d"].isocalendar()[1] in cur_weeks:
                    s2[r["id_field"]].append(r["_v"])
            if len(s2) >= 8:
                bm = [max(v) for v in s2.values()]
                same.append(sum(1 for v in bm if v > 0) / len(bm))

        def cls(v, b):
            if len(b) < 5:
                return "UNKNOWN_NO_BASELINE"
            below = sum(1 for x in b if x < v) + 0.5 * sum(1 for x in b if x == v)
            q = below / len(b)
            return "HIGHER" if q >= 0.80 else ("LOWER" if q <= 0.20 else "TYPICAL")
        print(f"  {p:14s} {cur:7.4f} {median(pub) if pub else float('nan'):22.4f} "
              f"{median(same) if same else float('nan'):20.4f} "
              f"{cls(cur, pub):>20s} {cls(cur, same):>18s}")

    print("\n3. HOW FAR DOES THE CAMPAIGN'S OWN TIMING MOVE BETWEEN SEASONS?")
    print("   first date each province reaches site-incidence >= 0.10 (rolling 14 days)")
    print(f"  {'province':14s} " + " ".join(f"{y%100:>3d}" for y in range(2006, 2027)))
    for p in sorted(byp):
        cells = []
        for y in range(2006, 2027):
            first = None
            days = sorted({r["_d"] for r in byp[p] if r["_d"].year == y})
            for d in days:
                st = collections.defaultdict(list)
                for r in byp[p]:
                    if d - dt.timedelta(days=13) <= r["_d"] <= d:
                        st[r["id_field"]].append(r["_v"])
                if len(st) >= 8:
                    m = [max(v) for v in st.values()]
                    if sum(1 for v in m if v > 0) / len(m) >= 0.10:
                        first = d
                        break
            cells.append(f"{first.timetuple().tm_yday if first else 0:>3d}")
        print(f"  {p:14s} " + " ".join(cells))
    print("   (day-of-year of first 10% incidence; 0 = never reached that season)")
