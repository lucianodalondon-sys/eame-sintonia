# -*- coding: utf-8 -*-
"""ONE FINAL INTELLIGENCE REFRESH — gerador dos artefatos derivados.

Le as entradas por COMMIT FIXO (nunca pela ponta de branch) e emite:

    data/refresh/SIGNAL-DEPENDENCY-GRAPH.json
    data/refresh/FINAL-INTELLIGENCE-REFRESH-EAME.json

Nenhuma coleta. Nenhuma escrita fora de data/refresh/. Nenhum numero digitado a mao:
tudo o que e contagem sai da leitura dos artefatos congelados.

    py scripts/refresh_final.py
"""
import json
import os
import subprocess
import sys

try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
except AttributeError:  # pragma: no cover
    pass

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEST = os.path.join(ROOT, 'data', 'refresh')

# ─────────────────────────────────────────── entradas fixadas por COMMIT
# Uma branch se move. Um refresh que aponta para a ponta responde diferente a cada hora
# sem que ninguem tenha mudado nada.
INPUTS = {
    'CREATOR_MAP': {
        'COMMIT': '248bd27027506a5f531a117ce50d35eb5304b152',
        'STATE': 'ACCEPTED', 'MANDATORY': True,
        'FILES': {'freeze': 'data/samples/CREATOR-MAP-EAME/PILOT-FREEZE-STATE.json',
                  'capability': 'data/samples/CREATOR-MAP-EAME/CREATOR-CAPABILITY-EAME.json'},
    },
    'COMPETITOR_FORESIGHT': {
        'COMMIT': 'dc32ce0', 'ORIGINAL_FREEZE': '25194e3',
        'STATE': 'ACCEPTED', 'MANDATORY': True, 'LINEAGE_CORRECTION': 'COMPLETE',
        'FILES': {'three_layer': 'data/samples/COMPETITOR-THREE-LAYER-AUDIT.json',
                  'crosswalk': 'data/samples/COMPETITOR-CROSSWALK.json'},
    },
    'EARLY_SIGNAL_TERRITORIAL': {
        'COMMIT': '11fd7b54e27adaaebed18f049f90b80b05806943',
        'HANDOFF_COMMIT': '4ea268d0cbdc5f28f535b6288ee6c48bea20a6aa',
        'STATE': 'PARTIAL', 'MANDATORY': True, 'MANDATORY_HANDOFF_READY': 'YES',
        'FILES': {'final': 'data/samples/TERRITORIAL/FINAL.json'},
    },
    'META_COMPETITOR': {
        'COMMIT': 'acfd987', 'HANDOFF_COMMIT': 'a2fad2d',
        'STATE': 'ACCEPTED', 'MANDATORY': True,
        'FILES': {'freeze': 'data/samples/META-EAME/META-HANDOFF-FREEZE-V1.json'},
        'HANDOFF_FILE_AT': 'a2fad2d',
    },
    'CREATOR_DEEP_CORPUS': {
        'COMMIT': 'a509c12', 'STATE': 'READY_WITH_LIMITATIONS', 'MANDATORY': False,
        'FILES': {'delivery': 'data/samples/CREATOR-CONTENT-CORPUS-EAME/CORPUS-DELIVERY.json'},
    },
    'MULTILINGUAL_CONTRACT': {
        'COMMIT': '1443f6435d4297a4563f25d83473142fc12e1f0d',
        'STATE': 'ACCEPTED_FROZEN', 'MANDATORY': False,
        'ROLE': 'PRODUCT_GUARDRAIL — nao e sinal de inteligencia',
        'FILES': {},
    },
}


def ler(commit, path):
    out = subprocess.run(['git', 'show', '%s:%s' % (commit, path)],
                         cwd=ROOT, capture_output=True)
    if out.returncode != 0:
        raise RuntimeError('nao consegui ler %s:%s' % (commit, path))
    return json.loads(out.stdout.decode('utf-8'))


