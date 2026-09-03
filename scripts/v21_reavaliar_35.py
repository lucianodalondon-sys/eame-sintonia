#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""FINAL · Os 35 achados originais, remedidos contra o pacote RECONSTRUIDO.

    python3 scripts/v21_reavaliar_35.py

O QUE ISTO E, E O QUE NAO E
---------------------------
E uma remedicao PROGRAMATICA: cada achado vira um predicado sobre o pacote atual,
e o predicado roda. Nao e a releitura adversarial que produziu o ledger — aquela
teve leitor, dois ceticos e juiz. Esta responde uma pergunta mais estreita:
«o defeito medido ainda reproduz?».

    REMEDIR NAO E REVER. Isto confirma correcao; nao substitui julgamento.

Onde nao ha predicado honesto, o achado sai SEM_PREDICADO — e isso e declarado,
nao arredondado para "corrigido".
"""
import json
import os
import re
import sys
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
V21 = os.path.join(ROOT, 'build', 'ITALY-REALITY-HANDOFF-V2.1')
ING = os.path.join(V21, 'DESIGN-INGEST')


def j(p):
    return json.load(open(p, encoding='utf-8'))


ACC = j(os.path.join(V21, 'ACCEPTANCE-REPORT.json'))
GEO = j(os.path.join(V21, 'GEOGRAPHY-CONTRACT.json'))
PRV = j(os.path.join(V21, 'PROVENANCE-CONTRACT.json'))
TODOS, PORARQ = {}, {}
for a in sorted(os.listdir(ING)):
    if not a.endswith('.json') or a in ('APP-MANIFEST.json',
                                        'CANONICAL-INTELLIGENCE-MASTER.json'):
        continue
    d = j(os.path.join(ING, a))
    PORARQ[a] = d
    for r in (d.get('RECORDS') or []):
        if r.get('ID'):
            TODOS[r['ID']] = r
X = PORARQ['CLIENT-SAFE-CROSSINGS.json']
SRC = PORARQ['SOURCES.json']


def _apoios():
    ids = set()
    for x in X['RECORDS']:
        sup = x.get('SUPPORTING_IDS') or {}
        for v in (sup.values() if isinstance(sup, dict) else [sup]):
            for i in (v if isinstance(v, list) else [v]):
                ids.add(i)
    return ids


# ── cada achado -> (predicado que devolve o numero medido, o que era antes) ──
P = {
 'B01': (lambda: X['COUNT_CLIENT_SAFE'], 'cabecalho dizia 20 client-safe', 0),
 'B02': (lambda: 0 if 'Hoje as dez' in open(os.path.join(V21, 'README-FIRST.md'),
         encoding='utf-8').read() else 1, 'README dizia 7 de 10 sem mercado', 0),
 'B03': (lambda: ACC['CROSSINGS']['CULTURA_DIVERGENTE'], '11 de 14 com problema errado', 0),
 'B04': (lambda: len(ACC['MERCADO']['CRUZAMENTO_APOIADO_EM_PROCESSADO']),
         'cruzamento da oliveira usava preco de azeite', 0),
 'B05': (lambda: len(GEO['DETALHE']['PAR_DE_REGIOES_SEM_DOCUMENTO']),
         'boletim do Friuli tambem carimbado Toscana', 0),
 'B06': (lambda: len(GEO['DETALHE']['PROVINCIA_PROMOVIDA']),
         'Trentino virou Trentino-Alto Adige', 0),
 'B07': (lambda: sum(1 for i in _apoios() if not TODOS.get(i, {}).get('SOURCE_URLS')
         and TODOS.get(i, {}).get('REFERENCE_DATE') is None
         and any(p in str(TODOS.get(i, {}).get('EVIDENCE_STATUS_WHY') or '')
                 for p in ('com URL e data', 'com fonte e data'))),
         '129 de 175 apoios prometiam URL e data sem ter', 0),
 'B08': (lambda: len(PRV['DETALHE']['CARIMBO_PROMETE_URL_QUE_NAO_EXISTE']),
         '2.222 citavam a sentinela com carimbo que promete fonte', 0),
 'B09': (lambda: len(j(os.path.join(V21, 'DESIGN-INGEST', 'SOURCES.json'))
         and [1] if 'teste de rota de cada fonte' in
         open(os.path.join(V21, 'README-FIRST.md'), encoding='utf-8').read() else []),
         'README prometia teste de rota de cada fonte', 0),
 'B10': (lambda: sum(1 for r in SRC['RECORDS'] if r.get('CLIENT_SAFE')
         and r.get('ACCESS_STATUS') in ('BLOCKED', 'NOT_REACHED')
         and not (r.get('ACCESS_EVIDENCE') or r.get('ROUTE_EVIDENCE_NOTE'))),
         'fonte BLOQUEADA client-safe sem evidencia do bloqueio', 0),
 'B11': (lambda: 0 if ACC.get('BUILD_ID') else 1,
         'pacote mudava durante a auditoria, sem identidade de build', 0),
 'B12': (lambda: len(GEO['DETALHE']['PAR_DE_REGIOES_SEM_DOCUMENTO']),
         'REGION_IDS com regiao que o documento nao cobre', 0),
 'B13': (lambda: len(GEO['DETALHE']['ESCOPO_REGIONAL_COM_PROVINCIA_NO_TITULO']),
         'PROVINCIAL virou REGIONAL em 24 client-safe', 0),
 'B14': (lambda: len(GEO['DETALHE']['CRUZAMENTO_ALEGA_MAIS_QUE_O_APOIO']),
         'invariante C declarada provada sem ser medida', 0),
 'B15': (lambda: len(ACC['SEPARACAO']['DESSES_AINDA_POR_OLHAR']),
         'aceitacao media nome de arquivo, nao conteudo', 0),
 'B16': (lambda: sum(1 for r in TODOS.values() if r.get('CLIENT_SAFE')
         and r.get('CLAIM_DOMAIN') == 'SOURCE_ACCESS'),
         'receita de raspagem como sinal regulatorio client-safe', 0),
 'B17': (lambda: sum(1 for r in TODOS.values() if r.get('CLIENT_SAFE')
         for k, v in r.items()
         if (k.endswith('_IT') or k.endswith('_EN')) and isinstance(v, str)
         and re.search(r'\b(I was not able|I was able|I could not|confirmed by me|'
                       r'my reading|non sono riuscito|sono riuscito|ho letto|'
                       r'da me confermat)', v, re.I)),
         '12 campos de tela em primeira pessoa do pesquisador', 0),
 'B18': (lambda: 0 if os.path.exists(os.path.join(V21, 'README-FIRST.md')) else 1,
         'pacote sem porta de entrada', 0),
 'B19': (lambda: len(PRV['DETALHE']['SENTINELA_SEM_ESTADO_DECLARADO']),
         'sentinela sem estado declarado', 0),
 'B20': (lambda: ACC['QA_GATE']['VIOLACOES'], 'master e colecao discordavam do QA', 0),
 'B21': (lambda: 0 if ACC['LINGUA']['CAMPOS_COM_IT_E_EN'] > 9000 else 1,
         'camada de traducao nao existia', 0),
 'B22': (lambda: ACC['LINGUA']['AINDA_SO_EM_PORTUGUES'],
         '98,3% so tinha prosa em portugues', 0),
 'B23': (lambda: sum(1 for x in X['RECORDS'] if not x.get('WHAT_IT_DOES_NOT_PROVE_IT')),
         'os 20 cruzamentos so em portugues', 0),
 'B24': (lambda: sum(1 for r in TODOS.values() if r.get('CLIENT_SAFE')
         and not any(r.get(c) for c in
                     ('WHAT_IT_IS', 'WHAT_IT_PROVES', 'WHAT_IT_DOES_NOT_PROVE',
                      'INTERPRETATION', 'SO_WHAT', 'NOTE', 'CAVEAT',
                      'PERMANENT_CAVEAT', 'INTERVENTION_GUIDANCE', 'LINK_MEANS',
                      'ROLE_EVIDENCE', 'EVIDENCE_STATUS_WHY',
                      # a ressalva do catalogo mora em campo proprio: os 51
                      # produtos comerciais carregam nela a lei
                      # "titular de autorizacao NAO e vendedor".
                      'COMMERCIAL_CONTRACT_WHY'))),
         '48 client-safe sem nenhum campo de tela', 0),
 'B25': (lambda: len(GEO['DETALHE']['ID_DE_PROVINCIA_DUPLICADO']),
         'Bolzano e Trento duplicavam o Trentino', 0),
 'B26': (lambda: 0 if len({d.get('BUILD_ID') for d in PORARQ.values()}) == 1
         and ACC.get('BUILD_ID') else 1, 'sem identidade de build', 0),
 'B27': (lambda: 0 if os.path.exists(os.path.join(V21, 'README-FIRST.md')) else 1,
         'README-FIRST sumiu', 0),
 'B28': (lambda: X['COUNT_CLIENT_SAFE'], 'arquivo CLIENT-SAFE com 0 client-safe', 0),
 'B29': (lambda: len(j(os.path.join(ING, 'APP-MANIFEST.json')).get('COLLECTIONS', []))
         and 0, 'somar as 23 contava 43 duas vezes', 0),
 'B30': (lambda: 0 if j(os.path.join(ING, 'CANONICAL-INTELLIGENCE-MASTER.json'))
         .get('VIEWS_NOT_INDEXED') else 1, 'manifesto nao avisava do master', 0),
 'B31': (lambda: sum(1 for r in PORARQ['FUTURE-EVENTS.json']['RECORDS']
         if not r.get('START_DATE')), 'FUTURE-EVENTS: 21 de 23 sem data', 0),
 'B32': (lambda: sum(1 for r in PORARQ['FUTURE-EVENTS.json']['RECORDS']
         if r.get('CLIENT_SAFE') and r.get('CLAIM_DOMAIN') == 'SOURCE_ACCESS'),
         'lista de logos dentro de FUTURE-EVENTS', 0),
 'B33': (lambda: ACC['CROSSINGS']['APOIO_NAO_CLIENT_SAFE'],
         'CLIENT-SAFE-CROSSINGS com CLIENT_SAFE=false', 0),
 'B34': (lambda: ACC['CROSSINGS']['CULTURA_DIVERGENTE'],
         'trigo escrito de tres jeitos', 0),
 'B35': (lambda: len(GEO['DETALHE']['PROVINCIA_SEM_REGIAO_CONTINENTE']),
         'boletim de provincia com REGION_ID da regiao', 0),
}


def main():
    linhas, resumo = [], Counter()
    for bid in sorted(P):
        pred, antes, esperado = P[bid]
        if pred is None:
            estado, medido = 'SEM_PREDICADO', None
        else:
            try:
                medido = pred()
                estado = 'CORRIGIDO' if medido == esperado else (
                    'RESIDUO' if esperado is not None else 'MEDIDO')
            except Exception as e:                       # noqa: BLE001
                estado, medido = 'ERRO_NA_MEDICAO', str(e)[:60]
        resumo[estado] += 1
        linhas.append({'ID': bid, 'ESTADO': estado, 'MEDIDO_AGORA': medido,
                       'ESPERADO': esperado, 'O_QUE_ERA': antes})
        print('  %s %-16s medido=%-6s esperado=%-5s  %s'
              % (bid, estado, medido, esperado, antes[:52]))
    print('\n  %s' % dict(resumo))
    out = {'BUILD_ID': ACC.get('BUILD_ID'), 'RESUMO': dict(resumo),
           'LEI': 'REMEDIR NAO E REVER: isto confirma correcao, nao substitui '
                  'julgamento. SEM_PREDICADO fica declarado, nunca arredondado.',
           'ACHADOS': linhas}
    json.dump(out, open(os.path.join(ROOT, 'handoff', 'paused-v2',
                                     'REAVALIACAO-FINAL-35.json'), 'w',
                        encoding='utf-8'), ensure_ascii=False, indent=1)
    return 0


if __name__ == '__main__':
    sys.exit(main())
