// SINTONIA EAME — AS PROVAS DO CONTRATO EXECUTÁVEL
//
//     node regras/motor_de_rota_test.mjs
//
// O QUE ELAS GUARDAM
// -------------------
// Que o contrato DIRIGE a coleta, e que continua a ser contrato — dados com
// vocabulário fechado — e não um programa disfarçado.
//
// NENHUMA PROVA AQUI ABRE A REDE. O leitor de índice é injectado, e devolve
// um HTML escrito à mão. A prova com rede real é o canário, e vive noutro
// sítio.

import { strict as assert } from "node:assert";
import { readFileSync } from "node:fs";
import {
  alvosDoContrato, identidadeDoContrato, conferirAquisicao,
  ContratoInvalido, ESTRATEGIAS, PROVIDERS, ligacoesDoIndice, nomeDoAlvo, ALVOS_POR_FONTE_D40, ePaginaDeLista,
  conferirIdentidade, ESTRATEGIAS_DE_IDENTIDADE, FONTES_DE_TEXTO,
} from "./motor_de_rota.mjs";
import { CONTRACTS } from "./italy_contracts.mjs";

let ok = 0, mau = 0;
const T = (nome, fn) => {
  try { fn(); console.log(`  PASS  ${nome}`); ok++; }
  catch (e) { console.log(`  FAIL  ${nome}\n        ${e.message}`); mau++; }
};
const TA = async (nome, fn) => {
  try { await fn(); console.log(`  PASS  ${nome}`); ok++; }
  catch (e) { console.log(`  FAIL  ${nome}\n        ${e.message}`); mau++; }
};

const indiceFalso = (html) => async () => ({ status: 200, buf: Buffer.from(html, "latin1") });

console.log("\n1 · O VOCABULÁRIO É FECHADO");

T("uma estratégia fora do vocabulário é recusada", () => {
  assert.throws(() => conferirAquisicao("X", { STRATEGY: "MAGIA" }), ContratoInvalido);
});

T("o vocabulário tem exactamente as 4 estratégias derivadas dos casos medidos", () => {
  assert.deepEqual([...ESTRATEGIAS].sort(),
    ["CUSTOM_ADAPTER", "HTML_LINK_DISCOVERY", "STATIC_ENDPOINT", "TEMPLATE_ENUMERATION"]);
});

console.log("\n2 · MUTAÇÃO M1 — campo estrutural em falta");

T("M1a · STATIC_ENDPOINT sem URL é recusado", () => {
  assert.throws(() => conferirAquisicao("X", { STRATEGY: "STATIC_ENDPOINT" }), ContratoInvalido);
});

T("M1b · HTML_LINK_DISCOVERY sem LINK_PATTERN é recusado", () => {
  assert.throws(() => conferirAquisicao("X", {
    STRATEGY: "HTML_LINK_DISCOVERY", INDEX_URL: "https://exemplo.it/",
  }), ContratoInvalido);
});

T("M1c · CUSTOM_ADAPTER sem ADAPTER_ID é recusado", () => {
  assert.throws(() => conferirAquisicao("X", { STRATEGY: "CUSTOM_ADAPTER" }), ContratoInvalido);
});

console.log("\n3 · MUTAÇÃO M3 — variável de molde sem provider");

T("M3 · {NN} no TEMPLATE e nada em VARS é recusado", () => {
  // Este é o defeito da v1, tal como `IT-T2-001` o tinha: molde com
  // variáveis e nenhuma instrução sobre o que elas são.
  assert.throws(() => conferirAquisicao("X", {
    STRATEGY: "TEMPLATE_ENUMERATION",
    TEMPLATE: "https://exemplo.it/{ANO}/{NN}.pdf",
    VARS: { ANO: { PROVIDER: "LITERAL", VALUE: "2026" } },
  }), /nao tem provider|não tem provider/i);
});

console.log("\n4 · MUTAÇÃO M4 — prosa humana como provider");

T("M4 · 'dia com 2 digitos' não é um PROVIDER", () => {
  // A frase medida no `ROUTE_VARS` real de `IT-T3-002`. Ela descreve; não
  // executa. Se isto passasse, o runtime estaria a ler prosa.
  assert.throws(() => conferirAquisicao("X", {
    STRATEGY: "TEMPLATE_ENUMERATION",
    TEMPLATE: "https://exemplo.it/{DD}.pdf",
    VARS: { DD: { PROVIDER: "dia com 2 digitos" } },
  }), /vocabul/i);
});

T("os providers são três, e só três", () => {
  assert.deepEqual([...PROVIDERS].sort(), ["ENUM", "LITERAL", "RANGE"]);
});

console.log("\n5 · O CONTRATO NÃO CARREGA CÓDIGO");

T("não há eval/Function/exec no motor", () => {
  const src = readFileSync(new URL("./motor_de_rota.mjs", import.meta.url), "utf8");
  // `new RegExp` sobre uma string do contrato é dado compilado, não código
  // executado: não alcança variáveis, não chama funções, não sai do texto.
  for (const proibido of ["eval(", "new Function", "execSync", "spawn("]) {
    assert.ok(!src.includes(proibido), `o motor contém ${proibido}`);
  }
});

console.log("\n6 · AS TRÊS ESTRATÉGIAS RESOLVEM ALVOS");

await TA("STATIC_ENDPOINT devolve o endereço escrito", async () => {
  const r = await alvosDoContrato("X", {
    ACQUISITION: { STRATEGY: "STATIC_ENDPOINT", URL: "https://exemplo.it/a.html" },
  }, {});
  assert.equal(r.length, 1);
  assert.equal(r[0].url, "https://exemplo.it/a.html");
});

