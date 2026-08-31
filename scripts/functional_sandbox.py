# -*- coding: utf-8 -*-
"""FUNCTIONAL_SANDBOX — PROTOTYPE_ONLY. Nao e o casco, nao e V8, nao e ferramenta.

Coloca as capacidades novas na dinamica que o casco V7 ja define para um caso:

    CASE -> CAMADAS -> CONVERGENCIAS -> CRUZAMENTOS -> TEMPO -> MAPA DE ACAO

DELTA 2026-08-30. A versao anterior usava UM booleano por camada — "acendeu" ou nao. Isso
escondia a diferenca entre *nao ha entidade*, *ha entidade mas a chave do caso nao bate*,
*a chave bate mas o problema nao*, *falta conteudo* e *falta handoff canonico*. Sao cinco
perguntas diferentes e cada uma manda numa decisao diferente. Agora cada camada responde
as cinco separadamente.

Nao escreve em banco, nao le rede, nao toca no casco, nao publica ferramenta.

    py scripts/functional_sandbox.py
    py scripts/functional_sandbox.py --json
    py scripts/functional_sandbox.py --medicao
"""
import json
import os
import sys

# O console do Windows abre em cp1252 e alguns nomes reais trazem hifen tipografico
# (U+2010) — "Mercado‐Blanco" derruba o print. O dado esta certo; e a saida que precisa
# aguentar. Nunca trocar o dado para caber no terminal.
try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
except AttributeError:  # pragma: no cover
    pass

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import functional_prep as fp  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FIX = os.path.join(ROOT, 'data', 'functional-sandbox', 'fixtures')

CAMADAS_DO_CASCO = ('Campo', 'Ciencia', 'Clima', 'Regulatorio',
                    'Portfolio local ADAMA', 'Competicao', 'Tempo')

# Os cinco estados. Nunca um booleano.
ESTADOS = ('PROVED', 'PARTIAL', 'NOT_PROVED', 'NOT_READY', 'NOT_APPLICABLE')

RECORTES = (
    {'CASE_ID': 'ES-OLIVE-REPILO', 'COUNTRY': 'ES', 'CROP': 'OLIVE', 'ISSUE': 'REPILO',
     'ISSUE_TERMS': ('repilo', 'venturia oleaginea', 'spilocaea oleagina',
                     'fusicladium oleagineum', 'peacock spot', 'olive scab')},
    {'CASE_ID': 'IT-VINE-FLAVESCENCE', 'COUNTRY': 'IT', 'CROP': 'GRAPEVINE', 'ISSUE': 'FLAVESCENCE',
     'ISSUE_TERMS': ('flavescence', 'flavescencia', 'scaphoideus', 'grapevine yellows')},
    {'CASE_ID': 'FR-CEREAL-SEPTORIA', 'COUNTRY': 'FR', 'CROP': 'CEREALS', 'ISSUE': 'SEPTORIA',
     'ISSUE_TERMS': ('septoria', 'zymoseptoria', 'mycosphaerella graminicola')},
)


def _carregar_tudo():
    j = os.path.join
    return {
        'creators': fp.adaptar_creator_capability(
            fp.carregar(j(FIX, 'creator-capability-sample.json'))),
        'contas': fp.adaptar_public_comm(
            fp.carregar(j(FIX, 'public-comm-batch-sample.json'))),
        'experts': fp.adaptar_expert_directory(
            fp.carregar(j(ROOT, 'data', 'samples', 'SPEAKER-UNIVERSE-PILOT-V1.json'))),
        'corpus_ciencia': fp.carregar(j(FIX, 'science-corpus-targets-sample.json')),
        'deep': fp.adaptar_creator_deep_corpus(
            fp.carregar(j(FIX, 'creator-deep-corpus-sample.json'))),
        'fs_cross': fp.adaptar_foresight_crosswalk(
            fp.carregar(j(FIX, 'foresight-crosswalk-sample.json'))),
        'fs_3l': fp.adaptar_foresight_three_layer(
            fp.carregar(j(FIX, 'foresight-three-layer-sample.json'))),
    }


def _crops(o):
    cp = o['FIELDS'].get('CROP_PROOF') or {}
    return set(cp.get('CROPS') or [])


