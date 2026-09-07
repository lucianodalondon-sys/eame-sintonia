#!/usr/bin/env python3
"""RT4-07  TAMPER. Never touches CASES/ - everything happens in a shadow copy outside the
repository, whose path is passed in.

usage: py rt4_07_tamper.py <shadow_case_dir>

Four tampers, each on a fresh copy of ONE raw file:

  T1 CHANGE ONE VALUE      one `val` in c2_s1_v-1001_2026.json, inside the published 28-day
                           window. Does any published number move? Does anything object?
  T2 INJECT A REAL COLLISION  append a row with an EXISTING (id_field,date) and a DIFFERENT
                           value, into the real file, and call the real loader. The tool's
                           own test D never does this - it re-implements the guard inside the
                           test and raises its own exception, so it proves nothing about the
                           loader. This does.
  T3 INJECT A SAME-VALUE DUPLICATE  same key, SAME value. The guard only fires on a different
                           value, so this should pass silently. Measure what it costs.
  T4 EDIT THE SEMANTIC SHEET  move one action-band edge. The sheet carries no hash anywhere
                           in the artifact, so nothing can notice.
"""
import os, sys, json, shutil, hashlib, glob, copy, datetime as dt

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "engine"))
import di_core, di_observe

SHADOW = os.path.abspath(sys.argv[1])
AS_OF = dt.date(2026, 9, 6)
METRIC = "ACTIVE_INFESTATION_COUNT"
VAR_FILE = "c2_s1_v-1001_2026.json"
RAW = os.path.join(SHADOW, "RAW")
PRISTINE = os.path.join(SHADOW, "_pristine_" + VAR_FILE)

if not os.path.exists(PRISTINE):
    shutil.copy2(os.path.join(RAW, VAR_FILE), PRISTINE)


def restore():
    shutil.copy2(PRISTINE, os.path.join(RAW, VAR_FILE))


def write_rows(rows):
    open(os.path.join(RAW, VAR_FILE), "wb").write(
        json.dumps(rows, ensure_ascii=False).encode("utf-8"))


def summary(sheet, province="Firenze"):
    loaded = di_core.load_visits(SHADOW, sheet, AS_OF)
    c = di_observe.cell(loaded["visits"], sheet, province, METRIC, AS_OF)
    o = c["observation"]
    return {"value_pct": o.get("value_pct"), "infested": o.get("infested_drupes"),
            "sampled": o.get("drupes_sampled"), "n_visits": o.get("n_visits"),
            "band": (o.get("source_band") or {}).get("label"),
            "historical_state": c["analysis"]["historical_state"],
            "trend": c["analysis"]["observed_trend"],
            "published_hash_for_the_tampered_file": next(
                (f["sha256"] for f in loaded["provenance"][METRIC]["files"]
                 if f["file"] == VAR_FILE), None),
            "engine_raised": None, "engine_warned": None}


res = {"shadow": SHADOW, "tampered_file": VAR_FILE}
sheet = di_core.load_sheet()
restore()
base = summary(sheet)
res["T0_BASELINE"] = base

# ---- T1 change one value inside the published window
restore()
rows = json.loads(open(os.path.join(RAW, VAR_FILE), "rb").read().decode("utf-8"))
lo, hi = di_observe._win(AS_OF, di_observe.PARAMS["WINDOW_DAYS"])
target = None
for i, r in enumerate(rows):
    try:
        d = dt.date.fromisoformat(str(r.get("date")))
    except Exception:
        continue
    if lo <= d <= hi and r.get("nome_area") == "Firenze" and r.get("val") not in (None, ""):
        target = i
        break
if target is None:
    res["T1"] = {"SKIPPED": "no Firenze row inside the window"}
