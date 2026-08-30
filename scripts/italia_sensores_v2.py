#!/usr/bin/env python3
"""
ITALY_HUMAN_SENSOR_MAP_V2 — quem fala ENQUANTO o campo está acontecendo.

Os pesquisadores estão congelados. Já sabemos o que eles são: risco estrutural,
mecanismo, tendência — e retrospectivos por calendário. A pergunta agora é outra:

    QUEM PUBLICA DURANTE A JANELA AGRONÔMICA, E NÃO SÓ DEPOIS DELA?

A ORDEM É PESSOA → CANAL
--------------------------
Não se escolhe plataforma porque existe Actor. Primeiro se pergunta quem são as
vozes; depois onde elas falam. Esta rodada não gastou uma execução paga sequer —
e mesmo assim encontrou a classe mais prospectiva de todas, que não está em rede
social nenhuma.

O QUE A MEDIÇÃO ENCONTROU
---------------------------
A voz mais prospectiva da Itália é **institucional**: os serviços fitossanitários
regionais publicam boletins numerados, semanais, DURANTE a estação, com fase
fenológica em escala BBCH, sintoma observado, comune, e recomendação. O ERSA do
Friuli-Venezia Giulia publicou o boletim n.7 em **20/04/2026** — três dias antes
da data do caso.

E a voz que a intuição colocaria em primeiro lugar — o creator agrícola — é a
menos prospectiva: o conteúdo medido é máquina, paixão e rotina, não sintoma.

    FOLLOWERS ≠ SENSOR QUALITY
    CREATOR ≠ SENSOR
    EVENT POST ≠ FIELD OBSERVATION

CADÊNCIA É A PERGUNTA, NÃO O ALCANCE
--------------------------------------
Uma voz tecnicamente excelente que publica depois da colheita tem função
diferente de um serviço que publica toda semana durante a floração. Não se somam.
Por isso cada voz carrega `CADENCE` e `SENSOR_POTENTIAL` separados — e nenhuma
das duas é um número.
"""
import datetime
import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import fato_local as fl  # noqa: E402

DEST = os.path.join(ROOT, 'data', 'samples', 'IT-CASOS', 'IT-SENSORES-V2.json')
EVID = os.path.join(ROOT, 'data', 'samples', 'IT-T5-SENSORES')

CASE_DATE = datetime.date(2026, 4, 23)
JANELA = (datetime.date(2026, 1, 1), datetime.date(2026, 5, 31))
TETO = 50

TECHNICAL_FIELD_VOICE = 'TECHNICAL_FIELD_VOICE'
PRODUCER_COOP_VOICE = 'PRODUCER_COOP_VOICE'
CREATOR_INFLUENCER = 'CREATOR_INFLUENCER'
INSTITUTIONAL_FIELD_VOICE = 'INSTITUTIONAL_FIELD_VOICE'
CLASSES = (TECHNICAL_FIELD_VOICE, PRODUCER_COOP_VOICE, CREATOR_INFLUENCER,
           INSTITUTIONAL_FIELD_VOICE)

# Cadência OBSERVADA, não prometida.
FIELD_SEASONAL, RECURRENT, EVENT_DRIVEN = 'FIELD_SEASONAL', 'RECURRENT', 'EVENT_DRIVEN'
OCCASIONAL, EVERGREEN_ONLY, CADENCE_NOT_KNOWN = ('OCCASIONAL', 'EVERGREEN_ONLY',
                                                 'NOT_KNOWN')

PROSPECTIVE_SENSOR = 'PROSPECTIVE_SENSOR'
CONTEXT_SENSOR = 'CONTEXT_SENSOR'
RETROSPECTIVE_SENSOR = 'RETROSPECTIVE_SENSOR'
COMMUNICATION_ONLY = 'COMMUNICATION_ONLY'
POTENTIAL_NOT_KNOWN = 'NOT_KNOWN'


def voz(**kw):
    """Uma voz. Campos ausentes viram NÃO SEI — nunca somem."""
    base = {'NAME': None, 'CLASS': None, 'ROLE': None, 'ORGANIZATION': None,
            'SOURCE_LOCATION': 'NÃO SEI', 'OPERATING_GEOGRAPHY': 'NÃO SEI',
            'MAIN_CROPS': [], 'MAIN_TOPICS': [], 'PUBLIC_CHANNELS': [],
            'PRIMARY_PUBLIC_CHANNEL': None, 'ACTIVE_2026': 'NOT_KNOWN',
            'LAST_OBSERVED_CONTENT_DATE': 'NOT_KNOWN',
            'CADENCE': CADENCE_NOT_KNOWN, 'SENSOR_POTENTIAL': POTENTIAL_NOT_KNOWN,
            'WHY': None}
    base.update(kw)
    # OPERATING_GEOGRAPHY é onde a voz atua. Nunca onde um fato aconteceu.
    base['OPERATING_GEOGRAPHY_IS_NOT_FACT_LOCATION'] = True
    return base


