#!/usr/bin/env node
/* O INVENTARIO DO ACERVO · o que ja esta no repo, quanto, de quando, e em que LUGAR deve viver.

       node pacote/acervo_inventario.mjs              # escreve os quatro ficheiros
       node pacote/acervo_inventario.mjs --conferir   # 0 = os commitados sao os destes ficheiros

   le     italia-portale/client/{italy-label-intelligence, italy-handoff-v21, italy-v21, italy-ingested,
          italy-catalog, italy-real-intelligence, italy-demo-data, meeting-intelligence-snapshot,
          italy-casa, italy-canonical-windows, adama-relevance, italy-label-verdicts}.js
          italia-portale/client/portale.html   (so para saber que ficheiros o portal carrega)
   grava  docs/acervo/INVENTARIO-ACERVO.json
          docs/acervo/INVENTARIO-ACERVO.md
          docs/intelligence/acervo/ENTRADA-INTELLIGENCE-ACERVO.json
          docs/intelligence/acervo/INSUMOS-DECLARADOS-ACERVO.json

   PORQUE EXISTE (D114 + correcao do dono, 27/09 16:50)
   «os numeros que estavam no portal antigo nao eram mentiras ... cheque o que ja tem e nao precisa
   coletar novamente, apenas organizar nos lugares novos e corretos» — e a pergunta: «tudo esta
   passando pelo processo correto? coleta, inteligencia e casco?»

   A LEI D97: COLLECTION -> SALA -> INTELLIGENCE (e INTELLIGENCE TOOLS) -> POTE -> CASCO. Dado
   coletado nunca vai direto do repo para o casco. Cada conjunto recebe UMA de cinco classes:

     a  SAIDA_DE_INTELLIGENCE_TOOL   saida selada de ferramenta; vai ao pote como produto dela
     b  REFERENCIA_OFICIAL           registro, catalogo, estatistica oficial; e INSUMO da Intelligence
     c  ITEM_COLETADO                anuncio, voz, preco, ciencia, noticia, boletim; passa pela Intelligence
     d  FORA                         demo, simulado, CLIENT_SAFE=false, oportunidade nao provada,
                                     interpretacao feita fora da Intelligence
     NAO_SEI                         nao se sabe; o motivo vai escrito

   A classe e DECLARADA aqui, conjunto a conjunto, com o motivo — nao adivinhada por nome. Um
   conjunto novo que apareca num destes ficheiros sem regra aqui NAO e classificado em silencio:
   o inventario recusa-se a escrever (ver `semRegra`).

   O QUE ESTE FICHEIRO NAO FAZ: nao coleta, nao corrige registro, nao cruza, nao promove. Conta,
   data e arruma. A ENTRADA da Intelligence e uma lista normalizada para a PROXIMA rodada ler; nada
   dela vai ao casco. */
import fs from 'node:fs';
import path from 'node:path';
import vm from 'node:vm';
import crypto from 'node:crypto';
import { fileURLToPath } from 'node:url';

const RAIZ = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const CLIENTE = 'italia-portale/client';
const SAIDA_JSON = 'docs/acervo/INVENTARIO-ACERVO.json';
const SAIDA_MD = 'docs/acervo/INVENTARIO-ACERVO.md';
const SAIDA_ENTRADA = 'docs/intelligence/acervo/ENTRADA-INTELLIGENCE-ACERVO.json';
const SAIDA_INSUMOS = 'docs/intelligence/acervo/INSUMOS-DECLARADOS-ACERVO.json';
const NAO_SEI = 'NAO SEI';

/* (b) · A REFERENCIA OFICIAL COMO INSUMO DECLARADO DA INTELLIGENCE (R7/R8).
   Nao se copia dado nenhum: aponta-se o conjunto (ficheiro, global, contagem, sha do ficheiro) e diz-se
   por que chaves ele junta e que pergunta de cruzamento ele permite. LEITORES sao [ficheiro, padrao]:
   a linha e PROCURADA a cada corrida — um leitor que desapareca fica «NAO ENCONTRADO», nunca herdado. */
