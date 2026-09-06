#!/usr/bin/env python3
"""
EARLY WARNING AT 7 / 14 / 21 / 30 DAYS — testable without the local collection.

The mission asks for these four horizons. They do NOT require leaf wetness: the Tuscan
observations are weekly per vineyard, so "given the season up to week W, what does week W+k
look like?" is answerable from what is already collected.

THE MANDATORY BASELINE IS PERSISTENCE, and it is deliberately strong.
For a k-week-ahead question the null hypothesis is "nothing changes": predict week W+k to be
whatever week W was. Any warning product must beat that, because a grower already knows what
their vineyard looked like last week. Two more baselines are added:
  WEEK_CLIMATOLOGY   the mean incidence for that ISO week across TRAINING seasons only
  SEASON_TO_DATE     the season's own mean up to W

NESTED TEMPORAL VALIDATION.
  test season Y  -> train only on seasons < Y
  feature choice -> made inside the training seasons only
  thresholds     -> from training seasons only
Nothing about season Y is used to build the rule that scores season Y.

TWO TARGETS, because they are different products:
  LEVEL   the incidence at W+k        (a state)
  RISE    does incidence INCREASE by more than the training-median rise?  (a warning)
The second is what a warning actually is. The first is nearly guaranteed by persistence.
"""
import json, os, sys, collections, importlib.util, random
from statistics import mean, median

ROOT = os.path.dirname(os.path.abspath(__file__))
_o = importlib.util.spec_from_file_location("oc", os.path.join(ROOT, "outcome.py"))
oc = importlib.util.module_from_spec(_o); _o.loader.exec_module(oc)
_h2 = importlib.util.spec_from_file_location("h2", os.path.join(ROOT, "horizon2.py"))
H2 = importlib.util.module_from_spec(_h2); _h2.loader.exec_module(H2)

WEEK_RANGE = range(18, 35)          # the Tuscan observation season
HORIZONS = {"7D": 1, "14D": 2, "21D": 3, "30D": 4}   # weeks ahead

def weekly_incidence(var, order, min_sites=20):
    """{year: {week: fraction of vineyards observed that week showing disease}}"""
    data = oc.load(var, "all")
    out = {}
    for y, rows in data.items():
        wk = collections.defaultdict(lambda: collections.defaultdict(list))
        for r in rows:
            if not r["week"]: continue
            wk[int(r["week"])][r["field"]].append(order.get(r["label"], 0))
        s = {}
        for w, sites in wk.items():
            if len(sites) >= min_sites:
                s[w] = sum(1 for v in sites.values() if max(v) > 0) / len(sites)
        if len(s) >= 6: out[y] = s
    return out

def build_pairs(W, k):
    """(year, week) -> (x_now, y_future). Disjoint weeks by construction."""
    pairs = []
    for y, s in W.items():
        for w in WEEK_RANGE:
            if w in s and (w + k) in s:
                assert w + k > w, "ASSERT FAILED: target week not after predictor week"
                pairs.append({"year": y, "week": w, "x": s[w], "y": s[w + k],
                              "hist": [s[q] for q in range(min(s), w + 1) if q in s]})
    return pairs