VOZES = [
    # ---------------------------------------------- INSTITUTIONAL_FIELD_VOICE
    voz(NAME='ERSA FVG — Servizio fitosanitario e chimico',
        CLASS=INSTITUTIONAL_FIELD_VOICE, ROLE='serviço fitossanitário regional',
        ORGANIZATION='ERSA Friuli-Venezia Giulia',
        SOURCE_LOCATION='Friuli-Venezia Giulia',
        OPERATING_GEOGRAPHY='Friuli-Venezia Giulia',
        MAIN_CROPS=['frumento', 'orzo', 'mais', 'soia', 'colza'],
        MAIN_TOPICS=['fase fenologica BBCH', 'septoriosi', 'ruggine bruna',
                     'elmintosporiosi', 'rincosporiosi', 'meteo', 'difesa integrata'],
        PUBLIC_CHANNELS=['site institucional (PDF numerado)',
                         'canal Telegram público t.me/ERSA_colture_erbacee_IPM'],
        PRIMARY_PUBLIC_CHANNEL='boletim PDF numerado no site institucional',
        ACTIVE_2026='YES', LAST_OBSERVED_CONTENT_DATE='2026-08-12',
        CADENCE=FIELD_SEASONAL, SENSOR_POTENTIAL=PROSPECTIVE_SENSOR,
        WHY=('série completa e numerada em 2026: n.1 em 19/01 a n.15 em 12/08. '
             'O n.7, de 20/04/2026, é de três dias antes da data do caso e traz '
             'fase fenológica BBCH, sintoma observado em campo e risco modelado '
             'declarados separadamente pelo próprio boletim')),
    voz(NAME='Regione Veneto — Servizio fitosanitario',
        CLASS=INSTITUTIONAL_FIELD_VOICE, ROLE='serviço fitossanitário regional',
        ORGANIZATION='Regione del Veneto', SOURCE_LOCATION='Veneto',
        OPERATING_GEOGRAPHY='Veneto',
        MAIN_CROPS=['cereali', 'mais', 'vite', 'frutticole'],
        MAIN_TOPICS=['difesa integrata', 'avversità', 'fenologia'],
        PUBLIC_CHANNELS=['página de boletins 2026 do portal regional'],
        PRIMARY_PUBLIC_CHANNEL='boletins fitossanitários no portal regional',
        ACTIVE_2026='YES', LAST_OBSERVED_CONTENT_DATE='2026-08-05',
        CADENCE=FIELD_SEASONAL, SENSOR_POTENTIAL=PROSPECTIVE_SENSOR,
        WHY='53 datas distintas em 2026, de 04/03 a 05/08 — a maior cadência medida'),
    voz(NAME='Servizio Fitosanitario Regionale Umbria',
        CLASS=INSTITUTIONAL_FIELD_VOICE, ROLE='serviço fitossanitário regional',
        ORGANIZATION='Regione Umbria', SOURCE_LOCATION='Umbria',
        OPERATING_GEOGRAPHY='Umbria — areali Conca Ternana, Eugubino Gualdese, '
                            'Lago Trasimeno, Media Valle del Tevere, Orvietano, '
                            'Valle Umbra Sud',
        MAIN_CROPS=['frumento', 'orzo'],
        MAIN_TOPICS=['fase fenologica', 'septoriosi', 'fusariosi della spiga'],
        PUBLIC_CHANNELS=['bollettino cereali (PDF)', 'portal regional'],
        PRIMARY_PUBLIC_CHANNEL='bollettino cereali em PDF',
        ACTIVE_2026='NOT_KNOWN', LAST_OBSERVED_CONTENT_DATE='2024-05-17',
        CADENCE=FIELD_SEASONAL, SENSOR_POTENTIAL=PROSPECTIVE_SENSOR,
        WHY=('o único boletim lido nomeia COMUNE e sintoma — "lieve attacco di '
             'Septoriosi nei Comuni di Branca di Gubbio", "presenza media di '
             'Septoriosi nel Comune di Parrano" — e recomenda intervenção contra '
             'fusariose em pré-floração. A página lista até 2024: ACTIVE_2026 é '
             'NÃO SEI, não NÃO')),
    voz(NAME='Regione Campania — bollettini fitosanitari',
        CLASS=INSTITUTIONAL_FIELD_VOICE, ROLE='serviço fitossanitário regional',
        ORGANIZATION='Regione Campania', SOURCE_LOCATION='Campania',
        OPERATING_GEOGRAPHY='Campania', MAIN_CROPS=['olivo'],
        MAIN_TOPICS=['difesa integrata'],
        PUBLIC_CHANNELS=['página de boletins 2026'],
        PRIMARY_PUBLIC_CHANNEL='boletins no portal regional',
        ACTIVE_2026='YES', LAST_OBSERVED_CONTENT_DATE='2026-08-28',
        CADENCE=OCCASIONAL, SENSOR_POTENTIAL=CONTEXT_SENSOR,
        WHY='só duas datas visíveis na página, ambas de agosto — porta aberta, volume baixo'),
    voz(NAME='LaMMA / Regione Toscana — Bollettino Frumento',
        CLASS=INSTITUTIONAL_FIELD_VOICE, ROLE='consórcio agrometeorológico regional',
        ORGANIZATION='Consorzio LaMMA', SOURCE_LOCATION='Toscana',
        OPERATING_GEOGRAPHY='Toscana', MAIN_CROPS=['frumento'],
        MAIN_TOPICS=['fenologia', 'rischio fusariosi', 'meteo'],
        PUBLIC_CHANNELS=['site LaMMA'],
        PRIMARY_PUBLIC_CHANNEL='bollettino frumento no site do LaMMA',
        ACTIVE_2026='YES', LAST_OBSERVED_CONTENT_DATE='2026-04-23',
        CADENCE=FIELD_SEASONAL, SENSOR_POTENTIAL=PROSPECTIVE_SENSOR,
        WHY=('já preservado em missão anterior como a perna de campo do caso — é a '
             'única voz medida que cobre a região E a data do caso')),
    voz(NAME='ARSIA Toscana — agroambiente.info',
        CLASS=INSTITUTIONAL_FIELD_VOICE, ROLE='ex-agência regional',
        ORGANIZATION='Regione Toscana (ARSIA, extinta)', SOURCE_LOCATION='Toscana',
        OPERATING_GEOGRAPHY='Toscana', MAIN_CROPS=['frumento duro', 'frumento tenero'],
        MAIN_TOPICS=['monitoraggio settimanale'],
        PUBLIC_CHANNELS=['agroambiente.info.arsia.toscana.it (links mortos)'],
        PRIMARY_PUBLIC_CHANNEL='NOT_AVAILABLE',
        ACTIVE_2026='NO', LAST_OBSERVED_CONTENT_DATE='2013-05-06',
        CADENCE=EVERGREEN_ONLY, SENSOR_POTENTIAL=COMMUNICATION_ONLY,
        WHY=('porta que NÃO rende, e registrar isso é resultado: a página do '
             'monitoramento semanal de trigo é de 2013 e os links do ARSIA estão '
             'mortos. A agência foi extinta')),

    # ------------------------------------------------- TECHNICAL_FIELD_VOICE
    voz(NAME='Horta srl — grano.net / orzo.net',
        CLASS=TECHNICAL_FIELD_VOICE, ROLE='provedor de modelo previsional',
        ORGANIZATION='Horta srl (spin-off Università Cattolica)',
        SOURCE_LOCATION='Piacenza', OPERATING_GEOGRAPHY='Itália, via serviços regionais',
        MAIN_CROPS=['frumento', 'orzo'],
        MAIN_TOPICS=['rischio septoriosi', 'ruggine', 'oidio', 'modelo previsional'],
        PUBLIC_CHANNELS=['grano.net', 'orzo.net', 'citado nos boletins regionais'],
        PRIMARY_PUBLIC_CHANNEL='saída do modelo republicada nos boletins regionais',
        ACTIVE_2026='YES', LAST_OBSERVED_CONTENT_DATE='2026-04-20',
        CADENCE=FIELD_SEASONAL, SENSOR_POTENTIAL=CONTEXT_SENSOR,
        WHY=('alimenta os mapas de risco do boletim ERSA com 10 pontos de '
             'monitoramento. Mas é RISCO MODELADO, não sintoma visto — e o próprio '
             'boletim separa as duas coisas na frase seguinte')),
    voz(NAME='Servizio fitosanitario ERSA — sezione cerealicoltura',
        CLASS=TECHNICAL_FIELD_VOICE, ROLE='técnicos de campo do serviço regional',
        ORGANIZATION='ERSA FVG', SOURCE_LOCATION='Friuli-Venezia Giulia',
        OPERATING_GEOGRAPHY='média e alta planície do FVG',
        MAIN_CROPS=['frumento', 'orzo'],
        MAIN_TOPICS=['rilievi in campo', 'sintomi', 'fenologia'],
        PUBLIC_CHANNELS=['assinam a seção técnica do boletim'],
        PRIMARY_PUBLIC_CHANNEL='seção "rilievi in campo" do boletim',
        ACTIVE_2026='YES', LAST_OBSERVED_CONTENT_DATE='2026-04-20',
        CADENCE=FIELD_SEASONAL, SENSOR_POTENTIAL=PROSPECTIVE_SENSOR,
        WHY=('é a frase mais prospectiva que esta missão leu: "dai rilievi in campo '
             'è emerso che in alcune zone della media e dell\'alta pianura si '
             'osservano dei sintomi evidenti della patologia". Observação própria, '
             'em janela, com fenologia — e sem unidade administrativa')),
    voz(NAME='Centro di Saggio — Consorzio Agrario dell\'Emilia',
        CLASS=TECHNICAL_FIELD_VOICE, ROLE='centro de ensaios / bollettino tecnico',
        ORGANIZATION='Consorzio Agrario dell\'Emilia',
        SOURCE_LOCATION='Bologna / Modena / Reggio Emilia',
        OPERATING_GEOGRAPHY='Emilia-Romagna',
        MAIN_CROPS=['frumento tenero', 'frumento duro', 'orzo', 'foraggere'],
        MAIN_TOPICS=['prove di difesa', 'soglie di intervento', 'concimazione'],
        PUBLIC_CHANNELS=['caemilia.it — Bollettino Tecnico'],
        PRIMARY_PUBLIC_CHANNEL='Bollettino Tecnico no site do consórcio',
        ACTIVE_2026='NOT_KNOWN', LAST_OBSERVED_CONTENT_DATE='NOT_KNOWN',
        CADENCE=CADENCE_NOT_KNOWN, SENSOR_POTENTIAL=POTENTIAL_NOT_KNOWN,
        WHY=('o site devolveu 503 nas duas tentativas — ROUTE_UNAVAILABLE, e falha '
             'de acesso não é ausência de sinal. É o candidato mais promissor da '
             'classe cooperativa e ficou por medir')),
    voz(NAME='Federico Cavina',
        CLASS=TECHNICAL_FIELD_VOICE, ROLE='Coordinatore Centro di Saggio',
        ORGANIZATION='Terremerse soc. coop.', SOURCE_LOCATION='Emilia-Romagna',
        OPERATING_GEOGRAPHY='Emilia-Romagna', MAIN_CROPS=['cereali'],
        MAIN_TOPICS=['prove di campo'],
        PUBLIC_CHANNELS=['LinkedIn (medido: 1 post na janela, anúncio de vaga)'],
        PRIMARY_PUBLIC_CHANNEL='NOT_FOUND_OUTSIDE_LINKEDIN',
        ACTIVE_2026='YES', LAST_OBSERVED_CONTENT_DATE='2026-04-08',
        CADENCE=OCCASIONAL, SENSOR_POTENTIAL=COMMUNICATION_ONLY,
        WHY=('identidade CONFIRMADA na rodada anterior, e o cargo é exatamente a '
             'classe certa — mas o único conteúdo em janela foi um anúncio de vaga. '
             'A função é prospectiva; o canal público medido, não')),

    # -------------------------------------------------- PRODUCER_COOP_VOICE
    voz(NAME='Consorzi Agrari d\'Italia (CAI)',
        CLASS=PRODUCER_COOP_VOICE, ROLE='rede nacional de consórcios agrários',
        ORGANIZATION='CAI', SOURCE_LOCATION='Itália', OPERATING_GEOGRAPHY='Itália',
        MAIN_CROPS=['frumento', 'orzo', 'mais'],
        MAIN_TOPICS=['giornate in campo', 'rese', 'qualità', 'prezzi'],
        PUBLIC_CHANNELS=['YouTube', 'imprensa técnica', 'giornate in campo'],
        PRIMARY_PUBLIC_CHANNEL='giornate in campo → YouTube e imprensa técnica',
        ACTIVE_2026='YES', LAST_OBSERVED_CONTENT_DATE='2026-05-26',
        CADENCE=EVENT_DRIVEN, SENSOR_POTENTIAL=CONTEXT_SENSOR,
        WHY=('as Giornate in Campo são em campo e na estação, mas o conteúdo '
             'publicado é de variedades, rendimento e mercado — e chega depois do '
             'evento. ORGANIZATION_COMMUNICATION, não PRODUCER_FIELD_SIGNAL')),
    voz(NAME='COPROB',
        CLASS=PRODUCER_COOP_VOICE, ROLE='cooperativa açucareira',
        ORGANIZATION='COPROB', SOURCE_LOCATION='Emilia-Romagna',
        OPERATING_GEOGRAPHY='Emilia-Romagna, Veneto', MAIN_CROPS=['barbabietola'],
        MAIN_TOPICS=['bollettini ai soci'],
        PUBLIC_CHANNELS=['coprob.com — area agricoltori, bollettini'],
        PRIMARY_PUBLIC_CHANNEL='bollettini na área de agricultores',
        ACTIVE_2026='NOT_KNOWN', LAST_OBSERVED_CONTENT_DATE='NOT_KNOWN',
        CADENCE=CADENCE_NOT_KNOWN, SENSOR_POTENTIAL=POTENTIAL_NOT_KNOWN,
        WHY='cultura fora do escopo dos pilotos; registrado, não medido'),

    # --------------------------------------------------- CREATOR_INFLUENCER
    voz(NAME='AgroNotizie (Image Line)',
        CLASS=CREATOR_INFLUENCER, ROLE='imprensa técnica com presença social',
        ORGANIZATION='Image Line', SOURCE_LOCATION='Faenza (Ravenna)',
        OPERATING_GEOGRAPHY='Itália',
        MAIN_CROPS=['mais', 'frumento', 'vite', 'olivo'],
        MAIN_TOPICS=['difesa', 'micotossine', 'mercati', 'eventi'],
        PUBLIC_CHANNELS=['site', 'Instagram @agronotizie', 'YouTube agronotizietv'],
        PRIMARY_PUBLIC_CHANNEL='site agronotizie.imagelinenetwork.com',
        ACTIVE_2026='YES', LAST_OBSERVED_CONTENT_DATE='2026-05-21',
        CADENCE=RECURRENT, SENSOR_POTENTIAL=CONTEXT_SENSOR,
        WHY=('é o canal que PUBLICA o pesquisador: a reportagem de 13/02/2026 com '
             'Locatelli é dele. Mas o que ele relata é evento, e o evento é '
             'retrospectivo')),
    voz(NAME='Tommaso Rossi Razzini ("The Roman Farmer")',
        CLASS=CREATOR_INFLUENCER, ROLE='agro-creator', ORGANIZATION='independente',
        SOURCE_LOCATION='Lazio', OPERATING_GEOGRAPHY='Lazio',
        MAIN_CROPS=['NÃO SEI'], MAIN_TOPICS=['macchine agricole', 'innovazione'],
        PUBLIC_CHANNELS=['Instagram', 'TikTok', 'YouTube', 'Facebook'],
        PRIMARY_PUBLIC_CHANNEL='Instagram',
        ACTIVE_2026='YES', LAST_OBSERVED_CONTENT_DATE='2026-02',
        CADENCE=RECURRENT, SENSOR_POTENTIAL=COMMUNICATION_ONLY,
        WHY=('conteúdo de máquinas e divulgação. CREATOR ≠ SENSOR: nada indica '
             'observação de sintoma, fenologia ou diagnóstico')),
    voz(NAME='Canais "agro-influencer" italianos em geral',
        CLASS=CREATOR_INFLUENCER, ROLE='classe agregada, não voz individual',
        ORGANIZATION='vários', SOURCE_LOCATION='Itália',
        OPERATING_GEOGRAPHY='Itália', MAIN_CROPS=['vários'],
        MAIN_TOPICS=['trattori', 'mietitrebbie', 'vita in azienda', 'passione'],
        PUBLIC_CHANNELS=['Instagram', 'YouTube', 'TikTok'],
        PRIMARY_PUBLIC_CHANNEL='Instagram / YouTube',
        ACTIVE_2026='YES', LAST_OBSERVED_CONTENT_DATE='2026',
        CADENCE=RECURRENT, SENSOR_POTENTIAL=COMMUNICATION_ONLY,
        WHY=('a classe existe e é ativa, e o que ela publica é máquina, rotina e '
             'paixão. Isso é um RESULTADO da medição, não uma amostra a trocar '
             'até achar um positivo')),
]

