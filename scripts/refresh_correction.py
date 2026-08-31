# -*- coding: utf-8 -*-
"""PRE-ARBITRATION CORRECTION PASS — tudo derivado de novo, zero rede.

Le apenas: commits congelados (`git show`) e arquivos ja existentes no disco.
NENHUMA requisicao HTTP, nenhum Apify, nenhuma fonte nova.

Emite em `data/refresh-corrected/`:
    SIGNAL-DEPENDENCY-GRAPH-V2.json · FINAL-INTELLIGENCE-REFRESH-EAME-V2.json
    ATTENTION-CANDIDATES.json · ACTION-CANDIDATES.json · SOURCE-LATENCY-EAME.json

    py scripts/refresh_correction.py
"""
import json
import os
import re
import subprocess
import sys
import unicodedata
from datetime import date

try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
except AttributeError:  # pragma: no cover
    pass

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEST = os.path.join(ROOT, 'data', 'refresh-corrected')
HOJE = date(2026, 8, 31)

BASE_REFRESH_COMMIT = 'eb18c87c7e75a3fe0f186c43ff5e60a83b28b0f1'

PIN = {
    'TERRITORIAL': ('11fd7b54e27adaaebed18f049f90b80b05806943',
                    'data/samples/TERRITORIAL/FINAL.json'),
    'FORESIGHT_3L': ('dc32ce0', 'data/samples/COMPETITOR-THREE-LAYER-AUDIT.json'),
    'META_FREEZE': ('a2fad2d', 'data/samples/META-EAME/META-HANDOFF-FREEZE-V1.json'),
    'CREATOR_FREEZE': ('248bd27027506a5f531a117ce50d35eb5304b152',
                       'data/samples/CREATOR-MAP-EAME/PILOT-FREEZE-STATE.json'),
    'DEEP_DELIVERY': ('a509c12',
                      'data/samples/CREATOR-CONTENT-CORPUS-EAME/CORPUS-DELIVERY.json'),
    'IT_EXPIRIES': ('origin/claude/sintonia-italy-pilot-b1l401',
                    'data/samples/IT-T4-001/IT-T4-001-adama-expiries.json'),
    'IT_LABEL_MANIFEST': ('origin/claude/sintonia-italy-pilot-b1l401',
                          'data/samples/IT-T4-001/IT-T4-001-etichette-manifest.json'),
}
EM_ARVORE = {
    'RAIF_2026': 'data/samples/ES-T3-001-raif-olivar-repilo-2026.json',
    'RAIF_SERIE': 'data/samples/ES-T3-001-repilo-serie-historica.json',
    'BACKTEST': 'data/samples/BACKTEST-REPILO-LEAD-TIME.json',
    'SLICE_SCHEMA': 'data/samples/PILOT-SCOPE-MATRIX-V1.json',
}


def do_git(commit, path):
    o = subprocess.run(['git', 'show', '%s:%s' % (commit, path)], cwd=ROOT,
                       capture_output=True)
    if o.returncode != 0:
        raise RuntimeError('nao consegui ler %s:%s' % (commit, path))
    return json.loads(o.stdout.decode('utf-8'))


def do_disco(rel):
    with open(os.path.join(ROOT, rel), encoding='utf-8') as f:
        return json.load(f)


def norm(s):
    s = unicodedata.normalize('NFKD', str(s or ''))
    return ''.join(c for c in s if not unicodedata.combining(c)).lower()


# ══════════════════════════════ 4 · PARSER DE RECORTE — schema, nunca split
def slice_schema():
    """O contrato explicito do recorte congelado.

    BUG CORRIGIDO: o refresh V1 quebrava o slug por '_' e devolvia, para
    `FR_VINE_DOWNY_MILDEW`, CROP='VINE_DOWNY' e ISSUE='MILDEW' — semanticamente
    impossivel. Cinco dos seis recortes funcionavam por sorte: so um tem ISSUE de dois
    tokens. Sorte nao e schema.
    """
    d = do_disco(EM_ARVORE['SLICE_SCHEMA'])
    m = {}
    for c in d['SELECTED_CASES']:
        slug = '%s_%s_%s' % (c['COUNTRY'], c['CROP'], c['ISSUE'])
        m[slug] = {'COUNTRY': c['COUNTRY'], 'CROP': c['CROP'], 'ISSUE': c['ISSUE'],
                   'CASE_ID': c['CASE_ID']}
    return m


