#!/usr/bin/env python3
"""
WHO COULD MARKETING CALL? (§13) — a ficha operacional por COUNTRY × REGION × CROP.

    python3 scripts/creator_fichas.py

POR QUE FICHA E NÃO INVENTÁRIO
--------------------------------
Um inventário responde "quem existe". A ficha responde a pergunta que o
Marketing realmente faz: *"para esta cultura, neste país, quem eu posso ligar — e
o que eu ainda não sei sobre essa pessoa?"*

Por isso cada ficha carrega as SEIS provas uma a uma, e não só o veredito. Um
`PROMISING` que diz `RECENT_ACTIVITY_PROVED=FALTA` é acionável: alguém sabe o que
buscar. Um `PROMISING` sozinho manda a pessoa de volta para a fila.

A ORDENAÇÃO — e o que ela deliberadamente NÃO é
-------------------------------------------------
Dentro de cada recorte, a ordem é por ESTADO (`ACTIVATION_READY` antes de
`PROMISING`) e, dentro do estado, alfabética. **Não** por seguidores. Esta missão
já mediu o que a ordenação por seguidores faria: os cinco maiores perfis da seed
italiana somam ~452 mil seguidores e quatro são mídia de vinho. O primeiro lugar
seria de quem não fala com produtor.

`FOLLOWERS` aparece na ficha como **descrição**, nunca como chave de ordem.
"""
import json
import os
import sys
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import creators as cr                                        # noqa: E402

MISSION = '14-MAPA-DE-CREATORS-EAME'
CAPTURA = '2026-08-30'
ORDEM = {'ACTIVATION_READY': 0, 'PROMISING': 1, 'RESEARCH_NEEDED': 2, 'NOT_RELEVANT': 3}


def _atividade():
    fora = {}
    for p in cr.carregar('CREATOR-ACTIVITY.json'):
        fora[(p.get('HANDLE') or '').lower()] = p
    return fora


def _colabs():
    return cr.carregar('BRAND-COLLABORATIONS-EU.json')


