#!/usr/bin/env python3
"""RT5 · accusation 4. The window is anchored on a calendar day, on a curve that
is climbing, and its right edge is truncated in the current season only.

  (a) SLIDE. as_of moves day by day from -28 to +28 and the ten verdicts are
      recomputed. A verdict that depends on which Sunday you ask is a verdict
      about the calendar, not about the groves.
  (b) RIGHT-EDGE TRUNCATION. The archive stops on 2026-09-04; the window runs to
      2026-09-06. The current window is short by however many days its province
      has no data for, while every matched season's window is complete. On a
      rising curve that biases the current side DOWN. Quantified by re-running
      the matched comparison with each baseline season truncated to the same
      elapsed-days coverage as the current one.
  (c) STEEPNESS. How many percentage points does the pooled rate move per week
      in this part of the season, per province, averaged over prior seasons?
"""
import os, sys, json, statistics, datetime as dt
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import rt5_lib as L

AS_OF = dt.date(2026, 9, 6)
idx, raw = L.get_index("ACTIVE_INFESTATION_COUNT")
P = L.PARAMS
BASE = {c["province"]: c for c in L.all_cells(idx, AS_OF)}

# ── (a) slide as_of ──────────────────────────────────────────────────────────
print("(a) SLIDING as_of.  h=historical_state  t=observed_trend")
print(f"{'as_of':>12} {'FI':>18} {'SI':>18} {'AR':>18} {'speak':>5} {'below':>5} "
      f"{'above':>5} {'dH':>3} {'dT':>3}  FI/SI/AR trend")
slide = []
for off in range(-28, 29):
    a = AS_OF + dt.timedelta(days=off)
    cells = {c["province"]: c for c in L.all_cells(idx, a)}
    h = {p: cells[p]["historical_state"] for p in idx.provinces}
    t = {p: cells[p]["observed_trend"] for p in idx.provinces}
    rec = {"offset": off, "as_of": a.isoformat(), "hist": h, "trend": t,
           "n_speaking": sum(1 for p in h if h[p] != "INSUFFICIENT_DATA"),
           "n_below": sum(1 for p in h if h[p] == "BELOW_HISTORICAL"),
           "n_above": sum(1 for p in h if h[p] == "ABOVE_HISTORICAL"),
           "dH": sum(1 for p in h if h[p] != BASE[p]["historical_state"]),
           "dT": sum(1 for p in t if t[p] != BASE[p]["observed_trend"]),
           "rates": {p: cells[p]["value_pct"] for p in idx.provinces},
           "n_lower": {p: cells[p].get("n_lower") for p in ("Firenze", "Siena", "Arezzo")},
           "n_matched": {p: cells[p].get("n_matched") for p in ("Firenze", "Siena", "Arezzo")}}
    slide.append(rec)
    if off in (-28, -21, -14, -7, -3, -1, 0, 1, 3, 7, 14, 21, 28):
        print(f"{a.isoformat():>12} {h['Firenze']:>18} {h['Siena']:>18} {h['Arezzo']:>18} "
              f"{rec['n_speaking']:>5} {rec['n_below']:>5} {rec['n_above']:>5} "
              f"{rec['dH']:>3} {rec['dT']:>3}  {t['Firenze'][:4]}/{t['Siena'][:4]}/{t['Arezzo'][:4]}")

for p in ("Firenze", "Siena", "Arezzo"):
    n = len(slide)
    same = sum(1 for r in slide if r["hist"][p] == BASE[p]["historical_state"])
    states = sorted({r["hist"][p] for r in slide})
    print(f"   {p:10s} keeps its published class on {same} of {n} as_of days in +/-28; "
          f"classes seen: {states}")