const INSUMO = {
  [`italy-handoff-v21.js::productRelationships`]: {
    JUNCAO: ['REGISTRATION_NUMBER', 'PRODUCT_NAME', 'CROP_ON_LABEL', 'CROP_IDS', 'TARGET_ON_LABEL', 'TARGET_KIND', 'ISSUE_IDS', 'LINK_STRENGTH'],
    PERGUNTA: 'o produto ADAMA serve para esta praga nesta cultura? (portfolio ADAMA × cultura × alvo, pelo rotulo)',
    LEITORES: [['motor/v21_crossings.py', "PRODUCT-RELATIONSHIPS.json"], ['motor/v21_oportunidades.py', "cs['PRODUCT-RELATIONSHIPS'], 'CROP_IDS'"],
      ['italia-portale/client/italy-app-model.js', 'RAW.HANDOFF_V21.productRelationships']] },
  [`italy-handoff-v21.js::productsRegulatory`]: {
    JUNCAO: ['REGISTRATION_NUMBER', 'NAME', 'ACTIVE_INGREDIENTS', 'STATUS', 'EXPIRY', 'AUTHORIZATION_HOLDER'],
    PERGUNTA: 'que produtos ADAMA estao autorizados hoje, com que substancia, ate quando',
    LEITORES: [['motor/v21_adama_registro_validar.py', 'PRODUCTS-REGULATORY.json'], ['motor/v21_oportunidades.py', "cs['PRODUCTS-REGULATORY']"],
      ['italia-portale/client/italy-app-model.js', "build('productsRegulatory'"]] },
  [`italy-handoff-v21.js::productActiveIngredients`]: {
    JUNCAO: ['PRODUCT_ID', 'REGISTRATION_NUMBER', 'ACTIVE_INGREDIENT_ID', 'ACTIVE_INGREDIENT'],
    PERGUNTA: 'a ponte produto × substancia: liga o cruzamento por substancia (o que a R7 faz) ao produto ADAMA',
    LEITORES: [['motor/v21_oportunidades.py', "'PRODUCT-ACTIVE-INGREDIENTS'"]] },
  [`italy-handoff-v21.js::activeIngredients`]: {
    JUNCAO: ['ID', 'NAME', 'NORMALIZED_NAME', 'HRAC', 'FRAC', 'IRAC', 'EU_STATE', 'EU_EXPIRATION_OF_APPROVAL'],
    PERGUNTA: 'modo de acao e estado UE da substancia (resistencia, rotacao, preparacao regulatoria)',
    LEITORES: [['motor/v21_oportunidades.py', "'ACTIVE-INGREDIENTS'"]] },
  [`italy-handoff-v21.js::regulatoryFutureFacts`]: {
    JUNCAO: ['ACTIVE_INGREDIENT_ID', 'EU_EXPIRATION_OF_APPROVAL', 'ITALIAN_REGISTRATIONS'],
    PERGUNTA: 'que substancias ADAMA tem data europeia a frente (data regulatoria NAO vira janela agronomica)',
    LEITORES: [['motor/v21_oportunidades.py', "'REGULATORY-FUTURE-FACTS'"]] },
  [`italy-handoff-v21.js::productsCommercial`]: {
    JUNCAO: ['MATCHED_REGULATORY_ID', 'REGISTRATION_NUMBER_ON_PAGE', 'NAME', 'CATALOG_STATUS'],
    PERGUNTA: 'o produto autorizado existe no catalogo para vender? (autorizacao nao e catalogo)',
    LEITORES: [['motor/v21_crossings.py', 'PRODUCTS-COMMERCIAL.json'], ['motor/v21_comercial.py', "p.get('MATCHED_REGULATORY_ID')"]] },
  [`italy-handoff-v21.js::cropEconomics`]: {
    JUNCAO: ['CROP_IDS', 'GEOGRAPHY_CODE', 'YEAR', 'INDICATOR', 'VALUE', 'UNIT'],
    PERGUNTA: 'peso economico da cultura na regiao (contexto, nunca prioridade sozinho)',
    LEITORES: [['motor/v21_crossings.py', 'CROP-ECONOMIC-WEIGHT.json']] },
  [`italy-handoff-v21.js::resistance`]: {
    JUNCAO: ['SPECIES', 'CROP_IDS', 'ISSUE_IDS', 'MECHANISM', 'REGIONS'],
    PERGUNTA: 'ha resistencia documentada ao modo de acao deste produto nesta cultura?',
    LEITORES: [['motor/v21_crossings.py', "le('RESISTANCE.json')"], ['guarda/importar_italia.py', 'insert into public.resistencia_confirmada']] },
  [`italy-catalog.js::ITEMS`]: {
    JUNCAO: ['reg', 'name', 'matchState'],
    PERGUNTA: 'catalogo comercial ADAMA com o estado da ligacao ao registro',
    LEITORES: [] },
  [`italy-ingested.js::LINKS`]: {
    JUNCAO: ['reg', 'crop', 'target', 'doses', 'maxApp', 'interval'],
    PERGUNTA: 'dose, numero maximo e intervalo do rotulo por par cultura × alvo',
    LEITORES: [] },
};
/* Insumos que NAO estao nos ficheiros do portal mas estao no repositorio. */
const INSUMO_EXTRA = [
  { ID: 'registro-completo-ministero', FICHEIRO: 'data/samples/IT-SOURCE-SAMPLES/IT-T4-001/PROD_FTS_6_20260907.csv',
    O_QUE_E: 'o registro INTEIRO do Ministero della Salute (todos os titulares, nao so ADAMA), snapshot 07/09/2026',
    JUNCAO: ['num_registrazione', 'ragione_sociale', 'sostanze_attive', 'attivita', 'stato_amministrativo', 'data_scadenza_autorizzazione'],
    PERGUNTA: 'concorrentes registados com a MESMA SUBSTANCIA ATIVA / a mesma atividade',
    LIMITE: 'o registro nao traz cultura × alvo: «concorrentes registados para o MESMO ALVO» e NAO SEI com o que esta no repo — exige os rotulos dos concorrentes, que nao estao aqui (e nao se coleta nesta missao)',
    LEITORES: [['fontes/adama_it_intelligence.py', 'PROD_FTS_6_']] },
  { ID: 'label-intelligence-usos', FICHEIRO: 'italia-portale/client/italy-label-intelligence.js',
    O_QUE_E: 'os usos (cultura × alvo) que a Label Intelligence leu, com o estado de prova de cada par — saida de ferramenta (classe a), consumivel como insumo',
    JUNCAO: ['products[].reg', 'products[].actives', 'products[].uses[].crop', 'products[].uses[].target', 'products[].uses[].proof'],
    PERGUNTA: 'o rotulo ADAMA lido autoriza a substancia nesta cultura? (a pergunta dos 86 cruzamentos da R7)',
    LIMITE: 'a R7 ja cruza por substancia com CULTURAS_NO_ROTULO; de que ficheiro a R7 leu esse portfolio NAO SEI (o motor nao esta neste repo)',
    LEITORES: [['italia-portale/audit/etichette-gate.mjs', 'ITALY_LABEL_INTELLIGENCE'], ['pacote/pote_ferramenta_label.py', 'ITALY_LABEL_INTELLIGENCE']] },
];
function leitor([ficheiro, padrao]) {
  const p = path.join(RAIZ, ficheiro);
  if (!fs.existsSync(p)) return `${ficheiro} · NAO ENCONTRADO (ficheiro)`;
  const linhas = fs.readFileSync(p, 'utf8').split('\n');
  const i = linhas.findIndex((l) => l.includes(padrao));
  return i < 0 ? `${ficheiro} · NAO ENCONTRADO («${padrao}»)` : `${ficheiro}:${i + 1}`;
}

const FICHEIROS = [
  ['italy-label-intelligence.js', 'ITALY_LABEL_INTELLIGENCE'],
  ['italy-handoff-v21.js', 'ITALY_HANDOFF_V21'],
  ['italy-v21.js', 'ITALY_HANDOFF_V21'],
  ['italy-ingested.js', 'ITALY_INGEST'],
  ['italy-catalog.js', 'ITALY_CATALOG'],
  ['italy-real-intelligence.js', 'ITALY_REAL'],
  ['italy-demo-data.js', 'ITALY_DEMO'],
  ['meeting-intelligence-snapshot.js', 'MEETING_INTELLIGENCE'],
  ['italy-casa.js', 'ITALY_CASA'],
  ['italy-canonical-windows.js', 'ITALY_CANONICAL'],
  ['adama-relevance.js', 'ADAMA_RELEVANCE'],
  ['italy-label-verdicts.js', 'ITALY_LABEL_VERDICTS'],
];

/* O LEITOR DA INTELLIGENCE QUE CADA ESPECIE DE ITEM COLETADO ENCONTRA. O compartimento e o do contrato
   POTE_INTELLIGENCE_CASCO/v2 (docs/casco/r7/POTE-R7.json → CONTRATO_CHAVES). O motor que produz o pote
   (SOURCE_HEAD.MOTOR a5db06c4, ramo int-intake-g0v4-v1) NAO esta neste repositorio: por isso
   LEITOR_NO_REPO diz o que existe AQUI, e nada mais. */