await TA("TEMPLATE_ENUMERATION combina ENUM × RANGE", async () => {
  const r = await alvosDoContrato("X", {
    ACQUISITION: {
      STRATEGY: "TEMPLATE_ENUMERATION",
      TEMPLATE: "https://exemplo.it/{PROV}-{NN}.pdf",
      VARS: {
        PROV: { PROVIDER: "ENUM", VALUES: ["AV", "SA"] },
        NN: { PROVIDER: "RANGE", FROM: 1, TO: 3, PAD: 2 },
      },
    },
  }, {});
  assert.equal(r.length, 6, "2 provincias × 3 numeros");
  assert.ok(r.some((a) => a.url.endsWith("AV-01.pdf")));
  assert.ok(r.some((a) => a.url.endsWith("SA-03.pdf")));
});

await TA("HTML_LINK_DISCOVERY extrai e resolve relativos", async () => {
  const r = await alvosDoContrato("X", {
    ACQUISITION: {
      STRATEGY: "HTML_LINK_DISCOVERY",
      INDEX_URL: "https://exemplo.it/indice/",
      LINK_PATTERN: 'href="([^"]*\\.pdf)"',
    },
  }, { buscar: indiceFalso('<a href="pdf/b1.pdf">x</a><a href="/abs/b2.pdf">y</a>') });
  assert.equal(r.length, 2);
  assert.equal(r[0].url, "https://exemplo.it/indice/pdf/b1.pdf", "relativo resolvido contra o índice");
  assert.equal(r[1].url, "https://exemplo.it/abs/b2.pdf");
});

await TA("índice sem nenhum alvo devolve EMPTY_LIST, e não zero calado", async () => {
  const r = await alvosDoContrato("X", {
    ACQUISITION: {
      STRATEGY: "HTML_LINK_DISCOVERY",
      INDEX_URL: "https://exemplo.it/", LINK_PATTERN: 'href="([^"]*\\.pdf)"',
    },
  }, { buscar: indiceFalso("<p>nada aqui</p>") });
  assert.ok(r.erro && r.erro.includes("EMPTY_LIST"));
});

console.log("\n7 · ADAPTER É NOMEADO, NÃO CARREGADO");

await TA("CUSTOM_ADAPTER resolve pelo registry", async () => {
  const r = await alvosDoContrato("X", {
    ACQUISITION: { STRATEGY: "CUSTOM_ADAPTER", ADAPTER_ID: "FAMILIA_TESTE_V1" },
  }, { adapters: { FAMILIA_TESTE_V1: () => [{ url: "https://exemplo.it/z.pdf", nome: "z.pdf" }] } });
  assert.equal(r[0].nome, "z.pdf");
});

await TA("adapter não registado falha fechado", async () => {
  await assert.rejects(() => alvosDoContrato("X", {
    ACQUISITION: { STRATEGY: "CUSTOM_ADAPTER", ADAPTER_ID: "NAO_EXISTE" },
  }, { adapters: {} }), ContratoInvalido);
});

console.log("\n8 · IDENTIDADE DECLARATIVA, E AS LEIS DE TEMPO");

T("FILENAME_CAPTURE monta o DOCUMENT_ID a partir do nome", () => {
  const id = identidadeDoContrato("X", {
    IDENTITY: { STRATEGY: "FILENAME_CAPTURE", PATTERN: "^([A-Z]{2})-(\\d{2})\\.pdf$",
                DOCUMENT_ID: "TESTE:$1:$2" },
  }, { nome: "AV-07.pdf" });
  assert.equal(id.DOCUMENT_ID, "TESTE:AV:07");
});

T("M5 · FACT_TIME não herda a data do documento", () => {
  // O ficheiro diz 2026; o FACT_TIME continua UNKNOWN porque ninguém provou
  // quando o facto aconteceu. Se um dia isto devolver "2026", a lei caiu.
  const id = identidadeDoContrato("X", {
    IDENTITY: { STRATEGY: "FILENAME_CAPTURE", PATTERN: "(20\\d{2})",
                DOCUMENT_ID: "T:$1", SOURCE_DATE: "$1" },
  }, { nome: "boletim-2026.pdf" });
  assert.equal(id.SOURCE_DATE, "2026");
  assert.equal(id.FACT_TIME, "UNKNOWN", "FACT_TIME != PUBLISHED_AT");
});

T("M6 · o motor não tem campo de FACT_LOCATION para herdar", () => {
  const id = identidadeDoContrato("X", {
    IDENTITY: { STRATEGY: "FILENAME_CAPTURE", PATTERN: "(x)", DOCUMENT_ID: "T:$1" },
  }, { nome: "x" });
  assert.ok(!("FACT_LOCATION" in id), "SOURCE_LOCATION != FACT_LOCATION");
});

console.log("\n9 · O CONTRATO REAL DE IT-T3-011 É EXECUTÁVEL");

T("IT-T3-011 declara ACQUISITION válida", () => {
  conferirAquisicao("IT-T3-011", CONTRACTS["IT-T3-011"].ACQUISITION);
});

T("IT-T3-011 declara IDENTITY com FACT_TIME UNKNOWN", () => {
  const i = CONTRACTS["IT-T3-011"].IDENTITY;
  assert.equal(i.STRATEGY, "FILENAME_CAPTURE");
  assert.ok(String(i.FACT_TIME).startsWith("UNKNOWN"));
});

console.log("\n10 · ACRESCENTAR FONTE DA MESMA FAMÍLIA NÃO TOCA NO DESPACHADOR");

