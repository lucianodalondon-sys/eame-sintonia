#!/usr/bin/env python3
"""
A ÚLTIMA FALSIFICAÇÃO — e a hipótese não caiu, mas mudou de forma.

A hipótese sob teste: *em cereais italianos o sinal de safra fica apenas na
instituição regional, sem camada pública local ou pessoal abaixo dela.*

Eu não fui procurar qualquer positivo. Fui aos lugares onde ela teria a maior
chance de cair: Puglia, Basilicata, Sicilia, Marche, Emilia-Romagna — as regiões
do grano duro, que a rodada anterior não tinha aberto.

E ela caiu pela metade.

O QUE A FALSIFICAÇÃO ENCONTROU
--------------------------------
As Marche publicam `Notiziario Agrometeorologico di Produzione Integrata` **por
província**, semanal, assinado por um **Centro Agrometeo Locale** — um nó
territorial abaixo da região, com endereço próprio em Osimo Stazione. A série da
província de Ancona traz n.613 em 08/04, n.615 em 22/04, n.616 em 29/04 e n.617
em 06/05 de 2026: cobre a janela de floração inteira, com fase fenológica BBCH,
e recomendação de intervenção contra fusariose no ponto certo do ciclo.

O n.615 é de **22 de abril de 2026** — um dia antes da data do caso.

E há uma rede de campo por baixo: "le trappole per il monitoraggio ... installate
nelle aziende della rete di riferimento". Fazendas hospedam armadilhas e a
contagem semanal entra no boletim.

O QUE ELA NÃO ENCONTROU
-------------------------
Nenhuma PESSOA. O boletim é assinado pelo Centro, com telefone e e-mail de
escritório — nunca por alguém. A rede de fazendas de referência não é nomeada.
E não há organização local INDEPENDENTE da instituição: o Centro Agrometeo
Locale é parte da agência regional.

Então a arquitetura de cereais não é "só a região". É:

    REGIÃO ─▶ CENTRO AGROMETEO **PROVINCIAL** ─▶ REDE DE FAZENDAS (anônima)

contra a arquitetura da vinha, que tem pessoa com nome em dois elos.

    LOCAL_ORGANIZATION_SENSOR ≠ TECHNICAL_PERSON_SENSOR

O VEREDITO QUE ISSO OBRIGA
----------------------------
`REGIONAL_INSTITUTION_DOMINANT` continua, mas com uma correção que importa: a
instituição desce até a província e apoia-se numa rede de fazendas. Chamar isso
de "só a região" seria perder o nó mais local que os cereais têm.

E o nacional continua sem fechar: Puglia e Sicilia não devolveram boletim de
campo de cereais nesta busca, a ALSIA da Basilicata está atrás de cadastro, e o
Consorzio Agrario dell'Emilia segue inacessível por cadeia TLS incompleta.

    NO_IN_MEASURED_NETWORK ≠ NO_IN_ITALY
    GATED ≠ ABSENT
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

DEST = os.path.join(ROOT, 'data', 'samples', 'IT-CASOS', 'IT-CEREAIS-FALSIFICACAO.json')
EVID = os.path.join(ROOT, 'data', 'samples', 'IT-T5-SENSORES')

CASE_DATE = datetime.date(2026, 4, 23)
JANELA = (datetime.date(2026, 3, 1), datetime.date(2026, 5, 31))
TETO_ORGS, TETO_PESSOAS = 15, 20

CEREAL_LOCAL_FIELD_SENSOR = 'CEREAL_LOCAL_FIELD_SENSOR'
PARTIAL_LOCAL = 'PARTIAL_LOCAL_FIELD_SENSOR'
INSTITUTION_ONLY = 'INSTITUTION_ONLY'
COMMUNICATION_ONLY = 'COMMUNICATION_ONLY'
NOT_MEASURED = 'NOT_MEASURED'
NOT_MEASURED_ACCESS = 'NOT_MEASURED_ACCESS_LIMIT'

MEDIDOS = [
    {'NAME': 'AMAP Marche — Centro Agrometeo Locale, provincia di Ancona',
     'REGION': 'Marche', 'ENTITY_KIND': 'ORGANIZATION',
     'ROLE': 'centro agrometeo PROVINCIAL da agência regional',
     'CROP': 'cereali autunno-vernini, vite, olivo, fruttiferi',
     'ISSUE': 'fusariosi della spiga, infestanti, fenologia',
     'CHANNEL': 'PDF numerado semanal em meteo.regione.marche.it + e-mail',
     'CADENCE': 'WEEKLY_IN_SEASON',
     'SERIES_2026': ['n.613 08/04', 'n.615 22/04', 'n.616 29/04', 'n.617 06/05'],
     'NAMED_TECHNICIAN': None, 'TECHNICIAN_STATE': 'NO_NAMED_TECHNICIAN',
     'FARM_NETWORK': ('"le trappole per il monitoraggio ... installate nelle aziende '
                      'della rete di riferimento" — fazendas hospedam armadilhas'),
     'VERDICT': PARTIAL_LOCAL,
     'WHY': ('é o nó mais local que os cereais têm: província, semanal, na janela, '
             'com BBCH e rede de fazendas. E não tem pessoa — nem no boletim, nem na '
             'rede')},

    {'NAME': 'ALSIA Basilicata — SeDI (Servizio Difesa Integrata)',
     'REGION': 'Basilicata', 'ENTITY_KIND': 'ORGANIZATION',
     'ROLE': 'agência regional com técnicos e estações agrometeo',
     'CROP': 'cereali entre outras', 'ISSUE': 'difesa integrata',
     'CHANNEL': 'boletins por distrito, atrás de cadastro gratuito',
     'CADENCE': 'NOT_KNOWN',
     'DISTRICTS': ['Metapontino', "Alta Valle d'Agri", 'Valle Bradano e Lavallese'],
     'NAMED_TECHNICIAN': None, 'TECHNICIAN_STATE': 'TECHNICIAN_IDENTITY_NOT_PROVED',
     'VERDICT': NOT_MEASURED_ACCESS,
     'WHY': ('a agência descreve exatamente o padrão — "i tecnici ALSIA predispongono '
             'periodicamente bollettini fitosanitari per alcuni distretti" a partir de '
             'monitoramento de campo, modelos e estações próprias. E os boletins pedem '
             'cadastro. GATED ≠ ABSENT, e não crio conta para medir')},

    {'NAME': 'Agrifoglio — periódico da ALSIA',
     'REGION': 'Basilicata', 'ENTITY_KIND': 'ORGANIZATION',
     'ROLE': 'periódico técnico mensal, gratuito, com autores nomeados',
     'CROP': 'agricultura lucana', 'ISSUE': 'vários',
     'CHANNEL': 'alsia.it — números públicos', 'CADENCE': 'MONTHLY',
     'NAMED_TECHNICIAN': 'autores assinam (ex.: Giuseppe Malvasi, Filippo Radogna)',
     'TECHNICIAN_STATE': 'TECHNICIAN_IDENTITY_NOT_PROVED',
     'VERDICT': NOT_MEASURED_ACCESS,
     'WHY': ('canal público com autor nomeado — o formato certo. Mas a enumeração de '
             'números só devolveu até 2022; os de 2026 não foram alcançados por esta '
             'rota. NOT_MEASURED, não NOT_PRODUCTIVE')},

    {'NAME': "Consorzio Agrario dell'Emilia — Bollettino Tecnico",
     'REGION': 'Emilia-Romagna', 'ENTITY_KIND': 'ORGANIZATION',
     'ROLE': 'consórcio agrário com Centro di Saggio',
     'CROP': 'cereali', 'ISSUE': 'difesa', 'CHANNEL': 'caemilia.it',
     'CADENCE': 'NOT_KNOWN', 'NAMED_TECHNICIAN': None,
     'TECHNICIAN_STATE': 'TECHNICIAN_IDENTITY_NOT_PROVED',
     'VERDICT': NOT_MEASURED_ACCESS,
     'ATTEMPTS': ['503 via WebFetch', '503 via curl', 'cadeia TLS incompleta',
                  'retentativa com o CA bundle do proxy — mesma falha'],
     'WHY': ('quatro tentativas por rotas seguras diferentes. Não desabilitei '
             'verificação TLS para obter um positivo. NOT_MEASURED_ACCESS_LIMIT')},

    {'NAME': 'Puglia — rede de cereais',
     'REGION': 'Puglia', 'ENTITY_KIND': 'ORGANIZATION', 'ROLE': 'busca dirigida',
     'CROP': 'grano duro', 'ISSUE': 'fusariosi', 'CHANNEL': 'NOT_FOUND',
     'CADENCE': 'NOT_KNOWN', 'NAMED_TECHNICIAN': None,
     'TECHNICIAN_STATE': 'NO_NAMED_TECHNICIAN', 'VERDICT': COMMUNICATION_ONLY,
     'WHY': ('a maior região de grano duro do país, e o que a busca devolveu foi '
             'produção, preço e posição de mercado — CIA Puglia sobre preços, '
             'Italmopa sobre colheita. Nenhum boletim de campo de cereais. '
             'ORGANIZATION_COMMUNICATION')},

    {'NAME': 'Sicilia — Servizio fitosanitario regionale',
     'REGION': 'Sicilia', 'ENTITY_KIND': 'ORGANIZATION',
     'ROLE': 'serviço fitossanitário regional', 'CROP': 'grano duro',
     'ISSUE': 'norme tecniche', 'CHANNEL': 'portal regional',
     'CADENCE': 'NOT_KNOWN', 'NAMED_TECHNICIAN': None,
     'TECHNICIAN_STATE': 'NO_NAMED_TECHNICIAN', 'VERDICT': INSTITUTION_ONLY,
     'WHY': ('aprovou as normas técnicas de defesa integrada 2026 — e norma técnica '
             'não é sinal de campo. Lei já registrada em rodada anterior')},
]

LEITURAS = [
    {'ID': 'AMAP-MARCHE/AN-615', 'ARQUIVO': 'marche-amap-an-615-2026-04-22.txt',
     'PUBLISHED_AT': '2026-04-22', 'CROP': 'cereali autunno-vernini',
     'ISSUE': 'Fusarium spp.', 'REGION': 'Marche',
     'RELATIVE_TO_CASE': 'BEFORE_CASE',
     'SIGNAL_TYPES': ['TECHNICAL_WARNING', 'MANAGEMENT_RECOMMENDATION',
                      'WEATHER_CONCERN'],
     'QUOTE': ('"Fusarium spp. Interventi fitosanitari: Intervenire al termine della '
               'spigatura/inizio fioritura"')},
    {'ID': 'AMAP-MARCHE/AN-616', 'ARQUIVO': 'marche-amap-an-616-2026-04-29.txt',
     'PUBLISHED_AT': '2026-04-29', 'CROP': 'cereali autunno-vernini',
     'ISSUE': 'Fusariosi della spiga', 'REGION': 'Marche',
     'RELATIVE_TO_CASE': 'AFTER_CASE',
     'SIGNAL_TYPES': ['PHENOLOGY_OBSERVATION', 'FIELD_OBSERVATION',
                      'TECHNICAL_WARNING'],
     'QUOTE': ('"I cereali autunno-vernini sono nella maggior parte degli '
               'appezzamenti nella fase fenologica compresa fra inizio spigatura e '
               'inizio fioritura BBCH 51-61"')},
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
        reg['DOCUMENT_SCOPE'] = fl.escopo_do_documento(texto)
        reg['FACT_LOCATIONS'] = aceitas
        reg['PLACE_MENTIONS_REJECTED'] = sorted({r['PLACE'] for r in recusadas})
        reg['TIME'] = fl.tempo_do_fato(texto, L['PUBLISHED_AT'])
        reg['OCCURRENCE_NOT_INCIDENCE'] = fl.ocorrencia_nao_e_incidencia(
            [a['TYPE_OF_EVIDENCE'] for a in aceitas])
        reg['IN_WINDOW'] = (JANELA[0] <= datetime.date.fromisoformat(L['PUBLISHED_AT'])
                            <= JANELA[1])
        fora.append(reg)
    return fora


def medir():
    leituras = ler()
    locais = [m for m in MEDIDOS if m['VERDICT'] in (CEREAL_LOCAL_FIELD_SENSOR,
                                                     PARTIAL_LOCAL)]
    pessoas = [m for m in MEDIDOS if m['TECHNICIAN_STATE'] == 'TECHNICIAN_PUBLIC_SENSOR']
    por_medir = [m for m in MEDIDOS if m['VERDICT'] in (NOT_MEASURED, NOT_MEASURED_ACCESS)]

    achou = ('YES' if any(m['VERDICT'] == CEREAL_LOCAL_FIELD_SENSOR for m in MEDIDOS)
             else 'NOT_OBSERVED_IN_MEASURED_HIGH_PRIORITY_NETWORKS')
    duro = ('PROMISING' if locais
            else 'NOT_OBSERVED_IN_MEASURED_HIGH_PRIORITY_NETWORKS')

    return {
        'QUESTION_ID': 'CEREAL_LOCAL_FIELD_SENSOR_FALSIFICATION',
        'CASE_ID': 'IT-CASE-DURUM-FUSARIUM-001',
        'SOURCE_ID': 'DERIVED/IT-CEREAIS-FALSIFICACAO',
        'source': 'busca dirigida de falsificação — nenhuma execução paga',
        'SOURCE_LOCATION': 'web pública italiana',
        'FACT_LOCATION': 'ver CONTENTS_READ — por conteúdo, nunca por voz',
        'ORIGINAL_LANGUAGE': 'it', 'EVIDENCE_CLASS': 'PRIMARY_SOURCE_PROBE',
        'captured_at': datetime.date.today().isoformat(),
        'CAPTURED_AT': datetime.date.today().isoformat(),
        'CASE_DATE': CASE_DATE.isoformat(),
        'WINDOW': [JANELA[0].isoformat(), JANELA[1].isoformat()],
        'APIFY_RUNS': 0, 'APIFY_COST_USD': 0,

        'HYPOTHESIS_UNDER_TEST': (
            'em cereais italianos o sinal de safra fica apenas na instituição '
            'regional, sem camada pública local ou pessoal abaixo dela'),
        'RESULT': 'PARTIALLY_FALSIFIED',
        'WHAT_FELL': (
            'a parte "apenas regional". As Marche publicam por PROVÍNCIA, semanal, '
            'por um Centro Agrometeo Locale, com rede de fazendas hospedando '
            'armadilhas. Há um nó territorial abaixo da região'),
        'WHAT_HELD': (
            'a parte "sem camada pessoal". Nenhum boletim de cereais medido é '
            'assinado por uma pessoa, e a rede de fazendas é anônima'),

        'CAPS': {'ORGANIZATIONS': TETO_ORGS, 'PERSONS': TETO_PESSOAS,
                 'MEASURED': len(MEDIDOS),
                 'NOTE': 'parou quando a hipótese caiu pela metade'},
        'MEASURED_BY_REGION': {m['REGION']: m['VERDICT'] for m in MEDIDOS},
        'ORGANIZATIONS': MEDIDOS,
        'PERSONS_FOUND': [],
        'STILL_NOT_MEASURED': [m['NAME'] for m in por_medir],

        'CONTENTS_READ': leituras, 'CONTENTS_READ_COUNT': len(leituras),
        'SIGNALS_BEFORE_CASE': [L['ID'] for L in leituras
                                if L['RELATIVE_TO_CASE'] == 'BEFORE_CASE'],
        'SIGNALS_AFTER_CASE': [L['ID'] for L in leituras
                               if L['RELATIVE_TO_CASE'] == 'AFTER_CASE'],
        'EARLIER_THAN_REGION': [],
        'SAME_DATE': [],
        'RETROSPECTIVE': [],

        'ARCHITECTURE': {
            'CEREALS': 'REGIÃO → CENTRO AGROMETEO PROVINCIAL → REDE DE FAZENDAS (anônima)',
            'VINE': 'OBSERVADOR CIDADÃO → TÉCNICO NOMEADO → CONSÓRCIO → INSTITUIÇÃO',
            'DIFFERENCE': 'a de cereais não tem pessoa em elo nenhum',
        },

        'LOCAL_ORGANIZATION_SENSOR': {
            'STATE': 'PROVED', 'CROP_SCOPE': 'cereali autunno-vernini',
            'GEOGRAPHIC_SCOPE': 'Marche — provincia di Ancona',
            'WHY': 'Centro Agrometeo Locale, provincial, semanal, com rede de fazendas'},
        'TECHNICAL_PERSON_SENSOR': {
            'STATE': 'NOT_PROVED', 'CROP_SCOPE': 'cereais',
            'GEOGRAPHIC_SCOPE': 'nenhuma das cinco regiões medidas',
            'WHY': 'nenhum boletim de cereais é assinado por pessoa'},
        'PRODUCER_PERSON_SENSOR': {
            'STATE': 'NOT_PROVED', 'CROP_SCOPE': 'cereais',
            'GEOGRAPHIC_SCOPE': 'nenhuma',
            'WHY': ('as "aziende della rete di riferimento" das Marche são produtores '
                    'contribuindo com campo — e entram sem nome, pela organização')},

        'LAWS': [
            'NO_IN_MEASURED_NETWORK ≠ NO_IN_ITALY',
            'GATED ≠ ABSENT',
            'NOT_MEASURED_ACCESS_LIMIT ≠ NOT_PRODUCTIVE',
            'LOCAL_ORGANIZATION_SENSOR ≠ TECHNICAL_PERSON_SENSOR',
            'PLANNED_ACTION_DATE ≠ FACT_TIME',
            'FUTURE_DATE ≠ FACT_TIME',
            'NORMA TÉCNICA ≠ SINAL DE CAMPO',
        ],

        # As duas chaves conviviam sem dizer QUE espécie de sensor cada uma
        # media, e lado a lado liam-se como contradição: uma diz YES, a outra diz
        # NOT_OBSERVED. Não são a mesma pergunta. A organização local existe; a
        # pessoa não. O achado não muda — muda o nome, que passa a dizer de quem
        # ele fala.
        #
        #     ORGANIZATION_SENSOR ≢ HUMAN_PERSON_SENSOR
        'CEREAL_LOCAL_FIELD_ORGANIZATION_SENSOR_FOUND': 'YES',
        'CEREAL_LOCAL_HUMAN_PERSON_SENSOR_FOUND': achou,
        'WHY_TWO_KEYS': (
            'organização local prospectiva em cereais: PROVADA (Centro Agrometeo '
            'Locale das Marche). Pessoa pública prospectiva em cereais: NÃO '
            'OBSERVADA nas redes de alta prioridade medidas. São dois estados, e '
            'juntá-los num só produziria uma contradição aparente ou uma promoção '
            'silenciosa'),
        'DURUM_FUSARIUM_LOCAL_HUMAN_SENSOR': duro,
        'IN_CEREALS_MEASURED_SIGNAL_ARCHITECTURE': 'REGIONAL_INSTITUTION_DOMINANT',
        'ARCHITECTURE_MUST_CARRY': (
            'dominante NÃO quer dizer exclusivamente regional: a instituição desce até '
            'a província e se apoia numa rede de fazendas. Chamar isso de "só a '
            'região" perderia o nó mais local que os cereais têm'),

        'HUMAN_SENSOR_ITALY_LINE': 'FROZEN_AFTER_CURRENT_EVIDENCE',
        'HUMAN_SENSOR_FREEZE_MEANS': (
            'a linha de sensores humanos da Itália não recebe nova busca. O que ficou '
            'por medir está nomeado e continua NOT_MEASURED — congelar não converte '
            'nenhum NOT_MEASURED em NOT_PRODUCTIVE'),
        'RECOMMENDATION': {
            'COLLECT_RECURRENTLY': (
                'os notiziari agrometeorológicos PROVINCIAIS das Marche, ao lado dos '
                'boletins regionais de Toscana, Umbria, FVG e Veneto. São PDF '
                'numerados, semanais, na janela, com BBCH — e a província é a melhor '
                'resolução que os cereais oferecem'),
            'DO_NOT_EXPECT': 'pessoa nomeada nem antecedência sobre a instituição',
            'CLOSE_THIS_LINE': (
                'a pergunta sobre camada humana pessoal em cereais está respondida no '
                'que era mensurável: não há. Reabrir exigiria as portas que ficaram '
                'atrás de cadastro ou de falha de transporte'),
            'STILL_UNMEASURED': [m['NAME'] for m in por_medir],
        },
        'STILL_FORBIDDEN_TO_WRITE': ['ITALY OPPORTUNITY', 'SALES OPPORTUNITY',
                                     'ADAMA SHOULD ACT', 'MARKET GAP',
                                     'DOES_NOT_EXIST_IN_ITALY'],
    }


def main():
    out = medir()
    os.makedirs(os.path.dirname(DEST), exist_ok=True)
    with open(DEST, 'w', encoding='utf-8') as fh:
        json.dump(out, fh, ensure_ascii=False, indent=2)
    print('hipótese:', out['RESULT'])
    print('  caiu :', out['WHAT_FELL'][:96])
    print('  ficou:', out['WHAT_HELD'][:96])
    print()
    for m in out['ORGANIZATIONS']:
        print('   %-12s %-52s %s' % (m['REGION'], m['NAME'][:52], m['VERDICT']))
    print()
    for L in out['CONTENTS_READ']:
        print('   %-20s %s  %-12s  FACT=%s' % (
            L['ID'], L['PUBLISHED_AT'], L['RELATIVE_TO_CASE'],
            [(a['FACT_LOCATION'], a['PRECISION_SOURCE']) for a in L['FACT_LOCATIONS']]))
        print('      FACT_TIME:', L['TIME']['FACT_TIME'])
    print()
    print('CEREAL_LOCAL_FIELD_ORGANIZATION_SENSOR_FOUND =',
          out['CEREAL_LOCAL_FIELD_ORGANIZATION_SENSOR_FOUND'])
    print('CEREAL_LOCAL_HUMAN_PERSON_SENSOR_FOUND       =',
          out['CEREAL_LOCAL_HUMAN_PERSON_SENSOR_FOUND'])
    print('DURUM_FUSARIUM_LOCAL_HUMAN_SENSOR  =', out['DURUM_FUSARIUM_LOCAL_HUMAN_SENSOR'])
    print('SIGNAL_ARCHITECTURE                =', out['IN_CEREALS_MEASURED_SIGNAL_ARCHITECTURE'])
    for k in ('LOCAL_ORGANIZATION_SENSOR', 'TECHNICAL_PERSON_SENSOR',
              'PRODUCER_PERSON_SENSOR'):
        print('   %-30s %-12s %s' % (k, out[k]['STATE'], out[k]['GEOGRAPHIC_SCOPE']))
    print('->', os.path.relpath(DEST, ROOT))


if __name__ == '__main__':
    main()
