"""Two more tests.

A) recount per_file 'state' distribution -- does the recount's per-file layer
   distinguish partial years?
B) does the ARPAV catalogue / job plan really advertise the short years as
   available years (the other auditor's header line asserts it)?
"""
import json
import os
import collections

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MAN = os.path.join(ROOT, "manifests")

rc = json.load(open(os.path.join(MAN, "daily-series-recount.json"), encoding="utf-8"))
pf = rc["per_file"]
print("=== A) recount per_file 'state' distribution ===")
for k, v in collections.Counter(x["state"] for x in pf).most_common():
    print("  %-24s %5d" % (k, v))

print("\n  the 10 short files as the recount per_file layer sees them:")
for x in pf:
    if x["anno"] != 2026 and x["distinct_dates"] / x["expected_days"] < 0.95:
        print("    %-30s %-8s %4d %4d/%3d  state=%s" % (
            x["stazione"][:30], x["tipo"], x["anno"], x["distinct_dates"],
            x["expected_days"], x["state"]))

print("\n=== B) does the job plan / catalogue advertise those years? ===")
jobs = json.load(open(os.path.join(MAN, "arpav-jobs.json"), encoding="utf-8"))
print("  arpav-jobs.json type:", type(jobs),
      len(jobs) if isinstance(jobs, (list, dict)) else "")
if isinstance(jobs, dict):
    print("  keys:", list(jobs.keys())[:10])
    jl = jobs.get("jobs") or jobs.get("job_list") or []
else:
    jl = jobs
print("  jobs:", len(jl))
if jl:
    print("  sample job:", json.dumps(jl[0], ensure_ascii=False))

targets = {(300001481, 2024), (300011272, 2016)}
for j in jl:
    k = (j.get("codseq"), j.get("anno"))
    if k in targets:
        print("  PLANNED:", json.dumps(j, ensure_ascii=False))

# planned vs preserved
planned = {(j.get("codseq"), j.get("anno")) for j in jl}
pres = {(x["codseq"], x["anno"]) for x in pf}
print("\n  planned jobs:", len(planned), " preserved files:", len(pres))
print("  planned but NOT preserved:", len(planned - pres))
print("  preserved but NOT planned:", len(pres - planned))
