#!/usr/bin/env python3
"""RT6-J2. Is the 18.18% Siena visit real, or a small-denominator artefact?
And what does the source's own legend actually say?"""
import os, sys, json, datetime as dt
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "engine"))
import di_core
CASE = os.path.abspath(os.path.join(HERE, "..", "..", "DISEASE-INTELLIGENCE-ITALY",
                                    "CASES", "OLIVO-BACTROCERA-TOSCANA"))
AS_OF = dt.date(2026, 9, 6)
M = "ACTIVE_INFESTATION_COUNT"
sheet = di_core.load_sheet()
print("THE SOURCE'S OWN LEGEND, as declared in the semantic sheet:")
print(json.dumps(sheet["SOURCE_ACTION_BANDS"], indent=1, ensure_ascii=False))
for k in sheet:
    if "TRAP" in k.upper() or "UNIT" in k.upper():
        print(f"\n{k}: {json.dumps(sheet[k], indent=1, ensure_ascii=False)[:900]}")

loaded = di_core.load_visits(CASE, sheet, AS_OF)
lo, hi = AS_OF - dt.timedelta(days=27), AS_OF
rows = []
for v in loaded["visits"]:
    if not v["usable_for_rates"]:
        continue
    d = dt.date.fromisoformat(v["observation_date"])
    if not (lo <= d <= hi):
        continue
    c = v["measurements"][M]["value"]
    n = v["measurements"]["SAMPLE_SIZE / DENOMINATOR"]["value"]
    if c is None or not n:
        continue
    rows.append((100.0*c/n, v["province"], v["comune"], v["observation_date"],
                 int(c), int(n), v["org"]))
rows.sort(reverse=True)
print(f"\nTOP 12 SINGLE VISITS IN THE 28-DAY WINDOW, by rate ({len(rows)} usable visits):")
print(f"{'rate%':>8s} {'prov':14s} {'comune':22s} {'date':11s} {'inf/n':>10s}  band")
for r in rows[:12]:
    b = di_core.band_for(sheet, r[0])
    print(f"{r[0]:8.3f} {r[1]:14s} {str(r[2])[:22]:22s} {r[3]:11s} "
          f"{str(r[4])+'/'+str(r[5]):>10s}  {b['label']} ({b['meaning']})")

for thr, name in ((6.0, "above the green band"), (10.0, "in the source's RED band")):
    n = sum(1 for r in rows if r[0] >= thr)
    prov = sorted({r[1] for r in rows if r[0] >= thr})
    print(f"\nvisits {name} (>= {thr}%): {n} of {len(rows)}  in provinces {prov}")
    dr = sum(r[5] for r in rows if r[0] >= thr)
    print(f"  those visits carry {dr} sampled drupes of "
          f"{sum(r[5] for r in rows)} in the window")
print("\nthe region card prints:  bandas da fonte: {'green': 10}")
print("  -> that dict is the band of the POOLED PROVINCIAL RATE, 10 of 10 green.")
print("  -> the engine also computed per_visit_rate_pct_max for every province and")
print("     never printed it. See rt6_suppressed.py.")
