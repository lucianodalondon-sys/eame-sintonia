import json, gzip, collections, datetime as dt

ROOT = r"C:/disease-local-collection-italy/pilot-disease-local-collection"
TAB = ROOT + "/raw/F4-arpav-rest/tabella/"
pf = json.load(open(r"C:/disease-local-collection-italy/audit-scratch/l3_perfile.json", encoding="utf-8"))
M = [json.loads(l) for l in open(ROOT + "/manifests/arpav-daily-manifest.jsonl", encoding="utf-8")]

cap = sorted(m["captured_at"] for m in M)
print("capture window of the daily pull:", cap[0], "..", cap[-1])
capday = dt.date.fromisoformat(cap[-1][:10])
elapsed = (capday - dt.date(2026, 1, 1)).days + 1
print("calendar days of 2026 elapsed at capture ({}): {}".format(capday, elapsed))
print("calendar days of 2026 in full:", 365)

y26 = [f for f in pf if f["year"] == 2026]
print("2026 files:", len(y26))
print("distinct dates per 2026 file: min {} max {}".format(min(f["distinct_dates"] for f in y26), max(f["distinct_dates"] for f in y26)))
print("elapsed-day shortfall (elapsed - preserved), per file: min {} max {}".format(
    elapsed - max(f["distinct_dates"] for f in y26), elapsed - min(f["distinct_dates"] for f in y26)))
print()
print("=== 'aggiornamento' the source itself stamps on the 2026 tables ===")
ag = collections.Counter()
for f in y26[:12]:
    doc = json.loads(gzip.open(TAB + f["file"], "rb").read().decode("utf-8"))
    ag[doc["data"][-1]["aggiornamento"]] += 1
print(dict(ag))
print()
print("=== 2026 per station, BFOGL ===")
for f in sorted([x for x in y26 if x["tipo"] == ["BFOGL"]], key=lambda x: x["station"][0]):
    gaps = elapsed - f["distinct_dates"]
    print("  {:<30} days={:>3}/{:<3} (Jan1..Jul31=212)  absent_vs_elapsed={}  {}..{}".format(
        f["station"][0], f["distinct_dates"], 365, gaps, f["first"], f["last"]))
print()
print("=== RADSOL: which stations, which years ===")
rs = collections.defaultdict(list)
for f in pf:
    if f["tipo"] == ["RADSOL"]:
        rs[f["station"][0]].append(f["year"])
for k in sorted(rs):
    ys = sorted(rs[k])
    print("  {:<30} {} yrs: {}-{} {}".format(k, len(ys), min(ys), max(ys),
          "CONTIGUOUS" if ys == list(range(min(ys), max(ys) + 1)) else "HOLES:" + str(sorted(set(range(min(ys), max(ys) + 1)) - set(ys)))))
print("  RADSOL stations:", len(rs), " files:", sum(len(v) for v in rs.values()))
