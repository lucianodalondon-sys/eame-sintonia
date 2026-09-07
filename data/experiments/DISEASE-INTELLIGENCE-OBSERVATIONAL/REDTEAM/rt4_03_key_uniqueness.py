#!/usr/bin/env python3
"""RT4-03  Verify, on the raw bytes and without the engine, the claim:
   "(id_field, date) is unique - 79,251 distinct keys over 79,251 rows in all four variables"

I count, per variable:
  rows_total            every element of the JSON array
  rows_with_full_key    both key fields present and not None
  distinct_keys         len(set)
  repeated_keys         keys seen more than once
  repeats_with_SAME_val a repeat the loader would silently accept (it only raises on a
                        DIFFERENT value - a same-value repeat is invisible)
  repeats_with_DIFF_val a repeat that would raise
Also: the TYPES of id_field and date, because the engine sorts by str(t[1]), str(t[0])
and a str/int mix would make that sort key non-injective.
"""
import os, json, glob, collections, hashlib

HERE = os.path.dirname(os.path.abspath(__file__))
RAW = os.path.abspath(os.path.join(HERE, "..", "..", "DISEASE-INTELLIGENCE-ITALY",
                                   "CASES", "OLIVO-BACTROCERA-TOSCANA", "RAW"))
KEY = ["id_field", "date"]
VARS = [1, -1001, -1002, -1003]


def _num(v):
    if v is None or v == "":
        return None
    try:
        return float(str(v).replace(",", "."))
    except ValueError:
        return None


out = {"RAW": RAW, "per_variable": {}, "cross_variable": {}}
allfiles = sorted(glob.glob(os.path.join(RAW, "*.json")))
out["files_in_RAW_total"] = len(allfiles)
matched_by_engine = set()

for v in VARS:
    pat = os.path.join(RAW, f"*_v{v}_*.json")
    files = sorted(glob.glob(pat))
    matched_by_engine |= set(files)
    rows = 0
    keys = collections.Counter()
    vals = collections.defaultdict(set)
    types_id, types_date = collections.Counter(), collections.Counter()
    nonint_vals = 0
    null_key = 0
    for fn in files:
        for r in json.loads(open(fn, "rb").read().decode("utf-8")):
            rows += 1
            k = tuple(r.get(f) for f in KEY)
            types_id[type(k[0]).__name__] += 1
            types_date[type(k[1]).__name__] += 1
            if None in k:
                null_key += 1
                continue
            keys[k] += 1
            n = _num(r.get("val"))
            vals[k].add(n)
            if n is not None and n != int(n):
                nonint_vals += 1
    rep = {k: c for k, c in keys.items() if c > 1}
    diff = {k: sorted(map(str, vals[k])) for k in rep if len(vals[k]) > 1}
    # would str(date),str(id) collide for two DIFFERENT keys? (sort-key injectivity)
    sortkeys = collections.Counter((str(k[1]), str(k[0])) for k in keys)
    sk_collisions = {sk: c for sk, c in sortkeys.items() if c > 1}
    out["per_variable"][str(v)] = {
        "n_files": len(files),
        "rows_total": rows,
        "rows_with_null_in_key": null_key,
        "distinct_keys": len(keys),
        "repeated_keys": len(rep),
        "repeats_with_SAME_value_silently_accepted": len(rep) - len(diff),
        "repeats_with_DIFFERENT_value_would_RAISE": len(diff),
        "example_diff": dict(list(diff.items())[:3]),
        "id_field_types": dict(types_id), "date_types": dict(types_date),
        "non_integer_val_count": nonint_vals,
        "SORT_KEY_str_date_str_id_collisions": len(sk_collisions),
    }

out["files_matched_by_the_engines_four_globs"] = len(matched_by_engine)
out["files_in_RAW_never_matched"] = sorted(
    os.path.basename(f) for f in set(allfiles) - matched_by_engine)
print(json.dumps(out, indent=1, default=str))
json.dump(out, open(os.path.join(HERE, "rt4_03_key_uniqueness.json"), "w",
                    encoding="utf-8"), indent=1, default=str)
