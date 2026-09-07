#!/usr/bin/env python3
"""RT3-04  The coordinates.

  a) how many rows fall outside Tuscany's bounding box, and outside Italy's?
  b) does swapping lat and lon rescue them (a transposition), or are they another
     coordinate system / garbage?
  c) which seasons are affected?
  d) does the coordinate agree with the comune the row claims? (distance to the median
     point of that comune, computed from the rows that ARE inside Tuscany)
"""
import collections, math, os, sys, statistics, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rt3_lib as L

# Tuscany, generous: Massa-Carrara north tip to Capalbio, Capraia to the Valtiberina.
TUS = (42.20, 44.50, 9.60, 12.45)          # latmin, latmax, lonmin, lonmax
ITA = (35.4, 47.1, 6.6, 18.6)

def inbox(la, lo, b):
    return la is not None and lo is not None and b[0] <= la <= b[1] and b[2] <= lo <= b[3]

def hav(la1, lo1, la2, lo2):
    R = 6371000.0
    p1, p2 = math.radians(la1), math.radians(la2)
    h = (math.sin((p2 - p1) / 2) ** 2 +
         math.cos(p1) * math.cos(p2) * math.sin(math.radians(lo2 - lo1) / 2) ** 2)
    return 2 * R * math.asin(math.sqrt(h))

print("=" * 78)
print("RT3-04  coordinates")
print("=" * 78)

R = L.visit_rows()
N = len(R)
in_tus = out_tus = out_ita = nulls = 0
per_season = collections.defaultdict(lambda: [0, 0])
swap_rescued = 0
swap_into_italy = 0
bad_examples = []
for (idf, date), r in R.items():
    la, lo = L.fnum(r.get("lat")), L.fnum(r.get("lon"))
    y = str(date)[:4]
    if la is None or lo is None:
        nulls += 1
        continue
    ok = inbox(la, lo, TUS)
    per_season[y][0 if ok else 1] += 1
    if ok:
        in_tus += 1
    else:
        out_tus += 1
        if not inbox(la, lo, ITA):
            out_ita += 1
        if inbox(lo, la, TUS):
            swap_rescued += 1
        elif inbox(lo, la, ITA):
            swap_into_italy += 1
        if len(bad_examples) < 8:
            bad_examples.append((idf, date, la, lo, r.get("name_4"), r.get("nome_area")))

print(f"\nvisits: {N:,}")
print(f"  lat/lon unparseable or missing            {nulls:,} / {N:,}")
print(f"  INSIDE the Tuscany bounding box           {in_tus:,} / {N:,}")
print(f"  OUTSIDE the Tuscany bounding box          {out_tus:,} / {N:,}")
print(f"    of which outside Italy altogether       {out_ita:,} / {N:,}")
print(f"    rescued by SWAPPING lat and lon (-> Tuscany) {swap_rescued:,} / {out_tus:,}")
print(f"    swap lands in Italy but not Tuscany     {swap_into_italy:,} / {out_tus:,}")
print("\n  examples of out-of-box rows:")
for idf, d, la, lo, n4, na in bad_examples:
    print(f"    id_field {idf:>7} {d}  lat={la:<12} lon={lo:<12} {n4}/{na}")

print("\n  per season: inside / outside the Tuscany box")
for y in sorted(per_season):
    a, b = per_season[y]
    flag = "   <-- ENTIRE SEASON OUT OF BOX" if a == 0 and b else ""
    print(f"    {y}  in {a:>6,}   out {b:>6,}{flag}")

# ---- what ARE the bad coordinates? ----------------------------------------------
bad = [(str(d)[:4], L.fnum(r.get("lat")), L.fnum(r.get("lon")))
       for (i, d), r in R.items()
       if not inbox(L.fnum(r.get("lat")), L.fnum(r.get("lon")), TUS)
       and L.fnum(r.get("lat")) is not None]
if bad:
    las = [b[1] for b in bad]; los = [b[2] for b in bad]
    print(f"\n  the out-of-box values themselves: "
          f"lat {min(las):.5f}..{max(las):.5f}, lon {min(los):.5f}..{max(los):.5f}")
    print("  (Tuscany in WGS84 is lat 42.2..44.5, lon 9.6..12.45. "
          "Neither the raw values nor the swap fall there -> another system or garbage.)")

# ---- does the coordinate agree with the comune it claims? ------------------------
cent = collections.defaultdict(list)
for (idf, date), r in R.items():
    la, lo = L.fnum(r.get("lat")), L.fnum(r.get("lon"))
    if inbox(la, lo, TUS):
        cent[L.admin6(r.get("admin_code"))].append((la, lo))
med = {c: (statistics.median([p[0] for p in v]), statistics.median([p[1] for p in v]))
       for c, v in cent.items() if v}
far = collections.Counter()
far_rows = []
checked = 0
for (idf, date), r in R.items():
    la, lo = L.fnum(r.get("lat")), L.fnum(r.get("lon"))
    if not inbox(la, lo, TUS):
        continue
    c = L.admin6(r.get("admin_code"))
    if c not in med:
        continue
    checked += 1
    dd = hav(la, lo, med[c][0], med[c][1])
    if dd > 25000:
        far[(c, str(r.get("name_4")).strip(), str(r.get("nome_area")))] += 1
        far_rows.append((dd, idf, date, c, r.get("name_4"), r.get("nome_area"), la, lo))
print(f"\n  in-box rows checked against their own comune's median point: {checked:,}")
print(f"  rows further than 25 km from the median point of the comune they claim: "
       f"{sum(far.values()):,} / {checked:,}")
far_rows.sort(reverse=True)
for dd, idf, date, c, n4, na, la, lo in far_rows[:12]:
    print(f"    {dd/1000:>7.1f} km  id_field {idf:>7} {date} claims {c} {n4}/{na} "
          f"but sits at ({la:.4f},{lo:.4f})")

# ---- province-level: does the point sit in the claimed province's cloud? ---------
pcent = collections.defaultdict(list)
for (idf, date), r in R.items():
    la, lo = L.fnum(r.get("lat")), L.fnum(r.get("lon"))
    if inbox(la, lo, TUS):
        pcent[str(r.get("nome_area"))].append((la, lo))
pmed = {p: (statistics.median([q[0] for q in v]), statistics.median([q[1] for q in v]))
        for p, v in pcent.items()}
wrong_nearest = collections.Counter()
tot = 0
for (idf, date), r in R.items():
    la, lo = L.fnum(r.get("lat")), L.fnum(r.get("lon"))
    if not inbox(la, lo, TUS):
        continue
    tot += 1
    claimed = str(r.get("nome_area"))
    nearest = min(pmed, key=lambda p: hav(la, lo, pmed[p][0], pmed[p][1]))
    if nearest != claimed:
        wrong_nearest[(claimed, nearest)] += 1
print(f"\n  NOTE: 'nearest province centroid' is a crude test - provinces are not discs.")
print(f"  in-box rows whose nearest province centroid is NOT the province claimed: "
      f"{sum(wrong_nearest.values()):,} / {tot:,}")
for (a, b), n in wrong_nearest.most_common(12):
    print(f"    claimed {a:16s} nearest centroid {b:16s} {n:>6,}")

json.dump({"visits": N, "in_tuscany_box": in_tus, "out_of_box": out_tus,
           "out_of_italy": out_ita, "rescued_by_swap": swap_rescued,
           "per_season": {k: v for k, v in sorted(per_season.items())},
           "rows_over_25km_from_own_comune": sum(far.values())},
          open(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                            "rt3_04_coords.json"), "w", encoding="utf-8"), indent=1)
