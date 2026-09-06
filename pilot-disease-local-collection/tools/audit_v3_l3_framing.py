"""Does the package PRESENT the 10 short files as full years?

Checks three surfaces:
  1. arpav-daily-manifest.jsonl   (per-file row)
  2. daily-series-provenance.jsonl (per-file row)
  3. daily-series-recount.json     (the aggregate sensor_types year lists)
"""
import gzip
import json
import os
import calendar

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(ROOT, "raw", "F4-arpav-rest", "tabella")
MAN = os.path.join(ROOT, "manifests")

# the 10 short files, re-derived here from raw (not copied from anyone)
short = {}
for fn in sorted(os.listdir(RAW)):
    if not fn.endswith(".json.gz"):
        continue
    codseq, yr = fn[:-8].replace(".json", "").split("_")
    yr = int(yr)
    if yr == 2026:
        continue
    with gzip.open(os.path.join(RAW, fn), "rb") as fh:
        d = json.loads(fh.read().decode("utf-8"))
    dates = {r["dataora"][:10] for r in (d.get("data") or []) if r.get("dataora")}
    cal = 366 if calendar.isleap(yr) else 365
    if len(dates) / cal < 0.95:
        short[(int(codseq), yr)] = len(dates)

print("short (<95pct, non-2026) files re-derived from raw:", len(short))

# --- surface 1: daily manifest ---
print("\n=== 1. arpav-daily-manifest.jsonl rows for those files ===")
seen = set()
with open(os.path.join(MAN, "arpav-daily-manifest.jsonl"), encoding="utf-8") as fh:
    for line in fh:
        o = json.loads(line)
        k = (o["codseq"], o["anno"])
        if k in short:
            seen.add(k)
            print("  %-30s %-8s %4d rows=%-4s expected=%-4s missing=%-4s completeness=%-20s preservation=%s" % (
                o["stazione"][:30], o.get("tipo"), o["anno"], o.get("rows"),
                o.get("expected_days"), o.get("missing_days"),
                o.get("completeness"), o.get("preservation")))
print("  matched", len(seen), "of", len(short))

# --- surface 2: provenance ---
print("\n=== 2. daily-series-provenance.jsonl COMPLETENESS for those files ===")
seen2 = set()
with open(os.path.join(MAN, "daily-series-provenance.jsonl"), encoding="utf-8") as fh:
    for line in fh:
        o = json.loads(line)
        k = (o["SENSOR_ID"], o["YEAR"])
        if k in short:
            seen2.add(k)
            print("  %-30s %-8s %4d ROWS=%-4s EXPECTED=%-4s MISSING=%-4s %s" % (
                o["STATION_NAME"][:30], o.get("VARIABLE_CODE"), o["YEAR"],
                o.get("ROWS"), o.get("EXPECTED_DAYS"), o.get("MISSING_DAYS"),
                o.get("COMPLETENESS")))
print("  matched", len(seen2), "of", len(short))

# --- surface 3: the recount aggregate ---
print("\n=== 3. daily-series-recount.json sensor_types year lists ===")
rc = json.load(open(os.path.join(MAN, "daily-series-recount.json"), encoding="utf-8"))
for t, v in rc["sensor_types"].items():
    print("  %-8s files=%-4d rows=%-7d stations=%-3d years=%s" % (
        t, v["files"], v["rows"], v["stations"],
        "%d-%d (n=%d)" % (min(v["years"]), max(v["years"]), len(v["years"]))))
    print("           keys present in this block: %s" % sorted(v.keys()))
print("\n  top-level keys of recount: %s" % sorted(rc.keys()))
print("  empty_year_files_not_zero: %r" % (rc.get("empty_year_files_not_zero"),))

# does any aggregate surface carry a completeness qualifier?
blob = json.dumps(rc)
for token in ["PARTIAL", "missing", "MISSING", "expected", "EXPECTED",
              "completeness", "COMPLETENESS", "partial"]:
    print("  recount contains %-14s : %s" % (token, token in blob))
