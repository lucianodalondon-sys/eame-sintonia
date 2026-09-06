#!/usr/bin/env python3
"""
RED TEAM / GATE G — "the statement discriminates between seasons", dominant class share <= 0.75.

The gate takes the walk-forward hindcast at the same calendar day in every season, counts the
three classes, and passes if no single class takes more than 75% of them. The question this
script answers is: what does that statistic do when there is NO season effect at all?

Null: the same leave-one-out exchangeability null used in rt_stats.py — the season that plays
the role of "current" is swapped with each usable baseline season at the same calendar window.
If gate G passes under that null too, it is a test of non-degeneracy, not of discrimination.

Out: REDTEAM/rt_gateg.json (+ stdout)
"""
import json, os, collections, random

HERE = os.path.dirname(os.path.abspath(__file__))
CELLS = json.load(open(os.path.join(HERE, "rt_cells.json")))["CELLS"]
HIGHER, TYPICAL, LOWER = "HIGHER_THAN_USUAL", "TYPICAL_FOR_THE_DATE", "LOWER_THAN_USUAL"
CLASSED = (HIGHER, TYPICAL, LOWER)
HIGH_P, LOW_P, FLOOR = 0.80, 0.20, 5


def klass(p):
    return HIGHER if p >= HIGH_P else (LOWER if p <= LOW_P else TYPICAL)


def null_for_cell(c, floor_on):
    pool = list(c["BASELINE_PRIOR_USABLE"]) + [{"INCIDENCE": c["VALUE"], "n_sites": c["n_sites"]}]
    n = len(pool) - 1
    out = []
    for i, s in enumerate(pool):
        rest = pool[:i] + pool[i + 1:]
        v = s["INCIDENCE"]
        below = sum(1 for r in rest if r["INCIDENCE"] < v)
        equal = sum(1 for r in rest if r["INCIDENCE"] == v)
        st = klass((below + 0.5 * equal) / n)
        if floor_on and st == HIGHER and s["n_sites"] * v < FLOOR:
            st = TYPICAL
        out.append(st)
    return out


# gate G's grid: the 6-September hindcast, every season, every province, per crop
grid = [c for c in CELLS if c["DATE"].endswith("-09-06") and c["STATE"] in CLASSED]
OUT = {"GRID": f"{len(grid)} classified province-season cells at 6 September, "
               f"{len({c['DATE'] for c in grid})} seasons"}
random.seed(20260906)
REP = 20000
res = {}
for crop in sorted({c["CROP"] for c in grid}) + ["ALL_CROPS"]:
    rows = grid if crop == "ALL_CROPS" else [c for c in grid if c["CROP"] == crop]
    if not rows:
        continue
    obs = collections.Counter(c["STATE"] for c in rows)
    obs_dom = max(obs[x] for x in CLASSED) / len(rows)
    nulls = [null_for_cell(c, True) for c in rows]
    doms, passes = [], 0
    classsum = collections.Counter()
    for _ in range(REP):
        cc = collections.Counter(random.choice(o) for o in nulls)
        d = max(cc[x] for x in CLASSED) / len(rows)
        doms.append(d)
        passes += d <= 0.75
        classsum.update(cc)
    doms.sort()
    res[crop] = {
        "N_CELLS": len(rows),
        "OBSERVED_COUNTS": {k: obs[k] for k in CLASSED},
        "OBSERVED_DOMINANT_SHARE": round(obs_dom, 3),
        "OBSERVED_VERDICT": "PASS" if obs_dom <= 0.75 else "FAIL",
        "NULL_DOMINANT_SHARE_2.5_50_97.5": [round(doms[int(.025 * REP)], 3),
                                            round(doms[REP // 2], 3),
                                            round(doms[int(.975 * REP)], 3)],
        "NULL_MAX_SEEN": round(doms[-1], 3),
        "PROBABILITY_A_NO_SEASON_EFFECT_NULL_PASSES_GATE_G": round(passes / REP, 4),
        "NULL_MEAN_CLASS_MIX": {k: round(classsum[k] / REP, 1) for k in CLASSED}}
    print(crop, json.dumps(res[crop]))
OUT["PER_CROP"] = res

# what would it take to FAIL gate G? the share of a class must exceed 3/4.
OUT["WHAT_THE_BAR_MEANS"] = {
    "MINIMUM_POSSIBLE_DOMINANT_SHARE_WITH_3_CLASSES": 0.333,
    "BAR": 0.75,
    "NOTE": "a labeller that assigned the three classes uniformly at random, ignoring the data "
            "entirely, has an expected dominant share of about 0.36 and passes; the gate can "
            "only fail a labeller that is nearly constant"}
# a coin-flip labeller, for scale
for name, probs in (("UNIFORM_RANDOM_LABELLER", (1 / 3, 1 / 3, 1 / 3)),
                    ("ALWAYS_TYPICAL_LABELLER", (0.0, 1.0, 0.0)),
                    ("NOMINAL_RANK_LABELLER_20_60_20", (0.2, 0.6, 0.2))):
    n = len(grid)
    d = []
    for _ in range(2000):
        cc = collections.Counter(random.choices(CLASSED, weights=probs, k=n))
        d.append(max(cc[x] for x in CLASSED) / n)
    OUT["WHAT_THE_BAR_MEANS"][name] = {
        "MEDIAN_DOMINANT_SHARE": round(sorted(d)[1000], 3),
        "PASSES_GATE_G": f"{sum(1 for x in d if x <= 0.75)}/2000"}
print("BAR:", json.dumps(OUT["WHAT_THE_BAR_MEANS"]))

json.dump(OUT, open(os.path.join(HERE, "rt_gateg.json"), "w"), indent=1, default=str)
print("\nwrote rt_gateg.json")
