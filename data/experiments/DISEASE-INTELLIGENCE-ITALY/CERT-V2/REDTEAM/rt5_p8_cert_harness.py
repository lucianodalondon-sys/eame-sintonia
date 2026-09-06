#!/usr/bin/env python3
"""RT5 -- ERROR IN THE CERTIFICATION ITSELF.

CERT-V2/p1_order_experiment.json is the artefact the certification offers as proof that the
committed numbers are "a property of the machine". Its six seeded rows were produced by
CERT-V2/_probe_order.py, which is NOT committed (CERT-V2/.gitignore excludes _probe_*.py).
Its mechanism is:

    rnd = random.Random(seed)
    cp.glob.glob = lambda p, **k: (lambda L: (rnd.shuffle(L), L)[1])(list(real(p, **k)))

ONE shared Random, RESHUFFLED ON EVERY CALL. sensitivity() invokes current_pressure 135 times
and each invocation calls denominator_guard -> glob.glob, so each of the 135 grid points is
computed against a DIFFERENT denominator join. hindcast() does the same, once per season.

No filesystem behaves that way. A directory listing is stable for the duration of a run; that
is the whole premise of the "different machine, different order" argument. So the spread the
certification reports is partly an artefact of its own harness.

This script runs BOTH harnesses over the same seeds and compares:
   FIXED   -- one permutation, held for the whole run (what a real filesystem does)
   PERCALL -- the certification's per-call reshuffle
"""
import json, os, sys, glob as globmod, random, datetime as dt, collections, time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "ENGINE")); sys.path.insert(0, os.path.join(ROOT, "CASES"))
import current_pressure as cp

AS = dt.date(2026, 9, 6)
OL = os.path.join(ROOT, "CASES", "OLIVO-BACTROCERA-TOSCANA")
VI = os.path.join(ROOT, "CASES", "VITE-OIDIO-TOSCANA")
REAL = globmod.glob
SEEDS = [1, 2, 3, 4, 5, 6]


def gate_G_and_C():
    H, T, L = cp.HIGHER, cp.TYPICAL, cp.LOWER
    c = 0
    for d, v in ((OL, -1002), (VI, 39)):
        h = cp.hindcast(d, v, AS.month, AS.day, range(2010, AS.year + 1))
        for row in h.values():
            if len({x for x in row.values() if x in (H, T, L)}) > 1:
                c += 1
    h = cp.hindcast(OL, -1002, AS.month, AS.day, range(2007, AS.year + 1))
    flat = [x for y in h.values() for x in y.values() if x in (H, T, L)]
    return c, round(max(flat.count(x) for x in (H, T, L)) / len(flat), 3)


def set_percall(seed):
    rnd = random.Random(seed)
    cp.glob.glob = lambda p, **k: (lambda Lst: (rnd.shuffle(Lst), Lst)[1])(list(REAL(p, **k)))


def set_fixed(seed):
    rnd = random.Random(seed)
    fixed = {}
    def g(p, **k):
        r = list(REAL(p, **k))
        key = p
        if key not in fixed:
            o = list(r); rnd.shuffle(o); fixed[key] = o
        # keep the memoised order, restricted to what actually exists
        return [x for x in fixed[key] if x in set(r)] or r
    cp.glob.glob = g


rows = []
for seed in SEEDS:
    for mode, setter in (("FIXED_one_order_for_the_whole_run", set_fixed),
                         ("PERCALL_the_certifications_harness", set_percall)):
        setter(seed)
        t0 = time.time()
        c, g = gate_G_and_C()
        f = cp.sensitivity(OL, -1002, AS)["MEAN_AGREEMENT"]
        cp.glob.glob = REAL
        rows.append({"seed": seed, "MODE": mode, "GATE_C": c, "GATE_G_olive": g, "GATE_F_olive": f,
                     "seconds": round(time.time() - t0)})
        print(f"seed {seed}  {mode:36s} C={c} G={g} F={f}  [{rows[-1]['seconds']}s]", flush=True)

cp.glob.glob = REAL
fixed = [r for r in rows if r["MODE"].startswith("FIXED")]
perc = [r for r in rows if r["MODE"].startswith("PERCALL")]
out = {
    "CERT_REPORTED_p1_order_experiment": {
        "GATE_F": [0.918, 0.921, 0.922, 0.923, 0.924],
        "GATE_C_disagreeing": [18, 19],
        "GATE_G_olive_dom": [0.424, 0.432, 0.439, 0.447],
        "note": "DISTINCT_VALUES_OBSERVED as published by the certification"},
    "RT5_FIXED_ORDER": {"GATE_F": sorted({r["GATE_F_olive"] for r in fixed}),
                        "GATE_C": sorted({r["GATE_C"] for r in fixed}),
                        "GATE_G": sorted({r["GATE_G_olive"] for r in fixed})},
    "RT5_PERCALL_RESHUFFLE": {"GATE_F": sorted({r["GATE_F_olive"] for r in perc}),
                              "GATE_C": sorted({r["GATE_C"] for r in perc}),
                              "GATE_G": sorted({r["GATE_G_olive"] for r in perc})},
    "ROWS": rows,
    "READING": "values that appear only under PERCALL are artefacts of the certification's "
               "harness, because no filesystem reorders a directory between two reads inside "
               "one process. Values that appear under FIXED are genuine file-order effects."}
json.dump(out, open(os.path.join(HERE, "rt5_p8_cert_harness.json"), "w"), indent=1)
print("\nFIXED   F", out["RT5_FIXED_ORDER"]["GATE_F"], " C", out["RT5_FIXED_ORDER"]["GATE_C"],
      " G", out["RT5_FIXED_ORDER"]["GATE_G"])
print("PERCALL F", out["RT5_PERCALL_RESHUFFLE"]["GATE_F"], " C", out["RT5_PERCALL_RESHUFFLE"]["GATE_C"],
      " G", out["RT5_PERCALL_RESHUFFLE"]["GATE_G"])
print("CERT    F", out["CERT_REPORTED_p1_order_experiment"]["GATE_F"])
print("wrote rt5_p8_cert_harness.json")
