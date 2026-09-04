#!/usr/bin/env python3
"""RADAR FUTURO — os sinais antecipatorios que o acervo sustenta, escritos a mao.

Como cada registro nasceu
--------------------------
1. o varredor (it_futuro_corpus.py) devolveu 3.035 CANDIDATOS em 131 documentos;
2. eu li o PARAGRAFO em volta de cada candidato promissor, e nao a frase;
3. so entrou aqui o que o contexto sustenta. A expressao de futuro sozinha nunca
   bastou: 'previsione' tanto abre uma previsao quanto fecha
   'contrariamente alla previsione, non e successo'.

A lei do tempo, que nao se afrouxa
-----------------------------------
    TENDENCIA nao vira PREVISAO.
    PREVISAO nao vira OCORRENCIA.
    EVENTO MARCADO nao significa RESULTADO CONHECIDO.
    PORTFOLIO RELATION nao vira LABEL AUTHORIZATION.

Campo que a fonte nao sustenta fica UNKNOWN com a CAUSA declarada. Um UNKNOWN
verdadeiro vale mais do que uma oportunidade inventada — e este arquivo prefere
ficar pequeno a ficar cheio.
"""

# ── causas de campo vazio (FASE 6) ──────────────────────────────────────────
# NOT_COLLECTED         a coleta nunca foi ate essa fonte
# NOT_EXTRACTED         esta no documento coletado, o pipeline nao tirou
# NOT_IN_SOURCE         o documento nao diz, e nenhum pipeline resolveria
# NEEDS_CROSSING        existe em duas fontes separadas; falta o cruzamento
# NEEDS_EXTERNAL_SOURCE so uma fonte de fora responderia
# NOT_APPLICABLE        a pergunta nao se aplica a este caso
# UNKNOWN               nao sei classificar a causa

