#!/usr/bin/env python3
"""RT5 / PROVENANCE 4 -- committed artefacts vs the code committed alongside them.

S1  ENGINE/answer_sheet.json was last written at 5c90455. ENGINE/current_pressure.py changed
    twice afterwards (e44515d, a4d19dd), gaining MIN_POSITIVE_SITES -- an effect-size floor
    that rewrites HIGHER into TYPICAL -- and assert_scale_decodes. Regenerate the artefact
    with the code that is committed beside it TODAY and diff. Nothing in ENGINE/ is written:
    answer_sheet() is called directly and the result is compared in memory.

S2  Is the drift CODE-dependent or MACHINE-dependent? gates.json says F_OLIVO=0.918 and
    G_OLIVO=0.424 both at 193689c (before the floor) and at a4d19dd (after it). If the floor
    moves the olive walk-forward at all, those two runs cannot both be honest full re-runs of
    the same frozen data. Measure the floor's effect directly.

S3  ENGINE/gates_final.txt was last written at e44515d; gates.py changed at 5cf2e48 and
    a4d19dd. Compare its recorded verdicts with the committed gates.json.
"""
import json, os, sys, datetime as dt, collections, difflib

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, "..", ".."))
ENGINE, CASEDIR = os.path.join(ROOT, "ENGINE"), os.path.join(ROOT, "CASES")
sys.path.insert(0, ENGINE); sys.path.insert(0, CASEDIR)
import current_pressure as cp
from answer_sheet import answer_sheet

AS_OF = dt.date(2026, 9, 6)
R = {}

# ================= S1 : answer_sheet.json ==============================================
SPEC = [("OLIVO-BACTROCERA-TOSCANA", -1002, "damaging olive-fly infestation", "olive", "Toscana"),
        ("VITE-OIDIO-TOSCANA", 39, "powdery mildew on leaves", "vine", "Toscana")]
fresh = {}
for base, v, issue, crop, region in SPEC:
    fresh[base] = answer_sheet(os.path.join(CASEDIR, base), v, AS_OF, issue, crop, region)
fresh_txt = json.dumps(fresh, indent=1, default=str)
committed_txt = open(os.path.join(ENGINE, "answer_sheet.json"), encoding="utf-8").read()
committed = json.loads(committed_txt)

def flat(o, p=""):
    if isinstance(o, dict):
        for k, val in o.items(): yield from flat(val, f"{p}.{k}")
    elif isinstance(o, list):
        yield p, json.dumps(o, default=str)
    else:
        yield p, o

fa, fb = dict(flat(json.loads(fresh_txt))), dict(flat(committed))
keys = sorted(set(fa) | set(fb))
diffs = [(k, fb.get(k, "<ABSENT>"), fa.get(k, "<ABSENT>")) for k in keys if fa.get(k) != fb.get(k)]
R["S1_answer_sheet_json"] = {
    "BYTE_IDENTICAL": fresh_txt == committed_txt,
    "leaf_fields_compared": len(keys),
    "leaf_fields_that_DIFFER": len(diffs),
    "committed_at": "5c90455 (current_pressure.py changed at e44515d and a4d19dd afterwards)",
    "DIFFS": [{"field": k, "COMMITTED": c, "RECOMPUTED_TODAY": n} for k, c, n in diffs[:40]],
    "PUBLISHED_STATES_committed": committed["OLIVO-BACTROCERA-TOSCANA"]["5_PRESSURE_HIGHER_OR_LOWER"]["PUBLISHED"],
    "PUBLISHED_STATES_recomputed": fresh["OLIVO-BACTROCERA-TOSCANA"]["5_PRESSURE_HIGHER_OR_LOWER"]["PUBLISHED"],
}

# ================= S2 : does the effect-size floor move the walk-forward? ==============
H, T, L = cp.HIGHER, cp.TYPICAL, cp.LOWER
_real = cp.current_pressure

def forced(floor):
    def f(case_dir, var_id, as_of, metric="INCIDENCE", *a, **kw):
        kw["min_positive_sites"] = floor
        return _real(case_dir, var_id, as_of, metric, *a, **kw)
    return f