const PORTA = 'admissao/admissao.py (a porta de admissao por par item × universo) → Sala → G0';
const CAMINHO = {
  anuncio: { COMPARTIMENTO: 'competitors', PASSO: 'G0 → crossing concorrente × produto × cultura (T4_REGISTRATION_EVIDENCE_ID exigido)' },
  voz: { COMPARTIMENTO: 'voices', PASSO: 'G0 → SPEAKER_ID/QUOTE_OR_TRANSCRIPT/FACT_TIME' },
  transcricao: { COMPARTIMENTO: 'voices', PASSO: 'G0 → a transcricao e a prova de uma voz, nao uma voz' },
  preco: { COMPARTIMENTO: 'market', PASSO: 'G0 → CROP_ID/MARKET_PLACE_ID/PERIOD/PRICE/UNIT' },
  ciencia: { COMPARTIMENTO: 'science', PASSO: 'G0 → DOI/MOLECULE/CROP_ID/ISSUE_ID (ciencia nao vira incidencia de campo)' },
  boletim: { COMPARTIMENTO: 'windows · archive', PASSO: 'G0 → o mesmo caminho dos boletins T3 que a R7 ja leu (sonda, cruzamentos X2/X3)' },
  agromet: { COMPARTIMENTO: 'windows', PASSO: 'G0 → condicao agrometeorologica e contexto, nao janela' },
  noticia: { COMPARTIMENTO: 'archive', PASSO: 'G0 → publicacao nao vira fact time' },
  evento: { COMPARTIMENTO: 'future · archive', PASSO: 'G0 → FATO_PRESENTE_SOBRE_O_FUTURO (data do evento ≠ janela)' },
  sinal_de_campo: { COMPARTIMENTO: 'windows', PASSO: 'G0 → sinal de campo com fonte e data' },
};

/* AS REGRAS, conjunto a conjunto. chave = '<ficheiro>::<caminho do conjunto>'.
   DUP = o mesmo registo existe, pelo ID, no conjunto canonico (italy-handoff-v21.js, V21-ef6e7e,
   o que o portal carrega) — medido abaixo, nao suposto. */
