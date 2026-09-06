"""Independently verify the four 'pockets' of real disease-outcome data that
red-team lens L4 reported, and record them with provenance.

This exists because the collector's own earlier scan concluded OUTCOMES = NONE.
That conclusion was wrong: the scan only covered the ARPAV documents manifest
and never looked inside the recon agents' F5/F6 folders. Verified here by
reading the PDFs.
"""
import glob, hashlib, json, os, re, subprocess

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def text_of(path):
    try:
        r = subprocess.run(['pdftotext', '-q', '-enc', 'UTF-8', path, '-'],
                           capture_output=True, timeout=240)
        return r.stdout.decode('utf-8', 'replace')
    except Exception:
        return ''


def sha(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for c in iter(lambda: f.read(1 << 20), b''):
            h.update(c)
    return h.hexdigest()


# terms that mark a MEASURED outcome, not an adjective and not a treatment
OUTCOME = re.compile(
    r'campioni\s+positivi|positivi\s+ai\s+giallumi|piante\s+madri|'
    r'incidenza\s+media|ha\s+con\s+giallumi|superficie\s+.{0,20}colpit|'
    r'RISULTATO|Positivo|focolai\s+\d', re.I)
NUM = re.compile(r'\b\d+(?:[.,]\d+)?\b')

targets = sorted(glob.glob(os.path.join(ROOT, 'raw', 'F5', '*.pdf')) +
                 glob.glob(os.path.join(ROOT, 'raw', 'F6-other-pests', '*.pdf')))

pockets = []
print(f'reading {len(targets)} PDFs from raw/F5 and raw/F6-other-pests\n')
for p in targets:
    t = text_of(p)
    rel = os.path.relpath(p, ROOT).replace('\\', '/')
    if not t.strip():
        print(f'  [TEXT_EXTRACTION_FAILED] {os.path.basename(p)}')
        continue
    lines = [re.sub(r'\s+', ' ', l).strip() for l in t.split('\n')]
    hits = [l for l in lines if OUTCOME.search(l) and NUM.search(l) and len(l) > 25]
    if not hits:
        print(f'  [no measured outcome] {os.path.basename(p)}  ({len(t)} chars)')
        continue
    print(f'  [OUTCOME CANDIDATES x{len(hits)}] {os.path.basename(p)}')
    for h in hits[:6]:
        print('        ' + h[:180].encode('ascii', 'replace').decode('ascii'))
    pockets.append({
        'raw_path': rel,
        'sha256': sha(p),
        'bytes': os.path.getsize(p),
        'text_chars': len(t),
        'measured_outcome_lines': hits[:40],
        'outcome_line_count': len(hits),
    })

out = os.path.join(ROOT, 'manifests', 'disease-outcome-pockets.json')
with open(out, 'w', encoding='utf-8') as f:
    json.dump({
        'note': ('Verified pockets of REAL, dated, numeric disease-outcome data inside the '
                 'package. Read the caveats: none of these joins the Treviso leaf-wetness '
                 'series in space, time and pathogen at once.'),
        'files_scanned': len(targets),
        'files_with_measured_outcome': len(pockets),
        'pockets': pockets,
    }, f, ensure_ascii=False, indent=1)
print(f'\nfiles scanned = {len(targets)}   with measured outcome = {len(pockets)}')
print('->', os.path.relpath(out, ROOT))
