// A CORRIDA QUE REBENTA A MEIO TAMBEM ESCREVE A SUA LINHA — PROVADO PELO CURL, CONTRA UM SERVIDOR LOCAL.
//
//     node provas/corrida_abortada_local.mjs
//
// FECHAR-ONDA2 (25/09/2026). Na 2.a onda web, IT-T2-050 (ARPA Campania) rebentou em
// `guardarRaw` — mkdir ENOENT, porque o DOCUMENT_ID pelo endereco levava `?redirect=%2F`
// e o Windows recusa `?` em nome de pasta — DEPOIS de 3 pedidos a arpacampania.it. A
// linha do `runs.ndjson` so se escrevia no fim da corrida: nao houve linha, e a
// PROVA-TETO deu NAO_SEI (e bem). Esta prova liga o transporte de verdade contra um
// servidor em 127.0.0.1 (o mecanismo de `teto_dominio_local.mjs`); quem conta e o SERVIDOR.
//
//   B1  rebentar a meio (pasta da fonte ocupada por um FICHEIRO; vale em qualquer SO)
//       -> a corrida rejeita; a linha existe, com ABORTED e PEDIDOS_POR_HOST = o que o servidor viu
//   B2  o caso real: `?redirect=%2F` no endereco (so no Windows, onde o mkdir o recusa)
//       -> ENOENT; linha escrita; a pasta da fonte fica vazia, como no vivo
//   B3  a PROVA-TETO fecha com a linha (PASS) e continua NAO_SEI sem ela
//   B4  corrida que acaba bem nao leva ABORTED
import { createServer } from "node:http";
import { mkdtempSync, rmSync, readFileSync, writeFileSync, mkdirSync, existsSync, readdirSync } from "node:fs";
import { execFileSync } from "node:child_process";
import { randomBytes } from "node:crypto";
import { tmpdir } from "node:os";
import { join } from "node:path";
import assert from "node:assert/strict";

const RAIZ = mkdtempSync(join(tmpdir(), "corrida-abortada-"));
process.env.ITALY_OPS_ROOT = RAIZ;
for (const k of ["http_proxy", "https_proxy", "HTTP_PROXY", "HTTPS_PROXY", "ALL_PROXY", "all_proxy"])
  process.env[k] = "http://127.0.0.1:9";
const NOMES = ["arpac.test", "www.arpac.test"];
process.env.NO_PROXY = process.env.no_proxy = ["127.0.0.1", "localhost", ...NOMES].join(",");
for (const k of ["SINTONIA_PAUSA_POR_HOST_S", "SINTONIA_TETO_POR_HOST", "SINTONIA_TETO_ONDA"]) delete process.env[k];
process.env.SINTONIA_PAUSA_POR_HOST_S = "0";

const enchimento = "<p>" + "Testo dell'articolo. ".repeat(80) + "</p>";
let LINKS = [];
const PEDIDOS = [];
const servidor = createServer((req, res) => {
  const host = String(req.headers.host || "").split(":")[0];
  PEDIDOS.push({ host, p: req.url });
  if (req.url === "/robots.txt") { res.writeHead(404); res.end("non trovato"); return; }
  res.setHeader("Content-Type", "text/html; charset=utf-8");
  if (req.url === "/") { res.end(`<!DOCTYPE html><html><body>${LINKS.map(l => `<a href="${l}">${l}</a>`).join("\n")}${enchimento}</body></html>`); return; }
  if (req.url.startsWith("/-/")) { res.end(`<!DOCTYPE html><html><head><title>m</title></head><body><h1>Materia</h1>${enchimento}</body></html>`); return; }
  res.writeHead(404); res.end("non trovato");
});
await new Promise(r => servidor.listen(0, "127.0.0.1", r));
const PORTA = servidor.address().port;
const CURL_HOME = mkdtempSync(join(tmpdir(), "corrida-abortada-curl-"));
const rc = NOMES.map(h => `resolve = "${h}:${PORTA}:127.0.0.1"`).join("\n") + "\n";
for (const n of ["_curlrc", ".curlrc"]) writeFileSync(join(CURL_HOME, n), rc);
process.env.CURL_HOME = CURL_HOME;