await TA("uma fonte fictícia HTML_LINK_DISCOVERY corre sem editar o coletor", async () => {
  // A prova do desacoplamento: este contrato não existe no repositório, não
  // tem `case`, e ninguém o registou em lado nenhum. Se ele corre, então
  // cadastrar a próxima fonte da família é escrever contrato — não código.
  const ficticia = {
    ACQUISITION: {
      STRATEGY: "HTML_LINK_DISCOVERY",
      INDEX_URL: "https://fonte-que-nao-existe.it/docs/",
      LINK_PATTERN: 'href="([^"]*\\.pdf)"',
    },
    IDENTITY: { STRATEGY: "FILENAME_CAPTURE", PATTERN: "(\\d{4})", DOCUMENT_ID: "FICT:$1" },
  };
  const r = await alvosDoContrato("IT-FICT-001", ficticia, {
    buscar: indiceFalso('<a href="rel/2026-boll.pdf">b</a>'),
  });
  assert.equal(r.length, 1);
  assert.equal(r[0].url, "https://fonte-que-nao-existe.it/docs/rel/2026-boll.pdf");
  const id = identidadeDoContrato("IT-FICT-001", ficticia, r[0]);
  assert.equal(id.DOCUMENT_ID, "FICT:2026");
});

console.log("\n11 · M2 — o despachador não pode voltar a conhecer SOURCE_ID");

T("M2 · alvosDe consulta ACQUISITION antes do switch", () => {
  const src = readFileSync(
    new URL("../coleta/italy_pilot_collect.mjs", import.meta.url), "utf8");
  const ini = src.indexOf("async function alvosDe");
  const corpo = src.slice(ini, src.indexOf("switch (sourceId)", ini));
  assert.ok(corpo.includes("alvosDoContrato"),
    "o contrato deixou de ter precedência sobre o switch");
});

T("M2b · identidade consulta IDENTITY antes do switch", () => {
  const src = readFileSync(
    new URL("../coleta/italy_pilot_collect.mjs", import.meta.url), "utf8");
  const ini = src.indexOf("function identidade(sourceId");
  const corpo = src.slice(ini, ini + 1400);
  assert.ok(corpo.includes("identidadeDoContrato"),
    "a identidade declarativa deixou de vir primeiro");
});

console.log("\n12 - MATCH:URL - o padrao corre sobre o ENDERECO, nao sobre a pagina");

// ⚠️ ESTAS PROVAS NASCERAM DE UMA CORRIDA REAL QUE MENTIU SOBRE AS FONTES.
// CANONICAL-MICRO-V1, RUN1 de 2026-09-21: seis fontes em seis devolveram
// `EMPTY_LIST — o indice nao anuncia nenhum alvo`. Era falso. Os indices
// anunciavam; o motor ignorava `MATCH: "URL"` e corria um padrao ancorado
// (`^https?://...$`) contra o TEXTO da pagina inteira, onde ele nunca casa.
//
//     EMPTY_LIST E UMA ACUSACAO A FONTE. So se faz depois de olhar
//     onde a fonte escreveu, e nao onde e comodo procurar.

const INDICE_REAL = `<html><body>
  <a href="/news/o-primeiro-artigo/">um</a>
  <a href="https://www.exemplo.it/news/segundo-artigo">dois</a>
  <a href="/news/category/vinho/">categoria</a>
  <a href="/news/page/2/">pagina 2</a>
  <a href="/tema.css">folha de estilo</a>
  <a href="/feed/">o feed</a>
  <a href="https://outro-sitio.com/news/de-fora/">outro host</a>
  <a href="/">a propria entrada</a>
</body></html>`;

const AQ_URL = {
  STRATEGY: "HTML_LINK_DISCOVERY", MATCH: "URL",
  INDEX_URL: "https://www.exemplo.it/",
  LINK_PATTERN: "^https?://(www\\.)?exemplo\\.it/news/(?!category/)[a-z0-9]+(?:-[a-z0-9]+)+/?$",
  MAX_TARGETS: 30,
};

T("URL - o padrao ancorado encontra os artigos que a pagina anuncia", () => {
  const u = ligacoesDoIndice(INDICE_REAL, AQ_URL);
  assert.deepEqual(u, ["https://www.exemplo.it/news/o-primeiro-artigo/",
                       "https://www.exemplo.it/news/segundo-artigo"]);
});

// ⚠️ ESTE FIXTURE MUDOU DEPOIS DO RED TEAM, E O MOTIVO IMPORTA.
// A 1.a versao usava `/news/page/2/` e `/feed/` como armadilhas. Nenhuma
// delas casava com o LINK_PATTERN (que exige um hifen no ultimo troco), por
// isso apagar os filtros do motor NAO mudava o resultado: dois mutantes
// SOBREVIVERAM a uma prova que parecia guardar isto.
//
//     UMA ARMADILHA QUE O PADRAO JA RECUSA NAO PROVA O FILTRO.
//     Ela tem de CASAR, para que o filtro seja a UNICA coisa que a barra.
const INDICE_COM_ARMADILHAS = `<html><body>
  <a href="/news/o-primeiro-artigo/">um</a>
  <a href="/news/pagina-dois/page/2/">paginacao que CASA com o padrao</a>
  <a href="/news/noticias-todas/feed/">feed que CASA com o padrao</a>
  <a href="/news/artigo-bonito.css">activo estatico que CASA</a>
  <a href="/news/tudo/?page=3">paginacao por parametro</a>
  <a href="https://outro-sitio.com/news/de-fora/">outro host</a>
</body></html>`;

const AQ_LARGO = { ...AQ_URL,
  LINK_PATTERN: "^https?://(www\\.)?exemplo\\.it/news/.+$" };

T("URL - paginacao, feed, activo estatico e outro host ficam fora MESMO casando", () => {
  const u = ligacoesDoIndice(INDICE_COM_ARMADILHAS, AQ_LARGO);
  assert.deepEqual(u, ["https://www.exemplo.it/news/o-primeiro-artigo/"],
    `entrou coisa que nao e documento: ${JSON.stringify(u)}`);
});

