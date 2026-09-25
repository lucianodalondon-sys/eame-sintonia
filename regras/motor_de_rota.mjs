// SINTONIA EAME — O MOTOR DE ROTA DECLARATIVO
//
// O QUE ELE RESOLVE, E COMO O PROBLEMA FOI MEDIDO
// ------------------------------------------------
// `coleta/italy_pilot_collect.mjs` escolhia COMO descobrir o documento por
// `switch (sourceId)`. Medido: 20 ramos por SOURCE_ID, dos quais 7 em
// `alvosDe` e 9 em `identidade`. Uma fonte sem `case` devolvia
// «fonte sem alvo definido no piloto» — e foi exactamente isso que aconteceu
// com `IT-T3-011` na Big Collection, que eu classifiquei erradamente como
// falha da fonte quando o site respondia HTTP 200.
//
//     A FONTE NÃO É O DESPACHANTE. O CONTRATO É.
//
// O QUE ELE NÃO É, E ISSO É A LEI
// --------------------------------
//     GENERIC TRAVERSAL != UNIVERSAL PARSER.
//
// Ele resolve UMA pergunta: «que endereços devo buscar?». Não interpreta
// conteúdo, não normaliza, não decide identidade semântica. Cada espécie
// continua a ter o seu adapter onde a diferença é real.
//
// E NUNCA LÊ PROSA
// ----------------
// O contrato tem campos escritos para gente — `DISCOVERY_METHOD`,
// `RETRIEVAL_METHOD`, `classificacao_honesta`. Eles continuam lá e continuam
// úteis: são o que uma pessoa lê para perceber a fonte. Este motor **não os
// abre**. O que ele lê é `ACQUISITION`, um bloco de dados com vocabulário
// fechado.
//
//     `"DD": "dia com 2 digitos"` DESCREVE. NÃO EXECUTA.
//
// O vocabulário abaixo não foi inventado: foi DERIVADO dos sete `case` que já
// existiam, medindo o que cada um realmente faz.
//
//     3 ESTRATÉGIAS COBREM OS 7 CASOS MEDIDOS.
//     UM QUARTO NOME SERIA ARQUITETURA PARA UM CASO QUE NÃO EXISTE.

import { createHash } from "node:crypto";

export const ESTRATEGIAS = Object.freeze([
  // O endereço está escrito no contrato e não muda. Dois casos medidos:
  // `IT-T3-005` e `IT-T2-004`.
  "STATIC_ENDPOINT",
  // O endereço nasce de um molde com variáveis, e cada variável tem PROVIDER
  // declarado. Um caso medido: `IT-T2-002` (32 zonas do ARPAV).
  "TEMPLATE_ENUMERATION",
  // Abre-se um índice e extraem-se as ligações que casam com um padrão.
  // Quatro casos medidos: `IT-T3-002`, `IT-T3-008`, `IT-T3-010`, `IT-T4-001`.
  "HTML_LINK_DISCOVERY",
  // A porta de saída honesta: quando a fonte exige lógica que o vocabulário
  // finito não descreve, o contrato NOMEIA um adapter registado. Ele não
  // carrega o código — carrega o nome.
  "CUSTOM_ADAPTER",
]);

// Como uma variável de molde recebe valor. Também derivado do que existe.
export const PROVIDERS = Object.freeze([
  "LITERAL",   // valor fixo escrito no contrato
  "ENUM",      // lista fechada de valores — o `PROV: ["AV","BN",...]` já medido
  "RANGE",     // intervalo numérico inteiro, com zeros à esquerda opcionais
]);

// ── AS ESTRATÉGIAS DE IDENTIDADE ───────────────────────────────────────────
// Enxertadas de `aquisicao-detalhe-v1` na CANONICAL-MICRO-V1 (2026-09-21).
// Duas, e as duas são a mesma operação — regex com grupos → molde — sobre
// fontes de texto diferentes.
export const ESTRATEGIAS_DE_IDENTIDADE = Object.freeze([
  "FILENAME_CAPTURE",   // um padrão sobre o nome do ficheiro — o caso v1
  "CONTENT_CAPTURE",    // vários padrões, cada um sobre uma fonte de texto declarada
]);

// De onde um `CONTENT_CAPTURE` lê o texto. Vocabulário fechado, e cada
// entrada corresponde a um leitor INJECTADO pelo coletor: o motor nunca abre
// um ficheiro nem chama um programa.
export const FONTES_DE_TEXTO = Object.freeze([
  "FILENAME",     // o nome do alvo (o mesmo que FILENAME_CAPTURE usa)
  "URL",          // o endereço do alvo — a identidade honesta de quem não expõe outra
                  // (SAME_URL != SAME_DOCUMENT continua a valer: bytes novos no mesmo
                  // endereço são DOCUMENT_CHANGED_IN_PLACE, nunca um documento a menos)
  "RAW_LATIN1",   // os bytes crus lidos como latin1 (metadados de PDF, HTML antigo)
  "RAW_UTF8",     // os bytes crus lidos como utf8 (HTML moderno)
  "PDF_TEXT",     // o texto extraído do PDF (pdftotext, injectado pelo coletor)
  // D42 (2) · «A PÁGINA É O BOLETIM»: a URL fixa não identifica a edição. A edição é o CONTEÚDO
  // (+ a data comprovada). Os dois leitores são os do retrato (coleta/retrato_html.mjs), que o
  // coletor injecta — o motor continua a não abrir nada.
  "PAGE_TEXT",      // o texto visível normalizado da página (retrato_html.textoVisivel, injectado)
  // ⚠️ A impressão do conteúdo NÃO é fonte de captura: hash é BYTE_ID, não identidade (a lei de
  // `motor_de_rota_test.mjs`). Ela sai AO LADO da identidade (CONTENT_SHA256, com CONTENT_SCOPE)
  // e serve para DEDUPLICAR versões do mesmo documento — nunca para o nomear.
]);

export class ContratoInvalido extends Error {}

const ehTexto = (v) => typeof v === "string" && v.trim() !== "";