# --------------------------------------------------------------- conteúdos
LEITURAS = [
    {'ID': 'ERSA-FVG/BOLL-07-2026',
     'ARQUIVO': 'ersa-fvg-boll-07-frumento-orzo-2026-04-20.txt',
     'VOICE': 'ERSA FVG — Servizio fitosanitario e chimico',
     'CLASS': INSTITUTIONAL_FIELD_VOICE, 'PUBLISHED_AT': '2026-04-20',
     'CROP': 'frumento/orzo', 'REGION_OF_SOURCE': 'Friuli-Venezia Giulia',
     'SIGNAL_TYPES': ['PHENOLOGY_OBSERVATION', 'FIELD_OBSERVATION',
                      'MODELLED_RISK', 'WEATHER_CONCERN',
                      'MANAGEMENT_RECOMMENDATION']},
    {'ID': 'UMBRIA/BOLL-CEREALI',
     'ARQUIVO': 'umbria-boll-cereali-04-servizio-fitosanitario.txt',
     'VOICE': 'Servizio Fitosanitario Regionale Umbria',
     'CLASS': INSTITUTIONAL_FIELD_VOICE, 'PUBLISHED_AT': None,
     'CROP': 'frumento/orzo', 'REGION_OF_SOURCE': 'Umbria',
     'SIGNAL_TYPES': ['FIELD_OBSERVATION', 'SYMPTOM_OBSERVATION',
                      'PHENOLOGY_OBSERVATION', 'TECHNICAL_WARNING']},
    {'ID': 'AGRONOTIZIE/88873',
     'ARQUIVO': 'agronotizie-88873-mais-micotossine-2026-02-13.txt',
     'VOICE': 'AgroNotizie (Image Line)',
     'CLASS': CREATOR_INFLUENCER, 'PUBLISHED_AT': '2026-02-13',
     'CROP': 'mais', 'REGION_OF_SOURCE': 'Itália',
     'SIGNAL_TYPES': ['EVENT_PRESENTATION', 'DIAGNOSTIC_RESULT',
                      'RETROSPECTIVE_ANALYSIS']},
]


