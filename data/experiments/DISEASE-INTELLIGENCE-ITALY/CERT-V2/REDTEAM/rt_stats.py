#!/usr/bin/env python3
"""
RED TEAM / LENS 1 — is the class a statistical artefact?

A1  RESOLUTION      the percentile lives on a grid of step 0.5/BASELINE_N. How many published
                    labels are one season away from flipping?
A2  ATTAINABILITY    is p>=0.80 reachable? is p<=0.20 reachable, given the tie rule and the
                    fact that the modal season value is exactly 0?
A3  TIES            how many published labels are produced by the 0.5*equal term alone?
A4  ZERO BASELINE   how many HIGHER calls only say "the issue was seen at all this year"?
A5  NULL            exact leave-one-out exchangeability null: how many HIGHER/LOWER calls
                    would this rule emit on data with no season effect at all?
A6  N_SITES         does the class track the number of fields visited rather than disease?

Out: REDTEAM/rt_stats.json  (+ stdout)
"""
import json, os, sys, collections, itertools, random
from statistics import mean, median

HERE = os.path.dirname(os.path.abspath(__file__))
CELLS = json.load(open(os.path.join(HERE, "rt_cells.json")))["CELLS"]
HIGH_P, LOW_P, MIN_BASE, MIN_SITES, FLOOR = 0.80, 0.20, 5, 8, 5
HIGHER, TYPICAL, LOWER = "HIGHER_THAN_USUAL", "TYPICAL_FOR_THE_DATE", "LOWER_THAN_USUAL"
CLASSED = (HIGHER, TYPICAL, LOWER)

cl = [c for c in CELLS if c["STATE_NO_FLOOR"] in CLASSED]
OUT = {}
print(f"classified cells (floor off) = {len(cl)} of {len(CELLS)}")


def klass(p):
    return HIGHER if p >= HIGH_P else (LOWER if p <= LOW_P else TYPICAL)


# ── A1 RESOLUTION ────────────────────────────────────────────────────────────────────
res = collections.Counter()
one_season_flip = 0
flip_by_state = collections.Counter()
for c in cl:
    n = c["BASELINE_N"]
    res[n] += 1
    k = c["N_BELOW"] + 0.5 * c["N_EQUAL"]
    # how far, in whole seasons, is k from the nearest threshold that changes the class?
    if c["STATE_NO_FLOOR"] == HIGHER:
        margin = k - HIGH_P * n              # seasons of slack above the HIGHER line
    elif c["STATE_NO_FLOOR"] == LOWER:
        margin = LOW_P * n - k
    else:
        margin = min(HIGH_P * n - k, k - LOW_P * n)
    c["_margin_seasons"] = margin
    if margin < 1.0:
        one_season_flip += 1
        flip_by_state[c["STATE_NO_FLOOR"]] += 1
OUT["A1_RESOLUTION"] = {
    "BASELINE_N_HISTOGRAM": dict(sorted(res.items())),
    "BASELINE_N_MIN": min(res), "BASELINE_N_MEDIAN": median([c["BASELINE_N"] for c in cl]),
    "BASELINE_N_MAX": max(res),
    "PERCENTILE_GRID_STEP_MIN": round(0.5 / max(res), 4),
    "PERCENTILE_GRID_STEP_MAX": round(0.5 / min(res), 4),
    "LABELS_ONE_SEASON_FROM_FLIPPING": f"{one_season_flip}/{len(cl)}",
    "BY_STATE": dict(flip_by_state),
    "HIGHER_ONE_SEASON_FROM_FLIPPING":
        f"{flip_by_state[HIGHER]}/{sum(1 for c in cl if c['STATE_NO_FLOOR'] == HIGHER)}"}
print("A1", json.dumps(OUT["A1_RESOLUTION"]))

# ── A2 ATTAINABILITY ─────────────────────────────────────────────────────────────────
# For the OBSERVED baseline vector of each cell, which classes could an ACHIEVABLE current
# value produce? An incidence is k/n_sites for an integer k in 0..n_sites: it cannot be
# negative, so a cell whose baseline is mostly zeros has NO achievable value that reaches
# the LOWER threshold.
def reachable(prior, n_sites):
    n = len(prior)
    seen = set()
    for k in range(n_sites + 1):
        v = round(k / n_sites, 4)
        below = sum(1 for s in prior if s["INCIDENCE"] < v)
        equal = sum(1 for s in prior if s["INCIDENCE"] == v)
        seen.add(klass((below + 0.5 * equal) / n))
    return seen


