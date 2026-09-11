#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RECUPERAR NÃO É RECOLHER — onde está o bruto que a casa já preservou.

    py provas/corpus_recuperar.py            # a tabela
    py provas/corpus_recuperar.py --json     # para o workflow

O QUE ISTO FAZ
---------------
Lê o manifesto que já existe — `TRANSCRICOES-REEL.json`, que carrega o bloco
`RAW` de cada item com `ARTIFACT_ID`, `STORAGE_LOCATION`, `SHA256` e `BYTES` —
e pergunta a ESTA máquina: os bytes estão aqui, e são os mesmos?

    PATH != IDENTIDADE. SHA != OBSERVACAO.

O caminho diz onde procurar. O hash diz se é o mesmo ficheiro. E nenhum dos dois
é a observação: dois RUNs que tragam o mesmo vídeo têm o mesmo `SHA256` e são
duas observações — a lei está escrita no próprio manifesto.

O QUE ISTO NÃO FAZ, E É O PONTO
--------------------------------
Não vai à rede. Não chama YouTube, Apify nem `yt-dlp`. Não descarrega Reel, não
reconstrói áudio e não cria observação nova. Se o byte não estiver aqui, ele
responde `NOT_FOUND` — e `NOT_FOUND` **não** é autorização para ir buscar.

    AUSENCIA DE CORPUS NAO E AUTORIZACAO DE RECOLHER.

⚠️ E a razão de existir: a C4B procurou `C-FanW_CYMz.wav` na máquina local e não
o encontrou, e daí saiu `SEM_CORPUS`. O `.wav` é DERIVADO — quem está preservado
com hash no manifesto é o `.mp4`.

    PROCURAR O ARTEFATO ERRADO DA UMA RESPOSTA VERDADEIRA SOBRE OUTRA COISA.
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import os
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)
import _gavetas                      # noqa: E402,F401

MANIFESTO = os.path.join(RAIZ, 'data', 'samples', 'REEL-TRANSCRICOES',
                         'TRANSCRICOES-REEL.json')
VERDADE = os.path.join(RAIZ, 'data', 'samples', 'REEL-TRANSCRICOES',
                       'QUALIDADE-DA-FALA-V1.json')

RECUPERADO = 'RECOVERED'
HASH_DIFERENTE = 'HASH_MISMATCH'
NAO_ESTA = 'NOT_FOUND'
SEM_MANIFESTO = 'NO_MANIFEST'


def _sha(caminho, pedaco=1 << 20):
    h = hashlib.sha256()
    with io.open(caminho, 'rb') as f:
        for b in iter(lambda: f.read(pedaco), b''):
            h.update(b)
    return h.hexdigest()


def verdade_por_reel():
    """Os termos declarados, por amostra. Sem isto não há qualidade a medir."""
    if not os.path.exists(VERDADE):
        return {}
    with io.open(VERDADE, encoding='utf-8') as f:
        d = json.load(f)
    return {l['REEL']: l for l in d.get('LINHAS') or [] if l.get('REEL')}


def censo():
    if not os.path.exists(MANIFESTO):
        return {'RESULT': SEM_MANIFESTO, 'MANIFESTO': os.path.relpath(MANIFESTO, RAIZ)}
    with io.open(MANIFESTO, encoding='utf-8') as f:
        d = json.load(f)
    gt = verdade_por_reel()

    linhas = []
    for it in d.get('ITEMS') or []:
        r = it.get('RAW') or {}
        if not r.get('STORAGE_LOCATION'):
            continue
        rel = r['STORAGE_LOCATION']
        p = os.path.join(RAIZ, rel)
        # O `REEL` do item e um dicionario de metadados; o id vive no POST_ID.
        alvo = (it.get('REEL') or {})
        rid = alvo.get('POST_ID') if isinstance(alvo, dict) else str(alvo)
        linha = {
            'SAMPLE_ID': rid,
            'ARTIFACT_ID': r.get('ARTIFACT_ID'),
            'STORAGE_LOCATION': rel,
            'SHA256_DECLARADO': r.get('SHA256'),
            'BYTES_DECLARADOS': r.get('BYTES'),
            'GROUND_TRUTH': 'YES' if rid in gt else 'NO',
            'GROUND_TRUTH_TERMOS': (gt.get(rid) or {}).get('TERMOS_ESPERADOS', 0),
        }
        if not os.path.exists(p):
            linha.update({'RESULT': NAO_ESTA, 'BYTES_NO_DISCO': None,
                          'SHA256_NO_DISCO': None})
        else:
            b, h = os.path.getsize(p), _sha(p)
            linha.update({
                'BYTES_NO_DISCO': b, 'SHA256_NO_DISCO': h,
                'RESULT': RECUPERADO if h == r.get('SHA256') else HASH_DIFERENTE,
            })
        linhas.append(linha)

    recuperados = [x for x in linhas if x['RESULT'] == RECUPERADO]
    elegiveis = [x for x in recuperados if x['GROUND_TRUTH'] == 'YES'
                 and (x['GROUND_TRUTH_TERMOS'] or 0) > 0]
    return {
        'PROVA': 'CORPUS_RECOVERY',
        'O_QUE_ISTO_NAO_E': ('nao e coleta. Nao vai a rede, nao cria observacao '
                             'e NOT_FOUND nao autoriza ir buscar.'),
        'MANIFESTO': os.path.relpath(MANIFESTO, RAIZ).replace('\\', '/'),
        'RUNNER_NAME': os.environ.get('RUNNER_NAME') or 'NOT_KNOWN',
        'TOTAL_DECLARADOS': len(linhas),
        'TOTAL_RECUPERADOS': len(recuperados),
        'TOTAL_ELEGIVEIS': len(elegiveis),
        'CORPUS_RECOVERY': RECUPERADO if recuperados else NAO_ESTA,
        'SAMPLE_ELIGIBLE': 'YES' if elegiveis else 'NO',
        'ITEMS': linhas,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--json', action='store_true')
    a = ap.parse_args()
    d = censo()
    if a.json:
        print(json.dumps(d, ensure_ascii=False, indent=1))
    else:
        print('\nRECUPERAR NAO E RECOLHER — o bruto preservado, nesta maquina')
        print('=' * 92)
        print('  %-13s %-9s %-12s %-6s %s'
              % ('AMOSTRA', 'VERDADE', 'RESULTADO', 'TERMOS', 'ONDE'))
        print('  ' + '-' * 88)
        for x in d.get('ITEMS') or []:
            print('  %-13s %-9s %-12s %-6s %s'
                  % (str(x['SAMPLE_ID'])[:13], x['GROUND_TRUTH'], x['RESULT'],
                     x['GROUND_TRUTH_TERMOS'], x['STORAGE_LOCATION']))
        print('\n  CORPUS_RECOVERY = %s · recuperados %s/%s · elegiveis %s'
              % (d.get('CORPUS_RECOVERY'), d.get('TOTAL_RECUPERADOS'),
                 d.get('TOTAL_DECLARADOS'), d.get('TOTAL_ELEGIVEIS')))
        print('  (NOT_FOUND nao autoriza recolher — e uma medicao desta maquina)\n')
    return 0 if d.get('CORPUS_RECOVERY') == RECUPERADO else 1


if __name__ == '__main__':
    raise SystemExit(main())
