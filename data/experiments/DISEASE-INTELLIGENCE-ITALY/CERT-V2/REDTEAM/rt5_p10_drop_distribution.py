#!/usr/bin/env python3
"""RT5 -- how wide is the reachable set? The denominator guard's drop count, over many orders.

ENGINE/regional_coverage.json, a committed artefact, records
    "DENOMINATOR_GUARD": {"dropped_zero_or_unknown_denominator": 3206, ...}
for the olive case. This script computes the EXACT set of values that number can take as the
21 denominator files are permuted, by sampling orders -- without re-parsing anything.

Algebra (exact, not an approximation). den.get(k) is truthy iff the LAST file in the order
that mentions k stored a non-zero, non-null value. So for a given order the only keys whose
verdict can move are those a file disagrees about. Precompute per key the (file -> truthy)
map once; then each order is 1,759 max-position lookups instead of 1.7M dict writes.
Validated against the shipped denominator_guard on asc and desc.
"""
import json, os, sys, glob, random, collections, itertools

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "ENGINE")); sys.path.insert(0, os.path.join(ROOT, "CASES"))
import current_pressure as cp

OL = os.path.join(ROOT, "CASES", "OLIVO-BACTROCERA-TOSCANA")
FILES = sorted(glob.glob(os.path.join(OL, "RAW", "*_v1_*.json")))
N = len(FILES)

def truthy(v):
    try:
        return bool(float(v)) if v not in (None, "") else False
    except (ValueError, TypeError):
        return False

# key -> {file_index: truthy}
per = collections.defaultdict(dict)
for i, f in enumerate(FILES):
    for r in json.load(open(f)):
        per[r["id_survey"]][i] = truthy(r.get("val"))

rows, _s, _m = cp.load_rows(OL, -1002)
cnt = collections.Counter(r.get("id_survey") for r in rows)
TOTAL = len(rows)

fixed_keep, variable = 0, []
for k, fm in per.items():
    c = cnt.get(k, 0)
    if c == 0:
        continue
    vals = set(fm.values())
    if len(vals) == 1:
        fixed_keep += c if vals.pop() else 0
    else:
        variable.append((c, sorted(fm.items())))
orphan = sum(c for k, c in cnt.items() if k not in per)     # rows with no denominator at all

def dropped_for(order):
    pos = {f: i for i, f in enumerate(order)}
    keep = fixed_keep
    for c, fm in variable:
        win = max(fm, key=lambda t: pos[t[0]])[1] if False else None
        best, bt = -1, False
        for fi, t in fm:
            if pos[fi] > best: best, bt = pos[fi], t
        if bt: keep += c
    return TOTAL - keep

# --- validate against the shipped function -------------------------------------------
real = glob.glob
val = {}
for label, order in (("asc", list(range(N))), ("desc", list(reversed(range(N))))):
    cp.glob.glob = (lambda o: (lambda p, **k: [FILES[i] for i in o] if "_v1_" in p else real(p, **k)))(order)
    _, info = cp.denominator_guard(rows, OL, 1)
    cp.glob.glob = real
    val[label] = {"shipped": info["dropped_zero_or_unknown_denominator"], "harness": dropped_for(order)}
assert all(v["shipped"] == v["harness"] for v in val.values()), val

# --- sample the reachable set ---------------------------------------------------------
rng = random.Random(20260906)
seen = collections.Counter()
base = list(range(N))
for _ in range(20000):
    o = base[:]; rng.shuffle(o); seen[dropped_for(o)] += 1
seen[dropped_for(list(range(N)))] += 1
seen[dropped_for(list(reversed(range(N))))] += 1

vals = sorted(seen)
COMMITTED = 3206
THIS_MACHINE = dropped_for(sorted(range(N), key=lambda i: FILES[i]))   # native == ascending here
out = {"n_denominator_files": N, "outcome_rows": TOTAL,
       "keys_with_a_row_in_the_outcome": len([1 for k in cnt if k in per]),
       "keys_whose_KEEP_verdict_depends_on_the_order": len(variable),
       "outcome_rows_hanging_on_those_keys": sum(c for c, _ in variable),
       "rows_with_no_denominator_entry_at_all": orphan,
       "VALIDATION_vs_shipped_denominator_guard": val,
       "ORDERS_SAMPLED": 20002,
       "DISTINCT_DROP_COUNTS": len(vals), "MIN": vals[0], "MAX": vals[-1],
       "SPREAD_rows": vals[-1] - vals[0],
       "SPREAD_pct_of_visits": round(100 * (vals[-1] - vals[0]) / TOTAL, 2),
       "COMMITTED_in_regional_coverage_json": COMMITTED,
       "COMMITTED_VALUE_REACHED": COMMITTED in seen,
       "times_reached": seen.get(COMMITTED, 0),
       "value_on_this_checkout_ascending": THIS_MACHINE}
json.dump(out, open(os.path.join(HERE, "rt5_p10_drop_distribution.json"), "w"), indent=1)
for k, v in out.items():
    if k != "VALIDATION_vs_shipped_denominator_guard":
        print(f"  {k:52s} {v}")
print("  validation:", val)
