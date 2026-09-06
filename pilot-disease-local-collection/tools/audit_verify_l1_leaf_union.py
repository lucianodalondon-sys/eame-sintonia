"""
INDEPENDENT verification of the L1 finding on C3 leaf wetness (BFOGL).

Does NOT trust manifests. Opens every one of the raw daily gzip files and reads
`tipo` / `codice_stazione` / `dataora` straight out of the payload.

Questions answered:
  Q1 how many BFOGL rows exist in the raw files?
  Q2 does any single file repeat a calendar date?
  Q3 how many distinct calendar dates in the UNION across all BFOGL files?
  Q4 how many distinct stations carry BFOGL?
  Q5 is each row really one distinct (station, date) pair -- i.e. do two
     different sensor ids for the SAME station cover the same day twice?
"""
import gzip
import json
import os
from collections import Counter, defaultdict

RAW = r"C:\disease-local-collection-italy\pilot-disease-local-collection\raw\F4-arpav-rest\tabella"

rows_by_tipo = Counter()
bfogl_rows = 0
bfogl_files = []
dates_per_file = {}          # fname -> list of date strings (with repeats kept)
union_dates = set()          # all distinct calendar dates, any station
station_dates = defaultdict(set)   # station code -> set of dates
station_date_pairs = 0       # total rows, to compare against distinct pairs
pair_counter = Counter()     # (station, date) -> how many rows
station_names = {}
station_sensorids = defaultdict(set)   # station -> set of file sensor ids
units = Counter()
years = set()

for fname in sorted(os.listdir(RAW)):
    if not fname.endswith(".json.gz"):
        continue
    path = os.path.join(RAW, fname)
    with gzip.open(path, "rt", encoding="utf-8") as fh:
        doc = json.load(fh)
    data = doc.get("data") or []
    tipos_here = {r.get("tipo") for r in data}
    for t in tipos_here:
        pass
    # count every row by tipo (for the global picture)
    for r in data:
        rows_by_tipo[r.get("tipo")] += 1
    if "BFOGL" not in tipos_here:
        continue
    # this file carries leaf wetness
    bfogl_files.append(fname)
    sensor_id, year = fname.replace(".json.gz", "").split("_")
    years.add(int(year))
    d_list = []
    for r in data:
        if r.get("tipo") != "BFOGL":
            continue
        bfogl_rows += 1
        day = r["dataora"][:10]
        st = r.get("codice_stazione")
        station_names[st] = r.get("nome_stazione")
        station_sensorids[st].add(sensor_id)
        d_list.append(day)
        union_dates.add(day)
        station_dates[st].add(day)
        pair_counter[(st, day)] += 1
        station_date_pairs += 1
        units[r.get("unitnm")] += 1
    dates_per_file[fname] = d_list

print("=" * 70)
print("Q1  BFOGL rows counted straight out of the raw gzip files :", bfogl_rows)
print("    BFOGL files                                          :", len(bfogl_files))
print("    year range                                           :", min(years), "..", max(years))
print("    units seen                                           :", dict(units))

# Q2 -- does any single file repeat a date?
repeat_files = {f: len(v) - len(set(v)) for f, v in dates_per_file.items() if len(v) != len(set(v))}
print()
print("Q2  files whose OWN dates repeat                          :", len(repeat_files))
if repeat_files:
    for f, n in list(repeat_files.items())[:10]:
        print("      ", f, "extra rows:", n)
in_file_distinct = sum(len(set(v)) for v in dates_per_file.values())
print("    sum of per-file DISTINCT dates                        :", in_file_distinct)

# Q3 -- the union
print()
print("Q3  UNION of distinct calendar dates across all stations  :", len(union_dates))
print("    earliest / latest date                                :", min(union_dates), "/", max(union_dates))

# Q4 -- stations
print()
print("Q4  distinct stations carrying BFOGL                      :", len(station_dates))
for st in sorted(station_dates, key=lambda s: -len(station_dates[s])):
    print("      %-8s %-38s days=%5d sensor_ids=%s"
          % (st, station_names[st], len(station_dates[st]),
             ",".join(sorted(station_sensorids[st]))))

# Q5 -- is a row really a distinct station-day?
distinct_pairs = len(pair_counter)
dupes = {k: v for k, v in pair_counter.items() if v > 1}
print()
print("Q5  total BFOGL rows                                      :", station_date_pairs)
print("    DISTINCT (station, date) pairs                        :", distinct_pairs)
print("    (station, date) pairs appearing more than once         :", len(dupes))
if dupes:
    extra = sum(v - 1 for v in dupes.values())
    print("    surplus rows caused by repeated station-days           :", extra)
    for k, v in list(sorted(dupes.items()))[:10]:
        print("      station", k[0], k[1], "->", v, "rows")

print()
print("ARITHMETIC CHECK  sum over stations of their distinct days :",
      sum(len(v) for v in station_dates.values()))
print("=" * 70)
