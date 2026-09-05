#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CAMADA EU ACTIVE SUBSTANCE × PORTFÓLIO ADAMA ITÁLIA — a camada que faltava.

    bash scripts/cellar.sh substances 2024 > .tmp/eu-2024.json   (e 2025, 2026)
    python3 scripts/eu_substancia_adama_it.py

POR QUE ISTO EXISTE
--------------------
Todo o regulatório italiano do acervo é de REGISTRO NACIONAL DO PRODUTO: `EXPIRY` de
2027, 2034, 2040. Mas nenhum registro nacional sobrevive à APROVAÇÃO EUROPEIA da
substância ativa que ele contém. São duas camadas, e o acervo só tinha uma.

    REGISTRO NACIONAL DO PRODUTO   vence, e o vencimento é rotina de re-registro
    APROVAÇÃO EU DA SUBSTÂNCIA     se cai, o produto cai junto, em toda a UE

⛔ E a ordem entre elas NÃO é simétrica: a UE decide sobre a substância, e o Estado-membro
decide sobre o produto DENTRO do que a UE aprovou.

O QUE ESTE ARQUIVO FAZ, E O QUE ELE NÃO FAZ
--------------------------------------------
Casa o TÍTULO dos atos da UE (rota CELLAR/SPARQL, já provada em EU-T4-001) contra a lista
de substâncias ativas que o registro italiano da ADAMA declara. É um casamento LEXICAL
sobre título — não é leitura do ato.

    ⛔ TÍTULO CASADO NÃO É ATO LIDO.

