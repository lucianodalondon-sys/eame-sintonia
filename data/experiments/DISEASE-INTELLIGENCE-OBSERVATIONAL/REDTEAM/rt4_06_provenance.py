#!/usr/bin/env python3
"""RT4-06  PROVENANCE AUDIT.

Claim under attack: "every input file is hashed and the hash matches disk", 84 files
(21 per variable x 4 variables).

Three separate questions, kept separate because they have different answers:

  A  COVERAGE   How many file hashes does the PUBLISHED artifact actually carry, and do they
                cover every RAW file the loader globbed?
  B  AGREEMENT  Does each published hash equal sha256 of the file on disk right now?
  C  COMPLETENESS  What OTHER bytes does the answer demonstrably depend on, that carry no
                hash anywhere in the artifact? For each candidate I do not argue - I record
                its sha256 and, where cheap, show that changing it changes the answer.

usage: py rt4_06_provenance.py <report.json>
"""
import os, sys, json, glob, hashlib, collections

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
EXP = os.path.abspath(os.path.join(HERE, ".."))
CASE = os.path.join(ROOT, "data", "experiments", "DISEASE-INTELLIGENCE-ITALY",
                    "CASES", "OLIVO-BACTROCERA-TOSCANA")


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


rep = json.load(open(sys.argv[1], encoding="utf-8"))
prov = rep["loaded"]["provenance"]

# ---- A coverage
published = {}
per_var = {}
for canonical, block in prov.items():
    per_var[canonical] = {"source_variable": block["source_variable"],
                          "n_files": len(block["files"])}
    for f in block["files"]:
        published.setdefault(f["file"], set()).add(f["sha256"])

on_disk = sorted(os.path.basename(p) for p in glob.glob(os.path.join(CASE, "RAW", "*.json")))
globbed = set()
for canonical, block in prov.items():
    v = block["source_variable"]
    globbed |= {os.path.basename(p)
                for p in glob.glob(os.path.join(CASE, "RAW", f"*_v{v}_*.json"))}

# ---- B agreement
mismatch, missing_on_disk = [], []
for fn, hs in published.items():
    p = os.path.join(CASE, "RAW", fn)
    if not os.path.exists(p):
        missing_on_disk.append(fn)
        continue
    d = sha(p)
    if d not in hs:
        mismatch.append({"file": fn, "published": sorted(hs), "on_disk": d})

# ---- C completeness: other bytes the answer depends on
others = collections.OrderedDict()
cand = [
    ("S1-SEMANTICS/SOURCE-SEMANTIC-SHEET.json",
     os.path.join(EXP, "S1-SEMANTICS", "SOURCE-SEMANTIC-SHEET.json"),
     "supplies SOURCE_VARIABLE ids, VISIT_KEY, SOURCE_ACTION_BANDS. Change a band edge and "
     "the published colour changes; change a SOURCE_VARIABLE and a different column is read."),
    ("engine/di_core.py", os.path.join(EXP, "engine", "di_core.py"),
     "the loader, the visit key, the sanity rules"),
    ("engine/di_observe.py", os.path.join(EXP, "engine", "di_observe.py"),
     "every published number and every declared parameter"),
    ("engine/di_adama.py", os.path.join(EXP, "engine", "di_adama.py"), "the ADAMA block"),
    ("engine/di_render.py", os.path.join(EXP, "engine", "di_render.py"),
     "the human text, which is the artifact a person reads"),
    ("engine/di_report.py", os.path.join(EXP, "engine", "di_report.py"), "the orchestration"),
    ("italia-portale/client/italy-label-verdicts.js",
     os.path.join(ROOT, "italia-portale", "client", "italy-label-verdicts.js"),
     "ADAMA_RELEVANCE YES/NO/UNKNOWN and its printed reason come from this file"),
    ("italia-portale/client/italy-handoff-v21.js",
     os.path.join(ROOT, "italia-portale", "client", "italy-handoff-v21.js"),
     "olive_objects counts printed inside the ADAMA reason string"),
]
for name, p, why in cand:
    others[name] = {"exists": os.path.exists(p),
                    "sha256": sha(p) if os.path.exists(p) else None,
                    "bytes": os.path.getsize(p) if os.path.exists(p) else None,
                    "appears_anywhere_in_the_artifact":
                        (sha(p)[:16] in json.dumps(rep)) if os.path.exists(p) else False,
                    "why_the_answer_depends_on_it": why}

# ---- is there ANY code path that COMPARES a hash to an expectation?
src = ""
for f in glob.glob(os.path.join(EXP, "engine", "*.py")):
    src += open(f, encoding="utf-8").read()
compares = [ln.strip() for ln in src.splitlines()
            if "sha256" in ln and ("==" in ln or "!=" in ln)]

out = {
 "A_COVERAGE": {
   "raw_files_on_disk": len(on_disk),
   "raw_files_matched_by_the_four_globs": len(globbed),
   "distinct_files_carrying_a_published_hash": len(published),
   "per_variable": per_var,
   "expected_21_per_variable_x_4": sum(v["n_files"] for v in per_var.values()),
   "raw_files_on_disk_with_NO_published_hash": sorted(set(on_disk) - set(published)),
   "COVERS_EVERY_RAW_FILE": set(on_disk) == set(published) == globbed},
 "B_AGREEMENT": {
   "files_checked": len(published),
   "hash_mismatches_vs_disk": mismatch,
   "published_files_absent_from_disk": missing_on_disk,
   "ALL_MATCH": not mismatch and not missing_on_disk,
   "WHAT_THIS_DOES_AND_DOES_NOT_PROVE":
     "The engine COMPUTES these hashes from the same disk it reads. Agreement is therefore "
     "circular: it proves the artifact records what it read, not that what it read is what "
     "was collected. There is no stored expectation to compare against."},
 "C_COMPLETENESS": {
   "other_inputs_the_answer_depends_on": others,
   "n_such_inputs_carrying_no_hash_in_the_artifact":
     sum(1 for v in others.values() if not v["appears_anywhere_in_the_artifact"]),
   "python_version_recorded_in_artifact": "python" in json.dumps(rep).lower(),
   "commit_or_code_version_recorded_in_artifact":
     any(k in json.dumps(rep) for k in ("commit", "git", "SHEET_VERSION"))},
 "D_IS_THERE_ANY_VERIFICATION": {
   "lines_in_engine_that_compare_a_sha256_to_anything": compares,
   "THE_READER_VERIFIES_NOTHING": not any("prev" not in c for c in compares) or not compares},
}
print(json.dumps(out, indent=1, default=str))
json.dump(out, open(os.path.join(HERE, "rt4_06_provenance.json"), "w", encoding="utf-8"),
          indent=1, default=str)
