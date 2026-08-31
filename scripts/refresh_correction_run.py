# -*- coding: utf-8 -*-
"""PRE-ARBITRATION CORRECTION PASS — montagem e emissao dos artefatos.

As primitivas (parser de recorte, pareamento, latencia, fenologia, grafo V2) vivem em
`refresh_correction.py`. Este arquivo monta e grava. Zero rede.

    py scripts/refresh_correction_run.py
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import refresh_correction as rc  # noqa: E402

try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
except AttributeError:  # pragma: no cover
    pass


# ══════════════════════════ 16 · rotulos italianos — so medir disponibilidade
def rotulos_italianos():
    man = rc.do_git(*rc.PIN['IT_LABEL_MANIFEST'])
    dirs = [r'C:\eame-sintonia-it\data\raw\IT', r'C:\eame-sintonia\data\raw\IT',
            os.path.join(rc.ROOT, 'data', 'raw', 'IT')]
    achados, onde = 0, None
    for c in dirs:
        if os.path.isdir(c):
            n = 0
            for dp, _, fs in os.walk(c):
                n += sum(1 for f in fs if f.lower().endswith('.pdf'))
            if n > achados:
                achados, onde = n, c
    alvo = man.get('TARGET_TOTAL')
    return {
        'LABEL_MANIFEST_TARGET': alvo,
        'LABELS_HASHED_IN_MANIFEST': man.get('LABELS_OBTAINED'),
        'MANIFEST_STATE': man.get('STATE'),
        'LOCAL_LABEL_PDFS_AVAILABLE_NOW': achados,
        'LOCAL_LABEL_PDFS_MISSING_NOW': (alvo - achados) if isinstance(alvo, int) else None,
        'WHERE_LOOKED': dirs, 'WHERE_FOUND': onde,
        'CROP_ISSUE_RECONSTRUCTION_MODE':
            'LOCAL_REPROCESSING_POSSIBLE_PARTIAL' if achados else 'RECOLLECTION_REQUIRED',
        'NOTE': 'SHA-256 preservado no manifesto NAO substitui o arquivo. Manifesto '
                'completo com PDF ausente = RECOLLECTION_REQUIRED para a parte ausente.',
        'RECONSTRUCTION_EXECUTED': 'NO',
    }


# ═══════════════════════════════════ 14 · MEDIDO != ESCRITO
def candidatos(itens, fh, rd, ic):
    esquema = rc.slice_schema()
    at, ac = [], []

    for slug, sc in esquema.items():
        do_pais = [i for i in itens if i['COUNTRY']['VALUE'] == sc['COUNTRY']]
        com_par = []
        for i in do_pais:
            for p in i['CROP_ISSUE_PAIRING']['PAIRS_PROVEN']:
                if p['CROP'] == sc['CROP'] and p['ISSUE'] == sc['ISSUE']:
                    com_par.append((i, p))
        chave_cheia = [(i, p) for i, p in com_par
                       if i['REGION']['STATE'] == 'PROVED' and i['TIME']['STATE'] == 'PROVED']
        blocos = {}
        for i in do_pais:
            b = rc.bloqueador(i)
            if b:
                blocos[b] = blocos.get(b, 0) + 1
        at.append({
            'CANDIDATE_ID': 'TERR-%s' % slug,
            'TYPE': 'TERRITORIAL_SLICE', 'SLICE': slug,
            'COUNTRY': sc['COUNTRY'], 'CROP': sc['CROP'], 'ISSUE': sc['ISSUE'],
            'EVIDENCE_INPUTS': ['%s:%s' % rc.PIN['TERRITORIAL']],
            'DERIVATION_RULE': 'item do pais com par cultura x problema provado DENTRO da '
                               'mesma passagem, mais REGION e TIME provados',
            'FACTS': {
                'BODY_ITEMS_IN_COUNTRY': len(do_pais),
                'WITH_CROP': sum(1 for i in do_pais if sc['CROP'] in (i['CROP']['VALUE'] or [])),
                'WITH_ISSUE': sum(1 for i in do_pais if sc['ISSUE'] in (i['ISSUE']['VALUE'] or [])),
                'WITH_TIME': sum(1 for i in do_pais if i['TIME']['STATE'] == 'PROVED'),
                'WITH_LOCALITY': sum(1 for i in do_pais if i['REGION']['STATE'] == 'PROVED'),
                'WITH_PAIR_PROVEN': len(com_par),
                'WITH_FULL_KEY': len(chave_cheia),
                'EXACT_BLOCKER_PER_ITEM': blocos,
            },
            'INFERENCES': {
                'INDEPENDENT_SIGNAL_FAMILIES': ['TERRITORIAL'] if chave_cheia else [],
                'CONVERGENCE_CLASS': 'SINGLE_SIGNAL' if chave_cheia else 'NOT_ENOUGH_EVIDENCE',
            },
            'JUDGMENT_REQUIRED': 'se um recorte com UMA familia merece fila de atencao',
            'ATTENTION_STATE': ('ATTENTION_CANDIDATE_TEST' if chave_cheia
                                else 'VALID_EVIDENCE_NOT_ATTENTION_READY'),
            'ITEMS_WITH_FULL_KEY': [i['ITEM_ID'] for i, _ in chave_cheia],
            'PAIR_PASSAGES': [p['PASSAGE'] for _, p in chave_cheia][:2],
        })

    at.append({
        'CANDIDATE_ID': 'FIELD-ES-OLIVE-REPILO', 'TYPE': 'LONGITUDINAL_FIELD_PRESSURE',
        'COUNTRY': 'ES', 'CROP': 'OLIVE', 'ISSUE': 'REPILO',
        'EVIDENCE_INPUTS': fh['ARTIFACTS'],
        'DERIVATION_RULE': 'serie preservada + coorte + backtest com regra declarada antes',
        'FACTS': {
            'SAMPLINGS_2026': fh['SAMPLINGS_2026'],
            'SEASONS_IN_PRESERVED_SERIES': fh['HISTORICAL_BASELINE']['SEASONS_IN_PRESERVED_SERIES'],
            'READINGS_IN_PRESERVED_SERIES': fh['HISTORICAL_BASELINE']['READINGS_IN_PRESERVED_SERIES'],
            'BACKTEST_TOTAL_FIRES': fh['LEAD_TIME_BACKTEST']['TOTAL_FIRES'],
            'BACKTEST_FALSE_POSITIVE_LOAD': fh['LEAD_TIME_BACKTEST']['FALSE_POSITIVE_LOAD'],
        },
        'INFERENCES': {
            'INDEPENDENCE_FROM_TERRITORIAL_RAIF': fh['INDEPENDENCE_FROM_TERRITORIAL_RAIF']['STATE'],
            'CONVERGENCE_CLASS': 'SINGLE_SIGNAL',
        },
        'JUDGMENT_REQUIRED': 'se uma serie retrospectiva sem antecedencia provada merece '
                             'fila de atencao, ou se e contexto',
        'ATTENTION_STATE': 'VALID_EVIDENCE_NOT_ATTENTION_READY',
        'WHY': fh['LEAD_TIME_BACKTEST']['HONEST_CONCLUSION'],
    })

    at.append({
        'CANDIDATE_ID': 'REGDEADLINE-IT-ADAMA', 'TYPE': 'REGULATORY_DEADLINE',
        'COUNTRY': 'IT', 'CROP': None, 'ISSUE': None,
        'EVIDENCE_INPUTS': ['%s:%s' % rc.PIN['IT_EXPIRIES']],
        'DERIVATION_RULE': 'registros ADAMA em vigor com vencimento futuro, como a fonte declara',
        'FACTS': {k: rd[k] for k in ('ADAMA_IN_FORCE_WITH_FUTURE_EXPIRY', 'IN_FORCE',
                                     'WITH_FUTURE_EXPIRY', 'NEXT_EXPIRIES_LISTED')},
        'INFERENCES': {'PERMITTED_ACTION': rd['PERMITTED_ACTION'],
                       'FORBIDDEN_ACTION': rd['FORBIDDEN_ACTION']},
        'JUDGMENT_REQUIRED': 'quais datas merecem revisao, e por quem',
        'ATTENTION_STATE': 'ATTENTION_CANDIDATE_TEST',
    })

    at.append({
        'CANDIDATE_ID': 'IDCHAIN-FORESIGHT-META', 'TYPE': 'IDENTITY_CHAIN_CONVERGENCE',
        'COUNTRY': 'ES/IT/FR', 'CROP': None, 'ISSUE': None,
        'EVIDENCE_INPUTS': ['%s:%s' % rc.PIN['FORESIGHT_3L']],
        'DERIVATION_RULE': 'concordancia de titular e pais nas tres pontas',
        'FACTS': {k: ic[k] for k in ('PROVED_TUPLES', 'PROVED_PRODUCTS', 'CANDIDATE_TUPLES',
                                     'NOT_KNOWN_TUPLES', 'REJECTED_TUPLES', 'BY_COUNTRY',
                                     'URBOLE_GUARD')},
        'INFERENCES': {'IS_NOT': ic['IS_NOT'], 'DOES_NOT_PROVE': ic['DOES_NOT_PROVE']},
        'JUDGMENT_REQUIRED': 'se identidade de produto de concorrente, sem cultura e sem '
                             'problema, merece fila de atencao',
        'ATTENTION_STATE': 'ATTENTION_CANDIDATE_TEST',
    })

    for c in at:
        tipo = 'BUSINESS_DECISION' if c['TYPE'] == 'REGULATORY_DEADLINE' else 'INVESTIGATION'
        ac.append({
            'CANDIDATE_ID': c['CANDIDATE_ID'], 'ACTION_TYPE': tipo,
            'EVIDENCE_INPUTS': c['EVIDENCE_INPUTS'],
            'DERIVATION_RULE': 'acao so existe onde o estado do candidato a sustenta',
            'FACTS': {'ATTENTION_STATE': c['ATTENTION_STATE']},
            'INFERENCES': {'OWNERS': (['REGULATORY', 'PORTFOLIO']
                                      if c['TYPE'] == 'REGULATORY_DEADLINE'
                                      else ['MARKET_DEVELOPMENT'])},
            'JUDGMENT_REQUIRED': 'se a acao e de negocio ou de desenvolvimento do proprio '
                                 'sistema — SYSTEM_DECISION nao prova valor de negocio',
        })
    return at, ac


def main():
    os.makedirs(rc.DEST, exist_ok=True)
    terr, itens = rc.reprocessar()
    fh = rc.field_historical()
    rd = rc.regulatory_deadlines()
    ic = rc.identity_chain()
    lab = rotulos_italianos()
    g = rc.grafo_v2()
    at, ac = candidatos(itens, fh, rd, ic)

    esquema = rc.slice_schema()
    bug = {s: {'SCHEMA': esquema[s], 'NAIVE': rc.parser_ingenuo(s)} for s in esquema}
    bug_hits = [s for s, v in bug.items()
                if v['NAIVE']['CROP'] != v['SCHEMA']['CROP']
                or v['NAIVE']['ISSUE'] != v['SCHEMA']['ISSUE']]

    lat = [dict(ITEM_ID=i['ITEM_ID'], SOURCE=i['SOURCE_ENTITY_ID'], **i['LATENCY'])
           for i in itens]
    medidos = [x for x in lat if x['STATE'] == 'MEASURED']
    por_fonte = {}
    for x in medidos:
        por_fonte.setdefault(x['SOURCE'], []).append(x['SOURCE_LATENCY_DAYS'])

    chaves_v2 = [c for c in at if c['TYPE'] == 'TERRITORIAL_SLICE'
                 and c['FACTS']['WITH_FULL_KEY'] > 0]
    deep = rc.do_git(*rc.PIN['DEEP_DELIVERY'])
    creator_fz = rc.do_git(*rc.PIN['CREATOR_FREEZE'])

    refresh = {
        'SOURCE_ID': 'REFRESH-CORRECTED/FINAL-INTELLIGENCE-REFRESH-EAME-V2',
        'source': 'correcao pre-arbitragem — tudo re-derivado, zero rede',
        'SOURCE_LOCATION': 'derivado', 'FACT_LOCATION': 'ES · IT · FR',
        'ARTIFACT_LANGUAGE': 'pt', 'EVIDENCE_CLASS': 'DERIVED_INTELLIGENCE',
        'captured_at': '2026-08-31', 'CAPTURED_AT': '2026-08-31',
        'BASE_REFRESH_COMMIT': rc.BASE_REFRESH_COMMIT,
        'REFRESH_V1_WITNESS': rc.BASE_REFRESH_COMMIT,
        'NEW_COLLECTION': 'NO', 'NETWORK_REQUESTS': 0,
        'SLICE_PARSER_BUG': {'FOUND_IN_V1': True, 'AFFECTED_SLICES': bug_hits,
                             'DETAIL': bug,
                             'FIX': 'schema explicito de PILOT-SCOPE-MATRIX-V1, nunca split'},
        'TERRITORIAL_BODY_ITEMS_REPROCESSED': len(itens),
        'TERRITORIAL_ITEMS': itens,
        'FIELD_HISTORICAL': fh,
        'REGULATORY_DEADLINE_OBJECT': rd,
        'IDENTITY_CHAIN_OBJECT': ic,
        'ITALIAN_LABELS': lab,
        'CREATOR_LAST_90D': {
            'FROM_CORPUS_DELIVERY': deep['E_COVERAGE_BY_WINDOW']['LAST_90D'],
            'MATERIALS_TOTAL': deep['C_MATERIALS_COLLECTED'],
            'UNIT': 'materiais na janela de 90 dias, contados por item',
            'NOTE': 'lido do freeze a509c12, nao do texto de nenhum documento',
        },
        'CREATOR_READINESS': creator_fz['READINESS'],
        'SOURCE_LATENCY': {
            'MEASURED_ITEMS': len(medidos), 'TOTAL_ITEMS': len(lat),
            'BY_SOURCE': {k: {'N': len(v), 'DAYS': sorted(v)} for k, v in por_fonte.items()},
            'LAW': 'PIPELINE_LATENCY != AGE_OF_OBSERVATION', 'NO_SCORE': True,
        },
        'FULL_CASE_KEYS_V2': sum(c['FACTS']['WITH_FULL_KEY'] for c in chaves_v2),
        'FULL_CASE_KEY_SLICES_V2': [c['SLICE'] for c in chaves_v2],
        'FR_FULL_CASE_KEYS_V2': sum(c['FACTS']['WITH_FULL_KEY'] for c in at
                                    if c['TYPE'] == 'TERRITORIAL_SLICE' and c['COUNTRY'] == 'FR'),
        'PHENOLOGY_AT_OBSERVATION_PROVED_ITEMS':
            sum(1 for i in itens if i['PHENOLOGY']['CROP_STAGE_AT_OBSERVATION'] == 'PROVED'),
        'APPLICATION_TRIGGER_AT_OBSERVATION_PROVED_ITEMS':
            sum(1 for i in itens if i['PHENOLOGY']['APPLICATION_TRIGGER_AT_OBSERVATION'] == 'PROVED'),
        'MULTI_BULLETIN_DOCUMENTS': sum(1 for i in itens if i['MULTI_BULLETIN_DOCUMENT']),
        'PAIRS_CARTESIAN_AVOIDED':
            sum(i['CROP_ISSUE_PAIRING']['PAIRS_CARTESIAN_AVOIDED'] for i in itens),
        'CASE_MULTI_SIGNAL_CONVERGENCES': 0,
        'IDENTITY_CHAIN_CONVERGENCES': ic['PROVED_TUPLES'],
        'LONGITUDINAL_FIELD_OBJECTS': 1,
        'REGULATORY_DEADLINE_OBJECTS': rd['ADAMA_IN_FORCE_WITH_FUTURE_EXPIRY'],
        'ATTENTION_READY': [c['CANDIDATE_ID'] for c in at if c['ATTENTION_STATE'] == 'ATTENTION_READY'],
        'ATTENTION_CANDIDATE_TEST': [c['CANDIDATE_ID'] for c in at
                                     if c['ATTENTION_STATE'] == 'ATTENTION_CANDIDATE_TEST'],
        'VALID_EVIDENCE_NOT_ATTENTION_READY': [c['CANDIDATE_ID'] for c in at
                                               if c['ATTENTION_STATE'] == 'VALID_EVIDENCE_NOT_ATTENTION_READY'],
        'NO_SCORE_DECLARATION': 'nenhum score agregado neste artefato',
        'PRODUCT_IMPLEMENTATION_MODE': 'NOT_ENTERED', 'CASCO_V7_MODIFIED': 'NO',
    }

    for nome, obj in [
        ('SIGNAL-DEPENDENCY-GRAPH-V2.json', g),
        ('FINAL-INTELLIGENCE-REFRESH-EAME-V2.json', refresh),
        ('ATTENTION-CANDIDATES.json',
         {'SOURCE_ID': 'REFRESH-CORRECTED/ATTENTION-CANDIDATES',
          'MEASURED_NOT_WRITTEN': 'cada linha separa FACTS de INFERENCES e de JUDGMENT_REQUIRED',
          'CANDIDATES': at}),
        ('ACTION-CANDIDATES.json',
         {'SOURCE_ID': 'REFRESH-CORRECTED/ACTION-CANDIDATES',
          'ACTION_TYPES': ['BUSINESS_DECISION', 'SYSTEM_DECISION', 'INVESTIGATION'],
          'CENTRAL_USER_ABSORPTION_GUARD':
              'Market Development e usuario central por decisao arquitetonica, NAO porque '
              'recebeu todas as linhas da tabela',
          'CANDIDATES': ac}),
        ('SOURCE-LATENCY-EAME.json',
         {'SOURCE_ID': 'REFRESH-CORRECTED/SOURCE-LATENCY',
          'LAW': 'PIPELINE_LATENCY != AGE_OF_OBSERVATION',
          'LIMITE_DESTA_MEDICAO':
              'todos os itens tem o MESMO CAPTURED_AT (2026-08-31): foi uma captura unica. '
              'Por construcao, SOURCE_LATENCY == AGE_OF_OBSERVATION em todas as linhas. '
              'Isto mede IDADE DO DOCUMENTO NA PRIMEIRA CAPTURA, nao latencia de regime '
              'de um pipeline que roda com cadencia. Separar as duas exige uma segunda '
              'captura, e nao ha coleta autorizada nesta passagem.',
          'MEASURED_ITEMS': len(medidos), 'TOTAL_ITEMS': len(lat),
          'BY_SOURCE': {k: {'N': len(v), 'DAYS': sorted(v)} for k, v in por_fonte.items()},
          'ITEMS': lat}),
    ]:
        p = os.path.join(rc.DEST, nome)
        with open(p, 'w', encoding='utf-8', newline='\n') as f:
            json.dump(obj, f, ensure_ascii=False, indent=1)
            f.write('\n')
        print('gravado %-42s %8d bytes' % (nome, os.path.getsize(p)))

    print()
    print('BUG DE PARSER afeta ............... %s' % (bug_hits or 'nenhum'))
    print('itens reprocessados ............... %d' % len(itens))
    print('documentos multi-boletim .......... %d' % refresh['MULTI_BULLETIN_DOCUMENTS'])
    print('pares cartesianos evitados ........ %d' % refresh['PAIRS_CARTESIAN_AVOIDED'])
    print('chaves completas V2 ............... %d  %s'
          % (refresh['FULL_CASE_KEYS_V2'], refresh['FULL_CASE_KEY_SLICES_V2']))
    print('chaves completas FR ............... %d' % refresh['FR_FULL_CASE_KEYS_V2'])
    print('fenologia na observacao ........... %d' % refresh['PHENOLOGY_AT_OBSERVATION_PROVED_ITEMS'])
    print('gatilho na observacao ............. %d' % refresh['APPLICATION_TRIGGER_AT_OBSERVATION_PROVED_ITEMS'])
    print('latencia medida ................... %d de %d' % (len(medidos), len(lat)))
    print('relacoes: %d total · %d dep · %d indep'
          % (g['RELATIONS_TOTAL'], g['RELATIONS_DEPENDENT'], g['RELATIONS_INDEPENDENT']))
    print('familias que contam hoje .......... %d %s'
          % (len(g['FAMILIES_THAT_CAN_COUNT_TODAY']), g['FAMILIES_THAT_CAN_COUNT_TODAY']))
    print('creator LAST_90D .................. %s' % refresh['CREATOR_LAST_90D']['FROM_CORPUS_DELIVERY'])
    print('rotulos IT: alvo %s · disco %s · faltam %s'
          % (lab['LABEL_MANIFEST_TARGET'], lab['LOCAL_LABEL_PDFS_AVAILABLE_NOW'],
             lab['LOCAL_LABEL_PDFS_MISSING_NOW']))
    return 0


if __name__ == '__main__':
    sys.exit(main())
