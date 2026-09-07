#!/usr/bin/env python3
"""RT3-10  A REAL row in the wrong province.

id_field 4553 is filed under comune 051034 SANSEPOLCRO, province Arezzo, but its coordinate
sits ~110 km west. Which comune is that coordinate actually nearest to, and does the row
reach a published number?
"""
import collections, math, os, sys, statistics, datetime as dt

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.abspath(os.path.join(HERE, "..", "engine")))
sys.path.insert(0, HERE)
import rt3_lib as L
import di_core, di_observe

def hav(a, b):
    R = 6371000.0
    p1, p2 = math.radians(a[0]), math.radians(b[0])
    h = (math.sin((p2 - p1) / 2) ** 2 + math.cos(p1) * math.cos(p2) *
         math.sin(math.radians(b[1] - a[1]) / 2) ** 2)
    return 2 * R * math.asin(math.sqrt(h))

def pt(r):
    la, lo = L.fnum(r.get("lat")), L.fnum(r.get("lon"))
    if la is None or lo is None: return None
    return (la, lo) if 42.2 <= la <= 44.5 and 9.6 <= lo <= 12.45 else None

R = L.visit_rows()
com_pts = collections.defaultdict(list)
nm, pv = {}, {}
for r in R.values():
    c = L.admin6(r.get("admin_code"))
    nm[c] = str(r.get("name_4")).strip(); pv[c] = str(r.get("nome_area"))
    p = pt(r)
    if p: com_pts[c].append(p)
med = {c: (statistics.median([q[0] for q in v]), statistics.median([q[1] for q in v]))
       for c, v in com_pts.items()}

seq = sorted((str(d), r) for (i, d), r in R.items() if i == 4553)
print("=" * 78)
print("RT3-10  id_field 4553")
print("=" * 78)
r0 = seq[0][1]
p0 = pt(r0)
print(f"  filed as   : comune {L.admin6(r0.get('admin_code'))} {r0.get('name_4')}, "
      f"province {r0.get('nome_area')}, sub-area {r0.get('name_5')!r}")
print(f"  site name  : {r0.get('name')!r}   org {r0.get('org_name')!r}")
print(f"  coordinate : {p0}")
print(f"  visits     : {len(seq)}  {seq[0][0]} .. {seq[-1][0]}")
near = sorted(((hav(p0, m), c) for c, m in med.items() if c != '051034'))[:8]
print("\n  nearest comuni to that coordinate (median point of each comune's own rows):")
for d, c in near:
    print(f"    {d/1000:>7.1f} km  {c} {nm[c]:26s} province {pv[c]}")
print(f"\n  distance to the median point of 051034 SANSEPOLCRO itself: "
      f"{hav(p0, med['051034'])/1000:.1f} km")
print("  -> the row says Arezzo. The coordinate is in the Firenze/Lucca plain.")
print("     The engine reads nome_area only, so it publishes it as Arezzo.")

# does it reach a number?
AS_OF = dt.date(2026, 9, 6)
sheet = di_core.load_sheet()
loaded = di_core.load_visits(L.CASE, sheet, AS_OF)
c = di_observe.cell(loaded["visits"], sheet, "Arezzo", "ACTIVE_INFESTATION_COUNT", AS_OF)
print(f"\n  Arezzo baseline seasons published: {c['analysis']['baseline_seasons']}")
yrs = {int(d[:4]) for d, _ in seq}
print(f"  seasons this grove appears in     : {sorted(yrs)}")
hit = sorted(yrs & set(c['analysis']['baseline_seasons']))
print(f"  overlap with the published baseline: {hit}")
if hit:
    v2 = [v for v in loaded["visits"] if v["visit_key"]["id_field"] != 4553]
    c2 = di_observe.cell(v2, sheet, "Arezzo", "ACTIVE_INFESTATION_COUNT", AS_OF)
    print(f"\n  Arezzo baseline_rate_pct_median WITH  it: "
          f"{c['analysis']['baseline_rate_pct_median']}")
    print(f"  Arezzo baseline_rate_pct_median WITHOUT it: "
          f"{c2['analysis']['baseline_rate_pct_median']}")
    for f in ("historical_state", "historical_state_unmatched", "matched_panel_seasons",
              "baseline_n", "observed_trend"):
        print(f"    {f:32s} {c['analysis'].get(f)!r} -> {c2['analysis'].get(f)!r}")
else:
    print("\n  it does NOT reach the published Arezzo baseline for this as_of "
          "(its seasons are not among the seasons that clear MIN_VISITS/MIN_DRUPES).")
    print("  It WOULD reach it at any as_of whose window includes "
          f"{sorted(str(d) for d,_ in seq)[0][5:]}..; tested below.")
    # find an as_of where it lands in a published baseline
    for cand in ("2026-08-16", "2026-09-20", "2026-10-04"):
        a = dt.date.fromisoformat(cand)
        ld = di_core.load_visits(L.CASE, sheet, a)
        cc = di_observe.cell(ld["visits"], sheet, "Arezzo", "ACTIVE_INFESTATION_COUNT", a)
        print(f"    as_of {cand}: Arezzo baseline seasons "
              f"{cc['analysis']['baseline_seasons']}  "
              f"(grove seasons {sorted(yrs)})")
