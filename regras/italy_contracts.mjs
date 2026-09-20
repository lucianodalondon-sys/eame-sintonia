// CONTRATOS DE FONTE — ITALIA V1
//
// Um contrato responde, de forma executavel:
//   quem e · onde esta · como encontro · o que espero receber · como sei que e o
//   documento certo · qual a identidade · qual a data · como sei que mudou ·
//   qual a frequencia · o que preservo · como falha · o que a falha significa.
//
// LEIS QUE ESTE ARQUIVO CARREGA (cada uma tem guarda em italy_contract_test.mjs):
//   HTTP_200                 != HEALTHY_SOURCE
//   EMPTY_LIST               != ZERO_DOCUMENTS      (lista vazia FALHA fechada)
//   SAME_URL                 != SAME_DOCUMENT       (hash novo = observacao nova)
//   DOCUMENT_ID              != BYTE_ID             (identidade semantica != SHA)
//   DECLARED_FREQUENCY       != OBSERVED_FREQUENCY
//   ACCESS_CLASSIFICATION    != ANALYTIC_VERDICT
//   SOURCE_VERDICT           != SOURCE_HEALTH
//   AGROCLIMATIC_SIGNAL      != PEST_OCCURRENCE
//   COMPANY_CLAIM            != REGULATORY_FACT
//   BROWSER_RENDERED_EXTRACT != RAW_PRESERVED
//   SAME_HASH                != DEGRADED            (corrigida em 2026-09-07, ver abaixo)
//   NO_CHANGE                != FAILURE
//   CAPTURE                  != DOCUMENT
//   NEW_HASH                 != NEW_SEMANTIC_FACT
//   MOVING_WINDOW            != NEW_DATASET_EVERY_DAY
//   FIRST_RUN                =  BASELINE
//
// CORRECAO DE LEI — 2026-09-07:
//   Eu havia escrito "hash repetido = DEGRADED / fonte parada". ERRADO e perigoso.
//   Uma fonte semanal consultada duas vezes no mesmo dia DEVE devolver o mesmo documento.
//   Atraso so existe com: EXPECTED_UPDATE + DEADLINE PROVADA + DEADLINE VENCIDA + SEM NOVA VERSAO.
//   Estados corretos: NO_CHANGE · EXPECTED_NO_CHANGE · UPDATE_DUE · OVERDUE_UPDATE · CADENCE_UNKNOWN

export const ROUTE_TYPES = ["STATIC_ROUTE", "PREDICTABLE_ROUTE", "DISCOVERED_ROUTE", "APPLICATION_ROUTE", "BROWSER_DISCOVERED_ROUTE"];
export const HEALTH_STATES = ["HEALTHY", "DEGRADED", "FAILED", "UNKNOWN"];