no_lower, no_higher = 0, 0
zero_cannot_be_lower = 0
n_zero_current = 0
zero_state = collections.Counter()
for c in cl:
    r = reachable(c["BASELINE_PRIOR_USABLE"], c["n_sites"])
    c["_reachable"] = sorted(r)
    if LOWER not in r:
        no_lower += 1
    if HIGHER not in r:
        no_higher += 1
    if c["VALUE"] == 0:
        n_zero_current += 1
        zero_state[c["STATE_NO_FLOOR"]] += 1
        if c["STATE_NO_FLOOR"] != LOWER:
            zero_cannot_be_lower += 1
# the pure arithmetic: with a current value of 0 and z zeros among n baselines, p = 0.5z/n
zero_rule = {}
for n in range(5, 22):
    zmax = max((z for z in range(n + 1) if 0.5 * z / n <= LOW_P), default=None)
    zero_rule[n] = f"a current value of 0 is LOWER only if at most {zmax} of {n} baseline seasons are 0"
OUT["A2_ATTAINABILITY"] = {
    "CELLS_WHERE_NO_ACHIEVABLE_VALUE_COULD_PRODUCE_LOWER": f"{no_lower}/{len(cl)}",
    "CELLS_WHERE_NO_ACHIEVABLE_VALUE_COULD_PRODUCE_HIGHER": f"{no_higher}/{len(cl)}",
    "CURRENT_VALUE_IS_EXACTLY_ZERO": f"{n_zero_current}/{len(cl)}",
    "STATE_OF_THE_ZERO_VALUED_CELLS": dict(zero_state),
    "OF_THOSE_NOT_CALLED_LOWER": zero_cannot_be_lower,
    "ZERO_RULE_BY_BASELINE_N": zero_rule}
print("A2", json.dumps({k: v for k, v in OUT["A2_ATTAINABILITY"].items() if k != "ZERO_RULE_BY_BASELINE_N"}))

# ── A3 TIES ──────────────────────────────────────────────────────────────────────────
# three tie conventions: shipped (below + .5 eq), MIN (below), MAX (below + eq)
change_min, change_max, either = 0, 0, 0
tie_driven_higher, tie_driven_lower = [], []
n_with_ties = 0
for c in cl:
    n, b, e = c["BASELINE_N"], c["N_BELOW"], c["N_EQUAL"]
    if e:
        n_with_ties += 1
    s_ship = klass((b + 0.5 * e) / n)
    s_min, s_max = klass(b / n), klass((b + e) / n)
    if s_min != s_ship:
        change_min += 1
    if s_max != s_ship:
        change_max += 1
    if s_min != s_ship or s_max != s_ship:
        either += 1
    if s_ship == HIGHER and s_min != HIGHER:
        tie_driven_higher.append(c)
    if s_ship == LOWER and s_max != LOWER:
        tie_driven_lower.append(c)
OUT["A3_TIES"] = {
    "CELLS_WITH_AT_LEAST_ONE_TIED_BASELINE_SEASON": f"{n_with_ties}/{len(cl)}",
    "LABEL_CHANGES_IF_TIES_COUNT_AS_BELOW(0)": f"{change_min}/{len(cl)}",
    "LABEL_CHANGES_IF_TIES_COUNT_AS_BELOW(1)": f"{change_max}/{len(cl)}",
    "LABEL_DEPENDS_ON_THE_TIE_CONVENTION": f"{either}/{len(cl)}",
    "HIGHER_THAT_EXISTS_ONLY_BECAUSE_OF_THE_HALF_TIE":
        f"{len(tie_driven_higher)}/{sum(1 for c in cl if c['STATE_NO_FLOOR'] == HIGHER)}",
    "LOWER_THAT_EXISTS_ONLY_BECAUSE_OF_THE_HALF_TIE":
        f"{len(tie_driven_lower)}/{sum(1 for c in cl if c['STATE_NO_FLOOR'] == LOWER)}",
    "TIE_DRIVEN_HIGHER_ROWS": [{k: c[k] for k in
                                ("CROP", "DATE", "PROVINCE", "VALUE", "PERCENTILE",
                                 "PERCENTILE_STRICT_ONLY", "N_BELOW", "N_EQUAL", "BASELINE_N",
                                 "n_sites", "n_pos")} for c in tie_driven_higher],
    "TIE_DRIVEN_LOWER_ROWS": [{k: c[k] for k in
                               ("CROP", "DATE", "PROVINCE", "VALUE", "PERCENTILE",
                                "N_BELOW", "N_EQUAL", "BASELINE_N", "n_sites", "n_pos")}
                              for c in tie_driven_lower][:25]}
dist_conv = {"SHIPPED_below+0.5eq": collections.Counter(),
             "MIN_below_only": collections.Counter(),
             "MAX_below+eq": collections.Counter()}
for c in cl:
    n, b, e = c["BASELINE_N"], c["N_BELOW"], c["N_EQUAL"]
    dist_conv["SHIPPED_below+0.5eq"][klass((b + 0.5 * e) / n)] += 1
    dist_conv["MIN_below_only"][klass(b / n)] += 1
    dist_conv["MAX_below+eq"][klass((b + e) / n)] += 1
