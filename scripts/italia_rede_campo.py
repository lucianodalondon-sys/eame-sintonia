#!/usr/bin/env python3
"""
ITALY_FIELD_SENSOR_NETWORK_V1 — quem está perto de quem, e quem acrescenta o quê.

A rodada anterior publicou `PROSPECTIVE_HUMAN_SENSOR = PROVED`. Estava errado, e
o erro era meu: as cinco vozes prospectivas eram cinco ORGANIZAÇÕES. Faltava o
campo que separa pessoa de instituição, e sem ele promovi uma na outra.

    INSTITUTIONAL_SIGNAL ≠ HUMAN_PERSON_SIGNAL

Esta rodada não abriu busca nova. Foi procurar AO REDOR dos quatro faróis que já
tinham sinal prospectivo provado — e a rede que apareceu tem uma forma clara:

    OBSERVADOR CIDADÃO  →  TÉCNICO NOMEADO  →  CONSÓRCIO  →  INSTITUIÇÃO REGIONAL
    (meteo, Telegram)      (agrônomo/enólogo)  (rede própria)  (boletim oficial)

O TESTE NÃO É "A PESSOA FALOU?"
---------------------------------
É: **a pessoa acrescentou algo que o boletim institucional não tinha?**

O agrônomo do Consorzio Collio acrescenta uma coisa que nenhuma instituição
regional tem: chuva medida em VINTE localidades nomeadas, da própria rede de
estações do consórcio. O boletim do ERSA fala da região; ele fala de Dolegna
(199 mm) e de Pradis (70 mm) na mesma semana. Isso é `MORE_LOCAL_THAN_INSTITUTION`
por uma ordem de grandeza.

E A CULTURA NÃO É A DO CASO
-----------------------------
O sinal humano prospectivo mais forte que existe nesta medição é sobre VITE, no
Friuli — não sobre grano duro na Toscana. Isso prova a CLASSE, não o caso.
Confundir as duas coisas seria o mesmo tipo de promoção que esta rodada veio
corrigir.

    CLASS_PROVED_ON_ANOTHER_CROP ≠ CASE_SIGNAL
"""
import datetime
import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import fato_local as fl          # noqa: E402
import italia_sensores_v2 as sv  # noqa: E402

DEST = os.path.join(ROOT, 'data', 'samples', 'IT-CASOS', 'IT-REDE-CAMPO-V1.json')
EVID = os.path.join(ROOT, 'data', 'samples', 'IT-T5-SENSORES')

CASE_DATE = datetime.date(2026, 4, 23)
JANELA = (datetime.date(2026, 3, 1), datetime.date(2026, 5, 31))
TETO_NOVOS = 30

# O diferencial humano — §3. Não é "falou", é "acrescentou".
EARLIER = 'EARLIER_THAN_INSTITUTION'
MORE_LOCAL = 'MORE_LOCAL_THAN_INSTITUTION'
FIELD_DETAIL = 'FIELD_DETAIL'
SYMPTOM_DETAIL = 'SYMPTOM_DETAIL'
PRODUCER_LANGUAGE = 'PRODUCER_LANGUAGE'
PHENOLOGY_DETAIL = 'PHENOLOGY_DETAIL'
WEATHER_CONCERN = 'WEATHER_CONCERN'
MANAGEMENT_CONTEXT = 'MANAGEMENT_CONTEXT'
INDEPENDENT_CONFIRMATION = 'INDEPENDENT_CONFIRMATION'
REPETITION_ONLY = 'REPETITION_ONLY'
NO_SIGNAL = 'NO_SIGNAL'

