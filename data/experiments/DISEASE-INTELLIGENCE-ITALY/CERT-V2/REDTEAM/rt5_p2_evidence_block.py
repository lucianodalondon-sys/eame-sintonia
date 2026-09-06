#!/usr/bin/env python3
"""RT5 / PROVENANCE 2 -- what is actually inside rec["EVIDENCE"], and can a third party
recompute one province's number from it?

The expression under test (ENGINE/current_pressure.py:286-288):

    "RAW_FILES":  sorted(meta["hashes"]),
    "RAW_SHA256": sorted(meta["hashes"].values())[:1] and
                  list(sorted(meta["hashes"].items()))[-1],

`X and Y` returns Y whenever X is truthy. X here is a 1-element list of the LOWEST hash,
used only as a non-empty guard, and is discarded. So RAW_SHA256 is the (filename, sha256)
pair of the ALPHABETICALLY LAST raw file of the outcome variable -- the same pair on every
province, regardless of which rows produced that province's value.

This script:
  1. evaluates the expression in isolation and prints what it returns;
  2. runs the shipped module and compares the EVIDENCE block across provinces;
  3. recomputes, per province, WHICH raw files actually supplied the rows behind the
     published VALUE and behind each BASELINE season -- the thing a third party would need.
"""
import json, os, sys, glob, hashlib, datetime as dt, collections

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, "..", ".."))
ENGINE = os.path.join(ROOT, "ENGINE")
sys.path.insert(0, ENGINE)
sys.path.insert(0, os.path.join(ROOT, "CASES"))
import current_pressure as cp

AS_OF = dt.date(2026, 9, 6)
CASES = [("OLIVO x BACTROCERA x TOSCANA", os.path.join(ROOT, "CASES", "OLIVO-BACTROCERA-TOSCANA"), -1002),
         ("VITE x OIDIO x TOSCANA", os.path.join(ROOT, "CASES", "VITE-OIDIO-TOSCANA"), 39)]

out = {"EXPRESSION_UNDER_TEST": "sorted(h.values())[:1] and list(sorted(h.items()))[-1]"}

# ---- 1. the expression, in isolation, on a toy dict ------------------------------------
toy = {"b.json": "aaa", "a.json": "zzz", "c.json": "mmm"}
lhs = sorted(toy.values())[:1]
rhs = list(sorted(toy.items()))[-1]
out["TOY"] = {"dict": toy, "left_operand_discarded": lhs, "value_returned": list(rhs),
              "IS_IT_A_HASH": isinstance(lhs and rhs, str),
              "READS_AS": "a 2-item [filename, sha256] of the alphabetically LAST filename; "
                          "the left operand (lowest hash) is evaluated and thrown away"}
# empty-dict behaviour: the guard makes RAW_SHA256 an empty LIST, not None
out["TOY_EMPTY"] = {"value_returned": (sorted({}.values())[:1] and list(sorted({}.items()))[-1])}

