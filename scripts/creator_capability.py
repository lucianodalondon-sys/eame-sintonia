#!/usr/bin/env python3
"""
CREATOR-CAPABILITY-EAME — o artefato que outra missão consulta.

    python3 scripts/creator_capability.py

PARA QUE ESTE ARQUIVO EXISTE
------------------------------
A pergunta que a Convergência fará não é "me dá a lista de creators". É:

    COUNTRY x CROP x ISSUE -> "ha alguem relevante para ativacao aqui?"

Um mapa aninhado para leitura humana não responde isso em código. Este artefato
responde: índice por `COUNTRY`, `REGION`, `CROP`, `ENTITY_TYPE` e
`ACTIVATION_STATE`, com a resposta honesta `NOT_READY` e a **causa** quando não
há ninguém — porque "não temos" e "não procuramos" são respostas diferentes.

O QUE ELE NÃO FAZ
-------------------
Não ordena, não pontua e não recomenda contratação. `ACTIVATION_STATE` significa
"o Marketing já consegue avaliar esta pessoa" — nada além disso.
"""
import json
import os
import sys
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import creators as cr                                        # noqa: E402

MISSION = '14-MAPA-DE-CREATORS-EAME'
CAPTURA = '2026-08-30'

# Recortes que a missão declarou perseguir, com o estado de cada um. Um recorte
# ausente do índice não é NOT_READY — é NOT_ASKED, e a diferença importa.
RECORTES_DECLARADOS = [
    ('ES', 'ALMERIA', 'PROTECTED_HORTICULTURE'),
    ('ES', 'ANDALUCIA', 'OLIVE'),
    ('FR', 'CENTRE_VAL_DE_LOIRE', 'CEREALS'),
    ('IT', 'ANY', 'GRAPEVINE'),
    ('IT', 'VENETO', 'MAIZE'),
]

# Culturas guarda-chuva e o que elas contêm. Sem isto, perguntar por CEREALS
# devolveria NOT_READY enquanto WHEAT e BARLEY tinham gente pronta — e a resposta
# errada nao viria de ausencia de dado, viria de desencontro de taxonomia.
GRUPOS_DE_CULTURA = {
    'CEREALS': ['CEREALS', 'WHEAT', 'BARLEY', 'DURUM_WHEAT', 'SOFT_WHEAT'],
    'ARABLE_CROPS': ['WHEAT', 'BARLEY', 'MAIZE', 'RAPESEED', 'SUNFLOWER', 'SOYBEAN'],
    'PROTECTED_HORTICULTURE': ['PROTECTED_HORTICULTURE', 'TOMATO', 'PEPPER'],
}

# §2 · ACTIVATION_READY tem DATA. Atividade recente é perecível: um recorte
# medido há três meses não é o mesmo recorte hoje. Mas inventar uma validade
# ("vale 90 dias") seria inventar precisão que nada sustenta — a cadência de
# publicação varia por pessoa, por cultura e por estação.
#
# Por isso a regra fica declarada como AUSENTE, e não preenchida por plausibilidade.
REVALIDATION_RULE = 'NOT_YET_DEFINED'
REVALIDATION_NOTE = (
    'Nenhuma validade arbitraria foi atribuida. ACTIVITY_WINDOW_MEASURED diz o que '
    'foi medido e AS_OF_DATE diz quando; quem usar a ficha decide, com esses dois '
    'dados, se precisa remedir. Ninguem fica "pronto para sempre".')

CAUSAS_NOT_READY = {
    ('IT', 'ANY', 'GRAPEVINE'):
        'Zero creators PESSOA italianos com VITICULTURE_RELEVANCE provada. Os '
        'candidatos de vide da seed externa eram MIDIA DE VINHO (critico, sommelier, '
        'blogger) e sairam como WRONG_ASSIGNMENT. A porta natural — Enovitis in Campo '
        '— teve a conta oficial PROVADA (@enovitis_) e rendeu ZERO pessoas em 12 '
        'publicacoes. O padrao medido e consistente: feiras mencionam empresas, '
        'premios mencionam pessoas. Falta uma porta italiana de PESSOAS em viticultura.',
}