// ── A CONFERÊNCIA DA IDENTIDADE ────────────────────────────────────────────
// ⚠️ PORQUE ISTO FALTAVA, MEDIDO NA RUN1B DESTA MISSÃO. Com a descoberta já
// corrigida, as 85 observações trouxeram endereços de artigos REAIS — e todas
// as 85 saíram `IDENTITY_FAILED`, com ZERO bytes descarregados. A causa: os
// contratos onboarded declaram `IDENTITY.STRATEGY = "CONTENT_CAPTURE"` (é o
// que `contratoGenerico()` escreve para quem não expõe identificador próprio)
// e este motor só sabia `FILENAME_CAPTURE` — devolvia `null` calado para tudo
// o resto, e o coletor parava antes de ir buscar o documento.
//
//     O MOTOR DEVOLVIA `null`, E `null` NÃO DIZ PORQUÊ.
//     Agora um vocabulário desconhecido reprova com o nome dele.
export function conferirIdentidade(sourceId, spec) {
  if (!spec || typeof spec !== "object") throw new ContratoInvalido(`${sourceId}: sem bloco IDENTITY`);
  if (!ESTRATEGIAS_DE_IDENTIDADE.includes(spec.STRATEGY)) {
    throw new ContratoInvalido(
      `${sourceId}: IDENTITY.STRATEGY ${JSON.stringify(spec.STRATEGY)} fora do vocabulário ` +
      `(${ESTRATEGIAS_DE_IDENTIDADE.join(", ")})`);
  }
  if (!ehTexto(spec.DOCUMENT_ID)) throw new ContratoInvalido(`${sourceId}: IDENTITY sem DOCUMENT_ID`);
  if (spec.STRATEGY === "FILENAME_CAPTURE") {
    if (!ehTexto(spec.PATTERN)) throw new ContratoInvalido(`${sourceId}: FILENAME_CAPTURE precisa de PATTERN`);
    try { new RegExp(spec.PATTERN); }
    catch (err) { throw new ContratoInvalido(`${sourceId}: PATTERN não compila: ${err.message}`); }
  }
  if (spec.STRATEGY === "CONTENT_CAPTURE") {
    const caps = spec.CAPTURES;
    if (!caps || typeof caps !== "object" || Object.keys(caps).length === 0) {
      throw new ContratoInvalido(`${sourceId}: CONTENT_CAPTURE sem CAPTURES`);
    }
    for (const [nome, c] of Object.entries(caps)) {
      if (!/^[A-Za-z_][A-Za-z0-9_]*$/.test(nome)) throw new ContratoInvalido(`${sourceId}: CAPTURES.${nome}: nome inválido`);
      if (!FONTES_DE_TEXTO.includes(c?.FROM)) {
        throw new ContratoInvalido(
          `${sourceId}: CAPTURES.${nome}.FROM ${JSON.stringify(c?.FROM)} fora do vocabulário ` +
          `(${FONTES_DE_TEXTO.join(", ")})`);
      }
      if (!ehTexto(c.PATTERN)) throw new ContratoInvalido(`${sourceId}: CAPTURES.${nome} sem PATTERN`);
      try { new RegExp(c.PATTERN, c.FLAGS || ""); }
      catch (err) { throw new ContratoInvalido(`${sourceId}: CAPTURES.${nome}.PATTERN não compila: ${err.message}`); }
      if (c.REQUIRED === false && !Array.isArray(c.DEFAULTS)) {
        // Uma captura opcional sem valores por omissão deixaria buracos no
        // molde — e um DOCUMENT_ID com buraco é uma identidade a meio.
        throw new ContratoInvalido(`${sourceId}: CAPTURES.${nome} é opcional (REQUIRED=false) e por isso exige DEFAULTS`);
      }
    }
    if (spec.CONTENT_SCOPE != null) {
      const s = spec.CONTENT_SCOPE;
      if (typeof s !== "object" || !ehTexto(s.START)) throw new ContratoInvalido(`${sourceId}: CONTENT_SCOPE precisa de START`);
      for (const k of ["START", "END"]) {
        if (s[k] == null) continue;
        try { new RegExp(s[k], s.FLAGS || ""); }
        catch (err) { throw new ContratoInvalido(`${sourceId}: CONTENT_SCOPE.${k} não compila: ${err.message}`); }
      }
    }
    // Todo `{nome.N}` dos moldes tem de apontar para uma captura declarada.
    for (const campo of ["DOCUMENT_ID", "SOURCE_DATE", "SOURCE_DATE_ISO", "FACT_TIME"]) {
      for (const m of String(spec[campo] || "").matchAll(/\{([A-Za-z_][A-Za-z0-9_]*)\.(\d+)\}/g)) {
        if (!caps[m[1]]) throw new ContratoInvalido(`${sourceId}: ${campo} usa {${m[1]}.${m[2]}}, e não há CAPTURES.${m[1]}`);
      }
    }
    conferirTempoELugar(sourceId, spec, caps);
  } else if (["PUBLISHED_AT", "FACT_LOCATION", "PUBLISHED_AT_BASIS", "FACT_TIME_BASIS", "FACT_LOCATION_BASIS"].some((k) => spec[k] != null)) {
    throw new ContratoInvalido(`${sourceId}: PUBLISHED_AT/FACT_LOCATION e as BASES so existem em CONTENT_CAPTURE`);
  }
  return true;
}

// ── D61/D62 · DATA E LUGAR DO BOLETIM, DECLARADOS PELA ROTA ────────────────
// A rota de um boletim conhece a FORMA dele: o cabeçalho «n. 38/2026 del 21 settembre 2026», o período
// «14 settembre 2026 - 20 settembre 2026», a província da lista. O contrato diz onde ler cada coisa e
// COMO se soube (a BASE); o motor lê, valida e devolve — nunca inventa:
//   PUBLISHED_AT   a data de EMISSÃO do boletim (AAAA-MM-DD)                            + PUBLISHED_AT_BASIS
//   FACT_TIME      o período de validade/observação (AAAA-MM-DD/AAAA-MM-DD, ou um dia)   + FACT_TIME_BASIS
//   FACT_LOCATION  a área que o boletim DECLARA (província/zona)                         + FACT_LOCATION_BASIS
// D62: NENHUM destes campos é obrigatório e NENHUM derruba o documento. Uma captura que não casa, ou
// um valor que não é data de calendário, sai «NAO SEI» com o porquê na BASE. Por isso as capturas
// destes campos têm de ser opcionais (REQUIRED=false): uma data em falta nunca é IDENTITY_FAILED.
// Os nomes são os da fronteira da Collection (`coleta/ingresso.py`): PUBLISHED_AT, FACT_TIME,
// FACT_LOCATION e as _BASIS.
export const CAMPOS_TEMPO_E_LUGAR = Object.freeze(["PUBLISHED_AT", "FACT_TIME", "FACT_LOCATION"]);
export const NAO_SEI = "NAO SEI";
// Os filtros de um molde: vocabulário FECHADO, cada um uma conversão escrita — nada de expressão livre.
const MESES_IT = ["gennaio", "febbraio", "marzo", "aprile", "maggio", "giugno", "luglio", "agosto",
  "settembre", "ottobre", "novembre", "dicembre"];
