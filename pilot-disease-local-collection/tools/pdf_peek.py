"""Read a PDF's own declared dates and a crude text sample, using only the
Python standard library (no pip install into this repo).

This is deliberately conservative:
  - /CreationDate and /ModDate come from the PDF's own metadata.
  - Text extraction is crude (Flate streams + text-showing operators). If it
    fails, the result is TEXT_EXTRACTION_FAILED, never "no text".
A term found in the text is a LEXICAL MENTION, not an observation of disease.
"""
import re, sys, zlib


def meta_dates(raw):
    out = {}
    for key in (b'CreationDate', b'ModDate'):
        m = re.search(rb'/' + key + rb'\s*\(\s*(D:)?(\d{4})(\d{2})(\d{2})', raw)
        if m:
            y, mo, d = (g.decode('ascii') for g in m.group(2, 3, 4))
            out[key.decode()] = f'{y}-{mo}-{d}'
        else:
            out[key.decode()] = 'NOT_DECLARED'
    return out


def crude_text(raw, limit=200000):
    chunks = []
    for m in re.finditer(rb'stream\r?\n', raw):
        start = m.end()
        end = raw.find(b'endstream', start)
        if end < 0:
            continue
        blob = raw[start:end]
        try:
            blob = zlib.decompress(blob)
        except Exception:
            continue
        chunks.append(blob)
        if sum(len(c) for c in chunks) > limit:
            break
    if not chunks:
        return None
    txt = []
    for c in chunks:
        for m in re.finditer(rb'\((?:\\.|[^()\\])*\)', c):
            s = m.group(0)[1:-1]
            s = re.sub(rb'\\([()\\])', rb'\1', s)
            try:
                txt.append(s.decode('latin-1'))
            except Exception:
                pass
    return ' '.join(txt)


for path in sys.argv[1:]:
    raw = open(path, 'rb').read()
    print('=' * 72)
    print(path, f'({len(raw)} bytes)')
    print('  pdf metadata dates:', meta_dates(raw))
    t = crude_text(raw)
    if t is None:
        print('  TEXT_EXTRACTION_FAILED (no decodable Flate stream) — content NOT read')
        continue
    t = re.sub(r'\s+', ' ', t)
    print(f'  text chars extracted: {len(t)}')
    dates = sorted(set(re.findall(r'\b(?:0?[1-9]|[12]\d|3[01])[/.-](?:0?[1-9]|1[0-2])[/.-](?:19|20)\d\d\b', t)))
    years = sorted(set(re.findall(r'\b(?:19|20)\d\d\b', t)))
    print('  dates in text (first 12):', dates[:12] or 'NONE_FOUND')
    print('  years in text:', years[:20] or 'NONE_FOUND')
    for term in ('vite', 'peronospora', 'Plasmopara', 'oidio', 'Erysiphe',
                 'bagnatura', 'infezione', 'incidenza', 'focolai'):
        n = len(re.findall(term, t, re.I))
        if n:
            print(f'    LEXICAL MENTION "{term}" x{n}  (mention, NOT an observation)')
    print('  sample:', t[:400])
