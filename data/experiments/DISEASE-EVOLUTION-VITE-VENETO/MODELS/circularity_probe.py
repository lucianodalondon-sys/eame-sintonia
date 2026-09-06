#!/usr/bin/env python3
"""
CIRCULARITY PROBE — answerable WITHOUT any disease label.

The threat:
  ARPAV explains each season's infections by the rain that caused them. So the
  severity class is, to an unknown degree, a restatement of the target season's own
  rainfall. If our antecedent predictors (previous season / autumn / winter) are
  themselves strongly correlated with the target season's rainfall, then any apparent
  "12-month skill" is really the target season's weather sneaking in through the back
  door, and the outlook proves nothing.

The test:
  Measure how much of the TARGET SEASON's infection-relevant weather is predictable
  from the antecedent blocks. If that correlation is near zero, the antecedent path is
  genuinely independent of the season's own weather, and a model built on it cannot be
  covertly circular. If it is high, we must say so.

IMPORTANT — CONTAINMENT:
  This script is the ONLY place in the pilot that computes target-season weather.
  It writes to EVIDENCE/circularity_probe.json. backtest.py never reads that file, and
  build_features.py refuses to emit any day past its cutoff. Target-season weather is a
  DIAGNOSTIC here and is never a predictor anywhere.
"""
import json, os, datetime as dt
from statistics import mean, pstdev

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
import importlib.util
spec = importlib.util.spec_from_file_location("bf", os.path.join(HERE, "build_features.py"))
bf = importlib.util.module_from_spec(spec); spec.loader.exec_module(bf)

D = dt.date
YEARS = list(range(1991, 2026))

def target_season_weather(points, Y):
    """April 1 - August 31 of year Y. DIAGNOSTIC ONLY."""
    per = []
    for pname, p in points.items():
        rows = bf.window(p["days"], D(Y, 4, 1), D(Y, 8, 31))
        if not rows:
            continue
        pr = [r["pr"] for _, r in rows]
        tm = [r["tm"] for _, r in rows]
        rh = [r["rh"] for _, r in rows]
        # crude primary-infection-event proxy, Baldacci "10-10-10"-flavoured:
        # a day with >=10 mm rain and mean T >= 10 C, counted once per wet spell.
        ev, armed = 0, True
        for (dte, r) in rows:
            hit = r["pr"] >= 10.0 and r["tm"] >= 10.0
            if hit and armed:
                ev += 1; armed = False
            elif not hit:
                armed = True
        per.append({
            "ts_precip_sum": sum(pr),
            "ts_rain_days": sum(1 for x in pr if x > 1.0),
            "ts_heavy_days": sum(1 for x in pr if x >= 10.0),
            "ts_infection_events_10_10": ev,
            "ts_tmean": mean(tm),
            "ts_rh_mean": mean(rh),
            "ts_rh75_days": sum(1 for x in rh if x >= 75),
        })
    if not per:
        return None
    return {k: round(mean(d[k] for d in per), 3) for k in per[0]}

def pearson(a, b):
    n = len(a)
    if n < 4: return None
    ma, mb = mean(a), mean(b)
    sa, sb = pstdev(a), pstdev(b)
    if sa == 0 or sb == 0: return None
    return round(sum((x-ma)*(y-mb) for x, y in zip(a, b)) / (n*sa*sb), 3)

def rank(v):
    order = sorted(range(len(v)), key=lambda i: v[i])
    r = [0]*len(v)
    for pos, i in enumerate(order): r[i] = pos
    return r

def spearman(a, b):
    return pearson([float(x) for x in rank(a)], [float(x) for x in rank(b)])

def perm_p_abs(a, b, n_perm=20000, seed=20260906):
    import random
    obs = abs(spearman(a, b) or 0)
    rng = random.Random(seed); bb = list(b); ge = 0
    for _ in range(n_perm):
        rng.shuffle(bb)
        if abs(spearman(a, bb) or 0) >= obs: ge += 1
    return round((ge+1)/(n_perm+1), 5)