s2 = {}
for base, var in (("OLIVO-BACTROCERA-TOSCANA", -1002), ("VITE-OIDIO-TOSCANA", 39)):
    d = os.path.join(CASEDIR, base)
    per = {}
    for label, floor in (("floor_0_pre_a4d19dd", 0), ("floor_5_as_shipped", cp.MIN_POSITIVE_SITES)):
        cp.current_pressure = forced(floor)
        h = cp.hindcast(d, var, 9, 6, range(2007, 2027))
        flatc = [s for y in h.values() for s in y.values() if s in (H, T, L)]
        c = collections.Counter(flatc)
        per[label] = {"G_dominant_share": round(max(c[H], c[T], c[L]) / len(flatc), 3) if flatc else None,
                      "n_classified": len(flatc), "counts": {"H": c[H], "T": c[T], "L": c[L]},
                      "grid": {str(y): dict(v) for y, v in sorted(h.items())}}
        cp.current_pressure = _real
    a, b = per["floor_0_pre_a4d19dd"], per["floor_5_as_shipped"]
    changed = sum(1 for y in a["grid"] for p in a["grid"][y]
                  if a["grid"][y][p] != b["grid"].get(y, {}).get(p))
    s2[base] = {"G_without_the_floor": a["G_dominant_share"], "G_with_the_floor": b["G_dominant_share"],
                "class_counts_without": a["counts"], "class_counts_with": b["counts"],
                "walk_forward_cells_the_floor_CHANGES": changed,
                "n_cells": sum(len(v) for v in a["grid"].values())}
R["S2_effect_size_floor_vs_walk_forward"] = s2

# ================= S3 : gates_final.txt ================================================
gf = os.path.join(ENGINE, "gates_final.txt")
gj = json.load(open(os.path.join(ENGINE, "gates.json"), encoding="utf-8"))
txt = open(gf, encoding="utf-8", errors="replace").read()
rows = []
for k, v in gj["GATES"].items():
    in_txt = None
    for line in txt.splitlines():
        if k in line:
            in_txt = line.split()[0]
            break
    rows.append({"gate": k, "gates_final_txt": in_txt, "gates_json": v["VERDICT"],
                 "AGREE": in_txt == v["VERDICT"]})
R["S3_gates_final_txt_vs_gates_json"] = {
    "gates_final_txt_last_written_at": "e44515d (gates.py changed at 5cf2e48 and a4d19dd afterwards)",
    "rows": rows, "n_disagreeing": sum(1 for r in rows if not r["AGREE"]),
    "tally_line_in_txt": [l for l in txt.splitlines() if "PASS=" in l or "NOT_TESTABLE" in l][:3],
    "tally_in_json": f"PASS={gj['PASS']} FAIL={gj['FAIL']} NOT_TESTABLE={gj['NOT_TESTABLE']}"}

json.dump(R, open(os.path.join(HERE, "rt5_p7_stale_artefacts.json"), "w"), indent=1, default=str)

print("=== S1 answer_sheet.json")
s = R["S1_answer_sheet_json"]
print(f"   byte-identical to a fresh run of the code beside it: {s['BYTE_IDENTICAL']}")
print(f"   leaf fields differing: {s['leaf_fields_that_DIFFER']} of {s['leaf_fields_compared']}")
print(f"   PUBLISHED committed : {s['PUBLISHED_STATES_committed']}")
print(f"   PUBLISHED recomputed: {s['PUBLISHED_STATES_recomputed']}")
for dd in s["DIFFS"][:12]:
    print(f"     {dd['field']}\n        committed = {str(dd['COMMITTED'])[:110]}\n        today     = {str(dd['RECOMPUTED_TODAY'])[:110]}")
print("=== S2 effect-size floor")
for k, v in R["S2_effect_size_floor_vs_walk_forward"].items():
    print(f"   {k:26s} G without floor={v['G_without_the_floor']}  with floor={v['G_with_the_floor']}  "
          f"cells changed={v['walk_forward_cells_the_floor_CHANGES']}/{v['n_cells']}")
print("=== S3 gates_final.txt")
print("   disagreeing gates:", R["S3_gates_final_txt_vs_gates_json"]["n_disagreeing"])
for r in R["S3_gates_final_txt_vs_gates_json"]["rows"]:
    if not r["AGREE"]: print(f"     {r['gate']}: txt={r['gates_final_txt']} json={r['gates_json']}")
print("   txt tally:", R["S3_gates_final_txt_vs_gates_json"]["tally_line_in_txt"])
print("   json tally:", R["S3_gates_final_txt_vs_gates_json"]["tally_in_json"])
print("\nwrote rt5_p7_stale_artefacts.json")
