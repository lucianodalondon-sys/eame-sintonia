import json, collections, os, re

rows = [json.loads(l) for l in open("manifests/arpav-daily-manifest.jsonl", encoding="utf-8") if l.strip()]
y26 = [r for r in rows if r["anno"] == 2026]

print("=== the source's OWN last-update stamp on 2026 files ===")
print("   aggiornamento values:", sorted(set(str(r.get("aggiornamento"))[:19] for r in y26)))
print("   last_date values    :", sorted(set(str(r.get("last_date"))[:10] for r in y26)))
print("   -> source updated 2026-08-25 but publishes only through 2026-07-31")

print("\n=== is there ANY label in the vocabulary for not-yet-existing / lag? ===")
vocab = collections.Counter(r.get("completeness") for r in rows)
print("  ", dict(vocab))
keys = set()
for r in rows: keys |= set(r.keys())
print("   manifest field names:", sorted(keys))

print("\n=== does the invented denominator propagate? grep expected_days / missing_days ===")
for fn in sorted(os.listdir("manifests")):
    p = os.path.join("manifests", fn)
    if not os.path.isfile(p): continue
    try:
        txt = open(p, encoding="utf-8", errors="replace").read()
    except Exception as e:
        print("  ", fn, "UNREADABLE", e); continue
    hits = []
    for tok in ("expected_days", "missing_days", "PARTIAL_SOURCE_GAP", "NOT_YET", "IN_PROGRESS", "coverage_pct", "completeness"):
        c = txt.count(tok)
        if c: hits.append("%s=%d" % (tok, c))
    if hits: print("   %-42s %s" % (fn, " ".join(hits)))

print("\n=== C4 window: does it touch 2026 at all? ===")
cm = json.load(open("manifests/collection-manifest.json", encoding="utf-8"))
flat = json.dumps(cm, ensure_ascii=False)
for m in sorted(set(re.findall(r"20\d\d-\d\d-\d\d", flat))):
    if m.startswith("2026"): print("   2026 date in collection-manifest:", m)
print("\n=== collection-manifest keys mentioning 2026 / coverage / complete ===")
def walk(o, path=""):
    if isinstance(o, dict):
        for k, v in o.items(): walk(v, path + "/" + str(k))
    elif isinstance(o, list):
        for i, v in enumerate(o[:200]): walk(v, path + "[%d]" % i)
    else:
        s = str(o)
        if ("2026" in s or "omplet" in s or "overage" in s or "365" in s) and ("2026" in s or "omplet" in s.lower() or "overage" in s.lower()):
            if len(s) < 400: print("   %-58s = %s" % (path[-58:], s))
walk(cm)
