import json, gzip, os, collections, datetime

ROOT = r'C:\disease-local-collection-italy\pilot-disease-local-collection'
rows = [json.loads(l) for l in open(os.path.join(ROOT, 'manifests', 'arpav-daily-manifest.jsonl'), encoding='utf-8')]

bf = [r for r in rows if r['tipo'] == 'BFOGL']
print('=== C3: leaf wetness (BFOGL) ===')
print('files:', len(bf))
print('sum of manifest rows:', sum(r['rows'] for r in bf))
print('distinct codseqst (stations):', len({r['codseqst'] for r in bf}))
print('distinct codseq (sensors)  :', len({r['codseq'] for r in bf}))
print('distinct station names     :', len({r['stazione'] for r in bf}))
print('years:', sorted({r['anno'] for r in bf}))
print('units:', dict(collections.Counter(r.get('unit') for r in bf)))
print('sensore labels:', dict(collections.Counter(r['sensore'] for r in bf)))
# station counted once per sensor?
per_st = collections.Counter(r['codseqst'] for r in bf)
sens_per_st = collections.defaultdict(set)
for r in bf:
    sens_per_st[r['codseqst']].add(r['codseq'])
print('stations with >1 BFOGL sensor id:', {k: sorted(v) for k, v in sens_per_st.items() if len(v) > 1})
print()

# recount rows from the actual files
tot = 0
totdist = 0
per_station_dates = collections.defaultdict(set)
for r in bf:
    p = os.path.join(ROOT, r['raw_path'].replace('/', os.sep))
    d = json.loads(gzip.decompress(open(p, 'rb').read()).decode('utf-8'))['data']
    tot += len(d)
    ds = {x['dataora'][:10] for x in d}
    totdist += len(ds)
    per_station_dates[(r['codseqst'], r['stazione'])] |= ds
print('RECOUNTED BFOGL rows          :', tot)
print('RECOUNTED BFOGL distinct dates:', totdist)
print('union of distinct dates across all 14 stations (rows would collapse to):',
      len(set().union(*per_station_dates.values())))
print()

print('=== C4: coverage of 2014-03-01 .. 2025-10-31 ===')
a = datetime.date(2014, 3, 1)
b = datetime.date(2025, 10, 31)
span = (b - a).days + 1
print('days in window (recomputed):', span)
allw = {(a + datetime.timedelta(days=i)).isoformat() for i in range(span)}
res = []
for (st, name), ds in per_station_dates.items():
    inw = ds & allw
    res.append((len(inw) / span, len(inw), name, st))
res.sort(reverse=True)
ge = 0
for pc, n, name, st in res:
    flag = 'OK' if pc >= 0.994 else '<< BELOW 99.4%'
    if pc >= 0.994:
        ge += 1
    print('   %6.2f%%  %5d/%d  %-46s %s' % (pc * 100, n, span, name, flag))
print('stations at >= 99.4%%: %d of %d' % (ge, len(res)))
print()

# province check
prov = {}
for l in open(os.path.join(ROOT, 'manifests', 'daily-series-provenance.jsonl'), encoding='utf-8'):
    d = json.loads(l)
    prov[d['STATION_ID']] = (d.get('PROVINCIA'), d.get('COMUNE'), d.get('STATION_NAME'))
print('=== province of the 14 stations (per provenance) ===')
for st in sorted({r['codseqst'] for r in bf}):
    print('   ', st, prov.get(st))
print('   province counter:', dict(collections.Counter(prov.get(st, ('?',))[0] for st in {r['codseqst'] for r in bf})))
