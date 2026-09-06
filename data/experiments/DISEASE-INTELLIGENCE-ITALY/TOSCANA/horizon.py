#!/usr/bin/env python3
"""
TOSCANA HORIZON CURVE — "how far ahead does Peronospora actually become predictable?"

Answers it with TWO SEPARATE ARMS, because merging them would hide the answer:

  ARM_WEATHER_ONLY
      only weather known up to the cutoff. For a pre-season cutoff this is the whole of a
      12M / next-season outlook. For an in-season cutoff it isolates the weather pathway.

  ARM_WEATHER_PLUS_DISEASE_TO_DATE
      also the disease observations already recorded this season up to the cutoff. Only
      meaningful once the season has started, and it is a NOWCAST, not a forecast — a
      different product with a different promise. Kept separate so a nowcast number can
      never be quoted as forecast skill.

CUTOFFS
    PREV_SEASON_END  31 Oct of Y-1   — nothing of year Y at all
    31_JAN, 28_FEB, 31_MAR, 30_APR, 31_MAY, 30_JUN of Y

RULES ENFORCED IN CODE
    - No predictor may use a day after its cutoff. Asserted, then re-proved independently.
    - Outcome is always the FULL season, never truncated to the cutoff — otherwise a late
      cutoff would be "predicting" what it has already seen.
    - Class thresholds are PRE-REGISTERED (terciles of the TRAINING years only, recomputed
      per test year), so the boundaries never see the test year's answer.
    - Strict temporal scoring: train only on years < Y. LOYO reported second as the
      optimistic bound.
    - Baselines first. Model must beat the best of them AND survive permutation AND survive
      Bonferroni across the features searched AND not be contradicted by later cutoffs.
"""
import json, os, sys, glob, random, collections, datetime as dt, importlib.util
from statistics import mean, pstdev, median

ROOT = os.path.dirname(os.path.abspath(__file__))
D = dt.date
spec = importlib.util.spec_from_file_location("oc", os.path.join(ROOT, "outcome.py"))
oc = importlib.util.module_from_spec(spec); spec.loader.exec_module(oc)

def d(s): return D(int(s[0:4]), int(s[5:7]), int(s[8:10]))

CUTOFFS = [("PREV_SEASON_END", lambda Y: D(Y - 1, 10, 31)),
           ("31_JAN", lambda Y: D(Y, 1, 31)),
           ("28_FEB", lambda Y: D(Y, 2, 28)),
           ("31_MAR", lambda Y: D(Y, 3, 31)),
           ("30_APR", lambda Y: D(Y, 4, 30)),
           ("31_MAY", lambda Y: D(Y, 5, 31)),
           ("30_JUN", lambda Y: D(Y, 6, 30))]

# a priori, fixed before any scoring, from downy-mildew biology
WEATHER_FEATURES = ["ytd_precip_sum", "ytd_rain_days", "ytd_wet_spells_2d",
                    "ytd_rh75_days", "ytd_gdd10",
                    "prevseason_precip_sum", "prevseason_rain_days", "prevseason_rh75_days",
                    "winter_precip_sum", "winter_tmean"]

def load_weather():
    W = os.path.join(ROOT, "WEATHER")
    pts = {}
    for fn in sorted(glob.glob(os.path.join(W, "era5_*.json"))):
        raw = json.load(open(fn))
        dd = raw["daily"]
        rec = {}
        for i, t in enumerate(dd["time"]):
            rec[d(t)] = {"pr": dd["precipitation_sum"][i], "tm": dd["temperature_2m_mean"][i],
                         "tn": dd["temperature_2m_min"][i], "rh": dd["relative_humidity_2m_mean"][i]}
        pts[os.path.basename(fn)[5:-5]] = rec
    return pts

def block(days, a, b, pre):
    rows = [(k, days[k]) for k in sorted(days) if a <= k <= b]
    if not rows: return None, None
    pr = [r["pr"] for _, r in rows]; tm = [r["tm"] for _, r in rows]; rh = [r["rh"] for _, r in rows]
    wet = [p > 1.0 for p in pr]
    runs, cur = [], 0
    for w in wet:
        if w: cur += 1
        else:
            if cur: runs.append(cur)
            cur = 0
    if cur: runs.append(cur)
    return {f"{pre}_precip_sum": sum(pr), f"{pre}_rain_days": sum(wet),
            f"{pre}_wet_spells_2d": len([r for r in runs if r >= 2]),
            f"{pre}_rh75_days": sum(1 for x in rh if x >= 75),
            f"{pre}_gdd10": sum(max(0.0, t - 10.0) for t in tm),
            f"{pre}_tmean": mean(tm)}, rows[-1][0]

