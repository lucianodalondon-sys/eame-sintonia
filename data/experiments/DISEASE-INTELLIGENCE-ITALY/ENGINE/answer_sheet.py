#!/usr/bin/env python3
"""
FASE 3 — VALUE WITHOUT FORECAST.

The eight questions, answered by computation and not by prose. If the tool cannot emit these
eight answers from the data alone, it has no value even before the forecast question is asked.
Every answer that cannot be computed comes back as NOT_KNOWN, never as an empty string and
never as zero.
"""
import sys, os, json, datetime as dt, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import current_pressure as cp
from statistics import mean

STAB_MIN, COV_MIN = 0.80, 0.60          # publish a CLASS only above these; declared, post-hoc


def answer_sheet(case_dir, var_id, as_of, issue, crop, region, metric="INCIDENCE"):
    pre = cp.load_rows(case_dir, var_id)
    live = cp.current_pressure(case_dir, var_id, as_of, metric, _pre=pre)
    prev = cp.current_pressure(case_dir, var_id, as_of - dt.timedelta(days=cp.WINDOW_DAYS),
                               metric, _pre=pre)
    sens = cp.sensitivity(case_dir, var_id, as_of, metric)
    hind = cp.hindcast(case_dir, var_id, as_of.month, as_of.day, range(2006, as_of.year + 1), metric)

    P = live["PROVINCES"]
    known = {p: v for p, v in P.items() if v.get("VALUE") is not None}
    classed = {p: v for p, v in P.items() if v.get("STATE") in (cp.HIGHER, cp.TYPICAL, cp.LOWER)}
    cov = {p: sum(1 for y in hind if hind[y].get(p) in (cp.HIGHER, cp.TYPICAL, cp.LOWER)) / max(len(hind), 1)
           for p in P}
    publishable = {p for p in classed
                   if (sens["PER_PROVINCE"].get(p, {}).get("AGREEMENT") or 0) >= STAB_MIN
                   and cov.get(p, 0) >= COV_MIN}

    def st(p): return P[p]["STATE"]
    a = collections.OrderedDict()

    # CORRECTED 2026-09-06. This sentence used to read "scouts recorded <issue> on N visits",
    # which states that N visits FOUND the issue. N is the number of visits SCORED for it, and
    # for four of those provinces the incidence is 0.000 — the sentence contradicted the table
    # directly beneath it. Scored, present and sites-with-it are now three separate numbers.
    n_scored = sum(v["n_visits"] for v in known.values())
    n_sites_tot = sum(v["n_sites"] for v in known.values())
    n_sites_pos = sum(round(v["VALUE"] * v["n_sites"]) for v in known.values())
    a["1_WHAT_HAPPENED"] = {
        "STATEMENT": (f"In the 28 days to {as_of}, official scouts scored {n_scored} visits for "
                      f"{issue} across {n_sites_tot} monitored {crop} sites in {region}. "
                      f"{n_sites_pos} of those sites had it present; {n_sites_tot - n_sites_pos} "
                      f"did not." if known else "NOT_KNOWN"),
        "n_visits_scored": n_scored or None, "n_sites_monitored": n_sites_tot or None,
        "n_sites_with_issue_present": n_sites_pos if known else None,
        "NOTE": "a scored visit is not a detection; the two were conflated until 2026-09-06"}

    a["2_WHERE"] = {"PROVINCES_WITH_DATA": sorted(known),
                    "PROVINCES_WITHOUT_DATA": sorted(p for p in P if p not in known),
                    "REGIONAL_UNIT": "province", "NEVER": "no national figure is produced"}

    a["3_HOW_MUCH"] = {p: {"VALUE": v["VALUE"], "UNITS": ("share of monitored sites with the issue present"
                                                          if metric == "INCIDENCE" else metric),
                           "n_sites": v["n_sites"], "BASELINE_MEDIAN": v.get("BASELINE_MEDIAN")}
                       for p, v in sorted(known.items())}

    a["4_HOW_IS_IT_EVOLVING"] = {
        "WITHIN_SEASON": {p: {"NOW": known[p]["VALUE"],
                              "ONE_WINDOW_AGO": prev["PROVINCES"].get(p, {}).get("VALUE"),
                              "DIRECTION": _dir(known[p]["VALUE"], prev["PROVINCES"].get(p, {}).get("VALUE"))}
                          for p in sorted(known)},
        "ACROSS_SEASONS": "EVOLUTION as season-vs-season ranking = PROVED; "
                          "EVOLUTION as a multi-year trend = TREND_NOT_PROVED (confounded with "
                          "monitoring era, see CHECKPOINT trend test)"}

    a["5_PRESSURE_HIGHER_OR_LOWER"] = {
        "PUBLISHED": {p: st(p) for p in sorted(publishable)},
        "WITHHELD_LOW_CONFIDENCE": {p: {"STATE_WOULD_BE": st(p),
                                        "LABEL_STABILITY": sens["PER_PROVINCE"].get(p, {}).get("AGREEMENT"),
                                        "HISTORICAL_COVERAGE": round(cov.get(p, 0), 3)}
                                    for p in sorted(set(classed) - publishable)},
        "UNKNOWN": {p: st(p) for p in sorted(P) if p not in classed},
        "AGAINST": f"the same 28-day calendar window in prior seasons of the same province "
                   f"(min {cp.MIN_BASE} usable seasons)"}

    a["6_WHAT_CHANGED"] = {p: {"STATE_NOW": st(p),
                               "STATE_LAST_SEASON_SAME_DATE": hind.get(as_of.year - 1, {}).get(p),
                               "CHANGED": st(p) != hind.get(as_of.year - 1, {}).get(p)}
                           for p in sorted(P)}

    a["7_SOURCE"] = {"URL": live["SOURCE"], "EVIDENCE_ROLE": live["EVIDENCE_ROLE"],
                     "CUTOFF_LABEL": live["CUTOFF_LABEL"],
                     "DATA_LATENCY_DAYS": live["DATA_LATENCY_DAYS"],
                     "RAW_FILES_SHA256": len(pre[2]["hashes"]),
                     "EMPTY_RESPONSES_RECORDED": pre[2]["empty_responses"]}

    a["8_WHAT_WE_DO_NOT_KNOW"] = {
        "PROVINCES_NEVER_CLASSIFIABLE": sorted(p for p in P if cov.get(p, 0) == 0),
        "PROVINCES_LOW_CONFIDENCE": sorted(set(classed) - publishable),
        "NOT_PROVED": ["EARLY_WARNING", "PRE_SEASON_OUTLOOK", "NEXT_SEASON_OUTLOOK",
                       "MULTI_YEAR_TREND", "ANY_STATEMENT_ABOUT_UNVISITED_FIELDS",
                       "ADAMA_PRODUCT_RELATION"],
        "PARAMETER_DEPENDENCE": {"MEAN_LABEL_STABILITY": sens["MEAN_AGREEMENT"],
                                 "GRID_SIZE": sens["GRID_SIZE"]},
        "SAMPLING": "the panel is the set of monitored fields, which is not a random sample of "
                    "the region's area; the figure describes the monitored network, not the region"}
    return a