export const CONTRACTS = {

  "IT-T3-002": {
    OWNER_ID: "IT-OWN-007", OWNER: "Regione Campania — Servizio Fitosanitario Regionale",
    TERRITORY: "T3", VALUE: "P0",
    CANONICAL_ENTRY_URL: "https://agricoltura.regione.campania.it/difesa/bollettini/bollettini_<ANO>.html",
    DISCOVERY_METHOD: "abrir a pagina do ano; ela lista uma sub-pagina por provincia (AV, BN, CE, NA, SA); cada uma lista os PDFs",
    RETRIEVAL_METHOD: "GET direto no PDF",
    ROUTE_TYPE: "PREDICTABLE_ROUTE",
    ROUTE_TEMPLATE: "https://agricoltura.regione.campania.it/difesa/bollettini/bollettini_{ANO}/pdf/{PROV}-{DD}-{MM}.pdf",
    ROUTE_VARS: { ANO: "2026", PROV: ["AV", "BN", "CE", "NA", "SA"], DD: "dia com 2 digitos", MM: "mes com 2 digitos" },
    ACCESS_INSTRUMENT: "HTTP", AUTH_REQUIRED: false, BROWSER_REQUIRED: false, JS_REQUIRED: false,
    OUTPUT_TYPE: "PDF", EXPECTED_MIME: /^application\/pdf/, EXPECTED_SIGNATURE: "%PDF",
    MIN_BYTES: 100000,
    IDENTITY_KEYS: ["provincia", "data_do_boletim"],
    DOCUMENT_ID_RULE: "CAMPANIA:{PROV}:{DD-MM-ANO}",
    DOCUMENT_DATE_FIELD: "a data esta no NOME do arquivo (DD-MM); o ano vem do caminho",
    VERSION_FIELD: "nao ha versao explicita; uma data = uma edicao",
    EXPECTED_CONTENT_MARKERS: ["Monitoraggio", "Chimico", "Soglia"],
    EXPECTED_STRUCTURE: "blocos por avversita com Agronomico / Chimico / Soglia e substancia ativa nomeada",
    DECLARED_FREQUENCY: "o proprio site declara: semanal de 1 marco a 30 setembro (olivo ate fim de outubro), mensal fora disso",
    OBSERVED_FREQUENCY: "7D — provado por 14 edicoes de SA em 2026 espacadas exatamente 7 dias",
    UPDATE_BEHAVIOR: "ADITIVO — cada edicao ganha arquivo proprio, a anterior permanece",
    HISTORICAL_OR_FORWARD: "HISTORICAL", ARCHIVE_REQUIREMENT: "NORMAL",
    EXPECTED_FAILURES: ["404 numa data sem edicao (esperado, nao e falha da fonte)", "HTML no lugar de PDF = FAILED", "PDF abaixo de 100 KB = suspeito"],
    FAIL_CLOSED_RULE: "se o corpo nao comecar com %PDF, e FAILED — nunca registrar como boletim",
    FALLBACK: "voltar a pagina do ano e reler a lista da provincia",
    SOURCE_LOCATION_RULE: "Napoli (sede da Regiao) — fixo",
    FACT_LOCATION_RULE: "a PROVINCIA do proprio arquivo. NUNCA a sede.",
    EVIDENCE_CLASS: "TECHNICAL_GUIDELINE + OBSERVED_FIELD_SIGNAL pontual (rotulo Presente/Non Presente)",
    AUTOMATION_FEASIBILITY: "HIGH",
    // ── O BLOCO EXECUTÁVEL (contrato v2 · cutover do `case`) ─────────────
    // Copiado do `case "IT-T3-002"` de `italy_pilot_collect.mjs` @ 380bf090,
    // medido e não reinterpretado: abrir o índice de SA do ano, apanhar os
    // href `SA-DD-MM.pdf` (relativos, resolvidos contra a pasta do ano) e
    // ficar com o primeiro. O `ROUTE_TEMPLATE` em prosa acima fala em 5
    // províncias; o `case` só colhia SA, e o bloco executável diz a MESMA
    // verdade. Alargar às cinco é decisão de owner, não efeito colateral de
    // uma migração.
    ACQUISITION: {
      STRATEGY: "HTML_LINK_DISCOVERY",
      INDEX_URL: "https://agricoltura.regione.campania.it/difesa/bollettini/bollettini_2026/SA_2026.html",
      BASE_URL: "https://agricoltura.regione.campania.it/difesa/bollettini/bollettini_2026/",
      LINK_PATTERN: 'href="([^"]*SA-\\d{2}-\\d{2}\\.pdf)"',
      MAX_TARGETS: 1,
    },
    // `FACT_TIME` continua UNKNOWN, palavra por palavra como o `case` dizia:
    // a data no nome é a da EDIÇÃO, não a da observação de campo.
    IDENTITY: {
      STRATEGY: "FILENAME_CAPTURE",
      PATTERN: "^([A-Z]{2})-(\\d{2})-(\\d{2})\\.pdf$",
      DOCUMENT_ID: "CAMPANIA:$1:$2-$3-2026",
      SOURCE_DATE: "$2/$3/2026",
      SOURCE_DATE_ISO: "2026-$3-$2",
      FACT_TIME: "UNKNOWN — o boletim nao data a observacao de campo",
    },
    NEGATIVE_CONTROL: { descricao: "pedir uma data que nao existe (SA-01-01.pdf)", esperado: "DOCUMENT_NOT_FOUND, nunca HTML tratado como boletim" }
  },

  "IT-T3-010": {
    OWNER_ID: "IT-OWN-012", OWNER: "A.P.OL. — Associazione tra Produttori Olivicoli, Lecce",
    TERRITORY: "T3", VALUE: "P0",
    CANONICAL_ENTRY_URL: "http://www.apol.it",
    aviso_de_esquema: "o site e HTTP, nao HTTPS. Tentar https:// nao resolve — foi o que escondeu esta fonte por uma rodada inteira.",
    DISCOVERY_METHOD: "a home lista os boletins com titulo, numero e periodo de validade",
    RETRIEVAL_METHOD: "GET direto no PDF",
    ROUTE_TYPE: "DISCOVERED_ROUTE",
    ROUTE_TEMPLATE: "http://www.apol.it/documenti/notizie/Bollettino_Mosca_dellOlivo_n_{N}_del_{DD}_{MM}_{AAAA}.pdf",
    aviso_de_rota: "o padrao de 2026 usa underscore (07_09_2026); o de 2025 usa hifen (20-10-2025). NAO adivinhar: descobrir no indice. Por isso ROUTE_TYPE = DISCOVERED, nao PREDICTABLE.",
    ACCESS_INSTRUMENT: "HTTP", AUTH_REQUIRED: false, BROWSER_REQUIRED: false, JS_REQUIRED: false,
    OUTPUT_TYPE: "PDF", EXPECTED_MIME: /^application\/pdf/, EXPECTED_SIGNATURE: "%PDF", MIN_BYTES: 300000,
    IDENTITY_KEYS: ["ano", "numero_da_edicao", "comprensorio"],
    DOCUMENT_ID_RULE: "APOL:{ANO}:N{NUMERO}:{COMPRENSORIO}",
    DOCUMENT_DATE_FIELD: "VALID_FROM e VALID_TO impressos no cabecalho: 'MOSCA DELLE OLIVE dd/mm/aaaa - dd/mm/aaaa'",
    VERSION_FIELD: "numero da edicao (n. 1..N por temporada)",
    EXPECTED_CONTENT_MARKERS: ["MOSCA DELLE OLIVE", "COMPRENSORIO"],
    EXPECTED_STRUCTURE: "cabecalho com periodo · comprensorio + lista de comuni · fase fenologica · capturas · % de infestacao · rotulo de tendencia · previsao diaria de 7 dias · texto tecnico com soglia",
    CAMPOS_A_EXTRAIR: ["ISSUE_NUMBER", "VALID_FROM", "VALID_TO", "COMPRENSORIO", "COMUNI", "PHENOLOGY", "TRAP_CAPTURES", "ACTIVE_INFESTATION_PERCENT", "TREND_LABEL", "TECHNICAL_RECOMMENDATION"],
    DECLARED_FREQUENCY: "o site nao declara cadencia em texto",
    OBSERVED_FREQUENCY: "7D — provado pelas DATAS dentro dos documentos preservados (VALID_FROM 31/08 e 07/09 = 7 dias exatos)",
    ressalva_da_cadencia: "so DOIS documentos foram preservados. A pagina lista 9 de 2026 e 14 de 2025, mas contar itens numa lista NAO e provar cadencia — a prova aqui vem do intervalo entre as datas impressas nos dois PDFs que temos.",
    UPDATE_BEHAVIOR: "ADITIVO", HISTORICAL_OR_FORWARD: "HISTORICAL", ARCHIVE_REQUIREMENT: "NORMAL",
    EXPECTED_FAILURES: ["indice vazio = FAILED (a home sempre lista boletins na temporada)", "HTTPS nao resolve — nao confundir com fonte fora do ar"],
    FAIL_CLOSED_RULE: "lista vazia no indice NAO e zero documentos: e FAILED",
    FALLBACK: "nenhum — fonte unica",
    SOURCE_LOCATION_RULE: "Lecce (sede) — fixo",
    FACT_LOCATION_RULE: "o COMPRENSORIO impresso no documento e os comuni listados. NUNCA a sede.",
    EVIDENCE_CLASS: "OBSERVED_FIELD_SIGNAL + COOPERATIVE_GUIDANCE",
    AUTOMATION_FEASIBILITY: "HIGH",
    // ── O BLOCO EXECUTÁVEL (contrato v2 · cutover do `case`) ─────────────
    // Copiado do `case "IT-T3-010"` @ 380bf090: a home lista os boletins; o
    // primeiro href `Bollettino_Mosca…pdf` é a edição corrente.
    ACQUISITION: {
      STRATEGY: "HTML_LINK_DISCOVERY",
      INDEX_URL: "http://www.apol.it",
      BASE_URL: "http://www.apol.it",
      LINK_PATTERN: 'href="([^"]*Bollettino_Mosca[^"]*\\.pdf)"',
      MAX_TARGETS: 1,
    },
    // A identidade vem de TRÊS sítios, como no `case`: o período impresso no
    // cabeçalho (texto do PDF), o número da edição (nome do ficheiro) e o
    // comprensorio (texto do PDF, opcional — o `case` punha "?" quando não
    // o lia). `PDF_TEXT` é o pdftotext que o coletor já tinha; não há um
    // segundo extractor.
    IDENTITY: {
      STRATEGY: "CONTENT_CAPTURE",
      CAPTURES: {
        periodo: { FROM: "PDF_TEXT", PATTERN: "MOSCA DELLE OLIVE\\s+((\\d{2})/(\\d{2})/(\\d{4}))\\s*-\\s*(\\d{2}/\\d{2}/\\d{4})" },
        numero: { FROM: "FILENAME", PATTERN: "_n_(\\d+)_" },
        comprensorio: { FROM: "PDF_TEXT", PATTERN: "COMPRENSORIO\\s*-?\\s*([A-Z]{2})\\s*-\\s*([A-Z ]+)", REQUIRED: false, DEFAULTS: ["?", "?"] },
      },
      DOCUMENT_ID: "APOL:{periodo.4}:N{numero.1}:{comprensorio.1}-{comprensorio.2}",
      SOURCE_DATE: "{periodo.1} a {periodo.5}",
      SOURCE_DATE_ISO: "{periodo.4}-{periodo.3}-{periodo.2}",
      FACT_TIME: "UNKNOWN — o periodo e de validade, nao de observacao",
    },
    NEGATIVE_CONTROL: { descricao: "indice sem nenhum link de boletim", esperado: "FAILED, nunca ZERO_DOCUMENTS" }
  },

  "IT-T3-008": {
    OWNER_ID: "IT-OWN-ARIF", OWNER: "ARIF Puglia — Agenzia regionale per le attivita irrigue e forestali",
    TERRITORY: "T3", VALUE: "P0",
    CANONICAL_ENTRY_URL: "https://www.agrometeopuglia.it/bollettini",
    OLD_ROUTE: "https://www.arifpuglia.it — DEAD (403 CloudFront, no curl E no navegador italiano)",
    CURRENT_ROUTE: "https://www.agrometeopuglia.it/bollettini — FOUND",
    DISCOVERY_METHOD: "a pagina lista o notiziario semanal corrente e o arquivo dos ultimos",
    RETRIEVAL_METHOD: "GET direto no PDF",
    ROUTE_TYPE: "PREDICTABLE_ROUTE",
    ROUTE_TEMPLATE: "https://www.agrometeopuglia.it/bollettino-elettronico/settimanale/{ANO}/Notiziario_Agrometeorologico_N{NN}_{DD-MM-AAAA}.pdf",
    ROTA_IRMA: "https://www.agrometeopuglia.it/bollettino-elettronico/quotidiano/{ANO}/Giornaliero_Meteorologico_N{NN}_{DD-MM-AAAA}.pdf — canal DIFERENTE (T2, so meteorologico). Nao misturar.",
    ACCESS_INSTRUMENT: "HTTP", AUTH_REQUIRED: false, BROWSER_REQUIRED: false, JS_REQUIRED: false,
    OUTPUT_TYPE: "PDF", EXPECTED_MIME: /^application\/pdf/, EXPECTED_SIGNATURE: "%PDF", MIN_BYTES: 1000000,
    IDENTITY_KEYS: ["ano", "numero_do_notiziario"],
    DOCUMENT_ID_RULE: "ARIF:SETTIMANALE:{ANO}:N{NUMERO}",
    DOCUMENT_DATE_FIELD: "no nome do arquivo E no cabecalho de cada pagina: 'n. 36 del 02 settembre 2026'",
    VERSION_FIELD: "numero sequencial + 'Anno XL' (ano da serie)",
    EXPECTED_CONTENT_MARKERS: ["Notiziario Agrometeorologico & Fitosanitario Regionale", "Situazione Fitosanitaria", "Programma di Difesa"],
    EXPECTED_STRUCTURE: "por cultura: Situazione Fenologica / Situazione Fitosanitaria / Programma di Difesa. 32 blocos de Situazione Fitosanitaria na edicao n.36.",
    LEITURA_RESOLVIDA_2026_09_07: "com pdftotext -layout a secao fitossanitaria le inteira: 32 blocos, 13 pragas com nome cientifico, soglie de 4-5%/5%/10%/20% e sostanze attive nomeadas (acetamiprid, flupyradifurone, deltametrina, spinosad, cyantraniliprole, pyriproxyfen, Bacillus thuringiensis).",
    LIMITE_CONHECIDO: "O NOME DA CULTURA E IMAGEM, nao texto. pdftotext le tudo menos o titulo da cultura. A cultura pode ser DERIVADA do nome cientifico da praga (mosca dell'olivo -> olivo; Plasmopara viticola -> vite), mas isso e DERIVACAO, nunca extracao. Marcar o campo como CROP_DERIVED, jamais como CROP_EXTRACTED.",
    DECLARED_FREQUENCY: "o site declara: semanal, com saida as quartas",
    OBSERVED_FREQUENCY: "7D — provado por 11 edicoes listadas (N26 24/06 ate N36 02/09) com espacamento exato de 7 dias",
    UPDATE_BEHAVIOR: "ADITIVO", HISTORICAL_OR_FORWARD: "HISTORICAL", ARCHIVE_REQUIREMENT: "NORMAL",
    EXPECTED_FAILURES: ["403 se alguem usar o dominio velho arifpuglia.it", "PDF abaixo de 1 MB e suspeito (as edicoes tem 2,7 MB)"],
    FAIL_CLOSED_RULE: "sem os tres marcadores de conteudo, e FAILED",
    FALLBACK: "reler a pagina /bollettini",
    SOURCE_LOCATION_RULE: "Bari (ARIF) — fixo",
    FACT_LOCATION_RULE: "Puglia regional; ha pontos de observacao citados no texto, ainda nao estruturados",
    EVIDENCE_CLASS: "OBSERVED_FIELD_SIGNAL + TECHNICAL_GUIDELINE (separar por bloco: 'Situazione Fitosanitaria' e OBSERVED, 'Programma di Difesa' e RECOMMENDED)",
    AUTOMATION_FEASIBILITY: "MEDIUM — rota e leitura sao faceis; o nome da cultura exige derivacao",
    // ── O BLOCO EXECUTÁVEL (contrato v2 · cutover do `case`) ─────────────
    // Copiado do `case "IT-T3-008"` @ 380bf090. O índice de /bollettini é
    // renderizado por JavaScript e o curl não vê os links (medido de novo em
    // 2026-09-20: HTTP 200, 25.993 bytes, 0 links). Isso NÃO é lista vazia
    // da fonte — é limite do nosso instrumento — e por isso há FALLBACK: a
    // rota previsível, sondada para trás a partir de hoje. O alvo que sai
    // daí carrega `descoberta_degradada`, e esse sinal é obrigatório: sem
    // ele, uma descoberta degradada ficaria igual a uma normal no ledger.
    //
    // ⚠️ ROTA CORRIGIDA COM PROVA (2026-09-20):
    //   OLD: NUMEROS = ENUM [37, 36, 35] — a lista fixa do `case`. Em
    //        2026-09-20 já não apanhava a edição corrente (N38 de 16/09),
    //        e a janela de 10 dias já não chegava à N37 (09/09).
    //   NEW: NUMEROS = ISO_WEEK — N35=26/08, N36=02/09, N37=09/09, N38=16/09:
    //        quatro de quatro edições coincidem com a semana ISO da data.
    //   PROOF: GET …/2026/Notiziario_Agrometeorologico_N38_16-09-2026.pdf →
    //        HTTP 200, application/pdf, 2.724.725 bytes, começa por %PDF.
    //   A equivalência com o `case` está provada com ENUM em
    //   `regras/cutover_equivalencia_test.mjs`; o contrato usa a regra provada.
    ACQUISITION: {
      STRATEGY: "HTML_LINK_DISCOVERY",
      INDEX_URL: "https://www.agrometeopuglia.it/bollettini",
      BASE_URL: "https://www.agrometeopuglia.it",
      LINK_PATTERN: 'href="([^"]*Notiziario_Agrometeorologico_N\\d+_[\\d-]+\\.pdf)"',
      MAX_TARGETS: 1,
      FALLBACK: {
        STRATEGY: "CUSTOM_ADAPTER", ADAPTER_ID: "SONDA_DE_ROTA_DATADA_V1",
        TEMPLATE: "https://www.agrometeopuglia.it/bollettino-elettronico/settimanale/{AAAA}/Notiziario_Agrometeorologico_N{N}_{DD}-{MM}-{AAAA}.pdf",
        DIAS_PARA_TRAS: 10,
        NUMEROS: { RULE: "ISO_WEEK", OFFSETS: [0, -1] },
        ACEITAR: { SIGNATURE: "%PDF", MIN_BYTES: 100000 },
        DEGRADED_REASON: "INDEX_REQUIRES_BROWSER — indice e JavaScript; caiu para a rota previsivel do contrato",
      },
    },
    IDENTITY: {
      STRATEGY: "FILENAME_CAPTURE",
      PATTERN: "_N(\\d+)_((\\d{2})-(\\d{2})-(\\d{4}))\\.pdf",
      DOCUMENT_ID: "ARIF:SETTIMANALE:$5:N$1",
      SOURCE_DATE: "$2",
      SOURCE_DATE_ISO: "$5-$4-$3",
      FACT_TIME: "UNKNOWN",
    },
    NEGATIVE_CONTROL: { descricao: "PDF que nao contenha 'Situazione Fitosanitaria'", esperado: "FAILED" }
  },

  "IT-T3-005": {
    OWNER_ID: "IT-OWN-008", OWNER: "Terre dell'Etruria — Societa Cooperativa Agricola",
    TERRITORY: "T3", VALUE: "P0",
    CANONICAL_ENTRY_URL: "https://www.terretruria.it/monitoraggio",
    DISCOVERY_METHOD: "rota unica e fixa", RETRIEVAL_METHOD: "GET",
    ROUTE_TYPE: "STATIC_ROUTE",
    ACCESS_INSTRUMENT: "HTTP", AUTH_REQUIRED: false, BROWSER_REQUIRED: false, JS_REQUIRED: false,
    OUTPUT_TYPE: "HTML", EXPECTED_MIME: /^text\/html/, EXPECTED_SIGNATURE: "<", MIN_BYTES: 200000,
    IDENTITY_KEYS: ["periodo_do_bollettino"],
    DOCUMENT_ID_RULE: "TERRETRURIA:{PERIODO_INICIO}:{PERIODO_FIM}",
    IDENTITY_KEYS_DO_PONTO: ["point_id", "lat", "lon", "sampling_date"],
    DOCUMENT_DATE_FIELD: "'Bollettino del periodo dal DD-MM-AAAA al DD-MM-AAAA' no corpo",
    VERSION_FIELD: "nao ha numero de edicao — so o periodo",
    EXPECTED_CONTENT_MARKERS: ["Bollettino del periodo", "Legenda infestazione", "reports_points"],
    EXPECTED_STRUCTURE: "139 blocos <div class=reports_points> com nome, lat, lon, data de campionamento, infestacao e rotulo",
    CAMPOS_POR_PONTO: ["MONITORING_POINT_ID", "LAT", "LON", "DATE", "CROP", "PHENOLOGY", "INFESTATION_PERCENT", "ALERT", "TRAP (fechado por login)"],
    MIN_PONTOS: 100,
    FAIL_CLOSED_RULE: "menos de 100 pontos = FAILED. Zero pontos NUNCA e 'sem infestacao': e falha.",
    DECLARED_FREQUENCY: "o documento declara periodo fechado de 7 dias",
    OBSERVED_FREQUENCY: "NÃO SEI — uma unica edicao capturada. O site NAO guarda arquivo (/bollettini da 404).",
    UPDATE_BEHAVIOR: "SOBRESCRITA — uma edicao por vez, a anterior desaparece",
    HISTORICAL_OR_FORWARD: "FORWARD_ONLY", ARCHIVE_REQUIREMENT: "CRITICAL",
    EXPECTED_FAILURES: ["fora de temporada a pagina pode anunciar pausa (ha vestigio de 'riprendera a Giugno')", "camada de catture continua LOGIN_REQUIRED"],
    FALLBACK: "nenhum — nao ha arquivo publico",
    SOURCE_LOCATION_RULE: "Livorno (sede) — fixo",
    FACT_LOCATION_RULE: "COORDENADA do ponto (lat/lon com 4 casas). PREFERIR a coordenada ao municipio inferido, e NUNCA usar a sede.",
    EVIDENCE_CLASS: "OBSERVED_FIELD_SIGNAL + COOPERATIVE_GUIDANCE",
    AUTOMATION_FEASIBILITY: "HIGH",
    // ── O BLOCO EXECUTÁVEL (contrato v2 · cutover do `case`) ─────────────
    // Copiado do `case "IT-T3-005"` @ 380bf090: rota única e fixa; a
    // identidade é o período impresso no corpo do HTML.
    ACQUISITION: { STRATEGY: "STATIC_ENDPOINT", URL: "https://www.terretruria.it/monitoraggio", NAME: "monitoraggio.html" },
    // `FACT_TIME` NÃO é UNKNOWN aqui, e NÃO é a data do boletim: cada ponto
    // traz a sua própria data de campionamento. A frase é a do `case`.
    IDENTITY: {
      STRATEGY: "CONTENT_CAPTURE",
      CAPTURES: {
        periodo: { FROM: "RAW_UTF8", PATTERN: "Bollettino del periodo dal\\s*([\\d-]+)\\s*al\\s*((\\d+)-(\\d+)-(\\d+))" },
      },
      DOCUMENT_ID: "TERRETRURIA:{periodo.1}:{periodo.2}",
      SOURCE_DATE: "{periodo.1} a {periodo.2}",
      SOURCE_DATE_ISO: "{periodo.5}-{periodo.4}-{periodo.3}",
      FACT_TIME: "por ponto — cada ponto traz sua propria data de campionamento",
    },
    NEGATIVE_CONTROL: { descricao: "HTML sem nenhum bloco reports_points", esperado: "FAILED, nunca 'zero pontos monitorados'" }
  },

  "IT-T4-001": {
    OWNER_ID: "IT-OWN-MINSALUTE", OWNER: "Ministero della Salute — Open Data",
    TERRITORY: "T4", VALUE: "P0",
    CANONICAL_ENTRY_URL: "https://www.dati.salute.gov.it/it/dataset/fitosanitari/",
    DISCOVERY_METHOD: "a pagina lista CSV, XML, JSON e o dicionario; o nome do arquivo carrega a data",
    RETRIEVAL_METHOD: "GET no CSV",
    ROUTE_TYPE: "PREDICTABLE_ROUTE",
    ROUTE_TEMPLATE: "https://www.dati.salute.gov.it/sites/default/files/opendata/PROD_FTS_6_{AAAAMMDD}.csv",
    ACCESS_INSTRUMENT: "HTTP", AUTH_REQUIRED: false, BROWSER_REQUIRED: false, JS_REQUIRED: false,
    OUTPUT_TYPE: "CSV", EXPECTED_MIME: /csv|text|octet/, EXPECTED_SIGNATURE: "num_registrazione;",
    MIN_BYTES: 3000000, MIN_ROWS: 15000,
    IDENTITY_KEYS: ["data_do_dataset", "num_registrazione"],
    DOCUMENT_ID_RULE: "MINSALUTE:FTS6:{AAAAMMDD}  ·  por linha: {num_registrazione}",
    DOCUMENT_DATE_FIELD: "data no nome do arquivo",
    VERSION_FIELD: "a propria data do arquivo",
    EXPECTED_COLUMNS: ["num_registrazione", "denominazione_prodotto", "ragione_sociale", "data_registrazione", "data_scadenza_autorizzazione", "sostanze_attive"],
    DECLARED_FREQUENCY: "nao declarada em texto; ha RSS de aviso de atualizacao",
    OBSERVED_FREQUENCY: "NÃO SEI — uma unica data observada",
    UPDATE_BEHAVIOR: "ADITIVO por data de arquivo", HISTORICAL_OR_FORWARD: "NÃO SEI — nao se testou se arquivos antigos permanecem",
    ARCHIVE_REQUIREMENT: "ALTO ate provar que os antigos ficam",
    EXPECTED_FAILURES: ["CSV com menos de 15.000 linhas = DEGRADED", "coluna sostanze_attive ausente = FAILED"],
    FAIL_CLOSED_RULE: "faltando qualquer coluna obrigatoria, e FAILED",
    FALLBACK: "XML ou JSON da mesma pagina",
    SOURCE_LOCATION_RULE: "Roma", FACT_LOCATION_RULE: "ITALIA — nacional",
    EVIDENCE_CLASS: "REGULATORY_AUTHORIZATION",
    AUTOMATION_FEASIBILITY: "HIGH",
    // ── O BLOCO EXECUTÁVEL (contrato v2 · cutover do `case`) ─────────────
    // Copiado do `case "IT-T4-001"` @ 380bf090: a página do dataset anuncia
    // o nome do CSV corrente; o ficheiro vive noutra pasta (BASE_URL), e a
    // data no nome é a versão.
    ACQUISITION: {
      STRATEGY: "HTML_LINK_DISCOVERY",
      INDEX_URL: "https://www.dati.salute.gov.it/it/dataset/fitosanitari/",
      BASE_URL: "https://www.dati.salute.gov.it/sites/default/files/opendata/",
      LINK_PATTERN: "opendata/(PROD_FTS_6_\\d{8}\\.csv)",
      MAX_TARGETS: 1,
    },
    IDENTITY: {
      STRATEGY: "FILENAME_CAPTURE",
      PATTERN: "^PROD_FTS_6_((\\d{4})(\\d{2})(\\d{2}))\\.csv$",
      DOCUMENT_ID: "MINSALUTE:FTS6:$1",
      SOURCE_DATE: "$2-$3-$4",
      SOURCE_DATE_ISO: "$2-$3-$4",
      FACT_TIME: "UNKNOWN — o CSV traz datas de registro por linha, nao uma data de fato do arquivo",
    },
    NEGATIVE_CONTROL: { descricao: "CSV sem a coluna sostanze_attive", esperado: "FAILED" }
  },

  "IT-T1-001": {
    OWNER_ID: "IT-OWN-ISTAT", OWNER: "ISTAT", TERRITORY: "T1", VALUE: "P0",
    CANONICAL_ENTRY_URL: "https://esploradati.istat.it/SDMXWS/rest/data/IT1,101_1015_DF_DCSP_COLTIVAZIONI_2,1.0/",
    DISCOVERY_METHOD: "catalogo SDMX de dataflows (4.897 dataflows) — o de interesse e 101_1015_DF_DCSP_COLTIVAZIONI_2",
    RETRIEVAL_METHOD: "GET com Accept: application/vnd.sdmx.data+csv",
    ROUTE_TYPE: "APPLICATION_ROUTE",
    classificacao_honesta: "e API SDMX 2.1 documentada e sem chave — pode ser chamada de OFFICIAL_API. O PORTAL visual do mesmo dominio exige JavaScript e chegou a devolver erro; sao coisas diferentes.",
    ACCESS_INSTRUMENT: "HTTP", AUTH_REQUIRED: false, BROWSER_REQUIRED: false, JS_REQUIRED: false,
    OUTPUT_TYPE: "CSV", EXPECTED_MIME: /sdmx.*csv/, EXPECTED_SIGNATURE: "DATAFLOW,FREQ,REF_AREA",
    MIN_ROWS: 10000,
    IDENTITY_KEYS: ["DATAFLOW", "REF_AREA", "TYPE_OF_CROP", "TIME_PERIOD"],
    DOCUMENT_ID_RULE: "ISTAT:{DATAFLOW}:{REF_AREA}:{TYPE_OF_CROP}:{TIME_PERIOD}",
    DOCUMENT_DATE_FIELD: "TIME_PERIOD", VERSION_FIELD: "versao do dataflow (1.0)",
    EXPECTED_COLUMNS: ["DATAFLOW", "FREQ", "REF_AREA", "TYPE_OF_CROP", "TIME_PERIOD", "OBS_VALUE"],
    DECLARED_FREQUENCY: "serie anual", OBSERVED_FREQUENCY: "NÃO SEI — nao medido por captura repetida",
    UPDATE_BEHAVIOR: "REVISAO — series estatisticas sao revisadas; a mesma chave pode mudar de valor",
    HISTORICAL_OR_FORWARD: "HISTORICAL", ARCHIVE_REQUIREMENT: "NORMAL",
    EXPECTED_FAILURES: ["resposta lenta (13 s para 13,6 MB no catalogo)", "timeout curto devolve resposta parcial — NUNCA aceitar corpo truncado"],
    FAIL_CLOSED_RULE: "corpo sem o cabecalho DATAFLOW,FREQ,REF_AREA = FAILED",
    FALLBACK: "nenhum",
    SOURCE_LOCATION_RULE: "Roma", FACT_LOCATION_RULE: "REF_AREA da propria linha (provincia)",
    EVIDENCE_CLASS: "SERIE_OFICIAL_DE_PRODUCAO", AUTOMATION_FEASIBILITY: "HIGH",
    NEGATIVE_CONTROL: { descricao: "corpo truncado no meio", esperado: "FAILED, nunca contagem parcial tratada como total" }
  },

  "IT-T2-004": {
    OWNER_ID: "IT-OWN-SIAS", OWNER: "SIAS — Servizio Informativo Agrometeorologico Siciliano",
    TERRITORY: "T2", VALUE: "P1",
    CANONICAL_ENTRY_URL: "http://www.sias.regione.sicilia.it/NHEOWL0530_00.html",
    DISCOVERY_METHOD: "site em FRAMESET: home.htm > frameset_dati.htm > corpo_dati.htm > tabela por grandeza. A home direta devolve casca vazia.",
    RETRIEVAL_METHOD: "GET na pagina da grandeza",
    ROUTE_TYPE: "STATIC_ROUTE",
    ACCESS_INSTRUMENT: "HTTP", AUTH_REQUIRED: false, BROWSER_REQUIRED: false, JS_REQUIRED: false,
    OUTPUT_TYPE: "HTML", EXPECTED_MIME: /^text\/html/, EXPECTED_SIGNATURE: "<", MIN_BYTES: 30000,
    ENCODING: "iso-8859-1 — charset antigo; decodificar antes de comparar texto",
    IDENTITY_KEYS: ["table_type", "station", "window_end"],
    DOCUMENT_ID_RULE: "SIAS:{TABLE_TYPE}:{STATION}:{WINDOW_END}",
    LEI_CRITICA: "SAME_URL != SAME_DOCUMENT — a URL e fixa e a janela de dados anda todo dia. Deduplicar por URL PERDE dado. Deduplicar por (table_type, station, window_end) + SHA256.",
    DOCUMENT_DATE_FIELD: "'dal DD/MM/AAAA al DD/MM/AAAA' no cabecalho da tabela",
    VERSION_FIELD: "window_end",
    EXPECTED_CONTENT_MARKERS: ["Precipitazioni giornaliere", "Ultimo", "cumulate"],
    MIN_STATIONS: 20,
    DECLARED_FREQUENCY: "a rede declara 88 estacoes e dados diarios",
    OBSERVED_FREQUENCY: "NÃO SEI — uma captura so",
    UPDATE_BEHAVIOR: "SOBRESCRITA — janela movel de 11 dias na mesma URL",
    HISTORICAL_OR_FORWARD: "FORWARD_ONLY", ARCHIVE_REQUIREMENT: "CRITICAL",
    nota_de_arquivo: "existe 'SEZIONE RICHIESTA DATI' para serie historica, NAO testada. Ate testar, tratar como FORWARD_ONLY.",
    EXPECTED_FAILURES: ["tabela sem linhas de estacao = FAILED", "janela igual a da captura anterior = NO_CHANGE, NAO DEGRADED. So vira OVERDUE_UPDATE se houver cadencia PROVADA e o prazo tiver vencido — e a cadencia do SIAS ainda e NÃO SEI."],
    FAIL_CLOSED_RULE: "tabela vazia NAO e 'nao choveu': e FAILED",
    FALLBACK: "outra grandeza (temperatura) para confirmar se o servidor esta vivo",
    SOURCE_LOCATION_RULE: "Palermo", FACT_LOCATION_RULE: "a ESTACAO da linha",
    EVIDENCE_CLASS: "AGROCLIMATIC_SIGNAL",
    LEI: "AGROCLIMATIC_SIGNAL != PEST_OCCURRENCE",
    AUTOMATION_FEASIBILITY: "HIGH",
    // ── O BLOCO EXECUTÁVEL (contrato v2 · cutover do `case`) ─────────────
    // Copiado do `case "IT-T2-004"` @ 380bf090: rota fixa da grandeza; a
    // identidade é o fim da janela impressa no cabeçalho da tabela, e a
    // grandeza (PRECIPITAZIONE_GIORNALIERA) está no DOCUMENT_ID como o
    // `case` a punha — era um literal do alvo, é um literal do molde.
    ACQUISITION: { STRATEGY: "STATIC_ENDPOINT", URL: "http://www.sias.regione.sicilia.it/NHEOWL0530_00.html", NAME: "NHEOWL0530_00.html" },
    IDENTITY: {
      STRATEGY: "CONTENT_CAPTURE",
      CAPTURES: {
        janela: { FROM: "RAW_LATIN1", PATTERN: "dal\\s*(\\d{2}/\\d{2}/\\d{4})\\s*al\\s*((\\d{2})/(\\d{2})/(\\d{4}))" },
      },
      DOCUMENT_ID: "SIAS:PRECIPITAZIONE_GIORNALIERA:WINDOW_END_{janela.5}-{janela.4}-{janela.3}",
      SOURCE_DATE: "{janela.1} a {janela.2}",
      SOURCE_DATE_ISO: "{janela.5}-{janela.4}-{janela.3}",
      FACT_TIME: "por linha — cada celula tem sua propria data",
    },
    NEGATIVE_CONTROL: { descricao: "tabela sem nenhuma linha de estacao", esperado: "FAILED, nunca zero chuva" }
  },

  "IT-T2-001": {
    OWNER_ID: "IT-OWN-ARPAE", OWNER: "ARPAE Emilia-Romagna", TERRITORY: "T2", VALUE: "P1",
    CANONICAL_ENTRY_URL: "https://www.arpae.it/it/temi-ambientali/meteo/report-meteo/bollettini-e-rapporti-agrometeo/bollettini-agrometeo/bollettini-{ANO}",
    OLD_ROUTE: "https://www.arpae.it/it/temi-ambientali/meteo/agrometeo — 404",
    CURRENT_ROUTE: "a rota acima",
    DISCOVERY_METHOD: "pagina do ano lista os PDFs numerados",
    RETRIEVAL_METHOD: "GET no PDF, SEM o sufixo /view",
    ARMADILHA: "o site e Plone. O link exibido termina em /view, que devolve a CASCA HTML da pagina, nao o PDF. SEMPRE remover /view e SEMPRE conferir a assinatura %PDF.",
    ROUTE_TYPE: "PREDICTABLE_ROUTE",
    ROUTE_TEMPLATE: ".../bollettini-{ANO}/{NN}_boll_agro_{AAAAMMDD}.pdf",
    ACCESS_INSTRUMENT: "HTTP", AUTH_REQUIRED: false, BROWSER_REQUIRED: false, JS_REQUIRED: false,
    OUTPUT_TYPE: "PDF", EXPECTED_MIME: /^application\/pdf/, EXPECTED_SIGNATURE: "%PDF", MIN_BYTES: 500000,
    IDENTITY_KEYS: ["ano", "numero_do_boletim"],
    DOCUMENT_ID_RULE: "ARPAE:{ANO}:N{NUMERO}",
    DOCUMENT_DATE_FIELD: "AAAAMMDD no nome do arquivo", VERSION_FIELD: "numero sequencial",
    DECLARED_FREQUENCY: "semanal", OBSERVED_FREQUENCY: "7D — provado por 7 edicoes seguidas na listagem",
    UPDATE_BEHAVIOR: "ADITIVO", HISTORICAL_OR_FORWARD: "HISTORICAL",
    ARCHIVE_REQUIREMENT: "BAIXO — ha arquivo por ano de 2021 a 2026",
    EXPECTED_FAILURES: ["usar /view devolve HTML com HTTP 200 — e FAILED"],
    FAIL_CLOSED_RULE: "corpo sem %PDF = FAILED",
    FALLBACK: "reler a pagina do ano",
    SOURCE_LOCATION_RULE: "Bologna", FACT_LOCATION_RULE: "Emilia-Romagna regional",
    EVIDENCE_CLASS: "AGROCLIMATIC_SIGNAL", LEI: "AGROCLIMATIC_SIGNAL != PEST_OCCURRENCE",
    AUTOMATION_FEASIBILITY: "HIGH",
    // ── O BLOCO EXECUTÁVEL (contrato v2 · ADDENDUM-01 FASE 5, endpoint provado) ──
    // Esta fonte nunca teve `case`: só prosa. Rota provada em 2026-09-20:
    //   INDEX_URL  → HTTP 200, 72.040 bytes, 60 href `*_boll_agro_*.pdf/view`
    //                (30 edições, cada uma listada duas vezes)
    //   primeiro   → …/bollettini-2026/37_boll_agro_20260914.pdf (sem /view)
    //                HTTP 200, application/pdf, 1.326.663 bytes, começa por %PDF
    // O `/view` é a ARMADILHA escrita acima: STRIP_SUFFIX tira-o ANTES de
    // pedir, e a validação de bytes (%PDF) continua a guardar a porta.
    ACQUISITION: {
      STRATEGY: "HTML_LINK_DISCOVERY", MATCH: "URL",
      INDEX_URL: "https://www.arpae.it/it/temi-ambientali/meteo/report-meteo/bollettini-e-rapporti-agrometeo/bollettini-agrometeo/bollettini-2026",
      LINK_PATTERN: "/bollettini-2026/\\d+_boll_agro_\\d{8}\\.pdf$",
      STRIP_SUFFIX: "/view",
      MAX_TARGETS: 1,
    },
    IDENTITY: {
      STRATEGY: "FILENAME_CAPTURE",
      PATTERN: "^(\\d+)_boll_agro_((\\d{4})(\\d{2})(\\d{2}))\\.pdf$",
      DOCUMENT_ID: "ARPAE:$3:N$1",
      SOURCE_DATE: "$2",
      SOURCE_DATE_ISO: "$3-$4-$5",
      FACT_TIME: "UNKNOWN — a data no nome e a da edicao semanal, nao a da observacao",
    },
    NEGATIVE_CONTROL: { descricao: "baixar a URL COM /view", esperado: "FAILED — HTML detectado, apesar do HTTP 200" }
  },

  "IT-T2-002": {
    OWNER_ID: "IT-OWN-ARPAV", OWNER: "ARPAV Veneto", TERRITORY: "T2", VALUE: "P1",
    CANONICAL_ENTRY_URL: "https://www.arpa.veneto.it/dati-ambientali/bollettini/agrometeo/agrometeoinforma",
    DISCOVERY_METHOD: "a pagina lista 32 links de zona; a leitura simples do HTML nao os mostrou — foram revelados pelo navegador",
    RETRIEVAL_METHOD: "GET direto no PDF da zona",
    ROUTE_TYPE: "BROWSER_DISCOVERED_ROUTE",
    ROUTE_TEMPLATE: "https://www.arpa.veneto.it/risorse/data-agrometeo/agrometeo/32zone/agro_{NN}.pdf  (NN = 01..32)",
    ACCESS_INSTRUMENT: "HTTP para baixar; BROWSER foi necessario para descobrir",
    AUTH_REQUIRED: false, BROWSER_REQUIRED: false, JS_REQUIRED: false,
    OUTPUT_TYPE: "PDF", EXPECTED_MIME: /^application\/pdf/, EXPECTED_SIGNATURE: "%PDF", MIN_BYTES: 200000,
    IDENTITY_KEYS: ["zone_id", "generated_at"],
    DOCUMENT_ID_RULE: "ARPAV:Z{ZONE_ID}:{GENERATED_AT}",
    DOCUMENT_DATE_FIELD: "NAO esta no nome do arquivo. Esta no metadado /CreationDate do proprio PDF (ex.: D:20260903160930+0200).",
    VERSION_FIELD: "CreationDate + SHA256",
    LEI_CRITICA: "SAME_URL != SAME_DOCUMENT — o nome do arquivo e FIXO e o conteudo e sobrescrito. Nunca deduplicar por URL. Cada SHA256 novo e uma observacao nova.",
    prova_medida: "agro_01 e agro_09 tem hashes diferentes E CreationDate diferentes (03/09 e 02/09) — as zonas publicam de forma independente",
    DECLARED_FREQUENCY: "o site declara: zonas 2-15/23/24 as segundas e quintas na primavera-verao, quartas no outono-inverno; as demais em outro calendario",
    OBSERVED_FREQUENCY: "NÃO SEI — uma captura so",
    UPDATE_BEHAVIOR: "SOBRESCRITA", HISTORICAL_OR_FORWARD: "FORWARD_ONLY", ARCHIVE_REQUIREMENT: "CRITICAL",
    EXPECTED_FAILURES: ["mesmo SHA numa nova captura = NO_CHANGE, NAO DEGRADED. Consultar duas vezes no mesmo dia uma fonte que publica 2x por semana DEVE devolver o mesmo documento — isso e o comportamento esperado.", "sem CreationDate = DEGRADED, porque ai falta identidade temporal"],
    FAIL_CLOSED_RULE: "corpo sem %PDF = FAILED",
    FALLBACK: "nenhum — o arquivo anterior ja foi perdido",
    SOURCE_LOCATION_RULE: "Teolo/Padova", FACT_LOCATION_RULE: "a ZONA do numero do arquivo",
    EVIDENCE_CLASS: "AGROCLIMATIC_SIGNAL", LEI: "AGROCLIMATIC_SIGNAL != PEST_OCCURRENCE",
    AUTOMATION_FEASIBILITY: "HIGH",
    // ── O BLOCO EXECUTÁVEL (contrato v2 · cutover do `case`) ─────────────
    // Copiado do `case "IT-T2-002"` @ 380bf090. O `case` tinha DUAS listas:
    // as 4 zonas do piloto (1, 9, 16, 24) e as 29 publicadas (1..32 menos
    // 17, 18, 19, que devolvem 404 consistente — facto da fonte, medido em
    // `candidatas/italy_profiles.mjs`). As duas continuam a existir, mas
    // como DADOS: o provider tem as 29, e `SUBCONJUNTOS.PILOTO` tem as 4.
    // Quem corre escolhe o subconjunto; o despachador não sabe o que é uma
    // zona.
    ACQUISITION: {
      STRATEGY: "TEMPLATE_ENUMERATION",
      TEMPLATE: "https://www.arpa.veneto.it/risorse/data-agrometeo/agrometeo/32zone/agro_{NN}.pdf",
      VARS: {
        NN: { PROVIDER: "ENUM", VALUES: [
          "01", "02", "03", "04", "05", "06", "07", "08", "09", "10", "11", "12", "13", "14", "15", "16",
          "20", "21", "22", "23", "24", "25", "26", "27", "28", "29", "30", "31", "32",
        ] },
      },
      SUBCONJUNTOS: { PILOTO: { NN: ["01", "09", "16", "24"] } },
    },
    // A identidade é a zona (nome do ficheiro) + o `/CreationDate` do PDF
    // (bytes crus, latin1) — exactamente os dois sítios que o `case` lia.
    IDENTITY: {
      STRATEGY: "CONTENT_CAPTURE",
      CAPTURES: {
        zona: { FROM: "FILENAME", PATTERN: "^agro_(\\d{2})\\.pdf$" },
        gerado: { FROM: "RAW_LATIN1", PATTERN: "/CreationDate\\s*\\(D:((\\d{4})(\\d{2})(\\d{2})\\d{6})" },
      },
      DOCUMENT_ID: "ARPAV:Z{zona.1}:{gerado.1}",
      SOURCE_DATE: "{gerado.2}-{gerado.3}-{gerado.4}",
      SOURCE_DATE_ISO: "{gerado.2}-{gerado.3}-{gerado.4}",
      FACT_TIME: "UNKNOWN — o PDF nao expoe a data do fato medido, so a de geracao",
    },
    NEGATIVE_CONTROL: { descricao: "capturar duas vezes seguidas sem mudanca", esperado: "SEEN_AGAIN + NO_CHANGE, com 0 objetos RAW novos. NUNCA DEGRADED, e NUNCA duas versoes." }
  },

  "IT-T7-002": {
    OWNER_ID: "IT-OWN-MASAF", OWNER: "MASAF", TERRITORY: "T7", VALUE: "P0",
    CANONICAL_ENTRY_URL: "https://www.masaf.gov.it/flex/cm/pages/ServeBLOB.php/L/IT/IDPagina/6063",
    DISCOVERY_METHOD: "navegar Politiche nazionali > Filiere > Organizzazioni di Produttori > Elenco nazionale; o anexo tem hash opaco na URL e MUDA a cada edicao",
    RETRIEVAL_METHOD: "descobrir o link do anexo na pagina e baixar",
    ROUTE_TYPE: "DISCOVERED_ROUTE",
    aviso_de_rota: "NAO fixar a URL do anexo. Ela contem um hash de conteudo que muda a cada nova edicao. Fixar quebraria silenciosamente na proxima publicacao.",
    ACCESS_INSTRUMENT: "HTTP", AUTH_REQUIRED: false, BROWSER_REQUIRED: false, JS_REQUIRED: false,
    OUTPUT_TYPE: "ODS", EXPECTED_MIME: /opendocument|octet|zip/, EXPECTED_SIGNATURE: "PK", MIN_BYTES: 30000,
    IDENTITY_KEYS: ["versao_da_publicacao", "codice_organizzazione"],
    DOCUMENT_ID_RULE: "MASAF:OP:{DATA_DA_EDICAO}  ·  por linha: {CODICE_IT}",
    DOCUMENT_DATE_FIELD: "no titulo do link: 'al 31 dicembre 2025 - aggiornato al 08.04.2026'",
    VERSION_FIELD: "a data de referencia + o 'REV.' quando existir",
    EXPECTED_COLUMNS: ["CODICE IT", "OP AOP", "SETTORE", "DENOMINAZIONE", "FORMA SOCIETARIA", "SEDE", "DATA DI RICONOSCIMENTO", "REGIONE"],
    CONTAGEM: {
      RAW_ROWS: 324, UNIQUE_ORGANIZATIONS: 272, OP: 264, AOP: 8, DUPLICADOS: 0,
      DUPLICATE_KEY_RULE: "chave = CODICE IT, casando /^IT\\//. Linha sem CODICE IT nao e organizacao.",
      WHY_DIFFERENT: "as 52 linhas a mais sao cabecalho, titulo do regulamento, linhas de secao por setor e linhas em branco do layout. ROWS != UNIQUE_ORGANIZATIONS.",
      CORRECAO: "publiquei 269 e depois 264. AMBOS ERRADOS. O 269 vinha de um parse por linha que perdia codigos; o 264 de um regex /^IT\\/[A-Z]+\\/\\d+/ que nao casa AOP, cujo codigo tem QUATRO segmentos (IT/OLI/AOP/001). Certo: 272."
    },
    DECLARED_FREQUENCY: "nao declarada em texto", OBSERVED_FREQUENCY: "1Y — tres edicoes anuais na mesma pagina (31/12/2023, 31/12/2024 REV.3, 31/12/2025)",
    UPDATE_BEHAVIOR: "ADITIVO", HISTORICAL_OR_FORWARD: "HISTORICAL", ARCHIVE_REQUIREMENT: "NORMAL",
    EXPECTED_FAILURES: ["planilha com menos de 200 organizacoes = DEGRADED", "coluna CODICE IT ausente = FAILED"],
    FAIL_CLOSED_RULE: "sem a coluna CODICE IT nao ha identidade — FAILED",
    FALLBACK: "as edicoes anteriores continuam na mesma pagina",
    SOURCE_LOCATION_RULE: "Roma", FACT_LOCATION_RULE: "a REGIONE e a SEDE declaradas em CADA LINHA da planilha.",
    POR_QUE_A_SEDE_VALE_AQUI: "excecao explicita, e a unica. Nas outras fontes a sede e a de QUEM PUBLICA, e usa-la seria localizar mal um fato de campo. Aqui o proprio fato registrado E o endereco: a linha diz onde aquela organizacao esta sediada. Nao ha fato de campo nenhum nesta fonte. Continua valendo que a sede do MASAF (Roma) NUNCA e FACT_LOCATION.",
    EVIDENCE_CLASS: "OFFICIAL_ORGANIZATION_REGISTRY", SOURCE_ROLE: "DISCOVERY_IDENTITY",
    LEI: "REGISTRY != FIELD_SIGNAL — esta fonte nunca prova nada de campo",
    AUTOMATION_FEASIBILITY: "MEDIUM",
    NEGATIVE_CONTROL: { descricao: "planilha sem a coluna CODICE IT", esperado: "FAILED" }
  },

  "IT-T3-011": {
    OWNER_ID: "IT-OWN-AGRIOS", OWNER: "AGRIOS — Alto Adige", TERRITORY: "T3", VALUE: "P1",
    CANONICAL_ENTRY_URL: "https://www.agrios.it/it/per-i-frutticoltori/documenti-e-disciplinari/",
    aviso_de_idioma: "o site e primariamente em ALEMAO. A versao italiana vive em /it/. Detector que so procura palavras italianas na home NAO acha nada — foi o que gerou o falso diagnostico de 'JavaScript'.",
    DISCOVERY_METHOD: "pagina de documentos lista os PDFs e planilhas",
    RETRIEVAL_METHOD: "GET no PDF", ROUTE_TYPE: "DISCOVERED_ROUTE",
    ACCESS_INSTRUMENT: "HTTP", AUTH_REQUIRED: false, BROWSER_REQUIRED: false, JS_REQUIRED: false,
    OUTPUT_TYPE: "PDF", EXPECTED_MIME: /^application\/pdf/, EXPECTED_SIGNATURE: "%PDF", MIN_BYTES: 1000000,
    IDENTITY_KEYS: ["ano_da_edicao"], DOCUMENT_ID_RULE: "AGRIOS:DIRETTIVE:{ANO}",
    DOCUMENT_DATE_FIELD: "o ano no titulo da capa", VERSION_FIELD: "ano da edicao",
    EXPECTED_CONTENT_MARKERS: ["DIRETTIVE PER", "FRUTTICOLTURA INTEGRATA"],
    DECLARED_FREQUENCY: "anual, pelo proprio titulo", OBSERVED_FREQUENCY: "NÃO SEI — uma edicao observada",
    UPDATE_BEHAVIOR: "ANUAL — nome de arquivo livre, muda a cada ano",
    HISTORICAL_OR_FORWARD: "NÃO SEI", ARCHIVE_REQUIREMENT: "NORMAL",
    EXPECTED_FAILURES: ["nome de arquivo fixado quebra no ano seguinte"],
    FAIL_CLOSED_RULE: "sem os marcadores de titulo = FAILED",
    FALLBACK: "a versao alema do mesmo documento",
    SOURCE_LOCATION_RULE: "Terlano (BZ)", FACT_LOCATION_RULE: "Alto Adige — area de aplicacao",
    EVIDENCE_CLASS: "TECHNICAL_GUIDELINE",
    LEI: "TECHNICAL_GUIDELINE != CURRENT_FIELD_SIGNAL e != DEROGA. Se aparecer uma deroga, ela e OUTRO documento e provavelmente OUTRO canal.",
    AUTOMATION_FEASIBILITY: "MEDIUM",
    // ── O BLOCO EXECUTÁVEL (contrato v2) ──────────────────────────────────
    // ⚠️ ESTA FONTE FALHOU NA BIG COLLECTION E A CULPA NÃO ERA DELA.
    // Medido: o site respondeu HTTP 200 com 39.340 bytes e QUATRO links PDF.
    // O que devolveu zero foi `italy_pilot_collect.mjs`, com a frase
    // «fonte sem alvo definido no piloto» — ela não tinha `case` no switch.
    // Eu próprio classifiquei isso como falha de fonte; era falha nossa.
    //
    //     UM SITE QUE RESPONDE E UMA COLETA QUE NÃO PERGUNTA
    //     PRODUZEM O MESMO ZERO, E NÃO SÃO A MESMA COISA.
    //
    // Nada aqui foi inventado: `INDEX_URL` é o `CANONICAL_ENTRY_URL` que já
    // estava escrito, e `LINK_PATTERN` foi medido contra o HTML real. Os
    // campos em prosa acima — `DISCOVERY_METHOD`, `aviso_de_idioma` — ficam
    // onde estão, para quem lê; o runtime não os abre.
    ACQUISITION: {
      STRATEGY: "HTML_LINK_DISCOVERY",
      INDEX_URL: "https://www.agrios.it/it/per-i-frutticoltori/documenti-e-disciplinari/",
      // Dado, não código: uma string compilada com `new RegExp`. Sem `eval`,
      // sem função serializada. O grupo 1 é o endereço a seguir.
      LINK_PATTERN: 'href="([^"]*\\.pdf)"',
      MAX_TARGETS: 4,
    },
    // A identidade tambem declarada — para nao deixar metade do problema
    // resolvido. `ano_da_edicao` ja era a `IDENTITY_KEY` escrita acima; aqui
    // ela ganha forma executavel.
    //
    // ⚠️ `FACT_TIME` FICA `UNKNOWN`, E ISSO E A RESPOSTA CERTA.
    // Uma diretriz tecnica anual diz quando FOI PUBLICADA, nao quando um
    // facto aconteceu no campo. Usar o ano da edicao como tempo do facto
    // seria fabricar evidencia.
    //
    //     FACT_TIME != PUBLISHED_AT.
    IDENTITY: {
      STRATEGY: "FILENAME_CAPTURE",
      PATTERN: "(20\\d{2})",
      DOCUMENT_ID: "AGRIOS:DIRETTIVE:$1",
      SOURCE_DATE: "$1",
      FACT_TIME: "UNKNOWN — uma diretriz anual nao data o facto de campo",
    },
    NEGATIVE_CONTROL: { descricao: "PDF de outro documento do mesmo site", esperado: "FAILED por marcador de titulo ausente" }
  },

  "IT-T5-002": {
    OWNER_ID: "IT-OWN-014", OWNER: "Fondazione Edmund Mach — OpenPub (IRIS/CINECA)",
    TERRITORY: "T5", VALUE: "P1",
    CANONICAL_ENTRY_URL: "https://openpub.fmach.it/handle/{HANDLE}",
    OLD_ROUTE: "publications.fmach.it — host inexistente", CURRENT_ROUTE: "openpub.fmach.it",
    DISCOVERY_METHOD: "busca simples na interface; a rota de busca com parametros proprios devolveu HTTP 400 — usar as rotas que a interface gera",
    RETRIEVAL_METHOD: "GET na pagina do handle", ROUTE_TYPE: "APPLICATION_ROUTE",
    ACCESS_INSTRUMENT: "HTTP", AUTH_REQUIRED: false, BROWSER_REQUIRED: false, JS_REQUIRED: false,
    OUTPUT_TYPE: "HTML", EXPECTED_MIME: /^text\/html/, EXPECTED_SIGNATURE: "<", MIN_BYTES: 20000,
    IDENTITY_KEYS: ["handle"], DOCUMENT_ID_RULE: "FEM:HANDLE:{10449/NNNNN}",
    CAMPOS: ["PUBLICATION_ID", "TITLE", "AUTHOR_IDS", "DATE", "DOI", "SUBJECT/QUERY", "ABSTRACT"],
    LEI_CRITICA: "QUERY_MATCH != PROVED_TOPIC. Os 188 resultados da busca por 'Drosophila suzukii' sao 188 REGISTROS QUE A BUSCA CASOU — nao 188 evidencias independentes, nao 188 pesquisadores, e nao 188 trabalhos comprovadamente sobre o tema. A contagem e da busca, nao do assunto.",
    DECLARED_FREQUENCY: "nenhuma", OBSERVED_FREQUENCY: "IRREGULAR — repositorio alimentado quando sai publicacao",
    UPDATE_BEHAVIOR: "ADITIVO", HISTORICAL_OR_FORWARD: "HISTORICAL", ARCHIVE_REQUIREMENT: "BAIXO",
    EXPECTED_FAILURES: ["busca com parametros proprios devolve HTTP 400", "resultado vazio = FAILED, nao 'nenhuma publicacao'"],
    FAIL_CLOSED_RULE: "lista de busca vazia e FAILED",
    FALLBACK: "navegar por Settore Scientifico Disciplinare",
    SOURCE_LOCATION_RULE: "San Michele all'Adige (TN)",
    FACT_LOCATION_RULE: "UNKNOWN por padrao — so preencher se o proprio trabalho declarar a area de estudo",
    EVIDENCE_CLASS: "SCIENTIFIC_EVIDENCE", AUTOMATION_FEASIBILITY: "MEDIUM",
    NEGATIVE_CONTROL: { descricao: "busca que retorna zero resultados", esperado: "FAILED, nunca 'zero publicacoes sobre o tema'" }
  },

  "IT-T9-008": {
    // OWNER_ID e a CHAVE do catalogo candidato ITALY-SOURCE-MASTER-V1, nao
    // identidade canonica de dono (know-how §127-5b.2). Ate 2026-09-16 este
    // contrato de ACESSO usava a chave IT-OWN-ADAMA-IT para a mesma entidade
    // (ADAMA Italia S.r.l., a que a ficha IT-T9-008 do Atlas nomeia); passou a
    // usar a chave do MASTER. A chave anterior fica aqui como historia.
    OWNER_ID: "IT-OWN-040", OWNER: "ADAMA Italia S.r.l.", TERRITORY: "T9", VALUE: "P2",
    CANONICAL_ENTRY_URL: "https://www.adama.com/italia/it/articoli-news-ed-eventi-main",
    DISCOVERY_METHOD: "listagem de artigos no site", RETRIEVAL_METHOD: "navegador com janela",
    ROUTE_TYPE: "BROWSER_DISCOVERED_ROUTE",
    ACCESS_INSTRUMENT: "BROWSER", AUTH_REQUIRED: false, BROWSER_REQUIRED: true, JS_REQUIRED: "NÃO SEI — o servidor recusa antes de dar para testar",
    WAF_OBSERVED: true,
    OUTPUT_TYPE: "BROWSER_RENDERED_EXTRACT",
    LEI_CRITICA: "SERVER_RAW > BROWSER_RENDERED_DOCUMENT > BROWSER_RENDERED_EXTRACT. Hoje so temos o terceiro. NAO existe caminho honesto para virar RAW_PRESERVED enquanto o servidor recusar cliente sem navegador. Nao forcar.",
    IDENTITY_KEYS: ["canonical_url", "article_published_time"],
    DOCUMENT_ID_RULE: "ADAMA:{CANONICAL_URL}:{PUBLISHED_TIME}",
    DOCUMENT_DATE_FIELD: "meta article:published_time e article:modified_time (o site e Drupal 10 e expoe os dois)",
    VERSION_FIELD: "modified_time",
    DECLARED_FREQUENCY: "nenhuma", OBSERVED_FREQUENCY: "NÃO SEI",
    UPDATE_BEHAVIOR: "ADITIVO", HISTORICAL_OR_FORWARD: "HISTORICAL", ARCHIVE_REQUIREMENT: "NORMAL",
    EXPECTED_FAILURES: ["403 se tentar sem navegador — e o comportamento NORMAL, nao uma queda da fonte"],
    FAIL_CLOSED_RULE: "extrato sem canonical_url ou sem published_time nao tem identidade — FAILED",
    FALLBACK: "nenhum",
    SOURCE_LOCATION_RULE: "site nacional",
    FACT_LOCATION_RULE: "UNKNOWN — artigo de empresa nao localiza fato de campo. NUNCA inferir pela sede.",
    EVIDENCE_CLASS: "COMPANY_CLAIM", LEI: "COMPANY_CLAIM != REGULATORY_FACT — vale inclusive para a ADAMA",
    AUTOMATION_FEASIBILITY: "MEDIUM — exige navegador. BROWSER_REQUIRED != SOURCE_UNAUTOMATABLE.",
    NEGATIVE_CONTROL: { descricao: "extrato sem published_time", esperado: "FAILED por falta de identidade" }
    },

    "IT-T8-001": {
    // Este contrato NAO constroi rota nova. Ele DECLARA como esta fonte usa
    // capacidades YouTube que ja existem e ja foram provadas no repositorio:
    //   youtube.channel.discovery  ·  youtube.video.metadata  ·  youtube.public_audio
    // Nao ha aqui yt-dlp, nao ha chamada a YouTube Data API, nao ha ASR e nao
    // ha RSS proprio: quem faz isso sao os donos acima. Duplicar qualquer um
    // deles criaria um segundo downloader, e um segundo downloader diverge.
    OWNER_ID: "IT-OWN-IMAGE-LINE", OWNER: "Image Line Network S.r.l.",
    TERRITORY: "T8", VALUE: "P1",
    CANONICAL_ENTRY_URL: "https://www.youtube.com/@AgroNotizie",
    SOURCE_NATIVE_ID: "UCUs2Mg7jvUTRt7_MSOFYM5Q",
    SOURCE_NATIVE_ID_KIND: "YOUTUBE_CHANNEL_ID",
    LEI_DA_IDENTIDADE: "SOURCE_ID != CHANNEL_ID. IT-T8-001 e a identidade do projeto; UCUs2... e a identidade da plataforma. O contrato liga as duas AQUI, e este e o unico sitio onde essa ligacao esta escrita. Derivar SOURCE_ID do handle, da URL, do slug ou do proprio channel_id e proibido.",
    DISCOVERY_METHOD: "listagem de videos do canal pela capacidade ja provada youtube.channel.discovery",
    RETRIEVAL_METHOD: "metadata por youtube.video.metadata; audio publico por youtube.public_audio",
    ROUTE_TYPE: "APPLICATION_ROUTE",
    CAPABILITIES_REUTILIZADAS: ["youtube.channel.discovery", "youtube.video.metadata", "youtube.public_audio"],
    ACCESS_INSTRUMENT: "SCRAP", AUTH_REQUIRED: false, BROWSER_REQUIRED: false, JS_REQUIRED: false,
    SESSION_FORBIDDEN: "rota publica: sem cookie, sem login, sem sessao. Ver C13.",
    OUTPUT_TYPE: "VIDEO_METADATA + PUBLIC_AUDIO",
    IDENTITY_KEYS: ["video_id", "published_at"],
    DOCUMENT_ID_RULE: "AGRONOTIZIE:YT:{VIDEO_ID}  —  o video_id nativo do YouTube e a identidade do ITEM, nao da FONTE. A fonte continua a ser IT-T8-001.",
    DOCUMENT_DATE_FIELD: "published_at do video",
    VERSION_FIELD: "nenhum — o YouTube nao versiona o video publicado",
    DECLARED_FREQUENCY: "nao declarada pelo canal",
    OBSERVED_FREQUENCY: "NÃO SEI — nao medido por captura repetida",
    UPDATE_BEHAVIOR: "ADITIVO", HISTORICAL_OR_FORWARD: "HISTORICAL", ARCHIVE_REQUIREMENT: "NORMAL",
    EXPECTED_FAILURES: [
    "video sem video_id = FAILED por falta de identidade",
    "video privado/removido = FAILED, nao DEGRADED",
    "audio indisponivel = DEGRADED: a metadata continua valida sem ele"
    ],
    FAIL_CLOSED_RULE: "item sem video_id ou sem published_at nao tem identidade — FAILED",
    FALLBACK: "nenhum. Nao cair para scraping de pagina nem para rota paga.",
    SOURCE_LOCATION_RULE: "ITALIA — o canal e italiano e publica em italiano",
    FACT_LOCATION_RULE: "UNKNOWN — canal italiano NAO prova fato ocorrido em Italia. Cada item tem de dizer de si. NUNCA inferir a partir do canal.",
    TIME_RULE: "published_at e PUBLICATION_TIME. NAO e FACT_TIME.",
    EVIDENCE_CLASS: "EDITORIAL_AGRONOMIC_MEDIA",
    LEI: "MEDIA_EDITORIAL != REGULATORY_FACT — o canal noticia e comenta, nao autoriza nada.",
    AUTOMATION_FEASIBILITY: "HIGH — capacidades ja provadas, rota publica, sem credencial de sessao",
    NEGATIVE_CONTROL: { descricao: "item sem video_id", esperado: "FAILED por falta de identidade" }
    }
    };

