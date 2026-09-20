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
  alvosDoContrato, identidadeDoContrato, conferirAquisicao, conferirIdentidade,
  ContratoInvalido, ESTRATEGIAS, PROVIDERS,
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

// Até ao cutover estas duas provas mediam «o contrato vem ANTES do switch».
// Depois dele o switch não existe, e a prova passa a medir isso mesmo:
// LEGACY_DISCOVERY_CASES = 0 e LEGACY_IDENTITY_CASES = 0, no código, não
// nos comentários (que têm o direito de citar o defeito antigo).
const codigoDoColetor = () => readFileSync(
  new URL("../coleta/italy_pilot_collect.mjs", import.meta.url), "utf8")
  .split("\n").filter((l) => !l.trim().startsWith("//")).join("\n");

T("M2 · alvosDe vai ao motor e não tem switch por SOURCE_ID", () => {
  const src = codigoDoColetor();
  const ini = src.indexOf("async function alvosDe");
  const corpo = src.slice(ini, src.indexOf("function textoDoPdf", ini));
  assert.ok(corpo.includes("alvosDoContrato"), "a descoberta deixou de vir do contrato");
  assert.ok(!corpo.includes("switch (sourceId)"), "o switch por SOURCE_ID voltou à descoberta");
  assert.equal((src.match(/case "IT-/g) || []).length, 0, "há `case` por SOURCE_ID no coletor");
});

T("M2b · identidade vai ao motor com os leitores injectados, e não tem switch", () => {
  const src = codigoDoColetor();
  const ini = src.indexOf("function identidade(sourceId");
  const corpo = src.slice(ini, src.indexOf("export function normalizarSias", ini));
  assert.ok(corpo.includes("identidadeDoContrato"), "a identidade deixou de vir do contrato");
  for (const leitor of ["RAW_LATIN1", "RAW_UTF8", "PDF_TEXT"]) {
    assert.ok(corpo.includes(leitor), `o coletor não injecta o leitor ${leitor}`);
  }
  assert.ok(!corpo.includes("switch (sourceId)"), "o switch por SOURCE_ID voltou à identidade");
});

console.log("\n12 · CONTENT_CAPTURE — a identidade que vive no conteúdo, sem o motor abrir nada");

const specConteudo = {
  IDENTITY: {
    STRATEGY: "CONTENT_CAPTURE",
    CAPTURES: {
      janela: { FROM: "RAW_LATIN1", PATTERN: "dal\\s*(\\d{2}/\\d{2}/\\d{4})\\s*al\\s*((\\d{2})/(\\d{2})/(\\d{4}))" },
      n: { FROM: "FILENAME", PATTERN: "_n_(\\d+)_" },
      compr: { FROM: "PDF_TEXT", PATTERN: "COMPRENSORIO\\s*-\\s*([A-Z]{2})\\s*-\\s*([A-Z ]+)", REQUIRED: false, DEFAULTS: ["?", "?"] },
    },
    DOCUMENT_ID: "T:{janela.5}-{janela.4}-{janela.3}:N{n.1}:{compr.1}-{compr.2}",
    SOURCE_DATE: "{janela.1} a {janela.2}",
    SOURCE_DATE_ISO: "{janela.5}-{janela.4}-{janela.3}",
    FACT_TIME: "por linha — cada celula tem sua propria data",
  },
};

T("três capturas de três fontes de texto montam um DOCUMENT_ID", () => {
  const id = identidadeDoContrato("X", specConteudo, { nome: "boll_n_9_del.pdf" }, { leitores: {
    RAW_LATIN1: () => "Dati dal 26/08/2026 al 05/09/2026",
    PDF_TEXT: () => "COMPRENSORIO - BR - COLLINA   \n",
  } });
  assert.equal(id.DOCUMENT_ID, "T:2026-09-05:N9:BR-COLLINA", "grupos recompostos e aparados (trim)");
  assert.equal(id.SOURCE_DATE, "26/08/2026 a 05/09/2026");
  assert.equal(id.SOURCE_DATE_ISO, "2026-09-05");
  assert.equal(id.FACT_TIME, "por linha — cada celula tem sua propria data");
});

T("uma captura opcional que não casa usa os DEFAULTS; uma obrigatória que não casa anula tudo", () => {
  const leitores = { RAW_LATIN1: () => "Dati dal 26/08/2026 al 05/09/2026", PDF_TEXT: () => "sem comprensorio" };
  const id = identidadeDoContrato("X", specConteudo, { nome: "boll_n_9_del.pdf" }, { leitores });
  assert.equal(id.DOCUMENT_ID, "T:2026-09-05:N9:?-?");
  const nada = identidadeDoContrato("X", specConteudo, { nome: "boll_sem_numero.pdf" }, { leitores });
  assert.equal(nada.DOCUMENT_ID, null, "IDENTITY_FAILED, não identidade a meio");
  assert.equal(nada.SOURCE_DATE, null);
  assert.equal(nada.FACT_TIME, "por linha — cada celula tem sua propria data", "FACT_TIME é do contrato, não do documento");
});

T("o leitor é preguiçoso: PDF_TEXT só se lê se uma captura o pedir", () => {
  let lido = 0;
  identidadeDoContrato("X", {
    IDENTITY: { STRATEGY: "CONTENT_CAPTURE", CAPTURES: { a: { FROM: "FILENAME", PATTERN: "(x)" } }, DOCUMENT_ID: "T:{a.1}" },
  }, { nome: "x" }, { leitores: { PDF_TEXT: () => { lido++; return ""; } } });
  assert.equal(lido, 0);
});

T("captura que pede um leitor não injectado falha fechado, com nome", () => {
  assert.throws(() => identidadeDoContrato("X", {
    IDENTITY: { STRATEGY: "CONTENT_CAPTURE", CAPTURES: { a: { FROM: "PDF_TEXT", PATTERN: "(x)" } }, DOCUMENT_ID: "T:{a.1}" },
  }, { nome: "x" }, { leitores: {} }), /PDF_TEXT/);
});

T("M7 · FROM fora do vocabulário, molde a apontar para captura inexistente, opcional sem DEFAULTS: os três são contrato inválido", () => {
  assert.throws(() => conferirIdentidade("X", { STRATEGY: "CONTENT_CAPTURE", DOCUMENT_ID: "T:{a.1}",
    CAPTURES: { a: { FROM: "o corpo do html", PATTERN: "(x)" } } }), /vocabulário/);
  assert.throws(() => conferirIdentidade("X", { STRATEGY: "CONTENT_CAPTURE", DOCUMENT_ID: "T:{b.1}",
    CAPTURES: { a: { FROM: "FILENAME", PATTERN: "(x)" } } }), /não há CAPTURES\.b/);
  assert.throws(() => conferirIdentidade("X", { STRATEGY: "CONTENT_CAPTURE", DOCUMENT_ID: "T:{a.1}",
    CAPTURES: { a: { FROM: "FILENAME", PATTERN: "(x)", REQUIRED: false } } }), /DEFAULTS/);
});

T("M8 · FACT_TIME de CONTENT_CAPTURE também não herda a data capturada", () => {
  const id = identidadeDoContrato("X", {
    IDENTITY: { STRATEGY: "CONTENT_CAPTURE", CAPTURES: { d: { FROM: "RAW_UTF8", PATTERN: "(\\d{4}-\\d{2}-\\d{2})" } },
                DOCUMENT_ID: "T:{d.1}", SOURCE_DATE_ISO: "{d.1}" },
  }, { nome: "x" }, { leitores: { RAW_UTF8: () => "pubblicato il 2026-09-16" } });
  assert.equal(id.SOURCE_DATE_ISO, "2026-09-16");
  assert.equal(id.FACT_TIME, "UNKNOWN", "FACT_TIME != PUBLISHED_AT");
});

console.log("\n13 · FALLBACK — só depois de EMPTY_LIST, e sempre com o sinal de degradação");

const comFallback = (fallback) => ({
  ACQUISITION: {
    STRATEGY: "HTML_LINK_DISCOVERY", INDEX_URL: "https://exemplo.it/idx", LINK_PATTERN: 'href="([^"]*\\.pdf)"',
    FALLBACK: { STRATEGY: "STATIC_ENDPOINT", URL: "https://exemplo.it/fixo.pdf", DEGRADED_REASON: "INDEX_REQUIRES_BROWSER — prova", ...fallback },
  },
});

await TA("índice sem links → corre o fallback e o alvo carrega descoberta_degradada", async () => {
  const r = await alvosDoContrato("X", comFallback({}), { buscar: indiceFalso("<p>nada</p>") });
  assert.equal(r.length, 1);
  assert.equal(r[0].url, "https://exemplo.it/fixo.pdf");
  assert.equal(r[0].descoberta_degradada, "INDEX_REQUIRES_BROWSER — prova");
});

await TA("índice com links → o fallback NÃO corre e não há sinal", async () => {
  const r = await alvosDoContrato("X", comFallback({}), { buscar: indiceFalso('<a href="a.pdf">a</a>') });
  assert.equal(r[0].url, "https://exemplo.it/a.pdf");
  assert.equal(r[0].descoberta_degradada, undefined);
});

await TA("índice INACESSÍVEL → erro, sem fallback: uma fonte caída não se esconde atrás de uma rota adivinhada", async () => {
  const r = await alvosDoContrato("X", comFallback({}), { buscar: async () => ({ status: 503, buf: Buffer.alloc(0) }) });
  assert.ok(r.erro && /inacessivel/.test(r.erro));
});

T("M9 · FALLBACK sem DEGRADED_REASON é contrato inválido; FALLBACK dentro de FALLBACK também", () => {
  assert.throws(() => conferirAquisicao("X", { STRATEGY: "HTML_LINK_DISCOVERY", INDEX_URL: "https://e.it/", LINK_PATTERN: "(x)",
    FALLBACK: { STRATEGY: "STATIC_ENDPOINT", URL: "https://e.it/f.pdf" } }), /DEGRADED_REASON/);
  assert.throws(() => conferirAquisicao("X", { STRATEGY: "HTML_LINK_DISCOVERY", INDEX_URL: "https://e.it/", LINK_PATTERN: "(x)",
    FALLBACK: { STRATEGY: "STATIC_ENDPOINT", URL: "https://e.it/f.pdf", DEGRADED_REASON: "x",
      FALLBACK: { STRATEGY: "STATIC_ENDPOINT", URL: "https://e.it/g.pdf", DEGRADED_REASON: "y" } } }), /FALLBACK dentro de FALLBACK/);
});

console.log("\n14 · SUBCONJUNTOS — a lista curta vive no contrato, e quem corre só a nomeia");

const enumerada = {
  ACQUISITION: {
    STRATEGY: "TEMPLATE_ENUMERATION", TEMPLATE: "https://e.it/z_{NN}.pdf",
    VARS: { NN: { PROVIDER: "RANGE", FROM: 1, TO: 6, PAD: 2 } },
    SUBCONJUNTOS: { PILOTO: { NN: ["01", "04"] } },
  },
};

await TA("sem subconjunto: o provider inteiro; com PILOTO: só os declarados; VARS vai no alvo", async () => {
  const todos = await alvosDoContrato("X", enumerada, {});
  assert.equal(todos.length, 6);
  const piloto = await alvosDoContrato("X", enumerada, { subconjunto: "PILOTO" });
  assert.deepEqual(piloto.map((a) => a.nome), ["z_01.pdf", "z_04.pdf"]);
  assert.deepEqual(piloto.map((a) => a.VARS.NN), ["01", "04"]);
});

await TA("um subconjunto que a fonte não declara é ignorado — a escolha é de quem corre, a lista é do contrato", async () => {
  const r = await alvosDoContrato("X", enumerada, { subconjunto: "NAO_EXISTE" });
  assert.equal(r.length, 6);
});

T("M10 · subconjunto que inventa um valor fora do provider é contrato inválido", () => {
  assert.throws(() => conferirAquisicao("X", {
    STRATEGY: "TEMPLATE_ENUMERATION", TEMPLATE: "https://e.it/z_{NN}.pdf",
    VARS: { NN: { PROVIDER: "ENUM", VALUES: ["01", "02"] } },
    SUBCONJUNTOS: { PILOTO: { NN: ["01", "99"] } },
  }), /não está no provider/);
});

console.log("\n15 · O ADAPTER RECEBE O SEU BLOCO E O RELÓGIO — e não sabe se é fallback");

await TA("CUSTOM_ADAPTER recebe { sourceId, contrato, aq, buscar, agora }", async () => {
  let recebido = null;
  await alvosDoContrato("X", {
    ACQUISITION: { STRATEGY: "CUSTOM_ADAPTER", ADAPTER_ID: "ECO", PARAM: 42 },
  }, { adapters: { ECO: (args) => { recebido = args; return [{ url: "u", nome: "n" }]; } }, agora: () => new Date("2026-09-20T00:00:00Z") });
  assert.equal(recebido.aq.PARAM, 42, "o adapter lê os parâmetros do seu bloco");
  assert.equal(recebido.agora().toISOString(), "2026-09-20T00:00:00.000Z");
});

T("o motor continua sem processo filho e sem relógio próprio", () => {
  const src = readFileSync(new URL("./motor_de_rota.mjs", import.meta.url), "utf8");
  for (const proibido of ["execFileSync", "child_process", "readFileSync", "Date.now()"]) {
    assert.ok(!src.includes(proibido), `o motor contém ${proibido}`);
  }
});

console.log("\n16 · MATCH: \"URL\" — o padrão corre sobre cada endereço absoluto, e o que não é documento fica de fora");

const indiceUrl = {
  ACQUISITION: {
    STRATEGY: "HTML_LINK_DISCOVERY", MATCH: "URL", INDEX_URL: "https://www.exemplo.it/news/",
    LINK_PATTERN: "^https?://(www\\.)?exemplo\\.it/news/[a-z]+-[a-z]+", MAX_TARGETS: 2,
  },
  OUTPUT_TYPE: "HTML",
};
const HTML_INDICE = `
  <link href="/style.css"><a href="/news/">Indice</a>
  <a href="/news/page/2/">seguinte</a><a href="/feed/">rss</a>
  <a href='https://outro.it/news/artigo-externo'>fora</a>
  <a href="/news/primo-articolo">1</a><a href="/news/primo-articolo#top">1 outra vez</a>
  <a href="/news/secondo-articolo/">2</a><a href="/news/terzo-articolo">3</a>`;

await TA("resolve, filtra por host, ignora ativos/paginação/feed e a própria entrada, dedupe, respeita MAX_TARGETS", async () => {
  const r = await alvosDoContrato("X", indiceUrl, { buscar: indiceFalso(HTML_INDICE) });
  assert.deepEqual(r.map((a) => a.url), ["https://www.exemplo.it/news/primo-articolo", "https://www.exemplo.it/news/secondo-articolo/"]);
  assert.deepEqual(r.map((a) => a.nome), ["primo-articolo.html", "secondo-articolo.html"], "artigo sem extensão ganha .html no armazém");
});

await TA("SAME_HOST=false deixa passar outro host; STRIP_SUFFIX tira o /view do Plone", async () => {
  const c = structuredClone(indiceUrl);
  c.ACQUISITION.SAME_HOST = false; c.ACQUISITION.LINK_PATTERN = "artigo-externo|\\.pdf$"; c.ACQUISITION.STRIP_SUFFIX = "/view";
  c.OUTPUT_TYPE = "PDF";
  const r = await alvosDoContrato("X", c, { buscar: indiceFalso(HTML_INDICE + `<a href="/docs/boll.pdf/view">pdf</a>`) });
  assert.deepEqual(r.map((a) => a.url), ["https://outro.it/news/artigo-externo", "https://www.exemplo.it/docs/boll.pdf"]);
  assert.equal(r[1].nome, "boll.pdf");
});

await TA("nenhum endereço casa → EMPTY_LIST, e não a página de entrada como documento", async () => {
  const r = await alvosDoContrato("X", indiceUrl, { buscar: indiceFalso('<a href="/news/">so a entrada</a>') });
  assert.ok(r.erro && /EMPTY_LIST/.test(r.erro));
});

T("M11 · MATCH fora do vocabulário é contrato inválido", () => {
  assert.throws(() => conferirAquisicao("X", { STRATEGY: "HTML_LINK_DISCOVERY", INDEX_URL: "https://e.it/", LINK_PATTERN: "(x)", MATCH: "TEXTO" }), /MATCH/);
});

T("FROM: \"URL\" — a identidade pelo endereço, dita com esse nome, e FACT_TIME continua UNKNOWN", () => {
  const id = identidadeDoContrato("IT-FICT-002", {
    IDENTITY: { STRATEGY: "CONTENT_CAPTURE", CAPTURES: { doc: { FROM: "URL", PATTERN: "^https?://[^/]+/?(.*?)/?$" } },
                DOCUMENT_ID: "IT-FICT-002:URL:{doc.1}" },
  }, { nome: "secondo-articolo.html", url: "https://www.exemplo.it/news/secondo-articolo/" }, { leitores: {} });
  assert.equal(id.DOCUMENT_ID, "IT-FICT-002:URL:news/secondo-articolo");
  assert.equal(id.SOURCE_DATE, null);
  assert.equal(id.FACT_TIME, "UNKNOWN");
});

console.log("\n17 · A TABELA ONBOARDED EXPANDE-SE EM CONTRATOS VÁLIDOS, E NÃO CONTRADIZ NENHUM CONTRATO À MÃO");

T("todos os contratos com ACQUISITION passam na conferência, e a tabela não reescreve o IT-T3-011", () => {
  let n = 0;
  for (const [sid, c] of Object.entries(CONTRACTS)) {
    if (!c.ACQUISITION) continue;
    conferirAquisicao(sid, c.ACQUISITION);
    conferirIdentidade(sid, c.IDENTITY);
    n++;
  }
  assert.ok(n >= 100, `só ${n} contratos executáveis`);
  assert.equal(CONTRACTS["IT-T3-011"].BATCH_ID, undefined, "o contrato à mão do IT-T3-011 foi tocado pela tabela");
  assert.equal(CONTRACTS["IT-T3-011"].IDENTITY.DOCUMENT_ID, "AGRIOS:DIRETTIVE:$1");
});

T("nenhum contrato genérico fabrica tempo ou lugar do facto", () => {
  for (const [sid, c] of Object.entries(CONTRACTS)) {
    if (!c.BATCH_ID) continue;
    assert.ok(String(c.IDENTITY.FACT_TIME).startsWith("UNKNOWN"), `${sid}: FACT_TIME não é UNKNOWN`);
    assert.ok(!("FACT_LOCATION" in c.IDENTITY), `${sid}: IDENTITY declara FACT_LOCATION`);
    // A tabela diz COM QUE a identidade se faz: pelo endereço (URL_PATH) ou por um
    // identificador nativo da plataforma que a LINHA declarou (PLATFORM_NATIVE_ID,
    // BIG-COLLECTION-RELEASE: o videoId do YouTube). Nunca "NAO SEI", nunca calado.
    assert.ok(["URL_PATH", "PLATFORM_NATIVE_ID"].includes(c.IDENTITY_KIND), `${sid}: a identidade não diz com que se faz (${c.IDENTITY_KIND})`);
    if (c.IDENTITY_KIND === "PLATFORM_NATIVE_ID") {
      assert.ok(!c.IDENTITY.DOCUMENT_ID.includes(":URL:"), `${sid}: diz PLATFORM_NATIVE_ID e usa o endereço`);
      assert.ok(/\{[A-Za-z_]+\.\d+\}/.test(c.IDENTITY.DOCUMENT_ID), `${sid}: PLATFORM_NATIVE_ID sem captura no DOCUMENT_ID`);
      assert.ok(!/[?*"<>|]/.test(c.IDENTITY.DOCUMENT_ID), `${sid}: DOCUMENT_ID com caractere que o coletor não consegue pôr em pasta`);
    }
  }
});

console.log(`\n  PASSOU ${ok} · FALHOU ${mau}\n`);
if (mau) process.exit(1);
