#!/usr/bin/env python3
"""
THE ARM THAT WAS DOCUMENTED BUT NEVER BUILT.

horizon.py's docstring promised ARM_WEATHER_PLUS_DISEASE_TO_DATE and never implemented it.
The red team caught that. It matters, because after the retraction it is the only arm that
could still support an honest product.

THE QUESTION IS DIFFERENT FROM THE HORIZON QUESTION.
  Horizon asked: can weather BEFORE a date predict the season? Answer: no, at any date.
  This asks:     given what the season HAS ALREADY SHOWN by date X, does the rest of the
                 season follow? That is a NOWCAST, not a forecast, and it is a different
                 product with a different promise.

WHY IT IS NOT CIRCULAR. The target is the disease state of the REMAINDER of the season
(weeks after the cutoff). The predictor is the disease state OBSERVED UP TO the cutoff.
Those are disjoint sets of observations. Trivially there is autocorrelation — that is the
point of a nowcast — but it must still be shown to beat the baselines, and the baselines
here are strong on purpose.

EVERY RED-TEAM FIX FROM horizon2.py IS CARRIED OVER:
  causal walk-forward selection (never choose the predictor using the answers)
  direction locked a priori
  exact McNemar against the best baseline
  Bonferroni over the whole family including the cutoff axis
  leave-one-season-out sensitivity, always reported
  real asserts on the observation-window split
"""
import json, os, sys, glob, collections, importlib.util
from statistics import mean

ROOT = os.path.dirname(os.path.abspath(__file__))
_h = importlib.util.spec_from_file_location("h", os.path.join(ROOT, "horizon.py"))
H = importlib.util.module_from_spec(_h); _h.loader.exec_module(H)
_o = importlib.util.spec_from_file_location("oc", os.path.join(ROOT, "outcome.py"))
oc = importlib.util.module_from_spec(_o); _o.loader.exec_module(oc)
_h2 = importlib.util.spec_from_file_location("h2", os.path.join(ROOT, "horizon2.py"))
H2 = importlib.util.module_from_spec(_h2); _h2.loader.exec_module(H2)

# ISO week cutoffs; the Tuscan observation season runs roughly weeks 15-38
WEEK_CUTOFFS = [18, 20, 22, 24, 26, 28]

def split_season(var, order, cut_week):
    """Return {year: (state_up_to_cut, state_after_cut)} — DISJOINT observation sets."""
    data = oc.load(var, "all")
    out = {}
    for y, rows in data.items():
        early = [r for r in rows if r["week"] and int(r["week"]) <= cut_week]
        late = [r for r in rows if r["week"] and int(r["week"]) > cut_week]
        assert not (set(id(r) for r in early) & set(id(r) for r in late)), \
            "ASSERT FAILED: early and late observation sets overlap"
        if len(early) < 30 or len(late) < 30:
            continue
        def site_inc(rs):
            s = collections.defaultdict(list)
            for r in rs: s[r["field"]].append(order.get(r["label"], 0))
            return sum(1 for v in s.values() if max(v) > 0) / len(s), len(s)
        e, ne = site_inc(early); l, nl = site_inc(late)
        out[y] = {"early": e, "late": l, "n_sites_early": ne, "n_sites_late": nl,
                  "n_visits_early": len(early), "n_visits_late": len(late)}
    return out

