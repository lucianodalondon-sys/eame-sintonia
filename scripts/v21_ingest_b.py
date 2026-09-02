#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DESIGN-INGEST · parte B — as camadas de fato, fundidas.

    python3 scripts/v21_ingest_b.py

⚠️ §7 · O DADO GRANULAR VOLTA
------------------------------
O V2 guardou 33 «afirmações-resumo» de peso econômico, com frases como «6
culturas com dado regional completo». Isso não é dado operacional: é prosa
sobre dado.

Aqui voltam as **983 linhas atômicas** do ISTAT — uma por cultura × território
× ano × indicador. As 33 afirmações continuam, mas como CAMADA DE LEITURA, não
como substituto.

    UMA FRASE SOBRE UM CONJUNTO NÃO É O CONJUNTO.

⚠️ §14 · VOZ NÃO É FONTE INDEPENDENTE
--------------------------------------
Quatro pessoas citadas num artigo são QUATRO VOZES e UM DOCUMENTO. Por isso
toda voz carrega `SOURCE_DOCUMENT_ID` além de `VOICE_ID` e `PERSON_ID` — e a
contagem de convergência futura tem de contar documento, não gente.
"""
import csv
import json
import os
import re
import sys
from collections import Counter, defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import v21_normalizar as N            # noqa: E402
from v21_ingest import (ANT, ING, ISTAT_CSV, LM, V2, ant, base, do_anterior,  # noqa: E402
                        do_lastmile, le, sid)

MAP = {}


def grava(nome, colecao, itens, chave, verdade, substitui=None, lei=None, extra=None):
    cs = sum(1 for x in itens if x.get('CLIENT_SAFE'))
    corpo = {
        'COLLECTION': colecao, 'FILE': nome, 'SCHEMA_VERSION': 'V2.1',
        'BUILT_AT': '2026-09-02', 'PRIMARY_KEY': chave, 'SOURCE_OF_TRUTH': verdade,
        'COUNT_TOTAL': len(itens), 'COUNT_CLIENT_SAFE': cs,
        'BY_ORIGIN': dict(Counter(x.get('ORIGIN_LAYER') for x in itens)),
        'BY_QA': dict(Counter(x.get('QA_STATUS') for x in itens)),
    }
    if substitui:
        corpo['REPLACES_OLD_FILES'] = substitui
    if lei:
        corpo['LAW'] = lei
    if extra:
        corpo.update(extra)
    corpo['RECORDS'] = itens
    json.dump(corpo, open(os.path.join(ING, nome), 'w', encoding='utf-8'),
              ensure_ascii=False, indent=1)
    MAP[colecao] = corpo
    return corpo


def main():
    lm = le(os.path.join(V2, 'CANONICAL-INTELLIGENCE.json'), 'RECORDS')
    fam = defaultdict(list)
    for r in lm:
        fam[r['FAMILIA']].append(r)

    # ══ CROP WINDOWS ═════════════════════════════════════════════════════════
    w = [do_anterior(x, 'CROP_WINDOW', [x.get('SOURCE_URL') or x.get('URL')],
                     x.get('DECREE_DATE') or x.get('DATE'),
                     [N.crop_id(x.get('CROP'))], [N.issue_id(x.get('TARGET'),
                                                             x.get('ISSUE'))],
                     N.region_ids(x.get('REGION')), N.escopo(x.get('REGION')),
                     extra={k: v for k, v in x.items() if k != 'ID'})
         for x in ant('CROP-WINDOWS/crop-windows.json', 'WINDOWS')]
    grava('CROP-WINDOWS.json', 'CROP_WINDOWS', w, 'ID',
          'decretos regionais de lotta obbligatoria',
          ['PREVIOUS-HANDOFF/.../CROP-WINDOWS/crop-windows.json'])

    # ══ SINAIS DE CAMPO CORRENTES — 73 anteriores + last-mile ════════════════
    cf = []
    for x in ant('CROP-WINDOWS/current-phenology.json', 'PHENOLOGY'):
        crops = [N.crop_id(c) for c in (x.get('CROPS') or [])]
        # §7 · A GEOGRAFIA VEM DO DOCUMENTO, NAO DA PASTA DO COLETOR.
        # O campo REGION desta fonte e rotulo de LOTE ("TOSCANA-FVG",
        # "MARCHE-UMBRIA", "PUGLIA-SUD"): diz onde o coletor guardou, nao onde o
        # boletim vale. Lendo-o como geografia, 12 boletins do Friuli sairam
        # carimbados Toscana e 4 boletins provinciais das Marche sairam como
        # Umbria. A propria fonte declara, nos 73 registros:
        #   "boletim provincial NAO representa a regiao"
        # e o codigo ignorava a declaracao.
        g = N.geografia(x.get('BULLETIN_TITLE'), x.get('URL'),
                        rotulo_de_lote=x.get('REGION'))
        cf.append(do_anterior(
            x, 'FIELD_SIGNAL', [x.get('URL')], x.get('PUBLICATION_DATE'),
            crops, [N.issue_id(*(x.get('PESTS_AND_DISEASES_CITED') or []))],
            g['REGION_IDS'], g['GEOGRAPHIC_SCOPE'],
            extra={
                'PROVINCE_IDS': g['PROVINCE_IDS'],
                'AREAL_IDS': g['AREAL_IDS'],
                'GEOGRAPHY_STATE': g['GEOGRAPHY_STATE'],
                'REGION_REPRESENTS': g['REGION_REPRESENTS'],
                'GEOGRAPHY_EVIDENCE': g['GEOGRAPHY_EVIDENCE'],
                'GEOGRAPHY_BATCH_LABEL': g['GEOGRAPHY_BATCH_LABEL'],
                'GEOGRAPHY_LAW': ('PROVINCIAL != REGIONAL. REGION_IDS aqui diz '
                                  'que regiao CONTEM o documento; REGION_REPRESENTS '
                                  'diz se o documento fala PELA regiao.'),
                'BULLETIN_TITLE': x.get('BULLETIN_TITLE'),
                'BULLETIN_NUMBER': x.get('BULLETIN_NUMBER'),
                'PHENOLOGICAL_STAGE_DECLARED': x.get('PHENOLOGICAL_STAGE_DECLARED'),
                'PESTS_AND_DISEASES_CITED': x.get('PESTS_AND_DISEASES_CITED'),
                'CROP_STATE': x.get('CROP_STATE'),
                'CROPS_DECLARED': x.get('CROPS'),
                'INTERVENTION_GUIDANCE': x.get('INTERVENTION_GUIDANCE'),
                'CITATION': x.get('CITATION'),
                'OBSERVATION_CLASS': 'CURRENT',
            }))
    for x in fam['CURRENT_FIELD_SIGNALS']:
        cf.append(do_lastmile(x, 'FIELD_SIGNAL',
                              issues=[N.issue_id(x.get('valor'), x.get('tipo'),
                                                 x.get('o_que'), permitir_prosa=True)]))
    grava('CURRENT-FIELD-SIGNALS.json', 'FIELD_SIGNALS', cf, 'ID',
          'boletins fitossanitarios oficiais regionais e provinciais',
          ['PREVIOUS-HANDOFF/.../CROP-WINDOWS/current-phenology.json',
           'V2/CURRENT-FIELD-SIGNALS.json'],
          'GEOGRAPHIC_SCOPE nunca sobe: boletim PROVINCIAL ou AREALE nao '
          'representa a regiao. Cinco documentos provinciais da Campania nao sao '
          '«a Campania».')

    # ══ PESO ECONÔMICO — as 983 linhas atômicas voltam ═══════════════════════
    ec = []
    if os.path.exists(ISTAT_CSV):
        with open(ISTAT_CSV, encoding='utf-8') as f:
            for i, row in enumerate(csv.DictReader(f)):
                ano = int(row['year'])
                nac = row['area_code'] == 'IT'
                rid = ['GEO_ITALY'] if nac else N.region_ids(row['area_it'])
                for col, ind, uni, deriv in (
                        ('superficie_totale_ha', 'AREA', 'ha', False),
                        ('produzione_raccolta_q', 'PRODUCTION', 'quintali', False),
                        ('resa_calculada_t_ha', 'YIELD', 't/ha', True)):
                    v = (row.get(col) or '').strip()
                    if not v:
                        continue
                    ec.append(base(
                        'ECW_%s_%s_%d_%s' % (row['crop_code'], row['area_code'],
                                             ano, ind),
                        'CROP_ECONOMIC_WEIGHT',
                        'REAL_DERIVED' if deriv else 'REAL_SOURCE_LAST_MILE',
                        'QA_UNREVIEWED', [row['source_url']], '%d-12-31' % ano,
                        [N.crop_id(row['crop_it'])], [], rid,
                        'NACIONAL' if nac else 'REGIONAL',
                        extra={
                            'CROP_LITERAL': row['crop_it'],
                            'CROP_CODE': row['crop_code'],
                            'GEOGRAPHY': row['area_it'],
                            'GEOGRAPHY_CODE': row['area_code'],
                            'GEOGRAPHY_LEVEL': 'NATIONAL' if nac else 'REGION',
                            'YEAR': ano, 'INDICATOR': ind,
                            'VALUE': float(v), 'UNIT': uni,
                            'IS_DERIVED_BY_SINTONIA': deriv,
                            'DERIVATION_FORMULA': (
                                'produzione_raccolta_q / 10 / superficie_totale_ha'
                                if deriv else None),
                            'DATASET': row['dataflow'],
                            'OBSERVATION_CLASS': 'OUTLOOK' if ano >= 2026 else 'HISTORICAL',
                            'CAVEAT': (
                                'o rendimento e DERIVADO sobre a area TOTAL: a area em '
                                'producao veio vazia em 100% das linhas, entao para '
                                'cultura perene este valor e um PISO.' if deriv else
                                ('o ano 2026 foi publicado em 28/07/2026, antes da '
                                 'colheita de oliveira, uva e milho — nao e colheita '
                                 'observada.' if ano >= 2026 else None)),
                        }))
    for x in fam['CROP_ECONOMIC_WEIGHT']:
        r = do_lastmile(x, 'CROP_ECONOMIC_WEIGHT_CLAIM')
        r['IS_SUMMARY_CLAIM'] = True
        r['SUMMARY_CLAIM_NOTE'] = (
            'e uma LEITURA sobre o conjunto, nao um dado atomico. As linhas '
            'atomicas estao neste mesmo arquivo com ENTITY_TYPE '
            'CROP_ECONOMIC_WEIGHT. Uma frase sobre um conjunto nao e o conjunto.')
        ec.append(r)
    grava('CROP-ECONOMIC-WEIGHT.json', 'CROP_ECONOMIC_WEIGHT', ec, 'ID',
          'ISTAT · cubo 101_1015 Coltivazioni · 20 regioes + nacional',
          ['V2/CROP-ECONOMIC-WEIGHT.json (eram 33 afirmacoes-resumo)'],
          'valor PUBLICADO e valor DERIVADO nao se misturam: '
          'IS_DERIVED_BY_SINTONIA marca cada linha, e o rendimento e nosso.',
          extra={'ATOMIC_ROWS': sum(1 for x in ec
                                    if x['ENTITY_TYPE'] == 'CROP_ECONOMIC_WEIGHT'),
                 'SUMMARY_CLAIMS': sum(1 for x in ec if x.get('IS_SUMMARY_CLAIM'))})

    # ══ MERCADO ══════════════════════════════════════════════════════════════
    mk = [do_anterior(x, 'MARKET_OBSERVATION', [x.get('SOURCE_URL')],
                      x.get('PERIOD_END') or x.get('PERIOD'),
                      [N.crop_id(x.get('CROP') or x.get('PRODUCT'))], [],
                      N.region_ids(x.get('PLACE') or x.get('GEOGRAPHY')),
                      N.escopo(x.get('PLACE') or x.get('GEOGRAPHY')),
                      extra={k: v for k, v in x.items() if k != 'ID'})
          for x in ant('MARKET-PULSE/market-pulse.json', 'PRICES')]
    mk += [do_lastmile(x, 'MARKET_OBSERVATION') for x in fam['MARKET_OBSERVATIONS']]
    grava('MARKET-OBSERVATIONS.json', 'MARKET', mk, 'ID',
          'ISMEA Mercati · EC Agri-food Data Portal · Eurostat · BMTI',
          ['PREVIOUS-HANDOFF/.../MARKET-PULSE/market-pulse.json',
           'V2/MARKET-OBSERVATIONS.json'],
          'preco de uma PIAZZA nao e preco NACIONAL. E serie parada mantem o '
          'ultimo valor e parece corrente.')

    # ══ CONCORRENTE ══════════════════════════════════════════════════════════
    cp = [do_anterior(x, 'COMPETITOR_ACTIVITY', [x.get('SOURCE_URL')],
                      x.get('PUBLISHED_AT') or x.get('FIRST_OBSERVED'),
                      [N.crop_id(c) for c in (x.get('CROP_TERMS') or [])], [],
                      ['GEO_ITALY'], 'NACIONAL',
                      extra={k: v for k, v in x.items() if k != 'ID'})
          for x in ant('COMPETITOR-WATCH/competitor-activities.json', 'ACTIVITIES')]
    cp += [do_lastmile(x, 'COMPETITOR_ACTIVITY')
           for x in fam['COMPETITOR_PUBLIC_SIGNALS']]
    grava('COMPETITOR-ACTIVITIES.json', 'COMPETITORS', cp, 'ID',
          'Meta Ad Library · YouTube · sitios .it das empresas · imprensa tecnica',
          ['PREVIOUS-HANDOFF/.../COMPETITOR-WATCH/competitor-activities.json',
           'V2/COMPETITOR-PUBLIC-SIGNALS.json'],
          'AD_REACHED_COUNTRY nao e AD_TARGETED_COUNTRY. E comunicacao nao e '
          'participacao de mercado.')

    # ══ CIÊNCIA · PESQUISADORES · RESISTÊNCIA ════════════════════════════════
    for arq, chave, col, tipo, nome in (
            ('SCIENCE/scientific-records.json', 'RECORDS', 'SCIENCE',
             'SCIENTIFIC_RECORD', 'SCIENCE.json'),
            ('SCIENCE/researchers.json', 'RESEARCHERS', 'RESEARCHERS',
             'RESEARCHER', 'RESEARCHERS.json'),
            ('SCIENCE/herbicide-resistance.json', 'RESISTANCES', 'RESISTANCE',
             'RESISTANCE_RECORD', 'RESISTANCE.json')):
        itens = [do_anterior(
            x, tipo, [x.get('SOURCE_URL') or x.get('URL') or x.get('DOI')],
            x.get('PUBLISHED_AT') or x.get('FIRST_CASE_YEAR'),
            [N.crop_id(x.get('CROP') or x.get('CROP_DECLARED'))],
            [N.issue_id(x.get('SPECIES'), x.get('SPECIES_IT'), x.get('TARGET'))],
            N.region_ids(x.get('REGION')), N.escopo(x.get('REGION')),
            extra={k: v for k, v in x.items() if k != 'ID'})
            for x in ant(arq, chave)]
        grava(nome, col, itens, 'ID',
              {'SCIENCE': 'OpenAlex · DOI', 'RESEARCHERS': 'OpenAlex · ORCID',
               'RESISTANCE': 'GIRE · Gruppo Italiano Resistenza Erbicidi'}[col],
              ['PREVIOUS-HANDOFF/.../' + arq])

    # ══ VOZES — §14: voz não é fonte independente ════════════════════════════
    vz = []
    for x in ant('VOCI-DAL-CAMPO/field-voices.json', 'VOICES'):
        doc = sid(x.get('SOURCE_URL'))
        vz.append(do_anterior(
            x, 'AUDIENCE_COMMENT', [x.get('SOURCE_URL')], x.get('PUBLISHED_AT'),
            [N.crop_id(x.get('CROP'))], [N.issue_id(x.get('TARGET'))],
            N.region_ids(x.get('REGION')), N.escopo(x.get('REGION')),
            extra=dict({k: v for k, v in x.items() if k != 'ID'}, **{
                'VOICE_ID': x['ID'], 'PERSON_ID': None,
                'SOURCE_DOCUMENT_ID': 'DOC_' + doc,
                'VOICE_KIND': 'AUDIENCE_COMMENT',
                'ROLE_EVIDENCE': 'nenhuma: e comentario sob video. O fonte_id e o '
                                 'CANAL, nunca o autor.',
                'AUDIENCE_KIND': x.get('CHANNEL_AUDIENCE_KIND'),
            })))
    for x in fam['PUBLIC_VOICES']:
        r = do_lastmile(x, 'IDENTIFIED_VOICE')
        doc = 'DOC_' + sid(x.get('source_url')) + '_' + str(
            x.get('publication_date') or '')[:10].replace('-', '')
        r.update({
            'VOICE_ID': r['ID'], 'SOURCE_DOCUMENT_ID': doc,
            'VOICE_KIND': 'IDENTIFIED_VOICE',
            'PERSON_ID': 'PER_' + re.sub(r'[^A-Z0-9]+', '_',
                                         str(x.get('valor') or x.get('crop') or
                                             '')[:40].upper()).strip('_') or None,
            'ROLE_EVIDENCE': x.get('o_que_prova'),
        })
        vz.append(r)
    docs = len({v.get('SOURCE_DOCUMENT_ID') for v in vz})
    grava('PUBLIC-VOICES.json', 'VOICES', vz, 'VOICE_ID',
          'YouTube (plateia de canal) · imprensa tecnica e institucional (vozes '
          'identificadas)',
          ['PREVIOUS-HANDOFF/.../VOCI-DAL-CAMPO/field-voices.json',
           'V2/PUBLIC-VOICES.json'],
          'VOZ NAO E FONTE INDEPENDENTE. Quatro pessoas citadas num artigo sao '
          'quatro VOZES e UM documento. Contagem de convergencia conta '
          'SOURCE_DOCUMENT_ID, nunca numero de pessoas.',
          extra={'DISTINCT_SOURCE_DOCUMENTS': docs,
                 'VOICES_PER_DOCUMENT': round(len(vz) / max(1, docs), 2)})

    ch = [do_anterior(x, 'PUBLIC_CHANNEL', [x.get('URL') or x.get('CHANNEL_URL')],
                      None, [], [], [], 'NAO_SEI',
                      extra={k: v for k, v in x.items() if k != 'ID'})
          for x in ant('VOCI-DAL-CAMPO/italian-channels.json', 'CHANNELS')]
    grava('PUBLIC-CHANNELS.json', 'CHANNELS', ch, 'ID', 'YouTube · canais italianos',
          ['PREVIOUS-HANDOFF/.../VOCI-DAL-CAMPO/italian-channels.json'])

    # ══ REGULATÓRIO FUTURO · CLIMA ═══════════════════════════════════════════
    rf = [do_lastmile(x, 'REGULATORY_FUTURE_SIGNAL') for x in fam['REGULATORY_FUTURE']]
    grava('REGULATORY-FUTURE.json', 'REGULATORY_FUTURE', rf, 'ID',
          'EU Pesticides Database · SCoPAFF · EUR-Lex · EFSA',
          ['V2/REGULATORY-FUTURE.json'],
          'PRORROGACAO NAO E RENOVACAO. Rascunho, discussao e reuniao nao sao '
          'decisao final.')
    ag = [do_lastmile(x, 'AGROMET_CONDITION') for x in fam['AGROMET_CONDITIONS']]
    grava('AGROMET-CONDITIONS.json', 'AGROMET', ag, 'ID',
          'ARPA regionais · Copernicus EDO · JRC MARS',
          ['V2/AGROMET-CONDITIONS.json'],
          'CLIMA E CONDICAO. Nao e presenca de doenca, nao e incidencia de praga, '
          'nao e perda. Qualquer cruzamento clima x cultura x doenca e '
          'INTERPRETACAO do Sintonia.')

    # ══ EVENTOS ══════════════════════════════════════════════════════════════
    ev = [do_anterior(x, 'EVENT', [x.get('OFFICIAL_URL') or x.get('SOURCE_URL')],
                      x.get('DATE'), [N.crop_id(x.get('CROP_RELEVANCE'))], [],
                      N.region_ids(x.get('LOCATION')), N.escopo(x.get('LOCATION')),
                      extra={k: v for k, v in x.items() if k != 'ID'})
          for x in ant('EVENTS/events.json', 'EVENTS')]
    ev += [do_lastmile(x, 'EVENT') for x in fam['FUTURE_EVENTS']]
    grava('EVENTS.json', 'EVENTS', ev, 'ID',
          'sitios de organizador, feira e sociedade cientifica',
          ['PREVIOUS-HANDOFF/.../EVENTS/events.json', 'V2/FUTURE-EVENTS.json'],
          'participacao futura NUNCA se infere de participacao passada.')
    fut = [x for x in ev if str(x.get('REFERENCE_DATE') or '') >= '2026-09-02']
    grava('FUTURE-EVENTS.json', 'FUTURE_EVENTS', fut, 'ID',
          'subconjunto de EVENTS.json com data a partir de 02/09/2026',
          None,
          'ATENCAO: este arquivo e um RECORTE de EVENTS.json, nao uma colecao '
          'independente. Carregar os dois soma o mesmo evento duas vezes.')

    # ══ OPORTUNIDADES · SINAIS · FONTES · NOTÍCIAS ═══════════════════════════
    op = [do_anterior(x, 'OPPORTUNITY_CANDIDATE', [x.get('OFFICIAL_URL')], None,
                      [N.crop_id(x.get('CROP'))], [N.issue_id(x.get('ISSUE'))],
                      N.region_ids(x.get('REGION')), N.escopo(x.get('REGION')),
                      extra={k: v for k, v in x.items() if k != 'ID'})
          for x in ant('OPPORTUNITIES/opportunities.json', 'OPPORTUNITIES')]
    grava('OPPORTUNITIES.json', 'OPPORTUNITIES', op, 'ID',
          'derivacao do Sintonia sobre fatos verificados',
          ['PREVIOUS-HANDOFF/.../OPPORTUNITIES/opportunities.json'],
          'o rotulo obrigatorio e «CONVERGENCIA QUE MERECE INVESTIGACAO», nunca '
          '«oportunidade».')
    fs = [do_anterior(x, 'FUTURE_SIGNAL', [x.get('SOURCE_URL')], None,
                      [N.crop_id(x.get('CROP'))], [], [], 'NAO_SEI',
                      extra={k: v for k, v in x.items() if k != 'ID'})
          for x in ant('FUTURE-RADAR/future-signals.json', 'SIGNALS')]
    grava('FUTURE-SIGNALS.json', 'FUTURE_SIGNALS', fs, 'ID',
          'CELLAR/EUR-Lex · OpenAlex',
          ['PREVIOUS-HANDOFF/.../FUTURE-RADAR/future-signals.json'])
    nw = [do_anterior(x, 'NEWS_ITEM', [x.get('URL') or x.get('SOURCE_URL')],
                      x.get('PUBLISHED_AT'), [N.crop_id(x.get('CROP'))], [],
                      N.region_ids(x.get('REGION')), N.escopo(x.get('REGION')),
                      extra={k: v for k, v in x.items() if k != 'ID'})
          for x in ant('NEWS/news.json', 'NEWS')]
    grava('NEWS.json', 'NEWS', nw, 'ID', 'imprensa tecnica italiana',
          ['PREVIOUS-HANDOFF/.../NEWS/news.json'],
          'CONTENT_KIND separa editorial de conteudo patrocinado.')

    src = []
    for x in ant('SOURCES/sources.json', 'SOURCES'):
        src.append(do_anterior(x, 'SOURCE', [x.get('URL')], None, [], [], [],
                               'NAO_SEI',
                               extra=dict({k: v for k, v in x.items() if k != 'ID'},
                                          RUNTIME_DEPENDENCY='NENHUMA')))
    novas = le(os.path.join(ROOT_RES := os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        'research', 'italy-lastmile'), 'NEW-REAL-SOURCES.json'))
    for s in (novas.get('FONTES') or []):
        src.append(base('SRCX_' + sid(s.get('URL'))[4:], 'SOURCE',
                        'REAL_SOURCE_LAST_MILE', 'QA_UNREVIEWED',
                        [s.get('URL')], None, [], [], [], 'NAO_SEI',
                        extra={
                            'NAME': s.get('NOME'),
                            'WHAT_IT_PUBLISHES': s.get('O_QUE_PUBLICA'),
                            'ACCESS_STATE': s.get('ESTADO_DE_ACESSO'),
                            'ACCESS_EVIDENCE': s.get('EVIDENCIA_DO_ESTADO'),
                            'REQUIRES_ITALIAN_ROUTE': s.get('EXIGE_ROTA_ITALIANA'),
                            'RUNTIME_DEPENDENCY': 'NENHUMA',
                        }))
    grava('SOURCES.json', 'SOURCES', src, 'ID', 'medicao propria de estado de acesso',
          ['PREVIOUS-HANDOFF/.../SOURCES/sources.json', 'V2/SOURCES.json'],
          '§18 · metadado de rota e INFRAESTRUTURA DE COLETA. O portal consome '
          'dado ja guardado e NUNCA precisa da rota italiana para renderizar.')

    p = os.path.join(ING, '_PARCIAL.json')
    if os.path.exists(p):
        os.remove(p)
    json.dump(MAP and {k: {kk: vv for kk, vv in v.items() if kk != 'RECORDS'}
                       for k, v in MAP.items()},
              open(os.path.join(ING, '_COLECOES.json'), 'w', encoding='utf-8'),
              ensure_ascii=False, indent=1)

    print('%-26s %7s %7s' % ('COLECAO', 'TOTAL', 'SAFE'))
    for k, v in MAP.items():
        print('%-26s %7d %7d' % (k, v['COUNT_TOTAL'], v['COUNT_CLIENT_SAFE']))


if __name__ == '__main__':
    main()
