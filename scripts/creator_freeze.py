#!/usr/bin/env python3
"""
CONGELAMENTO DO PILOTO (§1) — o estado final desta fase, derivado e não digitado.

    python3 scripts/creator_freeze.py

POR QUE UM ARTEFATO DE CONGELAMENTO
-------------------------------------
Um estado congelado escrito à mão envelhece em silêncio: alguém mexe num
artefato, o número muda, e o documento continua a dizer o antigo. Aqui cada
número é **lido dos artefatos** no momento em que o congelamento é gravado, e a
conferência abaixo falha se algum divergir do que o dono declarou.

O QUE ESTE ARQUIVO NÃO AUTORIZA
---------------------------------
Nenhum estado além do declarado. Congelar é fixar o que foi medido — não é
arredondar para cima o que quase fechou.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import creators as cr                                        # noqa: E402

MISSION = '14-MAPA-DE-CREATORS-EAME'
CAPTURA = '2026-08-30'

# O estado que o dono declarou. A verificação abaixo compara com o MEDIDO.
DECLARADO = {
    'PERSON_CREATOR_ACTIVATION_READY': 8,
    'FARM_BUSINESS_PARTNER_READY': 2,
    'MARKETING_CONTACTABLE_ENTITIES_READY': 10,
}


def montar():
    fichas = cr.carregar('WHO-COULD-MARKETING-CALL.json')
    medido = cr.metricas_de_prontidao(fichas)

    divergencias = [
        '%s: declarado=%s medido=%s' % (k, v, medido.get(k))
        for k, v in DECLARADO.items() if medido.get(k) != v
    ]

    prontos = [f for f in fichas if f.get('ACTIVATION_STATE') == 'ACTIVATION_READY']
    franceses = {f['CREATOR']: f['ACTIVATION_STATE'] for f in fichas
                 if f.get('COUNTRY') == 'FR'
                 and str(f.get('CREATOR')) in ('David Forge', 'Gilles Van Kempen')}

    corpo = {
        'SOURCE_ID': MISSION, 'CAPTURED_AT': CAPTURA,
        'STATE': 'FROZEN_WAITING_FOR_INTELLIGENCE',
        'WHAT_FROZEN_MEANS':
            'fixar o que foi medido. NAO e arredondar para cima o que quase fechou, '
            'e nao autoriza nenhum estado alem dos declarados aqui.',

        'READINESS': medido,
        'PROHIBITED_METRIC': {'NAME': cr.METRICA_PROIBIDA, 'STATUS': 'PROHIBITED_METRIC',
                              'WHY': 'pessoa != empresa; a soma so pode chamar-se '
                                     'MARKETING_CONTACTABLE_ENTITIES_READY'},
        'DECLARED_VS_MEASURED': ('MATCH' if not divergencias else divergencias),

        'FRANCE': franceses,
        'ITALY_VITE': {
            'STATE': 'NOT_READY',
            'CLASSIFICATION': 'CAPABILITY_COVERAGE_GAP',
            'DOES_NOT_PROVE': 'NO_CREATORS_EXIST',
            'CAUSE': [
                'candidatos consumer/wine-media nao provam creator agricola',
                'Enovitis oficial foi resolvido (@enovitis_, site enovitisincampo.it)',
                '12 publicacoes medidas',
                'zero pessoas reveladas',
                'feiras observadas rendem predominantemente EMPRESAS',
                'falta uma porta de PESSOAS em viticultura',
            ],
        },
        'ENOVITIS': {
            'OFFICIAL_IDENTITY': 'PROVED',
            'CREATOR_HUB_YIELD': '0 pessoas / 12 publicacoes medidas',
            'CREATOR_HUB_ROLE': 'DEMOTED',
            'TECHNICAL_EVENT_VALUE': 'PRESERVED',
        },
        'CONTENT_RATE_MIN_N': {'VALUE': 30, 'STATUS': 'PROPOSAL_ONLY',
                               'WHY': 'aguarda arbitragem; nao foi tornada canonica'},
        'REVALIDATION_RULE': 'NOT_YET_DEFINED',
        'SUPABASE': {'CANONICAL_CREATOR_SCHEMA_VISIBLE_IN_REPO': 'NO',
                     'DOES_NOT_MEAN': 'SUPABASE_EAME_DOES_NOT_EXIST',
                     'MIGRATION_APPLIED': 'NO', 'PROPOSAL': 'PRESERVED'},
        'ENTITY_SEPARATION_LAW':
            'PERSON_CREATOR e FARM_BUSINESS nunca se somam sob o nome de creators. '
            'Uma FARM_BUSINESS pode ser altamente util para Marketing, campo, evento '
            'ou conteudo — e continua fora da contagem de creators-pessoa.',
        'CONVERGENCE_BOUNDARY': {
            'CAN_ADD': ['ACTIVATION_ROUTE_AVAILABLE', 'RELEVANT_PUBLIC_VOICE_AVAILABLE'],
            'CANNOT_CONFIRM': ['FIELD_PROBLEM', 'INCIDENCE', 'MARKET_OPPORTUNITY',
                               'PRODUCT_FIT'],
            'LAYER': 'AUDIENCE / ACTIVATION / PUBLIC VOICE',
        },
        'MAIN_QUESTION': 'WHO COULD MARKETING EVALUATE / CALL?',
        'NOT_THE_QUESTION': 'WHO SHOULD MARKETING HIRE?',
        'READY_ENTITIES': [
            {'NAME': f['CREATOR'], 'HANDLE': f['HANDLE'], 'COUNTRY': f['COUNTRY'],
             'REGION': f['REGION'], 'CROPS': f['CROPS'],
             'ENTITY_TYPE': f['ACTIVATION_ENTITY_TYPE'],
             'LAST_ACTIVITY_DATE': (f.get('RECENT_ACTIVITY') or {}).get(
                 'LAST_ACTIVITY_DATE')} for f in prontos],
    }
    with open(os.path.join(cr.BASE, 'PILOT-FREEZE-STATE.json'), 'w',
              encoding='utf-8') as f:
        json.dump(corpo, f, ensure_ascii=False, indent=2)
    print('gravado: PILOT-FREEZE-STATE.json')
    print('STATE =', corpo['STATE'])
    print('DECLARADO vs MEDIDO:', corpo['DECLARED_VS_MEASURED'])
    for k, v in medido.items():
        if k != 'NOTE':
            print('  %-42s %s' % (k, v))
    print('FRANCE:', franceses)
    if divergencias:
        print('DIVERGENCIA — o congelamento NAO bate com o declarado')
        raise SystemExit(1)


if __name__ == '__main__':
    montar()
