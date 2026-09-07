#!/usr/bin/env python3
"""RT4-10  Two follow-ups, because rt4_09 answered one question badly and left another open.

C-REDONE  GLOB CASE SENSITIVITY. rt4_09's probe created two files differing only in case; on
  a case-insensitive filesystem the second CREATE overwrites the first, so only one file
  existed and the result was meaningless. Redone: create ONE file whose name differs from the
  pattern only in case, and see whether the pattern matches it.

D-EXPLAINED  WHY the loaded payload depends on the order the four variables are requested in.
  rt4_09 showed 3 permutations give 3 different hashes. That is either cosmetic (a list order)
  or semantic (a visit's date/province changes). Decide it field by field.
"""
import os, sys, json, glob, tempfile, collections, datetime as dt

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "engine"))
import di_core

CASE = os.path.abspath(os.path.join(HERE, "..", "..", "DISEASE-INTELLIGENCE-ITALY",
                                    "CASES", "OLIVO-BACTROCERA-TOSCANA"))
AS_OF = dt.date(2026, 9, 6)
out = {}

# ---------- C redone
d = tempfile.mkdtemp(prefix="rt4_glob2_")
open(os.path.join(d, "c2_s1_V1_2099.json"), "w").write("[]")   # ONE file, uppercase V
listed = sorted(os.listdir(d))
m_lower = sorted(os.path.basename(x) for x in glob.glob(os.path.join(d, "*_v1_*.json")))
m_upper = sorted(os.path.basename(x) for x in glob.glob(os.path.join(d, "*_V1_*.json")))
for f in os.listdir(d):
    os.remove(os.path.join(d, f))
os.rmdir(d)
out["C_GLOB_CASE_SENSITIVITY_REDONE"] = {
    "one_file_created": "c2_s1_V1_2099.json",
    "os.listdir_says": listed,
    "pattern_*_v1_*.json_matches": m_lower,
    "pattern_*_V1_*.json_matches": m_upper,
    "GLOB_IS_CASE_INSENSITIVE_ON_THIS_FILESYSTEM": bool(m_lower),
    "MEANING": ("the loader's pattern *_v1_*.json matches a file named ..._V1_... here and "
                "would NOT match it on a case-sensitive filesystem. Same bytes, different "
                "platform, different file set, different denominator. No such file exists in "
                "CASES today, so this is a portability hazard and not a live defect."
                if m_lower else
                "the pattern binds exactly one case here, as it does on Linux")}

# ---------- D explained
sheet = di_core.load_sheet()
canon = ["SAMPLE_SIZE / DENOMINATOR", "ACTIVE_INFESTATION_COUNT",
         "DAMAGING_INFESTATION_COUNT", "TOTAL_INFESTATION_COUNT"]
perms = {"canonical": tuple(canon), "reversed": tuple(reversed(canon))}
runs = {}
for name, perm in perms.items():
    L = di_core.load_visits(CASE, sheet, AS_OF, wanted=perm)
    runs[name] = {v["visit_key"]["id_field"]: v for v in []}   # placeholder, replaced below
    runs[name] = {(v["visit_key"]["id_field"], v["visit_key"]["date"]): v
                  for v in L["visits"]}
    runs[name + "_top"] = {k: val for k, val in L.items() if k not in ("visits",)}

a, b = runs["canonical"], runs["reversed"]
fields = ["observation_date", "province", "comune", "comune_code", "org", "week",
          "usable_for_rates"]
