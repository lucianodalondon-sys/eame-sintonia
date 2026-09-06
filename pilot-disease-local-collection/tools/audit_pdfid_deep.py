import re, json, os, hashlib, collections

rows = [json.loads(l) for l in open('manifests/arpav-docs-manifest.verified.jsonl', encoding='utf-8')]

pats = [
    rb'/ID\s*\[\s*<([0-9A-Fa-f]*)>\s*<([0-9A-Fa-f]*)>\s*\]',
    rb'/ID\s*\[\s*\(([^)]*)\)\s*\(([^)]*)\)\s*\]',
]

noid = []
ids = collections.defaultdict(list)
for r in rows:
    p = r['raw_path']
    d = open(p, 'rb').read()
    found = None
    for pat in pats:
        m = re.findall(pat, d, re.S)
        if m:
            found = m[0][0]
            break
    b = os.path.basename(p)
    if found is None:
        noid.append((b, len(d), d[:9].decode('latin-1'),
                     b'/Encrypt' in d, len(re.findall(rb'/ID', d)),
                     len(re.findall(rb'/Type\s*/XRef', d))))
    else:
        ids[found].append(b)

print('total preserved docs:', len(rows))
print('files with extractable /ID:', sum(len(v) for v in ids.values()))
print('distinct /ID values among those:', len(ids))
dupe = {k: v for k, v in ids.items() if len(v) > 1}
print('/ID values shared by >1 file:', len(dupe))
for k, v in dupe.items():
    print('   SHARED', k[:32], v)
print()
print('files with NO extractable /ID:', len(noid))
print('  name | bytes | header | has/Encrypt | count of "/ID" substr | XRef streams')
for t in noid:
    print('   ', t)
