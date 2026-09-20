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

TA("M3 · nenhum contrato aponta para caminho barrado pelo robots do YouTube", async () => {
  // A regressao que esta suite nao apanhava: um ACQUISITION pode estar
  // perfeitamente formado, responder 200, e mesmo assim ser ILEGAL.
  // `feeds/videos.xml` esta em `Disallow` no robots.txt do YouTube e o portao
  // canonico recusa-o — mas `conferirAquisicao` so valida a FORMA.
  //
  //     BEM FORMADO != PERMITIDO.
  const { CONTRACTS } = await import("./italy_contracts.mjs");
  const barrados = [];
  for (const [id, c] of Object.entries(CONTRACTS)) {
    const aq = c && c.ACQUISITION;
    if (!aq) continue;
    const alvo = `${aq.INDEX_URL || ""} ${aq.URL || ""} ${aq.TEMPLATE || ""}`;
    if (/youtube\.com\/(feeds\/videos\.xml|results|youtubei|api\/|get_video|comment)/.test(alvo)) {
      barrados.push(`${id}: ${alvo.trim()}`);
    }
  }
  assert.deepEqual(barrados, [],
    "contrato a apontar para caminho que o robots.txt do YouTube barra");
});

TA("M4 · todo ADAPTER_ID nomeado existe no registry do coletor", async () => {
  // Um contrato pode nomear um adapter que ninguem registou. O motor so
  // descobre isso a meio de uma corrida; aqui descobre-se antes.
  const { CONTRACTS } = await import("./italy_contracts.mjs");
  const src = readFileSync(
    new URL("../coleta/italy_pilot_collect.mjs", import.meta.url), "utf8");
  const orfaos = [];
  for (const [id, c] of Object.entries(CONTRACTS)) {
    const aq = c && c.ACQUISITION;
    if (!aq || aq.STRATEGY !== "CUSTOM_ADAPTER") continue;
    if (!src.includes(`"${aq.ADAPTER_ID}"`)) orfaos.push(`${id} -> ${aq.ADAPTER_ID}`);
  }
  assert.deepEqual(orfaos, [], "ADAPTER_ID nomeado no contrato sem entrada no registry");
});

// ⚠️ O SUMARIO TEM DE ESPERAR PELOS TESTES ASSINCRONOS.
// Medido: com `TA` no ficheiro, o sumario corria no primeiro tick e imprimia
// «PASSOU 23 · FALHOU 0» ANTES de os TA terminarem — e um TA reprovado nao
// mudava o codigo de saida. A suite dava exit 0 com um FAIL no ecra.
//
//     UM SUMARIO QUE NAO ESPERA MEDE MENOS TESTES DO QUE CORREU.
//     UM RUNNER QUE SAI 0 COM FAIL NO ECRA NAO E UM PORTAO.
//
// `setImmediate` nao bastava: os TA fazem `await import(...)`, que resolve em
// microtasks encadeadas. Uma volta explicita pela fila de promessas garante
// que todos ja registaram o seu resultado.
await new Promise((r) => setTimeout(r, 0));
console.log(`\n  PASSOU ${ok} · FALHOU ${mau}\n`);
if (mau) process.exit(1);
