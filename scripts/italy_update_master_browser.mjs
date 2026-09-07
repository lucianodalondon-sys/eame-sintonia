import { readFileSync, writeFileSync } from "node:fs";
const p = "data/samples/ITALY-SOURCE-MASTER-V1.json";
const d = JSON.parse(readFileSync(p, "utf8"));

d.rodada_browser_2026_09_07 = {
  instrumento: "navegador com janela, do IP italiano. IP de saida do NAVEGADOR verificado antes de tudo: 205.147.30.20 · Milano · IT · Proton AG. A extensao do Chrome do usuario continua nao pareada; usou-se o navegador embutido, que sai pela mesma VPN do sistema.",
  base: "claude/italy-source-master-v1 @ d1639e61b9460948a65fd94ed87030a17623e840",

  o_que_o_browser_resolveu: [
    { fonte: "IT-T7-002 MASAF OP/AOP", antes: "lista nao aparecia por navegacao simples", agora: "planilha .ods com 269 organizacoes, achada pelo menu Politiche nazionali > Filiere" },
    { fonte: "IT-T3-011 AGRIOS", antes: "marcada como 'provavel JavaScript'", agora: "nao era JavaScript — o site e em ALEMAO. Direttive 2026 em italiano preservadas." },
    { fonte: "IT-T2-002 ARPAV", antes: "escolha de zona parecia JavaScript", agora: "32 PDFs de zona com URL fixa, que so o navegador revelou" },
    { fonte: "IT-T2-004 SIAS Sicilia", antes: "frameset devolvia casca vazia", agora: "tabela diaria por estacao, 88 estacoes declaradas" },
    { fonte: "IT-T3-008 ARIF Puglia", antes: "403 ao curl", agora: "arifpuglia.it da 403 ATE no navegador, MAS a ARIF publica em agrometeopuglia.it — semanal fitossanitario, Anno XL" },
    { fonte: "IT-T3-010 APOL Lecce", antes: "sem URL no catalogo", agora: "http://www.apol.it (HTTP, nao HTTPS) — 9 boletins semanais de mosca-da-azeitona em 2026 + 14 em 2025" },
    { fonte: "IT-T5-002 FEM OpenPub", antes: "host do catalogo nao resolvia", agora: "openpub.fmach.it — artigo com abstract preservado" },
    { fonte: "IT-T9-008 ADAMA / IT-T9-002 Bayer", antes: "403 ao curl", agora: "ABREM no navegador italiano. 403 era filtro anti-robo, nao bloqueio ao pais." }
  ],

  concorrentes_T9: {
    lei: "COMPANY_CLAIM != REGULATORY_FACT — vale inclusive para a ADAMA",
    ADAMA_Italia: { ACCESS: "ACCESS_OK no navegador", BROWSER_REQUIRED: "YES", WAF: "YES (403 ao curl com cabecalhos completos)", CONTENT_AVAILABLE: "YES", amostra: "artigo 03/06/2026 sobre Sonavio®/bifenox, inibidor de PPO, resistencia de infestantes em horticolas/tomate", estado: "BROWSER_RENDERED_EXTRACT" },
    Bayer_Crop_Science_Italia: { ACCESS: "ACCESS_OK no navegador", BROWSER_REQUIRED: "YES", WAF: "YES", CONTENT_AVAILABLE: "YES", amostra: "Mais Lab — podcast sobre diserbo e resistencia de infestantes em milho, com quatro tecnicos nomeados e a marca Dekalb", estado: "BROWSER_RENDERED_EXTRACT" },
    Syngenta_Italia: { ACCESS: "WAF_CHALLENGE", detalhe: "pagina de verificacao anti-bot nao foi vencida em 6 segundos de espera no navegador", CONTENT_AVAILABLE: "NO nesta tentativa", VERDICT: "NÃO SEI — nao vira RED" },
    achado_comparativo: "ADAMA e Bayer estao, no mesmo ano, comunicando o MESMO problema — resistencia de plantas daninhas a herbicida — em culturas diferentes. Observacao direta de duas paginas datadas, sem inferencia.",
    aviso_de_preservacao: "os dois extratos NAO sao RAW_PRESERVED. Sao BROWSER_RENDERED_EXTRACT: o site recusa qualquer cliente sem navegador, entao os bytes servidos nao puderam ser guardados."
  },

  tres_fontes_sem_url: {
    "IT-T3-003": { resultado: "URL ENCONTRADA, AMOSTRA NAO", URL: "https://simfito.regione.campania.it/", rota_dos_boletins: "https://simfito.regione.campania.it/bollettini", estado: "SOURCE_REAL_BUT_REQUIRES_LOGIN — a pagina pede login e aceite de licenca", classificacao: "PUBLIC_CAPABILITY", regra_aplicada: "NAO se tentou contornar autenticacao", VERDICT: "NÃO SEI", nota: "a landing publica descreve uma plataforma GIS do Servizio Fitosanitario da Campania. A existencia esta provada; a entrega, nao." },
    "IT-T3-010": { resultado: "RESOLVIDA COM AMOSTRA", URL: "http://www.apol.it", causa_do_erro_anterior: "o site e HTTP, nao HTTPS — o teste com https:// devolvia zero", VERDICT: "GREEN" },
    "IT-T7-012": { resultado: "URL ENCONTRADA, IDENTIDADE PROVADA, AMOSTRA NAO", URL: "https://pica.cavit.it/", identidade: "PICA e mesmo a Piattaforma Integrata Cartografica Agri-vitivinicola, e o vinculo com a CAVIT esta PROVADO — o sistema mora no dominio cavit.it", estado: "OPERATIONAL_DATA = NOT_PUBLICLY_ACCESSIBLE — ha AREA RISERVATA com login", classificacao: "PUBLIC_CAPABILITY", regra_aplicada: "NAO se tentou contornar autenticacao. Resultado negativo e resultado valido.", VERDICT: "NÃO SEI" }
  },

  fontes_que_continuam_sem_amostra: {
    Syngenta_Italia: "WAF_CHALLENGE no navegador",
    ISMEA_Mercati: "rota do banco de precos ENCONTRADA (4 vistas: prodotto/varieta, prodotto/piazza, prodotto/piazza-condizione, piazza/prodotto), mas o painel nao renderizou a tabela nesta sessao e nenhuma chamada de dados apareceu no trafego. Criterio de parada aplicado. VERDICT = NÃO SEI.",
    ICQRF: "nao alcancada nesta rodada — sem tempo, nao por bloqueio",
    cooperativas_P3: "Agrintesa, Apofruit, Apo Conerpo, Ortofruit, VOG, Melinda, CAI nao foram testadas nesta rodada. Continuam ROUTE_PROBED sem amostra.",
    CNR_IRIS_e_SIRFI: "nao alcancadas nesta rodada"
  },

  leis_confirmadas_em_campo: [
    "ROUTE_NOT_FOUND != SOURCE_BLOCKED — confirmada TRES vezes nesta rodada: ARIF (outro dominio), APOL (HTTP e nao HTTPS), FEM OpenPub (outro host)",
    "BROWSER_REQUIRED != SOURCE_UNAUTOMATABLE — ADAMA e Bayer exigem navegador e continuam automatizaveis com navegador",
    "AGROCLIMATIC_SIGNAL != PEST_OCCURRENCE — aplicada a ARPAV e ao SIAS",
    "COMPANY_CLAIM != REGULATORY_FACT — aplicada a ADAMA e a Bayer",
    "ACCESS_OK != SOURCE_ANALYTICALLY_USEFUL — por isso IT-T3-008 ficou YELLOW: o PDF esta preservado, mas a secao fitossanitaria nao foi lida"
  ]
};

