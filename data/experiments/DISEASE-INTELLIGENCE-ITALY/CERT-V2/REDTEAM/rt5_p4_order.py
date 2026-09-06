#!/usr/bin/env python3
"""RT5 / REPRODUCIBILITY 1 -- independent reproduction of the order-dependence claim.

Written from scratch. Imports NOTHING from CERT-V2. Nothing in ENGINE/ or CASES/ is edited.

WHAT IS PATCHED, AND WHY IT IS FAITHFUL
denominator_guard() does, verbatim:

    den = {}
    for fn in glob.glob(RAW/*_v{denom}_*.json):
        for r in json.load(open(fn)):
            v = r.get("val")
            try: den[r["id_survey"]] = float(v) if v not in (None,"") else None
            except ValueError: den[r["id_survey"]] = None
    kept = [r for r in rows if den.get(r.get("id_survey"))]

The ONLY order-sensitive step is which file writes each id_survey LAST. So for a given file
order I build `den` by replaying exactly that loop over a cached parse of each file, then swap
in a denominator_guard that returns the identical `kept`. VALIDATED in MODE=validate against
the untouched shipped function driven by a patched glob.glob -- the two must agree exactly.

GATES REPRODUCED, using gates.py's own definitions:
  C  sum over both cases of hindcast(9,6,range(2010,2027)) years where provinces disagree
  F  sensitivity(as_of).MEAN_AGREEMENT per case               (135-point grid)
  G  hindcast(9,6,range(2007,2027)) dominant-class share      per case
"""
import json, os, sys, glob as globmod, random, datetime as dt, itertools, argparse, time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "ENGINE"))
sys.path.insert(0, os.path.join(ROOT, "CASES"))
import current_pressure as cp

AS_OF = dt.date(2026, 9, 6)
CASES = [("OLIVO x BACTROCERA x TOSCANA", os.path.join(ROOT, "CASES", "OLIVO-BACTROCERA-TOSCANA"), -1002),
         ("VITE x OIDIO x TOSCANA", os.path.join(ROOT, "CASES", "VITE-OIDIO-TOSCANA"), 39)]

_ORIG_GUARD = cp.denominator_guard
_PARSE = {}          # filename -> parsed rows, parsed once


def denom_files(case_dir, denom_var):
    return sorted(globmod.glob(os.path.join(case_dir, "RAW", f"*_v{denom_var}_*.json")))


def parsed(fn):
    if fn not in _PARSE:
        _PARSE[fn] = json.load(open(fn))
    return _PARSE[fn]


def build_den(order):
    """Replay denominator_guard's dict-building loop verbatim, in the given file order."""
    den = {}
    for fn in order:
        for r in parsed(fn):
            v = r.get("val")
            try:
                den[r["id_survey"]] = float(v) if v not in (None, "") else None
            except ValueError:
                den[r["id_survey"]] = None
    return den


def guard_factory(order_by_case):
    cache = {}
    def guard(rows, case_dir, denom_var):
        k = os.path.abspath(case_dir)
        if k not in cache:                      # den depends only on the file order
            cache[k] = build_den(order_by_case[k])
        den = cache[k]
        kept = [r for r in rows if den.get(r.get("id_survey"))]
        return kept, {"dropped_zero_or_unknown_denominator": len(rows) - len(kept),
                      "denominator_var": denom_var}
    return guard


def gate_numbers():
    """Exactly gates.py's arithmetic for C, F, G."""
    H, T, L = cp.HIGHER, cp.TYPICAL, cp.LOWER
    C = 0
    F, G = {}, {}
    for name, d, v in CASES:
        h_c = cp.hindcast(d, v, AS_OF.month, AS_OF.day, range(2010, AS_OF.year + 1))
        for row in h_c.values():
            if len({s for s in row.values() if s in (H, T, L)}) > 1:
                C += 1
        F[name] = cp.sensitivity(d, v, AS_OF)["MEAN_AGREEMENT"]
        h_g = cp.hindcast(d, v, AS_OF.month, AS_OF.day, range(2007, AS_OF.year + 1))
        flat = [s for y in h_g.values() for s in y.values() if s in (H, T, L)]
        dom = max(flat.count(x) for x in (H, T, L)) / len(flat) if flat else None
        G[name] = round(dom, 3) if dom else None
    return {"GATE_C_disagreeing_season_cells": C,
            "GATE_F_MEAN_AGREEMENT": F, "GATE_G_DOMINANT_SHARE": G}