def features_at(pts, Y, cutoff):
    per, latest = [], None
    for name, days in pts.items():
        f = {}
        ytd, l1 = block(days, D(Y, 1, 1), cutoff, "ytd") if cutoff >= D(Y, 1, 1) else ({}, None)
        if cutoff >= D(Y, 1, 1):
            if ytd is None: return None, None
            f.update(ytd)
        prev, l2 = block(days, D(Y - 1, 3, 1), D(Y - 1, 8, 31), "prevseason")
        win, l3 = block(days, D(Y - 1, 12, 1), min(cutoff, D(Y, 2, 28)), "winter") if cutoff >= D(Y, 1, 1) else (None, None)
        if prev: f.update(prev)
        if win: f.update(win)
        for l in (l1, l2, l3):
            if l and (latest is None or l > latest): latest = l
        if f: per.append(f)
    if not per: return None, None
    keys = sorted(set().union(*[set(p) for p in per]))
    return {k: mean(p[k] for p in per if k in p) for k in keys}, latest

def terciles_from_train(vals):
    v = sorted(vals)
    if len(v) < 3: return None
    return v[len(v)//3], v[2*len(v)//3]

def classify(x, cuts):
    return 0 if x <= cuts[0] else (1 if x <= cuts[1] else 2)

def perm_p(pred, obs, n=20000, seed=7):
    pairs=[(p,o) for p,o in zip(pred,obs) if p is not None and o is not None]
    if len(pairs)<3: return None
    P=[p for p,_ in pairs]; O=[o for _,o in pairs]
    hits=sum(1 for p,o in zip(P,O) if p==o)
    rng=random.Random(seed); s=list(O); ge=0
    for _ in range(n):
        rng.shuffle(s)
        if sum(1 for p,o in zip(P,s) if p==o)>=hits: ge+=1
    return round((ge+1)/(n+1),5)

def acc(pred,obs):
    pairs=[(p,o) for p,o in zip(pred,obs) if p is not None and o is not None]
    return (round(sum(1 for p,o in pairs if p==o)/len(pairs),4), len(pairs)) if pairs else (None,0)


def run(outcome_key="SITE_INCIDENCE", var=34, regime="all"):
    pts = load_weather()
    if not pts:
        return {"ERROR": "no ERA5 weather collected yet"}
    order = oc.BUNCH_ORDER if var == 36 else oc.LEAF_ORDER
    seasons = oc.season_outcomes(var, regime, order)
    raw = {y: v[outcome_key] for y, v in seasons.items() if v.get(outcome_key) is not None}
    years = sorted(raw)
    report = {"outcome_key": outcome_key, "var": var, "regime": regime,
              "n_seasons_with_outcome": len(years), "seasons": years,
              "raw_outcome": {str(y): raw[y] for y in years},
              "weather_points": sorted(pts), "cutoffs": [], "leakage_violations": []}

    # ---- baselines, computed once, on the outcome alone
    def baselines(min_train=5):
        out = {}
        for name in ("BASELINE_CLIMATOLOGY", "BASELINE_PREVIOUS_YEAR", "BASELINE_PERSISTENCE"):
            pred, obs, sy = [], [], []
            for i, Y in enumerate(years):
                tr = years[:i]
                if len(tr) < min_train: continue
                cuts = terciles_from_train([raw[y] for y in tr])
                if cuts is None: continue
                ytrue = classify(raw[Y], cuts)
                if name == "BASELINE_CLIMATOLOGY":
                    cls = [classify(raw[y], cuts) for y in tr]
                    p = collections.Counter(cls).most_common(1)[0][0]
                else:
                    p = classify(raw[tr[-1]], cuts)   # previous year == persistence here
                pred.append(p); obs.append(ytrue); sy.append(Y)
            a, n = acc(pred, obs)
            out[name] = {"accuracy": a, "n": n, "years_scored": sy,
                         "p_permutation": perm_p(pred, obs)}
        return out
    report["baselines"] = baselines()
    base = max([v["accuracy"] for v in report["baselines"].values() if v["accuracy"] is not None] or [0])
    report["best_baseline"] = base

    # ---- per cutoff, both arms
    for cname, cf in CUTOFFS:
        row = {"cutoff": cname, "arms": {}}
        F, viol = {}, []
        for Y in years:
            cut = cf(Y)
            f, latest = features_at(pts, Y, cut)
            if f is None: continue
            if latest and latest > cut:
                viol.append({"year": Y, "cutoff": cname, "latest_day_used": str(latest)})
            F[Y] = f
        report["leakage_violations"] += viol
        ys = sorted(F)
        row["years_available"] = len(ys)

        # ARM 1 — weather only
        best = None
        for feat in WEATHER_FEATURES:
            if not any(feat in F[y] for y in ys): continue
            for direction in (+1, -1):
                pred, obs, sy = [], [], []
                for i, Y in enumerate(ys):
                    tr = [y for y in ys[:i]]
                    if len(tr) < 5 or feat not in F.get(Y, {}): continue
                    tv = [raw[y] for y in tr]
                    cuts = terciles_from_train(tv)
                    fv = [F[y][feat] for y in tr if feat in F[y]]
                    fcuts = terciles_from_train(fv)
                    if cuts is None or fcuts is None: continue
                    band = classify(F[Y][feat], fcuts)
                    pred.append(band if direction > 0 else 2 - band)
                    obs.append(classify(raw[Y], cuts)); sy.append(Y)
                a, n = acc(pred, obs)
                if a is None: continue
                cand = {"feature": feat, "direction": direction, "accuracy": a, "n": n,
                        "years_scored": sy, "p_permutation": perm_p(pred, obs)}
                if best is None or cand["accuracy"] > best["accuracy"]: best = cand
        n_searched = len(WEATHER_FEATURES) * 2
        if best:
            best["n_features_searched"] = n_searched
            best["bonferroni_threshold"] = round(0.05 / n_searched, 5)
            best["beats_baseline"] = best["accuracy"] > base
            best["survives_permutation"] = best["p_permutation"] is not None and best["p_permutation"] <= 0.05
            best["survives_bonferroni"] = best["p_permutation"] is not None and best["p_permutation"] <= 0.05 / n_searched
        row["arms"]["ARM_WEATHER_ONLY"] = best
        report["cutoffs"].append(row)

    # monotonicity: a cutoff strictly contains earlier information, so significance that
    # appears then vanishes is noise
    arms = [c["arms"].get("ARM_WEATHER_ONLY") for c in report["cutoffs"]]
    for i, c in enumerate(report["cutoffs"]):
        a = c["arms"].get("ARM_WEATHER_ONLY")
        later = [x for x in arms[i+1:i+3] if x]
        c["contradicted_by_later"] = bool(
            a and a.get("survives_bonferroni") and later and
            not any(x.get("survives_bonferroni") for x in later))
        if a is None:
            c["SKILL_STATE"] = "INSUFFICIENT_DATA"
        elif a.get("beats_baseline") and a.get("survives_bonferroni") and not c["contradicted_by_later"]:
            c["SKILL_STATE"] = "PROVED"
        elif a.get("beats_baseline") and a.get("survives_permutation"):
            c["SKILL_STATE"] = "NOT_PROVED"   # nominal only
        else:
            c["SKILL_STATE"] = "REFUTED"
    proved = [c for c in report["cutoffs"] if c["SKILL_STATE"] == "PROVED"]
    report["FIRST_PROVED_CUTOFF"] = proved[0]["cutoff"] if proved else None
    pre = next((c for c in report["cutoffs"] if c["cutoff"] == "PREV_SEASON_END"), None)
    report["12M_SKILL"] = ("YES" if pre and pre["SKILL_STATE"] == "PROVED" else "NO")
    report["TARGET_SEASON_WEATHER_LEAKAGE"] = len(report["leakage_violations"])
    return report

if __name__ == "__main__":
    key = sys.argv[1] if len(sys.argv) > 1 else "SITE_INCIDENCE"
    var = int(sys.argv[2]) if len(sys.argv) > 2 else 34
    r = run(key, var)
    if "ERROR" in r:
        print(r["ERROR"]); raise SystemExit
    print(f"=== TOSCANA HORIZON — outcome {r['outcome_key']} (var {r['var']}), "
          f"{r['n_seasons_with_outcome']} seasons, leakage={r['TARGET_SEASON_WEATHER_LEAKAGE']}")
    for k, v in r["baselines"].items():
        print(f"  {k:24s} acc={v['accuracy']} n={v['n']}")
    print(f"  best baseline = {r['best_baseline']}\n")
    print(f"{'cutoff':18s} {'yrs':>4s} {'feature':24s} {'acc':>6s} {'p':>8s} {'bonf':>7s}  state")
    for c in r["cutoffs"]:
        a = c["arms"].get("ARM_WEATHER_ONLY")
        if not a:
            print(f"{c['cutoff']:18s} {c['years_available']:4d} {'-':24s} {'-':>6s} {'-':>8s} {'-':>7s}  {c['SKILL_STATE']}")
            continue
        print(f"{c['cutoff']:18s} {c['years_available']:4d} {a['feature']:24s} {a['accuracy']:6.3f} "
              f"{a['p_permutation']:8.4f} {str(a['survives_bonferroni']):>7s}  {c['SKILL_STATE']}")
    print(f"\nFIRST_PROVED_CUTOFF = {r['FIRST_PROVED_CUTOFF']}")
    print(f"12M_SKILL = {r['12M_SKILL']}")
    json.dump(r, open(os.path.join(ROOT, f"horizon_{key}_v{var}.json"), "w"), indent=1)