T("URL - a propria pagina de entrada nunca entra como documento seu", () => {
  // A entrada com barra, sem barra, e a entrada anunciada em absoluto.
  const html = `<html>
    <a href="/">a entrada</a>
    <a href="https://www.exemplo.it">a entrada em absoluto</a>
    <a href="https://www.exemplo.it/">a entrada com barra</a>
    <a href="/news/um-artigo-verdadeiro/">o unico documento</a></html>`;
  const aq = { ...AQ_URL, INDEX_URL: "https://www.exemplo.it/",
               LINK_PATTERN: "^https?://(www\\.)?exemplo\\.it/?.*$" };
  const u = ligacoesDoIndice(html, aq);
  assert.ok(!u.includes("https://www.exemplo.it/"), "a homepage entrou como materia");
  assert.ok(!u.includes("https://www.exemplo.it"), "a homepage entrou como materia");
  assert.deepEqual(u, ["https://www.exemplo.it/news/um-artigo-verdadeiro/"]);
});

// ── CAPA-MATERIA (25/09): a pagina institucional nao e alvo, esteja onde estiver ──
// O indice REAL da IT-T7-135 (cia.it) anunciava primeiro a pagina de contatos debaixo
// de /news/, e com MAX_TARGETS = 1 ela foi o unico alvo da 1.a onda (capa != materia).
const AQ_CIA = { STRATEGY: "HTML_LINK_DISCOVERY", MATCH: "URL", MAX_TARGETS: 1,
  INDEX_URL: "https://cia.it/agrichef-1/",
  LINK_PATTERN: "^https?://(www\\.)?cia\\.it/(?!(?:category|tag|author|contatti|chi-siamo)(?:/|$))(?:[^?#]*/)?(?:news|notizie)[^?#]*/(?:[a-z0-9]+(?:-[a-z0-9]+){2,}|\\d{4}[^?#]*)/?(?:[?#].*)?$" };
const INDICE_CIA = `<html>
  <a href="https://cia.it/news/settore-comunicazione-contatti/">Contatti</a>
  <a href="https://cia.it/news/notizie/agrichef-festival-la-campania-porta-alla-finale/">artigo</a>
  <a href="https://cia.it/news/notizie/nuovi-contatti-con-la-cina-per-l-export/">artigo com contatti no meio</a>
</html>`;

await TA("CAPA-MATERIA - a pagina de contatos debaixo de /news/ nao e alvo; o 1.o alvo passa a ser o artigo", async () => {
  const u = ligacoesDoIndice(INDICE_CIA, AQ_CIA);
  assert.ok(!u.some((x) => x.endsWith("settore-comunicazione-contatti/")), `a pagina de contatos entrou: ${u}`);
  assert.equal(u[0], "https://cia.it/news/notizie/agrichef-festival-la-campania-porta-alla-finale/");
  const alvos = await alvosDoContrato("IT-T7-135", { ACQUISITION: AQ_CIA, OUTPUT_TYPE: "HTML" },
    { buscar: async () => ({ status: 200, buf: Buffer.from(INDICE_CIA) }) });
  assert.equal(alvos.length, 1);
  assert.equal(alvos[0].url, u[0], "com MAX_TARGETS = 1 o unico alvo tem de ser o artigo");
});

T("CAPA-MATERIA - a palavra institucional so conta no FIM do ultimo troco", () => {
  const u = ligacoesDoIndice(INDICE_CIA, AQ_CIA);
  assert.ok(u.includes("https://cia.it/news/notizie/nuovi-contatti-con-la-cina-per-l-export/"),
    "um artigo com «contatti» no meio do titulo foi recusado");
});

T("CAPA-MATERIA - privacy, chi-siamo, newsletter e faq no ultimo troco ficam fora", () => {
  const html = ["privacy-policy", "chi-siamo", "iscriviti-alla-newsletter", "faq", "lavora-con-noi"]
    .map((s) => `<a href="https://cia.it/news/pagina/${s}/">x</a>`).join("") +
    `<a href="https://cia.it/news/notizie/un-vero-articolo-di-campo/">y</a>`;
  const aq = { ...AQ_CIA, LINK_PATTERN: "^https?://(www\\.)?cia\\.it/news/.+$" };
  assert.deepEqual(ligacoesDoIndice(html, aq), ["https://cia.it/news/notizie/un-vero-articolo-di-campo/"]);
});

// ── D40: o 1.o alvo ainda NAO coletado, ate 3 por fonte ─────────────────────
const IDX_D40 = `<html>` + [1, 2, 3, 4, 5, 6].map((n) =>
  `<a href="https://www.exemplo.it/news/artigo-numero-${n}-de-teste/">a${n}</a>`).join("") + `</html>`;
const AQ_D40 = { STRATEGY: "HTML_LINK_DISCOVERY", MATCH: "URL", MAX_TARGETS: 1,
  INDEX_URL: "https://www.exemplo.it/news/", LINK_PATTERN: "^https?://(www\\.)?exemplo\\.it/news/.+$" };
const url = (n) => `https://www.exemplo.it/news/artigo-numero-${n}-de-teste/`;
const pedidosD40 = [];
const buscarD40 = async (u) => { pedidosD40.push(u); return { status: 200, buf: Buffer.from(IDX_D40, "latin1") }; };

await TA("D40 - o conhecido sai ANTES do corte: com 1 e 2 no livro, os alvos sao 3, 4, 5", async () => {
  pedidosD40.length = 0;
  const conhecidos = new Set([url(1), url(2)]);
  const alvos = await alvosDoContrato("X", { ACQUISITION: AQ_D40, OUTPUT_TYPE: "HTML" },
    { buscar: buscarD40, classificar: (u) => (conhecidos.has(u) ? "CONHECIDO" : "NOVO") });
  assert.deepEqual(alvos.map((a) => a.url), [url(3), url(4), url(5)]);
  assert.deepEqual(pedidosD40, ["https://www.exemplo.it/news/"], "so o indice foi pedido: a escolha nao gasta rede");
  assert.equal(alvos.D40.CONHECIDOS_SALTADOS, 2);
});

