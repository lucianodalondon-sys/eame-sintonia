#!/usr/bin/env python3
"""O CENSO DAS CLASSES DE ESTRADA DA COLETA ITALIANA.

    python3 system-map/scripts/censo_das_estradas_it.py

A unidade de analise nao e a fonte. E a CLASSE DE ESTRADA — o conjunto de
fontes que compartilham a mesma cadeia operacional:

    DISCOVER -> FETCH -> RAW -> RUN -> CHECKPOINT -> DERIVED
             -> STRUCTURED -> ADMISSION

Uma fonte nova numa estrada ja fechada nao e missao: e configuracao. So estrada
NOVA justifica canario novo.

O vocabulario de classe NAO foi inventado aqui: `leis/social_matriz.py` ja
declara `CLASSE` por rota, e as classes nao-sociais saem do codigo medido. O
que este script faz e CONTAR, para que o mapa em
`docs/operacao/MAPA-DE-FECHAMENTO-DA-COLETA-ITALIANA.md` nunca dependa de
memoria.
"""
import collections
import json
import os
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(os.path.dirname(AQUI))
sys.path.insert(0, RAIZ)
import _gavetas  # noqa: E402,F401
import social_matriz as mz          # noqa: E402
import fundacao_da_coleta as fdc    # noqa: E402

CATALOGO = os.path.join(RAIZ, 'candidatas', 'ITALY-SOURCE-MASTER-V1.json')
SAIDA = os.path.join(RAIZ, 'system-map', 'data', 'estradas-it.generated.json')
LEDGER_GIT = os.path.join(RAIZ, 'data', 'collection-ledger', 'italy')


def fontes_it():
    with open(CATALOGO, encoding='utf-8') as f:
        return json.load(f).get('sources') or []


def rota_conhecida(fonte):
    """A rota da fonte esta declarada, ou o catalogo diz NAO SEI?

    `NAO SEI` e uma resposta legitima e por isso e CONTADA, nunca convertida
    em palpite. Enquanto ela existir, ninguem sabe quantas missoes faltam.
    """
    return not str(fonte.get('ACCESS_METHOD') or '').upper().startswith('NÃO SEI')


def classes_sociais():
    """As classes que a matriz social ja declara, com quantas rotas permitidas."""
    dec, perm, sem_razao = collections.Counter(), collections.Counter(), 0
    for _plat, caps in mz.MATRIZ.items():
        for cap, rotas in caps.items():
            if cap.startswith('_') or not isinstance(rotas, (list, tuple)):
                continue
            for r in rotas:
                if not isinstance(r, dict):
                    continue
                dec[r.get('CLASSE')] += 1
                if r.get('PERMITIDA') == 'SIM':
                    perm[r.get('CLASSE')] += 1
                if not str(r.get('NOTA') or '').strip():
                    sem_razao += 1
    return dec, perm, sem_razao


def apify():
    """Apify e default em alguma rota? A pergunta que a casa mais erra de cabeca."""
    default = fallback = 0
    for _plat, caps in mz.MATRIZ.items():
        for cap, rotas in caps.items():
            if cap.startswith('_') or not isinstance(rotas, (list, tuple)):
                continue
            for r in rotas:
                if isinstance(r, dict) and 'apify' in str(r.get('ROTA', '')).lower():
                    if r.get('PRIORIDADE') == 1:
                        default += 1
                    else:
                        fallback += 1
    return default, fallback


def git_como_banco():
    """Onde o Git ainda guarda estado operacional. Historico nao se apaga."""
    achados = []
    if os.path.isdir(LEDGER_GIT):
        for n in sorted(os.listdir(LEDGER_GIT)):
            caminho = os.path.join(LEDGER_GIT, n)
            with open(caminho, encoding='utf-8', errors='ignore') as f:
                linhas = sum(1 for _ in f)
            achados.append({'FICHEIRO': os.path.relpath(caminho, RAIZ).replace('\\', '/'),
                            'LINHAS': linhas})
    return achados


def main():
    fontes = ordenadas = fontes_it()
    dec, perm, sem_razao = classes_sociais()
    ap_def, ap_fb = apify()
    rel = {
        'SCHEMA': 'estradas-it/v1',
        'PROVENANCE': {
            'CATALOGO': os.path.relpath(CATALOGO, RAIZ).replace('\\', '/'),
            'MATRIZ': 'leis/social_matriz.py',
            'NOTA': ('a CLASSE de rota social vem da matriz, que ja era a dona. '
                     'As classes nao-sociais sao derivadas do codigo medido, e '
                     'estao no mapa em prosa — este ficheiro conta o que da para '
                     'contar sem opinar.'),
        },
        'FONTES_IT': {
            'TOTAL': len(fontes),
            'COM_ROTA_DECLARADA': sum(1 for f in ordenadas if rota_conhecida(f)),
            'ROTA_NAO_SEI': sum(1 for f in ordenadas if not rota_conhecida(f)),
            'POR_PAPEL': dict(collections.Counter(str(f.get('SOURCE_ROLE')) for f in fontes)),
        },
        'CLASSES_SOCIAIS': {
            'DECLARADAS': dict(dec),
            'PERMITIDAS': dict(perm),
            'ROTAS_SEM_RAZAO_ESCRITA': sem_razao,
        },
        'APIFY': {'DEFAULT': ap_def, 'FALLBACK': ap_fb,
                  'NOTA': 'APIFY-LAST: default zero e a leitura correta'},
        'GIT_COMO_BANCO_OPERACIONAL': git_como_banco(),
        'ORQUESTRADOR': {
            'EXISTE': False,
            'PROVA': ('censo_da_coleta.py mede 0 pecas que coordenam mais de um '
                      'executor. SINTONIA SCRAP e COMPOSITE_EXECUTOR: coordena '
                      'rotas de UMA aquisicao, nao o calendario da casa.'),
        },
        'COLLECTION_FOUNDATION_CLOSED': fdc.COLLECTION_FOUNDATION_CLOSED,
    }
    with open(SAIDA, 'w', encoding='utf-8') as f:
        json.dump(rel, f, ensure_ascii=False, indent=1)
    print('FONTES IT %d · rota declarada %d · NAO SEI %d'
          % (rel['FONTES_IT']['TOTAL'], rel['FONTES_IT']['COM_ROTA_DECLARADA'],
             rel['FONTES_IT']['ROTA_NAO_SEI']))
    print('CLASSES SOCIAIS %d · APIFY default %d / fallback %d'
          % (len(dec), ap_def, ap_fb))
    print('GIT COMO BANCO: %d ficheiro(s)' % len(rel['GIT_COMO_BANCO_OPERACIONAL']))
    print('ORQUESTRADOR: nao existe')
    print('COLLECTION_FOUNDATION_CLOSED = %s'
          % ('SIM' if rel['COLLECTION_FOUNDATION_CLOSED'] else 'NAO'))
    print('\nescrito em %s' % os.path.relpath(SAIDA, RAIZ).replace('\\', '/'))


if __name__ == '__main__':
    main()