# ------------------------------------------------------------- os baselines
BASELINES = [
    {'ID': 'BASE/ERSA-FVG-07',
     'SOURCE': 'ERSA FVG — Bollettino difesa integrata frumento-orzo n.7',
     'ENTITY_KIND': sv.ORGANIZATION, 'DATE': '2026-04-20',
     'CROP': 'frumento/orzo', 'ISSUE': 'septoriosi, ruggine bruna',
     'FACT_LOCATION': 'Friuli-Venezia Giulia', 'FACT_LOCATION_PRECISION': fl.REGION,
     'FACT_TIME': 'NOT_KNOWN',
     'SIGNAL_TYPE': ['PHENOLOGY_OBSERVATION', 'MODELLED_RISK', 'FIELD_OBSERVATION'],
     'EVIDENCE': ('"dai rilievi in campo è emerso che in alcune zone della media e '
                  "dell'alta pianura si osservano dei sintomi evidenti della patologia\""),
     'CADENCE': 'WEEKLY_IN_SEASON'},
    {'ID': 'BASE/VENETO-2026',
     'SOURCE': 'Regione Veneto — bollettini fitosanitari 2026',
     'ENTITY_KIND': sv.ORGANIZATION, 'DATE': '2026-03-04..2026-08-05',
     'CROP': 'cereali, mais', 'ISSUE': 'difesa integrata',
     'FACT_LOCATION': 'NOT_READ', 'FACT_LOCATION_PRECISION': fl.NOT_KNOWN,
     'FACT_TIME': 'NOT_KNOWN', 'SIGNAL_TYPE': ['NOT_READ'],
     'EVIDENCE': '53 datas distintas em 2026 — cadência medida, conteúdo não lido',
     'CADENCE': 'WEEKLY_IN_SEASON'},
    {'ID': 'BASE/UMBRIA-CEREALI',
     'SOURCE': 'Servizio Fitosanitario Regionale Umbria — bollettino cereali',
     'ENTITY_KIND': sv.ORGANIZATION, 'DATE': 'NOT_DATED_IN_TEXT',
     'CROP': 'frumento/orzo', 'ISSUE': 'septoriosi, fusariosi della spiga',
     'FACT_LOCATION': 'Branca di Gubbio; Parrano',
     'FACT_LOCATION_PRECISION': fl.MUNICIPALITY, 'FACT_TIME': 'NOT_KNOWN',
     'SIGNAL_TYPE': ['FIELD_OBSERVATION', 'SYMPTOM_OBSERVATION', 'TECHNICAL_WARNING'],
     'EVIDENCE': ('"lieve attacco di Septoriosi nei Comuni di Branca di Gubbio"; '
                  '"presenza media di Septoriosi nel Comune di Parrano"'),
     'CADENCE': 'WEEKLY_IN_SEASON'},
    {'ID': 'BASE/LAMMA-TOSCANA',
     'SOURCE': 'LaMMA / Regione Toscana — Bollettino Frumento',
     'ENTITY_KIND': sv.ORGANIZATION, 'DATE': '2026-04-23',
     'CROP': 'frumento', 'ISSUE': 'fusariosi', 'FACT_LOCATION': 'Grosseto',
     'FACT_LOCATION_PRECISION': fl.PROVINCE, 'FACT_TIME': '2026-04-23',
     'SIGNAL_TYPE': ['PHENOLOGY_OBSERVATION', 'MODELLED_RISK'],
     'EVIDENCE': 'preservado em missão anterior — é a perna de campo do caso',
     'CADENCE': 'WEEKLY_IN_SEASON'},
]

