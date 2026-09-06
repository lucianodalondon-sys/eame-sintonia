#!/usr/bin/env python3
"""RT5 / PROVENANCE 3 -- tamper tests in a SANDBOX COPY. ENGINE/ and CASES/ are never touched.

Four experiments, each on a throwaway copy of OLIVO-BACTROCERA-TOSCANA:

  T1  corrupt an OUTCOME file (v-1002)      -> the check SHOULD fire
  T2  corrupt a DENOMINATOR file (v1)       -> read by denominator_guard(), never hashed
  T3  delete a file's index entry, corrupt it -> by_file.get(base) is None -> falsy -> no check
  T4  set sha256:null in the index, corrupt it-> by_file[base] falsy       -> no check

and one read-only experiment:

  T5  RAW_SHA256 under HINDCAST. Gates C and G are computed from cp.hindcast(), which calls
      current_pressure with as_of in a PAST season. Does the evidence still name the 2026 file?
"""
import json, os, sys, glob, shutil, hashlib, datetime as dt, subprocess, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, "..", ".."))
SRC = os.path.join(ROOT, "CASES", "OLIVO-BACTROCERA-TOSCANA")
SANDBOX = os.path.join(HERE, "_rt5_sandbox")
AS_OF = dt.date(2026, 9, 6)

sys.path.insert(0, os.path.join(ROOT, "ENGINE"))
sys.path.insert(0, os.path.join(ROOT, "CASES"))
import current_pressure as cp

res = {}

def fresh():
    if os.path.exists(SANDBOX): shutil.rmtree(SANDBOX)
    os.makedirs(SANDBOX)
    dst = os.path.join(SANDBOX, "CASE")
    shutil.copytree(SRC, dst)
    return dst

def bump_first_value(path, marker):
    """Change real DATA, not whitespace: flip the first non-null 'val' to a different number.
    This guarantees the bytes differ AND the arithmetic can differ."""
    rows = json.load(open(path))
    n = 0
    for r in rows:
        if r.get("val") not in (None, ""):
            r["val"] = marker
            n += 1
            if n >= 400: break
    json.dump(rows, open(path, "w"))
    return n

def run(dst):
    try:
        r = cp.current_pressure(dst, -1002, AS_OF)
        st = {p: v.get("STATE") for p, v in r["PROVINCES"].items()}
        vals = {p: v.get("VALUE") for p, v in r["PROVINCES"].items()}
        drop = r["DENOMINATOR_GUARD"].get("dropped_zero_or_unknown_denominator")
        return {"RAN": True, "STATES": st, "VALUES": vals, "dropped_by_guard": drop}
    except Exception as e:
        return {"RAN": False, "REFUSED_WITH": f"{type(e).__name__}: {e}"}

baseline = run(fresh() if False else SRC)
res["BASELINE_untouched"] = baseline

# ---- T1: corrupt an OUTCOME file -------------------------------------------------------
dst = fresh()
f = os.path.join(dst, "RAW", "c2_s1_v-1002_2026.json")
n1 = bump_first_value(f, 9999)
res["T1_corrupt_OUTCOME_file"] = {"file": "c2_s1_v-1002_2026.json", "values_changed": n1,
                                  "listed_in_index": True, "has_sha256_in_index": True,
                                  "RESULT": run(dst)}

