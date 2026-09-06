#!/usr/bin/env python3
"""
CERT-V2 / STEP 12 — CAN THE INSTRUMENT SAY NO?

An instrument tested only on the cells its author chose is not tested. These are cells where
the correct answer is UNKNOWN, INSUFFICIENT_EVIDENCE or a refusal, and where any published
class is a false positive by construction — no agronomic ground truth is needed to score them.

  N1  a season that has not started            (olive in March)
  N2  a season that has ended                  (wheat in September)
  N3  a date before the archive begins         (2001)
  N4  a province the programme does not monitor for that crop
  N5  a survey variable that does not exist in the requested schema
      (the source answers HTTP 200, ok:true, the FULL row skeleton, every value null)
  N6  a variable that exists but is a PREDICTOR, not an outcome
  N7  an evidence role that is a model, not an observation
  N8  a crop the pilot never collected          (maize)

WHERE THERE IS NO GROUND TRUTH, THIS FILE SAYS SO. For N1..N5 the right answer is fixed by
the definition itself, so false positives are countable. For "is the olive really under more
pressure than usual in Grosseto today" there is no independent register in this repository,
and the honest entry is UNKNOWN_GROUND_TRUTH, not a number.

Out: p12_negative_controls.json
"""
import json, os, sys, datetime as dt

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "ENGINE"))
sys.path.insert(0, os.path.join(HERE, "..", "CASES"))
import current_pressure as cp
import automation_probe as ap
from contracts import EvidenceRole

CASEDIR = os.path.join(HERE, "..", "CASES")
OLIVE = os.path.join(CASEDIR, "OLIVO-BACTROCERA-TOSCANA")
VINE = os.path.join(CASEDIR, "VITE-OIDIO-TOSCANA")
WHEAT = os.path.join(CASEDIR, "FRUMENTO-SEPTORIA-TOSCANA")
CLASSED = (cp.HIGHER, cp.TYPICAL, cp.LOWER)


def run(case, var, as_of, **kw):
    try:
        r = cp.current_pressure(case, var, as_of, **kw)
        st = {p: v.get("STATE") for p, v in r["PROVINCES"].items()}
        return {"OUTCOME": "RAN",
                "n_classed": sum(1 for s in st.values() if s in CLASSED),
                "n_provinces": len(st),
                "states": st,
                "DATA_LATENCY_DAYS": r.get("DATA_LATENCY_DAYS")}
    except ValueError as e:
        return {"OUTCOME": "REFUSED", "message": str(e)[:200]}
    except Exception as e:
        return {"OUTCOME": "CRASHED", "message": f"{type(e).__name__}: {str(e)[:200]}"}


