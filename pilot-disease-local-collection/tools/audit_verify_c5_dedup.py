"""INDEPENDENT: are the 26 annate files really 26 distinct files on disk, real
PDFs, and is the 2005 pair byte-distinct (i.e. is the duplication semantic
rather than byte-level)? Read-only."""
import json, os, hashlib, subprocess
from collections import Counter

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
MAN = os.path.join(ROOT, 'manifests', 'arpav-docs-manifest.verified.jsonl')
rows = [json.loads(l) for l in open(MAN, encoding='utf-8')]
ann = [r for r in rows if '/annate-agrarie/' in r['source_url']]

sh, magic, missing = {}, Counter(), []
for r in ann:
    p = os.path.join(ROOT, r['raw_path'].replace('/', os.sep))
    if not os.path.exists(p):
        missing.append(r['raw_path']); continue
    b = open(p, 'rb').read()
    d = hashlib.sha256(b).hexdigest()
    sh[r['document_title']] = d
    magic[b[:5]] += 1
    if d != r['sha256']:
        print('SHA MISMATCH vs manifest:', r['document_title'])

print('annate rows            :', len(ann))
print('files present on disk  :', len(sh), ' missing:', missing)
print('leading magic bytes    :', dict(magic))
print('distinct sha256        :', len(set(sh.values())))
dupes = [k for k, v in Counter(sh.values()).items() if v > 1]
print('byte-identical groups  :', [[t for t, d in sh.items() if d == k] for k in dupes] or 'none')
print()
print('2004-05 sha:', sh['Annata agraria 2004-05'])
print('2005    sha:', sh['annata agraria 2005'])
print('byte-identical?', sh['Annata agraria 2004-05'] == sh['annata agraria 2005'])

# is the quarantined failed attempt double-counted into the annate set?
q = os.path.join(ROOT, 'raw', '_failed-captures')
if os.path.isdir(q):
    qf = []
    for dp, _, fn in os.walk(q):
        for f in fn:
            qf.append(os.path.join(dp, f))
    qs = set()
    for p in qf:
        qs.add(hashlib.sha256(open(p, 'rb').read()).hexdigest())
    print()
    print('quarantined files      :', len(qf), ' distinct sha:', len(qs))
    print('quarantine sha overlapping the 26 annate sha:', len(qs & set(sh.values())))