export const FILTROS_DE_MOLDE = Object.freeze({
  MES_IT: (v) => { const i = MESES_IT.indexOf(String(v).toLowerCase()); return i < 0 ? null : String(i + 1).padStart(2, "0"); },
  MES2: (v) => (/^\d{1,2}$/.test(v) ? String(v).padStart(2, "0") : null),
  DIA2: (v) => (/^\d{1,2}$/.test(v) ? String(v).padStart(2, "0") : null),
  ANO4: (v) => (/^\d{4}$/.test(v) ? String(v) : /^\d{2}$/.test(v) ? `20${v}` : null),
});
const MOLDE = /\{([A-Za-z_][A-Za-z0-9_]*)\.(\d+)(?::([A-Z0-9_]+))?\}/g;

function conferirTempoELugar(sourceId, spec, caps) {
  for (const campo of CAMPOS_TEMPO_E_LUGAR) {
    const base = spec[`${campo}_BASIS`];
    if (campo !== "FACT_TIME" && spec[campo] != null && !ehTexto(base)) {
      throw new ContratoInvalido(`${sourceId}: ${campo} sem ${campo}_BASIS — como se sabe faz parte do que se sabe`);
    }
    if (base != null && !ehTexto(base)) throw new ContratoInvalido(`${sourceId}: ${campo}_BASIS vazia`);
    if (campo === "FACT_TIME" && base == null) continue;      // o FACT_TIME antigo segue a regra antiga
    const moldes = spec[campo] == null ? [] : Array.isArray(spec[campo]) ? spec[campo] : [spec[campo]];
    if (Array.isArray(spec[campo]) && (!moldes.length || !moldes.every(ehTexto))) {
      throw new ContratoInvalido(`${sourceId}: ${campo} em lista tem de ter moldes de texto não vazios`);
    }
    for (const m of moldes.join(" ").matchAll(MOLDE)) {
      if (!caps[m[1]]) throw new ContratoInvalido(`${sourceId}: ${campo} usa {${m[1]}.${m[2]}}, e não há CAPTURES.${m[1]}`);
      if (m[3] && !(m[3] in FILTROS_DE_MOLDE)) {
        throw new ContratoInvalido(`${sourceId}: ${campo} usa o filtro ${m[3]}, fora do vocabulário (${Object.keys(FILTROS_DE_MOLDE).join(", ")})`);
      }
      if (caps[m[1]].REQUIRED !== false) {
        throw new ContratoInvalido(`${sourceId}: ${campo} lê CAPTURES.${m[1]}, que é obrigatória — D62: falta de data ou de lugar nunca derruba o documento (REQUIRED=false)`);
      }
    }
  }
}

const eData = (iso) => {
  if (!/^\d{4}-\d{2}-\d{2}$/.test(iso)) return false;
  const d = new Date(`${iso}T00:00:00Z`);
  return !Number.isNaN(d.getTime()) && d.toISOString().slice(0, 10) === iso;
};

// Um campo de tempo/lugar. O contrato pode dar UM molde ou uma LISTA deles, pela ordem de confiança
// (ex.: o cabeçalho do PDF antes do nome do ficheiro; a forma «(22/09/2026 – 29/09/2026)» antes da forma
// «dal 20/07 al 04/08/2026»): vale o primeiro que der um valor válido; se nenhum der, NAO SEI com o
// porquê de cada um. Uma BASE sem molde é o contrato a dizer que o boletim NÃO traz o campo, e porquê.
function campoDoBoletim(campo, spec, grupos, ausentes) {
  const baseDeclarada = spec[`${campo}_BASIS`];
  if (spec[campo] == null) {
    return [NAO_SEI, baseDeclarada ? `NAO SEI · ${baseDeclarada}` : `NAO SEI · o contrato não declara onde o boletim diz o ${campo}`];
  }
  const moldes = Array.isArray(spec[campo]) ? spec[campo] : [spec[campo]];
  const porques = [];
  for (const [k, molde] of moldes.entries()) {
    const [v, b] = umMolde(campo, molde, baseDeclarada, grupos, ausentes);
    if (v !== NAO_SEI) return [v, moldes.length > 1 ? `${b} · forma ${k + 1} de ${moldes.length}` : b];
    porques.push(moldes.length > 1 ? `forma ${k + 1}: ${b.replace(/^NAO SEI · /, "")}` : b.replace(/^NAO SEI · /, ""));
  }
  return [NAO_SEI, `NAO SEI · ${porques.join(" | ")}`];
}

