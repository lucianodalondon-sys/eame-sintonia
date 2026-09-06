#!/usr/bin/env python3
"""
CERT-V2 / STEP 1 — WHY THE CLEAN CHECKOUT DID NOT REPRODUCE.

The blind re-run of ENGINE/gates.py from a clean checkout of a4d19dd disagreed with the
gates.json committed at that same commit, on four lines:

    gate C  disagreeing season-cells   19 -> 18
    gate F  OLIVO label stability   0.918 -> 0.924
    gate G  OLIVO dominant share    0.424 -> 0.432
    gate J  NOT_TESTABLE(PARTIALLY_OVERLAPS) -> FAIL (inventory not readable)

VITE reproduced to the digit (0.596 / 0.806). Only OLIVO moved, and OLIVO is the only case
that declares DENOMINATOR_VAR. This file tests that coincidence instead of asserting it.

TWO CANDIDATE CAUSES, both inside current_pressure.denominator_guard:

  H1  ORDER DEPENDENCE.  The guard builds  den[r["id_survey"]] = value  while iterating an
      UNSORTED glob.glob(). Whichever file the filesystem happens to hand over LAST wins the
      key. If the same id_survey carries different values in different files, the set of
      dropped visits — and therefore every downstream number — is a property of the
      directory listing order, not of the data.

  H2  JOIN KEY IS NOT UNIQUE.  Deeper than H1: if one id_survey appears in several season
      files, the join between the numerator variable (-1002) and the denominator variable (1)
      is wrong in EVERY order. A 2015 denominator can silence a 2006 visit.

Both are tested by execution, not by reading. H1 is tested by re-running the SHIPPED module
against the SAME bytes in three different file orders. Nothing in ENGINE/ is modified: the
order is changed by monkeypatching glob.glob for the duration of one call, which is exactly
what a different filesystem does to the shipped code.

Run:  py p1_drift_cause.py
Out:  p1_drift_cause.json
"""
import json, os, sys, glob as globmod, hashlib, collections, datetime as dt

HERE = os.path.dirname(os.path.abspath(__file__))
ENGINE = os.path.join(HERE, "..", "ENGINE")
CASES = os.path.join(HERE, "..", "CASES")
sys.path.insert(0, ENGINE)
sys.path.insert(0, CASES)
import current_pressure as cp

OLIVE = os.path.join(CASES, "OLIVO-BACTROCERA-TOSCANA")
VINE = os.path.join(CASES, "VITE-OIDIO-TOSCANA")
AS_OF = dt.date(2026, 9, 6)


def with_glob_order(order):
    """Return a context that makes glob.glob deterministic in a chosen direction.
    'asc' and 'desc' are two legal filesystem orders; the shipped code assumes neither."""
    real = globmod.glob

    class C:
        def __enter__(self):
            cp.glob.glob = lambda p, **k: sorted(real(p, **k), reverse=(order == "desc"))

        def __exit__(self, *a):
            cp.glob.glob = real
    return C()


def run(case, var, order):
    with with_glob_order(order):
        r = cp.current_pressure(case, var, AS_OF)
    return {p: {"STATE": v.get("STATE"), "VALUE": v.get("VALUE"),
                "n_sites": v.get("n_sites"), "n_visits": v.get("n_visits"),
                "PERCENTILE": v.get("PERCENTILE")} for p, v in r["PROVINCES"].items()}


def join_key_uniqueness(case, denom_var):
    """H2: is id_survey unique in the denominator variable's own files?"""
    per_key_files = collections.defaultdict(set)
    per_key_vals = collections.defaultdict(set)
    for fn in sorted(globmod.glob(os.path.join(case, "RAW", f"*_v{denom_var}_*.json"))):
        b = os.path.basename(fn)
        for r in json.load(open(fn)):
            k = r.get("id_survey")
            v = r.get("val")
            per_key_files[k].add(b)
            per_key_vals[k].add(None if v in (None, "") else str(v))
    multi_file = {k for k, f in per_key_files.items() if len(f) > 1}
    conflicting = {k for k, v in per_key_vals.items() if len(v) > 1}
    # a key that decides DROP vs KEEP differently depending on which file wins
    decisive = {k for k in conflicting
                if any(x in (None, "0", "0.0") for x in per_key_vals[k])
                and any(x not in (None, "0", "0.0") for x in per_key_vals[k])}
    return {"denominator_var": denom_var,
            "id_survey_keys": len(per_key_files),
            "keys_in_more_than_one_file": len(multi_file),
            "keys_with_conflicting_values": len(conflicting),
            "keys_where_the_conflict_flips_DROP_vs_KEEP": len(decisive),
            "example": sorted(decisive)[:3] and
                       {str(k): {"values": sorted(per_key_vals[k], key=str),
                                 "files": sorted(per_key_files[k])}
                        for k in sorted(decisive)[:2]}}


