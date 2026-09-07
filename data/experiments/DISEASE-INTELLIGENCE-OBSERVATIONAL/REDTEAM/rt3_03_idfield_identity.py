#!/usr/bin/env python3
"""RT3-03  ATTACK THE MATCHED PANEL.

The published historical statement is the MATCHED-PANEL one, and it rests entirely on
id_field being a stable identity for ONE grove. If an id_field is recycled - moves comune,
moves province, or jumps hundreds of metres between seasons - then "the same groves" is a
lie and the matched comparison is WORSE than the unmatched one.

Tests:
  1. does an id_field ever carry more than one nome_area?  more than one admin_code?
  2. does an id_field's coordinate move? by how much? (haversine, metres)
  3. does an id_field ever change cultivar / name / org?
  4. gaps: does an id_field disappear for years and come back (a recycling signature)?
  5. how much of the CURRENT window's matched panel is affected?
"""
import collections, math, os, sys, json, datetime as dt
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rt3_lib as L

def hav(a, b):
    (la1, lo1), (la2, lo2) = a, b
    R = 6371000.0
    p1, p2 = math.radians(la1), math.radians(la2)
    dp = p2 - p1
    dl = math.radians(lo2 - lo1)
    h = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * R * math.asin(math.sqrt(h))

print("=" * 78)
print("RT3-03  is id_field a stable identity?")
print("=" * 78)

R = L.visit_rows()
by_field = collections.defaultdict(list)
for (idf, date), r in R.items():
    by_field[idf].append((str(date), r))
for v in by_field.values():
    v.sort()
print(f"\ndistinct id_field: {len(by_field):,}   visits: {len(R):,}")

# ---- 1. categorical stability ----------------------------------------------------
moves_prov, moves_com, moves_cult, moves_name, moves_org, moves_name5 = ({}, {}, {}, {}, {}, {})
for idf, seq in by_field.items():
    provs = collections.Counter(str(r.get("nome_area")) for _, r in seq)
    coms = collections.Counter(L.admin6(r.get("admin_code")) for _, r in seq)
    cults = collections.Counter(str(r.get("cultivar")) for _, r in seq)
    nms = collections.Counter(str(r.get("name")) for _, r in seq)
    orgs = collections.Counter(str(r.get("org_name")) for _, r in seq)
    n5 = collections.Counter(str(r.get("name_5")) for _, r in seq)
    if len(provs) > 1: moves_prov[idf] = dict(provs)
    if len(coms) > 1: moves_com[idf] = dict(coms)
    if len(cults) > 1: moves_cult[idf] = dict(cults)
    if len(nms) > 1: moves_name[idf] = dict(nms)
    if len(orgs) > 1: moves_org[idf] = dict(orgs)
    if len(n5) > 1: moves_name5[idf] = dict(n5)

def rep(label, d, show=6):
    nvis = sum(len(by_field[k]) for k in d)
    print(f"\n{label}: {len(d):,} of {len(by_field):,} id_field "
          f"({nvis:,} of {len(R):,} visits)")
    for k in sorted(d)[:show]:
        print(f"    id_field {k}: {d[k]}")
    if len(d) > show:
        print(f"    ... and {len(d)-show} more")

rep("id_field carrying MORE THAN ONE nome_area", moves_prov)
rep("id_field carrying MORE THAN ONE admin_code (comune)", moves_com)
rep("id_field carrying MORE THAN ONE name_5 (sub-area)", moves_name5)
rep("id_field carrying MORE THAN ONE cultivar", moves_cult)
rep("id_field carrying MORE THAN ONE name (site name)", moves_name)
rep("id_field carrying MORE THAN ONE org_name", moves_org)

# ---- 2. coordinate drift ---------------------------------------------------------
drift = []
bad_coord = 0
for idf, seq in by_field.items():
    pts = []
    for d, r in seq:
        la, lo = L.fnum(r.get("lat")), L.fnum(r.get("lon"))
        if la is None or lo is None:
            bad_coord += 1
            continue
        pts.append((d, la, lo))
    if len(pts) < 2:
        continue
    mx, pair = 0.0, None
    for i in range(len(pts)):
        for j in range(i + 1, len(pts)):
            dd = hav((pts[i][1], pts[i][2]), (pts[j][1], pts[j][2]))
            if dd > mx:
                mx, pair = dd, (pts[i], pts[j])
    drift.append((mx, idf, pair, len(pts)))
drift.sort(reverse=True)
print(f"\n\nCOORDINATE DRIFT within one id_field (max pairwise distance, metres)")
print(f"  id_field with >=2 coordinate-bearing visits: {len(drift):,}")
print(f"  rows with unparseable lat/lon: {bad_coord:,}")
for thr in (0, 1, 10, 100, 250, 500, 1000, 5000, 20000):
    n = sum(1 for m, *_ in drift if m > thr)
    print(f"    id_field moving more than {thr:>6} m : {n:>6,} / {len(drift):,}")
print("\n  worst 15:")
for m, idf, pair, npts in drift[:15]:
    (d1, la1, lo1), (d2, la2, lo2) = pair
    r1 = dict(by_field[idf])[d1]
    r2 = dict(by_field[idf])[d2]
    print(f"    id_field {idf:>7}  {m:>10,.0f} m  {d1} ({la1:.5f},{lo1:.5f}) "
          f"{r1.get('name_4')}/{r1.get('nome_area')}  ->  {d2} ({la2:.5f},{lo2:.5f}) "
          f"{r2.get('name_4')}/{r2.get('nome_area')}   [{npts} visits]")

# ---- 3. absence gaps (recycling signature) ---------------------------------------
gaps = []
for idf, seq in by_field.items():
    yrs = sorted({int(d[:4]) for d, _ in seq})
    g = max((b - a for a, b in zip(yrs, yrs[1:])), default=1)
    if g > 1:
        gaps.append((g, idf, yrs))
gaps.sort(reverse=True)
print(f"\n\nid_field with a GAP of >=2 seasons: {len(gaps):,} / {len(by_field):,}")
for g, idf, yrs in gaps[:10]:
    print(f"    id_field {idf:>7}  max gap {g} seasons, seen {yrs}")

# ---- 4. how many of these reach the CURRENT matched panel? ----------------------
AS_OF = dt.date(2026, 9, 6)
lo_ = AS_OF - dt.timedelta(days=27)
cur_fields = {idf for (idf, d), r in R.items()
              if lo_ <= dt.date.fromisoformat(str(d)) <= AS_OF}
print(f"\n\ngroves in the current 28-day window: {len(cur_fields):,}")
suspect = set(moves_prov) | set(moves_com) | {idf for m, idf, *_ in drift if m > 500}
print(f"  of those, groves that ever moved province/comune or >500 m: "
      f"{len(cur_fields & suspect):,}")

json.dump({"n_id_field": len(by_field),
           "moves_province": moves_prov, "moves_comune": moves_com,
           "moves_name5": moves_name5, "moves_cultivar": moves_cult,
           "moves_name": {k: v for k, v in list(moves_name.items())[:50]},
           "drift_over_500m": [{"id_field": i, "metres": round(m, 1)}
                               for m, i, *_ in drift if m > 500],
           "max_drift_m": round(drift[0][0], 1) if drift else None},
          open(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                            "rt3_03_idfield.json"), "w", encoding="utf-8"),
          indent=1, default=str)
