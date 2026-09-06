"""Independent re-derivation of per-file year completeness.

Reads ONLY the raw gz files. Does not read the other auditor's script,
does not trust any manifest field. Year is taken from the DATA rows
(and cross-checked against the filename).
"""
import gzip
import json
import os
import calendar
import collections

RAW = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                   "raw", "F4-arpav-rest", "tabella")

rows = []
bad_year = []
for fn in sorted(os.listdir(RAW)):
    if not fn.endswith(".json.gz"):
        continue
    codseq, yr = fn[:-len(".json.gz")].split("_")
    yr = int(yr)
    with gzip.open(os.path.join(RAW, fn), "rb") as fh:
        d = json.loads(fh.read().decode("utf-8"))
    data = d.get("data") or []
    dates = set()
    years_in_data = set()
    tipo = set()
    station = set()
    for r in data:
        dt = r.get("dataora")
        if dt:
            dates.add(dt[:10])
            years_in_data.add(int(dt[:4]))
        if r.get("tipo"):
            tipo.add(r["tipo"])
        if r.get("nome_stazione"):
            station.add(r["nome_stazione"])
    if years_in_data and years_in_data != {yr}:
        bad_year.append((fn, sorted(years_in_data)))
    cal = 366 if calendar.isleap(yr) else 365
    rows.append({
        "file": fn,
        "codseq": int(codseq),
        "year": yr,
        "n_rows": len(data),
        "n_distinct_dates": len(dates),
        "cal_days": cal,
        "pct": 100.0 * len(dates) / cal,
        "first": min(dates) if dates else None,
        "last": max(dates) if dates else None,
        "tipo": "|".join(sorted(tipo)) or "?",
        "station": "|".join(sorted(station)) or "?",
    })

print("files opened:", len(rows))
print("files whose data-year != filename-year:", len(bad_year), bad_year[:5])

buckets = collections.Counter()
for r in rows:
    if r["year"] == 2026:
        buckets["2026 (in progress, excluded)"] += 1
    elif r["pct"] >= 99.995:
        buckets["100.0 pct"] += 1
    elif r["pct"] >= 99.0:
        buckets["99.0-99.9 pct"] += 1
    elif r["pct"] >= 95.0:
        buckets["95-99 pct"] += 1
    elif r["pct"] >= 90.0:
        buckets["90-95 pct"] += 1
    elif r["pct"] >= 50.0:
        buckets["50-90 pct"] += 1
    else:
        buckets["UNDER 50 pct"] += 1

print("\n=== my buckets (distinct dates / calendar days) ===")
for k in ["100.0 pct", "99.0-99.9 pct", "95-99 pct", "90-95 pct", "50-90 pct",
          "UNDER 50 pct", "2026 (in progress, excluded)"]:
    print("  %-34s %5d" % (k, buckets[k]))
print("  %-34s %5d" % ("TOTAL", len(rows)))

non2026 = [r for r in rows if r["year"] != 2026]
print("\nnon-2026 files:", len(non2026))
print("non-2026 at exactly 100pct:", sum(1 for r in non2026 if r["pct"] >= 99.995))
print("non-2026 short by 1..19 days:",
      sum(1 for r in non2026 if 1 <= (r["cal_days"] - r["n_distinct_dates"]) <= 19))
print("non-2026 below 95pct:", sum(1 for r in non2026 if r["pct"] < 95.0))
print("non-2026 below 50pct:", sum(1 for r in non2026 if r["pct"] < 50.0))

print("\n=== every non-2026 file under 95 pct ===")
short = sorted([r for r in non2026 if r["pct"] < 95.0],
               key=lambda r: r["pct"])
for r in short:
    print("%-30s %-8s %4d  %4d/%3d  %5.1f%%  %s..%s  rows=%d" % (
        r["station"][:30], r["tipo"], r["year"], r["n_distinct_dates"],
        r["cal_days"], r["pct"], r["first"], r["last"], r["n_rows"]))

print("\n=== worst non-2026 ===")
w = short[0]
print(w["file"], w["station"], w["tipo"], w["year"],
      "%d/%d = %.1f%%" % (w["n_distinct_dates"], w["cal_days"], w["pct"]),
      w["first"], w["last"])
