#!/usr/bin/env python3
"""RT5 / PROVENANCE 1 -- when does the sha256 check silently NOT run?

Written from scratch. Does not import anything from CERT-V2. Reads ENGINE/CASES read-only.

load_rows() does:
    by_file = {r["file"]: r.get("sha256") for r in idx["requests"] if r.get("file")}
    for fn in sorted(glob(RAW/*_v{var_id}_*.json)):
        h = sha256(fn)
        if by_file.get(base) and by_file[base] != h: raise
Two falsy escapes:
    (a) base not in by_file          -> .get() is None -> no check
    (b) by_file[base] is None/""/0   -> falsy          -> no check
and one scope escape:
    (c) files whose var != var_id are never globbed at all, including the DENOMINATOR files.
"""
import json, os, glob, hashlib, sys, collections

HERE = os.path.dirname(os.path.abspath(__file__))
CASES = os.path.normpath(os.path.join(HERE, "..", "..", "CASES"))

def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()

def var_of(basename):
    # c{crop}_s{schema}_v{var}_{year}.json
    stem = basename[:-5] if basename.endswith(".json") else basename
    parts = stem.split("_")
    for p in parts:
        if p.startswith("v"):
            try:
                return int(p[1:])
            except ValueError:
                pass
    return None

report = {}
for case in sorted(os.listdir(CASES)):
    d = os.path.join(CASES, case)
    idx_p = os.path.join(d, "collection_index.json")
    if not os.path.isdir(d) or not os.path.exists(idx_p):
        continue
    idx = json.load(open(idx_p))
    reqs = idx.get("requests") or []
    by_file = {r["file"]: r.get("sha256") for r in reqs if r.get("file")}
    on_disk = sorted(os.path.basename(x) for x in glob.glob(os.path.join(d, "RAW", "*.json")))

    listed_with_hash = sorted(f for f, h in by_file.items() if h)
    listed_no_hash = sorted(f for f, h in by_file.items() if not h)
    on_disk_unlisted = sorted(f for f in on_disk if f not in by_file)
    listed_missing_on_disk = sorted(f for f in by_file if f not in on_disk)

    # which vars does the OUTCOME glob actually cover?
    outcome_var = idx.get("OUTCOME_VAR")
    denom_var = idx.get("DENOMINATOR_VAR")
    vars_on_disk = collections.Counter(var_of(f) for f in on_disk)

    # files the pipeline READS but never hashes: denominator glob in denominator_guard()
    denom_files = []
    if denom_var is not None:
        denom_files = sorted(os.path.basename(x) for x in
                             glob.glob(os.path.join(d, "RAW", f"*_v{denom_var}_*.json")))

    # verify actual bytes vs recorded hash, for the ones that ARE checkable
    mismatches = [f for f in listed_with_hash
                  if os.path.exists(os.path.join(d, "RAW", f))
                  and sha(os.path.join(d, "RAW", f)) != by_file[f]]

    report[case] = {
        "files_on_disk": len(on_disk),
        "requests_in_index": len(reqs),
        "index_entries_with_a_file": len(by_file),
        "COVERED_by_a_real_sha256": len(listed_with_hash),
        "ESCAPE_a_on_disk_but_not_in_index": {"n": len(on_disk_unlisted), "files": on_disk_unlisted},
        "ESCAPE_b_in_index_but_sha256_falsy": {"n": len(listed_no_hash), "files": listed_no_hash},
        "index_entries_with_no_file_on_disk": {"n": len(listed_missing_on_disk),
                                               "files": listed_missing_on_disk},
        "DECLARED_OUTCOME_VAR": outcome_var,
        "DECLARED_DENOMINATOR_VAR": denom_var,
        "vars_present_on_disk": {str(k): v for k, v in sorted(vars_on_disk.items(),
                                                              key=lambda kv: (kv[0] is None, kv[0]))},
        "ESCAPE_c_denominator_files_read_but_never_hashed": {
            "n": len(denom_files), "files": denom_files[:3] + (["..."] if len(denom_files) > 3 else [])},
        "hash_mismatches_among_checked": mismatches,
    }

out = os.path.join(HERE, "rt5_p1_hash_coverage.json")
json.dump(report, open(out, "w"), indent=1)
for c, r in report.items():
    print(f"=== {c}")
    print(f"    {r['files_on_disk']} files on disk | {r['COVERED_by_a_real_sha256']} have a usable sha256 in the index")
    print(f"    ESCAPE a (on disk, unlisted)      : {r['ESCAPE_a_on_disk_but_not_in_index']['n']}")
    print(f"    ESCAPE b (listed, sha256 falsy)   : {r['ESCAPE_b_in_index_but_sha256_falsy']['n']}")
    print(f"    ESCAPE c (denominator, never hashed): {r['ESCAPE_c_denominator_files_read_but_never_hashed']['n']}")
    print(f"    mismatches among the checked      : {r['hash_mismatches_among_checked']}")
print("\nwrote", out)
