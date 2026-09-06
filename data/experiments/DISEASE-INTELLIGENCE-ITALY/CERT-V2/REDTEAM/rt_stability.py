#!/usr/bin/env python3
"""
RED TEAM / two more measurements.

S1  IS INCIDENCE STABLE GIVEN THE NUMBER OF SITES VISITED?
    Non-parametric bootstrap of the site sample. A province's INCIDENCE is k positives out of
    n_sites monitored fields; the fields visited are a sample. Resample n_sites fields with
    replacement (a) in the current window only, (b) in the current window and in every baseline
    season, recompute the published class, and count how often it changes.

S2  DOES THE FLOOR IMPROVE THE CALLS' EXCESS OVER CHANCE, OR JUST SHRINK BOTH?
    For every floor value, the observed number of HIGHER calls and the number the
    leave-one-out exchangeability null produces. A floor that DISCRIMINATES should raise
    observed/expected. A floor that is a blunt patch leaves the ratio flat.

Out: REDTEAM/rt_stability.json (+ stdout)
"""
import json, os, random, collections

HERE = os.path.dirname(os.path.abspath(__file__))
CELLS = json.load(open(os.path.join(HERE, "rt_cells.json")))["CELLS"]
HIGHER, TYPICAL, LOWER = "HIGHER_THAN_USUAL", "TYPICAL_FOR_THE_DATE", "LOWER_THAN_USUAL"
CLASSED = (HIGHER, TYPICAL, LOWER)
HIGH_P, LOW_P, FLOOR = 0.80, 0.20, 5
cl = [c for c in CELLS if c["STATE_NO_FLOOR"] in CLASSED]
random.seed(20260906)
OUT = {}


def klass(p):
    return HIGHER if p >= HIGH_P else (LOWER if p <= LOW_P else TYPICAL)


def classify(v, baseline_vals, n_sites, floor=FLOOR):
    n = len(baseline_vals)
    below = sum(1 for b in baseline_vals if b < v)
    equal = sum(1 for b in baseline_vals if b == v)
    st = klass((below + 0.5 * equal) / n)
    if floor and st == HIGHER and n_sites * v < floor:
        st = TYPICAL
    return st


def resample(k, n):
    """bootstrap incidence: n draws with replacement from n sites of which k are positive"""
    hit = sum(1 for _ in range(n) if random.random() < k / n)
    return round(hit / n, 4)


B = 1000
flip_cur = collections.Counter()
flip_all = collections.Counter()
tot = collections.Counter()
per_state_cur = collections.defaultdict(list)
for c in cl:
    base = [s["INCIDENCE"] for s in c["BASELINE_PRIOR_USABLE"]]
    basen = [s["n_sites"] for s in c["BASELINE_PRIOR_USABLE"]]
    basek = [s["n_pos"] for s in c["BASELINE_PRIOR_USABLE"]]
    st0 = c["STATE"]
    ch_cur = ch_all = 0
    for _ in range(B):
        v = resample(c["n_pos"], c["n_sites"])
        if classify(v, base, c["n_sites"]) != st0:
            ch_cur += 1
        b2 = [resample(k, n) for k, n in zip(basek, basen)]
        if classify(v, b2, c["n_sites"]) != st0:
            ch_all += 1
    tot[st0] += 1
    flip_cur[st0] += ch_cur / B
    flip_all[st0] += ch_all / B
    per_state_cur[st0].append(ch_cur / B)

OUT["S1_BOOTSTRAP"] = {
    "REPLICATES_PER_CELL": B, "CELLS": len(cl),
    "MEAN_PROBABILITY_THE_PUBLISHED_CLASS_CHANGES_IF_THE_SITE_SAMPLE_IS_RESAMPLED": {
        "CURRENT_WINDOW_ONLY": {k: f"{round(flip_cur[k] / tot[k], 3)} (n={tot[k]})"
                                for k in CLASSED if tot[k]},
        "CURRENT_AND_BASELINE_SEASONS": {k: f"{round(flip_all[k] / tot[k], 3)} (n={tot[k]})"
                                         for k in CLASSED if tot[k]}},
    "HIGHER_CELLS_WITH_>25pct_CHANCE_OF_FLIPPING":
        f"{sum(1 for x in per_state_cur[HIGHER] if x > .25)}/{tot[HIGHER]}",
    "LOWER_CELLS_WITH_>25pct_CHANCE_OF_FLIPPING":
        f"{sum(1 for x in per_state_cur[LOWER] if x > .25)}/{tot[LOWER]}"}
print("S1", json.dumps(OUT["S1_BOOTSTRAP"]))

# ── S2 ───────────────────────────────────────────────────────────────────────────────
def null_states(c, floor):
    pool = list(c["BASELINE_PRIOR_USABLE"]) + [{"INCIDENCE": c["VALUE"], "n_sites": c["n_sites"]}]
    n = len(pool) - 1
    out = []
    for i, s in enumerate(pool):
        rest = [r["INCIDENCE"] for r in pool[:i] + pool[i + 1:]]
        out.append(classify(s["INCIDENCE"], rest, s["n_sites"], floor))
    return out


s2 = {}
for T in (0, 1, 2, 3, 4, 5, 6, 8, 10, 15, 20, 30, 50):
    obs = sum(1 for c in cl
              if (c["STATE_NO_FLOOR"] == HIGHER and c["FLOOR_PRODUCT"] >= T))
    exp = 0.0
    for c in cl:
        o = null_states(c, T)
        exp += sum(1 for x in o if x == HIGHER) / len(o)
    s2[str(T)] = {"OBSERVED_HIGHER": obs, "EXPECTED_UNDER_NULL": round(exp, 1),
                  "OBSERVED/EXPECTED": round(obs / exp, 3) if exp else None}
    print(f"   floor={T:<3} observed={obs:<3} expected_null={exp:6.1f} "
          f"ratio={obs / exp if exp else 0:.3f}")
OUT["S2_FLOOR_VS_NULL"] = s2

json.dump(OUT, open(os.path.join(HERE, "rt_stability.json"), "w"), indent=1, default=str)
print("\nwrote rt_stability.json")
