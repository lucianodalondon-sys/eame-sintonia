// A PROVA PELO TRANSPORTE DE VERDADE — O COLETOR, O CURL, E UM SERVIDOR HTTP LOCAL.
//
//     node provas/recollection_http_local.mjs
//
// ⚠️ PORQUE ESTA PROVA EXISTE AO LADO DE `paridade_duas_rodadas.mjs`.
// Aquela injecta os bytes por `forcarBuf`: prova a regra dentro do coletor, mas
// com o transporte desligado. Esta liga o transporte — `baixar()` com `curl`,
// o mesmo da producao — contra um servidor HTTP em 127.0.0.1, numa raiz
// descartavel. A contagem de pedidos e a do SERVIDOR: uma rodada que nao bate
// a porta nao chega ao servidor.
//
// ZERO REDE EXTERNA, E PROVADO. Sem `forcarBuf` o coletor mede o egresso em
// ipinfo.io. O proxy de saida aponta para uma porta fechada em 127.0.0.1 e so
// 127.0.0.1/localhost ficam fora dele: o pedido externo falha antes de sair da
// maquina, e o resumo tem de dizer egresso NAO SEI.
//
// O que se mede, rodada a rodada (MUTABLE declarado a partir da R5, como na paridade):
//   R1  documento novo                     -> 1 pedido, NEW
//   R2  o mesmo endereco                   -> 0 pedidos (incrementalidade)
//   R3  endereco novo, servidor 503        -> falha contada; o endereco NAO fica conhecido
//   R4  o servidor volta                   -> o endereco e colhido (recollection: nada perdido)
//   R5  revalidacao, so ruido de HTML      -> SEEN_AGAIN, nao CHANGED (FALSE_DOCUMENT_CHANGED = 0)
//   R6  a materia muda                     -> CHANGED, versao nova; a ANTIGA continua em disco
import { createServer } from "node:http";
import { mkdtempSync, rmSync, readFileSync, existsSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { createHash } from "node:crypto";
import { spawnSync } from "node:child_process";
import assert from "node:assert/strict";

const RAIZ = mkdtempSync(join(tmpdir(), "recollection-http-"));
process.env.ITALY_OPS_ROOT = RAIZ;
for (const k of ["http_proxy", "https_proxy", "HTTP_PROXY", "HTTPS_PROXY", "ALL_PROXY", "all_proxy"])
  process.env[k] = "http://127.0.0.1:9";           // porta fechada: nada sai
process.env.NO_PROXY = process.env.no_proxy = "127.0.0.1,localhost";

// ── O SERVIDOR ──────────────────────────────────────────────────────────────
let estado = {}, modo = 200;
const PEDIDOS = [], ROBOTS_PEDIDOS = [];
const pagina = (v = {}) => `<!DOCTYPE html><html><head>
<meta property="article:modified_time" content="${v.hora ?? "2026-09-22T02:01:41+00:00"}" />
</head><body>
<div class="views">${v.visitas ?? 134}</div>
<p>Bollettino del periodo ${v.periodo ?? "dal 01-09-2026 al 07-09-2026"}</p>
<p id="materia">${v.corpo ?? "Infestazione attiva: bassa"}</p>
<form><input name="_token" type="hidden" value="${v.token ?? "A".repeat(40)}"></form>
</body></html>`;
const servidor = createServer((req, res) => {
  // ⚠️ A5 · O COLETOR LE O ROBOTS.TXT ANTES DE PEDIR (a cortesia vive em
  // `baixar()`). Este servidor nao publica robots — 404, «sem ficheiro = sem
  // proibicao» — e conta essas idas A PARTE: as contas desta prova sao de
  // documentos, e continuam exactamente as mesmas.
  if (req.url === "/robots.txt") { ROBOTS_PEDIDOS.push(Date.now()); res.writeHead(404); res.end("non trovato"); return; }
  PEDIDOS.push(req.url);
  if (modo !== 200) { res.writeHead(modo); res.end("indisponivel"); return; }
  res.writeHead(200, { "Content-Type": "text/html; charset=ISO-8859-1" });
  res.end(Buffer.from(pagina(estado), "latin1"));
});
await new Promise(r => servidor.listen(0, "127.0.0.1", r));
const BASE = `http://127.0.0.1:${servidor.address().port}`;

const { executarRodada } = await import("../coleta/italy_pilot_collect.mjs");
const { CONTRACTS } = await import("../regras/italy_contracts.mjs");
const FONTE = "IT-T3-005";
const ORIGINAL = { RECOLLECTION: CONTRACTS[FONTE].RECOLLECTION, URL: CONTRACTS[FONTE].CANONICAL_ENTRY_URL };
CONTRACTS[FONTE].RECOLLECTION = undefined;
CONTRACTS[FONTE].CANONICAL_ENTRY_URL = `${BASE}/monitoraggio`;

const livro = () => {
  const f = join(RAIZ, "data/collection-ledger/italy/observations.ndjson");
  return existsSync(f) ? readFileSync(f, "utf8").split("\n").filter(Boolean).map(JSON.parse) : [];
};
async function rodada(nome) {
  const antes = PEDIDOS.length, robotsAntes = ROBOTS_PEDIDOS.length;
  const { resumo } = await executarRodada({ runId: `PROVA_HTTP_${nome}_${Date.now()}`, apenas: [FONTE],
                                            pularParse: true, nota: `prova http local ${nome}` });
  return { c: resumo.contadores, resumo, pedidos: PEDIDOS.length - antes,
           robots: ROBOTS_PEDIDOS.length - robotsAntes };
}

let passou = 0, falhou = 0;
const t = (nome, fn) => {
  try { fn(); passou++; console.log(`  ok    ${nome}`); }
  catch (e) { falhou++; console.log(`  FALHA ${nome}\n        ${e.message}`); }
};
const censo = [];
const anota = (nome, r) => censo.push(`  ${nome.padEnd(4)} pedidos_ao_servidor=${r.pedidos}  DETAIL_REQUESTS=${r.c.DETAIL_REQUESTS}` +
  `  NEW=${r.c.NEW_DOCUMENTS} SKIPPED_KNOWN=${r.c.SKIPPED_KNOWN} CHANGED=${r.c.CHANGED_IN_PLACE} SEEN_AGAIN=${r.c.SEEN_AGAIN}` +
  `  FAILED=${r.c.FAILED}  UNNECESSARY_REFETCHES=${r.c.UNNECESSARY_REFETCHES}`);

try {
  console.log(`\n(servidor ${BASE} · raiz ${RAIZ})`);
  console.log("\n══ R1 · documento novo, pelo curl ════════════════════════════════");
  const r1 = await rodada("R1"); anota("R1", r1);
  t("R1 chega ao servidor uma vez e cria o documento", () => {
    assert.equal(r1.pedidos, 1); assert.equal(r1.c.DETAIL_NEW, 1); assert.equal(r1.c.RAW_OBJECTS_CREATED, 1);
  });
  t("zero rede externa: o egresso ficou NAO SEI (o pedido ao ipinfo nao saiu)", () => {
    assert.equal(r1.resumo.EGRESS_IP, "NAO SEI", `egresso medido: ${r1.resumo.EGRESS_IP}`);
  });
  t("zero rede externa: o curl, com este ambiente, nao alcanca a internet", () => {
    const x = spawnSync("curl", ["-s", "-o", "NUL", "-w", "%{http_code}", "--max-time", "10", "https://ipinfo.io/json"], { encoding: "utf8" });
    assert.equal(x.stdout.trim(), "000", `a internet respondeu: ${x.stdout}`);
  });

  console.log("\n══ R2 · o mesmo endereco — incrementalidade ════════════════════");
  estado = { visitas: 135, hora: "2026-09-22T02:06:03+00:00", token: "B".repeat(40) };
  const r2 = await rodada("R2"); anota("R2", r2);
  t("R2 NAO chega ao servidor", () => { assert.equal(r2.pedidos, 0); assert.equal(r2.c.SKIPPED_KNOWN, 1); });
  t("A5: R1 leu o robots UMA vez; R2, que nao pediu nada, nem o robots leu", () => {
    assert.equal(r1.robots, 1); assert.equal(r2.robots, 0); assert.equal(r2.c.ROBOTS_REQUESTS, 0);
  });
  t("R2: UNNECESSARY_REFETCHES = 0 e nenhum CHANGED", () => {
    assert.equal(r2.c.UNNECESSARY_REFETCHES, 0); assert.equal(r2.c.CHANGED_IN_PLACE, 0);
  });

  console.log("\n══ R3 · endereco novo, o servidor responde 503 ═════════════════");
  // Um boletim NOVO (outro periodo) num endereco novo — e o servidor esta em baixo.
  CONTRACTS[FONTE].CANONICAL_ENTRY_URL = `${BASE}/monitoraggio-2`;
  estado = { periodo: "dal 08-09-2026 al 14-09-2026" };
  modo = 503;
  const linhasAntes = livro().length;
  const r3 = await rodada("R3"); anota("R3", r3);
  t("R3 bateu a porta e a falha foi contada", () => {
    assert.ok(r3.pedidos >= 1, "o transporte tem de ter ido ao servidor");
    // DETAIL_NEW conta a DECISAO de ir buscar um endereco novo, antes do transporte.
    assert.equal(r3.c.DETAIL_NEW, 1); assert.equal(r3.c.NEW_DOCUMENTS, 0); assert.equal(r3.c.RAW_OBJECTS_CREATED, 0);
    assert.equal(r3.c.FAILED, 1, `contadores: ${JSON.stringify(r3.c)}`);
    const u = livro().at(-1);
    assert.equal(u.OBSERVATION_RESULT, "TRANSPORT_OR_EMPTY"); assert.equal(u.DOCUMENT_ID, null);
  });
  t("R3 nao escreveu documento nenhum para o endereco novo", () => {
    const novas = livro().slice(linhasAntes).filter(l => String(l.SOURCE_URL || "").endsWith("/monitoraggio-2"));
    assert.ok(!novas.some(l => ["BASELINE_DOCUMENT", "NEW_DOCUMENT", "SEEN_AGAIN", "DOCUMENT_CHANGED_IN_PLACE"]
      .includes(l.OBSERVATION_RESULT)), JSON.stringify(novas.map(l => l.OBSERVATION_RESULT)));
  });

  console.log("\n══ R4 · o servidor volta — o endereco e retomado ═══════════════");
  modo = 200;
  const r4 = await rodada("R4"); anota("R4", r4);
  t("R4 vai buscar o endereco que falhou (nao ficou marcado como conhecido)", () => {
    assert.equal(r4.pedidos, 1); assert.equal(r4.c.SKIPPED_KNOWN, 0);
    assert.equal(r4.c.NEW_DOCUMENTS, 1); assert.equal(r4.c.RAW_OBJECTS_CREATED, 1);
  });
  t("R4 escreve o documento no livro — nada perdido", () => {
    const u = livro().at(-1);
    assert.ok(String(u.SOURCE_URL).endsWith("/monitoraggio-2"), u.SOURCE_URL);
    assert.ok(["NEW_DOCUMENT", "BASELINE_DOCUMENT"].includes(u.OBSERVATION_RESULT), u.OBSERVATION_RESULT);
    assert.ok(existsSync(u.RAW_PATH));
  });

  console.log("\n══ R5 · revalidacao declarada, so ruido de HTML ════════════════");
  CONTRACTS[FONTE].RECOLLECTION = { DETAIL_CONTENT: "MUTABLE" };
  estado = { ...estado, visitas: 999, hora: "2026-09-23T00:00:00+00:00", token: "C".repeat(40) };
  const r5 = await rodada("R5"); anota("R5", r5);
  t("R5 vai, com razao, e so ruido -> SEEN_AGAIN (FALSE_DOCUMENT_CHANGED = 0)", () => {
    assert.equal(r5.pedidos, 1); assert.equal(r5.c.REVALIDATED, 1);
    assert.equal(r5.c.CHANGED_IN_PLACE, 0); assert.equal(r5.c.SEEN_AGAIN, 1);
    assert.equal(r5.c.RAW_OBJECTS_CREATED, 0, "ruido nao cria versao");
    assert.equal(r5.c.UNNECESSARY_REFETCHES, 0);
  });

  console.log("\n══ R6 · a materia muda — versao nova, a antiga fica ════════════");
  const antiga = livro().filter(l => l.RAW_PATH).at(-1);
  estado = { ...estado, visitas: 1000, token: "D".repeat(40), corpo: "Infestazione attiva: ALTA" };
  const r6 = await rodada("R6"); anota("R6", r6);
  t("R6: DOCUMENT_CHANGED_IN_PLACE e versao nova", () => {
    assert.equal(r6.pedidos, 1); assert.equal(r6.c.CHANGED_IN_PLACE, 1); assert.equal(r6.c.RAW_OBJECTS_CREATED, 1);
  });
  t("R6: a versao ANTIGA continua em disco, com o sha256 do livro", () => {
    const nova = livro().at(-1);
    assert.equal(nova.OBSERVATION_RESULT, "DOCUMENT_CHANGED_IN_PLACE");
    assert.notEqual(nova.RAW_PATH, antiga.RAW_PATH, "a versao nova nao pode sobrescrever a antiga");
    assert.ok(existsSync(antiga.RAW_PATH), `a versao antiga desapareceu: ${antiga.RAW_PATH}`);
    assert.equal(createHash("sha256").update(readFileSync(antiga.RAW_PATH)).digest("hex"), antiga.RAW_SHA256);
    assert.equal(createHash("sha256").update(readFileSync(nova.RAW_PATH)).digest("hex"), nova.RAW_SHA256);
  });
  t("R6: proveniencia — a linha nova traz os dois hashes normalizados e MATERIAL_DIFF", () => {
    const nova = livro().at(-1);
    assert.equal(nova.MATERIAL_DIFF, true);
    assert.ok(nova.OLD_NORMALIZED_HASH && nova.NEW_NORMALIZED_HASH && nova.OLD_NORMALIZED_HASH !== nova.NEW_NORMALIZED_HASH);
  });

  console.log("\n══ CENSO ═══════════════════════════════════════════════════════");
  for (const l of censo) console.log(l);
  t("UNNECESSARY_REFETCHES = 0 em TODAS as rodadas", () => {
    assert.ok(censo.every(l => l.endsWith("UNNECESSARY_REFETCHES=0")));
  });
  t("so houve pedidos a 127.0.0.1 (o servidor viu tudo o que o coletor pediu)", () => {
    assert.ok(PEDIDOS.every(p => p.startsWith("/monitoraggio")), JSON.stringify(PEDIDOS));
  });
} finally {
  CONTRACTS[FONTE].RECOLLECTION = ORIGINAL.RECOLLECTION;
  CONTRACTS[FONTE].CANONICAL_ENTRY_URL = ORIGINAL.URL;
  servidor.close();
  rmSync(RAIZ, { recursive: true, force: true });
}
console.log(`\n  ${passou} passaram, ${falhou} falharam`);
process.exit(falhou ? 1 : 0);