def camada(nome, estado, evidencia, **extra):
    if estado not in ESTADOS:
        raise ValueError('estado desconhecido: %r' % (estado,))
    d = {'LAYER': nome, 'STATE': estado, 'EVIDENCE': evidencia}
    d.update(extra)
    return d


def montar(rec, dados):
    pais, cultura, issue = rec['COUNTRY'], rec['CROP'], rec['ISSUE']

    # ---------------------------------------------------------- CREATOR
    do_pais = [o for o in dados['creators'] if o['COUNTRY'] == pais]
    da_cultura = [o for o in do_pais if cultura in _crops(o)]
    prontos = [o for o in da_cultura
               if o['FIELDS'].get('ACTIVATION_STATE') == 'ACTIVATION_READY']
    pessoas = [o for o in prontos if o['ANALYTICAL_UNIT'] == 'PERSON']
    empresas = [o for o in prontos if o['ANALYTICAL_UNIT'] == 'FARM_BUSINESS_ENTITY']

    # a chave que produziu o numero — auditada e declarada
    creator_route = camada(
        'CREATOR_ACTIVATION_ROUTE',
        'PROVED' if prontos else 'NOT_PROVED',
        'casamento por COUNTRY + CROP, e SO por isso',
        MATCH_KEY='COUNTRY + CROP',
        ENTITY_AVAILABLE=len(do_pais),
        CASE_KEY_MATCH_PROVED=len(da_cultura),
        CASE_ISSUE_MATCH_PROVED=0,
        CONTENT_AVAILABLE=None,
        CANONICAL_HANDOFF_AVAILABLE='YES',
        PERSON_CREATOR_ACTIVATION_READY=len(pessoas),
        FARM_BUSINESS_PARTNER_READY=len(empresas),
        NAMES=[o['FIELDS']['DISPLAY_NAME'] for o in prontos],
        NUNCA_SOMAR='pessoa != empresa; a soma nao se chama CREATORS_READY')

    # ISSUE do creator: so o conteudo do deep corpus poderia sustentar
    deep_pais = [o for o in dados['deep'] if o['COUNTRY'] == pais]
    com_rota = [o for o in deep_pais if o['FIELDS']['CONTENT_ROUTE'] == 'PROVED']
    issues_obs = {}
    for o in com_rota:
        for k, v in (o['FIELDS']['ISSUES_OBSERVED_IN_CONTENT'] or {}).items():
            issues_obs[k] = issues_obs.get(k, 0) + v
    creator_issue = camada(
        'CREATOR_ISSUE_RELEVANCE',
        'NOT_PROVED',
        ('o corpus profundo classifica problema por LINHA (%s), nunca por problema '
         'nomeado como %s' % (', '.join(sorted(issues_obs)) or 'nenhuma', issue)),
        ENTITY_AVAILABLE=len(deep_pais),
        CONTENT_AVAILABLE=sum(o['FIELDS']['N_CONTENT_ITEMS_REVIEWED'] for o in deep_pais),
        CONTENT_ROUTES_PROVED=len(com_rota),
        CASE_ISSUE_MATCH_PROVED=0,
        ISSUE_CLASSES_OBSERVED=issues_obs,
        CANONICAL_HANDOFF_AVAILABLE='YES',
        LEI='CROP_EXPERTISE != CROP_X_ISSUE_EXPERTISE')

    # ---------------------------------------------------------- EXPERT
    do_caso = [o for o in dados['experts'] if o['FIELDS'].get('CASE_ID') == rec['CASE_ID']]
    provas = [fp.expertise_no_caso(o, dados['corpus_ciencia'], cultura, issue,
                                   rec['ISSUE_TERMS']) for o in do_caso]
    com_issue = [p for p in provas if p['ISSUE_EXPERTISE'] == 'PROVED']
    mensuraveis = [p for p in provas if p['ISSUE_EXPERTISE'] != 'NOT_MEASURABLE']

    expert_avail = camada(
        'EXPERT_DIRECTORY_AVAILABILITY',
        'PROVED' if do_caso else 'NOT_PROVED',
        '%d pessoa(s) com identidade provada e ORCID resolvido, amarradas por CASE_ID'
        % len(do_caso),
        ENTITY_AVAILABLE=len(do_caso),
        CASE_KEY_MATCH_PROVED=len(do_caso),
        CANONICAL_HANDOFF_AVAILABLE='YES',
        NAMES=[o['FIELDS']['NAME'] for o in do_caso])

    if not do_caso:
        est = 'NOT_PROVED'
        ev = 'nenhuma pessoa amarrada a este caso'
    elif com_issue:
        est = 'PROVED'
        ev = '%d de %d com o problema no titulo de um trabalho' % (len(com_issue), len(do_caso))
    elif not mensuraveis:
        est = 'NOT_READY'
        ev = ('nenhum trabalho destas pessoas no corpus disponivel — o corpus e espanhol '
              '(institutions.country_code:es). Ausencia aqui NAO e ausencia de obra')
    else:
        est = 'NOT_PROVED'
        ev = ('nenhum trabalho com o problema no titulo. O campo ISSUE do corpus vem da '
              'CONSULTA que trouxe o documento, nao de leitura — herdar da consulta nao '
              'e expertise')
    expert_case = camada(
        'EXPERT_CASE_EXPERTISE', est, ev,
        COUNTRY_MATCH='PROVED' if do_caso else 'NOT_KNOWN',
        CASE_ISSUE_MATCH_PROVED=len(com_issue),
        PER_PERSON=provas,
        LEI='IDENTITY_PROVED != ISSUE_EXPERTISE_PROVED')

    # ------------------------------------------- COMPETITOR PUBLIC COMM
    contas = [o for o in dados['contas'] if o['COUNTRY'] == pais]
    comp_comm = camada(
        'COMPETITOR_PUBLIC_COMM_ACCOUNTS',
        'PARTIAL' if contas else 'NOT_PROVED',
        'identidade congelada; conteudo NAO coletado',
        ENTITY_AVAILABLE=len(contas),
        COMPANIES=sorted(set(o['FIELDS']['COMPANY'] for o in contas)),
        CASE_KEY_MATCH_PROVED=len(contas),
        CASE_ISSUE_MATCH_PROVED=0,
        CONTENT_AVAILABLE=0,
        CONTENT_COLLECTION_STAGE='NOT_STARTED',
        CANONICAL_HANDOFF_AVAILABLE='NO',
        ZERO_SIGNIFICA='NO_CONTENT_COLLECTION_EXECUTED, nunca COMPANY_NOT_COMMUNICATING')

    # ---------------------------------------------------------- FORESIGHT
    fs_pais = [o for o in dados['fs_cross'] if o['COUNTRY'] == pais]
    fs3_pais = [o for o in dados['fs_3l'] if o['COUNTRY'] == pais]
    foresight = camada(
        'FORESIGHT_PROVISIONAL',
        'PARTIAL' if (fs_pais or fs3_pais) else 'NOT_APPLICABLE',
        ('crosswalk marca<->registro disponivel; CROP e ISSUE ausentes nos tres registros '
         'nacionais, entao a camada nao entra no eixo cultura x praga'),
        ENTITY_AVAILABLE=len(fs_pais),
        THREE_LAYER_TUPLES=len(fs3_pais),
        CASE_KEY_MATCH_PROVED=len(fs_pais),
        CASE_ISSUE_MATCH_PROVED=0,
        CANONICAL_HANDOFF_AVAILABLE='YES',
        FREEZE='ACCEPTED',
        SOURCE_COMMIT=fp.FORESIGHT_FREEZE['FORESIGHT_SOURCE_COMMIT'],
        URBOLE_GUARD='PASS')

    meta = camada(
        'META_PROVISIONAL', 'NOT_READY',
        ('a branch da Meta nao esta publicada em origin (13 heads, nenhuma "meta"). Os '
         'numeros chegam em SEGUNDA MAO pela auditoria do Foresight'),
        ENTITY_AVAILABLE=len(fs3_pais),
        META_LEG='NOT_VERIFIABLE_FROM_ORIGIN',
        CANONICAL_HANDOFF_AVAILABLE='NO',
        CASE_ISSUE_MATCH_PROVED=0)

    territorial = camada(
        'TERRITORIAL_PROVISIONAL', 'NOT_READY',
        'missao em voo; medicao intermediaria apenas, com commit declarado',
        CANONICAL_HANDOFF_AVAILABLE='NO',
        SNAPSHOT='841fb54 · data/samples/TERRITORIAL/MEDICAO.json',
        MEASUREMENT_STATE='PROVISIONAL_MEASUREMENT')

    camadas_casco = dict((c, 'NAO MEDIDO') for c in CAMADAS_DO_CASCO)
    camadas_casco['Ciencia'] = ('PARCIAL — %d identidade(s); expertise no problema %s'
                                % (len(do_caso), est))
    if contas:
        camadas_casco['Competicao'] = ('PARCIAL — %d conta(s) local(is); %d par(es) '
                                       'marca<->registro; conteudo NAO coletado'
                                       % (len(contas), len(fs_pais)))
    camadas_casco['Tempo'] = 'NAO CONECTADO'

    return {
        'CASE_ID': rec['CASE_ID'], 'COUNTRY': pais, 'CROP': cultura, 'ISSUE': issue,
        'CAMADAS_DO_CASCO': camadas_casco,
        'CAMADAS': [creator_route, creator_issue, expert_avail, expert_case,
                    comp_comm, foresight, meta, territorial],
        'TEMPO': {'JANELA_AGRONOMICA': 'NAO CONECTADA',
                  'JANELA_DE_DECISAO': 'NAO DETERMINADA'},
        'WIRED_TO_CASCO': False, 'MODE': 'PROTOTYPE_ONLY',
    }


