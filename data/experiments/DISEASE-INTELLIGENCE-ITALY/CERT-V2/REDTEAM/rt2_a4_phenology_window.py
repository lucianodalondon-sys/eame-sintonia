#!/usr/bin/env python3
"""RT2-A4 — is a 28-day trailing window agronomically meaningful, and for which of the three?

Three separate questions, all answered from the archive:

  Q1  WHERE IS EACH ISSUE'S SEASON?  Visits and positives by ISO week, per case. One window
      length is applied to three pathosystems with different cycles; this shows the cycles.

  Q2  DOES THE WINDOW HAVE MEMORY?  -1002 dannosa counts damage already inflicted, including
      exit holes, which do not heal. If the variable ACCUMULATES within a season, a "trailing
      28 days" is not a nowcast of current pressure; it is season-to-date accumulation, and a
      LOWER reading on a fixed calendar date can mean a LATER season rather than a lighter one.
      Tested by asking whether a site's value ever falls back to zero after being positive.

  Q3  DOES THE 28-DAY WINDOW AT 6 SEPTEMBER PREDICT THE SEASON?  For each province and season,
      the incidence in the 10 Aug - 6 Sep window is compared with the incidence in the LAST
      28 days that season actually has. If the two are weakly related, "LOWER_THAN_USUAL on
      6 September" is a statement about one month, not about the campaign.
"""
import json, glob, os, sys, collections, datetime as dt
from statistics import mean

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "CASES"))
import province_agreement as pa           # for its spearman
import run_case as rc

CASES = [("OLIVE  x Bactrocera", "OLIVO-BACTROCERA-TOSCANA", -1002),
         ("VINE   x oidio", "VITE-OIDIO-TOSCANA", 39),
         ("WHEAT  x Septoria", "FRUMENTO-SEPTORIA-TOSCANA", 372)]


def num(v):
    if v in (None, ""):
        return None
    try:
        return float(str(v).replace(",", "."))
    except ValueError:
        return None


def rows_of(case, var):
    d = os.path.join(ROOT, "CASES", case)
    idx = json.load(open(os.path.join(d, "collection_index.json"), encoding="utf-8"))
    scale, _, _ = rc.build_scale(idx.get("codes") or [], var)
    out = []
    for fn in sorted(glob.glob(os.path.join(d, "RAW", f"*_v{var}_*.json"))):
        for r in json.load(open(fn, encoding="utf-8")):
            if not r.get("date"):
                continue
            try:
                r["_d"] = dt.date.fromisoformat(r["date"])
            except ValueError:
                continue
            if scale:
                s = scale.get(str(r.get("val")))
                r["_v"] = None if s is None else float(s["ordinal"])
            else:
                r["_v"] = num(r.get("val"))
            out.append(r)
    return out, bool(scale)


if __name__ == "__main__":
    print("Q1 — WHERE IS EACH SEASON? visits and share-of-visits-positive by ISO week")
    for name, case, var in CASES:
        rows, _ = rows_of(case, var)
        wk = collections.defaultdict(lambda: [0, 0])
        for r in rows:
            if r["_v"] is None:
                continue
            w = r["_d"].isocalendar()[1]
            wk[w][0] += 1
            wk[w][1] += r["_v"] > 0
        tot = sum(v[0] for v in wk.values())
        active = sorted(w for w in wk if wk[w][0] >= 0.005 * tot)
        print(f"\n  {name:22s} readable visits {tot}")
        print(f"    weeks holding >=0.5% of all visits: {min(active)}..{max(active)} "
              f"(calendar {dt.date.fromisocalendar(2025, min(active), 1)} .. "
              f"{dt.date.fromisocalendar(2025, max(active), 7)})")
        peak = max(wk, key=lambda w: wk[w][0])
        print(f"    peak visit week {peak}; a 28-day window is 4 weeks = "
              f"{4/len(active):.2f} of this issue's whole scouting season")
        line = "    "
        for w in range(min(active), max(active) + 1):
            n, p = wk.get(w, [0, 0])
            line += f"w{w}:{n}/{p} "
        print(line)

    # ---------------- Q2 : does dannosa ever go back down? --------------------------------
    print("\nQ2 — DOES THE PUBLISHED VARIABLE ACCUMULATE WITHIN A SEASON?")
    for name, case, var in CASES:
        rows, ordinal = rows_of(case, var)
        seq = collections.defaultdict(list)
        for r in rows:
            if r["_v"] is None:
                continue
            seq[(r["id_field"], r["_d"].year)].append((r["_d"], r["_v"]))
        up = down = flat = n = 0
        for k, s in seq.items():
            s.sort()
            if len(s) < 2:
                continue
            for (d0, v0), (d1, v1) in zip(s, s[1:]):
                n += 1
                if v1 > v0:
                    up += 1
                elif v1 < v0:
                    down += 1
                else:
                    flat += 1
        # the sharper test: once positive, does a site ever read zero again the same season?
        relapse = pos_sites = 0
        for k, s in seq.items():
            s.sort()
            vals = [v for _, v in s]
            if max(vals) <= 0:
                continue
            pos_sites += 1
            first = next(i for i, v in enumerate(vals) if v > 0)
            if any(v <= 0 for v in vals[first:]):
                relapse += 1
        print(f"  {name:22s} consecutive visit pairs {n}: rose {up}, fell {down}, flat {flat}")
        print(f"  {'':22s} site-seasons that went positive {pos_sites}; "
              f"of those, {relapse} later read zero again "
              f"({relapse/pos_sites:.3f} if >0)" if pos_sites else "")

    # ---------------- Q3 : does 6 Sep predict the campaign? -------------------------------
    print("\nQ3 — DOES THE 10 Aug - 6 Sep WINDOW PREDICT THE SEASON'S OWN LAST 28 DAYS?")
    name, case, var = CASES[0]
    rows, _ = rows_of(case, var)
    byp = collections.defaultdict(list)
    for r in rows:
        if r["_v"] is not None and r.get("nome_area"):
            byp[r["nome_area"]].append(r)

    def inc(rs, lo, hi):
        st = collections.defaultdict(list)
        for r in rs:
            if lo <= r["_d"] <= hi:
                st[r["id_field"]].append(r["_v"])
        if len(st) < 8:
            return None, len(st)
        mx = [max(v) for v in st.values()]
        return sum(1 for v in mx if v > 0) / len(mx), len(mx)

    print(f"  {'province':14s} {'seasons':>7s} {'rho(SepWindow, seasonEnd)':>26s}  "
          f"{'median Sep':>10s} {'median End':>10s}")
    allpairs = []
    for p in sorted(byp):
        xs, ys = [], []
        for y in sorted({r["_d"].year for r in byp[p]}):
            if y == 2026:
                continue
            a, _ = inc(byp[p], dt.date(y, 8, 10), dt.date(y, 9, 6))
            last = max(r["_d"] for r in byp[p] if r["_d"].year == y)
            b, _ = inc(byp[p], last - dt.timedelta(days=27), last)
            if a is not None and b is not None:
                xs.append(a); ys.append(b)
        if len(xs) >= 8:
            r_ = pa.spear(xs, ys)
            allpairs.append(r_)
            print(f"  {p:14s} {len(xs):7d} {r_:26.3f}  {sorted(xs)[len(xs)//2]:10.3f} "
                  f"{sorted(ys)[len(ys)//2]:10.3f}")
    if allpairs:
        print(f"  mean rho across {len(allpairs)} provinces = {mean(allpairs):+.3f}")
