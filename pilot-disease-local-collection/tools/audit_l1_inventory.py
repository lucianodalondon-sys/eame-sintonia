import json, hashlib, os, collections

ROOT = r'C:\disease-local-collection-italy\pilot-disease-local-collection'
INV = os.path.join(ROOT, 'manifests', 'raw-file-inventory.jsonl')

R = [json.loads(l) for l in open(INV, encoding='utf-8')]
print('inventory rows:', len(R))
print('distinct raw_path:', len({r['raw_path'] for r in R}))
print('distinct sha256 :', len({r['sha256'] for r in R}))
print()
print('by dedup field:', dict(collections.Counter(r.get('dedup') for r in R)))
print()
print('by extension:')
for k, v in collections.Counter(r.get('ext') for r in R).most_common():
    print('   %-8s %d' % (k, v))
print()
print('by front:')
for k, v in collections.Counter(r.get('front') for r in R).most_common():
    print('   %-32s %d' % (k, v))
print()
# does the inventory include tool scripts?
py = [r for r in R if r['raw_path'].endswith('.py')]
print('*** .py files inside raw-file-inventory:', len(py))
for r in py[:40]:
    print('    ', r['raw_path'], r['bytes'], r.get('dedup'))
print()
fail = [r for r in R if '_failed-captures' in r['raw_path']]
print('*** rows under raw/_failed-captures inside raw-file-inventory:', len(fail))
print('    their dedup values:', dict(collections.Counter(r.get('dedup') for r in fail)))
for r in fail[:6]:
    print('    ', r['raw_path'], r['bytes'], r.get('dedup'), r.get('duplicate_of'))
print()
html = [r for r in R if r.get('ext') in ('.html', '.htm')]
print('*** .html/.htm rows:', len(html), ' of which under _failed-captures:',
      len([r for r in html if '_failed-captures' in r['raw_path']]))

# actual files on disk under raw/
disk = []
for dp, dn, fn in os.walk(os.path.join(ROOT, 'raw')):
    for f in fn:
        disk.append(os.path.relpath(os.path.join(dp, f), ROOT).replace('\\', '/'))
print()
print('*** files actually on disk under raw/:', len(disk))
sinv = {r['raw_path'] for r in R}
sd = set(disk)
print('    in inventory but not on disk:', len(sinv - sd))
for x in sorted(sinv - sd)[:10]:
    print('       ', x)
print('    on disk but not in inventory:', len(sd - sinv))
for x in sorted(sd - sinv)[:20]:
    print('       ', x)

# duplicate sha256 across the whole raw tree
c = collections.Counter(r['sha256'] for r in R)
dups = {k: v for k, v in c.items() if v > 1}
print()
print('*** sha256 present in >1 raw file:', len(dups), ' total files involved:', sum(dups.values()),
      ' redundant copies:', sum(v - 1 for v in dups.values()))
for k, v in sorted(dups.items(), key=lambda x: -x[1])[:25]:
    paths = [r['raw_path'] for r in R if r['sha256'] == k]
    print('   ', k[:12], 'x', v, paths[:6])
