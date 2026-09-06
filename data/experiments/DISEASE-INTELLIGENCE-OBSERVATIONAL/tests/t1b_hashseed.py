#!/usr/bin/env python3
"""T1b — the result must not depend on PYTHONHASHSEED, which randomises set/dict iteration
for str keys between processes. Run once per process by t1_determinism.sh."""
import os, sys, json, hashlib, datetime as dt
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "engine"))
import di_core, di_observe
CASE = os.path.abspath(os.path.join(HERE, "..", "..", "DISEASE-INTELLIGENCE-ITALY",
                                    "CASES", "OLIVO-BACTROCERA-TOSCANA"))
AS_OF = dt.date(2026, 9, 6)
sheet = di_core.load_sheet()
loaded = di_core.load_visits(CASE, sheet, AS_OF)
provs = sorted({v["province"] for v in loaded["visits"] if v["province"]})
cells = [di_observe.cell(loaded["visits"], sheet, p, m, AS_OF)
         for m in ("ACTIVE_INFESTATION_COUNT", "DAMAGING_INFESTATION_COUNT") for p in provs]
blob = json.dumps({"loaded": {k: v for k, v in loaded.items() if k != "visits"},
                   "cells": cells}, sort_keys=True, default=str).encode("utf-8")
print(json.dumps({"PYTHONHASHSEED": os.environ.get("PYTHONHASHSEED"),
                  "sha256": hashlib.sha256(blob).hexdigest()}))
