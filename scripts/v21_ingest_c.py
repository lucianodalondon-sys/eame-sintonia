#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PARTE C DO INGEST — a camada de SUBSTÂNCIA ATIVA que o V2.1 não tinha.

    python3 scripts/v21_ingest_c.py     (roda depois de v21_ingest_b.py)

O QUE ENTRA, E POR QUE SÓ ISSO
-------------------------------
O pacote `research/adama-italy-product-intelligence-deep/` foi aceito para
ingestão PARCIAL: camadas regulatória e de MoA, sim; camada de uso de rótulo,
não. Este passo respeita a fronteira.

Até aqui a substância ativa era um CAMPO de texto dentro do produto. Não dava
para perguntar «quais produtos partilham modo de ação» sem varrer strings. Ela
passa a ser ENTIDADE, com relação própria para produto e para o estado europeu.

⚠️ A MISTURA NUNCA VIRA UM MoA SÓ
----------------------------------
Cada componente é uma entidade e uma relação. Um produto com dois ativos gera
DUAS relações, nunca uma com o nome colado. O pacote de origem chegou a colar —
dividia por `+` quando o registro italiano divide por `|` — e foi corrigido lá
antes de chegar aqui. O V2.1 nunca teve esse defeito: `PRODUCTS-REGULATORY`
já guardava lista de verdade. Nada a desfazer aqui, e isso foi CONFERIDO, não
suposto.

⚠️ O QUE O ATO EUROPEU PROVA, E O QUE NÃO PROVA
------------------------------------------------
A EU Pesticides Database continua fechada. O estado europeu vem do Anexo do
Regulamento 540/2011 consolidado, que prova APPROVED e a data de expiração da
aprovação. Não prova renovação em curso, projeto de não-renovação nem revisão
do artigo 21 — esses ficam UNKNOWN.

    EXPIRAÇÃO DE APROVAÇÃO NÃO É RISCO.
    NÃO É RETIRADA. NÃO É OPORTUNIDADE.
    E ESTADO EUROPEU NÃO É COMERCIALIZAÇÃO NA ITÁLIA.

