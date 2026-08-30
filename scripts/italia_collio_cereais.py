#!/usr/bin/env python3
"""
EXISTE UM "COLLIO DOS CEREAIS"? — a pergunta, e a resposta que a estrutura dá.

O Consorzio Collio virou o controle positivo: organização local, técnico
nomeado que assina, rede agrometeorológica própria, parcela-sentinela,
boletim semanal na estação, resolução de encosta. Tudo isso para VITE, no Friuli.

A pergunta desta rodada é se os cereais têm o mesmo. E a resposta não veio de
não encontrar: veio de uma evidência estrutural que se pode apontar.

O ÍNDICE DO PRÓPRIO ERSA
--------------------------
O serviço fitossanitário do Friuli publica boletins em oito seções — actinidia,
cimice, colture erbacee-orticole, colture orticole, melo, nocciolo, olivo, vite.
E a sub-seção `consorzi/`, onde seis consórcios publicam boletim próprio,
**existe só embaixo de `vite`**. Para as culturas herbáceas — trigo incluído —
não há camada de consórcio: a região publica sozinha.

Não é que eu não tenha achado. É que a instituição que hospedaria não abriu a
porta para cereais, e a ausência é verificável no índice dela.

POR QUE A ASSIMETRIA — e isto é HIPÓTESE, não medição
-------------------------------------------------------
Os consórcios da vinha são consórcios de DENOMINAÇÃO: território pequeno,
delimitado, valor por hectare alto, e defesa integrada amarrada à denominação.
Isso paga uma rede de estações própria e um enólogo que assina toda semana. A
cooperativa de cereais é comercial, cobre área grande e valor por hectare baixo,
e a função de monitorar fica com a região.

Registro como `STRUCTURAL_HYPOTHESIS`: explica o observado e NÃO foi medida.

O QUE OS CEREAIS TÊM, ENTÃO
-----------------------------
Uma cadeia mais curta e sem pessoa pública:

    MODELO (Horta/grano.net) ─┐
    TÉCNICO DE ASSOCIAÇÃO ────┼──▶ INSTITUIÇÃO REGIONAL ──▶ PDF
    (AIAB, não nomeado)       ┘

Contra a cadeia da vinha, que tem quatro elos e duas pessoas com nome.

    CEREAL_CHAIN_IS_SHORTER_AND_ANONYMOUS
"""
import datetime
import hashlib
import html
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import fato_local as fl          # noqa: E402
import italia_sensores_v2 as sv  # noqa: E402

DEST = os.path.join(ROOT, 'data', 'samples', 'IT-CASOS', 'IT-COLLIO-CEREAIS.json')
LAMMA = os.path.join(ROOT, 'data', 'samples', 'IT-T3-LAMMA',
                     'grosseto-ftsnt-2026-04-23.html')
EVID = os.path.join(ROOT, 'data', 'samples', 'IT-T5-SENSORES')

CASE_DATE = datetime.date(2026, 4, 23)
JANELA = (datetime.date(2026, 3, 1), datetime.date(2026, 5, 31))
TETO_ORGS, TETO_PESSOAS = 20, 30

# Checklist estrutural do padrão Collio. Não é score: é presença/ausência.
PADRAO = ('LOCAL_ORGANIZATION', 'NAMED_TECHNICIAN', 'FIELD_SEASONAL_CADENCE',
          'LOCAL_OBSERVATION', 'WEATHER_OR_PHENOLOGY', 'FACT_LOCATION',
          'FACT_TIME', 'PUBLIC_CHANNEL', 'INDEPENDENT_DETAIL')

COLLIO_EQUIVALENT = 'COLLIO_EQUIVALENT'
PARTIAL_COLLIO = 'PARTIAL_COLLIO_PATTERN'
NOT_COLLIO = 'NOT_COLLIO_PATTERN'
NOT_MEASURED = 'NOT_MEASURED'

