"""Fechamento — casco de deploy depois do patch de uma linha.

Reusa o medidor de scripts/v8_receptor_ready.py apontando para outra testemunha.
Duplicar o medidor criaria dois que podem divergir, e a divergencia apareceria
como "o casco melhorou" quando so o medidor mudou.

Uso:
    py scripts/v8_receptor_closeout.py            # imprime
    py scripts/v8_receptor_closeout.py --sync     # grava o artefato
"""
import gzip
import json
import os
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(RAIZ, 'scripts'))

from v8_receptor_ready import medir as medir_com  # noqa: E402

DEPLOY = os.path.join(RAIZ, 'casco', 'canonical', 'deploy-v8-closeout')
INDEX_GZ = os.path.join(DEPLOY, 'deploy-index.html.gz')
SUPPORT = os.path.join(DEPLOY, 'support.js')
CROPMAP = os.path.join(DEPLOY, 'crop-map.js')
SAIDA = os.path.join(RAIZ, 'data', 'implementation', 'V8-RECEPTOR-CLOSEOUT.json')

SHAS = {
    'INDEX': 'd28f6b5876e2fa28720eb555a8b99a275e56c229ed0ac5c4b07edf89f4e81328',
    'SUPPORT': '8fe7df74405f3c55f49b7249c74ea1397e65d07dea2b1bd3b4a489bec2e28cbe',
    'CROPMAP': 'a55c6011e6aadb014b2617c8f5b302d9d2fb4bbfb1ee3e444cad345bbb1614c8',
    'ZIP': 'b1256d71708cfaae97b20756c18a67774cf3bdb826bb909404a6222d6f5c925b',
    'INDEX_BYTES': 372425,
}

# a testemunha anterior, para o diff de uma linha ser verificavel
ANTERIOR_GZ = os.path.join(RAIZ, 'casco', 'canonical', 'deploy-v8-receptor-ready',
                           'deploy-index.html.gz')
SHA_ANTERIOR = 'a103bd62e3bbe92cbd56dd5b0da43a878fe4244db7bfbf89d683eaea8b024dc8'


def abrir():
    with open(INDEX_GZ, 'rb') as fh:
        idx = gzip.decompress(fh.read()).decode('utf-8', 'replace')
    with open(SUPPORT, encoding='utf-8', errors='replace') as fh:
        sup = fh.read()
    with open(CROPMAP, encoding='utf-8', errors='replace') as fh:
        mapa = fh.read()
    return idx, sup, mapa


def abrir_anterior():
    with open(ANTERIOR_GZ, 'rb') as fh:
        return gzip.decompress(fh.read()).decode('utf-8', 'replace')


def diff_de_linhas():
    """As linhas que mudaram entre a testemunha anterior e esta."""
    import difflib
    antes, agora = abrir_anterior(), abrir()[0]
    saida = []
    for linha in difflib.unified_diff(antes.split('\n'), agora.split('\n'),
                                      'antes', 'agora', lineterm='', n=0):
        if linha[:1] in '+-' and not linha.startswith(('+++', '---')):
            saida.append(linha)
    return saida


def medir():
    m = medir_com(fontes=abrir(), shas=SHAS)
    d = diff_de_linhas()
    m['DIFF_CONTRA_TESTEMUNHA_ANTERIOR'] = {
        'SHA_ANTERIOR': SHA_ANTERIOR,
        'LINHAS_ALTERADAS': len(d),
        'LINHAS': d,
        'BYTES_A_MAIS': SHAS['INDEX_BYTES'] - 372418,
        'NOTA': ('7 bytes a mais e o tamanho exato de "_ENTITY". support.js e '
                 'crop-map.js tem SHA identico ao export anterior: so o index mudou.'),
    }
    return m


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    m = medir()
    if '--sync' in sys.argv:
        with open(SAIDA, 'w', encoding='utf-8', newline='\n') as fh:
            json.dump(m, fh, ensure_ascii=False, indent=2)
            fh.write('\n')
        print('gravado em', os.path.relpath(SAIDA, RAIZ))
    v = dict(m['VERDICTS'])
    v.pop('HOSES'), v.pop('SUBRECEPTORES')
    print(json.dumps(v, ensure_ascii=False, indent=2))
    print('\nENTITY_KIND:', json.dumps(m['ENTITY_KIND'], ensure_ascii=False))
    print('DIFF:', json.dumps(m['DIFF_CONTRA_TESTEMUNHA_ANTERIOR'], ensure_ascii=False, indent=1))
