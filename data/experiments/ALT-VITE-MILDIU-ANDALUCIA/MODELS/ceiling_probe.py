#!/usr/bin/env python3
"""
CEILING PROBE — is the outcome predictable from weather AT ALL?

MODEL_HAS_SKILL = NO has two very different explanations, and they lead to opposite
recommendations:

  (A) The disease index is real and weather-driven, but the drivers are the TARGET SEASON's
      own weather, which is unknowable in advance. Then a 12-month outlook is impossible in
      principle, and the honest product is a within-season warning, which already exists.

  (B) The disease index is mostly noise / sampling composition. Then no weather model of
      any horizon would work, and the outcome itself is the problem.

This distinguishes them. It deliberately CHEATS: it predicts season Y using season Y's own
weather. That is not a forecast and is never presented as one — it is the ceiling any
honest forecast must sit below. If even the cheating model cannot beat climatology, the
outcome is noise (B). If the cheating model does well and the antecedent model does not,
the pathway is real but not knowable in advance (A).

Written to EVIDENCE/, never to BACKTEST/, and never read by backtest.py.
"""
import json, os, sys, importlib.util, random
from statistics import mean, pstdev

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
spec = importlib.util.spec_from_file_location("bf", os.path.join(HERE, "build_features.py"))
bf = importlib.util.module_from_spec(spec); spec.loader.exec_module(bf)
spec2 = importlib.util.spec_from_file_location("cp", os.path.join(HERE, "circularity_probe.py"))
cp = importlib.util.module_from_spec(spec2); spec2.loader.exec_module(cp)
spec3 = importlib.util.spec_from_file_location("bt", os.path.join(HERE, "backtest.py"))
bt = importlib.util.module_from_spec(spec3); spec3.loader.exec_module(bt)

L = json.load(open(os.path.join(ROOT, "OBSERVATIONS", "outcome_labels.json")))
levels = L["levels"]; k = len(levels); omap = {lv: i for i, lv in enumerate(levels)}
labels = {int(y): omap[v] for y, v in L["assignments"].items()}
raw = {int(y): v for y, v in L["raw_values_pct"].items()}

pts = bf.load_points()
years = sorted(labels)
ts = {Y: cp.target_season_weather(pts, Y) for Y in years}
ts = {Y: v for Y, v in ts.items() if v}
feat_names = sorted(next(iter(ts.values())).keys())

def rank(v):
    o = sorted(range(len(v)), key=lambda i: v[i]); r = [0]*len(v)
    for pos, i in enumerate(o): r[i] = pos
    return r
def pear(a, b):
    ma, mb = mean(a), mean(b); sa, sb = pstdev(a), pstdev(b)
    return None if sa == 0 or sb == 0 else sum((x-ma)*(y-mb) for x, y in zip(a, b))/(len(a)*sa*sb)
def spear(a, b): return pear([float(x) for x in rank(a)], [float(x) for x in rank(b)])
def perm_p(a, b, N=20000, seed=1):
    obs = abs(spear(a, b) or 0); rng = random.Random(seed); bb = list(b); ge = 0
    for _ in range(N):
        rng.shuffle(bb)
        if abs(spear(a, bb) or 0) >= obs: ge += 1
    return (ge+1)/(N+1)

ys = sorted(set(ts) & set(labels))
tv = [raw[y] for y in ys]
print(f"TARGET-SEASON weather vs the observed mildiu index, n={len(ys)} seasons ({ys[0]}-{ys[-1]})")
print(f"{'feature':32s} {'rho':>7s} {'p':>8s}")
rows = []
for f in feat_names:
    fv = [ts[y][f] for y in ys]
    s = spear(fv, tv)
    if s is None: continue
    rows.append({"feature": f, "spearman": round(s, 3), "p_permutation": round(perm_p(fv, tv), 5)})
rows.sort(key=lambda r: -abs(r["spearman"]))
for r in rows: print(f"{r['feature']:32s} {r['spearman']:+7.3f} {r['p_permutation']:8.4f}")

# cheating classifier: same-season weather, leave-one-year-out
best = rows[0]
cheat = {"feature": best["feature"], "direction": 1 if best["spearman"] > 0 else -1}
pred, obs = [], []
for Y in ys:
    train = [(ts[y][cheat["feature"]], labels[y]) for y in ys if y != Y]
    p = bt.tercile_rule(train, ts[Y][cheat["feature"]], cheat["direction"], k)
    pred.append(p); obs.append(labels[Y])
sc = bt.score(pred, obs, k)
sc["p_permutation"] = bt.permutation_p(pred, obs, k)

BT = json.load(open(os.path.join(ROOT, "BACKTEST", "backtest_report.json")))
hon = max(h["strict_temporal"]["accuracy"] for r in BT.values()
          for h in r["hypotheses"] if h.get("strict_temporal"))
base = max(v["accuracy"] for r in BT.values() for v in r["baselines"].values() if v and "accuracy" in v)

print(f"\nCHEATING model (best target-season feature, chosen AFTER seeing the answers, LOYO): {sc}")
print(f"honest antecedent best: {hon}   climatology baseline: {base}")
maxrho = abs(rows[0]["spearman"])
if maxrho < 0.45 and sc["accuracy"] <= base:
    verdict = ("OUTCOME_IS_LARGELY_NOISE — even the target season's OWN weather, with the feature "
               "chosen after seeing the answers, cannot beat climatology. The limitation is the "
               "outcome, not the forecast horizon.")
elif sc["accuracy"] > base:
    verdict = ("PATHWAY_REAL_BUT_NOT_KNOWABLE_IN_ADVANCE — the season's own weather does predict the "
               "index, but antecedent weather does not. A 12M outlook is therefore blocked by the "
               "horizon, not by the data quality, and the honest product is a within-season warning.")
else:
    verdict = "AMBIGUOUS — neither reading is clearly supported."
out = {"note": "DIAGNOSTIC. Uses target-season weather deliberately. Never a forecast, never read by backtest.py.",
       "n_seasons": len(ys), "correlations": rows,
       "cheating_model": {"feature_chosen_after_seeing_answers": cheat["feature"], **sc},
       "honest_antecedent_best_accuracy": hon, "climatology_baseline": base,
       "max_abs_spearman": round(maxrho, 3), "VERDICT": verdict}
json.dump(out, open(os.path.join(ROOT, "EVIDENCE", "ceiling_probe.json"), "w"), indent=1)
print(f"\nVERDICT: {verdict}")