const H = 'italy-handoff-v21.js::';
const R = {
  /* a · a Label Intelligence selada */
  'italy-label-intelligence.js::products': { C: 'a', M: 'leitura selada do rotulo oficial pela ferramenta pilot-label-intelligence (selo CONTENT_SHA256 recalculado)' },
  'italy-label-intelligence.js::objects': { C: 'a', M: 'objetos de registro da mesma ferramenta (diferencas entre snapshots oficiais)' },
  'italy-label-intelligence.js::versions': { C: 'a', M: 'as versoes do registro oficial que a ferramenta leu — procedencia da propria ferramenta' },
  'italy-label-intelligence.js::crop_check_list': { C: 'a', M: 'agregado selado da ferramenta (crop_check)' },
  'italy-label-intelligence.js::pair_check_list': { C: 'a', M: 'agregado selado da ferramenta (pair_check)' },

  /* b · referencia oficial, insumo da Intelligence */
  [H + 'productsRegulatory']: { C: 'b', M: 'registro ministerial dos 163 produtos ADAMA (Ministero della Salute)' },
  [H + 'productsCommercial']: { C: 'b', M: 'catalogo comercial ADAMA Italia (51)' },
  [H + 'productRelationships']: { C: 'b', M: 'pares produto × cultura × alvo lidos nos rotulos — o portfolio que os cruzamentos pedem' },
  [H + 'productActiveIngredients']: { C: 'b', M: 'ponte produto × substancia ativa do registro' },
  [H + 'activeIngredients']: { C: 'b', M: 'substancias ativas com estado de aprovacao UE (EU pesticides database / CELEX)' },
  [H + 'regulatoryFutureFacts']: { C: 'b', M: 'datas de expiracao de aprovacao UE por substancia — referencia oficial (data regulatoria nao vira janela)' },
  [H + 'regulatoryFuture']: { C: 'b', M: 'atos regulatorios futuros com fonte oficial; CLIENT_SAFE maioritariamente false: so como procedencia' },
  [H + 'cropEconomics']: { C: 'b', M: 'estatistica oficial (ISTAT/Eurostat) de peso economico da cultura' },
  [H + 'resistance']: { C: 'b', M: 'casos de resistencia com autoridade e citacao (GIRE/HRAC)' },
  [H + 'researchers']: { C: 'b', M: 'diretorio de investigadores (ORCID/OpenAlex) — entidade de referencia, nao item' },
  [H + 'sources']: { C: 'b', M: 'registro de fontes — procedencia, nao dado' },
  [H + 'publicChannels']: { C: 'b', M: 'registro de canais publicos — procedencia das vozes, nao voz' },

  /* c · item coletado: passa pela Intelligence */
  [H + 'competitorActivities']: { C: 'c', M: 'anuncios/atividade de concorrentes (Meta Ad Library)', T: 'anuncio' },
  [H + 'publicVoices']: { C: 'c', M: 'vozes publicas com pessoa, canal e data', T: 'voz' },
  [H + 'transcripts']: { C: 'c', M: 'transcricoes de video (a prova das vozes)', T: 'transcricao' },
  [H + 'marketObservations']: { C: 'c', M: 'observacoes de preco com publicador e periodo', T: 'preco' },
  [H + 'scienceRecords']: { C: 'c', M: 'registos de ciencia com DOI/autor/instituicao', T: 'ciencia' },
  [H + 'scienceCorpus']: { C: 'c', M: 'corpus cientifico colhido (OpenAlex); IDs distintos dos 88 scienceRecords', T: 'ciencia' },
  [H + 'fieldBulletins']: { C: 'c', M: 'boletins fitossanitarios regionais', T: 'boletim' },
  [H + 'agrometConditions']: { C: 'c', M: 'condicoes agrometeorologicas publicadas', T: 'agromet' },
  [H + 'news']: { C: 'c', M: 'noticias da imprensa tecnica', T: 'noticia' },
  [H + 'events']: { C: 'c', M: 'eventos do setor com data e organizador', T: 'evento' },
  [H + 'futureEvents']: { C: 'c', M: 'RECORTE de events (DOUBLE_COUNT_WARNING do proprio pacote)', T: 'evento', DUP_DE: H + 'events' },
  [H + 'currentFieldSignals']: { C: 'c', M: 'sinais de campo correntes com fonte', T: 'sinal_de_campo' },

  /* d · fora do casco */
  [H + 'opportunities']: { C: 'd', M: 'oportunidades do motor V2.1: CLIENT_SAFE=false em todas, nao provadas, nao sao da Intelligence do pote' },
  [H + 'opportunityEvidence']: { C: 'd', M: 'evidencia das 43 oportunidades V2.1 — vai com elas' },
  [H + 'clientSafeCrossings']: { C: 'd', M: 'cruzamentos V2.1: CLIENT_SAFE=false em todos (o nome do conjunto nao e o estado dos registos)' },
  [H + 'relationships']: { C: 'd', M: 'ligacoes dos mesmos 19 cruzamentos V2.1, CLIENT_SAFE=false' },
  [H + 'futureSignals']: { C: 'd', M: 'interpretacao SINTONIA feita fora da Intelligence (SINTONIA_INTERPRETATION)' },
  [H + 'opportunityRules']: { C: 'd', M: 'regras do motor V2.1 (arquetipos, estados) — configuracao, nao dado' },

  /* italy-v21.js · build ANTERIOR (V21-843baf) do mesmo pacote, nao carregada pelo portal */
  'italy-v21.js::MANIFEST': { C: 'd', M: 'manifesto de uma build anterior do pacote — nao e dado' },

  /* italy-ingested.js · o pack de design de 02/09; os registos com o mesmo ID estao no handoff */
  'italy-ingested.js::PRODUCTS': { C: 'b', M: 'registro ministerial (copia do design pack)', DUP_DE: H + 'productsRegulatory', CHAVE: ['reg', 'REGISTRATION_NUMBER'] },
  'italy-ingested.js::LINKS': { C: 'b', M: 'pares produto × cultura × alvo com dose do rotulo (design pack)' },
  'italy-ingested.js::CROPS': { C: 'b', M: 'vocabulario de culturas com contagem de produtos no rotulo' },
  'italy-ingested.js::COMP_ACTIVITIES': { C: 'c', M: 'anuncios Meta e videos organicos (copia do design pack)', T: 'anuncio', DUP_DE: H + 'competitorActivities' },
  'italy-ingested.js::COMP_COMPANIES': { C: 'd', M: 'agregado por empresa derivado fora da Intelligence (contagens de anuncios)' },
  'italy-ingested.js::COMP_PRODUCTS': { C: 'd', M: 'agregado por produto concorrente derivado fora da Intelligence' },
  'italy-ingested.js::SCIENCE': { C: 'c', M: 'ciencia (copia)', T: 'ciencia', DUP_DE: H + 'scienceRecords' },
  'italy-ingested.js::RESEARCHERS': { C: 'b', M: 'diretorio (copia)', DUP_DE: H + 'researchers' },
  'italy-ingested.js::RESISTANCE': { C: 'b', M: 'resistencia (copia)', DUP_DE: H + 'resistance' },
  'italy-ingested.js::THEMES': { C: 'd', M: 'agregados de tema derivados fora da Intelligence' },
  'italy-ingested.js::VOICES': { C: 'c', M: 'vozes (copia)', T: 'voz', DUP_DE: H + 'publicVoices' },
  'italy-ingested.js::CHANNELS': { C: 'b', M: 'canais (copia)', DUP_DE: H + 'publicChannels' },
  'italy-ingested.js::SOURCES': { C: 'b', M: 'registro de fontes (copia parcial)', DUP_DE: H + 'sources', CHAVE: ['SOURCE_ID', 'SOURCE_ID'] },
  'italy-ingested.js::PEOPLE': { C: 'b', M: 'pessoas com evidencia de identidade e papel — entidade de referencia' },
  'italy-ingested.js::EVENTS': { C: 'c', M: 'eventos (copia)', T: 'evento', DUP_DE: H + 'events' },
  'italy-ingested.js::NEWS': { C: 'c', M: 'noticias (copia)', T: 'noticia', DUP_DE: H + 'news' },
  'italy-ingested.js::MARKET': { C: 'c', M: 'precos (copia)', T: 'preco', DUP_DE: H + 'marketObservations' },
  'italy-ingested.js::MARKET_SUMMARIES': { C: 'd', M: 'sumarios de texto por cultura — interpretacao fora da Intelligence' },
  'italy-ingested.js::CROP_WINDOWS': { C: 'd', M: 'janelas montadas a mao a partir de boletins e da norma — interpretacao fora da Intelligence' },
  'italy-ingested.js::OPPORTUNITIES': { C: 'd', M: 'tres fichas de oportunidade escritas a mao (LEGACY_CASE_ID IT-HERO)' },
  'italy-ingested.js::FUTURE_SIGNALS': { C: 'd', M: 'interpretacao fora da Intelligence' },

  'italy-catalog.js::ITEMS': { C: 'b', M: 'catalogo comercial ADAMA Italia com o estado da ligacao ao registro' },

  /* ITALY_REAL: registos escritos a mao a partir do brief do projeto */
  'italy-real-intelligence.js::RESEARCHERS': { C: 'NAO_SEI', M: 'transcrito a mao do brief (LAST_CHECKED 2026-09-01): sem URL, sem COLLECTED_AT, sem observacao bruta — nao se sabe se e coleta nem de quando' },
  'italy-real-intelligence.js::SCIENCE': { C: 'NAO_SEI', M: 'idem: transcrito do brief, sem URL nem data de coleta' },
  'italy-real-intelligence.js::NEWS': { C: 'NAO_SEI', M: 'idem: transcrito do brief; datas sem ano («01 Sep»)' },
  'italy-real-intelligence.js::BULLETINS': { C: 'NAO_SEI', M: 'idem: contagens de boletins transcritas, sem o boletim' },
  'italy-real-intelligence.js::COMPETITOR_REAL': { C: 'NAO_SEI', M: 'idem: REAL_DERIVED do dataset Meta, sem ID do anuncio' },
  'italy-real-intelligence.js::EVENTS_EXTRA': { C: 'NAO_SEI', M: 'idem' },
  'italy-real-intelligence.js::SOURCES_EXTRA': { C: 'NAO_SEI', M: 'idem' },
  'italy-real-intelligence.js::REALITY': { C: 'd', M: 'etiquetas de estado para a demo (REAL_DATA_AVAILABLE...) — nao e dado' },

  'meeting-intelligence-snapshot.js::CASES': { C: 'd', M: 'os 43 casos do motor V2.1 (07/09): oportunidades nao provadas, nao sao da Intelligence do pote' },
  'italy-canonical-windows.js::windows': { C: 'd', M: 'janelas EXPECTED_NORM montadas fora da Intelligence (nenhuma CONFIRMED, dito no proprio ficheiro)' },
  'italy-label-verdicts.js::VERIFIED': { C: 'NAO_SEI', M: 'vereditos de uma leitura dos rotulos (02/09) sem selo nem ferramenta nomeada — nao se sabe se e saida de ferramenta' },
  'italy-label-verdicts.js::NOT_FOUND': { C: 'NAO_SEI', M: 'idem' },
};
/* italy-v21.js: toda colecao herda a classe da familia do handoff, e e DUPLICADO dela (build anterior). */
const V21_FAMILIA = {
  'products.regulatory': 'productsRegulatory', 'products.commercial': 'productsCommercial',
  'products.relationships': 'productRelationships', activeIngredients: 'activeIngredients',
  'products.activeIngredients': 'productActiveIngredients', regulatoryFutureFacts: 'regulatoryFutureFacts',
  windows: null, fieldSignals: 'fieldBulletins', cropEconomicWeight: 'cropEconomics', market: 'marketObservations',
  competitors: 'competitorActivities', science: 'scienceRecords', researchers: 'researchers', resistance: 'resistance',
  voices: 'publicVoices', channels: 'publicChannels', regulatoryFuture: 'regulatoryFuture', agromet: 'agrometConditions',
  events: 'events', futureEvents: 'futureEvents', opportunities: 'opportunities', futureSignals: 'futureSignals',
  sources: 'sources', news: 'news', transcripts: 'transcripts', crossings: 'clientSafeCrossings', relationships: 'relationships',
};
/* ITALY_DEMO e ITALY_CASA: blocos inteiros, uma regra por ficheiro (ver `blocos`). */
const DEMO_M = 'pacote de demonstracao (ITALY-DEMO-PROVENANCE-MATRIX.md): fixtures locais, nao dado — FORA do casco';
const CASA = {
  AUTORIZACOES: ['b', 'contagens do registro ministerial feitas por superficie/it_casa_dados.py — referencia; o casco so a mostra via pote'],
  COBERTURA: ['d', 'medida de cobertura de uma leitura fora da Intelligence'],
  DESTAQUE: ['d', 'destaque montado fora da Intelligence'],
  EVIDENCIA: ['d', 'regra de apresentacao'],
  FONTES: ['d', 'contagem de fontes da camada humana'],
  OPPORTUNITA_ATTUALI: ['d', 'as 43 oportunidades V2.1 (CLIENT_SAFE=false)'],
  RADAR_FUTURO: ['d', 'radar futuro montado sobre o V2.1, fora da Intelligence'],
  REVOGADO_X_SCADUTO: ['b', 'estado administrativo do registro (revogado × scaduto)'],
  SENSORES: ['d', 'sensores humanos julgados fora da Intelligence'],
  SINAIS_DE_CAMPO: ['d', 'cartao de sinais de campo da camada humana'],
  LABELS: ['d', 'rotulos IT/EN — vocabulario, nao dado'],
};