const M = await import("../coleta/italy_pilot_collect.mjs");
const { CONTRACTS } = await import("../regras/italy_contracts.mjs");
// A IT-T2-050 so esta nos contratos onde a ponte a onboardou (o vivo); fora dele, uma irma
// da mesma forma: HTML_LINK_DISCOVERY com a identidade POR OMISSAO, pelo endereco inteiro.
const FONTE = CONTRACTS["IT-T2-050"] ? "IT-T2-050" : "IT-T2-051";
assert.match(String(CONTRACTS[FONTE].IDENTITY?.DOCUMENT_ID), /:URL:\{doc\.1\}$/, "a fonte da prova tem de usar a identidade pelo endereco");
const ORIGINAL = { ACQUISITION: CONTRACTS[FONTE].ACQUISITION, RECOLLECTION: CONTRACTS[FONTE].RECOLLECTION,
                   CANONICAL_ENTRY_URL: CONTRACTS[FONTE].CANONICAL_ENTRY_URL };
const STORE_DA_FONTE = join(RAIZ, "data", "collection-store", "italy", FONTE);
const LEDGER = join(RAIZ, "data", "collection-ledger", "italy", "runs.ndjson");
let n = 0;

async function corrida(slug) {
  n++;
  const host = "www.arpac.test";
  LINKS = [`http://${host}:${PORTA}/-/${slug}`];
  CONTRACTS[FONTE].ACQUISITION = { ...ORIGINAL.ACQUISITION, INDEX_URL: `http://${host}:${PORTA}/`, MAX_TARGETS: 1,
    LINK_PATTERN: String.raw`^http://(www\.)?arpac\.test:\d+/\-/[a-z0-9]+(?:-[a-z0-9]+)+(?:\?redirect=[^&]+)?$` };
  CONTRACTS[FONTE].CANONICAL_ENTRY_URL = `http://${host}:${PORTA}/`;
  CONTRACTS[FONTE].RECOLLECTION = undefined;
  // a forma de um RUN_ID de verdade: a PROVA-TETO so reconhece essa
  const runId = `IT-T2-2026-09-25-00000${n}-${randomBytes(8).toString("hex")}`;
  const antes = PEDIDOS.length;
  let erro = null, resumo = null;
  try { ({ resumo } = await M.executarRodada({ runId, apenas: [FONTE], pularParse: true, nota: "prova corrida abortada" })); }
  catch (e) { erro = e; }
  const linhas = existsSync(LEDGER) ? readFileSync(LEDGER, "utf8").trim().split("\n").map(l => JSON.parse(l)) : [];
  const linha = linhas.filter(l => l.RUN_ID === runId);
  const noServidor = {};
  for (const x of PEDIDOS.slice(antes)) { const s = M.siteDe(x.host); noServidor[s] = (noServidor[s] || 0) + 1; }
  return { runId, erro, resumo, linha, noServidor };
}

let passou = 0, falhou = 0;
const t = (nome, fn) => {
  try { fn(); passou++; console.log(`  ok    ${nome}`); }
  catch (e) { falhou++; console.log(`  FALHA ${nome}\n        ${e.message}`); }
};
const PY = process.env.SINTONIA_PY || (process.platform === "win32" ? "py" : "python3");
function prova(runIds, livro) {
  const onda = join(RAIZ, `onda-${Date.now()}.txt`);
  writeFileSync(onda, runIds.join("\n") + "\n");
  try { execFileSync(PY, ["provas/prova_teto_dominio.py", "--livro", livro, "--onda", onda], { encoding: "utf8", stdio: "pipe" }); return 0; }
  catch (e) { return e.status; }
}

