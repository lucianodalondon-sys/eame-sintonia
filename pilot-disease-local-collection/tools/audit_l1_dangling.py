import json, os

ROOT = r'C:\disease-local-collection-italy\pilot-disease-local-collection'
for name in ['FAILED-arpav-docs-manifest-htmlshells.jsonl', 'FAILED-arpav-monthly-manifest-htmlshells.jsonl']:
    R = [json.loads(l) for l in open(os.path.join(ROOT, 'manifests', name), encoding='utf-8')]
    ex = 0
    for r in R:
        if os.path.exists(os.path.join(ROOT, r['raw_path'].replace('/', os.sep))):
            ex += 1
    print(name)
    print('   rows:', len(R), ' raw_path exists on disk:', ex, ' DANGLING:', len(R) - ex)
    print('   preservation values:', {r.get('preservation') for r in R})
    print('   dedup values       :', {r.get('dedup') for r in R})
    print('   media_type values  :', {r.get('media_type') for r in R})
    print('   sample raw_path    :', R[0]['raw_path'])
    print()

# how many distinct SOURCE DOCUMENTS do the F8 manifests really describe?
ok = [json.loads(l) for l in open(os.path.join(ROOT, 'manifests', 'arpav-docs-manifest.verified.jsonl'), encoding='utf-8')]
bad = [json.loads(l) for l in open(os.path.join(ROOT, 'manifests', 'FAILED-arpav-docs-manifest-htmlshells.jsonl'), encoding='utf-8')]
print('F8: rows saying PRESERVED across the two manifests:', len(ok) + len(bad))
print('F8: distinct source_url (after stripping /@@download/file):',
      len({r['source_url'].replace('/@@download/file', '') for r in ok + bad}))
print('F8: distinct sha256 across the two manifests:', len({r['sha256'] for r in ok + bad}))
print('F8: real PDFs actually on disk:',
      len([f for f in os.listdir(os.path.join(ROOT, 'raw', 'F8-arpav-agrometeo-docs'))]))
print('F8: same source document appearing in BOTH manifests:',
      len({r['source_url'].replace('/@@download/file', '') for r in ok} &
          {r['source_url'].replace('/@@download/file', '') for r in bad}))

mon = [json.loads(l) for l in open(os.path.join(ROOT, 'manifests', 'arpav-monthly-manifest.jsonl'), encoding='utf-8')]
monbad = [json.loads(l) for l in open(os.path.join(ROOT, 'manifests', 'FAILED-arpav-monthly-manifest-htmlshells.jsonl'), encoding='utf-8')]
print()
print('F7 monthly: PRESERVED rows across the two manifests:', len(mon) + len(monbad))
print('F7 monthly: distinct source_url:',
      len({r['source_url'].replace('/@@download/file', '') for r in mon + monbad}))
print('F7 monthly: same source document in BOTH manifests:',
      len({r['source_url'].replace('/@@download/file', '') for r in mon} &
          {r['source_url'].replace('/@@download/file', '') for r in monbad}))
print('F7 monthly: files on disk:', len(os.listdir(os.path.join(ROOT, 'raw', 'F7-arpav-bollettino-mese'))))
print('F7 monthly: inventory rows:',
      sum(1 for _ in open(os.path.join(ROOT, 'manifests', 'arpav-monthly-inventory.jsonl'), encoding='utf-8')))