else:
    old = rows[target]["val"]
    rows[target]["val"] = "99"
    write_rows(rows)
    try:
        t1 = summary(sheet)
        t1["engine_raised"] = False
    except Exception as e:
        t1 = {"engine_raised": True, "exception": f"{type(e).__name__}: {e}"}
    res["T1_CHANGE_ONE_VALUE"] = {
        "row_index": target, "date": rows[target].get("date"),
        "id_field": rows[target].get("id_field"), "old_val": old, "new_val": "99",
        "after": t1,
        "value_pct_moved": (None if t1.get("value_pct") is None or base["value_pct"] is None
                            else round(t1["value_pct"] - base["value_pct"], 6)),
        "published_hash_changed":
            t1.get("published_hash_for_the_tampered_file") !=
            base["published_hash_for_the_tampered_file"],
        "ENGINE_OBJECTED": bool(t1.get("engine_raised"))}

# ---- T2 inject a REAL collision, different value, and call the REAL loader
restore()
rows = json.loads(open(os.path.join(RAW, VAR_FILE), "rb").read().decode("utf-8"))
dup = copy.deepcopy(rows[0])
orig_val = dup.get("val")
dup["val"] = str(float(di_core._num(orig_val) or 0) + 7)
rows.append(dup)
write_rows(rows)
t2 = {"duplicated_key": {"id_field": dup.get("id_field"), "date": dup.get("date")},
      "original_val": orig_val, "injected_val": dup["val"]}
try:
    out, files = di_core._read_variable(SHADOW, -1001, sheet)
    t2["LOADER_RAISED"] = False
    t2["result"] = "the loader accepted the collision and returned a value"
    t2["value_the_loader_kept"] = out[(dup.get("id_field"), dup.get("date"))]["value"]
except di_core.JoinConflict as e:
    t2["LOADER_RAISED"] = True
    t2["exception_type"] = "JoinConflict"
    t2["message"] = str(e)[:260]
except Exception as e:
    t2["LOADER_RAISED"] = True
    t2["exception_type"] = type(e).__name__
    t2["message"] = str(e)[:260]
res["T2_INJECTED_COLLISION_DIFFERENT_VALUE"] = t2

# ---- T3 same-value duplicate
restore()
rows = json.loads(open(os.path.join(RAW, VAR_FILE), "rb").read().decode("utf-8"))
dup = copy.deepcopy(rows[0])
rows.append(dup)
write_rows(rows)
t3 = {"duplicated_key": {"id_field": dup.get("id_field"), "date": dup.get("date")},
      "val": dup.get("val")}
try:
    out, files = di_core._read_variable(SHADOW, -1001, sheet)
    t3["LOADER_RAISED"] = False
    t3["n_keys_returned"] = len(out)
    t3["NOTE"] = ("a same-key same-value duplicate is accepted in silence and is invisible "
                  "in the output: nothing counts it, nothing reports it")
except Exception as e:
    t3["LOADER_RAISED"] = True
    t3["message"] = f"{type(e).__name__}: {e}"[:260]
res["T3_INJECTED_DUPLICATE_SAME_VALUE"] = t3

# ---- T4 edit the semantic sheet (in memory - the sheet on disk is never touched)
restore()
s2 = di_core.load_sheet()
s2["SOURCE_ACTION_BANDS"]["BANDS"][1]["to_pct"] = 0.5      # 0-6% green becomes 0-0.5%
s2["SOURCE_ACTION_BANDS"]["BANDS"][2]["from_pct"] = 0.5
try:
    t4 = summary(s2)
    t4["engine_raised"] = False
except Exception as e:
    t4 = {"engine_raised": True, "exception": f"{type(e).__name__}: {e}"}
res["T4_EDIT_THE_SEMANTIC_SHEET"] = {
    "edit": "SOURCE_ACTION_BANDS green band upper edge 6 -> 0.5",
    "band_before": base["band"], "band_after": t4.get("band"),
    "BAND_CHANGED": base["band"] != t4.get("band"),
    "any_hash_in_the_artifact_covers_the_sheet": False,
    "ENGINE_OBJECTED": bool(t4.get("engine_raised"))}

restore()
print(json.dumps(res, indent=1, default=str))
json.dump(res, open(os.path.join(HERE, "rt4_07_tamper.json"), "w", encoding="utf-8"),
          indent=1, default=str)