await TA("D40 - no maximo 3, mesmo com o contrato a pedir 1 ou 30", async () => {
  for (const mt of [1, 30]) {
    const alvos = await alvosDoContrato("X", { ACQUISITION: { ...AQ_D40, MAX_TARGETS: mt }, OUTPUT_TYPE: "HTML" },
      { buscar: buscarD40, classificar: () => "NOVO" });
    assert.equal(alvos.length, ALVOS_POR_FONTE_D40, `MAX_TARGETS=${mt}`);
    assert.equal(ALVOS_POR_FONTE_D40, 3);
  }
});

await TA("D40 - ordem estavel: a ordem do indice, duas corridas iguais", async () => {
  const cls = (u) => (u === url(2) ? "CONHECIDO" : "NOVO");
  const a = await alvosDoContrato("X", { ACQUISITION: AQ_D40 }, { buscar: buscarD40, classificar: cls });
  const b = await alvosDoContrato("X", { ACQUISITION: AQ_D40 }, { buscar: buscarD40, classificar: cls });
  assert.deepEqual(a.map((x) => x.url), [url(1), url(3), url(4)]);
  assert.deepEqual(a.map((x) => x.url), b.map((x) => x.url));
});

await TA("D40 - o NOVO passa a frente da REVISITA, e a revisita so entra se sobrar lugar", async () => {
  const cls = (u) => (u === url(1) || u === url(2) ? "REVISITA" : u === url(3) ? "CONHECIDO" : u === url(6) ? "NOVO" : "CONHECIDO");
  const alvos = await alvosDoContrato("X", { ACQUISITION: AQ_D40 }, { buscar: buscarD40, classificar: cls });
  assert.deepEqual(alvos.map((x) => x.url), [url(6), url(1), url(2)]);
});

await TA("D40 - tudo conhecido: volta VAZIO, com a conta, e sem inventar alvo", async () => {
  const alvos = await alvosDoContrato("X", { ACQUISITION: AQ_D40 }, { buscar: buscarD40, classificar: () => "CONHECIDO" });
  assert.equal(alvos.length, 0);
  assert.ok(!alvos.erro, "tudo conhecido nao e erro da fonte");
  assert.equal(alvos.D40.VAZIO_HONESTO, true);
  assert.equal(alvos.D40.CONHECIDOS_SALTADOS, 6);
});

await TA("D40 - vale tambem para o padrao lido dentro do HTML (MATCH HTML)", async () => {
  const alvos = await alvosDoContrato("X", { ACQUISITION: { STRATEGY: "HTML_LINK_DISCOVERY", MAX_TARGETS: 30,
    INDEX_URL: "https://exemplo.it/i/", LINK_PATTERN: 'href="([^"]*\\.pdf)"' } }, {
    buscar: indiceFalso(["a", "b", "c", "d", "e"].map((x) => `<a href="${x}.pdf">x</a>`).join("")),
    classificar: (u) => (u.endsWith("/a.pdf") ? "CONHECIDO" : "NOVO") });
  assert.deepEqual(alvos.map((x) => x.nome), ["b.pdf", "c.pdf", "d.pdf"]);
  assert.equal(alvos.D40.CONHECIDOS_SALTADOS, 1);
});

T("LISTA - so lista e recusada: ano sozinho, lista+ano, paginacao, categoria, etiqueta, arquivo", () => {
  for (const u of [
    "https://www.ciatoscana.eu/home/tutte-le-notizie/comunicati-stampa/comunicati-stampa-2026/",
    "https://x.it/news/notizie-2025/", "https://x.it/news/2026/", "https://x.it/news/page/3/",
    "https://x.it/tag/vino/", "https://x.it/categoria/ortofrutta/", "https://x.it/news/archivio/",
  ]) assert.equal(ePaginaDeLista(u), true, u);
});

T("LISTA - materia com ano no fim NAO e lista (o risco medido: 0 dos 169 do livro)", () => {
  for (const u of [
    "https://www.istat.it/comunicato-stampa/prezzi-al-consumo-agosto-2026/",
    "https://www.istat.it/comunicato-stampa/linnovazione-nelle-imprese-anni-2022-2024/",
    "https://x.it/news/vinitaly-2026/",
    "https://plantgest.imagelinenetwork.com/it/news/2026/09/15/pesco-cosa-cambia-tra-varieta-e-nuovi-astoni/89677",
    "https://www.myfruit.it/news/macfrut-neri-siamo-in-simbiosi-con-gli-espositori",
  ]) assert.equal(ePaginaDeLista(u), false, u);
});

await TA("D40 - a lista sai antes do livro e do corte; so listas = vazio honesto", async () => {
  const perguntados = [];
  const IDX = `<html>` + ["comunicati-stampa-2026", "comunicati-stampa-2025", "raccolta-uva-in-toscana-2026", "comunicati-stampa-2024"]
    .map((s) => `<a href="https://www.exemplo.it/news/${s}/">x</a>`).join("") + `</html>`;
  const aq = { ...AQ_D40, LINK_PATTERN: "^https?://(www\\.)?exemplo\\.it/news/.+$" };
  const alvos = await alvosDoContrato("X", { ACQUISITION: aq }, { buscar: indiceFalso(IDX),
    classificar: (u) => { perguntados.push(u); return "NOVO"; } });
  assert.deepEqual(alvos.map((a) => a.url), ["https://www.exemplo.it/news/raccolta-uva-in-toscana-2026/"]);
  assert.equal(alvos.D40.LISTAS_RECUSADAS, 3);
  assert.deepEqual(perguntados, ["https://www.exemplo.it/news/raccolta-uva-in-toscana-2026/"], "lista nem chega ao livro");
  const so = await alvosDoContrato("X", { ACQUISITION: aq }, {
    buscar: indiceFalso(`<a href="https://www.exemplo.it/news/comunicati-stampa-2026/">x</a>`), classificar: () => "NOVO" });
  assert.equal(so.length, 0);
  assert.equal(so.D40.VAZIO_HONESTO, true);
  assert.equal(so.D40.LISTAS_RECUSADAS, 1);
});

