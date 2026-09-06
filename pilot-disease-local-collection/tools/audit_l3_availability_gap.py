import json, collections

pf = json.load(open(r"C:/disease-local-collection-italy/audit-scratch/l3_perfile.json", encoding="utf-8"))

buckets = collections.Counter()
rows = []
for f in pf:
    pct = 100.0 * f["distinct_dates"] / f["calendar_days"]
    inprog = (f["year"] == 2026)
    rows.append((pct, f, inprog))
    if inprog:
        buckets["2026 in progress (excluded)"] += 1
    elif pct == 100.0:
        buckets["100.0 pct complete"] += 1
    elif pct >= 99.0:
        buckets["99.0-99.9 pct"] += 1
    elif pct >= 95.0:
        buckets["95-99 pct"] += 1
    elif pct >= 90.0:
        buckets["90-95 pct"] += 1
    elif pct >= 50.0:
        buckets["50-90 pct"] += 1
    else:
        buckets["UNDER 50 pct but catalogued as an available year"] += 1

print("=== every (sensor,year) the ARPAV catalogue advertises as an available year ===")
for k in ["100.0 pct complete", "99.0-99.9 pct", "95-99 pct", "90-95 pct", "50-90 pct",
          "UNDER 50 pct but catalogued as an available year", "2026 in progress (excluded)"]:
    print("  {:<52} {}".format(k, buckets[k]))
print("  total files:", len(pf))

print()
print("=== every non-2026 file under 95 pct of its calendar year ===")
bad = sorted([r for r in rows if not r[2] and r[0] < 95.0], key=lambda r: r[0])
print("count:", len(bad))
print("{:<28} {:<8} {:>5} {:>6} {:>5} {:>8}  {}".format("station", "sensor", "year", "days", "cal", "pct", "span"))
for pct, f, _ in bad:
    print("{:<28} {:<8} {:>5} {:>6} {:>5} {:>7.1f}%  {}..{}".format(
        f["station"][0], f["tipo"][0], f["year"], f["distinct_dates"], f["calendar_days"], pct, f["first"], f["last"]))

print()
print("=== Oderzo 2024: all five sensors side by side ===")
for f in pf:
    if f["station"] and f["station"][0] == "Oderzo" and f["year"] == 2024:
        print("  {:<8} seq={} days={:>3}/{:<3} {}..{}".format(
            f["tipo"][0], f["codseq"], f["distinct_dates"], f["calendar_days"], f["first"], f["last"]))
print("  Oderzo 2025 for comparison:")
for f in pf:
    if f["station"] and f["station"][0] == "Oderzo" and f["year"] == 2025:
        print("  {:<8} seq={} days={:>3}/{:<3} {}..{}".format(
            f["tipo"][0], f["codseq"], f["distinct_dates"], f["calendar_days"], f["first"], f["last"]))
print("  Oderzo 2026 for comparison:")
for f in pf:
    if f["station"] and f["station"][0] == "Oderzo" and f["year"] == 2026:
        print("  {:<8} seq={} days={:>3}/{:<3} {}..{}".format(
            f["tipo"][0], f["codseq"], f["distinct_dates"], f["calendar_days"], f["first"], f["last"]))
