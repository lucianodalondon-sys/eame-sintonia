#!/usr/bin/env python3
"""
ANALOG YEARS — the mechanism a 12M outlook would actually use.

Idea: for target season Y, find the k most similar PRIOR seasons using only
antecedent (cutoff-respecting) features, then state the outlook as the empirical
distribution of the outcome class among those analogs.

Why analogs rather than a fitted model, at n<=12:
  A fitted classifier on 12 labelled years with 40 features is not a model, it is a
  memorisation. Analogs make the reasoning inspectable: the user can see WHICH past
  seasons the outlook is standing on, and judge for themselves whether they are alike.

Two honesty constraints built in:
  1. The similarity space is a SMALL A-PRIORI feature set, fixed before any label was
     read, standardised on prior years only. No feature is chosen because it improved
     the answer.
  2. The analog pool for year Y contains only years < Y. An analog from the future is
     not an analog.

The percentages this produces are empirical frequencies among named analogs (k of n),
which is auditable. They are NOT a conversion of prose severity into a number: that
remains forbidden.
"""
import json, os, sys
from statistics import mean, pstdev

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

# fixed a priori similarity space: inoculum proxy, autumn/winter moisture, winter warmth
SIMILARITY_FEATURES = [
    "prevseason_precip_sum",     # last season's wetness -> inoculum produced
    "prevseason_rain_days",      # last season's infection opportunities
    "prevseason_rh75_days",      # last season's humid-day load
    "winter_precip_sum",         # oospore maturation moisture   (CUTOFF_A only)
    "winter_tmean",              # oospore overwinter mortality  (CUTOFF_A only)
    "autumn_precip_sum",         # litter wetness at leaf fall   (CUTOFF_A only)
]
SIMILARITY_FEATURES_B = [
    "prevseason_precip_sum", "prevseason_rain_days", "prevseason_rh75_days",
    "prevwinter_precip_sum", "prevwinter_tmean", "prevautumn_precip_sum",
]

def zspace(feats, years, names):
    """Standardise each feature over the given years. Returns {year: [z...]}"""
    usable = [n for n in names if all(n in feats.get(y, {}) for y in years)]
    stats = {}
    for n in usable:
        v = [feats[y][n] for y in years]
        stats[n] = (mean(v), pstdev(v) or 1.0)
    return {y: [(feats[y][n] - stats[n][0]) / stats[n][1] for n in usable] for y in years}, usable

def analogs_for(Y, feats, years, names, k=4):
    pool = [y for y in years if y < Y]
    if len(pool) < k + 1:
        return None
    Z, usable = zspace(feats, pool + [Y], names)   # standardised on pool+Y, no future years
    tv = Z[Y]
    d = []
    for y in pool:
        yv = Z[y]
        dist = sum((a - b) ** 2 for a, b in zip(tv, yv)) ** 0.5
        d.append({"year": y, "distance": round(dist, 3)})
    d.sort(key=lambda x: x["distance"])
    return {"target": Y, "k": k, "pool_size": len(pool),
            "features_used": usable, "analogs": d[:k], "all_distances": d}

