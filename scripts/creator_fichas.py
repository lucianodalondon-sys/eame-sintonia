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


def _crop_proof():
    """Resultado da prova de cultura por CONTEÚDO, indexado por handle."""
    return {p['HANDLE'].lower(): p for p in cr.carregar('CROP-PROOF.json')}


def _fr_activity():
    return {c['CREATOR_ID']: c for c in cr.carregar('FR-ACTIVITY.json')}


def _colabs():
    return cr.carregar('BRAND-COLLABORATIONS-EU.json')


def montar():
    atividade = _atividade()
    colabs = _colabs()
    provas = _crop_proof()
    fr = _fr_activity()

    # Universo: identidades resolvidas + a base de candidatos aberta.
    universo = list(cr.carregar('PRIMARY-IDENTITY-RESOLVED.json'))
    ids = {r['CREATOR_ID'] for r in universo}
    for fonte in ('HUB-DISCOVERED-CLASSIFIED.json', 'CREATORS-ES-IT-FR.json'):
        for r in cr.carregar(fonte):
            if r['CREATOR_ID'] not in ids:
                universo.append(r); ids.add(r['CREATOR_ID'])

    # §9 — pecuária não contamina o mapa vegetal, e menção de hub não dá país.
    # Os dois grupos NÃO são descartados: saem para listas próprias, porque um
    # creator de pecuária é excelente no mapa que ainda não existe.
    pecuaria = [r for r in universo if r.get('LIVESTOCK_CREATOR') == 'YES']
    universo = [r for r in universo if r.get('LIVESTOCK_CREATOR') != 'YES']

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

        # ── §1-§2 · a prova por CONTEÚDO decide a cultura, acima da bio
        pv = provas.get(str(r.get('ORIGIN_ID', '')).lower())
        if pv:
            r['N_CONTENT_ITEMS_REVIEWED'] = pv['N_CONTENT_ITEMS_REVIEWED']
            r['CONTENT_TYPES_OBSERVED'] = pv['CONTENT_TYPES_OBSERVED']
            r['CROP_PROOF_TYPE'] = pv['CROP_PROOF_TYPE']
            r['CROP_PROOF_STRENGTH'] = pv['CROP_PROOF_STRENGTH']
            ev = (pv.get('EVIDENCE') or [{}])[0]
            r['CROP_PROOF_URL'] = ev.get('CROP_PROOF_URL', cr.NAO_SEI)
            r['CROP_PROOF_DATE'] = ev.get('CROP_PROOF_DATE', cr.NAO_SEI)
            r['CROP_PROOF_TEXT'] = ev.get('CROP_PROOF_TEXT', cr.NAO_SEI)
            if pv['CROP_PROOF_RESULT'] == 'PROVED':
                r['CROP_STATE'] = 'PROVED'
                r['CROPS'] = pv['CROPS_RECURRING']
                r['CROP_PROVED_BY_CONTENT'] = pv['CROPS_RECURRING']
                r['CROP_EVIDENCE'] = pv['REASON']
            elif pv['CROP_PROOF_RESULT'] == 'PARTIAL':
                r['CROP_STATE'] = 'PARTIAL'
                r['CROP_EVIDENCE'] = pv['REASON']
            else:
                r['CROP_STATE'] = pv['CROP_PROOF_RESULT']
                r['CROP_EVIDENCE'] = pv['REASON']
            r['CROP_TOPIC_ONLY'] = pv.get('CROP_TOPIC_ONLY') or []

        # ── §5 · atividade dos canais franceses
        f_ativ = fr.get(r.get('CREATOR_ID'))
        if f_ativ and f_ativ.get('ACTIVITY_STATE') != 'NOT_MEASURED':
            r['ACTIVITY_STATE'] = f_ativ['ACTIVITY_STATE']
            r['LAST_ACTIVITY_DATE'] = f_ativ['LAST_ACTIVITY_DATE']
            r['POSTS_LAST_30D'] = f_ativ['VIDEOS_LAST_30D']
            r['POSTS_LAST_90D'] = f_ativ['VIDEOS_LAST_90D']
            r['YOUTUBE'] = f_ativ.get('HANDLE', r.get('YOUTUBE'))

        fit, porque_fit = cr.fit_para_adama(r)
        r['AUDIENCE_FIT_FOR_ADAMA'] = fit
        estado, porques = cr.relevancia(r, colaboracoes=colabs)
        r['RELEVANCE_STATE'] = estado

        meus = [c for c in colabs if c.get('CREATOR_ID') == r['CREATOR_ID']]
        conc = [c for c in meus if c.get('BRAND') in cr.CONCORRENTES]

        # NAO reutilizar o nome `provas`: ele guarda o dicionario de prova de
        # CULTURA, carregado uma vez antes do laco. Rebinda-lo aqui fazia todos os
        # registros a partir do segundo perderem a prova de cultura — e o efeito
        # era invisivel, porque o resultado continuava plausivel.
        provas_ativacao = cr.provas_de_ativacao(r)
        faltando = [k for k in cr.PROVAS_DE_ATIVACAO if not provas_ativacao[k]]

        fichas.append({
            'COUNTRY': r.get('COUNTRY'), 'REGION': r.get('REGION', cr.NAO_SEI),
            'CROPS': r.get('CROPS', cr.NAO_SEI), 'CROP_STATE': r.get('CROP_STATE'),
            'CREATOR': r.get('NAME'), 'CREATOR_ID': r.get('CREATOR_ID'),
            'HANDLE': r.get('ORIGIN_ID', cr.NAO_SEI),
            'PROFILE_URL': r.get('PROFILE_URL', cr.NAO_SEI),
            'ENTITY_KIND': r.get('ENTITY_KIND'),
            'CREATOR_TYPE': r.get('CREATOR_TYPE'),
            'FACING': r.get('FACING', cr.NAO_SEI),
            'ACTIVATION_ENTITY_TYPE': r.get('ACTIVATION_ENTITY_TYPE', cr.NAO_SEI),
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
    # §13 · duas relações comerciais diferentes, duas listas diferentes.
    pessoas = [f for f in prontos if f.get('ACTIVATION_ENTITY_TYPE') == 'PERSON_CREATOR']
    negocios = [f for f in prontos if f.get('ACTIVATION_ENTITY_TYPE') in
                ('FARM_BUSINESS', 'FARMER_FAMILY_ACCOUNT')]
    outros = [f for f in prontos if f not in pessoas and f not in negocios]
    pendentes = Counter()
    for f in fichas:
        if f['ACTIVATION_STATE'] == 'PROMISING':
            for p in f['WHY_RELEVANT']:
                if str(p).startswith('PENDENTE:'):
                    for c in str(p).split(':', 1)[1].split(','):
                        pendentes[c.strip()] += 1
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
        # Lista plana além do mapa aninhado: o mapa serve à leitura humana, a
        # lista serve a quem consome o artefato em código. Sem ela, `carregar()`
        # não alcança nenhum registro deste arquivo.
        'FICHAS': fichas,
        'MAP': saida,
        'PROMISING_PENDING_REASONS': dict(pendentes),
        'LIVESTOCK_SEPARATE_MAP': [{'CREATOR': r.get('NAME'), 'HANDLE': r.get('ORIGIN_ID'),
                                    'COUNTRY': r.get('COUNTRY')} for r in pecuaria],
        'LIVESTOCK_NOTE': 'creators de pecuária saem do mapa de proteção de cultivo '
                          'VEGETAL e ficam listados aqui — não são descartados.',
        # §13 — a separação que a rodada 3 não fez e que gerou uma contagem errada
        'PERSON_CREATORS_ACTIVATION_READY': [
            {'COUNTRY': f['COUNTRY'], 'REGION': f['REGION'], 'CROPS': f['CROPS'],
             'CREATOR': f['CREATOR'], 'HANDLE': f['HANDLE']} for f in pessoas],
        'FARM_BUSINESS_PARTNERS_READY': [
            {'COUNTRY': f['COUNTRY'], 'REGION': f['REGION'], 'CROPS': f['CROPS'],
             'ACCOUNT': f['CREATOR'], 'HANDLE': f['HANDLE'],
             'ENTITY': f['ACTIVATION_ENTITY_TYPE']} for f in negocios],
        'OTHER_READY_ENTITIES': [
            {'ACCOUNT': f['CREATOR'], 'HANDLE': f['HANDLE'],
             'ENTITY': f['ACTIVATION_ENTITY_TYPE']} for f in outros],
        'SPLIT_LAW': 'ACCOUNT_OF_FARM_COMPANY != PERSON_CREATOR. Uma exploração com '
                     'canal forte é um parceiro comercial — outra relação, outro '
                     'contrato, outro interlocutor. Contá-la como creator-pessoa infla '
                     'o número que o Marketing usa para planear elenco.',
    }
    with open(os.path.join(cr.BASE, 'WHO-COULD-MARKETING-CALL.json'), 'w',
              encoding='utf-8') as f:
        json.dump(corpo, f, ensure_ascii=False, indent=2)
    print('gravado: data/samples/CREATOR-MAP-EAME/WHO-COULD-MARKETING-CALL.json')
    print('FICHAS=%d  POR_ESTADO=%s' % (len(fichas), corpo['BY_STATE']))
    print('PERSON_CREATORS_READY=%d  FARM_BUSINESS_READY=%d  OUTROS=%d'
          % (len(pessoas), len(negocios), len(outros)))
    print('ACTIVATION_READY:')
    for f in prontos:
        print('  %s · %s · %s → %s (%s)' % (f['COUNTRY'], f['REGION'],
                                            f['CROPS'], f['CREATOR'], f['HANDLE']))


if __name__ == '__main__':
    montar()
