import json, gzip, hashlib, os, collections

ROOT = r'C:\disease-local-collection-italy\pilot-disease-local-collection'
tab = os.path.join(ROOT, 'raw', 'F4-arpav-rest', 'tabella')

rows = []
with open(os.path.join(ROOT, 'manifests', 'arpav-daily-manifest.jsonl'), encoding='utf-8') as fh:
    for l in fh:
        rows.append(json.loads(l))

# 1) does manifest sha256 == sha256 of the DECOMPRESSED payload?
ok = 0
bad = 0
for d in rows[:50]:
    p = os.path.join(ROOT, d['raw_path'].replace('/', os.sep))
    inner = gzip.decompress(open(p, 'rb').read())
    if hashlib.sha256(inner).hexdigest() == d['sha256'] and len(inner) == d['bytes']:
        ok += 1
    else:
        bad += 1
print('[A] first 50: manifest sha256/bytes match DECOMPRESSED payload:', ok, 'mismatch:', bad)

# 2) semantic key duplication
print()
print('[B] semantic duplication in the 1038 "station x sensor x year" files')
print('  distinct (codseq, anno):', len({(d['codseq'], d['anno']) for d in rows}))
print('  distinct (codseqst, tipo, anno):', len({(d['codseqst'], d['tipo'], d['anno']) for d in rows}))
print('  distinct (stazione, sensore, anno):', len({(d['stazione'], d['sensore'], d['anno']) for d in rows}))
print('  distinct codseq (sensor ids):', len({d['codseq'] for d in rows}))
print('  distinct codseqst (station ids):', len({d['codseqst'] for d in rows}))
print('  distinct stazione strings:', len({d['stazione'] for d in rows}))
print('  distinct sensore strings:', len({d['sensore'] for d in rows}))
print('  distinct anno:', len({d['anno'] for d in rows}))

c = collections.Counter((d['codseqst'], d['tipo'], d['anno']) for d in rows)
dup = {k: v for k, v in c.items() if v > 1}
print('  (codseqst,tipo,anno) appearing >1 time:', len(dup), 'extra files:', sum(v - 1 for v in dup.values()))
for k, v in sorted(dup.items(), key=lambda x: -x[1])[:20]:
    print('    ', k, 'x', v)

# 3) station -> how many station ids per station NAME (station double count risk)
name2st = collections.defaultdict(set)
st2name = collections.defaultdict(set)
for d in rows:
    name2st[d['stazione']].add(d['codseqst'])
    st2name[d['codseqst']].add(d['stazione'])
multi = {k: v for k, v in name2st.items() if len(v) > 1}
print()
print('[C] station names mapped to >1 codseqst:', len(multi))
for k, v in list(multi.items())[:10]:
    print('    ', k, sorted(v))
multi2 = {k: v for k, v in st2name.items() if len(v) > 1}
print('    codseqst mapped to >1 station name:', len(multi2))
for k, v in list(multi2.items())[:10]:
    print('    ', k, sorted(v))