def _registro(f):
    """Um resultado do lookup — com tudo o que §6 exige preservado.

    Inclusive `WHAT_IS_NOT_KNOWN`: quem consulta a capacidade a partir de outra
    missão precisa receber a lacuna junto com o achado, senão a lacuna perde-se
    exatamente no ponto em que o dado é reutilizado.
    """
    ativ = f.get('RECENT_ACTIVITY') or {}
    return {
        'CREATOR': f.get('CREATOR'), 'HANDLE': f.get('HANDLE'),
        'PUBLIC_CHANNEL': f.get('PROFILE_URL', cr.NAO_SEI),
        'COUNTRY': f.get('COUNTRY'), 'REGION': f.get('REGION'),
        'ENTITY_TYPE': f.get('ACTIVATION_ENTITY_TYPE'),
        'ACTIVATION_STATE': f.get('ACTIVATION_STATE'),
        'ACTUAL_FARMER': f.get('ACTUAL_FARMER'),
        'IDENTITY_EVIDENCE': f.get('EVIDENCE') or [],
        'CROP_PROOF': {'CROPS': f.get('CROPS'), 'STATE': f.get('CROP_STATE'),
                       'WHY': f.get('WHY_RELEVANT')},
        'RECENT_ACTIVITY': ativ,
        # §2 · a ficha carrega a sua propria data e o que foi medido
        'AS_OF_DATE': CAPTURA,
        'LAST_ACTIVITY_DATE': ativ.get('LAST_ACTIVITY_DATE', cr.NAO_SEI),
        'ACTIVITY_WINDOW_MEASURED': '30 e 90 dias, contados a partir de AS_OF_DATE',
        'ACTIVITY_EVIDENCE': ('posts/videos lidos na rota publica; '
                              '30d=%s 90d=%s' % (ativ.get('POSTS_LAST_30D', cr.NAO_SEI),
                                                 ativ.get('POSTS_LAST_90D', cr.NAO_SEI))),
        'REVALIDATION_NEEDED_AFTER': REVALIDATION_RULE,
        'PUBLIC_CONTACT': f.get('PUBLIC_CONTACT', cr.NAO_SEI),
        'AUDIENCE_FACING': f.get('FACING', cr.NAO_SEI),
        'AUDIENCE_FIT_FOR_ADAMA': f.get('AUDIENCE_FIT_FOR_ADAMA'),
        'BRAND_HISTORY': f.get('BRAND_HISTORY', 'NOT_OBSERVED'),
        'COMPETITOR_HISTORY': f.get('COMPETITOR_HISTORY', 'NOT_OBSERVED'),
        'WHAT_IS_NOT_KNOWN': f.get('MISSING_PROOFS'),
    }


