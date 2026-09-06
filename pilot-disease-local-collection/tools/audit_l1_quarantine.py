import json, hashlib, os, collections

ROOT = r'C:\disease-local-collection-italy\pilot-disease-local-collection'


def load(p):
    return [json.loads(l) for l in open(os.path.join(ROOT, 'manifests', p), encoding='utf-8')]


inv = load('raw-file-inventory.jsonl')
sinv = {r['raw_path'] for r in inv}

disk = []
for dp, dn, fn in os.walk(os.path.join(ROOT, 'raw')):
    for f in fn:
        disk.append(os.path.relpath(os.path.join(dp, f), ROOT).replace('\\', '/'))
missing = sorted(set(disk) - sinv)
print('=== files on disk NOT in raw-file-inventory, by folder ===')
for k, v in collections.Counter(m.split('/')[1] for m in missing).most_common():
    print('   %-32s %d' % (k, v))
print('   TOTAL missing:', len(missing))
print('   inventory rows:', len(inv), ' files on disk:', len(disk))
print()

print('=== does the inventory flag the redundant copies itself? ===')
c = collections.Counter(r['sha256'] for r in inv)
redundant = sum(v - 1 for v in c.values() if v > 1)
flagged = [r for r in inv if r.get('dedup') == 'SAME_CONTENT_DIFFERENT_URL']
print('   redundant copies computed by me :', redundant)
print('   rows flagged SAME_CONTENT_DIFFERENT_URL:', len(flagged))
print('   flagged rows that really are a repeat of an earlier sha:',
      len([r for r in flagged if c[r['sha256']] > 1]))
print('   DISTINCT_DOCUMENT rows whose sha256 appears more than once:',
      len([r for r in inv if r.get('dedup') == 'DISTINCT_DOCUMENT' and c[r['sha256']] > 1]))
print()

print('=== quarantine: is the failed capture double counted? ===')
qf = []
for dp, dn, fn in os.walk(os.path.join(ROOT, 'raw', '_failed-captures')):
    for f in fn:
        p = os.path.join(dp, f)
        b = open(p, 'rb').read()
        qf.append((os.path.relpath(p, ROOT).replace('\\', '/'), hashlib.sha256(b).hexdigest(), len(b), b[:5]))
print('   quarantined files on disk:', len(qf))
print('   by folder:', dict(collections.Counter(x[0].split('/')[2] for x in qf)))
print('   distinct sha256 among quarantined:', len({x[1] for x in qf}))
print('   quarantined files whose magic bytes are %PDF:', len([x for x in qf if x[3][:4] == b'%PDF']))
print('   magic byte samples:', collections.Counter(x[3] for x in qf).most_common(5))
qsha = {x[1] for x in qf}

docs = load('arpav-docs-manifest.verified.jsonl')
docs_un = load('arpav-docs-manifest.jsonl')
mon = load('arpav-monthly-manifest.jsonl')
print()
print('   docs manifest rows:', len(docs), ' unverified:', len(docs_un),
      ' same sha set:', {r['sha256'] for r in docs} == {r['sha256'] for r in docs_un})
print('   preserved doc sha256 that ALSO appear in quarantine:',
      len({r['sha256'] for r in docs} & qsha))
print('   preserved monthly sha256 that ALSO appear in quarantine:',
      len({r['sha256'] for r in mon} & qsha))
print('   quarantined paths present in raw-file-inventory:',
      len([x for x in qf if x[0] in sinv]))
print()

failed_docs = load('FAILED-arpav-docs-manifest-htmlshells.jsonl')
failed_mon = load('FAILED-arpav-monthly-manifest-htmlshells.jsonl')
print('   FAILED docs manifest rows:', len(failed_docs), ' distinct sha:', len({r.get('sha256') for r in failed_docs}))
print('   FAILED monthly manifest rows:', len(failed_mon), ' distinct sha:', len({r.get('sha256') for r in failed_mon}))
print('   FAILED docs preservation values:', dict(collections.Counter(r.get('preservation') for r in failed_docs)))
print('   FAILED docs sample row:')
print('   ', json.dumps(failed_docs[0])[:600])
print()

print('=== monthly manifest duplication (download was RUNNING) ===')
print('   rows:', len(mon), ' distinct sha256:', len({r['sha256'] for r in mon}),
      ' distinct raw_path:', len({r['raw_path'] for r in mon}),
      ' distinct source_url:', len({r['source_url'] for r in mon}))
mc = collections.Counter(r['sha256'] for r in mon)
md = {k: v for k, v in mc.items() if v > 1}
print('   monthly sha256 appearing >1:', len(md), ' redundant:', sum(v - 1 for v in md.values()))
for k, v in sorted(md.items(), key=lambda x: -x[1])[:15]:
    t = [(r.get('document_title'), r.get('raw_path')) for r in mon if r['sha256'] == k]
    print('     ', k[:12], 'x', v, t[:6])
inv_mon = load('arpav-monthly-inventory.jsonl')
print('   monthly INVENTORY rows:', len(inv_mon), ' distinct url:',
      len({r.get('source_url') or r.get('api_url') for r in inv_mon}),
      ' distinct title:', len({r.get('document_title') for r in inv_mon}))