/* ── ler ─────────────────────────────────────────────────────────────── */
const sha = (buf) => crypto.createHash('sha256').update(buf).digest('hex');
function carregar(ficheiro) {
  const bruto = fs.readFileSync(path.join(RAIZ, CLIENTE, ficheiro));
  const win = { location: { search: '', hash: '' } };
  const ctx = { window: win, document: { write() {} }, console: { log() {}, warn() {}, error() {} } };
  vm.createContext(ctx);
  vm.runInContext(bruto.toString('utf8'), ctx, { filename: ficheiro });
  return { win, sha: sha(bruto), bytes: bruto.length };
}
const HTML = fs.readFileSync(path.join(RAIZ, CLIENTE, 'portale.html'), 'utf8');
const carregadoPeloPortal = (f) => new RegExp('<script src="(?:\\./)?' + f.replace(/\./g, '\\.') + '"').test(HTML);

/* ── medir um conjunto ───────────────────────────────────────────────── */
const ISO = /^(\d{4})-(\d{2})-(\d{2})/;
const CAMPOS_DATA = ['PUBLICATION_DATE', 'PUBLISHED_AT', 'DATE', 'START_DATE', 'EXAMPLE_PUBLISHED_AT', 'OBSERVED_AT',
  'LAST_ACTIVITY', 'VALID_FROM', 'label_effective', 'date', 'start', 'REFERENCE_PERIOD', 'EXPIRY', 'expiry', 'REFERENCE_DATE'];
/* Valores que o proprio registo usa para dizer «nao sei a data»: nao sao data, e ficam contados. */
const SEM_DATA = new Set(['NOT_ESTABLISHED', 'NOT_KNOWN', 'NAO SEI', 'NOT_APPLICABLE', 'UNKNOWN']);
const DMY = /^(\d{2})\/(\d{2})\/(\d{4})/;
function paraIso(s) {
  s = String(s);
  let m = ISO.exec(s);
  if (m) return `${m[1]}-${m[2]}-${m[3]}`;
  if (/^\d{8}$/.test(s)) return `${s.slice(0, 4)}-${s.slice(4, 6)}-${s.slice(6, 8)}`;
  m = DMY.exec(s);
  return m ? `${m[3]}-${m[2]}-${m[1]}` : null;
}
const CAMPOS_COLETA = ['COLLECTED_AT', 'CAPTURED_AT', 'captured_at', 'OBSERVED_AT', 'COLHIDO_EM'];
/* O primeiro campo da lista que traga DATA de verdade. Um campo mais forte que so diz «nao sei»
   (PUBLICATION_DATE = NOT_ESTABLISHED) nao e escondido: fica em SEM_DATA_EM, com a contagem. */
function datas(recs, campos) {
  const semData = {};
  for (const c of campos) {
    const v = recs.map((r) => r && r[c]).filter((x) => x !== undefined && x !== null && x !== '' && typeof x !== 'object');
    if (!v.length) continue;
    const nao = v.filter((x) => SEM_DATA.has(String(x))).length;
    if (nao) semData[c] = nao;
    const iso = v.map(paraIso).filter(Boolean).sort();
    if (!iso.length) continue;
    return { CAMPO: c, COM_VALOR: iso.length, DE: recs.length, MIN: iso[0], MAX: iso[iso.length - 1], SEM_DATA_EM: semData };
  }
  return { CAMPO: NAO_SEI, COM_VALOR: 0, DE: recs.length, MIN: NAO_SEI, MAX: NAO_SEI, SEM_DATA_EM: semData };
}
function dist(recs, ...campos) {
  const d = {};
  for (const r of recs) {
    let v;
    for (const c of campos) if (r && r[c] !== undefined) { v = r[c]; break; }
    const k = v === undefined ? '(sem campo)' : String(v);
    d[k] = (d[k] || 0) + 1;
  }
  return Object.fromEntries(Object.entries(d).sort((a, b) => (a[0] < b[0] ? -1 : a[0] > b[0] ? 1 : 0)));
}
const idDe = (r) => (r && (r.ID ?? r.id ?? r.OBJETO_ID ?? r.INTELLIGENCE_OBJECT_ID ?? r.reg)) ?? null;

/* ── os conjuntos de cada ficheiro ───────────────────────────────────── */
function conjuntos(ficheiro, G) {
  const out = [];
  if (!G || typeof G !== 'object') return out;
  if (ficheiro === 'italy-v21.js') {
    if (Array.isArray(G.MANIFEST)) out.push(['MANIFEST', G.MANIFEST]);
    for (const [k, v] of Object.entries(G.collections || {})) {
      const recs = Array.isArray(v) ? v : Object.values(v || {}).find((x) => Array.isArray(x) && x.length && typeof x[0] === 'object');
      out.push(['collections.' + k, recs || []]);
    }
    return out;
  }
  for (const [k, v] of Object.entries(G)) {
    if (Array.isArray(v) && v.length && v.every((x) => x && typeof x === 'object')) out.push([k, v]);
    else if (Array.isArray(v) && v.length && ficheiro === 'italy-real-intelligence.js') out.push([k, v]);
    else if (ficheiro === 'italy-handoff-v21.js' && v && typeof v === 'object' && !Array.isArray(v) &&
      (k === 'opportunityEvidence' || k === 'opportunityRules')) out.push([k, Object.entries(v).map(([id, x]) => ({ ID: id, ...(x && typeof x === 'object' && !Array.isArray(x) ? x : { VALOR: x }) }))]);
  }
  return out;
}
function blocos(ficheiro, G) {
  /* ITALY_DEMO e ITALY_CASA nao sao colecoes de registos: medem-se por bloco. */
  const out = [];
  for (const [k, v] of Object.entries(G || {})) {
    if (typeof v === 'function' || v === undefined) continue;
    const n = Array.isArray(v) ? v.length : (v && typeof v === 'object') ? Object.keys(v).length : null;
    if (n === null || n === 0) continue;
    out.push([k, n]);
  }
  return out;
}

