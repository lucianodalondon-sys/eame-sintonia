"""Scan preserved PDFs for DISEASE OUTCOME evidence, and classify honestly.

The distinction this script exists to protect:
  LEXICAL_MENTION_ONLY  the word appears (e.g. in a fungicide target list)
  QUALITATIVE_ONLY      the source describes pressure in words ("elevata",
                        "sporadiche") but publishes no number
  NUMERIC_CANDIDATE     a number appears in the SAME sentence as a disease term
                        AND next to an outcome word (incidenza, gravita,
                        focolai, superficie colpita, % di piante)

NUMERIC_CANDIDATE is a CANDIDATE, not a confirmed outcome series. A human must
read it. Nothing here converts an adjective into a number.
"""
import json, os, re, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PDFTOTEXT = 'pdftotext'

DISEASE = re.compile(r'peronospora|plasmopara|oidio|erysiphe|botrite|botrytis|flavescenza', re.I)
OUTCOME = re.compile(
    r'incidenz|gravit|severit|focolai|infezion[ei]\s+(?:su|del|nel)|'
    r'%\s*(?:di\s*)?(?:piante|grappoli|foglie|superficie)|'
    r'superficie\s+colpit|piante\s+colpit|grappoli\s+colpit|'
    r'campion|monitorat|parcell|rilievi', re.I)
NUMBER = re.compile(r'\b\d+(?:[.,]\d+)?\s*(?:%|ha\b|ettari|piante|grappoli|focolai|casi)\b', re.I)


def text_of(path):
    try:
        out = subprocess.run([PDFTOTEXT, '-q', '-enc', 'UTF-8', path, '-'],
                             capture_output=True, timeout=180)
        if out.returncode != 0 and not out.stdout:
            return None
        return out.stdout.decode('utf-8', 'replace')
    except Exception:
        return None


def classify(txt):
    if txt is None:
        return 'TEXT_EXTRACTION_FAILED', [], 0
    sentences = re.split(r'(?<=[.!?;:])\s+|\n{2,}', txt)
    hits = []
    n_disease = len(DISEASE.findall(txt))
    for s in sentences:
        if not DISEASE.search(s):
            continue
        has_num = bool(NUMBER.search(s))
        has_out = bool(OUTCOME.search(s))
        if has_num and has_out:
            hits.append(re.sub(r'\s+', ' ', s.strip())[:300])
    if hits:
        return 'NUMERIC_CANDIDATE', hits, n_disease
    if n_disease:
        return 'QUALITATIVE_OR_MENTION_ONLY', [], n_disease
    return 'NO_DISEASE_TERM', [], 0


manifest = sys.argv[1]
url_filter = sys.argv[2] if len(sys.argv) > 2 else ''
rows = [json.loads(l) for l in open(os.path.join(ROOT, manifest), encoding='utf-8') if l.strip()]
rows = [r for r in rows if r.get('preservation') == 'PRESERVED' and url_filter in r.get('source_url', '')]
print(f'scanning {len(rows)} preserved documents from {manifest}')

results = []
counts = {}
for r in rows:
    p = os.path.join(ROOT, r['raw_path'])
    txt = text_of(p)
    state, hits, n = classify(txt)
    counts[state] = counts.get(state, 0) + 1
    results.append({'title': r.get('document_title'), 'url': r['source_url'],
                    'raw_path': r['raw_path'], 'sha256': r.get('sha256'),
                    'outcome_state': state, 'disease_term_hits': n,
                    'numeric_candidate_sentences': hits,
                    'text_chars': len(txt) if txt else 0})
    print(f'  [{state:28}] terms={n:4d} chars={len(txt) if txt else 0:7d}  {r.get("document_title")}')

out = os.path.join(ROOT, 'manifests', 'disease-outcome-scan.json')
prev = []
if os.path.exists(out):
    prev = json.load(open(out, encoding='utf-8')).get('documents', [])
allrows = prev + results
with open(out, 'w', encoding='utf-8') as f:
    json.dump({'note': ('NUMERIC_CANDIDATE means a number and an outcome word share a '
                        'sentence with a disease term. It is a CANDIDATE for human '
                        'reading, NOT a confirmed disease outcome series.'),
               'documents': allrows}, f, ensure_ascii=False, indent=1)
print()
print('summary:', counts)
print('->', os.path.relpath(out, ROOT))