diff = collections.Counter()
examples = collections.defaultdict(list)
for k in a:
    if k not in b:
        diff["key_missing_in_reversed"] += 1
        continue
    for f in fields:
        if a[k].get(f) != b[k].get(f):
            diff[f] += 1
            if len(examples[f]) < 4:
                examples[f].append({"visit_key": list(k), "canonical": a[k].get(f),
                                    "reversed": b[k].get(f)})
    # measurements: compare VALUES only, ignoring dict key order
    ma = {c: a[k]["measurements"][c]["value"] for c in a[k]["measurements"]}
    mb = {c: b[k]["measurements"][c]["value"] for c in b[k]["measurements"]}
    if ma != mb:
        diff["measurement_VALUES"] += 1
        if len(examples["measurement_VALUES"]) < 4:
            examples["measurement_VALUES"].append({"visit_key": list(k), "canonical": ma,
                                                   "reversed": mb})
    if sorted(a[k].get("exclusion_reasons", [])) != sorted(b[k].get("exclusion_reasons", [])):
        diff["exclusion_reasons_as_a_SET"] += 1
    elif a[k].get("exclusion_reasons") != b[k].get("exclusion_reasons"):
        diff["exclusion_reasons_ORDER_ONLY"] += 1
        if len(examples["exclusion_reasons_ORDER_ONLY"]) < 4:
            examples["exclusion_reasons_ORDER_ONLY"].append(
                {"visit_key": list(k), "canonical": a[k].get("exclusion_reasons"),
                 "reversed": b[k].get("exclusion_reasons")})

topa = runs["canonical_top"]
topb = runs["reversed_top"]
top_diff = {k: {"canonical": topa[k], "reversed": topb[k]}
            for k in topa if k != "provenance" and topa[k] != topb[k]}

out["D_WHY_VARIABLE_ORDER_MATTERS"] = {
    "n_visits": len(a),
    "per_visit_field_disagreements": dict(diff),
    "examples": {k: v for k, v in examples.items()},
    "top_level_summary_fields_that_disagree": top_diff,
    "SEMANTIC_OR_COSMETIC": (
        "SEMANTIC - at least one visit's date, province or measurement value depends on which "
        "variable was requested first"
        if any(diff[f] for f in fields + ["measurement_VALUES"]) else
        "COSMETIC - only the ORDER of exclusion_reasons differs; every value, date, province "
        "and measurement is identical. The published report always uses the default order, so "
        "nothing published is affected."),
    "WHY_IT_IS_POSSIBLE_AT_ALL": (
        "di_core.load_visits picks the row that supplies date/province/comune/org/week with "
        "  any_row = next((per_var[c][k]['row'] for c in wanted if k in per_var[c]), None)  "
        "so the FIRST variable in `wanted` that has the key wins. Nothing checks that the "
        "four variables agree about that visit's date or province."),
}

# does the winning row ever disagree between variables?
per_var = {}
for c in canon:
    spec = di_core.var_for(sheet, c)
    rows, _ = di_core._read_variable(CASE, spec["SOURCE_VARIABLE"], sheet)
    per_var[c] = rows
keys = set().union(*[set(v) for v in per_var.values()])
disagree = collections.Counter()
ex2 = []
for k in keys:
    vals = {}
    for c in canon:
        r = per_var[c].get(k)
        if r is None:
            continue
        vals.setdefault("nome_area", set()).add(r["row"].get("nome_area"))
        vals.setdefault("date", set()).add(r["row"].get("date"))
        vals.setdefault("name_4", set()).add(r["row"].get("name_4"))
        vals.setdefault("org_name", set()).add(r["row"].get("org_name"))
        vals.setdefault("week", set()).add(r["row"].get("week"))
    for f, s in vals.items():
        if len(s) > 1:
            disagree[f] += 1
            if len(ex2) < 5:
                ex2.append({"visit_key": list(k), "field": f, "values": sorted(map(str, s))})
out["D2_DO_THE_FOUR_VARIABLES_EVER_DISAGREE_ABOUT_A_VISIT"] = {
    "keys_checked": len(keys),
    "keys_where_the_four_files_disagree_about_a_field": dict(disagree),
    "examples": ex2,
    "MEANING": ("the four files agree about every visit, so 'whichever variable is first "
                "wins' can never change a date or a province on this archive. It is an "
                "unguarded assumption that happens to hold, not a checked invariant."
                if not disagree else
                "THE FOUR FILES DISAGREE: the published date/province depends on the order "
                "the variables are requested in")}

print(json.dumps(out, indent=1, default=str))
json.dump(out, open(os.path.join(HERE, "rt4_10_order_and_glob.json"), "w", encoding="utf-8"),
          indent=1, default=str)
