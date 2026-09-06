#!/usr/bin/env python3
"""
CERT-V2 / STEP 4b — THE PILOT'S OWN CENTRAL DATE CLAIM, RE-MEASURED.

The fifth red-team round (commit 5cf2e48, finding C25) reported this table and called the
whole scoping decision a property of the DATE rather than of the cell:

    2026-06-15  OLIVE 0/10 (latency 241d)   VINE 6/10
    2026-08-01  OLIVE 6/10                  VINE 1/10
    2026-09-06  OLIVE 8/10                  VINE 0/10

"N/10" there is not "has a class". It is the answer_sheet PUBLICATION GATE: a province is
published only if its class survives the 135-point parameter grid (AGREEMENT >= STAB_MIN =
0.80) AND it has been classifiable in at least COV_MIN = 0.60 of the walk-forward seasons.
Step 4 measured the looser quantity, so this file measures the strict one, with the shipped
constants, and puts the two side by side.

Out: p4b_publication_gate_by_date.json
"""
import json, os, sys, datetime as dt

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "ENGINE"))
sys.path.insert(0, os.path.join(HERE, "..", "CASES"))
import current_pressure as cp
from answer_sheet import STAB_MIN, COV_MIN

CASES = [("OLIVE", os.path.join(HERE, "..", "CASES", "OLIVO-BACTROCERA-TOSCANA"), -1002),
         ("VINE", os.path.join(HERE, "..", "CASES", "VITE-OIDIO-TOSCANA"), 39)]
DATES = [dt.date(2026, 6, 15), dt.date(2026, 8, 1), dt.date(2026, 9, 6)]
CLASSED = (cp.HIGHER, cp.TYPICAL, cp.LOWER)

PILOT_C25 = {"2026-06-15": {"OLIVE": "0/10", "VINE": "6/10"},
             "2026-08-01": {"OLIVE": "6/10", "VINE": "1/10"},
             "2026-09-06": {"OLIVE": "8/10", "VINE": "0/10"}}


def memoize_guard():
    real = cp.denominator_guard
    cache = {}

    def patched(rows, case_dir, denom_var):
        k = (os.path.abspath(case_dir), denom_var, len(rows), id(rows))
        if k not in cache:
            cache[k] = real(rows, case_dir, denom_var)
        return cache[k]
    cp.denominator_guard = patched


def main():
    memoize_guard()
    out = {"STAB_MIN": STAB_MIN, "COV_MIN": COV_MIN, "PILOT_C25_TABLE": PILOT_C25,
           "MEASURED": {}}
    for crop, case, var in CASES:
        pre = cp.load_rows(case, var)
        for as_of in DATES:
            live = cp.current_pressure(case, var, as_of, _pre=pre)
            sens = cp.sensitivity(case, var, as_of)
            hind = cp.hindcast(case, var, as_of.month, as_of.day,
                               range(2006, as_of.year + 1))
            P = live["PROVINCES"]
            classed = {p for p, v in P.items() if v.get("STATE") in CLASSED}
            cov = {p: (sum(1 for y in hind if hind[y].get(p) in CLASSED) / max(len(hind), 1))
                   for p in P}
            publishable, withheld = set(), {}
            for p in classed:
                agree = (sens["PER_PROVINCE"].get(p, {}).get("AGREEMENT") or 0)
                c = cov.get(p, 0)
                if agree >= STAB_MIN and c >= COV_MIN:
                    publishable.add(p)
                else:
                    withheld[p] = {"STATE_WOULD_BE": P[p]["STATE"],
                                   "LABEL_STABILITY": agree,
                                   "HISTORICAL_COVERAGE": round(c, 3),
                                   "FAILS": ("stability" if agree < STAB_MIN else "") +
                                            ("+coverage" if c < COV_MIN else "")}
            out["MEASURED"].setdefault(as_of.isoformat(), {})[crop] = {
                "PUBLISHED_STRICT": f"{len(publishable)}/{len(P)}",
                "CLASSED_LOOSE": f"{len(classed)}/{len(P)}",
                "DATA_LATENCY_DAYS": live.get("DATA_LATENCY_DAYS"),
                "MEAN_LABEL_STABILITY": sens["MEAN_AGREEMENT"],
                "PUBLISHED_PROVINCES": {p: P[p]["STATE"] for p in sorted(publishable)},
                "WITHHELD": withheld,
                "UNKNOWN": {p: P[p]["STATE"] for p in sorted(set(P) - classed)}}

    # side by side with what the pilot recorded
    cmp = {}
    for d, byc in sorted(out["MEASURED"].items()):
        cmp[d] = {c: {"PILOT_C25": PILOT_C25.get(d, {}).get(c),
                      "RE_MEASURED_STRICT": byc[c]["PUBLISHED_STRICT"],
                      "RE_MEASURED_LOOSE": byc[c]["CLASSED_LOOSE"],
                      "LATENCY": byc[c]["DATA_LATENCY_DAYS"],
                      "AGREES": PILOT_C25.get(d, {}).get(c) == byc[c]["PUBLISHED_STRICT"]}
                  for c in byc}
    out["SIDE_BY_SIDE"] = cmp

    states = {}
    for d, byc in out["MEASURED"].items():
        for c, v in byc.items():
            for p, s in v["PUBLISHED_PROVINCES"].items():
                states.setdefault(f"{c}|{p}", {})[d] = s
    flip = {k: v for k, v in states.items() if len(set(v.values())) > 1}
    out["PUBLISHED_CELLS_THAT_CHANGE_CLASS_BETWEEN_THESE_THREE_DATES"] = flip
    out["VERDICT"] = {
        "DATE_IS_PART_OF_THE_IDENTITY_OF_THE_SIGNAL": True,
        "CELLS_PUBLISHED_ON_ONE_DATE_AND_NOT_ANOTHER": sum(
            1 for k in {f"{c}|{p}" for d, byc in out["MEASURED"].items()
                        for c, v in byc.items() for p in v["PUBLISHED_PROVINCES"]}
            if len({d for d, byc in out["MEASURED"].items()
                    for c, v in byc.items()
                    if f"{c}|{k.split('|')[1]}" == k and k.split('|')[1]
                    in v["PUBLISHED_PROVINCES"]}) < len(DATES))}

    json.dump(out, open(os.path.join(HERE, "p4b_publication_gate_by_date.json"), "w"),
              indent=1, default=str)
    print(f"STAB_MIN={STAB_MIN}  COV_MIN={COV_MIN}\n")
    print(f"{'DATE':12s} {'CROP':6s} {'pilot C25':10s} {'re-measured':12s} {'loose':8s} "
          f"{'latency':8s} agrees")
    for d, byc in sorted(cmp.items()):
        for c, v in byc.items():
            print(f"{d:12s} {c:6s} {str(v['PILOT_C25']):10s} {v['RE_MEASURED_STRICT']:12s} "
                  f"{v['RE_MEASURED_LOOSE']:8s} {str(v['LATENCY']):8s} {v['AGREES']}")
    print("\npublished cells whose CLASS changes between these three dates:")
    for k, v in flip.items():
        print("  ", k, v)


if __name__ == "__main__":
    main()