# ── (b) right-edge truncation ────────────────────────────────────────────────
print("\n(b) RIGHT-EDGE TRUNCATION")
lo, hi = L.win(AS_OF, P["WINDOW_DAYS"])
trunc = {}
for prov in ("Firenze", "Siena", "Arezzo"):
    cur = idx.pooled(prov, lo, hi, as_of=AS_OF)
    last = dt.date.fromisoformat(cur["last_observation"])
    dead = (hi - last).days
    cover = (last - lo).days           # elapsed days actually covered this season
    rowsA, rowsB = [], []
    for y in range(2006, AS_OF.year):
        b_all = idx.pooled(prov, L.shift(lo, y), L.shift(hi, y), as_of=AS_OF)
        if not b_all:
            continue
        shared = cur["sites"] & b_all["sites"]
        if len(shared) < P["MIN_PANEL_OVERLAP_FOR_LIKE_FOR_LIKE"]:
            continue
        now = idx.pooled(prov, lo, hi, only_sites=shared, as_of=AS_OF)
        then_full = idx.pooled(prov, L.shift(lo, y), L.shift(hi, y),
                               only_sites=shared, as_of=AS_OF)
        then_cut = idx.pooled(prov, L.shift(lo, y),
                              L.shift(lo, y) + dt.timedelta(days=cover),
                              only_sites=shared, as_of=AS_OF)
        if not (now and then_full):
            continue
        rowsA.append((now["rate_pct"], then_full["rate_pct"]))
        if then_cut and then_cut["drupes_sampled"]:
            rowsB.append((now["rate_pct"], then_cut["rate_pct"]))
    def verdict(rs):
        if len(rs) < P["MIN_BASELINE_SEASONS"]:
            return "INSUFFICIENT_DATA", 0, 0, len(rs)
        lo_ = sum(1 for a, b in rs if a < b)
        hi_ = sum(1 for a, b in rs if a > b)
        v = ("BELOW_HISTORICAL" if lo_ / len(rs) >= P["HIGH_PCTL"] else
             "ABOVE_HISTORICAL" if hi_ / len(rs) >= P["HIGH_PCTL"] else "TYPICAL")
        return v, lo_, hi_, len(rs)
    vA = verdict(rowsA); vB = verdict(rowsB)
    trunc[prov] = {"last_observation": last.isoformat(), "as_of": AS_OF.isoformat(),
                   "dead_days_at_right_edge": dead, "days_covered": cover,
                   "published": {"verdict": vA[0], "lower": vA[1], "higher": vA[2], "k": vA[3]},
                   "baseline_truncated_to_same_coverage":
                       {"verdict": vB[0], "lower": vB[1], "higher": vB[2], "k": vB[3]}}
    print(f"   {prov:10s} last observation {last} -> {dead} dead days inside the 28-day "
          f"window; this season covers {cover+1} of 28 days")
    print(f"              published            : {vA[0]:18s} lower {vA[1]} of {vA[3]}")
    print(f"              baseline cut to match: {vB[0]:18s} lower {vB[1]} of {vB[3]}")

# ── (c) steepness of the curve here ──────────────────────────────────────────
print("\n(c) STEEPNESS: pooled rate in the 28-day window ending on each date, prior seasons")
steep = {}
for prov in ("Firenze", "Siena", "Arezzo", "Grosseto", "Livorno", "Pisa"):
    per_year = []
    for y in range(2006, 2026):
        pts = {}
        for off in (-14, -7, 0, 7, 14):
            h2 = L.shift(AS_OF, y) + dt.timedelta(days=off)
            l2 = h2 - dt.timedelta(days=P["WINDOW_DAYS"] - 1)
            w = idx.pooled(prov, l2, h2, as_of=dt.date(2026, 9, 6))
            if w and w["n_visits"] >= P["MIN_VISITS"] and w["drupes_sampled"] >= P["MIN_DRUPES"]:
                pts[off] = w["rate_pct"]
        if -7 in pts and 7 in pts:
            per_year.append({"season": y, "pts": pts,
                             "pp_per_week": round((pts[7] - pts[-7]) / 2.0, 4)})
    if per_year:
        vals = [x["pp_per_week"] for x in per_year]
        steep[prov] = {"seasons": len(per_year),
                       "median_pp_per_week": round(statistics.median(vals), 4),
                       "min": min(vals), "max": max(vals), "detail": per_year}
        print(f"   {prov:10s} n={len(per_year)} prior seasons; median change "
              f"{statistics.median(vals):+.3f} percentage points per week "
              f"(range {min(vals):+.3f} to {max(vals):+.3f})")

json.dump({"slide": slide, "truncation": trunc, "steepness": steep},
          open(os.path.join(HERE, "rt5_04_seasonality.json"), "w"), indent=1)
print("\nwrote rt5_04_seasonality.json")
