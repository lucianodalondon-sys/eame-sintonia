#!/usr/bin/env python3
"""RT5 -- what the certification measured, and what it did not.

p1_order_experiment.json reports:
    "TODAYS_PUBLISHED_CELLS": "0 of 10 province cells change class with file order on 2026-09-06"
and p1_drift_cause.json reports CELLS_THAT_CHANGE_WITH_FILE_ORDER: 0.

Both count CLASS changes only. Every published cell also carries VALUE, n_sites, n_visits,
BASELINE_MEDIAN, BASELINE_N and PERCENTILE, and ENGINE/answer_sheet.json publishes VALUE and
BASELINE_MEDIAN per province under question 3, "HOW MUCH". This script counts how many of
those published NUMBERS move with file order, and whether the committed answer-sheet value
Grosseto BASELINE_MEDIAN = 0.4633 is reachable.

Cheap: one current_pressure() call per order. Nothing in ENGINE/ or CASES/ is edited.
"""
import json, os, sys, glob as globmod, random, datetime as dt, collections

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "ENGINE")); sys.path.insert(0, os.path.join(ROOT, "CASES"))
import current_pressure as cp

AS = dt.date(2026, 9, 6)
OL = os.path.join(ROOT, "CASES", "OLIVO-BACTROCERA-TOSCANA")
REAL = globmod.glob
FIELDS = ["STATE", "VALUE", "n_sites", "n_visits", "PERCENTILE", "BASELINE_MEDIAN", "BASELINE_N"]

files = sorted(REAL(os.path.join(OL, "RAW", "*_v1_*.json")))
orders = {"native": None, "asc": list(files), "desc": list(reversed(files))}
for s in range(1, 41):
    o = list(files); random.Random(s).shuffle(o); orders[f"seed{s}"] = o

pre = cp.load_rows(OL, -1002)
runs = {}
for label, order in orders.items():
    if order is None:
        cp.glob.glob = REAL
    else:
        cp.glob.glob = (lambda o: (lambda p, **k: list(o) if "_v1_" in p else REAL(p, **k)))(order)
    r = cp.current_pressure(OL, -1002, AS, _pre=pre)
    runs[label] = {p: {f: v.get(f) for f in FIELDS} for p, v in r["PROVINCES"].items()}
    runs[label]["_dropped"] = r["DENOMINATOR_GUARD"].get("dropped_zero_or_unknown_denominator")
cp.glob.glob = REAL

provs = sorted(p for p in runs["native"] if not p.startswith("_"))
moves = {}
for f in FIELDS:
    per = {p: sorted({json.dumps(runs[l][p][f]) for l in runs}) for p in provs}
    moves[f] = {"provinces_whose_value_MOVES_with_file_order": sorted(p for p in provs if len(per[p]) > 1),
                "distinct_values": {p: [json.loads(x) for x in per[p]] for p in provs if len(per[p]) > 1}}

committed_as = json.load(open(os.path.join(ROOT, "ENGINE", "answer_sheet.json"), encoding="utf-8"))
com3 = committed_as["OLIVO-BACTROCERA-TOSCANA"]["3_HOW_MUCH"]
hit = {}
for p, cell in com3.items():
    got_v = {runs[l][p]["VALUE"] for l in runs}
    got_b = {runs[l][p]["BASELINE_MEDIAN"] for l in runs}
    hit[p] = {"committed_VALUE": cell["VALUE"], "VALUE_reachable": cell["VALUE"] in got_v,
              "committed_BASELINE_MEDIAN": cell["BASELINE_MEDIAN"],
              "BASELINE_MEDIAN_reachable": cell["BASELINE_MEDIAN"] in got_b,
              "values_seen": sorted(x for x in got_b if x is not None)}

out = {"N_ORDERS": len(orders), "orders": sorted(orders),
       "dropped_rows_by_order": sorted({runs[l]["_dropped"] for l in runs}),
       "FIELD_MOVEMENT": moves,
       "CAN_FILE_ORDER_REACH_THE_COMMITTED_ANSWER_SHEET_NUMBERS": hit,
       "n_published_cells": len(provs)}
json.dump(out, open(os.path.join(HERE, "rt5_p9_published_values.json"), "w"), indent=1, default=str)

print(f"{len(orders)} file orders, {len(provs)} province cells")
print("rows dropped by the guard, across orders:", out["dropped_rows_by_order"])
for f in FIELDS:
    m = moves[f]["provinces_whose_value_MOVES_with_file_order"]
    print(f"  {f:16s} moves in {len(m)}/{len(provs)} cells  {m}")
print("\ncommitted answer_sheet.json numbers, reachable by file order?")
for p, h in hit.items():
    print(f"  {p:14s} VALUE {h['committed_VALUE']} -> {h['VALUE_reachable']:5} | "
          f"BASELINE_MEDIAN {h['committed_BASELINE_MEDIAN']} -> {h['BASELINE_MEDIAN_reachable']:5} "
          f"| seen {h['values_seen']}")
print("wrote rt5_p9_published_values.json")
