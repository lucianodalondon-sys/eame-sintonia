import json, gzip, datetime, collections

d = datetime.date
print("=== calendar arithmetic ===")
print("2026 leap?", 2026 % 4 == 0)
print("Jan1..Jul31 2026 inclusive =", (d(2026,7,31)-d(2026,1,1)).days + 1, "days")
print("Jan1..Sep05 2026 inclusive =", (d(2026,9,5)-d(2026,1,1)).days + 1, "days")
print("Jan1..Sep06 2026 inclusive =", (d(2026,9,6)-d(2026,1,1)).days + 1, "days")
print("Sep06..Dec31 2026 inclusive =", (d(2026,12,31)-d(2026,9,6)).days + 1, "days")
print("Aug01..Sep05 2026 inclusive =", (d(2026,9,5)-d(2026,8,1)).days + 1, "days")
print("Aug01..Dec31 2026 inclusive =", (d(2026,12,31)-d(2026,8,1)).days + 1, "days")

rows = [json.loads(l) for l in open("manifests/arpav-daily-manifest.jsonl", encoding="utf-8") if l.strip()]
y26 = [r for r in rows if r["anno"] == 2026]

print("\n=== open every 2026 RAW file and classify the gap ===")
print("   %-38s %-5s %-5s %-8s %-8s %s" % ("station/sensor", "rows", "uniq", "tailgap", "intgap", "last"))
tot_tail = tot_int = 0
for r in sorted(y26, key=lambda x: x["stazione"]):
    p = r["raw_path"]
    with gzip.open(p, "rt", encoding="utf-8") as fh:
        obj = json.load(fh)
    data = obj["data"] if isinstance(obj, dict) and "data" in obj else obj
    dates = sorted(set(x["dataora"][:10] for x in data))
    first = d.fromisoformat(dates[0]); last = d.fromisoformat(dates[-1])
    span = (last - first).days + 1
    interior = span - len(dates)                 # holes inside first..last
    tail = 365 - span - (first - d(2026,1,1)).days  # days after last, to Dec 31
    tot_tail += tail; tot_int += interior
    print("   %-38s %-5d %-5d %-8d %-8d %s" % (
        (r["stazione"][:20] + "/" + str(r["sensore"])[:16]), len(data), len(dates), tail, interior, dates[-1]))

print("\n   TOTAL tail days (after last preserved day): %d" % tot_tail)
print("   TOTAL interior holes                      : %d" % tot_int)
print("   sum of manifest missing_days              : %d" % sum(r["missing_days"] for r in y26))
print("   tail + interior                           : %d" % (tot_tail + tot_int))

print("\n=== how much of the declared 'missing' is days that had NOT HAPPENED at capture ===")
notyet = (d(2026,12,31) - d(2026,9,6)).days + 1
print("   days 2026-09-06..2026-12-31 (not yet existing at capture) = %d per file" % notyet)
print("   over 60 files                                            = %d row-days" % (notyet*60))
print("   total declared missing_days over 60 files                = %d" % sum(r["missing_days"] for r in y26))
print("   share of declared 'missing' that is future               = %.1f%%" % (100.0*notyet*60/sum(r["missing_days"] for r in y26)))
