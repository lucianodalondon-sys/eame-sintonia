#!/usr/bin/env python3
"""RT3-09
  a) spatial coherence of each comune: Tuscan comuni are small. A comune whose monitored
     points span tens of kilometres is not one comune.
  b) the one id_field that carries two PROVINCES (5700), in full.
  c) the 25 id_field that carry two comuni: do they cross a province line?
  d) Prato in the current window: which comuni, which groves, what the reader is told.
  e) id_field 4554, the worst comune-vs-coordinate mismatch.
"""
import collections, math, os, sys, statistics, datetime as dt

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.abspath(os.path.join(HERE, "..", "engine")))
sys.path.insert(0, HERE)
import rt3_lib as L

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
print("=" * 78)
print("RT3-09a  is each comune spatially coherent?")
print("=" * 78)
bycom = collections.defaultdict(set)
name = {}
prov = {}
for r in R.values():
    p = pt(r)
    c = L.admin6(r.get("admin_code"))
    name[c] = str(r.get("name_4")).strip()
    prov[c] = str(r.get("nome_area"))
    if p:
        bycom[c].add((round(p[0], 6), round(p[1], 6)))
spans = []
for c, pts in bycom.items():
    pl = list(pts)
    if len(pl) < 2:
        continue
    mx = 0.0
    for i in range(len(pl)):
        for j in range(i + 1, len(pl)):
            d = hav(pl[i], pl[j])
            if d > mx: mx = d
    spans.append((mx, c, len(pl)))
spans.sort(reverse=True)
print(f"\ncomuni with >=2 distinct usable points: {len(spans)} of {len(bycom)}")
for thr in (10000, 20000, 30000, 40000):
    print(f"  comuni whose monitored points span more than {thr/1000:>4.0f} km: "
          f"{sum(1 for m,*_ in spans if m>thr):>3} / {len(spans)}")
print("\n  widest 12 (largest Tuscan comune, Grosseto, is ~47 km across; most are <15 km):")
for m, c, n in spans[:12]:
    print(f"    {c} {name[c]:26s} {prov[c]:14s} span {m/1000:>6.1f} km over {n:>4} points")

print("\n" + "=" * 78)
print("RT3-09b  id_field 5700 - the one grove id that carries two PROVINCES")
print("=" * 78)
seq = sorted((str(d), r) for (i, d), r in R.items() if i == 5700)
for d, r in seq:
    print(f"    {d}  {str(r.get('nome_area')):9s} {L.admin6(r.get('admin_code'))} "
          f"{str(r.get('name_4')):22s} {str(r.get('name_5')):20s} "
          f"lat={r.get('lat')} lon={r.get('lon')} org={r.get('org_name')} "
          f"name={r.get('name')!r} cultivar={r.get('cultivar')!r}")
pts = [pt(r) for _, r in seq]
good = [p for p in pts if p]
if len(good) >= 2:
    print(f"    max distance between its usable points: "
          f"{max(hav(a,b) for a in good for b in good)/1000:.2f} km")

print("\n" + "=" * 78)
print("RT3-09c  the 25 id_field that carry two comuni")
print("=" * 78)
byf = collections.defaultdict(list)
for (i, d), r in R.items():
    byf[i].append((str(d), r))
print(f"  {'id_field':>8} {'comuni':>6} {'provinces':>9} {'max move km':>11}  detail")
cross = 0
for i, seq in sorted(byf.items()):
    coms = collections.Counter(L.admin6(r.get("admin_code")) for _, r in seq)
    if len(coms) < 2:
        continue
    provs = {str(r.get("nome_area")) for _, r in seq}
    g = [p for p in (pt(r) for _, r in seq) if p]
    mv = max((hav(a, b) for a in g for b in g), default=0.0) / 1000
    if len(provs) > 1:
        cross += 1
    print(f"  {i:>8} {len(coms):>6} {len(provs):>9} {mv:>11.2f}  "
          f"{[(c, name.get(c), n) for c, n in coms.most_common()]}")
print(f"\n  of the {sum(1 for i in byf if len({L.admin6(r.get('admin_code')) for _,r in byf[i]})>1)} "
      f"id_field with two comuni, {cross} cross a PROVINCE line")

print("\n" + "=" * 78)
print("RT3-09d  Prato in the current 28-day window")
print("=" * 78)
lo_, hi_ = dt.date(2026, 8, 10), dt.date(2026, 9, 6)
cur = [(i, d, r) for (i, d), r in R.items()
       if str(r.get("nome_area")) == "Prato"
       and lo_ <= dt.date.fromisoformat(str(d)) <= hi_]
print(f"  visits: {len(cur)}   groves: {len({i for i,_,_ in cur})}")
for c, n in collections.Counter((L.admin6(r.get('admin_code')), str(r.get('name_4')).strip())
                                for _, _, r in cur).most_common():
    tag = "legacy 048 code, comune is in province 100 today" \
        if c[0] in L.PRATO_REFORM else ""
    print(f"    {c[0]} {c[1]:20s} {n:>3} visits   {tag}")

print("\n" + "=" * 78)
print("RT3-09e  id_field 4554 - claims SANSEPOLCRO, sits 55 km away")
print("=" * 78)
seq = sorted((str(d), r) for (i, d), r in R.items() if i == 4554)
seen = set()
for d, r in seq:
    k = (L.admin6(r.get("admin_code")), str(r.get("lat"))[:9], str(r.get("lon"))[:9])
    if k in seen: continue
    seen.add(k)
    print(f"    {d}  {L.admin6(r.get('admin_code'))} {str(r.get('name_4')):20s} "
          f"{str(r.get('nome_area')):9s} lat={r.get('lat')} lon={r.get('lon')} "
          f"name={r.get('name')!r}")
print(f"    ({len(seq)} visits total, {len(seen)} distinct comune+coordinate combinations)")
