// FEED_DISCOVERY E O ROBOTS (D91, 26/09 22:32) — o coletor de verdade contra um servidor local.
//
//     node provas/feed_robots_local.mjs
//
// A D88 nao dispensa o robots.txt: o feed e cada item sao paginas comuns. O robots do servidor proibe um item
// (/news/peronospora…) e um feed inteiro (/feed-chiuso/). Quem conta os pedidos e o SERVIDOR.
//
//   R1  o item proibido NUNCA chega ao servidor; os permitidos sim
//   R2  o feed proibido NUNCA chega ao servidor, e a corrida nao colhe nada dele
//
// O transporte real (`executarRodada` → `baixar()` com o curl) le o feed de uma fonte e colhe os itens.
// Quem conta os pedidos e o SERVIDOR. Zero rede externa: proxy de saida para uma porta fechada; o nome
// resolve para 127.0.0.1 por um `_curlrc` so desta prova (o mecanismo de `teto_dominio_local.mjs`).
//
import { createServer } from "node:http";
import { mkdtempSync, rmSync, readFileSync, existsSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import assert from "node:assert/strict";

const RAIZ = mkdtempSync(join(tmpdir(), "feed-robots-"));
process.env.ITALY_OPS_ROOT = RAIZ;
for (const k of ["http_proxy", "https_proxy", "HTTP_PROXY", "HTTPS_PROXY", "ALL_PROXY", "all_proxy"])
  process.env[k] = "http://127.0.0.1:9";
const HOST = "feedrobots.test";
process.env.NO_PROXY = process.env.no_proxy = ["127.0.0.1", "localhost", HOST].join(",");
for (const k of ["SINTONIA_TETO_POR_HOST", "SINTONIA_TETO_ONDA"]) delete process.env[k];
process.env.SINTONIA_PAUSA_POR_HOST_S = "0";

const enchimento = "<p>" + "Testo dell'articolo sulla mosca dell'olivo. ".repeat(60) + "</p>";
const PEDIDOS = [];
let PORTA = 0;
const rss = () => `<?xml version="1.0" encoding="UTF-8"?><rss version="2.0"><channel>
<item><title>Mosca dell'olivo, catture in aumento</title><link>http://${HOST}:${PORTA}/news/mosca-olivo-catture-aumento/</link><pubDate>Thu, 24 Sep 2026 07:30:00 +0000</pubDate></item>
<item><title>Peronospora, allerta</title><link>http://${HOST}:${PORTA}/news/peronospora-allerta-vigneto/</link><pubDate>Wed, 23 Sep 2026 09:00:00 +0000</pubDate></item>
<item><title>Senza data</title><link>http://${HOST}:${PORTA}/news/articolo-senza-data-nel-feed/</link></item>
<item><title>Quarto</title><link>http://${HOST}:${PORTA}/news/quarto-articolo-del-feed/</link><pubDate>Tue, 22 Sep 2026 09:00:00 +0000</pubDate></item>
</channel></rss>`;
const servidor = createServer((req, res) => {
  PEDIDOS.push(req.url);
  if (req.url === "/robots.txt") { res.setHeader("Content-Type", "text/plain"); res.end("User-agent: *\nDisallow: /news/peronospora\nDisallow: /feed-chiuso/\n"); return; }
  if (req.url === "/feed/" || req.url === "/feed-chiuso/") { res.setHeader("Content-Type", "application/rss+xml; charset=utf-8"); res.end(rss()); return; }
  if (/^\/news\/[a-z0-9-]+\/$/.test(req.url)) {
    res.setHeader("Content-Type", "text/html; charset=utf-8");
    res.end(`<!DOCTYPE html><html><head><title>${req.url}</title></head><body><article><h1>${req.url}</h1>${enchimento}</article></body></html>`);
    return;
  }
  res.writeHead(404); res.end("non trovato");
});
await new Promise((r) => servidor.listen(0, "127.0.0.1", r));
PORTA = servidor.address().port;
const CURL_HOME = mkdtempSync(join(tmpdir(), "feed-robots-curl-"));
for (const n of ["_curlrc", ".curlrc"]) writeFileSync(join(CURL_HOME, n), `resolve = "${HOST}:${PORTA}:127.0.0.1"\n`);
process.env.CURL_HOME = CURL_HOME;

const M = await import("../coleta/italy_pilot_collect.mjs");
const { CONTRACTS } = await import("../regras/italy_contracts.mjs");
const FONTE = "IT-T10-018";
const ORIGINAL = { ...CONTRACTS[FONTE] };
let passou = 0, falhou = 0;
const t = (nome, fn) => {
  try { fn(); passou++; console.log(`  ok    ${nome}`); }
  catch (e) { falhou++; console.log(`  FALHA ${nome}\n        ${e.message}`); }
};
try {
  CONTRACTS[FONTE].ACQUISITION = { STRATEGY: "FEED_DISCOVERY", FEED_URL: `http://${HOST}:${PORTA}/feed/` };
  CONTRACTS[FONTE].IDENTITY = { STRATEGY: "CONTENT_CAPTURE", DOCUMENT_ID: "IT-T10-018:URL:{doc.1}",
    CAPTURES: { doc: { FROM: "URL", PATTERN: `${HOST.replace(".", "\\.")}:\\d+/(news/[a-z0-9-]+)` } } };
  CONTRACTS[FONTE].CANONICAL_ENTRY_URL = `http://${HOST}:${PORTA}/feed/`;
  CONTRACTS[FONTE].RECOLLECTION = undefined;
  const RUN1 = `PROVA_FEED_ROBOTS_1_${Date.now()}`;
  await M.executarRodada({ runId: RUN1, apenas: [FONTE], pularParse: true, nota: "prova feed robots 1" });
  console.log(`  pedidos (1): ${JSON.stringify(PEDIDOS)}`);
  t("R1: o item proibido pelo robots nunca chega ao servidor; o feed e os permitidos sim", () => {
    assert.equal(PEDIDOS[0], "/robots.txt");
    assert.ok(PEDIDOS.includes("/feed/"), JSON.stringify(PEDIDOS));
    assert.ok(PEDIDOS.includes("/news/mosca-olivo-catture-aumento/"), JSON.stringify(PEDIDOS));
    assert.ok(!PEDIDOS.some((p) => p.startsWith("/news/peronospora")), JSON.stringify(PEDIDOS));
  });
  PEDIDOS.length = 0;
  CONTRACTS[FONTE].ACQUISITION = { STRATEGY: "FEED_DISCOVERY", FEED_URL: `http://${HOST}:${PORTA}/feed-chiuso/` };
  CONTRACTS[FONTE].CANONICAL_ENTRY_URL = `http://${HOST}:${PORTA}/feed-chiuso/`;
  const RUN2 = `PROVA_FEED_ROBOTS_2_${Date.now()}`;
  await M.executarRodada({ runId: RUN2, apenas: [FONTE], pularParse: true, nota: "prova feed robots 2" });
  console.log(`  pedidos (2): ${JSON.stringify(PEDIDOS)}`);
  const obs2 = readFileSync(join(RAIZ, "data/collection-ledger/italy/observations.ndjson"), "utf8")
    .split("\n").filter(Boolean).map((l) => JSON.parse(l)).filter((o) => o.RUN_ID === RUN2 && o.SOURCE_URL);
  t("R2: o feed proibido pelo robots nunca chega ao servidor e nada se colhe dele", () => {
    assert.ok(!PEDIDOS.includes("/feed-chiuso/"), JSON.stringify(PEDIDOS));
    assert.ok(!PEDIDOS.some((p) => p.startsWith("/news/")), JSON.stringify(PEDIDOS));
    assert.equal(obs2.length, 0);
  });
} finally {
  Object.assign(CONTRACTS[FONTE], ORIGINAL);
  servidor.close();
  rmSync(RAIZ, { recursive: true, force: true });
  rmSync(CURL_HOME, { recursive: true, force: true });
}
console.log(`\nFEED_ROBOTS_LOCAL · passou=${passou} FALHAS=${falhou}`);
process.exit(falhou ? 1 : 0);