def montar():
    atividade = _atividade()
    colabs = _colabs()

    # Universo: identidades resolvidas + a base de candidatos aberta.
    universo = list(cr.carregar('PRIMARY-IDENTITY-RESOLVED.json'))
    ids = {r['CREATOR_ID'] for r in universo}
    for r in cr.carregar('CREATORS-ES-IT-FR.json'):
        if r['CREATOR_ID'] not in ids:
            universo.append(r)

    fichas = []
    for r in universo:
        r = dict(r)
        # ── casar atividade medida com o registro, pelo handle resolvido
        chave = None
        for campo in ('INSTAGRAM', 'ORIGIN_ID', 'X', 'YOUTUBE'):
            v = r.get(campo)
            if v and v != cr.NAO_SEI and v.lower() in atividade:
                chave = v.lower(); break
        if chave:
            a = atividade[chave]
            r['ACTIVITY_STATE'] = a['ACTIVITY_STATE']
            r['LAST_ACTIVITY_DATE'] = a['LAST_ACTIVITY_DATE']
            r['POSTS_LAST_30D'] = a['POSTS_LAST_30D']
            r['POSTS_LAST_90D'] = a['POSTS_LAST_90D']
            r['ACTIVITY_RECENCY'] = a['ACTIVITY_STATE']

        fit, porque_fit = cr.fit_para_adama(r)
        r['AUDIENCE_FIT_FOR_ADAMA'] = fit
        estado, porques = cr.relevancia(r, colaboracoes=colabs)
        r['RELEVANCE_STATE'] = estado

        meus = [c for c in colabs if c.get('CREATOR_ID') == r['CREATOR_ID']]
        conc = [c for c in meus if c.get('BRAND') in cr.CONCORRENTES]

        provas = cr.provas_de_ativacao(r)
        faltando = [k for k in cr.PROVAS_DE_ATIVACAO if not provas[k]]

        fichas.append({
            'COUNTRY': r.get('COUNTRY'), 'REGION': r.get('REGION', cr.NAO_SEI),
            'CROPS': r.get('CROPS', cr.NAO_SEI), 'CROP_STATE': r.get('CROP_STATE'),
            'CREATOR': r.get('NAME'), 'CREATOR_ID': r.get('CREATOR_ID'),
            'HANDLE': r.get('ORIGIN_ID', cr.NAO_SEI),
            'PROFILE_URL': r.get('PROFILE_URL', cr.NAO_SEI),
            'ENTITY_KIND': r.get('ENTITY_KIND'),
            'CREATOR_TYPE': r.get('CREATOR_TYPE'),
            'ACTUAL_FARMER': r.get('ACTUAL_FARMER'),
            'ACTUAL_FARMER_EVIDENCE': r.get('ACTUAL_FARMER_EVIDENCE'),
            'WHY_RELEVANT': porques,
            'AUDIENCE_FIT_FOR_ADAMA': fit, 'AUDIENCE_FIT_REASON': porque_fit,
            'FOLLOWERS': r.get('FOLLOWERS_BY_PLATFORM', cr.NAO_SEI),
            'FOLLOWERS_NOTE': 'descritivo — NUNCA chave de ordenação',
            'RECENT_ACTIVITY': {
                'STATE': r.get('ACTIVITY_STATE'),
                'LAST_ACTIVITY_DATE': r.get('LAST_ACTIVITY_DATE', cr.NAO_SEI),
                'POSTS_LAST_30D': r.get('POSTS_LAST_30D', cr.NAO_SEI),
                'POSTS_LAST_90D': r.get('POSTS_LAST_90D', cr.NAO_SEI)},
            'BRAND_HISTORY': [{'BRAND': c.get('BRAND'), 'TYPE': c.get('RELATION_TYPE'),
                               'DATE': c.get('DATE')} for c in meus] or 'NOT_OBSERVED',
            'COMPETITOR_HISTORY': [c.get('BRAND') for c in conc] or 'NOT_OBSERVED',
            'ADAMA_HISTORY': r.get('ADAMA_COLLABORATION_OBSERVED'),
            'PUBLIC_CONTACT': r.get('PUBLIC_CONTACT_ROUTE', cr.NAO_SEI),
            'CONTACT_KIND': r.get('CONTACT_KIND', cr.NAO_SEI),
            'ACTIVATION_STATE': estado,
            'MISSING_PROOFS': faltando or 'NENHUMA',
            'EVIDENCE': r.get('CROP_PROOF_URLS') or [r.get('SOURCE_URL')],
            'CAVEAT': r.get('SEED_ERROR_CLASS', cr.NAO_SEI),
        })

    # ── COUNTRY → REGION → CROP
    mapa = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))
    for f in fichas:
        crops = f['CROPS'] if isinstance(f['CROPS'], list) else [f['CROPS']]
        for c in (crops or [cr.NAO_SEI]):
            mapa[f['COUNTRY']][f['REGION']][c].append(f)

    saida = {}
    for pais in sorted(mapa):
        saida[pais] = {}
        for regiao in sorted(mapa[pais], key=str):
            saida[pais][regiao] = {}
            for cultura in sorted(mapa[pais][regiao], key=str):
                lista = sorted(mapa[pais][regiao][cultura],
                               key=lambda x: (ORDEM.get(x['ACTIVATION_STATE'], 9),
                                              str(x['CREATOR'])))
                saida[pais][regiao][cultura] = lista

    prontos = [f for f in fichas if f['ACTIVATION_STATE'] == 'ACTIVATION_READY']
    corpo = {
        'SOURCE_ID': MISSION, 'CAPTURED_AT': CAPTURA,
        'QUESTION': 'Se o Marketing quiser agir para esta cultura neste país/região, '
                    'quem já tem relevância real junto àquele público?',
        'ORDERING_LAW': 'ordenado por ESTADO e depois alfabeticamente. NUNCA por '
                        'seguidores — medido nesta missão: os 5 maiores perfis da seed '
                        'italiana somam ~452 mil seguidores e 4 são mídia de vinho.',
        'TOTAL': len(fichas),
        'BY_STATE': dict(Counter(f['ACTIVATION_STATE'] for f in fichas)),
        'BY_COUNTRY': dict(Counter(f['COUNTRY'] for f in fichas)),
        'ACTIVATION_READY': [{'COUNTRY': f['COUNTRY'], 'REGION': f['REGION'],
                              'CROPS': f['CROPS'], 'CREATOR': f['CREATOR'],
                              'HANDLE': f['HANDLE']} for f in prontos],
        'MAP': saida,
    }
    with open(os.path.join(cr.BASE, 'WHO-COULD-MARKETING-CALL.json'), 'w',
              encoding='utf-8') as f:
        json.dump(corpo, f, ensure_ascii=False, indent=2)
    print('gravado: data/samples/CREATOR-MAP-EAME/WHO-COULD-MARKETING-CALL.json')
    print('FICHAS=%d  POR_ESTADO=%s' % (len(fichas), corpo['BY_STATE']))
    print('ACTIVATION_READY:')
    for f in prontos:
        print('  %s · %s · %s → %s (%s)' % (f['COUNTRY'], f['REGION'],
                                            f['CROPS'], f['CREATOR'], f['HANDLE']))


if __name__ == '__main__':
    montar()
