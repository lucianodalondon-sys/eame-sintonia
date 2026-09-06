import json, os, re, subprocess, collections

ROOT = r'C:\disease-local-collection-italy\pilot-disease-local-collection'
D = os.path.join(ROOT, 'raw', 'F8-arpav-agrometeo-docs')
R = [json.loads(l) for l in open(os.path.join(ROOT, 'manifests', 'arpav-docs-manifest.verified.jsonl'), encoding='utf-8')]
ann = sorted([r for r in R if 'annate-agrarie' in r['source_url']], key=lambda x: x['source_url'])
print('annate agrarie rows:', len(ann))

MONTHS = 'gennaio|febbraio|marzo|aprile|maggio|giugno|luglio|agosto|settembre|ottobre|novembre|dicembre'
for r in ann:
    f = os.path.join(D, os.path.basename(r['raw_path']))
    out = subprocess.run(['pdftotext', '-layout', '-f', '1', '-l', '2', f, '-'],
                         capture_output=True)
    t = out.stdout.decode('latin1', 'replace')
    t = re.sub(r'\s+', ' ', t)
    # find explicit period statements
    per = re.findall(r'(?:dal|da)\s+\d{0,2}\s*(?:%s)?\s*\d{4}\s+al?\s+\d{0,2}\s*(?:%s)?\s*\d{4}' % (MONTHS, MONTHS), t, re.I)
    yrs = sorted(set(re.findall(r'\b(19[89]\d|20[0-2]\d)\b', t)))
    print()
    print('%-26s | first-2-pages years seen: %s' % (r['document_title'].strip(), yrs[:14]))
    print('   head:', t[:220].strip())
    if per:
        print('   period phrases:', per[:4])
