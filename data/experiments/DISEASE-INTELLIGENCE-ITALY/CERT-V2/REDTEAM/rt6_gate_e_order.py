#!/usr/bin/env python3
"""
RT6 / E — what "byte-identical re-run" actually certifies.

Gate E (ENGINE/gates.py 120-125):
    a = json.dumps(live)                                  # computed earlier in evaluate()
    b = json.dumps({n: cp.current_pressure(d, v, as_of)}) # recomputed a few lines later
    VERDICT = PASS if a == b
Both sides run in the SAME process, under whatever patches are in force. So the predicate is
f(x) == f(x): every DETERMINISTIC change to f survives it by construction, and only an
intra-process non-determinism (M08's nonce, M09's advancing shuffle) can make it FAIL.

This script measures three things:
  1. gate E's predicate under M27 (glob order fixed but reversed)          -> expected PASS
  2. whether M27 changes the published bytes AT ALL relative to no patch   -> the real question
  3. the same output under a THIRD order, to stand in for "the machine next door"
  4. how much of the archive the "every raw file sha256-checked" claim covers

Out: rt6_gate_e_order.json
"""
import os, sys, json, glob as globmod, hashlib, datetime as dt

HERE = os.path.dirname(os.path.abspath(__file__))
CERT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(CERT, "..", "ENGINE"))
sys.path.insert(0, os.path.join(CERT, "..", "CASES"))
import current_pressure as cp

AS_OF = dt.date(2026, 9, 6)
CASES = [("OLIVO x BACTROCERA x TOSCANA",
          os.path.join(CERT, "..", "CASES", "OLIVO-BACTROCERA-TOSCANA"), -1002),
         ("VITE x OIDIO x TOSCANA",
          os.path.join(CERT, "..", "CASES", "VITE-OIDIO-TOSCANA"), 39)]

real_glob = globmod.glob
out = {"AS_OF": AS_OF.isoformat()}


def run_all():
    return {n: cp.current_pressure(d, v, AS_OF) for n, d, v in CASES}


def dump(o):
    return json.dumps(o, sort_keys=True, default=str)


# 1 ── unpatched: this checkout's own filesystem order
cp.glob.glob = real_glob
plain = run_all()

# 2 ── M27: fixed but reversed
cp.glob.glob = lambda p, **k: sorted(real_glob(p, **k), reverse=True)
m27 = run_all()

# 3 ── a third fixed order: ascending, explicit
cp.glob.glob = lambda p, **k: sorted(real_glob(p, **k))
asc = run_all()
cp.glob.glob = real_glob

out["GATE_E_PREDICATE"] = {
    "SHAPE": "json.dumps(f(x)) == json.dumps(f(x)), both inside one process",
    "NOTE": "under any DETERMINISTIC patch both sides are computed with the patch in force, so "
            "they are equal and the gate passes. Only intra-process non-determinism can fail it."}

# recompute gate E's exact predicate with M27 in force, honestly
cp.glob.glob = lambda p, **k: sorted(real_glob(p, **k), reverse=True)
_a = dump({n: cp.current_pressure(d, v, AS_OF, _pre=cp.load_rows(d, v)) for n, d, v in CASES})
_b = dump({n: cp.current_pressure(d, v, AS_OF) for n, d, v in CASES})
cp.glob.glob = real_glob
out["GATE_E_PREDICATE"]["RECOMPUTED_UNDER_M27"] = {
    "a_equals_b": _a == _b, "VERDICT_THE_PREDICATE_RETURNS": "PASS" if _a == _b else "FAIL"}

# 2b ── did M27 change anything the product shows?
diff = {}
for n, _, _ in CASES:
    P, M, A = plain[n]["PROVINCES"], m27[n]["PROVINCES"], asc[n]["PROVINCES"]
    cells = list(P)
    diff[n] = {
        "n_cells": len(cells),
        "M27_vs_unpatched_cells_with_different_STATE":
            [p for p in cells if P[p].get("STATE") != M.get(p, {}).get("STATE")],
        "M27_vs_unpatched_cells_with_different_VALUE":
            [p for p in cells if P[p].get("VALUE") != M.get(p, {}).get("VALUE")],
        "M27_vs_unpatched_cells_with_different_n_visits":
            [p for p in cells if P[p].get("n_visits") != M.get(p, {}).get("n_visits")],
        "M27_vs_unpatched_cells_with_different_BASELINE_MEDIAN":
            [p for p in cells if P[p].get("BASELINE_MEDIAN") != M.get(p, {}).get("BASELINE_MEDIAN")],
        "M27_vs_unpatched_WHOLE_CASE_JSON_identical": dump(plain[n]) == dump(m27[n]),
        "ASC_vs_unpatched_WHOLE_CASE_JSON_identical": dump(plain[n]) == dump(asc[n]),
        "DENOMINATOR_VAR_declared": json.load(
            open(os.path.join([d for nn, d, _ in CASES if nn == n][0],
                              "collection_index.json"))).get("DENOMINATOR_VAR")}
out["DID_M27_CHANGE_TODAYS_PUBLISHED_OUTPUT"] = diff

# 4 ── coverage of the "every raw file sha256-checked" claim
cov = {}
for n, d, v in CASES:
    idx = json.load(open(os.path.join(d, "collection_index.json")))
    by_file = {r["file"]: r.get("sha256") for r in idx["requests"] if r.get("file")}
    on_disk = sorted(os.path.basename(f) for f in real_glob(os.path.join(d, "RAW", "*.json")))
    loaded = sorted(os.path.basename(f)
                    for f in real_glob(os.path.join(d, "RAW", f"*_v{v}_*.json")))
    checked = [f for f in loaded if by_file.get(f)]
    cov[n] = {"raw_files_on_disk": len(on_disk),
              "raw_files_this_variable_loads": len(loaded),
              "of_those_with_a_recorded_sha256": len(checked),
              "of_those_loaded_with_NO_hash_check": sorted(set(loaded) - set(checked)),
              "files_on_disk_absent_from_the_index": sorted(set(on_disk) - set(by_file))}
out["SHA256_COVERAGE_OF_THE_FILES_GATE_E_CITES"] = cov
out["SHA256_NOTE"] = ("load_rows checks a hash only when `by_file.get(base)` is truthy. A file "
                      "present in RAW/ but absent from collection_index.json, or listed with a "
                      "null sha256, is loaded unverified. Gate E does not run any hash check of "
                      "its own; the sentence in its EVIDENCE describes load_rows.")

json.dump(out, open(os.path.join(HERE, "rt6_gate_e_order.json"), "w"), indent=1, default=str)
print(json.dumps(out, indent=1, default=str))