TECHNICIAN_PUBLIC_SENSOR = 'TECHNICIAN_PUBLIC_SENSOR'
TECHNICIAN_INSIDE_ONLY = 'TECHNICIAN_INSIDE_INSTITUTION_ONLY'
TECHNICIAN_NOT_PROVED = 'TECHNICIAN_IDENTITY_NOT_PROVED'
NO_NAMED_TECHNICIAN = 'NO_NAMED_TECHNICIAN'


def _tem(*quais):
    return {p: (p in quais) for p in PADRAO}


CANDIDATOS = [
    {'NAME': 'Consorzio Collio', 'CROP': 'vite', 'REGION': 'Friuli-Venezia Giulia',
     'ENTITY_KIND': sv.ORGANIZATION, 'ROLE': 'consórcio de denominação',
     'PATTERN': _tem(*PADRAO), 'VERDICT': COLLIO_EQUIVALENT,
     'TECHNICIAN_STATE': TECHNICIAN_PUBLIC_SENSOR,
     'NAMED_PEOPLE': ['Dario Maurigh'],
     'IS_THE_CONTROL': True,
     'WHY': 'é o controle positivo — e é vinha, não cereal'},

    {'NAME': 'LaMMA / Regione Toscana — Bollettino Frumento',
     'CROP': 'frumento tenero e duro', 'REGION': 'Toscana',
     'ENTITY_KIND': sv.ORGANIZATION, 'ROLE': 'consórcio agrometeorológico regional',
     'PATTERN': _tem('FIELD_SEASONAL_CADENCE', 'LOCAL_OBSERVATION',
                     'WEATHER_OR_PHENOLOGY', 'FACT_LOCATION', 'FACT_TIME',
                     'PUBLIC_CHANNEL'),
     'VERDICT': PARTIAL_COLLIO, 'TECHNICIAN_STATE': NO_NAMED_TECHNICIAN,
     'NAMED_PEOPLE': [],
     'WHY': ('tem tudo do padrão MENOS o que o define: nenhuma pessoa assina, e não '
             'há organização local abaixo dele. É a instituição falando sozinha — e '
             'ainda assim é o melhor sinal de cereais que existe para o caso')},

    {'NAME': 'ERSA FVG — bollettini colture erbacee',
     'CROP': 'frumento, orzo, mais', 'REGION': 'Friuli-Venezia Giulia',
     'ENTITY_KIND': sv.ORGANIZATION, 'ROLE': 'serviço fitossanitário regional',
     'PATTERN': _tem('NAMED_TECHNICIAN', 'FIELD_SEASONAL_CADENCE',
                     'LOCAL_OBSERVATION', 'WEATHER_OR_PHENOLOGY', 'FACT_LOCATION',
                     'PUBLIC_CHANNEL', 'INDEPENDENT_DETAIL'),
     'VERDICT': PARTIAL_COLLIO, 'TECHNICIAN_STATE': TECHNICIAN_INSIDE_ONLY,
     'NAMED_PEOPLE': ['Maurizio Martinuzzi', 'Valentina Caron'],
     'WHY': ('nomeia técnicos, mas eles não têm canal próprio — e não há '
             'organização local abaixo. Falta o elo que o Collio tem')},

    {'NAME': 'Servizio Fitosanitario Umbria — bollettino cereali',
     'CROP': 'frumento, orzo', 'REGION': 'Umbria',
     'ENTITY_KIND': sv.ORGANIZATION, 'ROLE': 'serviço fitossanitário regional',
     'PATTERN': _tem('FIELD_SEASONAL_CADENCE', 'LOCAL_OBSERVATION',
                     'WEATHER_OR_PHENOLOGY', 'FACT_LOCATION', 'PUBLIC_CHANNEL'),
     'VERDICT': PARTIAL_COLLIO, 'TECHNICIAN_STATE': NO_NAMED_TECHNICIAN,
     'NAMED_PEOPLE': [],
     'WHY': ('a melhor resolução de cereais medida — nomeia COMUNE e sintoma — e '
             'assinada só por "Servizio Fitosanitario Regionale". Os nós da rede são '
             'AREALI, não organizações: Conca Ternana, Lago Trasimeno, Valle Umbra Sud')},

    {'NAME': "Consorzio Agrario dell'Emilia — Bollettino Tecnico",
     'CROP': 'cereali', 'REGION': 'Emilia-Romagna',
     'ENTITY_KIND': sv.ORGANIZATION, 'ROLE': 'consórcio agrário comercial',
     'PATTERN': _tem(), 'VERDICT': NOT_MEASURED,
     'TECHNICIAN_STATE': TECHNICIAN_NOT_PROVED, 'NAMED_PEOPLE': [],
     'WHY': ('o candidato mais próximo do padrão, e continua por medir: 503 em duas '
             'tentativas e, na terceira, cadeia TLS incompleta no servidor. '
             'ROUTE_TLS_CHAIN_INCOMPLETE — não é bloqueio e não se contorna '
             'desligando verificação')},

    {'NAME': "Consorzi Agrari d'Italia (CAI)", 'CROP': 'cereali', 'REGION': 'Itália',
     'ENTITY_KIND': sv.ORGANIZATION, 'ROLE': 'rede nacional de consórcios',
     'PATTERN': _tem('LOCAL_ORGANIZATION', 'PUBLIC_CHANNEL'),
     'VERDICT': NOT_COLLIO, 'TECHNICIAN_STATE': NO_NAMED_TECHNICIAN,
     'NAMED_PEOPLE': [],
     'WHY': ('publica giornate in campo, rendimento, qualidade e preço — depois do '
             'evento. ORGANIZATION_COMMUNICATION, não boletim de campo')},

    {'NAME': 'AgroAmbiente.info — Regione Toscana',
     'CROP': 'cereali e outras', 'REGION': 'Toscana',
     'ENTITY_KIND': sv.ORGANIZATION, 'ROLE': 'portal regional de dados e diagnose',
     'PATTERN': _tem('PUBLIC_CHANNEL'), 'VERDICT': NOT_MEASURED,
     'TECHNICIAN_STATE': TECHNICIAN_NOT_PROVED, 'NAMED_PEOPLE': [],
     'WHY': ('CORREÇÃO da rodada anterior: eu tinha dado esta porta como MORTA, com '
             'links de 2013 do ARSIA. Ela não morreu — MUDOU DE HOST. Está viva em '
             'agroambiente.info.regione.toscana.it, com seções Dati, Bollettini, '
             'Modelli, Diagnosi e Irrigazione, e é ela que o boletim do LaMMA linka. '
             'O conteúdo é renderizado por JavaScript e parte pede login, então segue '
             'NOT_MEASURED. DEAD_LINK ≠ DEAD_SERVICE')},
]

