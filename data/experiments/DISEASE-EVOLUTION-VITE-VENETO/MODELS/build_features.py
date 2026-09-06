#!/usr/bin/env python3
"""
Build CUTOFF-RESPECTING seasonal predictors for Veneto vine peronospora.

LAW ENFORCED IN CODE:
    TARGET_SEASON_WEATHER_LEAKAGE = FORBIDDEN.
    To predict season Y we may not read one single day of season Y's own
    spring/summer weather. This is asserted, not assumed: build_features()
    refuses to emit a row whose contributing days cross its cutoff, and
    assert_no_leakage() re-proves it independently afterwards.

TWO ISSUE REGIMES
    CUTOFF_B_TRUE_12M   issued (Y-1)-09-01 -> ~10 months before peak season Y.
                        Uses: season Y-1 (Apr-Aug), winter (Y-2 Dec .. Y-1 Feb),
                        season Y-2. NOTHING after (Y-1)-08-31.
    CUTOFF_A_PRESEASON  issued Y-03-01 -> ~4 months before peak season Y,
                        before bud break. Everything in B, plus autumn Y-1
                        (Sep-Nov) and winter (Y-1 Dec .. Y Feb).
                        NOTHING after (Y)-02-28/29.

Anomalies are expressed against a 1991-2020 climatology computed ONLY from
days that are themselves inside the row's cutoff, so the baseline cannot leak
either.
"""
import json, os, sys, datetime as dt
from statistics import mean, pstdev

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
WEATHER = os.path.join(ROOT, "WEATHER")

D = dt.date
def d(s): return D(int(s[0:4]), int(s[5:7]), int(s[8:10]))

# ---------------------------------------------------------------- load
def load_points():
    pts = {}
    for fn in sorted(os.listdir(WEATHER)):
        if not fn.startswith("era5_") or not fn.endswith(".json"):
            continue
        name = fn[5:-5]
        raw = json.load(open(os.path.join(WEATHER, fn)))
        dd = raw["daily"]
        rec = {}
        for i, t in enumerate(dd["time"]):
            rec[d(t)] = {
                "pr":  dd["precipitation_sum"][i],
                "tm":  dd["temperature_2m_mean"][i],
                "tn":  dd["temperature_2m_min"][i],
                "tx":  dd["temperature_2m_max"][i],
                "rh":  dd["relative_humidity_2m_mean"][i],
            }
        pts[name] = {"lat": raw["latitude"], "lon": raw["longitude"],
                     "elev": raw.get("elevation"), "days": rec}
    return pts

# ---------------------------------------------------------------- windows
def window(days, a, b):
    """Inclusive [a,b]. Returns list of (date, rec) sorted."""
    return [(k, days[k]) for k in sorted(days) if a <= k <= b]

def block_stats(rows, prefix):
    """Descriptors of one calendar block. Pure aggregation, no target info."""
    if not rows:
        return None
    pr = [r["pr"] for _, r in rows]
    tm = [r["tm"] for _, r in rows]
    tn = [r["tn"] for _, r in rows]
    rh = [r["rh"] for _, r in rows]
    wet = [p > 1.0 for p in pr]
    # longest run and count of runs of >=2 consecutive wet days
    runs, cur = [], 0
    for w in wet:
        if w: cur += 1
        else:
            if cur: runs.append(cur)
            cur = 0
    if cur: runs.append(cur)
    long_runs = [r for r in runs if r >= 2]
    out = {
        f"{prefix}_precip_sum":     round(sum(pr), 1),
        f"{prefix}_rain_days":      sum(wet),
        f"{prefix}_wet_spells_2d":  len(long_runs),
        f"{prefix}_max_wet_run":    max(runs) if runs else 0,
        f"{prefix}_tmean":          round(mean(tm), 2),
        f"{prefix}_tmin_mean":      round(mean(tn), 2),
        f"{prefix}_rh_mean":        round(mean(rh), 2),
        f"{prefix}_rh75_days":      sum(1 for x in rh if x >= 75),
        f"{prefix}_frost_days":     sum(1 for x in tn if x < 0.0),
        f"{prefix}_gdd10":          round(sum(max(0.0, t - 10.0) for t in tm), 1),
        f"{prefix}_n_days":         len(rows),
    }
    return out

