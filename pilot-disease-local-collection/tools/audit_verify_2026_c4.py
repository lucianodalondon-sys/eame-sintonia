import json

cm = json.load(open("manifests/collection-manifest.json", encoding="utf-8"))
lw = cm["LEAF_WETNESS_WINDOW_COVERAGE"]
print("=== LEAF_WETNESS_WINDOW_COVERAGE[0] full record ===")
print(json.dumps(lw[0], ensure_ascii=False, indent=2)[:2500])

print("\n=== every station: coverage_pct and the 2026 artifact ===")
for e in lw:
    print("   %-34s cov=%-8s short=%s" % (
        str(e.get("station"))[:34], e.get("coverage_pct"), e.get("short_years_missing_days")))

print("\n=== keys anywhere in collection-manifest naming the window ===")
for k, v in cm.items():
    if isinstance(v, str) and ("2014" in v or "2025-10" in v):
        print("   %s = %s" % (k, v))
    if "WINDOW" in k.upper() and isinstance(v, (str, int)):
        print("   %s = %s" % (k, v))

print("\n=== daily-series-recount.json: does coverage_pct there include 2026? ===")
rc = json.load(open("manifests/daily-series-recount.json", encoding="utf-8"))
print("   top-level type:", type(rc), (list(rc.keys()) if isinstance(rc, dict) else len(rc)))
if isinstance(rc, dict):
    for k, v in rc.items():
        if not isinstance(v, (list, dict)):
            print("   %s = %s" % (k, v))
