#!/usr/bin/env python3
"""RT2-B4 — is the panel rotation real, and does the class survive a MATCHED-GROVE baseline?

B3 found the 2026 window panel shares a median of 0 groves with the typical baseline season in
Livorno, Pistoia and Prato. Two things must be established before that is an accusation:

  A. IS id_field STABLE ACROSS YEARS, or does the source re-issue it every season?
     Measured as Jaccard by year-lag. A re-issued id gives ~0 at every lag including lag 1;
     genuine turnover decays with lag.

  B. THE COUNTERFACTUAL. Recompute the class using, for each baseline season, ONLY the groves
     that season shares with the 2026 window panel (paired comparison, same places). Any class
     that changes was a comparison of places dressed as a comparison of years.

  C. A CHEAPER, STRONGER VARIANT. Restrict BOTH sides to the groves present in the window in
     2026 AND in at least MIN_BASE prior seasons — a genuine longitudinal panel — and see how
     many provinces still have >= 8 such groves.
"""
import json, glob, os, sys, collections, datetime as dt
from statistics import median

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
CASE = os.path.join(ROOT, "CASES", "OLIVO-BACTROCERA-TOSCANA")
VAR = -1002
LO, HI = dt.date(2026, 8, 10), dt.date(2026, 9, 6)
MIN_SITES, MIN_BASE, HIGH_P, LOW_P = 8, 5, 0.80, 0.20


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


def cls(v, base):
    if len(base) < MIN_BASE:
        return "UNKNOWN_NO_BASELINE", None
    below = sum(1 for b in base if b < v) + 0.5 * sum(1 for b in base if b == v)
    p = below / len(base)
    return ("HIGHER" if p >= HIGH_P else ("LOWER" if p <= LOW_P else "TYPICAL")), round(p, 3)


if __name__ == "__main__":
    rows = load()
    byp = collections.defaultdict(list)
    for r in rows:
        if r.get("nome_area"):
            byp[r["nome_area"]].append(r)

    def sites(p, y, only=None):
        try:
            lo, hi = LO.replace(year=y), HI.replace(year=y)
        except ValueError:
            return {}
        st = collections.defaultdict(list)
        for r in byp[p]:
            if lo <= r["_d"] <= hi and (only is None or r["id_field"] in only):
                st[r["id_field"]].append(r["_v"])
        return st

    # ---- A. id_field stability by lag, over the whole season, not just the window ---------
    print("A. IS id_field STABLE? Jaccard of the WHOLE-SEASON id_field set, by year lag")
    per_year = collections.defaultdict(set)
    for r in rows:
        per_year[r["_d"].year].add(r["id_field"])
    print(f"  {'lag':>4s} {'pairs':>6s} {'median Jaccard':>15s}")
    for lag in (1, 2, 3, 5, 10, 15, 20):
        js = [len(per_year[y] & per_year[y + lag]) / len(per_year[y] | per_year[y + lag])
              for y in range(2006, 2027 - lag) if per_year[y] and per_year[y + lag]]
        if js:
            print(f"  {lag:4d} {len(js):6d} {median(js):15.3f}")
    print(f"  distinct id_field ever seen: {len(set().union(*per_year.values()))}; "
          f"per season min {min(len(v) for v in per_year.values())} "
          f"max {max(len(v) for v in per_year.values())}")

    # ---- B. matched-grove baseline -------------------------------------------------------
    print("\nB. MATCHED-GROVE BASELINE — each baseline season restricted to the groves it "
          "shares with the 2026 window panel")
    print(f"  {'province':14s} {'cur':>7s} {'class AS PUBLISHED':>19s} {'base_n':>7s} "
          f"{'class MATCHED':>14s} {'matched base_n':>15s} {'shared groves used':>19s}")
    changed = []
    for p in sorted(byp):
        cs = sites(p, 2026)
        if len(cs) < MIN_SITES:
            continue
        cur_set = set(cs)
        mx = [max(v) for v in cs.values()]
        cur = sum(1 for v in mx if v > 0) / len(mx)
        pub, mat, shared = [], [], []
        for y in range(2006, 2026):
            b = sites(p, y)
            if len(b) >= MIN_SITES:
                m = [max(v) for v in b.values()]
                pub.append(sum(1 for v in m if v > 0) / len(m))
            bm = sites(p, y, only=cur_set)
            if len(bm) >= MIN_SITES:
                m = [max(v) for v in bm.values()]
                mat.append(sum(1 for v in m if v > 0) / len(m))
                shared.append(len(bm))
        c1, _ = cls(cur, pub)
        c2, _ = cls(cur, mat)
        if c1 != c2:
            changed.append((p, c1, c2))
        print(f"  {p:14s} {cur:7.4f} {c1:>19s} {len(pub):7d} {c2:>14s} {len(mat):15d} "
              f"{(median(shared) if shared else 0):19.1f}")
    print(f"  provinces whose class changes under a matched-grove baseline: "
          f"{len(changed)} -> {changed}")

    # ---- C. a real longitudinal panel ----------------------------------------------------
    print("\nC. HOW BIG IS THE GENUINELY LONGITUDINAL PANEL? groves present in the 10 Aug-6 Sep "
          "window in 2026 AND in >= 5 prior seasons")
    print(f"  {'province':14s} {'2026 sites':>10s} {'also in >=5 prior seasons':>26s} "
          f"{'>= MIN_SITES(8)?':>17s}")
    for p in sorted(byp):
        cs = set(sites(p, 2026))
        if not cs:
            continue
        cnt = collections.Counter()
        for y in range(2006, 2026):
            for f in sites(p, y):
                if f in cs:
                    cnt[f] += 1
        long_ = [f for f, c in cnt.items() if c >= MIN_BASE]
        print(f"  {p:14s} {len(cs):10d} {len(long_):26d} "
              f"{('YES' if len(long_) >= MIN_SITES else 'NO'):>17s}")