def em_janela(d):
    if not d:
        return 'NOT_DATED_PRECISELY'
    x = datetime.date.fromisoformat(d)
    return 'IN_WINDOW' if JANELA[0] <= x <= JANELA[1] else 'OUT_OF_WINDOW'


def ler():
    fora = []
    for L in LEITURAS:
        reg = dict(L)
        caminho = os.path.join(EVID, L['ARQUIVO'])
        if not os.path.exists(caminho):
            reg['EVIDENCE_STATE'] = 'NOT_PRESERVED'
            reg['FACT_LOCATIONS'] = []
            fora.append(reg)
            continue
        with open(caminho, encoding='utf-8') as fh:
            texto = fh.read()
        reg['EVIDENCE_STATE'] = 'PRESERVED'
        reg['EVIDENCE_PATH'] = 'data/samples/IT-T5-SENSORES/' + L['ARQUIVO']
        reg['SHA256'] = hashlib.sha256(texto.encode('utf-8')).hexdigest()
        aceitas, recusadas = fl.localizacoes_do_fato(texto, origem=L['ID'])
        reg['FACT_LOCATIONS'] = aceitas
        reg['PLACE_MENTIONS_REJECTED'] = [{'PLACE': r['PLACE'], 'WHY': r['WHY']}
                                          for r in recusadas]
        reg['TIME'] = fl.tempo_do_fato(texto, L['PUBLISHED_AT'])
        reg['OCCURRENCE_NOT_INCIDENCE'] = fl.ocorrencia_nao_e_incidencia(
            [a['TYPE_OF_EVIDENCE'] for a in aceitas])
        reg['IN_CASE_WINDOW'] = em_janela(L['PUBLISHED_AT'])
        fora.append(reg)
    return fora