def montar():
    fichas = cr.carregar('WHO-COULD-MARKETING-CALL.json')
    prontos = [f for f in fichas if f.get('ACTIVATION_STATE') == 'ACTIVATION_READY']

    indice = defaultdict(list)
    por_regiao, por_entidade, por_estado = (defaultdict(list), defaultdict(list),
                                            defaultdict(list))
    for f in fichas:
        crops = f.get('CROPS')
        crops = crops if isinstance(crops, list) else ([] if crops in (None, cr.NAO_SEI)
                                                       else [crops])
        for c in (crops or ['NOT_KNOWN']):
            registro = _registro(f)
            indice[(f.get('COUNTRY'), c)].append(registro)
            por_regiao[(f.get('COUNTRY'), f.get('REGION'))].append(registro)
            por_entidade[f.get('ACTIVATION_ENTITY_TYPE')].append(registro)
            por_estado[f.get('ACTIVATION_STATE')].append(registro)

    lookup = {}
    for (pais, crop), gente in sorted(indice.items(), key=lambda x: (str(x[0][0]), str(x[0][1]))):
        chave = '%s|%s' % (pais, crop)
        pessoas_prontas = [g for g in gente
                           if g['ACTIVATION_STATE'] == 'ACTIVATION_READY'
                           and g['ENTITY_TYPE'] == 'PERSON_CREATOR']
        negocios_prontos = [g for g in gente
                            if g['ACTIVATION_STATE'] == 'ACTIVATION_READY'
                            and g['ENTITY_TYPE'] in ('FARM_BUSINESS',
                                                     'FARMER_FAMILY_ACCOUNT')]
        lookup[chave] = {
            'COUNTRY': pais, 'CROP': crop,
            'PERSON_CREATOR_ACTIVATION_READY': len(pessoas_prontas),
            'FARM_BUSINESS_PARTNER_READY': len(negocios_prontos),
            'CANDIDATES_TOTAL': len(gente),
            'ANSWER': ('READY' if (pessoas_prontas or negocios_prontos) else 'NOT_READY'),
            'PEOPLE': pessoas_prontas,
            'BUSINESSES': negocios_prontos,
            'ALL_CANDIDATES': gente,
        }

    # recortes declarados, com causa quando vazio
    declarados = {}
    for pais, regiao, crop in RECORTES_DECLARADOS:
        membros = GRUPOS_DE_CULTURA.get(crop, [crop])
        pessoas, negocios, via = 0, 0, []
        for m in membros:
            v = lookup.get('%s|%s' % (pais, m))
            if v and v['ANSWER'] == 'READY':
                pessoas += v['PERSON_CREATOR_ACTIVATION_READY']
                negocios += v['FARM_BUSINESS_PARTNER_READY']
                via.append(m)
        if pessoas or negocios:
            declarados['%s|%s|%s' % (pais, regiao, crop)] = {
                'ANSWER': 'READY',
                'PERSON_CREATOR_ACTIVATION_READY': pessoas,
                'FARM_BUSINESS_PARTNER_READY': negocios,
                'MATCHED_VIA_CROPS': via,
                'NOTE': ('%s e cultura guarda-chuva; a resposta vem das culturas '
                         'membro %s' % (crop, via)) if len(membros) > 1 else cr.NAO_SEI,
            }
        else:
            declarados['%s|%s|%s' % (pais, regiao, crop)] = {
                'ANSWER': 'NOT_READY',
                'CAUSE': CAUSAS_NOT_READY.get((pais, regiao, crop),
                                              'sem candidato pronto neste recorte'),
            }

    metricas = cr.metricas_de_prontidao(fichas)
    corpo = {
        'SOURCE_ID': MISSION, 'CAPTURED_AT': CAPTURA,
        'QUESTION_ANSWERED':
            'COUNTRY x REGION x CROP -> ha pessoa ou entidade relevante para ativacao?',
        'WHAT_THIS_IS_NOT':
            'nao ordena, nao pontua, nao recomenda contratacao. ACTIVATION_STATE '
            'significa que o Marketing JA CONSEGUE AVALIAR — nada alem disso.',
        'READINESS_METRICS': metricas,
        'METRIC_LAW': 'a soma NUNCA se chama CREATORS_READY. Pessoa != empresa.',
        'DECLARED_SLICES': declarados,
        'LOOKUP_BY_COUNTRY_CROP': lookup,
        'LOOKUP_BY_COUNTRY_REGION': {'%s|%s' % (k[0], k[1]): v
                                     for k, v in sorted(por_regiao.items(),
                                                        key=lambda x: str(x[0]))},
        'LOOKUP_BY_ENTITY_TYPE': {str(k): v for k, v in sorted(por_entidade.items(),
                                                               key=lambda x: str(x[0]))},
        'LOOKUP_BY_ACTIVATION_STATE': {str(k): v for k, v in sorted(por_estado.items(),
                                                                    key=lambda x: str(x[0]))},
        'FIELDS_PRESERVED_PER_RESULT': [
            'IDENTITY_EVIDENCE', 'CROP_PROOF', 'RECENT_ACTIVITY', 'PUBLIC_CHANNEL',
            'PUBLIC_CONTACT', 'AUDIENCE_FACING', 'BRAND_HISTORY', 'COMPETITOR_HISTORY',
            'AS_OF_DATE', 'WHAT_IS_NOT_KNOWN'],
        'REVALIDATION_RULE': REVALIDATION_RULE,
        'REVALIDATION_NOTE': REVALIDATION_NOTE,
        'NO_RANKING': 'este artefato nao ordena e nao pontua. A ordem das listas e a '
                      'ordem de insercao, sem significado.',
        # §8 · a fronteira com a Convergencia, escrita no proprio artefato
        'CONVERGENCE_BOUNDARY': {
            'CREATOR_MAP_CAN_ADD': ['ACTIVATION_ROUTE_AVAILABLE',
                                    'RELEVANT_PUBLIC_VOICE_AVAILABLE'],
            'CREATOR_MAP_CANNOT_CONFIRM': ['FIELD_PROBLEM', 'INCIDENCE',
                                           'MARKET_OPPORTUNITY', 'PRODUCT_FIT'],
            'LAYER': 'AUDIENCE / ACTIVATION / PUBLIC VOICE',
            'WHY': 'um creator prova que existe VOZ para aquela cultura naquele lugar. '
                   'Nao prova que ha problema de campo, nem incidencia, nem oportunidade '
                   'de mercado, nem encaixe de produto — essas vem de outras camadas.',
        },
        'ENTITY_TYPES': list(cr.ENTIDADES_DE_ATIVACAO),
        'ACTIVATION_STATES': list(cr.RELEVANCIA),
        'JOIN_KEYS_FOR_OTHER_MISSIONS': {
            'KEYS': ['PERSON_ID', 'ENTITY_ID', 'BRAND', 'COUNTRY', 'CROP', 'OBSERVED_AT'],
            'META_CROSSOVER': 'se a missao Meta encontrar uma destas pessoas num anuncio, '
                              'isso vira CREATOR_APPEARANCE_OBSERVED. PAID_CREATOR_RELATION '
                              'so sobe com prova adicional — e nao e antecipado aqui.',
        },
        'NOT_ASKED_IS_NOT_NOT_READY':
            'um recorte ausente deste indice nao e NOT_READY: e NOT_ASKED. "nao temos" e '
            '"nao procuramos" sao respostas diferentes.',
    }
    with open(os.path.join(cr.BASE, 'CREATOR-CAPABILITY-EAME.json'), 'w',
              encoding='utf-8') as f:
        json.dump(corpo, f, ensure_ascii=False, indent=2)
    print('gravado: CREATOR-CAPABILITY-EAME.json')
    print('METRICAS:', {k: v for k, v in metricas.items() if k != 'NOTE'})
    print('RECORTES DECLARADOS:')
    for k, v in declarados.items():
        print('  %-34s %s' % (k, v['ANSWER']))
    prontas = [k for k, v in lookup.items() if v['ANSWER'] == 'READY']
    print('COUNTRY|CROP com resposta READY: %d' % len(prontas))
    for k in prontas:
        print('   %-28s pessoas=%d empresas=%d' % (k,
              lookup[k]['PERSON_CREATOR_ACTIVATION_READY'],
              lookup[k]['FARM_BUSINESS_PARTNER_READY']))


if __name__ == '__main__':
    montar()
