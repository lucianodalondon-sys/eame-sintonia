import json, collections

M = [json.loads(l) for l in open(r"C:/disease-local-collection-italy/pilot-disease-local-collection/manifests/arpav-daily-manifest.jsonl", encoding="utf-8")]
P = [json.loads(l) for l in open(r"C:/disease-local-collection-italy/pilot-disease-local-collection/manifests/daily-series-provenance.jsonl", encoding="utf-8")]
pf = json.load(open(r"C:/disease-local-collection-italy/audit-scratch/l3_perfile.json", encoding="utf-8"))
by = {(f["codseq"], f["year"]): f for f in pf}

print("=== manifest rows:", len(M), " provenance rows:", len(P), " raw files:", len(pf))
print()
print("=== how the manifest treats 2026 ===")
m26 = [m for m in M if m["anno"] == 2026]
print("manifest 2026 rows:", len(m26))
print("expected_days values used for 2026:", sorted(set(m["expected_days"] for m in m26)))
print("missing_days range 2026:", min(m["missing_days"] for m in m26), "..", max(m["missing_days"] for m in m26))
print("completeness labels 2026:", collections.Counter(m["completeness"] for m in m26))
print("last_date values 2026:", sorted(set(m["last_date"][:10] for m in m26)))
print()
print("=== completeness label distribution, ALL manifest rows ===")
print(collections.Counter(m["completeness"] for m in M))
print()
p26 = [p for p in P if p["YEAR"] == 2026]
print("=== provenance 2026 ===")
print("rows:", len(p26))
print("EXPECTED_DAYS values:", sorted(set(p["EXPECTED_DAYS"] for p in p26)))
print("COMPLETENESS labels:", collections.Counter(p["COMPLETENESS"] for p in p26))
print("MISSING_DAYS range:", min(p["MISSING_DAYS"] for p in p26), "..", max(p["MISSING_DAYS"] for p in p26))
print()
print("=== provenance COMPLETENESS distribution, ALL ===")
print(collections.Counter(p["COMPLETENESS"] for p in P))
print()
print("=== cross-check manifest rows vs my recount ===")
bad = 0
for m in M:
    k = (m["codseq"], m["anno"])
    f = by.get(k)
    if f is None:
        print("MANIFEST ROW WITH NO RAW FILE:", k); bad += 1; continue
    if m["rows"] != f["rows"]:
        print("ROWS MISMATCH", k, "manifest", m["rows"], "actual", f["rows"]); bad += 1
print("manifest-vs-raw mismatches:", bad)
print()
print("=== cross-check provenance ROWS/DISTINCT_DATES/ROWS_WITH_VALUE vs my recount ===")
bad2 = 0
for p in P:
    k = (p["SENSOR_ID"], p["YEAR"])
    f = by.get(k)
    if f is None:
        print("PROV ROW WITH NO RAW FILE:", k); bad2 += 1; continue
    if p["ROWS"] != f["rows"] or p["DISTINCT_DATES"] != f["distinct_dates"] or p["ROWS_WITH_VALUE"] != f["rows"] - f["nullish_values"]:
        print("PROV MISMATCH", k, p["ROWS"], p["DISTINCT_DATES"], p["ROWS_WITH_VALUE"], "vs", f["rows"], f["distinct_dates"], f["rows"] - f["nullish_values"]); bad2 += 1
print("provenance-vs-raw mismatches:", bad2)