# ---------------------------------------------------------------- blocks per target year
def blocks_for(Y, regime):
    """
    Returns (cutoff_date, [(block_name, start, end), ...]).
    Every block end MUST be <= cutoff_date. Enforced below.
    """
    if regime == "CUTOFF_B_TRUE_12M":
        cutoff = D(Y - 1, 8, 31)
        blocks = [
            ("prevseason",   D(Y - 1, 4, 1),  D(Y - 1, 8, 31)),   # season Y-1
            ("prevwinter",   D(Y - 2, 12, 1), D(Y - 1, 2, 28)),   # winter before season Y-1
            ("prevautumn",   D(Y - 2, 9, 1),  D(Y - 2, 11, 30)),  # autumn Y-2
            ("prev2season",  D(Y - 2, 4, 1),  D(Y - 2, 8, 31)),   # season Y-2
        ]
    elif regime == "CUTOFF_A_PRESEASON":
        cutoff = D(Y, 2, 28) if Y % 4 else D(Y, 2, 29)
        blocks = [
            ("prevseason",   D(Y - 1, 4, 1),  D(Y - 1, 8, 31)),
            ("autumn",       D(Y - 1, 9, 1),  D(Y - 1, 11, 30)),  # autumn just past
            ("winter",       D(Y - 1, 12, 1), cutoff),            # winter just past
            ("prev2season",  D(Y - 2, 4, 1),  D(Y - 2, 8, 31)),
        ]
    else:
        raise ValueError(regime)
    for nm, a, b in blocks:
        assert b <= cutoff, f"block {nm} for {Y} ends {b} after cutoff {cutoff}"
    return cutoff, blocks

# target season that must never be touched
def target_season(Y):
    return D(Y, 3, 1), D(Y, 9, 30)

# ---------------------------------------------------------------- build
def build(points, years, regime, clim_years=(1991, 2020)):
    rows = {}
    provenance = {}
    for Y in years:
        cutoff, blocks = blocks_for(Y, regime)
        per_point = {}
        used_dates_max = None
        for pname, p in points.items():
            feats = {}
            for nm, a, b in blocks:
                rr = window(p["days"], a, b)
                if rr:
                    hi = rr[-1][0]
                    used_dates_max = hi if used_dates_max is None else max(used_dates_max, hi)
                bs = block_stats(rr, nm)
                if bs is None:
                    feats = None
                    break
                feats.update(bs)
            if feats is None:
                per_point[pname] = None
                continue
            per_point[pname] = feats
        good = {k: v for k, v in per_point.items() if v}
        if not good:
            continue
        keys = sorted(set().union(*[set(v) for v in good.values()]))
        regional = {k: round(mean([v[k] for v in good.values()]), 3) for k in keys}
        rows[Y] = regional
        provenance[Y] = {
            "regime": regime,
            "cutoff_date": cutoff.isoformat(),
            "latest_day_used": used_dates_max.isoformat() if used_dates_max else None,
            "blocks": [{"name": nm, "from": a.isoformat(), "to": b.isoformat()} for nm, a, b in blocks],
            "points_used": sorted(good),
            "points_missing": sorted([k for k, v in per_point.items() if not v]),
        }

    # anomalies vs climatology built ONLY from years whose own blocks end
    # before this row's cutoff -> no future information in the normal either.
    feat_names = sorted(set().union(*[set(v) for v in rows.values()])) if rows else []
    clim_pool_years = [y for y in range(clim_years[0], clim_years[1] + 1)]
    clim_rows = {}
    for Y in clim_pool_years:
        try:
            cutoff, blocks = blocks_for(Y, regime)
        except Exception:
            continue
        per_point = {}
        for pname, p in points.items():
            feats = {}
            ok = True
            for nm, a, b in blocks:
                bs = block_stats(window(p["days"], a, b), nm)
                if bs is None:
                    ok = False; break
                feats.update(bs)
            per_point[pname] = feats if ok else None
        good = {k: v for k, v in per_point.items() if v}
        if good:
            clim_rows[Y] = {k: mean([v[k] for v in good.values()]) for k in feat_names if all(k in v for v in good.values())}

    anom = {}
    for Y, r in rows.items():
        a = {}
        for k in feat_names:
            pool = [clim_rows[cy][k] for cy in clim_rows if k in clim_rows[cy] and cy < Y]
            if len(pool) < 10:
                continue
            m, s = mean(pool), pstdev(pool)
            a[k + "_z"] = round((r[k] - m) / s, 3) if s > 0 else 0.0
            a[k + "_clim_mean"] = round(m, 3)
            a[k + "_clim_n"] = len(pool)
        anom[Y] = a
    return rows, anom, provenance

