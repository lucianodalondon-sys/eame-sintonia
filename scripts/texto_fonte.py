#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TEXTO LIMPO DE UMA FONTE PÚBLICA — ajudante de leitura, sem chave e sem custo.

    python3 scripts/texto_fonte.py eu 32026R1826          # ato da UE, texto integral EN
    python3 scripts/texto_fonte.py gire Lolium            # ficha de espécie do GIRE
    python3 scripts/texto_fonte.py url <endereco>         # qualquer HTML/PDF público

POR QUE ISTO EXISTE
--------------------
Os atos da UE chegam como XHTML de 30-300 KB com marcação de diagramação, e a ficha do
GIRE chega com menu, CSS e contador de visitas em volta do conteúdo. Ler tag a tag gasta
contexto e esconde a frase que decide. Este arquivo devolve só o texto.

    ⛔ ELE NÃO INTERPRETA NADA. Devolve texto. A leitura é de quem chamou.
"""
import html
import io
import re
import sys
import urllib.request

UA = ('Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 '
      '(KHTML, like Gecko) Chrome/126.0 Safari/537.36')
CELLAR = 'https://publications.europa.eu/resource/celex/%s'
GIRE = 'http://gire.mlib.cnr.it/index.php?sel=schedeSpecie/%s'


def _bruto(url, accept=None):
    req = urllib.request.Request(url, headers={
        'User-Agent': UA,
        'Accept': accept or 'text/html,application/xhtml+xml,*/*',
        'Accept-Language': 'eng',
    })
    with urllib.request.urlopen(req, timeout=120) as r:
        return r.read(), (r.headers.get('Content-Type') or '')


def _pdf(dados):
    """PDF sem dependência externa: extrai os literais de texto dos fluxos."""
    try:
        import zlib
    except ImportError:
        return '[PDF: zlib indisponível]'
    saida = []
    for m in re.finditer(rb'stream\r?\n(.*?)endstream', dados, re.S):
        bloco = m.group(1)
        try:
            bloco = zlib.decompress(bloco)
        except Exception:                                        # noqa: BLE001
            continue
        for t in re.findall(rb'\((?:\\.|[^\\()])*\)', bloco):
            s = t[1:-1]
            s = re.sub(rb'\\([()\\])', rb'\1', s)
            try:
                saida.append(s.decode('latin-1'))
            except Exception:                                    # noqa: BLE001
                pass
    txt = ' '.join(saida)
    return re.sub(r'\s+', ' ', txt).strip() or '[PDF sem texto extraível — pode ser imagem]'


def limpar(dados, ctype=''):
    if 'pdf' in ctype.lower() or dados[:5] == b'%PDF-':
        return _pdf(dados)
    t = dados.decode('utf-8', errors='replace')
    t = re.sub(r'<(script|style)\b.*?</\1>', ' ', t, flags=re.S | re.I)
    t = re.sub(r'<[^>]+>', ' ', t)
    t = html.unescape(t)
    t = re.sub(r'[ \t\xa0]+', ' ', t)
    t = re.sub(r'\n\s*\n+', '\n', t)
    return '\n'.join(l.strip() for l in t.split('\n') if l.strip())


def main():
    if len(sys.argv) < 3:
        print(__doc__); return 2
    modo, alvo = sys.argv[1], sys.argv[2]
    url = {'eu': CELLAR % alvo, 'gire': GIRE % alvo}.get(modo, alvo)
    try:
        dados, ctype = _bruto(url)
    except Exception as e:                                       # noqa: BLE001
        print('FALHA_DE_REDE %s: %s' % (type(e).__name__, str(e)[:200])); return 1
    txt = limpar(dados, ctype)
    print('FONTE: %s' % url)
    print('BYTES_BRUTOS: %d · CARACTERES_LIMPOS: %d' % (len(dados), len(txt)))
    print('-' * 70)
    sys.stdout.write(txt)
    return 0


if __name__ == '__main__':
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except Exception:                                            # noqa: BLE001
        pass
    sys.exit(main())
