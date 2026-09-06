"""ADVERSARIAL AUDIT L3 - independent recount from the gz files themselves.

Reads NOTHING from the manifests. Everything derived from raw/ payloads.
Writes a JSON blob to stdout.
"""
import gzip, json, glob, os, sys, calendar, datetime as dt
from collections import defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TAB = os.path.join(ROOT, "raw", "F4-arpav-rest", "tabella")

NULLISH = {"", "null", "NULL", "None", "-", "--", "NaN", "nan", "N/A", "n/a", "NA", " "}

files = sorted(glob.glob(os.path.join(TAB, "*.json.gz")))
per_file = []
for p in files:
    base = os.path.basename(p)
    stem = base[:-len(".json.gz")]
    codseq_s, year_s = stem.split("_")
    codseq, year = int(codseq_s), int(year_s)
    raw = gzip.open(p, "rb").read()
    doc = json.loads(raw.decode("utf-8"))
    data = doc.get("data")
    success = doc.get("success")
    meta_total = (doc.get("meta") or {}).get("total")
    if data is None:
        per_file.append(dict(file=base, codseq=codseq, year=year, success=success,
                             data_is_none=True, rows=0))
        continue
    rows = len(data)
    dates = []
    nullish = 0
    missing_key = 0
    tipos, units, stations, stcodes = set(), set(), set(), set()
    for r in data:
        d = r.get("dataora")
        if d is not None:
            dates.append(d[:10])
        if "valore" not in r:
            missing_key += 1
        else:
            v = r["valore"]
            if v is None or (isinstance(v, str) and v.strip() in NULLISH):
                nullish += 1
        if r.get("tipo") is not None: tipos.add(r["tipo"])
        if r.get("unitnm") is not None: units.add(r["unitnm"])
        if r.get("nome_stazione") is not None: stations.add(r["nome_stazione"])
        if r.get("codice_stazione") is not None: stcodes.add(r["codice_stazione"])
    dset = set(dates)
    dup_dates = rows - len(dset)
    off_year = sorted(d for d in dset if not d.startswith(str(year)))
    cal_days = 366 if calendar.isleap(year) else 365
    per_file.append(dict(
        file=base, codseq=codseq, year=year, success=success, meta_total=meta_total,
        rows=rows, meta_total_matches=(meta_total == rows),
        distinct_dates=len(dset), dup_date_rows=dup_dates,
        nullish_values=nullish, missing_valore_key=missing_key,
        off_year_dates=off_year[:5], off_year_count=len(off_year),
        calendar_days=cal_days, short_by=cal_days - len(dset),
        first=min(dset) if dset else None, last=max(dset) if dset else None,
        tipo=sorted(tipos), unit=sorted(units),
        station=sorted(stations), station_code=sorted(stcodes),
        dates=sorted(dset),
    ))

out = sys.argv[1] if len(sys.argv) > 1 else "audit_l3_perfile.json"
with open(out, "w", encoding="utf-8") as fh:
    json.dump(per_file, fh, ensure_ascii=False)
print("wrote", out, len(per_file), "files")
