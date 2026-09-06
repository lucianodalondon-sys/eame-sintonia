"""Second half of the L3 lens: within a span, is each YEAR complete?
Also: which 8 stations actually hold RADSOL, and are the short spans
contiguous truncations or gappy?
"""
import gzip
import json
import os
import calendar
from collections import defaultdict

RAW = os.path.join(os.path.dirname(__file__), "..", "raw", "F4-arpav-rest", "tabella")
files = sorted(f for f in os.listdir(RAW) if f.endswith(".json.gz"))

# tipo -> year -> set of (station, date)
days = defaultdict(lambda: defaultdict(set))
radsol_stations = set()
all_stations = set()

for fn in files:
    with gzip.open(os.path.join(RAW, fn), "rt", encoding="utf-8", errors="replace") as fh:
        obj = json.load(fh)
    for r in obj.get("data") or []:
        tipo = r.get("tipo")
        st = r.get("nome_stazione")
        d = r["dataora"][:10]
        all_stations.add(st)
        if tipo == "RADSOL":
            radsol_stations.add(st)
        days[tipo][int(d[:4])].add((st, d))

print("EDGE YEARS: are 2010 and 2026 complete years, per sensor?")
print("(distinct dates held / (stations holding that year x days in year))")
for tipo in ["TARIA2M", "UMID2M", "BFOGL", "RADSOL", "PREC"]:
    for y in (2010, 2025, 2026):
        pairs = days[tipo][y]
        sts = {s for s, _ in pairs}
        dates = {d for _, d in pairs}
        ydays = 366 if calendar.isleap(y) else 365
        if not sts:
            continue
        print("  %-8s %d: %d stations, %d distinct dates in year (max %d), "
              "last date %s, station-days %d of %d (%.1f%%)"
              % (tipo, y, len(sts), len(dates), ydays, max(dates),
                 len(pairs), len(sts) * ydays, 100.0 * len(pairs) / (len(sts) * ydays)))

print()
print("RADSOL is held by %d of the %d preserved stations. The %d WITHOUT it:"
      % (len(radsol_stations), len(all_stations), len(all_stations) - len(radsol_stations)))
for s in sorted(all_stations - radsol_stations):
    print("   -", s)
print("RADSOL stations:")
for s in sorted(radsol_stations):
    print("   +", s)
