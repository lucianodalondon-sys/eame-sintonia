#!/usr/bin/env python3
"""
ENRIQUECIMENTO DAS 9 CONVERGENCIAS CONFIRMADAS — evidencia nova, status intocado.

    py scripts/it_enriquecimento.py

A REGRA QUE MANDA AQUI
------------------------
    NAO MEXER EM STATUS. NAO MEXER EM SCORE. NAO PROMOVER A MAO.

Enriquecer e ANEXAR evidencia nova que passou pelo mesmo metodo. Se a evidencia nova
mudasse o score, quem muda o score e a regua — e a regua nao roda nesta branch.

O QUE A LEITURA DAS NOVE REVELOU, E NAO ESTAVA DITO EM LUGAR NENHUM
---------------------------------------------------------------------
Sete das nove sao O5_REGULATORY_PREPARATION com GEOGRAPHY = GEO_EU, e as familias de
evidencia das nove sao, sem excecao, regulatorias, de rotulo, de mercado ou de peso
economico. NENHUMA das nove carrega FIELD_SIGNAL, PUBLIC_VOICE ou AGROMET.

    AS NOVE CONFIRMADAS SAO UM CALENDARIO REGULATORIO, NAO UMA OBSERVACAO DE CAMPO.

Isso e coerente com o que o SINTONIA ja provou duas vezes: BETTER TIMING sobrevive no
vencimento regulatorio e NAO sobrevive na voz publica. Mas significa que, hoje, a
resposta de "o que esta acontecendo AGORA" nao vem das nove.

E o enriquecimento desta missao ataca exatamente isso.
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SAIDA = os.path.join(ROOT, 'data', 'samples', 'IT-CRUZAMENTO-V1')
CAPTURA = '2026-09-03'

ENRIQUECIMENTOS = [
    {
        'OPPORTUNITY_ID': 'OPP_88CC35C57C7B',
        'CROP': 'CROP_SOYBEAN', 'SUBSTANCE': 'IMAZAMOX',
        'EU_LIMIT_DATE': '2027-06-30', 'DAYS_TO_DATE_AT_REFERENCE': 301,
        'STATUS_BEFORE': 'OPPORTUNITY_CONFIRMED', 'STATUS_AFTER': 'OPPORTUNITY_CONFIRMED',
        'SCORE_BEFORE': 9, 'SCORE_AFTER': 9,
        'WHAT_IS_NEW': 'primeira evidencia ITALIANA, DATADA e de CAMPO ligada a esta substancia',
        'NEW_EVIDENCE': {
            'LAYER': 'FIELD_BULLETIN', 'DATE': '2026-08-21',
            'DOC': 'Bollettino di produzione integrata e biologica Piacenza N. 27 del 21/08/2026',
            'SECTION': 'FAGIOLINO',
            'QUOTE_IT': ('In pre-emergenza contro graminacee e dicotiledoni utilizzare Clomazone o '
                         'Pendimetalin(*). In post-emergenza contro dicotiledoni utilizzare Imazamox '
                         'e Bentazone. In post-emergenza contro graminacee utilizzare '
                         'Quizalofop-p-etile, Propaquizafop o Ciclossidim.'),
            'EVIDENCE_PATH': 'data/samples/IT-CAMPO-V1/IT-BOLLETTINI-ER-SOSTANZE-ATTIVE-V1.json',
        },
        'HONEST_LIMIT': ('a secao e FAGIOLINO, NAO soia. A oportunidade e de soja. A ligacao e de '
                         'SUBSTANCIA numa cultura vizinha da mesma familia (LEGUMINOSE, 70 pares de '
                         'rotulo ADAMA), e nao substitui evidencia de campo em soja. Forcar isso '
                         'seria cruzar sem chave.'),
        'WHY_IT_STILL_MATTERS': ('mostra que, 301 dias antes do limite de aprovacao UE, o servico '
                                 'regional ainda posiciona imazamox como a solucao de pos-emergencia '
                                 'contra dicotiledoneas. A janela de preparacao existe e esta aberta.'),
    },
    {
        'OPPORTUNITY_ID': 'OPP_3965565ACFCC',
        'CROP': 'CROP_GRAPEVINE', 'SUBSTANCE': 'FOLPET',
        'EU_LIMIT_DATE': '2039-10-31', 'DAYS_TO_DATE_AT_REFERENCE': 4807,
        'STATUS_BEFORE': 'OPPORTUNITY_CONFIRMED', 'STATUS_AFTER': 'OPPORTUNITY_CONFIRMED',
        'SCORE_BEFORE': 8, 'SCORE_AFTER': 8,
        'WHAT_IS_NEW': ('duas evidencias italianas datadas: um TETO DE RESISTENCIA que nomeia folpet, '
                        'e DUAS derogas de emergencia com folpet numa cultura diferente'),
        'NEW_EVIDENCE': {
            'LAYER': 'FIELD_BULLETIN + REGULATORY_EVENT', 'DATE': '2026-08-21',
            'DOC': 'Bollettino Parma N. 27 del 21/08/2026',
            'SECTION': 'POMODORO DA INDUSTRIA',
            'QUOTE_IT_1': 'Tra Captano, Folpet e Fluazinam Max 4',
            'QUOTE_IT_2': ('In data 13 maggio 2026 ... uso eccezionale del prodotto fitosanitario '
                           'FOLPEC 50 SC, contenente la sostanza attiva folpet, per il contenimento '
                           'della maculatura bruna (Stemphylium vesicarium) sulla coltura del pero - '
                           'impiego consentito dal 28/04/2026 al 25/08/2026.'),
            'QUOTE_IT_3': ('In data 6 maggio ... uso eccezionale del prodotto fitosanitario FOLDER 80 WG, '
                           'contenente la sostanza attiva folpet, ... sulla coltura del pero - impiego '
                           'consentito dal 28/04/2026 al 25/08/2026.'),
            'EVIDENCE_PATH': 'data/samples/IT-CAMPO-V1/IT-BOLLETTINI-ER-SOSTANZE-ATTIVE-V1.json',
        },
        'HONEST_LIMIT': ('a oportunidade e de VITE. As tres citacoes sao de POMODORO DA INDUSTRIA e de '
                         'PERO. Nenhuma prova nada sobre vite. FOLPEC 50 SC e FOLDER 80 WG NAO sao '
                         'produtos ADAMA. A ligacao e de SUBSTANCIA.'),
        'WHY_IT_STILL_MATTERS': ('o folpet italiano vive dentro de um teto compartilhado com captano e '
                                 'fluazinam (Max 4 no total) e e chamado duas vezes em deroga na mesma '
                                 'campanha. Isso descreve a POSICAO da molecula no calendario italiano, '
                                 'que uma data UE de 2039 sozinha nao descreve.'),
    },
    {
        'OPPORTUNITY_ID': 'OPP_576D71D702F0',
        'CROP': 'CROP_MAIZE', 'SUBSTANCE_VIA_PRODUCT': 'PIRIMICARB (APHOX, APHOX 50)',
        'STATUS_BEFORE': 'OPPORTUNITY_CONFIRMED', 'STATUS_AFTER': 'OPPORTUNITY_CONFIRMED',
        'SCORE_BEFORE': 9, 'SCORE_AFTER': 9,
        'WHAT_IS_NEW': ('o boletim regional NOMEIA pirimicarb como intervencao, com LIMIAR declarado, '
                        'e na mesma linha marca a substancia como candidata a substituicao'),
        'NEW_EVIDENCE': {
            'LAYER': 'FIELD_BULLETIN', 'DATE': '2026-09-02',
            'DOC': 'Bollettino Forli-Cesena, Ravenna e Rimini N. 28 del 02/09/2026',
            'SECTION': 'MELO',
            'QUOTE_IT': ('Al superamento della soglia di 10 colonie vitali su 100 organi controllati '
                         'con infestazione in atto intervenire con Pirimicarb(*), attivi contro l’afide '
                         'verde o Sali potassici degli acidi grassi. ... (*) Sostanza attiva Candidata '
                         'alla Sostituzione'),
            'CROSSING_ID': 'IT-X-2026-001',
            'EVIDENCE_PATH': 'data/samples/IT-CRUZAMENTO-V1/IT-CRUZAMENTOS-V1.json#IT-X-2026-001',
        },
        'HONEST_LIMIT': ('a oportunidade e de MAIS; a citacao e da secao MELO. APHOX e APHOX 50 estao nos '
                         'PRODUCT_RELATIONSHIPS desta oportunidade E tem par de rotulo lido em MELO x '
                         'AFIDI x Eriosoma spp na LINHA DA TABELA. A evidencia nova e forte, e e de '
                         'outra cultura.'),
        'WHY_IT_STILL_MATTERS': ('e a unica das nove que ganhou, nesta rodada, uma evidencia de campo '
                                 'CORRENTE (1 dia de idade) que nomeia a substancia de um produto ADAMA '
                                 'e declara um limiar operacional.'),
        'RISK_FLAG': ('pirimicarb aparece marcado como Sostanza attiva Candidata alla Sostituzione. Isto '
                      'e RISCO DE PORTFOLIO e deveria alimentar uma leitura O5, nao so a O2 de mercado.'),
    },
    {
        'OPPORTUNITY_ID': 'OPP_8EA4F5C0D3F4',
        'CROP': 'CROP_BARLEY', 'SUBSTANCE_VIA_PRODUCT': 'AZOXYSTROBIN (CUSTODIA ULTRA, MIRADOR TURBO)',
        'STATUS_BEFORE': 'OPPORTUNITY_CONFIRMED', 'STATUS_AFTER': 'OPPORTUNITY_CONFIRMED',
        'SCORE_BEFORE': 8, 'SCORE_AFTER': 8,
        'WHAT_IS_NEW': 'teto de intervencoes e gestao de resistencia que nomeia azoxystrobin, com data',
        'NEW_EVIDENCE': {
            'LAYER': 'FIELD_BULLETIN', 'DATE': '2026-08-21',
            'DOC': 'Bollettino Parma N. 27 del 21/08/2026', 'SECTION': 'POMODORO DA INDUSTRIA',
            'QUOTE_IT': ('Si ricorda l’importanza di effettuare una rotazione dei principi attivi a '
                         'disposizione per la difesa e di rispettare le dosi (non vanno ridotte '
                         'arbitrariamente) e il numero massimo di interventi al fine di evitare '
                         'l’instaurarsi di resistenze. ... Tra Pyraclostrobin e Azoxystrobin Max 3'),
            'EVIDENCE_PATH': 'data/samples/IT-CAMPO-V1/IT-BOLLETTINI-ER-SOSTANZE-ATTIVE-V1.json',
        },
        'HONEST_LIMIT': ('a oportunidade e de ORZO. A citacao e de POMODORO DA INDUSTRIA. Nao prova nada '
                         'sobre cevada. E ligacao de SUBSTANCIA e de PRATICA (gestao de resistencia).'),
        'WHY_IT_STILL_MATTERS': 'mostra que o teto de estrobilurina e um limite operacional real e escrito na Italia',
    },
    {'OPPORTUNITY_ID': 'OPP_2BDE8FC566CE', 'SUBSTANCE': 'FENPROPIDIN', 'CROP': 'CROP_SUGAR_BEET',
     'EU_LIMIT_DATE': '2027-05-15',
     'WHY_IT_LOOKED_CLOSED': (
         'zero ocorrencias de "fenpropidin" nos 14 boletins, e a scheda tecnica de cercospora '
         'do Servizio Fitosanitario ER — que eu li — nao nomeia fungicida nenhum. Eu tinha '
         'registrado NOT_ENRICHED_ROUTE_READ_AND_REFUTED.'),
     'WHAT_THE_ADVERSARIAL_PASS_FOUND': (
         'o elo nao estava na palavra "fenpropidin": estava no PAR DE ROTULO. A ADAMA tem '
         'EXATAMENTE UMA linha de rotulo BARBABIETOLA x CERCOSPORA em todo o radar — '
         'IT-LBL-409, SPYRALE, registro 009757, com a citacao "Barbabietola da zucchero '
         'Cercosporiosi (Cercospora beticola) Oidio (Erysiphe betae) ... 2 trattamenti ad '
         'intervalli di 21 giorni". SPYRALE e difenoconazolo + fenpropidin, e fenpropidin e '
         'a substancia desta oportunidade.'),
     'NEW_EVIDENCE': {
         'LAYER': 'FIELD_BULLETIN', 'DATE': '2026-08-06',
         'DOC': 'Bollettini interprovinciali ER N.26 — Reggio Emilia 06/08/2026 e Modena 04/08/2026',
         'SECTION': 'BARBABIETOLA DA ZUCCHERO',
         'QUOTE_IT': ('BARBABIETOLA DA ZUCCHERO Fase fenologica: accrescimento fittone-maturazione '
                      'Difesa Cercospora: presenza della malattia modesta. Proseguire la difesa '
                      'intervenendo con Prodotti rameici o miscele di rame e Zolfo.'),
         'VERIFICATION': 'SURVIVED_ADVERSARIAL_REFUTATION',
         'EVIDENCE_PATH': 'data/samples/IT-CAMPO-V1/IT-CAMPO-SINAIS-VERIFICADOS-V1.json'},
     'THIS_ENRICHMENT_COOLS_THE_CASE_INSTEAD_OF_WARMING_IT': (
         'e por isso que ele vale. O boletim diz "presenza della malattia MODESTA" — pressao '
         'BAIXA, declarada pela propria fonte. A recomendacao e RAME e ZOLFO, nao um IBE. '
         'SPYRALE nao e nomeado em nenhum dos 14 boletins. E SPYRALE e um registro do '
         'Ministero detido pela ADAMA, NAO um dos 51 produtos do catalogo comercial — '
         '51 comerciais != 163 regulatorios continua valendo aqui.'),
     'STATUS_BEFORE': 'OPPORTUNITY_CONFIRMED', 'STATUS_AFTER': 'OPPORTUNITY_CONFIRMED',
     'SCORE_BEFORE': 9, 'SCORE_AFTER': 9,
     'STATE': 'ENRICHED_AND_COOLED'},
]

SEM_ENRIQUECIMENTO = [
    {'OPPORTUNITY_ID': 'OPP_6E18A133EE14', 'SUBSTANCE': 'BUPIRIMATE', 'CROP': 'CROP_TOMATO',
     'EU_LIMIT_DATE': '2027-01-31',
     'WHY': 'zero ocorrencias de "bupirimate" nos 14 boletins lidos.',
     'NOTE': ('e a data-limite MAIS PROXIMA das nove: 151 dias na data de referencia. A ausencia de '
              'mencao no campo torna a preparacao regulatoria ainda mais o unico eixo desta.'),
     'STATE': 'NOT_ENRICHED'},
    {'OPPORTUNITY_ID': 'OPP_886307860F79', 'SUBSTANCE': 'MESOTRIONE', 'CROP': 'CROP_MAIZE',
     'EU_LIMIT_DATE': '2032-05-31',
     'WHY': 'zero ocorrencias de "mesotrione" nos 14 boletins lidos.', 'STATE': 'NOT_ENRICHED'},
    {'OPPORTUNITY_ID': 'OPP_E6200AA0FA63', 'SUBSTANCE': 'FLORASULAM', 'CROP': 'CROP_BARLEY',
     'EU_LIMIT_DATE': '2030-12-31',
     'WHY': 'zero ocorrencias de "florasulam" nos 14 boletins lidos.',
     'NOTE': ('cereal de inverno em setembro esta fora de janela de diserbo. A ausencia aqui e '
              'esperada e nao diz nada sobre a molecula.'),
     'STATE': 'NOT_ENRICHED_OUT_OF_SEASON'},
    {'OPPORTUNITY_ID': 'OPP_AF16E6A6B8B3', 'CROP': 'CROP_GRAPEVINE',
     'WHY': ('a vite aparece nos boletins, mas nenhuma das 25 marcas ADAMA desta oportunidade '
             'aparece por nome — e nenhuma substancia dela foi isolada nesta passagem com '
             'fronteira de palavra na secao VITE.'),
     'NOTE': 'e a oportunidade mais recente das nove (sinal de 5 dias) e continua sem evidencia de campo nova',
     'STATE': 'NOT_ENRICHED'},
]

LEI_DA_AUSENCIA = ('zero ocorrencias nos 14 boletins da Emilia-Romagna dos ultimos 30 dias significa '
                   'ZERO NESTA LEITURA. Nao significa que a molecula sumiu do campo italiano, nem que '
                   'nao e recomendada, nem que outra regiao nao a cita. O boletim de produzione '
                   'integrata nomeia SUBSTANCIA ATIVA e nao marca: nenhum dos 51 produtos comerciais '
                   'ADAMA aparece por nome em nenhum dos 14 documentos.')


def escrever():
    os.makedirs(SAIDA, exist_ok=True)
    corpo = {
        'DATASET': 'IT-ENRIQUECIMENTO-CONFIRMADAS-V1',
        'SOURCE': ('boletins do Servizio Fitosanitario Emilia-Romagna dos ultimos 30 dias, lidos por '
                   'rota propria; cruzados contra activeIngredients e productRelationships do pacote '
                   'canonico V2.1'),
        'SOURCE_ID': 'IT-ENRIQUECIMENTO-V1',
        'CAPTURED_AT': CAPTURA,
        'REFERENCE_DATE': CAPTURA,
        'RULE': 'NAO MEXER EM STATUS. NAO MEXER EM SCORE. NAO PROMOVER A MAO.',
        'STRUCTURAL_FINDING': ('7 das 9 confirmadas sao O5_REGULATORY_PREPARATION com GEOGRAPHY=GEO_EU, '
                               'e NENHUMA das 9 carrega FIELD_SIGNAL, PUBLIC_VOICE ou AGROMET entre as '
                               'suas EVIDENCE_FAMILIES. As nove confirmadas sao um calendario '
                               'regulatorio, nao uma observacao de campo.'),
        'ENRICHED': len(ENRIQUECIMENTOS),
        'NOT_ENRICHED': len(SEM_ENRIQUECIMENTO),
        'STATUS_CHANGES': 0,
        'SCORE_CHANGES': 0,
        'ABSENCE_LAW': LEI_DA_AUSENCIA,
        'ENRICHMENTS': ENRIQUECIMENTOS,
        'NOT_ENRICHED_AND_WHY': SEM_ENRIQUECIMENTO,
    }
    caminho = os.path.join(SAIDA, 'IT-ENRIQUECIMENTO-CONFIRMADAS-V1.json')
    with open(caminho, 'w', encoding='utf-8') as fh:
        json.dump(corpo, fh, ensure_ascii=False, indent=1)
    return caminho, corpo


if __name__ == '__main__':
    c, corpo = escrever()
    print('escrito: %s' % os.path.relpath(c, ROOT))
    print()
    print('ENRICHED       %d  -> %s' % (corpo['ENRICHED'], ', '.join(e['OPPORTUNITY_ID'] for e in ENRIQUECIMENTOS)))
    print('NOT_ENRICHED   %d  -> %s' % (corpo['NOT_ENRICHED'], ', '.join(e['OPPORTUNITY_ID'] for e in SEM_ENRIQUECIMENTO)))
    print('STATUS_CHANGES %d' % corpo['STATUS_CHANGES'])
    print('SCORE_CHANGES  %d' % corpo['SCORE_CHANGES'])
