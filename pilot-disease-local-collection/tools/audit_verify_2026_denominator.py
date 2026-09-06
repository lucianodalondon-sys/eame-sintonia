import json, collections

M = "manifests/arpav-daily-manifest.jsonl"
rows = [json.loads(l) for l in open(M, encoding="utf-8") if l.strip()]
print("total manifest lines:", len(rows))

# 1. expected_days distribution per year, over ALL files
byyear = collections.defaultdict(collections.Counter)
for r in rows:
    byyear[r["anno"]][r.get("expected_days")] += 1
print("\n=== expected_days by year (ALL files) ===")
for y in sorted(byyear):
    print("   %s  %s   n=%d" % (y, dict(byyear[y]), sum(byyear[y].values())))

# 2. is the denominator even the right calendar length?
def is_leap(y): return y % 4 == 0 and (y % 100 != 0 or y % 400 == 0)
print("\n=== expected_days vs calendar length of that year ===")
bad = collections.Counter()
for r in rows:
    cal = 366 if is_leap(r["anno"]) else 365
    if r.get("expected_days") != cal:
        bad[(r["anno"], r.get("expected_days"), cal)] += 1
for k, v in sorted(bad.items()):
    print("   year=%s expected_days=%s calendar=%s count=%d" % (k[0], k[1], k[2], v))
if not bad:
    print("   (none - all equal calendar length)")

# 3. the 2026 files in full
print("\n=== every 2026 file ===")
y26 = [r for r in rows if r["anno"] == 2026]
print("count:", len(y26))
for r in sorted(y26, key=lambda x: x["stazione"]):
    print("   %-42s rows=%4d exp=%s miss=%s first=%s last=%s %s" % (
        r["stazione"][:42], r["rows"], r.get("expected_days"), r.get("missing_days"),
        str(r.get("first_date"))[:10], str(r.get("last_date"))[:10], r.get("completeness")))

# 4. arithmetic check + last_date distribution
print("\n=== 2026 aggregates ===")
print("   distinct expected_days :", sorted(set(r.get("expected_days") for r in y26)))
print("   distinct last_date     :", sorted(set(str(r.get("last_date"))[:10] for r in y26)))
print("   distinct completeness  :", collections.Counter(r.get("completeness") for r in y26))
print("   rows min/max           :", min(r["rows"] for r in y26), max(r["rows"] for r in y26))
print("   missing_days min/max   :", min(r["missing_days"] for r in y26), max(r["missing_days"] for r in y26))
print("   check exp-rows==miss ? :", all(r["expected_days"] - r["rows"] == r["missing_days"] for r in y26))

# 5. capture dates
print("\n=== captured_at range over 2026 files ===")
caps = sorted(set(r["captured_at"][:10] for r in y26))
print("   ", caps)
print("=== captured_at range over ALL files ===")
allcaps = sorted(set(r["captured_at"][:10] for r in rows))
print("   ", allcaps)

# 6. how many completeness labels exist overall, and what vocabulary
print("\n=== completeness vocabulary over ALL 1038 ===")
for k, v in collections.Counter(r.get("completeness") for r in rows).most_common():
    print("   %-24s %d" % (k, v))