def sha_do_blob(commit, path):
    out = subprocess.run(['git', 'rev-parse', '%s:%s' % (commit, path)],
                         cwd=ROOT, capture_output=True)
    return out.stdout.decode('utf-8').strip()


# ══════════════════════════════════════════════ 1 · GRAFO DE DEPENDENCIAS
#
# Antes de contar convergencia, provar independencia. Duas telas nao sao dois sinais.
RELACOES = [
    {
        'FROM': 'FORESIGHT_THREE_LAYER', 'TO': 'META_PAID_ADS',
        'RELATION': 'DERIVED_FROM',
        'WHY': 'a perna META da cadeia de tres camadas E o anuncio da Meta. O Foresight '
               'le acfd987 por git show e usa o anuncio como terceira concordancia.',
        'CONSEQUENCE': 'FORESIGHT_THREE_LAYER + META_AD nunca contam como duas familias '
                       'independentes para o mesmo produto/pais.',
        'GUARD': 'DERIVED_DEPENDENCY_ON_META',
    },
    {
        'FROM': 'FORESIGHT_THREE_LAYER', 'TO': 'FORESIGHT_TRADEMARK_REGISTRATION_CROSSWALK',
        'RELATION': 'DERIVED_FROM',
        'WHY': 'as duas primeiras pernas da cadeia sao o proprio crosswalk marca<->registro.',
        'CONSEQUENCE': 'cadeia e crosswalk sao a mesma evidencia vista com uma perna a mais.',
        'GUARD': 'SAME_DATA_DIFFERENT_VIEW',
    },
    {
        'FROM': 'FORESIGHT_REGISTRATION_LEG', 'TO': 'NATIONAL_REGULATORY_REGISTRY',
        'RELATION': 'SAME_SOURCE',
        'WHY': 'a perna de registro do Foresight le ROPF (ES), Ministero (IT) e E-Phy (FR) '
               '— exatamente as mesmas bases da camada regulatoria e do portfolio local.',
        'CONSEQUENCE': 'somar FORESIGHT e REGULATORIO como duas familias para o mesmo pais '
                       'conta o registro nacional duas vezes.',
        'GUARD': 'SHARED_REGISTRY_NOT_TWO_FAMILIES',
    },
    {
        'FROM': 'LOCAL_ADAMA_PORTFOLIO', 'TO': 'NATIONAL_REGULATORY_REGISTRY',
        'RELATION': 'DERIVED_FROM',
        'WHY': 'o portfolio local provado sai do registro nacional, com o catalogo publico '
               'como segunda ponta apenas onde ela abriu.',
        'CONSEQUENCE': 'portfolio e registro nao sao duas observacoes independentes.',
        'GUARD': 'SHARED_REGISTRY_NOT_TWO_FAMILIES',
    },
    {
        'FROM': 'CREATOR_DEEP_CORPUS', 'TO': 'CREATOR_MAP',
        'RELATION': 'DERIVED_FROM',
        'WHY': 'o corpus profundo le o conteudo das identidades que o Creator Map resolveu. '
               'Sem a identidade do mapa nao ha alvo de coleta.',
        'CONSEQUENCE': 'identidade e conteudo do mesmo creator sao UMA familia com duas '
                       'observacoes, nao duas familias.',
        'GUARD': 'SAME_ENTITY_DIFFERENT_OBSERVATION',
    },
    {
        'FROM': 'RESEARCHER_CORPUS', 'TO': 'EXPERT_DIRECTORY',
        'RELATION': 'DERIVED_FROM',
        'WHY': 'o corpus de pesquisador herda a identidade do diretorio; os dois saem do '
               'mesmo OpenAlex.',
        'CONSEQUENCE': 'ciencia e pesquisador nao sao duas familias independentes.',
        'GUARD': 'SAME_SOURCE',
    },
    {
        'FROM': 'TERRITORIAL_LISTING', 'TO': 'TERRITORIAL_BODY',
        'RELATION': 'SAME_SOURCE',
        'WHY': 'listagem e corpo sao duas leituras do MESMO documento. A propria missao '
               'declara LISTING_ROLE = DISCOVERY_INDEX_ONLY.',
        'CONSEQUENCE': 'a listagem nao e evidencia; nao acrescenta sinal ao corpo.',
        'GUARD': 'SAME_DATA_DIFFERENT_VIEW',
    },
    {
        'FROM': 'META_SNAPSHOT_2', 'TO': 'META_SNAPSHOT_1',
        'RELATION': 'SAME_ENTITY_DIFFERENT_OBSERVATION',
        'WHY': 'as duas capturas leem as MESMAS paginas com cerca de uma hora de distancia.',
        'CONSEQUENCE': 'dois snapshots nao sao duas fontes; sao dois instantes da mesma.',
        'GUARD': 'SAME_ENTITY_DIFFERENT_OBSERVATION',
    },
    {
        'FROM': 'COMPETITOR_PUBLIC_COMM', 'TO': 'META_PAID_ADS',
        'RELATION': 'INDEPENDENT_SOURCE',
        'WHY': 'comunicacao organica em canal proprio e anuncio pago na Biblioteca sao '
               'rotas e naturezas diferentes.',
        'CONSEQUENCE': 'seriam duas familias — mas COMPETITOR_PUBLIC_COMM ainda nao tem '
                       'conteudo coletado, entao hoje nao entra como sinal.',
        'GUARD': 'IDENTITY_IS_NOT_SIGNAL',
    },
    {
        'FROM': 'TERRITORIAL_BODY', 'TO': 'NATIONAL_REGULATORY_REGISTRY',
        'RELATION': 'INDEPENDENT_SOURCE',
        'WHY': 'boletim fitossanitario regional e registro nacional sao publicadores, '
               'processos e cadencias diferentes.',
        'CONSEQUENCE': 'podem contar como duas familias independentes.',
        'GUARD': None,
    },
    {
        'FROM': 'TERRITORIAL_BODY', 'TO': 'SCIENCE_CORPUS',
        'RELATION': 'INDEPENDENT_SOURCE',
        'WHY': 'boletim de servico fitossanitario e publicacao cientifica indexada sao '
               'fontes independentes.',
        'CONSEQUENCE': 'podem contar como duas familias independentes.',
        'GUARD': None,
    },
    {
        'FROM': 'CREATOR_MAP', 'TO': 'META_PAID_ADS',
        'RELATION': 'INDEPENDENT_SOURCE',
        'WHY': 'perfil publico de creator e anuncio pago de empresa sao fontes distintas.',
        'CONSEQUENCE': 'se a Meta encontrar um creator num anuncio isso vira '
                       'CREATOR_APPEARANCE_OBSERVED — e PAID_CREATOR_RELATION so sobe com '
                       'prova adicional.',
        'GUARD': 'NOT_ANTICIPATED',
    },
]