await TA("D40 - sem `classificar` (canarios, provas) o motor corta como antes: MAX_TARGETS", async () => {
  const alvos = await alvosDoContrato("X", { ACQUISITION: AQ_D40 }, { buscar: buscarD40 });
  assert.deepEqual(alvos.map((x) => x.url), [url(1)]);
  assert.equal(alvos.D40, undefined);
});

T("URL - categoria, paginacao, activo estatico, feed e outro host ficam fora", () => {
  const u = ligacoesDoIndice(INDICE_REAL, AQ_URL).join(" ");
  for (const fora of ["category", "/page/", ".css", "/feed", "outro-sitio"]) {
    assert.ok(!u.includes(fora), `${fora} entrou, e nao e um documento`);
  }
});

T("URL - alvosDoContrato devolve alvos, e nao EMPTY_LIST", async () => {
  const r = await alvosDoContrato("IT-FICT-URL", { ACQUISITION: AQ_URL, OUTPUT_TYPE: "HTML" },
    { buscar: async () => ({ status: 200, buf: Buffer.from(INDICE_REAL, "latin1") }) });
  assert.ok(Array.isArray(r), `devolveu erro: ${JSON.stringify(r)}`);
  assert.equal(r.length, 2);
  assert.equal(r[0].nome, "o-primeiro-artigo.html", "o nome do alvo perdeu a extensao");
});

T("URL - indice que MESMO nao anuncia nada continua a dizer EMPTY_LIST", async () => {
  const r = await alvosDoContrato("IT-FICT-URL", { ACQUISITION: AQ_URL, OUTPUT_TYPE: "HTML" },
    { buscar: async () => ({ status: 200, buf: Buffer.from("<html><a href='/sobre/'>x</a></html>", "latin1") }) });
  assert.ok(r && r.erro && r.erro.startsWith("EMPTY_LIST"),
    "um indice sem documentos deixou de se queixar - EMPTY_LIST tem de continuar a existir");
});

T("URL - MAX_TARGETS continua a limitar", async () => {
  const r = await alvosDoContrato("IT-FICT-URL",
    { ACQUISITION: { ...AQ_URL, MAX_TARGETS: 1 }, OUTPUT_TYPE: "HTML" },
    { buscar: async () => ({ status: 200, buf: Buffer.from(INDICE_REAL, "latin1") }) });
  assert.equal(r.length, 1);
});

T("HTML - o modo antigo nao mudou: grupo 1 sobre o texto da pagina", async () => {
  const r = await alvosDoContrato("IT-FICT-HTML",
    { ACQUISITION: { STRATEGY: "HTML_LINK_DISCOVERY", INDEX_URL: "http://www.apol.it/",
                     LINK_PATTERN: 'href="([^"]*Bollettino_Mosca[^"]*\\.pdf)"', MAX_TARGETS: 1 } },
    { buscar: async () => ({ status: 200,
        buf: Buffer.from('<a href="/x/Bollettino_Mosca_01.pdf">p</a>', "latin1") }) });
  assert.equal(r.length, 1);
  assert.equal(r[0].url, "http://www.apol.it/x/Bollettino_Mosca_01.pdf");
  assert.equal(r[0].nome, "Bollettino_Mosca_01.pdf", "o modo HTML passou a usar nomeDoAlvo");
});

T("MATCH fora do vocabulario reprova na CONFERENCIA, nao a meio da visita", () => {
  assert.throws(() => conferirAquisicao("X", { ...AQ_URL, MATCH: "JSON" }), ContratoInvalido);
  assert.doesNotThrow(() => conferirAquisicao("X", { ...AQ_URL, MATCH: "URL" }));
  assert.doesNotThrow(() => conferirAquisicao("X", { ...AQ_URL, MATCH: "HTML" }));
});

T("as fontes onboarded que declaram MATCH:URL sao servidas pelo ramo certo", () => {
  const comURL = Object.keys(CONTRACTS).filter(
    (id) => CONTRACTS[id].ACQUISITION && CONTRACTS[id].ACQUISITION.MATCH === "URL");
  assert.ok(comURL.length > 100, `so ${comURL.length} fontes declaram MATCH:URL`);
  for (const id of comURL) conferirAquisicao(id, CONTRACTS[id].ACQUISITION);
});

T("nomeDoAlvo - a cauda fica, e a extensao nasce do OUTPUT_TYPE", () => {
  assert.equal(nomeDoAlvo("https://x.it/news/uma-noticia/", "HTML"), "uma-noticia.html");
  assert.equal(nomeDoAlvo("https://x.it/docs/b.pdf", "PDF"), "b.pdf");
  assert.ok(nomeDoAlvo("https://x.it/" + "a".repeat(200), "HTML").length <= 65,
    "o nome passou do limite que o MAX_PATH do Windows aguenta");
});

console.log("\n13 - CONTENT_CAPTURE - identidade de quem nao expoe identificador proprio");

// ⚠️ ESTAS PROVAS NASCERAM DA RUN1B DESTA MISSAO. Com a descoberta ja
// corrigida, 85 observacoes trouxeram enderecos de artigos REAIS e as 85
// sairam `IDENTITY_FAILED`, com ZERO bytes descarregados. O motor so sabia
// `FILENAME_CAPTURE` e devolvia `null` calado para tudo o resto — e os
// contratos onboarded declaram `CONTENT_CAPTURE`.
//
//     `null` NAO DIZ PORQUE. Um vocabulario desconhecido reprova
//     agora com o nome dele, na conferencia.