if __name__ == "__main__":
    pts = bf.load_points()
    ts = {Y: target_season_weather(pts, Y) for Y in YEARS}
    ts = {Y: v for Y, v in ts.items() if v}

    out = {"note": "DIAGNOSTIC ONLY. Target-season weather is never used as a predictor.",
           "target_season_window": "Apr 1 - Aug 31 of year Y",
           "regimes": {}}

    for regime in ("CUTOFF_A_PRESEASON", "CUTOFF_B_TRUE_12M"):
        rows, anom, prov = bf.build(pts, YEARS, regime)
        n_v, viol = bf.assert_no_leakage(prov)
        yrs = sorted(set(rows) & set(ts))
        featnames = sorted(set().union(*[set(rows[y]) for y in yrs]))
        # the outcome-relevant target-season variables we care about
        targets = ["ts_precip_sum", "ts_rain_days", "ts_infection_events_10_10", "ts_rh75_days"]
        table = {}
        for t in targets:
            tv = [ts[y][t] for y in yrs]
            corrs = []
            for f in featnames:
                if f.endswith("_n_days"): continue
                fv = [rows[y][f] for y in yrs]
                s = spearman(fv, tv)
                if s is None: continue
                corrs.append({"feature": f, "spearman": s, "abs": abs(s)})
            corrs.sort(key=lambda c: -c["abs"])
            top = corrs[:6]
            for c in top:
                fv = [rows[y][c["feature"]] for y in yrs]
                c["p_permutation"] = perm_p_abs(fv, tv)
                del c["abs"]
            table[t] = {
                "n_years": len(yrs),
                "strongest_antecedent_links": top,
                "max_abs_spearman": round(max((abs(c["spearman"]) for c in corrs), default=0), 3),
                "n_features_screened": len(corrs),
            }
        # multiplicity: screening this many features, what |rho| is expected by chance?
        out["regimes"][regime] = {
            "leakage_violations": len(viol),
            "years": yrs,
            "per_target": table,
        }

    # verdict
    worst = 0.0
    for rg, r in out["regimes"].items():
        for t, v in r["per_target"].items():
            worst = max(worst, v["max_abs_spearman"])
    out["max_abs_spearman_any_link"] = round(worst, 3)
    if worst >= 0.7:
        out["CIRCULARITY_VERDICT"] = "HIGH — antecedent blocks strongly predict the target season's own weather; apparent 12M skill could be the season's weather in disguise"
    elif worst >= 0.5:
        out["CIRCULARITY_VERDICT"] = "MEDIUM — some antecedent/target-season coupling; must be disclosed"
    else:
        out["CIRCULARITY_VERDICT"] = "LOW — antecedent blocks carry little information about the target season's own weather, so a model built on them is not covertly restating it"
    out["caveat"] = ("Screening ~50 features x 4 targets means the LARGEST |rho| is inflated by selection. "
                     "The permutation p-values shown are per-link and NOT corrected for that screening. "
                     "Read the verdict from the magnitude, not from the p-value.")

    dest = os.path.join(ROOT, "EVIDENCE", "circularity_probe.json")
    json.dump(out, open(dest, "w"), indent=1)
    print(f"years: {len(out['regimes']['CUTOFF_A_PRESEASON']['years'])}  "
          f"({out['regimes']['CUTOFF_A_PRESEASON']['years'][0]}-{out['regimes']['CUTOFF_A_PRESEASON']['years'][-1]})")
    for rg, r in out["regimes"].items():
        print(f"\n=== {rg}  (leakage violations: {r['leakage_violations']})")
        for t, v in r["per_target"].items():
            print(f"  {t:30s} max|rho|={v['max_abs_spearman']:.3f}  over {v['n_features_screened']} features")
            for c in v["strongest_antecedent_links"][:3]:
                print(f"      {c['feature']:34s} rho={c['spearman']:+.3f}  p={c['p_permutation']}")
    print(f"\nMAX |rho| ANY LINK = {out['max_abs_spearman_any_link']}")
    print(f"CIRCULARITY_VERDICT = {out['CIRCULARITY_VERDICT']}")
    print(f"wrote {dest}")
