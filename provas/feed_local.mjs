// FEED_DISCOVERY PELO COLETOR DE VERDADE — contra um servidor local (SCRAP-EVOLUCAO-V1, 26/09).
//
//     node provas/feed_local.mjs
//
// O transporte real (`executarRodada` → `baixar()` com o curl) le o feed de uma fonte e colhe os itens.
// Quem conta os pedidos e o SERVIDOR. Zero rede externa: proxy de saida para uma porta fechada; o nome
// resolve para 127.0.0.1 por um `_curlrc` so desta prova (o mecanismo de `teto_dominio_local.mjs`).
//
//   F1  robots + feed + 3 itens = 5 pedidos (o teto D38), e nenhum pedido a paginacao/listas
//   F2  cada observacao leva PUBLISHED_AT do feed com a base «nivel indice; nunca FACT_TIME»
//   F3  FACT_TIME continua UNKNOWN (a data do feed nunca e a data do facto)
//   F4  o item sem data no feed sai com PUBLISHED_AT = NAO SEI e o porque
import { createServer } from "node:http";
import { mkdtempSync, rmSync, readFileSync, existsSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import assert from "node:assert/strict";

const RAIZ = mkdtempSync(join(tmpdir(), "feed-local-"));
process.env.ITALY_OPS_ROOT = RAIZ;
for (const k of ["http_proxy", "https_proxy", "HTTP_PROXY", "HTTPS_PROXY", "ALL_PROXY", "all_proxy"])
  process.env[k] = "http://127.0.0.1:9";
const HOST = "feed.test";
process.env.NO_PROXY = process.env.no_proxy = ["127.0.0.1", "localhost", HOST].join(",");
for (const k of ["SINTONIA_TETO_POR_HOST", "SINTONIA_TETO_ONDA"]) delete process.env[k];
// D124 (dono, 27/09) — AJUSTE DECLARADO: o 5 fixo deixou de ser a omissao (o teto e o orcamento vigente
// da politica adaptativa). Esta prova mede a MECANICA do teto por dominio com o teto MANUAL declarado de 5.
process.env.SINTONIA_TETO_POR_HOST = "5";
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
  if (req.url === "/robots.txt") { res.writeHead(404); res.end("non trovato"); return; }
  if (req.url === "/feed/") { res.setHeader("Content-Type", "application/rss+xml; charset=utf-8"); res.end(rss()); return; }
  if (/^\/news\/[a-z0-9-]+\/$/.test(req.url)) {
    res.setHeader("Content-Type", "text/html; charset=utf-8");
    res.end(`<!DOCTYPE html><html><head><title>${req.url}</title></head><body><article><h1>${req.url}</h1>${enchimento}</article></body></html>`);
    return;
  }
  res.writeHead(404); res.end("non trovato");
});
await new Promise((r) => servidor.listen(0, "127.0.0.1", r));
PORTA = servidor.address().port;
const CURL_HOME = mkdtempSync(join(tmpdir(), "feed-local-curl-"));
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
  const RUN = `PROVA_FEED_LOCAL_${Date.now()}`;
  const { resumo } = await M.executarRodada({ runId: RUN, apenas: [FONTE], pularParse: true, nota: "prova feed local" });
  const obs = readFileSync(join(RAIZ, "data/collection-ledger/italy/observations.ndjson"), "utf8")
    .split("\n").filter(Boolean).map((l) => JSON.parse(l)).filter((o) => o.RUN_ID === RUN && o.SOURCE_URL);
  console.log(`  pedidos ao servidor: ${JSON.stringify(PEDIDOS)}`);
  t("F1: robots + feed + 3 itens = 5 pedidos (teto D38); nada de listas", () => {
    assert.equal(PEDIDOS.length, 5, JSON.stringify(PEDIDOS));
    assert.deepEqual(PEDIDOS.slice(0, 2), ["/robots.txt", "/feed/"]);
    assert.equal(resumo.contadores.FAILED, 0, JSON.stringify(resumo.contadores));
  });
  const porUrl = Object.fromEntries(obs.map((o) => [o.SOURCE_URL.replace(/^http:\/\/[^/]+/, ""), o]));
  t("F2: PUBLISHED_AT do feed com a base de nivel indice", () => {
    const o = porUrl["/news/mosca-olivo-catture-aumento/"];
    assert.ok(o, JSON.stringify(Object.keys(porUrl)));
    assert.equal(o.PUBLISHED_AT, "2026-09-24T07:30:00.000Z");
    assert.match(o.PUBLISHED_AT_BASIS, /^FEED pubDate em .*nivel indice; nunca FACT_TIME$/);
  });
  t("F3: FACT_TIME continua UNKNOWN em todas", () => {
    assert.ok(obs.length === 3 && obs.every((o) => o.FACT_TIME === "UNKNOWN"), JSON.stringify(obs.map((o) => o.FACT_TIME)));
  });
  t("F4: o item sem data no feed sai NAO SEI com o porque", () => {
    const o = porUrl["/news/articolo-senza-data-nel-feed/"];
    assert.equal(o.PUBLISHED_AT, "NAO SEI");
    assert.match(o.PUBLISHED_AT_BASIS, /^NAO SEI: o item do feed/);
  });
} finally {
  Object.assign(CONTRACTS[FONTE], ORIGINAL);
  servidor.close();
  rmSync(RAIZ, { recursive: true, force: true });
  rmSync(CURL_HOME, { recursive: true, force: true });
}
console.log(`\nFEED_LOCAL · passou=${passou} FALHAS=${falhou}`);
process.exit(falhou ? 1 : 0);
