#!/usr/bin/env python3
"""
C11 — DOES SURVEY EFFORT AGREE ACROSS PROVINCES MORE THAN THE DISEASE DOES?

CHECKPOINT 12 calls this "the strongest single discriminator found" and used it to WITHDRAW the
oidio case's province agreement as evidence. An independent arbiter then pointed out that the
number had no code: it was computed once in an ad-hoc shell heredoc and never committed, so the
mission's sharpest claim could not be re-run by anyone. That is exactly the failure this project
keeps finding in other people's work. Here it is as a script.

The logic: if the monitoring programme's INTENSITY agrees across provinces more strongly than the
biological signal does, then "provinces agree about which seasons were bad" is a statement about
the programme, not about the disease.
"""
import json, glob, os, sys, collections, itertools
from statistics import mean
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import province_agreement as pa


def series(case_dir, var, minsites=8):
    """Return (effort, disease) province -> year -> value, from one pass over the raw files."""
    idx = json.load(open(os.path.join(case_dir, "collection_index.json")))
    scale, _, _ = pa.rc.build_scale(idx.get("codes") or [], var)
    E, D = collections.defaultdict(dict), collections.defaultdict(dict)
    for fn in sorted(glob.glob(os.path.join(case_dir, "RAW", f"*_v{var}_*.json"))):
        y = int(os.path.basename(fn)[:-5].split("_")[-1])
        prov = collections.defaultdict(lambda: collections.defaultdict(list))
        for r in json.load(open(fn)):
            v = r.get("val")
            if v is None: continue
            if scale:
                sc = scale.get(str(v))
                if sc is None: continue          # never fall back to the code id
                val = float(sc["ordinal"])
            else:
                try: val = float(str(v).replace(",", "."))
                except ValueError: continue
            prov[r.get("nome_area")][r["id_field"]].append(val)
        for p, sites in prov.items():
            if p and len(sites) >= minsites:
                mx = [max(v) for v in sites.values()]
                D[p][y] = sum(1 for x in mx if x > 0) / len(mx)          # INCIDENCE, as published
                E[p][y] = sum(len(v) for v in sites.values()) / len(sites)  # visits per site
    return E, D


def agreement(P, min_seasons=10, min_overlap=8):
    provs = sorted([p for p in P if len(P[p]) >= min_seasons])
    rs = []
    for a, b in itertools.combinations(provs, 2):
        sh = sorted(set(P[a]) & set(P[b]))
        if len(sh) >= min_overlap:
            r = pa.spear([P[a][y] for y in sh], [P[b][y] for y in sh])
            if r is not None: rs.append(r)
    return len(rs), sum(1 for r in rs if r > 0), (mean(rs) if rs else None)


if __name__ == "__main__":
    CASES = [("OIDIO", "VITE-OIDIO-TOSCANA", 39), ("BACTROCERA", "OLIVO-BACTROCERA-TOSCANA", -1002)]
    if len(sys.argv) > 2: CASES = [(os.path.basename(sys.argv[1]), sys.argv[1], int(sys.argv[2]))]
    print(f"{'case':12s} {'EFFORT pairs pos rho':>26s} {'DISEASE pairs pos rho':>26s}   verdict")
    for name, d, var in CASES:
        E, D = series(d, var)
        ne, pe, re_ = agreement(E)
        nd, pd, rd = agreement(D)
        verdict = ("EFFORT AGREES MORE -> agreement is the programme's, not the biology's"
                   if (re_ or 0) > (rd or 0) else "disease exceeds effort -> agreement survives")
        print(f"{name:12s} {ne:8d} {pe:4d} {re_:+9.3f} {nd:12d} {pd:4d} {rd:+9.3f}   {verdict}")