def outlook(Y, feats, years, labels, levels, names, k=4):
    """
    Two analog pools, reported side by side, because they answer different questions.

      MET_POOL   every prior season with ERA5 features (back to 1992). Answers
                 "what did the run-up to this season look like, historically?"
                 Most of these years have NO disease label, so they cannot vote.
      LAB_POOL   prior seasons that actually carry a verified outcome class. Only
                 these can produce a distribution. There are at most 19 of them, ever.

    Reporting only the first would imply a depth of history the outcome does not have.
    Reporting only the second would hide that the nearest meteorological analogs are
    often years we know nothing about.
    """
    met = analogs_for(Y, feats, years, names, k)
    lab_years = [y for y in years if y < Y and labels.get(y) is not None]
    res = {"target": Y, "meteorological_analogs": met["analogs"] if met else None,
           "n_labelled_prior_seasons": len(lab_years)}

    if met:
        near_unlabelled = [a["year"] for a in met["analogs"] if labels.get(a["year"]) is None]
        res["nearest_analogs_without_an_outcome"] = near_unlabelled
        res["fraction_of_nearest_analogs_unlabelled"] = f"{len(near_unlabelled)}/{len(met['analogs'])}"

    if len(lab_years) < 3:
        res["status"] = "NOT_ENOUGH_LABELLED_HISTORY"
        res["note"] = (f"only {len(lab_years)} prior season(s) carry an outcome; an analog "
                       f"outlook needs at least 3 and is thin below 6")
        return res

    kk = min(k, len(lab_years))
    Z, usable = zspace(feats, lab_years + [Y], names)
    tv = Z[Y]
    d = sorted(({"year": y,
                 "distance": round(sum((a - b) ** 2 for a, b in zip(tv, Z[y])) ** 0.5, 3),
                 "class": labels[y]} for y in lab_years),
               key=lambda x: x["distance"])[:kk]
    counts = {lv: sum(1 for x in d if x["class"] == lv) for lv in levels}
    res.update({
        "status": "OK",
        "labelled_analogs": d,
        "n_labelled_analogs": kk,
        "distribution": {lv: f"{counts[lv]}/{kk}" for lv in levels},
        "modal_class": max(levels, key=lambda lv: counts[lv]),
        "features_used": usable,
        "HONESTY": (f"This outlook stands on {kk} named past seasons drawn from a pool of "
                    f"{len(lab_years)}. The finest distinction it can express is 1/{kk}. Render it "
                    f"as the fraction and the named years, never as a smoothed percentage."),
    })
    return res


if __name__ == "__main__":
    F = json.load(open(os.path.join(ROOT, "MODELS", "features_cutoff_respecting.json")))
    lp = os.path.join(ROOT, "OBSERVATIONS", "outcome_labels.json")
    have_labels = os.path.exists(lp)
    L = json.load(open(lp)) if have_labels else None

    out = {}
    for regime, names in (("CUTOFF_A_PRESEASON", SIMILARITY_FEATURES),
                          ("CUTOFF_B_TRUE_12M", SIMILARITY_FEATURES_B)):
        assert F[regime]["TARGET_SEASON_WEATHER_LEAKAGE"] == 0
        feats = {int(y): v for y, v in F[regime]["features"].items()}
        years = sorted(feats)
        if have_labels:
            levels = L["levels"]
            labels = {int(y): (lv if lv in levels else None) for y, lv in L["assignments"].items()}
            out[regime] = {Y: outlook(Y, feats, years, labels, levels, names)
                           for Y in years if Y >= 2006}
        else:
            out[regime] = {Y: analogs_for(Y, feats, years, names)
                           for Y in years if Y >= 2006}
    dest = os.path.join(ROOT, "MODELS", "analog_years.json")
    json.dump(out, open(dest, "w"), indent=1, default=str)

    r = out["CUTOFF_A_PRESEASON"]
    print("ANALOG YEARS (CUTOFF_A_PRESEASON, similarity on 6 a-priori antecedent features)")
    print("target -> nearest prior seasons (distance in standardised space)")
    for Y in sorted(r):
        v = r[Y]
        if not v: 
            print(f"  {Y}: pool too small"); continue
        if "analogs" in v:
            s = "  ".join(f"{a['year']}({a['distance']})" for a in v["analogs"])
        elif v.get("labelled_analogs"):
            s = ("MET " + "  ".join(f"{a['year']}({a['distance']})" for a in v["meteorological_analogs"])
                 + "   | LABELLED " + "  ".join(f"{a['year']}={a['class']}" for a in v["labelled_analogs"]))
        elif v.get("meteorological_analogs"):
            s = ("MET " + "  ".join(f"{a['year']}({a['distance']})" for a in v["meteorological_analogs"])
                 + "   | " + v.get("status", "?"))
        else:
            s = v.get("status", "?")
        print(f"  {Y}: {s}")
    print(f"\nwrote {dest}")
    if not have_labels:
        print("NOTE: no outcome labels yet — analog SETS are final, the outlook DISTRIBUTION is not.")
