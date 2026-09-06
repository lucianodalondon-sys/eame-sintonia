"""L4 AUDIT — hunt for a DATED NUMERIC disease-outcome value in the preserved corpus.

Read-only. Extracts text with pdftotext, then looks for a disease name within
120 characters of a number that carries an outcome unit (%, ha, n., casi,
focolai, campioni, positivi). Prints every hit so a human can judge it.
"""
import os, re, subprocess, sys, json

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(os.environ.get('TEMP', '/tmp'), 'l4txt')
os.makedirs(OUT, exist_ok=True)

DISEASE = re.compile(
    r'peronospor\w*|oidio|erysiphe|plasmopara|botrite|botrytis|flavescenz\w*|'
    r'legno nero|bois noir|mal dell.esca|black rot|escoriosi|marciume', re.I)
# a number followed by an outcome-bearing unit
OUTCOME = re.compile(
    r'(\d[\d.,]*)\s*(%|ha\b|ettar\w+|focolai|casi|campion\w+|positiv\w+|'
    r'piante|ceppi|vigneti|aziende)', re.I)


def totext(pdf, tag):
    dst = os.path.join(OUT, tag + '.txt')
    if not os.path.exists(dst):
        subprocess.run(['pdftotext', '-layout', pdf, dst],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        return open(dst, encoding='utf-8', errors='replace').read()
    except Exception:
        return ''


def scan(txt):
    flat = re.sub(r'\s+', ' ', txt)
    hits = []
    for m in DISEASE.finditer(flat):
        lo = max(0, m.start() - 120)
        hi = min(len(flat), m.end() + 120)
        win = flat[lo:hi]
        for n in OUTCOME.finditer(win):
            hits.append((m.group(0), n.group(0), win.strip()))
            break
    return hits


targets = []
man = [json.loads(l) for l in open(os.path.join(ROOT, 'manifests', 'arpav-docs-manifest.jsonl'),
                                   encoding='utf-8') if l.strip()]
for r in man:
    targets.append((os.path.join(ROOT, r['raw_path'].replace('/', os.sep)),
                    'F8_' + re.sub(r'\W+', '_', r['document_title'].strip())[:40],
                    'F8 ' + r['document_title'].strip()))
for f in sorted(os.listdir(os.path.join(ROOT, 'raw', 'F5'))):
    if f.lower().endswith('.pdf'):
        targets.append((os.path.join(ROOT, 'raw', 'F5', f),
                        'F5_' + re.sub(r'\W+', '_', f)[:40], 'F5 ' + f))
for f in sorted(os.listdir(os.path.join(ROOT, 'raw', 'F2b'))):
    if f.lower().endswith('.pdf'):
        targets.append((os.path.join(ROOT, 'raw', 'F2b', f),
                        'F2b_' + re.sub(r'\W+', '_', f)[:40], 'F2b ' + f))

grand = 0
for path, tag, label in targets:
    if not os.path.exists(path):
        print('MISSING', label)
        continue
    txt = totext(path, tag)
    hits = scan(txt)
    ndis = len(DISEASE.findall(txt))
    print('%-58s textchars=%7d  disease_mentions=%4d  numeric_adjacent=%3d'
          % (label[:58], len(txt), ndis, len(hits)))
    grand += len(hits)
    for d, n, w in hits[:3]:
        print('      [%s | %s]  ...%s...' % (d, n, w[:190]))
print('\nTOTAL numeric-adjacent disease windows:', grand)
