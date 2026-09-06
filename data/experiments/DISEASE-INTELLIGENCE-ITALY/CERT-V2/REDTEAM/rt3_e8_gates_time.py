#!/usr/bin/env python3
"""RT3-E8. Drive the REAL ENGINE/gates.py evaluate() -- not a transcription --

  RUN 1  default as_of (the hardcoded literal dt.date(2026, 9, 6))
  RUN 2  as_of + 30 days, archive unchanged: what does gate H's 'latency <= 21' do as
         real time passes?
  RUN 3  default as_of, but with current_pressure._window_value patched so the UPPER
         bound is removed. A gate B that 'can detect its removal' must go FAIL.

Nothing under ENGINE/ or CASES/ is modified; the patch is applied to the imported module
object at runtime and restored. Results are written under REDTEAM/.
"""
import sys, os, json, datetime as dt, traceback

HERE = os.path.dirname(os.path.abspath(__file__))
ENG = os.path.abspath(os.path.join(HERE, "..", "..", "ENGINE"))
sys.path.insert(0, ENG)
# gates.py's CASES list uses paths relative to the CWD ("../CASES/..."), so evaluate() only
# runs with CWD == ENGINE/. We call evaluate() directly, never gates.py __main__, so nothing
# writes over ENGINE/gates.json.
os.chdir(ENG)
import current_pressure as cp
import gates

ORIG = cp._window_value
FAR = dt.date(9999, 12, 31)
OUT = {}


def slim(r):
    return {"AS_OF": r["AS_OF"], "PASS": r["PASS"], "FAIL": r["FAIL"],
            "NOT_TESTABLE": r["NOT_TESTABLE"],
            "DESERVES_FUTURE_INTEGRATION": r["DESERVES_FUTURE_INTEGRATION"],
            "VERDICTS": {k: v["VERDICT"] for k, v in r["GATES"].items()},
            "B_EVIDENCE": r["GATES"]["B_NOT_SOLD_AS_FORECAST"]["EVIDENCE"],
            "H_EVIDENCE": r["GATES"]["H_REFRESHABLE_WITHOUT_RESEARCH"]["EVIDENCE"][-420:]}


import inspect
OUT["GATES_DEFAULT_AS_OF_SIGNATURE"] = str(inspect.signature(gates.evaluate))

for label, as_of, patch in (("RUN1_default_as_of", dt.date(2026, 9, 6), False),
                            ("RUN2_as_of_plus_30d", dt.date(2026, 10, 6), False),
                            ("RUN3_upper_cutoff_REMOVED", dt.date(2026, 9, 6), True)):
    if patch:
        cp._window_value = lambda rows, scale, lo, hi, mode="ORDINAL": ORIG(rows, scale, lo, FAR, mode)
    try:
        r = gates.evaluate(as_of)
        OUT[label] = slim(r)
    except Exception:
        OUT[label] = {"RAISED": traceback.format_exc()[-1200:]}
    finally:
        cp._window_value = ORIG
    print("=" * 78)
    print(label, as_of)
    print(json.dumps(OUT[label], indent=1)[:2600])

json.dump(OUT, open(os.path.join(HERE, "rt3_e8_gates_time.json"), "w"), indent=1, default=str)