const ALVO = { url: "https://www.exemplo.it/news/uma-noticia-de-campo",
               nome: "uma-noticia-de-campo.html" };

const ID_URL = {
  STRATEGY: "CONTENT_CAPTURE",
  CAPTURES: { doc: { FROM: "URL", PATTERN: "^https?://[^/]+/?(.*?)/?$" } },
  DOCUMENT_ID: "IT-FICT-001:URL:{doc.1}",
  FACT_TIME: "UNKNOWN - identidade pelo endereco",
};

T("CONTENT_CAPTURE - a identidade nasce do ENDERECO quando e so isso que ha", () => {
  const r = identidadeDoContrato("IT-FICT-001", { IDENTITY: ID_URL }, ALVO);
  assert.equal(r.DOCUMENT_ID, "IT-FICT-001:URL:news/uma-noticia-de-campo");
});

T("CONTENT_CAPTURE - FACT_TIME continua UNKNOWN e NAO herda nada", () => {
  const r = identidadeDoContrato("IT-FICT-001", { IDENTITY: ID_URL }, ALVO);
  assert.ok(/UNKNOWN/.test(r.FACT_TIME), "FACT_TIME deixou de confessar que nao sabe");
  assert.equal(r.SOURCE_DATE, null, "SOURCE_DATE nasceu do nada");
  // O endereco tem um ano la dentro e continua a NAO virar tempo do facto.
  const comAno = { url: "https://x.it/news/2026/03/colheita", nome: "colheita.html" };
  const r2 = identidadeDoContrato("IT-FICT-001", { IDENTITY: ID_URL }, comAno);
  assert.ok(/UNKNOWN/.test(r2.FACT_TIME), "uma data no endereco virou tempo do facto");
});

T("CONTENT_CAPTURE - captura que nao casa devolve identidade VAZIA, nao meia", () => {
  const spec = { ...ID_URL,
    CAPTURES: { doc: { FROM: "FILENAME", PATTERN: "^BOLETIM-(\\d{4})\\.pdf$" } },
    DOCUMENT_ID: "X:{doc.1}" };
  const r = identidadeDoContrato("IT-FICT-001", { IDENTITY: spec }, ALVO);
  assert.equal(r.DOCUMENT_ID, null, "saiu um DOCUMENT_ID com buraco");
  assert.ok(/UNKNOWN/.test(r.FACT_TIME));
});

T("CONTENT_CAPTURE - um leitor que o coletor nao injectou DIZ-SE, nao se adivinha", () => {
  const spec = { ...ID_URL, CAPTURES: { d: { FROM: "PDF_TEXT", PATTERN: "(\\d{4})" } },
                 DOCUMENT_ID: "X:{d.1}" };
  assert.throws(() => identidadeDoContrato("IT-FICT-001", { IDENTITY: spec }, ALVO),
    ContratoInvalido, "um leitor em falta passou calado");
});

T("CONTENT_CAPTURE - o leitor injectado e lido UMA vez e serve a captura", () => {
  let vezes = 0;
  const spec = { ...ID_URL,
    CAPTURES: { a: { FROM: "RAW_UTF8", PATTERN: "edicao (\\d+)" },
                b: { FROM: "RAW_UTF8", PATTERN: "ano (\\d{4})" } },
    DOCUMENT_ID: "X:{a.1}:{b.1}" };
  const r = identidadeDoContrato("IT-FICT-001", { IDENTITY: spec }, ALVO,
    { leitores: { RAW_UTF8: () => { vezes++; return "edicao 42 ano 2026"; } } });
  assert.equal(r.DOCUMENT_ID, "X:42:2026");
  assert.equal(vezes, 1, "o mesmo texto foi lido mais que uma vez");
});

T("FILENAME_CAPTURE - o caminho antigo nao mudou", () => {
  const spec = { STRATEGY: "FILENAME_CAPTURE", PATTERN: "^([A-Z]{2})-(\\d{2})-(\\d{2})\\.pdf$",
                 DOCUMENT_ID: "CAMPANIA:$1:$2-$3-2026", SOURCE_DATE: "$2/$3/2026",
                 FACT_TIME: "UNKNOWN - o boletim nao data a observacao de campo" };
  const r = identidadeDoContrato("IT-T3-002", { IDENTITY: spec }, { nome: "SA-02-09.pdf" });
  assert.equal(r.DOCUMENT_ID, "CAMPANIA:SA:02-09-2026");
  assert.equal(r.SOURCE_DATE, "02/09/2026");
  assert.ok(/UNKNOWN/.test(r.FACT_TIME));
});

T("conferirIdentidade - vocabulario fechado nas duas dimensoes", () => {
  assert.throws(() => conferirIdentidade("X", { ...ID_URL, STRATEGY: "ADIVINHA" }), ContratoInvalido);
  assert.throws(() => conferirIdentidade("X",
    { ...ID_URL, CAPTURES: { d: { FROM: "TELEPATIA", PATTERN: "x" } } }), ContratoInvalido);
  assert.throws(() => conferirIdentidade("X", { ...ID_URL, DOCUMENT_ID: "" }), ContratoInvalido);
  assert.equal(ESTRATEGIAS_DE_IDENTIDADE.length, 2);
  assert.ok(FONTES_DE_TEXTO.includes("URL") && FONTES_DE_TEXTO.includes("PDF_TEXT"));
});

T("conferirIdentidade - molde que aponta para captura inexistente reprova", () => {
  assert.throws(() => conferirIdentidade("X",
    { ...ID_URL, DOCUMENT_ID: "X:{naoexiste.1}" }), ContratoInvalido);
});

T("conferirIdentidade - captura opcional exige DEFAULTS, senao o molde fica com buraco", () => {
  assert.throws(() => conferirIdentidade("X",
    { ...ID_URL, CAPTURES: { doc: { FROM: "URL", PATTERN: "(x)", REQUIRED: false } } }),
    ContratoInvalido);
});

