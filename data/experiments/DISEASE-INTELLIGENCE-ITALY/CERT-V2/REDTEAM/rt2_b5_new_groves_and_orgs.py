#!/usr/bin/env python3
"""RT2-B5 — do NEWLY RECRUITED groves, and different ORGANISATIONS, read differently?

B4 established that the 2026 panel is largely new. That only matters if new groves score
differently from veteran ones. Two nuisance factors, both measured inside the same
province x 28-day window so the comparison is like-for-like:

  1. GROVE TENURE. Within one province-window, site incidence among groves appearing for the
     FIRST time in the archive vs groves with >= 3 prior seasons. Pooled over all seasons, and
     shown for 2026 alone.
  2. ORGANISATION. Within one province-window, site incidence by scouting organisation. If two
     crews walking the same province in the same four weeks return different numbers, the
     organisation mix is a confounder of the province series.
"""
import json, glob, os, sys, collections, datetime as dt
from statistics import median, mean

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
CASE = os.path.join(ROOT, "CASES", "OLIVO-BACTROCERA-TOSCANA")
VAR = -1002
LO, HI = dt.date(2026, 8, 10), dt.date(2026, 9, 6)


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
    rows = load()
    seen_before = collections.defaultdict(set)      # id_field -> set of seasons seen
    for r in rows:
        seen_before[r["id_field"]].add(r["_d"].year)

    # ---- 1. TENURE ----------------------------------------------------------------------
    print("1. GROVE TENURE inside the 10 Aug - 6 Sep window, pooled over 2006-2026")
    buckets = collections.defaultdict(lambda: [0, 0])
    per_year = collections.defaultdict(lambda: collections.defaultdict(lambda: [0, 0]))
    for y in range(2006, 2027):
        try:
            lo, hi = LO.replace(year=y), HI.replace(year=y)
        except ValueError:
            continue
        st = collections.defaultdict(list)
        for r in rows:
            if lo <= r["_d"] <= hi:
                st[r["id_field"]].append(r["_v"])
        for f, vs in st.items():
            prior = len([yy for yy in seen_before[f] if yy < y])
            b = "NEW_0_prior" if prior == 0 else ("1-2_prior" if prior <= 2 else
                                                  "3-5_prior" if prior <= 5 else ">5_prior")
            buckets[b][0] += 1
            buckets[b][1] += max(vs) > 0
            per_year[y][b][0] += 1
            per_year[y][b][1] += max(vs) > 0
    print(f"  {'tenure':13s} {'site-windows':>13s} {'positive':>9s} {'site incidence':>15s}")
    for b in ("NEW_0_prior", "1-2_prior", "3-5_prior", ">5_prior"):
        n, p = buckets[b]
        print(f"  {b:13s} {n:13d} {p:9d} {p/n:15.4f}" if n else f"  {b:13s} 0")

    print("\n   the same split, season by season (site incidence; n in brackets)")
    print(f"  {'year':>5s} " + " ".join(f"{b:>16s}" for b in
                                        ("NEW_0_prior", "1-2_prior", "3-5_prior", ">5_prior")))
    for y in sorted(per_year):
        line = f"  {y:5d} "
        for b in ("NEW_0_prior", "1-2_prior", "3-5_prior", ">5_prior"):
            n, p = per_year[y][b]
            line += f"{(f'{p/n:.3f}({n})' if n else '-'):>17s}"
        print(line)

    # paired within-season test: does NEW read lower than veteran in the same season?
    pairs = [(per_year[y]["NEW_0_prior"], per_year[y][">5_prior"]) for y in per_year]
    ok = [(a[1] / a[0], b[1] / b[0]) for a, b in pairs if a[0] >= 8 and b[0] >= 8]
    if ok:
        low = sum(1 for a, b in ok if a < b)
        print(f"\n   seasons where NEW groves read LOWER than >5-prior groves: {low}/{len(ok)}")
        print(f"   mean difference (NEW - veteran) = {mean(a-b for a, b in ok):+.4f}")

    # ---- 2. ORGANISATION ----------------------------------------------------------------
    print("\n2. ORGANISATION effect inside one province x one 28-day window")
    print("   (only province-season-windows scouted by >= 2 organisations, each with >= 8 sites)")
    diffs = []
    shown = 0
    for y in range(2006, 2027):
        try:
            lo, hi = LO.replace(year=y), HI.replace(year=y)
        except ValueError:
            continue
        pw = collections.defaultdict(lambda: collections.defaultdict(
            lambda: collections.defaultdict(list)))
        for r in rows:
            if lo <= r["_d"] <= hi and r.get("nome_area") and r.get("org_name"):
                pw[r["nome_area"]][r["org_name"]][r["id_field"]].append(r["_v"])
        for p, orgs in pw.items():
            big = {o: s for o, s in orgs.items() if len(s) >= 8}
            if len(big) < 2:
                continue
            inc = {o: sum(1 for v in s.values() if max(v) > 0) / len(s)
                   for o, s in big.items()}
            lo_o = min(inc, key=inc.get); hi_o = max(inc, key=inc.get)
            diffs.append(inc[hi_o] - inc[lo_o])
            if shown < 20:
                print(f"   {y} {p:14s} " + "  ".join(
                    f"{o}={inc[o]:.3f}(n{len(big[o])})" for o in sorted(inc, key=inc.get)))
                shown += 1
    if diffs:
        print(f"\n   province-windows with >=2 organisations of >=8 sites: {len(diffs)}")
        print(f"   spread between the highest- and lowest-reading organisation in the SAME "
              f"province and SAME four weeks: median {median(diffs):.3f}, max {max(diffs):.3f}")

    # ---- 3. 2026 window, per province, split by tenure -----------------------------------
    print("\n3. THE PUBLISHED 2026 WINDOW, split by grove tenure")
    st = collections.defaultdict(lambda: collections.defaultdict(list))
    for r in rows:
        if LO <= r["_d"] <= HI and r.get("nome_area"):
            st[r["nome_area"]][r["id_field"]].append(r["_v"])
    print(f"  {'province':14s} {'NEW n':>6s} {'NEW inc':>8s} {'VET(>=3 prior) n':>17s} "
          f"{'VET inc':>8s}")
    for p in sorted(st):
        new = [f for f in st[p] if len([y for y in seen_before[f] if y < 2026]) == 0]
        vet = [f for f in st[p] if len([y for y in seen_before[f] if y < 2026]) >= 3]
        f1 = (sum(1 for f in new if max(st[p][f]) > 0) / len(new)) if new else float("nan")
        f2 = (sum(1 for f in vet if max(st[p][f]) > 0) / len(vet)) if vet else float("nan")
        print(f"  {p:14s} {len(new):6d} {f1:8.3f} {len(vet):17d} {f2:8.3f}")