// ── OS CONTRATOS ONBOARDED, EM LOTE (ADDENDUM-01 · FAST TRACK) ─────────────
// 107 fontes que a missao SOURCE-COLLECTION-READINESS-V1 sondou em 2026-09-18
// (HTTP 200, documento observado, assinatura conferida) e deixou numa tabela
// declarativa com vocabulario proprio (SHAPE). Aqui entram TRADUZIDAS para o
// vocabulario do motor de rota — STRATEGY / MATCH / INDEX_URL / LINK_PATTERN —
// para que exista UM motor e nao dois. Uma linha por fonte, em
// `italy_contracts_onboarded.json`; o contrato completo nasce de
// `contratoGenerico()`.
//
// O DONO DO CONTRATO CONTINUA A SER ESTE FICHEIRO (o export `CONTRACTS`).
// A tabela e configuracao, nao uma segunda autoridade.
//
//     UMA FONTE CONFIGURADA NAO E UMA FONTE APROVADA.
//     A tabela diz COMO se chega; o Livro de Relevancia diz SE se vai.
//
// O QUE ESTE CONTRATO NAO INVENTA. A identidade SEMANTICA do documento (numero
// de edicao, data no cabecalho) exige regra medida por fonte, e nenhuma destas
// linhas a tem. O que existe de honesto e o ENDERECO do documento — e e isso
// que o DOCUMENT_ID carrega, dito com esse nome (`IDENTITY_KIND = URL_PATH`).
// Bytes novos no mesmo endereco sao DOCUMENT_CHANGED_IN_PLACE, e o ledger
// guarda as duas versoes: SAME_URL != SAME_DOCUMENT continua a valer.
//
//     FACT_TIME = UNKNOWN. Nenhuma destas fontes data o facto por regra
//     generica, e o endereco nao e uma data.
import { readFileSync } from "node:fs";
const TABELA_ONBOARDED = JSON.parse(
  readFileSync(new URL("./italy_contracts_onboarded.json", import.meta.url), "utf8"));