PESSOAS_CEREAIS = [
    {'NAME': 'Maurizio Martinuzzi', 'ORGANIZATION': 'ERSA FVG',
     'STATE': TECHNICIAN_INSIDE_ONLY, 'PUBLIC_CHANNEL': 'INSTITUTIONAL_ONLY',
     'ADDS': ['REPETITION_ONLY']},
    {'NAME': 'Valentina Caron', 'ORGANIZATION': 'ERSA FVG',
     'STATE': TECHNICIAN_INSIDE_ONLY, 'PUBLIC_CHANNEL': 'INSTITUTIONAL_ONLY',
     'ADDS': ['REPETITION_ONLY']},
    {'NAME': 'técnico AIAB (não nomeado)', 'ORGANIZATION': 'AIAB',
     'STATE': TECHNICIAN_NOT_PROVED, 'PUBLIC_CHANNEL': 'NOT_FOUND',
     'ADDS': ['INDEPENDENT_CONFIRMATION'],
     'WHY': ('o boletim do ERSA cita "Fonte: tecnico AIAB" ao lado do modelo Horta. '
             'Uma pessoa de campo alimenta o boletim oficial de cereais — e não tem '
             'nome. É o elo do Collio, sem a atribuição que o tornaria um sensor')},
]


def ler_lamma():
    with open(LAMMA, encoding='utf-8', errors='replace') as fh:
        bruto = fh.read()
    texto = html.unescape(re.sub(r'<[^>]+>', ' ',
                                 re.sub(r'<script.*?</script>|<style.*?</style>',
                                        '', bruto, flags=re.S)))
    texto = re.sub(r'\s+', ' ', texto).split('Bollettino Vite')[0]
    aceitas, recusadas = fl.localizacoes_do_fato(texto, origem='IT-T3-LAMMA/2026-04-23')
    return {
        'ID': 'IT-T3-LAMMA/2026-04-23',
        'EVIDENCE_PATH': 'data/samples/IT-T3-LAMMA/grosseto-ftsnt-2026-04-23.html',
        'SHA256': hashlib.sha256(bruto.encode('utf-8')).hexdigest(),
        'PUBLISHED_AT': '2026-04-23', 'CROP': 'frumento duro e tenero',
        'ISSUE': 'fusariosi, septoria, ruggini, oidio',
        'DOCUMENT_SCOPE': fl.escopo_do_documento(texto),
        'FACT_LOCATIONS': aceitas,
        'PLACE_MENTIONS_REJECTED': [{'PLACE': r['PLACE'], 'WHY': r['WHY']}
                                    for r in recusadas],
        'TIME': fl.tempo_do_fato(texto, '2026-04-23'),
        'OCCURRENCE_NOT_INCIDENCE': fl.ocorrencia_nao_e_incidencia(
            [a['TYPE_OF_EVIDENCE'] for a in aceitas]),
        'SUB_PROVINCIAL_QUALIFIER': (
            'o boletim separa "area nord" e "area sud" da província e dá fenologia '
            'diferente para cada uma. É zona agronômica, não unidade administrativa, '
            'e por isso NÃO vira FACT_LOCATION: fica como qualificador'),
        'SEPARATES_OBSERVATION_FROM_MODEL': (
            'a própria fonte separa: "Si segnala la comparsa di sintomi lievi nel '
            'frumento duro" e, em parágrafo próprio, "Rischio fusariosi da modello"'),
    }