# ---- T2: corrupt a DENOMINATOR file ----------------------------------------------------
dst = fresh()
f = os.path.join(dst, "RAW", "c2_s1_v1_2026.json")
n2 = bump_first_value(f, 0)          # 0 denominators -> the guard DROPS those visits
idx = json.load(open(os.path.join(dst, "collection_index.json")))
listed = any(r.get("file") == "c2_s1_v1_2026.json" and r.get("sha256") for r in idx["requests"])
r2 = run(dst)
res["T2_corrupt_DENOMINATOR_file"] = {
    "file": "c2_s1_v1_2026.json", "values_changed": n2,
    "listed_in_index_with_sha256": listed,
    "RESULT": r2,
    "STATES_CHANGED_vs_BASELINE": sorted(p for p in baseline["STATES"]
                                         if r2.get("STATES", {}).get(p) != baseline["STATES"][p]) if r2["RAN"] else None,
    "VALUES_CHANGED_vs_BASELINE": sorted(p for p in baseline["VALUES"]
                                         if r2.get("VALUES", {}).get(p) != baseline["VALUES"][p]) if r2["RAN"] else None,
    "dropped_delta": (r2.get("dropped_by_guard") - baseline["dropped_by_guard"]) if r2["RAN"] else None}

# ---- T3: file present, index entry removed ---------------------------------------------
dst = fresh()
f = os.path.join(dst, "RAW", "c2_s1_v-1002_2026.json")
n3 = bump_first_value(f, 9999)
ip = os.path.join(dst, "collection_index.json")
idx = json.load(open(ip))
idx["requests"] = [r for r in idx["requests"] if r.get("file") != "c2_s1_v-1002_2026.json"]
json.dump(idx, open(ip, "w"))
res["T3_index_entry_deleted"] = {"file": "c2_s1_v-1002_2026.json", "values_changed": n3,
                                 "RESULT": run(dst)}

# ---- T4: index entry present, sha256 null ----------------------------------------------
dst = fresh()
f = os.path.join(dst, "RAW", "c2_s1_v-1002_2026.json")
n4 = bump_first_value(f, 9999)
ip = os.path.join(dst, "collection_index.json")
idx = json.load(open(ip))
for r in idx["requests"]:
    if r.get("file") == "c2_s1_v-1002_2026.json":
        r["sha256"] = None
json.dump(idx, open(ip, "w"))
res["T4_sha256_set_to_null"] = {"file": "c2_s1_v-1002_2026.json", "values_changed": n4,
                                "RESULT": run(dst)}

# ---- T5: RAW_SHA256 under hindcast ------------------------------------------------------
t5 = {}
pre = cp.load_rows(SRC, -1002)
for y in (2015, 2020, 2026):
    r = cp.current_pressure(SRC, -1002, dt.date(y, 9, 6), _pre=pre)
    cell = next((c for c in r["PROVINCES"].values() if "EVIDENCE" in c), None)
    t5[str(y)] = {"RAW_SHA256_names": cell["EVIDENCE"]["RAW_SHA256"][0] if cell else None,
                  "file_the_window_rows_are_actually_in": f"c2_s1_v-1002_{y}.json",
                  "CORRECT": (cell["EVIDENCE"]["RAW_SHA256"][0] == f"c2_s1_v-1002_{y}.json") if cell else None}
res["T5_RAW_SHA256_under_hindcast"] = t5

if os.path.exists(SANDBOX): shutil.rmtree(SANDBOX)
p = os.path.join(HERE, "rt5_p3_tamper.json")
json.dump(res, open(p, "w"), indent=1, default=str)

for k, v in res.items():
    if k.startswith("BASELINE"): continue
    print(f"=== {k}")
    if k == "T5_RAW_SHA256_under_hindcast":
        for y, d in v.items():
            print(f"    as_of {y}-09-06 -> RAW_SHA256 names {d['RAW_SHA256_names']}  CORRECT={d['CORRECT']}")
        continue
    rr = v["RESULT"]
    print(f"    values changed: {v.get('values_changed')}   pipeline RAN: {rr['RAN']}")
    if not rr["RAN"]:
        print(f"    REFUSED: {rr['REFUSED_WITH'][:120]}")
    else:
        print(f"    ACCEPTED SILENTLY. states changed: {v.get('STATES_CHANGED_vs_BASELINE')}")
        print(f"                       values changed: {v.get('VALUES_CHANGED_vs_BASELINE')}")
        print(f"                       guard-drop delta: {v.get('dropped_delta')}")
print("\nwrote", p)