def parser_ingenuo(slug):
    p = slug.split('_')
    return {'CROP': '_'.join(p[1:-1]), 'ISSUE': p[-1]}


# ══════════════════════════ 5/6 · PAREAMENTO CULTURA×PROBLEMA no mesmo trecho
CROP_TERMOS = {
    'DURUM_WHEAT': ('frumento duro', 'grano duro', 'ble dur', 'trigo duro'),
    'CEREAL': ('frumento', 'grano', 'cereal', 'ble ', 'trigo', 'orzo', 'cebada'),
    'VINE': ('vite', 'vigne', 'vid ', 'uva', 'grappol', 'vigneto', 'vino'),
    'OLIVE': ('olivo', 'olivar', 'olivier', 'oliva'),
    'MAIZE': ('mais', 'mais ', 'maiz', 'mais'),
}


def pareamento(item):
    """Um documento pode conter varios boletins. Presenca de CEREAL+VINE e de
    SEPTORIA+FUSARIUM+DOWNY_MILDEW no MESMO documento NAO autoriza produto cartesiano.

    O par so fecha quando o termo da cultura aparece DENTRO do trecho que sustenta o
    problema. Fora disso: CROP_ISSUE_PAIRING_NOT_PROVEN.
    """
    crops = item.get('CROP') or []
    issues = item.get('ISSUE') or []
    if not isinstance(crops, list) or not isinstance(issues, list):
        return {'PAIRS_PROVEN': [], 'PAIRS_CARTESIAN_AVOIDED': 0,
                'STATE': 'CROP_ISSUE_PAIRING_NOT_PROVEN'}
    ev = item.get('ISSUE_EVIDENCE') or {}
    provados, testados = [], 0
    for iss in issues:
        trecho = norm(ev.get(iss, ''))
        for cr in crops:
            testados += 1
            termos = CROP_TERMOS.get(cr, (norm(cr),))
            if any(t in trecho for t in termos):
                provados.append({'CROP': cr, 'ISSUE': iss,
                                 'PROOF': 'termo da cultura dentro do trecho do problema',
                                 'PASSAGE': (ev.get(iss) or '')[:220]})
    # DURUM_WHEAT nao e rotulo do item; ele so aparece dentro do trecho
    extra = []
    for iss in issues:
        trecho = norm(ev.get(iss, ''))
        if any(t in trecho for t in CROP_TERMOS['DURUM_WHEAT']):
            extra.append({'CROP': 'DURUM_WHEAT', 'ISSUE': iss,
                          'PROOF': 'cultura NOMEADA dentro do trecho, ausente do rotulo do item',
                          'PASSAGE': (ev.get(iss) or '')[:220]})
    return {
        'PAIRS_PROVEN': provados + extra,
        'PAIRS_TESTED': testados,
        'PAIRS_CARTESIAN_AVOIDED': max(0, testados - len(provados)),
        'STATE': 'PAIRED' if (provados or extra) else 'CROP_ISSUE_PAIRING_NOT_PROVEN',
    }


# ══════════════════════════════════════════ 11 · LATENCIA
def latencia(item):
    p, c = item.get('PUBLISHED_AT'), item.get('CAPTURED_AT')
    def parse(x):
        m = re.match(r'(\d{4})-(\d{2})-(\d{2})', str(x))
        return date(int(m.group(1)), int(m.group(2)), int(m.group(3))) if m else None
    dp, dc = parse(p), parse(c)
    if not dp or not dc:
        return {'SOURCE_LATENCY_DAYS': None, 'STATE': 'NOT_MEASURABLE',
                'WHY': 'falta PUBLISHED_AT ou CAPTURED_AT'}
    return {'PUBLISHED_AT': str(dp), 'CAPTURED_AT': str(dc),
            'SOURCE_LATENCY_DAYS': (dc - dp).days,
            'AGE_OF_OBSERVATION_DAYS': (HOJE - dp).days,
            'STATE': 'MEASURED',
            'LEI': 'PIPELINE_LATENCY != AGE_OF_OBSERVATION'}


# ═══════════════════════════ 10 · FENOLOGIA NA OBSERVACAO, nao hoje
FENO_TERMOS = ('fenologia', 'fasi fenologiche', 'stadio', 'bbch', 'fenologic',
               'grappoli visibili', 'grappoli distesi', 'spigatura', 'fioritura',
               'floraison', 'stade')