def medir():
    leituras = ler()
    por_classe = {c: [v for v in VOZES if v['CLASS'] == c] for c in CLASSES}
    por_potencial = {p: [v['NAME'] for v in VOZES if v['SENSOR_POTENTIAL'] == p]
                     for p in (PROSPECTIVE_SENSOR, CONTEXT_SENSOR,
                               RETROSPECTIVE_SENSOR, COMMUNICATION_ONLY,
                               POTENTIAL_NOT_KNOWN)}
    fatos = [a for L in leituras for a in L.get('FACT_LOCATIONS', [])]
    tempos = [L['TIME'] for L in leituras
              if L.get('TIME', {}).get('FACT_TIME') not in (None, 'NOT_KNOWN')]
    em_jan = [L['ID'] for L in leituras if L.get('IN_CASE_WINDOW') == 'IN_WINDOW']
    campo = [L['ID'] for L in leituras
             if 'FIELD_OBSERVATION' in L.get('SIGNAL_TYPES', [])]

    prospectivos = por_potencial[PROSPECTIVE_SENSOR]
    ecossistema = ('MAPPED' if len(VOZES) >= TETO else
                   'PARTIALLY_MAPPED' if prospectivos else 'NOT_PROVED')
    prospectivo = ('PROVED' if (prospectivos and campo and fatos) else
                   'PROMISING' if prospectivos else 'NOT_PROVED')

    return {
        'MAP_ID': 'ITALY_HUMAN_SENSOR_MAP_V2',
        'CASE_ID': 'IT-CASE-DURUM-FUSARIUM-001',
        'SOURCE_ID': 'DERIVED/IT-SENSORES-V2',
        'source': 'descoberta pública de vozes e canais — nenhuma execução paga',
        'SOURCE_LOCATION': 'web pública italiana',
        'FACT_LOCATION': 'ver FACT_LOCATIONS_FOUND — por conteúdo, nunca por voz',
        'ORIGINAL_LANGUAGE': 'it', 'EVIDENCE_CLASS': 'PRIMARY_SOURCE_PROBE',
        'captured_at': datetime.date.today().isoformat(),
        'CAPTURED_AT': datetime.date.today().isoformat(),
        'CASE_DATE': CASE_DATE.isoformat(),
        'WINDOW': [JANELA[0].isoformat(), JANELA[1].isoformat()],
        'APIFY_RUNS': 0, 'APIFY_COST_USD': 0,
        'RESEARCHERS_FROZEN': ['Sabrina Locatelli', 'Pasquale De Vita',
                               'Nicola Pecchioni', 'Francesca Nocente',
                               'Daniela Pacifico'],
        'CAP': TETO, 'TOTAL_VOICES': len(VOZES),
        'BY_CLASS': {c: len(v) for c, v in por_classe.items()},
        'VOICES': VOZES,
        'BY_CADENCE': {c: [v['NAME'] for v in VOZES if v['CADENCE'] == c]
                       for c in (FIELD_SEASONAL, RECURRENT, EVENT_DRIVEN,
                                 OCCASIONAL, EVERGREEN_ONLY, CADENCE_NOT_KNOWN)},
        'BY_SENSOR_POTENTIAL': por_potencial,
        'ACTIVE_2026': [v['NAME'] for v in VOZES if v['ACTIVE_2026'] == 'YES'],
        'BEST_CHANNEL_BY_CLASS': {
            INSTITUTIONAL_FIELD_VOICE: 'boletim fitossanitário regional numerado (PDF)',
            TECHNICAL_FIELD_VOICE: 'a seção "rilievi in campo" dentro do boletim regional',
            PRODUCER_COOP_VOICE: 'bollettino tecnico de consórcio — NÃO MEDIDO (503)',
            CREATOR_INFLUENCER: 'site de imprensa técnica, não a rede social',
        },
        'CONTENTS_READ': leituras,
        'CONTENTS_READ_COUNT': len(leituras),
        'CONTENTS_IN_CASE_WINDOW': em_jan,
        'WITH_FIELD_OBSERVATION': campo,
        'FACT_LOCATIONS_FOUND': fatos,
        'FACT_LOCATIONS_COUNT': len(fatos),
        'FACT_TIMES_DEFENSIBLE': len(tempos),
        'LAWS': [
            'FOLLOWERS ≠ SENSOR QUALITY',
            'CREATOR ≠ SENSOR',
            'EVENT POST ≠ FIELD OBSERVATION',
            'ORGANIZATION_COMMUNICATION ≠ PRODUCER_FIELD_SIGNAL',
            'SINTOMA OBSERVADO ≠ RISCO MODELADO',
            'OPERATING_GEOGRAPHY ≠ FACT_LOCATION',
            'SOURCE_GEOGRAPHY ≠ ADMIN_GEOGRAPHY',
            'DECLARED_ADMIN_MARKER > GAZETTEER',
            'NEGATED_OBSERVATION ≠ OBSERVATION',
            'REGULATORY_VALIDITY ≠ FACT_TIME',
            'ROUTE_UNAVAILABLE ≠ NO_SIGNAL',
        ],
        'ITALY_HUMAN_SENSOR_ECOSYSTEM': ecossistema,
        'RESEARCHER_SENSOR': 'CONTEXT_AND_RETROSPECTIVE_PROVED',
        'PROSPECTIVE_HUMAN_SENSOR': prospectivo,
        'HIGH_VALUE_SENSOR_TARGETS': [
            {'TARGET': 'ERSA FVG — bollettini colture erbacee',
             'WHY': 'série numerada, semanal, em janela, com BBCH e sintoma',
             'CROP_ISSUE': 'frumento × septoriosi/fusariosi; mais',
             'CHANNEL': 'PDF numerado + canal Telegram público'},
            {'TARGET': 'Regione Veneto — bollettini fitosanitari',
             'WHY': '53 datas em 2026, a maior cadência medida',
             'CROP_ISSUE': 'cereali e mais', 'CHANNEL': 'portal regional'},
            {'TARGET': 'LaMMA Toscana — bollettino frumento',
             'WHY': 'única voz que cobre a região E a data do caso',
             'CROP_ISSUE': 'grano duro × fusariosi', 'CHANNEL': 'site LaMMA'},
            {'TARGET': 'Servizio Fitosanitario Umbria — bollettino cereali',
             'WHY': 'nomeia COMUNE e sintoma, o melhor FACT_LOCATION da amostra',
             'CROP_ISSUE': 'frumento × septoriosi/fusariosi', 'CHANNEL': 'PDF'},
            {'TARGET': "Consorzio Agrario dell'Emilia — Bollettino Tecnico",
             'WHY': 'melhor candidato da classe cooperativa, e ficou por medir (503)',
             'CROP_ISSUE': 'cereali', 'CHANNEL': 'site do consórcio'},
        ],
        'NEXT_STEP': {
            'WHO': 'os quatro serviços fitossanitários regionais com cadência provada',
            'CHANNEL': 'boletim PDF numerado no portal de cada região',
            'CROP_ISSUE': 'frumento × fusariosi/septoriosi na janela de floração',
            'WHY_NOT_SOCIAL': ('nenhuma rede social entrou nesta lista, e não por '
                               'falta de acesso: por falta de sinal de campo'),
            'STILL_UNMEASURED': ["Consorzio Agrario dell'Emilia (503 nas duas tentativas)",
                                 'COPROB', 'cadência 2026 do boletim da Umbria'],
        },
        'STILL_FORBIDDEN_TO_WRITE': ['ITALY OPPORTUNITY', 'SALES OPPORTUNITY',
                                     'ADAMA SHOULD ACT', 'MARKET GAP'],
    }


