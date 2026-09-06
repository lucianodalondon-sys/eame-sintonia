#!/usr/bin/env python3
"""Regenerate regional_coverage.json with the CURRENT engine, so no artefact on disk disagrees
with the documents. Coverage and stability are both evaluated at the same AS_OF."""
import datetime as dt, json, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import current_pressure as cp
from answer_sheet import STAB_MIN, COV_MIN
from statistics import mean

CASES = [("OLIVO x BACTROCERA x TOSCANA", "../CASES/OLIVO-BACTROCERA-TOSCANA", -1002),
         ("VITE x OIDIO x TOSCANA", "../CASES/VITE-OIDIO-TOSCANA", 39)]
as_of = dt.date.fromisoformat(sys.argv[1]) if len(sys.argv) > 1 else dt.date(2026, 9, 6)
rep = {}
for name, d, v in CASES:
    live = cp.current_pressure(d, v, as_of)
    sens = cp.sensitivity(d, v, as_of)
    hind = cp.hindcast(d, v, as_of.month, as_of.day, range(2007, as_of.year + 1))
    rows = {}
    for p in sorted(live["PROVINCES"]):
        st = [hind[y].get(p) for y in sorted(hind)]
        cls = sum(1 for s in st if s in (cp.HIGHER, cp.TYPICAL, cp.LOWER))
        stab = sens["PER_PROVINCE"].get(p, {}).get("AGREEMENT")
        rows[p] = {"SEASONS_EVALUATED": len(st), "CLASSIFIED": cls,
                   "COVERAGE": round(cls / len(st), 3),
                   "UNKNOWN_NO_DATA": sum(1 for s in st if s == cp.UNKNOWN_NO_DATA),
                   "UNKNOWN_NO_BASELINE": sum(1 for s in st if s == cp.UNKNOWN_NO_BASELINE),
                   "LABEL_STABILITY": stab, "LIVE_STATE": live["PROVINCES"][p]["STATE"]}
    pub = [p for p, r in rows.items()
           if (r["LABEL_STABILITY"] or 0) >= STAB_MIN and r["COVERAGE"] >= COV_MIN
           and r["LIVE_STATE"] in (cp.HIGHER, cp.TYPICAL, cp.LOWER)]
    rep[name] = {"AS_OF": as_of.isoformat(), "PROVINCES": rows,
                 "MEAN_LABEL_STABILITY": sens["MEAN_AGREEMENT"], "GRID_SIZE": sens["GRID_SIZE"],
                 "DATA_LATENCY_DAYS": live["DATA_LATENCY_DAYS"], "VALUE_MODE": live["VALUE_MODE"],
                 "DENOMINATOR_GUARD": live["DENOMINATOR_GUARD"],
                 "PUBLISHABLE_PROVINCES": pub, "PUBLISHABLE_N": len(pub)}
    print(f"{name:30s} grid={sens['GRID_SIZE']} stab={sens['MEAN_AGREEMENT']} "
          f"latency={live['DATA_LATENCY_DAYS']}d publishable={len(pub)}/{len(rows)} {pub}")
json.dump(rep, open("regional_coverage.json", "w"), indent=1)