# ---------------------------------------------------- as pessoas ao redor
# Nenhum nome novo veio de busca genérica: todos saíram de DENTRO dos boletins
# dos quatro faróis, ou do índice que o próprio ERSA publica.
PESSOAS = [
    {'NAME': 'Dario Maurigh', 'ENTITY_KIND': sv.PERSON,
     'CLASS': sv.TECHNICAL_FIELD_VOICE, 'ROLE': 'enólogo, cura o boletim do consórcio',
     'ORGANIZATION': 'Consorzio Collio', 'SOURCE_LOCATION': 'Gorizia, FVG',
     'OPERATING_GEOGRAPHY': 'zona D.O.C. Collio', 'CROPS': ['vite'],
     'PUBLIC_CHANNELS': ['Bollettino fitosanitario Collio (PDF, hospedado pelo ERSA)',
                         'Avviso di trattamento BIO', 'Avviso Produzione Integrata'],
     'PRIMARY_PUBLIC_CHANNEL': 'Bollettino fitosanitario do Consorzio Collio',
     'ACTIVE_2026': 'YES', 'LAST_OBSERVED_CONTENT_DATE': '2026-08-03',
     'CADENCE': sv.FIELD_SEASONAL, 'SENSOR_POTENTIAL': sv.PROSPECTIVE_SENSOR,
     'LINKED_TO': ['BASE/ERSA-FVG-07'],
     'ADDS': [MORE_LOCAL, FIELD_DETAIL, SYMPTOM_DETAIL, PHENOLOGY_DETAIL,
              WEATHER_CONCERN, MANAGEMENT_CONTEXT, INDEPENDENT_CONFIRMATION],
     'WHY': ('assina o boletim com nome. O consórcio opera REDE PRÓPRIA de estações '
             'agrometeorológicas e ele publica chuva em vinte localidades nomeadas na '
             'mesma semana — Dolegna 199 mm, Pradis 70 mm. A instituição regional fala '
             'da região; ele fala da encosta. Mantém parcela-sentinela não tratada em '
             'Plessiva e relata o que aparece nela')},
    {'NAME': 'Maurizio Martinuzzi', 'ENTITY_KIND': sv.PERSON,
     'CLASS': sv.TECHNICAL_FIELD_VOICE, 'ROLE': 'técnico, seção cerealicoltura',
     'ORGANIZATION': 'ERSA FVG — Servizio fitosanitario e chimico',
     'SOURCE_LOCATION': 'Friuli-Venezia Giulia', 'OPERATING_GEOGRAPHY': 'FVG',
     'CROPS': ['frumento', 'orzo'],
     'PUBLIC_CHANNELS': ['assina como contato técnico do boletim ERSA'],
     'PRIMARY_PUBLIC_CHANNEL': 'INSTITUTIONAL_CHANNEL_ONLY',
     'ACTIVE_2026': 'YES', 'LAST_OBSERVED_CONTENT_DATE': '2026-04-20',
     'CADENCE': sv.FIELD_SEASONAL, 'SENSOR_POTENTIAL': sv.CONTEXT_SENSOR,
     'LINKED_TO': ['BASE/ERSA-FVG-07'], 'ADDS': [REPETITION_ONLY],
     'WHY': ('a pessoa existe e é a certa, mas não tem voz pública própria: o sinal '
             'sai pelo boletim da instituição. PERSON_INSIDE_INSTITUTION ≠ '
             'PERSON_AS_PUBLIC_SENSOR')},
    {'NAME': 'Valentina Caron', 'ENTITY_KIND': sv.PERSON,
     'CLASS': sv.TECHNICAL_FIELD_VOICE, 'ROLE': 'técnica, seção cerealicoltura',
     'ORGANIZATION': 'ERSA FVG — Servizio fitosanitario e chimico',
     'SOURCE_LOCATION': 'Friuli-Venezia Giulia', 'OPERATING_GEOGRAPHY': 'FVG',
     'CROPS': ['frumento', 'orzo'],
     'PUBLIC_CHANNELS': ['assina como contato técnico do boletim ERSA'],
     'PRIMARY_PUBLIC_CHANNEL': 'INSTITUTIONAL_CHANNEL_ONLY',
     'ACTIVE_2026': 'YES', 'LAST_OBSERVED_CONTENT_DATE': '2026-04-20',
     'CADENCE': sv.FIELD_SEASONAL, 'SENSOR_POTENTIAL': sv.CONTEXT_SENSOR,
     'LINKED_TO': ['BASE/ERSA-FVG-07'], 'ADDS': [REPETITION_ONLY],
     'WHY': 'mesma situação: nomeada no boletim, sem canal público próprio'},
    {'NAME': 'Lorenzo Ghiraldelli — "Pazzi per il Meteo Goriziano"',
     'ENTITY_KIND': sv.PERSON, 'CLASS': sv.CREATOR_INFLUENCER,
     'ROLE': 'observador meteorológico cidadão',
     'ORGANIZATION': 'independente / rede Pretemp, MeteoNetwork',
     'SOURCE_LOCATION': 'Gorizia, FVG', 'OPERATING_GEOGRAPHY': 'goriziano, isontino',
     'CROPS': ['n/a — meteorologia'],
     'PUBLIC_CHANNELS': ['canal Telegram', 'página Facebook', 'Storm Report Italia'],
     'PRIMARY_PUBLIC_CHANNEL': 'canal Telegram',
     'ACTIVE_2026': 'YES', 'LAST_OBSERVED_CONTENT_DATE': '2026-05-14',
     'CADENCE': 'EVENT_DRIVEN', 'SENSOR_POTENTIAL': sv.PROSPECTIVE_SENSOR,
     'LINKED_TO': ['BASE/ERSA-FVG-07'],
     'ADDS': [EARLIER, MORE_LOCAL, WEATHER_CONCERN, INDEPENDENT_CONFIRMATION],
     'WHY': ('o achado mais inesperado da rodada: um creator de meteorologia é CITADO '
             'COMO FONTE dentro do boletim técnico do consórcio. O relato de granizo de '
             '14/05 — "fino a 5-8 eventi ravvicinati" sobre a Bassa orientale, o '
             'cormonese, o isontino e o goriziano — entrou na cadeia técnica pela porta '
             'do Telegram. CREATOR ≠ SENSOR continua valendo como regra; este é o '
             'contraexemplo que a regra tem de admitir')},
]

