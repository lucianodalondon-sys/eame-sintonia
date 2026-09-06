#!/usr/bin/env python3
"""
Honest backtest harness for a SEASONAL (12M/24M) outlook on Veneto vine peronospora.

The harness is deliberately hostile to its own hypothesis.

  1. BASELINES FIRST. Three of them. If the model does not beat all three,
     MODEL_HAS_SKILL = NO and we stop selling a forecast.
        BASELINE_CLIMATOLOGY  predict the modal class of the training years
        BASELINE_PERSISTENCE  predict last year's class
        BASELINE_UNIFORM      1/k, reported as the floor
  2. NO FEATURE SELECTION ON THE TEST YEAR. Hypotheses are stated a priori,
     in HYPOTHESES below, written before any label was read. A model that
     picks its feature by looking at all 12 labels is reported separately and
     labelled OVERFIT_DEMONSTRATION, never as evidence.
  3. STRICT TEMPORAL BACKTEST is primary: to score year Y, train ONLY on
     years < Y. Leave-one-year-out is reported second, as the optimistic bound.
  4. PERMUTATION TEST. With n<=12 a good-looking accuracy is cheap. Every
     score is accompanied by the probability of doing that well by chance,
     from label shuffles.
  5. Ordinal metrics, not just accuracy: mean absolute class distance, and
     the count of 2-class blunders (predicting HIGH when it was LOW).
"""
import json, os, sys, itertools, random
from statistics import mean, median

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

# --- A PRIORI hypotheses. Written from peronospora biology, not from the labels.
HYPOTHESES = [
    {"id": "H1_prev_season_rain",
     "feature": "prevseason_precip_sum",
     "direction": +1,
     "biology": "A wet previous season means more leaf/berry lesions, therefore more "
                "oospores dropped into the litter, therefore more primary inoculum next spring."},
    {"id": "H2_winter_wet_mild",
     "feature": "winter_precip_sum",
     "direction": +1,
     "biology": "Oospores need moisture to mature and survive; a wet winter should raise "
                "the primary-infection potential."},
    {"id": "H3_autumn_rain",
     "feature": "autumn_precip_sum",
     "direction": +1,
     "biology": "Autumn rain both feeds late sporulation and buries inoculum in wet litter."},
    {"id": "H4_prev_season_wet_days",
     "feature": "prevseason_rain_days",
     "direction": +1,
     "biology": "Number of infection events last season is a better inoculum proxy than total mm."},
    {"id": "H5_winter_mild",
     "feature": "winter_tmean",
     "direction": +1,
     "biology": "A mild winter should reduce oospore mortality."},
]

def ordinal_map(levels):
    return {lv: i for i, lv in enumerate(levels)}

# ------------------------------------------------------------------ predictors
def tercile_rule(train_pairs, x, direction, k):
    """train_pairs: [(feature_value, class_index)]. Predict by placing x in the
    feature terciles ESTIMATED ON TRAINING YEARS ONLY, then mapping tercile->class
    monotonically in `direction`. No label of the test year is touched."""
    if len(train_pairs) < 3:
        return None
    vals = sorted(v for v, _ in train_pairs)
    if k <= 1:
        return 0
    cuts = [vals[int(round(i * (len(vals) - 1) / k))] for i in range(1, k)]
    band = sum(1 for c in cuts if x > c)          # 0..k-1
    return band if direction > 0 else (k - 1 - band)