d.estados_de_cobertura_2026_09_07 = {
  porque_existe: "quatro estados separados, nunca colapsados. Atualizado apos a rodada browser.",
  ROTAS_NO_CATALOGO: 54,
  ROUTE_PROBED: { n: 54, o_que_significa: "porta medida. Subiu de 51 para 54: as tres sem URL ganharam endereco nesta rodada." },
  SAMPLE_CAPTURED: { n: 16, o_que_significa: "documento real obtido alem da homepage", detalhe: "9 da rodada anterior + 7 novas com RAW + 2 extratos de navegador que NAO contam como RAW" },
  RAW_PRESERVED: { n: 14, o_que_significa: "bytes no disco com MIME/BYTES/SHA256 conferido contra o arquivo", detalhe: "7 da rodada anterior + 7 novas" },
  BROWSER_RENDERED_EXTRACT: { n: 2, quais: ["IT-T9-008 ADAMA", "IT-T9-002 Bayer"], o_que_significa: "conteudo lido do DOM renderizado; os bytes servidos NAO puderam ser guardados porque o site recusa cliente sem navegador. NAO equivale a RAW_PRESERVED." },
  ANALYTICALLY_CLASSIFIED: { n: 16, o_que_significa: "tem veredito, prioridade, recorrencia, o que prova e o que NAO prova" },
  NUNCA_TOCADAS: { n: 0, nota: "as tres que faltavam endereco foram todas localizadas nesta rodada" },
  PROBADAS_SEM_AMOSTRA: { n: 38 },
  aviso: "SAMPLE_CAPTURED (16) = RAW_PRESERVED (14) + BROWSER_RENDERED_EXTRACT (2). Nao somar duas vezes."
};