# ---- 2. the real module ----------------------------------------------------------------
percase = {}
for name, d, v in CASES:
    pre = cp.load_rows(d, v)
    rows, scale, meta = pre
    r = cp.current_pressure(d, v, AS_OF, _pre=pre)
    cells = {p: c for p, c in r["PROVINCES"].items() if "EVIDENCE" in c}
    ev_json = {p: json.dumps(c["EVIDENCE"], sort_keys=True) for p, c in cells.items()}
    distinct = sorted(set(ev_json.values()))
    one = json.loads(distinct[0]) if distinct else None

    # what the module hashed vs. what the case actually holds
    all_raw = sorted(os.path.basename(x) for x in glob.glob(os.path.join(d, "RAW", "*.json")))
    idx = json.load(open(os.path.join(d, "collection_index.json")))
    denom_var = idx.get("DENOMINATOR_VAR")
    denom_files = sorted(os.path.basename(x) for x in
                         glob.glob(os.path.join(d, "RAW", f"*_v{denom_var}_*.json"))) if denom_var is not None else []

    # ---- 3. which files actually produced each province's numbers? ----------------------
    # re-derive the row->file mapping ourselves (the module discards it)
    file_of_row = {}
    for fn in sorted(glob.glob(os.path.join(d, "RAW", f"*_v{v}_*.json"))):
        b = os.path.basename(fn)
        for rr in json.load(open(fn)):
            file_of_row[id(rr)] = b
    lo, hi = AS_OF - dt.timedelta(days=cp.WINDOW_DAYS - 1), AS_OF

    contrib = {}
    for prov, cell in sorted(cells.items()):
        # files supplying rows in the CURRENT window, and in the BASELINE windows
        cur_files, base_files = set(), set()
        for fn in sorted(glob.glob(os.path.join(d, "RAW", f"*_v{v}_*.json"))):
            b = os.path.basename(fn)
            for rr in json.load(open(fn)):
                if rr.get("nome_area") != prov: continue
                ds = rr.get("date")
                if not ds: continue
                try: dd = dt.date.fromisoformat(ds)
                except ValueError: continue
                if lo <= dd <= hi:
                    cur_files.add(b)
                for y in (cell.get("BASELINE_SEASONS") or []):
                    if cp._shift_year(lo, y) <= dd <= cp._shift_year(hi, y):
                        base_files.add(b)
        contrib[prov] = {"files_behind_the_published_VALUE": sorted(cur_files),
                         "files_behind_the_BASELINE": sorted(base_files),
                         "n_files_actually_used": len(cur_files | base_files)}

    used_union = sorted(set().union(*[set(c["files_behind_the_published_VALUE"]) |
                                      set(c["files_behind_the_BASELINE"]) for c in contrib.values()])) \
        if contrib else []

    percase[name] = {
        "n_published_cells_with_EVIDENCE": len(cells),
        "DISTINCT_EVIDENCE_BLOCKS_ACROSS_PROVINCES": len(distinct),
        "THE_EVIDENCE_BLOCK": one,
        "RAW_SHA256_field": one["RAW_SHA256"] if one else None,
        "RAW_SHA256_is_the_alphabetically_last_outcome_file":
            (one["RAW_SHA256"][0] == sorted(meta["hashes"])[-1]) if one else None,
        "n_RAW_FILES_named": len(one["RAW_FILES"]) if one else 0,
        "n_files_in_the_case_on_disk": len(all_raw),
        "DENOMINATOR_VAR": denom_var,
        "n_denominator_files_read_by_the_pipeline": len(denom_files),
        "denominator_files_named_in_EVIDENCE": sorted(set(denom_files) & set(one["RAW_FILES"])) if one else [],
        "PER_PROVINCE_TRUE_PROVENANCE": contrib,
        "distinct_true_file_sets_across_provinces":
            len({tuple(c["files_behind_the_published_VALUE"]) for c in contrib.values()}),
        "files_the_case_uses_at_all_for_this_var": len(used_union),
        "FIELDS_IN_EVIDENCE": sorted(one.keys()) if one else [],
        "row_level_identifiers_recorded": [k for k in (one or {})
                                           if k.lower() in ("id_field", "id_survey", "rows", "row_ids")],
    }

out["PER_CASE"] = percase
p = os.path.join(HERE, "rt5_p2_evidence_block.json")
json.dump(out, open(p, "w"), indent=1, default=str)

print("TOY  RAW_SHA256 ->", out["TOY"]["value_returned"], "  (empty dict ->", out["TOY_EMPTY"]["value_returned"], ")")
for n, c in percase.items():
    print(f"\n=== {n}")
    print(f"  published cells carrying EVIDENCE : {c['n_published_cells_with_EVIDENCE']}")
    print(f"  DISTINCT evidence blocks          : {c['DISTINCT_EVIDENCE_BLOCKS_ACROSS_PROVINCES']}")
    print(f"  RAW_SHA256                        : {c['RAW_SHA256_field']}")
    print(f"  == alphabetically last file?      : {c['RAW_SHA256_is_the_alphabetically_last_outcome_file']}")
    print(f"  RAW_FILES named / on disk         : {c['n_RAW_FILES_named']} / {c['n_files_in_the_case_on_disk']}")
    print(f"  denominator files read / named    : {c['n_denominator_files_read_by_the_pipeline']} / "
          f"{len(c['denominator_files_named_in_EVIDENCE'])}")
    print(f"  distinct TRUE file sets by province: {c['distinct_true_file_sets_across_provinces']}")
    print(f"  row-level ids recorded            : {c['row_level_identifiers_recorded']}")
    for prov, cc in list(c["PER_PROVINCE_TRUE_PROVENANCE"].items())[:3]:
        print(f"     {prov:14s} value from {cc['files_behind_the_published_VALUE']}, "
              f"{len(cc['files_behind_the_BASELINE'])} baseline files")
print("\nwrote", p)
