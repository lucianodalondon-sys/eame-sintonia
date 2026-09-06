import json, gzip, hashlib, os

ROOT = r'C:\disease-local-collection-italy\pilot-disease-local-collection'
tab = os.path.join(ROOT, 'raw', 'F4-arpav-rest', 'tabella')
man = {}
with open(os.path.join(ROOT, 'manifests', 'arpav-daily-manifest.jsonl'), encoding='utf-8') as fh:
    for l in fh:
        d = json.loads(l)
        man[os.path.basename(d['raw_path'])] = d

files = sorted(os.listdir(tab))
print('files on disk:', len(files), 'manifest rows:', len(man))

gz_h = {}
inner_h = {}
mismatch = []
sizemis = []
for f in files:
    p = os.path.join(tab, f)
    b = open(p, 'rb').read()
    g = hashlib.sha256(b).hexdigest()
    gz_h.setdefault(g, []).append(f)
    try:
        inner = gzip.decompress(b)
    except Exception as e:
        inner = b''
        print('DECOMPRESS FAIL', f, e)
    ih = hashlib.sha256(inner).hexdigest()
    inner_h.setdefault(ih, []).append(f)
    d = man.get(f)
    if d is None:
        print('FILE NOT IN MANIFEST:', f)
        continue
    if d['sha256'] != g:
        mismatch.append((f, d['sha256'], g))
    if d['bytes'] != len(b):
        sizemis.append((f, d['bytes'], len(b)))

print('recomputed distinct sha256 of .gz files:', len(gz_h))
print('manifest sha256 mismatches:', len(mismatch))
for m in mismatch[:5]:
    print('  ', m)
print('manifest bytes vs gz filesize mismatches:', len(sizemis))
for m in sizemis[:5]:
    print('  ', m)
print('distinct sha256 of DECOMPRESSED payloads:', len(inner_h))
dups = {k: v for k, v in inner_h.items() if len(v) > 1}
print('payload sha256 shared by >1 file:', len(dups), 'files involved:', sum(len(v) for v in dups.values()))
for k, v in sorted(dups.items(), key=lambda x: -len(x[1]))[:15]:
    print('  ', k[:16], len(v), v[:8])