d.counts.tested_this_mission = 54;
d.counts.amostras_preservadas = 14;
d.counts.GREEN = 9;
d.counts.YELLOW = 5;
d.counts.RED = 0;
d.counts.NAO_SEI_com_amostra = 2;
d.counts.NOT_TESTED = 38;
d.counts.nota_de_contagem = "placar sobre as 16 fontes com amostra e classificacao. As outras 38 tiveram a porta medida e NAO tem veredito analitico — ficam ROUTE_PROBED.";
d.counts.verified_by = "scripts/italy_contract_test.mjs — rodado apos a rodada browser";

d.matriz_regiao_x_cultura = {
  metodo: "so entra celula com FONTE PROVADA (amostra preservada ou extrato) nesta ou na rodada anterior. Nada inferido.",
  PUGLIA: { OLIVE: "IT-T3-010 APOL Lecce — sinal de campo semanal por comprensorio · IT-T7-002 MASAF: 62 OP na regiao", GERAL: "IT-T3-008 ARIF/Agrometeopuglia — semanal agromet+fitossanitario (secao fito nao lida)", DURUM_WHEAT: "AINDA VAZIO" },
  SICILIA: { CLIMA: "IT-T2-004 SIAS — diario por estacao", FITOSSANITARIO: "AINDA VAZIO" },
  CAMPANIA: { "AGRUMI, DRUPACEE, POMACEE, OLIVO": "IT-T3-002 — boletim semanal por provincia, com limiar e substancia ativa", SISTEMA: "IT-T3-003 SIMFITO existe mas pede login" },
  "EMILIA-ROMAGNA": { CLIMA: "IT-T2-001 ARPAE — semanal, arquivo de 6 anos" },
  VENETO: { CLIMA: "IT-T2-002 ARPAV — 32 zonas (conteudo nao lido)" },
  TOSCANA: { OLIVE: "IT-T3-005 Terre dell'Etruria — 139 pontos, mosca dell'olivo" },
  BASILICATA: { OLIVE: "IT-T5-003 bilancio fitossanitario anual (retrospectivo)" },
  MARCHE: { OLIVE: "IT-T5-003 bilancio fitossanitario anual (retrospectivo)" },
  "TRENTINO-ALTO ADIGE": { APPLE: "IT-T3-011 AGRIOS — disciplinar 2026 de pomacee", VINE: "IT-T7-012 PICA existe mas o dado e privado", CIENCIA: "IT-T5-002 FEM OpenPub" },
  PIEMONTE: { nada: "sem fonte propria provada" },
  NACIONAL: { TODAS: "IT-T1-001 ISTAT (233 culturas por provincia) · IT-T4-001 registro de autorizacoes · IT-T7-002 MASAF OP · IT-T10-002 BMTI (mais e grano tenero)" },
  leitura_das_culturas_prioritarias: {
    OLIVE: "MUITO melhor: Puglia (sinal semanal), Toscana (139 pontos), Basilicata e Marche (retrospectivo), + 103 OP de azeite no MASAF",
    MAIZE: "parcial: preco (BMTI), producao (ISTAT), comunicacao de concorrente (Bayer). Sem sinal de campo.",
    VINE: "fraco em sinal: PICA e privado; ha ciencia (FEM) e producao (ISTAT)",
    APPLE: "regra tecnica (AGRIOS) e ciencia (FEM). Sem sinal de campo.",
    DURUM_WHEAT: "CONTINUA A MAIOR LACUNA — nenhuma fonte nova cobre. So preco e producao nacional."
  }
};

writeFileSync(p, JSON.stringify(d, null, 1));
console.log("master atualizado");