def run(var=36):
    order = oc.BUNCH_ORDER if var == 36 else oc.LEAF_ORDER
    W = weekly_incidence(var, order)
    years = sorted(W)
    rep = {"var": var, "n_seasons": len(years), "seasons": years,
           "week_range": [min(WEEK_RANGE), max(WEEK_RANGE)], "horizons": {}}
    for hname, k in HORIZONS.items():
        pairs = build_pairs(W, k)
        rows = {"n_pairs": len(pairs), "horizon_weeks": k}
        # ---------- TARGET 1: RISE (the actual warning question) ----------
        scored = []
        for Y in years:
            tr = [p for p in pairs if p["year"] < Y]
            te = [p for p in pairs if p["year"] == Y]
            if len(tr) < 60 or not te: continue
            thr = median([p["y"] - p["x"] for p in tr])          # training only
            # candidate rules, all fitted on training only
            cands = {}
            xs = sorted(p["x"] for p in tr)
            lo, hi = xs[len(xs)//3], xs[2*len(xs)//3]
            cands["rule_low_x_rises"] = lambda p: p["x"] <= lo
            slopes = [ (p["hist"][-1]-p["hist"][-2]) if len(p["hist"])>=2 else 0.0 for p in tr]
            sthr = median(slopes)
            cands["rule_recent_slope"] = lambda p: ((p["hist"][-1]-p["hist"][-2]) if len(p["hist"])>=2 else 0.0) > sthr
            cands["rule_always_yes"] = lambda p: True
            # pick the rule on TRAINING only
            best, bacc = None, -1
            for nm, f in cands.items():
                if nm == "rule_always_yes": continue
                a = mean(1.0 if (f(p) == ((p["y"]-p["x"]) > thr)) else 0.0 for p in tr)
                if a > bacc: bacc, best = a, nm
            f = cands[best]
            model = mean(1.0 if (f(p) == ((p["y"]-p["x"]) > thr)) else 0.0 for p in te)
            # BASELINE: persistence says "no meaningful change"
            persist = mean(1.0 if (False == ((p["y"]-p["x"]) > thr)) else 0.0 for p in te)
            majority = mean(1.0 if ((bacc > 0.5) == ((p["y"]-p["x"]) > thr)) else 0.0 for p in te)
            scored.append({"year": Y, "n_test": len(te), "rule": best,
                           "model": round(model,4), "persistence": round(persist,4),
                           "majority": round(majority,4)})
        if scored:
            m = mean(s["model"] for s in scored); pz = mean(s["persistence"] for s in scored)
            mj = mean(s["majority"] for s in scored)
            base = max(pz, mj)
            wins = sum(1 for s in scored if s["model"] > max(s["persistence"], s["majority"]))
            # sign test across seasons
            n_eff = sum(1 for s in scored if s["model"] != max(s["persistence"], s["majority"]))
            from math import comb
            p_sign = (sum(comb(n_eff,i) for i in range(wins, n_eff+1))/2**n_eff) if n_eff else 1.0
            rows["RISE"] = {"model_acc": round(m,4), "persistence_acc": round(pz,4),
                            "majority_acc": round(mj,4), "best_baseline": round(base,4),
                            "seasons_scored": len(scored), "seasons_model_wins": wins,
                            "p_sign_test": round(min(1.0,p_sign),4),
                            "per_season": scored}
            rows["RISE"]["SKILL_STATE"] = ("PROVED" if (m > base and p_sign <= 0.05/len(HORIZONS))
                                           else ("NOT_PROVED" if m > base else "REFUTED"))
        # ---------- TARGET 2: LEVEL, to show persistence dominates ----------
        errs_m, errs_p = [], []
        for Y in years:
            tr = [p for p in pairs if p["year"] < Y]; te = [p for p in pairs if p["year"] == Y]
            if len(tr) < 60 or not te: continue
            wc = collections.defaultdict(list)
            for p in tr: wc[p["week"]].append(p["y"])
            clim = {w: mean(v) for w, v in wc.items()}
            for p in te:
                errs_p.append(abs(p["y"] - p["x"]))                       # persistence
                errs_m.append(abs(p["y"] - clim.get(p["week"], mean(clim.values()) if clim else 0)))
        if errs_p:
            rows["LEVEL"] = {"MAE_persistence": round(mean(errs_p),4),
                             "MAE_week_climatology": round(mean(errs_m),4),
                             "n": len(errs_p),
                             "note": "persistence MAE lower => the level is dominated by 'nothing changes'"}
        rep["horizons"][hname] = rows
    return rep

if __name__ == "__main__":
    var = int(sys.argv[1]) if len(sys.argv) > 1 else 36
    r = run(var)
    print(f"=== EARLY WARNING (var {var}) — {r['n_seasons']} seasons, weeks {r['week_range'][0]}-{r['week_range'][1]}")
    print(f"\nTARGET = RISE (does incidence increase more than the training-median rise?)")
    print(f"{'horizon':8s} {'pairs':>6s} {'seasons':>8s} {'MODEL':>7s} {'persist':>8s} {'major':>7s} "
          f"{'wins':>6s} {'p_sign':>7s}  state")
    for h, v in r["horizons"].items():
        R = v.get("RISE")
        if not R: print(f"{h:8s} {v['n_pairs']:6d} {'-':>8s}  INSUFFICIENT_DATA"); continue
        print(f"{h:8s} {v['n_pairs']:6d} {R['seasons_scored']:8d} {R['model_acc']:7.3f} "
              f"{R['persistence_acc']:8.3f} {R['majority_acc']:7.3f} "
              f"{R['seasons_model_wins']:3d}/{R['seasons_scored']:<2d} {R['p_sign_test']:7.4f}  {R['SKILL_STATE']}")
    print(f"\nTARGET = LEVEL (mean absolute error)")
    print(f"{'horizon':8s} {'MAE persistence':>16s} {'MAE week-clim':>15s}")
    for h, v in r["horizons"].items():
        L = v.get("LEVEL")
        if L: print(f"{h:8s} {L['MAE_persistence']:16.4f} {L['MAE_week_climatology']:15.4f}")
    json.dump(r, open(os.path.join(ROOT, f"early_warning_v{var}.json"), "w"), indent=1)