# ---------------------------------------------------------------- leakage proof
def assert_no_leakage(provenance):
    """Independent re-proof. Returns (n_checked, violations)."""
    viol = []
    for Y, pv in provenance.items():
        cutoff = d(pv["cutoff_date"])
        ts_a, ts_b = target_season(Y)
        if cutoff >= ts_a:
            viol.append({"year": Y, "why": f"cutoff {cutoff} is inside target season {ts_a}..{ts_b}"})
        if pv["latest_day_used"] and d(pv["latest_day_used"]) > cutoff:
            viol.append({"year": Y, "why": f"used day {pv['latest_day_used']} > cutoff {cutoff}"})
        for b in pv["blocks"]:
            ba, bb = d(b["from"]), d(b["to"])
            if not (bb < ts_a or ba > ts_b):
                viol.append({"year": Y, "why": f"block {b['name']} {ba}..{bb} overlaps target season {ts_a}..{ts_b}"})
            if bb > cutoff:
                viol.append({"year": Y, "why": f"block {b['name']} ends {bb} after cutoff {cutoff}"})
    return len(provenance), viol

# ---------------------------------------------------------------- main
if __name__ == "__main__":
    pts = load_points()
    print(f"POINTS LOADED: {len(pts)}")
    for k, v in pts.items():
        print(f"  {k:28s} lat={v['lat']:.3f} lon={v['lon']:.3f} elev={v['elev']} days={len(v['days'])}")
    # full ERA5 span: feature history is 34 seasons even though LABELS exist only for
    # 2014-2025. More antecedent history helps the climatology and the analog space;
    # it cannot help the outcome, and is never allowed to pretend otherwise.
    YEARS = list(range(1992, 2026))
    out = {}
    for regime in ("CUTOFF_B_TRUE_12M", "CUTOFF_A_PRESEASON"):
        rows, anom, prov = build(pts, YEARS, regime)
        n, viol = assert_no_leakage(prov)
        print(f"\n{regime}: rows={len(rows)} leakage_checks={n} violations={len(viol)}")
        for v in viol:
            print("   VIOLATION", v)
        out[regime] = {"features": rows, "anomalies": anom, "provenance": prov,
                       "leakage_violations": viol,
                       "TARGET_SEASON_WEATHER_LEAKAGE": len(viol)}
    dest = os.path.join(ROOT, "MODELS", "features_cutoff_respecting.json")
    json.dump(out, open(dest, "w"), indent=1)
    print(f"\nwrote {dest}")
    r = out["CUTOFF_A_PRESEASON"]["features"]
    ks = ["prevseason_precip_sum", "prevseason_rain_days", "winter_precip_sum",
          "winter_tmean", "autumn_precip_sum", "prevseason_rh75_days"]
    print("\nLABELLED WINDOW ONLY (2014-2025); full table has %d seasons" % len(r))
    print("YEAR  " + "  ".join(f"{k[:18]:>18s}" for k in ks))
    for Y in sorted(y for y in r if y >= 2014):
        print(f"{Y}  " + "  ".join(f"{r[Y].get(k, float('nan')):18.1f}" for k in ks))