ORGANIZACOES_NOVAS = [
    {'NAME': 'Consorzio Collio', 'ENTITY_KIND': sv.ORGANIZATION,
     'CLASS': sv.PRODUCER_COOP_VOICE, 'CADENCE': sv.FIELD_SEASONAL,
     'SENSOR_POTENTIAL': sv.PROSPECTIVE_SENSOR, 'ACTIVE_2026': 'YES',
     'LAST_OBSERVED_CONTENT_DATE': '2026-08-03',
     'ADDS': [MORE_LOCAL, FIELD_DETAIL, WEATHER_CONCERN],
     'WHY': ('opera rede própria de estações agrometeorológicas e publica boletim '
             'numerado n.06 a n.16 em 2026, mais avisos de tratamento separados para '
             'BIO e Produção Integrada. É PRODUCER_FIELD_REPORT, não '
             'ORGANIZATION_COMMUNICATION')},
    {'NAME': 'Consorzi Aquileia, Latisana, Annia', 'ENTITY_KIND': sv.ORGANIZATION,
     'CLASS': sv.PRODUCER_COOP_VOICE, 'CADENCE': sv.FIELD_SEASONAL,
     'SENSOR_POTENTIAL': sv.PROSPECTIVE_SENSOR, 'ACTIVE_2026': 'NOT_KNOWN',
     'LAST_OBSERVED_CONTENT_DATE': 'NOT_KNOWN', 'ADDS': ['NOT_MEASURED'],
     'WHY': 'consta do índice de boletins de consórcio do ERSA; conteúdo não lido'},
    {'NAME': 'Consorzio Isonzo', 'ENTITY_KIND': sv.ORGANIZATION,
     'CLASS': sv.PRODUCER_COOP_VOICE, 'CADENCE': sv.FIELD_SEASONAL,
     'SENSOR_POTENTIAL': sv.PROSPECTIVE_SENSOR, 'ACTIVE_2026': 'NOT_KNOWN',
     'LAST_OBSERVED_CONTENT_DATE': 'NOT_KNOWN', 'ADDS': ['NOT_MEASURED'],
     'WHY': 'idem'},
    {'NAME': 'Consorzio Grave', 'ENTITY_KIND': sv.ORGANIZATION,
     'CLASS': sv.PRODUCER_COOP_VOICE, 'CADENCE': sv.FIELD_SEASONAL,
     'SENSOR_POTENTIAL': sv.PROSPECTIVE_SENSOR, 'ACTIVE_2026': 'NOT_KNOWN',
     'LAST_OBSERVED_CONTENT_DATE': 'NOT_KNOWN', 'ADDS': ['NOT_MEASURED'],
     'WHY': 'idem'},
    {'NAME': 'Consorzio Colli orientali', 'ENTITY_KIND': sv.ORGANIZATION,
     'CLASS': sv.PRODUCER_COOP_VOICE, 'CADENCE': sv.FIELD_SEASONAL,
     'SENSOR_POTENTIAL': sv.PROSPECTIVE_SENSOR, 'ACTIVE_2026': 'NOT_KNOWN',
     'LAST_OBSERVED_CONTENT_DATE': 'NOT_KNOWN', 'ADDS': ['NOT_MEASURED'],
     'WHY': 'idem'},
    {'NAME': 'Consorzio Carso', 'ENTITY_KIND': sv.ORGANIZATION,
     'CLASS': sv.PRODUCER_COOP_VOICE, 'CADENCE': sv.FIELD_SEASONAL,
     'SENSOR_POTENTIAL': sv.PROSPECTIVE_SENSOR, 'ACTIVE_2026': 'NOT_KNOWN',
     'LAST_OBSERVED_CONTENT_DATE': 'NOT_KNOWN', 'ADDS': ['NOT_MEASURED'],
     'WHY': 'idem'},
    {'NAME': 'AIAB — técnico citado como fonte no boletim ERSA',
     'ENTITY_KIND': sv.ORGANIZATION, 'CLASS': sv.TECHNICAL_FIELD_VOICE,
     'CADENCE': sv.CADENCE_NOT_KNOWN, 'SENSOR_POTENTIAL': sv.POTENTIAL_NOT_KNOWN,
     'ACTIVE_2026': 'YES', 'LAST_OBSERVED_CONTENT_DATE': '2026-04-20',
     'ADDS': [INDEPENDENT_CONFIRMATION],
     'WHY': ('o boletim do ERSA cita "Fonte: tecnico AIAB" ao lado da fonte do modelo '
             'Horta — uma associação de agricultura biológica alimentando o boletim '
             'oficial com dado de campo. O técnico não é nomeado')},
    {'NAME': 'OSMER ARPA FVG', 'ENTITY_KIND': sv.ORGANIZATION,
     'CLASS': sv.INSTITUTIONAL_FIELD_VOICE, 'CADENCE': 'DAILY',
     'SENSOR_POTENTIAL': sv.CONTEXT_SENSOR, 'ACTIVE_2026': 'YES',
     'LAST_OBSERVED_CONTENT_DATE': '2026-05-15', 'ADDS': [WEATHER_CONCERN],
     'WHY': 'previsão meteorológica citada pelos dois boletins, o do ERSA e o do Collio'},
]

