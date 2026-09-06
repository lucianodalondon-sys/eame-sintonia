"""Test the ONE sentence in the handoff that characterises the 241 partials:
   'A maior parte dos 241 e 2026, que ainda esta em curso.'
and test whether the per-station coverage table could reveal the Oderzo hole.
All counts re-derived from the raw gz files.
"""
import gzip
import json
import os
import calendar
import collections

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(ROOT, "raw", "F4-arpav-rest", "tabella")

recs = []
for fn in sorted(os.listdir(RAW)):
    if not fn.endswith(".json.gz"):
        continue
    codseq, yr = fn[:-8].replace(".json", "").split("_")
    yr = int(yr)
    with gzip.open(os.path.join(RAW, fn), "rb") as fh:
        d = json.loads(fh.read().decode("utf-8"))
    data = d.get("data") or []
    dates = {r["dataora"][:10] for r in data if r.get("dataora")}
    tipo = data[0]["tipo"] if data else "?"
    st = data[0]["nome_stazione"] if data else "?"
    cal = 366 if calendar.isleap(yr) else 365
    recs.append((st, tipo, yr, len(dates), cal, min(dates) if dates else None,
                 max(dates) if dates else None))

partial = [r for r in recs if r[3] < r[4]]
print("files with at least one calendar day missing:", len(partial))
n2026 = sum(1 for r in partial if r[2] == 2026)
print("  of those, year 2026:", n2026, "(%.1f%%)" % (100.0 * n2026 / len(partial)))
print("  of those, NOT 2026 :", len(partial) - n2026,
      "(%.1f%%)" % (100.0 * (len(partial) - n2026) / len(partial)))
print("  -> handoff says 'A maior parte dos 241 e 2026'. Majority = >50%.")
print("  -> 2026 share is %.1f%% : claim is %s" % (
    100.0 * n2026 / len(partial), "TRUE" if n2026 > len(partial) / 2 else "FALSE"))

print("\n=== Oderzo (196): every sensor x year, to see what the BFOGL-only table hides ===")
for r in sorted([x for x in recs if x[0] == "Oderzo"], key=lambda x: (x[2], x[1])):
    if x_flag := (r[3] < r[4]):
        pass
    mark = "  <-- " if r[3] / r[4] < 0.95 else ""
    if r[2] in (2023, 2024, 2025):
        print("  %-8s %4d  %4d/%3d  %5.1f%%  %s..%s%s" % (
            r[1], r[2], r[3], r[4], 100.0 * r[3] / r[4], r[5], r[6], mark))

print("\n=== does the BFOGL-only station table cover the sensors that are short? ===")
short = [r for r in recs if r[2] != 2026 and r[3] / r[4] < 0.95]
c = collections.Counter(r[1] for r in short)
print("  sensor types among the 10 short non-2026 files:", dict(c))
print("  BFOGL among them:", c.get("BFOGL", 0),
      "-> the other", sum(c.values()) - c.get("BFOGL", 0),
      "are sensors the handoff coverage table never measures")