def main():
    out = medir()
    os.makedirs(os.path.dirname(DEST), exist_ok=True)
    with open(DEST, 'w', encoding='utf-8') as fh:
        json.dump(out, fh, ensure_ascii=False, indent=2)
    print('vozes mapeadas:', out['TOTAL_VOICES'], '(teto %d)' % out['CAP'])
    for c, n in out['BY_CLASS'].items():
        print('   %-28s %d' % (c, n))
    print('cadência:')
    for c, v in out['BY_CADENCE'].items():
        if v:
            print('   %-18s %d  %s' % (c, len(v), ', '.join(x[:26] for x in v[:3])))
    print('potencial:')
    for p, v in out['BY_SENSOR_POTENTIAL'].items():
        if v:
            print('   %-22s %d  %s' % (p, len(v), ', '.join(x[:24] for x in v[:3])))
    print('conteúdos lidos:', out['CONTENTS_READ_COUNT'],
          '| em janela:', len(out['CONTENTS_IN_CASE_WINDOW']),
          '| com observação de campo:', len(out['WITH_FIELD_OBSERVATION']))
    for a in out['FACT_LOCATIONS_FOUND']:
        print('   FACT %-22s %-13s %-16s %s' % (
            a['FACT_LOCATION'], a['FACT_LOCATION_PRECISION'],
            a['PRECISION_SOURCE'], a['TYPE_OF_EVIDENCE']))
    print()
    print('ITALY_HUMAN_SENSOR_ECOSYSTEM =', out['ITALY_HUMAN_SENSOR_ECOSYSTEM'])
    print('RESEARCHER_SENSOR            =', out['RESEARCHER_SENSOR'])
    print('PROSPECTIVE_HUMAN_SENSOR     =', out['PROSPECTIVE_HUMAN_SENSOR'])
    print('->', os.path.relpath(DEST, ROOT))


if __name__ == '__main__':
    main()