def medir():
    lamma = ler_lamma()
    equivalentes = [c for c in CANDIDATOS
                    if c['VERDICT'] == COLLIO_EQUIVALENT and not c.get('IS_THE_CONTROL')]
    parciais = [c for c in CANDIDATOS if c['VERDICT'] == PARTIAL_COLLIO]
    cereais = [c for c in CANDIDATOS if 'vite' not in c['CROP']]
    publicos = [p for p in PESSOAS_CEREAIS if p['STATE'] == TECHNICIAN_PUBLIC_SENSOR]

    achou = 'YES' if equivalentes else ('PARTIAL' if parciais else 'NO')
    para_duro = 'NO' if not equivalentes else 'YES'

    return {
        'QUESTION_ID': 'CEREAL_COLLIO_EQUIVALENT',
        'CASE_ID': 'IT-CASE-DURUM-FUSARIUM-001',
        'SOURCE_ID': 'DERIVED/IT-COLLIO-CEREAIS',
        'source': 'busca dirigida a partir dos faróis — nenhuma execução paga',
        'SOURCE_LOCATION': 'web pública italiana',
        'FACT_LOCATION': 'ver CASE_FIELD_LEG — por conteúdo, nunca por voz',
        'ORIGINAL_LANGUAGE': 'it', 'EVIDENCE_CLASS': 'PRIMARY_SOURCE_PROBE',
        'captured_at': datetime.date.today().isoformat(),
        'CAPTURED_AT': datetime.date.today().isoformat(),
        'CASE_DATE': CASE_DATE.isoformat(),
        'WINDOW': [JANELA[0].isoformat(), JANELA[1].isoformat()],
        'APIFY_RUNS': 0, 'APIFY_COST_USD': 0,

        'PRODUCER_CORRECTION': (
            'PROSPECTIVE_PRODUCER_SENSOR = PROVED vinha do Consorzio Collio, que é '
            'ORGANIZAÇÃO. Cooperativa é classe válida de organização e não substitui '
            'produtor-pessoa. Separado em PRODUCER_COOP e PRODUCER_PERSON, e o '
            'segundo é NOT_PROVED: nenhuma pessoa física produtora foi medida'),

        'CAPS': {'ORGANIZATIONS': TETO_ORGS, 'PERSONS': TETO_PESSOAS,
                 'NOTE': 'parou muito antes — o padrão fechou'},
        'CANDIDATES': CANDIDATOS, 'CANDIDATES_COUNT': len(CANDIDATOS),
        'CEREAL_CANDIDATES_COUNT': len(cereais),
        'PERSONS_IN_CEREAL_CHAIN': PESSOAS_CEREAIS,

        'STRUCTURAL_EVIDENCE': {
            'FINDING': 'CONSORTIUM_LAYER_EXISTS_ONLY_FOR_VINE',
            'HOW_MEASURED': ('o índice de boletins do ERSA tem oito seções, e a '
                             'sub-seção consorzi/ — onde seis consórcios publicam '
                             'boletim próprio — existe só embaixo de vite'),
            'SECTIONS': ['actinidia', 'cimice-marmorata-asiatica', 'colture-erbacee-orticole',
                         'colture-orticole', 'melo', 'nocciolo', 'olivo', 'vite'],
            'CONSORTIUM_SLOT_UNDER': ['vite'],
            'WHY_THIS_MATTERS': ('não é ausência de busca: é ausência verificável no '
                                 'índice da própria instituição que hospedaria'),
        },
        'STRUCTURAL_HYPOTHESIS': {
            'STATEMENT': ('consórcio de denominação — território pequeno, delimitado e '
                          'de alto valor por hectare — sustenta rede própria e técnico '
                          'que assina toda semana. Cooperativa de cereais é comercial, '
                          'cobre área grande com valor baixo por hectare, e a função de '
                          'monitorar fica com a região'),
            'STATE': 'NOT_MEASURED — explica o observado e não foi testada',
        },

        'CEREAL_CHAIN': {
            'SHAPE': 'MODELO + TÉCNICO DE ASSOCIAÇÃO (anônimo) → INSTITUIÇÃO → PDF',
            'VS_VINE_CHAIN': 'OBSERVADOR CIDADÃO → TÉCNICO NOMEADO → CONSÓRCIO → INSTITUIÇÃO',
            'LINKS_MISSING': ['organização local abaixo da região',
                             'técnico com canal público próprio',
                             'observador citado nominalmente'],
        },

        'CASE_FIELD_LEG': lamma,
        'CREATOR_CITED_BY_TECHNICAL_CHAIN': {
            'IN_VINE': 'Lorenzo Ghiraldelli — "Pazzi per il Meteo Goriziano"',
            'IN_CEREALS': 'NOT_FOUND_IN_THIS_SEARCH',
            'WHY': ('nenhum boletim de cereais lido cita observador externo nomeado. '
                    'O único elo externo é "tecnico AIAB", sem nome'),
        },

        'TIMELINE': {
            'FIRST_HUMAN_OBSERVATION': 'NOT_OBSERVED — nenhuma pessoa nomeada na cadeia de cereais',
            'FIRST_LOCAL_ORGANIZATION_SIGNAL': 'NOT_OBSERVED — não há camada local',
            'FIRST_REGIONAL_INSTITUTION_SIGNAL': '2026-04-23 (LaMMA, Grosseto)',
            'CASE_DATE': '2026-04-23',
            'ANTICIPATION': ('ZERO dias. O sinal institucional e o caso são o MESMO '
                             'documento e a MESMA data — não há antecedência a medir, '
                             'e inventá-la seria o pior erro possível aqui'),
        },

        'ADDS_OVER_REGIONAL_BASELINE': {
            'EARLIER_THAN_INSTITUTION': [],
            'MORE_LOCAL_THAN_INSTITUTION': [],
            'FIELD_DETAIL': ['Umbria — comune e sintoma'],
            'INDEPENDENT_CONFIRMATION': ['técnico AIAB (anônimo), no boletim do ERSA'],
            'REPETITION_ONLY': ['Maurizio Martinuzzi', 'Valentina Caron'],
        },

        'LAWS': [
            'PRODUCER_COOP_ORGANIZATION ≠ PRODUCER_PERSON',
            'CONSORTIUM_LAYER_EXISTS_ONLY_FOR_VINE (medido no índice do ERSA)',
            'DEAD_LINK ≠ DEAD_SERVICE',
            'ROUTE_TLS_CHAIN_INCOMPLETE ≠ NO_SIGNAL',
            'DOCUMENT_SCOPE ≠ IN_SENTENCE_ANCHOR',
            'AGRONOMIC_ZONE ≠ ADMIN_UNIT',
            'SAME_DATE ≠ ANTICIPATION',
        ],

        'CEREAL_COLLIO_EQUIVALENT_FOUND': achou,
        'EXISTS_FOR_DURUM_FUSARIUM': para_duro,
        'EXISTS_FOR_DURUM_FUSARIUM_WHY': (
            'para grano duro × fusariosi o melhor sinal é o boletim do LaMMA, que é '
            'institucional, não tem pessoa assinando e não tem camada local abaixo. '
            'É PARTIAL_COLLIO_PATTERN, não equivalente'),

        'PROSPECTIVE_INSTITUTIONAL_FIELD_SENSOR': {
            'STATE': 'PROVED', 'CROP_SCOPE': 'frumento, orzo, mais',
            'GEOGRAPHIC_SCOPE': 'FVG, Veneto, Umbria, Toscana'},
        'PROSPECTIVE_TECHNICAL_PERSON_SENSOR': {
            'STATE': 'PROVED', 'CROP_SCOPE': 'vite — NÃO cereais',
            'GEOGRAPHIC_SCOPE': 'Friuli-Venezia Giulia — NÃO Toscana'},
        'PROSPECTIVE_PRODUCER_COOP_SENSOR': {
            'STATE': 'PROVED', 'CROP_SCOPE': 'vite — NÃO cereais',
            'GEOGRAPHIC_SCOPE': 'Friuli-Venezia Giulia'},
        'PROSPECTIVE_PRODUCER_PERSON_SENSOR': {
            'STATE': 'NOT_PROVED', 'CROP_SCOPE': 'nenhuma',
            'GEOGRAPHIC_SCOPE': 'nenhuma'},
        'PROSPECTIVE_CREATOR_SENSOR': {
            'STATE': 'PROMISING', 'CROP_SCOPE': 'vite (meteorologia) — NÃO cereais',
            'GEOGRAPHIC_SCOPE': 'goriziano'},
        'PROSPECTIVE_RESEARCHER_SENSOR': {
            'STATE': 'NOT_PROVED', 'CROP_SCOPE': 'nenhuma',
            'GEOGRAPHIC_SCOPE': 'nenhuma'},
        'PROSPECTIVE_HUMAN_PERSON_SENSOR': {
            'STATE': 'PROVED', 'CROP_SCOPE': 'vite — NÃO grano duro',
            'GEOGRAPHIC_SCOPE': 'Friuli — NÃO Toscana',
            'MUST_CARRY': 'prova a CLASSE, não o caso'},
        'PROSPECTIVE_HUMAN_PERSON_SENSOR_FOR_CEREALS': {
            'STATE': 'NOT_PROVED', 'CROP_SCOPE': 'frumento, grano duro',
            'GEOGRAPHIC_SCOPE': 'Toscana, Umbria, FVG',
            'WHY': 'nenhuma pessoa com canal público próprio na cadeia de cereais'},

        'RECOMMENDATION': {
            'COLLECT_RECURRENTLY': (
                'a camada institucional regional de cereais — LaMMA Toscana, ERSA FVG, '
                'Umbria, Veneto. É a única que publica na janela para trigo, e a '
                'única que cobre a região e a data do caso'),
            'WHY': ('a camada humana pessoal de cereais não existe como sensor público. '
                    'Esperar por ela seria esperar por algo que a estrutura do setor '
                    'não produz'),
            'DO_NOT_EXPECT': 'antecedência sobre o boletim regional em cereais',
            'WHERE_THE_PERSON_LAYER_EXISTS': (
                'vinha, e lá vale coletar: consórcio + técnico nomeado + observador '
                'cidadão, com resolução de encosta'),
            'STILL_UNMEASURED': [
                "Consorzio Agrario dell'Emilia — TLS incompleto, 3 tentativas",
                'AgroAmbiente.info Toscana — JS e login, porta VIVA e não medida',
                'os cinco outros consórcios de vinha do índice do ERSA',
                'se algum consórcio de cereais do sul (Puglia, Basilicata) publica boletim'],
        },
        'STILL_FORBIDDEN_TO_WRITE': ['ITALY OPPORTUNITY', 'SALES OPPORTUNITY',
                                     'ADAMA SHOULD ACT', 'MARKET GAP'],
    }


