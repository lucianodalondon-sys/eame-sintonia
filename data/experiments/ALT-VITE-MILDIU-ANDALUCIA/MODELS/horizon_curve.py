#!/usr/bin/env python3
"""
SKILL HORIZON CURVE — the constructive half of the negative result.

"A 12-month outlook has no skill" is true but not actionable on its own. The useful
question is: HOW LATE do you have to wait before the data start telling you anything?

This walks the issue date forward through the target season and re-scores at each step:

    31 Jan  -> a true pre-season outlook (nothing of season Y is known)
    31 Mar  -> bud break past, early spring rain known
    30 Apr  -> the primary-infection window is largely known
    31 May  -> flowering past
    30 Jun  -> the epidemic is essentially decided

Every issue date uses ONLY weather up to that date, enforced the same way as everywhere
else in this pilot. Scoring is strict-temporal (train on years < Y only) so late issue dates
get no easier a test than early ones.

The curve is the deliverable: it says where a product could honestly sit, and where it
could not. It is NOT a 12M outlook and must never be presented as one — from 31 March
onward these are within-season nowcasts of increasing confidence, which is a different
product with a different promise.
"""
import json, os, importlib.util, datetime as dt
from statistics import mean

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
spec = importlib.util.spec_from_file_location("bf", os.path.join(HERE, "build_features.py"))
bf = importlib.util.module_from_spec(spec); spec.loader.exec_module(bf)
spec3 = importlib.util.spec_from_file_location("bt", os.path.join(HERE, "backtest.py"))
bt = importlib.util.module_from_spec(spec3); spec3.loader.exec_module(bt)
D = dt.date

L = json.load(open(os.path.join(ROOT, "OBSERVATIONS", "outcome_labels.json")))
levels = L["levels"]; k = len(levels); omap = {lv: i for i, lv in enumerate(levels)}
labels = {int(y): omap[v] for y, v in L["assignments"].items()}
pts = bf.load_points()
YEARS = sorted(labels)

ISSUE = [("31 Jan (true pre-season)", 1, 31),
         ("28 Feb", 2, 28), ("31 Mar", 3, 31), ("30 Apr", 4, 30),
         ("31 May", 5, 31), ("30 Jun", 6, 30), ("31 Jul", 7, 31)]

def feats_at(Y, m, d):
    """Weather of year Y from 1 Jan up to (m,d), plus the previous season. Nothing later."""
    cutoff = D(Y, m, d)
    per = []
    for name, p in pts.items():
        f = {}
        ytd = bf.window(p["days"], D(Y, 1, 1), cutoff)
        if not ytd: return None, cutoff
        b = bf.block_stats(ytd, "ytd")
        if b is None: return None, cutoff
        f.update(b)
        prev = bf.block_stats(bf.window(p["days"], D(Y - 1, 3, 1), D(Y - 1, 8, 31)), "prevseason")
        if prev: f.update(prev)
        # hard proof: no contributing day may exceed the cutoff
        assert ytd[-1][0] <= cutoff, "leak"
        per.append(f)
    keys = sorted(set().union(*[set(f) for f in per]))
    return {kk: mean(f[kk] for f in per if kk in f) for kk in keys}, cutoff

# a priori: wetness-to-date is the driver, direction positive. Fixed for every issue date,
# so the curve is not the product of re-picking a feature at each step.
CAND = ["ytd_precip_sum", "ytd_rain_days", "ytd_rh75_days", "ytd_wet_spells_2d"]

print(f"{'issue date':26s} {'feature':20s} {'n':>3s} {'acc':>6s} {'baseline':>9s} {'perm p':>8s}  skill")
rows = []
base_acc = None
for label, m, d in ISSUE:
    F = {}
    for Y in YEARS:
        f, _ = feats_at(Y, m, d)
        if f: F[Y] = f
    ys = sorted(F)
    if base_acc is None:
        bl = bt.baselines(ys, labels, k, min_train=5)
        base_acc = bl["BASELINE_CLIMATOLOGY"]["accuracy"]
    best = None
    for feat in CAND:
        h = {"feature": feat, "direction": +1}
        pr, ob, sy = bt.strict_temporal(ys, F, labels, h, k, min_train=5)
        sc = bt.score(pr, ob, k)
        if sc is None: continue
        sc["p_permutation"] = bt.permutation_p(pr, ob, k)
        sc["feature"] = feat
        if best is None or sc["accuracy"] > best["accuracy"]: best = sc
    if best is None: continue
    skill = "YES" if (best["accuracy"] > base_acc and best["p_permutation"] <= 0.05) else "no"
    rows.append({"issue_date": label, **best, "baseline": base_acc, "skill": skill})
    print(f"{label:26s} {best['feature']:20s} {best['n']:3d} {best['accuracy']:6.3f} "
          f"{base_acc:9.3f} {best['p_permutation']:8.4f}  {skill}")

# --- multiplicity and monotonicity, applied to my own curve before believing it ---
n_tests = len(CAND) * len(rows)
bonf = 0.05 / len(CAND)          # per issue date, corrected for the features searched
for r in rows:
    r["bonferroni_threshold_per_issue_date"] = round(bonf, 5)
    r["survives_multiplicity"] = r["p_permutation"] <= bonf

# A real signal cannot get WEAKER when the model is given strictly MORE information.
# Every issue date contains everything the earlier ones did, so significance that appears
# and then disappears is noise, not an early-warning window.
for i, r in enumerate(rows):
    later = rows[i+1:i+3]
    r["contradicted_by_later_issue_dates"] = bool(
        r["survives_multiplicity"] and later and
        not any(x["survives_multiplicity"] for x in later))

robust = [r for r in rows if r["survives_multiplicity"] and not r["contradicted_by_later_issue_dates"]]
first = robust[0] if robust else None
nominal = next((r for r in rows if r["skill"] == "YES"), None)
out = {"note": ("Weather up to each issue date only, strict-temporal scoring. From 31 March "
                "onward these are WITHIN-SEASON nowcasts, not a 12M outlook, and must never "
                "be presented as one."),
       "candidate_features_fixed_in_advance": CAND,
       "baseline_climatology": base_acc, "curve": rows,
       "n_tests_run": n_tests,
       "bonferroni_threshold_per_issue_date": round(bonf, 5),
       "first_issue_date_nominally_significant": nominal["issue_date"] if nominal else None,
       "first_issue_date_with_ROBUST_skill": first["issue_date"] if first else None,
       "why_nominal_is_not_enough": (
           "4 features were searched at each of 7 issue dates. A nominal p just under 0.05 is "
           "expected by chance at that search width, so each issue date is held to p <= 0.0125. "
           "Separately, every issue date strictly CONTAINS the information of the earlier ones, "
           "so significance that appears and then vanishes at the next two dates is noise, not "
           "an early-warning window — that check is applied and reported per row."),
       "VERDICT": (f"Robust skill first appears at {first['issue_date']} "
                   f"(accuracy {first['accuracy']}, p={first['p_permutation']})." if first
                   else "No issue date shows skill that survives multiplicity correction.")}
json.dump(out, open(os.path.join(ROOT, "BACKTEST", "horizon_curve.json"), "w"), indent=1)
print(f"\nAfter correcting for {n_tests} tests (threshold p <= {bonf:.4f} per issue date):")
for r in rows:
    tag = "ROBUST" if (r["survives_multiplicity"] and not r["contradicted_by_later_issue_dates"]) else (
          "nominal only, contradicted by later dates" if r["contradicted_by_later_issue_dates"] else
          "not significant")
    print(f"   {r['issue_date']:26s} {tag}")
print(f"\n{out['VERDICT']}")