TRIGGER_TERMOS = ('trattamento', 'intervento', 'si consiglia', 'soglia',
                  'traitement', 'protection', 'raccomanda', 'recettive al parassita')


def fenologia(item):
    """ACHADO DESTA PASSAGEM: o corpo completo NAO esta preservado.

    `DOCUMENT_TEXT_PRESERVED` e um INTEIRO — a contagem de caracteres que foram lidos,
    nao o texto. O que sobrevive no acervo e `DOCUMENT_EXCERPT` (3.000 caracteres) mais
    as passagens de CROP_EVIDENCE e ISSUE_EVIDENCE.

    Isso limita o reprocessamento autorizado: mede-se sobre o trecho, e o escopo sai
    declarado. Procurar termo num inteiro devolve zero em tudo — foi o que a primeira
    execucao desta passagem fez, e o zero parecia resultado.
    """
    partes = [item.get('DOCUMENT_EXCERPT') or '']
    for campo in ('CROP_EVIDENCE', 'ISSUE_EVIDENCE'):
        v = item.get(campo)
        if isinstance(v, dict):
            partes.extend(str(x) for x in v.values())
        elif v:
            partes.append(str(v))
    partes.append(str(item.get('OBSERVATION_TYPE_EVIDENCE') or ''))
    txt = norm(' '.join(partes))
    fe = [t for t in FENO_TERMOS if t in txt]
    tr = [t for t in TRIGGER_TERMOS if t in txt]
    corpo = item.get('DOCUMENT_TEXT_PRESERVED')
    return {
        'TEXT_SCOPE': 'DOCUMENT_EXCERPT + EVIDENCE_PASSAGES',
        'FULL_BODY_PRESERVED': isinstance(corpo, str),
        'DOCUMENT_CHARS_DECLARED': item.get('DOCUMENT_CHARS'),
        'EXCERPT_CHARS': len(item.get('DOCUMENT_EXCERPT') or ''),
        'CROP_STAGE_AT_OBSERVATION': 'PROVED' if fe else 'NOT_PROVED',
        'STAGE_TERMS_FOUND': fe[:5],
        'APPLICATION_TRIGGER_AT_OBSERVATION': 'PROVED' if tr else 'NOT_PROVED',
        'TRIGGER_TERMS_FOUND': tr[:5],
        'CURRENT_CROP_STAGE_TODAY': 'NOT_PROVED',
        'CURRENT_APPLICATION_WINDOW': 'NOT_PROVED',
        'LEI': 'OBSERVATION_STAGE != CURRENT_STAGE',
    }


# ══════════════════════════════════════════ 8/9 · reprocessar os 22 corpos
def reprocessar():
    terr = do_git(*PIN['TERRITORIAL'])
    saida = []
    for it in terr['ITEMS']:
        crops = it.get('CROP') if isinstance(it.get('CROP'), list) else []
        issues = it.get('ISSUE') if isinstance(it.get('ISSUE'), list) else []
        multi = len(crops) > 1 or len(issues) > 1
        saida.append({
            'ITEM_ID': it['ITEM_ID'],
            'SOURCE_ENTITY_ID': it.get('SOURCE_ENTITY_ID'),
            'SOURCE_URL': it.get('SOURCE_URL'),
            'COUNTRY': {'VALUE': it.get('COUNTRY_OF_FACT'),
                        'BASIS': it.get('COUNTRY_BASIS'),
                        'STATE': 'PROVED' if it.get('COUNTRY_OF_FACT') not in (None, 'NOT_KNOWN') else 'NOT_PROVED'},
            'REGION': {'VALUE': it.get('REGION_OF_FACT'),
                       'BASIS': it.get('LOCALITY_BASIS'),
                       'STATE': 'PROVED' if it.get('REGION_OF_FACT') not in (None, 'NOT_KNOWN') else 'NOT_PROVED'},
            'CROP': {'VALUE': crops, 'STATE': 'PROVED' if crops else 'NOT_PROVED'},
            'ISSUE': {'VALUE': issues, 'STATE': 'PROVED' if issues else 'NOT_PROVED'},
            'TIME': {'VALUE': it.get('PUBLISHED_AT'),
                     'STATE': 'PROVED' if str(it.get('PUBLISHED_AT', 'NOT_KNOWN'))[:4].isdigit() else 'NOT_PROVED'},
            'MULTI_BULLETIN_DOCUMENT': multi,
            'CROP_ISSUE_PAIRING': pareamento(it),
            'PHENOLOGY': fenologia(it),
            'LATENCY': latencia(it),
            'DOCUMENT_CHARS': it.get('DOCUMENT_CHARS'),
            'FULL_BODY_PRESERVED': isinstance(it.get('DOCUMENT_TEXT_PRESERVED'), str),
            'EXCERPT_CHARS': len(it.get('DOCUMENT_EXCERPT') or ''),
        })
    return terr, saida


