"""INDEPENDENT verification of C5 (26 Annate agrarie -> 26 distinct seasons 2000-01..2025).

Does NOT reuse any prior audit script. Extracts page-1 text with pdftotext and
reports, per file, the reporting period the PDF declares about ITSELF.
Read-only: touches nothing under raw/ or manifests/ except reading.
"""
import json, re, subprocess, sys, os
from collections import Counter, defaultdict

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
MAN = os.path.join(ROOT, 'manifests', 'arpav-docs-manifest.verified.jsonl')

rows = [json.loads(l) for l in open(MAN, encoding='utf-8')]
ann = [r for r in rows if '/annate-agrarie/' in r['source_url']]
print('annate-agrarie files in manifest:', len(ann))

MONTHS = ('gennaio febbraio marzo aprile maggio giugno luglio agosto '
          'settembre ottobre novembre dicembre').split()
MRE = '|'.join(MONTHS)


def page1(path):
    out = subprocess.run(['pdftotext', '-f', '1', '-l', '1', '-layout', path, '-'],
                         capture_output=True)
    return out.stdout.decode('latin-1', 'replace')


def firstpages(path, n=2):
    out = subprocess.run(['pdftotext', '-f', '1', '-l', str(n), '-layout', path, '-'],
                         capture_output=True)
    return out.stdout.decode('latin-1', 'replace')


results = []
for r in ann:
    p = os.path.join(ROOT, r['raw_path'].replace('/', os.sep))
    txt = page1(p)
    flat = re.sub(r'\s+', ' ', txt)
    head = flat[:400]

    # 1) explicit declared period: "RELATIVO AL PERIODO <MONTH>-<MONTH> <YYYY>"
    m = re.search(r'RELATIVO\s+AL\s+PERIODO\s+([A-Za-z]+)\s*[-–]\s*([A-Za-z]+)\s+(\d{4})',
                  flat, re.I)
    # 2) "ANDAMENTO ... ANNATA <YYYY>" / "ANNATA AGRARIA <YYYY>"
    m2 = re.search(r'ANNATA\s+(?:AGRARIA\s+)?(\d{4})', flat, re.I)
    # 3) any "<month> <YYYY>" mentions -> year histogram
    mm = Counter(y for _, y in re.findall(r'\b(%s)\s+(\d{4})\b' % MRE, flat, re.I))

    if m:
        declared = m.group(3)
        how = 'RELATIVO AL PERIODO %s-%s %s' % (m.group(1), m.group(2), m.group(3))
    elif m2:
        declared = m2.group(1)
        how = 'ANNATA ... %s' % m2.group(1)
    elif mm:
        declared = mm.most_common(1)[0][0]
        how = 'month+year modal = %s (%s)' % (declared, dict(mm))
    else:
        declared = 'NOT_PARSED'
        how = 'no period statement found on page 1'

    results.append({
        'title': r['document_title'],
        'slug': r['source_url'].rsplit('/', 3)[-3],
        'raw': r['raw_path'],
        'declared_year': declared,
        'how': how,
        'head': head[:220],
    })

print()
print('%-26s %-10s  %s' % ('TITLE LABEL', 'DECLARED', 'BASIS'))
print('-' * 100)
for x in sorted(results, key=lambda z: z['slug']):
    print('%-26s %-10s  %s' % (x['title'][:26], x['declared_year'], x['how'][:60]))

years = [x['declared_year'] for x in results]
c = Counter(years)
print()
print('files                :', len(results))
print('DISTINCT declared yrs:', len(set(years)))
print('declared twice       :', {k: v for k, v in c.items() if v > 1})
num = sorted(y for y in years if y.isdigit())
print('span                 :', num[0], '..', num[-1])
print('year 2000 declared?  :', '2000' in years)
print('NOT_PARSED           :', [x['title'] for x in results if x['declared_year'] == 'NOT_PARSED'])
print('title-label years    :', len(set(x['slug'] for x in results)))

# where a title label disagrees with what the doc declares
print()
print('TITLE-LABEL vs DECLARED mismatches:')
for x in sorted(results, key=lambda z: z['slug']):
    lab = re.search(r'(\d{4})(?:-(\d{2}))?', x['slug'])
    if not lab:
        continue
    y1 = lab.group(1)
    if x['declared_year'] != y1:
        print('  %-26s label-start %s -> declares %s' % (x['title'][:26], y1, x['declared_year']))

json.dump(results, open(os.path.join(ROOT, 'tools', '_verify_c5.json'), 'w'), indent=1)