LEITURAS = [
    {'ID': 'COLLIO/BOLL-06-2026',
     'ARQUIVO': 'collio-boll-06-vite-2026-05-15.txt',
     'AUTHOR': 'Dario Maurigh', 'AUTHOR_KIND': sv.PERSON,
     'ORGANIZATION': 'Consorzio Collio', 'PUBLISHED_AT': '2026-05-15',
     'CROP': 'vite', 'ISSUE': 'peronospora, oidio, scaphoideus, giallumi',
     'BASELINE': 'BASE/ERSA-FVG-07',
     'RELATION_TO_BASELINE': 'AFTER_BASELINE',
     'ADDS': [MORE_LOCAL, FIELD_DETAIL, SYMPTOM_DETAIL, PHENOLOGY_DETAIL,
              WEATHER_CONCERN, MANAGEMENT_CONTEXT, INDEPENDENT_CONFIRMATION]},
    {'ID': 'ERSA-FVG/BOLL-07-2026',
     'ARQUIVO': 'ersa-fvg-boll-07-frumento-orzo-2026-04-20.txt',
     'AUTHOR': 'ERSA FVG', 'AUTHOR_KIND': sv.ORGANIZATION,
     'ORGANIZATION': 'ERSA FVG', 'PUBLISHED_AT': '2026-04-20',
     'CROP': 'frumento/orzo', 'ISSUE': 'septoriosi, ruggine bruna',
     'BASELINE': 'BASE/ERSA-FVG-07', 'RELATION_TO_BASELINE': 'IS_THE_BASELINE',
     'ADDS': ['IS_THE_BASELINE']},
    {'ID': 'UMBRIA/BOLL-CEREALI',
     'ARQUIVO': 'umbria-boll-cereali-04-servizio-fitosanitario.txt',
     'AUTHOR': 'Servizio Fitosanitario Regionale Umbria',
     'AUTHOR_KIND': sv.ORGANIZATION, 'ORGANIZATION': 'Regione Umbria',
     'PUBLISHED_AT': None, 'CROP': 'frumento/orzo',
     'ISSUE': 'septoriosi, fusariosi', 'BASELINE': 'BASE/UMBRIA-CEREALI',
     'RELATION_TO_BASELINE': 'IS_THE_BASELINE', 'ADDS': ['IS_THE_BASELINE']},
]


def ler():
    fora = []
    for L in LEITURAS:
        reg = dict(L)
        caminho = os.path.join(EVID, L['ARQUIVO'])
        with open(caminho, encoding='utf-8') as fh:
            texto = fh.read()
        reg['EVIDENCE_PATH'] = 'data/samples/IT-T5-SENSORES/' + L['ARQUIVO']
        reg['SHA256'] = hashlib.sha256(texto.encode('utf-8')).hexdigest()
        aceitas, recusadas = fl.localizacoes_do_fato(texto, origem=L['ID'])
        reg['FACT_LOCATIONS'] = aceitas
        reg['PLACE_MENTIONS_REJECTED'] = [{'PLACE': r['PLACE'], 'WHY': r['WHY'],
                                           'STATE': r['STATE']} for r in recusadas]
        reg['TIME'] = fl.tempo_do_fato(texto, L['PUBLISHED_AT'])
        reg['OCCURRENCE_NOT_INCIDENCE'] = fl.ocorrencia_nao_e_incidencia(
            [a['TYPE_OF_EVIDENCE'] for a in aceitas])
        fora.append(reg)
    return fora


