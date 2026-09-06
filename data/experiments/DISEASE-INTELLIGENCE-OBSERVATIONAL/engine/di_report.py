#!/usr/bin/env python3
"""The full pilot: load -> observe -> analyse -> ADAMA -> human reading. One command."""
import os, sys, json, datetime as dt
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import di_core, di_observe, di_adama, di_render
HERE = os.path.dirname(os.path.abspath(__file__))
CASE = os.path.abspath(os.path.join(HERE, "..", "..", "DISEASE-INTELLIGENCE-ITALY",
                                    "CASES", "OLIVO-BACTROCERA-TOSCANA"))
OUT = os.path.join(HERE, "..", "OUT")


def run(as_of, metric="ACTIVE_INFESTATION_COUNT"):
    sheet = di_core.load_sheet()
    loaded = di_core.load_visits(CASE, sheet, as_of)
    provs = sorted({v["province"] for v in loaded["visits"] if v["province"]})
    adama = di_adama.relevance("Olive", "Olive Fruit Fly")
    cells = []
    for p in provs:
        c = di_observe.cell(loaded["visits"], sheet, p, metric, as_of)
        c["adama"] = adama
        c["attention"] = di_adama.attention_class(c, adama)
        c["provenance"] = {"source": loaded["provenance"][metric]["source_variable"],
                           "api": sheet["SOURCE"]["api"],
                           "source_files": sorted(
                               f["file"] for f in loaded["provenance"][metric]["files"]),
                           "source_hashes": sorted(
                               f["sha256"][:16] for f in loaded["provenance"][metric]["files"]),
                           "denominator_files": sorted(
                               f["file"] for f in
                               loaded["provenance"]["SAMPLE_SIZE / DENOMINATOR"]["files"])}
        cells.append(c)
    return sheet, loaded, cells, adama


if __name__ == "__main__":
    as_of = dt.date.fromisoformat(sys.argv[1]) if len(sys.argv) > 1 else dt.date(2026, 9, 6)
    metric = sys.argv[2] if len(sys.argv) > 2 else "ACTIVE_INFESTATION_COUNT"
    sheet, loaded, cells, adama = run(as_of, metric)
    os.makedirs(OUT, exist_ok=True)
    json.dump({"loaded": {k: v for k, v in loaded.items() if k != "visits"},
               "cells": cells},
              open(os.path.join(OUT, f"report_{metric}_{as_of}.json"), "w", encoding="utf-8"),
              indent=1, default=str)
    print(di_render.render_region(cells, adama))
    print("\n" + "=" * 78 + "\n")
    for p in ("Firenze", "Siena", "Lucca"):
        c = next(x for x in cells if x["province"] == p)
        print(di_render.render_province(c, adama, c["attention"]))
        print("\n" + "-" * 78 + "\n")