def rodar():
    d = _carregar_tudo()
    return {
        'SANDBOX': 'FUNCTIONAL_SANDBOX', 'MODE': 'PROTOTYPE_ONLY',
        'CASCO_V7_MODIFIED': False, 'REAL_DATA_WIRED': False,
        'SCOPE_NOTE': 'OBSERVED_IN_3_TEST_CASES — nunca EAME_COVERAGE_RATE. Tres recortes '
                      'escolhidos nao sao amostra de nada.',
        'TOTAIS': {
            'CREATOR_OBJECTS': fp.contar(d['creators']),
            'CREATOR_CONTENT_PROFILES': fp.contar(d['deep']),
            'PUBLIC_COMM_OBJECTS': fp.contar(d['contas']),
            'EXPERT_OBJECTS': fp.contar(d['experts']),
            'FORESIGHT_LINKS': fp.contar(d['fs_cross']),
            'FORESIGHT_THREE_LAYER': fp.contar(d['fs_3l']),
        },
        'RECORTES': [montar(r, d) for r in RECORTES],
    }


def medicao():
    """Artefato de medicao DERIVADO — nenhum numero e digitado a mao."""
    s = rodar()
    d = _carregar_tudo()
    cap = fp.carregar(os.path.join(FIX, 'creator-capability-sample.json'))
    linhas_ar = cap['LOOKUP_BY_ACTIVATION_STATE']['ACTIVATION_READY']
    deep = d['deep']
    com_rota = [o for o in deep if o['FIELDS']['CONTENT_ROUTE'] == 'PROVED']
    sem_rota = [o for o in deep if o['FIELDS']['CONTENT_ROUTE'] != 'PROVED']
    com_issue = [o for o in deep if o['FIELDS']['ISSUES_OBSERVED_IN_CONTENT']]

    def por_camada(nome):
        out = {}
        for r in s['RECORTES']:
            for c in r['CAMADAS']:
                if c['LAYER'] == nome:
                    out[r['CASE_ID']] = c['STATE']
        return out

    return {
        'SOURCE_ID': 'FUNCTIONAL-SANDBOX/PREP-MEDICAO',
        'source': 'derivado dos adaptadores sobre fixtures reais — nenhuma coleta, custo zero',
        'SOURCE_LOCATION': 'derivado',
        'FACT_LOCATION': 'n/a — descreve o acervo, nao o mundo',
        'ORIGINAL_LANGUAGE': 'pt',
        'EVIDENCE_CLASS': 'DERIVED_MEASUREMENT',
        'captured_at': '2026-08-30', 'CAPTURED_AT': '2026-08-30',
        'DELTA_REFRESH': '2026-08-30 — Foresight aceito, Deep Corpus congelado, expertise '
                         'por ISSUE medida contra o corpus cientifico',
        'MODE': 'PROTOTYPE_ONLY',
        'CASCO_V7_MODIFIED': False, 'REAL_DATA_WIRED': False,
        'PRODUCT_IMPLEMENTATION_MODE': 'NOT_ENTERED',
        'FINAL_REFRESH_EXECUTED': 'NO',
        'MANDATORY_HANDOFFS_ACCEPTED': '2/4',
        'COMO_REPRODUZIR': 'py scripts/functional_sandbox.py --medicao',
        'SCOPE_NOTE': s['SCOPE_NOTE'],
        'OBJETOS_POR_CAPACIDADE': s['TOTAIS'],
        'CARDINALIDADE_PERIGOSA': {
            'ONDE': 'CREATOR_CAPABILITY.LOOKUP_BY_ACTIVATION_STATE.ACTIVATION_READY',
            'LINHAS': len(linhas_ar),
            'ENTIDADES': len(set(x['HANDLE'] for x in linhas_ar)),
            'FATOR_DE_INFLACAO': round(len(linhas_ar) / float(len(set(x['HANDLE'] for x in linhas_ar))), 2),
            'LEI': 'ROW != ENTITY',
        },
        'CONTA_NAO_E_EMPRESA': {
            'CONTAS_LOCAIS': len(d['contas']),
            'EMPRESAS_DISTINTAS': len(set(o['FIELDS']['COMPANY'] for o in d['contas'])),
            'LEI': 'COMPANY_LOCAL_ACCOUNT != COMPANY',
        },
        'CREATOR_DEEP_CORPUS': {
            'TARGETS': len(deep),
            'CONTENT_ROUTES_PROVED': len(com_rota),
            'CONTENT_ROUTES_NOT_PROVED': len(sem_rota),
            'SEM_ROTA_QUEM': [o['FIELDS']['NAME'] for o in sem_rota],
            'FICHAS_COM_ISSUE_NO_CONTEUDO': len(com_issue),
            'ISSUE_E_CLASSE_DE_LINHA': 'WEED / PEST / DISEASE — nunca problema nomeado',
            'LEI': 'IDENTIDADE (Creator Map) != CONTEUDO (Deep Corpus)',
        },
        'EXPERTISE_POR_CASO': por_camada('EXPERT_CASE_EXPERTISE'),
        'CREATOR_ISSUE_POR_CASO': por_camada('CREATOR_ISSUE_RELEVANCE'),
        'CREATOR_ROTA_POR_CASO': por_camada('CREATOR_ACTIVATION_ROUTE'),
        'AFIRMACOES_RETIRADAS': {
            'EXPERT_3_OF_3': 'RETIRADA — media identidade, nao expertise no problema',
            'CREATOR_2_OF_3_VAZIOS': 'REFORMULADA — o numero era rota de ativacao por '
                                     'COUNTRY+CROP, nunca relevancia no problema',
        },
        'RECORTES': s['RECORTES'],
    }


