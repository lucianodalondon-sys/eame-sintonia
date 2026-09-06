#!/usr/bin/env python3
"""RT3-E11. Does the published class depend on WHEN the code table was collected?

build_scale() assigns each code an ORDINAL by ranks.index(rank) -- the position of that code's
rank inside the SET of ranks present in the table. If a later collection returns MORE codes,
the set of ranks can grow and every existing code can be renumbered. The archive's ordinal
scale is then a function of the collection date, and so is SEVERITY (a mean of ordinals) and
so is every percentile computed from it.

The shipped VITE index stores 16 codes; the source serves 74 for 2025/2026 today (RT3-E9).
This script compares the scale built from the STORED table with the scale built from the
LIVE table, and then re-runs the published output under each.
"""
import sys, os, json, datetime as dt, collections

HERE = os.path.dirname(os.path.abspath(__file__))
ENG = os.path.abspath(os.path.join(HERE, "..", "..", "ENGINE"))
CAS = os.path.abspath(os.path.join(HERE, "..", "..", "CASES"))
sys.path.insert(0, ENG)
sys.path.insert(0, CAS)
import current_pressure as cp
from run_case import build_scale
from collect_generic import fetch, unwrap

AS_OF = dt.date(2026, 9, 6)
OUT = {}

for cname, crop, schema, var in (("VITE-OIDIO-TOSCANA", 3, 8, 39),):
    d = os.path.join(CAS, cname)
    idx = json.load(open(os.path.join(d, "collection_index.json"), encoding="utf-8"))
    stored_codes = idx.get("codes") or []

    # the most complete table the source will serve today, exactly as collect_generic picks it
    best = []
    for y in range(2006, 2027):
        js = fetch({"tipo_elab": "elab_pivot", "year": y, "crop": crop,
                    "survey_schema": schema, "survey_var": var, "difesa": "all",
                    "week": "all", "cultivar": "all", "area": "all",
                    "accesso": "all", "user_access": "all"})
        ok, rc, rows, fb = unwrap(js)
        cand = ((fb or {}).get("survey_code") or {}).get("data") or []
        if len(cand) > len(best):
            best = cand

    s_stored, u_stored, h_stored = build_scale(stored_codes, var)
    s_live, u_live, h_live = build_scale(best, var)

    rows, scale, meta = cp.load_rows(d, var)
    vals = collections.Counter(str(r.get("val")) for r in rows if r.get("val") not in (None, ""))
    dec_stored = sum(n for v, n in vals.items() if v in s_stored)
    dec_live = sum(n for v, n in vals.items() if v in s_live)

    changed = {k: {"label": s_stored[k]["label"],
                   "ordinal_stored": s_stored[k]["ordinal"],
                   "ordinal_live": s_live[k]["ordinal"]}
               for k in s_stored if k in s_live
               and s_stored[k]["ordinal"] != s_live[k]["ordinal"]}

    res = {
        "N_CODES_IN_STORED_INDEX_ALL_VARS": len(stored_codes),
        "N_CODES_IN_MOST_COMPLETE_LIVE_TABLE_ALL_VARS": len(best),
        "N_CODES_FOR_THIS_VAR_STORED": len(s_stored),
        "N_CODES_FOR_THIS_VAR_LIVE": len(s_live),
        "SCALE_STORED": {k: (v["label"], v["rank"], v["ordinal"]) for k, v in sorted(s_stored.items())},
        "SCALE_LIVE": {k: (v["label"], v["rank"], v["ordinal"]) for k, v in sorted(s_live.items())},
        "UNRESOLVED_STORED": u_stored, "UNRESOLVED_LIVE": u_live,
        "DERIVATION_METHODS_STORED": h_stored, "DERIVATION_METHODS_LIVE": h_live,
        "CODES_WHOSE_ORDINAL_CHANGES": changed,
        "N_CODES_WHOSE_ORDINAL_CHANGES": len(changed),
        "N_ROWS_WITH_A_VALUE": sum(vals.values()),
        "N_ROWS_DECODABLE_BY_STORED_SCALE": dec_stored,
        "N_ROWS_DECODABLE_BY_LIVE_SCALE": dec_live,
        "DISTINCT_VALS_IN_ARCHIVE": sorted(vals),
        "VALS_NOT_IN_STORED_SCALE": sorted(v for v in vals if v not in s_stored),
    }

    # what would publish under each scale?
    pub = {}
    for tag, sc in (("STORED_SCALE", s_stored), ("LIVE_SCALE", s_live)):
        for metric in ("INCIDENCE", "SEVERITY"):
            r = cp.current_pressure(d, var, AS_OF, metric, _pre=(rows, sc, meta))
            pub[f"{tag}|{metric}"] = {
                p: {"STATE": v["STATE"], "VALUE": v.get("VALUE"),
                    "PERCENTILE": v.get("PERCENTILE")} for p, v in r["PROVINCES"].items()}
    diffs = {}
    for metric in ("INCIDENCE", "SEVERITY"):
        a, b = pub[f"STORED_SCALE|{metric}"], pub[f"LIVE_SCALE|{metric}"]
        diffs[metric] = {
            "CELLS_WITH_DIFFERENT_STATE": [p for p in a if a[p]["STATE"] != b[p]["STATE"]],
            "CELLS_WITH_DIFFERENT_VALUE": [p for p in a if a[p]["VALUE"] != b[p]["VALUE"]],
            "N_PROVINCES": len(a)}
    res["PUBLISHED_UNDER_EACH_SCALE"] = pub
    res["DIFFERENCE"] = diffs
    OUT[cname] = res

json.dump(OUT, open(os.path.join(HERE, "rt3_e11_scale_drift.json"), "w"), indent=1, default=str)
print(json.dumps(OUT, indent=1, default=str)[:6000])