/* ── inventariar ─────────────────────────────────────────────────────── */
export function inventariar() {
  const fich = [], conj = [], semRegra = [], entrada = [];
  const idsCanonicos = {};
  const cargas = Object.fromEntries(FICHEIROS.map(([f]) => [f, carregar(f)]));
  const G = (f, g) => cargas[f].win[g];
  const HO = G('italy-handoff-v21.js', 'ITALY_HANDOFF_V21');
  for (const [k, v] of conjuntos('italy-handoff-v21.js', HO)) idsCanonicos[H + k] = v;

  for (const [f, g] of FICHEIROS) {
    const obj = G(f, g);
    const meta = {};
    for (const k of ['BUILD_ID', 'buildId', 'BUILT', 'BUILT_AT', 'packageBuiltAt', 'referenceDate', 'REFERENCE_DATE',
      'DATA_DATE', 'DATA_SNAPSHOT_ID', 'COLLECTED_AT', 'RUN', 'LAST_CHECKED', 'GENERATED_AT', 'MEETING_CUTOFF',
      'SOURCE_HEAD', 'DATA_DE_REFERENCIA', 'AUDIT_DATE', 'version']) if (obj && obj[k] !== undefined && typeof obj[k] !== 'object') meta[k] = obj[k];
    fich.push({ FICHEIRO: `${CLIENTE}/${f}`, GLOBAL: 'window.' + g, SHA256: cargas[f].sha, BYTES: cargas[f].bytes,
      CARREGADO_PELO_PORTAL: carregadoPeloPortal(f), DATAS_DO_FICHEIRO: meta });

    if (f === 'italy-demo-data.js') {
      for (const [k, n] of blocos(f, obj)) conj.push({ ID: `${f}::${k}`, FICHEIRO: f, CONJUNTO: k, N: n, UNIDADE: 'entradas do bloco',
        CLASSE: 'd', MOTIVO: DEMO_M, PROVENANCE: { 'SYNTHETIC_DEMO (ficheiro inteiro)': n }, CLIENT_SAFE: {}, DATA_DO_DADO: null, DATA_DE_COLETA: null, DUPLICADO_DE: null });
      continue;
    }
    if (f === 'italy-casa.js') {
      for (const [k, n] of blocos(f, obj)) {
        if (!CASA[k]) continue; /* metadados do gerador (GERADO_POR, HASHES...) nao sao conjuntos */
        conj.push({ ID: `${f}::${k}`, FICHEIRO: f, CONJUNTO: k, N: n, UNIDADE: 'chaves do bloco', CLASSE: CASA[k][0], MOTIVO: CASA[k][1],
          PROVENANCE: {}, CLIENT_SAFE: {}, DATA_DO_DADO: { CAMPO: 'DATA_DE_REFERENCIA', MIN: obj.DATA_DE_REFERENCIA, MAX: obj.DATA_DE_REFERENCIA }, DATA_DE_COLETA: null, DUPLICADO_DE: null });
      }
      continue;
    }
    if (f === 'adama-relevance.js') {
      conj.push({ ID: `${f}::VERDETTI`, FICHEIRO: f, CONJUNTO: 'VERDETTI', N: Object.keys(obj.VERDETTI || {}).length, UNIDADE: 'vereditos',
        CLASSE: 'd', MOTIVO: 'veredito de relevancia sobre as 43 oportunidades V2.1 — fora com elas', PROVENANCE: {}, CLIENT_SAFE: {},
        DATA_DO_DADO: null, DATA_DE_COLETA: null, DUPLICADO_DE: null });
      continue;
    }
    for (const [k, recs] of conjuntos(f, obj)) {
      const id = `${f}::${k}`;
      let regra = R[id];
      if (!regra && f === 'italy-v21.js' && k.startsWith('collections.')) {
        const fam = V21_FAMILIA[k.slice('collections.'.length)];
        if (fam && R[H + fam]) regra = { ...R[H + fam], M: 'build ANTERIOR V21-843baf do mesmo pacote, nao carregada pelo portal — ' + R[H + fam].M, DUP_DE: H + fam };
        else if (fam === null) regra = { C: 'd', M: 'build anterior: janelas montadas a mao (mesmas 7 do design pack) — interpretacao fora da Intelligence' };
      }
      if (!regra) { semRegra.push(id); continue; }
      const objs = recs.filter((r) => r && typeof r === 'object');
      let dup = null;
      if (regra.DUP_DE) {
        const [ka, kb] = regra.CHAVE || [null, null];
        const alvo = idsCanonicos[regra.DUP_DE] || [];
        const setB = new Set(alvo.map((r) => String(kb ? r[kb] : idDe(r))));
        const meus = objs.map((r) => String(ka ? r[ka] : idDe(r)));
        const presentes = meus.filter((x) => setB.has(x)).length;
        dup = { DE: regra.DUP_DE, MESMO_ID_LA: presentes, DE_N: meus.length, CHAVE: ka ? `${ka} = ${kb}` : 'ID', TODOS: presentes === meus.length };
      }
      conj.push({
        ID: id, FICHEIRO: f, CONJUNTO: k, N: recs.length, UNIDADE: 'registos', CLASSE: regra.C, MOTIVO: regra.M,
        PROVENANCE: dist(objs, 'PROVENANCE_CLASS', 'PROVENANCE', 'prov', 'provenance'),
        CLIENT_SAFE: dist(objs, 'CLIENT_SAFE'),
        DATA_DO_DADO: datas(objs, CAMPOS_DATA), DATA_DE_COLETA: datas(objs, CAMPOS_COLETA),
        DUPLICADO_DE: dup,
        CAMINHO: regra.C === 'c' ? { PORTA, ...CAMINHO[regra.T], LEITOR_NO_REPO: 'a porta existe (admissao/admissao.py); o passo da Intelligence NAO esta neste repositorio (motor a5db06c4, ramo int-intake-g0v4-v1)', NA_ENTRADA: !(dup && dup.TODOS) } : undefined,
      });
      /* ENTRADA: so os itens coletados do conjunto canonico (sem copia), normalizados, sem juizo. */
      if (regra.C === 'c' && !(dup && dup.TODOS)) {
        for (const r of objs) entrada.push(normalizar(f, k, regra.T, r, cargas[f].sha, HO));
      }
    }
  }
  if (semRegra.length) throw new Error('conjunto sem regra declarada (nao se classifica em silencio): ' + semRegra.join(', '));

  /* contagem por classe: unicos (sem DUPLICADO total) e com as copias */
  const cont = (lista) => {
    const o = {};
    for (const c of ['a', 'b', 'c', 'd', 'NAO_SEI']) {
      const l = lista.filter((x) => x.CLASSE === c);
      o[c] = { CONJUNTOS: l.length, REGISTOS: l.reduce((s, x) => s + (x.UNIDADE === 'registos' ? x.N : 0), 0),
        BLOCOS: l.filter((x) => x.UNIDADE !== 'registos').length };
    }
    return o;
  };
  const unicos = conj.filter((x) => !(x.DUPLICADO_DE && x.DUPLICADO_DE.TODOS));
  const shaDe = Object.fromEntries(fich.map((f) => [f.FICHEIRO.split('/').pop(), f.SHA256]));
  const naoDeclarados = unicos.filter((x) => x.CLASSE === 'b' && x.UNIDADE === 'registos' && !INSUMO[x.ID]).map((x) => x.ID);
  const insumos = {
    SCHEMA: 'INSUMOS_DECLARADOS_ACERVO/v1',
    O_QUE_E: 'a referencia oficial (classe b) que ja esta no repositorio, declarada como INSUMO da Intelligence R7/R8. Aponta; nao copia.',
    LEI: 'insumo nao e objeto do casco: no pote so aparece como objeto referenciado / procedencia de um cruzamento da Intelligence',
    GERADO_POR: 'pacote/acervo_inventario.mjs',
    INSUMOS: Object.entries(INSUMO).map(([id, d]) => {
      const c = conj.find((x) => x.ID === id);
      return { ID: id, FICHEIRO: `${CLIENTE}/${id.split('::')[0]}`, CONJUNTO: id.split('::')[1], N: c ? c.N : NAO_SEI,
        FICHEIRO_SHA256: shaDe[id.split('::')[0]] || NAO_SEI, DATA_DO_DADO: c ? c.DATA_DO_DADO : null,
        JUNCAO: d.JUNCAO, PERGUNTA: d.PERGUNTA, LEITORES_EXISTENTES: d.LEITORES.map(leitor) };
    }),
    INSUMOS_FORA_DO_PORTAL: INSUMO_EXTRA.map((d) => {
      const p = path.join(RAIZ, d.FICHEIRO);
      return { ...d, FICHEIRO_SHA256: fs.existsSync(p) ? sha(fs.readFileSync(p)) : NAO_SEI, LEITORES: undefined, LEITORES_EXISTENTES: d.LEITORES.map(leitor) };
    }),
    REFERENCIA_SEM_DECLARACAO_DE_USO: naoDeclarados,
  };
  return {
    insumos,
    inventario: {
      SCHEMA: 'INVENTARIO_ACERVO/v1',
      MISSAO: 'ACERVO-ORGANIZADO (D114 + correcao do dono 27/09 16:50)',
      LEI: 'D97 · COLLECTION -> SALA -> INTELLIGENCE (e INTELLIGENCE TOOLS) -> POTE -> CASCO; dado coletado nunca vai direto do repo para o casco',
      GERADO_POR: 'pacote/acervo_inventario.mjs',
      CLASSES: {
        a: 'SAIDA_DE_INTELLIGENCE_TOOL — vai ao pote como produto da ferramenta, com a data do snapshot, sem recalcular',
        b: 'REFERENCIA_OFICIAL — insumo da Intelligence; no pote so como objeto referenciado/procedencia',
        c: 'ITEM_COLETADO — NAO vai ao casco; passa pela Intelligence (ENTRADA-INTELLIGENCE-ACERVO.json)',
        d: 'FORA — demo, simulado, CLIENT_SAFE=false, oportunidade nao provada, interpretacao fora da Intelligence',
        NAO_SEI: 'nao se sabe; o motivo vai escrito',
      },
      CANONICO: 'italia-portale/client/italy-handoff-v21.js (V21-ef6e7e5f37eaa6e6) — o que o portal carrega; copias noutros ficheiros sao DUPLICADO_DE medido pelo ID',
      CONTAGEM_POR_CLASSE: { SEM_COPIAS: cont(unicos), COM_COPIAS: cont(conj) },
      ENTRADA_INTELLIGENCE: { FICHEIRO: SAIDA_ENTRADA, ITENS: entrada.length },
      FICHEIROS: fich,
      CONJUNTOS: conj,
    },
    entrada: {
      SCHEMA: 'ENTRADA_INTELLIGENCE_ACERVO/v1',
      MARCA: 'EXPERIMENTAL · NAO_PARA_CLIENTE',
      NAO_VAI_AO_CASCO: true,
      O_QUE_E: 'itens COLETADOS que ja estavam no repositorio (classe c do inventario), normalizados para a proxima rodada da Intelligence ler. Nada aqui foi julgado, cruzado ou promovido.',
      COMO_ENTRA: PORTA,
      GERADO_POR: 'pacote/acervo_inventario.mjs',
      ORIGEM: { FICHEIRO: `${CLIENTE}/italy-handoff-v21.js`, BUILD_ID: HO.buildId, PACOTE_DE: HO.packageBuiltAt, SHA256: cargas['italy-handoff-v21.js'].sha },
      DUPLICADOS_FORA: 'futureEvents (recorte de events) e as copias de italy-ingested.js / italy-v21.js nao entram: o mesmo ID ja esta aqui',
      POR_TIPO: Object.fromEntries(Object.entries(entrada.reduce((o, x) => { o[x.TIPO] = (o[x.TIPO] || 0) + 1; return o; }, {})).sort()),
      ITENS: entrada.length,
      LISTA: entrada,
    },
  };
}