try {
  console.log(`\n(servidor 127.0.0.1:${PORTA} · raiz ${RAIZ})`);

  console.log("\n══ B1 · rebentar a meio: a pasta da fonte e um FICHEIRO ══");
  mkdirSync(join(RAIZ, "data", "collection-store", "italy"), { recursive: true });
  writeFileSync(STORE_DA_FONTE, "isto ocupa o lugar da pasta");
  const b1 = await corrida("materia-uno");
  rmSync(STORE_DA_FONTE, { force: true });
  console.log(`  erro: ${b1.erro && b1.erro.code} · servidor ${JSON.stringify(b1.noServidor)} · linhas ${b1.linha.length}`);
  t("B1a: a corrida rejeita (o codigo de saida continua a dizer que falhou)", () => assert.ok(b1.erro, "nao rebentou"));
  t("B1b: a linha da corrida existe, uma so, e diz ABORTED na fonte em curso", () => {
    assert.equal(b1.linha.length, 1);
    assert.equal(b1.linha[0].ABORTED?.SOURCE_ID, FONTE, JSON.stringify(b1.linha[0].ABORTED));
    assert.ok(b1.linha[0].ABORTED.ERRO.length > 0);
    assert.ok(b1.linha[0].contadores.FAILED >= 1, JSON.stringify(b1.linha[0].contadores));
  });
  t("B1c: PEDIDOS_POR_HOST da linha = o que o SERVIDOR contou (robots + indice + materia)", () => {
    assert.deepEqual(b1.linha[0].CORTESIA.PEDIDOS_POR_HOST, b1.noServidor);
    assert.ok((b1.noServidor["arpac.test"] || 0) >= 3, JSON.stringify(b1.noServidor));
  });

  console.log("\n══ B2 · o caso real: `?redirect=%2F` no endereco ══");
  if (process.platform === "win32") {
    const b2 = await corrida("materia-due?redirect=%2F");
    console.log(`  erro: ${b2.erro && b2.erro.code} · servidor ${JSON.stringify(b2.noServidor)} · linhas ${b2.linha.length}`);
    t("B2: ENOENT como no vivo; linha escrita com os pedidos do servidor; pasta da fonte vazia", () => {
      assert.equal(b2.erro?.code, "ENOENT", String(b2.erro));
      assert.equal(b2.linha.length, 1);
      assert.deepEqual(b2.linha[0].CORTESIA.PEDIDOS_POR_HOST, b2.noServidor);
      assert.equal(readdirSync(STORE_DA_FONTE).length, 0);
    });
  } else {
    console.log("  (salta: fora do Windows o `?` e nome de pasta valido)");
  }

  console.log("\n══ B3 · a PROVA-TETO ══");
  const semLinha = join(RAIZ, "runs-sem-a-linha.ndjson");
  writeFileSync(semLinha, readFileSync(LEDGER, "utf8").split("\n").filter(l => !l.includes(b1.runId)).join("\n"));
  t("B3a: com a linha da corrida abortada, a prova fecha (PASS, codigo 0)", () => assert.equal(prova([b1.runId], LEDGER), 0));
  t("B3b: sem a linha, continua NAO_SEI (codigo 2) — nao se conta zero", () => assert.equal(prova([b1.runId], semLinha), 2));

  console.log("\n══ B4 · corrida que acaba bem ══");
  const b4 = await corrida("materia-quattro");
  t("B4: nao rebenta e a linha nao leva ABORTED", () => {
    assert.equal(b4.erro, null, String(b4.erro));
    assert.equal(b4.linha.length, 1);
    assert.ok(!("ABORTED" in b4.linha[0]), JSON.stringify(b4.linha[0].ABORTED));
  });
} finally {
  CONTRACTS[FONTE].ACQUISITION = ORIGINAL.ACQUISITION;
  CONTRACTS[FONTE].RECOLLECTION = ORIGINAL.RECOLLECTION;
  CONTRACTS[FONTE].CANONICAL_ENTRY_URL = ORIGINAL.CANONICAL_ENTRY_URL;
  servidor.close();
  rmSync(RAIZ, { recursive: true, force: true });
  rmSync(CURL_HOME, { recursive: true, force: true });
}
console.log(`\nCORRIDA_ABORTADA_LOCAL · passou=${passou} FALHAS=${falhou}`);
process.exit(falhou ? 1 : 0);
