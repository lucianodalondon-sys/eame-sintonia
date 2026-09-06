import json, gzip, collections

ROOT = r"C:/disease-local-collection-italy/pilot-disease-local-collection"
TAB = ROOT + "/raw/F4-arpav-rest/tabella/"
RC = json.load(open(ROOT + "/manifests/daily-series-recount.json", encoding="utf-8"))
pf = json.load(open(r"C:/disease-local-collection-italy/audit-scratch/l3_perfile.json", encoding="utf-8"))

print("=== dataora time-of-day check (sub-daily rows would fake completeness) ===")
times = collections.Counter()
for f in pf:
    doc = json.loads(gzip.open(TAB + f["file"], "rb").read().decode("utf-8"))
    for r in doc["data"]:
        times[r["dataora"][10:]] += 1
print("distinct time-of-day suffixes across all 366978 rows:", dict(times))

print()
print("=== recount sensor_types 'years' is a UNION - how many stations actually span it? ===")
S = collections.defaultdict(lambda: collections.defaultdict(set))
name = {}
for f in pf:
    S[f["tipo"][0]][f["station_code"][0]].add(f["year"])
    name[f["station_code"][0]] = f["station"][0]

for t, blk in RC["sensor_types"].items():
    yrs = set(blk["years"])
    lo, hi = min(yrs), max(yrs)
    st = S[t]
    full = [k for k in st if st[k] == yrs]
    partial = sorted([(name[k], min(st[k]), max(st[k]), len(st[k])) for k in st if st[k] != yrs])
    myrows = sum(f["rows"] for f in pf if f["tipo"] == [t])
    print()
    print("{}: recount says files={} rows={} stations={} years={}-{}".format(t, blk["files"], blk["rows"], blk["stations"], lo, hi))
    print("   my recount:  files={} rows={} stations={}".format(len([f for f in pf if f['tipo'] == [t]]), myrows, len(st)))
    print("   stations that actually hold EVERY year {}-{}: {} of {}".format(lo, hi, len(full), len(st)))
    for p in partial:
        print("      SHORT SPAN: {:<30} {}-{} ({} yrs, not {})".format(p[0], p[1], p[2], p[3], len(yrs)))

print()
print("=== totals ===")
print("recount daily_files={} daily_rows={}".format(RC["daily_files"], RC["daily_rows"]))
print("my       daily_files={} daily_rows={}".format(len(pf), sum(f["rows"] for f in pf)))
print("recount empty_year_files_not_zero:", RC["empty_year_files_not_zero"])
