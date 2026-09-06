import json, os, gzip, collections, hashlib, random

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def P(*a): return os.path.join(ROOT, *a)
def rd(p): return [json.loads(l) for l in open(P(p), encoding='utf-8') if l.strip()]

MAN = rd('manifests/arpav-daily-manifest.jsonl')
print("manifest rows:", len(MAN))
print("sum of 'rows' field:", sum(r['rows'] for r in MAN))
print("distinct sha256 in manifest:", len({r['sha256'] for r in MAN}))

tot_real = 0
tot_val = 0
mismatch = []
shabad = []
missing = []
meta_total_mismatch = []
for r in MAN:
    p = P(r['raw_path'])
    if not os.path.exists(p):
        missing.append(r['raw_path']); continue
    b = open(p, 'rb').read()
    h = hashlib.sha256(gzip.decompress(b)).hexdigest()
    if h != r['sha256']:
        # maybe sha is of the gz itself
        if hashlib.sha256(b).hexdigest() != r['sha256']:
            shabad.append(r['raw_path'])
    d = json.loads(gzip.decompress(b).decode('utf-8'))
    data = d.get('data') or []
    n = len(data)
    tot_real += n
    if n != r['rows']:
        mismatch.append((r['raw_path'], r['rows'], n))
    # does the API declare its own total?
    mt = (d.get('meta') or {}).get('total')
    if mt is not None and mt != n:
        meta_total_mismatch.append((r['raw_path'], mt, n))
    for row in data:
        v = row.get('valore')
        if v is not None and v != '':
            tot_val += 1

print()
print("=== RECOUNTED BY OPENING EVERY FILE ===")
print("files opened:", len(MAN) - len(missing), " missing:", len(missing))
print("REAL total data rows:", tot_real)
print("rows carrying a non-null value:", tot_val,
      "  pct: %.4f%%" % (100.0 * tot_val / tot_real if tot_real else 0))
print("manifest 'rows' != real len(data):", len(mismatch), mismatch[:10])
print("sha256 mismatches (neither payload nor gz):", len(shabad), shabad[:5])
print("files where meta.total != len(data):", len(meta_total_mismatch), meta_total_mismatch[:10])

# distinct sha of the gz files themselves and of payloads
gz = collections.Counter()
pl = collections.Counter()
for r in MAN:
    p = P(r['raw_path'])
    if not os.path.exists(p): continue
    b = open(p, 'rb').read()
    gz[hashlib.sha256(b).hexdigest()] += 1
    pl[hashlib.sha256(gzip.decompress(b)).hexdigest()] += 1
print()
print("distinct sha256 of .gz containers:", len(gz))
print("distinct sha256 of decompressed payloads:", len(pl))
dupe = {k: v for k, v in pl.items() if v > 1}
print("payload sha appearing more than once:", len(dupe))