OUT["A3_TIES"]["CLASS_DISTRIBUTION_UNDER_EACH_TIE_CONVENTION"] = \
    {k: dict(v) for k, v in dist_conv.items()}
print("A3", json.dumps({k: v for k, v in OUT["A3_TIES"].items() if not k.endswith("ROWS")}))

# ── A4 ZERO BASELINE ─────────────────────────────────────────────────────────────────
hi = [c for c in cl if c["STATE_NO_FLOOR"] == HIGHER]
hi_kept = [c for c in cl if c["STATE"] == HIGHER]
allzero = [c for c in hi if c["BASELINE_ALL_ZERO"]]
medzero = [c for c in hi if c["BASELINE_MEDIAN"] == 0]
allzero_kept = [c for c in hi_kept if c["BASELINE_ALL_ZERO"]]
medzero_kept = [c for c in hi_kept if c["BASELINE_MEDIAN"] == 0]
OUT["A4_ZERO_BASELINE"] = {
    "HIGHER_NO_FLOOR": len(hi), "HIGHER_SHIPPED": len(hi_kept),
    "HIGHER_WHERE_EVERY_BASELINE_SEASON_IS_ZERO": f"{len(allzero)}/{len(hi)}",
    "HIGHER_WHERE_THE_BASELINE_MEDIAN_IS_ZERO": f"{len(medzero)}/{len(hi)}",
    "SHIPPED_HIGHER_WHERE_EVERY_BASELINE_SEASON_IS_ZERO": f"{len(allzero_kept)}/{len(hi_kept)}",
    "SHIPPED_HIGHER_WHERE_THE_BASELINE_MEDIAN_IS_ZERO": f"{len(medzero_kept)}/{len(hi_kept)}",
    "SMALLEST_INCIDENCE_EVER_PUBLISHED_AS_HIGHER": min(c["VALUE"] for c in hi_kept),
    "SMALLEST_POSITIVE_SITES_EVER_PUBLISHED_AS_HIGHER": min(c["n_pos"] for c in hi_kept)}
print("A4", json.dumps(OUT["A4_ZERO_BASELINE"]))

# ── A5 EXACT EXCHANGEABILITY NULL ────────────────────────────────────────────────────
# For every classified cell, take the set of usable seasons at that same calendar window
# (prior baselines + the current one). Under the null there is no season effect, so which
# season plays the role of "current" is arbitrary. Enumerate all n+1 assignments exactly.
def null_for_cell(c):
    pool = list(c["BASELINE_PRIOR_USABLE"]) + [{"year": "CURRENT", "INCIDENCE": c["VALUE"],
                                                "n_sites": c["n_sites"], "n_pos": c["n_pos"]}]
    n = len(pool) - 1
    outc = []
    for i, s in enumerate(pool):
        rest = pool[:i] + pool[i + 1:]
        v = s["INCIDENCE"]
        below = sum(1 for r in rest if r["INCIDENCE"] < v)
        equal = sum(1 for r in rest if r["INCIDENCE"] == v)
        p = (below + 0.5 * equal) / n
        st = klass(p)
        st_floor = TYPICAL if (st == HIGHER and s["n_sites"] * v < FLOOR) else st
        outc.append((st, st_floor))
    return outc


exp_hi = exp_lo = exp_hi_floor = 0.0
for c in cl:
    o = null_for_cell(c)
    m = len(o)
    exp_hi += sum(1 for a, b in o if a == HIGHER) / m
    exp_lo += sum(1 for a, b in o if a == LOWER) / m
    exp_hi_floor += sum(1 for a, b in o if b == HIGHER) / m
obs_hi = len(hi)
obs_lo = sum(1 for c in cl if c["STATE_NO_FLOOR"] == LOWER)
obs_hi_floor = len(hi_kept)

# Monte-Carlo p-value for "more HIGHER than the null expects", drawing one assignment per cell
random.seed(20260906)
REP = 20000
cellnull = [null_for_cell(c) for c in cl]
cnt_hi = cnt_lo = cnt_hi_floor = 0
dist_hi = []
for _ in range(REP):
    h = l = hf = 0
    for o in cellnull:
        a, b = random.choice(o)
        h += a == HIGHER
        l += a == LOWER
        hf += b == HIGHER
    dist_hi.append(h)
    cnt_hi += h >= obs_hi
    cnt_lo += l >= obs_lo
    cnt_hi_floor += hf >= obs_hi_floor
