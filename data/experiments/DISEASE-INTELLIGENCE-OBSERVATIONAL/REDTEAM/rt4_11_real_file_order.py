#!/usr/bin/env python3
"""RT4-11  The file-order test the tool's own test could not perform.

t1_determinism.py varies the return order of glob.glob across 8 conditions. But
di_core._read_variable does

        for fn in sorted(glob.glob(pattern)):

so all 8 permutations are collapsed to the SAME ascending order before a single byte is read.
Condition A therefore cannot fail, whatever the engine does downstream: it is a tautology.

Here I remove the collapse. `sorted` is looked up as a global in di_core, so assigning
di_core.sorted shadows the builtin for that module only. With the sort gone I feed the loader
ascending, descending, and four fixed permutations, and ask whether the answer survives.

Two possible outcomes, both worth knowing:
  the answer changes -> the sort is genuinely load-bearing, and the tool has never tested it
  the answer holds   -> the engine is order-invariant even without the sort, and the sort is
                        belt-and-braces
"""
import os, sys, json, glob as globmod, hashlib, random, builtins, datetime as dt

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "engine"))
import di_core, di_observe

CASE = os.path.abspath(os.path.join(HERE, "..", "..", "DISEASE-INTELLIGENCE-ITALY",
                                    "CASES", "OLIVO-BACTROCERA-TOSCANA"))
AS_OF = dt.date(2026, 9, 6)
REAL_SORTED = builtins.sorted


def run(order_fn):
    """order_fn is applied where di_core would have called sorted() on the glob result."""
    def fake_sorted(it, **kw):
        seq = list(it)
        if seq and all(isinstance(x, str) and x.endswith(".json") for x in seq):
            return order_fn(seq)          # the file list: impose OUR order, no sort
        return REAL_SORTED(seq, **kw)     # every other sorted() in the module is untouched
    di_core.sorted = fake_sorted
    try:
        sheet = di_core.load_sheet()
        loaded = di_core.load_visits(CASE, sheet, AS_OF)
        provs = REAL_SORTED({v["province"] for v in loaded["visits"] if v["province"]})
        cells = [di_observe.cell(loaded["visits"], sheet, p, m, AS_OF)
                 for m in ("ACTIVE_INFESTATION_COUNT", "DAMAGING_INFESTATION_COUNT")
                 for p in provs]
        blob = json.dumps({"loaded": {k: v for k, v in loaded.items() if k != "visits"},
                           "cells": cells}, sort_keys=True, default=str).encode("utf-8")
        return hashlib.sha256(blob).hexdigest(), None
    except Exception as e:
        return None, f"{type(e).__name__}: {str(e)[:200]}"
    finally:
        di_core.sorted = REAL_SORTED


conds = {"ascending": lambda s: REAL_SORTED(s),
         "descending": lambda s: REAL_SORTED(s, reverse=True),
         "by_basename_reversed": lambda s: REAL_SORTED(s, key=lambda x: os.path.basename(x)[::-1]),
         "shuffle_seed_1": lambda s: random.Random(1).sample(s, len(s)),
         "shuffle_seed_2": lambda s: random.Random(2).sample(s, len(s)),
         "shuffle_seed_3": lambda s: random.Random(3).sample(s, len(s))}

res, errs = {}, {}
for name, fn in conds.items():
    h, e = run(fn)
    res[name] = h
    if e:
        errs[name] = e

distinct = REAL_SORTED({v for v in res.values() if v})
out = {"WHAT_THIS_REMOVES": "the sorted() around glob.glob inside di_core._read_variable",
       "per_condition": res, "errors": errs,
       "distinct_results": len(distinct),
       "ORDER_INVARIANT_EVEN_WITHOUT_THE_SORT": len(distinct) == 1 and not errs,
       "matches_the_published_hash": [k for k, v in res.items()
                                      if v == "61ac20d6b5be53707ccc7261e4d0091d4ef72ed9"
                                              "1ac4e6d78cd9b6db043546d8"],
       "WHY_THE_TOOLS_OWN_CONDITION_A_CANNOT_FAIL":
           "it permutes glob.glob's return value, which _read_variable immediately re-sorts, "
           "so all 8 of its conditions read the files in one and the same ascending order"}
print(json.dumps(out, indent=1, default=str))
json.dump(out, open(os.path.join(HERE, "rt4_11_real_file_order.json"), "w",
                    encoding="utf-8"), indent=1, default=str)
