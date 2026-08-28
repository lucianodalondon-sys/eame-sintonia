#!/usr/bin/env python3
"""
Leitor da EPPO Global Database (gd.eppo.int) — nomes multilíngues por código EPPO.

A API REST da EPPO exige token (EU-T3-001 = NÃO SEI). A página pública do táxon,
porém, responde 200 e traz os nomes comuns por idioma. Este módulo busca UMA página
por código, com cache em disco, para não repetir requisição — não é varredura.

    python3 scripts/eppo_gd.py PLASVI VITVI
"""
import os, re, sys, html, json, time, urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CACHE = os.path.join(ROOT, 'data', 'raw', 'EPPO-CACHE')
UA = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/126.0 Safari/537.36'}
LANGS = ('French', 'Spanish', 'Italian', 'English', 'German', 'Portuguese', 'Dutch', 'Danish')


def _fetch(code):
    os.makedirs(CACHE, exist_ok=True)
    # alguns códigos do dicionário espanhol vêm com barra ("ANTNO/MATCH"); o nome de
    # arquivo precisa ser saneado ou a escrita do cache estoura
    safe = re.sub(r'[^A-Za-z0-9_-]', '_', code)
    p = os.path.join(CACHE, f'{safe}.html')
    if os.path.exists(p):
        with open(p, encoding='utf-8', errors='replace') as f:
            return f.read()
    req = urllib.request.Request(f'https://gd.eppo.int/taxon/{code}', headers=UA)
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            t = r.read().decode('utf-8', 'replace')
    except Exception as e:
        t = f'<!--FETCH_ERROR {type(e).__name__}-->'
    with open(p, 'w', encoding='utf-8') as f:
        f.write(t)
    time.sleep(0.7)          # cortesia com a fonte
    return t


def names(code):
    """{'French': [...], 'Spanish': [...], ...} + 'preferred' e 'ok'."""
    t = _fetch(code)
    if 'FETCH_ERROR' in t[:80] or 'Page not found' in t:
        return {'ok': False, 'preferred': None}
    txt = re.sub(r'<[^>]+>', ' ', t)
    txt = re.sub(r'\s+', ' ', html.unescape(txt))
    out = {'ok': True, 'preferred': None}
    m = re.search(r'Preferred name:?\s*([A-Z][a-zé\- ]+?)\s+(?:Authority|Other names|Taxonomy)', txt)
    if m:
        out['preferred'] = m.group(1).strip()
    # A tabela de nomes vira a sequência "<nome> <Idioma> <nome> <Idioma> ...".
    # Cada nome é o texto ENTRE o marcador de idioma anterior e o atual — varrer em
    # ordem evita que o nome de um idioma arraste a cauda do anterior.
    blk = txt
    i = blk.find('Common names')
    if i > 0:
        blk = blk[i + len('Common names'):]
    for tail in ('Taxonomy', 'more photos', 'Categorization'):
        j = blk.find(tail)
        if j > 0:
            blk = blk[:j]
    blk = re.sub(r'^\s*Name\s+Language\s*', '', blk)
    marks = list(re.finditer(r'\b(' + '|'.join(LANGS) + r')\b', blk))
    prev = 0
    for m in marks:
        name = blk[prev:m.start()].strip(' .,;')
        prev = m.end()
        if not (2 < len(name) <= 70):
            continue
        out.setdefault(m.group(1), [])
        if name.lower() not in {v.lower() for v in out[m.group(1)]}:
            out[m.group(1)].append(name)
    return out


if __name__ == '__main__':
    for c in sys.argv[1:]:
        n = names(c)
        print(f'== {c} | preferred: {n.get("preferred")} | ok={n["ok"]}')
        for l in LANGS:
            if n.get(l):
                print(f'   {l:11s}: {n[l][:5]}')
