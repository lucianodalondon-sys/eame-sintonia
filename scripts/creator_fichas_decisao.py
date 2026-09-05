#!/usr/bin/env python3
"""
FICHAS DE DECISÃO (§6 e §7) — o que o Marketing lê, e o que ele NÃO deve ler.

    python3 scripts/creator_fichas_decisao.py

DUAS FICHAS PORQUE SÃO DUAS RELAÇÕES
--------------------------------------
Uma pessoa creator e uma exploração com canal forte não se contratam da mesma
forma, não custam o mesmo e não falam pela mesma boca. Por isso saem em fichas
com CAMPOS diferentes, não só em listas diferentes.

A LINGUAGEM É PARTE DO CONTRATO
---------------------------------
Nenhuma ficha diz `BEST`, `TOP` ou `RECOMMENDED TO HIRE` — e há teste para isso.
A ferramenta ajuda o Marketing a decidir **quem avaliar**; ela não decide
contratação. Por isso toda ficha carrega `WHAT_IS_NOT_KNOWN`: o que falta é tão
parte da decisão quanto o que se sabe.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import creators as cr                                        # noqa: E402

MISSION = '14-MAPA-DE-CREATORS-EAME'
CAPTURA = '2026-08-30'
PROIBIDAS = ('BEST', 'TOP CREATOR', 'RECOMMENDED TO HIRE', 'MELHOR', 'CONTRATAR')

PAPEIS_DE_ATIVACAO = ('FIELD_CONTENT_PARTNER', 'FARM_VISIT', 'TECHNICAL_EVENT_PARTNER',
                      'CONTENT_COLLABORATION', 'CASE_STUDY_CANDIDATE', 'OTHER',
                      'NOT_KNOWN')


def _nao_sabido(f):
    """O que falta — em linguagem que o Marketing usa, não em código interno."""
    fora = []
    if f.get('AUDIENCE_TYPE') in (None, 'NOT_KNOWN', cr.NAO_SEI):
        fora.append('a composição real da audiência não foi medida — só o lado do '
                    'balcão (FACING) foi observado')
    if f.get('REGION') in (None, cr.NAO_SEI, 'NOT_KNOWN'):
        fora.append('a região exata não está resolvida')
    if f.get('BRAND_HISTORY') in ('NOT_OBSERVED', None, []):
        fora.append('nenhum histórico de marca foi observado — o que não significa '
                    'que não exista')
    n = f.get('N_CONTENT_ITEMS_REVIEWED')
    if isinstance(n, int):
        fora.append('a leitura de conteúdo cobriu %d publicações; abaixo do N que a '
                    'missão propôs (30) para publicar taxas por tipo de conteúdo' % n)
    if f.get('ADAMA_HISTORY') == 'NOT_OBSERVED':
        fora.append('nenhuma colaboração ADAMA observada — busca feita, não é prova '
                    'de ausência')
    return fora


def montar():
    fichas = cr.carregar('WHO-COULD-MARKETING-CALL.json')
    prontos = [f for f in fichas if f.get('ACTIVATION_STATE') == 'ACTIVATION_READY']

    pessoas, negocios = [], []
    for f in prontos:
        base_ev = f.get('EVIDENCE') or []
        if f.get('ACTIVATION_ENTITY_TYPE') == 'PERSON_CREATOR':
            pessoas.append({
                'NAME': f.get('CREATOR'),
                'HANDLE_OR_PUBLIC_CHANNEL': f.get('HANDLE'),
                'PROFILE_URL': f.get('PROFILE_URL'),
                'COUNTRY': f.get('COUNTRY'), 'REGION': f.get('REGION'),
                'ENTITY_TYPE': f.get('ACTIVATION_ENTITY_TYPE'),
                'ACTUAL_FARMER': f.get('ACTUAL_FARMER'),
                'CROP_PROVED': f.get('CROPS'),
                'CROP_PROOF_EVIDENCE': f.get('WHY_RELEVANT'),
                'RECENT_ACTIVITY': f.get('RECENT_ACTIVITY'),
                # §2 · nenhuma ficha diz "pronto para sempre"
                'AS_OF_DATE': CAPTURA,
                'LAST_ACTIVITY_DATE': (f.get('RECENT_ACTIVITY') or {}).get(
                    'LAST_ACTIVITY_DATE', cr.NAO_SEI),
                'ACTIVITY_WINDOW_MEASURED': '30 e 90 dias a partir de AS_OF_DATE',
                'ACTIVITY_EVIDENCE': 'contagem de publicacoes na rota publica medida',
                'REVALIDATION_NEEDED_AFTER': 'NOT_YET_DEFINED',
                'REVALIDATION_NOTE': 'atividade e pericivel; nenhuma validade '
                                     'arbitraria foi atribuida',
                'AUDIENCE_FACING': f.get('FACING'),
                'AUDIENCE_FIT_FOR_ADAMA': f.get('AUDIENCE_FIT_FOR_ADAMA'),
                'AUDIENCE_FIT_REASON': f.get('AUDIENCE_FIT_REASON'),
                'CONTENT_TYPES_OBSERVED': f.get('CONTENT_TYPES_OBSERVED', cr.NAO_SEI),
                'N_CONTENT_ITEMS_REVIEWED': f.get('N_CONTENT_ITEMS_REVIEWED', cr.NAO_SEI),
                'PUBLIC_CONTACT_ROUTE': f.get('PUBLIC_CONTACT'),
                'CONTACT_KIND': f.get('CONTACT_KIND'),
                'BRAND_HISTORY': f.get('BRAND_HISTORY'),
                'COMPETITOR_HISTORY': f.get('COMPETITOR_HISTORY'),
                'ACTIVATION_STATE': f.get('ACTIVATION_STATE'),
                'WHY_MARKETING_MIGHT_EVALUATE':
                    'cultura provada por evidência material, identidade resolvida em '
                    'fonte, atividade recente medida e canal público resolvido — os '
                    'seis requisitos fecham. Isto NÃO é recomendação de contratação.',
                'WHAT_IS_NOT_KNOWN': _nao_sabido(f),
                'EVIDENCE': base_ev,
            })
        elif f.get('ACTIVATION_ENTITY_TYPE') in ('FARM_BUSINESS', 'FARMER_FAMILY_ACCOUNT'):
            negocios.append({
                'ENTITY_NAME': f.get('CREATOR'),
                'PUBLIC_CHANNEL': f.get('HANDLE'),
                'PROFILE_URL': f.get('PROFILE_URL'),
                'COUNTRY': f.get('COUNTRY'), 'REGION': f.get('REGION'),
                'CROP': f.get('CROPS'),
                'PRODUCTION_ROLE': f.get('ACTUAL_FARMER_EVIDENCE', cr.NAO_SEI),
                'RECENT_ACTIVITY': f.get('RECENT_ACTIVITY'),
                'AS_OF_DATE': CAPTURA,
                'LAST_ACTIVITY_DATE': (f.get('RECENT_ACTIVITY') or {}).get(
                    'LAST_ACTIVITY_DATE', cr.NAO_SEI),
                'ACTIVITY_WINDOW_MEASURED': '30 e 90 dias a partir de AS_OF_DATE',
                'ACTIVITY_EVIDENCE': 'contagem de publicacoes na rota publica medida',
                'REVALIDATION_NEEDED_AFTER': 'NOT_YET_DEFINED',
                'PUBLIC_CONTACT': f.get('PUBLIC_CONTACT'),
                'WHY_RELEVANT': f.get('WHY_RELEVANT'),
                'POSSIBLE_ACTIVATION_ROLE': ['FIELD_CONTENT_PARTNER', 'FARM_VISIT',
                                             'CASE_STUDY_CANDIDATE'],
                'ACTIVATION_ROLE_NOTE':
                    'papéis POSSÍVEIS, não acordados. Esta entidade NÃO é chamada de '
                    'influencer: é uma exploração/empresa com canal público.',
                'WHAT_IS_NOT_KNOWN': _nao_sabido(f),
                'EVIDENCE': base_ev,
            })

    # o portão de linguagem
    texto = json.dumps({'P': pessoas, 'N': negocios}, ensure_ascii=False).upper()
    violacoes = [p for p in PROIBIDAS if p in texto]
    if violacoes:
        print('LINGUAGEM_PROIBIDA nas fichas: %s' % violacoes); raise SystemExit(1)

    corpo = {
        'SOURCE_ID': MISSION, 'CAPTURED_AT': '2026-08-30',
        'LAW': 'A ferramenta ajuda o Marketing a decidir QUEM AVALIAR. Nao decide '
               'contratacao, e nenhuma ficha usa linguagem de recomendacao — ha '
               'teste que varre as fichas a procura dela.',
        'PERSON_CREATOR_ACTIVATION_READY': len(pessoas),
        'FARM_BUSINESS_PARTNER_READY': len(negocios),
        'MARKETING_CONTACTABLE_ENTITIES_READY': len(pessoas) + len(negocios),
        'METRIC_LAW': 'a soma NUNCA se chama CREATORS_READY',
        'PERSON_CREATOR_FICHES': pessoas,
        'FARM_BUSINESS_FICHES': negocios,
        'POSSIBLE_ACTIVATION_ROLES': list(PAPEIS_DE_ATIVACAO),
    }
    with open(os.path.join(cr.BASE, 'DECISION-FICHES.json'), 'w', encoding='utf-8') as f:
        json.dump(corpo, f, ensure_ascii=False, indent=2)
    print('gravado: DECISION-FICHES.json')
    print('PESSOAS=%d  EMPRESAS=%d' % (len(pessoas), len(negocios)))
    for p in pessoas:
        print('  %-24s %-3s %-22s %s' % (str(p['NAME'])[:24], p['COUNTRY'],
                                         str(p['CROP_PROVED'])[:22],
                                         str(p['PUBLIC_CONTACT_ROUTE'])[:30]))


if __name__ == '__main__':
    montar()