SINAIS = [

 # ═══════════════════════════════════════════════════════════════════════════
 {
  'ID': 'ITF-001',
  'FUTURE_SIGNAL': 'A campanha 2026 abre sem estrategia definida contra Eriosoma '
                   'lanigerum em macieira: o palestrante chama 2026 de "anno zero" '
                   'e diz que a defesa sera um slalom entre revogacoes e possiveis '
                   'artigos 53 que ainda nao se conhecem.',
  'FUTURE_SIGNAL_TYPE': 'VAZIO_DE_SOLUCAO_ANUNCIADO',
  'EVIDENCE_TIME_STATE': 'EXPECTED',
  'EVIDENCE_TIME_WHY': 'nao e previsao meteorologica nem evento marcado: e uma '
                       'expectativa tecnica declarada por quem faz o balanco '
                       'fitossanitario da regiao, sobre uma campanha que ainda nao '
                       'comecou. O proprio palestrante marca a incerteza '
                       '("una grande incognita", "non abbiamo percezione").',
  'SOURCE_ID': 'uf5bx-oTees', 'SOURCE_TYPE': 'CONVEGNO_BILANCIO_FITOSANITARIO',
  'SOURCE_DATE': '2025-12-05',
  'SOURCE_TITLE': 'Il bilancio fitosanitario 2024/2025 delle pomacee — sessione insetti',
  'QUOTE_IT': 'l\'anno zero sara il 2026 e una grande incognita su come declineremo '
              'le strategie di difesa, facendo un po\' lo slalom tra revoche, '
              'possibili articoli 53 dei quali ancora oggi non abbiamo percezione',
  'COUNTRY': 'IT', 'REGION': 'Piemonte',
  'REGION_WHY': 'o palestrante fala do territorio piemontes e cita a giornata '
                'tecnica da Agrion, que e piemontesa',
  'CROP': 'MELO', 'TARGET': 'ERIOSOMA_LANIGERUM',
  'TARGET_IN_CONTROLLED_VOCAB': False,
  'EXPECTED_START': '2026-03', 'EXPECTED_END': '2026-09',
  'TIME_HORIZON_DAYS': 180, 'HORIZON_BUCKET': 'HORIZON_181_365_DAYS',
  'TRIGGER': 'publicacao (ou ausencia) de autorizacao excepcional artigo 53 para '
             'Eriosoma em macieira antes da retomada vegetativa de 2026',
  'INVALIDATION_TRIGGER': 'sai um artigo 53 que cobre o vazio, ou uma nova '
                          'autorizacao ordinaria — o sinal deixa de valer',
  'WINDOW_EXPECTED': 'YES',
  'EXPECTED_WINDOW_START': '2026-03', 'EXPECTED_WINDOW_END': '2026-06',
  'WINDOW_TRIGGER': 'gemme gonfie / retomada vegetativa — a propria fala cita o '
                    'oleo ativado nesse estadio',
  'WINDOW_SOURCE': 'a fala declara o estadio; nenhuma data de calendario e dada',
  'WINDOW_IS_CALENDAR_BASED': 'NO',
  'WINDOW_DEPENDS_ON_FIELD_MEASUREMENT': 'YES',
  'CONFIDENCE': 'MEDIUM',
  'CONFIDENCE_WHY': 'fonte tecnica regional em evento oficial, declarando o proprio '
                    'grau de incerteza. Uma fonte so, e sem documento normativo ao lado.',
  'ADAMA_LOCAL_RESPONSE': 'NO',
  'PORTFOLIO_MATCHES': [],
  'PRIMARY_MATCH': None,
  'PRIMARY_MATCH_REASON': 'NENHUM_PRODUTO_NO_PAR',
  'WHY_ADAMA': 'MELO x ERIOSOMA nao aparece em NENHUM dos 2.313 pares publicados. '
               'A rodada de rotulos ja tinha recusado inventar esse par para APYZA; '
               'aqui o campo confirma que o vazio existe dos dois lados.',
  'WHY_FUTURE': 'a campanha 2026 ainda nao comecou e a decisao de estrategia esta '
                'aberta agora',
  'WHY_COMMERCIAL': 'NAO E OPORTUNIDADE COMERCIAL. E um vazio de portfolio '
                    'declarado. Tratar como oportunidade seria vender o que nao '
                    'temos autorizacao para vender.',
  'DECISION_STILL_OPEN': 'YES',
  'DECISION_DEADLINE': '2026-03 (retomada vegetativa)',
  'LEAD_TIME_AVAILABLE': 'cerca de 3 meses a partir da data da fala',
  'FUTURE_INTELLIGENCE_STATE': 'COMPLETE',
  'ACTION_MAP': {
    'MARKET_DEVELOPMENT': {
      'ACTION_STATE': 'MARKET_DEVELOPMENT_VALIDATE',
      'ACTION': 'verificar se alguma substancia do portfolio tem eficacia declarada '
                'sobre Eriosoma em outro pais da EAME, e se existe caminho '
                'regulatorio italiano',
      'WHY': 'a lacuna e de autorizacao, nao de demanda: o campo declara o problema '
             'e diz que ficara sem ferramenta',
      'WHEN_TO_START': 'imediatamente', 'DEADLINE': '2026-02',
      'DEPENDENCY': 'registro regulatorio', 'NEXT_TRIGGER': 'artigo 53 publicado ou nao'},
    'TECHNICAL_SCIENTIFIC': {
      'ACTION_STATE': 'WATCH_TRIGGER',
      'ACTION': 'acompanhar a giornata tecnica Agrion e o balanco 2026',
      'WHY': 'o proprio evento anunciou que voltara ao tema',
      'WHEN_TO_START': '2026-01', 'DEADLINE': 'UNKNOWN',
      'DEPENDENCY': 'calendario do evento', 'NEXT_TRIGGER': 'anuncio da proxima edicao'},
    'COMMERCIAL': {
      'ACTION_STATE': 'WATCH_TRIGGER',
      'ACTION': 'nenhuma acao de venda — nao ha produto autorizado',
      'WHY': 'PORTFOLIO vazio para o par', 'WHEN_TO_START': 'NOT_APPLICABLE',
      'DEADLINE': 'NOT_APPLICABLE', 'DEPENDENCY': 'existencia de autorizacao',
      'NEXT_TRIGGER': 'autorizacao publicada'},
    'MARKETING': {'ACTION_STATE': 'WATCH_TRIGGER', 'ACTION': 'nenhuma',
                  'WHY': 'sem produto nao ha mensagem', 'WHEN_TO_START': 'NOT_APPLICABLE',
                  'DEADLINE': 'NOT_APPLICABLE', 'DEPENDENCY': 'MARKET_DEVELOPMENT',
                  'NEXT_TRIGGER': 'resultado da validacao'},
    'SUPPLY': {'ACTION_STATE': 'WATCH_TRIGGER', 'ACTION': 'nenhuma',
               'WHY': 'sem produto nao ha estoque a preparar',
               'WHEN_TO_START': 'NOT_APPLICABLE', 'DEADLINE': 'NOT_APPLICABLE',
               'DEPENDENCY': 'MARKET_DEVELOPMENT', 'NEXT_TRIGGER': 'idem'},
  },
  'MISSING_FIELDS': {},
 },

 # ═══════════════════════════════════════════════════════════════════════════
 {
  'ID': 'ITF-002',
  'FUTURE_SIGNAL': 'Revogacoes recentes deixam a psila do pero sem ferramentas: '
                   '"nao sera facil gerir a psila com estas revogacoes; sobra '
                   'muito pouco" e "nao teremos mais instrumentos a disposicao".',
  'FUTURE_SIGNAL_TYPE': 'RETIRADA_REGULATORIA_COM_EFEITO_FUTURO',
  'EVIDENCE_TIME_STATE': 'EXPECTED',
  'EVIDENCE_TIME_WHY': 'as revogacoes ja aconteceram (OBSERVED_NOW), mas a '
                       'consequencia declarada — ficar sem instrumento — e sobre as '
                       'campanhas seguintes. O que entra no radar futuro e a '
                       'consequencia, e nao o ato normativo.',
  'SOURCE_ID': 'uf5bx-oTees', 'SOURCE_TYPE': 'CONVEGNO_BILANCIO_FITOSANITARIO',
  'SOURCE_DATE': '2025-12-05',
  'SOURCE_TITLE': 'Il bilancio fitosanitario 2024/2025 delle pomacee — sessione insetti',
  'QUOTE_IT': 'non sara facile gestire la psilla con queste revoche recenti e quindi '
              'rimane veramente poco (...) questi inserimenti saranno sempre piu '
              'importanti, proprio perche non avremo piu strumenti a disposizione',
  'COUNTRY': 'IT', 'REGION': 'Piemonte',
  'REGION_WHY': 'a fala diz "la situazione a livello territoriale piemontese"',
  'CROP': 'PERO', 'TARGET': 'PSILLE', 'TARGET_IN_CONTROLLED_VOCAB': True,
  'EXPECTED_START': '2026-03', 'EXPECTED_END': '2026-08',
  'TIME_HORIZON_DAYS': 180, 'HORIZON_BUCKET': 'HORIZON_181_365_DAYS',
  'TRIGGER': 'primeira geracao de psila na retomada vegetativa de 2026 com o '
             'portfolio reduzido',
  'INVALIDATION_TRIGGER': 'nova autorizacao que reponha as moleculas revogadas',
  'WINDOW_EXPECTED': 'YES',
  'EXPECTED_WINDOW_START': '2026-02', 'EXPECTED_WINDOW_END': '2026-05',
  'WINDOW_TRIGGER': 'pre-fioritura / inicio da infestacao — a fala liga o oleo '
                    'ativado a "gemme gonfie"',
  'WINDOW_SOURCE': 'estadio declarado na fala; sem data de calendario',
  'WINDOW_IS_CALENDAR_BASED': 'NO',
  'WINDOW_DEPENDS_ON_FIELD_MEASUREMENT': 'YES',
  'CONFIDENCE': 'MEDIUM',
  'CONFIDENCE_WHY': 'duas vozes independentes no mesmo evento (o palestrante '
                    'confirma o que "diceva anche Lorenzo Tosi"). Falta o documento '
                    'normativo que nomeia as moleculas revogadas.',
  'ADAMA_LOCAL_RESPONSE': 'YES',
  'PORTFOLIO_MATCHES': [
    {'REGISTRATION_ID': '007555', 'PRODUCT': 'KLARTAN 20 EW',
     'ACTIVE_INGREDIENTS': ['TAU-FLUVALINATE'], 'PAIR_SOURCE': 'IT-ROTULOS-PARES-V3'},
    {'REGISTRATION_ID': '007864', 'PRODUCT': 'TAU AL 240 EW',
     'ACTIVE_INGREDIENTS': ['TAU-FLUVALINATE'], 'PAIR_SOURCE': 'IT-ROTULOS-PARES-V3'},
    {'REGISTRATION_ID': '009800', 'PRODUCT': 'MAVRIK SMART',
     'ACTIVE_INGREDIENTS': ['TAU-FLUVALINATE'], 'PAIR_SOURCE': 'IT-ROTULOS-PARES-V3'},
    {'REGISTRATION_ID': '012023', 'PRODUCT': 'KLARTAN SMART',
     'ACTIVE_INGREDIENTS': ['TAU-FLUVALINATE'], 'PAIR_SOURCE': 'IT-ROTULOS-PARES-V3'},
    {'REGISTRATION_ID': '014190', 'PRODUCT': 'MAVRIK EW',
     'ACTIVE_INGREDIENTS': ['TAU-FLUVALINATE'], 'PAIR_SOURCE': 'IT-ROTULOS-PARES-V3'},
    {'REGISTRATION_ID': '014210', 'PRODUCT': 'EVURE PRO',
     'ACTIVE_INGREDIENTS': ['TAU-FLUVALINATE'], 'PAIR_SOURCE': 'IT-ROTULOS-PARES-V3'},
    {'REGISTRATION_ID': '012573', 'PRODUCT': 'EKO OIL SPRAY',
     'ACTIVE_INGREDIENTS': ['PARAFFIN OIL'], 'PAIR_SOURCE': 'IT-ROTULOS-PARES-V3'},
    {'REGISTRATION_ID': '014386', 'PRODUCT': 'OLIONET',
     'ACTIVE_INGREDIENTS': ['PARAFFIN OIL'], 'PAIR_SOURCE': 'IT-ROTULOS-PARES-V3'},
  ],
  'PRIMARY_MATCH': None,
  'PRIMARY_MATCH_REASON': 'SEM_REGRA_DEFENSAVEL_PARA_ESCOLHER — oito rotulos, duas '
                          'familias quimicas, e a fonte NAO nomeia nenhuma '
                          'substancia. Escolher um seria eleger pelo array.',
  'WHY_ADAMA': 'oito rotulos ADAMA autorizam PERO x PSILLE nos pares publicados, em '
               'duas familias distintas (tau-fluvalinato e oleo de parafina). O '
               'oleo tem interesse particular: a propria fala cita o oleo ativado '
               'como pratica que se difunde.',
  'WHY_FUTURE': 'a consequencia das revogacoes se realiza na campanha seguinte, que '
                'ainda nao comecou',
  'WHY_COMMERCIAL': 'abertura competitiva: o campo declara escassez de ferramenta '
                    'num par em que a ADAMA tem autorizacao viva. NAO prova demanda '
                    'nem venda — prova que o espaco tecnico existe.',
  'DECISION_STILL_OPEN': 'YES',
  'DECISION_DEADLINE': '2026-02 (antes da retomada vegetativa)',
  'LEAD_TIME_AVAILABLE': 'cerca de 2 a 3 meses a partir da data da fala',
  'FUTURE_INTELLIGENCE_STATE': 'COMPLETE',
  'ACTION_MAP': {
    'MARKET_DEVELOPMENT': {
      'ACTION_STATE': 'VALIDATE_BEFORE_WINDOW',
      'ACTION': 'montar testemunha de campo em pereira piemontesa comparando o '
                'oleo de parafina em gemme gonfie com o padrao que restou apos as '
                'revogacoes',
      'WHY': 'a fala declara que o oleo ativado ja se difunde e que faltam '
             'ferramentas: e a janela para gerar prova local ANTES da campanha',
      'WHEN_TO_START': '2026-01', 'DEADLINE': '2026-02',
      'DEPENDENCY': 'acesso a pomar piemontes com historico de psila',
      'NEXT_TRIGGER': 'gemme gonfie'},
    'TECHNICAL_SCIENTIFIC': {
      'ACTION_STATE': 'PREPARE_NOW',
      'ACTION': 'levantar quais moleculas foram efetivamente revogadas e datar cada '
                'revogacao no documento oficial',
      'WHY': 'a fala nao nomeia as moleculas; sem isso o argumento tecnico fica sem '
             'lastro documental',
      'WHEN_TO_START': 'imediatamente', 'DEADLINE': '2026-01',
      'DEPENDENCY': 'consulta ao registro fitossanitario',
      'NEXT_TRIGGER': 'lista de revogacoes fechada'},
    'COMMERCIAL': {
      'ACTION_STATE': 'COMMERCIAL_PREPARE',
      'ACTION': 'mapear as cooperativas de pomacee do Piemonte antes de fevereiro',
      'WHY': 'a janela agronomica abre na retomada vegetativa e a decisao de compra '
             'e anterior a ela',
      'WHEN_TO_START': '2026-01', 'DEADLINE': '2026-02',
      'DEPENDENCY': 'lista de canal — HOJE INEXISTENTE no acervo',
      'NEXT_TRIGGER': 'validacao tecnica concluida'},
    'MARKETING': {
      'ACTION_STATE': 'MARKETING_PREPARE',
      'ACTION': 'preparar material tecnico sobre manejo da psila com portfolio '
                'reduzido, sem afirmar substituicao de molecula revogada',
      'WHY': 'a mensagem util e de MANEJO, e nao de troca direta',
      'WHEN_TO_START': '2026-01', 'DEADLINE': '2026-02',
      'DEPENDENCY': 'TECHNICAL_SCIENTIFIC', 'NEXT_TRIGGER': 'lista de revogacoes'},
    'SUPPLY': {
      'ACTION_STATE': 'SUPPLY_PREPARE',
      'ACTION': 'checar cobertura de estoque de oleo de parafina e tau-fluvalinato '
                'para a janela de fevereiro a maio no noroeste',
      'WHY': 'janela curta e concentrada; ruptura nela nao se recupera no ano',
      'WHEN_TO_START': '2026-01', 'DEADLINE': '2026-02',
      'DEPENDENCY': 'previsao comercial', 'NEXT_TRIGGER': 'confirmacao do comercial'},
  },
  'MISSING_FIELDS': {
    'REVOKED_MOLECULES': 'NOT_IN_SOURCE — a fala diz "queste revoche" sem nomear',
    'CHANNEL': 'NOT_COLLECTED — nao ha camada de cooperativa/revenda no acervo',
  },
 },

 # ═══════════════════════════════════════════════════════════════════════════
 {
  'ID': 'ITF-003',
  'FUTURE_SIGNAL': 'Resistencia multipla a varios mecanismos de acao em Lolium, '
                   'Papavero e Avena no trigo duro da Puglia — descrita como '
                   '"grave, gravissima" e presente "em todos os talhoes, todos os '
                   'areais" de Foggia e Bari.',
  'FUTURE_SIGNAL_TYPE': 'RESISTENCIA_EMERGENTE_CONSOLIDADA',
  'EVIDENCE_TIME_STATE': 'OBSERVED_NOW',
  'EVIDENCE_TIME_WHY': 'a resistencia JA existe e e observada — nao e previsao. O '
                       'que e futuro e a CONSEQUENCIA: a proxima semeadura de '
                       'outono-inverno tera de ser desenhada com isso. Registro o '
                       'estado como OBSERVED_NOW e nao inflo para FORECAST.',
  'SOURCE_ID': 'mIunZ-pH3RY', 'SOURCE_TYPE': 'CONVEGNO_BILANCIO_FITOSANITARIO',
  'SOURCE_DATE': '2025-11-07',
  'SOURCE_TITLE': 'Il bilancio fitosanitario 2024/2025 dei cereali e della soia',
  'QUOTE_IT': 'le infestanti resistenti agli erbicidi ormai sono diventate molto '
              'frequenti in tutti gli appezzamenti, tutti gli areali, in particolare '
              'di Lolium, Papavero e Avena, sono presenti popolazioni resistenti con '
              'resistenza multipla a diversi meccanismi di azione',
  'COUNTRY': 'IT', 'REGION': 'Puglia (Foggia, Bari)',
  'REGION_WHY': 'as provincias sao nomeadas na propria fala',
  'CROP': 'FRUMENTO', 'TARGET': 'INFESTANTI', 'TARGET_IN_CONTROLLED_VOCAB': True,
  'EXPECTED_START': '2026-10', 'EXPECTED_END': '2027-04',
  'TIME_HORIZON_DAYS': 330, 'HORIZON_BUCKET': 'NEXT_SEASON',
  'TRIGGER': 'semeadura de outono-inverno 2026/27 e a decisao de programa de '
             'diserbo que a antecede',
  'INVALIDATION_TRIGGER': 'monitoramento que mostre reversao das populacoes — '
                          'improvavel no horizonte de uma safra',
  'WINDOW_EXPECTED': 'YES',
  'EXPECTED_WINDOW_START': '2026-10', 'EXPECTED_WINDOW_END': '2027-02',
  'WINDOW_TRIGGER': 'pre-emergencia e pos-emergencia precoce do cereal',
  'WINDOW_SOURCE': 'os proprios rotulos ADAMA declaram a epoca; a fala nao da data',
  'WINDOW_IS_CALENDAR_BASED': 'NO',
  'WINDOW_DEPENDS_ON_FIELD_MEASUREMENT': 'NO',
  'CONFIDENCE': 'HIGH',
  'CONFIDENCE_WHY': 'fonte tecnica oficial, provincias nomeadas, especies nomeadas, '
                    'mecanismo nomeado (resistencia multipla). Nada aqui depende de '
                    'interpretacao minha.',
  'ADAMA_LOCAL_RESPONSE': 'YES',
  'PORTFOLIO_MATCHES': [
    {'REGISTRATION_ID': '015229', 'PRODUCT': 'STOPPER P',
     'ACTIVE_INGREDIENTS': ['PENDIMETHALIN', 'DIFLUFENICAN'], 'MOA_NOTE': 'HRAC K1 + F1'},
    {'REGISTRATION_ID': '016218', 'PRODUCT': 'DICURAN PLUS',
     'ACTIVE_INGREDIENTS': ['CHLOROTOLURON', 'DIFLUFENICAN'], 'MOA_NOTE': 'HRAC C2 + F1'},
    {'REGISTRATION_ID': '016823', 'PRODUCT': 'ACTIVUS 40 SC',
     'ACTIVE_INGREDIENTS': ['PENDIMETHALIN'], 'MOA_NOTE': 'HRAC K1'},
    {'REGISTRATION_ID': '017094', 'PRODUCT': 'ANTHEM EKO',
     'ACTIVE_INGREDIENTS': ['PENDIMETHALIN'], 'MOA_NOTE': 'HRAC K1'},
    {'REGISTRATION_ID': '017660', 'PRODUCT': 'ACTIGAN EKO',
     'ACTIVE_INGREDIENTS': ['PENDIMETHALIN'], 'MOA_NOTE': 'HRAC K1'},
  ],
  'PRIMARY_MATCH': None,
  'PRIMARY_MATCH_REASON': 'SEM_REGRA_DEFENSAVEL_PARA_ESCOLHER — 15 rotulos '
                          'FRUMENTO x INFESTANTI no conjunto publicado e a fonte '
                          'nao nomeia substancia. Listo os de mecanismo NAO-ALS '
                          'porque e o que a resistencia declarada torna relevante, '
                          'e nao porque um deles seja "o" produto.',
  'WHY_ADAMA': 'a resistencia declarada e a mecanismos de acao multiplos, e a '
               'fala nomeia ALS implicitamente pelas especies afetadas. O portfolio '
               'ADAMA de cereais em Italia e pendimetalina (K1), clorotoluron (C2) e '
               'diflufenican (F1) — nenhum deles ALS. Essa e a razao tecnica, e nao '
               'uma preferencia comercial.',
  'WHY_FUTURE': 'a decisao de programa de diserbo do proximo outono-inverno esta '
                'aberta agora e e tomada meses antes da semeadura',
  'WHY_COMMERCIAL': 'a demanda por mecanismo alternativo e uma consequencia tecnica '
                    'da resistencia declarada. NAO prova venda nem participacao de '
                    'mercado.',
  'DECISION_STILL_OPEN': 'YES', 'DECISION_DEADLINE': '2026-09',
  'LEAD_TIME_AVAILABLE': 'cerca de 10 meses',
  'FUTURE_INTELLIGENCE_STATE': 'COMPLETE',
  'ACTION_MAP': {
    'MARKET_DEVELOPMENT': {
      'ACTION_STATE': 'MARKET_DEVELOPMENT_VALIDATE',
      'ACTION': 'protocolo de campo em Foggia/Bari com pendimetalina e clorotoluron '
                'sobre populacoes de Lolium com resistencia confirmada',
      'WHY': 'sem testemunha local o argumento de mecanismo alternativo e teoria',
      'WHEN_TO_START': '2026-06', 'DEADLINE': '2026-09',
      'DEPENDENCY': 'acesso a talhoes com resistencia caracterizada',
      'NEXT_TRIGGER': 'semeadura 2026/27'},
    'TECHNICAL_SCIENTIFIC': {
      'ACTION_STATE': 'PREPARE_NOW',
      'ACTION': 'obter a caracterizacao dos mecanismos resistentes das populacoes '
                'pugliesi junto ao grupo que apresentou o balanco',
      'WHY': 'a fala diz "diversi meccanismi" sem enumera-los; sem a lista, a '
             'recomendacao de alternancia fica generica',
      'WHEN_TO_START': 'imediatamente', 'DEADLINE': '2026-05',
      'DEPENDENCY': 'contato com o relator', 'NEXT_TRIGGER': 'publicacao dos atos'},
    'COMMERCIAL': {
      'ACTION_STATE': 'COMMERCIAL_PREPARE',
      'ACTION': 'preparar a campanha de cereais do sul para a temporada 2026/27',
      'WHY': 'a compra de herbicida de cereal e decidida no verao anterior',
      'WHEN_TO_START': '2026-06', 'DEADLINE': '2026-09',
      'DEPENDENCY': 'canal na Puglia — HOJE INEXISTENTE no acervo',
      'NEXT_TRIGGER': 'validacao tecnica'},
    'MARKETING': {
      'ACTION_STATE': 'MARKETING_PREPARE',
      'ACTION': 'material sobre alternancia de mecanismo em cereais, ancorado no '
                'balanco fitossanitario publico',
      'WHY': 'a fonte e publica e oficial, o que permite citar sem expor cliente',
      'WHEN_TO_START': '2026-06', 'DEADLINE': '2026-09',
      'DEPENDENCY': 'TECHNICAL_SCIENTIFIC', 'NEXT_TRIGGER': 'lista de mecanismos'},
    'SUPPLY': {
      'ACTION_STATE': 'SUPPLY_PREPARE',
      'ACTION': 'projetar demanda de pendimetalina e clorotoluron para o sul na '
                'janela outubro-fevereiro',
      'WHY': 'janela de pre-emergencia e concentrada e nao se recupera depois',
      'WHEN_TO_START': '2026-07', 'DEADLINE': '2026-09',
      'DEPENDENCY': 'previsao comercial', 'NEXT_TRIGGER': 'plano comercial fechado'},
  },
  'MISSING_FIELDS': {
    'RESISTANT_MOA_LIST': 'NOT_IN_SOURCE — a fala diz "diversi meccanismi" sem '
                          'enumerar; exigiria o artigo completo',
    'AREA_AFFECTED': 'NEEDS_EXTERNAL_SOURCE — nenhuma fonte do acervo da hectares',
    'CHANNEL': 'NOT_COLLECTED',
  },
 },

 # ═══════════════════════════════════════════════════════════════════════════
 {
  'ID': 'ITF-004',
  'FUTURE_SIGNAL': 'Um concorrente registra herbicida novo de cereais com '
                   'piroxsulam + metsulfuron, apresentado nas Giornate '
                   'Fitopatologiche de marco de 2026, para frumento duro, tenero e '
                   'triticale, com foco em graminaceas.',
  'FUTURE_SIGNAL_TYPE': 'LANCAMENTO_DE_CONCORRENTE',
  'EVIDENCE_TIME_STATE': 'ANNOUNCED',
  'EVIDENCE_TIME_WHY': 'o produto e descrito como "di nuova registrazione" e '
                       'apresentado num congresso — o ato ja ocorreu, a entrada em '
                       'mercado e o que ainda se desdobra. ANNOUNCED, e nao FORECAST.',
  'SOURCE_ID': '3m0OxLSK4ro', 'SOURCE_TYPE': 'CONGRESSO_CIENTIFICO',
  'SOURCE_DATE': '2026-05-11',
  'SOURCE_TITLE': 'Giornate Fitopatologiche 2026 — sessao da manha de 18 de marco',
  'QUOTE_IT': 'un nuovo prodotto per il diserbo dei cereali a base di questi due '
              'principi attivi, il piroxulam e metsulfuron (...) concepiti per una '
              'sorta di complementarieta per il controllo soprattutto delle '
              'graminacee, ma in parte anche delle dicotiledoni per frumento duro e '
              'tenero e triticale (...) di nuova registrazione',
  'COUNTRY': 'IT', 'REGION': 'UNKNOWN',
  'REGION_WHY': 'NOT_IN_SOURCE — a apresentacao e nacional e nao regionaliza',
  'CROP': 'FRUMENTO', 'TARGET': 'INFESTANTI', 'TARGET_IN_CONTROLLED_VOCAB': True,
  'EXPECTED_START': '2026-10', 'EXPECTED_END': '2027-04',
  'TIME_HORIZON_DAYS': 330, 'HORIZON_BUCKET': 'NEXT_SEASON',
  'TRIGGER': 'a primeira campanha comercial do produto no diserbo de cereais',
  'INVALIDATION_TRIGGER': 'o produto nao chegar ao canal na temporada',
  'WINDOW_EXPECTED': 'YES',
  'EXPECTED_WINDOW_START': '2026-11', 'EXPECTED_WINDOW_END': '2027-03',
  'WINDOW_TRIGGER': 'pos-emergencia do cereal',
  'WINDOW_SOURCE': 'a fala declara o alvo e a cultura; a epoca vem da pratica '
                   'declarada nos rotulos de cereais',
  'WINDOW_IS_CALENDAR_BASED': 'NO',
  'WINDOW_DEPENDS_ON_FIELD_MEASUREMENT': 'NO',
  'CONFIDENCE': 'MEDIUM',
  'CONFIDENCE_WHY': 'a transcricao e ASR e escreve "piroxulam" e "mezzo sulfuron"; '
                    'a leitura como piroxsulam + metsulfuron e minha, sustentada '
                    'pelo contexto (familia das sulfonilureias e das '
                    'triazolopirimidinas, dito na propria fala). O nome comercial '
                    'que a ASR devolve ("fancade") NAO e confiavel e nao entra.',
  'ADAMA_LOCAL_RESPONSE': 'YES',
  'PORTFOLIO_MATCHES': [
    {'REGISTRATION_ID': '015229', 'PRODUCT': 'STOPPER P',
     'ACTIVE_INGREDIENTS': ['PENDIMETHALIN', 'DIFLUFENICAN'], 'MOA_NOTE': 'HRAC K1 + F1'},
    {'REGISTRATION_ID': '016218', 'PRODUCT': 'DICURAN PLUS',
     'ACTIVE_INGREDIENTS': ['CHLOROTOLURON', 'DIFLUFENICAN'], 'MOA_NOTE': 'HRAC C2 + F1'},
  ],
  'PRIMARY_MATCH': None,
  'PRIMARY_MATCH_REASON': 'SEM_REGRA_DEFENSAVEL_PARA_ESCOLHER',
  'WHY_ADAMA': 'CRUZAMENTO ENTRE DUAS FONTES INDEPENDENTES DO ACERVO: piroxsulam e '
               'metsulfuron sao ambos inibidores de ALS, e o balanco dos cereais '
               '(ITF-003, outra fonte, outro evento, outra data) declara resistencia '
               'MULTIPLA justamente em Lolium, Papavero e Avena na Puglia. Um '
               'lancamento ALS entra num mercado onde a resistencia a esse '
               'mecanismo ja e descrita como gravissima. O portfolio ADAMA de '
               'cereais nao e ALS.',
  'WHY_FUTURE': 'a campanha em que o produto competira ainda nao comecou',
  'WHY_COMMERCIAL': 'define o terreno competitivo da proxima temporada de cereais. '
                    'NAO prova que o concorrente falhara — prova que ha uma pergunta '
                    'tecnica legitima a fazer no campo.',
  'DECISION_STILL_OPEN': 'YES', 'DECISION_DEADLINE': '2026-09',
  'LEAD_TIME_AVAILABLE': 'cerca de 4 meses ate o planejamento da campanha',
  'FUTURE_INTELLIGENCE_STATE': 'PARTIAL',
  'WHY_PARTIAL': 'REGION = UNKNOWN e o nome comercial nao e legivel na ASR. O caso '
                 'sustenta o cruzamento tecnico, mas nao sustenta uma acao '
                 'territorial.',
  'ACTION_MAP': {
    'MARKET_DEVELOPMENT': {
      'ACTION_STATE': 'MARKET_DEVELOPMENT_VALIDATE',
      'ACTION': 'incluir uma testemunha ALS versus nao-ALS no protocolo de Foggia '
                'ja previsto em ITF-003',
      'WHY': 'a mesma parcela responde as duas perguntas; montar dois ensaios '
             'separados seria desperdicio',
      'WHEN_TO_START': '2026-06', 'DEADLINE': '2026-09',
      'DEPENDENCY': 'ITF-003', 'NEXT_TRIGGER': 'semeadura 2026/27'},
    'TECHNICAL_SCIENTIFIC': {
      'ACTION_STATE': 'PREPARE_NOW',
      'ACTION': 'confirmar no registro italiano o nome e o numero do produto novo, '
                'porque a ASR nao permite le-lo',
      'WHY': 'sem o registro nao ha nome citavel',
      'WHEN_TO_START': 'imediatamente', 'DEADLINE': '2026-06',
      'DEPENDENCY': 'consulta ao registro', 'NEXT_TRIGGER': 'nome confirmado'},
    'COMMERCIAL': {'ACTION_STATE': 'WATCH_TRIGGER',
      'ACTION': 'observar a entrada do produto no canal',
      'WHY': 'sem regiao declarada nao ha territorio a preparar',
      'WHEN_TO_START': '2026-09', 'DEADLINE': 'UNKNOWN',
      'DEPENDENCY': 'nome confirmado', 'NEXT_TRIGGER': 'aparicao em lista de preco'},
    'MARKETING': {'ACTION_STATE': 'WATCH_TRIGGER', 'ACTION': 'nenhuma agora',
      'WHY': 'comunicar contra um concorrente sem o nome confirmado seria imprudente',
      'WHEN_TO_START': 'NOT_APPLICABLE', 'DEADLINE': 'NOT_APPLICABLE',
      'DEPENDENCY': 'TECHNICAL_SCIENTIFIC', 'NEXT_TRIGGER': 'nome confirmado'},
    'SUPPLY': {'ACTION_STATE': 'WATCH_TRIGGER', 'ACTION': 'nenhuma',
      'WHY': 'nao ha efeito de estoque mensuravel a partir deste sinal',
      'WHEN_TO_START': 'NOT_APPLICABLE', 'DEADLINE': 'NOT_APPLICABLE',
      'DEPENDENCY': '-', 'NEXT_TRIGGER': '-'},
  },
  'MISSING_FIELDS': {
    'REGION': 'NOT_IN_SOURCE — apresentacao nacional',
    'PRODUCT_NAME': 'NOT_EXTRACTED — a ASR devolve ruido; o registro resolveria',
    'REGISTRATION_NUMBER': 'NEEDS_EXTERNAL_SOURCE — consulta ao registro italiano',
  },
 },

 # ═══════════════════════════════════════════════════════════════════════════
 {
  'ID': 'ITF-005',
  'FUTURE_SIGNAL': 'Cyperus deixou de ser emergente e esta INSTALADO nos solos '
                   'arenosos de Ferrara, com achados ja no bolonhes. A regiao '
                   'concedeu artigo 53 para sulfosulfuron, cuja etiqueta obriga a '
                   'cultura seguinte a ser frumento, orzo ou veccia.',
  'FUTURE_SIGNAL_TYPE': 'DANINHA_EMERGENTE_CONSOLIDADA_COM_TRAVA_DE_ROTACAO',
  'EVIDENCE_TIME_STATE': 'OBSERVED_NOW',
  'EVIDENCE_TIME_WHY': 'a instalacao e observada e a deroga ja foi concedida. O '
                       'FUTURO aqui e a trava de rotacao: quem aplicou este ano '
                       'esta obrigado a semear cereal ou veccia no ano seguinte. '
                       'Isso e consequencia contratada, e nao previsao.',
  'SOURCE_ID': 'dGmP236Z4uQ', 'SOURCE_TYPE': 'CONVEGNO_BILANCIO_FITOSANITARIO',
  'SOURCE_DATE': '2025-10-20',
  'SOURCE_TITLE': 'Il bilancio fitosanitario 2024/2025 di pomodoro e patata',
  'QUOTE_IT': 'nel 2023 lo avevamo citato come problematica emergente. Adesso non e '
              'piu emergente nel ferrarese purtroppo, ma e insediata (...) uso '
              'eccezionale del solfosulfuron (...) c\'e stato l\'articolo 53 e anche '
              'noi come regione abbiamo concesso la deroga (...) nell\'etichetta e '
              'specificato che la coltura seguente nella rotazione dovra essere '
              'frumento, orzo, veccia',
  'COUNTRY': 'IT', 'REGION': 'Emilia-Romagna (Ferrara; achados em Bologna)',
  'REGION_WHY': 'provincias nomeadas na fala',
  'CROP': 'PATATA', 'TARGET': 'INFESTANTI', 'TARGET_IN_CONTROLLED_VOCAB': True,
  'EXPECTED_START': '2026-10', 'EXPECTED_END': '2027-06',
  'TIME_HORIZON_DAYS': 300, 'HORIZON_BUCKET': 'NEXT_SEASON',
  'TRIGGER': 'a semeadura do cereal obrigatorio na rotacao apos a batata tratada',
  'INVALIDATION_TRIGGER': 'nova deroga que remova a trava de rotacao, ou registro '
                          'ordinario com outra prescricao',
  'WINDOW_EXPECTED': 'YES',
  'EXPECTED_WINDOW_START': '2026-10', 'EXPECTED_WINDOW_END': '2026-12',
  'WINDOW_TRIGGER': 'semeadura de frumento/orzo apos a batata',
  'WINDOW_SOURCE': 'a trava esta na etiqueta do produto derogado, citada na fala',
  'WINDOW_IS_CALENDAR_BASED': 'NO',
  'WINDOW_DEPENDS_ON_FIELD_MEASUREMENT': 'NO',
  'CONFIDENCE': 'HIGH',
  'CONFIDENCE_WHY': 'a fonte e o servico fitossanitario da propria regiao que '
                    'concedeu a deroga, e cita a prescricao da etiqueta que exibiu '
                    'em tela.',
  'ADAMA_LOCAL_RESPONSE': 'YES',
  'PORTFOLIO_MATCHES': [
    {'REGISTRATION_ID': '015229', 'PRODUCT': 'STOPPER P',
     'ACTIVE_INGREDIENTS': ['PENDIMETHALIN', 'DIFLUFENICAN'],
     'FIT_NOTE': 'entra na CULTURA SEGUINTE obrigatoria (frumento/orzo), e nao na '
                 'batata'},
    {'REGISTRATION_ID': '016218', 'PRODUCT': 'DICURAN PLUS',
     'ACTIVE_INGREDIENTS': ['CHLOROTOLURON', 'DIFLUFENICAN'],
     'FIT_NOTE': 'idem'},
  ],
  'PRIMARY_MATCH': None,
  'PRIMARY_MATCH_REASON': 'SEM_REGRA_DEFENSAVEL_PARA_ESCOLHER',
  'WHY_ADAMA': 'o encaixe NAO e na batata: e na cultura seguinte que a trava de '
               'rotacao obriga. Quem aplicou sulfosulfuron em Ferrara tera cereal no '
               'talhao, e a ADAMA tem 15 rotulos FRUMENTO x INFESTANTI e 15 em ORZO. '
               'Uma area de cereal previsivel, criada por prescricao de etiqueta.',
  'WHY_FUTURE': 'a area de cereal obrigatorio ainda nao foi semeada',
  'WHY_COMMERCIAL': 'demanda de herbicida de cereal geograficamente concentrada e '
                    'antecipavel. NAO prova hectares: nenhuma fonte do acervo diz '
                    'quantos talhoes usaram a deroga.',
  'DECISION_STILL_OPEN': 'YES', 'DECISION_DEADLINE': '2026-09',
  'LEAD_TIME_AVAILABLE': 'cerca de 11 meses',
  'FUTURE_INTELLIGENCE_STATE': 'COMPLETE',
  'ACTION_MAP': {
    'MARKET_DEVELOPMENT': {
      'ACTION_STATE': 'MARKET_DEVELOPMENT_VALIDATE',
      'ACTION': 'confirmar com o servico fitossanitario da Emilia-Romagna quantos '
                'talhoes usaram a deroga e onde',
      'WHY': 'o tamanho da area obrigada e a unica coisa que falta para o caso '
             'virar acao comercial dimensionada',
      'WHEN_TO_START': 'imediatamente', 'DEADLINE': '2026-06',
      'DEPENDENCY': 'dado da regiao', 'NEXT_TRIGGER': 'resposta do servico'},
    'COMMERCIAL': {
      'ACTION_STATE': 'COMMERCIAL_PREPARE',
      'ACTION': 'preparar oferta de herbicida de cereal para o ferrarense antes de '
                'setembro de 2026',
      'WHY': 'a rotacao esta contratada por etiqueta; a area vira cereal quer o '
             'produtor queira ou nao',
      'WHEN_TO_START': '2026-06', 'DEADLINE': '2026-09',
      'DEPENDENCY': 'dimensionamento', 'NEXT_TRIGGER': 'resposta da regiao'},
    'TECHNICAL_SCIENTIFIC': {
      'ACTION_STATE': 'PREPARE_NOW',
      'ACTION': 'verificar se ha residual do sulfosulfuron que restrinja o herbicida '
                'do cereal seguinte',
      'WHY': 'a etiqueta trava a rotacao; pode travar tambem o programa seguinte',
      'WHEN_TO_START': 'imediatamente', 'DEADLINE': '2026-05',
      'DEPENDENCY': 'etiqueta do produto derogado', 'NEXT_TRIGGER': 'leitura da etiqueta'},
    'MARKETING': {'ACTION_STATE': 'MARKETING_PREPARE',
      'ACTION': 'material sobre manejo de Cyperus em rotacao batata-cereal',
      'WHY': 'o tema e novo na regiao e a fonte publica ja o nomeou',
      'WHEN_TO_START': '2026-06', 'DEADLINE': '2026-09',
      'DEPENDENCY': 'TECHNICAL_SCIENTIFIC', 'NEXT_TRIGGER': 'validacao'},
    'SUPPLY': {'ACTION_STATE': 'WATCH_TRIGGER',
      'ACTION': 'aguardar o dimensionamento antes de projetar volume',
      'WHY': 'sem hectares nao ha volume defensavel',
      'WHEN_TO_START': '2026-06', 'DEADLINE': 'UNKNOWN',
      'DEPENDENCY': 'MARKET_DEVELOPMENT', 'NEXT_TRIGGER': 'area confirmada'},
  },
  'MISSING_FIELDS': {
    'AREA_UNDER_DEROGATION': 'NEEDS_EXTERNAL_SOURCE — so o servico regional tem',
    'CHANNEL': 'NOT_COLLECTED',
  },
 },

 # ═══════════════════════════════════════════════════════════════════════════
 {
  'ID': 'ITF-006',
  'FUTURE_SIGNAL': 'A producao integrada do olivo nas Marche esta no teto: em 2025 '
                   'foram PEDIDAS derogas para mais dois tratamentos larvicidas e um '
                   'de piretro contra a mosca, e ainda uma deroga para a tignola.',
  'FUTURE_SIGNAL_TYPE': 'PRESSAO_REGULATORIA_RECORRENTE',
  'EVIDENCE_TIME_STATE': 'ANNOUNCED',
  'EVIDENCE_TIME_WHY': 'o pedido de deroga e um ato declarado e datado (2025). O que '
                       'NAO se sabe pela fonte e se foi concedido — e por isso nao '
                       'escrevo SCHEDULED nem trato o resultado como conhecido.',
  'SOURCE_ID': '-4lUyIORl4A', 'SOURCE_TYPE': 'CONVEGNO_BILANCIO_FITOSANITARIO',
  'SOURCE_DATE': '2025-12-11',
  'SOURCE_TITLE': "Il bilancio fitosanitario 2024/2025 dell'olivo — I sessione",
  'QUOTE_IT': 'nel disciplinare di produzione integrata abbiamo due trattamenti '
              'ammessi larvicidi e un piretro (...) Nel 2025 sono state chieste la '
              'deroga per ulteriori due trattamenti larvicidi e un ulteriore '
              'trattamento di piretro (...) quest\'anno e stato chiesto la deroga '
              'anche su Prays, la tignola',
  'COUNTRY': 'IT', 'REGION': 'Marche',
  'REGION_WHY': 'o relator fala pelo servico das Marche e compara-se a Toscana',
  'CROP': 'OLIVO', 'TARGET': 'MOSCA', 'TARGET_IN_CONTROLLED_VOCAB': True,
  'EXPECTED_START': '2026-06', 'EXPECTED_END': '2026-10',
  'TIME_HORIZON_DAYS': 240, 'HORIZON_BUCKET': 'HORIZON_181_365_DAYS',
  'TRIGGER': 'pedido de deroga da campanha 2026 ao disciplinare regional',
  'INVALIDATION_TRIGGER': 'revisao do disciplinare que amplie o numero ordinario de '
                          'tratamentos — a deroga deixa de ser necessaria',
  'WINDOW_EXPECTED': 'YES',
  'EXPECTED_WINDOW_START': '2026-07', 'EXPECTED_WINDOW_END': '2026-09',
  'WINDOW_TRIGGER': 'monitoramento semanal de armadilhas — a propria fala descreve '
                    'visitas semanais com trappole',
  'WINDOW_SOURCE': 'declarado na fala',
  'WINDOW_IS_CALENDAR_BASED': 'NO',
  'WINDOW_DEPENDS_ON_FIELD_MEASUREMENT': 'YES',
  'CONFIDENCE': 'MEDIUM',
  'CONFIDENCE_WHY': 'fonte oficial regional e ato datado, mas a fala nao diz se a '
                    'deroga foi concedida nem quais moleculas cobre.',
  'ADAMA_LOCAL_RESPONSE': 'UNKNOWN',
  'PORTFOLIO_MATCHES': [],
  'PRIMARY_MATCH': None,
  'PRIMARY_MATCH_REASON': 'NENHUM_PRODUTO_NO_PAR',
  'WHY_ADAMA': 'OLIVO x MOSCA nao aparece nos 2.313 pares publicados. Os nove '
               'rotulos que autorizam OLIVO cobrem COCCINIGLIE, TIGNOLE e '
               'INFESTANTI — nenhum cobre a mosca. A assimetria do olivo, medida na '
               'rodada anterior, continua de pe e agora tem data: e no alvo de maior '
               'pressao regulatoria que falta autorizacao.',
  'WHY_FUTURE': 'a campanha 2026 e o pedido de deroga que a acompanha ainda nao '
                'aconteceram',
  'WHY_COMMERCIAL': 'NAO E OPORTUNIDADE DE VENDA. E a medida exata de um vazio: o '
                    'alvo que consome deroga todo ano e o que o portfolio nao cobre.',
  'DECISION_STILL_OPEN': 'YES', 'DECISION_DEADLINE': '2026-06',
  'LEAD_TIME_AVAILABLE': 'cerca de 6 meses',
  'FUTURE_INTELLIGENCE_STATE': 'COMPLETE',
  'ACTION_MAP': {
    'MARKET_DEVELOPMENT': {
      'ACTION_STATE': 'MARKET_DEVELOPMENT_VALIDATE',
      'ACTION': 'verificar se alguma substancia ADAMA tem autorizacao para '
                'Bactrocera oleae em outro pais da EAME e qual o caminho italiano',
      'WHY': 'a pressao e recorrente e documentada; o vazio e de autorizacao',
      'WHEN_TO_START': 'imediatamente', 'DEADLINE': '2026-06',
      'DEPENDENCY': 'registro', 'NEXT_TRIGGER': 'campanha 2026'},
    'TECHNICAL_SCIENTIFIC': {
      'ACTION_STATE': 'WATCH_TRIGGER',
      'ACTION': 'acompanhar o balanco do olivo de 2026 e o desfecho da deroga de 2025',
      'WHY': 'a fonte nao diz se foi concedida',
      'WHEN_TO_START': '2026-01', 'DEADLINE': 'UNKNOWN',
      'DEPENDENCY': 'publicacao regional', 'NEXT_TRIGGER': 'proximo bilancio'},
    'COMMERCIAL': {'ACTION_STATE': 'WATCH_TRIGGER', 'ACTION': 'nenhuma',
      'WHY': 'sem autorizacao nao ha oferta', 'WHEN_TO_START': 'NOT_APPLICABLE',
      'DEADLINE': 'NOT_APPLICABLE', 'DEPENDENCY': 'MARKET_DEVELOPMENT',
      'NEXT_TRIGGER': 'autorizacao'},
    'MARKETING': {'ACTION_STATE': 'WATCH_TRIGGER', 'ACTION': 'nenhuma',
      'WHY': 'idem', 'WHEN_TO_START': 'NOT_APPLICABLE', 'DEADLINE': 'NOT_APPLICABLE',
      'DEPENDENCY': 'MARKET_DEVELOPMENT', 'NEXT_TRIGGER': 'autorizacao'},
    'SUPPLY': {'ACTION_STATE': 'WATCH_TRIGGER', 'ACTION': 'nenhuma',
      'WHY': 'idem', 'WHEN_TO_START': 'NOT_APPLICABLE', 'DEADLINE': 'NOT_APPLICABLE',
      'DEPENDENCY': 'MARKET_DEVELOPMENT', 'NEXT_TRIGGER': 'autorizacao'},
  },
  'MISSING_FIELDS': {
    'DEROGATION_GRANTED': 'NOT_IN_SOURCE — a fala diz que foi PEDIDA, nao que foi '
                          'concedida',
    'MOLECULES_UNDER_DEROGATION': 'NOT_IN_SOURCE',
    'ADAMA_LOCAL_RESPONSE': 'NOT_APPLICABLE — nao ha par no conjunto publicado',
  },
 },

 # ═══════════════════════════════════════════════════════════════════════════
 {
  'ID': 'ITF-007',
  'FUTURE_SIGNAL': 'A alternariose da batata consome deroga: em 2024 foi concedida '
                   'na Emilia-Romagna uma deroga para UM tratamento a mais a base '
                   'de difenoconazol, e a alternaria perdeu o dimetomorf.',
  'FUTURE_SIGNAL_TYPE': 'TETO_DE_TRATAMENTO_COM_MOLECULA_DO_PORTFOLIO',
  'EVIDENCE_TIME_STATE': 'OBSERVED_NOW',
  'EVIDENCE_TIME_WHY': 'a deroga de 2024 foi concedida — fato. O elemento futuro e '
                       'a recorrencia esperada, que a fonte NAO promete. Por isso '
                       'OBSERVED_NOW, e nao EXPECTED: nao invento a repeticao.',
  'SOURCE_ID': 'dGmP236Z4uQ', 'SOURCE_TYPE': 'CONVEGNO_BILANCIO_FITOSANITARIO',
  'SOURCE_DATE': '2025-10-20',
  'SOURCE_TITLE': 'Il bilancio fitosanitario 2024/2025 di pomodoro e patata',
  'QUOTE_IT': 'Le molecole chiave sono il difenoconazolo e l\'azoxystrobin (...) '
              'per l\'alternaria nel 2024 e stata concessa una deroga, anche in '
              'Emilia-Romagna e stata richiesta e concessa questa deroga per un '
              'incremento di un trattamento a base di difenoconazolo. Anche '
              'l\'alternaria ha visto perdere il dimetomorf',
  'COUNTRY': 'IT', 'REGION': 'Emilia-Romagna',
  'REGION_WHY': 'nomeada na fala', 'CROP': 'PATATA', 'TARGET': 'ALTERNARIA',
  'TARGET_IN_CONTROLLED_VOCAB': True,
  'EXPECTED_START': '2026-06', 'EXPECTED_END': '2026-08',
  'TIME_HORIZON_DAYS': 270, 'HORIZON_BUCKET': 'HORIZON_181_365_DAYS',
  'TRIGGER': 'pedido de deroga da campanha 2026, se houver',
  'INVALIDATION_TRIGGER': 'revisao do disciplinare que aumente o numero ordinario '
                          'de tratamentos',
  'WINDOW_EXPECTED': 'YES',
  'EXPECTED_WINDOW_START': '2026-06', 'EXPECTED_WINDOW_END': '2026-08',
  'WINDOW_TRIGGER': 'da chiusura dell\'interfila ate a colheita — declarado na fala',
  'WINDOW_SOURCE': 'estadio declarado pelo relator',
  'WINDOW_IS_CALENDAR_BASED': 'NO', 'WINDOW_DEPENDS_ON_FIELD_MEASUREMENT': 'YES',
  'CONFIDENCE': 'HIGH',
  'CONFIDENCE_WHY': 'servico fitossanitario regional descrevendo deroga que a '
                    'propria regiao concedeu, com as moleculas nomeadas.',
  'ADAMA_LOCAL_RESPONSE': 'NO',
  'PORTFOLIO_MATCHES': [],
  'PRIMARY_MATCH': None, 'PRIMARY_MATCH_REASON': 'NENHUM_PRODUTO_NO_PAR',
  'PORTFOLIO_RELATION_ONLY': [
    {'REGISTRATION_ID': '009757', 'PRODUCT': 'SPYRALE',
     'ACTIVE_INGREDIENTS': ['DIFENOCONAZOLE', 'FENPROPIDIN'],
     'AUTHORISED_FOR': 'BARBABIETOLA x CERCOSPORA e OIDIO'},
    {'REGISTRATION_ID': '017955', 'PRODUCT': 'MAGANIC',
     'ACTIVE_INGREDIENTS': ['DIFENOCONAZOLE', 'PROTHIOCONAZOLE'],
     'AUTHORISED_FOR': 'cereais'},
  ],
  'WHY_ADAMA': 'ESTE E O CASO MAIS LIMPO DA DISTINCAO QUE ESTA CASA DEFENDE. A '
               'molecula da deroga e o difenoconazol, e a ADAMA TEM difenoconazol '
               'em dois rotulos italianos. Mas PATATA x ALTERNARIA nao aparece em '
               'nenhum dos 2.313 pares publicados: os dois rotulos autorizam '
               'beterraba e cereais.\n'
               '    PORTFOLIO RELATION != LABEL AUTHORIZATION.\n'
               'Ter a molecula nao e ter a autorizacao, e a distancia entre as duas '
               'coisas e exatamente o trabalho de Desenvolvimento de Mercado.',
  'WHY_FUTURE': 'a campanha 2026 da batata e o eventual pedido de deroga ainda nao '
                'aconteceram',
  'WHY_COMMERCIAL': 'NAO E OFERTA. E uma pergunta regulatoria com dono: vale a pena '
                    'pedir extensao de uso do difenoconazol para batata na Italia?',
  'DECISION_STILL_OPEN': 'YES', 'DECISION_DEADLINE': 'UNKNOWN',
  'LEAD_TIME_AVAILABLE': 'UNKNOWN — depende do rito regulatorio, que nenhuma fonte '
                         'do acervo descreve',
  'FUTURE_INTELLIGENCE_STATE': 'COMPLETE',
  'ACTION_MAP': {
    'MARKET_DEVELOPMENT': {
      'ACTION_STATE': 'MARKET_DEVELOPMENT_VALIDATE',
      'ACTION': 'avaliar extensao de uso do difenoconazol para batata x alternaria '
                'na Italia',
      'WHY': 'a molecula e nossa, o alvo consome deroga, e a autorizacao nao existe',
      'WHEN_TO_START': 'imediatamente', 'DEADLINE': '2026-06',
      'DEPENDENCY': 'regulatorio', 'NEXT_TRIGGER': 'campanha 2026'},
    'TECHNICAL_SCIENTIFIC': {
      'ACTION_STATE': 'PREPARE_NOW',
      'ACTION': 'reunir a base de eficacia de difenoconazol sobre Alternaria solani '
                'disponivel no grupo',
      'WHY': 'e o dossie que sustenta o pedido',
      'WHEN_TO_START': 'imediatamente', 'DEADLINE': '2026-04',
      'DEPENDENCY': 'arquivo tecnico', 'NEXT_TRIGGER': 'decisao regulatoria'},
    'COMMERCIAL': {'ACTION_STATE': 'WATCH_TRIGGER',
      'ACTION': 'nenhuma venda — nao ha autorizacao',
      'WHY': 'vender fora do rotulo nao se faz', 'WHEN_TO_START': 'NOT_APPLICABLE',
      'DEADLINE': 'NOT_APPLICABLE', 'DEPENDENCY': 'autorizacao',
      'NEXT_TRIGGER': 'autorizacao publicada'},
    'MARKETING': {'ACTION_STATE': 'WATCH_TRIGGER', 'ACTION': 'nenhuma',
      'WHY': 'idem', 'WHEN_TO_START': 'NOT_APPLICABLE', 'DEADLINE': 'NOT_APPLICABLE',
      'DEPENDENCY': 'autorizacao', 'NEXT_TRIGGER': 'autorizacao'},
    'SUPPLY': {'ACTION_STATE': 'WATCH_TRIGGER', 'ACTION': 'nenhuma',
      'WHY': 'idem', 'WHEN_TO_START': 'NOT_APPLICABLE', 'DEADLINE': 'NOT_APPLICABLE',
      'DEPENDENCY': 'autorizacao', 'NEXT_TRIGGER': 'autorizacao'},
  },
  'MISSING_FIELDS': {
    'REGULATORY_PATHWAY': 'NEEDS_EXTERNAL_SOURCE — nenhuma fonte do acervo descreve '
                          'o rito de extensao de uso italiano',
    'DECISION_DEADLINE': 'NOT_IN_SOURCE',
  },
 },

 # ═══════════════════════════════════════════════════════════════════════════
 {
  'ID': 'ITF-008',
  'FUTURE_SIGNAL': 'O lancamento do parasitoide Trissolcus japonicus (vespa samurai) '
                   'contra a cimice asiatica se estende a Marche e Toscana, e as '
                   'capturas em armadilha vem caindo desde cerca de 2020 no Veneto e '
                   'no Friuli.',
  'FUTURE_SIGNAL_TYPE': 'SINAL_NEGATIVO_REDUCAO_ESPERADA_DE_DEMANDA',
  'EVIDENCE_TIME_STATE': 'OBSERVED_NOW',
  'EVIDENCE_TIME_WHY': 'o programa de lancamento existe e as capturas caem — as duas '
                       'coisas sao observadas. A CONSEQUENCIA sobre a demanda futura '
                       'de inseticida e inferencia minha, e por isso ela vai marcada '
                       'como HYPOTHESIS no campo proprio, e nao como o estado do sinal.',
  'DERIVED_CLAIM_TIME_STATE': 'HYPOTHESIS',
  'SOURCE_ID': 'uf5bx-oTees', 'SOURCE_TYPE': 'CONVEGNO_BILANCIO_FITOSANITARIO',
  'SOURCE_DATE': '2025-12-05',
  'SOURCE_TITLE': 'Il bilancio fitosanitario 2024/2025 delle pomacee — sessione insetti',
  'CORROBORATING_SOURCES': [
    {'SOURCE_ID': 'mIunZ-pH3RY', 'SOURCE_DATE': '2025-11-07',
     'QUOTE_IT': 'il lancio di Vespa Samurai del Trissolcus per quello che riguarda '
                 'la cimice asiatica'},
    {'SOURCE_ID': '-4lUyIORl4A', 'SOURCE_DATE': '2025-12-11',
     'QUOTE_IT': 'anche con le Marche siamo due regioni che siamo nel progetto del '
                 'lancio del Trissolcus'},
  ],
  'QUOTE_IT': 'una diminuzione della presenza delle catture delle cimici nelle '
              'trappole a partire dal 2020 circa (...) leggera diminuzione fino '
              'appunto al 2025',
  'COUNTRY': 'IT', 'REGION': 'Veneto, Friuli, Marche, Toscana, Emilia-Romagna',
  'REGION_WHY': 'cada regiao e nomeada por um relator diferente; nenhuma foi herdada',
  'CROP': 'MELO, PERO', 'TARGET': 'CIMICI', 'TARGET_IN_CONTROLLED_VOCAB': True,
  'EXPECTED_START': '2026-05', 'EXPECTED_END': '2026-09',
  'TIME_HORIZON_DAYS': 240, 'HORIZON_BUCKET': 'HORIZON_181_365_DAYS',
  'TRIGGER': 'serie de capturas de 2026 nas armadilhas das regioes com lancamento',
  'INVALIDATION_TRIGGER': 'repique de capturas em 2026 — a queda nao e monotona e a '
                          'propria fonte a chama de "leggera"',
  'WINDOW_EXPECTED': 'UNKNOWN',
  'EXPECTED_WINDOW_START': 'UNKNOWN', 'EXPECTED_WINDOW_END': 'UNKNOWN',
  'WINDOW_TRIGGER': 'UNKNOWN', 'WINDOW_SOURCE': 'NOT_IN_SOURCE',
  'WINDOW_IS_CALENDAR_BASED': 'UNKNOWN',
  'WINDOW_DEPENDS_ON_FIELD_MEASUREMENT': 'YES',
  'CONFIDENCE': 'MEDIUM',
  'CONFIDENCE_WHY': 'tres fontes independentes confirmam o programa de lancamento; a '
                    'serie de capturas vem de uma so e e descrita como "leggera '
                    'diminuzione". Atribuir a queda ao parasitoide seria causalidade '
                    'que nenhuma fonte afirma.',
  'ADAMA_LOCAL_RESPONSE': 'YES',
  'PORTFOLIO_MATCHES': [
    {'REGISTRATION_ID': '007555', 'PRODUCT': 'KLARTAN 20 EW',
     'ACTIVE_INGREDIENTS': ['TAU-FLUVALINATE'], 'PAIR': 'MELO/PERO x CIMICI'},
    {'REGISTRATION_ID': '009800', 'PRODUCT': 'MAVRIK SMART',
     'ACTIVE_INGREDIENTS': ['TAU-FLUVALINATE'], 'PAIR': 'MELO/PERO x CIMICI'},
  ],
  'PRIMARY_MATCH': None, 'PRIMARY_MATCH_REASON': 'SEM_REGRA_DEFENSAVEL_PARA_ESCOLHER',
  'WHY_ADAMA': 'a ADAMA tem autorizacao para cimici em pomacee. O valor deste sinal '
               'e o AVESSO do habitual: ele sugere que a demanda quimica para este '
               'alvo pode encolher onde o parasitoide se estabelecer.',
  'WHY_FUTURE': 'a serie de 2026 ainda nao existe',
  'WHY_COMMERCIAL': 'INTELIGENCIA NEGATIVA. Serve para NAO superdimensionar a '
                    'previsao de cimice nas regioes com lancamento. Um radar que so '
                    'sabe crescer nao e um radar.',
  'DECISION_STILL_OPEN': 'YES', 'DECISION_DEADLINE': '2026-04',
  'LEAD_TIME_AVAILABLE': 'cerca de 4 meses ate o planejamento de temporada',
  'FUTURE_INTELLIGENCE_STATE': 'PARTIAL',
  'WHY_PARTIAL': 'sem janela declarada e sem quantificacao da queda. O sinal e '
                 'suficiente para moderar previsao, e insuficiente para dimensionar.',
  'ACTION_MAP': {
    'SUPPLY': {
      'ACTION_STATE': 'SUPPLY_PREPARE',
      'ACTION': 'nao aumentar a projecao de inseticida para cimice em Veneto e '
                'Friuli sem a serie de capturas de 2026',
      'WHY': 'a serie disponivel cai desde 2020; projetar crescimento contrariaria '
             'a unica evidencia que existe',
      'WHEN_TO_START': '2026-01', 'DEADLINE': '2026-04',
      'DEPENDENCY': 'serie de armadilhas 2026', 'NEXT_TRIGGER': 'publicacao da serie'},
    'MARKET_DEVELOPMENT': {
      'ACTION_STATE': 'WATCH_TRIGGER',
      'ACTION': 'acompanhar o projeto Trissolcus nas cinco regioes citadas',
      'WHY': 'e o fator que pode mudar a demanda deste alvo por varios anos',
      'WHEN_TO_START': '2026-01', 'DEADLINE': 'UNKNOWN',
      'DEPENDENCY': 'relatorio do projeto', 'NEXT_TRIGGER': 'proximo bilancio'},
    'COMMERCIAL': {'ACTION_STATE': 'WATCH_TRIGGER',
      'ACTION': 'nao construir campanha de cimice sobre expectativa de alta',
      'WHY': 'a evidencia disponivel aponta para baixa',
      'WHEN_TO_START': '2026-01', 'DEADLINE': '2026-04',
      'DEPENDENCY': 'SUPPLY', 'NEXT_TRIGGER': 'serie 2026'},
    'MARKETING': {'ACTION_STATE': 'WATCH_TRIGGER', 'ACTION': 'nenhuma',
      'WHY': 'nao ha mensagem util numa reducao de pressao',
      'WHEN_TO_START': 'NOT_APPLICABLE', 'DEADLINE': 'NOT_APPLICABLE',
      'DEPENDENCY': '-', 'NEXT_TRIGGER': '-'},
    'TECHNICAL_SCIENTIFIC': {'ACTION_STATE': 'WATCH_TRIGGER',
      'ACTION': 'verificar seletividade do tau-fluvalinato sobre Trissolcus',
      'WHY': 'se o nosso produto prejudica o parasitoide que a regiao esta '
             'soltando, isso e informacao que precisamos saber ANTES de recomendar',
      'WHEN_TO_START': 'imediatamente', 'DEADLINE': '2026-04',
      'DEPENDENCY': 'literatura de seletividade',
      'NEXT_TRIGGER': 'resposta da revisao'},
  },
  'MISSING_FIELDS': {
    'CAPTURE_SERIES_NUMBERS': 'NOT_EXTRACTED — a fala mostra grafico; a ASR nao '
                              'carrega os valores',
    'WINDOW': 'NOT_IN_SOURCE',
    'CAUSALITY_PARASITOID_TO_DECLINE': 'NOT_IN_SOURCE — nenhuma fonte a afirma, e '
                                       'eu nao a afirmo',
  },
 },

 # ═══════════════════════════════════════════════════════════════════════════
 {
  'ID': 'ITF-009',
  'FUTURE_SIGNAL': 'Lobesia botrana (tignoletta) teve em 2025 um incremento nitido '
                   'em TODO o territorio do norte, com presencas importantes em '
                   'areas onde o inseto NUNCA tinha sido observado. Barbera e '
                   'Moscato foram as castas mais atingidas.',
  'FUTURE_SIGNAL_TYPE': 'EXPANSAO_GEOGRAFICA_DE_PRAGA',
  'EVIDENCE_TIME_STATE': 'OBSERVED_NOW',
  'EVIDENCE_TIME_WHY': 'a expansao de 2025 e observada e descrita com detalhe. O '
                       'que e futuro e a campanha de 2026 nas areas recem-invadidas, '
                       'onde nao ha historico nem confusao sexual instalada. Nao '
                       'escrevo FORECAST: a fonte nao projeta 2026.',
  'SOURCE_ID': 'VE8gaWinRmY', 'SOURCE_TYPE': 'CONVEGNO_BILANCIO_FITOSANITARIO',
  'SOURCE_DATE': '2025-11-15',
  'SOURCE_TITLE': 'Il bilancio fitosanitario 2024/2025 della vite nel nord Italia — '
                  'sessione insetti',
  'QUOTE_IT': 'Nel 2025 invece e cambiata la situazione e si e avuto un netto '
              'incremento della presenza di Lobesia su tutto il territorio con '
              'segnalazioni, presenze anche importanti in aree dove l\'insetto non '
              'era mai stato osservato in passato. I vitigni piu colpiti sono '
              'risultati Barbera e Moscato',
  'COUNTRY': 'IT', 'REGION': 'Nord Italia (Barbera e Moscato indicam Piemonte)',
  'REGION_WHY': 'o titulo declara "nord Italia"; as castas nomeadas sao piemontesas. '
                'A regiao precisa NAO e declarada e por isso vai qualificada.',
  'CROP': 'VITE', 'TARGET': 'TIGNOLE', 'TARGET_IN_CONTROLLED_VOCAB': True,
  'EXPECTED_START': '2026-05', 'EXPECTED_END': '2026-08',
  'TIME_HORIZON_DAYS': 180, 'HORIZON_BUCKET': 'HORIZON_181_365_DAYS',
  'TRIGGER': 'primeiro voo de adultos em meados de maio de 2026 nas areas novas',
  'INVALIDATION_TRIGGER': 'capturas de 2026 voltando aos niveis anteriores a 2025',
  'WINDOW_EXPECTED': 'YES',
  'EXPECTED_WINDOW_START': '2026-05', 'EXPECTED_WINDOW_END': '2026-07',
  'WINDOW_TRIGGER': 'primeiro voo em meados de maio; armadilhas de feromonio a '
                    'partir da segunda semana de junho para a segunda geracao — '
                    'ambas as datas ditas na fonte',
  'WINDOW_SOURCE': 'declarado com precisao pelo relator',
  'WINDOW_IS_CALENDAR_BASED': 'NO',
  'WINDOW_DEPENDS_ON_FIELD_MEASUREMENT': 'YES',
  'CONFIDENCE': 'HIGH',
  'CONFIDENCE_WHY': 'balanco oficial regional, com fenologia datada, castas nomeadas '
                    'e a distincao explicita entre areas historicas e areas novas.',
  'ADAMA_LOCAL_RESPONSE': 'YES',
  'PORTFOLIO_MATCHES': [
    {'REGISTRATION_ID': '012573', 'PRODUCT': 'EKO OIL SPRAY',
     'ACTIVE_INGREDIENTS': ['PARAFFIN OIL'], 'PAIR_SOURCE': 'IT-ROTULOS-PARES-V3'},
    {'REGISTRATION_ID': '014386', 'PRODUCT': 'OLIONET',
     'ACTIVE_INGREDIENTS': ['PARAFFIN OIL'], 'PAIR_SOURCE': 'IT-ROTULOS-PARES-V3'},
    {'REGISTRATION_ID': '008259', 'PRODUCT': 'LAMDEX EXTRA',
     'ACTIVE_INGREDIENTS': ['LAMBDA-CYHALOTHRIN'],
     'PAIR_SOURCE': 'CONJUNTO ANTIGO (productRelationships.json) — o parser novo NAO '
                    'le este par, porque 008259 e uma matriz de 393 blocos que o '
                    'gabarito excluiu. Entra pela UNIAO, e nao por leitura nova.'},
  ],
  'PRIMARY_MATCH': None,
  'PRIMARY_MATCH_REASON': 'SEM_REGRA_DEFENSAVEL_PARA_ESCOLHER',
  'WHY_ADAMA': 'ESTE E O CASO QUE JUSTIFICA A UNIAO DA FASE 4. O sinal de campo mais '
               'acionavel do acervo cai exatamente sobre o par que o parser novo le '
               'pior. Se o conjunto de 2.313 tivesse SUBSTITUIDO o antigo, '
               'OPP_169BD86DB324 e OPP_3C8C3960CC66 (tignoletta x videira) ficariam '
               'com zero produto no momento em que o campo declara expansao. A '
               'divida de recall tem endereco: 008259, 013560 e os outros rotulos-'
               'matriz.',
  'WHY_FUTURE': 'as areas recem-invadidas entram em 2026 sem confusao sexual '
                'instalada e sem historico de monitoramento',
  'WHY_COMMERCIAL': 'area nova, sem estrategia estabelecida, com janela declarada. '
                    'NAO prova demanda: prova que a decisao de manejo dessas areas '
                    'ainda nao foi tomada.',
  'DECISION_STILL_OPEN': 'YES', 'DECISION_DEADLINE': '2026-04',
  'LEAD_TIME_AVAILABLE': 'cerca de 5 meses ate o primeiro voo',
  'FUTURE_INTELLIGENCE_STATE': 'COMPLETE',
  'ACTION_MAP': {
    'MARKET_DEVELOPMENT': {
      'ACTION_STATE': 'VALIDATE_BEFORE_WINDOW',
      'ACTION': 'identificar os areais novos citados e montar monitoramento proprio '
                'antes do primeiro voo de maio',
      'WHY': 'em area sem historico nao ha curva de referencia; quem medir primeiro '
             'define a recomendacao',
      'WHEN_TO_START': '2026-02', 'DEADLINE': '2026-04',
      'DEPENDENCY': 'lista dos areais — a fonte diz "aree nuove" sem nomear',
      'NEXT_TRIGGER': 'primeiro voo'},
    'TECHNICAL_SCIENTIFIC': {
      'ACTION_STATE': 'PREPARE_NOW',
      'ACTION': 'fechar a divida de leitura dos rotulos-matriz (008259, 013560, '
                '013590, 015275, 017687, 018067, 019095) para saber o que a ADAMA '
                'realmente autoriza em VITE x TIGNOLE',
      'WHY': 'hoje o conjunto novo enxerga so oleo de parafina neste par, e isso e '
             'buraco de parser, nao realidade regulatoria',
      'WHEN_TO_START': 'imediatamente', 'DEADLINE': '2026-03',
      'DEPENDENCY': 'parser de tabela-matriz', 'NEXT_TRIGGER': 'gabarito ampliado'},
    'COMMERCIAL': {
      'ACTION_STATE': 'COMMERCIAL_PREPARE',
      'ACTION': 'preparar abordagem para as areas novas do Piemonte antes de abril',
      'WHY': 'a janela de decisao antecede o primeiro voo',
      'WHEN_TO_START': '2026-02', 'DEADLINE': '2026-04',
      'DEPENDENCY': 'canal — HOJE INEXISTENTE no acervo',
      'NEXT_TRIGGER': 'lista de areais'},
    'MARKETING': {
      'ACTION_STATE': 'MARKETING_PREPARE',
      'ACTION': 'material de monitoramento de Lobesia para viticultor sem historico '
                'da praga',
      'WHY': 'o publico novo nao conhece a fenologia do inseto',
      'WHEN_TO_START': '2026-02', 'DEADLINE': '2026-04',
      'DEPENDENCY': 'TECHNICAL_SCIENTIFIC', 'NEXT_TRIGGER': 'validacao'},
    'SUPPLY': {
      'ACTION_STATE': 'SUPPLY_PREPARE',
      'ACTION': 'rever cobertura para a janela maio-julho no noroeste',
      'WHY': 'expansao territorial declarada aumenta a area potencial tratada',
      'WHEN_TO_START': '2026-03', 'DEADLINE': '2026-04',
      'DEPENDENCY': 'previsao comercial', 'NEXT_TRIGGER': 'plano fechado'},
  },
  'MISSING_FIELDS': {
    'NEW_AREAS_NAMED': 'NOT_IN_SOURCE — a fala diz "aree dove non era mai stato '
                       'osservato" sem nomea-las',
    'CHANNEL': 'NOT_COLLECTED',
  },
 },

 # ═══════════════════════════════════════════════════════════════════════════
 {
  'ID': 'ITF-010',
  'FUTURE_SIGNAL': 'Os acaros tetraniquideos, sobretudo o ragnetto giallo, sobem de '
                   'forma lenta e constante na vite do norte desde cerca de 2014. Em '
                   '2025 as populacoes de fitoseideos estavam mais altas e nao se '
                   'observou efeito dos inseticidas de fim de junho contra '
                   'Scaphoideus titanus.',
  'FUTURE_SIGNAL_TYPE': 'TENDENCIA_DE_DECADA',
  'EVIDENCE_TIME_STATE': 'OBSERVED_NOW',
  'EVIDENCE_TIME_WHY': 'e uma serie observada de dez anos. TENDENCIA NAO VIRA '
                       'PREVISAO: a fonte descreve a subida passada e nao projeta '
                       '2026. Marcar FORECAST aqui seria exatamente o erro que a '
                       'missao proibe.',
  'SOURCE_ID': 'VE8gaWinRmY', 'SOURCE_TYPE': 'CONVEGNO_BILANCIO_FITOSANITARIO',
  'SOURCE_DATE': '2025-11-15',
  'SOURCE_TITLE': 'Il bilancio fitosanitario 2024/2025 della vite nel nord Italia — '
                  'sessione insetti',
  'QUOTE_IT': 'una problematica piu emergente (...) in questi ultimi 10 anni e la '
              'questione acari tetranichidi, quindi soprattutto ragnetto giallo che '
              'ha aumentato in maniera lenta ma costante dal 2014 circa (...) '
              'quest\'anno abbiamo trovato mediamente delle popolazioni di fitoseidi '
              'piu alte rispetto all\'anno scorso',
  'COUNTRY': 'IT', 'REGION': 'Nord Italia',
  'REGION_WHY': 'declarado no titulo da sessao; nenhuma regiao especifica e nomeada',
  'CROP': 'VITE', 'TARGET': 'ACARI', 'TARGET_IN_CONTROLLED_VOCAB': True,
  'EXPECTED_START': '2026-06', 'EXPECTED_END': '2026-08',
  'TIME_HORIZON_DAYS': 270, 'HORIZON_BUCKET': 'HORIZON_181_365_DAYS',
  'TRIGGER': 'monitoramento de sintomas de 2026 confirmando ou nao a continuidade '
             'da subida',
  'INVALIDATION_TRIGGER': 'a propria fonte ja aponta o contrafator: fitoseideos em '
                          'alta e ausencia de efeito dos inseticidas de junho. Se o '
                          'equilibrio se mantiver, a subida pode parar sozinha.',
  'WINDOW_EXPECTED': 'UNKNOWN',
  'EXPECTED_WINDOW_START': 'UNKNOWN', 'EXPECTED_WINDOW_END': 'UNKNOWN',
  'WINDOW_TRIGGER': 'UNKNOWN', 'WINDOW_SOURCE': 'NOT_IN_SOURCE',
  'WINDOW_IS_CALENDAR_BASED': 'UNKNOWN',
  'WINDOW_DEPENDS_ON_FIELD_MEASUREMENT': 'YES',
  'CONFIDENCE': 'MEDIUM',
  'CONFIDENCE_WHY': 'serie longa e fonte oficial, mas sem numeros na transcricao e '
                    'com um contrafator declarado pelo proprio relator. Uma '
                    'tendencia de dez anos nao autoriza afirmar o proximo ano.',
  'ADAMA_LOCAL_RESPONSE': 'YES',
  'PORTFOLIO_MATCHES': [
    {'REGISTRATION_ID': '012573', 'PRODUCT': 'EKO OIL SPRAY',
     'ACTIVE_INGREDIENTS': ['PARAFFIN OIL'], 'PAIR_SOURCE': 'IT-ROTULOS-PARES-V3'},
    {'REGISTRATION_ID': '014386', 'PRODUCT': 'OLIONET',
     'ACTIVE_INGREDIENTS': ['PARAFFIN OIL'], 'PAIR_SOURCE': 'IT-ROTULOS-PARES-V3'},
  ],
  'PRIMARY_MATCH': None,
  'PRIMARY_MATCH_REASON': 'SEM_REGRA_DEFENSAVEL_PARA_ESCOLHER',
  'WHY_ADAMA': 'a ADAMA tem dois rotulos VITE x ACARI, ambos de oleo de parafina, '
               'que e compativel com a preservacao de fitoseideos que a fonte '
               'destaca. Isso e uma HIPOTESE tecnica minha, e nao um dado da fonte.',
  'WHY_FUTURE': 'a serie de 2026 ainda nao existe',
  'WHY_COMMERCIAL': 'tendencia de decada nao sustenta campanha. Sustenta observacao '
                    'e uma pergunta tecnica sobre seletividade.',
  'DECISION_STILL_OPEN': 'YES', 'DECISION_DEADLINE': 'UNKNOWN',
  'LEAD_TIME_AVAILABLE': 'UNKNOWN',
  'FUTURE_INTELLIGENCE_STATE': 'PARTIAL',
  'WHY_PARTIAL': 'sem janela declarada, sem numeros e com contrafator explicito. '
                 'Suficiente para observar, insuficiente para agir.',
  'ACTION_MAP': {
    'TECHNICAL_SCIENTIFIC': {
      'ACTION_STATE': 'WATCH_TRIGGER',
      'ACTION': 'acompanhar a serie de acaros e de fitoseideos do norte em 2026',
      'WHY': 'a subida e lenta e o contrafator e real; so a serie decide',
      'WHEN_TO_START': '2026-06', 'DEADLINE': 'UNKNOWN',
      'DEPENDENCY': 'proximo bilancio', 'NEXT_TRIGGER': 'publicacao 2026'},
    'MARKET_DEVELOPMENT': {
      'ACTION_STATE': 'WATCH_TRIGGER',
      'ACTION': 'nenhuma validacao antes de a serie confirmar',
      'WHY': 'validar sobre tendencia de decada gastaria parcela por nada',
      'WHEN_TO_START': 'NOT_APPLICABLE', 'DEADLINE': 'NOT_APPLICABLE',
      'DEPENDENCY': 'serie 2026', 'NEXT_TRIGGER': 'confirmacao'},
    'COMMERCIAL': {'ACTION_STATE': 'WATCH_TRIGGER', 'ACTION': 'nenhuma',
      'WHY': 'tendencia nao e janela', 'WHEN_TO_START': 'NOT_APPLICABLE',
      'DEADLINE': 'NOT_APPLICABLE', 'DEPENDENCY': 'serie', 'NEXT_TRIGGER': 'serie'},
    'MARKETING': {'ACTION_STATE': 'WATCH_TRIGGER', 'ACTION': 'nenhuma',
      'WHY': 'idem', 'WHEN_TO_START': 'NOT_APPLICABLE', 'DEADLINE': 'NOT_APPLICABLE',
      'DEPENDENCY': 'serie', 'NEXT_TRIGGER': 'serie'},
    'SUPPLY': {'ACTION_STATE': 'WATCH_TRIGGER', 'ACTION': 'nenhuma',
      'WHY': 'idem', 'WHEN_TO_START': 'NOT_APPLICABLE', 'DEADLINE': 'NOT_APPLICABLE',
      'DEPENDENCY': 'serie', 'NEXT_TRIGGER': 'serie'},
  },
  'MISSING_FIELDS': {
    'SERIES_NUMBERS': 'NOT_EXTRACTED — grafico em tela, ASR nao carrega os valores',
    'WINDOW': 'NOT_IN_SOURCE',
    'REGION_PRECISE': 'NOT_IN_SOURCE',
  },
 },
]
