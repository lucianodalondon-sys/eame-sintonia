#!/usr/bin/env python3
"""RT5 · accusation 5. TREND_MIN_ABS_CHANGE_PCT = 1.0 is not calibrated to this
quantity.

The rule names a direction only if three consecutive 28-day windows are monotone
AND the end-to-end change is at least 1.0 PERCENTAGE POINT. The whole observed
range across the ten provinces today is 0.03% to 1.15%. So the threshold is
roughly the size of the largest value in the panel.

Method: walk every province and every window-end date in the archive (7-day step,
2006-2026), apply the tool's own gates, and record the end-to-end change. Then
count how often a direction could EVER be named, and what threshold would be
needed to name one, say, a fifth of the time."""
import os, sys, json, statistics, datetime as dt
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import rt5_lib as L

P = L.PARAMS
LAST = dt.date(2026, 9, 6)
METRICS = ["ACTIVE_INFESTATION_COUNT", "DAMAGING_INFESTATION_COUNT",
           "TOTAL_INFESTATION_COUNT"]

out = {}
for metric in METRICS:
    idx, raw = L.get_index(metric)
    recs = []
    d = dt.date(2006, 4, 1)
    while d <= LAST:
        for prov in idx.provinces:
            pts = []
            for i in range(P["TREND_MIN_WINDOWS"] + 1):
                h = d - dt.timedelta(days=P["WINDOW_DAYS"] * i)
                l = h - dt.timedelta(days=P["WINDOW_DAYS"] - 1)
                w = idx.pooled(prov, l, h, as_of=LAST)
                if w and w["n_visits"] >= P["MIN_VISITS"] and w["drupes_sampled"] >= P["MIN_DRUPES"]:
                    pts.append(w["rate_pct"])
            pts.reverse()
            if len(pts) < P["TREND_MIN_WINDOWS"]:
                continue
            delta = pts[-1] - pts[0]
            mono_up = all(b >= a for a, b in zip(pts, pts[1:]))
            mono_dn = all(b <= a for a, b in zip(pts, pts[1:]))
            recs.append({"date": d.isoformat(), "prov": prov, "pts": pts,
                         "delta": round(delta, 4),
                         "mono": bool(mono_up or mono_dn),
                         "named": bool(abs(delta) >= P["TREND_MIN_ABS_CHANGE_PCT"]
                                       and (mono_up or mono_dn))})
        d += dt.timedelta(days=7)
    n = len(recs)
    ad = sorted(abs(r["delta"]) for r in recs)
    named = sum(1 for r in recs if r["named"])
    mono = sum(1 for r in recs if r["mono"])
    big = sum(1 for r in recs if abs(r["delta"]) >= 1.0)

    def q(f):
        return round(ad[min(n - 1, int(f * n))], 4)

    # what threshold would name a direction in 20% of the monotone cases?
    mono_ad = sorted(abs(r["delta"]) for r in recs if r["mono"])
    thr20 = round(mono_ad[int(0.80 * len(mono_ad))], 4) if mono_ad else None

    out[metric] = {
        "n_province_windows_passing_the_gates": n,
        "n_monotone": mono, "pct_monotone": round(100 * mono / n, 2),
        "n_abs_change_ge_1pp": big, "pct_abs_change_ge_1pp": round(100 * big / n, 2),
        "n_named_a_direction": named, "pct_named": round(100 * named / n, 2),
        "abs_delta_percentiles": {"p50": q(.50), "p75": q(.75), "p90": q(.90),
                                  "p95": q(.95), "p99": q(.99), "max": ad[-1]},
        "threshold_that_would_name_20pct_of_monotone_cases": thr20,
    }
    r = out[metric]
    print(f"\n{metric}")
    print(f"  province-windows passing the tool's own gates, 2006-2026, 7-day step: {n:,}")
    print(f"  monotone over 3 windows                : {mono:,} of {n:,} "
          f"({r['pct_monotone']}%)")
    print(f"  end-to-end change of at least 1.0 pp   : {big:,} of {n:,} "
          f"({r['pct_abs_change_ge_1pp']}%)")
    print(f"  BOTH, i.e. a direction is named        : {named:,} of {n:,} "
          f"({r['pct_named']}%)")
    print(f"  |change| percentiles: p50 {r['abs_delta_percentiles']['p50']}  "
          f"p75 {r['abs_delta_percentiles']['p75']}  p90 {r['abs_delta_percentiles']['p90']}  "
          f"p95 {r['abs_delta_percentiles']['p95']}  p99 {r['abs_delta_percentiles']['p99']}  "
          f"max {r['abs_delta_percentiles']['max']}")
    print(f"  a threshold of {thr20} pp would name a direction in the top 20% of "
          f"monotone cases")

# ── today's ten sequences, and what a ratio rule would say ───────────────────
print("\nTODAY'S TEN SEQUENCES (ACTIVE_INFESTATION_COUNT, as_of 2026-09-06)")
idx, _ = L.get_index("ACTIVE_INFESTATION_COUNT")
today = []
for c in L.all_cells(idx, LAST):
    pts = c["trend_points"]
    ratio = None
    if len(pts) >= 2 and pts[0] > 0:
        ratio = round(pts[-1] / pts[0], 3)
    today.append({"prov": c["province"], "pts": pts, "trend": c["observed_trend"],
                  "delta": c.get("trend_delta"), "ratio_end_over_start": ratio})
    print(f"  {c['province']:15s} {' -> '.join(str(x) for x in pts):45s} "
          f"delta {str(c.get('trend_delta')):>8}  ratio {str(ratio):>8}  "
          f"{c['observed_trend']}")

json.dump({"archive": out, "today": today},
          open(os.path.join(HERE, "rt5_05_trend.json"), "w"), indent=1)
print("\nwrote rt5_05_trend.json")