def medir():
    leituras = ler()
    novos = PESSOAS + ORGANIZACOES_NOVAS
    pessoas_prosp = [p for p in PESSOAS
                     if p['SENSOR_POTENTIAL'] == sv.PROSPECTIVE_SENSOR]
    tecnicos_prosp = [p for p in pessoas_prosp if p['CLASS'] == sv.TECHNICAL_FIELD_VOICE]
    creators_prosp = [p for p in pessoas_prosp if p['CLASS'] == sv.CREATOR_INFLUENCER]
    produtores_pessoa = [p for p in PESSOAS
                         if p['CLASS'] == sv.PRODUCER_COOP_VOICE
                         and p['ENTITY_KIND'] == sv.PERSON
                         and p['SENSOR_POTENTIAL'] == sv.PROSPECTIVE_SENSOR]
    coops_prosp = [o for o in ORGANIZACOES_NOVAS
                   if o['CLASS'] == sv.PRODUCER_COOP_VOICE
                   and o['SENSOR_POTENTIAL'] == sv.PROSPECTIVE_SENSOR
                   and o['ACTIVE_2026'] == 'YES']

    def acrescentos(rotulo):
        return [L['ID'] for L in LEITURAS if rotulo in L['ADDS']]

    fatos = [a for L in leituras for a in L['FACT_LOCATIONS']]
    por_tipo = {}
    for a in fatos:
        por_tipo.setdefault(a['TYPE_OF_EVIDENCE'], []).append(a['FACT_LOCATION'])

    return {
        'NETWORK_ID': 'ITALY_FIELD_SENSOR_NETWORK_V1',
        'CASE_ID': 'IT-CASE-DURUM-FUSARIUM-001',
        'SOURCE_ID': 'DERIVED/IT-REDE-CAMPO-V1',
        'source': 'busca ao redor dos quatro faróis — nenhuma execução paga',
        'SOURCE_LOCATION': 'web pública italiana',
        'FACT_LOCATION': 'ver FACT_LOCATIONS_FOUND — por conteúdo, nunca por voz',
        'ORIGINAL_LANGUAGE': 'it', 'EVIDENCE_CLASS': 'PRIMARY_SOURCE_PROBE',
        'captured_at': datetime.date.today().isoformat(),
        'CAPTURED_AT': datetime.date.today().isoformat(),
        'CASE_DATE': CASE_DATE.isoformat(),
        'WINDOW': [JANELA[0].isoformat(), JANELA[1].isoformat()],
        'APIFY_RUNS': 0, 'APIFY_COST_USD': 0,

        'CORRECTION_OF_PREVIOUS_ROUND': (
            'a rodada anterior publicou PROSPECTIVE_HUMAN_SENSOR = PROVED a partir de '
            'cinco vozes prospectivas das quais CINCO eram organizações. Instituição '
            'não é pessoa. INSTITUTIONAL_SIGNAL ≠ HUMAN_PERSON_SIGNAL'),

        'BASELINES': BASELINES,
        'CAP_NEW_ENTRIES': TETO_NOVOS, 'NEW_ENTRIES': len(novos),
        'NEW_PERSONS': [p['NAME'] for p in PESSOAS],
        'NEW_ORGANIZATIONS': [o['NAME'] for o in ORGANIZACOES_NOVAS],
        'PERSONS': PESSOAS, 'ORGANIZATIONS': ORGANIZACOES_NOVAS,

        'NETWORK_EDGES': [
            {'FROM': 'Lorenzo Ghiraldelli — "Pazzi per il Meteo Goriziano"',
             'FROM_KIND': sv.CREATOR_INFLUENCER, 'TO': 'Dario Maurigh',
             'TO_KIND': sv.TECHNICAL_FIELD_VOICE, 'RELATION': 'CITED_AS_SOURCE',
             'EVIDENCE': ('o boletim de 15/05 traz "Fonte: Lorenzo Ghiraldelli, Pazzi '
                          'per il Meteo Goriziano (canale Telegram e pagina FB)"')},
            {'FROM': 'Dario Maurigh', 'FROM_KIND': sv.TECHNICAL_FIELD_VOICE,
             'TO': 'Consorzio Collio', 'TO_KIND': sv.PRODUCER_COOP_VOICE,
             'RELATION': 'AUTHORS_BULLETIN_FOR',
             'EVIDENCE': '"A cura di: Enol. Dario Maurigh"'},
            {'FROM': 'Consorzio Collio', 'FROM_KIND': sv.PRODUCER_COOP_VOICE,
             'TO': 'ERSA FVG', 'TO_KIND': sv.INSTITUTIONAL_FIELD_VOICE,
             'RELATION': 'BULLETIN_HOSTED_BY',
             'EVIDENCE': 'o boletim do consórcio é publicado no portal do ERSA'},
            {'FROM': 'AIAB — técnico citado como fonte no boletim ERSA',
             'FROM_KIND': sv.TECHNICAL_FIELD_VOICE, 'TO': 'ERSA FVG',
             'TO_KIND': sv.INSTITUTIONAL_FIELD_VOICE, 'RELATION': 'CITED_AS_SOURCE',
             'EVIDENCE': '"Fonte: tecnico AIAB" no boletim n.7'},
            {'FROM': 'Horta srl — grano.net', 'FROM_KIND': sv.TECHNICAL_FIELD_VOICE,
             'TO': 'ERSA FVG', 'TO_KIND': sv.INSTITUTIONAL_FIELD_VOICE,
             'RELATION': 'MODEL_FEEDS_BULLETIN',
             'EVIDENCE': '"Sulla base degli output del modello previsionale grano.net"'},
            {'FROM': 'OSMER ARPA FVG', 'FROM_KIND': sv.INSTITUTIONAL_FIELD_VOICE,
             'TO': 'Consorzio Collio', 'TO_KIND': sv.PRODUCER_COOP_VOICE,
             'RELATION': 'WEATHER_FEEDS_BULLETIN',
             'EVIDENCE': 'ambos os boletins citam o OSMER'},
            {'FROM': 'Maurizio Martinuzzi', 'FROM_KIND': sv.TECHNICAL_FIELD_VOICE,
             'TO': 'ERSA FVG', 'TO_KIND': sv.INSTITUTIONAL_FIELD_VOICE,
             'RELATION': 'NAMED_TECHNICIAN_INSIDE',
             'EVIDENCE': 'assina como contato técnico da seção cerealicoltura'},
        ],

        'CONTENTS_READ': leituras, 'CONTENTS_READ_COUNT': len(leituras),
        'SIGNALS_BEFORE_BASELINE': acrescentos(EARLIER),
        'EARLIER_THAN_INSTITUTION': [p['NAME'] for p in PESSOAS if EARLIER in p['ADDS']],
        'MORE_LOCAL_THAN_INSTITUTION': [p['NAME'] for p in PESSOAS
                                        if MORE_LOCAL in p['ADDS']],
        'FIELD_DETAIL': acrescentos(FIELD_DETAIL),
        'INDEPENDENT_CONFIRMATION': [p['NAME'] for p in PESSOAS
                                     if INDEPENDENT_CONFIRMATION in p['ADDS']],
        'REPETITION_ONLY': [p['NAME'] for p in PESSOAS if REPETITION_ONLY in p['ADDS']],

        'FACT_LOCATIONS_FOUND': fatos, 'FACT_LOCATIONS_COUNT': len(fatos),
        'FACT_LOCATIONS_BY_TYPE': por_tipo,
        'MODELLED_RISK': por_tipo.get(fl.MODELLED_RISK, []),
        'FIELD_OBSERVATION': por_tipo.get(fl.FIELD_OBSERVATION, []),
        'CONVERGENCE': (
            'o boletim do ERSA traz MODELLED_RISK e FIELD_OBSERVATION no MESMO '
            'documento e em frases seguidas — mapa de risco do grano.net, e depois '
            '"dai rilievi in campo è emerso". Convergem, e ficam preservados separados: '
            'fundir as duas evidências apagaria justamente a checagem que elas fazem '
            'uma na outra'),
        'FACT_TIMES_DEFENSIBLE': [L['ID'] for L in leituras
                                  if L['TIME'].get('FACT_TIME') not in (None, 'NOT_KNOWN')],

        'LAWS': [
            'INSTITUTIONAL_SIGNAL ≠ HUMAN_PERSON_SIGNAL',
            'PERSON_INSIDE_INSTITUTION ≠ PERSON_AS_PUBLIC_SENSOR',
            'CLASS_PROVED_ON_ANOTHER_CROP ≠ CASE_SIGNAL',
            'STRUCTURAL_NEGATION ≠ OBSERVATIONAL_NEGATION',
            'MODELLED_RISK ≠ FIELD_OBSERVATION',
            'PRODUCER_FIELD_REPORT ≠ ORGANIZATION_COMMUNICATION',
            'PRODUCER_COOP_ORGANIZATION ≠ PRODUCER_PERSON',
        ],

        'PROSPECTIVE_INSTITUTIONAL_FIELD_SENSOR': 'PROVED',
        'PROSPECTIVE_TECHNICAL_PERSON_SENSOR': 'PROVED' if tecnicos_prosp else 'NOT_PROVED',

        # CORREÇÃO. `PROSPECTIVE_PRODUCER_SENSOR = PROVED` vinha do Consorzio
        # Collio, que é uma ORGANIZAÇÃO. É o mesmo erro da rodada passada com
        # outro nome: cooperativa não é produtor-pessoa. Nenhum produtor físico
        # foi medido, e o estado honesto é NOT_PROVED.
        #
        #     PRODUCER_COOP_ORGANIZATION ≠ PRODUCER_PERSON
        'PROSPECTIVE_PRODUCER_COOP_SENSOR': 'PROVED' if coops_prosp else 'NOT_PROVED',
        'PROSPECTIVE_PRODUCER_PERSON_SENSOR': ('PROVED' if produtores_pessoa
                                               else 'NOT_PROVED'),
        'PRODUCER_CORRECTION': (
            'o veredito anterior de produtor saía do Consorzio Collio — '
            'ENTITY_KIND=ORGANIZATION. Cooperativa é classe válida de organização e '
            'não substitui produtor-pessoa. Nenhuma pessoa física produtora foi '
            'medida nesta rodada'),
        'PROSPECTIVE_CREATOR_SENSOR': 'PROMISING' if creators_prosp else 'NOT_PROVED',
        'PROSPECTIVE_RESEARCHER_SENSOR': 'NOT_PROVED',
        'PROSPECTIVE_HUMAN_PERSON_SENSOR': 'PROVED' if pessoas_prosp else 'NOT_PROVED',
        'PROSPECTIVE_HUMAN_PERSON_SENSOR_MUST_CARRY': {
            'CROP': 'vite, não grano duro',
            'REGION': 'Friuli-Venezia Giulia, não Toscana',
            'CASE': 'não é sinal do caso — prova a CLASSE, em outra cultura e outra região',
            'HOW_MANY': '2 pessoas de 4 medidas',
        },
        'ITALY_HUMAN_SENSOR_ECOSYSTEM': 'PARTIALLY_MAPPED',

        'RECOMMENDATION': {
            'COLLECT_RECURRENTLY': (
                'a camada institucional regional + os boletins de consórcio que ela '
                'hospeda. São a mesma porta técnica e saem juntos, na estação'),
            'WHY': ('é a única camada medida que publica ENQUANTO a decisão está aberta, '
                    'e a única onde uma pessoa nomeada acrescenta resolução que a '
                    'instituição não tem'),
            'DO_NOT_COLLECT': 'rede social por padrão; LinkedIn deste painel',
            'WATCH': ('o canal Telegram do ERSA e o do observador meteorológico — são '
                      'os dois pontos onde o sinal aparece antes do PDF'),
            'STILL_UNMEASURED': [
                'os cinco outros consórcios do índice do ERSA',
                'a cadência 2026 do boletim da Umbria',
                "Consorzio Agrario dell'Emilia (503)",
                'se existe equivalente do Collio para CEREAIS, e não só para vite'],
        },
        'STILL_FORBIDDEN_TO_WRITE': ['ITALY OPPORTUNITY', 'SALES OPPORTUNITY',
                                     'ADAMA SHOULD ACT', 'MARKET GAP'],
    }