def main():
    out = {"AS_OF": AS_OF.isoformat(), "H1_ORDER_DEPENDENCE": {}, "H2_JOIN_KEY": {}}

    for name, case, var, denom in [("OLIVO x BACTROCERA x TOSCANA", OLIVE, -1002, 1),
                                   ("VITE x OIDIO x TOSCANA", VINE, 39, None)]:
        asc, desc = run(case, var, "asc"), run(case, var, "desc")
        changed = sorted(p for p in asc if asc[p] != desc.get(p))
        out["H1_ORDER_DEPENDENCE"][name] = {
            "DECLARES_DENOMINATOR_VAR": denom is not None,
            "PROVINCE_CELLS": len(asc),
            "CELLS_THAT_CHANGE_WITH_FILE_ORDER": len(changed),
            "CHANGED": {p: {"asc": asc[p], "desc": desc[p]} for p in changed},
            "STATE_CHANGES": sorted(p for p in changed
                                    if asc[p]["STATE"] != desc[p]["STATE"])}
        if denom is not None:
            out["H2_JOIN_KEY"][name] = join_key_uniqueness(case, denom)
        else:
            out["H2_JOIN_KEY"][name] = {"denominator_var": None,
                                        "note": "no denominator guard runs for this case"}

    # gate-level consequence: the two numbers that drifted, recomputed under both orders
    gate_numbers = {}
    for order in ("asc", "desc"):
        with with_glob_order(order):
            s = cp.sensitivity(OLIVE, -1002, AS_OF)
            h = cp.hindcast(OLIVE, -1002, AS_OF.month, AS_OF.day, range(2007, AS_OF.year + 1))
        flat = [x for y in h.values() for x in y.values()
                if x in (cp.HIGHER, cp.TYPICAL, cp.LOWER)]
        dom = max(flat.count(x) for x in (cp.HIGHER, cp.TYPICAL, cp.LOWER)) / len(flat)
        gate_numbers[order] = {"GATE_F_MEAN_AGREEMENT": s["MEAN_AGREEMENT"],
                               "GATE_G_DOMINANT_SHARE": round(dom, 3),
                               "n_classified": len(flat)}
    out["GATE_NUMBERS_BY_FILE_ORDER"] = gate_numbers
    out["COMMITTED_AT_a4d19dd"] = {"GATE_F_MEAN_AGREEMENT": 0.918,
                                   "GATE_G_DOMINANT_SHARE": 0.424}

    seen = {v["GATE_F_MEAN_AGREEMENT"] for v in gate_numbers.values()} | {0.918}
    out["VERDICT"] = {
        "H1_ORDER_DEPENDENCE_PROVED":
            any(v["CELLS_THAT_CHANGE_WITH_FILE_ORDER"] > 0
                for v in out["H1_ORDER_DEPENDENCE"].values()),
        "H2_JOIN_KEY_NOT_UNIQUE":
            any(isinstance(v, dict) and v.get("keys_in_more_than_one_file", 0) > 0
                for v in out["H2_JOIN_KEY"].values()),
        "DISTINCT_GATE_F_VALUES_OBSERVED": sorted(seen),
        "REPRODUCIBLE_FROM_CLEAN_CHECKOUT": False,
        "NOTE": "gate J's drift has a separate and simpler cause, recorded in p2_gate_inventory."}

    json.dump(out, open(os.path.join(HERE, "p1_drift_cause.json"), "w"), indent=1, default=str)
    print(json.dumps(out["VERDICT"], indent=1))
    print("\nH1 per case:")
    for k, v in out["H1_ORDER_DEPENDENCE"].items():
        print(f"  {k:32s} denom={v['DECLARES_DENOMINATOR_VAR']} "
              f"cells_changed_by_file_order={v['CELLS_THAT_CHANGE_WITH_FILE_ORDER']}/"
              f"{v['PROVINCE_CELLS']} state_changes={v['STATE_CHANGES']}")
    print("\nH2 join key:")
    for k, v in out["H2_JOIN_KEY"].items():
        print(f"  {k:32s} {v}")
    print("\nGate numbers by file order:", json.dumps(gate_numbers))


if __name__ == "__main__":
    main()
