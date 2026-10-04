// A PROVA DA FONTE COM ÍNDICE — O CASO DA MICRO-COLETA, PELO CURL, CONTRA UM SERVIDOR LOCAL.
//
//     node provas/recollection_indice_local.mjs
//
// As 8 fontes da coorte da micro-coleta são todas `HTML_LINK_DISCOVERY` com
// `MATCH: "URL"`: abre-se um índice, extraem-se as ligações que casam com
// LINK_PATTERN, e cada ligação é uma matéria. A R1 provou a fonte de endereço
// único; esta prova o índice.
//
// O contrato usado é o de uma fonte REAL da coorte (IT-T10-018, myfruit), com a
// aquisição apontada, em memória, para um servidor em 127.0.0.1 — e restaurado
// no `finally`. A identidade é a genérica da tabela onboarded (pelo endereço),
// a mesma que a fonte usa em produção. A contagem de pedidos é a do SERVIDOR,
// separada em índice e matérias.
//
// ZERO REDE EXTERNA, provado como na R1: proxy de saída para uma porta fechada,
// só 127.0.0.1/localhost fora dele; `EGRESS_IP = NAO SEI`.
//
//   I1  índice com 3 matérias                    -> 1 índice + 3 matérias, NEW=3
//   (cada matéria é ligada DUAS vezes no índice — foto e título — como nos sites reais)
//   I2  o mesmo índice com ruído (data, contador,
//       ligação com #fragmento, ordem trocada)    -> 1 índice + 0 matérias
//   I3  1 matéria nova no topo                    -> 1 índice + 1 matéria, NEW=1
//   I4  a matéria mais antiga sai do índice       -> 1 índice + 0 matérias; nada apagado
//   I5  uma matéria conhecida anunciada sem a barra
//       final (mesma página)                      -> 1 pedido gasto, 0 documentos novos
//                                                    (LIMITE CONHECIDO — ver a rodada)
//   I6  MUTABLE declarado                         -> revalida as conhecidas, com razão;
//       medido para a proposta do ETag (não é defeito: é o custo da declaração)
import { createServer } from "node:http";
import { mkdtempSync, rmSync, readFileSync, existsSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { createHash } from "node:crypto";
import assert from "node:assert/strict";

const RAIZ = mkdtempSync(join(tmpdir(), "recollection-indice-"));
process.env.ITALY_OPS_ROOT = RAIZ;
for (const k of ["http_proxy", "https_proxy", "HTTP_PROXY", "HTTPS_PROXY", "ALL_PROXY", "all_proxy"])
  process.env[k] = "http://127.0.0.1:9";
process.env.NO_PROXY = process.env.no_proxy = "127.0.0.1,localhost";

// ── O SERVIDOR ──────────────────────────────────────────────────────────────
const enchimento = "<p>" + "Testo dell'articolo. ".repeat(80) + "</p>";   // > MIN_BYTES
const MATERIAS = {
  "mele-prezzi-in-calo":   "Prezzi delle mele in calo a settembre",
  "pere-export-germania":  "Export di pere verso la Germania",
  "kiwi-raccolta-anticipata": "Raccolta anticipata del kiwi",
  "uva-da-tavola-record":  "Uva da tavola: campagna record",
};
let INDICE = { lista: [], ruido: 0, barra: {} };
const PEDIDOS = [], ROBOTS_PEDIDOS = [];
const paginaIndice = () => `<!DOCTYPE html><html><head><title>News</title>
<meta property="article:modified_time" content="2026-09-2${INDICE.ruido}T0${INDICE.ruido}:00:00+00:00" /></head><body>
<div class="oggi">Oggi è il ${20 + INDICE.ruido} settembre 2026 · visitatori ${1000 + INDICE.ruido * 37}</div>
<a href="/news/">News</a> <a href="/news/page/2/">Pagina 2</a> <a href="/feed/">RSS</a> <link href="/style.css">
${INDICE.lista.map(s => `<article><a href="/news/${s}${INDICE.barra[s] ?? "/"}"><img src="/img/${s}.jpg"></a>
  <a href="/news/${s}${INDICE.barra[s] ?? "/"}">${MATERIAS[s]}</a>
  <a href="/news/${s}/#commenti">commenti</a></article>`).join("\n")}
${enchimento}</body></html>`;
const paginaMateria = (s) => `<!DOCTYPE html><html><head><title>${MATERIAS[s]}</title></head><body>
<h1>${MATERIAS[s]}</h1><div class="views">${PEDIDOS.length}</div>${enchimento}</body></html>`;
const servidor = createServer((req, res) => {
  const p = req.url;
  // ⚠️ A5 · O COLETOR LE O ROBOTS.TXT ANTES DE PEDIR (a cortesia vive em
  // `baixar()`). Este servidor nao publica robots — 404, «sem ficheiro = sem
  // proibicao» — e conta essas idas A PARTE: as contas desta prova sao de
  // documentos, e continuam exactamente as mesmas.
  if (p === "/robots.txt") { ROBOTS_PEDIDOS.push(Date.now()); res.writeHead(404); res.end("non trovato"); return; }
  PEDIDOS.push(p);
  res.setHeader("Content-Type", "text/html; charset=utf-8");
  if (p === "/news/") { res.end(paginaIndice()); return; }
  const m = p.match(/^\/news\/([a-z-]+)\/?$/);
  if (m && MATERIAS[m[1]]) { res.end(paginaMateria(m[1])); return; }
  res.writeHead(404); res.end("non trovato");
});
await new Promise(r => servidor.listen(0, "127.0.0.1", r));
const BASE = `http://127.0.0.1:${servidor.address().port}`;

const { executarRodada } = await import("../coleta/italy_pilot_collect.mjs");
const { CONTRACTS } = await import("../regras/italy_contracts.mjs");
const FONTE = "IT-T10-018";
assert.ok(CONTRACTS[FONTE], `${FONTE} tem de ter contrato nesta linha`);
assert.equal(CONTRACTS[FONTE].ACQUISITION.STRATEGY, "HTML_LINK_DISCOVERY");
assert.equal(CONTRACTS[FONTE].ACQUISITION.MATCH, "URL");
const ORIGINAL = { ACQUISITION: CONTRACTS[FONTE].ACQUISITION, RECOLLECTION: CONTRACTS[FONTE].RECOLLECTION,
                   CANONICAL_ENTRY_URL: CONTRACTS[FONTE].CANONICAL_ENTRY_URL };
CONTRACTS[FONTE].ACQUISITION = { ...ORIGINAL.ACQUISITION, INDEX_URL: `${BASE}/news/`,
  LINK_PATTERN: String.raw`^http://127\.0\.0\.1:\d+/news/[a-z0-9]+(?:-[a-z0-9]+)+/?$` };
CONTRACTS[FONTE].CANONICAL_ENTRY_URL = `${BASE}/news/`;
CONTRACTS[FONTE].RECOLLECTION = undefined;          // a coorte: 7 das 8 sem bloco declarado

const livro = () => {
  const f = join(RAIZ, "data/collection-ledger/italy/observations.ndjson");
  return existsSync(f) ? readFileSync(f, "utf8").split("\n").filter(Boolean).map(JSON.parse) : [];
};
async function rodada(nome) {
  const antes = PEDIDOS.length, robotsAntes = ROBOTS_PEDIDOS.length;
  const { resumo } = await executarRodada({ runId: `PROVA_IDX_${nome}_${Date.now()}`, apenas: [FONTE],
                                            pularParse: true, nota: `prova indice local ${nome}` });
  const feitos = PEDIDOS.slice(antes);
  return { c: resumo.contadores, resumo, indice: feitos.filter(p => p === "/news/").length,
           materias: feitos.filter(p => p !== "/news/"), feitos, robots: ROBOTS_PEDIDOS.length - robotsAntes };
}

let passou = 0, falhou = 0;
const t = (nome, fn) => {
  try { fn(); passou++; console.log(`  ok    ${nome}`); }
  catch (e) { falhou++; console.log(`  FALHA ${nome}\n        ${e.message}`); }
};
const censo = [];
const anota = (nome, r) => censo.push(`  ${nome.padEnd(3)} indice=${r.indice} materias=${r.materias.length}` +
  `  NEW=${r.c.NEW_DOCUMENTS} SKIPPED_KNOWN=${r.c.SKIPPED_KNOWN} REVALIDATED=${r.c.REVALIDATED} SEEN_AGAIN=${r.c.SEEN_AGAIN}` +
  ` CHANGED=${r.c.CHANGED_IN_PLACE} INDEX_REQUESTS=${r.c.INDEX_REQUESTS}  UNNECESSARY_REFETCHES=${r.c.UNNECESSARY_REFETCHES}`);

try {
  console.log(`\n(servidor ${BASE} · raiz ${RAIZ})`);

  console.log("\n══ I1 · índice com 3 matérias ═══════════════════════════════════");
  INDICE = { lista: ["mele-prezzi-in-calo", "pere-export-germania", "kiwi-raccolta-anticipata"], ruido: 0, barra: {} };
  const i1 = await rodada("I1"); anota("I1", i1);
  t("I1: 1 índice + 3 matérias, 3 documentos novos", () => {
    assert.equal(i1.indice, 1); assert.equal(i1.materias.length, 3);
    assert.equal(i1.c.NEW_DOCUMENTS, 3); assert.equal(i1.c.RAW_OBJECTS_CREATED, 3);
    assert.equal(i1.c.INDEX_REQUESTS, 1, "o contador do coletor tem de bater com o servidor");
  });
  t("I1: paginação, feed, css e a própria entrada não são matérias", () => {
    assert.ok(i1.materias.every(p => /^\/news\/[a-z-]+\/$/.test(p)), JSON.stringify(i1.materias));
  });
  t("zero rede externa: EGRESS_IP = NAO SEI", () => assert.equal(i1.resumo.EGRESS_IP, "NAO SEI"));
  t("A5: I1 leu o robots UMA vez, contado a parte (ROBOTS_REQUESTS), nao como indice", () => {
    assert.equal(i1.robots, 1); assert.equal(i1.c.ROBOTS_REQUESTS, 1);
  });

  console.log("\n══ I2 · o mesmo índice, com ruído ═══════════════════════════════");
  INDICE = { lista: ["kiwi-raccolta-anticipata", "mele-prezzi-in-calo", "pere-export-germania"], ruido: 3, barra: {} };
  const i2 = await rodada("I2"); anota("I2", i2);
  t("I2: o índice é pedido (é preciso, para ver o que é novo)", () => assert.equal(i2.indice, 1));
  t("I2: 0 matérias conhecidas pedidas", () => {
    assert.equal(i2.materias.length, 0, JSON.stringify(i2.materias));
    assert.equal(i2.c.SKIPPED_KNOWN, 3); assert.equal(i2.c.UNNECESSARY_REFETCHES, 0);
  });
  t("I2: ruído do índice (data, contador, #commenti, ordem) não gera falso novo", () => {
    assert.equal(i2.c.NEW_DOCUMENTS, 0); assert.equal(i2.c.DETAIL_NEW, 0); assert.equal(i2.c.RAW_OBJECTS_CREATED, 0);
  });

  console.log("\n══ I3 · uma matéria nova no topo ════════════════════════════════");
  INDICE = { lista: ["uva-da-tavola-record", "kiwi-raccolta-anticipata", "mele-prezzi-in-calo", "pere-export-germania"], ruido: 4, barra: {} };
  const i3 = await rodada("I3"); anota("I3", i3);
  t("I3: 1 índice + só a matéria nova", () => {
    assert.equal(i3.indice, 1);
    assert.deepEqual(i3.materias, ["/news/uva-da-tavola-record/"]);
    assert.equal(i3.c.NEW_DOCUMENTS, 1); assert.equal(i3.c.SKIPPED_KNOWN, 3);
  });

  console.log("\n══ I4 · a matéria mais antiga sai do índice ═════════════════════");
  const antesI4 = livro().filter(l => String(l.SOURCE_URL || "").includes("pere-export-germania") && l.RAW_PATH);
  INDICE = { lista: ["uva-da-tavola-record", "kiwi-raccolta-anticipata", "mele-prezzi-in-calo"], ruido: 5, barra: {} };
  const linhasAntes = livro().length;
  const i4 = await rodada("I4"); anota("I4", i4);
  t("I4: 0 matérias pedidas", () => { assert.equal(i4.indice, 1); assert.equal(i4.materias.length, 0); });
  t("I4: a matéria que saiu do índice NÃO é apagada — livro e bytes intactos", () => {
    assert.equal(antesI4.length, 1);
    const [o] = antesI4;
    assert.ok(existsSync(o.RAW_PATH), `sumiu do armazém: ${o.RAW_PATH}`);
    assert.equal(createHash("sha256").update(readFileSync(o.RAW_PATH)).digest("hex"), o.RAW_SHA256);
    const l = livro();
    assert.ok(l.length >= linhasAntes, "o livro encolheu");
    assert.ok(l.some(x => x.RAW_PATH === o.RAW_PATH), "a linha da matéria saiu do livro");
    assert.ok(!l.slice(linhasAntes).some(x => String(x.SOURCE_URL || "").includes("pere-export-germania")),
      "a corrida não deve escrever nada sobre a matéria que saiu");
  });

  console.log("\n══ I5 · uma matéria conhecida anunciada sem a barra final ═══════");
  INDICE = { lista: ["uva-da-tavola-record", "kiwi-raccolta-anticipata", "mele-prezzi-in-calo"], ruido: 6,
             barra: { "mele-prezzi-in-calo": "" } };
  const i5 = await rodada("I5"); anota("I5", i5);
  // ⚠️ LIMITE CONHECIDO, MEDIDO E NÃO CORRIGIDO (R2, 2026-09-23). A memória do
  // coletor é por endereço EXACTO. A mesma página anunciada com outra grafia
  // (sem a barra final) é pedida outra vez: 1 pedido gasto. O documento NÃO
  // nasce duas vezes — a identidade genérica tira a barra e dá SEEN_AGAIN — e
  // o medidor UNNECESSARY_REFETCHES não vê este pedido (conta-o como endereço
  // novo). Nos quatro livros reais desta máquina (521, 574, 144 e 20
  // observações) não há UM endereço com duas grafias: corrigir seria por
  // ansiedade. Estas verificações descrevem o comportamento de hoje; se alguém
  // o corrigir, a primeira acende e manda actualizar esta prova e o know-how.
  t("I5 (limite conhecido): outra grafia do mesmo endereço custa 1 pedido", () => {
    assert.deepEqual(i5.materias, ["/news/mele-prezzi-in-calo"]);
    assert.equal(i5.c.DETAIL_NEW, 1, "o medidor conta-o como endereço novo, não como refetch");
  });
  t("I5: e não nasce documento novo (FALSO_NOVO = 0)", () => {
    assert.equal(i5.c.NEW_DOCUMENTS, 0); assert.equal(i5.c.RAW_OBJECTS_CREATED, 0);
    assert.equal(i5.c.SEEN_AGAIN, 1);
  });

  console.log("\n══ I6 · MUTABLE declarado — o custo medido ══════════════════════");
  CONTRACTS[FONTE].RECOLLECTION = { DETAIL_CONTENT: "MUTABLE" };
  INDICE = { lista: ["uva-da-tavola-record", "kiwi-raccolta-anticipata", "mele-prezzi-in-calo"], ruido: 7, barra: {} };
  const i6 = await rodada("I6"); anota("I6", i6);
  t("I6: revalida as 3 do índice, com razão nomeada, e não as dá por mudadas", () => {
    assert.equal(i6.materias.length, 3); assert.equal(i6.c.REVALIDATED, 3);
    assert.equal(i6.c.UNNECESSARY_REFETCHES, 0);
    assert.equal(i6.c.CHANGED_IN_PLACE, 0, "o contador de visitas da matéria é ruído");
    assert.equal(i6.c.RAW_OBJECTS_CREATED, 0);
  });

  console.log("\n══ CENSO ═══════════════════════════════════════════════════════");
  for (const l of censo) console.log(l);
  t("UNNECESSARY_REFETCHES = 0 em TODAS as rodadas", () => {
    assert.ok(censo.every(l => l.endsWith("UNNECESSARY_REFETCHES=0")));
  });
} finally {
  Object.assign(CONTRACTS[FONTE], ORIGINAL);
  if (ORIGINAL.RECOLLECTION === undefined) delete CONTRACTS[FONTE].RECOLLECTION;
  servidor.close();
  rmSync(RAIZ, { recursive: true, force: true });
}
console.log(`\n  ${passou} passaram, ${falhou} falharam`);
process.exit(falhou ? 1 : 0);