function umMolde(campo, molde, baseDeclarada, grupos, ausentes) {
  const usadas = [...String(molde).matchAll(MOLDE)];
  const faltam = usadas.map((m) => m[1]).filter((n) => ausentes.has(n));
  if (faltam.length) {
    return [NAO_SEI, `NAO SEI · ${baseDeclarada} · não está neste documento (captura ${[...new Set(faltam)].join(", ")} sem resultado) — o documento não cai (D62)`];
  }
  let invalido = null;
  const valor = String(molde).replace(MOLDE, (_, n, i, f) => {
    const bruto = grupos[n]?.[Number(i)] ?? "";
    if (!f) return bruto;
    const v = FILTROS_DE_MOLDE[f](bruto);
    if (v == null) invalido = `«${bruto}» não passa no filtro ${f}`;
    return v ?? "";
  }).replace(/\s+/g, " ").trim();
  const trecho = [...new Set(usadas.map((m) => grupos[m[1]]?.[0]).filter(Boolean))].join(" … ").replace(/\s+/g, " ").slice(0, 200);
  if (!invalido && campo !== "FACT_LOCATION") {
    const partes = valor.split("/");
    if (!(partes.length <= (campo === "FACT_TIME" ? 2 : 1) && partes.every(eData))) invalido = `«${valor}» não é data de calendário`;
    else if (partes.length === 2 && partes[0] > partes[1]) invalido = `«${valor}» começa depois de acabar`;
  }
  if (!invalido && !valor) invalido = "o valor lido está vazio";
  if (invalido) return [NAO_SEI, `NAO SEI · ${baseDeclarada} · ${invalido} — nunca se inventa (D62) · «${trecho}»`];
  return [valor, `${baseDeclarada} · «${trecho}»`];
}

// ── O QUE FAZ UM BLOCO SER EXECUTÁVEL ──────────────────────────────────────
// ⚠️ ESTA FUNÇÃO É A DIFERENÇA ENTRE CONTRATO E DESCRIÇÃO.
// Ela recusa fechado: um bloco que não declara tudo o que a sua estratégia
// exige não é «quase executável» — é documentação. E documentação não corre.
//
//     DECLARAR PELA METADE É NÃO DECLARAR.
export function conferirAquisicao(sourceId, aq) {
  if (!aq || typeof aq !== "object") {
    throw new ContratoInvalido(`${sourceId}: sem bloco ACQUISITION`);
  }
  const e = aq.STRATEGY;
  if (!ESTRATEGIAS.includes(e)) {
    throw new ContratoInvalido(
      `${sourceId}: STRATEGY ${JSON.stringify(e)} fora do vocabulário fechado ` +
      `(${ESTRATEGIAS.join(", ")})`);
  }
  if (e === "STATIC_ENDPOINT") {
    if (!ehTexto(aq.URL)) throw new ContratoInvalido(`${sourceId}: STATIC_ENDPOINT sem URL`);
  }
  if (e === "TEMPLATE_ENUMERATION") {
    if (!ehTexto(aq.TEMPLATE)) throw new ContratoInvalido(`${sourceId}: TEMPLATE_ENUMERATION sem TEMPLATE`);
    const vars = [...String(aq.TEMPLATE).matchAll(/\{([A-Za-z_]+)\}/g)].map((m) => m[1]);
    const dec = aq.VARS || {};
    for (const v of vars) {
      const spec = dec[v];
      if (!spec) {
        // ⚠️ O DEFEITO CENTRAL DA V1, NOMEADO: um molde com `{NN}` e nenhuma
        // instrução sobre o que é `NN`. `IT-T2-001` tinha exactamente isto.
        throw new ContratoInvalido(
          `${sourceId}: a variável {${v}} do TEMPLATE não tem provider em VARS. ` +
          `Um molde sem provider é uma frase, não uma rota.`);
      }
      if (!PROVIDERS.includes(spec.PROVIDER)) {
        // E isto apanha a prosa: `"dia com 2 digitos"` não é um PROVIDER.
        throw new ContratoInvalido(
          `${sourceId}: {${v}} declara PROVIDER ${JSON.stringify(spec.PROVIDER)}, ` +
          `que não é do vocabulário (${PROVIDERS.join(", ")}). ` +
          `Prosa descreve; não executa.`);
      }
      if (spec.PROVIDER === "LITERAL" && spec.VALUE === undefined) {
        throw new ContratoInvalido(`${sourceId}: {${v}} LITERAL sem VALUE`);
      }
      if (spec.PROVIDER === "ENUM" && !Array.isArray(spec.VALUES)) {
        throw new ContratoInvalido(`${sourceId}: {${v}} ENUM sem VALUES`);
      }
      if (spec.PROVIDER === "RANGE" &&
          !(Number.isInteger(spec.FROM) && Number.isInteger(spec.TO))) {
        throw new ContratoInvalido(`${sourceId}: {${v}} RANGE sem FROM/TO inteiros`);
      }
    }
  }
  if (e === "HTML_LINK_DISCOVERY") {
    if (!ehTexto(aq.INDEX_URL)) throw new ContratoInvalido(`${sourceId}: HTML_LINK_DISCOVERY sem INDEX_URL`);
    if (!ehTexto(aq.LINK_PATTERN)) throw new ContratoInvalido(`${sourceId}: HTML_LINK_DISCOVERY sem LINK_PATTERN`);
    // ⚠️ O PADRÃO É DADO, E NÃO CÓDIGO. É compilado com `new RegExp` sobre uma
    // string do contrato — não há `eval`, não há função serializada, não há
    // expressão livre. Um padrão que não compila é contrato inválido, e
    // descobre-se AQUI, na conferência, e não a meio de uma corrida.
    try { new RegExp(aq.LINK_PATTERN, "i"); }
    catch (err) { throw new ContratoInvalido(`${sourceId}: LINK_PATTERN não compila: ${err.message}`); }
    // ⚠️ ACEITAR UM CAMPO SEM O IMPLEMENTAR É PIOR QUE RECUSÁ-LO. Antes desta
    // linha, `MATCH` não era conferido nem lido em lado nenhum: as 182 fontes
    // passavam a conferência e a corrida acusava a FONTE de não anunciar nada.
    // Um campo fora do vocabulário reprova AQUI, e não a meio de uma visita.
    if (aq.MATCH !== undefined && !["HTML", "URL"].includes(aq.MATCH)) {
      throw new ContratoInvalido(`${sourceId}: MATCH ${JSON.stringify(aq.MATCH)} fora do vocabulário (HTML, URL)`);
    }
    if (aq.STRIP_SUFFIX !== undefined && !ehTexto(aq.STRIP_SUFFIX)) {
      throw new ContratoInvalido(`${sourceId}: STRIP_SUFFIX tem de ser texto não vazio`);
    }
    if (aq.SAME_HOST !== undefined && typeof aq.SAME_HOST !== "boolean") {
      throw new ContratoInvalido(`${sourceId}: SAME_HOST tem de ser true/false`);
    }
  }
  if (e === "CUSTOM_ADAPTER") {
    if (!ehTexto(aq.ADAPTER_ID)) throw new ContratoInvalido(`${sourceId}: CUSTOM_ADAPTER sem ADAPTER_ID`);
  }
  return true;
}