Por isso a coleção de futuro que sai daqui chama-se FACT, não SIGNAL, e cada
registro carrega `NOT_A_CLAIM` dizendo o que ele não autoriza a concluir.
"""
import json
import os
import re
import sys
from collections import Counter, defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from v21_ingest import ING, base, le, sid  # noqa: E402

MAP = {}


def grava(nome, colecao, itens, chave, verdade, lei=None, extra=None):
    """Mesmo envelope de coleção das partes A e B, e o mesmo lugar de gravação.

    Não importa o MAP da parte B: aquele dicionário só existe enquanto o processo
    dela roda. Este passo lê do disco o que ela escreveu, que é o que o pacote de
    fato tem — e é o que a aceitação vai reler depois."""
    cs = sum(1 for x in itens if x.get('CLIENT_SAFE'))
    corpo = {
        'COLLECTION': colecao, 'FILE': nome, 'SCHEMA_VERSION': 'V2.1',
        'BUILT_AT': DATA, 'PRIMARY_KEY': chave, 'SOURCE_OF_TRUTH': verdade,
        'COUNT_TOTAL': len(itens), 'COUNT_CLIENT_SAFE': cs,
        'BY_ORIGIN': dict(Counter(x.get('ORIGIN_LAYER') for x in itens)),
        'BY_QA': dict(Counter(x.get('QA_STATUS') for x in itens)),
    }
    if lei:
        corpo['LAW'] = lei
    if extra:
        corpo.update(extra)
    corpo['RECORDS'] = itens
    json.dump(corpo, open(os.path.join(ING, nome), 'w', encoding='utf-8'),
              ensure_ascii=False, indent=1)
    MAP[colecao] = corpo
    # o índice de coleções que a parte B deixou tem de crescer junto, senão o
    # fechamento não enxerga estas três e o pacote sai menor do que é
    idx = os.path.join(ING, '_COLECOES.json')
    if os.path.exists(idx):
        with open(idx, encoding='utf-8') as fh:
            atual = json.load(fh)
        atual[colecao] = {k: v for k, v in corpo.items() if k != 'RECORDS'}
        json.dump(atual, open(idx, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    return corpo


def colecao(nome):
    with open(os.path.join(ING, nome), encoding='utf-8') as fh:
        return json.load(fh)['RECORDS']

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PKG = os.path.join(ROOT, 'research', 'adama-italy-product-intelligence-deep')

DATA = '2026-09-02'


def pkg(nome, chave=None):
    with open(os.path.join(PKG, nome), encoding='utf-8') as fh:
        d = json.load(fh)
    return d[chave] if chave else d


def ai_id(nome):
    return 'AI_' + re.sub(r'[^A-Z0-9]+', '_', nome.upper()).strip('_')


def main():
    ais = pkg('ACTIVE-INGREDIENTS.json', 'ACTIVE_INGREDIENTS')
    frac = {f['ACTIVE_INGREDIENT']: f for f in pkg('FRAC-CLASSIFICATIONS.json', 'ROWS')}
    eu = {e['ACTIVE_INGREDIENT']: e for e in pkg('EU-ACTIVE-SUBSTANCE-STATUS.json', 'ROWS')}
    eu_meta = pkg('EU-ACTIVE-SUBSTANCE-STATUS.json')
    fut = pkg('REGULATORY-FUTURE-DEEP.json', 'RELATIONSHIPS')
    qa = pkg('QA-REPORT.json')

    # Os produtos já ingeridos são a única âncora de identidade. Substância que
    # não encosta em produto nenhum não entra: relação órfã é dívida, não dado.
    reg = {r['REGISTRATION_NUMBER']: r for r in colecao('PRODUCTS-REGULATORY.json')
           if r.get('REGISTRATION_NUMBER')}
    com = colecao('PRODUCTS-COMMERCIAL.json')
    com_por_reg = defaultdict(list)
    for c in com:
        if c.get('MATCHED_REGULATORY_ID'):
            com_por_reg[c['MATCHED_REGULATORY_ID']].append(c)

    # ══ SUBSTÂNCIAS ATIVAS ═══════════════════════════════════════════════════
    subs, orfas = [], []
    for a in ais:
        regs = [r for r in a['REGISTRATION_NUMBERS'] if r in reg]
        if not regs:
            orfas.append(a['NAME'])
            continue
        f = frac.get(a['NAME'], {})
        e = eu.get(a['NAME'], {})
        urls = [u for u in ([f.get('SOURCE_URL')] + (a.get('SOURCE_URL') or [])
                            + [e.get('SOURCE_URL')]) if u]
        subs.append(base(
            ai_id(a['NAME']), 'ACTIVE_INGREDIENT', 'EVIDENCE_SOURCED', 'QA_PASS',
            urls, DATA, [], [], ['GEO_ITALY'], 'NACIONAL',
            extra={
                'NAME': a['NAME'],
                'NORMALIZED_NAME': a['NORMALIZED_NAME'],
                'ITALIAN_REGISTRATION_COUNT': len(regs),
                'HRAC': a.get('HRAC'), 'HRAC_WSSA': a.get('HRAC_WSSA'),
                'CHEMICAL_FAMILY': a.get('CHEMICAL_FAMILY'),
                'IRAC': a.get('IRAC'), 'IRAC_SUBGROUP': a.get('IRAC_SUBGROUP'),
                'FRAC': f.get('FRAC_CODE'),
                'FRAC_SOURCE_VERSION': f.get('SOURCE_VERSION'),
                'FRAC_DOCUMENT_SHA256': f.get('DOCUMENT_SHA256'),
                'MOA_STATE': ('CLASSIFIED' if (a.get('HRAC') or a.get('IRAC')
                                               or f.get('FRAC_CODE')) else 'UNKNOWN'),
                'EU_STATE': e.get('EU_STATE', 'UNKNOWN'),
                'EU_DATE_OF_APPROVAL': e.get('DATE_OF_APPROVAL'),
                'EU_EXPIRATION_OF_APPROVAL': e.get('EXPIRATION_OF_APPROVAL'),
                'EU_CELEX': e.get('LATEST_RELEVANT_COMMISSION_ACT'),
                'EU_RENEWAL_STATE': 'UNKNOWN',
                'CAS': e.get('CAS'), 'CIPAC': e.get('CIPAC'),
                'WHAT_IT_DOES_NOT_PROVE': (
                    'estado europeu nao e comercializacao na Italia; expiracao de '
                    'aprovacao nao e retirada, risco nem oportunidade; classificacao '
                    'de modo de acao nao e resistencia presente em campo'),
            }))

    grava('ACTIVE-INGREDIENTS.json', 'ACTIVE_INGREDIENTS', subs, 'ID',
          'registro do Ministero (composicao) + HRAC + IRAC + FRAC Code List 2026 '
          '+ Anexo do Reg. (UE) 540/2011 consolidado em ' + eu_meta['CONSOLIDATION_DATE'],
          lei='SUBSTANCIA ATIVA e ENTIDADE, nao campo de texto do produto. Cada '
              'componente de mistura e uma entidade propria: mistura NUNCA vira um '
              'MoA so. FRAC ausente significa que a substancia nao tem linha na '
              'tabela FRAC — e o caso de todo herbicida e inseticida —, nunca que o '
              'codigo foi perdido na leitura.',
          extra={'MOA_SOURCES': {
                     'HRAC': 'https://www.hracglobal.com/tools/classification-lookup',
                     'IRAC': 'https://irac-online.org/mode-of-action/classification-online/',
                     'FRAC': pkg('FRAC-CLASSIFICATIONS.json')['SOURCE_URL']},
                 'EU_SOURCE': eu_meta['SOURCE_URL'], 'EU_CELEX': eu_meta['CELEX'],
                 'DROPPED_AS_ORPHAN': len(orfas),
                 'DROPPED_WHY': 'substancia sem nenhum produto regulatorio ingerido nesta versao'})

    # ══ PRODUTO × SUBSTÂNCIA ATIVA ═══════════════════════════════════════════
    pares = []
    for a in ais:
        for r in a['REGISTRATION_NUMBERS']:
            p = reg.get(r)
            if not p:
                continue
            pares.append(base(
                'PAI_%s_%s' % (r, ai_id(a['NAME'])[3:]),
                'PRODUCT_ACTIVE_INGREDIENT', 'EVIDENCE_DOCUMENTED', 'QA_PASS',
                [], DATA, [], [], ['GEO_ITALY'], 'NACIONAL',
                extra={
                    'PRODUCT_ID': p['ID'], 'PRODUCT_NAME': p.get('NAME'),
                    'REGISTRATION_NUMBER': r,
                    'ACTIVE_INGREDIENT_ID': ai_id(a['NAME']),
                    'ACTIVE_INGREDIENT': a['NAME'],
                    'IS_MIXTURE_COMPONENT': len(p.get('ACTIVE_INGREDIENTS') or []) > 1,
                    'COMPONENTS_IN_PRODUCT': len(p.get('ACTIVE_INGREDIENTS') or []) or 1,
                    'COMMERCIAL_CATALOG_PRODUCTS': [c.get('NAME') for c in com_por_reg.get(r, [])],
                    'WHAT_IT_DOES_NOT_PROVE':
                        'a relacao diz o que o produto CONTEM, nunca em que cultura ou '
                        'contra que alvo ele e autorizado — isso e do rotulo',
                }))
    grava('PRODUCT-ACTIVE-INGREDIENTS.json', 'PRODUCT_ACTIVE_INGREDIENTS', pares, 'ID',
          'campo sostanze_attive do registro do Ministero, um componente por relacao',
          lei='UMA RELACAO POR COMPONENTE. Produto com dois ativos gera duas linhas. '
              'Somar linhas nao conta produtos.')

    # ══ FUTURO REGULATÓRIO — FATO, NÃO SINAL ═════════════════════════════════
    fatos = []
    for r in fut:
        regs = [x for x in r['ITALIAN_REGISTRATIONS'] if x in reg]
        if not regs:
            continue
        fatos.append(base(
            'RFF_' + ai_id(r['ACTIVE_INGREDIENT'])[3:], 'REGULATORY_FUTURE_FACT',
            'EVIDENCE_DOCUMENTED', 'QA_PASS', [eu_meta['SOURCE_URL']],
            r['EU_EXPIRATION_OF_APPROVAL'], [], [], ['GEO_EU', 'GEO_ITALY'], 'REGIONAL',
            extra={
                'ACTIVE_INGREDIENT': r['ACTIVE_INGREDIENT'],
                'ACTIVE_INGREDIENT_ID': ai_id(r['ACTIVE_INGREDIENT']),
                'EU_STATE': r['EU_STATE'],
                'EU_EXPIRATION_OF_APPROVAL': r['EU_EXPIRATION_OF_APPROVAL'],
                'EU_CELEX': eu_meta['CELEX'],
                'ITALIAN_REGISTRATIONS': regs,
                'ITALIAN_REGISTRATION_COUNT': len(regs),
                'COMMERCIAL_CATALOG_PRODUCTS': r['COMMERCIAL_CATALOG_PRODUCTS'],
                'VERIFIED_LABEL_CROPS': [],
                'VERIFIED_LABEL_CROPS_STATE': 'LABEL_CHECK_NEEDED',
                'IS_OPPORTUNITY': False,
                'IS_RISK': False,
                'NOT_A_CLAIM': (
                    'data factual de expiracao de aprovacao europeia. NAO e risco '
                    'regulatorio, NAO e risco comercial, NAO e oportunidade e NAO e '
                    'nao-renovacao. Interpretar exige evidencia que este ato nao traz.'),
            }))
    fatos.sort(key=lambda x: x['EU_EXPIRATION_OF_APPROVAL'] or '9999')
    grava('REGULATORY-FUTURE-FACTS.json', 'REGULATORY_FUTURE_FACTS', fatos, 'ID',
          'Anexo do Reg. (UE) 540/2011 consolidado em ' + eu_meta['CONSOLIDATION_DATE'],
          lei='FATO DE DATA, NAO LEITURA. Nenhum registro aqui vira card de '
              'oportunidade sozinho: quem interpreta e o V2.1, com evidencia a mais.',
          extra={'QA_PACKAGE_ERROR_RATE': qa['MEASURED_ERROR_RATE'],
                 'QA_SAMPLE_SIZE': qa['QA_SAMPLE_SIZE'],
                 'STATES_NOT_OBTAINABLE': eu_meta['STATES_NOT_OBTAINABLE_FROM_THIS_SOURCE'],
                 'WHY_NOT_OBTAINABLE': 'EU Pesticides Database: 307 -> sorry.ec.europa.eu'})

    print('%-30s %7s %7s' % ('COLECAO (parte C)', 'TOTAL', 'SAFE'))
    for k in ('ACTIVE_INGREDIENTS', 'PRODUCT_ACTIVE_INGREDIENTS', 'REGULATORY_FUTURE_FACTS'):
        print('%-30s %7d %7d' % (k, MAP[k]['COUNT_TOTAL'], MAP[k]['COUNT_CLIENT_SAFE']))
    if orfas:
        print('substancias sem produto ingerido, deixadas de fora: %d' % len(orfas))


if __name__ == '__main__':
    main()
