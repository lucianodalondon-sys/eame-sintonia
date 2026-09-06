"""
Second pass: attack the FINDING's own corrected value.

  A. Is the 6,056-date union GAPLESS over its own span, or does it have holes?
     (i.e. is 6,056 a thin scatter of days, or a complete daily calendar?)
  B. Is the union just Ponte di Piave's series re-labelled? Do the other 13
     stations add ANY calendar date the best station does not already have?
  C. Do all 82,125 rows actually carry a value? A null row is not an
     observation, so "82,125 station-days observed" would be overstated.
"""
import datetime as dt
import gzip
import json
import os
from collections import defaultdict

RAW = r"C:\disease-local-collection-italy\pilot-disease-local-collection\raw\F4-arpav-rest\tabella"

union = set()
station_dates = defaultdict(set)
station_names = {}
null_rows = []
empty_valore = 0
total = 0
bad_parse = 0

for fname in sorted(os.listdir(RAW)):
    if not fname.endswith(".json.gz"):
        continue
    with gzip.open(os.path.join(RAW, fname), "rt", encoding="utf-8") as fh:
        doc = json.load(fh)
    for r in doc.get("data") or []:
        if r.get("tipo") != "BFOGL":
            continue
        total += 1
        day = r["dataora"][:10]
        st = r.get("codice_stazione")
        station_names[st] = r.get("nome_stazione")
        union.add(day)
        station_dates[st].add(day)
        v = r.get("valore")
        if v is None or v == "" or v == "null":
            empty_valore += 1
            null_rows.append((fname, st, day, repr(v)))
            continue
        # valore is a JSON string like {"MINIMO":..,"MEDIO":..,"MASSIMO":..}
        try:
            inner = json.loads(v) if isinstance(v, str) else v
        except Exception:
            bad_parse += 1
            null_rows.append((fname, st, day, "UNPARSEABLE " + repr(v)[:60]))
            continue
        if isinstance(inner, dict):
            if not inner or all(x is None for x in inner.values()):
                empty_valore += 1
                null_rows.append((fname, st, day, "ALL-NULL " + repr(inner)[:60]))

lo, hi = min(union), max(union)
d0 = dt.date.fromisoformat(lo)
d1 = dt.date.fromisoformat(hi)
span = (d1 - d0).days + 1
missing = sorted({(d0 + dt.timedelta(days=i)).isoformat() for i in range(span)} - union)

print("=" * 70)
print("A. GAPLESSNESS OF THE UNION")
print("   union size                    :", len(union))
print("   span", lo, "..", hi, "= calendar days:", span)
print("   calendar days NOT in the union:", len(missing))
if missing:
    print("   first 15 missing              :", missing[:15])
print("   -> union is", "GAPLESS (a complete daily calendar)" if not missing else "NOT gapless")

print()
print("B. DOES ANY STATION ADD A DATE THE BEST STATION LACKS?")
best = max(station_dates, key=lambda s: len(station_dates[s]))
print("   best station:", best, station_names[best], "days =", len(station_dates[best]))
print("   union minus best station      :", len(union - station_dates[best]))
adds_any = False
for st in sorted(station_dates, key=lambda s: -len(station_dates[s])):
    extra = station_dates[st] - station_dates[best]
    if extra:
        adds_any = True
        print("   station", st, station_names[st], "adds", len(extra), "dates:", sorted(extra)[:5])
if not adds_any:
    print("   -> NO station adds a single calendar date beyond the best station.")
    print("      All 13 other stations are redundant for TEMPORAL coverage.")

print()
print("C. DO ALL BFOGL ROWS CARRY A VALUE?")
print("   BFOGL rows                    :", total)
print("   rows with null/empty value    :", empty_valore)
print("   rows with unparseable value   :", bad_parse)
if null_rows:
    for row in null_rows[:10]:
        print("     ", row)
print("   -> ", "every row carries a value" if not null_rows else "SOME ROWS DO NOT CARRY A VALUE")
print("=" * 70)