function valoresDe(spec) {
  if (spec.PROVIDER === "LITERAL") return [String(spec.VALUE)];
  if (spec.PROVIDER === "ENUM") return spec.VALUES.map(String);
  const largura = Number.isInteger(spec.PAD) ? spec.PAD : 0;
  const fora = [];
  for (let i = spec.FROM; i <= spec.TO; i++) {
    const s = String(i);
    fora.push(largura > 0 ? s.padStart(largura, "0") : s);
  }
  return fora;
}

function combinar(template, vars) {
  const nomes = [...String(template).matchAll(/\{([A-Za-z_]+)\}/g)].map((m) => m[1]);
  let saida = [template];
  for (const n of [...new Set(nomes)]) {
    const vals = valoresDe(vars[n]);
    const nova = [];
    for (const base of saida) for (const v of vals) nova.push(base.split(`{${n}}`).join(v));
    saida = nova;
  }
  return saida;
}

// ── A ÚNICA PERGUNTA QUE ESTE MOTOR RESPONDE ───────────────────────────────
// «Que endereços devo buscar para esta fonte?» — e mais nada.
//
// `buscar` é injectado: o motor não conhece HTTP, não conhece o armazém e não
// escreve nada. Isso mantém-no testável sem rede e impede que ele cresça para
// dentro do plano de dados.
//
//     CONTROL PLANE != DATA PLANE.
// ── MATCH: "URL" — as ligações de um índice, endereço a endereço ──────────
// Enxertado de `aquisicao-detalhe-v1` (CANONICAL-MICRO-V1, 2026-09-21), onde
// foi derivado do `linksDaEntrada()` que a SOURCE-COLLECTION-READINESS-V1
// provou sobre 107 fontes em 2026-09-18. O que fica de fora fica de fora por
// medição: activos estáticos, paginação e feeds não são documentos; e a
// própria entrada não é um documento seu.
const ATIVOS_ESTATICOS = /\.(css|js|png|jpe?g|gif|svg|ico|woff2?|xml|rss)(\?|#|$)/i;
const PAGINACAO = /\/page\/\d+\/?(\?|#|$)|[?&](page|pagina|pag|p)=\d+/i;
const FEED = /\/(feed|rss|atom)\/?(\?|#|$)/i;
// CAPA-MATERIA (25/09/2026): a PAGINA INSTITUCIONAL nao e documento, esteja onde estiver
// no caminho. Os LINK_PATTERN do molde recusam «contatti», «chi-siamo»... so no PRIMEIRO
// troco (`cia.it/contatti/`); `cia.it/news/settore-comunicazione-contatti/` passava, era o
// 1.o link do indice, e com MAX_TARGETS = 1 foi o unico alvo da IT-T7-135 na 1.a onda (BC5):
// capa no lugar de materia. Medido no livro de coletas da producao: dos 169 enderecos ja
// coletados, esta regra recusa 2 — os dois essa mesma pagina de contatos (IT-T7-121, 135) —
// e nenhuma materia. So o ULTIMO troco, e so quando ACABA na palavra: um artigo
// «nuovi-contatti-con-la-cina» continua a passar.
const PAGINA_INSTITUCIONAL = /(?:^|-)(contatti|contatto|contacts|chi-siamo|dove-siamo|privacy|privacy-policy|cookie|cookie-policy|note-legali|lavora-con-noi|accessibilita|mappa-del-sito|newsletter|login|area-riservata|faq)$/i;
function eInstitucional(u) {
  let ultimo = "";
  try { ultimo = new URL(u).pathname.split("/").filter(Boolean).pop() || ""; } catch { return false; }
  return PAGINA_INSTITUCIONAL.test(ultimo);
}

export function ligacoesDoIndice(html, aq) {
  const padrao = new RegExp(aq.LINK_PATTERN, "i");
  const entrada = aq.INDEX_URL;
  const host = new URL(entrada).hostname.replace(/^www\./, "");
  const entradaNorm = entrada.replace(/\/+$/, "");
  const vistos = new Set(), fora = [];
  for (const m of String(html).matchAll(/href\s*=\s*["']([^"'#]+)["']/gi)) {
    let u;
    try { u = new URL(m[1].trim(), entrada).href; } catch { continue; }
    if (!/^https?:/i.test(u)) continue;
    if (aq.STRIP_SUFFIX && u.endsWith(aq.STRIP_SUFFIX)) u = u.slice(0, -aq.STRIP_SUFFIX.length);
    if (vistos.has(u)) continue;
    vistos.add(u);
    if (aq.SAME_HOST !== false && new URL(u).hostname.replace(/^www\./, "") !== host) continue;
    if (ATIVOS_ESTATICOS.test(u) || PAGINACAO.test(u) || FEED.test(u)) continue;
    if (u.replace(/\/+$/, "") === entradaNorm) continue;
    if (eInstitucional(u)) continue;
    if (!padrao.test(u)) continue;
    fora.push(u);
  }
  return fora;
}

// O nome do ficheiro guardado nasce do último troço do caminho; um artigo
// HTML raramente traz extensão, e o armazém precisa de uma.
export function nomeDoAlvo(url, outputType) {
  let nome = "";
  try { nome = decodeURIComponent(new URL(url).pathname.split("/").filter(Boolean).pop() || ""); } catch { }
  // ⚠️ 60 e nao 120: medido na Big Collection 2, com a pasta do documento ja
  // limitada, 9 ficheiros continuavam acima dos 260 caracteres do MAX_PATH do
  // Windows por causa do NOME. Fica a cauda, que e onde vive a extensao.
  nome = nome.replace(/[^A-Za-z0-9._-]+/g, "_").slice(-60);
  const ext = String(outputType || "").toUpperCase() === "PDF" ? ".pdf" : ".html";
  return nome.toLowerCase().endsWith(ext) ? nome : (nome || "documento") + ext;
}


// ── D40 (bot Luciano, 25/09): O 1.º ALVO AINDA NÃO COLETADO, ATÉ 3 POR FONTE ──
// Medido na 1.a onda (BC5): 12 de 18 fontes voltaram VAZIAS. O contrato pedia 1 alvo
// (MAX_TARGETS = 1), o corte era feito AQUI, antes de se saber se esse alvo era novo, e
// o coletor so depois via que ja o conhecia (SKIP_KNOWN). A fonte tinha materia nova no
// indice — o 2.o, o 3.o link — e a corrida nao lhe chegava.
//
//     CORTAR ANTES DE PERGUNTAR «JA TENHO?» E ESCOLHER O QUE JA SE TEM.
//
// Com `classificar(url)` (o coletor passa-a, lendo o livro de observacoes da producao):
//   * «CONHECIDO» (o livro diz SKIP_KNOWN) sai ANTES do corte — zero pedidos por ele;
//   * «NOVO» (nunca guardado com documento) vem primeiro, pela ORDEM DO INDICE;
//   * «REVISITA» (a lei do conteudo MUTABLE manda revisitar) vem depois, tambem por ordem;
//   * corta em ALVOS_POR_FONTE_D40 = 3, seja qual for o MAX_TARGETS do contrato;
//   * sem nada novo nem revisita, volta VAZIO — com a conta dos conhecidos saltados, nao
//     um zero calado.
// O teto por DOMINIO (D38, 5 pedidos por corrida contando robots e indice) NAO vive aqui:
// quem corta e o transporte (`umaIda()` em coleta/italy_pilot_collect.mjs, ONDA2-G3). Esta
// escolha so planeia: robots (1) + indice (1) + 3 materias = 5.
export const ALVOS_POR_FONTE_D40 = 3;

// ── PAGINA DE LISTA NAO E ALVO (coordenador, ALVOS-NOVOS-2, 25/09) ───────────
// Medido com D40: a ciatoscana escolheria `comunicati-stampa-2026/2025/2024` — tres
// paginas que LISTAM comunicados, nenhuma e um comunicado. E o defeito capa-no-lugar-
// de-materia, noutro molde. Recusa-se pelo ULTIMO pedaco do endereco, e so quando ele
// e SO lista: um ano sozinho (`/2026/`), palavras de lista + ano (`comunicati-stampa-
// 2026`, `notizie-2025`), paginacao (`/page/3/`), ou categoria/etiqueta/arquivo.
//
//     «TERMINA EM ANO» NAO BASTA: `prezzi-al-consumo-agosto-2026` E UMA MATERIA.
//
// Por isso o ano so recusa quando TUDO o que vem antes dele sao palavras de lista.
const PALAVRA_DE_LISTA = "(?:comunicati|comunicato|stampa|notizie|news|archivio|archive|articoli|eventi|rassegna|press|releases?|blog|pubblicazioni|bollettini|anno|tutte|le)";
const LISTA_COM_ANO = new RegExp(`^(?:${PALAVRA_DE_LISTA}-)*(?:19|20)\\d{2}$`, "i");
const SO_LISTA = /^(?:category|categoria|categorie|tag|tags|archivio|archive|archivi|page|pagina|author|autore)$/i;
const DENTRO_DE_LISTA = /^(?:category|categoria|categorie|tag|tags|author|autore)$/i;
export function ePaginaDeLista(u) {
  let pedacos;
  try { pedacos = new URL(u).pathname.split("/").filter(Boolean).map((p) => decodeURIComponent(p)); } catch { return false; }
  const ultimo = pedacos.at(-1) || "", antes = pedacos.at(-2) || "";
  if (/^(?:page|pagina|pag)$/i.test(antes) && /^\d+$/.test(ultimo)) return true;
  if (DENTRO_DE_LISTA.test(antes)) return true;
  return SO_LISTA.test(ultimo) || LISTA_COM_ANO.test(ultimo);
}

export function escolherAlvosD40(urls, classificar, nomeDe) {
  const novos = [], revisitas = [];
  let conhecidos = 0, listas = 0;
  for (const url of urls) {
    // antes do livro: uma lista nao e alvo, seja nova ou conhecida
    if (ePaginaDeLista(url)) { listas++; continue; }
    const classe = classificar(url);
    if (classe === "CONHECIDO") conhecidos++;
    else if (classe === "REVISITA") revisitas.push(url);
    else novos.push(url);
  }
  const alvos = [...novos, ...revisitas].slice(0, ALVOS_POR_FONTE_D40)
    .map((url) => ({ url, nome: nomeDe(url) }));
  // a conta vai no proprio resultado (o coletor pode dize-la no resumo); um array continua
  // a ser o que todos os chamadores ja recebiam
  Object.defineProperty(alvos, "D40", { value: {
    NO_INDICE: urls.length, LISTAS_RECUSADAS: listas, CONHECIDOS_SALTADOS: conhecidos, NOVOS: novos.length,
    REVISITAS: revisitas.length, ESCOLHIDOS: alvos.length,
    VAZIO_HONESTO: alvos.length === 0 } });
  return alvos;
}

export async function alvosDoContrato(sourceId, contrato, { buscar, adapters = {}, classificar = null } = {}) {
  const aq = contrato && contrato.ACQUISITION;
  conferirAquisicao(sourceId, aq);

  if (aq.STRATEGY === "STATIC_ENDPOINT") {
    return [{ url: aq.URL, nome: aq.NAME || aq.URL.split("/").pop() }];
  }

  if (aq.STRATEGY === "TEMPLATE_ENUMERATION") {
    return combinar(aq.TEMPLATE, aq.VARS || {})
      .map((url) => ({ url, nome: url.split("/").pop() }));
  }

  if (aq.STRATEGY === "HTML_LINK_DISCOVERY") {
    if (typeof buscar !== "function") {
      throw new ContratoInvalido(`${sourceId}: HTML_LINK_DISCOVERY precisa de um leitor`);
    }
    const idx = await buscar(aq.INDEX_URL);
    if (idx.erro || idx.status !== 200) {
      return { erro: `indice inacessivel: ${idx.erro || idx.status}` };
    }
    const texto = idx.buf.toString("latin1");
    // ── MATCH: ONDE O PADRÃO SE APLICA ────────────────────────────────────
    // Enxertado de `aquisicao-detalhe-v1` na CANONICAL-MICRO-V1 (2026-09-21),
    // a mão e só este ramo: trazer o ficheiro inteiro apagava 42 linhas deste.
    //
    // "HTML" (omissão) — o padrão corre sobre o TEXTO do índice e o grupo 1 é
    //   o endereço. É o modo dos `case` migrados, e é o que fica em baixo,
    //   intacto: nenhuma fonte que já funcionava muda de caminho.
    // "URL" — extraem-se TODOS os `href`, resolvem-se contra o índice, e o
    //   padrão corre sobre cada endereço ABSOLUTO.
    //
    // ⚠️ PORQUE ISTO FALTAVA, MEDIDO NA RUN1 DESTA MISSÃO. A tabela onboarded
    // declara `MATCH: "URL"` e traz padrões que são URLs inteiras ancoradas —
    // `^https?://(www\.)?myfruit\.it/news/...$`. Este motor ignorava `MATCH`
    // (zero ocorrências da palavra no ficheiro) e corria o padrão contra o
    // documento todo. Um `^...$` sem flag `m` só casa se o documento INTEIRO
    // for exactamente aquele endereço — nunca dentro de uma página.
    //
    // O resultado foi SEIS de SEIS fontes com `EMPTY_LIST`, e `EMPTY_LIST` é
    // uma afirmação sobre a FONTE: «o índice não anuncia nada». Era falso. O
    // índice anunciava; o motor é que estava a ler o sítio errado.
    //
    //     UM VOCABULÁRIO QUE O MOTOR NÃO LÊ NÃO É CONFIGURAÇÃO:
    //     É UMA PROMESSA QUE O CONTRATO FAZ E NINGUÉM CUMPRE.
    //
    // `conferirAquisicao` passava as 182 linhas porque nunca olhou para
    // `MATCH`. Aceitar um campo sem o implementar é pior que recusá-lo: a
    // conferência dá verde e a corrida acusa a fonte.
    const limite = Number.isInteger(aq.MAX_TARGETS) ? aq.MAX_TARGETS : Infinity;
    if (aq.MATCH === "URL") {
      const urls = ligacoesDoIndice(texto, aq);
      if (urls.length === 0) {
        return { erro: "EMPTY_LIST — o indice nao anuncia nenhum endereco que case com LINK_PATTERN" };
      }
      if (typeof classificar === "function") {
        return escolherAlvosD40(urls, classificar, (url) => nomeDoAlvo(url, contrato && contrato.OUTPUT_TYPE));
      }
      return urls.slice(0, limite).map((url) => ({ url, nome: nomeDoAlvo(url, contrato && contrato.OUTPUT_TYPE) }));
    }
    const re = new RegExp(aq.LINK_PATTERN, "gi");
    const achados = [...texto.matchAll(re)].map((m) => (m[1] !== undefined ? m[1] : m[0]));
    if (achados.length === 0) {
      // EMPTY_LIST não é erro de rede nem de contrato: é o índice a não
      // anunciar nada. Diz-se com esse nome, e não com um zero calado.
      return { erro: "EMPTY_LIST — o indice nao anuncia nenhum alvo que case com LINK_PATTERN" };
    }
    const base = aq.BASE_URL || aq.INDEX_URL;
    const urls = [...new Set(achados.map((h) => new URL(h, base).href))];
    if (typeof classificar === "function") {
      return escolherAlvosD40(urls, classificar, (url) => url.split("/").pop());
    }
    return urls.slice(0, Number.isFinite(limite) ? limite : urls.length)
               .map((url) => ({ url, nome: url.split("/").pop() }));
  }

  // CUSTOM_ADAPTER — o contrato NOMEIA; o registry resolve. O despachador
  // central continua sem conhecer SOURCE_ID nenhum.
  const fn = adapters[aq.ADAPTER_ID];
  if (typeof fn !== "function") {
    throw new ContratoInvalido(
      `${sourceId}: ADAPTER_ID ${JSON.stringify(aq.ADAPTER_ID)} não está no registry`);
  }
  return fn({ sourceId, contrato, buscar });
}

// ── IDENTIDADE DECLARATIVA ─────────────────────────────────────────────────
// Medido: `identidade()` tinha NOVE ramos por SOURCE_ID — mais do que o
// discovery. Generalizar só o discovery seria o falso fechamento
// «DISCOVERY_GENERIC = YES, IDENTITY_STILL_REQUIRES_SOURCE_CASE = YES».
//
// O que se generaliza é o caso provado: a identidade que nasce do NOME do
// ficheiro por captura. `DOCUMENT_ID_RULE` continua a existir em prosa, para
// gente, e NÃO é lido aqui.
//
//     DOCUMENT_ID_RULE_TEXT != IDENTITY_EXECUTABLE_SPEC.
// A parte do texto entre START (inclusive) e END (exclusive), ou o texto todo sem CONTENT_SCOPE.
// null quando o contrato declara um recorte que o texto nao tem.
export function recortar(texto, scope) {
  const t = String(texto || "");
  if (!scope) return t;
  const i = t.search(new RegExp(scope.START, scope.FLAGS || ""));
  if (i < 0) return null;
  const resto = t.slice(i);
  if (!scope.END) return resto;
  const j = resto.slice(1).search(new RegExp(scope.END, scope.FLAGS || ""));
  return j < 0 ? resto : resto.slice(0, j + 1);
}

// A mesma normalizacao do TEXT_SHA256 do retrato (coleta/retrato_html.mjs): espacos colapsados.
export function impressao(texto) {
  return createHash("sha256").update(String(texto).replace(/\s+/g, " ").trim(), "utf8").digest("hex");
}

export function identidadeDoContrato(sourceId, contrato, alvo, { leitores = {} } = {}) {
  const spec = contrato && contrato.IDENTITY;
  if (!spec) return null;
  conferirIdentidade(sourceId, spec);
  // ⚠️ `FACT_TIME` NÃO TEM FALLBACK, E ISSO É DELIBERADO.
  // Ele não herda `SOURCE_DATE`, não herda `PUBLISHED_AT`, e não se calcula
  // a partir do nome do ficheiro. A data do documento é quando a fonte o
  // publicou; o tempo do facto é quando a coisa aconteceu no campo — e um
  // boletim que não o diz não passa a dizê-lo por conveniência nossa.
  //
  //     FACT_TIME != PUBLISHED_AT. UNKNOWN CONTINUA UNKNOWN.
  const FACT_TIME = spec.FACT_TIME || "UNKNOWN";
  const vazio = { DOCUMENT_ID: null, SOURCE_DATE: null, SOURCE_DATE_ISO: null, FACT_TIME };

  if (spec.STRATEGY === "FILENAME_CAPTURE") {
    const m = String(alvo.nome || "").match(new RegExp(spec.PATTERN));
    if (!m) return vazio;
    const põe = (molde) => String(molde).replace(/\$(\d+)/g, (_, i) => m[Number(i)] ?? "");
    return {
      DOCUMENT_ID: põe(spec.DOCUMENT_ID),
      SOURCE_DATE: spec.SOURCE_DATE ? põe(spec.SOURCE_DATE) : null,
      SOURCE_DATE_ISO: spec.SOURCE_DATE_ISO ? põe(spec.SOURCE_DATE_ISO) : null,
      FACT_TIME,
    };
  }

  // CONTENT_CAPTURE — cada captura lê a sua fonte de texto uma vez.
  // O motor NUNCA abre um ficheiro nem chama um programa: `FILENAME` e `URL`
  // já estão no alvo, e tudo o resto (bytes, texto de PDF) chega por um
  // leitor INJECTADO. Um leitor que o coletor não injectou é contrato por
  // cumprir, e diz-se assim — não se devolve identidade a meio.
  const textos = {};
  const textoDe = (de) => {
    if (de === "FILENAME") return String(alvo.nome || "");
    if (de === "URL") return String(alvo.url || "");
    if (!(de in textos)) {
      const ler = leitores[de];
      if (typeof ler !== "function") {
        throw new ContratoInvalido(`${sourceId}: CAPTURES pede ${de}, e o coletor não injectou esse leitor`);
      }
      textos[de] = String(ler() ?? "");
    }
    return textos[de];
  };
  const grupos = {};
  const ausentes = new Set();
  for (const [nome, c] of Object.entries(spec.CAPTURES)) {
    const m = textoDe(c.FROM).match(new RegExp(c.PATTERN, c.FLAGS || ""));
    if (m) {
      // `.trim()` em cada grupo: um padrão como `([A-Z ]+)` apanha o espaço
      // antes do fim da linha, e o `case` medido tirava-o à mão.
      grupos[nome] = m.map((g) => (g == null ? "" : String(g).trim()));
    } else if (c.REQUIRED === false) {
      grupos[nome] = ["", ...c.DEFAULTS.map(String)];
      ausentes.add(nome);
    } else {
      return vazio;
    }
  }
  const põe = (molde) => String(molde).replace(/\{([A-Za-z_][A-Za-z0-9_]*)\.(\d+)\}/g,
    (_, n, i) => grupos[n]?.[Number(i)] ?? "");
  // ⚠️ D42 (2): UM TEMPO QUE A FONTE NÃO DISSE É `UNKNOWN`, INTEIRO.
  // Os DEFAULTS de uma captura opcional servem para a IDENTIDADE não ficar com buraco
  // (ex.: «IT-T2-152:UNKNOWN:ab12…»). Num campo de TEMPO (SOURCE_DATE, SOURCE_DATE_ISO,
  // FACT_TIME) um valor por omissão seria uma data inventada — e a data de coleta nunca entra
  // no lugar dela. Se o molde de tempo usa uma captura ausente, o campo inteiro é UNKNOWN.
  const tempo = (molde) => {
    if (!molde) return null;
    for (const m of String(molde).matchAll(/\{([A-Za-z_][A-Za-z0-9_]*)\.\d+\}/g)) {
      if (ausentes.has(m[1])) return "UNKNOWN";
    }
    return põe(molde);
  };
  // ⚠️ A IMPRESSÃO MIRA O BOLETIM, NÃO A PÁGINA (COL-LAW-029). O texto visível inteiro leva menus,
  // contadores e a hora da nossa visita. O contrato diz onde o boletim começa e acaba
  // (CONTENT_SCOPE); sem o recorte, a identidade falha fechada (IDENTITY_FAILED) em vez de guardar
  // lixo com cara de boletim. A impressão vai AO LADO da identidade, para deduplicar.
  let CONTENT_SHA256;
  if (spec.CONTENT_SCOPE) {
    const parte = recortar(textoDe("PAGE_TEXT"), spec.CONTENT_SCOPE);
    if (parte == null || !parte.trim()) return vazio;
    CONTENT_SHA256 = impressao(parte);
  }
  const saida = {
    DOCUMENT_ID: põe(spec.DOCUMENT_ID),
    ...(CONTENT_SHA256 ? { CONTENT_SHA256 } : {}),
    SOURCE_DATE: tempo(spec.SOURCE_DATE),
    SOURCE_DATE_ISO: tempo(spec.SOURCE_DATE_ISO),
    // FACT_TIME pode ser um molde com capturas (ex.: o periodo que o boletim cobre); sem
    // capturas, e o literal do contrato ou UNKNOWN, como antes.
    FACT_TIME: /\{[A-Za-z_][A-Za-z0-9_]*\.\d+\}/.test(FACT_TIME) ? tempo(FACT_TIME) : FACT_TIME,
  };
  // D61/D62: so quem declara uma BASE entra no modo «boletim com data e lugar»; os outros contratos
  // saem exactamente como antes (sem FACT_LOCATION: SOURCE_LOCATION != FACT_LOCATION).
  if (CAMPOS_TEMPO_E_LUGAR.some((k) => spec[`${k}_BASIS`] != null)) {
    for (const campo of CAMPOS_TEMPO_E_LUGAR) {
      const [v, b] = campoDoBoletim(campo, spec, grupos, ausentes);
      saida[campo] = v;
      saida[`${campo}_BASIS`] = b;
    }
  }
  return saida;
}

export const CONTRATO_MOTOR_VERSAO = "route-engine-v1";
