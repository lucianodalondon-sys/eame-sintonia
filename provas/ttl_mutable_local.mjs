// A PROVA DO PRAZO DE VALIDADE (TTL) NAS FONTES MUTABLE — PELO CURL, CONTRA UM SERVIDOR LOCAL.
//
//     node provas/ttl_mutable_local.mjs
//
// Duas fontes na MESMA corrida, as duas com o contrato REAL desta linha:
//   IT-T7-017 (Riunite)  MUTABLE com TTL_SECONDS = 3 dias (T1) — índice + 3 matérias
//   IT-T3-005 (Terre)    MUTABLE SEM prazo — o boletim reescrito na mesma morada;
//                        é o controlo: tem de continuar a ser revisitado SEMPRE
// Só os endereços são apontados, em memória, para 127.0.0.1 (e restaurados).
//
// ⚠️ O TEMPO É SIMULADO NO LIVRO, NÃO NO RELÓGIO. Não se esperam três dias: entre
// corridas, as datas CAPTURED_AT do livro DESCARTÁVEL desta prova recuam N dias
// — é exactamente o que o livro diria se a última visita tivesse sido há N dias.
// O coletor e a regra não são tocados; o relógio deles é o de verdade.
//
// A mesma história corre DUAS vezes: com o prazo (T1) e sem ele (a regra de
// antes, TTL anulado em memória) — e comparam-se os pedidos do servidor.
//
//   C1 dia 0      tudo novo
//   C2 dia 0      logo a seguir: Riunite 0 matérias (T1) · boletim revisitado
//                 → a matéria A é EDITADA no servidor
//   C3 dia 2      dentro do prazo: Riunite 0 matérias — a edição ainda NÃO foi vista
//                 (FALSE_DOCUMENT_UNCHANGED = 1, contado e com idade)
//   C4 dia 3,5    prazo vencido: revisita as 3 por TTL_EXPIRED — A dá CHANGED
//   C5 dia 3,5    logo a seguir: 0 outra vez
import { createServer } from "node:http";
import { mkdtempSync, rmSync, readFileSync, writeFileSync, existsSync, readdirSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import assert from "node:assert/strict";

const RAIZ = mkdtempSync(join(tmpdir(), "ttl-mutable-"));
process.env.ITALY_OPS_ROOT = RAIZ;
for (const k of ["http_proxy", "https_proxy", "HTTP_PROXY", "HTTPS_PROXY", "ALL_PROXY", "all_proxy"])
  process.env[k] = "http://127.0.0.1:9";
process.env.NO_PROXY = process.env.no_proxy = "127.0.0.1,localhost";

// ── O SERVIDOR ──────────────────────────────────────────────────────────────
const enchimento = "<p>" + "Testo dell'articolo. ".repeat(80) + "</p>";
const SLUGS = ["vinitaly-2026-riunite", "nuova-annata-lambrusco", "premio-tre-bicchieri"];
let EDITADA = false, VISITAS = 0;
const PEDIDOS = [];
const pagina = (s) => `<!DOCTYPE html><html><head><title>${s}</title></head><body><h1>${s}</h1>
<div class="views">${VISITAS}</div>
<p id="materia">${s === SLUGS[0] && EDITADA ? "Aggiornamento: lo stand sarà nel padiglione 7." : "Testo originale."}</p>
${enchimento}</body></html>`;
const boletim = () => `<!DOCTYPE html><html><body><p>Bollettino del periodo dal 01-09-2026 al 07-09-2026</p>
<p id="materia">Infestazione attiva: bassa</p><div class="views">${VISITAS}</div></body></html>`;
const servidor = createServer((req, res) => {
  VISITAS++;
  PEDIDOS.push(req.url);
  res.setHeader("Content-Type", "text/html; charset=utf-8");
  if (req.url === "/news-e-eventi/")
    return res.end(`<!DOCTYPE html><html><body>${SLUGS.map(s => `<a href="/news-e-eventi/${s}/">${s}</a>`).join("\n")}${enchimento}</body></html>`);
  if (req.url === "/monitoraggio") return res.end(Buffer.from(boletim(), "latin1"));
  const s = (req.url.match(/^\/news-e-eventi\/([a-z0-9-]+)\/$/) || [])[1];
  if (SLUGS.includes(s)) return res.end(pagina(s));
  res.writeHead(404); res.end("non trovato");
});
await new Promise(r => servidor.listen(0, "127.0.0.1", r));
const BASE = `http://127.0.0.1:${servidor.address().port}`;

const { executarRodada } = await import("../coleta/italy_pilot_collect.mjs");
const { CONTRACTS } = await import("../regras/italy_contracts.mjs");
const RIUNITE = "IT-T7-017", BOLETIM = "IT-T3-005";
// O contrato desta linha TEM de trazer o prazo — é isso que se prova.
assert.equal(CONTRACTS[RIUNITE].RECOLLECTION.DETAIL_CONTENT, "MUTABLE");
assert.equal(CONTRACTS[RIUNITE].RECOLLECTION.TTL_SECONDS, 3 * 86400, "o contrato da Riunite não declara o prazo de 3 dias");
assert.equal(CONTRACTS[BOLETIM].RECOLLECTION.DETAIL_CONTENT, "MUTABLE");
assert.ok(!CONTRACTS[BOLETIM].RECOLLECTION.TTL_SECONDS, "o boletim ganhou prazo — o controlo deixou de o ser");
const ORIG = {
  r: { ACQUISITION: CONTRACTS[RIUNITE].ACQUISITION, CANONICAL_ENTRY_URL: CONTRACTS[RIUNITE].CANONICAL_ENTRY_URL,
       RECOLLECTION: CONTRACTS[RIUNITE].RECOLLECTION },
  b: { CANONICAL_ENTRY_URL: CONTRACTS[BOLETIM].CANONICAL_ENTRY_URL },
};
CONTRACTS[RIUNITE].ACQUISITION = { ...ORIG.r.ACQUISITION, INDEX_URL: `${BASE}/news-e-eventi/`,
  LINK_PATTERN: String.raw`^http://127\.0\.0\.1:\d+/news-e-eventi/[a-z0-9]+(?:-[a-z0-9]+)+/?$` };
CONTRACTS[RIUNITE].CANONICAL_ENTRY_URL = `${BASE}/news-e-eventi/`;
CONTRACTS[BOLETIM].CANONICAL_ENTRY_URL = `${BASE}/monitoraggio`;

const LIVRO = join(RAIZ, "data/collection-ledger/italy/observations.ndjson");
const livro = () => existsSync(LIVRO) ? readFileSync(LIVRO, "utf8").split("\n").filter(Boolean).map(JSON.parse) : [];
function envelhecer(dias) {                   // a última visita passa a ter sido há `dias`
  const ms = dias * 86400e3;
  const linhas = livro().map(o => ({ ...o,
    ...(o.CAPTURED_AT ? { CAPTURED_AT: new Date(Date.parse(o.CAPTURED_AT) - ms).toISOString() } : {}) }));
  writeFileSync(LIVRO, linhas.map(o => JSON.stringify(o)).join("\n") + "\n");
}
async function corrida(nome) {
  const antes = PEDIDOS.length;
  const { resumo } = await executarRodada({ runId: `PROVA_TTL_${nome}_${Date.now()}`, apenas: [RIUNITE, BOLETIM],
                                            pularParse: true, nota: `prova ttl mutable ${nome}` });
  const f = PEDIDOS.slice(antes);
  return { c: resumo.contadores, materias: f.filter(p => /^\/news-e-eventi\/.+\/$/.test(p)).length,
           boletim: f.filter(p => p === "/monitoraggio").length, razoes: resumo.contadores.REVISIT_REASONS };
}
function limpar() {
  for (const d of readdirSync(RAIZ)) rmSync(join(RAIZ, d), { recursive: true, force: true });
  EDITADA = false;
}

async function historia(comPrazo) {
  limpar();
  CONTRACTS[RIUNITE].RECOLLECTION = comPrazo ? ORIG.r.RECOLLECTION : { ...ORIG.r.RECOLLECTION, TTL_SECONDS: null };
  const h = {};
  h.C1 = await corrida("C1");
  h.C2 = await corrida("C2");
  EDITADA = true;
  envelhecer(2);
  h.C3 = await corrida("C3");
  h.C3_EDICAO_NAO_VISTA = !livro().some(o => o.SOURCE_URL?.includes(SLUGS[0]) && o.OBSERVATION_RESULT === "DOCUMENT_CHANGED_IN_PLACE");
  envelhecer(1.5);
  h.C4 = await corrida("C4");
  h.C4_EDICAO_VISTA = livro().some(o => o.SOURCE_URL?.includes(SLUGS[0]) && o.OBSERVATION_RESULT === "DOCUMENT_CHANGED_IN_PLACE");
  h.C5 = await corrida("C5");
  h.TOTAL_MATERIAS = ["C1", "C2", "C3", "C4", "C5"].reduce((s, k) => s + h[k].materias, 0);
  return h;
}

let passou = 0, falhou = 0;
const t = (nome, fn) => {
  try { fn(); passou++; console.log(`  ok    ${nome}`); }
  catch (e) { falhou++; console.log(`  FALHA ${nome}\n        ${e.message}`); }
};

try {
  console.log(`\n(servidor ${BASE} · raiz ${RAIZ})`);
  const T1 = await historia(true);
  const ANTES = await historia(false);

  console.log("\n══ COM O PRAZO (T1) ═════════════════════════════════════════════");
  t("C1: tudo novo — 3 matérias + 1 boletim", () => {
    assert.equal(T1.C1.materias, 3); assert.equal(T1.C1.boletim, 1); assert.equal(T1.C1.c.NEW_DOCUMENTS, 4);
  });
  t("C2 (logo a seguir): 0 matérias da Riunite — dentro do prazo", () => {
    assert.equal(T1.C2.materias, 0); assert.equal(T1.C2.c.SKIPPED_KNOWN, 3);
  });
  t("C2: o boletim MUTABLE sem prazo continua revisitado", () => {
    assert.equal(T1.C2.boletim, 1); assert.equal(T1.C2.razoes.CONTRACT_DECLARES_MUTABLE, 1);
  });
  t("C3 (dia 2): 0 matérias — a edição de A ainda não foi vista (atraso contado)", () => {
    assert.equal(T1.C3.materias, 0); assert.equal(T1.C3_EDICAO_NAO_VISTA, true);
    assert.equal(T1.C3.boletim, 1);
  });
  t("C4 (dia 3,5): prazo vencido — as 3 revisitadas por TTL_EXPIRED", () => {
    assert.equal(T1.C4.materias, 3); assert.equal(T1.C4.c.REVALIDATED, 4);
    assert.equal(T1.C4.razoes.TTL_EXPIRED, 3); assert.equal(T1.C4.razoes.CONTRACT_DECLARES_MUTABLE, 1);
  });
  t("C4: a matéria editada é apanhada na 1.ª corrida depois do prazo", () => {
    assert.equal(T1.C4_EDICAO_VISTA, true); assert.equal(T1.C4.c.CHANGED_IN_PLACE, 1);
  });
  t("C4: as outras duas e o boletim dão SEEN_AGAIN (ruído não é mudança)", () => {
    assert.equal(T1.C4.c.SEEN_AGAIN, 3);
  });
  t("C5 (logo a seguir): 0 matérias outra vez", () => {
    assert.equal(T1.C5.materias, 0); assert.equal(T1.C5.boletim, 1);
  });
  t("UNNECESSARY_REFETCHES = 0 em todas as corridas", () => {
    for (const k of ["C1", "C2", "C3", "C4", "C5"]) assert.equal(T1[k].c.UNNECESSARY_REFETCHES, 0, k);
  });

  console.log("\n══ ANTES (a mesma história, sem prazo) ══════════════════════════");
  t("sem prazo: revisita as 3 em todas as corridas depois da 1.ª", () => {
    for (const k of ["C2", "C3", "C4", "C5"]) assert.equal(ANTES[k].materias, 3, k);
  });
  t("sem prazo: a edição é vista na C3 (dia 2) — é esse o atraso que o prazo compra", () => {
    assert.equal(ANTES.C3_EDICAO_NAO_VISTA, false);
  });

  console.log("\n══ CENSO ═══════════════════════════════════════════════════════");
  const linha = (n, h) => `  ${n.padEnd(6)} ` + ["C1", "C2", "C3", "C4", "C5"].map(k => `${k}=${h[k].materias}`).join(" ") +
    `  total de pedidos a matérias=${h.TOTAL_MATERIAS}`;
  console.log(linha("ANTES", ANTES));
  console.log(linha("T1", T1));
  t("o prazo poupa pedidos: 15 -> 6 nesta história", () => {
    assert.equal(ANTES.TOTAL_MATERIAS, 15); assert.equal(T1.TOTAL_MATERIAS, 6);
  });
} finally {
  CONTRACTS[RIUNITE].ACQUISITION = ORIG.r.ACQUISITION;
  CONTRACTS[RIUNITE].CANONICAL_ENTRY_URL = ORIG.r.CANONICAL_ENTRY_URL;
  CONTRACTS[RIUNITE].RECOLLECTION = ORIG.r.RECOLLECTION;
  CONTRACTS[BOLETIM].CANONICAL_ENTRY_URL = ORIG.b.CANONICAL_ENTRY_URL;
  servidor.close();
  rmSync(RAIZ, { recursive: true, force: true });
}
console.log(`\n  ${passou} passaram, ${falhou} falharam`);
process.exit(falhou ? 1 : 0);
