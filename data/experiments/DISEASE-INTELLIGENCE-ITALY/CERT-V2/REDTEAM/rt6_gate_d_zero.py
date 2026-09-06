#!/usr/bin/env python3
"""
RT6 / D — what gate D actually counts, and what the FAILURE!=ZERO assertion actually asserts.

Gate D (ENGINE/gates.py 112-118):
    unk = {case: how many published provinces are UNKNOWN_*}
    VERDICT = PASS if all(u > 0)
It is an EXISTENCE counter. It never asks whether the cells that SHOULD be UNKNOWN ARE.

Gate D's EVIDENCE also claims "Missing.NEVER_ZERO is asserted on every empty cell". The only
live call site is ENGINE/current_pressure.py:274:
    Missing.assert_not_coerced_to_zero(Missing.NOT_KNOWN, None)
Two CONSTANTS. contracts.Missing.assert_not_coerced_to_zero raises only when value is in
(0, 0.0, "0"); None never is. This script proves the call cannot raise.

Out: rt6_gate_d_zero.json
"""
import os, sys, json, datetime as dt, collections

HERE = os.path.dirname(os.path.abspath(__file__))
CERT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(CERT, "..", "ENGINE"))
sys.path.insert(0, os.path.join(CERT, "..", "CASES"))
import current_pressure as cp
from contracts import Missing

AS_OF = dt.date(2026, 9, 6)
CASES = [("OLIVO x BACTROCERA x TOSCANA",
          os.path.join(CERT, "..", "CASES", "OLIVO-BACTROCERA-TOSCANA"), -1002),
         ("VITE x OIDIO x TOSCANA",
          os.path.join(CERT, "..", "CASES", "VITE-OIDIO-TOSCANA"), 39)]

out = {"AS_OF": AS_OF.isoformat()}

# 1 ── the shipped picture
base = {}
for name, d, v in CASES:
    r = cp.current_pressure(d, v, AS_OF)
    base[name] = r
    st = collections.Counter(x["STATE"] for x in r["PROVINCES"].values())
    out.setdefault("SHIPPED", {})[name] = {
        "n_published_province_cells": len(r["PROVINCES"]),
        "STATES": dict(st),
        "n_UNKNOWN": sum(st[k] for k in (cp.UNKNOWN_NO_DATA, cp.UNKNOWN_NO_BASELINE)),
        "UNKNOWN_PROVINCES": sorted(p for p, x in r["PROVINCES"].items()
                                    if x["STATE"] in (cp.UNKNOWN_NO_DATA, cp.UNKNOWN_NO_BASELINE))}

# 2 ── M07 v3, replayed exactly, and gate D's predicate recomputed on the result
real = cp.current_pressure


def m07(*a, **k):
    r = real(*a, **k)
    rewritten = []
    for p, v in list(r["PROVINCES"].items()):
        if v.get("STATE") in (cp.UNKNOWN_NO_DATA, cp.UNKNOWN_NO_BASELINE):
            rewritten.append(p)
            r["PROVINCES"][p] = {"STATE": cp.LOWER, "VALUE": 0.0, "PERCENTILE": 0.0,
                                 "n_sites": v.get("n_sites", 0), "n_visits": v.get("n_visits", 0),
                                 "BASELINE_N": cp.MIN_BASE, "BASELINE_MEDIAN": 0.0}
    r["PROVINCES"]["_ALIBI"] = {"STATE": cp.UNKNOWN_NO_DATA, "VALUE": None,
                                "n_sites": 0, "n_visits": 0}
    r["_REWRITTEN"] = rewritten
    return r


cp.current_pressure = m07
mut = {}
for name, d, v in CASES:
    mut[name] = cp.current_pressure(d, v, AS_OF)

unk = {n: sum(1 for x in r["PROVINCES"].values()
              if x["STATE"] in (cp.UNKNOWN_NO_DATA, cp.UNKNOWN_NO_BASELINE))
       for n, r in mut.items()}
out["M07_v3_REPLAYED"] = {
    "cells_rewritten_as_VALUE_0.0_LOWER_THAN_USUAL":
        {n: r["_REWRITTEN"] for n, r in mut.items()},
    "n_cells_rewritten": {n: len(r["_REWRITTEN"]) for n, r in mut.items()},
    "n_real_UNKNOWN_cells_left": {n: 0 for n in mut},
    "synthetic_alibi_cells_added": {n: 1 for n in mut},
    "GATE_D_unk_counter_sees": unk,
    "GATE_D_VERDICT": "PASS" if all(u > 0 for u in unk.values()) else "FAIL",
    "READ_PLAINLY": "every province that the engine could not measure is now published as "
                    "'0.0, LOWER_THAN_USUAL' — 'we did not look' rendered as 'there is nothing "
                    "there' — and gate D reports UNKNOWN_IS_VISIBLE = PASS because one fake "
                    "UNKNOWN cell was appended."}

# 3 ── the size of the property being destroyed, stated with its denominator
out["HOW_BIG_IS_THIS_MUTATION"] = {
    "real_UNKNOWN_cells_in_the_shipped_output":
        {n: out["SHIPPED"][n]["n_UNKNOWN"] for n in out["SHIPPED"]},
    "published_cells_per_case": {n: out["SHIPPED"][n]["n_published_province_cells"]
                                 for n in out["SHIPPED"]},
    "NOTE": "the mutation destroys 100% of the cells the property applies to, but that is "
            "2 cells out of 20 published today. M07 v2 was withdrawn for exactly this reason "
            "(unknown[1:] was empty); v3 works only because it appends an alibi."}

# 4 ── can the shipped FAILURE!=ZERO assertion ever raise?
probe = []
for state, value, why in [("NOT_KNOWN", None, "the arguments the shipped runner actually passes"),
                          ("NOT_KNOWN", 0.0, "what the runner would pass if it passed the cell"),
                          ("NOT_KNOWN", 0, "integer zero"),
                          ("INSUFFICIENT_DATA", 0.0, "the other NEVER_ZERO state")]:
    try:
        Missing.assert_not_coerced_to_zero(state, value)
        probe.append({"state": state, "value": value, "RESULT": "no exception", "why": why})
    except ValueError as e:
        probe.append({"state": state, "value": value, "RESULT": f"RAISED: {e}", "why": why})
src = open(os.path.join(CERT, "..", "ENGINE", "current_pressure.py"), encoding="utf-8").read()
out["FAILURE_NOT_ZERO_ASSERTION"] = {
    "ONLY_LIVE_CALL_SITE": "ENGINE/current_pressure.py:274",
    "ARGUMENTS_PASSED": "Missing.NOT_KNOWN, None   (two constants)",
    "call_site_text_found": "Missing.assert_not_coerced_to_zero(Missing.NOT_KNOWN, None)" in src,
    "PROBE": probe,
    "CONCLUSION": "the shipped call passes value=None, which is not in (0, 0.0, '0'), so it "
                  "cannot raise for any input. The assertion gate D cites as evidence is a "
                  "no-op at its only live call site."}

json.dump(out, open(os.path.join(HERE, "rt6_gate_d_zero.json"), "w"), indent=1, default=str)
print(json.dumps(out, indent=1, default=str))
