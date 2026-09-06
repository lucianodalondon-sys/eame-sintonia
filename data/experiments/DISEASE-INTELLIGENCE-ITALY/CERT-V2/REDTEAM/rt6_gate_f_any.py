#!/usr/bin/env python3
"""
RT6 / F — gate F says `any`, its evidence sentence says `all`.

ENGINE/gates.py 127-133:
    ok = {n: s["MEAN_AGREEMENT"] for n, s in sens.items()}
    VERDICT = PASS if any(v >= STAB_MIN for v in ok.values())
STAB_MIN is 0.80. One case above the line carries the whole suite. Gate H's own docstring
records that exactly this confusion (a list read for truthiness where an all() was meant) was
found and fixed there; it is still in F.

The evidence sentence also says "cells below 0.8 are withheld rather than published". The
withholding lives in answer_sheet.publishable, and gates.evaluate() computes `sheets` and never
reads it; current_pressure publishes every province's STATE whatever its stability.

Out: rt6_gate_f_any.json
"""
import os, sys, json, datetime as dt

HERE = os.path.dirname(os.path.abspath(__file__))
CERT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(CERT, "..", "ENGINE"))
sys.path.insert(0, os.path.join(CERT, "..", "CASES"))
import current_pressure as cp
from answer_sheet import STAB_MIN

AS_OF = dt.date(2026, 9, 6)
CASES = [("OLIVO x BACTROCERA x TOSCANA",
          os.path.join(CERT, "..", "CASES", "OLIVO-BACTROCERA-TOSCANA"), -1002),
         ("VITE x OIDIO x TOSCANA",
          os.path.join(CERT, "..", "CASES", "VITE-OIDIO-TOSCANA"), 39)]

out = {"STAB_MIN": STAB_MIN, "GRID": None, "CASES": {}}
means = {}
for name, d, v in CASES:
    s = cp.sensitivity(d, v, AS_OF)
    out["GRID"] = s["GRID_SIZE"]
    means[name] = s["MEAN_AGREEMENT"]
    per = s["PER_PROVINCE"]
    classed = {p: x for p, x in per.items()
               if x["REFERENCE_STATE"] in (cp.HIGHER, cp.TYPICAL, cp.LOWER)}
    below = {p: x["AGREEMENT"] for p, x in classed.items() if x["AGREEMENT"] < STAB_MIN}
    out["CASES"][name] = {
        "MEAN_AGREEMENT": s["MEAN_AGREEMENT"],
        "n_province_cells": len(per),
        "n_cells_carrying_a_CLASS": len(classed),
        "n_classed_cells_BELOW_STAB_MIN": len(below),
        "AGREEMENT_per_classed_cell": {p: x["AGREEMENT"] for p, x in sorted(classed.items())},
        "cells_below_the_line": below,
        "STATES_SEEN_on_the_worst_cell":
            (min(classed.items(), key=lambda kv: kv[1]["AGREEMENT"])[1]["STATES_SEEN"]
             if classed else [])}

out["GATE_F_PREDICATE"] = {
    "AS_WRITTEN": "any(v >= 0.8 for v in MEAN_AGREEMENT.values())",
    "VALUES": means,
    "VERDICT_any": "PASS" if any(v is not None and v >= STAB_MIN for v in means.values()) else "FAIL",
    "VERDICT_if_it_said_all": "PASS" if all(v is not None and v >= STAB_MIN
                                            for v in means.values()) else "FAIL",
    "WHAT_THAT_MEANS": "one case above the line carries the other; the vine case's published "
                       "labels are certified NOT_PARAMETER_ARTEFACT by the olive case's "
                       "stability."}

src = open(os.path.join(CERT, "..", "ENGINE", "gates.py"), encoding="utf-8").read()
out["WITHHOLDING_CLAIM"] = {
    "EVIDENCE_SENTENCE": "cells below 0.8 are withheld rather than published",
    "gates_evaluate_computes_sheets": "sheets[name] = answer_sheet(" in src,
    "gates_evaluate_reads_sheets_anywhere_after":
        src.count("sheets") > 1 and any("sheets[" in l and "answer_sheet" not in l
                                        for l in src.splitlines()),
    "n_times_the_token_sheets_appears_in_gates.py": src.count("sheets"),
    "current_pressure_applies_STAB_MIN":
        "STAB_MIN" in open(os.path.join(CERT, "..", "ENGINE", "current_pressure.py"),
                           encoding="utf-8").read(),
    "CONCLUSION": "answer_sheet computes a `publishable` set and gates.evaluate() throws it "
                  "away; current_pressure, the thing gates A-G actually read, publishes every "
                  "province's STATE regardless of its stability."}

json.dump(out, open(os.path.join(HERE, "rt6_gate_f_any.json"), "w"), indent=1, default=str)
print(json.dumps(out, indent=1, default=str))