// ── O SOBREVIVENTE DA CANONICAL-MICRO-V1, E A LEI QUE O PRENDE ────────────
// ⚠️ MEDIDO DE FORA PELO DONO, E REPRODUZIDO AQUI ANTES DE ESCREVER ISTO:
// apagar a linha 114 de `motor_de_rota.mjs` — o `throw` de
// «CONTENT_CAPTURE sem CAPTURES» — deixava a suite inteira em
// `45 PASSOU · 0 FALHOU`. O mutante SOBREVIVIA.
//
// Porque sobrevivia: havia `assert.throws` para `MAGIA`, para
// `STATIC_ENDPOINT` sem URL, para `CUSTOM_ADAPTER` sem ADAPTER_ID, para
// `FROM: "TELEPATIA"` e para a captura opcional sem `DEFAULTS` — mas nenhum
// para a ausencia do proprio bloco `CAPTURES`. Todas as provas de
// `CONTENT_CAPTURE` partiam de `ID_URL`, que TRAZ `CAPTURES` ja preenchido.
//
//     COBRIR OUTRA ESTRATEGIA NAO E COBRIR ESTA LEI.
//     UMA LEI SO ESTA PROVADA PELA PROVA QUE FALHA QUANDO ELA CAI.
//
// As tres formas de nao ter `CAPTURES` nao caem no mesmo sitio, e por isso
// sao medidas as tres:
//   ausente / `null` → sem o `throw`, `Object.entries` rebenta com um
//     `TypeError`, que NAO e `ContratoInvalido`: contrato invalido passaria
//     a parecer avaria do motor;
//   `{}` com molde literal → sem o `throw` nao ha mais nada a reprovar, e a
//     conferencia devolve `true` a um contrato que nao sabe identificar nada.
//     Esta e a forma que mata mesmo: e o unico guarda no caminho.
const DOC_FIXO = "IT-FICT-001:documento-unico";

T("CONTENT_CAPTURE sem CAPTURES reprova — e reprova por ESTA lei", () => {
  const semCaptures = (caps) => {
    const s = { STRATEGY: "CONTENT_CAPTURE", DOCUMENT_ID: DOC_FIXO };
    if (caps !== undefined) s.CAPTURES = caps;
    return s;
  };
  // `{}` — molde SEM `{nome.N}`, para que este `throw` seja o unico guarda no
  // caminho. Se ele cair, a conferencia devolve `true` e a prova acusa.
  assert.throws(() => conferirIdentidade("IT-FICT-001", semCaptures({})),
    (err) => {
      assert.ok(err instanceof ContratoInvalido,
        `CAPTURES vazio saiu como ${err.constructor.name}, nao como ContratoInvalido`);
      assert.match(err.message, /CONTENT_CAPTURE sem CAPTURES/,
        "reprovou, mas por outra lei que nao esta");
      return true;
    }, "CONTENT_CAPTURE com CAPTURES VAZIO passou a conferencia");
  // ausente e `null` — tem de sair `ContratoInvalido`, nao um TypeError cru.
  for (const caps of [undefined, null]) {
    assert.throws(() => conferirIdentidade("IT-FICT-001", semCaptures(caps)),
      (err) => {
        assert.ok(err instanceof ContratoInvalido,
          `CAPTURES ${JSON.stringify(caps) ?? "ausente"} saiu como ` +
          `${err.constructor.name} — contrato invalido a parecer avaria do motor`);
        assert.match(err.message, /CONTENT_CAPTURE sem CAPTURES/);
        return true;
      });
  }
});

// CONTROLO POSITIVO. Sem ele, a prova acima seria satisfeita por um motor que
// recusasse TODO o `CONTENT_CAPTURE` — e recusar tudo tambem mata o mutante,
// sem servir para nada. Esta prova diz o que a lei NAO pode barrar.
T("CONTROLO POSITIVO - CONTENT_CAPTURE com CAPTURES valido passa e identifica", () => {
  const spec = { STRATEGY: "CONTENT_CAPTURE", DOCUMENT_ID: DOC_FIXO,
                 CAPTURES: { doc: { FROM: "URL", PATTERN: "/news/(.+)$" } } };
  assert.equal(conferirIdentidade("IT-FICT-001", spec), true,
    "um CONTENT_CAPTURE bem declarado foi reprovado");
  // E um so par `CAPTURES` chega: a lei exige pelo menos um, nao um numero.
  const r = identidadeDoContrato("IT-FICT-001",
    { IDENTITY: { ...spec, DOCUMENT_ID: "IT-FICT-001:{doc.1}" } }, ALVO);
  assert.equal(r.DOCUMENT_ID, "IT-FICT-001:uma-noticia-de-campo");
});

T("as 174 fontes com bloco IDENTITY passam a conferencia", () => {
  const comId = Object.keys(CONTRACTS).filter((id) => CONTRACTS[id].IDENTITY);
  assert.ok(comId.length > 150, `so ${comId.length} contratos tem bloco IDENTITY`);
  for (const id of comId) conferirIdentidade(id, CONTRACTS[id].IDENTITY);
});

T("nenhum DOCUMENT_ID dos contratos onboarded usa o SHA como identidade", () => {
  for (const id of Object.keys(CONTRACTS)) {
    const s = CONTRACTS[id].IDENTITY;
    if (!s) continue;
    assert.ok(!/SHA|HASH|RAW_SHA/i.test(String(s.DOCUMENT_ID)),
      `${id}: o DOCUMENT_ID cita o hash — hash e BYTE_ID, nao identidade`);
  }
});

console.log(`\n  PASSOU ${ok} · FALHOU ${mau}\n`);
if (mau) process.exit(1);
