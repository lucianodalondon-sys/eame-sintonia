#!/usr/bin/env python3
"""
CERT-V2 / STEP 1b — MY OWN ORDER EXPERIMENT WAS WRONG, AND THE COMMITTED NUMBERS ARE REACHABLE.

p1_order_experiment.json said the committed values (C=19, F=0.918, G=0.424) were not
reproduced by any file order tried, and concluded the published number is "a property of the
machine that produced it".

An independent provenance lens found the defect: my probe reshuffled on EVERY glob call, so
each of the 135 sensitivity grid points was scored against a DIFFERENT join. No filesystem
behaves that way. A real machine has ONE order and holds it.

This file uses FIXED permutations: one order per seed, applied identically to every call.

Out: p1b_fixed_order_experiment.json
"""
import os, sys, json, random, hashlib, glob as gm, datetime as dt
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "ENGINE"))
sys.path.insert(0, os.path.join(HERE, "..", "CASES"))
import current_pressure as cp

AS = dt.date(2026, 9, 6)
OL = os.path.join(HERE, "..", "CASES", "OLIVO-BACTROCERA-TOSCANA")
VI = os.path.join(HERE, "..", "CASES", "VITE-OIDIO-TOSCANA")
real = gm.glob


def fixed_order(seed):
    """One permutation, decided by the seed and the file name only, so every call agrees."""
    def g(p, **k):
        files = list(real(p, **k))
        return sorted(files, key=lambda f: hashlib.md5(
            f"{seed}|{os.path.basename(f)}".encode()).hexdigest())
    return g


def measure():
    s = cp.sensitivity(OL, -1002, AS)
    c = 0
    for d, v in ((OL, -1002), (VI, 39)):
        h = cp.hindcast(d, v, AS.month, AS.day, range(2010, AS.year + 1))
        for y, row in h.items():
            if len({x for x in row.values()
                    if x in (cp.HIGHER, cp.TYPICAL, cp.LOWER)}) > 1:
                c += 1
    h = cp.hindcast(OL, -1002, AS.month, AS.day, range(2007, AS.year + 1))
    flat = [x for y in h.values() for x in y.values()
            if x in (cp.HIGHER, cp.TYPICAL, cp.LOWER)]
    dom = round(max(flat.count(x) for x in (cp.HIGHER, cp.TYPICAL, cp.LOWER)) / len(flat), 3)
    return {"GATE_F": s["MEAN_AGREEMENT"], "GATE_C": c, "GATE_G": dom}


if __name__ == "__main__":
    seed = sys.argv[1]
    cp.glob.glob = fixed_order(seed)
    r = measure()
    r["seed"] = seed
    print(json.dumps(r))