def main():
    out = medir()
    os.makedirs(os.path.dirname(DEST), exist_ok=True)
    with open(DEST, 'w', encoding='utf-8') as fh:
        json.dump(out, fh, ensure_ascii=False, indent=2)
    print('candidatos:', out['CANDIDATES_COUNT'], '| de cereais:', out['CEREAL_CANDIDATES_COUNT'])
    for c in out['CANDIDATES']:
        faltam = [p for p, v in c['PATTERN'].items() if not v]
        print('   %-46s %-24s falta: %s' % (c['NAME'][:46], c['VERDICT'],
                                            ', '.join(faltam[:3]) or '—'))
    print()
    print('evidencia estrutural:', out['STRUCTURAL_EVIDENCE']['FINDING'])
    print('   slot de consorzi embaixo de:', out['STRUCTURAL_EVIDENCE']['CONSORTIUM_SLOT_UNDER'])
    fl_ = out['CASE_FIELD_LEG']
    print('perna de campo do caso:', fl_['PUBLISHED_AT'])
    for a in fl_['FACT_LOCATIONS']:
        print('   FACT %-12s %-10s %-15s %s' % (a['FACT_LOCATION'],
              a['FACT_LOCATION_PRECISION'], a['PRECISION_SOURCE'], a['TYPE_OF_EVIDENCE']))
    print()
    print('CEREAL_COLLIO_EQUIVALENT_FOUND =', out['CEREAL_COLLIO_EQUIVALENT_FOUND'])
    print('EXISTS_FOR_DURUM_FUSARIUM      =', out['EXISTS_FOR_DURUM_FUSARIUM'])
    print()
    for k in ('PROSPECTIVE_INSTITUTIONAL_FIELD_SENSOR',
              'PROSPECTIVE_TECHNICAL_PERSON_SENSOR', 'PROSPECTIVE_PRODUCER_COOP_SENSOR',
              'PROSPECTIVE_PRODUCER_PERSON_SENSOR', 'PROSPECTIVE_CREATOR_SENSOR',
              'PROSPECTIVE_RESEARCHER_SENSOR', 'PROSPECTIVE_HUMAN_PERSON_SENSOR',
              'PROSPECTIVE_HUMAN_PERSON_SENSOR_FOR_CEREALS'):
        v = out[k]
        print('   %-44s %-11s %s' % (k, v['STATE'], v['CROP_SCOPE']))
    print('->', os.path.relpath(DEST, ROOT))


if __name__ == '__main__':
    main()
