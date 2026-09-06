import json, os, re, subprocess, collections

ROOT = r'C:\disease-local-collection-italy\pilot-disease-local-collection'
D = os.path.join(ROOT, 'raw', 'F8-arpav-agrometeo-docs')
R = [json.loads(l) for l in open(os.path.join(ROOT, 'manifests', 'arpav-docs-manifest.verified.jsonl'), encoding='utf-8')]
ann = [r for r in R if 'annate-agrarie' in r['source_url']]

rowsout = []
for r in ann:
    f = os.path.join(D, os.path.basename(r['raw_path']))
    t = subprocess.run(['pdftotext', '-layout', '-f', '1', '-l', '1', f, '-'], capture_output=True).stdout.decode('latin1', 'replace')
    h = re.sub(r'\s+', ' ', t[:300]).strip()
    m = re.search(r'(?:PERIODO\s+[A-Z\-]+|ANNATA)\s+(\d{4})', h, re.I)
    yr = m.group(1) if m else None
    label = re.search(r'(\d{4}(?:-\d{2,4})?)', r['document_title']).group(1)
    rowsout.append((label, yr, h[:110]))

rowsout.sort()
print('%-10s %-10s %s' % ('TITLE-YR', 'DOC-SAYS', 'header (page 1)'))
for a, b, c in rowsout:
    print('%-10s %-10s %s' % (a, b or 'NOT_PARSED', c))

covered = [b for a, b, c in rowsout if b]
print()
print('title labels                :', len(rowsout), ' distinct:', len({a for a, b, c in rowsout}))
print('years the documents THEMSELVES report on:', len(covered), ' distinct:', len(set(covered)))
cc = collections.Counter(covered)
print('years reported by >1 document:', {k: v for k, v in cc.items() if v > 1})
print('span of reported years:', min(covered), '..', max(covered))
allyrs = set(range(int(min(covered)), int(max(covered)) + 1))
print('gaps inside the span:', sorted(allyrs - {int(x) for x in covered}))
print('is calendar year 2000 reported by any document?', '2000' in set(covered))
