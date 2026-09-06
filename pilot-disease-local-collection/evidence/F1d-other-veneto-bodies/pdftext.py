import re, sys, zlib

TERMS = ['peronospora', 'oidio', 'botrite', 'flavescenza', 'scaphoideus', 'tignoletta',
         'vite', 'vigneto', 'BBCH', 'grappolo', 'bollettino', 'fitosanitar',
         'Regione del Veneto', 'infezion', 'trattament', 'plasmopara', 'erysiphe',
         'mal dell', 'cocciniglia', 'Lobesia', 'Erasmoneura', 'giallumi']

for path in sys.argv[1:]:
    raw = open(path, 'rb').read()
    out = []
    for m in re.finditer(rb'stream\r?\n', raw):
        start = m.end()
        end = raw.find(b'endstream', start)
        if end < 0:
            continue
        chunk = raw[start:end]
        try:
            d = zlib.decompress(chunk)
        except Exception:
            continue
        # pull text-showing operators
        for t in re.findall(rb'\((?:\\.|[^\\()])*\)', d):
            s = t[1:-1]
            s = re.sub(rb'\\([()\\])', rb'\1', s)
            try:
                out.append(s.decode('latin-1'))
            except Exception:
                pass
    text = ' '.join(out)
    text = re.sub(r'\s+', ' ', text)
    print("=====", path, "| extracted chars:", len(text))
    low = text.lower()
    hits = [(t, low.count(t.lower())) for t in TERMS if t.lower() in low]
    print("  TERM HITS:", hits if hits else "NONE")
    print("  SAMPLE:", text[:700].strip())
    print()
