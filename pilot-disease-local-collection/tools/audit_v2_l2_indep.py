# Independent re-audit of C3 year-span claim.
# Reads ONLY the raw gzip payloads. Does not consult any manifest.
import gzip, json, glob, os, datetime, collections

files = sorted(glob.glob('raw/F4-arpav-rest/tabella/*.json.gz'))
print("raw gz files on disk:", len(files))

# tipo -> station -> set(years); also rows, units
by_tipo = collections.defaultdict(lambda: {
    'files': 0, 'rows': 0, 'stations': collections.defaultdict(set),
    'units': collections.Counter(), 'years': set()})

# per (tipo, station) -> set of dates
dates = collections.defaultdict(set)

for p in files:
    base = os.path.basename(p).replace('.json.gz', '')
    codseq, yr = base.split('_')
    yr = int(yr)
    d = json.loads(gzip.open(p, 'rb').read().decode('utf-8'))
    rows = d.get('data') or []
    if not rows:
        # empty payload: cannot learn tipo from data
        by_tipo['__EMPTY__']['files'] += 1
        by_tipo['__EMPTY__']['years'].add(yr)
        continue
    tipos = {r.get('tipo') for r in rows}
    assert len(tipos) == 1, (p, tipos)
    tipo = tipos.pop()
    st = {(r.get('codice_stazione'), r.get('nome_stazione')) for r in rows}
    assert len(st) == 1, (p, st)
    st = st.pop()
    b = by_tipo[tipo]
    b['files'] += 1
    b['rows'] += len(rows)
    b['stations'][st].add(yr)
    b['years'].add(yr)
    for r in rows:
        b['units'][r.get('unitnm')] += 1
        dates[(tipo, st)].add(r['dataora'][:10])

print()
print("=== per-sensor, computed from raw payloads only ===")
for tipo in sorted(by_tipo):
    b = by_tipo[tipo]
    ns = len(b['stations'])
    ny = len(b['years'])
    print(f"{tipo:10s} files={b['files']:4d} rows={b['rows']:6d} stations={ns:3d} "
          f"union_years={min(b['years'])}-{max(b['years'])} ({ny}) "
          f"grid={ns*ny:4d} shortfall={ns*ny-b['files']:3d} units={dict(b['units'].most_common(3))}")

print()
print("=== BFOGL: per-station year sets (raw-derived) ===")
b = by_tipo['BFOGL']
span_counter = collections.Counter()
for (code, name), yrs in sorted(b['stations'].items(), key=lambda kv: (min(kv[1]), kv[0][0])):
    span = f"{min(yrs)}-{max(yrs)}"
    gaps = sorted(set(range(min(yrs), max(yrs) + 1)) - yrs)
    span_counter[span] += 1
    print(f"  {code:5d} {name:36s} n_years={len(yrs):2d} span={span} interior_gaps={gaps}")
print("  span histogram:", dict(span_counter))
print("  sum of files over stations:", sum(len(v) for v in b['stations'].values()))

# How many stations actually hold each year?
print()
print("=== BFOGL: how many of the 14 stations hold each year ===")
per_year = collections.Counter()
for (code, name), yrs in b['stations'].items():
    for y in yrs:
        per_year[y] += 1
for y in sorted(per_year):
    print(f"  {y}  stations_with_file={per_year[y]:2d}")

# C4 window coverage, computed from raw dates
W0 = datetime.date(2014, 3, 1)
W1 = datetime.date(2025, 10, 31)
wdays = (W1 - W0).days + 1
print()
print(f"=== C4 window {W0}..{W1} = {wdays} days (BFOGL, raw-derived distinct dates) ===")
rows_out = []
for (tipo, st), ds in dates.items():
    if tipo != 'BFOGL':
        continue
    inw = {x for x in ds if W0.isoformat() <= x <= W1.isoformat()}
    rows_out.append((len(inw), st, 100.0 * len(inw) / wdays))
rows_out.sort(reverse=True)
ge994 = 0
for n, st, pct in rows_out:
    flag = 'OK' if pct >= 99.4 else '<<<< BELOW 99.4'
    if pct >= 99.4:
        ge994 += 1
    print(f"  {st[1]:36s} ({st[0]:4d})  days={n:4d}/{wdays}  {pct:6.2f} %  {flag}")
print(f"  stations >= 99.4%: {ge994} of {len(rows_out)}")