def _dir(now, then):
    if now is None or then is None: return "NOT_KNOWN"
    if now > then: return "RISING"
    if now < then: return "FALLING"
    return "FLAT"


if __name__ == "__main__":
    CASES = [("../CASES/OLIVO-BACTROCERA-TOSCANA", -1002, "damaging olive-fly infestation",
              "olive", "Toscana"),
             ("../CASES/VITE-OIDIO-TOSCANA", 39, "powdery mildew on leaves", "vine", "Toscana")]
    as_of = dt.date.fromisoformat(sys.argv[1]) if len(sys.argv) > 1 else dt.date(2026, 9, 6)
    out = {}
    for d, v, issue, crop, region in CASES:
        a = answer_sheet(d, v, as_of, issue, crop, region)
        out[os.path.basename(d)] = a
        print(f"\n{'='*78}\n{os.path.basename(d)}   as_of {as_of}")
        print(" 1 WHAT HAPPENED :", a["1_WHAT_HAPPENED"]["STATEMENT"])
        print(" 2 WHERE         :", len(a["2_WHERE"]["PROVINCES_WITH_DATA"]), "provinces with data;",
              "no data:", a["2_WHERE"]["PROVINCES_WITHOUT_DATA"])
        print(" 3 HOW MUCH      :", ", ".join(f"{p} {x['VALUE']:.3f} (usual {x['BASELINE_MEDIAN']})"
              for p, x in list(a["3_HOW_MUCH"].items())[:4]), "...")
        print(" 4 EVOLVING      :", collections.Counter(x["DIRECTION"] for x in
              a["4_HOW_IS_IT_EVOLVING"]["WITHIN_SEASON"].values()))
        print(" 5 PRESSURE      : PUBLISHED", a["5_PRESSURE_HIGHER_OR_LOWER"]["PUBLISHED"])
        print("                   WITHHELD", list(a["5_PRESSURE_HIGHER_OR_LOWER"]["WITHHELD_LOW_CONFIDENCE"]))
        print("                   UNKNOWN ", a["5_PRESSURE_HIGHER_OR_LOWER"]["UNKNOWN"])
        print(" 6 WHAT CHANGED  :", sum(1 for x in a["6_WHAT_CHANGED"].values() if x["CHANGED"]),
              "of", len(a["6_WHAT_CHANGED"]), "provinces differ from the same date last season")
        print(" 7 SOURCE        :", a["7_SOURCE"]["EVIDENCE_ROLE"], a["7_SOURCE"]["CUTOFF_LABEL"],
              f"latency {a['7_SOURCE']['DATA_LATENCY_DAYS']}d,",
              a["7_SOURCE"]["RAW_FILES_SHA256"], "raw files hash-checked")
        print(" 8 DO NOT KNOW   : never-classifiable", a["8_WHAT_WE_DO_NOT_KNOW"]["PROVINCES_NEVER_CLASSIFIABLE"],
              "| low-confidence", a["8_WHAT_WE_DO_NOT_KNOW"]["PROVINCES_LOW_CONFIDENCE"])
    json.dump(out, open("answer_sheet.json", "w"), indent=1, default=str)
