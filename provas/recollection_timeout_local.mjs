// A PROVA DO SITE QUE DEMORA E NÃO RESPONDE — TIMEOUT, NÃO 503.
//
//     node provas/recollection_timeout_local.mjs
//
// Um 503 responde depressa; um site pendurado não responde nunca. O coletor
// limita CADA pedido (`curl --max-time 90`, e uma segunda tentativa porque o
// código 28 — timeout — é transitório): 2 × 90 s = 180 s por endereço. O que
// esta prova mede é o que acontece à FONTE: com 30 matérias no índice (o
// MAX_TARGETS da maior parte da coorte) e o site pendurado, 30 × 180 s são
// 90 minutos numa só fonte, numa só corrida.
//
// Servidor local em 127.0.0.1 que aceita a ligação e não responde; rede externa
// fechada como na R1/R2 (proxy para porta fechada). Contrato de uma fonte REAL
// da coorte (IT-T10-018), apontado em memória para o servidor e restaurado.
//
//   T1  índice responde; as 3 matérias penduram    -> FAILED com motivo (timeout),
//       nenhuma vira documento nem fica conhecida; a fonte pára depois do
//       PRIMEIRO timeout — as outras ficam para a próxima corrida, contadas
//       tempo da fonte <= 1 índice + 1 matéria pendurada
//   T2  o site volta (uma matéria demora 3 s mas responde)
//                                                  -> as 3 são colhidas: nada perdido
//   T3  o próprio índice pendura                   -> DISCOVERY_FAILED com motivo,
//       tempo <= 1 pedido pendurado
import { createServer } from "node:http";
import { mkdtempSync, rmSync, readFileSync, existsSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import assert from "node:assert/strict";

const RAIZ = mkdtempSync(join(tmpdir(), "recollection-timeout-"));
process.env.ITALY_OPS_ROOT = RAIZ;
for (const k of ["http_proxy", "https_proxy", "HTTP_PROXY", "HTTPS_PROXY", "ALL_PROXY", "all_proxy"])
  process.env[k] = "http://127.0.0.1:9";
process.env.NO_PROXY = process.env.no_proxy = "127.0.0.1,localhost";

// Um pedido pendurado custa no máximo 2 tentativas × 90 s. A folga cobre o
// arranque do curl e a escrita do livro.
const PEDIDO_PENDURADO_MAX_S = 2 * 90;
const FOLGA_S = 25;

const enchimento = "<p>" + "Testo dell'articolo. ".repeat(80) + "</p>";
const SLUGS = ["mele-prezzi-in-calo", "pere-export-germania", "kiwi-raccolta-anticipata"];
let MODO = { indice: "ok", materias: "pendura", lenta: null };
const PEDIDOS = [], SOCKETS = new Set();
const servidor = createServer((req, res) => {
  const p = req.url;
  PEDIDOS.push(p);
  const pendura = p === "/news/" ? MODO.indice === "pendura" : MODO.materias === "pendura";
  if (pendura) return;                                   // aceita e nunca responde
  res.setHeader("Content-Type", "text/html; charset=utf-8");
  if (p === "/news/") {
    res.end(`<!DOCTYPE html><html><body>${SLUGS.map(s => `<a href="/news/${s}/">${s}</a>`).join("\n")}${enchimento}</body></html>`);
    return;
  }
  const s = (p.match(/^\/news\/([a-z-]+)\/$/) || [])[1];
  if (!SLUGS.includes(s)) { res.writeHead(404); res.end("non trovato"); return; }
  const corpo = `<!DOCTYPE html><html><head><title>${s}</title></head><body><h1>${s}</h1>${enchimento}</body></html>`;
  if (MODO.lenta === s) setTimeout(() => res.end(corpo), 3000); else res.end(corpo);
});
servidor.on("connection", s => { SOCKETS.add(s); s.on("close", () => SOCKETS.delete(s)); });
await new Promise(r => servidor.listen(0, "127.0.0.1", r));
const BASE = `http://127.0.0.1:${servidor.address().port}`;

const { executarRodada } = await import("../coleta/italy_pilot_collect.mjs");
const { CONTRACTS } = await import("../regras/italy_contracts.mjs");
const FONTE = "IT-T10-018";
const ORIGINAL = { ACQUISITION: CONTRACTS[FONTE].ACQUISITION, CANONICAL_ENTRY_URL: CONTRACTS[FONTE].CANONICAL_ENTRY_URL };
CONTRACTS[FONTE].ACQUISITION = { ...ORIGINAL.ACQUISITION, INDEX_URL: `${BASE}/news/`,
  LINK_PATTERN: String.raw`^http://127\.0\.0\.1:\d+/news/[a-z0-9]+(?:-[a-z0-9]+)+/?$` };
CONTRACTS[FONTE].CANONICAL_ENTRY_URL = `${BASE}/news/`;

const livro = () => {
  const f = join(RAIZ, "data/collection-ledger/italy/observations.ndjson");
  return existsSync(f) ? readFileSync(f, "utf8").split("\n").filter(Boolean).map(JSON.parse) : [];
};
async function rodada(nome) {
  const antes = PEDIDOS.length, linhas = livro().length, t0 = Date.now();
  const { resumo, detalhes } = await executarRodada({ runId: `PROVA_TO_${nome}_${Date.now()}`, apenas: [FONTE],
                                                      pularParse: true, nota: `prova timeout local ${nome}` });
  const s = (Date.now() - t0) / 1000;
  for (const k of SOCKETS) k.destroy();                  // larga as ligações penduradas
  const feitos = PEDIDOS.slice(antes);
  return { c: resumo.contadores, resumo, detalhes, segundos: s, novas: livro().slice(linhas),
           indice: feitos.filter(p => p === "/news/").length, materias: feitos.filter(p => p !== "/news/") };
}

let passou = 0, falhou = 0;
const t = (nome, fn) => {
  try { fn(); passou++; console.log(`  ok    ${nome}`); }
  catch (e) { falhou++; console.log(`  FALHA ${nome}\n        ${e.message}`); }
};
const censo = [];
const anota = (nome, r) => censo.push(`  ${nome} ${r.segundos.toFixed(0).padStart(4)} s  indice=${r.indice} materias=${r.materias.length}` +
  `  NEW=${r.c.NEW_DOCUMENTS} FAILED=${r.c.FAILED} ADIADAS=${r.c.DETAIL_DEFERRED_AFTER_TIMEOUT ?? "—"}  UNNECESSARY_REFETCHES=${r.c.UNNECESSARY_REFETCHES}`);

try {
  console.log(`\n(servidor ${BASE} · raiz ${RAIZ})`);

  console.log("\n══ T1 · o índice responde, as matérias penduram ═════════════════");
  MODO = { indice: "ok", materias: "pendura", lenta: null };
  const t1 = await rodada("T1"); anota("T1", t1);
  t(`T1: a fonte não custa mais que 1 índice + 1 matéria pendurada (<= ${PEDIDO_PENDURADO_MAX_S + FOLGA_S} s)`, () => {
    assert.ok(t1.segundos <= PEDIDO_PENDURADO_MAX_S + FOLGA_S, `a fonte levou ${t1.segundos.toFixed(0)} s`);
  });
  t("T1: o timeout é FAILED com motivo, no livro", () => {
    const falhas = t1.novas.filter(o => o.OBSERVATION_RESULT === "TRANSPORT_OR_EMPTY");
    assert.ok(falhas.length >= 1, JSON.stringify(t1.novas.map(o => o.OBSERVATION_RESULT)));
    assert.ok(falhas.every(o => o.HEALTH_STATE === "FAILED" && /timed out|\(28\)/i.test(o.motivo)),
      JSON.stringify(falhas.map(o => o.motivo)));
    assert.ok(t1.c.FAILED >= 1);
  });
  t("T1: nenhuma matéria vira documento nem fica conhecida", () => {
    assert.equal(t1.c.NEW_DOCUMENTS, 0); assert.equal(t1.c.RAW_OBJECTS_CREATED, 0);
    assert.ok(t1.novas.every(o => o.DOCUMENT_ID == null));
  });
  t("T1: as matérias não tentadas ficam contadas e fora do livro (não viram NEVER)", () => {
    assert.equal(t1.c.DETAIL_DEFERRED_AFTER_TIMEOUT, SLUGS.length - 1);
    const adiadas = t1.detalhes.filter(d => d.DECISAO === "DEFERRED_AFTER_TIMEOUT");
    assert.equal(adiadas.length, SLUGS.length - 1);
    const noLivro = new Set(t1.novas.map(o => o.SOURCE_URL));
    assert.ok(adiadas.every(d => !noLivro.has(d.SOURCE_URL)), "uma adiada não é observação");
  });

  console.log("\n══ T2 · o site volta (uma matéria demora 3 s) ═══════════════════");
  MODO = { indice: "ok", materias: "ok", lenta: "pere-export-germania" };
  const t2 = await rodada("T2"); anota("T2", t2);
  t("T2: as 3 são colhidas — a que falhou e as adiadas", () => {
    assert.equal(t2.materias.length, 3); assert.equal(t2.c.NEW_DOCUMENTS, 3); assert.equal(t2.c.FAILED, 0);
    assert.equal(t2.c.UNNECESSARY_REFETCHES, 0);
  });
  t("T2: a lenta (3 s) não é timeout", () => {
    assert.ok(t2.novas.some(o => String(o.SOURCE_URL).includes("pere-export-germania") && o.RAW_PATH));
  });

  console.log("\n══ T3 · o próprio índice pendura ════════════════════════════════");
  MODO = { indice: "pendura", materias: "ok", lenta: null };
  const t3 = await rodada("T3"); anota("T3", t3);
  t("T3: DISCOVERY_FAILED com motivo, e nada pedido às matérias", () => {
    assert.equal(t3.materias.length, 0);
    const [o] = t3.novas;
    assert.equal(o.OBSERVATION_RESULT, "DISCOVERY_FAILED");
    assert.match(o.motivo, /indice inacessivel/);
  });
  t(`T3: tempo <= 1 pedido pendurado (<= ${PEDIDO_PENDURADO_MAX_S + FOLGA_S} s)`, () => {
    assert.ok(t3.segundos <= PEDIDO_PENDURADO_MAX_S + FOLGA_S, `levou ${t3.segundos.toFixed(0)} s`);
  });

  console.log("\n══ CENSO ═══════════════════════════════════════════════════════");
  for (const l of censo) console.log(l);
} finally {
  Object.assign(CONTRACTS[FONTE], ORIGINAL);
  for (const k of SOCKETS) k.destroy();
  servidor.close();
  rmSync(RAIZ, { recursive: true, force: true });
}
console.log(`\n  ${passou} passaram, ${falhou} falharam`);
process.exit(falhou ? 1 : 0);