Um ato chamado «...renewal of approval of X...» diz que existe um ato sobre X. Ele NÃO diz
o resultado, NÃO diz a data de fim, e NÃO diz se atinge o uso italiano. Cada linha sai com
`ACT_READ: false` até alguém abrir o CELEX.
"""
import glob
import json
import os
import re
import sys
import unicodedata
from collections import defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SAIDA = os.path.join(ROOT, 'data', 'samples', 'IT-REGUA')


def _n(t):
    return ''.join(c for c in unicodedata.normalize('NFD', t or '')
                   if unicodedata.category(c) != 'Mn').lower()


def substancias_adama_it():
    """Da fonte primária: os 163 registros vigentes do Ministero."""
    alvo = None
    for b in os.popen('git branch -r').read().split():
        if 'HEAD' in b or '->' in b:
            continue
        p = 'data/samples/IT-T4-001/ITALY-ADAMA-REGULATORY-INTELLIGENCE.json'
        if os.system('git cat-file -e %s:%s 2>nul' % (b, p)) == 0:
            alvo = os.popen('git show %s:%s' % (b, p)).read()
            break
    if not alvo:
        print('NAO_ACHEI_O_REGULATORIO'); return {}
    d = json.loads(alvo)
    fora = defaultdict(list)
    for p in d['PRODUCTS']:
        for s in (p.get('ACTIVE_INGREDIENTS') or []):
            fora[s].append(p['PRODUCT'])
    return fora


# ⚠️ Sinônimos que o título da UE usa e o rótulo italiano não. Sem isto, `2,4-D` e
# `CLOQUINTOCET MEXYL` nunca casariam — e a ausência pareceria «sem ato».
SINONIMOS = {
    '2,4-D': ['2,4-d'],
    'CLOQUINTOCET MEXYL': ['cloquintocet-mexyl', 'cloquintocet'],
    'QUIZALOFOP-P-ETHYL': ['quizalofop-p-ethyl', 'quizalofop-p'],
    'MEFENPYR DIETHYL': ['mefenpyr-diethyl', 'mefenpyr'],
    'ISOXADIFEN ETHYL': ['isoxadifen-ethyl', 'isoxadifen'],
    'CHLOROTOLURON': ['chlorotoluron', 'chlortoluron'],
    'PARAFFIN OIL/(CAS 97862-82-3)': ['paraffin oil'],
    'MESOSULFURON-METHYL': ['mesosulfuron-methyl', 'mesosulfuron'],
    'TRIBENURON': ['tribenuron-methyl', 'tribenuron'],
    'CLODINAFOP': ['clodinafop-propargyl', 'clodinafop'],
}


def main():
    subs = substancias_adama_it()
    if not subs:
        return 1
    print('substancias ativas no registro ADAMA IT: %d' % len(subs))

    atos = []
    for f in sorted(glob.glob(os.path.join(ROOT, '.tmp', 'eu-*.json'))):
        d = json.load(open(f, encoding='utf-8'))
        for b in d.get('results', {}).get('bindings', []):
            atos.append({
                'CELEX': b.get('celex', {}).get('value'),
                'DATE': (b.get('date', {}).get('value') or '')[:10],
                'TITLE': b.get('title', {}).get('value') or '',
            })
    vistos, unicos = set(), []
    for a in atos:
        if a['CELEX'] in vistos:
            continue
        vistos.add(a['CELEX'])
        unicos.add if False else unicos.append(a)
    print('atos UE «active substance» 2024-2026 lidos: %d (unicos %d)'
          % (len(atos), len(unicos)))

    casados = defaultdict(list)
    for s, produtos in subs.items():
        termos = SINONIMOS.get(s, [_n(s)])
        for a in unicos:
            t = _n(a['TITLE'])
            if any(re.search(r'\b%s' % re.escape(x), t) for x in termos):
                casados[s].append(a)

    linhas = []
    for s, produtos in sorted(subs.items(), key=lambda kv: -len(kv[1])):
        ats = sorted(casados.get(s, []), key=lambda a: a['DATE'], reverse=True)
        linhas.append({
            'ACTIVE_SUBSTANCE': s,
            'ADAMA_IT_PRODUCTS': len(produtos),
            'ADAMA_IT_PRODUCT_NAMES': sorted(set(produtos))[:14],
            'EU_ACTS_MATCHED': len(ats),
            'EU_ACTS': [dict(a, ACT_READ=False,
                             ACT_OUTCOME='NÃO SEI — só o título foi casado') for a in ats[:6]],
            'STATE': ('ACT_FOUND_NOT_READ' if ats else 'NO_ACT_IN_THIS_WINDOW'),
            'STATE_MEANING': ('existe ato da UE 2024-2026 cujo TÍTULO nomeia esta substância'
                              if ats else
                              'nenhum ato 2024-2026 com esta substância no título. '
                              'NÃO significa aprovação estável — significa que a janela '
                              'lida não tem ato.'),
        })

    corpo = {
        'DATASET': 'IT-ADAMA-EU-ACTIVE-SUBSTANCE-V1',
        'COUNTRY': 'IT',
        'SOURCE_ID': 'EU-T4-001-B',
        'source': 'EU Publications Office / CELLAR — endpoint SPARQL público, sem chave',
        'endpoint': 'https://publications.europa.eu/webapi/rdf/sparql',
        'reproduce': 'bash scripts/cellar.sh substances <ano>',
        'SOURCE_LOCATION': 'EUROPEAN UNION',
        'FACT_LOCATION': 'EUROPEAN UNION',
        'ORIGINAL_LANGUAGE': 'EN',
        'REGULATORY_LAYER': 'EU ACTIVE SUBSTANCE',
        'EVIDENCE_CLASS': 'REGULATORY_FACT',
        'CAPTURED_AT': '2026-09-02',
        'APIFY_RUNS': 0, 'COST_USD': 0,
        'JANELA': '2024-01-01 a 2026-12-31, atos 3YYYYR* com "active substance" no título',
        'POR_QUE_ISTO_IMPORTA': (
            'todo o regulatório italiano do acervo é de REGISTRO NACIONAL DO PRODUTO. '
            'Nenhum registro nacional sobrevive à APROVAÇÃO EUROPEIA da substância. '
            'São duas camadas, e o acervo só tinha uma.'),
        'CONTRATO_DE_LEITURA': {
            'MATCH_E_LEXICAL': 'o casamento é sobre o TÍTULO do ato, não sobre o texto',
            'TITULO_CASADO_NAO_E_ATO_LIDO': (
                'o título diz que EXISTE ato sobre a substância. Não diz o resultado, '
                'não diz a data de fim da aprovação, e não diz se atinge o uso italiano.'),
            'NO_ACT_NAO_E_APROVACAO_ESTAVEL': (
                'ausência de ato na janela lida NÃO é prova de aprovação estável. '
                'A aprovação pode ter sido decidida antes de 2024.'),
            'LIMITE_DA_CONSULTA': (
                'a consulta traz LIMIT 200 por ano e só atos com "active substance" no '
                'título em inglês. Ato que use outra formulação de título fica de fora.'),
        },
        'SUBSTANCIAS_TOTAL': len(subs),
        'SUBSTANCIAS_COM_ATO': sum(1 for l in linhas if l['EU_ACTS_MATCHED']),
        'SUBSTANCIAS_SEM_ATO_NA_JANELA': sum(1 for l in linhas if not l['EU_ACTS_MATCHED']),
        'ATOS_UE_LIDOS': len(unicos),
        'AFIRMACOES_PROIBIDAS': [
            'a substância vai ser proibida',
            'o produto vai sair do mercado',
            'a aprovação foi renovada',
            'não há risco regulatório nesta substância',
        ],
        'SUBSTANCIAS': linhas,
    }
    os.makedirs(SAIDA, exist_ok=True)
    cam = os.path.join(SAIDA, 'IT-ADAMA-EU-ACTIVE-SUBSTANCE-V1.json')
    with open(cam, 'w', encoding='utf-8') as f:
        json.dump(corpo, f, ensure_ascii=False, indent=1)

    print('\n%-30s %5s %5s  %s' % ('SUBSTANCIA', 'PROD', 'ATOS', 'ATO MAIS RECENTE'))
    for l in linhas:
        if l['EU_ACTS_MATCHED']:
            a = l['EU_ACTS'][0]
            print('%-30s %5d %5d  %s %s' % (l['ACTIVE_SUBSTANCE'][:30],
                                            l['ADAMA_IT_PRODUCTS'], l['EU_ACTS_MATCHED'],
                                            a['DATE'], a['TITLE'][:74]))
    print('\nsem ato na janela: %s' % ', '.join(
        l['ACTIVE_SUBSTANCE'] for l in linhas if not l['EU_ACTS_MATCHED'])[:400])
    print('\ngravado: data/samples/IT-REGUA/IT-ADAMA-EU-ACTIVE-SUBSTANCE-V1.json')
    return 0


if __name__ == '__main__':
    sys.exit(main())