def main():
    out = medir()
    os.makedirs(os.path.dirname(DEST), exist_ok=True)
    with open(DEST, 'w', encoding='utf-8') as fh:
        json.dump(out, fh, ensure_ascii=False, indent=2)
    print('baselines:', len(out['BASELINES']),
          '| novas entradas:', out['NEW_ENTRIES'], '(teto %d)' % out['CAP_NEW_ENTRIES'])
    print('arestas da rede:')
    for e in out['NETWORK_EDGES']:
        print('   %-38s -%s-> %s' % (e['FROM'][:38], e['RELATION'][:22], e['TO'][:26]))
    print('acrescentos humanos:')
    print('   EARLIER_THAN_INSTITUTION   :', out['EARLIER_THAN_INSTITUTION'])
    print('   MORE_LOCAL_THAN_INSTITUTION:', out['MORE_LOCAL_THAN_INSTITUTION'])
    print('   REPETITION_ONLY            :', out['REPETITION_ONLY'])
    print('FACT_LOCATIONS por tipo:', out['FACT_LOCATIONS_BY_TYPE'])
    print()
    for k in ('PROSPECTIVE_INSTITUTIONAL_FIELD_SENSOR',
              'PROSPECTIVE_TECHNICAL_PERSON_SENSOR',
              'PROSPECTIVE_PRODUCER_COOP_SENSOR',
              'PROSPECTIVE_PRODUCER_PERSON_SENSOR',
              'PROSPECTIVE_CREATOR_SENSOR', 'PROSPECTIVE_RESEARCHER_SENSOR',
              'PROSPECTIVE_HUMAN_PERSON_SENSOR'):
        print('   %-42s %s' % (k, out[k]))
    print('->', os.path.relpath(DEST, ROOT))


if __name__ == '__main__':
    main()