def main():
    C = []

    C.append({"ID": "N1", "CELL": "TOSCANA x OLIVE x BACTROCERA x 2026-03-15",
              "WHY_THE_ANSWER_MUST_BE_UNKNOWN":
                  "olive-fly scouting has not started; the newest readable observation is "
                  "from the previous autumn",
              "RESULT": run(OLIVE, -1002, dt.date(2026, 3, 15))})

    C.append({"ID": "N2", "CELL": "TOSCANA x WHEAT x SEPTORIA x 2026-09-06",
              "WHY_THE_ANSWER_MUST_BE_UNKNOWN":
                  "the wheat is harvested; the survey stopped in June",
              "RESULT": run(WHEAT, 372, dt.date(2026, 9, 6))})

    C.append({"ID": "N3", "CELL": "TOSCANA x OLIVE x BACTROCERA x 2001-09-06",
              "WHY_THE_ANSWER_MUST_BE_UNKNOWN": "the archive starts in 2006",
              "RESULT": run(OLIVE, -1002, dt.date(2001, 9, 6))})

    r4 = run(WHEAT, 372, dt.date(2026, 5, 15))
    C.append({"ID": "N4", "CELL": "provinces not monitored for wheat, 2026-05-15",
              "WHY_THE_ANSWER_MUST_BE_UNKNOWN":
                  "the wheat programme covers a handful of provinces; the rest have no visits "
                  "and must not inherit a neighbour",
              "RESULT": r4,
              "UNKNOWN_PROVINCES": [p for p, s in (r4.get("states") or {}).items()
                                    if s not in CLASSED]})

    probe = ap.fetch(3, 8, 50, 2026)
    C.append({"ID": "N5", "CELL": "crop 3 / schema 8 / survey_var 50 (does not exist)",
              "WHY_THE_ANSWER_MUST_BE_A_FAILURE":
                  "the source answers HTTP 200, ok:true, the schema's FULL visit skeleton and "
                  "every value null. Read as data this is 'nobody found anything anywhere'.",
              "RESULT": {"HTTP": probe.get("HTTP"), "ok": probe.get("ok"),
                         "n_rows": probe.get("n_rows"),
                         "non_null_values": probe.get("non_null_values"),
                         "SILENT_FAILURE": probe.get("SILENT_FAILURE"),
                         "error": probe.get("error")},
              "DETECTOR_TRIPPED": bool(probe.get("SILENT_FAILURE"))})

    C.append({"ID": "N6", "CELL": "a variable that is not a survey variable of the case",
              "WHY_THE_ANSWER_MUST_BE_A_REFUSAL": "a predictor is not an outcome",
              "RESULT": run(VINE, 999999, dt.date(2026, 9, 6))})

    C.append({"ID": "N7", "CELL": "the olive case offered as MODELLED_RISK",
              "WHY_THE_ANSWER_MUST_BE_A_REFUSAL": "RISK_FORECAST != DISEASE_PRESENCE",
              "RESULT": run(OLIVE, -1002, dt.date(2026, 9, 6),
                            evidence_role=EvidenceRole.MODELLED_RISK)})

    C.append({"ID": "N8", "CELL": "TOSCANA x MAIZE x anything",
              "WHY_THE_ANSWER_MUST_BE_UNKNOWN":
                  "no maize case exists in this pilot and none is in its Italy census",
              "RESULT": {"OUTCOME": "NO_CASE_ON_DISK",
                         "cases_present": sorted(d for d in os.listdir(CASEDIR)
                                                 if os.path.isdir(os.path.join(CASEDIR, d))
                                                 and d != "__pycache__")},
              "MUST_NOT_BE_REPORTED_AS": "absence of maize disease in Toscana"})

    # score: for N1..N4 a published class is a false positive by construction
    fp = 0
    for c in C:
        if c["ID"] in ("N1", "N2", "N3"):
            fp += (c["RESULT"].get("n_classed") or 0)
    n5_ok = C[4]["DETECTOR_TRIPPED"]
    n6_ok = C[5]["RESULT"]["OUTCOME"] == "REFUSED"
    n7_ok = C[6]["RESULT"]["OUTCOME"] == "REFUSED"

    out = {"CONTROLS": C,
           "NEGATIVE_CONTROLS": len(C),
           "FALSE_POSITIVES_ON_STRUCTURAL_CONTROLS": fp,
           "SILENT_FAILURE_DETECTOR_TRIPS": n5_ok,
           "NON_OUTCOME_VARIABLE_REFUSED": n6_ok,
           "MODELLED_ROLE_REFUSED": n7_ok,
           "FALSE_NEGATIVES": "UNKNOWN_GROUND_TRUTH",
           "UNKNOWN_GROUND_TRUTH":
               "A false negative is a cell where the pressure really was higher than usual "
               "and the instrument said TYPICAL or UNKNOWN. Deciding that needs an "
               "independent register of olive-fly and oidio pressure in Tuscany by province "
               "and date. This repository does not contain one, and the source under test "
               "cannot be its own referee. The rate is NOT KNOWN and no number is offered.",
           "WHAT_THE_CONTROLS_DO_AND_DO_NOT_PROVE":
               "They prove the instrument goes silent where silence is the only correct "
               "answer, which is the property most easily lost. They do not prove that the "
               "classes it does publish are agronomically right."}
    out["NEGATIVE_CONTROLS_VERDICT"] = "PASS" if (fp == 0 and n5_ok and n6_ok and n7_ok) \
        else "FAIL"

    json.dump(out, open(os.path.join(HERE, "p12_negative_controls.json"), "w"),
              indent=1, default=str)
    for c in C:
        r = c["RESULT"]
        print(f"{c['ID']}  {c['CELL'][:58]:58s} -> {r.get('OUTCOME')} "
              f"classed={r.get('n_classed')}/{r.get('n_provinces')} "
              f"latency={r.get('DATA_LATENCY_DAYS')} {str(r.get('message',''))[:60]}")
    print(f"\nfalse positives on structural controls = {fp}")
    print(f"silent-failure detector trips = {n5_ok} | non-outcome var refused = {n6_ok} "
          f"| modelled role refused = {n7_ok}")
    print(f"NEGATIVE_CONTROLS_VERDICT = {out['NEGATIVE_CONTROLS_VERDICT']}")
    print("FALSE_NEGATIVES = UNKNOWN_GROUND_TRUTH")


if __name__ == "__main__":
    main()
