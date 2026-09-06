import json, gzip, os, collections, datetime

ROOT = r'C:\disease-local-collection-italy\pilot-disease-local-collection'

rows = []
with open(os.path.join(ROOT, 'manifests', 'arpav-daily-manifest.jsonl'), encoding='utf-8') as fh:
    for l in fh:
        rows.append(json.loads(l))

total_rows = 0
total_rows_with_value = 0
total_distinct_dates = 0
dupdate_files = []
per_file = {}
shapes = collections.Counter()

for d in rows:
    p = os.path.join(ROOT, d['raw_path'].replace('/', os.sep))
    payload = json.loads(gzip.decompress(open(p, 'rb').read()).decode('utf-8'))
    shapes[type(payload).__name__] += 1
    if isinstance(payload, dict):
        data = payload.get('data') or payload.get('DATA') or []
        keys = tuple(sorted(payload.keys()))
    else:
        data = payload
        keys = ('LIST',)
    n = len(data)
    dates = []
    withval = 0
    for r in data:
        dt = r.get('dataora') or r.get('DATAORA') or r.get('data') or r.get('DATA')
        dates.append(dt)
        v = r.get('valore') if 'valore' in r else r.get('VALORE')
        if v is not None and v != '' and v != 'null':
            withval += 1
    dd = len(set(dates))
    total_rows += n
    total_rows_with_value += withval
    total_distinct_dates += dd
    if dd != n:
        dupdate_files.append((os.path.basename(p), n, dd))
    per_file[d['local_item_id']] = dict(n=n, dd=dd, withval=withval, mrows=d['rows'],
                                        tipo=d['tipo'], st=d['codseqst'], stz=d['stazione'],
                                        anno=d['anno'], dates=set(dates), unit=d.get('unit'),
                                        codseq=d['codseq'])

print('payload shapes:', dict(shapes))
print('RECOUNTED total rows          :', total_rows)
print('RECOUNTED distinct-date rows  :', total_distinct_dates)
print('RECOUNTED rows carrying value :', total_rows_with_value)
print('files where rows != distinct dates:', len(dupdate_files))
for f in dupdate_files[:20]:
    print('   ', f)
print('manifest sum of rows          :', sum(d['rows'] for d in rows))
mism = [(d['local_item_id'], d['rows'], per_file[d['local_item_id']]['n']) for d in rows if d['rows'] != per_file[d['local_item_id']]['n']]
print('files where manifest rows != recounted rows:', len(mism))
for m in mism[:10]:
    print('   ', m)

json.dump({k: {kk: (sorted(vv) if isinstance(vv, set) else vv) for kk, vv in v.items()} for k, v in per_file.items()},
          open(os.path.join(ROOT, 'tools', '_audit_perfile.json'), 'w'), default=str)
print('wrote tools/_audit_perfile.json')
