# Corroboration: where exactly are Castelfranco's 27 missing BFOGL days?
# And is 4236 an artifact of ignoring a second series? Read-only.
import gzip, json, os, datetime, collections

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TAB = os.path.join(ROOT, "raw", "F4-arpav-rest", "tabella")
W0, W1 = datetime.date(2014, 3, 1), datetime.date(2025, 10, 31)

held = set()
rows_total = 0
series = collections.Counter()   # distinct (file) contributing BFOGL for station 102
dup = collections.Counter()
for fn in sorted(os.listdir(TAB)):
    if not fn.endswith(".json.gz"):
        continue
    with gzip.open(os.path.join(TAB, fn), "rt", encoding="utf-8", errors="replace") as fh:
        obj = json.load(fh)
    for r in obj.get("data") or []:
        if r.get("tipo") != "BFOGL" or r.get("codice_stazione") != 102:
            continue
        dt = (r.get("dataora") or "")[:10]
        dd = datetime.date(int(dt[0:4]), int(dt[5:7]), int(dt[8:10]))
        if W0 <= dd <= W1:
            rows_total += 1
            dup[dd] += 1
            held.add(dd)
            series[fn] += 1

print("Castelfranco (102) BFOGL, window 2014-03-01..2025-10-31")
print("  raw BFOGL rows in window :", rows_total)
print("  DISTINCT days in window  :", len(held))
print("  duplicate days (row appears >1x):", sum(1 for v in dup.values() if v > 1))
print("  distinct gz files contributing  :", len(series))
print()

want = set()
d = W0
while d <= W1:
    want.add(d)
    d += datetime.timedelta(days=1)
missing = sorted(want - held)
print("  window days:", len(want), " held:", len(held), " MISSING:", len(missing))
by_year = collections.Counter(m.year for m in missing)
print("  missing by year:", dict(sorted(by_year.items())))
print("  missing dates:", ", ".join(str(m) for m in missing))
print()
k = 0
while 100.0 * k / len(want) < 99.4:
    k += 1
print(f"  days required for a TRUE 99.4%: {k}  (held {len(held)}, short by {k-len(held)})")
print(f"  exact pct: {100.0*len(held)/len(want):.10f}")