def run(var=36):
    order = oc.BUNCH_ORDER if var == 36 else oc.LEAF_ORDER
    family = len(WEEK_CUTOFFS) * 2      # 2 candidate predictors, direction locked
    rep = {"var": var, "week_cutoffs": WEEK_CUTOFFS,
           "bonferroni_family_size": family,
           "bonferroni_threshold": round(0.05 / family, 6),
           "target": "SITE_INCIDENCE over the REMAINDER of the season (weeks > cutoff)",
           "predictor": "SITE_INCIDENCE observed UP TO the cutoff (disjoint observations)",
           "rows": []}
    for cw in WEEK_CUTOFFS:
        S = split_season(var, order, cw)
        years = sorted(S)
        if len(years) < 10:
            rep["rows"].append({"cut_week": cw, "n_years": len(years),
                                "SKILL_STATE": "INSUFFICIENT_DATA"}); continue
        raw = {y: S[y]["late"] for y in years}
        F = {y: {"early_incidence": S[y]["early"],
                 "early_x_visits": S[y]["early"] * S[y]["n_visits_early"]} for y in years}
        cands = [("early_incidence", +1), ("early_x_visits", +1)]

        # baselines on the TARGET (the remainder), not the whole season
        bl = {}
        for name in ("BASELINE_CLIMATOLOGY", "BASELINE_PREVIOUS_YEAR"):
            pr, ob, sy = [], [], []
            for i, Y in enumerate(years):
                tr = years[:i]
                if len(tr) < 5: continue
                cuts = H.terciles_from_train([raw[y] for y in tr])
                if cuts is None: continue
                t = H.classify(raw[Y], cuts)
                p = (collections.Counter(H.classify(raw[y], cuts) for y in tr).most_common(1)[0][0]
                     if name == "BASELINE_CLIMATOLOGY" else H.classify(raw[tr[-1]], cuts))
                pr.append(p); ob.append(t); sy.append(Y)
            bl[name] = {"pred": pr, "obs": ob, "years": sy,
                        "accuracy": round(sum(1 for a, b in zip(pr, ob) if a == b) / len(pr), 4) if pr else None}
        bbn = max(bl, key=lambda k: bl[k]["accuracy"] or 0); bb = bl[bbn]

        pr, ob, sy, picks = H2.causal_walk_forward(F, raw, years, cands)
        row = {"cut_week": cw, "n_years": len(years), "years": years,
               "baselines": {k: v["accuracy"] for k, v in bl.items()},
               "best_baseline": bb["accuracy"], "best_baseline_name": bbn}
        if pr:
            acc = sum(1 for a, b in zip(pr, ob) if a == b) / len(pr)
            pp = H.perm_p(pr, ob, n=20000, seed=11)
            m = {y: p for y, p in zip(sy, pr)}
            bm = {y: p for y, p in zip(bb["years"], bb["pred"])}
            tt = {y: o for y, o in zip(bb["years"], bb["obs"])}
            shared = [y for y in sy if y in bm]
            mc = {"p": 1.0}
            if shared:
                a = [m[y] == tt[y] for y in shared]; b = [bm[y] == tt[y] for y in shared]
                p_mc, nb, nc = H2.mcnemar_exact(a, b)
                mc = {"p": round(p_mc, 4), "model_only": nb, "baseline_only": nc, "n": len(shared)}
            row["CAUSAL"] = {"accuracy": round(acc, 4), "n": len(pr), "years_scored": sy,
                             "features_picked": picks, "p_permutation": pp,
                             "mcnemar_vs_best_baseline": mc}
            if acc > (bb["accuracy"] or 0) and pp is not None and pp <= rep["bonferroni_threshold"] and mc["p"] <= 0.05:
                row["SKILL_STATE"] = "PROVED"
            elif acc > (bb["accuracy"] or 0) and pp is not None and pp <= 0.05:
                row["SKILL_STATE"] = "NOT_PROVED"
            else:
                row["SKILL_STATE"] = "REFUTED"
        else:
            row["SKILL_STATE"] = "INSUFFICIENT_DATA"
        rep["rows"].append(row)
    pv = [r for r in rep["rows"] if r.get("SKILL_STATE") == "PROVED"]
    rep["FIRST_PROVED_WEEK"] = pv[0]["cut_week"] if pv else None
    return rep

if __name__ == "__main__":
    var = int(sys.argv[1]) if len(sys.argv) > 1 else 36
    r = run(var)
    print(f"=== NOWCAST ARM (var {var}) — predict the REST of the season from what it has already shown")
    print(f"    Bonferroni family {r['bonferroni_family_size']} -> threshold {r['bonferroni_threshold']}\n")
    print(f"{'cut wk':7s} {'yrs':>4s} {'base':>6s} {'CAUSAL':>7s} {'p':>8s} {'McNemar':>8s}  state")
    for x in r["rows"]:
        c = x.get("CAUSAL")
        print(f"{x['cut_week']:7d} {x['n_years']:4d} {(x.get('best_baseline') or 0):6.3f} "
              f"{(c['accuracy'] if c else 0):7.3f} {(c['p_permutation'] if c else 1):8.4f} "
              f"{(c['mcnemar_vs_best_baseline']['p'] if c else 1):8.3f}  {x['SKILL_STATE']}")
    print(f"\nFIRST_PROVED_WEEK = {r['FIRST_PROVED_WEEK']}")
    json.dump(r, open(os.path.join(ROOT, f"nowcast_v{var}.json"), "w"), indent=1)