def bloqueador(it):
    faltam = [k for k in ('COUNTRY', 'REGION', 'CROP', 'ISSUE', 'TIME')
              if it[k]['STATE'] != 'PROVED']
    if not faltam:
        if it['CROP_ISSUE_PAIRING']['STATE'] != 'PAIRED':
            return 'CROP_ISSUE_PAIRING_NOT_PROVEN'
        return None
    return 'FALTA: ' + ' + '.join(faltam)


# ═════════════════════════════════ 1 · RAIF · linhagem contra o territorial
def field_historical():
    r26 = do_disco(EM_ARVORE['RAIF_2026'])
    serie = do_disco(EM_ARVORE['RAIF_SERIE'])
    bt = do_disco(EM_ARVORE['BACKTEST'])
    terr, _ = reprocessar()
    fontes_terr = sorted(set(i.get('SOURCE_ENTITY_ID') for i in terr['ITEMS']))
    raif_no_territorial = [f for f in fontes_terr if 'RAIF' in str(f).upper()]
    return {
        'FIELD_HISTORICAL_SCOPE': 'IN',
        'FIELD_HISTORICAL_INPUT_COMMIT': 'in-tree @ %s' % BASE_REFRESH_COMMIT[:7],
        'ARTIFACTS': [EM_ARVORE['RAIF_2026'], EM_ARVORE['RAIF_SERIE'], EM_ARVORE['BACKTEST']],
        'COUNTRY': 'ES', 'CROP': 'OLIVE', 'ISSUE': 'REPILO',
        'REGION_SCOPE': 'Andalucia — %d provincias' % len(r26.get('provinces', {})),
        'SAMPLINGS_2026': r26.get('samplings_2026'),
        'LAST_OBSERVATION_SEASON': 2026,
        'CAPTURED_AT': r26.get('captured_at'),
        'HISTORICAL_BASELINE': {
            'SEASONS_IN_PRESERVED_SERIES': serie.get('seasons'),
            'READINGS_IN_PRESERVED_SERIES': serie.get('readings'),
            'METRIC': serie.get('metric'),
            'BASELINE_TYPE': serie.get('baseline_type'),
            'COHORT_CONTROL_PROVINCES': len(serie.get('cohort_control', {})),
            'DIVERGENCIA_DECLARADA':
                'o artefato de serie preservado declara %s safras e %s leituras; o '
                'backtest declara serie completa de 23 safras (2003-2026). As duas '
                'unidades sao diferentes e nao se escolhe a mais conveniente.'
                % (serie.get('seasons'), serie.get('readings')),
        },
        'LEAD_TIME_BACKTEST': {
            'RULE_DECLARED_BEFORE_LOOKING': bt.get('RULE_DECLARED_BEFORE_LOOKING'),
            'TOTAL_FIRES': bt.get('TOTAL_FIRES'),
            'LEAD_TIME': bt.get('LEAD_TIME'),
            'FALSE_POSITIVE_LOAD': bt.get('FALSE_POSITIVE_LOAD'),
            'HONEST_CONCLUSION': bt.get('HONEST_CONCLUSION'),
        },
        'INDEPENDENCE_FROM_TERRITORIAL_RAIF': {
            'TERRITORIAL_SOURCE_ENTITIES': fontes_terr,
            'RAIF_APPEARS_IN_TERRITORIAL': raif_no_territorial,
            'CLASSIFICATION': ('SOURCE_DEPENDENCY_ONLY' if raif_no_territorial
                               else 'INDEPENDENT_OBSERVATION'),
            'STATE': 'NOT_PROVED',
            'WHY': 'o territorial e o historico compartilham o publicador RAIF em pelo '
                   'menos um item. SAME_PUBLISHER nao prova INDEPENDENT_OBSERVATION, e '
                   'a linhagem parcela-a-parcela nao esta preservada. Nao se compra uma '
                   'segunda perna por inferencia.'
                   if raif_no_territorial else
                   'nenhum item territorial vem do RAIF nesta captura; ainda assim a '
                   'independencia parcela-a-parcela nao foi medida.',
        },
        'ADAMA_CONTEXT_DECLARED_IN_ARTIFACT': r26.get('adama_link'),
        'ADAMA_CONTEXT_LAW': 'declaracao em artefato NAO e '
                             'LOCAL_PRODUCT_AUTHORIZATION_PROVED, nem PRODUCT_FIT_PROVED, '
                             'nem APPLICATION_WINDOW_PROVED',
        'LOCAL_PRODUCT_AUTHORIZATION_PROVED': 'NOT_MEASURED',
        'FIELD_PRESSURE_LAW': 'FIELD_PRESSURE != DEMAND',
        'OBJECT_TYPE': 'LONGITUDINAL_FIELD_PRESSURE',
        'UNIT': 'COUNTRY x REGION x CROP x ISSUE x TIME',
    }


