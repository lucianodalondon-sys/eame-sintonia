import json, datetime, gzip
d = datetime.date

print("=== C4 window length ===")
print("   2014-03-01..2025-10-31 inclusive =", (d(2025,10,31)-d(2014,3,1)).days + 1)

rc = json.load(open("manifests/daily-series-recount.json", encoding="utf-8"))
print("\n=== recount 'window' block ===")
print(json.dumps(rc["window"], ensure_ascii=False, indent=2)[:1200])

print("\n=== recompute window coverage MYSELF from raw files, for Conegliano leaf wetness ===")
man = [json.loads(l) for l in open("manifests/arpav-daily-manifest.jsonl", encoding="utf-8") if l.strip()]
tgt = [r for r in man if r["stazione"].startswith("Conegliano") and r["tipo"] == "BFOGL"]
lo, hi = d(2014,3,1), d(2025,10,31)
days = set()
for r in tgt:
    o = json.load(gzip.open(r["raw_path"], "rt", encoding="utf-8"))
    for x in o["data"]:
        dt = d.fromisoformat(x["dataora"][:10])
        if lo <= dt <= hi:
            days.add(dt)
print("   files for this station/sensor :", len(tgt))
print("   distinct days inside window   :", len(days))
print("   window length                 :", (hi-lo).days + 1)
print("   coverage                      : %.2f%%" % (100.0*len(days)/((hi-lo).days+1)))
print("   manifest says days_in_window  : 4255 / 4263 = 99.81%")
print("   any 2026 day inside window?   :", any(x.year == 2026 for x in days))
