import json, gzip, os, collections

ROOT = r'C:\disease-local-collection-italy\pilot-disease-local-collection'
rows = [json.loads(l) for l in open(os.path.join(ROOT, 'manifests', 'arpav-daily-manifest.jsonl'), encoding='utf-8')]

tot = 0
empty = 0
nullinside = 0
kinds = collections.Counter()
bytipo_null = collections.Counter()
bytipo_tot = collections.Counter()
for r in rows:
    p = os.path.join(ROOT, r['raw_path'].replace('/', os.sep))
    data = json.loads(gzip.decompress(open(p, 'rb').read()).decode('utf-8'))['data']
    for x in data:
        tot += 1
        bytipo_tot[r['tipo']] += 1
        v = x.get('valore')
        if v is None or v == '':
            empty += 1
            kinds['EMPTY_OR_NONE'] += 1
            continue
        if isinstance(v, str) and v.startswith('{'):
            try:
                o = json.loads(v)
            except Exception:
                kinds['UNPARSEABLE_OBJ'] += 1
                continue
            if any(m is None for m in o.values()):
                nullinside += 1
                bytipo_null[r['tipo']] += 1
                kinds['OBJ_WITH_NULL_MEMBER'] += 1
            elif not o:
                kinds['EMPTY_OBJ'] += 1
            else:
                kinds['OBJ_OK'] += 1
        else:
            kinds['SCALAR'] += 1

print('total rows                       :', tot)
print('rows with valore null/empty      :', empty)
print('rows whose valore is a JSON object with at least one null member:', nullinside)
print('value kinds:', dict(kinds))
print('object-with-null by sensor type:', dict(bytipo_null))
print('rows by sensor type:', dict(bytipo_tot))