const ASSINATURA_POR_TIPO = { PDF: "%PDF", HTML: "<" };
const MIME_POR_TIPO = { PDF: /^application\/pdf/, HTML: /^text\/html/ };

export function contratoGenerico(linha) {
  const tipo = String(linha.OUTPUT_TYPE || "").toUpperCase();
  if (!ASSINATURA_POR_TIPO[tipo]) throw new Error(`OUTPUT_TYPE desconhecido na tabela onboarded: ${linha.SOURCE_ID} -> ${tipo}`);
  const aq = linha.ACQUISITION;
  if (!aq || !aq.STRATEGY) throw new Error(`linha sem ACQUISITION na tabela onboarded: ${linha.SOURCE_ID}`);
  const fixo = aq.STRATEGY === "STATIC_ENDPOINT";
  const entrada = fixo ? aq.URL : aq.INDEX_URL;
  return {
    OWNER_ID: "NAO SEI", OWNER: linha.OWNER || linha.NAME || "NAO SEI",
    TERRITORY: linha.TERRITORY, VALUE: "NAO SEI",
    CANONICAL_ENTRY_URL: entrada,
    DISCOVERY_METHOD: fixo
      ? "GET direto no documento observado (documento fixo; descoberta de edicoes novas NAO configurada)"
      : "GENERICO: abrir INDEX_URL, resolver todos os href e ficar com os que casam com LINK_PATTERN (MATCH=URL)",
    RETRIEVAL_METHOD: "GET direto no documento",
    ROUTE_TYPE: fixo ? "STATIC_ROUTE" : "DISCOVERED_ROUTE",
    ACCESS_INSTRUMENT: "HTTP", AUTH_REQUIRED: false, BROWSER_REQUIRED: false, JS_REQUIRED: false,
    OUTPUT_TYPE: tipo, EXPECTED_MIME: MIME_POR_TIPO[tipo], EXPECTED_SIGNATURE: ASSINATURA_POR_TIPO[tipo], MIN_BYTES: 1000,
    ACQUISITION: aq,
    IDENTITY_KEYS: ["url_path"],
    IDENTITY_KIND: "URL_PATH",
    DOCUMENT_ID_RULE: `${linha.SOURCE_ID}:URL:{caminho do endereco} — identidade pelo ENDERECO, nao semantica; a fonte nao expoe identificador proprio por regra generica`,
    IDENTITY: {
      STRATEGY: "CONTENT_CAPTURE",
      CAPTURES: { doc: { FROM: "URL", PATTERN: "^https?://[^/]+/?(.*?)/?$" } },
      DOCUMENT_ID: `${linha.SOURCE_ID}:URL:{doc.1}`,
      FACT_TIME: "UNKNOWN — identidade pelo endereco; a fonte nao expoe data do facto por regra generica",
    },
    DOCUMENT_DATE_FIELD: "NAO SEI", VERSION_FIELD: "NAO SEI",
    EXPECTED_CONTENT_MARKERS: null,
    DECLARED_FREQUENCY: "NAO SEI", OBSERVED_FREQUENCY: "NAO SEI — uma captura so",
    UPDATE_BEHAVIOR: "NAO SEI", HISTORICAL_OR_FORWARD: "NAO SEI", ARCHIVE_REQUIREMENT: "NAO SEI",
    EXPECTED_FAILURES: [
      "entrada inacessivel (transporte, 403, 404) = FAILED, nunca zero documentos",
      "entrada sem nenhum endereco que case com LINK_PATTERN = EMPTY_LIST = FAILED",
      `documento cuja assinatura de bytes nao e ${tipo} = BYTE_VALIDATION_FAILED (HTTP 200 nao salva)`,
    ],
    FAIL_CLOSED_RULE: `sem endereco descoberto ou com bytes que nao sao ${tipo}, e FAILED — nunca se regista a pagina de entrada como documento`,
    FALLBACK: "nenhum",
    SOURCE_LOCATION_RULE: "NAO SEI",
    FACT_LOCATION_RULE: "UNKNOWN por padrao — so preencher se o proprio documento declarar; NUNCA inferir",
    EVIDENCE_CLASS: "NAO SEI",
    AUTOMATION_FEASIBILITY: "MEDIUM — rota generica; identidade semantica por medir",
    NEGATIVE_CONTROL: { descricao: "entrada que nao lista nenhum endereco que case com LINK_PATTERN", esperado: "EMPTY_LIST -> FAILED, nunca a pagina de entrada como documento" },
    BATCH_ID: linha.BATCH_ID,
    ONBOARDED_BY: "SOURCE-COLLECTION-READINESS-V1 (sondagem 2026-09-18) · traduzido no CUTOVER-RECUPERADO 2026-09-20",
    EVIDENCE: linha.EVIDENCE || null,
    SONDAGEM: linha.SONDAGEM || null,
  };
}

