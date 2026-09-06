"""
INDEPENDENT re-derivation of C4 leaf-wetness window coverage.
Written from scratch. Reads ONLY the raw gzip files, never the collector's
recount, never the other auditor's script.

Method:
  1. open every *.json.gz under raw/F4-arpav-rest/tabella/
  2. keep only rows whose sensor code (tipo) == BFOGL
  3. group by codice_stazione; build the SET of distinct calendar dates
  4. window = 2014-03-01 .. 2025-10-31 inclusive
  5. coverage = |dates & window| / |window|
"""
import gzip, json, os, datetime, collections

TAB = os.path.join(os.path.dirname(__file__), "..", "raw", "F4-arpav-rest", "tabella")
TAB = os.path.abspath(TAB)

W0 = datetime.date(2014, 3, 1)
W1 = datetime.date(2025, 10, 31)
window = set()
d = W0
while d <= W1:
    window.add(d)
    d += datetime.timedelta(days=1)
print("window days (built by day-stepping):", len(window))
print("cross-check by subtraction     :", (W1 - W0).days + 1)

station_dates = collections.defaultdict(set)   # station -> set of dates (BFOGL)
station_name = {}
station_files = collections.Counter()
station_rows = collections.Counter()
bfogl_files = []
dupe_rows = collections.Counter()              # station -> repeated (date) rows

allfiles = sorted(f for f in os.listdir(TAB) if f.endswith(".json.gz"))
print("total .json.gz files:", len(allfiles))

for fn in allfiles:
    with gzip.open(os.path.join(TAB, fn), "rt", encoding="utf-8") as fh:
        doc = json.load(fh)
    rows = doc.get("data") or []
    if not rows:
        continue
    tipos = {r.get("tipo") for r in rows}
    if "BFOGL" not in tipos:
        continue
    if tipos != {"BFOGL"}:
        print("  !! MIXED SENSOR FILE", fn, tipos)
    bfogl_files.append(fn)
    for r in rows:
        if r.get("tipo") != "BFOGL":
            continue
        st = r["codice_stazione"]
        station_name[st] = r.get("nome_stazione")
        station_files[st] += 0
        station_rows[st] += 1
        dt = datetime.date.fromisoformat(r["dataora"][:10])
        if dt in station_dates[st]:
            dupe_rows[st] += 1
        station_dates[st].add(dt)
    st = rows[0]["codice_stazione"]
    station_files[st] += 1

print("BFOGL files:", len(bfogl_files))
print("BFOGL rows :", sum(station_rows.values()))
print("BFOGL stations:", len(station_dates))
print()

res = []
for st, dates in station_dates.items():
    inwin = len(dates & window)
    pct = 100.0 * inwin / len(window)
    res.append((pct, inwin, st, station_name[st]))
res.sort(reverse=True)

ge994 = ge993 = 0
print(f"{'pct(exact)':>13}  {'days':>9}  station")
for pct, inwin, st, nm in res:
    flag = ""
    if pct >= 99.4:
        ge994 += 1
    else:
        flag = "  << BELOW 99.4"
    if pct >= 99.3:
        ge993 += 1
    print(f"{pct:13.6f}  {inwin:4d}/{len(window)}  {nm} ({st}){flag}")

print()
print("stations >= 99.4% :", ge994, "of", len(res))
print("stations >= 99.3% :", ge993, "of", len(res))
print()
print("duplicate (station,date) BFOGL rows:", dict(dupe_rows) or "none")
print("rows per station total:", dict(station_rows))
