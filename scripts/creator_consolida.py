#!/usr/bin/env python3
"""
CONSOLIDAÇÃO — junta ALEGAÇÃO (seed), MEDIÇÃO ABERTA (web) e MEDIÇÃO PAGA (Apify)
sem deixar nenhuma das três se disfarçar de outra.

    python3 scripts/creator_consolida.py

O QUE A RODADA APIFY MOSTROU, E QUE NENHUMA LEITURA DE LISTA MOSTRARIA
-----------------------------------------------------------------------
25 handles resolvidos por US$ 0,0624. O resultado inverte a leitura otimista
da seed:

  · os CINCO maiores perfis da seed somam ~452 mil seguidores, e QUATRO deles
    são mídia de VINHO — não viticultura;
  · vários "creators" de cultura têm presença mínima no Instagram
    (@giulia_tonello 90, @pedro.pastore 536, @filippoballardin 820);
  · @nicolo.polo devolve um perfil chamado "phineASS", e @giacomolepri devolve
    "giacomo_le." com 2 seguidores e 0 posts — NAME_MATCH = NO_MATCH;
  · @davide_gomiero — o único produtor de 400 ha da lista, com ~410 mil
    seguidores segundo a imprensa — NÃO devolveu perfil. O handle da seed
    provavelmente não é o dele.

Esse último caso é o mais caro se passar batido: o melhor candidato da lista
some porque o endereço está errado, e a lista continuaria parecendo correta.

REGRA DE OURO DESTE ARQUIVO
-----------------------------
Perfil que a rota não devolveu sai como `HANDLE_UNRESOLVED`, nunca como
"não existe". A rota devolveu 25 de 25 objetos, mas alguns vieram sem dado —
e "veio vazio" e "não existe" continuam sendo coisas diferentes.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import creators as cr                                        # noqa: E402

MISSION = '14-MAPA-DE-CREATORS-EAME'

# Handles cuja evidência ABERTA contradiz o silêncio da rota paga: a imprensa
# mede alcance grande e o Instagram do handle da seed não devolve nada.
# Isso não é "perfil morto" — é suspeita de HANDLE ERRADO NA SEED.
CONTRADICOES = {
    '@davide_gomiero': 'imprensa mede ~410.000 seguidores e empresa agrícola de '
                       '~400 ha; a rota não devolveu perfil para este handle',
    '@evolovers': 'imprensa descreve comunidade consolidada de olivicultura desde '
                  '2020; a rota devolveu perfil com 13 seguidores e 9 posts',
    '@maria.pezone': 'imprensa mede ~21.000 seguidores; a rota não devolveu perfil',
    '@yuliyapyliavska': 'imprensa mede ~109.000 no Instagram; a rota não devolveu perfil',
}


def _num(v):
    return v if isinstance(v, (int, float)) else None


def montar():
    seed = {r['ORIGIN_ID']: r for r in cr.carregar('SEED-IT-CANDIDATES.json')}
    resolvidos = {p['HANDLE']: p for p in cr.carregar('SEED-IT-RESOLVED.json')}
    validados = {}
    caminho = os.path.join(cr.BASE, 'SEED-IT-VALIDATION.json')
    if os.path.exists(caminho):
        with open(caminho, encoding='utf-8') as f:
            validados = {v['HANDLE']: v for v in json.load(f)['VALIDATIONS']}

    fora = []
    for handle, s in seed.items():
        ap = resolvidos.get(handle, {})
        vw = validados.get(handle, {})
        foll = _num(ap.get('FOLLOWERS'))
        posts = _num(ap.get('POSTS_COUNT'))

        # Estado do handle — três casos, nunca dois.
        if foll is None and posts is None:
            estado_handle = 'HANDLE_UNRESOLVED'
        elif (foll or 0) < 100 and (posts or 0) < 20:
            estado_handle = 'RESOLVED_MINIMAL_PRESENCE'
        else:
            estado_handle = 'RESOLVED'

        reg = cr.registro_vazio()
        reg.update({
            'CREATOR_ID': s['CREATOR_ID'], 'ORIGIN_ID': handle,
            'NAME': vw.get('NAME_MEASURED') or s['NAME'],
            'DISPLAY_NAME': ap.get('PROFILE_FULL_NAME', cr.NAO_SEI),
            'COUNTRY': 'IT', 'LANGUAGE': 'it',
            'REGION': vw.get('REGION', cr.NAO_SEI),
            'OCCUPATION': vw.get('OCCUPATION', cr.NAO_SEI),
            'ENTITY_KIND': 'PERSON',
            'INSTAGRAM': handle, 'PLATFORMS': ['INSTAGRAM'],
            'PROFILE_URL': ap.get('PROFILE_URL', cr.NAO_SEI),
            'HANDLE_EXISTS': estado_handle,
            'NAME_MATCH': ap.get('NAME_MATCH', 'NOT_TESTED'),
            'FOLLOWERS_BY_PLATFORM': ({'INSTAGRAM': foll} if foll is not None
                                      else cr.NAO_SEI),
            'AS_OF_DATE': ap.get('AS_OF_DATE', cr.NAO_SEI),
            'POSTS_LAST_30D': cr.NAO_SEI, 'POSTS_LAST_90D': cr.NAO_SEI,
            'LAST_ACTIVITY_DATE': ap.get('LAST_ACTIVITY_DATE', cr.NAO_SEI),
            'ACTIVITY_STATE': 'NOT_MEASURED',
            'CREATOR_TYPE': vw.get('CREATOR_TYPE', cr.NAO_SEI),
            'ACTUAL_FARMER': vw.get('ACTUAL_FARMER', 'NOT_KNOWN'),
            'ACTUAL_FARMER_EVIDENCE': vw.get('ACTUAL_FARMER_EVIDENCE', 'não testado'),
            'SENSOR_ROLE_LINK': 'NOT_LINKED',
            'ACTIVATION_CREATOR': 'NOT_KNOWN',
            'TECHNICAL_SENSOR_CANDIDATE': 'NOT_KNOWN',
            'CROP_CLAIMED_BY_SEED': s['CROP_CLAIMED_BY_SEED'],
            'CROP_PROVED_BY_CONTENT': vw.get('CROP_PROVED_BY_CONTENT', cr.NAO_SEI),
            'CROPS': vw.get('CROP_PROVED_BY_CONTENT', cr.NAO_SEI),
            'CROP_STATE': vw.get('CROP_STATE', 'NOT_KNOWN'),
            'CROP_EVIDENCE': vw.get('CROP_EVIDENCE', 'não validado nesta rodada'),
            'CROP_PROOF_URLS': vw.get('CROP_PROOF_URLS', []),
            'SUSPECTED_CHAIN_MISMATCH': s.get('SUSPECTED_CHAIN_MISMATCH'),
            'SUSPECTED_CHAIN_MISMATCH_REASON': s.get('SUSPECTED_CHAIN_MISMATCH_REASON'),
            'AUDIENCE_TYPE': vw.get('AUDIENCE_TYPE', 'NOT_KNOWN'),
            'IDENTITY_STATE': vw.get('IDENTITY_STATE', 'NOT_PROVED'),
            'IDENTITY_EVIDENCE': vw.get('IDENTITY_EVIDENCE',
                                        'só a seed afirma; não validado'),
            'BRAND_RELATIONSHIP_STATE': 'NOT_KNOWN',
            'ADAMA_COLLABORATION_OBSERVED': 'NOT_TESTED',
            'SOURCE_URL': ap.get('PROFILE_URL') or 'SEED_EXTERNO',
            'SOURCE_KIND': 'SEED + WEB_SEARCH + APIFY_INSTAGRAM',
            'SOURCE_ID': MISSION, 'CAPTURE_DATE': '2026-08-30',
            'COLLECTION_ROUTE': 'apify:apify~instagram-profile-scraper (runner residencial)',
            'DISCOVERY_ROUTES': ['SEED_EXTERNO_IT', 'WEB_SEARCH', 'APIFY_INSTAGRAM'],
        })
        for c in ('WINE_RELEVANCE', 'VITICULTURE_RELEVANCE',
                  'OLIVE_OIL_RELEVANCE', 'OLIVE_GROWING_RELEVANCE'):
            reg[c] = vw.get(c, 'NOT_KNOWN')

        if handle in CONTRADICOES and estado_handle != 'RESOLVED':
            reg['HANDLE_EXISTS'] = 'SEED_HANDLE_LIKELY_WRONG'
            reg['IDENTITY_EVIDENCE'] = (
                'CONTRADIÇÃO MEDIDA: %s. O handle da seed provavelmente não é o '
                'desta pessoa — resolver o endereço antes de descartar o candidato.'
                % CONTRADICOES[handle])

        fit, porque_fit = cr.fit_para_adama(reg)
        reg['AUDIENCE_FIT_FOR_ADAMA'] = fit
        estado, porques = cr.relevancia(reg)
        reg['RELEVANCE_STATE'] = estado
        reg['WHY_RELEVANT'] = porques + ['FIT_ADAMA=%s: %s' % (fit, porque_fit)]

        faltas = cr.checar(reg)
        if faltas:
            print('PORTAO %s: %s' % (handle, faltas)); raise SystemExit(1)
        fora.append(reg)

    from collections import Counter
    com_foll = [(r['ORIGIN_ID'], r['FOLLOWERS_BY_PLATFORM']['INSTAGRAM'], r['CREATOR_TYPE'])
                for r in fora if isinstance(r['FOLLOWERS_BY_PLATFORM'], dict)]
    com_foll.sort(key=lambda x: -x[1])
    top5 = com_foll[:5]
    vinho_no_top5 = [t for t in top5 if t[2] == 'WINE_MEDIA_CREATOR']

    corpo = {
        'SOURCE_ID': MISSION, 'CAPTURED_AT': '2026-08-30',
        'LAW': 'Três camadas, três estados: a seed ALEGA, a web MEDE identidade, '
               'a Apify MEDE presença. Nenhuma vira a outra.',
        'COUNT': len(fora),
        'HANDLE_STATE': dict(Counter(r['HANDLE_EXISTS'] for r in fora)),
        'NAME_MATCH': dict(Counter(r['NAME_MATCH'] for r in fora)),
        'CROP_STATE': dict(Counter(r['CROP_STATE'] for r in fora)),
        'AUDIENCE_FIT_FOR_ADAMA': dict(Counter(r['AUDIENCE_FIT_FOR_ADAMA'] for r in fora)),
        'TOP5_BY_FOLLOWERS': [{'HANDLE': h, 'FOLLOWERS': f, 'TYPE': t} for h, f, t in top5],
        'TOP5_FINDING':
            '%d dos 5 maiores perfis da seed são mídia de VINHO, não viticultura. '
            'Somam %d seguidores. Ordenar esta lista por seguidores entregaria ao '
            'Marketing uma audiência de consumidor de vinho como se fosse de '
            'produtor de uva.' % (len(vinho_no_top5), sum(f for _, f, _ in top5)),
        'SEED_HANDLE_LIKELY_WRONG': [r['ORIGIN_ID'] for r in fora
                                     if r['HANDLE_EXISTS'] == 'SEED_HANDLE_LIKELY_WRONG'],
        'CREATORS': fora,
    }
    with open(os.path.join(cr.BASE, 'IT-CREATORS-CONSOLIDATED.json'), 'w',
              encoding='utf-8') as f:
        json.dump(corpo, f, ensure_ascii=False, indent=2)
    print('gravado: data/samples/CREATOR-MAP-EAME/IT-CREATORS-CONSOLIDATED.json')
    print('HANDLE_STATE:', corpo['HANDLE_STATE'])
    print('NAME_MATCH  :', corpo['NAME_MATCH'])
    print('FIT_ADAMA   :', corpo['AUDIENCE_FIT_FOR_ADAMA'])
    print('TOP5:', [(h, f, t) for h, f, t in top5])
    print('HANDLE SUSPEITO NA SEED:', corpo['SEED_HANDLE_LIKELY_WRONG'])


if __name__ == '__main__':
    montar()