dist_hi.sort()
OUT["A5_NULL"] = {
    "NULL": "leave-one-out exchangeability: the current season is swapped with each usable "
            "baseline season at the same calendar window; all n+1 assignments enumerated exactly",
    "CLASSIFIED_CELLS": len(cl),
    "EXPECTED_HIGHER_NO_FLOOR": round(exp_hi, 1), "OBSERVED_HIGHER_NO_FLOOR": obs_hi,
    "EXPECTED_LOWER": round(exp_lo, 1), "OBSERVED_LOWER": obs_lo,
    "EXPECTED_HIGHER_WITH_FLOOR": round(exp_hi_floor, 1), "OBSERVED_HIGHER_WITH_FLOOR": obs_hi_floor,
    "MC_REPLICATES": REP,
    "P_OBSERVED_HIGHER_>=_NULL": round(cnt_hi / REP, 4),
    "P_OBSERVED_LOWER_>=_NULL": round(cnt_lo / REP, 4),
    "P_OBSERVED_HIGHER_WITH_FLOOR_>=_NULL": round(cnt_hi_floor / REP, 4),
    "NULL_HIGHER_2.5_50_97.5_PCT": [dist_hi[int(.025 * REP)], dist_hi[REP // 2],
                                    dist_hi[int(.975 * REP)]],
    "CAVEAT": "the Monte-Carlo p-values treat the 282 cells as independent; they are not "
              "(25 province-cells x 30 dates, and the eleven 2026 windows overlap). The "
              "EXPECTED counts are unbiased under any dependence (linearity); only the "
              "p-values are optimistic. Sub-samples with one window per season are below."}
# sub-samples: (a) only the 2026 dates, (b) only the 19 prior 6-September dates (one
# non-overlapping window per season), (c) split by crop
subs = {"2026_DATES_ONLY": [c for c in cl if c["DATE"].startswith("2026")],
        "PRIOR_SEP6_ONLY": [c for c in cl if not c["DATE"].startswith("2026")]}
for crop in sorted({c["CROP"] for c in cl}):
    subs["CROP_" + crop] = [c for c in cl if c["CROP"] == crop]
sub_out = {}
for name, rows in subs.items():
    eh = el = ehf = 0.0
    for c in rows:
        o = null_for_cell(c)
        m = len(o)
        eh += sum(1 for a, b in o if a == HIGHER) / m
        el += sum(1 for a, b in o if a == LOWER) / m
        ehf += sum(1 for a, b in o if b == HIGHER) / m
    sub_out[name] = {
        "N": len(rows),
        "HIGHER_obs/exp_no_floor": f"{sum(1 for c in rows if c['STATE_NO_FLOOR'] == HIGHER)}/{round(eh, 1)}",
        "HIGHER_obs/exp_shipped": f"{sum(1 for c in rows if c['STATE'] == HIGHER)}/{round(ehf, 1)}",
        "LOWER_obs/exp": f"{sum(1 for c in rows if c['STATE_NO_FLOOR'] == LOWER)}/{round(el, 1)}"}
OUT["A5_NULL"]["SUBSAMPLES"] = sub_out
print("A5", json.dumps(OUT["A5_NULL"]))

# ── A6 N_SITES ───────────────────────────────────────────────────────────────────────
def bucket(n):
    return "8-14" if n < 15 else ("15-39" if n < 40 else "40+")


tab = collections.defaultdict(collections.Counter)
for c in cl:
    tab[bucket(c["n_sites"])][c["STATE_NO_FLOOR"]] += 1
    tab[bucket(c["n_sites"])]["_ALL"] += 1
tab_shipped = collections.defaultdict(collections.Counter)
for c in cl:
    tab_shipped[bucket(c["n_sites"])][c["STATE"]] += 1
    tab_shipped[bucket(c["n_sites"])]["_ALL"] += 1
# point-biserial-ish: mean n_sites by class
by_state = collections.defaultdict(list)
for c in cl:
    by_state[c["STATE_NO_FLOOR"]].append(c["n_sites"])
OUT["A6_N_SITES"] = {
    "CLASS_BY_N_SITES_BUCKET_FLOOR_OFF":
        {k: {s: f"{v[s]}/{v['_ALL']}" for s in CLASSED} for k, v in sorted(tab.items())},
    "CLASS_BY_N_SITES_BUCKET_SHIPPED":
        {k: {s: f"{v[s]}/{v['_ALL']}" for s in CLASSED} for k, v in sorted(tab_shipped.items())},
    "MEDIAN_N_SITES_BY_CLASS": {k: median(v) for k, v in sorted(by_state.items())},
    "INCIDENCE_GRID_STEP": "1/n_sites; smallest non-zero incidence expressible per bucket: "
                           f"8 sites -> 0.125, 14 -> 0.0714, 40 -> 0.025, 119 -> 0.0084"}
print("A6", json.dumps(OUT["A6_N_SITES"]))

json.dump(OUT, open(os.path.join(HERE, "rt_stats.json"), "w"), indent=1, default=str)
print("\nwrote rt_stats.json")