def orders_for(label, rng=None):
    """Return {abs_case_dir: file order} for every case that declares a denominator."""
    out = {}
    for _n, d, _v in CASES:
        idx = json.load(open(os.path.join(d, "collection_index.json")))
        dv = idx.get("DENOMINATOR_VAR")
        if dv is None:
            continue
        fs = denom_files(d, dv)
        if label == "asc":
            o = list(fs)
        elif label == "desc":
            o = list(reversed(fs))
        else:
            o = list(fs); rng.shuffle(o)
        out[os.path.abspath(d)] = o
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", default="search", choices=["search", "validate"])
    ap.add_argument("--seeds", type=int, default=20)
    a = ap.parse_args()

    if a.mode == "validate":
        # drive the UNTOUCHED shipped denominator_guard through a patched glob, and compare
        # to the fast replay. They must agree to the digit.
        res = {}
        for label in ("asc", "desc"):
            o = orders_for(label)
            real = globmod.glob
            def fake(pat, *args, **kw):
                r = real(pat, *args, **kw)
                for cd, order in o.items():
                    if os.path.abspath(os.path.dirname(os.path.dirname(pat))) == cd and r:
                        if set(os.path.abspath(x) for x in r) == set(os.path.abspath(x) for x in order):
                            return list(order)
                return r
            cp.glob.glob = fake
            cp.denominator_guard = _ORIG_GUARD
            slow = {n: cp.current_pressure(d, v, AS_OF)["PROVINCES"] for n, d, v in CASES}
            cp.glob.glob = real
            cp.denominator_guard = guard_factory(o)
            fast = {n: cp.current_pressure(d, v, AS_OF)["PROVINCES"] for n, d, v in CASES}
            res[label] = {"IDENTICAL": json.dumps(slow, sort_keys=True, default=str) ==
                                      json.dumps(fast, sort_keys=True, default=str)}
            cp.denominator_guard = _ORIG_GUARD
            print(f"validate {label}: harness == shipped code -> {res[label]['IDENTICAL']}")
        json.dump(res, open(os.path.join(HERE, "rt5_p4_order_validate.json"), "w"), indent=1)
        return

    runs = []
    labels = [("asc", None), ("desc", None)] + [(f"seed{i}", i) for i in range(1, a.seeds + 1)]
    # the shipped, unpatched behaviour on THIS machine, first
    cp.denominator_guard = _ORIG_GUARD
    t0 = time.time()
    nat = gate_numbers()
    nat["ORDER"] = "native (unpatched glob on this filesystem)"
    runs.append(nat)
    print(f"native  C={nat['GATE_C_disagreeing_season_cells']} "
          f"F={nat['GATE_F_MEAN_AGREEMENT']} G={nat['GATE_G_DOMINANT_SHARE']}  "
          f"[{time.time()-t0:.0f}s]")

    for label, seed in labels:
        o = orders_for(label, random.Random(seed) if seed is not None else None)
        cp.denominator_guard = guard_factory(o)
        t0 = time.time()
        r = gate_numbers()
        r["ORDER"] = label
        runs.append(r)
        print(f"{label:8s} C={r['GATE_C_disagreeing_season_cells']} "
              f"F={r['GATE_F_MEAN_AGREEMENT']} G={r['GATE_G_DOMINANT_SHARE']}  "
              f"[{time.time()-t0:.0f}s]", flush=True)
    cp.denominator_guard = _ORIG_GUARD

    COMMITTED = {"GATE_C": 19, "GATE_F_OLIVO": 0.918, "GATE_G_OLIVO": 0.424,
                 "GATE_F_VITE": 0.596, "GATE_G_VITE": 0.806}
    seen_C = sorted({r["GATE_C_disagreeing_season_cells"] for r in runs})
    seen_F = sorted({r["GATE_F_MEAN_AGREEMENT"][CASES[0][0]] for r in runs})
    seen_G = sorted({r["GATE_G_DOMINANT_SHARE"][CASES[0][0]] for r in runs})
    seen_Fv = sorted({r["GATE_F_MEAN_AGREEMENT"][CASES[1][0]] for r in runs})
    seen_Gv = sorted({r["GATE_G_DOMINANT_SHARE"][CASES[1][0]] for r in runs})
    out = {"N_ORDERS_TRIED": len(runs), "COMMITTED_AT_a4d19dd": COMMITTED, "RUNS": runs,
           "DISTINCT_OLIVO": {"GATE_C": seen_C, "GATE_F": seen_F, "GATE_G": seen_G},
           "DISTINCT_VITE": {"GATE_F": seen_Fv, "GATE_G": seen_Gv},
           "COMMITTED_VALUE_HIT": {
               "GATE_C_19": 19 in seen_C, "GATE_F_OLIVO_0.918": 0.918 in seen_F,
               "GATE_G_OLIVO_0.424": 0.424 in seen_G,
               "GATE_F_VITE_0.596": 0.596 in seen_Fv, "GATE_G_VITE_0.806": 0.806 in seen_Gv},
           "ALL_THREE_OLIVO_TOGETHER": [r["ORDER"] for r in runs
                                        if r["GATE_C_disagreeing_season_cells"] == 19
                                        and r["GATE_F_MEAN_AGREEMENT"][CASES[0][0]] == 0.918
                                        and r["GATE_G_DOMINANT_SHARE"][CASES[0][0]] == 0.424]}
    p = os.path.join(HERE, "rt5_p4_order.json")
    json.dump(out, open(p, "w"), indent=1)
    print("\nDISTINCT OLIVO  C:", seen_C, " F:", seen_F, " G:", seen_G)
    print("DISTINCT VITE   F:", seen_Fv, " G:", seen_Gv)
    print("COMMITTED HIT  :", out["COMMITTED_VALUE_HIT"])
    print("ORDERS HITTING ALL THREE OLIVO VALUES:", out["ALL_THREE_OLIVO_TOGETHER"])
    print("wrote", p)


if __name__ == "__main__":
    main()