# ═══════════════════════════ 12 · REGULATORY_DEADLINE como objeto
def regulatory_deadlines():
    e = do_git(*PIN['IT_EXPIRIES'])
    prox = e.get('adama_next_expiries') or []
    por_data = {}
    for x in prox:
        d = x.get('expiry') or x.get('data_scadenza') or x.get('DATE') or 'NOT_KNOWN'
        por_data[str(d)] = por_data.get(str(d), 0) + 1
    return {
        'OBJECT_TYPE': 'REGULATORY_DEADLINE',
        'UNIT': 'COUNTRY x REGISTRATION x PRODUCT x DEADLINE',
        'COUNTRY': 'IT',
        'SOURCE_ID': e.get('SOURCE_ID'), 'DATASET_FILE': e.get('dataset_file'),
        'CAPTURED_AT': e.get('captured_at'),
        'PRODUCTS_TOTAL': e.get('products_total'),
        'IN_FORCE': e.get('in_force'),
        'WITH_FUTURE_EXPIRY': e.get('with_future_expiry'),
        'ADAMA_IN_FORCE_WITH_FUTURE_EXPIRY': e.get('adama_in_force_with_future_expiry'),
        'NEXT_EXPIRIES_LISTED': len(prox),
        'PRODUCTS_PER_EXPIRY_DATE': por_data,
        'STATUS_AS_DECLARED_BY_SOURCE': 'in_force / with_future_expiry, como a fonte declara',
        'LAWS': ['EXPIRY != WITHDRAWAL',
                 'EXPIRY_DATE_REACHED != PRODUCT_DISCONTINUED'],
        'PERMITTED_ACTION': 'REVIEW / CONFIRMATION BY REGULATORY',
        'FORBIDDEN_ACTION': 'ALERT: PRODUCT WILL DISAPPEAR',
        'NOT_A_DASHBOARD': 'entra como candidato de RADAR / ATTENTION QUEUE, nunca como '
                           'painel regulatorio',
    }


# ══════════════════════════ 7 · IDENTITY CHAIN (nao e convergencia de caso)
def identity_chain():
    fs = do_git(*PIN['FORESIGHT_3L'])
    prov = fs['PROVADAS']
    pais, emp = {}, {}
    for p in prov:
        pais[p['COUNTRY']] = pais.get(p['COUNTRY'], 0) + 1
        emp[p['META_COMPANY']] = emp.get(p['META_COMPANY'], 0) + 1
    return {
        'OBJECT_TYPE': 'IDENTITY_CHAIN_CONVERGENCE',
        'UNIT': 'COMPETITOR x COUNTRY x PRODUCT',
        'PROPOSITION': 'a mesma identidade de produto/titular e sustentada entre '
                       'trademark + registro local + Meta',
        'PROVED_TUPLES': fs['RESULTADO']['THREE_LAYER_CHAIN_PROVED_TUPLES'],
        'PROVED_PRODUCTS': fs['RESULTADO']['POR_UNIDADE_PRODUTO'][
            'META_PRODUCTS_WITH_PROVED_THREE_LAYER_CHAIN'],
        'CANDIDATE_TUPLES': fs['UNIVERSO']['THREE_LAYER_CANDIDATES_TOTAL'],
        'NOT_KNOWN_TUPLES': fs['RESULTADO']['THREE_LAYER_CHAIN_NOT_KNOWN_TUPLES'],
        'REJECTED_TUPLES': fs['RESULTADO']['THREE_LAYER_CHAIN_REJECTED_TUPLES'],
        'BY_COUNTRY': pais, 'BY_COMPANY': emp,
        'URBOLE_GUARD': fs['URBOLE_GUARD']['URBOLE_GUARD'],
        'IS_NOT': 'CASE_MULTI_SIGNAL_CONVERGENCE',
        'DOES_NOT_REQUIRE': ['CROP', 'ISSUE'],
        'DOES_NOT_PROVE': ['FIELD_PROBLEM', 'DEMAND', 'MARKET_MOVEMENT', 'SALES', 'SUCCESS'],
    }


