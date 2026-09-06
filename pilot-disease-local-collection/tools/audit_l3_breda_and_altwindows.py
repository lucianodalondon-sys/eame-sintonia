import json, collections, datetime as dt

RC = json.load(open(r"C:/disease-local-collection-italy/pilot-disease-local-collection/manifests/daily-series-recount.json", encoding="utf-8"))
pf = json.load(open(r"C:/disease-local-collection-italy/audit-scratch/l3_perfile.json", encoding="utf-8"))

print("=== recount leaf_wetness entries: catalog_years vs years_preserved ===")
for e in RC["leaf_wetness"]:
    cy, yp = e["catalog_years"], e["years_preserved"]
    gap = sorted(set(cy) - set(yp))
    print("{:<34} catalog {}-{} ({}) preserved {}-{} ({}) not_preserved={} short_years={}".format(
        e["stazione"], min(cy), max(cy), len(cy), min(yp), max(yp), len(yp), gap,
        e.get("short_years_missing_days")))

print()
print("=== jobs file: what was PLANNED for BFOGL ===")
J = json.load(open(r"C:/disease-local-collection-italy/pilot-disease-local-collection/manifests/arpav-jobs.json", encoding="utf-8"))
print("type:", type(J).__name__, ("keys: " + str(list(J.keys()))) if isinstance(J, dict) else ("len " + str(len(J))))
jobs = J if isinstance(J, list) else (J.get("jobs") or J.get("items"))
print("jobs:", len(jobs))
print("sample job:", json.dumps(jobs[0], ensure_ascii=False))
bf = [j for j in jobs if str(j.get("tipo") or j.get("VARIABLE_CODE") or "") == "BFOGL"]
print("planned BFOGL jobs:", len(bf))
byst = collections.Counter()
for j in bf:
    byst[j.get("stazione")] += 1
for s, n in sorted(byst.items()):
    print("  planned {:>3}  {}".format(n, s))

print()
print("=== alternative windows, BFOGL, distinct dates present ===")
bfp = [f for f in pf if f["tipo"] == ["BFOGL"]]
have = collections.defaultdict(set); name = {}
for f in bfp:
    k = f["station_code"][0]; name[k] = f["station"][0]
    have[k] |= set(f["dates"])

def span(a, b):
    a, b = dt.date.fromisoformat(a), dt.date.fromisoformat(b)
    return set((a + dt.timedelta(i)).isoformat() for i in range((b - a).days + 1))

W1 = span("2014-03-01", "2025-10-31")   # the claimed window
W2 = span("2014-03-01", "2025-12-31")   # same start, calendar year end
W3 = span("2010-01-01", "2025-12-31")   # full preserved history excl in-progress 2026
print("{:<30} {:>14} {:>16} {:>16}".format("station", "claimed_win", "to_2025-12-31", "2010-2025_full"))
for k in sorted(have, key=lambda x: name[x]):
    print("{:<30} {:>7}/{:<6} {:>8}/{:<7} {:>8}/{:<7}".format(
        name[k], len(have[k] & W1), len(W1), len(have[k] & W2), len(W2), len(have[k] & W3), len(W3)))
print()
for label, W in (("claimed 2014-03-01..2025-10-31", W1), ("2014-03-01..2025-12-31", W2), ("2010-01-01..2025-12-31", W3)):
    n = sum(1 for k in have if 100.0 * len(have[k] & W) / len(W) >= 99.4)
    print("stations >=99.4 pct under {}: {} of {}".format(label, n, len(have)))
