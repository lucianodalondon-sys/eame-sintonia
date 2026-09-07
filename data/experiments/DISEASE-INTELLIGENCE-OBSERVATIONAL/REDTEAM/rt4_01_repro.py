#!/usr/bin/env python3
"""RT4-01  Independent reproduction of the determinism hash, written from the claim, not
from the tool's test.

The tool publishes sha256 61ac20d6... over
    json.dumps({"loaded": <loaded minus visits>, "cells": <cells>}, sort_keys=True,
               default=str).encode("utf-8")
for AS_OF 2026-09-06 and METRICS [ACTIVE, DAMAGING], provinces sorted.

I reconstruct that payload here from the engine's public API only, then ALSO hash the
things the tool's own test never hashed:
    EXT_REPORT  the full di_report.run() output, which carries the ADAMA block and the
                per-cell provenance the tool's test drops
    EXT_RENDER  the rendered human text that is what a person actually reads

Prints JSON on stdout so it can be run under different PYTHONHASHSEED / locale / cwd.
"""
import os, sys, json, hashlib, datetime as dt

HERE = os.path.dirname(os.path.abspath(__file__))
ENGINE = os.path.join(HERE, "..", "engine")
sys.path.insert(0, ENGINE)
import di_core, di_observe, di_adama, di_render, di_report

CASE = os.path.abspath(os.path.join(HERE, "..", "..", "DISEASE-INTELLIGENCE-ITALY",
                                    "CASES", "OLIVO-BACTROCERA-TOSCANA"))
AS_OF = dt.date(2026, 9, 6)


def sha(o):
    return hashlib.sha256(json.dumps(o, sort_keys=True, default=str).encode("utf-8")).hexdigest()


def core_hash():
    sheet = di_core.load_sheet()
    loaded = di_core.load_visits(CASE, sheet, AS_OF)
    provs = sorted({v["province"] for v in loaded["visits"] if v["province"]})
    cells = [di_observe.cell(loaded["visits"], sheet, p, m, AS_OF)
             for m in ("ACTIVE_INFESTATION_COUNT", "DAMAGING_INFESTATION_COUNT")
             for p in provs]
    return sha({"loaded": {k: v for k, v in loaded.items() if k != "visits"},
                "cells": cells}), loaded, cells


def ext_hashes():
    sheet, loaded, cells, adama = di_report.run(AS_OF, "ACTIVE_INFESTATION_COUNT")
    rep = sha({"loaded": {k: v for k, v in loaded.items() if k != "visits"}, "cells": cells})
    txt = di_render.render_region(cells, adama)
    for c in cells:
        txt += "\n" + di_render.render_province(c, adama, c["attention"])
    return rep, hashlib.sha256(txt.encode("utf-8")).hexdigest(), adama["relevance"]


if __name__ == "__main__":
    h, loaded, cells = core_hash()
    rep, ren, rel = ext_hashes()
    print(json.dumps({
        "PYTHONHASHSEED": os.environ.get("PYTHONHASHSEED"),
        "PY": sys.version.split()[0],
        "CWD": os.getcwd(),
        "LANG": os.environ.get("LANG"), "LC_ALL": os.environ.get("LC_ALL"),
        "CORE_HASH_the_one_the_tool_publishes": h,
        "EXT_REPORT_HASH_with_adama_and_provenance": rep,
        "EXT_RENDERED_TEXT_HASH": ren,
        "ADAMA_RELEVANCE": rel,
        "n_visits": loaded["n_visits"],
        "n_usable": loaded["n_visits_usable_for_rates"],
        "n_provinces": len({c["province"] for c in cells}),
    }, sort_keys=True))
