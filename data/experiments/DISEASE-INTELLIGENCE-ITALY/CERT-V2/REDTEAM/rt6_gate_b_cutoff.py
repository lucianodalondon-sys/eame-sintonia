#!/usr/bin/env python3
"""
RT6 / B — is gate B able to detect the removal of its own cutoff?

Gate B's predicate (ENGINE/gates.py lines 63-79) compares two objects:
    honest = live[name]                                   current_pressure(..., as_of)
    leaked = cp.current_pressure(d, v, as_of + 30d, _pre=pre)
Both go through cp._window_value. M03 patches cp._window_value. So under M03 BOTH sides of the
comparison are mutated and the difference that survives is the difference between two window
STARTS (lo), not the presence or absence of an upper bound.

This script measures, without any gate involved:
  1. how many archived rows are dated after as_of, before and after the denominator guard;
  2. what the published cells look like with the cutoff and with the cutoff removed;
  3. gate B's own load_bearing counter, recomputed under the M03 patch.

Out: rt6_gate_b_cutoff.json
"""
import os, sys, json, datetime as dt, collections

HERE = os.path.dirname(os.path.abspath(__file__))
CERT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(CERT, "..", "ENGINE"))
sys.path.insert(0, os.path.join(CERT, "..", "CASES"))
import current_pressure as cp

AS_OF = dt.date(2026, 9, 6)
CASES = [("OLIVO x BACTROCERA x TOSCANA", os.path.join(CERT, "..", "CASES",
                                                       "OLIVO-BACTROCERA-TOSCANA"), -1002),
         ("VITE x OIDIO x TOSCANA", os.path.join(CERT, "..", "CASES",
                                                 "VITE-OIDIO-TOSCANA"), 39)]

out = {"AS_OF": AS_OF.isoformat(), "WINDOW_DAYS": cp.WINDOW_DAYS, "CASES": {}}
w0 = AS_OF - dt.timedelta(days=cp.WINDOW_DAYS - 1)

honest, mutated = {}, {}
for name, d, v in CASES:
    pre = cp.load_rows(d, v)
    rows = pre[0]
    after = [r for r in rows if r["_d"] > AS_OF]
    in_win = [r for r in after if w0 <= r["_d"]]
    readable = [r for r in in_win
                if cp.read_value(r, pre[1], pre[2]["VALUE_MODE"]) is not None]
    # what the denominator guard does to those same rows
    idx = json.load(open(os.path.join(d, "collection_index.json")))
    dv = idx.get("DENOMINATOR_VAR")
    if dv is not None:
        kept, _ = cp.denominator_guard(rows, d, dv)
        kept_ids = {id(r) for r in kept}
        survive_guard = [r for r in readable if id(r) in kept_ids]
    else:
        survive_guard = readable
    honest[name] = cp.current_pressure(d, v, AS_OF, _pre=pre)
    out["CASES"][name] = {
        "n_rows_total": len(rows),
        "n_rows_dated_after_as_of": len(after),
        "n_of_those_inside_the_28d_window": len(in_win),
        "n_of_those_with_a_READABLE_value": len(readable),
        "n_of_those_that_survive_the_denominator_guard": len(survive_guard),
        "dates_after_as_of": sorted({r["_d"].isoformat() for r in after}),
        "provinces_of_those_rows": sorted({r.get("nome_area") for r in in_win if r.get("nome_area")}),
    }

# ── now apply M03 exactly as p3_mutation.py does, in this same process ──────────────
_real_window = cp._window_value
cp._window_value = lambda rows, scale, lo, hi, mode="ORDINAL": \
    _real_window(rows, scale, lo, dt.date(2100, 1, 1), mode)

for name, d, v in CASES:
    pre = cp.load_rows(d, v)
    mutated[name] = cp.current_pressure(d, v, AS_OF, _pre=pre)

