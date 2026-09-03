#!/usr/bin/env python3
"""
CRUZAMENTOS ITALIA — onde duas fontes independentes se encontram sobre a mesma chave.

    py scripts/it_cruzamentos.py

O QUE E UM CRUZAMENTO AQUI
----------------------------
Duas ou mais fontes INDEPENDENTES que falam da mesma CULTURA x ALVO x GEOGRAFIA numa
janela de tempo, e uma relacao com a ADAMA que se sustenta sem inventar nada.

    SEM CHAVE REAL, NAO CRUZA.
    Aproximar duas coisas porque ficariam bem juntas na tela e o oposto disto.

A ESCADA DE LIGACAO COM A ADAMA — ela nao se achata
-----------------------------------------------------
    LINHA_DA_TABELA        o rotulo une CULTURA e ALVO na MESMA linha. E o mais forte.
    BLOCO_DA_CULTURA       o rotulo trata a cultura num bloco e cita o alvo dentro dele.
    DECLARACAO_DE_PRODUTO  o rotulo diz separadamente que atua no alvo e que se usa na cultura.
    SUBSTANCIA_ATIVA       a ADAMA detem a substancia; NENHUM par de rotulo foi lido para
                           esta cultura x alvo. Isto e PORTFOLIO RELATION, e so.

    PORTFOLIO RELATION != LABEL AUTHORIZATION.
    E um par nao lido nunca vira "a ADAMA nao tem produto para X" — vira NAO LEMOS.

O QUE NENHUM CRUZAMENTO DAQUI PROVA
-------------------------------------
Nao prova incidencia regional, nao prova incidencia italiana, nao prova demanda, nao prova
venda, nao prova pedido de revenda, nao prova market share. Um boletim que recomenda uma
substancia prova que o servico regional a recomendou naquela cultura naquela data.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SAIDA = os.path.join(ROOT, 'data', 'samples', 'IT-CRUZAMENTO-V1')
CAPTURA = '2026-09-03'

CRUZAMENTOS = [

    {
        'ID': 'IT-X-2026-001',
        'TITLE': 'Melo x afide lanigero: o boletim recomenda a substancia da ADAMA pelo nome, '
                 'com limiar, e na mesma linha marca a substancia como candidata a substituicao',
        'CROP': 'MELO',
        'TARGET': 'AFIDE LANIGERO (Eriosoma lanigerum)',
        'GEOGRAPHY': 'Emilia-Romagna — Forli-Cesena, Ravenna, Rimini',
        'GEOGRAPHY_STATE': 'DECLARED_BY_THE_DOCUMENT',
        'WINDOW': '2026-09-02 (bollettino n. 28) — janela corrente',
        'SOURCES_CROSSED': 3,
        'CROSSING_TYPE': 'FIELD_BULLETIN x PUBLIC_VOICE_TRANSCRIPT x ADAMA_LABEL_PAIR',
        'EVIDENCE': [
            {'LAYER': 'FIELD_BULLETIN', 'SOURCE': 'Servizio Fitosanitario Emilia-Romagna',
             'DOC': 'Bollettino di produzione integrata e biologica Forli-Cesena, Ravenna e Rimini N. 28 del 02/09/2026',
             'DATE': '2026-09-02',
             'QUOTE_IT': ('Afide lanigero: situazione al momento ben controllata. Momento caratterizzato '
                          'da un leggero aumento di presenza di E. lanigerum. Monitorare la presenza '
                          'dell’afide. Al superamento della soglia di 10 colonie vitali su 100 organi '
                          'controllati con infestazione in atto intervenire con Pirimicarb(*), attivi '
                          'contro l’afide verde o Sali potassici degli acidi grassi. Per favorire la '
                          'presenza degli antagonisti naturali (tra cui il parassitoide Aphelinus mali) '
                          'importante limitare per quanto possibile l’impiego di piretroidi e spinosine. '
                          '(*) Sostanza attiva Candidata alla Sostituzione'),
             'EVIDENCE_PATH': 'data/samples/IT-CAMPO-V1/IT-BOLLETTINI-ER-SOSTANZE-ATTIVE-V1.json'},
            {'LAYER': 'PUBLIC_VOICE_TRANSCRIPT_ONLY', 'SOURCE': 'Agricast — progetto Riduci (Gruppo Operativo PEI-AGRI, Emilia-Romagna)',
             'DOC': 'Riduci – Ridurre gli input chimici e gestire le nuove emergenze fitosanitarie nelle colture arboree',
             'DATE': '2026-05-11', 'TIMESTAMP_S': 345.5,
             'QUOTE_IT': ('A questo si aggiunge la progressiva riduzione degli insetticidi ad ampio spettro '
                          'che ha modificato gli equilibri del frutteto. Da un lato ha ridotto alcune '
                          'possibilità di intervento diretto, dall’altro ha reso più evidente il ruolo degli '
                          'antagonisti naturali, come Aphelinus mali, nel contenimento dell’afide lanigero.'),
             'ONLY_IN_TRANSCRIPT': True,
             'WHY_ONLY_IN_TRANSCRIPT': ('a descricao do episodio (751 caracteres) fala de "difesa piu mirata e '
                                        'meno input chimici" e nao contem afide lanigero, Aphelinus mali, '
                                        'insetticidi ad ampio spettro nem o mecanismo. A fala tem 14.214 '
                                        'caracteres. Razao legenda:fala = 1:19.'),
             'EVIDENCE_PATH': 'data/samples/IT-VOZ-AUDIO-V1/IT-VOZ-AUDIO-TRANSCRICOES-V1.json#70245845'},
            {'LAYER': 'ADAMA_LABEL_PAIR', 'SOURCE': 'rotulo autorizado, Ministero della Salute',
             'DOC': '5 pares lidos DENTRO da linha da tabela',
             'PAIRS': ['IT-LBL-024 PIRIMOR 50 | MELO | AFIDI | Eriosoma spp',
                       'IT-LBL-231 PIRIMOR 17,5 | MELO | AFIDI | Eriosoma spp',
                       'IT-LBL-992 APHOX | MELO | AFIDI | Eriosoma spp',
                       'IT-LBL-1544 APHOX 50 | MELO | AFIDI | Eriosoma spp',
                       'IT-LBL-1592 XINTECH 50 | MELO | AFIDI | Eriosoma spp'],
             'LINK_STRENGTH': 'LINHA_DA_TABELA',
             'EVIDENCE_PATH': 'v21/productRelationships.json (pacote canonico V2.1)'},
        ],
        'ADAMA_RELATION': ('LINHA_DA_TABELA — o nivel mais forte da escada. Cinco registros ADAMA trazem '
                           'MELO x AFIDI x Eriosoma spp na MESMA linha da tabela do rotulo, e pirimicarb '
                           'e a substancia ativa de PIRIMOR e APHOX. O boletim oficial nomeia pirimicarb '
                           'como a intervencao ao ultrapassar o limiar.'),
        'ADAMA_RISK_ON_THE_SAME_LINE': ('o mesmo boletim marca pirimicarb com (*) = Sostanza attiva Candidata '
                                        'alla Sostituzione. A solucao recomendada e a molecula sob pressao '
                                        'regulatoria sao a mesma. Isto e risco de portfolio, nao oportunidade.'),
        'OPPORTUNITY_LINK': ['OPP_576D71D702F0 (APHOX/APHOX 50 estao entre os PRODUCT_RELATIONSHIPS)',
                             'OPP_DA4B5954F72A (MELO, Emilia-Romagna)',
                             'OPP_E1A1D73F07BF (MELO, competitive opening)'],
        'ACTION_MAP': ['SCIENCE_TECHNICAL', 'MARKET_DEVELOPMENT', 'REGULATION_PORTFOLIO'],
        'PROVES': ('que em 2026-09-02 o servico fitossanitario da Emilia-Romagna, num documento publico e '
                   'datado, recomendou pirimicarb ao ultrapassar um limiar declarado de 10 colonias vivas '
                   'em 100 orgaos controlados em melo; que a ADAMA tem cinco registros com esse par lido '
                   'na linha da tabela; e que o mesmo documento marca a substancia como candidata a '
                   'substituicao.'),
        'DOES_NOT_PROVE': ('nao prova incidencia de afide lanigero na Emilia-Romagna — o proprio boletim diz '
                           '"situazione al momento ben controllata"; nao prova incidencia italiana; nao prova '
                           'demanda, venda, pedido de revenda nem share; nao prova que a substituicao vai '
                           'acontecer nem quando.'),
        'PROVENANCE': 'REAL_SOURCE + SINTONIA_CROSSING',
        'CLIENT_SAFE': True,
    },

    {
        'ID': 'IT-X-2026-002',
        'TITLE': 'Noce x necrosi apicale bruna: uma deroga datada com fluazinam, e a voz '
                 'que explica por que a doenca e dificil — dita, nao escrita',
        'CROP': 'NOCE',
        'TARGET': 'NECROSI APICALE BRUNA (complexo de patogenos)',
        'GEOGRAPHY': 'Emilia-Romagna (deroga regional)',
        'GEOGRAPHY_STATE': 'DECLARED_BY_THE_DOCUMENT',
        'WINDOW': 'deroga concedida em 2026-05-07, maximo 2 intervencoes',
        'SOURCES_CROSSED': 2,
        'CROSSING_TYPE': 'REGULATORY_EVENT x PUBLIC_VOICE_TRANSCRIPT',
        'EVIDENCE': [
            {'LAYER': 'REGULATORY_EVENT', 'SOURCE': 'Regione Emilia-Romagna, via bollettino fitosanitario',
             'DOC': 'Bollettino Forli-Cesena, Ravenna e Rimini N. 28 del 02/09/2026',
             'DATE': '2026-09-02',
             'QUOTE_IT': ('In data 7 maggio 2026 è stata concessa la deroga valida per il territorio della '
                          'Regione Emilia-Romagna per l’esecuzione di massimo 2 interventi con la sostanza '
                          'attiva fluazinam per il contenimento della necrosi apicale bruna sulla coltura del noce.'),
             'EVIDENCE_PATH': 'data/samples/IT-CAMPO-V1/IT-BOLLETTINI-ER-SOSTANZE-ATTIVE-V1.json'},
            {'LAYER': 'PUBLIC_VOICE_TRANSCRIPT_ONLY', 'SOURCE': 'Agricast — progetto INNOVA.DRUPE',
             'DOC': 'INNOVA.DRUPE – Difesa Innovativa per Drupacee e Noce',
             'DATE': '2026-04-27', 'TIMESTAMP_S': 315.0,
             'QUOTE_IT': ('La necrosi apicale bruna è una malattia fungina del noce molto complessa da '
                          'gestire. Quali strumenti vengono sperimentati per la difesa? Affrontiamo la '
                          'malattia tenendo conto che si tratta di un complesso di patogeni.'),
             'ONLY_IN_TRANSCRIPT': True,
             'WHY_ONLY_IN_TRANSCRIPT': ('a legenda cita "drupacee e noce" e "novos instrumentos de apoio a '
                                        'decisao". Nao nomeia a necrosi apicale bruna, nem que e um complexo '
                                        'de patogenos, nem a amostragem sazonal.'),
             'EVIDENCE_PATH': 'data/samples/IT-VOZ-AUDIO-V1/IT-VOZ-AUDIO-TRANSCRICOES-V1.json#70245821'},
        ],
        'ADAMA_RELATION': ('SUBSTANCIA_ATIVA apenas. Fluazinam esta no universo de substancias ativas da '
                           'ADAMA Italia. NENHUM par de rotulo NOCE x necrosi apicale bruna foi lido. '
                           'NOCE nao esta entre as 35 culturas de rotulo lidas.'),
        'OPPORTUNITY_LINK': [],
        'ACTION_MAP': ['REGULATION_PORTFOLIO', 'SCIENCE_TECHNICAL'],
        'PROVES': ('que a Emilia-Romagna abriu, em 2026-05-07, uma janela excepcional de no maximo duas '
                   'intervencoes com fluazinam contra a necrosi apicale bruna do noce; e que um projeto '
                   'de pesquisa publico trata a doenca como complexo de patogenos.'),
        'DOES_NOT_PROVE': ('NAO prova que a ADAMA tem produto autorizado para noce, nem para esta doenca. '
                           'A ligacao e de SUBSTANCIA, o degrau mais fraco da escada. Nao prova area, '
                           'nao prova incidencia, nao prova demanda.'),
        'PROVENANCE': 'REAL_SOURCE + SINTONIA_CROSSING',
        'CLIENT_SAFE': True,
    },

    {
        'ID': 'IT-X-2026-003',
        'TITLE': 'Patata x elateridi: a vacancia de modo de acao esta dita em voz alta, '
                 'com o ano da revogacao e o nome das tres especies',
        'CROP': 'PATATA',
        'TARGET': 'ELATERIDI (Agriotes litigiosus, A. sordidus, A. brevis)',
        'GEOGRAPHY': 'Emilia-Romagna',
        'GEOGRAPHY_STATE': 'DECLARED_BY_THE_SPEAKER',
        'WINDOW': 'episodio de 2026-03-23; a revogacao citada e de 2014 e continua valendo',
        'SOURCES_CROSSED': 2,
        'CROSSING_TYPE': 'PUBLIC_VOICE_TRANSCRIPT x ADAMA_LABEL_PAIR',
        'EVIDENCE': [
            {'LAYER': 'PUBLIC_VOICE_TRANSCRIPT_ONLY', 'SOURCE': 'Agricast — progetto elateridi su patata (OP settore patate, PO 2023/2027)',
             'DOC': 'Difesa della patata dagli elateridi, nuove strategie in campo',
             'DATE': '2026-03-23', 'TIMESTAMP_S': 61.5,
             'QUOTE_IT': ('Dall’altro, la revoca o l’inefficacia dei formulati di sintesi disponibili. '
                          'In Emilia-Romagna in particolare dobbiamo fare i conti con tre specie di elateridi '
                          'potenzialmente dannose che appartengono al genere Agriotes, che sono litigiosus, '
                          'sordidus e brevis. Queste specie, essendo polifaghe, arrecano danni oltre che alla '
                          'patata, anche a cereali, erba medica, ba[rbabietola]...'),
             'SECOND_QUOTE_IT': ('...nel 2014 quando è stato revocato un geoinsetticida a base di fipronil, '
                                 'a cui sono seguite altre revoche. Purtroppo anche gli insetticidi di sintesi '
                                 'disponibili a base di spinosad o piretrine sintetiche usati tutti come '
                                 'geodisinfestanti non garantiscono un controllo risolutivo.'),
             'SECOND_TIMESTAMP_S': 211.7,
             'ONLY_IN_TRANSCRIPT': True,
             'WHY_ONLY_IN_TRANSCRIPT': ('a legenda (681 caracteres) diz apenas que o projeto afinou a '
                                        'metodologia de monitoramento e estuda as especies. Nao nomeia '
                                        'Agriotes, nao nomeia especie nenhuma, nao cita revogacao, nao cita '
                                        'fipronil, nao cita spinosad, nao diz que o controle disponivel nao '
                                        'e resolutivo. Tudo isso esta so na fala.'),
             'EVIDENCE_PATH': 'data/samples/IT-VOZ-AUDIO-V1/IT-VOZ-AUDIO-TRANSCRICOES-V1.json#70245792'},
            {'LAYER': 'ADAMA_LABEL_PAIR', 'SOURCE': 'rotulo autorizado, Ministero della Salute',
             'DOC': 'LEBRON 0.5 G — ELATERIDI na linha da tabela',
             'PAIRS': ['IT-LBL-272 LEBRON 0.5 G | BARBABIETOLA | ELATERIDI',
                       'IT-LBL-276 LEBRON 0.5 G | FRUMENTO | ELATERIDI',
                       'IT-LBL-279 LEBRON 0.5 G | SORGO | ELATERIDI',
                       'IT-LBL-282 LEBRON 0.5 G | GIRASOLE | ELATERIDI',
                       'IT-LBL-291 LEBRON 0.5 G | LEGUMINOSE | ELATERIDI',
                       'IT-LBL-300 LEBRON 0.5 G | BRASSICACEE | ELATERIDI'],
             'LINK_STRENGTH': 'LINHA_DA_TABELA',
             'EVIDENCE_PATH': 'v21/productRelationships.json'},
        ],
        'ADAMA_RELATION': ('a ponte e a POLIFAGIA dita pelo proprio pesquisador. As mesmas tres especies de '
                           'Agriotes danificam cereali, erba medica e barbabietola — e a ADAMA tem LEBRON 0.5 G '
                           'com ELATERIDI na LINHA DA TABELA para FRUMENTO, BARBABIETOLA, SORGO, GIRASOLE, '
                           'LEGUMINOSE e BRASSICACEE. Em PATATA o corpus so tem 2 pares ELATERIDI lidos.'),
        'OPPORTUNITY_LINK': ['nenhuma das 37 cobre PATATA x ELATERIDI — e candidato a NEW TO_VALIDATE'],
        'ACTION_MAP': ['SCIENCE_TECHNICAL', 'MARKET_DEVELOPMENT'],
        'PROVES': ('que um projeto publico da OP do setor da batata declara, em 2026-03-23, que tres especies '
                   'de Agriotes pesam na Emilia-Romagna, que o dano se agravou, que a causa inclui revogacao '
                   'de formulados de sintese desde 2014, e que os geodisinfestantes disponiveis nao dao '
                   'controle resolutivo; e que a ADAMA tem par de rotulo lido para ELATERIDI em seis das '
                   'culturas hospedeiras que o mesmo pesquisador nomeia.'),
        'DOES_NOT_PROVE': ('nao prova incidencia medida, nao prova area afetada, nao prova que a ADAMA pode '
                           'usar LEBRON em patata — os 2 pares de PATATA x ELATERIDI nao foram verificados '
                           'produto a produto nesta missao; nao prova demanda; e uma voz nao e uma tendencia.'),
        'PROVENANCE': 'REAL_SOURCE + SINTONIA_CROSSING',
        'CLIENT_SAFE': True,
    },

    {
        'ID': 'IT-X-2026-004',
        'TITLE': 'Melo x cimice asiatica: a serie de capturas sobe, o boletim nomeia a substancia '
                 'ADAMA com teto de intervencoes, e a economia disso aparece na fala',
        'CROP': 'MELO (e pero, pesco, actinidia)',
        'TARGET': 'CIMICE ASIATICA (Halyomorpha halys) — 2a geracao',
        'GEOGRAPHY': 'Emilia-Romagna — provincias MO, RA, PC, PR, RE',
        'GEOGRAPHY_STATE': 'DECLARED_BY_THE_DOCUMENTS',
        'WINDOW': 'capturas ate 2026-08-31; recomendacao de 2026-09-02 — janela aberta',
        'SOURCES_CROSSED': 3,
        'CROSSING_TYPE': 'TRAP_NETWORK_SERIES x FIELD_BULLETIN x PUBLIC_VOICE_TRANSCRIPT',
        'EVIDENCE': [
            {'LAYER': 'TRAP_NETWORK_SERIES', 'SOURCE': 'UNIBO BIG — rete di monitoraggio Halyomorpha halys',
             'DOC': 'serie por provincia e estadio, 2021-03-08 a 2026-08-31',
             'DATE': '2026-08-31',
             'OBSERVATION': ('semana de 2026-08-31: giovani II-III em PC 108 (n=3 trappole), RA 107 (n=6), '
                             'MO 175 (n=15); giovani IV-V RA 52 (n=6) contra 22 na semana anterior; '
                             'adulti MO 92 (n=15).'),
             'EVIDENCE_PATH': 'data/samples/IT-CAMPO-V1/IT-CIMICE-TRAPPOLE-UNIBO-SERIE.json'},
            {'LAYER': 'FIELD_BULLETIN', 'SOURCE': 'Servizio Fitosanitario Emilia-Romagna',
             'DOC': 'Bollettino Forli-Cesena, Ravenna e Rimini N. 28 del 02/09/2026',
             'DATE': '2026-09-02',
             'QUOTE_IT': ('Cimice asiatica: i monitoraggi evidenziano un incremento della presenza di ninfe '
                          'e di adulti di seconda generazione, e il progressivo esaurimento delle '
                          'ovideposizioni. Qualora si riscontrasse un’importante presenza del fitofago '
                          'intervenire con Tau-fluvalinate (Max 2, attenzione ai tempi di carenza) o '
                          'Lambdacialot[rina]...'),
             'EVIDENCE_PATH': 'data/samples/IT-CAMPO-V1/IT-BOLLETTINI-ER-SOSTANZE-ATTIVE-V1.json'},
            {'LAYER': 'PUBLIC_VOICE_TRANSCRIPT_ONLY', 'SOURCE': 'Agricast — progetto REMUNERA',
             'DOC': 'REMUNERA - Il prezzo delle scelte in frutticoltura',
             'DATE': '2026-08-31', 'TIMESTAMP_S': 125.1,
             'QUOTE_IT': ('restando nel tema delle reti, crescente è l’interesse verso quelle anti-insetto, '
                          'soprattutto dopo la diffusione della cimice asiatica ed altri parassiti alieni. '
                          '[...] Scegliendo una copertura di tipo multitasking, come ad esempio una rete '
                          'anti-insetto monoblocco che offre una migliore protezione da insetti parassiti e '
                          'permette di ridurre l’apporto di agrofarmaci, l’investimento iniziale sale '
                          'intorno a 55.000 euro ettaro.'),
             'ONLY_IN_TRANSCRIPT': True,
             'WHY_ONLY_IN_TRANSCRIPT': ('a legenda fala de benchmarking de custos de producao. Nao cita cimice '
                                        'asiatica, nao cita rede anti-insecto, nao da o numero de 55.000 '
                                        'euro/ha, e nao diz que a rede REDUZ o aporte de agrofarmacos.'),
             'EVIDENCE_PATH': 'data/samples/IT-VOZ-AUDIO-V1/IT-VOZ-AUDIO-TRANSCRICOES-V1.json#73838361'},
        ],
        'ADAMA_RELATION': ('BLOCO_DA_CULTURA. Tau-fluvalinate esta no universo de substancias ativas da ADAMA '
                           'Italia e quatro produtos trazem MELO x CIMICE no bloco da cultura: KLARTAN 20 EW, '
                           'TAU AL 240 EW, MAVRIK SMART, KLARTAN SMART. LAMDEX EXTRA traz AGRUMI x CIMICE '
                           'na linha da tabela. Lambda-cialotrina tambem e substancia ADAMA.'),
        'THE_UNCOMFORTABLE_HALF': ('a mesma fala mede o SUBSTITUTO: uma rede anti-insecto monobloco a 55.000 '
                                   'euro/ha que "permite reduzir o aporte de agrofarmacos". O sinal de campo '
                                   'e o sinal de substituicao estao no mesmo episodio.'),
        'OPPORTUNITY_LINK': ['OPP_56F19FD9F62B (MELO x ISSUE_STINK_BUG, GEO_ITALY)'],
        'ACTION_MAP': ['MARKET_DEVELOPMENT', 'SCIENCE_TECHNICAL', 'COMPETITOR_WATCH'],
        'PROVES': ('que a rede de trappole registrou aumento de ninfas e adultos de 2a geracao ate 2026-08-31 '
                   'em provincias da Emilia-Romagna; que em 2026-09-02 o boletim regional recomendou '
                   'tau-fluvalinate com teto de 2 intervencoes; e que um projeto publico discute rede '
                   'anti-insecto como alternativa com custo declarado.'),
        'DOES_NOT_PROVE': ('n = trappole ispezionate MEXE semana a semana (RA passou de 13 para 6) e provincia '
                           'com n=0 e observacao ausente, nunca pressao zero. As parcelas nao sao amostra '
                           'aleatoria. Nao prova incidencia regional, nao prova dano, nao prova demanda, e o '
                           'custo de 55.000 euro/ha e uma cifra citada num podcast, nao um preco de mercado medido.'),
        'PROVENANCE': 'REAL_SOURCE + SINTONIA_CROSSING',
        'CLIENT_SAFE': True,
    },

    {
        'ID': 'IT-X-2026-005',
        'TITLE': 'Pero x maculatura bruna: uma janela excepcional com folpet, com data de '
                 'abertura e de fechamento — e ela ja fechou',
        'CROP': 'PERO',
        'TARGET': 'MACULATURA BRUNA (Stemphylium vesicarium)',
        'GEOGRAPHY': 'Emilia-Romagna',
        'GEOGRAPHY_STATE': 'DECLARED_BY_THE_DOCUMENT',
        'WINDOW': 'impiego consentito dal 28/04/2026 al 25/08/2026 — FECHADA na data de referencia',
        'SOURCES_CROSSED': 2,
        'CROSSING_TYPE': 'REGULATORY_EVENT x ADAMA_PORTFOLIO_RELATION',
        'EVIDENCE': [
            {'LAYER': 'REGULATORY_EVENT', 'SOURCE': 'Regione Emilia-Romagna, via bollettino fitosanitario de Parma',
             'DOC': 'Bollettino n. 27 del 21 agosto 2026 di Parma',
             'DATE': '2026-08-21',
             'QUOTE_IT': ('In data 13 maggio 2026 è stata concessa la deroga valida per il territorio della '
                          'Regione Emilia-Romagna per l’uso eccezionale del prodotto fitosanitario FOLPEC 50 SC, '
                          'contenente la sostanza attiva folpet, per il contenimento della maculatura bruna '
                          '(Stemphylium vesicarium) sulla coltura del pero - impiego consentito dal 28/04/2026 '
                          'al 25/08/2026.'),
             'EVIDENCE_PATH': 'data/samples/IT-CAMPO-V1/IT-BOLLETTINI-ER-SOSTANZE-ATTIVE-V1.json'},
            {'LAYER': 'ADAMA_PORTFOLIO_RELATION', 'SOURCE': 'catalogo e registro ADAMA Italia',
             'DOC': 'folpet no universo ADAMA',
             'OBSERVATION': ('folpet e substancia ativa ADAMA; FOLPAN 80 WDG e FOLPAN ENERGY estao no '
                             'catalogo comercial e entre os PRODUCT_RELATIONSHIPS de OPP_3965565ACFCC. '
                             'FOLPEC 50 SC NAO e produto ADAMA.'),
             'EVIDENCE_PATH': 'v21/activeIngredients.json · v21/productsCommercial.json'},
        ],
        'ADAMA_RELATION': ('SUBSTANCIA_ATIVA. Nenhum par de rotulo PERO x Stemphylium foi lido para a ADAMA: '
                           'os tres pares de PERO no corpus (BANJO, EMBRACE, AGHARTA) estao em BLOCO_DA_CULTURA '
                           'com TARGET NAO_MAPEADO, e os alvos lidos para pero sao TICCHIOLATURA e ALTERNARIA.'),
        'TIMING': ('a janela FECHOU em 2026-08-25, nove dias antes da data de referencia. O valor deste '
                   'cruzamento nao e agir agora: e que a deroga recorre por campanha, e a preparacao da '
                   'campanha 2027 comeca antes de abril.'),
        'OPPORTUNITY_LINK': ['OPP_20D89B04F64D (PERO, Emilia-Romagna) — mesma cultura e mesma regiao, alvo diferente'],
        'ACTION_MAP': ['REGULATION_PORTFOLIO'],
        'PROVES': ('que a Emilia-Romagna autorizou uso excepcional de folpet em pero contra Stemphylium '
                   'vesicarium numa janela declarada de 28/04/2026 a 25/08/2026, atraves de um produto que '
                   'nao e da ADAMA.'),
        'DOES_NOT_PROVE': ('nao prova que a ADAMA pode registrar, vender ou pedir a mesma deroga; nao prova '
                           'que a deroga se repetira em 2027; nao prova incidencia; e produto de concorrente '
                           'nao e produto ADAMA.'),
        'PROVENANCE': 'REAL_SOURCE + SINTONIA_CROSSING',
        'CLIENT_SAFE': True,
    },
]

CRUZAMENTOS += [

    {
        'ID': 'IT-X-2026-006',
        'TITLE': 'Um agronomo independente diz, em video datado, para NAO tratar — e diz que '
                 'a terceira geracao de tignoletta comecou',
        'CROP': 'VITE',
        'TARGET': 'PERONOSPORA e OIDIO (ausentes) · TIGNOLETTA (terceiro voo, comecando)',
        'GEOGRAPHY': 'Lombardia — Brescia, Bergamo, Mantova',
        'GEOGRAPHY_STATE': 'DECLARED_BY_THE_SPEAKER',
        'WINDOW': '2026-07-23, fase de invaiatura avancada declarada na fala',
        'SOURCES_CROSSED': 2,
        'CROSSING_TYPE': 'TECHNICAL_ADVISER_VIDEO x ADAMA_LABEL_PAIR',
        'EVIDENCE': [
            {'LAYER': 'TECHNICAL_ADVISER_VIDEO',
             'SOURCE': 'Agralia Studio Agronomico (Brescia) — canal YouTube proprio',
             'DOC': 'Aggiornamento Agrometeo Vite – Fine luglio 2026',
             'URL': 'https://www.youtube.com/watch?v=EmDDkVgfzEM',
             'DATE': '2026-07-23',
             'CAPTION_SOURCE': 'YOUTUBE_ASR_AUTO',
             'QUOTE_IT': ('aggiornamento Agrometeo Lombardia e dintorni settore vite, ehm Brescia, '
                          'Bergamo, Mantova e via dicendo. [...] 23 luglio 2026 [...] siamo ormai '
                          'in fase di invaiatura avanzata. [...] Di fatto non abbiamo peronospora, '
                          'non abbiamo oidio, quindi vi consiglio di non trattare se non prima '
                          'delle possibili piogge. Pare che stia cominciando il volo di terza '
                          'generazione di tignoletta.'),
             'ONLY_IN_TRANSCRIPT': True,
             'WHY_ONLY_IN_TRANSCRIPT': ('o titulo do video e "Aggiornamento Agrometeo Vite – Fine '
                                        'luglio 2026" e nao diz avversita nenhuma. Peronospora, '
                                        'oidio, tignoletta, a fase fenologica e as tres provincias '
                                        'estao SO NA FALA.'),
             'EVIDENCE_PATH': 'data/samples/IT-VIDEO-V1/falas/EmDDkVgfzEM.json'},
            {'LAYER': 'ADAMA_LABEL_PAIR', 'SOURCE': 'rotulo autorizado, Ministero della Salute',
             'PAIRS': ['IT-LBL-326 LAMDEX EXTRA | VITE | TIGNOLE | "Tignola e[uropea]"',
                       'IT-LBL-823 FORZA | VITE | TIGNOLE', 'IT-LBL-903 NINJA | VITE | TIGNOLE',
                       'IT-LBL-1371 DURAVIS | VITE | TIGNOLE', 'IT-LBL-1675 ELTIRA | VITE | TIGNOLE',
                       'IT-LBL-796 FOLPAN GOLD | VITE | PERONOSPORA',
                       'IT-LBL-1442 SESTO GOLD | VITE | PERONOSPORA',
                       'IT-LBL-1958 MOMENTUM PFNPE | VITE | PERONOSPORA'],
             'LINK_STRENGTH': 'LINHA_DA_TABELA',
             'EVIDENCE_PATH': 'v21/productRelationships.json'},
        ],
        'VOCABULARY_RECONCILIATION': ('o agronomo diz TIGNOLETTA; o rotulo escreve TIGNOLE e '
                                      '"Tignola e[uropea]". Ligar os dois e INFERENCIA NOSSA, '
                                      'nao observacao — e as duas reguas batizaram a mesma coisa '
                                      'de jeitos diferentes.'),
        'ADAMA_RELATION': ('LINHA_DA_TABELA nos dois lados: cinco registros ADAMA trazem '
                           'VITE x TIGNOLE na linha da tabela, e tres trazem VITE x PERONOSPORA. '
                           'VITE tem 96 pares de rotulo ADAMA.'),
        'WHY_THIS_ONE_IS_DIFFERENT': ('e o unico sinal desta rodada em que a fonte tecnica '
                                      'recomenda NAO TRATAR. Para uma empresa de protecao de '
                                      'cultivos isso e mais dificil e mais util que um alerta de '
                                      'pressao: e exatamente a FALSE-SIGNAL AVOIDANCE que este '
                                      'sistema ja provou ser o que faz de melhor.'),
        'OPPORTUNITY_LINK': ['OPP_C37A1FD2742E (VITE x ISSUE_GRAPE_MOTH, GEO_ITALY)',
                             'OPP_3F736F0A9467 (VITE x ISSUE_DOWNY_MILDEW, GEO_ITALY)',
                             'OPP_AF16E6A6B8B3 (VITE, confirmada, GEO_ITALY)'],
        'ACTION_MAP': ['SCIENCE_TECHNICAL', 'MARKET_DEVELOPMENT'],
        'PROVES': ('que em 2026-07-23 um estudio agronomico privado da Lombardia declarou '
                   'publicamente, em video, ausencia de peronospora e oidio nas suas vinhas de '
                   'Brescia, Bergamo e Mantova, recomendou nao tratar, e afirmou que o terceiro '
                   'voo de tignoletta estava comecando.'),
        'DOES_NOT_PROVE': ('nao prova ausencia de peronospora na Lombardia nem na Italia — prova '
                           'o que ESTE tecnico observou nas parcelas que ele acompanha; nao prova '
                           'incidencia de tignoletta, so o inicio do voo declarado por ele; nao '
                           'prova demanda nem queda de demanda. UMA VOZ NAO E UMA TENDENCIA.'),
        'PROVENANCE': 'REAL_SOURCE + SINTONIA_CROSSING',
        'CLIENT_SAFE': True,
    },

    {
        'ID': 'IT-X-2026-007',
        'TITLE': 'Vite x quatro avversita nomeadas so na fala — e a mesma fala fecha a porta: '
                 'a vinha e biologica desde 2024 e a tignoletta ja e "um recordo"',
        'CROP': 'VITE',
        'TARGET': 'PERONOSPORA · FLAVESCENZA DORATA (via SCAFOIDEO) · OIDIO · TIGNOLETTA (Lobesia botrana)',
        'GEOGRAPHY': 'Emilia-Romagna — Rio Saliceto, provincia de Reggio Emilia',
        'GEOGRAPHY_STATE': 'DECLARED_BY_THE_SPEAKER',
        'WINDOW': '2026-06-09 (episodio publicado) — janela de 90 dias',
        'SOURCES_CROSSED': 3,
        'CROSSING_TYPE': 'PUBLIC_VOICE_TRANSCRIPT x ADAMA_LABEL_PAIR x SCIENTIFIC_VOICE',
        'EVIDENCE': [
            {'LAYER': 'PUBLIC_VOICE_TRANSCRIPT_ONLY',
             'SOURCE': 'Terra di Denari (podcast, Spreaker show 6623075) — IT-SRCX-088',
             'DOC': 'Episodio "Sotto controllo", 1.811 s, azienda das irmas Acerbi',
             'DATE': '2026-06-09',
             'QUOTE_IT': ('Si trovano a Rio Saliceto in provincia di Reggio Emilia. Il pilastro '
                          'economico aziendale e la vigna, 39 ettari sparsi in diversi comuni. '
                          '[...] Tutta l azienda e in biologico, compresa la vigna che e '
                          'certificata dal 2024. [...] Il nemico numero uno si chiama Peronospora. '
                          'Il vigneto poi si trova sfortunatamente nella zona colpita di recente '
                          'dalla Flavescenza dorata e raramente devono anche combattere contro '
                          'l oidio. Potendo utilizzare solo trattamenti specificamente ammessi nel '
                          'biologico, si sono dovute organizzare. [...] la tignoletta per le '
                          'sorelle Acerbi e ormai un ricordo. [...] La tecnica della confusione '
                          'sessuale con la distribuzione di diffusori in vigna ha aiutato.'),
             'ONLY_IN_TRANSCRIPT': True,
             'WHY_ONLY_IN_TRANSCRIPT': ('a descricao do episodio na API do Spreaker tem ZERO '
                                        'caracteres. A fala tem 26.200. Razao legenda:fala = 0:26.200. '
                                        'Este e o caso limite do medidor: sem transcricao, este '
                                        'episodio e invisivel.'),
             'EVIDENCE_PATH': 'data/samples/IT-VOZ-AUDIO-V2/IT-VOZ-AUDIO-TRANSCRICOES-V2.json#72418542'},
            {'LAYER': 'SCIENTIFIC_VOICE_IN_THE_SAME_AUDIO',
             'SOURCE': 'Andrea Lucchi, professor de entomologia geral e aplicada (entrevistado no episodio)',
             'DOC': 'mesmo episodio, bloco sobre semioquimicos e confusao sexual',
             'DATE': '2026-06-09',
             'QUOTE_IT': ('le tignole grappolo... sono presenti in tutte le principali regioni '
                          'vitivinicole del Nord e anche al Sud, in particolare in Puglia'),
             'ONLY_IN_TRANSCRIPT': True,
             'EVIDENCE_PATH': 'data/samples/IT-VOZ-AUDIO-V2/IT-VOZ-AUDIO-TRANSCRICOES-V2.json#72418542'},
            {'LAYER': 'ADAMA_LABEL_PAIR', 'SOURCE': 'rotulo autorizado, Ministero della Salute',
             'DOC': '13 pares lidos, em dois niveis diferentes da escada',
             'PAIRS': ['IT-LBL-326 LAMDEX EXTRA reg 008259 | VITE | TIGNOLE | LINHA_DA_TABELA',
                       'IT-LBL-823 FORZA reg 013560 | VITE | TIGNOLE | LINHA_DA_TABELA',
                       'IT-LBL-903 NINJA reg 013590 | VITE | TIGNOLE | LINHA_DA_TABELA',
                       'IT-LBL-1371 DURAVIS reg 015275 | VITE | TIGNOLE | LINHA_DA_TABELA',
                       'IT-LBL-1675 ELTIRA reg 017687 | VITE | TIGNOLE | LINHA_DA_TABELA',
                       'IT-LBL-1343 CUSTODIA ULTRA reg 015232 | VITE | OIDIO (Uncinula necator) | LINHA_DA_TABELA',
                       'IT-LBL-1852 MIRADOR TURBO reg 017824 | VITE | OIDIO (Uncinula necator) | LINHA_DA_TABELA',
                       'IT-LBL-065 KLARTAN 20 EW reg 007555 | VITE | cicaline (Scaphoideus titanus) | BLOCO_DA_CULTURA',
                       'IT-LBL-159 TAU AL 240 EW reg 007864 | VITE | cicaline (Scaphoideus titanus) | BLOCO_DA_CULTURA',
                       'IT-LBL-466 MAVRIK SMART reg 009800 | VITE | cicaline (Scaphoideus titanus) | BLOCO_DA_CULTURA',
                       'IT-LBL-658 KLARTAN SMART reg 012023 | VITE | cicaline (Scaphoideus titanus) | BLOCO_DA_CULTURA',
                       'IT-LBL-1035 MAVRIK EW reg 014190 | VITE | cicaline (Scaphoideus titanus) | BLOCO_DA_CULTURA',
                       'IT-LBL-1115 EVURE PRO reg 014210 | VITE | cicaline (Scaphoideus titanus) | BLOCO_DA_CULTURA'],
             'LINK_STRENGTH': 'LINHA_DA_TABELA',
             'QUOTE_FROM_LABEL': ('Vite (da vino e da tavola) Contro cicaline (Empoasca vitis, '
                                  'Scaphoideus titanus) e tripidi — a citacao NOMEIA o vetor da '
                                  'flavescenza dorada dentro do bloco da cultura.'),
             'EVIDENCE_PATH': 'v21/productRelationships.json (pacote canonico V2.1), lido em 2026-09-03'},
        ],
        'ADAMA_RELATION': ('das quatro avversita que a produtora nomeia, TRES tem par de rotulo ADAMA em '
                           'VITE: TIGNOLE em LINHA_DA_TABELA (5 registros), OIDIO em LINHA_DA_TABELA '
                           '(2 registros) e o VETOR da flavescenza — Scaphoideus titanus — nomeado '
                           'dentro do BLOCO_DA_CULTURA de 6 registros de tau-fluvalinate. '
                           'FLAVESCENZA DORATA em si tem ZERO pares: nao se trata a doenca, trata-se '
                           'o vetor, e e o vetor que esta no rotulo.'),
        'WHY_THIS_CROSSING_COOLS_INSTEAD_OF_WARMING': (
            'a mesma fala que nomeia as quatro avversita fecha a porta para as tres quimicas: '
            '"Tutta l azienda e in biologico, compresa la vigna che e certificata dal 2024" e '
            '"potendo utilizzare solo trattamenti specificamente ammessi nel biologico". Nenhum dos '
            '13 registros ADAMA citados e admitido em regime biologico. E a tignoletta, o unico alvo '
            'com cinco produtos em LINHA_DA_TABELA, e descrita como "ormai un ricordo" porque a '
            'CONFUSAO SEXUAL resolveu — isto e, um metodo NAO QUIMICO ja ocupou o espaco. '
            'ACHAR O ELO E AINDA ASSIM ESFRIAR O CASO E O COMPORTAMENTO CORRETO.'),
        'OPPORTUNITY_LINK': ['nenhuma. Este cruzamento NAO e proposto como oportunidade.'],
        'ACTION_MAP': ['SCIENCE_TECHNICAL'],
        'PROVES': ('que em 2026-06-09 uma produtora de 39 ha de vinha em Rio Saliceto (Reggio Emilia) '
                   'declarou publicamente, em audio, quatro avversita da vinha — peronospora como '
                   '"nemico numero uno", zona atingida por flavescenza dorada, oidio ocasional e '
                   'tignoletta —, e que a ADAMA tem 13 pares de rotulo em VITE para tres delas, '
                   'incluindo a citacao que nomeia Scaphoideus titanus. E prova que a descricao '
                   'publicada do episodio tem ZERO caracteres: sem transcricao, nada disso existe.'),
        'DOES_NOT_PROVE': ('nao prova incidencia em Reggio Emilia nem na Emilia-Romagna: e UMA azienda, '
                           'e uma voz. Nao prova demanda — prova o contrario, porque a azienda e '
                           'biologica certificada e os 13 produtos citados nao sao admitidos ali. Nao '
                           'prova que a flavescenza avanca: prova que a produtora diz estar "na zona '
                           'atingida". E nao prova nada sobre a tignoletta em outras vinhas — a fala '
                           'do professor Lucchi diz que ela esta em todas as regioes vitivinicolas do '
                           'Norte e na Puglia, o que e uma afirmacao dele, e nao uma medicao desta casa. '
                           'UMA VOZ NAO E UMA TENDENCIA.'),
        'PROVENANCE': 'REAL_SOURCE + SINTONIA_CROSSING',
        'CLIENT_SAFE': True,
    },
]

NAO_CRUZADOS = [
    {'PAIR': 'Popillia japonica (AIPP, webinar de 2026-07-09) x portfolio ADAMA',
     'WHY': ('a fala e forte e datada: descreve a OBRIGACAO de tratar a superficie na area '
             'delimitada com "adulticidi abbattenti come la deltametrina e l acetamiprid", e pede '
             '"molecole efficaci in autorizzazione eccezionale nelle aree ad eradicazione, come fu '
             'per la cimice asiatica". Mas nem deltametrina nem acetamiprid estao entre as 53 '
             'substancias ativas da ADAMA Italia, e o corpus tem ZERO pares de rotulo para '
             'Popillia. NAO HA CHAVE. Forcar aqui seria inventar relevancia ADAMA — e a missao '
             'proibe exatamente isso.'),
     'WHAT_IT_IS_INSTEAD': ('e um sinal de ABERTURA REGULATORIA que o portfolio atual nao responde: '
                            'uma sociedade cientifica italiana pedindo autorizacao excepcional '
                            'para uma quarentena em expansao em Lombardia e Piemonte. Vale como '
                            'FUTURE, e nao como oportunidade.'),
     'EVIDENCE': 'data/samples/IT-VIDEO-V1/falas/ep1KX19XxS8.json'},
    {'PAIR': 'voz publica x incidencia regional medida',
     'WHY': ('nenhuma fonte italiana desta rodada entrega serie de INCIDENCIA por parcela comparavel ao '
             'RAIF espanhol. A rede de trappole da cimice entrega CAPTURA, que nao e incidencia. Sem essa '
             'chave, o cruzamento voz x campo que a Espanha reprovou nem sequer pode ser tentado aqui.')},
    {'PAIR': 'sinal de campo x area de cultura por provincia',
     'WHY': ('as capturas da cimice sao por provincia; a area de melo por provincia nao foi lida nesta '
             'missao. Sem denominador, ordenar provincias repetiria o erro que o indice de exposicao '
             'espanhol corrigiu — e o indice de exposicao ORDENA, nunca dimensiona.')},
    {'PAIR': 'os outros 10 episodios de audio x portfolio ADAMA',
     'WHY': ('a rota de audio marcou "sinal so na fala" em 11 dos 13 episodios, e a auditoria que fiz '
             'em cima dessa marca derruba a maior parte dela: em 8 dos 11 o que a fala acrescenta e '
             'INVENTARIO DE CULTURA ("coltiviamo mais, frumento, erba medica"), e nao observacao de '
             'alvo, janela ou molecula. CULTURA CITADA != SINAL DE CAMPO. So 3 episodios nomeiam '
             'avversita, e apenas um deles (IT-X-2026-007) tem geografia, data e par de rotulo.'),
     'WHAT_IT_IS_INSTEAD': ('e a medida honesta do rendimento da rota: 13 episodios, 5,3 horas de audio, '
                            '286.395 caracteres, 1 cruzamento. Caro por cruzamento, e ainda assim '
                            'INFINITAMENTE melhor que os 3 lotes de Instagram, que deram ZERO.'),
     'EVIDENCE': 'data/samples/IT-VOZ-AUDIO-V2/IT-VOZ-AUDIO-TRANSCRICOES-V2.json'},
    {'PAIR': 'FRUMENTO no episodio "Sotto controllo" x qualquer coisa',
     'WHY': ('FALSO POSITIVO DO MEU PROPRIO VOCABULARIO, encontrado na auditoria e registrado aqui em '
             'vez de apagado: o regex de FRUMENTO e `\\bgrano\\b`, e a fala diz "farro, sorgo, miglio '
             'e GRANO SARACENO" — trigo sarraceno, que e Fagopyrum esculentum e nao e trigo. Mesma '
             'familia de "sentiamo un bel pomodoro forte" (nota de degustacao de azeite lida como '
             'POMODORO) e de LIGA vindo de "obbligatorio". '
             'A PALAVRA EXISTE, O SIGNIFICADO NAO.'),
     'EVIDENCE': 'data/samples/IT-VOZ-AUDIO-V2/IT-VOZ-AUDIO-TRANSCRICOES-V2.json#72418542'},
    {'PAIR': 'OLIVO x MOSCA DELL OLIVO (bollettini semanais da OlivoNews) x portfolio ADAMA',
     'ID': 'IT-NX-2026-005',
     'WHY': ('E O MELHOR NAO-CRUZAMENTO DESTA MISSAO, e ele custou tres transcricoes para '
             'aparecer. Os tres bollettini olivicoli semanais (2026-08-16, 08-23 e 08-30, '
             '11.427 caracteres transcritos localmente) sao exatamente o que um sinal de campo '
             'deveria ser: cultura nomeada, alvo nomeado (mosca dell olivo), NIVEL DE RISCO '
             'declarado por macro-regiao ("Nord Italia, stato di allerta, rischio elevato"), '
             'data semanal, e ate o teto de intervencoes ("massimo 8 interventi all anno"). '
             'E NAO HA CHAVE. As moleculas que os boletins nomeiam para intervir sao '
             'acetamiprid, flupyradifurone, spinosad, caolino calcinato e azadiractina — e '
             'NENHUMA das cinco esta entre as 53 substancias ativas do corpus ADAMA Italia. '
             'Conferido uma a uma contra activeIngredients.json.'),
     'WHAT_IT_IS_INSTEAD': ('e uma POSICAO DE PORTFOLIO medida, e ela e mais util que um '
                            'cruzamento forcado: a ADAMA tem UM unico par de rotulo em OLIVO em '
                            'todo o radar — IT-LBL-018101, MORAINE, contra INFESTANTI, em '
                            'LINHA_DA_TABELA. Um HERBICIDA. A conversa italiana da oliveira, '
                            'semana a semana, e sobre a MOSCA; o portfolio lido responde por '
                            'ERVA DANINHA. A assimetria que o relatorio ja tinha notado (OLIVO: '
                            '1 par lido, 3 oportunidades, 5 crop windows) ganha aqui metade da '
                            'explicacao — e a outra metade continua sendo que a leitura de '
                            'rotulo cobre 102 dos 163 registros.'),
     'WHAT_WOULD_CHANGE_IT': ('ler os 61 registros do Ministero que ainda nao tiveram o rotulo '
                              'lido. Se algum deles trouxer OLIVO com um alvo entomologico, este '
                              'nao-cruzamento vira cruzamento no mesmo dia. Enquanto isso, '
                              'AUSENCIA NA NOSSA LEITURA != AUSENCIA NO MUNDO.'),
     'EVIDENCE': 'data/samples/IT-VOZ-AUDIO-V2/IT-VOZ-AUDIO-LOCAIS-V2.json (olivonews-2026-08-16|23|30)'},
    {'PAIR': 'comunicacao de concorrente x sinal de campo',
     'WHY': ('adama.com, syngenta.it/news e cropscience.bayer.it recusaram esta sessao com HTTP 403. '
             'ROUTE_BLOCKED_FOR_AUTOMATION != CATALOG_EMPTY: nao ha o que cruzar porque nao houve leitura.')},
]


def escrever():
    os.makedirs(SAIDA, exist_ok=True)
    from collections import Counter
    corpo = {
        'DATASET': 'IT-CRUZAMENTO-V1',
        'LAYER': 'SINTONIA_CROSSING_ITALY',
        'COUNTRY': 'IT',
        'SOURCE': ('derivado: cada cruzamento cita, registro a registro, as fontes primarias que o '
                   'sustentam — bollettino do Servizio Fitosanitario Emilia-Romagna, serie de '
                   'trappole UNIBO BIG, transcricao local de audio publico, e pares de rotulo do '
                   'pacote canonico V2.1.'),
        'SOURCE_ID': 'IT-CRUZAMENTO-V1',
        'CAPTURED_AT': CAPTURA,
        'BUILT_AT': CAPTURA,
        'REFERENCE_DATE': CAPTURA,
        'LAW_1': 'SEM CHAVE REAL, NAO CRUZA',
        'LAW_2': 'PORTFOLIO RELATION != LABEL AUTHORIZATION',
        'LAW_3': 'UMA VOZ NAO E UMA TENDENCIA — quando varias fontes convergem, o nome e CLUSTER NELLE FONTI MONITORATE, nunca TREND IN ITALY',
        'LAW_4': 'AUSENCIA NA NOSSA LEITURA != AUSENCIA NO MUNDO',
        'COUNT': len(CRUZAMENTOS),
        'BY_LINK_STRENGTH': dict(Counter(
            next((e.get('LINK_STRENGTH') for e in x['EVIDENCE'] if e.get('LINK_STRENGTH')), 'SUBSTANCIA_ATIVA')
            for x in CRUZAMENTOS)),
        'WITH_TRANSCRIPT_ONLY_EVIDENCE': sum(
            1 for x in CRUZAMENTOS if any(e.get('ONLY_IN_TRANSCRIPT') for e in x['EVIDENCE'])),
        'CROSSINGS': CRUZAMENTOS,
        'NOT_CROSSED_AND_WHY': NAO_CRUZADOS,
    }
    caminho = os.path.join(SAIDA, 'IT-CRUZAMENTOS-V1.json')
    with open(caminho, 'w', encoding='utf-8') as fh:
        json.dump(corpo, fh, ensure_ascii=False, indent=1)
    return caminho, corpo


if __name__ == '__main__':
    caminho, corpo = escrever()
    print('escrito: %s' % os.path.relpath(caminho, ROOT))
    print()
    print('%-38s %s' % ('CROSSINGS', corpo['COUNT']))
    print('%-38s %s' % ('BY_LINK_STRENGTH', corpo['BY_LINK_STRENGTH']))
    print('%-38s %s' % ('WITH_TRANSCRIPT_ONLY_EVIDENCE', corpo['WITH_TRANSCRIPT_ONLY_EVIDENCE']))
    print('%-38s %s' % ('NOT_CROSSED_AND_WHY', len(corpo['NOT_CROSSED_AND_WHY'])))
    print()
    for x in CRUZAMENTOS:
        print('  %-16s %-8s %-34s %s fontes' % (x['ID'], x['CROP'][:8], x['TARGET'][:34], x['SOURCES_CROSSED']))