/* Normalizar = escolher campos, nunca inventar: o que nao existe fica NAO SEI e a data REAL diz de que campo veio. */
function primeiro(r, campos) {
  for (const c of campos) { const v = r[c]; if (v !== undefined && v !== null && v !== '' && !SEM_DATA.has(String(v)) && !(Array.isArray(v) && !v.length)) return [c, v]; }
  return [null, NAO_SEI];
}
function normalizar(f, k, tipo, r, shaFicheiro, HO) {
  const CD = ['PUBLICATION_DATE', 'PUBLISHED_AT', 'DATE', 'START_DATE', 'EXAMPLE_PUBLISHED_AT', 'OBSERVED_AT', 'REFERENCE_PERIOD'];
  const [cData, vData] = primeiro(r, CD);
  const semDataEm = CD.filter((c) => r[c] !== undefined && SEM_DATA.has(String(r[c])));
  const [cCol, vCol] = primeiro(r, CAMPOS_COLETA);
  const [, url] = primeiro(r, ['SOURCE_URL', 'AD_URL', 'URL', 'OFFICIAL_URL', 'EXAMPLE_URL', 'CHANNEL_URL', 'SOURCE_URLS']);
  const [, fontes] = primeiro(r, ['SOURCE_IDS', 'SOURCE_ID']);
  return {
    ACERVO_ID: `${f}::${k}::${idDe(r)}`,
    TIPO: tipo,
    COMPARTIMENTO_DO_CONTRATO: CAMINHO[tipo].COMPARTIMENTO,
    SOURCE_IDS: Array.isArray(fontes) ? fontes : (fontes === NAO_SEI ? NAO_SEI : [fontes]),
    URL: Array.isArray(url) ? url : url,
    DATA_REAL: { CAMPO: cData || NAO_SEI, VALOR: vData, SEM_DATA_EM: semDataEm,
      NOTA: cData ? 'data do proprio registo, tal como escrita' : 'o registo nao traz data propria; REFERENCE_DATE do pacote NAO e data do facto' },
    COLHIDO_EM: { CAMPO: cCol || NAO_SEI, VALOR: vCol },
    DATA_DO_PACOTE: HO.packageBuiltAt,
    PROVENANCE: r.PROVENANCE_STATE ?? r.PROVENANCE ?? NAO_SEI,
    CLIENT_SAFE: r.CLIENT_SAFE ?? NAO_SEI,
    QA_STATUS: r.QA_STATUS ?? NAO_SEI,
    EVIDENCE_STATUS: r.EVIDENCE_STATUS ?? NAO_SEI,
    CROP_IDS: r.CROP_IDS ?? NAO_SEI,
    ISSUE_IDS: r.ISSUE_IDS ?? NAO_SEI,
    REGION_IDS: r.REGION_IDS ?? NAO_SEI,
    ORIGEM_SHA256: shaFicheiro,
  };
}

