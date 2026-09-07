#!/usr/bin/env python3
"""RT4-11b  With the loader's sort removed, six file orders gave six hashes. Is that six
different ANSWERS, or one answer with six differently-ordered receipts? Hash the payload
twice: once whole, once with the provenance file lists sorted out of the way."""
import os, sys, json, hashlib, random, builtins, datetime as dt
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "engine"))
import di_core, di_observe
CASE = os.path.abspath(os.path.join(HERE, "..", "..", "DISEASE-INTELLIGENCE-ITALY",
                                    "CASES", "OLIVO-BACTROCERA-TOSCANA"))
AS_OF = dt.date(2026, 9, 6)
RS = builtins.sorted

def run(order_fn):
    def fake(it, **kw):
        s = list(it)
        if s and all(isinstance(x, str) and x.endswith(".json") for x in s):
            return order_fn(s)
        return RS(s, **kw)
    di_core.sorted = fake
    try:
        sheet = di_core.load_sheet()
        L = di_core.load_visits(CASE, sheet, AS_OF)
        provs = RS({v["province"] for v in L["visits"] if v["province"]})
        cells = [di_observe.cell(L["visits"], sheet, p, m, AS_OF)
                 for m in ("ACTIVE_INFESTATION_COUNT", "DAMAGING_INFESTATION_COUNT")
                 for p in provs]
        whole = {"loaded": {k: v for k, v in L.items() if k != "visits"}, "cells": cells}
        # numbers only: drop provenance entirely, and drop per-visit source_file provenance
        numbers = {"loaded": {k: v for k, v in L.items()
                              if k not in ("visits", "provenance")}, "cells": cells}
        # provenance file lists, normalised
        prov_sorted = {c: RS(f["file"] for f in b["files"])
                       for c, b in L["provenance"].items()}
        prov_hashes = {c: RS(f["sha256"] for f in b["files"])
                       for c, b in L["provenance"].items()}
        h = lambda o: hashlib.sha256(json.dumps(o, sort_keys=True,
                                                default=str).encode()).hexdigest()
        return h(whole), h(numbers), h(prov_sorted), h(prov_hashes)
    finally:
        di_core.sorted = RS

conds = {"ascending": lambda s: RS(s), "descending": lambda s: RS(s, reverse=True),
         "by_basename_reversed": lambda s: RS(s, key=lambda x: os.path.basename(x)[::-1]),
         "shuffle_1": lambda s: random.Random(1).sample(s, len(s)),
         "shuffle_2": lambda s: random.Random(2).sample(s, len(s)),
         "shuffle_3": lambda s: random.Random(3).sample(s, len(s))}
rows = {n: run(f) for n, f in conds.items()}
out = {"per_condition": {n: {"whole_payload": r[0], "numbers_only_no_provenance": r[1],
                             "provenance_file_names_sorted": r[2],
                             "provenance_sha256_set_sorted": r[3]} for n, r in rows.items()},
       "distinct_whole_payload": len({r[0] for r in rows.values()}),
       "distinct_NUMBERS_ONLY": len({r[1] for r in rows.values()}),
       "distinct_provenance_file_SET": len({r[2] for r in rows.values()}),
       "distinct_provenance_hash_SET": len({r[3] for r in rows.values()})}
out["VERDICT"] = ("removing the sort changes ONLY the order of the provenance file list; "
                  "every published number is identical"
                  if out["distinct_NUMBERS_ONLY"] == 1 else
                  "removing the sort changes PUBLISHED NUMBERS")
print(json.dumps(out, indent=1, default=str))
json.dump(out, open(os.path.join(HERE, "rt4_11b.json"), "w", encoding="utf-8"),
          indent=1, default=str)