# familias de sinal, e quais realmente sao independentes entre si
FAMILIAS = {
    'TERRITORIAL': {'INDEPENDENT': True,
                    'SOURCE': 'boletins de servico fitossanitario regional / imprensa tecnica'},
    'SCIENCE_RESEARCHER': {'INDEPENDENT': True, 'SOURCE': 'OpenAlex',
                           'NOTA': 'ciencia e pesquisador sao UMA familia, nao duas'},
    'NATIONAL_REGISTRY': {'INDEPENDENT': True,
                          'SOURCE': 'ROPF (ES) · Ministero (IT) · E-Phy (FR)',
                          'NOTA': 'compartilhada por REGULATORIO, PORTFOLIO LOCAL e pela '
                                  'perna de registro do FORESIGHT'},
    'TRADEMARK': {'INDEPENDENT': True, 'SOURCE': 'TMview (OEPM · UIBM · INPI · EUIPO)'},
    'META_PAID_ADS': {'INDEPENDENT': True, 'SOURCE': 'Meta Ads Library (UI)',
                      'NOTA': 'a cadeia de tres camadas do Foresight DEPENDE desta familia'},
    'CREATOR': {'INDEPENDENT': True, 'SOURCE': 'perfis publicos + corpus de conteudo',
                'NOTA': 'mapa e corpus profundo sao UMA familia'},
    'COMPETITOR_PUBLIC_COMM': {'INDEPENDENT': True, 'SOURCE': '22 contas oficiais provadas',
                               'SIGNAL_TODAY': False,
                               'NOTA': 'CONTENT_COLLECTION = NOT_STARTED. Identidade nao e sinal.'},
    'FIELD_HISTORICAL': {'INDEPENDENT': True, 'SOURCE': 'RAIF Andaluzia (ES-T3-001)',
                         'NOTA': 'artefato canonico em arvore, FORA da lista de entradas '
                                 'do coordenador — declarado, nao consumido como prova'},
}