def main():
    if '--medicao' in sys.argv:
        destino = os.path.join(ROOT, 'data', 'functional-sandbox', 'PREP-MEDICAO.json')
        with open(destino, 'w', encoding='utf-8', newline='\n') as f:
            json.dump(medicao(), f, ensure_ascii=False, indent=1)
            f.write('\n')
        print('gravado %s' % destino)
        return 0
    saida = rodar()
    if '--json' in sys.argv:
        print(json.dumps(saida, ensure_ascii=False, indent=1))
        return 0
    print('FUNCTIONAL_SANDBOX — PROTOTYPE_ONLY · casco nao tocado, nada ligado')
    print(saida['SCOPE_NOTE'] + '\n')
    for k, v in saida['TOTAIS'].items():
        print('  %-26s linhas=%-4d entidades=%-4d' % (k, v['ROWS'], v['ENTITIES']))
    for r in saida['RECORTES']:
        print('\n' + '=' * 78)
        print('%s   %s x %s x %s' % (r['CASE_ID'], r['COUNTRY'], r['CROP'], r['ISSUE']))
        print('  %-34s %-12s %s' % ('CAMADA', 'ESTADO', 'EVIDENCIA'))
        for c in r['CAMADAS']:
            print('  %-34s %-12s %s' % (c['LAYER'], c['STATE'], c['EVIDENCE'][:74]))
    print('\nMANDATORY_HANDOFFS_ACCEPTED = 2/4 · PRODUCT_IMPLEMENTATION_MODE = NOT_ENTERED')
    return 0


if __name__ == '__main__':
    sys.exit(main())