changed = {}
for name, _, _ in CASES:
    h, m = honest[name]["PROVINCES"], mutated[name]["PROVINCES"]
    ch = [{"PROVINCE": p, "STATE_WITH_CUTOFF": h[p].get("STATE"),
           "STATE_WITHOUT_CUTOFF": m.get(p, {}).get("STATE"),
           "VALUE_WITH": h[p].get("VALUE"), "VALUE_WITHOUT": m.get(p, {}).get("VALUE"),
           "n_visits_WITH": h[p].get("n_visits"), "n_visits_WITHOUT": m.get(p, {}).get("n_visits")}
          for p in h]
    changed[name] = {
        "n_province_cells": len(h),
        "n_cells_whose_CLASS_changes_when_the_cutoff_is_removed":
            sum(1 for c in ch if c["STATE_WITH_CUTOFF"] != c["STATE_WITHOUT_CUTOFF"]),
        "n_cells_whose_VALUE_changes":
            sum(1 for c in ch if c["VALUE_WITH"] != c["VALUE_WITHOUT"]),
        "n_cells_whose_n_visits_changes":
            sum(1 for c in ch if c["n_visits_WITH"] != c["n_visits_WITHOUT"]),
        "CELLS": ch}
out["CUTOFF_REMOVED_EFFECT_ON_TODAYS_PUBLISHED_CELLS"] = changed

# ── gate B's own counter, recomputed with the mutation live ────────────────────────
fut = used_fut = load_bearing = 0
for name, d, v in CASES:
    pre = cp.load_rows(d, v)
    after = [r for r in pre[0] if r["_d"] > AS_OF]
    fut += len(after)
    used_fut += sum(1 for r in after if w0 <= r["_d"])
    leaked = cp.current_pressure(d, v, AS_OF + dt.timedelta(days=30), _pre=pre)
    hon = mutated[name]                       # what live[] is under the mutation
    load_bearing += sum(1 for p in hon["PROVINCES"]
                        if hon["PROVINCES"][p].get("STATE")
                        != leaked["PROVINCES"].get(p, {}).get("STATE"))
labels_ok = all(r["CUTOFF_LABEL"] == "NOWCAST" for r in mutated.values())
out["GATE_B_PREDICATE_RECOMPUTED_UNDER_M03"] = {
    "fut": fut, "used_fut": used_fut, "load_bearing": load_bearing,
    "all_labels_NOWCAST": labels_ok,
    "VERDICT_THE_PREDICATE_RETURNS":
        "PASS" if (fut > 0 and used_fut > 0 and load_bearing > 0 and labels_ok) else "FAIL",
    "WHY": "load_bearing counts the difference between two runs that are BOTH mutated; the "
           "surviving difference is the 30-day shift of the window START (lo), which M03 does "
           "not touch. The upper bound can be deleted and this counter never reaches 0."}

# ── does contracts.Cutoff.assert_no_day_leakage ever run? ─────────────────────────
src = open(os.path.join(CERT, "..", "ENGINE", "current_pressure.py"), encoding="utf-8").read()
out["DAY_LEAKAGE_GUARD"] = {
    "DEFINED_IN": "ENGINE/contracts.py Cutoff.assert_no_day_leakage",
    "CALLED_IN_current_pressure": "assert_no_day_leakage" in src,
    "Cutoff_USED_ONLY_FOR": "label()" if ".label()" in src else "unknown"}

json.dump(out, open(os.path.join(HERE, "rt6_gate_b_cutoff.json"), "w"), indent=1, default=str)
print(json.dumps({k: v for k, v in out.items()
                  if k != "CUTOFF_REMOVED_EFFECT_ON_TODAYS_PUBLISHED_CELLS"}, indent=1)[:2500])
for n, c in changed.items():
    print(f"\n{n}: class changes {c['n_cells_whose_CLASS_changes_when_the_cutoff_is_removed']}"
          f"/{c['n_province_cells']}  value changes {c['n_cells_whose_VALUE_changes']}"
          f"  n_visits changes {c['n_cells_whose_n_visits_changes']}")
    for x in c["CELLS"]:
        if x["STATE_WITH_CUTOFF"] != x["STATE_WITHOUT_CUTOFF"] or \
           x["VALUE_WITH"] != x["VALUE_WITHOUT"]:
            print("   ", x)
