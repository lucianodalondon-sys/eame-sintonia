#!/usr/bin/env python3
"""RT3-08
  a) Is nome_area the province of the FIELD or of the recording ORGANISATION?
     If it were the org's, an org would never appear in two provinces.
  b) Is the province string normalised anywhere? What happens to a case/whitespace variant?
  c) Is any Tuscan province silently missing, and could a reader tell?
  d) Can an observation be published under a province that is not in Tuscany at all?
"""
import collections, os, sys, copy, datetime as dt

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.abspath(os.path.join(HERE, "..", "engine")))
sys.path.insert(0, HERE)
import rt3_lib as L
import di_core, di_observe, di_render, di_adama

AS_OF = dt.date(2026, 9, 6)
METRIC = "ACTIVE_INFESTATION_COUNT"

print("=" * 78)
print("RT3-08a  is nome_area the province of the FIELD or of the ORGANISATION?")
print("=" * 78)
R = L.visit_rows()
org_prov = collections.defaultdict(collections.Counter)
org_com = collections.defaultdict(set)
idorg_prov = collections.defaultdict(collections.Counter)
prov_org = collections.defaultdict(collections.Counter)
for r in R.values():
    o = str(r.get("org_name"))
    p = str(r.get("nome_area"))
    org_prov[o][p] += 1
    idorg_prov[str(r.get("id_org"))][p] += 1
    org_com[o].add(L.admin6(r.get("admin_code")))
    prov_org[p][o] += 1
print(f"\n{'org_name':16s} {'id_org':>7} {'provinces':>9} {'comuni':>7}  breakdown")
for o in sorted(org_prov, key=lambda x: -sum(org_prov[x].values())):
    ids = sorted({str(r.get("id_org")) for r in R.values() if str(r.get("org_name")) == o})
    print(f"{o:16s} {','.join(ids):>7} {len(org_prov[o]):>9} {len(org_com[o]):>7}  "
          f"{dict(org_prov[o].most_common())}")
multi = [o for o in org_prov if len(org_prov[o]) > 1]
print(f"\norganisations recording in more than one province: {len(multi)} of {len(org_prov)}")
print(f"provinces served by more than one organisation    : "
      f"{sum(1 for p in prov_org if len(prov_org[p])>1)} of {len(prov_org)}")
print("\n  -> nome_area cannot be the organisation's own province: the same organisation")
print("     files rows under several provinces, and each province is served by several")
print("     organisations. It tracks the FIELD. (It matches admin_code on 77,850/79,251.)")
print("\n  id_org -> province, for completeness:")
for i in sorted(idorg_prov, key=lambda x: (x == "None", int(x) if x != "None" else 0)):
    print(f"    id_org {i:>3}: {len(idorg_prov[i])} province(s) {dict(idorg_prov[i])}")

# ---------------------------------------------------------------------------
print("\n" + "=" * 78)
print("RT3-08b/c/d  the province LABEL is a raw pass-through string")
print("=" * 78)
sheet = di_core.load_sheet()
adama = di_adama.relevance("Olive", "Olive Fruit Fly")
loaded = di_core.load_visits(L.CASE, sheet, AS_OF)

import re
eng = open(os.path.join(HERE, "..", "engine", "di_observe.py"), encoding="utf-8").read() + \
      open(os.path.join(HERE, "..", "engine", "di_core.py"), encoding="utf-8").read() + \
      open(os.path.join(HERE, "..", "engine", "di_report.py"), encoding="utf-8").read() + \
      open(os.path.join(HERE, "..", "engine", "run_pilot.py"), encoding="utf-8").read() + \
      open(os.path.join(HERE, "..", "engine", "di_render.py"), encoding="utf-8").read()
for tok in ["Massa-Carrara", "PROVINCES", "10 provinc", ".strip()", ".upper()", ".title()",
            "admin_code", "lat", "lon"]:
    print(f"  token {tok!r} appears in the engine source: {eng.count(tok)} time(s)")
print("  (the only province list anywhere is derived from the data itself:")
print("   run_pilot/di_report both do  sorted({v['province'] for v in visits if v['province']}) )")

def run(vs):
    provs = sorted({v["province"] for v in vs if v["province"]})
    return [dict(di_observe.cell(vs, sheet, p, METRIC, AS_OF), adama=adama) for p in provs]

# b) a case variant splits a province in two
v = copy.deepcopy(loaded["visits"])
n = 0
for x in v:
    if x["province"] == "Siena" and x["observation_date"] >= "2026-08-24":
        x["province"] = "SIENA "
        n += 1
cells = run(v)
print(f"\n  b) {n} recent Siena visits relabelled 'SIENA ' (upper case + trailing space)")
print(f"     provinces published: {[c['province'] for c in cells]}")
for c in cells:
    if c["province"] in ("Siena", "SIENA "):
        print(f"       {c['province']!r:10s} rate={c['observation'].get('value_pct')} "
              f"n_vis={c['observation'].get('n_visits')} "
              f"hist={c['analysis']['historical_state']} "
              f"pub={c['quality']['observation_publishable']}")

# c) a missing province
base = run(loaded["visits"])
print("\n  c) BASELINE regional report header:")
for line in di_render.render_region(base, adama).splitlines()[:6]:
    print("       " + line)
print(f"     baseline rising provinces: "
      f"{[c['province'] for c in base if c['analysis']['observed_trend']=='INCREASING_OBSERVED']}")
v2 = [x for x in copy.deepcopy(loaded["visits"]) if x["province"] != "Lucca"]
c2 = run(v2)
print(f"\n     with every Lucca row simply absent from the feed:")
for line in di_render.render_region(c2, adama).splitlines()[:6]:
    print("       " + line)
print(f"     rising provinces now: "
      f"{[c['province'] for c in c2 if c['analysis']['observed_trend']=='INCREASING_OBSERVED']}")

# d) a province outside Tuscany
v3 = copy.deepcopy(loaded["visits"])
n = 0
for x in v3:
    if x["province"] == "Pistoia":
        x["province"] = "Bologna"
        n += 1
c3 = run(v3)
b = next(c for c in c3 if c["province"] == "Bologna")
print(f"\n  d) {n} Pistoia visits relabelled 'Bologna' (Emilia-Romagna, not Tuscany)")
print(f"     published cell: country={b['country']} region={b['region']} "
      f"province={b['province']} publishable={b['quality']['observation_publishable']}")
print("     rendered headline:")
print("       " + di_render.render_province(b, adama, di_adama.attention_class(b, adama))
      .splitlines()[0])
