#!/usr/bin/env python3
"""
RT6 — DO THE CERTIFICATION'S OWN MUTATIONS DESTROY ANYTHING?

Three of p3_mutation.py's recipes were already withdrawn as no-ops (m07 v1, m07 v2, m10 v1) and
say so in their docstrings. A mutation that changes nothing produces a meaningless SURVIVED /
UNDETECTED. This script replays each recipe whose recorded outcome was "no gate moved"
(M20, M22, M23, M26, M27) and measures the diff it makes to the PUBLISHED output on the
certified date, field by field. A recipe with an empty diff is a no-op.

Out: rt6_mutation_validity.json
"""
import os, sys, json, datetime as dt, glob as globmod, copy

HERE = os.path.dirname(os.path.abspath(__file__))
CERT = os.path.dirname(HERE)
CASEDIR = os.path.join(CERT, "..", "CASES")
sys.path.insert(0, os.path.join(CERT, "..", "ENGINE"))
sys.path.insert(0, CASEDIR)
import current_pressure as cp

AS_OF = dt.date(2026, 9, 6)
CASES = [("OLIVO", os.path.join(CASEDIR, "OLIVO-BACTROCERA-TOSCANA"), -1002),
         ("VITE", os.path.join(CASEDIR, "VITE-OIDIO-TOSCANA"), 39)]

REAL = {"load_rows": cp.load_rows, "current_pressure": cp.current_pressure,
        "read_value": cp.read_value, "glob": globmod.glob}


def restore():
    cp.load_rows = REAL["load_rows"]
    cp.current_pressure = REAL["current_pressure"]
    cp.read_value = REAL["read_value"]
    cp.glob.glob = REAL["glob"]


def run():
    return {n: cp.current_pressure(d, v, AS_OF) for n, d, v in CASES}


restore()
base = copy.deepcopy(run())


def m20():
    real = REAL["load_rows"]
    def p(case_dir, var_id):
        rows, scale, meta = real(case_dir, var_id)
        idx = json.load(open(os.path.join(case_dir, "collection_index.json")))
        ids = [str(c.get("id_survey_code")) for c in (idx.get("codes") or [])]
        if ids:
            for i, r in enumerate(rows):
                r["val"] = ids[i % len(ids)]
        return rows, scale, meta
    cp.load_rows = p


def m22():
    real = REAL["load_rows"]
    def p(case_dir, var_id):
        rows, scale, meta = real(case_dir, var_id)
        for r in rows:
            r["_d"] = r["_d"] + dt.timedelta(days=365)
        return rows, scale, meta
    cp.load_rows = p


def m23():
    real = REAL["load_rows"]
    def p(case_dir, var_id):
        rows, scale, meta = real(case_dir, var_id)
        meta["api"] = None
        meta["hashes"] = {}
        return rows, scale, meta
    cp.load_rows = p


def m24():
    real = REAL["read_value"]
    cp.read_value = lambda r, scale, mode: (
        None if real(r, scale, mode) is None else
        (100.0 - real(r, scale, mode) if real(r, scale, mode) > 1
         else 1.0 - real(r, scale, mode)))


def m26():
    real = REAL["current_pressure"]
    def p(*a, **k):
        r = real(*a, **k)
        for _, v in r["PROVINCES"].items():
            if isinstance(v, dict) and "EVIDENCE" in v:
                v["EVIDENCE"] = {}
        return r
    cp.current_pressure = p


def m27():
    real = REAL["glob"]
    cp.glob.glob = lambda p, **k: sorted(real(p, **k), reverse=True)


RECIPES = {"M20_values_replaced_by_code_ids": m20,
           "M22_dates_shifted_one_year": m22,
           "M23_source_url_and_hashes_removed": m23,
           "M24_signal_inverted": m24,
           "M26_evidence_link_broken": m26,
           "M27_file_order_fixed_but_reversed": m27}

out = {"AS_OF": AS_OF.isoformat(),
       "BASELINE_STATES": {n: {p: v.get("STATE") for p, v in r["PROVINCES"].items()}
                           for n, r in base.items()}}

for mid, recipe in RECIPES.items():
    restore()
    try:
        recipe()
        got = run()
        rep = {}
        for n, _, _ in CASES:
            B, G = base[n]["PROVINCES"], got[n]["PROVINCES"]
            keys = ("STATE", "VALUE", "n_sites", "n_visits", "BASELINE_N", "BASELINE_MEDIAN",
                    "PERCENTILE", "EVIDENCE")
            rep[n] = {"n_cells": len(B),
                      "cells_with_a_different_STATE":
                          sum(1 for p in B if B[p].get("STATE") != G.get(p, {}).get("STATE")),
                      "cells_with_ANY_different_field":
                          sum(1 for p in B
                              if any(B[p].get(k) != G.get(p, {}).get(k) for k in keys)),
                      "top_level_SOURCE_changed": base[n]["SOURCE"] != got[n]["SOURCE"],
                      "top_level_LATENCY": [base[n]["DATA_LATENCY_DAYS"],
                                            got[n]["DATA_LATENCY_DAYS"]],
                      "whole_case_json_identical":
                          json.dumps(base[n], sort_keys=True, default=str)
                          == json.dumps(got[n], sort_keys=True, default=str)}
        total_changed = sum(v["cells_with_ANY_different_field"] for v in rep.values())
        rep["IS_A_NO_OP"] = all(v["whole_case_json_identical"] for v in rep.values())
        rep["n_of_20_published_cells_touched"] = total_changed
        out[mid] = rep
    except Exception as e:
        out[mid] = {"RAISED": f"{type(e).__name__}: {e}"}
restore()

json.dump(out, open(os.path.join(HERE, "rt6_mutation_validity.json"), "w"),
          indent=1, default=str)
print(json.dumps(out, indent=1, default=str))