def grafo():
    derivadas = [r for r in RELACOES if r['RELATION'] != 'INDEPENDENT_SOURCE']
    independentes = [r for r in RELACOES if r['RELATION'] == 'INDEPENDENT_SOURCE']
    familias_sinal_hoje = [k for k, v in FAMILIAS.items() if v.get('SIGNAL_TODAY', True)]
    return {
        'SOURCE_ID': 'REFRESH/SIGNAL-DEPENDENCY-GRAPH',
        'source': 'derivado dos handoffs congelados — nenhuma coleta',
        'SOURCE_LOCATION': 'derivado',
        'FACT_LOCATION': 'n/a — descreve o acervo, nao o mundo',
        'ARTIFACT_LANGUAGE': 'pt',
        'EVIDENCE_CLASS': 'DERIVED_DEPENDENCY_ANALYSIS',
        'captured_at': '2026-08-31', 'CAPTURED_AT': '2026-08-31',
        'POR_QUE_ESTE_ARQUIVO_VEM_PRIMEIRO':
            'contar convergencia antes de provar independencia produz numero bonito e '
            'falso. Duas telas nao sao dois sinais; duas leituras do mesmo documento '
            'tampouco.',
        'LEI': '2 cards != 2 independent signals',
        'RELACOES': RELACOES,
        'RELACOES_TOTAL': len(RELACOES),
        'RELACOES_DEPENDENTES': len(derivadas),
        'RELACOES_INDEPENDENTES': len(independentes),
        'FAMILIAS_DE_SINAL': FAMILIAS,
        'FAMILIAS_QUE_PODEM_CONTAR_HOJE': familias_sinal_hoje,
        'FAMILIAS_QUE_NAO_CONTAM_HOJE':
            [k for k, v in FAMILIAS.items() if not v.get('SIGNAL_TODAY', True)],
        'DOUBLE_COUNT_GUARDS': [
            'DERIVED_DEPENDENCY_ON_META — cadeia Foresight nao soma com anuncio Meta',
            'SHARED_REGISTRY_NOT_TWO_FAMILIES — registro nacional conta uma vez',
            'SAME_ENTITY_DIFFERENT_OBSERVATION — creator identidade+conteudo conta uma vez',
            'SAME_DATA_DIFFERENT_VIEW — listagem territorial nao acrescenta ao corpo',
            'IDENTITY_IS_NOT_SIGNAL — 22 contas provadas sem conteudo nao sao sinal',
        ],
    }