/* ── o texto humano ──────────────────────────────────────────────────── */
function md(inv) {
  const L = [];
  const C = inv.CONTAGEM_POR_CLASSE;
  L.push('# INVENTÁRIO DO ACERVO — o que já está no repositório, e o lugar certo de cada coisa', '');
  L.push('> **GERADO** por `node pacote/acervo_inventario.mjs` — não editar à mão. `--conferir` prova que este ficheiro é o dos dados.', '');
  L.push('Lei D97: `COLLECTION → SALA → INTELLIGENCE (e INTELLIGENCE TOOLS) → POTE → CASCO`. Dado coletado nunca vai direto do repo para o casco.', '');
  L.push('## As classes', '');
  for (const [k, v] of Object.entries(inv.CLASSES)) L.push(`- **${k}** — ${v}`);
  L.push('', `Conjunto canónico: ${inv.CANONICO}.`, '');
  L.push('## Contagem por classe', '', '| classe | conjuntos (sem cópias) | registos (sem cópias) | blocos | conjuntos (com cópias) | registos (com cópias) |', '|---|---:|---:|---:|---:|---:|');
  for (const c of ['a', 'b', 'c', 'd', 'NAO_SEI']) L.push(`| ${c} | ${C.SEM_COPIAS[c].CONJUNTOS} | ${C.SEM_COPIAS[c].REGISTOS} | ${C.SEM_COPIAS[c].BLOCOS} | ${C.COM_COPIAS[c].CONJUNTOS} | ${C.COM_COPIAS[c].REGISTOS} |`);
  L.push('', `Itens coletados (classe c, sem cópias) entregues à Intelligence: **${inv.ENTRADA_INTELLIGENCE.ITENS}** em \`${inv.ENTRADA_INTELLIGENCE.FICHEIRO}\`.`, '');
  L.push('## Os ficheiros', '', '| ficheiro | global | o portal carrega | datas do ficheiro | sha256 |', '|---|---|---|---|---|');
  for (const f of inv.FICHEIROS) L.push(`| \`${f.FICHEIRO.split('/').pop()}\` | \`${f.GLOBAL}\` | ${f.CARREGADO_PELO_PORTAL ? 'sim' : 'NÃO'} | ${Object.entries(f.DATAS_DO_FICHEIRO).map(([k, v]) => `${k} ${v}`).join(' · ') || 'NÃO SEI'} | \`${f.SHA256.slice(0, 12)}…\` |`);
  L.push('', '## Os conjuntos', '', '| conjunto | n | classe | data do dado (campo: min → max) | coleta | PROVENANCE | CLIENT_SAFE | cópia de | motivo |', '|---|---:|---|---|---|---|---|---|---|');
  const semd = (x) => Object.entries((x && x.SEM_DATA_EM) || {}).map(([k, v]) => ` · ${k} sem data em ${v}`).join('');
  const d = (x) => (!x ? '—' : x.CAMPO === NAO_SEI ? 'NÃO SEI' + semd(x) : `${x.CAMPO}: ${x.MIN} → ${x.MAX}${x.COM_VALOR !== undefined && x.COM_VALOR < x.DE ? ` (${x.COM_VALOR}/${x.DE})` : ''}${semd(x)}`);
  const o = (x) => Object.entries(x || {}).map(([k, v]) => `${k} ${v}`).join(' · ') || '—';
  for (const c of inv.CONJUNTOS) {
    L.push(`| \`${c.ID}\` | ${c.N}${c.UNIDADE === 'registos' ? '' : ' ' + c.UNIDADE} | **${c.CLASSE}** | ${d(c.DATA_DO_DADO)} | ${d(c.DATA_DE_COLETA)} | ${o(c.PROVENANCE)} | ${o(c.CLIENT_SAFE)} | ${c.DUPLICADO_DE ? `${c.DUPLICADO_DE.DE.split('::')[1]} (${c.DUPLICADO_DE.MESMO_ID_LA}/${c.DUPLICADO_DE.DE_N} pelo ${c.DUPLICADO_DE.CHAVE})` : '—'} | ${c.MOTIVO}${c.CAMINHO ? ` → **${c.CAMINHO.COMPARTIMENTO}** (${c.CAMINHO.PASSO})` : ''} |`);
  }
  L.push('', '## O caminho dos itens coletados (classe c)', '', `Porta: ${PORTA}. O passo da Intelligence que os lê **não está neste repositório** (motor \`a5db06c4\`, ramo \`int-intake-g0v4-v1\`): até lá, nenhum destes itens vai ao casco.`, '');
  return L.join('\n') + '\n';
}

const json = (x) => JSON.stringify(x, null, 1) + '\n';
function main() {
  const { inventario, entrada, insumos } = inventariar();
  const alvos = [[SAIDA_JSON, json(inventario)], [SAIDA_MD, md(inventario)], [SAIDA_ENTRADA, json(entrada)], [SAIDA_INSUMOS, json(insumos)]];
  if (process.argv.includes('--conferir')) {
    let dif = 0;
    for (const [p, t] of alvos) {
      const a = fs.existsSync(path.join(RAIZ, p)) ? fs.readFileSync(path.join(RAIZ, p), 'utf8') : '';
      if (a !== t) { dif++; console.log('DIFERENTE: ' + p); } else console.log('IGUAL: ' + p);
    }
    process.exit(dif ? 1 : 0);
  }
  for (const [p, t] of alvos) { fs.mkdirSync(path.dirname(path.join(RAIZ, p)), { recursive: true }); fs.writeFileSync(path.join(RAIZ, p), t); }
  const C = inventario.CONTAGEM_POR_CLASSE.SEM_COPIAS;
  console.log(`INVENTARIO · ${inventario.CONJUNTOS.length} conjuntos · a ${C.a.REGISTOS} · b ${C.b.REGISTOS} · c ${C.c.REGISTOS} · d ${C.d.REGISTOS} · NAO_SEI ${C.NAO_SEI.REGISTOS} (registos, sem copias) · ENTRADA ${entrada.ITENS}`);
}
if (process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url)) main();
