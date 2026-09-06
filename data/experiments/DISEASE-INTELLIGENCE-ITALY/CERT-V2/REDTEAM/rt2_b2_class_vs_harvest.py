#!/usr/bin/env python3
"""RT2-B2 — does the published class on 6 September say anything about the CAMPAIGN?

An olive grower's decision on 6 September is about the last larvicide/adulticide rounds before
harvest. So the only agronomically interesting question about "LOWER_THAN_USUAL on 6 September"
is whether the seasons that scored LOWER on 6 September ended with less damage than the seasons
that scored TYPICAL or HIGHER.

Method, entirely inside the engine's own definitions:
  * run the engine's hindcast at 6 September of every season 2006..2025 (walk-forward baseline,
    prior seasons only), giving the class it WOULD have published;
  * for each (province, season) compute the SEASON-END outcome = site incidence in the last 28
    days that season actually has, and its rank among that province's seasons;
  * cross-tabulate.
A class with no relation to the season end is a nowcast of one month and must be sold as that.
"""
import json, glob, os, sys, collections, datetime as dt
from statistics import mean, median

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "ENGINE"))
sys.path.insert(0, os.path.join(ROOT, "CASES"))
import current_pressure as cp
import province_agreement as pa

CASE = os.path.join(ROOT, "CASES", "OLIVO-BACTROCERA-TOSCANA")
VAR = -1002


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
            if v is None or not r.get("date") or not den.get(str(r["id_survey"])):
                continue
            try:
                r["_d"] = dt.date.fromisoformat(r["date"])
            except ValueError:
                continue
            r["_v"] = v
            rows.append(r)
    return rows


if __name__ == "__main__":
    years = list(range(2006, 2026))
    h = cp.hindcast(CASE, VAR, 9, 6, years)

    rows = load()
    byp = collections.defaultdict(list)
    for r in rows:
        if r.get("nome_area"):
            byp[r["nome_area"]].append(r)

    end = collections.defaultdict(dict)
    for p in byp:
        for y in years:
            ds = [r["_d"] for r in byp[p] if r["_d"].year == y]
            if not ds:
                continue
            last = max(ds)
            st = collections.defaultdict(list)
            for r in byp[p]:
                if last - dt.timedelta(days=27) <= r["_d"] <= last:
                    st[r["id_field"]].append(r["_v"])
            if len(st) >= 8:
                m = [max(v) for v in st.values()]
                end[p][y] = (sum(1 for v in m if v > 0) / len(m), last)

    tab = collections.defaultdict(list)
    detail = []
    for y in years:
        for p, s in h.get(y, {}).items():
            if p in end and y in end[p]:
                tab[s].append(end[p][y][0])
                detail.append((p, y, s, end[p][y][0], end[p][y][1]))
    print("SEASON-END SITE INCIDENCE, grouped by the class the engine would have published "
          "on 6 September of the same season")
    print(f"  {'class published 6 Sep':24s} {'n cells':>8s} {'median season-end incidence':>28s} "
          f"{'min':>7s} {'max':>7s}")
    for s in sorted(tab, key=lambda k: -len(tab[k])):
        v = sorted(tab[s])
        print(f"  {s:24s} {len(v):8d} {median(v):28.3f} {v[0]:7.3f} {v[-1]:7.3f}")

    # rank-correlation form, within province so provincial level differences cannot carry it
    rank = {cp.LOWER: 0, cp.TYPICAL: 1, cp.HIGHER: 2}
    rs = []
    print(f"\n  {'province':14s} {'n seasons':>9s} {'rho(class 6Sep, season-end incidence)':>38s}")
    for p in sorted(byp):
        xs = [(rank[s], e) for (pp, y, s, e, _) in detail if pp == p and s in rank]
        if len(xs) >= 8:
            r = pa.spear([a for a, _ in xs], [b for _, b in xs])
            rs.append(r)
            print(f"  {p:14s} {len(xs):9d} {r:38.3f}")
    if rs:
        print(f"  mean rho = {mean(rs):+.3f} over {len(rs)} provinces")

    # the operational question: how often does LOWER on 6 Sep end in the province's worst third?
    worst = 0
    n_low = 0
    for p in sorted(byp):
        vals = sorted(end[p].values())
        if len(vals) < 6:
            continue
        cut = sorted(v for v, _ in end[p].values())[int(0.66 * len(end[p]))]
        for (pp, y, s, e, _) in detail:
            if pp == p and s == cp.LOWER:
                n_low += 1
                worst += e >= cut
    print(f"\n  cells published LOWER_THAN_USUAL on 6 September that nevertheless ended the "
          f"season in that province's WORST THIRD: {worst}/{n_low}")

    # and how many DAYS of campaign remain after 6 September
    rem = [(e[1] - dt.date(y, 9, 6)).days for p in end for y, e in end[p].items()]
    print(f"  days of scouting still to come after 6 September, over {len(rem)} province-seasons:"
          f" median {median(rem)}, min {min(rem)}, max {max(rem)}")