def climatology(train_classes, k):
    if not train_classes:
        return None
    counts = {c: train_classes.count(c) for c in set(train_classes)}
    best = max(counts.values())
    tied = sorted([c for c, n in counts.items() if n == best])
    if len(tied) == 1:
        return tied[0]
    return tied[len(tied) // 2]                    # deterministic middle tie-break

def persistence(prev_class):
    return prev_class

# ------------------------------------------------------------------ scoring
def score(pred, obs, k):
    pairs = [(p, o) for p, o in zip(pred, obs) if p is not None and o is not None]
    if not pairs:
        return None
    n = len(pairs)
    acc = sum(1 for p, o in pairs if p == o) / n
    mad = mean(abs(p - o) for p, o in pairs)
    blunders = sum(1 for p, o in pairs if abs(p - o) >= 2)
    return {"n": n, "accuracy": round(acc, 4), "mean_abs_class_dist": round(mad, 4),
            "blunders_2class": blunders}

def permutation_p(pred, obs, k, n_perm=20000, seed=20260906):
    """P(chance accuracy >= observed) under label shuffling."""
    pairs = [(p, o) for p, o in zip(pred, obs) if p is not None and o is not None]
    if len(pairs) < 3:
        return None
    P = [p for p, _ in pairs]; O = [o for _, o in pairs]
    obs_hits = sum(1 for p, o in zip(P, O) if p == o)
    rng = random.Random(seed)
    shuf = list(O); ge = 0
    for _ in range(n_perm):
        rng.shuffle(shuf)
        if sum(1 for p, o in zip(P, shuf) if p == o) >= obs_hits:
            ge += 1
    return round((ge + 1) / (n_perm + 1), 5)

# ------------------------------------------------------------------ backtests
def strict_temporal(years, feats, labels, hyp, k, min_train=5):
    """Score year Y using only years < Y. This is the honest one."""
    pred, obs, scored_years = [], [], []
    for i, Y in enumerate(years):
        train = [y for y in years[:i] if labels.get(y) is not None]
        if len(train) < min_train or labels.get(Y) is None:
            continue
        tp = [(feats[y][hyp["feature"]], labels[y]) for y in train if hyp["feature"] in feats.get(y, {})]
        if hyp["feature"] not in feats.get(Y, {}):
            continue
        p = tercile_rule(tp, feats[Y][hyp["feature"]], hyp["direction"], k)
        pred.append(p); obs.append(labels[Y]); scored_years.append(Y)
    return pred, obs, scored_years

def loyo(years, feats, labels, hyp, k):
    """Leave-one-year-out: optimistic bound, reported second."""
    pred, obs, scored_years = [], [], []
    for Y in years:
        if labels.get(Y) is None or hyp["feature"] not in feats.get(Y, {}):
            continue
        train = [y for y in years if y != Y and labels.get(y) is not None and hyp["feature"] in feats.get(y, {})]
        tp = [(feats[y][hyp["feature"]], labels[y]) for y in train]
        p = tercile_rule(tp, feats[Y][hyp["feature"]], hyp["direction"], k)
        pred.append(p); obs.append(labels[Y]); scored_years.append(Y)
    return pred, obs, scored_years

def baselines(years, labels, k, min_train=5):
    out = {}
    for name in ("BASELINE_CLIMATOLOGY", "BASELINE_PERSISTENCE"):
        pred, obs, sy = [], [], []
        for i, Y in enumerate(years):
            train = [labels[y] for y in years[:i] if labels.get(y) is not None]
            if len(train) < min_train or labels.get(Y) is None:
                continue
            if name == "BASELINE_CLIMATOLOGY":
                p = climatology(train, k)
            else:
                prev = [y for y in years[:i] if labels.get(y) is not None]
                p = persistence(labels[prev[-1]]) if prev else None
            pred.append(p); obs.append(labels[Y]); sy.append(Y)
        s = score(pred, obs, k)
        if s:
            s["years_scored"] = sy
            s["p_permutation"] = permutation_p(pred, obs, k)
        out[name] = s
    out["BASELINE_UNIFORM"] = {"accuracy": round(1.0 / k, 4),
                               "note": "theoretical floor for k equiprobable classes"}
    return out

# ------------------------------------------------------------------ runner
def run(labels_path, regime="CUTOFF_A_PRESEASON", min_train=5):
    F = json.load(open(os.path.join(ROOT, "MODELS", "features_cutoff_respecting.json")))
    assert F[regime]["TARGET_SEASON_WEATHER_LEAKAGE"] == 0, "REFUSING TO RUN: leakage detected"
    feats = {int(y): v for y, v in F[regime]["features"].items()}

    L = json.load(open(labels_path))
    levels = L["levels"]                       # ordered, low -> high
    k = len(levels)
    omap = ordinal_map(levels)
    labels = {}
    for y, lv in L["assignments"].items():
        labels[int(y)] = omap.get(lv)          # None for NOT_ASSIGNABLE
    years = sorted(set(feats) & set(labels))
    labelled = [y for y in years if labels[y] is not None]

    report = {
        "scale_name": L.get("scale_name"),
        "levels": levels,
        "regime": regime,
        "TARGET_SEASON_WEATHER_LEAKAGE": 0,
        "years_with_features": sorted(feats),
        "years_with_labels": labelled,
        "n_labelled": len(labelled),
        "min_train": min_train,
        "baselines": baselines(years, labels, k, min_train),
        "hypotheses": [],
        "overfit_demonstration": None,
    }

    for h in HYPOTHESES:
        entry = {"id": h["id"], "feature": h["feature"], "direction": h["direction"],
                 "biology": h["biology"], "stated_a_priori": True}
        p, o, sy = strict_temporal(years, feats, labels, h, k, min_train)
        s = score(p, o, k)
        if s:
            s["years_scored"] = sy
            s["p_permutation"] = permutation_p(p, o, k)
        entry["strict_temporal"] = s
        p2, o2, sy2 = loyo(years, feats, labels, h, k)
        s2 = score(p2, o2, k)
        if s2:
            s2["years_scored"] = sy2
            s2["p_permutation"] = permutation_p(p2, o2, k)
        entry["leave_one_year_out"] = s2
        report["hypotheses"].append(entry)

    # what the best a-priori hypothesis achieved, vs the baselines
    base_acc = max([v["accuracy"] for kk, v in report["baselines"].items()
                    if v and "accuracy" in v] or [0])
    cands = [h for h in report["hypotheses"] if h["strict_temporal"]]
    best = max(cands, key=lambda h: h["strict_temporal"]["accuracy"]) if cands else None
    report["best_a_priori_hypothesis"] = best["id"] if best else None
    report["best_a_priori_accuracy"] = best["strict_temporal"]["accuracy"] if best else None
    report["best_baseline_accuracy"] = base_acc
    if best is None:
        report["MODEL_HAS_SKILL"] = "NOT_TESTABLE"
        report["skill_reason"] = "no hypothesis could be scored (too few labelled years)"
    else:
        beats = best["strict_temporal"]["accuracy"] > base_acc
        pval = best["strict_temporal"].get("p_permutation")
        sig = pval is not None and pval <= 0.05
        report["MODEL_HAS_SKILL"] = "YES" if (beats and sig) else "NO"
        report["skill_reason"] = (
            f"best a-priori rule {best['id']} scored {best['strict_temporal']['accuracy']} "
            f"vs best baseline {base_acc} (permutation p={pval}); "
            + ("beats baseline AND survives permutation" if (beats and sig)
               else "does NOT clear both bars — a seasonal outlook must not be sold as a forecast")
        )
        # honest multiplicity note: we tried len(HYPOTHESES) hypotheses
        report["multiplicity_note"] = (
            f"{len(HYPOTHESES)} a-priori hypotheses were tested. A Bonferroni-corrected "
            f"threshold is p <= {round(0.05/len(HYPOTHESES),4)}; the best hypothesis "
            + ("clears" if (pval is not None and pval <= 0.05/len(HYPOTHESES)) else "does NOT clear")
            + " it."
        )

    # OVERFIT DEMONSTRATION: pick the best feature using all labels. Never evidence.
    allf = sorted(set().union(*[set(feats[y]) for y in years])) if years else []
    bestf, bestacc = None, -1
    for f in allf:
        for dirn in (+1, -1):
            h = {"feature": f, "direction": dirn}
            p, o, sy = loyo(years, feats, labels, h, k)
            s = score(p, o, k)
            if s and s["accuracy"] > bestacc:
                bestacc, bestf = s["accuracy"], (f, dirn, s)
    if bestf:
        report["overfit_demonstration"] = {
            "WARNING": "This feature was chosen by looking at the answers. It is NOT evidence of skill.",
            "n_features_searched": len(allf) * 2,
            "feature": bestf[0], "direction": bestf[1], "loyo_accuracy": bestf[2]["accuracy"],
            "interpretation": (
                f"Searching {len(allf)*2} feature/direction combinations on {len(labelled)} labelled "
                f"years reaches {bestf[2]['accuracy']} by selection alone. Any headline number near "
                f"this that was not pre-registered is noise."),
        }
    return report

if __name__ == "__main__":
    lp = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "OBSERVATIONS", "outcome_labels.json")
    if not os.path.exists(lp):
        print(f"NO LABELS YET at {lp}")
        print("Harness is ready. It will run the moment the verified outcome scale lands.")
        sys.exit(0)
    regimes = ["CUTOFF_A_PRESEASON", "CUTOFF_B_TRUE_12M"]
    allrep = {}
    for rg in regimes:
        allrep[rg] = run(lp, rg)
    dest = os.path.join(ROOT, "BACKTEST", "backtest_report.json")
    json.dump(allrep, open(dest, "w"), indent=1)
    for rg, r in allrep.items():
        print(f"\n===== {rg} =====")
        print(f"labelled years: {r['n_labelled']}  {r['years_with_labels']}")
        for kk, v in r["baselines"].items():
            print(f"  {kk:24s} {v}")
        for h in r["hypotheses"]:
            print(f"  {h['id']:24s} strict={h['strict_temporal']}")
        print(f"  MODEL_HAS_SKILL = {r['MODEL_HAS_SKILL']}")
        print(f"  {r['skill_reason']}")
        if r.get("overfit_demonstration"):
            print(f"  OVERFIT DEMO: {r['overfit_demonstration']['loyo_accuracy']} by pure selection")
    print(f"\nwrote {dest}")