# ═════════════════════════════ 17 · GRAFO V2 com dependencia TIPADA
TIPOS_DEP = ('SOURCE_DEPENDENCY', 'OBSERVATION_DEPENDENCY', 'ENTITY_DEPENDENCY',
             'DERIVATION_DEPENDENCY', 'SEMANTIC_DEPENDENCY', 'INDEPENDENT_SOURCE')

REL_V2 = [
    ('FORESIGHT_THREE_LAYER', 'META_PAID_ADS', 'DERIVATION_DEPENDENCY',
     'a perna META da cadeia E o anuncio da Meta, lido por git show sobre commit fixo'),
    ('FORESIGHT_THREE_LAYER', 'FORESIGHT_TRADEMARK_REGISTRATION_CROSSWALK',
     'DERIVATION_DEPENDENCY',
     'as duas primeiras pernas sao o proprio crosswalk marca<->registro'),
    ('FORESIGHT_REGISTRATION_LEG', 'NATIONAL_REGULATORY_REGISTRY', 'SOURCE_DEPENDENCY',
     'le ROPF (ES), Ministero (IT) e E-Phy (FR) — as mesmas bases do regulatorio'),
    ('LOCAL_ADAMA_PORTFOLIO', 'NATIONAL_REGULATORY_REGISTRY', 'SOURCE_DEPENDENCY',
     'o portfolio local provado sai do registro nacional'),
    ('REGULATORY_DEADLINE', 'NATIONAL_REGULATORY_REGISTRY', 'DERIVATION_DEPENDENCY',
     'o objeto de vencimento e derivado do mesmo registro nacional'),
    ('CREATOR_DEEP_CORPUS', 'CREATOR_MAP', 'ENTITY_DEPENDENCY',
     'o corpus le o conteudo das identidades que o mapa resolveu'),
    ('RESEARCHER_CORPUS', 'EXPERT_DIRECTORY', 'ENTITY_DEPENDENCY',
     'o corpus de pesquisador herda a identidade resolvida pelo diretorio'),
    ('SCIENCE_CORPUS', 'OPENALEX_INDEX', 'SOURCE_DEPENDENCY',
     'OpenAlex e infraestrutura de DESCOBERTA. SAME_INDEX != SAME_EVIDENCE: dois artigos '
     'achados pelo mesmo indice continuam sendo dois artigos'),
    ('TERRITORIAL_LISTING', 'TERRITORIAL_BODY', 'OBSERVATION_DEPENDENCY',
     'duas leituras do MESMO documento; a missao declara LISTING_ROLE = DISCOVERY_INDEX_ONLY'),
    ('META_SNAPSHOT_2', 'META_SNAPSHOT_1', 'OBSERVATION_DEPENDENCY',
     'as mesmas paginas, cerca de uma hora de distancia'),
    ('FIELD_HISTORICAL_RAIF', 'TERRITORIAL_RAIF', 'SOURCE_DEPENDENCY',
     'mesmo publicador RAIF; a linhagem parcela-a-parcela nao esta preservada. '
     'INDEPENDENCE = NOT_PROVED'),
    ('MULTI_BULLETIN_DOCUMENT', 'CROP_ISSUE_PAIRING', 'SEMANTIC_DEPENDENCY',
     'um documento com varios boletins nao autoriza produto cartesiano entre culturas e '
     'problemas: o par so fecha dentro da mesma passagem'),
    ('NATIONAL_REGISTRATION_FOR_PAIR', 'FIELD_OBSERVATION_OF_PAIR', 'SEMANTIC_DEPENDENCY',
     'registro autorizado para cultura x alvo oferece CONTEXTO DE PORTFOLIO. Nao confirma '
     'que o fenomeno de campo existe: SEMANTIC_MISMATCH_NOT_CORROBORATION'),
    ('COMPETITOR_PUBLIC_COMM', 'META_PAID_ADS', 'INDEPENDENT_SOURCE',
     'organica em canal proprio e paga na Biblioteca sao rotas diferentes — mas a primeira '
     'nao tem conteudo coletado, entao nao entra como sinal'),
    ('TERRITORIAL_BODY', 'NATIONAL_REGULATORY_REGISTRY', 'INDEPENDENT_SOURCE',
     'boletim regional e registro nacional sao publicadores e processos diferentes'),
    ('TERRITORIAL_BODY', 'SCIENCE_CORPUS', 'INDEPENDENT_SOURCE',
     'servico fitossanitario e publicacao indexada sao fontes independentes'),
    ('CREATOR_MAP', 'META_PAID_ADS', 'INDEPENDENT_SOURCE',
     'perfil publico de creator e anuncio pago de empresa sao fontes distintas'),
]