for (const linha of TABELA_ONBOARDED.FONTES) {
  if (!/^IT-T\d+-\d{3}$/.test(String(linha.SOURCE_ID || "")))
    throw new Error(`SOURCE_ID invalido na tabela onboarded: ${linha.SOURCE_ID}`);
  if (CONTRACTS[linha.SOURCE_ID]) {
    // Uma fonte que JA tem contrato escrito a mao nao e reescrita: a tabela
    // so lhe empresta a forma de aquisicao se ele ainda nao a tiver.
    if (CONTRACTS[linha.SOURCE_ID].ACQUISITION)
      throw new Error(`${linha.SOURCE_ID} tem contrato executavel a mao E linha na tabela onboarded — a tabela nao pode contradizer o contrato`);
    CONTRACTS[linha.SOURCE_ID].ACQUISITION = linha.ACQUISITION;
    CONTRACTS[linha.SOURCE_ID].IDENTITY = contratoGenerico(linha).IDENTITY;
    CONTRACTS[linha.SOURCE_ID].IDENTITY_KIND = "URL_PATH";
    CONTRACTS[linha.SOURCE_ID].BATCH_ID = linha.BATCH_ID;
    CONTRACTS[linha.SOURCE_ID].ONBOARDED_BY = "SOURCE-COLLECTION-READINESS-V1 (so a forma de aquisicao e a identidade generica; o contrato a mao manda no resto)";
    continue;
  }
  CONTRACTS[linha.SOURCE_ID] = contratoGenerico(linha);
}
export const ONBOARDED_IDS = Object.freeze(TABELA_ONBOARDED.FONTES.map((l) => l.SOURCE_ID));

export const CONTRACT_IDS = Object.keys(CONTRACTS);