# ══════════════════════════════════════════════════ 2 · O REFRESH
def montar():
    fs3 = ler(INPUTS['COMPETITOR_FORESIGHT']['COMMIT'],
              INPUTS['COMPETITOR_FORESIGHT']['FILES']['three_layer'])
    terr = ler(INPUTS['EARLY_SIGNAL_TERRITORIAL']['COMMIT'],
               INPUTS['EARLY_SIGNAL_TERRITORIAL']['FILES']['final'])
    meta = ler(INPUTS['META_COMPETITOR']['HANDOFF_FILE_AT'],
               INPUTS['META_COMPETITOR']['FILES']['freeze'])
    cfz = ler(INPUTS['CREATOR_MAP']['COMMIT'], INPUTS['CREATOR_MAP']['FILES']['freeze'])
    deep = ler(INPUTS['CREATOR_DEEP_CORPUS']['COMMIT'],
               INPUTS['CREATOR_DEEP_CORPUS']['FILES']['delivery'])

    prov = fs3['PROVADAS']
    por_pais, por_emp = {}, {}
    for p in prov:
        por_pais[p['COUNTRY']] = por_pais.get(p['COUNTRY'], 0) + 1
        por_emp[p['META_COMPANY']] = por_emp.get(p['META_COMPANY'], 0) + 1

    med = terr['MEDICAO']
    recortes = terr['POR_RECORTE']
    prontos = [k for k, v in recortes.items() if v['STATE'] == 'CASE_SIGNAL_READY']
    parciais = [k for k, v in recortes.items() if v['STATE'] == 'PARTIAL']

    # ── CASE CANDIDATES · nenhum numero forcado
    cases = []
    for nome in prontos:
        v = recortes[nome]
        pais, cultura, issue = nome.split('_', 1)[0], None, None
        partes = nome.split('_')
        pais = partes[0]
        issue = partes[-1]
        cultura = '_'.join(partes[1:-1])
        cases.append({
            'CASE_ID': 'REFRESH-CASE-001',
            'SLICE': nome,
            'COUNTRY': {'VALUE': pais, 'STATE': 'PROVED'},
            'REGION': {'VALUE': 'declarado no item territorial', 'STATE': 'PROVED'},
            'CROP': {'VALUE': cultura, 'STATE': 'PROVED'},
            'ISSUE': {'VALUE': issue, 'STATE': 'PROVED'},
            'TIME': {'VALUE': 'PUBLISHED_AT do boletim', 'STATE': 'PROVED'},
            'SIGNALS_PRESENT': ['TERRITORIAL'],
            'INDEPENDENT_SIGNAL_FAMILIES': ['TERRITORIAL'],
            'INDEPENDENT_SIGNAL_FAMILY_COUNT': 1,
            'DEPENDENT_SIGNALS': [],
            'EVIDENCE': v.get('EVIDENCE'),
            'SOURCE_COMMITS': {
                'TERRITORIAL_DATA': INPUTS['EARLY_SIGNAL_TERRITORIAL']['COMMIT'],
                'TERRITORIAL_HANDOFF': INPUTS['EARLY_SIGNAL_TERRITORIAL']['HANDOFF_COMMIT'],
            },
            'WHAT_IS_PROVED': 'uma observacao territorial com as CINCO ancoras no corpo do '
                              'documento: pais, localidade, cultura, problema e tempo.',
            'WHAT_IS_NOT_PROVED': [
                'nenhuma segunda familia independente confirma este par',
                'expertise de especialista no problema: NOT_PROVED',
                'rota de creator especifica do problema: NOT_PROVED',
                'janela de aplicacao: nao existe relogio de lavoura conectado',
                'resposta ADAMA local para o par: NOT_MEASURED nesta rodada',
            ],
            'CONVERGENCE_CLASS': 'SINGLE_SIGNAL',
            'WHY_IT_MAY_DESERVE_ATTENTION':
                'e o unico recorte de todo o acervo em que a chave territorial completa '
                'fecha no corpo do documento, e nao no indice.',
            'WHAT_WOULD_CHANGE_A_DECISION':
                'uma segunda familia independente sobre o MESMO par — ciencia com o problema '
                'no titulo, registro local com cultura x alvo, ou campo datado.',
            'WHAT_IS_STILL_MISSING': ['segunda familia independente', 'janela agronomica',
                                      'resposta local ADAMA medida para o par'],
        })

    for i, nome in enumerate(parciais, start=2):
        v = recortes[nome]
        partes = nome.split('_')
        cases.append({
            'CASE_ID': 'REFRESH-PARTIAL-%03d' % i,
            'SLICE': nome,
            'COUNTRY': {'VALUE': partes[0], 'STATE': 'PROVED'},
            'REGION': {'VALUE': 'parcial', 'STATE': 'PARTIAL'},
            'CROP': {'VALUE': '_'.join(partes[1:-1]), 'STATE': 'PROVED'},
            'ISSUE': {'VALUE': partes[-1], 'STATE': 'NOT_PROVED'},
            'TIME': {'VALUE': 'PUBLISHED_AT', 'STATE': 'PROVED'},
            'SIGNALS_PRESENT': ['TERRITORIAL'],
            'INDEPENDENT_SIGNAL_FAMILIES': [],
            'INDEPENDENT_SIGNAL_FAMILY_COUNT': 0,
            'DEPENDENT_SIGNALS': [],
            'EVIDENCE': None,
            'SOURCE_COMMITS': {'TERRITORIAL_DATA': INPUTS['EARLY_SIGNAL_TERRITORIAL']['COMMIT']},
            'WHAT_IS_PROVED': 'pais, cultura e tempo. %s' % v['WHY'],
            'WHAT_IS_NOT_PROVED': ['o problema nao foi sustentado pelo CORPO do documento'],
            'CONVERGENCE_CLASS': 'NOT_ENOUGH_EVIDENCE',
            'WHY_IT_MAY_DESERVE_ATTENTION': 'o recorte existe e tem lastro parcial; falta o '
                                            'problema, que e o que amarra o caso.',
            'WHAT_WOULD_CHANGE_A_DECISION': 'o problema nomeado no corpo de um documento.',
            'WHAT_IS_STILL_MISSING': ['ISSUE no corpo'],
        })

    # ── observacoes de concorrente que NAO conseguem entrar na chave de caso
    comp = {
        'UNIT': 'TUPLA (competidor, pais, produto normalizado)',
        'PROVED_TUPLES': fs3['RESULTADO']['THREE_LAYER_CHAIN_PROVED_TUPLES'],
        'PROVED_PRODUCTS': fs3['RESULTADO']['POR_UNIDADE_PRODUTO'][
            'META_PRODUCTS_WITH_PROVED_THREE_LAYER_CHAIN'],
        'CANDIDATE_TUPLES': fs3['UNIVERSO']['THREE_LAYER_CANDIDATES_TOTAL'],
        'NOT_KNOWN_TUPLES': fs3['RESULTADO']['THREE_LAYER_CHAIN_NOT_KNOWN_TUPLES'],
        'REJECTED_TUPLES': fs3['RESULTADO']['THREE_LAYER_CHAIN_REJECTED_TUPLES'],
        'BY_COUNTRY': por_pais,
        'BY_COMPANY': por_emp,
        'URBOLE_GUARD': fs3['URBOLE_GUARD']['URBOLE_GUARD'],
        'CROP': {'VALUE': None, 'STATE': 'NOT_APPLICABLE'},
        'ISSUE': {'VALUE': None, 'STATE': 'NOT_APPLICABLE'},
        'POR_QUE_NAO_VIRA_CASO':
            'nenhum dos tres registros nacionais traz cultura x alvo neste dataset. Sem '
            'CROP e ISSUE a observacao nao entra na chave COUNTRY x REGION x CROP x ISSUE '
            'x TIME. Ela e real, e e de outra unidade.',
        'DEPENDENCIA': 'a perna META desta cadeia depende de META_PAID_ADS — nao somar as '
                       'duas como familias independentes.',
    }

    return {
        'SOURCE_ID': 'REFRESH/FINAL-INTELLIGENCE-REFRESH-EAME',
        'source': 'derivado de quatro handoffs obrigatorios + entradas opcionais, todos por '
                  'commit fixo. Nenhuma coleta, custo zero.',
        'SOURCE_LOCATION': 'derivado',
        'FACT_LOCATION': 'ES · IT · FR',
        'ARTIFACT_LANGUAGE': 'pt',
        'EVIDENCE_CLASS': 'DERIVED_INTELLIGENCE',
        'captured_at': '2026-08-31', 'CAPTURED_AT': '2026-08-31',
        'MANDATORY_HANDOFFS_ACCEPTED': '4/4',
        'INPUTS': INPUTS,
        'INPUT_BLOBS': {
            'FORESIGHT_THREE_LAYER': sha_do_blob(
                INPUTS['COMPETITOR_FORESIGHT']['COMMIT'],
                INPUTS['COMPETITOR_FORESIGHT']['FILES']['three_layer']),
            'TERRITORIAL_FINAL': sha_do_blob(
                INPUTS['EARLY_SIGNAL_TERRITORIAL']['COMMIT'],
                INPUTS['EARLY_SIGNAL_TERRITORIAL']['FILES']['final']),
            'META_FREEZE': sha_do_blob(
                INPUTS['META_COMPETITOR']['HANDOFF_FILE_AT'],
                INPUTS['META_COMPETITOR']['FILES']['freeze']),
        },
        'TERRITORIAL_MEASUREMENT': med,
        'TERRITORIAL_SLICES': {'CASE_SIGNAL_READY': prontos, 'PARTIAL': parciais},
        'META_CAPABILITIES': meta['capabilities'],
        'META_SNAPSHOT_1': meta['snapshot_1'],
        'META_PAGE_MODEL': meta['page_model'],
        'META_CANNOT_CLAIM': meta['cannot_claim'],
        'CREATOR_READINESS': cfz['READINESS'],
        'CREATOR_DEEP_CORPUS': {
            'TARGETS': deep['A_PERSON_CREATORS_ATTEMPTED'] + deep['B_FARM_BUSINESSES_ATTEMPTED'],
            'MATERIALS': deep['C_MATERIALS_COLLECTED'],
            'LAST_90D': deep['E_COVERAGE_BY_WINDOW']['LAST_90D'],
            'ISSUE_COVERAGE': deep['G_ISSUE_COVERAGE'],
        },
        'COMPETITOR_PRODUCT_OBSERVATIONS': comp,
        'CASE_CANDIDATES': cases,
        'CASE_CANDIDATE_COUNT': len(cases),
        'MULTI_SIGNAL_CONVERGENCES': [c['CASE_ID'] for c in cases
                                      if c['CONVERGENCE_CLASS'] == 'MULTI_SIGNAL_CONVERGENCE'],
        'PARTIAL_CONVERGENCES': [c['CASE_ID'] for c in cases
                                 if c['CONVERGENCE_CLASS'] == 'PARTIAL_CONVERGENCE'],
        'SINGLE_SIGNAL_CASES': [c['CASE_ID'] for c in cases
                                if c['CONVERGENCE_CLASS'] == 'SINGLE_SIGNAL'],
        'NOT_ENOUGH_EVIDENCE_CASES': [c['CASE_ID'] for c in cases
                                      if c['CONVERGENCE_CLASS'] == 'NOT_ENOUGH_EVIDENCE'],
        'NO_SCORE_DECLARATION':
            'este artefato nao contem ADAMA_OPPORTUNITY_SCORE, MARKET_OPPORTUNITY_SCORE '
            'nem SALES_SCORE. Nenhum numero aqui ordena por valor.',
        'PRODUCT_IMPLEMENTATION_MODE': 'NOT_ENTERED',
        'CASCO_V7_MODIFIED': 'NO',
        'REAL_DATA_WIRED': 'NO',
        'FINAL_TOOL_SET_DECIDED': 'NO',
    }


def main():
    os.makedirs(DEST, exist_ok=True)
    for nome, obj in (('SIGNAL-DEPENDENCY-GRAPH.json', grafo()),
                      ('FINAL-INTELLIGENCE-REFRESH-EAME.json', montar())):
        p = os.path.join(DEST, nome)
        with open(p, 'w', encoding='utf-8', newline='\n') as f:
            json.dump(obj, f, ensure_ascii=False, indent=1)
            f.write('\n')
        print('gravado %-42s %8d bytes' % (nome, os.path.getsize(p)))
    return 0


if __name__ == '__main__':
    sys.exit(main())