def grafo_v2():
    rel = [{'FROM': a, 'TO': b, 'DEPENDENCY_TYPE': t, 'WHY': w} for a, b, t, w in REL_V2]
    dep = [r for r in rel if r['DEPENDENCY_TYPE'] != 'INDEPENDENT_SOURCE']
    ind = [r for r in rel if r['DEPENDENCY_TYPE'] == 'INDEPENDENT_SOURCE']
    por_tipo = {}
    for r in rel:
        por_tipo[r['DEPENDENCY_TYPE']] = por_tipo.get(r['DEPENDENCY_TYPE'], 0) + 1
    familias = {
        'TERRITORIAL': True, 'SCIENCE_RESEARCHER': True, 'NATIONAL_REGISTRY': True,
        'TRADEMARK': True, 'META_PAID_ADS': True, 'CREATOR': True,
        'FIELD_HISTORICAL': True,           # entrou por decisao do coordenador
        'COMPETITOR_PUBLIC_COMM': False,    # identidade sem conteudo
    }
    return {
        'SOURCE_ID': 'REFRESH-CORRECTED/SIGNAL-DEPENDENCY-GRAPH-V2',
        'source': 'derivado dos handoffs congelados — nenhuma coleta, nenhuma rede',
        'SOURCE_LOCATION': 'derivado', 'FACT_LOCATION': 'n/a',
        'ARTIFACT_LANGUAGE': 'pt', 'EVIDENCE_CLASS': 'DERIVED_DEPENDENCY_ANALYSIS',
        'captured_at': '2026-08-31', 'CAPTURED_AT': '2026-08-31',
        'BASE_REFRESH_COMMIT': BASE_REFRESH_COMMIT,
        'DEPENDENCY_TYPES': list(TIPOS_DEP),
        'RELATIONS': rel,
        'RELATIONS_TOTAL': len(rel),
        'RELATIONS_DEPENDENT': len(dep),
        'RELATIONS_INDEPENDENT': len(ind),
        'RELATIONS_BY_TYPE': por_tipo,
        'SIGNAL_FAMILIES': familias,
        'FAMILIES_THAT_CAN_COUNT_TODAY': sorted(k for k, v in familias.items() if v),
        'FAMILIES_THAT_CANNOT_COUNT_TODAY': sorted(k for k, v in familias.items() if not v),
        'LAWS': [
            '2 cards != 2 independent signals',
            'SAME_INDEX != SAME_EVIDENCE',
            'SAME_PUBLISHER != INDEPENDENT_OBSERVATION',
            'SEMANTIC_MISMATCH_NOT_CORROBORATION',
            'CONVERGENCE_REQUIRES = SAME_PROPOSITION + INDEPENDENT_EVIDENCE',
        ],
        'CONVERGENCE_KINDS': {
            'PHENOMENON_CONVERGENCE': 'duas familias independentes afirmam O MESMO fenomeno',
            'IDENTITY_CONVERGENCE': 'duas fontes sustentam a mesma IDENTIDADE (marca, '
                                    'titular, produto)',
            'CONTEXTUAL_ALIGNMENT': 'uma fonte oferece contexto para a outra sem afirmar '
                                    'a mesma proposicao',
            'NUNCA_SOMAR': 'os tres tipos nunca entram no mesmo numero',
        },
    }
