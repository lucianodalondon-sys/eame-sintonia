"""INDEPENDENT verification of the L3 'years is a union' finding.

Reads every preserved raw gz payload and derives (station, sensor tipo, year)
from the payload ITSELF -- not from any manifest. Then compares the per-sensor
station-year matrix against what daily-series-recount.json's sensor_types block
implies to a reader.
"""
import gzip
import json
import os
from collections import defaultdict

RAW = os.path.join(os.path.dirname(__file__), "..", "raw", "F4-arpav-rest", "tabella")
RECOUNT = os.path.join(os.path.dirname(__file__), "..", "manifests", "daily-series-recount.json")

files = sorted(f for f in os.listdir(RAW) if f.endswith(".json.gz"))
print("raw gz files on disk:", len(files))

# tipo -> station -> set(years)   (all derived from payload contents)
matrix = defaultdict(lambda: defaultdict(set))
tipo_files = defaultdict(int)
tipo_rows = defaultdict(int)
empty_files = []
fname_year_mismatch = []
multi_tipo_files = []
multi_station_files = []

for fn in files:
    with gzip.open(os.path.join(RAW, fn), "rt", encoding="utf-8", errors="replace") as fh:
        obj = json.load(fh)
    rows = obj.get("data") or []
    if not rows:
        empty_files.append(fn)
        continue
    tipos = {r.get("tipo") for r in rows}
    stations = {r.get("nome_stazione") for r in rows}
    years = {r["dataora"][:4] for r in rows if r.get("dataora")}
    if len(tipos) > 1:
        multi_tipo_files.append((fn, sorted(tipos)))
    if len(stations) > 1:
        multi_station_files.append((fn, sorted(stations)))
    tipo = sorted(tipos)[0]
    st = sorted(stations)[0]
    tipo_files[tipo] += 1
    tipo_rows[tipo] += len(rows)
    for y in years:
        matrix[tipo][st].add(int(y))
    # does the year inside match the year in the file name?
    fy = fn.rsplit("_", 1)[1].split(".")[0]
    if years != {fy}:
        fname_year_mismatch.append((fn, sorted(years)))

print("empty (zero-row) files:", len(empty_files))
print("files whose payload holds >1 tipo:", len(multi_tipo_files))
print("files whose payload holds >1 station:", len(multi_station_files))
print("files whose interior year(s) != filename year:", len(fname_year_mismatch))
for m in fname_year_mismatch[:5]:
    print("   ", m)

rec = json.load(open(RECOUNT, encoding="utf-8"))
st_block = rec["sensor_types"]

print()
print("=" * 78)
for tipo in ["TARIA2M", "UMID2M", "BFOGL", "RADSOL", "PREC"]:
    claimed = st_block[tipo]
    cy = claimed["years"]
    full = set(range(min(cy), max(cy) + 1))
    stations = matrix[tipo]
    print()
    print("%s  recount block says: files=%d rows=%d stations=%d years=%d-%d"
          % (tipo, claimed["files"], claimed["rows"], claimed["stations"], min(cy), max(cy)))
    print("   MY recount from raw: files=%d rows=%d stations=%d"
          % (tipo_files[tipo], tipo_rows[tipo], len(stations)))
    print("   naive read of the block (stations x years) = %d x %d = %d station-years"
          % (claimed["stations"], len(full), claimed["stations"] * len(full)))
    print("   station-years ACTUALLY held                 = %d"
          % sum(len(v) for v in stations.values()))
    short = []
    for st in sorted(stations):
        ys = stations[st]
        if ys != full:
            short.append((st, ys))
    print("   stations holding EVERY year %d-%d: %d of %d"
          % (min(cy), max(cy), len(stations) - len(short), len(stations)))
    for st, ys in short:
        gaps = sorted(full - ys)
        contiguous = ys == set(range(min(ys), max(ys) + 1))
        print("      SHORT: %-34s %d-%d (%d yrs, not %d)%s"
              % (st, min(ys), max(ys), len(ys), len(full),
                 "" if contiguous else "  [INTERNAL GAPS: %s]" % gaps))

print()
print("=" * 78)
print("Does the sensor_types block contain ANY per-station year info?")
for tipo in st_block:
    print("  ", tipo, "keys ->", sorted(st_block[tipo].keys()))
